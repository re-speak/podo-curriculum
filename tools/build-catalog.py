#!/usr/bin/env python3
"""
Render the public catalog: every live course, every lesson in it, and every deck
opened exactly as the room opens it.

Why this exists. The decks are already public — they sit in a public repo and are
fetched from a public bucket by the room — but "public" and "readable" are not the
same thing. Somebody outside the content team who wants to know what a learner is
taught has, today, no way in that does not involve cloning a repo or booking a
class. This turns the same files into a page.

**The design is not this repo's.** The chrome, the gateway and the course page are
shared with the authoring catalogs under tools/authoring/, whose Pages site
is already the front door for the curriculum — so the two read as one product
rather than as two teams' idea of a catalog:

    tools/catalog/site.css     ← shared design with the authoring catalog
    tools/catalog/gateway.html ← korean/tools/gateway_template.html
    tools/catalog/course.html  ← korean/tools/track_template.html

Each vendored file carries a header naming its origin and the few edits made to
it, so a drift upstream is a diff, not a mystery. **Do not restyle them here** —
change them upstream, re-vendor, and the edits re-apply.

What the data is. Upstream's catalog is built from `tracks/*/table-of-contents.md`
and describes the whole authored curriculum: 5 tracks, 490 planned lessons. This
repo holds what deploys — courses with a natural key, and the 교재 that ship with
them. So the templates are filled from `model.discover()` instead, with the one
structural difference the vendored `course.html` names in its header: **a track
there is a course here, and a course has no units.** `solo` collapses the unit
shell so the lesson list starts where the unit list would have.

**Only `enabled: true` courses are published.** The flag already means "a learner
can reach this" (→ `USE_YN`), so reusing it keeps one switch instead of two: a
course that is not live is not advertised, and turning a course on turns its page
on with it.

Decks are copied verbatim, never rewritten. A deck is a directory of `index.html`
+ `deck.css` + its own images, all referenced relatively, with the shared runtime
on the CDN — so copying the directory is the whole port. The viewer frames it in
an iframe rather than inlining it, which keeps the deck's CSS out of the
catalog's and means what a visitor sees is byte-for-byte the file the room loads.

    python3 tools/build-catalog.py            # → site/
    python3 -m http.server -d site 8000       # → http://localhost:8000

Nothing here is part of the deploy. `build.py`, `plan.py` and `apply.py` never
import this module, and it never writes into `courses/`. Deleting the output
changes nothing.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import model  # noqa: E402

REPO = model.REPO
TEMPLATES = REPO / "tools" / "catalog"
SOURCE_URL = "https://github.com/re-speak/podo-curriculum/blob/main"
REPO_URL = "https://github.com/re-speak/podo-curriculum"

# 레벨의 원본은 course.yaml 의 `# podo:level:` 주석 한 줄이다. 스키마가 metadata 에
# 새 필드를 막아서 주석으로 사는 값이고, tools/authoring/kr/new_lesson.py 가 덱의
# <meta name="podo:level"> 에 찍는 것도 같은 줄이다 — 카탈로그가 레벨을 다른 데서
# 읽으면 페이지와 덱이 서로 다른 말을 하게 된다.
#
# spec.difficulty 로는 대신할 수 없다. BEGINNER 하나가 한글 떼기(왕초급)와 핵심 문법
# 패턴 1(초급)을 함께 덮어서, 사다리의 어느 칸인지 말해 주지 못한다. 예전에는 여기서
# difficulty 를 옮겼고, 표에 없는 값은 조용히 None 이 되어 살아 있는 코스가 페이지에
# "전 레벨 · 계획만 있음 · 현재 개발하지 않음" 으로 실렸다 — 아무 데서도 그 사실이
# 드러나지 않은 채로. 그래서 이 값은 없으면 빌드를 세운다.
LEVEL_COMMENT = re.compile(r"^\s*#\s*podo:level:\s*(\S+)\s*$", re.M)

# 언어마다 사다리의 눈금이 다르다 — 한국어는 6단, 영어는 CEFR 이다. 각 페이지의 축은
# 이 순서를 그 페이지의 코스가 실제로 쓰는 눈금으로 걸러서 만든다.
LEVEL_ORDER = {
    "kr": ["왕초급", "초급", "초중급", "중급", "중고급", "고급"],
    "en": ["A1", "A2", "A2-B1", "B1", "B2", "B2-C1", "C1"],
}

# 카드를 묶는 단위. upstream 의 게이트웨이가 고르게 하는 물건은 다섯 개의 트랙이고,
# 이 저장소에는 트랙 필드가 없다 — 대신 슬러그 앞머리가 트랙을 그대로 따라간다
# (course.yaml 의 `# podo-curriculum-public 2-core-patterns` 주석과 하나씩 맞는다).
# 그래서 앞머리로 묶고, 묶음의 설명은 authoring 카탈로그의 트랙 설명을 그대로 쓴다.
#
# 모르는 앞머리는 '기타' 로 흘리지 않고 빌드를 세운다. 한 코스가 엉뚱한 묶음에 들어간
# 것은 페이지를 봐서는 알 수 없지만, 빌드가 멈추면 반드시 보인다.
FAMILIES = [
    ("trial-", {
        "kr": ("체험 레슨",
               "수업을 처음 열어 보는 55분짜리 한 과 코스. 레벨마다 하나씩 있습니다."),
    }),
    ("hangul-", {
        "kr": ("한글 떼기",
               "어떤 한국어 음절이든 소리 내어 읽을 수 있게. 한 레슨에 새 요소는 하나만."),
    }),
    ("core-", {
        "kr": ("핵심 문법 패턴",
               "문법의 척추. 1과＝할 수 있는 것 1개＋패턴 2개. 초급부터 고급까지 쌓습니다."),
        "en": ("영어 핵심 패턴",
               "문법의 척추. 1과＝할 수 있는 것 1개＋패턴 2개. CEFR 을 따라 쌓습니다."),
    }),
    ("ctx-", {
        "kr": ("상황별 한국어",
               "드라마·K-POP·여행·반말 — 흥미 있는 소재에서 패턴을 실전으로 추출."),
        "en": ("상황별 영어",
               "장면이 정해진 대화 — 흥미 있는 소재에서 패턴을 실전으로 추출."),
    }),
    ("talk-", {
        "kr": ("프리토킹",
               "새 문법은 없음 — 말하고 싶어지는 주제만. 주제를 계속 추가해 나갑니다."),
        "en": ("프리토킹",
               "새 문법은 없음 — 말하고 싶어지는 주제만. 주제를 계속 추가해 나갑니다."),
    }),
]

# 한 페이지가 한 언어를 맡는다. 56장을 한 장에 쌓으면 "한국어 커리큘럼" 이라는 제목
# 아래에 영어 코스가 섞여 서고, 사다리의 눈금(6단 vs CEFR)도 한 축에 못 선다.
# upstream 의 네비게이션이 이미 한국어 / English 두 탭이라, 그 탭을 되살린 것이다.
LANGUAGES = {
    "kr": {
        "page": "index.html",
        "nav": "한국어",
        "title": "커리큘럼 카탈로그 · PODO 한국어",
        "kicker": "PODO · 한국어 커리큘럼",
        "foot": "PODO · 한국어 커리큘럼 — 일본어 학습자를 위한 한국어 코스",
    },
    "en": {
        "page": "english.html",
        "nav": "English",
        "title": "커리큘럼 카탈로그 · PODO 영어",
        "kicker": "PODO · 영어 커리큘럼",
        "foot": "PODO · 영어 커리큘럼 — 일본어 학습자를 위한 영어 코스",
    },
}

# Upstream's category palette, in upstream's order. The colour is a name tag, not
# a rank — so it is keyed by family, not by card number: every 핵심 문법 패턴 card
# is the same colour, and that colour follows the course into its own page.
PALETTE = [
    ("#4f7d10", "#f2f7e8"),
    ("#2b5fd9", "#eef2fd"),
    ("#c22a5f", "#fdeff3"),
    ("#0080a8", "#e9f6fa"),
    ("#69737d", "#f4f5f7"),
]

DECK_LABEL = {"lecture": "수업용", "prestudy": "예습용"}

UNIT_WORD = "단원"
LESSON_WORD = "과"


def e(text) -> str:
    return html.escape(str(text), quote=True)


def pick(d: dict | None, *keys: str) -> str:
    """First non-empty value among `keys`. Titles carry ko/en/ja and not every
    course fills all three, so every read of a translated field goes through here
    rather than assuming one language is always present."""
    for k in keys:
        if d and d.get(k):
            return str(d[k])
    return ""


def course_level(course: model.Course) -> str:
    """The rung this course sits on, read from course.yaml's `# podo:level:` line.

    Missing or unknown is a hard stop, not a shrug. The page has no honest way to
    draw a course whose level it does not know, and the shape it used to fall back
    to — "전 레벨 · 계획만 있음 · 현재 개발하지 않음" — says the opposite of the
    truth about a course that is live and in class today."""
    path = course.root / "course.yaml"
    m = LEVEL_COMMENT.search(path.read_text(encoding="utf-8"))
    if not m:
        raise model.ValidationError(
            path,
            "no '# podo:level:' line — the catalog reads the level from that "
            "comment, the same one tools/authoring/kr/new_lesson.py stamps into "
            "<meta name=\"podo:level\">. spec.difficulty cannot stand in for it: "
            "BEGINNER covers both 왕초급 and 초급.",
        )

    level, order = m.group(1), LEVEL_ORDER[course.lang]
    if level not in order:
        raise model.ValidationError(
            path,
            f"podo:level '{level}' is not one of {course.lang}'s rungs "
            f"({' · '.join(order)}) — fix the line, or add the rung to "
            f"LEVEL_ORDER in tools/build-catalog.py if it is a real new one",
        )
    return level


def course_family(course: model.Course) -> tuple[int, str, str]:
    """(order, 이름, 설명) of the band this course's card sits under."""
    for i, (prefix, langs) in enumerate(FAMILIES):
        if not course.slug.startswith(prefix):
            continue
        if course.lang not in langs:
            raise model.ValidationError(
                course.root / "course.yaml",
                f"'{prefix}' has no {course.lang} name — add one to FAMILIES in "
                f"tools/build-catalog.py so the card gets a band to sit under",
            )
        return (i, *langs[course.lang])

    raise model.ValidationError(
        course.root / "course.yaml",
        f"slug '{course.slug}' starts with none of the known families "
        f"({' · '.join(p for p, _ in FAMILIES)}) — add its prefix to FAMILIES in "
        f"tools/build-catalog.py rather than letting the card go unfiled",
    )


def fill(template: str, data: dict) -> str:
    """Both templates take their data at one marked spot and render themselves.

    Keeping the substitution to `/*__DATA__*/null` is what makes re-vendoring
    cheap: the templates stay upstream's files with upstream's script, and this
    module only decides what to put in them."""
    marker = "/*__DATA__*/null"
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise SystemExit(f"{template}: expected exactly one {marker}")
    return text.replace(marker, json.dumps(data, ensure_ascii=False))


# --------------------------------------------------------------------------- #
# course → the shape the templates already know how to draw
# --------------------------------------------------------------------------- #

def lesson_entry(course: model.Course, lesson: model.Lesson, deck_hrefs: dict) -> dict:
    """One row in the lesson list, plus what it shows when opened.

    Every field here is read off lesson.yaml. `teaches` is free-form by design
    (`letters`, `concepts`, `patterns`, … differ per track) and several imported
    lessons leave it empty on purpose, so this carries whatever is there and
    nothing when there is nothing."""
    teaches = lesson.spec.get("teaches") or {}
    letters = teaches.get("letters") if isinstance(teaches, dict) else None

    if letters:
        # 낱자를 가르치는 과. 배우는 것은 글자 그 자체이고 outcome 은 그 결과로 읽히는
        # 단어라, 템플릿의 한글 레이아웃이 정확히 이 두 가지를 나눠 그린다.
        #
        # 낱자는 한 덩어리로 묶어 하나의 칸에 넣는다 — 그 과가 얹는 글자 묶음이 하나의
        # 배울 거리이지, 아홉 개의 배울 거리가 아니다. 규칙(concepts)이 그 옆에 선다.
        chips = [" ".join(str(x) for x in letters)]
        chips += [str(c) for c in (teaches.get("concepts") or [])]
    else:
        chips = []
        if isinstance(teaches, dict):
            for value in teaches.values():
                if not value:
                    continue
                chips += [str(v) for v in (value if isinstance(value, list) else [value])]

    entry = {
        "n": lesson.week,
        "title": pick(lesson.spec.get("title"), "ko", "ja", "en"),
        "sub": pick(lesson.spec.get("title"), "ja"),
        "chips": chips,
        "jamo": bool(letters),
        "decks": deck_hrefs.get(lesson.slug, []),
    }
    if lesson.spec.get("outcome"):
        entry["can"] = lesson.spec["outcome"]
        entry["canLabel"] = "읽을 수 있다" if letters else ""
    return entry


def course_entry(course: model.Course, no: int, decks: dict) -> dict:
    """One card on the gateway, and the head of that course's own page."""
    spec = course.spec
    order, family, _ = course_family(course)
    accent, tint = PALETTE[order % len(PALETTE)]
    level = course_level(course)
    ready = sum(len(v) for v in decks.values())

    return {
        "id": f"{course.lang}-{course.slug}",
        "no": no,
        "ko": pick(spec.get("title"), "ko", "ja", "en"),
        "en": pick(spec.get("title"), "ja", "en"),
        "glyph": (pick(spec.get("title"), "ko", "ja") or "·")[0],
        # 모든 과가 두 교재를 갖췄으면 완성, 아니면 계속 추가 중이다. upstream 의
        # "open" 이 그 뜻이라 표시(계속 추가)도 그대로 따라온다.
        "status": "live" if not course.incomplete else "open",
        "accent": accent,
        "tint": tint,
        "unitWord": UNIT_WORD,
        "lessonWord": LESSON_WORD,
        "desc": pick(spec.get("description"), "ja", "ko"),
        "stats": [
            {"k": LESSON_WORD, "v": len(course.lessons)},
            {"k": "교재", "v": ready},
            {"k": "분", "v": spec["lessonTime"]},
        ],
        "family": family,
        "dist": {level: len(course.lessons)},
        "span": [level],
        "total": len(course.lessons),
        "solo": True,
        "source": f"courses/{course.lang}/{course.slug}/course.yaml",
    }


# --------------------------------------------------------------------------- #
# building
# --------------------------------------------------------------------------- #

def copy_decks(out: pathlib.Path, course: model.Course) -> dict:
    """Copy every deck this course has, and hand back where each one landed.

    The deck directory travels whole — index.html, deck.css and every image it
    names, all still siblings, all still relative."""
    hrefs: dict[str, list[dict]] = {}
    for lesson in course.lessons:
        for slot in ("lecture", "prestudy"):
            deck = lesson.decks.get(slot)
            if deck is None or not deck.exists:
                continue
            deck_rel = f"decks/{course.lang}/{course.slug}/{lesson.slug}/{slot}"
            shutil.copytree(deck.entry.parent, out / deck_rel)
            hrefs.setdefault(lesson.slug, []).append({
                "href": f"view/{course.lang}/{course.slug}/{lesson.slug}/{slot}.html",
                "level": DECK_LABEL.get(slot, slot),
                "slot": slot,
                "entry": f"{deck_rel}/{deck.entry.name}",
                "source": str(deck.entry.relative_to(REPO)),
            })
    return hrefs


# 두 템플릿이 --lv-1 … --lv-6 여섯 칸의 초록 램프를 들고 있다.
RAMP_STEPS = 6


def level_ramp(axis: list[str]) -> dict[str, int]:
    """눈금 이름 → 램프의 몇 번째 칸.

    이름이 아니라 축 위의 자리로 매긴다. 눈금 이름은 언어마다 다르지만(한국어 6단,
    영어 CEFR) 옅은 것에서 짙은 것으로 오른다는 규칙은 같아서, 자리로 매기면 어떤
    눈금 체계가 와도 색이 빈 채로 남지 않는다."""
    if len(axis) == 1:
        return {axis[0]: 4}
    return {lv: 1 + round(i * (RAMP_STEPS - 1) / (len(axis) - 1))
            for i, lv in enumerate(axis)}


def nav_links(built: list[str], lang: str, up: str = "") -> list[dict]:
    """한국어 / English 탭. 만들지 않은 언어는 탭도 없다 — 코스가 하나도 열리지 않은
    언어의 페이지는 쓰이지 않고, 탭만 남으면 404 로 간다."""
    links = [{
        "label": LANGUAGES[code]["nav"],
        "href": f"{up}{LANGUAGES[code]['page']}",
        "current": code == lang,
    } for code in LANGUAGES if code in built]
    links.append({"label": "Repository", "href": REPO_URL, "optional": True})
    return links


def build_language(out: pathlib.Path, lang: str, courses: list[model.Course],
                   built: list[str]) -> tuple[list[dict], list[dict], dict]:
    """한 언어의 페이지 하나와, 그 안의 코스 페이지·뷰어를 전부 쓴다."""
    # 카드·사다리·탭이 모두 같은 순서를 따르도록 한 번만 정한다. 묶음이 첫째 키다 —
    # 카드가 묶음별 띠 아래로 들어가므로, 순서가 묶음을 가로지르면 띠가 쪼개진다.
    # 그 안에서는 레벨이 곧 코스의 자리라 CLASS_LEVEL 순이 그대로 목차 순서가 된다.
    courses = sorted(courses, key=lambda c: (course_family(c)[0],
                                             float(c.spec["classLevel"]), c.slug))

    entries, catalog_json, total_lessons, total_decks = [], [], 0, 0

    for no, course in enumerate(courses, start=1):
        decks = copy_decks(out, course)
        entry = course_entry(course, no, decks)
        lessons = [
            lesson_entry(course, l, decks)
            for l in sorted(course.lessons, key=lambda l: l.week)
        ]

        # 단원이 없으므로 묶음은 하나뿐이고, 템플릿은 solo 를 보고 그 껍데기를 그리지
        # 않는다. 머리글 값은 껍데기가 살아날 때를 위해 그대로 채워 둔다.
        entry["groups"] = [{
            "label": f"{len(lessons)}{LESSON_WORD}",
            "title": entry["ko"],
            "subtitle": entry["en"],
            "levels": entry["span"],
            "lessons": lessons,
        }]
        entry["decks"] = [
            {"n": l["n"], "title": l["title"], "href": d["href"], "level": d["level"]}
            for l in lessons for d in l["decks"]
        ]
        entries.append(entry)

        total_lessons += len(lessons)
        total_decks += len(entry["decks"])

        for lesson in sorted(course.lessons, key=lambda l: l.week):
            for deck in decks.get(lesson.slug, []):
                write_viewer(out, course, lesson, deck, entry, lang, built)

        catalog_json.append({
            "lang": course.lang,
            "slug": course.slug,
            "title": course.spec.get("title", {}),
            "description": course.spec.get("description", {}),
            "curriculumType": course.spec["curriculumType"],
            "classLevel": course.spec["classLevel"],
            "lessonTime": course.spec["lessonTime"],
            "countryCode": course.spec.get("countryCode"),
            "level": entry["span"][0],
            "family": entry["family"],
            "page": f"catalog/{entry['id']}.html",
            "lessons": [
                {"week": l["n"], "title": t.spec.get("title", {}), "slug": t.slug,
                 "decks": {d["slot"]: d for d in decks.get(t.slug, [])}}
                for l, t in zip(lessons, sorted(course.lessons, key=lambda x: x.week))
            ],
        })

    # 사다리의 축은 이 페이지의 코스가 실제로 쓰는 눈금만 세운다. 한국어는 여섯 단을
    # 다 쓰지만, 영어는 CEFR 일곱 칸 중 세 칸만 쓰고 있어서 빈 칸 넷을 그릴 이유가 없다.
    used = {lv for entry in entries for lv in entry["span"]}
    axis = [lv for lv in LEVEL_ORDER[lang] if lv in used]
    ramp = level_ramp(axis)

    # 카드를 묶음별 띠 아래로 넣는다. 코스가 하나도 없는 묶음은 띠도 서지 않는다.
    seen = {entry["family"] for entry in entries}
    families = [
        {"name": name, "desc": desc}
        for _, langs in FAMILIES
        if lang in langs
        for name, desc in [langs[lang]]
        if name in seen
    ]

    cfg = LANGUAGES[lang]
    nav = [{"id": e["id"], "no": e["no"], "ko": e["ko"], "accent": e["accent"]}
           for e in entries]
    page = {
        "title": cfg["title"],
        "kicker": cfg["kicker"],
        "foot": cfg["foot"],
        "home": cfg["page"],
        "nav": nav_links(built, lang),
    }

    (out / cfg["page"]).write_text(fill("gateway.html", {
        "levels": axis,
        "ramp": ramp,
        "page": page,
        "families": families,
        "totals": {
            "tracks": len(entries),
            "lessons": total_lessons,
            "units": len(entries),
            "patterns": 0,
            "decks": total_decks,
        },
        "tracks": entries,
    }), encoding="utf-8")

    for entry in entries:
        (out / "catalog" / f"{entry['id']}.html").write_text(
            fill("course.html", {
                "levels": axis,
                "ramp": ramp,
                "nav": nav,
                "track": entry,
                "page": {**page, "home": f"../{cfg['page']}",
                         "nav": nav_links(built, lang, up="../")},
            }),
            encoding="utf-8",
        )

    return entries, catalog_json, {"courses": len(entries), "lessons": total_lessons,
                                   "decks": total_decks}


def build(out: pathlib.Path) -> dict:
    courses = [c for c in model.discover() if c.spec.get("enabled")]

    unknown = sorted({c.lang for c in courses} - set(LANGUAGES))
    if unknown:
        raise model.ValidationError(
            model.COURSES,
            f"no catalog page is defined for {', '.join(unknown)} — add it to "
            f"LANGUAGES in tools/build-catalog.py, or those courses ship "
            f"nowhere a reader can see them",
        )
    # 코스가 하나도 열리지 않은 언어는 페이지도 탭도 만들지 않는다.
    built = [code for code in LANGUAGES if any(c.lang == code for c in courses)]

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copy2(TEMPLATES / "site.css", out / "site.css")
    shutil.copy2(TEMPLATES / "favicon.svg", out / "favicon.svg")
    (out / "catalog").mkdir()

    catalog_json, counts = [], {"courses": 0, "lessons": 0, "decks": 0}
    for lang in built:
        _, rows, sub = build_language(
            out, lang, [c for c in courses if c.lang == lang], built)
        catalog_json += rows
        for k in counts:
            counts[k] += sub[k]

    (out / "catalog.json").write_text(
        json.dumps({"counts": counts, "courses": catalog_json},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Pages served from an Actions artifact does not run Jekyll, but a repo that
    # later switches to a branch source would — and Jekyll drops directories that
    # start with an underscore. One empty file makes both paths behave the same.
    (out / ".nojekyll").write_text("", encoding="utf-8")

    return counts


VIEWER = """<!DOCTYPE html>
<!-- GENERATED by tools/build-catalog.py — the deck below is untouched. -->
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google" content="notranslate">
<meta name="theme-color" content="#ffffff">
<title>{title} · {slot} · PODO</title>
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="{up}site.css">
<style>
  @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

  /* 이 페이지는 덱을 담는 액자다. 위의 한 줄은 어디에서 왔는지와 돌아가는 길만 말하고,
     그 아래는 전부 덱의 자리다 — 교재 자체는 수업에서 열리는 파일 그대로라 손대지 않는다. */
  * {{ box-sizing: border-box; }}
  /* 이 페이지 자체는 스크롤하지 않는다. 액자가 창을 정확히 채우고, 스크롤은 안쪽 덱의
     몫이다 — 바깥에도 스크롤바가 생기면 한 화면에 막대가 둘이 되고, 둘 중 어느 것이
     교재를 넘기는 것인지 알 수 없게 된다. */
  html, body {{ height: 100%; }}
  body {{ margin: 0; display: flex; flex-direction: column; overflow: hidden;
    background: #f4f6f8; color: #16181a; line-height: 1.6;
    font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    -webkit-font-smoothing: antialiased; }}
  .podo-bar, .strip {{ flex: 0 0 auto; }}
  a {{ color: inherit; text-decoration: none; }}
  .strip {{ display: flex; align-items: center; flex-wrap: wrap; gap: 14px;
    width: min(1080px, calc(100% - 40px)); margin: 0 auto; padding: 15px 0; }}
  .strip .back {{ color: #62686e; font-size: 13px; font-weight: 650; }}
  .strip .back:hover {{ color: #16181a; }}
  .strip .t {{ font-size: 14px; font-weight: 750; letter-spacing: -.02em; }}
  .strip .t em {{ font-style: normal; color: #7d848a; font-weight: 550; }}
  .strip .right {{ margin-left: auto; display: flex; align-items: center; gap: 12px; }}
  .strip .slot {{ padding: 4px 9px; border-radius: 2px; background: {tint}; color: {accent};
    font-size: 11px; font-weight: 800; }}
  .strip .plain {{ color: #62686e; font-size: 12.5px; font-weight: 650; }}
  .strip .plain:hover {{ color: #16181a; }}
  .stage {{ flex: 1 1 auto; min-height: 0; display: flex; justify-content: center; padding: 0 12px 18px; }}
  .stage iframe {{ width: 480px; max-width: 100%; height: 100%;
    border: 1px solid #e6e8ea; border-radius: 10px; background: #fff; box-shadow: 0 10px 34px rgba(0,0,0,.07); }}
</style>
</head>
<body>
<a class="podo-skip" href="#deck">본문으로 건너뛰기</a>
<header class="podo-bar">
  <div class="podo-bar__inner">
    <a class="podo-brand" href="{home}"><img src="{up}favicon.svg" width="28" height="28" alt="">PODO Curriculum</a>
    <nav class="podo-nav" aria-label="커리큘럼 탐색">
{nav}
    </nav>
  </div>
</header>
<div class="strip">
  <a class="back" href="{course_href}">← {course}</a>
  <span class="t">{week:02d} · {title} <em>{sub}</em></span>
  <span class="right">
    <span class="slot">{slot}</span>
    <a class="plain" href="{deck}" target="_blank" rel="noopener">전체 화면 ↗</a>
    <a class="plain" href="{source}" target="_blank" rel="noopener">소스 ↗</a>
  </span>
</div>
<div class="stage">
  <iframe id="deck" src="{deck}" title="{title} · {slot}"></iframe>
</div>
<script>
  /* 덱 파일은 룸에서 열리는 그대로라 손대지 않는다 — 액자 안에서 막대만 감춘다.

     shared/css/lesson-card.css 는 `scrollbar-gutter: stable` 로 세로 막대 자리를 항상 열어
     둔다. 룸에서는 그게 맞다 — 페이지마다 높이가 달라서, 막대가 나타났다 사라질 때마다
     가운데 480px 단이 좌우로 흔들리기 때문이다. 그런데 자리를 예약하면 브라우저가
     겹침(overlay) 막대를 포기하고 늘 보이는 막대를 그려서, 액자 바깥 막대와 나란히 둘이
     된다 — 그러면 둘 중 어느 것이 교재를 넘기는 것인지 알 수 없다.

     예약을 풀고 막대 자체도 감춘다. 넘치는 페이지에서 아래에 더 있다는 표시가 사라지지만,
     교재를 넘기는 것은 막대가 아니라 페이저이고 스크롤은 그대로 된다. 덱과 이 페이지는
     같은 출처라 스타일 한 줄을 넣어 줄 수 있다. */
  (function () {{
    var frame = document.getElementById("deck");
    function hideBars() {{
      try {{
        var doc = frame.contentDocument;
        if (!doc || !doc.head) return;
        var style = doc.createElement("style");
        style.textContent =
          "html{{scrollbar-gutter:auto;scrollbar-width:none}}" +
          "html::-webkit-scrollbar,body::-webkit-scrollbar{{width:0;height:0}}";
        doc.head.appendChild(style);
      }} catch (err) {{ /* 다른 출처면 그냥 둔다 — 막대가 보일 뿐 동작은 같다 */ }}
    }}
    frame.addEventListener("load", hideBars);
    hideBars();
  }})();
</script>
</body>
</html>
"""


def write_viewer(out, course, lesson, deck, entry, lang, built) -> None:
    rel = pathlib.Path(deck["href"])
    path = out / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = len(rel.parts) - 1
    up = "../" * depth
    links = nav_links(built, lang, up=up)
    path.write_text(VIEWER.format(
        up=up,
        home=e(f"{up}{LANGUAGES[lang]['page']}"),
        nav="\n".join(
            '      <a{cls} href="{href}"{cur}>{label}</a>'.format(
                cls=' class="podo-nav__optional"' if n.get("optional") else "",
                href=e(n["href"]),
                cur=' aria-current="page"' if n.get("current") else "",
                label=e(n["label"]),
            ) for n in links
        ),
        course=e(entry["ko"]),
        course_href=e(os.path.relpath(out / "catalog" / f"{entry['id']}.html", path.parent)),
        week=lesson.week,
        title=e(pick(lesson.spec.get("title"), "ko", "ja")),
        sub=e(pick(lesson.spec.get("title"), "ja")),
        slot=e(deck["level"]),
        accent=entry["accent"],
        tint=entry["tint"],
        deck=e(os.path.relpath(out / deck["entry"], path.parent)),
        source=e(f"{SOURCE_URL}/{deck['source']}"),
    ), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--out", default="site", help="output directory (default: site)")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    if not out.is_absolute():
        out = REPO / out

    try:
        counts = build(out)
    except model.ValidationError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    where = out.relative_to(REPO) if out.is_relative_to(REPO) else out
    print(f"✓ {where}: {counts['courses']} courses, {counts['lessons']} lessons, "
          f"{counts['decks']} decks")
    if counts["courses"] == 0:
        print("  (nothing published — only courses with `enabled: true` appear)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
