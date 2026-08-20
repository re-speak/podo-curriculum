#!/usr/bin/env python3
"""Regression contract for explicit CORE-103--112 source and rendered decks."""

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
import generate_core_emphasis_and_tone_batch as batch
import vocabulary


EXPECTED = set(range(103, 113))
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
FUNCTION_WORDS = {
    "a", "an", "the", "i", "i'm", "i'd", "i'll", "my", "you", "your",
    "he", "she", "it", "it's", "we", "we're", "we'll", "they", "they're",
    "me", "is", "are", "be", "been", "was", "were", "do", "does", "did",
    "have", "has", "had", "will", "would", "can", "can't", "could", "should",
    "to", "of", "in", "on", "at", "for", "from", "with", "as", "by",
    "and", "but", "or", "not", "no", "yes", "this", "that", "what", "how",
    "why", "where", "when", "if", "after", "before", "now", "more", "most",
    "just", "here", "there", "there's", "any", "anything", "one", "who",
    "than", "so", "all", "else", "again", "don't", "doesn't", "didn't",
    "let's", "that's", "too", "up", "away", "over", "about", "back", "still",
    "already", "any", "another", "both", "first", "second", "right", "today",
    "tomorrow", "now", "yet", "ever", "none", "nothing", "everything", "some",
}
IRREGULAR = {
    "sent": {"send"}, "called": {"call"}, "changed": {"change"},
    "suggested": {"suggest"}, "moved": {"move"}, "booked": {"book"},
    "worried": {"worry"}, "worries": {"worry"}, "came": {"come"},
    "sounded": {"sound"}, "said": {"say"}, "told": {"tell"},
}


def forms(token):
    found = {token} | IRREGULAR.get(token, set())
    if token.endswith("'s") and len(token) > 2:
        found.add(token[:-2])
    if token.endswith("ing") and len(token) > 4:
        base = token[:-3]
        found.update((base, base + "e"))
        if len(base) > 2 and base[-1] == base[-2]:
            found.add(base[:-1])
    if token.endswith("ed") and len(token) > 3:
        base = token[:-2]
        found.update((base, base + "e"))
    if token.endswith("s") and len(token) > 3:
        found.add(token[:-1])
    return found


def tokens(text):
    return TOKEN_RE.findall(text.casefold().replace("’", "'"))


class CoreEmphasisAndToneBatchTests(unittest.TestCase):
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
        for path in batch.TRACK.glob("courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            if check_deck.meta_content(source, "podo:review-id") == review_id:
                return {
                    entry.split("|", 1)[0].casefold()
                    for entry in filter(None, check_deck.meta_content(source, "podo:vocabulary:new").split("; "))
                }
        raise AssertionError(f"missing visible owner {review_id}")

    def test_source_tables_cover_exactly_the_owned_course(self):
        for values in (
            batch.LESSONS, batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS,
            batch.TRANSLATE_HINTS, batch.OPEN_MENUS, batch.SUPPORT_EXPRESSIONS,
            batch.DIALOGUES, batch.LIVE_SCENES, batch.LIVE_HINTS,
            batch.TRANSFER_SCENES, batch.BRIEF_PRODUCTION_MODELS,
            batch.DIALOGUE_SEMANTIC_LEDGER, batch.WRITE_FRAMES, batch.FREE_TALK,
        ):
            self.assertEqual(set(values), EXPECTED)
        used_roles = {
            data[variant][0]
            for data in batch.DIALOGUES.values()
            for variant in ("model", "wild")
        }
        self.assertEqual(set(batch.ROLE_JA), used_roles)

    def test_identity_title_level_and_exact_one_complete_marker(self):
        for number, data in batch.LESSONS.items():
            brief = (batch.TRACK / "toc" / f"CORE-{number}.md").read_text(encoding="utf-8")
            self.assertTrue(brief.startswith(f"# CORE-{number} · {data['title']}\n"), number)
            _, source = batch.build(number, data)
            self.assertEqual(check_deck.meta_content(source, "podo:review-id"), f"CORE-{number}")
            self.assertEqual(check_deck.meta_content(source, "podo:title-en"), data["title"])
            self.assertEqual(check_deck.meta_content(source, "podo:level"), "B2" if number <= 107 else "B2-C1")
            self.assertEqual(source.count('name="podo:proofread-status"'), 1, number)
            self.assertEqual(check_deck.meta_content(source, "podo:proofread-status"), "complete")

    def test_polite_spiral_keeps_the_sentence_stable_and_choices_small(self):
        rows = batch.SPIRAL_CHOICES["POLITE-01"]
        self.assertEqual(rows[0][0], "距離のある相手へ：送って{t}いただけますか{/t}？")
        self.assertEqual(rows[1][0], "親しい同僚へ：時間があるときに{t}確認してくれる{/t}？")
        self.assertEqual((rows[0][1], rows[0][4]), ("Would you ", " send it over?"))
        self.assertEqual((rows[1][1], rows[1][4]), ("", " check it when you get a sec?"))
        selectable = {choice for row in rows for choice in row[2:4]}
        self.assertNotIn("Would you be able to", selectable)
        self.assertNotIn("check it when you get a sec", selectable)
        self.assertTrue(all(len(choice.split()) <= 3 for choice in selectable))
        for number in (108, 110, 112):
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["spiral-polite-01"]
            self.assertIn("Would you ", page)
            self.assertIn(" send it over?", page)
            self.assertEqual(check_deck.smallest_unit_choice_issues({"spiral-polite-01": page}), [])

    def test_semantic_specs_are_complete_and_rules_are_visible_operations(self):
        for number, spec in batch.SPECS.items():
            self.assertEqual(len(spec["meanings"]), 2, number)
            self.assertEqual(len(spec["writes"]), 2, number)
            self.assertEqual(len(spec["choices"]), 2, number)
            self.assertEqual(len(spec["rules"]), 2, number)
            self.assertEqual(len(spec["tip"]), 6, number)
            for title, title_ja, formula, heading, heading_ja, examples in spec["rules"]:
                self.assertTrue(all((title, title_ja, formula, heading, heading_ja)))
                self.assertEqual(len(examples), 2)
                self.assertIn("<b>", formula)

    def test_choices_are_small_and_reconstruct_their_own_examples(self):
        for number, spec in batch.SPECS.items():
            omitted = set(batch.LESSONS[number].get("omit_choice", ()))
            for part, choices in enumerate(spec["choices"], 1):
                if part in omitted:
                    self.assertEqual(choices, (), (number, part))
                    continue
                examples = {shared_core.strip_marks(row[0]) for row in batch.LESSONS[number][f"p{part}"]}
                self.assertEqual(len(choices), 4, (number, part))
                for japanese, prefix, correct, distractor, suffix in choices:
                    self.assertEqual(japanese.count("{t}"), 1, (number, part, japanese))
                    self.assertEqual(japanese.count("{/t}"), 1, (number, part, japanese))
                    self.assertNotEqual(correct, distractor)
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertLessEqual(len(distractor.split()), 3, (number, part, distractor))
                    self.assertIn(prefix + correct + suffix, examples, (number, part, prefix + correct + suffix))

        # CORE-104's old choices only recovered content nouns/names or repeated
        # one fixed relative word. Neither was a useful decision, so both pages
        # are deliberately absent instead of manufacturing distractors.
        self.assertEqual(batch.LESSONS[104]["omit_choice"], (1, 2))
        self.assertEqual(batch.SPECS[104]["choices"], ((), ()))
        for part in (0, 1):
            for japanese, _prefix, correct, distractor, _suffix in batch.SPECS[112]["choices"][part]:
                self.assertIn("形容詞", japanese)
                self.assertFalse(correct.endswith("ly"), correct)
                self.assertTrue(distractor.endswith("ly"), distractor)

    def test_reorders_use_four_meaningful_units_or_one_documented_exception(self):
        actual = set()
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                shared_core.validate_reorder_pattern(data[f"p{part}"])
                if part in data.get("omit_reorder", ()):
                    actual.add((number, part))
                    _, source = batch.build(number, data)
                    self.assertNotIn(f'data-page-id="p{part}-reorder"', source)
                    continue
                counts = {len(row[2].split("|")) for row in data[f"p{part}"]}
                self.assertEqual(len(counts), 1, (number, part, counts))
                count = counts.pop()
                self.assertIn(count, (3, 4), (number, part, count))
                if count == 3:
                    actual.add((number, part))
        self.assertEqual(actual, set(batch.THREE_CHIP_EXCEPTIONS))
        self.assertTrue(all(len(reason.split()) >= 7 for reason in batch.THREE_CHIP_EXCEPTIONS.values()))

        for number in (109, 110, 111):
            for part in (1, 2):
                if part in batch.LESSONS[number].get("omit_reorder", ()):
                    continue
                for _english, _japanese, pattern in batch.LESSONS[number][f"p{part}"]:
                    chips = pattern.split("|")
                    self.assertFalse({"won't", "walk", "been", "has", "is"} & set(chips), (number, part, chips))
                    self.assertNotIn(("walk", "away."), tuple(zip(chips, chips[1:])), (number, part, chips))

    def test_translation_hints_are_exactly_row_aligned(self):
        banned_hint_tokens = {"a", "an", "the", "is", "are", "was", "were", "who", "that"}
        for number in batch.NUMBERS:
            data = batch.LESSONS[number]
            for part in (1, 2):
                hints = batch.TRANSLATE_HINTS[number][part - 1]
                self.assertEqual(len(hints), len(data[f"p{part}"]))
                for row, hint_text in zip(data[f"p{part}"], hints, strict=True):
                    english = shared_core.strip_marks(row[0]).casefold()
                    sentence_forms = {form for token in tokens(english) for form in forms(token)}
                    for hint in hint_text.split("; "):
                        target = hint.split(":", 1)[1].casefold()
                        target_tokens = tokens(target)
                        self.assertTrue(target_tokens, (number, part, hint))
                        self.assertTrue(all(forms(token) & sentence_forms for token in target_tokens),
                                        (number, part, english, target))
                        self.assertFalse(set(target_tokens) <= banned_hint_tokens,
                                         (number, part, "grammar-only hint", hint))

    def test_open_writes_name_the_exact_communicative_frame(self):
        fixed_frame_chips = {
            "worries", "matters", "longer", "harder", "sooner", "one thing",
            "worth raising", "as for", "coming back to", "when you get a sec",
            "bluntly", "honestly", "i'm afraid", "just so you know", "heads up",
            "come across as",
        }
        for number, spec in batch.SPECS.items():
            for part, (english, japanese) in enumerate(spec["writes"], 1):
                frame = batch.WRITE_FRAMES[number][part - 1]
                self.assertTrue(english.startswith(f'Use “{frame}” to '), (number, part, english))
                self.assertTrue(japanese.startswith(f'「{frame}」を使って、'), (number, part, japanese))
                _, source = batch.build(number, batch.LESSONS[number])
                page = dict(check_deck.pages(source))[f"p{part}-write"]
                self.assertIn(shared_core.esc(english), page, (number, part))
                self.assertIn(shared_core.esc(japanese), page, (number, part))
                menu_values = {
                    item.split(":", 1)[1].casefold()
                    for item in batch.OPEN_MENUS[number][part - 1]
                }
                self.assertFalse(menu_values & fixed_frame_chips,
                                 (number, part, menu_values & fixed_frame_chips))

    def test_vocabulary_is_parseable_and_every_hint_is_declared(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            vocabulary.parse(source, source=f"CORE-{number}")
            self.assertLessEqual(len(self.words(number, "new")), 8, number)
            self.assertTrue(vocabulary.hint_words(source) <= self.words(number), (number, vocabulary.hint_words(source) - self.words(number)))

    def test_recycled_words_have_exact_visible_earlier_owners(self):
        for number, values in batch.VOCAB.items():
            for entry in filter(None, values["recycled"].split("; ")):
                word, japanese, owner = entry.split("|")
                self.assertTrue(japanese)
                self.assertLess(int(owner.removeprefix("CORE-")), number)
                self.assertIn(word.casefold(), self.source_new_words(owner), (number, word, owner))

    def test_reviewed_productive_ownership_is_exact(self):
        def entries(number, category):
            return {
                tuple(item.split("|"))
                for item in batch.VOCAB[number][category].split("; ") if item
            }

        self.assertIn(("concern", "懸念"), entries(103, "new"))
        self.assertIn(("suggest", "提案する", "CORE-103"), entries(104, "recycled"))
        self.assertIn(("final version", "最終版", "CORE-83"), entries(104, "recycled"))
        self.assertIn(("suggest", "提案する", "CORE-103"), entries(106, "recycled"))
        self.assertIn(("point", "要点", "CORE-85"), entries(106, "recycled"))
        self.assertIn(("concern", "懸念", "CORE-103"), entries(106, "recycled"))
        self.assertIn(("update", "更新する", "CORE-37"), entries(111, "recycled"))
        self.assertIn(("behind", "後ろに", "CORE-11"), entries(110, "recycled"))
        self.assertNotIn(("behind", "予定より遅れている"), entries(110, "new"))
        self.assertIn(("behind schedule", "予定より遅れて"), entries(110, "new"))
        self.assertIn(("hate to say", "言いにくいですが"), entries(110, "new"))
        self.assertIn(("came across as", "〜という印象を与えた"), entries(112, "new"))
        self.assertIn(("cold", "冷たい"), entries(112, "new"))
        self.assertIn(("send over", "送る"), entries(108, "new"))
        self.assertNotIn("送ってよこす", str((batch.VOCAB[108], batch.TRANSLATE_HINTS[108], batch.OPEN_MENUS[108])))

    def test_core92_to_102_map_is_visible_and_has_no_false_citations(self):
        stable = {
            92: {"entirely convinced", "before deciding"}, 93: {"to be fair", "that said"},
            94: {"wouldn't it be better if", "what if"}, 95: {"push back", "take into account"},
            96: {"i meant", "trying to say"}, 97: {"would rather not", "another time"},
            98: {"mostly because of", "comes from", "misunderstanding"},
            99: {"suggests that", "would explain"}, 100: {"as a result", "that meant", "reschedule"},
            101: {"depends on whether", "either way"}, 102: {"otherwise"},
        }
        for number, expected in stable.items():
            self.assertEqual(self.source_new_words(f"CORE-{number}"), expected, number)
        citations = " ".join(v["recycled"] for v in batch.VOCAB.values())
        self.assertNotRegex(citations, r"CORE-(?:9[2-9]|10[0-2])")

    def test_new_words_are_productive_or_visible_support(self):
        for number in EXPECTED:
            productive_and_support = " ".join(map(str, (
                batch.LESSONS[number], batch.SPECS[number], batch.OPEN_MENUS[number],
                batch.SUPPORT_EXPRESSIONS[number], batch.LIVE_SCENES[number],
            ))).casefold()
            for word in self.words(number, "new"):
                self.assertIn(word.casefold(), productive_and_support, (number, word))

    def test_derived_learner_language_has_productive_coverage(self):
        for number, data in batch.LESSONS.items():
            declared = [
                entry.split("|", 1)[0]
                for category, raw in batch.VOCAB[number].items() if category != "receptive"
                for entry in raw.split("; ") if entry
            ]
            declared_forms = {form for entry in declared for token in tokens(entry) for form in forms(token)}
            produced = [shared_core.strip_marks(row[0]) for part in ("p1", "p2") for row in data[part]]
            produced += [batch.DIALOGUES[number][variant][6][0] for variant in ("model", "wild")]
            missing = {
                token for line in produced for token in tokens(line.replace("___ing", "___"))
                if token not in FUNCTION_WORDS and not (forms(token) & declared_forms)
            }
            self.assertEqual(missing, set(), (number, sorted(missing)))

    def test_exact_brief_models_and_support_are_visible(self):
        for number, models in batch.BRIEF_PRODUCTION_MODELS.items():
            _, source = batch.build(number, batch.LESSONS[number])
            visible = html_lib.unescape(re.sub(r"<[^>]+>", "", source))
            for model in models:
                self.assertIn(model, visible, (number, model))
            support = html_lib.unescape(re.sub(r"<[^>]+>", "", dict(check_deck.pages(source))["supporting-expressions"]))
            for english, japanese in batch.SUPPORT_EXPRESSIONS[number]:
                self.assertIn(english, support, (number, english))
                self.assertIn(japanese, support, (number, japanese))

    def test_whole_sentence_and_pattern_inputs_wrap_in_static_markup(self):
        for number, data in batch.LESSONS.items():
            out, source = batch.build(number, data)
            self.assertIn('href="growing-inputs.css"', source)
            self.assertEqual(source.count('src="growing-inputs.js"'), 1)
            self.assertNotRegex(source, r'<input class="(?:space-input|free-input phrase-input|slot-input)"')
            self.assertGreaterEqual(source.count('<textarea class="space-input"'), 8, number)
            self.assertGreaterEqual(source.count('<textarea class="free-input phrase-input"'), 4, number)
            self.assertGreaterEqual(source.count('<textarea class="slot-input phrase-input"'), 8, number)
            css = out.with_name("growing-inputs.css")
            self.assertEqual(css.read_text(encoding="utf-8"), batch.NARROW_GROWING_INPUT_CSS)
            js = out.with_name("growing-inputs.js")
            self.assertEqual(js.read_text(encoding="utf-8"), batch.NARROW_GROWING_INPUT_JS)
        self.assertNotIn("overflow: hidden", batch.NARROW_GROWING_INPUT_CSS)
        self.assertNotIn("field-sizing", batch.NARROW_GROWING_INPUT_CSS)
        self.assertIn("scrollHeight", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("control.scrollHeight > control.clientHeight + 1", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("style.height = 'auto'", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("addEventListener('input'", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("addEventListener('change'", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("ResizeObserver", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("MutationObserver", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn(".pg-on ${selector}", batch.NARROW_GROWING_INPUT_JS)
        self.assertIn("requestAnimationFrame(() => grow(control))", batch.NARROW_GROWING_INPUT_JS)

    def test_live_exchange_is_audio_safe_reciprocal_and_truthful(self):
        expected_roles = (("text", "other", "Tutor"), ("input", "me", "Me"), ("text", "me", "Me"), ("input", "other", "Tutor"))
        for number, scene in batch.LIVE_SCENES.items():
            self.assertEqual(tuple(turn[:3] for turn in scene), expected_roles, number)
            self.assertEqual(scene[1][3:], ("Student's answer", "自分の答え"), number)
            self.assertEqual(scene[3][3:], ("Tutor's answer", "先生の答え"), number)
            self.assertEqual(scene[0][3:], batch.FREE_TALK[number][:2], number)
            self.assertEqual(scene[2][3:], batch.FREE_TALK[number][2:], number)
            self.assertTrue(scene[0][3].endswith("?"), number)
            self.assertTrue(scene[2][3].startswith("What about you"), number)
            self.assertTrue(scene[2][3].endswith("?"), number)
            self.assertNotIn("___", scene[0][3] + scene[2][3], number)
            self.assertNotRegex(" ".join(turn[3] for turn in scene).casefold(), r"look at me|watch me|gesture")
            self.assertEqual(batch.LIVE_HINTS[number], {}, number)
            _, source = batch.build(number, batch.LESSONS[number])
            page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertIn(shared_core.esc(scene[0][3]), page, number)
            self.assertIn(shared_core.esc(scene[2][3]), page, number)
            self.assertIn("Use today's pattern only if it fits", page, number)

    def test_rendered_translation_role_and_target_contracts_are_explicit(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                translate = pages[f"p{part}-translate"]
                self.assertIn('data-scaffolding-contract="target-v2"', translate, (number, part))
                self.assertIn('data-support-stage="supported"', translate, (number, part))
                self.assertGreaterEqual(translate.count('class="hint-chip"'), 4, (number, part))
            for page_id, variant in (("p3-model", "model"), ("p3-complete", "model"),
                                     ("in-the-wild", "wild")):
                role = batch.DIALOGUES[number][variant][0]
                self.assertIn(batch.ROLE_JA[role], pages[page_id], (number, page_id, role))
                self.assertNotIn("相手役", pages[page_id], (number, page_id))

    def test_model_completion_and_transfer_are_resolved_six_turn_scenes(self):
        for number, data in batch.LESSONS.items():
            _, source = batch.build(number, data)
            pages = dict(check_deck.pages(source))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)
            for variant in ("model", "wild"):
                jobs = batch.DIALOGUE_SEMANTIC_LEDGER[number][variant]
                self.assertEqual(len(jobs), 6, (number, variant))
                self.assertEqual(len(set(jobs)), 6, (number, variant))
                dialogue = batch.DIALOGUES[number][variant]
                self.assertNotEqual(dialogue[6][0], shared_core.strip_marks(data["p1"][dialogue[1]][0]))
                self.assertNotEqual(dialogue[6][0], shared_core.strip_marks(data["p2"][dialogue[2]][0]))

    def test_semantic_regressions_lock_context_register_and_repair(self):
        self.assertIn("one more week", batch.DIALOGUES[103]["model"][5][0])
        self.assertIn("Who first proposed", batch.DIALOGUES[104]["model"][4][0])
        self.assertIn("rooms are filling up", batch.DIALOGUES[105]["wild"][3][0])
        self.assertIn("anything else before we print", batch.DIALOGUES[106]["wild"][4][0])
        self.assertIn("return to the second option", batch.DIALOGUES[107]["wild"][4][0])
        self.assertIn("new supplier", batch.DIALOGUES[108]["model"][3][0])
        self.assertIn("close teammate", batch.DIALOGUES[108]["model"][4][0])
        self.assertIn("two extra fees", batch.DIALOGUES[109]["wild"][3][0])
        self.assertIn("check the booking", batch.DIALOGUES[110]["wild"][5][0])
        self.assertEqual(batch.DIALOGUES[110]["model"][2], 2)
        self.assertIn("caused the delay", batch.DIALOGUES[110]["model"][4][0])
        self.assertIn("mistake", shared_core.strip_marks(batch.LESSONS[110]["p2"][batch.DIALOGUES[110]["model"][2]][0]))
        self.assertIn("update my calendar", batch.DIALOGUES[111]["model"][5][0])
        self.assertIn("Could you do it today?", batch.DIALOGUES[112]["model"][6][0])

    def test_japanese_and_native_tip_risks_are_locked(self):
        self.assertEqual(batch.LESSONS[103]["p2"][0][1], "{t}私が提案したいのは{/t}、1週間待つことです。")
        self.assertIn("価格ではなく", batch.LESSONS[104]["p1"][0][1])
        self.assertIn("待てば待つほど", batch.LESSONS[105]["p1"][0][1])
        self.assertIn("二つほど", batch.LESSONS[106]["p2"][0][1])
        self.assertIn("話に戻ると", batch.LESSONS[107]["p2"][0][1])
        self.assertIn("親しい同僚", batch.SPECS[108]["tip"][3])
        self.assertEqual(batch.LESSONS[109]["p2"][0][1], "{t}正直に言うと、私なら見送ります{/t}。")
        self.assertIn("文字どおりの恐怖ではない", batch.SPECS[110]["rules"][1][4])
        self.assertIn("中立的な更新", batch.LESSONS[111]["goal"][1])
        self.assertIn("意図と影響を分ける", batch.SPECS[112]["rules"][1][4])

    def test_build_is_deterministic(self):
        first = {n: hashlib.sha256(batch.build(n, batch.LESSONS[n])[1].encode()).hexdigest() for n in batch.NUMBERS}
        second = {n: hashlib.sha256(batch.build(n, batch.LESSONS[n])[1].encode()).hexdigest() for n in batch.NUMBERS}
        self.assertEqual(first, second)

    def test_rendered_sources_match_the_generator_and_checker_is_clean(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertTrue(path.is_file(), number)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, number)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], (number, errors))
            self.assertEqual(warnings, [], (number, warnings))


if __name__ == "__main__":
    unittest.main()
