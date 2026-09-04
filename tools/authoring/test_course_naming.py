"""What a course is called, and the ways it can stop agreeing with itself."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import course_naming as naming


def row(slug, difficulty="INTERMEDIATE", class_level=300.0, corpus="kr",
        enabled=True, **title):
    return naming.Row(corpus, slug, class_level, difficulty, enabled, title)


class TitleShape(unittest.TestCase):
    def test_level_leads_and_the_rail_header_is_not_repeated(self):
        self.assertEqual(
            naming.title_for("kr", "talk-me-lately-advanced", "ja",
                             "最近のわたし", "ADVANCED", 3),
            "(上級) 最近のわたし")

    def test_a_contextual_course_names_its_sub_family(self):
        self.assertEqual(
            naming.title_for("kr", "ctx-drama-friends-intermediate", "ja",
                             "友だちになるまで", "INTERMEDIATE", 1),
            "(中級) ドラマ · 友だちになるまで")

    def test_a_topic_that_leads_with_the_family_does_not_repeat_it(self):
        self.assertEqual(
            naming.title_for("kr", "ctx-kpop-talk-beginner", "ja",
                             "K-POPトーク", "BEGINNER", 1),
            "(初級) K-POPトーク")
        self.assertEqual(
            naming.title_for("kr", "ctx-banmal-chatting-intermediate", "ko",
                             "반말로 수다 떨기", "INTERMEDIATE", 2),
            "(중급) 반말로 수다 떨기")

    def test_a_topic_that_merely_ends_with_the_family_keeps_it(self):
        # `여행 · 혼자 하는 여행` is repetitive but the prefix is the rail name,
        # and dropping it would silently rename a live English course.
        self.assertEqual(
            naming.title_for("en", "ctx-travel-independent-social", "ko",
                             "혼자 하는 여행", "UPPER_INTERMEDIATE", 5),
            "(중고급) 여행 · 혼자 하는 여행")

    def test_a_latin_family_name_has_to_end_on_a_boundary(self):
        # `Travel` must not swallow `Travelling alone`.
        self.assertEqual(
            naming.title_for("en", "ctx-travel-independent-social", "en",
                             "Travelling alone", "UPPER_INTERMEDIATE", 5),
            "(Upper Intermediate) Travel · Travelling alone")

    def test_a_korean_core_course_is_named_by_its_rung(self):
        self.assertEqual(
            naming.title_for("kr", "core-upper-beginner-1", "ja", "", "UPPER_BEGINNER", 5),
            "(初中級) コアパターン 5")

    def test_an_english_core_course_is_named_by_its_topic(self):
        self.assertEqual(
            naming.title_for("en", "core-first-exchanges-1", "ja", "最初の一文", "BEGINNER", 1),
            "(初級) コアパターン · 最初の一文")

    def test_a_rung_is_what_comes_back_out_of_a_core_title(self):
        self.assertEqual(
            naming.topic_of("kr", "core-upper-beginner-1", "ja", "(初中級) コアパターン 5"),
            "5")

    def test_the_topic_survives_a_round_trip(self):
        for corpus, slug, lang, topic in (
                ("kr", "ctx-drama-friends-intermediate", "ja", "友だちになるまで"),
                ("kr", "ctx-kpop-talk-beginner", "ja", "K-POPトーク"),
                ("kr", "talk-me-lately-advanced", "ko", "요즘의 나"),
                ("en", "ctx-travel-arrivals-transport", "en", "Arrivals"),
        ):
            title = naming.title_for(corpus, slug, lang, topic, "INTERMEDIATE", 1)
            self.assertEqual(naming.topic_of(corpus, slug, lang, title), topic)


class Ladder(unittest.TestCase):
    def test_position_follows_class_level_within_a_family(self):
        rows = [row("core-b-2", class_level=200.02), row("core-b-1", class_level=200.01),
                row("ctx-drama-x", class_level=300.01)]
        place = naming.ladder(rows)
        self.assertEqual(place[("kr", "core-b-1")], 1)
        self.assertEqual(place[("kr", "core-b-2")], 2)
        self.assertEqual(place[("kr", "ctx-drama-x")], 1)

    def test_retiring_a_course_closes_the_gap(self):
        rows = [row("core-b-1", class_level=200.01),
                row("core-b-2", class_level=200.02, enabled=False),
                row("core-b-3", class_level=200.03)]
        place = naming.ladder(rows)
        self.assertEqual(place[("kr", "core-b-3")], 2)
        self.assertNotIn(("kr", "core-b-2"), place)


class Gate(unittest.TestCase):
    def test_a_title_that_composes_itself_is_silent(self):
        self.assertEqual(naming.problems([row(
            "ctx-drama-friends-intermediate",
            ko="(중급) 드라마 · 친구", en="(Intermediate) Drama · Becoming friends",
            ja="(中級) ドラマ · 友だちになるまで")]), [])

    def test_a_level_word_that_disagrees_with_difficulty_fails(self):
        found = naming.problems([row(
            "ctx-drama-friends-intermediate", difficulty="ADVANCED",
            ko="(중급) 드라마 · 친구", en="(Intermediate) Drama · Becoming friends",
            ja="(中級) ドラマ · 友だちになるまで")])
        self.assertEqual(len(found), 3)
        self.assertIn("(고급) 드라마 · 친구", found[0])

    def test_a_rung_that_disagrees_with_class_level_fails(self):
        found = naming.problems([
            row("core-a", class_level=200.01, ko="(중급) 핵심 패턴 1",
                en="(Intermediate) Core 1", ja="(中級) コアパターン 1"),
            row("core-b", class_level=200.02, ko="(중급) 핵심 패턴 1",
                en="(Intermediate) Core 1", ja="(中級) コアパターン 1"),
        ])
        self.assertEqual(len(found), 3)
        self.assertTrue(all("core-b" in problem for problem in found))

    def test_the_old_trailing_shape_fails(self):
        found = naming.problems([row(
            "talk-me-lately-advanced", difficulty="ADVANCED",
            ko="프리토킹 · 요즘의 나 · 고급", en="Free talking · Me lately · Advanced",
            ja="フリートーキング · 最近のわたし · 上級")])
        self.assertEqual(len(found), 6)  # three wrong shapes, three stray level words

    def test_a_level_word_hiding_in_the_topic_fails(self):
        found = naming.problems([row(
            "hangul-starter", difficulty="BEGINNER", class_level=100.01,
            ko="(초급) 한글 떼기 · 왕초급", en="(Beginner) Hangul reading",
            ja="(初級) ハングル入門")])
        self.assertEqual(len(found), 1)
        self.assertIn("says its level twice", found[0])

    def test_a_missing_language_fails(self):
        found = naming.problems([row(
            "talk-me-lately-advanced", difficulty="ADVANCED",
            ko="(고급) 요즘의 나", ja="(上級) 最近のわたし")])
        self.assertEqual(len(found), 1)
        self.assertIn("spec.title.en is missing", found[0])


class Cover(unittest.TestCase):
    def test_the_pill_and_the_title_carry_the_same_rung(self):
        pill, title = naming.cover_copy(
            "kr", "core-upper-beginner-1",
            {"ko": "(초중급) 핵심 패턴 5", "en": "(Upper Beginner) Core 5",
             "ja": "(初中級) コアパターン 5"},
            "UPPER_BEGINNER", 5)
        self.assertEqual(pill, "パターン 5 · 初中級")
        self.assertEqual(title, "핵심 패턴 5")

    def test_the_pill_level_is_the_filter_word_not_the_title_word(self):
        pill, _ = naming.cover_copy(
            "kr", "hangul-starter", {"ko": "(초급) 한글 떼기", "en": "(Beginner) Hangul reading",
                                     "ja": "(初級) ハングル入門"}, "BEGINNER", None)
        self.assertEqual(pill, "ハングル · 初級")

    def test_an_unordered_family_gets_no_number(self):
        pill, title = naming.cover_copy(
            "kr", "ctx-travel-eating-out-upper-beginner",
            {"ko": "(초중급) 여행 · 식당 & 카페", "en": "(Upper Beginner) Travel · Eating out",
             "ja": "(初中級) 旅行 · レストランとカフェ"}, "UPPER_BEGINNER", 2)
        self.assertEqual(pill, "旅行 · 初中級")
        self.assertEqual(title, "식당 & 카페")


class DisplayLevel(unittest.TestCase):
    """The one course whose filter slot and level word are different things.

    trial-lv2 is written at 초급 but sits in the UPPER_BEGINNER slot, because
    the ladder has a 왕초급 rung and the app's filter does not — see
    `course_naming.DISPLAY_LEVEL`. What must not drift is the pair: the title
    and the pill both take the declared word, and everything else about the
    title is still recomposed and checked.
    """

    TITLE = {"ko": "(초급) 체험 레슨", "en": "(Beginner) Trial lesson",
             "ja": "(初級) 体験レッスン"}

    def test_the_title_takes_the_declared_word_not_the_difficulty(self):
        self.assertEqual(
            naming.title_for("kr", "trial-lv2-patterns", "ja", "体験レッスン",
                             "UPPER_BEGINNER", None),
            "(初級) 体験レッスン")

    def test_the_pill_follows_the_title_rather_than_the_filter_chip(self):
        pill, _ = naming.cover_copy("kr", "trial-lv2-patterns", self.TITLE,
                                    "UPPER_BEGINNER", None)
        self.assertEqual(pill, "体験 · 初級")

    def test_the_gate_accepts_the_declared_pair(self):
        self.assertEqual(
            naming.problems([row("trial-lv2-patterns", difficulty="UPPER_BEGINNER",
                                 class_level=12.0, **self.TITLE)]),
            [])

    def test_a_course_without_an_entry_still_has_to_match_its_difficulty(self):
        found = naming.problems([row("trial-lv3-contextual", difficulty="UPPER_BEGINNER",
                                     class_level=13.0, **self.TITLE)])
        self.assertTrue(any("composes" in problem for problem in found), found)


if __name__ == "__main__":
    unittest.main()
