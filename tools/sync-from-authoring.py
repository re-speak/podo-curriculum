#!/usr/bin/env python3
"""
Mirror `podo-curriculum-public` into this repo's non-deployable authoring area.

That repository is the upstream for `shared/`, `sandbox/authoring/` and
`references/`. The complete curriculum-under-review stays together under
`sandbox/authoring/<code>/`; an explicit promotion into `courses/<code>/` is
what makes a verified course deployable. Per language `<L>` (filed here under
its code `<c>`: korean -> kr, english -> en):

  runtime/{css,js}                       -> shared/{css,js} once, shared
  <L>/tracks/                            -> sandbox/authoring/<c>/tracks/
  korean/trial/                          -> sandbox/authoring/kr/trial/
  korean/interactive/                    -> sandbox/authoring/kr/interactive/
  korean/references/{curricula,reports}  -> references/kr/ minus licensed scans
  english/reference/                     -> references/en/reference/

`references/` is only durable source and evidence material. TOCs, generated
briefs, blueprints, course manifests and actual lessons are curriculum, so they
travel together through the sandbox review boundary instead of being split
between `references/` and `sandbox/`.

**Nothing synced here is deployable.** `tools/model.py` only discovers
`courses/`. Promotion tools read the reviewed sandbox copy and perform the
packaging transforms required by grape and lemonboard.

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
                                         [--runtime-only | --skip-runtime]
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


def sync_authoring(src: pathlib.Path, code: str, language: str) -> None:
    """Replace one language's complete, non-deployable curriculum mirror."""
    destination = REPO / "sandbox" / "authoring" / code
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    tree(src / "tracks", destination / "tracks")
    if language == upstream.DEFAULT_LANGUAGE:
        tree(src / "trial", destination / "trial")
        tree(src / "interactive", destination / "interactive")

    n = repoint_runtime(destination)
    done.append(
        f"sandbox/authoring/{code}/**  ({n} runtime refs repointed at shared/)")


def sync_reference_material(src: pathlib.Path, code: str, language: str) -> None:
    """Mirror durable evidence only; curriculum-under-review belongs in sandbox."""
    for rel, dest in MATERIAL.get(language, ()):
        source = src / rel
        destination = REPO / "references" / code / dest
        if source.is_dir():
            tree(source, destination)
        elif destination.exists():
            shutil.rmtree(destination)


def remove_legacy_layout(code: str, language: str) -> None:
    """Delete destinations superseded by sandbox/authoring/<code>."""
    obsolete = [
        REPO / "references" / code / "tracks",
        REPO / "sandbox" / "track-samples" / code,
    ]
    if language == upstream.DEFAULT_LANGUAGE:
        obsolete.extend((
            REPO / "sandbox" / "trial",
            REPO / "sandbox" / "interactive",
            REPO / "sandbox" / "viewers",
        ))

    for path in obsolete:
        if path.exists():
            shutil.rmtree(path)
            done.append(f"removed obsolete {path.relative_to(REPO)}")

    samples = REPO / "sandbox" / "track-samples"
    if samples.is_dir() and not any(samples.iterdir()):
        samples.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    upstream.add_argument(ap)
    ap.add_argument("--language", choices=(*upstream.LANGUAGES, "all"), default="all",
                    help="which subject language to mirror (default: every one upstream has)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--runtime-only", action="store_true",
                      help="only refresh shared/ — skip sandbox/ and references/")
    mode.add_argument("--skip-runtime", action="store_true",
                      help="refresh sandbox/ and references/ without overwriting shared/")
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

    if not args.skip_runtime:
        sync_runtime(next(iter(roots.values())))
    if not args.runtime_only:
        for language, src in roots.items():
            code = upstream.LANGUAGES[language]
            sync_authoring(src, code, language)
            sync_reference_material(src, code, language)
            remove_legacy_layout(code, language)

    print("synced:")
    for line in done:
        print(f"  {line}")
    print("\nreview sandbox/authoring/ before explicitly promoting into courses/")
    return 0


def _fail(message: str) -> int:
    print(f"✗ {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
