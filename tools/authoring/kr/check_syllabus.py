#!/usr/bin/env python3
"""Scan decks for grammar a later 과 owns.

「아직 아님」 binds the learner, not the tutor — the tutor's spoken
.section-subtitle is natural Korean and may run ahead of the syllabus. So the
blue script boxes, and the Japanese glosses, come out before scanning.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# form -> 과 that owns it. Only forms distinctive enough to grep literally.
OWNED = {
    "있어요": 16, "없어요": 16,
    "(으)세요": 18, "주세요": 19,
    "하고": 20, "한테": 20, "에게": 20,
    "보다": 23,
    "입니다": 24, "습니다": 24, "ㅂ니다": 24,
    "았어요": 25, "었어요": 25, "했어요": 25, "왔어요": 25, "갔어요": 25, "봤어요": 25,
    "지만": 28,
    "어떻게": 29,
    "고 싶": 31,
    "거예요": 32, "ㄹ게요": 33,
    "러 가": 34, "수 있어요": 35, "수 없어요": 35,
    "려고": 36,
    "도 돼요": 38, "면 돼요": 39, "야 돼요": 40, "야 해요": 40,
    "고 있어요": 41, "어 보세요": 42, "아 보세요": 42,
}
# The tutor's spoken script is <p class="section-subtitle">, and .tutor-note is
# the private coaching line on her screen — neither is learner-produced Korean.
STRIP = [
    # class may carry extra tokens ("section-subtitle spot"), so do not demand
    # the closing quote right after the name — that silently kept tutor lines in.
    re.compile(r'<p class="[^"]*\bsection-subtitle\b[^"]*".*?</p>', re.S),
    re.compile(r'<div class="[^"]*\btutor-note\b[^"]*".*?</div>', re.S),
    re.compile(r'<span class="hint-chip".*?</span>', re.S),
    re.compile(r'<span class="ja">.*?</span>', re.S),
    re.compile(r'<div class="ja">.*?</div>', re.S),
    re.compile(r"<!--.*?-->", re.S),
]

for deck in sorted((REPO / "sandbox/drafts/kr/tracks/2-core-patterns/courses").glob("*/lessons/*/lesson.html")):
    src = deck.read_text(encoding="utf-8")
    if "data-page-id" not in src:
        continue
    no = int(re.match(r"\d+", deck.parent.name).group())  # 과 100+ has three digits
    body = src
    for pat in STRIP:
        body = pat.sub(" ", body)
    hits = []
    for form, owner in OWNED.items():
        if owner > no and form in body:
            n = body.count(form)
            hits.append(f"{form}(과{owner})×{n}")
    print(f"{'✗' if hits else '✓'} 과 {no:<3} {deck.parent.name:<26} {' '.join(hits)}")
