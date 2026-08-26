#!/usr/bin/env python3
"""Lay a track out as courses, in the shape podo-curriculum deploys.

    python3 tools/authoring/kr/plan_courses.py sandbox/drafts/kr/tracks/3-contextual-korean
    python3 tools/authoring/kr/plan_courses.py --all

A track is not a course. A deployable course is one `classLevel` with weeks
running 1..N and no gaps, so every track has to be cut into courses before any of
it can ship. Doing that cut here, against the table of contents, means the
production importer copies a plan instead of inventing one.

Most tracks already say where the cuts go — `3-contextual-korean` is named shows
of ten episodes, `4-freetalking` is themes of ten sessions, `1-hangul` and
`5-pronunciation` are one course each. Only `2-core-patterns` has to be packed,
because 116 numbered 과 have no course boundaries of their own; there the packer
groups units into roughly twelve lessons without ever splitting a unit, so a
course always ends on its 체크포인트.

Reading each TOC is `track_parsers.py`'s job. This file only turns courses into
YAML.

Layout written under the track:

    courses/<course-slug>/course.yaml
    courses/<course-slug>/lessons/<lesson-slug>/lesson.yaml
    courses/<course-slug>/lessons/<lesson-slug>/lesson.html   <- the deck, if written

Both validate against podo-curriculum's `schemas/`.

**`course.yaml` for every course; `lesson.yaml` only where a deck exists.** The
lesson schema wants a slug of `NN-english-words`, and the English name is a
writing decision that does not exist before the lesson does — scaffolding 350 of
them would be 350 renames later. The plan still shows up: each course lists its
lessons as comments, so a diff shows what is coming without pretending it is here.

**Weeks are provisional until a course is complete**, because `_check_weeks`
demands 1..N with no gaps, so week is the position among lessons that exist. Safe
only because an incomplete course is `enabled: false` and never applied.

**This tool never deletes a directory holding a deck.** It owns the YAML; a
`lesson.html` is handwritten work, so a lesson orphaned by a re-plan is reported,
not removed.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import course_naming as naming  # noqa: E402  (path set above)
import track_parsers

VALID_COUNTRY_CODES = {"KR", "JP"}
MARKET_COUNTRY_CODE = "JP"

# --- 2-core-patterns packing ------------------------------------------------
TARGET = 12            # a course should look like the ones already shipping
MAX_AFTER_MERGE = 15   # a trailing stub may join the previous course up to this
MERGE_IF_UNDER = 5

# classLevel is part of grape's natural key, so two courses sharing one are the
# same row.
#
# CLASS_LEVEL is also used by hard-coded backend ranges. Existing data follows
# an integer-band convention, but a band does not create a new app section by
# itself — the backend and app still need an explicit label/filter for that range:
#
#     1–2          the graded ladder (level 1, level 2)
#     1000         Breaking News          (15 courses, monthly × level)
#     1001, 1002   single topic courses
#     2001–2006    the Business series
#     3500         가벼운 프리토킹          (12 courses)
#     999          test junk — 'html test (john)' lives here
#
# Give each Korean track its own 100-level band. Primary course positions advance
# by 0.010, leaving nine 0.001 insertion slots between neighbours. When the
# fractional part is exhausted the sequence continues normally (200.990,
# 201.000, 201.010, ...), so one section can hold 9,999 primary positions.
# Keeping the bands below 1000 matters: the current BASIC query treats >=1000 as
# legacy special content (Breaking News / free talking), while <1000 remains in
# the regular BASIC ladder. 999.x is also the wrong home: throwaway rows live there.
#
# LANG_TYPE already separates KR from EN/JP, so these bands cannot collide with
# the English or Japanese curricula even where the numbers coincide. Audience
# ("Korean for Japanese speakers" vs anything later) is GT_CLASS_COURSE.
# COUNTRY_CODE, not this number — see AGENTS.md § Getting a lesson to production.
# curriculumType is a supported product line, not a content-edition number.
# podo-app, podo-backend, and grape all know BASIC; none supports invented
# version-suffixed variants. Using
# BASIC also makes tutor assignment use the supported PODO_KR_BASIC key. A future
# English curriculum generation should likewise stay BASIC and receive unused
# CLASS_LEVEL values; do not invent BASIC_V3.
#
# `prefix` and `name` make every course say which track and level it belongs to.
# A slug is <prefix>-<bare>-<level>, so `drama-crush` — which told you nothing —
# is now `ctx-drama-crush-intermediate`, and a directory listing groups by track
# and then by course, with the level last. Single-course tracks drop the bare part.
TRACKS = {
    "1-hangul":            {"band": 100, "type": "BASIC", "prefix": "hangul",
                            "name": {"ko": "한글 떼기", "en": "Hangul reading",
                                     "ja": "ハングル入門"}},
    # levelFirst: core's bare name is only a counter, so the level *is* its
    # identity and the number just orders within it. Level-last would sort
    # core-1-advanced next to core-1-beginner and hide the progression. Every
    # other track has a real name (a show, a theme), which is what should sort.
    "2-core-patterns":     {"band": 200, "type": "BASIC", "prefix": "core",
                            "levelFirst": True,
                            "name": {"ko": "핵심 문법 패턴", "en": "Core grammar patterns",
                                     "ja": "コア文法パターン"}},
    "3-contextual-korean": {"band": 300, "type": "BASIC", "prefix": "ctx",
                            "name": {"ko": "상황별 한국어", "en": "Korean in context",
                                     "ja": "場面別の韓国語"}},
    "4-freetalking":       {"band": 400, "type": "BASIC", "prefix": "talk",
                            "name": {"ko": "프리토킹", "en": "Free talking",
                                     "ja": "フリートーキング"}},
    "5-pronunciation":     {"band": 500, "type": "BASIC", "prefix": "pron",
                            "name": {"ko": "발음 교정", "en": "Pronunciation repair",
                                     "ja": "発音の矯正"}},
}

# GT_CLASS_COURSE.DIFFICULTY is five bands wide and the live catalogue uses all
# five — UPPER_BEGINNER and UPPER_INTERMEDIATE together carry more deployed
# lessons than the other three combined. Collapsing 초중급 into BEGINNER and
# 중고급 into INTERMEDIATE (as this map did) threw away the two bands our own
# ladder is densest in, and sorted 초중급 courses beside 한글 떼기.
#
# classLevel is part of grape's natural key but DIFFICULTY is not, so this is a
# safe update on an already-deployed row — it is only cheap while every course
# is still `enabled: false`.
DIFFICULTY = {"왕초급": "BEGINNER", "초급": "BEGINNER", "초중급": "UPPER_BEGINNER",
              "중급": "INTERMEDIATE", "중고급": "UPPER_INTERMEDIATE",
              "고급": "ADVANCED"}
LEVEL_SLUG = {"왕초급": "starter", "초급": "beginner", "초중급": "upper-beginner",
              "중급": "intermediate", "중고급": "upper-intermediate", "고급": "advanced"}
# The level words a learner reads are not here. They are in
# ../course_naming.py, keyed by `difficulty` rather than by the table of
# contents' word, because that is the key the app's level filter uses. This file
# held its own copy until 2026-08-26 and the two disagreed — `Upper beginner`
# here against `Upper Beginner` in the English corpus, and `超入門` against a
# course the filter called `初級`.

# Attribute order is not ours to rely on: a deck that has been through an HTML
# formatter comes back as `<meta content="…" name="podo:title-ko"/>`, and the
# two 3-contextual-korean travel courses are stored that way. Matching on
# `name="…" content="…"` silently read no title for those 19 decks and wrote
# lesson.yaml without `en`/`ja` — the deck was fine, the parser was not.
META_TAG = re.compile(r"<meta\b[^>]*>")
META_ATTR = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"')
# schemas/lesson.schema.json — metadata.slug. Kept verbatim so a mismatch shows
# up while writing rather than at the merge gate.
SLUG_RE = re.compile(r"^[0-9]{2,3}-[a-z0-9]+(-[a-z0-9]+)*$")


def pack_core(units: list) -> list[dict]:
    """2-core-patterns only: units -> ~12-lesson courses, never splitting a unit."""
    groups: list[list] = []
    for level in dict.fromkeys(u["level"] for u in units):      # keep TOC order
        band = [u for u in units if u["level"] == level]
        cur: list = []
        for unit in band:
            n = len(unit["lessons"])
            if cur and sum(len(u["lessons"]) for u in cur) + n > TARGET:
                groups.append(cur)
                cur = []
            cur.append(unit)
        if cur:
            size = sum(len(u["lessons"]) for u in cur)
            prev = groups[-1] if groups else None
            if (prev and prev[0]["level"] == level and size < MERGE_IF_UNDER
                    and sum(len(u["lessons"]) for u in prev) + size <= MAX_AFTER_MERGE):
                prev.extend(cur)
            else:
                groups.append(cur)

    courses, nth = [], {}
    for g in groups:
        level = g[0]["level"]
        nth[level] = nth.get(level, 0) + 1
        lessons = [l for u in g for l in u["lessons"]]
        span = f"Unit {g[0]['no']}" + (f"–{g[-1]['no']}" if len(g) > 1 else "")
        # bare name only — compose() adds the track prefix, level and titles, the
        # same way it does for every other track.
        courses.append({
            "slug": str(nth[level]),
            "level": level,
            "title": {k: str(nth[level]) for k in ("ko", "en", "ja")},
            "note": f"{span} · " + " · ".join(u["title"].split(" — ")[0] for u in g),
            "lessons": [{"no": l["no"], "title": l["title"], "canDo": l["can_do"],
                         "patterns": [p["form"] for p in l["patterns"]], "scene": None}
                        for l in lessons],
        })
    return courses


def compose(course: dict, cfg: dict, rung: int) -> dict:
    """Give a course its slug, and the title the catalogue shows.

    Parsers return a *bare* name — `drama-crush`, `me-lately`, `1` — because the
    track knows its own prefix and the level comes off the course. Composing here
    means a slug can never disagree with the track it sits in.

        ctx-drama-crush-intermediate     (중급) 드라마 · 설렘 & 고백
        talk-me-lately-advanced          (고급) 요즘의 나
        core-beginner-1                  (초급) 핵심 패턴 1
        hangul-starter                   (초급) 한글 떼기

    **The slug still ends in the level**, so `ctx-drama-*` and `ctx-kpop-*` sort
    together by show instead of scattering across levels — except on the core
    ladder, where `levelFirst` keeps the progression in order because the bare
    name there is only a counter.

    **The title does not.** Its shape belongs to `course_naming`, shared with the
    English generator, the covers and the PR gate — the level in front, the
    sub-family the rail header does not already say, and the topic. Composing it
    anywhere else is how the two corpora ended up with two shapes and how the
    covers ended up naming a level the filter disagreed with.

    `rung` is this course's place on its track, which the core ladder puts in the
    title in place of a topic. `course_naming.ladder` is authoritative and counts
    only enabled courses; this counts all of them, so a plan that disables one
    mid-ladder is caught by the gate rather than here.
    """
    level = course["level"]
    bare = course["slug"].strip("-")
    lvl = LEVEL_SLUG[level]
    order = (lvl, bare) if cfg.get("levelFirst") else (bare, lvl)
    course["slug"] = "-".join(x for x in (cfg["prefix"], *order) if x)

    course["title"] = {
        k: naming.title_for("kr", course["slug"], k,
                            course["title"].get(k) or cfg["name"][k],
                            DIFFICULTY[level], rung)
        for k in naming.LANGS
    }
    return course


def yaml_str(value: str) -> str:
    """Quote only where YAML would otherwise misread the scalar."""
    value = value.replace("\n", " ").strip()
    if value == "" or value[0] in "!&*[]{}>|%@`'\"#-?:," or ": " in value or " #" in value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def meta_values(raw: str) -> dict[str, str]:
    """Every `podo:*` meta value, regardless of attribute order."""
    out: dict[str, str] = {}
    for tag in META_TAG.findall(raw):
        attrs = {k.lower(): v for k, v in META_ATTR.findall(tag)}
        name = attrs.get("name", "")
        if name.startswith("podo:"):
            out[name] = html_lib.unescape(attrs.get("content", ""))
    return out


def deck_meta(deck: pathlib.Path) -> tuple[dict, str | None]:
    meta = meta_values(deck.read_text(encoding="utf-8"))
    titles = {k: meta[f"podo:title-{k}"] for k in ("ko", "en", "ja")
              if meta.get(f"podo:title-{k}")}
    return titles, meta.get("podo:lesson-id")


COPY_PATH = pathlib.Path(__file__).resolve().parent / "course-copy.json"


def course_copy() -> dict[str, dict]:
    """Learner-facing course copy, keyed by slug. See course-copy.json."""
    return json.loads(COPY_PATH.read_text(encoding="utf-8"))["courses"]


# Live cover titles average 13 characters in ko and run to 22. Held here for
# the two columns this market actually reads: `ja` is on the learner's screen
# and `ko` is grape's admin label. `en` is deliberately exempt — no learner of
# a Korean course sees EN_BOOK_NAME, and holding it to 40 would mean rewriting
# approved TOC theme names ("Staying & fixing problems") to save nobody a read.
TITLE_LIMITS = {"ko": 30, "ja": 30}


def course_title(course: dict, copy: dict[str, dict]) -> dict[str, str]:
    """The composed title, unless this course was given a written one.

    compose() builds `track · theme · level` from parts that are each short,
    but a theme carrying its own explainer ("말 놓기 — 존댓말에서 반말로") pushes
    the result past what a catalogue list can show. An override trims the
    explainer without editing the TOC, where the long form is the real name.
    """
    written = copy.get(course["slug"], {}).get("title", {})
    return {k: written.get(k) or course["title"][k] for k in ("ko", "en", "ja")}


def course_description(course: dict, copy: dict[str, dict]) -> dict[str, str]:
    """The three-language description for one course.

    `ko` falls back to the TOC's 끝내면 할 수 있는 것 line, which is already a
    can-do sentence everywhere except 2-core-patterns. `en` and `ja` have no
    derivable form — GT_CLASS_COURSE.DESCRIPTION is what the learner reads in
    their own locale, and synthesising it from the level and the lesson count
    produced '初級。10課。', which described the build rather than the course.
    """
    written = copy.get(course["slug"], {}).get("description", {})
    ko = written.get("ko") or course["note"] or course["title"]["ko"]
    out = {"ko": ko}
    for lang in ("en", "ja"):
        if written.get(lang):
            out[lang] = written[lang]
    return out


def market_country_code(value: str | None) -> str:
    """Validate the downstream market identity for this authoring tree."""
    if value is None:
        raise ValueError("countryCode is required")
    if value not in VALID_COUNTRY_CODES:
        raise ValueError(
            f"countryCode must be one of {sorted(VALID_COUNTRY_CODES)}; got {value!r}")
    if value != "JP":
        raise ValueError(
            f"Japanese-market Korean courses require countryCode JP; got {value!r}")
    return value


def course_yaml(course, cfg, class_level, track, written,
                country_code: str | None = MARKET_COUNTRY_CODE,
                copy: dict[str, dict] | None = None) -> str:
    plan = "\n".join(
        f"#   {l['no']:>3}  {'✓ ' + written[l['no']] if l['no'] in written else '·  '}"
        f"{l['title']}{' [깊게]' if l.get('deep') else ''}"
        for l in course["lessons"])
    copy = copy if copy is not None else {}
    t = course_title(course, copy)
    desc = course_description(course, copy)
    description = "\n".join(f"    {k}: {yaml_str(v)}" for k, v in desc.items())
    return f"""\
apiVersion: podo.curriculum/v1
kind: Course
metadata:
  # podo-curriculum-public {track} · {len(course['lessons'])}과.
  # tools/plan_courses.py 가 목차에서 끊었다.
  #
  # podo:level: {course['level']}
  # 이 코스의 덱이 <meta name="podo:level"> 에 적을 값이다. 스키마가 metadata 에
  # 새 필드를 막아서 주석으로 둔다 — tools/new_lesson.py 가 이 줄을 읽는다.
  # 발음 표기(.yomi)를 다는지가 이 값으로 갈리므로 덱마다 손으로 넣게 두면 안 된다.
  slug: {course['slug']}

spec:
  curriculumType: {cfg['type']}
  countryCode: {market_country_code(country_code)}
  # 자연키의 일부다 — 바꾸면 같은 코스의 수정이 아니라 다른 코스가 된다.
  classLevel: "{class_level}"
  lessonTime: 25
  # 검수 전까지는 false. true 로 바꾸는 순간 apply 가 학습자에게 노출시킨다.
  enabled: false
  difficulty: {DIFFICULTY[course['level']]}

  title:
    ko: {yaml_str(t['ko'])}
    en: {yaml_str(t['en'])}
    ja: {yaml_str(t['ja'])}

  # 학습자가 카탈로그에서 읽는 문장이다. 앱이 로케일로 고르므로 JP 마켓 코스는
  # ja 가 화면에 뜬다 — 여기 세 언어는 tools/course-copy.json 이 원본이고,
  # ko 만 목차의 '끝내면 할 수 있는 것' 을 그대로 쓴다.
  description:
{description}

  tutorGroups:
    allowRandom: []
    assignedOnly: []

# 이 코스가 담을 과 — 덱을 쓰면 lessons/ 밑에 디렉터리가 생긴다.
# 슬러그는 스키마가 NN-english-words 를 요구하므로 덱을 쓸 때 정해진다.
{plan}
# Generated by tools/authoring/kr/plan_courses.py — 목차를 고치고 다시 돌린다.
"""


def lesson_yaml(lesson, week, slug, titles, track, course_slug) -> str:
    extra = "".join(f"    {k}: {yaml_str(titles[k])}\n"
                    for k in ("en", "ja") if titles.get(k))
    pats = "\n".join(f"      - {yaml_str(p)}" for p in lesson["patterns"])
    scene = f"  scene: {yaml_str(lesson['scene'])}\n" if lesson.get("scene") else ""
    return f"""\
apiVersion: podo.curriculum/v1
kind: Lesson
metadata:
  slug: {slug}

spec:
  week: {week}                      # → CLASS_WEEK. 코스 안에서 1..N 연속이어야 한다.

  title:
    ko: {yaml_str(titles.get('ko') or lesson['title'])}
{extra}\
  decks:
    lecture:  {{ entry: lecture/index.html }}    # 수업용  → CLASS_LEMONBOARD_KEY
    prestudy: {{ entry: prestudy/index.html }}   # 예습용  → PRESTUDY_LEMONBOARD_KEY

  # ---- 아래는 레포에만 남는다. DB 로 가지 않는다 ----
  teaches:
    patterns:
{pats or "      []"}
    canDo: {yaml_str(lesson['canDo'] or '')}
{scene}\
  prerequisites: []
  source: podo-curriculum-public {track}/{course_slug} · {lesson['no']}

# Generated by tools/authoring/kr/plan_courses.py — 내용은 목차와 덱이 원본이다.
"""


def plan_track(track: pathlib.Path, dry: bool, only_course: str | None = None) -> int:
    cfg = TRACKS.get(track.name)
    parser = track_parsers.PARSERS.get(track.name)
    if cfg is None or parser is None:
        print(f"✗ no plan for track '{track.name}'")
        return 0

    parsed = parser(track)
    courses = pack_core(parsed) if track.name == "2-core-patterns" else parsed
    courses = [compose(c, cfg, i) for i, c in enumerate(courses, 1)]
    copy = course_copy()
    selected_courses = [c for c in courses if only_course is None or c["slug"] == only_course]
    if not selected_courses:
        print(f"✗ no course '{only_course}' in track '{track.name}'")
        return 0

    root, seen, written_n = track / "courses", set(), 0
    print(f"\n{track.name}")

    used_class_levels: set[str] = set()
    for i, course in enumerate(courses, start=1):
        # Most courses advance by .010 across the 100-level section. A parser
        # may reserve an explicit thousandth slot when an existing natural key
        # must stay fixed while a paired course is inserted beside it. Free
        # talking uses .009/.010, .019/.020, ... for Intermediate/Advanced.
        slot = course.get("classLevelSlot", i * 10)
        if not isinstance(slot, int) or not 1 <= slot <= 99_999:
            print(f"    ! {course['slug']}: classLevelSlot must be an integer "
                  "from 1 to 99,999")
            return 0
        class_level_units = cfg["band"] * 1000 + slot
        class_level = f"{class_level_units // 1000}.{class_level_units % 1000:03d}"
        if class_level in used_class_levels:
            print(f"    ! {course['slug']}: duplicate classLevel {class_level}")
            return 0
        used_class_levels.add(class_level)
        if only_course is not None and course["slug"] != only_course:
            continue
        cdir = root / course["slug"]
        seen.add(cdir)

        decks: dict[int, pathlib.Path] = {}
        if (cdir / "lessons").is_dir():
            for deck in sorted((cdir / "lessons").glob("*/lesson.html")):
                m = re.match(r"(\d{2,3})-", deck.parent.name)
                if m:
                    decks[int(m.group(1))] = deck
                else:
                    print(f"    ! {deck.parent.name}: cannot read a lesson number "
                          f"from the directory name — skipped")

        week = 0
        for lesson in course["lessons"]:
            deck = decks.get(lesson["no"])
            if deck is None:
                continue
            week += 1
            slug = deck.parent.name
            titles, ident = deck_meta(deck)
            if ident and ident != slug:
                print(f"    ! {slug}: podo:lesson-id is '{ident}' — deck and "
                      f"directory must agree")
            if not SLUG_RE.match(slug):
                print(f"    ! {slug}: not NN-english-words — will fail validation")
            seen.add(deck.parent)
            if not dry:
                (deck.parent / "lesson.yaml").write_text(
                    lesson_yaml(lesson, week, slug, titles, track.name,
                                course["slug"]), encoding="utf-8")
            written_n += 1

        missing = [lang for lang in ("en", "ja")
                   if not copy.get(course["slug"], {}).get("description", {}).get(lang)]
        if missing:
            print(f"    ! {course['slug']}: no {'/'.join(missing)} description in "
                  "tools/course-copy.json — the learner reads this field")
        for lang, limit in TITLE_LIMITS.items():
            length = len(course_title(course, copy)[lang])
            if length > limit:
                print(f"    ! {course['slug']}: {lang} title is {length} chars, over "
                      f"{limit} — shorten it, or add a title override to "
                      "tools/course-copy.json")

        if not dry:
            (cdir / "lessons").mkdir(parents=True, exist_ok=True)
            (cdir / "course.yaml").write_text(
                course_yaml(course, cfg, class_level,
                            track.name, {n: d.parent.name for n, d in decks.items()},
                            copy=copy),
                encoding="utf-8")

        print(f"  {course['slug']:<30} {course['level']:<6} {class_level:<8} "
              f"{len(course['lessons']):>3} planned, {len(decks)} written")

    if only_course is None and root.is_dir():
        for p in sorted(root.rglob("lesson.yaml")):
            if p.parent not in seen:
                keep = "  (has a deck — move it, do not delete)" if \
                    (p.parent / "lesson.html").is_file() else ""
                print(f"  ! orphaned by the current plan: {p.parent}{keep}")

    print(f"  → {len(selected_courses)} course(s), "
          f"{sum(len(c['lessons']) for c in selected_courses)} planned, {written_n} written")
    return len(selected_courses)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("track", nargs="?", help="e.g. sandbox/drafts/kr/tracks/1-hangul")
    ap.add_argument("--all", action="store_true", help="every track with a parser")
    ap.add_argument("--course", help="regenerate only this course (requires one track)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.all and args.course:
        return ap.error("--course cannot be combined with --all")

    here = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"
    if args.all:
        targets = [here / "tracks" / n for n in sorted(TRACKS)]
    elif args.track:
        targets = [pathlib.Path(args.track)]
    else:
        return ap.error("give a track path or --all")

    total = sum(plan_track(t, args.dry_run, args.course) for t in targets)
    print(f"\n{total} course(s) across {len(targets)} track(s)"
          f"{' — dry run, nothing written' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
