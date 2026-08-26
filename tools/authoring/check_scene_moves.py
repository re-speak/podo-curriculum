#!/usr/bin/env python3
"""Scene echo — a turn that says again what the turn before it just said.

    python3 tools/authoring/check_scene_moves.py sandbox/drafts/kr/tracks
    python3 tools/authoring/check_scene_moves.py path/to/lesson.html ...
    python3 tools/authoring/check_scene_moves.py --all

Why this exists
---------------
Contextual scenes are five turns, and the learner's two lines sit at turns 2 and
4 because those two lines *are* the lesson's target expressions — the partner's
turns get written around them afterwards. That frame is sound when a target is a
**reaction** (agreeing, being surprised, comforting): a reaction can follow
anything. It breaks when a target **initiates** — asking, relaying news,
explaining — because turn 1 has already taken the opening move, and the scene
then says the same thing twice.

The 2026-08-26 audit of the two Korean banmal courses found this in eight of ten
scenes in one course. The clearest case, `04-hearsay`, had the partner relay a
rumour and the learner relay the identical rumour straight back to them:

    친구  너 그 둘 소문 들었어? 결국 헤어졌다는 얘기가 있던데.
    나    너 그 소문 들었어? 걔네 헤어졌대.        ← this

That is what this check finds: consecutive turns whose content words largely
coincide. It is deliberately narrow. It cannot tell whether a target *is* an
initiation, and it does not try — the repeated content is the mechanical trace
the defect leaves behind, and it is the part a static reader can prove.

Shared rather than per-language on purpose: the frame and the failure are about
discourse, not about Korean, and both corpora render a scene the same way — the
target-language line is `.bubble .korean`, whatever that language happens to be.
Only the canonical `scene` block is read; `p3-model`, `p3-complete` and the next
episode teaser replay it, and reporting the same defect four times helps nobody.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

MIN_STEMS = 3          # ignore turns too short to repeat anything meaningfully
OVERLAP = 0.6          # share of the later turn's stems already in the earlier one

STOP = {
    "the","a","an","is","are","was","were","be","been","to","of","in","on","at","for",
    "and","or","but","it","this","that","i","you","we","they","he","she","my","your",
    "do","does","did","not","no","so","if","as","with","from","have","has","had","will",
}


def turns(html: str) -> list[str]:
    """Target-language lines of the canonical scene, in order."""
    m = re.search(r'data-page-id="scene"', html)
    if not m:
        return []
    tail = html[m.end():]
    nxt = re.search(r'data-page-id=', tail)
    block = tail[: nxt.start()] if nxt else tail
    out = []
    for chunk in re.split(r'(?=<div class="turn )', block)[1:]:
        say = re.search(r'<span class="korean">([\s\S]*?)</span>\s*<span class="(?:yomi|translation)"', chunk)
        if not say:
            continue
        text = re.sub(r"<[^>]+>", "", say.group(1))
        text = re.sub(r"&[a-z]+;", " ", text).strip()
        if text:
            out.append(text)
    return out


def stems(line: str) -> set[str]:
    """Crude, deliberately language-agnostic content words.

    Korean is agglutinative, so a bare word match misses 헤어졌다는 / 헤어졌대.
    Taking a two-character prefix of each token collapses most inflection without
    needing a morphological analyser. For Latin script the token is the stem, minus
    a small stop list.
    """
    got = set()
    for tok in re.split(r"[^0-9A-Za-z가-힣]+", line):
        if not tok:
            continue
        if re.match(r"^[가-힣]", tok):
            if len(tok) >= 2:
                got.add(tok[:2])
        else:
            low = tok.lower()
            if len(low) >= 3 and low not in STOP:
                got.add(low)
    return got


def asked(line: str) -> bool:
    """Does the line end on a question? Both corpora punctuate them."""
    return line.rstrip().endswith(("?", "？"))


def echoes(html: str):
    """Yield (index, earlier, later, shared) for each echoing adjacent pair."""
    lines = turns(html)
    for i in range(len(lines) - 1):
        a, b = stems(lines[i]), stems(lines[i + 1])
        if len(a) < MIN_STEMS or len(b) < MIN_STEMS:
            continue
        if asked(lines[i]) and not asked(lines[i + 1]):
            # A question and its answer share words because that is what an answer
            # does. Only an echo that is not answering anything is a defect.
            continue
        shared = a & b
        if len(shared) >= MIN_STEMS and len(shared) / len(b) >= OVERLAP:
            yield i + 2, lines[i], lines[i + 1], sorted(shared)


def scan(paths: list[pathlib.Path]) -> int:
    bad = 0
    for p in paths:
        try:
            html = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for turn_no, earlier, later, shared in echoes(html):
            bad += 1
            print(f"\n{p}")
            print(f"  turn {turn_no} repeats turn {turn_no - 1} ({', '.join(shared)})")
            print(f"    {turn_no - 1}: {earlier}")
            print(f"    {turn_no}: {later}")
    print(f"\n{len(paths)} deck(s) checked · {bad} echo(es)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="deck files or directories to scan")
    ap.add_argument("--all", action="store_true", help="scan every deck in the repo")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[2]
    targets: list[pathlib.Path] = []
    if args.all:
        targets = sorted(root.glob("sandbox/drafts/*/tracks/**/lessons/*/lesson.html"))
    for raw in args.paths:
        p = pathlib.Path(raw)
        targets += sorted(p.rglob("lesson.html")) if p.is_dir() else [p]
    if not targets:
        ap.error("nothing to scan — give a path or --all")
    return scan(sorted(set(targets)))


if __name__ == "__main__":
    sys.exit(main())
