#!/usr/bin/env python3
"""Source-level regression tests for the narrow FT 2-8 batch generator."""

from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import re
import unittest

from bs4 import BeautifulSoup


HERE = pathlib.Path(__file__).resolve().parent
GENERATOR = HERE / "generate_ft_course_batch.py"
SPEC = importlib.util.spec_from_file_location("generate_ft_course_batch", GENERATOR)
assert SPEC and SPEC.loader
ft = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ft)


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def variant_value(topic: dict, key: str, variant: str):
    return topic.get(f"{key}_full", topic[key]) if variant == "full" else topic[key]


class FreetalkingBatchSourceTest(unittest.TestCase):
    def test_generator_owns_only_ft2_to_ft6_and_ft8(self) -> None:
        self.assertEqual(set(ft.TOPICS), {2, 3, 4, 5, 6, 8})
        self.assertNotIn(1, ft.TOPICS)
        self.assertNotIn(7, ft.TOPICS)

    def test_preserved_ft7_pair_matches_locked_hashes(self) -> None:
        for variant, (path, expected) in ft.PRESERVED_FT7.items():
            with self.subTest(variant=variant):
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_pair_has_the_same_eight_conversation_jobs(self) -> None:
        for number, topic in ft.TOPICS.items():
            accessible = ["Start here", *[item[0] for item in [topic["warm2"], *topic["questions"]]]]
            full = ["Start here", *[item[0] for item in [variant_value(topic, "warm2", "full"), *variant_value(topic, "questions", "full")]]]
            with self.subTest(topic=number):
                self.assertEqual(accessible, full)
                self.assertEqual(len(accessible), 8)
                self.assertEqual(len(topic["article_accessible"]), len(topic["article"]))
                self.assertEqual(
                    [ja for _en, ja in topic["article_accessible"]],
                    [ja for _en, ja in topic["article"]],
                )
                accessible_glosses = topic["gloss_accessible"]
                full_glosses = topic["gloss"]
                overlap = {
                    item[1].casefold() for item in accessible_glosses.values()
                } & {
                    item[1].casefold() for item in full_glosses.values()
                }
                self.assertLessEqual(len(overlap) / len(full_glosses), 0.70)
                for article_key, gloss_key in (("article_accessible", "gloss_accessible"), ("article", "gloss")):
                    article = topic[article_key]
                    for index, (surface, _headword, _meaning) in topic[gloss_key].items():
                        self.assertIn(surface, article[index - 1][0])

    def test_each_variant_has_eight_distinct_prompts_and_followups(self) -> None:
        for number, topic in ft.TOPICS.items():
            for variant in ("accessible", "full"):
                opening = variant_value(topic, "opening", variant)
                opening_followups = variant_value(topic, "opening_followups", variant)
                warm2 = variant_value(topic, "warm2", variant)
                questions = variant_value(topic, "questions", variant)
                items = [
                    (opening[0], opening_followups),
                    (warm2[2], warm2[4]),
                    *((item[2], item[4]) for item in questions),
                ]
                prompts = [normalized(prompt) for prompt, _ in items]
                followups = [normalized(question) for _prompt, group in items for question in group]
                with self.subTest(topic=number, variant=variant):
                    self.assertEqual(len(items), 8)
                    self.assertEqual(len(prompts), len(set(prompts)))
                    self.assertEqual(len(followups), len(set(followups)))
                    self.assertTrue(all(2 <= len(group) <= 3 for _prompt, group in items))

    def test_full_articles_do_not_use_generic_discourse_leads(self) -> None:
        banned = (
            "A useful starting point is this:",
            "Seen more broadly,",
            "A further complication is that",
            "The key nuance is that",
            "Taken together, the point is that",
        )
        for number in ft.TOPICS:
            html = ft.build(number, "full")
            with self.subTest(topic=number):
                self.assertFalse(any(lead in html for lead in banned))

    def test_rendered_conversation_pages_keep_distinct_prompts_and_followups(self) -> None:
        for number in ft.TOPICS:
            for variant in ("accessible", "full"):
                soup = BeautifulSoup(ft.build(number, variant), "html.parser")
                pages = [soup.select_one(f'[data-page-id="{page_id}"]') for page_id in ("warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6")]
                prompts = [normalized(page.select_one(".section-subtitle.ask .ko").get_text(" ", strip=True)) for page in pages]
                followup_sets = [tuple(normalized(item.get_text(" ", strip=True)) for item in page.select(".tn-more li")) for page in pages]
                with self.subTest(topic=number, variant=variant):
                    self.assertEqual(len(prompts), len(set(prompts)))
                    self.assertEqual(len(followup_sets), len(set(followup_sets)))

    def test_talk_intro_requires_real_reciprocal_conversation(self) -> None:
        for number in ft.TOPICS:
            for variant in ("accessible", "full"):
                html = ft.build(number, variant)
                with self.subTest(topic=number, variant=variant):
                    self.assertIn("React or share briefly", html)
                    self.assertIn("the most interesting parts of your answers", html)


if __name__ == "__main__":
    unittest.main()
