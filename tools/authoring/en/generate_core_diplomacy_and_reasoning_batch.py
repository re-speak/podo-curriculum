#!/usr/bin/env python3
"""Generate the explicit CORE-92--102 Diplomacy and Reasoning batch."""

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
COURSE = "core-diplomacy-and-reasoning"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
NUMBERS = tuple(range(92, 103))

# Whole-sentence answers must wrap and grow rather than hide their tails at
# 360px. This is the reviewed narrow wrapper first used by CORE60--70; it is
# deliberately local so already-approved course bytes do not drift.
NARROW_GROWING_INPUT_CSS = """/* CORE92--102: keep complete learner answers visible at phone widths. */
textarea.space-input,
textarea.free-input,
textarea.phrase-input {
  box-sizing: border-box;
  field-sizing: content;
  block-size: auto;
  min-block-size: 2.75em;
  max-block-size: none;
  overflow: hidden;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  resize: none;
}
textarea.phrase-input {
  margin-block: 4px;
}
.sent-hero,
.korean {
  min-inline-size: 0;
  overflow-wrap: anywhere;
}
"""


def rows(*items):
    return items


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


def choice_rows(items):
    return tuple(items)


LESSONS = {
    92: dict(
        slug="im-not-entirely-convinced", title="I'm not entirely convinced", ko="완전히 납득되지는 않아요", ja="完全には納得していません",
        goal=("Express a doubt softly and name the evidence you need.", "疑問をやわらかく伝え、必要な根拠を示しましょう。"),
        p1=rows(
            ("{t}I'm not entirely convinced that{/t} it'll work.", "うまくいくとは{t}完全には納得していません{/t}。", "I'm not entirely convinced|that|it'll work."),
            ("{t}I'm not entirely convinced that{/t} this plan is practical.", "この案が現実的だとは{t}完全には納得していません{/t}。", "I'm not entirely convinced|that|this plan is practical."),
            ("{t}I'm not entirely convinced that{/t} the deadline is realistic.", "その期限が現実的だとは{t}完全には納得していません{/t}。", "I'm not entirely convinced|that|the deadline is realistic."),
            ("{t}I'm not entirely convinced that{/t} we have enough evidence.", "十分な根拠があるとは{t}完全には納得していません{/t}。", "I'm not entirely convinced|that|we have enough evidence."),
        ),
        p2=rows(
            ("{t}I'd want to see{/t} the numbers {t}before deciding{/t}.", "{t}決める前に{/t}数字を{t}確認したいです{/t}。", "I'd want to see|the numbers|before|deciding."),
            ("{t}I'd want to see{/t} the final price {t}before agreeing{/t}.", "{t}同意する前に{/t}最終価格を{t}確認したいです{/t}。", "I'd want to see|the final price|before|agreeing."),
            ("{t}I'd want to see{/t} the evidence {t}before approving it{/t}.", "{t}承認する前に{/t}根拠を{t}確認したいです{/t}。", "I'd want to see|the evidence|before|approving it."),
            ("{t}I'd want to see{/t} the full plan {t}before choosing{/t}.", "{t}選ぶ前に{/t}案全体を{t}確認したいです{/t}。", "I'd want to see|the full plan|before|choosing."),
        ),
        rules=(("Follow convinced with that plus the complete idea you doubt.", "convinced のあとに that と、疑問に思う内容を文で続けます。"), ("Put the evidence after see, then use before plus the -ing action.", "see のあとに根拠を置き、before と -ing 形でその後の判断を示します。")),
        prompt=("Respond to my proposal with a real doubt, or say that you are convinced.", "私の提案に本当の疑問を伝えるか、納得していると答えましょう。"),
    ),
    93: dict(
        slug="to-be-fair", title="To be fair,", ko="공정하게 말하면", ja="公平に言えば",
        goal=("Concede one point before stating what still needs attention.", "相手の一つの点を認めてから、まだ必要なことを伝えましょう。"),
        p1=rows(
            ("{t}To be fair,{/t} they {t}did warn{/t} us.", "{t}公平に言えば{/t}、彼らは{t}確かに{/t}私たちに警告しました。", "To be fair,|they|did warn|us."),
            ("{t}To be fair,{/t} the supplier {t}did call{/t} us.", "{t}公平に言えば{/t}、取引先は{t}確かに{/t}私たちに電話をくれました。", "To be fair,|the supplier|did call|us."),
            ("{t}To be fair,{/t} she {t}did send{/t} the draft.", "{t}公平に言えば{/t}、彼女は{t}確かに{/t}下書きを送りました。", "To be fair,|she|did send|the draft."),
            ("{t}To be fair,{/t} we {t}did discuss{/t} the cost.", "{t}公平に言えば{/t}、費用については{t}確かに{/t}話し合いました。", "To be fair,|we|did discuss|the cost."),
        ),
        p2=rows(
            ("{t}That said,{/t} we still need a date.", "{t}とはいえ{/t}、まだ日付が必要です。", "That said,|we|still need|a date."),
            ("{t}That said,{/t} we still need a price.", "{t}とはいえ{/t}、まだ価格が必要です。", "That said,|we|still need|a price."),
            ("{t}That said,{/t} the timing is still unclear.", "{t}とはいえ{/t}、時期はまだ不明です。", "That said,|the timing|is still|unclear."),
            ("{t}That said,{/t} the plan still needs approval.", "{t}とはいえ{/t}、その案にはまだ承認が必要です。", "That said,|the plan|still needs|approval."),
        ),
        rules=(("Use To be fair before the point you are granting; did plus a plain verb adds emphasis.", "認める点の前に To be fair を置き、did と動詞の原形で「確かに」を強調します。"), ("Use That said at the start of the counterpoint that follows the concession.", "認めたあとに続く反対側の要点は、文頭の That said で始めます。")),
        prompt=("React to my opinion by conceding one point, or say that you fully agree.", "私の意見の一つの点を認めて返すか、全面的に賛成だと伝えましょう。"),
    ),
    94: dict(
        slug="wouldnt-it-be-better-if", title="Wouldn't it be better if", ko="차라리 ~하는 게 낫지 않을까요", ja="むしろ〜したほうがよくないですか",
        goal=("Suggest an alternative as a tentative question.", "別案を断定ではなく、控えめな質問として提案しましょう。"),
        p1=rows(
            ("{t}Wouldn't it be better if we waited{/t}?", "{t}待ったほうがよくないですか{/t}？", "Wouldn't it be better|if we|waited?"),
            ("{t}Wouldn't it be better if we checked{/t}?", "{t}確認したほうがよくないですか{/t}？", "Wouldn't it be better|if we|checked?"),
            ("{t}Wouldn't it be better if we called{/t}?", "{t}電話したほうがよくないですか{/t}？", "Wouldn't it be better|if we|called?"),
            ("{t}Wouldn't it be better if we asked{/t} first?", "{t}先に聞いたほうがよくないですか{/t}？", "Wouldn't it be better|if we|asked first?"),
        ),
        p2=rows(
            ("{t}What if we tried{/t} it the other way?", "{t}別のやり方で試してみたら{/t}どうですか？", "What if|we|tried it|the other way?"),
            ("{t}What if we sent{/t} the summary first?", "{t}先に要約を送ってみたら{/t}どうですか？", "What if|we|sent|the summary first?"),
            ("{t}What if we moved{/t} it to Friday?", "{t}金曜日に動かしてみたら{/t}どうですか？", "What if|we|moved it|to Friday?"),
            ("{t}What if we used{/t} the smaller room?", "{t}小さい会議室を使ってみたら{/t}どうですか？", "What if|we|used|the smaller room?"),
        ),
        rules=(("After if we, use a past form to make the suggestion tentative, not past in time.", "if we のあとに過去形を使い、過去ではなく提案を控えめにします。"), ("What if we also takes a past form when you float an alternative.", "別案を持ち出す What if we のあとにも過去形を使います。")),
        prompt=("Suggest one change to my plan, or say that the plan works as it is.", "私の案に変更を一つ提案するか、このままでよいと伝えましょう。"),
    ),
    95: dict(
        slug="where-id-push-back-is-on-the-cost", title="Where I'd push back is on the cost", ko="제가 이의를 제기하고 싶은 건 비용이에요", ja="私が異議を唱えたいのは費用です",
        goal=("Limit disagreement to one weakness and name what was overlooked.", "反対する点を一つに絞り、見落とされた要素を示しましょう。"),
        p1=rows(
            ("{t}Where I'd push back is on{/t} the cost.", "私が{t}異議を唱えたいのは{/t}費用です。", "Where I'd push back|is|on|the cost."),
            ("{t}Where I'd push back is on{/t} the timing.", "私が{t}異議を唱えたいのは{/t}時期です。", "Where I'd push back|is|on|the timing."),
            ("{t}Where I'd push back is on{/t} the deadline.", "私が{t}異議を唱えたいのは{/t}期限です。", "Where I'd push back|is|on|the deadline."),
            ("{t}Where I'd push back is on{/t} the final number.", "私が{t}異議を唱えたいのは{/t}最終的な数字です。", "Where I'd push back|is|on|the final number."),
        ),
        p2=rows(
            ("{t}I don't think{/t} that takes the delay {t}into account{/t}.", "それが遅れを{t}考慮に入れている{/t}とは{t}思いません{/t}。", "I don't think|that takes|the delay|into account."),
            ("{t}I don't think{/t} that takes the budget {t}into account{/t}.", "それが予算を{t}考慮に入れている{/t}とは{t}思いません{/t}。", "I don't think|that takes|the budget|into account."),
            ("{t}I don't think{/t} that takes the extra work {t}into account{/t}.", "それが追加作業を{t}考慮に入れている{/t}とは{t}思いません{/t}。", "I don't think|that takes|the extra work|into account."),
            ("{t}I don't think{/t} that takes the risk {t}into account{/t}.", "それがリスクを{t}考慮に入れている{/t}とは{t}思いません{/t}。", "I don't think|that takes|the risk|into account."),
        ),
        rules=(("Put the one area of disagreement after push back is on.", "反対する一つの領域を push back is on のあとに置きます。"), ("Place the missing factor between takes and into account.", "見落とされた要素を takes と into account の間に置きます。")),
        prompt=("Question one part of my proposal, or say that you accept the whole proposal.", "私の提案の一部に異議を示すか、全体を受け入れると伝えましょう。"),
    ),
    96: dict(
        slug="i-meant-next-friday-not-this-friday", title="I meant next Friday, not this Friday", ko="이번 주 금요일이 아니라 다음 주 금요일을 말한 거예요", ja="今週の金曜日ではなく、来週の金曜日という意味でした",
        goal=("Correct one mistaken detail and restate your intended message.", "誤解された一つの情報を直し、本来の意図を言い直しましょう。"),
        p1=rows(
            ("{t}I meant{/t} next Friday, {t}not{/t} this Friday.", "今週の金曜日{t}ではなく{/t}、来週の金曜日という{t}意味でした{/t}。", "I meant|next Friday,|not|this Friday."),
            ("{t}I meant{/t} the morning, {t}not{/t} the afternoon.", "午後{t}ではなく{/t}、午前という{t}意味でした{/t}。", "I meant|the morning,|not|the afternoon."),
            ("{t}I meant{/t} the small room, {t}not{/t} the main room.", "メイン会議室{t}ではなく{/t}、小さい会議室という{t}意味でした{/t}。", "I meant|the small room,|not|the main room."),
            ("{t}I meant{/t} the draft, {t}not{/t} the final version.", "最終版{t}ではなく{/t}、下書きという{t}意味でした{/t}。", "I meant|the draft,|not|the final version."),
        ),
        p2=rows(
            ("{t}What I was trying to say is that{/t} we need more time.", "{t}私が言おうとしていたのは{/t}、もっと時間が必要だということです。", "What I was trying to say|is that|we need more time."),
            ("{t}What I was trying to say is that{/t} the date may change.", "{t}私が言おうとしていたのは{/t}、日付が変わるかもしれないということです。", "What I was trying to say|is that|the date may change."),
            ("{t}What I was trying to say is that{/t} this is only a draft.", "{t}私が言おうとしていたのは{/t}、これは下書きにすぎないということです。", "What I was trying to say|is that|this is only a draft."),
            ("{t}What I was trying to say is that{/t} we should wait.", "{t}私が言おうとしていたのは{/t}、待つべきだということです。", "What I was trying to say|is that|we should wait."),
        ),
        rules=(("Put the intended detail after meant and the mistaken detail after not.", "意図した情報を meant のあと、誤解された情報を not のあとに置きます。"), ("Keep What I was trying to say is that together, then add the intended clause.", "What I was trying to say is that をひとまとまりにして、本来の内容を文で続けます。")),
        prompt=("Correct one detail people sometimes misunderstand, or say that nothing needs correcting.", "誤解されることのある情報を一つ直すか、訂正はないと伝えましょう。"),
    ),
    97: dict(
        slug="id-rather-not-if-thats-ok", title="I'd rather not, if that's OK", ko="괜찮다면 안 하고 싶어요", ja="よければ、遠慮したいです",
        goal=("Decline explicitly and offer a polite alternative.", "はっきり断りながら、丁寧な別案を出しましょう。"),
        p1=rows(
            ("{t}I'd rather not{/t} join, {t}if that's OK{/t}.", "{t}よければ{/t}、参加は{t}遠慮したいです{/t}。", "I'd rather not|join,|if that's OK."),
            ("{t}I'd rather not{/t} drive, {t}if that's OK{/t}.", "{t}よければ{/t}、運転は{t}遠慮したいです{/t}。", "I'd rather not|drive,|if that's OK."),
            ("{t}I'd rather not{/t} decide today, {t}if that's OK{/t}.", "{t}よければ{/t}、今日決めるのは{t}遠慮したいです{/t}。", "I'd rather not|decide today,|if that's OK."),
            ("{t}I'd rather not{/t} share it yet, {t}if that's OK{/t}.", "{t}よければ{/t}、まだ共有するのは{t}遠慮したいです{/t}。", "I'd rather not|share it yet,|if that's OK."),
        ),
        p2=rows(
            ("{t}Could we do{/t} it {t}another time{/t}?", "{t}また別の機会に{/t}{t}できますか{/t}？", "Could we|do it|another time?"),
            ("{t}Could we meet{/t} {t}another time{/t}?", "{t}また別の機会に{/t}{t}会えますか{/t}？", "Could we|meet|another time?"),
            ("{t}Could we discuss{/t} it {t}another time{/t}?", "{t}また別の機会に{/t}{t}話し合えますか{/t}？", "Could we|discuss it|another time?"),
            ("{t}Could we decide{/t} {t}another time{/t}?", "{t}また別の機会に{/t}{t}決められますか{/t}？", "Could we|decide|another time?"),
        ),
        rules=(("After would rather not, use a plain verb without to.", "would rather not のあとには to を付けず、動詞の原形を使います。"), ("After Could we, use a plain verb and place another time after the activity.", "Could we のあとに動詞の原形を置き、活動のあとに another time を続けます。")),
        prompt=("Respond to my invitation honestly, or accept it if you want to join.", "私の誘いに正直に答えるか、参加したければ受けましょう。"),
    ),
    98: dict(
        slug="thats-mostly-because-of", title="That's mostly because of", ko="그건 주로 ~ 때문이에요", ja="それは主に〜が原因です",
        goal=("Name the main source of a situation without claiming it is the only cause.", "唯一の原因とは断定せず、主な原因を示しましょう。"),
        p1=rows(
            ("{t}That's mostly because of{/t} the delay.", "それは{t}主に遅れが原因です{/t}。", "That's|mostly|because of|the delay."),
            ("{t}That's mostly because of{/t} the late approval.", "それは{t}主に承認の遅れが原因です{/t}。", "That's|mostly|because of|the late approval."),
            ("{t}That's mostly because of{/t} the missing information.", "それは{t}主に不足している情報が原因です{/t}。", "That's|mostly|because of|the missing information."),
            ("{t}That's mostly because of{/t} the weather.", "それは{t}主に天候が原因です{/t}。", "That's|mostly|because of|the weather."),
        ),
        p2=rows(
            ("{t}A lot of it comes from{/t} a misunderstanding.", "その多くは{t}誤解から生じています{/t}。", "A lot of it|comes from|a misunderstanding."),
            ("{t}A lot of it comes from{/t} unclear instructions.", "その多くは{t}分かりにくい指示から生じています{/t}。", "A lot of it|comes from|unclear instructions."),
            ("{t}A lot of it comes from{/t} the old system.", "その多くは{t}古い仕組みから生じています{/t}。", "A lot of it|comes from|the old system."),
            ("{t}A lot of it comes from{/t} one missing step.", "その多くは{t}一つ抜けた手順から生じています{/t}。", "A lot of it|comes from|one missing step."),
        ),
        rules=(("Use because of before a noun or -ing phrase, not before a complete subject-verb clause.", "because of のあとには名詞か -ing 句を置き、主語と動詞のある文は置きません。"), ("Keep comes from with the noun phrase that names the source.", "原因を示す名詞句の前では comes from をひとまとまりで使います。")),
        prompt=("Explain one real cause, or say that you are not sure what caused it.", "実際の原因を一つ説明するか、原因は分からないと伝えましょう。"),
    ),
    99: dict(
        slug="that-suggests-that", title="That suggests that", ko="그건 ~라는 뜻일 수 있어요", ja="それは〜を示していると考えられます",
        goal=("Draw a cautious conclusion from an observation.", "観察したことから、控えめに結論を導きましょう。"),
        p1=rows(
            ("The drop {t}suggests that{/t} people didn't see it.", "その減少は、人々が見なかったことを{t}示しています{/t}。", "The drop|suggests that|people|didn't see it."),
            ("The empty room {t}suggests that{/t} the message was missed.", "空の会議室は、連絡が見落とされたことを{t}示しています{/t}。", "The empty room|suggests that|the message|was missed."),
            ("The low response {t}suggests that{/t} the question was unclear.", "反応の少なさは、質問が不明確だったことを{t}示しています{/t}。", "The low response|suggests that|the question|was unclear."),
            ("The second call {t}suggests that{/t} the issue is urgent.", "二度目の電話は、その問題が緊急だということを{t}示しています{/t}。", "The second call|suggests that|the issue|is urgent."),
        ),
        p2=rows(
            ("{t}That would explain{/t} the delay.", "{t}それなら遅れの説明がつきます{/t}。", "That|would explain|the delay."),
            ("{t}That would explain{/t} the low response.", "{t}それなら反応が少なかった理由を説明できます{/t}。", "That|would explain|the low response."),
            ("{t}That would explain{/t} the empty room.", "{t}それなら会議室が空だった理由を説明できます{/t}。", "That|would explain|the empty room."),
            ("{t}That would explain{/t} the missing replies.", "{t}それなら返事がなかった理由を説明できます{/t}。", "That|would explain|the missing replies."),
        ),
        rules=(("Use suggests that before the inferred clause, not before a noun alone.", "推測した内容を文で続けるときは suggests that を使います。"), ("Use would explain for a tentative logical fit, not a future prediction.", "断定せず論理的に説明できると示すときに would explain を使います。")),
        prompt=("Interpret one real observation, or say that it does not suggest anything yet.", "実際の観察を一つ解釈するか、まだ何も示していないと伝えましょう。"),
    ),
    100: dict(
        slug="as-a-result-we-had-to-reschedule", title="As a result, we had to reschedule", ko="그 결과 일정을 다시 잡아야 했어요", ja="その結果、日程を変更しなければなりませんでした",
        goal=("Connect a stated cause to two practical consequences.", "示された原因を、二つの実際的な結果につなげましょう。"),
        p1=rows(
            ("The train was canceled. {t}As a result,{/t} we had to reschedule.", "電車が運休しました。{t}その結果{/t}、日程を変更しなければなりませんでした。", "The train was canceled.|As a result,|we had to|reschedule."),
            ("The file arrived late. {t}As a result,{/t} we missed the deadline.", "ファイルが遅れて届きました。{t}その結果{/t}、期限に間に合いませんでした。", "The file arrived late.|As a result,|we missed|the deadline."),
            ("The room was unavailable. {t}As a result,{/t} we moved the meeting.", "会議室が使えませんでした。{t}その結果{/t}、会議を移しました。", "The room was unavailable.|As a result,|we moved|the meeting."),
            ("The price went up. {t}As a result,{/t} we changed the plan.", "価格が上がりました。{t}その結果{/t}、案を変更しました。", "The price went up.|As a result,|we changed|the plan."),
        ),
        p2=rows(
            ("We had to reschedule. {t}That meant{/t} we lost a week.", "日程を変更しなければなりませんでした。{t}そのため{/t}、1週間を失いました。", "We had to reschedule.|That meant|we lost|a week."),
            ("We missed the deadline. {t}That meant{/t} the launch moved.", "期限に間に合いませんでした。{t}そのため{/t}、開始日がずれました。", "We missed the deadline.|That meant|the launch|moved."),
            ("We moved the meeting. {t}That meant{/t} two people couldn't join.", "会議を移しました。{t}そのため{/t}、二人が参加できませんでした。", "We moved the meeting.|That meant|two people|couldn't join."),
            ("We changed the plan. {t}That meant{/t} more work for the team.", "案を変更しました。{t}そのため{/t}、チームの作業が増えました。", "We changed the plan.|That meant|more work|for the team."),
        ),
        rules=(("Put As a result at the start of a new result sentence after the cause is complete.", "原因の文を終え、結果を述べる新しい文の先頭に As a result を置きます。"), ("Use That meant plus a clause to state the practical consequence of the whole fact before it.", "前の事実全体がもたらした実際の結果を That meant と文で続けます。")),
        prompt=("Connect the late file to one possible result, or say that nothing changed.", "遅れたファイルを一つの結果につなげるか、何も変わらなかったと伝えましょう。"),
    ),
    101: dict(
        slug="it-depends-on-whether", title="It depends on whether", ko="~인지에 따라 달라요", ja="〜かどうかによります",
        goal=("Make an answer conditional, then name what remains true in both outcomes.", "答えを条件付きにし、どちらの結果でも変わらないことを伝えましょう。"),
        p1=rows(
            ("{t}It depends on whether{/t} they approve it.", "彼らが承認するかどうかに{t}よります{/t}。", "It depends|on whether|they approve|it."),
            ("{t}It depends on whether{/t} the room is free.", "会議室が空いているかどうかに{t}よります{/t}。", "It depends|on whether|the room|is free."),
            ("{t}It depends on whether{/t} the price changes.", "価格が変わるかどうかに{t}よります{/t}。", "It depends|on whether|the price|changes."),
            ("{t}It depends on whether{/t} we hear back today.", "今日返事が来るかどうかに{t}よります{/t}。", "It depends|on whether|we hear back|today."),
        ),
        p2=rows(
            ("{t}Either way,{/t} we should prepare.", "{t}どちらにしても{/t}、準備すべきです。", "Either way,|we|should prepare."),
            ("{t}Either way,{/t} we need a backup plan.", "{t}どちらにしても{/t}、予備案が必要です。", "Either way,|we need|a backup plan."),
            ("{t}Either way,{/t} the deadline stays the same.", "{t}どちらにしても{/t}、期限は変わりません。", "Either way,|the deadline|stays the same."),
            ("{t}Either way,{/t} I'll send the update.", "{t}どちらにしても{/t}、更新を送ります。", "Either way,|I'll send|the update."),
        ),
        rules=(("Keep depends on whether together, then add the unresolved possibility as a clause.", "depends on whether をひとまとまりにして、未確定の可能性を文で続けます。"), ("Use Either way before the action or fact that is true in both possible outcomes.", "二つの可能性のどちらでも変わらない行動や事実の前に Either way を置きます。")),
        prompt=("Answer my real question conditionally, or give a clear yes or no if nothing is unresolved.", "私の質問に条件付きで答えるか、未確定な点がなければ、はっきり「はい／いいえ」で答えましょう。"),
    ),
    102: dict(
        slug="otherwise-wed-have-to-start-again", title="Otherwise, we'd have to start again", ko="그렇지 않으면 다시 시작해야 해요", ja="そうでなければ、また最初から始めなければなりません",
        goal=("State the consequence of a failed condition and offer a fallback.", "条件が満たされない場合の結果を示し、代案を出しましょう。"),
        p1=rows(
            ("{t}Otherwise, we'd have to{/t} start again.", "{t}そうでなければ{/t}、また最初から始めなければなりません。", "Otherwise,|we'd have to start|again."),
            ("{t}Otherwise, we'd have to{/t} move the meeting.", "{t}そうでなければ{/t}、会議を移さなければなりません。", "Otherwise,|we'd have to move|the meeting."),
            ("{t}Otherwise, we'd have to{/t} change the plan.", "{t}そうでなければ{/t}、案を変えなければなりません。", "Otherwise,|we'd have to change|the plan."),
            ("{t}Otherwise, we'd have to{/t} pay the full price.", "{t}そうでなければ{/t}、全額を払わなければなりません。", "Otherwise,|we'd have to pay|the full price."),
        ),
        p2=rows(
            ("{t}If that doesn't work, we could{/t} ask them.", "{t}それでうまくいかなければ{/t}、彼らに聞くことができます。", "If that doesn't work,|we could ask|them."),
            ("{t}If that doesn't work, we could{/t} call the supplier.", "{t}それでうまくいかなければ{/t}、取引先に電話できます。", "If that doesn't work,|we could call|the supplier."),
            ("{t}If that doesn't work, we could{/t} use the old plan.", "{t}それでうまくいかなければ{/t}、古い案を使えます。", "If that doesn't work,|we could use|the old plan."),
            ("{t}If that doesn't work, we could{/t} try another date.", "{t}それでうまくいかなければ{/t}、別の日を試せます。", "If that doesn't work,|we could try|another date."),
        ),
        rules=(("Otherwise replaces the failed condition; keep would have to with the necessary consequence.", "Otherwise が満たされなかった条件を表し、would have to で必要になる結果を続けます。"), ("After If that doesn't work, use could plus a plain verb for a possible fallback.", "If that doesn't work のあとに could と動詞の原形を置き、可能な代案を示します。")),
        prompt=("Build a fallback chain, or explain why another fallback is not needed.", "代案を順につなげるか、別の代案が必要ない理由を説明しましょう。"),
    ),
}


SPECS = {
    92: semantic_spec(
        (("Use this to signal a real doubt without stating blunt disagreement.", "はっきり反対と言わずに、本当の疑問を伝えるときに使います。"), ("Use this to name the evidence you need before making a decision.", "判断する前に必要な根拠を示すときに使います。")),
        (("State one real doubt, or say you are convinced.", "本当の疑問を一つ言うか、納得していると伝えましょう。"), ("Name evidence you would genuinely want, or say you can decide now.", "本当に確認したい根拠を挙げるか、今決められると伝えましょう。")),
        (choice_rows((("うまくいくとは{t}完全には納得していません{/t}。", "I'm not entirely convinced ", "that", "about", " it'll work."), ("この案が現実的だとは{t}完全には納得していません{/t}。", "I'm not entirely convinced ", "that", "about", " this plan is practical."), ("期限が現実的だとは{t}完全には納得していません{/t}。", "I'm not entirely convinced ", "that", "about", " the deadline is realistic."), ("十分な根拠があるとは{t}完全には納得していません{/t}。", "I'm not entirely convinced ", "that", "about", " we have enough evidence."))), choice_rows((("数字を確認してから{t}決めたいです{/t}。", "I'd want to see the numbers before ", "deciding", "decide", "."), ("最終価格を確認してから{t}同意したいです{/t}。", "I'd want to see the final price before ", "agreeing", "agree", "."), ("根拠を確認してから{t}承認したいです{/t}。", "I'd want to see the evidence before ", "approving", "approve", " it."), ("案全体を確認してから{t}選びたいです{/t}。", "I'd want to see the full plan before ", "choosing", "choose", ".")))),
        (("Attach the doubtful idea", "疑問に思う内容をつなぐ", "I'm not entirely convinced + <b>that</b> + 文", "Soft disagreement", "やわらかな反対", ("I'm not entirely convinced <b>that it'll work</b>.", "I'm not entirely convinced <b>that the plan is practical</b>.")), ("Evidence before the decision", "判断前の根拠", "I'd want to see + 根拠 + <b>before + -ing</b>", "Same person decides", "判断する人は同じ", ("I'd want to see the numbers <b>before deciding</b>.", "I'd want to see the price <b>before agreeing</b>."))),
        ("Tentative or direct disagreement?", "控えめな反対・直接的な反対", "Both disagree. The first leaves room for more evidence; the second states the difference directly.", "どちらも反対です。前者は追加の根拠で変わる余地を残し、後者は違いを直接示します。", ("Open to more evidence", "追加の根拠に開かれている", "I'm not entirely convinced that it'll work.", "うまくいくとは完全には納得していません。"), ("Direct position", "立場を直接示す", "I don't agree that it'll work.", "うまくいくとは思いません。")),
    ),
    93: semantic_spec(
        (("Use this to grant the other side one fair point before you respond.", "返答する前に、相手側の妥当な点を一つ認めるときに使います。"), ("Use this to turn from the concession to the point that still matters.", "認めた点から、まだ重要な反対側の要点へ移るときに使います。")),
        (("Concede one true point, or say there is nothing to concede.", "本当に認められる点を一つ言うか、認める点はないと伝えましょう。"), ("Add one genuine counterpoint, or say no issue remains.", "本当の反対側の要点を一つ加えるか、問題は残っていないと伝えましょう。")),
        (choice_rows((("公平に言えば、彼らは確かに{t}警告しました{/t}。", "To be fair, they did ", "warn", "warned", " us."), ("公平に言えば、取引先は確かに{t}電話しました{/t}。", "To be fair, the supplier did ", "call", "called", "."), ("公平に言えば、彼女は確かに{t}送りました{/t}。", "To be fair, she did ", "send", "sent", " the draft."), ("公平に言えば、私たちは確かに{t}話し合いました{/t}。", "To be fair, we did ", "discuss", "discussed", " the cost."))), choice_rows((("{t}とはいえ{/t}、まだ日付が必要です。", "That ", "said", "saying", ", we still need a date."), ("{t}とはいえ{/t}、まだ価格が必要です。", "That ", "said", "saying", ", we still need a price."), ("{t}とはいえ{/t}、時期はまだ不明です。", "That ", "said", "saying", ", the timing is still unclear."), ("{t}とはいえ{/t}、その案にはまだ承認が必要です。", "That ", "said", "saying", ", the plan still needs approval.")))),
        (("Emphasize the granted point", "認める点を強調", "To be fair, + 主語 + <b>did + 動詞の原形</b>", "Concession", "譲歩", ("To be fair, they <b>did warn</b> us.", "To be fair, she <b>did send</b> it.")), ("Turn to the counterpoint", "反対側の要点へ", "<b>That said,</b> + まだ重要な点", "Concede, then counter", "認めてから反対へ", ("<b>That said,</b> we still need a date.", "<b>That said,</b> the timing is unclear."))),
        ("Fair or honest?", "fair と honest", "Use “To be fair” to balance both sides, whereas “To be honest” introduces your own candid view.", "両方の立場を公平に扱うなら「To be fair」、自分の率直な考えを切り出すなら「To be honest」を使います。", ("Balance the sides", "双方を公平に扱う", "To be fair, they did warn us.", "公平に言えば、彼らは確かに警告しました。"), ("Introduce candor", "率直な考えを切り出す", "To be honest, I expected more.", "正直に言うと、もっと期待していました。")),
    ),
    94: semantic_spec(
        (("Use this to present your preferred alternative as a question that invites agreement.", "自分の望む別案を、同意を促す質問として示すときに使います。"), ("Use this to float another possible action without presenting it as a correction.", "別の行動を訂正ではなく、一つの可能性として持ち出すときに使います。")),
        (("Suggest one useful change, or say the current plan is better.", "役立つ変更を一つ提案するか、今の案のほうがよいと伝えましょう。"), ("Offer one different approach, or say you have no alternative.", "別のやり方を一つ出すか、代案はないと伝えましょう。")),
        (choice_rows((("{t}待ったほうがよくないですか{/t}？", "Wouldn't it be better if we ", "waited", "wait", "?"), ("{t}確認したほうがよくないですか{/t}？", "Wouldn't it be better if we ", "checked", "check", "?"), ("{t}電話したほうがよくないですか{/t}？", "Wouldn't it be better if we ", "called", "call", "?"), ("{t}先に聞いたほうがよくないですか{/t}？", "Wouldn't it be better if we ", "asked", "ask", " first?"))), choice_rows((("{t}別のやり方で試してみたら{/t}どうですか？", "What if we ", "tried", "try", " it the other way?"), ("{t}先に要約を送ってみたら{/t}どうですか？", "What if we ", "sent", "send", " the summary first?"), ("{t}金曜日に動かしてみたら{/t}どうですか？", "What if we ", "moved", "move", " it to Friday?"), ("{t}小さい会議室を使ってみたら{/t}どうですか？", "What if we ", "used", "use", " the smaller room?")))),
        (("Past form, present suggestion", "過去形でも今の提案", "Wouldn't it be better if we + <b>過去形</b>?", "Tentative alternative", "控えめな別案", ("Wouldn't it be better if we <b>waited</b>?", "Wouldn't it be better if we <b>checked</b>?")), ("Float another route", "別の道を持ち出す", "What if we + <b>過去形</b>?", "Open suggestion", "開かれた提案", ("What if we <b>tried</b> it another way?", "What if we <b>sent</b> the summary first?"))),
        ("Leading or open?", "同意を求める・案を開く", "“Wouldn't it be better if” signals your preferred answer. “Maybe we could” leaves the choice more open.", "「Wouldn't it be better if」は自分の望む答えを示します。「Maybe we could」は選択をより開いたままにします。", ("Preferred alternative", "望む別案がある", "Wouldn't it be better if we waited?", "待ったほうがよくないですか？"), ("More open option", "より開かれた案", "Maybe we could wait.", "待つという手もあるかもしれません。")),
    ),
    95: semantic_spec(
        (("Use this to isolate one area of disagreement instead of rejecting the whole proposal.", "提案全体を否定せず、反対する領域を一つに絞るときに使います。"), ("Use this to point out one factor that the current judgment leaves out.", "今の判断で抜けている要素を一つ指摘するときに使います。")),
        (("Name one specific weakness, or say you accept every part.", "具体的な弱点を一つ言うか、すべて受け入れると伝えましょう。"), ("Name one overlooked factor, or say the judgment is complete.", "見落とされた要素を一つ言うか、判断は十分だと伝えましょう。")),
        (choice_rows((("私が異議を唱えたいのは{t}費用についてです{/t}。", "Where I'd push back is ", "on", "about", " the cost."), ("私が異議を唱えたいのは{t}時期についてです{/t}。", "Where I'd push back is ", "on", "about", " the timing."), ("私が異議を唱えたいのは{t}期限についてです{/t}。", "Where I'd push back is ", "on", "about", " the deadline."), ("私が異議を唱えたいのは{t}最終的な数字についてです{/t}。", "Where I'd push back is ", "on", "about", " the final number."))), choice_rows((("遅れを{t}考慮に入れていない{/t}と思います。", "I don't think that takes the delay ", "into", "in", " account."), ("予算を{t}考慮に入れていない{/t}と思います。", "I don't think that takes the budget ", "into", "in", " account."), ("追加作業を{t}考慮に入れていない{/t}と思います。", "I don't think that takes the extra work ", "into", "in", " account."), ("リスクを{t}考慮に入れていない{/t}と思います。", "I don't think that takes the risk ", "into", "in", " account.")))),
        (("Focus one area", "一つの領域に絞る", "Where I'd push back + is + <b>on</b> + 一点", "Not the whole proposal", "提案全体ではない", ("Where I'd push back is <b>on the cost</b>.", "Where I'd push back is <b>on the timing</b>.")), ("Insert the missing factor", "抜けた要素を入れる", "take + 要素 + <b>into account</b>", "Included in the judgment", "判断に含める", ("That takes <b>the delay into account</b>.", "That takes <b>the risk into account</b>."))),
        ("Push back or raise a concern?", "異議・懸念", "“Push back” clearly signals disagreement. “Raise a concern” sounds less oppositional when you mainly want discussion.", "「push back」は反対を明確に示します。主に話し合いたいときは「raise a concern」のほうが対立的に聞こえません。", ("Clear disagreement", "明確な反対", "I'd push back on the cost.", "費用には異議を唱えたいです。"), ("Invite discussion", "話し合いを促す", "I'd raise a concern about the cost.", "費用について懸念を挙げたいです。")),
    ),
    96: semantic_spec(
        (("Use this to replace one detail that the listener understood incorrectly.", "聞き手が誤って理解した一つの情報を置き換えるときに使います。"), ("Use this to restate the complete message you intended to communicate.", "本来伝えたかった内容全体を言い直すときに使います。")),
        (("Correct one real detail, or say the listener understood correctly.", "本当の情報を一つ訂正するか、相手の理解が正しいと伝えましょう。"), ("Restate one intended message, or say no restatement is needed.", "本来の意図を一つ言い直すか、言い直しは必要ないと伝えましょう。")),
        (choice_rows((("{t}今週ではなく来週の{/t}金曜日という意味でした。", "I meant ", "next", "this", " Friday, not this Friday."), ("{t}午後ではなく午前{/t}という意味でした。", "I meant the ", "morning", "afternoon", ", not the afternoon."), ("{t}メインではなく小さい{/t}会議室という意味でした。", "I meant the ", "small", "main", " room, not the main room."), ("{t}最終版ではなく下書き{/t}という意味でした。", "I meant the ", "draft", "final version", ", not the final version."))), choice_rows((("私が{t}言おうとしていた{/t}のは、もっと時間が必要だということです。", "What I was trying to ", "say", "tell", " is that we need more time."), ("私が{t}言おうとしていた{/t}のは、日付が変わるかもしれないということです。", "What I was trying to ", "say", "tell", " is that the date may change."), ("私が{t}言おうとしていた{/t}のは、これは下書きだということです。", "What I was trying to ", "say", "tell", " is that this is only a draft."), ("私が{t}言おうとしていた{/t}のは、待つべきだということです。", "What I was trying to ", "say", "tell", " is that we should wait.")))),
        (("Replace A with B", "AをBに置き換える", "I meant + <b>A</b>, not + <b>B</b>", "Intended then mistaken", "意図→誤解", ("I meant <b>next Friday, not this Friday</b>.", "I meant <b>the draft, not the final version</b>.")), ("Restate the intended clause", "本来の内容を言い直す", "What I was trying to say + <b>is that</b> + 文", "Complete intended message", "本来の内容全体", ("What I was trying to say <b>is that we need more time</b>.", "What I was trying to say <b>is that we should wait</b>."))),
        ("Mean or meant?", "mean と meant", "Use “I mean” to clarify now, whereas “I meant” repairs something you said earlier.", "今言っていることを補足するなら「I mean」、前に言ったことを訂正するなら「I meant」を使います。", ("Clarify now", "今の発言を補足", "I mean next Friday.", "つまり来週の金曜日です。"), ("Repair earlier words", "前の発言を訂正", "I meant next Friday.", "来週の金曜日という意味でした。")),
    ),
    97: semantic_spec(
        (("Use this to decline explicitly while softening the refusal.", "はっきり断りながら、拒否をやわらげるときに使います。"), ("Use this to propose doing the activity at a different time.", "その活動を別の機会にする提案をするときに使います。")),
        (("Decline one real invitation, or accept it honestly.", "本当の誘いを一つ断るか、正直に受けましょう。"), ("Suggest doing it another time, or say no alternative works.", "別の機会にする提案をするか、代案も難しいと伝えましょう。")),
        (choice_rows((("よければ、参加は{t}遠慮したいです{/t}。", "I'd rather not ", "join", "to join", ", if that's OK."), ("よければ、運転は{t}遠慮したいです{/t}。", "I'd rather not ", "drive", "to drive", ", if that's OK."), ("よければ、今日決めるのは{t}遠慮したいです{/t}。", "I'd rather not ", "decide", "to decide", " today, if that's OK."), ("よければ、まだ共有するのは{t}遠慮したいです{/t}。", "I'd rather not ", "share", "to share", " it yet, if that's OK."))), choice_rows((("また別の機会に{t}できますか{/t}？", "Could we ", "do", "doing", " it another time?"), ("また別の機会に{t}会えますか{/t}？", "Could we ", "meet", "meeting", " another time?"), ("また別の機会に{t}話し合えますか{/t}？", "Could we ", "discuss", "discussing", " it another time?"), ("また別の機会に{t}決められますか{/t}？", "Could we ", "decide", "deciding", " another time?")))),
        (("No to after rather", "rather のあとに to は不要", "I'd rather not + <b>動詞の原形</b>", "Explicit softened refusal", "明確でやわらかな拒否", ("I'd rather not <b>join</b>.", "I'd rather not <b>decide today</b>.")), ("Modal plus plain verb", "助動詞＋動詞の原形", "Could we + <b>動詞の原形</b> + another time?", "Polite alternative", "丁寧な別案", ("Could we <b>meet another time</b>?", "Could we <b>discuss it another time</b>?"))),
        ("Pass or take a rain check?", "pass と rain check", "“I'll pass” declines this invitation. “Can I take a rain check?” suggests you may accept another time.", "「I'll pass」は今回の誘いを断ります。「Can I take a rain check?」は別の機会なら受ける可能性を示します。", ("Decline this invitation", "今回は断る", "I'll pass, thanks.", "今回は遠慮します。ありがとう。"), ("Maybe another time", "別の機会なら", "Can I take a rain check?", "また今度でもいいですか？")),
    ),
    98: semantic_spec(
        (("Use this to name the main cause while leaving room for other causes.", "ほかの原因の余地を残しながら、主な原因を示すときに使います。"), ("Use this to name the source that produces much of a situation.", "状況の多くを生み出している出所を示すときに使います。")),
        (("Name one likely main cause, or say you do not know it.", "主な原因と思われるものを一つ言うか、分からないと伝えましょう。"), ("Name one likely source, or say the source is unclear.", "考えられる出所を一つ言うか、不明だと伝えましょう。")),
        (choice_rows((("それは主に{t}遅れが原因です{/t}。", "That's mostly ", "because of", "because", " the delay."), ("それは主に{t}承認の遅れが原因です{/t}。", "That's mostly ", "because of", "because", " the late approval."), ("それは主に{t}情報不足が原因です{/t}。", "That's mostly ", "because of", "because", " the missing information."), ("それは主に{t}天候が原因です{/t}。", "That's mostly ", "because of", "because", " the weather."))), choice_rows((("その多くは誤解{t}から生じています{/t}。", "A lot of it ", "comes from", "comes of", " a misunderstanding."), ("その多くは分かりにくい指示{t}から生じています{/t}。", "A lot of it ", "comes from", "comes of", " unclear instructions."), ("その多くは古い仕組み{t}から生じています{/t}。", "A lot of it ", "comes from", "comes of", " the old system."), ("その多くは一つ抜けた手順{t}から生じています{/t}。", "A lot of it ", "comes from", "comes of", " one missing step.")))),
        (("Noun after because of", "because of のあとに名詞", "mostly + <b>because of</b> + 名詞・-ing", "Main cause, not only cause", "唯一とは限らない主因", ("That's mostly <b>because of the delay</b>.", "That's mostly <b>because of the weather</b>.")), ("Name the source", "出所を示す", "A lot of it + <b>comes from</b> + 名詞・-ing", "Source of the situation", "状況の出所", ("A lot of it <b>comes from a misunderstanding</b>.", "A lot of it <b>comes from the old system</b>."))),
        ("Mostly or partly?", "mostly と partly", "Use “mostly” for the main cause and “partly” for only one contributing cause.", "主な原因なら「mostly」、複数ある原因の一つにすぎないなら「partly」を使います。", ("Main cause", "主な原因", "That's mostly because of the delay.", "それは主に遅れが原因です。"), ("One contributing cause", "複数ある原因の一つ", "That's partly because of the delay.", "それは一部、遅れが原因です。")),
    ),
    99: semantic_spec(
        (("Use this to connect an observation to a cautious inferred conclusion.", "観察した事実を、控えめに推測した結論へつなぐときに使います。"), ("Use this when a new fact would logically account for something unexplained.", "新しい事実によって未説明のことに筋が通るときに使います。")),
        (("Draw one reasonable inference, or say the evidence is too weak.", "妥当な推測を一つ言うか、根拠が弱すぎると伝えましょう。"), ("Name one thing the fact could explain, or say it explains nothing.", "その事実で説明できることを一つ言うか、何も説明できないと伝えましょう。")),
        (choice_rows((("減少は、人々が見なかったことを{t}示しています{/t}。", "The drop suggests ", "that", "about", " people didn't see it."), ("空の会議室は、連絡が見落とされたことを{t}示しています{/t}。", "The empty room suggests ", "that", "about", " the message was missed."), ("反応の少なさは、質問が不明確だったことを{t}示しています{/t}。", "The low response suggests ", "that", "about", " the question was unclear."), ("二度目の電話は、問題が緊急だと{t}示しています{/t}。", "The second call suggests ", "that", "about", " the issue is urgent."))), choice_rows((("それなら遅れの{t}説明がつきます{/t}。", "That ", "would explain", "will explain", " the delay."), ("それなら反応の少なさの{t}説明がつきます{/t}。", "That ", "would explain", "will explain", " the low response."), ("それなら空の会議室の{t}説明がつきます{/t}。", "That ", "would explain", "will explain", " the empty room."), ("それなら返事がないことの{t}説明がつきます{/t}。", "That ", "would explain", "will explain", " the missing replies.")))),
        (("Observation to inference", "観察から推測へ", "観察 + <b>suggests that</b> + 推測の文", "Cautious conclusion", "控えめな結論", ("The drop <b>suggests that people didn't see it</b>.", "The empty room <b>suggests that the message was missed</b>.")), ("Tentative logical fit", "控えめな論理的説明", "That + <b>would explain</b> + 未説明の事実", "Not a future prediction", "未来の予測ではない", ("That <b>would explain the delay</b>.", "That <b>would explain the low response</b>."))),
        ("Tentative or confident?", "控えめ・確信", "Use “would explain” for a possible fit and “explains” when you accept it as the cause.", "可能な説明なら「would explain」、原因として受け入れるなら「explains」を使います。", ("Possible explanation", "可能な説明", "That would explain the delay.", "それなら遅れの説明がつきます。"), ("Accepted explanation", "原因として確信", "That explains the delay.", "それが遅れの原因です。")),
    ),
    100: semantic_spec(
        (("Use this at the start of a new sentence to link a stated cause to its result.", "述べた原因を結果へつなぐ新しい文の先頭で使います。"), ("Use this to add the practical consequence created by the fact before it.", "直前の事実が生んだ実際の影響を加えるときに使います。")),
        (("Give one real cause and result, or say there was no result.", "実際の原因と結果を一つ言うか、結果はなかったと伝えましょう。"), ("Add one real practical consequence, or say there was none.", "実際の影響を一つ加えるか、影響はなかったと伝えましょう。")),
        (choice_rows((("電車が運休しました。{t}その結果{/t}、日程を変更しました。", "The train was canceled. ", "As a result", "Because of", ", we had to reschedule."), ("ファイルが遅れて届きました。{t}その結果{/t}、期限に間に合いませんでした。", "The file arrived late. ", "As a result", "Because of", ", we missed the deadline."), ("会議室が使えませんでした。{t}その結果{/t}、会議を移しました。", "The room was unavailable. ", "As a result", "Because of", ", we moved the meeting."), ("価格が上がりました。{t}その結果{/t}、案を変えました。", "The price went up. ", "As a result", "Because of", ", we changed the plan."))), choice_rows((("日程を変更しました。{t}そのため{/t}、1週間を失いました。", "We had to reschedule. That ", "meant", "meaning", " we lost a week."), ("期限に間に合いませんでした。{t}そのため{/t}、開始日がずれました。", "We missed the deadline. That ", "meant", "meaning", " the launch moved."), ("会議を移しました。{t}そのため{/t}、二人が参加できませんでした。", "We moved the meeting. That ", "meant", "meaning", " two people couldn't join."), ("案を変えました。{t}そのため{/t}、作業が増えました。", "We changed the plan. That ", "meant", "meaning", " more work for the team.")))),
        (("Cause, full stop, result", "原因を終えて結果へ", "原因の文. + <b>As a result,</b> + 結果の文", "Across two sentences", "二文をつなぐ", ("The train was canceled. <b>As a result, we had to reschedule</b>.", "The price went up. <b>As a result, we changed the plan</b>.")), ("Whole fact to consequence", "事実全体から影響へ", "前の事実. + <b>That meant</b> + 影響の文", "Practical consequence", "実際の影響", ("We had to reschedule. <b>That meant we lost a week</b>.", "We moved the meeting. <b>That meant two people couldn't join</b>."))),
        ("Written or conversational link?", "書き言葉・会話", "“As a result” is clear and slightly formal. In everyday conversation, “so” often sounds lighter.", "「As a result」は明確でややフォーマルです。日常会話では「so」のほうが軽く聞こえることが多いです。", ("Clear or formal", "明確・ややフォーマル", "As a result, we had to reschedule.", "その結果、日程を変更しなければなりませんでした。"), ("Everyday conversation", "日常会話", "So we had to reschedule.", "それで、日程を変更しなければなりませんでした。")),
    ),
    101: semantic_spec(
        (("Use this when the answer changes according to one unresolved yes-or-no possibility.", "一つの未確定な「する／しない」によって答えが変わるときに使います。"), ("Use this before something that remains true in both possible outcomes.", "二つの可能な結果のどちらでも変わらないことの前に使います。")),
        (("Name one real unresolved condition, or give a definite answer.", "本当に未確定な条件を一つ言うか、はっきり答えましょう。"), ("Name one action true in both outcomes, or say the outcomes need different actions.", "どちらでも同じ行動を一つ言うか、結果ごとに行動が違うと伝えましょう。")),
        (choice_rows((("承認される{t}かどうかによります{/t}。", "It depends on ", "whether", "what", " they approve it."), ("会議室が空いている{t}かどうかによります{/t}。", "It depends on ", "whether", "what", " the room is free."), ("価格が変わる{t}かどうかによります{/t}。", "It depends on ", "whether", "what", " the price changes."), ("今日返事が来る{t}かどうかによります{/t}。", "It depends on ", "whether", "what", " we hear back today."))), choice_rows((("{t}どちらにしても{/t}、準備すべきです。", "", "Either way", "Both ways", ", we should prepare."), ("{t}どちらにしても{/t}、予備案が必要です。", "", "Either way", "Both ways", ", we need a backup plan."), ("{t}どちらにしても{/t}、期限は変わりません。", "", "Either way", "Both ways", ", the deadline stays the same."), ("{t}どちらにしても{/t}、更新を送ります。", "", "Either way", "Both ways", ", I'll send the update.")))),
        (("Name the unresolved branch", "未確定な分岐を示す", "It depends + <b>on whether</b> + 文", "Yes-or-no unknown", "するかどうかが未確定", ("It depends <b>on whether they approve it</b>.", "It depends <b>on whether the room is free</b>.")), ("Same in both branches", "どちらの分岐でも同じ", "<b>Either way,</b> + 変わらない行動・事実", "Both outcomes", "二つの結果", ("<b>Either way, we should prepare</b>.", "<b>Either way, the deadline stays the same</b>."))),
        ("Either way or in either case?", "Either way と in either case", "Both mean the same thing. “Either way” is more conversational; “in either case” is more formal.", "意味は同じです。「Either way」は会話的で、「in either case」はよりフォーマルです。", ("Conversation", "会話", "Either way, we should prepare.", "どちらにしても、準備すべきです。"), ("Formal explanation", "フォーマルな説明", "In either case, we should prepare.", "いずれの場合も、準備すべきです。")),
    ),
    102: semantic_spec(
        (("Use this to compress the failed condition and state its necessary consequence.", "満たされなかった条件を短くまとめ、必要になる結果を示すときに使います。"), ("Use this to offer a possible fallback after the first option fails.", "最初の方法が失敗したあとに、可能な代案を出すときに使います。")),
        (("State one real consequence if a condition fails, or say there is none.", "条件が失敗した場合の本当の結果を一つ言うか、結果はないと伝えましょう。"), ("Offer one realistic fallback, or say there is no fallback.", "現実的な代案を一つ出すか、代案はないと伝えましょう。")),
        (choice_rows((("そうでなければ、また最初から{t}始めなければなりません{/t}。", "Otherwise, we'd have to ", "start", "starting", " again."), ("そうでなければ、会議を{t}移さなければなりません{/t}。", "Otherwise, we'd have to ", "move", "moving", " the meeting."), ("そうでなければ、案を{t}変えなければなりません{/t}。", "Otherwise, we'd have to ", "change", "changing", " the plan."), ("そうでなければ、全額を{t}払わなければなりません{/t}。", "Otherwise, we'd have to ", "pay", "paying", " the full price."))), choice_rows((("それでうまくいかなければ、彼らに{t}聞くことができます{/t}。", "If that doesn't work, we could ", "ask", "asking", " them."), ("それでうまくいかなければ、取引先に{t}電話できます{/t}。", "If that doesn't work, we could ", "call", "calling", " the supplier."), ("それでうまくいかなければ、古い案を{t}使えます{/t}。", "If that doesn't work, we could ", "use", "using", " the old plan."), ("それでうまくいかなければ、別の日を{t}試せます{/t}。", "If that doesn't work, we could ", "try", "trying", " another date.")))),
        (("Compressed failed condition", "失敗した条件を圧縮", "<b>Otherwise,</b> + we'd have to + 動詞の原形", "Necessary consequence", "必要になる結果", ("<b>Otherwise, we'd have to start again</b>.", "<b>Otherwise, we'd have to move the meeting</b>.")), ("Possible fallback", "可能な代案", "If that doesn't work, + <b>we could + 動詞の原形</b>", "Plan after failure", "失敗後の案", ("If that doesn't work, <b>we could ask them</b>.", "If that doesn't work, <b>we could use the old plan</b>."))),
        ("Otherwise or or else?", "otherwise と or else", "Use “otherwise” for neutral planning. “Or else” can sound like a warning or threat.", "中立的な計画には「otherwise」を使います。「or else」は警告や脅しのように聞こえることがあります。", ("Neutral consequence", "中立的な結果", "Otherwise, we'd have to start again.", "そうでなければ、また最初から始めなければなりません。"), ("Warning", "警告", "Leave now, or else you'll miss it.", "今出ないと、間に合いませんよ。")),
    ),
}


VOCAB = {
    92: dict(new="entirely convinced|完全には納得していない; before deciding|決める前に", recycled="data|データ|CORE-85; deadline|期限|CORE-82; final price|最終価格|CORE-86; approval|承認|CORE-82; option|選択肢|CORE-45", assumed="plan|案; practical|現実的な; realistic|現実的な; evidence|根拠; numbers|数字; work|うまくいく; agree|同意する; approve|承認する; choose|選ぶ; full plan|案全体; want|望む; see|確認する; enough|十分な; thanks|ありがとう; look at|確認する; review|検討する", receptive="I have my doubts|疑問がある; on paper|理屈の上では; launch|開始する; figures|数値; breakdown|内訳"),
    93: dict(new="to be fair|公平に言えば; that said|とはいえ", recycled="supplier|取引先|CORE-82; draft|下書き|CORE-82; timing|時期|CORE-85; approval|承認|CORE-82; option|選択肢|CORE-45; work from home|在宅勤務をする|CORE-25", assumed="warn|警告する; call|電話する; send|送る; discuss|話し合う; date|日付; price|価格; cost|費用; unclear|不明な; plan|案; completely agree|全面的に賛成する; concede|認める; decide|決める; good|よい; need|必要である; point|点; settle|解決する; thanks|ありがとう", receptive="in fairness|公平に言えば; having said that|そうは言っても; go ahead|進める; expected more|もっと期待した"),
    94: dict(new="wouldn't it be better if|〜したほうがよくないか; what if|〜してみたらどうか", recycled="Friday|金曜日|CORE-28; small|小さい|CORE-43; meeting room|会議室|CORE-62; option|選択肢|CORE-45", assumed="wait|待つ; check|確認する; call|電話する; ask|聞く; other way|別のやり方; summary|要約; plan|案; first|先に; meeting|会議; report|レポート; room|会議室; small meeting room|小さい会議室; change|変更; current|現在の; full|完全な; great|よい; later|あとで; move|移す; send|送る; start|始める; suggest|提案する; thanks|ありがとう; think|思う; time|時間; try|試す; use|使う", receptive="just a thought|一つの案として; worth considering|検討する価値がある; client|顧客; figure|数値; preferred answer|望む答え"),
    95: dict(new="push back|異議を唱える; take into account|考慮に入れる", recycled="timing|時期|CORE-85; deadline|期限|CORE-82; budget|予算|CORE-53; point|要点|CORE-85; option|選択肢|CORE-45", assumed="cost|費用; delay|遅れ; final number|最終的な数字; extra work|追加作業; risk|リスク; proposal|提案; accept|受け入れる; plan|案; choose|選ぶ; complete|十分な; decision|判断; make a decision|判断する; good|よい; judge|判断する; thanks|ありがとう; think|思う; whole|全体の", receptive="I take your point|おっしゃることは分かる; let's park that|それはいったん保留にする; raise a concern|懸念を挙げる; basic plan|基本案; savings|節約額"),
    96: dict(new="I meant|〜という意味だった; trying to say|言おうとしていた", recycled="Friday|金曜日|CORE-28; draft|下書き|CORE-82; final version|最終版|CORE-83; meeting room|会議室|CORE-62; schedule|予定|CORE-67; small|小さい|CORE-43", assumed="morning|午前; afternoon|午後; main room|メイン会議室; small room|小さい会議室; date|日付; more time|もっと時間; wait|待つ; correct|訂正する; plan|案; change|変わる; need|必要である; next|次の; only|〜にすぎない; thank|ありがとう; thanks|ありがとう; think|思う", receptive="let me rephrase|言い換えさせてください; I put that badly|言い方が悪かった; urgent|緊急の; calendar|カレンダー; booking|予約; mark|記す"),
    97: dict(new="would rather not|〜しないほうを選ぶ; another time|別の機会", recycled="share|共有する|CORE-70; drive|運転する|CORE-14", assumed="join|参加する; decide|決める; meet|会う; discuss|話し合う; invitation|誘い; accept|受ける; topic|話題; plan|案; if that's OK|よければ; happy|喜んで; prepare|準備する; thanks|ありがとう; today|今日; work|うまくいく", receptive="I'll pass|今回は遠慮する; take a rain check|またの機会にする; no problem|大丈夫; next week|来週"),
    98: dict(new="mostly because of|主に〜が原因; comes from|〜から生じる; misunderstanding|誤解", recycled="approval|承認|CORE-82; issue|問題|CORE-82", assumed="delay|遅れ; information|情報; weather|天候; instructions|指示; system|仕組み; step|手順; source|出所; cause|原因; another|別の; clear|明確な; give|与える; good|よい; late|遅い; a lot of it|その多く; missing|欠けている; old|古い; prevent|防ぐ; reason|理由; sure|確かな; thanks|ありがとう; think|思う; unclear|不明確な", receptive="partly because of|一部〜が原因; the main reason|主な理由; formal alternative|フォーマルな別表現; clarify|明確にする"),
    99: dict(new="suggests that|〜を示している; would explain|〜の説明がつく", recycled="issue|問題|CORE-82; urgent|緊急の|CORE-83", assumed="drop|減少; people|人々; empty room|空の会議室; message|連絡; low response|少ない反応; question|質問; second call|二度目の電話; delay|遅れ; missing replies|返事がないこと; evidence|根拠; bring|連れてくる; good|よい; great|よい; notice|気づく; see|見る; stronger|より強い; thing|こと; today|今日; unclear|不明確な", receptive="it looks like|〜のようだ; on the face of it|一見したところ; website visits|ウェブサイト訪問数; logs|記録"),
    100: dict(new="as a result|その結果; that meant|そのため〜となった; reschedule|日程を変更する", recycled="deadline|期限|CORE-82; meeting room|会議室|CORE-62; schedule|予定|CORE-67", assumed="train|電車; canceled|運休した; file|ファイル; late|遅い; unavailable|使えない; price|価格; plan|案; meeting|会議; room|会議室; lose|失う; week|週; lose a week|1週間を失う; launch|開始; more work|追加作業; arrive|到着する; change|変える; good|よい; clear|はっきりした; happen|起きる; impact|影響; join|参加する; limit|抑える; miss|間に合わない; move|移す; people|人々; problem|問題; resolve|解決する; team|チーム; thanks|ありがとう; price went up|価格が上がった; workload|作業量; this week|今週", receptive="knock-on effect|連鎖的な影響; in turn|その結果; supplier|取引先; conversational link|会話的なつなぎ"),
    101: dict(new="depends on whether|〜かどうかによる; either way|どちらにしても", recycled="approval|承認|CORE-82; free|空いている|CORE-28; deadline|期限|CORE-82; hear back|返事をもらう|CORE-80; update|更新|CORE-37; schedule|予定|CORE-67", assumed="approve|承認する; room|会議室; price|価格; prepare|準備する; backup plan|予備案; same|同じ; unresolved|未確定の; plan|案; answer|答え; change|変わる; good|よい; great|よい; lose|失う; manageable|対応できる; need|必要である; outcome|結果; send|送る; stay|変わらない; time|時間; today|今日", receptive="up to them|彼ら次第; we'll cross that bridge|その時に考える; in either case|どちらの場合も; checklist|確認表"),
    102: dict(new="otherwise|そうでなければ", recycled="supplier|取引先|CORE-82; restart|再起動する|CORE-64; option|選択肢|CORE-45; free|空いている|CORE-28", assumed="start again|また最初から始める; move|移す; meeting|会議; move the meeting|会議を移す; change|変える; change the plan|案を変える; full price|全額; old plan|古い案; another date|別の日; fallback|代案; ask|聞く; call|電話する; work|うまくいく; plan|案; backup|代案; room|会議室; order|注文; you'd have to|あなたは〜しなければならない; great|よい; keep|続ける; need|必要である; pay|支払う; thanks|ありがとう; try|試す; use|使う; workable|実行できる", receptive="as a last resort|最後の手段として; plan B|代案; or else|さもないと; confirmation|確認"),
}

# Exact multiword scaffolds used in live menus. Keeping these as explicit
# productive assumptions prevents a menu from offering an ungrammatical bare
# noun where the blank needs a clause or an inflected verb phrase.
LIVE_SCAFFOLD_VOCAB = {
    92: "this plan is practical|この案は現実的だ; the deadline is realistic|その期限は現実的だ; we have enough evidence|根拠が十分ある; the numbers|その数字; the final price|その最終価格; the evidence|その根拠; the plan|その案; the option|その選択肢; the deadline|その期限",
    93: "it saves travel time|通勤時間を節約できる; some discussions are easier in person|対面のほうが話しやすい議論もある; not everyone has a quiet workspace|静かな仕事場がない人もいる; think|思う",
    94: "waited|待った; checked first|先に確認した; sent a summary|要約を送った; moved it to Friday|金曜日に移した",
    95: "",
    96: "we need more time|もっと時間が必要だ; the date may change|日付が変わるかもしれない; this is only a draft|これは下書きにすぎない; we should wait|待つべきだ; clear|明確な; work|都合がよい",
    97: "discuss it|それを話し合う; continue|続ける; decide now|今決める",
    98: "late approval|承認の遅れ; missing information|不足している情報; unclear instructions|分かりにくい指示; an old system|古い仕組み; a misunderstanding|誤解; one missing step|一つ抜けた手順; project|プロジェクト",
    99: "people missed the message|人々が連絡を見落とした; the message was unclear|連絡が不明確だった; the question was unclear|質問が不明確だった; the issue is urgent|問題が緊急だ; one number|一つの数字; alone|それだけで; need|必要である",
    100: "we missed the deadline|期限に間に合わなかった; we had more work|追加作業が増えた; the launch moved|開始日がずれた; spare day|予備の1日; delay|遅れ",
    101: "your managers approve the request|上司が申請を承認する; someone covers the meeting|誰かが会議を代わる; the project schedule changes|プロジェクトの予定が変わる; we hear back today|今日返事が来る; take a day off|休む; next week|来週; for sure|確実に",
    102: "check|確認する; confirm|確認する; smaller|小さい; try another date|別の日を試す",
}
for _number, _entries in LIVE_SCAFFOLD_VOCAB.items():
    if _entries:
        VOCAB[_number]["assumed"] += "; " + _entries


KNOWN_WORDS = {
    92: (("プラン", "plan"), ("データ", "data"), ("オプション", "option")),
    93: (("プラン", "plan"), ("サプライヤー", "supplier"), ("ドラフト", "draft")),
    94: (("プラン", "plan"), ("オプション", "option"), ("ミーティングルーム", "meeting room")),
    95: (("ポイント", "point"), ("タイミング", "timing"), ("リスク", "risk")),
    96: (("ドラフト", "draft"), ("プラン", "plan"), ("ミーティングルーム", "meeting room")),
    97: (("ドライブ", "drive"), ("シェア", "share"), ("プラン", "plan")),
    98: (("システム", "system"), ("ステップ", "step"), ("ソース", "source")),
    99: (("メッセージ", "message"), ("クエスチョン", "question"), ("イシュー", "issue")),
    100: (("ファイル", "file"), ("プラン", "plan"), ("ミーティングルーム", "meeting room")),
    101: (("アップデート", "update"), ("プラン", "plan"), ("ルーム", "room")),
    102: (("プラン", "plan"), ("オプション", "option"), ("サプライヤー", "supplier")),
}


TRANSLATE_HINTS = {
    92: (("うまくいく:work", "案:plan; 現実的な:practical", "期限:deadline; 現実的な:realistic", "根拠:evidence"), ("数字:numbers", "最終価格:final price; 同意する:agree", "根拠:evidence; 承認する:approve", "案全体:full plan; 選ぶ:choose")),
    93: (("警告する:warn", "取引先:supplier; 電話する:call", "下書き:draft; 送る:send", "費用:cost; 話し合う:discuss"), ("日付:date", "価格:price", "時期:timing; 不明な:unclear", "案:plan; 承認:approval")),
    94: (("待つ:wait", "確認する:check", "電話する:call", "先に:first; 聞く:ask"), ("別のやり方:other way", "要約:summary; 先に:first", "金曜日:Friday", "小さい:small; 会議室:room")),
    95: (("費用:cost", "時期:timing", "期限:deadline", "最終的な数字:final number"), ("遅れ:delay", "予算:budget", "追加作業:extra work", "リスク:risk")),
    96: (("金曜日:Friday", "午前:morning; 午後:afternoon", "小さい:small; メイン会議室:main room", "下書き:draft; 最終版:final version"), ("もっと時間:more time", "日付:date", "下書き:draft", "待つ:wait")),
    97: (("参加する:join", "運転する:drive", "決める:decide", "共有する:share"), ("別の機会:another time", "会う:meet", "話し合う:discuss", "決める:decide")),
    98: (("遅れ:delay", "承認:approval", "情報:information", "天候:weather"), ("誤解:misunderstanding", "指示:instructions", "仕組み:system", "手順:step")),
    99: (("減少:drop", "空の会議室:empty room; 連絡:message", "少ない反応:low response; 質問:question", "二度目の電話:second call; 問題:issue"), ("遅れ:delay", "少ない反応:low response", "空の会議室:empty room", "返事がないこと:missing replies")),
    100: (("電車:train; 運休した:canceled", "ファイル:file; 遅い:late", "会議室:room; 使えない:unavailable", "価格:price; 案:plan"), ("日程を変更する:reschedule; 失う:lose; 週:week", "期限:deadline; 開始:launch", "会議:meeting", "案:plan; 追加作業:more work")),
    101: (("承認する:approve", "会議室:room; 空いている:free", "価格:price", "返事をもらう:hear back"), ("準備する:prepare", "予備案:backup plan", "期限:deadline; 同じ:same", "更新:update")),
    102: (("また最初から始める:start again", "移す:move; 会議:meeting", "変える:change; 案:plan", "全額:full price"), ("聞く:ask", "取引先:supplier; 電話する:call", "古い案:old plan", "別の日:another date")),
}


OPEN_MENUS = {
    92: (("案:plan", "期限:deadline", "根拠:evidence", "現実的な:realistic"), ("数字:numbers", "最終価格:final price", "根拠:evidence", "案全体:full plan")),
    93: (("警告する:warn", "電話する:call", "送る:send", "話し合う:discuss"), ("日付:date", "価格:price", "時期:timing", "承認:approval")),
    94: (("待つ:wait", "確認する:check", "電話する:call", "聞く:ask"), ("別のやり方:other way", "要約:summary", "金曜日:Friday", "小さい会議室:small meeting room")),
    95: (("費用:cost", "時期:timing", "期限:deadline", "最終的な数字:final number"), ("遅れ:delay", "予算:budget", "追加作業:extra work", "リスク:risk")),
    96: (("金曜日:Friday", "午前:morning", "小さい会議室:small room", "下書き:draft"), ("もっと時間:more time", "日付:date", "下書き:draft", "待つ:wait")),
    97: (("参加する:join", "運転する:drive", "決める:decide", "共有する:share"), ("会う:meet", "話し合う:discuss", "決める:decide", "別の機会:another time")),
    98: (("遅れ:delay", "承認:approval", "情報:information", "天候:weather"), ("誤解:misunderstanding", "指示:instructions", "仕組み:system", "手順:step")),
    99: (("減少:drop", "空の会議室:empty room", "少ない反応:low response", "二度目の電話:second call"), ("遅れ:delay", "少ない反応:low response", "空の会議室:empty room", "返事がないこと:missing replies")),
    100: (("運休した:canceled", "期限:deadline", "会議室:meeting room", "案:plan"), ("失う:lose", "週:week", "追加作業:more work", "日程を変更する:reschedule")),
    101: (("承認:approval", "空いている:free", "価格:price", "返事をもらう:hear back"), ("準備する:prepare", "予備案:backup plan", "期限:deadline", "更新:update")),
    102: (("また最初から始める:start again", "移す:move", "変える:change", "全額:full price"), ("聞く:ask", "取引先:supplier", "古い案:old plan", "別の日:another date")),
}


SUPPORT_EXPRESSIONS = {
    92: (("I have my doubts.", "疑問が残ります。"), ("On paper, yes.", "理屈の上では、そうです。")),
    93: (("In fairness, they did tell us.", "公平に言えば、彼らは確かに伝えました。"), ("Having said that, we still need an answer.", "そうは言っても、まだ返事が必要です。")),
    94: (("Just a thought.", "一つの案としてですが。"), ("It's worth considering.", "検討する価値があります。")),
    95: (("I take your point.", "おっしゃることは分かります。"), ("Let's park that for now.", "それはいったん保留にしましょう。")),
    96: (("Let me rephrase.", "言い換えさせてください。"), ("I put that badly.", "言い方がよくありませんでした。")),
    97: (("I'll pass, thanks.", "今回は遠慮します。ありがとう。"), ("Can I take a rain check?", "また今度でもいいですか？")),
    98: (("It's partly because of the timing.", "一部は時期が原因です。"), ("The main reason is the delay.", "主な理由は遅れです。")),
    99: (("It looks like they missed it.", "見落としたようです。"), ("On the face of it, the plan worked.", "一見したところ、案はうまくいきました。")),
    100: (("There was a knock-on effect.", "連鎖的な影響がありました。"), ("That, in turn, delayed the launch.", "それがさらに、開始を遅らせました。")),
    101: (("It's up to them.", "彼ら次第です。"), ("We'll cross that bridge when we come to it.", "その時になったら考えましょう。")),
    102: (("As a last resort, we could call them.", "最後の手段として、電話できます。"), ("That's our plan B.", "それが私たちの代案です。")),
}


DIALOGUES = {
    92: dict(
        model=("Manager", 0, 0, ("The team wants to launch on Monday. Do you think the plan will work?", "チームは月曜日に開始したいそうです。この案はうまくいくと思いますか？"), ("What would help you decide?", "何があれば決められますか？"), ("I'll send the figures this afternoon.", "今日の午後、数値を送ります。"), ("Thanks. I'll look at them.", "ありがとう。確認します。")),
        wild=("Board member", 1, 1, ("The board wants this plan approved today. Is it practical?", "取締役会は今日この案を承認したいそうです。現実的ですか？"), ("What do you need before you can agree?", "同意する前に何が必要ですか？"), ("I'll send the final price and a full breakdown.", "最終価格と詳しい内訳を送ります。"), ("Thanks. I'll review it.", "ありがとう。確認します。")),
    ),
    93: dict(
        model=("Project lead", 0, 0, ("They warned us that the date might move. Can we proceed?", "日付がずれる可能性は警告されていました。進められますか？"), ("What is still missing?", "まだ何が足りませんか？"), ("I'll get a firm date from them today.", "今日、確定した日付を確認します。"), ("Thanks. Then we can decide.", "ありがとう。それなら決められます。")),
        wild=("Buyer", 1, 1, ("The supplier called to explain the change. Is everything settled?", "取引先から変更の説明の電話がありました。すべて解決しましたか？"), ("What do we still need from them?", "取引先からまだ何が必要ですか？"), ("I'll ask for the final price now.", "今、最終価格を確認します。"), ("Good. That will settle it.", "いいですね。それで解決します。")),
    ),
    94: dict(
        model=("Coworker", 0, 1, ("One figure is missing, but I want to send the report now.", "数値が一つ足りませんが、レポートを今送りたいです。"), ("The client needs something today. Do you have another option?", "顧客には今日何か送る必要があります。別案はありますか？"), ("That works. I'll send the summary and wait for the figure.", "それでいきましょう。要約を送り、数値を待ちます。"), ("Great. We can send the full report later.", "いいですね。完全なレポートはあとで送れます。")),
        wild=("Organizer", 1, 3, ("The large meeting room is not ready. The smaller room may be free, but we have not checked it. What should we do?", "大きい会議室は準備できていません。小さい会議室は空いているかもしれませんが、まだ確認していません。どうすればいいですか？"), ("If it is free, what alternative would keep the meeting on time?", "空いていれば、時間どおりに会議を始められる別案は何ですか？"), ("Good idea. I'll reserve the smaller room now.", "いい案です。今、小さい会議室を予約します。"), ("Thanks. Then the meeting can start on time.", "ありがとう。それなら会議を時間どおり始められます。")),
    ),
    95: dict(
        model=("Director", 0, 0, ("The basic plan costs less, so I think we should choose it.", "基本案のほうが安いので、これを選ぶべきだと思います。"), ("What is the cost comparison missing?", "費用の比較には何が抜けていますか？"), ("You're right. I'll compare the savings with the cost of the delay.", "そのとおりです。節約額と遅れによる費用を比較します。"), ("Thanks. Then we can judge the whole plan.", "ありがとう。それなら案全体を判断できます。")),
        wild=("Committee member", 1, 3, ("This event date gives us the largest audience. Shall we confirm it?", "このイベント日は最も多くの人が参加できます。確定しますか？"), ("What else should the committee include in its decision?", "委員会はほかに何を判断に含めるべきですか？"), ("I'll add the risk to the comparison before we vote.", "投票の前にリスクも比較に加えます。"), ("Good. Then the decision will be complete.", "いいですね。それなら十分な判断になります。")),
    ),
    96: dict(
        model=("Coordinator", 0, 0, ("So you want the file this Friday, correct?", "つまり、ファイルは今週の金曜日に必要なのですね？"), ("Then what was the main point of your message?", "では、メッセージの要点は何でしたか？"), ("Understood. I'll change the date in the calendar.", "分かりました。カレンダーの日付を変えます。"), ("Thanks. That is correct now.", "ありがとう。これで正しくなりました。")),
        wild=("Receptionist", 2, 2, ("I booked the main room and marked your file as final. Is that right?", "メイン会議室を予約し、ファイルを最終版としました。これで合っていますか？"), ("And what did you want me to understand about the file?", "それと、ファイルについて何を伝えたかったのですか？"), ("Got it. I'll move the booking to the small room and mark the file as a draft.", "分かりました。予約を小さい会議室に移し、ファイルを下書きと記します。"), ("Thank you. That is correct now.", "ありがとう。これで正しくなりました。")),
    ),
    97: dict(
        model=("Friend", 0, 0, ("Would you like to join us for dinner tonight?", "今夜、一緒に夕食に行きませんか？"), ("No problem. Would another day be better?", "大丈夫です。別の日のほうがいいですか？"), ("Sure. Let's choose a day next week.", "もちろん。来週の日を選びましょう。"), ("Thanks. That works for me.", "ありがとう。それなら大丈夫です。")),
        wild=("Team lead", 2, 2, ("Can we make the final decision at today's meeting?", "今日の会議で最終決定できますか？"), ("That's fine. What alternative do you suggest?", "分かりました。どんな別案がありますか？"), ("Yes. I'll add it to next week's agenda.", "はい。来週の議題に加えます。"), ("Thanks. I'll prepare before then.", "ありがとう。それまでに準備します。")),
    ),
    98: dict(
        model=("Manager", 1, 0, ("The project is late. What is the main cause?", "プロジェクトが遅れています。主な原因は何ですか？"), ("Where did the approval problem come from?", "承認の問題は何から生じましたか？"), ("I'll clarify the decision and send it to everyone.", "判断を明確にして全員に送ります。"), ("Good. That should prevent another misunderstanding.", "いいですね。次の誤解を防げるはずです。")),
        wild=("Station staff", 3, 2, ("Several trains are late today. Do you know why?", "今日は何本かの電車が遅れています。理由は分かりますか？"), ("And where does the repeated delay come from?", "繰り返す遅れは何から生じていますか？"), ("I'll tell passengers about the old system and the weather.", "古い仕組みと天候について乗客に伝えます。"), ("Thanks. That gives them a clear reason.", "ありがとう。それなら理由がはっきりします。")),
    ),
    99: dict(
        model=("Analyst", 0, 1, ("We posted the redesign announcement yesterday, but website visits dropped and few people opened it. What do you make of that?", "昨日デザイン変更のお知らせを出しましたが、ウェブサイト訪問数が減り、それを開いた人もほとんどいませんでした。どう考えますか？"), ("The response to our message was also low. Does that fit your conclusion?", "連絡への反応も少なかったです。その結論と合いますか？"), ("I'll check the logs to see whether the message was visible.", "連絡が見えていたか記録を確認します。"), ("Good. Then we'll have stronger evidence.", "いいですね。それなら根拠が強くなります。")),
        wild=("Event host", 1, 2, ("The meeting room is empty even though the event started ten minutes ago.", "イベント開始から10分たっていますが、会議室は空です。"), ("We also found that the reminder was never sent.", "リマインダーが送られていなかったことも分かりました。"), ("I'll send it now and direct people to this room.", "今送って、参加者をこの部屋へ案内します。"), ("Great. That should bring them here.", "いいですね。それなら参加者が来るはずです。")),
    ),
    100: dict(
        model=("Planner", 0, 0, ("Tell me what happened when the train was canceled.", "電車が運休したとき何が起きたか教えてください。"), ("What practical impact did the new schedule have?", "新しい日程には、どんな実際的な影響がありましたか？"), ("I'll adjust the remaining deadlines so we do not lose more time.", "これ以上時間を失わないよう、残りの期限を調整します。"), ("Thanks. That limits the impact.", "ありがとう。それで影響を抑えられます。")),
        wild=("Producer", 3, 3, ("The supplier raised the price. What happened after that?", "取引先が価格を上げました。そのあと何が起きましたか？"), ("What did the changed plan mean for the team?", "変更した案はチームにどんな影響を与えましたか？"), ("I'll reduce the scope so the team can manage the extra work.", "チームが追加作業に対応できるよう、範囲を縮めます。"), ("Good. That resolves the workload problem.", "いいですね。それで作業量の問題が解決します。")),
    ),
    101: dict(
        model=("Manager", 0, 0, ("Can the project start on Friday?", "プロジェクトは金曜日に始められますか？"), ("What can we do while we wait for their decision?", "判断を待つ間に何ができますか？"), ("Agreed. I'll start the preparation checklist today.", "賛成です。今日、準備の確認表に取りかかります。"), ("Great. Then we won't lose time.", "いいですね。それなら時間を失いません。")),
        wild=("Event coordinator", 1, 1, ("Can we hold the event in the main room?", "イベントをメイン会議室で開けますか？"), ("What should we do while the room is uncertain?", "会議室が未確定の間に何をすべきですか？"), ("I'll prepare a backup plan for the smaller room.", "小さい会議室用の予備案を準備します。"), ("Good. Then either outcome is manageable.", "いいですね。それならどちらの結果にも対応できます。")),
    ),
    102: dict(
        model=("Coordinator", 0, 0, ("The supplier needs our order file today. Our first plan is to restore the saved copy. If that fails, what happens?", "取引先には今日、注文ファイルが必要です。最初の案は保存したコピーを復元することです。それが失敗したら、どうなりますか？"), ("Could we try the backup copy before starting over?", "最初からやり直す前に、バックアップのコピーを試せますか？"), ("Good. I'll try the backup and then call the supplier if it fails.", "いいですね。バックアップを試し、失敗したら取引先に電話します。"), ("Thanks. That may keep the order moving.", "ありがとう。それなら注文を進められるかもしれません。")),
        wild=("Venue manager", 1, 3, ("We need a room for Tuesday's meeting. Our first plan is to get the main room confirmed by noon. If it is not confirmed, what happens?", "火曜日の会議には会議室が必要です。最初の案は、正午までにメイン会議室を確定することです。確定できなければ、どうなりますか？"), ("Could we try the room that is free on Friday before moving the meeting again?", "会議をもう一度動かす前に、金曜日に空いている会議室を試せますか？"), ("Friday is free. I'll hold it while we check the main room.", "金曜日は空いています。メイン会議室を確認する間、押さえておきます。"), ("Great. Then we have a workable backup date.", "いいですね。それなら実行できる予備の日があります。")),
    ),
}


LIVE_SCENES = {
    92: (("text", "other", "Tutor", "I think a four-day workweek would work for every team. What do you think?", "私は週4日勤務がどのチームにもうまくいくと思います。どう思いますか？"), ("input", "me", "Me", "I'm not entirely convinced that ___. I'd want to see ___ before deciding. / I'm convinced that it would work.", "___とは完全には納得していません。決める前に___を確認したいです。／うまくいくと納得しています。"), ("input", "me", "Me", "What would you want to see before deciding about ___?", "___について決める前に、先生なら何を確認したいか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real evidence:", "先生が実際に確認したい根拠")),
    93: (("text", "other", "Tutor", "I think working from home is always better. What do you think?", "私は在宅勤務のほうがいつでもよいと思います。どう思いますか？"), ("input", "me", "Me", "To be fair, it saves travel time. That said, ___. / I completely agree.", "公平に言えば、通勤時間を節約できます。とはいえ、___。／全面的に賛成です。"), ("input", "me", "Me", "What do you think about working from home?", "在宅勤務について先生がどう思うか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real concession and counterpoint:", "先生が実際に認める点と反対側の要点")),
    94: (("text", "other", "Tutor", "I think we should send an unfinished report today. What do you think?", "未完成のレポートを今日送るべきだと思います。どう思いますか？"), ("input", "me", "Me", "Wouldn't it be better if we ___? What if we ___? / I think the current plan is better.", "___したほうがよくないですか？___してみたらどうですか？／今の案のほうがよいと思います。"), ("input", "me", "Me", "What change would you suggest?", "先生ならどんな変更を提案するか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real suggestion:", "先生の実際の提案")),
    95: (("text", "other", "Tutor", "I think the most expensive option is the safest. Which part would you question?", "最も高い選択肢がいちばん安全だと思います。どの点に疑問がありますか？"), ("input", "me", "Me", "Where I'd push back is on ___. I don't think that takes ___ into account. / I accept the whole proposal.", "私が異議を唱えたいのは___です。それは___を考慮に入れていないと思います。／提案全体を受け入れます。"), ("input", "me", "Me", "What do you take into account when making a decision?", "判断するとき、先生なら何を考慮に入れるか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real factor:", "先生が実際に考慮する要素")),
    96: (("text", "other", "Tutor", "I understood that you meant this Friday. Is that right?", "今週の金曜日という意味だと理解しました。合っていますか？"), ("input", "me", "Me", "I meant next Friday, not this Friday. What I was trying to say is that ___. / Nothing needs correcting.", "今週の金曜日ではなく、来週の金曜日という意味でした。私が言おうとしていたのは___ということです。／訂正することはありません。"), ("input", "me", "Me", "Would next Friday work for you? / Would this Friday work for you?", "訂正したなら、来週の金曜日で先生に都合がよいか聞きましょう。訂正がなければ、今週の金曜日で都合がよいか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real availability for next Friday or this Friday:", "来週の金曜日、または今週の金曜日についての先生の実際の都合")),
    97: (("text", "other", "Tutor", "Would you like to discuss one more topic after this lesson?", "このレッスンのあと、もう一つ話題を話し合いませんか？"), ("input", "me", "Me", "I'd rather not ___, if that's OK. / Yes, I'd be happy to.", "よければ、___は遠慮したいです。／はい、ぜひ。"), ("input", "me", "Me", "Could we do it another time? / What topic shall we discuss?", "断るなら「また別の機会にできますか？」／受けるなら、どの話題を話すか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real response:", "先生の実際の返事")),
    98: (("text", "other", "Tutor", "Why do projects sometimes run late?", "プロジェクトが遅れることがあるのはなぜですか？"), ("input", "me", "Me", "That's mostly because of ___. A lot of it comes from ___. / I'm not sure what causes it.", "それは主に___が原因です。その多くは___から生じています。／原因はよく分かりません。"), ("input", "me", "Me", "What do you think project delays mostly come from?", "プロジェクトの遅れの多くは何から生じると思うか、先生に聞きましょう。"), ("input", "other", "Tutor", "Tutor's real cause:", "先生が考える実際の原因")),
    99: (("text", "other", "Tutor", "Only two people opened today's update. What might that low response suggest?", "今日の更新を開いたのは2人だけでした。この少ない反応は何を示しているでしょうか？"), ("input", "me", "Me", "The low response suggests that ___. That would explain the missing replies. / That one number alone doesn't suggest anything yet.", "反応の少なさは___ことを示しています。それなら返事がないことの説明がつきます。／その一つの数字だけでは、まだ何も示していません。"), ("input", "me", "Me", "What does that low response suggest to you? / Would you need more evidence?", "推測したなら、少ない反応が何を示すと思うか聞きましょう。まだ推測できないなら、さらに根拠が必要か聞きましょう。"), ("input", "other", "Tutor", "Tutor's real inference or evidence decision:", "先生の実際の推測、または根拠についての判断")),
    100: (("text", "other", "Tutor", "The supplier delivered our file one day late. Let's imagine what happened next. Did the delay force us to reschedule, or did a spare day mean nothing changed?", "取引先がファイルを1日遅れて届けたとします。そのあと何が起きたか想像しましょう。遅れで日程変更が必要になりましたか、それとも予備の1日があって何も変わりませんでしたか？"), ("input", "me", "Me", "The file arrived late. As a result, we rescheduled. That meant ___. / The file arrived late, but we had a spare day. As a result, the schedule didn't change.", "ファイルが遅れて届きました。その結果、日程を変更しました。そのため、___。／ファイルは遅れて届きましたが、予備の1日がありました。その結果、予定は変わりませんでした。"), ("input", "me", "Me", "Did a delay change your plans?", "遅れで先生の予定が変わったか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real cause and result:", "先生の実際の原因と結果")),
    101: (("text", "other", "Tutor", "Imagine your managers are reviewing your request for next Friday off. Could you take that day off, or would it depend on their approval?", "上司が来週の金曜日に休む申請を確認していると想像してください。その日に休めますか、それとも承認されるかどうかで変わりますか？"), ("input", "me", "Me", "It depends on whether ___. Either way, I'll send an update today. / Yes, I can. / No, I can't.", "___かどうかによります。どちらにしても、今日更新を送ります。／はい、できます。／いいえ、できません。"), ("input", "me", "Me", "What does your answer depend on? / Can you take a day off next week for sure?", "条件で変わるなら、先生の答えが何によって変わるか聞きましょう。はっきり答えられるなら、来週確実に休めるか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real condition or definite answer:", "先生の実際の条件、またははっきりした答え")),
    102: (("text", "other", "Tutor", "My plan is to hold Tuesday's meeting in the main room. First, I'll ask the supplier to confirm it today. If they can't, my next step is to try the smaller room, but I don't know yet if I can use it. What should I do next?", "火曜日の会議をメイン会議室で開く予定です。まず、今日取引先に確認を頼みます。取引先が確認できなければ、次に小さい会議室を試しますが、使えるかはまだ分かりません。次にどうすればいいですか？"), ("input", "me", "Me", "You should check the smaller room. Otherwise, you'd have to ___. If that doesn't work, you could ___. / If the smaller room is confirmed, you don't need another fallback.", "小さい会議室を確認したほうがいいです。そうでなければ___しなければなりません。それでうまくいかなければ、___できます。／小さい会議室が確保できているなら、別の代案は必要ありません。"), ("input", "me", "Me", "If the smaller room is not free, what will you do? / Is the smaller room confirmed?", "代案を出したなら、小さい会議室が空いていない場合にどうするか聞きましょう。代案が不要なら、小さい会議室が確保できているか聞きましょう。"), ("input", "other", "Tutor", "Tutor's real fallback or room confirmation:", "先生の実際の代案、または会議室が確保できているかについての答え")),
}


LIVE_HINTS = {
    92: {1: ("案が現実的だ:this plan is practical", "期限が現実的だ:the deadline is realistic", "根拠が十分ある:we have enough evidence", "数字:the numbers", "最終価格:the final price", "根拠:the evidence"), 2: ("その案:the plan", "その選択肢:the option", "その期限:the deadline")},
    93: {1: ("対面のほうが話しやすい議論もある:some discussions are easier in person", "静かな仕事場がない人もいる:not everyone has a quiet workspace")},
    94: {1: ("待つ:waited", "先に確認する:checked first", "要約を送る:sent a summary", "金曜日に移す:moved it to Friday"), 2: ("変更:change",)},
    95: {1: ("費用:cost", "時期:timing", "予算:budget", "リスク:risk"), 2: ("判断する:make a decision",)},
    96: {1: ("もっと時間が必要だ:we need more time", "日付が変わるかもしれない:the date may change", "これは下書きにすぎない:this is only a draft", "待つべきだ:we should wait")},
    97: {1: ("それを話し合う:discuss it", "続ける:continue", "今決める:decide now"), 2: ("話題:topic", "別の機会:another time")},
    98: {1: ("承認の遅れ:late approval", "不足している情報:missing information", "分かりにくい指示:unclear instructions", "古い仕組み:an old system", "誤解:a misunderstanding", "一つ抜けた手順:one missing step")},
    99: {1: ("人々が連絡を見落とした:people missed the message", "連絡が不明確だった:the message was unclear", "質問が不明確だった:the question was unclear", "問題が緊急だ:the issue is urgent")},
    100: {1: ("期限に間に合わなかった:we missed the deadline", "追加作業が増えた:we had more work", "開始日がずれた:the launch moved")},
    101: {1: ("上司が申請を承認する:your managers approve the request", "誰かが会議を代わる:someone covers the meeting", "プロジェクトの予定が変わる:the project schedule changes", "今日返事が来る:we hear back today")},
    102: {1: ("会議を移す:move the meeting", "別の日を試す:try another date")},
}


# Human-reviewed operating copy for the page-by-page audit. Open production
# names both the exact frame and the communicative job. A choice page survives
# only when its rows require a real form decision; fixed-answer pseudo-choices
# are omitted. Free Talk is a genuine reciprocal topic exchange, with today's
# pattern available but never forced into an unnatural answer.
WRITE_PROMPTS = {
    92: (("Now use “I'm not entirely convinced that ___” to express one real doubt softly.", "では、「I'm not entirely convinced that ___」を使って、本当の疑問を一つやわらかく伝えてください。"), ("Now use “I'd want to see ___ before ___ing” to name evidence you need before a decision.", "では、「I'd want to see ___ before ___ing」を使って、決める前に必要な根拠を示してください。")),
    93: (("Now use “To be fair, ___” to concede one true point.", "では、「To be fair, ___」を使って、本当に認められる点を一つ伝えてください。"), ("Now use “That said, ___” to state what still needs attention.", "では、「That said, ___」を使って、まだ注意が必要な点を一つ伝えてください。")),
    94: (("Now use “Wouldn't it be better if we ___?” to suggest one useful change.", "では、「Wouldn't it be better if we ___?」を使って、役立つ変更を一つ提案してください。"), ("Now use “What if we ___?” to offer one different approach.", "では、「What if we ___?」を使って、別のやり方を一つ提案してください。")),
    95: (("Now use “Where I'd push back is on ___” to identify one part of a proposal you question.", "では、「Where I'd push back is on ___」を使って、提案の中で疑問に思う点を一つ示してください。"), ("Now use “I don't think that takes ___ into account” to name one overlooked factor.", "では、「I don't think that takes ___ into account」を使って、見落とされた要素を一つ示してください。")),
    96: (("Now use “I meant ___, not ___” to correct one misunderstood detail.", "では、「I meant ___, not ___」を使って、誤解された情報を一つ訂正してください。"), ("Now use “What I was trying to say is that ___” to restate your intended message.", "では、「What I was trying to say is that ___」を使って、本来伝えたかったことを言い直してください。")),
    97: (("Now use “I'd rather not ___, if that's OK” to decline one invitation politely.", "では、「I'd rather not ___, if that's OK」を使って、誘いを一つ丁寧に断ってください。"), ("Now use “Could we ___ another time?” to suggest a different time.", "では、「Could we ___ another time?」を使って、別の機会を提案してください。")),
    98: (("Now use “That's mostly because of ___” to name one main cause without ruling out others.", "では、「That's mostly because of ___」を使って、ほかの可能性を残しながら主な原因を一つ示してください。"), ("Now use “A lot of it comes from ___” to name one source of a problem.", "では、「A lot of it comes from ___」を使って、問題の出所を一つ示してください。")),
    99: (("Now use “___ suggests that ___” to draw one cautious conclusion from an observation.", "では、「___ suggests that ___」を使って、観察から控えめな結論を一つ導いてください。"), ("Now use “That would explain ___” to connect a fact to what it could explain.", "では、「That would explain ___」を使って、事実と、それで説明できることをつないでください。")),
    100: (("Now use “As a result, ___” to connect one cause to its direct result.", "では、「As a result, ___」を使って、原因を直接の結果につないでください。"), ("Now use “That meant ___” to state one practical consequence.", "では、「That meant ___」を使って、実際に生じた影響を一つ伝えてください。")),
    101: (("Now use “It depends on whether ___” to answer one real question conditionally.", "では、「It depends on whether ___」を使って、本当の質問に条件付きで答えてください。"), ("Now use “Either way, ___” to say what remains true in both outcomes.", "では、「Either way, ___」を使って、どちらの結果でも変わらないことを伝えてください。")),
    102: (("Now use “Otherwise, we'd have to ___” to state the consequence of a failed condition.", "では、「Otherwise, we'd have to ___」を使って、条件が満たされない場合の結果を伝えてください。"), ("Now use “If that doesn't work, we could ___” to offer one realistic fallback.", "では、「If that doesn't work, we could ___」を使って、現実的な代案を一つ出してください。")),
}

CHOICE_OMISSIONS = {
    92: {1}, 93: {2}, 94: set(), 95: {1, 2}, 96: {2}, 97: set(),
    98: {1, 2}, 99: {1, 2}, 100: {1, 2}, 101: {1, 2}, 102: set(),
}

REVIEWED_LIVE = {
    92: ("What's an opinion you changed your mind about, and what convinced you?", "考えが変わった意見は何ですか？何がきっかけでしたか？", "What changed your mind about an opinion?", "先生は何がきっかけで意見が変わりましたか？"),
    93: ("What's one good thing about working from home, and one downside?", "在宅勤務のよい点と大変な点を一つずつ教えてください。", "What's one good thing and one downside for you?", "先生にとってのよい点と大変な点は何ですか？"),
    94: ("When a plan goes wrong, do you fix it quickly or rethink it first? Why?", "計画がうまくいかないとき、すぐ直しますか？それともまず考え直しますか？なぜですか？", "Do you fix a plan quickly or rethink it first?", "先生はすぐ直しますか？それともまず考え直しますか？"),
    95: ("When you question a plan, what do you check first: cost, timing, or risk?", "計画に疑問があるとき、費用、時期、リスクのどれを最初に確認しますか？", "What do you check first in a plan?", "先生は計画の何を最初に確認しますか？"),
    96: ("Have you ever mixed up a date or time? What happened?", "日付や時間を取り違えたことはありますか？何がありましたか？", "Have you ever mixed up a date or time?", "先生は日付や時間を取り違えたことがありますか？"),
    97: ("What kind of invitation do you sometimes prefer to turn down, and why?", "どんな誘いを断りたいことがありますか？なぜですか？", "What kind of invitation do you sometimes turn down?", "先生はどんな誘いを断ることがありますか？"),
    98: ("Why do projects or plans often run late, in your experience?", "経験上、プロジェクトや計画が遅れる主な理由は何ですか？", "Why do plans often run late in your experience?", "先生の経験では、計画はなぜ遅れることが多いですか？"),
    99: ("What's one clue that tells you a meeting or event was poorly communicated?", "会議やイベントの連絡がうまく伝わっていないと分かる手がかりは何ですか？", "What clue suggests poor communication to you?", "先生はどんな手がかりで連絡不足だと考えますか？"),
    100: ("What's a small delay that caused a surprisingly big result for you?", "小さな遅れが思いがけず大きな結果につながった経験はありますか？", "What small delay had a big result for you?", "先生はどんな小さな遅れが大きな結果につながりましたか？"),
    101: ("When you make weekend plans, what does your decision usually depend on?", "週末の予定を決めるとき、何によって決まることが多いですか？", "What do your weekend plans usually depend on?", "先生の週末の予定は、何によって決まることが多いですか？"),
    102: ("When your first plan fails, what backup do you usually try?", "最初の案がうまくいかないとき、どんな代案を試しますか？", "What backup do you usually try?", "先生はふだんどんな代案を試しますか？"),
}

MODEL_ROLE_JA = {
    92: "マネージャー", 93: "プロジェクトリーダー", 94: "同僚",
    95: "責任者", 96: "調整担当者", 97: "友人", 98: "マネージャー",
    99: "分析担当者", 100: "計画担当者", 101: "マネージャー",
    102: "調整担当者",
}

WILD_ROLE_JA = {
    92: "取締役会のメンバー", 93: "購買担当者", 94: "主催者",
    95: "委員", 96: "受付係", 97: "チームリーダー", 98: "駅員",
    99: "イベント主催者", 100: "制作担当者", 101: "イベント調整担当者",
    102: "会場責任者",
}

for _number in NUMBERS:
    SPECS[_number]["writes"] = WRITE_PROMPTS[_number]
    LESSONS[_number]["omit_choice"] = tuple(sorted(CHOICE_OMISSIONS[_number]))
    SPECS[_number]["role_ja"] = MODEL_ROLE_JA[_number]
    _wild_role = DIALOGUES[_number]["wild"][0].lower()
    SPECS[_number]["wild_script"] = (
        f"I'll be the {_wild_role}. Say each complete line, including the missing words.",
        f"私は{WILD_ROLE_JA[_number]}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。",
    )
    LESSONS[_number]["prompt"] = (
        "Let's talk about this topic. Answer my question, then ask me too.",
        "この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。",
    )
    _question, _question_ja, _ask_back, _ask_back_ja = REVIEWED_LIVE[_number]
    LIVE_SCENES[_number] = (
        ("text", "other", "Tutor", _question, _question_ja),
        ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
        ("text", "me", "Me", _ask_back, _ask_back_ja),
        ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
    )
    LIVE_HINTS[_number] = {}


TRANSFER_SCENES = {
    92: "board proposal evidence review", 93: "supplier price concession",
    94: "meeting room alternative", 95: "event date risk review",
    96: "room booking correction", 97: "team decision deferral",
    98: "station delay explanation", 99: "empty event room inference",
    100: "supplier price consequence", 101: "event room contingency",
    102: "venue date fallback",
}

BRIEF_PRODUCTION_MODELS = {
    number: (core.strip_marks(LESSONS[number]["p1"][0][0]).split(". ")[-1],
             core.strip_marks(LESSONS[number]["p2"][0][0]).split(". ")[-1])
    for number in NUMBERS
}

THREE_CHIP_EXCEPTIONS = {
    (92, 1): "The hedge and its that-clause form three honest discourse units.",
    (94, 1): "The suggestion frame and complete if-clause form three honest units.",
    (96, 2): "The restatement frame, clause linker, and complete clause form three honest units.",
    (97, 1): "The refusal frame, action, and softener form three honest units.",
    (97, 2): "The modal question, activity, and intact time phrase form three units.",
    (98, 2): "The quantity subject, source frame, and noun phrase form three units.",
    (99, 2): "The referent, modal predicate, and explanation object form three units.",
    (101, 2): "The discourse linker, subject, and complete modal predicate form three units.",
    (102, 1): "The connector, complete modal predicate, and complement form three units.",
    (102, 2): "The failed-condition clause, complete modal predicate, and object form three units.",
}

SPIRAL_MARKERS = {
    94: (("NEGQ-01", "contrast"),),
    95: (("PREP-01", "transfer"),),
    96: (("REPORT-01", "transfer"), ("ORDER-01", "transfer")),
    97: (("POLITE-01", "checkpoint"), ("MODAL-01", "transfer")),
    98: (("PREP-01", "contrast"),),
    102: (("MODAL-01", "checkpoint"),),
}

SPIRAL_CHOICES = {
    (94, "NEGQ-01"): (
        ("実際には警告しなかった。「警告しなかったの？」", "", "No, they didn't", "Yes, they did", "."),
        ("実際には警告した。「警告しなかったの？」", "", "Yes, they did", "No, they didn't", "."),
        ("「待ったほうがよくない？」への返事", "", "That sounds better", "No, we didn't", "."),
        ("「先に確認したほうがよくない？」への返事", "", "Good idea", "Yes, we did", "."),
    ),
    (95, "PREP-01"): (
        ("費用について異議を唱える。", "I'd push back ", "on", "at", " the cost."),
        ("遅れを考慮に入れる。", "Take the delay ", "into", "onto", " account."),
        ("案について話し合う。", "Let's talk ", "about", "at", " the plan."),
        ("取引先から返事をもらう。", "We heard back ", "from", "to", " the supplier."),
    ),
    (96, "REPORT-01"): (
        ("彼女は日付を言った。", "She ", "said", "told", " the date might change."),
        ("彼女は私に日付を伝えた。", "She ", "told", "said", " me the date."),
        ("彼は待つよう私に頼んだ。", "He ", "asked me to", "said me to", " wait."),
        ("彼はもっと時間が必要だと言った。", "He ", "said", "told", " he needed more time."),
    ),
    (96, "ORDER-01"): (
        ("何を言ったのか教えてください。", "Tell me what ", "you said", "did you say", "."),
        ("日付がいつ変わったのか分かりますか？", "Do you know when ", "the date", "did the date", " changed?"),
        ("彼らが何を承認したのか教えてください。", "Tell me what ", "they", "did they", " approved."),
        ("なぜ遅れたのか分かりますか？", "Do you know why ", "it", "was it", " was late?"),
    ),
    (97, "POLITE-01"): (
        ("丁寧に断る。", "", "I'd rather not", "I don't", " join, if that's OK."),
        ("丁寧に別案を聞く。", "", "Could we", "We could", " meet another time?"),
        ("丁寧にお願いする。", "", "Could you", "You could", " send it?"),
        ("丁寧に保留する。", "", "Can I", "I can", " confirm tomorrow?"),
    ),
    (97, "MODAL-01"): (
        ("could のあと。", "Could we ", "meet", "meeting", " tomorrow?"),
        ("would rather のあと。", "I'd rather ", "wait", "waiting", "."),
        ("can のあと。", "I can ", "join", "joining", " Friday."),
        ("should のあと。", "We should ", "decide", "deciding", " later."),
    ),
    (98, "PREP-01"): (
        ("遅れが原因。", "It's because ", "of", "from", " the delay."),
        ("誤解から生じる。", "It comes ", "from", "of", " a misunderstanding."),
        ("案について話す。", "Let's talk ", "about", "at", " the plan."),
        ("取引先から届く。", "It came ", "from", "to", " the supplier."),
    ),
    (102, "MODAL-01"): (
        ("would have to のあと。", "We'd have to ", "start", "starting", " again."),
        ("could のあと。", "We could ", "ask", "asking", " them."),
        ("should のあと。", "We should ", "prepare", "preparing", " now."),
        ("might のあと。", "They might ", "call", "calling", " later."),
    ),
}

DIALOGUE_SEMANTIC_LEDGER = {
    92: dict(model=("manager gives launch proposal", "learner signals doubt", "manager asks decision need", "learner requests evidence", "manager promises figures", "learner accepts review"), wild=("board requests approval", "learner doubts practicality", "board asks evidence need", "learner requests final price", "board promises breakdown", "learner accepts review")),
    93: dict(model=("lead cites prior warning", "learner concedes warning", "lead asks missing item", "learner counters with date", "lead promises date", "learner accepts decision path"), wild=("buyer cites supplier call", "learner concedes call", "buyer asks remaining need", "learner counters with price", "buyer requests price", "learner confirms resolution")),
    94: dict(model=("coworker proposes incomplete report", "learner suggests waiting", "coworker states today constraint", "learner offers summary", "coworker accepts sequence", "learner confirms later full report"), wild=("organizer states room problem", "learner suggests checking", "organizer asks timely alternative", "learner offers smaller room", "organizer reserves room", "learner confirms on-time outcome")),
    95: dict(model=("director proposes basic plan", "learner isolates cost", "director asks missing comparison factor", "learner names delay", "director promises comparison", "learner accepts complete review"), wild=("committee proposes event date", "learner isolates timing", "committee asks missing factor", "learner names risk", "committee adds risk", "learner accepts complete decision")),
    96: dict(model=("coordinator states Friday interpretation", "learner corrects Friday", "coordinator asks intended message", "learner restates need", "coordinator updates calendar", "learner confirms repair"), wild=("receptionist states room and file interpretation", "learner corrects room", "receptionist asks intended file message", "learner explains draft", "receptionist fixes room and file", "learner confirms repair")),
    97: dict(model=("friend invites learner", "learner declines", "friend offers another day", "learner requests another time", "friend proposes next week", "learner accepts"), wild=("lead requests decision today", "learner declines today", "lead asks alternative", "learner requests later discussion", "lead moves agenda", "learner commits preparation")),
    98: dict(model=("manager asks late-project cause", "learner names approval", "manager asks source", "learner names misunderstanding", "manager clarifies decision", "learner predicts prevention"), wild=("staff asks train delay cause", "learner names weather", "staff asks repeated source", "learner names old system", "staff explains to passengers", "learner confirms clarity")),
    99: dict(model=("analyst states visit drop", "learner infers visibility issue", "analyst adds low response", "learner explains response", "analyst checks logs", "learner seeks stronger evidence"), wild=("host states empty room", "learner infers missed message", "host reveals unsent reminder", "learner explains empty room", "host sends reminder", "learner predicts arrival")),
    100: dict(model=("planner asks canceled-train outcome", "learner links cancellation to reschedule", "planner asks practical impact", "learner links reschedule to lost week", "planner adjusts deadlines", "learner confirms limited impact"), wild=("producer asks price outcome", "learner links price to plan change", "producer asks team impact", "learner links change to work", "producer reduces scope", "learner confirms workload repair")),
    101: dict(model=("manager asks Friday feasibility", "learner names approval condition", "manager asks current action", "learner names preparation", "manager begins checklist", "learner confirms time saved"), wild=("coordinator asks room feasibility", "learner names room condition", "coordinator asks current action", "learner names backup", "coordinator prepares smaller room", "learner confirms both outcomes")),
    102: dict(model=("coordinator states saved-copy plan", "learner states restart consequence", "coordinator proposes backup copy", "learner proposes asking supplier", "coordinator commits to backup then supplier call", "learner confirms order may keep moving"), wild=("manager states room deadline", "learner states meeting consequence", "manager asks alternate date", "learner proposes another date", "manager holds Friday", "learner confirms backup")),
}

# Human-authored inventory of content language the learner reads, completes, or
# may select in an open menu. The test requires every term to have one explicit
# four-way vocabulary owner instead of trusting incidental string coverage.
PRODUCTIVE_TERMS = {
    92: ("entirely convinced", "before deciding", "plan", "deadline", "evidence", "numbers", "final price", "agree", "choose"),
    93: ("to be fair", "that said", "warn", "supplier", "draft", "discuss", "date", "price", "timing", "approval"),
    94: ("wouldn't it be better if", "what if", "wait", "check", "call", "ask", "other way", "summary", "Friday", "meeting room"),
    95: ("push back", "take into account", "cost", "timing", "deadline", "final number", "delay", "budget", "extra work", "risk"),
    96: ("I meant", "trying to say", "Friday", "morning", "afternoon", "meeting room", "draft", "final version", "more time", "date", "wait"),
    97: ("would rather not", "another time", "join", "drive", "decide", "share", "meet", "discuss"),
    98: ("mostly because of", "comes from", "misunderstanding", "delay", "approval", "information", "weather", "instructions", "system", "step"),
    99: ("suggests that", "would explain", "drop", "empty room", "message", "low response", "question", "second call", "issue", "delay", "missing replies"),
    100: ("as a result", "that meant", "reschedule", "train", "canceled", "file", "late", "meeting room", "price", "plan", "deadline", "lose a week", "launch", "more work"),
    101: ("depends on whether", "either way", "approval", "free", "price", "hear back", "prepare", "backup plan", "deadline", "update"),
    102: ("otherwise", "start again", "move the meeting", "change the plan", "full price", "ask", "supplier", "old plan", "another date"),
}


@contextlib.contextmanager
def course_data():
    names = (
        "LESSONS", "SPECS", "VOCAB", "KNOWN_WORDS", "TRANSLATE_HINTS",
        "OPEN_MENUS", "DIALOGUES", "LIVE_SCENES", "LIVE_HINTS",
        "SUPPORT_EXPRESSIONS",
    )
    previous = {name: getattr(approved, name) for name in names}
    role_ja_previous = approved.ROLE_JA.copy()
    core_previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    try:
        for name in names:
            setattr(approved, name, globals()[name])
        for number in NUMBERS:
            approved.ROLE_JA[DIALOGUES[number]["model"][0]] = MODEL_ROLE_JA[number]
            approved.ROLE_JA[DIALOGUES[number]["wild"][0]] = WILD_ROLE_JA[number]
        core.VOCAB = {
            number: (values["new"], values["assumed"], values["receptive"])
            for number, values in VOCAB.items()
        }
        core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = SPECS, DIALOGUES, LIVE_SCENES
        yield
    finally:
        for name, value in previous.items():
            setattr(approved, name, value)
        approved.ROLE_JA.clear()
        approved.ROLE_JA.update(role_ja_previous)
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = core_previous


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{value}\2', head, count=1,
        )
    return head


def spiral_page(number, spiral_id, mode):
    page = core.choose_words(
        f"spiral-{spiral_id.casefold()}", "Retrieve an earlier contrast", "前の対比を思い出そう",
        "Choose the smallest form that keeps the earlier rule accurate.",
        "前のルールが正しくなる最小の形を選びましょう。",
        SPIRAL_CHOICES[(number, spiral_id)],
    )
    return page.replace(
        f'data-page-id="spiral-{spiral_id.casefold()}"',
        f'data-page-id="spiral-{spiral_id.casefold()}" data-spiral-id="{spiral_id}" data-spiral-level="{mode}"',
        1,
    )


def growing_sentence_inputs(page):
    """Use wrapping static value controls for full-sentence answers."""
    return re.sub(
        r'<input class="space-input" type="text"([^>]*)>',
        r'<textarea class="space-input free-input"\1 rows="2"></textarea>',
        page,
    )


def concise_roleplay_copy(page):
    """Keep transition and role instructions short, explicit, and bilingual."""
    pid = page_id(page)
    if pid == "part3-intro":
        page = re.sub(
            r'<p class="section-subtitle">.*?</p><div class="tutor-note">.*?</div>',
            '<p class="section-subtitle"><span class="ko">Next, let\'s role-play a conversation.</span>'
            '<span class="ja">次は、会話をロールプレイしましょう。</span></p>'
            '<div class="tutor-note">Move on to the role-play.</div>',
            page,
            count=1,
        )
    if pid == "p3-model":
        page = page.replace("Please read the Me lines aloud.", "Read your lines aloud.")
        page = page.replace("Please read your lines aloud.", "Read your lines aloud.")
        page = page.replace("役をします。Me のセリフを声に出して読んでください。", "です。自分のセリフを声に出して読んでください。")
    if pid == "p3-complete":
        page = page.replace("役をします。空欄に入る言葉も含めて", "です。空欄に入る言葉も含めて")
    return page


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def customize_pages(number, data, pages):
    pages = approved.customize_pages(number, data, pages)
    result = []
    for page in pages:
        page = concise_roleplay_copy(growing_sentence_inputs(page))
        if page_id(page) == "part3-intro":
            result.extend(
                spiral_page(number, spiral_id, mode)
                for spiral_id, mode in SPIRAL_MARKERS.get(number, ())
            )
        result.append(page)
    return result


def build(number, data):
    if number not in NUMBERS:
        raise ValueError(f"CORE-{number} is not owned by this generator")
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    head = new_lesson.retarget(
        head, review_id=f"CORE-{number}", lesson_id=slug, level="B2",
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"],
        version="2026-08-20",
    )
    head = head.replace("</head>", '  <link rel="stylesheet" href="growing-inputs.css">\n</head>', 1)
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
        ("productive terms", PRODUCTIVE_TERMS),
        ("live scaffold vocabulary", LIVE_SCAFFOLD_VOCAB),
        ("write prompts", WRITE_PROMPTS),
        ("choice omissions", CHOICE_OMISSIONS),
        ("reviewed live prompts", REVIEWED_LIVE),
        ("model role Japanese", MODEL_ROLE_JA),
        ("wild role Japanese", WILD_ROLE_JA),
    ):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-92--102")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    validate_source()
    for number, data in LESSONS.items():
        out, text = build(number, data)
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        out.with_name("growing-inputs.css").write_text(NARROW_GROWING_INPUT_CSS, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS)} Core decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
