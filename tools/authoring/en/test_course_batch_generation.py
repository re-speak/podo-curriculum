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


class CourseBatchGenerationTests(unittest.TestCase):
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
