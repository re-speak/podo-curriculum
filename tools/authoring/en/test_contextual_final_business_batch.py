#!/usr/bin/env python3
"""Narrow semantic, structural, and provenance gates for CTX49-60."""

from __future__ import annotations

import pathlib
import re
import sys
import unittest
import html

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_contextual_final_business_batch as batch
import vocabulary


ROOT = pathlib.Path(__file__).resolve().parents[3]
ENGLISH = ROOT / "sandbox/drafts/en"
CORE = ENGLISH / "tracks/1-core-patterns"
CTX = ENGLISH / "tracks/2-contextual-english"
REVIEW_ID = re.compile(r'<meta name="podo:review-id" content="([^"]+)">')
TARGET = re.compile(r"\{t\}(.*?)\{/t\}")


def source_by_review_id(review_id: str) -> tuple[pathlib.Path, str]:
    matches = []
    track = CTX if review_id.startswith("CTX-") else CORE
    for path in track.rglob("lesson.html"):
        source = path.read_text(encoding="utf-8")
        match = REVIEW_ID.search(source)
        if match and match.group(1) == review_id:
            matches.append((path, source))
    if len(matches) != 1:
        raise AssertionError(f"{review_id}: expected one canonical deck, found {[p for p, _ in matches]}")
    return matches[0]


def entry_floor(number: int) -> int:
    source = (CTX / "toc" / f"CTX-{number}.md").read_text(encoding="utf-8")
    match = re.search(r"\*\*Entry floor:\*\* Core (\d+)", source)
    if not match:
        raise AssertionError(f"CTX-{number}: missing entry floor")
    return int(match.group(1))


def reachable(owner: str, number: int) -> bool:
    core = re.fullmatch(r"CORE-(\d+)", owner)
    if core:
        return int(core.group(1)) <= entry_floor(number)
    ctx = re.fullmatch(r"CTX-(\d+)", owner)
    return bool(ctx and int(ctx.group(1)) < number)


def declarations(review_id: str) -> dict:
    path, source = source_by_review_id(review_id)
    return vocabulary.parse(source, source=path)["categories"]


class ContextualFinalBusinessBatchTests(unittest.TestCase):
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
            (52, 1): ("The faster we move,", "the less time we'll have for"),
            (59, 1): ("We recognise the", "this is causing"),
        }
        for (number, part), targets in expected.items():
            self.assertEqual(
                {tuple(TARGET.findall(row[0])) for row in batch.LESSONS[number][f"p{part}"]["rows"]},
                {targets},
                (number, part),
            )

    def test_scope_models_and_source_validation(self):
        self.assertEqual(set(batch.LESSONS), set(range(49, 61)))
        for number, lesson in batch.LESSONS.items():
            batch.validate_lesson(number, lesson)
            brief = (CTX / "toc" / f"CTX-{number}.md").read_text(encoding="utf-8")
            self.assertIn(batch.core.strip_marks(lesson["p1"]["rows"][0][0]), brief, number)
            self.assertIn(batch.core.strip_marks(lesson["p2"]["rows"][0][0]), brief, number)

    def test_generated_bytes_checker_and_complete_status(self):
        for number, lesson in batch.LESSONS.items():
            path, expected = batch.build(number, lesson)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path)
            errors, warnings = check_deck.check(path)
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)
            self.assertEqual(expected.count('name="podo:proofread-status"'), 1, number)
            self.assertEqual(check_deck.meta_content(expected, "podo:proofread-status"), "complete", number)
            self.assertNotIn('name="podo:proofread-status" content="pending"', expected, number)

    def test_arc_teaching_and_six_turn_replays_are_complete(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertNotIn("situation-card", pages, number)
            self.assertEqual(list(pages)[:2], ["lesson-goal", "scene"], number)
            for pid in ("scene", "lesson-goal", "expressions", "understand",
                        "p1-teach", "p1-fill", "p1-translate", "p1-write",
                        "p2-teach", "p2-fill", "p2-translate", "p2-write",
                        "p3-model", "p3-complete", "p3-freetalk", "native-tip",
                        "transfer-scene"):
                self.assertIn(pid, pages, (number, pid))
            self.assertEqual(list(pages)[-1], "transfer-scene", number)
            for pid in ("p1-teach", "p2-teach"):
                self.assertIn('class="sent-hero"', pages[pid], (number, pid))
                self.assertIn('class="sent-more"', pages[pid], (number, pid))
            for pid in ("scene", "p3-model", "p3-complete", "transfer-scene"):
                self.assertEqual(len(check_deck.TURN_OPEN.findall(pages[pid])), 6, (number, pid))
            self.assertEqual(check_deck.partner_turns(pages["scene"]), check_deck.partner_turns(pages["p3-model"]), number)
            self.assertEqual(check_deck.partner_turns(pages["p3-model"]), check_deck.partner_turns(pages["p3-complete"]), number)

    def test_closed_work_targets_and_reorders_are_honest(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(check_deck.class_tag_count(pages["understand"], "choose-row", "receptive-choice"), 4, number)
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                for english, japanese, chunks in pattern["rows"]:
                    self.assertEqual(english.count("{t}"), japanese.count("{t}"), (number, part, english))
                    self.assertGreaterEqual(english.count("{t}"), 1, (number, part, english))
                    if not pattern.get("omit_reorder"):
                        self.assertIn(len(chunks.split("|")), (3, 4), (number, part, chunks))
                        self.assertEqual(batch.renderer.normalize_words(" ".join(chunks.split("|"))),
                                         batch.renderer.normalize_words(batch.core.strip_marks(english)),
                                         (number, part, english))
                if pattern.get("omit_reorder"):
                    self.assertNotIn(f"p{part}-reorder", pages, (number, part))
                else:
                    self.assertIn(f"p{part}-reorder", pages, (number, part))

    def test_bounded_chunks_do_not_receive_grammar_rules(self):
        bounded = {(50, 1), (52, 1), (54, 1), (55, 1), (55, 2), (56, 1),
                   (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2)}
        for number, part in bounded:
            self.assertTrue(batch.LESSONS[number][f"p{part}"]["omit_rule"], (number, part))
            self.assertTrue(batch.LESSONS[number][f"p{part}"]["omit_reorder"], (number, part))

    def test_live_exchange_is_real_reciprocal_free_talk(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            live = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(len(check_deck.TURN_OPEN.findall(live)), 4, number)
            self.assertIn('data-sync-id="p3-real-answer"', live, number)
            self.assertIn('data-sync-id="p3-tutor-answer"', live, number)
            prompt, _, scaffold, _, ask, _ = lesson["live"]
            self.assertTrue(prompt.endswith("?"), (number, prompt))
            self.assertTrue(ask.endswith("?"), number)
            self.assertTrue(ask.casefold().startswith("what about you"), (number, ask))
            self.assertNotRegex(prompt.casefold(), r"^(use|say|tell|report|reframe|make|give|name|imagine)\b")
            self.assertNotIn("___", prompt + scaffold + ask, number)
            self.assertIn(batch.core.esc(prompt), live, number)
            self.assertIn(batch.core.esc(ask), live, number)

    def test_write_jobs_translation_support_and_target_only_fills_are_explicit(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                self.assertTrue(pattern.get("write_frame"), (number, part))
                self.assertIn(pattern["write_frame"], pattern["write_script"], (number, part))
                self.assertIn("ましょう", pattern["write_script_ja"], (number, part))
                write = pages[f"p{part}-write"]
                self.assertIn(batch.core.esc(pattern["write_script"]), write, (number, part))
                fill = pages[f"p{part}-fill"]
                expected_targets = sum(row[0].count("{t}") for row in pattern["rows"])
                self.assertEqual(fill.count('class="slot-input"'), expected_targets, (number, part))
                translate = pages[f"p{part}-translate"]
                self.assertIn('data-scaffolding-contract="target-v2"', translate, (number, part))
                if pattern.get("translate_stage") == "checkpoint":
                    self.assertIn('data-support-stage="checkpoint"', translate, (number, part))
                    self.assertNotIn('class="hint-chip"', translate, (number, part))
                else:
                    self.assertTrue(pattern.get("translate_hints"), (number, part))
                    self.assertIn('data-support-stage="supported"', translate, (number, part))
                    self.assertIn('class="hint-chip"', translate, (number, part))

    def test_understand_uses_complete_counterpart_lines(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            understand = dict(check_deck.pages(source))["understand"]
            self.assertIn("I’ll read each line. Choose what it means.", understand, number)
            self.assertIn("私がそれぞれのセリフを読みます。意味を選んでください。", understand, number)
            counterpart = {
                turn[1] for turns in (lesson["scene_turns"], lesson["transfer_turns"])
                for turn in turns if turn[0] == "other"
            }
            for line, *_ in lesson["receptive"]:
                self.assertIn(line, counterpart, (number, line))
                self.assertRegex(line, r"[.?!]$", (number, line))

    def test_roles_and_transfer_intro_are_explicit_and_bilingual(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            scene = pages["scene"]
            transfer = pages["transfer-scene"]
            self.assertIn(batch.core.esc(lesson["role_ja"]), scene, number)
            self.assertIn(batch.core.esc(lesson["transfer_role_ja"]), transfer, number)
            self.assertIn("same two lines", transfer, number)
            self.assertIn("同じ二つの表現", transfer, number)

    def test_recycled_owners_are_exact_and_reachable(self):
        for number in range(49, 61):
            own = declarations(f"CTX-{number}")
            for item in own["recycled"]:
                self.assertTrue(reachable(item["source"], number), (number, item, entry_floor(number)))
                owner_new = {
                    (entry["english"].casefold(), entry["japanese"])
                    for entry in declarations(item["source"])["new"]
                }
                self.assertIn((item["english"].casefold(), item["japanese"]), owner_new, (number, item))

    def test_new_items_have_no_reachable_prior_owner(self):
        owners: dict[str, set[str]] = {}
        for track in (CORE, CTX):
            for path in track.rglob("lesson.html"):
                source = path.read_text(encoding="utf-8")
                match = REVIEW_ID.search(source)
                if not match:
                    continue
                review_id = match.group(1)
                for item in vocabulary.parse(source, source=path)["categories"]["new"]:
                    owners.setdefault(item["english"].casefold(), set()).add(review_id)
        for number in range(49, 61):
            for item in declarations(f"CTX-{number}")["new"]:
                found = {owner for owner in owners.get(item["english"].casefold(), set())
                         if owner != f"CTX-{number}" and reachable(owner, number)}
                self.assertEqual(found, set(), (number, item, found))

    def test_no_local_control_or_spacing_overrides(self):
        for number, lesson in batch.LESSONS.items():
            path, source = batch.build(number, lesson)
            self.assertFalse((path.parent / "growing-inputs.css").exists(), path)
            self.assertFalse((path.parent / "growing-inputs.js").exists(), path)
            self.assertNotIn("<style", source, path)
            self.assertNotIn("phrase-input {", source, path)

    def test_exact_target_cues_preserve_meaning_and_order(self):
        expected = {
            (49, 2): (["I'd call it", "rather than"], [["こう呼びます", "ではなく"]] * 4),
            (50, 1): (["We could", "provided"], [
                ["対応できます", "という条件なら"], ["維持できます", "という条件なら"],
                ["追加できます", "という条件なら"], ["開始できます", "という条件なら"],
            ]),
            (51, 1): (["I'd rather not commit to", "yet"], [["確約を控えたいです", "現時点では"]] * 4),
            (56, 2): (["What I'd like you to do is"], [["お願いしたいのは"]] * 4),
        }
        for (number, part), (english_targets, japanese_by_row) in expected.items():
            for index, (english, japanese, _) in enumerate(batch.LESSONS[number][f"p{part}"]["rows"]):
                self.assertEqual(TARGET.findall(english), english_targets, (number, part, english))
                self.assertEqual(TARGET.findall(japanese), japanese_by_row[index], (number, part, japanese))

        c57_printed = (
            ("that yet", "update everyone at four", "それはまだ", "4時に全員に更新情報を伝えます"),
            ("the cause yet", "update everyone at six", "原因はまだ", "6時に全員に更新情報を伝えます"),
            ("the full impact yet", "share another update at noon", "影響の全容はまだ", "正午に次の情報を共有します"),
            ("when service will resume yet", "update this page hourly", "サービスの再開時刻はまだ", "このページを1時間ごとに更新します"),
        )
        for (english, japanese, _), printed in zip(batch.LESSONS[57]["p2"]["rows"], c57_printed):
            self.assertEqual(TARGET.findall(english), ["We don't know", "but we'll"])
            self.assertEqual(TARGET.findall(japanese), ["分かりません", "ただし、必ず"])
            outside_en, outside_ja = TARGET.sub("", english), TARGET.sub("", japanese)
            for value in printed[:2]:
                self.assertIn(value, outside_en, (57, value, english))
            for value in printed[2:]:
                self.assertIn(value, outside_ja, (57, value, japanese))

        c59_printed = (
            ("provide another update within an hour", "1時間以内に次の情報をお伝えします"),
            ("confirm the cause by six", "6時までに原因を確認します"),
            ("share verified details at noon", "正午に確認済みの詳細を共有します"),
            ("update this page every hour", "このページを1時間ごとに更新します"),
        )
        for (english, japanese, _), (printed_en, printed_ja) in zip(batch.LESSONS[59]["p2"]["rows"], c59_printed):
            self.assertEqual(TARGET.findall(english), ["I don't want to speculate, but we'll"])
            self.assertEqual(TARGET.findall(japanese), ["推測でお伝えすることは避けますが、必ず"])
            self.assertIn(printed_en, TARGET.sub("", english), (59, english))
            self.assertIn(printed_ja, TARGET.sub("", japanese), (59, japanese))

        c56_actions = ("lead with the recommendation", "shorten the background section",
                       "quantify the expected impact", "state the decision on page one")
        for (english, japanese, _), action in zip(batch.LESSONS[56]["p2"]["rows"], c56_actions):
            self.assertEqual(TARGET.findall(english), ["What I'd like you to do is"])
            self.assertEqual(TARGET.findall(japanese), ["お願いしたいのは"])
            self.assertIn(action, TARGET.sub("", english), (56, english))
        _, c56_source = batch.build(56, batch.LESSONS[56])
        c56_pages = dict(check_deck.pages(c56_source))
        self.assertIn("What I&#x27;d like <br>you to do is", c56_pages["p2-teach"])
        self.assertIn('data-answer="What I&#x27;d like you to do is"', c56_pages["p2-fill"])

        english_cues = (["We recognise the", "this is causing"],) * 4
        japanese_cues = (["これにより生じている", "を認識しています"],) * 4
        for index, (english, japanese, _) in enumerate(batch.LESSONS[59]["p1"]["rows"]):
            self.assertEqual(TARGET.findall(english), english_cues[index], english)
            self.assertEqual(TARGET.findall(japanese), japanese_cues[index], japanese)

    def test_c51_reorder_uses_four_honest_units(self):
        expected_objects = ("that date", "a quantity", "that price", "a launch month")
        for row, object_phrase in zip(batch.LESSONS[51]["p1"]["rows"], expected_objects):
            english, _, chunks = row
            self.assertEqual(chunks.split("|"), ["I'd rather not", "commit to", object_phrase, "yet."])
            self.assertEqual(batch.renderer.normalize_words(" ".join(chunks.split("|"))),
                             batch.renderer.normalize_words(batch.core.strip_marks(english)))

    def test_c55_employee_perspective_is_elicited_before_the_cause(self):
        for turns, evidence in ((batch.LESSONS[55]["scene_turns"], "urgent requests"),
                                (batch.LESSONS[55]["transfer_turns"], "approval data")):
            self.assertEqual(turns[3], ("target", 2, turns[3][2]))
            self.assertNotIn(evidence, turns[2][1].casefold())
            self.assertIn("know", turns[2][1].casefold())
            self.assertIn(evidence, turns[4][1].casefold())
            self.assertIn("would help", turns[4][1].casefold())

    def test_c60_recommendation_is_qualified_by_incomplete_evidence(self):
        first_turn = batch.LESSONS[60]["scene_turns"][0]
        prompt, prompt_ja, scaffold, scaffold_ja, ask, ask_ja = batch.LESSONS[60]["live"]
        self.assertIn("forecast is still incomplete", first_turn[1])
        self.assertIn("需要予測はまだ不完全", first_turn[2])
        self.assertIn("evidence is incomplete", prompt.casefold())
        self.assertIn("reversible decision", prompt.casefold())
        self.assertIn("根拠が不完全", prompt_ja)
        self.assertTrue(ask.endswith("?"))

    def test_reviewed_semantic_and_bilingual_repairs_are_locked(self):
        self.assertIn("refused to commit and asked for more evidence", batch.LESSONS[49]["transfer_turns"][0][1])
        self.assertIn("deliberate pivot", batch.LESSONS[53]["tip"][0])
        self.assertIn("終わってすぐに", batch.LESSONS[53]["transfer_turns"][0][2])
        self.assertIn("締め切りに間に合わなかった", batch.LESSONS[55]["p1"]["rows"][0][1])
        self.assertIn("主張する結果", batch.LESSONS[58]["tip"][5][3])
        self.assertNotIn("誇う結果", batch.LESSONS[58]["tip"][5][3])
        self.assertIn("recommend|おすすめする|CTX-45", batch.LESSONS[60]["vocab"][1])


if __name__ == "__main__":
    unittest.main()
