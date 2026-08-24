#!/usr/bin/env python3
"""Do the reorder chips actually rebuild the answer they are graded against?

activities.js compares with norm(): strip every whitespace character and every
punctuation mark, then compare. So a chip set is correct iff concatenating the
chips in their data-item-id order, normalised, equals the normalised answer.

Nothing else checks this. Chip COUNT is checked, chip UNIQUENESS is checked, but
a chip carrying a word that is not in the sentence — or a missing word — grades
as permanently wrong for the learner and is invisible to every other pass.

Parsing note: a chip is <span class="choice" ...>말<span class="yomi">マル</span></span>
at 초급 and <span class="choice" ...>말</span> at 중급. A non-greedy .*?</span>
therefore truncates the first shape at the INNER close. Spans are counted here
instead, and .yomi subtrees are dropped with their text before comparing.
"""
import argparse
import re
import sys
import unicodedata
import html
from itertools import permutations
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"
SPAN = re.compile(r"<span\b[^>]*>|</span>")
YOMI = re.compile(r'<span class="yomi">.*?</span>', re.S)
SMALLYOMI = re.compile(r'<small class="yomi">.*?</small>', re.S)


def span_body(src, start):
    """src[start] is just past a <span ...> open tag; return its inner html."""
    depth = 1
    pos = start
    for m in SPAN.finditer(src, start):
        depth += 1 if m.group(0) != "</span>" else -1
        if depth == 0:
            return src[start:m.start()], m.end()
        pos = m.end()
    return src[start:pos], pos


def norm(s):
    s = YOMI.sub("", s)
    s = SMALLYOMI.sub("", s)
    s = re.sub(r"<[^>]+>", "", s)
    out = []
    for ch in s:
        if ch.isspace() or unicodedata.category(ch).startswith("P"):
            continue
        if ch in "…、。？！":
            continue
        out.append(ch)
    return "".join(out)


def check(path):
    src = path.read_text(encoding="utf-8")
    problems = []
    zone = re.compile(
        r'<span class="answer-space build-zone" data-sync-id="([^"]+)" '
        r'data-sync-kind="order" data-a="([^"]*)"></span>')
    for m in zone.finditer(src):
        sid = m.group(1)
        answer = html.unescape(m.group(2))
        # chips for this sid follow, before the next build zone
        nxt = zone.search(src, m.end())
        region = src[m.end():nxt.start() if nxt else len(src)]
        chips = []
        for c in re.finditer(r'<span class="choice" data-item-id="' + re.escape(sid) + r'-(\d+)">', region):
            body, _ = span_body(region, c.end())
            chips.append((int(c.group(1)), body))
        if not chips:
            continue
        want = norm(answer)
        parts = [norm(b) for _, b in sorted(chips)]
        # data-item-id is a NAME for cross-screen sync, not a position
        # (activities.js: "위치가 아니라 칩의 이름(data-item-id)으로 지칭한다"),
        # so any ordering counts. The chips are correct iff SOME permutation
        # concatenates to the answer exactly.
        if not any("".join(p) == want for p in permutations(parts)):
            problems.append((sid, want, "".join(parts)))
    return problems


def deck_paths(paths, every):
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [TRACKS]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
    ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
    args = ap.parse_args()

    decks = deck_paths(args.paths, args.all)
    bad = 0
    for d in decks:
        for sid, want, built in check(d):
            bad += 1
            print(f"✗ {d.parent.name}  {sid}\n    answer : {want}\n    chips  : {built}")
    print(f"\n{len(decks)} deck(s) · {bad} mismatch(es)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
