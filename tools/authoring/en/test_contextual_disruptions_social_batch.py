#!/usr/bin/env python3
"""Regression tests for the explicit CTX 13-24 disruptions-and-social batch."""

from __future__ import annotations

import copy
import pathlib
import re
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_contextual_disruptions_social_batch as batch
import vocabulary


REVIEW_ID = re.compile(r'<meta name="podo:review-id" content="([^"]+)">')
ROOT = pathlib.Path(__file__).resolve().parents[3]
REVIEWED_HTML = range(13, 25)


def source_by_review_id(review_id: str) -> tuple[pathlib.Path, str]:
    for path in (ROOT / "sandbox" / "drafts" / "en" / "tracks").rglob("lesson.html"):
        text = path.read_text(encoding="utf-8")
        match = REVIEW_ID.search(text)
        if match and match.group(1) == review_id:
            return path, text
    raise AssertionError(f"no deck with review id {review_id}")


def entry_floor(number: int) -> int:
    brief = ROOT / "sandbox/drafts/en/tracks/2-contextual-english/toc" / f"CTX-{number}.md"
    match = re.search(r"\*\*Entry floor:\*\* Core (\d+)", brief.read_text(encoding="utf-8"))
    if not match:
        raise AssertionError(f"CTX-{number}: brief has no Core entry floor")
    return int(match.group(1))


def owner_is_reachable(owner: str, number: int) -> bool:
    core_owner = re.fullmatch(r"CORE-(\d+)", owner)
    if core_owner:
        return int(core_owner.group(1)) <= entry_floor(number)
    contextual_owner = re.fullmatch(r"CTX-(\d+)", owner)
    if contextual_owner:
        return int(contextual_owner.group(1)) < number
    return False


class ContextualDisruptionsSocialBatchTests(unittest.TestCase):
    def test_batch_is_two_complete_six_lesson_courses(self):
        self.assertEqual(set(batch.LESSONS), set(range(13, 25)))
        self.assertEqual(set(batch.AUTHORITATIVE), set(batch.LESSONS))
        self.assertEqual({batch.course_for(number) for number in range(13, 19)}, {"ctx-travel-disruptions-urgent-problems"})
        self.assertEqual({batch.course_for(number) for number in range(19, 25)}, {"ctx-travel-independent-social"})

    def test_authoritative_titles_models_and_bilingual_cues_are_preserved(self):
        for number, lesson in batch.LESSONS.items():
            batch.validate_lesson(number, lesson)
            for part in (1, 2):
                for english, japanese, _ in lesson[f"p{part}"]["rows"]:
                    self.assertEqual(english.count("{t}"), english.count("{/t}"), (number, part, english))
                    self.assertEqual(japanese.count("{t}"), japanese.count("{/t}"), (number, part, japanese))
                    self.assertEqual(english.count("{t}"), japanese.count("{t}"), (number, part, english, japanese))

    def test_generated_html_is_exact_and_checker_clean(self):
        # CTX 13-24 have now each completed a bounded source-first review pass.
        for number in REVIEWED_HTML:
            lesson = batch.LESSONS[number]
            path, expected = batch.build(number, lesson)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)
            self.assertEqual(expected.count('name="podo:proofread-status" content="complete"'), 1, path)
            self.assertNotIn('name="podo:proofread-status" content="pending"', expected, path)

    def test_every_deck_keeps_the_full_contextual_arc(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(list(pages)[-1], "transfer-scene", number)
            self.assertNotIn("situation-card", pages, number)
            for required in ("lesson-goal", "scene", "understand", "p1-fill", "p1-translate", "p1-write", "p2-fill", "p2-translate", "p2-write", "p3-model", "p3-complete", "p3-freetalk", "transfer-scene"):
                self.assertIn(required, pages, (number, required))
            self.assertEqual(check_deck.class_tag_count(pages["understand"], "choose-row", "receptive-choice"), 4, number)
            self.assertIn('data-sync-id="p3-real-answer"', pages["p3-freetalk"], number)
            self.assertIn('data-sync-id="p3-tutor-answer"', pages["p3-freetalk"], number)
            self.assertIn('class="nuance-compare"', pages["native-tip"], number)
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                self.assertIn('class="sent-hero"', pages[f"p{part}-teach"], (number, part))
                self.assertIn('class="sent-more"', pages[f"p{part}-teach"], (number, part))
                self.assertIn(f"p{part}-fill", pages, (number, part))
                if pattern.get("omit_rule"):
                    self.assertNotIn(f"p{part}-rule", pages, (number, part))
                else:
                    self.assertIn('class="batchim ending-rule"', pages[f"p{part}-rule"], (number, part))
                if pattern.get("omit_reorder"):
                    self.assertNotIn(f"p{part}-reorder", pages, (number, part))
                else:
                    self.assertIn(f"Reorder criterion: {pattern['reorder_criterion']}", source, (number, part))

    def test_reviewed_write_freetalk_and_transfer_copy_names_the_real_job(self):
        for number in REVIEWED_HTML:
            lesson = batch.LESSONS[number]
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            freetalk = pages["p3-freetalk"]
            tutor_question, _, _, _, learner_question, _ = lesson["live"]
            self.assertTrue(tutor_question.endswith("?"), number)
            self.assertTrue(learner_question.endswith("?"), number)
            self.assertNotIn("___", tutor_question, number)
            self.assertNotRegex(tutor_question.lower(), r"what would you (?:say|ask)|imagine|report it|explain")
            self.assertIn(batch.base.esc(tutor_question), freetalk, number)
            self.assertIn(batch.base.esc(learner_question), freetalk, number)
            for part in (1, 2):
                write = pages[f"p{part}-write"]
                self.assertIn(batch.base.esc(lesson[f"p{part}"]["write_script"]), write, (number, part))
                self.assertNotIn("to make your own sentence", write, (number, part))
            transfer = pages["transfer-scene"]
            self.assertIn("using the same two lines", transfer, number)
            self.assertIn("同じ二つの表現を使って", transfer, number)
            transfer_role_ja = lesson.get(
                "transfer_role_ja",
                batch.base.ROLE_JA.get(lesson["transfer_role"], "相手役"),
            )
            self.assertIn(batch.base.esc(transfer_role_ja), transfer, number)

            broken = copy.deepcopy(lesson)
            broken["live"] = ("Report it and ask for help.",) + broken["live"][1:]
            with self.assertRaisesRegex(ValueError, "real question"):
                batch.validate_lesson(number, broken)

    def test_sentence_answers_use_only_canonical_v1121_controls(self):
        for number, lesson in batch.LESSONS.items():
            path, source = batch.build(number, lesson)
            self.assertIn('<input class="space-input" type="text"', source, number)
            self.assertIn('<input class="slot-input"', source, number)
            self.assertNotRegex(source, r'<textarea class="(?:slot|space)-input', number)
            self.assertNotIn("growing-inputs.css", source, number)
            self.assertNotIn(".answer-fill .korean", source, number)
            self.assertFalse(path.with_name("growing-inputs.css").exists(), path)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                fill = pages[f"p{part}-fill"]
                self.assertIn('<input class="slot-input"', fill, (number, part))
                self.assertNotIn('<textarea class="free-input phrase-input"', fill, (number, part))
            for element in re.findall(r'<input class="(?:slot|space)-input"[^>]*>', source):
                self.assertIn("data-sync-id=", element, (number, element))
                self.assertIn("data-answer=", element, (number, element))

    def test_plural_scenes_name_the_travel_companion_before_we_our_or_us(self):
        lesson = batch.LESSONS[13]
        self.assertIn("旅行仲間と二人", lesson["situation"])
        self.assertIn("both", lesson["scene_turns"][0][1])
        self.assertIn("the two of you", lesson["transfer_turns"][0][1])

        lesson = batch.LESSONS[17]
        self.assertIn("旅行仲間", lesson["situation"])
        self.assertIn("both", lesson["scene_turns"][0][1])
        self.assertIn("both rented", lesson["transfer_turns"][0][1])

        lesson = batch.LESSONS[19]
        self.assertIn("旅行仲間と二人", lesson["situation"])
        self.assertIn("you two", lesson["scene_turns"][0][1])
        self.assertIn("the two of you", lesson["transfer_turns"][0][1])

    def test_ctx21_grounds_group_and_solo_counterpart_without_directive_japanese(self):
        lesson = batch.LESSONS[21]
        self.assertIn("旅行仲間と二人", lesson["situation"])
        self.assertIn("you and your friend", lesson["scene_turns"][0][1])
        self.assertIn("on your own", lesson["transfer_turns"][0][1])
        self.assertIn("I'd love to", lesson["scene_turns"][5][1])
        self.assertNotIn("we'd love", str(lesson["scene_turns"]).casefold())
        self.assertEqual(batch.core.strip_marks(lesson["p1"]["rows"][2][0]), "I'm thinking of getting coffee nearby.")
        self.assertEqual(batch.core.strip_marks(lesson["p2"]["rows"][1][0]), "You're welcome to come with me if you have time.")
        self.assertEqual(lesson["transfer_turns"][1], ("target", 1, 2))
        self.assertEqual(lesson["transfer_turns"][3], ("target", 2, 1))
        for _, japanese, _ in lesson["p2"]["rows"]:
            self.assertNotIn("ください", japanese)
            self.assertEqual(japanese.count("{t}"), 2)

    def test_ctx16_24_support_and_safety_copy_is_explicit(self):
        for number in range(16, 25):
            lesson = batch.LESSONS[number]
            self.assertTrue(lesson["role_ja"], number)
            self.assertTrue(lesson["transfer_role_ja"], number)
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                self.assertTrue(pattern["write_frame"], (number, part))
                self.assertTrue(pattern["write_script"], (number, part))
                self.assertTrue(pattern["write_script_ja"], (number, part))
                support_stage = pattern.get(
                    "translate_stage",
                    "supported" if pattern.get("translate_hints") else None,
                )
                if (number, part) == (17, 2):
                    self.assertEqual(support_stage, "checkpoint")
                    self.assertFalse(pattern.get("translate_hints"))
                else:
                    self.assertEqual(support_stage, "supported", (number, part))
                    self.assertEqual(len(pattern["translate_hints"]), 4, (number, part))

        self.assertIn("After checking with your travel companion", batch.LESSONS[17]["p1"]["write_script"])
        self.assertIn("imagined symptom", batch.LESSONS[18]["p1"]["write_script"])
        self.assertIn("imagined next step", batch.LESSONS[18]["p2"]["write_script"])
        self.assertIn("when you are alone", batch.LESSONS[21]["p1"]["write_script"])
        self.assertIn("leaving room to decline", batch.LESSONS[21]["p2"]["write_script"])

    def test_ctx14_freetalk_uses_two_real_related_questions(self):
        lesson = batch.LESSONS[14]
        self.assertEqual(lesson["live"][0], "Which feature makes your bag easiest to recognize?")
        self.assertEqual(lesson["live"][4], "What does your suitcase look like?")
        self.assertIn("先生", lesson["live"][5])

    def test_ctx23_transfer_uses_one_reason_for_stepping_away(self):
        lesson = batch.LESSONS[23]
        transfer = " ".join(turn[1] if turn[0] != "target" else batch.core.strip_marks(lesson[f"p{turn[1]}"]["rows"][turn[2]][0]) for turn in lesson["transfer_turns"])
        self.assertIn("needed a minute", transfer)
        self.assertIn("get some air", transfer)
        self.assertEqual(transfer.count("wanted to leave"), 2)
        self.assertNotIn("making you uncomfortable", transfer)

    def test_named_taught_expressions_are_actual_new_owners_here(self):
        expected = {18: "getting worse", 23: "I didn't realise"}
        current = {f"CTX-{number}" for number in batch.LESSONS}
        prior_owners: dict[str, set[str]] = {term.casefold(): set() for term in expected.values()}
        for path in (ROOT / "sandbox" / "drafts" / "en" / "tracks").rglob("lesson.html"):
            source = path.read_text(encoding="utf-8")
            match = REVIEW_ID.search(source)
            if not match or match.group(1) in current:
                continue
            data = vocabulary.parse(source, source=path)
            for entry in data["categories"]["new"]:
                key = entry["english"].casefold()
                if key in prior_owners:
                    prior_owners[key].add(match.group(1))
        self.assertEqual(prior_owners, {"getting worse": set(), "i didn't realise": set()})
        for number, term in expected.items():
            _, source = batch.build(number, batch.LESSONS[number])
            new_words = {entry["english"].casefold() for entry in vocabulary.parse(source, source=f"CTX-{number}")["categories"]["new"]}
            self.assertIn(term.casefold(), new_words, number)

    def test_reorders_use_three_or_four_honest_meaning_chunks(self):
        forbidden = {"a", "an", "the", "to", "for", "at", "in", "on", "?", ".", ","}
        for number, lesson in batch.LESSONS.items():
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                if pattern.get("omit_reorder"):
                    continue
                for _, _, chunk_source in pattern["rows"]:
                    chunks = chunk_source.split("|")
                    self.assertIn(len(chunks), (3, 4), (number, part, chunks))
                    self.assertFalse(forbidden.intersection(chunk.casefold().strip() for chunk in chunks), (number, part, chunks))
                    self.assertTrue(all(chunk.strip(" ?!.,") for chunk in chunks), (number, part, chunks))

    def test_bounded_frames_are_not_unpacked_by_reorder(self):
        for number, part in ((13, 2), (17, 1), (18, 1), (23, 1), (24, 2)):
            pattern = batch.LESSONS[number][f"p{part}"]
            self.assertTrue(pattern["omit_rule"], (number, part))
            self.assertTrue(pattern["omit_reorder"], (number, part))

    def test_replay_completion_and_transfer_are_resolved_scenes(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            scene_count = len(check_deck.TURN_OPEN.findall(pages["scene"]))
            self.assertEqual(len(check_deck.TURN_OPEN.findall(pages["p3-model"])), scene_count, number)
            self.assertEqual(len(check_deck.TURN_OPEN.findall(pages["p3-complete"])), scene_count, number)
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)
            self.assertIn(len(check_deck.TURN_OPEN.findall(pages["transfer-scene"])), (5, 6, 7), number)
            for part in (1, 2):
                self.assertIn(f"ctx-{number}-complete-p{part}", pages["p3-complete"], (number, part))
                self.assertIn(f"ctx-{number}-transfer-p{part}", pages["transfer-scene"], (number, part))

    def test_recycled_vocabulary_cites_the_actual_declared_owner(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            self.assertEqual(data["status"], "reviewed", number)
            self.assertLessEqual(len(data["categories"]["new"]), 8, number)
            for entry in data["categories"]["recycled"]:
                self.assertTrue(owner_is_reachable(entry["source"], number), (number, entry, entry_floor(number)))
                owner_path, owner_source = source_by_review_id(entry["source"])
                owner = vocabulary.parse(owner_source, source=owner_path)
                owner_words = {item["english"].casefold() for item in owner["categories"]["new"]}
                self.assertIn(entry["english"].casefold(), owner_words, (number, entry, owner_path))

    def test_every_new_owner_is_visible_in_learner_production_support(self):
        for number, lesson in batch.LESSONS.items():
            production = [english for english, _ in lesson["expressions"]]
            for part in (1, 2):
                production.extend(batch.core.strip_marks(row[0]) for row in lesson[f"p{part}"]["rows"])
            for turns in (lesson["scene_turns"], lesson["transfer_turns"]):
                production.extend(turn[1] for turn in turns if turn[0] == "me")
            tip = lesson["tip"]
            production.extend((tip[0], tip[2], tip[4][2], tip[5][2]))
            corpus = " ".join(production).casefold()
            _, source = batch.build(number, lesson)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            for entry in data["categories"]["new"]:
                self.assertIn(entry["english"].casefold(), corpus, (number, entry["english"]))

    def test_new_words_do_not_duplicate_a_reachable_existing_owner(self):
        existing: dict[tuple[str, str], set[str]] = {}
        current = {f"CTX-{number}" for number in batch.LESSONS}
        for path in (ROOT / "sandbox" / "drafts" / "en" / "tracks").rglob("lesson.html"):
            source = path.read_text(encoding="utf-8")
            match = REVIEW_ID.search(source)
            if not match or match.group(1) in current:
                continue
            data = vocabulary.parse(source, source=path)
            for entry in data["categories"]["new"]:
                key = (entry["english"].casefold(), entry["japanese"])
                existing.setdefault(key, set()).add(match.group(1))
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            for entry in data["categories"]["new"]:
                key = (entry["english"].casefold(), entry["japanese"])
                owners = existing.get(key, set())
                reachable = {owner for owner in owners if owner_is_reachable(owner, number)}
                self.assertEqual(reachable, set(), (number, entry, reachable, entry_floor(number)))
                existing.setdefault(key, set()).add(f"CTX-{number}")

    def test_ctx13_owns_delayed_below_its_core70_entry_floor(self):
        self.assertEqual(entry_floor(13), 70)
        _, source = batch.build(13, batch.LESSONS[13])
        data = vocabulary.parse(source, source="CTX-13")
        new_words = {entry["english"].casefold() for entry in data["categories"]["new"]}
        recycled = {entry["english"].casefold(): entry["source"] for entry in data["categories"]["recycled"]}
        self.assertIn("delayed", new_words)
        self.assertNotIn("delayed", recycled)
        self.assertEqual(recycled["miss"], "CORE-39")

    def test_medical_scene_stays_bounded_non_diagnostic_and_answer_safe(self):
        lesson = batch.LESSONS[18]
        scene = " ".join(turn[1] if turn[0] != "target" else "" for turn in lesson["scene_turns"])
        self.assertIn("Any trouble breathing?", scene)
        self.assertIn("seek emergency help immediately", scene)
        self.assertNotRegex(scene.casefold(), r"\b(diagnos|definitely|you have|prescribe)\b")
        self.assertIn(("me", "No, but the fever is getting worse.", "いいえ。ただ、熱が悪化しています。"), lesson["scene_turns"])
        self.assertIn("You should see a doctor today.", {row[0] for row in lesson["receptive"]})
        self.assertNotIn("The fever is getting worse.", {row[0] for row in lesson["receptive"]})

    def test_ctx20_targets_the_identification_frame_not_the_activity_vocabulary(self):
        for english, japanese, _ in batch.LESSONS[20]["p1"]["rows"]:
            self.assertEqual(re.findall(r"\{t\}(.*?)\{/t\}", english), ["Is this", "for"])
            self.assertEqual(re.findall(r"\{t\}(.*?)\{/t\}", japanese), ["これは", "の"])

    def test_ctx17_itemised_bill_and_ctx20_transfer_are_not_isolated_or_redundant(self):
        self.assertIn("itemised bill", batch.LESSONS[17]["scene_turns"][1][1])
        self.assertEqual(batch.LESSONS[20]["transfer_turns"][0][1], "Hi there. Can I help you?")

    def test_key_semantic_repairs_remain_in_source(self):
        self.assertEqual(batch.core.strip_marks(batch.LESSONS[23]["p1"]["rows"][0][0]), batch.AUTHORITATIVE[23][1])
        self.assertNotIn("in the wrong train", str(batch.LESSONS[15]["tip"]).casefold())
        self.assertIn("I took the wrong train", str(batch.LESSONS[15]["tip"]))
        self.assertIn("turned in|届けられた", batch.LESSONS[16]["vocab"][0])
        self.assertIn("popular with tourists|観光客に人気がある", batch.LESSONS[19]["vocab"][0])
        self.assertIn("I see your point|言い分は分かる", batch.LESSONS[22]["vocab"][0])

    def test_validation_rejects_bad_reorder_units(self):
        broken = copy.deepcopy(batch.LESSONS[15])
        row = list(broken["p2"]["rows"][0])
        row[2] = "How do I|get back|to|Central Station?"
        broken["p2"]["rows"] = (tuple(row),) + broken["p2"]["rows"][1:]
        with self.assertRaises(ValueError):
            batch.validate_lesson(15, broken)


if __name__ == "__main__":
    unittest.main()
