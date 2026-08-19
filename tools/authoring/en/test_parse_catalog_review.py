#!/usr/bin/env python3
"""Regression tests for native catalog-review intake."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import parse_catalog_review


CURRENT = {
    "CORE-31": {"title": "We watched a movie last night", "firstLine": "We watched a movie last night."},
    "FT-7": {"title": "Convenience showdown", "firstLine": "Convenience stores, trains, taxis, delivery — pick the one Japan does best."},
}


VALID = """PODO ENGLISH CURRICULUM — NATIVE REVIEW
303 items · 1 flagged · 2 commented

## GENERAL
Workplace register needs one pass.

## FLAGGED — 1
CORE-31  We watched a movie last night
    says: We watched a movie last night.
    → This is natural, but the frame is too empty.

## COMMENTS, not flagged — 1
FT-7  Convenience showdown
    says: Convenience stores, trains, taxis, delivery — pick the one Japan does best.
    → Strong topic.
      Keep the concrete opening.
"""


class CatalogReviewTests(unittest.TestCase):
    def test_parses_flags_comments_and_general_feedback(self):
        review = parse_catalog_review.parse(VALID, CURRENT)
        self.assertEqual(review["general"], "Workplace register needs one pass.")
        self.assertEqual([item["id"] for item in review["items"]], ["CORE-31", "FT-7"])
        self.assertTrue(review["items"][0]["flagged"])
        self.assertFalse(review["items"][1]["flagged"])
        self.assertEqual(review["items"][1]["comment"], "Strong topic.\nKeep the concrete opening.")

    def test_rejects_stale_snapshot(self):
        stale = VALID.replace("We watched a movie last night.", "We saw a film.")
        with self.assertRaisesRegex(parse_catalog_review.ReviewError, "stale first line"):
            parse_catalog_review.parse(stale, CURRENT)

    def test_rejects_unknown_or_duplicate_ids(self):
        with self.assertRaisesRegex(parse_catalog_review.ReviewError, "unknown review id"):
            parse_catalog_review.parse(VALID.replace("CORE-31", "CORE-999"), CURRENT)
        duplicated = VALID + "\n## FLAGGED — 1\nCORE-31  We watched a movie last night\n    says: We watched a movie last night.\n"
        with self.assertRaisesRegex(parse_catalog_review.ReviewError, "duplicate"):
            parse_catalog_review.parse(duplicated, CURRENT)


if __name__ == "__main__":
    unittest.main()
