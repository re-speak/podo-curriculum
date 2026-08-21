#!/usr/bin/env python3
"""Regression contract for the explicit Core 1-11 course batch."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_course_batch as shared_core
import generate_core_first_exchanges_1_batch as batch


EXPECTED_KNOWN_WORDS = {
    1: (("ハロー", "hello"), ("デザイナー", "designer"), ("エンジニア", "engineer")),
    2: (("東京", "Tokyo"), ("大阪", "Osaka"), ("カナダ", "Canada")),
    3: (("バッグ", "bag"), ("トレイン", "train"), ("オーケー", "okay")),
    7: (("カフェ", "café"), ("ホテル", "hotel"), ("ステーション", "station")),
    8: (("ホット", "hot"), ("レイニー", "rainy"), ("トゥデイ", "today")),
    9: (("コーヒー", "coffee"), ("チケット", "ticket"), ("バッグ", "bag")),
    10: (("カフェ", "café"), ("レストラン", "restaurant"), ("バンク", "bank")),
    11: (("ステーション", "station"), ("ホテル", "hotel"), ("カフェ", "café")),
}


SUPPORT_FINALS = {
    1: "Nice to meet you.",
    2: "That's right.",
    3: "Okay.",
    7: "That's right.",
    8: "Not really.",
    9: "That's all, thanks.",
    10: "Yes, the same one.",
    11: "It's about five minutes.",
}


class CoreFirstExchangesOneBatchTests(unittest.TestCase):
    @staticmethod
    def category_words(number, category):
        return {
            entry.split("|", 1)[0].casefold()
            for entry in batch.VOCAB[number][category].split("; ")
            if entry
        }

    @staticmethod
    def owned_words(number):
        words = set()
        for category, value in batch.VOCAB[number].items():
            for entry in filter(None, value.split("; ")):
                parts = entry.split("|")
                assert len(parts) == (3 if category == "recycled" else 2), entry
                words.add(parts[0].casefold())
        return words

    def test_course_batch_is_complete_and_explicit(self):
        expected = {1, 2, 3, 7, 8, 9, 10, 11}
        self.assertEqual(set(batch.LESSONS), expected)
        self.assertEqual(set(batch.SPECS), expected)
        self.assertEqual(set(batch.DIALOGUES), expected)
        self.assertEqual(set(batch.LIVE_SCENES), expected)
        self.assertEqual(set(batch.VOCAB), expected)
        for number, categories in batch.VOCAB.items():
            self.assertEqual(
                set(categories), {"new", "recycled", "assumed", "receptive"}, number
            )

    def test_all_choices_are_smallest_unit_and_specs_are_complete(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            for part, rows in enumerate(spec["choices"], start=1):
                if part in batch.LESSONS[number].get("omit_choice", ()):
                    self.assertIn(len(rows), {0, 4}, (number, part))
                else:
                    self.assertEqual(len(rows), 4, (number, part))
            for rows in spec["choices"]:
                for japanese, _, correct, distractor, _ in rows:
                    self.assertNotEqual(correct, distractor, number)
                    self.assertIn("{t}", japanese, (number, japanese))
                    self.assertNotIn(".", correct, (number, correct))

    def test_known_words_are_explicit_and_owned(self):
        self.assertEqual(batch.KNOWN_WORDS, EXPECTED_KNOWN_WORDS)
        for number, entries in batch.KNOWN_WORDS.items():
            self.assertEqual(len(entries), 3, number)
            owned = self.owned_words(number)
            for _, english in entries:
                self.assertIn(english.casefold(), owned, (number, english))
        disallowed = {"from", "behind", "actually", "quantity"}
        actual = {english.casefold() for entries in batch.KNOWN_WORDS.values() for _, english in entries}
        self.assertTrue(actual.isdisjoint(disallowed))

    def test_recycled_vocabulary_has_earlier_provenance(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, source = entry.split("|")
                self.assertTrue(word and japanese, (number, entry))
                self.assertTrue(source.startswith("CORE-"), (number, entry))
                source_number = int(source.removeprefix("CORE-"))
                self.assertLess(source_number, number, entry)
                source_new = {
                    source_entry.split("|", 1)[0].casefold()
                    for source_entry in batch.VOCAB[source_number]["new"].split("; ")
                    if source_entry
                }
                self.assertIn(word.casefold(), source_new, (number, entry))

    def test_reviewed_choice_cues_name_the_actual_decision(self):
        self.assertEqual(batch.LESSONS[1]["omit_choice"], (1, 2))
        self.assertEqual(batch.LESSONS[3]["omit_choice"], (1, 2))
        self.assertEqual(
            {shared_core.strip_marks(row[0]).split()[0] for row in batch.LESSONS[2]["p1"]},
            {"I'm", "He's", "She's", "They're"},
        )
        self.assertEqual(
            {row[2] for row in batch.SPECS[10]["choices"][1]},
            {"a", "The"},
        )
        for number, spec in batch.SPECS.items():
            for part, choices in enumerate(spec["choices"], start=1):
                if part not in batch.LESSONS[number].get("omit_choice", ()):
                    self.assertGreaterEqual(
                        len({row[2] for row in choices}), 2, (number, part)
                    )
                for _, prefix, correct, _, suffix in choices:
                    rebuilt = prefix + correct + suffix
                    self.assertTrue(rebuilt.strip(), (number, part))

    def test_reorders_are_honest_or_explicitly_omitted(self):
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part not in data.get("omit_reorder", ()):
                    shared_core.validate_reorder_pattern(data[f"p{part}"])

    def test_round_two_semantic_repairs_are_source_locked(self):
        self.assertEqual(batch.LESSONS[1]["omit_reorder"], (1, 2))
        self.assertTrue(all(len(row[2].split("|")) == 2 for row in batch.LESSONS[1]["p2"]))
        self.assertEqual(batch.LESSONS[3]["omit_reorder"], (1, 2))
        for variant in ("model", "wild"):
            weather_question = batch.DIALOGUES[8][variant][4][0]
            self.assertIn("Is it ", weather_question)
            self.assertNotIn("How is it", weather_question)

        for number in batch.LESSONS:
            prompt_en, prompt_ja = batch.LESSONS[number]["prompt"]
            self.assertTrue(prompt_en and prompt_ja, number)
            if number <= 3:
                self.assertEqual(batch.LIVE_SCENES[number][0][:2], ("text", "other"))
                self.assertEqual(batch.LIVE_SCENES[number][1][:2], ("input", "me"))
            else:
                self.assertEqual(batch.LIVE_SCENES[number][0][:2], ("input", "me"))
                self.assertIn("only if it fits naturally", batch.LIVE_SCENES[number][0][3])

        core10 = " ".join(
            shared_core.strip_marks(row[0]) for part in ("p1", "p2") for row in batch.LESSONS[10][part]
        )
        self.assertIn("restaurant near the station", core10)
        self.assertIn("restaurant is open until midnight", core10)
        self.assertNotIn("hotel is open until midnight", core10)

    def test_required_vocabulary_ownership_is_explicit(self):
        self.assertIn("now", self.category_words(2, "new"))
        self.assertTrue({"from", "friend", "coworker"} <= self.category_words(2, "new"))
        self.assertTrue({"bag", "key", "student", "ready"} <= self.category_words(3, "new"))
        self.assertIn("here", self.category_words(7, "new"))
        self.assertIn("really", self.category_words(8, "receptive"))
        self.assertTrue({"just", "please", "thanks"} <= self.category_words(9, "new"))
        self.assertIn("near", self.category_words(10, "recycled"))
        self.assertIn("that", self.category_words(10, "receptive"))

    def test_decks_match_generator_and_canonical_shape(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(
                check_deck.meta_content(expected, "podo:proofread-status"),
                "complete",
                number,
            )

    def test_transfer_intro_names_the_explicit_role_in_both_languages(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            model_role_en = batch.DIALOGUES[number]["model"][0].lower()
            for page_id in ("p3-model", "p3-complete"):
                self.assertIn(f"the {model_role_en}.", pages[page_id], (number, page_id))
                self.assertIn(
                    f'私は{batch.MODEL_ROLE_JA[number]}役をします。',
                    pages[page_id],
                    (number, page_id),
                )
                if batch.MODEL_ROLE_JA[number] != batch.TRANSFER_ROLE_JA[number]:
                    self.assertNotIn(
                        f'私は{batch.TRANSFER_ROLE_JA[number]}役をします。',
                        pages[page_id],
                        (number, page_id),
                    )

            page = pages["in-the-wild"]
            role_en = batch.DIALOGUES[number]["wild"][0].lower()
            self.assertIn(f"I’ll be the {role_en}.", page, number)
            self.assertIn(f'私は{batch.TRANSFER_ROLE_JA[number]}役をします。', page, number)
            if batch.MODEL_ROLE_JA[number] != batch.TRANSFER_ROLE_JA[number]:
                self.assertNotIn(f'私は{batch.MODEL_ROLE_JA[number]}役をします。', page, number)
            self.assertNotIn("同じ二つのパターンを別の会話で使いましょう。", page, number)
            self.assertRegex(page, r"Say each complete Me line, including the missing words\.")

    def test_model_and_completion_are_exact_six_turn_replays(self):
        for number, data in batch.LESSONS.items():
            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]),
                number,
            )

    def test_final_learner_lines_are_owned_current_patterns(self):
        for number, data in batch.LESSONS.items():
            allowed = {
                shared_core.strip_marks(row[0])
                for part in ("p1", "p2")
                for row in data[part]
            }
            for variant in ("model", "wild"):
                final, owner = batch.FINAL_LINE_OWNERSHIP[number][variant]
                self.assertEqual(final, batch.DIALOGUES[number][variant][6][0])
                if owner == f"CORE-{number} current pattern":
                    self.assertIn(final, allowed, (number, variant, final))
                else:
                    self.assertEqual(owner, batch.SUPPORT_LINE_OWNERS[number])
                    self.assertEqual(final, SUPPORT_FINALS[number])

    def test_productive_pages_include_explicit_vocabulary_scaffolds(self):
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                self.assertEqual(len(batch.TRANSLATE_HINTS[number][part - 1]), 4)
                stage = batch.TRANSLATE_STAGES[number][part - 1]
                if stage == "supported":
                    self.assertTrue(any(batch.TRANSLATE_HINTS[number][part - 1]))
                else:
                    self.assertEqual(stage, "checkpoint")
                    self.assertFalse(any(batch.TRANSLATE_HINTS[number][part - 1]))
                self.assertTrue(batch.OPEN_MENUS[number][part - 1])
            learner_input_indexes = {
                index
                for index, (kind, side, *_rest) in enumerate(batch.LIVE_SCENES[number])
                if kind == "input" and side == "me"
            }
            self.assertEqual(set(batch.LIVE_HINTS[number]), learner_input_indexes, number)
            self.assertTrue(all(batch.LIVE_HINTS[number].values()))
            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for part in (1, 2):
                translate = pages[f"p{part}-translate"]
                self.assertEqual(translate.count('class="task-block"'), 4, (number, part))
                self.assertIn('data-scaffolding-contract="target-v2"', translate)
                stage = batch.TRANSLATE_STAGES[number][part - 1]
                self.assertIn(f'data-support-stage="{stage}"', translate)
                if stage == "supported":
                    self.assertGreaterEqual(translate.count('class="hint"'), 1, (number, part))
                else:
                    self.assertNotIn('class="hint"', translate)
                self.assertIn('class="hint"', pages[f"p{part}-write"], (number, part))
            live = pages["p3-freetalk"]
            learner_inputs = live.count('class="turn me"')
            self.assertGreaterEqual(live.count('class="hint"'), 1, number)
            self.assertGreaterEqual(learner_inputs, 1, number)

    def test_removed_unowned_quantity_label(self):
        self.assertNotIn("quantity", " ".join(batch.VOCAB[9].values()).casefold())


if __name__ == "__main__":
    unittest.main()
