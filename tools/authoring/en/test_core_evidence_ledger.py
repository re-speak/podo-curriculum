#!/usr/bin/env python3
"""Prove the Core evidence ledger is complete and current."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_core_evidence_ledger
import track_parsers


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"


class CoreEvidenceLedgerTests(unittest.TestCase):
    def test_every_live_core_row_has_evidence(self):
        lessons = track_parsers.parse_core()
        self.assertEqual(len(lessons), 119)
        for lesson in lessons:
            with self.subTest(lesson=lesson["id"]):
                inventory, cefr, status, note = build_core_evidence_ledger.evidence_for(lesson)
                self.assertTrue(inventory)
                self.assertTrue(cefr)
                self.assertTrue(status)
                self.assertTrue(note)

    def test_generated_ledger_is_current(self):
        expected = build_core_evidence_ledger.render(track_parsers.parse_core())
        actual = (ROOT / "reference" / "core-evidence-ledger.md").read_text(encoding="utf-8")
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
