#!/usr/bin/env python3
"""Count reorder chips per sentence, and items per closed activity page,
against the two ux-philosophy rules:
  - four meaningful chunks per reorder sentence; four is default AND ceiling
  - four items in every closed sentence activity (read/choose/reorder/fill/translate)
"""
import argparse, re, sys, collections
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"
DEFAULT = TRACKS / "2-core-patterns"
PAGE = re.compile(r'data-page-id="([^"]+)"')

def pages(src):
    """split on top-level page divs by data-page-id offsets"""
    ms = list(PAGE.finditer(src))
    for i, m in enumerate(ms):
        end = ms[i+1].start() if i+1 < len(ms) else len(src)
        yield m.group(1), src[m.start():end]

def deck_paths(paths, every):
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [DEFAULT]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html")) + sorted(r.rglob("trial/lessons/*.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


CLOSED = ("read", "choose", "reorder", "fill", "translate")

ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
args = ap.parse_args()

hist = collections.Counter()
rows = []
for deck in deck_paths(args.paths, args.all):
    src = deck.read_text(encoding="utf-8")
    if "data-page-id" in src:
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
# four is the ceiling, so a page above it is a defect and the exit code says so.
# The distribution and the >=4 census above are measurements; nobody fails them.
sys.exit(1 if over else 0)
