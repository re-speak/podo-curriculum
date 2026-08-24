#!/usr/bin/env python3
"""Generate CTX49-60, the final two Contextual Business courses."""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_contextual_complex_workplace_batch as renderer
import generate_core_course_batch as core
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/2-contextual-english"
COURSES = {
    range(49, 55): ("ctx-business-negotiation-diplomacy", "B2", "BUSINESS ENGLISH", "Negotiator", "交渉を進める担当者"),
    range(55, 61): ("ctx-business-leadership-high-stakes", "C1", "BUSINESS ENGLISH", "Leader", "判断を伝えるリーダー"),
}


def rows(*items):
    return items


def pattern(*, bridge, meaning, rows_, rule, write, omit_rule=False, omit_reorder=False):
    return renderer.pattern(
        bridge=bridge,
        meaning=meaning,
        rows_=rows_,
        rule=rule,
        write=write,
        omit_rule=omit_rule,
        omit_reorder=omit_reorder,
    )


def rule(title, title_ja, explain, explain_ja, formula, job, job_ja, examples):
    return (title, title_ja, explain, explain_ja, formula, job, job_ja, examples)


def receptive(*items):
    return items


def live(prompt, prompt_ja, scaffold, scaffold_ja, ask, ask_ja):
    return (prompt, prompt_ja, scaffold, scaffold_ja, ask, ask_ja)


def concise_lesson(*, slug, title, ko, ja, role, scene, scene_ja, situation, goal, expressions,
                   p1_rows, p1_bridge, p1_meaning, p1_rule, p1_write,
                   p2_rows, p2_bridge, p2_meaning, p2_rule, p2_write,
                   scene_turns, receptive_, live_, tip, transfer_title, transfer_ja,
                   transfer_role, transfer_turns, vocab, p1_omit_rule=False,
                   p1_omit_reorder=False, p2_omit_rule=False, p2_omit_reorder=False):
    """Keep later specifications compact without hiding any learner-facing copy."""
    return dict(
        slug=slug, title=title, ko=ko, ja=ja, role=role, scene=scene, scene_ja=scene_ja,
        situation=situation, goal=goal, expressions=expressions,
        p1=pattern(bridge=p1_bridge, meaning=p1_meaning, rows_=p1_rows, rule=p1_rule,
                   write=p1_write, omit_rule=p1_omit_rule, omit_reorder=p1_omit_reorder),
        p2=pattern(bridge=p2_bridge, meaning=p2_meaning, rows_=p2_rows, rule=p2_rule,
                   write=p2_write, omit_rule=p2_omit_rule, omit_reorder=p2_omit_reorder),
        scene_turns=scene_turns, receptive=receptive_, live=live_, tip=tip,
        transfer_title=transfer_title, transfer_ja=transfer_ja, transfer_role=transfer_role,
        transfer_turns=transfer_turns, vocab=vocab,
    )


LESSONS = {
    49: dict(
        slug="reframe-a-problem-more-accurately", title="Reframe a problem more accurately",
        ko="문제를 더 정확하게 다시 규정하기", ja="問題をより正確に捉え直す",
        role="Partner", scene="Correcting an exaggerated description in a partner meeting",
        scene_ja="パートナー会議で大げさな表現を修正する場面",
        situation="短い遅れをプロジェクト全体の失敗と決めつけず、影響を認めながら、より正確な問題の捉え方に言い換えます。",
        goal=("Replace an exaggerated label with a more accurate description without dismissing the impact.", "影響を軽視せず、大げさな決めつけをより正確な表現に置き換えましょう。"),
        expressions=(("strictly speaking", "厳密に言えば"), ("more accurately", "より正確には")),
        p1=pattern(
            bridge="まず、二つの捉え方を対比して、より正確なほうを示します。",
            meaning=("Use this contrast to replace an overstated label with a more accurate one.", "大げさな表現を、より正確な表現に置き換える対比です。"),
            rows_=rows(
                ("{t}It's not so much{/t} a failure {t}as{/t} a delay.", "失敗{t}というより{/t}、{t}むしろ{/t}遅れです。", "It's not so much|a failure|as a delay."),
                ("{t}It's not so much{/t} resistance {t}as{/t} uncertainty.", "反対{t}というより{/t}、{t}むしろ{/t}不確かさです。", "It's not so much|resistance|as uncertainty."),
                ("{t}It's not so much{/t} a cost problem {t}as{/t} a timing problem.", "費用の問題{t}というより{/t}、{t}むしろ{/t}時期の問題です。", "It's not so much|a cost problem|as a timing problem."),
                ("{t}It's not so much{/t} a refusal {t}as{/t} a request for evidence.", "拒否{t}というより{/t}、{t}むしろ{/t}根拠を求めているのです。", "It's not so much|a refusal|as a request for evidence."),
            ),
            rule=rule("Put the rejected label before “as”", "退ける表現を as の前に", "Name the less accurate label first and the better description last.", "正確さの低い表現を先に、よりよい説明を最後に置きます。", "not so much + first label + as + better label", "Correct the framing", "捉え方を修正", ("failure · as a delay", "resistance · as uncertainty")),
            write=("Which exaggerated label would you replace, and with what?", "どの大げさな表現を、何に置き換えますか？"),
        ),
        p2=pattern(
            bridge="次に、自分ならどう呼ぶかを示し、極端な表現を避けます。",
            meaning=("Use this to offer your own more measured label for the situation.", "状況をより穏当で正確な言葉で呼び直す表現です。"),
            rows_=rows(
                ("{t}I'd call it{/t} a setback {t}rather than{/t} a fundamental problem.", "根本的な問題{t}というより{/t}、私なら後退{t}と呼びます{/t}。", "I'd call it|a setback|rather than|a fundamental problem."),
                ("{t}I'd call it{/t} a warning {t}rather than{/t} a crisis.", "危機{t}というより{/t}、私なら警告{t}と呼びます{/t}。", "I'd call it|a warning|rather than|a crisis."),
                ("{t}I'd call it{/t} a revision {t}rather than{/t} a reversal.", "方針転換{t}というより{/t}、私なら修正{t}と呼びます{/t}。", "I'd call it|a revision|rather than|a reversal."),
                ("{t}I'd call it{/t} a constraint {t}rather than{/t} a deal-breaker.", "決裂要因{t}というより{/t}、私なら制約{t}と呼びます{/t}。", "I'd call it|a constraint|rather than|a deal-breaker."),
            ),
            rule=rule("Name your label before the rejected one", "自分の表現を先に", "Lead with the accurate description, then use “rather than” for the label you reject.", "正確な表現を先に述べ、退ける表現は 「rather than」 のあとに置きます。", "I'd call it + accurate label + rather than + rejected label", "Offer a better label", "よりよい表現を示す", ("a setback · rather than a failure", "a warning · rather than a crisis")),
            write=("What measured label would you use for a difficult situation?", "難しい状況を、どんな穏当な表現で呼びますか？"),
        ),
        scene_turns=(("other", "This three-week delay means the project has failed.", "3週間の遅れですから、このプロジェクトは失敗です。"), ("target", 1, 0), ("other", "The delay still has a cost.", "それでも遅れにはコストがあります。"), ("target", 2, 0), ("other", "That's fair, provided we recover quickly.", "早く立て直せるなら、その見方は妥当です。"), ("me", "Agreed. Let's review the recovery plan now.", "同意します。今、立て直し計画を確認しましょう。")),
        receptive=receptive(
            ("The project has failed.", "The partner treats the delay as total failure", "相手は遅れを全面的な失敗と捉えている", "The partner says the schedule is unchanged", "相手は予定に変更がないと言っている"),
            ("The delay still has a cost.", "The partner accepts the distinction but keeps the impact visible", "相手は違いを認めつつ影響を重視している", "The partner withdraws every concern", "相手は懸念をすべて取り下げている"),
            ("provided we recover quickly", "Agreement depends on a quick recovery", "同意には早い立て直しが必要", "Agreement is unconditional", "無条件で同意している"),
            ("review the recovery plan", "The discussion moves to a practical next step", "実際の次の行動へ進む", "The meeting ends without action", "行動を決めずに会議を終える"),
        ),
        live=live("Use a real or imaginary overstatement at work and replace it with a more accurate description.", "実際または架空の職場での大げさな表現を、より正確な表現に置き換えてください。", "Real or imaginary: It's not so much ___ as ___. I'd call it ___ rather than ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "If a work problem were described too strongly, how would you reframe it?", "仕事の問題が強すぎる言葉で表されたら、先生はどう捉え直しますか？"),
        tip=("Use “setback” for a recoverable problem", "立て直せる問題には setback", "A setback slows progress; a failure says the intended result was not achieved.", "setback は進行を遅らせる問題、failure は意図した結果を達成できなかったことを示します。", ("Recoverable", "立て直せる", "a temporary setback", "一時的な後退"), ("Result not achieved", "結果を達成していない", "a project failure", "プロジェクトの失敗")),
        transfer_title="Reframing a difficult pilot result", transfer_ja="難しい試験導入の結果を捉え直す", transfer_role="Sponsor",
        transfer_turns=(("other", "The weak pilot response proves the product is a failure.", "試験導入の反応が弱く、この製品は失敗です。"), ("target", 1, 3), ("other", "So how would you describe the result?", "では、この結果をどう表しますか？"), ("target", 2, 1), ("other", "A warning is serious, but it gives us something to test.", "警告なら深刻ですが、検証すべき点が分かります。"), ("me", "Exactly. Let's test the revised offer before deciding.", "その通りです。判断前に修正版を検証しましょう。")),
        vocab=("fundamental problem|根本的な問題", "setback|一時的な後退|CORE-89", "failure|失敗; delay|遅れ; warning|警告; crisis|危機; call it|〜と呼ぶ; reframe|捉え直す; overstatement|大げさな表現", "recover|立て直す; revised offer|修正版の提案"),
    ),
    50: dict(
        slug="make-a-conditional-proposal", title="Make a conditional proposal",
        ko="조건부 제안하기", ja="条件つきの提案をする", role="Client",
        scene="Trading scope for an earlier delivery date", scene_ja="範囲と早い納期を交換条件にする場面",
        situation="早い納期を受け入れる代わりに、報告機能を後の段階へ回すという明確な条件を提案します。",
        goal=("Trade one concession for a clear, workable condition.", "一つの譲歩と引き換えに、明確で実行可能な条件を提示しましょう。"),
        expressions=(("on the condition that", "〜という条件で"), ("reduce the scope", "範囲を縮小する")),
        p1=pattern(
            bridge="まず、受け入れられることと必要な条件を一文で結びます。",
            meaning=("Use this fixed proposal to make an offer conditional on one clear change.", "一つの明確な変更を条件に、提案を受け入れる定型表現です。"),
            rows_=rows(
                ("{t}We could{/t} meet the earlier date, {t}provided{/t} we reduce the scope.", "範囲を縮小する{t}という条件なら{/t}、早い日程に{t}対応できます{/t}。", "We could|meet the earlier date,|provided|we reduce the scope."),
                ("{t}We could{/t} hold the price, {t}provided{/t} the term is two years.", "契約期間が2年{t}という条件なら{/t}、価格を{t}維持できます{/t}。", "We could|hold the price,|provided|the term is two years."),
                ("{t}We could{/t} add training, {t}provided{/t} it stays remote.", "オンライン実施{t}という条件なら{/t}、研修を{t}追加できます{/t}。", "We could|add training,|provided|it stays remote."),
                ("{t}We could{/t} start in May, {t}provided{/t} approval comes this week.", "今週承認される{t}という条件なら{/t}、5月に{t}開始できます{/t}。", "We could|start in May,|provided|approval comes this week."),
            ),
            rule=rule("Keep the offer and condition intact", "提案と条件を一まとまりで", "State the possible concession first and the required condition after “provided.”", "可能な譲歩を先に、必要条件を provided のあとに置きます。", "We could + concession, provided + condition", "Make a conditional offer", "条件つきで提案", ("meet the date · provided we reduce scope", "hold the price · provided the term is two years")),
            write=("What could you offer if one clear condition were met?", "一つの条件が満たされるなら、何を提案できますか？"), omit_rule=True,
        ),
        p2=pattern(
            bridge="次に、相手が先送りできる項目と、こちらが納品できる範囲を具体化します。",
            meaning=("Use this to link the other side's concession to what your team can deliver.", "相手の譲歩と、自分たちが提供できる内容を結びつける表現です。"),
            rows_=rows(
                ("{t}If you can defer{/t} the reporting feature, {t}we can{/t} deliver the rest by June.", "報告機能を{t}先送りできれば{/t}、残りは6月までに{t}納品できます{/t}。", "If you can defer|the reporting feature,|we can deliver|the rest by June."),
                ("{t}If you can defer{/t} the custom dashboard, {t}we can{/t} launch in May.", "カスタム画面を{t}先送りできれば{/t}、5月に{t}公開できます{/t}。", "If you can defer|the custom dashboard,|we can launch|in May."),
                ("{t}If you can defer{/t} the second workshop, {t}we can{/t} keep the budget.", "2回目の研修を{t}先送りできれば{/t}、予算を{t}維持できます{/t}。", "If you can defer|the second workshop,|we can keep|the budget."),
                ("{t}If you can defer{/t} the regional rollout, {t}we can{/t} finish the pilot first.", "地域展開を{t}先送りできれば{/t}、まず試験導入を{t}完了できます{/t}。", "If you can defer|the regional rollout,|we can finish|the pilot first."),
            ),
            rule=rule("Put the client's concession in the if-clause", "相手の譲歩は if 節に", "Name what the client can defer first and your deliverable second.", "相手が先送りできるものを先に、こちらが提供できるものを後に置きます。", "If you can defer + item, we can + result", "Exchange concessions", "譲歩を交換", ("defer reporting · deliver by June", "defer rollout · finish pilot")),
            write=("Which feature could be deferred, and what would that enable?", "どの機能を先送りすれば、何が可能になりますか？"),
        ),
        scene_turns=(("other", "We need the full product a month earlier.", "製品全体を1か月早く必要としています。"), ("target", 1, 0), ("other", "What exactly would you take out?", "具体的に何を外しますか？"), ("target", 2, 0), ("other", "That may work. Put it in the revised proposal.", "それなら可能かもしれません。修正提案書に入れてください。"), ("me", "I will send the revised scope and date today.", "今日、修正した範囲と日程を送ります。")),
        receptive=receptive(("We need the full product a month earlier.", "The client wants the same scope sooner", "相手は同じ範囲をより早く求めている", "The client wants fewer features later", "相手は機能を減らして遅く求めている"), ("What exactly would you take out?", "The client asks which scope item would be removed", "どの範囲を外すか尋ねている", "The client asks who approved the contract", "契約の承認者を尋ねている"), ("That may work.", "The client sees the conditional proposal as possible", "条件つき提案を可能と見ている", "The client rejects every change", "すべての変更を拒否している"), ("Put it in the revised proposal.", "The client asks for the condition in writing", "条件を書面にするよう求めている", "The client asks for an oral apology", "口頭での謝罪を求めている")),
        live=live("Use a real or imaginary negotiation and trade one concession for one condition.", "実際または架空の交渉で、一つの譲歩と一つの条件を交換してください。", "Real or imaginary: We could ___, provided ___. If you can defer ___, we can ___.", "実際の交渉でも架空の交渉でも、二つの表現を使いましょう。", "If you had to trade scope for time, what would you propose?", "範囲と時間を交換するとしたら、先生は何を提案しますか？"),
        tip=("Use “provided” for a firm condition", "明確な条件には provided", "“Provided” sets a firm condition; “if possible” presents a preference rather than a requirement.", "「provided」 は明確な条件、「if possible」 は必須ではない希望を示します。", ("Requirement", "必須条件", "provided we reduce the scope", "範囲を縮小する条件で"), ("Preference", "希望", "by June, if possible", "できれば6月までに")),
        transfer_title="Trading workshop format for budget", transfer_ja="研修形式と予算を交換条件にする", transfer_role="Procurement Lead",
        transfer_turns=(("other", "We need the training included without increasing the price.", "価格を上げずに研修も含める必要があります。"), ("target", 1, 2), ("other", "Which part would move out of the first phase?", "どの部分を第1段階から外しますか？"), ("target", 2, 1), ("other", "Remote training and a later dashboard could fit the budget.", "オンライン研修と後日の画面提供なら予算に収まります。"), ("me", "Good. I'll document both conditions in the offer.", "分かりました。両方の条件を提案書に記載します。")),
        vocab=("defer|先送りする; reduce the scope|範囲を縮小する", "", "deliver|納品する; feature|機能; approval|承認; budget|予算; launch|公開する; conditional proposal|条件つき提案; revised proposal|修正提案書", "procurement|調達; rollout|展開"),
    ),
    51: dict(
        slug="avoid-committing-too-early", title="Avoid committing too early", ko="너무 일찍 확약하지 않기", ja="早すぎる確約を避ける", role="Customer", scene="Responding when a customer presses for a firm date", scene_ja="顧客から確定日を求められる場面",
        situation="供給元の確認が取れる前に日程を確約せず、何によって決まるかと次の確認時刻を明確にします。", goal=("Keep a date open while making the dependency and next update clear.", "日程を未確定のままにしつつ、条件と次の連絡時刻を明確にしましょう。"), expressions=(("hold off on", "〜を見送る"), ("firm date", "確定日")),
        p1=pattern(bridge="まず、現時点では確約しないと穏やかに伝えます。", meaning=("Use this to decline a firm commitment without closing the discussion.", "話し合いを終わらせずに、確約を控える表現です。"), rows_=rows(
            ("{t}I'd rather not commit to{/t} that date {t}yet{/t}.", "{t}まだ{/t}その日程は{t}確約したくありません{/t}。", "I'd rather not|commit to that date|yet"),
            ("{t}I'd rather not commit to{/t} a quantity {t}yet{/t}.", "{t}まだ{/t}数量は{t}確約したくありません{/t}。", "I'd rather not|commit to a quantity|yet"),
            ("{t}I'd rather not commit to{/t} that price {t}yet{/t}.", "{t}まだ{/t}その価格は{t}確約したくありません{/t}。", "I'd rather not|commit to that price|yet"),
            ("{t}I'd rather not commit to{/t} a launch month {t}yet{/t}.", "{t}まだ{/t}公開月は{t}確約したくありません{/t}。", "I'd rather not|commit to a launch month|yet")), rule=rule("Soften the refusal and keep it temporary", "断りを和らげ、現時点に限る", "Use ‘I'd rather not’ for your preference and ‘yet’ to leave room for a later decision.", "「I'd rather not」 で意向を和らげ、yet で後の判断の余地を残します。", "I'd rather not commit to + item + yet", "Delay a commitment", "確約を延期", ("that date · yet", "that price · yet")), write=("What would you avoid committing to until you have more information?", "情報が増えるまで、何の確約を控えますか？")),
        p2=pattern(bridge="次に、判断を左右する条件を示します。", meaning=("Use this to name the unresolved factor that controls the decision.", "判断を左右する未確定の条件を示す表現です。"), rows_=rows(
            ("{t}It depends on whether{/t} the supplier confirms capacity.", "供給元が生産能力を確認するか{t}どうかによります{/t}。", "It depends on whether|the supplier|confirms capacity"),
            ("{t}It depends on whether{/t} legal approves the terms.", "法務が条件を承認するか{t}どうかによります{/t}。", "It depends on whether|legal|approves the terms"),
            ("{t}It depends on whether{/t} the parts arrive tomorrow.", "部品が明日届くか{t}どうかによります{/t}。", "It depends on whether|the parts|arrive tomorrow"),
            ("{t}It depends on whether{/t} the budget is released.", "予算が使えるようになるか{t}どうかによります{/t}。", "It depends on whether|the budget|is released")), rule=rule("Name the open question after whether", "whether のあとに未確定事項", "Put the factor that can change the decision after ‘whether.’", "判断を変える条件を whether のあとに置きます。", "It depends on whether + open question", "Explain the dependency", "判断条件を説明", ("supplier confirms", "legal approves")), write=("What unresolved factor does your decision depend on?", "あなたの判断は、どの未確定要素によって決まりますか？")),
        scene_turns=(("other", "Can you guarantee delivery on June 10?", "6月10日の納品を保証できますか？"), ("target", 1, 0), ("other", "What information are you waiting for?", "何の情報を待っているのですか？"), ("target", 2, 0), ("other", "When will you know?", "いつ分かりますか？"), ("me", "The supplier will confirm by noon tomorrow, and I'll update you then.", "供給元が明日正午までに確認するので、その時点でご連絡します。")),
        receptive=receptive(("guarantee delivery", "The customer wants a firm commitment", "顧客は確約を求めている", "The customer is only asking for an estimate", "概算だけを尋ねている"), ("not commit yet", "The date remains open for now", "日程は現時点で未確定", "The date is permanently rejected", "日程を永久に拒否した"), ("depends on whether", "One unresolved factor controls the answer", "未確定要素が回答を左右する", "The answer is already final", "回答はすでに確定している"), ("by noon tomorrow", "A specific update time is promised", "具体的な連絡時刻を約束している", "No follow-up is offered", "次の連絡がない")),
        live=live("Use a real or imaginary request for a commitment and explain what the answer depends on.", "実際または架空の確約依頼を想定し、何によって回答が決まるか説明してください。", "Real or imaginary: I'd rather not commit to ___ yet. It depends on whether ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "What would you avoid committing to before one fact is confirmed?", "一つの事実が確認されるまで、先生は何の確約を控えますか？"),
        tip=("Commit to a date only when you can stand behind it", "責任を持てるときだけ日程を確約", "To commit to a date is stronger than to aim for a date: it creates a firm expectation.", "commit to a date は確定的な期待を生むため、aim for a date より強い表現です。", ("Firm", "確約", "commit to June 10", "6月10日を確約する"), ("Target", "目標", "aim for June 10", "6月10日を目指す")),
        transfer_title="Holding off on a price commitment", transfer_ja="価格の確約を控える", transfer_role="Buyer", transfer_turns=(("other", "Can you lock in this price for next year?", "来年の価格をこれで固定できますか？"), ("target", 1, 2), ("other", "What needs to happen first?", "先に何が必要ですか？"), ("target", 2, 3), ("other", "We can wait until the budget decision on Friday.", "金曜日の予算決定まで待てます。"), ("me", "Thank you. I'll give you a firm answer that afternoon.", "ありがとうございます。その日の午後に確定回答をお伝えします。")),
        vocab=("firm date|確定日; capacity|生産能力; dependency|判断条件; commit to|確約する", "", "supplier|供給元; guarantee|保証する; legal|法務; terms|条件; update|連絡する; lock in|固定する", "hold off on|〜を見送る; aim for|〜を目指す"),
    ),
    52: dict(
        slug="explain-a-trade-off", title="Explain a trade-off", ko="트레이드오프 설명하기", ja="トレードオフを説明する", role="Product Owner", scene="Balancing speed against reliable testing", scene_ja="速度と十分なテストの釣り合いを話す場面",
        situation="早く進めるほどテスト時間が減るという関係を示し、最も重視する基準を確認します。", goal=("Make the cost of each option visible before choosing a priority.", "優先順位を決める前に、それぞれの選択肢の代償を明らかにしましょう。"), expressions=(("trade-off", "トレードオフ"), ("at the expense of", "〜を犠牲にして")),
        p1=pattern(bridge="まず、一方を増やすともう一方が減る関係を示します。", meaning=("Use this fixed frame to show how gaining speed reduces another resource.", "速度を上げると別の余裕が減る関係を示す定型表現です。"), rows_=rows(
            ("{t}The faster we move{/t}, {t}the less time we'll have for{/t} testing.", "{t}早く進むほど{/t}、テストに使える時間は{t}少なくなります{/t}。", "The faster we move,|the less time|we'll have|for testing."),
            ("{t}The faster we decide{/t}, {t}the less evidence we'll have for{/t} comparison.", "{t}早く決めるほど{/t}、比較に使える根拠は{t}少なくなります{/t}。", "The faster we decide,|the less evidence|we'll have|for comparison."),
            ("{t}The more we customise{/t}, {t}the less time we'll have for{/t} training.", "{t}カスタマイズを増やすほど{/t}、研修に使える時間は{t}少なくなります{/t}。", "The more we customise,|the less time|we'll have|for training."),
            ("{t}The longer we wait{/t}, {t}the less room we'll have for{/t} negotiation.", "{t}長く待つほど{/t}、交渉の余地は{t}少なくなります{/t}。", "The longer we wait,|the less room|we'll have|for negotiation.")), rule=rule("Keep both sides of the relationship together", "両方の関係をまとめて覚える", "This is a fixed paired frame: the first change drives the second change.", "最初の変化が次の変化を引き起す対の定型表現です。", "The + comparative ..., the + comparative ...", "Show the trade-off", "得失関係を示す", ("faster · less time", "longer · less room")), write=("What improves while something else becomes harder?", "何が良くなる一方で、何が難しくなりますか？"), omit_rule=True),
        p2=pattern(bridge="次に、判断の中心となる二つの基準を示します。", meaning=("Use this to focus the decision on which of two priorities matters more.", "二つの優先事項のどちらがより重要かに判断を集中させる表現です。"), rows_=rows(
            ("{t}The question is whether{/t} cost {t}or{/t} reliability {t}matters more{/t}.", "{t}問題は{/t}、コスト{t}と{/t}信頼性のどちらが{t}より重要かです{/t}。", "The question is|whether cost|or reliability|matters more."),
            ("{t}The question is whether{/t} speed {t}or{/t} accuracy {t}matters more{/t}.", "{t}問題は{/t}、速さ{t}と{/t}正確さのどちらが{t}より重要かです{/t}。", "The question is|whether speed|or accuracy|matters more."),
            ("{t}The question is whether{/t} reach {t}or{/t} control {t}matters more{/t}.", "{t}問題は{/t}、届く範囲{t}と{/t}管理のしやすさのどちらが{t}より重要かです{/t}。", "The question is|whether reach|or control|matters more."),
            ("{t}The question is whether{/t} flexibility {t}or{/t} certainty {t}matters more{/t}.", "{t}問題は{/t}、柔軟性{t}と{/t}確実性のどちらが{t}より重要かです{/t}。", "The question is|whether flexibility|or certainty|matters more.")), rule=rule("Put the two competing priorities around or", "or の前後に競合する基準", "Name one priority before ‘or,’ the other after it, and end with the comparison.", "or の前後に一つずつ基準を置き、比較で終えます。", "The question is whether + A + or + B + matters more", "Set the decision criterion", "判断基準を定める", ("cost or reliability", "speed or accuracy")), write=("Which two priorities are competing in your decision?", "あなたの判断で競合している二つの基準は何ですか？")),
        scene_turns=(("other", "Could we launch two weeks earlier?", "2週間早く公開できますか？"), ("target", 1, 0), ("other", "Then what should guide the decision?", "では、何を基準に決めるべきですか？"), ("target", 2, 0), ("other", "Reliability matters more for this release.", "今回の公開では信頼性のほうが重要です。"), ("me", "Then let's keep the current date and protect the test period.", "では現在の日程を維持し、テスト期間を確保しましょう。")),
        receptive=receptive(("launch earlier", "The proposal increases speed", "提案は速度を上げる", "The proposal adds testing time", "テスト時間を増やす"), ("less time for testing", "Speed carries a testing cost", "速度にはテスト時間の代償がある", "Speed has no cost", "速度に代償はない"), ("what should guide", "A decision criterion is needed", "判断基準が必要", "The decision is already fixed", "判断はすでに確定済み"), ("keep the current date", "The team chooses reliability", "チームは信頼性を選んだ", "The team chooses the earlier launch", "チームは早い公開を選んだ")),
        live=live("Use a real or imaginary trade-off and name the two priorities that compete.", "実際または架空のトレードオフと、競合する二つの優先事項を示してください。", "Real or imaginary: The ___ we ___, the less ___ we'll have for ___. The question is whether ___ or ___ matters more.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "What trade-off do you face when planning work?", "仕事の計画で、先生はどんなトレードオフに直面しますか？"),
        tip=("A trade-off is not the same as a compromise", "trade-off と compromise は同じではない", "A trade-off is the cost of gaining one thing; a compromise is an agreement in which each side gives something up.", "「trade-off」 は一つを得るための代償、compromise は双方が一部を譲って成立する合意です。", ("Cost", "代償", "a speed-quality trade-off", "速度と品質の得失関係"), ("Agreement", "合意", "reach a compromise", "妥協点に達する")),
        transfer_title="Balancing customisation and training", transfer_ja="カスタマイズと研修の釣り合い", transfer_role="Implementation Lead", transfer_turns=(("other", "Can we add three more custom workflows?", "カスタム業務フローをあと3つ追加できますか？"), ("target", 1, 2), ("other", "Which priority should decide this?", "どの優先事項で決めるべきですか？"), ("target", 2, 1), ("other", "Accuracy matters more than speed for the first month.", "最初の1か月は速度より正確さが重要です。"), ("me", "Then we'll keep the training time and postpone two workflows.", "では研修時間を確保し、2つのフローを後回しにします。")),
        vocab=("trade-off|トレードオフ; reliability|信頼性; certainty|確実性", "flexibility|調整の余地|CTX-30", "testing|テスト; comparison|比較; accuracy|正確さ; custom workflow|カスタム業務フロー; decision criterion|判断基準", "at the expense of|〜を犠牲にして; reach a compromise|妥協点に達する"),
    ),
    53: concise_lesson(
        slug="acknowledge-then-push-back", title="Acknowledge, then push back", ko="인정한 뒤 반론하기", ja="認めてから反論する", role="Supplier", scene="Challenging a charge after acknowledging a warning", scene_ja="事前の説明を認めたうえで費用に異議を唱える場面", situation="相手が事前に説明した点は公平に認めつつ、それでも残る具体的な懸念を明確に伝えます。", goal=("Acknowledge the other side's valid point before stating the concern that remains.", "相手の正当な点を認めてから、残る懸念を伝えましょう。"), expressions=(("give credit", "評価する"), ("push back", "異議を唱える")),
        p1_rows=rows(("{t}To be fair,{/t} you did warn us about the lead time.", "{t}公平に言えば{/t}、納期については確かに事前に説明がありました。", "To be fair,|you did warn us|about the lead time."), ("{t}To be fair,{/t} you did flag the risk early.", "{t}公平に言えば{/t}、リスクは早くから指摘されていました。", "To be fair,|you did flag|the risk early."), ("{t}To be fair,{/t} you did offer an alternative.", "{t}公平に言えば{/t}、代案は確かに提示されました。", "To be fair,|you did offer|an alternative."), ("{t}To be fair,{/t} you did explain the limitation.", "{t}公平に言えば{/t}、制約は確かに説明されました。", "To be fair,|you did explain|the limitation.")), p1_bridge="まず、相手の正当な点を公平に認めます。", p1_meaning=("Use this to give genuine credit before disagreeing.", "異議を述べる前に、相手の正当な点を認める表現です。"), p1_rule=rule("Open with the fair point", "公平な点を先に", "Put the point you genuinely accept after 'To be fair.'", "本当に認める点を 「To be fair」 のあとに置きます。", "To be fair, + valid point", "Acknowledge first", "まず認める", ("warned us", "offered an alternative")), p1_write=("What valid point can you acknowledge?", "相手のどの正当な点を認められますか？"), p1_omit_reorder=True,
        p2_rows=rows(("{t}That said,{/t} the final amount still seems disproportionate.", "{t}そうは言っても{/t}、最終的な金額はそれでも不釣り合いに思えます。", "That said,|the final amount|still seems disproportionate."), ("{t}That said,{/t} the delay still needs an explanation.", "{t}そうは言っても{/t}、遅れにはそれでも説明が必要です。", "That said,|the delay|still needs an explanation."), ("{t}That said,{/t} the remedy still falls short.", "{t}そうは言っても{/t}、救済策はそれでも不十分です。", "That said,|the remedy|still falls short."), ("{t}That said,{/t} the terms still seem one-sided.", "{t}そうは言っても{/t}、条件はそれでも一方的に思えます。", "That said,|the terms|still seem one-sided.")), p2_bridge="次に、認めたうえでも残る懸念を述べます。", p2_meaning=("Use this to pivot from acknowledgement to a concern that still matters.", "認めた内容から、それでも重要な懸念へ移る表現です。"), p2_rule=rule("Put the remaining concern after the pivot", "転換のあとに残る懸念", "Use 'That said' only after a real acknowledgement, then state the unresolved concern.", "実際に認める点を述べたあとに 「That said」 を使い、未解決の懸念を示します。", "That said, + remaining concern", "Push back constructively", "建設的に反論", ("amount seems disproportionate", "remedy falls short")), p2_write=("What concern remains after you acknowledge the other side?", "相手の点を認めたあと、どんな懸念が残りますか？"), p2_omit_reorder=True,
        scene_turns=(("other", "We told you the rush order would take longer.", "特急注文は時間がかかるとお伝えしました。"), ("target", 1, 0), ("other", "Then do you accept the extra charge?", "では追加料金を受け入れますか？"), ("target", 2, 0), ("other", "I'll review the calculation with finance today.", "今日、経理と計算を見直します。"), ("me", "Thank you. Please send the itemised calculation by five.", "ありがとうございます。5時までに内訳の計算を送ってください。")), receptive_=receptive(("take longer", "The supplier had warned about timing", "供給元は日程を事前に説明した", "The delay was never mentioned", "遅れは説明されていない"), ("To be fair", "A valid point is acknowledged", "正当な点を認めている", "Every objection is withdrawn", "反論をすべて撤回した"), ("That said", "A concern still remains", "それでも懸念が残る", "The charge is accepted", "料金を受け入れた"), ("review the calculation", "The supplier offers a next step", "供給元が次の対応を提示した", "The discussion ends without action", "対応なしで終わる")), live_=live("Use a real or imaginary disagreement: acknowledge one valid point, then state the concern that remains.", "実際または架空の意見の相違で、正当な点を一つ認め、残る懸念を示してください。", "Real or imaginary: To be fair, ___. That said, ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "When you disagree at work, what valid point do you acknowledge first?", "仕事で意見が異なるとき、先生はまずどの正当な点を認めますか？"), tip=("'That said' is firmer than 'but'", "That said は but より明確", "'That said' signals that a considered concern remains after a genuine acknowledgement.", "That said は、本当に認めたうえでも検討すべき懸念が残ると示します。", ("Measured pivot", "検討した転換", "That said, the amount is high.", "そうは言っても金額は高額です。"), ("Simple contrast", "単純な対比", "but the amount is high", "しかし金額は高額です")), transfer_title="Challenging a proposed remedy", transfer_ja="提案された救済策に異議を唱える", transfer_role="Service Provider", transfer_turns=(("other", "We offered a credit as soon as the outage ended.", "停止が終わるとぐにクレジットを提示しました。"), ("target", 1, 2), ("other", "Do you think the credit is insufficient?", "クレジットが不十分だと思いますか？"), ("target", 2, 2), ("other", "We'll review a larger credit by tomorrow.", "明日までに増額を検討します。"), ("me", "That would address the remaining concern.", "それなら残る懸念に対応できます。")), vocab=("disproportionate|不釣り合いな; one-sided|一方的な; lead time|リードタイム", "push back|異議を唱える|CORE-95; remedy|救済策|CTX-8", "warn|事前に説明する; extra charge|追加料金; alternative|代案; limitation|制約", "give credit|評価する; fall short|不十分である")),
    54: concise_lesson(
        slug="find-common-ground", title="Find common ground", ko="공통점 찾기", ja="共通点を見つける", role="Client", scene="Separating agreement on the outcome from disagreement on timing", scene_ja="成果の合意と時期の不一致を分ける場面", situation="目指す結果は共通していると確認し、残る相違を限定したうえで、段階的な合意を提案します。", goal=("Name what both sides share, isolate the disagreement, and propose a workable next step.", "双方の共通点と相違点を分け、実行可能な次の一手を提案しましょう。"), expressions=(("common ground", "共通点"), ("phased agreement", "段階的合意")),
        p1_rows=rows(("{t}We seem to agree on{/t} the outcome, {t}but not{/t} the timeline.", "成果については{t}合意しているようですが{/t}、日程については{t}まだ合意していません{/t}。", "We seem to agree|on the outcome,|but not|the timeline."), ("{t}We seem to agree on{/t} the scope, {t}but not{/t} the price.", "範囲については{t}合意しているようですが{/t}、価格については{t}まだ合意していません{/t}。", "We seem to agree|on the scope,|but not|the price."), ("{t}We seem to agree on{/t} the principle, {t}but not{/t} the wording.", "原則については{t}合意しているようですが{/t}、表現については{t}まだ合意していません{/t}。", "We seem to agree|on the principle,|but not|the wording."), ("{t}We seem to agree on{/t} the first phase, {t}but not{/t} the second.", "第1段階については{t}合意しているようですが{/t}、第2段階については{t}まだ合意していません{/t}。", "We seem to agree|on the first phase,|but not|the second.")), p1_bridge="まず、合意済みの点と未合意の点を分けます。", p1_meaning=("Use this fixed frame to narrow a broad disagreement to one issue.", "広い意見の相違を一つの論点に絞る定型表現です。"), p1_rule=rule("Keep the shared and disputed points together", "共通点と相違点を対で覚える", "This is a fixed frame for naming agreement first and disagreement second.", "合意点を先に、相違点を後に示す定型表現です。", "We seem to agree on A, but not B", "Narrow the disagreement", "相違点を限定", ("outcome · timeline", "scope · price")), p1_write=("What do both sides agree on, and what remains open?", "双方が合意している点と、まだ残る点は何ですか？"), p1_omit_rule=True,
        p2_rows=rows(("{t}What if we agreed on{/t} phase one today {t}and revisited{/t} phase two next week?", "今日、第1段階に{t}合意し、{/t}来週、第2段階を{t}改めて検討するのはどうでしょうか{/t}？", "What if we agreed|on phase one today|and revisited|phase two next week?"), ("{t}What if we agreed on{/t} the scope today {t}and revisited{/t} the price tomorrow?", "今日、範囲に{t}合意し、{/t}明日、価格を{t}改めて検討するのはどうでしょうか{/t}？", "What if we agreed|on the scope today|and revisited|the price tomorrow?"), ("{t}What if we agreed on{/t} the principle now {t}and revisited{/t} the wording later?", "今、原則に{t}合意し、{/t}後で表現を{t}改めて検討するのはどうでしょうか{/t}？", "What if we agreed|on the principle now|and revisited|the wording later?"), ("{t}What if we agreed on{/t} the pilot today {t}and revisited{/t} expansion in June?", "今日、試験導入に{t}合意し、{/t}6月に拡大を{t}改めて検討するのはどうでしょうか{/t}？", "What if we agreed|on the pilot today|and revisited|expansion in June?")), p2_bridge="次に、今決められる点と後で見直す点を提案します。", p2_meaning=("Use this to secure partial agreement without forcing the unresolved issue.", "未解決の論点を無理に決めず、部分的な合意を得る表現です。"), p2_rule=rule("Pair today's agreement with a later review", "今の合意と後の再検討を対に", "Name what can be agreed now, then what can be revisited later.", "今合意できることを先に、後で再検討することを次に示します。", "What if we agreed on A and revisited B?", "Propose phased agreement", "段階的な合意を提案", ("agree on phase one", "revisit phase two")), p2_write=("What could you agree now and revisit later?", "今合意し、後で見直せることは何ですか？"),
        scene_turns=(("other", "We both want the full rollout, but we need it in May.", "全面展開を目指す点は同じですが、5月に必要です。"), ("target", 1, 0), ("other", "How can we move forward today?", "今日どう進められますか？"), ("target", 2, 0), ("other", "Yes. We can approve phase one today.", "はい。今日、第1段階を承認できます。"), ("me", "Great. I'll document that agreement and book next week's review.", "それでは合意内容を書面化し、来週の再検討を設定します。")), receptive_=receptive(("both want", "The outcome is shared", "目指す成果は共通している", "The sides want different outcomes", "目指す成果が異なる"), ("but we need it in May", "Timing is the remaining disagreement", "時期が残る相違点", "Price is the remaining disagreement", "価格が残る相違点"), ("phase one today", "Part of the agreement can be made now", "合意の一部は今決められる", "Everything is postponed", "すべてを延期する"), ("book next week's review", "The open issue has a next step", "未解決の論点に次の行動がある", "The open issue is ignored", "未解決の論点を無視する")), live_=live("Use a real or imaginary negotiation: name the common ground and propose what to agree now and revisit later.", "実際または架空の交渉で、共通点を示し、今合意する点と後で見直す点を提案してください。", "Real or imaginary: We seem to agree on ___, but not ___. What if we agreed on ___ today and revisited ___ later?", "実際の例でも架空の例でも、二つの表現を使いましょう。", "In a negotiation, what could you agree now and revisit later?", "交渉で、先生は何を今合意し、何を後で見直しますか？"), tip=("Common ground is a shared point, not full agreement", "common ground は完全合意ではない", "Finding common ground identifies a point both sides share; other issues can remain open.", "common ground を見つけるとは、双方の共通点を確認することであり、他の論点は未合意でも構いません。", ("Shared point", "共通点", "agree on the outcome", "成果には合意する"), ("Full agreement", "完全合意", "agree on every term", "すべての条件に合意する")), transfer_title="Agreeing on a pilot first", transfer_ja="まず試験導入に合意する", transfer_role="Partner", transfer_turns=(("other", "We support expansion, but not before the pilot results.", "拡大には賛成ですが、試験導入の結果が出る前は同意できません。"), ("target", 1, 3), ("other", "What can we decide this week?", "今週、何を決められますか？"), ("target", 2, 3), ("other", "That works. Let's approve the pilot today.", "それでいいです。今日、試験導入を承認しましょう。"), ("me", "Agreed. I'll set a June review for expansion.", "同意します。6月に拡大の再検討を設定します。")), vocab=("common ground|共通点; phased agreement|段階的合意; revisit|改めて検討する; principle|原則", "", "outcome|成果; timeline|日程; scope|範囲; wording|表現; pilot|試験導入; expansion|拡大", "move forward|前に進む; isolate|切り分ける")),
}


LESSONS.update({
    55: concise_lesson(
        slug="address-a-performance-pattern", title="Address a performance pattern", ko="성과 패턴 짚어 보기", ja="業務上の傾向について話す", role="Team Member", scene="Discussing repeated missed deadlines without blame", scene_ja="責めずに繰り返しの締め切り遅れを話す場面", situation="観察した事実を具体的に示し、決めつけずに背景を尋ね、実際に役立つ支援を決めます。", goal=("Name a repeated pattern with evidence, then ask what is making the work difficult.", "根拠とともに繰り返しの傾向を示し、仕事を難しくしている原因を尋ねましょう。"), expressions=(("recurring pattern", "繰り返しの傾向"), ("get in the way", "妨げになる")),
        p1_rows=rows(("{t}I've noticed that{/t} the last three deadlines have been missed.", "直近3回の締め切りが過ぎていることに{t}気づきました{/t}。", "I've noticed that|the last three deadlines|have been missed."), ("{t}I've noticed that{/t} the weekly figures arrive late.", "週次の数値が遅れて届くことに{t}気づきました{/t}。", "I've noticed that|the weekly figures|arrive late."), ("{t}I've noticed that{/t} client updates are often delayed.", "顧客への連絡がよく遅れていることに{t}気づきました{/t}。", "I've noticed that|client updates|are often delayed."), ("{t}I've noticed that{/t} handovers are taking longer.", "引き継ぎにより時間がかかっていることに{t}気づきました{/t}。", "I've noticed that|handovers|are taking longer.")), p1_bridge="まず、評価ではなく、観察した事実を示します。", p1_meaning=("Use this fixed opening to introduce an observable pattern without accusing the person.", "相手を責めず、観察できる傾向を話題にする定型表現です。"), p1_rule=rule("Keep the observation factual", "観察は事実に限る", "Use this fixed opening before a specific pattern you can point to.", "具体的に示せる傾向の前に置く定型表現です。", "I've noticed that + observable pattern", "Open a performance conversation", "業務の対話を始める", ("three deadlines missed", "updates delayed")), p1_write=("What repeated, observable pattern do you need to discuss?", "話し合う必要がある、繰り返しの事実は何ですか？"), p1_omit_rule=True, p1_omit_reorder=True,
        p2_rows=rows(("{t}I'd like to understand what's{/t} getting in the way.", "何が妨げになっているのか{t}理解したいです{/t}。", "I'd like to understand|what's getting|in the way."), ("{t}I'd like to understand what's{/t} causing the delay.", "何が遅れを引き起こしているのか{t}理解したいです{/t}。", "I'd like to understand|what's causing|the delay."), ("{t}I'd like to understand what's{/t} changed this month.", "今月、何が変わったのか{t}理解したいです{/t}。", "I'd like to understand|what's changed|this month."), ("{t}I'd like to understand what's{/t} making handovers difficult.", "何が引き継ぎを難しくしているのか{t}理解したいです{/t}。", "I'd like to understand|what's making|handovers difficult.")), p2_bridge="次に、原因を決めつけず、相手の説明を求めます。", p2_meaning=("Use this fixed frame to invite the person's explanation before proposing a solution.", "解決策を決める前に、相手の説明を促す定型表現です。"), p2_rule=rule("Ask to understand before solving", "解決より先に理解を求める", "Use this fixed frame before the obstacle or change you want the person to explain.", "説明してほしい障害や変化の前に置く定型表現です。", "I'd like to understand what's + obstacle", "Invite an explanation", "説明を促す", ("getting in the way", "causing the delay")), p2_write=("What would you like to understand before offering support?", "支援を提案する前に、何を理解したいですか？"), p2_omit_rule=True, p2_omit_reorder=True,
        scene_turns=(("other", "You wanted to discuss my project work.", "私のプロジェクト作業について話したいとのことでしたね。"), ("target", 1, 0), ("other", "Two urgent requests have been arriving every afternoon.", "毎日の午後に緊急依頼が2件ずつ来ています。"), ("target", 2, 0), ("other", "Protecting two mornings a week would help.", "週に2回、午前の時間を確保できると助かります。"), ("me", "Let's block those mornings and review progress next Friday.", "その午前を確保し、来週金曜日に進捗を確認しましょう。")), receptive_=receptive(("last three deadlines", "The manager cites a repeated fact", "上司は繰り返しの事実を示す", "The manager makes a vague accusation", "上司は曖昧に責める"), ("urgent requests", "The team member names a real obstacle", "メンバーは具体的な障害を説明する", "The team member denies the pattern", "メンバーは傾向を否定する"), ("understand what's getting in the way", "The manager seeks the cause", "上司は原因を理解しようとする", "The manager has already decided the cause", "上司は原因を決めつけている"), ("block those mornings", "They agree on concrete support", "具体的な支援に合意する", "No action is agreed", "行動に合意しない")), live_=live("Use a real or imaginary performance pattern: state the evidence and ask what is getting in the way.", "実際または架空の業務上の傾向について、根拠を示し、何が妨げになっているか尋ねてください。", "Real or imaginary: I've noticed that ___. I'd like to understand what's ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "What evidence would you mention before asking about an obstacle?", "障害について尋ねる前に、先生はどんな根拠を示しますか？"), tip=("Describe a pattern, not a personality", "性格ではなく傾向を説明", "A specific pattern can be discussed and changed; a label such as 'unreliable' turns the conversation into a judgment about the person.", "具体的な傾向は話し合って変えられますが、unreliable のようなレッテルは人物の評価になります。", ("Observable", "観察可能", "three deadlines were missed", "3回締め切りを過ぎた"), ("Personal label", "人物評価", "you're unreliable", "あなたは信頼できない")), transfer_title="Discussing delayed client updates", transfer_ja="遅れている顧客連絡を話す", transfer_role="Account Manager", transfer_turns=(("other", "You asked about my client communication.", "私の顧客対応についてですね。"), ("target", 1, 2), ("other", "The approval data has been arriving after our calls.", "承認データが顧客との通話後に届いています。"), ("target", 2, 1), ("other", "A morning data check would remove the delay.", "朝にデータを確認すれば遅れをなくせます。"), ("me", "I'll arrange that check from tomorrow.", "明日からその確認を手配します。")), vocab=("recurring pattern|繰り返しの傾向; handover|引き継ぎ; observable|観察可能な", "deadline|締め切り|CTX-32", "notice|気づく; miss|間に合わない; delay|遅れ; support|支援; progress|進捗", "get in the way|妨げになる; block time|時間を確保する")),
    56: concise_lesson(
        slug="give-high-standard-feedback", title="Give high-standard feedback", ko="높은 기준의 피드백 주기", ja="高い基準のフィードバックを伝える", role="Analyst", scene="Improving an executive briefing", scene_ja="経営層向け説明の改善点を話す場面", situation="成果物の強みを認め、核心が埋もれているという影響を特定し、次に取る具体的な行動を伝えます。", goal=("Recognise what is strong, isolate the issue, and request one concrete improvement.", "強みを認め、問題を絞り、具体的な改善を一つ求めましょう。"), expressions=(("bury the main point", "要点を埋もれさせる"), ("lead with", "〜から始める")),
        p1_rows=rows(("The analysis is strong; {t}the issue is that{/t} the main point gets buried.", "分析は優れていますが、{t}問題は{/t}要点が埋もれている{t}ことです{/t}。", "The analysis is strong;|the issue is that|the main point|gets buried."), ("The evidence is solid; {t}the issue is that{/t} the conclusion comes too late.", "根拠はしっかりしていますが、{t}問題は{/t}結論が遅すぎる{t}ことです{/t}。", "The evidence is solid;|the issue is that|the conclusion|comes too late."), ("The structure is clear; {t}the issue is that{/t} the recommendation is vague.", "構成は明確ですが、{t}問題は{/t}提言が曖昧な{t}ことです{/t}。", "The structure is clear;|the issue is that|the recommendation|is vague."), ("The detail is useful; {t}the issue is that{/t} the decision is hard to find.", "詳細は役立ちますが、{t}問題は{/t}判断が見つけにくい{t}ことです{/t}。", "The detail is useful;|the issue is that|the decision|is hard to find.")), p1_bridge="まず、強みと問題を一組で明確に示します。", p1_meaning=("Use this fixed contrast to preserve the strength while isolating the problem.", "強みを残したまま、問題を限定する定型表現です。"), p1_rule=rule("Keep the strength and issue in one contrast", "強みと問題を一つの対比に", "Name the genuine strength first, then the specific issue and its effect.", "本当の強みを先に、具体的な問題と影響を後に示します。", "Strength; the issue is that + effect", "Diagnose the work", "成果物の課題を示す", ("analysis strong · point buried", "evidence solid · conclusion late")), p1_write=("What is strong, and what specific issue weakens the result?", "何が優れていて、どの具体的な問題が結果を弱めていますか？"), p1_omit_rule=True,
        p2_rows=rows(("{t}What I'd like you to do is{/t} lead with the recommendation.", "{t}あなたにしてほしいのは{/t}、提言から始めることです。", "What I'd like you|to do is|lead with|the recommendation."), ("{t}What I'd like you to do is{/t} shorten the background section.", "{t}あなたにしてほしいのは{/t}、背景の部分を短くすることです。", "What I'd like you|to do is|shorten|the background section."), ("{t}What I'd like you to do is{/t} quantify the expected impact.", "{t}あなたにしてほしいのは{/t}、予想される影響を数値で示すことです。", "What I'd like you|to do is|quantify|the expected impact."), ("{t}What I'd like you to do is{/t} state the decision on page one.", "{t}あなたにしてほしいのは{/t}、1ページ目に判断を明記することです。", "What I'd like you|to do is|state the decision|on page one.")), p2_bridge="次に、改善につながる一つの行動を具体的に依頼します。", p2_meaning=("Use this fixed frame to turn feedback into one clear action.", "フィードバックを一つの明確な行動に変える定型表現です。"), p2_rule=rule("Follow the frame with one observable action", "表現のあとに一つの行動", "State one action the person can complete and you can review.", "相手が実行でき、自分が確認できる行動を一つ示します。", "What I'd like you to do is + action", "Request the improvement", "改善行動を求める", ("lead with the recommendation", "quantify the impact")), p2_write=("What single change would make the work stronger?", "成果物をより強くする一つの変更は何ですか？"), p2_omit_rule=True,
        scene_turns=(("other", "What did you think of the briefing?", "説明資料はどうでしたか？"), ("target", 1, 0), ("other", "What should I change first?", "まず何を変えるべきですか？"), ("target", 2, 0), ("other", "I'll move the recommendation to the opening slide.", "提言を最初のスライドに移します。"), ("me", "Good. Send me that revision by three and I'll review it today.", "いいですね。3時までに修正版を送ってください。今日確認します。")), receptive_=receptive(("analysis is strong", "A genuine strength is recognised", "本当の強みを認めている", "The whole briefing is rejected", "説明資料全体を否定する"), ("main point gets buried", "The issue is the effect on the reader", "問題は読み手への影響である", "The analyst's intention is criticised", "分析担当者の意図を批判する"), ("lead with the recommendation", "One concrete revision is requested", "具体的な修正を一つ求める", "The analyst must rewrite everything", "全部書き直すよう求める"), ("review it today", "The revision has a follow-up", "修正には確認の次の段階がある", "No review is offered", "確認の予定はない")), live_=live("Use a real or imaginary piece of work: recognise a strength, name the issue, and request one improvement.", "実際または架空の成果物について、強みを認め、問題を示し、改善を一つ求めてください。", "Real or imaginary: ___ is strong; the issue is that ___. What I'd like you to do is ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "What one change would you request in a piece of work?", "成果物に対して、先生はどんな変更を一つ求めますか？"), tip=("Describe impact, not presumed intent", "推測した意図ではなく影響を述べる", "'The point gets buried' describes the result for the audience; 'you ignored the point' assumes why the writer did it.", "the point gets buried は読み手への結果を述べますが、you ignored the point は書き手の意図を決めつけます。", ("Impact", "影響", "the point gets buried", "要点が埋もれる"), ("Assumed intent", "推測した意図", "you ignored the point", "要点を無視した")), transfer_title="Improving a decision memo", transfer_ja="意思決定メモを改善する", transfer_role="Strategy Manager", transfer_turns=(("other", "Is the decision memo ready for the board?", "意思決定メモは取締役会向けに完成していますか？"), ("target", 1, 3), ("other", "What revision would fix that?", "どんな修正で改善できますか？"), ("target", 2, 3), ("other", "I'll put the decision and owner on the first page.", "1ページ目に判断と担当者を記載します。"), ("me", "Perfect. That will make the memo ready for review.", "いいですね。それならメモを確認できます。")), vocab=("bury the main point|要点を埋もれさせる; executive briefing|経営層向け説明; quantify|数値で示す; decision memo|意思決定メモ", "recommendation|提言|CORE-116", "analysis|分析; evidence|根拠; conclusion|結論; revision|修正; impact|影響", "lead with|〜から始める; stand behind|自信を持って支持する")),
    57: concise_lesson(
        slug="communicate-uncertainty-clearly", title="Communicate uncertainty clearly", ko="불확실성을 명확하게 전달하기", ja="不確実性を明確に伝える", role="Executive", scene="Giving a factual update during an investigation", scene_ja="調査中に事実に基づく状況報告をする場面", situation="確認済みの事実とまだ分からない点を分け、次の更新時刻を約束します。", goal=("Separate confirmed facts from open questions and give a specific update time.", "確認済みの事実と未確認の点を分け、次の更新時刻を示しましょう。"), expressions=(("confirmed fact", "確認済みの事実"), ("open question", "未解決の疑問")),
        p1_rows=rows(("{t}What we know is that{/t} customer data remains secure.", "{t}現時点で分かっているのは{/t}、顧客データは安全なままだということです。", "What we know|is that|customer data|remains secure."), ("{t}What we know is that{/t} the backup is intact.", "{t}現時点で分かっているのは{/t}、バックアップは無事だということです。", "What we know|is that|the backup|is intact."), ("{t}What we know is that{/t} payments are still processing.", "{t}現時点で分かっているのは{/t}、決済処理は続いているということです。", "What we know|is that|payments are|still processing."), ("{t}What we know is that{/t} only one region is affected.", "{t}現時点で分かっているのは{/t}、影響は一つの地域に限られるということです。", "What we know|is that|only one region|is affected.")), p1_bridge="まず、確認できている事実だけを明示します。", p1_meaning=("Use this to mark a statement as confirmed rather than inferred.", "推測ではなく、確認済みの事実だと示す表現です。"), p1_rule=rule("Follow the frame with a verified fact", "表現のあとに確認済みの事実", "State only information supported by the current investigation.", "現在の調査で裏づけられている情報だけを述べます。", "What we know is that + verified fact", "State what is known", "既知の事実を示す", ("data remains secure", "backup is intact")), p1_write=("What fact can you confirm now?", "現在、どの事実を確認できますか？"),
        p2_rows=rows(("{t}We don't know{/t} that {t}yet, but we'll{/t} update everyone at four.", "それは{t}まだ分かりませんが{/t}、4時に全員に{t}更新情報を伝えます{/t}。", "We don't know|that yet,|but we'll update everyone|at four."), ("{t}We don't know{/t} the cause {t}yet, but we'll{/t} update everyone at six.", "原因は{t}まだ分かりませんが{/t}、6時に全員に{t}更新情報を伝えます{/t}。", "We don't know|the cause yet,|but we'll update everyone|at six."), ("{t}We don't know{/t} the full impact {t}yet, but we'll{/t} share another update at noon.", "影響の全容は{t}まだ分かりませんが{/t}、正午に次の情報を{t}共有します{/t}。", "We don't know|the full impact yet,|but we'll share another update|at noon."), ("{t}We don't know{/t} when service will resume {t}yet, but we'll{/t} update this page hourly.", "サービスの再開時刻は{t}まだ分かりませんが{/t}、このページを1時間ごとに{t}更新します{/t}。", "We don't know|when service will resume yet,|but we'll update this page|hourly.")), p2_bridge="次に、未確認の点を正直に示し、次の連絡を約束します。", p2_meaning=("Use this to acknowledge an unknown and immediately pair it with a reliable update plan.", "分からない点を認め、信頼できる更新予定と組み合わせる表現です。"), p2_rule=rule("Pair the unknown with a concrete update", "未確認事項と具体的な更新を対に", "State what is not known yet, then give a time or cadence for the next update.", "まだ分からないことを述べ、次の更新時刻または頻度を示します。", "We don't know ... yet, but we'll + update", "Manage uncertainty", "不確実性に対応", ("don't know cause · update at six", "don't know impact · update at noon")), p2_write=("What is still unknown, and when will you update people?", "何がまだ分からず、いつ情報を更新しますか？"),
        scene_turns=(("other", "Is customer data at risk?", "顧客データに危険はありますか？"), ("target", 1, 0), ("other", "Do we know what caused the incident?", "事象の原因は分かっていますか？"), ("target", 2, 0), ("other", "Good. I'll direct questions to the four o'clock update.", "分かりました。質問は4時の更新へ案内します。"), ("me", "Thank you. Please avoid sharing anything unconfirmed before then.", "ありがとうございます。それまで未確認情報は共有しないでください。")), receptive_=receptive(("remains secure", "Customer data is confirmed safe", "顧客データの安全は確認済み", "The cause is confirmed", "原因が確認済み"), ("don't know that yet", "The cause remains open", "原因はまだ未確認", "No investigation is happening", "調査は行われていない"), ("update everyone at four", "A specific update time is promised", "具体的な更新時刻を約束する", "The next update is indefinite", "次の更新時刻は未定"), ("avoid sharing unconfirmed", "Communication stays within verified facts", "確認済みの事実に限って伝える", "People may speculate", "推測を共有してもよい")), live_=live("Use a real or imaginary uncertain situation: state one confirmed fact, one unknown, and the next update time.", "実際または架空の不確実な状況で、確認済みの事実、未確認の点、次の更新時刻を示してください。", "Real or imaginary: What we know is that ___. We don't know ___ yet, but we'll update everyone at ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "In an uncertain situation, what fact would you confirm first?", "不確実な状況で、先生はまずどの事実を確認しますか？"), tip=("'Confirmed' is stronger than 'likely'", "confirmed は likely より強い", "Use 'confirmed' only for verified information. 'Likely' still describes a probability, not a fact.", "confirmed は検証済みの情報にだけ使います。likely は事実ではなく、まだ可能性を示します。", ("Verified", "検証済み", "the backup is confirmed intact", "バックアップの無事を確認済み"), ("Probable", "可能性", "the backup is likely intact", "バックアップは無事の可能性が高い")), transfer_title="Updating leaders on a payment issue", transfer_ja="決済問題を経営層に報告する", transfer_role="Board Member", transfer_turns=(("other", "Have all payments stopped?", "すべての決済が停止したのですか？"), ("target", 1, 2), ("other", "When will we know the full impact?", "影響の全容はいつ分かりますか？"), ("target", 2, 2), ("other", "I'll wait for the noon update before contacting clients.", "顧客に連絡する前に正午の更新を待ちます。"), ("me", "That's best. I'll send the verified facts at noon.", "それが最善です。正午に確認済みの事実を送ります。")), vocab=("uncertainty|不確実性; intact|無事な; speculate|推測する; verified|検証済みの", "secure|安全な|CORE-75", "customer data|顧客データ; update|更新情報; cause|原因; impact|影響; payment|決済", "open question|未解決の疑問; cadence|頻度")),
    58: concise_lesson(
        slug="adapt-a-message-for-stakeholders", title="Adapt a message for stakeholders", ko="이해관계자에 맞게 메시지 조정하기", ja="ステークホルダーに合わせて伝え方を変える", role="Programme Director", scene="Presenting one proposal to finance and operations", scene_ja="一つの提案を経理と運用に説明する場面", situation="同じ提案を、経理には予測可能なコスト、運用には計画外停止のリスク低減という異なる価値で説明します。", goal=("Keep the proposal accurate while connecting it to each stakeholder's priority.", "提案の正確さを保ちながら、それぞれの優先事項に結びつけましょう。"), expressions=(("tailor the message", "伝え方を合わせる"), ("unplanned downtime", "計画外停止")),
        p1_rows=rows(("{t}For{/t} finance, {t}the key benefit is{/t} predictable cost.", "{t}経理にとって{/t}、{t}最大の利点は{/t}コストを予測できることです。", "For finance,|the key benefit|is predictable cost."), ("{t}For{/t} sales, {t}the key benefit is{/t} faster onboarding.", "{t}営業にとって{/t}、{t}最大の利点は{/t}導入が早くなることです。", "For sales,|the key benefit|is faster onboarding."), ("{t}For{/t} legal, {t}the key benefit is{/t} clearer accountability.", "{t}法務にとって{/t}、{t}最大の利点は{/t}責任所在が明確になることです。", "For legal,|the key benefit|is clearer accountability."), ("{t}For{/t} customers, {t}the key benefit is{/t} quicker support.", "{t}顧客にとって{/t}、{t}最大の利点は{/t}対応が早くなることです。", "For customers,|the key benefit|is quicker support.")), p1_bridge="まず、対象とその相手にとっての主な利点を結びつけます。", p1_meaning=("Use this fixed frame to lead with the value most relevant to one audience.", "一つの聞き手に最も関係のある価値から伝える定型表現です。"), p1_rule=rule("Pair one audience with one real benefit", "一つの対象と一つの実際の利点", "Use the frame as one unit and name a benefit the proposal genuinely delivers.", "表現を一まとまりで使い、提案が実際にもたらす利点を示します。", "For + audience, the key benefit is + value", "Lead with audience value", "対象別の価値を示す", ("finance · predictable cost", "sales · faster onboarding")), p1_write=("Which stakeholder needs to hear which benefit first?", "どのステークホルダーに、どの利点を最初に伝えますか？"), p1_omit_rule=True,
        p2_rows=rows(("{t}For{/t} operations, {t}it addresses the risk of{/t} unplanned downtime.", "{t}運用にとって{/t}、これは計画外停止のリスクに{t}対応します{/t}。", "For operations,|it addresses|the risk of|unplanned downtime."), ("{t}For{/t} finance, {t}it addresses the risk of{/t} unexpected cost.", "{t}経理にとって{/t}、これは予期しないコストのリスクに{t}対応します{/t}。", "For finance,|it addresses|the risk of|unexpected cost."), ("{t}For{/t} legal, {t}it addresses the risk of{/t} unclear ownership.", "{t}法務にとって{/t}、これは担当の不明確さというリスクに{t}対応します{/t}。", "For legal,|it addresses|the risk of|unclear ownership."), ("{t}For{/t} customers, {t}it addresses the risk of{/t} slow recovery.", "{t}顧客にとって{/t}、これは復旧の遅れというリスクに{t}対応します{/t}。", "For customers,|it addresses|the risk of|slow recovery.")), p2_bridge="次に、同じ提案が別の対象のリスクにどう対応するかを示します。", p2_meaning=("Use this fixed frame to connect the proposal to a stakeholder's concrete risk.", "提案をステークホルダーの具体的なリスクに結びつける定型表現です。"), p2_rule=rule("Name the audience and the risk it actually faces", "対象と実際に直面するリスクを示す", "Use the fixed frame only for a risk the proposal genuinely reduces.", "提案が実際に低減するリスクに限って、定型表現を使います。", "For + audience, it addresses the risk of + risk", "Connect to stakeholder risk", "対象別のリスクに結びつける", ("operations · downtime", "finance · unexpected cost")), p2_write=("Which real risk does the proposal reduce for another stakeholder?", "この提案は、別のステークホルダーのどの実際のリスクを減らしますか？"), p2_omit_rule=True,
        scene_turns=(("other", "Why should finance support this service plan?", "なぜ経理はこのサービス計画を支持すべきですか？"), ("target", 1, 0), ("other", "And what matters to operations?", "運用部門にとって重要な点は何ですか？"), ("target", 2, 0), ("other", "Those are both supported by the service data.", "どちらもサービスデータで裏づけられています。"), ("me", "Good. I'll use those two messages in tomorrow's review.", "よいですね。明日のレビューでその二つを伝えます。")), receptive_=receptive(("finance", "The first audience is finance", "最初の対象は経理", "The first audience is operations", "最初の対象は運用"), ("predictable cost", "The finance message focuses on planning cost", "経理向けはコスト計画に焦点", "It promises lower cost", "コスト削減を約束する"), ("unplanned downtime", "The operations message focuses on continuity risk", "運用向けは継続性のリスクに焦点", "It focuses on hiring", "採用に焦点"), ("supported by data", "Both messages remain evidence-based", "どちらも根拠に基づく", "The proposal changes for each audience", "対象ごとに提案自体が変わる")), live_=live("Use a real or imaginary proposal and explain its value to two different stakeholders.", "実際または架空の提案を、二つの異なるステークホルダーに対する価値で説明してください。", "Real or imaginary: For ___, the key benefit is ___. For ___, it addresses the risk of ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "Which two stakeholders would you explain the same proposal to differently?", "同じ提案を異なる伝え方で説明するなら、先生はどの二つの対象を選びますか？"), tip=("Translate value, not facts", "事実ではなく価値の見せ方を変える", "Adapting a message changes which truthful benefit you lead with; it does not change the evidence or promise a result the proposal cannot deliver.", "伝え方を変えるとは、事実に基づくどの利点から話すかを変えることで、根拠を変えたり実現できない結果を約束したりすることではありません。", ("Tailored", "対象に合わせる", "lead with their priority", "相手の優先事項から話す"), ("Misleading", "誤解を招く", "change the claimed result", "誇う結果を変える")), transfer_title="Explaining a platform change", transfer_ja="プラットフォーム変更を説明する", transfer_role="Chief of Staff", transfer_turns=(("other", "How would you explain the platform change to sales?", "プラットフォーム変更を営業にどう説明しますか？"), ("target", 1, 1), ("other", "And what should legal hear?", "法務には何を伝えるべきですか？"), ("target", 2, 2), ("other", "Both points match the approved business case.", "どちらも承認済みの事業計画と一致します。"), ("me", "Then I'll keep the facts fixed and tailor the opening.", "では事実は変えず、導入だけ対象に合わせます。")), vocab=("stakeholder|ステークホルダー; predictable cost|予測可能なコスト; unplanned downtime|計画外停止; accountability|責任所在", "", "finance|経理; operations|運用; key benefit|最大の利点; risk|リスク; onboarding|導入", "tailor the message|伝え方を合わせる; business case|事業計画")),
    59: concise_lesson(
        slug="deliver-a-calm-crisis-update", title="Deliver a calm crisis update", ko="차분하게 위기 상황 전달하기", ja="危機時に落ち着いて状況を伝える", role="Client", scene="Updating a client during a service disruption", scene_ja="サービス障害中に顧客へ状況を伝える場面", situation="影響を過小評価せずに認め、原因は推測せず、次の更新を1時間以内に行うと約束します。", goal=("Acknowledge the disruption, avoid speculation, and commit to the next update.", "影響を認め、推測を避け、次の更新を約束しましょう。"), expressions=(("service disruption", "サービス障害"), ("restore service", "サービスを復旧する")),
        p1_rows=rows(("{t}We recognise the disruption{/t} this {t}is causing{/t}.", "これが引き起こしている{t}影響を重く受け止めています{/t}。", "We recognise|the disruption|this is causing."), ("{t}We recognise the pressure{/t} this {t}is creating{/t}.", "これが生み出している{t}負担を重く受け止めています{/t}。", "We recognise|the pressure|this is creating."), ("{t}We recognise the delay{/t} this {t}is causing{/t}.", "これが引き起こしている{t}遅れを認識しています{/t}。", "We recognise|the delay|this is causing."), ("{t}We recognise the uncertainty{/t} this {t}is creating{/t}.", "これが生み出している{t}不安を認識しています{/t}。", "We recognise|the uncertainty|this is creating.")), p1_bridge="まず、相手が受けている影響を明確に認めます。", p1_meaning=("Use this fixed frame to acknowledge the impact without making an unsupported promise.", "根拠のない約束をせずに、影響を認める定型表現です。"), p1_rule=rule("Keep the acknowledgement focused on impact", "影響に焦点を当てて認める", "Use this fixed frame for the real disruption people are experiencing.", "相手が実際に経験している影響に対して使う定型表現です。", "We recognise the + impact + this is causing", "Acknowledge impact", "影響を認める", ("disruption this is causing", "pressure this is creating")), p1_write=("What concrete impact should you acknowledge?", "どの具体的な影響を認めるべきですか？"), p1_omit_rule=True,
        p2_rows=rows(("{t}I don't want to speculate, but we'll{/t} provide another update within an hour.", "{t}推測でお伝えすることは避けますが{/t}、1時間以内に次の情報をお伝えします。", "I don't want to speculate,|but we'll provide|another update|within an hour."), ("{t}I don't want to speculate, but we'll{/t} confirm the cause by six.", "{t}推測でお伝えすることは避けますが{/t}、6時までに原因を確認します。", "I don't want to speculate,|but we'll confirm|the cause|by six."), ("{t}I don't want to speculate, but we'll{/t} share verified details at noon.", "{t}推測でお伝えすることは避けますが{/t}、正午に確認済みの詳細を共有します。", "I don't want to speculate,|but we'll share|verified details|at noon."), ("{t}I don't want to speculate, but we'll{/t} update this page every hour.", "{t}推測でお伝えすることは避けますが{/t}、このページを1時間ごとに更新します。", "I don't want to speculate,|but we'll update|this page|every hour.")), p2_bridge="次に、未確認の原因を推測せず、代わりに次の連絡を約束します。", p2_meaning=("Use this fixed frame to refuse speculation while remaining accountable for communication.", "推測を避けつつ、情報発信の責任を果たす定型表現です。"), p2_rule=rule("Follow the boundary with a timed commitment", "推測しない線引きと時間つきの約束", "Use the fixed frame as one unit, then give a specific next update.", "定型表現を一まとまりで使い、具体的な次の更新を示します。", "I don't want to speculate, but we'll + update", "Set a responsible boundary", "責任ある線引き", ("provide update within an hour", "confirm cause by six")), p2_write=("What update can you responsibly promise, and by when?", "責任を持って約束できる更新は何で、いつまでですか？"), p2_omit_rule=True,
        scene_turns=(("other", "Our teams cannot access the service.", "私たちのチームがサービスを利用できません。"), ("target", 1, 0), ("other", "Was the outage caused by last night's release?", "障害は昨夜のリリースが原因ですか？"), ("target", 2, 0), ("other", "Please send the update directly to our incident lead.", "次の情報は弊社の障害対応責任者に直接送ってください。"), ("me", "I will. You'll receive the verified status within an hour.", "承知しました。1時間以内に確認済みの状況をお送りします。")), receptive_=receptive(("cannot access", "The disruption affects current work", "障害は現在の業務に影響する", "The client reports a future risk", "顧客は将来のリスクを報告する"), ("recognise the disruption", "The impact is acknowledged", "影響を認めている", "The impact is minimised", "影響を過小評価する"), ("don't want to speculate", "The unconfirmed cause is not guessed", "未確認の原因を推測しない", "The release is blamed", "リリースを原因と決めつける"), ("within an hour", "The next update has a deadline", "次の更新に期限がある", "No update is promised", "次の更新を約束しない")), live_=live("Use a real or imaginary disruption: acknowledge the impact and promise a timed update without speculating.", "実際または架空の障害で、影響を認め、推測せずに時間つきの更新を約束してください。", "Real or imaginary: We recognise the disruption this is causing. I don't want to speculate, but we'll provide another update within ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "During a disruption, how soon could you promise the next update?", "障害中、先生は次の更新をどのくらいで約束できますか？"), tip=("Recognising disruption is not the same as accepting fault", "影響を認めることと過失を認めることは別", "You can acknowledge what people are experiencing before the cause or responsibility has been established.", "原因や責任が確定する前でも、相手が受けている影響は認められます。", ("Impact", "影響", "We recognise the disruption.", "影響を重く受け止めています。"), ("Fault", "過失", "We caused the outage.", "私たちが障害を起こしました。")), transfer_title="Updating staff during an access problem", transfer_ja="アクセス問題中に社員へ情報を伝える", transfer_role="Department Head", transfer_turns=(("other", "People cannot open the shared files.", "共有ファイルを開けない人がいます。"), ("target", 1, 2), ("other", "Was this caused by the security update?", "セキュリティ更新が原因ですか？"), ("target", 2, 2), ("other", "I'll tell staff to wait for the noon update.", "社員に正午の更新を待つよう伝えます。"), ("me", "Thank you. I'll share only verified details then.", "ありがとうございます。その時点で確認済みの詳細だけを共有します。")), vocab=("service disruption|サービス障害; speculate|推測する; incident lead|障害対応責任者; restore service|サービスを復旧する", "", "recognise|認める; pressure|負担; uncertainty|不安; cause|原因; update|更新情報", "accept fault|過失を認める; verified status|確認済みの状況")),
    60: concise_lesson(
        slug="make-an-executive-recommendation", title="Make an executive recommendation", ko="경영진 제언 전달하기", ja="経営層として提言する", role="Board Chair", scene="Recommending a limited first phase after reviewing evidence", scene_ja="根拠を確認したうえで限定的な第1段階を提言する場面", situation="推奨案を最初に明示し、小さく始めることで需要を検証しながら損失を抑えられるという核心的な理由で支えます。", goal=("State one clear recommendation and the decisive reason behind it.", "一つの明確な提言と、それを支える決定的な理由を示しましょう。"), expressions=(("limited first phase", "限定的な第1段階"), ("limit the downside", "損失を抑える")),
        p1_rows=rows(("{t}Overall, I recommend{/t} proceeding with a limited first phase.", "{t}総合的に判断して、限定的な第1段階を進めることを提言します{/t}。", "Overall,|I recommend proceeding|with a limited|first phase."), ("{t}Overall, I recommend{/t} renewing the contract for one year.", "{t}総合的に判断して、契約を1年更新することを提言します{/t}。", "Overall,|I recommend renewing|the contract|for one year."), ("{t}Overall, I recommend{/t} pausing expansion until June.", "{t}総合的に判断して、6月まで拡大を保留することを提言します{/t}。", "Overall,|I recommend pausing|expansion|until June."), ("{t}Overall, I recommend{/t} selecting the lower-risk option.", "{t}総合的に判断して、リスクの低い案を選ぶことを提言します{/t}。", "Overall,|I recommend selecting|the lower-risk|option.")), p1_bridge="まず、結論を一文で明確に示します。", p1_meaning=("Use this fixed frame to state the decision you recommend after considering the evidence.", "根拠を検討したうえで、推奨する判断を示す定型表現です。"), p1_rule=rule("Keep the recommendation complete and direct", "提言を完全で直接的に", "Use the fixed opening as one unit and follow it with one actionable recommendation.", "定型の導入を一まとまりで使い、実行可能な提言を一つ続けます。", "Overall, I recommend + action", "State the recommendation", "提言を明示する", ("proceed with phase one", "renew for one year")), p1_write=("What single course of action do you recommend?", "どの一つの行動を提言しますか？"), p1_omit_rule=True,
        p2_rows=rows(("{t}What it comes down to is that{/t} we can limit the downside while testing demand.", "{t}結局のところ重要なのは{/t}、需要を検証しながら損失を抑えられることです。", "What it comes down to|is that we can|limit the downside|while testing demand."), ("{t}What it comes down to is that{/t} we keep flexibility without losing momentum.", "{t}結局のところ重要なのは{/t}、勢いを失わずに柔軟性を保てることです。", "What it comes down to|is that we keep|flexibility|without losing momentum."), ("{t}What it comes down to is that{/t} the evidence does not support full expansion yet.", "{t}結局のところ重要なのは{/t}、根拠がまだ全面展開を支えるには不十分なことです。", "What it comes down to|is that the evidence|does not support|full expansion yet."), ("{t}What it comes down to is that{/t} the smaller option protects our core business.", "{t}結局のところ重要なのは{/t}、小さい案なら主力事業を守れることです。", "What it comes down to|is that the smaller option|protects|our core business.")), p2_bridge="次に、提言を支える最も重要な理由に絞ります。", p2_meaning=("Use this fixed frame to reduce a complex decision to the decisive consideration.", "複雑な判断を決定的な一つの要素に絞る定型表現です。"), p2_rule=rule("Follow the frame with the decisive reason", "表現のあとに決定的な理由", "Use this fixed frame for the consideration that actually drives the recommendation.", "実際に提言を左右する要素に対して使う定型表現です。", "What it comes down to is that + decisive reason", "Give the decisive reason", "決定的な理由を示す", ("limit downside · test demand", "protect core business")), p2_write=("What decisive reason supports your recommendation?", "あなたの提言を支える決定的な理由は何ですか？"), p2_omit_rule=True,
        scene_turns=(("other", "You've reviewed the market test and risk analysis. What do you recommend?", "市場テストとリスク分析を確認しましたね。どう提言しますか？"), ("target", 1, 0), ("other", "Why is that the best course?", "なぜそれが最善なのですか？"), ("target", 2, 0), ("other", "I support a six-month first phase with a review after three months.", "6か月の第1段階と、3か月後の見直しに賛成します。"), ("me", "Agreed. I'll bring that decision and review point to the board.", "同意します。その判断と見直し時点を取締役会に提示します。")), receptive_=receptive(("reviewed", "The recommendation follows evidence review", "提言は根拠の検討後に行われる", "The decision is a guess", "判断は推測である"), ("limited first phase", "The recommended commitment is bounded", "提言する確約は限定的", "Full expansion is recommended", "全面展開を提言する"), ("limit downside while testing demand", "The reason balances learning and risk", "理由は学習とリスクを両立させる", "Demand is already certain", "需要はすでに確定している"), ("review after three months", "The decision includes a review point", "判断に見直し時点がある", "The decision cannot be revisited", "判断は見直せない")), live_=live("Use a real or imaginary executive decision: give one recommendation and the decisive reason.", "実際または架空の経営判断で、一つの提言と決定的な理由を示してください。", "Real or imaginary: Overall, I recommend ___. What it comes down to is that ___.", "実際の例でも架空の例でも、二つの表現を使いましょう。", "What decision would you recommend after reviewing limited evidence?", "限られた根拠を検討したあと、先生はどんな判断を提言しますか？"), tip=("A recommendation needs a decision, not just a topic", "提言には話題ではなく判断が必要", "'I recommend discussing the pilot' names an activity; 'I recommend a six-month pilot' gives the group a course of action to approve.", "I recommend discussing the pilot は活動を示すだけですが、I recommend a six-month pilot は承認できる行動方針を示します。", ("Decision", "判断", "proceed with a six-month pilot", "6か月の試験導入を進める"), ("Topic", "話題", "discuss the pilot", "試験導入を話し合う")), transfer_title="Recommending a contract renewal", transfer_ja="契約更新を提言する", transfer_role="Audit Chair", transfer_turns=(("other", "The supplier improved, but we only have six months of data.", "供給元は改善しましたが、データは6か月分しかありません。"), ("target", 1, 1), ("other", "What is the decisive reason for one year?", "1年とする決定的な理由は何ですか？"), ("target", 2, 1), ("other", "That protects flexibility while keeping the work moving.", "それなら柔軟性を保ちつつ、仕事を進められます。"), ("me", "Exactly. I'll submit the one-year renewal for approval.", "その通りです。1年更新を承認申請します。")), vocab=("executive recommendation|経営層への提言; limited first phase|限定的な第1段階; downside|損失面; decisive reason|決定的な理由", "", "recommend|提言する; proceed|進める; demand|需要; expansion|拡大; evidence|根拠; contract renewal|契約更新", "come down to|結局は〜である; limit the downside|損失を抑える")),
})

# Exact bilingual target alignment and provenance corrections found by the
# batch's own entry-floor audit.  Keep these adjacent to the specifications so
# regeneration remains the sole output path.
LESSONS[56]["p1"]["rows"] = tuple(
    (english, japanese.replace("{t}ことです{/t}", "ことです"), chunks)
    for english, japanese, chunks in LESSONS[56]["p1"]["rows"]
)
_ordered_ja = {
    49: (
        "私なら、{t}こう呼びます{/t}——根本的な問題{t}ではなく{/t}、後退です。",
        "私なら、{t}こう呼びます{/t}——危機{t}ではなく{/t}、警告です。",
        "私なら、{t}こう呼びます{/t}——方針転換{t}ではなく{/t}、修正です。",
        "私なら、{t}こう呼びます{/t}——決裂要因{t}ではなく{/t}、制約です。",
    ),
    50: (
        "早い日程に{t}対応できます{/t}——範囲を縮小する{t}という条件なら{/t}。",
        "価格を{t}維持できます{/t}——契約期間が2年{t}という条件なら{/t}。",
        "研修を{t}追加できます{/t}——オンライン実施{t}という条件なら{/t}。",
        "5月に{t}開始できます{/t}——今週承認される{t}という条件なら{/t}。",
    ),
    51: (
        "その日程は{t}確約を控えたいです{/t}——{t}現時点では{/t}。",
        "数量は{t}確約を控えたいです{/t}——{t}現時点では{/t}。",
        "その価格は{t}確約を控えたいです{/t}——{t}現時点では{/t}。",
        "公開月は{t}確約を控えたいです{/t}——{t}現時点では{/t}。",
    ),
}
for _number, _part in ((49, 2), (50, 1), (51, 1)):
    LESSONS[_number][f"p{_part}"]["rows"] = tuple(
        (english, _ordered_ja[_number][index], chunks)
        for index, (english, _, chunks) in enumerate(LESSONS[_number][f"p{_part}"]["rows"])
    )

_ctx51_chunks = (
    "I'd rather not|commit to|that date|yet.",
    "I'd rather not|commit to|a quantity|yet.",
    "I'd rather not|commit to|that price|yet.",
    "I'd rather not|commit to|a launch month|yet.",
)
LESSONS[51]["p1"]["rows"] = tuple(
    (english, japanese, _ctx51_chunks[index])
    for index, (english, japanese, _) in enumerate(LESSONS[51]["p1"]["rows"])
)
LESSONS[56]["p2"]["rows"] = tuple(
    (
        english,
        japanese.replace("{t}あなたにしてほしいのは{/t}", "{t}お願いしたいのは{/t}"),
        chunks,
    )
    for english, japanese, chunks in LESSONS[56]["p2"]["rows"]
)
LESSONS[57]["p2"]["rows"] = rows(
    ("{t}We don't know{/t} that yet, {t}but we'll{/t} update everyone at four.",
     "それはまだ{t}分かりません{/t}。{t}ただし、必ず{/t}4時に全員に更新情報を伝えます。",
     "We don't know|that yet,|but we'll update everyone|at four."),
    ("{t}We don't know{/t} the cause yet, {t}but we'll{/t} update everyone at six.",
     "原因はまだ{t}分かりません{/t}。{t}ただし、必ず{/t}6時に全員に更新情報を伝えます。",
     "We don't know|the cause yet,|but we'll update everyone|at six."),
    ("{t}We don't know{/t} the full impact yet, {t}but we'll{/t} share another update at noon.",
     "影響の全容はまだ{t}分かりません{/t}。{t}ただし、必ず{/t}正午に次の情報を共有します。",
     "We don't know|the full impact yet,|but we'll share another update|at noon."),
    ("{t}We don't know{/t} when service will resume yet, {t}but we'll{/t} update this page hourly.",
     "サービスの再開時刻はまだ{t}分かりません{/t}。{t}ただし、必ず{/t}このページを1時間ごとに更新します。",
     "We don't know|when service will resume yet,|but we'll update this page|hourly."),
)
_ctx59_p1_ja = (
    "{t}この混乱を重く受け止めています{/t}。これはこの状況が実際に{t}引き起こしているものです{/t}。",
    "{t}この負担を重く受け止めています{/t}。これはこの状況が実際に{t}生み出しているものです{/t}。",
    "{t}この遅れを認識しています{/t}。これはこの状況が実際に{t}引き起こしているものです{/t}。",
    "{t}この不安を認識しています{/t}。これはこの状況が実際に{t}生み出しているものです{/t}。",
)
LESSONS[59]["p1"]["rows"] = tuple(
    (english, _ctx59_p1_ja[index], chunks)
    for index, (english, _, chunks) in enumerate(LESSONS[59]["p1"]["rows"])
)
LESSONS[59]["p2"]["rows"] = rows(
    ("{t}I don't want to speculate, but we'll{/t} provide another update within an hour.",
     "{t}推測でお伝えすることは避けますが、必ず{/t}1時間以内に次の情報をお伝えします。",
     "I don't want to speculate,|but we'll provide|another update|within an hour."),
    ("{t}I don't want to speculate, but we'll{/t} confirm the cause by six.",
     "{t}推測でお伝えすることは避けますが、必ず{/t}6時までに原因を確認します。",
     "I don't want to speculate,|but we'll confirm|the cause|by six."),
    ("{t}I don't want to speculate, but we'll{/t} share verified details at noon.",
     "{t}推測でお伝えすることは避けますが、必ず{/t}正午に確認済みの詳細を共有します。",
     "I don't want to speculate,|but we'll share|verified details|at noon."),
    ("{t}I don't want to speculate, but we'll{/t} update this page every hour.",
     "{t}推測でお伝えすることは避けますが、必ず{/t}このページを1時間ごとに更新します。",
     "I don't want to speculate,|but we'll update|this page|every hour."),
)
LESSONS[56]["vocab"] = (
    LESSONS[56]["vocab"][0], LESSONS[56]["vocab"][1],
    LESSONS[56]["vocab"][2] + "; recommendation|提言", LESSONS[56]["vocab"][3],
)
LESSONS[56]["vocab"] = (
    LESSONS[56]["vocab"][0], "", LESSONS[56]["vocab"][2], LESSONS[56]["vocab"][3],
)
LESSONS[53]["vocab"] = (
    LESSONS[53]["vocab"][0], LESSONS[53]["vocab"][1].replace("push back|異議を唱える|CORE-95; remedy|救済策|CTX-8", "push back|異議を唱える|CORE-95"),
    LESSONS[53]["vocab"][2], LESSONS[53]["vocab"][3] + "; remedy|救済策",
)
LESSONS[57]["vocab"] = (
    LESSONS[57]["vocab"][0], "", LESSONS[57]["vocab"][2] + "; secure|安全な", LESSONS[57]["vocab"][3],
)
LESSONS[59]["vocab"] = (
    LESSONS[59]["vocab"][0].replace("speculate|推測する; ", ""),
    "speculate|推測する|CTX-57", LESSONS[59]["vocab"][2], LESSONS[59]["vocab"][3],
)
LESSONS[60]["vocab"] = (
    LESSONS[60]["vocab"][0], "recommend|おすすめする|CTX-45",
    LESSONS[60]["vocab"][2].replace("recommend|提言する; ", ""), LESSONS[60]["vocab"][3],
)
for _number, _title in {
    51: "Push back on an unsafe commitment",
    52: "Explain a trade-off without oversimplifying it",
    53: "Acknowledge a point without giving up your position",
    54: "Break a negotiation deadlock",
    55: "Open a difficult performance conversation",
    56: "Give feedback that leads to action",
    57: "Lead through genuine uncertainty",
    58: "Persuade stakeholders with competing interests",
    59: "Communicate during a service crisis",
    60: "Make an executive recommendation under uncertainty",
}.items():
    LESSONS[_number]["title"] = _title
for _number, _scene in {
    49: "Correcting an exaggerated description",
    53: "Challenging a charge fairly",
    55: "Discussing repeated missed deadlines",
    60: "Recommending a limited first phase",
}.items():
    LESSONS[_number]["scene"] = _scene
for _number, _scene_ja in {
    49: "大げさな表現を修正する",
    53: "費用に公平に異議を唱える",
    55: "締め切り遅れを話す",
    60: "限定的な第1段階を提言する",
}.items():
    LESSONS[_number]["scene_ja"] = _scene_ja
for _number, _part in {
    (50, 1), (52, 1), (54, 1), (55, 1), (55, 2), (56, 1),
    (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2),
}:
    LESSONS[_number][f"p{_part}"]["omit_reorder"] = True
LESSONS[49]["transfer_turns"] = (
    ("other", "The pilot customers refused to commit and asked for more evidence. That proves the product is a failure.",
     "試験導入の顧客は確約を避け、さらなる根拠を求めました。これで製品の失敗は明らかです。"),
    *LESSONS[49]["transfer_turns"][1:],
)
LESSONS[53]["tip"] = (
    "Use 'That said' for a deliberate pivot", "考えたうえで転換する That said",
    "'That said' marks a more deliberate return to the remaining concern than a simple 'but.'",
    "「That said」 は、単なる but よりも、考えたうえで残る懸念に話を戻す表現です。",
    ("Deliberate pivot", "考えた転換", "That said, the amount is high.", "そうは言っても金額は高額です。"),
    ("Simple contrast", "単純な対比", "but the amount is high", "しかし金額は高額です"),
)
_ctx53_transfer = list(LESSONS[53]["transfer_turns"])
_ctx53_transfer[0] = (
    _ctx53_transfer[0][0], _ctx53_transfer[0][1],
    "停止が終わってすぐにクレジットを提示しました。",
)
LESSONS[53]["transfer_turns"] = tuple(_ctx53_transfer)
_ctx55_rows = list(LESSONS[55]["p1"]["rows"])
_ctx55_rows[0] = (
    _ctx55_rows[0][0], "直近3回の締め切りに間に合わなかったことに{t}気づきました{/t}。", _ctx55_rows[0][2],
)
LESSONS[55]["p1"]["rows"] = tuple(_ctx55_rows)
LESSONS[55]["scene_turns"] = (
    ("other", "You wanted to discuss my project work.", "私のプロジェクト作業について話したいとのことでしたね。"),
    ("target", 1, 0),
    ("other", "Yes, I know the deadlines have slipped.", "はい、締め切りが遅れていることは分かっています。"),
    ("target", 2, 0),
    ("other", "Two urgent requests arrive every afternoon. Protecting two mornings a week would help.",
     "毎日の午後に緊急依頼が2件届きます。週に2回、午前の時間を確保できると助かります。"),
    ("me", "Let's block those mornings and review progress next Friday.", "その午前を確保し、来週金曜日に進捗を確認しましょう。"),
)
LESSONS[55]["transfer_turns"] = (
    ("other", "You asked about my client communication.", "私の顧客対応についてですね。"),
    ("target", 1, 2),
    ("other", "Yes, I know the updates have been late.", "はい、更新が遅れていることは分かっています。"),
    ("target", 2, 1),
    ("other", "The approval data arrives after our calls. A morning data check would help.",
     "承認データが顧客との通話後に届きます。朝にデータを確認できると助かります。"),
    ("me", "I'll arrange that check from tomorrow.", "明日からその確認を手配します。"),
)
LESSONS[58]["tip"] = (
    *LESSONS[58]["tip"][:5],
    ("Misleading", "誤解を招く", "change the claimed result", "主張する結果を変える"),
)
LESSONS[60]["scene_turns"] = (
    ("other", "The market test is encouraging, but the demand forecast is still incomplete. What do you recommend?",
     "市場テストは好調ですが、需要予測はまだ不完全です。どう提言しますか？"),
    *LESSONS[60]["scene_turns"][1:],
)
LESSONS[60]["receptive"] = (
    ("forecast is still incomplete", "The recommendation must account for limited evidence", "提言では限られた根拠を考慮する",
     "Demand is already certain", "需要はすでに確定している"),
    *LESSONS[60]["receptive"][1:],
)
LESSONS[60]["live"] = (
    "Use a real or imaginary executive decision with an incomplete forecast. Give a qualified recommendation and the decisive reason.",
    "予測が不完全な実際または架空の経営判断で、条件を踏まえた提言と決定的な理由を示してください。",
    "Real or imaginary: The forecast is still incomplete. Overall, I recommend ___. What it comes down to is that ___.",
    "実際の例でも架空の例でも、不完全な予測を踏まえて二つの表現を使いましょう。",
    "When a forecast is incomplete, what limited decision would you recommend?",
    "予測が不完全なとき、先生はどんな限定的な判断を提言しますか？",
)


# Human-reviewed operating copy for the CTX49-60 page-by-page semantic pass.
# Supported translation pages expose only useful lexical help; articles,
# auxiliaries, inflections, and the taught frame remain learner work.  A
# checkpoint deliberately carries no hints.
REVIEWED_COPY_49_60 = {
    49: dict(
        role_ja="パートナー", transfer_role_ja="スポンサー",
        live=("Do people at work sometimes describe small problems too dramatically? Why or why not?", "職場では、小さな問題を大げさに表現することがありますか？なぜそう思いますか？", "Your opinion and a brief reason", "自分の意見と短い理由", "What about you—do you think that happens often?", "先生はどうですか？よくあると思いますか？"),
        p1=dict(write_frame="It's not so much ___ as ___", write_script="Use “It's not so much ___ as ___” to replace an exaggerated label with a more accurate description.", write_script_ja="「It's not so much ___ as ___」を使って、大げさな表現をより正確な説明に置き換えましょう。", translate_hints=((('失敗', 'failure'), ('遅れ', 'delay')), (('反対', 'resistance'), ('不確かさ', 'uncertainty')), (('費用の問題', 'cost problem'), ('時期の問題', 'timing problem')), (('拒否', 'refusal'), ('根拠を求めている', 'request for evidence')))),
        p2=dict(write_frame="I'd call it ___ rather than ___", write_script="Use “I'd call it ___ rather than ___” to give a measured label without dismissing the impact.", write_script_ja="「I'd call it ___ rather than ___」を使って、影響を軽視せずに穏当な表現で捉え直しましょう。", translate_hints=((('後退', 'setback'), ('根本的な問題', 'fundamental problem')), (('警告', 'warning'), ('危機', 'crisis')), (('修正', 'revision'), ('方針転換', 'reversal')), (('制約', 'constraint'), ('決裂要因', 'deal-breaker')))),
    ),
    50: dict(
        role_ja="顧客", transfer_role_ja="調達責任者",
        live=("In a negotiation, would you rather compromise on price, time, or scope? Why?", "交渉では、価格・時間・範囲のどれを譲歩しやすいですか？なぜですか？", "Your choice and a brief reason", "自分の選択と短い理由", "What about you—which one would you compromise on?", "先生はどうですか？どれを譲歩しますか？"),
        p1=dict(write_frame="We could ___, provided ___", write_script="Use “We could ___, provided ___” to offer one concession on a clear condition.", write_script_ja="「We could ___, provided ___」を使って、明確な条件と引き換えに一つの譲歩を提案しましょう。", translate_hints=((('早い日程', 'earlier date'), ('範囲を縮小する', 'reduce scope')), (('価格', 'price'), ('契約期間が2年', 'two-year term')), (('研修', 'training'), ('オンライン実施', 'remote')), (('5月', 'May'), ('承認', 'approval')))),
        p2=dict(write_frame="If you can defer ___, we can ___", write_script="Use “If you can defer ___, we can ___” to trade a delayed item for a deliverable.", write_script_ja="「If you can defer ___, we can ___」を使って、一項目の先送りと提供できる内容を交換条件にしましょう。", translate_hints=((('報告機能', 'reporting feature'), ('残りは6月まで', 'rest by June')), (('カスタム画面', 'custom dashboard'), ('5月', 'May')), (('2回目の研修', 'second workshop'), ('予算', 'budget')), (('地域展開', 'regional rollout'), ('試験導入', 'pilot')))),
    ),
    51: dict(
        role_ja="顧客", transfer_role_ja="購買担当者",
        live=("Which work promise would you be most careful about making too early?", "仕事では、どんな約束を早くしすぎないよう特に注意しますか？", "One promise and why it needs care", "約束を一つと、注意が必要な理由", "What about you—which promise would you avoid making too early?", "先生はどうですか？どんな約束を早くしないようにしますか？"),
        p1=dict(write_frame="I'd rather not commit to ___ yet", write_script="Use “I'd rather not commit to ___ yet” to keep one promise open until you have enough information.", write_script_ja="「I'd rather not commit to ___ yet」を使って、情報がそろうまで一つの約束を保留しましょう。", translate_hints=((('その日程', 'that date'),), (('数量', 'quantity'),), (('その価格', 'that price'),), (('公開月', 'launch month'),))),
        p2=dict(write_frame="It depends on whether ___", write_script="Use “It depends on whether ___” to name the condition that controls your answer.", write_script_ja="「It depends on whether ___」を使って、回答を左右する条件を伝えましょう。", translate_hints=((('供給元', 'supplier'), ('生産能力', 'capacity')), (('法務', 'legal'), ('条件', 'terms')), (('部品', 'parts'), ('明日', 'tomorrow')), (('予算', 'budget'),))),
    ),
    52: dict(
        role_ja="製品責任者", transfer_role_ja="導入責任者",
        live=("At work, which trade-off is harder for you: speed versus quality, or cost versus flexibility?", "仕事では、速さと品質、費用と柔軟性のどちらの両立が難しいですか？", "Your choice and why it is difficult", "自分の選択と、難しい理由", "What about you—which trade-off is harder?", "先生はどうですか？どちらの両立が難しいですか？"),
        p1=dict(write_frame="The ___, the less ___", write_script="Use “The ___, the less ___” to explain what is lost when one priority increases.", write_script_ja="「The ___, the less ___」を使って、一つを優先すると何が減るか説明しましょう。", translate_hints=((('テスト', 'testing'),), (('比較', 'comparison'),), (('研修', 'training'),), (('交渉', 'negotiation'),))),
        p2=dict(write_frame="The question is whether ___ or ___ matters more", write_script="Use “The question is whether ___ or ___ matters more” to name the two priorities the decision must balance.", write_script_ja="「The question is whether ___ or ___ matters more」を使って、判断で比べる二つの優先事項を示しましょう。", translate_hints=((('コスト', 'cost'), ('信頼性', 'reliability')), (('速さ', 'speed'), ('正確さ', 'accuracy')), (('届く範囲', 'reach'), ('管理のしやすさ', 'control')), (('柔軟性', 'flexibility'), ('確実性', 'certainty')))),
    ),
    53: dict(
        role_ja="供給元担当者", transfer_role_ja="サービス提供会社の担当者",
        live=("When you disagree with someone, is it easy for you to acknowledge their strongest point?", "誰かと意見が違うとき、相手の最も妥当な点を認めるのは簡単ですか？", "Your honest answer and why", "率直な答えと理由", "What about you—is that easy for you?", "先生はどうですか？簡単ですか？"),
        p1=dict(write_frame="To be fair, ___", write_script="Use “To be fair, ___” to acknowledge one valid point before you disagree.", write_script_ja="「To be fair, ___」を使って、反論する前に相手の妥当な点を一つ認めましょう。", translate_hints=((('納期', 'lead time'),), (('リスク', 'risk'),), (('代案', 'alternative'),), (('制約', 'limitation'),))),
        p2=dict(write_frame="That said, ___", write_script="Use “That said, ___” to return to the concern that still needs an answer.", write_script_ja="「That said, ___」を使って、まだ回答が必要な懸念に話を戻しましょう。", translate_hints=((('最終的な金額', 'final amount'),), (('遅れ', 'delay'),), (('救済策', 'remedy'),), (('条件', 'terms'),))),
    ),
    54: dict(
        role_ja="顧客", transfer_role_ja="パートナー",
        live=("When a discussion is stuck, do you prefer a partial agreement or more time to negotiate?", "話し合いが行き詰まったら、部分的な合意と交渉時間の延長のどちらを選びますか？", "Your preference and a brief reason", "自分の希望と短い理由", "What about you—which do you prefer?", "先生はどうですか？どちらを選びますか？"),
        p1=dict(write_frame="We seem to agree on ___, but not ___", write_script="Use “We seem to agree on ___, but not ___” to separate what is settled from what remains open.", write_script_ja="「We seem to agree on ___, but not ___」を使って、合意済みの点と未解決の点を分けましょう。", translate_hints=((('成果', 'outcome'), ('日程', 'timeline')), (('範囲', 'scope'), ('価格', 'price')), (('原則', 'principle'), ('表現', 'wording')), (('第1段階', 'first phase'), ('第2段階', 'second phase')))),
        p2=dict(write_frame="What if we agreed on ___ and revisited ___?", write_script="Use “What if we agreed on ___ and revisited ___?” to propose a partial agreement and a clear return point.", write_script_ja="「What if we agreed on ___ and revisited ___?」を使って、部分合意と再検討する時点を提案しましょう。", translate_hints=((('第1段階', 'phase one'), ('第2段階', 'phase two')), (('範囲', 'scope'), ('価格', 'price')), (('原則', 'principle'), ('表現', 'wording')), (('試験導入', 'pilot'), ('拡大', 'expansion')))),
    ),
    55: dict(
        role_ja="チームメンバー", transfer_role_ja="顧客担当者",
        live=("What makes a difficult feedback conversation feel fair?", "難しいフィードバックの会話が公平だと感じられるのは、どんなときですか？", "One thing that makes feedback fair", "フィードバックを公平にする点を一つ", "What about you—what makes feedback feel fair?", "先生はどうですか？どんなフィードバックなら公平だと感じますか？"),
        p1=dict(write_frame="I've noticed that ___", write_script="Use “I've noticed that ___” to describe a repeated work pattern without judging the person.", write_script_ja="「I've noticed that ___」を使って、相手を決めつけずに繰り返し起きている仕事上の事実を伝えましょう。", translate_hints=((('直近3回の締め切り', 'last three deadlines'),), (('週次の数値', 'weekly figures'),), (('顧客への連絡', 'client updates'),), (('引き継ぎ', 'handovers'),))),
        p2=dict(write_frame="I'd like to understand what's ___", write_script="Use “I'd like to understand what's ___” to invite the other person to explain the obstacle.", write_script_ja="「I'd like to understand what's ___」を使って、妨げになっていることを相手に説明してもらいましょう。", translate_hints=((('妨げ', 'getting in the way'),), (('遅れ', 'delay'),), (('今月', 'this month'),), (('引き継ぎ', 'handovers'),))),
    ),
    56: dict(
        role_ja="分析担当者", transfer_role_ja="戦略責任者",
        live=("Which kind of feedback helps you act fastest: a clear problem, an example, or a requested next step?", "どんなフィードバックなら最も早く行動できますか？明確な問題、具体例、次の行動の依頼のどれですか？", "Your choice and why it helps", "自分の選択と、役立つ理由", "What about you—which kind helps you act fastest?", "先生はどうですか？どれなら最も早く行動できますか？"),
        p1=dict(write_frame="___; the issue is that ___", write_script="Use “___; the issue is that ___” to recognise a strength and identify the problem that needs action.", write_script_ja="「___; the issue is that ___」を使って、良い点を認めたうえで改善が必要な問題を示しましょう。", translate_hints=((('分析', 'analysis'), ('要点', 'main point')), (('根拠', 'evidence'), ('結論', 'conclusion')), (('構成', 'structure'), ('提言', 'recommendation')), (('詳細', 'detail'), ('判断', 'decision')))),
        p2=dict(write_frame="What I'd like you to do is ___", write_script="Use “What I'd like you to do is ___” to request one specific revision.", write_script_ja="「What I'd like you to do is ___」を使って、具体的な修正を一つ依頼しましょう。", translate_hints=((('提言', 'recommendation'),), (('背景の部分', 'background section'),), (('予想される影響', 'expected impact'),), (('1ページ目', 'page one'),))),
    ),
    57: dict(
        role_ja="経営責任者", transfer_role_ja="取締役",
        live=("During uncertainty, what helps you trust a leader's update?", "先が見えない状況では、リーダーのどんな説明なら信頼できますか？", "One feature that builds trust and why", "信頼につながる特徴を一つと、その理由", "What about you—what makes an update trustworthy?", "先生はどうですか？どんな説明なら信頼できますか？"),
        p1=dict(write_frame="What we know is that ___", write_script="Use “What we know is that ___” to separate a verified fact from what is still uncertain.", write_script_ja="「What we know is that ___」を使って、確認できた事実をまだ不明な点と分けて伝えましょう。", translate_hints=((('顧客データ', 'customer data'),), (('バックアップ', 'backup'),), (('決済処理', 'payments'),), (('一つの地域', 'one region'),))),
        p2=dict(write_frame="We don't know ___ yet, but we'll ___", write_script="Use “We don't know ___ yet, but we'll ___” to admit one unknown and promise a specific update.", write_script_ja="「We don't know ___ yet, but we'll ___」を使って、不明点を認め、次の具体的な更新を約束しましょう。", translate_hints=((('4時', 'four'),), (('原因', 'cause'), ('6時', 'six')), (('影響の全容', 'full impact'), ('正午', 'noon')), (('サービスの再開時刻', 'service resumption'), ('1時間ごと', 'hourly')))),
    ),
    58: dict(
        role_ja="プログラム責任者", transfer_role_ja="経営企画責任者",
        live=("Whose support is usually hardest to win for a new idea, and why?", "新しい案への支持を得るのが最も難しいのは、どんな立場の人ですか？なぜですか？", "One stakeholder and a brief reason", "関係者を一人と短い理由", "What about you—whose support is hardest to win?", "先生はどうですか？誰の支持を得るのが最も難しいですか？"),
        p1=dict(write_frame="For ___, the key benefit is ___", write_script="Use “For ___, the key benefit is ___” to connect one stakeholder to the value they care about.", write_script_ja="「For ___, the key benefit is ___」を使って、関係者と、その人が重視する価値を結びつけましょう。", translate_hints=((('経理', 'finance'), ('コストを予測できる', 'predictable cost')), (('営業', 'sales'), ('導入が早くなる', 'faster onboarding')), (('法務', 'legal'), ('責任所在が明確', 'clearer accountability')), (('顧客', 'customers'), ('対応が早くなる', 'quicker support')))),
        p2=dict(write_frame="For ___, it addresses the risk of ___", write_script="Use “For ___, it addresses the risk of ___” to connect a stakeholder to the risk the proposal reduces.", write_script_ja="「For ___, it addresses the risk of ___」を使って、関係者と、提案が減らすリスクを結びつけましょう。", translate_hints=((('運用', 'operations'), ('計画外停止', 'unplanned downtime')), (('経理', 'finance'), ('予期しないコスト', 'unexpected cost')), (('法務', 'legal'), ('担当の不明確さ', 'unclear ownership')), (('顧客', 'customers'), ('復旧の遅れ', 'slow recovery')))),
    ),
    59: dict(
        role_ja="顧客", transfer_role_ja="部門責任者",
        live=("During a service problem, which matters more to you: frequent updates or detailed updates?", "サービス障害のとき、頻繁な更新と詳しい更新のどちらが重要ですか？", "Your preference and why", "自分の希望と理由", "What about you—which matters more?", "先生はどうですか？どちらが重要ですか？"),
        p1=dict(write_frame="We recognise the ___ this is causing", write_script="Use “We recognise the ___ this is causing” to acknowledge the real effect of a service problem.", write_script_ja="「We recognise the ___ this is causing」を使って、サービス障害が実際に与えている影響を認めましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="I don't want to speculate, but we'll ___", write_script="Use “I don't want to speculate, but we'll ___” to avoid guessing and promise one verified update.", write_script_ja="「I don't want to speculate, but we'll ___」を使って、推測を避け、確認済みの更新を一つ約束しましょう。", translate_hints=((('次の情報', 'another update'), ('1時間以内', 'within an hour')), (('原因', 'cause'), ('6時', 'six')), (('確認済みの詳細', 'verified details'), ('正午', 'noon')), (('このページ', 'this page'), ('1時間ごと', 'every hour')))),
    ),
    60: dict(
        role_ja="取締役会議長", transfer_role_ja="監査委員長",
        live=("When evidence is incomplete, are you comfortable making a small reversible decision? Why or why not?", "根拠が不完全なとき、小さくて見直せる判断ならできますか？なぜですか？", "Your honest answer and a brief reason", "率直な答えと短い理由", "What about you—are you comfortable with that?", "先生はどうですか？そのような判断はできますか？"),
        p1=dict(write_frame="Overall, I recommend ___", write_script="Use “Overall, I recommend ___” to give one bounded course of action after reviewing the evidence.", write_script_ja="「Overall, I recommend ___」を使って、根拠を検討したうえで限定的な行動方針を一つ提言しましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="What it comes down to is that ___", write_script="Use “What it comes down to is that ___” to state the decisive reason for your recommendation.", write_script_ja="「What it comes down to is that ___」を使って、提言を支える決定的な理由を伝えましょう。", translate_hints=((('損失', 'downside'), ('需要', 'demand')), (('柔軟性', 'flexibility'), ('勢い', 'momentum')), (('根拠', 'evidence'), ('全面展開', 'full expansion')), (('小さい案', 'smaller option'), ('主力事業', 'core business')))),
    ),
}

for _number, _copy in REVIEWED_COPY_49_60.items():
    _lesson = LESSONS[_number]
    _lesson["role_ja"] = _copy["role_ja"]
    _lesson["transfer_role_ja"] = _copy["transfer_role_ja"]
    _lesson["live"] = _copy["live"]
    _lesson.pop("live_sequence", None)
    for _part in (1, 2):
        _lesson[f"p{_part}"].update(_copy[f"p{_part}"])

    _owned_english = {
        _entry.split("|")[0].strip().casefold()
        for _category in _lesson["vocab"]
        for _entry in _category.split(";")
        if _entry.strip()
    }
    _support_additions = []
    for _part in (1, 2):
        for _hint_row in _lesson[f"p{_part}"].get("translate_hints", ()):
            if len(_hint_row) == 2 and all(isinstance(_item, str) for _item in _hint_row):
                _hint_row = (_hint_row,)
            for _japanese_hint, _english_hint in _hint_row:
                if _english_hint.casefold() not in _owned_english:
                    _support_additions.append(f"{_english_hint}|{_japanese_hint}")
                    _owned_english.add(_english_hint.casefold())
    if _support_additions:
        _vocab = list(_lesson["vocab"])
        _vocab[2] = "; ".join(filter(None, (_vocab[2], *_support_additions)))
        _lesson["vocab"] = tuple(_vocab)


# Preserve one teachable frame across the completion rows.  The changing
# decision payload stays visible; only the reusable language move is blanked.
LESSONS[52]["p1"]["rows"] = rows(
    ("{t}The faster we move,{/t} {t}the less time we'll have for{/t} testing.", "{t}早く進むほど、{/t}テスト{t}に使える時間は少なくなります{/t}。", "The faster we move,|the less time|we'll have|for testing."),
    ("{t}The faster we move,{/t} {t}the less time we'll have for{/t} a proper comparison.", "{t}早く進むほど、{/t}十分な比較{t}に使える時間は少なくなります{/t}。", "The faster we move,|the less time|we'll have|for a proper comparison."),
    ("{t}The faster we move,{/t} {t}the less time we'll have for{/t} training.", "{t}早く進むほど、{/t}研修{t}に使える時間は少なくなります{/t}。", "The faster we move,|the less time|we'll have|for training."),
    ("{t}The faster we move,{/t} {t}the less time we'll have for{/t} the client to review it.", "{t}早く進むほど、{/t}顧客が確認する{t}時間は少なくなります{/t}。", "The faster we move,|the less time|we'll have|for the client to review it."),
)
LESSONS[52]["p1"].update(
    write_frame="The faster we move, the less time we'll have for ___",
    write_script="Use “The faster we move, the less time we'll have for ___” to explain what an earlier decision would leave less time for.",
    write_script_ja="「The faster we move, the less time we'll have for ___」を使って、決定を早めると何に使える時間が減るか説明しましょう。",
)
LESSONS[59]["p1"]["rows"] = rows(
    ("{t}We recognise the{/t} disruption {t}this is causing{/t}.", "{t}これにより生じている{/t}業務の混乱{t}を認識しています{/t}。", "We recognise|the disruption|this is causing."),
    ("{t}We recognise the{/t} pressure on your teams {t}this is causing{/t}.", "{t}これにより生じている{/t}現場のご負担{t}を認識しています{/t}。", "We recognise|the pressure on your teams|this is causing."),
    ("{t}We recognise the{/t} delay {t}this is causing{/t}.", "{t}これにより生じている{/t}遅れ{t}を認識しています{/t}。", "We recognise|the delay|this is causing."),
    ("{t}We recognise the{/t} operational uncertainty {t}this is causing{/t}.", "{t}これにより生じている{/t}業務上のご不安{t}を認識しています{/t}。", "We recognise|the operational uncertainty|this is causing."),
)


# The Understand page is tutor-read listening.  Every prompt is a complete
# counterpart line from the opening or transfer roleplay, never a learner
# target fragment or an isolated clause.
REVIEWED_RECEPTIVE_49_60 = {
    49: (
        ("This three-week delay means the project has failed.", "The partner describes a delay as total failure", "相手は遅れを全面的な失敗と表現している", "The partner says the project is ahead of schedule", "相手は計画が予定より進んでいると言っている"),
        ("The delay still has a cost.", "The partner accepts the distinction but keeps the impact visible", "相手は違いを認めつつ影響を重視している", "The partner withdraws every concern", "相手は懸念をすべて取り下げている"),
        ("That's fair, provided we recover quickly.", "Agreement depends on a quick recovery", "同意には早い立て直しが必要である", "Agreement is unconditional", "無条件で同意している"),
        ("So how would you describe the result?", "The sponsor asks for a more accurate label", "スポンサーはより正確な表現を求めている", "The sponsor ends the discussion", "スポンサーは話し合いを終える"),
    ),
    50: (
        ("We need the full product a month earlier.", "The client wants the same scope sooner", "顧客は同じ範囲をより早く求めている", "The client wants fewer features later", "顧客は機能を減らして遅く求めている"),
        ("What exactly would you take out?", "The client asks which scope item would be removed", "顧客はどの範囲を外すか尋ねている", "The client asks who approved the contract", "顧客は契約の承認者を尋ねている"),
        ("That may work. Put it in the revised proposal.", "The client sees the condition as possible and wants it in writing", "顧客は条件を可能と見て書面化を求めている", "The client rejects every change", "顧客はすべての変更を拒否している"),
        ("Which part would move out of the first phase?", "The procurement lead asks what will be deferred", "調達責任者は何を先送りするか尋ねている", "The procurement lead asks for an apology", "調達責任者は謝罪を求めている"),
    ),
    51: (
        ("Can you guarantee delivery on June 10?", "The customer asks for a firm delivery promise", "顧客は確定した納品の約束を求めている", "The customer cancels the delivery", "顧客は納品を中止する"),
        ("What information are you waiting for?", "The customer asks what prevents a commitment", "顧客は確約を妨げる情報を尋ねている", "The customer confirms every detail", "顧客はすべての詳細を確定する"),
        ("When will you know?", "The customer asks for the next update time", "顧客は次の連絡時刻を尋ねている", "The customer refuses another update", "顧客は次の連絡を断る"),
        ("We can wait until the budget decision on Friday.", "The buyer agrees to wait for a named dependency", "購買担当者は条件が確定するまで待つ", "The buyer demands an immediate guarantee", "購買担当者は即時の保証を求める"),
    ),
    52: (
        ("Could we launch two weeks earlier?", "The product owner asks about an earlier launch", "製品責任者は公開を早められるか尋ねている", "The product owner postpones the launch indefinitely", "製品責任者は公開を無期限に延期する"),
        ("Then what should guide the decision?", "The product owner asks which priority should decide", "製品責任者は判断基準を尋ねている", "The product owner says no decision is needed", "製品責任者は判断が不要だと言っている"),
        ("Reliability matters more for this release.", "The product owner prioritises reliability", "製品責任者は信頼性を優先している", "The product owner prioritises speed", "製品責任者は速さを優先している"),
        ("Which priority should decide this?", "The implementation lead asks for the decisive priority", "導入責任者は決定的な優先事項を尋ねている", "The implementation lead cancels the decision", "導入責任者は判断を中止する"),
    ),
    53: (
        ("We told you the rush order would take longer.", "The supplier reminds the learner of an earlier warning", "供給元は以前の説明を確認している", "The supplier says there was no warning", "供給元は説明がなかったと言っている"),
        ("Then do you accept the extra charge?", "The supplier asks whether the charge is accepted", "供給元は追加費用を受け入れるか尋ねている", "The supplier offers a full refund", "供給元は全額返金を申し出る"),
        ("I'll review the calculation with finance today.", "The supplier promises to check the amount", "供給元は金額を確認すると約束している", "The supplier refuses to review the bill", "供給元は請求の確認を断る"),
        ("Do you think the credit is insufficient?", "The service provider asks whether the remedy is enough", "サービス提供会社は対応が十分か尋ねている", "The provider cancels the credit", "サービス提供会社はクレジットを取り消す"),
    ),
    54: (
        ("We both want the full rollout, but we need it in May.", "The client shares the outcome but disputes the timing", "顧客は成果には合意し日程では意見が違う", "The client rejects the rollout itself", "顧客は展開自体を拒否している"),
        ("How can we move forward today?", "The client asks for a practical way past the deadlock", "顧客は行き詰まりを進める方法を尋ねている", "The client ends the negotiation", "顧客は交渉を終える"),
        ("Yes. We can approve phase one today.", "The client accepts a partial agreement", "顧客は部分的な合意を受け入れている", "The client rejects phase one", "顧客は第1段階を拒否している"),
        ("What can we decide this week?", "The partner asks what can be settled now", "パートナーは今決められることを尋ねている", "The partner asks to reopen every issue", "パートナーはすべての論点を再開しようとしている"),
    ),
    55: (
        ("You wanted to discuss my project work.", "The team member opens the performance conversation", "チームメンバーは面談の話題を確認している", "The team member refuses to talk", "チームメンバーは話し合いを断る"),
        ("Yes, I know the deadlines have slipped.", "The team member recognises the repeated delay", "チームメンバーは締め切りの遅れを認識している", "The team member says every deadline was met", "チームメンバーはすべて締め切りどおりだったと言っている"),
        ("Two urgent requests arrive every afternoon. Protecting two mornings a week would help.", "The team member explains an obstacle and suggests support", "チームメンバーは障害と必要な支援を説明している", "The team member says no support is needed", "チームメンバーは支援が不要だと言っている"),
        ("The approval data arrives after our calls. A morning data check would help.", "The account manager explains why updates are late", "顧客担当者は更新が遅れる原因を説明している", "The account manager says the data always arrives early", "顧客担当者はデータがいつも早く届くと言っている"),
    ),
    56: (
        ("What did you think of the briefing?", "The analyst asks for feedback on the briefing", "分析担当者は説明資料への感想を求めている", "The analyst cancels the briefing", "分析担当者は説明を中止する"),
        ("What should I change first?", "The analyst asks for one first revision", "分析担当者は最初の修正点を尋ねている", "The analyst refuses to revise anything", "分析担当者は修正を断る"),
        ("I'll move the recommendation to the opening slide.", "The analyst accepts the requested action", "分析担当者は依頼された修正を受け入れている", "The analyst will remove the recommendation", "分析担当者は提言を削除する"),
        ("What revision would fix that?", "The strategy manager asks for a specific corrective action", "戦略責任者は具体的な修正を尋ねている", "The strategy manager says no revision is possible", "戦略責任者は修正できないと言っている"),
    ),
    57: (
        ("Is customer data at risk?", "The executive asks about verified customer-data risk", "経営責任者は顧客データのリスクを尋ねている", "The executive says the incident is over", "経営責任者は障害が終わったと言っている"),
        ("Do we know what caused the incident?", "The executive asks about an unknown cause", "経営責任者はまだ不明な原因を尋ねている", "The executive confirms the cause", "経営責任者は原因を確定している"),
        ("Good. I'll direct questions to the four o'clock update.", "The executive accepts the next update time", "経営責任者は次の更新時刻を受け入れている", "The executive asks staff to speculate", "経営責任者は推測するよう求めている"),
        ("When will we know the full impact?", "The board member asks when more verified information will arrive", "取締役は追加の確認情報がいつ出るか尋ねている", "The board member says no update is needed", "取締役は更新が不要だと言っている"),
    ),
    58: (
        ("Why should finance support this service plan?", "The programme director asks for finance's benefit", "プログラム責任者は経理にとっての利点を尋ねている", "The director asks about a holiday", "責任者は休暇について尋ねている"),
        ("And what matters to operations?", "The programme director asks about operations' concern", "プログラム責任者は運用部門の懸念を尋ねている", "The director says operations has no role", "責任者は運用部門は関係ないと言っている"),
        ("Those are both supported by the service data.", "The programme director confirms evidence for both claims", "プログラム責任者は二つの主張の根拠を確認している", "The director says there is no evidence", "責任者は根拠がないと言っている"),
        ("And what should legal hear?", "The chief of staff asks for the message to legal", "経営企画責任者は法務への説明を尋ねている", "The chief of staff cancels the proposal", "経営企画責任者は提案を中止する"),
    ),
    59: (
        ("Our teams cannot access the service.", "The client describes the current disruption", "顧客は現在のサービス障害を説明している", "The client says service is working normally", "顧客はサービスが正常だと言っている"),
        ("Was the outage caused by last night's release?", "The client asks about an unverified cause", "顧客は未確認の原因を尋ねている", "The client confirms the exact cause", "顧客は原因を確定している"),
        ("Please send the update directly to our incident lead.", "The client names who should receive the update", "顧客は更新情報の受取人を指定している", "The client asks to stop all updates", "顧客は更新をやめるよう求めている"),
        ("I'll tell staff to wait for the noon update.", "The department head accepts a specific update time", "部門責任者は具体的な更新時刻を受け入れている", "The department head asks staff to guess", "部門責任者は職員に推測するよう求めている"),
    ),
    60: (
        ("The market test is encouraging, but the demand forecast is still incomplete. What do you recommend?", "The board chair asks for a recommendation under uncertainty", "取締役会議長は不確実な状況で提言を求めている", "The board chair says demand is certain", "取締役会議長は需要が確定していると言っている"),
        ("Why is that the best course?", "The board chair asks for the decisive reason", "取締役会議長は決定的な理由を尋ねている", "The board chair asks for a meeting time", "取締役会議長は会議時刻を尋ねている"),
        ("I support a six-month first phase with a review after three months.", "The board chair supports a bounded decision with a review point", "取締役会議長は見直し時点のある限定的な判断を支持している", "The board chair supports immediate full expansion", "取締役会議長は即時の全面展開を支持している"),
        ("What is the decisive reason for one year?", "The audit chair asks why the renewal should be limited", "監査委員長は限定更新の理由を尋ねている", "The audit chair asks for a permanent contract", "監査委員長は無期限契約を求めている"),
    ),
}

for _number, _receptive in REVIEWED_RECEPTIVE_49_60.items():
    LESSONS[_number]["receptive"] = _receptive


def _move_new_vocab_to_receptive(number: int, *terms: str) -> None:
    """Keep pre-taught terms out of the productive new-vocabulary bucket."""

    new, recycled, assumed, receptive_vocab = LESSONS[number]["vocab"]
    new_items = [item for item in new.split("; ") if item]
    receptive_items = [item for item in receptive_vocab.split("; ") if item]
    for term in terms:
        prefix = f"{term}|"
        matches = [item for item in new_items if item.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError(f"CTX-{number}: expected one new-vocabulary item for {term!r}")
        item = matches[0]
        new_items.remove(item)
        receptive_items.append(item)
    LESSONS[number]["vocab"] = ("; ".join(new_items), recycled, assumed, "; ".join(receptive_items))


_move_new_vocab_to_receptive(55, "observable")
_move_new_vocab_to_receptive(56, "executive briefing", "decision memo")
_move_new_vocab_to_receptive(57, "uncertainty")
_move_new_vocab_to_receptive(59, "incident lead")
_move_new_vocab_to_receptive(60, "executive recommendation")

COURSES = {
    range(49, 55): ("ctx-business-negotiation-diplomacy", "B2", "BUSINESS ENGLISH", "Negotiator", "交渉担当者"),
    range(55, 61): ("ctx-business-leadership-high-stakes", "C1", "BUSINESS ENGLISH", "Leader", "リーダー"),
}

AUTHORITATIVE = {
    number: (lesson["title"], core.strip_marks(lesson["p1"]["rows"][0][0]), core.strip_marks(lesson["p2"]["rows"][0][0]))
    for number, lesson in LESSONS.items()
}

LIVE_FRAME_CONTRACTS = {
    49: ("It's not so much", " as ", "I'd call it", "rather than"),
}


@contextlib.contextmanager
def renderer_scope():
    names = ("COURSES", "LESSONS", "AUTHORITATIVE", "LIVE_FRAME_CONTRACTS", "VISIBLE_PRIOR_CTX_OWNERS")
    previous = {name: getattr(renderer, name) for name in names}
    try:
        renderer.COURSES = COURSES
        renderer.LESSONS = LESSONS
        renderer.AUTHORITATIVE = AUTHORITATIVE
        renderer.LIVE_FRAME_CONTRACTS = LIVE_FRAME_CONTRACTS
        renderer.VISIBLE_PRIOR_CTX_OWNERS = set()
        yield
    finally:
        for name, value in previous.items():
            setattr(renderer, name, value)


def validate_lesson(number, lesson):
    with renderer_scope():
        renderer.validate_lesson(number, lesson)


def build(number, lesson):
    with renderer_scope():
        output, source = renderer.build(number, lesson)
    # The receptive pool deliberately includes complete counterpart lines from
    # both the opening scene and the transfer scene.  Name the tutor's action
    # without falsely assigning every line to the opening-scene role.
    source = re.sub(
        r"I’ll read each [^.]+ line\. Choose what it means\.",
        "I’ll read each line. Choose what it means.",
        source,
        count=1,
    )
    source = re.sub(
        r"私が[^<。]+のセリフを読みます。意味を選んでください。",
        "私がそれぞれのセリフを読みます。意味を選んでください。",
        source,
        count=1,
    )
    complete = '<meta name="podo:proofread-status" content="complete">'
    if source.count(complete) != 1 or 'name="podo:proofread-status" content="pending"' in source:
        raise ValueError(f"CTX-{number}: renderer proofread marker shape drifted")
    if number in {49, 53, 55, 60}:
        start = source.index('data-page-id="scene"')
        end = source.index('</h2>', start)
        heading = source[start:end].replace('<span class="title-ja">', '<br><span class="title-ja">', 1)
        source = source[:start] + heading + source[end:]
    if number == 53:
        start = source.index('data-page-id="p2-teach"')
        end = source.index('data-page-id="p2-read"', start)
        page = source[start:end].replace("That said,</span> the final amount still seems disproportionate", "That said,</span><br> the final amount<br> still seems<br> dispropor<wbr>tionate", 1)
        source = source[:start] + page + source[end:]
    if number == 56:
        start = source.index('data-page-id="p2-teach"')
        end = source.index('data-page-id="p2-read"', start)
        page = source[start:end].replace(
            "What I&#x27;d like you to do is</span> lead with the recommendation",
            "What I&#x27;d like <br>you to do is</span><br> lead with<br> the recom<wbr>mendation",
            1,
        )
        source = source[:start] + page + source[end:]
    return output, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, action="append", choices=sorted(LESSONS))
    args = parser.parse_args()
    selected = set(args.lesson or LESSONS)
    for number, lesson in LESSONS.items():
        if number not in selected:
            continue
        output, source = build(number, lesson)
        if output.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(source, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    print(f"{len(selected)} Contextual decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
