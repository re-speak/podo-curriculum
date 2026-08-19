#!/usr/bin/env python3
"""Split a track's table-of-contents.md into one brief per lesson.

The monolithic TOC is the source of truth and stays that way — these shards are
generated, never hand-edited. Re-run after any TOC change:

    python3 tools/authoring/kr/shard_toc.py sandbox/drafts/kr/tracks/2-core-patterns

Why this exists: writing 과 7 needs about 15 lines of that file, but an agent
that opens the whole thing pays ~35k tokens and still has to *infer* what the
learner already knows. Each brief states that instead, so the constraint is read
rather than derived.

A brief carries four things:
  이 과            what this lesson teaches
  이 단원          the unit's framing + the checkpoint it builds toward
  이미 배운 것     cumulative ledger — recent lessons with glosses, older ones compact
  아직 아님        the next few lessons, so the writer doesn't preempt them
"""

import re
import sys
from pathlib import Path

# how much history gets full glosses before collapsing to a compact list
DETAIL_UNITS = 2
# how far ahead "아직 아님" looks
LOOKAHEAD = 6

UNIT_RE = re.compile(r"^## Unit (\d+) · (.+?) · (\d+)과 · \*\*(.+?)\*\*\s*$")
LESSON_RE = re.compile(r"^\*\*(\d+)\. (.+?)\*\*\s*$")
CHECKPOINT_RE = re.compile(r"^\*▸ 체크포인트 .*?· 수행: (.+?)\*\s*$")
SUMMARY_RE = re.compile(r"^\*정리: (.+?)\*\s*$")
CAN_DO_RE = re.compile(r"^\*할 수 있는 것: (.+?)\*\s*$")
EXPR_RE = re.compile(r"^- \*표현:\* (.+?)\s*$")
GRAMMAR_RE = re.compile(r"^- \*문법:\* (.+?)\s*$")
# `- 저는 다나카예요. — `N이에요/예요` (명사 서술형)` is the common shape, but the
# gloss is optional and the backticks wrap only part of the form in the numbers
# unit (`- 삼천 원이에요. — 한자어 숫자 + `원` (가격)`). Capture loosely, then
# peel the trailing parenthetical off. The (?!\*) keeps 표현/문법 lines out.
PATTERN_RE = re.compile(r"^- (?!\*)(.+?) [—–] (.+?)\s*$")
GLOSS_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)$")


def parse(toc_path):
    """Walk the TOC once and return its units, each holding its lessons."""
    lines = toc_path.read_text(encoding="utf-8").splitlines()

    # everything before the first `# Part` heading is front matter whose bold
    # numbered lines ("**1. 구어 빈도 점검…**") look exactly like lesson headers
    start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("# Part ")), 0
    )

    units, unit, lesson = [], None, None
    for raw in lines[start:]:
        line = raw.rstrip()

        m = UNIT_RE.match(line)
        if m:
            unit = {
                "no": int(m.group(1)),
                "title": m.group(2),
                "count": int(m.group(3)),
                "level": m.group(4),
                "framing": None,
                "checkpoint": None,
                "summary": None,
                "lessons": [],
            }
            units.append(unit)
            lesson = None
            continue

        if unit is None:
            continue

        m = LESSON_RE.match(line)
        if m:
            lesson = {
                "no": int(m.group(1)),
                "title": m.group(2),
                "can_do": None,
                "patterns": [],
                "expressions": None,
                "grammar": None,
                "unit": unit,
            }
            unit["lessons"].append(lesson)
            continue

        m = CHECKPOINT_RE.match(line)
        if m:
            unit["checkpoint"] = m.group(1)
            lesson = None
            continue

        m = SUMMARY_RE.match(line)
        if m:
            unit["summary"] = m.group(1)
            continue

        if lesson is not None:
            m = CAN_DO_RE.match(line)
            if m:
                lesson["can_do"] = m.group(1)
                continue
            m = EXPR_RE.match(line)
            if m:
                lesson["expressions"] = m.group(1)
                continue
            m = GRAMMAR_RE.match(line)
            if m:
                lesson["grammar"] = m.group(1)
                continue
            m = PATTERN_RE.match(line)
            if m:
                example, rest = m.group(1), m.group(2)
                g = GLOSS_RE.match(rest)
                form, gloss = (g.group(1), g.group(2)) if g else (rest, None)
                # backticks may wrap all, part, or none of the form — normalise
                # so rendering can add exactly one pair back
                form = form.replace("`", "").strip()
                lesson["patterns"].append(
                    {"example": example, "form": form, "gloss": gloss}
                )
                continue
        elif unit["framing"] is None and line.startswith("*") and line.endswith("*"):
            # the italic line right under a unit header is its framing note
            unit["framing"] = line.strip("*")

    return units


def ledger(prior, current_unit_no):
    """Render 이미 배운 것 — recent units in full, older ones compacted.

    Late lessons inherit 100+ patterns. Printing every gloss would rebuild the
    problem this script exists to solve, so only the reuse zone (the last couple
    of units, where precision actually changes the writing) keeps its glosses.
    """
    if not prior:
        return "*아직 없음 — 이 트랙의 첫 과다.*"

    recent_cut = current_unit_no - DETAIL_UNITS
    older = [l for l in prior if l["unit"]["no"] <= recent_cut]
    recent = [l for l in prior if l["unit"]["no"] > recent_cut]

    out = []

    if older:
        out.append(f"### 과 {older[0]['no']}–{older[-1]['no']} · 패턴만")
        out.append("")
        by_unit = {}
        for l in older:
            by_unit.setdefault(l["unit"]["no"], []).append(l)
        for uno in sorted(by_unit):
            forms = [
                f"`{p['form']}`"
                for l in by_unit[uno]
                for p in l["patterns"]
            ]
            out.append(f"- **U{uno}** — " + " · ".join(forms))
        out.append("")

    if recent:
        out.append(f"### 과 {recent[0]['no']}–{recent[-1]['no']} · 직전 구간 (자세히)")
        out.append("")
        for l in recent:
            out.append(f"**{l['no']}. {l['title']}**")
            for p in l["patterns"]:
                gloss = f"{p['gloss']} — " if p["gloss"] else ""
                out.append(f"- `{p['form']}` — {gloss}예: {p['example']}")
            if l["expressions"]:
                out.append(f"- *표현:* {l['expressions']}")
            out.append("")

    return "\n".join(out).rstrip()


def render(lesson, prior, upcoming, track_name):
    u = lesson["unit"]
    L = []

    L.append(f"# 과 {lesson['no']} · {lesson['title']}")
    L.append("")
    L.append(
        f"`{track_name}` · Unit {u['no']} · **{u['level']}** · "
        f"생성 파일 — 고치지 말 것, 원본은 `../table-of-contents.md`"
    )
    L.append("")

    L.append("## 이 과에서 만드는 것")
    L.append("")
    if lesson["can_do"]:
        L.append(f"**할 수 있는 것:** {lesson['can_do']}")
        L.append("")
    L.append("**패턴 (발화 목표 — 모범 문장 없이 만들어 말할 수 있어야 한다)**")
    L.append("")
    for p in lesson["patterns"]:
        tail = f" ({p['gloss']})" if p["gloss"] else ""
        L.append(f"- {p['example']} — `{p['form']}`{tail}")
    L.append("")
    if lesson["expressions"]:
        L.append(f"**표현 (발화 — 문장에 끼워 쓸 수 있으면 된다):** {lesson['expressions']}")
        L.append("")
    if lesson["grammar"]:
        L.append(f"**문법 (이해만 — 세 번째 학습 목표가 아니다):** {lesson['grammar']}")
        L.append("")

    L.append(f"## 이 단원 · Unit {u['no']} · {u['title']}")
    L.append("")
    if u["framing"]:
        L.append(f"*{u['framing']}*")
        L.append("")
    if u["checkpoint"]:
        L.append(f"**단원 끝 수행 과제:** {u['checkpoint']}")
        L.append("")
    if u["summary"]:
        L.append(f"**정리:** {u['summary']}")
        L.append("")

    L.append("## 이미 배운 것")
    L.append("")
    L.append(
        "학습자가 여기까지 이미 쓸 수 있는 것. 다시 설명하지 말고, "
        "예문·대화·연습에 자유롭게 섞어 쓴다."
    )
    L.append("")
    L.append(ledger(prior, u["no"]))
    L.append("")

    L.append("## 아직 아님")
    L.append("")
    if upcoming:
        L.append("이 과에서 미리 쓰면 안 되는 것 — 뒤에서 가르친다.")
        L.append("")
        for l in upcoming:
            forms = " · ".join(f"`{p['form']}`" for p in l["patterns"])
            L.append(f"- **과 {l['no']}** {l['title']} — {forms}")
    else:
        L.append("*트랙의 마지막 구간 — 아껴 둘 것이 없다.*")
    L.append("")

    return "\n".join(L)


def main():
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <track-dir>")

    track = Path(sys.argv[1])
    toc = track / "table-of-contents.md"
    if not toc.exists():
        sys.exit(f"no table-of-contents.md in {track}")

    units = parse(toc)
    lessons = [l for u in units for l in u["lessons"]]
    if not lessons:
        sys.exit(f"parsed 0 lessons from {toc} — the format changed, fix the regexes")

    # A lesson is defined as one 할 수 있는 것 plus the patterns that achieve it, so
    # either field coming back empty means a line shape slipped past the regexes.
    # This has to be loud: a brief that silently loses its patterns still renders,
    # and the lesson written from it would just be quietly wrong.
    broken = [
        f"과 {l['no']} ({l['title']}): "
        + ", ".join(
            n for n, ok in (("패턴 없음", l["patterns"]), ("할 수 있는 것 없음", l["can_do"])) if not ok
        )
        for l in lessons
        if not l["patterns"] or not l["can_do"]
    ]
    if broken:
        sys.exit(
            "TOC parse incomplete — fix the regexes before trusting these briefs:\n  "
            + "\n  ".join(broken)
        )

    out_dir = track / "toc"
    out_dir.mkdir(exist_ok=True)
    for stale in out_dir.glob("*.md"):
        stale.unlink()

    for i, lesson in enumerate(lessons):
        body = render(
            lesson,
            prior=lessons[:i],
            upcoming=lessons[i + 1 : i + 1 + LOOKAHEAD],
            track_name=track.name,
        )
        (out_dir / f"lesson-{lesson['no']:03d}.md").write_text(body, encoding="utf-8")

    index = ["# 과 목록", "", f"`{track.name}` · {len(lessons)}과 · {len(units)}단원.",
             "생성 파일 — 고치지 말 것. 원본은 `table-of-contents.md`,",
             "다시 만들려면 `python3 tools/authoring/kr/shard_toc.py sandbox/drafts/kr/tracks/" + track.name + "`.",
             "",
             "한 과를 쓸 때는 그 과의 브리프 하나만 읽으면 된다. "
             "이미 배운 것과 아직 아닌 것이 브리프 안에 들어 있다.", ""]
    for u in units:
        index.append(f"## Unit {u['no']} · {u['title']} · **{u['level']}**")
        index.append("")
        for l in u["lessons"]:
            index.append(
                f"- [`{l['no']}`](toc/lesson-{l['no']:03d}.md) {l['title']}"
            )
        index.append("")
    (track / "toc" / "index.md").write_text("\n".join(index), encoding="utf-8")

    sizes = [len((out_dir / f"lesson-{l['no']:03d}.md").read_text(encoding="utf-8")) for l in lessons]
    print(f"{len(lessons)} briefs from {len(units)} units -> {out_dir}")
    print(f"  toc source : {toc.stat().st_size:,} bytes")
    print(f"  brief size : min {min(sizes):,} / median {sorted(sizes)[len(sizes)//2]:,} / max {max(sizes):,} bytes")


if __name__ == "__main__":
    main()
