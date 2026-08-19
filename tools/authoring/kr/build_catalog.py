#!/usr/bin/env python3
"""tracks/*/table-of-contents.md → korean/catalog.html

The catalog is the visual table of contents for every track: level ladder,
per-track stats, and every lesson with what it teaches. It holds no facts of its
own — everything on the page is parsed out of the five TOCs, so the way to change
the catalog is to change the TOC and re-run this.

    python3 tools/authoring/kr/build_catalog.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import track_parsers

ROOT = Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"          # korean/
TRACKS = ROOT / "tracks"
OUT = ROOT / "catalog.html"                            # 관문
OUT_DIR = ROOT / "catalog"                             # 트랙별 상세

LEVELS = ["왕초급", "초급", "초중급", "중급", "중고급", "고급"]


# ---------------------------------------------------------------- helpers

def read(track: str) -> list[str]:
    return (TRACKS / track / "table-of-contents.md").read_text(encoding="utf-8").splitlines()


def unbold(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()


def plain(s: str) -> str:
    """Markdown inline → text, keeping backticked terms as-is."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = s.replace("`", "")
    return s.strip()


def split_title(s: str) -> tuple[str, str]:
    """'저는 다나카예요 — 이름 주고받기' → ('저는 다나카예요', '이름 주고받기')"""
    if " — " in s:
        head, tail = s.split(" — ", 1)
        return head.strip(), tail.strip()
    return s.strip(), ""


def ticks(s: str) -> list[str]:
    return re.findall(r"`([^`]+)`", s)


def primary_level(s: str) -> str:
    """'초급 → 초중급' → '초급'. Unknown labels fall back to the last known level."""
    for lv in LEVELS:
        if s.startswith(lv):
            return lv
    for lv in LEVELS:
        if lv in s:
            return lv
    return LEVELS[-1]


def level_span(s: str) -> list[str]:
    """'초급 → 초중급' → 그 사이 전부. 왕초급/중고급이 초급/고급을 부분 문자열로 품으므로
    긴 이름부터 지워 가며 찾는다."""
    rest, hits = s, []
    for lv in sorted(LEVELS, key=len, reverse=True):
        if lv in rest:
            hits.append(lv)
            rest = rest.replace(lv, "·")
    hits.sort(key=LEVELS.index)
    if not hits:
        return [LEVELS[-1]]
    lo, hi = LEVELS.index(hits[0]), LEVELS.index(hits[-1])
    return LEVELS[lo:hi + 1]


# ------------------------------------------- 배우는 것을 문장 안에서 짚기

HANGUL = re.compile(r"[가-힣]+")


def chunks_of(pattern: str) -> list[str]:
    """패턴을 이루는 실제 한글 덩어리.

    `N이에요/예요` → 이에요 · 예요 ·  `~(으)ㄴ 적 있다` → 으 · 적 · 있다
    자리표시자(N/A/V)와 물결·괄호·낱자모는 문장에 나타날 수 없으므로 구분자 역할만 한다.
    """
    seen, out = set(), []
    for c in HANGUL.findall(pattern):
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


JONGSUNG = "  ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"[1:]


def locate_jamo(sentence: str, jamo: str) -> tuple[int, int] | None:
    """받침으로 실현되는 패턴을 음절 단위로 짚는다.

    `-(으)ㄴ N` 의 ㄴ 은 예【쁜】 옷 처럼 앞 음절의 받침으로만 나타나므로 글자
    비교로는 절대 걸리지 않는다. 관형사형이 이 트랙의 큰 산이라 이것만 따로 본다.
    관형사형은 뒤에 꾸밀 명사가 오므로, 어절 끝에 있는 음절을 먼저 고른다.
    """
    best = None
    for i, ch in enumerate(sentence):
        if not ("가" <= ch <= "힣"):
            continue
        if JONGSUNG[(ord(ch) - 0xAC00) % 28] != jamo:
            continue
        score = 0 if sentence[i + 1:i + 2] == " " else 1
        if best is None or score < best[0]:
            best = (score, i)
    return (best[1], best[1] + 1) if best else None


def locate(sentence: str, chunk: str) -> tuple[int, int] | None:
    """이 덩어리가 문장의 어디에 앉아 있는지.

    사전형은 활용을 견디지 못하므로(있다 → 있지) 뭔가 걸릴 때까지 꼬리를 자른다.
    한 음절짜리는 어절 끝에 붙은 자리를 고른다 — 조사가 붙는 자리가 거기다:
    사람【이】 선생님이에요, 사람이 선생님【이】에요가 아니라.
    """
    # 꼬리부터 자르고(있다 → 있), 그래도 없으면 머리부터 자른다(습니다 → 니다):
    # 활용은 앞이 줄기도 하고 뒤가 줄기도 한다
    trims = [chunk[:i] for i in range(len(chunk), 0, -1)]
    trims += [chunk[j:] for j in range(1, len(chunk))]
    for v in trims:
        if len(v) == 1:
            best = None
            for m in re.finditer(re.escape(v), sentence):
                tail = sentence[m.end():m.end() + 1]
                score = 0 if tail in ("", " ", ".", "?", "!", ",") else 1
                if best is None or score < best[0]:
                    best = (score, m.start())
            if best:
                return best[1], best[1] + 1
        else:
            j = sentence.rfind(v)
            if j >= 0:
                return j, j + len(v)
    return None


def find_spans(sentence: str, pattern: str) -> list[list[int]]:
    hits = [h for c in chunks_of(pattern) if (h := locate(sentence, c))]
    if not hits:
        for jamo in re.findall(r"[-~(\)으]\s*([ㄴㄹㅁㅂ])(?![가-힣])", pattern):
            if h := locate_jamo(sentence, jamo):
                hits.append(h)
    if not hits:
        return []

    hits.sort()
    clusters: list[list[int]] = []
    for a, b in hits:
        if clusters and a - clusters[-1][1] <= 1:      # 적 + 있 은 한 덩어리다
            clusters[-1][1] = max(clusters[-1][1], b)
        else:
            clusters.append([a, b])

    strong = [c for c in clusters if c[1] - c[0] >= 2]  # 외톨이 한 음절은 잡음이다
    keep = strong or clusters[:1]                       # 아무것도 안 걸렸을 때만 봐준다
    if sum(b - a for a, b in keep) > len(sentence) * 0.7:
        keep = [max(keep, key=lambda c: c[1] - c[0])]
    return keep


def pattern_bullet(line: str) -> dict | None:
    r"""``- 저는 다나카예요. — `N이에요/예요` (명사 서술형 "です")`` 한 줄을 뜯는다."""
    body = line[2:].strip()
    tick = ticks(body)
    if not tick:
        return None
    ex = plain(body.split(" — ")[0]) if " — " in body else ""
    pat = tick[0]
    gloss = ""
    m = re.search(r"`\s*\((.+?)\)\s*$", body)
    if m:
        gloss = plain(m.group(1))
    return {"ex": ex, "pat": pat, "gloss": gloss,
            "spans": find_spans(ex, pat) if ex else []}


# ---------------------------------------------------------------- 1 · 한글

def parse_hangul() -> list[dict]:
    groups: list[dict] = []
    for line in read("1-hangul"):
        m = re.match(r"^## (\d+부) · (.+)$", line)
        if m:
            groups.append({"label": m.group(1), "title": m.group(2), "level": "왕초급",
                           "blurb": "", "lessons": []})
            continue
        m = re.match(r"^\| \*\*(\d+)\. (.+?)\*\*\s*(\*\([^)]+\)\*)?\s*\|(.+)\|(.+)\|\s*$", line)
        if m and groups:
            note = plain(m.group(3) or "").strip("()")
            pieces = [p.strip() for p in plain(m.group(4)).split(" · ") if p.strip()]
            groups[-1]["lessons"].append({
                "n": int(m.group(1)),
                "title": m.group(2).strip(),
                "sub": note,
                "can": plain(m.group(5)),
                "canLabel": "읽을 수 있다",
                "level": "왕초급",
                "chips": pieces[:6],
            })
    return groups


# ------------------------------------------------------- 2 · 핵심 문법 패턴

def parse_core() -> list[dict]:
    groups: list[dict] = []
    lines = read("2-core-patterns")
    started = False
    cur: dict | None = None
    for i, line in enumerate(lines):
        if line.startswith("# Part "):
            started = True
        if not started:
            continue

        m = re.match(r"^## Unit (\d+) · (.+?) · (\d+)과 · \*\*(.+?)\*\*\s*$", line)
        if m:
            title, sub = split_title(m.group(2))
            groups.append({
                "label": f"Unit {m.group(1)}",
                "title": title, "subtitle": sub,
                "level": primary_level(m.group(4)),
                "levelText": m.group(4),
                "blurb": "", "lessons": [],
            })
            cur = None
            continue
        if not groups:
            continue

        if not groups[-1]["blurb"] and re.match(r"^\*[^*].+\*$", line) and not groups[-1]["lessons"]:
            groups[-1]["blurb"] = plain(line)
            continue

        m = re.match(r"^\*\*(\d+)\. (.+?)\*\*\s*$", line)
        if m:
            title, sub = split_title(m.group(2))
            cur = {"n": int(m.group(1)), "title": title, "sub": sub, "can": "",
                   "canLabel": "할 수 있다", "level": groups[-1]["level"],
                   "chips": [], "pats": [], "notes": []}
            groups[-1]["lessons"].append(cur)
            continue

        if cur is None:
            continue

        m = re.match(r"^\*할 수 있는 것: (.+)\*$", line)
        if m:
            cur["can"] = plain(m.group(1))
            continue
        m = re.match(r"^- \*(표현|문법|메모|이해):\*\s*(.+)$", line)
        if m:
            cur["notes"].append({"k": m.group(1), "v": plain(m.group(2))})
            continue
        if line.startswith("- "):
            b = pattern_bullet(line)
            if b:
                cur["pats"].append(b)
                if b["pat"] not in cur["chips"]:
                    cur["chips"].append(b["pat"])
            cur["np"] = cur.get("np", 0) + 1
            continue
        m = re.match(r"^\*▸ 체크포인트 \d+ · (.+?)\*$", line)
        if m:
            groups[-1]["checkpoint"] = plain(m.group(1))
            cur = None
    return groups


# --------------------------------------------------- 3 · 상황별 한국어

def parse_contextual() -> list[dict]:
    groups: list[dict] = []
    lines = read("3-contextual-korean")
    area = ""
    started = False
    cur: dict | None = None
    for line in lines:
        m = re.match(r"^# (드라마|케이팝|여행|반말)\s*$", line)
        if m:
            area, started, cur = m.group(1), True, None
            continue
        if not started:
            continue

        if line.startswith(("# ", "## ")):
            m2 = re.match(r"^## (.+?) \[(.+?)\] · (\d+) ?(화|레슨) · 문법 최고점: 핵심 (\d+)과\s*$", line)
            if not m2:
                started = bool(re.match(r"^# (드라마|케이팝|여행|반말)", line))
                cur = None
                continue
        m = re.match(r"^## (.+?) \[(.+?)\] · (\d+) ?(화|레슨) · 문법 최고점: 핵심 (\d+)과\s*$", line)
        if m:
            groups.append({
                "label": area, "title": m.group(1),
                "level": primary_level(m.group(2)), "levelText": m.group(2),
                "unit": m.group(4), "peak": int(m.group(5)),
                "blurb": "", "story": "", "cast": "", "work": "",
                "lessons": [],
            })
            cur = None
            continue
        if not groups:
            continue
        g = groups[-1]

        if line.startswith("> "):
            q = line[2:].strip()
            m = re.match(r"^### 《(.+?)》", q)
            if m:
                g["work"] = m.group(1)
                continue
            m = re.match(r"^\*\*등장인물\*\* — (.+)$", q)
            if m:
                g["cast"] = plain(m.group(1))
                continue
            if not q.startswith("**") and not g["lessons"]:
                # 줄거리에 섞인 튜터 지시("튜터는 2화 첫머리에서…")는 제작 노트다.
                # 카탈로그는 이 코스가 어떤 이야기인지만 보여 준다.
                keep = [t for t in re.split(r"(?<=[.!?])\s+", plain(q))
                        if t and "튜터" not in t and "체험 레슨" not in t]
                if keep:
                    g["story"] = (g["story"] + " " + " ".join(keep)).strip()
            continue

        m = re.match(r"^\*\*끝내면 할 수 있는 것:\*\* (.+)$", line)
        if m:
            g["blurb"] = plain(m.group(1))
            continue
        if g["blurb"] and not line.startswith("**") and line.strip() and not g["lessons"] \
                and not line.startswith(("*", "-", "#", "|", ">")):
            g["blurb"] = (g["blurb"] + " " + plain(line)).strip()
            continue

        m = re.match(r"^\*\*(\d+)(화)? ?[·.] ?(.+?)\*\*\s*(\*\([^)]*\)\*)?\s*$", line)
        if m:
            title, sub = split_title(m.group(3))
            # Family-drama episodes put the speaking direction just outside the
            # bold title: **잔소리** *(엄마 → 나)*. It is part of the canonical
            # lesson identity used by plan_courses.py and the deck index.
            if m.group(4):
                title = f"{title} {plain(m.group(4))}"
            cur = {"n": int(m.group(1)), "title": title, "sub": sub, "scene": "", "can": "",
                   "canLabel": "할 수 있다", "level": g["level"],
                   "chips": [], "pats": [], "refs": [], "notes": []}
            g["lessons"].append(cur)
            continue

        if cur is None:
            continue
        m = re.match(r"^\*장면: (.+)\*$", line)
        if m:
            cur["scene"] = plain(m.group(1))
            continue
        m = re.match(r"^\*할 수 있는 것: (.+)\*$", line)
        if m:
            cur["can"] = plain(m.group(1))
            continue
        m = re.match(r"^- \*(표현|문법|메모|이해):\*\s*(.+)$", line)
        if m:
            cur["notes"].append({"k": m.group(1), "v": plain(m.group(2))})
            continue
        if line.startswith("- "):
            b = pattern_bullet(line)
            if b:
                cur["pats"].append(b)
                if b["pat"] not in cur["chips"]:
                    cur["chips"].append(b["pat"])
            for r in re.findall(r"핵심 (\d+)", line):
                if int(r) not in cur["refs"]:
                    cur["refs"].append(int(r))
            continue
        if line.strip().startswith("→ ") and cur.get("pats"):
            cur["pats"][-1]["reply"] = plain(line.strip()[2:])
    return groups


# ------------------------------------------------- 4 · 중급·고급 프리토킹

def parse_freetalking() -> list[dict]:
    groups: list[dict] = []
    lines = read("4-freetalking")
    italic = False
    for i, line in enumerate(lines):
        m = re.match(r"^# (\d+)\. (.+)$", line)
        if m:
            groups.append({"label": f"테마 {m.group(1)}", "title": m.group(2).strip(),
                           "level": "중급", "levelText": "중급 · 고급",
                           "levels": ["중급", "고급"],
                           "blurb": "", "form": "", "lessons": []})
            italic = False
            continue
        m = re.match(r"^# 워밍업 은행 — (.+)$", line)
        if m:
            groups.append({"label": "워밍업 은행", "title": m.group(1).strip(),
                           "level": "중급", "levelText": "중급 · 고급",
                           "levels": ["중급", "고급"],
                           "blurb": "", "form": "고르기",
                           "warmup": True, "lessons": []})
            italic = False
            continue
        if not groups:
            continue
        g = groups[-1]

        m = re.match(r"^\*\*Course outcome:\*\*\s*(.+?)\s*$", line)
        if m:
            g["blurb"] = plain(m.group(1))
            continue
        m = re.match(r"^\*\*Session format:\*\*\s*(.+?)\s*$", line)
        if m:
            g["form"] = plain(m.group(1))
            continue

        # 테마 설명은 여러 줄에 걸친 한 덩어리의 이탤릭이라 닫는 * 를 만날 때까지 이어 붙인다
        if not g["lessons"] and (italic or (line.startswith("*") and not line.startswith("* "))):
            italic = not line.rstrip().endswith("*") or line.strip() == "*"
            g["blurb"] = (g["blurb"] + " " + plain(line)).strip().strip("*").strip()
            m = re.search(r"형식은 (?:전부 )?\*\*(.+?)\*\*", line)
            if m:
                g["form"] = m.group(1)
            continue

        # Editorial flags have appeared both as `[깊게]` and as
        # `` `[깊게]` `` in the TOC.  Keep either spelling out of the
        # observable outcome so the catalog can match the generated course
        # plan, which records the flag after the lesson title.
        m = re.match(
            r"^(\d+)\. \*\*(.+?)\*\*(?: — (.*?))?"
            r"(?:\s+`?\[([^\]]+)\]`?)?\s*$",
            line,
        )
        if m:
            g["lessons"].append({"n": int(m.group(1)), "title": m.group(2).strip(),
                                 "sub": plain(m.group(4) or ""),
                                 "can": plain(m.group(3) or ""),
                                 "canLabel": "이야기한다", "level": "중급",
                                 "levels": ["중급", "고급"], "chips": []})
            continue
        m = re.match(r"^(\d+)\. (.+?) \*\*vs\*\* (.+)$", line)
        if m and g.get("warmup"):
            g["lessons"].append({"n": int(m.group(1)),
                                 "title": f"{plain(m.group(2))} vs {plain(m.group(3))}",
                                 "sub": "", "can": "", "canLabel": "", "level": "중급",
                                 "levels": ["중급", "고급"],
                                 "chips": []})
    for group in groups:
        if group.get("warmup"):
            continue
        if not group["blurb"]:
            raise ValueError(f"free-talking {group['label']} has no Course outcome")
        if group["form"] not in track_parsers.FT_FORMATS:
            raise ValueError(
                f"free-talking {group['label']} has invalid Session format: "
                f"{group['form']!r}"
            )
        if not group["lessons"]:
            raise ValueError(f"free-talking {group['label']} has no lessons")
        missing = [str(lesson["n"]) for lesson in group["lessons"] if not lesson["can"]]
        if missing:
            raise ValueError(
                f"free-talking {group['label']} lessons missing outcomes: "
                + ", ".join(missing)
            )
    return groups


# --------------------------------------------------------- 5 · 발음 교정

def parse_pronunciation() -> list[dict]:
    groups: list[dict] = []
    for line in read("5-pronunciation"):
        m = re.match(r"^## (\d+부) · (.+)$", line)
        if m:
            groups.append({"label": m.group(1), "title": m.group(2), "level": "",
                           "blurb": "", "lessons": []})
            continue
        m = re.match(r"^\| \*\*(\d+)\. (.+?)\*\*\s*(\*\([^)]+\)\*)?\s*\|(.+?)\|(.+?)\|(.+?)\|\s*$", line)
        if m and groups:
            pairs = [p.strip() for p in plain(m.group(6)).split(" · ") if p.strip()]
            groups[-1]["lessons"].append({
                "n": int(m.group(1)),
                "title": m.group(2).strip(),
                "sub": plain(m.group(3) or "").strip("()"),
                "can": plain(m.group(4)),
                "canLabel": "일본어의 습관",
                "fix": plain(m.group(5)),
                "level": "", "chips": pairs[:6],
            })
    return groups


# -------------------------------------------------- 이미 써 놓은 덱 찾아 붙이기

def deck_index(track: str) -> dict[str, list[dict]]:
    """다 쓴 덱을 그 과의 목차 제목으로 찾아 준다.

    한 주제에 중급·고급 덱이 함께 있을 수 있으므로 값은 경로 하나가 아니라
    ``[{href, level}, ...]`` 이다.

    **파일이 있다고 다 쓴 과가 아니다.** `new_lesson.py` 는 페이지가 한 장도 없는
    골격을 먼저 깔아 두므로(`.phone` 이 비어 있는 lesson.html), 다 쓴 덱은 페이지가
    한 장이라도 있는 것 — 즉 `data-act` 를 가진 것 — 으로만 센다. 이 조건을 빼면
    아직 아무것도 안 쓴 과 수십 개가 카탈로그에서 완성으로 보인다.

    그 덱이 목차의 몇 과인지는 그 코스의 과 목록(`course.yaml` 주석)이 정한다. 목록은
    코스 안에서 매긴 번호이고 슬러그 앞의 숫자도 같은 번호라, 둘을 맞추면 제목이 나온다.
    번호만으로 트랙 전체에서 과를 찾지 않는 이유는 트랙 3·4 의 과 번호가 코스마다 1부터
    다시 시작하기 때문이다 — 거기서는 코스를 거치지 않으면 과를 특정할 수 없다.
    """
    out: dict[str, list[dict]] = {}
    for deck in sorted((TRACKS / track).glob("courses/*/lessons/*/lesson.html")):
        if "data-act=" not in deck.read_text(encoding="utf-8"):
            continue                                   # 아직 페이지가 없는 골격
        slug = deck.parent.name
        n = int(m.group(1)) if (m := re.match(r"(\d+)-", slug)) else 0
        course_path = deck.parent.parent.parent / "course.yaml"
        course_text = course_path.read_text(encoding="utf-8")
        title = course_titles(course_path).get(n, "")
        # 덱을 쓴 과의 줄은 `✓ <슬러그><제목>` 이라 슬러그가 제목 앞에 붙어 있다
        if title.startswith(slug):
            title = title[len(slug):].strip()
        # `[깊게]` is an editorial/sensitivity flag, not part of the lesson's
        # learner-facing title.  The TOC parser exposes it separately as the
        # lesson sublabel, while plan_courses.py intentionally records it in
        # the course comment.  Normalize the comment before title matching.
        title = re.sub(r"\s+\[깊게\]\s*$", "", title)
        level_match = re.search(r"^  # podo:level: (.+)$", course_text, re.MULTILINE)
        level = level_match.group(1).strip() if level_match else ""
        out.setdefault(title or slug, []).append({
            "href": str(deck.relative_to(ROOT)),
            "level": level,
        })
    return out


def course_titles(course: Path) -> dict[int, str]:
    """`course.yaml` 꼬리의 과 목록 주석 → {코스 안의 과 번호: 목차 제목}

    `#     7  ✓ 07-daily-routine저는 매일 운동해요 — 하루 일과 말하기`  (덱을 쓴 과)
    `#     9  ·  와, 진짜 맛있네요! — 느낌 바로 말하기`                 (아직 안 쓴 과)
    """
    if not course.exists():
        return {}
    out: dict[int, str] = {}
    for line in course.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#\s+(\d+)\s+[✓·]\s*(.+)$", line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def attach_decks(track: str, groups: list[dict]) -> list[dict]:
    """완성된 덱을 그 과에 붙이고, 붙은 것들을 순서대로 돌려준다."""
    idx = deck_index(track)
    made: list[dict] = []
    for g in groups:
        for l in g["lessons"]:
            full = f"{l['title']} — {l['sub']}" if l.get("sub") else l["title"]
            decks = idx.pop(full, None) or idx.pop(l["title"], None)
            if decks:
                l["decks"] = decks
                for deck in decks:
                    made.append({"n": l["n"], "title": l["title"], **deck,
                                 "group": g.get("label", "")})
    for orphan, decks in idx.items():
        # 덱은 다 썼는데 목차의 과에 못 붙었다 — 대개 course.yaml 의 ✓ 줄이 낡은 것이라
        # plan_courses.py 를 다시 돌리면 된다. 조용히 빠뜨리면 카탈로그에서 영영 안 보인다.
        hrefs = ", ".join(deck["href"] for deck in decks)
        print(f"   ! {track}: 목차에서 못 찾은 덱 — {orphan} ({hrefs})")
    return made


def mark_first_lesson(groups: list[dict]) -> None:
    """워밍업 은행이 아닌 커리큘럼의 실제 시작점 하나만 표시한다."""
    for g in groups:
        if not g.get("warmup") and g["lessons"]:
            g["lessons"][0]["first"] = True
            return


# ---------------------------------------------------------------- assembly

def count_by_level(groups: list[dict]) -> dict[str, int]:
    """워밍업 은행은 과가 아니라 5분짜리 여는 질문이라 과 수에 넣지 않는다."""
    out: dict[str, int] = {}
    for g in groups:
        levels = g.get("levels") or [g.get("level") or ""]
        if not any(levels) or g.get("warmup"):
            continue
        for lv in levels:
            out[lv] = out.get(lv, 0) + len(g["lessons"])
    return out


def build() -> dict:
    hangul = parse_hangul()
    core = parse_core()
    ctx = parse_contextual()
    free = parse_freetalking()
    pron = parse_pronunciation()

    core_patterns = sum(l.get("np", 0) for g in core for l in g["lessons"])
    ctx_lessons = sum(len(g["lessons"]) for g in ctx)
    free_themes = sum(1 for g in free if not g.get("warmup"))
    free_topics = sum(len(g["lessons"]) for g in free if not g.get("warmup"))
    free_warmups = sum(len(g["lessons"]) for g in free if g.get("warmup"))

    tracks = [
        {
            "id": "1-hangul", "no": 1, "ko": "한글 읽기", "en": "Hangul Reading",
            "glyph": "가", "status": "live", "accent": "#4f7d10", "tint": "#f2f7e8",
            "unitWord": "부", "lessonWord": "레슨",
            "desc": "한글을 한 번도 본 적 없는 상태에서 어떤 한국어 음절이든 소리 내어 읽는 데까지. "
                    "한 과에 새 요소는 하나만 얹고, 80%는 복습으로 채웁니다.",
            "note": "《세종학당 한국어 입문》과 같은 순서 — 모음 → 자음 → 격음 → 경음 → 받침 → 연음.",
            "stats": [("레슨", len(hangul[0]["lessons"]) + len(hangul[1]["lessons"]) + len(hangul[2]["lessons"])),
                      ("부", len(hangul)), ("복습 회차", 4)],
            "groups": hangul,
        },
        {
            "id": "2-core-patterns", "no": 2, "ko": "핵심 문법 패턴", "en": "Core Patterns",
            "glyph": "文", "status": "live", "accent": "#2b5fd9", "tint": "#eef2fd",
            "unitWord": "단원", "lessonWord": "과",
            "desc": "커리큘럼의 척추. 1과 = 할 수 있는 것 1개 + 패턴 2개. "
                    "명사 문장에서 시작해 피동·사동, 그리고 고급 어미까지 23개 단원으로 쌓아 올립니다.",
            "note": "해요체를 먼저 세우고 격식체는 24과에서 대응표로, 반말(43–45)과 높임말(46–48)로 정중함의 양끝을 채웁니다.",
            "stats": [("과", sum(len(g["lessons"]) for g in core)), ("단원", len(core)),
                      ("패턴", core_patterns)],
            # 완성 덱은 이제 코스 밑에 산다 — tools/plan_courses.py 가 트랙을
            # 코스로 끊은 뒤로 경로가 courses/<코스>/lessons/<슬러그>/lesson.html 이다.
            "groups": core,
        },
        {
            "id": "3-contextual-korean", "no": 3, "ko": "상황별 한국어", "en": "Contextual Korean",
            "glyph": "劇", "status": "live", "accent": "#c22a5f", "tint": "#fdeff3",
            "unitWord": "코스", "lessonWord": "레슨",
            "desc": "한국어를 배우러 오는 사람은 없습니다 — 드라마를 자막 없이 보고 싶어서 옵니다. "
                    "네 커리큘럼의 14개 코스는 각각 등장인물과 이야기가 있는 한 편의 작품입니다.",
            "note": "패턴마다 핵심 트랙의 과 번호가 붙습니다. 그 숫자는 문(gate)이 아니라 참고이고, "
                    "실제 조건은 코스마다 하나씩인 입장 바닥입니다.",
            "stats": [("레슨", ctx_lessons), ("코스", len(ctx)), ("커리큘럼", 4)],
            "groups": ctx,
        },
        {
            "id": "4-freetalking", "no": 4, "ko": "중급·고급 프리토킹", "en": "Intermediate & Advanced Freetalking",
            "glyph": "話", "status": "open", "accent": "#0080a8", "tint": "#e9f6fa",
            "unitWord": "테마", "unitCount": free_themes, "lessonWord": "레슨",
            "desc": "같은 말이 나오는 주제를 중급과 고급 두 버전으로 제공합니다. 고급을 먼저 쓰고, 중급은 지문과 어려운 질문의 한국어 부담만 낮춥니다. "
                    "끝이 없는 트랙이라 주제는 매주 늘어납니다.",
            "note": "한 세션은 25분입니다. 질문 여덟 개는 완료 목록이 아니라 넉넉한 콘텐츠 풀이라, 빠르면 전부 쓰고 천천히 길게 말하면 일부만 진행합니다.",
            "stats": [("주제", free_topics), ("레벨", 2), ("레슨", free_topics * 2),
                      ("워밍업", free_warmups)],
            "totalMultiplier": 2,
            "groups": free,
        },
        {
            "id": "5-pronunciation", "no": 5, "ko": "발음 교정", "en": "Pronunciation",
            "glyph": "音", "status": "plan", "accent": "#69737d", "tint": "#f4f5f7",
            "unitWord": "부", "lessonWord": "레슨",
            "desc": "일본어 화자의 한국어를 어색하게 만드는 지점만 골라 고칩니다. 일반적인 발음 강의가 아니라, "
                    "일본어에 한 칸뿐인 자리에 한국어가 두세 칸을 두는 곳의 목록입니다.",
            "note": "계획만 있고 현재 개발하지 않습니다. 레슨 덱 제작도 승인되지 않았습니다. "
                    "개발을 시작한다면 각 레슨은 서로 독립적으로 사용할 수 있습니다.",
            "stats": [("레슨", sum(len(g["lessons"]) for g in pron)), ("부", len(pron)),
                      ("상태", "계획")],
            "groups": pron,
        },
    ]

    for t in tracks:
        t["stats"] = [{"k": k, "v": v} for k, v in t["stats"]]
        t["dist"] = count_by_level(t["groups"])
        spans = [lv for g in t["groups"]
                 for lv in (g.get("levels") or level_span(g.get("levelText") or g.get("level") or ""))
                 if g.get("levels") or g.get("levelText") or g.get("level")]
        t["span"] = [lv for lv in LEVELS if lv in spans]
        t["total"] = (sum(len(g["lessons"]) for g in t["groups"] if not g.get("warmup"))
                      * t.get("totalMultiplier", 1))
        t["decks"] = attach_decks(t["id"], t["groups"])
        mark_first_lesson(t["groups"])

    totals = {
        "tracks": len(tracks),
        "lessons": sum(t["total"] for t in tracks),
        "units": sum(len(t["groups"]) for t in tracks if True) - 1,   # 워밍업 은행은 단원이 아니다
        "patterns": core_patterns,
        "decks": sum(len(t["decks"]) for t in tracks),
    }
    return {"levels": LEVELS, "tracks": tracks, "totals": totals}


def render(template: str, data: dict, out: Path) -> None:
    tpl = (Path(__file__).parent / template).read_text(encoding="utf-8")
    out.write_text(tpl.replace("/*__DATA__*/null",
                               json.dumps(data, ensure_ascii=False, separators=(",", ":"))),
                   encoding="utf-8")


def main() -> None:
    data = build()
    OUT_DIR.mkdir(exist_ok=True)

    # 관문에는 트랙의 겉면만 싣는다 — 과 목록은 각자의 페이지가 들고 있다
    nav = [{"id": t["id"], "no": t["no"], "ko": t["ko"], "accent": t["accent"],
            "total": t["total"], "lessonWord": t["lessonWord"],
            "decks": len(t["decks"])} for t in data["tracks"]]
    summary = [{k: v for k, v in t.items() if k != "groups"} for t in data["tracks"]]
    render("gateway_template.html",
           {"levels": data["levels"], "totals": data["totals"], "tracks": summary}, OUT)

    for t in data["tracks"]:
        render("track_template.html", {"levels": data["levels"], "track": t, "nav": nav},
               OUT_DIR / f"{t['id']}.html")

    print(f"→ {OUT.relative_to(ROOT.parent)}  +  {OUT_DIR.relative_to(ROOT.parent)}/*.html")
    for t in data["tracks"]:
        made = f" · 완성 덱 {len(t['decks'])}" if t["decks"] else ""
        print(f"   {t['no']}. {t['ko']:<10} {t['total']:>4} {t['lessonWord']} · "
              f"{t.get('unitCount', len(t['groups']))} {t['unitWord']} · "
              f"{' '.join(t['span']) or '전 레벨'}{made}")
    print(f"   합계 {data['totals']['lessons']} 레슨 · {data['totals']['units']} 단원 · "
          f"{data['totals']['patterns']} 패턴 · 완성 덱 {data['totals']['decks']}")


if __name__ == "__main__":
    main()
