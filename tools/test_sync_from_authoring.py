from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest


TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sync = _load("sync_from_authoring", "sync-from-authoring.py")
trial = _load("import_trial_decks", "import-trial-decks.py")


class AuthoringMirrorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.repo = self.root / "downstream"
        self.repo.mkdir()
        (self.repo / "shared").mkdir()
        self.old_repo = sync.REPO
        sync.REPO = self.repo
        sync.done.clear()

    def tearDown(self):
        sync.REPO = self.old_repo
        sync.done.clear()
        self.tmp.cleanup()

    def test_complete_english_track_replaces_split_legacy_layout(self):
        source = self.root / "upstream" / "english"
        track = source / "tracks" / "1-core-patterns"
        lesson = track / "courses" / "core-first" / "lessons" / "01-hello"
        brief = track / "toc" / "CORE-1.md"
        lesson.mkdir(parents=True)
        brief.parent.mkdir(parents=True)
        (track / "table-of-contents.md").write_text("# TOC\n", encoding="utf-8")
        (track / "lesson-blueprint.md").write_text("# Blueprint\n", encoding="utf-8")
        brief.write_text("# Brief\n", encoding="utf-8")
        (lesson / "lesson.yaml").write_text("kind: Lesson\n", encoding="utf-8")
        (lesson / "lesson.html").write_text(
            '<link rel="stylesheet" href="../../../../../../../runtime/css/lesson-card.css">',
            encoding="utf-8")
        (source / "reference").mkdir()
        (source / "reference" / "evidence.md").write_text("evidence\n", encoding="utf-8")

        old_plan = self.repo / "references" / "en" / "tracks" / "old.md"
        old_sample = self.repo / "sandbox" / "track-samples" / "en" / "old.html"
        old_plan.parent.mkdir(parents=True)
        old_sample.parent.mkdir(parents=True)
        old_plan.write_text("old\n", encoding="utf-8")
        old_sample.write_text("old\n", encoding="utf-8")

        sync.sync_authoring(source, "en", "english")
        sync.sync_reference_material(source, "en", "english")
        sync.remove_legacy_layout("en", "english")

        mirrored = (self.repo / "sandbox" / "authoring" / "en" / "tracks" /
                    "1-core-patterns")
        self.assertEqual((mirrored / "table-of-contents.md").read_text(), "# TOC\n")
        self.assertEqual((mirrored / "toc" / "CORE-1.md").read_text(), "# Brief\n")
        self.assertTrue((mirrored / "courses" / "core-first" / "lessons" /
                         "01-hello" / "lesson.yaml").is_file())
        html = (mirrored / "courses" / "core-first" / "lessons" /
                "01-hello" / "lesson.html").read_text()
        self.assertIn("shared/css/lesson-card.css", html)
        self.assertNotIn("runtime/css/lesson-card.css", html)
        self.assertEqual(
            (self.repo / "references" / "en" / "reference" / "evidence.md").read_text(),
            "evidence\n")
        self.assertFalse((self.repo / "references" / "en" / "tracks").exists())
        self.assertFalse((self.repo / "sandbox" / "track-samples" / "en").exists())

    def test_korean_trial_is_namespaced_and_old_roots_are_removed(self):
        source = self.root / "upstream" / "korean"
        (source / "tracks").mkdir(parents=True)
        trial_lesson = source / "trial" / "lessons" / "trial.html"
        trial_lesson.parent.mkdir(parents=True)
        trial_lesson.write_text(
            '<link rel="stylesheet" href="../../runtime/css/trial.css">',
            encoding="utf-8")

        for relative in ("sandbox/trial/old", "sandbox/interactive/old",
                         "sandbox/viewers/old"):
            path = self.repo / relative
            path.mkdir(parents=True)

        sync.sync_authoring(source, "kr", "korean")
        sync.remove_legacy_layout("kr", "korean")

        mirrored = (self.repo / "sandbox" / "authoring" / "kr" / "trial" /
                    "lessons" / "trial.html")
        self.assertTrue(mirrored.is_file())
        self.assertIn("shared/css/trial.css", mirrored.read_text())
        self.assertFalse((self.repo / "sandbox" / "trial").exists())
        self.assertFalse((self.repo / "sandbox" / "interactive").exists())
        self.assertFalse((self.repo / "sandbox" / "viewers").exists())

    def test_trial_promoter_accepts_repointed_shared_stylesheets(self):
        raw = ('<link rel="stylesheet" href="../../../../../shared/css/trial.css">\n'
               '<script src="../../../../../shared/js/pager.js"></script>')
        page, scripts, assets = trial.flatten(raw)

        self.assertIn('href="trial.css"', page)
        self.assertIn('src="pager.js"', page)
        self.assertEqual(scripts, ["pager.js"])
        self.assertEqual(assets, [])

    def test_trial_promoter_rejects_runtime_promoted_control_shells(self):
        raw = '<span class="slot" data-sync-id="answer">정답</span>'
        with self.assertRaisesRegex(trial.ImportError_, "runtime-promoted control"):
            trial.audit_static_controls(raw, "trial.html")

    def test_trial_promoter_preserves_and_counts_static_controls(self):
        raw = (
            '<input class="slot-input" type="text" data-sync-id="slot" '
            'data-answer="정답">'
            '<span class="answer-space as-input"><textarea class="free-input" '
            'data-sync-id="free"></textarea></span>'
            '<span class="answer-space build-zone" data-sync-id="order" '
            'data-sync-kind="order" data-a="문장"></span>'
        )
        self.assertEqual(
            trial.audit_static_controls(raw, "trial.html"),
            {"slot": 1, "input": 0, "free": 1, "build": 1},
        )


if __name__ == "__main__":
    unittest.main()
