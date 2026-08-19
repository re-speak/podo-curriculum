#!/usr/bin/env python3
"""Structural checks for the standalone product decision console."""

from __future__ import annotations

from html.parser import HTMLParser
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
PAGE = ROOT / "product-decisions.html"


class _DecisionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.radio_names: list[str] = []
        self.checked_radios: dict[str, str] = {}
        self.ids: set[str] = set()
        self.external_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "input" and values.get("type") == "radio" and values.get("name"):
            self.radio_names.append(values["name"])
            if "checked" in values and values.get("value"):
                self.checked_radios[values["name"]] = values["value"]
        if tag in {"script", "link", "img"}:
            source = values.get("src") or values.get("href")
            if source and (source.startswith("http://") or source.startswith("https://")):
                self.external_assets.append(source)


class ProductDecisionConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = PAGE.read_text(encoding="utf-8")
        self.parser = _DecisionParser()
        self.parser.feed(self.raw)

    def test_four_decisions_are_present(self):
        self.assertEqual(set(self.parser.radio_names), {"courses", "freetalk", "trial", "prestudy"})

    def test_console_is_self_contained(self):
        self.assertEqual(self.parser.external_assets, [])
        self.assertIn("localStorage", self.raw)
        self.assertIn("prefers-reduced-motion", self.raw)

    def test_primary_controls_exist(self):
        self.assertTrue({"acceptAll", "copySummary", "resetChoices", "progressCount"}.issubset(self.parser.ids))

    def test_recorded_owner_decisions_are_the_defaults(self):
        self.assertEqual(
            self.parser.checked_radios,
            {
                "courses": "natural-arcs",
                "freetalk": "separate",
                "trial": "defer",
                "prestudy": "defer",
            },
        )
        self.assertIn("redesigned practical Contextual courses", self.raw)


if __name__ == "__main__":
    unittest.main()
