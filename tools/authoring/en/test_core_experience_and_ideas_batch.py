#!/usr/bin/env python3
"""Regression contract for the explicit CORE-48--59 course batch."""

from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_course_batch as shared_core
import generate_core_experience_and_ideas_batch as batch
import vocabulary


EXPECTED = set(range(48, 60))


class CoreExperienceAndIdeasBatchTests(unittest.TestCase):
    @staticmethod
    def owned_words(number):
        words = set()
        for category, value in batch.VOCAB[number].items():
            for entry in filter(None, value.split("; ")):
                parts = entry.split("|")
                assert len(parts) == (3 if category == "recycled" else 2), entry
                words.add(parts[0].casefold())
        return words

    @staticmethod
    def category_words(number, category):
        return {
            entry.split("|", 1)[0].casefold()
            for entry in filter(None, batch.VOCAB[number][category].split("; "))
        }

    @staticmethod
    def source_new_words(review_id):
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            html = path.read_text(encoding="utf-8")
            if check_deck.meta_content(html, "podo:review-id") == review_id:
                value = check_deck.meta_content(html, "podo:vocabulary:new")
                return {
                    entry.split("|", 1)[0].casefold()
                    for entry in filter(None, value.split("; "))
                }
        raise AssertionError(f"missing owner deck {review_id}")

    def test_batch_is_complete_and_explicit(self):
        for values in (
            batch.LESSONS,
            batch.SPECS,
            batch.VOCAB,
            batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS,
            batch.OPEN_MENUS,
            batch.DIALOGUES,
            batch.LIVE_SCENES,
            batch.LIVE_HINTS,
            batch.TRANSFER_SCENES,
            batch.DIALOGUE_SEMANTIC_LEDGER,
        ):
            self.assertEqual(set(values), EXPECTED)
        self.assertEqual(set(batch.BRIEF_PRODUCTION_MODELS), {48, 49, 53})
        self.assertEqual(set(batch.SUPPORT_EXPRESSIONS), {48, 50, 53, 55, 56, 57, 59})
        self.assertEqual(set(batch.SUPPORT_OWNERSHIP), set(batch.SUPPORT_EXPRESSIONS))
        for number, categories in batch.VOCAB.items():
            self.assertEqual(
                set(categories), {"new", "recycled", "assumed", "receptive"}, number
            )

    def test_semantic_specs_are_complete(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual(len(spec["tip"]), 6, number)
            for english, japanese in spec["meanings"] + spec["writes"]:
                self.assertTrue(english.strip(), number)
                self.assertTrue(japanese.strip(), number)

    def test_choices_are_smallest_meaningful_units_or_explicitly_omitted(self):
        for number, spec in batch.SPECS.items():
            omitted = set(batch.LESSONS[number].get("omit_choice", ()))
            for part, rows in enumerate(spec["choices"], start=1):
                if part in omitted:
                    continue
                self.assertEqual(len(rows), 4, (number, part))
                for index, (japanese, prefix, correct, distractor, suffix) in enumerate(rows):
                    self.assertIn("{t}", japanese, (number, part, japanese))
                    self.assertNotEqual(correct, distractor, (number, part))
                    for option in (correct, distractor):
                        self.assertLessEqual(
                            len(option.split()), 3, (number, part, option)
                        )
                        self.assertFalse(
                            re.fullmatch(r"[^A-Za-z0-9]+", option),
                            (number, part, option),
                        )
                    rebuilt = prefix + correct + suffix
                    self.assertRegex(rebuilt, r"^[A-Z].*[.!?]$")
                    self.assertNotIn("{t}", rebuilt)

    def test_reorders_are_honest_or_explicitly_omitted(self):
        actual_exceptions = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part in data.get("omit_reorder", ()):
                    actual_exceptions.add((number, part))
                    continue
                shared_core.validate_reorder_pattern(data[f"p{part}"])
                chip_count = len(data[f"p{part}"][0][2].split("|"))
                self.assertIn(chip_count, (3, 4), (number, part))
                self.assertTrue(
                    all(len(row[2].split("|")) == chip_count for row in data[f"p{part}"])
                )
                if chip_count == 3:
                    actual_exceptions.add((number, part))
        self.assertEqual(actual_exceptions, set(batch.THREE_CHIP_EXCEPTIONS))
        for key, reason in batch.THREE_CHIP_EXCEPTIONS.items():
            self.assertGreaterEqual(len(reason.split()), 6, key)

    def test_known_words_and_all_scaffold_hints_are_owned(self):
        for number, entries in batch.KNOWN_WORDS.items():
            self.assertEqual(len(entries), 3, number)
            owned = self.owned_words(number)
            for _, english in entries:
                self.assertIn(english.casefold(), owned, (number, english))
            _, html = batch.build(number, batch.LESSONS[number])
            vocabulary.parse(html, source=f"CORE-{number}")
            declared = self.owned_words(number)
            self.assertTrue(vocabulary.hint_words(html) <= declared, number)

    def test_known_words_are_only_assumed_or_genuinely_recycled(self):
        for number, entries in batch.KNOWN_WORDS.items():
            allowed = self.category_words(number, "assumed") | self.category_words(
                number, "recycled"
            )
            forbidden = self.category_words(number, "new") | self.category_words(
                number, "receptive"
            )
            for _, english in entries:
                word = english.casefold()
                self.assertIn(word, allowed, (number, english))
                self.assertNotIn(word, forbidden, (number, english))

    def test_recycled_vocabulary_has_earlier_provenance(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, source = entry.split("|")
                self.assertTrue(word and japanese)
                self.assertRegex(source, r"^CORE-\d+$")
                self.assertLess(int(source.removeprefix("CORE-")), number)
                self.assertIn(
                    word.casefold(), self.source_new_words(source), (number, word, source)
                )

    def test_new_vocabulary_is_used_by_the_learner_not_only_a_partner(self):
        for number in EXPECTED:
            learner_source = " ".join(
                map(
                    str,
                    (
                        batch.LESSONS[number],
                        batch.SPECS[number],
                        batch.KNOWN_WORDS[number],
                        batch.TRANSLATE_HINTS[number],
                        batch.OPEN_MENUS[number],
                        batch.LIVE_SCENES[number],
                        batch.LIVE_HINTS[number],
                    ),
                )
            ).casefold()
            for word in self.category_words(number, "new"):
                self.assertIn(word, learner_source, (number, word))

    def test_closed_and_open_production_pages_are_scaffolded(self):
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                self.assertEqual(len(batch.TRANSLATE_HINTS[number][part - 1]), 4)
                self.assertTrue(all(batch.TRANSLATE_HINTS[number][part - 1]))
                self.assertTrue(batch.OPEN_MENUS[number][part - 1])
            self.assertEqual(batch.LIVE_HINTS[number], {}, number)

            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for part in (1, 2):
                self.assertEqual(
                    pages[f"p{part}-translate"].count('class="task-block"'), 4
                )
                self.assertGreaterEqual(
                    pages[f"p{part}-translate"].count('class="hint"'), 4
                )
                self.assertIn(
                    'data-scaffolding-contract="target-v2"',
                    pages[f"p{part}-translate"],
                )
                self.assertIn(
                    'data-support-stage="supported"',
                    pages[f"p{part}-translate"],
                )
                self.assertIn('class="hint"', pages[f"p{part}-write"])
                expected_targets = sum(row[0].count("{t}") for row in data[f"p{part}"])
                self.assertEqual(
                    pages[f"p{part}-fill"].count('class="slot-input"'),
                    expected_targets,
                    (number, part),
                )
            self.assertNotIn('class="hint-chip"', pages["p3-freetalk"])
        self.assertNotIn("1日:a day", str(batch.TRANSLATE_HINTS))
        self.assertIn("1日:day", str(batch.TRANSLATE_HINTS[51]))

    def test_live_pages_follow_canonical_ask_back_sequence(self):
        expected_roles = (
            ("text", "other", "Tutor"),
            ("input", "me", "Me"),
            ("text", "me", "Me"),
            ("input", "other", "Tutor"),
        )
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), expected_roles, number)
            self.assertTrue(scene[0][3].endswith("?"), (number, scene[0][3]))
            self.assertTrue(scene[2][3].endswith("?"), (number, scene[2][3]))
            self.assertTrue(scene[2][3].casefold().startswith("what about you"), number)
            self.assertEqual(scene[1][3:], ("Student's answer", "自分の答え"), number)
            self.assertEqual(scene[3][3:], ("Tutor's answer", "先生の答え"), number)
            _, html = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(html))["p3-freetalk"]
            for index in (1, 3):
                self.assertIn(f'data-sync-id="live-{index}"', page, number)
            self.assertNotIn('data-sync-id="live-2"', page, number)
            self.assertIn("Tutor&#x27;s answer", page, number)
            self.assertEqual(page.count('class="turn '), 4, number)
            self.assertIn(shared_core.esc(scene[0][3]), page, number)
            self.assertIn(shared_core.esc(scene[2][3]), page, number)

    def test_every_live_deck_is_real_topic_talk_not_pattern_production(self):
        for number, scene in batch.LIVE_SCENES.items():
            question = scene[0][3]
            ask_back = scene[2][3]
            self.assertNotRegex(
                question.casefold(),
                r"^(use|say|tell|make|give|ask|describe|report|imagine)\b",
            )
            self.assertNotIn("___", question + ask_back, number)
            self.assertNotIn(" / ", question + ask_back, number)
            self.assertGreaterEqual(len(question.split()), 7, number)

    def test_exact_brief_models_and_required_support_are_learner_visible(self):
        for number, models in batch.BRIEF_PRODUCTION_MODELS.items():
            _, deck = batch.build(number, batch.LESSONS[number])
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", deck))
            for model in models:
                self.assertIn(model, visible, (number, model))
        for number, expressions in batch.SUPPORT_EXPRESSIONS.items():
            _, deck = batch.build(number, batch.LESSONS[number])
            pages = dict(check_deck.pages(deck))
            self.assertIn("supporting-expressions", pages, number)
            visible = html_lib.unescape(
                re.sub(r"<[^>]+>", "", pages["supporting-expressions"])
            ).casefold()
            receptive = batch.VOCAB[number]["receptive"].casefold()
            for english, japanese in expressions:
                self.assertIn(english.casefold(), visible, (number, english))
                self.assertIn(japanese, pages["supporting-expressions"], (number, japanese))
            for term in batch.SUPPORT_OWNERSHIP[number]:
                self.assertIn(term.casefold(), receptive, (number, term))
                self.assertIn(term.casefold(), visible, (number, term))

    def test_write_prompts_name_the_exact_pattern_and_communicative_job(self):
        for number, spec in batch.SPECS.items():
            _, html = batch.build(number, batch.LESSONS[number])
            pages = dict(check_deck.pages(html))
            for part, (english, japanese) in enumerate(spec["writes"], 1):
                self.assertTrue(english.startswith("Use “"), (number, part, english))
                self.assertIn("を使って", japanese, (number, part, japanese))
                self.assertIn(shared_core.esc(english), pages[f"p{part}-write"])
                self.assertIn(shared_core.esc(japanese), pages[f"p{part}-write"])

    def test_required_spiral_retrievals_are_visible_and_controlled(self):
        self.assertEqual(
            batch.SPIRAL_MARKERS,
            {50: ("NEGQ-01", "recognition"), 54: ("ASPECT-02", "controlled"), 59: ("REL-01", "checkpoint")},
        )
        for number, (spiral_id, level) in batch.SPIRAL_MARKERS.items():
            _, html = batch.build(number, batch.LESSONS[number])
            self.assertIn(f'data-spiral-id="{spiral_id}"', html, number)
            self.assertIn(f'data-spiral-level="{level}"', html, number)
        _, core50 = batch.build(50, batch.LESSONS[50])
        self.assertIn("Haven&#x27;t you been to Kyoto?", core50)
        _, core54 = batch.build(54, batch.LESSONS[54])
        self.assertIn("I&#x27;ve been", core54)
        self.assertIn("I&#x27;ve", core54)
        _, core59 = batch.build(59, batch.LESSONS[59])
        self.assertIn("who called", core59)
        self.assertIn("that opens", core59)

    def test_decks_match_source_and_completed_reviewer_handoff(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(
                check_deck.meta_content(expected, "podo:proofread-status"),
                "complete",
                number,
            )
            self.assertEqual(
                len(
                    re.findall(
                        r'<meta name="podo:proofread-status" content="[^"]+">',
                        expected,
                    )
                ),
                1,
                number,
            )
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], (number, errors))
            self.assertEqual(warnings, [], (number, warnings))

    def test_roleplay_actions_and_roles_are_explicit_and_bilingual(self):
        for number, data in batch.LESSONS.items():
            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for page_id, variant in (("p3-model", "model"), ("p3-complete", "model"), ("in-the-wild", "wild")):
                role = batch.DIALOGUES[number][variant][0]
                role_ja = batch.ROLE_JA[role]
                page = pages[page_id]
                self.assertIn(role.casefold(), check_deck.plain_text(page).casefold())
                self.assertIn(role_ja, page, (number, page_id))
                self.assertNotIn("相手役", page, (number, page_id))
                self.assertNotIn("Me のセリフ", page, (number, page_id))

    def test_model_completion_and_transfer_are_exact_six_turn_conversations(self):
        for number, data in batch.LESSONS.items():
            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(
                    pages[page_id].count('class="turn '), 6, (number, page_id)
                )
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]),
                number,
            )
            for variant in ("model", "wild"):
                final = batch.DIALOGUES[number][variant][6][0]
                p1 = shared_core.strip_marks(
                    data["p1"][batch.DIALOGUES[number][variant][1]][0]
                )
                p2 = shared_core.strip_marks(
                    data["p2"][batch.DIALOGUES[number][variant][2]][0]
                )
                self.assertNotIn(final, {p1, p2}, (number, variant, final))

    def test_dialogue_semantic_ledger_covers_resolved_adjacent_scenes(self):
        forbidden = (
            "Not yet, but let's find",
            "Are we ready for dinner?",
            "Are we on track?",
            "Who brought the cake to the party?",
            "in this photo",
            "Would you choose the local gym?",
            "Having said that",
            "How did you get there?",
            "It's a longer trip",
            "avoids the traffic",
        )
        for number, variants in batch.DIALOGUE_SEMANTIC_LEDGER.items():
            self.assertEqual(set(variants), {"model", "wild"}, number)
            for variant, turns in variants.items():
                self.assertEqual(len(turns), 6, (number, variant))
                self.assertTrue(all(len(turn.split()) >= 2 for turn in turns))
            dialogue_source = str(batch.DIALOGUES[number])
            for phrase in forbidden:
                self.assertNotIn(phrase, dialogue_source, (number, phrase))

        core55_wild = batch.DIALOGUES[55]["wild"]
        opener = core55_wild[3][0].casefold()
        learner_target = shared_core.strip_marks(
            batch.LESSONS[55]["p1"][core55_wild[1]][0]
        ).casefold()
        target_clue = "brought the cake"
        self.assertIn("which person", opener)
        self.assertIn(target_clue, learner_target)
        self.assertNotIn(target_clue, opener)

    def test_key_contrasts_are_source_locked(self):
        core50 = " ".join(row[0] for row in batch.LESSONS[50]["p2"])
        self.assertIn("last year", core50)
        self.assertIn("two months ago", core50)
        self.assertIn("finished time", batch.LESSONS[50]["rules"][1][0])
        self.assertIn("for", batch.LESSONS[51]["rules"][1][0])
        self.assertIn("since", batch.LESSONS[51]["rules"][1][0])
        self.assertIn("have been plus the -ing form", batch.LESSONS[52]["rules"][0][0])
        self.assertIn(1, batch.LESSONS[53]["omit_reorder"])
        self.assertIn("result first", batch.LESSONS[54]["rules"][0][0])
        self.assertIn("reason first", batch.LESSONS[54]["rules"][1][0])
        self.assertIn("after the noun", batch.LESSONS[55]["rules"][0][0])
        self.assertIn("present form after if", batch.LESSONS[57]["rules"][0][0])
        self.assertIn("present form after when", batch.LESSONS[58]["rules"][0][0])
        self.assertIn("to plus the plain verb", batch.LESSONS[59]["rules"][0][0])

    def test_transfer_scenes_are_unique_within_the_batch(self):
        scenes = list(batch.TRANSFER_SCENES.values())
        self.assertEqual(len(scenes), len(set(scenes)))


if __name__ == "__main__":
    unittest.main()
