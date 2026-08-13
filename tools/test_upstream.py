from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import upstream


class UpstreamResolutionTest(unittest.TestCase):
    def test_current_repo_root_and_korean_directory_resolve_identically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "runtime").mkdir()
            (root / "korean" / "trial").mkdir(parents=True)

            content = root / "korean"
            self.assertEqual(upstream.resolve(root), content.resolve())
            self.assertEqual(upstream.resolve(content), content.resolve())
            self.assertEqual(upstream.site_root(content), root)
            self.assertEqual(upstream.runtime_root(content), root / "runtime")

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


if __name__ == "__main__":
    unittest.main()
