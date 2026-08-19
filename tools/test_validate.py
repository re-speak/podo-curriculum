from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
import unittest.mock

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location("validate", TOOLS / "validate.py")
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate
SPEC.loader.exec_module(validate)


class DeclaredRetirementTests(unittest.TestCase):
    """Layer 6's escape hatch: a retirement done directly in the DB and GCS."""

    def _log(self, text: str, returncode: int = 0):
        result = unittest.mock.Mock()
        result.returncode = returncode
        result.stdout = text
        return unittest.mock.patch.object(validate.subprocess, "run", return_value=result)

    def test_reads_the_trailer(self):
        with self._log("chore: drop the test courses\n\n"
                       "Retired-course: courses/kr/intermediate-test\n"):
            self.assertEqual(validate.declared_retirements("origin/stage"),
                             {"courses/kr/intermediate-test"})

    def test_reads_several(self):
        with self._log("Retired-course: courses/kr/a\nRetired-course: courses/kr/b\n"):
            self.assertEqual(validate.declared_retirements("x"),
                             {"courses/kr/a", "courses/kr/b"})

    def test_ignores_prose_that_merely_mentions_it(self):
        with self._log("we should add a Retired-course trailer some day\n"):
            self.assertEqual(validate.declared_retirements("x"), set())

    def test_empty_when_git_fails(self):
        with self._log("", returncode=128):
            self.assertEqual(validate.declared_retirements("x"), set())

    def test_empty_when_git_is_missing(self):
        with unittest.mock.patch.object(validate.subprocess, "run", side_effect=OSError):
            self.assertEqual(validate.declared_retirements("x"), set())


if __name__ == "__main__":
    unittest.main()
