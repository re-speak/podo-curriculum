#!/usr/bin/env python3
"""Regression contract for the explicit CORE-71--80 course batch."""

from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_course_batch as shared_core
import generate_core_work_and_arrangements_batch as batch
import vocabulary


EXPECTED = set(range(71, 81))


class CoreWorkAndArrangementsBatchTests(unittest.TestCase):
    @staticmethod
    def category_words(number, category):
        return {entry.split("|", 1)[0].casefold() for entry in filter(None, batch.VOCAB[number][category].split("; "))}

    @classmethod
    def owned_words(cls, number):
        return set().union(*(cls.category_words(number, category) for category in ("new", "recycled", "assumed", "receptive")))

    @staticmethod
    def source_new_words(review_id):
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            if check_deck.meta_content(source, "podo:review-id") == review_id:
                return {entry.split("|", 1)[0].casefold() for entry in filter(None, check_deck.meta_content(source, "podo:vocabulary:new").split("; "))}
        raise AssertionError(f"missing owner deck {review_id}")

    def test_batch_source_is_complete_and_explicit(self):
        for values in (batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS, batch.TRANSLATE_HINTS, batch.OPEN_MENUS, batch.SUPPORT_EXPRESSIONS, batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS, batch.TRANSFER_SCENES, batch.DIALOGUE_SEMANTIC_LEDGER):
            self.assertEqual(set(values), EXPECTED)
        for number, categories in batch.VOCAB.items():
            self.assertEqual(set(categories), {"new", "recycled", "assumed", "receptive"}, number)
            self.assertLessEqual(len(self.category_words(number, "new")), 8, number)

    def test_semantic_specs_own_every_nonmechanical_decision(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["choices"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual(len(spec["tip"]), 6, number)
            for english, japanese in spec["meanings"] + spec["writes"]:
                self.assertTrue(english.strip() and japanese.strip(), number)

    def test_choices_are_smallest_nonempty_units_or_explicitly_omitted(self):
        for number, spec in batch.SPECS.items():
            omitted = set(batch.LESSONS[number].get("omit_choice", ()))
            for part, rows in enumerate(spec["choices"], start=1):
                if part in omitted:
                    self.assertEqual(rows, (), (number, part))
                    continue
                self.assertEqual(len(rows), 4, (number, part))
                for japanese, prefix, correct, distractor, suffix in rows:
                    self.assertIn("{t}", japanese, (number, part, japanese))
                    self.assertTrue(correct.strip() and distractor.strip(), (number, part))
                    self.assertNotEqual(correct, distractor, (number, part))
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertLessEqual(len(distractor.split()), 3, (number, part, distractor))
                    rebuilt = prefix + correct + suffix
                    self.assertRegex(rebuilt, r"^[A-Z].*[.!?]$")

    def test_reorders_use_four_units_except_documented_source_justifications(self):
        exceptions = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                shared_core.validate_reorder_pattern(data[f"p{part}"])
                counts = {len(row[2].split("|")) for row in data[f"p{part}"]}
                self.assertEqual(len(counts), 1, (number, part, counts))
                count = counts.pop()
                if count == 3:
                    exceptions.add((number, part))
                else:
                    self.assertEqual(count, 4, (number, part))
        self.assertEqual(exceptions, set(batch.THREE_CHIP_EXCEPTIONS))
        for reason in batch.THREE_CHIP_EXCEPTIONS.values():
            self.assertGreaterEqual(len(reason.split()), 7)

    def test_vocabulary_hints_known_words_and_provenance_are_honest(self):
        for number in EXPECTED:
            _, deck = batch.build(number, batch.LESSONS[number])
            vocabulary.parse(deck, source=f"CORE-{number}")
            self.assertTrue(vocabulary.hint_words(deck) <= self.owned_words(number), number)
            allowed_known = self.category_words(number, "assumed") | self.category_words(number, "recycled")
            for _, english in batch.KNOWN_WORDS[number]:
                self.assertIn(english.casefold(), allowed_known, (number, english))
            for entry in filter(None, batch.VOCAB[number]["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                owner_number = int(owner.removeprefix("CORE-"))
                self.assertLess(owner_number, number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))

    def test_every_new_item_is_in_a_learner_production_source(self):
        for number, data in batch.LESSONS.items():
            dialogue = batch.DIALOGUES[number]
            live_inputs = tuple(turn[3] for turn in batch.LIVE_SCENES[number] if turn[0] == "input")
            production_source = " ".join(
                str(value)
                for value in (
                    data["p1"],
                    data["p2"],
                    batch.SPECS[number]["choices"],
                    dialogue["model"][6],
                    dialogue["wild"][6],
                    live_inputs,
                )
            ).casefold()
            for word in self.category_words(number, "new"):
                self.assertIn(word, production_source, (number, word))

    def test_exact_brief_models_and_support_are_learner_visible(self):
        for number, data in batch.LESSONS.items():
            _, deck = batch.build(number, data)
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", deck))
            for part in (1, 2):
                self.assertIn(shared_core.strip_marks(data[f"p{part}"][0][0]), visible, (number, part))
            support = dict(check_deck.pages(deck))["supporting-expressions"]
            support_visible = html_lib.unescape(re.sub(r"<[^>]+>", "", support))
            for english, japanese in batch.SUPPORT_EXPRESSIONS[number]:
                self.assertIn(english, support_visible, (number, english))
                self.assertIn(japanese, support_visible, (number, japanese))

    def test_planned_spirals_are_visible_at_exact_modes(self):
        expected = {
            71: (("MODAL-01", "contrast"),),
            72: (("PERF-01", "contrast"), ("MODAL-01", "transfer")),
            73: (("PERF-01", "transfer"), ("ASPECT-02", "transfer")),
            74: (("REPORT-01", "controlled"),),
            75: (("ASPECT-01", "checkpoint"), ("DO-01", "transfer")),
            77: (("PERF-01", "transfer"),),
            78: (("ASPECT-02", "contrast"), ("MODAL-01", "transfer")),
            80: (("ASPECT-02", "checkpoint"), ("PREP-01", "transfer")),
        }
        self.assertEqual({n: tuple((row[0], row[1]) for row in rows) for n, rows in batch.SPIRALS.items()}, expected)
        for number, markers in expected.items():
            _, deck = batch.build(number, batch.LESSONS[number])
            for spiral_id, level in markers:
                self.assertIn(f'data-spiral-id="{spiral_id}"', deck)
                self.assertIn(f'data-spiral-level="{level}"', deck)

    def test_live_exchange_is_audio_safe_static_ask_back_and_truthful(self):
        roles = (("text", "other", "Tutor"), ("input", "me", "Me"), ("text", "me", "Me"), ("input", "other", "Tutor"))
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), roles, number)
            self.assertIn(" / ", scene[1][3], number)
            self.assertIn("／", scene[1][4], number)
            self.assertTrue(any(token in scene[1][3] for token in ("No,", "Nothing", "I can't", "I don't")), number)
            self.assertTrue(scene[2][3].endswith("?"), number)
            _, deck = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(deck))["p3-freetalk"]
            self.assertEqual(page.count('class="turn '), 4, number)
            self.assertEqual(page.count("Tutor&#x27;s answer:"), 1, number)
            self.assertIn('data-sync-id="live-1"', page, number)
            self.assertIn('data-sync-id="live-3"', page, number)

    def test_model_completion_and_transfer_are_resolved_six_turn_scenes(self):
        for number, data in batch.LESSONS.items():
            _, deck = batch.build(number, data)
            pages = dict(check_deck.pages(deck))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)
            for variant, ledger in batch.DIALOGUE_SEMANTIC_LEDGER[number].items():
                self.assertEqual(len(ledger), 6, (number, variant))
                self.assertTrue(all(len(purpose.split()) >= 2 for purpose in ledger), (number, variant))
                final = batch.DIALOGUES[number][variant][6][0]
                p1 = shared_core.strip_marks(data["p1"][batch.DIALOGUES[number][variant][1]][0])
                p2 = shared_core.strip_marks(data["p2"][batch.DIALOGUES[number][variant][2]][0])
                self.assertNotIn(final, {p1, p2}, (number, variant))

    def test_key_l1_and_semantic_contrasts_are_source_locked(self):
        self.assertIn("/ʃʊdəv/", batch.SPECS[71]["tip"][2])
        self.assertIn("not a past obligation", batch.LESSONS[72]["rules"][1][0])
        self.assertIn("Your key isn't here", batch.DIALOGUES[72]["model"][3][0])
        self.assertIn("earlier event", batch.LESSONS[73]["rules"][0][0])
        self.assertIn("train had left and the shop had closed", batch.DIALOGUES[73]["model"][5][0])
        self.assertIn("REPORT-01", str(batch.SPIRALS[74]))
        self.assertIn("no longer true", batch.LESSONS[75]["rules"][0][0])
        self.assertNotIn("get someone to", str(batch.LESSONS[76]).casefold())
        self.assertIn("Use had plus", batch.LESSONS[76]["rules"][0][0])
        self.assertIn("need to get", batch.LESSONS[76]["rules"][1][0])
        self.assertIn("calmly stating the expectation", batch.LESSONS[77]["rules"][1][0])
        self.assertEqual(batch.DIALOGUES[77]["model"][0], "Repair clerk")
        self.assertEqual(batch.DIALOGUES[77]["wild"][0], "Delivery clerk")
        self.assertIn("future time anchor", batch.LESSONS[78]["rules"][0][0])
        self.assertIn("not advice or regret", batch.LESSONS[79]["rules"][0][0])
        self.assertEqual(batch.VOCAB[79]["new"], "")
        self.assertNotIn("estimate", batch.DIALOGUES[79]["wild"][6][0].casefold())
        self.assertIn("present form after once", batch.LESSONS[80]["rules"][0][0])

    def test_round_two_semantic_repairs_are_source_locked(self):
        # CORE75: the contrast always owns an action and tests only don't/didn't.
        self.assertEqual(batch.LESSONS[75]["p2"][0][0], "I {t}don't walk to school{/t} anymore.")
        self.assertNotIn("I {t}don't{/t} anymore.", str(batch.LESSONS[75]))
        self.assertNotIn("する:do", str(batch.TRANSLATE_HINTS[75]))
        for _, prefix, correct, distractor, suffix in batch.SPECS[75]["choices"][1]:
            self.assertEqual((prefix, correct, distractor), ("I ", "don't", "didn't"))
            self.assertRegex(suffix, r"^ .+ anymore\.$")

        # CORE77: no false contraction binary; by + time remains one meaning unit.
        self.assertEqual(batch.SPECS[77]["choices"][1], ())
        self.assertIn(2, batch.LESSONS[77]["omit_choice"])
        self.assertNotIn("what happened", str(batch.SPECS[77]["choices"]).casefold())
        self.assertIn("by noon", batch.LESSONS[77]["p1"][2][2].split("|"))
        self.assertIn("by six", batch.LESSONS[77]["p1"][3][2].split("|"))
        self.assertIn("Was an order or repair ever late?", batch.LIVE_SCENES[77][2][3])

        # CORE78: preserve the established US-spelling owner and make the question answerable.
        self.assertNotIn("travelling", str((batch.LESSONS[78], batch.SPECS[78], batch.VOCAB[78], batch.TRANSLATE_HINTS[78], batch.LIVE_HINTS[78], batch.SPIRALS[78])))
        self.assertIn("traveling|移動中|CORE-27", batch.VOCAB[78]["recycled"])
        self.assertIn("Will you be home by six?", batch.DIALOGUES[78]["model"][4][0])

        # CORE79: omit the false should/will choice and scaffold the actual model word.
        self.assertEqual(batch.SPECS[79]["choices"][0], ())
        self.assertIn(1, batch.LESSONS[79]["omit_choice"])
        self.assertNotIn("追加の:extra", str(batch.TRANSLATE_HINTS[79]))
        self.assertIn("さらに:another", str(batch.TRANSLATE_HINTS[79]))
        self.assertEqual(batch.hint_html(batch.OPEN_MENUS[79][1]).count("さらに:another"), 1)
        self.assertIn("client may ask for changes", batch.DIALOGUES[79]["model"][4][0].casefold())
        self.assertIn("supplier may be late", batch.DIALOGUES[79]["wild"][4][0].casefold())

        # CORE80 owns ready and both repaired scenes preserve one explicit dependency.
        self.assertIn("ready|準備できた", batch.VOCAB[80]["new"])
        self.assertNotIn("ready|準備できた", batch.VOCAB[80]["assumed"])
        self.assertIn("final file isn't ready", batch.DIALOGUES[80]["model"][3][0].casefold())
        self.assertIn("file is ready", batch.DIALOGUES[80]["model"][5][0].casefold())
        self.assertEqual(batch.DIALOGUES[80]["wild"][2], 1)
        self.assertIn("when it arrives", batch.DIALOGUES[80]["wild"][4][0].casefold())

    def test_live_blank_order_and_known_word_bridges_are_honest(self):
        self.assertIn("___を___までに", batch.LIVE_SCENES[79][1][4])
        self.assertIn("___を___までに", batch.LIVE_SCENES[79][3][4])
        self.assertIn("___します。___したら", batch.LIVE_SCENES[80][1][4])
        self.assertIn("___します。___したら", batch.LIVE_SCENES[80][3][4])
        banned = {"トレイン", "クック", "ブック", "サンデー", "フォン"}
        actual = {japanese for number in range(71, 81) for japanese, _ in batch.KNOWN_WORDS[number]}
        self.assertFalse(actual & banned)
        self.assertEqual(batch.KNOWN_WORDS[72], (("バッグ", "bag"), ("キー", "key"), ("ドア", "door")))
        self.assertEqual(batch.KNOWN_WORDS[74], (("レポート", "report"), ("カレンダー", "calendar"), ("レストラン", "restaurant")))
        self.assertEqual(batch.KNOWN_WORDS[75][-1], ("テニス", "tennis"))
        self.assertEqual(batch.KNOWN_WORDS[76][0], ("バッテリー", "battery"))

    def test_generated_decks_match_source_and_are_complete(self):
        self.assertEqual(batch.PROOFREAD_STATUS, "complete")
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete", number)
            self.assertEqual(len(re.findall(r'<meta name="podo:proofread-status" content="[^"]+">', expected)), 1, number)

    def test_transfer_scenes_are_unique(self):
        scenes = list(batch.TRANSFER_SCENES.values())
        self.assertEqual(len(scenes), len(set(scenes)))


if __name__ == "__main__":
    unittest.main()
