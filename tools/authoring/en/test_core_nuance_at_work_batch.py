#!/usr/bin/env python3
"""Regression contract for the explicit missing CORE-81--91 batch."""

from __future__ import annotations

import hashlib
import html as html_lib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_course_batch as shared_core
import generate_core_nuance_at_work_batch as batch
import vocabulary

EXPECTED = set(batch.NUMBERS)
CORE82_SHA256 = "3d479dc2b3e4d87d64538ef19c7733f1939fff39252c298bc09fcf5b46a7e70a"


class CoreNuanceAtWorkBatchTests(unittest.TestCase):
    @staticmethod
    def category_words(number, category):
        return {
            entry.split("|", 1)[0].casefold()
            for entry in filter(None, batch.VOCAB[number][category].split("; "))
        }

    @classmethod
    def owned_words(cls, number):
        return set().union(*(cls.category_words(number, c) for c in batch.VOCAB[number]))

    @staticmethod
    def source_new_words(review_id):
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            if check_deck.meta_content(source, "podo:review-id") == review_id:
                return {
                    entry.split("|", 1)[0].casefold()
                    for entry in filter(
                        None,
                        check_deck.meta_content(source, "podo:vocabulary:new").split("; "),
                    )
                }
        raise AssertionError(f"missing visible owner deck {review_id}")

    def test_source_tables_cover_exactly_the_ten_missing_lessons(self):
        for values in (
            batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS, batch.OPEN_MENUS, batch.SUPPORT_EXPRESSIONS,
            batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS,
            batch.TRANSFER_SCENES, batch.BRIEF_PRODUCTION_MODELS,
            batch.DIALOGUE_SEMANTIC_LEDGER,
        ):
            self.assertEqual(set(values), EXPECTED)
        self.assertNotIn(82, EXPECTED)

    def test_identity_title_and_level_match_the_authoritative_briefs(self):
        for number, data in batch.LESSONS.items():
            brief = (batch.TRACK / "toc" / f"CORE-{number}.md").read_text(encoding="utf-8")
            self.assertTrue(brief.startswith(f"# CORE-{number} · {data['title']}\n"), number)
            _, source = batch.build(number, data)
            self.assertEqual(check_deck.meta_content(source, "podo:review-id"), f"CORE-{number}")
            self.assertEqual(check_deck.meta_content(source, "podo:title-en"), data["title"])
            self.assertEqual(
                check_deck.meta_content(source, "podo:level"),
                "B1+" if number <= 86 else "B2",
            )

    def test_core82_is_preserved_at_the_reviewed_byte_identity(self):
        source = batch.EXISTING_CORE82.read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), CORE82_SHA256)
        with self.assertRaises(ValueError):
            batch.build(82, {})

    def test_semantic_specs_are_fully_authored(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["choices"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual(len(spec["tip"]), 6, number)
            for english, japanese in spec["meanings"] + spec["writes"]:
                self.assertTrue(english.strip(), number)
                self.assertTrue(japanese.strip(), number)

    def test_smallest_unit_choices_are_explicit_and_solvable(self):
        for number, spec in batch.SPECS.items():
            for part, rows in enumerate(spec["choices"], 1):
                self.assertEqual(len(rows), 4, (number, part))
                for japanese, prefix, correct, distractor, suffix in rows:
                    self.assertIn("{t}", japanese, (number, part))
                    self.assertNotEqual(correct, distractor, (number, part))
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertLessEqual(len(distractor.split()), 3, (number, part, distractor))
                    rebuilt = prefix + correct + suffix
                    self.assertRegex(rebuilt, r"^[A-Z].*[.!?]$", (number, part, rebuilt))

    def test_reorders_are_four_units_or_have_an_explicit_reason(self):
        actual = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part in data.get("omit_reorder", ()):
                    actual.add((number, part))
                    continue
                shared_core.validate_reorder_pattern(data[f"p{part}"])
                counts = {len(row[2].split("|")) for row in data[f"p{part}"]}
                self.assertEqual(len(counts), 1, (number, part, counts))
                count = counts.pop()
                self.assertIn(count, (3, 4), (number, part, count))
                if count == 3:
                    actual.add((number, part))
        self.assertEqual(actual, set(batch.THREE_CHIP_EXCEPTIONS))
        for key, reason in batch.THREE_CHIP_EXCEPTIONS.items():
            self.assertGreaterEqual(len(reason.split()), 7, (key, reason))

    def test_vocabulary_metadata_is_parseable_and_all_hints_are_owned(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            vocabulary.parse(source, source=f"CORE-{number}")
            self.assertLessEqual(len(self.category_words(number, "new")), 8, number)
            self.assertTrue(vocabulary.hint_words(source) <= self.owned_words(number), number)

    def test_each_translation_hint_matches_its_own_source_row(self):
        surface_aliases = {"come": "came"}
        for number, parts in batch.TRANSLATE_HINTS.items():
            for part, hints in enumerate(parts, 1):
                rows = batch.LESSONS[number][f"p{part}"]
                self.assertEqual(len(hints), len(rows), (number, part))
                for row, hint in zip(rows, hints, strict=True):
                    sentence = shared_core.strip_marks(row[0]).casefold()
                    for item in hint.split("; "):
                        english = item.split(":", 1)[1].casefold()
                        expected = surface_aliases.get(english, english)
                        self.assertIn(expected, sentence, (number, part, sentence, hint))

    def test_known_words_are_assumed_or_genuinely_recycled(self):
        for number, entries in batch.KNOWN_WORDS.items():
            allowed = self.category_words(number, "assumed") | self.category_words(number, "recycled")
            forbidden = self.category_words(number, "new") | self.category_words(number, "receptive")
            self.assertEqual(len(entries), 3, number)
            for _, english in entries:
                self.assertIn(english.casefold(), allowed, (number, english))
                self.assertNotIn(english.casefold(), forbidden, (number, english))

    def test_recycled_words_have_real_visible_earlier_owners(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                self.assertLess(int(owner.removeprefix("CORE-")), number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))
        self.assertIn("prefer|より好む|CORE-42", batch.VOCAB[90]["recycled"])
        self.assertNotIn("prefer|より好む|CORE-63", batch.VOCAB[90]["recycled"])

    def test_new_words_are_used_in_learner_owned_source(self):
        for number in EXPECTED:
            learner_source = " ".join(map(str, (
                batch.LESSONS[number], batch.SPECS[number], batch.KNOWN_WORDS[number],
                batch.TRANSLATE_HINTS[number], batch.OPEN_MENUS[number],
                batch.LIVE_SCENES[number], batch.LIVE_HINTS[number],
            ))).casefold()
            for word in self.category_words(number, "new"):
                self.assertIn(word, learner_source, (number, word))

    def test_exact_brief_models_and_support_are_learner_visible(self):
        for number, models in batch.BRIEF_PRODUCTION_MODELS.items():
            _, source = batch.build(number, batch.LESSONS[number])
            pages = dict(check_deck.pages(source))
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", source))
            for model in models:
                self.assertIn(model, visible, (number, model))
            support = html_lib.unescape(re.sub(r"<[^>]+>", "", pages["supporting-expressions"]))
            for english, japanese in batch.SUPPORT_EXPRESSIONS[number]:
                self.assertIn(english, support, (number, english))
                self.assertIn(japanese, support, (number, japanese))

    def test_live_exchange_is_audio_safe_reciprocal_and_truthful(self):
        roles = (("text", "other", "Tutor"), ("input", "me", "Me"),
                 ("input", "me", "Me"), ("input", "other", "Tutor"))
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), roles, number)
            self.assertIn(" / ", scene[1][3], number)
            self.assertIn("／", scene[1][4], number)
            self.assertNotRegex(" ".join(turn[3] for turn in scene).casefold(), r"watch me|look at me|gesture")
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(page.count('class="turn '), 4, number)
            self.assertIn("Tutor&#x27;s answer:", page, number)

    def test_live_menus_fit_real_slots_and_do_not_decorate_fixed_ask_backs(self):
        expected_turns = {
            81: {1}, 83: {1, 2}, 84: {1, 2}, 85: {1},
            86: {1, 2}, 87: {1}, 88: {1, 2}, 89: {1},
            90: {1}, 91: {1, 2},
        }
        for number, hints in batch.LIVE_HINTS.items():
            self.assertEqual(set(hints), expected_turns[number], number)
            ask_back = batch.LIVE_SCENES[number][2][3]
            self.assertEqual(2 in hints, "___" in ask_back, (number, ask_back))
            for turn, menu in hints.items():
                self.assertGreaterEqual(len(menu), 3, (number, turn))

    def test_every_open_production_prompt_has_a_truthful_alternative(self):
        for number, spec in batch.SPECS.items():
            for english, japanese in spec["writes"]:
                self.assertIn(" or ", english, (number, english))
                self.assertIn("か", japanese, (number, japanese))
        for number, data in batch.LESSONS.items():
            self.assertIn(" or ", data["prompt"][0], number)
            self.assertIn("か", data["prompt"][1], number)

    def test_reviewer_found_live_branches_are_complete_and_audible(self):
        c84 = batch.LIVE_SCENES[84]
        self.assertIn("If I need the change:", c84[2][3])
        self.assertIn("If not:", c84[2][3])
        self.assertIn("anything you'd like me to change?", c84[2][3])

        c85 = batch.LIVE_SCENES[85]
        self.assertIn("I think the more expensive option is worth choosing.", c85[0][3])
        self.assertIn("I agree with your view.", c85[1][3])

        c86 = batch.LIVE_SCENES[86]
        self.assertIn("If I need time:", c86[2][3])
        self.assertIn("If I can answer now:", c86[2][3])
        self.assertIn("anything else?", c86[2][3])

        c91 = batch.LIVE_SCENES[91]
        self.assertIn("one real resource and a specific need", c91[0][3])
        self.assertIn("We need ___ for ___.", c91[1][3])
        self.assertIn("There isn't enough ___ to ___.", c91[1][3])
        self.assertIn("Do you have enough ___ to ___?", c91[2][3])
        self.assertNotIn("more than enough", batch.LESSONS[91]["prompt"][0])

    def test_model_completion_and_transfer_are_exact_six_turn_scenes(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]), number,
            )
            for variant in ("model", "wild"):
                jobs = batch.DIALOGUE_SEMANTIC_LEDGER[number][variant]
                self.assertEqual(len(jobs), 6, (number, variant))
                self.assertEqual(len(set(jobs)), 6, (number, variant))

    def test_dialogue_prompts_introduce_and_preserve_each_target_topic(self):
        # These guards cover the cross-turn relationships that a structural
        # six-turn/count check cannot see.
        self.assertIn("final version", batch.DIALOGUES[83]["wild"][4][0])
        self.assertEqual(batch.DIALOGUES[84]["wild"][1:3], (2, 2))
        self.assertIn("meeting", batch.DIALOGUES[84]["wild"][3][0])
        self.assertIn("Apart from cost", batch.DIALOGUES[85]["model"][4][0])
        self.assertEqual(batch.DIALOGUES[87]["wild"][1:3], (2, 3))
        self.assertEqual(batch.DIALOGUES[88]["wild"][1:3], (2, 3))
        self.assertIn("time", batch.DIALOGUES[88]["wild"][4][0])
        self.assertEqual(batch.DIALOGUES[89]["model"][1:3], (0, 0))
        self.assertIn("problem and a project failure", batch.DIALOGUES[89]["model"][3][0])
        self.assertEqual(batch.DIALOGUES[89]["wild"][1:3], (3, 3))
        self.assertIn("cost problem", batch.DIALOGUES[89]["wild"][3][0])
        self.assertIn("restart", batch.DIALOGUES[89]["wild"][4][0])
        self.assertEqual(batch.DIALOGUES[90]["model"][1:3], (1, 0))
        self.assertEqual(batch.DIALOGUES[90]["wild"][1:3], (3, 2))

    def test_japanese_cues_are_natural_not_literal_for_reviewed_risks(self):
        core85 = str((batch.LESSONS[85], batch.SPECS[85], batch.LIVE_SCENES[85]))
        self.assertIn("よく分からない点", core85)
        self.assertNotIn("確信を持てない点", core85)
        core87 = str((batch.LESSONS[87], batch.SPECS[87], batch.LIVE_SCENES[87]))
        self.assertIn("遠く及びません", core87)
        self.assertNotIn("ほど速くはまったくありません", core87)
        _, core88 = batch.build(88, batch.LESSONS[88])
        self.assertIn("昼食を食べるために残った人は", core88)
        self.assertNotIn("昼食まで残りませんでした", core88)
        _, core81 = batch.build(81, batch.LESSONS[81])
        self.assertIn("responsible for recruitment", core81)
        self.assertNotIn("responsible for new hiring", core81)

    def test_required_spiral_review_is_visible_with_exact_modes(self):
        for number, markers in batch.SPIRAL_MARKERS.items():
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["spiral-review"]
            for spiral_id, mode in markers:
                self.assertIn(f"{spiral_id}:{mode}", page, (number, spiral_id, mode))
        for number in EXPECTED - set(batch.SPIRAL_MARKERS):
            _, source = batch.build(number, batch.LESSONS[number])
            self.assertNotIn("spiral-review", dict(check_deck.pages(source)), number)

    def test_transfer_scenes_are_unique_and_differ_from_main_scenes(self):
        self.assertEqual(len(set(batch.TRANSFER_SCENES.values())), len(EXPECTED))
        for number, label in batch.TRANSFER_SCENES.items():
            self.assertGreaterEqual(len(label.split()), 3, number)
            self.assertNotIn(label.casefold(), str(batch.DIALOGUES[number]["model"]).casefold(), number)

    def test_rendered_sources_match_generator_and_are_complete(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete", number)
            self.assertEqual(expected.count('name="podo:proofread-status"'), 1, number)

    def test_checker_is_clean_after_proofreading(self):
        for number, data in batch.LESSONS.items():
            path, _ = batch.build(number, data)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], (number, errors))
            self.assertEqual(warnings, [], (number, warnings))

    def test_static_controls_and_sync_ids_are_present_and_unique(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            ids = re.findall(r'data-sync-id="([^"]+)"', source)
            self.assertGreater(len(ids), 20, number)
            self.assertEqual(len(ids), len(set(ids)), number)
            self.assertNotRegex(source, r"createElement\(['\"](?:input|textarea|select)")
            controls = re.findall(r'<(?:input|textarea)[^>]+data-sync-id="', source)
            selections = re.findall(r'data-sync-id="[^"]+"[^>]*data-sync-kind="selection"', source)
            self.assertGreater(len(controls), 20, number)
            self.assertGreaterEqual(len(selections), 8, number)

    def test_generation_is_deterministic_in_memory(self):
        first = {number: batch.build(number, batch.LESSONS[number])[1] for number in batch.NUMBERS}
        second = {number: batch.build(number, batch.LESSONS[number])[1] for number in reversed(batch.NUMBERS)}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
