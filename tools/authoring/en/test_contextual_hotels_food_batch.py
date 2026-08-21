#!/usr/bin/env python3
"""Regression tests for the explicit CTX 7-12 hotels-and-food batch."""

from __future__ import annotations

import copy
import html
import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_contextual_hotels_food_batch as batch


class ContextualHotelsFoodBatchTests(unittest.TestCase):
    def test_transition_uses_an_aligned_pair_without_parsing_write_copy(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                purpose_en, purpose_ja = lesson[f"p{part}"]["meaning"]
                transition = html.unescape(pages[f"part{part}-intro"])
                self.assertIn(purpose_en.rstrip(". "), transition, (number, part))
                self.assertIn(purpose_ja.rstrip("。 "), transition, (number, part))
                self.assertIn("Read the line above aloud.", transition, (number, part))
                self.assertIn("上の文を声に出して読みましょう。", transition, (number, part))
                self.assertNotIn("practice this useful line", transition, (number, part))

        explicit = copy.deepcopy(batch.LESSONS[7]["p1"])
        explicit["write_script"] = "A deliberately unparsable learner-facing instruction"
        explicit["transition_purpose"] = (
            "State the booking name clearly",
            "予約名をはっきり伝えます",
        )
        transition = html.unescape(batch.transition(1, explicit))
        self.assertIn("State the booking name clearly. Read the line above aloud.", transition)
        self.assertIn("予約名をはっきり伝えます。 上の文を声に出して読みましょう。", transition)

    def test_batch_is_the_authorized_six_lesson_course(self):
        self.assertEqual(set(batch.LESSONS), set(range(7, 13)))
        self.assertEqual(set(batch.AUTHORITATIVE), set(batch.LESSONS))

    def test_authoritative_titles_and_models_are_preserved(self):
        for number, lesson in batch.LESSONS.items():
            batch.validate_lesson(number, lesson)

    def test_generated_html_is_exact_and_clean(self):
        for number, lesson in batch.LESSONS.items():
            path, expected = batch.build(number, lesson)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)

    def test_every_deck_keeps_the_contextual_production_arc(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(list(pages)[-1], "transfer-scene", number)
            self.assertNotIn("situation-card", pages, number)
            for required in ("lesson-goal", "scene", "understand", "p1-fill", "p1-translate", "p1-write", "p2-fill", "p2-translate", "p2-write", "p3-model", "p3-complete", "p3-freetalk", "transfer-scene"):
                self.assertIn(required, pages, (number, required))
            self.assertIn('class="sent-hero"', pages["p1-teach"], number)
            self.assertIn('class="sent-more"', pages["p1-teach"], number)
            self.assertIn('class="sent-hero"', pages["p2-teach"], number)
            self.assertIn('class="sent-more"', pages["p2-teach"], number)
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                rule_id = f"p{part}-rule"
                fill_id = f"p{part}-fill"
                if pattern.get("omit_rule"):
                    self.assertNotIn(rule_id, pages, number)
                else:
                    self.assertIn('class="batchim ending-rule"', pages[rule_id], number)
                if pattern.get("omit_fill"):
                    self.assertNotIn(fill_id, pages, number)
                else:
                    self.assertIn(fill_id, pages, number)
            self.assertIn('class="nuance-compare"', pages["native-tip"], number)
            self.assertEqual(check_deck.class_tag_count(pages["understand"], "choose-row", "receptive-choice"), 4, number)
            self.assertEqual(check_deck.meta_content(source, "podo:proofread-status"), "complete", number)

    def test_write_freetalk_and_transfer_copy_names_the_real_job(self):
        rejected_prompt = "You have a problem. What would you say?"
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            freetalk = pages["p3-freetalk"]
            tutor_question, _, _, _, learner_question, _ = lesson["live"]
            self.assertTrue(tutor_question.endswith("?"), number)
            self.assertTrue(learner_question.endswith("?"), number)
            self.assertNotIn("___", tutor_question, number)
            self.assertNotRegex(tutor_question.lower(), r"what would you (?:say|ask)|imagine|report it|explain")
            self.assertIn(batch.esc(tutor_question), freetalk, number)
            self.assertIn(batch.esc(learner_question), freetalk, number)
            for part in (1, 2):
                write = pages[f"p{part}-write"]
                self.assertIn(batch.esc(lesson[f"p{part}"]["write_script"]), write, (number, part))
                self.assertNotIn("to make your own sentence", write, (number, part))
            transfer = pages["transfer-scene"]
            self.assertIn("using the same two lines", transfer, number)
            self.assertIn("同じ二つの表現を使って", transfer, number)
            self.assertIn(batch.esc(batch.ROLE_JA[lesson["transfer_role"]]), transfer, number)

            broken = copy.deepcopy(lesson)
            broken["live"] = (rejected_prompt,) + broken["live"][1:]
            with self.assertRaisesRegex(ValueError, "conversation, not pattern production"):
                batch.validate_lesson(number, broken)

    def test_review_repairs_are_encoded_in_source_and_output(self):
        ctx7 = batch.LESSONS[7]
        self.assertIn("under + booking name", ctx7["p1"]["rule"][2])
        self.assertIn("backpacks", ctx7["transfer_turns"][4][1])
        self.assertIn("{t}の名前で{/t}", ctx7["p1"]["rows"][0][1])
        self.assertIn("{t}まで{/t}", ctx7["p2"]["rows"][0][1])
        self.assertIn("backpack|リュック", ctx7["vocab"][2])
        self.assertIn("stroller|ベビーカー", ctx7["vocab"][2])

        ctx8 = batch.LESSONS[8]
        self.assertIn("bedside lamp|ベッド脇のランプ", ctx8["vocab"][2])
        self.assertIn("fan|扇風機", ctx8["vocab"][2])

        ctx9 = batch.LESSONS[9]
        self.assertIn("real allergy", ctx9["p1"]["write"][0])
        self.assertIn("I don't eat", ctx9["p1"]["write_scaffold"])
        self.assertNotIn("dish", ctx9["p2"]["write"][0].lower())
        self.assertIn("cross-contact", ctx9["transfer_turns"][4][1])
        self.assertNotIn("safe for you", " ".join(turn[1] for turn in ctx9["transfer_turns"] if turn[0] != "target"))
        self.assertIn("I don't eat|食べません", ctx9["vocab"][2])
        self.assertNotIn("I don't eat|食べません", ctx9["vocab"][1])
        self.assertIn("cross-contact|交差接触", ctx9["vocab"][3])

        ctx10 = batch.LESSONS[10]
        self.assertEqual(ctx10["p1"]["rows"][0][2].split("|"), ["Sorry,", "I ordered", "the iced coffee,", "not the hot one."])
        self.assertTrue(ctx10["p1"]["omit_rule"])
        self.assertNotIn("omit_fill", ctx10["p1"])
        self.assertEqual(ctx10["p1"]["reorder_criterion"], "softener / order lead-in / correct item / not + received item")
        self.assertIn("{t}代わりに{/t}", ctx10["p2"]["rows"][0][1])
        _, ctx10_source = batch.build(10, ctx10)
        ctx10_pages = dict(check_deck.pages(ctx10_source))
        self.assertIn("p1-fill", ctx10_pages)
        self.assertNotIn("whole-turn-input", ctx10_source)
        self.assertEqual(ctx10_pages["p1-fill"].count("slot-input"), 8)
        self.assertIn('data-answer="I ordered"', ctx10_pages["p1-fill"])
        self.assertIn('data-answer="not"', ctx10_pages["p1-fill"])
        self.assertIn("the iced coffee", ctx10_pages["p1-fill"])
        self.assertIn("the hot one", ctx10_pages["p1-fill"])
        self.assertIn('data-answer="I ordered"', ctx10_pages["p3-complete"])
        self.assertIn('data-answer="not"', ctx10_pages["p3-complete"])
        self.assertIn("the iced coffee", ctx10_pages["p3-complete"])
        self.assertIn("the hot one", ctx10_pages["p3-complete"])

        ctx12 = batch.LESSONS[12]
        self.assertIn(("me", "Eight-fifteen works for us.", "8時15分で大丈夫です。"), ctx12["scene_turns"])
        self.assertIn("I've changed it to eight-fifteen", ctx12["scene_turns"][-1][1])
        self.assertEqual(ctx12["p2"]["write"][0], "How many people would you confirm?")
        self.assertIn("Is it + still + for four people?", ctx12["p2"]["rule"][4])

    def test_reorder_prepositions_stay_attached_to_their_complements(self):
        ctx11 = batch.LESSONS[11]
        for _, _, chunk_source in ctx11["p2"]["rows"]:
            chunks = chunk_source.split("|")
            self.assertNotIn("for", chunks)
            self.assertTrue(any(chunk.startswith("for ") for chunk in chunks))

        broken = copy.deepcopy(ctx11)
        first = list(broken["p2"]["rows"][0])
        first[2] = "Can I exchange|it|for|another one?"
        broken["p2"]["rows"] = (tuple(first),) + broken["p2"]["rows"][1:]
        with self.assertRaisesRegex(ValueError, "attach 'for' to its complement"):
            batch.validate_lesson(11, broken)

    def test_replay_and_completion_use_the_same_complete_scene(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            scene_turns = len(check_deck.TURN_OPEN.findall(pages["scene"]))
            model_turns = len(check_deck.TURN_OPEN.findall(pages["p3-model"]))
            complete_turns = len(check_deck.TURN_OPEN.findall(pages["p3-complete"]))
            self.assertEqual((scene_turns, model_turns, complete_turns), (scene_turns,) * 3, number)
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]),
                number,
            )


if __name__ == "__main__":
    unittest.main()
