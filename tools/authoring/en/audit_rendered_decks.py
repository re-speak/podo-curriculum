#!/usr/bin/env python3
"""Audit every page of English decks in Orca at the supported phone widths.

The static checker cannot see CSS overflow. This script deliberately uses the
Orca embedded browser, navigates one existing worktree tab, snapshots after
every navigation, and measures every page with paged mode genuinely active.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_ROOT = ROOT / "sandbox/drafts/en/tracks"
PHONE_WIDTHS = (360, 480)
MIN_VIEWPORT_HEIGHT = 800


def orca(*arguments: str) -> dict:
    command = shutil.which("orca")
    if not command:
        raise SystemExit("orca CLI is not available")
    run = subprocess.run(
        [command, *arguments, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if run.returncode:
        raise SystemExit(run.stderr or run.stdout)
    return json.loads(run.stdout)


def active_page() -> str:
    tabs = orca("tab", "list")["result"]["tabs"]
    local = [tab for tab in tabs if str(ROOT) in tab.get("worktreeId", "")]
    candidates = [tab for tab in local if tab.get("active")] or local
    if not candidates:
        raise SystemExit("Open an Orca browser tab for this worktree, or pass --page.")
    return candidates[0]["browserPageId"]


def probe_expression() -> str:
    widths = json.dumps(PHONE_WIDTHS)
    return f"""(() => {{
      const phone = document.querySelector('.phone');
      if (!phone) return [{{page: 'document', reason: 'missing .phone'}}];
      const pages = [...phone.children].filter(p => p.hasAttribute('data-page-id'));
      const was = phone.querySelector('.pg-on');
      const styles = getComputedStyle(document.documentElement);
      const expectedClearance = parseFloat(styles.getPropertyValue('--pager-clearance'));
      const bad = [];
      for (const width of {widths}) {{
        phone.style.width = width + 'px';
        for (const page of pages) {{
          pages.forEach(candidate => candidate.classList.toggle('pg-on', candidate === page));
          const overflow = [page, ...page.querySelectorAll('*')]
            .filter(element => element.scrollWidth > element.clientWidth + 1);
          const spacing = [];
          const checkSiblings = (elements, label, minimum) => {{
            for (let index = 1; index < elements.length; index++) {{
              const previous = elements[index - 1].getBoundingClientRect();
              const current = elements[index].getBoundingClientRect();
              const gap = current.top - previous.bottom;
              if (current.top > previous.top + 1 && gap < minimum) {{
                spacing.push({{label, gap: Math.round(gap * 10) / 10}});
              }}
            }}
          }};
          page.querySelectorAll('.model-list').forEach(list =>
            checkSiblings([...list.children].filter(row => row.classList.contains('model-line')),
                          'model-line', 8));
          page.querySelectorAll('.dialogue').forEach(dialogue =>
            checkSiblings([...dialogue.children].filter(turn => turn.classList.contains('turn')),
                          'dialogue-turn', 12));
          page.querySelectorAll('.answer-fill .korean').forEach(line =>
            checkSiblings([...line.querySelectorAll('.slot-input, .phrase-input')],
                          'inline-answer-input', 8));
          const previousMinHeight = page.style.minHeight;
          page.style.minHeight = '0px';
          const rect = page.getBoundingClientRect();
          const required = rect.height + rect.top + scrollY;
          const clearance = parseFloat(getComputedStyle(page).paddingBottom) || 0;
          page.style.minHeight = previousMinHeight;
          if (overflow.length || spacing.length ||
              (required > {MIN_VIEWPORT_HEIGHT} - expectedClearance &&
               clearance < expectedClearance)) {{
            bad.push({{
              width,
              page: page.dataset.pageId,
              overflow: overflow.slice(0, 3).map(element => element.className),
              spacing: spacing.slice(0, 3),
              clearance,
            }});
          }}
        }}
      }}
      pages.forEach(candidate => candidate.classList.toggle('pg-on', candidate === was));
      return bad;
    }})()"""


def decks(arguments: list[str]) -> list[pathlib.Path]:
    roots = [pathlib.Path(item).resolve() for item in arguments] or [DEFAULT_ROOT]
    found: list[pathlib.Path] = []
    for root in roots:
        if root.is_dir():
            found.extend(root.rglob("lesson.html"))
        elif root.name == "lesson.html":
            found.append(root)
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--page", help="Orca browserPageId; defaults to this worktree's active tab")
    args = parser.parse_args()
    page = args.page or active_page()
    failures = []
    targets = decks(args.paths)
    for index, deck in enumerate(targets, 1):
        orca("goto", "--page", page, "--url", deck.as_uri())
        orca("snapshot", "--page", page)
        response = orca(
            "eval", "--page", page, "--expression", probe_expression()
        )["result"]["result"]
        issues = json.loads(response) if isinstance(response, str) else response
        if issues:
            failures.append((deck, issues))
            print(f"FAIL {deck.relative_to(ROOT)}: {json.dumps(issues, ensure_ascii=False)}")
        else:
            print(f"ok {index}/{len(targets)} {deck.relative_to(ROOT)}")
    print(f"{len(targets)} deck(s) rendered · {len(failures)} failing deck(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
