#!/usr/bin/env python3
"""Render fully authored contextual lessons from a reviewed course manifest.

This is deliberately a renderer, not a content generator.  Every Korean line,
Japanese translation, teaching explanation, reaction and continuity hook lives
in the manifest and is reviewed there.  The renderer only repeats those facts
through the canonical 26-page interaction arc without hand-copying runtime
markup sixty times.


Manifest schema — the four sentence sets
========================================

A part (``p1`` / ``p2``) runs four closed sentence activities, and each one
draws from its **own** four sentences.  Running read, reorder, fill and
translate over a single list is four passes over the same four sentences: the
learner has read the answer three times before being asked to produce it.

Every row is the same compact triple everywhere — ``[ko, ja, yomi?]``, or the
equivalent ``{"ko": …, "ja": …, "yomi": …}``.  Exactly four rows per list
(``ux-philosophy.md``: "Four items in every closed sentence activity", and the
page copy says 네 문장 out loud).  Two of the lists mark one extra thing inside
``ko`` itself, so an author writes an ordinary sentence and adds one character:

  ``readExamples``       plain sentences, read aloud            → ``p1-read``
  ``reorderExamples``    ``|`` marks the chunk boundaries       → ``p1-reorder``
  ``fillExamples``       ``[…]`` marks the blank                → ``p1-fill``
  ``translateExamples``  plain sentences, produced from the ja  → ``p1-translate``

reorderExamples — the author decides the chunks
    ``"제 최애는 | 민지예요."`` → chips ``제 최애는`` / ``민지예요``, graded
    against ``제 최애는 민지예요``.  Three or four chunks, never two, never
    five: "Reorder four meaningful chunks, not four arbitrary fragments …
    Decide the boundaries from the sentence."  Word count cannot decide this —
    it split ``이 멤버는 혜인이에요`` into ``이`` / ``멤버는`` / ``혜인이에요``,
    tearing a determiner off its noun.  The renderer never invents a boundary;
    it only refuses a chunking that cannot rebuild its own answer.

fillExamples — the blank holds the pattern, nothing else
    ``"제 최애는 [민지예요]."`` → ``제 최애는 ▁▁▁.`` with ``민지예요`` as the
    answer.  Exactly one ``[…]``, and something must survive outside it
    ("Blanks target only the pattern being practiced").  When the deck carries
    readings, the yomi marks the same span and the renderer masks it:
    ``"チェ チェエヌン [ミンジイェヨ]"`` → ``チェ チェエヌン ＿＿＿``.

All four fields are required.  There is no fallback to the old single
``examples`` list — a silent fallback would let a part keep running four
activities on one sentence set while looking fine.  ``--check`` reports which
parts are still missing which field.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
from itertools import permutations, product

import check_reorder


# activities.js grades a reorder tray with norm(): whitespace and punctuation
# stripped, then compared.  check_reorder.py already mirrors that exactly, so
# the chunk validator borrows it instead of deriving a second copy that can
# drift.
norm = check_reorder.norm

ACTIVITY_FIELDS = ('readExamples', 'reorderExamples', 'fillExamples', 'translateExamples')
ROWS_PER_ACTIVITY = 4
CHUNK_RANGE = (3, 4)
CHUNK_SEP = '|'
BLANK_RE = re.compile(r'\[([^\[\]]*)\]')
TRAILING_PUNCT = re.compile(r'[.!?。？！]+$')
BLANK_YOMI = '＿＿＿'


class ManifestError(ValueError):
    """A manifest the renderer refuses to guess at."""


AVATAR = ('<span class="avatar icon"><svg aria-hidden="true" viewBox="0 0 24 24">'
          '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2.5c-4.7 0-8.5 '
          '2.6-8.5 5.8V22h17v-1.7c0-3.2-3.8-5.8-8.5-5.8Z" fill="currentColor"/>'
          '</svg></span>')
PORTRAIT_PREFIX = '../../../../../../../../../shared/assets/'
PORTRAIT_CAST = json.loads(
    (pathlib.Path(__file__).resolve().parents[3]
     / 'sandbox/drafts/kr/tracks/3-contextual-korean/portrait-cast.json').read_text()
)


def avatar_for(role: str, course_name: str) -> str:
    """Return a stable course-scoped face; tutors and learners stay neutral."""
    if role in {'나', '선생님'}:
        return AVATAR
    # Unit tests render synthetic course fragments that intentionally have no
    # cast ledger. Real course renders always pass a key present in the ledger.
    if course_name not in PORTRAIT_CAST:
        return f'<img alt="" class="avatar" src="{PORTRAIT_PREFIX}portrait-yujin.jpg"/>'
    try:
        filename = PORTRAIT_CAST[course_name][role]
    except KeyError as failure:
        raise ManifestError(f'{course_name}: no portrait assignment for role {role!r}') from failure
    return f'<img alt="" class="avatar" src="{PORTRAIT_PREFIX}{esc(filename)}"/>'


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def example_values(value: dict | list) -> tuple[str, str, str | None]:
    """Allow compact [ko, ja, yomi?] rows in reviewed manifests."""
    if isinstance(value, dict):
        return value['ko'], value['ja'], value.get('yomi')
    return value[0], value[1], value[2] if len(value) > 2 else None


def yomi_span(value: str | None) -> str:
    return f'<span class="yomi">{esc(value)}</span>' if value else ''


def slot_input(sync_id: str, answer: str) -> str:
    """A validator-visible inline blank, already present in the source HTML."""
    return (f'<input class="slot-input" type="text" data-sync-id="{esc(sync_id)}" '
            f'data-answer="{esc(answer)}" autocomplete="off" spellcheck="false">')


def answer_input(sync_id: str, answer: str = "") -> str:
    """A full-width exact-answer input, or an open textarea when no answer exists."""
    if answer:
        control = (f'<input class="space-input" type="text" data-sync-id="{esc(sync_id)}" '
                   f'data-answer="{esc(answer)}" autocomplete="off" spellcheck="false">')
    else:
        control = (f'<textarea class="free-input" data-sync-id="{esc(sync_id)}" rows="2" '
                   'spellcheck="false" maxlength="2000"></textarea>')
    return f'<span class="answer-space as-input">{control}</span>'


def feedback_activity(sync_id: str, task: str = "") -> str:
    """A spoken response the tutor can transcribe, correct, and annotate."""
    prompt = f'<span class="fb-task">{esc(task)}</span>' if task else ''
    return (f'<div class="fb-compose"><div class="fb" data-fb="{esc(sync_id)}">{prompt}</div>'
            '<div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ 교정</button>'
            '<button class="fb-add" data-add="note" type="button">＋ 노트</button></div></div>')


def build_zone(sync_id: str, answer: str) -> str:
    """A validator-visible custom order control; activities.js supplies the kind."""
    return (f'<span class="answer-space build-zone" data-sync-id="{esc(sync_id)}" '
            f'data-sync-kind="order" data-a="{esc(answer)}"></span>')


def turn(role: str, ko: str, ja: str, *, course_name: str = '', slot: str | None = None,
         yomi: str | None = None) -> str:
    mine = role == "나"
    who = avatar_for(role, course_name)
    bubble = "bubble me" if mine else "bubble"
    cls = "turn me" if mine else "turn other"
    if slot:
        content = (f'<div class="answer-box"><span class="answer-label">{esc(ja)}</span>'
                   f'<span class="answer-fill"><span class="korean">'
                   f'{slot_input(slot, ko)}</span></span></div>')
    else:
        reading = f'<span class="yomi">{esc(yomi)}</span>' if yomi else ''
        content = f'<span class="korean">{esc(ko)}</span>{reading}<span class="translation">{esc(ja)}</span>'
    return (f'<div class="{cls}"><span class="who">{who}<span class="who-name">{esc(role)}</span>'
            f'</span><div class="{bubble}">{content}</div></div>')


def open_turn(role: str, label: str, sync_id: str, *, course_name: str = '', seed: str = "",
              tall: bool = False) -> str:
    """Render a genuinely editable free response, rather than an exact-answer slot."""
    mine = role == "나"
    who = avatar_for(role, course_name)
    bubble = "bubble me" if mine else "bubble"
    cls = "turn me" if mine else "turn other"
    size = " tall" if tall else " small"
    return (f'<div class="{cls}"><span class="who">{who}<span class="who-name">{esc(role)}</span>'
            f'</span><div class="{bubble}"><div class="answer-box{size}">'
            f'<span class="answer-label task">{esc(label)}</span>'
            f'{answer_input(sync_id, seed)}</div></div></div>')


def page(page_id: str, title: str, title_ja: str, body: str, subtitle: tuple[str, str] | None = None,
         cls: str = "section", act: str | None = None) -> str:
    act_attr = f' data-act="{esc(act)}"' if act else ""
    sub = ""
    if subtitle:
        sub = (f'<p class="section-subtitle"><span class="ko">{esc(subtitle[0])}</span>'
               f'<span class="ja">{esc(subtitle[1])}</span></p>')
    return (f'<div class="{cls}" data-page-id="{page_id}"{act_attr}><h2 class="section-title">'
            f'{esc(title)} <span class="title-ja">({esc(title_ja)})</span></h2>{sub}{body}</div>')


def transition(page_id: str, kicker: str, title: str, title_ja: str, copy_ja: str, act: str | None = None) -> str:
    act_attr = f' data-act="{esc(act)}"' if act else ""
    return (f'<div class="transition-page" data-page-id="{page_id}"{act_attr}>'
            f'<span class="transition-kicker">{esc(kicker)}</span><h2 class="transition-title">'
            f'{esc(title)} <span class="title-ja">({esc(title_ja)})</span></h2>'
            f'<p class="transition-copy">{esc(copy_ja)}</p></div>')


def episode_card(item: dict, course_name: str, course_key: str) -> str:
    return (f'<div class="transition-page episode-card" data-page-id="episode-card" '
            f'data-act="{esc(item["titleKo"])}"><span class="transition-kicker">'
            f'{esc(course_name)} · 제{item["number"]}화</span><h2 class="transition-title">'
            f'{esc(item["titleKo"])}</h2><p class="transition-copy">{esc(item["sceneJa"])}</p>'
            f'<div class="scene-cast"><span class="cast-row">{AVATAR}<span class="cast-who">나'
            f'<small>{esc(item.get("learnerRoleJa", "K-POPファン・あなたの役"))}</small></span></span>'
            f'<span class="cast-row">{avatar_for(item["incoming"]["role"], course_key)}'
            f'<span class="cast-who">{esc(item["incoming"]["role"])}'
            f'<small>{esc(item.get("partnerRoleJa", "同じ趣味を楽しむ友達"))}</small></span></span></div></div>')


def model_list(examples: list[dict]) -> str:
    rows = []
    for value in examples:
        ko, ja, yomi = example_values(value)
        reading = f'<span class="yomi">{esc(yomi)}</span>' if yomi else ''
        rows.append(f'<div class="model-line"><span class="korean">{esc(ko)}</span>'
                    f'{reading}<span class="translation">{esc(ja)}</span></div>')
    return '<div class="model-list">' + ''.join(rows) + '</div>'


def rule_visual(pattern: dict) -> str:
    cards = pattern.get('ruleCards') or [
        {'headKo': '표현의 틀', 'headJa': '表現の形', 'form': pattern['pattern']},
    ]
    return '<div class="batchim one">' + ''.join(
        f'<div class="bt-box"><span class="bt-head">{esc(card["headKo"])} '
        f'<small>{esc(card["headJa"])}</small></span><div class="bt-ex"><span>'
        f'{esc(card["form"])}</span></div></div>' for card in cards
    ) + '</div>'


def correct_slots(choices: list[dict], where: str) -> list[int]:
    """Where the right answer sits in each row — not one column, not every other.

    A learner reads a column before they read Korean.  The manifest authors the
    options in a fixed order, so the placement is the renderer's to decide: it
    picks one seeded pattern for the whole page, with the constant and the
    strictly alternating patterns removed from the candidate set.
    """
    widths = [len(row['options']) for row in choices]
    patterns = list(product(*(range(w) for w in widths)))
    if len(choices) >= 3:
        alternating = [tuple((start + i) % w for i, w in enumerate(widths)) for start in (0, 1)]
        kept = [p for p in patterns if len(set(p)) > 1 and p not in alternating]
        patterns = kept or patterns
    seed = seed_of(where, *(str(row.get('prefix', '')) + '|'.join(row['options'])
                            for row in choices))
    return list(patterns[seed % len(patterns)])


def choose_activity(part: str, choices: list[dict], where: str = '') -> str:
    rows = []
    slots = correct_slots(choices, where or part)
    for i, (row, slot) in enumerate(zip(choices, slots), 1):
        ordered = list(row['options'])
        ordered.insert(slot, ordered.pop(row['correct']))
        options = []
        for j, option in enumerate(ordered):
            correct = ' data-correct=""' if j == slot else ''
            options.append(f'<span class="opt"{correct} data-sync-option="{chr(97 + j)}">'
                           f'{esc(option)}</span>')
        joined = '<span class="sep">/</span>'.join(options)
        rows.append(f'<div class="choose-row sentence" data-sync-id="{part}-choice-{i}" '
                    f'data-sync-kind="selection"><span class="translation">{esc(row["ja"])}</span>'
                    f'<span class="choose-sentence">{esc(row.get("prefix", ""))}{joined}'
                    f'{esc(row.get("suffix", ""))}</span></div>')
    return ''.join(rows)


def nuance_tip(item: dict) -> str:
    tip = (f'<p class="section-subtitle"><span class="ko">{esc(item["tipKo"])}</span>'
           f'<span class="ja">{esc(item["tipJa"])}</span></p>')
    if not item.get('tipCompare'):
        return tip
    first, second = item['tipCompare']
    return (tip + '<div class="nuance-compare">'
            f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(first["whenKo"])}</b>'
            f'<small>{esc(first["whenJa"])}</small></span><span class="korean">{esc(first["ko"])}</span>'
            f'<span class="translation">{esc(first["ja"])}</span></div>'
            '<div class="nuance-or"><span>상황에 따라 <small>場面で選ぶ</small></span></div>'
            f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(second["whenKo"])}</b>'
            f'<small>{esc(second["whenJa"])}</small></span><span class="korean">{esc(second["ko"])}</span>'
            f'<span class="translation">{esc(second["ja"])}</span></div></div>')


def seed_of(*parts: str) -> int:
    """A stable integer for a string, so re-rendering never churns the tree.

    random without a seed would reshuffle every deck on every run; the diff
    would then be unreviewable and a re-render could not be told apart from an
    edit.  The sentence itself is the seed, so the same sentence always lands
    the same way and a different sentence lands differently.
    """
    digest = hashlib.sha256(''.join(parts).encode('utf-8')).digest()
    return int.from_bytes(digest, 'big')


def scramble(items: list[str]) -> list[str]:
    """Deterministically disorder chips — never identity, never last-to-front.

    The old ``[groups[-1], *groups[:-1]]`` was a fixed rotation: 360 of 360
    rows in these courses put the last chunk first, so "move the first chip to
    the end" solved every row without reading any Korean.  Both of those
    orderings are removed from the candidate set rather than merely made
    unlikely, because with three chunks an unlucky hash would otherwise
    reproduce the tell often enough to be learnable.
    """
    return [items[i] for i in scramble_order(items)]


def scramble_order(items: list[str]) -> tuple[int, ...]:
    """The permutation `scramble` picks, so pairs can follow the same one.

    Seeded from the chunk text alone. A chip's reading must not change which
    order the chips come out in — otherwise adding readings would reshuffle
    thirty already-reviewed decks.
    """
    n = len(items)
    identity = tuple(range(n))
    rotation = (n - 1, *range(n - 1))
    candidates = [p for p in permutations(range(n)) if p not in (identity, rotation)]
    if not candidates:                      # unreachable: chunks are 3 or 4
        return identity
    return candidates[seed_of(*items) % len(candidates)]


def scramble_pairs(pairs: list[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
    """Disorder (chunk, reading) pairs exactly as `scramble` would the chunks."""
    order = scramble_order([chunk for chunk, _ in pairs])
    return [pairs[i] for i in order]


def parse_chunks(ko: str, where: str) -> tuple[list[str], str]:
    """Split an authored ``가 | 나 | 다`` row into chips plus its graded answer."""
    answer = TRAILING_PUNCT.sub('', ko.replace(CHUNK_SEP, ' ')).strip()
    answer = re.sub(r'\s+', ' ', answer)
    pieces = [piece.strip() for piece in TRAILING_PUNCT.sub('', ko).split(CHUNK_SEP)]
    if any(not piece for piece in pieces):
        raise ManifestError(f'{where}: an empty chunk — check the "{CHUNK_SEP}" marks in {ko!r}')
    low, high = CHUNK_RANGE
    if not low <= len(pieces) <= high:
        raise ManifestError(
            f'{where}: {len(pieces)} chunks in {ko!r}; reorder takes {low}–{high} meaning units '
            f'(mark them with "{CHUNK_SEP}")')
    if norm(''.join(pieces)) != norm(answer):
        raise ManifestError(f'{where}: chunks {pieces} do not rebuild {answer!r}')
    return pieces, answer


def parse_blank(ko: str, where: str) -> tuple[str, str, str]:
    """Split an authored ``제 최애는 [민지예요].`` row into before / blank / after."""
    found = BLANK_RE.findall(ko)
    if len(found) != 1:
        raise ManifestError(
            f'{where}: {len(found)} blanks marked in {ko!r}; mark exactly one with [ ]')
    blank = found[0].strip()
    if not blank:
        raise ManifestError(f'{where}: the blank is empty in {ko!r}')
    before, after = BLANK_RE.split(ko, 1)[0], BLANK_RE.split(ko, 1)[2]
    if not norm(before + after):
        raise ManifestError(
            f'{where}: the blank swallows the whole sentence in {ko!r}; '
            'a blank targets only the pattern being practiced')
    return before, blank, after


def mask_blank(yomi: str | None, where: str) -> str | None:
    """A reading supports the visible words, so the blank's reading is hidden."""
    if not yomi:
        return None
    if len(BLANK_RE.findall(yomi)) != 1:
        raise ManifestError(
            f'{where}: the yomi {yomi!r} must mark the same blank with [ ] '
            f'(it is rendered as {BLANK_YOMI})')
    return BLANK_RE.sub(BLANK_YOMI, yomi, count=1)


def rows_of(part: dict, field: str, where: str) -> list:
    rows = part.get(field)
    if rows is None:
        raise ManifestError(f'{where}: missing {field}')
    if not isinstance(rows, list) or len(rows) != ROWS_PER_ACTIVITY:
        raise ManifestError(
            f'{where}: {field} holds {len(rows) if isinstance(rows, list) else "no"} rows; '
            f'{ROWS_PER_ACTIVITY} are required')
    return rows


def chunk_readings(yomi: str | None, pieces: list[str], where: str) -> list[str | None]:
    """Line each chunk up with its own kana reading, or give every chunk none.

    A chip is a thing the learner is asked to say, so below 중급 it carries a
    reading like every other spoken Korean in the deck — `deltas-kr.md`, and the
    eleven hand-authored sub-중급 contextual decks all do it this way, one
    `.yomi` inside each `.choice`. This renderer discarded the reading outright
    and shipped thirty decks whose chips a 초급 learner may not be able to
    decode.

    The reading is marked with the same `|` as the Korean so the two cannot
    drift: a row that splits its chunks one way and its reading another is an
    error here rather than a silently misaligned chip.
    """
    if not yomi:
        return [None] * len(pieces)
    readings = [piece.strip() for piece in yomi.split(CHUNK_SEP)]
    if len(readings) != len(pieces):
        raise ManifestError(
            f'{where}: {len(pieces)} chunks but {len(readings)} reading(s) — mark the '
            f'reading with "{CHUNK_SEP}" at the same places as the Korean')
    if any(not reading for reading in readings):
        raise ManifestError(f'{where}: an empty reading chunk in {yomi!r}')
    return readings


def reorder_activity(part: str, rows: list, where: str) -> str:
    blocks = []
    for i, value in enumerate(rows, 1):
        ko, ja, yomi = example_values(value)
        spot = f'{where} reorderExamples[{i}]'
        pieces, answer = parse_chunks(ko, spot)
        readings = chunk_readings(yomi, pieces, spot)
        paired = list(zip(pieces, readings))
        chips = ''.join(
            f'<span class="choice" data-item-id="{part}-o{i}-{j}">{esc(chunk)}'
            f'{yomi_span(reading)}</span>'
            for j, (chunk, reading) in enumerate(scramble_pairs(paired), 1)
        )
        blocks.append(f'<div class="task-block"><div class="answer-box small">'
                      f'<span class="answer-label">{esc(ja)}</span>'
                      f'{build_zone(f"{part}-order-{i}", answer)}</div>{chips}</div>')
    return ''.join(blocks)


def fill_activity(part: str, rows: list, where: str) -> str:
    blocks = []
    for i, value in enumerate(rows, 1):
        ko, ja, yomi = example_values(value)
        spot = f'{where} fillExamples[{i}]'
        before, blank, after = parse_blank(ko, spot)
        reading = yomi_span(mask_blank(yomi, spot))
        blocks.append(f'<div class="task-block"><div class="answer-box"><span class="answer-label">'
                      f'{esc(ja)}</span><span class="answer-fill"><span class="korean">'
                      f'{esc(before)}{slot_input(f"{part}-fill-{i}", blank)}{esc(after)}'
                      f'</span>{reading}</span></div></div>')
    return ''.join(blocks)


def translate_activity(part: str, rows: list) -> str:
    blocks = []
    for i, value in enumerate(rows, 1):
        ko, ja, _ = example_values(value)
        blocks.append(f'<div class="task-block"><div class="answer-box"><span class="answer-label">'
                      f'{esc(ja)}</span>{answer_input(f"{part}-translate-{i}", ko)}'
                      f'</div></div>')
    return ''.join(blocks)


def activities(part: str, data: dict, where: str) -> tuple[str, str, str]:
    """Reorder, fill and translate — each from its own authored sentence set."""
    return (reorder_activity(part, rows_of(data, 'reorderExamples', where), where),
            fill_activity(part, rows_of(data, 'fillExamples', where), where),
            translate_activity(part, rows_of(data, 'translateExamples', where)))


def render_lesson(item: dict, course_name: str, final: bool, where: str = '',
                  course_key: str = '') -> str:
    where = where or item['slug']
    p1, p2 = item['p1'], item['p2']
    scene_role = item['incoming']['role']
    p1_role = p1.get('responseRole', scene_role)
    p2_role = p2.get('responseRole', scene_role)
    ending_role = item.get('ending', {}).get('openRole', scene_role)
    teaser_role = scene_role
    def t(role: str, ko: str, ja: str, **kwargs: object) -> str:
        return turn(role, ko, ja, course_name=course_key, **kwargs)

    def ot(role: str, label: str, sync_id: str, **kwargs: object) -> str:
        return open_turn(role, label, sync_id, course_name=course_key, **kwargs)

    scene_turns = [
        t(scene_role, item['incoming']['ko'], item['incoming']['ja']),
        t('나', p1['line'], p1['ja'], yomi=p1.get('yomi')),
        t(p1_role, p1['responseKo'], p1['responseJa']),
        t('나', p2['line'], p2['ja'], yomi=p2.get('yomi')),
        t(p2_role, p2['responseKo'], p2['responseJa']),
    ]
    scene = ''.join(scene_turns)
    complete = ''.join([
        t(scene_role, item['incoming']['ko'], item['incoming']['ja']),
        t('나', p1['line'], p1['ja'], slot='p3-complete-1'),
        t(p1_role, p1['responseKo'], p1['responseJa']),
        t('나', p2['line'], p2['ja'], slot='p3-complete-2'),
        t(p2_role, p2['responseKo'], p2['responseJa']),
    ])
    p1_reorder, p1_fill, p1_translate = activities('p1', p1, f'{where} p1')
    p2_reorder, p2_fill, p2_translate = activities('p2', p2, f'{where} p2')
    pages = [
        episode_card(item, course_name, course_key),
        page('scene', '오늘의 장면', '今日のワンシーン', f'<div class="dialogue">{scene}</div>',
             (item['sceneKo'], item['sceneJa'])),
        (f'<div class="transition-page" data-page-id="lesson-goal"><span class="transition-kicker">목표</span>'
         f'<h2 class="transition-title">오늘의 두 가지 목표 <span class="title-ja">(今日の2つのゴール)</span></h2>'
         f'<p class="section-subtitle"><span class="ko">{esc(item["canDoKo"])}</span><span class="ja">'
         f'{esc(item["canDoJa"])}</span></p><div class="known lines"><div class="known-row">'
         f'<span class="k">{esc(p1["line"])}</span>'
         f'{yomi_span(p1.get("yomi"))}'
         f'<span class="j">{esc(p1["ja"])}</span></div>'
         f'<div class="known-row"><span class="k">{esc(p2["line"])}</span>'
         f'{yomi_span(p2.get("yomi"))}'
         f'<span class="j">'
         f'{esc(p2["ja"])}</span></div></div></div>'),
        page('expressions', '먼저 익힐 표현', '先に覚える表現', model_list(item['expressions']),
             ('먼저 핵심 표현 네 개를 볼게요.', 'まず中心表現を4つ見てみましょう。')),
        transition('part1-intro', 'パート 1', p1['pattern'], '最初の表現', p1['ja'], p1['pattern']),
        page('p1-teach', p1.get('teachTitleKo', '첫 번째 표현'), p1.get('teachTitleJa', '最初の表現'),
             f'<p class="section-subtitle pattern-meaning"><span class="meaning-kicker">뜻과 쓰임 '
             f'<small>意味・使い方</small></span><span class="ko">{esc(p1["meaningKo"])}</span>'
             f'<span class="ja">{esc(p1["meaningJa"])}</span></p><div class="sent-hero">'
             f'<span class="korean">{esc(p1["line"])}</span>'
             f'{yomi_span(p1.get("yomi"))}'
             f'<span class="translation">{esc(p1["ja"])}</span></div>'),
        page('p1-read', '따라 읽기', '声に出して練習', model_list(rows_of(p1, 'readExamples', f'{where} p1')),
             ('이번엔 네 문장을 한 줄씩 소리 내어 읽어 볼까요?', '今度は4つの文を、1行ずつ声に出して読んでみましょうか。')),
        page('p1-rule', '모양 확인', '形を確認',
             rule_visual(p1),
             (p1.get('ruleKo', '핵심 표현부터 볼게요.'), p1.get('ruleJa', 'まず中心表現を見てみましょう。'))),
    ]
    if p1.get('choices'):
        pages.append(page('p1-choose', '맞는 형태 고르기', '正しい形を選ぼう',
                          f'<div class="choose-list">{choose_activity("p1", p1["choices"], f"{where} p1")}</div>',
                          ('맞는 형태를 골라 보세요.', '正しい形を選んでみましょう。')))
    pages.extend([
        page('p1-reorder', '문장 만들기', '文を組み立てよう', p1_reorder,
             ('이번엔 흩어진 낱말을 순서대로 놓아 대사를 완성해 볼까요?', '今度はばらばらのことばを順番に並べて、セリフを完成させてみましょうか。')),
        page('p1-fill', '빈칸 채우기', '穴埋め練習', p1_fill,
             ('핵심 문장을 완성해 보세요.', '中心文を完成させましょう。')),
        page('p1-translate', '한국어로 말하기', '韓国語で言おう', p1_translate,
             ('이번엔 일본어만 보고 한국어 대사로 바꿔 말해 볼까요?', '今度は日本語だけを見て、韓国語のセリフに変えて言ってみましょうか。')),
        page('p1-write', '내 경험을 말하기', '自分の経験を話そう',
             feedback_activity('p1-write-answer', '自分の状況で一文作ろう'),
             (p1.get('writeKo', '이번엔 같은 표현으로 자신의 경험을 한 문장 만들어 볼까요?'), p1.get('writeJa', '今度は同じ表現で、自分の経験を1文話してみましょうか。'))),
        transition('part2-intro', 'パート 2', p2['pattern'], '次の表現', p2['ja'], p2['pattern']),
        page('p2-teach', p2.get('teachTitleKo', '두 번째 표현'), p2.get('teachTitleJa', '次の表現'),
             f'<p class="section-subtitle pattern-meaning"><span class="meaning-kicker">뜻과 쓰임 '
             f'<small>意味・使い方</small></span><span class="ko">{esc(p2["meaningKo"])}</span>'
             f'<span class="ja">{esc(p2["meaningJa"])}</span></p><div class="sent-hero">'
             f'<span class="korean">{esc(p2["line"])}</span>'
             f'{yomi_span(p2.get("yomi"))}'
             f'<span class="translation">{esc(p2["ja"])}</span></div>'),
        page('p2-read', '따라 읽기', '声に出して練習', model_list(rows_of(p2, 'readExamples', f'{where} p2')),
             ('이번엔 네 문장을 한 줄씩 소리 내어 읽어 볼까요?', '今度は4つの文を、1行ずつ声に出して読んでみましょうか。')),
        page('p2-rule', '모양 확인', '形を確認',
             rule_visual(p2),
             (p2.get('ruleKo', '핵심 표현부터 볼게요.'), p2.get('ruleJa', 'まず中心表現を見てみましょう。'))),
    ])
    if p2.get('choices'):
        pages.append(page('p2-choose', '맞는 형태 고르기', '正しい形を選ぼう',
                          f'<div class="choose-list">{choose_activity("p2", p2["choices"], f"{where} p2")}</div>',
                          ('맞는 형태를 골라 보세요.', '正しい形を選んでみましょう。')))
    pages.extend([
        page('p2-reorder', '문장 만들기', '文を組み立てよう', p2_reorder,
             ('이번엔 흩어진 낱말을 순서대로 놓아 대사를 완성해 볼까요?', '今度はばらばらのことばを順番に並べて、セリフを完成させてみましょうか。')),
        page('p2-fill', '빈칸 채우기', '穴埋め練習', p2_fill,
             ('핵심 문장을 완성해 보세요.', '中心文を完成させましょう。')),
        page('p2-translate', '한국어로 말하기', '韓国語で言おう', p2_translate,
             ('이번엔 일본어만 보고 한국어 대사로 바꿔 말해 볼까요?', '今度は日本語だけを見て、韓国語のセリフに変えて言ってみましょうか。')),
        page('p2-write', '내 경험을 말하기', '自分の経験を話そう',
             feedback_activity('p2-write-answer', '自分の状況で一文作ろう'),
             (p2.get('writeKo', '이번엔 같은 표현으로 자신의 경험을 한 문장 만들어 볼까요?'), p2.get('writeJa', '今度は同じ表現で、自分の経験を1文話してみましょうか。'))),
        transition('part3-intro', 'パート 3', '장면으로 돌아가기', '場面に戻ろう',
                   '二つの表現を一つの会話で使います。', '장면 복습'),
        page('p3-model', '장면 다시 읽기', 'シーンをもう一度', f'<div class="dialogue">{scene}</div>',
             ('지금까지 배운 표현으로 처음 장면을 다시 연기해 볼까요?', 'これまでに習った表現で、最初の場面をもう一度演じてみましょうか。')),
        page('p3-complete', '장면 완성하기', '場面を完成しよう', f'<div class="dialogue">{complete}</div>',
             ('핵심 대사 두 개를 완성하고 장면을 이어 보세요.', '中心のセリフを2つ完成させ、場面を続けてみましょう。')),
        page('p3-freetalk', '자유 대화', 'フリートーク',
             f'<div class="dialogue">{t("선생님", item.get("freeQuestionKo", item["canDoKo"]), item.get("freeQuestionJa", item["canDoJa"]))}'
             f'{ot("나", item.get("freePromptJa", "自分の経験を韓国語で話そう"), "p3-freetalk-answer", tall=True)}'
             f'{ot("나", item.get("tutorQuestionJa", "先生にも同じことを聞こう"), "p3-freetalk-question", seed=item.get("tutorQuestionKo", "선생님은 어때요?"))}'
             f'{ot("선생님", "先生の答え", "p3-freetalk-tutor-answer")}</div>',
             ('자기 이야기를 한 뒤, 저한테도 물어보세요.', '自分の話をしたら、私にも聞いてみてください。')),
        page('native-tip', '원어민 팁', 'ネイティブのひとこと',
             nuance_tip(item)),
    ])
    if final:
        ending_turns = [
            t(ending_role, item['ending']['openKo'], item['ending']['openJa']),
            t('나', p1['line'], p1['ja'], slot='ending-1'),
            t(p1_role, p1['responseKo'], p1['responseJa']),
            t('나', p2['line'], p2['ja'], slot='ending-2'),
            t(p2_role, p2['responseKo'], p2['responseJa']),
            t('나', item['ending']['confirmKo'], item['ending']['confirmJa']),
            t(item['ending'].get('closeRole', p2_role), item['ending']['closeKo'], item['ending']['closeJa']),
        ]
        pages.append(page('course-epilogue', '코스 에필로그', 'コース・エピローグ',
                          f'<div class="dialogue">{"".join(ending_turns)}</div>',
                          (item['ending']['subtitleKo'], item['ending']['subtitleJa'])))
    else:
        teaser = [
            # Reuse the scene's real prompt so the learner produces each target once.
            # A prewritten summary here duplicated both target lines before the slots.
            t(teaser_role, item['incoming']['ko'], item['incoming']['ja']),
            t('나', p1['line'], p1['ja'], slot='next-1'),
            t(p1_role, p1['responseKo'], p1['responseJa']),
            t('나', p2['line'], p2['ja'], slot='next-2'),
            t(p2_role, p2['responseKo'], p2['responseJa']),
            t(item['teaser'].get('bridgeRole', p2_role), item['teaser']['bridgeKo'], item['teaser']['bridgeJa']),
            t(item['nextHook']['role'], item['nextHook']['ko'], item['nextHook']['ja']),
        ]
        pages.append(page(f'episode{item["number"] + 1}-taste', '다음 장면', '次の場面',
                          f'<div class="dialogue">{"".join(teaser)}</div>',
                          (item['teaser']['subtitleKo'], item['teaser']['subtitleJa'])))
    return '\n    '.join(pages)


REPO = pathlib.Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TOC = KR / "tracks/3-contextual-korean/toc"


def part_report(part: dict, spot: str) -> list[str]:
    """Every reason this part cannot be rendered, in one pass."""
    missing: list[str] = []
    problems: list[str] = []
    for field in ACTIVITY_FIELDS:
        try:
            rows = rows_of(part, field, spot)
        except ManifestError as exc:
            (missing.append(field) if part.get(field) is None else problems.append(str(exc)))
            continue
        for i, value in enumerate(rows, 1):
            place = f'{spot} {field}[{i}]'
            try:
                ko, _ja, yomi = example_values(value)
                if field == 'reorderExamples':
                    parse_chunks(ko, place)
                elif field == 'fillExamples':
                    parse_blank(ko, place)
                    mask_blank(yomi, place)
            except ManifestError as exc:
                problems.append(str(exc))
            except (KeyError, IndexError, TypeError) as exc:
                problems.append(f'{place}: not a [ko, ja, yomi?] row ({exc})')
    if missing:
        problems.insert(0, f'{spot}: missing {", ".join(missing)}')
    return problems


def manifest_report(data: dict) -> tuple[int, list[str]]:
    parts = 0
    problems: list[str] = []
    for item in data['lessons']:
        for key in ('p1', 'p2'):
            parts += 1
            problems += part_report(item.get(key) or {}, f'{item["slug"]} {key}')
    return parts, problems


def check(paths: list[pathlib.Path]) -> int:
    """Report which manifests still lack the four authored sentence sets."""
    parts = ready = 0
    for path in paths:
        data = json.loads(path.read_text())
        found, problems = manifest_report(data)
        blocked = {line.split(':')[0] for line in problems}
        parts += found
        ready += found - len(blocked)
        print(f'{data["course"]} · {found} parts · {found - len(blocked)} ready')
        for line in problems:
            print(f'  {line}')
    print(f'\n{len(paths)} manifest(s) · {parts} parts · {ready} ready · {parts - ready} to author')
    return 1 if ready < parts else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('manifest', nargs='*', type=pathlib.Path,
                        help='authoring-manifest.json files (default with --check: all six)')
    parser.add_argument('--check', action='store_true',
                        help='report the parts still missing a sentence set; write nothing')
    args = parser.parse_args()
    paths = args.manifest or sorted(TOC.glob('*/authoring-manifest.json'))
    if args.check:
        return check(paths)
    if not args.manifest:
        parser.error('name a manifest to render (--check may be run over all of them)')
    for path in paths:
        render(json.loads(path.read_text()))
    return 0


def render(data: dict) -> None:
    course = KR / 'tracks/3-contextual-korean/courses' / data['course']
    # Refuse the whole course before writing any of it — half a course rendered
    # from a half-authored manifest is worse than a course that did not move.
    parts, problems = manifest_report(data)
    if problems:
        raise ManifestError(f'{data["course"]}: {len(problems)} problem(s) in {parts} parts\n  '
                            + '\n  '.join(problems))
    for item in data['lessons']:
        item.setdefault('learnerRoleJa', data.get('learnerRoleJa', 'この場面で話すあなた'))
        item.setdefault('partnerRoleJa', data.get('partnerRoleJa', '会話の相手'))
        target = course / 'lessons' / item['slug'] / 'lesson.html'
        source = target.read_text()
        start = source.index('  <div class="phone">') + len('  <div class="phone">')
        end = source.index('\n  </div>', start)
        authored = '\n    ' + render_lesson(item, data['courseTitleKo'], item['number'] == 10,
                                                f'{data["course"]} {item["slug"]}',
                                                data['course']) + '\n'
        rendered = source[:start] + authored + source[end:]
        # The path is computed, not written down. The literal here used to be
        # `../../../../../../runtime/js/yomi.js` — six levels to a directory that
        # stopped existing when `runtime/` became `shared/`. Worse, the dedupe
        # test compared against that same dead string, so it never recognised the
        # correct tag the deck already carried and appended a second, broken one
        # on every render.
        depth = len(target.parent.relative_to(REPO).parts)
        yomi_script = f'<script src="{"../" * depth}shared/js/yomi.js"></script>'
        if 'class="yomi"' in authored and 'js/yomi.js' not in rendered:
            rendered = rendered.replace('\n\n</body>', f'  {yomi_script}\n\n\n</body>')
        target.write_text(rendered)
        print(f'wrote {target}')


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ManifestError as failure:
        raise SystemExit(f'✗ {failure}')
