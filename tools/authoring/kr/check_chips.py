#!/usr/bin/env python3
"""Count reorder chips per sentence, and items per closed activity page,
against the two ux-philosophy rules:
  - four meaningful chunks per reorder sentence; four is default AND ceiling
  - four items in every closed sentence activity (read/choose/reorder/fill/translate)
"""
import re, sys, collections
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PAGE = re.compile(r'data-page-id="([^"]+)"')

def pages(src):
    """split on top-level page divs by data-page-id offsets"""
    ms = list(PAGE.finditer(src))
    for i, m in enumerate(ms):
        end = ms[i+1].start() if i+1 < len(ms) else len(src)
        yield m.group(1), src[m.start():end]

CLOSED = ("read", "choose", "reorder", "fill", "translate")

hist = collections.Counter()
rows = []
for track in sys.argv[1:] or ["2-core-patterns"]:
    base = REPO / "sandbox/drafts/kr/tracks" / track
    decks = sorted(base.glob("courses/*/lessons/*/lesson.html"))
    decks += sorted(base.glob("trial/lessons/*.html"))
    for deck in decks:
        src = deck.read_text(encoding="utf-8")
        if "data-page-id" not in src: continue
        for pid, chunk in pages(src):
            kind = next((k for k in CLOSED if k in pid), None)
            if not kind: continue
            blocks = re.findall(r'<div class="task-block[^"]*">(.*?)(?=<div class="task-block|\Z)', chunk, re.S)
            if kind == "reorder":
                counts = [len(re.findall(r'class="choice"', b)) for b in blocks]
                if counts:
                    for c in counts: hist[c] += 1
                    rows.append((deck.parent.name, pid, counts))
print("chips per reorder sentence — distribution")
for n in sorted(hist): print(f"  {n} chips: {hist[n]:>4} sentences")
print(f"  total {sum(hist.values())} sentences, mean {sum(k*v for k,v in hist.items())/max(1,sum(hist.values())):.2f}")
print()
four = [r for r in rows if all(c >= 4 for c in r[2])]
print(f"reorder pages where every sentence has >=4 chips: {len(four)}/{len(rows)}")
over = [r for r in rows if any(c > 4 for c in r[2])]
print(f"reorder pages with any sentence over 4 chips: {len(over)}")
for r in over[:10]: print("   ", r)
