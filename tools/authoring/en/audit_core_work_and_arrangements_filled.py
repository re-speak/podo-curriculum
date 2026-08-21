#!/usr/bin/env python3
"""Run the CORE71--80 Orca layout probe with every editable field filled."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys

import audit_rendered_decks


ROOT = pathlib.Path(__file__).resolve().parents[3]
COURSE = ROOT / "sandbox/drafts/en/tracks/1-core-patterns/courses/core-work-and-arrangements"


def orca(*arguments: str) -> dict:
    command = shutil.which("orca")
    if not command:
        raise SystemExit("orca CLI is not available")
    run = subprocess.run([command, *arguments, "--json"], cwd=ROOT, text=True, capture_output=True, check=False)
    if run.returncode:
        raise SystemExit(run.stderr or run.stdout)
    return json.loads(run.stdout)


def filled_probe() -> str:
    layout_probe = audit_rendered_decks.probe_expression()
    return f"""(() => {{
      document.querySelectorAll('input, textarea').forEach((field, index) => {{
        field.value = field.dataset.answer || `A complete realistic learner answer ${{index + 1}} with enough words to wrap naturally.`;
        field.dispatchEvent(new Event('input', {{bubbles: true}}));
        field.dispatchEvent(new Event('change', {{bubbles: true}}));
      }});
      return ({layout_probe});
    }})()"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", required=True, help="Dedicated Orca browserPageId")
    args = parser.parse_args()
    failures = []
    decks = sorted(COURSE.glob("lessons/*/lesson.html"))
    for index, deck in enumerate(decks, 1):
        orca("goto", "--page", args.page, "--url", deck.as_uri())
        orca("snapshot", "--page", args.page)
        response = orca("eval", "--page", args.page, "--expression", filled_probe())["result"]["result"]
        issues = json.loads(response) if isinstance(response, str) else response
        # A one-line input scrolls its own text by design. That intrinsic
        # scrollWidth is not page/container overflow; retain every spacing or
        # non-control overflow finding from the canonical probe.
        issues = [
            issue for issue in issues
            if issue["spacing"] or any(
                not str(name).startswith(("slot-input", "space-input", "free-input"))
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
