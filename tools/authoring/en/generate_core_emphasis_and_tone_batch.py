#!/usr/bin/env python3
"""Generate the explicit CORE-103--112 Emphasis and Tone course batch.

All pedagogical and language decisions live in this narrow source.  The shared
Core renderer is used only for the already-approved component and page arc.
"""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_core_course_batch as core
import generate_core_nuance_at_work_batch as approved
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-emphasis-and-tone"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
NUMBERS = tuple(range(103, 113))

NARROW_GROWING_INPUT_CSS = """/* CORE103--112: keep complete learner answers visible at phone widths. */
textarea.space-input,
textarea.free-input,
textarea.phrase-input {
  box-sizing: border-box;
  block-size: auto;
  min-block-size: 2.75em;
  max-block-size: none;
  overflow: auto !important;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  resize: none;
}
textarea.phrase-input {
  margin-block: 4px;
}
"""

NARROW_GROWING_INPUT_JS = """/* CORE103--112: grow synced textareas after local or remote value changes. */
(() => {
  const selector = 'textarea.space-input, textarea.free-input, textarea.phrase-input';
  const grow = (control) => {
    control.style.height = 'auto';
    const borders = control.offsetHeight - control.clientHeight;
    control.style.height = `${control.scrollHeight + borders}px`;
    control.style.overflow = 'auto';
    for (let pass = 0; pass < 3 && control.scrollHeight > control.clientHeight + 1; pass += 1) {
      control.style.height = `${control.offsetHeight + control.scrollHeight - control.clientHeight}px`;
    }
  };
  const growAll = () => document.querySelectorAll(selector).forEach(grow);
  const queueGrow = (control) => {
    grow(control);
    requestAnimationFrame(() => {
      grow(control);
      requestAnimationFrame(() => grow(control));
    });
  };
  document.addEventListener('input', (event) => {
    if (event.target.matches?.(selector)) queueGrow(event.target);
  });
  document.addEventListener('change', (event) => {
    if (event.target.matches?.(selector)) queueGrow(event.target);
  });
  const widths = new WeakMap();
  const widthObserver = new ResizeObserver((entries) => {
    for (const {target, contentRect} of entries) {
      if (widths.get(target) !== contentRect.width) {
        widths.set(target, contentRect.width);
        queueGrow(target);
      }
    }
  });
  document.querySelectorAll(selector).forEach((control) => widthObserver.observe(control));
  const phone = document.querySelector('.phone');
  if (phone) {
    const pageObserver = new MutationObserver(() => {
      phone.querySelectorAll(`.pg-on ${selector}`).forEach(queueGrow);
    });
    pageObserver.observe(phone, {subtree: true, attributes: true, attributeFilter: ['class']});
  }
  window.addEventListener('load', growAll);
  requestAnimationFrame(growAll);
})();
"""


def rows(*items):
    return items


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


LESSONS = {
    103: dict(
        slug="what-worries-me-most-is-the-cost", title="What worries me most is the cost",
        ko="가장 걱정되는 건 비용이에요", ja="一番心配なのは費用です",
        goal=("Put your main concern first, then focus your suggestion.", "一番の懸念を先に示し、提案の焦点をはっきりさせましょう。"),
        p1=rows(
            ("{t}What worries me most is{/t} the cost.", "{t}一番心配なのは{/t}費用です。", "What worries me|most|is|the cost."),
            ("{t}What worries me most is{/t} the schedule.", "{t}一番心配なのは{/t}日程です。", "What worries me|most|is|the schedule."),
            ("{t}What worries me most is{/t} the deadline.", "{t}一番心配なのは{/t}期限です。", "What worries me|most|is|the deadline."),
            ("{t}What worries me most is{/t} the quality.", "{t}一番心配なのは{/t}品質です。", "What worries me|most|is|the quality."),
        ),
        p2=rows(
            ("{t}What I'd suggest is{/t} waiting a week.", "{t}私が提案したいのは{/t}、1週間待つことです。", "What I'd suggest|is|waiting|a week."),
            ("{t}What I'd suggest is{/t} checking the data.", "{t}私が提案したいのは{/t}、データを確認することです。", "What I'd suggest|is|checking|the data."),
            ("{t}What I'd suggest is{/t} asking the client.", "{t}私が提案したいのは{/t}、顧客に聞くことです。", "What I'd suggest|is|asking|the client."),
            ("{t}What I'd suggest is{/t} starting tomorrow.", "{t}私が提案したいのは{/t}、明日始めることです。", "What I'd suggest|is|starting|tomorrow."),
        ),
        rules=(("Keep the whole What-clause before is; the important point comes after is.", "What 節全体を is の前に置き、重要な点を is の後ろに置きます。"), ("After What I'd suggest is, use a noun phrase or an -ing action.", "What I'd suggest is の後ろには、名詞句または -ing の行動を置きます。")),
        prompt=("Name a real concern and suggestion, or say you have no decision to discuss today.", "実際の懸念と提案を言うか、今日は相談する判断がないと伝えましょう。"),
    ),
    104: dict(
        slug="its-the-timing-that-matters", title="It's the timing that matters",
        ko="중요한 건 타이밍이에요", ja="重要なのはタイミングです",
        goal=("Single out the deciding point and the person behind an action.", "決め手となる点と、行動した人をはっきり示しましょう。"),
        p1=rows(
            ("{t}It's the timing that matters{/t}, not the price.", "重要なのは価格ではなく、{t}タイミングです{/t}。", "It's the timing|that matters,|not|the price."),
            ("{t}It's the schedule that matters{/t}, not the budget.", "重要なのは予算ではなく、{t}日程です{/t}。", "It's the schedule|that matters,|not|the budget."),
            ("{t}It's the quality that matters{/t}, not the speed.", "重要なのは速さではなく、{t}品質です{/t}。", "It's the quality|that matters,|not|the speed."),
            ("{t}It's the deadline that matters{/t}, not the format.", "重要なのは形式ではなく、{t}期限です{/t}。", "It's the deadline|that matters,|not|the format."),
        ),
        p2=rows(
            ("{t}It was Sam who suggested it{/t}.", "{t}それを提案したのはサムです{/t}。", "It was|Sam|who suggested|it."),
            ("{t}It was Maya who called the client{/t}.", "{t}顧客に電話したのはマヤです{/t}。", "It was|Maya|who called|the client."),
            ("{t}It was Ken who changed the date{/t}.", "{t}日付を変更したのはケンです{/t}。", "It was|Ken|who changed|the date."),
            ("{t}It was Yuki who sent the final version{/t}.", "{t}最終版を送ったのはユキです{/t}。", "It was|Yuki|who sent|the final version."),
        ),
        rules=(("Use It is plus a thing and that to focus the deciding element.", "物事を強調するときは It is＋物事＋that を使います。"), ("Use It was plus a person and who to focus who did the action.", "行動した人を強調するときは It was＋人＋who を使います。")),
        prompt=("Name the deciding point and the person responsible, or say there is no current decision.", "決め手と担当した人を言うか、今は判断することがないと伝えましょう。"),
    ),
    105: dict(
        slug="the-sooner-we-start-the-better", title="The sooner we start, the better",
        ko="빨리 시작할수록 좋아요", ja="早く始めるほどいいです",
        goal=("Link two changes and show how one moves with the other.", "二つの変化を結び、一方に応じてもう一方がどう変わるか示しましょう。"),
        p1=rows(
            ("{t}The longer we wait, the harder it'll be to catch up{/t}.", "{t}待てば待つほど、遅れを取り戻すのが難しくなります{/t}。", "The longer we wait,|the harder|it'll be|to catch up."),
            ("{t}The longer we wait, the harder it'll be to finish{/t}.", "{t}待てば待つほど、終えるのが難しくなります{/t}。", "The longer we wait,|the harder|it'll be|to finish."),
            ("{t}The longer we wait, the harder it'll be to find a room{/t}.", "{t}待てば待つほど、部屋を見つけるのが難しくなります{/t}。", "The longer we wait,|the harder|it'll be|to find a room."),
            ("{t}The longer we wait, the harder it'll be to fix{/t}.", "{t}待てば待つほど、直すのが難しくなります{/t}。", "The longer we wait,|the harder|it'll be|to fix."),
        ),
        p2=rows(
            ("{t}The sooner we start, the sooner we can finish{/t}.", "{t}早く始めるほど、早く終えられます{/t}。", "The sooner we start,|the sooner|we can|finish."),
            ("{t}The sooner we leave, the sooner we can arrive{/t}.", "{t}早く出るほど、早く着けます{/t}。", "The sooner we leave,|the sooner|we can|arrive."),
            ("{t}The sooner we decide, the sooner we can book{/t}.", "{t}早く決めるほど、早く予約できます{/t}。", "The sooner we decide,|the sooner|we can|book."),
            ("{t}The sooner we ask, the sooner we can know{/t}.", "{t}早く聞くほど、早く分かります{/t}。", "The sooner we ask,|the sooner|we can|know."),
        ),
        rules=(("Repeat the plus a comparative in both halves to link the two changes.", "二つの変化を結ぶため、両方の節で the＋比較級を繰り返します。"), ("Keep each half complete: the sooner plus a clause, then another the sooner clause.", "それぞれを the sooner＋節の形にし、二つの節をそろえます。")),
        prompt=("Explain one real linked change, or say no urgent decision comes to mind.", "実際に連動する変化を一つ説明するか、急ぐ判断は思いつかないと伝えましょう。"),
    ),
    106: dict(
        slug="theres-one-thing-id-change", title="There's one thing I'd change",
        ko="한 가지 바꾸고 싶은 게 있어요", ja="一つ変えたい点があります",
        goal=("Announce one point or a small set before you give the details.", "一つの点や少数の項目を、詳しく述べる前に予告しましょう。"),
        p1=rows(
            ("{t}There's one thing I'd change{/t}.", "{t}一つ変えたい点があります{/t}。", "There's|one thing|I'd|change."),
            ("{t}There's one thing I'd check{/t}.", "{t}一つ確認したい点があります{/t}。", "There's|one thing|I'd|check."),
            ("{t}There's one thing I'd add{/t}.", "{t}一つ加えたい点があります{/t}。", "There's|one thing|I'd|add."),
            ("{t}There's one thing I'd suggest{/t}.", "{t}一つ提案したい点があります{/t}。", "There's|one thing|I'd|suggest."),
        ),
        p2=rows(
            ("{t}There are a couple of issues worth raising{/t}.", "{t}取り上げる価値のある問題が二つほどあります{/t}。", "There are|a couple of issues|worth|raising."),
            ("{t}There are two points worth discussing{/t}.", "{t}話し合う価値のある点が二つあります{/t}。", "There are|two points|worth|discussing."),
            ("{t}There are three details worth checking{/t}.", "{t}確認する価値のある詳細が三つあります{/t}。", "There are|three details|worth|checking."),
            ("{t}There are a few options worth reviewing{/t}.", "{t}見直す価値のある選択肢がいくつかあります{/t}。", "There are|a few options|worth|reviewing."),
        ),
        rules=(("Use There's with the singular one thing, then say what you would do.", "単数の one thing には There's を使い、そのあとにしたいことを続けます。"), ("Use There are with plural items, and put an -ing action after worth.", "複数の項目には There are を使い、worth の後ろには -ing 形を置きます。")),
        prompt=("Announce one real point and any further issues, or say everything looks fine.", "実際の一点と追加の問題を予告するか、すべて問題ないと伝えましょう。"),
    ),
    107: dict(
        slug="as-for-the-budget", title="As for the budget,",
        ko="예산에 관해서는", ja="予算については",
        goal=("Introduce a new topic and return to an earlier one clearly.", "新しい話題を出し、前の話題にも分かりやすく戻りましょう。"),
        p1=rows(
            ("{t}As for the budget{/t}, we're still waiting.", "{t}予算については{/t}、まだ返事を待っています。", "As for|the budget,|we're still|waiting."),
            ("{t}As for the delivery{/t}, we're still waiting.", "{t}配達については{/t}、まだ返事を待っています。", "As for|the delivery,|we're still|waiting."),
            ("{t}As for the venue{/t}, it's already booked.", "{t}会場については{/t}、もう予約済みです。", "As for|the venue,|it's already|booked."),
            ("{t}As for the schedule{/t}, it may change.", "{t}日程については{/t}、変更になるかもしれません。", "As for|the schedule,|it may|change."),
        ),
        p2=rows(
            ("{t}Coming back to the timeline{/t}, we need a firm date.", "{t}予定表の話に戻ると{/t}、確定日が必要です。", "Coming back to|the timeline,|we need|a firm date."),
            ("{t}Coming back to the price{/t}, we need a firm answer.", "{t}価格の話に戻ると{/t}、はっきりした返事が必要です。", "Coming back to|the price,|we need|a firm answer."),
            ("{t}Coming back to the meeting{/t}, we need a firm decision.", "{t}会議の話に戻ると{/t}、確定した判断が必要です。", "Coming back to|the meeting,|we need|a firm decision."),
            ("{t}Coming back to the second option{/t}, we need a firm date.", "{t}二つ目の案の話に戻ると{/t}、確定日が必要です。", "Coming back to|the second option,|we need|a firm date."),
        ),
        rules=(("Put a noun topic after As for and use a comma before the message.", "As for の後ろに名詞の話題を置き、本文の前にコンマを置きます。"), ("Put the earlier noun topic after Coming back to, followed by a comma.", "Coming back to の後ろに前の話題を名詞で置き、そのあとにコンマを置きます。")),
        prompt=("Move between two real topics, or say there are no updates to organise.", "実際の二つの話題を切り替えるか、整理する更新はないと伝えましょう。"),
    ),
    108: dict(
        slug="would-you-be-able-to", title="Would you be able to",
        ko="해 주실 수 있을까요", ja="していただくことはできますか",
        goal=("Make one careful request and one informal request at the right level.", "丁寧な依頼とくだけた依頼を、相手に合う調子で使い分けましょう。"),
        p1=rows(
            ("{t}Would you be able to{/t} send it over?", "送って{t}いただくことはできますか{/t}？", "Would you|be able to|send it|over?"),
            ("{t}Would you be able to{/t} review the draft?", "下書きを確認して{t}いただくことはできますか{/t}？", "Would you|be able to|review|the draft?"),
            ("{t}Would you be able to{/t} confirm the date?", "日付を確認して{t}いただくことはできますか{/t}？", "Would you|be able to|confirm|the date?"),
            ("{t}Would you be able to{/t} check the figures?", "数字を確認して{t}いただくことはできますか{/t}？", "Would you|be able to|check|the figures?"),
        ),
        p2=rows(
            ("{t}Can you send it over when you get a sec{/t}?", "時間があるときに{t}送ってくれる{/t}？", "Can you|send it over|when you|get a sec?"),
            ("{t}Can you review it when you get a sec{/t}?", "時間があるときに{t}確認してくれる{/t}？", "Can you|review it|when you|get a sec?"),
            ("{t}Can you call me when you get a sec{/t}?", "時間があるときに{t}電話してくれる{/t}？", "Can you|call me|when you|get a sec?"),
            ("{t}Can you check the date when you get a sec{/t}?", "時間があるときに{t}日付を確認してくれる{/t}？", "Can you|check the date|when you|get a sec?"),
        ),
        rules=(("After Would you be able to, use a plain verb; the longer frame adds distance.", "Would you be able to の後ろは動詞の原形にし、長い形で丁寧な距離を作ります。"), ("After Can you, use a plain verb; when you get a sec makes the request informal and unhurried.", "Can you の後ろは動詞の原形にし、when you get a sec でくだけた急がない依頼にします。")),
        prompt=("Make one request that fits our relationship, or say you do not need help right now.", "私たちの関係に合う依頼を一つするか、今は手伝いが必要ないと伝えましょう。"),
    ),
    109: dict(
        slug="to-put-it-bluntly", title="To put it bluntly",
        ko="솔직히 말해서", ja="率直に言えば",
        goal=("Signal directness before giving a clear negative view.", "はっきりした否定的な意見の前に、率直に言う合図を出しましょう。"),
        p1=rows(
            ("{t}To put it bluntly{/t}, it won't work.", "{t}率直に言えば{/t}、うまくいきません。", "To put it bluntly,|it|won't work."),
            ("{t}To put it bluntly{/t}, it costs too much.", "{t}率直に言えば{/t}、費用がかかりすぎます。", "To put it bluntly,|it|costs too much."),
            ("{t}To put it bluntly{/t}, it's too late.", "{t}率直に言えば{/t}、もう遅すぎます。", "To put it bluntly,|it's|too late."),
            ("{t}To put it bluntly{/t}, we need another plan.", "{t}率直に言えば{/t}、別の案が必要です。", "To put it bluntly,|we|need another plan."),
        ),
        p2=rows(
            ("{t}Honestly? I'd walk away{/t}.", "{t}正直に言うと、私なら見送ります{/t}。", "Honestly?|I'd|walk|away."),
            ("{t}Honestly? I'd wait for now{/t}.", "{t}正直に言うと、私なら今は待ちます{/t}。", "Honestly?|I'd|wait|for now."),
            ("{t}Honestly? I'd say no{/t}.", "{t}正直に言うと、私なら断ります{/t}。", "Honestly?|I'd|say|no."),
            ("{t}Honestly? I'd choose the other option{/t}.", "{t}正直に言うと、私ならもう一つの案を選びます{/t}。", "Honestly?|I'd choose|the other|option."),
        ),
        omit_reorder=(2,),
        rules=(("Use To put it bluntly before a full clause and a comma to warn that you will be direct.", "To put it bluntly のあとにコンマと完全な節を置き、率直に言う合図にします。"), ("Use sentence-level Honestly before your full reaction; the question mark adds a spoken pause.", "文全体にかかる Honestly のあとに反応を続け、疑問符で話し言葉の間を示します。")),
        prompt=("Give a direct view on a low-stakes option, or say you would rather not judge it.", "重要度の低い案に率直な意見を言うか、判断は控えたいと伝えましょう。"),
    ),
    110: dict(
        slug="i-hate-to-say-it-but", title="I hate to say it, but",
        ko="말하기 그렇지만", ja="言いにくいのですが",
        goal=("Cushion unwelcome news and still state the problem clearly.", "好ましくない知らせを和らげつつ、問題をはっきり伝えましょう。"),
        p1=rows(
            ("{t}I hate to say it, but{/t} we're behind.", "{t}言いにくいのですが{/t}、私たちは遅れています。", "I hate to say it,|but|we're behind."),
            ("{t}I hate to say it, but{/t} we can't finish today.", "{t}言いにくいのですが{/t}、今日は終えられません。", "I hate to say it,|but|we can't finish today."),
            ("{t}I hate to say it, but{/t} the order is delayed.", "{t}言いにくいのですが{/t}、注文が遅れています。", "I hate to say it,|but|the order is delayed."),
            ("{t}I hate to say it, but{/t} the price has changed.", "{t}言いにくいのですが{/t}、価格が変わりました。", "I hate to say it,|but|the price has changed."),
        ),
        p2=rows(
            ("{t}I'm afraid there's been a problem{/t}.", "{t}残念ですが、問題が起きました{/t}。", "I'm afraid|there's been|a problem."),
            ("{t}I'm afraid there's been a delay{/t}.", "{t}残念ですが、遅れが出ました{/t}。", "I'm afraid|there's been|a delay."),
            ("{t}I'm afraid there's been a mistake{/t}.", "{t}残念ですが、間違いがありました{/t}。", "I'm afraid|there's been|a mistake."),
            ("{t}I'm afraid there's been a change{/t}.", "{t}残念ですが、変更がありました{/t}。", "I'm afraid|there's been|a change."),
        ),
        rules=(("Put the unwelcome clause after I hate to say it, but; do not hide the news.", "I hate to say it, but のあとに好ましくない内容を置き、知らせを曖昧にしません。"), ("Here I'm afraid introduces bad news; it does not mean the speaker feels fear.", "ここでの I'm afraid は悪い知らせを導き、話し手の恐怖を表すものではありません。")),
        prompt=("Deliver one clear piece of practice bad news, or say there is no bad news today.", "練習用の悪い知らせを一つ明確に伝えるか、今日は悪い知らせがないと伝えましょう。"),
    ),
    111: dict(
        slug="just-so-you-know", title="Just so you know,",
        ko="참고로 알려드리면", ja="念のためお知らせすると",
        goal=("Pass on a neutral update without turning it into a request or complaint.", "中立的な更新を、依頼や不満にせず伝えましょう。"),
        p1=rows(
            ("{t}Just so you know{/t}, the room's booked.", "{t}念のためお知らせすると{/t}、部屋は予約済みです。", "Just so you know,|the room's|booked."),
            ("{t}Just so you know{/t}, the meeting has moved.", "{t}念のためお知らせすると{/t}、会議の時間が変わりました。", "Just so you know,|the meeting|has moved."),
            ("{t}Just so you know{/t}, the tickets are ready.", "{t}念のためお知らせすると{/t}、チケットは準備できています。", "Just so you know,|the tickets|are ready."),
            ("{t}Just so you know{/t}, the client called.", "{t}念のためお知らせすると{/t}、顧客から電話がありました。", "Just so you know,|the client|called."),
        ),
        p2=rows(
            ("{t}Heads up — they moved the meeting{/t}.", "{t}先に知らせておくと、会議が変更になりました{/t}。", "Heads up —|they|moved the meeting."),
            ("{t}Heads up — the price has changed{/t}.", "{t}先に知らせておくと、価格が変わりました{/t}。", "Heads up —|the price|has changed."),
            ("{t}Heads up — the train is delayed{/t}.", "{t}先に知らせておくと、電車が遅れています{/t}。", "Heads up —|the train|is delayed."),
            ("{t}Heads up — Sam called earlier{/t}.", "{t}先に知らせておくと、サムから先ほど電話がありました{/t}。", "Heads up —|Sam|called earlier."),
        ),
        rules=(("Follow Just so you know with a full clause; it frames the information as a neutral update.", "Just so you know のあとには完全な節を続け、中立的な更新として伝えます。"), ("Heads up stands outside the clause as an informal alert, so pause before the news.", "Heads up は節の外に置くくだけた注意喚起なので、知らせの前で間を置きます。")),
        prompt=("Pass on one real neutral update, or say there is nothing new to report.", "実際の中立的な更新を一つ伝えるか、知らせることはないと伝えましょう。"),
    ),
    112: dict(
        slug="that-came-across-as-rude", title="That came across as rude",
        ko="그 말은 무례하게 들렸어요", ja="その言い方は失礼に聞こえました",
        goal=("Name the effect of someone's wording and repair an unintended tone.", "言い方が与えた印象を伝え、意図しない調子を修復しましょう。"),
        p1=rows(
            ("{t}That came across as rude{/t}.", "{t}その言い方は失礼に聞こえました{/t}。", "That|came across|as|rude."),
            ("{t}That came across as cold{/t}.", "{t}その言い方は冷たく聞こえました{/t}。", "That|came across|as|cold."),
            ("{t}That came across as impatient{/t}.", "{t}その言い方はいら立っているように聞こえました{/t}。", "That|came across|as|impatient."),
            ("{t}That came across as unclear{/t}.", "{t}その言い方は分かりにくく聞こえました{/t}。", "That|came across|as|unclear."),
        ),
        p2=rows(
            ("{t}I didn't mean to sound rude{/t}.", "{t}失礼に聞こえるつもりはありませんでした{/t}。", "I didn't|mean to|sound|rude."),
            ("{t}I didn't mean to sound cold{/t}.", "{t}冷たく聞こえるつもりはありませんでした{/t}。", "I didn't|mean to|sound|cold."),
            ("{t}I didn't mean to sound impatient{/t}.", "{t}いら立って聞こえるつもりはありませんでした{/t}。", "I didn't|mean to|sound|impatient."),
            ("{t}I didn't mean to sound unclear{/t}.", "{t}分かりにくく聞こえるつもりはありませんでした{/t}。", "I didn't|mean to|sound|unclear."),
        ),
        rules=(("Use came across as plus an adjective to describe the listener's impression.", "聞き手が受けた印象には came across as＋形容詞を使います。"), ("Use mean to plus plain sound, then an adjective for the unintended tone.", "意図しなかった調子には mean to＋動詞の原形 sound＋形容詞を使います。")),
        prompt=("Describe one low-stakes wording problem and repair it, or say none comes to mind.", "重要度の低い言い方の問題と修復を述べるか、思いつかないと伝えましょう。"),
    ),
}


def rule(title, title_ja, formula, heading, heading_ja, examples):
    return title, title_ja, formula, heading, heading_ja, examples


def tip(title, title_ja, script, script_ja, left, right):
    return title, title_ja, script, script_ja, left, right


SPECS = {
    103: semantic_spec(
        (("Use this to put your biggest concern after is.", "最大の懸念を is の後ろに置いて強調します。"), ("Use this to focus the action you recommend.", "勧める行動に焦点を当てます。")),
        (("Name your main concern, or say nothing worries you about the decision.", "一番の懸念を言うか、その判断には心配がないと伝えましょう。"), ("Suggest one action, or say you would not change the current plan.", "行動を一つ提案するか、今の案を変えないと伝えましょう。")),
        (tuple((jp, "What ", "worries", "worry", tail) for jp, tail in (("私を一番{t}心配させる{/t}のは費用です。", " me most is the cost."), ("私を一番{t}心配させる{/t}のは日程です。", " me most is the schedule."), ("私を一番{t}心配させる{/t}のは期限です。", " me most is the deadline."), ("私を一番{t}心配させる{/t}のは品質です。", " me most is the quality."))), (("私が提案したいのは1週間{t}待つこと{/t}です。", "What I'd suggest is ", "waiting", "wait", " a week."), ("私が提案したいのはデータを{t}確認すること{/t}です。", "What I'd suggest is ", "checking", "check", " the data."), ("私が提案したいのは顧客に{t}聞くこと{/t}です。", "What I'd suggest is ", "asking", "ask", " the client."), ("私が提案したいのは明日{t}始めること{/t}です。", "What I'd suggest is ", "starting", "start", " tomorrow."))),
        (rule("Focus after is", "is の後ろに焦点", "What + clause + <b>is</b> + focus", "Front the concern frame", "懸念の枠を先に", ("What worries me most <b>is the cost</b>.", "What worries me most <b>is the deadline</b>.")), rule("Suggestion as an action", "提案は行動の形で", "What I'd suggest is + 動詞<b>-ing</b>", "Focused recommendation", "焦点を当てた提案", ("What I'd suggest is <b>waiting</b> a week.", "What I'd suggest is <b>checking</b> the data."))),
        tip("My main concern or what worries me most?", "直接的な懸念・焦点を当てた懸念", "Both are natural. The What-clause deliberately saves the key point for the end.", "どちらも自然です。What 節は重要な点を意図的に文末まで取っておきます。", ("Neutral and direct", "中立で直接的", "My main concern is the cost.", "主な懸念は費用です。"), ("Deliberate end focus", "文末に焦点", "What worries me most is the cost.", "一番心配なのは費用です。")),
    ),
    104: semantic_spec(
        (("Use this to contrast the deciding thing with a less important one.", "決め手となる物事を、重要でないものと対比します。"), ("Use this to single out the person who did something.", "行動した人を一人に絞って示します。")),
        (("Contrast one deciding point with another, or say both matter.", "一つの決め手を別の点と対比するか、両方重要だと伝えましょう。"), ("Name who did one action, or say you do not know who did it.", "行動した人を言うか、誰か分からないと伝えましょう。")),
        ((("重要なのは価格ではなく{t}タイミング{/t}です。", "It's the ", "timing", "price", " that matters, not the price."), ("重要なのは予算ではなく{t}日程{/t}です。", "It's the ", "schedule", "budget", " that matters, not the budget."), ("重要なのは速さではなく{t}品質{/t}です。", "It's the ", "quality", "speed", " that matters, not the speed."), ("重要なのは形式ではなく{t}期限{/t}です。", "It's the ", "deadline", "format", " that matters, not the format.")), (("それを提案したのは{t}サム{/t}です。", "It was ", "Sam", "the timing", " who suggested it."), ("顧客に電話したのは{t}マヤ{/t}です。", "It was ", "Maya", "the client", " who called the client."), ("日付を変更したのは{t}ケン{/t}です。", "It was ", "Ken", "the date", " who changed the date."), ("最終版を送ったのは{t}ユキ{/t}です。", "It was ", "Yuki", "the final version", " who sent the final version."))),
        (rule("Thing focus with that", "物事の強調は that", "It is + thing + <b>that</b> + clause", "Single out the deciding element", "決め手を一つに絞る", ("It's the timing <b>that matters</b>.", "It's the quality <b>that matters</b>.")), rule("Person focus with who", "人の強調は who", "It was + person + <b>who</b> + clause", "Single out the person", "人を一人に絞る", ("It was Sam <b>who suggested it</b>.", "It was Maya <b>who called</b>."))),
        tip("It was Sam who... or Sam was the one who...?", "強い焦点・会話的な特定", "The cleft is compact and emphatic. “The one who” is often more conversational when identifying a person.", "分裂文は簡潔で強調的です。人を特定する会話では the one who のほうが口語的なこともあります。", ("Compact emphasis", "簡潔に強調", "It was Sam who suggested it.", "それを提案したのはサムです。"), ("Conversational identification", "会話的に特定", "Sam was the one who suggested it.", "提案したのはサムでした。")),
    ),
    105: semantic_spec(
        (("Use this when delay makes a task progressively harder.", "遅れるほど作業が難しくなるときに使います。"), ("Use this when an earlier start brings an earlier result.", "早く始めるほど結果も早くなるときに使います。")),
        (("Describe one real cost of waiting, or say waiting would not matter.", "待つことで生じる実際の問題を言うか、待っても影響はないと伝えましょう。"), ("Describe one benefit of starting sooner, or say there is no need to hurry.", "早く始める利点を言うか、急ぐ必要はないと伝えましょう。")),
        (tuple((jp, "The ", "longer", "longest", tail) for jp, tail in (("{t}長く{/t}待つほど、追いつくのが難しくなります。", " we wait, the harder it'll be to catch up."), ("{t}長く{/t}待つほど、終えるのが難しくなります。", " we wait, the harder it'll be to finish."), ("{t}長く{/t}待つほど、部屋を見つけにくくなります。", " we wait, the harder it'll be to find a room."), ("{t}長く{/t}待つほど、直しにくくなります。", " we wait, the harder it'll be to fix."))), tuple((jp, "The ", "sooner", "soonest", tail) for jp, tail in (("{t}早く{/t}始めるほど、早く終えられます。", " we start, the sooner we can finish."), ("{t}早く{/t}出るほど、早く着けます。", " we leave, the sooner we can arrive."), ("{t}早く{/t}決めるほど、早く予約できます。", " we decide, the sooner we can book."), ("{t}早く{/t}聞くほど、早く分かります。", " we ask, the sooner we can know.")))),
        (rule("Two linked comparatives", "二つの比較級を連結", "<b>The + comparative</b> ..., <b>the + comparative</b> ...", "One change moves with the other", "一方に応じてもう一方も変化", ("<b>The longer</b> we wait, <b>the harder</b> it'll be.", "<b>The more</b> we add, <b>the longer</b> it takes.")), rule("Earlier action, earlier result", "行動も結果も早く", "<b>The sooner</b> + clause, <b>the sooner</b> + clause", "Repeat the relationship", "関係を二つの節で示す", ("The sooner we <b>start</b>, the sooner we can <b>finish</b>.", "The sooner we <b>ask</b>, the sooner we'll <b>know</b>."))),
        tip("Full link or the sooner, the better?", "関係を明示・短く評価", "Use the full form when both changes matter. Use the short fixed expression when the only message is urgency.", "二つの変化が重要なら完全な形を使います。急ぐほどよいという評価だけなら短い定型表現を使います。", ("Name both changes", "二つの変化を明示", "The sooner we start, the sooner we can finish.", "早く始めるほど、早く終えられます。"), ("Simple urgency", "単純に急ぐ", "The sooner, the better.", "早ければ早いほどいいです。")),
    ),
    106: semantic_spec(
        (("Use this to announce one point before explaining it.", "一つの点を説明する前に予告します。"), ("Use this to announce a small plural set worth discussing.", "話す価値のある少数の項目を予告します。")),
        (("Announce one point you would change, or say you would change nothing.", "変えたい一点を予告するか、何も変えないと伝えましょう。"), ("Announce a small set of issues, or say there are none to raise.", "少数の問題を予告するか、取り上げる問題はないと伝えましょう。")),
        (tuple((jp, "There", "'s", " are", tail) for jp, tail in (("一つなので{t}単数形{/t}：変えたい点があります。", " one thing I'd change."), ("一つなので{t}単数形{/t}：確認したい点があります。", " one thing I'd check."), ("一つなので{t}単数形{/t}：加えたい点があります。", " one thing I'd add."), ("一つなので{t}単数形{/t}：提案したい点があります。", " one thing I'd suggest."))), (("{t}取り上げる{/t}価値があります。", "There are a couple of issues worth ", "raising", "to raise", "."), ("{t}話し合う{/t}価値があります。", "There are two points worth ", "discussing", "to discuss", "."), ("{t}確認する{/t}価値があります。", "There are three details worth ", "checking", "to check", "."), ("{t}見直す{/t}価値があります。", "There are a few options worth ", "reviewing", "to review", "."))),
        (rule("Singular agreement", "単数との一致", "<b>There's one thing</b> + clause", "One announced point", "一点を予告", ("<b>There's one thing</b> I'd change.", "<b>There's one thing</b> I'd add.")), rule("Plural plus worth -ing", "複数＋worth -ing", "<b>There are</b> + plural + worth + 動詞<b>-ing</b>", "A small set of points", "少数の項目", ("There are two points worth <b>discussing</b>.", "There are a few options worth <b>reviewing</b>."))),
        tip("A couple of or two?", "およその少数・正確な二つ", "In conversation, “a couple of” often means a small number around two. Use “two” when the count itself matters.", "会話の a couple of は二つ前後の少数を表すことがあります。数が重要なら two を使います。", ("Small approximate set", "およその少数", "There are a couple of issues worth raising.", "取り上げたい問題が二つほどあります。"), ("Exact count", "正確に二つ", "There are two issues worth raising.", "取り上げたい問題が二つあります。")),
    ),
    107: semantic_spec(
        (("Use this to introduce a new noun topic.", "新しい名詞の話題を導入します。"), ("Use this to return explicitly to an earlier noun topic.", "前に出た名詞の話題へ明示的に戻ります。")),
        (("Introduce one real topic and update it, or say there is no update.", "実際の話題を一つ出して更新するか、更新はないと伝えましょう。"), ("Return to one earlier topic, or say there is nothing to revisit.", "前の話題に一つ戻るか、戻る話題はないと伝えましょう。")),
        (tuple((jp, "As ", "for", "to", tail) for jp, tail in (("予算{t}については{/t}、まだ待っています。", " the budget, we're still waiting."), ("配達{t}については{/t}、まだ待っています。", " the delivery, we're still waiting."), ("会場{t}については{/t}、予約済みです。", " the venue, it's already booked."), ("日程{t}については{/t}、変更になるかもしれません。", " the schedule, it may change."))), tuple((jp, "Coming back ", "to", "at", tail) for jp, tail in (("予定表{t}の話に戻ると{/t}、確定日が必要です。", " the timeline, we need a firm date."), ("価格{t}の話に戻ると{/t}、はっきりした返事が必要です。", " the price, we need a firm answer."), ("会議{t}の話に戻ると{/t}、確定した判断が必要です。", " the meeting, we need a firm decision."), ("二つ目の案{t}の話に戻ると{/t}、確定日が必要です。", " the second option, we need a firm date.")))),
        (rule("Introduce with As for", "As for で話題を導入", "<b>As for + noun</b>, + message", "New topic", "新しい話題", ("<b>As for the budget</b>, we're still waiting.", "<b>As for the venue</b>, it's booked.")), rule("Return with Coming back to", "Coming back to で戻る", "<b>Coming back to + noun</b>, + message", "Earlier topic", "前に出た話題", ("<b>Coming back to the timeline</b>, we need a date.", "<b>Coming back to the price</b>, we need an answer."))),
        tip("As for or speaking of?", "話題を整理・連想で話題転換", "“As for” deliberately organises a topic. “Speaking of” changes topic because the last thing reminded you of it.", "As for は話題を意図的に整理します。Speaking of は直前の話から連想して話題を変えます。", ("Organise the agenda", "議題を整理", "As for the budget, we're still waiting.", "予算については、まだ返事を待っています。"), ("Follow an association", "連想で話題転換", "Speaking of Sam, did he reply?", "サムと言えば、返事は来ましたか？")),
    ),
    108: semantic_spec(
        (("Use this careful request with distance or a less familiar person.", "距離を保ちたい相手や、あまり親しくない相手への丁寧な依頼です。"), ("Use this informal request with a close colleague.", "親しい同僚へのくだけた依頼です。")),
        (("Make a careful request, or say you do not need the task done.", "丁寧に依頼するか、その作業は必要ないと伝えましょう。"), ("Make an informal request to a close colleague, or say it is not needed.", "親しい同僚にくだけて頼むか、必要ないと伝えましょう。")),
        ((("{t}送って{/t}いただけますか？", "Would you be able to ", "send", "sending", " it over?"), ("下書きを{t}確認して{/t}いただけますか？", "Would you be able to ", "review", "reviewing", " the draft?"), ("日付を{t}確認して{/t}いただけますか？", "Would you be able to ", "confirm", "confirming", " the date?"), ("数字を{t}確認して{/t}いただけますか？", "Would you be able to ", "check", "checking", " the figures?")), (("時間があるときに{t}送って{/t}くれる？", "Can you ", "send", "sending", " it over when you get a sec?"), ("時間があるときに{t}確認して{/t}くれる？", "Can you ", "review", "reviewing", " it when you get a sec?"), ("時間があるときに{t}電話して{/t}くれる？", "Can you ", "call", "calling", " me when you get a sec?"), ("時間があるときに日付を{t}確認して{/t}くれる？", "Can you ", "check", "checking", " the date when you get a sec?"))),
        (rule("Careful distance", "丁寧な距離", "Would you be able to + <b>plain verb</b>?", "Less familiar or higher-stakes", "あまり親しくない・重要度が高い", ("Would you be able to <b>send</b> it over?", "Would you be able to <b>confirm</b> the date?")), rule("Informal colleague request", "同僚へのくだけた依頼", "Can you + <b>plain verb</b> + when you get a sec?", "Close and low-pressure", "親しい・急がない", ("Can you <b>send</b> it over when you get a sec?", "Can you <b>check</b> it when you get a sec?"))),
        tip("Polite or too formal?", "丁寧・親しい相手には堅すぎる", "The longer request suits distance. With a close colleague, it can sound cold if the task is routine.", "長い依頼は距離のある相手に合います。親しい同僚への日常的な依頼では、冷たく聞こえることがあります。", ("New supplier", "初めての取引先", "Would you be able to send it over?", "送っていただくことはできますか？"), ("Close teammate", "親しい同僚", "Can you send it over when you get a sec?", "時間があるときに送ってくれる？")),
    ),
    109: semantic_spec(
        (("Use this to warn that a clear negative judgment follows.", "はっきりした否定的判断が続くと予告します。"), ("Use this spoken form before your candid personal choice.", "率直な個人的選択の前に使う話し言葉です。")),
        (("Give a direct low-stakes judgment, or decline to judge.", "重要度の低いことを率直に判断するか、判断を控えましょう。"), ("Say what you would honestly do, or say you are not sure yet.", "自分ならどうするか率直に言うか、まだ分からないと伝えましょう。")),
        (tuple((jp, "To put it ", "bluntly", "blunt", tail) for jp, tail in (("{t}率直に{/t}言えば、うまくいきません。", ", it won't work."), ("{t}率直に{/t}言えば、費用がかかりすぎます。", ", it costs too much."), ("{t}率直に{/t}言えば、遅すぎます。", ", it's too late."), ("{t}率直に{/t}言えば、別の案が必要です。", ", we need another plan."))), (("{t}正直に言うと{/t}、私なら見送ります。", "", "Honestly", "Honest", "? I'd walk away."), ("{t}正直に言うと{/t}、私なら今は待ちます。", "", "Honestly", "Honest", "? I'd wait for now."), ("{t}正直に言うと{/t}、私なら断ります。", "", "Honestly", "Honest", "? I'd say no."), ("{t}正直に言うと{/t}、私ならもう一つを選びます。", "", "Honestly", "Honest", "? I'd choose the other option."))),
        (rule("Announce bluntness", "率直さを予告", "<b>To put it bluntly</b>, + full clause", "Direct judgment", "直接的な判断", ("To put it bluntly, <b>it won't work</b>.", "To put it bluntly, <b>it costs too much</b>.")), rule("Honestly comments on the sentence", "Honestly は文全体にかかる", "<b>Honestly?</b> + personal reaction", "Candid spoken choice", "率直な話し言葉の選択", ("Honestly? <b>I'd walk away</b>.", "Honestly? <b>I'd say no</b>."))),
        tip("Honestly, or Honestly?", "穏やかな前置き・独立した率直な反応", "A comma smoothly introduces an opinion. A question mark makes Honestly a separate, more conversational beat.", "コンマなら意見を滑らかに導きます。疑問符なら Honestly が独立し、より会話的な間になります。", ("Smooth introduction", "滑らかな前置き", "Honestly, I don't think it'll work.", "正直に言うと、うまくいかないと思います。"), ("Spoken beat", "会話的な間", "Honestly? I'd walk away.", "正直に言うと、私なら見送ります。")),
    ),
    110: semantic_spec(
        (("Use this when you dislike having to state the bad news.", "悪い知らせを言わなければならないのが心苦しいときに使います。"), ("Use this conventional cushion before a clear problem statement.", "明確な問題を述べる前の定型的な和らげ表現です。")),
        (("State one clear practice problem, or say there is no problem.", "練習用の問題を一つ明確に言うか、問題はないと伝えましょう。"), ("Cushion one clear piece of bad news, or say there is none.", "悪い知らせを一つ和らげて伝えるか、知らせはないと伝えましょう。")),
        (tuple((jp, "I hate to say it, ", "but", "so", tail) for jp, tail in (("言いにくいのですが、{t}しかし{/t}遅れています。", " we're behind."), ("言いにくいのですが、{t}しかし{/t}今日は終えられません。", " we can't finish today."), ("言いにくいのですが、{t}しかし{/t}注文が遅れています。", " the order is delayed."), ("言いにくいのですが、{t}しかし{/t}価格が変わりました。", " the price has changed."))), (("残念ですが、{t}問題{/t}が起きました。", "I'm afraid there's been ", "a problem", "problems", "."), ("残念ですが、{t}遅れ{/t}が出ました。", "I'm afraid there's been ", "a delay", "delays", "."), ("残念ですが、{t}間違い{/t}がありました。", "I'm afraid there's been ", "a mistake", "mistakes", "."), ("残念ですが、{t}変更{/t}がありました。", "I'm afraid there's been ", "a change", "changes", "."))),
        (rule("Behind or behind schedule?", "behind / behind schedule", "<b>behind</b>（文脈）／<b>behind schedule</b>（明示）", "After the cushion", "和らげ表現のあと", ("I hate to say it, but <b>we're behind</b>.", "I hate to say it, but <b>we're behind schedule</b>.")), rule("Afraid as a news cushion", "知らせを和らげる afraid", "I'm afraid + <b>full clause</b>", "Not literal fear", "文字どおりの恐怖ではない", ("I'm afraid <b>there's been a problem</b>.", "I'm afraid <b>there's been a delay</b>."))),
        tip("I'm sorry, but or I'm afraid?", "責任を認める・悪い知らせを和らげる", "Use “I'm sorry, but” when you own an inconvenience. “I'm afraid” can introduce bad news without claiming personal fault.", "自分が迷惑をかけたなら I'm sorry, but を使います。I'm afraid は自分の責任を認めずに悪い知らせを導くこともできます。", ("Own the inconvenience", "自分の責任", "I'm sorry, but I sent the wrong file.", "すみません、間違ったファイルを送りました。"), ("Introduce bad news", "悪い知らせを導入", "I'm afraid there's been a delay.", "残念ですが、遅れが出ました。")),
    ),
    111: semantic_spec(
        (("Use this for a neutral update the listener may find useful.", "相手に役立つかもしれない中立的な更新に使います。"), ("Use this informal alert before timely news.", "早めに伝えたい知らせの前に使うくだけた注意喚起です。")),
        (("Give one neutral update, or say there is nothing new.", "中立的な更新を一つ言うか、新しいことはないと伝えましょう。"), ("Give one timely informal alert, or say no alert is needed.", "早めに伝える知らせを一つ言うか、注意喚起は不要だと伝えましょう。")),
        (tuple((jp, "Just ", "so", "for", tail) for jp, tail in (("{t}念のためお知らせすると{/t}、部屋は予約済みです。", " you know, the room's booked."), ("{t}念のためお知らせすると{/t}、会議が変更になりました。", " you know, the meeting has moved."), ("{t}念のためお知らせすると{/t}、チケットは準備できています。", " you know, the tickets are ready."), ("{t}念のためお知らせすると{/t}、顧客から電話がありました。", " you know, the client called."))), (("{t}先に知らせておくと{/t}、会議が変更になりました。", "", "Heads", "Head", " up — they moved the meeting."), ("{t}先に知らせておくと{/t}、価格が変わりました。", "", "Heads", "Head", " up — the price has changed."), ("{t}先に知らせておくと{/t}、電車が遅れています。", "", "Heads", "Head", " up — the train is delayed."), ("{t}先に知らせておくと{/t}、サムから先ほど電話がありました。", "", "Heads", "Head", " up — Sam called earlier."))),
        (rule("Neutral full-clause update", "中立的な完全節の更新", "Just so you know, + <b>full clause</b>", "Information, not a request", "依頼ではなく情報", ("Just so you know, <b>the room's booked</b>.", "Just so you know, <b>the report is ready</b>.")), rule("Informal alert outside the clause", "節の外に置く注意喚起", "<b>Heads up</b> — + full clause", "Timely informal news", "早めのくだけた知らせ", ("Heads up — <b>they moved the meeting</b>.", "Heads up — <b>the train is delayed</b>."))),
        tip("Heads up or just a heads-up?", "簡潔な注意喚起・少し柔らかい名詞句", "“Heads up” is brisk. “Just a heads-up” often sounds a little softer before the same news.", "Heads up は簡潔です。Just a heads-up は同じ知らせの前で少し柔らかく聞こえることがあります。", ("Brisk alert", "簡潔", "Heads up — they moved the meeting.", "先に知らせておくと、会議が変更になりました。"), ("Softer lead-in", "少し柔らかい", "Just a heads-up: they moved the meeting.", "念のためお知らせすると、会議が変更になりました。")),
    ),
    112: semantic_spec(
        (("Use this to describe the impression created by wording.", "言い方が与えた印象を説明します。"), ("Use this to separate your intention from an unintended tone.", "自分の意図と、意図しなかった調子を分けて伝えます。")),
        (("Name how one low-stakes message sounded, or say it sounded fine.", "重要度の低いメッセージがどう聞こえたか言うか、問題なかったと伝えましょう。"), ("Repair an unintended tone, or say no repair is needed.", "意図しない調子を修復するか、修復は不要だと伝えましょう。")),
        ((("as の後ろは{t}形容詞「失礼な」{/t}。", "That came across as ", "rude", "rudely", "."), ("as の後ろは{t}形容詞「冷たい」{/t}。", "That came across as ", "cold", "coldly", "."), ("as の後ろは{t}形容詞「いら立っている」{/t}。", "That came across as ", "impatient", "impatiently", "."), ("as の後ろは{t}形容詞「分かりにくい」{/t}。", "That came across as ", "unclear", "unclearly", ".")), (("sound の後ろは{t}形容詞「失礼な」{/t}。", "I didn't mean to sound ", "rude", "rudely", "."), ("sound の後ろは{t}形容詞「冷たい」{/t}。", "I didn't mean to sound ", "cold", "coldly", "."), ("sound の後ろは{t}形容詞「いら立っている」{/t}。", "I didn't mean to sound ", "impatient", "impatiently", "."), ("sound の後ろは{t}形容詞「分かりにくい」{/t}。", "I didn't mean to sound ", "unclear", "unclearly", "."))),
        (rule("Impact as an impression", "印象としての影響", "come across as + <b>adjective</b>", "Name how it sounded", "どう聞こえたかを示す", ("That came across as <b>rude</b>.", "That came across as <b>cold</b>.")), rule("Intent plus sound adjective", "意図＋sound＋形容詞", "didn't mean to + <b>sound + adjective</b>", "Separate intent from effect", "意図と影響を分ける", ("I didn't mean to sound <b>rude</b>.", "I didn't mean to sound <b>impatient</b>."))),
        tip("Came across as rude or sounded rude?", "印象に焦点・直接的な評価", "“Came across as” foregrounds the listener's impression and can feel less absolute. “Sounded rude” is a more direct judgment.", "came across as は聞き手の印象に焦点を置き、断定を弱められます。sounded rude はより直接的な評価です。", ("Focus on impression", "受けた印象", "That came across as rude.", "その言い方は失礼に聞こえました。"), ("Direct judgment", "直接的な評価", "That sounded rude.", "それは失礼に聞こえました。")),
    ),
}


VOCAB = {
    103: dict(new="worries|心配させる; suggest|提案する; concern|懸念; bottom line|要するに; the real question is|本当の問題は", recycled="schedule|予定|CORE-67; deadline|期限|CORE-82; quality|品質|CORE-85; data|データ|CORE-85; client|顧客|CORE-54; great|よかった|CORE-33; thanks|ありがとう|CORE-9", assumed="cost|費用; wait|待つ; week|週; start|始める; ask|聞く; check|確認する; compare|比べる; date|日付; decide|決める; decision|判断; discuss|話す; then|そうすれば; two|二つ", receptive="deliberate focus|意図的な焦点"),
    104: dict(new="matters|重要である; precisely|まさに; that's the thing|そこが重要な点", recycled="timing|タイミング|CORE-85; price|値段|CORE-19; schedule|予定|CORE-67; budget|予算|CORE-53; quality|品質|CORE-85; deadline|期限|CORE-82; client|顧客|CORE-54; called|電話した|CORE-36; know|分かる|CORE-62; thanks|ありがとう|CORE-9; suggest|提案する|CORE-103; final version|最終版|CORE-83", assumed="speed|速さ; format|形式; date|日付; afternoon|午後; change|変更する; choose|選ぶ; clear|明確な; give|与える; Ken|ケン; Maya|マヤ; next|次; perfect|よかった; Sam|サム; send|送る; step|一歩; then|それなら; us|私たち; Yuki|ユキ", receptive="cleft|分裂文; deciding element|決め手"),
    105: dict(new="longer|より長く; harder|より難しく; catch up|遅れを取り戻す; every day counts|一日一日が大切; the less, the better|少ないほどよい", recycled="sooner|もっと早く|CORE-71; book|予約する|CORE-41; great|よかった|CORE-33; know|分かる|CORE-62; mind|気にする|CORE-60; urgent|緊急の|CORE-83", assumed="wait|待つ; finish|終える; find|見つける; room|部屋; start|始める; arrive|着く; decide|決める; ask|聞く; come|来る; confirm|確認する; file|ファイル; fix|直す; good|よい; group|グループ; it'll|〜になる; leave|出る; prepare|準備する; size|人数", receptive="linked change|連動する変化"),
    106: dict(new="worth raising|取り上げる価値がある; a couple of|二つほど; if I may|差し支えなければ; while we're on it|この話のついでに", recycled="issue|問題|CORE-82; option|選択肢|CORE-45; suggest|提案する|CORE-103; draft|下書き|CORE-82; point|点|CORE-85; concern|懸念|CORE-103", assumed="one thing|一つの点; change|変える; check|確認する; add|加える; detail|詳細; discuss|話し合う; review|見直す; few|いくつか; fine|問題ない; good|よい; important|重要な; look|見える; mark|印を付ける; perfect|よかった; start|始める; them|それら; three|三つ; two|二つ; worth discussing|話し合う価値がある; worth checking|確認する価値がある; worth reviewing|見直す価値がある", receptive="announce|予告する; approximate|およその"),
    107: dict(new="As for|〜については; Coming back to|〜に話を戻す; timeline|予定表; firm date|確定日; on that note|その流れで; while I remember|思い出したついでに", recycled="budget|予算|CORE-53; delivery|配達|CORE-77; schedule|予定|CORE-67; price|値段|CORE-19; meeting|会議|CORE-30; great|よかった|CORE-33; reply|返事をする|CORE-80; thanks|ありがとう|CORE-9; update|更新する|CORE-37", assumed="venue|会場; wait|待つ; booked|予約済み; change|変更; answer|返事; decision|判断; second option|二つ目の案; call|電話する; decide|決める; may|かもしれない; need|必要; organise|整理する; plan|案", receptive="organise a topic|話題を整理する; speaking of|〜と言えば"),
    108: dict(new="send over|送る; figures|数字; when you get a sec|時間があるとき; at your earliest convenience|できるだけ早く", recycled="draft|下書き|CORE-82; meeting|会議|CORE-30; could|〜してもらえる|CORE-60; would|〜していただける|CORE-60; thanks|ありがとう|CORE-9", assumed="send|送る; review|確認する; confirm|確認する; date|日付; check|確認する; call|電話する; colleague|同僚; help|手伝い; able|できる; Alex|アレックス; ask|頼む; Leo|レオ; lunch|昼食; message|メッセージする; need|必要; perfect|よかった", receptive="register|言葉の調子; routine task|日常的な作業"),
    109: dict(new="bluntly|率直に; honestly|正直に; walk away|見送る; no offence, but|悪く取らないでほしいが; frankly|率直に言えば", recycled="price|値段|CORE-19; option|選択肢|CORE-45; contract|契約書|CORE-59; won't|〜しない|CORE-64", assumed="work|うまくいく; cost|費用; late|遅い; another plan|別の案; wait|待つ; say no|断る; choose|選ぶ; agent|担当者; call|電話する; give|与える; good|よい; judge|判断する; much|多すぎる; need|必要; next|次; other|もう一つ; practical|現実的な; put|言う; rather|むしろ; step|一歩; us|私たち", receptive="directness|率直さ; candid|偽りのない"),
    110: dict(new="behind schedule|予定より遅れて; I'm afraid|残念ですが; bear with me|少々お待ちください", recycled="behind|後ろに|CORE-11; unfortunately|残念ながら|CORE-34; delayed|遅れている|CORE-82; price|値段|CORE-19; hate|嫌う|CORE-27; thanks|ありがとう|CORE-9", assumed="problem|問題; delay|遅れ; finish|終える; order|注文; mistake|間違い; change|変更; bad news|悪い知らせ; booking|予約; correct|修正する; revise|変更する; say|言う; send|送る; thank|感謝する; wait|待つ; cause|原因", receptive="cushion|和らげる表現; inconvenience|不便"),
    111: dict(new="Just so you know|念のためお知らせします; Heads up|先にお知らせ; FYI|参考までに; for what it's worth|参考になるか分かりませんが", recycled="book|予約する|CORE-41; meeting|会議|CORE-30; ready|準備できた|CORE-80; client|顧客|CORE-54; price|値段|CORE-19; delayed|遅れている|CORE-82; earlier|さっき|CORE-55; great|よかった|CORE-33; tell|伝える|CORE-62; thanks|ありがとう|CORE-9; ticket|チケット|CORE-5; update|更新する|CORE-37", assumed="room|部屋; room's|部屋は; moved|変更になった; report|レポート; call|電話する; train|電車; change|変更する; group|グループ; new|新しい; rest|残り; Sam|サム; see|会う; three|3時", receptive="neutral update|中立的な更新; timely alert|早めの注意"),
    112: dict(new="come across as|〜という印象を与える; rude|失礼な; impatient|いら立っている; rephrase|言い換える; intention|意図", recycled="cold|冷たい|CORE-8; mind|気にする|CORE-60", assumed="unclear|分かりにくい; sound|聞こえる; mean to|〜するつもり; wording|言い方; message|メッセージ; answer|答え; course|もちろん; explain|説明する; politely|丁寧に; say|言う", receptive="impact|影響; repair path|修復の道筋"),
}


KNOWN_WORDS = {
    103: (("予定", "schedule"), ("期限", "deadline"), ("品質", "quality")),
    104: (("タイミング", "timing"), ("価格", "price"), ("予算", "budget")),
    105: (("もっと早く", "sooner"), ("予約する", "book"), ("終える", "finish")),
    106: (("問題", "issue"), ("選択肢", "option"), ("確認する", "check")),
    107: (("予算", "budget"), ("配達", "delivery"), ("会議", "meeting")),
    108: (("下書き", "draft"), ("送る", "send"), ("確認する", "check")),
    109: (("価格", "price"), ("選択肢", "option"), ("契約書", "contract")),
    110: (("嫌う", "hate"), ("遅れている", "delayed"), ("価格", "price")),
    111: (("会議", "meeting"), ("準備できた", "ready"), ("顧客", "client")),
    112: (("冷たい", "cold"), ("聞こえる", "sound"), ("メッセージ", "message")),
}


TRANSLATE_HINTS = {
    103: (("心配させる:worries",) * 4, ("提案する:suggest",) * 4),
    104: (("タイミング:timing", "予定:schedule", "品質:quality", "期限:deadline"), ("サム:Sam", "マヤ:Maya", "ケン:Ken", "ユキ:Yuki")),
    105: (("より長く:longer; より難しく:harder; 遅れを取り戻す:catch up", "より長く:longer; より難しく:harder; 終える:finish", "より長く:longer; より難しく:harder; 見つける:find", "より長く:longer; より難しく:harder; 直す:fix"), ("もっと早く:sooner; 始める:start", "もっと早く:sooner; 出る:leave", "もっと早く:sooner; 決める:decide", "もっと早く:sooner; 聞く:ask")),
    106: (("変える:change", "確認する:check", "加える:add", "提案する:suggest"), ("取り上げる価値がある:worth raising", "話し合う価値がある:worth discussing", "確認する価値がある:worth checking", "見直す価値がある:worth reviewing")),
    107: (("〜については:As for",) * 4, ("〜に話を戻す:Coming back to",) * 4),
    108: (("送る:send", "下書き:draft", "日付:date", "数字:figures"), ("時間があるとき:when you get a sec",) * 4),
    109: (("率直に:bluntly",) * 4, ("正直に:honestly",) * 4),
    110: (("予定より遅れている:behind", "終える:finish", "遅れている:delayed", "価格:price"), ("問題:problem", "遅れ:delay", "間違い:mistake", "変更:change")),
    111: (("念のためお知らせします:Just so you know",) * 4, ("先にお知らせ:Heads up",) * 4),
    112: (("〜という印象を与える:come across as",) * 4, ("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear")),
}


OPEN_MENUS = {
    103: (("心配させる:worries", "予定:schedule", "期限:deadline", "品質:quality"), ("提案する:suggest", "データ:data", "顧客:client", "始める:start")),
    104: (("重要である:matters", "タイミング:timing", "価格:price", "品質:quality"), ("提案する:suggest", "顧客:client", "日付:date", "最終版:final version")),
    105: (("より長く:longer", "より難しく:harder", "遅れを取り戻す:catch up"), ("もっと早く:sooner", "始める:start", "終える:finish", "予約する:book")),
    106: (("一つの点:one thing", "変える:change", "確認する:check", "加える:add"), ("取り上げる価値がある:worth raising", "問題:issue", "選択肢:option")),
    107: (("〜については:As for", "予算:budget", "配達:delivery", "予定:schedule"), ("〜に話を戻す:Coming back to", "予定表:timeline", "確定日:firm date", "会議:meeting")),
    108: (("送る:send over", "下書き:draft", "数字:figures", "日付:date"), ("時間があるとき:when you get a sec", "送る:send", "確認する:check", "電話する:call")),
    109: (("率直に:bluntly", "費用:cost", "遅い:late", "別の案:another plan"), ("正直に:honestly", "見送る:walk away", "待つ:wait", "断る:say no")),
    110: (("予定より遅れて:behind schedule", "終える:finish", "遅れている:delayed", "価格:price"), ("残念ですが:I'm afraid", "問題:problem", "間違い:mistake", "変更:change")),
    111: (("念のためお知らせします:Just so you know", "会議:meeting", "準備できた:ready", "顧客:client"), ("先にお知らせ:Heads up", "価格:price", "遅れている:delayed", "電車:train")),
    112: (("〜という印象を与える:come across as", "失礼な:rude", "冷たい:cold", "いら立っている:impatient"), ("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear")),
}


SUPPORT_EXPRESSIONS = {
    103: (("The real question is whether we can wait.", "本当の問題は、待てるかどうかです。"), ("The bottom line is the cost.", "要するに、問題は費用です。")),
    104: (("Precisely. The timing is the point.", "そのとおりです。重要なのはタイミングです。"), ("That's the thing — we don't have a date.", "そこが問題です。日付が決まっていません。")),
    105: (("Every day counts.", "一日一日が大切です。"), ("For changes, the less, the better.", "変更は少なければ少ないほどいいです。")),
    106: (("There's one concern, if I may.", "差し支えなければ、一つ懸念があります。"), ("While we're on it, there are two details worth checking.", "この話のついでに、確認したい点が二つあります。")),
    107: (("On that note, what about the date?", "その流れで、日付はどうなっていますか？"), ("While I remember, the venue is booked.", "思い出したついでに、会場は予約済みです。")),
    108: (("Please send it at your earliest convenience.", "できるだけ早く送ってください。"), ("Can you check it when you get a sec?", "時間があるときに確認してくれる？")),
    109: (("No offence, but I don't think it'll work.", "悪く取らないでほしいのですが、うまくいかないと思います。"), ("Frankly, I'd choose the other option.", "率直に言えば、私ならもう一つの案を選びます。")),
    110: (("Unfortunately, the order is delayed.", "残念ながら、注文が遅れています。"), ("Please bear with me while I check.", "確認しますので、少々お待ちください。")),
    111: (("FYI, the report is ready.", "参考までに、レポートは準備できています。"), ("For what it's worth, Sam called earlier.", "参考になるか分かりませんが、サムから先ほど電話がありました。")),
    112: (("That wasn't my intention.", "そのつもりではありませんでした。"), ("Let me rephrase that.", "言い換えさせてください。")),
}


DIALOGUES = {
    103: dict(model=("Project lead", 0, 0, ("We need to choose between the two plans. What's your main concern?", "二つの案から選ぶ必要があります。一番の懸念は何ですか？"), ("I agree. What do you recommend?", "同感です。どうするのがよいと思いますか？"), ("Okay. I'll ask the client for one more week.", "分かりました。顧客にもう1週間頼みます。"), ("Thanks. Then we can check the data before we decide.", "ありがとうございます。そうすれば判断前にデータを確認できます。")), wild=("Community organiser", 1, 1, ("We need to choose the event date. What's the biggest risk?", "イベントの日付を決める必要があります。一番のリスクは何ですか？"), ("Right. What should we do before deciding?", "そうですね。決める前に何をすべきですか？"), ("I'll send you the attendance data today.", "今日、参加者データを送ります。"), ("Great. Then we can compare the two dates.", "よかったです。そうすれば二つの日付を比べられます。"))),
    104: dict(model=("Teammate", 0, 0, ("We're comparing two suppliers. Which point should decide it?", "二つの取引先を比べています。何を決め手にすべきですか？"), ("I agree. Who first proposed the change?", "同感です。最初に変更を提案したのは誰ですか？"), ("Right. I'll ask Sam for the new schedule.", "そうですね。サムに新しい日程を聞きます。"), ("Thanks. That gives us a clear next step.", "ありがとうございます。次にすることがはっきりしました。")), wild=("Event coordinator", 2, 1, ("The fast venue is noisy. What should matter more?", "早く使える会場は騒がしいです。何を重視すべきですか？"), ("Good point. Who contacted the client about it?", "確かに。顧客に連絡したのは誰ですか？"), ("I'll use Maya's notes to compare the venues.", "マヤのメモを使って会場を比べます。"), ("Perfect. Then we can choose this afternoon.", "よかったです。では今日の午後に選べます。"))),
    105: dict(model=("Project manager", 0, 0, ("We're already two weeks behind. Can we wait?", "すでに2週間遅れています。待てますか？"), ("Then when should we begin?", "では、いつ始めるべきですか？"), ("Agreed. I'll schedule the first task for today.", "賛成です。最初の作業を今日に設定します。"), ("Great. I'll prepare the files now.", "よかったです。今、ファイルを準備します。")), wild=("Hotel planner", 2, 2, ("The rooms are filling up. Should we delay the booking?", "部屋が埋まってきています。予約を遅らせますか？"), ("I see. So when should we choose?", "分かりました。では、いつ選ぶべきですか？"), ("Let's decide today and book the rooms.", "今日決めて部屋を予約しましょう。"), ("Good. I'll confirm the group size now.", "分かりました。今、人数を確認します。"))),
    106: dict(model=("Reviewer", 0, 0, ("What did you think of the draft?", "下書きについてどう思いましたか？"), ("Okay. Is there anything else we should discuss?", "分かりました。ほかに話すべきことはありますか？"), ("Let's list all three points now.", "では三つの点を今まとめましょう。"), ("Good. I'll start with the most important one.", "分かりました。一番重要な点から始めます。")), wild=("Café owner", 1, 2, ("How does the new menu look?", "新しいメニューはどうですか？"), ("Please show me. Is there anything else before we print it?", "見せてください。印刷前にほかにありますか？"), ("Let's check the prices and names together.", "価格と名前を一緒に確認しましょう。"), ("Perfect. I'll mark them on the draft.", "分かりました。下書きに印を付けます。"))),
    107: dict(model=("Manager", 0, 0, ("We've covered the design. What about the budget?", "デザインは確認しました。予算はどうですか？"), ("Okay. Let's return to timing. What do we need?", "分かりました。日程の話に戻りましょう。何が必要ですか？"), ("I'll call the client for both answers.", "両方の答えを聞くため顧客に電話します。"), ("Thanks. We can decide after that call.", "ありがとうございます。その電話のあとに決められます。")), wild=("Event organiser", 1, 3, ("The venue is confirmed. What about delivery?", "会場は確定しました。配達はどうですか？"), ("Understood. Let's return to the second option. What do we need?", "分かりました。二つ目の案に戻りましょう。何が必要ですか？"), ("I'll ask the supplier today.", "今日、取引先に聞きます。"), ("Great. I'll update the plan when they reply.", "よかったです。返事が来たら案を更新します。"))),
    108: dict(model=("Project lead", 0, 3, ("We need the report from a new supplier. How will you ask?", "新しい取引先からレポートをもらう必要があります。どう頼みますか？"), ("Good. You also need the date from Alex, your close teammate. How will you ask?", "いいですね。親しい同僚のアレックスから日付も必要です。どう頼みますか？"), ("Those levels fit. I'll send the supplier request.", "その調子で合っています。取引先への依頼は私が送ります。"), ("Thanks. I'll message Alex now.", "ありがとうございます。今アレックスにメッセージします。")), wild=("Trip coordinator", 2, 1, ("We need the date from the hotel manager. How will you ask?", "ホテルの責任者から日付を聞く必要があります。どう頼みますか？"), ("Great. Your close teammate Leo also has the plan. How will you ask him to review it?", "いいですね。親しい同僚のレオも案を持っています。確認をどう頼みますか？"), ("Good. I'll contact the hotel manager.", "分かりました。ホテルの責任者に連絡します。"), ("Perfect. I'll ask Leo before lunch.", "よかったです。昼食前にレオへ頼みます。"))),
    109: dict(model=("Consultant", 0, 0, ("We need a decision on this plan. What's your honest view?", "この案について判断が必要です。率直な意見は？"), ("Understood. If you were responsible, what would you do?", "分かりました。担当者ならどうしますか？"), ("Then I'll reject this proposal and ask for a new one.", "ではこの提案は断り、新しい案を頼みます。"), ("Good. That gives us a practical next step.", "分かりました。現実的な次の一歩になりました。")), wild=("Friend", 1, 2, ("This rental contract has two extra fees. What do you think?", "この賃貸契約には追加料金が二つあります。どう思いますか？"), ("Would you accept it?", "受け入れますか？"), ("I agree. Let's look at the other apartment.", "同感です。もう一つのアパートを見ましょう。"), ("Yes. I'll call the agent now.", "はい。今、不動産会社に電話します。"))),
    110: dict(model=("Team lead", 0, 2, ("Can we still finish the report on time?", "レポートはまだ期限どおりに終えられますか？"), ("I understand. What caused the delay?", "分かりました。遅れの原因は何ですか？"), ("I'll move the review to Friday and tell the client.", "確認を金曜日に移し、顧客に伝えます。"), ("Thanks. I'll send the revised schedule now.", "ありがとうございます。今、変更した日程を送ります。")), wild=("Hotel agent", 3, 2, ("Is everything correct with the group booking?", "団体予約はすべて正しいですか？"), ("I see. What caused the price change?", "分かりました。価格変更の原因は何ですか？"), ("I'll check the booking and send a corrected price.", "予約を確認し、修正した価格を送ります。"), ("Thank you. I'll wait for the corrected booking.", "ありがとうございます。修正した予約を待ちます。"))),
    111: dict(model=("Coworker", 0, 0, ("Anything I should know before I leave?", "出る前に知っておくことはありますか？"), ("Thanks. Has the meeting time changed?", "ありがとう。会議の時間は変わりましたか？"), ("I'll update my calendar now.", "今、カレンダーを更新します。"), ("Great. See you in the booked room at three.", "よかったです。3時に予約した部屋で会いましょう。")), wild=("Travel companion", 2, 2, ("Is there any update before we go to the station?", "駅へ行く前に何か更新はありますか？"), ("Good to know. Is the train still on time?", "分かりました。電車はまだ時間どおりですか？"), ("Then I'll change our departure time.", "では出発時刻を変えます。"), ("Thanks. I'll tell the rest of the group.", "ありがとう。ほかのメンバーに伝えます。"))),
    112: dict(model=("Coworker", 0, 0, ("Your message said, 'Do it now.' How do you think it sounded?", "あなたのメッセージは「今やって」でした。どう聞こえたと思いますか？"), ("Yes, it did. Was that what you intended?", "そう聞こえました。それが意図でしたか？"), ("Thanks for saying that. Could you rephrase it?", "そう言ってくれてありがとう。言い換えてもらえますか？"), ("Of course. I'll say, 'Could you do it today?'", "もちろんです。「今日してもらえますか」と言います。")), wild=("Teammate", 1, 1, ("Your reply only said, 'No. Read the email.' How did it sound?", "返信は「いいえ。メールを読んで」だけでした。どう聞こえましたか？"), ("I agree. Was that your intention?", "同感です。それが意図でしたか？"), ("Okay. Please send a warmer reply.", "分かりました。もっと温かい返信を送ってください。"), ("I will. I'll explain the answer politely.", "そうします。丁寧に答えを説明します。"))),
}


LIVE_SCENES = {
    103: (("text", "other", "Tutor", "Think of a decision you are actually considering, or use a practice decision. What is your main concern and suggestion?", "実際に検討中の判断を思い浮かべるか、練習用の判断を使いましょう。一番の懸念と提案は何ですか？"), ("input", "me", "Me", "What worries me most is ___. What I'd suggest is ___. / I don't have a decision to discuss today.", "一番心配なのは___です。私が提案したいのは___です。／今日は相談する判断がありません。"), ("text", "me", "Me", "What worries you most about a decision right now, and what would you suggest?", "先生が今考えている判断で一番心配なことと、提案は何ですか？"), ("input", "other", "Tutor", "Tutor's real concern and suggestion, or no current decision:", "先生の実際の懸念と提案、または今は判断がないという答え")),
    104: (("text", "other", "Tutor", "Think of a group decision. What matters most, and who suggested the current idea?", "グループの判断を考えましょう。何が一番重要で、今の案を提案したのは誰ですか？"), ("input", "me", "Me", "It's ___ that matters, not ___. It was ___ who ___. / I don't know who suggested it.", "重要なのは___ではなく___です。___したのは___です。／誰が提案したか分かりません。"), ("text", "me", "Me", "In one of your recent decisions, what mattered most and who suggested the idea?", "先生が最近した判断では、何が一番重要で、誰が提案しましたか？"), ("input", "other", "Tutor", "Tutor's real deciding point and person, or no recent example:", "先生の実際の決め手と人、または最近の例はないという答え")),
    105: (("text", "other", "Tutor", "Think of a real task that could get harder if delayed. What changes together?", "遅らせると難しくなる実際の作業を考えましょう。何と何が連動しますか？"), ("input", "me", "Me", "The longer we ___, the harder it'll be to ___. The sooner we ___, the sooner we can ___. / Nothing urgent comes to mind.", "___するのが遅いほど、___するのが難しくなります。___するのが早いほど、___できます。／急ぐことは思いつきません。"), ("text", "me", "Me", "What task gets harder for you when it is delayed?", "先生にとって、遅らせると難しくなる作業は何ですか？"), ("input", "other", "Tutor", "Tutor's real linked change, or no urgent task:", "先生の実際に連動する変化、または急ぐ作業はないという答え")),
    106: (("text", "other", "Tutor", "Think of something you reviewed recently. Is there one change or a few issues worth raising?", "最近確認したものを考えましょう。変えたい一点や、取り上げたい問題はありますか？"), ("input", "me", "Me", "There's one thing I'd ___. There are ___ worth ___ing. / Everything looks fine to me.", "一つ___したい点があります。___する価値のある___があります。／私にはすべて問題なく見えます。"), ("text", "me", "Me", "Is there one thing you would change about something you use often?", "先生がよく使うものに、一つ変えたい点はありますか？"), ("input", "other", "Tutor", "Tutor's real point, or nothing to change:", "先生の実際の一点、または変えたいことはないという答え")),
    107: (("text", "other", "Tutor", "Choose two real topics from one plan. Give an update on the first, then return to the second.", "一つの計画から実際の話題を二つ選びましょう。一つ目を更新し、二つ目に戻ってください。"), ("input", "me", "Me", "As for ___, ___. Coming back to ___, ___. / I don't have any updates to organise.", "___については、___です。___の話に戻ると、___です。／整理する更新はありません。"), ("text", "me", "Me", "What two topics and updates would you organise in a plan today?", "先生なら今日の計画で、どの二つの話題と更新を整理しますか？"), ("input", "other", "Tutor", "Tutor's real two topics and updates, or no plan today:", "先生の実際の二つの話題と更新、または今日は計画がないという答え")),
    108: (("text", "other", "Tutor", "What small task could you ask a colleague to do today? A practice request is fine.", "今日、同僚に頼める小さな作業は何ですか？ 練習用の依頼でも構いません。"), ("input", "me", "Me", "Would you be able to ___? / Can you ___ when you get a sec? / I don't need help right now.", "___していただくことはできますか？／時間があるときに___してくれる？／今は手伝いが必要ありません。"), ("text", "me", "Me", "What small task would you like help with today?", "先生は今日、どんな小さな作業を手伝ってほしいですか？"), ("input", "other", "Tutor", "Tutor's real task, or no task today:", "先生の実際の作業、または今日は作業がないという答え")),
    109: (("text", "other", "Tutor", "Think of a low-stakes plan you can judge safely. What's your candid view?", "気軽に判断できる重要度の低い案を考えましょう。率直な意見は？"), ("input", "me", "Me", "To put it bluntly, ___. Honestly? I'd ___. / I'd rather not judge it yet.", "率直に言えば、___です。正直に言うと、私なら___します。／まだ判断は控えたいです。"), ("text", "me", "Me", "What's your honest view of one low-stakes option you've considered?", "先生が検討した重要度の低い選択肢について、率直な意見は？"), ("input", "other", "Tutor", "Tutor's real candid view, or no safe example:", "先生の実際の率直な意見、または適切な例はないという答え")),
    110: (("text", "other", "Tutor", "Give me one clear piece of imaginary bad news about a routine plan.", "日常的な計画について、想像上の悪い知らせを一つ明確に伝えてください。"), ("input", "me", "Me", "I hate to say it, but ___. I'm afraid ___. / There's no bad news today.", "言いにくいのですが、___です。残念ですが、___です。／今日は悪い知らせはありません。"), ("text", "me", "Me", "Can you give me one piece of imaginary bad news about a routine plan?", "先生も日常的な計画について、想像上の悪い知らせを一つ言えますか？"), ("input", "other", "Tutor", "Tutor's imaginary bad news for practice, or none today:", "先生の練習用の想像上の悪い知らせ、または今日はないという答え")),
    111: (("text", "other", "Tutor", "Think of one update. If it is simply useful, use a neutral lead-in. If I need it before acting, use a timely alert.", "更新を一つ考えましょう。単に役立つ情報なら中立的な前置きを使い、先生が行動する前に必要な情報なら早めの注意喚起を使ってください。"), ("input", "me", "Me", "Just so you know, ___. / Heads up — ___. / There's nothing new to report.", "念のためお知らせすると、___です。／先に知らせておくと、___です。／新しく知らせることはありません。"), ("text", "me", "Me", "Do you have a neutral update or a timely alert for me?", "先生から私への中立的な更新、または早めの注意喚起はありますか？"), ("input", "other", "Tutor", "Tutor's real neutral update or timely alert, or nothing new:", "先生の実際の中立的な更新または早めの注意喚起、あるいは新しいことはないという答え")),
    112: (("text", "other", "Tutor", "Think of a low-stakes message that sounded harsher than intended. Give the wording, its effect, and a repair.", "意図よりきつく聞こえた重要度の低いメッセージを考え、その文面、与えた印象、言い換えを伝えてください。"), ("input", "me", "Me", "The message was \"___.\" That came across as ___. I didn't mean to sound ___. I'd rephrase it as \"___.\" / Nothing comes to mind.", "元のメッセージは「___」でした。それは___という印象でした。___に聞こえるつもりはありませんでした。「___」と言い換えます。／思いつきません。"), ("text", "me", "Me", "Can you give a real low-stakes example and how you repaired it?", "先生も重要度の低い実際の例と、その言い換えを教えてもらえますか？"), ("input", "other", "Tutor", "Tutor's real example, effect, and repaired wording, or no example:", "先生の実際の例、与えた印象、言い換えた文面、または例はないという答え")),
}


LIVE_HINTS = {n: {1: OPEN_MENUS[n][0] + OPEN_MENUS[n][1]} for n in NUMBERS}
LIVE_HINTS[112] = {1: ("メッセージ:message", "言い換える:rephrase", "失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear")}

TRANSFER_SCENES = {103: "community event date", 104: "venue selection", 105: "group hotel booking", 106: "cafe menu review", 107: "event delivery planning", 108: "hotel and teammate requests", 109: "rental contract decision", 110: "group booking correction", 111: "travel departure update", 112: "cold written reply repair"}

BRIEF_PRODUCTION_MODELS = {n: (core.strip_marks(LESSONS[n]["p1"][0][0]), core.strip_marks(LESSONS[n]["p2"][0][0])) for n in NUMBERS}

DIALOGUE_SEMANTIC_LEDGER = {
    103: dict(model=("lead establishes decision", "learner focuses cost concern", "lead asks recommendation", "learner recommends delay", "lead secures time", "learner names use of time"), wild=("organiser establishes date decision", "learner focuses schedule", "organiser asks next step", "learner recommends data check", "organiser provides data", "learner names comparison")),
    104: dict(model=("teammate establishes supplier choice", "learner focuses timing", "teammate asks originator", "learner identifies Sam", "teammate requests schedule", "learner confirms next step"), wild=("coordinator establishes venue tradeoff", "learner focuses quality", "coordinator asks contact", "learner identifies Maya", "coordinator uses notes", "learner schedules decision")),
    105: dict(model=("manager establishes delay", "learner links delay to difficulty", "manager asks start", "learner links early start to finish", "manager schedules task", "learner begins preparation"), wild=("planner establishes scarce rooms", "learner links waiting to difficulty", "planner asks choice time", "learner links decision to booking", "planner decides today", "learner confirms group size")),
    106: dict(model=("reviewer asks draft view", "learner announces one change", "reviewer asks further points", "learner announces issues", "reviewer sets listing action", "learner prioritises first point"), wild=("owner asks menu view", "learner announces check", "owner asks further points", "learner announces details", "owner sets joint check", "learner marks draft")),
    107: dict(model=("manager transitions from design", "learner updates budget", "manager returns to timing", "learner requests firm date", "manager seeks both answers", "learner waits to decide"), wild=("organiser confirms venue", "learner updates delivery", "organiser returns to option", "learner requests firm date", "organiser asks supplier", "learner updates on reply")),
    108: dict(model=("lead establishes distant recipient", "learner forms careful request", "lead establishes close recipient", "learner forms informal request", "lead sends supplier request", "learner messages teammate"), wild=("coordinator establishes hotel request", "learner forms careful date request", "coordinator establishes teammate request", "learner forms informal review request", "coordinator contacts hotel", "learner contacts teammate")),
    109: dict(model=("consultant requests candid plan view", "learner rejects workability", "consultant asks action", "learner chooses withdrawal", "consultant rejects proposal", "learner validates next step"), wild=("friend establishes extra fees", "learner rejects price", "friend asks acceptance", "learner declines", "friend chooses other apartment", "learner calls agent")),
    110: dict(model=("lead asks deadline status", "learner cushions delay", "lead asks cause", "learner reports underlying mistake", "lead revises review", "learner sends schedule"), wild=("agent asks booking accuracy", "learner reports price change", "agent asks cause", "learner reports mistake", "agent corrects booking", "learner awaits correction")),
    111: dict(model=("coworker asks update", "learner reports booked room", "coworker asks time change", "learner alerts meeting move", "coworker updates calendar", "learner confirms time and place"), wild=("companion asks travel update", "learner reports ready report", "companion asks train", "learner alerts delay", "companion changes departure", "learner tells group")),
    112: dict(model=("coworker quotes abrupt message", "learner names rude impact", "coworker asks intent", "learner separates intent", "coworker asks repair", "learner provides polite rewrite"), wild=("teammate quotes cold reply", "learner names cold impact", "teammate asks intent", "learner separates intent", "teammate asks warmer reply", "learner commits explanation")),
}


ROLE_JA = {
    "Café owner": "カフェの店主",
    "Community organiser": "地域イベントの主催者",
    "Consultant": "コンサルタント",
    "Coworker": "同僚",
    "Event coordinator": "イベントの調整担当者",
    "Event organiser": "イベントの主催者",
    "Friend": "友人",
    "Hotel agent": "ホテルの予約担当者",
    "Hotel planner": "ホテル手配の担当者",
    "Manager": "上司",
    "Project lead": "プロジェクトリーダー",
    "Project manager": "プロジェクトマネージャー",
    "Reviewer": "レビュー担当者",
    "Team lead": "チームリーダー",
    "Teammate": "チームメンバー",
    "Travel companion": "旅行仲間",
    "Trip coordinator": "旅行の調整担当者",
}


# Proofread operating copy and personal conversation for this owned lane.
WRITE_FRAMES = {
    103: ("What worries me most is ___", "What I'd suggest is ___"),
    104: ("It's ___ that matters", "It was ___ who ___"),
    105: ("The longer ___, the harder ___", "The sooner ___, the sooner ___"),
    106: ("There's one thing I'd ___", "There are ___ worth ___ing"),
    107: ("As for ___, ___", "Coming back to ___, ___"),
    108: ("Would you be able to ___?", "Can you ___ when you get a sec?"),
    109: ("To put it bluntly, ___", "Honestly? I'd ___"),
    110: ("I hate to say it, but ___", "I'm afraid ___"),
    111: ("Just so you know, ___", "Heads up — ___"),
    112: ("That came across as ___", "I didn't mean to sound ___"),
}

FREE_TALK = {
    103: (
        "When you make a big decision, what do you worry about first?",
        "大きな判断をするとき、最初に何を心配しますか？",
        "What about you—what do you worry about first?",
        "先生はどうですか？最初に何を心配しますか？",
    ),
    104: (
        "What usually matters most when you choose between two options?",
        "二つの選択肢から選ぶとき、普段いちばん重要なのは何ですか？",
        "What about you—what usually matters most?",
        "先生はどうですか？普段いちばん重要なのは何ですか？",
    ),
    105: (
        "What is one task you prefer to start early, and why?",
        "早めに始めたい作業は何ですか？なぜですか？",
        "What about you—what do you prefer to start early?",
        "先生はどうですか？何を早めに始めたいですか？",
    ),
    106: (
        "If you could change one small thing about a service you use, what would it be?",
        "利用しているサービスを一つだけ少し変えられるなら、何を変えますか？",
        "What about you—what small thing would you change?",
        "先生はどうですか？どんな小さなことを変えたいですか？",
    ),
    107: (
        "Is it easy for you to follow a conversation that changes topics often?",
        "話題がよく変わる会話についていくのは簡単ですか？",
        "What about you—is it easy to follow changing topics?",
        "先生はどうですか？話題が変わる会話についていくのは簡単ですか？",
    ),
    108: (
        "Do you prefer people to ask you directly or very politely for help? Why?",
        "人から頼まれるなら、直接的な言い方と、とても丁寧な言い方のどちらが好きですか？なぜですか？",
        "What about you—which kind of request do you prefer?",
        "先生はどうですか？どちらの頼み方が好きですか？",
    ),
    109: (
        "Do you prefer honest feedback that is direct or gentle? Why?",
        "率直で直接的な意見と、やわらかい意見のどちらが好きですか？なぜですか？",
        "What about you—do you prefer direct or gentle feedback?",
        "先生はどうですか？直接的な意見とやわらかい意見のどちらが好きですか？",
    ),
    110: (
        "What makes difficult news easier for you to hear?",
        "言いにくい知らせを聞くとき、どんな伝え方なら受け取りやすいですか？",
        "What about you—what makes difficult news easier to hear?",
        "先生はどうですか？どんな伝え方なら聞きやすいですか？",
    ),
    111: (
        "How do you prefer to receive a last-minute update?",
        "直前の変更は、どんな方法で知らせてもらいたいですか？",
        "What about you—how do you prefer to get an update?",
        "先生はどうですか？どんな方法で知らせてもらいたいですか？",
    ),
    112: (
        "Have you ever misunderstood someone's tone in a message? What happened?",
        "メッセージの口調を誤解したことはありますか？何がありましたか？",
        "What about you—have you ever misunderstood a message's tone?",
        "先生はどうですか？メッセージの口調を誤解したことはありますか？",
    ),
}

# Whole-sentence translation supports non-target vocabulary without supplying
# articles, auxiliaries, inflections, or the lesson's fixed discourse frame.
TRANSLATE_HINTS = {
    103: (
        ("費用:cost", "予定:schedule", "期限:deadline", "品質:quality"),
        ("待つ:wait; 週:week", "確認する:check; データ:data", "聞く:ask; 顧客:client", "始める:start; 明日:tomorrow"),
    ),
    104: (
        ("タイミング:timing; 価格:price", "予定:schedule; 予算:budget", "品質:quality; 速さ:speed", "期限:deadline; 形式:format"),
        ("サム:Sam; 提案する:suggest", "マヤ:Maya; 電話した:called; 顧客:client", "ケン:Ken; 変更する:change; 日付:date", "ユキ:Yuki; 送る:send; 最終版:final version"),
    ),
    105: (
        ("遅れを取り戻す:catch up", "終える:finish", "見つける:find; 部屋:room", "直す:fix"),
        ("始める:start; 終える:finish", "出る:leave; 着く:arrive", "決める:decide; 予約する:book", "聞く:ask; 分かる:know"),
    ),
    106: (
        ("変える:change", "確認する:check", "加える:add", "提案する:suggest"),
        ("問題:issue; 取り上げる:raise", "点:point; 話し合う:discuss", "詳細:detail; 確認する:check", "選択肢:option; 見直す:review"),
    ),
    107: (
        ("予算:budget; 待つ:wait", "配達:delivery; 待つ:wait", "会場:venue; 予約済み:booked", "予定:schedule; 変更:change"),
        ("予定表:timeline; 確定日:firm date", "価格:price; 返事:answer", "会議:meeting; 判断:decision", "二つ目の案:second option; 確定日:firm date"),
    ),
    108: (
        ("送る:send over", "確認する:review; 下書き:draft", "確認する:confirm; 日付:date", "確認する:check; 数字:figures"),
        ("送る:send over", "確認する:review", "電話する:call", "確認する:check; 日付:date"),
    ),
    109: (
        ("うまくいく:work", "費用:cost", "遅い:late", "別の案:another plan"),
        ("見送る:walk away", "待つ:wait", "断る:say no", "選ぶ:choose; 選択肢:option"),
    ),
    110: (
        ("予定より遅れている:behind", "終える:finish", "遅れている:delayed", "価格:price; 変更:change"),
        ("問題:problem", "遅れ:delay", "間違い:mistake", "変更:change"),
    ),
    111: (
        ("部屋:room; 予約する:book", "会議:meeting; 変更になった:moved", "チケット:ticket; 準備できた:ready", "顧客:client; 電話する:call"),
        ("会議:meeting; 変更になった:moved", "価格:price; 変更する:change", "電車:train; 遅れている:delayed", "サム:Sam; 電話する:call; さっき:earlier"),
    ),
    112: (
        ("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear"),
        ("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear"),
    ),
}

OPEN_MENUS = {
    103: (("費用:cost", "予定:schedule", "期限:deadline", "品質:quality"),
          ("待つ:wait", "週:week", "データ:data", "顧客:client", "始める:start")),
    104: (("タイミング:timing", "価格:price", "予定:schedule", "品質:quality"),
          ("提案する:suggest", "電話する:call", "変更する:change", "送る:send")),
    105: (("遅れを取り戻す:catch up", "終える:finish", "見つける:find", "直す:fix"),
          ("始める:start", "終える:finish", "予約する:book", "聞く:ask")),
    106: (("変える:change", "確認する:check", "加える:add", "提案する:suggest"),
          ("問題:issue", "取り上げる:raise", "話し合う:discuss", "見直す:review")),
    107: (("予算:budget", "配達:delivery", "会場:venue", "予定:schedule"),
          ("予定表:timeline", "価格:price", "会議:meeting", "二つ目の案:second option")),
    108: (("送る:send over", "下書き:draft", "数字:figures", "日付:date"),
          ("送る:send", "確認する:review", "確認する:check", "電話する:call")),
    109: (("うまくいく:work", "費用:cost", "遅い:late", "別の案:another plan"),
          ("見送る:walk away", "待つ:wait", "断る:say no", "選ぶ:choose")),
    110: (("予定より遅れて:behind schedule", "終える:finish", "遅れている:delayed", "価格:price"),
          ("問題:problem", "遅れ:delay", "間違い:mistake", "変更:change")),
    111: (("部屋:room", "会議:meeting", "準備できた:ready", "顧客:client"),
          ("価格:price", "遅れている:delayed", "電車:train", "会議:meeting")),
    112: (("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear"),
          ("失礼な:rude", "冷たい:cold", "いら立っている:impatient", "分かりにくい:unclear")),
}

OMIT_CHOICES = {
    103: (1,),
    104: (1, 2),
    105: (1, 2),
    106: (1,),
    107: (1, 2),
    109: (1, 2),
    110: (1,),
    111: (1, 2),
}
for _number, _parts in OMIT_CHOICES.items():
    LESSONS[_number]["omit_choice"] = _parts
    _choices = list(SPECS[_number]["choices"])
    for _part in _parts:
        _choices[_part - 1] = ()
    SPECS[_number]["choices"] = tuple(_choices)

VOCAB[103]["assumed"] += "; tomorrow|明日"
VOCAB[104]["assumed"] += "; call|電話する"
VOCAB[106]["assumed"] += "; raise|取り上げる"

for _number in NUMBERS:
    _writes = []
    for _part, (_old_en, _old_ja) in enumerate(SPECS[_number]["writes"], 1):
        _frame = WRITE_FRAMES[_number][_part - 1]
        _writes.append((
            f'Use “{_frame}” to {_old_en[0].lower() + _old_en[1:]}',
            f'「{_frame}」を使って、{_old_ja}',
        ))
    SPECS[_number]["writes"] = tuple(_writes)
    _question, _question_ja, _ask_back, _ask_back_ja = FREE_TALK[_number]
    LESSONS[_number]["prompt"] = (
        "Let's talk about this topic. Answer my question, then ask me too.",
        "この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。",
    )
    LIVE_SCENES[_number] = (
        ("text", "other", "Tutor", _question, _question_ja),
        ("input", "me", "Me", "Student's answer", "自分の答え"),
        ("text", "me", "Me", _ask_back, _ask_back_ja),
        ("input", "other", "Tutor", "Tutor's answer", "先生の答え"),
    )
    LIVE_HINTS[_number] = {}


SPIRAL_MARKERS = {
    103: (("ORDER-01", "transfer"), ("REL-01", "transfer")),
    104: (("ORDER-01", "transfer"),),
    106: (("REL-01", "transfer"), ("DUMMY-01", "transfer")),
    107: (("PREP-01", "transfer"), ("REL-01", "checkpoint")),
    108: (("POLITE-01", "contrast"), ("MODAL-01", "transfer")),
    110: (("POLITE-01", "transfer"),),
    111: (("REPORT-01", "transfer"),),
    112: (("ADJ-01", "checkpoint"), ("POLITE-01", "transfer")),
}

SPIRAL_CHOICES = {
    "ORDER-01": (("英語の節は{t}主語が先{/t}。", "Inside the clause: ", "subject first", "verb first", "."), ("間接疑問の中も{t}主語が先{/t}。", "Inside the question: ", "subject first", "verb first", ".")),
    "REL-01": (("昨日届いた{t}レポート{/t}です。", "The report ", "that arrived", "arrived that", " yesterday is ready."), ("電話した{t}人{/t}です。", "The person ", "who called", "called who", " has the answer.")),
    "DUMMY-01": (("一つ問題が{t}あります{/t}。", "", "There's", "It's", " one problem."), ("今日は{t}寒いです{/t}。", "", "It's", "There's", " cold today.")),
    "PREP-01": (("予算{t}について{/t}。", "As ", "for", "to", " the budget."), ("予定表{t}に戻って{/t}。", "Coming back ", "to", "for", " the timeline.")),
    "POLITE-01": (("距離のある相手へ：送って{t}いただけますか{/t}？", "Would you ", "be able to", "have to", " send it over?"), ("親しい同僚へ：時間があるときに{t}確認してくれる{/t}？", "", "Can you", "Could I", " check it when you get a sec?")),
    "MODAL-01": (("would の後ろは動詞の{t}原形{/t}。", "Would you ", "send", "sending", " it?"), ("can の後ろは動詞の{t}原形{/t}。", "Can you ", "check", "checking", " it?")),
    "REPORT-01": (("発言内容を{t}伝える{/t}。", "Sam ", "said", "told", " the meeting had moved."), ("人に情報を{t}伝える{/t}。", "Sam ", "told me", "said me", " the meeting had moved.")),
    "ADJ-01": (("本人が{t}いら立っている{/t}。", "She sounds ", "impatient", "impatiencing", "."), ("知らせが人を{t}がっかりさせる{/t}。", "The news is ", "disappointing", "disappointed", ".")),
}

THREE_CHIP_EXCEPTIONS = {
    (109, 1): "The discourse marker and complete predicate leave three honest meaning units.",
    (109, 2): "The brief Honestly reaction has no honest reconstruction without splitting lexical units, so reorder is omitted.",
    (110, 1): "The fixed cushion and complete bad-news clause leave three honest meaning units.",
    (110, 2): "The fixed cushion and complete present-perfect clause leave three honest meaning units.",
    (111, 1): "The alert frame and complete subject-predicate leave three honest constituents.",
    (111, 2): "The alert frame and complete news predicate leave three honest meaning units.",
}


@contextlib.contextmanager
def course_data():
    names = ("LESSONS", "SPECS", "VOCAB", "KNOWN_WORDS", "TRANSLATE_HINTS", "OPEN_MENUS", "DIALOGUES", "LIVE_SCENES", "LIVE_HINTS", "SUPPORT_EXPRESSIONS", "ROLE_JA")
    previous = {name: getattr(approved, name) for name in names}
    core_previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    try:
        for name in names:
            setattr(approved, name, globals()[name])
        core.VOCAB = {n: (v["new"], v["assumed"], v["receptive"]) for n, v in VOCAB.items()}
        core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = SPECS, DIALOGUES, LIVE_SCENES
        yield
    finally:
        for name, value in previous.items():
            setattr(approved, name, value)
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = core_previous


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")', rf'\g<1>{value}\2', head, count=1)
    return head


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def growing_sentence_inputs(page):
    page = re.sub(r'<input class="space-input" type="text"([^>]*)>', r'<textarea class="space-input"\1 rows="2"></textarea>', page)
    page = re.sub(r'<input class="free-input phrase-input" type="text"([^>]*)>', r'<textarea class="free-input phrase-input"\1 rows="1"></textarea>', page)
    return re.sub(r'<input class="slot-input" type="text"([^>]*)>', r'<textarea class="slot-input phrase-input"\1 rows="1"></textarea>', page)


def spiral_page(sid, level):
    page = core.choose_words(
        f"spiral-{sid.casefold()}", "Retrieve an earlier contrast", "前の対比を思い出そう",
        "Choose the smallest form that keeps the earlier rule accurate.", "前のルールが正しくなる最小の形を選びましょう。",
        SPIRAL_CHOICES[sid],
    )
    return page.replace(f'data-page-id="spiral-{sid.casefold()}"', f'data-page-id="spiral-{sid.casefold()}" data-spiral-id="{sid}" data-spiral-level="{level}"', 1)


def customize_pages(number, data, pages):
    pages = approved.customize_pages(number, data, pages)
    result = []
    for page in pages:
        page = growing_sentence_inputs(page)
        if page_id(page) == "part3-intro":
            result.extend(spiral_page(sid, level) for sid, level in SPIRAL_MARKERS.get(number, ()))
        result.append(page)
    return result


def build(number, data):
    if number not in NUMBERS:
        raise ValueError(f"CORE-{number} is not owned by this generator")
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    level = "B2" if number <= 107 else "B2-C1"
    head = new_lesson.retarget(head, review_id=f"CORE-{number}", lesson_id=slug, level=level, title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-20")
    head = head.replace("</head>", '  <link rel="stylesheet" href="growing-inputs.css">\n</head>', 1)
    with course_data():
        head = set_vocab(head.replace('content="todo"', 'content="reviewed"'), number)
        head = core.set_proofread_status(head, "complete")
        pages = customize_pages(number, data, core.canonical_pages(number, data))
    foot = foot.replace("</body>", '  <script src="growing-inputs.js"></script>\n</body>', 1)
    out = TRACK / "courses" / COURSE / "lessons" / slug / "lesson.html"
    return out, new_lesson.redepth(head + "\n".join(pages) + foot, out)


def validate_source():
    expected = set(NUMBERS)
    for label, values in (
        ("lessons", LESSONS), ("semantic specs", SPECS), ("vocabulary", VOCAB),
        ("known words", KNOWN_WORDS), ("translation hints", TRANSLATE_HINTS),
        ("open menus", OPEN_MENUS), ("support expressions", SUPPORT_EXPRESSIONS),
        ("dialogues", DIALOGUES), ("live scenes", LIVE_SCENES),
        ("live hints", LIVE_HINTS), ("transfer scenes", TRANSFER_SCENES),
        ("brief models", BRIEF_PRODUCTION_MODELS), ("dialogue ledger", DIALOGUE_SEMANTIC_LEDGER),
    ):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-103--112")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    validate_source()
    for number in NUMBERS:
        out, text = build(number, LESSONS[number])
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        out.with_name("growing-inputs.css").write_text(NARROW_GROWING_INPUT_CSS, encoding="utf-8")
        out.with_name("growing-inputs.js").write_text(NARROW_GROWING_INPUT_JS, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print("10 Core emphasis-and-tone decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
