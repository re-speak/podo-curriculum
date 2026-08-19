#!/usr/bin/env python3
"""Regression tests for validator-visible controls emitted by the renderer."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import render_contextual_course as renderer


class StaticControlTests(unittest.TestCase):
    def test_inline_slot_is_a_real_input(self):
        control = renderer.slot_input("p1-fill", "정답")
        self.assertIn('<input class="slot-input"', control)
        self.assertIn('data-sync-id="p1-fill"', control)
        self.assertIn('data-answer="정답"', control)
        self.assertNotIn('<span class="slot"', control)

    def test_exact_and_open_answers_use_real_controls(self):
        exact = renderer.answer_input("translate", "문장")
        open_answer = renderer.answer_input("free")
        self.assertIn('<input class="space-input"', exact)
        self.assertIn('data-answer="문장"', exact)
        self.assertIn('<textarea class="free-input"', open_answer)

    def test_spoken_response_uses_shared_feedback_activity(self):
        control = renderer.feedback_activity("p1-write-answer", "自分の話 & 例")
        self.assertIn('class="fb-compose"', control)
        self.assertIn('class="fb" data-fb="p1-write-answer"', control)
        self.assertIn('<span class="fb-task">自分の話 &amp; 例</span>', control)
        self.assertIn('class="fb-add" data-add="fix"', control)
        self.assertIn('class="fb-add" data-add="note"', control)
        self.assertNotIn('textarea class="free-input"', control)

    def test_reorder_kind_is_visible_without_javascript(self):
        control = renderer.build_zone("order", "문장")
        self.assertIn('class="answer-space build-zone"', control)
        self.assertIn('data-sync-kind="order"', control)
        self.assertIn('data-a="문장"', control)


if __name__ == "__main__":
    unittest.main()
