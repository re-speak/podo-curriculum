#!/usr/bin/env python3
"""Regression tests for the isolated CTX 25-36 Contextual batch."""

from __future__ import annotations

import pathlib
import re
import sys
import unittest
import html

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_contextual_complex_workplace_batch as batch
import vocabulary


ROOT = pathlib.Path(__file__).resolve().parents[3]
REVIEW_ID = re.compile(r'<meta name="podo:review-id" content="([^"]+)">')
TARGET = re.compile(r"\{t\}(.*?)\{/t\}")


def source_by_review_id(review_id: str) -> tuple[pathlib.Path, str]:
    for path in (ROOT / "sandbox/drafts/en/tracks").rglob("lesson.html"):
        source = path.read_text(encoding="utf-8")
        match = REVIEW_ID.search(source)
        if match and match.group(1) == review_id:
            return path, source
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


class ContextualComplexWorkplaceBatchTests(unittest.TestCase):
    def test_transition_pages_are_specific_short_bilingual_actions(self):
        purposes = set()
        japanese_purposes = set()
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                purpose, purpose_ja = pattern.get("transition_purpose", pattern["meaning"])
                page = html.unescape(pages[f"part{part}-intro"])
                self.assertIn(purpose.rstrip(". ").casefold(), page.casefold(), (number, part))
                self.assertIn(purpose_ja.rstrip("。 "), page, (number, part))
                self.assertIn("Read the line above aloud.", page, (number, part))
                self.assertIn("上の文を声に出して読みましょう。", page, (number, part))
                self.assertNotIn("practice this useful line", page, (number, part))
                self.assertLessEqual(len(purpose), 150, (number, part))
                self.assertLessEqual(len(purpose_ja), 70, (number, part))
                purposes.add(purpose)
                japanese_purposes.add(purpose_ja)
        self.assertEqual(len(purposes), 24)
        self.assertEqual(len(japanese_purposes), 24)

    def test_repaired_completion_targets_are_invariant_frames(self):
        expected = {
            (26, 2): ("may have been", "but I can't be certain"),
            (27, 2): ("What", "can you offer me"),
            (28, 1): ("My", "says", "whereas your system says"),
            (30, 2): ("I'd only",),
        }
        for (number, part), targets in expected.items():
            self.assertEqual(
                {tuple(TARGET.findall(row[0])) for row in batch.LESSONS[number][f"p{part}"]["rows"]},
                {targets},
                (number, part),
            )

    def test_scope_and_authoritative_models(self):
        self.assertEqual(set(batch.LESSONS), set(range(25, 37)))
        self.assertEqual(set(batch.AUTHORITATIVE), set(batch.LESSONS))
        for number, lesson in batch.LESSONS.items():
            batch.validate_lesson(number, lesson)

    def test_generated_html_is_exact_and_checker_clean(self):
        for number, lesson in batch.LESSONS.items():
            path, expected = batch.build(number, lesson)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)

    def test_status_is_exactly_one_complete_marker(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            self.assertEqual(source.count('name="podo:proofread-status"'), 1, number)
            self.assertEqual(check_deck.meta_content(source, "podo:proofread-status"), "complete", number)
            self.assertNotIn('podo:proofread-status" content="pending"', source, number)

    def test_contextual_arc_and_six_turn_replays_are_intact(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(list(pages)[-1], "transfer-scene", number)
            self.assertEqual(list(pages)[0], "lesson-goal", number)
            self.assertNotIn("situation-card", pages, number)
            for required in ("scene", "lesson-goal", "expressions", "understand",
                             "p1-teach", "p2-teach", "p3-model", "p3-complete", "p3-freetalk",
                             "native-tip", "transfer-scene"):
                self.assertIn(required, pages, (number, required))
            self.assertIn('class="sent-hero"', pages["p1-teach"], number)
            self.assertIn('class="sent-more"', pages["p1-teach"], number)
            self.assertIn('class="sent-hero"', pages["p2-teach"], number)
            self.assertIn('class="sent-more"', pages["p2-teach"], number)
            counts = [len(check_deck.TURN_OPEN.findall(pages[pid])) for pid in
                      ("scene", "p3-model", "p3-complete", "transfer-scene")]
            self.assertEqual(counts, [6, 6, 6, 6], number)
            self.assertEqual(check_deck.partner_turns(pages["scene"]), check_deck.partner_turns(pages["p3-model"]), number)
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)
            scene_targets = [turn for turn in lesson["scene_turns"] if turn[0] == "target"]
            transfer_targets = [turn for turn in lesson["transfer_turns"] if turn[0] == "target"]
            expected_scene_fields = sum(lesson[f"p{part}"]["rows"][row][0].count("{t}") for _, part, row in scene_targets)
            expected_transfer_fields = sum(lesson[f"p{part}"]["rows"][row][0].count("{t}") for _, part, row in transfer_targets)
            self.assertEqual(pages["p3-complete"].count("phrase-input"), expected_scene_fields, number)
            self.assertEqual(pages["transfer-scene"].count("phrase-input"), expected_transfer_fields, number)

    def test_closed_work_has_four_rows_and_honest_reorder_units(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(check_deck.class_tag_count(pages["understand"], "choose-row", "receptive-choice"), 4, number)
            for part in (1, 2):
                for activity in ("read", "fill", "translate"):
                    page = pages[f"p{part}-{activity}"]
                    expected_class = "model-line" if activity == "read" else "task-block"
                    self.assertEqual(check_deck.class_tag_count(page, expected_class), 4, (number, part, activity))
                pattern = lesson[f"p{part}"]
                reorder_id = f"p{part}-reorder"
                if pattern.get("omit_reorder"):
                    self.assertNotIn(reorder_id, pages, number)
                else:
                    self.assertIn(reorder_id, pages, number)
                    counts = {len(row[2].split("|")) for row in pattern["rows"]}
                    self.assertTrue(counts.issubset({3, 4}), number)
                    for english, _, chunks in pattern["rows"]:
                        self.assertEqual(batch.normalize_words(" ".join(chunks.split("|"))),
                                         batch.normalize_words(batch.core.strip_marks(english)), number)

    def test_all_productive_fields_wrap_and_sync_statically(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                fill = pages[f"p{part}-fill"]
                translate = pages[f"p{part}-translate"]
                self.assertEqual(fill.count('class="slot-input"'),
                                 sum(row[0].count("{t}") for row in lesson[f"p{part}"]["rows"]), (number, part))
                self.assertNotIn("<br><br>", fill, (number, part))
                self.assertEqual(translate.count('<input class="space-input"'), 4, (number, part))
                self.assertIn('data-scaffolding-contract="target-v2"', translate, (number, part))
                stage = lesson[f"p{part}"].get("translate_stage", "supported")
                self.assertIn(f'data-support-stage="{stage}"', translate, (number, part))
                if stage == "supported":
                    self.assertIn('class="hint-chip"', translate, (number, part))
                else:
                    self.assertNotIn('class="hint-chip"', translate, (number, part))
            for pid in ("p3-complete", "transfer-scene"):
                self.assertNotIn('class="slot-input"', pages[pid], (number, pid))
                self.assertIn('class="free-input phrase-input"', pages[pid], (number, pid))

    def test_live_exchange_is_reciprocal_conversation_not_pattern_production(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            live = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(len(check_deck.TURN_OPEN.findall(live)), 4, number)
            self.assertRegex(live, r"Tutor(?:'|&#x27;)s answer", number)
            self.assertIn('data-sync-id="p3-real-answer"', live, number)
            self.assertIn('data-sync-id="p3-tutor-answer"', live, number)
            prompt_en, prompt_ja, _, _, ask_en, ask_ja = lesson["live"]
            for question in (prompt_en, prompt_ja, ask_en, ask_ja):
                self.assertTrue(question.endswith(("?", "？")), (number, question))
                self.assertIn(batch.esc(question), live, (number, question))
            self.assertNotRegex(
                prompt_en.casefold(),
                r"\b(?:what would you say|report it|explain it|imagine|use today(?:'s|&apos;s) pattern)\b",
                number,
            )
            self.assertNotIn("___", prompt_en + ask_en, number)
            self.assertNotIn("live_sequence", lesson, number)

    def test_provenance_and_batch_specific_repairs_are_locked(self):
        required = {
            25: ("CORE-59",), 26: ("CTX-11", "CORE-65"), 27: ("CTX-21",),
            28: ("CORE-19",), 29: ("CORE-71",), 30: ("CORE-59",),
            32: ("CORE-24", "CORE-28"), 33: ("CORE-28", "CORE-10"),
            35: ("CTX-3", "CTX-32"), 36: ("CORE-2",),
        }
        for number, owners in required.items():
            recycled = batch.LESSONS[number]["vocab"][1]
            for owner in owners:
                self.assertIn(owner, recycled, (number, owner))
        for number, lesson in batch.LESSONS.items():
            metadata = "; ".join(lesson["vocab"])
            citations = {
                item for field in lesson["vocab"] for item in field.split("; ")
                if re.search(r"\|CTX-(?:1[3-9]|2[0-4])$", item)
            }
            self.assertTrue(citations.issubset(batch.VISIBLE_PRIOR_CTX_OWNERS), number)
        self.assertTrue(batch.LESSONS[27]["p1"]["omit_rule"])
        self.assertTrue(batch.LESSONS[29]["p2"]["omit_rule"])
        self.assertTrue(batch.LESSONS[33]["p1"]["omit_rule"])
        self.assertTrue(batch.LESSONS[31]["p1"]["omit_reorder"])
        self.assertTrue(batch.LESSONS[32]["p2"]["omit_reorder"])
        for (number, part), owners in batch.CHUNK_OWNERS.items():
            self.assertTrue(batch.LESSONS[number][f"p{part}"]["omit_rule"], (number, part))
            self.assertTrue(batch.LESSONS[number][f"p{part}"]["omit_reorder"], (number, part))
            for owner in owners:
                self.assertRegex(owner, r"^CORE-\d+$")
        self.assertNotIn("CORE-117", batch.LESSONS[29]["vocab"][1])
        self.assertNotIn("CORE-81", batch.LESSONS[31]["vocab"][1])
        self.assertNotIn("CORE-60", batch.LESSONS[33]["vocab"][1])
        self.assertEqual(batch.LESSONS[28]["transfer_turns"][0][1], "Our system shows a daily parking charge.")
        self.assertIn("morning ferry", batch.core.strip_marks(batch.LESSONS[30]["p1"]["rows"][2][0]))
        self.assertEqual(batch.LESSONS[32]["scene_turns"][2][1], "Of course. I said the final deadline has changed.")
        self.assertEqual(batch.LESSONS[32]["transfer_turns"][0][1], "About the replacement budget—")
        self.assertNotIn("tracking number", batch.LESSONS[32]["vocab"][3])
        self.assertIn("in charge of", batch.LESSONS[31]["tip"][2])
        self.assertIn("meet you there|そこで会う|CTX-21", batch.LESSONS[27]["vocab"][1])

    def test_reviewed_vocabulary_owners_and_bounded_new_items_are_exact(self):
        _, ctx32_source = batch.build(32, batch.LESSONS[32])
        self.assertRegex(ctx32_source, r'name="podo:vocabulary:new" content="[^"]*deadline\|締め切り')
        self.assertIn("deadline|締め切り|CTX-32", batch.LESSONS[35]["vocab"][1])
        self.assertNotIn("deadline|締め切り|CORE-82", batch.LESSONS[35]["vocab"][1])
        self.assertNotIn("deadline|締め切り", batch.LESSONS[35]["vocab"][0])
        self.assertIn("confirm|確認する|CTX-3", batch.LESSONS[35]["vocab"][1])
        for item in ("essential|必須の", "optional|任意の", "alternative|代案"):
            self.assertIn(item, batch.LESSONS[27]["vocab"][0])
        for item in ("postpone|延期する", "turn back|引き返す", "take the risk|危険を冒す"):
            self.assertIn(item, batch.LESSONS[29]["vocab"][0])
        self.assertIn("replace|差し替える", batch.LESSONS[34]["vocab"][0])
        self.assertNotIn("could you also|追加でしていただけますか|CORE-20", batch.LESSONS[34]["vocab"][1])
        self.assertIn("direct|直行の", batch.LESSONS[25]["vocab"][0])
        self.assertIn("robbed|強盗に遭った", batch.LESSONS[26]["vocab"][0])
        self.assertIn("stolen|盗まれた|CORE-65", batch.LESSONS[26]["vocab"][1])
        self.assertIn("midnight|深夜0時|CORE-10", batch.LESSONS[33]["vocab"][1])
        self.assertNotIn("midnight|深夜0時", batch.LESSONS[33]["vocab"][0])

    def test_every_recycled_item_has_its_actual_reachable_declared_owner(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            self.assertEqual(data["status"], "reviewed", number)
            self.assertLessEqual(len(data["categories"]["new"]), 8, number)
            for entry in data["categories"]["recycled"]:
                self.assertTrue(
                    owner_is_reachable(entry["source"], number),
                    (number, entry, entry_floor(number)),
                )
                owner_path, owner_source = source_by_review_id(entry["source"])
                owner = vocabulary.parse(owner_source, source=owner_path)
                owner_words = {item["english"].casefold() for item in owner["categories"]["new"]}
                self.assertIn(entry["english"].casefold(), owner_words, (number, entry, owner_path))

    def test_semantic_repairs_and_grounded_askbacks_are_locked(self):
        self.assertIn("ferry route", batch.LESSONS[30]["transfer_turns"][2][1])
        self.assertNotIn("flight", batch.LESSONS[30]["transfer_turns"][2][1])
        self.assertNotIn("remit", batch.LESSONS[31]["goal"][0])
        self.assertNotIn("remit", batch.LESSONS[31]["p1"]["rule"][5])
        for number in batch.LESSONS:
            ask_en, ask_ja = batch.LESSONS[number]["live"][4:6]
            self.assertTrue(ask_en.startswith("What about you"), number)
            self.assertTrue(ask_ja.endswith("？"), number)
        tip = batch.LESSONS[25]["tip"]
        self.assertIn("途中で着陸しない", tip[4][3])
        self.assertIn("同じ便名", tip[5][3])
        self.assertNotEqual(tip[4][3], tip[5][3])
        _, c36_source = batch.build(36, batch.LESSONS[36])
        self.assertEqual(batch.LESSONS[36]["transfer_role"], "IT support specialist")
        self.assertIn("I'll be the it support specialist.", html.unescape(c36_source))
        self.assertNotIn("I'll be the it support.", html.unescape(c36_source))

    def test_japanese_cues_map_one_to_one_to_the_english_blanks(self):
        def cues(number, part):
            return [tuple(re.findall(r"\{t\}(.*?)\{/t\}", row[1]))
                    for row in batch.LESSONS[number][f"p{part}"]["rows"]]

        for row_cues in cues(28, 1):
            self.assertEqual(row_cues[:2], ("私の", "の記載は"))
            self.assertEqual(row_cues[2], "ですが、そちらのシステムの記載は")
            self.assertTrue(row_cues[2].startswith("ですが、"))
            self.assertFalse(any(detail in "".join(row_cues) for detail in
                                 ("確認書", "メール", "バウチャー", "朝食", "駐車", "2泊", "ダブル")))
        self.assertEqual(set(cues(29, 1)), {("という事実だけでは", "必ずしもなりません")})
        self.assertNotIn("必ずしも", cues(29, 1)[0][0])
        self.assertNotIn("安全", cues(29, 1)[0][1])
        self.assertEqual(set(cues(29, 2)), {("総合的に考えると、私が望むのは", "危険を冒すことではありません")})
        self.assertIn("望む", cues(29, 2)[0][0])
        self.assertEqual(set(cues(32, 1)), {("のあとで音声が途切れました",)})
        self.assertFalse(any(any(word in cue for word in ("Friday", "budget", "send it", "client"))
                             for row in cues(32, 1) for cue in row))
        self.assertEqual(set(cues(33, 1)), {("それなら", "私にとっては")})
        self.assertIn("なら", cues(33, 1)[0][0])
        self.assertEqual(set(cues(36, 2)), {("動きました", "が、今表示されるのは")})

        _, source = batch.build(36, batch.LESSONS[36])
        pages = dict(check_deck.pages(source))
        self.assertEqual([row[0].count("{t}") for row in batch.LESSONS[36]["p2"]["rows"]], [2] * 4)
        self.assertEqual([row[1].count("{t}") for row in batch.LESSONS[36]["p2"]["rows"]], [2] * 4)
        self.assertEqual(pages["p2-fill"].count('class="target ending"'), 8)
        self.assertEqual(pages["p3-complete"].count('class="target"'), 3)
        self.assertEqual(pages["transfer-scene"].count('class="target"'), 3)

    def test_source_side_spacing_and_title_fits_are_rendered_without_local_css(self):
        for number, lesson in batch.LESSONS.items():
            path, source = batch.build(number, lesson)
            self.assertNotIn('<link rel="stylesheet" href="growing-inputs.css">', source, number)
            self.assertNotIn("<style", source, number)
            self.assertFalse(path.with_name("growing-inputs.css").exists(), number)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                self.assertEqual(
                    pages[f"p{part}-fill"].count('class="slot-input"'),
                    sum(row[0].count("{t}") for row in lesson[f"p{part}"]["rows"]),
                    (number, part),
                )
                self.assertNotIn('class="free-input phrase-input"', pages[f"p{part}-fill"], (number, part))
        self.assertEqual(batch.LESSONS[32]["goal_title"], "Repair a bad connection on a call")
        self.assertLessEqual(len(batch.LESSONS[26]["transfer_ja"]), 16)
        self.assertLessEqual(len(batch.LESSONS[30]["transfer_ja"]), 16)

    def test_write_jobs_roles_and_transfer_intros_are_explicit_and_aligned(self):
        generic = re.compile(r"to make your own sentence", re.IGNORECASE)
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            learner_role = batch.course_for(number)[3].lower()
            self.assertIn(f"You're the {learner_role}", pages["scene"], number)
            self.assertIn(batch.esc(lesson["role_ja"]), pages["scene"], number)
            self.assertIn(batch.esc(lesson["transfer_role_ja"]), pages["transfer-scene"], number)
            self.assertIn("same two lines", pages["transfer-scene"], number)
            self.assertIn("同じ二つの表現", pages["transfer-scene"], number)
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                write = pages[f"p{part}-write"]
                self.assertIn(batch.esc(pattern["write_script"]), write, (number, part))
                self.assertIn(batch.esc(pattern["write_script_ja"]), write, (number, part))
                self.assertNotRegex(pattern["write_script"], generic, (number, part))

    def test_supported_hints_are_lexical_and_checkpoint_pages_have_none(self):
        for number, lesson in batch.LESSONS.items():
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                stage = pattern.get("translate_stage", "supported")
                hints = pattern.get("translate_hints")
                if stage == "checkpoint":
                    self.assertFalse(hints, (number, part))
                    continue
                self.assertEqual(len(hints), 4, (number, part))
                for row, row_hints in zip(pattern["rows"], hints):
                    if len(row_hints) == 2 and all(isinstance(item, str) for item in row_hints):
                        row_hints = (row_hints,)
                    self.assertTrue(row_hints, (number, part))
                    sentence = batch.core.strip_marks(row[0]).casefold()
                    target_chunks = [
                        chunk.casefold()
                        for chunk in re.findall(r"\{t\}(.*?)\{/t\}", row[0])
                    ]
                    for japanese, english in row_hints:
                        self.assertTrue(japanese.strip() and english.strip(), (number, part))
                        self.assertNotIn("___", japanese + english, (number, part))
                        self.assertIn(english.casefold(), sentence, (number, part, english))
                        self.assertNotIn(english.casefold(), target_chunks, (number, part, english))


if __name__ == "__main__":
    unittest.main()
