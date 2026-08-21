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


VALID_CONTEXTUAL = """\
# 상황별 한국어 — 목차

# 드라마

## 썸 & 고백 [중급] · 10 화 · 슬롯 010 · 문법 최고점: 핵심 106과

> ### 《우리, 어디서 본 적 있죠?》
>
> **등장인물** — `나`(학습자) · `유진`(그 사람)
>
> 비 오는 밤, 편의점 앞에서 시작한다.

**끝내면 할 수 있는 것:** 호감을 돌려서 표현하고 고백할 수 있다.

**1화 · 첫 만남**

*장면: 비 오는 밤 편의점 앞.*
*할 수 있는 것: 아는 사이인지 떠본다.*
- 우리 어디서 본 적 있지 않아요? — `~(으)ㄴ 적 있다` (핵심 42)
  → 네? 글쎄요…
- *표현:* `혹시`
"""


class ContextualParserTests(unittest.TestCase):
    """The slot pin is the guard on grape's natural key — see track_parsers.CTX_SLOT."""

    def parse(self, text: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as tmp:
            track = pathlib.Path(tmp) / "3-contextual-korean"
            track.mkdir()
            (track / "table-of-contents.md").write_text(text, encoding="utf-8")
            return track_parsers.parse_contextual(track)

    def test_reads_the_pinned_slot_off_the_course_header(self):
        (course,) = self.parse(VALID_CONTEXTUAL)

        self.assertEqual(course["slug"], "drama-crush")
        self.assertEqual(course["classLevelSlot"], 10)
        self.assertEqual(course["cast"], "`나`(학습자) · `유진`(그 사람)")

    def test_a_slot_is_read_wherever_it_sits_in_the_header_tail(self):
        text = VALID_CONTEXTUAL.replace(
            "· 10 화 · 슬롯 010 · 문법 최고점: 핵심 106과",
            "· 10 화 · 문법 최고점: 핵심 106과 · 슬롯 005")
        (course,) = self.parse(text)

        self.assertEqual(course["classLevelSlot"], 5)

    def test_rejects_a_course_that_does_not_pin_its_slot(self):
        """Unpinned, plan_courses.py would number it by position and silently
        renumber — and re-identify — every contextual course below it."""
        text = VALID_CONTEXTUAL.replace(" · 슬롯 010", "")

        with self.assertRaises(track_parsers.ParseError) as caught:
            self.parse(text)
        self.assertIn("슬롯", str(caught.exception))
