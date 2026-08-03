#!/usr/bin/env python3
"""
Package one deck into the zip the lemonboard-html upload slot takes.

Grape unpacks that zip to S3 under lemonboard-html/{교재ID}/, FLATTENING every
entry into that one prefix, and renames the first .html and first .css it finds
to lecture.* or prestudy.*. Three consequences drive this script:

  1. A deck loads several stylesheets (shared/css/lesson-card.css plus its own).
     They have to be merged into one, in link order, so the cascade survives.
  2. Grape rewrites the <link> for us — it str_replaces the css basename
     throughout the HTML with the slot's name. So we ship ONE link pointing at
     the css basename in the zip, and the same zip works in both slots.
  3. Flattening means images ride under their basename, and src="assets/x.png"
     is rewritten to src="x.png". Basenames must be unique across folders —
     a collision is a hard error, not a silently overwritten image.

Everything ships inside the zip, so a packaged deck needs no CDN and survives a
locked-down classroom network. (The Pretendard webfont is an @import and stays
the one remote dependency.)

    python3 tools/build.py DECK.html --out DIR
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import shutil
import sys
import zipfile

# Neutral names. Grape renames them per slot; staying slot-agnostic means the
# unzipped output is also directly viewable in a browser.
HTML_NAME = "lesson.html"
CSS_NAME = "lesson.css"

LINK_RE = re.compile(r'[ \t]*<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>\n?')
SRC_RE = re.compile(r'\bsrc="([^"]+)"')
CSS_URL_RE = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)')

# The rewrites above understand exactly one spelling each. Everything a deck
# could plausibly use instead is caught below and reported, because the failure
# is otherwise silent: the asset is neither bundled nor rewritten, so it 404s
# from S3 while the build prints success.
UNHANDLED = [
    (re.compile(r'<link(?![^>]*rel="stylesheet"[^>]*href=")[^>]*rel=[\'"]?stylesheet', re.I),
     'a <link rel=stylesheet> the merger cannot read (href must follow rel, in double quotes)'),
    (re.compile(r'\bsrcset\s*='), 'srcset= (not bundled; use a plain src=)'),
    (re.compile(r"\bsrc\s*=\s*'"), "src='...' in single quotes (not bundled; use double quotes)"),
    (re.compile(r'\bSRC\s*='), 'uppercase SRC= (not bundled; use lowercase)'),
    (re.compile(r'style="[^"]*url\('), 'inline style="...url(...)" (not bundled)'),
]

REMOTE_PREFIXES = ("http://", "https://", "//", "data:", "#")

# lesson.* collides with the merged output; lecture.*/prestudy.* are uploaded
# AFTER the css, so an asset by that name would overwrite the lesson at its S3 key.
RESERVED = {HTML_NAME, CSS_NAME, "lecture.html", "lecture.css",
            "prestudy.html", "prestudy.css"}


class BuildError(Exception):
    pass


def is_remote(ref: str) -> bool:
    return ref.startswith(REMOTE_PREFIXES)


def strip_comments(css: str) -> str:
    """Blank out /* */ blocks, preserving offsets, so scans ignore commented code."""
    return re.sub(r'/\*.*?\*/', lambda m: re.sub(r'\S', ' ', m.group(0)), css, flags=re.S)


def package(source: pathlib.Path, outdir: pathlib.Path, quiet: bool = False) -> tuple[pathlib.Path, str]:
    """Build the zip. Returns (zip path, sha256 digest of its contents)."""
    html = source.read_text(encoding="utf-8")
    srcdir = source.parent

    # ---- 1. merge every local stylesheet, in link order, into one file ----
    links = LINK_RE.findall(html)
    local_sheets = [href for href in links if not is_remote(href)]
    if not local_sheets:
        raise BuildError(f"no local stylesheet <link> found in {source.name}")

    merged = []
    for href in local_sheets:
        path = (srcdir / href).resolve()
        if not path.is_file():
            raise BuildError(f"stylesheet not found: {href} -> {path}")
        merged.append(f"/* ===== {path.name} ===== */\n{path.read_text(encoding='utf-8')}")
    css = "\n\n".join(merged)

    # A merged sheet may hold several @import lines; CSS requires them before any
    # rule, so hoist them to the top in first-seen order. Only real, top-level
    # statements — a line-anchored substitution would also lift a commented-out
    # @import back to life and pull one out of an @media block.
    imports: list[str] = []
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
        target = (re.search(r'url\(\s*[\'"]?([^\'")]+)', statement)
                  or re.search(r'[\'"]([^\'"]+)[\'"]', statement))
        if target and not is_remote(target.group(1)):
            raise BuildError(f"local @import is not bundled and would 404: {statement.strip()}")

    # ---- 2. collapse the link tags down to the one grape will rename ----
    first = True

    def swap(match):
        nonlocal first
        if is_remote(match.group(1)):
            return match.group(0)
        if first:
            first = False
            return f'  <link rel="stylesheet" href="{CSS_NAME}">\n'
        return ""

    html = LINK_RE.sub(swap, html)

    # ---- 3. local assets ride in the zip, flattened to their basename ----
    assets: dict[str, pathlib.Path] = {}
    remote_refs: list[str] = []
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
        seen = assets.get(path.name)
        if seen is not None and seen != path:
            raise BuildError(f"basename collision after flattening: {path.name}\n  {seen}\n  {path}")
        assets[path.name] = path
        return f'src="{path.name}"'

    html, n_ref = SRC_RE.subn(flatten, html)

    missing = sorted(str(p) for p in assets.values() if not p.is_file())
    if missing:
        raise BuildError("referenced assets not on disk:\n  " + "\n  ".join(missing))

    clashing = sorted(RESERVED & set(assets))
    if clashing:
        raise BuildError(f"asset name(s) reserved by the upload slot: {', '.join(clashing)} — rename them")

    audit(html, css)

    # ---- 4. write + zip ----
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / HTML_NAME).write_text(html, encoding="utf-8")
    (outdir / CSS_NAME).write_text(css, encoding="utf-8")
    for name, path in assets.items():
        shutil.copyfile(path, outdir / name)

    zip_path = outdir / f"{source.parent.name}.zip"
    # Fixed timestamps: the digest must reflect content, not build time, or every
    # CI run would look like a change and re-upload every live lesson.
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in [HTML_NAME, CSS_NAME] + sorted(assets):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (outdir / name).read_bytes())

    digest = digest_of(outdir, [HTML_NAME, CSS_NAME] + sorted(assets))

    if not quiet:
        print(f"{zip_path.name}  ({zip_path.stat().st_size // 1024} KB)  {digest[:19]}…")
        print(f"  merged css : {', '.join(pathlib.Path(s).name for s in local_sheets)} -> {CSS_NAME}")
        print(f"  hoisted    : {len(imports)} @import")
        print(f"  bundled    : {len(assets)} asset(s) "
              f"({n_local} local ref(s) flattened, {n_ref - n_local} left remote)")
        if remote_refs:
            print(f"  NOTE       : {len(remote_refs)} asset(s) stay on the network — not offline-safe:")
            for ref in sorted(set(remote_refs))[:5]:
                print(f"    {ref}")

    return zip_path, digest


def digest_of(outdir: pathlib.Path, names: list[str]) -> str:
    """Content hash over the packaged files, name-sensitive and order-stable."""
    h = hashlib.sha256()
    for name in names:
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update((outdir / name).read_bytes())
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def audit(html: str, css: str) -> None:
    """Fail loudly on anything the rewrites above silently pass through."""
    problems = []

    for pattern, description in UNHANDLED:
        if pattern.search(html):
            problems.append(description)

    # A surviving stylesheet link points at a file that will not exist on S3 —
    # the unpack flattens, and only the merged sheet is uploaded.
    for href in LINK_RE.findall(html):
        if not is_remote(href) and href != CSS_NAME:
            problems.append(f'stylesheet <link href="{href}"> was not merged')

    for ref in CSS_URL_RE.findall(strip_comments(css)):
        if not is_remote(ref):
            problems.append(f'css url({ref}) is not bundled and would 404')

    leftover = [r for r in SRC_RE.findall(html) if not is_remote(r) and "/" in r]
    problems.extend(f'src="{r}" still points at a subfolder' for r in leftover)

    if problems:
        raise BuildError("cannot package — these would break silently on S3:\n  "
                         + "\n  ".join(problems))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    a = ap.parse_args()
    try:
        package(a.source.resolve(), a.out.resolve())
    except BuildError as exc:
        sys.exit(str(exc))
