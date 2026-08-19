#!/usr/bin/env python3
"""Regression contract for the source-first Core 37-47 authoring batch."""

from __future__ import annotations

import hashlib
import html as html_lib
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
    def test_scope_is_exact_and_core45_source_first_repair_is_locked(self):
        self.assertEqual(set(batch.NUMBERS), set(range(37, 48)) - {45})
        self.assertEqual(set(batch.LESSONS), set(batch.NUMBERS))
        preserved = batch.TRACK / "courses" / batch.COURSE / "lessons/45-this-ones-cheaper/lesson.html"
        self.assertEqual(
            hashlib.sha256(preserved.read_bytes()).hexdigest(),
            "dd28bde7103e5bd3bda51e62675f3f7ddcfee37e1f2c05934223c63e24e83104",
        )

    def test_every_semantic_field_is_explicit(self):
        expected = set(batch.NUMBERS)
        for mapping in (
            batch.SPECS, batch.VOCAB, batch.KNOWN_WORDS, batch.DIALOGUES,
            batch.LIVE_SCENES, batch.TRANSLATE_HINTS, batch.OPEN_MENUS,
            batch.GOAL_EXCHANGES,
        ):
            self.assertEqual(set(mapping), expected)
        for number in batch.NUMBERS:
            self.assertEqual(set(batch.VOCAB[number]), {"new", "recycled", "assumed", "receptive"})
            self.assertEqual(len(batch.SPECS[number]["meanings"]), 2)
            self.assertEqual(len(batch.SPECS[number]["writes"]), 2)
            self.assertEqual(len(batch.SPECS[number]["rules"]), 2)
            self.assertEqual(len(batch.SPECS[number]["choices"]), 2)
            self.assertEqual(len(batch.GOAL_EXCHANGES[number]), 3)

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

    def test_choices_rebuild_targets_and_use_smallest_meaningful_units(self):
        for number, data in batch.LESSONS.items():
            omitted = set(data.get("omit_choose", ()))
            for part in (1, 2):
                choices = batch.SPECS[number]["choices"][part - 1]
                if part in omitted:
                    self.assertEqual(choices, ())
                    continue
                self.assertEqual(len(choices), 4)
                for index, (japanese, prefix, correct, distractor, suffix) in enumerate(choices):
                    target = core.strip_marks(data[f"p{part}"][index][0])
                    self.assertEqual(prefix + correct + suffix, target, (number, part, index))
                    self.assertNotEqual(correct, distractor)
                    self.assertEqual(japanese.count("{t}"), 1)
                    self.assertLessEqual(len(correct.split()), 3, (number, part, correct))
                    self.assertFalse(re.search(r"[.!?]", correct), (number, part, correct))

    def test_reorders_are_honest_or_explicitly_omitted(self):
        for number, data in batch.LESSONS.items():
            for part in (1, 2):
                if part not in data.get("omit_reorder", ()):
                    core.validate_reorder_pattern(data[f"p{part}"])

    def test_vocabulary_provenance_and_scaffolds_are_complete(self):
        for number in batch.NUMBERS:
            owned = set()
            new_entries = list(filter(None, batch.VOCAB[number]["new"].split("; ")))
            self.assertLessEqual(len(new_entries), 8)
            for category, value in batch.VOCAB[number].items():
                for entry in filter(None, value.split("; ")):
                    pieces = entry.split("|")
                    self.assertEqual(len(pieces), 3 if category == "recycled" else 2, (number, entry))
                    owned.add(pieces[0].casefold())
                    if category == "recycled":
                        source_id = pieces[2]
                        self.assertLess(int(source_id.removeprefix("CORE-")), number, (number, entry))
                        source = next(
                            path for path in batch.TRACK.rglob("lesson.html")
                            if f'content="{source_id}"' in path.read_text(encoding="utf-8")
                        )
                        source_new = {
                            item["english"].casefold()
                            for item in vocabulary.parse(source.read_text(encoding="utf-8"))["categories"]["new"]
                        }
                        self.assertIn(pieces[0].casefold(), source_new, (number, entry))
            for _, english in batch.KNOWN_WORDS[number]:
                self.assertIn(english.casefold(), owned)
            for part in (0, 1):
                self.assertEqual(len(batch.TRANSLATE_HINTS[number][part]), 4)
                self.assertTrue(batch.OPEN_MENUS[number][part])
            learner_inputs = {
                index for index, event in enumerate(batch.LIVE_SCENES[number])
                if event[0:2] == ("input", "me")
            }
            self.assertEqual(set(batch.LIVE_HINTS[number]), learner_inputs)

    def test_new_vocabulary_has_one_chronological_owner(self):
        owners = {}
        for path in batch.TRACK.rglob("lesson.html"):
            source = path.read_text(encoding="utf-8")
            match = re.search(r'<meta name="podo:review-id" content="CORE-(\d+)"', source)
            if not match or int(match.group(1)) >= 37:
                continue
            for item in vocabulary.parse(source)["categories"]["new"]:
                owners.setdefault(item["english"].casefold(), int(match.group(1)))

        preserved = batch.TRACK / "courses" / batch.COURSE / "lessons/45-this-ones-cheaper/lesson.html"
        for number in range(37, 48):
            if number == 45:
                source = preserved.read_text(encoding="utf-8")
            else:
                source = batch.build(number, batch.LESSONS[number])[1]
            for item in vocabulary.parse(source)["categories"]["new"]:
                key = item["english"].casefold()
                self.assertNotIn(key, owners, (number, item["english"], owners.get(key)))
                owners[key] = number

    def test_dialogues_are_coherent_exact_six_turn_replays(self):
        nonrepeating_closures = {
            (38, "wild"), (40, "wild"), (41, "wild"),
            (42, "model"), (42, "wild"), (43, "wild"),
            (46, "wild"), (47, "model"), (47, "wild"),
        }
        for number, data in batch.LESSONS.items():
            allowed = {
                core.strip_marks(row[0]).replace("’", "'")
                for part in ("p1", "p2") for row in data[part]
            }
            for variant in ("model", "wild"):
                dialogue = batch.DIALOGUES[number][variant]
                self.assertEqual(len(dialogue), 7)
                final, owner = batch.FINAL_LINE_OWNERSHIP[number][variant]
                self.assertEqual(final, dialogue[6][0], (number, variant))
                self.assertTrue(owner.strip(), (number, variant))
                source_match = re.match(r"CORE-(\d+) supporting response", owner)
                if source_match:
                    source_id = f"CORE-{source_match.group(1)}"
                    source = next(
                        path for path in batch.TRACK.rglob("lesson.html")
                        if f'content="{source_id}"' in path.read_text(encoding="utf-8")
                    )
                    self.assertIn(final, html_lib.unescape(source.read_text(encoding="utf-8")))
                if "current pattern" in owner:
                    self.assertIn(final.replace("’", "'"), allowed, (number, variant, final))
                if (number, variant) in nonrepeating_closures:
                    selected = {
                        core.strip_marks(data["p1"][dialogue[1]][0]).replace("’", "'"),
                        core.strip_marks(data["p2"][dialogue[2]][0]).replace("’", "'"),
                    }
                    self.assertNotIn(final.replace("’", "'"), selected, (number, variant, final))
            _, html = batch.build(number, data)
            pages = dict(check_deck.pages(html))
            for page_id in ("p3-model", "p3-complete", "in-the-wild"):
                self.assertEqual(pages[page_id].count('class="turn '), 6, (number, page_id))
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]),
            )

    def test_generated_decks_are_exact_complete_and_canonical(self):
        for number, data in batch.LESSONS.items():
            path, expected = batch.build(number, data)
            self.assertEqual(path.read_text(encoding="utf-8"), expected)
            pages = dict(check_deck.pages(expected))
            omitted_choices = set(data.get("omit_choose", ()))
            for part in (1, 2):
                self.assertEqual(f"p{part}-choose" in pages, part not in omitted_choices, (number, part))
            self.assertEqual(check_deck.core_canonical_shape_issues(pages), [], number)
            self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [], number)
            self.assertEqual(check_deck.phrase_input_structure_issues(expected), [], number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete")
            self.assertEqual(
                len(re.findall(r'<meta name="podo:proofread-status"', expected)),
                1,
                number,
            )
            ids = re.findall(r'data-sync-id="([^"]+)"', expected)
            self.assertEqual(len(ids), len(set(ids)), number)

    def test_finalization_changes_only_one_status_marker_per_deck(self):
        status_stripped_hashes = {
            37: "7a0be0dda513b7658a9796a690371a9a36a88ef3c51ea995fff245bfa1334018",
            38: "6d0f03380abfd22b5c4972bf4fc2f475b72cb2a28a05c4dc4967bc3aaa98c1f5",
            39: "272c221ec63f3b476e3396e264f047c10bed27570ba31a90bb46ac8acb39cc72",
            40: "bb71ca3fabf26e278cbcbce4442bb679dfe8e7009d6d9b0ebc35eb59bc5f7f6c",
            41: "5d785fbb9a76fe92ca462569bcb05434d8c1c4ba67aaf0e7dc9cebf20858986e",
            42: "53ea3a664bc0e22d9fbe94560f0f4dcd51db2113c424c3b57da10c3f25597b86",
            43: "1b360a0ca641c32b09ab7402a557182f6d3eb6a8c6ba95d602e3228bb118bac3",
            44: "b205e324371be81b20a741962ffc414eb6c53f69e3b8a59c921132c07414a2ac",
            45: "fad9de660ac0de30ff9b5e47df0fac5d9810a8ebb4376d5c8b5f188738518ba7",
            46: "00444a34adb9fae2d18e237047ac9d8214d37a0e65bbdb68a83ccf3a888713b4",
            47: "8b5d0a25e7730a6214bd0df1a78972acc1d67b3133cd85c86c4e849a2c00626c",
        }
        lessons = batch.TRACK / "courses" / batch.COURSE / "lessons"
        for path in sorted(lessons.glob("*/lesson.html")):
            number = int(path.parent.name.split("-", 1)[0])
            source = path.read_text(encoding="utf-8")
            self.assertEqual(
                re.findall(r'<meta name="podo:proofread-status" content="([^"]+)"', source),
                ["complete"],
                number,
            )
            stripped = re.sub(
                r'\n\s*<meta name="podo:proofread-status" content="[^"]*"\s*/?>',
                "",
                source,
            )
            self.assertEqual(
                hashlib.sha256(stripped.encode("utf-8")).hexdigest(),
                status_stripped_hashes[number],
                number,
            )

    def test_independent_review_repairs_are_source_locked(self):
        self.assertEqual(batch.LESSONS[38]["ja"], "私が手伝います")
        self.assertIn("about it", batch.SPECS[37]["tip"][2])
        self.assertNotIn("thinking about", batch.SPECS[37]["tip"][2].casefold())
        self.assertEqual(batch.DIALOGUES[37]["model"][5][0], "A new bag. What are you going to do first?")
        self.assertEqual(batch.DIALOGUES[37]["wild"][6][0], "I'm going to take an online course.")

        self.assertEqual(batch.DIALOGUES[38]["model"][5][1], "よかった。任せても大丈夫ですか？")
        self.assertEqual(batch.LIVE_SCENES[38][0][3], "I need to carry this box.")
        self.assertEqual(batch.LIVE_SCENES[38][1][3], "Let me ___ for you.")
        self.assertEqual(batch.OPEN_MENUS[38][0], ("箱を運ぶ:carry the box",))
        first_action = batch.OPEN_MENUS[38][0][0].split(":", 1)[1]
        self.assertEqual(
            batch.LIVE_SCENES[38][1][3].replace("___", first_action, 1),
            "Let me carry the box for you.",
        )
        self.assertEqual(
            batch.LIVE_SCENES[38][2][3],
            "Thanks. I also need to send these files by noon. Can you do that?",
        )
        self.assertEqual(
            batch.OPEN_MENUS[38][1],
            ("ファイルを送る:send the files", "正午:noon"),
        )
        promise = batch.LIVE_SCENES[38][3][3]
        for hint in batch.OPEN_MENUS[38][1]:
            promise = promise.replace("___", hint.split(":", 1)[1], 1)
        self.assertEqual(promise, "Don't worry, I'll send the files by noon.")
        self.assertEqual(
            batch.LESSONS[38]["prompt"],
            ("Offer to help me now, then make a promise about a second task.",
             "今できる手助けを申し出てから、別の作業について約束してください。"),
        )
        self.assertNotIn("about it", " ".join(batch.LESSONS[38]["prompt"]).casefold())
        self.assertNotIn("heavy", repr((batch.LESSONS[38], batch.LIVE_SCENES[38], batch.OPEN_MENUS[38])).casefold())
        owned38 = {
            entry.split("|", 1)[0].casefold()
            for value in batch.VOCAB[38].values()
            for entry in filter(None, value.split("; "))
        }
        self.assertTrue(
            {"need", "carry", "carry the box", "box", "file", "send", "send the files", "noon"}
            <= owned38
        )
        self.assertNotIn("When will you do it?", repr(batch.LIVE_SCENES[38]))
        self.assertIsNone(re.search(r"\brain\b", repr(batch.SPECS[39]), re.IGNORECASE))

        core40 = repr((batch.LESSONS[40], batch.VOCAB[40], batch.TRANSLATE_HINTS[40],
                       batch.OPEN_MENUS[40], batch.SPECS[40], batch.DIALOGUES[40],
                       batch.LIVE_SCENES[40]))
        self.assertNotIn("medicine", core40.casefold())
        self.assertIn("I didn't sleep well last night", batch.LIVE_SCENES[40][0][3])
        self.assertIn("I have a headache", batch.LIVE_SCENES[40][4][3])

        rule41 = repr(batch.SPECS[41]["rules"][1]).casefold()
        self.assertIn("don't have to", rule41.replace("’", "'"))
        self.assertIn("mustn't", rule41.replace("’", "'"))
        self.assertEqual(batch.DIALOGUES[41]["model"][0], "Museum visitor")
        self.assertEqual(batch.DIALOGUES[41]["wild"][0], "Office visitor")

        for part in ("p1", "p2"):
            self.assertTrue(all("？" in row[1] for row in batch.LESSONS[42][part]))
        for choice_group in batch.SPECS[42]["choices"]:
            self.assertTrue(all("？" in row[0] for row in choice_group))
        self.assertIn("作ります", batch.LESSONS[42]["p1"][3][1])
        self.assertNotIn("好きです", batch.LESSONS[42]["p1"][3][1])
        self.assertTrue(batch.DIALOGUES[42]["model"][4][0].startswith("Don't"))
        self.assertTrue(batch.DIALOGUES[42]["wild"][4][0].startswith("Don't"))
        _, core42_html = batch.build(42, batch.LESSONS[42])
        core42_pages = dict(check_deck.pages(core42_html))
        self.assertIn("？」→", core42_pages["p1-read"])
        for page_id in ("p3-model", "p3-complete", "in-the-wild"):
            self.assertNotIn("？」→", core42_pages[page_id])

        self.assertEqual(batch.DIALOGUES[43]["wild"][0], "Prospective renter")
        self.assertEqual(batch.DIALOGUES[44]["model"][6][0], "Yes, please.")
        self.assertEqual(batch.DIALOGUES[44]["wild"][6][0], "Yes, please.")

        core46 = repr((batch.LESSONS[46], batch.SPECS[46], batch.LIVE_SCENES[46]))
        self.assertNotIn("strongest option", core46.casefold())
        self.assertIn("the most comfortable", core46)
        self.assertIn("express—35 min", batch.LIVE_SCENES[46][0][3])
        self.assertIn("express and the bus", batch.LIVE_SCENES[46][2][3])
        self.assertEqual(batch.OPEN_MENUS[46][1], ("急行:express", "バス:bus"))


if __name__ == "__main__":
    unittest.main()
