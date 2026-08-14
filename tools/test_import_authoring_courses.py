from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location(
    "import_authoring_courses", HERE / "import-authoring-courses.py")
assert SPEC and SPEC.loader
importer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(importer)


def manifest(country: str = "JP", enabled: str = "false") -> bytes:
    return f"""apiVersion: podo.curriculum/v1
kind: Course
metadata:
  slug: example
spec:
  curriculumType: BASIC
  countryCode: {country}
  classLevel: \"100.010\"
  lessonTime: 25
  enabled: {enabled}
  title:
    ko: Example
""".encode()


class AuthoringCourseImportTests(unittest.TestCase):
    def test_country_code_is_read_without_transforming_manifest_bytes(self):
        raw = manifest("JP")
        self.assertEqual(importer.validate_manifest(raw, pathlib.Path("course.yaml")), "JP")
        self.assertEqual(raw, manifest("JP"))

    def test_country_code_is_required_exactly_once(self):
        raw = manifest().replace(b"  countryCode: JP\n", b"")
        with self.assertRaisesRegex(importer.ImportError_, "exactly one"):
            importer.validate_manifest(raw, pathlib.Path("course.yaml"))

        duplicate = manifest().replace(
            b"  countryCode: JP\n", b"  countryCode: JP\n  countryCode: JP\n")
        with self.assertRaisesRegex(importer.ImportError_, "exactly one"):
            importer.validate_manifest(duplicate, pathlib.Path("course.yaml"))

    def test_invalid_country_code_is_rejected(self):
        with self.assertRaisesRegex(importer.ImportError_, "KR or JP"):
            importer.validate_manifest(manifest("US"), pathlib.Path("course.yaml"))

    def test_enabled_authoring_course_is_rejected(self):
        with self.assertRaisesRegex(importer.ImportError_, "enabled: false"):
            importer.validate_manifest(manifest(enabled="true"), pathlib.Path("course.yaml"))


if __name__ == "__main__":
    unittest.main()
