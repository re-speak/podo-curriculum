#!/usr/bin/env python3
"""The Korean checkers' command line: paths, --all, and honest exit codes.

Every checker here used to walk a corpus pinned in its source and return 0
whatever it printed. These tests pin the two halves of the fix: a positional
path is checked instead of the default corpus, and a checker that prints a
defect exits non-zero while one that prints a candidate does not.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent

HEAD = """\
<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="podo:lesson-id" content="{slug}">
<meta name="podo:level" content="초급">
<meta name="podo:title-ko" content="제목">
<meta name="podo:title-en" content="Title">
<meta name="podo:title-ja" content="タイトル">
</head><body>
"""
FOOT = "</body></html>\n"


def deck(tmp: pathlib.Path, body: str, slug: str = "01-fixture") -> pathlib.Path:
    """Write one deck into its own <NN-slug>/lesson.html, as the corpus does."""
    lesson = tmp / slug
    lesson.mkdir(parents=True, exist_ok=True)
    path = lesson / "lesson.html"
    path.write_text(HEAD.format(slug=slug) + body + FOOT, encoding="utf-8")
    return path


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HERE / script), *map(str, args)],
        capture_output=True, text=True)


CLEAN_PAGE = '<div class="page" data-page-id="p1-read" data-act="read">읽기</div>'
REORDER = """\
<div class="page" data-page-id="p1-reorder" data-act="reorder">
<div class="task-block">{chips}</div>
</div>
"""
CHIP = '<span class="choice">{}</span>'


class ArgumentShapeTests(unittest.TestCase):
    """A positional path replaces the pinned corpus; a track name still works."""

    def test_directory_and_named_deck_are_both_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            path = deck(tmp, CLEAN_PAGE)
            for target in (tmp, path):
                out = run("check_structure.py", target)
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertIn("01-fixture", out.stdout)

    def test_unknown_name_is_reported_as_a_track_lookup(self):
        out = run("check_structure.py", "no-such-track")
        self.assertIn("no such path", out.stderr)
        self.assertIn("sandbox/drafts/kr/tracks/no-such-track", out.stderr)

    def test_all_is_accepted_by_every_checker(self):
        for script in ("check_chips.py", "check_reorder.py", "check_teaching.py"):
            out = run(script, "--all")
            self.assertIn(out.returncode, (0, 1), out.stderr)
            self.assertTrue(out.stdout.strip(), script)


class ExitCodeTests(unittest.TestCase):
    """A printed defect fails; a printed candidate does not."""

    def test_structure_fails_on_a_duplicate_page_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, CLEAN_PAGE * 2)
            out = run("check_structure.py", tmp)
            self.assertEqual(out.returncode, 1)
            self.assertIn("dup data-page-id", out.stdout)

    def test_chips_fails_above_the_four_chunk_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, REORDER.format(chips="".join(CHIP.format(c) for c in "가나다라")))
            self.assertEqual(run("check_chips.py", tmp).returncode, 0)
            deck(tmp, REORDER.format(chips="".join(CHIP.format(c) for c in "가나다라마")))
            out = run("check_chips.py", tmp)
            self.assertEqual(out.returncode, 1)
            self.assertIn("over 4 chips: 1", out.stdout)

    def test_reorder_fails_when_the_chips_cannot_rebuild_the_answer(self):
        zone = ('<span class="answer-space build-zone" data-sync-id="r1" '
                'data-sync-kind="order" data-a="가 나 다"></span>')
        chips = ('<span class="choice" data-item-id="r1-1">가</span>'
                 '<span class="choice" data-item-id="r1-2">나</span>')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, f'<div data-page-id="p1-reorder">{zone}{chips}</div>')
            out = run("check_reorder.py", tmp)
            self.assertEqual(out.returncode, 1)
            self.assertIn("가나다", out.stdout)

    def test_teaching_fails_on_a_lesson_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, '<div data-page-id="p1-read">'
                      '<span class="ko">90과에서 배운 말이에요.</span></div>')
            out = run("check_teaching.py", tmp)
            self.assertEqual(out.returncode, 1)
            self.assertIn("[ref", out.stdout)

    def test_freetalk_fails_on_a_deck_that_is_not_a_freetalking_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, CLEAN_PAGE)
            out = run("check_freetalk.py", tmp)
            self.assertEqual(out.returncode, 1)
            self.assertIn("missing page(s)", out.stdout)


class AdvisoryTests(unittest.TestCase):
    """Two checkers surface candidates a human has to read. They say so."""

    DISTRACTOR = """\
<div data-page-id="p1-choose">
<div class="choose-row"><span class="translation">ja</span>
<span class="opt" data-correct>맞아요</span><span class="opt">있어요</span></div>
</div>
<div class="model-line"><span class="korean">있어요</span></div>
"""

    def test_distractors_is_advisory_until_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, self.DISTRACTOR)
            out = run("check_distractors.py", tmp)
            self.assertEqual(out.returncode, 0)
            self.assertIn("1 with a distractor", out.stdout)
            self.assertIn("advisory", out.stdout)
            self.assertEqual(run("check_distractors.py", tmp, "--strict").returncode, 1)

    def test_syllabus_is_advisory_until_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            deck(tmp, '<div data-page-id="p1-read">반갑습니다.</div>')
            out = run("check_syllabus.py", tmp)
            self.assertEqual(out.returncode, 0)
            self.assertIn("습니다(과24)", out.stdout)
            self.assertEqual(run("check_syllabus.py", tmp, "--strict").returncode, 1)


if __name__ == "__main__":
    unittest.main()
