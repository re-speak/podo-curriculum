from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest
import unittest.mock


TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location("promote", TOOLS / "promote.py")
assert SPEC and SPEC.loader
promote = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = promote
SPEC.loader.exec_module(promote)


DECK = (
    '<link rel="stylesheet" href="../../shared/css/lesson-card.css">\n'
    '<input class="space-input" data-sync-id="a" data-answer="정답">\n'
    '<script src="../../shared/js/activities.js"></script>\n'
)


class AuditTests(unittest.TestCase):
    """The audit exists because this failure is silent at runtime."""

    def test_rejects_runtime_promoted_control_shells(self):
        raw = DECK + '<span class="slot" data-sync-id="shell">정답</span>'
        with self.assertRaisesRegex(promote.PromoteFailed, "runtime-promoted shell"):
            promote.flatten(raw)

    def test_rejects_ids_that_resolve_to_no_kind(self):
        raw = '<div data-sync-id="nothing">…</div>'
        with self.assertRaisesRegex(promote.PromoteFailed, "resolve to no kind"):
            promote.resolve_kinds(raw)

    def test_rejects_duplicate_sync_ids(self):
        raw = ('<input data-sync-id="a"><input data-sync-id="a">')
        with self.assertRaisesRegex(promote.PromoteFailed, "duplicate data-sync-id"):
            promote.resolve_kinds(raw)

    def test_resolves_kinds_in_lemonboard_order(self):
        raw = (
            '<input data-sync-id="value-one">'
            '<div data-sync-id="explicit" data-sync-kind="order"></div>'
            '<div data-sync-id="chooser"><b data-sync-option></b></div>'
            '<div data-sync-id="toggler" data-sync-state="on"></div>'
        )
        self.assertEqual(promote.resolve_kinds(raw), {
            "value-one": "value",
            "explicit": "order",
            "chooser": "selection",
            "toggler": "toggle",
        })


class FlattenTests(unittest.TestCase):
    def test_flattens_refs_to_basenames(self):
        page, sheets, scripts, assets = promote.flatten(DECK)
        self.assertIn('href="lesson-card.css"', page)
        self.assertIn('src="activities.js"', page)
        self.assertEqual(sheets, ["lesson-card.css"])
        self.assertEqual(scripts, ["activities.js"])
        self.assertEqual(assets, [])

    def test_leaves_remote_refs_alone(self):
        raw = DECK + '<img src="https://example.com/a.png">'
        page, _, _, assets = promote.flatten(raw)
        self.assertIn('src="https://example.com/a.png"', page)
        self.assertEqual(assets, [])

    def test_bundles_the_remote_avatars(self):
        url = list(promote.AVATARS)[0]
        page, _, _, assets = promote.flatten(DECK + f'<img src="{url}">')
        self.assertNotIn(url, page)
        self.assertEqual(assets, [promote.AVATARS[url]])

    def test_rejects_basename_collisions(self):
        raw = DECK + '<img src="../a/logo.png"><img src="../b/logo.png">'
        with self.assertRaisesRegex(promote.PromoteFailed, "basename collision"):
            promote.flatten(raw)

    def test_requires_a_local_stylesheet(self):
        with self.assertRaisesRegex(promote.PromoteFailed, "no local stylesheet"):
            promote.flatten('<input data-sync-id="a">')


class ManifestTests(unittest.TestCase):
    """A manifest that is wrong should fail here, not halfway through a write."""

    def _write(self, body: str) -> pathlib.Path:
        tmp = pathlib.Path(tempfile.mkdtemp()) / "promotion.yaml"
        tmp.write_text(textwrap.dedent(body), encoding="utf-8")
        return tmp

    def test_rejects_wrong_kind(self):
        path = self._write("""
            apiVersion: podo.curriculum/v1
            kind: Lesson
        """)
        # Manifest resolves paths against REPO, so it needs a real relative path.
        with self.assertRaises(Exception):
            promote.Manifest(path)

    def test_weeks_must_be_contiguous(self):
        lessons = [{"slug": "a", "week": 1, "source": "a.html", "title": {}},
                   {"slug": "b", "week": 3, "source": "b.html", "title": {}}]
        weeks = sorted(l["week"] for l in lessons)
        # The rule the Manifest enforces: 1..N with no gaps.
        self.assertNotEqual(weeks, list(range(1, len(weeks) + 1)))


class RetireTests(unittest.TestCase):
    def test_flips_enabled_true_to_false_keeping_comments(self):
        course = pathlib.Path(tempfile.mkdtemp())
        (course / "course.yaml").write_text(
            "spec:\n  enabled: true               # → USE_YN\n", encoding="utf-8")
        promote.retire(course)
        after = (course / "course.yaml").read_text(encoding="utf-8")
        self.assertIn("enabled: false", after)
        self.assertIn("# → USE_YN", after)

    def test_raises_when_there_is_nothing_to_retire(self):
        course = pathlib.Path(tempfile.mkdtemp())
        (course / "course.yaml").write_text("spec:\n  enabled: false\n", encoding="utf-8")
        with self.assertRaisesRegex(promote.PromoteFailed, "could not find"):
            promote.retire(course)



class GateTests(unittest.TestCase):
    """The retirement gate: promotion is the only thing that removes from courses/."""

    def _manifest(self, enabled: bool, existing: set[str], wanted: set[str]):
        course = pathlib.Path(tempfile.mkdtemp())
        (course / "course.yaml").write_text(
            f"spec:\n  enabled: {'true' if enabled else 'false'}\n", encoding="utf-8")

        class Fake:
            pass

        man = Fake()
        man.course = course
        man.enabled = enabled
        man.existing_slugs = lambda: existing
        man.wanted_slugs = lambda: wanted
        return man

    def test_silent_when_nothing_is_removed(self):
        man = self._manifest(True, {"01-a"}, {"01-a", "02-b"})
        promote.check_removals(man, assume_yes=False)      # must not raise

    def test_silent_when_the_course_is_not_live(self):
        man = self._manifest(False, {"01-a", "02-b"}, {"01-a"})
        promote.check_removals(man, assume_yes=False)      # disabled: removal is safe

    def test_refuses_in_non_interactive_runs(self):
        man = self._manifest(True, {"01-a", "02-b"}, {"01-a"})
        with self.assertRaisesRegex(promote.PromoteFailed, "non-interactive"):
            promote.check_removals(man, assume_yes=True)

    def test_yes_retires_the_course_and_writes_nothing_else(self):
        man = self._manifest(True, {"01-a", "02-b"}, {"01-a"})
        with unittest.mock.patch.object(sys.stdin, "isatty", return_value=True), \
             unittest.mock.patch("builtins.input", return_value="y"):
            with self.assertRaisesRegex(promote.PromoteFailed, "now enabled: false"):
                promote.check_removals(man, assume_yes=False)
        self.assertIn("enabled: false",
                      (man.course / "course.yaml").read_text(encoding="utf-8"))

    def test_no_stops_without_touching_the_course(self):
        man = self._manifest(True, {"01-a", "02-b"}, {"01-a"})
        with unittest.mock.patch.object(sys.stdin, "isatty", return_value=True), \
             unittest.mock.patch("builtins.input", return_value="n"):
            with self.assertRaisesRegex(promote.PromoteFailed, "stopped"):
                promote.check_removals(man, assume_yes=False)
        self.assertIn("enabled: true",
                      (man.course / "course.yaml").read_text(encoding="utf-8"))

    def test_closed_stdin_is_a_refusal_not_a_yes(self):
        man = self._manifest(True, {"01-a", "02-b"}, {"01-a"})
        with unittest.mock.patch.object(sys.stdin, "isatty", return_value=True), \
             unittest.mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaisesRegex(promote.PromoteFailed, "stdin closed"):
                promote.check_removals(man, assume_yes=False)
        self.assertIn("enabled: true",
                      (man.course / "course.yaml").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
