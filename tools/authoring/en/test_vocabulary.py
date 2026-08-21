#!/usr/bin/env python3
"""Regression tests for vocabulary ownership, load and ledger generation."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_running_lexicon
import check_deck
import vocabulary


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
PILOT = ROOT / "tracks/1-core-patterns/courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"


def metadata(new: str = "box|箱", *, status: str = "reviewed", waiver: str = "") -> str:
    waiver_meta = f'<meta name="podo:vocabulary-waiver" content="{waiver}">' if waiver else ""
    return f"""
<meta name="podo:vocabulary-status" content="{status}">
<meta name="podo:vocabulary:new" content="{new}">
<meta name="podo:vocabulary:recycled" content="big|大きい|CORE-19">
<meta name="podo:vocabulary:assumed" content="menu|メニュー">
<meta name="podo:vocabulary:receptive" content="counter|カウンター">
{waiver_meta}
"""


def deck_metadata(review_id: str, new: str = "surprise|驚かせる") -> str:
    return f'<meta name="podo:review-id" content="{review_id}">\n' + metadata(new)


class VocabularyTests(unittest.TestCase):
    def test_pilot_owns_box_and_recycles_bag_from_core_5(self):
        data = vocabulary.parse(PILOT.read_text(encoding="utf-8"), source=PILOT)
        self.assertEqual(data["status"], "reviewed")
        self.assertEqual(
            [
                (entry["english"], entry["japanese"])
                for entry in data["categories"]["new"]
            ],
            [("box", "箱")],
        )
        self.assertEqual(
            [
                (entry["english"], entry["japanese"], entry["source"])
                for entry in data["categories"]["recycled"]
            ],
            [("bag", "かばん", "CORE-5")],
        )

    def test_duplicate_across_categories_is_rejected(self):
        with self.assertRaisesRegex(vocabulary.VocabularyError, "both new and assumed"):
            vocabulary.parse(metadata().replace("menu|メニュー", "box|ボックス"))

    def test_more_than_eight_requires_a_waiver(self):
        nine = "; ".join(f"word{i}|語{i}" for i in range(9))
        result = vocabulary.load_result(vocabulary.parse(metadata(nine)))
        self.assertEqual(result[0], "error")
        waived = vocabulary.load_result(vocabulary.parse(metadata(nine, waiver="scene requires it")))
        self.assertEqual(waived[0], "warning")

    def test_hint_chip_words_are_machine_readable(self):
        page = '<span class="hint-chip">箱:box</span><span class="hint-chip">運ぶ:carry</span>'
        self.assertEqual(vocabulary.hint_words(page), {"box", "carry"})

    def test_reviewed_deck_cannot_leave_all_vocabulary_categories_empty(self):
        source = PILOT.read_text(encoding="utf-8")
        for category in ("new", "recycled", "assumed", "receptive"):
            source = __import__("re").sub(
                rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
                r"\1\2",
                source,
                count=1,
            )
        with tempfile.TemporaryDirectory(dir=ROOT / "tracks/1-core-patterns") as temporary:
            lesson = pathlib.Path(temporary) / "20-empty-vocabulary"
            lesson.mkdir()
            deck = lesson / "lesson.html"
            deck.write_text(source.replace(
                'content="20-asking-for-help"', 'content="20-empty-vocabulary"', 1
            ), encoding="utf-8")
            errors, _warnings = check_deck.check(deck)
            self.assertTrue(any("vocabulary ownership is empty" in item for item in errors))

    def test_running_lexicon_is_current(self):
        records = build_running_lexicon.collect(build_running_lexicon.decks())
        actual = (ROOT / "reference/running-lexicon.md").read_text(encoding="utf-8")
        self.assertEqual(actual, build_running_lexicon.render(records))

    def test_freetalking_versions_share_one_review_id_owner(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tracks/3-freetalking") as tmp:
            base = pathlib.Path(tmp)
            paths = []
            for course in ("talk-topic-accessible", "talk-topic-full"):
                path = base / course / "lessons/01-topic/lesson.html"
                path.parent.mkdir(parents=True)
                path.write_text(deck_metadata("FT-1"), encoding="utf-8")
                paths.append(path)
            records = build_running_lexicon.collect(paths)
            self.assertEqual([record["review_id"] for record in records], ["FT-1", "FT-1"])

    def test_different_freetalking_topics_cannot_both_own_a_new_word(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tracks/3-freetalking") as tmp:
            base = pathlib.Path(tmp)
            paths = []
            for number, review_id in ((1, "FT-1"), (2, "FT-2")):
                path = base / f"talk-topic-{number}" / f"lessons/{number:02d}-topic/lesson.html"
                path.parent.mkdir(parents=True)
                path.write_text(deck_metadata(review_id), encoding="utf-8")
                paths.append(path)
            with self.assertRaisesRegex(vocabulary.VocabularyError, "also declared new"):
                build_running_lexicon.collect(paths)

    def test_same_surface_form_with_a_different_sense_has_its_own_owner(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tracks/1-core-patterns") as tmp:
            base = pathlib.Path(tmp)
            paths = []
            for number, review_id, japanese in (
                (1, "CORE-1", "開いている"),
                (2, "CORE-2", "開ける"),
            ):
                path = base / f"core-topic-{number}" / f"lessons/{number:02d}-topic/lesson.html"
                path.parent.mkdir(parents=True)
                path.write_text(deck_metadata(review_id, f"open|{japanese}"), encoding="utf-8")
                paths.append(path)
            records = build_running_lexicon.collect(paths)
            self.assertEqual(
                [(item["review_id"], item["categories"]["new"][0]["japanese"]) for item in records],
                [("CORE-1", "開いている"), ("CORE-2", "開ける")],
            )

    def test_same_surface_form_and_same_sense_still_has_one_owner(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tracks/1-core-patterns") as tmp:
            base = pathlib.Path(tmp)
            paths = []
            for number, review_id in ((1, "CORE-1"), (2, "CORE-2")):
                path = base / f"core-topic-{number}" / f"lessons/{number:02d}-topic/lesson.html"
                path.parent.mkdir(parents=True)
                path.write_text(deck_metadata(review_id, "open|開ける"), encoding="utf-8")
                paths.append(path)
            with self.assertRaisesRegex(vocabulary.VocabularyError, "also declared new"):
                build_running_lexicon.collect(paths)


if __name__ == "__main__":
    unittest.main()
