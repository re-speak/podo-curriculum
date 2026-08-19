#!/usr/bin/env python3
"""Generate disabled English course manifests from the approved TOC cuts.

The destination directory in podo-curriculum supplies LANG_TYPE=EN. These
manifests supply the learner market as countryCode=JP; the two fields are not
interchangeable. Prestudy is still deferred, so this generator intentionally
writes course.yaml only and never creates a deployable lesson.yaml.

    python3 tools/authoring/en/plan_courses.py --all
    python3 tools/authoring/en/plan_courses.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import pathlib

import track_parsers

ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
VALID_COUNTRY_CODES = {"KR", "JP"}
MARKET_COUNTRY_CODE = "JP"
COPY_PATH = pathlib.Path(__file__).resolve().parent / "course-copy.json"

# GT_CLASS_COURSE keeps three name columns and the app picks one by locale, so
# a catalogue entry is only complete when all three are written. Live cover
# rows average 13 characters in ko and 22 in en; these ceilings are the loosest
# limit that still keeps a title short enough to read in a list. See
# course-copy.json for why the CJK ceiling is 30 rather than the live 22.
TITLE_LIMITS = {"ko": 30, "en": 40, "ja": 30}
LANGS = ("ko", "en", "ja")

CORE = (
    ("core-first-exchanges-1", 1, 11),
    ("core-first-exchanges-2", 12, 24),
    ("core-daily-life-and-past", 25, 36),
    ("core-plans-and-comparison", 37, 47),
    ("core-experience-and-ideas", 48, 59),
    ("core-careful-interaction", 60, 70),
    ("core-work-and-arrangements", 71, 80),
    ("core-nuance-at-work", 81, 91),
    ("core-diplomacy-and-reasoning", 92, 102),
    ("core-emphasis-and-tone", 103, 112),
    ("core-advanced-stance", 113, 122),
)

CONTEXTUAL = (
    "ctx-travel-arrivals-transport",
    "ctx-travel-hotels-food",
    "ctx-travel-disruptions-urgent-problems",
    "ctx-travel-independent-social",
    "ctx-travel-complex-decisions",
    "ctx-business-workplace-essentials",
    "ctx-business-projects-deadlines",
    "ctx-business-meetings-decisions",
    "ctx-business-negotiation-diplomacy",
    "ctx-business-leadership-high-stakes",
)

FREETALKING_SLUGS = (
    "between-two-countries", "me-lately", "things-i-like", "small-things",
    "people-and-ties", "love-and-marriage", "work-and-money",
    "what-came-before", "what-if", "worth-thinking-about", "balance-games",
)


def market_country_code(value: str | None) -> str:
    if value is None:
        raise ValueError("countryCode is required")
    if value not in VALID_COUNTRY_CODES:
        raise ValueError(
            f"countryCode must be one of {sorted(VALID_COUNTRY_CODES)}; got {value!r}")
    if value != "JP":
        raise ValueError(
            f"Japanese-market English courses require countryCode JP; got {value!r}")
    return value


def yaml_str(value: str) -> str:
    value = value.replace("\n", " ").strip()
    if value == "" or value[0] in "!&*[]{}>|%@`'\"#-?:," or ": " in value or " #" in value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


# CEFR band -> GT_CLASS_COURSE.DIFFICULTY. The live catalogue is five bands
# wide and leans on the two this used to discard: UPPER_BEGINNER and
# UPPER_INTERMEDIATE hold more deployed lessons than BEGINNER, INTERMEDIATE and
# ADVANCED together. The old rule read "B2" anywhere in the string and returned
# ADVANCED, which filed a B1+ → B2 course beside a C1 one.
#
# Read highest-first: a course spanning "A2 → B1" is entered at its ceiling,
# because difficulty is what the learner needs to finish it, not to start.
CEFR_DIFFICULTY = (
    ("C1", "ADVANCED"),
    ("B2", "UPPER_INTERMEDIATE"),
    ("B1+", "UPPER_INTERMEDIATE"),
    ("B1", "INTERMEDIATE"),
    ("A2", "UPPER_BEGINNER"),
    ("A1", "BEGINNER"),
)


def _level(value: str) -> str:
    for band, difficulty in CEFR_DIFFICULTY:
        if band in value:
            return difficulty
    return "BEGINNER"


def course_copy() -> dict[str, dict]:
    """Learner-facing title and description per slug. See course-copy.json."""
    return json.loads(COPY_PATH.read_text(encoding="utf-8"))["courses"]


def copy_for(slug: str, field: str, fallback: str, copy: dict[str, dict]) -> dict[str, str]:
    """One three-language field, falling back to the derived English string.

    The fallback keeps the generator runnable while a new course is being
    written, and never reaches production: `missing_copy` reports it and the
    test suite fails on it.
    """
    written = copy.get(slug, {}).get(field, {})
    return {lang: written.get(lang) or fallback for lang in LANGS}


def missing_copy(slug: str, copy: dict[str, dict]) -> list[str]:
    """Report every title/description language this course has not been given."""
    gaps = []
    for field in ("title", "description"):
        written = copy.get(slug, {}).get(field, {})
        gaps += [f"{field}.{lang}" for lang in LANGS if not written.get(lang)]
        for lang, limit in TITLE_LIMITS.items():
            if field == "title" and len(written.get(lang, "")) > limit:
                gaps.append(f"title.{lang} is {len(written[lang])} chars, over {limit}")
    return gaps


def planned_courses() -> list[dict]:
    courses: list[dict] = []

    core = track_parsers.parse_core()
    for index, (slug, start, end) in enumerate(CORE, start=1):
        lessons = [lesson for lesson in core if start <= lesson["no"] <= end]
        units = list(dict.fromkeys(lesson["unit"] for lesson in lessons))
        first_level, last_level = lessons[0]["level"], lessons[-1]["level"]
        level = (last_level if first_level in last_level else f"{first_level} → {last_level}") \
            if first_level != last_level else first_level
        courses.append({
            "track": "1-core-patterns", "slug": slug,
            "classLevel": f"100.{index * 10:03d}",
            "title": "English Core · " + " & ".join(units),
            "description": f"Core {start}–{end} · {level}",
            "difficulty": _level(level), "lessons": lessons,
        })

    contextual = track_parsers.parse_contextual()
    for course_no, slug in enumerate(CONTEXTUAL, start=1):
        lessons = [lesson for lesson in contextual if lesson["courseNo"] == course_no]
        courses.append({
            "track": "2-contextual-english", "slug": slug,
            "classLevel": f"200.{course_no * 10:03d}",
            "title": lessons[0]["course"],
            "description": f"{lessons[0]['area']} · {lessons[0]['level']}",
            "difficulty": _level(lessons[0]["level"]), "lessons": lessons,
        })

    freetalking = track_parsers.parse_freetalking()
    for theme_no in range(1, 12):
        lessons = [lesson for lesson in freetalking if lesson["themeNo"] == theme_no]
        theme = lessons[0]["theme"]
        bare = FREETALKING_SLUGS[theme_no - 1]
        for version, suffix, slot, difficulty in (
                ("Accessible", "accessible", theme_no * 10 - 1, "INTERMEDIATE"),
                ("Full", "full", theme_no * 10, "ADVANCED")):
            courses.append({
                "track": "3-freetalking", "slug": f"talk-{bare}-{suffix}",
                "classLevel": f"3100.{slot:03d}",
                "title": f"Free talking · {theme} · {version}",
                "description": f"{len(lessons)} topics · {version} version",
                "difficulty": difficulty, "lessons": lessons,
            })
    return courses


def course_yaml(course: dict, country_code: str | None = MARKET_COUNTRY_CODE,
                copy: dict[str, dict] | None = None) -> str:
    plan = "\n".join(
        f"#   {lesson['no']:>3}  ·  {lesson['id']} · {lesson['title']}"
        for lesson in course["lessons"]
    )
    copy = course_copy() if copy is None else copy
    title = "\n".join(
        f"    {lang}: {yaml_str(value)}" for lang, value in
        copy_for(course["slug"], "title", course["title"], copy).items())
    description = "\n".join(
        f"    {lang}: {yaml_str(value)}" for lang, value in
        copy_for(course["slug"], "description", course["description"], copy).items())
    return f"""\
apiVersion: podo.curriculum/v1
kind: Course
metadata:
  # Generated from the approved {course['track']} course cut.
  # LANG_TYPE is not stored here: podo-curriculum derives EN from courses/en/.
  slug: {course['slug']}

spec:
  curriculumType: BASIC
  countryCode: {market_country_code(country_code)}
  # classLevel and countryCode are natural-key fields. Changing either creates
  # a different course identity rather than updating the deployed row.
  classLevel: "{course['classLevel']}"
  lessonTime: 25
  # English remains pre-production; generation must never enable a course.
  enabled: false
  difficulty: {course['difficulty']}

  # Three name columns, three descriptions: the app picks by locale, so `ja` is
  # what this Japanese-market track puts on screen and `ko` is grape's admin
  # label. Both come from tools/course-copy.json, never from the TOC — a
  # generated title was English in all three slots and 72 characters long.
  title:
{title}

  description:
{description}

  tutorGroups:
    allowRandom: []
    assignedOnly: []

# Planned lessons only. Prestudy is deferred, so this generator intentionally
# does not create lesson.yaml or represent any English lesson as deployable.
{plan}
# Generated by tools/authoring/en/plan_courses.py — edit the TOC/mapping and re-run.
"""


def generate(track: str | None, dry_run: bool) -> int:
    courses = [course for course in planned_courses()
               if track is None or course["track"] == pathlib.Path(track).name]
    if not courses:
        raise ValueError(f"no generated course plan for {track!r}")
    copy = course_copy()
    for course in courses:
        target = ROOT / "tracks" / course["track"] / "courses" / course["slug"] / "course.yaml"
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(course_yaml(course, copy=copy), encoding="utf-8")
        print(f"{course['track']:<24} {course['slug']:<50} {course['classLevel']}  "
              f"{len(course['lessons']):>3} planned")
        for gap in missing_copy(course["slug"], copy):
            print(f"    ! {gap} — tools/course-copy.json")
    print(f"\n{len(courses)} English course(s)"
          f"{' — dry run, nothing written' if dry_run else ''}")
    return len(courses)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("track", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.all == bool(args.track):
        return parser.error("give one track path or --all")
    generate(None if args.all else args.track, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
