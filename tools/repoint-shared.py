#!/usr/bin/env python3
"""
Point a deck's shared runtime at `spec.sharedRuntime` in curriculum.yaml.

Two jobs, and it is idempotent in both:

  1. a local ref whose basename `shared/` also owns  ->  the pinned CDN URL,
     and the now-unreferenced local copy is deleted
  2. a CDN URL already on our baseUrl but an older tag  ->  re-pinned to the
     declared version

Deck-specific files and every image stay local and keep riding in the zip. Only
what `shared/` owns moves, because only that is identical across decks.

**Publish before you repoint.** The tag has to be live before a deck naming it
ships; `tools/publish-shared.py` does that, and `tools/validate.py` refuses a deck
whose tag is not serving. A deck pointing at an unpushed tag 404s in class, on the
learner's screen only, with nothing in your console to see.

    python3 tools/repoint-shared.py [COURSE ...] [--dry-run]

With no COURSE it walks every course under courses/. Name courses (`kr/test-report`)
to scope it — a deck deliberately left on its own bundled runtime just goes unnamed.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

import model

# grape str_replaces the shipped css basename through the HTML to rename it per
# slot (build.py:8). A remote URL holding that literal would be rewritten mid-URL.
FORBIDDEN = ("lesson.css", "lesson.html", "lecture.css", "prestudy.css")

STUB = "deck.css"
LINK_RE = re.compile(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>')
REMOTE = ("http://", "https://", "//", "data:", "#")


def shared_owns() -> dict[str, str]:
    """basename -> 'css' | 'js' for everything shared/ owns."""
    out = {}
    for sub in ("css", "js"):
        d = model.REPO / "shared" / sub
        if d.is_dir():
            for p in d.iterdir():
                if p.is_file():
                    out[p.name] = sub
    return out


def repoint_deck(deck: pathlib.Path, base: str, owned: dict[str, str],
                 dry: bool) -> tuple[int, int, bool]:
    """Returns (moved, repinned, wrote_stub)."""
    html_path = deck / "index.html"
    if not html_path.is_file():
        return (0, 0, False)
    html = original = html_path.read_text(encoding="utf-8")

    prefix = base.rsplit("@", 1)[0] if "@" in base else base.rsplit("/", 1)[0]
    moved: set[str] = set()
    repinned = 0

    def fix(match: re.Match, attr: str) -> str:
        nonlocal repinned
        ref = match.group(1)
        # already ours, but possibly an older tag
        if ref.startswith(prefix):
            tail = ref.split("/")
            rel = "/".join(tail[-2:])                      # css/x.css | js/x.js
            new = f"{base}/{rel}"
            if new != ref:
                repinned += 1
            return f'{attr}="{new}"'
        if ref.startswith(REMOTE):
            return match.group(0)
        name = pathlib.PurePosixPath(ref).name
        sub = owned.get(name)
        if sub is None:
            return match.group(0)
        moved.add(name)
        return f'{attr}="{base}/{sub}/{name}"'

    html = re.sub(r'\bsrc="([^"]+)"', lambda m: fix(m, "src"), html)
    html = re.sub(r'\bhref="([^"]+)"', lambda m: fix(m, "href"), html)

    # build.py:86 needs one LOCAL stylesheet — grape renames the first .css in the
    # zip to the slot name, so a deck with none has nothing to rename. If every
    # sheet just went remote, leave the deck its own. It links last, so deck
    # overrides still win the cascade.
    wrote_stub = False
    if not [h for h in LINK_RE.findall(html) if not h.startswith(REMOTE)]:
        links = list(re.finditer(r'[ \t]*<link[^>]+rel="stylesheet"[^>]*>\n?', html))
        if links:
            wrote_stub = True
            if not dry:
                (deck / STUB).write_text(
                    "/* Deck-specific overrides. Shared runtime comes from the CDN\n"
                    "   pinned in curriculum.yaml (spec.sharedRuntime). */\n",
                    encoding="utf-8")
            html = (html[:links[-1].end()]
                    + f'  <link rel="stylesheet" href="{STUB}">\n'
                    + html[links[-1].end():])

    if not dry and html != original:
        html_path.write_text(html, encoding="utf-8")
        for name in moved:
            local = deck / name
            if local.is_file():
                local.unlink()

    return (len(moved), repinned, wrote_stub)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("courses", nargs="*", metavar="COURSE",
                    help="course keys to repoint, e.g. kr/test-report (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        curriculum = model.load_curriculum()
        all_courses = model.discover()
    except model.ValidationError as exc:
        print(f"✗ {exc}")
        return 1

    rt = curriculum["spec"].get("sharedRuntime")
    if not rt:
        print("✗ curriculum.yaml has no spec.sharedRuntime")
        return 1

    base = f"{rt['baseUrl'].rstrip('/')}{rt.get('join', '@')}{rt['version']}"
    owned = shared_owns()

    for bad in FORBIDDEN:
        if bad in base:
            print(f"✗ baseUrl/version contains {bad!r} — grape's rename would mangle it")
            return 1
        for name in owned:
            if bad in name:
                print(f"✗ shared/ holds {name!r} containing {bad!r} — rename the file")
                return 1

    wanted = set(args.courses)
    picked = [c for c in all_courses if not wanted or c.key in wanted]
    if wanted:
        unknown = wanted - {c.key for c in all_courses}
        if unknown:
            print(f"✗ unknown course(s): {', '.join(sorted(unknown))}")
            return 1

    print(f"pin     : {base}")
    print(f"scope   : {', '.join(c.key for c in picked) if picked else '(nothing)'}")
    print()

    tot_moved = tot_repinned = tot_stub = 0
    for course in picked:
        for lesson in course.lessons:
            for slot, deck in sorted(lesson.decks.items()):
                if not deck.exists:
                    continue
                moved, repinned, stub = repoint_deck(
                    deck.entry.parent, base, owned, args.dry_run)
                if moved or repinned or stub:
                    bits = []
                    if moved:
                        bits.append(f"{moved} moved")
                    if repinned:
                        bits.append(f"{repinned} re-pinned")
                    if stub:
                        bits.append(f"+{STUB}")
                    print(f"  {course.key}/{lesson.slug}/{slot:<8} {', '.join(bits)}")
                tot_moved += moved
                tot_repinned += repinned
                tot_stub += 1 if stub else 0

    print()
    print(f"{'would move' if args.dry_run else 'moved'} {tot_moved} ref(s), "
          f"re-pinned {tot_repinned}, wrote {tot_stub} {STUB}")
    if args.dry_run:
        print("(dry run — nothing written)")
    else:
        print("next: python3 tools/validate.py --contract --env stage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
