#!/usr/bin/env python3
"""Regression tests for the generated English catalog family."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_catalog


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"


class CatalogGenerationTests(unittest.TestCase):
    def test_gateway_and_track_counts(self):
        data = build_catalog.build()
        self.assertEqual([track["total"] for track in data["tracks"]], [119, 60, 121, 12])
        self.assertEqual(data["totals"]["review"], 300)
        self.assertEqual(data["totals"]["items"], 312)

    def test_all_generated_pages_are_current(self):
        data = build_catalog.build()
        summaries = [{key: value for key, value in track.items() if key != "groups"}
                     for track in data["tracks"]]
        gateway = (build_catalog.TOOLS / "gateway_template.html").read_text(encoding="utf-8")
        expected_gateway = gateway.replace("/*__DATA__*/null", __import__("json").dumps(
            {**data, "tracks": summaries}, ensure_ascii=False, separators=(",", ":")))
        self.assertEqual((ROOT / "catalog.html").read_text(encoding="utf-8"), expected_gateway)

        nav = [{key: track[key] for key in ("id", "no", "name", "short", "accent")}
               for track in data["tracks"]]
        review = {item["id"]: {"title": item["title"], "primary": item["primary"]}
                  for track in data["tracks"] if track["status"] == "review"
                  for group in track["groups"] for item in group["lessons"]}
        template = (build_catalog.TOOLS / "track_template.html").read_text(encoding="utf-8")
        for track in data["tracks"]:
            with self.subTest(track=track["id"]):
                payload = {"levels": build_catalog.LEVELS, "track": track, "nav": nav,
                           "review": review}
                expected = template.replace("/*__DATA__*/null", __import__("json").dumps(
                    payload, ensure_ascii=False, separators=(",", ":")))
                actual = (ROOT / "catalog" / f'{track["id"]}.html').read_text(encoding="utf-8")
                self.assertEqual(actual, expected)

    def test_review_layer_is_shared_and_migrates_existing_state(self):
        source = (pathlib.Path(__file__).resolve().parent / "catalog_review.js").read_text(encoding="utf-8")
        self.assertIn('podo-en-review-v1', source)
        self.assertIn("PODO_REVIEW_INDEX", source)
        self.assertIn("flag-control", (pathlib.Path(__file__).resolve().parent / "track_template.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
