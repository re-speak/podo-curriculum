from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_freetalk_questions


class PromptSemanticWarningTests(unittest.TestCase):
    def test_abstract_unowned_prompt_is_reported_for_human_review(self):
        warnings = check_freetalk_questions.prompt_warnings(
            "en", "What can make a useful item stop feeling worth it?"
        )
        self.assertEqual(len(warnings), 1)
        self.assertIn("indefinite subject with no established referent", warnings[0])

    def test_personal_prompt_passes_the_grounding_heuristic(self):
        self.assertEqual(
            check_freetalk_questions.prompt_warnings(
                "en", "What have you bought that was really worth the money?"
            ),
            [],
        )

    def test_established_referent_passes_without_forcing_you(self):
        self.assertEqual(
            check_freetalk_questions.prompt_warnings("en", "When do you use it most?"),
            [],
        )

    def test_direct_opinion_question_does_not_need_you(self):
        self.assertEqual(
            check_freetalk_questions.prompt_warnings(
                "en", "Which kind of friendship is harder to maintain?"
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
