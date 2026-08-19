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
            "lesson-goal": '<div class="known-row"></div>' * 3,
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
            '<span>What do you need?</span></div>'
            '<div class="turn me"><span class="who"><span class="avatar icon">私</span></span>'
            '<span>Could you help me with ~?</span></div>'
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
