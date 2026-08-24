#!/usr/bin/env python3
"""Audit the eight spoken prompts of every Freetalking deck, in both curricula.

`check_deck.py` proves a deck is well formed and `kr/check_freetalk.py` proves it
has the right pages.  Both were green on a corpus where 54% of the English level
pairs printed byte-identical questions, another 16% differed by one synonym, and
62% of all 1,936 prompts never said "you" — because nothing here could see a
question as a *question*.

Three rules, each traceable to a real defect found in the shipped corpus:

**Full is the source conversation.** It is written first as the most natural,
interesting and immediately answerable version. Accessible may be identical. A
near-identical pair whose only change is `surprised` → `genuinely surprised` is
reported as a warning because that is cosmetic adaptation, not because the two
levels are required to diverge.

**The learner must be in the question.**  `What can make a useful item stop
feeling worth it?` has no person in it, so there is nothing to retrieve and
nothing to follow up.  A prompt addressed to nobody is a survey item.

**A prompt is one job.**  Two question marks, or two requests joined by `and`,
give the learner a choice to make before they can start answering.

Warnings cover the judgement calls — an over-long prompt, a missing inversion on
`q6` — and never block.

    python3 tools/authoring/check_freetalk_questions.py            # both curricula
    python3 tools/authoring/check_freetalk_questions.py --lang en
    python3 tools/authoring/check_freetalk_questions.py --warnings
"""
from __future__ import annotations

import argparse
import difflib
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

TRACKS = {
    "en": (REPO / "sandbox/drafts/en/tracks/3-freetalking/courses", ("accessible", "full")),
    "kr": (REPO / "sandbox/drafts/kr/tracks/4-freetalking/courses", ("intermediate", "advanced")),
}

# A non-identical pair above this ratio usually changed for no useful reason.
# It is advisory: an identical natural question is explicitly valid.
LEVEL_SIMILARITY_MAX = 0.80
# The lower level stays short enough to answer without re-parsing; the upper one
# may carry a second clause, but length is a symptom, not the level itself.
PROMPT_WORDS_MAX = {"lower": 16, "upper": 22}
FOLLOWUPS = (2, 3)

QUESTION = re.compile(
    r'<span class="q-n">([^<]+)</span><span class="ko">(.*?)</span><span class="ja">(.*?)</span>',
    re.S,
)
FOLLOWUP_BLOCK = re.compile(r'<ul class="tn-more">(.*?)</ul>', re.S)
FOLLOWUP_ITEM = re.compile(r"<li>(.*?)</li>", re.S)

# The defect is not a missing "you" — it is a prompt with no one and nothing in
# it.  `What can make a useful item stop feeling worth it?` fails because
# `a useful item` is an indefinite the learner has to invent before answering,
# while `When is that dish at its best?` is fine: `that dish` is the thing they
# named one page earlier.  So a prompt passes when it reaches *someone in the
# room* (you / I / we) or *something already on the table* (that, it, those) —
# and when it does neither, the generic subject is the reason it is dead.
EN_ADDRESS = re.compile(r"\b(you|your|yours|yourself)\b", re.I)
EN_ROOM = re.compile(r"\b(i|me|my|mine|we|us|our)\b", re.I)
EN_DEICTIC = re.compile(r"\b(that|those|it|its|them|their|this|these|there)\b", re.I)
EN_IMPERATIVE = re.compile(r"^(tell|sell|talk|ask|describe|give|choose|pick|convince|imagine|think|walk|take)\b", re.I)
KR_ADDRESS = re.compile(r"(요\?|까\?|나요|세요|봐요|어요|아요|예요|이에요)")

INVERSION = {"en": re.compile(r"^now the opposite\b", re.I), "kr": re.compile(r"(반대로|거꾸로)")}


def text(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def prompts(deck: Path):
    source = deck.read_text(encoding="utf-8")
    found = [(label, text(en), text(ja)) for label, en, ja in QUESTION.findall(source)]
    follow = [FOLLOWUP_ITEM.findall(block) for block in FOLLOWUP_BLOCK.findall(source)]
    return found, follow


def pairs(root: Path, variants: tuple[str, str]):
    lower_suffix, upper_suffix = variants
    for course in sorted(root.glob(f"*-{lower_suffix}")):
        theme = course.name[: -len(lower_suffix) - 1]
        upper = root / f"{theme}-{upper_suffix}"
        if not upper.is_dir():
            continue
        for lesson in sorted((course / "lessons").iterdir()):
            sibling = upper / "lessons" / lesson.name / "lesson.html"
            deck = lesson / "lesson.html"
            if deck.exists() and sibling.exists():
                yield theme, lesson.name, deck, sibling


def audit(lang: str, root: Path, variants: tuple[str, str]):
    errors: list[str] = []
    warnings: list[str] = []
    for theme, lesson, lower_deck, upper_deck in pairs(root, variants):
        where = f"{lang} {theme}/{lesson}"
        lower, lower_follow = prompts(lower_deck)
        upper, upper_follow = prompts(upper_deck)
        if len(lower) != len(upper):
            errors.append(f"{where}: {len(lower)} prompts at {variants[0]} vs {len(upper)} at {variants[1]}")
            continue

        for index, ((label, low_en, _low_ja), (_l2, up_en, _up_ja)) in enumerate(zip(lower, upper)):
            slot = label.strip()
            if low_en != up_en:
                ratio = difflib.SequenceMatcher(None, low_en, up_en).ratio()
                if ratio > LEVEL_SIMILARITY_MAX:
                    warnings.append(
                        f"{where} {slot}: adaptation may be cosmetic ({ratio:.0%} identical)\n"
                        f"      {variants[0]}: {low_en}\n      {variants[1]}: {up_en}"
                    )

            for variant, prompt in ((variants[0], low_en), (variants[1], up_en)):
                errors.extend(f"{where} {slot} {variant}: {problem}" for problem in prompt_problems(lang, prompt))
                limit = PROMPT_WORDS_MAX["lower" if variant == variants[0] else "upper"]
                words = len(re.findall(r"[^\s]+", prompt))
                if words > limit:
                    warnings.append(f"{where} {slot} {variant}: {words} words (over {limit}) — {prompt}")

        for variant, sets in ((variants[0], lower_follow), (variants[1], upper_follow)):
            for index, items in enumerate(sets):
                if not FOLLOWUPS[0] <= len(items) <= FOLLOWUPS[1]:
                    errors.append(f"{where} follow-up set {index + 1} {variant}: {len(items)} items, want {FOLLOWUPS[0]}–{FOLLOWUPS[1]}")
    return errors, warnings


def prompt_problems(lang: str, prompt: str) -> list[str]:
    problems = []
    if prompt.count("?") > 1:
        problems.append(f'two questions in one prompt — "{prompt}"')
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lang", choices=sorted(TRACKS), action="append", help="limit to one curriculum")
    parser.add_argument("--warnings", action="store_true", help="print the soft findings too")
    parser.add_argument("--summary", action="store_true", help="counts only")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    for lang in args.lang or sorted(TRACKS):
        root, variants = TRACKS[lang]
        if not root.is_dir():
            continue
        found, soft = audit(lang, root, variants)
        errors += found
        warnings += soft

    if not args.summary:
        for line in errors:
            print(f"error: {line}")
        if args.warnings:
            for line in warnings:
                print(f"warning: {line}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
