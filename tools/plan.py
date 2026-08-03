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

CREATE, UPDATE, NOOP, BLOCKED = "create", "update", "noop", "blocked"


def plan(env: str) -> list[dict]:
    state = model.load_state(env).get("courses", {})
    actions: list[dict] = []

    for course in model.discover():
        tracked = state.get(course.key)
        actions.append({
            "action": CREATE if tracked is None else UPDATE,
            "target": "course",
            "key": course.key,
            "detail": (f"COVER row · {course.lang_type} · {course.spec['curriculumType']} · "
                       f"level {course.spec['classLevel']} · USE_YN="
                       f"{'Y' if course.spec.get('enabled') else 'N'}"),
            "rowId": (tracked or {}).get("coverId"),
        })

        tracked_lessons = (tracked or {}).get("lessons", {}) or {}
        for lesson in course.lessons:
            known = tracked_lessons.get(lesson.slug, {})
            digests = known.get("digest", {}) or {}
            row_id = known.get("courseRowId")

            for slot in sorted(lesson.decks):
                deck = lesson.decks[slot]
                key = f"{course.key}/{lesson.slug}/{slot}"

                if not deck.exists:
                    actions.append({
                        "action": BLOCKED, "target": "deck", "key": key,
                        "detail": "no deck on disk — the lesson cannot deploy until both slots exist",
                        "rowId": row_id,
                    })
                    continue

                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        _, digest = build.package(deck.entry, pathlib.Path(tmp), quiet=True)
                    except build.BuildError as exc:
                        actions.append({
                            "action": BLOCKED, "target": "deck", "key": key,
                            "detail": f"does not package: {str(exc).splitlines()[0]}",
                            "rowId": row_id,
                        })
                        continue

                if digests.get(slot) == digest:
                    actions.append({
                        "action": NOOP, "target": "deck", "key": key,
                        "detail": "content unchanged — S3 untouched", "rowId": row_id,
                    })
                elif row_id is None:
                    actions.append({
                        "action": CREATE, "target": "deck", "key": key,
                        "detail": (f"new MAIN row (CLASS_WEEK={lesson.week}) → upload to "
                                   f"lemonboard-html/<new id>/{slot}.html, create HTML room"),
                        "rowId": None,
                    })
                else:
                    actions.append({
                        "action": UPDATE, "target": "deck", "key": key,
                        "detail": (f"overwrite lemonboard-html/{row_id}/{slot}.html "
                                   f"(room key unchanged)"),
                        "rowId": row_id,
                    })
    return actions


SYMBOL = {CREATE: "+", UPDATE: "~", NOOP: " ", BLOCKED: "!"}


def render(actions: list[dict]) -> str:
    if not actions:
        return "No courses under courses/. Nothing to do."

    lines = ["```", f"{'':2}{'target':<46} {'action':<8} what happens", "-" * 100]
    for a in actions:
        lines.append(f"{SYMBOL[a['action']]:<2}{a['key']:<46} {a['action']:<8} {a['detail']}")
    lines.append("```")

    counts = {k: sum(1 for a in actions if a["action"] == k) for k in (CREATE, UPDATE, NOOP, BLOCKED)}
    lines.append("")
    lines.append(f"**{counts[CREATE]} to create · {counts[UPDATE]} to update · "
                 f"{counts[NOOP]} unchanged · {counts[BLOCKED]} blocked**")
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
