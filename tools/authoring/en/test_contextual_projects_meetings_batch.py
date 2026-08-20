#!/usr/bin/env python3
"""Regression tests for the isolated CTX 37-48 business batch."""

from __future__ import annotations

import copy
import pathlib
import re
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_contextual_projects_meetings_batch as batch
import vocabulary


ROOT = pathlib.Path(__file__).resolve().parents[3]
REVIEW_ID = re.compile(r'<meta name="podo:review-id" content="([^"]+)">')


def source_by_review_id(review_id: str) -> tuple[pathlib.Path, str]:
    for path in (ROOT / "sandbox/drafts/en/tracks").rglob("lesson.html"):
        source = path.read_text(encoding="utf-8")
        match = REVIEW_ID.search(source)
        if match and match.group(1) == review_id:
            return path, source
    raise AssertionError(f"no deck with review id {review_id}")


def owner_is_reachable(owner: str, number: int) -> bool:
    core_owner = re.fullmatch(r"CORE-(\d+)", owner)
    if core_owner:
        return int(core_owner.group(1)) <= batch.ENTRY_FLOORS[number]
    contextual_owner = re.fullmatch(r"CTX-(\d+)", owner)
    return bool(contextual_owner and int(contextual_owner.group(1)) < number)


class ContextualProjectsMeetingsBatchTests(unittest.TestCase):
    def test_scope_models_and_source_validation(self):
        self.assertEqual(set(batch.LESSONS), set(range(37, 49)))
        self.assertEqual(set(batch.AUTHORITATIVE), set(batch.LESSONS))
        self.assertEqual(set(batch.PATTERN_CORE_OWNERS), set(batch.LESSONS))
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

    def test_contextual_arc_and_complete_six_turn_replays(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(list(pages)[-1], "transfer-scene", number)
            self.assertGreaterEqual(len(pages), 23, number)
            for required in (
                "situation-card", "scene", "lesson-goal", "expressions", "understand",
                "p1-teach", "p2-teach", "p3-model", "p3-complete", "p3-freetalk",
                "native-tip", "transfer-scene",
            ):
                self.assertIn(required, pages, (number, required))
            counts = [
                len(check_deck.TURN_OPEN.findall(pages[page_id]))
                for page_id in ("scene", "p3-model", "p3-complete", "transfer-scene")
            ]
            self.assertEqual(counts, [6, 6, 6, 6], number)
            self.assertEqual(
                check_deck.partner_turns(pages["scene"]),
                check_deck.partner_turns(pages["p3-model"]),
                number,
            )
            self.assertEqual(
                check_deck.partner_turns(pages["p3-model"]),
                check_deck.partner_turns(pages["p3-complete"]),
                number,
            )

    def test_closed_work_has_four_rows_and_reorders_use_honest_units(self):
        forbidden = {"a", "an", "the", "to", "for", "at", "in", "on", "?", ".", ","}
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            pages = dict(check_deck.pages(source))
            self.assertEqual(
                check_deck.class_tag_count(pages["understand"], "choose-row", "receptive-choice"),
                4,
                number,
            )
            for part in (1, 2):
                pattern = lesson[f"p{part}"]
                for activity in ("read", "fill", "translate"):
                    page = pages[f"p{part}-{activity}"]
                    expected_class = "model-line" if activity == "read" else "task-block"
                    self.assertEqual(check_deck.class_tag_count(page, expected_class), 4, (number, part, activity))
                reorder_id = f"p{part}-reorder"
                if pattern.get("omit_reorder"):
                    self.assertNotIn(reorder_id, pages, (number, part))
                    continue
                self.assertIn(reorder_id, pages, (number, part))
                for english, _, chunk_source in pattern["rows"]:
                    chunks = chunk_source.split("|")
                    expected = 3 if (number, part) in batch.HONEST_THREE_CHUNK_PARTS else 4
                    self.assertEqual(len(chunks), expected, (number, part, chunks))
                    self.assertFalse(forbidden.intersection(chunk.casefold().strip() for chunk in chunks))
                    self.assertEqual(
                        batch.renderer.normalize_words(" ".join(chunks)),
                        batch.renderer.normalize_words(batch.core.strip_marks(english)),
                        (number, part, chunks),
                    )

    def test_productive_controls_are_static_canonical_and_wrap(self):
        for number, lesson in batch.LESSONS.items():
            path, source = batch.build(number, lesson)
            self.assertNotIn("<style", source, number)
            self.assertNotRegex(source, r"\sstyle=")
            self.assertNotIn("growing-inputs.css", source, number)
            self.assertFalse(path.with_name("growing-inputs.css").exists(), path)
            self.assertIn('data-page-id="lesson-goal" data-act="Business task"', source, number)
            self.assertNotIn('data-page-id="lesson-goal" data-act="Travel task"', source, number)
            pages = dict(check_deck.pages(source))
            for part in (1, 2):
                fill = pages[f"p{part}-fill"]
                translate = pages[f"p{part}-translate"]
                self.assertEqual(
                    fill.count('class="free-input phrase-input"'),
                    sum(row[0].count("{t}") for row in lesson[f"p{part}"]["rows"]),
                    (number, part),
                )
                self.assertNotIn('class="slot-input', fill, (number, part))
                self.assertEqual(translate.count('<textarea class="free-input"'), 4, (number, part))
            for page_id in ("p3-complete", "transfer-scene"):
                self.assertIn('class="free-input phrase-input"', pages[page_id], (number, page_id))
                self.assertNotIn('class="slot-input', pages[page_id], (number, page_id))

    def test_live_exchange_is_reciprocal_truthful_and_frame_safe(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            live_page = dict(check_deck.pages(source))["p3-freetalk"]
            self.assertEqual(len(check_deck.TURN_OPEN.findall(live_page)), 4, number)
            self.assertIn('data-sync-id="live-me"', live_page, number)
            self.assertIn('data-sync-id="live-ask"', live_page, number)
            self.assertIn('data-sync-id="live-tutor"', live_page, number)
            prompt, _, scaffold, _, _, _ = lesson["live"]
            self.assertIn("real or imaginary", (prompt + " " + scaffold).casefold(), number)
            self.assertNotIn(" / ", scaffold, number)
            for frame in batch.LIVE_FRAME_CONTRACTS[number]:
                self.assertEqual(scaffold.count(frame), 1, (number, frame, scaffold))
        self.assertNotIn("___ing", batch.LESSONS[38]["live"][2])
        self.assertIn("who's contacting ___", batch.LESSONS[38]["live"][2])
        self.assertIn("I'm happy to contact them", batch.LESSONS[38]["live"][2])

    def test_brief_entry_floors_and_bounded_parts_are_locked(self):
        for number in batch.LESSONS:
            brief = ROOT / "sandbox/drafts/en/tracks/2-contextual-english/toc" / f"CTX-{number}.md"
            source = brief.read_text(encoding="utf-8")
            floor = re.search(r"\*\*Entry floor:\*\* Core (\d+)", source)
            self.assertIsNotNone(floor, number)
            self.assertEqual(int(floor.group(1)), batch.ENTRY_FLOORS[number], number)
            sections = re.split(r"### Pattern [12]\n", source)[1:]
            self.assertEqual(len(sections), 2, number)
            for part, section in enumerate(sections, start=1):
                owner_line = next(
                    (line for line in section.splitlines() if line.startswith("- **Core ownership:**")),
                    "",
                )
                owners = tuple(int(owner) for owner in re.findall(r"Core (\d+)", owner_line))
                self.assertEqual(owners, batch.PATTERN_CORE_OWNERS[number][part - 1], (number, part))
                bounded = "teach as a bounded chunk" in section
                self.assertEqual(bounded, (number, part) in batch.BOUNDED_PARTS, (number, part))
                if bounded:
                    pattern = batch.LESSONS[number][f"p{part}"]
                    self.assertTrue(pattern.get("omit_rule"), (number, part))
                    self.assertTrue(pattern.get("omit_reorder"), (number, part))

        broken = copy.deepcopy(batch.LESSONS[38])
        broken["p1"]["omit_rule"] = False
        with self.assertRaisesRegex(ValueError, "bounded chunk"):
            batch.validate_lesson(38, broken)

        broken = copy.deepcopy(batch.LESSONS[42])
        old_three_chunks = (
            "So I'll update the schedule,|and Mia|will contact the client.",
            "So I'll revise the budget,|and Ken|will check the figures.",
            "So I'll write the notes,|and Jo|will send the files.",
            "So I'll call the supplier,|and Lee|will update the team.",
        )
        broken["p1"]["rows"] = tuple(
            (*row[:2], chunks) for row, chunks in zip(broken["p1"]["rows"], old_three_chunks)
        )
        with self.assertRaisesRegex(ValueError, "expected 4 honest reorder chunks"):
            batch.validate_lesson(42, broken)

    def test_every_recycled_item_has_its_actual_reachable_declared_owner(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            self.assertEqual(data["status"], "reviewed", number)
            self.assertLessEqual(len(data["categories"]["new"]), 8, number)
            for entry in data["categories"]["recycled"]:
                self.assertTrue(owner_is_reachable(entry["source"], number), (number, entry))
                owner_path, owner_source = source_by_review_id(entry["source"])
                owner = vocabulary.parse(owner_source, source=owner_path)
                owner_rows = {
                    (item["english"].casefold(), item["japanese"])
                    for item in owner["categories"]["new"]
                }
                self.assertIn(
                    (entry["english"].casefold(), entry["japanese"]),
                    owner_rows,
                    (number, entry, owner_path),
                )

    def test_every_productive_vocabulary_item_is_visible_in_the_deck(self):
        for number, lesson in batch.LESSONS.items():
            _, source = batch.build(number, lesson)
            body = batch.visible_text(source)
            data = vocabulary.parse(source, source=f"CTX-{number}")
            for category in ("new", "recycled"):
                for entry in data["categories"][category]:
                    english = entry["english"].casefold()
                    forms = (english,) + batch.VISIBLE_VOCABULARY_FORMS.get((number, english), ())
                    self.assertTrue(
                        any(batch.phrase_is_visible(body, form) for form in forms),
                        (number, category, entry),
                    )

    def test_vocabulary_visibility_requires_whole_tokens_and_exact_alternatives(self):
        _, ctx47 = batch.build(47, batch.LESSONS[47])
        head, body = ctx47.split("</head>", 1)
        mistiming = head + "</head>" + body.replace("timing", "mistiming")
        with self.assertRaisesRegex(ValueError, "absent from visible deck text: timing"):
            batch.validate_rendered_vocabulary(47, mistiming)

        _, ctx41 = batch.build(41, batch.LESSONS[41])
        self.assertTrue(batch.phrase_is_visible(batch.visible_text(ctx41), "push it back"))
        head, body = ctx41.split("</head>", 1)
        backward = head + "</head>" + body.replace("push it back", "push backward")
        with self.assertRaisesRegex(ValueError, "absent from visible deck text: push back"):
            batch.validate_rendered_vocabulary(41, backward)

        self.assertFalse(batch.phrase_is_visible("mistiming", "timing"))
        self.assertFalse(batch.phrase_is_visible("push backward", "push back"))
        self.assertTrue(batch.phrase_is_visible("We need to push it back today.", "push it back"))

    def test_polysemy_and_stale_metadata_repairs_are_locked(self):
        ctx46 = batch.LESSONS[46]["vocab"]
        self.assertFalse(any("instead|" in field for field in ctx46))

        ctx47_new, ctx47_recycled, _, _ = batch.LESSONS[47]["vocab"]
        self.assertIn("not comfortable with|〜に不安がある", ctx47_new)
        self.assertNotIn("comfortable|", ctx47_recycled)
        self.assertIn("timing|タイミング|CORE-85", ctx47_recycled)
        self.assertNotIn("timing|日程|CORE-85", ctx47_recycled)

        self.assertIn("supplier|取引先|CORE-82", batch.LESSONS[43]["vocab"][1])
        self.assertIn("supplier|取引先|CORE-82", batch.LESSONS[48]["vocab"][1])
        self.assertNotIn("supplier|仕入先|CORE-82", batch.LESSONS[43]["vocab"][1])
        self.assertNotIn("supplier|仕入先|CORE-82", batch.LESSONS[48]["vocab"][1])

    def test_contextual_owner_citations_are_exact(self):
        citations = {
            item
            for lesson in batch.LESSONS.values()
            for field in lesson["vocab"]
            for item in field.split("; ")
            if re.search(r"\|CTX-\d+$", item)
        }
        self.assertEqual(
            citations,
            {
                "definitely|確実に|CTX-26",
                "push back|後ろへずらす|CTX-12",
                "final version|最終版|CTX-34",
                "on track|予定どおり|CTX-35",
                "before we move on|次へ進む前に|CTX-43",
            },
        )
        self.assertTrue(citations.issubset(batch.VISIBLE_PRIOR_CTX_OWNERS))
        self.assertIn("before we move on|次へ進む前に", batch.LESSONS[43]["vocab"][0])

    def test_semantic_scene_repairs_remain_grounded(self):
        self.assertEqual(
            batch.LESSONS[37]["scene_turns"][-1][1],
            "Understood. I will update the project plan now.",
        )
        self.assertEqual(batch.LESSONS[37]["scene_turns"][2][1], "Understood. What do you need from me?")
        self.assertIn("pricing file", batch.LESSONS[37]["transfer_turns"][0][1])
        self.assertIn("presentation slides", batch.LESSONS[37]["transfer_turns"][0][1])
        self.assertIn("definitely not", batch.LESSONS[37]["tip"][5][2])

        self.assertIn("keep me posted", batch.LESSONS[38]["tip"][5][2])
        self.assertIn("Your team thinks ours", batch.LESSONS[38]["scene_turns"][0][1])
        self.assertIn("our team thinks yours", batch.LESSONS[38]["scene_turns"][0][1])

        ctx39 = batch.LESSONS[39]
        self.assertIn("this week's analysis", ctx39["transfer_turns"][0][1])
        self.assertIn("risk may become a problem later", ctx39["tip"][2])

        for english, japanese, _ in batch.LESSONS[40]["p2"]["rows"]:
            self.assertNotIn("realistic if{/t}", english)
            self.assertIn("is realistic{/t} if", english)
            self.assertIn("{t}", japanese)

        ctx41 = batch.LESSONS[41]
        self.assertEqual(ctx41["transfer_turns"][1], ("target", 1, 2))
        self.assertIn("tomorrow's demo", ctx41["transfer_turns"][0][1])
        self.assertIn("push it back until Friday", batch.core.strip_marks(ctx41["p2"]["rows"][2][0]))
        self.assertEqual(ctx41["p2"]["write"][0], "How far would you move the event?")
        self.assertIn("action, owner, and deadline", ctx41["live"][0])
        self.assertIn("___ will ___ by ___", ctx41["live"][2])

        ctx42 = batch.LESSONS[42]
        transfer = " ".join(
            turn[1] if turn[0] != "target"
            else batch.core.strip_marks(ctx42[f"p{turn[1]}"]["rows"][turn[2]][0])
            for turn in ctx42["transfer_turns"]
        )
        for term in ("meeting notes", "project files", "write the notes", "send the files"):
            self.assertIn(term, transfer)
        self.assertNotIn("launch email", transfer)
        self.assertNotIn("pricing page", transfer)
        self.assertIn("thought the other person owned them", ctx42["scene_turns"][0][1])
        self.assertIn("still have no owners", ctx42["transfer_turns"][0][1])
        for row in ctx42["p1"]["rows"]:
            self.assertEqual(len(row[2].split("|")), 4)
            self.assertNotRegex(row[2], r"\|and [A-Z][a-z]+\|")

        ctx43 = batch.LESSONS[43]
        self.assertIn("client results change", batch.core.strip_marks(ctx43["p2"]["rows"][2][0]))
        self.assertNotIn("forecast is revised", batch.core.strip_marks(ctx43["p2"]["rows"][2][0]))
        self.assertEqual(ctx43["transfer_turns"][3], ("target", 2, 2))

        ctx44 = batch.LESSONS[44]
        self.assertEqual(ctx44["scene_turns"][0][1], "Let's test option B first.")
        self.assertIn("one smaller pilot", ctx44["transfer_turns"][0][1])
        self.assertIn("June review", ctx44["transfer_turns"][4][1])

        ctx45 = batch.LESSONS[45]
        self.assertIn("suggest", ctx45["tip"][0].casefold())
        self.assertIn("three implementation options", ctx45["scene"])
        self.assertIn("options A, B, and C", ctx45["scene_turns"][0][1])
        self.assertIn("A = ___; B = ___; C = ___", ctx45["live"][2])
        self.assertNotIn("___er", ctx45["live"][2])
        self.assertIn("easier や more practical", ctx45["live"][3])
        self.assertIn("three options you named", ctx45["live"][4])

        ctx48 = batch.LESSONS[48]
        self.assertIn("options A, B, and C", ctx48["scene_turns"][0][1])
        self.assertIn("three real or imaginary options", ctx48["live"][4])
        self.assertIn("three suppliers", ctx48["transfer_turns"][0][1])

    def test_authoritative_scene_cardinalities_and_ambiguities_are_preserved(self):
        brief_scenes = {}
        for number in (38, 42, 45, 48):
            brief = ROOT / "sandbox/drafts/en/tracks/2-contextual-english/toc" / f"CTX-{number}.md"
            source = brief.read_text(encoding="utf-8")
            match = re.search(r"^- \*\*Scene:\*\* (.+)$", source, re.MULTILINE)
            self.assertIsNotNone(match, number)
            brief_scenes[number] = match.group(1)
        self.assertIn("two teams", brief_scenes[38])
        self.assertIn("responsibilities remain unclear", brief_scenes[42])
        self.assertIn("three options", brief_scenes[45])
        self.assertIn("three options", brief_scenes[48])


if __name__ == "__main__":
    unittest.main()
