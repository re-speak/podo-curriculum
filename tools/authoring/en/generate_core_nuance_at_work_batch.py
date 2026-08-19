#!/usr/bin/env python3
"""Generate the explicit missing CORE-81--91 Nuance at Work decks.

CORE-82 is an approved existing deck and is deliberately preserved byte for
byte.  This source owns every semantic choice for CORE-81 and CORE-83--91;
the shared Core renderer owns only the canonical component markup.
"""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_core_course_batch as core
import new_lesson

ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-nuance-at-work"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
EXISTING_CORE82 = TRACK / "courses/core-nuance-at-work/lessons/82-were-on-track-but/lesson.html"
NUMBERS = (81, 83, 84, 85, 86, 87, 88, 89, 90, 91)


def rows(*items):
    return items


LESSONS = {
    81: dict(
        slug="im-responsible-for-customer-support", title="I'm responsible for customer support",
        ko="고객 지원을 담당하고 있어요", ja="カスタマーサポートを担当しています",
        goal=("Describe your role and the people you work with.", "自分の担当と、一緒に働く人を説明しましょう。"),
        p1=rows(
            ("{t}I'm responsible for{/t} customer support.", "カスタマーサポートを{t}担当しています{/t}。", "I'm|responsible for|customer support."),
            ("{t}I'm responsible for{/t} staff training.", "スタッフ研修を{t}担当しています{/t}。", "I'm|responsible for|staff training."),
            ("{t}I'm responsible for{/t} recruitment.", "採用を{t}担当しています{/t}。", "I'm|responsible for|recruitment."),
            ("{t}I'm responsible for{/t} client reports.", "顧客レポートを{t}担当しています{/t}。", "I'm|responsible for|client reports."),
        ),
        p2=rows(
            ("{t}I mainly work with{/t} the sales team.", "主に営業チームと{t}一緒に働いています{/t}。", "I|mainly work with|the sales team."),
            ("{t}I mainly work with{/t} the finance team.", "主に財務チームと{t}一緒に働いています{/t}。", "I|mainly work with|the finance team."),
            ("{t}I mainly work with{/t} our clients.", "主に顧客と{t}一緒に仕事をしています{/t}。", "I|mainly work with|our clients."),
            ("{t}I mainly work with{/t} new staff.", "主に新しいスタッフと{t}一緒に働いています{/t}。", "I|mainly work with|new staff."),
        ),
        rules=(("Keep responsible for with the duty or activity that follows it.", "responsible for のあとに、担当する仕事や活動を続けます。"),
               ("Use work with for the person or team you collaborate with.", "協力して働く人やチームには work with を使います。")),
        prompt=("Tell me about your real role, or say you do not have a work role right now.", "実際の担当を話すか、今は仕事上の担当がないと伝えましょう。"),
    ),
    83: dict(
        slug="so-what-youre-saying-is", title="So what you're saying is", ko="그러니까 말씀은", ja="つまり、言いたいことは",
        goal=("Restate someone's point and clarify one term.", "相手の要点を言い直し、一つの言葉を確認しましょう。"),
        p1=rows(
            ("{t}So what you're saying is{/t} we need more time.", "{t}つまり、言いたいことは{/t}、もっと時間が必要だということですね。", "So|what you're saying is|we need|more time."),
            ("{t}So what you're saying is{/t} the date may change.", "{t}つまり、言いたいことは{/t}、日程が変わるかもしれないということですね。", "So|what you're saying is|the date|may change."),
            ("{t}So what you're saying is{/t} testing comes first.", "{t}つまり、言いたいことは{/t}、テストが先だということですね。", "So|what you're saying is|testing|comes first."),
            ("{t}So what you're saying is{/t} this is the final version.", "{t}つまり、言いたいことは{/t}、これが最終版だということですね。", "So|what you're saying is|this is|the final version."),
        ),
        p2=rows(
            ("{t}What do you mean by{/t} 'ready'?", "「ready」とは{t}どういう意味ですか{/t}？", "What do you mean|by|'ready'?"),
            ("{t}What do you mean by{/t} 'final'?", "「final」とは{t}どういう意味ですか{/t}？", "What do you mean|by|'final'?"),
            ("{t}What do you mean by{/t} 'urgent'?", "「urgent」とは{t}どういう意味ですか{/t}？", "What do you mean|by|'urgent'?"),
            ("{t}What do you mean by{/t} 'approved'?", "「approved」とは{t}どういう意味ですか{/t}？", "What do you mean|by|'approved'?"),
        ),
        rules=(("Keep what you're saying as the subject, then add the point you understood.", "what you're saying を主語として保ち、そのあとに理解した要点を続けます。"),
               ("Put the word or idea you want clarified after mean by.", "確認したい言葉や考えを mean by のあとに置きます。")),
        prompt=("Restate one real point from our conversation, or say there is nothing to restate yet.", "この会話の要点を一つ言い直すか、まだ言い直す内容がないと伝えましょう。"),
    ),
    84: dict(
        slug="i-was-wondering-if-you-could", title="I was wondering if you could", ko="혹시 해 주실 수 있을까요", ja="もしよければ、していただけますか",
        goal=("Make a diplomatic request and offer a bounded alternative.", "丁寧に頼み、範囲を限った代案を出しましょう。"),
        p1=rows(
            ("{t}I was wondering if you could{/t} extend the deadline.", "期限を延ばして{t}いただけないでしょうか{/t}。", "I was wondering if you could|extend|the deadline."),
            ("{t}I was wondering if you could{/t} review the draft.", "下書きを確認して{t}いただけないでしょうか{/t}。", "I was wondering if you could|review|the draft."),
            ("{t}I was wondering if you could{/t} move the meeting.", "会議を変更して{t}いただけないでしょうか{/t}。", "I was wondering if you could|move|the meeting."),
            ("{t}I was wondering if you could{/t} reduce the scope.", "範囲を縮めて{t}いただけないでしょうか{/t}。", "I was wondering if you could|reduce|the scope."),
        ),
        p2=rows(
            ("{t}What I can do is{/t} send you the first half.", "{t}私にできるのは{/t}、前半を送ることです。", "What I can do is|send you|the first half."),
            ("{t}What I can do is{/t} review it today.", "{t}私にできるのは{/t}、今日確認することです。", "What I can do is|review it|today."),
            ("{t}What I can do is{/t} join after lunch.", "{t}私にできるのは{/t}、昼食後に参加することです。", "What I can do is|join|after lunch."),
            ("{t}What I can do is{/t} send a shorter version.", "{t}私にできるのは{/t}、短い版を送ることです。", "What I can do is|send|a shorter version."),
        ),
        rules=(("Use the past forms in this frame for polite distance, not past time.", "このフレームの過去形は過去の時ではなく、丁寧な距離を表します。"),
               ("After What I can do is, use a plain verb for the concrete offer.", "What I can do is のあとに動詞の原形を置き、具体的な提案を続けます。")),
        prompt=("Make one request you genuinely need, or say you do not need a change right now.", "本当に必要な依頼を一つするか、今は変更が必要ないと伝えましょう。"),
    ),
    85: dict(
        slug="i-see-your-point-but", title="I see your point, but", ko="말씀은 이해하지만", ja="おっしゃることは分かりますが",
        goal=("Acknowledge a view and state your different concern clearly.", "相手の考えを認め、自分の別の懸念をはっきり伝えましょう。"),
        p1=rows(
            ("{t}I see your point, but{/t} it may cost too much.", "{t}おっしゃることは分かりますが{/t}、費用が高すぎるかもしれません。", "I see your point,|but|it may cost|too much."),
            ("{t}I see your point, but{/t} the schedule is tight.", "{t}おっしゃることは分かりますが{/t}、日程が厳しいです。", "I see your point,|but|the schedule|is tight."),
            ("{t}I see your point, but{/t} we need more data.", "{t}おっしゃることは分かりますが{/t}、もっとデータが必要です。", "I see your point,|but|we need|more data."),
            ("{t}I see your point, but{/t} the quality may suffer.", "{t}おっしゃることは分かりますが{/t}、品質が下がるかもしれません。", "I see your point,|but|the quality|may suffer."),
        ),
        p2=rows(
            ("{t}The part I'm not sure about is{/t} the timing.", "{t}よく分からない点は{/t}、タイミングです。", "The part I'm not sure about|is|the timing."),
            ("{t}The part I'm not sure about is{/t} the cost.", "{t}よく分からない点は{/t}、費用です。", "The part I'm not sure about|is|the cost."),
            ("{t}The part I'm not sure about is{/t} the final number.", "{t}よく分からない点は{/t}、最終的な数字です。", "The part I'm not sure about|is|the final number."),
            ("{t}The part I'm not sure about is{/t} the supplier.", "{t}よく分からない点は{/t}、取引先です。", "The part I'm not sure about|is|the supplier."),
        ),
        rules=(("Use but after the acknowledgement to introduce your different view.", "相手を認めたあと、but で自分の異なる考えを続けます。"),
               ("Put one specific point after The part I'm not sure about is.", "The part I'm not sure about is のあとに、具体的な懸念を一つ置きます。")),
        prompt=("Name one genuine concern, or say you agree with my view.", "本当に気になる点を一つ言うか、私の考えに賛成だと伝えましょう。"),
    ),
    86: dict(
        slug="let-me-get-back-to-you", title="Let me get back to you", ko="확인하고 다시 말씀드릴게요", ja="確認して、改めてお返事します",
        goal=("Postpone a decision without refusing and promise a follow-up time.", "断らずに判断を保留し、返事の時を約束しましょう。"),
        p1=rows(
            ("{t}Let me get back to you on{/t} that.", "それは{t}確認して改めてお返事します{/t}。", "Let me|get back to you|on that."),
            ("{t}Let me get back to you on{/t} the final price.", "最終価格は{t}確認して改めてお返事します{/t}。", "Let me|get back to you|on the final price."),
            ("{t}Let me get back to you on{/t} our availability.", "空き状況は{t}確認して改めてお返事します{/t}。", "Let me|get back to you|on our availability."),
            ("{t}Let me get back to you on{/t} the estimate.", "見積もりは{t}確認して改めてお返事します{/t}。", "Let me|get back to you|on the estimate."),
        ),
        p2=rows(
            ("{t}Can I{/t} check and confirm {t}by{/t} tomorrow?", "確認して、{t}明日までに{/t}返事してもいいですか？", "Can I|check and confirm|by tomorrow?"),
            ("{t}Can I{/t} check and confirm {t}by{/t} noon?", "確認して、{t}正午までに{/t}返事してもいいですか？", "Can I|check and confirm|by noon?"),
            ("{t}Can I{/t} review it and confirm {t}by{/t} Friday?", "確認して、{t}金曜日までに{/t}返事してもいいですか？", "Can I|review it and confirm|by Friday?"),
            ("{t}Can I{/t} ask the team and confirm {t}by{/t} three?", "チームに聞いて、{t}3時までに{/t}返事してもいいですか？", "Can I|ask the team and confirm|by three?"),
        ),
        rules=(("After let me, keep the verb plain: let me get, not let me to get.", "let me のあとには動詞の原形を置き、let me get の形にします。"),
               ("Use by for the latest time when your answer will arrive.", "返事をする最終時刻には by を使います。")),
        prompt=("Name one decision you need time for, or say you can answer now.", "確認する時間が必要な判断を一つ言うか、今答えられると伝えましょう。"),
    ),
    87: dict(
        slug="its-slightly-more-expensive", title="It's slightly more expensive", ko="조금 더 비싸요", ja="少しだけ高いです",
        goal=("Compare options with a precise small or large difference.", "選択肢の小さな差・大きな差を正確に比べましょう。"),
        p1=rows(
            ("{t}It's slightly more{/t} expensive.", "{t}少しだけ{/t}高いです。", "It's|slightly more|expensive."),
            ("{t}It's slightly more{/t} convenient.", "{t}少しだけ{/t}便利です。", "It's|slightly more|convenient."),
            ("{t}It's slightly more{/t} comfortable.", "{t}少しだけ{/t}快適です。", "It's|slightly more|comfortable."),
            ("{t}It's slightly more{/t} reliable.", "{t}少しだけ{/t}信頼できます。", "It's|slightly more|reliable."),
        ),
        p2=rows(
            ("{t}It's nowhere near as{/t} fast {t}as{/t} the train.", "速さでは電車に{t}遠く及びません{/t}。", "It's nowhere near as|fast|as the train."),
            ("{t}It's nowhere near as{/t} cheap {t}as{/t} the bus.", "安さではバスに{t}遠く及びません{/t}。", "It's nowhere near as|cheap|as the bus."),
            ("{t}It's nowhere near as{/t} quiet {t}as{/t} this room.", "静かさではこの部屋に{t}遠く及びません{/t}。", "It's nowhere near as|quiet|as this room."),
            ("{t}It's nowhere near as{/t} convenient {t}as{/t} the other option.", "便利さではもう一つの選択肢に{t}遠く及びません{/t}。", "It's nowhere near as|convenient|as the other option."),
        ),
        rules=(("Put slightly before more plus the adjective to show a small difference.", "小さな差なら、more と形容詞の前に slightly を置きます。"),
               ("Keep nowhere near as before the adjective and put the comparison after as.", "形容詞の前に nowhere near as、比較する相手の前に as を置きます。")),
        prompt=("Compare two real options, or say they are about the same.", "実際の二つを比べるか、ほぼ同じだと伝えましょう。"),
    ),
    88: dict(
        slug="hardly-anyone-came", title="Hardly anyone came", ko="거의 아무도 오지 않았어요", ja="ほとんど誰も来ませんでした",
        goal=("Describe a quantity close to none without adding another negative.", "別の否定を加えずに、ほぼゼロの量を表しましょう。"),
        p1=rows(
            ("{t}Hardly anyone{/t} came.", "{t}ほとんど誰も{/t}来ませんでした。", "Hardly anyone|came."),
            ("{t}Hardly anyone{/t} stayed for lunch.", "昼食を食べるために残った人は{t}ほとんどいませんでした{/t}。", "Hardly anyone|stayed|for lunch."),
            ("{t}Hardly anyone{/t} answered the survey.", "{t}ほとんど誰も{/t}アンケートに答えませんでした。", "Hardly anyone|answered|the survey."),
            ("{t}Hardly anyone{/t} chose the morning session.", "{t}ほとんど誰も{/t}午前の回を選びませんでした。", "Hardly anyone|chose|the morning session."),
        ),
        p2=rows(
            ("{t}There's barely any{/t} left.", "{t}ほとんど残っていません{/t}。", "There's|barely any|left."),
            ("{t}There's barely any{/t} coffee left.", "コーヒーは{t}ほとんど残っていません{/t}。", "There's|barely any|coffee left."),
            ("{t}There's barely any{/t} space left.", "空きは{t}ほとんど残っていません{/t}。", "There's|barely any|space left."),
            ("{t}There's barely any{/t} time left.", "時間は{t}ほとんど残っていません{/t}。", "There's|barely any|time left."),
        ),
        rules=(("Hardly already carries a near-negative meaning, so keep the verb positive.", "hardly 自体がほぼ否定の意味なので、動詞は肯定形のままにします。"),
               ("Use barely any before an uncountable amount or an understood noun.", "数えない量や省略された名詞の前に barely any を使います。")),
        omit_reorder=(1,),
        prompt=("Describe one real near-zero result, or say that the amount was not low.", "実際にほぼゼロだった結果を話すか、少なくなかったと伝えましょう。"),
    ),
    89: dict(
        slug="its-not-so-much-a-problem-as-a-delay", title="It's not so much a problem as a delay", ko="문제라기보다 지연이에요", ja="問題というより遅れです",
        goal=("Replace one description with a more accurate one without flatly rejecting it.", "一つの説明を完全に否定せず、より正確な表現に置き換えましょう。"),
        p1=rows(
            ("{t}It's not so much{/t} a problem {t}as{/t} a delay.", "問題{t}というより{/t}遅れです。", "It's not so much|a problem|as|a delay."),
            ("{t}It's not so much{/t} a failure {t}as{/t} a setback.", "失敗{t}というより{/t}一時的な後退です。", "It's not so much|a failure|as|a setback."),
            ("{t}It's not so much{/t} a complaint {t}as{/t} a suggestion.", "苦情{t}というより{/t}提案です。", "It's not so much|a complaint|as|a suggestion."),
            ("{t}It's not so much{/t} a cost issue {t}as{/t} a timing issue.", "費用の問題{t}というより{/t}タイミングの問題です。", "It's not so much|a cost issue|as|a timing issue."),
        ),
        p2=rows(
            ("{t}I'd call it{/t} a setback {t}rather than{/t} a failure.", "失敗{t}というより{/t}一時的な後退{t}と呼びます{/t}。", "I'd call it|a setback|rather than|a failure."),
            ("{t}I'd call it{/t} a delay {t}rather than{/t} a problem.", "問題{t}というより{/t}遅れ{t}と呼びます{/t}。", "I'd call it|a delay|rather than|a problem."),
            ("{t}I'd call it{/t} feedback {t}rather than{/t} criticism.", "批判{t}というより{/t}フィードバック{t}と呼びます{/t}。", "I'd call it|feedback|rather than|criticism."),
            ("{t}I'd call it{/t} a revision {t}rather than{/t} a restart.", "やり直し{t}というより{/t}修正{t}と呼びます{/t}。", "I'd call it|a revision|rather than|a restart."),
        ),
        rules=(("Keep the two descriptions in the same grammatical form on both sides of the frame.", "not so much ... as の両側は同じ文法の形にそろえます。"),
               ("After I'd call it, name the better description before rather than.", "I'd call it のあと、より適切な説明を rather than の前に置きます。")),
        prompt=("Reframe one real situation, or say the first description is accurate.", "実際の状況を一つ言い換えるか、最初の説明が正確だと伝えましょう。"),
    ),
    90: dict(
        slug="the-vast-majority-of-people", title="The vast majority of people", ko="대다수의 사람들", ja="大多数の人々",
        goal=("Describe how much of a group something applies to.", "あることが集団のどのくらいに当てはまるか説明しましょう。"),
        p1=rows(
            ("{t}The vast majority of{/t} people prefer it.", "人々の{t}大多数が{/t}それを好みます。", "The vast majority of|people|prefer|it."),
            ("{t}The vast majority of{/t} customers chose online support.", "顧客の{t}大多数が{/t}オンラインサポートを選びました。", "The vast majority of|customers|chose|online support."),
            ("{t}The vast majority of{/t} staff approved the plan.", "スタッフの{t}大多数が{/t}その案を承認しました。", "The vast majority of|staff|approved|the plan."),
            ("{t}The vast majority of{/t} participants approved the plan.", "参加者の{t}大多数が{/t}その案に賛成しました。", "The vast majority of|participants|approved|the plan."),
        ),
        p2=rows(
            ("{t}Only a handful{/t} said no.", "反対したのは{t}ほんの一握り{/t}でした。", "Only a handful|said|no."),
            ("{t}Only a handful{/t} chose the old plan.", "以前の案を選んだのは{t}ほんの一握り{/t}でした。", "Only a handful|chose|the old plan."),
            ("{t}Only a handful{/t} asked for changes.", "変更を求めたのは{t}ほんの一握り{/t}でした。", "Only a handful|asked for|changes."),
            ("{t}Only a handful{/t} missed the deadline.", "期限に遅れたのは{t}ほんの一握り{/t}でした。", "Only a handful|missed|the deadline."),
        ),
        rules=(("After the majority of, use a plural group noun and normally a plural verb.", "the majority of のあとに複数の集団名詞を置き、通常は複数扱いの動詞を使います。"),
               ("A handful can stand alone when the group is already clear.", "どの集団か明らかなとき、a handful は名詞なしで使えます。")),
        prompt=("Describe a real group result, or say you do not have group data.", "実際の集団の結果を話すか、集団のデータがないと伝えましょう。"),
    ),
    91: dict(
        slug="theres-barely-enough-to-go-around", title="There's barely enough to go around", ko="겨우 모두에게 돌아갈 만큼 있어요", ja="全員に行き渡るぎりぎりの量です",
        goal=("Say that an amount should be sufficient, but only just.", "量が足りそうでも、ぎりぎりだと伝えましょう。"),
        p1=rows(
            ("{t}There's barely enough to{/t} go around.", "全員に行き渡るには{t}ぎりぎりの量です{/t}。", "There's barely enough to|go around."),
            ("{t}There's barely enough to{/t} feed everyone.", "全員に食べてもらうには{t}ぎりぎりの量です{/t}。", "There's barely enough to|feed|everyone."),
            ("{t}There's barely enough to{/t} print twenty copies.", "20部印刷するには{t}ぎりぎりの量です{/t}。", "There's barely enough to|print|twenty copies."),
            ("{t}There's barely enough to{/t} finish the order.", "注文を終えるには{t}ぎりぎりの量です{/t}。", "There's barely enough to|finish|the order."),
        ),
        p2=rows(
            ("That {t}should just about{/t} cover it.", "それで{t}ぎりぎり足りるはずです{/t}。", "That|should just about cover|it."),
            ("The budget {t}should just about{/t} cover it.", "予算で{t}ぎりぎり足りるはずです{/t}。", "The budget|should just about cover|it."),
            ("Ten chairs {t}should just about{/t} cover it.", "いす10脚で{t}ぎりぎり足りるはずです{/t}。", "Ten chairs|should just about cover|it."),
            ("These supplies {t}should just about{/t} cover it.", "この備品で{t}ぎりぎり足りるはずです{/t}。", "These supplies|should just about cover|it."),
        ),
        rules=(("After barely enough to, use a plain verb for what the amount must achieve.", "barely enough to のあとに動詞の原形を置き、その量で何をするか示します。"),
               ("Put just about between should and the plain verb to show a very small margin.", "余裕がほとんどないことを表すため、should と動詞の原形の間に just about を置きます。")),
        omit_reorder=(1,),
        prompt=("Name one real resource and need, then say whether the amount is just enough or not enough.", "実際に必要なものと用途を一つ挙げ、その量がぎりぎり足りるか、足りないかを伝えましょう。"),
    ),
}


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


def choice_rows(items):
    return tuple(items)


SPECS = {
    81: semantic_spec(
        (("Use this to name the duty or activity that belongs to your role.", "自分の役割として担当する仕事や活動を伝えるときに使います。"), ("Use this to name the person or team you collaborate with most.", "最もよく協力して働く人やチームを伝えるときに使います。")),
        (("Name one duty that is genuinely yours, or say you do not have one.", "実際の担当を一つ言うか、担当がないと伝えましょう。"), ("Name one person or team you genuinely work with, or say you work alone.", "実際に一緒に働く相手を一つ言うか、一人で働くと伝えましょう。")),
        (choice_rows((("カスタマーサポートを{t}担当しています{/t}。", "I'm responsible ", "for", "with", " customer support."), ("研修を{t}担当しています{/t}。", "I'm responsible ", "for", "to", " training."), ("採用を{t}担当しています{/t}。", "I'm responsible ", "for", "with", " recruitment."), ("顧客レポートを{t}担当しています{/t}。", "I'm responsible ", "for", "to", " client reports."))), choice_rows((("営業チームと{t}一緒に働いています{/t}。", "I mainly work ", "with", "to", " the sales team."), ("財務チームと{t}一緒に働いています{/t}。", "I mainly work ", "with", "to", " the finance team."), ("顧客と{t}一緒に仕事をしています{/t}。", "I mainly work ", "with", "to", " our clients."), ("新しいスタッフと{t}一緒に働いています{/t}。", "I mainly work ", "with", "to", " new staff.")))),
        (("Keep the preposition with the role", "役割と前置詞をセットで", "be + <b>responsible for</b> + 担当", "Duty or activity", "担当する仕事・活動", ("I'm <b>responsible for customer support</b>.", "I'm <b>responsible for training</b>.")), ("Name the collaborator", "協力相手を示す", "mainly + <b>work with</b> + 人・チーム", "Person or team involved", "関わる人・チーム", ("I mainly <b>work with the sales team</b>.", "I mainly <b>work with our clients</b>."))),
        ("Work with or work for?", "work with と work for", "Use “work with” for collaborators, while “work for” names the employer or client who receives your work.", "協力する相手には「work with」、雇用主や仕事を提供する相手には「work for」を使います。", ("Collaborator", "一緒に働く相手", "I work with the sales team.", "営業チームと一緒に働いています。"), ("Employer or client", "雇用主・仕事の相手", "I work for a software company.", "ソフトウェア会社に勤めています。")),
    ),
    83: semantic_spec(
        (("Use this to check that your summary matches the other person's point.", "自分の要約が相手の要点と合っているか確認するときに使います。"), ("Use this to ask exactly what one word or idea means.", "一つの言葉や考えが具体的に何を意味するか聞くときに使います。")),
        (("Restate one real point from this conversation, or say there is nothing to restate yet.", "この会話の要点を一つ言い直すか、まだ言い直す内容がないと伝えましょう。"), ("Ask about one genuinely unclear word, or say everything is clear.", "本当に曖昧な言葉を一つ確認するか、すべて明確だと伝えましょう。")),
        (choice_rows((("{t}つまり、言いたいことは{/t}、もっと時間が必要だということですね。", "So what ", "you're saying", "you saying", " is we need more time."), ("{t}つまり、言いたいことは{/t}、日程が変わるということですね。", "So what ", "you're saying", "you saying", " is the date may change."), ("{t}つまり、言いたいことは{/t}、テストが先だということですね。", "So what ", "you're saying", "you saying", " is testing comes first."), ("{t}つまり、言いたいことは{/t}、これが最終版だということですね。", "So what ", "you're saying", "you saying", " is this is final."))), choice_rows((("「ready」とは{t}どういう意味ですか{/t}？", "What do you mean ", "by", "with", " 'ready'?"), ("「final」とは{t}どういう意味ですか{/t}？", "What do you mean ", "by", "with", " 'final'?"), ("「urgent」とは{t}どういう意味ですか{/t}？", "What do you mean ", "by", "with", " 'urgent'?"), ("「approved」とは{t}どういう意味ですか{/t}？", "What do you mean ", "by", "with", " 'approved'?")))),
        (("Turn the point into the complement", "要点を補語にする", "So + what you're saying + <b>is</b> + 要点", "Restatement check", "要点の確認", ("So what you're saying <b>is we need more time</b>.", "So what you're saying <b>is the date may change</b>.")), ("Ask about one expression", "一つの表現を確認", "What do you + <b>mean by</b> + 言葉?", "Clarification target", "確認する言葉", ("What do you <b>mean by 'ready'</b>?", "What do you <b>mean by 'final'</b>?"))),
        ("Full restatement or short check?", "言い直し・短い確認", "Use the full frame when accuracy matters. In a quick conversation, “So, Monday?” can check one detail with rising intonation.", "正確さが重要なら完全なフレームを使います。短い会話では「So, Monday?」のように語尾を上げて一つの情報を確認できます。", ("Accuracy matters", "正確さが重要", "So what you're saying is we need more time.", "つまり、もっと時間が必要ということですね。"), ("One quick detail", "一つだけ素早く確認", "So, Monday?", "つまり、月曜日ですか？")),
    ),
    84: semantic_spec(
        (("Use this to make a difficult request with polite distance.", "難しい依頼を、丁寧な距離を保ってするときに使います。"), ("Use this to offer one concrete, limited thing you can provide.", "自分ができる具体的で範囲の限られた提案をするときに使います。")),
        (("Make one real diplomatic request, or state that you need no change.", "丁寧な依頼を一つするか、変更は必要ないと伝えましょう。"), ("Offer one realistic bounded alternative, or say you cannot offer one yet.", "現実的な代案を一つ出すか、まだ出せないと伝えましょう。")),
        (choice_rows((("期限を延ばして{t}いただけないでしょうか{/t}。", "I was wondering if you ", "could", "can", " extend the deadline."), ("下書きを確認して{t}いただけないでしょうか{/t}。", "I was wondering if you ", "could", "can", " review the draft."), ("会議を変更して{t}いただけないでしょうか{/t}。", "I was wondering if you ", "could", "can", " move the meeting."), ("範囲を縮めて{t}いただけないでしょうか{/t}。", "I was wondering if you ", "could", "can", " reduce the scope."))), choice_rows((("{t}私にできるのは{/t}前半を送ることです。", "What I can do ", "is", "are", " send you the first half."), ("{t}私にできるのは{/t}今日確認することです。", "What I can do ", "is", "are", " review it today."), ("{t}私にできるのは{/t}昼食後に参加することです。", "What I can do ", "is", "are", " join after lunch."), ("{t}私にできるのは{/t}短い版を送ることです。", "What I can do ", "is", "are", " send a shorter version.")))),
        (("Distance the request", "依頼に距離を置く", "I <b>was wondering if you could</b> + 動詞", "Polite request now", "今する丁寧な依頼", ("I <b>was wondering if you could extend</b> the deadline.", "I <b>was wondering if you could review</b> it.")), ("Offer what is possible", "可能なことを提案", "What I can do + <b>is</b> + 動詞", "Concrete bounded offer", "具体的で限定した提案", ("What I can do <b>is send</b> the first half.", "What I can do <b>is join</b> after lunch."))),
        ("Could you or would you be able to?", "could you と would you be able to", "Both are polite. “Would you be able to” puts extra focus on practical availability.", "どちらも丁寧です。「Would you be able to」は、実際に対応可能かにより焦点を当てます。", ("Polite request", "丁寧な依頼", "Could you extend the deadline?", "期限を延ばしていただけますか？"), ("Checking availability", "対応可能か確認", "Would you be able to review it today?", "今日確認していただくことは可能ですか？")),
    ),
    85: semantic_spec(
        (("Use this to acknowledge the other view before giving your different one.", "相手の考えを認めてから、自分の異なる考えを伝えるときに使います。"), ("Use this to narrow your disagreement to one specific concern.", "意見の違いを一つの具体的な懸念に絞るときに使います。")),
        (("Acknowledge one real point and add your concern, or say you agree.", "実際の要点を認めて懸念を加えるか、賛成だと伝えましょう。"), ("Name one specific uncertain point, or say none remains.", "よく分からない点を一つ言うか、もうないと伝えましょう。")),
        (choice_rows((("考えは分かります{t}が{/t}、費用が高すぎるかもしれません。", "I see your point, ", "but", "so", " it may cost too much."), ("考えは分かります{t}が{/t}、日程が厳しいです。", "I see your point, ", "but", "so", " the schedule is tight."), ("考えは分かります{t}が{/t}、もっとデータが必要です。", "I see your point, ", "but", "so", " we need more data."), ("考えは分かります{t}が{/t}、品質が下がるかもしれません。", "I see your point, ", "but", "so", " the quality may suffer."))), choice_rows((("よく分からない点は{t}タイミングです{/t}。", "The part I'm not sure ", "about", "with", " is the timing."), ("よく分からない点は{t}費用です{/t}。", "The part I'm not sure ", "about", "with", " is the cost."), ("よく分からない点は{t}最終的な数字です{/t}。", "The part I'm not sure ", "about", "with", " is the final number."), ("よく分からない点は{t}取引先です{/t}。", "The part I'm not sure ", "about", "with", " is the supplier.")))),
        (("Acknowledge, then differ", "認めてから異なる考えへ", "I see your point, + <b>but</b> + 異なる考え", "Clear and polite", "明確で丁寧", ("I see your point, <b>but it may cost too much</b>.", "I see your point, <b>but we need more data</b>.")), ("Localize the uncertainty", "不確かな点を絞る", "The part + I'm not sure about + <b>is</b> + 一点", "One concern only", "懸念を一つに", ("The part I'm not sure about <b>is the timing</b>.", "The part I'm not sure about <b>is the cost</b>."))),
        ("I see your point or I see what you mean?", "point と what you mean", "Use “I see what you mean” for conversational understanding, while “I see your point” more clearly acknowledges an argument before disagreement.", "会話的な理解には「I see what you mean」、反対意見の前に相手の主張を明確に認めるなら「I see your point」を使います。", ("Conversational understanding", "会話的な理解", "I see what you mean.", "言いたいことは分かります。"), ("Before a counterpoint", "反対意見の前", "I see your point, but the timing worries me.", "おっしゃることは分かりますが、時期が気になります。")),
    ),
    86: semantic_spec(
        (("Use this to defer one answer while clearly promising to return to it.", "一つの返事を保留しつつ、必ず返すと明確に伝えるときに使います。"), ("Use this to ask for a specific latest time to check and reply.", "確認して返事をする具体的な最終時刻を求めるときに使います。")),
        (("Name one decision you need to check, or say you can answer now.", "確認が必要な判断を一つ言うか、今答えられると伝えましょう。"), ("Promise a real reply time, or say you cannot promise one yet.", "実際の返事の時を約束するか、まだ約束できないと伝えましょう。")),
        (choice_rows((("それは{t}確認して改めて返事します{/t}。", "Let me ", "get back to", "get back at", " you on that."), ("最終価格は{t}確認して改めて返事します{/t}。", "Let me ", "get back to", "get back at", " you on the final price."), ("空き状況は{t}確認して改めて返事します{/t}。", "Let me ", "get back to", "get back at", " you on our availability."), ("見積もりは{t}確認して改めて返事します{/t}。", "Let me ", "get back to", "get back at", " you on the estimate."))), choice_rows((("{t}明日までに{/t}確認して返事してもいいですか？", "Can I check and confirm ", "by", "until", " tomorrow?"), ("{t}正午までに{/t}確認して返事してもいいですか？", "Can I check and confirm ", "by", "until", " noon?"), ("{t}金曜日までに{/t}確認して返事してもいいですか？", "Can I review it and confirm ", "by", "until", " Friday?"), ("{t}3時までに{/t}確認して返事してもいいですか？", "Can I ask the team and confirm ", "by", "until", " three?")))),
        (("Promise to return to the topic", "話題に戻ると約束", "Let me + <b>get back to you on</b> + 話題", "Not a refusal", "拒否ではない", ("Let me <b>get back to you on that</b>.", "Let me <b>get back to you on the price</b>.")), ("Set the latest reply time", "返事の最終時刻", "Can I + 確認 + <b>by</b> + 時刻?", "Deadline for reply", "返事の期限", ("Can I confirm <b>by tomorrow</b>?", "Can I confirm <b>by noon</b>?"))),
        ("By tomorrow or tomorrow?", "by tomorrow と tomorrow", "Use “by tomorrow” for no later than tomorrow, while “tomorrow” names the day without emphasizing a deadline.", "遅くとも明日までなら「by tomorrow」、期限を強調せず日を示すなら「tomorrow」を使います。", ("Latest time", "最終期限", "I'll confirm by tomorrow.", "明日までに確認します。"), ("Day of the action", "行動する日", "I'll confirm tomorrow.", "明日確認します。")),
    ),
    87: semantic_spec(
        (("Use this to mark a small, precise difference on a comparative scale.", "比較の尺度で、小さく正確な差を示すときに使います。"), ("Use this to say that one option is far below another on one quality.", "一つの性質で、一方が他方よりはるかに劣ると伝えるときに使います。")),
        (("Compare two real options by one small difference, or say they are equal.", "二つの実際の選択肢を小さな差で比べるか、同じだと伝えましょう。"), ("Name one large difference, or say there is no large difference.", "大きな差を一つ言うか、大きな差はないと伝えましょう。")),
        (choice_rows((("{t}少しだけ{/t}高いです。", "It's ", "slightly more", "much more", " expensive."), ("{t}少しだけ{/t}便利です。", "It's ", "slightly more", "much more", " convenient."), ("{t}少しだけ{/t}快適です。", "It's ", "slightly more", "much more", " comfortable."), ("{t}少しだけ{/t}信頼できます。", "It's ", "slightly more", "much more", " reliable."))), choice_rows((("速さでは電車に{t}遠く及びません{/t}。", "It's ", "nowhere near as", "almost as", " fast as the train."), ("安さではバスに{t}遠く及びません{/t}。", "It's ", "nowhere near as", "almost as", " cheap as the bus."), ("静かさではこの部屋に{t}遠く及びません{/t}。", "It's ", "nowhere near as", "almost as", " quiet as this room."), ("便利さではもう一つの選択肢に{t}遠く及びません{/t}。", "It's ", "nowhere near as", "almost as", " convenient as the other option.")))),
        (("Small movement on the scale", "尺度上の小さな差", "slightly + <b>more</b> + 形容詞", "Small difference", "小さな差", ("It's <b>slightly more expensive</b>.", "It's <b>slightly more reliable</b>.")), ("Far below the comparison", "比較対象よりはるかに下", "nowhere near + <b>as</b> + 形容詞 + <b>as</b>", "Large shortfall", "大きく劣る", ("It's <b>nowhere near as fast as</b> the train.", "It's <b>nowhere near as cheap as</b> the bus."))),
        ("Slightly or a little?", "slightly と a little", "Both mark a small difference. “Slightly” is common in precise or professional comparisons; “a little” is more conversational.", "どちらも小さな差です。「slightly」は正確・仕事上の比較でよく使い、「a little」はより会話的です。", ("Precise or professional", "正確・仕事上", "It's slightly more expensive.", "少しだけ高いです。"), ("Conversational", "会話的", "It's a little more expensive.", "ちょっと高いです。")),
    ),
    88: semantic_spec(
        (("Use this for a number of people that is close to zero.", "人数がほぼゼロのときに使います。"), ("Use this for an uncountable amount that is close to zero.", "数えない量がほぼゼロのときに使います。")),
        (("Give one true near-zero people result, or say it was not low.", "人がほぼゼロだった本当の結果を言うか、少なくなかったと伝えましょう。"), ("Give one true near-zero amount, or say plenty remains.", "ほぼゼロの量を一つ言うか、十分残っていると伝えましょう。")),
        (choice_rows((("{t}ほとんど誰も{/t}来ませんでした。", "Hardly ", "anyone", "someone", " came."), ("{t}ほとんど誰も{/t}残りませんでした。", "Hardly ", "anyone", "someone", " stayed."), ("{t}ほとんど誰も{/t}答えませんでした。", "Hardly ", "anyone", "someone", " answered."), ("{t}ほとんど誰も{/t}選びませんでした。", "Hardly ", "anyone", "someone", " chose it."))), choice_rows((("コーヒーは{t}ほとんど{/t}残っていません。", "There's barely ", "any", "some", " coffee left."), ("空きは{t}ほとんど{/t}ありません。", "There's barely ", "any", "some", " space left."), ("時間は{t}ほとんど{/t}ありません。", "There's barely ", "any", "some", " time left."), ("水は{t}ほとんど{/t}残っていません。", "There's barely ", "any", "some", " water left.")))),
        (("Near zero without not", "not なしでほぼゼロ", "<b>Hardly anyone</b> + 肯定形の動詞", "People", "人", ("<b>Hardly anyone came</b>.", "<b>Hardly anyone answered</b>.")), ("Near-zero amount", "ほぼゼロの量", "There's + <b>barely any</b> + 数えない名詞", "Amount", "量", ("There's <b>barely any coffee left</b>.", "There's <b>barely any time left</b>."))),
        ("Hardly any or almost no?", "hardly any と almost no", "Both mean close to none. “Almost no” is more transparent; “hardly any” is compact and common in conversation.", "どちらもほぼゼロです。「almost no」は意味が分かりやすく、「hardly any」は短く会話でよく使われます。", ("Transparent", "分かりやすい", "Almost no coffee is left.", "コーヒーはほとんど残っていません。"), ("Compact conversation", "短い会話", "There's hardly any coffee left.", "コーヒーはほとんど残っていません。")),
    ),
    89: semantic_spec(
        (("Use this to replace one description with a more accurate parallel description.", "一つの説明を、同じ形のより正確な説明に置き換えるときに使います。"), ("Use this to personally label something as B instead of A.", "自分の判断として、AではなくBと呼ぶときに使います。")),
        (("Recast one real description, or say the first label is accurate.", "実際の説明を言い換えるか、最初の呼び方が正確だと伝えましょう。"), ("Give your own better label, or say you would keep the original.", "自分のよりよい呼び方を言うか、元の呼び方を使うと伝えましょう。")),
        (choice_rows((("問題{t}というより{/t}遅れです。", "It's not so much a problem ", "as", "than", " a delay."), ("失敗{t}というより{/t}後退です。", "It's not so much a failure ", "as", "than", " a setback."), ("苦情{t}というより{/t}提案です。", "It's not so much a complaint ", "as", "than", " a suggestion."), ("費用{t}というより{/t}時期の問題です。", "It's not so much a cost issue ", "as", "than", " a timing issue."))), choice_rows((("失敗{t}というより{/t}後退と呼びます。", "I'd call it a setback ", "rather than", "more than", " a failure."), ("問題{t}というより{/t}遅れと呼びます。", "I'd call it a delay ", "rather than", "more than", " a problem."), ("批判{t}というより{/t}フィードバックと呼びます。", "I'd call it feedback ", "rather than", "more than", " criticism."), ("やり直し{t}というより{/t}修正と呼びます。", "I'd call it a revision ", "rather than", "more than", " a restart.")))),
        (("Keep A and B parallel", "A と B の形をそろえる", "not so much + A + <b>as</b> + B", "B is more accurate", "B のほうが正確", ("not so much <b>a problem as a delay</b>", "not so much <b>a failure as a setback</b>")), ("Give your label first", "自分の呼び方を先に", "I'd call it + B + <b>rather than</b> + A", "Personal classification", "自分の分類", ("I'd call it <b>a setback rather than a failure</b>.", "I'd call it <b>feedback rather than criticism</b>."))),
        ("I'd call it or I'd describe it as?", "call it と describe it as", "Use “I'd call it” for a concise label, while “I'd describe it as” allows a longer or more qualified description.", "短い呼び方なら「I'd call it」、長い説明や条件つきの説明なら「I'd describe it as」を使います。", ("Concise label", "短い呼び方", "I'd call it a setback.", "一時的な後退と呼びます。"), ("Longer description", "長い説明", "I'd describe it as a temporary delay.", "一時的な遅れと説明します。")),
    ),
    90: semantic_spec(
        (("Use this for a very large proportion of a clearly named group.", "明確な集団の非常に大きな割合を表すときに使います。"), ("Use this for a very small number when the group is already clear.", "どの集団か明らかなとき、非常に少ない人数を表します。")),
        (("Report one genuine large-majority result, or say you have no data.", "本当の大多数の結果を伝えるか、データがないと伝えましょう。"), ("Name the small minority, or say there was no minority result.", "少数側を言うか、少数の結果がないと伝えましょう。")),
        (choice_rows((("{t}大多数の人々が{/t}それを好みます。", "The vast majority of ", "people", "person", " prefer it."), ("{t}大多数の顧客が{/t}選びました。", "The vast majority of ", "customers", "customer", " chose it."), ("{t}大多数のスタッフが{/t}承認しました。", "The vast majority of ", "staff", "staff member", " approved it."), ("{t}大多数の参加者が{/t}賛成しました。", "The vast majority of ", "participants", "participant", " approved the plan."))), choice_rows((("反対したのは{t}ほんの一握り{/t}でした。", "Only a handful ", "said", "says", " no."), ("選んだのは{t}ほんの一握り{/t}でした。", "Only a handful ", "chose", "chooses", " the old plan."), ("求めたのは{t}ほんの一握り{/t}でした。", "Only a handful ", "asked", "asks", " for changes."), ("遅れたのは{t}ほんの一握り{/t}でした。", "Only a handful ", "missed", "misses", " the deadline.")))),
        (("Name the plural group", "複数の集団を示す", "The vast majority of + <b>複数名詞</b> + 複数動詞", "Large proportion", "大きな割合", ("The vast majority of <b>people prefer</b> it.", "The vast majority of <b>customers chose</b> it.")), ("Small number already understood", "集団が分かる少数", "Only + <b>a handful</b> + 複数扱いの動詞", "Small minority", "少数", ("Only <b>a handful said no</b>.", "Only <b>a handful asked</b> for changes."))),
        ("The vast majority or most?", "vast majority と most", "“Most” is shorter and neutral. “The vast majority” stresses that the proportion is overwhelmingly large.", "「Most」は短く中立的です。「The vast majority」は圧倒的に多いことを強調します。", ("Neutral majority", "中立的な多数", "Most people prefer it.", "多くの人がそれを好みます。"), ("Overwhelming majority", "圧倒的多数", "The vast majority of people prefer it.", "大多数の人がそれを好みます。")),
    ),
    91: semantic_spec(
        (("Use this when an amount is almost insufficient for a stated purpose.", "ある目的に対して、量が足りない寸前のときに使います。"), ("Use this when you expect an amount to cover the need with almost no margin.", "余裕はほぼないものの、必要量を満たす見込みのときに使います。")),
        (("Judge one real amount, or say there is not enough.", "実際の量を判断するか、足りないと伝えましょう。"), ("Say what should just cover a need, or say it will not cover it.", "ぎりぎり足りそうなものを言うか、足りないと伝えましょう。")),
        (choice_rows((("全員に行き渡るには{t}ぎりぎりです{/t}。", "There's ", "barely enough", "more than enough", " to go around."), ("全員に食べてもらうには{t}ぎりぎりです{/t}。", "There's ", "barely enough", "more than enough", " to feed everyone."), ("20部印刷するには{t}ぎりぎりです{/t}。", "There's ", "barely enough", "more than enough", " to print twenty copies."), ("注文を終えるには{t}ぎりぎりです{/t}。", "There's ", "barely enough", "more than enough", " to finish the order."))), choice_rows((("それで{t}ぎりぎり足りるはずです{/t}。", "That should ", "just about", "not quite", " cover it."), ("予算で{t}ぎりぎり足りるはずです{/t}。", "The budget should ", "just about", "not quite", " cover it."), ("いす10脚で{t}ぎりぎり足りるはずです{/t}。", "Ten chairs should ", "just about", "not quite", " cover it."), ("この備品で{t}ぎりぎり足りるはずです{/t}。", "These supplies should ", "just about", "not quite", " cover it.")))),
        (("State the purpose of the amount", "量の目的を示す", "There's + barely enough + <b>to + 動詞</b>", "Almost insufficient", "不足寸前", ("There's barely enough <b>to go around</b>.", "There's barely enough <b>to feed everyone</b>.")), ("Predict a tiny margin", "小さな余裕を予測", "主語 + should + <b>just about</b> + 動詞", "Expected to be sufficient", "足りる見込み", ("That should <b>just about cover it</b>.", "Ten chairs should <b>just about cover it</b>."))),
        ("Just about or easily?", "just about と easily", "Use “just about” for a tiny margin, while “easily” says there is comfortable extra capacity.", "余裕がほぼないなら「just about」、十分な余裕があるなら「easily」を使います。", ("Tiny margin", "余裕がほぼない", "That should just about cover it.", "それでぎりぎり足りるはずです。"), ("Comfortable margin", "十分な余裕", "That should easily cover it.", "それで十分余裕をもって足ります。")),
    ),
}


# Vocabulary declarations are editorial source. Recycled entries cite only an
# earlier visible deck whose `podo:vocabulary:new` actually owns the item.
VOCAB = {
    81: dict(new="customer support|カスタマーサポート; sales team|営業チーム; finance team|財務チーム; staff training|スタッフ研修; recruitment|採用; client reports|顧客レポート", recycled="manager|上司|CORE-54; client|顧客|CORE-54", assumed="work|働く; team|チーム; staff|スタッフ; report|レポート; role|役割; day|日", receptive="day to day|日々の業務では; I report to|〜に直属しています; duty|担当業務; collaborate|協力する"),
    83: dict(new="final version|最終版; urgent|緊急の", recycled="meeting|会議|CORE-30; more time|もっと時間|CORE-66", assumed="ready|準備できた; final|最終の; time|時間; date|日程; testing|テスト; approved|承認された", receptive="term|用語; just to be clear|念のため確認すると; correct me if I'm wrong|間違っていたら訂正してください; summary|要約; timeline|予定表; That is exactly right.|そのとおりです。"),
    84: dict(new="extend|延ばす; first half|前半; scope|範囲; shorter version|短い版", recycled="deadline|期限|CORE-82; draft|下書き|CORE-82; repair|修理する|CORE-76", assumed="review|確認する; reduce|縮める; meeting|会議; today|今日; after lunch|昼食後", receptive="I appreciate it|ありがとうございます; Does that work?|それで大丈夫ですか？; revised date|変更後の日付; practical availability|対応可能性"),
    85: dict(new="point|要点; timing|タイミング; quality|品質; data|データ", recycled="expensive|高い|CORE-19; schedule|予定|CORE-67; supplier|取引先|CORE-82; issue|問題|CORE-82", assumed="cost|費用; final number|最終的な数字; plan|案", receptive="fair enough|なるほど、それなら分かります; where I'm coming from|私の考えの背景; concern|懸念; trade-off|一長一短; Let's compare both options.|両方の案を比べましょう。"),
    86: dict(new="final price|最終価格; availability|空き状況", recycled="noon|正午|CORE-38; manager|上司|CORE-54; deadline|期限|CORE-82", assumed="that|そのこと; three|3時; tomorrow|明日; Friday|金曜日; team|チーム; answer|返事; estimate|見積もり", receptive="off the top of my head|今すぐ思いつく範囲では; leave it with me|私に任せてください; check the figures|数字を確認する; No problem. Tomorrow works.|大丈夫です。明日で構いません。"),
    87: dict(new="", recycled="expensive|高い|CORE-19; convenient|便利な|CORE-45; comfortable|快適な|CORE-45; fast|速い|CORE-45; cheap|安い|CORE-44; quiet|静かな|CORE-43; reliable|信頼できる|CORE-56", assumed="train|電車; bus|バス; room|部屋; option|選択肢", receptive="marginally|わずかに; a fraction more|ほんの少しだけ多く; shuttle|送迎バス; precise comparison|正確な比較; Then the train is worth the extra cost.|それなら追加料金を払っても電車がよいですね。"),
    88: dict(new="survey|アンケート; morning session|午前の回; space|空き", recycled="coffee|コーヒー|CORE-9; water|水|CORE-9", assumed="anyone|誰か; time|時間; lunch|昼食; come|来る; answer|答える; came|来た; stayed|残った; answered|答えた; left|残っている", receptive="next to nothing|ほとんど何もない; few and far between|めったにない; attendee|参加者; near zero|ほぼゼロ; I'll order more before the afternoon session.|午後の回の前に追加で注文します。"),
    89: dict(new="setback|一時的な後退; failure|失敗; complaint|苦情; suggestion|提案; criticism|批判; feedback|フィードバック; revision|修正", recycled="issue|問題|CORE-82", assumed="problem|問題; delay|遅れ; cost|費用; timing|タイミング; restart|やり直し", receptive="if anything|どちらかといえば; strictly speaking|厳密に言えば; label|呼び方; classification|分類; I'll change the wording in the report.|レポートの表現を変えます。"),
    90: dict(new="participant|参加者; customer|顧客", recycled="prefer|より好む|CORE-42; share|共有する|CORE-70; deadline|期限|CORE-82", assumed="survey|アンケート; no|反対; people|人々; staff|スタッフ; plan|案; change|変更; approved|賛成した; said no|反対した", receptive="by and large|全体として; across the board|全面的に; proportion|割合; minority|少数; Then we can proceed with the new plan.|それなら新しい案で進められます。"),
    91: dict(new="supplies|備品; copies|部数; go around|行き渡る; feed everyone|全員に食べてもらう; print twenty copies|20部印刷する; finish the order|注文を終える", recycled="chair|椅子|CORE-61; enough|十分に|CORE-44; deadline|期限|CORE-82", assumed="it|必要量; food|食べ物; paper|紙; budget|予算; order|注文; everyone|全員; extra|追加の", receptive="portion|一人分; cutting it fine|ぎりぎりである; at a push|無理をすれば; margin|余裕; capacity|余力; I'll bring two extra portions.|追加で二人分持っていきます。"),
}

KNOWN_WORDS = {
    81: (("チーム", "team"), ("レポート", "report"), ("マネージャー", "manager")),
    83: (("ミーティング", "meeting"), ("タイム", "time"), ("テスト", "testing")),
    84: (("ミーティング", "meeting"), ("ドラフト", "draft"), ("レビュー", "review")),
    85: (("コスト", "cost"), ("プラン", "plan"), ("スケジュール", "schedule")),
    86: (("チーム", "team"), ("フライデー", "Friday"), ("マネージャー", "manager")),
    87: (("ルーム", "room"), ("バス", "bus"), ("オプション", "option")),
    88: (("コーヒー", "coffee"), ("タイム", "time"), ("ランチ", "lunch")),
    89: (("コスト", "cost"), ("タイミング", "timing"), ("リスタート", "restart")),
    90: (("スタッフ", "staff"), ("プラン", "plan"), ("チェンジ", "change")),
    91: (("フード", "food"), ("バジェット", "budget"), ("オーダー", "order")),
}

TRANSLATE_HINTS = {
    81: (("カスタマーサポート:customer support", "研修:staff training", "採用:recruitment", "顧客レポート:client reports"), ("営業チーム:sales team", "財務チーム:finance team", "顧客:client", "スタッフ:staff")),
    83: (("時間:time", "日程:date", "テスト:testing", "最終版:final version"), ("準備できた:ready", "最終の:final", "緊急の:urgent", "承認された:approved")),
    84: (("期限:deadline", "下書き:draft", "会議:meeting", "範囲:scope"), ("前半:first half", "今日:today", "昼食後:after lunch", "短い版:shorter version")),
    85: (("費用:cost", "日程:schedule", "データ:data", "品質:quality"), ("タイミング:timing", "費用:cost", "最終的な数字:final number", "取引先:supplier")),
    86: (("そのこと:that", "最終価格:final price", "空き状況:availability", "見積もり:estimate"), ("明日:tomorrow", "正午:noon", "金曜日:Friday", "3時:three")),
    87: (("高い:expensive", "便利な:convenient", "快適な:comfortable", "信頼できる:reliable"), ("電車:train", "バス:bus", "部屋:room", "選択肢:option")),
    88: (("来る:come", "昼食:lunch", "アンケート:survey", "午前の回:morning session"), ("残っている:left", "コーヒー:coffee", "空き:space", "時間:time")),
    89: (("問題:problem; 遅れ:delay", "失敗:failure; 後退:setback", "苦情:complaint; 提案:suggestion", "費用:cost; 時期:timing"), ("後退:setback; 失敗:failure", "遅れ:delay; 問題:problem", "フィードバック:feedback; 批判:criticism", "修正:revision; やり直し:restart")),
    90: (("人々:people", "顧客:customer", "スタッフ:staff", "参加者:participant"), ("反対:no", "案:plan", "変更:change", "期限:deadline")),
    91: (("行き渡る:go around", "全員に食べてもらう:feed everyone", "20部印刷する:print twenty copies", "注文を終える:finish the order"), ("それ:it", "予算:budget", "いす:chair", "備品:supplies")),
}

OPEN_MENUS = {
    81: (("サポート:customer support", "研修:staff training", "採用:recruitment"), ("営業チーム:sales team", "財務チーム:finance team", "顧客:client")),
    83: (("時間:time", "日程:date", "最終版:final version"), ("準備できた:ready", "緊急の:urgent", "承認された:approved")),
    84: (("期限:deadline", "下書き:draft", "範囲:scope"), ("前半:first half", "今日:today", "短い版:shorter version")),
    85: (("費用:cost", "日程:schedule", "品質:quality"), ("タイミング:timing", "最終的な数字:final number", "取引先:supplier")),
    86: (("最終価格:final price", "空き状況:availability", "見積もり:estimate"), ("明日:tomorrow", "正午:noon", "金曜日:Friday")),
    87: (("高い:expensive", "便利な:convenient", "信頼できる:reliable"), ("電車:train", "バス:bus", "選択肢:option")),
    88: (("アンケート:survey", "午前の回:morning session", "昼食:lunch"), ("コーヒー:coffee", "空き:space", "時間:time")),
    89: (("問題:problem", "遅れ:delay", "後退:setback"), ("失敗:failure", "フィードバック:feedback", "修正:revision")),
    90: (("人々:people", "顧客:customer", "参加者:participant"), ("案:plan", "変更:change", "期限:deadline")),
    91: (("食べ物:food", "部数:copies", "注文:order"), ("予算:budget", "いす:chair", "備品:supplies")),
}

SUPPORT_EXPRESSIONS = {
    81: (("Day to day, I handle customer questions.", "日々の業務では、顧客からの質問を担当します。"), ("I report to the support manager.", "サポート部門の上司に直属しています。")),
    83: (("Just to be clear, the date is Monday.", "念のため確認すると、日付は月曜日です。"), ("Correct me if I'm wrong, but testing comes first.", "間違っていたら訂正してください。テストが先ですね。")),
    84: (("I appreciate it.", "ありがとうございます。"), ("Does that work?", "それで大丈夫ですか？")),
    85: (("Fair enough.", "なるほど、それなら分かります。"), ("Let me explain where I'm coming from.", "私の考えの背景を説明させてください。")),
    86: (("Off the top of my head, I can't confirm it.", "今すぐ思いつく範囲では、確認できません。"), ("Leave it with me.", "私に任せてください。")),
    87: (("It's marginally cheaper.", "わずかに安いです。"), ("It costs a fraction more.", "ほんの少しだけ高くなります。")),
    88: (("There's next to nothing left.", "ほとんど何も残っていません。"), ("Good examples are few and far between.", "よい例はめったにありません。")),
    89: (("If anything, it's a delay.", "どちらかといえば、遅れです。"), ("Strictly speaking, it isn't a failure.", "厳密に言えば、失敗ではありません。")),
    90: (("By and large, people approved.", "全体として、人々は賛成しました。"), ("The result was consistent across the board.", "結果は全面的に一貫していました。")),
    91: (("We're cutting it fine.", "ぎりぎりです。"), ("We can fit one more at a push.", "無理をすれば、あと一人入れます。")),
}

SUPPORT_OWNERSHIP = {n: tuple(e.split("|")[0].casefold() for e in filter(None, VOCAB[n]["receptive"].split("; "))) for n in NUMBERS}

DIALOGUES = {
    81: dict(model=("New colleague", 0, 0, ("Could you tell me about your role?", "担当について教えてもらえますか？"), ("Who do you work with most?", "主に誰と一緒に働いていますか？"), ("Great. I'll introduce you to our sales lead.", "分かりました。営業責任者を紹介します。"), ("Thanks. That would help.", "ありがとう。助かります。")), wild=("Coordinator", 1, 1, ("What is your role at the conference?", "この会議での担当は何ですか？"), ("Which team will you work with?", "どのチームと一緒に働きますか？"), ("Perfect. The finance team is at the next desk.", "よかったです。財務チームは隣の机にいます。"), ("Thanks. I'll speak to them now.", "ありがとう。今、話してきます。"))),
    83: dict(model=("Coworker", 0, 0, ("Testing will take two more days, so the launch may move.", "テストにあと2日かかるので、公開がずれるかもしれません。"), ("Exactly. The product must be ready first.", "そのとおりです。まず製品の準備ができている必要があります。"), ("I mean fully tested and approved.", "完全にテストされ、承認された状態という意味です。"), ("Got it. That is clear now.", "分かりました。これではっきりしました。")), wild=("Vendor", 1, 1, ("We can deliver on Monday if the final checks pass.", "最終確認が通れば月曜日に納品できます。"), ("Correct. We still need the final version.", "そのとおりです。まだ最終版が必要です。"), ("I mean the version the client has signed off.", "顧客が承認した版という意味です。"), ("Thanks. Now I know what to check.", "ありがとう。確認する点が分かりました。"))),
    84: dict(model=("Client", 0, 0, ("The full report is due Friday.", "完全なレポートは金曜日が期限です。"), ("I can't move the full deadline. Is there another option?", "全体の期限は動かせません。別の案はありますか？"), ("Yes. Send that today and the rest on Friday.", "はい。前半は今日、残りは金曜日に送ってください。"), ("I appreciate it. I'll do that.", "ありがとうございます。そうします。")), wild=("Property manager", 2, 2, ("The meeting with the repair team is booked for Tuesday morning.", "修理チームとの打ち合わせは火曜日の午前に予定されています。"), ("I can't change the day. Could you join later?", "日は変えられません。遅れて参加できますか？"), ("Yes, after lunch works. I'll tell the repair team.", "はい、昼食後で大丈夫です。修理チームに伝えます。"), ("Thank you. That works for me.", "ありがとう。それなら大丈夫です。"))),
    85: dict(model=("Teammate", 0, 0, ("The premium supplier could finish faster.", "高価格の取引先なら、もっと早く終えられそうです。"), ("Apart from cost, what part are you unsure about?", "費用以外では、どの点がよく分かりませんか？"), ("Fair enough. Let's compare the cost and timing.", "なるほど。費用と時期を比べましょう。"), ("Good. Then we can decide with both facts.", "いいですね。両方の事実を見て決められます。")), wild=("Organizer", 2, 2, ("I think we should launch the event next week.", "来週イベントを始めるべきだと思います。"), ("Which part needs more evidence?", "どの点にもっと根拠が必要ですか？"), ("That makes sense. I'll collect the final numbers.", "分かりました。最終的な数字を集めます。"), ("Thanks. Then I'll review the plan again.", "ありがとう。それから案をもう一度見ます。"))),
    86: dict(model=("Manager", 1, 0, ("Can you approve the final price now?", "今、最終価格を承認できますか？"), ("Sure. When can you confirm it?", "分かりました。いつ確認できますか？"), ("Tomorrow is fine. I'll wait for your answer.", "明日で大丈夫です。返事を待ちます。"), ("Thanks. I'll check the figures today.", "ありがとう。今日、数字を確認します。")), wild=("Booking agent", 2, 1, ("Can you confirm the group booking now?", "今、団体予約を確定できますか？"), ("Of course. When should I expect your answer?", "もちろんです。いつ返事をいただけますか？"), ("Noon works. I'll hold the rooms until then.", "正午で大丈夫です。それまで部屋を押さえます。"), ("Thank you. I'll contact the group now.", "ありがとう。今、グループに連絡します。"))),
    87: dict(model=("Coworker", 0, 0, ("How does the express train compare with the bus?", "急行電車はバスと比べてどうですか？"), ("What about the bus for speed?", "速さではバスはどうですか？"), ("Then the train is worth the extra cost.", "それなら追加料金を払っても電車がよいですね。"), ("I agree. Let's take the train.", "同感です。電車にしましょう。")), wild=("Friend", 2, 3, ("How does the hotel shuttle compare with a taxi?", "ホテルの送迎バスはタクシーと比べてどうですか？"), ("And how convenient is it compared with the taxi?", "タクシーと比べて便利さはどうですか？"), ("Then let's pay a little more for the taxi.", "では、少し多く払ってタクシーにしましょう。"), ("Good idea. It will save us time.", "いい考えです。時間を節約できます。"))),
    88: dict(model=("Organizer", 0, 1, ("How was the morning session?", "午前の回はどうでしたか？"), ("That's disappointing. Is there coffee for the afternoon group?", "残念ですね。午後のグループ用のコーヒーはありますか？"), ("I'll order more before the afternoon session.", "午後の回の前に追加で注文します。"), ("Good idea. Then we won't run out.", "いいですね。それなら足りなくなりません。")), wild=("Club leader", 2, 3, ("Did many members answer the event survey?", "イベントのアンケートに多くの会員が答えましたか？"), ("Then do we still have time to ask again?", "では、もう一度聞く時間はありますか？"), ("I'll send one short reminder now.", "今、短いリマインダーを一つ送ります。"), ("Good. That may bring in a few more answers.", "いいですね。回答が少し増えるかもしれません。"))),
    89: dict(model=("Manager", 0, 0, ("The report calls this a serious problem and a project failure.", "レポートでは、これを深刻な問題であり、プロジェクトの失敗だとしています。"), ("And what label would you use instead of failure?", "では、失敗の代わりにどんな呼び方をしますか？"), ("That is more accurate. I'll change the wording.", "そのほうが正確です。表現を変えます。"), ("Thanks. It still shows that action is needed.", "ありがとう。それでも対応が必要だと伝わります。")), wild=("Neighbor", 3, 3, ("The renovation plan says we must restart because of a cost problem.", "改修計画には、費用の問題でやり直す必要があると書いてあります。"), ("Then how would you describe the restart?", "では、そのやり直しをどう説明しますか？"), ("That sounds less alarming and more precise.", "そのほうが不安をあおらず、正確ですね。"), ("Exactly. We can keep the work already done.", "そのとおりです。すでに終えた作業は残せます。"))),
    90: dict(model=("Manager", 1, 0, ("What did the customer survey show about online support?", "顧客アンケートでは、オンラインサポートについて何が分かりましたか？"), ("Did many customers reject that option?", "その選択肢に反対した顧客は多かったですか？"), ("Then we can proceed with online support.", "それならオンラインサポートで進められます。"), ("Yes. I'll share the full results today.", "はい。今日、全結果を共有します。")), wild=("Committee member", 3, 2, ("How did participants respond to the neighborhood plan?", "地域の計画に参加者はどう反応しましたか？"), ("Did many ask for changes?", "変更を求めた人は多かったですか？"), ("Then the committee has a clear result.", "それなら委員会には明確な結果があります。"), ("Yes. We can record the decision now.", "はい。今、決定を記録できます。"))),
    91: dict(model=("Organizer", 0, 0, ("Do we have enough food for everyone?", "全員分の食べ物はありますか？"), ("And is the budget enough for the extra portions?", "追加分の予算は足りますか？"), ("I'll bring two extra portions, just in case.", "念のため、追加で二人分持っていきます。"), ("Great. Then everyone will have enough.", "よかったです。それなら全員に足ります。")), wild=("Volunteer", 2, 2, ("Do we have enough paper for the workshop?", "ワークショップ用の紙は足りますか？"), ("And are ten chairs enough?", "いす10脚で足りますか？"), ("I'll bring two extra chairs from the next room.", "隣の部屋から追加でいすを2脚持ってきます。"), ("Perfect. Then we have a small margin.", "完璧です。それなら少し余裕があります。"))),
}

LIVE_SCENES = {
    81: (("text", "other", "Tutor", "What are you responsible for, and who do you mainly work with?", "何を担当し、主に誰と一緒に働いていますか？"), ("input", "me", "Me", "I'm responsible for ___. I mainly work with ___. / I don't have a work role right now.", "___を担当し、主に___と働いています。／今は仕事上の担当がありません。"), ("input", "me", "Me", "What are you responsible for, and who do you mainly work with?", "先生の担当と、一緒に働く相手も聞きましょう。"), ("input", "other", "Tutor", "Tutor's real answer:", "先生の実際の答え")),
    83: (("text", "other", "Tutor", "What point from our conversation would you like to check?", "この会話のどの要点を確認したいですか？"), ("input", "me", "Me", "So what you're saying is ___. / I don't have anything to restate yet.", "つまり、___ということですね。／まだ言い直す内容はありません。"), ("input", "me", "Me", "What do you mean by '___'?", "「___」とはどういう意味か先生に聞きましょう。"), ("input", "other", "Tutor", "Tutor's real clarification:", "先生の実際の説明")),
    84: (("text", "other", "Tutor", "Is there a deadline or plan you genuinely need changed?", "本当に変えてほしい期限や予定はありますか？"), ("input", "me", "Me", "I was wondering if you could ___. / I don't need a change right now.", "___していただけないでしょうか。／今は変更が必要ありません。"), ("input", "me", "Me", "If I need the change: What I can do is ___. Does that work? / If not: Is there anything you'd like me to change?", "変更が必要なら「私にできるのは___です。それで大丈夫ですか？」／必要なければ、先生が私に変えてほしいことがあるか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real response or request:", "先生の実際の返事、または依頼")),
    85: (("text", "other", "Tutor", "I think the more expensive option is worth choosing. What do you think?", "私は、高いほうを選ぶ価値があると思います。あなたはどう思いますか？"), ("input", "me", "Me", "I see your point, but ___. The part I'm not sure about is ___. / I agree with your view.", "おっしゃることは分かりますが、___。よく分からない点は___です。／先生の考えに賛成です。"), ("input", "me", "Me", "Where are you coming from on this?", "先生の考えの背景も聞きましょう。"), ("input", "other", "Tutor", "Tutor's real explanation:", "先生の実際の説明")),
    86: (("text", "other", "Tutor", "Is there one decision you need time to check?", "確認する時間が必要な判断はありますか？"), ("input", "me", "Me", "Let me get back to you on ___. / I can answer now: ___.", "___は確認して改めて返事します。／今答えられます：___。"), ("input", "me", "Me", "If I need time: Can I check and confirm by ___? / If I can answer now: Do you need me to confirm anything else?", "時間が必要なら、___までに確認して返事してよいか聞きましょう。／今答えられるなら、ほかに確認することがあるか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real response:", "先生の実際の返事")),
    87: (("text", "other", "Tutor", "Compare two real options for me.", "実際の二つの選択肢を比べてください。"), ("input", "me", "Me", "___ is slightly more ___. It is nowhere near as ___ as ___. / They're about the same.", "___は少しだけ___です。___は___に遠く及びません。／ほぼ同じです。"), ("input", "me", "Me", "How do those two options compare for you?", "先生にとって二つがどう違うか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real comparison:", "先生の実際の比較")),
    88: (("text", "other", "Tutor", "Was there a recent event with very low attendance?", "最近、参加者がとても少ないイベントはありましたか？"), ("input", "me", "Me", "Hardly anyone ___. / The number wasn't low.", "ほとんど誰も___しませんでした。／人数は少なくありませんでした。"), ("input", "me", "Me", "Is there barely any ___ left?", "___がほとんど残っていないか先生に聞きましょう。"), ("input", "other", "Tutor", "Tutor's real answer:", "先生の実際の答え")),
    89: (("text", "other", "Tutor", "Is there a situation you would describe more accurately?", "もっと正確に表現したい状況はありますか？"), ("input", "me", "Me", "It's not so much ___ as ___. I'd call it ___ rather than ___. / The original description is accurate.", "___というより___です。___ではなく___と呼びます。／元の説明が正確です。"), ("input", "me", "Me", "What would you call it?", "先生なら何と呼ぶか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real label:", "先生の実際の呼び方")),
    90: (("text", "other", "Tutor", "Do you know a real result for a group of people?", "実際の集団の結果を知っていますか？"), ("input", "me", "Me", "The vast majority of ___ ___. Only a handful ___. / I don't have group data.", "___の大多数が___。ほんの一握りが___。／集団のデータはありません。"), ("input", "me", "Me", "What do most people you know prefer?", "先生の知る多くの人が何を好むか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real answer:", "先生の実際の答え")),
    91: (("text", "other", "Tutor", "Think of one real resource and a specific need. Will the amount cover it?", "実際に必要なものと、具体的な用途を一つ考えてください。その量で足りますか？"), ("input", "me", "Me", "We need ___ for ___. There's barely enough to ___. That should just about cover it. / There isn't enough ___ to ___.", "___には___が必要です。___するにはぎりぎりです。それでぎりぎり足りるはずです。／___するための___が足りません。"), ("input", "me", "Me", "Do you have enough ___ to ___?", "先生にも、___するための___が足りるか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real resource and need:", "先生が実際に必要なものと用途")),
}

LIVE_HINTS = {
    81: {1: ("サポート:customer support", "研修:staff training", "営業チーム:sales team", "財務チーム:finance team")},
    83: {1: OPEN_MENUS[83][0], 2: OPEN_MENUS[83][1]},
    84: {1: ("延ばす:extend", "確認する:review", "縮める:reduce"), 2: OPEN_MENUS[84][1]},
    85: {1: ("費用:cost", "日程:schedule", "タイミング:timing", "品質:quality")},
    86: {1: OPEN_MENUS[86][0], 2: OPEN_MENUS[86][1]},
    87: {1: ("高い:expensive", "快適な:comfortable", "速い:fast", "電車:train")},
    88: {1: ("来た:came", "残った:stayed", "答えた:answered"), 2: OPEN_MENUS[88][1]},
    89: {1: ("問題:problem", "遅れ:delay", "後退:setback", "失敗:failure")},
    90: {1: ("人々:people", "スタッフ:staff", "好む:prefer", "反対した:said no")},
    91: {1: ("食べ物:food", "全員に食べてもらう:feed everyone", "紙:paper", "20部印刷する:print twenty copies"), 2: ("食べ物:food", "全員に食べてもらう:feed everyone", "紙:paper", "20部印刷する:print twenty copies")},
}

TRANSFER_SCENES = {81: "conference role handoff", 83: "vendor terminology call", 84: "apartment repair rescheduling", 85: "community event proposal review", 86: "group hotel booking", 87: "hotel shuttle versus taxi", 88: "club survey follow-up", 89: "home renovation reclassification", 90: "neighborhood proposal poll", 91: "workshop paper and chairs"}

BRIEF_PRODUCTION_MODELS = {n: (core.strip_marks(LESSONS[n]["p1"][0][0]), core.strip_marks(LESSONS[n]["p2"][0][0])) for n in NUMBERS}

THREE_CHIP_EXCEPTIONS = {
    (81, 1): "The complete role frame and its duty make only three honest units.",
    (81, 2): "The complete collaborator frame and team make only three honest units.",
    (83, 2): "The clarification frame, preposition, and quoted term make three units.",
    (84, 1): "Keep the diplomatic request frame intact before verb and object.",
    (84, 2): "Keep the cleft offer frame intact before action and complement.",
    (85, 2): "Keep the uncertainty frame intact before copula and focused concern.",
    (86, 1): "Keep the phrasal frame get back to you intact with its topic.",
    (86, 2): "Keep check and confirm together before the promised deadline.",
    (87, 1): "The subject, degree phrase, and adjective are three semantic units.",
    (87, 2): "Keep both halves of the as comparison attached to their complements.",
    (88, 1): "Hardly anyone is one quantifier subject followed by its predicate.",
    (88, 2): "Barely any is one quantifier inside the existential frame.",
    (90, 2): "Only a handful is one quantifier subject followed by its predicate.",
    (91, 1): "Keep barely enough to as the taught sufficiency frame.",
    (91, 2): "Keep should just about cover as the taught modal predicate.",
}

SPIRAL_MARKERS = {
    81: (("PREP-01", "transfer"),),
    83: (("REL-01", "transfer"), ("REPORT-01", "transfer")),
    84: (("POLITE-01", "transfer"), ("MODAL-01", "transfer")),
    86: (("PREP-01", "checkpoint"), ("POLITE-01", "transfer")),
    88: (("COUNT-01", "transfer"), ("NUM-01", "transfer")),
    89: (("ART-01", "transfer"),),
    90: (("NUM-01", "transfer"), ("COUNT-01", "contrast")),
    91: (("DUMMY-01", "transfer"), ("COUNT-01", "checkpoint")),
}

SPIRAL_CHOICES = {
    81: (("担当する{t}仕事{/t}です。", "I'm responsible ", "for", "with", " support."), ("協力する{t}チーム{/t}です。", "I work ", "with", "to", " sales."), ("直属する{t}上司{/t}です。", "I report ", "to", "for", " my manager."), ("返事を待っている{t}対象{/t}です。", "I'm waiting ", "for", "to", " approval.")),
    83: (("昨日送った{t}レポート{/t}です。", "The report ", "that", "what", " you sent says Monday."), ("電話した{t}人{/t}です。", "The person ", "who", "which", " called needs an answer."), ("彼は遅れると{t}言いました{/t}。", "He ", "said", "told", " he would be late."), ("彼は私に日程を{t}伝えました{/t}。", "He ", "told", "said", " me the date.")),
    84: (("丁寧に頼む。", "Could you ", "review", "to review", " it?"), ("丁寧に頼む。", "Would you ", "send", "to send", " it?"), ("可能な提案。", "What I can do is ", "call", "to call", " today."), ("丁寧な距離。", "I was ", "wondering", "wonder", " if you could help.")),
    86: (("最終期限は金曜日。", "I'll confirm ", "by", "until", " Friday."), ("金曜日まで続ける。", "I'll wait ", "until", "by", " Friday."), ("丁寧に時間を求める。", "Can I ", "check", "to check", " and reply tomorrow?"), ("話題について返事する。", "I'll get back to you ", "on", "at", " the price.")),
    88: (("数えない量。", "There isn't much ", "coffee", "coffees", " left."), ("複数の物。", "Hardly any ", "chairs", "chair", " were free."), ("一人もほぼいない。", "Hardly ", "anyone", "any people", " came."), ("数えない時間。", "There's barely any ", "time", "times", " left.")),
    89: (("一つの問題。", "It's ", "a", "an", " problem."), ("一つの遅れ。", "It's ", "a", "an", " delay."), ("一つの問題点。", "It's ", "an", "a", " issue."), ("一つの修正。", "It's ", "a", "an", " revision.")),
    90: (("複数の人。", "The majority of ", "people", "person", " prefer it."), ("複数の顧客。", "Most ", "customers", "customer", " agreed."), ("数えられる少数。", "A handful of ", "participants", "participation", " objected."), ("数えない少量。", "Only a little ", "time", "times", " remained.")),
    91: (("量がある。", "There ", "is", "are", " enough food."), ("必要量を指す。", "It ", "should", " there", " cover the cost."), ("数えない量。", "There is enough ", "paper", "papers", " for the class."), ("複数の物。", "There are enough ", "chairs", "chair", " for everyone.")),
}

DIALOGUE_SEMANTIC_LEDGER = {
    81: dict(model=("colleague asks role", "learner names duty", "colleague asks collaborator", "learner names team", "colleague offers introduction", "learner accepts"), wild=("coordinator asks conference role", "learner names training duty", "coordinator asks team", "learner names finance", "coordinator locates team", "learner acts")),
    83: dict(model=("coworker explains possible move", "learner restates", "coworker confirms and names ready", "learner asks term meaning", "coworker defines term", "learner confirms clarity"), wild=("vendor gives conditional date", "learner restates", "vendor confirms uncertainty", "learner asks final meaning", "vendor defines it", "learner names next check")),
    84: dict(model=("client states deadline", "learner requests extension", "client rejects full move and asks option", "learner offers half", "client accepts sequence", "learner commits"), wild=("landlord states repair time", "learner requests move", "landlord asks later option", "learner offers afternoon", "landlord accepts", "learner closes")),
    85: dict(model=("teammate proposes premium supplier", "learner acknowledges cost concern", "teammate asks focus", "learner names timing", "teammate proposes comparison", "learner agrees"), wild=("organizer proposes early launch", "learner asks for data", "organizer asks evidence focus", "learner names final number", "organizer commits to collect", "learner commits to review")),
    86: dict(model=("manager asks price approval", "learner defers price", "manager asks reply time", "learner requests tomorrow", "manager accepts", "learner commits check"), wild=("agent asks booking confirmation", "learner defers availability", "agent asks time", "learner requests noon", "agent holds rooms", "learner contacts group")),
    87: dict(model=("coworker asks train comparison", "learner names small price difference", "coworker asks bus speed", "learner names large gap", "coworker chooses train", "learner agrees"), wild=("friend asks shuttle comparison", "learner names small comfort difference", "friend asks taxi convenience gap", "learner names large gap", "friend chooses taxi", "learner gives benefit")),
    88: dict(model=("organizer asks attendance", "learner reports near-zero attendance", "organizer asks coffee", "learner reports near-zero coffee", "organizer orders more", "learner confirms resolution"), wild=("leader asks survey response", "learner reports near-zero responses", "leader asks time", "learner reports near-zero time", "leader sends reminder", "learner predicts benefit")),
    89: dict(model=("manager presents problem and failure labels", "learner recasts problem as delay", "manager asks replacement for failure", "learner labels setback", "manager updates wording", "learner preserves action need"), wild=("neighbor presents cost and restart labels", "learner recasts cost as timing", "neighbor asks restart description", "learner labels revision", "neighbor validates", "learner preserves completed work")),
    90: dict(model=("manager asks online-support survey", "learner reports customer majority", "manager asks opposition", "learner reports handful", "manager proceeds with option", "learner promises results"), wild=("committee asks participant response", "learner reports participant approval", "committee asks change requests", "learner reports handful", "committee identifies clear result", "learner records decision")),
    91: dict(model=("organizer asks food sufficiency", "learner reports tiny margin", "organizer asks budget", "learner predicts coverage", "organizer adds portions", "learner confirms sufficient outcome"), wild=("volunteer asks paper", "learner reports print margin", "volunteer asks chairs", "learner predicts coverage", "volunteer adds chairs", "learner confirms margin")),
}


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{value}\2', head, count=1,
        )
    return head


def hint_html(items):
    chips = []
    for item in items:
        chips.extend(part for part in item.split("; ") if part)
    return '<span class="hint">' + "".join(
        f'<span class="hint-chip">{core.esc(item)}</span>' for item in chips
    ) + "</span>"


def known_page(number):
    cards = "".join(
        f'<div class="br-row"><span class="br-cn">{core.esc(japanese)}</span>'
        f'<span class="br-eq">→</span><span class="br-ko">{core.esc(english)}</span></div>'
        for japanese, english in KNOWN_WORDS[number]
    )
    return core.section(
        "words-you-know", "Words you know", "知っている単語",
        '<p class="section-subtitle"><span class="ko">Say the three familiar words in English.</span>'
        '<span class="ja">知っている3つの単語を英語で言いましょう。</span></p>'
        f'<div class="bridge">{cards}</div>',
    )


def support_page(number):
    lines = "".join(
        '<div class="model-line">'
        f'<span class="korean">{core.esc(english)}</span>'
        f'<span class="translation">{core.esc(japanese)}</span></div>'
        for english, japanese in SUPPORT_EXPRESSIONS[number]
    )
    return core.section(
        "supporting-expressions", "Useful conversation support", "会話を支える表現",
        '<p class="section-subtitle"><span class="ko">Read these optional phrases, then use one only if it fits.</span>'
        '<span class="ja">補助表現を読み、合う場面だけで一つ使いましょう。</span></p>'
        f'<div class="model-list">{lines}</div>',
    )


def spiral_page(number):
    markers = SPIRAL_MARKERS[number]
    marker_text = " ".join(f"{sid}:{mode}" for sid, mode in markers)
    page = core.choose_words(
        "spiral-review", "Retrieve an earlier rule", "前のルールを思い出そう",
        "Choose the smallest form that keeps the earlier rule accurate.",
        "前のルールが正しくなる最小の形を選びましょう。",
        SPIRAL_CHOICES[number],
    )
    return page.replace(
        'data-page-id="spiral-review"',
        f'data-page-id="spiral-review" data-spiral-review="{marker_text}"', 1,
    )


def translate_page(number, part, pattern):
    blocks = []
    for index, ((english, japanese, _), hints) in enumerate(
        zip(pattern, TRANSLATE_HINTS[number][part - 1], strict=True)
    ):
        blocks.append(
            '<div class="task-block"><div class="answer-box">'
            f'<span class="answer-label">{core.esc(core.strip_marks(japanese))}</span>'
            '<span class="answer-space as-input">'
            f'<input class="space-input" type="text" data-sync-id="p{part}-translate-{index}" '
            f'data-answer="{core.esc(core.strip_marks(english))}" autocomplete="off" spellcheck="false">'
            '</span>' + hint_html((hints,)) + '</div></div>'
        )
    return core.section(
        f"p{part}-translate", "Say it in English", "英語にしよう",
        '<p class="section-subtitle"><span class="ko">Use the vocabulary menu, then say the whole sentence.</span>'
        '<span class="ja">単語メニューを使って、文をまるごと英語で言いましょう。</span></p>'
        + "".join(blocks),
    )


def write_page(number, part, pattern):
    prompt_en, prompt_ja = SPECS[number]["writes"][part - 1]
    return core.section(
        f"p{part}-write", "Make it yours", "自分の文にしよう",
        f'<p class="section-subtitle"><span class="ko">{core.esc(prompt_en)}</span>'
        f'<span class="ja">{core.esc(prompt_ja)}</span></p>'
        '<div class="task-block"><div class="answer-box tall">'
        '<span class="answer-label">Your sentence<span class="task">自分の情報で</span></span>'
        '<span class="answer-space as-input">'
        f'<textarea class="free-input" data-sync-id="p{part}-write" rows="2" spellcheck="false" maxlength="2000"></textarea>'
        '</span>' + hint_html(OPEN_MENUS[number][part - 1]) + '</div></div>',
    )


def live_page(number):
    rendered = []
    for index, (kind, side, speaker, english, japanese) in enumerate(LIVE_SCENES[number]):
        avatar = core.live_avatar(speaker)
        bubble = "bubble me" if side == "me" else "bubble"
        if kind == "text":
            rendered.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}">'
                f'<span class="korean">{core.esc(english)}</span>'
                f'<span class="translation">{core.esc(japanese)}</span></div></div>'
            )
        else:
            hints = hint_html(LIVE_HINTS[number].get(index, ())) if side == "me" else ""
            label = "Tutor's answer:" if side == "other" else english
            rendered.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}"><div class="answer-box tall">'
                f'<span class="answer-label">{core.esc(label)}<span class="task">{core.esc(japanese)}</span></span>'
                '<span class="answer-space as-input">'
                f'<textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea>'
                f'</span>{hints}</div></div></div>'
            )
    return core.section(
        "p3-freetalk", "Your real answer", "自分の答え",
        f'<p class="section-subtitle"><span class="ko">{core.esc(LESSONS[number]["prompt"][0])}</span>'
        f'<span class="ja">{core.esc(LESSONS[number]["prompt"][1])}</span></p>'
        '<div class="dialogue">' + "".join(rendered) + "</div>",
    )


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def customize_pages(number, data, pages):
    replacements = {
        "words-you-know": known_page(number),
        "p1-translate": translate_page(number, 1, data["p1"]),
        "p2-translate": translate_page(number, 2, data["p2"]),
        "p1-write": write_page(number, 1, data["p1"]),
        "p2-write": write_page(number, 2, data["p2"]),
        "p3-freetalk": live_page(number),
    }
    omitted = {f"p{part}-reorder" for part in data.get("omit_reorder", ())}
    result = []
    for page in pages:
        pid = page_id(page)
        if pid in omitted:
            continue
        if pid == "part3-intro":
            result.append(support_page(number))
            if number in SPIRAL_MARKERS:
                result.append(spiral_page(number))
        result.append(replacements.get(pid, page))
    return result


@contextlib.contextmanager
def course_data():
    previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    renderer_vocab = {
        number: (values["new"], values["assumed"], values["receptive"])
        for number, values in VOCAB.items()
    }
    core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = (
        renderer_vocab, SPECS, DIALOGUES, LIVE_SCENES,
    )
    try:
        yield
    finally:
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = previous


def build(number, data):
    if number not in NUMBERS:
        raise ValueError(f"CORE-{number} is not owned by this generator")
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    level = "B1+" if number <= 86 else "B2"
    head = new_lesson.retarget(
        head, review_id=f"CORE-{number}", lesson_id=slug, level=level,
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"],
        version="2026-08-20",
    )
    with course_data():
        head = set_vocab(head.replace('content="todo"', 'content="reviewed"'), number)
        head = core.set_proofread_status(head, "complete")
        pages = customize_pages(number, data, core.canonical_pages(number, data))
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
        ("brief models", BRIEF_PRODUCTION_MODELS),
        ("dialogue ledger", DIALOGUE_SEMANTIC_LEDGER),
    ):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover the ten owned lessons")
    if 82 in expected or not EXISTING_CORE82.is_file():
        raise SystemExit("CORE-82 preservation boundary is invalid")


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
        print(f"wrote {out.relative_to(ROOT)}")
    print("10 missing Core decks generated; CORE-82 preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
