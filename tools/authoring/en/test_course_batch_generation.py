#!/usr/bin/env python3
"""Keep generated English course batches reproducible from their reviewed data."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_contextual_course_batch as contextual
import generate_core_course_batch as core
import generate_ft_course_batch as freetalking
import check_deck


class CourseBatchGenerationTests(unittest.TestCase):
    def assert_rules_are_pattern_specific(self, module):
        forbidden = (
            "Use the second frame",
            "Use the complete frame",
            "Use the second move",
            "make the practical result clear",
        )
        for number, data in module.LESSONS.items():
            self.assertEqual(len(data["rules"]), 2, number)
            for english, japanese in data["rules"]:
                self.assertTrue(english.strip(), number)
                self.assertTrue(japanese.strip(), number)
                self.assertFalse(any(text in english for text in forbidden), number)

    def test_generated_rules_are_pattern_specific(self):
        self.assert_rules_are_pattern_specific(core)
        self.assert_rules_are_pattern_specific(contextual)

    def test_every_emitted_reorder_uses_meaningful_chunks(self):
        for module in (core, contextual):
            for number, data in module.LESSONS.items():
                for part in (1, 2):
                    if part not in data.get("omit_reorder", ()):
                        core.validate_reorder_pattern(data[f"p{part}"])

    def test_core_18_preserves_the_authoritative_model(self):
        self.assertEqual(core.strip_marks(core.LESSONS[18]["p1"][0][0]), "Can you drive?")

    def test_core_12_uses_the_canonical_proofread_shape(self):
        _, html = core.build(12, core.LESSONS[12])
        page_chunks = dict(check_deck.pages(html))
        self.assertEqual(len(page_chunks), 26)
        self.assertEqual(check_deck.meta_content(html, "podo:proofread-status"), "complete")
        self.assertEqual(check_deck.core_canonical_shape_issues(page_chunks), [])
        self.assertIn('class="sent-hero"', page_chunks["p1-teach"])
        self.assertIn('class="sent-more"', page_chunks["p1-teach"])
        self.assertIn('class="batchim ending-rule"', page_chunks["p1-rule"])
        self.assertIn('class="nuance-compare"', page_chunks["native-tip"])
        self.assertIn('class="word-choice-list"', page_chunks["p1-choose"])
        self.assertIn('class="word-choice-list"', page_chunks["p2-choose"])
        self.assertNotIn("I start work at eight.</span>", page_chunks["p1-choose"])
        self.assertIn('data-sync-option="correct" data-correct>eight</span>', page_chunks["p1-choose"])
        self.assertIn('data-sync-option="correct" data-correct>usually finish</span>', page_chunks["p2-choose"])
        self.assertEqual(
            [len(block.split('class="choice"')) - 1 for block in page_chunks["p1-reorder"].split('class="task-block"')[1:]],
            [4, 4, 4, 4],
        )

    def test_unproofread_generated_core_lessons_are_explicitly_pending(self):
        for number in core.LESSONS:
            if number == 12:
                continue
            _, html = core.build(number, core.LESSONS[number])
            self.assertEqual(
                check_deck.meta_content(html, "podo:proofread-status"),
                "pending",
                number,
            )

    def test_core_batch_matches_generator(self):
        for number, data in core.LESSONS.items():
            path, expected = core.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)

    def test_contextual_batch_matches_generator(self):
        for number, data in contextual.LESSONS.items():
            path, expected = contextual.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)

    def test_freetalking_pairs_match_generator(self):
        for number, data in freetalking.TOPICS.items():
            for level in ("accessible", "full"):
                slug = f'{number:02d}-{data["slug"]}'
                path = (
                    freetalking.TRACK
                    / "courses"
                    / f"{freetalking.COURSE}-{level}"
                    / "lessons"
                    / slug
                    / "lesson.html"
                )
                expected = freetalking.build(number, level)
                self.assertEqual(path.read_text(encoding="utf-8"), expected, path)


if __name__ == "__main__":
    unittest.main()
