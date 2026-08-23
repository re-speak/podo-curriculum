#!/usr/bin/env python3
"""Generate the explicit CORE-113--122 Advanced Stance course batch.

Every semantic and pedagogical decision lives in this file.  The shared Core
renderer supplies only the already-approved component markup.
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
COURSE = "core-advanced-stance"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
NUMBERS = tuple(range(113, 123))

# Whole-sentence answers must remain fully visible at 360px.  Keep the control
# static in source HTML and let it wrap/grow; JavaScript must not manufacture it.
NARROW_GROWING_INPUT_CSS = """/* CORE113--122: visible multi-line answers at phone widths. */
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
.slot-hints {
  display: grid;
  gap: 7px;
  margin-top: 8px;
  min-width: 0;
}
.slot-hint-group {
  min-width: 0;
}
.slot-hint-label {
  display: block;
  color: var(--gray-700);
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 3px;
  overflow-wrap: anywhere;
}
.slot-hint-label .task {
  display: block;
  color: var(--gray-600);
  font-weight: 500;
}
.word-choice-sentence,
.choose-row.word-choice,
.choose-row.word-choice .opt {
  min-width: 0;
  max-width: 100%;
  white-space: normal;
  overflow-wrap: anywhere;
}
.choose-row.word-choice {
  display: inline-flex;
  flex-wrap: wrap;
}
"""


def rows(*items):
    return items


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


def choices(*items):
    return items


LESSONS = {
    113: dict(
        slug="the-underlying-issue-is", title="The underlying issue is",
        ko="근본적인 문제는", ja="根本的な問題は",
        goal=("Move from one recurring complaint to the broader pattern behind it.", "繰り返す問題から、その背後にあるより大きな構造へ話を進めましょう。"),
        p1=rows(
            ("{t}The underlying issue is{/t} how we scope things.", "{t}根本的な問題は{/t}、仕事の範囲の決め方です。", "The underlying issue|is|how we|scope things."),
            ("{t}The underlying issue is{/t} unclear ownership.", "{t}根本的な問題は{/t}、担当が不明確なことです。", "The underlying issue|is|unclear|ownership."),
            ("{t}The underlying issue is{/t} how decisions get made.", "{t}根本的な問題は{/t}、意思決定の仕方です。", "The underlying issue|is|how decisions|get made."),
            ("{t}The underlying issue is{/t} conflicting priorities.", "{t}根本的な問題は{/t}、優先事項がぶつかっていることです。", "The underlying issue|is|conflicting|priorities."),
        ),
        p2=rows(
            ("{t}It's symptomatic of{/t} a bigger problem.", "それは、{t}より大きな問題の表れです{/t}。", "It's|symptomatic of|a bigger problem."),
            ("{t}It's symptomatic of{/t} poor communication.", "それは、{t}意思疎通の不足の表れです{/t}。", "It's|symptomatic of|poor communication."),
            ("{t}It's symptomatic of{/t} unclear priorities.", "それは、{t}優先事項が不明確なことの表れです{/t}。", "It's|symptomatic of|unclear priorities."),
            ("{t}It's symptomatic of{/t} weak planning.", "それは、{t}計画不足の表れです{/t}。", "It's|symptomatic of|weak planning."),
        ),
        rules=(("After The underlying issue is, use a noun phrase or a how, what, or why clause.", "「The underlying issue is」 のあとには、名詞句か how・what・why で始まる節を置きます。"),
               ("Use symptomatic of before the broader problem revealed by one visible sign.", "目に見える一つの兆候が示す、より大きな問題の前に 「symptomatic of」 を使います。")),
        prompt=("Name a recurring problem you really know, or say none comes to mind.", "実際に知っている繰り返す問題を挙げるか、思いつかないと伝えましょう。"),
    ),
    114: dict(
        slug="that-may-be-true-for-some-people", title="That may be true for some people",
        ko="어떤 사람들에게는 그럴 수 있어요", ja="一部の人には当てはまるかもしれません",
        goal=("Accept a claim only within the limits where it actually holds.", "主張が本当に当てはまる範囲だけを認めましょう。"),
        p1=rows(
            ("{t}That may be true for{/t} large teams, {t}but not for{/t} small ones.", "大きなチームには{t}当てはまるかもしれませんが{/t}、小さなチームには{t}当てはまりません{/t}。", "That may be true|for large teams,|but not|for small ones."),
            ("{t}That may be true for{/t} new users, {t}but not for{/t} experienced ones.", "新しい利用者には{t}当てはまるかもしれませんが{/t}、経験のある利用者には{t}当てはまりません{/t}。", "That may be true|for new users,|but not|for experienced ones."),
            ("{t}That may be true for{/t} city offices, {t}but not for{/t} rural ones.", "都市のオフィスには{t}当てはまるかもしれませんが{/t}、地方のオフィスには{t}当てはまりません{/t}。", "That may be true|for city offices,|but not|for rural ones."),
            ("{t}That may be true for{/t} short projects, {t}but not for{/t} long ones.", "短期のプロジェクトには{t}当てはまるかもしれませんが{/t}、長期のものには{t}当てはまりません{/t}。", "That may be true|for short projects,|but not|for long ones."),
        ),
        p2=rows(
            ("It's {t}more complicated than that{/t}.", "実際は{t}それほど単純ではありません{/t}。", "It's|more|complicated|than that."),
            ("It's {t}less clear-cut than that{/t}.", "実際は{t}それほど割り切れません{/t}。", "It's|less|clear-cut|than that."),
            ("It's {t}more expensive than that{/t}.", "実際は{t}それより費用がかかります{/t}。", "It's|more|expensive|than that."),
            ("It's {t}a bit more nuanced than that{/t}.", "実際は{t}それより少し込み入っています{/t}。", "It's|a bit more|nuanced|than that."),
        ),
        rules=(("Use plural ones to replace a repeated plural noun after the contrast.", "対比の後半で同じ複数名詞を繰り返さないときは、複数形 「ones」 を使います。"),
               ("Put more before the adjective and than that after it to reject an oversimplified description.", "単純化された説明を修正するときは、形容詞の前に 「more」、後ろに 「than that」 を置きます。")),
        prompt=("Qualify one real claim, or say you do not have a claim to qualify.", "実際の主張を一つ限定するか、限定したい主張がないと伝えましょう。"),
    ),
    115: dict(
        slug="thats-true-but-it-doesnt-account-for", title="That's true, but it doesn't account for",
        ko="맞지만, 그 점은 고려하지 않았어요", ja="それは事実ですが、〜が考慮されていません",
        goal=("Accept a point, identify what it misses, and preserve the action still needed.", "相手の要点を認め、見落としを示し、それでも必要な対応を伝えましょう。"),
        p1=rows(
            ("{t}That's true, but it doesn't account for{/t} the cost.", "{t}それは事実ですが、考慮されていないのは{/t}費用です。", "That's true,|but|it doesn't account for|the cost."),
            ("{t}That's true, but it doesn't account for{/t} the timing.", "{t}それは事実ですが、考慮されていないのは{/t}時期です。", "That's true,|but|it doesn't account for|the timing."),
            ("{t}That's true, but it doesn't account for{/t} staff capacity.", "{t}それは事実ですが、考慮されていないのは{/t}スタッフの対応力です。", "That's true,|but|it doesn't account for|staff capacity."),
            ("{t}That's true, but it doesn't account for{/t} the delivery risk.", "{t}それは事実ですが、考慮されていないのは{/t}納品リスクです。", "That's true,|but|it doesn't account for|the delivery risk."),
        ),
        p2=rows(
            ("{t}Even so, we still need to{/t} reduce the risk.", "それでも、{t}リスクを下げる必要があります{/t}。", "Even so,|we|still need to reduce|the risk."),
            ("{t}Even so, we still need to{/t} check the data.", "それでも、{t}データを確認する必要があります{/t}。", "Even so,|we|still need to check|the data."),
            ("{t}Even so, we still need to{/t} compare the suppliers.", "それでも、{t}取引先を比較する必要があります{/t}。", "Even so,|we|still need to compare|the suppliers."),
            ("{t}Even so, we still need to{/t} review the schedule.", "それでも、{t}日程を見直す必要があります{/t}。", "Even so,|we|still need to review|the schedule."),
        ),
        rules=(("Put the missing factor after account for; do not leave the counterpoint implicit.", "見落としている要因を 「account for」 のあとに置き、反論を曖昧にしないようにします。"),
               ("Use Even so for the counterpoint and still for the need that remains.", "反対方向の要点には 「Even so」、残っている必要には still を使います。")),
        prompt=("Respond to one real view, or say you agree and see no missing factor.", "実際の意見に答えるか、賛成で見落としはないと伝えましょう。"),
    ),
    116: dict(
        slug="if-anything-its-got-worse", title="If anything, it's got worse",
        ko="오히려 더 나빠졌어요", ja="むしろ悪化しています",
        goal=("Correct an assumption by showing that the evidence points the opposite way.", "想定を修正し、事実が逆方向を示していると伝えましょう。"),
        p1=rows(
            ("{t}If anything,{/t} it's got worse.", "{t}むしろ{/t}悪化しています。", "If anything,|it's got worse."),
            ("{t}If anything,{/t} it's become less reliable.", "{t}むしろ{/t}信頼性が下がっています。", "If anything,|it's become|less reliable."),
            ("{t}If anything,{/t} delays have increased.", "{t}むしろ{/t}遅れが増えています。", "If anything,|delays|have increased."),
            ("{t}If anything,{/t} the workload has doubled.", "{t}むしろ{/t}作業量は2倍になっています。", "If anything,|the workload|has doubled."),
        ),
        p2=rows(
            ("{t}It's actually the opposite:{/t} demand has gone up.", "{t}実際は逆で{/t}、需要は増えています。", "It's actually the opposite:|demand|has gone up."),
            ("{t}It's actually the opposite:{/t} costs have gone up.", "{t}実際は逆で{/t}、費用は増えています。", "It's actually the opposite:|costs|have gone up."),
            ("{t}It's actually the opposite:{/t} response times have increased.", "{t}実際は逆で{/t}、応答時間は長くなっています。", "It's actually the opposite:|response times|have increased."),
            ("{t}It's actually the opposite:{/t} fewer people are available.", "{t}実際は逆で{/t}、対応できる人は減っています。", "It's actually the opposite:|fewer people|are available."),
        ),
        rules=(("Use If anything before the clause that reverses the listener's expectation.", "相手の予想と逆の事実を述べる節の前に 「If anything」 を置きます。"),
               ("After the colon, give a complete clause that proves the reversal.", "コロンのあとには、その逆転を示す完全な節を続けます。")),
        omit_reorder=(1,),
        prompt=("Correct one real assumption, or say no clear example comes to mind.", "実際の想定を一つ修正するか、はっきりした例が思いつかないと伝えましょう。"),
    ),
    117: dict(
        slug="overall-id-say", title="Overall, I'd say",
        ko="전반적으로 보면, 제 생각에는", ja="総合的に見ると、私としては",
        goal=("Weigh competing considerations and state the factor that decides your conclusion.", "複数の要素を比べ、結論を決める要因を伝えましょう。"),
        p1=rows(
            ("{t}Overall, I'd say{/t} it's worth it.", "{t}総合的に見ると、私としては{/t}価値があると思います。", "Overall,|I'd say|it's worth it."),
            ("{t}Overall, I'd say{/t} the plan is practical.", "{t}総合的に見ると、私としては{/t}その案は現実的だと思います。", "Overall,|I'd say|the plan is practical."),
            ("{t}Overall, I'd say{/t} the change has helped.", "{t}総合的に見ると、私としては{/t}その変更は役に立ったと思います。", "Overall,|I'd say|the change has helped."),
            ("{t}Overall, I'd say{/t} it costs too much.", "{t}総合的に見ると、私としては{/t}費用が高すぎると思います。", "Overall,|I'd say|it costs too much."),
        ),
        p2=rows(
            ("{t}What it comes down to for me is{/t} the cost.", "{t}私にとって最終的な決め手は{/t}費用です。", "What it comes down to|for me|is|the cost."),
            ("{t}What it comes down to for me is{/t} the timing.", "{t}私にとって最終的な決め手は{/t}時期です。", "What it comes down to|for me|is|the timing."),
            ("{t}What it comes down to for me is{/t} reliability.", "{t}私にとって最終的な決め手は{/t}信頼性です。", "What it comes down to|for me|is|reliability."),
            ("{t}What it comes down to for me is{/t} long-term value.", "{t}私にとって最終的な決め手は{/t}長期的な価値です。", "What it comes down to|for me|is|long-term value."),
        ),
        rules=(("Use I'd say before a clause to make the final judgment measured rather than absolute.", "最終判断を断定ではなく穏やかに示すため、節の前に 「I'd say」 を使います。"),
               ("Put the deciding noun phrase after What it comes down to for me is.", "自分にとっての決め手となる名詞句を 「What it comes down to for me is」 のあとに置きます。")),
        prompt=("Sum up one real decision, or say you have not weighed one recently.", "実際の判断を一つまとめるか、最近検討したものはないと伝えましょう。"),
    ),
    118: dict(
        slug="you-could-see-it-that-way", title="You could see it that way",
        ko="그렇게 볼 수도 있겠지만", ja="そう見ることもできますが",
        goal=("Acknowledge an interpretation while making your reservation audible.", "一つの解釈を認めつつ、自分が引っかかる点もはっきり伝えましょう。"),
        p1=rows(
            ("{t}You could see it as{/t} cautious, {t}but{/t} I think it's too slow.", "慎重だと{t}見ることもできます{/t}{t}が{/t}、私には遅すぎると思います。", "You could see it|as cautious,|but I think|it's too slow."),
            ("{t}You could see it as{/t} efficient, {t}but{/t} I think it's too rigid.", "効率的だと{t}見ることもできます{/t}{t}が{/t}、私には厳格すぎると思います。", "You could see it|as efficient,|but I think|it's too rigid."),
            ("{t}You could see it as{/t} flexible, {t}but{/t} I think it's unclear.", "柔軟だと{t}見ることもできます{/t}{t}が{/t}、私には不明確だと思います。", "You could see it|as flexible,|but I think|it's unclear."),
            ("{t}You could see it as{/t} simple, {t}but{/t} I think it's incomplete.", "単純だと{t}見ることもできます{/t}{t}が{/t}、私には不十分だと思います。", "You could see it|as simple,|but I think|it's incomplete."),
        ),
        p2=rows(
            ("{t}I can see why you'd call it{/t} a success, {t}though{/t}.", "成功と{t}呼ぶ理由は分かります{/t}{t}けどね{/t}。", "I can see why|you'd call it|a success,|though."),
            ("{t}I can see why you'd call it{/t} progress, {t}though{/t}.", "進歩と{t}呼ぶ理由は分かります{/t}{t}けどね{/t}。", "I can see why|you'd call it|progress,|though."),
            ("{t}I can see why you'd call it{/t} cautious, {t}though{/t}.", "慎重と{t}呼ぶ理由は分かります{/t}{t}けどね{/t}。", "I can see why|you'd call it|cautious,|though."),
            ("{t}I can see why you'd call it{/t} fair, {t}though{/t}.", "公平と{t}呼ぶ理由は分かります{/t}{t}けどね{/t}。", "I can see why|you'd call it|fair,|though."),
        ),
        rules=(("Use see it as before a description; as is required in this frame.", "説明を続けるときは 「see it as」 を使い、この形では as が必要です。"),
               ("Use call it directly before the description, then final though to signal a reservation.", "「call it」 の直後に説明を置き、文末の 「though」 で少し距離を示します。")),
        prompt=("Respond to one interpretation, or say you do not have a view yet.", "一つの解釈に答えるか、まだ意見がないと伝えましょう。"),
    ),
    119: dict(
        slug="lets-just-say-it-didnt-go-well", title="Let's just say it didn't go well",
        ko="그냥 잘 안 됐다고만 해 두죠", ja="うまくいかなかった、とだけ言っておきます",
        goal=("Offer deliberately limited information and let the listener infer the rest.", "意図的に情報を限定し、残りは相手に察してもらいましょう。"),
        p1=rows(
            ("{t}Let's just say{/t} it didn't go well.", "{t}うまくいかなかった、とだけ言っておきます{/t}。", "Let's just say|it didn't go well."),
            ("{t}Let's just say{/t} the meeting was difficult.", "{t}会議は大変だった、とだけ言っておきます{/t}。", "Let's just say|the meeting|was difficult."),
            ("{t}Let's just say{/t} we didn't agree.", "{t}意見が合わなかった、とだけ言っておきます{/t}。", "Let's just say|we didn't agree."),
            ("{t}Let's just say{/t} the result was disappointing.", "{t}結果は残念だった、とだけ言っておきます{/t}。", "Let's just say|the result|was disappointing."),
        ),
        p2=rows(
            ("{t}All I'll say is that{/t} we disagreed.", "{t}私が言えるのは{/t}、意見が合わなかったということだけです。", "All I'll say|is that|we|disagreed."),
            ("{t}All I'll say is that{/t} the timing was wrong.", "{t}私が言えるのは{/t}、時期が悪かったということだけです。", "All I'll say|is that|the timing|was wrong."),
            ("{t}All I'll say is that{/t} the project needs more work.", "{t}私が言えるのは{/t}、その企画にはさらに作業が必要ということだけです。", "All I'll say|is that|the project|needs more work."),
            ("{t}All I'll say is that{/t} the discussion ended early.", "{t}私が言えるのは{/t}、話し合いが早く終わったということだけです。", "All I'll say|is that|the discussion|ended early."),
        ),
        rules=(("After Let's just say, use one complete clause that gives the limited version.", "「Let's just say」 のあとには、限定して伝える内容を完全な節で続けます。"),
               ("After All I'll say is, use that plus the one clause you are willing to offer.", "「All I'll say is」 のあとには that と、伝えてよい一つの節を続けます。")),
        omit_reorder=(1,),
        prompt=("Summarize one experience without details, or say no such example comes to mind.", "詳しく話さずに一つの経験をまとめるか、そのような例は思いつかないと伝えましょう。"),
    ),
    120: dict(
        slug="you-might-want-to-check-that", title="You might want to check that",
        ko="그건 확인해 보는 게 좋겠어요", ja="それは確認したほうがよさそうです",
        goal=("Recognize and give an instruction that is phrased like a suggestion.", "提案の形をした指示を聞き取り、自分でも使いましょう。"),
        p1=rows(
            ("{t}You might want to{/t} check that again.", "それはもう一度{t}確認したほうがよさそうです{/t}。", "You|might want to|check|that again."),
            ("{t}You might want to{/t} review the numbers.", "数字を{t}見直したほうがよさそうです{/t}。", "You|might want to|review|the numbers."),
            ("{t}You might want to{/t} save a copy.", "コピーを{t}保存したほうがよさそうです{/t}。", "You|might want to|save|a copy."),
            ("{t}You might want to{/t} ask the manager.", "上司に{t}聞いたほうがよさそうです{/t}。", "You|might want to|ask|the manager."),
        ),
        p2=rows(
            ("It {t}might be worth{/t} asking her.", "彼女に聞いてみる{t}価値があるかもしれません{/t}。", "It|might be worth|asking|her."),
            ("It {t}might be worth{/t} checking the schedule.", "日程を確認してみる{t}価値があるかもしれません{/t}。", "It|might be worth|checking|the schedule."),
            ("It {t}might be worth{/t} getting another quote.", "別の見積もりを取ってみる{t}価値があるかもしれません{/t}。", "It|might be worth|getting|another quote."),
            ("It {t}might be worth{/t} checking the file name.", "ファイル名を確認してみる{t}価値があるかもしれません{/t}。", "It|might be worth|checking|the file name."),
        ),
        rules=(("After might want to, use the plain verb; in context, the line may function as an instruction.", "「might want to」 のあとは動詞の原形にし、文脈によっては指示として働くことにも注意します。"),
               ("After might be worth, use the -ing form for the action to consider.", "検討する行動は 「might be worth」 のあとに -ing 形で置きます。")),
        prompt=("Give one useful suggestion, or say you do not have one to offer.", "役に立つ提案を一つするか、提案は思いつかないと伝えましょう。"),
    ),
    121: dict(
        slug="id-rather-not-go-into-it", title="I'd rather not go into it",
        ko="그 얘기는 자세히 하지 않을게요", ja="そのことは詳しく話さないでおきます",
        goal=("Set a clear boundary without rejecting the other person.", "相手を拒まずに、会話の境界をはっきり示しましょう。"),
        p1=rows(
            ("{t}I'd rather not go into{/t} the details.", "詳細には{t}触れないでおきます{/t}。", "I'd rather not|go into|the details."),
            ("{t}I'd rather not go into{/t} the reasons.", "理由には{t}触れないでおきます{/t}。", "I'd rather not|go into|the reasons."),
            ("{t}I'd rather not go into{/t} the complaint.", "その苦情には{t}触れないでおきます{/t}。", "I'd rather not|go into|the complaint."),
            ("{t}I'd rather not go into{/t} what happened.", "何があったかには{t}触れないでおきます{/t}。", "I'd rather not|go into|what happened."),
        ),
        p2=rows(
            ("{t}Can we leave{/t} this {t}for now{/t}?", "これは{t}今はいったん{/t}{t}置いておけますか{/t}？", "Can we|leave|this|for now?"),
            ("{t}Can we leave{/t} that topic {t}for now{/t}?", "その話題は{t}今はいったん{/t}{t}置いておけますか{/t}？", "Can we|leave|that topic|for now?"),
            ("{t}Can we leave{/t} the decision {t}for now{/t}?", "その判断は{t}今はいったん{/t}{t}置いておけますか{/t}？", "Can we|leave|the decision|for now?"),
            ("{t}Can we leave{/t} the next step {t}for now{/t}?", "次の段階は{t}今はいったん{/t}{t}置いておけますか{/t}？", "Can we|leave|the next step|for now?"),
        ),
        rules=(("After would rather not, use the plain verb without to: rather not go.", "「would rather not」 のあとは to を入れず、動詞の原形を使って 「rather not go」 とします。"),
               ("Put the topic between leave and for now to postpone that topic, not reject it forever.", "話題を 「leave」 と 「for now」 の間に置き、永久に拒否するのではなく今だけ保留します。")),
        prompt=("Set one real conversational boundary, or say every current topic is fine.", "実際の会話の境界を一つ示すか、今の話題はすべて大丈夫だと伝えましょう。"),
    ),
    122: dict(
        slug="its-not-that-simple", title="It's not that simple",
        ko="그렇게 단순한 문제는 아니에요", ja="それほど単純ではありません",
        goal=("Reject an oversimplified framing and replace it with the question that matters.", "単純化された枠組みを退け、本当に重要な問いに置き換えましょう。"),
        p1=rows(
            ("{t}It's not that{/t} simple, {t}though{/t}.", "{t}ただ{/t}、{t}それほど単純ではありません{/t}。", "It's|not that simple,|though."),
            ("{t}It's not quite that{/t} clear, {t}though{/t}.", "{t}ただ{/t}、{t}それほど明確とは言えません{/t}。", "It's|not quite that clear,|though."),
            ("{t}It's not that{/t} easy, {t}though{/t}.", "{t}ただ{/t}、{t}それほど簡単ではありません{/t}。", "It's|not that easy,|though."),
            ("{t}It's not always that{/t} straightforward, {t}though{/t}.", "{t}ただ{/t}、{t}いつもそれほど単純明快とは限りません{/t}。", "It's|not always that straightforward,|though."),
        ),
        p2=rows(
            ("{t}That's not really{/t} the question.", "それは{t}本当に問うべきことではありません{/t}。", "That's|not really|the question."),
            ("{t}That's not really{/t} what I meant.", "それは{t}私が言いたかったことではありません{/t}。", "That's|not really|what I meant."),
            ("{t}That's not really{/t} the issue.", "それは{t}本当の論点ではありません{/t}。", "That's|not really|the issue."),
            ("{t}That's not really{/t} how I'd put it.", "それは{t}私ならそうは言いません{/t}。", "That's|not really|how I'd put it."),
        ),
        rules=(("In It's not that plus an adjective, that points back to the listener's description; final though softens the correction.", "「It's not that」＋形容詞の that は相手の説明を指し、文末の 「though」 が修正を和らげます。"),
               ("Use not really before the noun to reject the proposed frame rather than answer inside it.", "提示された枠組みの中で答えずに退けるときは、名詞の前に 「not really」 を置きます。")),
        prompt=("Challenge one oversimplified question, or say the simple framing works for you.", "単純化された問いを一つ見直すか、その枠組みで問題ないと伝えましょう。"),
    ),
}


SPECS = {
    113: semantic_spec(
        (("Use this to name the deeper pattern behind one recurring visible problem.", "繰り返し見える一つの問題の背後にある、より深い構造を示すときに使います。"),
         ("Use this to show that one visible sign belongs to a broader problem.", "一つの目に見える兆候が、より広い問題の一部だと示すときに使います。")),
        (("Name the deeper cause of one recurring problem, or say none comes to mind.", "繰り返す問題の深い原因を挙げるか、思いつかないと伝えましょう。"),
         ("Name the broader problem it reveals, or say you cannot identify one.", "それが示すより広い問題を挙げるか、特定できないと伝えましょう。")),
        (choices(
            ("根本的な問題{t}は{/t}、仕事の範囲の決め方です。", "The underlying issue ", "is", "are", " how we scope things."),
            ("根本的な問題{t}は{/t}、意思決定の仕方です。", "The underlying issue ", "is", "are", " how decisions get made."),
            ("根本的な問題{t}は{/t}、担当が不明確なことです。", "The underlying issue ", "is", "are", " unclear ownership."),
            ("根本的な問題{t}は{/t}、優先事項の衝突です。", "The underlying issue ", "is", "are", " conflicting priorities."),
        ), choices(
            ("それは、より大きな問題{t}の表れです{/t}。", "It's symptomatic ", "of", "for", " a bigger problem."),
            ("それは、意思疎通の不足{t}の表れです{/t}。", "It's symptomatic ", "of", "for", " poor communication."),
            ("それは、計画不足{t}の表れです{/t}。", "It's symptomatic ", "of", "for", " weak planning."),
            ("それは、優先事項の不明確さ{t}の表れです{/t}。", "It's symptomatic ", "of", "for", " unclear priorities."),
        )),
        (("Name the abstraction", "抽象的な問題を示す", "The underlying issue + <b>is</b> + 名詞句／wh節", "One deeper pattern", "一つの深い構造", ("The underlying issue <b>is unclear ownership</b>.", "The underlying issue <b>is how decisions get made</b>.")),
         ("Connect sign and cause", "兆候と原因をつなぐ", "兆候 + be + <b>symptomatic of</b> + 広い問題", "Broader problem", "より広い問題", ("It's <b>symptomatic of poor communication</b>.", "It's <b>symptomatic of weak planning</b>."))),
        ("Issue or symptom?", "問題か兆候か", "Use “issue” for the problem itself and “symptom” for the visible sign that points to it.", "問題そのものには「issue」、その問題を示す目に見える兆候には「symptom」を使います。", ("Problem itself", "問題そのもの", "The issue is unclear ownership.", "問題は担当が不明確なことです。"), ("Visible sign", "目に見える兆候", "Repeated delays are a symptom.", "繰り返す遅れは兆候です。")),
    ),
    114: semantic_spec(
        (("Use this to accept a claim for one group while explicitly excluding another.", "一つの集団には主張を認めつつ、別の集団には当てはまらないと明示するときに使います。"),
         ("Use this to reject a description as too simple on one comparative scale.", "一つの比較尺度で、説明が単純すぎると修正するときに使います。")),
        (("Name the group where a claim holds and the group where it does not, or say the claim holds generally.", "主張が当てはまる集団と当てはまらない集団を挙げるか、その主張は一般に当てはまると伝えましょう。"),
         ("Say what is more complex, costly, uncertain, or flexible, or say the first description is enough.", "より複雑・高価・不確か・柔軟な点を言うか、最初の説明で十分だと伝えましょう。")),
        (choices(
            ("大きなチームには当てはまりますが、小さな{t}チームには{/t}当てはまりません。", "That may be true for large teams, but not for small ", "ones", "one", "."),
            ("新しい利用者には当てはまりますが、経験のある{t}利用者には{/t}当てはまりません。", "That may be true for new users, but not for experienced ", "ones", "one", "."),
            ("都市のオフィスには当てはまりますが、地方の{t}オフィスには{/t}当てはまりません。", "That may be true for city offices, but not for rural ", "ones", "one", "."),
            ("短期の企画には当てはまりますが、長期の{t}企画には{/t}当てはまりません。", "That may be true for short projects, but not for long ", "ones", "one", "."),
        ), choices(
            ("実際は{t}それより複雑です{/t}。", "It's ", "more complicated", "most complicated", " than that."),
            ("実際は{t}それより費用がかかります{/t}。", "It's ", "more expensive", "most expensive", " than that."),
            ("実際は{t}それより不確かです{/t}。", "It's ", "more uncertain", "most uncertain", " than that."),
            ("実際は{t}それより柔軟です{/t}。", "It's ", "more flexible", "most flexible", " than that."),
        )),
        (("Limit the claim", "主張の範囲を限定", "true + <b>for A, but not for B</b>", "Plural noun replacement", "複数名詞の置き換え", ("true for large teams, but not for small <b>ones</b>", "true for new users, but not for experienced <b>ones</b>")),
         ("Reject oversimplification", "単純化を修正", "be + <b>more</b> + 形容詞 + <b>than that</b>", "One comparative scale", "一つの比較尺度", ("It's <b>more complicated than that</b>.", "It's <b>more uncertain than that</b>."))),
        ("Generally true or true for some?", "一般に正しい・一部に正しい", "Use “generally true” for a broad tendency and “true for some” when important exceptions remain.", "広い傾向なら「generally true」、重要な例外が残るなら「true for some」を使います。", ("Broad tendency", "広い傾向", "That's generally true.", "それは一般に当てはまります。"), ("Important exceptions", "重要な例外あり", "That's true for some teams.", "一部のチームには当てはまります。")),
    ),
    115: semantic_spec(
        (("Use this to concede a real point and immediately name the factor it leaves out.", "相手の正しい点を認め、直後に見落としている要因を示すときに使います。"),
         ("Use this to preserve the action that remains necessary after that concession.", "相手の点を認めたあとも必要な対応を残すときに使います。")),
        (("Accept one point and name one missing factor, or say nothing is missing.", "一つの点を認めて見落としを一つ挙げるか、見落としはないと伝えましょう。"),
         ("Name the action still needed, or say no further action is needed.", "それでも必要な対応を挙げるか、追加対応は不要だと伝えましょう。")),
        (choices(
            ("それは事実ですが、費用が{t}考慮されていません{/t}。", "That's true, but it doesn't ", "account for", "count for", " the cost."),
            ("それは事実ですが、時期が{t}考慮されていません{/t}。", "That's true, but it doesn't ", "account for", "count for", " the timing."),
            ("それは事実ですが、対応力が{t}考慮されていません{/t}。", "That's true, but it doesn't ", "account for", "count to", " staff capacity."),
            ("それは事実ですが、納品リスクが{t}考慮されていません{/t}。", "That's true, but it doesn't ", "account for", "count for", " the delivery risk."),
        ), choices(
            ("それでも、リスクを{t}下げる必要があります{/t}。", "Even so, we ", "still need to", "need still to", " reduce the risk."),
            ("それでも、データを{t}確認する必要があります{/t}。", "Even so, we ", "still need to", "need still to", " check the data."),
            ("それでも、取引先を{t}比較する必要があります{/t}。", "Even so, we ", "still need to", "need still to", " compare the suppliers."),
            ("それでも、日程を{t}見直す必要があります{/t}。", "Even so, we ", "still need to", "need still to", " review the schedule."),
        )),
        (("Make the omission explicit", "見落としを明示", "it doesn't + <b>account for</b> + 要因", "One missing factor", "見落とした一要因", ("It doesn't <b>account for the cost</b>.", "It doesn't <b>account for the delivery risk</b>.")),
         ("Keep the need alive", "必要な対応を残す", "<b>Even so</b>, 主語 + <b>still need to</b> + 動詞", "Required next action", "必要な次の対応", ("<b>Even so, we still need to</b> check the data.", "<b>Even so, we still need to</b> reduce the risk."))),
        ("But or even so?", "but と even so", "Use “but” inside one contrast. Use “Even so” to respond to a complete point while preserving your conclusion.", "一つの文の中の対比には「but」を使います。相手の完結した要点を受けても結論を保つときは「Even so」を使います。", ("Inside one sentence", "一文内の対比", "That's true, but the risk remains.", "それは事実ですが、リスクは残ります。"), ("After a complete point", "完結した要点のあと", "Even so, we need to check.", "それでも、確認が必要です。")),
    ),
    116: semantic_spec(
        (("Use this when the evidence does not merely weaken an assumption but points in the reverse direction.", "事実が想定を弱めるだけでなく、逆方向を示すときに使います。"),
         ("Use this to state the reversal first and then give the clause that proves it.", "最初に逆だと示し、そのあとに根拠となる節を続けるときに使います。")),
        (("State one real reversal, or say no clear example comes to mind.", "実際の逆転を一つ述べるか、はっきりした例は思いつかないと伝えましょう。"),
         ("Give the fact that proves the opposite, or say you do not have enough evidence.", "逆だと示す事実を挙げるか、十分な根拠がないと伝えましょう。")),
        (choices(
            ("想定に反して、{t}むしろ{/t}悪化しています。", "", "If anything,", "If something,", " it's got worse."),
            ("想定に反して、{t}むしろ{/t}信頼性が下がっています。", "", "If anything,", "If everything,", " it's become less reliable."),
            ("想定に反して、{t}むしろ{/t}遅れが増えています。", "", "If anything,", "If something,", " delays have increased."),
            ("想定に反して、{t}むしろ{/t}作業量が2倍です。", "", "If anything,", "If everything,", " the workload has doubled."),
        ), choices(
            ("実際は{t}逆で{/t}、需要が増えています。", "It's actually ", "the opposite", "an opposite", ": demand has gone up."),
            ("実際は{t}逆で{/t}、費用が増えています。", "It's actually ", "the opposite", "an opposite", ": costs have gone up."),
            ("実際は{t}逆で{/t}、応答時間が長くなっています。", "It's actually ", "the opposite", "an opposite", ": response times have increased."),
            ("実際は{t}逆で{/t}、対応できる人が減っています。", "It's actually ", "the opposite", "an opposite", ": fewer people are available."),
        )),
        (("Reverse the expectation", "予想を逆転", "<b>If anything</b>, + 逆方向の節", "Stronger than a small correction", "小さな修正より強い", ("<b>If anything,</b> it's got worse.", "<b>If anything,</b> delays have increased.")),
         ("State and prove the opposite", "逆だと示して証明", "It's actually <b>the opposite:</b> + 完全な節", "Evidence after the colon", "コロン後に根拠", ("It's actually <b>the opposite: demand has gone up</b>.", "It's actually <b>the opposite: costs have gone up</b>."))),
        ("Actually or if anything?", "actually と if anything", "Use “actually” for a correction. Use “if anything” only when the truth points beyond neutral in the opposite direction.", "単なる修正には「actually」を使います。事実が中立を越えて逆方向にあるときだけ「if anything」を使います。", ("Simple correction", "単なる修正", "Actually, demand is stable.", "実際、需要は安定しています。"), ("Opposite direction", "逆方向", "If anything, demand has risen.", "むしろ需要は増えています。")),
    ),
    117: semantic_spec(
        (("Use this to land on a measured conclusion after considering more than one side.", "複数の面を考えたあと、穏やかな結論に着地するときに使います。"),
         ("Use this to name the single factor that ultimately decides your own judgment.", "最終的に自分の判断を決める一つの要因を示すときに使います。")),
        (("Give your overall judgment on one real choice, or say you have not weighed one.", "実際の選択について総合判断を述べるか、検討したものはないと伝えましょう。"),
         ("Name your deciding factor, or say no single factor decided it.", "自分の決め手を挙げるか、一つの要因では決まらなかったと伝えましょう。")),
        (choices(
            ("総合的に見ると、{t}私としては{/t}価値があると思います。", "Overall, ", "I'd say", "I say", " it's worth it."),
            ("総合的に見ると、{t}私としては{/t}現実的だと思います。", "Overall, ", "I'd say", "I said", " the plan is practical."),
            ("総合的に見ると、{t}私としては{/t}役に立ったと思います。", "Overall, ", "I'd say", "I tell", " the change has helped."),
            ("総合的に見ると、{t}私としては{/t}費用が高すぎると思います。", "Overall, ", "I'd say", "I told", " it costs too much."),
        ), choices(
            ("私にとって最終的な決め手{t}は{/t}費用です。", "What it comes down to for me ", "is", "are", " the cost."),
            ("私にとって最終的な決め手{t}は{/t}時期です。", "What it comes down to for me ", "is", "are", " the timing."),
            ("私にとって最終的な決め手{t}は{/t}信頼性です。", "What it comes down to for me ", "is", "are", " reliability."),
            ("私にとって最終的な決め手{t}は{/t}長期的な価値です。", "What it comes down to for me ", "is", "are", " long-term value."),
        )),
        (("Land on the judgment", "判断に着地", "<b>Overall, I'd say</b> + 節", "Measured conclusion", "穏やかな結論", ("<b>Overall, I'd say</b> it's worth it.", "<b>Overall, I'd say</b> it costs too much.")),
         ("Focus the deciding factor", "決め手を焦点化", "What it comes down to + <b>for me is</b> + 名詞句", "Personal deciding factor", "自分の決め手", ("What it comes down to <b>for me is the cost</b>.", "What it comes down to <b>for me is reliability</b>."))),
        ("For me or objectively?", "自分の判断・客観的事実", "Add “for me” when you are naming your own deciding factor rather than claiming that everyone should rank it first.", "誰にとっても最優先だと主張せず、自分の決め手を示すときは「for me」を加えます。", ("Personal priority", "自分の優先事項", "For me, it comes down to cost.", "私にとっては費用が決め手です。"), ("Shared evidence", "共有できる事実", "The total cost is ten thousand dollars.", "総費用は1万ドルです。")),
    ),
    118: semantic_spec(
        (("Use this to grant that an interpretation is possible before stating your reservation.", "一つの解釈が可能だと認めてから、自分が引っかかる点を述べるときに使います。"),
         ("Use this to acknowledge why someone chose a label while final though keeps your distance from it.", "相手がその呼び方を選ぶ理由を認めつつ、文末の 「though」 で距離を残すときに使います。")),
        (("Acknowledge one interpretation and add your reservation, or say you agree with it.", "一つの解釈を認めて違う見方を加えるか、その解釈に賛成だと伝えましょう。"),
         ("Acknowledge one label while keeping your reservation, or say the label fully fits.", "一つの呼び方を認めつつ少し距離を置くか、その呼び方で完全に合うと伝えましょう。")),
        (choices(
            ("慎重だと見ることもできます{t}が{/t}、遅すぎると思います。", "You could see it as cautious, ", "but", "so", " I think it's too slow."),
            ("効率的だと見ることもできます{t}が{/t}、厳格すぎると思います。", "You could see it as efficient, ", "but", "so", " I think it's too rigid."),
            ("柔軟だと見ることもできます{t}が{/t}、不明確だと思います。", "You could see it as flexible, ", "but", "so", " I think it's unclear."),
            ("単純だと見ることもできます{t}が{/t}、不十分だと思います。", "You could see it as simple, ", "but", "so", " I think it's incomplete."),
        ), choices(
            ("成功と{t}呼ぶ理由は分かりますけどね{/t}。", "I can see why you'd call it ", "a success", "as a success", ", though."),
            ("進歩と{t}呼ぶ理由は分かりますけどね{/t}。", "I can see why you'd call it ", "progress", "as progress", ", though."),
            ("慎重と{t}呼ぶ理由は分かりますけどね{/t}。", "I can see why you'd call it ", "cautious", "as cautious", ", though."),
            ("公平と{t}呼ぶ理由は分かりますけどね{/t}。", "I can see why you'd call it ", "fair", "as fair", ", though."),
        )),
        (("Interpret with as", "as で解釈", "see + it + <b>as</b> + 説明", "Possible interpretation", "可能な解釈", ("You could see it <b>as cautious</b>.", "You could see it <b>as efficient</b>.")),
         ("Label without as", "as なしで呼ぶ", "call + it + 説明 + <b>though</b>", "Acknowledged label, reserved stance", "呼び方を認めつつ少し距離を置く", ("I can see why you'd <b>call it a success, though</b>.", "I can see why you'd <b>call it progress, though</b>."))),
        ("Where does though go?", "though の位置", "Final “though” sounds conversational and leaves the reservation hanging gently; initial “although” starts a more explicit clause contrast.", "文末の「though」は会話的に少し距離を残し、文頭の「although」はより明示的な節の対比を始めます。", ("Conversational reservation", "少し距離を残す", "I see why, though.", "理由は分かりますけどね。"), ("Explicit clause contrast", "明示的な節の対比", "Although I see why, I disagree.", "理由は分かりますが、反対です。")),
    ),
    119: semantic_spec(
        (("Use this to give a deliberately limited version and signal that the omitted detail matters.", "意図的に限定した説明をし、省いた詳細にも意味があると示すときに使います。"),
         ("Use this to state the one fact you are willing to offer and set a clear information limit.", "伝えてよい一つの事実だけを述べ、情報の範囲を明確にするときに使います。")),
        (("Give a deliberately brief summary, or say you have no matching experience.", "意図的に短くまとめるか、当てはまる経験はないと伝えましょう。"),
         ("State the one fact you are willing to share, or say there is nothing to add.", "伝えてよい一つの事実を述べるか、付け加えることはないと伝えましょう。")),
        (choices(
            ("うまくいかなかった{t}とだけ言っておきます{/t}。", "", "Let's just say", "Let's only tell", " it didn't go well."),
            ("会議は大変だった{t}とだけ言っておきます{/t}。", "", "Let's just say", "Let's only tell", " the meeting was difficult."),
            ("意見が合わなかった{t}とだけ言っておきます{/t}。", "", "Let's just say", "Let's only tell", " we didn't agree."),
            ("結果は残念だった{t}とだけ言っておきます{/t}。", "", "Let's just say", "Let's only tell", " the result was disappointing."),
        ), choices(
            ("私が言えるのは、意見が合わなかった{t}ということだけです{/t}。", "All I'll say is ", "that", "what", " we disagreed."),
            ("私が言えるのは、時期が悪かった{t}ということだけです{/t}。", "All I'll say is ", "that", "what", " the timing was wrong."),
            ("私が言えるのは、さらに作業が必要だ{t}ということだけです{/t}。", "All I'll say is ", "that", "what", " the project needs more work."),
            ("私が言えるのは、話し合いが早く終わった{t}ということだけです{/t}。", "All I'll say is ", "that", "what", " the discussion ended early."),
        )),
        (("Signal deliberate restraint", "意図的な抑制を示す", "<b>Let's just say</b> + 完全な節", "Limited summary", "限定したまとめ", ("<b>Let's just say</b> it didn't go well.", "<b>Let's just say</b> we didn't agree.")),
         ("Offer one fact only", "一つの事実だけ伝える", "All I'll say + <b>is that</b> + 完全な節", "Explicit information limit", "明示的な情報制限", ("All I'll say <b>is that we disagreed</b>.", "All I'll say <b>is that it ended early</b>."))),
        ("Brief, not evasive", "短く、逃げずに", "A calm complete clause sounds deliberate. Trailing off mid-sentence can sound uncertain rather than private.", "落ち着いて完全な節を言うと、意図的な限定に聞こえます。文の途中で曖昧に終えると、不確かに聞こえることがあります。", ("Deliberate limit", "意図的な限定", "Let's just say we disagreed.", "意見が合わなかった、とだけ言っておきます。"), ("Uncertain hesitation", "不確かなためらい", "Well, I sort of...", "ええと、その…。")),
    ),
    120: semantic_spec(
        (("Use this when a suggestion-shaped line is meant to prompt action; context and tone decide how optional it is.", "提案の形をした文で行動を促すときに使い、任意かどうかは文脈と声調で判断します。"),
         ("Use this to recommend an action as worth considering without directly assigning it.", "行動を直接命じず、検討する価値があると勧めるときに使います。")),
        (("Give one useful softened instruction, or say you have no suggestion.", "役に立つやわらかな指示を一つするか、提案はないと伝えましょう。"),
         ("Recommend one action worth considering, or say no extra step is needed.", "検討する価値がある行動を一つ勧めるか、追加の手順は不要だと伝えましょう。")),
        (choices(
            ("それはもう一度{t}確認した{/t}ほうがよさそうです。", "You might want to ", "check", "checking", " that again."),
            ("数字を{t}見直した{/t}ほうがよさそうです。", "You might want to ", "review", "reviewing", " the numbers."),
            ("コピーを{t}保存した{/t}ほうがよさそうです。", "You might want to ", "save", "saving", " a copy."),
            ("上司に{t}聞いた{/t}ほうがよさそうです。", "You might want to ", "ask", "asking", " the manager."),
        ), choices(
            ("彼女に{t}聞いてみる{/t}価値があるかもしれません。", "It might be worth ", "asking", "ask", " her."),
            ("日程を{t}確認してみる{/t}価値があるかもしれません。", "It might be worth ", "checking", "check", " the schedule."),
            ("別の見積もりを{t}取る{/t}価値があるかもしれません。", "It might be worth ", "getting", "get", " another quote."),
            ("ファイル名を{t}確認する{/t}価値があるかもしれません。", "It might be worth ", "checking", "check", " the file name."),
        )),
        (("Softened directive", "やわらかな指示", "might + <b>want to</b> + 動詞の原形", "Action may still be expected", "行動を期待する場合もある", ("You might want to <b>check</b> that.", "You might want to <b>save</b> a copy.")),
         ("Recommendation to consider", "検討を勧める", "might be + <b>worth</b> + -ing", "Action worth considering", "検討する価値のある行動", ("It might be worth <b>asking</b> her.", "It might be worth <b>waiting</b>."))),
        ("Might want to or could?", "might want to と could", "In workplace context, “might want to” can imply expected action. “Could” more often presents an available option.", "職場の文脈では「might want to」が期待される行動を暗示することがあります。「could」は選択可能な案を示すことが多いです。", ("Action may be expected", "行動を期待", "You might want to check that.", "それは確認したほうがよさそうです。"), ("One available option", "選べる案の一つ", "You could check that.", "それを確認する手もあります。")),
    ),
    121: semantic_spec(
        (("Use this to decline detail explicitly while keeping the relationship respectful.", "詳しく話すことを明確に断りつつ、相手との関係を丁寧に保つときに使います。"),
         ("Use this to postpone one named topic without rejecting it forever.", "一つの話題を永久に拒否せず、今だけ保留するときに使います。")),
        (("Name one detail you prefer not to discuss, or say every current topic is fine.", "話したくない詳細を一つ挙げるか、今の話題はすべて大丈夫だと伝えましょう。"),
         ("Name one topic to leave for now, or say you are ready to continue.", "今はいったん置きたい話題を挙げるか、続けられると伝えましょう。")),
        (choices(
            ("詳細には{t}触れないで{/t}おきます。", "I'd rather not ", "go", "to go", " into the details."),
            ("理由には{t}触れないで{/t}おきます。", "I'd rather not ", "go", "to go", " into the reasons."),
            ("苦情には{t}触れないで{/t}おきます。", "I'd rather not ", "go", "to go", " into the complaint."),
            ("何があったかには{t}触れないで{/t}おきます。", "I'd rather not ", "go", "to go", " into what happened."),
        ), choices(
            ("これは{t}今はいったん置いておけますか{/t}？", "Can we ", "leave", "leaving", " this for now?"),
            ("その話題は{t}今はいったん置いておけますか{/t}？", "Can we ", "leave", "left", " that topic for now?"),
            ("その判断は{t}今はいったん置いておけますか{/t}？", "Can we ", "leave", "leaving", " the decision for now?"),
            ("次の段階は{t}今はいったん置いておけますか{/t}？", "Can we ", "leave", "left", " the next step for now?"),
        )),
        (("Choose the plain verb", "動詞の原形を選ぶ", "would rather not + <b>go into</b> + 詳細", "No to before the verb", "動詞の前に to なし", ("I'd rather not <b>go into the details</b>.", "I'd rather not <b>go into the reasons</b>.")),
         ("Postpone one named topic", "一つの話題を保留", "Can we + <b>leave</b> + 話題 + <b>for now</b>?", "Temporary boundary", "一時的な境界", ("Can we <b>leave this for now</b>?", "Can we <b>leave the decision for now</b>?"))),
        ("Softer or firmer boundary?", "やわらかい・強い境界", "“I'd rather not say” is a polite neutral boundary. “I don't want to discuss it” is firmer when the boundary must be unmistakable.", "「I'd rather not say」は丁寧で中立的な境界です。より明確に断る必要があるときは「I don't want to discuss it」と言えます。", ("Polite neutral boundary", "丁寧で中立", "I'd rather not say.", "それは言わないでおきます。"), ("Firmer boundary", "より強い境界", "I don't want to discuss it.", "それについて話したくありません。")),
    ),
    122: semantic_spec(
        (("Use this to reject the listener's simple description without rejecting the whole conversation.", "相手の単純な説明だけを退け、会話そのものは拒否しないときに使います。"),
         ("Use this to step outside the proposed question and redirect attention to the real issue.", "提示された問いの外に出て、本当の論点へ注意を向け直すときに使います。")),
        (("Reject one oversimplified description, or say it is simple enough.", "単純化された説明を一つ退けるか、十分に単純だと伝えましょう。"),
         ("Name the framing that misses the point, or say the original question is right.", "要点を外している枠組みを示すか、元の問いでよいと伝えましょう。")),
        (choices(
            ("ただ、それほど{t}単純ではありません{/t}。", "It's not that ", "simple", "simply", ", though."),
            ("ただ、それほど{t}明確ではありません{/t}。", "It's not that ", "clear", "clearly", ", though."),
            ("ただ、それほど{t}簡単ではありません{/t}。", "It's not that ", "easy", "easily", ", though."),
            ("ただ、それほど{t}単純明快ではありません{/t}。", "It's not that ", "straightforward", "straightforwardly", ", though."),
        ), choices(
            ("それは{t}厳密には問うべきことではありません{/t}。", "That's ", "not really", "really not", " the question."),
            ("それは{t}まったく論点ではありません{/t}。", "That's ", "really not", "not really", " the issue."),
            ("それは{t}厳密には選択肢とは言えません{/t}。", "That's ", "not really", "really not", " the choice."),
            ("それは{t}まったく問題ではありません{/t}。", "That's ", "really not", "not really", " the problem."),
        )),
        (("Resist the description", "説明を退ける", "It's + <b>not that</b> + 形容詞 + <b>though</b>", "Softened correction", "和らげた修正", ("It's <b>not that simple, though</b>.", "It's <b>not that clear, though</b>.")),
         ("Resist the premise", "前提を退ける", "That's + <b>not really</b> + 問われたもの", "Redirect the question", "問いを向け直す", ("That's <b>not really the question</b>.", "That's <b>not really the issue</b>."))),
        ("Not that simple or not quite that simple?", "not that simple と not quite that simple", "Adding “quite” makes the correction a little softer without changing the premise you are resisting.", "「quite」を加えると、退ける前提は変えずに修正を少しやわらかくできます。", ("Direct but softened", "直接的だが緩和", "It's not that simple, though.", "ただ、それほど単純ではありません。"), ("A little softer", "もう少しやわらかい", "It's not quite that simple.", "そこまで単純ではありません。")),
    ),
}


# Provenance is reconciled against the visible <= CORE-91 corpus.  Concurrent
# CORE-92--112 owners are intentionally not cited until their stable maps land.
VOCAB = {
    113: dict(new="ownership|担当の明確さ; priorities|優先事項; symptomatic|表れである", recycled="delivery|配達|CORE-77; scope|範囲|CORE-84", assumed="issue|問題; problem|問題; project|企画; communication|意思疎通; decisions|意思決定; planning|計画; unclear ownership|担当が不明確; conflicting priorities|優先事項の衝突; weak planning|計画不足; poor communication|意思疎通不足; unclear priorities|優先事項が不明確; a bigger problem|より大きな問題", receptive="at root|根本では; the bigger picture|全体像; symptom|兆候"),
    114: dict(new="complicated|複雑な; clear-cut|割り切れる; nuanced|込み入った; uncertain|不確かな; flexible|柔軟な; rural|地方の; experienced|経験のある", recycled="expensive|高い|CORE-19", assumed="large|大きい; small|小さい; team|チーム; large teams|大きなチーム; small teams|小さなチーム; user|利用者; new users|新しい利用者; experienced users|経験のある利用者; project|企画; city offices|都市のオフィス; rural offices|地方のオフィス; short projects|短期の企画; long projects|長期の企画", receptive="broadly speaking|大まかに言えば; with some caveats|いくつか条件付きで"),
    115: dict(new="capacity|対応力; risk|リスク; delivery risk|納品リスク", recycled="timing|タイミング|CORE-85; data|データ|CORE-85; delivery|配達|CORE-77; supplier|取引先|CORE-82; schedule|予定|CORE-67", assumed="cost|費用; record|記録; staff capacity|スタッフの対応力; reduce the risk|リスクを下げる; check the data|データを確認する; compare the suppliers|取引先を比較する; review the schedule|日程を見直す", receptive="factor|要因; the problem is|問題は; that still leaves|それでも残る"),
    116: dict(new="demand|需要; workload|作業量; doubled|2倍になった; got worse|悪化した; response time|応答時間; response times|応答時間", recycled="reliable|信頼できる|CORE-56", assumed="cost|費用; delay|遅れ; delays|遅れ; opposite|逆; available|対応できる; it's got worse|悪化している; it's become less reliable|信頼性が下がった; delays have increased|遅れが増えた; the workload has doubled|作業量が2倍になった; demand has gone up|需要が増えた; costs have gone up|費用が増えた; response times have increased|応答時間が延びた; fewer people are available|対応できる人が減った", receptive="far from it|とんでもない; not at all|まったく違う"),
    117: dict(new="worth it|価値がある; practical|現実的な; reliability|信頼性; long-term value|長期的な価値", recycled="timing|タイミング|CORE-85; reliable|信頼できる|CORE-56", assumed="cost|費用; costs too much|費用が高すぎる; plan|案; change|変更; decision|判断; it's worth it|価値がある; the plan is practical|案は現実的; the change has helped|変更は役立った; it costs too much|費用が高すぎる; the cost|費用; the timing|時期", receptive="all in all|総合すると; at the end of the day|結局のところ"),
    118: dict(new="cautious|慎重な; efficient|効率的な; rigid|厳格な; incomplete|不十分な; success|成功; progress|進歩", recycled="flexible|柔軟な|CORE-114", assumed="slow|遅い; simple|単純な; fair|公平な; result|結果; approval|承認; I think it's too slow|遅すぎると思う; I think it's too rigid|厳格すぎると思う; I think it's unclear|不明確だと思う; I think it's incomplete|不十分だと思う; a success|成功", receptive="hmm, maybe|うーん、そうかも; if you like|そう呼びたければ; reservation|異論"),
    119: dict(new="disagreed|意見が合わなかった; disappointing|残念な; discussion|話し合い", recycled="timing|タイミング|CORE-85", assumed="meeting|会議; project|企画; result|結果; experience|経験; difficult|大変な; disagree|意見が合わない; not go well|うまくいかない; it didn't go well|うまくいかなかった; the meeting was difficult|会議は大変だった; we didn't agree|意見が合わなかった; the result was disappointing|結果は残念だった; we disagreed|意見が合わなかった; the timing was wrong|時期が悪かった; the project needs more work|企画にはさらに作業が必要; the discussion ended early|話し合いが早く終わった", receptive="deliberately|意図的に; enough said|これで十分; read into that what you will|あとはご想像にお任せします; infer|察する"),
    120: dict(new="quote|見積もり", recycled="manager|上司|CORE-54; schedule|予定|CORE-67; figures|数字|CORE-108", assumed="ask|聞く; check|確認する; review|見直す; save|保存する; wait|待つ; copy|コピー; number|数字; file name|ファイル名; suggestion|提案; check that again|もう一度確認する; review the numbers|数字を見直す; save a copy|コピーを保存する; ask the manager|上司に聞く; asking her|彼女に聞く; checking the schedule|日程を確認する; getting another quote|別の見積もりを取る; checking the file name|ファイル名を確認する", receptive="reread|読み直す; overwrite|上書きする; no pressure|無理にとは言いません; up to you, of course|もちろん判断はお任せします; directive|指示; optional|任意の"),
    121: dict(new="details|詳細; topic|話題", recycled="prefer|〜のほうが好き|CORE-42; complaint|苦情|CORE-89; another time|別の機会|CORE-97", assumed="reason|理由; reasons|理由; decision|判断; situation|事情; what happened|何があったか; next step|次の段階; for now|今は; the details|詳細; the reasons|理由; the complaint|苦情; this topic|この話; the decision|その判断; the next step|次の段階; the contract discussion|契約の話", receptive="boundary|境界; long story|長い話; another time, maybe|また今度にしましょう; postpone|保留する"),
    122: dict(new="straightforward|単純明快な; framing|枠組み", recycled="issue|問題|CORE-82; the real question is|本当の問題は|CORE-103", assumed="question|問い; simple|単純な; clear|明確な; easy|簡単な; what i meant|言いたかったこと; how i'd put it|私ならこう言う; choice|選択; problem|問題; change|変化; what changed|何が変わったか; which option solves the problem|どの案が問題を解決するか; who benefits|誰に役立つか; what the evidence shows|事実が何を示すか; it's good overall|全体としてよい; it's bad overall|全体として悪い; it's clear|明確だ; it's unclear|不明確だ", receptive="premise|前提; it depends what you mean by|何を意味するかによる; let me back up|少し話を戻します"),
}


KNOWN_WORDS = {
    113: (("プロジェクト", "project"), ("デリバリー", "delivery"), ("プラン", "planning")),
    114: (("チーム", "team"), ("プロジェクト", "project"), ("ユーザー", "user")),
    115: (("データ", "data"), ("コスト", "cost"), ("スケジュール", "schedule")),
    116: (("コスト", "cost"), ("ディレイ", "delay"), ("リライアブル", "reliable")),
    117: (("プラン", "plan"), ("コスト", "cost"), ("タイミング", "timing")),
    118: (("フレキシブル", "flexible"), ("スロー", "slow"), ("フェア", "fair")),
    119: (("ミーティング", "meeting"), ("プロジェクト", "project"), ("タイミング", "timing")),
    120: (("マネージャー", "manager"), ("スケジュール", "schedule"), ("コピー", "copy")),
    121: (("プリファー", "prefer"), ("リーズン", "reason"), ("ステップ", "next step")),
    122: (("シンプル", "simple"), ("クリア", "clear"), ("チョイス", "choice")),
}


TRANSLATE_HINTS = {
    113: (("範囲を決める:scope", "担当:ownership", "意思決定:decisions", "優先事項:priorities"), ("問題:problem", "意思疎通:communication", "優先事項:priorities", "計画:planning")),
    114: (("チーム:team", "利用者:user", "地方の:rural", "企画:project"), ("複雑な:complicated", "割り切れる:clear-cut", "高い:expensive", "込み入った:nuanced")),
    115: (("費用:cost", "時期:timing", "対応力:capacity", "納品リスク:delivery risk"), ("リスク:risk", "データ:data", "取引先:supplier", "日程:schedule")),
    116: (("悪化した:got worse", "信頼できる:reliable", "遅れ:delay", "作業量:workload"), ("需要:demand", "費用:cost", "応答時間:response time", "対応できる:available")),
    117: (("価値がある:worth it", "現実的な:practical", "変更:change", "費用:cost"), ("費用:cost", "時期:timing", "信頼性:reliability", "長期的な価値:long-term value")),
    118: (("慎重な:cautious", "効率的な:efficient", "柔軟な:flexible", "不十分な:incomplete"), ("成功:success", "進歩:progress", "慎重な:cautious", "公平な:fair")),
    119: (("うまくいかない:not go well", "大変な:difficult", "意見が合わない:disagree", "残念な:disappointing"), ("意見が合わない:disagree", "時期:timing", "企画:project", "話し合い:discussion")),
    120: (("確認する:check", "見直す:review", "保存する:save", "上司:manager"), ("聞く:ask", "日程:schedule", "見積もり:quote", "ファイル名:file name")),
    121: (("詳細:details", "理由:reason", "苦情:complaint", "何があったか:what happened"), ("今は:for now", "話題:topic", "判断:decision", "次の段階:next step")),
    122: (("単純な:simple", "明確な:clear", "簡単な:easy", "単純明快な:straightforward"), ("問い:question", "言いたかったこと:what i meant", "論点:issue", "私ならこう言う:how i'd put it")),
}


OPEN_MENUS = {
    113: (("範囲を決める:scope", "担当:ownership", "優先事項:priorities"), ("意思疎通:communication", "計画:planning", "問題:problem")),
    114: (("大きなチーム:large teams", "小さなチーム:small teams", "新しい利用者:new users", "経験のある利用者:experienced users"), ("複雑な:complicated", "不確かな:uncertain", "柔軟な:flexible")),
    115: (("費用:cost", "時期:timing", "対応力:capacity", "納品リスク:delivery risk"), ("リスク:risk", "データ:data", "取引先:supplier", "日程:schedule")),
    116: (("悪化した:got worse", "遅れ:delays", "作業量:workload"), ("需要:demand", "費用:cost", "応答時間:response times")),
    117: (("価値がある:worth it", "現実的な:practical", "費用が高い:costs too much"), ("費用:cost", "時期:timing", "信頼性:reliability", "長期的な価値:long-term value")),
    118: (("慎重な:cautious", "効率的な:efficient", "厳格な:rigid", "遅い:slow"), ("成功:success", "進歩:progress", "公平な:fair")),
    119: (("うまくいかない:not go well", "大変な:difficult", "意見が合わない:disagree"), ("時期:timing", "企画:project", "話し合い:discussion")),
    120: (("確認する:check", "見直す:review", "保存する:save", "上司:manager"), ("聞く:ask", "日程:schedule", "見積もり:quote", "ファイル名:file name")),
    121: (("詳細:details", "理由:reasons", "苦情:complaint", "何があったか:what happened"), ("話題:topic", "判断:decision", "次の段階:next step")),
    122: (("単純な:simple", "明確な:clear", "簡単な:easy", "単純明快な:straightforward"), ("問い:question", "言いたかったこと:what i meant", "論点:issue", "私ならこう言う:how i'd put it")),
}


SUPPORT_EXPRESSIONS = {
    113: (("At root, this is an ownership problem.", "根本では、これは担当の問題です。"), ("We need to look at the bigger picture.", "全体像を見る必要があります。")),
    114: (("Broadly speaking, that is true.", "大まかに言えば、それは正しいです。"), ("I agree, with some caveats.", "いくつか条件付きで賛成です。")),
    115: (("The problem is the delivery risk.", "問題は納品リスクです。"), ("That still leaves the timing issue.", "それでも時期の問題が残ります。")),
    116: (("Far from it — demand has risen.", "とんでもありません。需要は増えています。"), ("No, not at all.", "いいえ、まったく違います。")),
    117: (("All in all, it worked well.", "総合すると、うまくいきました。"), ("At the end of the day, cost decides it.", "結局のところ、費用で決まります。")),
    118: (("Hmm, maybe — but I am not convinced.", "うーん、そうかもしれませんが、納得はしていません。"), ("You can call it progress, if you like.", "そう呼びたければ、進歩と呼べます。")),
    119: (("Enough said.", "これで十分です。"), ("Read into that what you will.", "あとはご想像にお任せします。")),
    120: (("No pressure.", "無理にとは言いません。"), ("It is up to you, of course.", "もちろん判断はお任せします。")),
    121: (("Long story.", "長い話です。"), ("Another time, maybe.", "また今度にしましょう。")),
    122: (("It depends what you mean by success.", "成功をどういう意味で使うかによります。"), ("Let me back up.", "少し話を戻します。")),
}


DIALOGUES = {
    113: dict(
        model=("Project lead", 1, 1, ("The handoff was missed again.", "また引き継ぎが抜けました。"), ("Do you think that explains the repeated delays too?", "それで繰り返す遅れも説明できると思いますか？"), ("Then let's map each handoff and owner.", "では、引き継ぎと担当を一つずつ整理しましょう。"), ("Good. Let's start with ownership.", "いいですね。まず担当から始めましょう。")),
        wild=("Volunteer lead", 3, 2, ("Three teams prepared the same material.", "3つのチームが同じ資料を準備していました。"), ("Does that point to a broader issue?", "それは、より広い問題を示していますか？"), ("I'll set one priority list for everyone.", "全員共通の優先順位表を一つ作ります。"), ("Great. That should prevent duplicate work.", "いいですね。それで重複作業を防げるはずです。"))),
    114: dict(
        model=("Consultant", 0, 0, ("One process should work for every team size.", "一つの手順が、どの規模のチームにも使えるはずです。"), ("What else makes the choice difficult?", "ほかに何が選択を難しくしますか？"), ("Then let's compare both team sizes separately.", "では、二つのチーム規模を分けて比べましょう。"), ("Agreed. That will give us a fair comparison.", "賛成です。それなら公平に比較できます。")),
        wild=("Trainer", 1, 0, ("The same training should suit every user.", "同じ研修がすべての利用者に合うはずです。"), ("So experience changes the answer?", "では、経験によって答えが変わりますか？"), ("I'll prepare two versions of the training.", "研修を2種類用意します。"), ("Good. Each group will get the right level.", "いいですね。それぞれに合うレベルになります。"))),
    115: dict(
        model=("Manager", 3, 0, ("The cheapest supplier will save us money.", "最も安い取引先なら費用を節約できます。"), ("What do we still need to do?", "それでも何をする必要がありますか？"), ("I'll get the delivery records for both suppliers.", "両方の取引先の納品記録を用意します。"), ("Good. I'll compare them before we decide.", "いいですね。決める前に比較します。")),
        wild=("Organizer", 2, 1, ("This plan needs fewer people, so it should be easier.", "この案は必要な人数が少ないので、簡単なはずです。"), ("What action still matters?", "それでも必要な対応は何ですか？"), ("I'll send you the latest data today.", "今日、最新のデータを送ります。"), ("Thanks. Then we can make a safer choice.", "ありがとう。それなら、より安全に選べます。"))),
    116: dict(
        model=("Support lead", 0, 0, ("Support requests seem to be falling now.", "問い合わせは今、減っているようです。"), ("What evidence points the other way?", "逆方向を示す根拠は何ですか？"), ("Then I'll add another person to the evening shift.", "では、夜の担当を一人増やします。"), ("Good. I'll plan for higher demand.", "いいですね。需要の増加を見込んで計画します。")),
        wild=("Coordinator", 2, 2, ("The new process was supposed to reduce delays.", "新しい手順で遅れが減るはずでした。"), ("So the response time proves the reverse?", "では、応答時間が逆を示していますか？"), ("I'll review where the extra time is going.", "増えた時間がどこにかかっているか確認します。"), ("Great. Then we can fix the real bottleneck.", "いいですね。それなら本当の詰まりを直せます。"))),
    117: dict(
        model=("Buyer", 0, 2, ("The reliable option costs more but lasts longer.", "信頼できる案は高いですが、長く使えます。"), ("What is the deciding factor for you?", "あなたにとっての決め手は何ですか？"), ("Then the reliable option sounds right.", "では、信頼できる案がよさそうですね。"), ("Agreed. Let's choose the reliable option.", "賛成です。信頼できるほうを選びましょう。")),
        wild=("Committee member", 1, 1, ("The plan is practical, but the timing is tight.", "その案は現実的ですが、時期が厳しいです。"), ("What does the decision come down to for you?", "あなたにとって判断の決め手は何ですか？"), ("Then let's move the date rather than reject the plan.", "では、案を退けずに日程を動かしましょう。"), ("Good. That keeps the useful part of the plan.", "いいですね。それなら案のよい部分を残せます。"))),
    118: dict(
        model=("Director", 0, 0, ("The delayed launch shows that we were cautious.", "公開を遅らせたのは慎重だった証拠です。"), ("Would you still call the pilot a success?", "それでも試行は成功と呼べますか？"), ("Fair point. Let's review retention, not just complaints.", "なるほど。苦情だけでなく継続率も見ましょう。"), ("Yes. That will give us a fuller result.", "はい。それなら、より全体的な結果が分かります。")),
        wild=("Editor", 1, 1, ("The extra approval step makes the process efficient.", "追加の承認手順で作業が効率的になります。"), ("Would you call the change progress?", "その変更を進歩と呼べますか？"), ("Then I'll compare speed and error rates.", "では、速さと誤りの割合を比べます。"), ("Good. That should test both interpretations.", "いいですね。それなら両方の見方を確かめられます。"))),
    119: dict(
        model=("Colleague", 0, 0, ("How did the client meeting go?", "顧客との会議はどうでしたか？"), ("Did you at least agree on the main point?", "少なくとも主要な点では合意しましたか？"), ("Understood. I won't press for details.", "分かりました。詳しくは聞きません。"), ("Thanks for understanding.", "理解してくれてありがとう。")),
        wild=("Friend", 2, 3, ("How was the group discussion?", "グループでの話し合いはどうでしたか？"), ("Is there anything else you want to say about it?", "ほかに何か言いたいことはありますか？"), ("That's enough. We can talk about something else.", "それで十分です。別の話をしましょう。"), ("Thanks. I'd like that.", "ありがとう。そうしたいです。"))),
    120: dict(
        model=("Colleague", 1, 0, ("Maya calculated this total, and I think it's ready to send.", "この合計はマヤが計算し、送れる状態だと思います。"), ("What should I do if the total still looks wrong?", "それでも合計がおかしければ、どうすればいいですか？"), ("Good idea. I'll ask Maya before sending it.", "いい考えです。送る前にマヤに聞きます。"), ("Great. She can confirm the figures.", "いいですね。マヤなら数字を確認できます。")),
        wild=("Team lead", 2, 3, ("I'm about to overwrite the only copy.", "唯一のコピーを上書き保存しようとしています。"), ("What else might be worth doing first?", "ほかに先に何をする価値がありますか？"), ("Right. I'll save a backup before I continue.", "そうですね。続ける前にバックアップを保存します。"), ("Good. Then the original stays safe.", "いいですね。それなら元のものが安全です。"))),
    121: dict(
        model=("Colleague", 0, 0, ("Why did the contract discussion end early?", "契約の話し合いはなぜ早く終わったのですか？"), ("Understood. Do you want to discuss the next step now?", "分かりました。次の段階は今話しますか？"), ("Of course. We can return to it tomorrow.", "もちろんです。明日また話せます。"), ("Thanks. I appreciate that.", "ありがとう。助かります。")),
        wild=("Friend", 3, 1, ("Do you want to explain what happened?", "何があったか説明したいですか？"), ("Should we keep talking about that topic?", "その話題を続けますか？"), ("No problem. Let's talk about something else.", "大丈夫です。別の話をしましょう。"), ("Thank you. That feels better.", "ありがとう。そのほうが楽です。"))),
    122: dict(
        model=("Reviewer", 0, 0, ("So was the pilot simply a success or a failure?", "では、試行は単純に成功か失敗のどちらですか？"), ("Then is the low response rate the problem?", "では、回答率が低いことが問題ですか？"), ("What should we ask instead?", "代わりに何を問うべきですか？"), ("The real question is what changed.", "本当に問うべきなのは、何が変わったかです。")),
        wild=("Host", 1, 1, ("Is this choice simply clear or unclear?", "この選択は単純に明確か不明確のどちらですか？"), ("Then is clarity the real issue?", "では、明確さが本当の論点ですか？"), ("What would be a better question?", "もっとよい問いは何ですか？"), ("Let's ask which option solves the problem.", "どの選択肢が問題を解決するかを問いましょう。"))),
}


LIVE_SCENES = {
    113: (("text", "other", "Tutor", "What recurring problem do you notice at work or in daily life, and what is behind it?", "仕事や日常生活で繰り返す問題は何ですか？その原因は何だと思いますか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What recurring problem do you notice, and what is behind it?", "先生はどんな繰り返す問題に気づきますか？その原因は何だと思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    114: (("text", "other", "Tutor", "Do you think working from home is better for everyone? Why or why not?", "在宅勤務は全員にとってよいと思いますか？なぜそう思いますか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "Who do you think working from home is best for?", "先生は、在宅勤務はどんな人に一番向いていると思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    115: (("text", "other", "Tutor", "When people make a quick decision, what important factor do they often miss?", "急いで決めるとき、人はどんな大切な要素を見落としやすいですか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What factor do you think people overlook most often?", "先生は、人が一番見落としやすい要素は何だと思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    116: (("text", "other", "Tutor", "What is something people say has improved, but you think has actually got worse?", "よくなったと言われるけれど、実際は悪くなったと思うものは何ですか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What do you think has got worse rather than better?", "先生は、よくなるどころか悪くなったものは何だと思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    117: (("text", "other", "Tutor", "What recent decision had both clear advantages and disadvantages? What mattered most in the end?", "最近、明確な長所と短所の両方があった判断は何ですか？最後の決め手は何でしたか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What recent decision did you weigh carefully, and what mattered most?", "先生が最近慎重に考えた判断と、一番大切だったことは何ですか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    118: (("text", "other", "Tutor", "Do extra approval steps usually make work safer or just slower?", "承認手順を増やすと、仕事はより安全になりますか？それとも遅くなるだけですか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "How do extra approval steps affect your work?", "先生の仕事では、承認手順を増やすとどんな影響がありますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    119: (("text", "other", "Tutor", "What's a trip, meal, or purchase that didn't go as planned but makes a good story now?", "予定どおりにいかなかったけれど、今では面白い話になった旅行・食事・買い物はありますか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What experience went badly but makes a good story now?", "先生は、うまくいかなかったけれど今では面白い話になった経験がありますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    120: (("text", "other", "Tutor", "What do you always double-check before sending or submitting something important?", "大切なものを送ったり提出したりする前に、必ず確認することは何ですか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What do you always check before you send something important?", "先生は大切なものを送る前に、必ず何を確認しますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    121: (("text", "other", "Tutor", "What topic do you think people are sometimes too curious about?", "人がときどき知りたがりすぎる話題は何だと思いますか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What topic do you think people should be more careful about asking about?", "先生は、どんな話題について聞くときに、もっと気をつけるべきだと思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
    122: (("text", "other", "Tutor", "Is working from home simply good or bad, or is that the wrong question?", "在宅勤務は単純によいか悪いかで決められますか？それとも、その問い方自体が違いますか？"), ("input", "me", "Me", "Student's answer", "自分の本当の答え"), ("text", "me", "Me", "What do you think the more useful question is?", "先生は、もっと役に立つ問いは何だと思いますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え")),
}


LIVE_HINTS = {
    113: {1: (
        ("The underlying issue is ___", "根本的な問題", ("担当が不明確:unclear ownership", "優先事項の衝突:conflicting priorities", "計画不足:weak planning")),
        ("It's symptomatic of ___", "何の表れか", ("意思疎通不足:poor communication", "優先事項が不明確:unclear priorities", "より大きな問題:a bigger problem")),
    )},
    114: {1: (
        ("true for ___", "当てはまる集団", ("大きなチーム:large teams", "新しい利用者:new users", "都市のオフィス:city offices", "短期の企画:short projects")),
        ("but not for ___", "当てはまらない集団", ("小さなチーム:small teams", "経験のある利用者:experienced users", "地方のオフィス:rural offices", "長期の企画:long projects")),
        ("more ___ than that", "よりどうなのか", ("複雑な:complicated", "高い:expensive", "不確かな:uncertain", "柔軟な:flexible")),
    )},
    115: {1: (
        ("doesn't account for ___", "見落としている要因", ("費用:cost", "時期:timing", "スタッフの対応力:staff capacity", "納品リスク:delivery risk")),
        ("still need to ___", "それでも必要な対応", ("リスクを下げる:reduce the risk", "データを確認する:check the data", "取引先を比較する:compare the suppliers", "日程を見直す:review the schedule")),
    )},
    116: {1: (
        ("If anything, ___", "むしろどうなのか", ("悪化している:it's got worse", "信頼性が下がった:it's become less reliable", "遅れが増えた:delays have increased", "作業量が2倍になった:the workload has doubled")),
        ("It's actually the opposite: ___", "逆だと示す事実", ("需要が増えた:demand has gone up", "費用が増えた:costs have gone up", "応答時間が延びた:response times have increased", "対応できる人が減った:fewer people are available")),
    )},
    117: {1: (
        ("Overall, I'd say ___", "総合的な判断", ("価値がある:it's worth it", "案は現実的だ:the plan is practical", "変更は役立った:the change has helped", "費用が高すぎる:it costs too much")),
        ("What it comes down to for me is ___", "自分の決め手", ("費用:the cost", "時期:the timing", "信頼性:reliability", "長期的な価値:long-term value")),
    )},
    118: {1: (
        ("see it as ___", "可能な見方", ("慎重な:cautious", "効率的な:efficient", "柔軟な:flexible", "単純な:simple")),
        ("but ___", "自分の違う見方", ("遅すぎると思う:I think it's too slow", "厳格すぎると思う:I think it's too rigid", "不明確だと思う:I think it's unclear", "不十分だと思う:I think it's incomplete")),
        ("call it ___, though", "少し距離を置く呼び方", ("成功:a success", "進歩:progress", "慎重:cautious", "公平:fair")),
    )},
    119: {1: (
        ("Let's just say ___", "短いまとめ", ("うまくいかなかった:it didn't go well", "会議は大変だった:the meeting was difficult", "意見が合わなかった:we didn't agree", "結果は残念だった:the result was disappointing")),
        ("All I'll say is that ___", "伝えてよい一つの事実", ("意見が合わなかった:we disagreed", "時期が悪かった:the timing was wrong", "企画にはさらに作業が必要:the project needs more work", "話し合いが早く終わった:the discussion ended early")),
    )},
    120: {1: (
        ("You might want to ___", "やわらかな指示", ("もう一度確認する:check that again", "数字を見直す:review the numbers", "コピーを保存する:save a copy", "上司に聞く:ask the manager")),
        ("It might be worth ___", "検討する価値のある行動", ("彼女に聞く:asking her", "日程を確認する:checking the schedule", "別の見積もりを取る:getting another quote", "ファイル名を確認する:checking the file name")),
    )},
    121: {1: (
        ("go into ___", "詳しく話さない内容", ("詳細:the details", "理由:the reasons", "苦情:the complaint", "何があったか:what happened")),
        ("leave ___ for now", "今は置いておく話題", ("この話:this topic", "その判断:the decision", "次の段階:the next step", "契約の話:the contract discussion")),
    )},
    122: {1: (
        ("It's not that ___, though", "単純化を退ける語", ("単純な:simple", "明確な:clear", "簡単な:easy", "単純明快な:straightforward")),
        ("The real question is ___", "本当に問うこと", ("何が変わったか:what changed", "どの案が問題を解決するか:which option solves the problem", "誰に役立つか:who benefits", "事実が何を示すか:what the evidence shows")),
        ("The simple framing works: ___", "単純な答えでよい場合", ("全体としてよい:it's good overall", "全体として悪い:it's bad overall", "明確だ:it's clear", "不明確だ:it's unclear")),
    )},
}


# Each live hint group has an independent grammatical frame.  Tests rebuild
# every chip through these frames so a menu cannot silently mix nouns, verb
# phrases, and clauses that do not fit the learner's visible slot.
LIVE_SLOT_FRAMES = {
    113: (("The underlying issue is ", "."), ("It's symptomatic of ", ".")),
    114: (("That may be true for ", "."), ("That may not be true for ", "."), ("It's more ", " than that.")),
    115: (("That doesn't account for ", "."), ("Even so, we still need to ", ".")),
    116: (("If anything, ", "."), ("It's actually the opposite: ", ".")),
    117: (("Overall, I'd say ", "."), ("What it comes down to for me is ", ".")),
    118: (("You could see it as ", "."), ("", "."), ("I can see why you'd call it ", ", though.")),
    119: (("Let's just say ", "."), ("All I'll say is that ", ".")),
    120: (("You might want to ", "."), ("It might be worth ", ".")),
    121: (("I'd rather not go into ", "."), ("Can we leave ", " for now?")),
    122: (("It's not that ", ", though."), ("The real question is ", "."), ("I think the simple framing works: ", ".")),
}

# Free Talk is a real reciprocal conversation, not another controlled
# production task.  Keep the earlier lexical menus in source for the controlled
# write pages, but do not place pattern-shaped hint menus inside Free Talk.
LIVE_HINTS = {number: {} for number in NUMBERS}
LIVE_SLOT_FRAMES = {number: () for number in NUMBERS}

# A choice page earns its place only when both alternatives can be correct in
# the activity.  These advanced frames do not provide that contrast; repeating
# the same answer four times adds no diagnostic value.  CORE-122 part 2 is the
# one retained scope contrast (not really / really not).
OMIT_CHOICES = {number: (1, 2) for number in range(113, 122)} | {122: (1,)}

WRITE_FRAMES = {
    113: ("The underlying issue is ___", "It's symptomatic of ___"),
    114: ("That may be true for ___, but not for ___", "It's more ___ than that"),
    115: ("That's true, but it doesn't account for ___", "Even so, we still need to ___"),
    116: ("If anything, ___", "It's actually the opposite: ___"),
    117: ("Overall, I'd say ___", "What it comes down to for me is ___"),
    118: ("You could see it as ___, but ___", "I can see why you'd call it ___, though"),
    119: ("Let's just say ___", "All I'll say is that ___"),
    120: ("You might want to ___", "It might be worth ___ing"),
    121: ("I'd rather not go into ___", "Can we leave ___ for now?"),
    122: ("It's not that ___, though", "That's not really the ___"),
}

FILL_HINTS = {(114, 2): TRANSLATE_HINTS[114][1]}


TRANSFER_SCENES = {
    113: "volunteer material duplication", 114: "training for new and experienced users",
    115: "event staffing and data", 116: "process delays and response time",
    117: "committee plan timing", 118: "editorial approval process",
    119: "private group discussion", 120: "protecting a sole file copy",
    121: "friend sets a private boundary", 122: "host reframes a binary choice",
}


BRIEF_PRODUCTION_MODELS = {
    number: (core.strip_marks(LESSONS[number]["p1"][0][0]), core.strip_marks(LESSONS[number]["p2"][0][0]))
    for number in NUMBERS
}


THREE_CHIP_EXCEPTIONS = {
    (113, 2): "The subject, fixed symptomatic-of frame, and broader problem are three honest units.",
    (116, 1): "The exact model must keep it's got worse intact, leaving only two honest units, so reorder is omitted.",
    (116, 2): "The reversal frame, evidence subject, and complete predicate are three honest units.",
    (117, 1): "Overall, the stance frame, and the complete conclusion are three discourse units.",
    (119, 1): "The exact brief model has only a restraint frame and one complete limited clause, so reorder is omitted.",
    (121, 1): "The preference frame, phrasal verb, and protected topic are three honest units.",
    (122, 1): "The subject, complete softened description, and final though are three honest units.",
    (122, 2): "The subject, soft negation, and proposed frame noun are three honest units.",
}


SPIRAL_MARKERS = {
    113: (("ART-02", "transfer"),),
    114: (("NUM-01", "transfer"),),
    116: (("PERF-01", "transfer"),),
    118: (("NEGQ-01", "transfer"), ("REPORT-01", "transfer")),
    119: (("REPORT-01", "transfer"),),
    120: (("MODAL-01", "transfer"), ("POLITE-01", "transfer")),
    121: (("PREP-01", "transfer"), ("POLITE-01", "transfer")),
}


SPIRAL_CHOICES = {
    (113, "ART-02"): choices(
        ("共有済みの問題", "We discussed ", "the issue", "an issue", " yesterday."),
        ("初めて出す問題", "This may reveal ", "a problem", "the problem", " elsewhere."),
        ("共有済みの全体像", "Let's return to ", "the bigger picture", "a bigger picture", "."),
        ("一般的な兆候", "A delay can be ", "a symptom", "the symptom", "."),
    ),
    (114, "NUM-01"): choices(
        ("複数のチーム", "Large ", "teams", "team", " may need it."),
        ("複数の利用者", "New ", "users", "user", " may need help."),
        ("複数のオフィス", "Rural ", "offices", "office", " differ."),
        ("複数の企画", "Long ", "projects", "project", " take time."),
    ),
    (116, "PERF-01"): choices(
        ("今に関係する変化", "Demand ", "has gone", "went", " up."),
        ("終わった過去の時", "Demand ", "went", "has gone", " up yesterday."),
        ("今までの変化", "Response times ", "have", "did", " increased."),
        ("特定の過去", "Costs ", "increased", "have increased", " last year."),
    ),
    (118, "NEGQ-01"): choices(
        ("事実：遅すぎる", "Isn't it too slow? — ", "Yes, it is", "No, it is", "."),
        ("事実：遅すぎない", "Isn't it too slow? — ", "No, it isn't", "Yes, it isn't", "."),
        ("事実：成功だった", "Wasn't it a success? — ", "Yes, it was", "No, it was", "."),
        ("事実：成功ではない", "Wasn't it a success? — ", "No, it wasn't", "Yes, it wasn't", "."),
    ),
    (118, "REPORT-01"): choices(
        ("彼女は成功だと言った。", "She ", "said", "told", " it was a success."),
        ("彼女は私に成功だと伝えた。", "She ", "told me", "said me", " it was a success."),
        ("彼は遅いと言った。", "He ", "said", "told", " it was slow."),
        ("彼は私に遅いと伝えた。", "He ", "told me", "said me", " it was slow."),
    ),
    (119, "REPORT-01"): choices(
        ("彼女は意見が合わなかったと言った。", "She ", "said", "told", " they had disagreed."),
        ("彼女は私に意見が合わなかったと伝えた。", "She ", "told me", "said me", " they had disagreed."),
        ("彼は会議が大変だったと言った。", "He ", "said", "told", " the meeting had been difficult."),
        ("彼は私に会議が大変だったと伝えた。", "He ", "told me", "said me", " the meeting had been difficult."),
    ),
    (120, "MODAL-01"): choices(
        ("might の後ろ", "You might ", "check", "to check", " it."),
        ("could の後ろ", "You could ", "ask", "to ask", " her."),
        ("should の後ろ", "You should ", "save", "to save", " a copy."),
        ("can の後ろ", "You can ", "wait", "to wait", " a day."),
    ),
    (120, "POLITE-01"): choices(
        ("やわらかな指示", "You ", "might want to", "must", " check that."),
        ("可能な提案", "You ", "could", "have to", " ask her."),
        ("丁寧な依頼", "", "Could you", "You must", " review this?"),
        ("検討を勧める", "It ", "might be worth", "must", " waiting."),
    ),
    (121, "PREP-01"): choices(
        ("詳細に触れる", "go ", "into", "in", " the details"),
        ("今は置いておく", "leave it ", "for", "to", " now"),
        ("苦情に触れる", "go ", "into", "at", " the complaint"),
        ("今は話題を置く", "leave the topic ", "for", "in", " now"),
    ),
    (121, "POLITE-01"): choices(
        ("丁寧な境界", "", "I'd rather not", "I refuse to", " discuss it."),
        ("今だけ保留", "", "Can we leave", "Stop", " this for now?"),
        ("丁寧に断る", "I'd prefer ", "not to", "not", " explain."),
        ("別の時を提案", "", "Another time, maybe", "No way", "."),
    ),
}


DIALOGUE_SEMANTIC_LEDGER = {
    113: dict(model=("lead names repeat handoff miss", "learner abstracts ownership", "lead links repeat delays", "learner links communication", "lead proposes ownership map", "learner starts with ownership"), wild=("lead names duplicate work", "learner abstracts priorities", "lead asks broader issue", "learner links unclear priorities", "lead sets shared list", "learner predicts no duplication")),
    114: dict(model=("consultant makes universal process claim", "learner limits by team size", "consultant asks complexity", "learner rejects simplicity", "consultant proposes separate comparison", "learner accepts fair test"), wild=("trainer makes universal training claim", "learner limits by experience", "trainer checks consequence", "learner names added complexity", "trainer prepares two versions", "learner predicts fit")),
    115: dict(model=("manager values cheapest supplier", "learner concedes and adds delivery risk", "manager asks remaining action", "learner preserves risk reduction", "manager gets records", "learner commits comparison"), wild=("organizer values low staffing", "learner adds capacity", "organizer asks action", "learner preserves data check", "organizer sends data", "learner predicts safer choice")),
    116: dict(model=("lead assumes demand fall", "learner reverses trend", "lead asks evidence", "learner names demand rise", "lead adds coverage", "learner plans for demand"), wild=("coordinator recalls intended delay reduction", "learner reports increased delays", "coordinator checks response evidence", "learner names response increase", "coordinator investigates", "learner identifies bottleneck outcome")),
    117: dict(model=("buyer weighs cost and durability", "learner concludes worth it", "buyer asks factor", "learner names reliability", "buyer recommends option", "learner chooses"), wild=("committee weighs practicality and timing", "learner concludes practical", "committee asks factor", "learner names timing", "committee moves date", "learner preserves plan")),
    118: dict(model=("director labels delay cautious", "learner acknowledges but objects", "director asks success label", "learner acknowledges with reservation", "director broadens evidence", "learner confirms fuller result"), wild=("editor labels approval efficient", "learner acknowledges but calls rigid", "editor asks progress label", "learner acknowledges reservation", "editor compares measures", "learner validates test")),
    119: dict(model=("colleague asks client meeting", "learner gives limited summary", "colleague asks agreement", "learner offers one fact", "colleague respects limit", "learner thanks"), wild=("friend asks group discussion", "learner gives limited summary", "friend asks more", "learner offers one fact", "friend changes topic", "learner accepts")),
    120: dict(model=("colleague plans to send Maya's total", "learner gives softened check instruction", "colleague asks next step", "learner recommends asking Maya", "colleague accepts", "learner says Maya can confirm figures"), wild=("lead risks sole copy", "learner instructs backup", "lead asks extra action", "learner recommends checking file name", "lead saves backup", "learner confirms safety")),
    121: dict(model=("colleague asks contract cause", "learner declines detail", "colleague asks next step", "learner postpones topic", "colleague accepts tomorrow", "learner appreciates"), wild=("friend asks private event", "learner declines situation", "friend asks continue", "learner leaves topic", "friend changes topic", "learner feels better")),
    122: dict(model=("reviewer forces success failure", "learner rejects simplicity", "reviewer proposes response rate", "learner rejects question", "reviewer asks replacement", "learner reframes as change"), wild=("host forces clear unclear", "learner rejects simplicity", "host proposes clarity", "learner rejects issue", "host asks better question", "learner reframes as solution")),
}


# The operating script names the tutor's actual role in both languages.  The
# model/replay and transfer scenes deliberately use different counterparts, so
# one generic role label cannot accurately serve both pages.
ROLE_JA = {
    113: ("プロジェクトリーダー", "ボランティアのリーダー"),
    114: ("コンサルタント", "研修担当者"),
    115: ("上司", "主催者"),
    116: ("サポートチームのリーダー", "調整担当者"),
    117: ("購買担当者", "委員"),
    118: ("責任者", "編集者"),
    119: ("同僚", "友人"),
    120: ("同僚", "チームリーダー"),
    121: ("同僚", "友人"),
    122: ("レビュー担当者", "司会者"),
}


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{value}\2', head, count=1,
        )
    return head


def hint_html(items):
    return '<span class="hint">' + "".join(
        f'<span class="hint-chip">{core.esc(item)}</span>' for item in items
    ) + '</span>'


def live_hints_html(groups):
    if not groups:
        return ""
    rendered = []
    for english_label, japanese_label, items in groups:
        rendered.append(
            '<div class="slot-hint-group">'
            f'<span class="slot-hint-label">{core.esc(english_label)}'
            f'<span class="task">{core.esc(japanese_label)}</span></span>'
            f'{hint_html(items)}</div>'
        )
    return '<div class="slot-hints">' + "".join(rendered) + '</div>'


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


def spiral_page(number, spiral_id, level):
    page_id = f"spiral-{spiral_id.casefold()}"
    page = core.choose_words(
        page_id, "Retrieve an earlier contrast", "前の対比を思い出そう",
        "Choose the form that matches the stated meaning.",
        "書かれた意味に合う形を選びましょう。",
        SPIRAL_CHOICES[(number, spiral_id)],
    )
    return page.replace(
        f'data-page-id="{page_id}"',
        f'data-page-id="{page_id}" data-spiral-id="{spiral_id}" data-spiral-level="{level}"', 1,
    )


def translate_page(number, part, pattern):
    blocks = []
    for index, ((english, japanese, _), hint) in enumerate(
        zip(pattern, TRANSLATE_HINTS[number][part - 1], strict=True)
    ):
        blocks.append(
            '<div class="task-block"><div class="answer-box">'
            f'<span class="answer-label">{core.esc(core.strip_marks(japanese))}</span>'
            '<span class="answer-space as-input">'
            f'<textarea class="space-input" data-sync-id="p{part}-translate-{index}" '
            f'data-answer="{core.esc(core.strip_marks(english))}" autocomplete="off" '
            'spellcheck="false" rows="2"></textarea></span>'
            + hint_html((hint,)) + '</div></div>'
        )
    rendered = core.section(
        f"p{part}-translate", "Say it in English", "英語にしよう",
        '<p class="section-subtitle"><span class="ko">Read the Japanese, then say it in English.</span>'
        '<span class="ja">日本語を見て、英語で言ってみましょう。</span></p>'
        '<div class="tutor-note">Type the learner\'s complete English sentence exactly as they say it.</div>'
        + "".join(blocks),
    )
    return rendered.replace(
        f'data-page-id="p{part}-translate"',
        f'data-page-id="p{part}-translate" data-scaffolding-contract="target-v2" '
        'data-support-stage="supported"',
        1,
    )


def write_page(number, part):
    prompt_en, prompt_ja = SPECS[number]["writes"][part - 1]
    frame = WRITE_FRAMES[number][part - 1]
    prompt_en = f'Now use “{frame}” to {prompt_en[0].lower() + prompt_en[1:]}'
    prompt_ja = f'では、「{frame}」を使って、{prompt_ja}'
    return core.section(
        f"p{part}-write", "Make it yours", "自分の文にしよう",
        f'<p class="section-subtitle"><span class="ko">{core.esc(prompt_en)}</span>'
        f'<span class="ja">{core.esc(prompt_ja)}</span></p>'
        '<div class="tutor-note">Let the learner answer aloud before you capture it. React first, then add only a useful correction.</div>'
        + core.feedback_compose(f"p{part}-write", hint_html(OPEN_MENUS[number][part - 1])),
    )


def live_page(number):
    turns = []
    for index, (kind, side, speaker, english, japanese) in enumerate(LIVE_SCENES[number]):
        avatar = core.live_avatar(speaker)
        bubble = "bubble me" if side == "me" else "bubble"
        if kind == "text":
            turns.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}">'
                f'<span class="korean">{core.esc(english)}</span>'
                f'<span class="translation">{core.esc(japanese)}</span></div></div>'
            )
            continue
        label = "Tutor's answer" if side == "other" else "Student's answer"
        label_ja = "先生の本当の短い答え" if side == "other" else "自分の本当の答え"
        hints = live_hints_html(LIVE_HINTS[number].get(index, ())) if side == "me" else ""
        turns.append(
            f'<div class="turn {side}">{avatar}<div class="{bubble}"><div class="answer-box tall">'
            f'<span class="answer-label">{core.esc(label)}<span class="task">{core.esc(label_ja)}</span></span>'
            '<span class="answer-space as-input">'
            f'<textarea class="free-input" data-sync-id="live-{index}" rows="2" '
            f'spellcheck="false" maxlength="2000"></textarea></span>{hints}</div></div></div>'
        )
    return core.section(
        "p3-freetalk", "Your real answer", "自分の答え",
        '<p class="section-subtitle"><span class="ko">Let\'s talk about this topic. Answer my question, then ask me too.</span>'
        '<span class="ja">この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。</span></p>'
        '<div class="tutor-note">React naturally and follow the most interesting detail. Use today\'s pattern only if it fits.</div>'
        '<div class="dialogue">' + "".join(turns) + '</div>',
    )


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def growing_sentence_inputs(page):
    """Keep every learner-produced phrase visible instead of horizontally scrolling."""
    page = re.sub(
        r'<input class="space-input" type="text"([^>]*)>',
        r'<textarea class="space-input"\1 rows="2"></textarea>',
        page,
    )
    return re.sub(
        r'<input class="slot-input" type="text"([^>]*)>',
        r'<textarea class="slot-input phrase-input"\1 rows="1"></textarea>',
        page,
    )


def add_fill_hints(page, hints):
    """Support the one fill whose target intentionally includes changing vocabulary."""
    fragments = page.split('<div class="task-block">')
    if len(fragments) - 1 != len(hints):
        raise ValueError("fill hint count must match the rendered task blocks")
    rendered = [fragments[0]]
    for fragment, hint in zip(fragments[1:], hints, strict=True):
        rendered.append(
            '<div class="task-block">'
            + fragment.replace('</div></div>', hint_html((hint,)) + '</div></div>', 1)
        )
    return "".join(rendered)


def customize_pages(number, data, pages):
    replacements = {
        "words-you-know": known_page(number),
        "p1-translate": translate_page(number, 1, data["p1"]),
        "p2-translate": translate_page(number, 2, data["p2"]),
        "p1-write": write_page(number, 1),
        "p2-write": write_page(number, 2),
        "p3-freetalk": live_page(number),
    }
    omitted = {f"p{part}-reorder" for part in data.get("omit_reorder", ())}
    omitted |= {f"p{part}-choose" for part in OMIT_CHOICES[number]}
    result = []
    for page in pages:
        page = growing_sentence_inputs(page)
        pid = page_id(page)
        if pid in {"p3-model", "p3-complete"}:
            page = page.replace("私は相手役をします。", f"私は{ROLE_JA[number][0]}役をします。", 1)
        elif pid == "in-the-wild":
            page = page.replace("私は相手役をします。", f"私は{ROLE_JA[number][1]}役をします。", 1)
        for part in (1, 2):
            if pid == f"p{part}-fill" and (number, part) in FILL_HINTS:
                page = add_fill_hints(page, FILL_HINTS[number, part])
        if pid in omitted:
            continue
        if pid == "part3-intro":
            result.append(support_page(number))
            result.extend(
                spiral_page(number, spiral_id, level)
                for spiral_id, level in SPIRAL_MARKERS.get(number, ())
            )
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
    head = new_lesson.retarget(
        head, review_id=f"CORE-{number}", lesson_id=slug, level="C1",
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
        ("live hints", LIVE_HINTS), ("live slot frames", LIVE_SLOT_FRAMES),
        ("transfer scenes", TRANSFER_SCENES),
        ("brief models", BRIEF_PRODUCTION_MODELS),
        ("dialogue ledger", DIALOGUE_SEMANTIC_LEDGER),
        ("role labels", ROLE_JA),
    ):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-113--122")


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
        print(f"wrote {out.relative_to(ROOT)}")
    print("10 Core Advanced Stance decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
