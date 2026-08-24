#!/usr/bin/env python3
"""Author and, after pilot release, render paired FT 101-106 source decks.

Importing this module is deliberately source-only.  Repository reads and the
pilot-dependent renderer remain behind ``build``/``output_path``/``main`` so a
reviewer can audit this batch while the canonical FT-1 shell is protected.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


COURSE = "talk-worth-thinking-about"
TOPIC_NUMBERS = tuple(range(101, 107))
VARIANTS = ("accessible", "full")
SENSITIVE_TOPICS = frozenset({102, 103, 104, 105})

# Freetalking enters after CORE-53.  Later Core references are useful retrieval
# evidence but are not legal vocabulary owners for this batch.
FUTURE_CORE_DEPENDENCIES = {
    101: ("CORE-89",), 102: ("CORE-99",), 103: ("CORE-117",),
    104: ("CORE-115", "CORE-116"), 106: ("CORE-117",),
}
REACHABLE_CORE_RETRIEVAL = {
    101: ("CORE-51",), 102: ("CORE-18",), 106: ("CORE-49",),
}
TOPIC_FORMAT = {number: "opinion" for number in TOPIC_NUMBERS}
SHARED_SOURCE = {
    101: "KR 10-1", 102: "KR 10-3", 103: "KR 10-4",
    104: "KR 10-5", 105: "KR 10-6", 106: "NEW → KR",
}
TOC_RETRIEVAL = {
    101: (("I'd last about ___.", ("CORE-51",), True), ("It's not so much ___ as ___.", ("CORE-89",), True)),
    102: (("It still can't ___.", ("CORE-18",), False), ("That suggests that ___.", ("CORE-99",), True)),
    103: (("That's true up to a point, but ___.", (), True), ("Overall, I'd say ___.", ("CORE-117",), True)),
    104: (("If anything, ___.", ("CORE-116",), True), ("That's true, but it doesn't account for ___.", ("CORE-115",), True)),
    105: (("I'd have ___ differently.", (), True), ("It still made sense at the time.", (), True)),
    106: (("I've noticed that ___.", ("CORE-49",), False), ("Overall, it's made me ___.", ("CORE-117",), True)),
}
TOC_RETRIEVAL_AUDIT_ONLY = True

BRIEF_OPENINGS = {
    101: "Would three days away from social media feel too short, too long, or about right?",
    102: "What is one thing AI does badly when it tries to do human work?",
    103: "When someone says, ‘I have enough money,’ what do you imagine they can afford?",
    104: "If you could stay one age for ten years, which age would you choose?",
    105: "Would you rather change a movie ending or a real historical decision?",
    106: "What has speaking English made you notice about Japanese?",
}


def prompt(job, title, title_ja, accessible, accessible_ja, followups, *, full, full_ja, safety, full_followups=None):
    return {
        "job": job, "title": title, "title_ja": title_ja,
        "accessible": accessible, "accessible_ja": accessible_ja,
        "accessible_followups": followups, "full": full, "full_ja": full_ja,
        "full_followups": full_followups if full_followups is not None else followups,
        "safety": safety,
    }


def topic(*, slug, title, ko, ja, goal, article_title, articles, prompts):
    return locals()


# Every article row is (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
    101: topic(
        slug="how-long-should-a-social-media-break-last", title="How long should a social-media break last?",
        ko="SNS 휴식 기간", ja="SNSを休む期間",
        goal=("Let's weigh what social media gives us against what it costs.", "SNSから得るものと、そのために使う時間や注意の両方を考えましょう。"),
        article_title=("What a break actually tests", "SNSを休むと分かること"),
        articles=[
            ("A break from social media can mean an hour, a week, or a permanent choice.", "A social-media break can range from a brief experiment to a permanent boundary.", "SNSを休む期間は、一時間、一週間、またはずっと離れるという選択もあります。", "SNSを休む期間は、短い実験から、ずっと使わないという線引きまで幅があります。"),
            ("The difficult part is different for each person.", "The hardest loss depends on which social need or practical task the platform serves.", "何が難しいかは人によって違います。", "最も困ることは、そのサービスがどんな人間関係や実用的な役割を支えているかで変わります。"),
            ("Some people would miss messages more than public posts.", "For many users, private coordination matters more than public performance.", "公開投稿よりも、メッセージが使えないことのほうが困る人もいます。", "多くの利用者にとって、公開の発信より、個人的な連絡や予定調整のほうが重要です。"),
            ("An app can be useful and still become a time sink.", "A useful platform can still become a time sink when checking loses a clear purpose.", "便利なアプリでも、時間を奪うものになることがあります。", "役立つサービスでも、目的なく確認するようになると時間を奪うものになります。"),
            ("Deleting an app does not remove every reason to reach for it.", "Removing an app changes access, but it does not automatically change the cue behind the habit.", "アプリを消しても、開きたくなる理由がすべてなくなるわけではありません。", "アプリを削除すれば使いにくくなりますが、習慣を始めるきっかけまで自動的に消えるわけではありません。"),
            ("Work, family, safety, or community may make one service hard to leave.", "Employment, care, safety, or community ties can make complete withdrawal unrealistic.", "仕事、家族、安全、地域とのつながりのため、やめにくいサービスもあります。", "仕事、ケア、安全、地域とのつながりによって、完全に離れるのが現実的でない場合もあります。"),
            ("A clear limit may work better than an all-or-nothing rule.", "A targeted boundary may be more sustainable than treating every platform alike.", "全部やめるより、明確な制限のほうが合う人もいます。", "すべてのサービスを同じように扱うより、目的を絞った制限のほうが続きやすい場合があります。"),
            ("Young users need guidance as well as limits.", "Teenagers need practical boundaries without being denied the social world their peers inhabit.", "若い利用者には、制限だけでなく使い方の助言も必要です。", "十代には現実的な境界線が必要ですが、同世代がいる社会的な場から締め出すべきではありません。"),
            ("People who manage social media well often know why they are opening it.", "Intentional users tend to distinguish communication, information, entertainment, and automatic checking.", "SNSを上手に使う人は、何のために開くのか分かっていることが多いです。", "意識的に使う人は、連絡、情報、娯楽、無意識の確認を区別する傾向があります。"),
            ("The useful question is not only how long we can stop, but what we want back.", "The deeper test is not endurance alone but which attention, relationships, or functions we want to reclaim.", "大切なのは、何日やめられるかだけでなく、何を取り戻したいかです。", "本当の課題は我慢できる期間だけでなく、どんな注意力、人間関係、機能を取り戻したいかです。"),
        ],
        prompts=[],
    ),
    102: topic(
        slug="what-ai-gets-wrong-about-human-work", title="What AI gets wrong about human work",
        ko="AI가 인간의 일을 잘못 이해하는 부분", ja="AIが人の仕事を誤解するところ",
        goal=("Let's examine where AI helps and where human judgment still matters.", "AIが役立つところと、人の判断が必要なところを検討しましょう。"),
        article_title=("Capability is not the whole job", "能力だけでは仕事にならない"),
        articles=[
            ("AI can perform a task without understanding the whole job around it.", "A system may execute a task while missing the institutional and human context that gives it meaning.", "AIは作業をこなせても、その周りにある仕事全体を理解しているとは限りません。", "システムは作業を実行できても、その意味を支える組織や人間の文脈を見落とすことがあります。"),
            ("Visible output is often only one part of good work.", "The measurable output may conceal coordination, trust, timing, and judgment.", "目に見える成果は、よい仕事の一部にすぎないことがあります。", "測定できる成果の裏には、調整、信頼、タイミング、判断が隠れていることがあります。"),
            ("A fast answer can still be wrong for the situation.", "Fluency and speed can make a contextually poor answer look more reliable than it is.", "答えが速くても、その状況には合わないことがあります。", "流暢さと速さによって、状況に合わない答えが実際以上に信頼できそうに見えることがあります。"),
            ("People also make mistakes, so human control is not automatically perfect.", "Human oversight matters, but it should not be treated as error-free by definition.", "人も間違えるので、人が管理すれば必ず完璧というわけではありません。", "人による監督は重要ですが、それだけで誤りがないと考えるべきではありません。"),
            ("Every tool has a blind spot that users need to understand.", "Responsible use begins by identifying the tool's blind spot rather than assuming general intelligence.", "どんな道具にも、利用者が知るべき見落としやすい点があります。", "責任ある利用は、万能な知能を想定せず、その道具が見落としやすい点を特定することから始まります。"),
            ("AI is often strongest when the task has clear examples and a clear check.", "Performance improves when the task is well specified and the output can be independently verified.", "明確な例と確認方法がある作業では、AIが力を発揮しやすいです。", "作業が明確に定義され、出力を別の方法で確認できるほど、性能は上がります。"),
            ("It is weaker when the real question is what should matter.", "Optimization is less useful when the disputed issue is which value or trade-off should govern the decision.", "何を大切にすべきかが本当の問いなら、AIは苦手です。", "どの価値やトレードオフを判断の基準にするかが争点なら、最適化の力は限られます。"),
            ("Handing over a task can make accountability less clear.", "Delegation changes effort and visibility, but accountability still needs a named person.", "作業を任せると、誰が結果に責任を持つのか分かりにくくなることがあります。", "作業を委ねれば労力や見通しは変わりますが、結果に責任を持つ人は明確にする必要があります。"),
            ("Five years from now, jobs may change in different ways rather than simply disappear.", "Automation may redistribute tasks, status, and entry routes more unevenly than predictions of total replacement suggest.", "五年後、仕事は単になくなるのではなく、さまざまな形に変わるかもしれません。", "自動化は、仕事がすべて置き換わるという予測より不均等に、作業、立場、仕事への入り口を変えるかもしれません。"),
            ("A good question is not whether AI is good or bad, but who checks what.", "A useful evaluation names the task, the failure cost, the reviewer, and the person accountable for the result.", "大切なのはAIがよいか悪いかではなく、誰が何を確認するかです。", "役立つ評価では、作業、失敗の代償、確認者、結果に責任を持つ人を明確にします。"),
        ],
        prompts=[],
    ),
    103: topic(
        slug="how-much-money-is-enough", title="How much money is enough?",
        ko="얼마면 충분한가", ja="いくらあれば十分か",
        goal=("Let's discuss financial security without requiring personal disclosure.", "個人的な金額を明かさなくても、経済的な安心について話しましょう。"),
        article_title=("Enough is a moving line", "「十分」の基準は動く"),
        articles=[
            ("Enough money means different things in different households and places.", "Any threshold for enough depends on household needs, location, obligations, and public support.", "十分な金額は、家庭や地域によって違います。", "「十分」の基準は、家庭の必要、地域、責任、公的支援によって変わります。"),
            ("A financial cushion can reduce fear without solving every problem.", "A financial cushion can absorb shocks, although it cannot remove uncertainty from life.", "金銭的な余裕があると不安は減りますが、すべての問題が解決するわけではありません。", "金銭的な余裕は突然の負担を吸収できますが、人生の不確かさまではなくせません。"),
            ("The first useful amount may be the one that covers a likely emergency.", "The most meaningful early threshold may be resilience to a foreseeable expense rather than a dramatic fortune.", "最初に役立つ金額は、起こりそうな緊急の出費を払える額かもしれません。", "最初に意味を持つ基準は、大きな財産より、予想できる出費に耐えられることかもしれません。"),
            ("More income often helps most when basic needs are not secure.", "Additional income has its strongest effect where housing, health, food, or safety remain unstable.", "住居や食事などが安定していないとき、収入が増える効果は特に大きいです。", "住居、健康、食事、安全が不安定なほど、収入の増加は大きな効果を持ちます。"),
            ("After that, money may buy choice, time, or privacy more than happiness itself.", "Beyond basic security, money often changes autonomy and exposure to stress rather than guaranteeing happiness.", "その後、お金は幸福そのものより、選択、時間、プライバシーを増やすかもしれません。", "基本的な安心を超えると、お金は幸福を保証するより、自由やストレスへのさらされ方を変えることが多いです。"),
            ("A bigger number can create a new idea of what counts as normal.", "Rising resources may shift comparison and expectation, moving the line of enough again.", "金額が増えると、普通だと思う基準も変わることがあります。", "使える資源が増えると、比較や期待が変わり、「十分」の線もまた動くことがあります。"),
            ("People above the same financial line can experience it very differently.", "Two people with similar resources may face different risks, responsibilities, and senses of security.", "同じくらいのお金がある人でも、感じ方は大きく違います。", "同じような資源を持つ二人でも、危険、責任、安心感は異なることがあります。"),
            ("It is difficult to judge another person's happiness from income alone.", "Income reveals little about health, relationships, debt, care burdens, or private fear.", "収入だけで、ほかの人が幸せかどうかを判断するのは難しいです。", "収入だけでは、健康、人間関係、借金、ケアの負担、個人的な不安はほとんど分かりません。"),
            ("Removing money worries could free attention for rest, relationships, or useful work.", "Financial security may matter partly because it releases attention previously consumed by uncertainty.", "お金の心配が減ると、休息、人間関係、意味のある活動に意識を向けられます。", "経済的な安心の価値は、不確かさに奪われていた注意を取り戻せることにもあります。"),
            ("Enough can be a range and a set of conditions, not one universal number.", "A defensible answer may be a range tied to security and choice rather than a universal figure.", "「十分」は一つの共通の金額ではなく、幅や条件で考えることもできます。", "納得できる答えは、全員に共通する数字ではなく、安心と選択に結びついた幅かもしれません。"),
        ],
        prompts=[],
    ),
    104: topic(
        slug="is-there-a-best-age-to-be", title="Is there a best age to be?",
        ko="가장 좋은 나이가 있을까?", ja="いちばんいい年齢はある？",
        goal=("Let's compare life stages without assuming one age is best.", "どれか一つの年齢が最高だと決めつけず、人生の段階を比べましょう。"),
        article_title=("No age keeps every advantage", "すべての長所を持つ年齢はない"),
        articles=[
            ("Every life stage combines opportunities with limits.", "Every life stage offers a particular mix of capacity, dependence, freedom, and constraint.", "どの人生の段階にも、機会と限界があります。", "どの人生の段階にも、能力、依存、自由、制約の独自の組み合わせがあります。"),
            ("A younger body does not guarantee an easier life.", "Physical youth may coexist with insecurity, limited control, or social pressure.", "体が若くても、人生が楽だとは限りません。", "身体的に若くても、不安定さ、限られた自由、社会的な圧力があることがあります。"),
            ("Later years can bring confidence, skill, and clearer priorities.", "Age may bring accumulated competence, firmer personal boundaries, and less need for approval.", "年齢を重ねると、自信、技能、優先順位の明確さが増えることがあります。", "年齢によって、積み重ねた能力、自分の線引きをはっきりさせる力、承認を求めすぎない姿勢が得られることがあります。"),
            ("They can also bring loss, responsibility, or reduced energy.", "The same years may carry grief, care obligations, or physical limitation.", "同時に、喪失、責任、体力の低下が増えることもあります。", "同じ時期に、悲しみ、ケアの責任、身体的な制限を抱えることもあります。"),
            ("Memory often keeps the best part of an age and softens the rest.", "Nostalgia edits a period by preserving vivid rewards and fading ordinary strain.", "記憶は、その年齢のよい部分を残し、ほかを薄くすることがあります。", "懐かしさは、鮮明な喜びを残し、日常の負担を薄めることで、その時期を編集します。"),
            ("Returning to an age would not automatically restore the same people or conditions.", "An age has meaning through relationships and circumstances that a number alone cannot recreate.", "同じ年齢に戻っても、同じ人や状況まで戻るわけではありません。", "年齢の意味は人間関係や状況から生まれ、数字だけでは再現できません。"),
            ("Staying one age forever would also mean missing later change.", "Freezing one stage preserves its advantages only by giving up development beyond it.", "一つの年齢にとどまると、その後の変化を経験できません。", "一つの段階を固定することは、その長所を保つ代わりに、その先の成長を手放すことです。"),
            ("Some people would choose their present age rather than return.", "Choosing the present can reflect attachment to current knowledge, relationships, or agency.", "過去に戻らず、今の年齢を選ぶ人もいます。", "今を選ぶことは、現在の知識、人間関係、自分で決める力を大切にしている表れかもしれません。"),
            ("An age can feel better because the circumstances were better, not because of the number.", "Preference for an age may reflect its relationships and circumstances more than the age itself.", "ある年齢がよく感じられるのは、数字ではなく、そのときの状況がよかったからかもしれません。", "ある年齢への好みは、年齢そのものより、その時期の人間関係や状況を反映していることがあります。"),
            ("There may be no best age, only a best fit for a particular value.", "The preferred age changes when the valued outcome shifts from health to freedom, belonging, or perspective.", "最高の年齢ではなく、特定の価値に合う年齢があるだけかもしれません。", "健康、自由、つながり、物の見方のどれを重視するかで、選ぶ年齢は変わります。"),
        ],
        prompts=[],
    ),
    105: topic(
        slug="a-decision-worth-revisiting", title="A decision worth revisiting",
        ko="다시 생각해 볼 만한 결정", ja="見直す価値のある決断",
        goal=("Let's examine one personal, low-stakes, public, or imagined decision without forcing regret.", "後悔を求めず、個人的な例、軽い例、公の例、または想定上の決断を一つ検討しましょう。"),
        article_title=("A different choice is not a simple rewrite", "別の選択だけでは書き換えられない"),
        articles=[
            ("Wanting to change one choice does not mean rejecting everything that followed.", "Revising one decision need not erase the value of the path that actually occurred.", "一つの選択を変えたいと思っても、その後のすべてを否定することにはなりません。", "一つの決断を見直しても、実際に歩んだ道の価値まで消す必要はありません。"),
            ("A decision can make sense with the information available at the time.", "A choice may have been reasonable under the evidence, pressure, and options then available.", "当時分かっていた情報では、その決断が妥当だったこともあります。", "当時の根拠、圧力、選択肢の中では、その選択が合理的だった可能性があります。"),
            ("Knowing the outcome makes the better option look more obvious than it was.", "Hindsight can convert uncertainty into a false sense that the outcome was predictable.", "結果を知っていると、よい選択肢が当時も明らかだったように見えます。", "結果を知った後では、当時は不確かだったことまで予測できたように感じられます。"),
            ("The alternative might have solved one problem and created another.", "A counterfactual path changes a network of consequences, not one isolated result.", "別の道は一つの問題を解決しても、別の問題を生んだかもしれません。", "反実仮想の道では、一つの結果だけでなく、結果のつながり全体が変わります。"),
            ("Regret can identify a value or boundary that matters now.", "Useful regret extracts a principle for future action without demanding endless punishment.", "後悔から、今大切な価値や境界線に気づくことがあります。", "役立つ後悔は、自分を責め続けず、将来の行動に使える原則を取り出します。"),
            ("It can become harmful when we repeatedly second-guess an unchangeable past.", "Regret becomes corrosive when we second-guess the past without gaining new action or understanding.", "変えられない過去の判断を何度も疑うと、後悔は苦しくなります。", "新しい行動や理解につながらないまま過去の判断を疑い続けると、後悔は心をすり減らします。"),
            ("Some people say they have no regrets because each choice shaped them.", "The claim of no regrets may express acceptance, identity, defense, or a genuinely low level of regret.", "どの選択も今の自分を作ったとして、後悔はないと言う人もいます。", "「後悔はない」という言葉は、受容、自分らしさ、防御、または本当に後悔が少ないことを表す場合があります。"),
            ("That view can be healthy without proving every decision was good.", "Acceptance of the path is compatible with admitting that a particular decision was poor.", "その考え方は健全でも、すべての決断がよかったという証明にはなりません。", "歩んだ道を受け入れることと、特定の決断がよくなかったと認めることは両立します。"),
            ("An ordinary decision can reveal the same reasoning as a life-changing one.", "A low-stakes decision can expose the same pattern of judgment as a life-changing one.", "日常の決断からも、人生を変える決断と同じ考え方が見えます。", "小さな決断からも、人生を変える決断と同じ判断の型が見えることがあります。"),
            ("The best use of the question may be deciding what to do differently next time.", "Counterfactual reflection earns its value when it improves a future choice rather than rewriting identity.", "この質問の一番よい使い方は、次に何を変えるか決めることかもしれません。", "反実仮想の振り返りは、自分自身を書き換えるのでなく、次の選択を改善するときに価値を持ちます。"),
        ],
        prompts=[],
    ),
    106: topic(
        slug="what-speaking-english-has-made-you-notice", title="What speaking English has made you notice",
        ko="영어로 말하며 알게 된 점", ja="英語を話して気づいたこと",
        goal=("Let's reflect on changes, non-changes, and surprises from learning to speak English.", "英語を話す学習による変化、変わらない点、意外だった点を振り返りましょう。"),
        article_title=("A new language changes attention", "新しい言語で気づき方が変わる"),
        articles=[
            ("Learning to speak English can change what a person notices in Japanese.", "Speaking another language can make familiar habits in Japanese newly visible.", "英語を話す学習によって、日本語での話し方に気づくことがあります。", "別の言語を話すことで、日本語の慣れた話し方が新しく見えることがあります。"),
            ("Some differences are grammatical, but many are about tone and expectation.", "The most noticeable contrast may involve directness, turn-taking, or what listeners expect speakers to state.", "文法の違いもありますが、口調や期待の違いも多くあります。", "最も目立つ違いは、発言の直接さ、会話の順番の取り方、聞き手が話し手にどこまで明示することを求めるかかもしれません。"),
            ("New word choice can make the speaker consider an idea from another angle.", "A different word choice can foreground a distinction that the speaker usually leaves implicit.", "新しい言葉の選び方によって、別の角度から考えることがあります。", "異なる言葉の選び方によって、普段は明示しない違いに意識が向くことがあります。"),
            ("That does not mean the language creates a completely different personality.", "Changes in expression should not automatically be mistaken for a separate or more authentic self.", "だからといって、言語が全く別の性格を作るわけではありません。", "表現の変化を、別の人格や、より本当の自分だと自動的に考えるべきではありません。"),
            ("A learner may feel more direct in English because the available phrases are direct.", "Perceived directness may reflect learned phrases, proficiency limits, context, or genuine preference.", "知っている英語表現が直接的なため、英語ではより直接的だと感じる人もいます。", "英語で直接的に感じる理由は、覚えた表現、習熟度、状況、本当の好みなどさまざまです。"),
            ("Speaking English may expand who someone can talk to without changing their closest relationships.", "A wider conversational range can coexist with continuity in the relationships that matter most.", "英語を話すことで話せる相手が増えても、大切な人間関係は変わらないことがあります。", "話せる相手の範囲が広がっても、最も大切な人間関係は変わらないことがあります。"),
            ("The hardest part may be speed, confidence, listening, or saying a precise thought.", "Difficulty can come from processing speed, social risk, listening uncertainty, or the loss of nuance.", "難しいのは、速さ、自信、聞き取り、考えを正確に言うことかもしれません。", "難しさは、処理の速さ、対人上の不安、聞き取りの不確かさ、細かな意味を失うことから生まれます。"),
            ("Progress often appears first in a small moment rather than a dramatic breakthrough.", "A spontaneous reply or repaired misunderstanding may reveal progress more honestly than a formal score.", "進歩は大きな成功より、小さな瞬間に最初に表れることがあります。", "自然な返答や誤解の修正が、正式な点数より正直に進歩を示すことがあります。"),
            ("Some learners notice no change yet, and that is also useful evidence.", "An absence of perceived change can point to limited use, stable identity, or changes too gradual to notice.", "まだ変化を感じない学習者もいて、それも大切な情報です。", "変化を感じないことは、使う機会の少なさ、安定した自己認識、または気づかないほどゆっくりした変化を示すかもしれません。"),
            ("Looking back helps a learner decide what kind of English speaker to become next.", "Reflection can turn accumulated experience into a deliberate next direction without inventing a transformation.", "振り返ることで、次にどんな英語話者になりたいかを決められます。", "振り返りによって、実際以上の変化を作り上げず、積み重ねた経験を次の意識的な方向へつなげられます。"),
        ],
        prompts=[],
    ),
}

# The discussion pool is authored as conversation, not as a sequence of
# defensive branches.  Each opening is answerable without private disclosure;
# later pages deepen the selected idea and the tutor reciprocates naturally.
REVISED_GOALS = {
    101: ("Let's examine what a meaningful break from social media would change.", "SNSを意味のある期間休むと何が変わるか考えましょう。"),
    102: ("Let's examine where AI misses the human context around work.", "AIが仕事を取り巻く人間の文脈をどこで見落とすか考えましょう。"),
    103: ("Let's discuss what financial security needs to make possible.", "経済的な安心によって何が可能になる必要があるか話しましょう。"),
    104: ("Let's compare the strengths and costs of different life stages.", "さまざまな人生の段階の強みと代償を比べましょう。"),
    105: ("Let's compare one decision with a realistic alternative.", "一つの決断と現実的な別の選択を比べましょう。"),
    106: ("Let's reflect on what speaking English makes us notice about language.", "英語を話すことで言語について何に気づくか振り返りましょう。"),
}

REVISED_PROMPTS = {
    101: [
        prompt("opening", "A meaningful break", "意味のある休み", BRIEF_OPENINGS[101], "SNSを休むことで何かが変わるには、どのくらいの期間が必要ですか？", ("What kind of change would count?", "Would a shorter break reveal anything?"), full="How long must a social-media break last before it meaningfully changes behaviour?", full_ja="SNSを休むことで行動が意味のある形で変わるには、どのくらいの期間が必要ですか？", full_followups=("Which change would demonstrate an effect?", "What could a shorter experiment still reveal?"), safety="meaningful-break-duration"),
        prompt("miss", "The first missing function", "最初に困る機能", "Which function would people miss first?", "人はどの機能が使えないと最初に困るでしょうか？", ("Is it communication, information, or entertainment?", "What already serves the same purpose?"), full="Which social or practical function would become difficult first?", full_ja="どの人間関係上または実用上の機能が最初に難しくなるでしょうか？", full_followups=("Which need does that function serve?", "What alternative could replace it?"), safety="first-missing-function"),
        prompt("deletion", "After deleting an app", "アプリを消したあと", "Which habit usually changes after someone deletes or mutes an app?", "アプリを削除したり通知を切ったりすると、どの習慣が変わりやすいですか？", ("What becomes easier?", "What tends to bring the person back?"), full="Which habit tends to change when access to an app is removed?", full_ja="アプリを利用しにくくすると、どの習慣が変わりやすいですか？", full_followups=("What becomes easier after access is removed?", "What cue can survive the deletion?"), safety="deletion-and-habit-cue"),
        prompt("value", "Hard to replace", "代えにくい価値", "What does social media provide that is hardest to replace?", "SNSが与えるもので、最も代えにくいものは何ですか？", ("Why is another tool less effective?", "Who benefits most from that value?"), full="Which distinctive value of social media is least replaceable by another tool?", full_ja="SNSの独自の価値のうち、ほかの手段で最も代えにくいものは何ですか？", full_followups=("What makes the value genuinely distinctive?", "Which users depend on it most?"), safety="hard-to-replace-value"),
        prompt("cost", "Useful or a time sink", "役立つか時間を奪うか", "When does social media become a time sink instead of a useful tool?", "SNSはいつ、役立つ道具ではなく時間を奪うものになりますか？", ("Which kind of checking has no clear purpose?", "What limit could restore a purpose?"), full="At what point does useful access become unintended attention loss?", full_ja="便利な利用が、意図しない注意力の消費に変わるのはどの時点ですか？", full_followups=("Which behaviour marks the change?", "What boundary could protect attention?"), safety="usefulness-attention-cost"),
        prompt("model", "Healthy use", "健全な使い方", "What habits show a healthy relationship with social media?", "どんな習慣が、SNSとの健全な関係を示しますか？", ("How does the person decide when to open it?", "Which habit would be hardest to copy?"), full="Which habits best demonstrate an intentional relationship with social media?", full_ja="どんな習慣が、SNSを意識的に使う関係を最もよく示しますか？", full_followups=("How is each visit given a purpose?", "Which boundary makes the routine sustainable?"), safety="healthy-social-media-habits"),
        prompt("teen", "Advice at fourteen", "十四歳への助言", "What would you tell a fourteen-year-old about using social media?", "十四歳の人にSNSの使い方について何と伝えますか？", ("Which rule would be realistic?", "What should adults understand too?"), full="Which boundary and which freedom would you recommend to a fourteen-year-old?", full_ja="十四歳の人に、どんな境界線とどんな自由を勧めますか？", full_followups=("Which boundary could a teenager actually maintain?", "What responsibility belongs to adults?"), safety="realistic-young-user-advice"),
        prompt("flip", "One function to keep", "残したい一つの機能", "Which one social-media function is most worth keeping?", "SNSの機能を一つだけ残すなら、どれが最も価値がありますか？", ("Why that function?", "What could replace the others?"), full="Which single social-media function creates enough value to preserve?", full_ja="SNSの機能を一つだけ残すなら、十分な価値を生むのはどれですか？", full_followups=("What makes that function worth preserving?", "How could the remaining functions be replaced?"), safety="single-function-value"),
    ],
    102: [
        prompt("opening", "A human context AI misses", "AIが見落とす人の文脈", BRIEF_OPENINGS[102], "人の仕事のどの部分を、AIは最も誤解しやすいですか？", ("Which role gives us a clear example?", "Why does that role matter?"), full="Which part of human work most clearly exposes the limits of AI understanding?", full_ja="人の仕事のどの部分が、AIの理解の限界を最も明確に示しますか？", full_followups=("Which role provides the clearest case?", "Why is that case important?"), safety="human-work-context"),
        prompt("reason", "The missing context", "欠ける文脈", "In one role, what important context would AI miss?", "一つの役割で、AIはどんな重要な文脈を見落としますか？", ("Does the task depend on trust, timing, or history?", "Who understands that context best?"), full="Which relationship, history, or value would remain invisible to the system?", full_ja="どんな人間関係、過去、価値が、そのシステムには見えないままになりますか？", full_followups=("Why is that context difficult to encode?", "Who is positioned to interpret it?"), safety="role-specific-missing-context"),
        prompt("evidence", "A visible mistake", "見える失敗", "What kind of AI mistake would make that blind spot visible?", "どんなAIの誤りなら、その見落としがはっきり分かりますか？", ("What would the output get wrong?", "How could someone check it?"), full="Which observable failure would reveal that blind spot most clearly?", full_ja="どんな観察できる失敗が、その見落としを最も明確に示しますか？", full_followups=("Which output would expose the error?", "What independent check could verify it?"), safety="observable-ai-failure"),
        prompt("strength", "A useful capability", "役立つ能力", "Which part of the same work could AI help with?", "同じ仕事のどの部分なら、AIが役立てますか？", ("Why is that task easier to check?", "What should a person still review?"), full="Which component of the role is genuinely suitable for AI assistance?", full_ja="その役割のどの部分が、本当にAIの支援に適していますか？", full_followups=("What makes the task verifiable?", "Which judgment still requires review?"), safety="verifiable-ai-assistance"),
        prompt("blind-spot", "The dangerous blind spot", "危険な見落とし", "Which AI blind spot is most dangerous in this role?", "この役割では、AIのどの見落としが最も危険ですか？", ("What warning sign could reveal it?", "Who should monitor it?"), full="Which systematic blind spot creates the greatest risk in this role?", full_ja="この役割では、どの体系的な見落としが最大の危険を生みますか？", full_followups=("Which warning signal matters most?", "Who has enough context to detect it?"), safety="role-specific-ai-risk"),
        prompt("boundary", "A named human owner", "責任を持つ人", "Which responsibility should always have a named human owner?", "どの責任には、必ず担当する人を明確にするべきですか？", ("What could go wrong without one?", "How could AI still assist?"), full="Which responsibility must remain under meaningful and identifiable human control?", full_ja="どの責任を、実質的で担当者が明確な人の管理下に残す必要がありますか？", full_followups=("What failure cost requires accountability?", "Where could automation still reduce effort?"), safety="named-human-accountability"),
        prompt("future", "The role in five years", "五年後の役割", "How might this role change over the next five years?", "この役割は、これから五年でどう変わるかもしれませんか？", ("Which task may shrink?", "Which new task may appear?"), full="How might AI redistribute tasks, status, and accountability in this role over five years?", full_ja="AIは五年間で、この役割の作業、立場、説明責任をどう再配分するかもしれませんか？", full_followups=("Which task is most likely to contract?", "Which new responsibility may emerge?"), safety="five-year-role-change"),
        prompt("flip", "A claim people overstate", "言い過ぎられる主張", "What do people most often get wrong about what AI can do?", "AIにできることについて、人は何を最もよく誤解しますか？", ("Is the claim too confident or too dismissive?", "What evidence would improve it?"), full="Which popular claim about AI capability most needs qualification?", full_ja="AIの能力について広く言われる主張のうち、最も条件を加える必要があるものは何ですか？", full_followups=("Which assumption makes the claim misleading?", "What evidence would produce a better judgment?"), safety="qualified-ai-capability-claim"),
    ],
    103: [
        prompt("opening", "What enough makes possible", "十分なお金で可能になること", BRIEF_OPENINGS[103], "「十分なお金」によって、何が可能になる必要がありますか？", ("Why is that freedom important?", "What would count as enough protection?"), full="Which freedoms and protections should define financial sufficiency?", full_ja="どんな自由と保護が、経済的に十分であることを決めるべきですか？", full_followups=("Why is that freedom central to sufficiency?", "What would count as adequate protection?"), safety="financial-sufficiency-purpose"),
        prompt("change", "The first constraint removed", "最初になくなる制約", "Which constraint should money remove first?", "お金によって最初になくなるべき制約は何ですか？", ("Would it affect time, housing, care, or another need?", "How quickly would the change appear?"), full="Which constraint should a financial cushion remove first?", full_ja="金銭的な余裕によって、どの制約が最初になくなるべきですか？", full_followups=("Which category carries the greatest pressure?", "How immediate would the effect be?"), safety="first-financial-constraint"),
        prompt("same", "Outside money's reach", "お金だけでは解決できないこと", "Which important problem remains outside money's reach?", "どんな重要な問題が、お金だけでは解決できませんか？", ("Could money still help indirectly?", "What different support would matter?"), full="Which important source of difficulty cannot be resolved by money alone?", full_ja="どんな重要な困難が、お金だけでは解決できませんか？", full_followups=("Where could resources still help indirectly?", "Which non-financial intervention is needed?"), safety="nonfinancial-problem-boundary"),
        prompt("example", "Different needs", "異なる必要額", "Why can two households need very different amounts to feel secure?", "二つの世帯が安心するために必要な金額が大きく違うのはなぜですか？", ("Which cost varies most?", "How do responsibilities change the answer?"), full="Which conditions make financial sufficiency differ sharply between households?", full_ja="どんな条件によって、経済的に十分な水準が世帯ごとに大きく違いますか？", full_followups=("Which expense creates the largest variation?", "How do care duties or location alter the threshold?"), safety="household-needs-differ"),
        prompt("happiness", "Money and well-being", "お金と幸福", "When does money improve well-being most?", "お金は、どんなときに幸福を最も高めますか？", ("Which need is being met?", "When does extra money matter less?"), full="Under which conditions are financial resources most likely to improve well-being?", full_ja="どんな条件のもとで、経済的な資源は幸福を最も高めやすいですか？", full_followups=("Which need is being secured?", "Where might the returns become smaller?"), safety="conditions-for-financial-wellbeing"),
        prompt("attention", "Attention after worry", "心配が減ったあとの注意", "Where could attention go when money worries take less of it?", "お金の心配が減ると、注意をどこに向けられますか？", ("Would rest, care, learning, or work change?", "What would still demand attention?"), full="Where might mental capacity be redirected after financial uncertainty decreases?", full_ja="経済的な不確かさが減ると、心の余裕をどこへ向け直せますか？", full_followups=("Which activity would benefit first?", "What pressure would remain?"), safety="attention-after-financial-worry"),
        prompt("definition", "A number or conditions", "金額か条件か", "Is enough best defined by a number, a range, or a set of conditions?", "「十分」は、金額、範囲、または条件の組み合わせのどれで最もよく定義できますか？", ("Which condition matters most?", "When should the definition move?"), full="Should sufficiency be defined by a figure, a range, resilience, or freedom of choice?", full_ja="十分な水準は、金額、範囲、回復力、選択の自由のどれで定義するべきですか？", full_followups=("Which measure is most informative?", "What change should move the threshold?"), safety="defining-financial-sufficiency"),
        prompt("flip", "Security beyond money", "お金以外の安心", "Which kind of security matters most besides money?", "お金以外では、どんな安心が最も重要ですか？", ("Can it reduce the amount of money needed?", "How could someone strengthen it?"), full="Which non-financial resource most changes the amount of money a person needs?", full_ja="どの金銭以外の資源が、人に必要なお金の額を最も変えますか？", full_followups=("How does it change the financial threshold?", "What makes that resource resilient?"), safety="nonfinancial-security-resource"),
    ],
    104: [
        prompt("opening", "A stage to freeze", "止めておきたい人生の段階", BRIEF_OPENINGS[104], "どの人生の段階が、時間を止めるなら最も魅力的ですか？", ("What makes that stage appealing?", "What does that stage look like at its best?"), full="Which life stage offers the strongest case for being preserved indefinitely?", full_ja="どの人生の段階が、ずっと保つものとして最も説得力がありますか？", full_followups=("Which value makes the stage attractive?", "What evidence supports that picture of it?"), safety="attractive-life-stage"),
        prompt("good", "The strongest advantage", "最も大きな利点", "What is the strongest advantage of that life stage?", "その人生の段階の最も大きな利点は何ですか？", ("Is it health, freedom, belonging, or something else?", "Who benefits most from it?"), full="Which advantage gives that life stage its strongest appeal?", full_ja="どの利点が、その人生の段階に最も強い魅力を与えていますか？", full_followups=("Which value does the advantage serve?", "How widely is the advantage shared?"), safety="life-stage-advantage"),
        prompt("bad", "The unavoidable cost", "避けられない代償", "What is the unavoidable cost of that stage?", "その段階の避けられない代償は何ですか？", ("Does the cost come from limits or responsibilities?", "Can anything reduce it?"), full="Which constraint is inseparable from the stage's main advantage?", full_ja="どの制約が、その段階の主な利点と切り離せませんか？", full_followups=("Why does the trade-off persist?", "Which condition could soften it?"), safety="life-stage-cost"),
        prompt("now", "What the present offers", "今だから得られるもの", "What does the present offer that an earlier stage may not?", "今だから得られるもので、以前の段階にはないものは何ですか？", ("Is it knowledge, choice, or a relationship?", "Why did it take time to develop?"), full="Which present capacity or perspective deserves more weight in the comparison?", full_ja="今のどの能力や視点を、この比較でもっと重視するべきですか？", full_followups=("How was that capacity accumulated?", "Which earlier advantage does it balance?"), safety="present-stage-value"),
        prompt("loss", "Growth that would stop", "止まってしまう成長", "What later growth might freezing that stage prevent?", "その段階で時間を止めると、その後のどんな成長が妨げられますか？", ("Which later experience would disappear?", "What would never have time to mature?"), full="Which later development would permanent preservation of that stage prevent?", full_ja="その段階を永続させると、その後のどんな発達が妨げられますか？", full_followups=("Which later experience would be lost?", "What capacity requires further change?"), safety="prevented-later-growth"),
        prompt("condition", "What changes the answer", "答えを変える条件", "Which condition most changes the appeal of a life stage?", "どの条件が、人生の段階の魅力を最も変えますか？", ("Does health, money, or responsibility matter most?", "How would the ranking change?"), full="Which circumstance most destabilizes a simple ranking of life stages?", full_ja="どの状況が、人生の段階の単純な順位を最も崩しますか？", full_followups=("Which resource changes the trade-off?", "Who would rank the stages differently?"), safety="life-stage-conditions"),
        prompt("best", "A best age for everyone", "誰にとっても最高の年齢", "Can any age really be best for everyone?", "どの年齢も、本当に誰にとっても最高になれますか？", ("Which value would define best?", "Who would reasonably disagree?"), full="Can a best age exist without first deciding which values and circumstances count?", full_ja="どの価値や状況を重視するか決めずに、最高の年齢は存在できますか？", full_followups=("Which criterion would control the judgment?", "Whose circumstances challenge it?"), safety="no-universal-best-age"),
        prompt("flip", "Credit for the present", "今に与える評価", "What deserves more credit about the present stage?", "今の段階のどんな点を、もっと評価するべきですか？", ("What has become clearer?", "Which ability is easy to overlook?"), full="Which feature of the present deserves more weight than nostalgia usually gives it?", full_ja="今のどの特徴を、懐かしさが与える以上に重く評価するべきですか？", full_followups=("Which present gain is underestimated?", "How does nostalgia distort the comparison?"), safety="present-stage-credit"),
    ],
    105: [
        prompt("opening", "A decision worth revisiting", "見直す価値のある決断", BRIEF_OPENINGS[105], "歴史、作品、日常生活のどの決断を、違う形で行えたと思いますか？", ("What was the original choice?", "Why is that case worth revisiting?"), full="Which historical, fictional, or everyday decision offers the most useful counterfactual?", full_ja="歴史、作品、日常生活のどの決断が、最も考える価値のある反実仮想を与えますか？", full_followups=("Which actual decision anchors the case?", "Why is the alternative worth testing?"), safety="public-fictional-everyday-decision"),
        prompt("alternative", "The alternative choice", "別の選択", "What different choice could have been made?", "どんな別の選択ができたでしょうか？", ("Was that option really available?", "Who would have needed to act?"), full="Which realistic alternative was available under the conditions of the time?", full_ja="当時の条件の中で、どんな現実的な別の選択が可能でしたか？", full_followups=("What made the option feasible?", "Which actor controlled the decision?"), safety="realistic-alternative-choice"),
        prompt("workability", "Would it have worked?", "うまくいったか", "Would the different choice really have worked?", "別の選択は本当にうまくいったでしょうか？", ("What evidence supports it?", "Which new problem could appear?"), full="How confident can we be that the alternative would improve the outcome?", full_ja="別の選択が結果をよくしたと、どの程度確信できますか？", full_followups=("Which evidence supports the prediction?", "What uncertainty remains?"), safety="alternative-workability"),
        prompt("result", "The actual result", "実際の結果", "What did the original choice lead to, both good and bad?", "元の選択は、よい面と悪い面の両方で何につながりましたか？", ("Which result was unexpected?", "What value came from the real path?"), full="Which valuable and costly consequences followed from the actual decision?", full_ja="実際の決断から、どんな価値のある結果と代償のある結果が生まれましたか？", full_followups=("Which consequence was least predictable?", "What would the alternative erase?"), safety="actual-choice-consequences"),
        prompt("tradeoff", "The alternative's trade-off", "別の選択の代償", "What trade-off would the different choice create?", "別の選択は、どんなトレードオフを生むでしょうか？", ("Which benefit is most plausible?", "Which cost is easiest to miss?"), full="Which trade-off might the counterfactual path create?", full_ja="反実仮想の道は、どんなトレードオフを生む可能性がありますか？", full_followups=("Which benefit is best supported?", "Which new cost is easiest to overlook?"), safety="alternative-gain-and-cost"),
        prompt("context", "Why it made sense", "当時は合理的だった理由", "Why did the original choice make sense at the time?", "元の選択が当時は合理的だったのはなぜですか？", ("What information was available?", "Which pressure or limit mattered?"), full="How reasonable was the original decision under the information and constraints of the time?", full_ja="当時の情報と制約の中で、元の決断はどの程度合理的でしたか？", full_followups=("Which fact shaped the decision most?", "What could the decision-maker not know?"), safety="original-decision-context"),
        prompt("regret", "Useful regret", "役立つ後悔", "When does regret become useful?", "後悔はいつ役に立つものになりますか？", ("Does it change a future action?", "When does reflection become self-punishment?"), full="Which conditions turn regret into learning rather than repeated self-punishment?", full_ja="どんな条件によって、後悔は繰り返す自己批判ではなく学びになりますか？", full_followups=("Which future behaviour should change?", "Where should reflection stop?"), safety="regret-as-learning"),
        prompt("flip", "What no regrets means", "後悔がないという意味", "What can someone really mean when they say they have no regrets?", "「後悔はない」と言うとき、本当はどんな意味でしょうか？", ("Can acceptance include mistakes?", "Does the phrase defend every choice?"), full="How should we interpret the claim that someone has no regrets?", full_ja="「後悔はない」という主張を、どう解釈するべきですか？", full_followups=("Can acceptance coexist with criticism?", "Which stronger claim would go too far?"), safety="interpreting-no-regrets"),
    ],
    106: [
        prompt("opening", "A difference you notice", "気づく違い", BRIEF_OPENINGS[106], "英語を話し始めてから、英語と日本語のどんな違いが以前より目立つようになりましたか？", ("What first made the difference noticeable?", "Which language makes it clearer?"), full="Which contrast between English and Japanese has become most salient through speaking practice?", full_ja="話す練習を通して、英語と日本語のどんな対照が最も目立つようになりましたか？", full_followups=("Which experience revealed the contrast?", "Why does speaking make it more visible?"), safety="noticed-language-contrast"),
        prompt("notice", "One clear example", "一つの明確な例", "Which example shows that difference most clearly?", "どの例が、その違いを最もはっきり示しますか？", ("What would someone say in English?", "How would Japanese handle it?"), full="Which specific exchange best demonstrates that contrast?", full_ja="どの具体的なやり取りが、その対照を最もよく示しますか？", full_followups=("How would the English version sound?", "What expectation shapes the Japanese version?"), safety="specific-language-example"),
        prompt("direction", "Words, tone, timing, or silence", "言葉、口調、間、沈黙", "Does the difference involve words, tone, timing, or silence?", "その違いは、言葉、口調、間、沈黙のどれに関係しますか？", ("Which part is hardest to translate?", "What might a listener misunderstand?"), full="Does the contrast lie mainly in wording, directness, turn-taking, or silence?", full_ja="その対照は主に、言葉遣い、直接さ、会話の順番、沈黙のどこにありますか？", full_followups=("Which feature resists direct translation?", "What expectation could cause misunderstanding?"), safety="language-contrast-feature"),
        prompt("people", "A wider conversational world", "広がる会話の世界", "How does English change the range of people a learner can talk to?", "英語は、学習者が話せる人の範囲をどう変えますか？", ("Which conversation becomes possible?", "What still limits the connection?"), full="How can spoken English alter a learner's conversational world?", full_ja="英語を話すことは、学習者の会話の世界をどう変えられますか？", full_followups=("Which relationship becomes possible?", "What barrier can remain despite shared language?"), safety="english-conversation-range"),
        prompt("difficulty", "The hardest adjustment", "最も難しい調整", "What is the hardest adjustment when speaking English?", "英語を話すとき、最も難しい調整は何ですか？", ("Has that difficulty changed?", "What support actually helps?"), full="Which speaking adjustment demands the most sustained effort?", full_ja="話すときのどの調整に、最も長く努力する必要がありますか？", full_followups=("How has the difficulty evolved?", "Which practice addresses it directly?"), safety="hardest-speaking-adjustment"),
        prompt("surprise", "Compared with expectations", "予想との違い", "How did speaking English compare with what you expected?", "英語を話す経験は、予想と比べてどうでしたか？", ("Which expectation was accurate?", "Which one changed most?"), full="How has the experience of speaking English compared with your earlier expectations?", full_ja="英語を話す経験は、以前の予想と比べてどうでしたか？", full_followups=("Which expectation proved accurate?", "Which expectation changed most?"), safety="speaking-versus-expectations"),
        prompt("identity", "Expression and identity", "表現と自分らしさ", "How can different words change expression without changing who someone is?", "違う言葉は、その人らしさを変えずに表現をどう変えられますか？", ("Which word choice shows the difference?", "What remains consistent across languages?"), full="How can language reshape expression while leaving identity recognizable?", full_ja="言語は、自分らしさを保ちながら表現をどう変えられますか？", full_followups=("Which linguistic choice makes the shift visible?", "What continuity preserves identity?"), safety="expression-with-stable-identity"),
        prompt("flip", "Would you start again?", "もう一度始めるか", "Would you choose to start learning English again, knowing what you know now?", "今知っていることを踏まえても、もう一度英語学習を始めますか？", ("What would you keep the same?", "What would you change from the beginning?"), full="Knowing what you know now, would you choose the same English-learning path again?", full_ja="今知っていることを踏まえても、同じ英語学習の道をもう一度選びますか？", full_followups=("Which part of the path would you preserve?", "What would you change from the beginning?"), safety="reflective-learning-choice"),
    ],
}

for _number in TOPIC_NUMBERS:
    TOPICS[_number]["goal"] = REVISED_GOALS[_number]
    TOPICS[_number]["prompts"] = REVISED_PROMPTS[_number]


def _conversation(a, ja, f=None, f_ja=None):
    return (a, ja, a if f is None else f, ja if f_ja is None else f_ja)


CONVERSATIONAL_MAIN_REVISIONS = {
    101: (
        _conversation("Would three days away from social media feel too short, too long, or about right?", "SNSから三日間離れるのは、短すぎますか、長すぎますか、それともちょうどよいですか？"),
        _conversation("Which app or social-media feature would you miss first?", "どのアプリやSNSの機能が最初に恋しくなりますか？"),
        _conversation("What would you do instead of checking social media?", "SNSを確認する代わりに、何をしますか？"),
        _conversation("Which useful thing on social media is hardest to replace?", "SNSの役立つもののうち、最も代えにくいものは何ですか？"),
        _conversation("What sign shows that scrolling is wasting your time?", "スクロールが時間を無駄にしていると分かるサインは何ですか？"),
        _conversation("What's one healthy rule for using social media?", "SNSを使うための健全なルールを一つ挙げるとしたら何ですか？", "Which simple rule keeps social media useful without letting it take over?", "SNSに時間を奪われず、役立つものに保つ簡単なルールは何ですか？"),
        _conversation("What social-media rule would you give a fourteen-year-old?", "十四歳の人に、どんなSNSのルールを伝えますか？"),
        _conversation("If you could keep only one social-media feature, which would you choose?", "SNSの機能を一つだけ残せるなら、どれを選びますか？"),
    ),
    102: (
        _conversation("What is one thing AI does badly when it tries to do human work?", "AIが人の仕事をしようとするとき、うまくできないことを一つ挙げるとしたら何ですか？"),
        _conversation("What human situation is hardest for AI to read correctly?", "AIが正しく理解するのが最も難しい人間の状況は何ですか？"),
        _conversation("What's a funny or worrying AI mistake you've seen or heard about?", "見たり聞いたりしたAIの面白い、または心配な間違いは何ですか？"),
        _conversation("Which boring part of human work should AI help with?", "人の仕事の地味な部分で、AIに手伝ってほしいものは何ですか？"),
        _conversation("Which AI mistake could seriously hurt someone?", "AIのどんな間違いが、人を深く傷つける可能性がありますか？"),
        _conversation("Which decision should always have a person responsible for it?", "どんな決断には、必ず責任を持つ人が必要ですか？"),
        _conversation("What human skill will matter more as AI improves?", "AIが進歩するほど、どんな人間の技能がより大切になりますか？"),
        _conversation("What do people often expect AI to do better than it can?", "人はAIに、実際よりもうまくできると何を期待しがちですか？"),
    ),
    103: (
        _conversation("When someone says, ‘I have enough money,’ what do you imagine they can afford?", "誰かが「十分なお金がある」と言うとき、何を無理なく払えると想像しますか？"),
        _conversation("Which money worry would you remove first?", "お金の心配を一つなくせるなら、最初にどれをなくしますか？"),
        _conversation("What's something important that more money can't fix?", "お金が増えても解決できない大切なことは何ですか？"),
        _conversation("Why can the same income feel enough for one person but not another?", "同じ収入でも、一人には十分で、別の人には足りないと感じるのはなぜですか？"),
        _conversation("When does extra money make the biggest difference?", "お金が増えることが最も大きな違いを生むのは、どんなときですか？"),
        _conversation("What would you do with the mental space left by fewer money worries?", "お金の心配が減ってできた心の余裕を、何に使いますか？"),
        _conversation("Would you rather have a fixed amount saved or reliable income every month?", "決まった額の貯金と、毎月の安定した収入のどちらがよいですか？", "Which creates a stronger feeling of security: savings or reliable monthly income?", "貯金と毎月の安定した収入のどちらが、より強い安心を生みますか？"),
        _conversation("What kind of security matters most besides money?", "お金以外では、どんな安心が最も重要ですか？"),
    ),
    104: (
        _conversation("If you could stay one age for ten years, which age would you choose?", "一つの年齢のまま十年間過ごせるなら、何歳を選びますか？"),
        _conversation("Which age gives the best mix of energy and freedom?", "どの年齢が、元気さと自由の最もよい組み合わせを持っていますか？"),
        _conversation("What's hard about the age many people call the best?", "多くの人が最高だと言う年齢にも、どんな大変さがありますか？"),
        _conversation("What's one good thing about your age now?", "今の年齢のよいところを一つ挙げるとしたら何ですか？"),
        _conversation("What future experience would you not want to miss by staying the same age?", "同じ年齢にとどまることで、どんな将来の経験を逃したくありませんか？"),
        _conversation("How do health or money change which age seems best?", "健康やお金によって、どの年齢が最高に見えるかはどう変わりますか？"),
        _conversation("Can the same age be best for two people with very different lives?", "生活が大きく違う二人にとって、同じ年齢が最高になることはありますか？"),
        _conversation("What's underrated about getting older?", "年を重ねることの、もっと評価されるべき点は何ですか？"),
    ),
    105: (
        _conversation("What is one decision you would change in a film, book, or real event?", "映画、本、現実の出来事で、変えたい決断を一つ挙げるとしたら何ですか？"),
        _conversation("What's one choice that looked wrong but led to something good?", "間違って見えても、よいことにつながった選択は何ですか？"),
        _conversation("How can we know whether another choice would really have been better?", "別の選択が本当によかったかを、どう判断できますか？"),
        _conversation("Which matters more when judging a decision: what was known then or what happened later?", "決断を評価するとき、当時分かっていたことと、その後起きたことのどちらが大切ですか？"),
        _conversation("What new problem can a better choice create?", "よりよい選択が、どんな新しい問題を生むことがありますか？"),
        _conversation("Why can a bad decision make sense at the time?", "悪い決断でも、そのときには納得できることがあるのはなぜですか？"),
        _conversation("When does looking back help with the next decision?", "振り返ることが、次の決断に役立つのはどんなときですか？"),
        _conversation("What can 'no regrets' mean without saying every choice was right?", "すべての選択が正しかったと言わずに、「後悔はない」とはどんな意味になりますか？"),
    ),
    106: (
        _conversation("What has speaking English made you notice about Japanese?", "英語を話すことで、日本語について何に気づきましたか？"),
        _conversation("What English phrase is hard to say naturally in Japanese?", "日本語で自然に言うのが難しい英語の表現は何ですか？"),
        _conversation("When do English speakers say something directly that Japanese speakers may leave unsaid?", "英語では直接言っても、日本語では言わないことがあるのはどんなときですか？"),
        _conversation("Who can you talk to now because of English?", "英語のおかげで、今はどんな人と話せますか？"),
        _conversation("Which part of speaking English still takes the most effort?", "英語を話すとき、今も最も努力が必要な部分は何ですか？"),
        _conversation("What was easier or harder about speaking English than you expected?", "英語を話すことは、予想より簡単でしたか、それとも難しかったですか？"),
        _conversation("Do you feel slightly different when you speak English?", "英語を話すとき、自分が少し違って感じますか？", "How can speaking another language bring out a different side of someone?", "別の言語を話すことで、人の違う一面が出るのはどうしてですか？"),
        _conversation("What would you practise first if you started learning English again?", "もう一度英語学習を始めるなら、最初に何を練習しますか？"),
    ),
}

for _number, _rows in CONVERSATIONAL_MAIN_REVISIONS.items():
    if len(_rows) != 8:
        raise ValueError(f"FT-{_number} must have eight conversational prompts")
    for _item, (_a, _a_ja, _f, _f_ja) in zip(TOPICS[_number]["prompts"], _rows, strict=True):
        _item.update(
            accessible=_a,
            accessible_ja=_a_ja,
            full=_f,
            full_ja=_f_ja,
            full_followups=_item["accessible_followups"],
            safety="standalone-conversation-pool",
        )

CONVERSATIONAL_FULL_DEEPENING = {
    (101, 5): ("How can you tell when useful scrolling has turned into wasted time?", "役立つスクロールが時間の無駄に変わったと、どう見分けられますか？"),
    (102, 2): ("Which human situation is easy for a person to read but hard for AI?", "人には分かりやすくても、AIには理解しにくい人間の状況は何ですか？"),
    (102, 6): ("Which decisions need a person who can explain the result and take responsibility for it?", "結果を説明し、責任を持つ人が必要なのは、どんな決断ですか？"),
    (103, 4): ("What can make the same income feel comfortable for one person and stressful for another?", "同じ収入でも、一人には余裕があり、別の人には苦しく感じられるのはなぜですか？"),
    (104, 3): ("What hidden difficulty comes with an age people often call the best?", "多くの人が最高だと言う年齢には、どんな見えにくい大変さがありますか？"),
    (104, 7): ("Could the same age be best for two people with very different health, money, or responsibilities?", "健康、お金、責任が大きく違う二人にとって、同じ年齢が最高になることはありますか？"),
    (105, 3): ("What evidence would convince you that a different choice would really have worked better?", "違う選択のほうが本当によかったと納得するには、どんな証拠が必要ですか？"),
    (105, 4): ("When judging a decision, how should we balance what was known then with what happened later?", "決断を評価するとき、当時分かっていたことと、その後の結果をどう両方考えるべきですか？"),
    (106, 3): ("When does English encourage direct wording where Japanese might rely on tone or silence?", "日本語では口調や沈黙に頼る場面で、英語はどんなときに直接的な言い方を促しますか？"),
}
for (_number, _index), (_full, _full_ja) in CONVERSATIONAL_FULL_DEEPENING.items():
    TOPICS[_number]["prompts"][_index - 1].update(full=_full, full_ja=_full_ja)

CONVERSATIONAL_PAGE_TITLES = {
    (101, 1): ("Three days away", "SNSから離れる三日間"),
    (101, 2): ("The first feature you would miss", "最初に恋しくなる機能"),
    (101, 3): ("Instead of checking", "確認する代わりに"),
    (101, 5): ("When scrolling wastes time", "スクロールが時間を無駄にするとき"),
    (101, 8): ("One feature to keep", "残したい一つの機能"),
    (102, 1): ("Something AI does badly", "AIが苦手なこと"),
    (102, 2): ("A situation AI misreads", "AIが読み違える状況"),
    (102, 3): ("A funny or worrying mistake", "面白い、または心配な間違い"),
    (102, 4): ("A boring task AI can help with", "AIが手伝える地味な仕事"),
    (102, 5): ("A mistake that can hurt someone", "人を傷つける可能性のある間違い"),
    (102, 6): ("A person must be responsible", "責任を持つ人が必要なこと"),
    (102, 7): ("A human skill that will matter more", "もっと大切になる人間の技能"),
    (102, 8): ("Expecting too much from AI", "AIに期待しすぎること"),
    (103, 1): ("What enough money can cover", "十分なお金で払えるもの"),
    (103, 2): ("The first money worry to remove", "最初になくしたいお金の心配"),
    (103, 5): ("When extra money matters most", "お金が最も役立つとき"),
    (103, 6): ("Space after money worries", "お金の心配が減った後の余裕"),
    (103, 7): ("Savings or steady income", "貯金か安定した収入か"),
    (104, 1): ("One age for ten years", "一つの年齢で過ごす十年間"),
    (104, 2): ("Energy and freedom", "元気さと自由"),
    (104, 3): ("The hard side of the best age", "最高の年齢の大変な面"),
    (104, 5): ("A future experience you would miss", "逃したくない将来の経験"),
    (104, 7): ("The same best age for different lives", "違う人生でも同じ最高の年齢か"),
    (104, 8): ("The underrated side of getting older", "年を重ねることの隠れたよさ"),
    (105, 2): ("A wrong-looking choice with a good result", "間違って見えたよい選択"),
    (105, 3): ("Would another choice be better?", "別の選択は本当によいか"),
    (105, 4): ("What was known then, or what happened later?", "当時の情報か、その後の結果か"),
    (105, 5): ("A new problem from a better choice", "よりよい選択が生む新しい問題"),
    (105, 7): ("Looking back to decide better", "次の決断のために振り返ること"),
    (106, 2): ("A phrase that is hard to translate", "訳しにくい表現"),
    (106, 3): ("Direct in English, unsaid in Japanese", "英語では直接、日本語では言わないこと"),
    (106, 4): ("Who English lets you talk to", "英語で話せる相手"),
    (106, 5): ("The part that still takes effort", "今も努力が必要な部分"),
    (106, 8): ("What you would practise first", "最初に練習すること"),
}
for (_number, _index), (_title, _title_ja) in CONVERSATIONAL_PAGE_TITLES.items():
    TOPICS[_number]["prompts"][_index - 1].update(title=_title, title_ja=_title_ja)

CONVERSATIONAL_FOLLOWUP_REVISIONS = {
    (101, 3): ("What would fill the first few minutes instead?", "What might make you open the app again?"),
    (101, 6): ("When would the rule apply?", "What could make the rule hard to keep?"),
    (102, 1): ("Which job gives a clear example?", "What does AI miss in that job?"),
    (102, 2): ("What makes that situation hard for AI?", "Who would understand it better?"),
    (102, 3): ("What did the AI get wrong?", "How could a person spot the mistake?"),
    (102, 5): ("Who could be hurt?", "Who should check the AI's work?"),
    (102, 7): ("Why will that skill matter more?", "How could someone practise it now?"),
    (102, 8): ("Why does the task look easier than it is?", "What example shows the real limit?"),
    (103, 1): ("Does enough include housing, food, and emergencies?", "Which cost would be hardest to cover?"),
    (103, 6): ("Would you use the space for rest, care, learning, or something else?", "What worry might still remain?"),
    (103, 7): ("Why does your choice feel safer?", "What is the main weakness of the other option?"),
    (104, 1): ("What makes that age attractive?", "What would be difficult about staying there?"),
    (104, 2): ("Which freedom matters most?", "What does that age still make difficult?"),
    (104, 4): ("Why is that good thing easy to overlook?", "Did it take time to develop?"),
    (104, 5): ("Why would that experience matter?", "Could the same age still allow personal growth?"),
    (105, 2): ("Why did the choice look wrong at first?", "What good result came from it?"),
    (105, 4): ("Why did you choose that side?", "What would make you judge the decision differently?"),
    (105, 5): ("Who might pay the new cost?", "Would the original problem still be solved?"),
    (106, 1): ("What experience made you notice it?", "Did the difference surprise you?"),
    (106, 2): ("What does the English phrase express?", "What would sound more natural in Japanese?"),
    (106, 6): ("Which part was easier?", "What still surprises you about the difficult part?"),
    (106, 7): ("Which side of you comes out more in English?", "What still feels the same in both languages?"),
    (106, 8): ("Why would you start there?", "What did you spend too much time on before?"),
}
for (_number, _index), _followups in CONVERSATIONAL_FOLLOWUP_REVISIONS.items():
    TOPICS[_number]["prompts"][_index - 1].update(
        accessible_followups=_followups,
        full_followups=_followups,
    )

FINAL_SEMANTIC_REPAIRS = {
    (101, 1): dict(accessible_followups=("What would make three days feel useful?", "What would make it feel too long?"), full_followups=("What would make three days feel useful?", "What would make it feel too long?")),
    (101, 4): dict(accessible_followups=("What makes it hard to replace?", "What could partly replace it?"), full_followups=("What makes it hard to replace?", "What could partly replace it?")),
    (104, 6): dict(accessible_followups=("Which matters more for your answer: health or money?", "Could either one change your choice completely?"), full_followups=("Which matters more for your answer: health or money?", "Could either one change your choice completely?")),
    (105, 3): dict(accessible_followups=("What could we never know for certain?", "Which new problem could appear?"), full_followups=("What could we never know for certain?", "Which new problem could appear?")),
    (105, 4): dict(accessible_followups=("What makes your balance fair?", "Which kind of case could change it?"), full_followups=("What makes your balance fair?", "Which kind of case could change it?")),
    (105, 8): dict(title="A decision people can fix", title_ja="直すことができる決断", accessible="What is one bad decision people can usually fix?", accessible_ja="人がたいてい直すことのできる悪い決断は何ですか？", full="Which bad decision is easier to repair than people expect?", full_ja="人が思うより直しやすい悪い決断は何ですか？", accessible_followups=("What is the first repair step?", "When is it too late to fix?"), full_followups=("What is the first repair step?", "When is it too late to fix?")),
    (106, 4): dict(title="A conversation English makes easier", title_ja="英語でしやすくなる会話", accessible="What kind of conversation becomes easier with English?", accessible_ja="英語があると、どんな会話がしやすくなりますか？", full="Which conversation can English make possible between people who do not share another language?", full_ja="ほかに共通の言語がない人同士でも、英語があるとどんな会話ができますか？", accessible_followups=("Who might have that conversation?", "What could still be difficult?"), full_followups=("Who might have that conversation?", "What could still be difficult?")),
    (106, 7): dict(title="A different side in English", title_ja="英語で出る違う一面", accessible="Which side of you, if any, comes out more when you speak English?", accessible_ja="英語を話すとき、いつもより出やすい自分の一面はありますか？", full="What different side of you can come out when you speak English?", full_ja="英語を話すとき、自分のどんな違う一面が出ることがありますか？", accessible_followups=("What makes that side appear?", "What stays the same in both languages?"), full_followups=("What makes that side appear?", "What stays the same in both languages?")),
}
for (_number, _index), _changes in FINAL_SEMANTIC_REPAIRS.items():
    TOPICS[_number]["prompts"][_index - 1].update(**_changes)

FINAL_REVIEW_REPAIRS = {
    (101, 2): dict(title="The first change you would notice", title_ja="最初に気づく変化", accessible="What would you notice first after three days away from social media?", accessible_ja="SNSから三日間離れたら、最初にどんな変化に気づきますか？", full="What change would you notice first during three days away from social media?", full_ja="SNSから三日間離れている間、最初にどんな変化に気づきますか？", accessible_followups=("Would it affect communication, information, or entertainment?", "What might not change at all?"), full_followups=("Would it affect communication, information, or entertainment?", "What might not change at all?")),
    (102, 3): dict(title="A mistake that starts funny", title_ja="最初は面白く見える間違い", accessible="What kind of AI mistake seems funny at first but could become worrying?", accessible_ja="最初は面白く見えても、心配につながりうるAIの間違いは何ですか？", full="Which AI mistake can look funny until it affects a real decision?", full_ja="実際の決断に影響するまでは面白く見えるAIの間違いは何ですか？", accessible_followups=("What could the AI get wrong?", "How could a person catch the mistake?"), full_followups=("What could the AI get wrong?", "How could a person catch the mistake?")),
    (104, 7): dict(accessible_followups=("What part of life could make their answers different?", "Who would reasonably disagree?")),
    (105, 4): dict(accessible_followups=("Why does that matter more to you?", "What kind of result could change your answer?")),
    (105, 7): dict(accessible_followups=("What future action could it change?", "When is it better to stop looking back?"), full_followups=("What future action could it change?", "When is it better to stop looking back?")),
}
for (_number, _index), _changes in FINAL_REVIEW_REPAIRS.items():
    TOPICS[_number]["prompts"][_index - 1].update(**_changes)

# The learner hears these questions once.  The first follow-up extends a real
# answer; the second gives a new, concrete foothold after "I don't know" or no
# matching experience.  Keep the same conversational jobs across variants.
THREE_SECOND_MAIN_REPAIRS = {
    (103, 6): dict(
        accessible="If you worried less about money, what would you spend more time thinking about?",
        accessible_ja="お金の心配が減ったら、何について考える時間を増やしたいですか？",
        full="If money worries took less of your attention, what would you focus on instead?",
        full_ja="お金の心配に注意を取られなくなったら、代わりに何に集中したいですか？",
    ),
    (104, 7): dict(
        accessible="Why might the same age feel great for one person and difficult for another?",
        accessible_ja="同じ年齢でも、一人には最高で、別の人には大変に感じられるのはなぜですか？",
        full="Why can the same age feel freeing for one person and limiting for another?",
        full_ja="同じ年齢でも、一人には自由に、別の人には制約が多く感じられるのはなぜですか？",
    ),
    (105, 3): dict(
        accessible="What proof would show that a different choice was better?",
        accessible_ja="別の選択のほうがよかったと分かる証拠は何ですか？",
        full="What evidence would show that a different choice led to a better result?",
        full_ja="別の選択がよりよい結果につながったと分かる証拠は何ですか？",
    ),
    (105, 4): dict(
        full="When judging a decision, which matters more: what was known then or what happened later?",
        full_ja="決断を評価するとき、当時分かっていたことと、その後起きたことのどちらがより大切ですか？",
    ),
    (102, 6): dict(
        full="Which decisions need a person who can explain the result and accept responsibility?",
        full_ja="結果を説明し、責任を引き受ける人が必要なのは、どんな決断ですか？",
    ),
    (106, 3): dict(
        full="When do English speakers say something directly that Japanese speakers may leave unsaid?",
        full_ja="英語では直接言っても、日本語では言わないことがあるのはどんなときですか？",
    ),
    (106, 4): dict(
        full="What kind of conversation becomes possible because of English?",
        full_ja="英語があることで、どんな会話ができるようになりますか？",
    ),
    (106, 6): dict(
        full="Which part of speaking English was most different from what you expected?",
        full_ja="英語を話すことで、予想と最も違っていた部分は何ですか？",
    ),
    (106, 7): dict(
        full="Which side of you, if any, comes out more when you speak English?",
        full_ja="英語を話すとき、いつもより出やすい自分の一面はありますか？",
    ),
}
for (_number, _index), _changes in THREE_SECOND_MAIN_REPAIRS.items():
    TOPICS[_number]["prompts"][_index - 1].update(**_changes)

THREE_SECOND_FOLLOWUPS = {
    101: (
        ("What would make three days feel useful?", "Which app would be easiest to leave for three days?"),
        ("Would you miss messages, news, or entertainment first?", "Which of those do you check most now?"),
        ("What would fill the first few minutes instead?", "When do you check social media most: morning, breaks, or evening?"),
        ("What makes that feature hard to replace?", "Which feature do you use most: messages, news, or videos?"),
        ("How do you feel after that kind of scrolling?", "Do you ever open an app without a clear reason?"),
        ("When would the rule apply?", "Which is easier: turning off notifications or setting a time limit?"),
        ("Why would that rule be realistic?", "Which is safer for a teenager: a private account or a public one?"),
        ("Why would you keep that feature?", "Which feature do you use most: messages, photos, or short videos?"),
    ),
    102: (
        ("Which job gives a clear example?", "Would you trust AI more with numbers or feelings?"),
        ("Why does AI struggle with the situation you named?", "Which is harder for AI to read: sarcasm or sadness?"),
        ("Who could be affected by that mistake?", "Have you ever seen AI give a strange answer?"),
        ("How could a person check the result?", "Would you rather let AI sort emails or write a complaint reply?"),
        ("Who could be hurt?", "Should AI choose who gets a job by itself?"),
        ("What could go wrong without a person in charge?", "Who should have the final say in a hiring decision?"),
        ("Why will that skill matter more?", "Which matters more with AI: asking good questions or checking answers?"),
        ("What example shows the real limit?", "Which does AI do better: summarizing text or understanding feelings?"),
    ),
    103: (
        ("Which cost matters most?", "Would a home and emergency savings count as enough?"),
        ("How would removing that worry change daily life?", "Which is more stressful: an unexpected bill or rising monthly costs?"),
        ("Could money still help indirectly?", "Can money buy trust?"),
        ("Which cost varies most?", "Who usually needs more money: one person or a family of four?"),
        ("Which need is being met?", "Does extra money matter more for rent or entertainment?"),
        ("Why would that deserve more attention?", "Would you use the extra focus for rest, family, or learning?"),
        ("Why does your choice feel safer?", "What's one bill people need to plan for every month?"),
        ("How can that kind of security help?", "Which gives more security: good health or people you can rely on?"),
    ),
    104: (
        ("What makes that age attractive?", "Would you rather keep youthful energy or later-life experience?"),
        ("Which freedom matters most?", "Which age seems most independent: twenty, forty, or sixty?"),
        ("Why is that part difficult?", "Which seems harder: being twenty or being sixty?"),
        ("Why is that good thing easy to overlook?", "What's easier for you now than when you were younger?"),
        ("Why would that experience matter?", "Would you rather see the future or relive the past?"),
        ("Which matters more for your answer: health or money?", "Would good health make almost any age feel better?"),
        ("Which life detail creates that difference?", "Could age thirty feel different with and without children?"),
        ("What has become clearer with age?", "Which improves more with age: confidence or patience?"),
    ),
    105: (
        ("What was the original choice?", "Would you rather change a movie ending or a real historical decision?"),
        ("What good result followed?", "Can a mistake ever create a good opportunity?"),
        ("What could we never know for certain?", "Is a good result always proof of a good decision?"),
        ("Why does that matter more to you?", "Should a doctor be judged by the decision or only the result?"),
        ("Who might pay the new cost?", "Can saving money now create a bigger cost later?"),
        ("What information was available then?", "Which matters more under pressure: more time or better information?"),
        ("What future action could looking back change?", "Is it useful to think about a small mistake after the mistake is fixed?"),
        ("What is the first repair step?", "Which is easier to fix: being late or sending the wrong message?"),
    ),
    106: (
        ("Which experience made the language difference clear?", "Which feels more direct to you: English or Japanese?"),
        ("What would sound more natural in Japanese?", "Which is harder to translate: a joke or an apology?"),
        ("What might a listener misunderstand?", "Which language feels more direct in requests?"),
        ("Who might have that conversation?", "Would English help more while travelling or working online?"),
        ("What support actually helps?", "Which is harder: speaking quickly or finding the right word?"),
        ("Which part was easier or harder?", "Which surprised you more: pronunciation or listening?"),
        ("What makes that side appear?", "Do you feel more direct in English?"),
        ("Why would you start there?", "Would you start with listening or speaking?"),
    ),
}
for _number, _rows in THREE_SECOND_FOLLOWUPS.items():
    if len(_rows) != 8:
        raise ValueError(f"FT-{_number} must have eight three-second follow-up sets")
    for _item, _followups in zip(TOPICS[_number]["prompts"], _rows, strict=True):
        _item.update(accessible_followups=_followups, full_followups=_followups)

# Final spoken review: every line must be understood after one hearing and let
# a learner begin a real answer within about three seconds.  These repairs also
# keep each page usable after "I don't know" and stop later questions from
# merely rephrasing an earlier one.
FINAL_ONE_HEARING_REPAIRS = {
    (101, 4): dict(
        accessible_followups=("Why would you miss it?", "Which would you miss most: messages, news, or videos?"),
        full_followups=("Why would you miss it?", "Which would you miss most: messages, news, or videos?"),
    ),
    (101, 6): dict(
        accessible_followups=("When would that rule be hardest to follow?", "Which is easier: turning off notifications or setting a time limit?"),
        full_followups=("When would that rule be hardest to follow?", "Which is easier: turning off notifications or setting a time limit?"),
    ),
    (101, 7): dict(
        accessible="Should a fourteen-year-old use a private or public social-media account?",
        accessible_ja="十四歳なら、SNSのアカウントは非公開と公開のどちらがよいですか？",
        full="Should a fourteen-year-old use a private or public social-media account?",
        full_ja="十四歳なら、SNSのアカウントは非公開と公開のどちらがよいですか？",
        accessible_followups=("Why would that be safer?", "Should strangers be able to send messages?"),
        full_followups=("Why would that be safer?", "Should strangers be able to send messages?"),
    ),
    (101, 8): dict(
        title="One part to lose",
        title_ja="なくしたい一つの部分",
        accessible="Which part of social media would you be happiest to lose?",
        accessible_ja="SNSのどんな部分なら、なくなってもうれしいですか？",
        full="Which part of social media would you be happiest to lose?",
        full_ja="SNSのどんな部分なら、なくなってもうれしいですか？",
        accessible_followups=("Why would life be better without it?", "Would social media feel calmer with no public comments?"),
        full_followups=("Why would life be better without it?", "Would social media feel calmer with no public comments?"),
    ),
    (102, 2): dict(
        title="Sarcasm or sadness",
        title_ja="皮肉、それとも悲しみ",
        accessible="Which is harder for AI to understand: sarcasm or sadness?",
        accessible_ja="AIにとって理解しにくいのは、皮肉と悲しみのどちらですか？",
        full="Which is harder for AI to understand: sarcasm or sadness?",
        full_ja="AIにとって理解しにくいのは、皮肉と悲しみのどちらですか？",
        accessible_followups=("What clue would a person notice?", "Could AI misunderstand 'I'm fine' in a text message?"),
        full_followups=("What clue would a person notice?", "Could AI misunderstand 'I'm fine' in a text message?"),
    ),
    (104, 5): dict(
        title="An experience for later",
        title_ja="将来してみたい経験",
        accessible="What is one experience you hope to have when you're older?",
        accessible_ja="年を重ねたときに、どんな経験をしてみたいですか？",
        full="What is one experience you hope to have when you're older?",
        full_ja="年を重ねたときに、どんな経験をしてみたいですか？",
    ),
    (105, 1): dict(
        accessible="Would you rather change a movie ending or a real historical decision?",
        accessible_ja="映画の結末と現実の歴史上の決断なら、どちらを変えたいですか？",
        full="Would you rather change a movie ending or a real historical decision?",
        full_ja="映画の結末と現実の歴史上の決断なら、どちらを変えたいですか？",
        accessible_followups=("Which ending or decision would you change?", "Would you make a sad movie ending happy?"),
        full_followups=("Which ending or decision would you change?", "Would you make a sad movie ending happy?"),
    ),
    (105, 2): dict(
        title="A choice that works out well",
        title_ja="結果的にうまくいく選択",
        accessible="Can a choice look wrong at first but work out well?",
        accessible_ja="最初は間違って見える選択が、結果的にうまくいくことはありますか？",
        full="Can a choice look wrong at first but work out well?",
        full_ja="最初は間違って見える選択が、結果的にうまくいくことはありますか？",
        accessible_followups=("What's a simple example?", "Does a good result mean it was a good choice?"),
        full_followups=("What's a simple example?", "Does a good result mean it was a good choice?"),
    ),
    (105, 3): dict(
        title="What shows a good choice",
        title_ja="よい選択を示すもの",
        accessible="Which better shows a good choice: fewer problems or happier people?",
        accessible_ja="問題が減ることと、人が幸せになることのどちらが、よい選択だったと分かりやすいですか？",
        full="When people disagree, which better shows a good choice: fewer problems or happier people?",
        full_ja="意見が分かれるとき、問題が減ることと、人が幸せになることのどちらが、よい選択だったと分かりやすいですか？",
        accessible_followups=("Can luck create a good result?", "Can a good choice still end badly?"),
        full_followups=("Can luck create a good result?", "Can a good choice still end badly?"),
    ),
    (105, 5): dict(
        title="One solution, another problem",
        title_ja="一つを解決して別の問題",
        accessible="Can solving one problem create a new one?",
        accessible_ja="一つの問題を解決すると、新しい問題が生まれることはありますか？",
        full="Can solving one problem create a new one?",
        full_ja="一つの問題を解決すると、新しい問題が生まれることはありますか？",
        accessible_followups=("What's a simple example?", "Can saving money now create a bigger cost later?"),
        full_followups=("What's a simple example?", "Can saving money now create a bigger cost later?"),
    ),
    (105, 8): dict(
        title="A fixable mistake",
        title_ja="直しやすい間違い",
        accessible="Which is easier to fix: being late or sending the wrong message?",
        accessible_ja="遅刻と、間違ったメッセージを送ることでは、どちらが直しやすいですか？",
        full="Which is easier to fix: being late or sending the wrong message?",
        full_ja="遅刻と、間違ったメッセージを送ることでは、どちらが直しやすいですか？",
        accessible_followups=("What would you do first?", "Which mistake gets worse if you wait?"),
        full_followups=("What would you do first?", "Which mistake gets worse if you wait?"),
    ),
    (106, 2): dict(
        title="A joke or an apology",
        title_ja="冗談、それとも謝罪",
        accessible="Which is harder to translate naturally: an English joke or an apology?",
        accessible_ja="自然に訳すのが難しいのは、英語の冗談と謝罪のどちらですか？",
        full="Which is harder to translate naturally: an English joke or an apology?",
        full_ja="自然に訳すのが難しいのは、英語の冗談と謝罪のどちらですか？",
        accessible_followups=("Does the tone change in Japanese?", "Which matters more in translation: the exact words or the feeling?"),
        full_followups=("Does the tone change in Japanese?", "Which matters more in translation: the exact words or the feeling?"),
    ),
    (106, 3): dict(
        title="Easier to say directly",
        title_ja="直接言いやすいこと",
        accessible="Which is easier to say directly in English: a request, an opinion, or a refusal?",
        accessible_ja="英語で直接言いやすいのは、お願い、意見、断りのどれですか？",
        full="Which is easier to say directly in English: a request, an opinion, or a refusal?",
        full_ja="英語で直接言いやすいのは、お願い、意見、断りのどれですか？",
        accessible_followups=("How would you say it differently in Japanese?", "Can a direct answer sound rude?"),
        full_followups=("How would you say it differently in Japanese?", "Can a direct answer sound rude?"),
    ),
    (106, 6): dict(
        title="A surprise in speaking English",
        title_ja="英語を話して驚いたこと",
        accessible="What surprised you most about speaking English?",
        accessible_ja="英語を話してみて、最も驚いたことは何ですか？",
        full="What surprised you most when English became part of a real conversation?",
        full_ja="実際の会話で英語を使ったとき、最も驚いたことは何ですか？",
        accessible_followups=("Was it easier or harder than expected?", "Which is harder for you: pronunciation or listening?"),
        full_followups=("Was it easier or harder than expected?", "Which is harder for you: pronunciation or listening?"),
    ),
    (106, 7): dict(
        title="Feeling different in English",
        title_ja="英語で感じる違い",
        accessible="Do you feel different when you speak English?",
        accessible_ja="英語を話すとき、いつもと違う自分を感じますか？",
        full="Do you feel different when you speak English?",
        full_ja="英語を話すとき、いつもと違う自分を感じますか？",
        accessible_followups=("Are you more direct, friendly, or quiet?", "Which is easier in English: making jokes or sharing opinions?"),
        full_followups=("Are you more direct, friendly, or quiet?", "Which is easier in English: making jokes or sharing opinions?"),
    ),
}
for (_number, _index), _changes in FINAL_ONE_HEARING_REPAIRS.items():
    TOPICS[_number]["prompts"][_index - 1].update(**_changes)

CLAIM_ORDER = {number: tuple(f"ft{number}-c{i:02d}" for i in range(1, 11)) for number in TOPIC_NUMBERS}

VOCABULARY = {
    101: {"new": "time sink|時間を奪うもの", "recycled": "", "assumed": "social media|SNS; app|アプリ; message|メッセージ; work|仕事; account|アカウント", "receptive": "algorithm|アルゴリズム; compulsive|やめにくい"},
    102: {"new": "blind spot|見落としやすい点", "recycled": "", "assumed": "AI|AI; work|仕事; task|作業; mistake|誤り; person|人", "receptive": "automation|自動化; accountability|説明責任"},
    103: {"new": "financial cushion|金銭的な余裕", "recycled": "", "assumed": "money|お金; worry|心配; cost|費用; save|貯める; enough|十分な", "receptive": "diminishing returns|限界効用の低下; uncertainty|不確かさ"},
    104: {"new": "life stage|人生の段階", "recycled": "", "assumed": "age|年齢; younger|より若い; older|より年上の; health|健康; responsibility|責任", "receptive": "nostalgia|懐かしさ; trade-off|一方を得るための代償"},
    105: {"new": "second-guess|後になって判断を疑う", "recycled": "", "assumed": "regret|後悔; choice|選択; change|変える; mistake|失敗; past|過去", "receptive": "counterfactual|反実仮想; hindsight bias|後知恵バイアス"},
    106: {"new": "word choice|言葉の選び方", "recycled": "", "assumed": "English|英語; Japanese|日本語; speak|話す; learn|学ぶ; language|言語", "receptive": "directness|直接さ; linguistic identity|言語上の自己認識"},
}

GLOSSES = {
    101: {"accessible": {4: ("time sink", "time sink", "時間を奪うもの")}, "full": {}},
    102: {"accessible": {5: ("blind spot", "blind spot", "見落としやすい点")}, "full": {8: ("accountability", "accountability", "説明責任")}},
    103: {"accessible": {2: ("financial cushion", "financial cushion", "金銭的な余裕")}, "full": {2: ("uncertainty", "uncertainty", "不確かさ")}},
    104: {"accessible": {}, "full": {5: ("Nostalgia", "nostalgia", "懐かしさ")}},
    105: {"accessible": {6: ("second-guess", "second-guess", "後になって判断を疑う")}, "full": {4: ("counterfactual", "counterfactual", "反実仮想")}},
    106: {"accessible": {}, "full": {2: ("directness", "directness", "直接さ")}},
}


def _render_dependencies():
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415
    return base, new_lesson


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    if topic_no not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_no, variant))
    _base, new_lesson = _render_dependencies()
    slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
    return new_lesson.ENGLISH / "tracks/3-freetalking/courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"


def _set_pending(head: str) -> str:
    marker = '<meta name="podo:proofread-status" content="complete">'
    head = re.sub(
        r'\n\s*<meta name="podo:proofread-status" content="(?:pending|complete)">',
        "",
        head,
        count=1,
    )
    return head.replace('<meta name="podo:vocabulary-status"', marker + '\n  <meta name="podo:vocabulary-status"', 1)


def _article_page(topic_no, data, variant, base):
    en_col, ja_col = (0, 2) if variant == "accessible" else (1, 3)
    rows = []
    for index, (article, claim_id) in enumerate(zip(data["articles"], CLAIM_ORDER[topic_no], strict=True), 1):
        en_markup, words = base.marked_text(article[en_col], GLOSSES[topic_no][variant].get(index))
        rows.append(f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{base.esc(article[ja_col])}</span>{words}</span></div>')
    title, title_ja = data["article_title"]
    body = '      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>\n      <div class="tutor-note">Answer the learner\'s questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article.</div>\n      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">\n' + "\n".join(rows) + "\n      </div>"
    return base.page("article", title, title_ja, body)


def _question_page(page_id, number, item, variant, base):
    lis = "".join(f"<li>{base.esc(value)}</li>" for value in item[f"{variant}_followups"])
    japanese = item[f"{variant}_ja"]
    if sum(item[variant].count(mark) for mark in ".!?") == 1:
        japanese = japanese.replace("。", "、")
    body = f'      <p class="section-subtitle ask"><span class="q-n">{number}</span><span class="ko">{base.esc(item[variant])}</span><span class="ja">{base.esc(japanese)}</span></p>\n      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span><ul class="tn-more">{lis}</ul></div></div>\n      <div class="fb" data-fb="{variant}-{page_id}" data-fb-spoken-label="Student\'s sentence"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'
    return base.page(page_id, item["title"], item["title_ja"], body)


def build(topic_no: int, variant: str) -> str:
    if topic_no not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_no, variant))
    base, new_lesson = _render_dependencies()
    track = new_lesson.ENGLISH / "tracks/3-freetalking"
    canonical = (track / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html").read_text(encoding="utf-8")
    data = TOPICS[topic_no]
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{data["slug"]}'
    head = new_lesson.retarget(head, review_id=f"FT-{topic_no}", lesson_id=slug, level="B1 accessible" if variant == "accessible" else "B2-C1 full", title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-20")
    head = _set_pending(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])
    goal_en, goal_ja = data["goal"]
    pages = [base.ft_contract.goal_page(title=data["title"], title_ja=data["ja"], topic_en=goal_en, topic_ja=goal_ja, data_act="Worth thinking about", kicker="WORTH THINKING ABOUT"), _article_page(topic_no, data, variant, base), base.extract_page(canonical, "lesson-style"), '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of the conversation.</span><span class="ja">全部の質問に答える必要はありません。会話の中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Use these pages as a flexible pool. Ask one question, react naturally, and share a brief real answer or relevant perspective of your own when it adds to the exchange. Skip freely and move to feedback with 2–3 minutes left.</div></div>\n''']
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple((f"q{i}", f"QUESTION {i}") for i in range(1, 7))
    pages.extend(_question_page(page_id, number, item, variant, base) for (page_id, number), item in zip(prompt_ids, data["prompts"], strict=True))
    pages.append(base.extract_page(canonical, "feedback"))
    return new_lesson.redepth(head + "\n".join(pages) + foot, output_path(topic_no, variant))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    for topic_no in TOPIC_NUMBERS:
        for variant in VARIANTS:
            output = output_path(topic_no, variant)
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
