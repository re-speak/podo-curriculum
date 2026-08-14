from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest


TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location(
    "import_trial_decks", TOOLS / "import-trial-decks.py")
assert SPEC and SPEC.loader
trial = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = trial
SPEC.loader.exec_module(trial)


class TrialImporterTests(unittest.TestCase):
    def test_rejects_runtime_promoted_control_shells(self):
        raw = '<span class="slot" data-sync-id="answer">정답</span>'
        with self.assertRaisesRegex(trial.ImportError_, "runtime-promoted control"):
            trial.audit_static_controls(raw, "trial.html")

    def test_preserves_and_counts_static_controls(self):
        raw = (
            '<input class="slot-input" type="text" data-sync-id="slot" '
            'data-answer="정답">'
            '<span class="answer-space as-input"><input class="space-input" '
            'data-sync-id="input" data-answer="문장"></span>'
            '<span class="answer-space as-input"><textarea class="free-input" '
            'data-sync-id="free"></textarea></span>'
            '<span class="answer-space build-zone" data-sync-id="order" '
            'data-sync-kind="order" data-a="문장"></span>'
        )
        self.assertEqual(
            trial.audit_static_controls(raw, "trial.html"),
            {"slot": 1, "input": 1, "free": 1, "build": 1},
        )

    def test_build_bundles_activities_from_shared_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            shared = root / "shared"
            (shared / "css").mkdir(parents=True)
            (shared / "js").mkdir()
            for sheet in ("lesson-card.css", "trial.css"):
                (shared / "css" / sheet).write_text(sheet, encoding="utf-8")
            canonical = "window.runtimeSource = 'shared';\n"
            (shared / "js" / "activities.js").write_text(canonical, encoding="utf-8")

            original_repo = trial.REPO
            trial.REPO = root
            try:
                target = root / "deck"
                trial.build_deck(
                    target,
                    "<html></html>",
                    ["activities.js"],
                    [],
                    root / "authoring",
                )
            finally:
                trial.REPO = original_repo

            self.assertEqual(
                (target / "activities.js").read_text(encoding="utf-8"), canonical)


if __name__ == "__main__":
    unittest.main()
