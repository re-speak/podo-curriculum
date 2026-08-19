#!/usr/bin/env python3
"""Read each track's table of contents into one common shape.

Every track's TOC is a different document, written for people before it was ever
read by a tool: `2-core-patterns` is units of numbered 과, `1-hangul` and
`5-pronunciation` are markdown tables, `3-contextual-korean` is named shows with
episodes, `4-freetalking` is themes of session topics. There is no shared grammar
to parse, so there is a parser per track and this module is where they live.

Each returns the same thing — a list of courses, in TOC order:

    [{ "slug":  "kpop-talk",          # ascii, kebab; becomes the directory
       "level": "초급",                # picks classLevel band + difficulty
       "classLevelSlot": 10,          # optional stable .001 slot inside the band
       "title": {"ko":…, "en":…, "ja":…},
       "note":  "…",                  # one line for the course description
       "lessons": [
           { "no": 1,                  # position within the course
             "title": "최애 소개",
             "canDo": "…" | None,
             "patterns": ["A는 B예요", …],
             "scene": "…" | None } ] }]

`plan_courses.py` turns that into course.yaml / lesson.yaml. Nothing here knows
about YAML or schemas — a parser's only job is to read its own TOC honestly, and
to raise rather than guess when the document has moved on without it.
"""

from __future__ import annotations

import pathlib
import re

import shard_toc


# any heading at # or ## level ends a course block — an appendix after the
# last course must not be read as more of that course.
STOP_HEADING = re.compile(r"^#{1,2} ")


class ParseError(Exception):
    pass


# --------------------------------------------------------------------------- #
# shared bits
# --------------------------------------------------------------------------- #

def slugify(text: str) -> str:
    """A kebab-case ascii slug. Korean is dropped, so callers must supply
    romanised names for Korean-titled courses rather than relying on this."""
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", out)


def _patterns_from(block: list[str]) -> list[str]:
    """`- 제 최애는 민지예요. — `A는 B예요` (핵심 1)` -> the form in backticks."""
    out = []
    for line in block:
        m = re.match(r"^- (?!\*)(.+?) [—–] (.+?)\s*$", line)
        if not m:
            continue
        rest = m.group(2)
        g = re.match(r"^(.*?)\s*\(([^()]*)\)$", rest)
        form = (g.group(1) if g else rest).replace("`", "").strip()
        if form:
            out.append(form)
    return out


def _field(block: list[str], label: str) -> str | None:
    for line in block:
        m = re.match(rf"^\*{label}: (.+?)\*\s*$", line)
        if m:
            return m.group(1)
    return None


def _bullet_field(block: list[str], label: str) -> str | None:
    """Read `- *표현:* ...` fields used by the contextual TOC."""
    for line in block:
        m = re.match(rf"^- \*{label}:\*\s*(.+?)\s*$", line)
        if m:
            return m.group(1)
    return None


def _paragraph_field(block: list[str], label: str) -> str | None:
    """Read a bold label whose value may continue on following Markdown lines."""
    for i, line in enumerate(block):
        m = re.match(rf"^\*\*{label}:\*\*\s*(.*?)\s*$", line)
        if not m:
            continue
        value = [m.group(1)] if m.group(1) else []
        for following in block[i + 1:]:
            if not following.strip():
                break
            if following.startswith(("#", "**", "- ", ">")):
                break
            value.append(following.strip())
        return " ".join(value) or None
    return None


def _dialogues_from(block: list[str]) -> list[dict]:
    """Keep the contextual learner line, pattern and partner reaction together.

    `_patterns_from` is sufficient for course manifests, but an episode writer
    also needs the actual dramatic exchange. Keeping the reaction next to the
    pattern prevents a generated lesson from turning a scene into two unrelated
    example sentences.
    """
    dialogues = []
    for i, line in enumerate(block):
        m = re.match(r"^- (?!\*)(.+?) [—–] (.+?)\s*$", line)
        if not m:
            continue
        rest = m.group(2)
        g = re.match(r"^(.*?)\s*\(([^()]*)\)$", rest)
        form = (g.group(1) if g else rest).replace("`", "").strip()
        reference = g.group(2).strip() if g else None
        reaction = None
        if i + 1 < len(block):
            rm = re.match(r"^\s+→\s*(.+?)\s*$", block[i + 1])
            if rm:
                reaction = rm.group(1)
        dialogues.append({
            "line": m.group(1).strip(),
            "form": form,
            "reference": reference,
            "reaction": reaction,
        })
    return dialogues


def _split_blocks(lines: list[str], header: re.Pattern,
                  stop: re.Pattern | None = None) -> list[tuple[re.Match, list[str]]]:
    """Cut `lines` at every header match; return (match, body-until-next).

    `stop` ends the *last* block early. Without it a trailing block runs to EOF
    and swallows whatever follows — 3-contextual's last course was picking up the
    appendix's numbered rows and reporting 14 episodes where the header says 10.
    """
    hits = [(i, m) for i, l in enumerate(lines) if (m := header.match(l))]
    out = []
    for k, (i, m) in enumerate(hits):
        end = hits[k + 1][0] if k + 1 < len(hits) else len(lines)
        if stop is not None:
            for j in range(i + 1, end):
                if stop.match(lines[j]):
                    end = j
                    break
        out.append((m, lines[i + 1:end]))
    return out


# --------------------------------------------------------------------------- #
# 1-hangul · 5-pronunciation — one markdown table, one course
# --------------------------------------------------------------------------- #

TABLE_ROW = re.compile(r"^\|\s*\*\*(\d+)\.\s*(.+?)\*\*\s*(?:\*\([^)]*\)\*)?\s*\|(.*)$")


def _one_table_course(path: pathlib.Path, *, slug, level, title, note,
                      can_do_col: int, pattern_col: int, columns: int) -> list[dict]:
    """One course out of one markdown table.

    The two table tracks have different columns, so which one is the outcome and
    which holds the drillable pieces is passed in rather than guessed:

      1-hangul       | 레슨 | 새로 배우는 것 | 읽을 수 있는 것 |
      5-pronunciation| 레슨 | 일본어의 습관 | 고치는 법 | 최소 대립쌍 |
    """
    lessons = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TABLE_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(3).split("|")]
        cells = [c for c in cells if c] or [""]
        if len(cells) < columns:
            raise ParseError(
                f"{path}: '{m.group(2)}' has {len(cells)} columns, expected "
                f"{columns} — the table changed shape, so the column roles here are wrong")
        pieces = [p.strip() for p in re.split(r"[·,]", cells[pattern_col])
                  if 0 < len(p.strip()) < 40]
        lessons.append({
            "no": int(m.group(1)),
            "title": re.sub(r"\s*\*\([^)]*\)\*", "", m.group(2)).strip(),
            "canDo": cells[can_do_col] or None,
            "patterns": pieces[:8],
            "scene": None,
        })
    if not lessons:
        raise ParseError(f"{path}: no `| **N. title** |` rows — the table shape changed")
    lessons.sort(key=lambda l: l["no"])
    return [{"slug": slug, "level": level, "title": title, "note": note,
             "lessons": lessons}]


def parse_hangul(track: pathlib.Path) -> list[dict]:
    return _one_table_course(
        track / "table-of-contents.md",
        slug="",
        level="왕초급",
        title={},   # one course in the track — plan_courses.compose() names it
        note="자음 · 모음 · 받침을 거쳐 간판을 읽기까지.",
        columns=2, can_do_col=1, pattern_col=0)   # 새로 배우는 것 | 읽을 수 있는 것


def parse_pronunciation(track: pathlib.Path) -> list[dict]:
    return _one_table_course(
        track / "table-of-contents.md",
        slug="",
        level="초급",
        title={},   # one course in the track — plan_courses.compose() names it
        note="일본어 습관이 무너뜨리는 대립만 골라 듣기부터 고친다.",
        columns=3, can_do_col=1, pattern_col=2)   # 습관 | 고치는 법 | 최소 대립쌍


# --------------------------------------------------------------------------- #
# 3-contextual-korean — each named show is a course
# --------------------------------------------------------------------------- #

CTX_COURSE = re.compile(
    r"^## (.+?) \[(.+?)\] · (\d+) ?(?:화|레슨)(?: · .*)?$")
# A header may carry a trailing annotation outside the bold — 가족 & 일상 marks
# who speaks with `*(엄마 → 나)*`. Capture it rather than refusing the line.
CTX_LESSON = re.compile(r"^\*\*(\d+) ?(?:화|레슨)? ?[·.] (.+?)\*\*\s*(.*)$")

# Korean course names need romanised directory names; slugify() drops hangul.
CTX_SLUGS = {
    "설렘 & 고백": ("drama-crush", "Crush & confession", "ときめきと告白"),
    "갈등 & 화해": ("drama-makeup", "Conflict & making up", "すれ違いと仲直り"),
    "가족 & 일상": ("drama-family", "Family & everyday", "家族と日常"),
    "경계 & 갈등": ("drama-boundaries", "Boundaries & friction", "境界と衝突"),
    "케이팝 토크": ("kpop-talk", "K-pop talk", "K-POPトーク"),
    "무대 & 감상": ("kpop-stage", "Stage & watching", "ステージと鑑賞"),
    "케이팝 팬 라이프": ("kpop-fan-life", "K-pop fan life", "K-POPファンライフ"),
    "온라인 팬덤 & 커뮤니티": ("kpop-online", "Online fandom", "オンラインファンダム"),
    "길 & 교통": ("travel-getting-around", "Getting around", "道と交通"),
    "식당 & 카페": ("travel-eating-out", "Eating out", "レストランとカフェ"),
    "쇼핑 & 결제": ("travel-shopping", "Shopping & paying", "買い物と支払い"),
    "숙소 & 문제 해결": ("travel-staying", "Staying & fixing problems", "宿泊とトラブル"),
    "말 놓기 — 존댓말에서 반말로": ("banmal-dropping-formality",
                                "Dropping formality", "タメ口への切り替え"),
    "반말로 수다 떨기": ("banmal-chatting", "Chatting in banmal", "タメ口でおしゃべり"),
}


def parse_contextual(track: pathlib.Path) -> list[dict]:
    lines = (track / "table-of-contents.md").read_text(encoding="utf-8").splitlines()
    courses = []
    for m, body in _split_blocks(lines, CTX_COURSE, STOP_HEADING):
        name, level, _count = m.group(1).strip(), m.group(2).strip(), int(m.group(3))
        known = CTX_SLUGS.get(name)
        if known is None:
            raise ParseError(
                f"course '{name}' has no entry in CTX_SLUGS — add a romanised slug "
                f"and en/ja titles (the directory name cannot be Korean)")
        slug, t_en, t_ja = known
        # "초급 → 초중급" means it opens at 초급; the entry level is what gates it.
        entry = level.split("→")[0].strip()
        first_lesson = next((i for i, line in enumerate(body)
                             if CTX_LESSON.match(line)), len(body))
        prelude = body[:first_lesson]
        work = next((m.group(1) for line in prelude
                     if (m := re.match(r"^> ### 《(.+?)》\s*$", line))), None)
        cast = next((m.group(1) for line in prelude
                     if (m := re.match(r"^> \*\*등장인물\*\* — (.+?)\s*$", line))), None)
        story = [line[2:].strip() for line in prelude
                 if line.startswith("> ")
                 and not line.startswith("> ### ")
                 and not line.startswith("> **등장인물**")]
        story = [line for line in story if line]
        lessons = []
        for lm, lbody in _split_blocks(body, CTX_LESSON):
            aside = re.sub(r"[*`]", "", lm.group(3)).strip()
            dialogues = _dialogues_from(lbody)
            lessons.append({
                "no": int(lm.group(1)),
                "title": lm.group(2).strip() + (f" {aside}" if aside else ""),
                "canDo": _field(lbody, "할 수 있는 것"),
                "patterns": [d["form"] for d in dialogues],
                "scene": _field(lbody, "장면"),
                "dialogues": dialogues,
                "expressions": _bullet_field(lbody, "표현"),
                "grammar": _bullet_field(lbody, "문법"),
                "understanding": _bullet_field(lbody, "이해"),
                "chunk": _bullet_field(lbody, "덩어리"),
                "memo": _bullet_field(lbody, "메모"),
            })
        if not lessons:
            raise ParseError(f"course '{name}' parsed 0 lessons")
        lessons.sort(key=lambda l: l["no"])
        note = _paragraph_field(prelude, "끝내면 할 수 있는 것") or ""
        courses.append({"slug": slug, "level": entry, "note": note,
                        "work": work, "cast": cast, "story": story,
                        "title": {"ko": name, "en": t_en, "ja": t_ja},
                        "lessons": lessons})
    if not courses:
        raise ParseError("no `## name [level] · N 화` course headers found")
    return courses


# --------------------------------------------------------------------------- #
# 4-freetalking — each theme is a course of session topics
# --------------------------------------------------------------------------- #

FT_THEME = re.compile(r"^# (\d+)\. (.+?)\s*$")
# `7. **나이 들면 왜 친구가 줄어들까** `[깊게]`` — the tail may be a dash-description,
# a [깊게] marker, or both. [깊게] is not decoration: the TOC says those topics are
# good but must wait until there is a relationship, so keep it as structured metadata.
FT_TOPIC = re.compile(r"^(\d+)\. \*\*(.+?)\*\*\s*(.*)$")

FT_FORMATS = {
    "이야기",
    "고르기",
    "한일",
    "의견",
    "이야기 + 의견",
    "이야기 + 고르기",
}

FT_SLUGS = {
    1: ("between-two-countries", "Between two countries", "ふたつの国のあいだ"),
    2: ("me-lately", "Me lately", "最近のわたし"),
    3: ("things-i-like", "Things I like", "好きなもの"),
    4: ("small-things", "Small things", "ささいなこと"),
    5: ("people-and-ties", "People & ties", "人と関係"),
    6: ("love-and-marriage", "Love & marriage", "恋愛と結婚"),
    7: ("work-and-money", "Work & money", "仕事とお金"),
    8: ("what-came-before", "What came before", "過ぎてきたもの"),
    9: ("what-if", "What if", "もしも"),
    10: ("worth-thinking-about", "Worth thinking about", "考えてみたいこと"),
    11: ("balance-games", "Balance games", "究極の二択"),
}

# Each topic exists at both levels. Intermediate is placed in the insertion slot
# immediately before its existing Advanced sibling, so the shipped Advanced
# natural keys (400.010, 400.020, ...) never move.
FT_LEVELS = (
    ("중급", -1),
    ("고급", 0),
)


def parse_freetalking(track: pathlib.Path) -> list[dict]:
    lines = (track / "table-of-contents.md").read_text(encoding="utf-8").splitlines()
    courses = []
    for m, body in _split_blocks(lines, FT_THEME, STOP_HEADING):
        n, name = int(m.group(1)), m.group(2).strip()
        known = FT_SLUGS.get(n)
        if known is None:
            raise ParseError(f"theme {n} ('{name}') has no entry in FT_SLUGS")
        slug, t_en, t_ja = known
        outcome = _paragraph_field(body, "Course outcome")
        if not outcome:
            raise ParseError(
                f"free-talking theme {n} ('{name}') has no `**Course outcome:**` field"
            )
        session_format = _paragraph_field(body, "Session format")
        if not session_format:
            raise ParseError(
                f"free-talking theme {n} ('{name}') has no `**Session format:**` field"
            )
        if session_format not in FT_FORMATS:
            allowed = ", ".join(sorted(FT_FORMATS))
            raise ParseError(
                f"free-talking theme {n} ('{name}') has unknown session format "
                f"'{session_format}' (expected one of: {allowed})"
            )
        if re.search(r"[*`]", outcome):
            raise ParseError(
                f"free-talking theme {n} ('{name}') course outcome contains "
                "unresolved Markdown markup"
            )
        lessons = []
        for tm in (FT_TOPIC.match(l) for l in body):
            if not tm:
                continue
            tail = tm.group(3).strip()
            deep = "[깊게]" in tail
            desc = re.sub(r"`?\[깊게\]`?", "", tail).lstrip("—– ").strip()
            lesson_no = int(tm.group(1))
            title = tm.group(2).strip()
            if not desc:
                raise ParseError(
                    f"free-talking theme {n} ('{name}') lesson {lesson_no} "
                    f"('{title}') has no observable outcome after `—`"
                )
            lessons.append({
                "no": lesson_no,
                "title": title,
                "canDo": desc,
                "deep": deep,
                "patterns": [], "scene": None,
            })
        if not lessons:
            raise ParseError(f"theme '{name}' parsed 0 session topics")
        numbers = [lesson["no"] for lesson in lessons]
        expected = list(range(1, len(lessons) + 1))
        if numbers != expected:
            raise ParseError(
                f"free-talking theme {n} ('{name}') lesson numbers must be "
                f"continuous from 1 (found {numbers})"
            )
        for level, slot_offset in FT_LEVELS:
            courses.append({
                "slug": slug,
                "level": level,
                "classLevelSlot": n * 10 + slot_offset,
                "pairKey": slug,
                "note": outcome,
                "sessionFormat": session_format,
                "title": {"ko": name, "en": t_en, "ja": t_ja},
                "lessons": [lesson.copy() for lesson in lessons],
            })
    if not courses:
        raise ParseError("no `# N. theme` headers found")
    return courses


# --------------------------------------------------------------------------- #
# 2-core-patterns — units packed into ~12-lesson courses (see plan_courses.py)
# --------------------------------------------------------------------------- #

def parse_core(track: pathlib.Path) -> list[dict]:
    """Units, already parsed by shard_toc; plan_courses packs them into courses."""
    units = shard_toc.parse(track / "table-of-contents.md")
    if not units:
        raise ParseError("shard_toc parsed 0 units")
    return units


PARSERS = {
    "1-hangul": parse_hangul,
    "2-core-patterns": parse_core,
    "3-contextual-korean": parse_contextual,
    "4-freetalking": parse_freetalking,
    "5-pronunciation": parse_pronunciation,
}
