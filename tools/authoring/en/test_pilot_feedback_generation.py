#!/usr/bin/env python3
"""Keep every English generator on the owner-approved pilot operating contract."""

from __future__ import annotations

import importlib
import pathlib
import re
import sys
import unittest


TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import check_deck


class PilotFeedbackGenerationTests(unittest.TestCase):
    def test_every_generated_lesson_uses_the_approved_operating_contract(self):
        generated = 0
        for path in sorted(TOOLS.glob("generate_*_batch.py")):
            if path.stem.startswith("generate_core"):
                track = "core"
            elif path.stem.startswith("generate_contextual"):
                track = "contextual"
            elif path.stem.startswith("generate_ft"):
                track = "freetalking"
            else:
                continue

            module = importlib.import_module(path.stem)
            if hasattr(module, "LESSONS"):
                cases = (
                    (number, module.build(number, data)[1])
                    for number, data in module.LESSONS.items()
                )
            else:
                cases = (
                    (f"{number}-{variant}", module.build(number, variant))
                    for number in module.TOPICS
                    for variant in ("accessible", "full")
                )

            for identity, source in cases:
                generated += 1
                issues = check_deck.pilot_operating_issues(
                    dict(check_deck.pages(source)), track=track
                )
                self.assertEqual(issues, [], f"{path.stem} {identity}")

        self.assertEqual(generated, 411)

    def test_core_13_keeps_real_choice_value_and_visible_open_frames(self):
        core = importlib.import_module("generate_core_course_batch")
        source = core.build(13, core.LESSONS[13])[1]
        pages = dict(check_deck.pages(source))

        self.assertIn("Do you ___?", pages["p1-write"])
        self.assertIn("Do you cook at home?", pages["p2-write"])
        self.assertEqual(pages["p1-choose"].count("data-correct>Do you</span>"), 2)
        self.assertEqual(pages["p1-choose"].count("data-correct>Are you</span>"), 2)
        self.assertEqual(
            re.findall(r'data-answer="([^"]+)"', pages["p1-fill"]),
            ["Do you"] * 4,
        )
        self.assertEqual(
            check_deck.controlled_target_alignment_issues(pages),
            [],
        )
        self.assertIn('data-scaffolding-contract="target-v2"', pages["p1-translate"])
        self.assertIn('data-support-stage="supported"', pages["p2-translate"])
        self.assertIn("毎朝:every morning", pages["p2-translate"])
        self.assertNotIn(">am<", pages["p2-choose"])
        self.assertEqual(pages["p2-choose"].count("data-correct>do</span>"), 2)
        self.assertEqual(pages["p2-choose"].count("data-correct>don&#x27;t</span>"), 2)
        self.assertGreaterEqual(pages["p3-freetalk"].count('class="turn '), 4)
        self.assertIn("What habit would you like to change?", pages["p3-freetalk"])

    def test_contextual_2_uses_roleplay_visual_rules_and_reciprocal_free_talk(self):
        contextual = importlib.import_module("generate_contextual_course_batch")
        source = contextual.build(2, contextual.LESSONS[2])[1]
        pages = dict(check_deck.pages(source))

        self.assertIn("Let&#x27;s role-play passport control.", pages["scene"])
        self.assertIn('class="bt-box"', pages["p1-rule"])
        self.assertIn('class="bt-box"', pages["p2-rule"])
        self.assertEqual(
            re.findall(r'data-answer="([^"]+)"', pages["p1-fill"]),
            ["I&#x27;m here for"] * 4,
        )
        self.assertEqual(
            re.findall(r'data-answer="([^"]+)"', pages["p2-fill"]),
            ["I&#x27;m staying at"] * 4,
        )
        self.assertEqual(
            check_deck.controlled_target_alignment_issues(pages),
            [],
        )
        self.assertIn("結婚式:wedding", pages["p1-translate"])
        self.assertIn("友人の家:friend&#x27;s place", pages["p2-translate"])
        self.assertGreaterEqual(pages["p3-freetalk"].count('class="turn '), 4)
        self.assertIn("Which question would be hardest for you?", pages["p3-freetalk"])


if __name__ == "__main__":
    unittest.main()
