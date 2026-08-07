#!/usr/bin/env python3
"""
Package a lesson deck for the lemonboard-html upload slot.

The slot takes a zip. Grape unpacks it to S3 under lemonboard-html/{교재ID}/,
flattening every entry into that one prefix, and renames the first .html and
first .css it finds to lecture.* (수업용) or prestudy.* (예습용).

Three consequences drive this script:

  1. Our decks load two stylesheets (the shared lesson-card.css plus the
     track's own sheet). They have to be merged into one, in link order, so
     the cascade survives.
  2. Grape rewrites the <link> for us: it str_replaces the css file's basename
     throughout the HTML with the slot's name. So we ship ONE link pointing at
     the css basename that is in the zip, and the same zip works in both slots.
  3. The unpack flattens folders, so images ride along under their basename
     and local src="mouth/x.png" is rewritten to src="x.png". Basenames must
     therefore be unique across folders — collisions are a hard error.

Local files ship inside the zip; absolute URLs are left alone and reported, so a
deck may pull its stylesheet, scripts or images from a CDN instead.

Usage:
    python3 build_lemonboard.py SOURCE.html --out DIR
"""

import argparse
import pathlib
import re
import shutil
import sys
import zipfile

# Neutral names. Grape renames them per slot; keeping them slot-agnostic means
# the unzipped output is also directly viewable in a browser.
HTML_NAME = "lesson.html"
CSS_NAME = "lesson.css"

LINK_RE = re.compile(r'[ \t]*<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>\n?')
SRC_RE = re.compile(r'\bsrc="([^"]+)"')

# The rewrites above only understand one spelling each. Everything a deck could
# plausibly use *instead* is caught below and reported, because the failure mode
# is otherwise silent: the asset is neither bundled nor rewritten, so it 404s
# from S3 while the build prints success.
UNHANDLED = [
    (re.compile(r'<link(?![^>]*rel="stylesheet"[^>]*href=")[^>]*rel=[\'"]?stylesheet', re.I),
     'a <link rel=stylesheet> the merger cannot read (href must follow rel, in double quotes)'),
    (re.compile(r'\bsrcset\s*='), 'srcset= (not bundled; use a plain src=)'),
    (re.compile(r"\bsrc\s*=\s*'"), "src='...' in single quotes (not bundled; use double quotes)"),
    (re.compile(r'\bSRC\s*=', ), 'uppercase SRC= (not bundled; use lowercase)'),
    (re.compile(r'style="[^"]*url\('), 'inline style="...url(...)" (not bundled)'),
]

CSS_URL_RE = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)')

REMOTE_PREFIXES = ("http://", "https://", "//", "data:", "#")


def is_remote(ref: str) -> bool:
    return ref.startswith(REMOTE_PREFIXES)


def strip_comments(css: str) -> str:
    """Blank out /* */ blocks, preserving offsets, so scans ignore commented code."""
    return re.sub(r'/\*.*?\*/', lambda m: re.sub(r'\S', ' ', m.group(0)), css, flags=re.S)


def build(source: pathlib.Path, outdir: pathlib.Path):
    html = source.read_text(encoding="utf-8")
    srcdir = source.parent

    # ---- 1. merge every local stylesheet, in link order, into one file ----
    links = LINK_RE.findall(html)
    local_sheets = [href for href in links if not is_remote(href)]
    if not local_sheets:
        sys.exit(f"no local stylesheet <link> found in {source.name}")

    merged = []
    for href in local_sheets:
        path = (srcdir / href).resolve()
        if not path.is_file():
            sys.exit(f"stylesheet not found: {href} -> {path}")
        merged.append(f"/* ===== {path.name} ===== */\n{path.read_text(encoding='utf-8')}")
    css = "\n\n".join(merged)

    # A merged sheet may hold several @import lines; CSS requires them before
    # any rule, so hoist them to the top in first-seen order.
    imports = []

    def lift(match):
        imports.append(match.group(0).strip())
        return ""

    # Only hoist imports that are real, top-level statements. A line-anchored
    # substitution over the raw text would also lift a commented-out @import back
    # to life, and pull one out of an @media block, making it unconditional.
    visible = strip_comments(css)

    def is_top_level(offset: int) -> bool:
        return visible.count("{", 0, offset) == visible.count("}", 0, offset)

    def lift(match):
        if visible[match.start():match.end()].strip().startswith("@import") and is_top_level(match.start()):
            imports.append(match.group(0).strip())
            return ""
        return match.group(0)

    css_body = re.sub(r'^[ \t]*@import[^;]+;[ \t]*\n?', lift, css, flags=re.M)
    if imports:
        css = "\n".join(dict.fromkeys(imports)) + "\n\n" + css_body

    for statement in imports:
        target = re.search(r'url\(\s*[\'"]?([^\'")]+)', statement) or re.search(r'[\'"]([^\'"]+)[\'"]', statement)
        if target and not is_remote(target.group(1)):
            sys.exit(f"local @import is not bundled and would 404: {statement.strip()}")

    # ---- 2. collapse the link tags down to the one grape will rename ----
    first = True

    def swap(match):
        nonlocal first
        if is_remote(match.group(1)):
            return match.group(0)          # leave remote sheets alone
        if first:
            first = False
            return f'  <link rel="stylesheet" href="{CSS_NAME}">\n'
        return ""

    html = LINK_RE.sub(swap, html)

    # ---- 3. local images ride in the zip, flattened to their basename ----
    assets = {}      # basename -> source path
    remote_refs = []
    n_local = 0

    def flatten(match):
        nonlocal n_local
        ref = match.group(1)
        if is_remote(ref):
            if ref.startswith(("http://", "https://", "//")):
                remote_refs.append(ref)
            return match.group(0)
        n_local += 1
        path = (srcdir / ref).resolve()
        name = path.name
        seen = assets.get(name)
        if seen is not None and seen != path:
            sys.exit(f"basename collision after flattening: {name}\n  {seen}\n  {path}")
        assets[name] = path
        return f'src="{name}"'

    html, n_img = SRC_RE.subn(flatten, html)

    missing = sorted(str(p) for p in assets.values() if not p.is_file())
    if missing:
        sys.exit("referenced images not on disk:\n  " + "\n  ".join(missing))

    # Reserved names: lesson.* would clobber the merged output on disk, and
    # lecture.*/prestudy.* are uploaded AFTER the css, so they would overwrite
    # the lesson at its S3 key.
    reserved = {HTML_NAME, CSS_NAME, "lecture.html", "lecture.css", "prestudy.html", "prestudy.css"}
    clashing = sorted(reserved & set(assets))
    if clashing:
        sys.exit(f"asset name(s) reserved by the upload slot: {', '.join(clashing)} — rename them")

    audit(html, css, srcdir)

    # ---- 4. write + zip ----
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / HTML_NAME).write_text(html, encoding="utf-8")
    (outdir / CSS_NAME).write_text(css, encoding="utf-8")
    for name, path in assets.items():
        shutil.copyfile(path, outdir / name)

    zip_path = outdir / f"{source.stem}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(outdir / HTML_NAME, HTML_NAME)
        z.write(outdir / CSS_NAME, CSS_NAME)
        for name in sorted(assets):
            z.write(outdir / name, name)

    print(f"{zip_path.name}  ({zip_path.stat().st_size // 1024} KB)")
    print(f"  merged css : {', '.join(pathlib.Path(s).name for s in local_sheets)} -> {CSS_NAME}")
    print(f"  hoisted    : {len(imports)} @import")
    print(f"  bundled    : {len(assets)} image(s) ({n_local} local ref(s) flattened, {n_img - n_local} left remote)")
    print(f"  slot names : grape renames {HTML_NAME}/{CSS_NAME} -> lecture.* or prestudy.*")
    if remote_refs:
        print(f"  NOTE       : {len(remote_refs)} reference(s) left remote (not bundled):")
        for ref in sorted(set(remote_refs))[:5]:
            print(f"    {ref}")
    return zip_path


def audit(html: str, css: str, srcdir: pathlib.Path):
    """Fail loudly on anything the rewrites above silently pass through."""
    problems = []

    for pattern, description in UNHANDLED:
        if pattern.search(html):
            problems.append(description)

    # A stylesheet link that survived the collapse points at a file that will not
    # exist on S3 (the unpack flattens, and only the merged sheet is uploaded).
    for href in LINK_RE.findall(html):
        if not is_remote(href) and href != CSS_NAME:
            problems.append(f'stylesheet <link href="{href}"> was not merged')

    for ref in CSS_URL_RE.findall(strip_comments(css)):
        if not is_remote(ref):
            problems.append(f'css url({ref}) is not bundled and would 404')

    leftover = [ref for ref in SRC_RE.findall(html) if not is_remote(ref) and "/" in ref]
    problems.extend(f'src="{ref}" still points at a subfolder' for ref in leftover)

    if problems:
        sys.exit("cannot package — these would break silently on S3:\n  " + "\n  ".join(problems))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    a = ap.parse_args()
    build(a.source.resolve(), a.out.resolve())
