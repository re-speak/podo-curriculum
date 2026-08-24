#!/usr/bin/env python3
"""The correct option must not land where a learner can predict it."""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import option_order


class CorrectSlotTests(unittest.TestCase):
    def test_same_key_always_gives_the_same_page(self):
        for count in range(3, 9):
            self.assertEqual(
                option_order.correct_slots("CORE-20-p1-choose", count),
                option_order.correct_slots("CORE-20-p1-choose", count),
            )

    def test_never_constant_and_never_alternating(self):
        for count in range(3, 9):
            for number in range(400):
                slots = option_order.correct_slots(f"CTX-{number}-p{number % 2}-choose", count)
                self.assertEqual(len(slots), count)
                self.assertGreater(len(set(slots)), 1, (number, count, slots))
                self.assertFalse(
                    all(a != b for a, b in zip(slots, slots[1:])),
                    (number, count, slots),
                )

    def test_both_options_are_used_somewhere_on_the_page(self):
        for number in range(200):
            slots = option_order.correct_slots(f"key-{number}", 4)
            self.assertEqual({0, 1}, set(slots), (number, slots))

    def test_different_pages_of_one_deck_differ(self):
        seen = {
            tuple(option_order.correct_slots(f"CORE-20-p{part}-choose", 4))
            for part in range(1, 3)
        }
        self.assertEqual(len(seen), 2)

    def test_two_rows_cannot_establish_a_pattern_so_are_left_alone(self):
        self.assertEqual(option_order.correct_slots("anything", 2), [0, 1])
        self.assertEqual(option_order.correct_slots("anything", 1), [0])

    def test_the_candidate_set_excludes_exactly_the_learnable_shapes(self):
        four = option_order._candidates(4)
        self.assertEqual(len(four), 16 - 4)
        for banned in ((0, 0, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0)):
            self.assertNotIn(banned, four)


if __name__ == "__main__":
    unittest.main()
