#!/usr/bin/env python3
"""Tests for the scene-echo check.

Fixtures are inline rather than corpus paths on purpose: the corpus is edited
every week, and a test that reads it fails for reasons that have nothing to do
with the rule being tested.

    python3 -m unittest tools.authoring.test_check_scene_moves
"""
from __future__ import annotations

import unittest

from tools.authoring.check_scene_moves import asked, echoes, stems, turns

TURN = ('<div class="turn {who}"><span class="who"><span class="who-name">{nm}</span></span>'
        '<div class="bubble"><span class="korean">{ko}</span>'
        '<span class="translation">{ja}</span></div></div>')


def deck(*lines: tuple[str, str]) -> str:
    body = "".join(TURN.format(who="other" if i % 2 == 0 else "me", nm="친구" if i % 2 == 0 else "나",
                               ko=ko, ja=ja) for i, (ko, ja) in enumerate(lines))
    return ('<div class="section" data-page-id="scene"><div class="dialogue">' + body +
            '</div></div><div class="section" data-page-id="p3-model"><div class="dialogue">'
            + body + '</div></div>')


class SceneEchoTest(unittest.TestCase):
    def test_reads_only_the_canonical_scene(self):
        """p3-model and the teaser replay the scene; reporting it four times helps nobody."""
        html = deck(("소문 들었어?", "噂聞いた？"), ("응 들었어.", "うん聞いた。"))
        self.assertEqual(2, len(turns(html)))

    def test_flags_a_turn_that_relays_back_what_it_was_just_told(self):
        html = deck(
            ("너 그 둘 소문 들었어? 결국 헤어졌다는 얘기가 있던데.", "あの二人の噂聞いた？"),
            ("너 그 소문 들었어? 걔네 헤어졌대.", "その噂聞いた？"),
        )
        found = list(echoes(html))
        self.assertEqual(1, len(found), found)
        turn_no, _, _, shared = found[0]
        self.assertEqual(2, turn_no)
        self.assertIn("소문", shared)

    def test_an_answer_may_reuse_its_question_s_words(self):
        """Q→A echo is what answering looks like, not a defect."""
        html = deck(
            ("남은 음식 포장해 드릴까요?", "残りをお包みしましょうか？"),
            ("네, 남은 음식 포장해 주세요.", "はい、包んでください。"),
        )
        self.assertEqual([], list(echoes(html)))

    def test_ordinary_conversation_is_left_alone(self):
        html = deck(
            ("오늘따라 조용하네. 무슨 일 있어?", "今日は静かだね。"),
            ("너 그 소문 들었어? 걔네 헤어졌대.", "その噂聞いた？"),
            ("진짜? 너는 어떻게 생각했는데?", "本当？"),
        )
        self.assertEqual([], list(echoes(html)))

    def test_short_turns_never_trip_it(self):
        html = deck(("응.", "うん。"), ("응.", "うん。"))
        self.assertEqual([], list(echoes(html)))

    def test_stems_collapse_korean_inflection(self):
        self.assertIn("헤어", stems("결국 헤어졌다는 얘기가 있던데"))
        self.assertIn("헤어", stems("걔네 헤어졌대"))

    def test_stems_drop_english_function_words(self):
        got = stems("The handoff was missed again")
        self.assertIn("handoff", got)
        self.assertIn("missed", got)
        self.assertNotIn("the", got)

    def test_works_on_an_english_deck(self):
        """Both corpora put the target-language line in .korean, whatever it is."""
        html = deck(
            ("The handoff was missed again by the team.", "引き継ぎが抜けました。"),
            ("The handoff was missed again.", "引き継ぎが抜けました。"),
        )
        self.assertEqual(1, len(list(echoes(html))))

    def test_asked_recognises_both_question_marks(self):
        self.assertTrue(asked("들었어?"))
        self.assertTrue(asked("聞いた？"))
        self.assertFalse(asked("들었어."))


if __name__ == "__main__":
    unittest.main()
