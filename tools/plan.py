#!/usr/bin/env python3
"""
What would `apply` do? Read-only; touches nothing.

CI posts this as a PR comment, the way podo-database-schema comments the ALTER
it is about to run. The point is that a curriculum change is reviewable as a
list of effects, not as a diff of HTML.

    python3 tools/plan.py --env stage [--json]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

import build
import model

# state lock 이 없어진 뒤로 create 와 update 를 여기서 가를 수 없다. 그 판정은 grape 가
# 자연키로 하고, 그걸 미리 알려면 grape 에 물어봐야 한다 — plan 이 DB 를 조회하기 시작하면
# "적용하지 않고 볼 수 있는 것"이라는 성질을 잃는다. 그래서 apply 하나로 합쳤다.
APPLY, BLOCKED = "apply", "blocked"


def plan(env: str) -> list[dict]:
    actions: list[dict] = []

    for course in model.discover():
        actions.append({
            "action": APPLY,
            "target": "course",
            "key": course.key,
            "detail": (f"COVER row · {course.lang_type} · {course.spec['curriculumType']} · "
                       f"level {course.spec['classLevel']} · USE_YN="
                       f"{'Y' if course.spec.get('enabled') else 'N'}"),
        })

        for lesson in course.lessons:
            for slot in sorted(lesson.decks):
                deck = lesson.decks[slot]
                key = f"{course.key}/{lesson.slug}/{slot}"

                if not deck.exists:
                    actions.append({
                        "action": BLOCKED, "target": "deck", "key": key,
                        "detail": "no deck on disk — the lesson cannot deploy until both slots exist",
                    })
                    continue

                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        _, digest = build.package(deck.entry, pathlib.Path(tmp), quiet=True)
                    except build.BuildError as exc:
                        actions.append({
                            "action": BLOCKED, "target": "deck", "key": key,
                            "detail": f"does not package: {str(exc).splitlines()[0]}",
                        })
                        continue

                actions.append({
                    "action": APPLY, "target": "deck", "key": key,
                    "detail": (f"MAIN row (CLASS_WEEK={lesson.week}) → upload deck, "
                               f"ensure HTML room  [{digest[:19]}]"),
                })
    return actions


SYMBOL = {APPLY: "~", BLOCKED: "!"}


def render(actions: list[dict]) -> str:
    if not actions:
        return "No courses under courses/. Nothing to do."

    lines = ["```", f"{'':2}{'target':<46} {'action':<8} what happens", "-" * 100]
    for a in actions:
        lines.append(f"{SYMBOL[a['action']]:<2}{a['key']:<46} {a['action']:<8} {a['detail']}")
    lines.append("```")

    counts = {k: sum(1 for a in actions if a["action"] == k) for k in (APPLY, BLOCKED)}
    lines.append("")
    lines.append(f"**{counts[APPLY]} to apply · {counts[BLOCKED]} blocked**")
    if counts[BLOCKED]:
        lines.append("")
        lines.append("> Blocked items are skipped by apply, not fixed by it. "
                     "The rest of the plan still runs.")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", default="stage")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        actions = plan(args.env)
    except model.ValidationError as exc:
        sys.exit(f"✗ {exc}")
    print(json.dumps(actions, indent=2, ensure_ascii=False) if args.json else render(actions))
