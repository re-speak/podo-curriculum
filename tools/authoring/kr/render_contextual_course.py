#!/usr/bin/env python3
"""Render fully authored contextual lessons from a reviewed course manifest.

This is deliberately a renderer, not a content generator.  Every Korean line,
Japanese translation, teaching explanation, reaction and continuity hook lives
in the manifest and is reviewed there.  The renderer only repeats those facts
through the canonical 26-page interaction arc without hand-copying runtime
markup sixty times.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re


AVATAR = ('<span class="avatar icon"><svg aria-hidden="true" viewBox="0 0 24 24">'
          '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2.5c-4.7 0-8.5 '
          '2.6-8.5 5.8V22h17v-1.7c0-3.2-3.8-5.8-8.5-5.8Z" fill="currentColor"/>'
          '</svg></span>')
HANA = '<img alt="" class="avatar" src="https://respeak-lemonade.s3.ap-northeast-2.amazonaws.com/test/hana-avatar.jpg"/>'


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


def turn(role: str, ko: str, ja: str, *, slot: str | None = None, yomi: str | None = None) -> str:
    mine = role == "나"
    who = AVATAR if mine else HANA
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


def open_turn(role: str, label: str, sync_id: str, *, seed: str = "", tall: bool = False) -> str:
    """Render a genuinely editable free response, rather than an exact-answer slot."""
    mine = role == "나"
    who = AVATAR if mine else HANA
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


def episode_card(item: dict, course_name: str) -> str:
    return (f'<div class="transition-page episode-card" data-page-id="episode-card" '
            f'data-act="{esc(item["titleKo"])}"><span class="transition-kicker">'
            f'{esc(course_name)} · 제{item["number"]}화</span><h2 class="transition-title">'
            f'{esc(item["titleKo"])}</h2><p class="transition-copy">{esc(item["sceneJa"])}</p>'
            f'<div class="scene-cast"><span class="cast-row">{AVATAR}<span class="cast-who">나'
            f'<small>{esc(item.get("learnerRoleJa", "K-POPファン・あなたの役"))}</small></span></span>'
            f'<span class="cast-row">{HANA}<span class="cast-who">{esc(item["incoming"]["role"])}'
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


def choose_activity(part: str, choices: list[dict]) -> str:
    rows = []
    for i, row in enumerate(choices, 1):
        options = []
        for j, option in enumerate(row['options']):
            correct = ' data-correct=""' if j == row['correct'] else ''
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


def chunks(sentence: str) -> list[str]:
    words = re.sub(r'[.!?]$', '', sentence).split()
    count = 4 if len(words) >= 7 else 3
    count = min(count, len(words))
    groups: list[str] = []
    for i in range(count):
        start = round(i * len(words) / count)
        end = round((i + 1) * len(words) / count)
        groups.append(' '.join(words[start:end]))
    return [groups[-1], *groups[:-1]]


def activities(part: str, examples: list[dict]) -> tuple[str, str, str]:
    reorder = []
    fill = []
    translate = []
    for i, value in enumerate(examples, 1):
        ko, ja, yomi = example_values(value)
        answer = re.sub(r'[.!?]$', '', ko)
        ko_chunks = chunks(ko)
        chips = ''.join(
            f'<span class="choice" data-item-id="{part}-o{i}-{j}">{esc(chunk)}</span>'
            for j, chunk in enumerate(ko_chunks, 1)
        )
        reorder.append(f'<div class="task-block"><div class="answer-box small">'
                       f'<span class="answer-label">{esc(ja)}</span>'
                       f'{build_zone(f"{part}-order-{i}", answer)}</div>{chips}</div>')
        fill.append(f'<div class="task-block"><div class="answer-box"><span class="answer-label">'
                    f'{esc(ja)}</span><span class="answer-fill"><span class="korean">'
                    f'{slot_input(f"{part}-fill-{i}", ko)}</span></span>'
                    f'{yomi_span("＿＿＿" if yomi else None)}'
                    f'</div></div>')
        translate.append(f'<div class="task-block"><div class="answer-box"><span class="answer-label">'
                         f'{esc(ja)}</span>{answer_input(f"{part}-translate-{i}", ko)}'
                         f'</div></div>')
    return ''.join(reorder), ''.join(fill), ''.join(translate)


def render_lesson(item: dict, course_name: str, final: bool) -> str:
    p1, p2 = item['p1'], item['p2']
    scene_role = item['incoming']['role']
    p1_role = p1.get('responseRole', scene_role)
    p2_role = p2.get('responseRole', scene_role)
    ending_role = item.get('ending', {}).get('openRole', scene_role)
    teaser_role = scene_role
    scene_turns = [
        turn(scene_role, item['incoming']['ko'], item['incoming']['ja']),
        turn('나', p1['line'], p1['ja'], yomi=p1.get('yomi')),
        turn(p1_role, p1['responseKo'], p1['responseJa']),
        turn('나', p2['line'], p2['ja'], yomi=p2.get('yomi')),
        turn(p2_role, p2['responseKo'], p2['responseJa']),
    ]
    scene = ''.join(scene_turns)
    complete = ''.join([
        turn(scene_role, item['incoming']['ko'], item['incoming']['ja']),
        turn('나', p1['line'], p1['ja'], slot='p3-complete-1'),
        turn(p1_role, p1['responseKo'], p1['responseJa']),
        turn('나', p2['line'], p2['ja'], slot='p3-complete-2'),
        turn(p2_role, p2['responseKo'], p2['responseJa']),
    ])
    p1_reorder, p1_fill, p1_translate = activities('p1', p1['examples'])
    p2_reorder, p2_fill, p2_translate = activities('p2', p2['examples'])
    pages = [
        episode_card(item, course_name),
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
             ('장면에 필요한 네 표현을 먼저 확인해요.', '場面に必要な4つの表現を先に確認します。')),
        transition('part1-intro', 'パート 1', p1['pattern'], '最初の表現', p1['ja'], p1['pattern']),
        page('p1-teach', p1.get('teachTitleKo', '첫 번째 표현'), p1.get('teachTitleJa', '最初の表現'),
             f'<p class="section-subtitle pattern-meaning"><span class="meaning-kicker">뜻과 쓰임 '
             f'<small>意味・使い方</small></span><span class="ko">{esc(p1["meaningKo"])}</span>'
             f'<span class="ja">{esc(p1["meaningJa"])}</span></p><div class="sent-hero">'
             f'<span class="korean">{esc(p1["line"])}</span>'
             f'{yomi_span(p1.get("yomi"))}'
             f'<span class="translation">{esc(p1["ja"])}</span></div>'),
        page('p1-read', '따라 읽기', '声に出して練習', model_list(p1['examples']),
             ('네 문장을 천천히 따라 읽어 보세요.', '4つの文をゆっくり読んでください。')),
        page('p1-rule', '모양 확인', '形を確認',
             rule_visual(p1),
             (p1.get('ruleKo', '문장 속 핵심 표현을 한 덩어리로 확인해요.'), p1.get('ruleJa', '文の中心表現をひとかたまりで確認します。'))),
    ]
    if p1.get('choices'):
        pages.append(page('p1-choose', '맞는 형태 고르기', '正しい形を選ぼう',
                          f'<div class="choose-list">{choose_activity("p1", p1["choices"])}</div>',
                          ('배운 형태 변화에 맞는 쪽을 골라 보세요.', '習った形の変化に合うほうを選びましょう。')))
    pages.extend([
        page('p1-reorder', '문장 만들기', '文を組み立てよう', p1_reorder,
             ('흩어진 덩어리를 자연스러운 문장으로 만들어 보세요.', 'ばらばらのかたまりを自然な文に並べましょう。')),
        page('p1-fill', '빈칸 채우기', '穴埋め練習', p1_fill,
             ('핵심 문장을 완성해 보세요.', '中心文を完成させましょう。')),
        page('p1-translate', '한국어로 말하기', '韓国語で言おう', p1_translate,
             ('일본어를 보고 문장 전체를 한국어로 말해 보세요.', '日本語を見て文全体を韓国語で言いましょう。')),
        page('p1-write', '내 이야기로 바꾸기', '自分の話に変えよう',
             feedback_activity('p1-write-answer', '自分の状況で一文作ろう'),
             (p1.get('writeKo', '같은 표현으로 내 상황에 맞는 문장을 만들어 보세요.'), p1.get('writeJa', '同じ表現で自分の状況に合う文を作りましょう。'))),
        transition('part2-intro', 'パート 2', p2['pattern'], '次の表現', p2['ja'], p2['pattern']),
        page('p2-teach', p2.get('teachTitleKo', '두 번째 표현'), p2.get('teachTitleJa', '次の表現'),
             f'<p class="section-subtitle pattern-meaning"><span class="meaning-kicker">뜻과 쓰임 '
             f'<small>意味・使い方</small></span><span class="ko">{esc(p2["meaningKo"])}</span>'
             f'<span class="ja">{esc(p2["meaningJa"])}</span></p><div class="sent-hero">'
             f'<span class="korean">{esc(p2["line"])}</span>'
             f'{yomi_span(p2.get("yomi"))}'
             f'<span class="translation">{esc(p2["ja"])}</span></div>'),
        page('p2-read', '따라 읽기', '声に出して練習', model_list(p2['examples']),
             ('네 문장을 천천히 따라 읽어 보세요.', '4つの文をゆっくり読んでください。')),
        page('p2-rule', '모양 확인', '形を確認',
             rule_visual(p2),
             (p2.get('ruleKo', '문장 속 핵심 표현을 한 덩어리로 확인해요.'), p2.get('ruleJa', '文の中心表現をひとかたまりで確認します。'))),
    ])
    if p2.get('choices'):
        pages.append(page('p2-choose', '맞는 형태 고르기', '正しい形を選ぼう',
                          f'<div class="choose-list">{choose_activity("p2", p2["choices"])}</div>',
                          ('배운 형태 변화에 맞는 쪽을 골라 보세요.', '習った形の変化に合うほうを選びましょう。')))
    pages.extend([
        page('p2-reorder', '문장 만들기', '文を組み立てよう', p2_reorder,
             ('흩어진 덩어리를 자연스러운 문장으로 만들어 보세요.', 'ばらばらのかたまりを自然な文に並べましょう。')),
        page('p2-fill', '빈칸 채우기', '穴埋め練習', p2_fill,
             ('핵심 문장을 완성해 보세요.', '中心文を完成させましょう。')),
        page('p2-translate', '한국어로 말하기', '韓国語で言おう', p2_translate,
             ('일본어를 보고 문장 전체를 한국어로 말해 보세요.', '日本語を見て文全体を韓国語で言いましょう。')),
        page('p2-write', '내 이야기로 바꾸기', '自分の話に変えよう',
             feedback_activity('p2-write-answer', '自分の状況で一文作ろう'),
             (p2.get('writeKo', '같은 표현으로 내 상황에 맞는 문장을 만들어 보세요.'), p2.get('writeJa', '同じ表現で自分の状況に合う文を作りましょう。'))),
        transition('part3-intro', 'パート 3', '장면으로 돌아가기', '場面に戻ろう',
                   '二つの表現を一つの会話で使います。', '장면 복습'),
        page('p3-model', '장면 다시 읽기', 'シーンをもう一度', f'<div class="dialogue">{scene}</div>',
             ('처음 장면을 같은 순서로 다시 읽어요.', '最初の場面を同じ順番でもう一度読みます。')),
        page('p3-complete', '장면 완성하기', '場面を完成しよう', f'<div class="dialogue">{complete}</div>',
             ('두 핵심 대사를 완성해 장면 전체를 이어 보세요.', '2つの中心せりふを完成させましょう。')),
        page('p3-freetalk', '자유 대화', 'フリートーク',
             f'<div class="dialogue">{turn("선생님", item.get("freeQuestionKo", item["canDoKo"]), item.get("freeQuestionJa", item["canDoJa"]))}'
             f'{open_turn("나", item.get("freePromptJa", "自分の経験を韓国語で話そう"), "p3-freetalk-answer", tall=True)}'
             f'{open_turn("나", item.get("tutorQuestionJa", "先生にも同じことを聞こう"), "p3-freetalk-question", seed=item.get("tutorQuestionKo", "선생님은 어때요?"))}'
             f'{open_turn("선생님", "先生の答え", "p3-freetalk-tutor-answer")}</div>',
             ('내 이야기를 말하고 선생님에게도 같은 질문을 해 보세요.', '自分の話をし、先生にも同じ質問をしましょう。')),
        page('native-tip', '원어민 팁', 'ネイティブのひとこと',
             nuance_tip(item)),
    ])
    if final:
        ending_turns = [
            turn(ending_role, item['ending']['openKo'], item['ending']['openJa']),
            turn('나', p1['line'], p1['ja'], slot='ending-1'),
            turn(p1_role, p1['responseKo'], p1['responseJa']),
            turn('나', p2['line'], p2['ja'], slot='ending-2'),
            turn(p2_role, p2['responseKo'], p2['responseJa']),
            turn('나', item['ending']['confirmKo'], item['ending']['confirmJa']),
            turn(item['ending'].get('closeRole', p2_role), item['ending']['closeKo'], item['ending']['closeJa']),
        ]
        pages.append(page('course-epilogue', '코스 에필로그', 'コース・エピローグ',
                          f'<div class="dialogue">{"".join(ending_turns)}</div>',
                          (item['ending']['subtitleKo'], item['ending']['subtitleJa'])))
    else:
        teaser = [
            # Reuse the scene's real prompt so the learner produces each target once.
            # A prewritten summary here duplicated both target lines before the slots.
            turn(teaser_role, item['incoming']['ko'], item['incoming']['ja']),
            turn('나', p1['line'], p1['ja'], slot='next-1'),
            turn(p1_role, p1['responseKo'], p1['responseJa']),
            turn('나', p2['line'], p2['ja'], slot='next-2'),
            turn(p2_role, p2['responseKo'], p2['responseJa']),
            turn(item['teaser'].get('bridgeRole', p2_role), item['teaser']['bridgeKo'], item['teaser']['bridgeJa']),
            turn(item['nextHook']['role'], item['nextHook']['ko'], item['nextHook']['ja']),
        ]
        pages.append(page(f'episode{item["number"] + 1}-taste', '다음 장면', '次の場面',
                          f'<div class="dialogue">{"".join(teaser)}</div>',
                          (item['teaser']['subtitleKo'], item['teaser']['subtitleJa'])))
    return '\n    '.join(pages)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=pathlib.Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text())
    root = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"
    course = root / 'tracks/3-contextual-korean/courses' / data['course']
    for index, item in enumerate(data['lessons']):
        item.setdefault('learnerRoleJa', data.get('learnerRoleJa', 'この場面で話すあなた'))
        item.setdefault('partnerRoleJa', data.get('partnerRoleJa', '会話の相手'))
        target = course / 'lessons' / item['slug'] / 'lesson.html'
        source = target.read_text()
        start = source.index('  <div class="phone">') + len('  <div class="phone">')
        end = source.index('\n  </div>', start)
        authored = '\n    ' + render_lesson(item, data['courseTitleKo'], item['number'] == 10) + '\n'
        rendered = source[:start] + authored + source[end:]
        yomi_script = '<script src="../../../../../../runtime/js/yomi.js"></script>'
        if 'class="yomi"' in authored and yomi_script not in rendered:
            rendered = rendered.replace('\n\n</body>', f'  {yomi_script}\n\n\n</body>')
        target.write_text(rendered)
        print(f'wrote {target}')


if __name__ == '__main__':
    main()
