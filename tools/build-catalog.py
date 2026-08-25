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

# 이 사이트가 서빙될 도메인. 값이 있으면 gh-pages 에 CNAME 으로 나간다.
#
# **DNS 레코드가 실제로 존재할 때만 채운다.** 순서를 뒤집으면 사이트가 죽는다:
# CNAME 파일이 올라가는 순간 GitHub 이 커스텀 도메인을 켜고, Pages 는
# re-speak.github.io/podo-curriculum/* 를 전부 그 도메인으로 301 시킨다. 도메인이
# 아직 안 풀리면 두 주소가 함께 막힌다 — DNS 가 생기기를 기다리는 동안 사이트가
# 꺼지는 것이 아니라, CNAME 이 사이트를 끄는 것이다.
#
# 켜는 순서:
#   1. DNS 에 curriculum CNAME → re-speak.github.io. 를 넣고 풀리는 것을 확인한다
#   2. 여기에 도메인을 적고 릴리스한다
#   3. Settings → Pages 에서 DNS check 가 초록이 되면 Enforce HTTPS 를 켠다
CUSTOM_DOMAIN = "curriculum.podospeaking.com"
# 저장소 링크는 카탈로그에 두지 않는다. 이 사이트는 학습자가 보는 곳이고, 소스로
# 나가는 문은 읽는 사람에게 할 일을 주지 않으면서 내부 사정만 드러낸다.

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
    "en": ["A1", "A2", "A2-B1", "B1", "B1+", "B2", "B2-C1", "C1"],
}

# 트랙. upstream 의 게이트웨이가 고르게 하는 물건이고, 여기서도 같다 — 한 트랙의
# 코스들이 그 트랙의 단원이 되고, 그 코스의 과가 그 트랙의 과가 된다. track_template 의
# 단원 껍데기가 원래 그러라고 있는 것이라 아무것도 접을 필요가 없었다.
#
# 저장소에 트랙 필드는 없지만 슬러그 앞머리가 트랙을 그대로 따라간다 — course.yaml 의
# `# podo-curriculum-public 2-core-patterns` 주석과 하나씩 맞는다. 모르는 앞머리는
# '기타' 로 흘리지 않고 빌드를 세운다.
FAMILIES = [
    # 체험은 upstream 에 없던 트랙이라 번호 없는 슬러그를 쓴다. 나머지는 upstream 의
    # 트랙 디렉터리 이름을 그대로 쓴다 — vendor 한 템플릿이 T.id === "1-hangul" 로
    # 한글 전용 표시를 켜고, URL 도 podo-curriculum-public 과 그대로 맞는다.
    ("trial-", {
        "kr": {"slug": "trial", "palette": 4, "ko": "체험 레슨", "en": "Trial Lessons",
               "chip": "Trial", "glyph": "체",
               "ja": "体験レッスン",
               "desc": {"ko": "수업을 처음 열어 보는 55분짜리 한 과 코스. 레벨마다 하나씩 있습니다.",
                        "ja": "はじめて授業を開く55分・1レッスンのコース。レベルごとに1つ用意しています。",
                        "en": "A single 55-minute lesson for opening a class for the first time — one per level."}},
        # 영어 체험은 25분이고, 한국어와 달리 리포트가 덱 안에 없다 — 레슨으로 끝나고
        # 튜터가 작별 뒤에 레벨만 남긴다. 리포트는 그다음 채팅에서 학습자가 읽는다.
        "en": {"slug": "trial", "palette": 4, "ko": "체험 레슨", "en": "Trial Lessons",
               "chip": "Trial", "glyph": "T",
               "ja": "体験レッスン",
               "desc": {"ko": "수업을 처음 열어 보는 25분짜리 한 과 코스. 레벨마다 하나씩 있습니다.",
                        "ja": "はじめて授業を開く25分・1レッスンのコース。レベルごとに1つ用意しています。",
                        "en": "A single 25-minute lesson for opening a class for the first time — one per level."}},
    }),
    ("hangul-", {
        "kr": {"slug": "1-hangul", "palette": 0, "ko": "한글 읽기", "en": "Hangul Reading",
               "chip": "Hangul", "glyph": "가",
               "ja": "ハングルを読む",
               "desc": {"ko": "어떤 한국어 음절이든 소리 내어 읽을 수 있게. 한 레슨에 새 요소는 하나만.",
                        "ja": "どんな韓国語の音節も声に出して読めるように。1レッスンで新しい要素は1つだけ。",
                        "en": "Read any Korean syllable aloud. One new element per lesson, never two."}},
    }),
    ("core-", {
        "kr": {"slug": "2-core-patterns", "palette": 1, "ko": "핵심 문법 패턴", "en": "Core Patterns",
               "chip": "Core", "glyph": "文",
               "ja": "コア文法パターン",
               "desc": {"ko": "문법의 척추. 1과＝할 수 있는 것 1개＋패턴 2개. 초급부터 고급까지 쌓아 올립니다.",
                        "ja": "文法の背骨。1レッスン＝できること1つ＋パターン2つ。初級から上級まで積み上げます。",
                        "en": "The spine of grammar. One lesson = one can-do plus two patterns, beginner to advanced."}},
        "en": {"slug": "1-core-patterns", "palette": 1, "ko": "영어 핵심 패턴", "en": "Core Patterns",
               "chip": "Core", "glyph": "英",
               "ja": "英語コアパターン",
               "desc": {"ko": "문법의 척추. 1과＝할 수 있는 것 1개＋패턴 2개. CEFR 을 따라 쌓아 올립니다.",
                        "ja": "文法の背骨。1レッスン＝できること1つ＋パターン2つ。CEFR に沿って積み上げます。",
                        "en": "The spine of grammar. One lesson = one can-do plus two patterns, following CEFR."}},
    }),
    ("ctx-", {
        "kr": {"slug": "3-contextual-korean", "palette": 2, "ko": "상황별 한국어", "en": "Contextual Korean",
               "chip": "Contextual", "glyph": "劇",
               "ja": "場面別の韓国語",
               "desc": {"ko": "드라마·K-POP·여행·반말 — 흥미 있는 소재에서 패턴을 실전으로 추출.",
                        "ja": "ドラマ・K-POP・旅行・タメ口 — 興味のある題材から、パターンを実戦で取り出します。",
                        "en": "Drama, K-pop, travel, casual speech — patterns pulled from material you actually care about."}},
        "en": {"slug": "2-contextual-english", "palette": 2, "ko": "상황별 영어", "en": "Contextual English",
               "chip": "Contextual", "glyph": "場",
               "ja": "場面別の英語",
               "desc": {"ko": "장면이 정해진 대화 — 흥미 있는 소재에서 패턴을 실전으로 추출.",
                        "ja": "場面が決まった会話 — 興味のある題材から、パターンを実戦で取り出します。",
                        "en": "Conversations with a fixed setting — patterns pulled from material you care about."}},
    }),
    ("talk-", {
        "kr": {"slug": "4-freetalking", "palette": 3, "ko": "중급·고급 프리토킹",
               "en": "Intermediate & Advanced Freetalking",
               "chip": "Freetalking", "glyph": "話",
               "ja": "中級・上級フリートーキング",
               "desc": {"ko": "새 문법은 없음 — 말하고 싶어지는 주제만. 끝이 없는 트랙이라 주제는 계속 늘어납니다.",
                        "ja": "新しい文法はありません — 話したくなる話題だけ。終わりのないトラックなので、話題は増え続けます。",
                        "en": "No new grammar — only topics you want to talk about. An open-ended track that keeps growing."}},
        "en": {"slug": "3-freetalking", "palette": 3, "ko": "프리토킹", "en": "Freetalking",
               "chip": "Freetalking", "glyph": "話",
               "ja": "フリートーキング",
               "desc": {"ko": "새 문법은 없음 — 말하고 싶어지는 주제만.",
                        "ja": "新しい文法はありません — 話したくなる話題だけ。",
                        "en": "No new grammar — only topics you want to talk about."}},
    }),
]

# 언어마다 디렉터리 하나. 깊이는 upstream 의 트리 그대로라 vendor 한 템플릿의
# ../site.css · ../../favicon.svg · ../${deck} 이 한 줄도 고치지 않고 맞는다.
# 이름만 두 가지가 다르다:
#
#   korean-jp/index.html          ← upstream 은 korean/catalog.html
#   korean-jp/catalog/1-hangul.html
#
# 카탈로그를 index 로 둔 것은 /korean-jp 가 그대로 열리게 하려는 것이고, 디렉터리에
# 시장(-jp)을 붙인 것은 지금 모든 코스가 countryCode: JP 이기 때문이다 — 나중에 다른
# 시장이 생겨도 korean-en 을 옆에 세우면 된다.
LANGUAGES = {
    "kr": {
        "dir": "korean-jp",
        "nav": "한국어",
        "langKey": "ko",
        "title": {"ko": "커리큘럼 카탈로그 · PODO 한국어",
                  "ja": "カリキュラム・カタログ · PODO 韓国語",
                  "en": "Curriculum catalog · PODO Korean"},
        "kicker": {"ko": "PODO · 한국어 커리큘럼", "ja": "PODO · 韓国語カリキュラム",
                   "en": "PODO · Korean curriculum"},
        "h1": {"ko": "개 과가<br>지금 수업에서 열립니다",
               "ja": "レッスンが<br>いま授業で開きます",
               "en": "lessons are open<br>in class right now"},
        "lead": {"ko": "지금 수업에서 실제로 열리는 교재입니다. 트랙을 하나 골라 들어가면 "
                       "그 안의 모든 코스와 과를, 각 과의 수업용 · 예습용 교재까지 "
                       "수업에서 열리는 파일 그대로 볼 수 있습니다.",
                 "ja": "いま授業で実際に開く教材です。トラックを一つ選ぶと、その中のすべての"
                       "コースとレッスンを、授業用・予習用の教材まで、授業で開くファイルの"
                       "まま見ることができます。",
                 "en": "These are the decks that actually open in class. Pick a track to see "
                       "every course and lesson inside it, including each lesson's in-class and "
                       "prep decks, exactly as they open in class."},
        "foot": {"ko": "PODO · 한국어 커리큘럼 — 일본어 학습자를 위한 한국어 코스",
                 "ja": "PODO · 韓国語カリキュラム — 日本語話者のための韓国語コース",
                 "en": "PODO · Korean curriculum — Korean courses for Japanese speakers"},
        "home": {"name": "Korean", "native": "한국어", "nativeLang": "ko", "modifier": "",
                 "desc": {"ko": "한글 첫 글자부터 핵심 패턴, 상황별 대화, 고급 프리토킹까지.",
                          "ja": "ハングルの最初の一文字から、コアパターン・場面別会話・上級フリートーキングまで。",
                          "en": "From first Hangul blocks through core patterns, contextual "
                                "conversation, and advanced free talking."}},
    },
    "en": {
        "dir": "english-jp",
        "nav": "English",
        "langKey": "en",
        "title": {"ko": "커리큘럼 카탈로그 · PODO 영어",
                  "ja": "カリキュラム・カタログ · PODO 英語",
                  "en": "Curriculum catalog · PODO English"},
        "kicker": {"ko": "PODO · 영어 커리큘럼", "ja": "PODO · 英語カリキュラム",
                   "en": "PODO · English curriculum"},
        "h1": {"ko": "개 과가<br>지금 수업에서 열립니다",
               "ja": "レッスンが<br>いま授業で開きます",
               "en": "lessons are open<br>in class right now"},
        "lead": {"ko": "지금 수업에서 실제로 열리는 교재입니다. 트랙을 하나 골라 들어가면 "
                       "그 안의 모든 코스와 과를, 각 과의 수업용 · 예습용 교재까지 "
                       "수업에서 열리는 파일 그대로 볼 수 있습니다.",
                 "ja": "いま授業で実際に開く教材です。トラックを一つ選ぶと、その中のすべての"
                       "コースとレッスンを、授業用・予習用の教材まで、授業で開くファイルの"
                       "まま見ることができます。",
                 "en": "These are the decks that actually open in class. Pick a track to see "
                       "every course and lesson inside it, including each lesson's in-class and "
                       "prep decks, exactly as they open in class."},
        "foot": {"ko": "PODO · 영어 커리큘럼 — 일본어 학습자를 위한 영어 코스",
                 "ja": "PODO · 英語カリキュラム — 日本語話者のための英語コース",
                 "en": "PODO · English curriculum — English courses for Japanese speakers"},
        "home": {"name": "English", "native": "英語", "nativeLang": "ja", "modifier": "english",
                 "desc": {"ko": "핵심 패턴 · 상황별 영어 · 프리토킹을 말하기 중심으로 잇는 순서.",
                          "ja": "コアパターン・場面別英語・フリートーキングを、話すことを軸につなぐ順序。",
                          "en": "A speaking-first sequence across core patterns, contextual "
                                "English, and free talking."}},
    },
}

# Upstream's category palette, in upstream's order. The colour is a name tag, not
# a rank — so each track names its own slot ("palette" above) instead of taking
# whatever its position happens to be. 핵심 문법 패턴 is the blue it has always been,
# and adding 체험 ahead of it does not repaint the whole catalog.
PALETTE = [
    ("#4f7d10", "#f2f7e8"),
    ("#2b5fd9", "#eef2fd"),
    ("#c22a5f", "#fdeff3"),
    ("#0080a8", "#e9f6fa"),
    ("#69737d", "#f4f5f7"),
]

DECK_LABEL = {"lecture": "수업용", "prestudy": "예습용"}

UNIT_WORD = "코스"
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


def course_family(course: model.Course) -> tuple[int, dict]:
    """(순서, 이 코스가 속한 트랙) — 슬러그 앞머리로 정한다."""
    for i, (prefix, langs) in enumerate(FAMILIES):
        if not course.slug.startswith(prefix):
            continue
        if course.lang not in langs:
            raise model.ValidationError(
                course.root / "course.yaml",
                f"'{prefix}' has no {course.lang} track — add one to FAMILIES in "
                f"tools/build-catalog.py so the course has a track to sit in",
            )
        return i, langs[course.lang]

    raise model.ValidationError(
        course.root / "course.yaml",
        f"slug '{course.slug}' starts with none of the known tracks "
        f"({' · '.join(p for p, _ in FAMILIES)}) — add its prefix to FAMILIES in "
        f"tools/build-catalog.py rather than letting the course go unfiled",
    )


def strings() -> dict:
    """UI 문자열 한 벌. 세 로케일이 함께 나가고 고르는 일은 브라우저가 한다.

    페이지를 로케일마다 굽지 않는 이유는 URL 이다 — /korean-jp 하나가 세 언어를
    모두 답해야 링크가 언어에 따라 갈라지지 않는다."""
    return json.loads((TEMPLATES / "i18n.json").read_text(encoding="utf-8"))


def _assert_ids_exist(template: str, text: str) -> None:
    """스크립트가 만지는 id 가 그 페이지에 실제로 있는지 본다.

    카탈로그는 브라우저에서 그려진다. getElementById 가 없는 자리를 집으면 그 줄이
    던지고 아래 전부가 멈춰, 페이지가 **빈 화면으로** 나간다 — 파이썬 쪽 검사도,
    node --check 도 이것을 잡지 못한다(문법은 멀쩡하다). 실제로 각주 하나를 지우면서
    그 안의 <code id="src">가 함께 사라졌고, 코스 페이지가 통째로 비었다."""
    import re
    ids = set(re.findall(r'id="([^"]+)"', text))
    used = set(re.findall(r'getElementById\("([^"]+)"\)', text))
    missing = sorted(used - ids)
    if missing:
        raise SystemExit(
            f"{template}: 스크립트가 없는 id 를 집는다 — {', '.join(missing)}. "
            f"그 자리를 지웠다면 집는 줄도 함께 지워라. 두면 페이지가 빈 화면이 된다."
        )


def fill(template: str, data: dict) -> str:
    """Both templates take their data at one marked spot and render themselves.

    Keeping the substitution to `/*__DATA__*/null` is what makes re-vendoring
    cheap: the templates stay upstream's files with upstream's script, and this
    module only decides what to put in them."""
    marker = "/*__DATA__*/null"
    data = dict(data, i18n=strings())
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise SystemExit(f"{template}: expected exactly one {marker}")
    _assert_ids_exist(template, text)
    return text.replace(marker, json.dumps(data, ensure_ascii=False))


# --------------------------------------------------------------------------- #
# 덱에서 읽어 오는 것 — 카탈로그가 비추는 원본은 덱이다
# --------------------------------------------------------------------------- #

# lesson.yaml 의 teaches 는 사람이 적는 값이고 그대로 둔다. 여기서 읽는 것은 카탈로그가
# *보여 주기만* 하는 것들이다 — 오늘의 목표와, 프리토킹 과의 질문 여덟 개.
#
# 왜 lesson.yaml 이 아니라 덱인가. 이 값들은 이미 덱 안에 일본어까지 함께 적혀 있고,
# 그것을 메타데이터로 옮겨 적으면 두 벌이 되어 언젠가 어긋난다. 카탈로그는 리뷰
# 대상이 아니라 덱을 비추는 화면이라, 덱을 직접 읽으면 어긋날 자리가 없다.
#
# bs4 는 함수 안에서 부른다. validate.py 가 이 파일을 통째로 exec 해서 course_level ·
# course_family 만 쓰는데, 위에서 import 하면 없는 bs4 하나가 머지 게이트를 죽인다 —
# tools/requirements.txt 가 지키기로 한 성질이 바로 그것이다.


def _soup(html: str):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser")


def _one_line(node) -> str:
    """덱의 문장은 <b> 같은 강조를 품는다. 태그를 걷어내고 한 줄로 만든다."""
    if node is None:
        return ""
    return " ".join(node.get_text(" ", strip=True).split())


_DECK_FACTS: dict[pathlib.Path, dict] = {}


def deck_facts(lesson) -> dict:
    """수업용 덱에서 목표와 질문을 읽는다. 덱이 없으면 빈 값이다.

    `t` 는 그 코스가 가르치는 언어의 문장이고(한국어 코스면 한국어, 영어 코스면 영어),
    `ja` 는 그 옆에 늘 붙어 있는 일본어다. 덱이 두 언어를 이미 나란히 들고 있어서,
    카탈로그의 언어 전환은 번역이 아니라 고르기가 된다."""
    deck = lesson.decks.get("lecture")
    path = getattr(deck, "path", None) or (lesson.root / "lecture" / "index.html")
    if path in _DECK_FACTS:
        return _DECK_FACTS[path]

    facts = {"goal": None, "qs": []}
    if path.exists():
        s = _soup(path.read_text(encoding="utf-8", errors="replace"))
        g = s.select_one('[data-page-id="lesson-goal"] p.section-subtitle')
        if g:
            t, ja = _one_line(g.select_one("span.ko")), _one_line(g.select_one("span.ja"))
            if t or ja:
                facts["goal"] = {"t": t, "ja": ja}
        # 프리토킹 과의 질문. 다른 트랙의 덱에는 .ask 가 없어 그냥 빈 리스트가 된다.
        for sec in s.select("div.section"):
            ask = sec.select_one("p.section-subtitle.ask")
            if ask is None:
                continue
            facts["qs"].append({
                "n":  _one_line(ask.select_one("span.q-n")),
                "t":  _one_line(ask.select_one("span.ko")),
                "ja": _one_line(ask.select_one("span.ja")),
                "f":  [_one_line(li) for li in sec.select("ul.tn-more li")],
            })

    _DECK_FACTS[path] = facts
    return facts


# --------------------------------------------------------------------------- #
# course → the shape the templates already know how to draw
# --------------------------------------------------------------------------- #

# 트랙마다 "끝내면 무엇이 되는가" 를 부르는 말이 다르다. 템플릿이 이 값을 보고 칸의
# 이름을 고른다 — 모르는 값이면 "이 과의 목표" 로 떨어진다.
CAN_LABEL = {
    "1-hangul": "읽을 수 있다",
    "4-freetalking": "이야기한다",
    "3-freetalking": "이야기한다",
}


def lesson_entry(course: model.Course, lesson: model.Lesson, deck_hrefs: dict,
                 level: str, family: dict) -> dict:
    """One row in the lesson list, plus what it shows when opened.

    `teaches` 는 목차에서 온다 — plan_courses.py 가 초안 lesson.yaml 에 적고,
    promote.py 가 그대로 courses/ 로 옮긴다. 덱을 읽어서 만든 값이 아니다.

    `canDo` 는 teaches 안에 살지만 배우는 것이 아니라 그 결과다. 값을 통째로 훑어
    칩으로 만들면 목표 문장이 칩 하나로 끼어들어가므로, 이름을 보고 갈라 놓는다."""
    teaches = lesson.spec.get("teaches") or {}
    if not isinstance(teaches, dict):
        teaches = {}

    # 낱자를 가르치는 과. 배우는 것은 글자 그 자체라, 낱자는 한 덩어리로 묶어 하나의
    # 칸에 넣는다 — 그 과가 얹는 글자 묶음이 하나의 배울 거리이지, 아홉 개가 아니다.
    entry_chips_ja: dict[str, list[str]] = {}
    letters = teaches.get("letters")
    if letters:
        chips = [" ".join(str(x) for x in letters)]
        chips += [str(c) for c in (teaches.get("concepts") or [])]
    else:
        chips = [str(x) for x in (teaches.get("patterns") or [])]
        # 패턴 자체는 배우는 한국어라 번역하지 않는다. 몇몇 줄에 붙은 설명·상호참조만
        # 다른 언어를 따로 들고 있어서, 길이가 맞을 때만 통째로 갈아 끼운다.
        for code in ("ja", "en"):
            alt = [str(x) for x in (teaches.get(f"patterns{code.title()}") or [])]
            if alt and len(alt) == len(chips):
                entry_chips_ja[code] = alt

    entry = {
        "n": lesson.week,
        "title": pick(lesson.spec.get("title"), "ko", "ja", "en"),
        "sub": pick(lesson.spec.get("title"), "ja"),
        # 제목은 이미 lesson.yaml 에 세 언어가 다 있다 — 전환은 번역이 아니라 고르기다.
        "titles": {k: str(v) for k, v in (lesson.spec.get("title") or {}).items()
                   if k in ("ko", "ja", "en") and v},
        "chips": chips,
        "jamo": bool(letters),
        # 트랙 페이지는 레벨로 거르고 레벨 태그를 과마다 붙인다. 코스 하나는 레벨
        # 하나에 놓이므로, 그 코스의 레벨이 곧 그 과의 레벨이다.
        "level": level,
        "decks": deck_hrefs.get(lesson.slug, []),
    }

    if entry_chips_ja:
        entry["chipsL10n"] = entry_chips_ja

    can = teaches.get("canDo") or lesson.spec.get("outcome")
    if can:
        entry["can"] = str(can)
        entry["canLabel"] = CAN_LABEL.get(family["slug"], "")
        # canDo 는 학습자가 말하는 문장이 아니라 "무엇을 할 수 있게 되는가" 의 설명이다.
        # 읽는 사람의 말로 있어야 하고, 없는 언어는 한국어가 그대로 남는다. 한글
        # 트랙에서는 낱말 목록 뒤에 붙는 지시문만 옮긴다 — 낱말은 배우는 대상이다.
        cans = {code: str(teaches[f"canDo{code.title()}"])
                for code in ("ja", "en") if teaches.get(f"canDo{code.title()}")}
        if cans:
            entry["cans"] = cans

    # 덱이 스스로 말하는 목표와 질문. canDo 와 나란히 두되 대체하지는 않는다 —
    # canDo 는 커리큘럼이 적어 둔 목표이고, goal 은 학습자가 덱에서 실제로 읽는 문장이다.
    facts = deck_facts(lesson)
    if facts["goal"]:
        entry["goal"] = facts["goal"]
    if facts["qs"]:
        entry["qs"] = facts["qs"]
    return entry


def unit_entry(course: model.Course, no: int, decks: dict, family: dict) -> dict:
    """한 코스 = 트랙 안의 단원 하나.

    껍데기 값(label · title · subtitle)이 단원 머리글에 그대로 뜬다. 제목에서 트랙
    이름을 떼는 것은 머리글이 "핵심 문법 패턴 · 초급 · 1" 처럼 트랙 이름을 한 번 더
    말하지 않게 하려는 것뿐이다 — 뗄 수 없으면 통째로 쓴다."""
    spec = course.spec
    level = course_level(course)
    title = pick(spec.get("title"), "ko", "ja", "en")
    prefix = f"{family['ko']} · "
    lessons = [
        lesson_entry(course, l, decks, level, family)
        for l in sorted(course.lessons, key=lambda l: l.week)
    ]
    # 코스 제목도 세 언어가 course.yaml 에 들어 있다. 트랙 이름을 떼는 일은 언어마다
    # 접두사가 달라서 각각 따로 해야 한다.
    titles = {}
    for code in ("ko", "ja", "en"):
        v = (spec.get("title") or {}).get(code)
        if not v:
            continue
        v = str(v)
        fam = f"{family.get(code) or family['ko']} · "
        titles[code] = v[len(fam):] if v.startswith(fam) else v

    return {
        # 숫자만 넘기고 "코스"는 화면에서 붙인다 — 표시 언어마다 단위가 다르다.
        "no": no,
        "label": f"{no}{UNIT_WORD}",
        "title": title[len(prefix):] if title.startswith(prefix) else title,
        "titles": titles,
        "subtitle": pick(spec.get("title"), "ja", "en"),
        "levels": [level],
        "level": level,
        "slug": course.slug,
        "lessons": lessons,
    }


def track_entry(lang: str, no: int, family: dict, units: list[dict],
                statuses: list[str], trial: bool = False) -> dict:
    """트랙 카드 하나, 그리고 그 트랙 페이지의 머리."""
    accent, tint = PALETTE[family["palette"]]
    lessons = [l for u in units for l in u["lessons"]]
    ready = sum(len(l["decks"]) for l in lessons)

    dist: dict[str, int] = {}
    for u in units:
        dist[u["level"]] = dist.get(u["level"], 0) + len(u["lessons"])
    span = [lv for lv in LEVEL_ORDER[lang] if lv in dist]

    return {
        "id": family["slug"],
        "no": no,
        # 체험은 번호를 갖지 않는다 — 사다리의 한 칸이 아니라 그 앞에 놓인 맛보기다.
        "trial": trial,
        "ko": family["ko"],
        "en": family["en"],
        "ja": family["ja"],
        "glyph": family["glyph"],
        # 모든 과가 두 교재를 갖췄으면 완성, 아니면 계속 추가 중이다.
        "status": "open" if "open" in statuses else "live",
        "accent": accent,
        "tint": tint,
        "unitWord": UNIT_WORD,
        "lessonWord": LESSON_WORD,
        "desc": family["desc"],
        "note": "",
        "stats": [
            {"k": "lessonWord", "v": len(lessons)},
            {"k": "unitWord", "v": len(units)},
            {"k": "deckWordShort", "v": ready},
        ],
        "groups": units,
        "dist": dist,
        "span": span,
        "total": len(lessons),
        "unitCount": len(units),
        "decks": [
            {"n": l["n"], "title": l["title"], "titles": l.get("titles") or {},
             "href": d["href"], "level": d["level"], "slot": d["slot"]}
            for l in lessons for d in l["decks"]
        ],
    }


# --------------------------------------------------------------------------- #
# building
# --------------------------------------------------------------------------- #

def copy_decks(base: pathlib.Path, course: model.Course) -> dict:
    """Copy every deck this course has, and hand back where each one landed.

    Paths are relative to the language directory, because that is what the
    vendored track template expects: it writes `../${deck.href}` from
    korean/catalog/<track>.html."""
    hrefs: dict[str, list[dict]] = {}
    for lesson in course.lessons:
        for slot in ("lecture", "prestudy"):
            deck = lesson.decks.get(slot)
            if deck is None or not deck.exists:
                continue
            deck_rel = f"decks/{course.slug}/{lesson.slug}/{slot}"
            shutil.copytree(deck.entry.parent, base / deck_rel)
            hrefs.setdefault(lesson.slug, []).append({
                # 링크에는 확장자가 없고(Pages 가 붙여서 찾는다) 파일은 .html 이다.
                "href": f"view/{course.slug}/{lesson.slug}/{slot}",
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


def nav_links(built: list[str], lang: str | None, up: str) -> list[dict]:
    """한국어 / English 탭. `up` 은 이 페이지에서 사이트 뿌리로 올라가는 접두사다.

    만들지 않은 언어는 탭도 없다 — 코스가 하나도 열리지 않은 언어의 페이지는 쓰이지
    않고, 탭만 남으면 404 로 간다."""
    links = [{
        "label": LANGUAGES[code]["nav"],
        # i18n.json 의 locale 표에 이미 세 언어가 있다 — 화면이 거기서 골라 쓴다.
        "langKey": LANGUAGES[code]["langKey"],
        "href": f"{up}{LANGUAGES[code]['dir']}/",
        "current": code == lang,
    } for code in LANGUAGES if code in built]
    return links


def build_language(out: pathlib.Path, lang: str, courses: list[model.Course],
                   built: list[str]) -> tuple[list[dict], list[dict], dict]:
    """한 언어의 카탈로그 한 장과, 그 아래 트랙 페이지·뷰어를 전부 쓴다."""
    cfg = LANGUAGES[lang]
    base = out / cfg["dir"]
    (base / "catalog").mkdir(parents=True)

    families: dict[int, tuple[dict, list[model.Course]]] = {}
    for course in courses:
        order, family = course_family(course)
        families.setdefault(order, (family, []))[1].append(course)

    tracks, catalog_json = [], []

    no = 0
    for order in sorted(families):
        family, in_track = families[order]
        is_trial = family["slug"] == "trial"
        if not is_trial:
            no += 1
        # 트랙 안에서는 레벨이 곧 코스의 자리라 CLASS_LEVEL 순이 그대로 목차 순서가 된다.
        in_track.sort(key=lambda c: (float(c.spec["classLevel"]), c.slug))

        units, statuses, deck_maps = [], [], {}
        for i, course in enumerate(in_track, start=1):
            decks = copy_decks(base, course)
            deck_maps[course.slug] = decks
            unit = unit_entry(course, i, decks, family)
            units.append(unit)
            statuses.append("open" if course.incomplete else "live")

            catalog_json.append({
                "lang": course.lang,
                "slug": course.slug,
                "title": course.spec.get("title", {}),
                "description": course.spec.get("description", {}),
                "curriculumType": course.spec["curriculumType"],
                "classLevel": course.spec["classLevel"],
                "lessonTime": course.spec["lessonTime"],
                "countryCode": course.spec.get("countryCode"),
                "level": unit["level"],
                "track": family["slug"],
                "page": f"{cfg['dir']}/catalog/{family['slug']}",
                "lessons": [
                    {"week": l["n"], "title": t.spec.get("title", {}), "slug": t.slug,
                     "decks": {d["slot"]: d for d in decks.get(t.slug, [])}}
                    for l, t in zip(unit["lessons"],
                                    sorted(course.lessons, key=lambda x: x.week))
                ],
            })

        # 뷰어는 코스 하나가 아니라 트랙 전체를 알아야 한다 — 차례도, 이전·다음 과도
        # 코스 경계를 넘어간다. 그래서 코스를 다 훑은 뒤에 한 번에 쓴다.
        toc_src = write_toc(base, family, track_toc(in_track, deck_maps, family))
        flat = []
        for course in in_track:
            for lesson in sorted(course.lessons, key=lambda l: l.week):
                slots = [d["slot"] for d in deck_maps[course.slug].get(lesson.slug, [])]
                if not slots:
                    continue
                flat.append((course, lesson, "lecture" if "lecture" in slots else slots[0]))
        for pos, (course, lesson, _) in enumerate(flat):
            slots = [s for s in ("lecture", "prestudy")
                     if s in {d["slot"] for d in deck_maps[course.slug][lesson.slug]}]
            for deck in deck_maps[course.slug][lesson.slug]:
                write_viewer(out, base, course, lesson, deck, family, lang, built,
                             *PALETTE[family["palette"]], toc_src, flat, pos, slots)

        tracks.append(track_entry(lang, 0 if is_trial else no, family, units,
                                  statuses, trial=is_trial))

    # 사다리의 축은 이 페이지의 트랙이 실제로 쓰는 눈금만 세운다.
    used = {lv for tr in tracks for lv in tr["span"]}
    axis = [lv for lv in LEVEL_ORDER[lang] if lv in used]
    ramp = level_ramp(axis)

    # 탭에 트랙 이름이 그대로 뜬다 — 세 언어를 다 실어야 표시 언어를 따라간다.
    nav = [{"id": tr["id"], "no": tr["no"], "ko": tr["ko"], "ja": tr["ja"],
            "en": tr["en"], "accent": tr["accent"], "trial": tr.get("trial", False)}
           for tr in tracks]

    lessons = sum(tr["total"] for tr in tracks)
    decks = sum(len(tr["decks"]) for tr in tracks)
    units = sum(tr["unitCount"] for tr in tracks)

    def page(up: str) -> dict:
        """머리·꼬리의 말. 문장은 {ko,ja,en} 그대로 나가고 고르는 일은 브라우저가 한다.

        숫자는 문장에서 떼어 따로 싣는다 — "3개의 학습 트랙" 을 언어마다 통째로
        번역해 두면 트랙이 넷이 되는 날 세 문장을 같이 고쳐야 한다."""
        return {
            "title": cfg["title"],
            "kicker": cfg["kicker"],
            "lead": cfg["lead"],
            "h1": cfg["h1"],
            "trackCount": sum(1 for t in tracks if not t.get("trial")),
            "stats": [[len(tracks), "tracksH"], [units, "unitWord"], [decks, "deckWord"]],
            "foot": cfg["foot"],
            "home": up or "./",
            "nav": nav_links(built, lang, up),
        }

    (base / "index.html").write_text(fill("gateway.html", {
        "levels": axis,
        "ramp": ramp,
        "page": page("../"),
        "totals": {"tracks": len(tracks), "lessons": lessons,
                   "units": units, "patterns": 0, "decks": decks},
        "tracks": tracks,
    }), encoding="utf-8")

    for tr in tracks:
        (base / "catalog" / f"{tr['id']}.html").write_text(
            fill("course.html", {
                "levels": axis,
                "ramp": ramp,
                "nav": nav,
                "track": tr,
                "page": page("../../"),
            }),
            encoding="utf-8",
        )

    summary = {"tracks": len(tracks), "courses": units,
               "lessons": lessons, "decks": decks}
    return tracks, catalog_json, summary


def build(out: pathlib.Path) -> dict:
    courses = [c for c in model.discover() if c.spec.get("enabled")]

    unknown = sorted({c.lang for c in courses} - set(LANGUAGES))
    if unknown:
        raise model.ValidationError(
            model.COURSES,
            f"no catalog is defined for {', '.join(unknown)} — add it to LANGUAGES "
            f"in tools/build-catalog.py, or those courses ship nowhere a reader "
            f"can see them",
        )
    # 코스가 하나도 열리지 않은 언어는 페이지도 탭도 만들지 않는다.
    built = [code for code in LANGUAGES if any(c.lang == code for c in courses)]

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copy2(TEMPLATES / "site.css", out / "site.css")
    shutil.copy2(TEMPLATES / "favicon.ico", out / "favicon.ico")
    shutil.copy2(TEMPLATES / "favicon.svg", out / "favicon.svg")
    write_assets(out)

    catalog_json, cards = [], []
    counts = {"tracks": 0, "courses": 0, "lessons": 0, "decks": 0}

    for lang in built:
        tracks, rows, sub = build_language(
            out, lang, [c for c in courses if c.lang == lang], built)
        catalog_json += rows
        for k in counts:
            counts[k] += sub[k]

        cfg = LANGUAGES[lang]
        cards.append({
            **cfg["home"],
            "href": f"{cfg['dir']}/",
            "state": "growing" if any(t["status"] == "open" for t in tracks) else "live",
            "counts": {"tracks": sub["tracks"], "courses": sub["courses"],
                       "lessons": sub["lessons"]},
            "tracks": [{"label": next(f[lang]["chip"] for _, f in FAMILIES
                                      if lang in f and f[lang]["slug"] == t["id"]),
                        "accent": t["accent"]} for t in tracks],
        })

    (out / "index.html").write_text(fill("home.html", {
        "languages": cards,
        "nav": [{"label": LANGUAGES[c]["nav"], "langKey": LANGUAGES[c]["langKey"],
                 "href": f"{LANGUAGES[c]['dir']}/"} for c in built]
               ,
    }), encoding="utf-8")

    (out / "catalog.json").write_text(
        json.dumps({"counts": counts, "courses": catalog_json},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # 커스텀 도메인은 저장소 설정과 이 파일 두 곳에 산다. gh-pages 는 매번 통째로
    # force-push 되므로, 도메인을 쓰는 동안에는 여기서 매번 다시 써 줘야 한다 —
    # 아니면 다음 배포가 CNAME 을 지우고 GitHub 이 도메인 설정을 해제한다.
    # 반대로 아직 DNS 가 없으면 쓰지 않는다(위 CUSTOM_DOMAIN 주석 참고).
    if CUSTOM_DOMAIN:
        (out / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")

    # Pages served from an Actions artifact does not run Jekyll, but a repo that
    # later switches to a branch source would — and Jekyll drops directories that
    # start with an underscore. One empty file makes both paths behave the same.
    (out / ".nojekyll").write_text("", encoding="utf-8")

    return counts


# --------------------------------------------------------------------------- #
# 차례 — 트랙 하나당 파일 하나
# --------------------------------------------------------------------------- #

# 뷰어는 트랙 전체의 차례를 들고 있어야 한다. 그런데 트랙 하나가 116과까지 가고 그 과가
# 저마다 뷰어를 둘씩(수업용·예습용) 가지므로, 차례를 파일마다 박아 넣으면 같은 27KB 가
# 232번 복사된다. 트랙마다 파일 하나로 빼서 <script src> 로 부르면 브라우저가 한 번만
#받아 캐시한다 — fetch 가 아니라 script 라서 file:// 로 열어도 그대로 돈다.
TOC_JS = """/* GENERATED by tools/build-catalog.py */
window.PODO_TOC = %s;
"""


def course_short(course: model.Course, family: dict, level: str) -> dict:
    """코스 이름에서 트랙 이름과 레벨을 뗀 나머지. 세 언어를 같은 자리에서 뗀다.

    제목은 `핵심 문법 패턴 · 초급 · 1` 처럼 마디로 적힌다. 차례에서는 트랙 이름이 머리글에,
    레벨이 칩에 이미 한 번씩 있으므로 세 번째로 되풀이하지 않는다.

    **뗄 자리는 한국어 제목으로 정하고 나머지 언어에 그대로 적용한다.** 값으로 비교하면
    영어 커리큘럼에서 어긋난다 — 코스 제목의 en 은 `Core grammar patterns` 인데 트랙의 en
    이름은 `Core Patterns` 이라 앞머리가 안 떨어지고, 그대로 두면 차례에 트랙 이름이 한 번
    더 실린다. 세 언어의 마디 수는 항상 같아서 자리로 떼면 어긋날 데가 없다.

    첫 마디는 트랙 이름일 때만 뗀다. `비즈니스 영어 · 회의와 발표 · B2` 처럼 트랙 안에서
    갈라지는 이름은 그 자체가 알맹이라, 떼면 무엇에 관한 코스인지가 사라진다."""
    def dash(x: str) -> str:
        return x.replace("–", "-").replace("—", "-")

    titles = {code: str(v) for code, v in (course.spec.get("title") or {}).items()
              if code in ("ko", "ja", "en") and v}
    ko = titles.get("ko", "")
    parts_ko = ko.split(" · ")
    names = {dash(level)} | {dash(level_name(level, c)) for c in ("ko", "ja", "en")}
    keep = [i for i, seg in enumerate(parts_ko)
            if not (i == 0 and seg == family.get("ko")) and dash(seg) not in names]

    out = {}
    for code, raw in titles.items():
        parts = raw.split(" · ")
        picked = ([parts[i] for i in keep if i < len(parts)]
                  if len(parts) == len(parts_ko)
                  else [p for p in parts if dash(p) not in names])
        out[code] = " · ".join(picked) or level_name(level, code)
    return out


def level_name(level: str, code: str) -> str:
    """레벨 이름의 표시 언어. 표에 없으면(영어 커리큘럼의 CEFR) 그대로 둔다."""
    return (strings().get("level", {}).get(level, {}) or {}).get(code) or level


def track_toc(in_track: list[model.Course], deck_maps: dict, family: dict) -> list[dict]:
    """트랙의 차례 한 벌. 코스가 접이 단위이고, 접을 것이 없으면 접지 않는다.

    `group` 이 거짓이면 그 코스의 과들은 묶이지 않고 그냥 줄로 눕는다 — 코스가 하나뿐인
    트랙(한글 떼기)과 과가 하나뿐인 코스(체험)가 그렇다. 펼칠 것이 하나뿐인 접이는
    누르는 일만 늘린다."""
    solo_track = len(in_track) < 2
    out = []
    for course in in_track:
        level = course_level(course)
        lessons = sorted(course.lessons, key=lambda l: l.week)
        rows = []
        for lesson in lessons:
            hrefs = deck_maps[course.slug].get(lesson.slug, [])
            if not hrefs:
                continue          # 덱이 없는 과는 열 곳이 없다
            slot = "lecture" if any(d["slot"] == "lecture" for d in hrefs) else hrefs[0]["slot"]
            rows.append({
                "w": lesson.week,
                "t": {k: str(v) for k, v in (lesson.spec.get("title") or {}).items()
                      if k in ("ko", "ja", "en") and v},
                "c": course.slug,
                "s": lesson.slug,
                "h": f"../../{course.slug}/{lesson.slug}/{slot}.html",
            })
        if not rows:
            continue
        out.append({
            "lv": level,
            "n": course_short(course, family, level),
            "group": not solo_track and len(rows) > 1,
            "l": rows,
        })
    return out


def write_toc(base: pathlib.Path, family: dict, toc: list[dict]) -> str:
    """차례 파일을 쓰고, 뷰어에서 그 파일로 가는 상대 경로를 돌려준다."""
    path = base / "toc" / f"{family['slug']}.js"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TOC_JS % json.dumps(toc, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8")
    # 뷰어는 view/<코스>/<과>/<슬롯>.html 에 있다 — 언어 뿌리까지 세 칸 올라간다.
    return f"../../../toc/{family['slug']}.js"


# 뷰어는 1838장이다. 한 장에 박아 넣은 1KB 는 사이트에서 1.8MB 가 된다 — 그래서 장마다
# 달라지는 것(이 과가 무엇인지)만 HTML 에 남기고, 모든 장이 똑같이 들고 있던 것은 파일
# 하나로 뺀다. 트랙 색만 <html> 의 인라인 변수로 장마다 다르게 온다.
VIEWER_CSS = r"""@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

  /* 이 페이지는 덱을 담는 액자다. 한 줄짜리 바가 어디에서 왔는지와 돌아가는 길을 말하고,
     그 아래는 전부 덱의 자리다 — 교재 자체는 수업에서 열리는 파일 그대로라 손대지 않는다.
     차례는 덱을 밀지 않고 원래 비어 있던 왼쪽 회색 자리에 얹히므로, 접고 펴는 일이
     교재를 좌우로 흔들지 않는다. */
  * { box-sizing: border-box; }
  /* 이 페이지 자체는 스크롤하지 않는다. 액자가 창을 정확히 채우고, 스크롤은 안쪽 덱의
     몫이다 — 바깥에도 스크롤바가 생기면 한 화면에 막대가 둘이 되고, 둘 중 어느 것이
     교재를 넘기는 것인지 알 수 없게 된다. */
  html, body { height: 100%; }
  body { margin: 0; display: flex; flex-direction: column; overflow: hidden;
    background: #f4f6f8; color: #16181a; line-height: 1.5;
    font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    -webkit-font-smoothing: antialiased; }
  a { color: inherit; text-decoration: none; }
  button { font: inherit; }

  .bar { flex: 0 0 auto; display: flex; align-items: center; gap: 10px;
    height: 56px; padding: 0 18px; background: rgba(255,255,255,.97);
    border-bottom: 1px solid #e1e4df; }
  .brand { display: inline-flex; align-items: center; gap: 8px; font-size: 13px;
    font-weight: 800; letter-spacing: -.01em; white-space: nowrap; }
  .brand img { width: 24px; height: 24px; border-radius: 6px; }
  .rule { width: 1px; height: 20px; background: #e1e4df; }
  .right { margin-left: auto; display: flex; align-items: center; gap: 8px; }

  /* 빵부스러기. 위로 가는 곳만 링크이고, 지금 있는 곳은 글자다 — 갈 데가 없으니까.
     둘의 차이는 색과 굵기가 말한다. 같아 보이면 죽은 쪽을 누르게 된다. */
  .crumb { display: flex; align-items: baseline; gap: 7px; min-width: 0; }
  .crumb__up { flex: 0 0 auto; color: #62686e; font-size: 13px; font-weight: 650;
    letter-spacing: -.01em; white-space: nowrap; }
  .crumb__up:hover { color: #16181a; text-decoration: underline; text-underline-offset: 3px; }
  .crumb__sep { flex: 0 0 auto; color: #c3c8cc; font-size: 13px; }
  .crumb__here { flex: 0 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis;
    white-space: nowrap; color: #16181a; font-size: 13.5px; font-weight: 750;
    letter-spacing: -.015em; }
  .crumb__lv { flex: 0 0 auto; padding: 2px 6px; border-radius: 5px; background: #16181a;
    color: #fff; font-size: 10.5px; font-weight: 800; }

  /* 두 갈래 스위치 하나로 슬롯과 표시 언어를 함께 그린다. */
  .seg { display: flex; gap: 2px; padding: 2px; border: 1px solid #e3e7ea;
    border-radius: 8px; background: #fff; }
  .seg > * { display: inline-flex; align-items: center; height: 26px; padding: 0 9px;
    border: 0; border-radius: 6px; background: transparent; color: #62686e;
    font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap; }
  .seg > *:hover { color: #16181a; }
  .seg > [aria-current="page"], .seg > [aria-pressed="true"] { background: #16181a; color: #fff; }
  .iconbtn { display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border: 1px solid #e3e7ea; border-radius: 8px;
    background: #fff; color: #62686e; cursor: pointer; }
  .iconbtn:hover { color: #16181a; background: #f5f6f3; }

  .tocbtn { display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 10px;
    border: 1px solid #e3e7ea; border-radius: 8px; background: #fff; color: #16181a;
    font-size: 12.5px; font-weight: 700; cursor: pointer; }
  .tocbtn:hover { background: #f5f6f3; }
  .tocbtn svg { color: #62686e; }
  .tocbtn[aria-expanded="true"] { background: #f5f6f3; border-color: #cdd0c6; }
  .tocbtn[aria-expanded="true"] svg { color: #16181a; }

  .rail { position: fixed; left: 0; top: 56px; bottom: 0; width: 288px; z-index: 70;
    display: flex; flex-direction: column; gap: 8px; padding: 14px 12px;
    border-right: 1px solid #e1e4df; background: rgba(255,255,255,.86);
    backdrop-filter: blur(10px); transition: transform .2s ease, opacity .2s ease; }
  body.toc-off .rail { transform: translateX(-100%); opacity: 0; pointer-events: none; }
  .railhead { margin: 0 0 2px; padding: 0 9px; color: #62686e; font-size: 11px;
    font-weight: 700; letter-spacing: .04em; font-variant-numeric: tabular-nums; }
  .list { display: flex; flex-direction: column; gap: 1px; overflow-y: auto; scrollbar-width: thin; }

  /* 코스 하나 = 접히는 묶음 하나. 지금 과가 든 묶음만 열린 채로 온다. */
  .grp > summary { display: flex; align-items: center; gap: 7px; padding: 8px 9px;
    border-radius: 8px; cursor: pointer; list-style: none; user-select: none; }
  .grp > summary::-webkit-details-marker { display: none; }
  .grp > summary::before { flex: 0 0 auto; width: 9px; height: 9px;
    border-right: 1.6px solid #62686e; border-bottom: 1.6px solid #62686e;
    transform: rotate(-45deg) translate(1px, -1px); transition: transform .15s ease; content: ""; }
  .grp[open] > summary::before { transform: rotate(45deg) translate(-1px, -1px); }
  .grp > summary:hover { background: #f5f6f3; }
  .lv { padding: 2px 6px; border-radius: 5px; background: var(--tint); color: var(--accent);
    font-size: 10.5px; font-weight: 800; white-space: nowrap; }
  .grp .nm { font-size: 12.5px; font-weight: 700; letter-spacing: -.01em; }
  .grp .n { margin-left: auto; color: #62686e; font-size: 11px; font-weight: 650;
    font-variant-numeric: tabular-nums; }

  .row { display: grid; grid-template-columns: 30px 1fr; align-items: baseline;
    column-gap: 8px; padding: 7px 9px 7px 25px; border-radius: 8px; }
  .row--solo { grid-template-columns: auto 1fr; padding-left: 9px; }
  .row:hover { background: #f5f6f3; }
  .row[aria-current="page"] { background: #fff;
    box-shadow: 0 1px 2px rgba(16,20,24,.10), inset 0 0 0 1px #e1e4df; }
  .row b { font-size: 11px; font-weight: 800; color: #62686e; font-variant-numeric: tabular-nums; }
  .row[aria-current="page"] b { color: var(--accent); }
  .row .t { font-size: 12.5px; font-weight: 650; letter-spacing: -.01em; line-height: 1.45; }
  .row .s { grid-column: 2; font-size: 11px; font-weight: 500; color: #62686e; }

  .railfoot { margin-top: auto; display: flex; gap: 6px; padding-top: 8px;
    border-top: 1px solid #e1e4df; }
  .railfoot a, .railfoot span { flex: 1; display: inline-flex; align-items: center;
    justify-content: center; gap: 5px; height: 34px; border: 1px solid #e3e7ea;
    border-radius: 9px; background: #fff; font-size: 12.5px; font-weight: 700; }
  .railfoot a:hover { background: #f5f6f3; }
  .railfoot span { color: #b3b9bf; }

  .menu { position: absolute; z-index: 80; min-width: 236px; padding: 6px;
    border: 1px solid #e3e7ea; border-radius: 12px; background: #fff;
    box-shadow: 0 14px 40px rgba(16,20,24,.14); }
  .menu[hidden] { display: none; }
  .menu a { display: flex; align-items: baseline; gap: 8px; padding: 8px 10px;
    border-radius: 8px; font-size: 13px; font-weight: 650; }
  .menu a:hover { background: #f5f6f3; }
  .menu a[aria-current="page"] { background: var(--tint); color: var(--accent); }
  .menu a b { flex: 0 0 34px; font-size: 11.5px; font-weight: 800; color: #62686e; }
  .menu a[aria-current="page"] b { color: var(--accent); }

  .railscrim { display: none; }
  .only-phone { display: none; }

  .stage { flex: 1 1 auto; min-height: 0; display: flex; justify-content: center;
    padding: 14px 12px 16px; }
  .stage iframe { width: 480px; max-width: 100%; height: 100%;
    border: 1px solid #e6e8ea; border-radius: 12px; background: #fff;
    box-shadow: 0 10px 34px rgba(0,0,0,.07); }

  /* 창이 좁아 차례가 교재를 덮기 시작하면 성격이 바뀐다 — 얹는 것에서 서랍으로.
     기본은 접힌 채로 오고, 열면 뒤에 막이 깔리고, Esc 로 닫힌다. */
  @media (max-width: 1080px) {
    .rail { box-shadow: 0 18px 48px rgba(16,20,24,.20); background: #fff; }
    body:not(.toc-off) .railscrim { display: block; position: fixed; inset: 56px 0 0 0;
      z-index: 65; background: rgba(23,25,22,.26); }
  }
  /* 폰. 한 줄이 넘치면 지금 보고 있는 것만 남기고, 나머지는 전부 ⋯ 안으로 들어간다. */
  @media (max-width: 720px) {
    .bar { height: 52px; padding: 0 10px; gap: 6px; }
    .brand { font-size: 0; gap: 0; }
    .brand img { width: 26px; height: 26px; }
    .rule, .crumb__up, .crumb__sep, .seg, .iconbtn:not(.only-phone) { display: none; }
    .only-phone { display: inline-flex; }
    .crumb { flex: 1 1 auto; }
    .right { gap: 4px; }
    .rail { top: 52px; width: min(300px, calc(100% - 44px)); }
    body:not(.toc-off) .railscrim { inset: 52px 0 0 0; }
    .tocbtn span { display: none; }
    .tocbtn { padding: 0 9px; }
    .menu { min-width: min(280px, calc(100vw - 24px)); }
    .stage { padding: 8px 8px 10px; }
  }
  @media (prefers-reduced-motion: reduce) {
    .rail, .grp > summary::before { transition: none; }
  }
"""

VIEWER_JS = r"""/* GENERATED by tools/build-catalog.py */
  /* 표시 언어. 카탈로그의 나머지와 같은 규칙이고 같은 키를 읽는다 — 카탈로그에서
     일본어로 보던 사람이 덱을 열었을 때 액자만 한국어로 돌아가면 안 된다. */
  (function () {
    var D = window.PODO_VIEW || {};
    var I18N = window.PODO_I18N || {};
    var LOCALES = ["ko", "ja", "en"], KEY = "podo-catalog-locale";
    var TOC = window.PODO_TOC || null;
    var L = "ja";
    try { var v = localStorage.getItem(KEY); if (LOCALES.indexOf(v) >= 0) L = v; } catch (e) {}

    function tr(sec, key) {
      var row = (I18N[sec] || {})[key] || {};
      return row[L] || row.ko || "";
    }
    function loc(o) { return !o ? "" : (o[L] || o.ko || o.en || o.ja || ""); }
    function lvName(lv) {
      var row = (I18N.level || {})[lv];
      return (row && row[L]) || lv;
    }
    function el(tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text != null) n.textContent = text;
      return n;
    }

    /* 차례는 한 번만 짓는다. 표시 언어를 바꿀 때 다시 지으면 펼쳐 둔 묶음이 도로 닫힌다 —
       그래서 글자만 갈아 끼우도록 만들 때 각 자리를 적어 둔다. */
    var paints = [];
    function buildRail() {
      var list = document.getElementById("list");
      if (!TOC) { document.getElementById("rail").hidden = true;
                  document.getElementById("toc").hidden = true; return; }
      TOC.forEach(function (c) {
        var box = list, here = c.l.some(function (r) { return r.c === D.course && r.s === D.lesson; });
        if (c.group) {
          var d = el("details", "grp"); d.open = here;
          var sm = document.createElement("summary");
          var lv = el("span", "lv"), nm = el("span", "nm"), n = el("span", "n");
          sm.appendChild(lv); sm.appendChild(nm); sm.appendChild(n);
          d.appendChild(sm); list.appendChild(d); box = d;
          paints.push(function () {
            lv.textContent = lvName(c.lv);
            nm.textContent = loc(c.n);
            /* 세는 말이 붙는 자리. 한국어·일본어는 붙여 쓰고 영어는 띄어 쓴다. */
            n.textContent = c.l.length + (L === "en" ? " " : "") + tr("ui", "lessonWord");
          });
        }
        /* 묶이지 않은 코스는 두 가지다. 과가 하나뿐이라 묶을 것이 없는 코스(체험)는
           그 줄이 곧 코스이므로 레벨로 부르고, 코스가 하나뿐인 트랙(한글 떼기)은
           줄마다 과가 다르므로 여느 때처럼 과 번호로 부른다. */
        var byLevel = !c.group && c.l.length === 1;
        c.l.forEach(function (r) {
          var a = el("a", byLevel ? "row row--solo" : "row");
          a.href = r.h;
          var b = el("b"), t = el("span", "t");
          a.appendChild(b); a.appendChild(t);
          if (r.c === D.course && r.s === D.lesson) a.setAttribute("aria-current", "page");
          box.appendChild(a);
          paints.push(function () {
            b.textContent = byLevel ? lvName(c.lv) : ("0" + r.w).slice(-2);
            t.textContent = loc(r.t);
          });
        });
      });
    }

    function foot() {
      var box = document.getElementById("foot");
      box.textContent = "";
      [["prev", D.prev], ["next", D.next]].forEach(function (pair) {
        var dir = pair[0], o = pair[1];
        var arrow = dir === "prev" ? "M10 3L5 8l5 5" : "M6 3l5 5-5 5";
        var svg = '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor"'
          + ' stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          + '<path d="' + arrow + '"/></svg>';
        var label = tr("ui", dir === "prev" ? "prevLesson" : "nextLesson");
        var node;
        if (o) {
          node = document.createElement("a");
          node.href = o.h;
          node.title = lvName(o.lv) + " · " + loc(o.t);
        } else {
          node = document.createElement("span");
          label = tr("ui", "none");
        }
        node.innerHTML = dir === "prev" ? svg + " " + label : label + " " + svg;
        box.appendChild(node);
      });
    }

    function segs() {
      var slots = document.getElementById("slots");
      slots.textContent = "";
      D.slots.forEach(function (s) {
        var a = el("a", null, tr("ui", s === "prestudy" ? "slotPrestudy" : "slotLecture"));
        a.href = s + ".html";
        if (s === D.slot) a.setAttribute("aria-current", "page");
        slots.appendChild(a);
      });
      var bar = document.getElementById("loc");
      bar.setAttribute("aria-label", tr("locale", "label"));
      bar.textContent = "";
      LOCALES.forEach(function (c) {
        var b = el("button", null, ((I18N.locale[c] || {})[c] || c));
        b.type = "button";
        b.setAttribute("data-loc", c);
        b.setAttribute("aria-pressed", String(c === L));
        bar.appendChild(b);
      });
    }

    function phoneMenu() {
      var m = document.getElementById("phone");
      m.textContent = "";
      function row(mark, text, href, sub, cur) {
        var a = document.createElement("a");
        a.href = href;
        var b = el("b", null, mark);
        a.appendChild(b);
        a.appendChild(document.createTextNode(text));
        if (sub) a.appendChild(el("span", null, " " + sub));
        if (cur) a.setAttribute("aria-current", "page");
        m.appendChild(a);
        return a;
      }
      row("←", loc(D.track), document.getElementById("track").href);
      D.slots.forEach(function (s) {
        if (s === D.slot) return;
        row("", tr("ui", s === "prestudy" ? "slotPrestudy" : "slotLecture"), s + ".html");
      });
      var f = row("", tr("ui", "fullScreen"), document.getElementById("full").href);
      f.target = "_blank"; f.rel = "noopener";
      LOCALES.forEach(function (c) {
        var a = row(((I18N.locale[c] || {})[c] || c), (I18N.locale[c] || {})[L] || c, "#",
                    null, c === L);
        a.addEventListener("click", function (e) { e.preventDefault(); setLocale(c); });
      });
    }

    function paint() {
      document.documentElement.lang = L;
      document.querySelectorAll("[data-i18n]").forEach(function (e) {
        var p = e.getAttribute("data-i18n").split("."), v = tr(p[0], p[1]);
        if (v) e.textContent = v;
      });
      document.querySelectorAll("[data-i18n-label]").forEach(function (e) {
        var p = e.getAttribute("data-i18n-label").split("."), v = tr(p[0], p[1]);
        if (v) e.setAttribute("aria-label", v);
      });
      var name = loc(D.title) || D.titleKo;
      var slot = tr("ui", D.slot === "prestudy" ? "slotPrestudy" : "slotLecture");
      document.getElementById("track").textContent = loc(D.track);
      document.getElementById("lv").textContent = lvName(D.level);
      document.getElementById("here").textContent = ("0" + D.week).slice(-2) + " · " + name;
      document.getElementById("pos").textContent = D.pos + " / " + D.total;
      document.title = name + " · " + slot + " · PODO";
      var frame = document.getElementById("deck");
      if (frame) frame.title = name + " · " + slot;
      paints.forEach(function (f) { f(); });
      segs();
      foot();
      phoneMenu();
    }

    function setLocale(c) {
      if (c === L) return;
      L = c;
      try { localStorage.setItem(KEY, L); } catch (e) {}
      paint();
    }

    document.getElementById("loc").addEventListener("click", function (e) {
      var b = e.target.closest("button[data-loc]");
      if (b) setLocale(b.dataset.loc);
    });

    buildRail();
    paint();

    /* 지금 과가 116줄 중 어디에 있든 보이는 자리에서 시작한다. */
    var list = document.getElementById("list"), cur = list.querySelector('[aria-current="page"]');
    if (cur) list.scrollTop = cur.offsetTop - list.clientHeight / 2 + cur.offsetHeight / 2;

    /* 열림·닫힘은 사람이 고른 값이라 기억한다. 고른 적이 없으면 창 너비가 정한다 —
       차례가 교재를 덮지 않는 넓이에서만 처음부터 열려 있다. */
    var btn = document.getElementById("toc"), body = document.body;
    function toc(open) {
      body.classList.toggle("toc-off", !open);
      btn.setAttribute("aria-expanded", String(open));
    }
    toc(!body.classList.contains("toc-off"));
    btn.addEventListener("click", function () {
      var open = body.classList.contains("toc-off");
      try { localStorage.setItem("podo-catalog-toc", open ? "1" : "0"); } catch (e) {}
      toc(open);
    });
    document.getElementById("scrim").addEventListener("click", function () { toc(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && window.innerWidth < 1080
          && !body.classList.contains("toc-off")) toc(false);
    });

    /* ⋯ 하나짜리 팝오버. 폰에서만 보인다. */
    var more = document.getElementById("morebtn"), menu = document.getElementById("phone");
    more.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      if (!open) return;
      var r = more.getBoundingClientRect();
      menu.style.top = (r.bottom + 6) + "px";
      menu.style.left = Math.max(8, Math.min(r.left, window.innerWidth - menu.offsetWidth - 12)) + "px";
    });
    document.addEventListener("click", function () { menu.hidden = true; });
  })();

  /* 덱 파일은 룸에서 열리는 그대로라 손대지 않는다 — 액자 안에서 막대만 감춘다.

     shared/css/lesson-card.css 는 `scrollbar-gutter: stable` 로 세로 막대 자리를 항상 열어
     둔다. 룸에서는 그게 맞다 — 페이지마다 높이가 달라서, 막대가 나타났다 사라질 때마다
     가운데 480px 단이 좌우로 흔들리기 때문이다. 그런데 자리를 예약하면 브라우저가
     겹침(overlay) 막대를 포기하고 늘 보이는 막대를 그려서, 액자 바깥 막대와 나란히 둘이
     된다 — 그러면 둘 중 어느 것이 교재를 넘기는 것인지 알 수 없다.

     예약을 풀고 막대 자체도 감춘다. 넘치는 페이지에서 아래에 더 있다는 표시가 사라지지만,
     교재를 넘기는 것은 막대가 아니라 페이저이고 스크롤은 그대로 된다. 덱과 이 페이지는
     같은 출처라 스타일 한 줄을 넣어 줄 수 있다. */
  (function () {
    var frame = document.getElementById("deck");
    function hideBars() {
      try {
        var doc = frame.contentDocument;
        if (!doc || !doc.head) return;
        var style = doc.createElement("style");
        style.textContent =
          "html{scrollbar-gutter:auto;scrollbar-width:none}" +
          "html::-webkit-scrollbar,body::-webkit-scrollbar{width:0;height:0}";
        doc.head.appendChild(style);
      } catch (err) { /* 다른 출처면 그냥 둔다 — 막대가 보일 뿐 동작은 같다 */ }
    }
    frame.addEventListener("load", hideBars);
    hideBars();
  })();
"""


def write_assets(out: pathlib.Path) -> None:
    """뷰어가 함께 쓰는 세 파일. 문자열표까지 밖으로 뺀다 — 12KB 짜리 표를 장마다
    복사하면 그것만으로 사이트가 20MB 무거워진다."""
    (out / "viewer.css").write_text(VIEWER_CSS, encoding="utf-8")
    (out / "viewer.js").write_text(VIEWER_JS, encoding="utf-8")
    (out / "i18n.js").write_text(
        "/* GENERATED by tools/build-catalog.py */\nwindow.PODO_I18N = "
        + json.dumps(strings(), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")


VIEWER = """<!DOCTYPE html>
<!-- GENERATED by tools/build-catalog.py — the deck below is untouched. -->
<html lang="ko" style="--accent:{accent};--tint:{tint}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google" content="notranslate">
<meta name="theme-color" content="#ffffff">
<title>{title} · PODO</title>
<link rel="icon" href="{up}favicon.ico" sizes="any">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="{up}site.css">
<link rel="stylesheet" href="{up}viewer.css">
</head>
<body>
<script>
  /* 접힌 채로 시작할지는 그릴 때 이미 알아야 한다 — 나중에 정하면 차례가 한 번 번쩍인다.
     상태는 반드시 body 의 클래스로만 말한다. 여기서 규칙을 하나 더 써 넣으면 그 규칙이
     차례를 영영 붙들어서, 나중에 토글을 눌러도 열리지 않는다. */
  (function () {{
    var o = null;
    try {{ o = localStorage.getItem("podo-catalog-toc"); }} catch (e) {{}}
    if (o === "0" || (o === null && window.innerWidth < 1080)) document.body.classList.add("toc-off");
  }})();
</script>
<a class="podo-skip" href="#deck" data-i18n="ui.skip">본문으로 건너뛰기</a>
<header class="bar">
  <button class="tocbtn" id="toc" aria-controls="rail" aria-expanded="false">
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor"
      stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M2.5 4h11M2.5 8h11M2.5 12h7"/></svg>
    <span data-i18n="ui.toc">차례</span></button>
  <a class="brand" href="{home}"><img src="{up}favicon.svg" width="24" height="24" alt="">PODO</a>
  <span class="rule"></span>
  <nav class="crumb" data-i18n-label="ui.where" aria-label="현재 위치">
    <a class="crumb__up" id="track" href="{course_href}"></a>
    <span class="crumb__sep" aria-hidden="true">›</span>
    <span class="crumb__lv only-phone" id="lv"></span>
    <span class="crumb__here" id="here" aria-current="page"></span>
  </nav>
  <span class="right">
    <span class="seg" id="slots"></span>
    <a class="iconbtn" href="{deck}" target="_blank" rel="noopener" id="full"
      data-i18n-label="ui.fullScreen" aria-label="전체 화면">
      <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor"
        stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M2.2 6V2.2H6M10 2.2h3.8V6M2.2 10v3.8H6M13.8 10v3.8H10"/></svg></a>
    <span class="seg" id="loc" role="group"></span>
    <button class="iconbtn only-phone" id="morebtn" data-menu="phone"
      data-i18n-label="ui.more" aria-label="더 보기">⋯</button>
  </span>
</header>
<div class="railscrim" id="scrim"></div>
<aside class="rail" id="rail" data-i18n-label="ui.toc" aria-label="차례">
  <p class="railhead" id="pos"></p>
  <nav class="list" id="list"></nav>
  <div class="railfoot" id="foot"></div>
</aside>
<div class="menu" id="phone" hidden></div>
<main class="stage">
  <iframe id="deck" src="{deck}" title="{title}"></iframe>
</main>
<script src="{up}i18n.js"></script>
<script src="{toc_src}"></script>
<script>window.PODO_VIEW = {data};</script>
<script src="{up}viewer.js"></script>
</body>
</html>
"""


def write_viewer(out, base, course, lesson, deck, family, lang, built,
                 accent, tint, toc_src, flat, pos, slots) -> None:
    """뷰어 한 장. `flat` 은 트랙의 과를 코스 경계 없이 이어 놓은 목록이고 `pos` 는 그 안의 자리다."""
    path = base / (deck["href"] + ".html")
    path.parent.mkdir(parents=True, exist_ok=True)
    up = os.path.relpath(out, path.parent) + "/"
    links = nav_links(built, lang, up)
    track_page = base / "catalog" / f"{family['slug']}.html"

    def side(i):
        """앞뒤 과. 코스 경계를 넘어 트랙을 평평하게 걷는다."""
        if not 0 <= i < len(flat):
            return None
        c, l, slot = flat[i]
        return {"h": f"../../{c.slug}/{l.slug}/{slot}.html",
                "lv": course_level(c),
                "t": {k: str(v) for k, v in (l.spec.get("title") or {}).items()
                      if k in ("ko", "ja", "en") and v}}

    path.write_text(VIEWER.format(
        up=up,
        home=e(f"{up}index.html"),
        course_href=e(os.path.relpath(track_page, path.parent)),
        title=e(pick(lesson.spec.get("title"), "ko", "ja")),
        toc_src=e(toc_src),
        data=json.dumps({
            "track": {c: family[c] for c in ("ko", "ja", "en") if family.get(c)},
            "titleKo": pick(lesson.spec.get("title"), "ko", "ja"),
            "title": {k: str(v) for k, v in (lesson.spec.get("title") or {}).items()
                      if k in ("ko", "ja", "en") and v},
            "week": lesson.week,
            "level": course_level(course),
            "course": course.slug,
            "lesson": lesson.slug,
            "slot": deck["slot"],
            # 두 슬롯이 다 있는 과에서만 스위치가 두 갈래가 된다.
            "slots": slots,
            "pos": pos + 1,
            "total": len(flat),
            "prev": side(pos - 1),
            "next": side(pos + 1),
        }, ensure_ascii=False),
        accent=accent,
        tint=tint,
        deck=e(os.path.relpath(base / deck["entry"], path.parent)),
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
