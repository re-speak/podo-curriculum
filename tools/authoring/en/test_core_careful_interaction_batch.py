#!/usr/bin/env python3
"""Regression contract for the explicit CORE-60--70 course batch."""

from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_core_careful_interaction_batch as batch
import generate_core_course_batch as shared_core
import vocabulary


EXPECTED = set(range(60, 71))
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
LEARNER_FUNCTION_WORDS = {
    "a", "an", "the", "i", "i'm", "i'd", "i'll", "my", "you", "your", "you're",
    "he", "he'd", "he'll", "she", "she'd", "it", "it's", "we", "we'll", "they",
    "they'd", "me", "am", "is", "are", "be", "been", "was", "were", "do", "does",
    "did", "have", "has", "had", "will", "would", "can", "can't", "could", "should", "to", "of", "in",
    "on", "at", "for", "from", "with",
    "and", "but", "or", "not", "no", "yes", "this", "that", "what", "how", "why",
    "where", "when", "if", "after", "before", "now", "more", "just", "here", "there", "there's",
    "any", "anything", "one", "someone", "who", "than", "so", "all", "else", "again",
    "don't", "let's", "that's", "ever", "right",
}
IRREGULAR_FORMS = {
    "said": {"say"}, "say": {"said"}, "told": {"tell"}, "tell": {"told"},
    "stolen": {"steal", "stole"}, "taken": {"take", "took"}, "won": {"win"},
}
SEMANTIC_CHOICE_PAGES = {(62, 1), (62, 2), (65, 1)}
BRIEF_MODELS = {
    60: ("Could you open the window?", "Would you mind opening the window?"),
    61: ("Do you mind if I sit here?", "Not at all, go ahead."),
    62: ("Do you know where the station is?", "Could you tell me when the next train leaves?"),
    63: ("I generally prefer coffee to tea.", "I tend to avoid crowded places."),
    64: ("My laptop won't turn on.", "Have you tried restarting it?"),
    65: ("My wallet was stolen.", "It was taken from my bag."),
    66: ("If I had more time, I'd travel more.", "What would you do if you won?"),
    67: ("I wish I had more free time.", "I wish I could drive."),
    68: ("He must be busy.", "Or he might just be out."),
    69: ("She said she was busy.", "He told me he'd call back."),
    70: ("She told me to wait here.", "He asked me not to mention it."),
}
SUPPORT_TERMS = {
    60: ("if it's not too much trouble", "whenever you get a chance"),
    61: ("please do", "sorry, someone's sitting there"),
    62: ("sorry to bother you", "by any chance"),
    63: ("in general", "as a rule"),
    64: ("it's playing up", "that did the trick"),
    65: ("apparently", "it turns out"),
    66: ("in a perfect world", "realistically"),
    67: ("if only", "oh well"),
    68: ("I bet", "who knows"),
    69: ("apparently", "word for word"),
    70: ("word has it", "strictly speaking"),
}


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
    if word.endswith("s") and len(word) > 3:
        forms.add(word[:-1])
    return forms


def english_tokens(text):
    normalized = text.casefold().replace("’", "'").replace("é", "e")
    return TOKEN_RE.findall(normalized)


class CoreCarefulInteractionBatchTests(unittest.TestCase):
    @staticmethod
    def words(number, category=None):
        categories = (category,) if category else tuple(batch.VOCAB[number])
        return {
            entry.split("|", 1)[0].casefold()
            for key in categories
            for entry in filter(None, batch.VOCAB[number][key].split("; "))
        }

    @staticmethod
    def source_new_words(review_id):
        number = int(review_id.removeprefix("CORE-"))
        if number in batch.VOCAB:
            return CoreCarefulInteractionBatchTests.words(number, "new")
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            if check_deck.meta_content(source, "podo:review-id") == review_id:
                return {
                    entry.split("|", 1)[0].casefold()
                    for entry in filter(None, check_deck.meta_content(source, "podo:vocabulary:new").split("; "))
                }
        raise AssertionError(f"missing owner {review_id}")

    def test_batch_is_complete_and_explicit(self):
        for values in (
            batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS, batch.TRANSLATE_STAGES, batch.OPEN_MENUS,
            batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS,
            batch.DIALOGUE_SEMANTIC_LEDGER, batch.SPIRAL_MARKERS,
            batch.WRITE_PROMPTS, batch.FILL_HINTS, batch.CHOICE_OMISSIONS,
            batch.REVIEWED_LIVE,
        ):
            self.assertEqual(set(values), EXPECTED)
        for number, categories in batch.VOCAB.items():
            self.assertEqual(set(categories), {"new", "recycled", "assumed", "receptive"}, number)
            self.assertLessEqual(len(self.words(number, "new")), 8, number)

    def test_generation_scope_is_exactly_core_60_through_70(self):
        expected_paths = {
            batch.TRACK / "courses" / batch.COURSE / "lessons"
            / f"{number:02d}-{batch.LESSONS[number]['slug']}" / "lesson.html"
            for number in EXPECTED
        }
        actual_paths = {
            batch.build(number, data)[0]
            for number, data in batch.LESSONS.items()
        }
        self.assertEqual(actual_paths, expected_paths)
        self.assertTrue(all(path.parent.name[:2].isdigit() for path in actual_paths))

    def test_exact_brief_models_and_support_are_visible(self):
        for number, data in batch.LESSONS.items():
            _, deck = batch.build(number, data)
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", deck))
            for model in BRIEF_MODELS[number]:
                self.assertIn(model, visible, (number, model))
            support = dict(check_deck.pages(deck))["supporting-expressions"]
            support_visible = html_lib.unescape(re.sub(r"<[^>]+>", "", support)).casefold()
            for term in SUPPORT_TERMS[number]:
                self.assertIn(term.casefold(), support_visible, (number, term))

    def test_core62_long_embedded_questions_have_a_narrow_break(self):
        _, deck = batch.build(62, batch.LESSONS[62])
        teach = dict(check_deck.pages(deck))["p1-teach"]
        self.assertEqual(
            teach.count(
                '<span class="ending">Do you know where</span><br>'
                '<span class="ending">the '
            ),
            3,
        )

    def test_choice_pages_are_discriminating_or_intentionally_omitted(self):
        for number, spec in batch.SPECS.items():
            omitted = set(batch.LESSONS[number].get("omit_choice", ()))
            self.assertEqual(omitted, batch.CHOICE_OMISSIONS[number])
            for part, rows in enumerate(spec["choices"], start=1):
                if part in omitted:
                    self.assertEqual(rows, (), (number, part))
                    continue
                self.assertEqual(len(rows), 4, (number, part))
                correct_answers = set()
                for japanese, _, correct, distractor, _ in rows:
                    self.assertEqual(japanese.count("{t}"), 1, (number, part))
                    self.assertEqual(japanese.count("{/t}"), 1, (number, part))
                    self.assertNotEqual(correct.casefold(), distractor.casefold())
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    correct_answers.add(correct.casefold())
                self.assertGreater(len(correct_answers), 1, (number, part, correct_answers))

    def test_reorders_are_honest_or_explicitly_justified(self):
        actual = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part in data.get("omit_reorder", ()):
                    actual.add((number, part))
                    continue
                shared_core.validate_reorder_pattern(data[f"p{part}"])
                counts = {len(row[2].split("|")) for row in data[f"p{part}"]}
                self.assertEqual(len(counts), 1, (number, part))
                count = counts.pop()
                self.assertIn(count, (3, 4))
                if count == 3:
                    actual.add((number, part))
        self.assertEqual(actual, set(batch.THREE_CHIP_EXCEPTIONS))
        self.assertTrue(all(len(reason.split()) >= 6 for reason in batch.THREE_CHIP_EXCEPTIONS.values()))

    def test_vocabulary_provenance_and_productive_support(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                self.assertLess(int(owner.removeprefix("CORE-")), number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))
            productive_source = str(batch.LESSONS[number]).casefold()
            for word in self.words(number, "new"):
                self.assertIn(word, productive_source, (number, word))
            receptive = self.words(number, "receptive")
            for menu in batch.OPEN_MENUS[number]:
                for chip in menu:
                    self.assertNotIn(chip.rsplit(":", 1)[-1].casefold(), receptive, (number, chip))
        self.assertIn("might|〜かもしれない|CORE-39", batch.VOCAB[68]["recycled"])
        self.assertNotIn("might|", batch.VOCAB[68]["new"])
        self.assertIn("print|印刷する|CORE-41", batch.VOCAB[64]["recycled"])
        self.assertNotIn("print|", batch.VOCAB[64]["new"])
        self.assertIn("anywhere|どこでも", batch.VOCAB[66]["new"])
        self.assertIn("open|開ける", batch.VOCAB[60]["new"])
        self.assertIn("open|開ける|CORE-60", batch.VOCAB[61]["recycled"])
        for number in (60, 62, 66, 67):
            declared = " ".join(batch.VOCAB[number].values()).casefold()
            self.assertNotRegex(declared, r"(?:^|; )(?:could|would)\|", number)
        self.assertTrue(any("anywhere" in hint for hint in batch.TRANSLATE_HINTS[66][1]))
        self.assertTrue(any("anywhere" in hint for hint in batch.OPEN_MENUS[66][1]))

    def test_known_words_are_honest_and_all_hints_are_declared(self):
        for number, entries in batch.KNOWN_WORDS.items():
            self.assertEqual(len(entries), 3, number)
            allowed = self.words(number, "assumed") | self.words(number, "recycled")
            for _, english in entries:
                self.assertIn(english.casefold(), allowed, (number, english))
            _, deck = batch.build(number, batch.LESSONS[number])
            vocabulary.parse(deck, source=f"CORE-{number}")
            self.assertTrue(vocabulary.hint_words(deck) <= self.words(number), (number, vocabulary.hint_words(deck) - self.words(number)))

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
            produced = [line.replace("___ing", "___") for line in produced]
            missing = {
                token
                for line in produced for token in english_tokens(line)
                if token not in LEARNER_FUNCTION_WORDS and not (word_forms(token) & owned_forms)
            }
            self.assertEqual(missing, set(), (number, sorted(missing)))

    def test_translate_write_and_live_production_are_scaffolded(self):
        for number, data in batch.LESSONS.items():
            _, deck = batch.build(number, data)
            pages = dict(check_deck.pages(deck))
            for part in (1, 2):
                self.assertEqual(batch.TRANSLATE_STAGES[number][part - 1], "supported")
                self.assertEqual(len(batch.TRANSLATE_HINTS[number][part - 1]), 4)
                self.assertEqual(pages[f"p{part}-translate"].count('class="task-block"'), 4)
                self.assertGreaterEqual(pages[f"p{part}-translate"].count('class="hint"'), 4)
                self.assertIn('data-scaffolding-contract="target-v2"', pages[f"p{part}-translate"])
                self.assertIn('data-support-stage="supported"', pages[f"p{part}-translate"])
                self.assertEqual(len(batch.FILL_HINTS[number][part - 1]), 4)
                self.assertGreaterEqual(pages[f"p{part}-fill"].count('class="hint"'), 4)
                self.assertIn('class="hint"', pages[f"p{part}-write"])
                prompt_en, prompt_ja = batch.WRITE_PROMPTS[number][part - 1]
                self.assertTrue(prompt_en.startswith("Now use “"), (number, part, prompt_en))
                self.assertTrue(prompt_ja.startswith("では、「"), (number, part, prompt_ja))
                self.assertIn("___", prompt_en)
            self.assertNotIn('class="hint"', pages["p3-freetalk"])

    def test_live_pages_are_audio_safe_reciprocal_and_branch_safe(self):
        for number, scene in batch.LIVE_SCENES.items():
            question, question_ja, ask_back, ask_back_ja = batch.REVIEWED_LIVE[number]
            self.assertEqual(scene, (
                ("text", "other", "Tutor", question, question_ja),
                ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
                ("text", "me", "Me", ask_back, ask_back_ja),
                ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
            ))
            self.assertIn("?", question)
            self.assertIn("？", question_ja)
            self.assertIn("?", ask_back)
            self.assertIn("？", ask_back_ja)
            self.assertNotRegex(scene[0][3].casefold(), r"look at me|watch me|gesture")
            self.assertEqual(batch.LIVE_HINTS[number], {})
            _, deck = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(deck))["p3-freetalk"]
            self.assertEqual(page.count('class="turn '), len(scene), number)
            for index, turn in enumerate(scene):
                if turn[0] != "input":
                    continue
                self.assertIn(f'data-sync-id="live-{index}"', page, number)

        for number in EXPECTED:
            self.assertEqual(
                batch.LESSONS[number]["prompt"][0],
                "Let's talk about this topic. Answer my question, then ask me too.",
            )

    def test_model_completion_transfer_are_six_turn_resolved_scenes(self):
        for number, data in batch.LESSONS.items():
            _, deck = batch.build(number, data)
            pages = dict(check_deck.pages(deck))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)
            for variant in ("model", "wild"):
                role, p1_row, p2_row, opener, follow, close, final = batch.DIALOGUES[number][variant]
                self.assertTrue(role and opener[0] and follow[0] and close[0] and final[0])
                self.assertNotEqual(final[0], shared_core.strip_marks(data["p1"][p1_row][0]))
                self.assertNotEqual(final[0], shared_core.strip_marks(data["p2"][p2_row][0]))

    def test_reviewed_semantic_repairs_remain_locked(self):
        for variant in ("model", "wild"):
            core62 = batch.DIALOGUES[62][variant]
            if variant == "model":
                self.assertEqual(core62[0], "Hotel receptionist")
                self.assertIn("heading", core62[3][0])
                self.assertNotEqual(core62[0], "Station staff")
        self.assertEqual(batch.SPECS[62]["choices"], ((), ()))
        core60_spiral = batch.spiral_page(60, "POLITE-01", "contrast")
        self.assertNotIn("普通の丁寧なお願い", core60_spiral)
        self.assertIn("Could you の後ろは動詞の原形", core60_spiral)
        self.assertIn("Would you mind の後ろは -ing 形", core60_spiral)
        self.assertIn("What kind of places do you avoid?", batch.DIALOGUES[63]["wild"][4][0])
        self.assertIn("This train is quiet", batch.DIALOGUES[63]["wild"][5][0])
        self.assertIn("commute every day", batch.DIALOGUES[67]["wild"][3][0])
        self.assertNotIn("work setup at home", batch.DIALOGUES[67]["wild"][3][0])
        self.assertIn("theft report", batch.WRITE_PROMPTS[65][0][0])
        self.assertNotIn("lost-property report", batch.WRITE_PROMPTS[65][0][0])
        self.assertIn("said they would do", batch.LESSONS[69]["goal"][0])
        self.assertNotIn("promised", batch.LESSONS[69]["goal"][0])
        for number in (63, 69, 70):
            for part in ("p1", "p2"):
                for _, japanese, _ in batch.LESSONS[number][part]:
                    self.assertEqual(japanese.count("{t}"), 1, (number, part, japanese))
                    self.assertEqual(japanese.count("{/t}"), 1, (number, part, japanese))
        self.assertEqual(batch.SPECS[70]["tip"][0], "Told me to or asked me to?")
        self.assertNotIn("Word has it", batch.SPECS[70]["tip"][2])
        for _, prefix, correct, distractor, suffix in batch.SPECS[70]["choices"][1]:
            self.assertTrue(correct.startswith("not to "))
            self.assertTrue(distractor.startswith("to "))
            self.assertIn(prefix + distractor + suffix, {
                "He asked me to mention it.", "She asked me to share the file.",
                "He asked me to call today.", "She asked me to open the door.",
            })
        self.assertEqual(
            {row[2] for row in batch.SPECS[61]["choices"][1]},
            {"Not at all", "Sorry"},
        )
        self.assertEqual(
            {row[2] for row in batch.SPECS[68]["choices"][0]},
            {"must be", "might be"},
        )

    def test_sentence_length_controls_are_static_wrapping_textareas(self):
        self.assertIn("field-sizing: content", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn("white-space: pre-wrap", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn("overflow-wrap: anywhere", batch.NARROW_GROWING_INPUT_CSS)
        for number, data in batch.LESSONS.items():
            path, deck = batch.build(number, data)
            self.assertEqual(deck.count('<link rel="stylesheet" href="growing-inputs.css">'), 1, number)
            self.assertEqual(path.with_name("growing-inputs.css").read_text(), batch.NARROW_GROWING_INPUT_CSS)
            self.assertNotIn('<input class="space-input"', deck, number)
            translate = [
                page for page_id, page in check_deck.pages(deck)
                if page_id.endswith("-translate")
            ]
            self.assertEqual(len(translate), 2, number)
            for page in translate:
                self.assertEqual(page.count('<textarea class="space-input"'), 4, number)
                self.assertEqual(page.count('rows="2"></textarea>'), 4, number)

    def test_required_spirals_are_visible_once(self):
        for number, markers in batch.SPIRAL_MARKERS.items():
            _, deck = batch.build(number, batch.LESSONS[number])
            for spiral_id, level in markers:
                self.assertEqual(deck.count(f'data-spiral-id="{spiral_id}"'), 1, (number, spiral_id))
                self.assertIn(f'data-spiral-id="{spiral_id}" data-spiral-level="{level}"', deck, (number, spiral_id))

    def test_decks_match_source_and_are_complete(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete", number)
            self.assertEqual(len(re.findall(r'<meta name="podo:proofread-status" content="[^"]+">', expected)), 1, number)


if __name__ == "__main__":
    unittest.main()
