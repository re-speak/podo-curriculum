#!/usr/bin/env python3
"""Narrow semantic, structural, and provenance gates for CTX49-60."""

from __future__ import annotations

import pathlib
import re
import sys
import unittest

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
            for pid in ("situation-card", "scene", "lesson-goal", "expressions", "understand",
                        "p1-teach", "p2-teach", "p3-model", "p3-complete", "p3-freetalk",
                        "native-tip", "transfer-scene"):
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

    def test_live_exchange_is_reciprocal_and_always_retrieves_both_frames(self):
        frames = {
            49: ("It's not so much", "I'd call it"), 50: ("We could", "If you can defer"),
            51: ("I'd rather not commit to", "It depends on whether"),
            52: ("The question is whether", "the less"), 53: ("To be fair", "That said"),
            54: ("We seem to agree on", "What if we agreed on"),
            55: ("I've noticed that", "I'd like to understand what's"),
            56: ("the issue is that", "What I'd like you to do is"),
            57: ("What we know is that", "We don't know"),
            58: ("the key benefit is", "it addresses the risk of"),
            59: ("We recognise the disruption", "I don't want to speculate"),
            60: ("Overall, I recommend", "What it comes down to is that"),
        }
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            live = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(len(check_deck.TURN_OPEN.findall(live)), 4, number)
            self.assertIn('data-sync-id="live-me"', live, number)
            self.assertIn('data-sync-id="live-ask"', live, number)
            self.assertIn('data-sync-id="live-tutor"', live, number)
            prompt, _, scaffold, _, ask, _ = lesson["live"]
            self.assertIn("real or imaginary", (prompt + " " + scaffold).casefold(), number)
            self.assertNotIn(" / ", scaffold, number)
            self.assertTrue(ask.endswith("?"), number)
            for frame in frames[number]:
                self.assertIn(frame, scaffold, (number, frame))

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

        english_cues = (["We recognise the disruption", "is causing"],
                        ["We recognise the pressure", "is creating"],
                        ["We recognise the delay", "is causing"],
                        ["We recognise the uncertainty", "is creating"])
        japanese_cues = (["この混乱を重く受け止めています", "引き起こしているものです"],
                         ["この負担を重く受け止めています", "生み出しているものです"],
                         ["この遅れを認識しています", "引き起こしているものです"],
                         ["この不安を認識しています", "生み出しているものです"])
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
        for text in (prompt, scaffold, ask):
            self.assertIn("incomplete", text.casefold())
        self.assertIn("qualified recommendation", prompt)
        self.assertIn("limited decision", ask)
        self.assertIn("不完全", prompt_ja + scaffold_ja + ask_ja)

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
