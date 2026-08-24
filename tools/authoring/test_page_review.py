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

    def test_freetalk_scaffold_requires_recorded_conversation_checks(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="warm-1">'
            '<span class="ko">What have you bought that was worth the money?</span>'
            '<span class="ja">買ってよかったものは何ですか？</span>'
            '<ul class="tn-more"><li>How often do you use it?</li>'
            '<li>Would you buy it again?</li></ul></section></main>',
            encoding="utf-8",
        )
        review = page_review.scaffold(self.lesson, self.review_path)
        self.assertEqual(
            set(review["pages"][0]["conversationReview"]),
            set(page_review.FREETALK_REVIEW_FIELDS),
        )
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("plausibleFirstAnswer" in error for error in errors))

    def test_no_answer_route_must_quote_a_current_followup(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="warm-1">'
            '<span class="ko">What have you bought that was worth the money?</span>'
            '<span class="ja">買ってよかったものは何ですか？</span>'
            '<ul class="tn-more"><li>How often do you use it?</li>'
            '<li>Would you buy it again?</li></ul></section></main>',
            encoding="utf-8",
        )
        review = self.completed_review()
        review["pages"][0]["targetOrPrompt"] = (
            "What have you bought that was worth the money?"
        )
        review["pages"][0]["conversationReview"] = {
            "plausibleFirstAnswer": "My rice cooker was worth the money.",
            "answerExpansion": "I can explain how often I use it and why it saves time.",
            "noAnswerFollowup": "What do people usually buy for convenience?",
        }
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("must quote one current tutor follow-up" in error for error in errors))

    def test_incomplete_template_fails(self) -> None:
        review = page_review.scaffold(self.lesson, self.review_path)
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("learnerAction" in error for error in errors))
        self.assertTrue(any("humanPageAudit" in error for error in errors))

    def test_visual_not_applicable_cannot_replace_viewport_review(self) -> None:
        review = self.completed_review()
        review["pages"][0]["visual360"] = "not-applicable"
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("visual360" in error for error in errors))

    def test_open_exchange_must_quote_actual_question_and_ask_back(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="p3-freetalk">'
            '<span class="korean">What would you change, and why?</span>'
            '<span class="korean">What would you change?</span>'
            '</section></main>',
            encoding="utf-8",
        )
        review = page_review.scaffold(self.lesson, self.review_path)
        review["stages"].update(
            generated="pass", mechanicalValidation="pass", humanPageAudit="pass"
        )
        page = review["pages"][0]
        page.update(
            learnerAction="The learner answers and asks the tutor back.",
            tutorAction="The tutor answers genuinely and follows up.",
            targetOrPrompt="A generic conversation about change.",
            learningTarget="The learner develops one relevant personal answer.",
            pedagogicalValue="The exchange creates reciprocal conversation.",
            failureDiagnosis="A generic or one-sided exchange would fail the task.",
            nonTargetSupport="The topic remains visible in both languages.",
            articleTreatment="No article is used on this open exchange page.",
            choiceQuality="There are no fixed choices on this open exchange page.",
            componentConsistency="The page uses the approved reciprocal exchange component.",
            visual360="pass",
            visual480="pass",
            verdict="pass",
        )
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("What would you change, and why?" in error for error in errors))
        self.assertTrue(any("What would you change?" in error for error in errors))

    def test_write_page_must_quote_visible_operating_prompt(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="p1-write">'
            '<span class="ko">Now use “I’m here for ___” to say why you are visiting.</span>'
            '</section></main>',
            encoding="utf-8",
        )
        review = page_review.scaffold(self.lesson, self.review_path)
        review["stages"].update(
            generated="pass", mechanicalValidation="pass", humanPageAudit="pass"
        )
        page = review["pages"][0]
        page.update(
            learnerAction="The learner makes one sentence with today's frame.",
            tutorAction="The tutor listens, captures, and corrects only if useful.",
            targetOrPrompt="Make one sentence using the pattern.",
            learningTarget="The learner uses the frame for one communicative purpose.",
            pedagogicalValue="The page transfers controlled practice into original content.",
            failureDiagnosis="A vague prompt would make the intended operation unclear.",
            nonTargetSupport="The frame remains visible above the response area.",
            articleTreatment="No article is used on this production page.",
            choiceQuality="The learner supplies open content rather than choosing an option.",
            componentConsistency="The page uses the approved feedback composition component.",
            visual360="pass",
            visual480="pass",
            verdict="pass",
        )
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("I’m here for" in error for error in errors))

    def test_complete_review_passes_but_owner_is_separate(self) -> None:
        self.completed_review()
        self.assertEqual(page_review.validate(self.lesson, self.review_path), [])
        owner_errors = page_review.validate(self.lesson, self.review_path, require_owner=True)
        self.assertEqual(owner_errors, ["stages.ownerApproval must be pass for owner-approved status"])

    def test_markdown_strips_trailing_whitespace_from_extracted_text(self) -> None:
        review = self.completed_review()
        review["pages"][0]["targetOrPrompt"] = "A visible target. "
        rendered = page_review.markdown(review)
        self.assertFalse(any(line.endswith(" ") for line in rendered.splitlines()))

    def test_changed_lesson_invalidates_review(self) -> None:
        self.completed_review()
        self.lesson.write_text(
            '<main><section data-page-id="goal"></section>'
            '<section data-page-id="practice"></section><p>changed</p></main>',
            encoding="utf-8",
        )
        errors = page_review.validate(self.lesson, self.review_path)
        self.assertTrue(any("lessonSha256 is stale" in error for error in errors))

    def test_refresh_updates_hash_and_evidence_without_erasing_judgments(self) -> None:
        review = self.completed_review()
        self.lesson.write_text(
            '<main><section data-page-id="goal"><span class="ending">new target</span></section>'
            '<section data-page-id="practice"></section></main>',
            encoding="utf-8",
        )
        page_review.refresh_evidence(self.lesson, self.review_path)
        refreshed = page_review.load_review(self.review_path)
        self.assertEqual(refreshed["lessonSha256"], page_review.sha256(self.lesson))
        self.assertEqual(refreshed["pages"][0]["evidence"]["targetHighlights"], ["new target"])
        self.assertEqual(
            refreshed["pages"][0]["pedagogicalValue"],
            review["pages"][0]["pedagogicalValue"],
        )

    def test_refresh_replaces_changed_prompt_without_erasing_review_context(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="warm-1">'
            '<span class="ko">What did you do yesterday?</span>'
            '</section></main>',
            encoding="utf-8",
        )
        review = page_review.scaffold(self.lesson, self.review_path)
        review["pages"][0]["targetOrPrompt"] = (
            "The page asks: What did you do yesterday? The answer is open."
        )
        review["pages"][0]["learnerAction"] = (
            "Answer What did you do yesterday? with one concrete detail."
        )
        self.review_path.write_text(json.dumps(review), encoding="utf-8")
        self.lesson.write_text(
            '<main><section data-page-id="warm-1">'
            '<span class="ko">What would you do with a free afternoon?</span>'
            '</section></main>',
            encoding="utf-8",
        )

        page_review.refresh_evidence(self.lesson, self.review_path)

        refreshed = page_review.load_review(self.review_path)
        target = refreshed["pages"][0]["targetOrPrompt"]
        self.assertIn("What would you do with a free afternoon?", target)
        self.assertIn("The answer is open.", target)
        self.assertNotIn("What did you do yesterday?", target)
        self.assertEqual(
            refreshed["pages"][0]["learnerAction"],
            "Answer What would you do with a free afternoon? with one concrete detail.",
        )

    def test_refresh_rebinds_complete_freetalk_spoken_contract(self) -> None:
        self.lesson.write_text(
            '<main><section data-page-id="warm-1">'
            '<span class="ko">What would you do with a free afternoon?</span>'
            '<span class="ja">自由な午後があったら、何をしますか？</span>'
            '<div class="tutor-note"><ul class="tn-more">'
            '<li>Would you go out or stay home?</li>'
            '<li>Who might join you?</li>'
            '</ul></div></section></main>',
            encoding="utf-8",
        )
        review = self.completed_review()
        page = review["pages"][0]
        page["targetOrPrompt"] = (
            "Old question / 古い質問 Tutor follow-ups: Old follow-up"
        )
        page["nonTargetSupport"] = "古い質問 was previously reviewed."
        self.review_path.write_text(json.dumps(review), encoding="utf-8")

        page_review.refresh_evidence(self.lesson, self.review_path)

        refreshed = page_review.load_review(self.review_path)["pages"][0]
        self.assertEqual(
            refreshed["targetOrPrompt"],
            "Conversation prompt: “What would you do with a free afternoon?” / "
            "“自由な午後があったら、何をしますか？” Tutor follow-ups: "
            "“Would you go out or stay home?” and “Who might join you?”",
        )
        self.assertIn("自由な午後があったら、何をしますか？", refreshed["nonTargetSupport"])
        self.assertNotIn("古い質問", json.dumps(refreshed, ensure_ascii=False))

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

    def test_corpus_audit_requires_a_completed_ledger_for_every_active_lesson(self) -> None:
        reviews = self.root / "reviews"
        reviews.mkdir()
        review = self.completed_review()
        review["lesson"] = str(self.lesson.resolve())
        first = reviews / "first.json"
        first.write_text(json.dumps(review), encoding="utf-8")
        second = self.root / "second" / "lesson.html"
        second.parent.mkdir()
        second.write_text('<section data-page-id="goal"></section>', encoding="utf-8")
        errors = page_review.audit_corpus(self.root, reviews)
        self.assertTrue(any(str(second) in error and "missing hash-bound" in error for error in errors))

    def test_corpus_audit_ignores_superseded_lessons(self) -> None:
        reviews = self.root / "reviews"
        reviews.mkdir()
        review = self.completed_review()
        review["lesson"] = str(self.lesson.resolve())
        (reviews / "first.json").write_text(json.dumps(review), encoding="utf-8")
        old = self.root / "old" / "lesson.html"
        old.parent.mkdir()
        old.write_text(
            '<meta name="podo:curriculum-status" content="superseded">'
            '<section data-page-id="goal"></section>',
            encoding="utf-8",
        )
        self.assertEqual(page_review.audit_corpus(self.root, reviews), [])


if __name__ == "__main__":
    unittest.main()


class AuditClaimsTests(unittest.TestCase):
    """A proofread claim is only as good as the ledger behind it."""

    def build(self, tmp, *, status="complete", with_ledger=True, tamper=False):
        root = pathlib.Path(tmp)
        lesson = root / "tracks/t/courses/c/lessons/01-x/lesson.html"
        lesson.parent.mkdir(parents=True)
        lesson.write_text(
            '<meta name="podo:review-id" content="CORE-1">'
            f'<meta name="podo:proofread-status" content="{status}">'
            '<div data-page-id="lesson-goal"></div>',
            encoding="utf-8",
        )
        reviews = root / "page-reviews"
        reviews.mkdir()
        if with_ledger:
            ledger = page_review.scaffold(lesson, reviews / "CORE-1.page-review.json")
            for page in ledger["pages"]:
                for field in page_review.REQUIRED_PAGE_FIELDS:
                    page[field] = "reviewed in full"
                page["visual360"] = page["visual480"] = "pass"
                page["verdict"] = "pass"
            for stage in page_review.PASS_STAGES:
                ledger.setdefault("stages", {})[stage] = "pass"
            if tamper:
                ledger["lessonSha256"] = "0" * 64
            page_review.write_json(reviews / "CORE-1.page-review.json", ledger)
        return root / "tracks", reviews

    def test_a_backed_claim_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons, reviews = self.build(tmp)
            self.assertEqual(page_review.audit_claims(lessons, reviews), [])

    def test_a_claim_with_no_ledger_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons, reviews = self.build(tmp, with_ledger=False)
            problems = page_review.audit_claims(lessons, reviews)
            self.assertEqual(len(problems), 1)
            self.assertIn("no ledger points at this deck", problems[0])

    def test_a_stale_ledger_does_not_back_the_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons, reviews = self.build(tmp, tamper=True)
            problems = page_review.audit_claims(lessons, reviews)
            self.assertEqual(len(problems), 1)
            self.assertIn("ledger does not pass", problems[0])

    def test_a_deck_that_claims_nothing_is_not_judged(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons, reviews = self.build(tmp, status="pending", with_ledger=False)
            self.assertEqual(page_review.audit_claims(lessons, reviews), [])
