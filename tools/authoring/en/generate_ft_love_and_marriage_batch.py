#!/usr/bin/env python3
"""Author and, once the canonical pilot is stable, render FT 57-63 pairs.

The module-level objects are the reviewed source specification.  Importing this
module performs no repository or canonical-deck reads.  Filesystem-dependent
imports and reads are deliberately confined to ``build``/``output_path``/``main``
so the source data can be reviewed and tested while the FT-1 pilot is protected.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


COURSE = "talk-love-and-marriage"
TOPIC_NUMBERS = tuple(range(57, 64))
VARIANTS = ("accessible", "full")
SENSITIVE_TOPICS = frozenset({58, 59, 60, 62, 63})

# The TOC deliberately retrieves these later Core moves, but Freetalking's
# current entry floor is CORE-53.  They are content-design dependencies, not
# legal recycled-vocabulary owners at checkpoint 9.
FUTURE_CORE_DEPENDENCIES = {
    58: ("CORE-58",),
    59: ("CORE-56", "CORE-66"),
    61: ("CORE-66", "CORE-97"),
    62: ("CORE-71",),
    63: ("CORE-62", "CORE-93"),
}
REACHABLE_CORE_RETRIEVAL = {
    57: ("CORE-43",),
    60: ("CORE-17", "CORE-49"),
    62: ("CORE-51",),
}
TOPIC_FORMAT = {57: "story", 58: "story", 59: "story", 60: "story", 61: "story", 62: "story", 63: "opinion"}
SHARED_SOURCE = {topic_no: f"KR 6-{topic_no - 56}" for topic_no in TOPIC_NUMBERS}
TOC_RETRIEVAL = {
    57: (("It's usually something small, like ___.", ("CORE-43",), False), ("I didn't expect to ___.", (), True)),
    58: (("The moment someone says ___, I'm done.", ("CORE-58",), False), ("I couldn't get past ___.", (), True)),
    59: (("I could live without ___, but not ___.", ("CORE-66", "CORE-56"), False), ("It's not negotiable.", (), True)),
    60: (("I know I ___ too much.", ("CORE-17",), False), ("I've got better at ___ing.", ("CORE-49",), False)),
    61: (("I'd definitely want ___.", ("CORE-66",), False), ("I'd rather not ___.", ("CORE-97",), False)),
    62: (("It took me ___ to ___.", ("CORE-51",), True), ("Looking back, I should have ___.", ("CORE-71",), False)),
    63: (("I can see why ___.", ("CORE-62",), False), ("To be fair, ___.", ("CORE-93",), False)),
}
# These rows preserve the authoritative TOC audit contract.  They are source
# review evidence only until the renderer has an approved metadata slot.
TOC_RETRIEVAL_AUDIT_ONLY = True

BRIEF_OPENINGS = {
    57: "What's something small that makes you like someone?",
    58: "Which is harder to forgive: a lie, an insult, or a broken promise?",
    59: "What's one thing you could never compromise on in a partner?",
    60: "Which relationship habit do you think is hardest to change?",
    61: "If you had a wedding tomorrow, what's the one thing you'd insist on?",
    62: "Why can some breakups be so hard to get over?",
    63: "Why might someone choose not to marry or have children?",
}


def prompt(
    job: str,
    title: str,
    title_ja: str,
    accessible: str,
    accessible_ja: str,
    accessible_followups: tuple[str, ...],
    *,
    full: str,
    full_ja: str,
    full_followups: tuple[str, ...],
    safety: str,
) -> dict[str, object]:
    return {
        "job": job,
        "title": title,
        "title_ja": title_ja,
        "accessible": accessible,
        "accessible_ja": accessible_ja,
        "accessible_followups": accessible_followups,
        "full": full,
        "full_ja": full_ja,
        "full_followups": full_followups,
        "safety": safety,
    }


def topic(
    *,
    slug: str,
    title: str,
    ko: str,
    ja: str,
    goal: tuple[str, str],
    outcomes: tuple[tuple[str, str], ...],
    article_title: tuple[str, str],
    articles: list[tuple[str, str, str, str]],
    prompts: list[dict[str, object]],
) -> dict[str, object]:
    return locals()


# Every article row is (accessible EN, full EN, accessible JA, full JA).
# The two Japanese columns are separately authored against their matching EN.
TOPICS = {
    57: topic(
        slug="a-little-thing-that-makes-you-like-someone",
        title="A little thing that makes you like someone",
        ko="누군가를 좋아하게 만드는 작은 것",
        ja="人を好きになる小さなきっかけ",
        goal=(
            "Let's talk about a small quality or gesture that can make someone appealing.",
            "人を魅力的に感じる小さな特徴や行動について話しましょう。",
        ),
        outcomes=(
            ("Name one small detail", "小さな特徴を一つ挙げる"),
            ("Explain why it matters", "なぜ大切か説明する"),
            ("Notice how preferences change", "好みの変化を考える"),
        ),
        article_title=("Why small things stand out", "小さなことが心に残る理由"),
        articles=[
            (
                "A small gesture can change how we feel about someone.",
                "A minor gesture can shape attraction before we know much about a person.",
                "ささやかな行動一つで、その人への感じ方が変わることがあります。",
                "相手をよく知る前から、何気ない行動が魅力の感じ方を左右することがあります。",
            ),
            (
                "Different people notice very different details.",
                "The details that attract attention vary sharply from person to person.",
                "人によって、目に留まる細かな点は大きく違います。",
                "どの細部に魅力を感じるかは、人によって大きく異なります。",
            ),
            (
                "Remembering a small detail can feel thoughtful.",
                "Remembering an unimportant-looking detail can signal real attentiveness.",
                "小さなことを覚えていてくれると、思いやりを感じることがあります。",
                "一見ささいなことを覚えていると、本当に注意を向けていたことが伝わります。",
            ),
            (
                "Kindness is often clearest when nobody is trying to impress anyone.",
                "Consideration can be most revealing when there is no audience to impress.",
                "誰かによく見られようとしていないときほど、親切さがはっきり表れることがあります。",
                "人に見せる必要のない場面ほど、さりげない配慮がその人らしさを表すことがあります。",
            ),
            (
                "A laugh, a voice, or an ordinary habit may become surprisingly appealing.",
                "A person's laugh, speaking rhythm, or ordinary habit may become unexpectedly attractive.",
                "笑い方や声、何気ない習慣が、意外と魅力的に感じられることがあります。",
                "笑い声や話すリズム、日常の癖が、思いがけず魅力として感じられることがあります。",
            ),
            (
                "What attracts us does not always match what we say we want.",
                "Our actual attraction does not always follow the qualities we claim to prefer.",
                "実際にひかれる点は、口で言う理想と一致するとは限りません。",
                "実際の魅力の感じ方は、自分が好むと言っている条件どおりにはならないことがあります。",
            ),
            (
                "One charming moment does not prove someone's whole character.",
                "A charming gesture is evidence of one moment, not a complete judgment of character.",
                "魅力的な一瞬だけで、その人の性格全体が分かるわけではありません。",
                "好ましい行動一つは一場面の手がかりであり、人柄全体の証明ではありません。",
            ),
            (
                "The same habit can seem sweet in one person and annoying in another.",
                "Context and trust can make the same habit endearing in one relationship and irritating in another.",
                "同じ癖でも、ある人なら好ましく、別の人なら気になることがあります。",
                "状況や信頼関係によって、同じ癖が愛らしくも、いら立たしくも感じられます。",
            ),
            (
                "The small things we value can change as we get older.",
                "Age and experience can shift which small qualities feel meaningful rather than superficial.",
                "年齢を重ねると、大切に感じる小さな点も変わることがあります。",
                "年齢や経験によって、表面的ではなく意味があると感じる小さな特徴は変化します。",
            ),
            (
                "A specific example often reveals the value behind a preference.",
                "Explaining one concrete example can expose the deeper value beneath an apparently minor preference.",
                "具体的な例を話すと、その好みの背景にある価値観が見えやすくなります。",
                "一つの具体例を説明すると、ささいに見える好みの奥にある価値観が明らかになります。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "A small attraction", "小さな魅力",
                BRIEF_OPENINGS[57], "どんな小さなことで、人を好きになりますか？",
                ("In what situation does it become noticeable?", "What first draws your attention to it?"),
                full="Which small gesture or quality can make you start liking someone?",
                full_ja="どんな小さな特徴や行動がきっかけで、人を好きになり始めますか？",
                full_followups=("In which situation does the gesture or quality become noticeable?", "What first makes it stand out?"),
                safety="real-or-general",
            ),
            prompt(
                "meaning", "What it suggests", "そこから感じること",
                "What might that small detail suggest about the person?", "その小さな点から、その人についてどんなことを感じますか？",
                ("Which value or quality might it show?", "What would stop you from reading too much into one detail?"),
                full="What might you infer from that small quality or gesture?",
                full_ja="その小さな特徴や行動から、どんなことを感じ取りますか？",
                full_followups=("Which value or quality might it indicate?", "How would you avoid treating one detail as proof of character?"),
                safety="impression-not-proof",
            ),
            prompt(
                "disclosure", "Saying it aloud", "本人に伝える",
                "Have you ever told the person that you liked that small thing about them—or would you keep it to yourself?",
                "その小さなところが好きだと本人に伝えたことはありますか。それとも、自分の中だけにしておきますか？",
                ("If you told someone, how did they react?", "If you would keep it private, what makes it hard to say?"),
                full="Have you ever named that small attraction to the person, or would you leave it unspoken?",
                full_ja="その小さな魅力を本人に伝えたことはありますか。それとも、言葉にせずにおきますか？",
                full_followups=("If you said it, how was the comment received?", "If you would leave it unspoken, what would make you hold back?"),
                safety="real-or-hypothetical",
            ),
            prompt(
                "recent-scene", "Noticing it", "気づいた場面",
                "When did you last notice that quality in someone you know or in a familiar example?",
                "知っている人や身近な例で、その特徴に最近気づいたのはいつですか？",
                ("What was happening at the time?", "If no recent example comes to mind, where might the quality appear?"),
                full="When did you last notice that quality in a real person, a familiar story, or fiction?",
                full_ja="実際の人、身近な話、または作品の中で、その特徴に最近気づいたのはいつですか？",
                full_followups=("Which part of the situation made it visible?", "If no recent example comes to mind, which setting would reveal it?"),
                safety="personal-familiar-or-fictional",
            ),
            prompt(
                "contrast", "What you say you want", "理想との違い",
                "Does that small thing match what you usually say you want in someone?",
                "その小さな点は、人に求めると普段言っていることと一致しますか？",
                ("If it matches, why is it important?", "If it does not, what surprises you about the difference?"),
                full="Does that attraction align with the qualities you consciously say you value?",
                full_ja="その魅力は、自分が意識して大切だと言う特徴と一致しますか？",
                full_followups=("If it aligns, what value connects them?", "If it does not, what does the mismatch reveal?"),
                safety="matching-or-mismatching",
            ),
            prompt(
                "boundary", "What turns it off", "魅力が消えるとき",
                "What could make that attractive habit stop feeling attractive?",
                "その魅力的な癖が、魅力的に感じられなくなるのはどんなときですか？",
                ("Does the person's intention matter?", "Which change in context would matter most?"),
                full="What could make the same appealing trait lose its attraction?",
                full_ja="同じ魅力的な特徴が、魅力を失うのはどのようなときですか？",
                full_followups=("How much would intention affect your judgment?", "Which change in context would alter the meaning?"),
                safety="trait-not-person",
            ),
            prompt(
                "change", "Changing with age", "年齢による変化",
                "Has what you notice in people changed with age—or even in the last few years?",
                "人のどこに目が向くかは、年齢とともに、またはここ数年だけでも変わりましたか？",
                ("If it changed, what matters more now?", "If it has not, which preference has stayed steady?"),
                full="Have the small qualities you value shifted with age or more recent experience?",
                full_ja="大切に感じる小さな特徴は、年齢や最近の経験によって変化しましたか？",
                full_followups=("If they shifted, what now carries more weight?", "If they did not, which preference has remained stable?"),
                safety="changed-or-unchanged",
            ),
            prompt(
                "flip", "What others notice", "自分の小さな魅力",
                "What small quality would you be happy for someone to notice in you?",
                "自分のどんな小さな特徴に気づいてもらえたら、うれしいですか？",
                ("How might that quality appear in everyday life?", "Would you want the person to mention it?"),
                full="Which understated quality would you be glad to have someone notice in you?",
                full_ja="自分のどんな控えめな特徴に気づいてもらえたら、うれしいですか？",
                full_followups=("How would that quality become visible in ordinary life?", "Would naming it make the moment better or awkward?"),
                safety="self-selected-quality",
            ),
        ],
    ),
    58: topic(
        slug="a-relationship-deal-breaker",
        title="A relationship deal-breaker",
        ko="관계를 끝내게 하는 한마디",
        ja="関係を終わらせる決定的な一言",
        goal=(
            "Let's talk about words that can cross a serious relationship boundary.",
            "人間関係の重大な境界線を越える言葉について話しましょう。",
        ),
        outcomes=(
            ("Name a possible deal-breaker", "受け入れられないことを挙げる"),
            ("Separate words from meaning", "言葉と意味を分けて考える"),
            ("Explain what repair would require", "修復に必要なことを説明する"),
        ),
        article_title=("Where a hard boundary comes from", "強い境界線が生まれる理由"),
        articles=[
            (
                "A deal-breaker is a boundary that can end a relationship.",
                "A deal-breaker is a boundary whose violation can make continuing a relationship unacceptable.",
                "ディールブレーカーとは、関係を終わらせることもある境界線です。",
                "ディールブレーカーとは、それを越えられると関係を続けられないと感じる境界線です。",
            ),
            (
                "Sometimes the exact words matter; sometimes the attitude behind them matters more.",
                "The decisive harm may lie in the literal words, the intention behind them, or the attitude they expose.",
                "言葉そのものが問題のこともあれば、その奥の態度のほうが重要なこともあります。",
                "決定的な傷つきは、言葉どおりの意味、意図、またはそこに表れた態度から生まれます。",
            ),
            (
                "A cruel joke can reveal disrespect even when the speaker calls it humour.",
                "Calling a remark a joke does not remove the contempt or disrespect it may reveal.",
                "残酷な冗談をユーモアだと呼んでも、相手への敬意のなさが表れることがあります。",
                "発言を「冗談」と呼んでも、そこに表れた軽蔑や敬意の欠如が消えるわけではありません。",
            ),
            (
                "One angry sentence and a repeated pattern are not always the same.",
                "An isolated remark made in anger differs from a repeated pattern, although either can still cause harm.",
                "怒って一度言った言葉と、繰り返される傾向は、同じとは限りません。",
                "怒りの中で一度出た発言と繰り返される傾向は異なりますが、どちらも傷つける可能性があります。",
            ),
            (
                "Context may explain a comment without making it acceptable.",
                "Context can explain why something was said without excusing its impact.",
                "事情が分かっても、その発言を受け入れられるとは限りません。",
                "背景事情は発言の理由を説明できますが、その影響を正当化するとは限りません。",
            ),
            (
                "Ending an interaction quickly can protect an important boundary.",
                "Ending an interaction immediately can be a legitimate way to protect a serious boundary.",
                "やり取りをすぐに終えることが、大切な境界線を守る方法になる場合があります。",
                "やり取りを直ちに終えることが、重大な境界線を守る正当な方法になることもあります。",
            ),
            (
                "In other cases, a short pause can prevent a mistaken final decision.",
                "In less clear cases, pausing before a final decision can separate shock from a settled judgment.",
                "一方で、少し時間を置くことで、早すぎる最終判断を避けられる場合もあります。",
                "判断が明確でない場合は、決める前に間を置くと、衝撃と落ち着いた判断を分けられます。",
            ),
            (
                "An apology matters more when it includes responsibility and change.",
                "Repair requires more than regret: it needs accountability, understanding, and credible change.",
                "謝罪には、責任を認めて行動を変えることが伴うと、より意味があります。",
                "関係の修復には後悔だけでなく、責任、理解、そして信頼できる変化が必要です。",
            ),
            (
                "People draw the line in different places.",
                "What feels forgivable to one person may violate a central value for another.",
                "どこを限界とするかは、人によって違います。",
                "ある人には許せることでも、別の人には大切な価値観を傷つけることがあります。",
            ),
            (
                "Knowing what we would never say can make our own boundaries clearer.",
                "Defining what we would refuse to say can clarify both the respect we expect and the respect we owe.",
                "自分なら決して言わない言葉を考えると、自分の境界線も明確になります。",
                "自分が言わないと決める言葉から、求める敬意と相手に示すべき敬意の両方が見えてきます。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "A possible deal-breaker", "受け入れられない一言",
                BRIEF_OPENINGS[58], "どんなことを言われたら、すぐに関係を終わらせようと思いますか？",
                ("A hypothetical type of comment is enough; what boundary would it cross?", "Would the relationship context change your answer?"),
                full="What kind of remark could make you end a relationship immediately?",
                full_ja="どのような発言なら、すぐに関係を終わらせる理由になり得ますか？",
                full_followups=("A hypothetical category is enough; which value would the remark violate?", "How much would the relationship context affect your judgment?"),
                safety="hypothetical-opt-out",
            ),
            prompt(
                "detail", "The kind of remark", "発言の種類",
                "Would the deal-breaker be an insult, a threat, a lie, or something else?",
                "受け入れられないのは、侮辱、脅し、うそ、それとも別の種類の発言ですか？",
                ("Which part makes it serious?", "Could a milder version be forgivable?"),
                full="Would your deal-breaker involve contempt, a threat, dishonesty, or another kind of remark?",
                full_ja="受け入れられないのは、軽蔑、脅し、不誠実さ、それとも別の種類の発言ですか？",
                full_followups=("Which feature makes the remark decisive?", "Would a less severe version remain repairable?"),
                safety="category-not-disclosure",
            ),
            prompt(
                "story", "Real or imagined", "実際または仮定",
                "Has anyone said something like that to you—or is this only a hypothetical boundary?",
                "似たことを言われた経験がありますか。それとも、これは仮定上の境界線ですか？",
                ("For a real case, what did you do next?", "For a hypothetical case, what response would protect you?"),
                full="Have you encountered a remark like that, or are you defining a hypothetical boundary?",
                full_ja="そのような発言を実際に受けたことがありますか。それとも、仮定上の境界線を考えていますか？",
                full_followups=("For a real case, what immediate response followed?", "For a hypothetical case, which response would protect the boundary?"),
                safety="real-or-hypothetical-opt-out",
            ),
            prompt(
                "response", "What happens next", "その後の対応",
                "In that real or imagined situation, would you leave, pause, or respond?",
                "その実際または想像の場面で、立ち去りますか、時間を置きますか、それとも応じますか？",
                ("What would you need in the first few minutes?", "Who, if anyone, could help you think clearly?"),
                full="In that real or hypothetical situation, would you leave, pause, confront the remark, or respond another way?",
                full_ja="その実際または仮定の場面で、立ち去る、時間を置く、発言に向き合う、または別の対応を選びますか？",
                full_followups=("What would matter most in the first few minutes?", "Whose perspective, if anyone's, could help you assess it?"),
                safety="real-or-hypothetical-continuity",
            ),
            prompt(
                "meaning", "Words or meaning", "言葉か意味か",
                "Would the exact words matter more, or the meaning behind them?",
                "言葉そのものと、その奥にある意味では、どちらがより重要ですか？",
                ("Could different wording carry the same harm?", "Could the same words mean something different in another context?"),
                full="Would the literal wording matter more, or the attitude and intention it revealed?",
                full_ja="文字どおりの言い方と、そこに表れた態度や意図では、どちらがより重要ですか？",
                full_followups=("Could different wording expose the same underlying harm?", "Could identical words carry a different meaning in another context?"),
                safety="abstract-analysis",
            ),
            prompt(
                "repair", "What is forgivable", "許せる条件",
                "What kind of hurtful comment could still be forgiven?",
                "傷つく発言でも、どのようなものなら許せる可能性がありますか？",
                ("What would a real apology need to include?", "Which repeated behaviour would make forgiveness harder?"),
                full="Under what conditions could a damaging remark still be forgivable?",
                full_ja="傷つける発言でも、どのような条件なら許せる可能性がありますか？",
                full_followups=("What would credible accountability require?", "Which repeated pattern would make repair unlikely?"),
                safety="conditions-not-personal-pressure",
            ),
            prompt(
                "boundary", "What you would not say", "自分が言わないこと",
                "What would you never say to a partner, even in an argument?",
                "口論中でも、パートナーに決して言わないことは何ですか？",
                ("A general category is enough; which value guides that limit?", "How would you express the same concern more safely?"),
                full="Which kind of remark would you refuse to direct at a partner, even during conflict?",
                full_ja="対立しているときでも、パートナーには向けないと決める発言はどのようなものですか？",
                full_followups=("A general category is enough; which principle sets that limit?", "How could the underlying concern be expressed without violating it?"),
                safety="general-category-opt-out",
            ),
            prompt(
                "flip", "Stating the boundary", "境界線の伝え方",
                "How could someone state a serious boundary before it is crossed?",
                "重大な境界線を越えられる前に、どう伝えればよいですか？",
                ("What wording would be clear without sounding like a threat?", "When would that conversation feel safest?"),
                full="How can a serious relationship boundary be communicated before a conflict tests it?",
                full_ja="対立によって試される前に、重大な関係の境界線をどのように伝えられますか？",
                full_followups=("Which wording would be firm without becoming coercive?", "What setting would make the conversation safer?"),
                safety="general-communication",
            ),
        ],
    ),
    59: topic(
        slug="something-you-could-never-compromise-on-in-a-partner",
        title="Something you could never compromise on in a partner",
        ko="파트너에게서 절대 타협할 수 없는 것",
        ja="パートナーについて絶対に妥協できないこと",
        goal=(
            "Let's talk about the values people should not have to compromise on.",
            "人が妥協すべきでない価値観について話しましょう。",
        ),
        outcomes=(
            ("Name one non-negotiable", "譲れないことを一つ挙げる"),
            ("Separate preferences from values", "好みと価値観を分ける"),
            ("Test whether the boundary can change", "境界線が変わる条件を考える"),
        ),
        article_title=("Preferences, values, and compromise", "好み・価値観・妥協"),
        articles=[
            (
                "A strong boundary usually protects a value, not just a preference.",
                "A durable non-negotiable usually protects a core value rather than a passing preference.",
                "強い境界線は、単なる好みではなく、大切な価値観を守ることが多いです。",
                "長く変わらない譲れない条件は、一時的な好みではなく、中心となる価値観を守っています。",
            ),
            (
                "People can compromise on a preference without surrendering everything.",
                "Partners can compromise on competing preferences without abandoning a central value.",
                "すべてを諦めなくても、好みについて妥協できます。",
                "中心的な価値観を捨てずに、競合する好みについて妥協できることがあります。",
            ),
            (
                "Taste, hobbies, and routines may allow more flexibility than honesty or safety.",
                "Preferences about taste, hobbies, and routines are often more negotiable than honesty, safety, or respect.",
                "好みや趣味、生活習慣は、誠実さや安全より柔軟に考えられることがあります。",
                "好み、趣味、生活習慣は、誠実さ、安全、敬意よりも妥協しやすい場合があります。",
            ),
            (
                "A concrete behaviour is easier to discuss than a vague ideal.",
                "Boundaries become more useful when they name observable behaviour instead of an abstract ideal partner.",
                "曖昧な理想より、具体的な行動のほうが話し合いやすくなります。",
                "理想の相手を抽象的に語るより、観察できる行動を示すほうが境界線は役立ちます。",
            ),
            (
                "Experience can make a long list of requirements shorter or more precise.",
                "Experience may shrink an unrealistic checklist while making a few essential boundaries more precise.",
                "経験によって、条件の長いリストが短くなったり、より具体的になったりします。",
                "経験を重ねると、現実的でない条件のリストが短くなる一方、少数の大切な境界線がより明確になることがあります。",
            ),
            (
                "Fear can make every preference feel non-negotiable.",
                "Fear of being hurt can turn ordinary preferences into rigid tests that no person can pass.",
                "傷つく不安があると、どんな好みも譲れないように感じることがあります。",
                "傷つくことへの恐れから、普通の好みが、誰にも満たせない厳しい条件になることがあります。",
            ),
            (
                "Pressure from others can also make an important boundary seem unreasonable.",
                "Social pressure can label a legitimate boundary unrealistic simply because it challenges expectations.",
                "周りからの圧力で、大切な境界線まで非現実的に見えることがあります。",
                "正当な境界線でも、期待に合わないというだけで、社会的な圧力から非現実的だと扱われることがあります。",
            ),
            (
                "Two reasonable boundaries can still conflict.",
                "Two people can hold defensible non-negotiables that are nevertheless incompatible.",
                "どちらももっともな境界線でも、互いに合わないことがあります。",
                "双方に理由のある譲れない条件でも、両立しないことがあります。",
            ),
            (
                "Discussing the important limits early can prevent false assumptions.",
                "Early discussion of major boundaries can reveal incompatibility before resentment builds.",
                "大切な限界を早めに話すと、誤った思い込みを防ぎやすくなります。",
                "重要な境界線を早く話し合うと、不満が積もる前に相性の不一致が分かることがあります。",
            ),
            (
                "A useful non-negotiable should be clear enough to explain.",
                "A defensible non-negotiable remains connected to a reason we can explain without controlling another person.",
                "意味のある譲れない条件は、理由を説明できるほど明確である必要があります。",
                "正当な譲れない条件は、相手を支配せずに説明できる理由と結びついています。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "One non-negotiable", "一つの譲れない条件",
                BRIEF_OPENINGS[59], "パートナーについて、絶対に妥協できないことを一つ挙げるとしたら何ですか？",
                ("A general or imagined partner is enough; what value does the boundary protect?", "What behaviour would show that the boundary had been crossed?"),
                full="Which single quality or behaviour would be non-negotiable in a partner?",
                full_ja="パートナーのどの特徴や行動が、絶対に譲れない条件になりますか？",
                full_followups=("A general or imagined partner is enough; which value underlies the boundary?", "What observable behaviour would violate it?"),
                safety="general-or-imagined-opt-out",
            ),
            prompt(
                "reason", "Why it matters", "大切な理由",
                "Why would that quality matter so much in a relationship?",
                "その特徴が関係の中でそれほど大切なのはなぜですか？",
                ("Which need does it protect?", "Could someone show the same value in a different way?"),
                full="Why would that quality carry enough weight to become non-negotiable?",
                full_ja="その特徴が譲れないほど重要になるのはなぜですか？",
                full_followups=("What real need or value does it protect?", "Could the same value be shown through different behaviour?"),
                safety="value-analysis",
            ),
            prompt(
                "contrast", "What you could compromise on", "妥協できること",
                "What could you compromise on in a partner without losing something important?",
                "大切なものを失わずに、パートナーについて妥協できることは何ですか？",
                ("Why is that preference more flexible?", "Where would the compromise need a limit?"),
                full="Which preference could you compromise on without abandoning a central value?",
                full_ja="中心となる価値観を損なわずに、どの好みなら調整できますか？",
                full_followups=("What makes that preference genuinely flexible?", "At which point would accommodation become too costly?"),
                safety="preference-not-person",
            ),
            prompt(
                "change", "How the list changes", "条件の変化",
                "Has your list of important qualities changed, stayed the same, or have you never kept a list?",
                "大切な特徴のリストは変わりましたか、変わっていませんか、それとも、もともとリストを作っていませんか？",
                ("If it changed, which item gained or lost importance?", "If it stayed the same, what has kept it steady?", "If you have no list, how do you recognize what matters when a situation arises?"),
                full="Has your list of essential qualities evolved, remained stable, or have you never maintained a list?",
                full_ja="大切な特徴のリストは変化しましたか、変わらずにいますか、それとも、そもそもリストを持っていませんか？",
                full_followups=("If it evolved, which criterion gained or lost weight?", "If it remained stable, what has sustained it?", "If you keep no list, how do you identify a priority when it becomes relevant?"),
                safety="changed-unchanged-or-no-list",
            ),
            prompt(
                "perspective", "Called unrealistic", "非現実的と言われる条件",
                "Has anyone called a boundary like that unrealistic—or can you name one that often gets judged that way?",
                "そのような境界線を非現実的だと言われたことはありますか。それとも、一般にそう判断されやすい境界線を一つ挙げられますか？",
                ("What reason did or might the other person give?", "Could social pressure be affecting the judgment?"),
                full="Has anyone challenged a boundary like that as unrealistic—or can you name a legitimate boundary often dismissed that way?",
                full_ja="そのような境界線を非現実的だと批判されたことはありますか。それとも、正当なのにそう退けられやすい境界線を一つ挙げられますか？",
                full_followups=("What reasoning supported or might support the criticism?", "How might social expectations distort the judgment?"),
                safety="real-or-general-criticism",
            ),
            prompt(
                "reassessment", "Were they right?", "見直す必要",
                "When should someone reconsider a relationship boundary?",
                "関係の境界線を見直したほうがよいのは、どんなときですか？",
                ("What new evidence would matter?", "Which value should remain protected during the change?"),
                full="What evidence would justify reassessing a boundary without abandoning the value behind it?",
                full_ja="背景の価値観を捨てずに境界線を見直すには、どのような根拠が必要ですか？",
                full_followups=("Would experience, consequences, or another perspective matter most?", "Which core value would still need protection?"),
                safety="general-reassessment",
            ),
            prompt(
                "conflict", "Two boundaries", "二つの境界線",
                "What if two people have reasonable boundaries that do not fit together?",
                "二人にもっともな境界線があっても、互いに合わない場合はどうしますか？",
                ("When is compromise possible?", "When is ending the match more honest?"),
                full="How should two people respond when their defensible non-negotiables are incompatible?",
                full_ja="二人の正当な譲れない条件が両立しないとき、どのように対応すべきですか？",
                full_followups=("Which differences might still allow negotiation?", "When would acknowledging incompatibility be more honest?"),
                safety="imagined-two-person-case",
            ),
            prompt(
                "flip", "A fair boundary", "公平な境界線",
                "How can someone state a non-negotiable without trying to control a partner?",
                "パートナーを支配しようとせずに、譲れない条件をどう伝えられますか？",
                ("What would make the statement clear?", "What choice must the other person still keep?"),
                full="How can a non-negotiable be expressed as a personal boundary rather than a demand for control?",
                full_ja="譲れない条件を、支配する要求ではなく、自分の境界線としてどう表現できますか？",
                full_followups=("Which wording would make ownership of the boundary clear?", "Which choice must remain with the other person?"),
                safety="general-communication",
            ),
        ],
    ),
    60: topic(
        slug="a-relationship-habit-you-know-you-should-change",
        title="A relationship habit you know you should change",
        ko="고쳐야 한다고 아는 연애 습관",
        ja="直したほうがよいと分かっている恋愛の癖",
        goal=(
            "Let's talk about relationship habits and how people can change them.",
            "人間関係の癖と、それを変える方法について話しましょう。",
        ),
        outcomes=(
            ("Name one unhelpful pattern", "役立たない傾向を一つ挙げる"),
            ("Describe what triggers it", "きっかけを説明する"),
            ("Choose a realistic alternative", "現実的な代わりを考える"),
        ),
        article_title=("Changing a relationship pattern", "関係の癖を変える"),
        articles=[
            (
                "Relationship habits often appear most clearly under stress.",
                "Relationship patterns often become most visible when stress reduces our patience and flexibility.",
                "関係の中での癖は、ストレスがあるときにはっきり表れることがよくあります。",
                "ストレスで忍耐力や柔軟性が低下すると、関係の中の傾向が最も見えやすくなります。",
            ),
            (
                "Some people interrupt; others shut down or ask for reassurance too often.",
                "Under pressure, one person may interrupt, another may shut down, and another may repeatedly seek reassurance.",
                "話を遮る人もいれば、黙り込んだり、安心できる言葉を何度も求めたりする人もいます。",
                "プレッシャーの中では、話を遮る人、心を閉ざす人、安心の確認を繰り返す人がいます。",
            ),
            (
                "We cannot change a habit until we notice when it starts.",
                "Change begins by identifying the trigger and the first moment the pattern appears.",
                "癖が始まる瞬間に気づかなければ、変えることはできません。",
                "変化は、きっかけと、その傾向が最初に表れる瞬間を見つけることから始まります。",
            ),
            (
                "Feedback can be useful without becoming a final judgment about us.",
                "A partner's feedback can provide evidence without becoming a complete verdict on our character.",
                "相手からの意見は、自分への最終評価にしなくても、役立つことがあります。",
                "パートナーの意見は、人柄全体への判決ではなく、行動を考える手がかりとして使えます。",
            ),
            (
                "Shame can make us defensive instead of helping us change.",
                "When feedback produces shame, defensiveness may protect the habit rather than correct it.",
                "恥ずかしさが強いと、変わるよりも身構えてしまうことがあります。",
                "指摘によって恥ずかしさが強まると、防御的な反応がその癖を直すどころか守ってしまうことがあります。",
            ),
            (
                "A small replacement action is more useful than a vague promise to be better.",
                "A specific replacement behaviour is more workable than a broad promise to become a better partner.",
                "もっとよくすると曖昧に約束するより、小さな代わりの行動を決めるほうが役立ちます。",
                "よりよいパートナーになるという広い約束より、具体的な代替行動のほうが実行しやすくなります。",
            ),
            (
                "Progress is not perfect, and an old habit may return in a hard week.",
                "Improvement is rarely linear; an old pattern may reappear when circumstances become difficult.",
                "改善は完璧には進まず、大変な週には昔の癖が戻ることもあります。",
                "改善は一直線ではなく、状況が厳しくなると古い傾向が再び表れることがあります。",
            ),
            (
                "The same habit can affect different partners in different ways.",
                "A behaviour that one person barely notices may feel deeply disruptive to another.",
                "同じ癖でも、相手によって受ける影響は違います。",
                "ある人がほとんど気にしない行動でも、別の人には関係を大きく乱すものに感じられます。",
            ),
            (
                "Warning someone about a habit can help, but it does not excuse the harm.",
                "Naming an unhelpful pattern in advance supports honesty, but it does not remove responsibility for its impact.",
                "自分の癖を前もって伝えることは役立ちますが、相手への影響がなくなるわけではありません。",
                "役立たない傾向を事前に伝えることは誠実さにつながりますが、その影響への責任を消すものではありません。",
            ),
            (
                "Looking at our strengths keeps self-improvement from becoming only self-criticism.",
                "Recognizing healthy habits prevents reflection from collapsing into a catalogue of personal faults.",
                "自分の長所にも目を向けると、改善が自己批判だけになるのを防げます。",
                "健全な習慣も認めることで、振り返りが自分の欠点を並べるだけになるのを防げます。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "One habit to change", "変えたい一つの癖",
                BRIEF_OPENINGS[60], "人間関係で、自分が直したほうがよいと分かっている癖は何ですか？",
                ("You may use a past relationship or a general pattern; what behaviour comes to mind?", "What usually triggers that behaviour?"),
                full="Which relationship pattern do you recognize as unhelpful in yourself?",
                full_ja="人間関係で、自分にあると気づいている役立たない傾向は何ですか？",
                full_followups=("You may use a past relationship or a general pattern; which behaviour fits?", "Which trigger tends to activate it?"),
                safety="past-or-general-opt-out",
            ),
            prompt(
                "notice", "When it appears", "癖が出るとき",
                "When did you first notice that habit in yourself—or when might someone notice a pattern like it?",
                "その癖に自分で最初に気づいたのはいつですか。それとも、一般にどんなときにその傾向に気づきそうですか？",
                ("For a real habit, what was happening?", "For a general example, what situation usually brings it out?"),
                full="When did you first recognize that pattern in yourself—or when might it become visible in a general example?",
                full_ja="その傾向を自分で最初に認識したのはいつですか。それとも、一般的な例ではどんなときに見えそうですか？",
                full_followups=("For a real pattern, which situation exposed it?", "For a general example, which conditions typically produce it?"),
                safety="real-or-general-continuity",
            ),
            prompt(
                "feedback", "What others say", "人からの指摘",
                "Has anyone pointed out that habit to you—or are you discussing a general example?",
                "その癖を誰かに指摘されたことはありますか。それとも、一般的な例について話していますか？",
                ("If someone said it, what part felt fair?", "If nobody did, what evidence could the person watch for?"),
                full="Has anyone identified that pattern for you, or are you examining a general case?",
                full_ja="その傾向を誰かに指摘されたことはありますか。それとも、一般的な例を考えていますか？",
                full_followups=("If it was identified, which part of the feedback felt accurate?", "If it was not, which observable evidence could reveal it?"),
                safety="personal-or-general-feedback",
            ),
            prompt(
                "progress", "Changing it", "変えられたか",
                "Have you got better at managing that habit—or what might make change possible?",
                "その癖は改善しましたか。それとも、何があれば変えられそうですか？",
                ("If it improved, which small action helped?", "If not, what keeps the old pattern going?"),
                full="Have you made progress in changing that pattern, or which condition would make improvement realistic?",
                full_ja="その傾向は改善しましたか。それとも、どんな条件なら現実的に変えられそうですか？",
                full_followups=("If it improved, which replacement behaviour mattered?", "If it has not, what continues to reinforce the pattern?"),
                safety="improved-or-not",
            ),
            prompt(
                "contrast", "A habit you dislike", "相手の気になる癖",
                "What relationship habit would be hard for you to handle in another person?",
                "ほかの人の関係の癖で、自分には受け止めにくいものは何ですか？",
                ("A general example is enough; what effect does the habit have?", "Could the person be unaware of it?"),
                full="Which relationship pattern in another person would be particularly difficult for you to tolerate?",
                full_ja="ほかの人のどのような関係の傾向が、自分には特に受け入れにくいですか？",
                full_followups=("A general example is enough; which effect makes it difficult?", "How might the person remain unaware of the impact?"),
                safety="general-example-opt-out",
            ),
            prompt(
                "warning", "What you would disclose", "前もって伝えること",
                "What habit would you warn a future or imagined partner about?",
                "将来または想像上のパートナーに、どんな癖を前もって伝えますか？",
                ("How could you say it without using it as an excuse?", "What effort would you promise to make?"),
                full="Which pattern would you disclose to a future or hypothetical partner?",
                full_ja="将来または仮定上のパートナーに、どの傾向を前もって伝えますか？",
                full_followups=("How could you name it without avoiding responsibility?", "Which concrete effort could accompany the disclosure?"),
                safety="future-or-imagined",
            ),
            prompt(
                "strategy", "A better response", "よりよい対応",
                "If it is your habit, what could you do instead; if it is a general example, what could the person do?",
                "自分の癖なら自分が、一般的な例ならその人が、代わりに何をできますか？",
                ("For your own habit, what might get in the way the first time you try the new response?", "For a general example, what support could make the replacement easier?"),
                full="If the pattern is yours, which replacement behaviour could you use; in a general case, which response could the person use?",
                full_ja="自分の傾向なら自分が、一般的な例ならその人が、どの代替行動を使えますか？",
                full_followups=("For your own pattern, which obstacle could block the replacement under stress?", "For a general case, what support could make the new response last?"),
                safety="self-or-general-strategy",
            ),
            prompt(
                "flip", "A healthy habit", "続けたいよい癖",
                "For your own case or a general example, which healthy relationship habit is worth keeping?",
                "自分の例でも一般的な例でも、続ける価値があるのはどの健全な関係の習慣ですか？",
                ("For your own case, how does the habit help the other person?", "For a general example, what makes that habit healthy?"),
                full="For your own case or a general example, which healthy pattern should remain while the unhelpful one changes?",
                full_ja="自分の例でも一般的な例でも、役立たない傾向を変える間、残すべきなのはどの健全な傾向ですか？",
                full_followups=("For your own case, how does the pattern support the other person?", "For a general case, what makes the pattern worth protecting?"),
                safety="self-or-general-strength",
            ),
        ],
    ),
    61: topic(
        slug="one-thing-your-wedding-would-have-to-include",
        title="One thing your wedding would have to include",
        ko="내 결혼식에 꼭 있어야 할 한 가지",
        ja="自分の結婚式に欠かせない一つのこと",
        goal=(
            "Let's talk about what can make a wedding meaningful.",
            "結婚式を意味のあるものにする要素について話しましょう。",
        ),
        outcomes=(
            ("Choose one element to keep", "残すものを一つ選ぶ"),
            ("Choose what to cut", "省くものを選ぶ"),
            ("Explain who the event is for", "誰のための式か説明する"),
        ),
        article_title=("What makes a wedding feel personal", "自分らしい結婚式を作るもの"),
        articles=[
            (
                "A wedding combines a private commitment with a public event.",
                "A wedding can bring a private commitment into a public ritual shared with other people.",
                "結婚式は、個人的な約束と、人が集まる行事を組み合わせます。",
                "結婚式は、二人の私的な約束を、ほかの人と共有する公の儀式にすることがあります。",
            ),
            (
                "One small element can carry more meaning than an expensive setting.",
                "A single symbolic element may carry more personal meaning than an elaborate venue.",
                "高価な会場よりも、一つの小さな要素に大きな意味があることがあります。",
                "豪華な会場より、一つの象徴的な要素のほうが個人的な意味を持つことがあります。",
            ),
            (
                "Guests, cost, family wishes, and tradition can pull the plan in different directions.",
                "Guest expectations, budget, family wishes, and tradition can create competing demands.",
                "招待客、費用、家族の希望、伝統によって、計画が別々の方向に引っ張られることがあります。",
                "招待客の期待、予算、家族の希望、伝統から、互いに競合する要求が生じることがあります。",
            ),
            (
                "A wedding tradition is a choice, not an automatic duty.",
                "A wedding tradition can be kept, adapted, or removed rather than treated as an unquestioned obligation.",
                "結婚式の習慣は、当然の義務ではなく、選べるものです。",
                "結婚式の伝統は、疑わない義務ではなく、残す、変える、省くという選択ができます。",
            ),
            (
                "Cutting one part may protect the thing that matters most.",
                "Removing a familiar element can preserve time, money, or attention for the event's real priority.",
                "一つを省くことで、いちばん大切なものを守れる場合があります。",
                "よくある要素を一つなくすと、本当の優先事項に時間、費用、注意を使えることがあります。",
            ),
            (
                "Decisions may involve the couple, their families, or the wider community.",
                "Wedding decisions often expose how authority is shared among the couple, families, and community.",
                "決めるときには、二人、家族、周りの人が関わることがあります。",
                "結婚式の決定から、二人、家族、地域の間で決定権がどう分かれているかが見えます。",
            ),
            (
                "The best wedding memory is not always the most expensive one.",
                "A memorable wedding moment often depends more on connection than expense or perfection.",
                "いちばんよい結婚式の思い出が、いちばん高価なものとは限りません。",
                "心に残る結婚式の瞬間は、費用や完璧さより、人とのつながりから生まれることがあります。",
            ),
            (
                "Some people would prefer a small legal ceremony or no wedding event at all.",
                "For some people, a private legal ceremony—or no wedding event—is more authentic than a celebration.",
                "小さな手続きだけの式や、結婚式をまったくしないことを選ぶ人もいます。",
                "人によっては、祝宴より、二人だけの法的な手続きや式をしない選択のほうが自分らしく感じられます。",
            ),
            (
                "A hypothetical wedding can reveal values even for someone with no plans to marry.",
                "Imagining the event can clarify values about family, privacy, and celebration without implying a plan to marry.",
                "結婚する予定がなくても、仮定の結婚式から大切な価値観が見えることがあります。",
                "結婚の予定を前提にしなくても、式を想像すると、家族、私生活、祝い方への価値観が明確になります。",
            ),
            (
                "The event feels personal when its choices tell one clear story.",
                "A wedding feels coherent when its choices express the people involved rather than a borrowed checklist.",
                "選んだものに一つのはっきりした意味があると、式は自分らしく感じられます。",
                "借りた条件表ではなく、関わる人を表す選択がそろうと、結婚式に一貫した自分らしさが生まれます。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "One thing to include", "欠かせない一つ",
                BRIEF_OPENINGS[61], "もし明日結婚式をするとしたら、絶対に入れたいものを一つ挙げるとしたら何ですか？",
                ("What feeling or value should that choice create?", "Who else, if anyone, would it matter to?"),
                full="If you were holding a wedding tomorrow, which single element would be essential?",
                full_ja="もし明日結婚式を行うなら、欠かせない要素を一つ選ぶとしたら何ですか？",
                full_followups=("Which value would that element express?", "Who else, if anyone, would share its meaning?"),
                safety="hypothetical-choice",
            ),
            prompt(
                "keep", "What stays", "残すもの",
                "Which wedding tradition would you definitely keep—or would you invent your own?",
                "どの結婚式の習慣を必ず残しますか。それとも、自分らしい習慣を新しく作りますか？",
                ("What does the tradition mean to you?", "How might you change it to fit the people involved?"),
                full="Which wedding tradition would you preserve, adapt, or replace with one of your own?",
                full_ja="どの結婚式の伝統を残す、変える、または自分たちのものに置き換えますか？",
                full_followups=("Which value does the tradition express?", "How would you adapt it to the people involved?"),
                safety="keep-adapt-or-invent",
            ),
            prompt(
                "cut", "What goes", "省くもの",
                "What common part of a wedding would you rather not include?",
                "結婚式によくあるもので、入れたくないものは何ですか？",
                ("What problem would cutting it solve?", "Would any guest miss it?"),
                full="Which conventional wedding element would you prefer to remove?",
                full_ja="一般的な結婚式のどの要素を省きたいですか？",
                full_followups=("Which cost, pressure, or distraction would removal reduce?", "Whose expectation might the decision challenge?"),
                safety="hypothetical-edit",
            ),
            prompt(
                "decision", "Who decides", "決める人",
                "Who should have the strongest voice in wedding decisions?",
                "結婚式の決定で、誰の意見を最も重く考えるべきですか？",
                ("Which decision could reasonably involve family?", "Which decision should stay with the couple?"),
                full="How should decision-making power be shared among the couple, families, and other people involved?",
                full_ja="二人、家族、関係する人々の間で、結婚式の決定権をどう分けるべきですか？",
                full_followups=("Which decision could legitimately involve family?", "Which choice should remain private to the couple?"),
                safety="general-roles",
            ),
            prompt(
                "example", "A memorable wedding", "心に残る結婚式",
                "What is the best wedding detail you have experienced, heard about, or seen in a story?",
                "実際に見た、聞いた、または物語で知った結婚式で、いちばんよかった細部は何ですか？",
                ("What made the detail memorable?", "Would it work in a very small wedding?"),
                full="Which wedding detail from experience, a familiar account, or fiction has impressed you most?",
                full_ja="実体験、身近な話、または作品の中で、最も印象に残った結婚式の細部は何ですか？",
                full_followups=("Which quality made the detail memorable?", "Would its meaning survive in a much smaller event?"),
                safety="experience-familiar-or-fictional",
            ),
            prompt(
                "friction", "The worst part", "大変な部分",
                "What part of weddings often creates the most stress?",
                "結婚式のどの部分が、いちばんストレスを生みやすいですか？",
                ("Who usually carries that stress?", "What simple change could reduce it?"),
                full="Which aspect of weddings most often creates unnecessary pressure?",
                full_ja="結婚式のどの面が、最も不要な負担を生みやすいですか？",
                full_followups=("Who tends to absorb that pressure?", "Which structural change could reduce it?"),
                safety="general-observation",
            ),
            prompt(
                "alternative", "Skipping the event", "式をしない選択",
                "Would you ever choose a tiny ceremony or no wedding event at all?",
                "小さな式だけにする、または結婚式をまったくしない選択をしますか？",
                ("What would that choice protect?", "How might family or friends respond?"),
                full="Could a private legal ceremony—or no wedding event—feel more authentic to you?",
                full_ja="二人だけの法的な手続きや、結婚式をしない選択のほうが、自分らしいと感じる可能性はありますか？",
                full_followups=("Which value would that choice protect?", "How would you handle other people's expectations?"),
                safety="wedding-or-no-wedding",
            ),
            prompt(
                "flip", "What the day is for", "式の目的",
                "What should a wedding be for, if people choose to have one?",
                "結婚式をするなら、それは何のためのものであるべきですか？",
                ("Who should feel most represented by the day?", "Which single choice would show that purpose?"),
                full="If people choose to hold a wedding, what central purpose should guide the event?",
                full_ja="結婚式を行うと選んだ場合、どんな中心的な目的が式を導くべきですか？",
                full_followups=("Whose identities or relationships should the event represent?", "Which design choice would express that purpose most clearly?"),
                safety="conditional-no-assumption",
            ),
        ],
    ),
    62: topic(
        slug="a-breakup-that-was-hard-to-get-over",
        title="A breakup that was hard to get over",
        ko="극복하기 힘들었던 이별",
        ja="立ち直るのが難しかった別れ",
        goal=(
            "Let's talk about why breakups can be difficult and what helps people recover.",
            "別れが難しい理由と、立ち直るために役立つことを話しましょう。",
        ),
        outcomes=(
            ("Choose a personal or general example", "個人的または一般的な例を選ぶ"),
            ("Name what made recovery hard", "回復を難しくしたことを挙げる"),
            ("Describe one sign of moving forward", "前に進むサインを説明する"),
        ),
        article_title=("Why some endings take time", "立ち直るまで時間がかかる理由"),
        articles=[
            (
                "There is no correct amount of time to get over a breakup.",
                "Recovery from a breakup has no universal schedule or correct emotional pace.",
                "別れから立ち直るのに、誰にでも当てはまる正しい期間はありません。",
                "別れからの回復には、誰にでも当てはまる予定や、「正しい」と言える感情の進み方はありません。",
            ),
            (
                "The loss may include routines, plans, friendships, and a future we imagined.",
                "A breakup can remove shared routines, mutual friendships, practical plans, and an imagined future at once.",
                "失うものには、習慣、予定、友人関係、想像していた未来も含まれることがあります。",
                "別れによって、共有した習慣、共通の友人、現実的な計画、想像した未来を一度に失うことがあります。",
            ),
            (
                "The hardest part is not always missing the person.",
                "The most difficult loss may be identity, certainty, or daily structure rather than the person alone.",
                "いちばんつらいのが、その人を恋しく思うこととは限りません。",
                "最もつらい喪失は、相手だけでなく、自分らしさ、安心感、日々の形である場合があります。",
            ),
            (
                "A clear final explanation is helpful, but it is not always available.",
                "Closure can help, yet a complete and satisfying explanation is not always possible.",
                "最後にはっきり説明してもらえると役立ちますが、いつも得られるとは限りません。",
                "区切りは助けになりますが、完全で納得できる説明が得られるとは限りません。",
            ),
            (
                "Some people need company; others first need privacy and routine.",
                "Recovery may require conversation, solitude, practical structure, or different forms of support at different times.",
                "誰かと一緒にいたい人もいれば、まず一人の時間や日課が必要な人もいます。",
                "回復には、会話、一人の時間、生活の形、または時期によって異なる支えが必要です。",
            ),
            (
                "Time helps, but avoiding every feeling does not always heal it.",
                "Time can soften pain, but time alone does not process emotions that are continually avoided.",
                "時間は助けになりますが、気持ちをすべて避けても回復するとは限りません。",
                "時間は痛みを和らげますが、避け続けた感情を時間だけで整理できるとは限りません。",
            ),
            (
                "Looking back can change how we understand the relationship.",
                "Distance can reveal patterns, needs, and warnings that were difficult to see inside the relationship.",
                "あとから振り返ると、その関係の理解が変わることがあります。",
                "時間と距離ができると、関係の中では見えにくかった傾向、必要、注意点が見えることがあります。",
            ),
            (
                "Learning from an ending is different from blaming ourselves for all of it.",
                "Reflection can identify our responsibility without turning the entire ending into personal failure.",
                "別れから学ぶことと、すべて自分のせいにすることは違います。",
                "振り返りによって自分の責任は見つけられますが、別れ全体を自分の失敗にする必要はありません。",
            ),
            (
                "Nobody has to share private details in order to discuss recovery.",
                "A useful conversation about recovery does not require disclosing identities, dates, or painful private facts.",
                "回復について話すために、私的な細部を話す必要はありません。",
                "回復について役立つ会話をするのに、相手の情報、時期、つらい私的な事実を明かす必要はありません。",
            ),
            (
                "Moving forward does not mean the relationship meant nothing.",
                "Recovery can preserve the significance of a relationship without allowing the ending to control the present.",
                "前に進むことは、その関係に意味がなかったということではありません。",
                "回復とは、関係の意味を残しながらも、その終わりに現在を支配させないことです。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "Only what feels safe", "話せる範囲で",
                BRIEF_OPENINGS[62] + " A personal, familiar, fictional, or general example is fine, and you may skip specifics.",
                "話せる範囲で、経験した中でいちばん立ち直るのが難しかった別れはどんなものでしたか？ 自分の経験、身近な話、作品、一般的な例のどれでもよく、具体的な話は省けます。",
                ("For a personal example, which part feels safe to discuss?", "For a familiar, fictional, or general example, what made the ending difficult?"),
                full="As much as feels safe, which breakup was hardest to recover from? A personal, familiar, fictional, or general case is welcome, and specifics may remain private.",
                full_ja="安心して話せる範囲で、立ち直るのが最も難しかった別れはどれですか？ 自分の経験、身近な話、作品、一般的な事例のどれでもよく、具体的な内容は伏せられます。",
                full_followups=("For a personal case, which aspect feels safe to examine?", "For a familiar, fictional, or general case, what made the ending difficult?"),
                safety="explicit-personal-opt-out",
            ),
            prompt(
                "event", "What ended", "終わったもの",
                "What can change after a relationship ends?",
                "関係が終わったあと、何が変わることがありますか？",
                ("In a personal, familiar, or fictional example, what changed first?", "Without a specific example, which consequence often appears first?"),
                full="Which immediate changes can follow the end of a relationship?",
                full_ja="関係が終わった直後には、どのような変化が起こり得ますか？",
                full_followups=("In a personal, familiar, or fictional case, which immediate consequence mattered most?", "Without a specific case, which consequence tends to emerge first?"),
                safety="selected-or-no-example-continuity",
            ),
            prompt(
                "duration", "Time to recover", "回復までの時間",
                "What affects how long it takes to recover from a breakup?",
                "別れから立ち直るまでの時間には、何が影響しますか？",
                ("If recovery moved forward in the example, what showed that change?", "If it is ongoing or not getting easier yet, what makes progress hard to judge?", "Without a specific example, which factor generally changes the timeline?"),
                full="Which factors shape the pace of recovery after a relationship ends?",
                full_ja="関係が終わったあとの回復の速さは、どのような要因に左右されますか？",
                full_followups=("If recovery progressed in the case, which sign marked that change?", "If it remains ongoing or stalled, what makes progress difficult to assess?", "Without a specific case, which factor generally shapes the timeline most strongly?"),
                safety="progressed-ongoing-stalled-or-general",
            ),
            prompt(
                "support", "Who knew", "誰に話したか",
                "What affects whether someone tells other people about a breakup?",
                "別れについて誰かに話すかどうかには、何が影響しますか？",
                ("In a personal, familiar, or fictional example, who knew and what support helped?", "If the experience stayed private or the discussion is general, what can make privacy feel necessary?"),
                full="Which factors influence whether someone seeks support after a breakup?",
                full_ja="別れたあとに支えを求めるかどうかは、どのような要因に左右されますか？",
                full_followups=("In a personal, familiar, or fictional case, which form of support was available?", "If the experience remained private or the case is general, what purpose can privacy serve?"),
                safety="selected-private-or-general-support",
            ),
            prompt(
                "help", "What helped", "助けになったもの",
                "What helped—or what could help—someone begin to get over that kind of breakup?",
                "そのような別れから立ち直り始めるために、何が役立ちましたか。または何が役立ちそうですか？",
                ("Was the help emotional, practical, or both?", "What advice would probably not help?"),
                full="What helped, or could help, someone begin to get over that kind of ending?",
                full_ja="そのような別れから回復し始めるために、何が役立ちましたか。または何が役立ち得ますか？",
                full_followups=("Was the useful support emotional, practical, or a combination?", "Which common response might make recovery harder?"),
                safety="actual-or-hypothetical-help",
            ),
            prompt(
                "hindsight", "What is clearer now", "今分かること",
                "What might someone understand later that was hard to see at the time?",
                "そのときは見えにくくても、あとになって分かることは何ですか？",
                ("Which pattern might become clearer?", "How could hindsight change the story without blaming one person for everything?"),
                full="Which truth might become visible only after enough distance from the breakup?",
                full_ja="別れから十分な距離ができて初めて、どんな事実が見えることがありますか？",
                full_followups=("Which relationship pattern might emerge in hindsight?", "How can the interpretation change without assigning all blame to one person?"),
                safety="general-hindsight",
            ),
            prompt(
                "past-self", "What to say then", "当時伝えること",
                "What would you tell the person in your example—or someone in general—at the beginning of a breakup?",
                "自分の例の人、または一般的な誰かに、別れたばかりの時点で何を伝えますか？",
                ("What would they probably not be ready to hear?", "Which practical next step would be kind and realistic?"),
                full="What would you tell the person in your case—or someone in general—at the earliest stage of a breakup?",
                full_ja="自分の事例の人、または一般的な誰かに、別れの最も早い段階で何を伝えますか？",
                full_followups=("Which truth might they be unable to receive yet?", "Which practical next step would combine kindness with realism?"),
                safety="third-person-advice",
            ),
            prompt(
                "flip", "A sign of moving forward", "前に進むサイン",
                "What is one sign that someone is moving forward without erasing the past?",
                "過去を消さずに前へ進んでいると分かるサインは一つ何ですか？",
                ("Would the sign be emotional, practical, or social?", "What might still remain difficult at that point?"),
                full="Which sign shows that recovery is underway without pretending the relationship was meaningless?",
                full_ja="その関係に意味がなかったふりをせず、回復が進んでいると分かるサインは何ですか？",
                full_followups=("Would the clearest evidence be emotional, practical, or social?", "Which difficulty could reasonably remain even then?"),
                safety="general-recovery-close",
            ),
        ],
    ),
    63: topic(
        slug="choosing-not-to-marry-or-have-children",
        title="Choosing not to marry or have children",
        ko="결혼이나 출산을 선택하지 않는 것",
        ja="結婚や子どもを持たない選択",
        goal=(
            "Let's talk about different choices around marriage and children.",
            "結婚や子どもについてのさまざまな選択を話しましょう。",
        ),
        outcomes=(
            ("Describe one perspective", "一つの考え方を説明する"),
            ("Separate marriage from parenthood", "結婚と親になることを分ける"),
            ("Respond without pressure", "圧力をかけずに応じる"),
        ),
        article_title=("More than one life path", "一つではない生き方"),
        articles=[
            (
                "Marriage and having children are separate decisions.",
                "Marriage and parenthood are distinct decisions, even when social expectations link them.",
                "結婚することと、子どもを持つことは別の決定です。",
                "社会の期待で結びつけられていても、結婚と親になることは別々の決定です。",
            ),
            (
                "People may want both, one, neither, or remain unsure.",
                "A person may want marriage and children, one without the other, neither, or more time before deciding.",
                "両方、一方だけ、どちらも望まない、またはまだ分からないという人がいます。",
                "結婚と子どもの両方、一方だけ、どちらも望まない、または決めるまで時間が必要という人がいます。",
            ),
            (
                "Reasons can include desire, health, money, care work, freedom, or values.",
                "Choices may reflect desire, health, finances, caregiving, freedom, relationships, or deeply held values.",
                "理由には、希望、健康、費用、人を支える責任、自由、価値観などがあります。",
                "選択には、希望、健康、経済状況、誰かを支える責任、自由、人間関係、強い価値観が関わります。",
            ),
            (
                "Some reasons are private, and nobody owes a complete explanation.",
                "Because the decision can involve intimate circumstances, a person does not owe others a full justification.",
                "理由には私的なものもあり、すべてを説明する義務はありません。",
                "その決定には非常に私的な事情が関わるため、ほかの人に完全な説明をする義務はありません。",
            ),
            (
                "Family interest can feel supportive to one person and like social pressure to another.",
                "The same family question may feel caring in one context and coercive in another.",
                "家族の関心は、支えに感じる人もいれば、社会的な圧力に感じる人もいます。",
                "同じ家族からの質問でも、ある状況では思いやりに、別の状況では強制的な圧力に感じられます。",
            ),
            (
                "Relatives may worry about loneliness, regret, or family continuity.",
                "Family concern may focus on future loneliness, regret, care, or continuity across generations.",
                "家族は、将来の孤独や後悔、家族のつながりが続くかどうかを心配する場合があります。",
                "家族は、将来の孤独、後悔、ケア、家族が次の世代へ続くかどうかを心配することがあります。",
            ),
            (
                "Those worries can be sincere without deciding what another adult should choose.",
                "Concern can be genuine while still leaving the final decision with the adult whose life it shapes.",
                "その心配が本気でも、別の大人の選択を決めるものではありません。",
                "心配が本物でも、その人生を生きる大人本人に最終判断を残すことはできます。",
            ),
            (
                "A person's view may change, stay stable, or remain undecided.",
                "Views about marriage or children may evolve, remain consistent, or stay genuinely unresolved.",
                "考えは変わることも、変わらないことも、決まらないままのこともあります。",
                "結婚や子どもについての考えは、変化する、安定している、または本当に未決定のままということがあります。",
            ),
            (
                "Housing, work, policy, and support can affect a choice without fully explaining it.",
                "Material conditions and public policy shape available choices, but they do not reduce every decision to economics.",
                "住まい、仕事、制度、支援は選択に影響しますが、それだけで理由のすべては説明できません。",
                "生活条件や公共政策は選べる道に影響しますが、すべての決定を経済だけで説明できるわけではありません。",
            ),
            (
                "Respect begins by asking without assuming that one answer is correct.",
                "A neutral conversation leaves room for multiple life paths and does not recruit the other person to a position.",
                "一つの答えが正しいと決めつけずに聞くことが、敬意の始まりです。",
                "中立的な会話は、複数の生き方を認め、相手を特定の立場へ引き込もうとしません。",
            ),
        ],
        prompts=[
            prompt(
                "opening", "Someone's decision", "誰かの選択",
                BRIEF_OPENINGS[63], "結婚しない、または子どもを持たないと決めた人を知っていますか？",
                ("If no personal example comes to mind, which familiar or public perspective could you discuss?", "Is the decision about marriage, children, or both?"),
                full="Do you know anyone who has chosen not to marry, not to have children, or both?",
                full_ja="結婚しない、子どもを持たない、またはその両方を選んだ人を知っていますか？",
                full_followups=("If no personal example comes to mind, which familiar or public perspective could you examine?", "Does the perspective concern marriage, parenthood, or both?"),
                safety="personal-familiar-or-public-opt-out",
            ),
            prompt(
                "reason", "Their reason", "その理由",
                "What reason does the person in that real, familiar, or public example give, if any?",
                "その実際、身近、または公に知られた例の人は、理由があるとすれば何と説明していますか？",
                ("Is the reason practical, personal, or based on values?", "Which part should remain private?"),
                full="What reason, if any, is given in that real, familiar, or public example?",
                full_ja="その実際、身近、または公に知られた例では、理由があるとすれば何ですか？",
                full_followups=("Is the reasoning practical, personal, value-based, or mixed?", "Which part of the explanation does nobody need to disclose?"),
                safety="selected-example-no-explanation-required",
            ),
            prompt(
                "reaction", "What people say", "周りの反応",
                "What do people often say to someone who makes that choice?",
                "その選択をした人に、周りはよく何と言いますか？",
                ("Which comment may sound caring but feel like pressure?", "What would a more neutral response sound like?"),
                full="How do other people commonly respond to someone who chooses that life path?",
                full_ja="その生き方を選ぶ人に、周りは一般にどのように反応しますか？",
                full_followups=("Which response may be intended as concern but experienced as pressure?", "What would genuine curiosity without advocacy sound like?"),
                safety="general-social-response",
            ),
            prompt(
                "change", "Your view", "自分の考えの変化",
                "Has your own view changed, stayed the same, or remained undecided?",
                "自分の考えは変わりましたか、変わっていませんか、それともまだ決まっていませんか？",
                ("What experience or idea influenced the current view?", "Which part are you least certain about?"),
                full="Has your perspective shifted, remained stable, or stayed genuinely unresolved?",
                full_ja="自分の見方は変化しましたか、安定したままですか、それとも本当に未決定ですか？",
                full_followups=("Which experience, condition, or idea shaped the current perspective?", "Where does uncertainty remain?"),
                safety="changed-stable-or-undecided",
            ),
            prompt(
                "family", "Family expectations", "家族の期待",
                "How can family or social expectations influence decisions about marriage or children?",
                "家族や社会の期待は、結婚や子どもについての決定にどう影響しますか？",
                ("If your own family is relevant, how is the expectation expressed?", "If there is no family context or discussion to draw on, which wider social expectation matters?", "If personal details are private or the answer is general, which boundary keeps the discussion respectful?"),
                full="How do family and social expectations shape decisions about marriage or parenthood?",
                full_ja="家族や社会の期待は、結婚や親になることについての決定をどう左右しますか？",
                full_followups=("If your own family is relevant, how is the expectation communicated?", "If there is no family context or discussion to draw on, which broader social expectation carries weight?", "If personal details remain private or the case is general, which boundary should the conversation respect?"),
                safety="family-none-private-or-general",
            ),
            prompt(
                "choice", "With no pressure", "圧力がないなら",
                "With no pressure from anyone, what would matter most in making either decision?",
                "誰からの圧力もなければ、どちらの決定をするうえで何が最も大切ですか？",
                ("You can keep your own choice private; which principle would guide a fair decision?", "Which practical condition might still matter?"),
                full="Without social pressure, which values and conditions should guide decisions about marriage or children?",
                full_ja="社会的な圧力がなければ、結婚や子どもについての決定を、どんな価値観や条件が導くべきですか？",
                full_followups=("Your own choice may remain private; which principle supports an autonomous decision?", "Which material condition might still carry legitimate weight?"),
                safety="explicit-private-choice-opt-out",
            ),
            prompt(
                "distinction", "Two different decisions", "二つの別の決定",
                "Why is choosing marriage different from choosing to have children?",
                "結婚を選ぶことと、子どもを持つことを選ぶのは、なぜ違いますか？",
                ("Which responsibilities are different?", "Why do people sometimes treat the choices as one?"),
                full="Why should marriage and parenthood be discussed as distinct decisions?",
                full_ja="結婚と親になることを、なぜ別々の決定として話す必要がありますか？",
                full_followups=("Which commitments and consequences differ?", "What social expectation tends to merge the two?"),
                safety="neutral-comparison",
            ),
            prompt(
                "flip", "Responding with respect", "敬意のある応じ方",
                "How can people respond respectfully to decisions about marriage or children?",
                "結婚や子どもについての決定に、どうすれば敬意を持って応じられますか？",
                ("For a settled choice, how should a response work whether it matches yours or differs?", "For an undecided or private choice, what should nobody demand?", "In a general discussion, which comment keeps the conversation neutral?"),
                full="What makes a response to decisions about marriage or parenthood genuinely respectful?",
                full_ja="結婚や親になることについての決定に対して、真に敬意ある応答とはどのようなものですか？",
                full_followups=("For a settled choice, how should the response work whether it aligns with yours or diverges?", "For an unresolved or private choice, which explanation should nobody demand?", "In a general discussion, which wording preserves neutrality?"),
                safety="neutral-respectful-close",
            ),
        ],
    ),
}

# Reviewed conversation source. Every main question is standalone because the
# tutor may skip freely through the pool. Safety comes from opinion and scenario
# questions, not from branching instructions that make the learner choose a
# personal, fictional, or hypothetical route before answering.
REVIEWED_PROMPTS = {
    57: (
        ("What's something small that makes you like someone?", "どんな小さなことで、人を好きになりますか？", ("When is it easiest to notice?", "Why does it appeal to you?"), "Which small gesture or quality can make someone especially appealing to you?", "どんな小さな行動や特徴に、特に魅力を感じますか？", ("In which setting does it stand out?", "Which value might explain its appeal?")),
        ("What can a small gesture reveal about a person—and what can it not prove?", "小さな行動から、その人の何が分かり、何は断定できないと思いますか？", ("Which quality might it suggest?", "Why can first impressions be misleading?"), "What might an understated gesture suggest about someone's character, without proving it?", "さりげない行動は、人柄について何を示唆しても、証明まではできないと思いますか？", ("Which trait could it indicate?", "What other evidence would you want before judging?")),
        ("Would you tell someone about a small quality you find attractive?", "魅力的だと感じる小さな特徴を、本人に伝えますか？", ("What would make the compliment feel sincere?", "What might make the moment awkward?"), "Would you name an understated quality you find attractive to the person who has it?", "その人のさりげない特徴に魅力を感じると、本人に伝えますか？", ("What would make the compliment feel genuine?", "Which context could make it uncomfortable?")),
        ("When is someone's kindness easiest to notice?", "その人の優しさに気づきやすいのは、どんなときですか？", ("What might the person do?", "Who benefits from the kindness?"), "Which ordinary situation reveals genuine consideration most clearly?", "本当の思いやりが最もはっきり現れるのは、どんな日常の場面ですか？", ("Which action would make it visible?", "Why would that moment carry weight?")),
        ("Which matters more at first: someone's appearance or their everyday habits?", "最初は、見た目と日常の習慣のどちらがより重要ですか？", ("Can your answer change over time?", "Which habit could outweigh appearance?"), "At the beginning of an attraction, how do appearance and ordinary behaviour compete for attention?", "人にひかれ始めるとき、見た目と日常の行動はどう影響し合いますか？", ("Which tends to matter first?", "Which behaviour could overturn the first impression?")),
        ("What can make a charming habit become annoying?", "魅力的な癖が、気になる癖に変わるのはどんなときですか？", ("Does intention matter?", "Which change in context matters most?"), "What can make an endearing habit lose its charm?", "愛らしい癖が魅力を失うのは、どんなときですか？", ("How much does intention affect the meaning?", "Which context could reverse your judgment?")),
        ("How have the small qualities you value in people changed over time?", "人の中で大切に感じる小さな特徴は、時間とともにどう変わりましたか？", ("What matters more now?", "Which preference has stayed steady?"), "How have age and experience changed which understated qualities you value?", "年齢や経験によって、大切に感じるさりげない特徴はどう変わりましたか？", ("Which quality carries more weight now?", "Which preference has remained stable?")),
        ("What small quality would you be happy for someone to notice in you?", "自分のどんな小さな特徴に気づいてもらえたら、うれしいですか？", ("How does it appear in everyday life?", "Would you want the person to mention it?"), "Which understated quality would you be glad to have someone notice in you?", "自分のどんなさりげない特徴に気づいてもらえたら、うれしいですか？", ("How would it become visible naturally?", "Would naming it improve the moment or make it awkward?")),
    ),
    58: (
        ("Which is harder to forgive: a lie, an insult, or a broken promise?", "うそ、侮辱、破られた約束の中で、最も許しにくいのはどれですか？", ("Why does that one hurt trust most?", "Could a sincere apology change your answer?"), "Which does more damage to trust: a lie, a cruel comment, or a broken promise?", "うそ、ひどい発言、破られた約束の中で、信頼を最も傷つけるのはどれですか？", ("Why does that one carry the most weight?", "Could the context change your answer?")),
        ("Can one comment end a relationship, or does a repeated pattern matter more?", "一度の発言で関係が終わることはありますか。それとも、繰り返される行動のほうが重要ですか？", ("What kind of comment could be a deal-breaker?", "When should someone look at the larger pattern?"), "Can one terrible comment be a deal-breaker, or does a repeated pattern matter more?", "一度のひどい発言が関係を終わらせる決定打になりますか。それとも、繰り返される行動のほうが重要ですか？", ("What could make one comment impossible to ignore?", "When does a pattern become clearer than a single moment?")),
        ("What makes an apology feel sincere?", "謝罪が心からのものだと感じられるのは、どんなときですか？", ("What words help?", "What action should follow?"), "What makes an apology feel genuine?", "謝罪が本心からのものだと感じられるのは、どんなときですか？", ("How much do the exact words matter?", "What change would need to follow?")),
        ("When is it better to pause an argument and talk later?", "口論をいったん止めて、後で話すほうがよいのはどんなときですか？", ("What can a short break prevent?", "How can someone promise to return to the conversation?"), "When is taking a break from an argument healthier than continuing it?", "口論を続けるより、いったん離れるほうが健全なのはどんなときですか？", ("What signs show that the conversation is no longer useful?", "How can the break avoid feeling like punishment?")),
        ("What should nobody use against a partner in an argument?", "口論の中でも、パートナーに対して持ち出すべきでないことは何ですか？", ("Why should it stay off-limits?", "How could the real concern be said more safely?"), "What should never be used as a weapon in an argument?", "口論の中で、決して攻撃の材料にしてはいけないことは何ですか？", ("Why would using it cause lasting harm?", "How could the same concern be raised fairly?")),
        ("What would someone need to do to rebuild trust after crossing a serious line?", "重大な一線を越えた後、信頼を取り戻すには何をする必要がありますか？", ("What should happen first?", "How long can rebuilding trust take?"), "What would real repair look like after someone crosses a serious line?", "重大な一線を越えた後、本当の関係修復とはどのようなものですか？", ("Which action would matter more than another promise?", "How would both people know that trust is returning?")),
        ("How can someone say “That's not okay” without making the fight worse?", "けんかを悪化させずに、「それは受け入れられない」とどう伝えられますか？", ("What words sound clear but calm?", "When is the best time to say it?"), "How can someone set a firm boundary without making a threat?", "脅しにせず、はっきりと境界線を示すにはどうすればよいですか？", ("What wording keeps the focus on the boundary?", "Which choice should the other person still have?")),
        ("What's one green flag that makes a relationship feel safe?", "人間関係に安心を感じさせるよいサインを一つ挙げるとしたら何ですか？", ("How does it show up in everyday life?", "What makes it especially valuable?"), "What's one green flag that tells you a relationship is safe?", "人間関係が安心できると分かるよいサインを一つ挙げるとしたら何ですか？", ("Which everyday action makes the sign visible?", "How does it help both people handle conflict?")),
    ),
    59: (
        ("What's one thing you could never compromise on in a partner?", "パートナーについて、絶対に妥協できないことは何ですか？", ("Which value does it protect?", "What behaviour would cross the line?"), "Which single quality or behaviour would be non-negotiable in a partner?", "パートナーのどの特徴や行動は、絶対に譲れませんか？", ("Which value underlies that boundary?", "What observable behaviour would violate it?")),
        ("Why do some preferences become non-negotiable?", "なぜ、ある好みは絶対に譲れない条件になるのでしょうか？", ("Which need can a boundary protect?", "Can the same value appear in different ways?"), "What gives one preference enough weight to become a non-negotiable?", "一つの好みが絶対に譲れない条件になるほどの重みは、どこから生まれますか？", ("What real need does it protect?", "Could the same value be shown differently?")),
        ("Which partner preference is usually safe to be flexible about?", "パートナーに求める条件の中で、柔軟に考えやすいのは何ですか？", ("Why is it less important?", "Where should flexibility stop?"), "Which preference can usually be negotiated without sacrificing a central value?", "中心的な価値観を犠牲にせず、通常は調整できる好みは何ですか？", ("What makes it genuinely flexible?", "At which point would accommodation become too costly?")),
        ("Which qualities in a partner matter more with age?", "年齢を重ねると、パートナーのどんな特徴がより重要になると思いますか？", ("Which quality may matter less?", "What could cause the change?"), "How might age and experience reorder the qualities someone values in a partner?", "年齢や経験は、パートナーに求める特徴の優先順位をどう変えると思いますか？", ("Which criterion might gain weight?", "Which ideal could become less important?")),
        ("Why are some reasonable boundaries called unrealistic?", "なぜ、理にかなった境界線でも現実的でないと言われることがあるのでしょうか？", ("What social pressure affects that judgment?", "Who gets to decide what is reasonable?"), "Why can a legitimate relationship boundary be dismissed as unrealistic?", "なぜ、正当な関係の境界線が現実的でないと退けられることがあるのでしょうか？", ("Which social expectation distorts the judgment?", "Whose interests does the criticism serve?")),
        ("When is it healthy to reconsider a relationship boundary?", "どんなときに、関係の境界線を見直すのが健全ですか？", ("What new evidence should matter?", "Which value should remain protected?"), "What evidence justifies reassessing a boundary without abandoning its purpose?", "境界線の目的を捨てずに見直すには、どんな根拠が必要ですか？", ("Would consequences or another perspective matter more?", "Which core value still needs protection?")),
        ("What should two people do when their reasonable boundaries do not fit together?", "二人の合理的な境界線が合わないとき、どうすべきですか？", ("Which differences allow compromise?", "When is accepting that the two people are a poor fit more honest?"), "How should two people respond when their defensible non-negotiables are incompatible?", "二人の正当な譲れない条件が両立しないとき、どう対応すべきですか？", ("Which differences might still allow negotiation?", "When is admitting that the two people are a poor fit more honest?")),
        ("How can someone state a non-negotiable without controlling another person?", "相手をコントロールせずに、譲れない条件をどう伝えられますか？", ("What wording makes it a personal boundary?", "Which choice must the other person keep?"), "How can a non-negotiable be expressed as a personal boundary rather than a demand?", "譲れない条件を、要求ではなく自分の境界線としてどう表現できますか？", ("Which wording shows ownership of the boundary?", "Which choice must remain with the other person?")),
    ),
    60: (
        ("Which relationship habit do you think is hardest to change?", "人間関係の癖の中で、最も変えにくいのは何だと思いますか？", ("What usually triggers it?", "Why does it continue?"), "Which unhelpful relationship pattern is usually hardest to change?", "役に立たない関係のパターンの中で、通常最も変えにくいのは何ですか？", ("Which trigger tends to activate it?", "What continues to reinforce it?")),
        ("When do people usually notice a bad relationship habit in themselves?", "人は普通、いつ自分のよくない関係の癖に気づきますか？", ("What evidence makes it clear?", "Why can it be hard to see?"), "Which situation most often exposes an unhelpful relationship pattern to the person who has it?", "役に立たない関係のパターンに本人が気づくのは、どんな状況が多いですか？", ("Which consequence makes the pattern visible?", "Why might the person notice it late?")),
        ("How can someone point out a relationship habit without starting a fight?", "口論を始めずに、相手の関係の癖をどう指摘できますか？", ("What wording keeps it specific?", "When is the best time to talk?"), "How can feedback about a relationship pattern remain specific without becoming an attack?", "関係のパターンについての指摘を、攻撃にせず具体的に伝えるにはどうすればよいですか？", ("Which observation would keep it concrete?", "Which timing would help the person feel less attacked?")),
        ("What small change can make a bad relationship habit easier to manage?", "よくない関係の癖を管理しやすくする小さな変化は何ですか？", ("What could replace the old response?", "How could progress be noticed?"), "Which small replacement behaviour can make an unhelpful pattern easier to change?", "役に立たないパターンを変えやすくする小さな代替行動は何ですか？", ("Which trigger would cue the new response?", "What evidence would show progress?")),
        ("Which relationship habit is especially difficult to live with?", "一緒に過ごす上で、特に受け入れにくい関係の癖は何ですか？", ("What effect does it have?", "Can the person be unaware of it?"), "Which relationship pattern in another person is particularly difficult to tolerate?", "相手のどのような関係のパターンが、特に受け入れにくいですか？", ("Which impact makes it difficult?", "How might the person remain unaware of it?")),
        ("When does explaining a bad habit become an excuse?", "よくない癖の説明が、言い訳になるのはどんなときですか？", ("What responsibility should remain?", "Which effort makes the explanation more honest?"), "Where is the line between honestly disclosing a pattern and using it to avoid responsibility?", "パターンを正直に説明することと、責任を避けるために使うことの境界はどこですか？", ("Which responsibility must remain?", "What concrete effort should accompany the disclosure?")),
        ("What can someone do instead of shutting down during conflict?", "対立中に心を閉ざす代わりに、何ができますか？", ("What makes the new response difficult?", "Which support could help?"), "Which replacement behaviour could interrupt the habit of shutting down during conflict?", "対立中に心を閉ざす癖を中断する代替行動は何ですか？", ("Which obstacle could block the response under stress?", "What support could make the new response last?")),
        ("Which healthy relationship habit deserves more attention?", "どの健全な関係の習慣が、もっと注目されるべきですか？", ("How does it help both people?", "Why is it easy to overlook?"), "Which healthy relationship pattern is most undervalued?", "どの健全な関係のパターンが、最も過小評価されていますか？", ("How does it support both people?", "Why can it be difficult to recognize?")),
    ),
    61: (
        ("If you had a wedding tomorrow, what's the one thing you'd insist on?", "もし明日結婚式をするなら、絶対に入れたいことは何ですか？", ("What feeling should it create?", "Who else would it matter to?"), "If you were holding a wedding tomorrow, which single element would be essential?", "もし明日結婚式を開くなら、どの一つの要素が必須ですか？", ("Which value would it express?", "Who else might share its meaning?")),
        ("Which wedding tradition is worth keeping?", "どの結婚式の習慣は残す価値がありますか？", ("What does it mean?", "How could it be updated?"), "Which wedding tradition deserves to be preserved, adapted, or reinvented?", "どの結婚式の伝統は、保存、応用、または作り直す価値がありますか？", ("Which value does it express?", "How could it fit the people involved?")),
        ("Which common wedding tradition would you remove?", "よくある結婚式の習慣の中で、どれをなくしたいですか？", ("What problem would that solve?", "Who might miss it?"), "Which conventional wedding element creates more pressure than meaning?", "どの一般的な結婚式の要素が、意味よりもプレッシャーを生みやすいですか？", ("Which cost or distraction would removal reduce?", "Whose expectation might be challenged?")),
        ("Who should have the strongest voice in wedding decisions?", "結婚式の決定で、誰の意見を最も強く反映すべきですか？", ("Which choices can involve family?", "Which choices belong to the couple?"), "How should decision-making power be shared among a couple and their families?", "結婚式の決定権は、二人と家族の間でどう分けるべきですか？", ("Which decision could legitimately involve family?", "Which choice should remain private to the couple?")),
        ("What makes a wedding detail memorable?", "結婚式の一つの演出が心に残るのは、どんなときですか？", ("Does it need to be expensive?", "Could it work at a small wedding?"), "Which qualities make one wedding detail genuinely memorable?", "結婚式の一つの演出を本当に心に残るものにするのは、どんな特徴ですか？", ("How much does cost matter?", "Would its meaning survive in a smaller event?")),
        ("What part of weddings creates the most unnecessary stress?", "結婚式のどの部分が、最も不必要なストレスを生みますか？", ("Who usually carries the stress?", "What simple change could reduce it?"), "Which aspect of wedding culture produces the most avoidable pressure?", "結婚式の文化のどの側面が、最も避けられるプレッシャーを生みますか？", ("Who tends to absorb that pressure?", "Which structural change could reduce it?")),
        ("Could a tiny ceremony feel more meaningful than a large wedding?", "ごく小さな式のほうが、大きな結婚式より意味深く感じられることはありますか？", ("What would the smaller event protect?", "What might be lost?"), "Can a private ceremony feel more authentic than a large public celebration?", "私的な式のほうが、大規模な公の祝いより自分らしく感じられますか？", ("Which value would the smaller event protect?", "Which social element might be lost?")),
        ("What should a wedding be for?", "結婚式は何のためにあるべきですか？", ("Who should feel represented?", "Which choice would show that purpose?"), "What central purpose should guide a wedding for people who choose to hold one?", "結婚式を開く人たちにとって、どんな中心的な目的が式を導くべきですか？", ("Whose identities should the event represent?", "Which design choice would express the purpose?")),
    ),
    62: (
        ("Why can some breakups be so hard to get over?", "なぜ、立ち直るのがとても難しい別れがあるのでしょうか？", ("What is lost besides the relationship?", "Which part can take longest to accept?"), "Why can some breakups be particularly hard to get over?", "なぜ、立ち直るのが特に難しい別れがあるのでしょうか？", ("Which losses extend beyond the relationship itself?", "What can make acceptance take longer?")),
        ("What changes most after a relationship ends?", "人間関係が終わった後、最も大きく変わるのは何ですか？", ("Which daily routine changes first?", "Which future plan is hardest to replace?"), "Which immediate change after a breakup tends to feel most disruptive?", "別れの後、どのような即時の変化が最も生活を乱しやすいですか？", ("Which routine disappears first?", "Which everyday effect is often overlooked?")),
        ("What affects how long it takes to recover from a breakup?", "別れから立ち直るまでの時間には、何が影響しますか？", ("Does the length of the relationship matter?", "Which sign shows progress?"), "Which factors shape the pace of recovery after a relationship ends?", "関係が終わった後、回復の速さを左右するのはどんな要因ですか？", ("How much does the nature of the ending matter?", "Which sign indicates genuine progress?")),
        ("When is privacy helpful after a breakup, and when is support better?", "別れの後、一人でいることが役立つのはいつで、人の支えがよりよいのはいつですか？", ("What can solitude provide?", "What kind of support feels useful?"), "How should someone balance privacy and social support after a breakup?", "別れの後、プライバシーと周りの支えをどうバランスすべきですか？", ("Which purpose can solitude serve?", "Which form of support tends to be constructive?")),
        ("What genuinely helps someone begin to get over a breakup?", "別れから立ち直り始めるために、本当に役立つのは何ですか？", ("Is the help emotional or practical?", "Which common advice does not help?"), "What helps someone begin recovering from a difficult breakup in a meaningful way?", "難しい別れから本当の意味で回復し始めるには、何が役立ちますか？", ("Is useful support mainly emotional or practical?", "Which familiar response can make recovery harder?")),
        ("What can people understand about a breakup only later?", "別れについて、後になって初めて分かることは何ですか？", ("Which pattern becomes clearer?", "Can hindsight be unfair?"), "Which truth about a breakup may become visible only after enough distance?", "別れから十分に距離を置いて初めて見える事実は何ですか？", ("Which relationship pattern might emerge?", "How can hindsight avoid assigning all blame to one person?")),
        ("What advice sounds kind after a breakup but is not actually helpful?", "別れの後、優しく聞こえても実際には役に立たない助言は何ですか？", ("Why can it feel dismissive?", "What could someone say instead?"), "Which well-meant response to a breakup can feel dismissive rather than supportive?", "善意からの別れへの反応の中で、支えより軽視と感じられるのは何ですか？", ("Which assumption makes it unhelpful?", "What wording would show patience?")),
        ("What is one sign that someone is moving forward without erasing the past?", "過去を消さずに前に進んでいることを示すサインは何ですか？", ("Is the sign emotional or practical?", "What might still remain difficult?"), "Which sign shows that recovery is underway without pretending the relationship was meaningless?", "その関係に意味がなかったふりをせずに、回復が進んでいると示すサインは何ですか？", ("Would the clearest evidence be emotional or practical?", "Which difficulty could reasonably remain?")),
    ),
    63: (
        ("Why might someone choose not to marry or have children?", "なぜ、結婚しない、または子どもを持たないと選ぶ人がいるのでしょうか？", ("Which reasons are often overlooked?", "Are marriage and children separate decisions?"), "Which values or circumstances can lead someone to choose neither marriage nor parenthood?", "どのような価値観や状況が、結婚も親になることも選ばない決定につながるのでしょうか？", ("Which reasons are commonly overlooked?", "Why should the two decisions remain distinct?")),
        ("Should anyone have to explain a choice not to marry or have children?", "結婚しない、または子どもを持たない選択を、誰かに説明する必要があるでしょうか？", ("Which questions feel too personal?", "When can curiosity be respectful?"), "Does anyone owe other people an explanation for choosing not to marry or become a parent?", "結婚しない、または親にならない選択について、他人に説明する義務はあるでしょうか？", ("Which details should remain private?", "What makes a question respectful rather than intrusive?")),
        ("What do people often say to someone who makes that choice?", "その選択をした人に、周りはよく何と言いますか？", ("Which comment sounds caring but feels like pressure?", "What would a neutral response sound like?"), "How do people commonly respond to someone who rejects marriage or parenthood?", "結婚や親になることを選ばない人に、周りは通常どう反応しますか？", ("Which response may disguise pressure as concern?", "What would curiosity without advocacy sound like?")),
        ("Why do views on marriage and children change over time?", "結婚や子どもについての考えが、時間とともに変わるのはなぜでしょうか？", ("Which life change can matter?", "Can uncertainty be a valid position?"), "Which experiences or conditions can reshape a person's view of marriage and parenthood?", "どのような経験や条件が、結婚や親になることへの考えを変えるのでしょうか？", ("Which material condition might carry weight?", "Why can uncertainty remain reasonable?")),
        ("How do family expectations affect decisions about marriage or children?", "家族の期待は、結婚や子どもについての決定にどう影響しますか？", ("How is pressure communicated?", "Which boundary keeps the discussion respectful?"), "How can family and social expectations shape decisions about marriage or parenthood?", "家族や社会の期待は、結婚や親になることへの決定をどう形作りますか？", ("Which messages carry the most pressure?", "Which boundary should the conversation respect?")),
        ("Without social pressure, what should matter most in either decision?", "社会的なプレッシャーがなければ、どちらの決定で最も重要なのは何ですか？", ("Which value should guide the choice?", "Which practical condition still matters?"), "Without social pressure, which values and conditions should guide decisions about marriage or parenthood?", "社会的なプレッシャーがなければ、どの価値観や条件が結婚や親になる決定を導くべきですか？", ("Which principle protects a person's freedom to choose?", "Which material condition carries legitimate weight?")),
        ("Why is choosing marriage different from choosing to have children?", "なぜ、結婚を選ぶことと子どもを持つことは異なる決定なのでしょうか？", ("Which responsibilities differ?", "Why are the choices often treated as one?"), "Why should marriage and parenthood be treated as separate life decisions?", "なぜ、結婚と親になることは別々の人生の決定として扱うべきですか？", ("Which commitments and consequences differ?", "Which expectation tends to merge the two?")),
        ("How can people respond respectfully to decisions about marriage or children?", "結婚や子どもについての決定に、どうすれば敬意を持って応じられますか？", ("What should nobody demand?", "Which comment keeps the conversation open?"), "What makes a response to decisions about marriage or parenthood genuinely respectful?", "結婚や親になることについての決定への、本当に敬意ある反応とは何ですか？", ("Which explanation should nobody demand?", "Which wording preserves neutrality?")),
    ),
}

for _topic_no, _rows in REVIEWED_PROMPTS.items():
    for _item, (_a, _a_ja, _a_followups, _f, _f_ja, _f_followups) in zip(
        TOPICS[_topic_no]["prompts"], _rows, strict=True
    ):
        _item.update(
            accessible=_a,
            accessible_ja=_a_ja,
            accessible_followups=_a_followups,
            full=_f,
            full_ja=_f_ja,
            full_followups=_f_followups,
            safety="standalone-opinion-or-scenario",
        )


# FT58 is the approved calibration and stays exact. In the other pairs, Full
# deepens the angle without replacing ordinary spoken English with essay terms.
_PLAIN_FULL_PHRASES = (
    ("understated", "small"),
    ("trait could it indicate", "quality could it show"),
    ("carry weight", "matter"),
    ("compete for attention", "shape the first impression"),
    ("reorder the qualities", "change the qualities"),
    ("non-negotiable", "deal-breaker"),
    ("underlies that boundary", "is behind that boundary"),
    ("observable behaviour", "real behaviour"),
    ("negotiated without sacrificing a central value", "flexible without giving up something important"),
    ("accommodation become too costly", "flexibility go too far"),
    ("legitimate relationship boundary be dismissed", "reasonable relationship boundary be called"),
    ("reassessing a boundary", "reconsidering a boundary"),
    ("defensible", "reasonable"),
    ("incompatible", "a poor fit"),
    ("unhelpful relationship pattern", "bad relationship habit"),
    ("exposes", "reveals"),
    ("replacement behaviour", "new habit"),
    ("disclosing a pattern", "explaining a habit"),
    ("avoid responsibility", "escape responsibility"),
    ("interrupt the habit", "replace the habit"),
    ("undervalued", "not appreciated enough"),
    ("single element", "one thing"),
    ("deserves to be preserved, adapted, or reinvented", "is worth keeping or changing"),
    ("conventional wedding element", "common wedding tradition"),
    ("decision-making power be shared", "wedding decisions be shared"),
    ("produces the most avoidable pressure", "creates the most unnecessary pressure"),
    ("authentic", "meaningful"),
    ("central purpose should guide", "main purpose should shape"),
    ("particularly", "especially"),
    ("disruptive", "difficult"),
    ("shape the pace of recovery", "affect how quickly someone recovers"),
    ("balance privacy and social support", "choose between privacy and support"),
    ("in a meaningful way", "for real"),
    ("dismissive", "uncaring"),
    ("recovery is underway", "someone is moving forward"),
    ("circumstances can lead", "reasons can lead"),
    ("owe other people an explanation", "have to explain"),
    ("rejects marriage or parenthood", "chooses not to marry or have children"),
    ("reshape", "change"),
    ("distinct decisions", "separate decisions"),
    ("genuinely respectful", "truly respectful"),
)


def _plain_full(value: str) -> str:
    for _old, _new in _PLAIN_FULL_PHRASES:
        value = value.replace(_old, _new)
    return value


for _topic_no, _topic in TOPICS.items():
    if _topic_no == 58:
        continue
    for _item in _topic["prompts"]:
        _item["full"] = _plain_full(_item["full"])
        _item["full_followups"] = tuple(_plain_full(_probe) for _probe in _item["full_followups"])

_STANDALONE_REVISIONS = {
    (57, 2): ("What can a small kind gesture show about someone—and what can it not prove?", "小さな親切から、その人の何が分かり、何は断定できないと思いますか？", "What can a small kind gesture show about a person without proving it?", "小さな親切は、人柄について何を示しても、証明まではできないと思いますか？"),
    (59, 6): ("What could make someone rethink a relationship deal-breaker?", "人間関係で絶対に譲れない条件を、考え直すきっかけは何ですか？", "What kind of experience could make a reasonable relationship boundary change?", "人間関係での妥当な境界線を変えるのは、どんな経験ですか？"),
    (60, 2): ("When do people notice a bad relationship habit in themselves?", "人はいつ、自分の人間関係でのよくない習慣に気づきますか？", "Which situation makes a bad relationship habit hardest to ignore?", "人間関係でのよくない習慣が、最も無視できなくなるのはどんな状況ですか？"),
    (62, 8): ("What's one sign that someone is moving forward after a breakup?", "別れのあと、前に進んでいると分かるサインは何ですか？", "Which sign shows that someone is moving forward without pretending the relationship meant nothing?", "その関係に意味がなかったふりをせず、前に進んでいると分かるサインは何ですか？"),
    (63, 3): ("What do people often say when someone chooses not to marry or have children?", "結婚や子どもを持たない選択をした人に、周りはよく何と言いますか？", "How do people commonly respond when someone chooses not to marry or have children?", "結婚や子どもを持たない選択に対して、周りは一般にどう反応しますか？"),
}
for (_topic_no, _prompt_no), (_a, _a_ja, _f, _f_ja) in _STANDALONE_REVISIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible=_a, accessible_ja=_a_ja, full=_f, full_ja=_f_ja
    )

_FINAL_FULL_QUESTIONS = {
    (57, 3): "Would you tell someone about a small quality you find attractive?",
    (57, 4): "What ordinary situation shows someone's kindness most clearly?",
    (57, 5): "When you first like someone, which matters more: appearance or everyday behaviour?",
    (59, 1): "Which quality or behaviour would be a deal-breaker in a partner?",
    (59, 2): "Why do some preferences become relationship deal-breakers?",
    (59, 3): "Which preference can stay flexible without giving up something important?",
    (59, 5): "Why are some reasonable relationship boundaries called unrealistic?",
    (59, 7): "What should two people do when their reasonable deal-breakers do not fit together?",
    (59, 8): "How can someone state a deal-breaker as a boundary instead of a demand?",
    (60, 3): "How can someone point out a relationship habit without making it sound like an attack?",
    (60, 4): "What small new habit can make a bad relationship pattern easier to change?",
    (60, 5): "Which relationship habit is especially hard to live with?",
    (60, 6): "When does explaining a bad habit become an excuse?",
    (60, 7): "What can someone do instead of shutting down during an argument?",
    (60, 8): "Which healthy relationship habit deserves more attention?",
    (61, 1): "If you had a wedding tomorrow, what one thing would have to be there?",
    (61, 2): "Which wedding tradition is worth keeping, changing, or dropping?",
    (61, 3): "Which common wedding tradition creates more pressure than meaning?",
    (61, 4): "How should a couple and their families share wedding decisions?",
    (61, 5): "What makes one wedding detail truly memorable?",
    (61, 6): "What part of wedding culture creates the most unnecessary stress?",
    (61, 8): "What should be the main purpose of a wedding?",
    (62, 2): "What change after a breakup can be hardest to get used to?",
    (62, 3): "What affects how quickly someone recovers after a breakup?",
    (62, 4): "When is privacy helpful after a breakup, and when is support better?",
    (62, 5): "What genuinely helps someone start recovering after a breakup?",
    (62, 6): "What can someone understand about a breakup only much later?",
    (62, 7): "What kind-sounding breakup advice can actually feel uncaring?",
    (63, 1): "Why might someone choose not to marry or become a parent?",
    (63, 2): "Should anyone have to explain a choice not to marry or have children?",
    (63, 4): "What can change someone's views on marriage or children over time?",
    (63, 5): "How can family expectations affect decisions about marriage or children?",
    (63, 6): "Without outside pressure, what should matter most in either decision?",
    (63, 7): "Why should marriage and having children be treated as separate decisions?",
    (63, 8): "What does a truly respectful response to either decision sound like?",
}
for (_topic_no, _prompt_no), _question in _FINAL_FULL_QUESTIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1]["full"] = _question

_CONCRETE_MAIN_QUESTIONS = {
    (57, 4): ("Where is kindness easiest to notice: at home, at work, or with strangers?", "Which ordinary situation reveals genuine kindness most clearly?"),
    (57, 5): ("Which matters more at first: appearance or everyday behaviour?", "Which can change a first attraction more: appearance or everyday behaviour?"),
    (59, 3): ("Which partner preference is usually safe to be flexible about?", "Which partner preference can stay flexible without giving up an important value?"),
    (59, 7): ("What should two people do when their important boundaries do not fit together?", "When two reasonable deal-breakers clash, is compromise possible—or is leaving fairer?"),
    (60, 4): ("What small habit could replace a bad reaction during an argument?", "What small replacement habit can interrupt a bad pattern during conflict?"),
    (60, 8): ("Which healthy habit helps relationships most: listening, checking in, or giving space?", "Which quiet relationship habit deserves much more attention?"),
    (62, 4): ("After a breakup, when is being alone helpful and when is company better?", "After a breakup, what is the right balance between privacy and support?"),
    (63, 2): ("Should people have to explain why they do not want marriage or children?", "Does anyone owe others an explanation for choosing not to marry or have children?"),
}
for (_topic_no, _prompt_no), (_accessible, _full) in _CONCRETE_MAIN_QUESTIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible=_accessible, full=_full
    )

_CONCRETE_JAPANESE = {
    (57, 4): ("優しさに最も気づきやすいのは、家、職場、知らない人との場面のどこですか？", "本当の優しさが最もはっきり現れる日常の場面は何ですか？"),
    (57, 5): ("最初は、見た目と日常の行動のどちらが大切ですか？", "最初の魅力をより変えるのは、見た目と日常の行動のどちらですか？"),
    (59, 3): ("パートナーに求める条件のうち、柔軟に考えやすいものは何ですか？", "大切な価値観を失わずに柔軟に考えられる条件は何ですか？"),
    (59, 7): ("大切な境界線が合わないとき、二人はどうすべきですか？", "妥当な譲れない条件がぶつかったとき、妥協は可能ですか。それとも別れるほうが公平ですか？"),
    (60, 4): ("口論中のよくない反応を、どんな小さな習慣に置き換えられますか？", "衝突中のよくないパターンを止める、小さな代わりの習慣は何ですか？"),
    (60, 8): ("人間関係に最も役立つのは、聞くこと、声をかけること、距離を与えることのどれですか？", "もっと注目されるべき、目立たない健全な習慣は何ですか？"),
    (62, 4): ("別れのあと、一人でいるほうがよいのはいつで、誰かといるほうがよいのはいつですか？", "別れのあと、プライバシーと支えをどのように両立させるとよいですか？"),
    (63, 2): ("結婚や子どもを望まない理由を、説明しなければならないと思いますか？", "結婚や子どもを持たない選択について、他人に説明する義務はありますか？"),
}
for (_topic_no, _prompt_no), (_accessible_ja, _full_ja) in _CONCRETE_JAPANESE.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible_ja=_accessible_ja, full_ja=_full_ja
    )

TOPICS[57]["prompts"][2]["full"] = "Would you tell someone about a small quality you quietly find attractive?"
TOPICS[60]["prompts"][5]["full"] = "When does an honest explanation of a bad habit turn into an excuse?"
TOPICS[60]["prompts"][7]["full"] = "Which healthy relationship habit is easiest to overlook?"
TOPICS[62]["prompts"][3]["full"] = "After a breakup, how should someone balance privacy and support?"
TOPICS[63]["prompts"][1]["full"] = "Does anyone owe an explanation for choosing not to marry or have children?"
TOPICS[63]["prompts"][5]["full"] = "Without social pressure, which personal value should matter most in either decision?"

_PLAIN_PROBE_REVISIONS = {
    "What other evidence would you want before judging?": "What else would you want to see before judging?",
    "Which context could make it uncomfortable?": "Which situation could make it uncomfortable?",
    "Which change in context matters most?": "Which change in the situation matters most?",
    "Which context could reverse your judgment?": "Which situation could reverse your judgment?",
    "What new evidence should matter?": "What new information should matter?",
    "Would consequences or another perspective matter more?": "Would the result or another person's view matter more?",
    "What evidence makes it clear?": "What makes the habit clear?",
    "What evidence would show progress?": "What would show that the habit is changing?",
    "What concrete effort should accompany the disclosure?": "What real effort should follow the explanation?",
    "Which structural change could reduce it?": "Which practical change could reduce it?",
    "Would the clearest evidence be emotional or practical?": "Would the clearest sign be emotional or practical?",
    "Which material condition might matter?": "Which practical condition might matter?",
    "Which practical condition still matters?": "Which practical issue still matters?",
    "Which material condition carries legitimate weight?": "Which practical issue deserves serious weight?",
}
for _topic_no, _topic in TOPICS.items():
    if _topic_no == 58:
        continue
    for _item in _topic["prompts"]:
        for _key in ("accessible_followups", "full_followups"):
            _item[_key] = tuple(_PLAIN_PROBE_REVISIONS.get(_probe, _probe) for _probe in _item[_key])


FT58_PAGE_TITLES = (
    ("A quick choice", "すぐに選ぶ"),
    ("One comment or a pattern", "一度の発言か繰り返しか"),
    ("A sincere apology", "心からの謝罪"),
    ("Take a break", "いったん休む"),
    ("Off-limits in an argument", "口論でも持ち出さないこと"),
    ("Rebuilding trust", "信頼を取り戻す"),
    ("Set a clear boundary", "はっきり境界線を示す"),
    ("One green flag", "よいサインを一つ"),
)
for _item, (_title, _title_ja) in zip(
    TOPICS[58]["prompts"], FT58_PAGE_TITLES, strict=True
):
    _item.update(title=_title, title_ja=_title_ja)


CLAIM_ORDER = {
    topic_no: tuple(f"ft{topic_no}-c{index:02d}" for index in range(1, 11))
    for topic_no in TOPIC_NUMBERS
}

# Exact checkpoint-9 owner proposal.  Later Core retrieval references above the
# FT entry floor are intentionally absent from `recycled` and listed in
# FUTURE_CORE_DEPENDENCIES instead.
VOCABULARY = {
    57: {
        "new": "small gesture|ささやかな行動",
        "recycled": "small|小さい|CORE-43",
        "assumed": "like|好意を持つ; person|人; notice|気づく; age|年齢; quality|特徴",
        "receptive": "thoughtful|思いやりのある; attraction|魅力; endearing|愛らしい",
    },
    58: {
        "new": "deal-breaker|どうしても受け入れられないこと",
        "recycled": "",
        "assumed": "relationship|関係; say|言う; words|言葉; meaning|意味; apology|謝罪; end|終わらせる",
        "receptive": "forgivable|許せる; contempt|軽蔑; accountability|責任を引き受けること",
    },
    59: {
        "new": "compromise on|〜について妥協する",
        "recycled": "",
        "assumed": "partner|パートナー; value|価値観; boundary|境界線; preference|好み; list|リスト",
        "receptive": "non-negotiable|譲れない; incompatible|両立しない; autonomy|自分で決める権利",
    },
    60: {
        "new": "shut down|心を閉ざす",
        "recycled": "too much|多すぎる|CORE-34",
        "assumed": "relationship|関係; habit|習慣; change|変える; partner|パートナー; notice|気づく",
        "receptive": "defensive|身構えた; trigger|きっかけ; replacement behaviour|代替行動",
    },
    61: {
        "new": "wedding tradition|結婚式の習慣",
        "recycled": "",
        "assumed": "wedding|結婚式; guest|招待客; family|家族; ceremony|式; cost|費用; music|音楽",
        "receptive": "symbolic|象徴的な; obligation|義務; authentic|自分らしい",
    },
    62: {
        "new": "get over|立ち直る",
        "recycled": "",
        "assumed": "breakup|別れ; time|時間; help|助け; memory|記憶; relationship|関係; private|私的な",
        "receptive": "closure|区切り; recovery|回復; solitude|一人の時間",
    },
    63: {
        "new": "social pressure|社会的な圧力",
        "recycled": "",
        "assumed": "marry|結婚する; marriage|結婚; children|子ども; family|家族; choice|選択; reason|理由",
        "receptive": "life path|生き方; parenthood|親になること; coercive|強制的な",
    },
}

GLOSSES = {
    57: {
        "accessible": {1: ("small gesture", "small gesture", "ささやかな行動"), 3: ("thoughtful", "thoughtful", "思いやりのある")},
        "full": {1: ("minor gesture", "minor gesture", "何気ない行動"), 3: ("attentiveness", "attentiveness", "注意深く気にかけること")},
    },
    58: {
        "accessible": {1: ("deal-breaker", "deal-breaker", "どうしても受け入れられないこと")},
        "full": {1: ("deal-breaker", "deal-breaker", "関係を続けられなくする決定的なこと"), 8: ("accountability", "accountability", "責任を引き受けること")},
    },
    59: {
        "accessible": {2: ("compromise on", "compromise on", "〜について妥協する")},
        "full": {8: ("incompatible", "incompatible", "両立しない")},
    },
    60: {
        "accessible": {5: ("defensive", "defensive", "身構えた")},
        "full": {6: ("replacement behaviour", "replacement behaviour", "代替行動")},
    },
    61: {
        "accessible": {4: ("wedding tradition", "wedding tradition", "結婚式の習慣")},
        "full": {2: ("symbolic", "symbolic", "象徴的な"), 4: ("obligation", "obligation", "義務")},
    },
    62: {
        "accessible": {1: ("get over", "get over", "立ち直る")},
        "full": {4: ("Closure", "closure", "気持ちの区切り"), 5: ("solitude", "solitude", "一人の時間")},
    },
    63: {
        "accessible": {5: ("social pressure", "social pressure", "社会的な圧力")},
        "full": {1: ("parenthood", "parenthood", "親になること"), 5: ("coercive", "coercive", "強制的な")},
    },
}


def _render_dependencies():
    """Import pilot-dependent renderer helpers only when rendering is requested."""
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415

    return base, new_lesson


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    _base, new_lesson = _render_dependencies()
    slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
    return (
        new_lesson.ENGLISH
        / "tracks/3-freetalking/courses"
        / f"{COURSE}-{variant}"
        / "lessons"
        / slug
        / "lesson.html"
    )


def _set_pending(head: str) -> str:
    marker = '<meta name="podo:proofread-status" content="complete">'
    head = re.sub(
        r'\n\s*<meta name="podo:proofread-status" content="(?:pending|complete)">',
        "",
        head,
        count=1,
    )
    return head.replace(
        '<meta name="podo:vocabulary-status"',
        marker + '\n  <meta name="podo:vocabulary-status"',
        1,
    )


def _article_page(topic_no: int, data: dict[str, object], variant: str, base) -> str:
    en_col, ja_col = (0, 2) if variant == "accessible" else (1, 3)
    rows = []
    for index, (article, claim_id) in enumerate(
        zip(data["articles"], CLAIM_ORDER[topic_no], strict=True), 1
    ):
        en_markup, words = base.marked_text(
            article[en_col], GLOSSES[topic_no][variant].get(index)
        )
        rows.append(
            '        <div class="sent" role="button" tabindex="0" '
            f'data-sync-option="s{index}" data-claim-id="{claim_id}">'
            f'<span class="s-line"><span class="s-ko">{en_markup}</span>'
            '<span class="s-mark" aria-hidden="true"></span></span>'
            f'<span class="s-open"><span class="s-ja">{base.esc(article[ja_col])}</span>'
            f'{words}</span></div>'
        )
    title, title_ja = data["article_title"]
    body = (
        '      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span>'
        '<span class="ja">記事について何か質問はありましたか？</span></p>\n'
        '      <div class="tutor-note">Answer the learner\'s questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>\n'
        '      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">\n'
        + "\n".join(rows)
        + "\n      </div>"
    )
    return base.page("article", title, title_ja, body)


def _question_page(page_id: str, number: str, item: dict[str, object], variant: str, base) -> str:
    followups = item[f"{variant}_followups"]
    lis = "".join(f"<li>{base.esc(value)}</li>" for value in followups)
    japanese = item[f"{variant}_ja"]
    if sum(item[variant].count(mark) for mark in ".!?") == 1:
        japanese = japanese.replace("。", "、")
    body = (
        f'      <p class="section-subtitle ask"><span class="q-n">{number}</span>'
        f'<span class="ko">{base.esc(item[variant])}</span>'
        f'<span class="ja">{base.esc(japanese)}</span></p>\n'
        '      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span>'
        f'<ul class="tn-more">{lis}</ul></div></div>\n'
        f'      <div class="fb" data-fb="{variant}-{page_id}" data-fb-spoken-label="Student\'s sentence"></div>'
        '<div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button>'
        '<button class="fb-add" data-add="note" type="button">＋ Note</button></div>'
    )
    return base.page(page_id, item["title"], item["title_ja"], body)


_FINAL_CONVERSATION_PATCHES = {
    (57, 2): {
        "full": "What can a small kind gesture suggest about a person?",
        "full_ja": "小さな親切から、その人のどんな人柄が感じられますか？",
    },
    (59, 4): {
        "full_followups": ("Which quality might become more important?", "Which ideal might matter less?"),
    },
    (59, 5): {
        "full_followups": ("Does social pressure make the choice harder to judge?", "Who benefits from the criticism?"),
    },
    (59, 7): {
        "accessible_followups": ("Which differences allow compromise?", "When is accepting that the two people are a poor fit more honest?"),
        "full_followups": ("Which differences might still allow negotiation?", "When is admitting that the two people are a poor fit more honest?"),
    },
    (60, 1): {
        "title": "A hard habit to change",
        "title_ja": "変えにくい癖",
        "full": "Which relationship habit is usually hardest to change?",
        "full_ja": "人間関係の癖の中で、普通いちばん変えにくいものは何ですか？",
        "full_followups": ("What usually brings the habit out?", "Why can it be hard to change?"),
    },
    (60, 2): {
        "title": "When people notice it",
        "title_ja": "癖に気づくとき",
        "full": "When do people usually notice a bad relationship habit in themselves?",
        "full_ja": "人は普通、いつ自分のよくない関係の癖に気づきますか？",
        "full_followups": ("What result makes the habit clear?", "Why can it be hard to notice?"),
    },
    (60, 3): {
        "full": "How can someone raise a relationship habit without turning it into a fight?",
        "full_ja": "関係の癖を、口論にせずどう話題にできますか？",
        "full_followups": ("What exact behaviour should they mention?", "When would the conversation go best?"),
    },
    (60, 4): {
        "title": "Changing the reaction",
        "title_ja": "反応を変える",
        "full": "What could someone do instead of reacting badly during an argument?",
        "full_ja": "口論中によくない反応をする代わりに、何ができますか？",
        "full_followups": ("What sign tells them to use the new response?", "What makes the change hard in the moment?"),
    },
    (60, 5): {
        "full": "Which relationship habit is hardest to live with, and why?",
        "full_ja": "一緒に過ごす上でいちばん受け入れにくい人間関係の癖と、その理由は何ですか？",
        "full_followups": ("What effect can it have on the other person?", "Can someone have the habit without noticing it?"),
    },
    (60, 6): {
        "title": "Explanation or excuse",
        "title_ja": "説明か言い訳か",
        "full": "When does explaining a bad relationship habit start to sound like an excuse?",
        "full_ja": "人間関係のよくない癖を説明することが、言い訳に聞こえ始めるのはどんなときですか？",
        "full_followups": ("What responsibility should the person still accept?", "What effort would make the explanation more honest?"),
    },
    (60, 7): {
        "full": "What response could replace shutting down during conflict?",
        "full_ja": "対立中に心を閉ざす反応を、何に置き換えられますか？",
        "full_followups": ("What could make the new response hard?", "What support could make the new response last?"),
    },
    (60, 8): {
        "full": "Which healthy relationship habit matters most but often goes unnoticed?",
        "full_ja": "大切なのに気づかれにくい、人間関係のよい癖は何ですか？",
        "full_followups": ("How does the habit help both people?", "Why might people fail to notice it?"),
    },
    (61, 2): {
        "full_ja": "結婚式の習慣の中で、残したいもの、変えたいもの、なくしたいものは何ですか？",
    },
    (61, 1): {
        "full_followups": ("What would that element actually look or sound like?", "Who else might share its meaning?"),
    },
    (61, 7): {
        "full_ja": "プライベートな式は、大規模な公の祝いより意味深く感じられますか？",
    },
    (61, 8): {
        "full_followups": ("Who should feel represented by the event?", "What choice would make that purpose visible?"),
    },
    (62, 2): {
        "full_ja": "別れのあと、どの変化に慣れるのが最も難しいですか？",
    },
    (62, 8): {
        "accessible_followups": ("Would other people notice the sign?", "What might still remain difficult?"),
        "full_followups": ("Would close friends notice the sign before the person did?", "Which difficulty could reasonably remain?"),
    },
    (63, 3): {
        "full": "How can someone ask about a choice not to marry or have children without sounding judgmental?",
        "full_ja": "結婚しない、または子どもを持たない選択について、批判的に聞こえずにどう質問できますか？",
        "full_followups": ("Which question would feel respectful?", "How can someone ask without trying to change the person's mind?"),
    },
    (63, 6): {
        "full": "Without social pressure, what should matter most in decisions about marriage or children?",
        "full_ja": "社会的なプレッシャーがなければ、結婚や子どもについての決定で何が最も大切ですか？",
        "full_followups": ("What does respecting the person's choice sound like?", "Which practical issue deserves the most attention?"),
    },
    (63, 8): {
        "full": "How can people discuss marriage and children without assuming one right choice?",
        "full_ja": "結婚や子どもについて、一つの正解を決めつけずにどう話せますか？",
        "full_followups": ("Which wording avoids pushing one answer?", "How can the discussion stay open and respectful?"),
    },
}
for (_topic_no, _prompt_no), _changes in _FINAL_CONVERSATION_PATCHES.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(_changes)


_THREE_SECOND_PATCHES = {
    (57, 1): {
        "full": "What small gesture or quality makes someone more attractive to you?",
        "full_ja": "どんな小さな行動や特徴が、その人をより魅力的に感じさせますか？",
        "full_followups": ("When do you notice it most?", "Why do you like it?"),
    },
    (57, 2): {
        "accessible": "What can a small kind gesture suggest about someone?",
        "accessible_ja": "小さな親切から、その人について何が感じられますか？",
        "accessible_followups": ("Which quality might it suggest?", "What else would you need to see before judging?"),
    },
    (57, 4): {
        "full": "Where does kindness show most clearly: at home, at work, or with strangers?",
        "full_ja": "親切が最もはっきり表れるのは、家、職場、知らない人との場面のどこですか？",
        "full_followups": ("What might the person do?", "Who would benefit?"),
    },
    (57, 5): {
        "full": "Which matters more after the first meeting: appearance or everyday behaviour?",
        "full_ja": "初対面のあとにより大切になるのは、外見と日常の行動のどちらですか？",
        "full_followups": ("Which one matters first?", "What behaviour could change the first impression?"),
    },
    (57, 6): {
        "full": "When can a charming habit start to feel annoying?",
        "full_ja": "魅力的な癖が、うっとうしく感じ始めるのはどんなときですか？",
        "accessible_followups": ("Does the person's intention matter?", "Which change could make the habit annoying?"),
        "full_followups": ("Does the person's intention matter?", "Which change could make the habit annoying?"),
    },
    (57, 7): {
        "full_followups": ("What matters more to you now?", "Which preference has stayed the same?"),
    },
    (57, 8): {
        "full_followups": ("How would people notice it in daily life?", "Would you want them to mention it?"),
    },
    (59, 1): {
        "accessible_followups": ("Why is it important to you?", "Which is hardest to accept: dishonesty, unkindness, or unreliability?"),
        "full_followups": ("Which personal need makes it important?", "Which crosses the line fastest: lying, cruelty, or broken promises?"),
    },
    (59, 2): {
        "accessible": "Why can one preference become a relationship deal-breaker?",
        "accessible_ja": "一つの好みが、人間関係で絶対に譲れない条件になるのはなぜですか？",
        "full": "How can a simple preference turn into a relationship deal-breaker?",
        "full_ja": "単純な好みが、人間関係で絶対に譲れない条件に変わるのはなぜですか？",
        "accessible_followups": ("What need might it protect?", "Could the same need be met another way?"),
        "full_followups": ("What need might it protect?", "Could the same need be met another way?"),
    },
    (59, 3): {
        "full": "Which preference can you be flexible about in a partner?",
        "full_ja": "パートナーのどんな好みなら柔軟に受け入れられますか？",
        "full_followups": ("Why is it less important?", "When would flexibility go too far?"),
    },
    (59, 4): {
        "full": "Which qualities in a partner can matter more as people get older?",
        "full_ja": "年齢を重ねると、パートナーのどんな特徴がより大切になることがありますか？",
        "full_followups": ("Which quality might matter more?", "Which one might matter less?"),
    },
    (59, 5): {
        "accessible_followups": ("Do family or friends affect that opinion?", "Who should decide what is reasonable?"),
        "full_followups": ("Do family or friends affect that opinion?", "Who should decide what is reasonable?"),
    },
    (59, 6): {
        "full_followups": ("What new fact could change the person's mind?", "What should still remain important?"),
    },
    (59, 7): {
        "full": "What should two people do when their deal-breakers clash?",
        "full_ja": "二人の絶対に譲れない条件がぶつかったら、どうすべきですか？",
        "full_followups": ("Which differences still allow compromise?", "When is ending the relationship more honest?"),
    },
    (59, 8): {
        "accessible_followups": ("What words show that it is your own limit?", "What choice must the other person keep?"),
        "full_followups": ("What words show that it is your own limit?", "What choice must the other person keep?"),
    },
    (60, 4): {
        "accessible_followups": ("What could the person do instead?", "How would they know the new response is helping?"),
        "full_followups": ("What could remind them to use the new response?", "Why might it be hard in the moment?"),
    },
    (60, 6): {
        "accessible_followups": ("What should the person still take responsibility for?", "What action would make the explanation more honest?"),
        "full_followups": ("What should the person still take responsibility for?", "What action would make the explanation more honest?"),
    },
    (60, 7): {
        "accessible_followups": ("Why might the new response be hard?", "Who or what could help?"),
        "full_followups": ("Why might the new response be hard?", "Who or what could help?"),
    },
    (61, 1): {
        "accessible_followups": ("What would it look or sound like?", "Who else would care about it?"),
        "full_followups": ("What would it look or sound like?", "Who else would care about it?"),
    },
    (61, 2): {
        "full_followups": ("Why does the tradition matter?", "How could it fit the couple?"),
    },
    (61, 3): {
        "full": "If one common wedding tradition had to go, which would you choose?",
        "full_ja": "よくある結婚式の習慣を一つなくすなら、どれを選びますか？",
        "full_followups": ("What problem would that solve?", "Who might miss it?"),
    },
    (61, 5): {
        "full_followups": ("Does it need to be expensive?", "Could it work at a small wedding?"),
    },
    (61, 6): {
        "full": "What part of a wedding creates the most unnecessary stress?",
        "full_ja": "結婚式で、いちばん余計なストレスを生むのはどの部分ですか？",
        "full_followups": ("Who usually feels the stress?", "What simple change could reduce it?"),
    },
    (61, 7): {
        "accessible": "Could a tiny ceremony feel more special than a large wedding?",
        "accessible_ja": "ごく小さな式のほうが、大きな結婚式より特別に感じられることはありますか？",
        "full": "Can a private ceremony feel more personal than a large public celebration?",
        "full_ja": "私的な式のほうが、大規模な公の祝いより個人的に感じられますか？",
        "accessible_followups": ("What would be easier at the smaller wedding?", "What might people miss?"),
        "full_followups": ("What would be easier at the private ceremony?", "What might people miss?"),
    },
    (61, 8): {
        "accessible_followups": ("Who is the wedding mainly for?", "What choice would show that?"),
        "full_followups": ("Who is the wedding mainly for?", "What choice would show that?"),
    },
    (62, 1): {
        "accessible_followups": ("What else is lost besides the relationship?", "What can take longest to accept?"),
        "full_followups": ("What else is lost besides the relationship?", "What can take longest to accept?"),
    },
    (62, 2): {
        "full_followups": ("Which daily routine changes first?", "Which change do people often forget about?"),
    },
    (62, 3): {
        "accessible_followups": ("Does a long relationship always take longer to recover from?", "What sign shows progress?"),
        "full_followups": ("Does the way the relationship ended matter?", "What sign shows progress?"),
    },
    (62, 4): {
        "full": "After a breakup, which moments call for time alone and which call for company?",
        "full_ja": "別れのあと、どんなときは一人の時間が必要で、どんなときは誰かといるほうがよいですか？",
        "full_followups": ("What can time alone provide?", "What kind of company would help?"),
    },
    (62, 6): {
        "accessible_followups": ("What becomes clearer with time?", "Can people remember the past unfairly?"),
        "full_followups": ("What becomes clearer with time?", "Can people unfairly blame one person later?"),
    },
    (62, 7): {
        "full_followups": ("Why can the advice feel uncaring?", "What could someone say instead?"),
    },
    (62, 8): {
        "full": "What is one sign that someone is moving forward after a breakup?",
        "full_ja": "別れのあと、前に進んでいると分かるサインは一つ何ですか？",
    },
    (63, 1): {
        "full_followups": ("Which reasons do people often forget about?", "Why are marriage and children separate choices?"),
    },
    (63, 2): {
        "full": "Does anyone owe others an explanation for not wanting marriage or children?",
        "full_ja": "結婚や子どもを望まない理由を、ほかの人に説明する義務はありますか？",
        "full_followups": ("Which questions are too personal?", "When can curiosity be respectful?"),
    },
    (63, 4): {
        "accessible_followups": ("Could money, health, or a relationship change the view?", "Is it okay to be unsure?"),
        "full_followups": ("Could money, health, or a relationship change the view?", "Is it okay to be unsure?"),
    },
    (63, 5): {
        "accessible_followups": ("What do families say that creates pressure?", "What question would be too personal?"),
        "full_followups": ("What do families say that creates pressure?", "What question would be too personal?"),
    },
    (63, 6): {
        "accessible": "Without social pressure, what should matter most when choosing marriage or children?",
        "accessible_ja": "社会的な圧力がなければ、結婚や子どもを選ぶときに何を最も大切にすべきですか？",
        "full": "If social pressure disappeared, what should guide a choice about marriage or children?",
        "full_ja": "社会的な圧力がなくなったら、結婚や子どもについての選択を何が導くべきですか？",
        "accessible_followups": ("Do personal wishes, money, or health matter most?", "What practical issue cannot be ignored?"),
        "full_followups": ("Do personal wishes, money, or health matter most?", "What practical issue cannot be ignored?"),
    },
    (63, 7): {
        "accessible_followups": ("Which daily responsibilities are different?", "Why do people often treat the choices as one?"),
        "full_followups": ("Which daily responsibilities are different?", "Why do people often treat the choices as one?"),
    },
    (63, 8): {
        "accessible_followups": ("What should nobody ask someone to prove?", "What comment would keep the conversation open?"),
        "full_followups": ("What should nobody ask someone to prove?", "What comment would keep the conversation open?"),
    },
}
for (_topic_no, _prompt_no), _changes in _THREE_SECOND_PATCHES.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(_changes)


_THREE_SECOND_FULL_FOLLOWUPS = {
    (57, 4): ("Which action would show kindness there?", "Who would notice the benefit first?"),
    (57, 6): ("Would a good intention change how the habit feels?", "What repeated behaviour could make it irritating?"),
    (59, 1): ("Which personal need makes it important?", "Which would end trust fastest: dishonesty, cruelty, or unreliability?"),
    (59, 2): ("Which need could make the preference non-negotiable?", "Is there another way to protect that need?"),
    (59, 3): ("What makes that preference easier to accept?", "When would being flexible create a real problem?"),
    (59, 5): ("Whose opinion affects the judgment most: family, friends, or the couple?", "Who has the right to set the boundary?"),
    (59, 8): ("How can you make clear that the limit belongs to you?", "Which decision must remain with the other person?"),
    (60, 6): ("Which part of the problem is still the person's responsibility?", "What follow-up action would make the explanation believable?"),
    (60, 7): ("What makes the better response difficult in the moment?", "Would a reminder, another person, or more time help most?"),
    (61, 1): ("How would guests notice that element?", "Which family member might value it too?"),
    (61, 3): ("Which source of stress would disappear?", "Would the couple, family, or guests miss it most?"),
    (61, 5): ("Could the element feel special without costing much?", "How would it work with only a few guests?"),
    (61, 6): ("Who carries most of that stress?", "Which one change would lower it fastest?"),
    (61, 7): ("What would become easier at a private ceremony?", "Which part of a large celebration would be hardest to give up?"),
    (61, 8): ("Should the couple, the families, or the guests come first?", "Which wedding decision would make that priority visible?"),
    (62, 1): ("Which shared plan, place, or routine also disappears?", "What part of the changed future may take longest to accept?"),
    (62, 2): ("What is the first everyday habit that usually changes?", "Which practical change can catch people by surprise?"),
    (62, 3): ("Does the way the relationship ended affect recovery?", "Which everyday sign would show that life is moving forward?"),
    (62, 6): ("Which part of the relationship becomes easier to understand later?", "Can time make someone blame one person too much?"),
    (62, 7): ("Why might that advice sound uncaring?", "Which kinder sentence could replace it?"),
    (63, 2): ("Which questions cross a privacy line?", "What wording would make honest curiosity feel respectful?"),
    (63, 4): ("Which change could matter most: money, health, or a relationship?", "Is ‘I haven't decided’ a complete answer?"),
    (63, 5): ("Which family comment creates the strongest pressure?", "What is one question relatives should avoid?"),
    (63, 6): ("Which should guide the choice first: personal wishes, health, or money?", "Which real-life limit still deserves attention?"),
    (63, 7): ("How do the daily duties of marriage and parenting differ?", "What makes people talk about the two decisions together?"),
    (63, 8): ("Which private reason should nobody demand proof of?", "What could someone say to welcome more than one life path?"),
}
for (_topic_no, _prompt_no), _followups in _THREE_SECOND_FULL_FOLLOWUPS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1]["full_followups"] = _followups


def build(topic_no: int, variant: str) -> str:
    """Render one pair member; intentionally unused until the pilot is released."""
    if topic_no not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_no, variant))
    base, new_lesson = _render_dependencies()
    track = new_lesson.ENGLISH / "tracks/3-freetalking"
    canonical = (
        track
        / f"courses/talk-between-two-countries-{variant}"
        / "lessons/01-this-surprised-me/lesson.html"
    ).read_text(encoding="utf-8")
    data = TOPICS[topic_no]
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{data["slug"]}'
    head = new_lesson.retarget(
        head,
        review_id=f"FT-{topic_no}",
        lesson_id=slug,
        level="B1 accessible" if variant == "accessible" else "B2-C1 full",
        title=data["title"],
        title_ko=data["ko"],
        title_ja=data["ja"],
        version="2026-08-21",
    )
    head = _set_pending(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(
            head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category]
        )
    goal_en, goal_ja = data["goal"]
    pages = [
        base.ft_contract.goal_page(
            title=data["title"],
            title_ja=data["ja"],
            topic_en=goal_en,
            topic_ja=goal_ja,
            data_act="Love and marriage",
            kicker="LOVE AND MARRIAGE",
        ),
        _article_page(topic_no, data, variant, base),
        base.extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of your answers.</span><span class="ja">全部の質問に答える必要はありません。答えの中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Treat these pages as a pool, not a sequence. React or share briefly before choosing the next prompt, skip freely, and move to feedback with 2–3 minutes left.</div></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple(
        (f"q{i}", f"QUESTION {i}") for i in range(1, 7)
    )
    pages.extend(
        _question_page(page_id, number, item, variant, base)
        for (page_id, number), item in zip(prompt_ids, data["prompts"], strict=True)
    )
    pages.append(base.extract_page(canonical, "feedback"))
    return new_lesson.redepth(
        head + "\n".join(pages) + foot, output_path(topic_no, variant)
    )


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
