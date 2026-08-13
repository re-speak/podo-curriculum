#!/usr/bin/env python3
"""
Mirror `podo-curriculum-public` into this repo.

That repository is the upstream for `shared/`, `sandbox/` and `references/`. It
is a different shape from this one — one directory per subject language, the
runtime shared at the root, nothing packaged — so a sync is a translation, not a
copy. Per language `<L>` (filed here under its code `<c>`: korean -> kr,
english -> en):

  runtime/{css,js}                       -> shared/{css,js}            once, shared
  <L>/tracks/*/table-of-contents.md      -> references/<c>/tracks/
  <L>/tracks/*/sample-lesson.html        -> sandbox/track-samples/<c>/ runtime refs repointed
  korean/references/{curricula,reports}  -> references/kr/             minus licensed scans
  english/reference/                     -> references/en/reference/
  korean/trial/*                         -> sandbox/trial/             runtime refs repointed
  korean/interactive/                    -> sandbox/interactive/       straight mirror

**Every language destination carries its code.** The two trees have identical
internal shape — `tracks/*/table-of-contents.md`, numbered by track — so an
unnamespaced destination is not a tidiness question. `references/tracks/` held
Korean's five tracks and English has four of its own; mirroring both into one
directory would have them overwrite each other by number, silently, and the
survivor would depend on which language synced last.

The 체험 destinations (`sandbox/trial/`, `sandbox/interactive/`) are the
exception: Korean is the only language with a `trial/` tree, and two importers —
`import-trial-decks.py`, `import-report-deck.py` — address those paths directly.
A second language growing a 체험 tree needs them namespaced first; until then a
name that promises per-language separation it does not have would be worse.

**The deployable decks are not synced by this script.** `trial/lessons/*.html`
becomes `courses/kr/hangul-trial-test/` via `import-trial-decks.py`, which has to
do considerably more: grape flattens the uploaded zip into one GCS prefix, so
each deck must carry its own runtime, and lemonboard's validator parses the HTML
statically, so the input controls have to exist in the markup. Run both.

**Every destination is replaced, not merged.** A file deleted upstream disappears
here. So edit upstream — anything written directly into these directories is lost
on the next run.

ONE DELIBERATE EXCLUSION: the licensed textbook scans. 41 PDFs and
`dekiru-kankokugo/page-images/` are 726MB of the 1.0GB in `references/curricula`,
they are licensed source material, and nothing in the build reads them. README.md
and references/README.md both say they stay upstream; this keeps that promise
rather than quietly reversing it. Derived markdown and wireframe PNGs do come.

    python3 tools/sync-from-authoring.py [--upstream PATH]
                                         [--language korean|english|all]
                                         [--runtime-only]
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import sys

import upstream

REPO = upstream.REPO

SKIP_SUFFIX = {".pdf"}
SKIP_DIR = {"page-images", ".git", "__pycache__", ".DS_Store"}

RUNTIME_REF = re.compile(r'((?:href|src)=")(?:\.\./)*runtime/')

# Planning material each language keeps in its own place upstream, mapped to a
# directory under `references/<code>/`. Korean's is the textbook study it was
# built from; English's is the design record for a curriculum still being built.
# Both are language-specific, so both live behind the code.
MATERIAL = {
    "korean": (("references/curricula", "curricula"),
               ("references/reports", "reports")),
    "english": (("reference", "reference"),),
}

done: list[str] = []


def _ignore(_dir, names):
    return [n for n in names
            if n in SKIP_DIR or pathlib.PurePath(n).suffix.lower() in SKIP_SUFFIX]


def tree(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.is_dir():
        print(f"  ~ not upstream, skipped: {src}")
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=_ignore)
    n = sum(1 for p in dst.rglob("*") if p.is_file())
    done.append(f"{dst.relative_to(REPO)}  ({n} files)")


def one(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.is_file():
        print(f"  ~ not upstream, skipped: {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    done.append(str(dst.relative_to(REPO)))


def repoint_runtime(root: pathlib.Path) -> int:
    """Point mirrored decks at shared/, which is this repo's name for runtime/.

    Without this the sandbox copies open with no stylesheet and no scripts. That
    is how the previous mirror rotted: its refs had been repointed by hand at
    `../../shared/lesson-card.css` and `../../interactive/*.js`, and neither path
    survived the reorganisation that put the CSS under shared/css/.

    Deployable decks never come through here — they bundle the runtime instead,
    because a relative path out of the deck directory cannot survive grape
    flattening the zip into a single GCS prefix.
    """
    hits = 0
    for page in sorted(root.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        rel = os.path.relpath(REPO / "shared", page.parent)
        new, n = RUNTIME_REF.subn(lambda m: f"{m.group(1)}{rel}/", text)
        if n:
            page.write_text(new, encoding="utf-8")
            hits += n
    return hits


def sync_runtime(src: pathlib.Path) -> None:
    """The files every language shares. Runs once, whichever language we have."""
    runtime = upstream.runtime_root(src)
    site = upstream.site_root(src)
    tree(runtime / "css", REPO / "shared" / "css")
    tree(runtime / "js", REPO / "shared" / "js")
    one(site / "ux-philosophy.md", REPO / "shared" / "ux-philosophy.md")


def sync_viewers(src: pathlib.Path) -> None:
    one(upstream.site_root(src) / "viewer.html",
        REPO / "sandbox" / "viewers" / "viewer.html")
    # Upstream's site index. Its links address the upstream tracks/ layout, which
    # this repo splits three ways, so they do not resolve here — see sandbox/README.
    one(src / "index.html", REPO / "sandbox" / "viewers" / "deck-index.html")


def sync_trial(src: pathlib.Path) -> None:
    """Korean's 체험 tree. See the module docstring on why this one is not coded."""
    for name in ("lessons", "full-trials", "reports", "assets", "lemonboard-build"):
        tree(src / "trial" / name, REPO / "sandbox" / "trial" / name)
    one(src / "trial" / "illustration-prompts.md",
        REPO / "sandbox" / "trial" / "illustration-prompts.md")
    tree(src / "interactive", REPO / "sandbox" / "interactive")


def sync_track_samples(src: pathlib.Path, code: str) -> None:
    samples = REPO / "sandbox" / "track-samples" / code
    if samples.exists():
        shutil.rmtree(samples)
    samples.mkdir(parents=True)
    for track in sorted((src / "tracks").iterdir()):
        if (track / "sample-lesson.html").is_file():
            one(track / "sample-lesson.html", samples / f"{track.name}.html")


def sync_references(src: pathlib.Path, code: str, language: str) -> None:
    plans = REPO / "references" / code / "tracks"
    if plans.exists():
        shutil.rmtree(plans)
    plans.mkdir(parents=True)
    for track in sorted((src / "tracks").iterdir()):
        if (track / "table-of-contents.md").is_file():
            one(track / "table-of-contents.md", plans / f"{track.name}.md")
        if (track / "toc").is_dir():
            tree(track / "toc", plans / track.name / "toc")
        if (track / "lesson-blueprint.md").is_file():
            one(track / "lesson-blueprint.md", plans / track.name / "lesson-blueprint.md")

    for rel, dest in MATERIAL.get(language, ()):
        tree(src / rel, REPO / "references" / code / dest)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    upstream.add_argument(ap)
    ap.add_argument("--language", choices=(*upstream.LANGUAGES, "all"), default="all",
                    help="which subject language to mirror (default: every one upstream has)")
    ap.add_argument("--runtime-only", action="store_true",
                    help="only refresh shared/ — skip sandbox/ and references/")
    args = ap.parse_args()

    if args.language == "all":
        roots = upstream.available(args.upstream)
        if not roots:
            # Report it the way a single named language would, so the message
            # still says where it looked and how to point it somewhere else.
            try:
                upstream.resolve(args.upstream)
            except upstream.UpstreamMissing as exc:
                return _fail(str(exc))
    else:
        try:
            roots = {args.language: upstream.resolve(args.upstream, args.language)}
        except upstream.UpstreamMissing as exc:
            return _fail(str(exc))

    print("upstream:")
    for language, src in roots.items():
        print(f"  {language:8} {src}")
    print()

    sync_runtime(next(iter(roots.values())))
    if not args.runtime_only:
        for language, src in roots.items():
            code = upstream.LANGUAGES[language]
            sync_track_samples(src, code)
            sync_references(src, code, language)
            if language == upstream.DEFAULT_LANGUAGE:
                sync_viewers(src)
                sync_trial(src)
        n = repoint_runtime(REPO / "sandbox")
        done.append(f"sandbox/**  ({n} runtime refs repointed at shared/)")

    print("synced:")
    for line in done:
        print(f"  {line}")
    print("\nnow run:  python3 tools/import-trial-decks.py")
    return 0


def _fail(message: str) -> int:
    print(f"✗ {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
