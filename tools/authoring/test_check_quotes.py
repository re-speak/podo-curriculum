#!/usr/bin/env python3
"""Regression tests for the 「인용한 표현」 citation checker, both corpora."""

from __future__ import annotations

import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_quotes


KR_PATH = "sandbox/drafts/kr/tracks/2-core-patterns/lessons/01-x/lesson.html"
EN_PATH = "sandbox/drafts/en/tracks/1-core-patterns/lessons/01-x/lesson.html"

EN_HEAD = (
    '<meta name="podo:target-language" content="en">'
    '<meta name="podo:title-en" content="You have to show ID">'
)


def pair(ko, ja):
    return f'<span class="ko">{ko}</span><span class="ja">{ja}</span>'


def kr(ko, ja):
    return check_quotes.deck_rows(KR_PATH, pair(ko, ja))


def en(body, ko, ja):
    return check_quotes.deck_rows(EN_PATH, EN_HEAD + body + pair(ko, ja))


class KoreanCitationTests(unittest.TestCase):
    def test_bare_hangul_in_japanese_prose_is_a_citation(self):
        rows = kr("‘도대체 왜 그랬어?’는 이유를 강하게 요구해요.",
                  "도대체 왜 그랬어?は理由を強く求めます。")
        self.assertEqual([r[0] for r in rows], [["도대체 왜 그랬어?"]])

    def test_wrapped_hangul_is_clean(self):
        self.assertEqual(
            kr("‘도대체 왜 그랬어?’는 이유를 강하게 요구해요.",
               "「도대체 왜 그랬어?」は理由を強く求めます。"),
            [])

    def test_a_ja_span_without_kana_is_not_japanese_prose(self):
        self.assertEqual(kr("가나다", "가나다"), [])

    def test_html_entities_do_not_hide_a_citation(self):
        rows = kr("‘어때?’만 물어보세요.", "&#x300C;어때?&#x300D;だけ聞いてください。")
        self.assertEqual(rows, [])


class EnglishCitationTests(unittest.TestCase):
    def test_bare_taught_ending_in_japanese_prose_is_a_citation(self):
        rows = en('<span class="ending">have to</span>',
                  "Use have to before a plain verb.",
                  "決まりで必要な行動には have to と動詞の原形を使います。")
        self.assertEqual([r[0] for r in rows], [["have to"]])

    def test_wrapped_taught_expression_is_clean(self):
        self.assertEqual(
            en('<span class="ending">have to</span>',
               "Use “have to” before a plain verb.",
               "決まりで必要な行動には「have to」と動詞の原形を使います。"),
            [])

    def test_untaught_latin_in_japanese_prose_is_left_alone(self):
        """role labels, loanwords and acronyms are not citations"""
        self.assertEqual(
            en('<span class="ending">have to</span>',
               "Read the Traveller lines aloud.",
               "AIやMBTIの話です。Traveller のセリフを読んでください。"),
            [])

    def test_sent_hero_english_half_qualifies(self):
        rows = en('<div class="sent-hero"><span class="korean">I went to the '
                  'park</span><span class="translation">公園に行きました</span></div>',
                  "Use went to plus a place.",
                  "終わった外出には went to と場所を使います。")
        self.assertEqual([r[0] for r in rows], [["went to"]])

    def test_title_meta_qualifies(self):
        rows = en("", "Use You have to show for a rule.",
                  "決まりには You have to show を使います。")
        self.assertEqual([r[0] for r in rows], [["You have to show"]])

    def test_single_word_needs_an_explicit_mark_and_length(self):
        marked = en("<b>anymore</b>", "Put anymore at the end.",
                    "文末に anymore を置きます。")
        self.assertEqual([r[0] for r in marked], [["anymore"]])
        # 'too' is bolded but shorter than MIN_SINGLE_WORD, so it stays quiet
        self.assertEqual(
            en("<b>too</b>", "Put too at the end.", "文末に too を置きます。"),
            [])
        # an unmarked single word never qualifies, however long
        self.assertEqual(
            en('<span class="ending">have to</span>',
               "Speak slowly.", "ゆっくり slowly と言ってください。"),
            [])

    def test_contrast_partner_on_a_flagged_line_is_reported_too(self):
        rows = en('<span class="ending">in the end</span>',
                  "In the end emphasises the result; finally the last step.",
                  "in the end は最終的な結果、finally the last step は最後の手順です。")
        self.assertEqual([r[0] for r in rows],
                         [["in the end", "finally the last step"]])

    def test_contrast_partners_alone_are_deliberately_missed(self):
        """no taught anchor on the line means no report — the conservative half"""
        self.assertEqual(
            en('<span class="ending">have to</span>',
               "To be honest and for some reason differ.",
               "to be honest は率直に、for some reason は原因不明のときです。"),
            [])

    def test_japanese_ending_spans_are_not_taught_english(self):
        self.assertEqual(
            en('<span class="ending">今日必要な判断は、</span>',
               "Read it aloud.", "AI の話をしましょう。"),
            [])


class LanguageDetectionTests(unittest.TestCase):
    def test_meta_beats_the_path(self):
        self.assertEqual(
            check_quotes.language_of(KR_PATH, EN_HEAD), "en")

    def test_path_is_the_fallback(self):
        self.assertEqual(check_quotes.language_of(EN_PATH, "<html>"), "en")
        self.assertEqual(check_quotes.language_of(KR_PATH, "<html>"), "kr")

    def test_a_korean_deck_is_read_as_korean_without_a_meta(self):
        rows = check_quotes.deck_rows(
            KR_PATH, pair("‘안녕’이에요.", "안녕です。"))
        self.assertEqual([r[0] for r in rows], [["안녕"]])


class StrictTests(unittest.TestCase):
    def test_particle_belongs_outside_the_quote(self):
        rows = check_quotes.deck_rows(
            KR_PATH, pair("‘어때?만’ 물어보세요.", "「어때?」だけ聞いてください。"),
            strict=True)
        self.assertEqual(len(rows), 1)
        self.assertIn("particle inside the quote in .ko", rows[0][3][0])

    def test_period_belongs_outside_the_quote(self):
        rows = check_quotes.deck_rows(
            KR_PATH,
            pair("‘선생님이 안 쓴대요.’ 믿기세요?",
                 "「先生は使わないそうです。」信じられますか？"),
            strict=True)
        notes = rows[0][3]
        self.assertTrue(any("period inside the quote in .ko" in n for n in notes))
        self.assertTrue(any("period inside the quote in .ja" in n for n in notes))

    def test_the_same_line_is_clean_when_the_period_is_outside(self):
        self.assertEqual(
            check_quotes.deck_rows(
                KR_PATH,
                pair("‘선생님이 안 쓴대요’. 믿기세요?",
                     "「先生は使わないそうです」。信じられますか？"),
                strict=True),
            [])

    def test_straight_quotes_are_never_used(self):
        rows = check_quotes.deck_rows(
            KR_PATH, pair("'저는'을 '전'이라고 짧게 말해요.",
                          "「저는」は「전」と短く言います。"),
            strict=True)
        self.assertTrue(any("straight quote in .ko" in n for n in rows[0][3]))

    def test_strict_is_off_by_default(self):
        self.assertEqual(
            check_quotes.deck_rows(
                KR_PATH, pair("'저는'을 '전'이라고 짧게 말해요.",
                              "「저는」は「전」と短く言います。")),
            [])


if __name__ == "__main__":
    unittest.main()
