from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import page_review


class PageReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.lesson = self.root / "lesson.html"
        self.review_path = self.root / "review.json"
        self.lesson.write_text(
            '<main><section data-page-id="goal"></section>'
            '<section data-page-id="practice"></section></main>',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def completed_review(self) -> dict:
        review = page_review.scaffold(self.lesson, self.review_path)
        review["stages"].update(
            generated="pass",
            mechanicalValidation="pass",
            humanPageAudit="pass",
        )
        for page in review["pages"]:
            page.update(
                learnerAction="The learner reads the visible sentence aloud.",
                tutorAction="The tutor listens and advances after the response.",
                targetOrPrompt="The complete target sentence remains visible.",
                learningTarget="The learner retrieves the lesson's stated target.",
                pedagogicalValue="The page retrieves a distinct sentence from the learner.",
                failureDiagnosis="A wrong answer identifies trouble with the stated target.",
                nonTargetSupport="All language outside the target remains visible or supported.",
                articleTreatment="No article decision is present on this test page.",
                choiceQuality="Not applicable because this page has no answer choices.",
                componentConsistency="Uses the approved component for this teaching job.",
                visual360="pass",
                visual480="pass",
                verdict="pass",
            )
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        return review

    def test_scaffold_tracks_every_page_in_order(self) -> None:
        review = page_review.scaffold(self.lesson, self.review_path)
        self.assertEqual([page["pageId"] for page in review["pages"]], ["goal", "practice"])
        self.assertEqual(review["lessonSha256"], page_review.sha256(self.lesson))

    def test_scaffold_captures_support_stage_from_page_root(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="practice" '
            'data-scaffolding-contract="target-v2" data-support-stage="supported">'
            '<span class="hint-chip">休暇:holiday</span></section></main>',
            encoding="utf-8",
        )
        review = page_review.scaffold(self.lesson, self.review_path)
        self.assertEqual(review["pages"][0]["evidence"]["supportStage"], "supported")

    def test_incomplete_template_fails(self) -> None:
        review = page_review.scaffold(self.lesson, self.review_path)
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("learnerAction" in error for error in errors))
        self.assertTrue(any("humanPageAudit" in error for error in errors))

    def test_complete_review_passes_but_owner_is_separate(self) -> None:
        self.completed_review()
        self.assertEqual(page_review.validate(self.lesson, self.review_path), [])
        owner_errors = page_review.validate(self.lesson, self.review_path, require_owner=True)
        self.assertEqual(owner_errors, ["stages.ownerApproval must be pass for owner-approved status"])

    def test_changed_lesson_invalidates_review(self) -> None:
        self.completed_review()
        self.lesson.write_text(
            '<main><section data-page-id="goal"></section>'
            '<section data-page-id="practice"></section><p>changed</p></main>',
            encoding="utf-8",
        )
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("lessonSha256 is stale" in error for error in errors))

    def test_page_coverage_and_order_are_exact(self) -> None:
        review = self.completed_review()
        review["pages"].reverse()
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("page order/coverage differs" in error for error in errors))

    def test_extracted_evidence_cannot_be_rationalized_away(self) -> None:
        review = self.completed_review()
        review["pages"][1]["evidence"]["blankAnswers"] = ["unrelated vocabulary"]
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("extracted evidence differs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
