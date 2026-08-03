#!/usr/bin/env python3
"""
The PR gate. Everything that could break a live lesson, checked before merge.

Four layers, cheapest first:

  1. schema      — course.yaml / lesson.yaml against JSON Schema
  2. structure   — slugs match directories, weeks run 1..N, both deck slots present
  3. package     — every deck actually builds, with the S3-flattening audit
  4. contract    — the built HTML through lemonboard's own data-sync validator

Layer 4 needs network and is skipped without --contract, because the contract is
owned by lemonboard and grape calls the same endpoint at upload time. Running it
here just moves the failure from "someone tried to deploy" to "someone opened a PR".

    python3 tools/validate.py [--contract] [--env stage]
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile
import urllib.error
import urllib.request

import build
import model

LEMONBOARD_KEY_ENV = "PODO_LEMONBOARD_API_KEY"


def _fail(message: str) -> int:
    print(f"\u2717 {message}")
    return 1


def check_deck_slots(course: model.Course) -> list[str]:
    """Both slots must exist on disk before a lesson can ship.

    A missing prestudy deck leaves PRESTUDY_LEMONBOARD_KEY empty, and class
    creation in podo-backend then duplicates /rooms/null/ and fails. Grape blocks
    the upload for exactly this reason; we block the merge instead.
    """
    problems = []
    for lesson in course.lessons:
        for slot in lesson.incomplete:
            problems.append(
                f"{model._rel(lesson.root)}: {slot} deck declared but "
                f"{lesson.spec['decks'][slot]['entry']} is not on disk"
            )
    return problems


def check_enabled_is_earned(course: model.Course) -> list[str]:
    """A course cannot be USE_YN='Y' while any lesson is unfinished."""
    if not course.spec.get("enabled"):
        return []
    if not course.lessons:
        return [f"{course.key}: enabled: true but the course has no lessons"]
    holes = course.incomplete
    if holes:
        names = ", ".join(l.slug for l in holes)
        return [f"{course.key}: enabled: true but these lessons are missing a deck — {names}"]
    return []


def check_no_orphan_rename(courses: list[model.Course], env: str) -> list[str]:
    """A slug in state but gone from the repo means a rename or a deletion.

    Either way the live course is now unreachable from the repo, and the next
    apply would create a duplicate rather than update it. Both are recoverable,
    but only deliberately — so stop and make someone say which it was.
    """
    state = model.load_state(env)
    known = {c.key for c in courses}
    orphans = [k for k in state.get("courses", {}) if k not in known]
    return [
        f"state/{env}.lock.yaml still tracks '{k}' but no such course exists in the repo — "
        f"rename the state entry to match, or remove it deliberately if the course is retired"
        for k in orphans
    ]


def validate_contract(html: str, api: str, label: str, key: str) -> list[str]:
    """Run the built HTML through lemonboard's data-sync contract validator.

    Fail-open on network trouble and 5xx, matching grape's own behaviour
    (class_course_ps.php:342) — an unavailable validator must not block work.
    A 4xx verdict is a real contract violation and does block.

    A response without an `ok` field is treated as a hard failure, not as a pass.
    Grape fail-opens there, but grape is authenticated and interactive; here the
    same case is almost always a bad token, and silently passing would mean the
    contract gate stops running with nobody noticing — which is the exact failure
    mode this repo exists to prevent.
    """
    url = api.rstrip("/") + "/api/v1/lesson-html/validate"
    req = urllib.request.Request(
        url,
        data=json.dumps({"html": html}).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            print(f"  ~ {label}: contract validator unavailable ({exc.code}) — skipped")
            return []
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return [f"{label}: contract validator rejected the request ({exc.code})"]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  ~ {label}: contract validator unreachable ({exc}) — skipped")
        return []

    if payload.get("ok") is True:
        return []

    if "ok" not in payload:
        detail = payload.get("message") or payload.get("code") or json.dumps(payload)[:200]
        return [f"{label}: contract validator did not return a verdict — {detail}"]

    problems = []
    for issue in payload.get("issues", []):
        text = issue.get("message", "unknown contract violation")
        where = issue.get("syncId") or issue.get("rule") or ""
        if issue.get("severity", "error") == "error":
            problems.append(f"{label}: {text}" + (f"  [{where}]" if where else ""))
        else:
            print(f"  ~ {label}: warning — {text}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--contract", action="store_true",
                    help="also run each built deck through lemonboard's validator (needs network)")
    ap.add_argument("--env", default="stage", help="which state lock to check against")
    args = ap.parse_args()

    curriculum = model.load_curriculum()
    api = curriculum["spec"]["environments"][args.env]["lemonboardApi"]

    # The validator is authenticated (grape sends the same bearer key from
    # $conf_{dev,prod}_lemonboard_key). Asking for --contract without one would
    # otherwise "pass" every deck on an auth rejection, so refuse up front.
    key = os.environ.get(LEMONBOARD_KEY_ENV, "")
    if args.contract and not key:
        return _fail(f"--contract needs {LEMONBOARD_KEY_ENV} "
                     f"(the lemonboard API key for {args.env}); "
                     f"drop --contract to run every other check")

    try:
        courses = model.discover()
    except model.ValidationError as exc:
        print(f"✗ {exc}")
        return 1

    if not courses:
        print("no courses found under courses/ — nothing to validate")
        return 0

    problems: list[str] = []
    problems += check_no_orphan_rename(courses, args.env)

    for course in courses:
        print(f"\n{course.key}  ({course.lang_type} · {course.spec['curriculumType']} · "
              f"level {course.spec['classLevel']} · {len(course.lessons)} lesson(s))")
        problems += check_deck_slots(course)
        problems += check_enabled_is_earned(course)

        for lesson in course.lessons:
            for slot, deck in sorted(lesson.decks.items()):
                label = f"{course.key}/{lesson.slug}/{slot}"
                if not deck.exists:
                    print(f"  · {slot:<8} — no deck yet")
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        _, digest = build.package(deck.entry, pathlib.Path(tmp), quiet=True)
                    except build.BuildError as exc:
                        problems.append(f"{label}: {exc}")
                        print(f"  ✗ {slot:<8} — build failed")
                        continue
                    print(f"  ✓ {slot:<8} — {digest[7:19]}")
                    if args.contract:
                        problems += validate_contract(
                            (pathlib.Path(tmp) / build.HTML_NAME).read_text(encoding="utf-8"),
                            api, label, key,
                        )

    print()
    if problems:
        print(f"✗ {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  • {p}")
        return 1

    incomplete = sum(len(c.incomplete) for c in courses)
    if incomplete:
        print(f"✓ valid — but {incomplete} lesson(s) still missing a deck, so they will not deploy")
    else:
        print("✓ valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
