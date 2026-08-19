#!/usr/bin/env python3
"""Regression contract for the explicit Core 25-36 missing-deck batch."""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_deck
import generate_core_course_batch as core
import generate_core_daily_life_and_past_batch as batch
import vocabulary


TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
LEARNER_FUNCTION_WORDS = {
    "a", "an", "the", "i", "i'm", "i'd", "my", "you", "your", "he", "she", "it", "we", "us", "our",
    "they", "yes", "no", "me", "am", "is", "are", "be", "been", "did", "do", "does", "has", "have",
    "to", "of", "in", "on", "at", "for", "from", "with", "and", "but", "then", "or", "not", "there",
    "this", "that", "what", "how", "why", "where", "after", "before", "out", "now", "last",
}


def word_forms(word):
    forms = {word}
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
    return TOKEN_RE.findall(text.casefold().replace("’", "'"))


class CoreDailyLifeAndPastBatchTests(unittest.TestCase):
    def test_scope_is_exact_and_core32_is_immutable(self):
        self.assertEqual(set(batch.NUMBERS), set(range(25, 37)) - {32})
        self.assertEqual(set(batch.LESSONS), set(batch.NUMBERS))
        digest = hashlib.sha256(batch.PRESERVED.read_bytes()).hexdigest()
        self.assertEqual(digest, "3ea3b1d966afab071b762cd20a5f5787fd50c1ea25a59630f6afb11b066a25a7")
        core32 = vocabulary.parse(batch.PRESERVED.read_text(encoding="utf-8"))["categories"]
        self.assertEqual(
            {(e["english"], e["source"]) for e in core32["recycled"]},
            {("went", "CORE-31"), ("café", "CORE-7"), ("restaurant", "CORE-10")},
        )

    def test_every_semantic_field_is_explicit(self):
        expected = set(batch.NUMBERS)
        for mapping in (batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS, batch.DIALOGUES,
                        batch.LIVE_SCENES, batch.TRANSLATE_HINTS, batch.OPEN_MENUS):
            self.assertEqual(set(mapping), expected)
        for n in batch.NUMBERS:
            self.assertEqual(set(batch.VOCAB[n]), {"new", "recycled", "assumed", "receptive"})
            self.assertEqual(len(batch.SPECS[n]["meanings"]), 2)
            self.assertEqual(len(batch.SPECS[n]["rules"]), 2)
            self.assertEqual(len(batch.SPECS[n]["choices"]), 2)

    def test_authoritative_models_and_frames_are_locked(self):
        expected = {
            25: ("I'm working from home today.", "What are you doing?"),
            26: ("I usually drive to work.", "But today I'm walking."),
            27: ("I like cooking.", "I love walking, but I hate running."),
            28: ("Are you free on Friday?", "Would you like to have dinner?"),
            29: ("I'm meeting Sam at six.", "Are you still coming on Tuesday?"),
            30: ("I was really tired yesterday.", "There were a lot of people."),
            31: ("I went to a concert last night.", "I stayed home and watched a movie."),
            33: ("Did you have a good time?", "Yes, we did. It was great."),
            34: ("I didn't sleep well.", "I had too much coffee."),
            35: ("First we ate, and then we walked around.", "In the end, we took a taxi home."),
            36: ("I was cooking when you called.", "While I was cooking, he set the table."),
        }
        for n, models in expected.items():
            self.assertEqual(tuple(core.strip_marks(batch.LESSONS[n][f"p{p}"][0][0]) for p in (1, 2)), models)
        self.assertTrue(all(core.strip_marks(r[0]).startswith("There were a lot of ") for r in batch.LESSONS[30]["p2"]))
        self.assertTrue(all(core.strip_marks(r[0]).startswith("I had too much ") for r in batch.LESSONS[34]["p2"]))
        self.assertTrue(all(" when you " in core.strip_marks(r[0]) for r in batch.LESSONS[36]["p1"]))
        self.assertTrue(all(core.strip_marks(r[0]).startswith("While I was ") and ", he " in core.strip_marks(r[0]) for r in batch.LESSONS[36]["p2"]))

    def test_choices_rebuild_targets_and_are_small_units(self):
        for n in batch.NUMBERS:
            for part in (1, 2):
                choices = batch.SPECS[n]["choices"][part - 1]
                self.assertEqual(len(choices), 4)
                for i, (ja, prefix, correct, wrong, suffix) in enumerate(choices):
                    self.assertEqual(prefix + correct + suffix, core.strip_marks(batch.LESSONS[n][f"p{part}"][i][0]))
                    self.assertNotEqual(correct, wrong)
                    self.assertEqual(ja.count("{t}"), 1)
                    self.assertLessEqual(len(correct.split()), 4)
                    self.assertNotIn(".", correct)

    def test_reorders_are_honest_or_explicitly_omitted(self):
        for n, data in batch.LESSONS.items():
            for part in (1, 2):
                if part not in data.get("omit_reorder", ()):
                    core.validate_reorder_pattern(data[f"p{part}"])
        self.assertEqual(batch.LESSONS[25]["omit_reorder"], (1, 2))
        self.assertIn(2, batch.LESSONS[26]["omit_reorder"])
        self.assertEqual(batch.LESSONS[29]["omit_reorder"], (1, 2))

    def test_vocabulary_provenance_and_scaffolds_are_complete(self):
        for n in batch.NUMBERS:
            owned = set()
            for category, value in batch.VOCAB[n].items():
                for entry in filter(None, value.split("; ")):
                    pieces = entry.split("|")
                    self.assertEqual(len(pieces), 3 if category == "recycled" else 2, (n, entry))
                    owned.add(pieces[0].casefold())
                    if category == "recycled":
                        source_id = pieces[2]
                        self.assertLess(int(source_id.removeprefix("CORE-")), n)
                        source = next(
                            p for p in batch.TRACK.rglob("lesson.html")
                            if f'content="{source_id}"' in p.read_text(encoding="utf-8")
                        )
                        source_new = {
                            e["english"].casefold()
                            for e in vocabulary.parse(source.read_text(encoding="utf-8"))["categories"]["new"]
                        }
                        self.assertIn(pieces[0].casefold(), source_new, (n, entry))
            for part in (0, 1):
                self.assertEqual(len(batch.TRANSLATE_HINTS[n][part]), 4)
                self.assertTrue(batch.OPEN_MENUS[n][part])
            self.assertTrue(batch.PRODUCTIVE_VOCABULARY[n] <= owned, (n, sorted(batch.PRODUCTIVE_VOCABULARY[n] - owned)))
            learner_inputs = {i for i, e in enumerate(batch.LIVE_SCENES[n]) if e[0:2] == ("input", "me")}
            self.assertEqual(set(batch.LIVE_HINTS[n]), learner_inputs)

    def test_derived_learner_language_has_non_receptive_ownership(self):
        for n, data in batch.LESSONS.items():
            owned_entries = [
                entry.split("|")[0]
                for category, value in batch.VOCAB[n].items() if category != "receptive"
                for entry in value.split("; ") if entry
            ]
            owned_forms = {
                form
                for entry in owned_entries
                for token in english_tokens(entry)
                for form in word_forms(token)
            }
            produced = [
                core.strip_marks(row[0])
                for part in ("p1", "p2") for row in data[part]
            ] + [batch.DIALOGUES[n][variant][6][0] for variant in ("model", "wild")]
            missing = {
                token
                for line in produced for token in english_tokens(line)
                if token not in LEARNER_FUNCTION_WORDS and not (word_forms(token) & owned_forms)
            }
            self.assertEqual(missing, set(), (n, sorted(missing)))

        self.assertIn("It was fun.", batch.VOCAB[31]["assumed"])
        self.assertIn("Nothing special.", batch.VOCAB[31]["assumed"])
        self.assertNotIn("fun", batch.VOCAB[31]["receptive"].casefold())
        self.assertIn("all of a sudden", batch.VOCAB[36]["new"])
        self.assertIn("at that moment", batch.VOCAB[36]["assumed"])
        self.assertEqual(batch.VOCAB[36]["receptive"], "")
        self.assertIn("very|", batch.VOCAB[30]["assumed"])
        self.assertIn("walked home|", batch.VOCAB[35]["assumed"])

    def test_dialogues_are_six_turn_replays_and_learner_lines_are_owned(self):
        for n, data in batch.LESSONS.items():
            allowed = {core.strip_marks(r[0]) for part in ("p1", "p2") for r in data[part]}
            for variant in ("model", "wild"):
                self.assertEqual(len(batch.DIALOGUES[n][variant]), 7)
                final, owner = batch.FINAL_LINE_OWNERSHIP[n][variant]
                if owner == f"CORE-{n} current pattern":
                    self.assertIn(final, allowed)
                else:
                    self.assertEqual(owner, batch.SUPPORT_LINE_OWNERS[n])
            _, html = batch.build(n, data)
            pages = dict(check_deck.pages(html))
            for pid in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[pid].count('class="turn '), 6, (n, pid))
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]))

    def test_reviewed_dialogue_and_live_branch_repairs_are_locked(self):
        self.assertIn("at the moment", batch.DIALOGUES[25]["wild"][3][0])
        self.assertEqual(batch.DIALOGUES[28]["model"][6][0], "Yes, I'd love to.")
        self.assertEqual(batch.DIALOGUES[28]["wild"][6][0], "Sorry, I can't.")
        self.assertEqual(batch.DIALOGUES[29]["model"][6][0], "See you then.")
        self.assertEqual(batch.DIALOGUES[31]["model"][6][0], "It was fun.")
        self.assertEqual(batch.DIALOGUES[33]["model"][6][0], "Not bad.")
        self.assertEqual(batch.DIALOGUES[34]["model"][6][0], "That's why I didn't sleep well.")
        self.assertEqual(batch.DIALOGUES[36]["model"][6][0], "No—it happened all of a sudden.")
        for n, scene in batch.LIVE_SCENES.items():
            self.assertTrue(any(e[0:2] == ("input", "other") and "Tutor's answer" in e[3] for e in scene), n)
            self.assertTrue(any(e[1] == "me" and ("you" in e[3].casefold() or "how about" in e[3].casefold()) for e in scene), n)
        self.assertIn("name a day you are free", batch.LIVE_SCENES[28][2][3])
        self.assertIn("Use the day I said I was free", batch.LIVE_SCENES[28][3][3])
        for variant in ("model", "wild"):
            core31 = " ".join(turn[0] for turn in batch.DIALOGUES[31][variant][3:] if isinstance(turn, tuple))
            self.assertNotIn("Friday", core31)
            self.assertNotIn("Saturday", core31)
            self.assertIn("the evening before", core31)

            core33 = batch.DIALOGUES[33][variant]
            self.assertIn("friends and I", core33[3][0])
            self.assertRegex(core33[4][0], r"Did you and your .+\?$")
            self.assertTrue(core33[4][0].startswith("Yes, we did."))

            self.assertTrue(batch.DIALOGUES[29][variant][3][0].startswith("What time"))
            self.assertIn("after that", batch.DIALOGUES[35][variant][4][0].casefold())

        self.assertEqual(batch.LIVE_SCENES[29][2][0:2], ("text", "other"))
        self.assertEqual(batch.LIVE_SCENES[29][2][3], "I'm meeting Ken on Tuesday.")
        self.assertIn("my activity and day", batch.LIVE_SCENES[29][3][3])
        self.assertEqual(batch.LIVE_HINTS[29][4], ("ケンと会う:meeting Ken", "火曜日:Tuesday"))
        self.assertRegex(batch.LIVE_SCENES[33][3][3], r"Did you and your friends .+\?$")
        for n in (25, 28, 29, 31, 33, 34, 36):
            tutor_lines = " ".join(
                turn[0] for variant in batch.DIALOGUES[n].values() for turn in variant[3:6]
                if isinstance(turn, tuple)
            ).casefold()
            for coaching in ("ask me", "now answer", "invite me", "now confirm"):
                self.assertNotIn(coaching, tutor_lines, (n, coaching))

    def test_reviewed_hints_and_tips_are_source_locked(self):
        self.assertEqual(batch.TRANSLATE_HINTS[25][1], ("する:do", "読む:read", "作る:make", "見る:watch"))
        self.assertEqual(batch.TRANSLATE_HINTS[26][0][0], "車で行く:drive")
        self.assertEqual(batch.TRANSLATE_HINTS[28][1][0], "夕食:dinner")
        self.assertEqual(batch.TRANSLATE_HINTS[30][1], ("人々:people", "車:cars", "会議:meeting", "店:shop"))
        self.assertEqual(batch.TRANSLATE_HINTS[33][1][1], "楽しい:fun")
        self.assertIn("歩き回った:walked around", batch.TRANSLATE_HINTS[35][0][0])
        self.assertIn("電話した:called", batch.TRANSLATE_HINTS[36][0][0])
        self.assertEqual(batch.SPECS[27]["tip"][0], "Hate or not really my thing?")
        self.assertEqual(batch.SPECS[30]["tip"][0], "To be honest or for some reason?")
        self.assertEqual(batch.SPECS[36]["tip"][0], "All of a sudden or at that moment?")

    def test_every_deck_has_exactly_one_complete_marker(self):
        paths = [batch.PRESERVED] + [batch.build(n, batch.LESSONS[n])[0] for n in batch.NUMBERS]
        for path in paths:
            html = path.read_text(encoding="utf-8")
            self.assertEqual(html.count('name="podo:proofread-status"'), 1, path)
            self.assertEqual(check_deck.meta_content(html, "podo:proofread-status"), "complete", path)

    def test_generated_decks_are_exact_complete_and_canonical(self):
        for n, data in batch.LESSONS.items():
            path, expected = batch.build(n, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected)
            pages = dict(check_deck.pages(expected))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], n)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], n)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete")
            ids = __import__("re").findall(r'data-sync-id="([^"]+)"', expected)
            self.assertEqual(len(ids), len(set(ids)), n)


if __name__ == "__main__":
    unittest.main()
