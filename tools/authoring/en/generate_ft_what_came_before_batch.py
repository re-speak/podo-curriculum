#!/usr/bin/env python3
"""Author and, after pilot release, render the paired FT 76-88 source batch.

Importing this module is source-only: it reads no repository file and imports no
pilot-dependent renderer.  Filesystem and renderer dependencies stay behind
``build``/``output_path``/``main`` so this authored specification can be reviewed
while the canonical FT-1 migration is protected.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


COURSE = "talk-what-came-before"
TOPIC_NUMBERS = tuple(range(76, 89))
VARIANTS = ("accessible", "full")
SENSITIVE_TOPICS = frozenset({80, 81, 84, 85, 87})

# The track entry floor is CORE-53. Later references remain audit evidence and
# are never legal recycled-vocabulary owners for this batch.
FUTURE_CORE_DEPENDENCIES = {
    76: ("CORE-70", "CORE-75"), 78: ("CORE-62",), 81: ("CORE-58",),
    82: ("CORE-66",), 84: ("CORE-66",), 85: ("CORE-58",),
    87: ("CORE-75",), 88: ("CORE-73",),
}
REACHABLE_CORE_RETRIEVAL = {
    76: ("CORE-34",), 77: ("CORE-30",), 79: ("CORE-12", "CORE-34"),
    80: ("CORE-32",), 81: ("CORE-35",), 83: ("CORE-30", "CORE-45"),
    86: ("CORE-30",), 87: ("CORE-43",), 88: ("CORE-30",),
}
TOPIC_FORMAT = {number: "story" for number in TOPIC_NUMBERS}
SHARED_SOURCE = {
    **{number: f"KR 8-{number - 75}" for number in range(76, 86)},
    86: "NEW → KR", 87: "NEW → KR", 88: "NEW → KR",
}
TOC_RETRIEVAL = {
    76: (("___ always used to tell me to ___.", ("CORE-75", "CORE-70"), False), ("I never listened.", ("CORE-34",), False)),
    77: (("We were all terrified of ___.", ("CORE-30",), False), ("Looking back, ___.", (), True)),
    78: (("Everyone called me ___.", (), True), ("I never found out who ___.", ("CORE-62",), False)),
    79: (("I couldn't stand ___.", ("CORE-34",), False), ("Now I ___ all the time.", ("CORE-12",), False)),
    80: (("I completely ___.", ("CORE-32",), False), ("I still can't believe I ___.", (), True)),
    81: (("Everything was fine until ___.", ("CORE-58",), False), ("In the end we ___.", ("CORE-35",), False)),
    82: (("I'd go back tomorrow.", ("CORE-66",), False), ("It wouldn't be the same, though.", ("CORE-66",), False)),
    83: (("I wanted to be ___.", ("CORE-30",), False), ("It's not that far from ___.", ("CORE-45",), False)),
    84: (("I'd go back to ___.", ("CORE-66",), False), ("I wouldn't change it, I'd just ___.", ("CORE-66",), False)),
    85: (("That's when everything ___.", ("CORE-58",), False), ("If that hadn't happened, ___.", (), True)),
    86: (("Apparently I was ___.", ("CORE-30",), False), ("I don't remember it that way.", (), True)),
    87: (("There used to be a ___.", ("CORE-75",), False), ("It's ___ now.", ("CORE-43",), False)),
    88: (("I was completely sure that ___.", ("CORE-30",), False), ("It turned out I'd ___.", ("CORE-73",), True)),
}
TOC_RETRIEVAL_AUDIT_ONLY = True

BRIEF_OPENINGS = {
    76: "What advice do adults often repeat to children?",
    77: "Which teacher—real or fictional—stands out to you most, and why?",
    78: "What's the most memorable school nickname you've heard?",
    79: "Which food do many children dislike but learn to enjoy later?",
    80: "What kind of old mistake becomes a story people keep retelling?",
    81: "What travel problem makes the best story afterward?",
    82: "Choose a place that deserves a return visit. What makes it worth going back?",
    83: "Which childhood dream job is especially interesting to you?",
    84: "You can visit one day in the past. Which day do you choose?",
    85: "What kind of moment can send a life in a completely different direction?",
    86: "How can the same child seem completely different to different people?",
    87: "Which vanished place—local, famous, or personal—would you bring back?",
    88: "What's a belief that many people once accepted but later proved wrong?",
}


def prompt(job, title, title_ja, accessible, accessible_ja, followups, *, full, full_ja, safety, full_followups=None):
    return {
        "job": job, "title": title, "title_ja": title_ja,
        "accessible": accessible, "accessible_ja": accessible_ja,
        "accessible_followups": followups, "full": full, "full_ja": full_ja,
        "full_followups": followups if full_followups is None else full_followups, "safety": safety,
    }


def topic(*, slug, title, ko, ja, goal, article_title, articles, prompts):
    return locals()


# Every article row is (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
    76: topic(
        slug="advice-you-kept-hearing-as-a-child", title="Advice you kept hearing as a child",
        ko="어릴 때 계속 들었던 조언", ja="子どもの頃に何度も聞いた助言",
        goal=("Let's discuss repeated childhood advice, whether personal or general.", "子どもの頃に繰り返し聞いた助言を、個人的な例でも一般的な例でも話しましょう。"),
        article_title=("Why repeated advice stays with us", "繰り返された助言が残る理由"),
        articles=[
            ("Adults often repeat advice because they want to protect a child.", "Adults often repeat advice because protection feels more urgent than explanation.", "大人は子どもを守りたくて、同じ助言を繰り返すことがあります。", "大人は、説明することより守ることを急ぎ、同じ助言を繰り返すことがあります。"),
            ("A child may hear the words long before understanding the reason.", "A child may absorb the wording years before grasping the reason behind it.", "子どもは理由を理解するよりずっと前に、その言葉を聞いていることがあります。", "子どもは、その理由を理解する何年も前から、言い回しだけを覚えていることがあります。"),
            ("Some advice is practical, such as checking the road or saving money.", "Some advice addresses practical risks, from crossing roads to managing money.", "道路を確認することや貯金など、実用的な助言もあります。", "道路を渡るときの確認からお金の管理まで、現実的な危険に関する助言もあります。"),
            ("Other advice reflects the adult's own fears and experiences.", "Other warnings reveal as much about the adult's history as the child's situation.", "別の助言には、大人自身の不安や経験が表れています。", "別の忠告には、子どもの状況と同じくらい大人自身の過去が表れています。"),
            ("Repeated words can feel like nagging when the reason is unclear.", "Without a clear reason, repetition can sound like nagging rather than care.", "理由が分からないと、繰り返す言葉は口うるさく感じられます。", "理由が明確でなければ、繰り返しは思いやりより小言のように聞こえます。"),
            ("People sometimes ignore good advice simply because they hear it too often.", "Even sound advice can lose force when repetition makes it background noise.", "よい助言でも、何度も聞くため無視してしまうことがあります。", "妥当な助言でも、繰り返されて当たり前になると力を失うことがあります。"),
            ("Its meaning may become clear only after a similar mistake.", "The meaning may become obvious only after experience recreates the original risk.", "同じような失敗をして初めて、意味が分かることもあります。", "経験によって同じ危険に直面して初めて、その意味が明らかになることがあります。"),
            ("Some people later repeat the same words to someone younger.", "People may later hear themselves passing the same warning to a younger person.", "後になって、同じ言葉を年下の人に言う人もいます。", "後になって、自分が同じ忠告を年下の人にしていると気づくこともあります。"),
            ("Other advice deserves to be questioned or left behind.", "Some inherited advice deserves revision because the world or the value behind it changed.", "一方で、疑ったり手放したりしたほうがよい助言もあります。", "時代や価値観が変わり、受け継いだ助言を見直す必要がある場合もあります。"),
            ("Remembering the words lets us decide what to keep and what to change.", "Revisiting the words helps us separate useful care from fear we need not inherit.", "その言葉を思い出すと、残すものと変えるものを選べます。", "その言葉を振り返ることで、役立つ思いやりと受け継ぐ必要のない不安を分けられます。"),
        ],
        prompts=[
            prompt("opening", "The repeated line", "何度も聞いた言葉", BRIEF_OPENINGS[76], "子どもの頃、大人から何度も言われたことは何ですか？", ("If a line comes to mind, who said it?", "If none does, what advice do adults commonly repeat to children?"), full="Which piece of advice did an adult repeat to you throughout childhood?", full_ja="子どもの頃、大人から繰り返し言われた助言は何ですか？", safety="personal-or-general-advice"),
            prompt("wording", "The exact words", "実際の言葉", "What did they actually say—or what is the common version?", "実際には何と言われましたか。それとも、よくある言い方は何ですか？", ("Was it short or explained?", "Which word made it memorable?"), full="What was the exact wording, or how is that advice usually phrased?", full_ja="正確にはどんな言い方でしたか。それとも、一般にどう言われますか？", safety="same-route-wording"),
            prompt("response", "Did it land?", "聞き入れたか", "Did the child in your example follow the advice, resist it, or react another way?", "その例の子どもは、その助言に従いましたか、反発しましたか、それとも別の反応をしましたか？", ("If they followed it, what did they do?", "If they resisted or reacted another way, what did they do?"), full="Did the child in your chosen example follow the advice, resist it, or respond in some other way?", full_ja="選んだ例の子どもは、その助言に従いましたか、反発しましたか、それとも別の形で反応しましたか？", full_followups=("If they followed it, how did that show?", "If they resisted or responded another way, what happened?"), safety="followed-resisted-or-other-response"),
            prompt("reason", "Why repeat it?", "繰り返す理由", "Did worry, experience, or tradition make the adult keep saying it?", "心配、経験、または習慣から、大人はそれを言い続けたのでしょうか？", ("Which source best explains the repetition?", "Was the reason clear at the time?"), full="What concern, experience, or tradition probably made the adult repeat it?", full_ja="どんな心配、経験、または習慣から、大人はそれを繰り返したのでしょうか？", safety="concern-experience-or-tradition"),
            prompt("hindsight", "Were they right?", "正しかったか", "Looking back, was the advice useful, partly useful, or wrong?", "振り返ると、その助言は役立ちましたか、一部だけ役立ちましたか、それとも間違っていましたか？", ("What changed your view?", "Which part would you rewrite?"), full="In hindsight, was the advice sound, limited, or mistaken?", full_ja="振り返ると、その助言は妥当でしたか、限界がありましたか、それとも間違っていましたか？", safety="balanced-hindsight"),
            prompt("inheritance", "Passing it on", "受け継ぐ言葉", "Would you pass that advice on, change it, or stop repeating it?", "その助言を伝えますか、変えますか、それとも繰り返すのをやめますか？", ("If you passed it on, how would you explain it?", "If you revised or ended it, why?"), full="Would you pass that advice on, revise it, or let it end with that generation?", full_ja="その助言を伝えますか、言い換えますか、それともその世代で終わらせますか？", safety="pass-revise-or-end"),
            prompt("nagging", "Your own reminder", "自分なら何を言うか", "What might you nag a child about, if anything?", "子どもに口うるさく言うとしたら、何についてですか。それとも特にありませんか？", ("If you chose a reminder, why would it matter?", "If you chose none, why avoid repeated reminders?"), full="What, if anything, might you repeatedly remind a child about?", full_ja="子どもに繰り返し伝えるとしたら何ですか。それとも特にありませんか？", safety="reminder-or-none"),
            prompt("flip", "Advice for adults", "大人への助言", "What advice do adults need to hear more often?", "大人がもっと聞く必要のある助言は何ですか？", ("Who could say it convincingly?", "Why is it easy to ignore?"), full="Which advice do adults themselves most need to hear repeatedly?", full_ja="大人自身が繰り返し聞く必要のある助言は何ですか？", safety="general-adult-flip"),
        ],
    ),
    77: topic(
        slug="a-teacher-you-still-remember", title="A teacher you still remember",
        ko="아직도 기억나는 선생님", ja="今も覚えている先生",
        goal=("Let's describe a real, familiar, or fictional teacher and their effect.", "実際の先生、身近な例、作品の先生のいずれかと、その影響について話しましょう。"),
        article_title=("Why some teachers remain memorable", "記憶に残る先生の理由"),
        articles=[
            ("A memorable teacher is not always the kindest or most popular one.", "A memorable teacher is not necessarily the warmest, easiest, or most admired one.", "記憶に残る先生が、いつも最も優しく人気があるとは限りません。", "記憶に残る先生が、最も温かく接しやすく、尊敬されていたとは限りません。"),
            ("Students may remember a teacher's voice, rules, humour, or patience.", "Memory may preserve a teacher's voice, standards, humour, patience, or unpredictability.", "生徒は先生の声、規則、ユーモア、忍耐強さを覚えていることがあります。", "記憶には、先生の声、基準、ユーモア、忍耐強さ、意外な一面が残ることがあります。"),
            ("Strictness can feel frightening at the time and fair later.", "Strictness can feel intimidating in the moment yet reasonable in retrospect.", "厳しさは当時怖く感じても、後で公平だったと思えることがあります。", "厳しさはその場では威圧的でも、振り返ると妥当だったと思えることがあります。"),
            ("It can also remain unfair, especially when it humiliates a student.", "Discipline remains harmful when it relies on humiliation rather than clear standards.", "一方、生徒に恥をかかせる厳しさは、不公平なまま残ることもあります。", "明確な基準ではなく屈辱に頼る指導は、後になっても有害なままです。"),
            ("A small act of attention can matter more than a dramatic speech.", "One precise act of attention may matter more than an inspirational speech.", "小さな気づかいが、大げさな言葉より大切なこともあります。", "的確な気づかいが、感動的な演説より大きな意味を持つことがあります。"),
            ("A teacher may notice an ability before the student does.", "A teacher can recognize potential before the learner has language for it.", "先生が、生徒本人より先に能力に気づくこともあります。", "先生が、学ぶ側がまだ言葉にできない可能性を先に見つけることもあります。"),
            ("Lessons about effort or fairness may last longer than subject knowledge.", "Lessons about effort, fairness, or curiosity can outlast the course content itself.", "努力や公平さについての教えは、教科の知識より長く残ることがあります。", "努力、公平さ、好奇心についての教えは、授業内容そのものより長く残ることがあります。"),
            ("Students also remember teachers through stories shared by classmates.", "Classroom memory is partly collective, shaped by stories students repeat to one another.", "生徒は、同級生と共有した話を通して先生を覚えていることもあります。", "教室の記憶は一部共有され、生徒同士が繰り返す話によって形作られます。"),
            ("Time can soften fear without making every action acceptable.", "Distance may soften fear without excusing conduct that crossed a line.", "時間が恐怖を和らげても、すべての行動が許されるわけではありません。", "時間が恐怖を和らげても、限度を越えた行動まで正当化されるわけではありません。"),
            ("Remembering a teacher can clarify what good teaching means to us.", "Revisiting a teacher's influence can reveal the kind of guidance we now value.", "先生を思い出すと、自分にとってよい指導とは何かが分かります。", "先生の影響を振り返ると、今の自分がどんな導き方を大切にするかが見えてきます。"),
        ],
        prompts=[
            prompt("opening", "A memorable teacher", "記憶に残る先生", BRIEF_OPENINGS[77], "今も覚えている先生は誰ですか。なぜ覚えていますか？", ("If nobody comes to mind, which teacher from a story or public example could you use?", "What makes that person memorable?"), full="Which teacher remains vivid in your memory, and why?", full_ja="今も鮮明に記憶に残る先生は誰ですか。なぜですか？", safety="real-familiar-fictional-teacher"),
            prompt("identity", "Who they were", "どんな先生か", "What did that teacher teach, or what role did they have?", "その先生は何を教えていましたか。それとも、どんな役割でしたか？", ("About how old was the student?", "What was the setting like?"), full="What subject or role connected the teacher to the student in your example?", full_ja="その例では、どの教科や役割で先生と生徒が関わっていましたか？", safety="same-example-identity"),
            prompt("scene", "One clear moment", "一つの場面", "What did the teacher do that stands out?", "その先生のどんな行動が強く印象に残っていますか？", ("What happened right before it?", "How did the student respond?"), full="Which specific action best captures why the teacher is memorable?", full_ja="その先生が記憶に残る理由を最もよく表す行動は何ですか？", safety="same-example-scene"),
            prompt("emotion", "Fear or gratitude", "怖さと感謝", "Did the student feel scared, grateful, both, or neither?", "その生徒は怖さ、感謝、その両方、またはどちらでもない気持ちでしたか？", ("If there was a feeling, did it change later?", "If neither fits, how did the student feel?"), full="Did the teacher inspire fear, gratitude, both, or neither in the student?", full_ja="その先生は生徒に恐れ、感謝、その両方、またはどちらでもない感情を抱かせましたか？", safety="fear-gratitude-both-or-neither"),
            prompt("learning", "Beyond the subject", "教科以外の学び", "What did the student learn from that teacher besides the subject?", "その生徒は教科以外に、その先生から何を学びましたか？", ("Does that lesson still matter?", "Was it taught directly or by example?"), full="Which lesson beyond the curriculum did the teacher leave with the student?", full_ja="その先生は、授業内容以外にどんな学びを生徒に残しましたか？", safety="same-example-learning"),
            prompt("hindsight", "Looking back", "振り返って", "Looking back, does the teacher seem fairer, less fair, or unchanged?", "振り返ると、その先生はより公平に、より不公平に、それとも同じように見えますか？", ("Which judgment changed, if any?", "Which judgment stayed the same?"), full="In retrospect, has your judgment of the teacher's approach improved, worsened, or remained stable?", full_ja="振り返ると、その先生のやり方への評価はよくなりましたか、悪くなりましたか、それとも変わりませんか？", safety="improved-worsened-or-unchanged"),
            prompt("message", "What you would say", "今伝えるなら", "What would you say to that teacher now, if anything?", "今その先生に何か伝えるなら、何と言いますか？", ("If you sent a message, would it be thanks, a question, or criticism?", "If you would send nothing, why leave it unsaid?"), full="If you could send one message to that teacher—or choose silence—what would you do?", full_ja="今その先生に一つメッセージを送れるなら何を伝えますか。それとも何も伝えませんか？", safety="message-or-silence"),
            prompt("flip", "A difficult teacher", "苦手だった先生", "What makes a teacher difficult to learn from?", "どんな先生だと学びにくいですか？", ("Can strict teaching still work?", "Which behaviour crosses a line?"), full="Which teacher behaviour most seriously prevents learning?", full_ja="先生のどんな行動が、学ぶことを最も大きく妨げますか？", safety="general-teaching-flip"),
        ],
    ),
    78: topic(
        slug="a-nickname-you-had-at-school", title="A nickname you had at school",
        ko="학교에서 불리던 별명", ja="学校で呼ばれていたあだ名",
        goal=("Let's discuss a real, observed, or imagined school nickname.", "実際にあった、見聞きした、または想像した学校のあだ名について話しましょう。"),
        article_title=("What a nickname can carry", "あだ名に込められるもの"),
        articles=[
            ("A school nickname may begin with a name, habit, joke, or accident.", "A school nickname may grow from a name, habit, private joke, or accidental moment.", "学校のあだ名は、名前、癖、冗談、偶然の出来事から生まれます。", "学校のあだ名は、名前、癖、内輪の冗談、偶然の瞬間から広がることがあります。"),
            ("Sometimes the person chooses it, but often someone else does.", "Some nicknames are chosen; others are assigned before the person can object.", "本人が選ぶこともありますが、多くは別の人が決めます。", "自分で選ぶあだ名もあれば、本人が断る前に周囲が決めるものもあります。"),
            ("A nickname can signal closeness when everyone understands its tone.", "Shared tone can make a nickname a compact sign of affection and belonging.", "みんながその調子を分かっていれば、あだ名は親しさを表せます。", "共有された調子によって、あだ名は愛情や仲間意識を短く表すものになります。"),
            ("The same nickname can hurt when it points to an insecurity.", "The same label can become cruel when it targets an insecurity or ignores discomfort.", "同じあだ名でも、本人の気にしている点を指すと傷つけます。", "同じ呼び名でも、本人が気にしている点を狙ったり、嫌がる気持ちを無視したりすると残酷になります。"),
            ("People may laugh along because refusing feels difficult.", "A student may pretend to accept a nickname because resistance risks more attention.", "断りにくくて、一緒に笑う人もいます。", "拒むとさらに注目されるため、あだ名を受け入れたふりをする生徒もいます。"),
            ("A good nickname usually disappears when the person asks it to stop.", "Affectionate use requires consent and should end when the person withdraws it.", "よいあだ名でも、本人がやめてほしいと言えば普通は使わなくなります。", "親しみのある呼び方にも同意が必要で、本人が取り消せば終わるべきです。"),
            ("Some nicknames survive for decades and connect old friends.", "A nickname may survive for decades as a shortcut back into an old friendship.", "何十年も残り、昔の友人を結びつけるあだ名もあります。", "あだ名が何十年も残り、昔の友情に戻る近道になることもあります。"),
            ("Others make sense only inside one classroom or year.", "Other labels depend so completely on one classroom that outsiders cannot decode them.", "一つの教室や学年でしか意味が通じないものもあります。", "一つの教室に強く結びつき、外の人には意味が分からない呼び名もあります。"),
            ("Adult nicknames often reflect roles, online identities, or shortened names.", "Adult nicknames may emerge from work roles, online identities, or deliberate reinvention.", "大人のあだ名は、役割、ネット上の名前、短い名前から生まれることがあります。", "大人のあだ名は、仕事の役割、オンライン上の名前、意図的な自己表現から生まれることがあります。"),
            ("The best nickname is easy to recognize and safe for its owner.", "A lasting nickname works only when recognition and the owner's comfort coexist.", "よいあだ名は分かりやすく、呼ばれる本人が安心できるものです。", "長く残るあだ名には、分かりやすさと本人の心地よさの両方が必要です。"),
        ],
        prompts=[
            prompt("opening", "A school nickname", "学校のあだ名", BRIEF_OPENINGS[78], "学校で何と呼ばれていましたか？", ("If you had no nickname, which nickname you heard—or an imagined one—can we use?", "Who used it?"), full="What nickname, if any, did people use for you at school?", full_ja="学校では、あだ名があるとすれば何と呼ばれていましたか？", safety="real-observed-imagined-nickname"),
            prompt("origin", "How it began", "始まった理由", "How did that nickname begin?", "そのあだ名はどのように始まりましたか？", ("Who first used it?", "Was the reason obvious?"), full="Where did the chosen nickname come from, and who introduced it?", full_ja="選んだあだ名は何から生まれ、誰が使い始めましたか？", safety="same-nickname-origin"),
            prompt("feeling", "How it felt", "どう感じたか", "Did the person like the nickname, dislike it, or not care?", "その人はあだ名が好きでしたか、嫌いでしたか、それとも気にしませんでしたか？", ("Did that feeling change?", "Could they ask people to stop?"), full="Did the person welcome, tolerate, or reject the nickname?", full_ja="その人はあだ名を喜びましたか、我慢しましたか、それとも拒みましたか？", safety="nonbinary-feeling-route"),
            prompt("meaning", "What it said", "表していたこと", "What did the nickname suggest about the person?", "そのあだ名は、その人のどんなところを表していましたか？", ("Was that picture accurate?", "Did outsiders understand it?"), full="Which identity or story did the nickname attach to the person?", full_ja="そのあだ名は、その人にどんな人物像や物語を結びつけましたか？", safety="same-nickname-meaning"),
            prompt("duration", "Did it last?", "今も残っているか", "Does anyone still use it—or when did it stop?", "今も誰かが使っていますか。それとも、いつ使われなくなりましたか？", ("Who kept using it longest?", "Would it feel strange now?"), full="Has the nickname survived, or what caused it to disappear?", full_ja="そのあだ名は今も残っていますか。それとも、何がきっかけで消えましたか？", safety="survived-or-ended"),
            prompt("others", "Names for others", "ほかの人のあだ名", "Did you use nicknames for other people—or can you give a general example?", "ほかの人をあだ名で呼びましたか。それとも一般的な例を挙げられますか？", ("Was the person comfortable with it?", "What made it friendly or unfair?"), full="Did you assign nicknames to others, or which general example shows how that works?", full_ja="ほかの人にあだ名を付けましたか。それとも、その仕組みが分かる一般的な例はありますか？", safety="personal-or-general-others"),
            prompt("boundary", "Friendly or cruel", "親しさと残酷さ", "When does a nickname stop being friendly?", "あだ名が親しみのある呼び方ではなくなるのは、どんなときですか？", ("Who gets to decide?", "Can a nickname recover after causing hurt?"), full="Which boundary separates affectionate naming from ridicule?", full_ja="親しみのある呼び方と、からかいを分ける境界は何ですか？", safety="general-consent-boundary"),
            prompt("flip", "A nickname now", "今のあだ名", "What nickname would fit you now, if any?", "今の自分に合うあだ名があるとすれば何ですか？", ("Who might use it?", "Would you choose it yourself?"), full="If you chose a nickname for your present self, what would it capture?", full_ja="今の自分にあだ名を付けるなら、どんな特徴を表しますか？", safety="optional-self-chosen-flip"),
        ],
    ),
    79: topic(
        slug="something-you-hated-as-a-child-but-love-now", title="Something you hated as a child but love now",
        ko="어릴 때 싫었지만 지금은 좋아하는 것", ja="子どもの頃は嫌いで今は好きなもの",
        goal=("Let's trace how a real or general preference can change over time.", "実際の例でも一般的な例でも、好みが時間とともに変わる過程を話しましょう。"),
        article_title=("How dislikes can change", "嫌いなものが変わるまで"),
        articles=[
            ("Children often reject food because of bitterness, texture, smell, or appearance.", "Children may reject food because bitterness, texture, smell, or appearance feels unusually intense.", "子どもは苦味、食感、匂い、見た目で食べ物を嫌うことがあります。", "子どもは、苦味、食感、匂い、見た目を特に強く感じて食べ物を拒むことがあります。"),
            ("A forced bite can make the dislike stronger.", "Pressure to eat can attach conflict to the taste and deepen resistance.", "無理に一口食べさせられると、嫌いな気持ちが強くなることがあります。", "食べるよう強制されると、味に対立の記憶が結びつき、抵抗が強まることがあります。"),
            ("Taste can change as the body and experience change.", "Taste develops alongside the body, familiarity, and wider experience.", "体や経験が変わるにつれて、味の好みも変わります。", "体、慣れ、経験の広がりとともに、味の好みも変化します。"),
            ("Preparation matters: one bad version is not every version.", "Preparation can transform the same ingredient, so one poor version proves little.", "調理法は大切で、一度まずかったからといって全部が同じではありません。", "調理法で同じ食材も変わるため、一度の悪い経験だけでは判断できません。"),
            ("A food may grow on someone after several relaxed tries.", "A flavour may gradually grow on someone when repeated exposure carries no pressure.", "気楽に何度か試すうちに、その食べ物を好きになることもあります。", "強制されずに何度か触れることで、その味が徐々に好きになることがあります。"),
            ("People are more willing to try food when they choose the moment.", "Choice over timing and portion can make experimentation feel safer.", "自分でタイミングを選ぶと、食べ物を試しやすくなります。", "試す時期や量を自分で選べると、新しい味に挑戦しやすくなります。"),
            ("Friends, travel, or cooking can change the context around a taste.", "Friends, travel, or learning to cook can give an old ingredient a new context.", "友人、旅行、料理が、その味を取り巻く状況を変えることがあります。", "友人、旅行、自分で料理する経験が、昔の食材に新しい意味を与えることがあります。"),
            ("Not every dislike needs to disappear.", "A stable dislike is not a personal failure and requires no correction.", "すべての嫌いなものを好きになる必要はありません。", "嫌いなままでいることは失敗ではなく、直す必要もありません。"),
            ("Adults also develop new dislikes as their habits and bodies change.", "Preference can move in both directions as health, routine, and attention change.", "習慣や体が変わり、大人になってから嫌いになるものもあります。", "健康、習慣、意識が変わると、好みはどちらの方向にも動きます。"),
            ("Changing taste is one small example of how people remain flexible.", "A changing palate is a concrete reminder that identity and preference are not fixed.", "味の好みの変化は、人が柔軟であり続ける小さな例です。", "味覚の変化は、自分らしさや好みが固定されていないことを具体的に示します。"),
        ],
        prompts=[
            prompt("opening", "Then and now", "昔と今", BRIEF_OPENINGS[79], "子どもの頃は食べなかったのに、今は好きなものは何ですか？", ("If nothing changed, which dislike stayed the same or which general example can we use?", "What did the child dislike about it?"), full="Which food did you reject as a child but enjoy now?", full_ja="子どもの頃は拒んでいたのに、今は好きな食べ物は何ですか？", safety="changed-stable-or-general-taste"),
            prompt("detail", "What was wrong with it?", "嫌だった点", "What did the child dislike: taste, smell, texture, or something else?", "その子どもは、味、匂い、食感、それとも別の点が嫌いでしたか？", ("Was one version especially bad?", "Did anyone pressure them to eat it?"), full="Which feature created the dislike in the chosen example?", full_ja="選んだ例では、どの特徴が嫌いな気持ちを生みましたか？", safety="same-example-detail"),
            prompt("timing", "When it changed", "変わった時期", "When did the preference change—or why has it stayed the same?", "好みはいつ変わりましたか。それとも、なぜ今も変わっていませんか？", ("If it changed, was the shift sudden or gradual?", "If it stayed the same, what kept the dislike stable?"), full="When did the preference shift, or what has kept the dislike stable?", full_ja="好みはいつ変化しましたか。それとも、何が嫌いなままにしていますか？", full_followups=("If it shifted, was the change sudden or gradual?", "If it remained stable, which condition kept the dislike in place?"), safety="change-or-stability-timing"),
            prompt("cause", "What changed it", "変えたもの", "What changed—or might change—the response, or what keeps the dislike stable?", "反応を変えた、または変えそうなものは何ですか。それとも、何が嫌いなままにしていますか？", ("If it changed, did cooking, a person, or a place matter?", "If it might change, what could matter; if it stays stable, what reinforces the dislike?"), full="Which experience transformed or might transform the response, or which condition keeps it stable?", full_ja="どんな経験が反応を変えた、または変える可能性がありますか。それとも、どんな条件が嫌いな状態を保っていますか？", full_followups=("If it transformed, which preparation, person, or setting mattered?", "If change is hypothetical, what could matter; if it remains stable, what reinforces it?"), safety="changed-hypothetical-or-stable-cause"),
            prompt("still-no", "Still off the menu", "今も苦手なもの", "Is there anything the person still refuses to eat—or can we use a general example?", "その人が今も食べないものはありますか。それとも一般的な例にしますか？", ("What makes that different?", "Would the person ever try it again?"), full="Which food, if any, does the person still rule out—or which general example can we use?", full_ja="その人が今も食べようとしないものはありますか。それとも一般的な例を使いますか？", safety="none-safe-current-dislike"),
            prompt("reverse", "A child would object", "子どもなら嫌がるもの", "What does the person enjoy now that their child self—or a child in a general example—might hate?", "その人が今は好きでも、子どもの頃の本人や一般的な例の子どもなら嫌がりそうなものは何ですか？", ("Is it the flavour or the setting?", "What would surprise the child most?"), full="Which present preference in the chosen example would most surprise the person's childhood self?", full_ja="選んだ例の今の好みのうち、その人の子どもの頃が最も驚きそうなものは何ですか？", safety="same-person-or-general-child"),
            prompt("respect", "No need to force it", "無理に変えない", "When should people stop trying to change someone's taste?", "人の好みを変えようとするのをやめるべきなのは、どんなときですか？", ("What is friendly encouragement?", "What becomes pressure?"), full="Where is the boundary between inviting someone to try and pressuring them?", full_ja="試してみるよう勧めることと、無理に迫ることの境界はどこですか？", safety="general-consent-boundary"),
            prompt("flip", "Taste at sixty", "六十歳の好み", "What might the person enjoy at sixty that they do not like now?", "その人が今は好きでなくても、六十歳なら楽しんでいそうなものは何ですか？", ("Why might that taste change?", "Which preference might stay the same?"), full="Which current dislike in the chosen example might the person's sixty-year-old self outgrow?", full_ja="選んだ例で今嫌いなもののうち、その人が六十歳までに克服しそうなものは何ですか？", safety="chosen-person-future-hypothesis"),
        ],
    ),
    80: topic(
        slug="a-mistake-people-still-remind-you-about", title="A mistake people still remind you about",
        ko="사람들이 아직도 꺼내는 실수", ja="今でも話題にされる失敗",
        goal=("Let's tell a real, familiar, fictional, or invented mistake story.", "実体験、身近な話、作品、または想像上の失敗談を話しましょう。"),
        article_title=("Why old mistakes become stories", "昔の失敗が物語になる理由"),
        articles=[
            ("A mistake can become a shared story after the problem is over.", "Once the problem has passed, a mistake can become part of a group's shared history.", "問題が終わると、失敗がみんなの思い出話になることがあります。", "問題が過ぎると、失敗が集団で共有する歴史の一部になることがあります。"),
            ("People bring it up because the details are easy to remember.", "People bring it up because a clear sequence and surprising result make it memorable.", "細かい内容を思い出しやすいため、人はその話を何度も出します。", "流れが明確で結果が意外だと記憶に残り、人はその話を繰り返します。"),
            ("The person involved may find it funny, painful, or both.", "The central person may experience the retelling as affectionate, painful, or both at once.", "当事者はそれを面白く、つらく、または両方に感じることがあります。", "当事者は、語り直されることを親しみ、苦痛、またはその両方として感じる場合があります。"),
            ("A funny story still needs the person's consent.", "Humour does not remove the need to respect the subject's discomfort.", "面白い話でも、本人がよいと思うことが必要です。", "ユーモアがあっても、本人の不快感を尊重する必要はなくなりません。"),
            ("Some mistakes reveal a weak plan rather than a careless person.", "Some errors expose a flawed system or assumption rather than individual carelessness.", "失敗によっては、人の不注意ではなく、計画の不備が明らかになります。", "失敗によっては、個人の不注意ではなく、仕組みや前提の欠陥が明らかになります。"),
            ("The next action often matters more than the original error.", "Repair, honesty, and responsibility often matter more than the initial error.", "最初の失敗より、その後の行動のほうが大切なことがあります。", "最初の誤りより、修復、正直さ、責任の取り方のほうが重要なことがあります。"),
            ("Retelling can show how much the person has changed.", "A repeated story can highlight distance between the person's past and present judgment.", "その話を繰り返すと、その人がどれだけ変わったかが分かります。", "繰り返される話は、過去と現在の判断の違いを浮かび上がらせます。"),
            ("It stops being harmless when it is used to shame someone.", "The story becomes harmful when humour turns into a fixed judgment about character.", "人を恥ずかしがらせるために使うと、無害な話ではなくなります。", "笑い話が人格への決めつけに変わると、その話は有害になります。"),
            ("Some stories deserve an apology instead of another laugh.", "Some memories call for acknowledgment or apology rather than another performance.", "もう一度笑うより、謝るべき思い出もあります。", "再び笑いにするより、認めたり謝ったりする必要のある記憶もあります。"),
            ("A good retelling leaves everyone able to laugh or decline.", "A fair retelling leaves the subject free to join the laughter or end the story.", "よい語り方なら、誰でも笑うか断るかを選べます。", "公平な語り直しなら、当事者は一緒に笑うことも話を終わらせることもできます。"),
        ],
        prompts=[
            prompt("opening", "An old mistake", "昔の失敗", BRIEF_OPENINGS[80], "自分の失敗で、人が今でも話題にするものは何ですか？", ("If none feels safe, which familiar, fictional, or invented mistake can we use?", "Why is that story remembered?"), full="Which mistake of yours do people still bring up?", full_ja="自分のどの失敗を、人は今でも話題にしますか？", safety="personal-familiar-fictional-invented"),
            prompt("event", "What happened", "何が起きたか", "What happened in the chosen story?", "選んだ話では何が起きましたか？", ("What was supposed to happen?", "Which detail caused the problem?"), full="What sequence of events produced the mistake in your chosen story?", full_ja="選んだ話では、どんな流れで失敗が起きましたか？", safety="same-story-event"),
            prompt("witness", "Who knew", "知っていた人", "Who saw it—or who learned about it later?", "誰が見ましたか。それとも、後で誰が知りましたか？", ("How did they find out?", "Did anyone help?"), full="Who witnessed the mistake, or how did the story reach other people?", full_ja="誰が失敗を見ましたか。それとも、どのようにほかの人へ伝わりましたか？", safety="witness-or-later-audience"),
            prompt("repair", "What came next", "その後の行動", "What did the person do next?", "その人は次に何をしましたか？", ("Could the problem be fixed?", "Did they admit the mistake?"), full="How did the person respond once the mistake became clear?", full_ja="失敗が明らかになった後、その人はどう対応しましたか？", safety="same-story-repair"),
            prompt("reaction", "Other people's response", "周りの反応", "If anyone else was involved, how did they react? If not, how did the person react alone?", "ほかの人が関わっていたなら、どう反応しましたか。誰もいなければ、本人は一人でどう反応しましたか？", ("If someone reacted, were they angry, amused, or something else?", "If nobody else was involved, did the person's private reaction feel fair?"), full="How did other people respond, if any, or how did the person process the mistake alone?", full_ja="ほかの人がいたならどう反応しましたか。それとも、本人は一人でその失敗をどう受け止めましたか？", safety="others-or-private-reaction"),
            prompt("now", "Funny now?", "今は笑えるか", "Is the story funny now, uncomfortable, or both?", "その話は今では面白いですか、気まずいですか、それとも両方ですか？", ("Who is allowed to tell it?", "Would the person rather retire it?"), full="Has the memory become amusing, remained uncomfortable, or acquired both meanings?", full_ja="その記憶は面白くなりましたか、気まずいままですか、それとも両方の意味を持ちましたか？", safety="nonbinary-current-feeling"),
            prompt("change", "What it changed", "変わったこと", "What changed because of that mistake, if anything?", "その失敗で何か変わりましたか。それとも何も変わりませんでしたか？", ("If something changed, was it a habit, rule, or judgment?", "If nothing lasted, why did the story remain memorable?"), full="Did the mistake create a lasting change in habit, rule, or judgment, or no lasting change?", full_ja="その失敗で習慣、規則、判断が長く変わりましたか。それとも長く残る変化はありませんでしたか？", safety="lasting-change-or-none"),
            prompt("flip", "Retelling fairly", "公平に語る", "What makes an old mistake fair to bring up again?", "昔の失敗をもう一度話題にしても公平なのは、どんな場合ですか？", ("Whose permission matters?", "When should the story stop?"), full="Which conditions make retelling another person's old mistake acceptable?", full_ja="ほかの人の昔の失敗を語り直してもよい条件は何ですか？", safety="general-consent-flip"),
        ],
    ),
    81: topic(
        slug="a-trip-that-went-wrong", title="A trip that went wrong", ko="잘못되어 버린 여행", ja="うまくいかなかった旅行",
        goal=("Let's tell a real, familiar, public, or imagined travel-mishap story.", "実体験、身近な話、公の例、または想像上の旅行トラブルを話しましょう。"),
        article_title=("Why bad trips become good stories", "大変な旅行がよい話になるまで"),
        articles=[
            ("A travel mishap interrupts a plan in an unfamiliar place.", "A travel mishap disrupts a plan when information and control are already limited.", "旅行のトラブルは、慣れない場所で計画を中断させます。", "旅行のトラブルは、情報も状況を自分で動かせる余地も限られた中で、計画を崩します。"),
            ("Missed transport, bad weather, and lost items create different problems.", "Missed connections, severe weather, and lost belongings demand different responses.", "乗り遅れ、悪天候、紛失では、それぞれ違う問題が起きます。", "乗り継ぎの失敗、厳しい天候、持ち物の紛失には、それぞれ違う対応が必要です。"),
            ("The first useful step is often to learn what is still possible.", "The first useful response is often to replace panic with accurate options.", "まず役立つのは、まだ何ができるかを知ることです。", "最初に役立つのは、慌てる代わりに正確な選択肢を知ることです。"),
            ("A small delay can become serious when plans are tightly connected.", "A minor delay can cascade when bookings and obligations depend on one another.", "予定が詰まっていると、小さな遅れが大きな問題になります。", "予約や用事が連動していると、小さな遅れが次々に影響します。"),
            ("Flexible time and money make recovery easier.", "Extra time, flexible bookings, and emergency funds increase room to recover.", "時間やお金に余裕があると、立て直しやすくなります。", "時間、変更できる予約、緊急用のお金があると、立て直す余地が増えます。"),
            ("People travelling together may want different solutions.", "Travel companions may disagree about cost, risk, speed, and when to give up.", "一緒に旅行する人が、違う解決策を望むこともあります。", "同行者は、費用、危険、速さ、諦める時点について意見が分かれることがあります。"),
            ("A solo traveller may need help from staff or strangers.", "A solo traveller may depend more heavily on clear information from staff or strangers.", "一人旅では、係員や知らない人の助けが必要なことがあります。", "一人旅では、係員や知らない人からの明確な情報により頼る場合があります。"),
            ("The trip may still contain one good moment.", "Even a disrupted trip may contain an unexpected kindness or discovery.", "大変な旅行にも、一つはよい瞬間があるかもしれません。", "予定が崩れた旅行にも、思いがけない親切や発見があるかもしれません。"),
            ("Distance can turn stress into a story, but not always.", "Time can make a stressful event narratable without making the original harm trivial.", "時間がたつと大変な出来事が話になりますが、いつもではありません。", "時間がたてば話せるようになっても、当時の被害が小さくなるわけではありません。"),
            ("The lesson is usually about preparation, priorities, or asking for help.", "What remains is often a clearer sense of preparation, priorities, and when to seek help.", "多くの場合、残る教訓は、準備や優先順位、助けを求めることに関するものです。", "残るのは、準備、優先順位、助けを求める時期への理解であることが多いです。"),
        ],
        prompts=[
            prompt("opening", "A trip in trouble", "大変だった旅行", BRIEF_OPENINGS[81], "何かがうまくいかなかった旅行について話してください。", ("If no personal trip fits, which familiar, public, or imagined travel mishap can we use?", "Where was the traveller going?"), full="Tell me about a trip disrupted by something going wrong.", full_ja="何かのトラブルで予定が崩れた旅行について話してください。", safety="personal-familiar-public-imagined"),
            prompt("setting", "The plan", "最初の計画", "Where was the traveller going, and what was the plan?", "旅行者はどこへ行き、どんな計画でしたか？", ("How much time did they have?", "What mattered most that day?"), full="What route and purpose defined the original plan?", full_ja="最初の計画では、どんな経路と目的がありましたか？", safety="same-story-setting"),
            prompt("problem", "What went wrong", "起きた問題", "What was the travel mishap?", "どんな旅行トラブルが起きましたか？", ("When did it become clear?", "What made it difficult?"), full="Which disruption changed the trip, and when did the traveller recognize it?", full_ja="どんな問題が旅行を変え、旅行者はいつ気づきましたか？", safety="same-story-problem"),
            prompt("response", "The first response", "最初の対応", "What did the traveller do first?", "旅行者は最初に何をしましたか？", ("What information, if any, guided the response?", "What made that action seem like the best available step?"), full="How did the traveller assess the available action or options and respond first?", full_ja="旅行者は、取れる行動や選択肢をどう判断し、最初にどう対応しましたか？", safety="one-or-several-options"),
            prompt("company", "Alone or together", "一人か一緒か", "Was anyone travelling with them—or were they alone?", "誰かと一緒でしたか。それとも一人でしたか？", ("If together, did they agree?", "If alone, what support was available?"), full="Was the traveller alone or accompanied, and how did that affect the response?", full_ja="旅行者は一人でしたか、同行者がいましたか。それによって対応はどう変わりましたか？", safety="alone-or-accompanied"),
            prompt("ending", "In the end", "結局どうなったか", "How did the trip end?", "その旅行は結局どうなりましたか？", ("What was lost or saved?", "Did the traveller reach the destination?"), full="What resolution, compromise, or unfinished problem remained at the end?", full_ja="最後には、どんな解決、妥協、または未解決の問題が残りましたか？", safety="resolved-or-unresolved-ending"),
            prompt("hindsight", "A good story now?", "今はよい話か", "Is it a good story now, still stressful, or both?", "今ではよい話ですか、今もつらいですか、それとも両方ですか？", ("Which detail changed with time?", "What should not be minimized?"), full="Has the mishap become a good story, remained stressful, or taken on both meanings?", full_ja="そのトラブルはよい話になりましたか、今もつらいですか、それとも両方の意味を持ちましたか？", safety="nonbinary-hindsight"),
            prompt("flip", "Would you return?", "もう一度行くか", "Would the traveller go back to that place?", "旅行者はその場所へもう一度行きたいですか？", ("What would they change next time?", "What would make the return worthwhile?"), full="Under which conditions, if any, would the traveller return?", full_ja="どんな条件なら、旅行者はその場所へもう一度行きますか。それとも行きませんか？", safety="optional-return"),
        ],
    ),
    82: topic(
        slug="a-place-you-would-happily-visit-again", title="A place you would happily visit again",
        ko="기꺼이 다시 가고 싶은 곳", ja="また喜んで訪れたい場所",
        goal=("Let's explain a real, local, familiar, or imagined return visit.", "実際の場所、近場、身近な例、または想像上の再訪について話しましょう。"),
        article_title=("Why a place can be worth revisiting", "もう一度行く価値が生まれる理由"),
        articles=[
            ("A return visit is different from seeing a place for the first time.", "A return visit replaces first discovery with recognition, comparison, and deeper attention.", "再訪は、初めてその場所を見るのとは違います。", "再訪では、最初の発見が、気づき、比較、より深い注意に変わります。"),
            ("The visitor already knows what is worth their time.", "The visitor can spend less time getting oriented and more time on what mattered before.", "訪れる人は、何に時間を使う価値があるか知っています。", "訪れる人は場所を把握する時間を減らし、以前大切だったことにより多くの時間を使えます。"),
            ("A place may be attractive because of atmosphere rather than famous sights.", "A destination may invite return through atmosphere, rhythm, and ordinary details rather than landmarks.", "有名な名所ではなく、雰囲気が魅力の場所もあります。", "名所ではなく、雰囲気、リズム、日常の細部が再訪を誘う場所もあります。"),
            ("Food, weather, people, or pace may shape the memory.", "Food, climate, relationships, and pace combine into the remembered experience.", "食べ物、天気、人、過ごす速さが思い出を作ります。", "食事、気候、人間関係、過ごす速さが合わさって記憶を作ります。"),
            ("Returning with different people can create a different trip.", "A new companion can transform the same destination by changing priorities and attention.", "違う人と戻ると、別の旅行になることがあります。", "新しい同行者によって優先することや注目点が変わり、同じ場所でも別の旅行になります。"),
            ("Returning alone can reveal what belonged to the place itself.", "A solo return may separate attachment to the place from attachment to the earlier company.", "一人で戻ると、その場所自体の魅力が分かることがあります。", "一人で戻ると、場所への思いと以前の同行者への思いを分けられることがあります。"),
            ("Change may improve the place or remove what made it special.", "Development can renew a place while also erasing the quality that drew someone back.", "変化によって場所がよくなることも、特別さが失われることもあります。", "開発で場所が新しくなる一方、再訪したいと思わせた魅力が消えることもあります。"),
            ("Memory can make a return impossible to judge fairly.", "Nostalgia can create expectations no present visit could completely satisfy.", "思い出のため、再訪を公平に判断できないこともあります。", "懐かしさによって、今の旅行では満たせない期待が生まれることがあります。"),
            ("A good return does not have to copy the first visit.", "A successful return can honour the earlier experience without trying to reproduce it.", "よい再訪は、最初の旅行と同じである必要はありません。", "よい再訪は、以前の経験を大切にしながら、再現しようとしないものです。"),
            ("The strongest reason to return is often one unfinished curiosity.", "The desire to return often rests on one unfinished question, relationship, or experience.", "また行きたい一番の理由は、まだ知りたいことがあるからです。", "再訪したい気持ちは、まだ終わっていない疑問、関係、経験に支えられることがあります。"),
        ],
        prompts=[
            prompt("opening", "Worth revisiting", "再訪したい場所", BRIEF_OPENINGS[82], "明日にでも戻りたい、行ったことのある場所はどこですか？", ("If you have not travelled, which local place, familiar example, or imagined destination can we use?", "What draws the visitor back?"), full="Which place you have visited would you gladly return to tomorrow?", full_ja="訪れた場所のうち、明日にでも喜んで戻りたいのはどこですか？", safety="travelled-local-familiar-imagined"),
            prompt("setting", "The first visit", "最初の訪問", "For a real visit, when did it happen? For an imagined example, what conditions are we assuming?", "実際の訪問なら、いつでしたか。想像上の例なら、どんな条件を想定しますか？", ("If it was real, how long did the visit last?", "If it is imagined, what time or season would fit?"), full="When and under what circumstances did the real visit occur, or what circumstances define the imagined one?", full_ja="実際の訪問はいつ、どんな状況でしたか。それとも、想像上の訪問をどんな状況にしますか？", safety="real-or-imagined-setting"),
            prompt("appeal", "What made it special", "特別だった点", "For a real return, what makes the place worth revisiting? For an imagined first visit, what makes it worth choosing?", "実際の再訪なら、その場所にもう一度行く価値があるのはなぜですか。想像上の初訪問なら、なぜその場所を選びたいですか？", ("For a return, was it one remembered scene or the overall feeling?", "For a first visit, which feature creates the appeal?"), full="Which quality gives the real place lasting appeal, or makes the imagined destination worth a first visit?", full_ja="実際の場所にはどんな魅力が長く残っていますか。それとも、想像上の行き先を初めて訪れる価値はどこにありますか？", full_followups=("For a return, which remembered quality draws the visitor back?", "For a first visit, which evidence or feature creates the appeal?"), safety="real-return-or-imagined-first-appeal"),
            prompt("company", "Who was there", "誰といたか", "For a real visit, was the visitor alone or with someone? For an imagined one, who would go?", "実際の訪問なら一人でしたか、誰かと一緒でしたか。想像上なら誰が行きますか？", ("For a real visit, how did company or solitude affect it?", "For an imagined first visit, why would company or solitude suit the trip?"), full="For a real visit, how did company or solitude shape it? For an imagined first visit, who would go?", full_ja="実際の訪問なら、一人か同行者がいるかで経験はどう変わりましたか。想像上の初訪問なら、誰が行きますか？", full_followups=("For a real visit, would a return use the same arrangement?", "For an imagined first visit, how would company or solitude shape it?"), safety="real-or-imagined-company"),
            prompt("change", "Would it be the same?", "同じかどうか", "For a real return, what might be different? For an imagined first visit, what might differ from expectations?", "実際の再訪なら、何が違っていそうですか。想像上の初訪問なら、予想と何が違うかもしれませんか？", ("For a return, has the place or visitor changed?", "For a first visit, which expectation is least certain?"), full="How might a real return differ from before, or an imagined first visit differ from expectation?", full_ja="実際の再訪は以前とどう違いそうですか。それとも、想像上の初訪問は予想とどう違うかもしれませんか？", full_followups=("For a return, which change in the place or visitor matters?", "For a first visit, which expectation is least reliable?"), safety="real-return-or-imagined-first-change"),
            prompt("plan", "Do differently", "変えたいこと", "For a real return, what would the visitor do differently? For an imagined first visit, what would come first?", "実際の再訪なら、訪れる人は何を変えますか。想像上の初訪問なら、何を最初にしますか？", ("For a return, what would they skip or give more time?", "For a first visit, which priority would guide the plan?"), full="Which priority would change on a real return, or lead an imagined first visit?", full_ja="実際の再訪なら、どの優先事項を変えますか。それとも、想像上の初訪問では何を優先しますか？", full_followups=("For a return, what would receive less or more time?", "For a first visit, which choice would shape the plan?"), safety="real-return-or-imagined-first-plan"),
            prompt("risk", "Memory versus reality", "記憶と現実", "For a real return, could going back spoil the memory? For an imagined first visit, which expectation could mislead?", "実際の再訪なら、戻ることで思い出が損なわれる可能性はありますか。想像上の初訪問なら、どの期待が誤解につながりそうですか？", ("For a return, what expectation might be too high?", "For a first visit, what evidence would keep expectations reasonable?"), full="Could nostalgia distort a real return, or could an unsupported expectation distort an imagined first visit?", full_ja="懐かしさが実際の再訪をゆがめる可能性はありますか。それとも、根拠のない期待が想像上の初訪問への見方をゆがめそうですか？", full_followups=("For a return, which remembered quality might be impossible to reproduce?", "For a first visit, which evidence would keep expectations proportionate?"), safety="real-return-or-imagined-first-risk"),
            prompt("flip", "Bring one thing home", "持ち帰るもの", "What quality from that place would you bring into daily life?", "その場所のどんなよさを日常生活に取り入れたいですか？", ("Why that quality?", "How could it work at home?"), full="Which element of that place would improve your ordinary life?", full_ja="その場所のどんな要素が、普段の生活をよりよくしますか？", safety="general-transfer-flip"),
        ],
    ),
    83: topic(
        slug="what-you-wanted-to-be-as-a-child", title="What you wanted to be as a child",
        ko="어릴 때 되고 싶었던 것", ja="子どもの頃になりたかったもの",
        goal=("Let's trace a real, remembered, or general childhood ambition.", "実際の記憶、思い出せる例、または一般的な子どもの夢をたどりましょう。"),
        article_title=("What childhood ambitions reveal", "子どもの夢が表すもの"),
        articles=[
            ("A childhood ambition often begins with one visible part of a job.", "A childhood ambition often grows from one vivid but incomplete image of adult work.", "子どもの夢は、仕事の目立つ一部分から始まることがよくあります。", "子どもの夢は、大人の仕事についての鮮明だが不完全なイメージから生まれます。"),
            ("Children may admire the uniform, tools, skill, or attention.", "A uniform, special tool, admired skill, or public attention may carry the appeal.", "制服、道具、技術、注目に憧れる子どももいます。", "制服、特別な道具、尊敬される技術、人からの注目が魅力になることがあります。"),
            ("They rarely know the daily routine behind the role.", "The ordinary routine, training, and compromise behind the role are usually invisible.", "その仕事の日常までは、ほとんど知りません。", "その役割の裏にある日常、訓練、妥協はたいてい見えません。"),
            ("Family, school, stories, and media provide possible futures.", "Family examples, school experiences, fiction, and media expand or narrow imaginable futures.", "家族、学校、物語、メディアが将来の選択肢を示します。", "家族の例、学校での経験、作品、メディアが、想像できる将来を広げたり狭めたりします。"),
            ("The dream may disappear after new information or a new interest.", "An ambition may fade when reality becomes clearer or another identity becomes possible.", "新しい情報や興味によって、その夢が消えることもあります。", "現実が明確になったり別の自分を想像できたりすると、夢が薄れることがあります。"),
            ("Some ambitions survive in a smaller or different form.", "A childhood ambition may survive indirectly through a related skill, value, or hobby.", "小さく形を変えて残る夢もあります。", "子どもの夢が、関連する技術、価値観、趣味として間接的に残ることもあります。"),
            ("Not remembering a dream is also ordinary.", "Some people had no fixed ambition, changed it constantly, or simply do not remember.", "夢を覚えていないことも普通です。", "決まった夢がなかった人、何度も変えた人、覚えていない人もいます。"),
            ("Adult work does not have to fulfil a childhood plan.", "A satisfying adult life need not confirm a prediction made with childhood knowledge.", "大人の仕事が、子どもの計画を実現する必要はありません。", "満足できる大人の生活は、子どもの知識で立てた予想どおりになる必要はありません。"),
            ("Looking back can reveal the value hidden inside the job title.", "The old title may conceal a durable wish to help, create, explore, or be recognized.", "振り返ると、職業名の中に隠れていた価値が見えます。", "昔の職業名には、人を助けたい、作りたい、探検したい、認められたいという願いが隠れていることがあります。"),
            ("That value may still connect the child to the adult.", "Even when the occupation changed, the underlying value may connect childhood and adulthood.", "その価値が、今も子どもと大人の自分を結んでいるかもしれません。", "職業が変わっても、その根底の価値が子ども時代と大人の今を結ぶことがあります。"),
        ],
        prompts=[
            prompt("opening", "A childhood ambition", "子どもの夢", BRIEF_OPENINGS[83], "十歳の頃、何になりたかったですか？", ("If you do not remember, which common childhood ambition or changing set of ideas can we use?", "What made it appealing?"), full="What was your childhood ambition around the age of ten?", full_ja="十歳ごろ、将来何になりたいと思っていましたか？", safety="remembered-changing-or-general"),
            prompt("image", "What appealed", "魅力だった点", "What part of that role appealed to the child?", "その役割のどんなところが子どもに魅力的でしたか？", ("Was it a skill, image, or value?", "What did the child not know yet?"), full="Which visible feature or underlying value made the role attractive?", full_ja="どんな目に見える特徴や根底の価値が、その役割を魅力的にしましたか？", safety="same-ambition-appeal"),
            prompt("source", "Where it came from", "きっかけ", "Where did the idea come from?", "その考えはどこから来ましたか？", ("Was there a person, story, or experience?", "Did anyone encourage it?"), full="Which person, experience, or story shaped the ambition?", full_ja="どんな人、経験、物語がその夢を形作りましたか？", safety="same-ambition-source"),
            prompt("change", "When it changed", "変わった時期", "When did the idea change, fade, or stay the same?", "その考えはいつ変わりましたか、消えましたか、それとも同じままでしたか？", ("If it changed or faded, what new information mattered?", "If it remained, what kept it alive?"), full="When and why did the ambition shift, fade, or remain?", full_ja="その夢はいつ、なぜ変わりましたか、消えましたか、それとも残りましたか？", safety="changed-faded-or-remained"),
            prompt("replacement", "What came next", "次の夢", "What replaced that idea, if anything?", "その考えの代わりに、何か新しい夢が生まれましたか？", ("If a new idea followed, was it related?", "If nothing replaced it, what took its place in the person's attention?"), full="Which ambition or direction followed, if there was one?", full_ja="次にどんな夢や方向が生まれましたか。それとも特にありませんでしたか？", safety="replacement-or-none"),
            prompt("connection", "Still connected", "今とのつながり", "Is the person's life now connected to that old dream in any way?", "その人の今の生活は、昔の夢と何かつながっていますか？", ("If a connection remains, which skill or value is it?", "If none remains, what is completely different?"), full="Does any skill or value from the childhood ambition survive now, or is there no connection?", full_ja="子どもの夢にあった技能や価値は今も残っていますか。それとも、つながりはありませんか？", safety="connection-or-none"),
            prompt("hindsight", "The realistic view", "現実的な見方", "What do you understand about that job now?", "今、その仕事について何を理解していますか？", ("Which part was missing from the childhood picture?", "Would you still try it for one day?"), full="How does adult knowledge complicate the childhood image of that work?", full_ja="大人になって得た知識は、その仕事への子どものイメージをどう複雑にしますか？", safety="general-job-hindsight"),
            prompt("flip", "Ten-year-old's verdict", "十歳の子どもの評価", "What might the child in the chosen example think of that person's adult life?", "選んだ例の子どもは、その人の大人になった生活をどう思うでしょうか？", ("What would surprise the child?", "What might the child admire or dislike?"), full="How might the childhood self in the chosen example judge or misunderstand the adult life that followed?", full_ja="選んだ例の子どもの頃の自分は、その後の大人の生活をどう評価し、どこを誤解しそうですか？", safety="same-example-imagined-child"),
        ],
    ),
    84: topic(
        slug="one-day-you-would-go-back-to", title="One day you would go back to", ko="돌아가고 싶은 하루", ja="戻ってみたい一日",
        goal=("Let's explore a real, familiar, historical, or invented day without forcing regret.", "実際の記憶、身近な話、歴史上、または想像上の一日を、後悔を前提にせず考えましょう。"),
        article_title=("What we seek in one past day", "過去の一日に求めるもの"),
        articles=[
            ("Wanting to revisit a day does not always mean wanting to change it.", "The wish to revisit a day may seek understanding or presence rather than revision.", "一日に戻りたいからといって、変えたいとは限りません。", "一日に戻りたい気持ちは、修正より理解やその場にいることを求める場合があります。"),
            ("Someone may want to notice details they missed the first time.", "A second view could recover details that stress, youth, or distraction originally hid.", "最初に見落とした細部に気づきたい人もいます。", "もう一度見れば、緊張、若さ、気の散りで見えなかった細部を取り戻せるかもしれません。"),
            ("A joyful day can be worth reliving without any regret.", "A joyful day may be worth reliving simply because attention was divided the first time.", "後悔がなくても、幸せな一日をもう一度体験したいことがあります。", "最初は注意が散っていたため、幸せな一日をもう一度味わいたいことがあります。"),
            ("A difficult day may hold an unanswered question.", "A painful day may attract attention because one question or conversation remained unfinished.", "つらい一日には、答えのない疑問が残っていることがあります。", "苦しい一日が気になるのは、疑問や会話が一つ終わらないままだからかもしれません。"),
            ("Changing one event could also change later events.", "Intervening in one event could alter consequences the visitor values now.", "一つの出来事を変えると、その後も変わるかもしれません。", "一つの出来事に介入すると、今大切にしている結果まで変わる可能性があります。"),
            ("Watching without acting may still be emotionally difficult.", "Choosing only to observe does not remove the emotional cost of returning.", "何もしないで見るだけでも、気持ちの上では難しいかもしれません。", "観察するだけでも、戻ることの感情的な負担はなくなりません。"),
            ("The imagined visit needs a clear boundary: one day and one purpose.", "A bounded thought experiment becomes clearer when it fixes one day, one purpose, and no permanent stay.", "想像の旅には、一日と一つの目的という境界が必要です。", "一日、一つの目的、残らないという条件を決めると、想像が明確になります。"),
            ("Some people would choose a public day rather than a private memory.", "A historical or familiar public day can offer distance from private experience.", "個人的な記憶ではなく、公の一日を選ぶ人もいます。", "歴史上または公に知られた一日なら、個人的な経験から距離を取れます。"),
            ("Others would not return because the present matters more.", "Refusing the trip can express acceptance rather than lack of imagination.", "今のほうが大切で、戻らない人もいます。", "戻らない選択は、想像力の不足ではなく受け入れを表すことがあります。"),
            ("The choice reveals what kind of understanding feels unfinished.", "The selected day often reveals which relationship, choice, or feeling still invites attention.", "選んだ一日は、どんな理解がまだ終わっていないかを表します。", "選ばれた一日は、どんな関係、選択、感情が今も注意を求めているかを表します。"),
        ],
        prompts=[
            prompt("opening", "One day only", "一日だけ", BRIEF_OPENINGS[84], "過去へ一日だけ行けるなら、どの日を選びますか？", ("Would you choose a personal, familiar, historical, or invented day—or decline the trip?", "Why that route?"), full="If you could revisit exactly one day in the past, which day would you choose?", full_ja="過去の一日だけを再び訪れられるなら、どの日を選びますか？", safety="personal-familiar-historical-invented-decline"),
            prompt("setting", "The chosen day", "選んだ一日", "If a day was chosen, what happened then? If not, what makes staying in the present preferable?", "一日を選んだなら何が起きましたか。選ばないなら、今にいるほうがよいのはなぜですか？", ("If entering the day, where would the visitor arrive?", "If declining, which part of the present matters most?"), full="Which events define the selected day, or which present value explains declining the trip?", full_ja="選んだ一日を形作る出来事は何ですか。それとも、どんな現在の価値から過去への旅を断りますか？", safety="selected-day-or-decline"),
            prompt("purpose", "Why return", "戻る目的", "If the visitor went, what would they seek? If not, what would they protect?", "行くなら何を求めますか。行かないなら何を守りたいですか？", ("For a visit, is the goal joy, understanding, or something else?", "For a refusal, which boundary matters?"), full="What would the visitor seek by reliving the day, or preserve by declining to enter it?", full_ja="その日を再体験して何を求めますか。それとも、その日に入らないことで何を守りますか？", safety="visit-purpose-or-refusal"),
            prompt("choice", "Change or observe", "変えるか見るか", "Would the visitor change something, only watch, or decline the trip?", "その人は何かを変えますか、見るだけですか、それとも旅を断りますか？", ("If entering, what could change afterward?", "If declining, which boundary would that protect?"), full="Would the visitor intervene, observe, or refuse to enter the day?", full_ja="その人は介入しますか、観察しますか、それともその日に入らないことを選びますか？", safety="intervene-observe-or-decline"),
            prompt("person", "Someone there", "その日にいる人", "Would the day involve seeing someone, focus on something else, or not be entered?", "その日は誰かに会うことが中心ですか、別のことが中心ですか、それともその日に入りませんか？", ("If a person matters, what would their presence change?", "If no person or no visit is involved, what carries the meaning?"), full="Would the day involve seeing someone, remain independent of any person, or be declined entirely?", full_ja="その日は誰かに会うことが中心ですか、人とは関係なく意味がありますか、それとも訪問自体を断りますか？", safety="person-no-person-or-decline"),
            prompt("message", "What to say", "伝える言葉", "Would the visitor say something, stay silent, or not make the visit?", "その人は何か言いますか、黙っていますか、それとも訪問しませんか？", ("If speaking, would the message be understood?", "If silent or absent, what makes that choice fit?"), full="Which message, question, silence, or refusal to visit would fit?", full_ja="どんな言葉、質問、沈黙、または訪問しない選択が合いますか？", safety="message-silence-or-no-visit"),
            prompt("effect", "Would it help?", "役に立つか", "If the visit happened, would it help, hurt, or change nothing? If declined, what would that preserve?", "訪問したなら、役立ちますか、つらくしますか、それとも何も変えませんか。断ったなら何を守れますか？", ("For a visit, what could return to the present?", "For a refusal, what could remain undisturbed?"), full="Would revisiting provide clarity, create difficulty, leave the present unchanged, or be less useful than declining?", full_ja="再訪は理解を与えますか、難しさを生みますか、現在を変えませんか、それとも断るほうがよいですか？", safety="visit-effect-or-decline-benefit"),
            prompt("flip", "Stay in the present", "今に残る理由", "What is one good reason not to go back?", "過去へ戻らないほうがよい理由を一つ挙げるとしたら何ですか？", ("What deserves attention now?", "Can acceptance be more useful than an answer?"), full="What makes remaining in the present more valuable than revisiting the past?", full_ja="過去を再訪するより、今にいるほうが価値があるのはなぜですか？", safety="present-focused-flip"),
        ],
    ),
    85: topic(
        slug="a-turning-point-in-your-life", title="A turning point in your life", ko="인생의 전환점", ja="人生の転機",
        goal=("Let's examine a personal, public, fictional, or general turning point.", "個人的な出来事、公の例、作品、または一般的な人生の転機を考えましょう。"),
        article_title=("How a turning point becomes visible", "転機が見えるまで"),
        articles=[
            ("A turning point changes which future becomes possible.", "A turning point redirects which futures remain available or imaginable.", "転機は、どんな将来が可能かを変えます。", "転機は、どんな将来が可能で想像できるかを変えます。"),
            ("The moment may look ordinary while it is happening.", "Its importance may remain invisible until later events reveal the new direction.", "その瞬間は、起きている間は普通に見えることがあります。", "その重要性は、後の出来事が新しい方向を示すまで見えないことがあります。"),
            ("A decision, accident, meeting, loss, or opportunity can redirect a life.", "Decisions, accidents, relationships, losses, and opportunities can all redirect a life.", "決断、事故、出会い、喪失、機会が人生を変えることがあります。", "決断、事故、人間関係、喪失、機会はどれも人生の方向を変え得ます。"),
            ("Some changes are chosen, while others require adaptation.", "Some turning points express agency; others force a response to circumstances.", "自分で選ぶ変化もあれば、対応を求められる変化もあります。", "主体的に選ぶ転機もあれば、状況への対応を迫る転機もあります。"),
            ("Other people may influence the choice without deciding it.", "Advice or pressure may shape a choice without fully determining it.", "ほかの人が、決めるのではなく選択に影響することもあります。", "助言や圧力が、完全に決めることなく選択を形作る場合があります。"),
            ("The alternative path is always partly imagined.", "The life not taken can be considered, but never known with certainty.", "別の道は、いつも一部は想像です。", "選ばなかった人生は考えられても、確実に知ることはできません。"),
            ("Luck and decision often work together.", "Chance creates conditions, while decisions shape the response to them.", "運と決断は、しばしば一緒に働きます。", "偶然が条件を作り、決断がそれへの対応を形作ります。"),
            ("A positive outcome does not make the transition easy.", "Later gratitude does not erase uncertainty or loss during the transition.", "よい結果でも、変化が簡単だったとは限りません。", "後の感謝が、転機の不安や喪失を消すわけではありません。"),
            ("A difficult outcome does not prove the original choice was foolish.", "An adverse result does not automatically make the earlier decision irrational.", "難しい結果でも、最初の選択が愚かだったとは限りません。", "悪い結果でも、以前の決断が不合理だったとは自動的に言えません。"),
            ("Naming a turning point helps organize a complicated story.", "Calling something a turning point gives structure to a life that felt uncertain while lived.", "転機と名付けると、複雑な話を整理できます。", "転機と呼ぶことで、当時は不確かだった人生に構造を与えられます。"),
        ],
        prompts=[
            prompt("opening", "A different direction", "別の方向", BRIEF_OPENINGS[85], "人生が全く別の方向へ進む可能性があった瞬間はありますか？", ("Which personal, public, fictional, or general example can we use while keeping private details private?", "What changed direction?"), full="Was there a moment when your life—or a chosen example—could have taken a completely different direction?", full_ja="自分の人生、または選んだ例が、全く別の方向へ進む可能性があった瞬間はありますか？", safety="personal-public-fictional-general"),
            prompt("event", "What happened", "起きたこと", "What happened at that turning point?", "その転機では何が起きましたか？", ("What was happening just before it?", "Which detail mattered most?"), full="Which event or decision created the turning point?", full_ja="どんな出来事や決断が転機を作りましたか？", safety="same-example-event"),
            prompt("awareness", "Did they know?", "気づいていたか", "Did the person know it was important at the time?", "その人は当時、それが重要だと気づいていましたか？", ("When did its importance become clear?", "What sign was missed?"), full="Did the person recognize the moment's significance then or only in retrospect?", full_ja="その人はその瞬間の重要性に当時気づきましたか、それとも後からですか？", safety="same-example-awareness"),
            prompt("alternative", "The other path", "別の道", "What was the realistic alternative?", "現実的な別の選択肢は何でしたか？", ("What might have changed?", "What probably would have stayed the same?"), full="Which plausible alternative path was available?", full_ja="どんな現実的な別の道がありましたか？", safety="bounded-counterfactual"),
            prompt("influence", "People or circumstances", "人か状況か", "Did a person influence the direction, or was it an accident, loss, or other circumstance?", "誰かが方向に影響しましたか。それとも事故、喪失、ほかの状況でしたか？", ("If a person was involved, what did they contribute?", "If no one decided it, which circumstance redirected the path?"), full="Did another person shape the direction, or did an accident, loss, or circumstance do so without a decision-maker?", full_ja="ほかの人が方向を形作りましたか。それとも、決定した人のいない事故、喪失、状況が方向を変えましたか？", safety="person-or-no-decision-maker"),
            prompt("difference", "Life on the other path", "別の人生", "What might be different now on the other path?", "別の道なら、今は何が違っていたでしょうか？", ("Which claim is fairly certain?", "Which part is pure imagination?"), full="Which present conditions might plausibly differ on the alternative path?", full_ja="別の道なら、今のどんな状況が違っていた可能性がありますか？", safety="bounded-present-counterfactual"),
            prompt("judgment", "Luck or decision", "運か決断か", "Was the turning point mostly luck, a decision, or both?", "その転機は主に運、決断、それとも両方でしたか？", ("Which part was controllable?", "What could nobody predict?"), full="How should responsibility be divided between chance and deliberate choice?", full_ja="偶然と意図的な選択の間で、責任をどう分けて考えますか？", safety="balanced-causation"),
            prompt("flip", "Recognizing change", "変化に気づく", "How can someone notice a turning point while it is happening?", "転機が起きている最中に、どうすれば気づけますか？", ("Which signals deserve attention?", "Can too much analysis be harmful?"), full="Which signals suggest that an ordinary moment may be redirecting a life?", full_ja="普通の瞬間が人生の方向を変えていると分かる兆候は何ですか？", safety="general-reflective-flip"),
        ],
    ),
    86: topic(
        slug="what-you-were-like-as-a-child", title="What you were like as a child", ko="어릴 때의 나", ja="子どもの頃の自分",
        goal=("Let's compare a remembered, reported, or general childhood self with the present.", "記憶、自分について聞いた話、または一般的な子どもの例を今と比べましょう。"),
        article_title=("How childhood identity is remembered", "子どもの頃の自分をどう覚えるか"),
        articles=[
            ("Childhood identity comes from memory and other people's stories.", "Our childhood identity is reconstructed from personal memory and other people's accounts.", "子どもの頃の自分は、自分の記憶と人の話から作られます。", "子どもの頃の自分像は、自分の記憶とほかの人の話から再構成されます。"),
            ("The child apparently acted differently in different places, according to other people's stories.", "The same child apparently seemed quiet at school and lively at home in one person's account.", "人から聞いた話によると、その子どもは場所によって違う行動をしていたそうです。", "ある人の話では、同じ子どもが学校では静かで、家では活発に見えたそうです。"),
            ("One adjective cannot describe every situation.", "A single trait cannot capture behaviour across every relationship and setting.", "一つの形容詞で、すべての場面を説明することはできません。", "一つの特徴だけでは、あらゆる関係や状況での行動を表せません。"),
            ("Family stories may repeat until they feel like facts.", "Repeated family stories can harden into an identity claim that nobody rechecks.", "家族の話は、繰り返されるうちに事実のようになります。", "家族の話は繰り返され、誰も確かめない人物像として固まることがあります。"),
            ("The child may remember the same event differently.", "The child's memory may preserve emotion while adults remember visible behaviour.", "子ども本人は、同じ出来事を違って覚えているかもしれません。", "子どもの記憶は感情を残し、大人は目に見えた行動を覚えていることがあります。"),
            ("A specific memory is more useful than a broad label.", "One concrete scene often reveals more than a general label such as shy or difficult.", "大まかな呼び方より、一つの具体的な記憶のほうが役立ちます。", "内気、扱いにくいといった一般的な呼び方より、具体的な一場面のほうが多くを示します。"),
            ("Some traits remain while their expression changes.", "A stable trait may survive in a more controlled or socially acceptable form.", "特徴が残っていても、表れ方が変わることがあります。", "同じ特徴が、より調整された社会的に受け入れられる形で残ることがあります。"),
            ("Other traits disappear when the environment changes.", "Behaviour may fade when the conditions that produced it no longer exist.", "環境が変わると、消える特徴もあります。", "その行動を生んだ条件がなくなると、行動も消えることがあります。"),
            ("Not everyone has family stories or clear childhood memories.", "Some people lack reliable family accounts, clear memories, or safe access to either.", "家族の話や明確な子どもの記憶がない人もいます。", "信頼できる家族の話、明確な記憶、そのどちらにも安心して触れられない人もいます。"),
            ("A fair description leaves room for more than one version.", "A fair childhood portrait holds several perspectives without forcing one final verdict.", "公平な説明には、複数の見方が入ります。", "公平な子ども時代の人物像は、一つの結論を押しつけず複数の視点を保ちます。"),
        ],
        prompts=[
            prompt("opening", "What the stories say", "人から聞く昔の自分", BRIEF_OPENINGS[86], "家族は、子どもの頃の自分をどんな子だったと言いますか？", ("If family accounts are unavailable, which memory or general child example can we use?", "Which description is most repeated?"), full="How do people who knew you—or your own memories—describe you as a child?", full_ja="当時を知る人や自分の記憶では、子どもの頃の自分はどんな子でしたか？", safety="family-memory-or-general"),
            prompt("source", "Who says so", "誰の話か", "Who gives that description, or where does the example come from?", "その説明は誰から聞きましたか。それとも、その例はどこから来ましたか？", ("Were they present often?", "Could they see every side?"), full="Whose perspective supports the description, and what could that person observe?", full_ja="誰の視点がその説明を支え、その人は何を見ることができましたか？", safety="same-route-source"),
            prompt("agreement", "Do you agree?", "自分の見方", "Does the person agree with that picture?", "その人は、その人物像に同意しますか？", ("Which part feels accurate?", "Which part is missing?"), full="Does the person accept, qualify, or reject that childhood portrait?", full_ja="その人は子どもの頃の人物像を受け入れますか、条件を付けますか、それとも否定しますか？", safety="nonbinary-agreement"),
            prompt("scene", "One memory", "一つの記憶", "Which specific memory shows that trait—or challenges it?", "どの具体的な記憶が、その特徴を示しますか。それとも反対を示しますか？", ("What happened?", "Who else was involved, if anyone?"), full="Which scene best supports or complicates the description?", full_ja="どの場面が、その説明を最もよく支えたり複雑にしたりしますか？", safety="specific-or-general-scene"),
            prompt("setting", "Different places", "場所による違い", "Was the child different across settings, or broadly the same?", "その子どもは場所によって違いましたか。それとも、だいたい同じでしたか？", ("If behaviour changed, where and why?", "If it stayed stable, what remained consistent?"), full="Did setting and relationship change the child's behaviour, or did the description remain stable across them?", full_ja="場所や人間関係によって行動は変わりましたか。それとも、その特徴はどこでも変わりませんでしたか？", safety="different-or-stable-settings"),
            prompt("continuity", "Still true?", "今も同じか", "Which parts remain, changed, disappeared, or are unknown now?", "今、その特徴のどの部分が残り、変わり、消え、または分からないままですか？", ("If something remains, is it expressed differently?", "If nothing remains or is known, what changed or is uncertain?"), full="Does any childhood trait persist in the chosen example, or did it change, disappear, or remain unknown?", full_ja="選んだ例では子どもの頃の特徴が残っていますか。それとも変わりましたか、消えましたか、分かりませんか？", safety="persists-changes-disappears-or-unknown"),
            prompt("fairness", "A fair label", "公平な表現", "Which childhood labels are too simple or unfair?", "子どもへのどんな呼び方は、単純すぎたり不公平だったりしますか？", ("What context is usually missing?", "How could the label be rewritten?"), full="Which common childhood labels hide more context than they reveal?", full_ja="子どもへの一般的な呼び方のうち、分かることより隠すことが多いのはどれですか？", safety="general-label-critique"),
            prompt("flip", "The child's view", "子どもから見た今", "What might the child in the chosen example think of that person's adult life?", "選んだ例の子どもは、その人の大人になった生活をどう思うでしょうか？", ("What might surprise the child?", "What might feel familiar?"), full="How might the childhood self in the chosen example interpret the adult life that followed?", full_ja="選んだ例の子どもの頃の自分は、その後の大人の生活をどう受け止めるでしょうか？", safety="same-example-imagined-child"),
        ],
    ),
    87: topic(
        slug="a-childhood-place-that-no-longer-exists", title="A childhood place that no longer exists", ko="이제는 사라진 어린 시절의 장소", ja="もう存在しない子どもの頃の場所",
        goal=("Let's describe a personal, local, public, or imagined place that disappeared.", "個人的な場所、近所、公の場所、または想像上の消えた場所について話しましょう。"),
        article_title=("What disappears with a place", "場所とともに消えるもの"),
        articles=[
            ("A childhood place can be small and still hold a large memory.", "A physically ordinary place can carry an unusually dense layer of childhood memory.", "子どもの頃の場所は小さくても、大きな記憶を持つことがあります。", "見た目は普通の場所でも、子ども時代の濃い記憶を抱えることがあります。"),
            ("It may be a shop, field, school, house, or meeting spot.", "The place may be commercial, natural, institutional, domestic, or simply where people gathered.", "店、空き地、学校、家、待ち合わせ場所かもしれません。", "店、自然、施設、家、または人が集まっただけの場所かもしれません。"),
            ("Children remember what they did there more than its design.", "Activity and relationship often survive in memory more strongly than architecture.", "子どもは、場所の形より、そこで何をしたかを覚えています。", "建物の形より、そこでの行動や人間関係のほうが強く記憶に残ります。"),
            ("A place may close slowly or be demolished without warning.", "A place may decline gradually or be demolished before former users notice the threat.", "場所はゆっくり閉まることも、突然取り壊されることもあります。", "場所は徐々に衰えることも、昔の利用者が気づく前に取り壊されることもあります。"),
            ("People often learn about the change after it has happened.", "Former visitors may discover the loss only when they try to return.", "変わった後に、そのことを知る人も多いです。", "昔の利用者は、戻ろうとしたとき初めて失われたと知ることがあります。"),
            ("The replacement may be useful and still feel disappointing.", "A useful replacement can serve the present while failing to carry the earlier meaning.", "新しい場所が便利でも、残念に感じることがあります。", "新しい場所は今の役に立っても、以前の意味を受け継げないことがあります。"),
            ("Photographs preserve appearance but not sound, smell, or routine.", "Images preserve surfaces while losing sound, smell, movement, and ordinary repetition.", "写真は見た目を残しますが、音、匂い、日常までは残しません。", "写真は表面を残しても、音、匂い、動き、日々の繰り返しを失います。"),
            ("Rebuilding a copy would not recreate the same childhood.", "Physical reconstruction cannot restore the age, relationships, or expectations surrounding the place.", "同じものを建て直しても、同じ子ども時代は戻りません。", "物理的に再現しても、その場所を囲んだ年齢、人間関係、期待は戻りません。"),
            ("Not every lost place needs to be preserved forever.", "Communities must balance memory with safety, housing, access, and changing needs.", "失われた場所をすべて永久に残す必要はありません。", "地域は、記憶と、安全、住居、利用しやすさ、変化するニーズとのバランスを取る必要があります。"),
            ("Telling the story can preserve what the map no longer shows.", "Narrating the place can preserve social meaning that no current map records.", "話をすることで、地図にない場所の意味を残せます。", "その場所を語ることで、今の地図にはない社会的な意味を残せます。"),
        ],
        prompts=[
            prompt("opening", "A vanished place", "なくなった場所", BRIEF_OPENINGS[87], "子どもの頃の場所で、今はもう存在しないところはありますか？", ("If none comes to mind, which changed local or public place, or imagined example, can we use?", "What kind of place was it?"), full="Which place from childhood, if any, no longer exists?", full_ja="子どもの頃の場所で、今はもう存在しないところがあるとすれば、どこですか？", safety="personal-local-public-imagined"),
            prompt("picture", "What it was", "どんな場所か", "What did the place look and feel like?", "その場所はどんな見た目で、どんな感じでしたか？", ("Which detail was easiest to recognize?", "What sound or smell belonged there?"), full="Which physical and sensory details defined the place?", full_ja="どんな見た目や感覚の細部が、その場所を特徴づけていましたか？", safety="same-place-description"),
            prompt("activity", "What happened there", "そこでしていたこと", "What did people do there?", "人々はそこで何をしていましたか？", ("Who used the place?", "What ordinary routine happened there?"), full="Which activities and relationships gave the place meaning?", full_ja="どんな活動や人間関係が、その場所に意味を与えていましたか？", safety="people-or-general-activity"),
            prompt("loss", "When it went", "なくなった時期", "When and how did the place disappear?", "その場所はいつ、どのようになくなりましたか？", ("Did it close, move elsewhere, change beyond recognition, or get demolished?", "Was there warning?"), full="How did the place disappear—through closure, relocation, major change, or demolition—and when?", full_ja="その場所は、閉鎖、移転、大きな変化、取り壊しのどれによって、いつなくなりましたか？", safety="four-disappearance-routes"),
            prompt("awareness", "Did anyone notice?", "気づいていたか", "Did the person know it was disappearing at the time?", "その人は当時、その場所がなくなると知っていましたか？", ("How did they find out?", "Would they have visited once more?"), full="Did the person recognize the final visit, or learn about the loss later?", full_ja="その人は最後の訪問だと気づきましたか。それとも後で失われたと知りましたか？", safety="noticed-or-later"),
            prompt("replacement", "What is there now", "今あるもの", "What is there now, if anything?", "今はそこに何がありますか。それとも何もありませんか？", ("If something replaced it, is the replacement useful?", "If nothing replaced it, does any trace remain?"), full="What, if anything, replaced the place, and what meaning does the new use—or empty space—carry?", full_ja="その場所に代わったものはありますか。新しい使い方、または何もない空間にはどんな意味がありますか？", safety="replacement-or-none"),
            prompt("feeling", "Does it bother you?", "どう感じるか", "Does the change feel sad, reasonable, neutral, or mixed?", "その変化を悲しいと思いますか、妥当だと思いますか、特に良くも悪くも感じませんか、それとも複雑な気持ちですか？", ("If it feels sad or mixed, what feels lost?", "If it feels reasonable or neutral, what makes that the honest response?"), full="Does the change feel regrettable, justified, neutral, or emotionally mixed?", full_ja="その変化を残念だと思いますか、妥当だと思いますか、特に良くも悪くも感じませんか、それとも複雑な気持ちですか？", full_followups=("If regret or mixed feelings remain, what carries the loss?", "If it feels justified or neutral, what supports that response?"), safety="regrettable-justified-neutral-or-mixed"),
            prompt("flip", "Preserve one detail", "一つ残すなら", "If one detail could be preserved, what should it be—or would you preserve nothing?", "一つだけ残せるなら何を残しますか。それとも何も残しませんか？", ("If you chose something, who would value it?", "If you chose nothing, why is preservation unnecessary?"), full="Which single feature or story deserves preservation, if any, or should nothing be kept?", full_ja="残す価値のある特徴や物語が一つあるとすれば何ですか。それとも何も残す必要はありませんか？", safety="preserve-one-or-none"),
        ],
    ),
    88: topic(
        slug="something-you-were-completely-wrong-about", title="Something you were completely wrong about", ko="완전히 잘못 알고 있던 것", ja="完全に間違っていたこと",
        goal=("Let's examine a personal, public, or general misconception and its correction.", "個人的な思い込み、公に知られた例、または一般的な誤解と、その修正について話しましょう。"),
        article_title=("How certainty survives bad information", "誤った情報でも確信が続く理由"),
        articles=[
            ("A misconception can feel true when it fits an existing story.", "A misconception becomes convincing when it fits a coherent story we already accept.", "誤解は、すでにある話に合うと本当のように感じられます。", "誤解は、すでに受け入れている筋の通った話に合うと説得力を持ちます。"),
            ("Repetition can create confidence without creating evidence.", "Repeated exposure increases familiarity, which can be mistaken for evidence.", "繰り返し聞くと、根拠がなくても自信が生まれます。", "繰り返し触れると親しみが増し、それを根拠と間違えることがあります。"),
            ("People may forget where the original claim came from.", "Source memory often fades while the claim itself remains available.", "元の話をどこで聞いたか忘れることもあります。", "情報源の記憶が薄れても、主張そのものは残ることがあります。"),
            ("A trusted person can pass on a mistake without intending harm.", "Trust can carry inaccurate information even when nobody intends to mislead.", "信頼する人が、悪気なく間違いを伝えることがあります。", "誰もだますつもりがなくても、信頼によって不正確な情報が広がります。"),
            ("Correct information may first feel less believable than the old idea.", "Correction can feel unstable because it disrupts a familiar explanation.", "正しい情報が、最初は昔の考えより信じにくいこともあります。", "訂正は慣れた説明を崩すため、最初は不安定に感じられます。"),
            ("Embarrassment can make someone defend the mistake longer.", "The threat of embarrassment can turn a factual correction into a defense of identity.", "恥ずかしさのため、間違いを長く守ってしまうことがあります。", "恥をかく不安によって、事実の訂正が自分らしさを守る行動に変わることがあります。"),
            ("A good correction provides evidence and room to change calmly.", "Effective correction combines verifiable evidence with a face-saving path to revision.", "よい訂正には、根拠と落ち着いて変わる余地があります。", "効果的な訂正には、確認できる根拠と、面目を保って考え直す道があります。"),
            ("Finding one mistake should lead to better checking, not certainty that everything else is wrong.", "Discovering one error should encourage better calibration, not certainty that every other claim is false.", "一つの間違いを見つけたら、ほかもすべて間違いだと決めつけず、よりよく確かめるべきです。", "一つの誤りを知ったら、ほかの主張もすべて誤りだと決めつけず、確信の度合いをより適切に調整すべきです。"),
            ("People can learn to state how sure they are and why.", "Confidence becomes more reliable when it includes source, evidence, and uncertainty.", "どのくらい確かで、なぜそう思うかを言えるようになります。", "情報源、根拠、不確かさを含めると、確信はより信頼できるものになります。"),
            ("Changing a belief is a strength when evidence changes.", "Revising a belief in response to evidence is intellectual flexibility, not failure.", "根拠が変わったときに考えを変えるのは強さです。", "根拠に応じて考えを変えることは、失敗ではなく知的な柔軟さです。"),
        ],
        prompts=[
            prompt("opening", "Completely wrong", "完全な思い違い", BRIEF_OPENINGS[88], "何年も信じていたのに、完全に間違いだと分かったことは何ですか？", ("If no personal example comes to mind, which common, public, or invented misconception can we use?", "How certain was the person?"), full="Which belief held for years turned out to be completely mistaken?", full_ja="何年も信じていたことのうち、完全な誤りだと分かったものは何ですか？", safety="personal-common-public-invented"),
            prompt("belief", "The old idea", "以前の考え", "What exactly did the person believe?", "その人は正確には何を信じていましたか？", ("Was the belief specific?", "What did it explain?"), full="What precise claim made up the misconception?", full_ja="どんな具体的な主張が、その誤解を作っていましたか？", safety="same-belief-definition"),
            prompt("duration", "How long", "信じた期間", "How long did the person believe it, or how widely was it believed?", "その人はどのくらい信じていましたか。それとも、どのくらい広く信じられていましたか？", ("Did confidence grow?", "Was it ever questioned?"), full="For how long, or how broadly, did the misconception remain convincing?", full_ja="その誤解はどのくらいの期間、またはどのくらい広く信じられていましたか？", safety="personal-or-public-duration"),
            prompt("source", "Where it came from", "情報源", "Where did the belief come from?", "その考えはどこから来ましたか？", ("Was the source trusted?", "Was the original source remembered?"), full="Which source, repetition, or assumption made the belief credible?", full_ja="どんな情報源、繰り返し、前提が、その考えを信じさせましたか？", safety="bounded-source"),
            prompt("discovery", "Finding out", "間違いに気づく", "How did the person find out it was wrong?", "その人は、どうやって間違いだと知りましたか？", ("What evidence mattered?", "Was the correction immediate?"), full="Which evidence or event overturned the misconception?", full_ja="どんな根拠や出来事が、その誤解を覆しましたか？", safety="same-belief-correction"),
            prompt("reaction", "The first reaction", "最初の反応", "Did the person accept the correction, argue, or need time?", "その人は訂正を受け入れましたか、反論しましたか、それとも時間が必要でしたか？", ("What supported acceptance, resistance, or delay?", "Was embarrassment involved, or was another concern more important?"), full="Did the person revise the belief immediately, resist, or reconsider gradually?", full_ja="その人はすぐに考えを変えましたか、抵抗しましたか、それとも徐々に考え直しましたか？", safety="accepted-resisted-or-gradual"),
            prompt("lesson", "What changed after", "その後の変化", "What changed after the correction, if anything?", "訂正の後、何か変わりましたか。それとも何も変わりませんでしたか？", ("If a habit or judgment changed, which one?", "If nothing lasting changed, why not?"), full="Which judgment, habit, or relationship to information changed afterward, or was there no lasting change?", full_ja="その後、判断、習慣、情報との向き合い方のどれが変わりましたか。それとも長く残る変化はありませんでしたか？", safety="lasting-change-or-none"),
            prompt("flip", "What are you sure about?", "今確かなこと", "What are you sure about now, and what supports that confidence?", "今、何を確かだと思い、その自信を何が支えていますか？", ("How strong is the evidence?", "What could change your mind?"), full="Which current belief feels well supported, and what evidence could still revise it?", full_ja="今よく根拠があると思う考えは何で、どんな証拠ならさらに見直しますか？", safety="calibrated-present-belief"),
        ],
    ),
}

# Conversation copy is reviewed independently from the article prose.  The TOC
# opening is the first accessible question; the full version keeps the same
# intellectual job with more precise language.  These revisions deliberately
# make every opening answerable without an apologetic "if none" fallback, then
# let later pages refer to the example selected on page one.
REVISED_GOALS = {
    76: ("Let's talk about childhood advice that stays with people.", "心に残る子どもの頃の助言について話しましょう。"),
    77: ("Let's talk about what makes a teacher unforgettable.", "先生が忘れられない存在になる理由について話しましょう。"),
    78: ("Let's explore how school nicknames begin and affect people.", "学校のあだ名がどう生まれ、人にどう影響するか考えましょう。"),
    79: ("Let's explore how food preferences change as people grow.", "成長とともに食べ物の好みがどう変わるか考えましょう。"),
    80: ("Let's examine why some old mistakes become lasting stories.", "昔の失敗がなぜ長く語られる話になるのか考えましょう。"),
    81: ("Let's tell a travel story shaped by an unexpected problem.", "思いがけないトラブルで変わった旅行の話をしましょう。"),
    82: ("Let's explain what makes a place worth visiting again.", "もう一度訪れる価値のある場所について話しましょう。"),
    83: ("Let's explore what childhood dream jobs reveal about people.", "子どもの頃の夢の仕事から何が分かるか考えましょう。"),
    84: ("Let's imagine one meaningful visit to the past.", "意味のある過去への一日旅行を想像しましょう。"),
    85: ("Let's examine how one moment can redirect a life.", "一つの瞬間が人生の方向をどう変えるか考えましょう。"),
    86: ("Let's compare different views of the same childhood self.", "同じ子どもの頃の姿を、違う視点から比べてみましょう。"),
    87: ("Let's remember a place that disappeared and what it meant.", "なくなった場所と、そこにあった意味を振り返りましょう。"),
    88: ("Let's examine how a confident belief can turn out to be wrong.", "確信していた考えが、どう間違いだと分かるのか考えましょう。"),
}


def _revise_prompt(number: int, job: str, **changes: object) -> None:
    item = next(candidate for candidate in TOPICS[number]["prompts"] if candidate["job"] == job)
    item.update(changes)


for _number, _goal in REVISED_GOALS.items():
    TOPICS[_number]["goal"] = _goal

_revise_prompt(76, "opening", accessible=BRIEF_OPENINGS[76], accessible_ja="子どもに大人がよく繰り返す助言は何ですか？", full="Which childhood advice gets repeated across generations, and why?", full_ja="どんな子どもの頃の助言が世代を越えて繰り返されますか。なぜですか？", accessible_followups=("Who usually gives that advice?", "What makes the line easy to remember?"), full_followups=("Who tends to repeat that advice?", "Why has the wording survived?"), safety="widely-shared-childhood-advice")
_revise_prompt(76, "wording", accessible="How is that advice usually worded?", accessible_ja="その助言は、ふつうどんな言い方をしますか？", full="What wording gives that advice its force?", full_ja="どんな言い方が、その助言に力を持たせていますか？")
_revise_prompt(76, "response", accessible_followups=("What did the child do next?", "How did that reaction shape the advice?"), full_followups=("How did the response become visible?", "What happened after the child reacted?"))
_revise_prompt(76, "inheritance", accessible_followups=("How would you explain it to a child?", "Which words would you change?"), full_followups=("How would you justify it to a child?", "Which part deserves revision?"))
_revise_prompt(76, "nagging", accessible="Which reminder matters enough for adults to repeat to children?", accessible_ja="大人が子どもに繰り返す価値のある注意は何ですか？", full="Which lesson deserves repeating to every new generation?", full_ja="新しい世代に繰り返し伝える価値のある教訓は何ですか？", accessible_followups=("Why does that reminder matter?", "How can an adult say it without nagging?"), full_followups=("Why does that lesson endure?", "How can repetition avoid becoming background noise?"), safety="valuable-repeated-reminder")

_revise_prompt(77, "opening", accessible=BRIEF_OPENINGS[77], accessible_ja="実在でも作品の中でも、特に印象に残る先生は誰ですか。なぜですか？", full="Which real or fictional teacher remains especially memorable, and what makes them stand out?", full_ja="実在でも作品の中でも、特に記憶に残る先生は誰で、何が際立っていますか？", accessible_followups=("What makes that teacher memorable?", "What kind of student did they teach?"), full_followups=("Which quality makes the teacher vivid?", "What was the learning setting?"), safety="memorable-teacher-example")
_revise_prompt(77, "emotion", accessible_followups=("How did that feeling change over time?", "Which moment best explains the feeling?"), full_followups=("How did distance change that response?", "Which classroom moment best explains it?"))
_revise_prompt(77, "hindsight", accessible_followups=("What changed in the later judgment?", "What still feels the same?"), full_followups=("Which judgment shifted in retrospect?", "Which part of the assessment remained stable?"))
_revise_prompt(77, "message", accessible="What would you want that teacher to know if you met today?", accessible_ja="今その先生に会うとしたら、何を知ってほしいですか？", full="What would be worth telling that teacher in a meeting today?", full_ja="今その先生に会うとしたら、何を伝える価値がありますか？", accessible_followups=("Would it be thanks, a question, or criticism?", "How might the teacher respond?"), full_followups=("Would the message express gratitude, curiosity, or criticism?", "How might the teacher understand it now?"), safety="present-day-teacher-message")

_revise_prompt(78, "opening", accessible=BRIEF_OPENINGS[78], accessible_ja="学校のあだ名で、最も印象に残っているものは何ですか？", full="Which school nickname has the most interesting story behind it?", full_ja="最も興味深い由来を持つ学校のあだ名は何ですか？", accessible_followups=("Who used the nickname?", "What made it memorable?"), full_followups=("Who used the nickname most often?", "Why did the story last?"), safety="memorable-nickname-story")
_revise_prompt(78, "others", accessible="Why do students give one another nicknames?", accessible_ja="生徒はなぜ互いにあだ名をつけるのでしょうか？", full="What social purpose do school nicknames serve?", full_ja="学校のあだ名は、どんな社会的な役割を果たしますか？", safety="nickname-social-purpose")
_revise_prompt(78, "flip", accessible="What would a good nickname for your present self capture?", accessible_ja="今の自分に合うよいあだ名なら、どんな特徴を表しますか？", full="What quality should a well-chosen nickname capture about your present self?", full_ja="よく選ばれたあだ名は、今の自分のどんな特徴を表すべきですか？", safety="present-self-nickname")

_revise_prompt(79, "opening", accessible=BRIEF_OPENINGS[79], accessible_ja="子どもが嫌いでも、後で好きになることの多い食べ物は何ですか？", full="Which childhood food aversion most often turns into adult enjoyment?", full_ja="子どもの頃の食べ物嫌いで、大人になると好みに変わりやすいものは何ですか？", accessible_followups=("What makes that food difficult for children?", "What helps people try it again?"), full_followups=("Which feature creates the early aversion?", "What later experience can reverse it?"), safety="common-changing-food-preference")
_revise_prompt(79, "timing", accessible_followups=("Was the shift sudden or gradual?", "What kept the old response in place?"), full_followups=("Did the shift happen abruptly or gradually?", "Which condition sustained the earlier dislike?"))
_revise_prompt(79, "cause", accessible="What experience changed—or could change—the response to that food?", accessible_ja="どんな経験が、その食べ物への反応を変えた、または変えそうですか？", full="Which experience can transform the response to that food?", full_ja="どんな経験が、その食べ物への反応を変えられますか？", accessible_followups=("Did preparation, company, or setting matter?", "What would make another try feel worthwhile?"), full_followups=("Which preparation, person, or setting matters most?", "What conditions make renewed exposure useful?"), safety="food-preference-change")
_revise_prompt(79, "still-no", accessible="Which food tends to remain difficult even after repeated tries?", accessible_ja="何度試しても苦手なままになりやすい食べ物は何ですか？", full="Which food aversion tends to resist repeated exposure?", full_ja="繰り返し試しても変わりにくい食べ物嫌いは何ですか？", safety="lasting-food-aversion")
_revise_prompt(79, "reverse", accessible="Which adult food would surprise the child in this example most?", accessible_ja="この例の子どもが最も驚きそうな大人の食べ物は何ですか？", full="Which adult preference would most surprise the child in the example?", full_ja="その例の子どもが最も驚きそうな大人の好みは何ですか？", safety="surprising-adult-preference")

_revise_prompt(80, "opening", accessible=BRIEF_OPENINGS[80], accessible_ja="どんな昔の失敗が、何度も語られる話になりますか？", full="What makes an old mistake turn into a story people keep retelling?", full_ja="どんな昔の失敗が、人に繰り返し語られる話になりますか？", accessible_followups=("Choose one example. What happened?", "Why did people remember it?"), full_followups=("Which example best shows this?", "What made the story durable?"), safety="retold-mistake-example")
_revise_prompt(80, "reaction", accessible="How did everyone involved react when the mistake became clear?", accessible_ja="失敗が明らかになったとき、関わった人たちはどう反応しましたか？", full="How did the people involved respond once the mistake became clear?", full_ja="失敗が明らかになったとき、関係者はどう対応しましたか？", accessible_followups=("Whose reaction mattered most?", "Did the reaction make the situation better or worse?"), full_followups=("Which response shaped the outcome?", "Did the reaction repair or intensify the problem?"), safety="involved-people-reaction")
_revise_prompt(80, "change", accessible="What lasting change came from the mistake?", accessible_ja="その失敗から、どんな長く残る変化が生まれましたか？", full="What lasting consequence did the mistake produce?", full_ja="その失敗は、どんな長く残る結果を生みましたか？", accessible_followups=("Did it change a habit, rule, or judgment?", "Why did the story remain memorable?"), full_followups=("Which habit, rule, or judgment shifted?", "Why did the account outlast the consequence?"), safety="lasting-mistake-consequence")

_revise_prompt(81, "opening", accessible=BRIEF_OPENINGS[81], accessible_ja="後になると一番面白い話になる旅行トラブルは何ですか？", full="Which kind of travel disruption becomes the most compelling story afterward?", full_ja="後から最も興味深い話になる旅行のトラブルはどんなものですか？", accessible_followups=("Choose one trip story. Where was the traveller going?", "What was the original plan?"), full_followups=("Which trip best illustrates it?", "What was the intended route and purpose?"), safety="travel-mishap-story")
_revise_prompt(81, "response", accessible_followups=("What information guided the response?", "Why did that action seem best?"), full_followups=("Which information shaped the response?", "Why did that action appear most viable?"))
_revise_prompt(81, "company", accessible_followups=("How did the travellers make decisions together?", "What support was available?"), full_followups=("How did company or solitude affect the decisions?", "Which source of support mattered most?"))
_revise_prompt(81, "flip", full="What would make the traveller willing to return?", full_ja="何があれば、その旅行者はもう一度その場所へ行く気になりますか？")

_revise_prompt(82, "opening", accessible=BRIEF_OPENINGS[82], accessible_ja="再訪する価値のある場所を一つ選んでください。なぜ戻る価値がありますか？", full="Choose a place that merits a return visit. What gives it lasting appeal?", full_ja="再訪に値する場所を一つ選んでください。どんな魅力が長く残りますか？", accessible_followups=("Who first visited the place?", "Which memory draws the visitor back?"), full_followups=("Whose return are we considering?", "Which remembered quality creates the pull?"), safety="return-worthy-place")
_revise_prompt(82, "setting", accessible="What would the ideal return visit look like?", accessible_ja="理想的な再訪は、どんなものになりますか？", full="What circumstances would make the return visit worthwhile?", full_ja="どんな状況なら、その再訪に価値がありますか？", accessible_followups=("Which season or time would fit?", "How long should the visit last?"), full_followups=("Which timing would suit the return?", "What duration would preserve its appeal?"), safety="ideal-return-setting")
_revise_prompt(82, "appeal", accessible="Which memory makes the place worth revisiting?", accessible_ja="どの思い出が、その場所をもう一度訪れる価値のあるものにしていますか？", full="Which remembered quality gives the place lasting appeal?", full_ja="記憶に残るどんな特徴が、その場所に長く続く魅力を与えていますか？", accessible_followups=("Is it one scene or the overall feeling?", "What detail is hardest to replace?"), full_followups=("Does one scene or the broader atmosphere dominate?", "Which feature would be hardest to reproduce elsewhere?"), safety="lasting-place-appeal")
_revise_prompt(82, "company", accessible="Who would make the return visit better?", accessible_ja="誰と行けば、その再訪がもっとよくなりますか？", full="How would company or solitude shape the return visit?", full_ja="同行者がいること、または一人でいることは、再訪をどう変えますか？", accessible_followups=("What would that person notice?", "Which part would you share?"), full_followups=("Which companion would change the experience?", "What would solitude make possible?"), safety="return-visit-company")
_revise_prompt(82, "change", accessible="What might be different when the visitor returns?", accessible_ja="訪れる人が戻ったとき、何が違っているかもしれませんか？", full="How might the place or the visitor have changed by the return?", full_ja="再訪までに、場所や訪れる人はどう変わっているかもしれませんか？", accessible_followups=("Which change matters most?", "What should remain the same?"), full_followups=("Which change would alter the experience most?", "What continuity would preserve the connection?"), safety="return-visit-change")
_revise_prompt(82, "plan", accessible="What should the visitor do first on the return?", accessible_ja="再訪したら、最初に何をするべきですか？", full="Which priority should guide the return visit?", full_ja="どの優先事項を再訪の中心にするべきですか？", accessible_followups=("What deserves more time?", "What can be skipped this time?"), full_followups=("What deserves greater attention?", "Which familiar step no longer needs time?"), safety="return-visit-priority")
_revise_prompt(82, "risk", accessible="Can high expectations spoil a return visit?", accessible_ja="期待が高すぎると、再訪が台無しになることはありますか？", full="How can nostalgia distort a return visit?", full_ja="懐かしさは再訪への見方をどうゆがめることがありますか？", accessible_followups=("Which expectation might be too high?", "How could the visitor stay open to change?"), full_followups=("Which memory might be impossible to reproduce?", "How can the visitor keep expectations proportionate?"), safety="return-visit-expectations")

_revise_prompt(83, "opening", accessible=BRIEF_OPENINGS[83], accessible_ja="子どもの頃の夢の仕事で、特に興味深いものは何ですか？", full="Which childhood ambition reveals the most about what children value?", full_ja="子どもが大切にするものを最もよく表す夢の仕事は何ですか？", accessible_followups=("Choose one example. What made the job appealing?", "What did the child imagine doing?"), full_followups=("Which example best reveals the underlying value?", "What image of the work attracted the child?"), safety="childhood-ambition-example")
_revise_prompt(83, "change", accessible_followups=("What new information changed the idea?", "What kept the ambition alive?"), full_followups=("Which new knowledge redirected the ambition?", "Which value allowed it to endure?"))
_revise_prompt(83, "replacement", accessible="What came next for that ambition?", accessible_ja="その夢は、その後どうなりましたか？", full="How did that ambition develop into the next direction?", full_ja="その夢は、次の方向へどう発展しましたか？", accessible_followups=("Did a related interest grow from it?", "What took most of the child's attention next?"), full_followups=("Which later interest inherited part of it?", "What redirected the child's attention?"), safety="ambition-next-direction")
_revise_prompt(83, "connection", accessible_followups=("Which old skill or value remains?", "What is completely different now?"), full_followups=("Which underlying value still survives?", "Which part of adult life breaks with the old ambition?"))
_revise_prompt(83, "flip", accessible="What would the child think of the adult's actual work?", accessible_ja="その子どもは、大人になった本人の実際の仕事をどう思うでしょうか？", safety="childhood-ambition-adult-work")

_revise_prompt(84, "opening", accessible=BRIEF_OPENINGS[84], accessible_ja="過去の一日を訪れられます。どの日を選びますか？", full="You may witness one day in the past. Which day is worth the journey?", full_ja="過去の一日を目撃できます。旅をする価値があるのはどの日ですか？", accessible_followups=("Why does that day matter?", "Where would you arrive?"), full_followups=("What gives that day its significance?", "Where would the visitor enter the scene?"), safety="bounded-past-day")
_revise_prompt(84, "setting", accessible="What is happening on that day?", accessible_ja="その日には何が起きていますか？", full="Which events define the chosen day?", full_ja="どんな出来事が、その日を特徴づけていますか？", accessible_followups=("Who is present?", "Which moment would you watch first?"), full_followups=("Which people shape the day?", "Where would attention first settle?"), safety="chosen-day-events")
_revise_prompt(84, "purpose", accessible="What would you hope to understand by seeing that day?", accessible_ja="その日を見ることで、何を理解したいですか？", full="What insight would make witnessing that day worthwhile?", full_ja="どんな理解が得られれば、その日を見る価値がありますか？", accessible_followups=("Which question matters most?", "What might the present-day visitor misunderstand?"), full_followups=("Which uncertainty deserves an answer?", "What bias might the present-day observer bring?"), safety="past-visit-purpose")
_revise_prompt(84, "choice", accessible="Would you only observe, or would you change something?", accessible_ja="見るだけにしますか、それとも何かを変えますか？", full="Would you remain an observer or intervene in the day?", full_ja="観察者のままでいますか、それともその日に介入しますか？", accessible_followups=("What could intervention change?", "What could observation reveal?"), full_followups=("Which consequence could intervention create?", "What would disciplined observation preserve?"), safety="observe-or-intervene")
_revise_prompt(84, "person", accessible="Who would you most want to see that day?", accessible_ja="その日に最も会いたいのは誰ですか？", full="Whose presence would matter most during the visit?", full_ja="その訪問で、誰の存在が最も重要ですか？", accessible_followups=("What would you notice about them?", "What might surprise you?"), full_followups=("Which detail about them would you study?", "How might the encounter challenge your assumptions?"), safety="meaningful-past-person")
_revise_prompt(84, "message", accessible="What would you ask that person?", accessible_ja="その人に何を尋ねますか？", full="Which question would be worth asking across time?", full_ja="時を越えて尋ねる価値のある質問は何ですか？", accessible_followups=("Why that question?", "Would the person understand your concern?"), full_followups=("Why does that question deserve the limited time?", "How might historical context shape the answer?"), safety="past-person-question")
_revise_prompt(84, "effect", accessible="How might you feel after returning to the present?", accessible_ja="現在に戻ったあと、どんな気持ちになるでしょうか？", full="How might the visit alter the way you see the present?", full_ja="その訪問は、現在の見方をどう変えるかもしれませんか？", accessible_followups=("What would feel clearer?", "What might become harder?"), full_followups=("Which present belief might shift?", "What new uncertainty could the visit create?"), safety="return-to-present-effect")

_revise_prompt(85, "opening", accessible=BRIEF_OPENINGS[85], accessible_ja="どんな瞬間が、人生を全く別の方向へ進ませることがありますか？", full="Which kind of moment can redirect a life before anyone recognizes its importance?", full_ja="どんな瞬間が、重要さに誰も気づかないうちに人生の方向を変えますか？", accessible_followups=("Choose one example. What changed direction?", "Why did that moment matter?"), full_followups=("Which example best captures that shift?", "What made the moment consequential?"), safety="turning-point-example")
_revise_prompt(85, "influence", accessible_followups=("What did the strongest influence contribute?", "Which circumstance redirected the path?"), full_followups=("How did the strongest influence operate?", "Which circumstance narrowed the alternatives?"))

_revise_prompt(86, "opening", accessible=BRIEF_OPENINGS[86], accessible_ja="同じ子どもでも、人によって全く違って見えるのはなぜですか？", full="Why can different adults remember the same child in strikingly different ways?", full_ja="同じ子どもを、大人によって大きく違って覚えているのはなぜですか？", accessible_followups=("Choose one child as an example. How are they described?", "Who sees a different side?"), full_followups=("Which example best shows the contrast?", "Whose perspectives differ most?"), safety="contrasting-childhood-views")
_revise_prompt(86, "scene", accessible_followups=("What happened?", "Who saw the scene?"), full_followups=("What happened in the scene?", "Whose interpretation carries the most weight?"))
_revise_prompt(86, "setting", accessible_followups=("Where did the behaviour change most?", "Which trait stayed consistent?"), full_followups=("Which setting changed the behaviour most?", "What remained stable across relationships?"))
_revise_prompt(86, "continuity", accessible_followups=("How is an old trait expressed differently now?", "What changed most with age?"), full_followups=("How has a surviving trait changed form?", "Which childhood pattern disappeared most clearly?"))

_revise_prompt(87, "opening", accessible=BRIEF_OPENINGS[87], accessible_ja="地元、有名な場所、個人的な場所の中で、消えた場所を一つ戻せるならどこですか？", full="Which vanished place—personal, local, or famous—would be most valuable to restore?", full_ja="個人的な場所、地域の場所、有名な場所のうち、最も戻す価値があるのはどこですか？", accessible_followups=("What kind of place was it?", "Who valued it most?"), full_followups=("What role did the place serve?", "Which community valued it?"), safety="vanished-place-example")
_revise_prompt(87, "replacement", accessible="What replaced the place?", accessible_ja="その場所の代わりに、今は何がありますか？", full="What occupies the site now, and what meaning does the new use carry?", full_ja="今その場所には何があり、新しい使い方にはどんな意味がありますか？", accessible_followups=("Is the replacement useful?", "Does any trace of the old place remain?"), full_followups=("What value does the replacement provide?", "Which trace of the earlier place survives?"), safety="place-replacement")
_revise_prompt(87, "feeling", accessible_followups=("What feels most clearly lost?", "What makes the change understandable?"), full_followups=("Which loss carries the strongest regret?", "What evidence makes the change defensible?"))
_revise_prompt(87, "flip", accessible="Which one detail from the place deserves to be preserved?", accessible_ja="その場所のどの一つの特徴を残す価値がありますか？", full="Which single feature or story most deserves preservation?", full_ja="どの一つの特徴や物語を最も保存する価値がありますか？", accessible_followups=("Who would value it?", "How could it be preserved?"), full_followups=("Which audience would benefit from it?", "What form of preservation would remain honest?"), safety="selective-place-preservation")

_revise_prompt(88, "opening", accessible=BRIEF_OPENINGS[88], accessible_ja="多くの人が以前は信じていたものの、後に間違いだと分かった考えは何ですか？", full="Which once-common belief was overturned most convincingly by later evidence?", full_ja="かつて広く信じられていた考えのうち、後の証拠で最も明確に覆されたものは何ですか？", accessible_followups=("Choose one belief. Why did it seem true?", "How confident were people?"), full_followups=("Which example best shows misplaced certainty?", "What made the claim persuasive at the time?"), safety="corrected-common-belief")
_revise_prompt(88, "lesson", accessible="What changed after the correction?", accessible_ja="訂正の後、何が変わりましたか？", full="How did the correction change later judgment or behaviour?", full_ja="その訂正は、その後の判断や行動をどう変えましたか？", accessible_followups=("Which habit or judgment shifted?", "Why did the correction matter?"), full_followups=("Which information habit changed most?", "What lasting effect did the revision have?"), safety="correction-consequence")

CLAIM_ORDER = {number: tuple(f"ft{number}-c{i:02d}" for i in range(1, 11)) for number in TOPIC_NUMBERS}

VOCABULARY = {
    76: {"new": "nagging|小言", "recycled": "", "assumed": "adult|大人; child|子ども; advice|助言; repeat|繰り返す; listen|聞く", "receptive": "inherit|受け継ぐ; background noise|意識されないもの"},
    77: {"new": "memorable|記憶に残る", "recycled": "", "assumed": "teacher|先生; student|生徒; school|学校; learn|学ぶ; strict|厳しい", "receptive": "humiliation|屈辱; retrospect|振り返って"},
    78: {"new": "nickname|あだ名", "recycled": "", "assumed": "school|学校; name|名前; friend|友人; call|呼ぶ; joke|冗談", "receptive": "ridicule|からかい; consent|同意"},
    79: {"new": "grow on|だんだん好きになる", "recycled": "", "assumed": "food|食べ物; child|子ども; taste|味; smell|匂い; texture|食感", "receptive": "palate|味覚; exposure|繰り返し触れること"},
    80: {"new": "", "recycled": "", "assumed": "mistake|失敗; story|話; laugh|笑う; remember|覚えている; fix|直す", "receptive": "retelling|語り直し; shame|恥をかかせる; bring up|話題にする"},
    81: {"new": "travel mishap|旅行のトラブル", "recycled": "", "assumed": "trip|旅行; plan|計画; weather|天気; lost|なくした; alone|一人で", "receptive": "cascade|次々に影響する; emergency funds|緊急用のお金"},
    82: {"new": "return visit|再訪", "recycled": "", "assumed": "place|場所; trip|旅行; visitor|訪れる人; memory|思い出; alone|一人で", "receptive": "nostalgia|懐かしさ; landmark|名所"},
    83: {"new": "childhood ambition|子どもの頃の夢", "recycled": "", "assumed": "child|子ども; job|仕事; future|将来; school|学校; family|家族", "receptive": "underlying value|根底の価値; fulfil|実現する"},
    84: {"new": "reliving|再体験すること", "recycled": "", "assumed": "past|過去; day|一日; memory|記憶; change|変える; watch|見る", "receptive": "intervene|介入する; thought experiment|思考実験"},
    85: {"new": "turning point|転機", "recycled": "", "assumed": "life|人生; choice|選択; luck|運; decision|決断; future|将来", "receptive": "agency|主体性; counterfactual|反実仮想の"},
    86: {"new": "apparently|どうやら", "recycled": "", "assumed": "child|子ども; family|家族; remember|覚えている; school|学校; quiet|静かな", "receptive": "account|人から聞く話; reconstruct|再構成する"},
    87: {"new": "demolished|取り壊された", "recycled": "", "assumed": "childhood|子ども時代; place|場所; shop|店; school|学校; close|閉まる", "receptive": "preserve|保存する; reconstruction|再現"},
    88: {"new": "misconception|誤解", "recycled": "", "assumed": "believe|信じる; wrong|間違った; information|情報; evidence|根拠; argue|反論する", "receptive": "calibration|確信の調整; verifiable|確認できる"},
}

GLOSSES = {
    76: {"accessible": {5: ("nagging", "nagging", "小言")}, "full": {6: ("background noise", "background noise", "意識されないもの")}},
    77: {"accessible": {}, "full": {4: ("humiliation", "humiliation", "屈辱")}},
    78: {"accessible": {1: ("nickname", "nickname", "あだ名")}, "full": {6: ("consent", "consent", "同意")}},
    79: {"accessible": {5: ("grow on", "grow on", "だんだん好きになる")}, "full": {10: ("palate", "palate", "味覚")}},
    80: {"accessible": {2: ("bring it up", "bring up", "話題にする")}, "full": {3: ("retelling", "retelling", "語り直し")}},
    81: {"accessible": {1: ("travel mishap", "travel mishap", "旅行のトラブル")}, "full": {4: ("cascade", "cascade", "次々に影響する")}},
    82: {"accessible": {}, "full": {8: ("Nostalgia", "nostalgia", "懐かしさ")}},
    83: {"accessible": {8: ("fulfil", "fulfil", "実現する")}, "full": {10: ("underlying value", "underlying value", "根底の価値")}},
    84: {"accessible": {3: ("reliving", "reliving", "再体験すること")}, "full": {7: ("thought experiment", "thought experiment", "思考実験")}},
    85: {"accessible": {}, "full": {4: ("agency", "agency", "主体性")}},
    86: {"accessible": {2: ("apparently", "apparently", "どうやら")}, "full": {1: ("reconstruct", "reconstruct", "再構成する")}},
    87: {"accessible": {4: ("demolished", "demolished", "取り壊された")}, "full": {8: ("reconstruction", "reconstruction", "再現")}},
    88: {"accessible": {}, "full": {7: ("verifiable", "verifiable", "確認できる")}},
}


def _render_dependencies():
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415
    return base, new_lesson


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    _base, new_lesson = _render_dependencies()
    slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
    return new_lesson.ENGLISH / "tracks/3-freetalking/courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"


def _set_pending(head: str) -> str:
    marker = '<meta name="podo:proofread-status" content="pending">'
    if re.search(r'<meta name="podo:proofread-status" content="(?:pending|complete)">', head):
        return re.sub(r'<meta name="podo:proofread-status" content="(?:pending|complete)">', marker, head, count=1)
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
    pages = [base.ft_contract.goal_page(title=data["title"], title_ja=data["ja"], topic_en=goal_en, topic_ja=goal_ja, data_act="What came before", kicker="WHAT CAME BEFORE"), _article_page(topic_no, data, variant, base), base.extract_page(canonical, "lesson-style"), '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of the conversation.</span><span class="ja">全部の質問に答える必要はありません。会話の中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Use these pages as a flexible pool. Ask one question, react naturally, and share a brief real answer of your own when it adds to the exchange. Skip freely and move to feedback with 2–3 minutes left.</div></div>\n''']
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
