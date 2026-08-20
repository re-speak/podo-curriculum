#!/usr/bin/env python3
"""Source specification for paired Freetalking FT 64-75.

Importing this module performs no filesystem or canonical-shell reads. Rendering
is deliberately deferred until the protected FT pilot and shared shell are
stable; this file is reviewable curriculum data first.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


COURSE = "talk-work-and-money"
TOPIC_NUMBERS = tuple(range(64, 76))
VARIANTS = ("accessible", "full")
SENSITIVE_TOPICS = frozenset({68, 69, 70, 71, 72, 74, 75})
TOPIC_FORMAT = {64: "story", 65: "story", 66: "story", 67: "story", 68: "story", 69: "story", 70: "story", 71: "story", 72: "story", 73: "両国", 74: "story", 75: "opinion"}
SHARED_SOURCE = {64: "KR 7-1", 65: "KR 7-2", 66: "KR 7-3", 67: "KR 7-4", 68: "KR 7-5", 69: "KR 7-6", 70: "KR 7-7", 71: "KR 7-8", 72: "KR 7-9", 73: "KR 1-6 moved/reworded", 74: "NEW -> KR", 75: "NEW -> KR"}
TOC_RETRIEVAL_AUDIT_ONLY = True
TOC_RETRIEVAL = {
    64: (("My first ___ was ___.", ("CORE-30",), False), ("I spent it all on ___.", ("CORE-32",), False)),
    65: (("I was actually proud of ___.", ("CORE-30",), False), ("Nobody said anything, but ___.", ("CORE-56",), False)),
    66: (("It wasn't big, but ___.", ("CORE-56",), False), ("That's when I felt ___.", ("CORE-58",), False)),
    67: (("I've been trying to ___.", ("CORE-52",), False), ("I lasted about ___.", ("CORE-51",), True)),
    68: (("I put a bit into ___.", ("CORE-12",), False), ("I wouldn't recommend ___ing.", ("CORE-66",), False)),
    69: (("I'd probably be ___ing.", ("CORE-66",), False), ("I almost ___.", (), True)),
    70: (("I use it for ___ now.", ("CORE-12",), False), ("It still can't ___.", ("CORE-18",), False)),
    71: (("I came close to ___ing.", (), True), ("What stopped me was ___.", ("CORE-103",), True)),
    72: (("___ was the kind of person who ___.", ("CORE-55",), False), ("What made the difference was ___.", ("CORE-103",), True)),
    73: (("Officially it's ___, but ___.", ("CORE-56",), False), ("Nobody actually ___.", ("CORE-15",), False)),
    74: (("Most of my day is spent ___ing.", (), True), ("The part people don't see is ___.", ("CORE-103",), True)),
    75: (("If it were up to me, I'd ___.", ("CORE-66",), False), ("The problem is that ___.", (), True)),
}
FUTURE_CORE_DEPENDENCIES = {65: ("CORE-56",), 66: ("CORE-56", "CORE-58"), 68: ("CORE-66",), 69: ("CORE-66",), 71: ("CORE-103",), 72: ("CORE-55", "CORE-103"), 73: ("CORE-56",), 74: ("CORE-103",), 75: ("CORE-66",)}
REACHABLE_CORE_RETRIEVAL = {64: ("CORE-30", "CORE-32"), 65: ("CORE-30",), 67: ("CORE-51", "CORE-52"), 68: ("CORE-12",), 70: ("CORE-12", "CORE-18"), 73: ("CORE-15",)}
BRIEF_OPENINGS = {
    64: "What are some memorable ways people use their first paycheck?",
    65: "What makes finishing something feel genuinely satisfying?",
    66: "What can make an ordinary moment feel like success?",
    67: "What skill would you most like to improve?",
    68: "Besides spending it, what can people do with money?",
    69: "Which career would you be curious to try for one year?",
    70: "Which everyday task has AI changed the most?",
    71: "What makes someone seriously consider changing careers?",
    72: "What makes a manager, teacher, or coach worth learning from?",
    73: "What time do people usually finish work or school where you live?",
    74: "Choose any recent two-hour period. What filled that time?",
    75: "What would you change about a place where people work or study?",
}


def p(job, title, title_ja, accessible, accessible_ja, accessible_followups, full, full_ja, full_followups, safety):
    return {"job": job, "title": title, "title_ja": title_ja, "accessible": accessible, "accessible_ja": accessible_ja, "accessible_followups": accessible_followups, "full": full, "full_ja": full_ja, "full_followups": full_followups, "safety": safety}


def topic(slug, title, ko, ja, goal, outcomes, article_title, articles, prompts):
    return locals()


# Every article row is (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
    64: topic(
        "what-you-did-with-your-first-paycheck", "What you did with your first paycheck", "첫 월급으로 한 일", "初めての給料で何をしたか",
        ("Let's tell the story of first earnings without requiring a personal amount.", "個人的な金額を求めずに、初めて収入を得たときの話をしましょう。"),
        (("Name the source of the money", "そのお金を得た方法を話す"), ("Describe one use", "使い道を一つ説明する"), ("Explain what it taught you", "学んだことを説明する")),
        ("Why first earnings stay memorable", "初めての収入が記憶に残る理由"),
        [
            ("A first paycheck can make work feel real in a new way.", "A first paycheck can turn the abstract idea of paid work into a concrete experience.", "初めてもらった給料で、働くことを初めて実感する人もいます。", "初めての給料によって、有給の仕事という抽象的な考えが具体的な経験になることがあります。"),
            ("The first money someone earns may come from a job, a task, or selling something.", "First earnings may come from formal employment, a one-off task, creative work, or a sale.", "初めての収入は、仕事、単発の作業、物を売ったことなどから得る場合があります。", "最初の収入は、正式な雇用、単発の作業、創作活動、販売など、さまざまな形から生まれます。"),
            ("The amount may be small while the feeling is important.", "The emotional significance of first earnings may be much greater than the amount itself.", "金額は小さくても、そのときの気持ちは大きいことがあります。", "初めての収入は、金額そのものより感情的な意味のほうが大きい場合があります。"),
            ("Some people spend it immediately; others save part of it.", "Some people celebrate by spending their first earnings, while others save or share them.", "すぐに使う人もいれば、一部を貯める人もいます。", "初めての収入を使って祝う人もいれば、貯めたり誰かと分けたりする人もいます。"),
            ("A purchase can become a reminder of the work behind it.", "An object bought with first earnings can preserve the memory of the effort that produced them.", "そのお金で買った物が、働いた経験を思い出させることがあります。", "初めての収入で買った物が、それを得るまでの努力の記憶を残すことがあります。"),
            ("Telling someone can make the moment feel more official.", "Sharing the news with someone can turn a private milestone into a recognized achievement.", "誰かに話すことで、その瞬間が正式な節目のように感じられることがあります。", "誰かに知らせることで、個人的な節目が周りにも認められた達成になります。"),
            ("Not everyone remembers the exact amount or date.", "A meaningful account does not require recalling the exact amount, employer, or date.", "正確な金額や日付を覚えていない人もいます。", "意味のある話をするために、正確な金額、雇い主、日付まで思い出す必要はありません。"),
            ("Someone who has not earned money yet can still discuss a familiar example.", "A learner without personal earnings can examine a familiar, public, or imagined first-pay story.", "まだ収入を得たことがなくても、身近な例について話せます。", "自分で収入を得た経験がなくても、身近な人、公に知られた例、想像上の話を考えられます。"),
            ("Looking back, we may choose a different use for that money now.", "Later priorities can change what we imagine doing with the same first payment.", "今振り返ると、同じお金を別のことに使いたいと思う場合があります。", "その後の優先順位によって、同じ初収入の使い道を今なら違って考えることがあります。"),
            ("First earnings can teach us what money represents to us.", "The first experience of earning can reveal whether money represents freedom, security, generosity, or reward.", "初めて稼ぐ経験から、自分にとってお金が何を意味するか分かることがあります。", "初めて収入を得る経験は、お金が自由、安心、分かち合い、報酬のどれを意味するかを示すことがあります。"),
        ],
        [
            p("opening", "First earnings", "初めての収入", BRIEF_OPENINGS[64] + " If you haven't earned money yet, use a familiar or imagined example.", "初めて自分で得たお金は何で、何に使いましたか？ まだ経験がなければ、身近な人や想像上の例でもかまいません。", ("What made that payment memorable?", "What did receiving it make possible for the first time?"), "What was the first money you earned, and how did you use it? A familiar or hypothetical example is equally welcome.", "初めて得た収入は何で、どのように使いましたか？ 身近な例や仮定の例でもかまいません。", ("Which part of the experience made it memorable?", "What did the payment make possible that had not been possible before?"), "personal-familiar-or-imagined"),
            p("amount", "The amount", "金額", "Did the amount feel large, small, or simply exciting at the time?", "その金額は当時、大きく感じましたか、小さく感じましたか、それとも金額よりうれしさがありましたか？", ("A rough answer is enough; what made it feel that way?", "If you prefer no figure, what could the money cover?"), "Did the amount feel substantial, modest, or important mainly because it was your first?", "その金額は大きく感じましたか、少なく感じましたか、それとも初めてだったことが主に重要でしたか？", ("A broad range is enough; what shaped that perception?", "Without disclosing a figure, what could the payment realistically cover?"), "rough-or-no-number"),
            p("source", "The work behind it", "お金を得た方法", "What job, task, or other activity produced the money?", "そのお金は、どんな仕事、作業、または活動で得ましたか？", ("How long did the work take?", "What part was harder than you expected?"), "Which job, task, sale, or other activity generated the first earnings?", "最初の収入は、どんな仕事、作業、販売、または活動から得ましたか？", ("How much time or preparation did it require?", "Which part demanded more effort than expected?"), "work-task-sale-or-example"),
            p("use", "What it paid for", "使い道", "What was the first thing the money paid for—or what might it pay for in your example?", "そのお金で最初に何を買いましたか。それとも、選んだ例では何に使いそうですか？", ("Why did that use come first?", "Did any of the money remain afterward?"), "What was the first use of the money, or what would be the first use in your example?", "そのお金を最初に何に使いましたか。それとも、選んだ例なら最初の使い道は何ですか？", ("Which priority made that use come first?", "Was any part saved, shared, or left unspent?"), "actual-or-example-use"),
            p("sharing", "Who knew", "誰に話したか", "Did you tell anyone about earning it—or would the person in your example tell someone?", "その収入について誰かに話しましたか。それとも、例の人なら誰かに話しますか？", ("If someone knew, how did they respond?", "If it stayed private, what made privacy comfortable?"), "Did anyone know about the earnings, or would the person in your example keep them private?", "その収入を誰かが知っていましたか。それとも、例の人なら自分だけにしておきますか？", ("If someone knew, what recognition or advice did they offer?", "If it remained private, what purpose did privacy serve?"), "shared-or-private"),
            p("now", "What you would do now", "今ならどうするか", "If you received the same first payment today, what would you do differently?", "今、同じ最初の収入を受け取ったら、何を変えますか？", ("Would you spend, save, share, or combine them?", "Which current priority would guide you?"), "If you received the equivalent payment today, how would your use of it differ?", "今、同じ程度の収入を受け取ったら、使い方はどう変わりますか？", ("Would you consume, save, share, or divide it among purposes?", "Which present priority would determine the choice?"), "hypothetical-current-choice"),
            p("lesson", "What it taught", "学んだこと", "What did that first payment teach you about work or money?", "その最初の収入から、仕事やお金について何を学びましたか？", ("Did the lesson come from earning it or using it?", "Has that lesson stayed useful?"), "What did the first experience of earning reveal about work, money, or independence?", "初めて収入を得た経験から、仕事、お金、自立について何が分かりましたか？", ("Did the insight come from earning, spending, or deciding?", "How has that lesson influenced a later choice?"), "lesson-not-advice"),
            p("flip", "A meaningful first use", "意味のある最初の使い道", "What is one good way for someone to mark a first paycheck?", "初めての給料を記念するよい方法を一つ挙げるとしたら何ですか？", ("Why might that choice feel meaningful?", "How could it work even with a small amount?"), "What is one meaningful way to recognize a first paycheck without prescribing how it must be used?", "使い道を決めつけずに、初めての給料を意味のある形で記念する方法は何ですか？", ("Which value would the choice express?", "How could the idea remain realistic with a modest amount?"), "general-nonprescriptive-close"),
        ],
    ),
    65: topic(
        "something-you-were-proud-to-finish", "Something you were proud to finish", "끝내고 자랑스러웠던 일", "終えて誇らしかったこと",
        ("Let's describe a finished effort and why it mattered, using a personal or familiar example.", "自分や身近な人の例を使って、やり終えた努力となぜ大切だったかを話しましょう。"),
        (("Name the finished effort", "やり終えたことを挙げる"), ("Describe who noticed", "誰が気づいたか話す"), ("Explain the source of pride", "誇りを感じた理由を説明する")),
        ("What makes completion feel meaningful", "やり終えることに意味が生まれる理由"),
        [
            ("Finishing something difficult can create a quiet sense of pride.", "Completing a demanding task can make a person feel proud of the effort even without public recognition.", "難しいことを終えると、静かな誇りを感じることがあります。", "大変な課題を完了すると、人に認められなくても、その努力を誇りに思うことがあります。"),
            ("Pride may come from effort, improvement, or keeping a promise.", "The source of pride may be persistence, growth, quality, or keeping a commitment.", "誇りは、努力、上達、約束を守ったことから生まれる場合があります。", "誇りの源は、粘り強さ、成長、質、約束を果たしたことなどさまざまです。"),
            ("A finished task does not have to be large or public.", "An achievement can be personally significant without being large, public, or competitive.", "やり終えたことは、大きなことや人に見せることでなくてもかまいません。", "達成は、大規模、公的、競争的でなくても、本人にとって大切なものになれます。"),
            ("Sometimes nobody notices the work behind the result.", "Invisible preparation often receives less attention than the final result.", "結果の裏にある努力に、誰も気づかないこともあります。", "目に見えない準備は、最終的な結果ほど注目されないことがよくあります。"),
            ("Recognition can feel good without being the only reason for pride.", "External recognition can reinforce pride without becoming its sole foundation.", "人に認められるとうれしくても、それだけが誇りの理由とは限りません。", "周囲からの評価は誇りを強めますが、唯一の土台になる必要はありません。"),
            ("Saying we are proud can feel uncomfortable in some settings.", "Cultural expectations can make direct expressions of pride feel boastful even when they are accurate.", "場面によっては、自分を誇りに思うと言いにくいことがあります。", "文化的な期待によって、正直な誇りの表現でも自慢のように感じられることがあります。"),
            ("A disappointing result does not erase the value of finishing.", "An imperfect outcome can coexist with pride in the process or persistence.", "結果が期待どおりでなくても、終えたことの価値は消えません。", "不完全な結果でも、その過程や粘り強さを誇りに思うことはできます。"),
            ("We can feel proud of someone else's effort too.", "A familiar person's achievement can provide a valid example when personal disclosure is not comfortable.", "ほかの人の努力を誇りに思うこともできます。", "自分の話をしにくい場合は、身近な人の達成も十分な例になります。"),
            ("What we are proud of often shows what we value.", "The achievements we value reveal standards that matter more deeply than status.", "誇りに思うことから、自分が大切にしているものが見えることがあります。", "大切にする達成から、地位より深い自分の基準が見えてきます。"),
            ("A useful next goal can grow from a completed one.", "Reflecting on a completed effort can identify the next meaningful direction without diminishing the achievement.", "終えたことを振り返ると、次の目標が見えることがあります。", "完了した努力を振り返ると、その価値を損なわずに次の意味ある方向を見つけられます。"),
        ],
        [
            p("opening", "A finished effort", "やり終えた努力", BRIEF_OPENINGS[65] + " A familiar or general example is also fine.", "最近、何かをやり終えて誇らしいと感じたのはいつですか？ 身近な人や一般的な例でもかまいません。", ("What sign showed that the effort was complete?", "What made the result matter?"), "When did you last complete something and feel genuinely proud of it? A familiar case is equally valid.", "最近、何かを完了して心から誇りに感じたのはいつですか？ 身近な事例でもかまいません。", ("Which sign confirmed that the effort had reached completion?", "What gave the result personal significance?"), "personal-familiar-or-general"),
            p("detail", "What you finished", "終えたこと", "What exactly was finished in that example?", "その例では、具体的に何を終えましたか？", ("How long had it taken?", "What almost prevented completion?"), "What exactly reached completion in the example you are discussing?", "話している例では、具体的に何が完了しましたか？", ("How long had the effort been underway?", "Which obstacle came closest to stopping it?"), "selected-example-continuity"),
            p("notice", "Who noticed", "誰が気づいたか", "Who noticed the result—or did nobody say anything?", "その結果に誰が気づきましたか。それとも、誰も何も言いませんでしたか？", ("If someone noticed, what did they say?", "If nobody did, how did you recognize the achievement?"), "Who recognized the result, if anyone?", "その結果に気づいた人はいましたか？", ("If someone recognized it, how did they respond?", "If it went unnoticed, what confirmed its value to you or the person?"), "noticed-or-unnoticed"),
            p("voice", "Saying it aloud", "言葉にする", "Did the person say they felt proud, or keep that feeling private?", "その人は誇らしい気持ちを言葉にしましたか。それとも自分の中に留めましたか？", ("What made speaking easy or difficult?", "How else could the pride be shown?"), "Was the pride expressed directly or kept private?", "その誇りは直接表現されましたか、それとも自分の中に留められましたか？", ("Which norm made expression easy or uncomfortable?", "What indirect sign could communicate the feeling?"), "spoken-or-private"),
            p("meaning", "Why it mattered", "大切だった理由", "Why did finishing that particular thing matter?", "なぜ、それをやり終えたことが大切だったのですか？", ("Was the effort, result, or promise most important?", "What value did the achievement show?"), "Why did that completion carry more meaning than an ordinary finished task?", "なぜ、その完了は普通の作業を終えたときより大きな意味を持ちましたか？", ("Did persistence, quality, growth, or commitment matter most?", "Which deeper value did the achievement express?"), "meaning-not-status"),
            p("contrast", "A result without pride", "誇れなかった結果", "What is something a person can finish without feeling proud of it?", "終えても誇らしく感じないことには、どんなものがありますか？", ("What might be missing from the result?", "Could the process still deserve credit?"), "What kind of completed result might fail to produce pride?", "完了しても誇りにつながらない結果には、どんなものがありますか？", ("Which standard might the result have failed to meet?", "Could the process still justify a different kind of recognition?"), "general-negative-example"),
            p("identity", "What to be known for", "何で知られたいか", "What kind of finished work would you want to be known for?", "どんな完成した仕事や成果で知られたいですか？", ("Which quality should people notice?", "Would the scale of the work matter?"), "Which kind of completed work would you want associated with your name or contribution?", "どんな完成した仕事や貢献と、自分の名前を結びつけたいですか？", ("Which quality should define the association?", "Would reach, difficulty, or lasting value matter most?"), "aspirational-no-current-role"),
            p("flip", "Recognizing effort", "努力を認める", "How can we help someone feel proud without giving empty praise?", "形だけの褒め言葉ではなく、相手が誇りを感じられるようにするにはどうすればよいですか？", ("Which specific effort could be named?", "What question could invite the person to reflect?"), "How can recognition support earned pride without becoming vague flattery?", "曖昧なお世辞ではなく、努力に基づく誇りを支えるにはどうすればよいですか？", ("Which concrete contribution should be named?", "Which question could help the person articulate the achievement?"), "earned-recognition-close"),
        ],
    ),
    66: topic(
        "a-moment-when-you-felt-successful", "A moment when you felt successful", "성공했다고 느낀 순간", "うまくいっていると感じた瞬間",
        ("Let's describe one concrete moment of small or large success.", "大小を問わず、うまくいった具体的な瞬間を一つ話しましょう。"),
        (("Set the scene", "場面を説明する"), ("Name what made it successful", "成功だと感じた理由を挙げる"), ("Compare an earlier and current standard", "以前と今の基準を比べる")),
        ("Success is often a moment, not a definition", "成功は定義より一つの瞬間"),
        [
            ("A small success can matter before anyone else notices it.", "A small success can signal progress before it receives external recognition.", "小さな成功でも、周りが気づく前から大切な意味を持つことがあります。", "小さな成功は、外から評価される前に進歩を示すことがあります。"),
            ("Success may feel like relief, confidence, or quiet satisfaction.", "A successful moment may register as relief, competence, momentum, or quiet satisfaction.", "成功は、安心、自信、静かな満足として感じられることがあります。", "成功の瞬間は、安堵、能力の実感、勢い、静かな満足として現れる場合があります。"),
            ("The scene makes the word success more specific.", "A concrete scene prevents success from becoming an abstract essay topic.", "具体的な場面があると、成功という言葉が分かりやすくなります。", "具体的な場面は、成功を抽象的な作文テーマにしてしまうのを防ぎます。"),
            ("One solved problem can make a whole day feel different.", "Resolving one stubborn problem can change the emotional direction of an entire day.", "一つの問題が解決すると、一日全体の感じ方が変わることがあります。", "なかなか解けなかった問題を一つ解決すると、一日全体の気持ちの流れが変わることがあります。"),
            ("Other people may be present without causing the feeling.", "Colleagues, classmates, friends, or family may witness success without defining it for us.", "周りに人がいても、その人たちが成功の感覚を決めるとは限りません。", "同僚、クラスメート、友人、家族が成功を見ていても、その意味を本人の代わりに決めるわけではありません。"),
            ("A successful feeling may last minutes or change later.", "The emotional high may be brief even when the underlying achievement remains important.", "成功した気持ちは数分だけ続き、あとで変わることもあります。", "高揚感は短くても、その根拠となった達成は大切なままであることがあります。"),
            ("A familiar or public example can replace a personal story.", "A familiar, observed, public, or imagined scene can support the same discussion without personal disclosure.", "自分の話の代わりに、身近な人や公に知られた例を使えます。", "個人的な話をせずに、身近な例、見聞きした例、公の例、想像上の場面で同じ議論ができます。"),
            ("What counts as success can change with circumstances.", "Health, responsibility, opportunity, and experience can all reshape the threshold for success.", "何を成功と考えるかは、状況によって変わります。", "健康、責任、機会、経験によって、成功と考える基準は変化します。"),
            ("A harder goal is not automatically a more meaningful success.", "Difficulty alone does not determine whether an achievement is valuable or well chosen.", "難しい目標ほど意味のある成功になるとは限りません。", "難しさだけで、その達成に価値があるか、よい目標だったかは決まりません。"),
            ("Naming one moment can reveal a practical definition of success.", "A specific moment often reveals a working definition of success more honestly than a broad slogan.", "一つの瞬間を挙げると、自分にとっての成功が具体的に見えます。", "具体的な瞬間は、広い標語より正直に、本人が実際に使っている成功の基準を示します。"),
        ],
        [
            p("opening", "One successful moment", "うまくいった瞬間", BRIEF_OPENINGS[66] + " A familiar or imagined moment is fine too.", "最近、物事がうまくいっていると感じたのはいつですか？ 大きなことでなくてよく、身近な人や想像上の場面でもかまいません。", ("What was happening in that moment?", "What made it count as a small success?"), "When did you last feel that things were going well? It need not be a major achievement, and a familiar example is welcome.", "最近、物事がうまく進んでいると感じたのはいつですか？ 大きな達成でなくてよく、身近な例でもかまいません。", ("Which scene captures that feeling?", "What made the moment qualify as success?"), "personal-familiar-or-imagined"),
            p("scene", "What was happening", "何が起きていたか", "What was happening just before the successful moment?", "うまくいったと感じる直前には、何が起きていましたか？", ("What problem or goal was in front of the person?", "Which detail changed the mood?"), "What circumstances immediately preceded the successful moment?", "成功を感じた瞬間の直前には、どのような状況がありましたか？", ("Which problem or objective framed the moment?", "Which detail marked the shift?"), "selected-scene"),
            p("people", "Who was there", "そこにいた人", "Who was there, if anyone, and did their presence matter?", "そこに誰かいましたか。その人がいたことは重要でしたか？", ("If someone was there, what did they notice?", "If nobody was there, how was the success recognized?"), "Who witnessed the moment, if anyone, and how did their presence affect it?", "その瞬間を見ていた人はいましたか。その人がいたことで何が変わりましたか？", ("If it was witnessed, which response mattered?", "If it was private, what confirmed the achievement?"), "witnessed-or-private"),
            p("feeling", "How it felt", "どう感じたか", "Did the moment feel exciting, relieving, calm, or something else?", "その瞬間は、わくわく、安心、落ち着き、それとも別の感覚でしたか？", ("Where did that feeling come from?", "Was it stronger than expected?"), "Did the moment register as excitement, relief, confidence, calm, or another feeling?", "その瞬間は、興奮、安堵、自信、落ち着き、または別の感覚として現れましたか？", ("Which part of the achievement produced that feeling?", "Did its intensity match your expectations?"), "emotion-menu-open"),
            p("duration", "Did it last", "続いたか", "How long did the successful feeling last?", "うまくいったという感覚は、どのくらい続きましたか？", ("What kept it going?", "If it faded quickly, what remained important?"), "How long did the sense of success persist, and what remained after it faded?", "成功の感覚はどのくらい続き、薄れたあとには何が残りましたか？", ("Which condition sustained the feeling?", "Did the achievement retain meaning after the emotion changed?"), "brief-or-lasting"),
            p("current", "What would count now", "今の成功", "What would count as a small success for you or someone like you now?", "今の自分や似た状況の人にとって、小さな成功になるのは何ですか？", ("Why would that matter now?", "What is the smallest visible sign?"), "What would qualify as meaningful progress for you or a comparable person now?", "今の自分や同じような人にとって、意味のある進歩と呼べるのは何ですか？", ("Which current condition gives it significance?", "What observable sign would confirm it?"), "self-or-comparable-person"),
            p("change", "A changing standard", "変わる基準", "Has your idea of success changed, stayed steady, or remained unclear?", "成功についての考えは変わりましたか、変わっていませんか、それともまだはっきりしませんか？", ("If it changed, what matters less now?", "If it stayed steady or unclear, which value remains central?"), "Has your working definition of success evolved, remained stable, or stayed unresolved?", "自分が実際に使う成功の定義は、変化しましたか、安定していますか、それとも未決定ですか？", ("If it evolved, which former measure lost weight?", "If it remained stable or unresolved, which value still anchors it?"), "changed-stable-or-unclear"),
            p("flip", "Someone else's success", "他の人の成功", "How can you recognize someone else's small success without comparing it with yours?", "自分と比べずに、ほかの人の小さな成功をどう認められますか？", ("Which effort or change could you name?", "What comparison should you avoid?"), "How can another person's success be acknowledged without imposing your own standard?", "自分の基準を押しつけずに、ほかの人の成功をどう認められますか？", ("Which concrete progress deserves recognition?", "Which comparison would distort its meaning?"), "noncomparative-close"),
        ],
    ),
    67: topic(
        "something-youre-trying-to-get-better-at", "Something you're trying to get better at", "더 잘하고 싶은 것", "もっと上達したいこと",
        ("Let's discuss an effort to improve, whether it is current, past, familiar, or imagined.", "今続けていることに限らず、過去、身近な人、想像上の例も使って、上達するための努力を話しましょう。"),
        (("Name one skill", "技能を一つ挙げる"), ("Describe an attempt", "取り組みを説明する"), ("Choose a realistic next step", "現実的な次の一歩を選ぶ")),
        ("Why improvement rarely follows a straight line", "上達が一直線に進まない理由"),
        [
            ("Getting better usually takes repeated practice.", "Improvement generally emerges through repeated, focused practice rather than one dramatic effort.", "上達には、たいてい繰り返し練習することが必要です。", "上達は、一度の大きな努力ではなく、焦点を絞った練習の積み重ねから生まれるのが一般的です。"),
            ("A clear skill is easier to practise than a vague goal.", "A precisely defined skill makes practice and feedback more useful.", "曖昧な目標より、具体的な技能のほうが練習しやすくなります。", "技能を明確に定めると、練習とフィードバックがより役立ちます。"),
            ("Short attempts still show what helps and what gets in the way.", "Even an abandoned attempt can reveal effective conditions and recurring obstacles.", "短い取り組みからも、役立つことや妨げになることが分かります。", "途中でやめた取り組みからも、効果的な条件や繰り返す障害が見えてきます。"),
            ("Failing to stick with a routine once does not mean a person cannot improve.", "A person who did not stick with one routine has not settled their long-term capacity to learn.", "一度習慣を続けられなくても、その人が上達できないという意味ではありません。", "一つの習慣を続けられなかったからといって、長期的な学習能力が決まるわけではありません。"),
            ("Useful feedback points to one change the learner can try.", "Effective feedback identifies a specific adjustment without reducing the learner to a weakness.", "役立つフィードバックは、次に試せる変更を一つ示します。", "効果的なフィードバックは、学ぶ人を弱点だけで捉えず、具体的な調整を一つ示します。"),
            ("Progress may be easier for someone else to notice first.", "Another person may detect gradual improvement before the learner feels it.", "少しずつの上達は、本人より周りの人が先に気づくことがあります。", "徐々な上達は、本人が実感する前に他の人が気づく場合があります。"),
            ("A familiar or imagined example can replace a personal goal.", "The same questions can examine a familiar, public, or hypothetical learning effort.", "自分の目標の代わりに、身近な人や想像上の例を使えます。", "同じ問いを、身近な例、公に知られた例、仮定の学習にも当てはめられます。"),
            ("Some skills no longer need to be a priority.", "Choosing not to pursue a skill can be sensible when priorities or circumstances change.", "今は優先しなくてよい技能もあります。", "優先順位や状況が変われば、ある技能を追求しない選択も合理的です。"),
            ("A small next step is easier to repeat.", "A modest, repeatable action often supports improvement better than an ambitious burst.", "小さな次の一歩は、繰り返しやすくなります。", "無理のない反復可能な行動は、大きな一時的努力より上達を支えやすいことがあります。"),
            ("The right measure depends on the skill.", "Evidence of improvement should match the skill rather than a generic idea of success.", "上達の測り方は、技能によって異なります。", "上達の証拠は、一般的な成功の考えではなく、その技能に合っている必要があります。"),
        ],
        [
            p("opening", "A skill to improve", "上達したい技能", BRIEF_OPENINGS[67] + " You may use a past, familiar, or imagined effort instead.", "今、何をもっと上達させようとしていますか？ 過去の取り組み、身近な人、想像上の例でもかまいません。", ("What part of the skill needs the most attention?", "If the attempt has stopped, what did it reveal?"), "What are you currently trying to improve? A past, familiar, or hypothetical effort is equally valid.", "今、何を上達させようとしていますか？ 過去、身近な人、仮定の取り組みでもかまいません。", ("Which component of the skill needs focused work?", "If the effort ended, what did it reveal about learning conditions?"), "current-past-familiar-or-imagined"),
            p("attempt", "What you tried", "試したこと", "What have you or the person in your example tried so far?", "自分や例の人は、これまで何を試しましたか？", ("How long did that attempt last?", "What made it easy or hard to repeat?"), "What methods have you or the selected person attempted so far?", "自分や選んだ人は、これまでどんな方法を試しましたか？", ("How long was each method sustained?", "Which condition supported or disrupted repetition?"), "active-or-ended-attempt"),
            p("obstacle", "What gets in the way", "妨げになること", "What is the main obstacle to improving this skill?", "この技能を上達させるうえで、主な障害は何ですか？", ("Is the obstacle time, access, confidence, or something else?", "Which part can the person influence?"), "What is the most persistent barrier to improvement in this example?", "この例で、上達を最も妨げ続けているものは何ですか？", ("Does it involve time, access, feedback, confidence, or another factor?", "Which part is realistically within the person's influence?"), "selected-example-obstacle"),
            p("feedback", "Useful feedback", "役立つフィードバック", "What feedback would help with the next attempt?", "次の取り組みに役立つのは、どんなフィードバックですか？", ("Who or what could provide it?", "Which detail should the feedback identify?"), "What kind of feedback would make the next attempt more effective?", "次の取り組みをより効果的にするのは、どんなフィードバックですか？", ("Which source could provide credible feedback?", "What concrete adjustment should it identify?"), "general-or-selected-example"),
            p("evidence", "Signs of progress", "上達の兆し", "What small sign would show that the skill is improving?", "どんな小さな兆しがあれば、その技能が上達していると分かりますか？", ("Who might notice it first?", "How could it be checked without a formal test?"), "What observable evidence would indicate genuine improvement?", "どんな観察可能な証拠があれば、本当に上達していると判断できますか？", ("Who would be well placed to notice it?", "How could the change be assessed without relying on one formal test?"), "evidence-not-feeling-only"),
            p("priority", "Worth continuing", "続ける価値", "Is this skill still worth pursuing, or have priorities changed?", "この技能は今も伸ばす価値がありますか。それとも優先順位が変わりましたか？", ("What would justify continuing?", "What would make stopping reasonable?"), "Does this skill still justify sustained effort, or have other priorities become more important?", "この技能は今も継続的な努力に値しますか。それとも、ほかの優先事項のほうが重要になりましたか？", ("Which benefit would justify continuing?", "Which changed circumstance would make stopping sensible?"), "continue-pause-or-stop"),
            p("next", "One next step", "次の一歩", "What is one small action the person could repeat this week?", "その人が今週繰り返せる小さな行動は何ですか？", ("When could it fit?", "What would make it easy to begin?"), "What is one modest, repeatable action that could move the skill forward this week?", "今週、その技能を前進させるために繰り返せる無理のない行動は何ですか？", ("Where could it fit into the week?", "Which cue or resource would lower the barrier to starting?"), "self-or-example-next-step"),
            p("flip", "Teaching the skill", "技能を教える", "If you taught this skill to a beginner, what would you start with?", "この技能を初心者に教えるなら、何から始めますか？", ("Why is that the best first step?", "What common mistake would you normalize?"), "If you introduced this skill to a beginner, which foundation would you teach first?", "この技能を初心者に紹介するなら、最初にどの基礎を教えますか？", ("Why does that foundation come first?", "Which early mistake should be treated as normal?"), "general-teaching-close"),
        ],
    ),
    68: topic(
        "what-you-do-with-money-you-dont-spend", "What you do with money you don't spend", "쓰지 않은 돈으로 하는 일", "使わなかったお金でしていること",
        ("Let's discuss ways money can be used without requesting income, balances, or advice.", "収入額や残高、助言を求めずに、使う以外のお金の扱い方を話しましょう。"),
        (("Name one use besides spending", "支出以外の使い道を一つ挙げる"), ("Explain a reason", "理由を説明する"), ("Compare priorities", "優先順位を比べる")),
        ("Money can serve more than one purpose", "お金には複数の役割がある"),
        [
            ("People may save, share, invest, repay debt, or simply keep money available.", "Beyond immediate spending, money may be reserved, shared, invested, used to reduce debt, or kept liquid.", "お金は、貯める、分ける、投資する、借金を返す、使える状態で持つなどに使われます。", "すぐに使う以外にも、お金は貯蓄、分配、投資、債務の削減、流動性の確保に充てられます。"),
            ("Not everyone has money left after essential costs.", "Any discussion of financial choices must acknowledge that essential costs may leave no surplus.", "必要な支出のあとにお金が残らない人もいます。", "金銭的な選択を話す際は、必要経費のあとに余裕がない場合も認める必要があります。"),
            ("People may set aside a small amount to create flexibility later.", "People may set aside even a modest reserve for flexibility when an expected or unexpected need appears.", "少額でも取っておくと、あとで選べる余地が生まれます。", "少額でも備えとして取っておくと、予想内外の必要が生じたときに選択の余地が生まれます。"),
            ("Giving money can express care, duty, or shared responsibility.", "Financial support may reflect generosity, obligation, reciprocity, or collective responsibility.", "お金を渡すことは、思いやり、義務、共同の責任を表す場合があります。", "金銭的な支援は、寛大さ、義務、互恵、共同責任を示すことがあります。"),
            ("A good choice depends on a person's circumstances.", "No single allocation is right for every income level, household, risk, or stage of life.", "よい選択は、その人の状況によって異なります。", "どの収入、世帯、リスク、人生段階にも当てはまる配分はありません。"),
            ("Financial privacy is a reasonable boundary.", "A useful conversation can focus on purposes and trade-offs without disclosing figures or accounts.", "お金について話さない部分を決めるのは自然なことです。", "金額や口座を明かさなくても、目的や選択の違いを話すことはできます。"),
            ("Advice that fits one person may be unsuitable for another.", "Financial guidance can become harmful when it ignores constraints, risk tolerance, or local rules.", "一人に合う助言が、別の人にも合うとは限りません。", "制約、リスクの許容度、地域の規則を無視した金融助言は有害になり得ます。"),
            ("A familiar or imagined budget can support a general discussion.", "A hypothetical allocation allows reflection without turning the learner's finances into evidence.", "身近な人や想像上の予算を使って一般的に話せます。", "仮定の配分なら、学習者自身の家計を材料にせず考えられます。"),
            ("Priorities can change after a new responsibility or loss.", "A change in dependants, work, health, or security can reorder financial priorities.", "新しい責任や損失があると、お金の優先順位が変わることがあります。", "扶養、仕事、健康、安心の変化によって、金銭的な優先順位が入れ替わる場合があります。"),
            ("The purpose of money may matter more than the method.", "A financial action is best understood through the need or value it is meant to serve.", "お金の扱い方より、その目的のほうが重要なことがあります。", "金銭的な行動は、それが支えようとする必要や価値から理解するのが適切です。"),
        ],
        [
            p("opening", "Beyond spending", "使う以外", BRIEF_OPENINGS[68] + " You can answer generally and give no figures.", "お金を使う以外に何かしていますか？ 一般的な話でよく、金額は言わなくてかまいません。", ("If yes, does it happen regularly or only sometimes?", "If nothing is left over, which future option would matter most?"), "What, if anything, do you do with money besides spend it? A general answer without figures is welcome.", "お金を使う以外に、何かしていることはありますか？ 金額を出さず、一般的に答えてかまいません。", ("If there is a current practice, is it regular or occasional?", "If no surplus is available, which future option would matter most?"), "personal-general-or-no-surplus"),
            p("purpose", "One purpose", "一つの目的", "Choose saving, sharing, repaying debt, investing, keeping money available, or another purpose. Why does it matter?", "貯蓄、分配、借金の返済、投資、手元に置くこと、または別の目的を一つ選んでください。なぜ大切ですか？", ("What need does it serve?", "Is it for now, later, or both?"), "Which non-spending purpose—reserving, sharing, repaying debt, investing, maintaining access, or another—matters in your example, and why?", "支出以外の目的のうち、貯蓄、分配、借金の返済、投資、使える状態の維持など、選んだ例で大切なのはどれで、なぜですか？", ("Which need or value does it serve?", "Is its benefit immediate, future, or both?"), "open-purpose-menu"),
            p("start", "When it began", "始めた時期", "When did that practice begin, or is it only an idea for now?", "その習慣はいつ始まりましたか。それとも、今はまだ考えているだけですか？", ("What prompted the beginning?", "If it has not begun, what would need to be true first?"), "When did that financial practice begin, or does it remain a possible future choice?", "そのお金の扱い方はいつ始まりましたか。それとも、将来の選択肢のままですか？", ("Which event or need prompted it?", "If it remains hypothetical, which condition would make it realistic?"), "started-or-not-started"),
            p("progress", "How it is going", "今の状況", "How is that approach going, or what would make it workable?", "その方法はうまくいっていますか。それとも、実行しやすくするには何が必要ですか？", ("What has helped so far?", "What has made it difficult?"), "How effective has that approach been, or what would determine its viability?", "その方法はどの程度効果がありましたか。それとも、実行可能かどうかを何が決めますか？", ("Which condition has supported it?", "Which constraint has limited or prevented it?"), "active-or-hypothetical-progress"),
            p("influence", "Where the idea came from", "考えのきっかけ", "Did a person, experience, or common idea influence that approach?", "その方法には、人、経験、よく聞く考えのどれかが影響しましたか？", ("If there was an influence, what part did you accept?", "If there was none, how did the approach develop?"), "Which person, experience, institution, or familiar idea influenced that approach, if any?", "その方法に影響した人、経験、組織、またはよくある考えがあるとすれば、何ですか？", ("If there was an influence, which part was useful?", "If there was none, how did the approach develop?"), "person-experience-idea-or-none"),
            p("recommend", "Would it suit someone else", "人に合うか", "Would you recommend that approach to everyone, only in some situations, or not at all?", "その方法を全員に勧めますか。一部の状況だけですか。それとも勧めませんか？", ("If you would recommend it anywhere, what makes it suitable?", "If not, what risk or limit leads you to reject it?"), "Would you recommend the approach broadly, conditionally, or not at all?", "その方法を広く勧めますか、条件つきで勧めますか、それとも勧めませんか？", ("If you would recommend it, which circumstances make it appropriate?", "If not, which constraint or risk rules it out?"), "broad-conditional-or-no-recommendation"),
            p("never", "A financial boundary", "しないこと", "What is one thing you would never do with money, or would treat with great caution?", "お金に関して、絶対にしないこと、または特に慎重にすることは何ですか？", ("What value or risk creates that boundary?", "Can you answer generally without personal details?"), "Which financial action would you reject or approach only with strict safeguards?", "どの金銭的な行動なら、避けるか、厳しい安全策がある場合だけ検討しますか？", ("Which risk, duty, or value justifies the boundary?", "How can the principle be explained without disclosing private finances?"), "general-boundary-not-advice"),
            p("flip", "More than money", "お金以外", "What important kind of support cannot be replaced by money?", "お金では代えられない大切な支援には何がありますか？", ("Why does that support matter?", "Can money still make it easier to provide?"), "Which valuable form of support cannot be reduced to a financial transfer?", "金銭の受け渡しだけでは表せない大切な支援は何ですか？", ("What distinctive need does that support meet?", "Can financial resources still help make it possible?"), "nonfinancial-close"),
        ],
    ),
    69: topic(
        "a-different-career-you-might-have-chosen", "A different career you might have chosen", "선택했을 수도 있는 다른 진로", "選んでいたかもしれない別のキャリア",
        ("Let's imagine an alternative career path without assuming a current career or regret.", "現在のキャリアや後悔を前提にせず、別のキャリアの進路を想像しましょう。"),
        (("Name an alternative path", "別の進路を挙げる"), ("Explain the attraction", "魅力を説明する"), ("Compare one trade-off", "選択の違いを一つ比べる")),
        ("An alternative path can clarify present values", "別の進路から今の価値観が見える"),
        [
            ("An imagined career path is not the same as a plan to leave.", "Considering an alternative career does not imply dissatisfaction or an intention to change.", "別のキャリアを想像しても、辞める計画があるとは限りません。", "別のキャリアを考えることは、不満や転職の意図を意味しません。"),
            ("Students, carers, retired people, and people between jobs can discuss the topic too.", "The topic remains relevant without a current job because it concerns roles, interests, and possible lives.", "学生、ケアをする人、退職した人、仕事の合間にいる人も話せます。", "現在仕事をしていなくても、役割、関心、可能な生き方を扱う話題として考えられます。"),
            ("A different path may appeal because of the work itself.", "The attraction may lie in daily tasks, social value, autonomy, learning, or working conditions.", "別の進路は、仕事そのものに魅力がある場合があります。", "魅力は、日々の業務、社会的価値、自律性、学び、労働条件にあるかもしれません。"),
            ("A public or fictional person can provide an example.", "A familiar, public, or fictional trajectory can replace personal career disclosure.", "公に知られた人や架空の人物を例にできます。", "個人的なキャリアを話さずに、身近な人、公人、架空の人物の歩みを使えます。"),
            ("Every path has gains and limits.", "A credible comparison recognizes constraints and losses as well as attractive possibilities.", "どの進路にも、得るものと制約があります。", "信頼できる比較では、魅力的な可能性だけでなく、制約や失うものも考えます。"),
            ("Timing can affect whether a path was realistic.", "Access, location, money, responsibility, and timing shape which careers are genuinely available.", "その進路が現実的だったかは、時期にも左右されます。", "機会、場所、お金、責任、時期によって、実際に選べるキャリアは変わります。"),
            ("A path not taken can still influence present choices.", "An unrealized interest may reappear through hobbies, volunteering, study, or a smaller role.", "選ばなかった進路も、今の選択に影響することがあります。", "実現しなかった関心が、趣味、ボランティア、学習、小さな役割として現れることがあります。"),
            ("Regret is only one possible response.", "People may feel curiosity, relief, gratitude, indifference, or mixed feelings about an alternative.", "別の進路に対する気持ちは、後悔だけではありません。", "別の進路には、好奇心、安堵、感謝、無関心、複雑な気持ちなどもあり得ます。"),
            ("Values can remain stable even when jobs change.", "Different occupations may express the same underlying values in different ways.", "仕事が変わっても、価値観は変わらないことがあります。", "異なる職業でも、同じ根本的な価値を別の形で表せます。"),
            ("Imagining another path can reveal one change worth making now.", "A counterfactual career can identify a present need without demanding a complete reinvention.", "別の進路を想像すると、今できる小さな変更が見えることがあります。", "仮定のキャリアから、全面的にやり直さなくても、今必要なことが見つかる場合があります。"),
        ],
        [
            p("opening", "Another path", "別の進路", BRIEF_OPENINGS[69] + " If you do not have a current career, imagine a familiar or fictional path.", "別のキャリアの進路を選んでいたら、何をしていると思いますか？ 現在のキャリアがなければ、身近な人や架空の進路でもかまいません。", ("When did this alternative first become interesting?", "Is this curiosity, regret, or neither?"), "What might you be doing if a different career path had been available? You may use a familiar, public, or fictional example.", "別のキャリアの進路を選べたとしたら、何をしていると思いますか？ 身近な人、公に知られた人、架空の人物の例でもかまいません。", ("When did this alternative first become worth considering?", "Does the comparison evoke curiosity, regret, relief, or none of these?"), "personal-familiar-public-or-fictional"),
            p("daily", "An ordinary day", "普通の一日", "What would an ordinary day on that path include?", "その進路では、普通の一日に何をするでしょうか？", ("Which task would take most time?", "Which part might be less appealing?"), "What activities and responsibilities would define an ordinary day on that path?", "その進路の普通の一日は、どんな活動や責任で成り立つでしょうか？", ("Which task would occupy the largest share of time?", "Which responsibility might be less attractive than it first appears?"), "imagined-role-not-current-job"),
            p("attraction", "Why it appeals", "魅力を感じる理由", "What is the strongest reason that path appeals to you or the person in your example?", "その進路に自分や例の人が魅力を感じる最大の理由は何ですか？", ("Is it the work, impact, freedom, or setting?", "Which value does it match?"), "What is the principal source of attraction in that alternative path?", "その別の進路の主な魅力はどこにありますか？", ("Does it concern the work, social contribution, autonomy, learning, or conditions?", "Which underlying value does it express?"), "selected-example-attraction"),
            p("realism", "What made it possible", "可能にする条件", "What would have needed to be different for that path to be realistic?", "その進路を現実的にするには、何が違う必要がありましたか？", ("Was timing, access, money, or responsibility important?", "Could any part of the path still be explored?"), "Which conditions would have needed to change for that path to become genuinely available?", "その進路を実際に選べるようにするには、どの条件が変わる必要がありましたか？", ("Did timing, access, resources, location, or responsibility matter most?", "Can any element of the path still be pursued on a smaller scale?"), "counterfactual-not-blame"),
            p("example", "Someone who changed paths", "進路を変えた人", "Do you know, know of, or can you imagine someone who chose a very different path?", "大きく違う進路を選んだ人を知っていますか、聞いたことがありますか、それとも想像できますか？", ("What made their change possible?", "Which trade-off did they face?"), "Can you identify a familiar, public, fictional, or hypothetical person who chose a substantially different path?", "大きく違う進路を選んだ、身近な人、公人、架空の人物、仮定の人物を挙げられますか？", ("Which condition enabled the transition?", "Which meaningful benefit or security did the choice put at risk?"), "familiar-public-fictional-or-imagined-person"),
            p("feeling", "How it feels now", "今の気持ち", "How do you feel about the path not taken: curious, relieved, regretful, or neutral?", "選ばなかった進路について、好奇心、安堵、後悔、無関心のどれに近いですか？", ("What creates that feeling?", "Has it changed over time?"), "What response does the unrealized path produce now—curiosity, relief, regret, indifference, or a mixture?", "実現しなかった進路に今どんな気持ちがありますか。好奇心、安堵、後悔、無関心、または複雑な気持ちですか？", ("Which comparison produces that response?", "How has the response evolved over time?"), "open-emotion-menu"),
            p("present", "A value to use now", "今生かせる価値", "Which part of that path, if any, could be brought into life now without changing careers?", "キャリアを変えずに、その進路の一部を今の生活に取り入れられるとすれば、何ですか？", ("If one part fits, could it appear in study, a hobby, or a small role?", "If none fits, what makes it inseparable from a full career change?"), "Which value or activity from the alternative, if any, could be incorporated now without a complete career change?", "全面的にキャリアを変えずに、その別の進路の価値や活動を今取り入れられるとすれば、何ですか？", ("If one part fits, could it take the form of study, volunteering, a project, or a smaller responsibility?", "If none fits, what makes it inseparable from a complete transition?"), "partial-present-or-none"),
            p("flip", "Advice to a younger person", "若い人への考え", "What question should a younger person ask before choosing a career path?", "若い人がキャリアの進路を選ぶ前に、どんな問いを考えるとよいですか？", ("What assumption should they test?", "Whose experience could broaden the picture?"), "Which question would help a younger person evaluate a career path without pretending the choice is permanent?", "選択が永遠に変えられないと思い込まずに、若い人がキャリアの進路を考えるための問いは何ですか？", ("Which attractive assumption should be tested?", "Whose experience could reveal the less visible parts of the path?"), "general-nonprescriptive-close"),
        ],
    ),
    70: topic(
        "how-ai-has-changed-your-work", "How AI has changed your work", "AI가 일을 바꾼 방식", "AIが仕事を変えたこと",
        ("Let's compare life with and without an AI tool, including a no-use route.", "AIを使わない場合も含めて、AIツールがある日常とない日常を比べましょう。"),
        (("Name one task or no-use case", "作業または不使用の例を挙げる"), ("Describe a real change", "実際の変化を説明する"), ("Set one boundary", "境界を一つ決める")),
        ("A tool matters when a routine actually changes", "道具の意味は習慣の変化に表れる"),
        [
            ("AI has not changed everyone's day.", "Access, relevance, preference, and policy mean that AI has not altered every person's routine.", "AIで日常が変わっていない人もいます。", "利用環境、必要性、好み、規則によって、AIが全員の日常を変えたわけではありません。"),
            ("A useful comparison begins with one specific task.", "Evaluating one concrete task is more informative than making a broad claim about AI.", "役立つ比較は、具体的な作業一つから始まります。", "AIについて広く主張するより、具体的な作業一つを評価するほうが有益です。"),
            ("A faster task is not automatically a better result.", "Time saved has value only when quality, judgment, privacy, and responsibility remain acceptable.", "作業が速くなっても、結果がよくなるとは限りません。", "時間短縮の価値は、質、判断、プライバシー、責任が保たれて初めて成り立ちます。"),
            ("AI can support work, study, home tasks, or creative projects.", "Relevant use may occur in employment, education, domestic administration, accessibility, or creative activity.", "AIは、仕事、勉強、家の用事、創作を支えることがあります。", "AIの活用は、雇用、教育、家庭の事務、アクセシビリティ、創作などに見られます。"),
            ("Delegating a step does not remove responsibility for the result.", "When people hand over part of a task to AI, they still need to review consequential output.", "作業の一部をAIに任せても、結果への責任はなくなりません。", "作業の一部をAIに任せても、重要な出力を確認する責任は残ります。"),
            ("Some information should not be entered into a tool.", "Confidential, identifying, or sensitive material may require strict limits or complete exclusion.", "ツールに入力しないほうがよい情報もあります。", "機密情報、個人を特定する情報、センシティブな内容には、厳しい制限や完全な除外が必要な場合があります。"),
            ("A tool can create new work as well as remove it.", "Verification, correction, prompting, and policy compliance can offset some apparent efficiency.", "道具は仕事を減らすだけでなく、新しい作業を生むこともあります。", "確認、修正、指示作成、規則への対応によって、見かけの効率が相殺される場合があります。"),
            ("A familiar or public example can replace personal use.", "A learner with no AI use can analyze a familiar, public, or hypothetical routine.", "自分でAIを使わなくても、身近な例や公の例を話せます。", "AIを使っていない学習者も、身近な例、公に知られた例、仮定の習慣を分析できます。"),
            ("The most important change may be what a person checks.", "As tools take over execution, human attention may shift toward framing, verification, and accountability.", "最も大きな変化は、人が何を確認するかかもしれません。", "道具が実行を担うと、人の注意は問題設定、検証、説明責任へ移ることがあります。"),
            ("Keeping a task human can be a deliberate choice.", "Rejecting automation can be reasonable when human contact, learning, authorship, or trust is central.", "作業を人の手で続けることも、意識的な選択です。", "人との関わり、学習、作者性、信頼が中心なら、自動化しない選択も合理的です。"),
        ],
        [
            p("opening", "One actual change", "実際の変化", BRIEF_OPENINGS[70] + " If you do not use AI, discuss a familiar or public example.", "AIによって、日常の何かが実際に変わりましたか？ 使っていなければ、身近な例や公に知られた例でもかまいません。", ("Which task changed—or stayed the same?", "What evidence shows the difference?"), "Has AI materially changed any part of your day? If not, analyze a familiar, public, or hypothetical routine.", "AIは日常の一部を実際に変えましたか？ 変わっていなければ、身近な例、公の例、仮定の習慣を考えてください。", ("Which task changed or remained unaffected?", "What observable evidence supports that conclusion?"), "self-or-general-no-use"),
            p("before", "Before and after", "導入前と後", "How was the selected task done before, and how is it done now?", "選んだ作業は以前どのように行われ、今はどう行われていますか？", ("Which step disappeared or changed?", "If there was no change, what kept the process stable?"), "How did the process operate before and after AI entered the example, or why did it remain unchanged?", "選んだ例では、AIの導入前後で手順はどう変わりましたか。それとも、なぜ変わりませんでしたか？", ("Which step was removed, added, or reassigned?", "If the process remained stable, which condition prevented change?"), "changed-or-unchanged"),
            p("quality", "The result", "結果", "Did the result become better, worse, mixed, or unchanged?", "結果はよくなりましたか、悪くなりましたか、両方ですか、それとも変わりませんか？", ("Which quality changed?", "What still needs a person's judgment?"), "Did the output improve, deteriorate, become mixed, or remain equivalent?", "出力は改善しましたか、悪化しましたか、長所と短所が混在していますか、それとも同等ですか？", ("Which dimension of quality changed?", "Where does human judgment remain indispensable?"), "open-result-evaluation"),
            p("newwork", "Work it created", "増えた作業", "What new work did the tool create, if any?", "その道具で新たに増えた作業はありますか？", ("If new work appeared, who checks or corrects it?", "If none appeared, what kept the extra burden low?"), "Which verification, correction, documentation, or policy tasks did the tool create, if any?", "その道具で新たに増えたものがあるとすれば、確認、修正、記録、規則対応のどんな作業ですか？", ("If additional work appeared, who performs it?", "If none appeared, which condition kept the extra burden low?"), "new-work-or-none"),
            p("boundary", "A clear boundary", "明確な境界", "What is one task or kind of information you would not hand over to AI?", "AIに任せない作業や情報を一つ挙げるとしたら何ですか？", ("What risk creates the boundary?", "Could AI support a smaller part safely?"), "Which task, decision, or category of information should remain outside AI use in this context?", "この状況で、どの作業、判断、情報をAIの利用範囲外にすべきですか？", ("Which risk justifies the boundary?", "Could a limited supporting role remain acceptable?"), "general-safety-boundary"),
            p("responsibility", "Who remains responsible", "残る責任", "If AI helps with the task, who should check the result?", "AIが作業を手伝う場合、誰が結果を確認すべきですか？", ("What should that person verify?", "What cannot be blamed on the tool?"), "When part of a task is handed over to AI, who retains responsibility for reviewing the result?", "作業の一部をAIに任せたとき、結果を確認する責任は誰に残りますか？", ("Which claims or consequences require verification?", "Which accountability cannot be transferred to the tool?"), "general-accountability"),
            p("keep", "Keep it human", "人が続けること", "What is one activity that should stay mainly human?", "主に人が行い続けるべき活動を一つ挙げるとしたら何ですか？", ("What human value does it protect?", "Could a tool still help at the edge?"), "Which activity should remain primarily human even if automation becomes possible?", "自動化できるようになっても、主に人が行うべき活動は何ですか？", ("Which human value would that preserve?", "Could the tool still support a limited peripheral step?"), "general-human-value"),
            p("flip", "A useful trial", "試す価値のある使い方", "What is one low-risk AI use a curious person could test?", "興味のある人が低いリスクで試せるAIの使い方は何ですか？", ("How would they judge whether it helps?", "What information should they keep out?"), "What limited, low-risk AI experiment could produce useful evidence rather than hype?", "誇張ではなく役立つ証拠を得られる、範囲を絞った低リスクのAI実験は何ですか？", ("Which measure would show whether it helped?", "Which data and decisions should remain excluded?"), "nonprescriptive-close"),
        ],
    ),
    71: topic(
        "a-time-you-seriously-considered-changing-careers", "A time you seriously considered changing careers", "진로 변경을 진지하게 고민한 때", "キャリア変更を真剣に考えたとき",
        ("Let's examine a real, familiar, or hypothetical career change without requiring a current job or disclosure.", "現在の仕事や個人的な開示を前提にせず、実際、身近、または仮定のキャリア変更を考えましょう。"),
        (("Establish a possible change", "考えた変更を示す"), ("Explain the pressure and attraction", "圧力と魅力を説明する"), ("Describe the decision or open question", "判断または未決定の点を話す")),
        ("A near-change reveals what a decision must protect", "変えかけた経験から守るべきものが見える"),
        [
            ("People may change careers by changing field, role, or working pattern.", "People may change careers through a shift in occupation, sector, responsibility, identity, schedule, or degree of paid work.", "分野、役割、働き方を変えることで、キャリアを変える人もいます。", "職業、業界、責任、自己認識、勤務形態、有給労働の程度を変えることで、キャリアを変える人もいます。"),
            ("Not everyone has a current career to change.", "Students, carers, retired people, and people outside paid work can discuss a familiar or hypothetical case.", "現在変えるキャリアがない人もいます。", "学生、ケアを担う人、退職した人、有給労働をしていない人は、身近な例や仮定の事例で話せます。"),
            ("Thinking seriously about change does not require taking action.", "A period of serious consideration may end in change, staying, postponement, or no final decision.", "真剣に考えても、実際に行動するとは限りません。", "真剣に検討した結果は、変更、継続、延期、未決定のいずれにもなり得ます。"),
            ("The attraction of a new path may coexist with real risk.", "Meaning, growth, flexibility, or relief may compete with income, identity, access, and responsibility.", "新しい進路の魅力と現実的なリスクは両立します。", "意味、成長、柔軟性、安堵が、収入、自己認識、機会、責任と競合することがあります。"),
            ("Staying can be an active decision, not a failure of courage.", "Remaining in a role can reflect informed priorities rather than fear or inertia.", "続けることも、勇気がないのではなく、積極的な判断になり得ます。", "今の役割に残ることは、恐れや惰性ではなく、十分に考えた優先順位を表す場合があります。"),
            ("A change can be gradual instead of complete.", "Training, experiments, reduced hours, projects, or role adjustments can test a direction before a full transition.", "変更は、一度に全部行うのではなく、段階的にもできます。", "研修、試行、時間の短縮、プロジェクト、役割調整によって、全面移行前に方向を試せます。"),
            ("Privacy is valid when work affects security or identity.", "A learner may discuss a public, fictional, or composite example rather than a sensitive personal decision.", "仕事が安心や自己認識に関わるとき、話さない選択は自然です。", "センシティブな個人の判断の代わりに、公の例、架空の例、複数を組み合わせた例を使えます。"),
            ("Advice should not pretend constraints are simple.", "Encouragement becomes unhelpful when it ignores dependants, health, immigration, discrimination, or local opportunity.", "助言で、制約を単純に扱うべきではありません。", "扶養、健康、在留資格、差別、地域の機会を無視する励ましは役立たなくなります。"),
            ("A decision can remain unresolved for a valid reason.", "Uncertainty may reflect missing evidence rather than indecision or weakness.", "正当な理由で、判断がまだ決まらないこともあります。", "不確実さは、優柔不断や弱さではなく、必要な情報がまだないことを示す場合があります。"),
            ("The key question is what a change is meant to improve.", "A credible transition begins with a defined problem or value rather than the appeal of novelty alone.", "大切なのは、変更によって何をよくしたいかです。", "信頼できる転換は、新しさの魅力だけでなく、解決したい問題や実現したい価値から始まります。"),
        ],
        [
            p("opening", "A possible change", "考えた変更", BRIEF_OPENINGS[71] + " You may discuss someone familiar, a public case, or a hypothetical choice.", "今していることを変えようと真剣に考えたことがありますか？ 身近な人、公の事例、仮定の選択でもかまいません。", ("What kind of change was considered?", "Was it a change of field, role, schedule, or something else?"), "Have you ever seriously considered changing careers or working patterns? A familiar, public, or hypothetical case is equally valid.", "キャリアや働き方を変えようと真剣に考えたことがありますか？ 身近な例、公の例、仮定の事例でもかまいません。", ("Which form of change was under consideration?", "Did it concern field, role, schedule, paid work, or another dimension?"), "personal-familiar-public-or-hypothetical"),
            p("pressure", "What pushed the question", "考えるきっかけ", "What made the person consider a change?", "その人が変更を考えたきっかけは何ですか？", ("Was the pressure temporary or ongoing?", "Which part needed to improve?"), "Which condition made a change worth serious consideration?", "どのような状況によって、変更を真剣に考えるようになりましたか？", ("Was that pressure temporary, structural, or still unclear?", "Which outcome needed to improve?"), "selected-case-pressure"),
            p("attraction", "What pulled the other way", "新しい方向の魅力", "What was attractive about the other direction?", "別の方向のどこに魅力がありましたか？", ("Was it the work, meaning, freedom, or conditions?", "Which attraction was strongest?"), "What made the alternative direction appealing?", "別の方向にはどんな魅力がありましたか？", ("Did the appeal concern tasks, meaning, growth, autonomy, or conditions?", "Which attraction carried the greatest weight?"), "selected-alternative"),
            p("risk", "What was at risk", "懸念したこと", "What made changing difficult or risky?", "変更を難しくしたことやリスクは何ですか？", ("Which risk was most concrete?", "Could any part be reduced?"), "Which constraint or potential loss made the transition difficult?", "どの制約や失う可能性が、移行を難しくしましたか？", ("Which risk was most immediate and evidence-based?", "Could a staged approach reduce any part of it?"), "no-pressure-to-disclose"),
            p("decision", "What happened", "その後", "Did the person change, stay, postpone, or remain undecided?", "その人は変更しましたか、続けましたか、延期しましたか、それともまだ決めていませんか？", ("What most influenced that outcome?", "Does the question feel settled now?"), "Did the case end in transition, staying, postponement, or an unresolved decision?", "その事例は、移行、継続、延期、未決定のどれに至りましたか？", ("Which evidence or responsibility most influenced the outcome?", "What, if anything, remains unsettled?"), "changed-stayed-postponed-or-open"),
            p("experiment", "A smaller test", "小さく試す", "What smaller experiment could test the new direction?", "新しい方向を試すために、どんな小さな実験ができますか？", ("What would the person learn?", "What limit would keep the test safe?"), "What reversible experiment could provide evidence about the alternative direction?", "別の方向について証拠を得るために、元に戻せるどんな試行ができますか？", ("Which uncertainty would the experiment reduce?", "Which boundary would limit the cost or risk?"), "general-or-selected-case"),
            p("sharing", "Who knew", "誰に話したか", "Did the person tell anyone about the possible change, or keep it private?", "その人は変更の可能性を誰かに話しましたか。それとも自分の中に留めましたか？", ("If someone knew, what response mattered?", "If it stayed private, what made privacy important?"), "Was the possible transition discussed with anyone, or kept private?", "その移行の可能性は誰かと話しましたか。それとも非公開のままでしたか？", ("If it was shared, which response influenced the decision?", "If it remained private, which risk or boundary justified that choice?"), "shared-or-private"),
            p("flip", "What a change should improve", "変更でよくしたいこと", "Before changing careers, what should a person be able to name clearly?", "キャリアを変える前に、何を明確に言えるとよいですか？", ("What problem should the change solve?", "What value should it protect?"), "Before a major transition, which intended improvement should a person be able to articulate?", "大きな移行の前に、目指すどの改善を明確に説明できるとよいですか？", ("Which problem is the transition meant to address?", "Which existing value or responsibility must it preserve?"), "general-reflective-close"),
        ],
    ),
    72: topic(
        "someone-you-learned-a-lot-from", "Someone you learned a lot from", "많이 배운 사람", "多くを学んだ人",
        ("Let's discuss what makes guidance useful without requiring a personal authority relationship.", "個人的な上下関係を話す必要なく、役立つ指導の特徴を考えましょう。"),
        (("Choose a real or public example", "実在または公の例を選ぶ"), ("Describe one behavior", "行動を一つ説明する"), ("Explain what was learned", "学んだことを説明する")),
        ("We learn from how people guide, not only what they know", "知識だけでなく導き方から学ぶ"),
        [
            ("A person can learn from a manager, teacher, coach, peer, or public example.", "Useful guidance can come from formal authority, a peer, a public figure, or a fictional case.", "上司、先生、コーチ、仲間、公の例から学ぶことができます。", "役立つ導きは、正式な権限を持つ人、仲間、公人、架空の事例からも得られます。"),
            ("A title does not guarantee good guidance.", "Formal authority and instructional skill are separate qualities.", "役職があっても、よい指導ができるとは限りません。", "正式な権限と指導力は別の性質です。"),
            ("Clear expectations can make feedback easier to use.", "Feedback becomes actionable when standards and purposes are visible in advance.", "期待されることが明確だと、フィードバックを生かしやすくなります。", "基準と目的が事前に明確なら、フィードバックを行動に移しやすくなります。"),
            ("A good guide adjusts support as confidence grows.", "Effective guidance changes from explanation to practice, feedback, and greater independence.", "よい指導者は、自信がつくにつれて支援を調整します。", "効果的な指導は、説明から練習、フィードバック、より大きな自立へと変化します。"),
            ("A learner may value honesty without accepting disrespect.", "Direct feedback can remain specific and demanding without humiliation or contempt.", "率直な指摘は大切でも、失礼さを受け入れる必要はありません。", "直接的なフィードバックも、屈辱や軽蔑なしに具体的で厳しくできます。"),
            ("People also learn from a poor example.", "Ineffective or unfair leadership can clarify practices the learner does not want to repeat.", "よくない例からも学ぶことがあります。", "効果のない、または不公平な指導から、自分が繰り返したくない行動が明確になることがあります。"),
            ("Naming someone may be unsafe or unnecessary.", "A composite, anonymous, public, or fictional example can protect privacy and power-sensitive relationships.", "名前を挙げることが安全でない、または不要な場合があります。", "複数を組み合わせた例、匿名、公の例、架空の例なら、プライバシーや上下関係を守れます。"),
            ("Learning can continue after the relationship ends.", "A principle learned from guidance may outlast the role, course, team, or contact.", "その関係が終わっても、学びは続くことがあります。", "指導から得た原則は、役割、講座、チーム、関係が終わったあとも残ることがあります。"),
            ("The learner decides what to keep.", "Respect for a mentor does not require adopting every habit, belief, or method.", "何を残すかは、学ぶ人が決めます。", "指導者を尊敬しても、すべての習慣、考え、方法を受け入れる必要はありません。"),
            ("Good guidance expands independent judgment.", "The strongest long-term evidence of guidance is a learner who can make sound decisions without constant supervision.", "よい指導は、自分で判断する力を広げます。", "指導の最も強い長期的な証拠は、常に監督されなくても適切に判断できる学習者です。"),
        ],
        [
            p("opening", "A person to learn from", "学んだ人", BRIEF_OPENINGS[72] + " If no one comes to mind, use a public, fictional, or general example.", "学んだことのある上司、先生、コーチを思い浮かべてください。どんな人でしたか？ 思い浮かばなければ、公の人、架空の人物、一般的な例でもかまいません。", ("What was the learner trying to improve or understand?", "You need not give a name; what role did the person or example play?"), "Consider a manager, teacher, coach, peer, public figure, or fictional guide you could learn from. What made the guidance useful or instructive?", "学びにつながった上司、先生、コーチ、仲間、公人、または架空の指導者の例を考えてください。その指導の何が役立った、または参考になりましたか？", ("What was the learner trying to improve or understand?", "Without naming anyone, what form did the guidance take?"), "personal-public-fictional-or-general"),
            p("behavior", "What they did", "行動", "What did the person or example actually do that helped learning?", "その人や例は、学びを助けるために実際に何をしましたか？", ("Was it explanation, practice, feedback, or trust?", "Which moment shows it clearly?"), "Which observable practice made the guidance effective?", "どの観察可能な行動によって、その指導が効果的になりましたか？", ("Did it involve explanation, practice, feedback, standards, or autonomy?", "Which incident illustrates the practice most clearly?"), "behavior-not-personality-only"),
            p("feedback", "How feedback worked", "フィードバックの方法", "How did the guide respond when something went wrong?", "何かがうまくいかなかったとき、その指導者はどう対応しましたか？", ("What made the response useful or unhelpful?", "Did it leave a clear next step?"), "How did the guide handle mistakes, uncertainty, or weak performance?", "間違い、不確実さ、十分でない成果に、その指導者はどう対応しましたか？", ("Which feature made the response constructive or damaging?", "Did it produce a clear and realistic next action?"), "positive-or-negative-example"),
            p("power", "Respect and power", "尊重と立場", "What should a person with authority do to make questions feel safe?", "権限のある人は、質問しやすくするために何をすべきですか？", ("Which reaction should they avoid?", "How can they show that uncertainty is normal?"), "How can someone in authority make disagreement, questions, and uncertainty safer?", "権限を持つ人は、反対意見、質問、不確実さをどうすればより安全に表明できるようにできますか？", ("Which response would silence honest questions?", "What visible behavior would demonstrate that uncertainty is acceptable?"), "general-power-sensitive"),
            p("lesson", "What remained", "残った学び", "What idea or habit did the learner keep from that example?", "その例から、学ぶ人はどんな考えや習慣を残しましたか？", ("Where is it useful now?", "Has it needed any adjustment?"), "Which principle or practice continued to matter after the guidance ended?", "指導が終わったあとも、どの原則や実践が大切なまま残りましたか？", ("Where does it remain applicable?", "How has it been adapted to a different context?"), "selected-example-continuity"),
            p("response", "How the learner responded", "学ぶ人の反応", "Did the learner respond to the guidance, keep the response private, or not respond at all?", "学ぶ人はその指導に反応しましたか、反応を自分の中に留めましたか、それとも何も反応しませんでしたか？", ("If the response was spoken or private, what did it communicate?", "If there was no response, why might that be the honest account?"), "Did the learner respond directly to the guidance, indirectly, or not at all?", "学ぶ人はその指導に直接、間接的に反応しましたか。それとも反応を示しませんでしたか？", ("If the response was direct or indirect, what did it communicate?", "If there was no response, why might that be the honest account?"), "direct-indirect-private-or-none"),
            p("independence", "Learning to decide", "自分で判断する", "How can a guide help someone need less help over time?", "指導者は、学ぶ人が徐々に助けを必要としなくなるよう、どう支援できますか？", ("What can be handed over first?", "What support should remain available?"), "How can guidance deliberately transfer judgment and responsibility to the learner?", "指導は、判断と責任をどのように意識して学ぶ人へ移せますか？", ("Which decision should be handed over first?", "Which safety net should remain available during the transition?"), "general-autonomy"),
            p("flip", "The guide you would be", "自分ならどう導くか", "What is one quality you would want to show when guiding someone?", "自分が誰かを導くとき、示したい性質を一つ挙げるとしたら何ですか？", ("What action would show it?", "How would you know it helped?"), "Which quality would you want your own guidance to be known for?", "自分の指導がどんな性質で知られてほしいですか？", ("Which repeatable behavior would demonstrate it?", "What evidence would show that it expanded the learner's judgment?"), "general-reflective-close"),
        ],
    ),
    73: topic(
        "what-a-normal-work-or-school-day-looks-like-where-you-live", "What a normal work or school day looks like where you live", "사는 곳의 보통 일·학교 하루", "住んでいる地域の普通の仕事・学校の一日",
        ("Let's compare official and real finishing times across work, school, care, and other routines.", "仕事、学校、ケアなどの習慣について、決まった終了時刻と実際の時刻を比べましょう。"),
        (("Describe one local routine", "地域の習慣を一つ説明する"), ("Compare official and actual time", "公式と実際の時刻を比べる"), ("Explain one cause or consequence", "原因または結果を一つ説明する")),
        ("The end of the day is both a schedule and a social rule", "一日の終わりは時刻であり社会的なルールでもある"),
        [
            ("Official finishing time and real finishing time can differ.", "A stated schedule may not match when work, school, care, or another daily responsibility actually ends.", "決まった終了時刻と実際に終わる時刻は、違うことがあります。", "決められた予定と、仕事、学校、ケアなどが実際に終わる時刻は一致しない場合があります。"),
            ("The pattern varies by role, place, day, and season.", "Occupation, institution, household role, transport, workload, and season can all affect departure time.", "終わる時間は、役割、場所、曜日、季節によって変わります。", "職種、組織、家庭での役割、交通、仕事量、季節によって、帰る時刻は変わります。"),
            ("Some people do not have a fixed work or school day.", "Carers, shift workers, freelancers, retired people, and others may have no single official finishing time.", "決まった仕事や学校の一日がない人もいます。", "ケアをする人、交代勤務、フリーランス、退職した人などには、決まった終了時刻がない場合があります。"),
            ("The choice to leave on time can be normal in one place and difficult in another.", "The meaning of the choice to leave on time depends on staffing, workload, authority, and local expectations.", "定時に帰ることが普通の場所も、難しい場所もあります。", "定時に帰ることの意味は、人員、仕事量、権限、地域の期待によって異なります。"),
            ("Staying late does not always mean more useful work.", "Longer presence can reflect demand or pressure without guaranteeing productivity or quality.", "遅くまでいることが、必ずしも役立つ仕事の多さを意味しません。", "長くいることは需要や圧力を示しても、生産性や質を保証しません。"),
            ("Early departure may be possible because work is flexible.", "A person may leave earlier because of flexible hours, a completed task, care duties, or a different starting time.", "柔軟な働き方によって、早く帰れることがあります。", "柔軟な時間、作業の完了、ケアの責任、開始時刻の違いによって、早く帰る場合があります。"),
            ("A local pattern should not be treated as true for everyone.", "A careful comparison avoids turning one workplace or school into a national stereotype.", "地域の一つの習慣を、全員に当てはめるべきではありません。", "丁寧な比較では、一つの職場や学校を国全体の固定観念にしません。"),
            ("The journey home can make the real day longer.", "Transport and unpaid preparation can extend the practical day beyond the official schedule.", "帰宅までの移動で、実際の一日が長くなることがあります。", "交通や無給の準備によって、実際の一日は公式の予定より長くなります。"),
            ("Predictable endings help people plan the rest of life.", "Reliable finishing times support care, rest, relationships, transport, and other commitments.", "終わる時間が予測できると、その後の生活を計画しやすくなります。", "終業時刻が安定すると、ケア、休息、人間関係、交通、ほかの予定を支えられます。"),
            ("A fair system makes exceptions visible rather than permanent.", "Occasional extra time differs from a culture in which hidden overtime is expected every day.", "例外的な延長と、毎日の暗黙の残業は違います。", "時々の延長と、見えない残業を毎日期待する文化は異なります。"),
        ],
        [
            p("opening", "When the day really ends", "実際に終わる時間", BRIEF_OPENINGS[73] + " You can discuss work, school, care, another routine, or a general local pattern.", "住んでいる地域では、実際に仕事や学校を終えるのは何時ごろですか？ 仕事、学校、ケア、別の習慣、一般的な地域の傾向でもかまいません。", ("Is there one common time or wide variation?", "Which group or setting does your example describe?"), "When do people actually finish work, school, care, or another regular responsibility where you live? A general local pattern is fine.", "住んでいる地域では、仕事、学校、ケアなどの定期的な責任を実際に終えるのはいつですか？ 一般的な地域の傾向でかまいません。", ("Is there a typical time or substantial variation?", "Which role, institution, or routine does the example represent?"), "work-school-care-other-or-general"),
            p("expected", "Expected or unusual", "普通か例外か", "Is that finishing time generally expected in the setting, or does it vary?", "その終了時刻は、その場では普通ですか。それとも日によって変わりますか？", ("Is there an official time to compare with it?", "If there is no set schedule, what signals the end?"), "Is that finishing time treated as normal in the setting, or is there substantial variation?", "その終了時刻は、その場で普通とされていますか。それとも大きなばらつきがありますか？", ("How does any stated time compare with practice?", "If no formal schedule exists, which event or condition marks the end?"), "expected-variable-or-no-schedule"),
            p("leave-first", "Leaving before others", "先に帰ること", "What tends to happen if someone finishes or leaves before other people there?", "その場で誰かがほかの人より先に終えたり帰ったりすると、どうなることが多いですか？", ("Is the reaction supportive, neutral, mixed, or negative?", "Does the person's role change the reaction?"), "What response, if any, follows when someone finishes or leaves before others in that setting?", "その場で誰かがほかの人より先に終えたり帰ったりすると、どんな反応がありますか？", ("Is the response supportive, neutral, mixed, or critical?", "How does authority, role, or reason affect the response?"), "supportive-neutral-critical-or-none"),
            p("local-label", "A local expression", "地域の呼び方", "Is there a local expression for someone who always works or studies very late—or no common label?", "いつも遅くまで働いたり勉強したりする人を表す地域の言い方はありますか。それとも、特にありませんか？", ("If there is one, is it praise, criticism, or neutral?", "If there is none, how is the pattern described instead?"), "Is there a local label for someone who consistently works or studies very late, or is there no established expression?", "いつも遅くまで働いたり勉強したりする人を表す地域の呼び方はありますか。それとも、決まった表現はありませんか？", ("If a label exists, does it express approval, criticism, humor, or neutrality?", "If none exists, how is the behavior described?"), "local-label-or-none-no-stereotype"),
            p("tutor-fact", "My reaction and example", "先生の反応と例", "I'll tell you what surprises me—or sounds familiar—about the local pattern you described. What do you think of my reaction?", "あなたが説明した地域の傾向について、先生が意外に感じた点、または身近に感じた点を話します。その反応をどう思いますか？", ("Here is one real finishing-time pattern from my own experience; what would you like to ask about it?", "Which fact from my example should we carry into the comparison?"), "I'll explain what strikes me as surprising or familiar in the local pattern you described. How do you interpret my reaction?", "あなたが説明した地域の傾向について、先生が意外または身近に感じた点を説明します。その反応をどう受け止めますか？", ("I will now give one concrete finishing-time pattern from my own experience without treating it as true for everyone; which detail would you like me to clarify?", "Which fact from my example will matter most when we compare the two settings?"), "tutor-reacts-and-supplies-real-fact"),
            p("compare", "Compare the two examples", "二つの例を比べる", "How does my example compare with the place or setting you described?", "先生の例は、あなたが話した地域や場面と比べてどうですか？", ("What is one clear similarity?", "What is one difference, if any?"), "How does the real example I gave compare with the location or setting you described?", "先生が話した実際の例は、あなたが説明した地域や場面と比べてどうですか？", ("Which similarity is most meaningful?", "Which difference, if any, needs context rather than a national explanation?"), "answer-dependent-two-location-comparison"),
            p("change", "A fairer ending", "より公平な終わり方", "What one change could make finishing times more predictable or fair?", "終了時刻をより予測しやすく、公平にする変更を一つ挙げるとしたら何ですか？", ("Who would need to support it?", "What exception would still be reasonable?"), "Which practical change could make the end of the day more predictable or equitable?", "一日の終わりをより予測可能で公平にするために、どんな実際的な変更ができますか？", ("Whose authority or cooperation would implementation require?", "Which occasional exception would remain legitimate?"), "general-system-change"),
            p("flip", "A good end to the day", "よい一日の終わり", "Besides the time, what helps a work or school day end well?", "時刻以外に、仕事や学校の一日をよく終えるために何が役立ちますか？", ("Is it a clear handover, a finished task, or something else?", "What can prevent unfinished work from following someone home?"), "Beyond clock time, what makes the transition out of work, school, or another responsibility effective?", "時刻以外に、仕事、学校、その他の責任からうまく切り替えるには何が必要ですか？", ("Does it require a handover, closure, planning, or a boundary?", "What keeps unfinished demands from dominating the next part of the day?"), "general-close"),
        ],
    ),
    74: topic(
        "what-your-workday-actually-looks-like", "What your workday actually looks like", "실제 하루 일과", "実際の仕事の一日",
        ("Let's reveal one behind-the-scenes part of work, study, care, or daily responsibility.", "仕事、勉強、ケア、日々の責任のうち、表に見えない部分を一つ話しましょう。"),
        (("Choose a two-hour window or general example", "二時間または一般的な例を選ぶ"), ("Name invisible work", "見えない作業を挙げる"), ("Explain why it matters", "重要な理由を説明する")),
        ("The work behind the results", "結果を支える仕事"),
        [
            ("If nine to eleven was not a work period, another two-hour period or a familiar example can reveal the same hidden work.", "A different two-hour period, a familiar case, or a general example can reveal the same hidden labor.", "九時から十一時が作業の時間でなければ、別の二時間や身近な例でも、同じように見えない仕事を示せます。", "別の二時間、身近な事例、一般的な例でも、同じように見えない仕事を示せます。"),
            ("Behind the scenes, people prepare, check, coordinate, and repair.", "Visible output often depends on preparation, verification, coordination, maintenance, and recovery work.", "表に見えないところで、人は準備、確認、調整、修復をしています。", "見える成果は、準備、検証、調整、保守、復旧の仕事に支えられることがよくあります。"),
            ("Care and domestic work can also be invisible.", "Unpaid care, household administration, and emotional coordination often remain absent from formal accounts of work.", "ケアや家の仕事も、見えにくいことがあります。", "無給のケア、家庭の事務、感情面の調整は、正式な仕事の記録から抜け落ちがちです。"),
            ("A smooth result can hide the effort that prevented problems.", "Preventive work is least visible precisely when it succeeds and nothing goes wrong.", "順調な結果の裏には、問題を防いだ努力が隠れていることがあります。", "予防の仕事は、成功して問題が起きないときほど見えにくくなります。"),
            ("Invisible work may require judgment rather than many actions.", "Monitoring, anticipating, waiting, and deciding not to intervene can all be consequential work.", "見えない仕事には、多くの動作より判断が必要な場合があります。", "監視、予測、待機、介入しない判断も、結果に影響する仕事です。"),
            ("Privacy may limit how much detail can be shared.", "A useful account can describe the type and purpose of hidden work without naming clients, colleagues, or sensitive facts.", "プライバシーのため、詳しく話せない場合があります。", "顧客、同僚、機密情報を明かさず、見えない仕事の種類と目的を説明できます。"),
            ("Recognition should not create more reporting work.", "Attempts to make hidden labor visible can fail if documentation becomes another unsupported burden.", "見えない仕事を認めるために、報告の負担を増やすべきではありません。", "見えない仕事を可視化する試みも、記録が新たな無支援の負担になれば失敗します。"),
            ("Different roles hide different forms of effort.", "The least visible work varies across employment, study, care, volunteering, and household life.", "役割によって、見えにくい努力の形は異なります。", "雇用、学習、ケア、ボランティア、家庭生活では、最も見えにくい仕事が異なります。"),
            ("A fair handover names unfinished hidden work.", "Continuity improves when pending checks, risks, and dependencies are communicated rather than left implicit.", "公平な引き継ぎでは、終わっていない見えない仕事も伝えます。", "保留中の確認、リスク、依存関係を暗黙にせず伝えると、仕事の継続性が高まります。"),
            ("Understanding hidden work can change how a result is valued.", "A fuller account of labor may alter judgments about time, skill, staffing, and responsibility.", "見えない仕事を知ると、結果の評価が変わることがあります。", "仕事の全体像を知ると、時間、技能、人員、責任に対する評価が変わる場合があります。"),
        ],
        [
            p("opening", "A two-hour window", "二時間の様子", BRIEF_OPENINGS[74] + " If that time does not fit, choose another two-hour period or a familiar example.", "今朝九時から十一時まで、何をしていましたか？ その時間が合わなければ、別の二時間や身近な例でもかまいません。", ("Which part would another person have seen?", "What made this period typical or unusual?"), "What occupied the period from nine to eleven this morning? If it was not a work period, use another two-hour window or a familiar example.", "今朝九時から十一時までは何をしていましたか？ 仕事の時間でなければ、別の二時間や身近な例を使ってください。", ("Which activity would have been visible to an observer?", "What made the selected period typical or unusual?"), "personal-other-period-familiar-or-general"),
            p("walkthrough", "Walk through the period", "時間の流れ", "What happened first, next, and last in that two-hour period?", "その二時間では、最初、次、最後に何が起きましたか？", ("Where did the plan change?", "If the example is general, what sequence is typical?"), "What happened from the first activity to the last in the selected period, or what sequence is typical in a general example?", "選んだ時間では、最初の活動から最後まで何が起きましたか。それとも、一般的な例ではどんな流れが典型的ですか？", ("At which point did the sequence depart from the plan?", "If the example is general, which variation is most common?"), "personal-familiar-or-general-sequence"),
            p("longest", "What takes longest", "最も時間がかかること", "Which part takes the most time, and why?", "どの部分に最も時間がかかり、なぜですか？", ("Is the time spent doing, waiting, checking, or coordinating?", "Could an outsider see why it takes so long?"), "Which activity consumes the largest share of the period, and what accounts for that duration?", "どの活動がその時間の最も大きな部分を占め、なぜそれだけ時間がかかりますか？", ("Does the duration come from execution, waiting, verification, or coordination?", "Would the reason be visible to an outsider?"), "selected-example-duration"),
            p("preference", "A part you value", "大切に思う部分", "Which part do you or the person in the example like, dislike, or feel neutral about?", "自分や例の人は、どの部分が好き、苦手、または特に気になりませんか？", ("What feature creates that response?", "Would a small change alter it?"), "Which part of the routine is satisfying, frustrating, or emotionally neutral for the person in the example?", "例の人にとって、日課のどの部分が満足、負担、または感情的に中立ですか？", ("Which feature of the activity produces that response?", "Would a modest change alter the experience?"), "like-dislike-or-neutral"),
            p("hidden", "What would surprise an outsider", "外からは意外なこと", "What happens behind the scenes that might surprise an outsider?", "表に見えないところで、外の人が驚きそうな何が起きていますか？", ("Why is that work easy to miss?", "What would happen if nobody did it?"), "Which preparation, verification, care, or coordination happens behind the scenes and would surprise an outsider?", "表に見えないところで、外の人が驚きそうな準備、検証、ケア、調整は何ですか？", ("Which feature keeps the work out of view?", "What consequence would follow if it were omitted?"), "productive-new-term-visible"),
            p("change", "How the routine changed", "変わった日課", "Has this routine changed, stayed similar, or remained unclear over time?", "この日課は、時間とともに変わりましたか、ほぼ同じですか、それともはっきりしませんか？", ("If it changed, which step moved most?", "If it stayed similar or is unclear, what appears stable?"), "Has the routine evolved, remained broadly stable, or become difficult to compare over time?", "この日課は変化しましたか、広く安定していますか、それとも時間を通した比較が難しいですか？", ("If it evolved, which activity or responsibility shifted most?", "If it stayed stable or cannot be compared, which feature remains identifiable?"), "changed-stable-or-unclear"),
            p("cut", "What to remove", "減らしたいこと", "Which part would you cut, shorten, or keep as it is?", "どの部分をなくす、短くする、またはそのままにしますか？", ("If you would change it, what would improve?", "If you would keep it, what useful function already works?"), "Which element should be removed, reduced, redesigned, or deliberately retained?", "どの要素をなくす、減らす、設計し直す、または意識して残すべきですか？", ("If you would change it, which outcome would improve?", "If you would retain it, which necessary function or protection already works?"), "remove-reduce-redesign-or-keep"),
            p("flip", "See the whole day", "一日全体を見る", "What question would help an outsider understand this routine fairly?", "外の人がこの日課を公平に理解するには、どんな質問が役立ちますか？", ("Who could answer it?", "What false assumption might the answer correct?"), "Which question would give an outsider a fairer account of the visible and hidden work in this routine?", "外の人が、この日課の見える仕事と見えない仕事をより公平に理解するには、どんな質問が役立ちますか？", ("Whose perspective would be most informative?", "Which mistaken assumption might the answer correct?"), "curious-close"),
        ],
    ),
    75: topic(
        "one-thing-you-would-change-about-your-work-or-school", "One thing you would change about your work or school", "일이나 학교에서 바꾸고 싶은 한 가지", "仕事や学校で変えたい一つのこと",
        ("Let's raise an issue and propose one realistic change, with personal, familiar, or general routes.", "自分、身近、一般的な例を使って、問題を提起し、現実的な変更を一つ提案しましょう。"),
        (("Name one issue", "問題を一つ挙げる"), ("Explain who is affected", "影響を受ける人を説明する"), ("Offer and test a proposal", "提案を出して検討する")),
        ("A useful change starts with a clear problem", "役立つ変更は明確な問題から始まる"),
        [
            ("A current workplace or school is not required; a familiar, former, public, or imagined setting works too.", "A familiar, former, public, or hypothetical setting can replace a current workplace or school.", "現在の職場や学校がなくても、身近な人の例、以前いた場所、公に知られた例、想像上の場を使えます。", "現在の職場や学校がなくても、身近な人の例、以前いた場所、公に知られた例、仮定の場を使えます。"),
            ("A specific issue is easier to change than a broad complaint.", "A proposal becomes more credible when it identifies the affected process, people, and evidence.", "広い不満より、具体的な問題のほうが変えやすくなります。", "影響を受ける手順、人、証拠を特定すると、提案の信頼性が高まります。"),
            ("The choice to raise an issue can carry different risks for different people.", "The personal cost of deciding to raise an issue can vary with authority, contract, identity, and local culture.", "問題を提起するリスクは、人によって違います。", "問題を提起する個人的な負担は、権限、契約、属性、地域の文化によって変わります。"),
            ("A good proposal explains who benefits and who carries the cost.", "Reform is easier to evaluate when its benefits, burdens, and unintended effects are explicit.", "よい提案は、誰が利益を得て、誰が負担するかを説明します。", "利益、負担、予期しない影響が明確なら、変更を評価しやすくなります。"),
            ("The person closest to a problem may not control the solution.", "Responsibility for reporting an issue is different from authority and resources to resolve it.", "問題に最も近い人が、解決を決められるとは限りません。", "問題を伝える責任と、それを解決する権限や資源は別です。"),
            ("For a low-risk proposal, a small trial can test a change before it spreads.", "When the issue is safe to test, a limited pilot can produce evidence, expose side effects, and make revision possible.", "リスクの低い提案なら、小さく試すことで、広げる前に変更を検証できます。", "安全に試せる問題なら、範囲を絞った試行で証拠を集め、副作用を見つけ、修正できます。"),
            ("Some concerns need a confidential or formal route.", "Safety, harassment, discrimination, or legal concerns may require protected channels rather than open debate.", "内容によっては、秘密を守る正式な経路が必要です。", "安全、嫌がらせ、差別、法的な懸念には、公開の議論ではなく保護された経路が必要な場合があります。"),
            ("No proposal is improved by inventing agreement.", "A learner may discuss an undecided, rejected, private, or hypothetical proposal honestly.", "合意がないのに、あることにする必要はありません。", "未決定、却下、非公開、仮定の提案を正直に話せます。"),
            ("Opposition may reveal a real constraint.", "A strong objection can identify cost, feasibility, fairness, or risk that the original proposal missed.", "反対意見から、実際の制約が見えることがあります。", "強い反対意見は、元の提案が見落とした費用、実現可能性、公平性、リスクを示すことがあります。"),
            ("A respectful response separates the issue from the person.", "Constructive disagreement tests evidence and design without questioning the speaker's worth or motives.", "丁寧な応答は、問題と人を分けて考えます。", "建設的な反対は、話し手の価値や動機を疑わず、証拠と設計を検討します。"),
        ],
        [
            p("opening", "One change", "一つの変更", BRIEF_OPENINGS[75] + " If you do not currently work or study there, use a familiar, former, or general setting.", "働いたり学んだりする場所で、明日一つ変えるなら何ですか？ 現在そのような場所がなければ、身近な人の例、以前いた場所、一般的な例でもかまいません。", ("What exact problem would the change address?", "Who experiences that problem?"), "What is one thing you would change tomorrow about a place where people work or study? A familiar, former, public, or hypothetical setting is valid.", "人が働いたり学んだりする場所で、明日一つ変えるとしたら何ですか？ 身近な人の例、以前いた場所、公に知られた例、仮定の場でもかまいません。", ("Which precisely defined problem would the change address?", "Who is directly affected by that problem?"), "personal-familiar-former-public-or-hypothetical"),
            p("unchanged", "Why it has not changed", "変わっていない理由", "Why has the issue not changed yet—or is it already being discussed?", "その問題はなぜまだ変わっていないのですか。それとも、すでに話し合われていますか？", ("Is the main barrier authority, cost, information, or disagreement?", "Who has the power to change it?"), "Why has the issue remained unchanged, or what discussion is already under way?", "その問題が変わっていないのはなぜですか。それとも、すでにどんな話し合いが進んでいますか？", ("Does the main barrier concern authority, resources, evidence, or disagreement?", "Which role has the authority to act?"), "unchanged-or-already-discussed"),
            p("objection", "Who might object", "反対する人", "Who might object to the change, if anyone, and why?", "その変更に反対する人がいるとすれば誰で、なぜですか？", ("What concern would they raise?", "If no one is likely to object, what could still slow the change?"), "Who, if anyone, would oppose the proposal, and what legitimate concern might they raise?", "その提案に反対する人がいるとすれば誰で、どんな妥当な懸念を示しそうですか？", ("Would the concern involve cost, fairness, risk, or feasibility?", "If no opposition is likely, which practical constraint could still delay action?"), "objector-or-no-objection"),
            p("cost", "What it would cost", "必要な負担", "What would the change cost in time, money, workload, or another resource?", "その変更には、時間、お金、作業量、または別の資源がどのくらい必要ですか？", ("Who would carry that cost?", "If the cost is small, what other obstacle remains?"), "What costs or burdens would implementation create, and who would carry them?", "その変更を実行すると、どんな費用や負担が生まれ、誰がそれを担いますか？", ("Would the burden involve time, money, staffing, authority, or attention?", "If the material cost is low, which nonfinancial constraint remains?"), "cost-burden-or-low-cost"),
            p("raised", "Whether it was raised", "提起したか", "Has anyone raised the issue—or would doing so openly be unsafe or inappropriate?", "その問題を誰かが提起しましたか。それとも、公に提起するのは安全でない、または不適切ですか？", ("If it was raised, which route was used?", "If not, would a private, representative, or formal route be safer?"), "Has the issue been raised, or would open reporting create an unacceptable risk?", "その問題は提起されましたか。それとも、公に報告すると受け入れられない危険が生じますか？", ("If it was raised, was the route direct, confidential, representative, or formal?", "If it was not, which protected route—or decision not to act—would be safer?"), "raised-private-protected-or-not-raised"),
            p("result", "What happened next", "その後の結果", "If the issue was raised, what happened? If not, what prevented it?", "問題を提起したなら、その後どうなりましたか。提起しなかったなら、何が理由でしたか？", ("Was the response acceptance, rejection, delay, or no answer?", "What did that result show about the next safe step?"), "What followed if the issue was raised, or what prevented it from being raised?", "問題を提起したなら何が起きましたか。提起しなかったなら、何がそれを妨げましたか？", ("Did the response produce acceptance, rejection, delay, a private process, or no answer?", "What does that outcome indicate about the next safe and realistic step?"), "raised-result-or-protected-nonaction"),
            p("next", "The safest next step", "安全な次の一歩", "What is the safest next step: a small test, more evidence, a private or formal route, or no action for now?", "最も安全な次の一歩は、小さな試行、追加の証拠、非公開または正式な経路、それとも今は行動しないことですか？", ("If a test is safe, what would count as improvement?", "If action is unsafe, what protection or support is needed first?"), "Which next step is proportionate: a limited test, stronger evidence, a protected channel, or deliberate nonaction for now?", "次の一歩として適切なのは、範囲を絞った試行、より強い証拠、保護された経路、それとも今は意図的に行動しないことですか？", ("If a trial is appropriate, which measure and stop condition would make it safe?", "If action is unsafe, which protection, representative, or formal support must come first?"), "trial-evidence-protected-route-or-no-action"),
            p("flip", "A respectful reply", "丁寧な応答", "How should a decision-maker respond when they cannot accept the proposal?", "提案を受け入れられないとき、意思決定者はどう応答すべきですか？", ("What part should they acknowledge?", "What next route or evidence could they offer?"), "How can a decision-maker reject or defer a proposal without dismissing the person who raised it?", "問題を提起した人を退けることなく、意思決定者は提案の却下や延期をどう伝えられますか？", ("Which concern or contribution should be acknowledged explicitly?", "Which next review point, alternative, or evidence could keep the process credible?"), "respectful-close"),
        ],
    ),
}

# Reviewed prompt layer. The tutor may skip freely through the pool, so every
# main question must work without an earlier page and without asking the learner
# to select a personal/familiar/hypothetical route first.
MAIN_REVISIONS = {
    (64, 1): (BRIEF_OPENINGS[64], "初めての給料の印象的な使い道には、どんなものがありますか？", "How do people often use their first earnings in a memorable way?", "人は初めての収入を、どのように印象に残る形で使うことが多いですか？"),
    (64, 2): ("Why can a first paycheck feel important even when the amount is small?", "金額が小さくても、初めての給料が大切に感じられるのはなぜですか？", "Why can the emotional value of first earnings exceed their monetary value?", "なぜ、初めての収入の感情的な価値が、金銭的な価値を上回ることがあるのですか？"),
    (64, 3): ("What kinds of work can produce someone's first earnings?", "どんな仕事が、誰かの初めての収入になり得ますか？", "Which forms of work can lead to a person's first earnings?", "どのような形の仕事が、人の初めての収入につながり得ますか？"),
    (64, 4): ("What is a meaningful first use for a paycheck?", "初めての給料の意味のある使い道は何ですか？", "What first use can give a paycheck lasting meaning?", "どんな最初の使い道が、給料に長く残る意味を与えますか？"),
    (64, 5): ("Who do people usually tell about their first paycheck?", "人は初めての給料のことを、普通誰に話しますか？", "Who is most likely to hear about someone's first earnings?", "誰かの初めての収入について、最も聞きそうなのは誰ですか？"),
    (64, 6): ("How would you use a small unexpected payment today?", "今、予想外の小さな収入があったら、どう使いますか？", "How would you divide a modest unexpected payment among current priorities?", "今の優先事項に合わせて、予想外の小額の収入をどう分けますか？"),
    (64, 7): ("What can earning money for the first time teach someone?", "初めてお金を稼ぐことから、人は何を学べますか？", "What can first earnings reveal about work, money, or independence?", "初めての収入は、仕事、お金、自立について何を示し得ますか？"),
    (65, 1): (BRIEF_OPENINGS[65], "何かを終えることが、本当に満足感のあるものになるのはどんなときですか？", "What makes completing an effort feel genuinely meaningful?", "一つの努力を完了することが、本当に意味のあるものになるのは何ですか？"),
    (65, 2): ("What kind of effort feels especially good to finish?", "どんな努力を終えると、特にうれしく感じますか？", "Which kind of demanding effort creates the strongest sense of completion?", "どのような大変な努力が、最も強い達成感を生みますか？"),
    (65, 3): ("Does recognition from other people change how proud someone feels?", "周りから認められることで、誇らしさは変わりますか？", "How does external recognition affect a person's pride in completed work?", "周囲からの評価は、完了した仕事への誇りにどう影響しますか？"),
    (65, 4): ("Why can saying “I'm proud of this” feel uncomfortable?", "「これを誇りに思う」と言うことが、気まずく感じられるのはなぜですか？", "Why can openly expressing pride feel like boasting?", "誇りを率直に表現することが、自慢のように感じられるのはなぜですか？"),
    (65, 5): ("Why can one finished task matter more than another?", "なぜ、一つの完了した作業が、別の作業より大切に感じられるのですか？", "What gives one completed effort more significance than another?", "一つの完了した努力が、別の努力より大きな意味を持つのは何ですか？"),
    (66, 1): (BRIEF_OPENINGS[66], "普通の瞬間が成功のように感じられるのはどんなときですか？", "What can make an ordinary moment register as genuine success?", "普通の瞬間が本物の成功と感じられるのは何ですか？"),
    (66, 2): ("What often happens just before a successful moment?", "成功した瞬間の直前には、どんなことが起こることが多いですか？", "Which conditions often precede a meaningful success?", "意味のある成功の前には、どのような条件があることが多いですか？"),
    (66, 3): ("Does success matter more when another person sees it?", "誰かに見てもらうと、成功はより大切になりますか？", "How does being witnessed change the meaning of success?", "誰かに見られることで、成功の意味はどう変わりますか？"),
    (66, 4): ("Which feeling best matches success: excitement, relief, confidence, or calm?", "成功に最も合う気持ちは、興奮、安心、自信、落ち着きのどれですか？", "Which emotional response most clearly signals success?", "成功を最もはっきり示す感情は何ですか？"),
    (66, 5): ("How long does a feeling of success usually last?", "成功した感覚は、普通どのくらい続きますか？", "What tends to remain after the immediate feeling of success fades?", "成功の直後の感覚が薄れた後、何が残ることが多いですか？"),
    (66, 7): ("How can a person's idea of success change over time?", "成功についての考えは、時間とともにどう変わり得ますか？", "How do experience and changing priorities reshape a definition of success?", "経験や優先事項の変化は、成功の定義をどう変えますか？"),
    (67, 1): (BRIEF_OPENINGS[67], "どのスキルを最も上達させたいですか？", "Which skill would be most worthwhile for you to improve?", "どのスキルを上達させることが、自分にとって最も価値がありますか？"),
    (67, 2): ("What is a good first method for improving a new skill?", "新しいスキルを上達させるための、よい最初の方法は何ですか？", "Which first method gives a learner useful evidence about how to improve?", "どの最初の方法が、上達のための有用な手がかりを学習者に与えますか？"),
    (67, 6): ("When is a skill no longer worth pursuing?", "どんなときに、スキルを追い求め続ける価値がなくなりますか？", "When should a learner redirect effort away from a skill?", "どんなときに、学習者はそのスキルから努力を別の方向に向けるべきですか？"),
    (67, 7): ("What small action can help someone improve this week?", "今週、上達の助けになる小さな行動は何ですか？", "Which modest repeatable action can produce useful progress in one week?", "一週間で有用な進歩を生む、小さく繰り返せる行動は何ですか？"),
    (68, 1): (BRIEF_OPENINGS[68], "使う以外に、人はお金をどう扱えますか？", "Which purposes can money serve besides immediate spending?", "目の前で使う以外に、お金はどんな目的に使えますか？"),
    (68, 2): ("Which non-spending use of money matters most?", "使う以外のお金の使い方で、最も大切なのは何ですか？", "Which non-spending purpose deserves the highest priority?", "使う以外の目的で、最も優先すべきなのは何ですか？"),
    (68, 3): ("What usually helps someone begin setting money aside?", "お金を取っておき始めるのに、普通何が役立ちますか？", "Which condition most often makes setting money aside realistic?", "お金を取っておくことを現実的にする条件は何ですか？"),
    (68, 4): ("What makes a saving or investment approach workable?", "貯蓄や投資の方法が無理なく続くのはどんなときですか？", "What determines whether a financial approach remains viable?", "お金の扱い方が実行可能であり続けるかを決めるのは何ですか？"),
    (68, 5): ("What most influences how people handle money they do not spend?", "人が使わないお金をどう扱うかに、最も影響するのは何ですか？", "Which influence most strongly shapes how people allocate money they do not spend?", "人が使わないお金をどう配分するかに、最も強く影響するのは何ですか？"),
    (68, 6): ("Which money habits should be recommended only in some situations?", "どのお金の習慣は、限られた状況でだけ勧めるべきですか？", "Which financial practices should be recommended only conditionally?", "どの金融行動は、条件付きでのみ勧めるべきですか？"),
    (68, 7): ("Which financial action deserves the most caution?", "どの金融行動に、最も注意が必要ですか？", "Which financial action should require the strictest safeguards?", "どの金融行動に、最も厳しい保護策が必要ですか？"),
    (69, 1): (BRIEF_OPENINGS[69], "どの仕事を一年間試してみたいですか？", "Which alternative career would be most interesting to try for one year?", "どの別のキャリアを一年間試すと最も面白そうですか？"),
    (69, 2): ("What might an ordinary day in that career look like?", "その仕事の普通の一日は、どんなものになりそうですか？", "Which activities and responsibilities would define an ordinary day in that career?", "その仕事の普通の一日を形作る活動や責任は何ですか？"),
    (69, 3): ("What makes that career appealing?", "その仕事のどんなところが魅力的ですか？", "What is the strongest source of attraction in that career?", "その仕事の最も強い魅力は何ですか？"),
    (69, 4): ("What would make that career realistic to try?", "その仕事を試すことが現実的になるのは、どんな条件があるときですか？", "Which conditions would make that career genuinely available?", "どのような条件があれば、そのキャリアが本当に選べるものになりますか？"),
    (69, 5): ("Who is a good example of someone who changed career direction dramatically?", "キャリアの方向を大きく変えた人のよい例は誰ですか？", "Who offers an instructive example of a major career change?", "大きなキャリアチェンジの参考になる例は誰ですか？"),
    (69, 6): ("How can people feel about a career path they did not choose?", "選ばなかったキャリアについて、人はどんな気持ちになり得ますか？", "What emotions can an unrealized career path produce over time?", "実現しなかったキャリアは、時間とともにどんな感情を生み得ますか？"),
    (69, 7): ("Which part of another career can be added to life without changing jobs?", "仕事を変えずに、別のキャリアのどの部分を生活に取り入れられますか？", "Which value or activity from another career can be incorporated without a complete transition?", "完全に転職せずに、別のキャリアのどの価値や活動を取り入れられますか？"),
    (70, 1): (BRIEF_OPENINGS[70], "AIが最も大きく変えた日常の作業は何ですか？", "Which everyday process has AI changed most substantially?", "AIが最も大きく変えた日常の過程は何ですか？"),
    (70, 2): ("How was a common AI-assisted task done before and now?", "AIが使われるよくある作業は、以前と今でどう変わりましたか？", "How does a common process operate before and after AI is introduced?", "AIが導入される前と後で、よくある過程はどう進みますか？"),
    (70, 3): ("Does AI usually make results better, worse, or simply different?", "AIは通常、結果をよくしますか、悪くしますか、それとも単に変えますか？", "Does AI generally improve output, weaken it, or change the kind of work produced?", "AIは一般に、成果物を改善しますか、弱めますか、それとも生み出される仕事の種類を変えますか？"),
    (70, 4): ("What new work can an AI tool create?", "AIツールは、どんな新しい作業を生み出すことがありますか？", "Which verification or correction tasks can AI create?", "AIはどんな検証や修正の作業を生み出すことがありますか？"),
    (70, 6): ("Who should check AI-assisted work?", "AIを使った仕事は、誰が確認すべきですか？", "Who should retain responsibility for reviewing AI-assisted work?", "AIを使った仕事の確認責任は、誰が持ち続けるべきですか？"),
    (71, 1): (BRIEF_OPENINGS[71], "人が本気でキャリアチェンジを考えるのは、何がきっかけですか？", "Which conditions make a career change worth serious consideration?", "どのような条件で、キャリアチェンジを本気で検討する価値が生まれますか？"),
    (71, 2): ("Which pressure most often pushes someone toward a career change?", "人をキャリアチェンジに向かわせることが多いプレッシャーは何ですか？", "Which structural pressure most often makes a career change necessary?", "キャリアチェンジを必要にすることが多い構造的なプレッシャーは何ですか？"),
    (71, 3): ("What makes a different career direction attractive?", "別のキャリアの方向が魅力的になるのは何ですか？", "What makes an alternative career direction compelling?", "別のキャリアの方向に強くひかれるのは何ですか？"),
    (71, 4): ("What makes a career change difficult or risky?", "キャリアチェンジを難しくしたり、リスクのあるものにしたりするのは何ですか？", "Which constraints make a career transition genuinely risky?", "どのような制約が、キャリアの移行を本当にリスクのあるものにしますか？"),
    (71, 5): ("Why do people postpone a career change?", "なぜ人はキャリアチェンジを延期するのですか？", "Why can postponing a career transition be a rational decision?", "キャリアの移行を延期することが、合理的な決定になり得るのはなぜですか？"),
    (71, 7): ("Who should someone talk to before changing careers?", "キャリアを変える前に、誰と話すとよいですか？", "Whose perspective is most useful before a major career transition?", "大きなキャリアの移行の前に、誰の視点が最も役立ちますか？"),
    (72, 1): (BRIEF_OPENINGS[72], "マネージャー、先生、コーチから学ぶ価値が生まれるのは、どんなときですか？", "Which qualities make a manager, teacher, or coach genuinely instructive?", "マネージャー、先生、コーチを本当に学べる存在にするのは、どんな特徴ですか？"),
    (72, 2): ("What actions make guidance useful?", "どんな行動が、指導を役立つものにしますか？", "Which observable practices make guidance effective?", "どのような観察できる実践が、指導を効果的にしますか？"),
    (72, 3): ("How should a good guide respond when something goes wrong?", "何かがうまくいかないとき、よい指導者はどう応じるべきですか？", "How should an effective guide handle mistakes or weak performance?", "効果的な指導者は、間違いや低い成果にどう対応すべきですか？"),
    (72, 5): ("Which ideas from a good guide tend to last?", "よい指導者から得た考えの中で、長く残りやすいのは何ですか？", "Which principle from effective guidance tends to remain useful over time?", "効果的な指導から得た原則の中で、時間がたっても役立ちやすいのは何ですか？"),
    (72, 6): ("Should someone always respond when advice helps them?", "助言が役に立ったとき、必ず反応を返すべきですか？", "Does useful guidance always require a direct response from the learner?", "役立つ指導には、必ず学習者からの直接の反応が必要ですか？"),
    (73, 1): (BRIEF_OPENINGS[73], "住んでいる場所では、人は普通何時に仕事や学校を終えますか？", "When do people actually finish work or school where you live?", "住んでいる場所では、人は実際に何時に仕事や学校を終えますか？"),
    (73, 2): ("How different are official and real finishing times where you live?", "住んでいる場所では、公式の終了時刻と実際の時刻はどのくらい違いますか？", "How closely do official finishing times match actual practice where you live?", "住んでいる場所では、公式の終了時刻と実際の運用はどの程度一致しますか？"),
    (73, 4): ("How does your language describe someone who always works or studies late?", "いつも遅くまで働いたり勉強したりする人を、あなたの言語ではどう表しますか？", "How does local language describe someone who consistently works or studies late?", "いつも遅くまで働いたり勉強したりする人を、地域の言葉ではどう表しますか？"),
    (73, 5): ("I'll share a real finishing-time pattern from my experience. What seems surprising or familiar about it?", "私の経験から、実際の終了時刻のパターンを一つ話します。どこが意外で、どこが身近に感じますか？", "I'll share one concrete finishing-time pattern from my experience. Which detail deserves comparison?", "私の経験から、具体的な終了時刻のパターンを一つ話します。どの詳細を比較すべきですか？"),
    (73, 6): ("How can finishing times differ across two places you know about?", "知っている二つの場所で、終了時刻はどう異なり得ますか？", "How can actual finishing times differ across two settings?", "二つの環境で、実際の終了時刻はどう異なり得ますか？"),
    (74, 1): (BRIEF_OPENINGS[74], "最近の二時間を一つ選んでください。その時間を何で過ごしましたか？", "Choose any recent two-hour window. Which activities filled it?", "最近の二時間を一つ選んでください。どんな活動がその時間を占めましたか？"),
    (74, 2): ("What sequence of activities often fills a typical two-hour period?", "よくある二時間は、どんな活動の順番で進むことが多いですか？", "Which sequence best represents a typical two-hour period?", "よくある二時間を最もよく表す活動の流れは何ですか？"),
    (74, 3): ("Which part of a daily routine usually takes the most time?", "日常の流れの中で、普通最も時間がかかるのはどの部分ですか？", "Which activity consumes the largest share of a typical routine?", "よくある日課の中で、最も大きな時間を占める活動は何ですか？"),
    (74, 4): ("Which part of a daily routine tends to feel satisfying or frustrating?", "日常の流れのどの部分が、満足感やストレスを感じやすいですか？", "Which part of a routine is most likely to feel satisfying, frustrating, or neutral?", "日課のどの部分が、満足、不満、または無感情に感じられやすいですか？"),
    (74, 6): ("How do daily work, study, or care routines change over time?", "仕事、勉強、ケアの日常的な流れは、時間とともにどう変わりますか？", "How do ordinary work, study, or care routines evolve over time?", "仕事、勉強、ケアの普通の日課は、時間とともにどう変化しますか？"),
    (74, 7): ("Which part of a daily routine is most worth cutting or shortening?", "日常の流れの中で、最もなくす、または短くする価値があるのはどの部分ですか？", "Which routine element should be removed, reduced, redesigned, or deliberately retained?", "日課のどの要素をなくす、減らす、設計し直す、または意識して残すべきですか？"),
    (75, 1): (BRIEF_OPENINGS[75], "人が働いたり学んだりする場所で、何を変えたいですか？", "What would you change about a place where people work or study?", "人が働いたり学んだりする場所で、何を変えたいですか？"),
    (75, 2): ("Why do obvious problems at work or school often remain unchanged?", "仕事や学校の明らかな問題が、なぜ変わらないことが多いのですか？", "Why can a clearly defined workplace or school problem remain unresolved?", "明確に定義された職場や学校の問題が、なぜ未解決のまま残ることがあるのですか？"),
    (75, 3): ("Who might object to a proposed change, and why?", "提案された変更に反対するのは誰で、なぜですか？", "Who might oppose a proposal, and which legitimate concern could they raise?", "提案に反対する可能性があるのは誰で、どんな正当な懸念を示し得ますか？"),
    (75, 4): ("What can a change cost in time, money, or workload?", "一つの変更には、時間、お金、作業量のどんな負担がかかり得ますか？", "Which costs and burdens can implementation create?", "実施によって、どんな費用や負担が生じ得ますか？"),
    (75, 5): ("What is the safest way to raise a problem at work or school?", "仕事や学校の問題を提起する最も安全な方法は何ですか？", "Which route can raise a workplace or school problem with the least unnecessary risk?", "不必要なリスクを最も抑えて、職場や学校の問題を提起できるのはどの経路ですか？"),
    (75, 6): ("What should happen after someone raises an issue?", "誰かが問題を提起した後、何が起こるべきですか？", "Which process should follow after an issue is raised?", "問題が提起された後、どのような手順が続くべきですか？"),
    (75, 7): ("How should people choose between a small test, stronger evidence, or a protected route?", "小さな試行、より強い証拠、保護された経路の中から、どう選ぶべきですか？", "How should a decision-maker choose among a limited trial, stronger evidence, and a protected channel?", "意思決定者は、範囲を限った試行、より強い証拠、保護された経路の中からどう選ぶべきですか？"),
}

for (_topic_no, _prompt_no), (_a, _a_ja, _f, _f_ja) in MAIN_REVISIONS.items():
    _item = TOPICS[_topic_no]["prompts"][_prompt_no - 1]
    _item.update(accessible=_a, accessible_ja=_a_ja, full=_f, full_ja=_f_ja)

# Tutor-only probes stay optional and deepen the page. These replacements remove
# administrative branching while retaining two useful directions.
for _topic in TOPICS.values():
    for _item in _topic["prompts"]:
        for _variant in VARIANTS:
            _key = f"{_variant}_followups"
            _clean = []
            for _probe in _item[_key]:
                _probe = re.sub(r"^(?:If [^,;]+[,;]\s*|For (?:a|the|your) [^,;]+[,;]\s*|Without [^,;]+[,;]\s*|A (?:rough|broad|general|familiar|hypothetical) [^;]+;\s*)", "", _probe, flags=re.I)
                _probe = _probe[:1].upper() + _probe[1:]
                _clean.append(_probe)
            _item[_key] = tuple(_clean)
        _item["safety"] = "standalone-opinion-or-scenario"


# Short, positive can-dos. These describe the lesson's actual conversation
# rather than explaining privacy fallbacks or listing exceptions.
GOAL_REVISIONS = {
    64: ("Let's talk about why first earnings can be memorable.", "初めての収入が記憶に残る理由について話しましょう。"),
    65: ("Let's talk about what makes finishing something feel meaningful.", "何かをやり終えることが意味を持つ理由について話しましょう。"),
    66: ("Let's talk about ordinary moments that can feel like success.", "成功のように感じられる日常の瞬間について話しましょう。"),
    67: ("Let's talk about practical ways to improve a skill.", "スキルを伸ばすための実践的な方法について話しましょう。"),
    68: ("Let's talk about what money can do besides pay for things.", "物を買う以外に、お金にできることについて話しましょう。"),
    69: ("Let's explore what makes another career interesting.", "別のキャリアが興味深く感じられる理由を考えましょう。"),
    70: ("Let's talk about how AI changes tasks and responsibility.", "AIが作業と責任をどう変えるかについて話しましょう。"),
    71: ("Let's talk about why people consider changing careers.", "人がキャリア変更を考える理由について話しましょう。"),
    72: ("Let's talk about what makes guidance useful.", "役立つ指導とは何かについて話しましょう。"),
    73: ("Let's compare official and actual finishing times.", "決まった終了時刻と実際の終了時刻を比べましょう。"),
    74: ("Let's uncover the visible and hidden work in a daily routine.", "日々の中で見える仕事と見えない仕事について話しましょう。"),
    75: ("Let's describe a problem and propose a realistic change.", "問題を説明し、現実的な変更を提案しましょう。"),
}
for _topic_no, _goal in GOAL_REVISIONS.items():
    TOPICS[_topic_no]["goal"] = _goal

# Keep the title meaningful while allowing the bilingual inline heading to fit
# the narrow lesson card without changing shared CSS.
TOPICS[73]["article_title"] = (
    "Official time and real time",
    "決まった時刻と実際の時刻",
)


# Article sentences should teach the topic itself. They must not narrate a
# fallback route, explain what a learner may disclose, or preserve an obsolete
# prompt such as the former fixed 9-to-11 window.
ARTICLE_REVISIONS = {
    (64, 8): ("People often remember the first choice they made with money they earned.", "The first decision made with earned money can become a lasting marker of independence.", "自分で稼いだお金で最初にした選択は、記憶に残りやすいものです。", "自分で得た収入について最初に下した判断は、自立を示す長く残る節目になることがあります。"),
    (66, 7): ("Comparing several small successes can reveal what progress means to a person.", "Comparing different forms of progress can reveal the standards a person uses to recognize success.", "いくつかの小さな成功を比べると、その人にとっての進歩が見えてきます。", "さまざまな進歩を比べると、何を成功と認めるかの基準が見えてきます。"),
    (67, 7): ("Watching how other people practise can suggest a new method.", "Observed examples can broaden the range of methods a learner considers worth testing.", "ほかの人の練習方法を見ると、新しいやり方のヒントが得られます。", "ほかの人の例を見ることで、試す価値のある方法の幅を広げられます。"),
    (68, 6): ("People can compare money choices by purpose instead of exact amounts.", "Comparing financial choices by purpose and trade-off can be more informative than comparing balances.", "正確な金額ではなく、目的に注目してお金の選択を比べることができます。", "残高を比べるより、目的とトレードオフでお金の選択を比べるほうが有益なことがあります。"),
    (68, 8): ("Dividing a sample amount among several goals can make priorities clearer.", "Allocating a fixed amount across competing goals can expose priorities and opportunity costs.", "一定のお金をいくつかの目的に分けると、優先順位が明確になります。", "限られた金額を複数の目的に配分すると、優先順位と機会費用が見えてきます。"),
    (69, 2): ("Career paths can include paid work, study, care, creative work, and service.", "A career path can combine paid employment with study, care, creative practice, public service, or enterprise.", "キャリアの進路には、仕事、勉強、ケア、創作、社会への貢献などがあります。", "キャリアの進路は、有給の仕事に加えて、勉強、ケア、創作活動、公共への貢献、事業などを組み合わせることができます。"),
    (70, 8): ("AI can affect a routine indirectly through the tools and services around it.", "Even without direct use, AI can change a routine through institutions, colleagues, products, and public services.", "AIを直接使わなくても、周りの道具やサービスを通して日常が変わることがあります。", "AIを直接使わなくても、組織、同僚、製品、公共サービスを通じて日常が変化することがあります。"),
    (71, 2): ("A career change can also mean moving between study, care, paid work, and retirement.", "Career transitions include movement among education, care, paid employment, self-employment, and retirement.", "キャリア変更には、勉強、ケア、有給の仕事、退職の間の移動も含まれます。", "キャリアの移行には、教育、ケア、有給雇用、自営業、退職の間の移動も含まれます。"),
    (74, 1): ("Any two-hour window can reveal how a daily routine is really organised.", "A carefully described two-hour window can expose the structure and interruptions of an ordinary routine.", "どの2時間を選んでも、日常が実際にどう組み立てられているかが見えてきます。", "2時間を丁寧にたどると、普段の流れの構造や中断が見えてきます。"),
    (75, 1): ("Places where people work or study often contain problems that have become normal.", "Workplaces and learning environments can normalize problems that still deserve deliberate attention.", "働いたり学んだりする場所では、問題が当たり前になっていることがあります。", "職場や学習環境では、本来きちんと検討すべき問題が日常化していることがあります。"),
    (75, 8): ("A proposal can be useful even when it is revised, delayed, or rejected.", "A proposal can clarify priorities and constraints even when it remains private, is revised, or is not adopted.", "提案は、修正されたり、延期されたり、却下されたりしても役立つことがあります。", "提案は、非公開のままでも、修正されても、採用されなくても、優先事項と制約を明確にできます。"),
    (67, 4): ("Failing to stick with a routine once does not mean a person cannot improve.", "Breaking one routine does not settle whether a person can make persistent progress.", "一度習慣を続けられなくても、その人が上達できないという意味ではありません。", "一つの習慣が途切れても、その人が継続的に進歩できるかどうかは決まりません。"),
    (70, 5): ("People can hand over a step to AI without handing over responsibility.", "When people hand over part of a task to AI, they still need to review consequential output.", "作業の一部をAIに任せても、責任まで任せることはできません。", "作業の一部をAIに任せても、重要な出力を確認する責任は残ります。"),
    (65, 8): ("We can feel proud of someone else's effort too.", "Shared effort and close observation can make another person's achievement a genuine source of pride.", "ほかの人の努力を誇りに思うこともできます。", "努力を共にしたり近くで見たりすると、ほかの人の達成も心から誇りに感じられます。"),
    (71, 7): ("Privacy matters when a career decision could affect security or identity.", "Career decisions may need confidentiality when disclosure could affect security, reputation, or identity.", "キャリアの決定が安全や自分の立場に影響する場合、プライバシーが大切です。", "キャリアの決定は、開示によって安全、評判、立場に影響が出る場合、秘密を守る必要があります。"),
}
for (_topic_no, _row_no), _row in ARTICLE_REVISIONS.items():
    TOPICS[_topic_no]["articles"][_row_no - 1] = _row


# Final semantic corrections found by reading the effective pool as a tutor.
TOPICS[68]["prompts"][6]["accessible_followups"] = (
    "Which value or risk creates that boundary?",
    "What safeguard would make the action less risky?",
)
TOPICS[73]["prompts"][2]["accessible"] = "How are people usually treated when they finish or leave before others?"
TOPICS[73]["prompts"][2]["accessible_ja"] = "ほかの人より先に仕事や勉強を終えて帰る人は、普通どのように受け止められますか？"
TOPICS[74]["prompts"][0]["full_followups"] = (
    "Which activity would have been visible to an observer?",
    "What made that period typical or unusual?",
)
TOPICS[74]["prompts"][4]["accessible_followups"] = (
    "Why is that work easy to miss?",
    "What problem does the hidden work prevent?",
)
TOPICS[75]["prompts"][0]["full"] = "Which change would most improve a place where people work or study?"
TOPICS[75]["prompts"][0]["full_ja"] = "人が働いたり学んだりする場所を最も改善する変更は何ですか？"

# Exact global uniqueness prevents a later pool from feeling copied from an
# earlier one. These variant-specific probes preserve intellectual parity while
# differentiating the language load.
TOPICS[65]["prompts"][2]["full_followups"] = (
    "Which response from other people most affected the person's view of the work?",
    "What confirmed its value to the person who completed it?",
)
TOPICS[68]["prompts"][0]["full_followups"] = (
    "Is that purpose regular or occasional?",
    "Which long-term option would carry the greatest value?",
)
TOPICS[68]["prompts"][4]["full_followups"] = (
    "Which part of that influence is useful?",
    "How has the resulting approach evolved?",
)
TOPICS[72]["prompts"][0]["full_followups"] = (
    "Which ability or understanding was the person trying to develop?",
    "What form did the guidance take?",
)
TOPICS[72]["prompts"][5]["accessible_followups"] = (
    "What can a response communicate?",
    "When might silence still be an honest response?",
)
TOPICS[72]["prompts"][5]["full_followups"] = (
    "What can a direct response communicate to the guide?",
    "When might no response still be ethically understandable?",
)
TOPICS[67]["prompts"][0]["accessible_followups"] = (
    "What part of the skill needs the most attention?",
    "What would improvement make possible?",
)
TOPICS[67]["prompts"][0]["full_followups"] = (
    "Which component of the skill needs focused work?",
    "What would meaningful improvement enable?",
)
TOPICS[67]["prompts"][1]["accessible_followups"] = (
    "How often should a beginner try that method?",
    "What would make it easy to repeat?",
)
TOPICS[67]["prompts"][1]["full_followups"] = (
    "How long should the method be tested before it is judged?",
    "Which condition would support consistent repetition?",
)
TOPICS[68]["prompts"][2]["accessible_followups"] = (
    "What can prompt the first step?",
    "What needs to be true before it feels realistic?",
)
TOPICS[68]["prompts"][2]["full_followups"] = (
    "Which event or need can prompt the first step?",
    "Which condition makes it sustainable rather than temporary?",
)
TOPICS[69]["prompts"][3]["accessible_followups"] = (
    "Would timing, access, money, or responsibility matter most?",
    "Could one part of the path be explored on a small scale?",
)
TOPICS[69]["prompts"][3]["full_followups"] = (
    "Would timing, access, resources, location, or responsibility matter most?",
    "Could one element of the path be tested without a complete transition?",
)
TOPICS[71]["prompts"][4]["accessible_followups"] = (
    "Which responsibility or uncertainty causes the delay?",
    "What new evidence could change the decision?",
)
TOPICS[71]["prompts"][4]["full_followups"] = (
    "Which evidence, responsibility, or constraint makes delay rational?",
    "What development could justify reconsidering the decision?",
)
TOPICS[71]["prompts"][6]["accessible_followups"] = (
    "What could that person help clarify?",
    "Which details would be inappropriate to share?",
)
TOPICS[71]["prompts"][6]["full_followups"] = (
    "Which uncertainty could that perspective reduce?",
    "Which information should remain confidential?",
)
TOPICS[73]["prompts"][4]["accessible_followups"] = (
    "What would you like to ask about my example?",
    "Which detail seems most different from your setting?",
)
TOPICS[73]["prompts"][4]["full_followups"] = (
    "Which part of my example would you like me to clarify?",
    "Which detail offers the strongest comparison with another setting?",
)
TOPICS[74]["prompts"][1]["accessible_followups"] = (
    "Which activity usually comes first?",
    "Which interruption is most common?",
)
TOPICS[74]["prompts"][1]["full_followups"] = (
    "Which activity normally determines the sequence?",
    "Which interruption most often changes the plan?",
)
TOPICS[74]["prompts"][4]["full_followups"] = (
    "Which feature keeps the work out of view?",
    "Which problem does that hidden work prevent?",
)
TOPICS[74]["prompts"][5]["accessible_followups"] = (
    "Which responsibility tends to change most?",
    "What usually stays stable?",
)
TOPICS[74]["prompts"][5]["full_followups"] = (
    "Which activity or responsibility tends to shift most?",
    "Which feature remains relatively stable?",
)
TOPICS[75]["prompts"][4]["accessible_followups"] = (
    "Which route offers the most privacy?",
    "When would a representative or formal route help?",
)
TOPICS[75]["prompts"][4]["full_followups"] = (
    "How do direct, confidential, representative, and formal routes differ?",
    "Which protection should exist before anyone speaks?",
)
TOPICS[75]["prompts"][5]["accessible_followups"] = (
    "How quickly should someone acknowledge the issue?",
    "What would a credible next step look like?",
)
TOPICS[75]["prompts"][5]["full_followups"] = (
    "Which first response would keep the process credible?",
    "How should responsibility and timing be made explicit?",
)


CLAIM_ORDER = {number: tuple(f"ft{number}-c{index:02d}" for index in range(1, 11)) for number in TOPIC_NUMBERS}

VOCABULARY = {
    64: {"new": (("first paycheck", "初めてもらった給料"),), "recycled": (), "assumed": (("earn", "稼ぐ"), ("spend", "使う")), "receptive": (("first earnings", "最初の収入"),)},
    65: {"new": (("feel proud of", "〜を誇りに思う"),), "recycled": (), "assumed": (("finish", "終える"), ("effort", "努力")), "receptive": (("recognition", "評価"),)},
    66: {"new": (("small success", "小さな成功"),), "recycled": (), "assumed": (("go well", "うまくいく"), ("notice", "気づく")), "receptive": (("threshold", "基準点"),)},
    67: {"new": (), "recycled": (), "assumed": (("improve", "上達する"), ("practice", "練習する")), "receptive": (("persistent", "続く"), ("stick with", "〜を続ける"))},
    68: {"new": (("set aside", "取っておく"),), "recycled": (), "assumed": (("save", "貯める"), ("debt", "借金")), "receptive": (("surplus", "余裕資金"),)},
    69: {"new": (("career path", "キャリアの進路"),), "recycled": (), "assumed": (("career", "キャリア"), ("choice", "選択")), "receptive": (("counterfactual", "事実と異なる仮定"),)},
    70: {"new": (("hand over", "〜に任せる"),), "recycled": (), "assumed": (("AI", "AI"), ("check", "確認する")), "receptive": (("accountability", "説明責任"),)},
    71: {"new": (("change careers", "キャリアを変える"),), "recycled": (), "assumed": (("risk", "リスク"), ("stay", "続ける")), "receptive": (("transition", "移行"),)},
    72: {"new": (), "recycled": (), "assumed": (("feedback", "フィードバック"), ("guide", "導く")), "receptive": (("formal authority", "正式な権限"), ("learn from", "〜から学ぶ"))},
    73: {"new": (("leave on time", "定時に帰る"),), "recycled": (), "assumed": (("finish", "終える"), ("official", "決まった")), "receptive": (("unpaid", "無給の"),)},
    74: {"new": (("behind the scenes", "表に見えないところで"),), "recycled": (), "assumed": (("prepare", "準備する"), ("check", "確認する")), "receptive": (("preventive", "予防の"),)},
    75: {"new": (("raise an issue", "問題を提起する"),), "recycled": (), "assumed": (("change", "変更"), ("proposal", "提案")), "receptive": (("unintended effect", "予期しない影響"),)},
}

GLOSSES = {
    64: {"accessible": {1: ("first paycheck", "first paycheck", "初めてもらった給料")}, "full": {3: ("The emotional significance of first earnings", "first earnings", "最初の収入")}},
    65: {"accessible": {8: ("feel proud of", "feel proud of", "〜を誇りに思う")}, "full": {5: ("External recognition", "recognition", "評価")}},
    66: {"accessible": {7: ("several small successes", "small success", "小さな成功")}, "full": {8: ("threshold", "threshold", "基準点")}},
    67: {"accessible": {4: ("stick with", "stick with", "〜を続ける")}, "full": {4: ("persistent", "persistent", "続く")}},
    68: {"accessible": {3: ("set aside", "set aside", "取っておく")}, "full": {2: ("surplus", "surplus", "余裕資金")}},
    69: {"accessible": {1: ("career path", "career path", "キャリアの進路")}, "full": {10: ("counterfactual", "counterfactual", "事実と異なる仮定")}},
    70: {"accessible": {5: ("hand over", "hand over", "〜に任せる")}, "full": {9: ("accountability", "accountability", "説明責任")}},
    71: {"accessible": {1: ("change careers", "change careers", "キャリアを変える")}, "full": {6: ("full transition", "transition", "移行")}},
    72: {"accessible": {1: ("learn from a manager", "learn from", "〜から学ぶ")}, "full": {1: ("formal authority", "formal authority", "正式な権限")}},
    73: {"accessible": {4: ("leave on time", "leave on time", "定時に帰る")}, "full": {8: ("unpaid", "unpaid", "無給の")}},
    74: {"accessible": {2: ("Behind the scenes", "behind the scenes", "表に見えないところで")}, "full": {4: ("Preventive", "preventive", "予防の")}},
    75: {"accessible": {3: ("raise an issue", "raise an issue", "問題を提起する")}, "full": {4: ("unintended effect", "unintended effect", "予期しない影響")}},
}


def _render_dependencies():
    """Import pilot-dependent renderer helpers only when rendering is requested."""
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415

    return base, new_lesson


def output_path(topic_number, variant):
    if topic_number not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_number, variant))
    _base, new_lesson = _render_dependencies()
    course = f"{COURSE}-{variant}"
    return new_lesson.ENGLISH / "tracks/3-freetalking/courses" / course / "lessons" / f"{topic_number:02d}-{TOPICS[topic_number]['slug']}" / "lesson.html"


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


def _vocabulary_meta(rows: tuple[tuple[str, str], ...]) -> str:
    return "; ".join(f"{english}|{japanese}" for english, japanese in rows)


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
    lis = "".join(
        f"<li>{base.esc(value)}</li>" for value in item[f"{variant}_followups"]
    )
    japanese = item[f"{variant}_ja"]
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


def build(topic_no: int, variant: str) -> str:
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
            head,
            f"podo:vocabulary:{category}",
            _vocabulary_meta(VOCABULARY[topic_no][category]),
        )
    goal_en, goal_ja = data["goal"]
    pages = [
        base.ft_contract.goal_page(
            title=data["title"],
            title_ja=data["ja"],
            topic_en=goal_en,
            topic_ja=goal_ja,
            data_act="Work and money",
            kicker="WORK AND MONEY",
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
