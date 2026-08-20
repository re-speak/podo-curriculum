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
    def generated_decks(self):
        paths = [
            core.build(number, core.LESSONS[number])[0]
            for number in core.GENERATED_LESSONS
        ]
        paths.append(core.PILOT)
        paths.extend(
            contextual.build(number, data)[0]
            for number, data in contextual.LESSONS.items()
        )
        for number, data in freetalking.TOPICS.items():
            for level in ("accessible", "full"):
                paths.append(
                    freetalking.TRACK
                    / "courses"
                    / f"{freetalking.COURSE}-{level}"
                    / "lessons"
                    / f'{number:02d}-{data["slug"]}'
                    / "lesson.html"
                )
        return paths

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

    def test_core_20_is_protected_from_batch_generation(self):
        self.assertNotIn(20, core.GENERATED_LESSONS)
        self.assertNotIn(20, core.LESSONS)
        self.assertTrue(core.PILOT.is_file())
        source = core.PILOT.read_text(encoding="utf-8")
        self.assertEqual(check_deck.meta_content(source, "podo:proofread-status"), "complete")

    def test_core_24_reuses_the_established_please_owner(self):
        new, _assumed, _receptive = core.VOCAB[24]
        self.assertNotIn("please|", new)
        self.assertEqual(core.RECYCLED_VOCAB[24], "please|お願いします|CORE-9")

    def test_revised_core_lane_has_supported_translation_and_real_freetalk(self):
        for number in (12, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24):
            _, html = core.build(number, core.LESSONS[number])
            chunks = dict(check_deck.pages(html))
            for page_id in ("p1-translate", "p2-translate"):
                self.assertIn('data-scaffolding-contract="target-v2"', chunks[page_id], number)
                self.assertIn('data-support-stage="supported"', chunks[page_id], number)
                self.assertIn('class="hint-chip"', chunks[page_id], number)
            freetalk = chunks["p3-freetalk"]
            self.assertGreaterEqual(freetalk.count('class="turn '), 4, number)
            self.assertIn("only if it fits naturally", freetalk, number)
            self.assertIn("Tutor", freetalk, number)
            self.assertIn("answer", freetalk, number)

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

    def test_every_generated_core_lesson_is_proofread_and_canonical(self):
        for number in core.GENERATED_LESSONS:
            _, html = core.build(number, core.LESSONS[number])
            self.assertEqual(
                check_deck.meta_content(html, "podo:proofread-status"),
                "complete",
                number,
            )
            page_chunks = dict(check_deck.pages(html))
            self.assertEqual(check_deck.core_canonical_shape_issues(page_chunks), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(page_chunks), [], number)
            self.assertIn('class="word-choice-list"', page_chunks["p1-choose"], number)
            self.assertIn('class="word-choice-list"', page_chunks["p2-choose"], number)
            self.assertIn('class="nuance-compare"', page_chunks["native-tip"], number)

    def test_generated_core_semantic_specs_are_complete(self):
        expected = set(core.GENERATED_LESSONS) - {12}
        self.assertEqual(set(core.CANONICAL_SPECS), expected)
        self.assertEqual(set(core.LIVE_SCENES), expected)
        for number in expected:
            spec = core.CANONICAL_SPECS[number]
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual([len(rows) for rows in spec["choices"]], [4, 4], number)
            self.assertEqual(core.LIVE_SCENES[number][0][1], "other", number)
            self.assertEqual(core.LIVE_SCENES[number][-1][1], "other", number)

    def test_core_batch_matches_generator(self):
        for number in core.GENERATED_LESSONS:
            path, expected = core.build(number, core.LESSONS[number])
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

    def test_every_generated_deck_passes_the_quality_checker(self):
        expected_count = (
            len(core.GENERATED_LESSONS)
            + 1  # protected, hand-edited CORE-20 pilot
            + len(contextual.LESSONS)
            + 2 * len(freetalking.TOPICS)
        )
        self.assertEqual(len(self.generated_decks()), expected_count)
        for path in self.generated_decks():
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)


if __name__ == "__main__":
    unittest.main()
