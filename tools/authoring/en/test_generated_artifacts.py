#!/usr/bin/env python3
"""Prove generated maps and briefs match the live parsed TOCs."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_grammar_map
import build_core_evidence_ledger
import build_lesson_briefs
import track_parsers


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"


class GeneratedArtifactTests(unittest.TestCase):
    def test_core_evidence_ledger_is_current(self):
        expected = build_core_evidence_ledger.render(track_parsers.parse_core())
        actual = (ROOT / "reference" / "core-evidence-ledger.md").read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_grammar_map_is_current(self):
        expected = build_grammar_map.render(track_parsers.parse_core())
        actual = (ROOT / "reference/grammar-coverage-map.md").read_text(encoding="utf-8")
        self.assertEqual(actual, expected)
        self.assertIn("**Missing grammar support:** 0 — none", actual)

    def test_every_brief_and_index_matches_its_parser(self):
        for track in sorted(track_parsers.PARSERS):
            lessons = track_parsers.parse_track(track)
            toc = ROOT / "tracks" / track / "toc"
            expected_names = {f"{lesson['id']}.md" for lesson in lessons} | {"index.md"}
            self.assertEqual({path.name for path in toc.glob("*.md")}, expected_names)
            for i, lesson in enumerate(lessons):
                with self.subTest(track=track, lesson=lesson["id"]):
                    actual = (toc / f"{lesson['id']}.md").read_text(encoding="utf-8")
                    self.assertEqual(actual, build_lesson_briefs.render(track, lessons, i))


if __name__ == "__main__":
    unittest.main()
