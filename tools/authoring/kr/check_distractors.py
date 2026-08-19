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
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DECKS = sorted((REPO / "sandbox/drafts/kr/tracks/2-core-patterns/courses").glob("*/lessons/*/lesson.html"))

def txt(x):
    x = re.sub(r'<span class="yomi">.*?</span>', "", x, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()

# every string the track presents as correct Korean
attested = set()
for d in DECKS:
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
