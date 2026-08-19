from __future__ import annotations

import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import plan_courses


class CoursePlanTests(unittest.TestCase):
    def test_approved_course_allocation_is_complete_and_unique(self):
        courses = plan_courses.planned_courses()
        self.assertEqual(len(courses), 43)
        self.assertEqual(len({course["slug"] for course in courses}), 43)
        self.assertEqual(len({course["classLevel"] for course in courses}), 43)
        self.assertIn("talk-balance-games-full", {course["slug"] for course in courses})

    def test_every_rendered_course_has_exactly_one_japan_market_country_code(self):
        for course in plan_courses.planned_courses():
            with self.subTest(course=course["slug"]):
                rendered = plan_courses.course_yaml(course)
                self.assertEqual(
                    re.findall(r"^  countryCode: (\S+)$", rendered, re.MULTILINE),
                    ["JP"],
                )
                self.assertNotIn("LANG_TYPE", "\n".join(
                    line for line in rendered.splitlines()
                    if not line.lstrip().startswith("#")
                ))
                self.assertIn("  enabled: false", rendered)

    def test_country_code_cannot_be_omitted(self):
        with self.assertRaisesRegex(ValueError, "required"):
            plan_courses.market_country_code(None)

    def test_country_code_must_be_supported_downstream(self):
        with self.assertRaisesRegex(ValueError, "KR.*JP|JP.*KR"):
            plan_courses.market_country_code("US")

    def test_japanese_market_course_cannot_use_kr(self):
        with self.assertRaisesRegex(ValueError, "require.*JP"):
            plan_courses.market_country_code("KR")


class CatalogueCopyTests(unittest.TestCase):
    """GT_CLASS_COURSE keeps three name columns and the app picks by locale."""

    def setUp(self):
        self.copy = plan_courses.course_copy()
        self.courses = plan_courses.planned_courses()

    def test_every_planned_course_has_written_copy_in_all_three_languages(self):
        for course in self.courses:
            with self.subTest(course=course["slug"]):
                self.assertEqual(plan_courses.missing_copy(course["slug"], self.copy), [])

    def test_copy_holds_no_entry_for_a_course_that_no_longer_exists(self):
        planned = {course["slug"] for course in self.courses}
        self.assertEqual(sorted(set(self.copy) - planned), [])

    def test_rendered_course_carries_a_ko_en_ja_title_and_description(self):
        for course in self.courses:
            rendered = plan_courses.course_yaml(course, copy=self.copy)
            title, description = rendered.split("  description:", 1)
            with self.subTest(course=course["slug"]):
                for block, name in ((title.split("  title:", 1)[1], "title"),
                                    (description, "description")):
                    langs = re.findall(r"^    ([a-z]{2}): ", block, re.MULTILINE)
                    self.assertEqual(langs, ["ko", "en", "ja"], name)

    def test_description_ships_no_build_notation(self):
        # 'Core 25–36 · A1 → A2' and '13 topics · Full version' described the
        # build, not the course. The CEFR band belongs in the title instead.
        for slug, entry in self.copy.items():
            with self.subTest(course=slug):
                for lang, text in entry["description"].items():
                    self.assertNotRegex(text, r"Core \d+|topics ·|version$", lang)

    def test_cefr_band_maps_across_all_five_difficulty_bands(self):
        seen = {course["difficulty"] for course in self.courses}
        self.assertEqual(seen, {"BEGINNER", "UPPER_BEGINNER", "INTERMEDIATE",
                                "UPPER_INTERMEDIATE", "ADVANCED"})

    def test_a_ceiling_band_wins_over_a_lower_one_in_the_same_string(self):
        self.assertEqual(plan_courses._level("B2–C1 bridge"), "ADVANCED")
        self.assertEqual(plan_courses._level("B1+ → B2"), "UPPER_INTERMEDIATE")
        self.assertEqual(plan_courses._level("A2 → B1 → B1"), "INTERMEDIATE")
        self.assertEqual(plan_courses._level("A1 → A2"), "UPPER_BEGINNER")


if __name__ == "__main__":
    unittest.main()
