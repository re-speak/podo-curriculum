import pathlib
import re
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRACK = ROOT / "sandbox/drafts/en/tracks/3-freetalking/courses"
sys.path.insert(0, str(HERE))

import ft_content_overrides  # noqa: E402
import ft_question_bank  # noqa: E402


def prompts(path: pathlib.Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    result = {}
    for page_id in ft_question_bank.PAGES:
        start, end = ft_question_bank._page_bounds(source, page_id)
        page = source[start:end]
        match = re.search(r'<p class="section-subtitle ask">.*?<span class="ko">(.*?)</span>', page, re.S)
        if not match:
            raise AssertionError(f"missing prompt in {path}: {page_id}")
        result[page_id] = re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return result


class FullFirstContractTests(unittest.TestCase):
    def test_every_batch_generator_applies_the_canonical_question_bank(self):
        generators = sorted(HERE.glob("generate_ft_*_batch.py"))
        self.assertEqual(len(generators), 11)
        for path in generators:
            with self.subTest(generator=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn("ft_question_bank.apply(", source)

    def test_only_documented_b1_adaptations_differ(self):
        differences = set()
        for full_course in sorted(TRACK.glob("*-full")):
            accessible_course = TRACK / full_course.name.replace("-full", "-accessible")
            for full_path in sorted(full_course.glob("lessons/*/lesson.html")):
                accessible_path = accessible_course / full_path.relative_to(full_course)
                review = re.search(r'content="FT-(\d+)"', full_path.read_text(encoding="utf-8"))
                self.assertIsNotNone(review, full_path)
                topic = int(review.group(1))
                full_prompts = prompts(full_path)
                accessible_prompts = prompts(accessible_path)
                differences.update(
                    (topic, page_id)
                    for page_id in ft_question_bank.PAGES
                    if accessible_prompts[page_id] != full_prompts[page_id]
                )
        self.assertEqual(differences, ft_question_bank.ACCESSIBLE_ADAPTATIONS)

    def test_replacement_topics_have_complete_conversation_pools(self):
        for topic, override in ft_content_overrides.TOPIC_OVERRIDES.items():
            with self.subTest(topic=topic):
                if "articles" in override:
                    self.assertEqual(len(override["articles"]), 10)
                if "questions" in override:
                    self.assertEqual(set(override["questions"]), set(ft_question_bank.PAGES))
                    for variants in override["questions"].values():
                        full = variants["full"]
                        self.assertEqual(len(full), 5)
                        self.assertEqual(len(full[4]), 2)

    def test_changed_decks_return_to_proofread_queue(self):
        changed = set(ft_question_bank.BANK) | set(ft_content_overrides.QUESTION_OVERRIDES) | set(ft_content_overrides.TOPIC_OVERRIDES)
        for topic in sorted(changed):
            for variant in ("accessible", "full"):
                paths = list(TRACK.glob(f"*-{variant}/lessons/{topic:02d}-*/lesson.html"))
                self.assertEqual(len(paths), 1, (topic, variant))
                source = paths[0].read_text(encoding="utf-8")
                self.assertIn('<meta name="podo:proofread-status" content="pending">', source)

    def test_balance_game_generator_matches_committed_decks(self):
        import generate_ft_balance_games_batch as generator

        retired_prompt = "Ask your tutor which option " + "they would choose and why."
        for topic in generator.TOPIC_NUMBERS:
            for variant in generator.VARIANTS:
                with self.subTest(topic=topic, variant=variant):
                    built = generator.build(topic, variant)
                    committed = generator.output_path(topic, variant).read_text(encoding="utf-8")
                    self.assertNotIn(retired_prompt, built)
                    self.assertEqual(built, committed)

    def test_preserved_hand_authored_pairs_match_their_content_locks(self):
        import generate_ft_course_batch
        import generate_ft_me_lately_batch
        import generate_ft_people_and_ties_batch

        generate_ft_course_batch.verify_preserved_ft7()
        generate_ft_me_lately_batch.verify_preserved_ft9()
        generate_ft_people_and_ties_batch.assert_preserved()


if __name__ == "__main__":
    unittest.main()
