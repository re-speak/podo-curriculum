#!/usr/bin/env python3
"""What a course is called — the one place both corpora agree.

A course says its level three times over: `spec.difficulty` drives the app's
level filter, `spec.title` puts the word in front of the learner, and the cover
pill repeats it on the card. Nothing joined those three, so they drifted:
`hangul-starter` was `BEGINNER` and called itself `Starter`, `trial-lv2` was
`UPPER_BEGINNER` and called itself `Elementary`, and until 2026-08-25 the whole
Korean corpus put its level at the *end* of the title while English put it in
front. Every one of those is invisible in review and wrong on the learner's
screen.

So the level word, the family name and the ladder position live here, once, and
three callers read them:

    tools/authoring/course_covers/generate.py   the card — pill and cover title
    tools/validate.py                           the gate — layer 2
    tools/authoring/{kr,en}/plan_courses.py     the generators

`title_for` composes; `problems` recomposes what is on disk and fails on any
difference. That is the whole anti-drift mechanism: a title cannot disagree with
its own `difficulty` or with its neighbours' numbering without failing the PR.

The shape, both corpora, all three languages:

    (初級) コアパターン 1          level · family · its place on the ladder
    (中級) ドラマ · 友だちになるまで   level · family · topic
    (中級) 最近のわたし             level · topic          (the family is the rail header)
    (初中級) タメ口への切り替え        the family is already in the topic, so it is not repeated
"""

from __future__ import annotations

import dataclasses
import re


# The five words a learner already sees on the level filter, verbatim from
# podo-app `apps/web/src/shared/config/i18n/messages/{ko,ja,en}.json`
# (`subscribeList.filters.level.*`). Taking them from there rather than writing
# our own is what makes the title, the cover and the filter chip agree — and it
# is why CEFR is gone: `A2–B1` and `B1+` are not buckets the filter has, so a
# course could not be filtered to the level it claimed.
LEVEL_WORDS = {
    "ko": {"BEGINNER": "초급", "UPPER_BEGINNER": "초중급", "INTERMEDIATE": "중급",
           "UPPER_INTERMEDIATE": "중고급", "ADVANCED": "고급"},
    "en": {"BEGINNER": "Beginner", "UPPER_BEGINNER": "Upper Beginner",
           "INTERMEDIATE": "Intermediate", "UPPER_INTERMEDIATE": "Upper Intermediate",
           "ADVANCED": "Advanced"},
    "ja": {"BEGINNER": "初級", "UPPER_BEGINNER": "初中級", "INTERMEDIATE": "中級",
           "UPPER_INTERMEDIATE": "中上級", "ADVANCED": "上級"},
}

LANGS = ("ko", "en", "ja")

# The language a corpus teaches. It is what the cover puts in large type, and
# the support language (Japanese for both, `countryCode: JP`) is what the pill
# is written in.
TAUGHT = {"kr": "ko", "en": "en"}


@dataclasses.dataclass(frozen=True)
class Family:
    """A family is the unit a learner compares within.

    `pill` is Japanese only and deliberately shorter than `label`: the pill has
    120 px and has to hold a number and a level word beside it, so core is
    `パターン` there and `コアパターン` in the title. They are two renderings of
    one name, kept adjacent so they cannot drift apart unnoticed.

    `label` is `None` where the rail header already says it — a free-talking
    card sitting under the フリートーク header does not need to say it twice.
    """

    pill: str
    label: dict[str, str] | None = None


FAMILY = {
    "core":     Family("パターン", {"ko": "핵심 패턴", "en": "Core", "ja": "コアパターン"}),
    "drama":    Family("ドラマ", {"ko": "드라마", "en": "Drama", "ja": "ドラマ"}),
    "kpop":     Family("K-POP", {"ko": "케이팝", "en": "K-pop", "ja": "K-POP"}),
    "travel":   Family("旅行", {"ko": "여행", "en": "Travel", "ja": "旅行"}),
    "banmal":   Family("タメ口", {"ko": "반말", "en": "Banmal", "ja": "タメ口"}),
    "business": Family("ビジネス", {"ko": "비즈니스", "en": "Business", "ja": "ビジネス"}),
    "hangul":   Family("ハングル"),
    "trial":    Family("体験"),
    "talk":     Family("フリートーク"),
}

# Families whose courses run in a fixed order, so the position is a fact and the
# pill carries it. Korean travel is not one of them — 식당 · 쇼핑 · 숙소 · 길 are
# four places on one trip, not four steps — but the English travel and business
# runs are ordered by classLevel from A2 to C1.
NUMBERED = ("core", "drama", "kpop", "banmal", "business")

# Where the number *is* the name. A Korean core course has no topic of its own —
# `core-upper-beginner-1` is the fifth rung and nothing else — so its title ends
# in that rung rather than in a phrase. English core courses are named
# (`core-first-exchanges-1` is 最初の一文), so they are not on this list.
NUMBER_IS_NAME = {("kr", "core")}

# Level words a title may not carry inside its topic — the five live ones in all
# three languages, plus the four this repository has already retired. The level
# belongs in the parentheses and nowhere else; `ハングル入門 · 超入門` said it twice
# and said it wrong, and only the half in the parentheses is checked against
# `difficulty`, so a word left in the topic is a claim nothing can verify.
RETIRED_LEVEL_WORDS = ("왕초급", "超入門", "Starter", "Elementary")
STRAY_LEVEL_WORDS = frozenset(
    list(RETIRED_LEVEL_WORDS)
    + [word for words in LEVEL_WORDS.values() for word in words.values()])


def numbered(corpus: str, family: str) -> bool:
    return family in NUMBERED or (corpus == "en" and family == "travel")


def family_of(corpus: str, slug: str) -> str:
    if slug.startswith("trial-"):
        return "trial"
    if "hangul" in slug:
        return "hangul"
    if slug.startswith("core-"):
        return "core"
    if slug.startswith("talk-"):
        return "talk"
    for family in ("drama", "kpop", "banmal", "business", "travel"):
        if family in slug:
            return family
    return "talk"


# ---------------------------------------------------------------- position

def ladder(courses) -> dict[tuple[str, str], int]:
    """Each course's place among its enabled siblings, in catalogue order.

    `classLevel` is the catalogue order, so it is what the count reads. Only
    enabled courses count, so retiring one closes the gap rather than leaving a
    hole — which is why this cannot be derived from the slug: `core-beginner-4`
    is the fourth rung only for as long as no earlier one is switched off.

    `courses` is anything with `.corpus`, `.slug`, `.class_level`, `.enabled`.
    """
    rows = sorted((c.corpus, family_of(c.corpus, c.slug), float(c.class_level), c.slug)
                  for c in courses if c.enabled)
    place, seen = {}, {}
    for corpus, family, _, slug in rows:
        seen[(corpus, family)] = seen.get((corpus, family), 0) + 1
        place[(corpus, slug)] = seen[(corpus, family)]
    return place


# ---------------------------------------------------------------- the title

def _parts(text: str) -> list[str]:
    return [part.strip() for part in text.split(" · ") if part.strip()]


def _leads_with(topic: str, label: str) -> bool:
    """Does the topic already open with the family name?

    `タメ口 · タメ口への切り替え` and `케이팝 · 케이팝 토크` say it twice; the
    prefix is noise there because the topic already carries the family. The same
    course can repeat in one language and not another — `반말 · 말 놓기` reads
    fine — so this is decided per language, on the string.

    *Leads with*, not *contains*: `여행 · 혼자 하는 여행` keeps its prefix, because
    the family is where the topic ends up rather than what it starts as. And a
    Latin label has to end on a boundary, or `Travel` swallows `Travelling
    alone` and a live English course silently loses its rail name.
    """
    if not topic.casefold().startswith(label.casefold()):
        return False
    tail, head = label[-1:], topic[len(label):len(label) + 1]
    return not (tail.isascii() and tail.isalnum() and head.isascii() and head.isalnum())


def title_for(corpus: str, slug: str, lang: str, topic: str,
              difficulty: str, rung: int | None) -> str:
    """`(level) [family · ]topic`, in one of ko / en / ja."""
    family = family_of(corpus, slug)
    level = LEVEL_WORDS[lang].get(difficulty, difficulty)
    label = FAMILY[family].label

    if (corpus, family) in NUMBER_IS_NAME:
        rest = f"{label[lang]} {rung}" if rung else label[lang]
    elif label and not _leads_with(topic, label[lang]):
        rest = f"{label[lang]} · {topic}"
    else:
        rest = topic
    return f"({level}) {rest}"


def topic_of(corpus: str, slug: str, lang: str, title: str) -> str:
    """The topic back out of a composed title — the inverse of `title_for`.

    Round-tripping is what lets `problems` recompose a title from the file it is
    checking: everything except the topic is derived, so everything except the
    topic can be checked.
    """
    family = family_of(corpus, slug)
    rest = re.sub(r"^\([^)]*\)\s*", "", title)
    label = FAMILY[family].label

    # `(초급) 핵심 패턴 1` — the family and the rung are one part, not two, so
    # what comes back is the rung. `title_for` recomposes it from `classLevel`
    # rather than from this, but the catalogue puts it in the unit header and a
    # core course whose name is nothing at all is a blank line on the site.
    if (corpus, family) in NUMBER_IS_NAME:
        return rest[len(label[lang]):].strip() if rest.startswith(label[lang]) else rest

    parts = _parts(rest)
    if label and len(parts) > 1 and parts[0] == label[lang]:
        parts = parts[1:]
    return " · ".join(parts)


# ---------------------------------------------------------------- the cover

def cover_copy(corpus: str, slug: str, titles: dict, difficulty: str,
               rung: int | None) -> tuple[str, str]:
    """(pill, cover title).

    The pill is `family [position] · level`, the cover title is the topic in the
    language being taught. Both read the tables above, so the number on the card
    is the number in the title beside it and the level word on the card is the
    word on the filter chip.

        ドラマ 2 · 中級   パターン 3 · 初級   旅行 · 初中級   フリートーク · 上級
    """
    family = family_of(corpus, slug)
    level = LEVEL_WORDS["ja"].get(difficulty, difficulty)
    lang = TAUGHT[corpus]
    label = FAMILY[family]

    topic = topic_of(corpus, slug, lang, titles[lang])
    if (corpus, family) in NUMBER_IS_NAME:
        topic = f"{label.label[lang]} {rung}" if rung else label.label[lang]

    if numbered(corpus, family) and rung:
        return f"{label.pill} {rung} · {level}", topic
    return f"{label.pill} · {level}", topic


# ---------------------------------------------------------------- the gate

def problems(courses) -> list[str]:
    """Every way a title can disagree with the rest of its own course.

    The topic is the only part not derived, so it is the only part not checked.
    Everything else — the level word against `difficulty`, the family against
    the slug, the rung against `classLevel`, the parentheses, the separator, the
    repeated family name — is recomposed here and compared.
    """
    rungs, found = ladder(courses), []
    for course in courses:
        rung = rungs.get((course.corpus, course.slug))
        for lang in LANGS:
            have = course.title.get(lang)
            if not have:
                found.append(f"{course.corpus}/{course.slug}: spec.title.{lang} is missing")
                continue
            topic = topic_of(course.corpus, course.slug, lang, have)
            want = title_for(course.corpus, course.slug, lang, topic,
                             course.difficulty, rung)
            if have != want:
                found.append(f"{course.corpus}/{course.slug}: spec.title.{lang} is "
                             f"{have!r}, but {course.difficulty} on classLevel "
                             f"{course.class_level} composes {want!r}")
            stray = [word for word in STRAY_LEVEL_WORDS if word in topic]
            if stray:
                found.append(f"{course.corpus}/{course.slug}: spec.title.{lang} says its "
                             f"level twice — {', '.join(sorted(stray))} is in the topic, "
                             f"and only the parentheses are checked against difficulty")
    return found


@dataclasses.dataclass(frozen=True)
class Row:
    """The five fields a name is made of, for callers that have no Course object."""

    corpus: str
    slug: str
    class_level: float
    difficulty: str
    enabled: bool
    title: dict
