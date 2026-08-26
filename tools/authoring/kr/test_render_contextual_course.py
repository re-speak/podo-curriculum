#!/usr/bin/env python3
"""Regression tests for validator-visible controls emitted by the renderer."""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_reorder
import render_contextual_course as renderer


def rows(*sentences: str) -> list[list[str]]:
    return [[ko, f'ja {i}'] for i, ko in enumerate(sentences, 1)]


READ = rows('제 최애는 민지예요.', '막내는 혜인이에요.',
            '이 멤버는 하니예요.', '제 최애는 다니엘이에요.')
REORDER = [['제 | 최애는 | 민지예요.', '私の最推しはミンジです。', 'チェ | チェエヌン | ミンジイェヨ'],
           ['우리 | 이 멤버는 | 혜인이에요.', 'うちのこのメンバーはヘインです。', None],
           ['우리 팀 | 막내는 | 하니예요.', 'うちのチームの末っ子はハニです。', None],
           ['어제 콘서트에서 | 본 멤버는 | 다니엘이에요.', '昨日のコンサートで見たメンバーはダニエルです。', None]]
FILL = [['제 최애는 [민지예요].', '私の最推しはミンジです。', 'チェ チェエヌン [ミンジイェヨ]'],
        ['막내는 [혜인이에요].', '末っ子はヘインです。', None],
        ['이 멤버는 [하니예요].', 'このメンバーはハニです。', None],
        ['우리 팀 막내는 [다니엘이에요].', 'うちのチームの末っ子はダニエルです。', None]]
TRANSLATE = rows('제 최애는 민지예요.', '막내는 하니예요.',
                 '이 멤버는 혜인이에요.', '제 최애는 다니엘이에요.')


def part(**overrides) -> dict:
    data = {
        'line': '제 최애는 민지예요.',
        'ja': '私の最推しはミンジです。',
        'pattern': 'A는 B예요',
        'meaningKo': '소개할 대상 뒤에는 는을 붙여요.',
        'meaningJa': '紹介する対象の後ろに는を付けます。',
        'responseKo': '아, 민지 좋아하시는군요.',
        'responseJa': 'あ、ミンジが好きなんですね。',
        'readExamples': [list(row) for row in READ],
        'reorderExamples': [list(row) for row in REORDER],
        'fillExamples': [list(row) for row in FILL],
        'translateExamples': [list(row) for row in TRANSLATE],
    }
    data.update(overrides)
    return data


def lesson(**overrides) -> dict:
    item = {
        'number': 1,
        'slug': '01-favorite-member',
        'titleKo': '최애 소개',
        'titleJa': '推し紹介',
        'sceneKo': '팬 모임에서 인사해요.',
        'sceneJa': 'ファン交流会であいさつします。',
        'canDoKo': '내 최애를 소개할 수 있어요.',
        'canDoJa': '自分の推しを紹介できます。',
        'incoming': {'role': '팬', 'ko': '어떤 그룹 좋아하세요?', 'ja': 'どのグループが好きですか？'},
        'p1': part(),
        'p2': part(),
        'expressions': [['최애', '最推し']],
        'tipKo': '처음 만난 팬에게는 더 정중하게 물어요.',
        'tipJa': '初対面のファンには丁寧に聞きます。',
        'teaser': {'subtitleKo': '다음 장면', 'subtitleJa': '次の場面',
                   'bridgeKo': '이름은 들어 봤어요.', 'bridgeJa': '名前は聞いたことがあります。'},
        'nextHook': {'role': '팬', 'ko': '멤버가 몇 명이에요?', 'ja': 'メンバーは何人ですか？'},
    }
    item.update(overrides)
    return item


class StaticControlTests(unittest.TestCase):
    def test_inline_slot_is_a_real_input(self):
        control = renderer.slot_input("p1-fill", "정답")
        self.assertIn('<input class="slot-input"', control)
        self.assertIn('data-sync-id="p1-fill"', control)
        self.assertIn('data-answer="정답"', control)
        self.assertNotIn('<span class="slot"', control)

    def test_exact_and_open_answers_use_real_controls(self):
        exact = renderer.answer_input("translate", "문장")
        open_answer = renderer.answer_input("free")
        self.assertIn('<input class="space-input"', exact)
        self.assertIn('data-answer="문장"', exact)
        self.assertIn('<textarea class="free-input"', open_answer)

    def test_dialogue_completion_omits_a_reading_for_the_hidden_answer(self):
        control = renderer.turn(
            "나", "자리 나면 전화 주시겠어요?", "席が空いたら電話していただけますか？",
            slot="p3-complete-2", yomi="チャリ ナミョン チョナ チュシゲッソヨ",
        )
        self.assertIn('<input class="slot-input"', control)
        self.assertNotIn('class="yomi"', control)

    def test_spoken_response_uses_shared_feedback_activity(self):
        control = renderer.feedback_activity("p1-write-answer", "自分の話 & 例")
        self.assertIn('class="fb-compose"', control)
        self.assertIn('class="fb" data-fb="p1-write-answer"', control)
        self.assertIn('<span class="fb-task">自分の話 &amp; 例</span>', control)
        self.assertIn('class="fb-add" data-add="fix"', control)
        self.assertIn('class="fb-add" data-add="note"', control)
        self.assertNotIn('textarea class="free-input"', control)

    def test_reorder_kind_is_visible_without_javascript(self):
        control = renderer.build_zone("order", "문장")
        self.assertIn('class="answer-space build-zone"', control)
        self.assertIn('data-sync-kind="order"', control)
        self.assertIn('data-a="문장"', control)


class ScrambleTests(unittest.TestCase):
    """The scramble has to be a puzzle, and the same puzzle every render."""

    # Every case holds distinct chunks. A list with a repeated chunk cannot be
    # tested this way: `['a', 'b', 'a', 'b']` rotated is a permutation the
    # scramble is entitled to return, so "never the rotation" is unsatisfiable
    # rather than false.
    SENTENCES = [
        ['우리 팀', '막내는', '하니예요'],
        ['어제', '콘서트에서', '본 멤버는', '다니엘이에요'],
        ['혹시', '뉴진스', '아세요'],
        ['저는', '어제', '콘서트에', '갔어요'],
        ['제', '최애는', '민지예요'],
        ['이', '멤버는', '혜인이에요', '아마도'],
    ]

    def cases(self):
        for pieces in self.SENTENCES:
            yield list(pieces)

    def test_same_input_gives_the_same_order(self):
        for pieces in self.cases():
            self.assertEqual(renderer.scramble(pieces), renderer.scramble(list(pieces)))

    def test_never_identity_and_never_last_to_front(self):
        for pieces in self.cases():
            got = renderer.scramble(pieces)
            self.assertNotEqual(got, list(pieces), f'identity order for {pieces}')
            self.assertNotEqual(got, [pieces[-1], *pieces[:-1]],
                                f'last-to-front rotation for {pieces}')

    def test_the_chips_are_the_chunks(self):
        for pieces in self.cases():
            self.assertEqual(sorted(renderer.scramble(pieces)), sorted(pieces))

    def test_different_sentences_do_not_share_one_fixed_order(self):
        seen = {tuple(renderer.scramble(list(p))[0:1]) for p in self.SENTENCES}
        self.assertGreater(len(seen), 1)


class ChunkTests(unittest.TestCase):
    def test_chunks_rebuild_the_answer(self):
        pieces, answer = renderer.parse_chunks('제 | 최애는 | 민지예요.', 'p1')
        self.assertEqual(pieces, ['제', '최애는', '민지예요'])
        self.assertEqual(answer, '제 최애는 민지예요')
        self.assertEqual(check_reorder.norm(''.join(pieces)), check_reorder.norm(answer))

    def test_boundaries_come_from_the_manifest_not_from_word_count(self):
        pieces, _ = renderer.parse_chunks('이 멤버는 | 혜인이에요 | 아마도.', 'p1')
        self.assertIn('이 멤버는', pieces)          # a determiner keeps its noun

    def test_two_chunks_are_refused(self):
        with self.assertRaises(renderer.ManifestError) as caught:
            renderer.parse_chunks('제 최애는 민지예요.', 'ctx-a 01-b p1 reorderExamples[1]')
        self.assertIn('3–4', str(caught.exception))
        self.assertIn('01-b p1', str(caught.exception))

    def test_five_chunks_are_refused(self):
        with self.assertRaises(renderer.ManifestError):
            renderer.parse_chunks('가 | 나 | 다 | 라 | 마', 'p1')

    def test_an_empty_chunk_is_refused(self):
        with self.assertRaises(renderer.ManifestError):
            renderer.parse_chunks('제 최애는 | | 민지예요', 'p1')

    def test_rendered_chips_rebuild_the_graded_answer(self):
        html = renderer.reorder_activity('p1', REORDER, 'ctx-a 01-b p1')
        with tempfile.TemporaryDirectory() as tmp:
            deck = pathlib.Path(tmp) / 'lesson.html'
            deck.write_text(html, encoding='utf-8')
            self.assertEqual(check_reorder.check(deck), [])


class FillTests(unittest.TestCase):
    def test_the_blank_holds_the_pattern_not_the_sentence(self):
        html = renderer.fill_activity('p1', FILL, 'ctx-a 01-b p1')
        first = html.split('</div></div>')[0]
        self.assertIn('제 최애는 <input class="slot-input"', first)
        self.assertIn('data-answer="민지예요"', first)
        self.assertNotIn('data-answer="제 최애는 민지예요."', html)
        self.assertIn('>.</span>', first.replace(' ', ''))

    def test_the_reading_masks_only_the_blank(self):
        html = renderer.fill_activity('p1', FILL, 'ctx-a 01-b p1')
        self.assertIn('<span class="yomi">チェ チェエヌン ＿＿＿</span>', html)
        self.assertNotIn('ミンジイェヨ', html)

    def test_a_whole_sentence_blank_is_refused(self):
        with self.assertRaises(renderer.ManifestError) as caught:
            renderer.parse_blank('[제 최애는 민지예요.]', 'ctx-a 01-b p1 fillExamples[1]')
        self.assertIn('01-b p1', str(caught.exception))

    def test_a_row_must_mark_exactly_one_blank(self):
        for ko in ('제 최애는 민지예요.', '제 [최애]는 [민지예요].'):
            with self.assertRaises(renderer.ManifestError):
                renderer.parse_blank(ko, 'p1')

    def test_an_unmarked_reading_would_leak_the_answer(self):
        with self.assertRaises(renderer.ManifestError):
            renderer.mask_blank('チェ チェエヌン ミンジイェヨ', 'p1')


class RequiredFieldTests(unittest.TestCase):
    def test_a_missing_set_names_the_course_lesson_and_part(self):
        item = lesson()
        del item['p1']['reorderExamples']
        with self.assertRaises(renderer.ManifestError) as caught:
            renderer.render_lesson(item, 'K-POP 토크', False, 'ctx-kpop-talk-beginner 01-favorite-member')
        message = str(caught.exception)
        self.assertIn('ctx-kpop-talk-beginner', message)
        self.assertIn('01-favorite-member', message)
        self.assertIn('p1', message)
        self.assertIn('reorderExamples', message)

    def test_there_is_no_fallback_to_the_old_single_list(self):
        data = part()
        data['examples'] = data.pop('reorderExamples')
        with self.assertRaises(renderer.ManifestError):
            renderer.activities('p1', data, 'ctx-a 01-b p1')

    def test_every_set_needs_four_rows(self):
        data = part(translateExamples=TRANSLATE[:3])
        with self.assertRaises(renderer.ManifestError) as caught:
            renderer.activities('p1', data, 'ctx-a 01-b p1')
        self.assertIn('translateExamples', str(caught.exception))

    def test_check_reports_the_missing_fields_of_every_part(self):
        item = lesson()
        del item['p2']['fillExamples']
        problems = renderer.manifest_report({'lessons': [item]})[1]
        self.assertEqual(problems, ['01-favorite-member p2: missing fillExamples'])

    def test_the_four_sets_are_four_separate_sets(self):
        item = lesson()
        rendered = renderer.render_lesson(item, 'K-POP 토크', False, 'ctx-a 01-b')
        self.assertIn('data-answer="다니엘이에요"', rendered)      # from fillExamples
        self.assertIn('data-a="어제 콘서트에서 본 멤버는 다니엘이에요"', rendered)  # reorderExamples


class ChoosePositionTests(unittest.TestCase):
    CHOICES = [
        {'ja': 'a', 'prefix': '손이 ', 'options': ['떨려서', '떨리서'], 'correct': 0, 'suffix': ' 못 했어.'},
        {'ja': 'b', 'prefix': '서버가 ', 'options': ['느려서', '느리서'], 'correct': 0, 'suffix': ' 못 했어.'},
        {'ja': 'c', 'prefix': '', 'options': ['긴장해서', '긴장하서'], 'correct': 0, 'suffix': ' 못 골랐어.'},
        {'ja': 'd', 'prefix': '길이 ', 'options': ['막혀서', '막히서'], 'correct': 0, 'suffix': ' 못 맞췄어.'},
    ]

    def slots(self, where):
        return renderer.correct_slots(self.CHOICES, where)

    def test_the_answer_is_neither_one_column_nor_every_other_row(self):
        for where in ('ctx-a 01-b p1', 'ctx-a 02-c p2', 'ctx-d 07-e p1', 'ctx-f 10-g p2'):
            got = self.slots(where)
            self.assertGreater(len(set(got)), 1, f'one column in {where}')
            self.assertNotIn(got, ([0, 1, 0, 1], [1, 0, 1, 0]), f'alternating in {where}')

    def test_placement_is_stable_across_renders(self):
        self.assertEqual(self.slots('ctx-a 01-b p1'), self.slots('ctx-a 01-b p1'))

    def test_the_marked_option_is_the_authored_answer(self):
        html = renderer.choose_activity('p1', self.CHOICES, 'ctx-a 01-b p1')
        marked = re.findall(r'<span class="opt" data-correct=""[^>]*>([^<]+)</span>', html)
        self.assertEqual(marked, ['떨려서', '느려서', '긴장해서', '막혀서'])
        self.assertEqual(html.count('data-correct'), 4)


if __name__ == "__main__":
    unittest.main()


class ChunkReadingTests(unittest.TestCase):
    """A chip a sub-중급 learner must say carries its own reading."""

    def test_each_chunk_gets_its_own_reading(self):
        self.assertEqual(
            renderer.chunk_readings('チェ | チェエヌン | ミンジイェヨ',
                                    ['제', '최애는', '민지예요'], 'x'),
            ['チェ', 'チェエヌン', 'ミンジイェヨ'],
        )

    def test_a_deck_without_readings_gets_none_per_chunk(self):
        self.assertEqual(renderer.chunk_readings(None, ['가', '나', '다'], 'x'),
                         [None, None, None])

    def test_a_reading_split_differently_from_the_korean_is_an_error(self):
        with self.assertRaises(renderer.ManifestError) as caught:
            renderer.chunk_readings('チェ | チェエヌン', ['제', '최애는', '민지예요'], 'x')
        self.assertIn('3 chunks but 2 reading(s)', str(caught.exception))

    def test_an_unsplit_reading_is_an_error_rather_than_one_long_chip(self):
        with self.assertRaises(renderer.ManifestError):
            renderer.chunk_readings('チェ チェエヌン ミンジイェヨ',
                                    ['제', '최애는', '민지예요'], 'x')

    def test_readings_follow_the_chips_through_the_scramble(self):
        pairs = [('제', 'チェ'), ('최애는', 'チェエヌン'), ('민지예요', 'ミンジイェヨ')]
        scrambled = renderer.scramble_pairs(pairs)
        self.assertEqual([c for c, _ in scrambled], renderer.scramble(['제', '최애는', '민지예요']))
        for chunk, reading in scrambled:
            self.assertEqual(dict(pairs)[chunk], reading)

    def test_adding_readings_does_not_reshuffle_the_chips(self):
        chunks = ['우리 팀', '막내는', '하니예요']
        without = renderer.scramble(chunks)
        with_readings = [c for c, _ in renderer.scramble_pairs(
            [(c, f'r{i}') for i, c in enumerate(chunks)])]
        self.assertEqual(without, with_readings)
