#!/usr/bin/env python3
"""Regression tests for silent deck checks shared by English and Korean."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck


class DeckCheckTests(unittest.TestCase):
    def test_english_deck_rejects_visible_hangul(self):
        with tempfile.TemporaryDirectory() as temporary:
            deck = (
                pathlib.Path(temporary)
                / "sandbox/drafts/en/tracks/1-core-patterns/lessons/01-test/lesson.html"
            )
            deck.parent.mkdir(parents=True)
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<meta name="podo:review-id" content="CORE-1">'
                '<meta name="podo:target-language" content="en">'
                '<body><div data-page-id="lesson-goal">튜터만</div></body>',
                encoding="utf-8",
            )
            errors, _ = check_deck.check(deck)
            self.assertTrue(any("visible Korean text" in error for error in errors))

    def test_meta_content_is_attribute_order_tolerant(self):
        source = (
            '<meta content="notranslate" name="google">'
            '<meta content="07-daily-routine" data-owner="author" '
            'name="podo:lesson-id">'
        )
        self.assertEqual(check_deck.meta_content(source, "google"), "notranslate")
        self.assertEqual(
            check_deck.meta_content(source, "podo:lesson-id"),
            "07-daily-routine",
        )

    def test_sentence_split_ignores_quoted_expression_punctuation(self):
        korean = "제가 ‘도대체 왜 그랬어?’라고 물을게요. 대답해 보세요."
        japanese = "私が「どうしてそうしたの」と聞きます。答えてみてください。"
        self.assertEqual(
            len(check_deck.sentences(korean, check_deck.KO_END, spaced=True)),
            2,
        )
        self.assertEqual(
            len(check_deck.sentences(japanese, check_deck.JA_END, spaced=False)),
            2,
        )

    def test_korean_mixed_reorder_counts_are_review_warnings(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = pathlib.Path(temporary) / "01-test"
            lesson.mkdir()
            deck = lesson / "lesson.html"
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<div data-page-id="p1-reorder">'
                '<div class="task-block"><span class="choice">가</span>'
                '<span class="choice">나</span></div>'
                '<div class="task-block"><span class="choice">가</span>'
                '<span class="choice">나</span><span class="choice">다</span></div>'
                '</div>',
                encoding="utf-8",
            )
            errors, warnings = check_deck.check(deck)
            self.assertEqual(errors, [])
            self.assertTrue(any("mixed chip counts" in item for item in warnings))

    def test_english_three_chip_reorder_requires_explicit_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = pathlib.Path(temporary) / "sandbox/drafts/en" / "tracks" / "1-core-patterns" / "lessons" / "01-test"
            lesson.mkdir(parents=True)
            deck = lesson / "lesson.html"
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<meta name="podo:review-id" content="CORE-1">'
                '<meta name="podo:target-language" content="en">'
                '<div data-page-id="p1-reorder">'
                '<div class="task-block">'
                '<span class="answer-space build-zone" data-sync-id="row" '
                'data-sync-kind="order" data-a="Could you help me?"></span>'
                '<span class="choice">Could you</span>'
                '<span class="choice">help</span>'
                '<span class="choice">me?</span>'
                '</div></div>',
                encoding="utf-8",
            )
            _, warnings = check_deck.check(deck)
            self.assertTrue(any("four is the English working default" in item for item in warnings))

    def test_runtime_promoted_control_shell_is_an_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = pathlib.Path(temporary) / "01-test"
            lesson.mkdir()
            deck = lesson / "lesson.html"
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<span class="slot" data-sync-id="answer">yes</span>',
                encoding="utf-8",
            )
            errors, _ = check_deck.check(deck)
            self.assertTrue(any("runtime-promoted control" in item for item in errors))

    def test_static_control_is_not_reported_as_a_shell(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = pathlib.Path(temporary) / "01-test"
            lesson.mkdir()
            deck = lesson / "lesson.html"
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<input class="slot-input" data-sync-id="answer" data-answer="yes">',
                encoding="utf-8",
            )
            errors, _ = check_deck.check(deck)
            self.assertFalse(any("runtime-promoted control" in item for item in errors))

    def test_reorder_accepts_any_chip_order_without_id_convention(self):
        chunk = (
            '<div data-page-id="p1-reorder">'
            '<div class="task-block">'
            '<span class="answer-space build-zone" data-sync-id="p1-row" '
            'data-sync-kind="order" data-a="Could you help me?"></span>'
            '<span class="choice" data-item-id="arbitrary-a">help</span>'
            '<span class="choice" data-item-id="arbitrary-b">me?</span>'
            '<span class="choice" data-item-id="arbitrary-c">Could you</span>'
            '</div></div>'
        )
        self.assertEqual(
            check_deck.reorder_solvability_errors("p1-reorder", chunk),
            [],
        )

    def test_reorder_rejects_chips_that_cannot_build_answer(self):
        chunk = (
            '<div data-page-id="p1-reorder">'
            '<div class="task-block">'
            '<span class="answer-space build-zone" data-sync-id="p1-row" '
            'data-sync-kind="order" data-a="Could you help me?"></span>'
            '<span class="choice">help</span>'
            '<span class="choice">them?</span>'
            '<span class="choice">Could you</span>'
            '</div></div>'
        )
        errors = check_deck.reorder_solvability_errors("p1-reorder", chunk)
        self.assertTrue(any("cannot reconstruct data-a" in item for item in errors))

    def test_reorder_rejects_punctuation_only_chip(self):
        chunk = (
            '<div data-page-id="p1-reorder"><div class="task-block">'
            '<span class="answer-space build-zone" data-sync-id="row" '
            'data-sync-kind="order" data-a="How often do you exercise?"></span>'
            '<span class="choice">How often</span><span class="choice">do you</span>'
            '<span class="choice">exercise</span><span class="choice">?</span>'
            '</div></div>'
        )
        errors = check_deck.reorder_solvability_errors("p1-reorder", chunk)
        self.assertTrue(any("punctuation-only chip" in item for item in errors))

    def test_reorder_rejects_standalone_article(self):
        chunk = (
            '<div data-page-id="p2-reorder"><div class="task-block">'
            '<span class="answer-space build-zone" data-sync-id="row" '
            'data-sync-kind="order" data-a="About twice a week."></span>'
            '<span class="choice">About</span><span class="choice">twice</span>'
            '<span class="choice">a</span><span class="choice">week.</span>'
            '</div></div>'
        )
        errors = check_deck.reorder_solvability_errors("p2-reorder", chunk)
        self.assertTrue(any("bound-word chip 'a'" in item for item in errors))

    def test_reorder_accepts_preposition_when_placement_is_the_learning_operation(self):
        chunk = (
            '<div data-page-id="p1-reorder"><div class="task-block">'
            '<span class="answer-space build-zone" data-sync-id="row" '
            'data-sync-kind="order" data-a="I start work at nine."></span>'
            '<span class="choice">I</span><span class="choice">start work</span>'
            '<span class="choice">at</span><span class="choice">nine.</span>'
            '</div></div>'
        )
        self.assertEqual(
            check_deck.reorder_solvability_errors("p1-reorder", chunk),
            [],
        )

    def test_core_shape_rejects_hollow_teaching_and_native_tip_pages(self):
        pages = {
            "lesson-goal": '<p class="section-subtitle"></p>',
            "p1-teach": '<div class="model-list"></div>',
            "p1-rule": '<p>Put at before a time.</p>',
            "p2-teach": '<div class="model-list"></div>',
            "p2-rule": '<p>Put usually before the action.</p>',
            "native-tip": '<h2>Two useful extras</h2><p>使える表現</p>',
        }
        errors = check_deck.core_canonical_shape_issues(pages)
        self.assertTrue(any("missing canonical pages" in item for item in errors))
        self.assertTrue(any("main pattern block" in item for item in errors))
        self.assertTrue(any("formation diagram" in item for item in errors))
        self.assertTrue(any("not a native tip" in item for item in errors))

    def test_pilot_goal_rejects_preview_rows(self):
        errors = check_deck.pilot_operating_issues(
            {
                "lesson-goal": (
                    '<p class="section-subtitle"><span class="ko">Please read the title aloud.</span>'
                    '<span class="ja">タイトルを声に出して読んでください。</span></p>'
                    '<div class="known-row"></div>'
                )
            },
            track="core",
        )
        self.assertTrue(any("remove example/outcome rows" in item for item in errors))

    def test_pilot_activity_scripts_and_feedback_are_accepted(self):
        pages = {
            "lesson-goal": (
                '<p class="section-subtitle"><span class="ko">Practice asking for help. '
                'Please read the title aloud.</span><span class="ja">手伝いを頼む練習をします。'
                'タイトルを声に出して読んでください。</span></p>'
            ),
            "p1-reorder": (
                '<p class="section-subtitle"><span class="ko">'
                f'{check_deck.REORDER_SCRIPT_EN}</span><span class="ja">'
                f'{check_deck.REORDER_SCRIPT_JA}</span></p>'
            ),
            "p1-fill": (
                '<p class="section-subtitle"><span class="ko">Say each whole sentence aloud, '
                'including the missing words.</span><span class="ja">空欄を含めて言ってください。</span></p>'
                '<div class="tutor-note">Type only the missing words exactly as the learner says them.</div>'
            ),
            "p1-translate": (
                '<p class="section-subtitle"><span class="ko">'
                f'{check_deck.TRANSLATE_SCRIPT_EN}</span><span class="ja">'
                f'{check_deck.TRANSLATE_SCRIPT_JA}</span></p>'
                '<div class="tutor-note">Type the learner\'s complete English sentence exactly as they say it.</div>'
            ),
            "p1-write": (
                '<p class="section-subtitle"><span class="ko">Now use “Could you help '
                'me with ___?” to ask me for help.</span><span class="ja">手伝いを頼んで'
                'ください。</span></p>'
                '<div class="tutor-note">Have the learner answer aloud before you capture it.</div>'
                '<div class="fb" data-fb="answer" '
                'data-fb-spoken-label="Student\'s sentence"></div>'
            ),
        }
        self.assertEqual(
            check_deck.pilot_operating_issues(pages, track="core"),
            [],
        )

    def test_pilot_goal_requires_a_useful_can_do_before_title_action(self):
        errors = check_deck.pilot_operating_issues(
            {
                "lesson-goal": (
                    '<p class="section-subtitle"><span class="ko">Please read the title aloud.</span>'
                    '<span class="ja">タイトルを声に出して読んでください。</span></p>'
                )
            },
            track="core",
        )
        self.assertTrue(any("useful can-do" in item for item in errors))

    def test_pilot_reading_and_listening_pages_assign_the_voice_explicitly(self):
        accepted = {
            "p1-read": (
                '<p class="section-subtitle"><span class="ko">Read each sentence aloud.</span>'
                '<span class="ja">一文ずつ声に出してください。</span></p>'
            ),
            "understand": (
                '<p class="section-subtitle"><span class="ko">I\'ll read each agent line. '
                'Choose what it means.</span><span class="ja">意味を選んでください。</span></p>'
            ),
        }
        self.assertEqual(
            check_deck.pilot_operating_issues(accepted, track="contextual"), []
        )

        rejected = {
            "p1-read": (
                '<p class="section-subtitle"><span class="ko">I\'ll read each sentence.</span>'
                '<span class="ja">聞いてください。</span></p>'
            ),
            "understand": (
                '<p class="section-subtitle"><span class="ko">Choose what it means.</span>'
                '<span class="ja">意味を選んでください。</span></p>'
            ),
        }
        errors = check_deck.pilot_operating_issues(rejected, track="contextual")
        self.assertTrue(any("learner reading is the default" in item for item in errors))
        self.assertTrue(any("tutor reads each English line" in item for item in errors))

    def test_pilot_contextual_scene_requires_short_explicit_roles(self):
        good = {
            "scene": (
                '<p class="section-subtitle"><span class="ko">Let\'s role-play. '
                'You\'re the passenger, and I\'ll be the agent.</span>'
                '<span class="ja">あなたは乗客で、私は係員です。</span></p>'
            )
        }
        self.assertEqual(
            check_deck.pilot_operating_issues(good, track="contextual"), []
        )
        vague = {
            "scene": (
                '<p class="section-subtitle"><span class="ko">Let\'s begin the scene.</span>'
                '<span class="ja">始めましょう。</span></p>'
            )
        }
        errors = check_deck.pilot_operating_issues(vague, track="contextual")
        self.assertTrue(any("name the learner's role" in item for item in errors))

    def test_pilot_feedback_rejects_duplicate_task_and_old_label(self):
        errors = check_deck.pilot_operating_issues(
            {
                "p1-write": (
                    '<div class="fb" data-fb="answer">'
                    '<div class="fb-task">もう一度やってみよう</div></div>'
                )
            },
            track="core",
        )
        self.assertTrue(any("repeated task" in item for item in errors))
        self.assertTrue(any("Student's sentence" in item for item in errors))

    def test_pilot_open_sentence_requires_shared_feedback_capture(self):
        errors = check_deck.pilot_operating_issues(
            {
                "p1-write": (
                    '<div class="task-block"><div class="answer-box">'
                    '<span class="answer-label">Your sentence</span></div></div>'
                )
            },
            track="core",
        )
        self.assertTrue(any("shared feedback component" in item for item in errors))

    def test_pilot_open_sentence_rejects_generic_make_your_own_sentence_copy(self):
        errors = check_deck.pilot_operating_issues(
            {
                "p1-write": (
                    '<p class="section-subtitle"><span class="ko">'
                    'Now use “I’m here for ___” to make your own sentence.</span>'
                    '<span class="ja">旅行の目的を伝えましょう。</span></p>'
                    '<div class="fb" data-fb="answer" '
                    'data-fb-spoken-label="Student\'s sentence"></div>'
                )
            },
            track="contextual",
        )
        self.assertTrue(any("communicative job" in item for item in errors))

    def test_pilot_open_production_requires_visible_frame_job_and_spoken_capture(self):
        errors = check_deck.pilot_operating_issues(
            {
                "p1-write": (
                    '<p class="section-subtitle"><span class="ko">Make one request.</span>'
                    '<span class="ja">依頼を作りましょう。</span></p>'
                    '<div class="tutor-note">Write the answer.</div>'
                    '<div class="fb" data-fb="answer" '
                    'data-fb-spoken-label="Student\'s sentence"></div>'
                )
            },
            track="core",
        )
        self.assertTrue(any("exact target frame" in item for item in errors))
        self.assertTrue(any("answer aloud" in item for item in errors))

    def test_core_shape_rejects_unjustified_full_sentence_choices(self):
        errors = check_deck.core_canonical_shape_issues(
            {
                "p1-choose": (
                    '<div class="choose-list"><div class="choose-row sentence">'
                    '<span class="opt">I start work at eight.</span>'
                    '<span class="opt">I start work at ten.</span>'
                    '</div></div>'
                )
            }
        )
        self.assertTrue(any("smallest meaningful unit" in item for item in errors))

    def test_core_shape_allows_explicit_whole_sentence_contrast(self):
        errors = check_deck.core_canonical_shape_issues(
            {
                "p1-choose": (
                    '<div class="choose-list" data-choice-scope="whole-sentence">'
                    '<div class="choose-row sentence"></div></div>'
                )
            }
        )
        self.assertFalse(any("p1-choose: choose at" in item for item in errors))

    def test_compact_word_choice_rejects_sentence_sized_options(self):
        pages = {
            "p1-choose": (
                '<div class="word-choice-list">'
                '<span class="opt">I start work at eight.</span>'
                '<span class="opt">I start work at ten.</span>'
                '</div>'
            )
        }
        errors = check_deck.smallest_unit_choice_issues(pages)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("sentence-sized" in item for item in errors))

    def test_compact_word_choice_accepts_local_units(self):
        pages = {
            "p1-choose": (
                '<div class="word-choice-list">'
                '<span class="word-choice-sentence">I start work at '
                '<span class="opt">eight</span><span class="opt">ten</span>.</span></div>'
            )
        }
        self.assertEqual(check_deck.smallest_unit_choice_issues(pages), [])

    def test_phrase_input_requires_spaced_answer_component(self):
        errors = check_deck.phrase_input_structure_issues(
            '<div class="bubble"><span class="korean">'
            '<input class="phrase-input"></span></div>'
        )
        self.assertTrue(any("canonical answer-box" in item for item in errors))
        self.assertEqual(
            check_deck.phrase_input_structure_issues(
                '<div class="answer-box"><span class="answer-fill">'
                '<span class="korean"><input class="phrase-input"></span>'
                '</span></div>'
            ),
            [],
        )

    def test_english_deck_rejects_unstyled_model_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            deck = pathlib.Path(temporary) / "sandbox/drafts/en/tracks/1-core-patterns/lesson.html"
            deck.parent.mkdir(parents=True)
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="lesson">'
                '<meta name="podo:review-id" content="CORE-1">'
                '<meta name="podo:target-language" content="en">'
                '<div data-page-id="p1-teach"><div class="model-lines"></div></div>',
                encoding="utf-8",
            )
            errors, _ = check_deck.check(deck)
            self.assertTrue(any("unstyled .model-lines" in item for item in errors))

    def test_freetalking_article_accepts_twelve_rows_with_exact_gloss_parity(self):
        script = (
            '<p class="section-subtitle"><span class="ko">'
            'Did you have any questions about the article?'
            '</span><span class="ja">記事について何か質問はありましたか？</span></p>'
        )
        row = (
            '<div class="sent"><span class="s-key">curiosity</span>'
            '<span class="s-w"><b>curiosity</b>好奇心</span></div>'
        )
        errors, warnings = check_deck.article_structure_issues(script + row * 12)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_freetalking_article_rejects_short_article_and_mismatched_glosses(self):
        script = (
            '<p class="section-subtitle"><span class="ko">'
            'Did you have any questions about the article?'
            '</span><span class="ja">記事について何か質問はありましたか？</span></p>'
        )
        matched = (
            '<div class="sent"><span class="s-key">curiosity</span>'
            '<span class="s-w"><b>curiosity</b>好奇心</span></div>'
        )
        mismatched = '<div class="sent"><span class="s-key">curiosity</span></div>'
        errors, _ = check_deck.article_structure_issues(script + matched * 6 + mismatched)
        self.assertTrue(any("7 sentence rows" in item for item in errors))
        self.assertTrue(any("1 highlighted item(s) but 0 gloss(es)" in item for item in errors))

    def test_freetalking_article_rejects_in_class_reading_coaching(self):
        script = (
            '<p class="section-subtitle"><span class="ko">'
            'Did you read the article? If not, skim it now.'
            '</span><span class="ja">記事を読みましたか？ まだなら今読んでください。</span></p>'
        )
        rows = '<div class="sent"></div>' * 12
        errors, _ = check_deck.article_structure_issues(script + rows)
        self.assertTrue(any("one question" in item for item in errors))
        self.assertTrue(any("must ask whether the learner has questions" in item for item in errors))
        self.assertTrue(any("coaches page use or in-class reading" in item for item in errors))

    def test_freetalking_question_note_accepts_followups_only(self):
        chunk = (
            '<div class="tutor-note"><div class="tn-body">'
            '<span class="tn-cap">Follow up</span><ul class="tn-more">'
            '<li>What happened next?</li><li>How did you react?</li>'
            '</ul></div></div><div class="fb"></div>'
        )
        self.assertEqual(check_deck.freetalk_question_note_issues("q1", chunk), [])

    def test_freetalking_question_note_rejects_coaching_preamble(self):
        chunk = (
            '<div class="tutor-note"><div class="tn-body">Build the story in short steps.'
            '<span class="tn-cap">Follow up</span><ul class="tn-more">'
            '<li>What happened next?</li><li>How did you react?</li>'
            '</ul></div></div><div class="fb"></div>'
        )
        errors = check_deck.freetalk_question_note_issues("q1", chunk)
        self.assertTrue(any("has coaching before the follow-ups" in item for item in errors))

    def test_freetalking_question_note_rejects_nonquestion_and_duplicate(self):
        chunk = (
            '<p class="section-subtitle ask"><span class="ko">What changed?</span>'
            '<span class="ja">何が変わりましたか？</span></p>'
            '<div class="tutor-note"><div class="tn-body">'
            '<span class="tn-cap">Follow up</span><ul class="tn-more">'
            '<li>Give one example.</li><li>Why did it change?</li>'
            '<li>Why did it change?</li></ul></div></div><div class="fb"></div>'
        )
        errors = check_deck.freetalk_question_note_issues("q2", chunk)
        self.assertTrue(any("is not a question" in item for item in errors))
        self.assertTrue(any("duplicate follow-up" in item for item in errors))

    def test_freetalking_question_note_rejects_repeated_main_question(self):
        chunk = (
            '<p class="section-subtitle ask"><span class="ko">What changed?</span>'
            '<span class="ja">何が変わりましたか？</span></p>'
            '<div class="tutor-note"><div class="tn-body">'
            '<span class="tn-cap">Follow up</span><ul class="tn-more">'
            '<li>What changed?</li><li>Why did it change?</li>'
            '</ul></div></div><div class="fb"></div>'
        )
        errors = check_deck.freetalk_question_note_issues("q2", chunk)
        self.assertTrue(any("repeats the printed question" in item for item in errors))

    def test_freetalking_conversation_requires_reciprocal_pool_intro(self):
        pages = {
            "talk-intro": (
                '<p class="section-subtitle"><span class="ko">Let\'s answer all eight.</span>'
                '<span class="ja">全部答えましょう。</span></p>'
                '<div class="tutor-note">Ask each question in order.</div>'
            )
        }
        errors = check_deck.freetalk_conversation_issues(pages)
        self.assertTrue(any("flexible question pool" in item for item in errors))

    def test_freetalking_conversation_rejects_duplicate_pages_and_double_prompt(self):
        question = (
            '<p class="section-subtitle ask"><span class="ko">What changed? Why?</span>'
            '<span class="ja">何が変わりましたか？ なぜですか？</span></p>'
            '<div class="tutor-note"><ul><li>What happened next?</li>'
            '<li>Who noticed?</li></ul></div>'
        )
        errors = check_deck.freetalk_conversation_issues({"q1": question, "q2": question})
        self.assertTrue(any("contains 2 questions" in item for item in errors))
        self.assertTrue(any("repeats the main prompt" in item for item in errors))
        self.assertTrue(any("repeats the complete follow-up set" in item for item in errors))

    def test_freetalking_conversation_accepts_distinct_pool_pages(self):
        intro = (
            '<p class="section-subtitle"><span class="ko">We do not need to answer every '
            'question. Let\'s follow the most interesting parts.</span>'
            '<span class="ja">全部答えなくても大丈夫です。</span></p>'
            '<div class="tutor-note">React or share briefly, and skip freely.</div>'
        )
        q1 = (
            '<p class="section-subtitle ask"><span class="ko">What changed?</span>'
            '<span class="ja">何が変わりましたか？</span></p>'
            '<div class="tutor-note"><ul><li>What happened next?</li></ul></div>'
        )
        q2 = (
            '<p class="section-subtitle ask"><span class="ko">Who noticed first?</span>'
            '<span class="ja">誰が最初に気づきましたか？</span></p>'
            '<div class="tutor-note"><ul><li>What did they say?</li></ul></div>'
        )
        self.assertEqual(
            check_deck.freetalk_conversation_issues(
                {"talk-intro": intro, "q1": q1, "q2": q2}
            ),
            [],
        )

    def test_english_tutor_notes_reject_japanese_or_korean(self):
        source = (
            '<div class="tutor-note">Answer questions, then move on.</div>'
            '<div class="tutor-note">質問に答えてください。</div>'
            '<ul class="opt-note"><li>질문에 답해 주세요.</li></ul>'
        )
        errors = check_deck.freetalk_tutor_language_issues(source)
        self.assertEqual(len(errors), 2)

    def test_pattern_meaning_requires_one_sentence_per_language(self):
        chunk = (
            '<p class="section-subtitle pattern-meaning">'
            '<span class="ko">Use this to ask politely. Read it with me.</span>'
            '<span class="ja">ていねいに頼むときに使います。一緒に読みましょう。</span>'
            '</p>'
        )
        errors = check_deck.pattern_meaning_issues("p1-teach", chunk)
        self.assertTrue(any("one concise sentence" in item for item in errors))

    def test_pattern_meaning_accepts_one_concise_pair(self):
        chunk = (
            '<p class="section-subtitle pattern-meaning">'
            '<span class="ko">Use this when you want to ask for help politely.</span>'
            '<span class="ja">ていねいに手伝いを頼むときに使います。</span>'
            '</p>'
        )
        self.assertEqual(check_deck.pattern_meaning_issues("p1-teach", chunk), [])

    def test_pattern_meaning_rejects_embedded_activity_instruction(self):
        chunk = (
            '<p class="section-subtitle pattern-meaning">'
            '<span class="ko">Use this to ask politely and read each example aloud.</span>'
            '<span class="ja">丁寧に頼む表現なので、例文を読んでください。</span>'
            '</p>'
        )
        errors = check_deck.pattern_meaning_issues("p1-teach", chunk)
        self.assertTrue(any("mixes teaching copy" in item for item in errors))

    def test_core_production_accepts_profiled_roleplay_and_reciprocal_freetalk(self):
        image = '<img class="avatar" src="person.jpg" alt="">'
        model = (
            f'<div class="turn other"><span class="who">{image}</span>'
            '<span class="ending">Could you help?</span></div>'
            f'<div class="turn me"><span class="who">{image}</span></div>'
            f'<div class="turn other"><span class="who">{image}</span></div>'
            f'<div class="turn me"><span class="who">{image}</span></div>'
            f'<div class="turn other"><span class="who">{image}</span></div>'
        )
        complete = (
            f'<div class="turn other"><span class="who">{image}</span></div>'
            f'<div class="turn me"><span class="who">{image}</span>'
            '<span class="target">手伝ってもらえますか</span>'
            '<textarea class="free-input phrase-input"></textarea></div>'
            f'<div class="turn other"><span class="who">{image}</span></div>'
            f'<div class="turn me"><span class="who">{image}</span></div>'
            f'<div class="turn other"><span class="who">{image}</span></div>'
        )
        live = (
            '<div class="turn other"><span class="who"><span class="avatar icon">T</span></span>'
            '<span class="korean">What do you need?</span></div>'
            '<div class="turn me"><span class="who"><span class="avatar icon">私</span></span>'
            '<span class="korean">What do you need help with?</span></div>'
            '<div class="turn other"><span class="who"><span class="avatar icon">T</span></span>'
            '<span>Tutor\'s answer</span></div>'
        )
        self.assertEqual(
            check_deck.core_production_issues(
                {"p3-model": model, "p3-complete": complete, "p3-freetalk": live}
            ),
            [],
        )

    def test_core_production_rejects_roleplay_icons_dropped_turns_and_generic_prompts(self):
        icon_turn = '<div class="turn other"><span class="who"><span class="avatar icon">T</span></span></div>'
        errors = check_deck.core_production_issues(
            {
                "p3-model": icon_turn * 2,
                "p3-complete": icon_turn,
                "p3-freetalk": '<div class="turn me">Use both patterns. Ask the tutor.</div>',
            }
        )
        self.assertTrue(any("profile images" in item for item in errors))
        self.assertTrue(any("5–7-turn exchange" in item for item in errors))
        self.assertTrue(any("turn count differs" in item for item in errors))
        self.assertTrue(any("speaker labels" in item for item in errors))
        self.assertTrue(any("generic production instruction" in item for item in errors))

    def test_core_production_rejects_one_way_freetalk_capture(self):
        errors = check_deck.core_production_issues({
            "p3-freetalk": '<div class="fb" data-fb="one-way"></div>',
        })
        self.assertTrue(any("reciprocal Tutor/Me exchange" in item for item in errors))

    def test_core_freetalk_rejects_forced_frame_or_missing_ask_back(self):
        icon = '<span class="who"><span class="avatar icon">T</span></span>'
        me = '<span class="who"><span class="avatar icon">私</span></span>'
        live = (
            f'<div class="turn other">{icon}<span class="korean">Using today\'s pattern, '
            'what would you say?</span></div>'
            f'<div class="turn me">{me}<textarea></textarea></div>'
            f'<div class="turn other">{icon}<span>Tutor\'s answer</span></div>'
        )
        errors = check_deck.core_production_issues({"p3-freetalk": live})
        self.assertTrue(any("disguised pattern production" in item for item in errors))
        self.assertTrue(any("ask-back" in item for item in errors))
        self.assertTrue(any("do not force today's frame" in item for item in errors))

    def test_contextual_freetalk_rejects_imperative_or_roleplay_production(self):
        icon = '<span class="who"><span class="avatar icon">T</span></span>'
        learner_icon = '<span class="who"><span class="avatar icon">私</span></span>'
        tutor_answer = (
            f'<div class="turn other">{icon}'
            '<textarea class="free-input">Tutor\'s answer</textarea></div>'
        )
        for first in (
            "Report the missing bag and describe one clear feature.",
            "What would you say to reception?",
        ):
            live = (
                f'<div class="turn other">{icon}<span class="korean">{first}</span></div>'
                f'<div class="turn me">{learner_icon}<textarea></textarea></div>'
                '<div class="turn me"><span class="who"><span class="avatar icon">私</span></span>'
                '<span class="korean">What would you prefer?</span></div>'
                + tutor_answer
            )
            with self.subTest(first=first):
                errors = check_deck.contextual_production_issues(
                    {"p3-freetalk": live}, enforce_frame_boundaries=False
                )
                self.assertTrue(any("roleplay" in item or "actual relevant question" in item for item in errors))

    def test_contextual_freetalk_accepts_relevant_reciprocal_question(self):
        other = '<span class="who"><span class="avatar icon">T</span></span>'
        me = '<span class="who"><span class="avatar icon">私</span></span>'
        live = (
            f'<div class="turn other">{other}<span class="korean">Which hotel problem bothers you most, and why?</span></div>'
            f'<div class="turn me">{me}<textarea></textarea></div>'
            f'<div class="turn me">{me}<span class="korean">Which problem bothers you most?</span></div>'
            f'<div class="turn other">{other}<textarea>Tutor\'s answer</textarea></div>'
        )
        self.assertEqual(
            check_deck.contextual_production_issues(
                {"p3-freetalk": live}, enforce_frame_boundaries=False
            ),
            [],
        )

    def test_core_late_phrase_inputs_reuse_only_controlled_targets(self):
        pages = {
            "p1-fill": '<input class="slot-input" data-answer="went">',
            "p2-fill": '<input class="slot-input" data-answer="had">',
            "p3-complete": (
                '<span class="target">行って</span>'
                '<textarea class="free-input phrase-input" data-answer="went"></textarea>'
            ),
            "in-the-wild": (
                '<span class="target">食べました</span>'
                '<textarea class="free-input phrase-input" '
                'data-answer="had dinner"></textarea>'
            ),
        }
        errors = check_deck.core_production_issues(pages)
        self.assertFalse(any("p3-complete: phrase input" in item for item in errors))
        self.assertTrue(any("in-the-wild: phrase input" in item for item in errors))

    def test_partner_turns_ignore_compact_learner_lines(self):
        source = (
            '<div class="turn other"><span class="korean">Question</span>\n'
            '<span class="translation">質問</span></div>'
            '<div class="turn me"><span class="korean">Answer</span>'
            '<span class="translation">答え</span></div>'
            '<div class="turn other"><span class="korean">Follow-up</span>\n'
            '<span class="translation">追加質問</span></div>'
        )
        self.assertEqual(check_deck.partner_turns(source), ["Question", "Follow-up"])

    def test_target_highlights_require_a_mirrored_pair_on_every_model_row(self):
        pages = {
            "p1-read": (
                '<div class="model-line"><span class="korean">Could we '
                '<span class="ending">have</span> a seat?</span>'
                '<span class="translation">席をいただけますか？</span></div>'
            )
        }
        errors = check_deck.target_highlight_issues(pages)
        self.assertTrue(any("mirrored target highlights differ" in item for item in errors))

    def test_target_highlights_accept_models_fills_and_word_choices(self):
        pages = {
            "p1-read": (
                '<span class="korean"><span class="ending">Could we have</span> a seat?</span>'
                '<span class="translation">席を<span class="ending">いただけますか</span>？</span>'
            ),
            "p1-fill": (
                '<span class="answer-label">席を<span class="target ending">いただけますか</span>？</span>'
                '<input class="slot-input" data-answer="Could we have">'
            ),
            "p1-choose": (
                '<div class="word-choice-list"><div class="word-choice-card">'
                '<span class="translation"><span class="ending">安い</span></span>'
                '<span class="choose-row word-choice"><span class="opt">cheaper</span></span>'
                '</div></div>'
            ),
        }
        self.assertEqual(check_deck.target_highlight_issues(pages), [])

    def test_controlled_fill_rejects_lexical_blanks_when_do_you_is_taught(self):
        pages = {
            "p1-read": (
                '<span class="korean"><span class="ending">Do you</span> drink coffee?</span>'
                '<span class="translation">コーヒーを<span class="ending">飲みますか</span>？</span>'
            ),
            "p1-fill": (
                '<div class="task-block"><span class="answer-label">コーヒーを'
                '<span class="target ending">飲みますか</span>？</span>'
                '<input class="slot-input" data-answer="drink"></div>'
            ),
        }
        errors = check_deck.controlled_target_alignment_issues(pages)
        self.assertTrue(any("blank answers ('drink',)" in item for item in errors))

    def test_controlled_fill_accepts_exact_taught_frame(self):
        pages = {
            "p1-read": (
                '<span class="korean"><span class="ending">I\'m here for</span> work.</span>'
                '<span class="translation"><span class="ending">仕事で来ました</span>。</span>'
            ),
            "p1-fill": (
                '<div class="task-block"><span class="answer-label">'
                '<span class="target ending">仕事で来ました</span>。</span>'
                '<input class="slot-input" data-answer="I\'m here for"></div>'
            ),
        }
        self.assertEqual(check_deck.controlled_target_alignment_issues(pages), [])

    def test_controlled_fill_accepts_one_of_multiple_taught_target_segments(self):
        pages = {
            "p1-read": (
                '<span class="korean"><span class="ending">We’d like</span> two seats, '
                '<span class="ending">if possible.</span></span>'
                '<span class="translation"><span class="ending">できれば</span>、2席を'
                '<span class="ending">希望します</span>。</span>'
            ),
            "p1-fill": (
                '<div class="task-block"><span class="answer-label">2席を'
                '<span class="target ending">希望します</span>。</span>'
                '<input class="slot-input" data-answer="We\'d like"></div>'
            ),
        }
        self.assertEqual(check_deck.controlled_target_alignment_issues(pages), [])

    def test_controlled_fill_requires_one_japanese_cue_per_blank(self):
        pages = {
            "p1-read": (
                '<span class="korean"><span class="ending">Do you</span> cook?</span>'
                '<span class="translation"><span class="ending">料理しますか</span>？</span>'
            ),
            "p1-fill": (
                '<div class="task-block"><span class="answer-label">料理しますか？</span>'
                '<input class="slot-input" data-answer="Do you"></div>'
            ),
        }
        errors = check_deck.controlled_target_alignment_issues(pages)
        self.assertTrue(any("Japanese target cue count" in item for item in errors))

    def test_target_v2_supported_translation_requires_lexical_hints(self):
        pages = {
            "p1-translate": (
                '<div data-scaffolding-contract="target-v2" '
                'data-support-stage="supported">'
                '<div class="task-block"><input class="space-input" '
                'data-answer="I\'m here for a holiday."></div></div>'
            )
        }
        errors = check_deck.translation_support_issues(pages)
        self.assertTrue(any("needs at least one useful lexical hint" in item for item in errors))

    def test_translation_production_rejects_unmarked_legacy_support(self):
        pages = {
            "p1-translate": (
                '<div><div class="task-block"><input class="space-input" '
                'data-answer="I\'m here for a holiday."></div></div>'
            )
        }
        errors = check_deck.translation_support_issues(pages)
        self.assertTrue(any("must declare" in item for item in errors))

    def test_supported_translation_allows_known_rows_without_redundant_hints(self):
        pages = {
            "p1-translate": (
                '<div data-scaffolding-contract="target-v2" '
                'data-support-stage="supported">'
                '<div class="task-block"><span class="hint-chip">休暇:holiday</span></div>'
                '<div class="task-block"><input class="space-input" '
                'data-answer="I\'m here for work."></div></div>'
            )
        }
        self.assertEqual(check_deck.translation_support_issues(pages), [])

    def test_target_v2_rejects_article_and_auxiliary_hints(self):
        pages = {
            "p1-translate": (
                '<div data-scaffolding-contract="target-v2" '
                'data-support-stage="supported"><div class="task-block">'
                '<span class="hint"><span class="hint-chip">一つ:a</span>'
                '<span class="hint-chip">休暇:holiday</span></span></div></div>'
            )
        }
        errors = check_deck.translation_support_issues(pages)
        self.assertTrue(any("non-lexical hint" in item for item in errors))

    def test_word_choice_requires_more_than_one_correct_branch(self):
        pages = {
            "p1-choose": (
                '<div class="word-choice-list">'
                '<span class="opt" data-correct>a</span><span class="opt">an</span>'
                '<span class="opt" data-correct>a</span><span class="opt">an</span>'
                '</div>'
            )
        }
        errors = check_deck.choice_branch_coverage_issues(pages)
        self.assertTrue(any("every row has the same correct branch" in item for item in errors))

    def test_word_choice_accepts_both_branches_being_meaningful(self):
        pages = {
            "p1-choose": (
                '<div class="word-choice-list">'
                '<span class="opt" data-correct>a</span><span class="opt">an</span>'
                '<span class="opt">a</span><span class="opt" data-correct>an</span>'
                '</div>'
            )
        }
        self.assertEqual(check_deck.choice_branch_coverage_issues(pages), [])

    @staticmethod
    def _choose_page(slots, *, container="choose-list", options=("이", "가")):
        """Build a two-option choose page whose correct slot follows `slots`."""
        rows = ""
        for index, slot in enumerate(slots):
            pair = ""
            for position, word in enumerate(options):
                mark = " data-correct" if position == slot else ""
                pair += (
                    f'<span class="opt" data-sync-option="{word}"{mark}>{word}</span>'
                )
            rows += (
                f'<div class="choose-row sentence" data-sync-id="row-{index}" '
                f'data-sync-kind="selection" data-sync-state="chosen">'
                f'<span class="choose-opts">{pair}</span></div>'
            )
        return {"p1-choose": f'<div class="{container}">{rows}</div>'}

    def test_korean_choose_list_is_read_for_branch_coverage(self):
        errors = check_deck.choice_branch_coverage_issues(self._choose_page([0, 0, 0]))
        self.assertTrue(
            any("every row has the same correct branch" in item for item in errors)
        )

    def test_korean_choose_list_accepts_both_branches_being_meaningful(self):
        self.assertEqual(
            check_deck.choice_branch_coverage_issues(self._choose_page([0, 1, 0])), []
        )

    def test_choice_position_rejects_a_constant_slot(self):
        errors = check_deck.choice_position_issues(self._choose_page([0, 0, 0, 0]))
        self.assertTrue(
            any("on the left in every row (left left left left)" in item
                for item in errors)
        )

    def test_choice_position_rejects_strict_alternation_the_branch_rule_allows(self):
        pages = self._choose_page([1, 0, 1, 0])
        # Both branches are exercised, so the branch rule is satisfied; the
        # answer is still readable off the position alone.
        self.assertEqual(check_deck.choice_branch_coverage_issues(pages), [])
        errors = check_deck.choice_position_issues(pages)
        self.assertTrue(
            any("alternates slot on every row (right left right left)" in item
                for item in errors)
        )

    def test_choice_position_accepts_an_irregular_sequence(self):
        self.assertEqual(
            check_deck.choice_position_issues(self._choose_page([0, 0, 1, 0])), []
        )

    def test_choice_position_reads_the_english_container_too(self):
        errors = check_deck.choice_position_issues(
            self._choose_page([0, 1, 0], container="word-choice-list",
                              options=("a", "an"))
        )
        self.assertTrue(any("alternates slot" in item for item in errors))

    def test_choice_position_declines_short_and_uneven_pages(self):
        self.assertEqual(
            check_deck.choice_position_issues(self._choose_page([0, 0])), []
        )
        uneven = self._choose_page([0, 0, 0])
        uneven["p1-choose"] = uneven["p1-choose"].replace(
            '<span class="choose-opts">',
            '<span class="choose-opts"><span class="opt">또</span>', 1
        )
        self.assertEqual(check_deck.choice_position_issues(uneven), [])

    def test_korean_pattern_deck_runs_the_variation_gates(self):
        with tempfile.TemporaryDirectory() as temporary:
            deck = (
                pathlib.Path(temporary)
                / "sandbox/drafts/kr/tracks/2-core-patterns/courses/core-beginner-1"
                / "lessons/01-test/lesson.html"
            )
            deck.parent.mkdir(parents=True)
            rows = "".join(
                f'<div class="model-line"><span class="korean">저는 {noun}'
                f'<span class="ending">이에요</span>.</span>'
                f'<span class="translation">私は{noun}です。</span></div>'
                for noun in ("학생", "회사원", "선생님")
            )
            choose = self._choose_page([0, 0, 0, 0])["p1-choose"]
            deck.write_text(
                '<meta name="google" content="notranslate">'
                '<meta name="podo:lesson-id" content="01-test">'
                '<meta name="podo:level" content="초급">'
                '<body>'
                '<div class="section" data-page-id="p1-read">'
                f'<div class="model-list">{rows}</div></div>'
                f'<div class="section" data-page-id="p1-choose">{choose}</div>'
                '</body>',
                encoding="utf-8",
            )
            errors, _ = check_deck.check(deck)
            self.assertTrue(any("differ in one word only" in item for item in errors))
            self.assertTrue(any("in every row" in item for item in errors))
            self.assertTrue(
                any("same correct branch" in item for item in errors)
            )

    @staticmethod
    def _read_page(*sentences):
        lines = "".join(
            f'<div class="model-line"><span class="korean">'
            f'<span class="ending">{s.split()[0]}</span> {" ".join(s.split()[1:])}'
            f'</span><span class="translation">訳</span></div>'
            for s in sentences
        )
        return {"p1-read": f'<div class="model-list">{lines}</div>'}

    def test_exemplar_set_rejects_a_single_word_substitution(self):
        pages = self._read_page(
            "Can you drive?", "Can you swim?", "Can you cook?", "Can you ski?"
        )
        errors = check_deck.exemplar_variation_issues(pages, level="A1")
        self.assertTrue(any("differ in one word only" in item for item in errors))

    def test_exemplar_set_accepts_a_varying_form(self):
        pages = self._read_page(
            "She works downtown.",
            "He lives nearby.",
            "They study at night.",
            "I cook at home.",
        )
        self.assertEqual(check_deck.exemplar_variation_issues(pages, level="A1"), [])

    def test_exemplar_set_exempts_pre_a1_formulaic_practice(self):
        pages = self._read_page(
            "Hi, I'm Mina.", "Hi, I'm Ken.", "Hi, I'm Yuki.", "Hi, I'm Emi."
        )
        self.assertEqual(check_deck.exemplar_variation_issues(pages, level="Pre-A1"), [])
        self.assertTrue(check_deck.exemplar_variation_issues(pages, level="A1"))

    def test_exemplar_set_exempts_the_korean_pre_generative_band(self):
        pages = self._read_page("저는 학생이에요.", "저는 의사예요.", "저는 가수예요.")
        self.assertEqual(check_deck.exemplar_variation_issues(pages, level="왕초급"), [])
        self.assertTrue(check_deck.exemplar_variation_issues(pages, level="초급"))

    def test_exemplar_set_ignores_a_taught_page_and_short_sets(self):
        varied = self._read_page("It's cold.", "It's very cold today.")
        self.assertEqual(check_deck.exemplar_variation_issues(varied, level="A1"), [])
        teach = {
            "p1-teach": self._read_page("a", "b", "c", "d")["p1-read"],
        }
        self.assertEqual(check_deck.exemplar_variation_issues(teach, level="A1"), [])

    def test_exemplar_varying_regions_strips_shared_prefix_and_suffix(self):
        self.assertEqual(
            check_deck.exemplar_varying_regions(
                ["I start work at nine.", "I start work at eleven."]
            ),
            [["nine"], ["eleven"]],
        )

    def test_contextual_rejects_japanese_only_receptive_choices_and_roleplay_icons(self):
        icon = '<span class="avatar icon">A</span>'
        pages = {
            "scene": f'<div class="turn other"><span class="who">{icon}</span></div>',
            "understand": (
                '<div class="choose-row sentence receptive-choice">'
                '<span class="opt">パスポートを見せる</span>'
                '<span class="opt">搭乗券を見せる</span></div>' * 4
            ),
        }
        errors = check_deck.contextual_production_issues(pages)
        self.assertTrue(any("profile images" in item for item in errors))
        self.assertTrue(any("5–9-turn scene" in item for item in errors))
        self.assertTrue(any("English sense label" in item for item in errors))

    def test_contextual_accepts_profiled_roleplay_and_bilingual_receptive_choices(self):
        profile = '<img class="avatar" src="person.jpg" alt="">'
        receptive = (
            '<div class="choose-row sentence receptive-choice">'
            '<span class="opt"><span class="choice-en">Show a passport</span>'
            '<small>パスポートを見せる</small></span>'
            '<span class="opt"><span class="choice-en">Show a ticket</span>'
            '<small>搭乗券を見せる</small></span></div>'
        )
        pages = {
            "scene": f'<div class="turn other"><span class="who">{profile}</span></div>' * 5,
            "p3-model": f'<div class="turn other"><span class="who">{profile}</span></div>' * 5,
            "p3-complete": f'<div class="turn other"><span class="who">{profile}</span></div>' * 5,
            "understand": receptive * 4,
        }
        self.assertEqual(check_deck.contextual_production_issues(pages), [])

    def test_contextual_rejects_one_way_freetalk_capture(self):
        errors = check_deck.contextual_production_issues({
            "p3-freetalk": '<div class="fb" data-fb="one-way"></div>',
        })
        self.assertTrue(any("reciprocal Tutor/Me exchange" in item for item in errors))

    def test_contextual_replay_must_preserve_the_opening_scene(self):
        profile = '<img class="avatar" src="person.jpg" alt="">'
        turn = f'<div class="turn other"><span class="who">{profile}</span></div>'
        errors = check_deck.contextual_production_issues({
            "scene": turn * 7,
            "p3-model": turn * 5,
            "p3-complete": turn * 5,
        })
        self.assertTrue(any("replay the complete scene" in item for item in errors))

    def test_contextual_late_phrase_inputs_reuse_only_controlled_frames(self):
        pages = {
            "p1-fill": (
                '<input class="slot-input" data-answer="We&#x27;d like">'
                '<input class="slot-input" data-answer="if possible">'
            ),
            "p2-fill": '<input class="slot-input" data-answer="Could we have">',
            "p3-complete": (
                '<span class="target">ほしいです</span>'
                '<textarea class="free-input phrase-input" data-answer="We&#x27;d like"></textarea>'
            ),
            "transfer-scene": (
                '<span class="target">いただけますか</span>'
                '<textarea class="free-input phrase-input" '
                'data-answer="Could we have two seats"></textarea>'
            ),
        }
        errors = check_deck.contextual_production_issues(pages)
        self.assertFalse(any("p3-complete: phrase input" in item for item in errors))
        self.assertTrue(any("transfer-scene: phrase input" in item for item in errors))

    def test_freetalking_inventory_requires_canonical_order(self):
        source = "".join(
            f'<div data-page-id="{page_id}"></div>'
            for page_id in check_deck.FREETALK_PAGES
        )
        self.assertEqual(check_deck.freetalk_inventory_issues(source), [])
        swapped = source.replace(
            '<div data-page-id="article"></div><div data-page-id="lesson-style"></div>',
            '<div data-page-id="lesson-style"></div><div data-page-id="article"></div>',
        )
        self.assertTrue(check_deck.freetalk_inventory_issues(swapped))

    def test_freetalking_pair_requires_matching_claim_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary) / "sandbox/drafts/en/tracks/3-freetalking/courses"
            full = root / "topic-full/lessons/01-topic/lesson.html"
            accessible = root / "topic-accessible/lessons/01-topic/lesson.html"
            full.parent.mkdir(parents=True)
            accessible.parent.mkdir(parents=True)

            def deck(level, count):
                rows = "".join(
                    f'<div class="sent"><span class="s-ko">Claim {i}.<span class="s-mark"></span></span></div>'
                    for i in range(count)
                )
                return (
                    '<meta name="podo:review-id" content="FT-7">'
                    f'<meta name="podo:level" content="{level}">'
                    f'<div data-page-id="article">{rows}</div>'
                )

            full.write_text(deck("B2-C1 full", 12), encoding="utf-8")
            accessible.write_text(deck("B1 accessible", 11), encoding="utf-8")
            errors, _ = check_deck.freetalk_pair_issues([full, accessible])
            self.assertTrue(any("different row counts" in item for item in errors[accessible]))

    def test_freetalking_style_accepts_canonical_direct_wording(self):
        chunk = (
            '<p class="section-subtitle"><span class="ko">'
            'Please choose your preferred discussion style.'
            '</span><span class="ja">希望する会話の進め方を選んでください。</span></p>'
            '<button>Discussion first</button><button>Correction first</button>'
        )
        self.assertEqual(check_deck.freetalk_style_issues(chunk), [])

    def test_freetalking_style_rejects_support_question_and_fluency_label(self):
        chunk = (
            '<p class="section-subtitle"><span class="ko">'
            'How would you like me to support your English today?'
            '</span><span class="ja">今日はどうしますか？</span></p>'
            '<button>Fluency first</button><button>Correction first</button>'
        )
        errors = check_deck.freetalk_style_issues(chunk)
        self.assertTrue(any("canonical direct script" in item for item in errors))
        self.assertTrue(any("Discussion first" in item for item in errors))

    def test_freetalking_title_accepts_exact_brief_title_with_level_suffix(self):
        title = "Something that surprised you about another culture"
        source = (
            f"<title>{title} · Full — PODO English</title>"
            '<div data-page-id="lesson-goal">'
            f'<h2 class="transition-title">{title} '
            '<span class="title-ja">(異文化で驚いたこと)</span></h2></div>'
        )
        self.assertEqual(check_deck.freetalk_title_issues(source, title), [])

    def test_freetalking_title_rejects_improvised_short_title(self):
        expected = "Something that surprised you about another culture"
        source = (
            "<title>This surprised me · Full — PODO English</title>"
            '<div data-page-id="lesson-goal">'
            '<h2 class="transition-title">This surprised me '
            '<span class="title-ja">(驚いたこと)</span></h2></div>'
        )
        errors = check_deck.freetalk_title_issues(source, expected)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("document title" in item for item in errors))
        self.assertTrue(any("visible title" in item for item in errors))

    def test_shared_title_contract_accepts_exact_core_title(self):
        title = "Could you help me with this?"
        source = (
            f"<title>{title} — PODO English</title>"
            '<div data-page-id="lesson-goal">'
            f'<h2 class="transition-title">{title} '
            '<span class="title-ja">(これを手伝ってもらえますか？)</span></h2></div>'
        )
        self.assertEqual(check_deck.title_identity_issues(source, title), [])

    def test_tutor_answer_field_requires_english_label(self):
        self.assertTrue(
            check_deck.live_tutor_answer_issues(
                "p3-freetalk",
                '<span class="answer-label">先生の答え</span><textarea></textarea>',
            )
        )
        self.assertEqual(
            check_deck.live_tutor_answer_issues(
                "p3-freetalk",
                '<span class="answer-label">Tutor\'s answer'
                '<span class="task">先生の答え</span></span><textarea></textarea>',
            ),
            [],
        )

    def test_partner_turn_replay_rejects_shortened_line(self):
        model = (
            '<div class="turn other"><div class="bubble">'
            '<span class="korean">True. The other one has more space.</span>'
            '<span class="translation">そうですね。</span></div></div>'
        )
        complete = model.replace("True. ", "")
        self.assertNotEqual(
            check_deck.partner_turns(model),
            check_deck.partner_turns(complete),
        )


if __name__ == "__main__":
    unittest.main()


class ExemplarFrameFixedMarkerTests(unittest.TestCase):
    """A page may declare its frame is honestly fixed — deliberately, and on the record."""

    def page(self, marker=""):
        rows = "".join(
            f'<div class="model-line"><span class="korean">저는 {noun} 아니에요.</span></div>'
            for noun in ("회사원이", "대학생이", "가수가", "기자가")
        )
        return {"p1-read": f'data-page-id="p1-read"{marker}>{rows}'}

    def test_a_one_word_swap_fails_without_the_marker(self):
        errors = check_deck.exemplar_variation_issues(self.page(), level="초급")
        self.assertEqual(len(errors), 1)
        self.assertIn("differ in one word only", errors[0])

    def test_the_marker_clears_it(self):
        errors = check_deck.exemplar_variation_issues(
            self.page(' data-exemplar-review="frame-fixed"'), level="초급"
        )
        self.assertEqual(errors, [])

    def test_the_marker_is_exact_and_a_near_miss_does_not_count(self):
        for near in (' data-exemplar-review="frame fixed"',
                     ' data-exemplar-review=""',
                     ' data-exemplar-review'):
            self.assertEqual(
                len(check_deck.exemplar_variation_issues(self.page(near), level="초급")), 1, near
            )
