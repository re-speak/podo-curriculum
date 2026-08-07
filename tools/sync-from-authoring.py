#!/usr/bin/env python3
"""
Mirror `beginner-curriculum/korean` into this repo.

That tree is the upstream for `shared/`, `sandbox/` and `references/`. It is a
different shape from this one — every deck reaches a single sibling `runtime/`,
nothing is packaged — so a sync is a translation, not a copy:

  runtime/{css,js}                     -> shared/{css,js}          straight mirror
  trial/*, tracks/*/sample-lesson.html -> sandbox/                 runtime refs repointed
  interactive/                         -> sandbox/interactive/     straight mirror
  tracks/*/table-of-contents.md        -> references/tracks/
  references/{curricula,reports}       -> references/              minus licensed scans

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

    python3 tools/sync-from-authoring.py [--upstream PATH] [--runtime-only]
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
    tree(src / "runtime" / "css", REPO / "shared" / "css")
    tree(src / "runtime" / "js", REPO / "shared" / "js")
    one(src / "ux-philosophy.md", REPO / "shared" / "ux-philosophy.md")


def sync_sandbox(src: pathlib.Path) -> None:
    for name in ("lessons", "full-trials", "reports", "assets", "lemonboard-build"):
        tree(src / "trial" / name, REPO / "sandbox" / "trial" / name)
    one(src / "trial" / "illustration-prompts.md",
        REPO / "sandbox" / "trial" / "illustration-prompts.md")

    samples = REPO / "sandbox" / "track-samples"
    if samples.exists():
        shutil.rmtree(samples)
    samples.mkdir(parents=True)
    for track in sorted((src / "tracks").iterdir()):
        if (track / "sample-lesson.html").is_file():
            one(track / "sample-lesson.html", samples / f"{track.name}.html")

    one(src / "viewer.html", REPO / "sandbox" / "viewers" / "viewer.html")
    # Upstream's site index. Its links address the upstream tracks/ layout, which
    # this repo splits three ways, so they do not resolve here — see sandbox/README.
    one(src / "index.html", REPO / "sandbox" / "viewers" / "deck-index.html")

    tree(src / "interactive", REPO / "sandbox" / "interactive")

    n = repoint_runtime(REPO / "sandbox")
    done.append(f"sandbox/**  ({n} runtime refs repointed at shared/)")


def sync_references(src: pathlib.Path) -> None:
    plans = REPO / "references" / "tracks"
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

    tree(src / "references" / "curricula", REPO / "references" / "curricula")
    tree(src / "references" / "reports", REPO / "references" / "reports")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    upstream.add_argument(ap)
    ap.add_argument("--runtime-only", action="store_true",
                    help="only refresh shared/ — skip sandbox/ and references/")
    args = ap.parse_args()

    try:
        src = upstream.resolve(args.upstream)
    except upstream.UpstreamMissing as exc:
        return _fail(str(exc))

    print(f"upstream: {src}\n")
    sync_runtime(src)
    if not args.runtime_only:
        sync_sandbox(src)
        sync_references(src)

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
