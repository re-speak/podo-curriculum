#!/usr/bin/env python3
"""Regression contract for the explicit CORE-92--102 batch."""

from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_course_batch as shared_core
import generate_core_diplomacy_and_reasoning_batch as batch
import vocabulary


EXPECTED = set(batch.NUMBERS)
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
LEARNER_FUNCTION_WORDS = {
    "a", "an", "the", "i", "i'm", "i'd", "i'll", "my", "you", "your", "you're",
    "he", "he'd", "he'll", "she", "she'd", "it", "it's", "we", "we'd", "we'll",
    "they", "they'd", "them", "me", "us", "am", "is", "are", "be", "been", "was",
    "were", "do", "does", "did", "have", "has", "had", "will", "would", "can",
    "can't", "could", "couldn't", "should", "may", "might", "must", "shall", "to", "of", "in", "on", "at", "for",
    "from", "with", "into", "and", "but", "or", "not", "no", "yes", "this", "that",
    "what", "how", "why", "where", "when", "if", "after", "before", "now", "more",
    "still", "just", "here", "there", "any", "anything", "one", "who", "than", "so",
    "all", "else", "again", "don't", "doesn't", "let's", "that's", "either", "way",
    "as", "about", "up", "out", "then", "yet", "too", "by", "both", "nothing",
    "first", "two", "it'll", "didn't", "won't",
}
IRREGULAR_FORMS = {
    "said": {"say"}, "say": {"said"}, "told": {"tell"}, "tell": {"told"},
    "lost": {"lose"}, "lose": {"lost"}, "meant": {"mean"}, "mean": {"meant"},
    "sent": {"send"}, "send": {"sent"}, "thought": {"think"}, "think": {"thought"},
}


def english_tokens(text):
    return TOKEN_RE.findall(shared_core.strip_marks(text).casefold())


def word_forms(word):
    forms = {word} | IRREGULAR_FORMS.get(word, set())
    if word.endswith("ing") and len(word) > 4:
        base = word[:-3]
        forms.update((base, base + "e"))
        if len(base) > 2 and base[-1] == base[-2]:
            forms.add(base[:-1])
    if word.endswith("ed") and len(word) > 3:
        base = word[:-2]
        forms.update((base, base + "e"))
        if len(base) > 2 and base[-1] == base[-2]:
            forms.add(base[:-1])
        if word.endswith("ied"):
            forms.add(word[:-3] + "y")
    if word.endswith("er") and len(word) > 4:
        base = word[:-2]
        forms.add(base)
        if len(base) > 2 and base[-1] == base[-2]:
            forms.add(base[:-1])
    if word.endswith("s") and len(word) > 3:
        forms.add(word[:-1])
        if word.endswith("es"):
            forms.add(word[:-2])
    return forms


class CoreDiplomacyAndReasoningBatchTests(unittest.TestCase):
    @staticmethod
    def category_words(number, category):
        return {
            entry.split("|", 1)[0].casefold()
            for entry in filter(None, batch.VOCAB[number][category].split("; "))
        }

    @classmethod
    def owned_words(cls, number):
        return set().union(*(cls.category_words(number, category) for category in batch.VOCAB[number]))

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

    def test_source_tables_cover_exact_course(self):
        for values in (
            batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS, batch.OPEN_MENUS, batch.SUPPORT_EXPRESSIONS,
            batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS,
            batch.TRANSFER_SCENES, batch.BRIEF_PRODUCTION_MODELS,
            batch.DIALOGUE_SEMANTIC_LEDGER, batch.PRODUCTIVE_TERMS,
            batch.LIVE_SCAFFOLD_VOCAB, batch.WRITE_PROMPTS,
            batch.CHOICE_OMISSIONS, batch.REVIEWED_LIVE,
            batch.MODEL_ROLE_JA, batch.WILD_ROLE_JA,
        ):
            self.assertEqual(set(values), EXPECTED)

    def test_identity_title_level_and_complete_status_match_briefs(self):
        for number, data in batch.LESSONS.items():
            brief = (batch.TRACK / "toc" / f"CORE-{number}.md").read_text(encoding="utf-8")
            self.assertTrue(brief.startswith(f"# CORE-{number} · {data['title']}\n"), number)
            _, source = batch.build(number, data)
            self.assertEqual(check_deck.meta_content(source, "podo:review-id"), f"CORE-{number}")
            self.assertEqual(check_deck.meta_content(source, "podo:title-en"), data["title"])
            self.assertEqual(check_deck.meta_content(source, "podo:level"), "B2")
            self.assertEqual(check_deck.meta_content(source, "podo:proofread-status"), "complete")
            self.assertEqual(source.count('name="podo:proofread-status"'), 1)

    def test_semantic_specs_are_explicit_and_complete(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["choices"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual(len(spec["tip"]), 6, number)
            for english, japanese in spec["meanings"] + spec["writes"]:
                self.assertTrue(english.strip(), number)
                self.assertTrue(japanese.strip(), number)
            for english, japanese in spec["writes"]:
                self.assertTrue(english.startswith("Now use “"), (number, english))
                self.assertTrue(japanese.startswith("では、「"), (number, japanese))

    def test_choices_are_discriminating_or_intentionally_omitted(self):
        for number, spec in batch.SPECS.items():
            omitted = set(batch.LESSONS[number].get("omit_choice", ()))
            self.assertEqual(omitted, batch.CHOICE_OMISSIONS[number])
            for part, rows in enumerate(spec["choices"], 1):
                if part in omitted:
                    continue
                self.assertEqual(len(rows), 4, (number, part))
                correct_answers = set()
                for japanese, prefix, correct, distractor, suffix in rows:
                    self.assertIn("{t}", japanese, (number, part))
                    self.assertNotEqual(correct, distractor, (number, part))
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertLessEqual(len(distractor.split()), 3, (number, part, distractor))
                    rebuilt = prefix + correct + suffix
                    self.assertRegex(rebuilt, r"^[A-Z].*[.!?]$", (number, part, rebuilt))
                    correct_answers.add(correct.casefold())
                self.assertGreater(len(correct_answers), 1, (number, part, correct_answers))
                _, source = batch.build(number, batch.LESSONS[number])
                choice_page = dict(check_deck.pages(source))[f"p{part}-choose"]
                first_option_is_correct = {
                    'data-correct' in row.split('class="sep"', 1)[0]
                    for row in choice_page.split('class="choose-row')[1:]
                }
                self.assertEqual(first_option_is_correct, {True, False}, (number, part))

    def test_reorders_are_four_units_or_have_an_explicit_reason(self):
        actual = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
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

    def test_multi_target_rows_have_one_japanese_cue_per_target(self):
        for number, part in ((92, 2), (93, 1), (95, 2), (97, 1), (97, 2)):
            for english, japanese, _ in batch.LESSONS[number][f"p{part}"]:
                self.assertEqual(english.count("{t}"), 2, (number, part, english))
                self.assertEqual(japanese.count("{t}"), 2, (number, part, japanese))

    def test_vocabulary_metadata_and_all_hints_are_owned(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            vocabulary.parse(source, source=f"CORE-{number}")
            self.assertLessEqual(len(self.category_words(number, "new")), 8, number)
            self.assertTrue(vocabulary.hint_words(source) <= self.owned_words(number), number)

        self.assertIn("take into account|考慮に入れる", batch.VOCAB[95]["new"])
        self.assertIn("Use take into account", batch.LESSONS[95]["rules"][1][0])

    def test_known_words_are_honest_assumed_or_recycled_items(self):
        for number, entries in batch.KNOWN_WORDS.items():
            allowed = self.category_words(number, "assumed") | self.category_words(number, "recycled")
            forbidden = self.category_words(number, "new") | self.category_words(number, "receptive")
            self.assertEqual(len(entries), 3, number)
            for _, english in entries:
                self.assertIn(english.casefold(), allowed, (number, english))
                self.assertNotIn(english.casefold(), forbidden, (number, english))

        # These are direct, meaning-preserving loanword bridges. Do not turn a
        # familiar Japanese form into a different English sense or larger phrase.
        risky_false_bridges = {
            ("デート", "date"), ("ミーティング", "meet"),
            ("プラン", "backup plan"), ("フルプライス", "full price"),
        }
        actual = {pair for entries in batch.KNOWN_WORDS.values() for pair in entries}
        self.assertTrue(actual.isdisjoint(risky_false_bridges))

    def test_recycled_words_have_visible_earlier_new_owners(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                self.assertLess(int(owner.removeprefix("CORE-")), number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))

    def test_new_ownership_is_unique_and_used_by_the_learner(self):
        seen = {}
        for number in batch.NUMBERS:
            learner_source = " ".join(map(str, (
                batch.LESSONS[number], batch.SPECS[number], batch.TRANSLATE_HINTS[number],
                batch.OPEN_MENUS[number], batch.LIVE_SCENES[number], batch.LIVE_HINTS[number],
            ))).casefold()
            for word in self.category_words(number, "new"):
                self.assertNotIn(word, seen, (word, seen.get(word), number))
                seen[word] = number
                self.assertTrue(
                    all(any(form in learner_source for form in word_forms(token))
                        for token in english_tokens(word)),
                    (number, word),
                )

    def test_productive_content_inventory_has_one_explicit_owner(self):
        for number, terms in batch.PRODUCTIVE_TERMS.items():
            owned = self.owned_words(number)
            self.assertEqual(len(terms), len(set(term.casefold() for term in terms)), number)
            for term in terms:
                self.assertIn(term.casefold(), owned, (number, term))
                self.assertNotIn(term.casefold(), self.category_words(number, "receptive"), (number, term))

    def test_all_derived_learner_language_has_productive_ownership(self):
        for number, data in batch.LESSONS.items():
            owned_entries = [
                entry.split("|", 1)[0]
                for category, value in batch.VOCAB[number].items() if category != "receptive"
                for entry in value.split("; ") if entry
            ]
            owned_forms = {
                form
                for entry in owned_entries
                for token in english_tokens(entry)
                for form in word_forms(token)
            }
            produced = [
                shared_core.strip_marks(row[0])
                for part in ("p1", "p2") for row in data[part]
            ] + [
                batch.DIALOGUES[number][variant][6][0]
                for variant in ("model", "wild")
            ] + [
                turn[3]
                for turn in batch.LIVE_SCENES[number]
                if turn[0:2] == ("input", "me") and turn[3] != "Student's answer"
            ]
            missing = {
                token
                for line in produced for token in english_tokens(line.replace("___ing", "___"))
                if token not in LEARNER_FUNCTION_WORDS and not (word_forms(token) & owned_forms)
            }
            self.assertEqual(missing, set(), (number, sorted(missing)))

    def test_translation_hints_match_their_source_rows(self):
        aliases = {
            "approve": ("approve", "approving"), "agree": ("agree", "agreeing"),
            "choose": ("choose", "choosing"), "discuss": ("discuss",),
            "wait": ("wait", "waited"), "check": ("check", "checked"),
            "ask": ("ask", "asked"), "meet": ("meet",),
            "reschedule": ("reschedule",), "lose": ("lose", "lost"),
            "week": ("week",), "lose a week": ("lose a week", "lost a week"),
        }
        for number, parts in batch.TRANSLATE_HINTS.items():
            for part, hints in enumerate(parts, 1):
                rows = batch.LESSONS[number][f"p{part}"]
                self.assertEqual(len(hints), len(rows), (number, part))
                for row, hint in zip(rows, hints, strict=True):
                    sentence = shared_core.strip_marks(row[0]).casefold()
                    for item in hint.split("; "):
                        english = item.split(":", 1)[1].casefold()
                        expected = aliases.get(english, (english,))
                        self.assertTrue(any(item in sentence for item in expected),
                                        (number, part, sentence, hint))

    def test_exact_brief_models_and_support_are_visible(self):
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

    def test_live_exchange_is_reciprocal_audio_safe_and_truthful(self):
        roles = (("text", "other", "Tutor"), ("input", "me", "Me"),
                 ("text", "me", "Me"), ("input", "other", "Tutor"))
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), roles, number)
            self.assertTrue(scene[0][3].endswith("?"), number)
            self.assertTrue(scene[2][3].endswith("?"), number)
            self.assertEqual(scene[1][3], "Student's answer")
            self.assertEqual(scene[3][3], "Tutor's answer")
            self.assertNotRegex(" ".join(turn[3] for turn in scene).casefold(), r"watch me|look at me|gesture")
            self.assertEqual(batch.LIVE_HINTS[number], {})
            self.assertEqual(
                scene,
                (
                    ("text", "other", "Tutor", *batch.REVIEWED_LIVE[number][:2]),
                    ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
                    ("text", "me", "Me", *batch.REVIEWED_LIVE[number][2:]),
                    ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
                ),
            )
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(page.count('class="turn '), 4, number)
            self.assertIn("Tutor&#x27;s answer:", page, number)
            self.assertNotIn('class="hint"', page, number)
            self.assertIn("Use today's pattern only if it fits.", page, number)

    def test_supported_translation_and_exact_write_contracts(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                translate = pages[f"p{part}-translate"]
                self.assertIn('data-scaffolding-contract="target-v2"', translate)
                self.assertIn('data-support-stage="supported"', translate)
                self.assertEqual(translate.count('class="task-block"'), 4)
                self.assertGreaterEqual(translate.count('class="hint"'), 4)
                write = pages[f"p{part}-write"]
                prompt_en, prompt_ja = batch.WRITE_PROMPTS[number][part - 1]
                self.assertIn(html_lib.escape(prompt_en, quote=True), write)
                self.assertIn(html_lib.escape(prompt_ja, quote=True), write)

    def test_lexical_hints_do_not_supply_article_answers(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                for page_id in (f"p{part}-translate", f"p{part}-write"):
                    hints = [
                        check_deck.plain_text(body).split(":", 1)[-1]
                        for body in check_deck.vocabulary.HINT_CHIP.findall(pages[page_id])
                    ]
                    for hint in hints:
                        self.assertNotRegex(hint.casefold(), r"\b(?:a|an|the)\b", (number, page_id, hint))

    def test_model_completion_and_transfer_are_resolved_six_turn_scenes(self):
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

    def test_cross_turn_topics_are_established_before_targets(self):
        self.assertIn("launch on Monday", batch.DIALOGUES[92]["model"][3][0])
        self.assertIn("warned us", batch.DIALOGUES[93]["model"][3][0])
        self.assertIn("figure is missing", batch.DIALOGUES[94]["model"][3][0])
        self.assertIn("basic plan", batch.DIALOGUES[95]["model"][3][0])
        self.assertIn("this Friday", batch.DIALOGUES[96]["model"][3][0])
        self.assertIn("join us", batch.DIALOGUES[97]["model"][3][0])
        self.assertIn("main cause", batch.DIALOGUES[98]["model"][3][0])
        self.assertIn("redesign announcement", batch.DIALOGUES[99]["model"][3][0])
        self.assertIn("train was canceled", batch.DIALOGUES[100]["model"][3][0])
        self.assertIn("start on Friday", batch.DIALOGUES[101]["model"][3][0])
        self.assertIn("first plan", batch.DIALOGUES[102]["model"][3][0])

    def test_reviewed_referents_and_alternatives_are_explicitly_grounded(self):
        self.assertIn("smaller room may be free", batch.DIALOGUES[94]["wild"][3][0])
        self.assertIn("have not checked", batch.DIALOGUES[94]["wild"][3][0])
        self.assertIn("cost of the delay", batch.DIALOGUES[95]["model"][5][0])
        self.assertIn("opened it", batch.DIALOGUES[99]["model"][3][0])

        core102_model = " ".join(turn[0] for turn in batch.DIALOGUES[102]["model"][3:])
        core102_wild = " ".join(turn[0] for turn in batch.DIALOGUES[102]["wild"][3:])
        for phrase in ("supplier", "first plan", "saved copy", "backup copy"):
            self.assertIn(phrase, core102_model)
        for phrase in ("Tuesday's meeting", "first plan", "Friday"):
            self.assertIn(phrase, core102_wild)

    def test_roleplay_copy_names_roles_concisely_in_both_languages(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            model_page = html_lib.unescape(pages["p3-model"])
            wild_page = html_lib.unescape(pages["in-the-wild"])
            transition_page = html_lib.unescape(pages["part3-intro"])
            model_role = batch.DIALOGUES[number]["model"][0].lower()
            wild_role = batch.DIALOGUES[number]["wild"][0].lower()
            self.assertIn(f"I'll be the {model_role}. Read your lines aloud.", model_page)
            self.assertIn(f"私は{batch.MODEL_ROLE_JA[number]}です。自分のセリフを声に出して読んでください。", model_page)
            self.assertIn(f"I'll be the {wild_role}.", wild_page)
            self.assertIn(f"私は{batch.WILD_ROLE_JA[number]}です。", wild_page)
            self.assertIn("Next, let's role-play a conversation.", transition_page)

    def test_generation_scope_is_exactly_core_92_through_102(self):
        expected_paths = {
            batch.TRACK / "courses" / batch.COURSE / "lessons"
            / f"{number:02d}-{batch.LESSONS[number]['slug']}" / "lesson.html"
            for number in EXPECTED
        }
        actual_paths = {batch.build(number, data)[0] for number, data in batch.LESSONS.items()}
        self.assertEqual(actual_paths, expected_paths)

    def test_core102_semantic_ledger_matches_the_actual_six_turn_model(self):
        expected_jobs = (
            "coordinator states saved-copy plan",
            "learner states restart consequence",
            "coordinator proposes backup copy",
            "learner proposes asking supplier",
            "coordinator commits to backup then supplier call",
            "learner confirms order may keep moving",
        )
        self.assertEqual(batch.DIALOGUE_SEMANTIC_LEDGER[102]["model"], expected_jobs)

        dialogue = batch.DIALOGUES[102]["model"]
        actual_turns = (
            dialogue[3][0],
            shared_core.strip_marks(batch.LESSONS[102]["p1"][0][0]).split(". ")[-1],
            dialogue[4][0],
            shared_core.strip_marks(batch.LESSONS[102]["p2"][0][0]).split(". ")[-1],
            dialogue[5][0],
            dialogue[6][0],
        )
        anchors = ("saved copy", "start again", "backup copy", "ask them", "call the supplier", "order moving")
        for job, turn, anchor in zip(expected_jobs, actual_turns, anchors, strict=True):
            self.assertIn(anchor, turn.casefold(), (job, turn))
        self.assertNotIn("approver", " ".join(expected_jobs))

    def test_required_spirals_are_visible_once_with_exact_modes(self):
        for number, markers in batch.SPIRAL_MARKERS.items():
            _, source = batch.build(number, batch.LESSONS[number])
            for spiral_id, mode in markers:
                self.assertEqual(source.count(f'data-spiral-id="{spiral_id}"'), 1, (number, spiral_id))
                self.assertIn(f'data-spiral-id="{spiral_id}" data-spiral-level="{mode}"', source)
        for number in EXPECTED - set(batch.SPIRAL_MARKERS):
            _, source = batch.build(number, batch.LESSONS[number])
            self.assertNotIn("data-spiral-id=", source, number)

    def test_transfer_scenes_are_unique_and_distinct_from_main_scenes(self):
        self.assertEqual(len(set(batch.TRANSFER_SCENES.values())), len(EXPECTED))
        for number, label in batch.TRANSFER_SCENES.items():
            self.assertGreaterEqual(len(label.split()), 3, number)
            self.assertNotIn(label.casefold(), str(batch.DIALOGUES[number]["model"]).casefold())

    def test_sentence_controls_wrap_and_are_static_in_source(self):
        self.assertIn("field-sizing: content", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn("overflow-wrap: anywhere", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn(".sent-hero", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn(".korean", batch.NARROW_GROWING_INPUT_CSS)
        for number, data in batch.LESSONS.items():
            path, source = batch.build(number, data)
            self.assertEqual(source.count('<link rel="stylesheet" href="growing-inputs.css">'), 1)
            self.assertEqual(path.with_name("growing-inputs.css").read_text(), batch.NARROW_GROWING_INPUT_CSS)
            self.assertNotIn('<input class="space-input"', source)
            self.assertNotRegex(source, r"createElement\(['\"](?:input|textarea|select)")
            for page_id, page in check_deck.pages(source):
                if page_id.endswith("-translate"):
                    self.assertEqual(page.count('<textarea class="space-input free-input"'), 4, (number, page_id))

    def test_rendered_sources_match_generator_and_checker_is_clean(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], (number, errors))
            self.assertEqual(warnings, [], (number, warnings))

    def test_sync_ids_are_unique_and_generation_is_deterministic(self):
        first = {}
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            ids = re.findall(r'data-sync-id="([^"]+)"', source)
            self.assertGreater(len(ids), 20, number)
            self.assertEqual(len(ids), len(set(ids)), number)
            first[number] = source
        second = {number: batch.build(number, batch.LESSONS[number])[1] for number in reversed(batch.NUMBERS)}
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
