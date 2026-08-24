#!/usr/bin/env python3
"""Regression contract for the explicit CORE-113--122 Advanced Stance batch."""

from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_advanced_stance_batch as batch
import generate_core_course_batch as shared_core
import vocabulary


EXPECTED = set(batch.NUMBERS)


class CoreAdvancedStanceBatchTests(unittest.TestCase):
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

    def test_source_tables_cover_exactly_the_assigned_lessons(self):
        for values in (
            batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS, batch.OPEN_MENUS, batch.SUPPORT_EXPRESSIONS,
            batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS,
            batch.LIVE_SLOT_FRAMES,
            batch.TRANSFER_SCENES, batch.BRIEF_PRODUCTION_MODELS,
            batch.DIALOGUE_SEMANTIC_LEDGER, batch.ROLE_JA,
        ):
            self.assertEqual(set(values), EXPECTED)
        self.assertEqual(EXPECTED, set(range(113, 123)))

    def test_identity_title_level_and_models_match_authoritative_briefs(self):
        for number, data in batch.LESSONS.items():
            brief = (batch.TRACK / "toc" / f"CORE-{number}.md").read_text(encoding="utf-8")
            self.assertTrue(brief.startswith(f"# CORE-{number} · {data['title']}\n"), number)
            _, source = batch.build(number, data)
            self.assertEqual(check_deck.meta_content(source, "podo:review-id"), f"CORE-{number}")
            self.assertEqual(check_deck.meta_content(source, "podo:title-en"), data["title"])
            self.assertEqual(check_deck.meta_content(source, "podo:level"), "C1")
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", source))
            for model in batch.BRIEF_PRODUCTION_MODELS[number]:
                self.assertIn(model, visible, (number, model))

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
                    self.assertEqual(japanese.count("{t}"), 1, (number, part, japanese))
                    self.assertNotEqual(correct.strip(), distractor.strip(), (number, part))
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertLessEqual(len(distractor.split()), 3, (number, part, distractor))
                    rebuilt = prefix + correct + suffix
                    self.assertRegex(rebuilt, r"^[A-Z].*[.!?]$", (number, part, rebuilt))

    def test_only_a_genuine_two_way_choice_is_rendered(self):
        self.assertEqual(batch.OMIT_CHOICES, {n: (1, 2) for n in range(113, 122)} | {122: (1,)})
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for part in batch.OMIT_CHOICES[number]:
                self.assertNotIn(f"p{part}-choose", pages, (number, part))
        _, source = batch.build(122, batch.LESSONS[122])
        retained = dict(check_deck.pages(source))["p2-choose"]
        self.assertIn("not really", retained)
        self.assertIn("really not", retained)
        self.assertEqual(retained.count("data-correct"), 4)
        self.assertEqual(retained.count(">not really<"), 4)
        self.assertEqual(retained.count(">really not<"), 4)

    def test_reorders_are_honest_or_have_an_explicit_exception(self):
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
                for row in data[f"p{part}"]:
                    chunks = row[2].split("|")
                    self.assertNotIn("?", chunks, (number, part, chunks))
                    self.assertNotIn(".", chunks, (number, part, chunks))
        self.assertEqual(actual, set(batch.THREE_CHIP_EXCEPTIONS))
        for key, reason in batch.THREE_CHIP_EXCEPTIONS.items():
            self.assertGreaterEqual(len(reason.split()), 7, (key, reason))

    def test_vocabulary_is_parseable_capped_and_all_hints_are_owned(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            vocabulary.parse(source, source=f"CORE-{number}")
            self.assertLessEqual(len(self.category_words(number, "new")), 8, number)
            self.assertTrue(vocabulary.hint_words(source) <= self.owned_words(number), number)

    def test_recycled_words_have_real_visible_earlier_owners(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                owner_number = int(owner.removeprefix("CORE-"))
                self.assertLess(owner_number, number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))

    def test_recycled_japanese_matches_the_canonical_owner(self):
        expected = {
            (113, "delivery"): ("配達", "CORE-77"),
            (113, "scope"): ("範囲", "CORE-84"),
            (115, "delivery"): ("配達", "CORE-77"),
            (115, "schedule"): ("予定", "CORE-67"),
            (115, "timing"): ("タイミング", "CORE-85"),
            (117, "timing"): ("タイミング", "CORE-85"),
            (119, "timing"): ("タイミング", "CORE-85"),
            (120, "schedule"): ("予定", "CORE-67"),
            (121, "prefer"): ("〜のほうが好き", "CORE-42"),
            (122, "the real question is"): ("本当の問題は", "CORE-103"),
        }
        actual = {}
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                if (number, word) in expected:
                    actual[number, word] = (japanese, owner)
        self.assertEqual(actual, expected)

    def test_new_words_have_no_visible_earlier_owner(self):
        prior_owners = {}
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            review_id = check_deck.meta_content(source, "podo:review-id")
            match = re.fullmatch(r"CORE-(\d+)", review_id)
            if not match:
                continue
            owner_number = int(match.group(1))
            for entry in filter(
                None, check_deck.meta_content(source, "podo:vocabulary:new").split("; ")
            ):
                prior_owners.setdefault(entry.split("|", 1)[0].casefold(), owner_number)
        for number in batch.NUMBERS:
            for word in self.category_words(number, "new"):
                owner = prior_owners.get(word)
                self.assertTrue(owner is None or owner == number or owner > number, (number, word, owner))

    def test_known_words_are_assumed_or_genuinely_recycled(self):
        for number, entries in batch.KNOWN_WORDS.items():
            allowed = self.category_words(number, "assumed") | self.category_words(number, "recycled")
            forbidden = self.category_words(number, "new") | self.category_words(number, "receptive")
            self.assertEqual(len(entries), 3, number)
            for _, english in entries:
                self.assertIn(english.casefold(), allowed, (number, english))
                self.assertNotIn(english.casefold(), forbidden, (number, english))

    def test_each_translation_hint_matches_its_source_row(self):
        aliases = {"disagree": "agree", "not go well": "didn't go well"}
        for number, parts in batch.TRANSLATE_HINTS.items():
            for part, hints in enumerate(parts, 1):
                rows = batch.LESSONS[number][f"p{part}"]
                self.assertEqual(len(hints), len(rows), (number, part))
                for row, item in zip(rows, hints, strict=True):
                    sentence = shared_core.strip_marks(row[0]).casefold()
                    english = item.split(":", 1)[1].casefold()
                    expected = aliases.get(english, english)
                    self.assertIn(expected, sentence, (number, part, sentence, item))

    def test_new_words_are_learner_owned_not_partner_only(self):
        for number in EXPECTED:
            learner_source = " ".join(map(str, (
                batch.LESSONS[number], batch.KNOWN_WORDS[number],
                batch.TRANSLATE_HINTS[number], batch.OPEN_MENUS[number],
                batch.LIVE_SCENES[number][1:3], batch.LIVE_HINTS[number],
            ))).casefold()
            for word in self.category_words(number, "new"):
                self.assertIn(word, learner_source, (number, word))

    def test_support_expressions_are_learner_visible_and_bilingual(self):
        for number in EXPECTED:
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["supporting-expressions"]
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", page))
            for english, japanese in batch.SUPPORT_EXPRESSIONS[number]:
                self.assertIn(english, visible, (number, english))
                self.assertIn(japanese, visible, (number, japanese))

    def test_every_open_prompt_has_an_honest_alternative(self):
        for number, spec in batch.SPECS.items():
            for english, japanese in spec["writes"]:
                self.assertIn(" or ", english, (number, english))
                self.assertIn("か", japanese, (number, japanese))
        for number, data in batch.LESSONS.items():
            self.assertIn(" or ", data["prompt"][0], number)
            self.assertIn("か", data["prompt"][1], number)

    def test_live_exchange_is_audio_safe_reciprocal_and_real(self):
        roles = (("text", "other", "Tutor"), ("input", "me", "Me"),
                 ("text", "me", "Me"), ("input", "other", "Tutor"))
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), roles, number)
            all_english = " ".join(turn[3] for turn in scene).casefold()
            self.assertNotRegex(all_english, r"watch me|look at me|gesture|as you can see")
            self.assertRegex(scene[2][3], r"\?$", (number, scene[2][3]))
            self.assertEqual(scene[1][3], "Student's answer", number)
            self.assertEqual(scene[3][3], "Tutor's answer", number)
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(page.count('class="turn '), 4, number)
            self.assertIn("Student&#x27;s answer", page, number)
            self.assertIn("Tutor&#x27;s answer", page, number)
            self.assertIn("Use today's pattern only if it fits", page, number)

    def test_live_hints_only_support_real_semantic_slots(self):
        for number, hints in batch.LIVE_HINTS.items():
            self.assertEqual(hints, {}, number)
            self.assertEqual(batch.LIVE_SLOT_FRAMES[number], (), number)
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertNotIn('class="slot-hint-group"', page, number)

    def test_roleplay_operating_copy_names_each_actual_role_in_both_languages(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            model_role, transfer_role = batch.ROLE_JA[number]
            for page_id in ("p3-model", "p3-complete"):
                self.assertIn(f"私は{model_role}役をします。", pages[page_id], (number, page_id))
                self.assertNotIn("私は相手役をします。", pages[page_id], (number, page_id))
            self.assertIn(f"私は{transfer_role}役をします。", pages["in-the-wild"], number)
            self.assertNotIn("私は相手役をします。", pages["in-the-wild"], number)

    def test_independent_review_fixes_are_source_locked(self):
        c115 = batch.LESSONS[115]["p2"]
        for _, japanese, _ in c115:
            visible = shared_core.strip_marks(japanese)
            self.assertRegex(visible, r"^それでも、.+必要があります。$")
            self.assertNotIn("必要なのは", visible)

        self.assertIn(1, batch.LESSONS[116]["omit_reorder"])
        self.assertEqual(batch.LESSONS[116]["p1"][0][2], "If anything,|it's got worse.")
        self.assertIn("keep it's got worse intact", batch.THREE_CHIP_EXCEPTIONS[(116, 1)])

        c118 = str((batch.LESSONS[118], batch.SPECS[118], batch.LIVE_SCENES[118]))
        self.assertNotIn("留保", c118)
        self.assertNotIn("my interpretation", batch.LIVE_SCENES[118][2][3])
        self.assertIn("extra approval steps", batch.LIVE_SCENES[118][2][3])

        self.assertIn(".choose-row.word-choice", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn("overflow-wrap: anywhere", batch.NARROW_GROWING_INPUT_CSS)
        _, c122_source = batch.build(122, batch.LESSONS[122])
        self.assertIn('href="growing-inputs.css"', c122_source)

    def test_word_choice_wrap_uses_phone_width_not_browser_viewport(self):
        # Reproduce a 360px lesson phone embedded in Orca's wide browser.  A
        # viewport media query is false here, so the safe wrap must be part of
        # the unconditional batch stylesheet.
        browser_viewport = 1274
        phone_width = 360
        self.assertGreater(browser_viewport, 400)
        self.assertLessEqual(phone_width, 360)

        css = batch.NARROW_GROWING_INPUT_CSS
        self.assertNotIn("@media (max-width: 400px)", css)
        self.assertRegex(
            css,
            r"(?s)\.choose-row\.word-choice\s*\{[^}]*flex-wrap:\s*wrap;",
        )
        self.assertRegex(
            css,
            r"(?s)\.choose-row\.word-choice \.opt\s*\{[^}]*max-width:\s*100%;",
        )

        _, source = batch.build(122, batch.LESSONS[122])
        page = dict(check_deck.pages(source))["p2-choose"]
        self.assertEqual(page.count('class="opt"'), 8)
        self.assertIn(">not really<", page)
        self.assertIn(">really not<", page)

    def test_semantic_reread_regressions_stay_natural_and_faithful(self):
        core118 = str((batch.LESSONS[118], batch.SPECS[118]))
        self.assertIn("呼ぶ理由は分かりますけどね", core118)
        self.assertNotIn("留保はあります", core118)
        core121 = str((batch.LESSONS[121], batch.SPECS[121], batch.OPEN_MENUS[121]))
        self.assertIn("into{/t} what happened", core121)
        self.assertNotIn("go into my private situation", core121)
        self.assertIn("makes a good story", batch.LIVE_SCENES[119][2][3])
        self.assertIn("always check", batch.LIVE_SCENES[120][2][3])
        self.assertIn("the real question is|本当の問題は|CORE-103", batch.VOCAB[122]["recycled"])
        self.assertEqual(batch.DIALOGUES[114]["wild"][1:3], (1, 0))
        self.assertEqual(batch.DIALOGUES[119]["wild"][1:3], (2, 3))
        self.assertIn("Maya calculated", batch.DIALOGUES[120]["model"][3][0])
        self.assertEqual(batch.DIALOGUES[120]["wild"][1:3], (2, 3))
        self.assertIn("checking the file name", batch.LESSONS[120]["p2"][3][0])

    def test_dialogue_model_completion_and_transfer_are_six_distinct_turns(self):
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

    def test_required_spirals_are_visible_in_exact_modes(self):
        for number, markers in batch.SPIRAL_MARKERS.items():
            _, source = batch.build(number, batch.LESSONS[number])
            pages = dict(check_deck.pages(source))
            for spiral_id, level in markers:
                page = pages[f"spiral-{spiral_id.casefold()}"]
                self.assertIn(f'data-spiral-id="{spiral_id}"', page)
                self.assertIn(f'data-spiral-level="{level}"', page)
        for number in EXPECTED - set(batch.SPIRAL_MARKERS):
            _, source = batch.build(number, batch.LESSONS[number])
            self.assertFalse(any(pid.startswith("spiral-") for pid in dict(check_deck.pages(source))), number)

    def test_transfer_scenes_are_unique_and_true_variations(self):
        self.assertEqual(len(set(batch.TRANSFER_SCENES.values())), len(EXPECTED))
        for number, label in batch.TRANSFER_SCENES.items():
            self.assertGreaterEqual(len(label.split()), 3, number)
            self.assertNotIn(label.casefold(), str(batch.DIALOGUES[number]["model"]).casefold(), number)

    def test_static_textareas_wrap_grow_and_keep_sync_contract(self):
        for number, data in batch.LESSONS.items():
            path, source = batch.build(number, data)
            css = path.with_name("growing-inputs.css")
            self.assertTrue(css.is_file(), number)
            self.assertIn('href="growing-inputs.css"', source)
            self.assertIn("field-sizing: content", css.read_text(encoding="utf-8"))
            self.assertNotIn('<input class="space-input"', source)
            self.assertNotIn('<input class="slot-input"', source)
            self.assertGreaterEqual(source.count('<textarea class="space-input"'), 8, number)
            self.assertGreaterEqual(source.count('<textarea class="slot-input phrase-input"'), 8, number)
            ids = re.findall(r'data-sync-id="([^"]+)"', source)
            self.assertGreater(len(ids), 20, number)
            self.assertEqual(len(ids), len(set(ids)), number)
            self.assertNotRegex(source, r"createElement\(['\"](?:input|textarea|select)")

    def test_rendered_sources_match_generator_and_canonical_shape(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete", number)
            self.assertEqual(expected.count('name="podo:proofread-status"'), 1, number)

    def test_checker_is_clean_after_independent_proofreading(self):
        for number, data in batch.LESSONS.items():
            path, _ = batch.build(number, data)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], (number, errors))
            self.assertEqual(warnings, [], (number, warnings))

    def test_generation_is_deterministic_in_memory(self):
        first = {number: batch.build(number, batch.LESSONS[number])[1] for number in batch.NUMBERS}
        second = {number: batch.build(number, batch.LESSONS[number])[1] for number in reversed(batch.NUMBERS)}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
