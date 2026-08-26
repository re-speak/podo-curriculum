from __future__ import annotations

import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import plan_courses


class CourseMarketContractTests(unittest.TestCase):
    def test_rendered_course_has_exactly_one_japan_market_country_code(self):
        course = {
            "level": "초급",
            "slug": "test-course",
            "title": {"ko": "테스트", "en": "Test", "ja": "テスト"},
            "note": "테스트",
            "lessons": [],
        }
        rendered = plan_courses.course_yaml(
            course,
            {"type": "BASIC"},
            "100.010",
            "test-track",
            {},
        )
        self.assertEqual(re.findall(r"^  countryCode: (\S+)$", rendered, re.MULTILINE), ["JP"])

    def test_country_code_cannot_be_omitted(self):
        with self.assertRaisesRegex(ValueError, "required"):
            plan_courses.market_country_code(None)

    def test_country_code_must_be_supported_downstream(self):
        with self.assertRaisesRegex(ValueError, "KR.*JP|JP.*KR"):
            plan_courses.market_country_code("US")

    def test_japanese_market_course_cannot_use_kr(self):
        with self.assertRaisesRegex(ValueError, "require.*JP"):
            plan_courses.market_country_code("KR")


class DeckMetaTests(unittest.TestCase):
    """The deck names the lesson; the parser must not lose that name."""

    def test_titles_are_read_whatever_order_the_attributes_are_in(self):
        # Two 3-contextual-korean travel courses have been through an HTML
        # formatter and store `content` first. Matching name-then-content read
        # no title for those 19 decks and wrote lesson.yaml without en/ja.
        formatted = (
            '<meta content="01-check-in" name="podo:lesson-id"/>\n'
            '<meta content="체크인 &amp; 요청" name="podo:title-ko"/>\n'
            '<meta content="Check-in and requests" name="podo:title-en"/>\n'
            '<meta content="チェックインとお願い" name="podo:title-ja"/>\n'
        )
        meta = plan_courses.meta_values(formatted)
        self.assertEqual(meta["podo:lesson-id"], "01-check-in")
        self.assertEqual(meta["podo:title-ko"], "체크인 & 요청")
        self.assertEqual(meta["podo:title-ja"], "チェックインとお願い")

    def test_entities_resolve_to_the_text_they_stand_for(self):
        meta = plan_courses.meta_values('<meta name="podo:title-ko" content="놀람 &amp; 반전">')
        self.assertEqual(meta["podo:title-ko"], "놀람 & 반전")


class CourseCopyTests(unittest.TestCase):
    def setUp(self):
        self.copy = plan_courses.course_copy()

    def test_every_planned_course_has_an_en_and_ja_description(self):
        here = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"
        for track, cfg in plan_courses.TRACKS.items():
            parsed = plan_courses.track_parsers.PARSERS[track](here / "tracks" / track)
            courses = plan_courses.pack_core(parsed) if track == "2-core-patterns" else parsed
            for course in (plan_courses.compose(c, cfg, i)
                           for i, c in enumerate(courses, 1)):
                with self.subTest(course=course["slug"]):
                    written = self.copy.get(course["slug"], {}).get("description", {})
                    self.assertTrue(written.get("en"), "no en description")
                    self.assertTrue(written.get("ja"), "no ja description")

    def test_ko_falls_back_to_the_toc_line_and_never_to_build_metadata(self):
        course = {"slug": "unknown", "note": "끝내면 할 수 있는 것.",
                  "title": {"ko": "제목"}, "level": "초급", "lessons": []}
        self.assertEqual(
            plan_courses.course_description(course, {})["ko"], "끝내면 할 수 있는 것.")

    def test_written_ko_overrides_the_toc_line(self):
        course = {"slug": "core-beginner-1", "note": "Unit 1–2 · 이건 뭐예요?",
                  "title": {"ko": "제목"}, "level": "초급", "lessons": []}
        self.assertNotIn("Unit", plan_courses.course_description(course, self.copy)["ko"])

    def test_titles_fit_the_two_columns_this_market_reads(self):
        # ja is on the learner's screen, ko is grape's admin label. en is
        # exempt: no learner of a Korean course sees EN_BOOK_NAME.
        here = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"
        for track, cfg in plan_courses.TRACKS.items():
            parsed = plan_courses.track_parsers.PARSERS[track](here / "tracks" / track)
            courses = plan_courses.pack_core(parsed) if track == "2-core-patterns" else parsed
            for course in (plan_courses.compose(c, cfg, i)
                           for i, c in enumerate(courses, 1)):
                title = plan_courses.course_title(course, self.copy)
                for lang, limit in plan_courses.TITLE_LIMITS.items():
                    with self.subTest(course=course["slug"], lang=lang):
                        self.assertLessEqual(len(title[lang]), limit, title[lang])

    def test_a_written_title_overrides_the_composed_one(self):
        course = {"slug": "ctx-banmal-dropping-formality-upper-beginner",
                  "title": {"ko": "x" * 40, "en": "x", "ja": "y"}}
        self.assertEqual(
            plan_courses.course_title(course, self.copy)["ko"], "(초중급) 반말 · 말 놓기")

    def test_upper_bands_are_not_collapsed_into_their_neighbours(self):
        self.assertEqual(plan_courses.DIFFICULTY["초중급"], "UPPER_BEGINNER")
        self.assertEqual(plan_courses.DIFFICULTY["중고급"], "UPPER_INTERMEDIATE")
        self.assertEqual(len(set(plan_courses.DIFFICULTY.values())), 5)


if __name__ == "__main__":
    unittest.main()
