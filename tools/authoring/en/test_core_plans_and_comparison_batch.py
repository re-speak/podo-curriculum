#!/usr/bin/env python3
"""Regression contract for the source-first Core 37-47 authoring batch."""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_deck
import generate_core_course_batch as core
import generate_core_plans_and_comparison_batch as batch
import vocabulary


class CorePlansAndComparisonBatchTests(unittest.TestCase):
    def test_scope_is_exact_and_core45_is_byte_preserved(self):
        self.assertEqual(set(batch.NUMBERS), set(range(37, 48)) - {45})
        self.assertEqual(set(batch.LESSONS), set(batch.NUMBERS))
        preserved = batch.TRACK / "courses" / batch.COURSE / "lessons/45-this-ones-cheaper/lesson.html"
        self.assertEqual(
            hashlib.sha256(preserved.read_bytes()).hexdigest(),
            "2740d6f9e47294d3239e72395b940f132e35b298999c7de86a53693ff8eeb4a6",
        )

    def test_every_semantic_field_is_explicit(self):
        expected = set(batch.NUMBERS)
        for mapping in (
            batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS, batch.DIALOGUES,
            batch.LIVE_SCENES, batch.LIVE_HINTS, batch.TRANSLATE_HINTS,
            batch.TRANSLATE_STAGES, batch.OPEN_MENUS, batch.WRITE_PROMPTS,
            batch.FILL_HINTS,
        ):
            self.assertEqual(set(mapping), expected)
        for number in batch.NUMBERS:
            self.assertEqual(set(batch.VOCAB[number]), {"new", "recycled", "assumed", "receptive"})
            self.assertEqual(len(batch.SPECS[number]["meanings"]), 2)
            self.assertEqual(batch.SPECS[number]["writes"], batch.WRITE_PROMPTS[number])
            self.assertEqual(batch.SPECS[number]["fill_hints"], batch.FILL_HINTS[number])
            self.assertEqual(len(batch.SPECS[number]["rules"]), 2)
            self.assertEqual(len(batch.SPECS[number]["choices"]), 2)

    def test_authoritative_models_and_titles_are_locked(self):
        expected = {
            37: ("I'm going to look for a new job", "I'm going to look for a new job.", "What are you going to do about it?"),
            38: ("Let me help", "Let me carry that for you.", "Don’t worry, I’ll send it by noon."),
            39: ("I might be late", "I might be a bit late.", "If you are, I’ll wait outside."),
            40: ("You should get some rest", "You should get some rest.", "If it gets worse, you need to see a doctor."),
            41: ("You have to show ID", "You have to show your ID.", "But you don't have to book ahead."),
            42: ("Don't you like it?", "Actually, I do. I watch it every week.", "No, I don’t. I prefer comedies."),
            43: ("It's a small, quiet café", "It’s a small, quiet place.", "It’s near the station."),
            44: ("It's too small", "It’s too small for me.", "This one isn’t big enough."),
            46: ("It's the best one here", "It’s the best one here.", "I prefer this one to that one."),
            47: ("I was bored during the movie", "I was bored during the movie.", "The movie was really boring."),
        }
        for number, (title, p1, p2) in expected.items():
            data = batch.LESSONS[number]
            self.assertEqual(data["title"], title)
            self.assertEqual(core.strip_marks(data["p1"][0][0]), p1)
            self.assertEqual(core.strip_marks(data["p2"][0][0]), p2)

    def test_open_production_and_free_talk_follow_approved_workflow(self):
        for number in batch.NUMBERS:
            for english, japanese in batch.WRITE_PROMPTS[number]:
                self.assertTrue(english.startswith("Now use “"), (number, english))
                self.assertTrue(japanese.startswith("では、「"), (number, japanese))
                self.assertIn("___", english)
            prompt_en, prompt_ja = batch.LESSONS[number]["prompt"]
            self.assertIn("?", prompt_en, number)
            self.assertIn("？", prompt_ja, number)
            self.assertEqual(batch.LIVE_SCENES[number], (
                ("text", "other", "Tutor", prompt_en, prompt_ja),
                ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
                ("text", "me", "Me", "How about you?", "先生はどうですか？"),
                ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
            ))
            self.assertEqual(batch.LIVE_HINTS[number], {})

        expected_no_experience_prompts = {
            40: "When you're exhausted, what advice would you actually want to hear?",
            42: "What makes a yes-or-no answer confusing for you?",
            44: "What feature makes a purchase feel worth the money to you?",
            47: "Which gives you the strongest reaction: a movie, a game, or a trip? Why?",
        }
        for number, prompt in expected_no_experience_prompts.items():
            self.assertEqual(batch.LESSONS[number]["prompt"][0], prompt)

    def test_translation_and_fill_support_do_not_reveal_the_pattern(self):
        forbidden = {"going to", "let me", "might", "should", "have to", "don't have to", "too", "enough"}
        for number in batch.NUMBERS:
            self.assertEqual(batch.TRANSLATE_STAGES[number], ("supported", "supported"))
            for part in (0, 1):
                hints = batch.TRANSLATE_HINTS[number][part]
                self.assertEqual(len(hints), 4)
                self.assertTrue(any(hints), (number, part + 1))
                fill_hints = batch.FILL_HINTS[number][part]
                if fill_hints is not None:
                    self.assertEqual(len(fill_hints), 4)
                    for row in fill_hints:
                        pairs = (row,) if len(row) == 2 and all(isinstance(item, str) for item in row) else row
                        for _, english in pairs:
                            self.assertNotIn(english.casefold(), forbidden)

    def test_choice_pages_are_discriminating_or_intentionally_omitted(self):
        expected_omissions = {
            37: {1, 2}, 38: {1, 2}, 39: {2}, 40: {2}, 41: {1, 2},
            42: {1}, 43: {1, 2}, 44: {1}, 46: {2}, 47: set(),
        }
        for number, data in batch.LESSONS.items():
            self.assertEqual(set(data.get("omit_choice", ())), expected_omissions[number])
            for part in (1, 2):
                choices = batch.SPECS[number]["choices"][part - 1]
                if part in expected_omissions[number]:
                    self.assertEqual(choices, ())
                    continue
                self.assertEqual(len(choices), 4)
                correct_answers = set()
                for index, (japanese, prefix, correct, distractor, suffix) in enumerate(choices):
                    self.assertNotEqual(correct, distractor)
                    self.assertEqual(japanese.count("{t}"), 1)
                    correct_answers.add(correct.casefold())
                    if (number, part) != (42, 2):
                        target = core.strip_marks(data[f"p{part}"][index][0])
                        self.assertEqual(prefix + correct + suffix, target, (number, part, index))
                self.assertGreater(len(correct_answers), 1, (number, part, correct_answers))
        self.assertEqual({row[2].casefold() for row in batch.SPECS[42]["choices"][1]}, {"do", "don't"})

    def test_reorders_are_honest_or_explicitly_omitted(self):
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part not in data.get("omit_reorder", ()):
                    core.validate_reorder_pattern(data[f"p{part}"])

    def test_vocabulary_provenance_is_complete(self):
        for number in batch.NUMBERS:
            owned = set()
            self.assertLessEqual(len(list(filter(None, batch.VOCAB[number]["new"].split("; ")))), 8)
            for category, value in batch.VOCAB[number].items():
                for entry in filter(None, value.split("; ")):
                    pieces = entry.split("|")
                    self.assertEqual(len(pieces), 3 if category == "recycled" else 2, (number, entry))
                    owned.add(pieces[0].casefold())
                    if category == "recycled":
                        source_id = pieces[2]
                        self.assertLess(int(source_id.removeprefix("CORE-")), number, (number, entry))
                        source = next(path for path in batch.TRACK.rglob("lesson.html") if f'content="{source_id}"' in path.read_text(encoding="utf-8"))
                        source_new = {item["english"].casefold() for item in vocabulary.parse(source.read_text(encoding="utf-8"))["categories"]["new"]}
                        self.assertIn(pieces[0].casefold(), source_new, (number, entry))
            for _, english in batch.KNOWN_WORDS[number]:
                self.assertIn(english.casefold(), owned)

        self.assertNotIn("printer|", batch.VOCAB[38]["new"])
        self.assertIn("entrance|入口", batch.VOCAB[41]["receptive"])
        self.assertIn("carry-on|機内持ち込み手荷物", batch.VOCAB[44]["receptive"])
        self.assertIn("bakery|パン屋", batch.VOCAB[46]["receptive"])

    def test_dialogues_are_exact_six_turn_replays(self):
        for number, data in batch.LESSONS.items():
            for variant in ("model", "wild"):
                dialogue = batch.DIALOGUES[number][variant]
                self.assertEqual(len(dialogue), 7)
                final, owner = batch.FINAL_LINE_OWNERSHIP[number][variant]
                self.assertEqual(final, dialogue[6][0], (number, variant))
                self.assertTrue(owner.strip())
            _, rendered = batch.build(number, data)
            pages = dict(check_deck.pages(rendered))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]))

    def test_generated_decks_are_exact_complete_and_canonical(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected)
            pages = dict(check_deck.pages(expected))
            omissions = set(data.get("omit_choice", ()))
            for part in (1, 2):
                self.assertEqual(f"p{part}-choose" in pages, part not in omissions, (number, part))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.phrase_input_structure_issues(expected), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete")
            self.assertEqual(len(re.findall(r'<meta name="podo:proofread-status"', expected)), 1)
            ids = re.findall(r'data-sync-id="([^"]+)"', expected)
            self.assertEqual(len(ids), len(set(ids)), number)


if __name__ == "__main__":
    unittest.main()
