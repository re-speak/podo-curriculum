#!/usr/bin/env python3
"""Focused regression tests for curriculum TOC parsers."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import track_parsers


VALID_FREETALKING = """\
# 중급·고급 프리토킹 — 목차

# 1. 두 나라 사이

*여러 줄로 쓰인 설명은 사람이 읽는 배경이다.
필수 필드는 아래에서 구조적으로 읽는다.*

**Course outcome:** 한일 차이를 설명하고 비교한다.
**Session format:** 한일

1. **놀랐던 순간** — 무엇이 왜 놀라웠는지 설명하기
2. **민감한 경험** — 말할 수 있는 범위에서 경험 이야기하기 `[깊게]`
"""


class FreeTalkingParserTests(unittest.TestCase):
    def parse(self, text: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as tmp:
            track = pathlib.Path(tmp) / "4-freetalking"
            track.mkdir()
            (track / "table-of-contents.md").write_text(text, encoding="utf-8")
            return track_parsers.parse_freetalking(track)

    def test_reads_structured_course_fields_and_lesson_metadata(self):
        courses = self.parse(VALID_FREETALKING)

        self.assertEqual(len(courses), 2)
        intermediate, advanced = courses
        self.assertEqual(intermediate["level"], "중급")
        self.assertEqual(intermediate["classLevelSlot"], 9)
        self.assertEqual(advanced["level"], "고급")
        self.assertEqual(advanced["classLevelSlot"], 10)
        course = advanced
        self.assertEqual(course["note"], "한일 차이를 설명하고 비교한다.")
        self.assertEqual(course["sessionFormat"], "한일")
        self.assertEqual(course["lessons"][1]["title"], "민감한 경험")
        self.assertEqual(course["lessons"][1]["canDo"], "말할 수 있는 범위에서 경험 이야기하기")
        self.assertTrue(course["lessons"][1]["deep"])

    def test_rejects_missing_course_outcome(self):
        text = VALID_FREETALKING.replace(
            "**Course outcome:** 한일 차이를 설명하고 비교한다.\n", ""
        )
        with self.assertRaisesRegex(track_parsers.ParseError, "Course outcome"):
            self.parse(text)

    def test_rejects_unknown_session_format(self):
        text = VALID_FREETALKING.replace(
            "**Session format:** 한일", "**Session format:** 설문"
        )
        with self.assertRaisesRegex(track_parsers.ParseError, "unknown session format"):
            self.parse(text)

    def test_rejects_missing_lesson_outcome(self):
        text = VALID_FREETALKING.replace(
            "1. **놀랐던 순간** — 무엇이 왜 놀라웠는지 설명하기",
            "1. **놀랐던 순간**",
        )
        with self.assertRaisesRegex(track_parsers.ParseError, "observable outcome"):
            self.parse(text)

    def test_rejects_non_continuous_lesson_numbers(self):
        text = VALID_FREETALKING.replace(
            "2. **민감한 경험**", "3. **민감한 경험**"
        )
        with self.assertRaisesRegex(track_parsers.ParseError, "continuous from 1"):
            self.parse(text)


if __name__ == "__main__":
    unittest.main()
