#!/usr/bin/env python3
"""Find inline citations that AUTHORING.md § 인용한 표현 says must be quoted.

The rule: an expression the deck teaches, pulled into a sentence as-is, gets
wrapped — ‘ ’ inside .ko, 「 」 inside .ja. Straight quotes are never used.

Detection follows 42d1dd4's own heuristic: a run of hangul sitting inside
Japanese prose is by definition a citation, so every hangul run in a .ja span
must already be inside 「 」. Where a .ja span is flagged, its paired .ko span
is printed too, because the two lines must be quoted in the same places.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

HANGUL = re.compile(r"[가-힣]+(?:[\s··][가-힣]+)*[?!.]?")
TAG = re.compile(r"<[^>]+>")
# a .ja span is Japanese prose only if it actually contains kana
KANA = re.compile(r"[぀-ヿ]")
PAIR = re.compile(
    r'<span class="ko">(.*?)</span>\s*<span class="ja">(.*?)</span>', re.S)


def strip(s):
    return TAG.sub("", s)


def spans(text):
    """the character ranges already inside 「 」"""
    out, depth, start = [], 0, None
    for i, c in enumerate(text):
        if c == "「":
            if depth == 0:
                start = i
            depth += 1
        elif c == "」":
            depth -= 1
            if depth == 0 and start is not None:
                out.append((start, i))
                start = None
    return out


def unquoted(ja):
    inside = spans(ja)
    hits = []
    for m in HANGUL.finditer(ja):
        a, b = m.span()
        if any(s <= a and b - 1 <= e for s, e in inside):
            continue
        hits.append(m.group().strip())
    return hits


def main(paths):
    total = 0
    for p in paths:
        src = Path(p).read_text(encoding="utf-8")
        rows = []
        for m in PAIR.finditer(src):
            ko, ja = strip(m.group(1)), strip(m.group(2))
            if not KANA.search(ja):
                continue
            hits = unquoted(ja)
            if hits:
                rows.append((hits, ko, ja))
        if rows:
            print(f"\n### {Path(p).parent.name}  — {len(rows)} line(s)")
            for hits, ko, ja in rows:
                print(f"  citations: {hits}")
                print(f"    ko: {ko[:150]}")
                print(f"    ja: {ja[:150]}")
        total += len(rows)
    print(f"\n{len(paths)} deck(s) · {total} line(s) with an unquoted citation")
    return 1 if total else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        args = [str(p) for p in sorted(
            (REPO / "sandbox/drafts/kr/tracks").glob("**/lesson.html"))]
    sys.exit(main(args))
