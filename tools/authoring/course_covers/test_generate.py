import importlib.util
import pathlib
import re
import unittest

import yaml


MODULE_PATH = pathlib.Path(__file__).with_name("generate.py")
SPEC = importlib.util.spec_from_file_location("course_cover_generate", MODULE_PATH)
assert SPEC and SPEC.loader
generate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate)


class CoverTypographyTest(unittest.TestCase):
    def test_english_title_wraps_only_between_words(self) -> None:
        self.assertEqual(generate.split_title("What came before"), ["What came", "before"])
        self.assertEqual(generate.split_title("Travelling alone"), ["Travelling", "alone"])
        self.assertEqual(generate.split_title("Getting things done"), ["Getting", "things done"])
        self.assertEqual(generate.split_title("Work and money"), ["Work and", "money"])
        self.assertEqual(generate.split_title("Worth a thought"), ["Worth a", "thought"])
        self.assertEqual(
            generate.split_title("Counterintelligence"),
            ["Counterintelligence"],
        )

    def test_korean_title_uses_semantic_spacing(self) -> None:
        self.assertEqual(
            generate.split_title("온라인 팬덤 & 커뮤니티"),
            ["온라인 팬덤", "& 커뮤니티"],
        )

    def test_shorter_lines_receive_larger_type(self) -> None:
        self.assertEqual(generate.title_size(["What came", "before"]), 96)
        self.assertGreater(generate.title_size(["At the office"]), 80)

    def test_catalog_titles_preserve_words_and_fit(self) -> None:
        for course_path in generate.discover():
            doc = yaml.safe_load(course_path.read_text(encoding="utf-8"))
            lang = course_path.parts[-3]
            slug = course_path.parent.name
            _, _, topic, _ = generate.cover_copy(lang, slug, doc["spec"]["title"])
            lines = generate.split_title(topic)
            font_size = generate.title_size(lines)
            with self.subTest(course=f"{lang}/{slug}"):
                self.assertEqual(" ".join(lines), re.sub(r"\s+", " ", topic).strip())
                self.assertLessEqual(len(lines), 2)
                self.assertTrue(
                    all(
                        generate.visual_width(line) * font_size
                        <= generate.TITLE_CONTENT_WIDTH
                        for line in lines
                    )
                )


if __name__ == "__main__":
    unittest.main()
