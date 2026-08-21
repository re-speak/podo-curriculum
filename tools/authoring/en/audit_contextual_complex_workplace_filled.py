#!/usr/bin/env python3
"""Run the CTX25-36 Orca layout probe with every activity visibly filled."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys

import audit_rendered_decks


ROOT = pathlib.Path(__file__).resolve().parents[3]
COURSES = (
    ROOT / "sandbox/drafts/en/tracks/2-contextual-english/courses/ctx-travel-complex-decisions",
    ROOT / "sandbox/drafts/en/tracks/2-contextual-english/courses/ctx-business-workplace-essentials",
)


def orca(*arguments: str) -> dict:
    command = shutil.which("orca")
    if not command:
        raise SystemExit("orca CLI is not available")
    run = subprocess.run([command, *arguments, "--json"], cwd=ROOT, text=True, capture_output=True, check=False)
    if run.returncode:
        raise SystemExit(run.stderr or run.stdout)
    if not run.stdout.strip():
        raise SystemExit("orca returned empty output; browser runtime is not ready")
    return json.loads(run.stdout)


def filled_probe() -> str:
    layout_probe = audit_rendered_decks.probe_expression()
    return f"""(() => {{
      document.querySelectorAll('input:not([type=range]), textarea').forEach((field, index) => {{
        field.value = field.dataset.answer || `A realistic complete answer ${{index + 1}} that wraps onto another line when the phone is narrow.`;
        field.dispatchEvent(new Event('input', {{bubbles: true}}));
      }});
      document.querySelectorAll('[data-sync-option]').forEach(option => option.classList.add('chosen'));
      document.querySelectorAll('.build-zone[data-a]').forEach(zone => {{
        zone.textContent = zone.dataset.a;
        zone.classList.add('filled');
      }});
      return ({layout_probe});
    }})()"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True, help="Dedicated Orca browserPageId")
    args = parser.parse_args()
    decks = sorted(path for course in COURSES for path in course.glob("lessons/*/lesson.html"))
    failures = []
    for index, deck in enumerate(decks, 1):
        orca("goto", "--page", args.page, "--url", deck.as_uri())
        orca("snapshot", "--page", args.page)
        response = orca("eval", "--page", args.page, "--expression", filled_probe())["result"]["result"]
        issues = json.loads(response) if isinstance(response, str) else response
        issues = [
            issue for issue in issues
            if issue["spacing"] or any(
                not str(name).startswith(("space-input", "free-input", "pg-scrub"))
                for name in issue["overflow"]
            )
        ]
        if issues:
            failures.append((deck, issues))
            print(f"FAIL {deck.relative_to(ROOT)}: {json.dumps(issues, ensure_ascii=False)}")
        else:
            print(f"ok filled {index}/{len(decks)} {deck.relative_to(ROOT)}")
    print(f"{len(decks)} filled deck(s) rendered · {len(failures)} failing deck(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
