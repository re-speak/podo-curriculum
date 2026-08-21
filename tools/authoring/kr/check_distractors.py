#!/usr/bin/env python3
"""Flag choose rows whose WRONG option is real Korean.

A good distractor is either an impossible form (좋아하으세요) or a real form
that is wrong in this slot for a reason the lesson taught (있으세요 for a
person). A bad one is a real form that is also CORRECT here — 과 52 had three
of those. This cannot be decided mechanically, so the script only surfaces
candidates: a distractor that appears somewhere in the track as ordinary
Korean — a model line, a hero sentence, an answer key — is a real form and
the row needs a human to say why it is wrong here.
"""
import argparse, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"
DEFAULT = TRACKS / "2-core-patterns"


def deck_paths(paths, every):
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [DEFAULT]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


def track_of(deck):
    """The track a deck sits in, or None outside sandbox/drafts/kr/tracks."""
    for parent in deck.parents:
        if parent.parent == TRACKS:
            return parent
    return None


ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
ap.add_argument("--strict", action="store_true",
                help="exit non-zero on candidates instead of only listing them")
args = ap.parse_args()

DECKS = deck_paths(args.paths, args.all)
# "real Korean elsewhere" is a claim about the whole track, so naming one deck
# must not shrink the corpus the distractor is weighed against.
ATTESTED_IN = sorted(set(DECKS).union(
    *(t.rglob("lesson.html") for t in {track_of(d) for d in DECKS} if t))) or DECKS

def txt(x):
    x = re.sub(r'<span class="yomi">.*?</span>', "", x, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()

# every string the track presents as correct Korean
attested = set()
for d in ATTESTED_IN:
    s = d.read_text(encoding="utf-8")
    for pat in (r'\bdata-answer="([^"]+)"',
                r'<span class="answer-space build-zone"[^>]*\bdata-a="([^"]+)"',
                r'<div class="model-line">.*?<span class="korean">(.*?)</span>',
                r'<div class="sent-hero">\s*<span class="korean">(.*?)</span>',
                r'<div class="bubble[^"]*"><span class="korean">(.*?)</span>'):
        for m in re.finditer(pat, s, re.S):
            t = txt(m.group(1))
            if t:
                attested.add(t)
attested_blob = " ⋮ ".join(attested)

rows = flagged = 0
for d in DECKS:
    s = d.read_text(encoding="utf-8")
    ms = list(re.finditer(r'data-page-id="([^"]+)"', s))
    for i, m in enumerate(ms):
        if "choose" not in m.group(1):
            continue
        page = s[m.start(): ms[i+1].start() if i+1 < len(ms) else len(s)]
        for r in re.finditer(r'<div class="choose-row[^"]*"[^>]*>(.*?)(?=<div class="choose-row|\Z)', page, re.S):
            body = r.group(1)
            ja = txt(re.search(r'<span class="translation">(.*?)</span>', body, re.S).group(1)) if re.search(r'<span class="translation">', body) else ""
            opts = [(txt(o.group(2)), "data-correct" in o.group(1))
                    for o in re.finditer(r'<span class="opt"([^>]*)>(.*?)</span>', body, re.S)]
            if len(opts) != 2:
                continue
            rows += 1
            wrong = [t for t, c in opts if not c]
            if not wrong:
                continue
            w = wrong[0].rstrip(".?!")
            if len(w) >= 2 and w in attested_blob:
                flagged += 1
                print(f"  과 {d.parent.name[:2]} {m.group(1):<12} {ja[:34]:<34} 오답 「{wrong[0]}」 는 다른 곳에서 정답으로 쓰인다")
print(f"\n{rows} choose rows, {flagged} with a distractor that is real Korean elsewhere")
print("advisory: a real form can still be the wrong one here — read each row "
      "before acting. --strict makes these fail.")
sys.exit(1 if args.strict and flagged else 0)
