#!/usr/bin/env python3
"""Structural checks for the decision consoles committed under `sandbox/drafts/`.

A decision console is an HTML page that carries the questions a round could not
answer by itself, so the person who can answer them finds the question in the
repository rather than in a pull-request body that scrolls away. Two exist:

    sandbox/drafts/en/product-decisions.html        product shape, 2026-08-13
    sandbox/drafts/kr/proofread-decisions.html      proofreading round, 2026-08-24

The checks are deliberately few, and each one guards a way these pages have
actually failed or would fail silently:

  ASSETS   a console is opened from a file:// path with no network. A stylesheet
           or script on another host renders an unstyled wall of text and the
           reader cannot tell that anything is missing. Google Fonts is the one
           exception the published-artifact CSP admits, so it is allowed here too.

  NAMES    every radio carries a `name`. A radio group with no name is not a
           group: each button becomes independently checkable, and the page
           silently records two answers to one question.

  IDS      no duplicate `id`. Both consoles look their controls up by id.

  HANDOFF  the page can give its answers back — a clipboard copy, a save, or
           both. A console that records decisions and cannot return them has
           wasted the reader's time.

This check is shared rather than per-language on purpose: the mechanism is not
about Korean or English, and a rule filed under one language is a rule the other
re-derives a week later.

    python3 -m unittest tools.authoring.test_decision_console
"""
from __future__ import annotations

import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[2] / "sandbox/drafts"
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
EXTERNAL = re.compile(r"^(?:https?:)?//", re.I)


def consoles() -> list[pathlib.Path]:
    return sorted(p for p in ROOT.glob("*/*.html") if "decisions" in p.name)


class _Scan(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.unnamed_radios = 0
        self.radio_names: set[str] = set()
        self.external: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "input" and a.get("type") == "radio":
            if a.get("name"):
                self.radio_names.add(a["name"])
            else:
                self.unnamed_radios += 1
        for key in ("src", "href"):
            url = a.get(key) or ""
            if EXTERNAL.match(url) and not any(h in url for h in FONT_HOSTS):
                self.external.append(url)


class DecisionConsoleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pages = consoles()
        self.assertTrue(self.pages, f"no decision console found under {ROOT}")

    def test_no_external_assets(self) -> None:
        for page in self.pages:
            scan = _Scan()
            scan.feed(page.read_text(encoding="utf-8"))
            self.assertEqual(
                [], scan.external,
                f"{page.name} loads from another host; it must open offline")

    def test_every_radio_is_in_a_named_group(self) -> None:
        """Two consoles, two shapes, one property.

        The English page writes its radios into the markup; the Korean one
        renders them from a data array. A static parse sees the first and finds
        nothing in the second, so check whichever the page actually uses — and
        require that it uses one of them, so a console with no choices at all
        still fails.
        """
        for page in self.pages:
            src = page.read_text(encoding="utf-8")
            scan = _Scan()
            scan.feed(src)
            self.assertEqual(
                0, scan.unnamed_radios,
                f"{page.name} has {scan.unnamed_radios} radio(s) with no name")
            if scan.radio_names:
                continue
            ids = re.findall(r"^\s*id:\s*\"([^\"]+)\"", src, re.M)
            opts = re.findall(r"^\s*opts:\s*\[", src, re.M)
            self.assertTrue(ids, f"{page.name} offers no choices, in markup or in data")
            self.assertEqual(
                len(ids), len(opts),
                f"{page.name} declares {len(ids)} item(s) but {len(opts)} option list(s)")
            self.assertEqual(
                len(ids), len(set(ids)), f"{page.name} repeats an item id")
            # Anchored to the input itself. A bare substring search passes on the
            # lookup selector elsewhere in the file even after the render site
            # loses its name, which is the one thing this test is here to catch.
            self.assertRegex(
                src, r'<input\s+type="radio"\s+name="\$\{it\.id\}"',
                f"{page.name} renders radios without naming the group after its item")

    def test_ids_are_unique(self) -> None:
        for page in self.pages:
            scan = _Scan()
            scan.feed(page.read_text(encoding="utf-8"))
            dupes = {i for i in scan.ids if scan.ids.count(i) > 1}
            self.assertEqual(set(), dupes, f"{page.name} repeats id(s) {sorted(dupes)}")

    def test_answers_can_be_handed_back(self) -> None:
        for page in self.pages:
            src = page.read_text(encoding="utf-8")
            self.assertTrue(
                "clipboard" in src or "localStorage" in src,
                f"{page.name} records decisions but cannot return them")


if __name__ == "__main__":
    unittest.main()
