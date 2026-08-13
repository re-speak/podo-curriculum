from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import upstream


def _split_layout(root: pathlib.Path) -> None:
    """The current upstream shape: shared runtime beside two language trees."""
    (root / "runtime").mkdir()
    (root / "korean" / "trial").mkdir(parents=True)
    (root / "korean" / "tracks").mkdir()
    (root / "english" / "tracks").mkdir(parents=True)


class UpstreamResolutionTest(unittest.TestCase):
    def test_current_repo_root_and_korean_directory_resolve_identically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _split_layout(root)

            content = root / "korean"
            self.assertEqual(upstream.resolve(root), content.resolve())
            self.assertEqual(upstream.resolve(content), content.resolve())
            self.assertEqual(upstream.site_root(content), root)
            self.assertEqual(upstream.runtime_root(content), root / "runtime")

    def test_english_resolves_from_the_repo_root_and_from_its_own_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _split_layout(root)

            content = root / "english"
            self.assertEqual(upstream.resolve(root, "english"), content.resolve())
            self.assertEqual(upstream.resolve(content, "english"), content.resolve())
            # English has no trial/ tree; tracks/ alone has to be enough.
            self.assertEqual(upstream.site_root(content), root)
            self.assertEqual(upstream.runtime_root(content), root / "runtime")

    def test_a_language_directory_is_never_accepted_for_another_language(self):
        """The failure this guards: syncing Korean into English's destination.

        Both trees have the same internal shape, so a fallback that returns
        "whichever content root exists" would find korean/tracks and mirror it
        under en/ without a word.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _split_layout(root)

            with self.assertRaises(upstream.UpstreamMissing):
                upstream.resolve(root / "korean", "english")
            with self.assertRaises(upstream.UpstreamMissing):
                upstream.resolve(root / "english", "korean")

    def test_missing_language_raises_rather_than_falling_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "runtime").mkdir()
            (root / "korean" / "tracks").mkdir(parents=True)

            self.assertEqual(sorted(upstream.available(root)), ["korean"])
            with self.assertRaises(upstream.UpstreamMissing):
                upstream.resolve(root, "english")

    def test_available_reports_every_language_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _split_layout(root)

            self.assertEqual(upstream.available(root),
                             {"korean": (root / "korean").resolve(),
                              "english": (root / "english").resolve()})

    def test_unknown_language_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _split_layout(root)

            with self.assertRaises(upstream.UpstreamMissing):
                upstream.resolve(root, "japanese")

    def test_legacy_korean_root_still_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = pathlib.Path(tmp)
            (content / "runtime").mkdir()
            (content / "trial").mkdir()

            self.assertEqual(upstream.resolve(content), content.resolve())
            self.assertEqual(upstream.site_root(content), content)
            self.assertEqual(upstream.runtime_root(content), content / "runtime")

    def test_rejects_half_of_the_split_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "runtime").mkdir()
            with self.assertRaises(upstream.UpstreamMissing):
                upstream.resolve(root)
            self.assertEqual(upstream.available(root), {})


if __name__ == "__main__":
    unittest.main()
