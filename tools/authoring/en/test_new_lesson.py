#!/usr/bin/env python3
"""Focused tests for the non-creative lesson shell operations."""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_lesson


PILOT = new_lesson.ENGLISH / "tracks/1-core-patterns/courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"


class LessonShellTests(unittest.TestCase):
    def test_core_and_contextual_have_approved_default_shells(self):
        for track_name, relative in new_lesson.CANONICAL_DECKS.items():
            with self.subTest(track=track_name):
                self.assertTrue((new_lesson.ENGLISH / "tracks" / track_name / relative).is_file())

    def test_split_removes_pages_and_canonical_identity_comment(self):
        head, foot = new_lesson.split_shell(PILOT.read_text(encoding="utf-8"))
        self.assertIn('<div class="phone">', head)
        self.assertNotIn('data-page-id=', head + foot)
        self.assertNotIn('CORE 20', head + foot)
        self.assertIn('shared/js/pager.js', foot)

    def test_retarget_changes_all_identity_fields(self):
        head, _foot = new_lesson.split_shell(PILOT.read_text(encoding="utf-8"))
        changed = new_lesson.retarget(
            head,
            review_id="CORE-31",
            lesson_id="31-past-action",
            level="A2",
            title="Past action",
            title_ko="지난 일 말하기",
            title_ja="過去のできごと",
            version="2099-01-02",
        )
        self.assertIn('content="CORE-31"', changed)
        self.assertIn('content="31-past-action"', changed)
        self.assertIn('content="A2"', changed)
        self.assertIn('content="2099-01-02"', changed)
        self.assertIn('<title>Past action — PODO English</title>', changed)
        # All three catalogue name columns, stamped from the shell's own slots.
        self.assertIn('name="podo:title-ko" content="지난 일 말하기"', changed)
        self.assertIn('name="podo:title-en" content="Past action"', changed)
        self.assertIn('name="podo:title-ja" content="過去のできごと"', changed)
        self.assertNotIn('도와주시겠어요', changed)
        self.assertIn('name="podo:vocabulary-status" content="todo"', changed)
        self.assertIn('name="podo:vocabulary:new" content=""', changed)
        self.assertNotIn('box|箱', changed)

    def test_redepth_resolves_shared_refs_from_a_planned_deck_location(self):
        with tempfile.TemporaryDirectory(dir=new_lesson.ENGLISH / "tracks/1-core-patterns") as tmp:
            out = pathlib.Path(tmp) / "courses/x/lessons/31-past-action/lesson.html"
            page = new_lesson.redepth('<link href="../../shared/css/lesson-card.css"><img src="../../korean/trial/assets/well-done.svg">', out)
            refs = [part.split('"')[1] for part in page.split('>') if '="' in part]
            self.assertTrue(all((out.parent / ref).resolve().is_file() for ref in refs))

    def test_feedback_runtime_follows_final_controls_not_the_pilot_footer(self):
        out = PILOT.parent / "generated/lesson.html"
        activities = '  <script src="../../shared/js/activities.js"></script>'
        feedback = '  <script src="../../shared/js/feedback.js"></script>'
        pager = '  <nav class="pager"></nav>'

        without_control = new_lesson.redepth(
            "\n".join((activities, feedback, '<p>No feedback control here.</p>', pager)), out
        )
        self.assertNotIn("shared/js/feedback.js", without_control)

        for inherited_feedback in (False, True):
            with self.subTest(inherited_feedback=inherited_feedback):
                lines = [activities]
                if inherited_feedback:
                    lines.append(feedback)
                lines.extend(('<div class="fb" data-fb="own-sentence"></div>', pager))
                with_control = new_lesson.redepth("\n".join(lines), out)
                self.assertEqual(with_control.count("shared/js/feedback.js"), 1)
                self.assertLess(with_control.index("shared/js/activities.js"),
                                with_control.index("shared/js/feedback.js"))
                self.assertLess(with_control.index("shared/js/feedback.js"),
                                with_control.index('class="pager"'))

    def test_feedback_detection_ignores_markup_shaped_inert_text(self):
        out = PILOT.parent / "generated/lesson.html"
        activities = '  <script src="../../shared/js/activities.js"></script>'
        feedback = '  <script src="../../shared/js/feedback.js"></script>'
        pager = '  <nav class="pager"></nav>'
        fake_controls = {
            "full tag in comment": '<!-- <div class="fb" data-fb="fake"></div> -->',
            "tag in script text": '<script>const fake = `<div data-fb="fake"></div>`;</script>',
            "tag in template": '<template><div data-fb="fake"></div></template>',
            "tag in attribute value": '<div data-example="&lt;div data-fb=\'fake\'&gt;"></div>',
            "bare comment token": '<!-- data-fb="fake" -->',
        }
        for label, fake in fake_controls.items():
            with self.subTest(label=label):
                page = new_lesson.redepth("\n".join((activities, feedback, fake, pager)), out)
                self.assertNotIn("shared/js/feedback.js", page)

    def test_feedback_control_without_activities_runtime_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "requires activities.js"):
            new_lesson.redepth('<div data-fb="own-sentence"></div>', PILOT)

    def test_core_shell_comment_does_not_load_yomi(self):
        head, foot = new_lesson.split_shell(PILOT.read_text(encoding="utf-8"))
        shell = head + foot
        self.assertIn("NO yomi.js", shell)
        self.assertIsNone(re.search(r'<script\b[^>]*\bsrc="[^"]*yomi\.js"', shell, re.I))
        self.assertIsNone(re.search(r'class="[^"]*\byomi\b[^"]*"', shell, re.I))


if __name__ == "__main__":
    unittest.main()
