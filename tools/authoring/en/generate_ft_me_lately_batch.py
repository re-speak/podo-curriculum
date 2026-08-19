#!/usr/bin/env python3
"""Generate the explicit FT 10-20 talk-me-lately accessible/full pairs.

This is a deliberately narrow course-batch generator. Topic language is authored
as paired content data: every accessible/full article row makes the same claim in
the same order, while the full wording may carry greater lexical or clause load.
Existing decks are never overwritten unless --refresh is supplied.
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/3-freetalking"
COURSE = "talk-me-lately"
CANONICAL = {
    variant: TRACK / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html"
    for variant in ("accessible", "full")
}


def prompt(title, title_ja, accessible, japanese, followups, full=None, full_followups=None):
    return {
        "title": title,
        "title_ja": title_ja,
        "accessible": accessible,
        "full": full or accessible,
        "ja": japanese,
        "accessible_followups": followups,
        "full_followups": full_followups or followups,
    }


TOPICS = {
    10: {
        "slug": "something-youve-recently-got-into",
        "title": "Something you've recently got into",
        "ko": "최근 새로 빠진 것",
        "ja": "最近夢中になっていること",
        "goal": ("Let's talk about a new interest and where it might lead.", "新しく興味を持ったことと、これからについて話しましょう。"),
        "outcomes": (("Describe the new interest", "新しい興味を説明する"), ("Explain how it began", "始めたきっかけを話す"), ("Choose a next step", "次の一歩を決める")),
        "article_title": ("How a new interest grows", "新しい興味が育つまで"),
        "articles": [
            ("A new interest often begins with one small moment of curiosity.", "A new interest often begins with a brief moment of curiosity rather than a serious plan.", "新しい興味は、ちょっとした好奇心から始まることがよくあります。"),
            ("A video, a friend, or a surprising result can make us try it once.", "A video, a friend's enthusiasm, or an unexpected result can be enough to make us try it once.", "動画や友人、意外な結果がきっかけで、一度試してみることがあります。"),
            ("The first stage feels exciting because small improvements are easy to notice.", "The early stage feels exciting because even small discoveries create visible progress.", "最初は、小さな上達に気づきやすいので、わくわくします。"),
            ("The interest becomes a habit when we make regular time for it.", "The interest starts becoming a habit only when we protect regular time for it.", "定期的に時間を作ると、その興味は習慣になっていきます。"),
            ("Other people can deepen the interest by sharing advice, tools, or encouragement.", "A community can deepen the interest by sharing advice, tools, and encouragement.", "ほかの人から助言や道具、励ましをもらうと、興味が深まります。"),
            ("Some people keep a new hobby private until they feel good at it.", "Some people keep a new hobby private until they feel competent enough to explain it.", "ある程度上手になるまで、新しい趣味を人に話さない人もいます。"),
            ("Every new activity also takes time away from something else.", "Every new activity has an opportunity cost because that time has to come from somewhere else.", "新しい活動に使う時間は、別の何かに使えない時間でもあります。"),
            ("Small signs of progress help us decide how much room the interest deserves in our lives.", "Small, concrete signs of progress help us decide how much room the interest deserves in our lives.", "小さな進歩が見えると、その興味に生活の中でどのくらい時間を使うか決めやすくなります。"),
            ("Stopping is not always failure; sometimes the experiment has done its job.", "Letting an interest go is not necessarily failure; sometimes the experiment has already done its job.", "やめることは必ずしも失敗ではなく、試したこと自体に意味がある場合もあります。"),
            ("If it lasts, the interest may become part of how we see ourselves.", "If it lasts, the interest may eventually become part of our identity rather than simply a pastime.", "長く続けば、その興味は自分らしさの一部になるかもしれません。"),
        ],
        "prompts": [
            prompt("A new interest", "新しい興味", "Have you got into anything new recently?", "最近、新しく夢中になったものはありますか？", ["If yes, what do you enjoy most about it?", "If not, what has caught your interest lately?"]),
            prompt("Your free time", "自由時間", "What has been taking most of your free time lately?", "最近、自由時間の多くを何に使っていますか？", ["Did you choose to spend that time on it?", "What would you like more time for?"]),
            prompt("How it began", "始めたきっかけ", "How did you first get interested in it?", "最初に興味を持ったきっかけは何でしたか？", ["What made you try it?", "Did you expect to enjoy it this much?"]),
            prompt("Time for it", "使っている時間", "How often do you do it now?", "今はどのくらいの頻度でしていますか？", ["When do you usually make time for it?", "What sometimes gets in the way?"]),
            prompt("Who knows", "知っている人", "Have you told anyone about this interest?", "この興味について誰かに話しましたか？", ["If yes, how did they react?", "If not, who would understand it best?"]),
            prompt("Sharing or private", "話す？秘密にする？", "Do you prefer sharing new interests or keeping them private?", "新しい興味は人に話すほうですか、それとも自分だけにしておくほうですか？", ["What makes you mention an interest?", "How much do other people's reactions matter?"]),
            prompt("What it replaces", "代わりに減ったこと", "Has this new interest reduced time for anything else?", "この新しい興味で、ほかのことに使う時間が減りましたか？", ["If so, was that change worth it?", "What would you not give up for it?"], full_followups=["If so, is that a good trade-off?", "What would you not give up for it?"]),
            prompt("Where it goes", "これから", "What would you like to do with this interest next?", "この興味をこれからどうしていきたいですか？", ["What would be a good result in three months?", "What is one small next step?"], full="Where do you hope this interest goes from here?", full_followups=["What would progress look like in three months?", "What is the next small step?"]),
        ],
    },
    11: {
        "slug": "a-show-you-cant-stop-watching",
        "title": "A show you can't stop watching",
        "ko": "계속 보게 되는 프로그램",
        "ja": "見るのをやめられない作品",
        "goal": ("Let's talk about what keeps you watching a show.", "つい見続けてしまう作品について話しましょう。"),
        "outcomes": (("Describe what you're watching", "今見ている作品を説明する"), ("Explain what keeps you watching", "見続ける理由を話す"), ("Choose what comes next", "次に見るものを考える")),
        "article_title": ("Why we keep watching", "見続けたくなる理由"),
        "articles": [
            ("Streaming gives us more shows than we could ever finish.", "Streaming services give us far more shows than we could realistically finish.", "配信サービスには、見終えられないほど多くの作品があります。"),
            ("Choosing what to start can be harder than choosing what to continue.", "With so much choice, deciding what to start can be harder than deciding what to continue.", "何を見るか決めるほうが、続きを見るか決めるより難しいことがあります。"),
            ("A strong first episode gives us a question that needs an answer.", "A strong opening episode creates an unanswered question that pulls us into the next one.", "よい第1話は、答えを知りたくなる疑問を残します。"),
            ("Characters can keep us watching even when the story moves slowly.", "Compelling characters can sustain our interest even when the plot develops slowly.", "物語の進みが遅くても、登場人物の魅力で見続けることがあります。"),
            ("Recommendations also help because they come with someone else's excitement.", "A personal recommendation also carries someone else's enthusiasm and gives us a reason to keep watching.", "人からのおすすめには、その人の熱意も含まれていて、見続ける理由になります。"),
            ("Binge-watching several episodes can be fun, but it can also steal sleep.", "Binge-watching can feel satisfying in the moment while quietly taking time from sleep and other plans.", "何話も一気見するのは楽しい一方、睡眠やほかの予定の時間を奪うこともあります。"),
            ("Dropping a show halfway is reasonable when it no longer feels rewarding.", "Abandoning a show halfway is reasonable when continuing feels more like an obligation than entertainment.", "楽しめなくなった作品を途中でやめるのは、悪いことではありません。"),
            ("The right show often depends on our mood and available attention.", "The right show often depends on our mood and how much attention we can give it that day.", "その日に合う作品は、気分や集中できる度合いによって変わります。"),
            ("A satisfying ending can change how we remember the whole series.", "A satisfying—or disappointing—ending can reshape how we remember the entire series.", "結末に満足できるかどうかで、作品全体の記憶が変わることがあります。"),
            ("Finishing one show usually sends us looking for the next feeling, not the same story.", "After a series ends, we often search for the same emotional experience rather than an identical story.", "一つ見終えると、同じ物語より、同じ気持ちを味わえる次の作品を探すことが多いです。"),
        ],
        "prompts": [
            prompt("Watching now", "今見ているもの", "Are you watching any shows at the moment?", "今、何か作品を見ていますか？", ["If yes, what kind of show is it?", "If not, do you usually watch shows at all?"]),
            prompt("Your last episode", "直近のエピソード", "When was the last time you watched an episode of a show?", "最後に作品の一話を見たのはいつですか？", ["If it was recent, what do you remember?", "If it was a long time ago, what do you watch instead?"]),
            prompt("How far in", "どこまで見る？", "How far do you usually get before you decide to continue a show?", "作品を見続けるか決めるまで、普段どのくらい見ますか？", ["What helps you decide?", "Have you ever decided after one episode?"]),
            prompt("The pull", "見続ける理由", "What usually makes you keep watching a show?", "普段、どんなことがあると作品を見続けますか？", ["Is the story or a character more important?", "At what point do you get interested?"]),
            prompt("Finding a show", "作品の見つけ方", "How do you usually find a new show?", "普段、新しい作品をどうやって見つけますか？", ["Do you trust friends or an app more?", "What makes a show look interesting?"], full="How do you usually discover a new show?", full_followups=["Do you trust personal recommendations or an app more?", "What first makes a show look interesting?"]),
            prompt("A show you dropped", "途中でやめた作品", "Have you stopped watching any show halfway?", "途中で見るのをやめた作品はありますか？", ["What usually makes you lose interest?", "What might make you try it again?"], full_followups=["What usually makes you lose interest?", "What could persuade you to return to a show?"]),
            prompt("Enough is enough", "見すぎの境目", "When does watching another episode become a bad idea?", "もう1話見るのがよくない判断になるのは、どんなときですか？", ["What would you need to do the next day?", "How late is too late for you?"], full_followups=["Which commitment would make you stop?", "What tends to happen when you ignore that limit?"]),
            prompt("What's next", "次に見るもの", "What kind of show would you like to watch next?", "次はどんな作品を見たいですか？", ["Do you want a similar feeling or something different?", "Where would you look for ideas?"], full_followups=["Do you want a familiar feeling or something different?", "Where would you look for a recommendation?"]),
        ],
    },
    12: {
        "slug": "a-compliment-you-still-remember",
        "title": "A compliment you still remember",
        "ko": "아직 기억나는 칭찬",
        "ja": "今も覚えている褒め言葉",
        "goal": ("Let's talk about a compliment that stayed with you.", "心に残っている褒め言葉について話しましょう。"),
        "outcomes": (("Recall the exact compliment", "実際の褒め言葉を思い出す"), ("Explain your response", "自分の反応を説明する"), ("Choose praise to pass on", "誰かに伝える褒め言葉を考える")),
        "article_title": ("Why some praise stays with us", "心に残る褒め言葉"),
        "articles": [
            ("A compliment can be only a few words and still stay with us for years.", "A compliment can last only a few seconds yet remain in our memory for years.", "褒め言葉は短くても、何年も心に残ることがあります。"),
            ("Specific praise often feels more believable than a general compliment.", "Specific praise often feels more credible than a broad statement that could apply to anyone.", "具体的な褒め言葉は、誰にでも当てはまる一般的な褒め言葉より信じやすく感じます。"),
            ("It matters when the speaker noticed effort that other people missed.", "It can matter especially when the speaker recognizes effort that everyone else overlooked.", "ほかの人が気づかなかった努力を見てくれたとき、その言葉は特に大切になります。"),
            ("Many people feel awkward and quickly reject praise.", "Many people feel awkward receiving praise and immediately minimize what they did.", "褒められると気まずく感じ、すぐ否定してしまう人も多いです。"),
            ("A simple thank-you accepts the kindness without claiming too much.", "A simple thank-you can accept the kindness without turning the moment into self-promotion.", "簡単にお礼を言えば、自慢せずに相手の好意を受け取れます。"),
            ("Criticism can be easier to remember because our minds watch for danger.", "Criticism may dominate our memory because the mind naturally pays closer attention to possible threats.", "人は危険に注意しやすいため、批判のほうを覚えやすいことがあります。"),
            ("Saving a meaningful compliment can balance that negative habit.", "Deliberately remembering meaningful praise can help balance that negative bias.", "意味のある褒め言葉を覚えておくと、その悪い傾向とのバランスを取れます。"),
            ("Giving good praise also requires attention to another person's real work.", "Offering sincere praise requires us to pay close attention to another person's actual effort.", "よい褒め言葉を伝えるには、相手の本当の努力を見る必要があります。"),
            ("The best time is often soon after the action, while the detail is clear.", "Praise is often most effective soon after the action, while the specific detail is still clear.", "具体的なことを覚えているうちに伝えると、褒め言葉はより効果的です。"),
            ("One honest sentence can change how someone sees their own ability.", "One honest, well-timed sentence can reshape how someone understands their own ability.", "たった一つの正直な言葉で、自分の能力についての見方が変わることがあります。"),
        ],
        "prompts": [
            prompt("A remembered compliment", "覚えている褒め言葉", "Is there a compliment you still remember?", "今も覚えている褒め言葉はありますか？", ["If yes, when did you hear it?", "If not, what kind of praise feels meaningful to you?"]),
            prompt("Praise you like", "うれしい褒め言葉", "What kind of praise do you most like hearing?", "どんな褒め言葉を言われると、いちばんうれしいですか？", ["Do you prefer praise about effort or results?", "Do you like short or detailed comments?"], full="What kind of praise do you most appreciate hearing?", full_followups=["Do you prefer praise about effort or results?", "Do specific details matter?"]),
            prompt("Whose praise matters", "心に残る相手", "Whose praise would stay with you most?", "誰から褒められると、一番心に残りますか？", ["Have they ever praised you?", "Why does that person's view matter?"]),
            prompt("Did you believe it?", "信じられた？", "Would you believe that kind of compliment?", "そのような褒め言葉を信じられると思いますか？", ["What would make it believable?", "What might make it hard to accept?"]),
            prompt("Your response", "そのときの返事", "How do you usually respond to praise?", "褒められたとき、普段どう返事をしますか？", ["What do you feel but not say?", "Does your answer change with the person?"]),
            prompt("What stays longer", "長く残るもの", "Do you remember praise or negative comments better?", "褒め言葉と批判では、どちらをよく覚えていますか？", ["Why do those words stay with you?", "Do they affect what you do next?"], full="Do you remember compliments or criticism better?", full_followups=["Why does that type stay with you?", "How does it affect your next decision?"]),
            prompt("Praise you gave", "自分が伝えた言葉", "Have you given someone a real compliment recently?", "最近、誰かを心から褒めましたか？", ["If yes, what had the person done?", "If not, what sometimes stops you?"]),
            prompt("Someone who deserves it", "褒めたい人", "Is there someone you would like to compliment now?", "今、褒めたい人はいますか？", ["If yes, what exactly would you praise?", "If not, what kind of effort deserves more praise?"], full_followups=["If yes, what exactly would you praise?", "If not, what kind of effort deserves more recognition?"]),
        ],
    },
    13: {
        "slug": "your-plans-for-this-weekend",
        "title": "Your plans for this weekend",
        "ko": "이번 주말 계획",
        "ja": "今週末の予定",
        "goal": ("Let's talk through your weekend plan and what could change it.", "週末の予定と、それが変わる可能性について話しましょう。"),
        "outcomes": (("Describe the weekend plan", "週末の予定を説明する"), ("Say what matters most", "いちばん大切なことを話す"), ("Adapt if it changes", "変更に合わせて考える")),
        "article_title": ("What a weekend plan does", "週末の予定がしてくれること"),
        "articles": [
            ("Weekend plans give us something to look forward to during the week.", "Weekend plans can give shape to the week by creating something concrete to anticipate.", "週末の予定があると、平日に楽しみにできるものが生まれます。"),
            ("Some people recover through quiet time, while others need people and activity.", "Some people recover through solitude, while others regain energy through company and activity.", "静かな時間で回復する人もいれば、人と過ごすことで元気になる人もいます。"),
            ("A good plan can include both rest and one meaningful activity.", "A satisfying plan often balances genuine rest with one activity that feels meaningful.", "よい予定には、休息と意味のある活動の両方を入れられます。"),
            ("Plans with other people require decisions about time, place, and cost.", "Shared plans require coordination around time, place, cost, and different expectations.", "人と一緒の予定では、時間、場所、費用を決める必要があります。"),
            ("Weather and health can change even a carefully arranged day.", "Weather, health, and unexpected responsibilities can disrupt even a carefully arranged day.", "天気や体調によって、よく考えた予定も変わることがあります。"),
            ("A backup plan makes change less disappointing.", "A realistic backup plan can make an unexpected change feel less disappointing.", "予備の案があると、変更があってもがっかりしにくくなります。"),
            ("Leaving every hour full can make the weekend feel like more work.", "Filling every hour can turn leisure into another schedule that has to be managed.", "すべての時間を埋めると、週末も仕事のように感じることがあります。"),
            ("Leaving some time open gives us room to rest or do something unplanned.", "Leaving some time uncommitted creates room for rest or an unplanned opportunity.", "少し時間を空けておくと、休んだり予定外のことをしたりできます。"),
            ("When a plan fails, the replacement can sometimes become the best part.", "When an original plan falls through, the improvised alternative can unexpectedly become the best part.", "予定がだめになったとき、代わりにしたことが一番よい思い出になることもあります。"),
            ("Our ideal weekend often shows what we need most right now.", "The weekend we want often reveals what is missing from the rest of our life at that moment.", "理想の週末には、今の自分に一番必要なものが表れることがあります。"),
        ],
        "prompts": [
            prompt("This weekend", "今週末", "How are you feeling about this weekend?", "今週末について、今どんな気持ちですか？", ["Are you hoping to rest or do something?", "What would make it feel different from a weekday?"]),
            prompt("A good weekend", "よい週末", "What would make this weekend feel well spent?", "何ができたら、よい週末だったと思えますか？", ["Do you need rest, activity, or both?", "What do you want to avoid?"]),
            prompt("The full plan", "全体の予定", "How much of the weekend is planned already?", "週末のどのくらいが、すでに決まっていますか？", ["What would you add if nothing is fixed?", "How much time do you want to leave open?"]),
            prompt("Who with", "誰と", "Who will you spend time with, if anyone?", "一緒に過ごす人がいるなら、誰ですか？", ["What do you enjoy about that choice?", "Would you prefer more time alone or with others?"]),
            prompt("Looking forward", "楽しみなこと", "What are you most looking forward to, even if you have no fixed plan?", "予定が決まっていなくても、何をいちばん楽しみにしていますか？", ["Why does that part matter now?", "What would make it even better?"]),
            prompt("What could change", "変わる可能性", "What could change how you spend the weekend?", "何が週末の過ごし方を変える可能性がありますか？", ["What would be easiest to change?", "When would you make a new decision?"], full_followups=["What would be easiest to adapt?", "When would you make a new decision?"]),
            prompt("Still undecided", "まだ決めていないこと", "Is there anything you still need to decide?", "まだ決める必要があることはありますか？", ["If yes, what information would help?", "If not, which decision feels best now?"]),
            prompt("If it falls through", "予定がなくなったら", "If a plan fell through this weekend, how would you use the time instead?", "もし週末の予定がなくなったら、その時間をどう使いますか？", ["Would you prefer the backup in any way?", "Who would you need to tell, if anyone?"]),
        ],
    },
    14: {
        "slug": "one-thing-you-still-want-to-do-this-year",
        "title": "One thing you still want to do this year",
        "ko": "올해 안에 하고 싶은 한 가지",
        "ja": "今年中にまだやりたいこと",
        "goal": ("Let's choose one goal and find a realistic first step.", "目標を一つ選び、現実的な最初の一歩を考えましょう。"),
        "outcomes": (("Choose one meaningful goal", "大切な目標を一つ選ぶ"), ("Name the real barrier", "本当の障害を説明する"), ("Plan this week's step", "今週の一歩を決める")),
        "article_title": ("Turning a wish into a plan", "願いを計画に変える"),
        "articles": [
            ("A deadline can help a vague wish become a real decision.", "A deadline can turn a vague wish into a decision that competes for real time.", "期限があると、ぼんやりした願いが本当の決断になります。"),
            ("Choosing one goal means accepting that other goals may wait.", "Choosing one priority also means accepting that several worthwhile goals may have to wait.", "目標を一つ選ぶことは、ほかの目標を待たせることでもあります。"),
            ("We often delay a goal when the first step is unclear or too large.", "We often postpone a goal because the first action is ambiguous, uncomfortable, or too large.", "最初の一歩が分かりにくかったり大きすぎたりすると、目標を先延ばしにしがちです。"),
            ("Breaking it into a small action makes progress easier to begin.", "Breaking the goal into a small, observable action reduces the effort needed to begin.", "小さな行動に分けると、始めやすくなります。"),
            ("Time is not the only barrier; fear and uncertainty can also stop us.", "A lack of time is not always the real barrier; fear, uncertainty, and possible judgment also matter.", "時間だけでなく、不安や自信のなさも行動を止めることがあります。"),
            ("Giving up one old goal can create space for a more important one.", "Consciously releasing an outdated goal can create room for a priority that still fits our identity.", "古い目標を一つ手放すと、もっと大切な目標のための余裕ができます。"),
            ("Telling someone can add support, but it can also add pressure.", "Sharing a goal can create useful accountability, although it may also create unwanted pressure.", "誰かに話すと支えになる一方、プレッシャーになることもあります。"),
            ("The result may matter less than learning to take the next step consistently.", "The final result may matter less than learning to take the next step consistently.", "結果よりも、次の一歩を続けて踏み出せるようになることが大切な場合もあります。"),
            ("One action this week is more useful than a perfect plan for next month.", "One concrete action this week is usually more valuable than a perfect plan that begins next month.", "来月からの完璧な計画より、今週の具体的な一歩のほうが役立ちます。"),
            ("A good goal can change as we learn what is actually possible.", "A serious goal can still be revised as new information changes what is possible or worthwhile.", "本気の目標でも、可能なことが分かるにつれて変えてかまいません。"),
        ],
        "prompts": [
            prompt("One goal", "一つの目標", "If you could only finish one thing before December, what would it be?", "12月までに一つだけ終えられるなら、何にしますか？", ["If something comes to mind, why that one?", "If nothing does, what matters more right now?"]),
            prompt("After it's finished", "終えたあと", "If you chose a goal, what might be different after you finished it?", "目標を選ぶなら、終えたあとに何が変わると思いますか？", ["Which change would matter most?", "Who else might notice it?"]),
            prompt("Why a goal matters", "目標が大切な理由", "What can make one goal feel important?", "一つの目標が大切に感じられるのは、どんなときですか？", ["What kind of change can a goal bring?", "What might you leave until later?"], full="What makes a goal feel important to you?", full_followups=["What kind of change can a goal create?", "What might you be willing to postpone?"]),
            prompt("What gets in the way", "進めない理由", "What usually stops a goal from moving forward?", "目標が進まないとき、普段何が原因になりますか？", ["Is it often time, money, or doubt?", "Which part can a person control?"], full_followups=["Is the main barrier time, money, or uncertainty?", "Which part can a person control?"]),
            prompt("What you dropped", "あきらめたこと", "Have you given up on any goal this year?", "今年、あきらめた目標はありますか？", ["If yes, what was the goal?", "If not, is there one goal you're still working on?"]),
            prompt("Who would notice", "気づく人", "If you completed a personal goal, who might notice?", "自分の目標を達成したら、誰が気づきそうですか？", ["Would anyone else's daily life change?", "Who would you want to tell, if anyone?"]),
            prompt("A realistic limit", "現実的な限界", "What can make it right to change or drop a goal?", "目標を変えたりやめたりしてよいのは、どんなときですか？", ["What would you refuse to change?", "When would changing the goal be a good idea?"], full="What can make it reasonable to change or drop a goal?", full_followups=["What should stay non-negotiable?", "When would changing the goal be sensible?"]),
            prompt("This week's step", "今週の一歩", "If you chose a goal, what small step could you take this week?", "目標を選ぶなら、今週どんな小さな一歩を踏み出せますか？", ["When could you do it?", "What could make it easier?"]),
        ],
    },
    15: {
        "slug": "what-you-spend-the-most-money-on",
        "title": "What you spend the most money on",
        "ko": "돈을 가장 많이 쓰는 것",
        "ja": "いちばんお金を使っているもの",
        "goal": ("Let's talk about what your spending says about your priorities.", "お金の使い方に表れる優先順位について話しましょう。"),
        "outcomes": (("Describe one real expense", "実際の支出を説明する"), ("Compare views of value", "価値への見方を比べる"), ("Name your real priority", "本当の優先順位を話す")),
        "article_title": ("What spending reveals", "支出から見えること"),
        "articles": [
            ("After rent and other basic costs, our spending often shows what we value most.", "Once rent and other basic costs are covered, discretionary spending often reveals what we genuinely value.", "家賃などの基本的な費用のあとに使うお金には、自分が大切にするものが表れます。"),
            ("Small monthly payments can become a large amount without feeling expensive.", "Small recurring payments can accumulate into a significant amount without ever feeling expensive individually.", "小さな月々の支払いも、一つずつは高く感じなくても大きな額になります。"),
            ("A hobby may look wasteful to someone who does not share it.", "Spending on a hobby may look irrational to someone who does not understand the value it provides.", "同じ趣味を持たない人には、その支出が無駄に見えることがあります。"),
            ("Price alone cannot show whether something was useful or meaningful.", "Price alone cannot measure usefulness, time saved, enjoyment, or emotional significance.", "値段だけでは、役立ち方や楽しさ、意味までは分かりません。"),
            ("Cost per use can be a better measure for things we use often.", "For frequently used items, cost per use can be a more informative measure than the original price.", "よく使う物は、一回あたりの費用で考えるほうが分かりやすい場合があります。"),
            ("Paying more for quality can save money if the item lasts longer.", "Paying more for quality can be economical when durability prevents repeated replacement.", "質のよい物に多く払うことは、長持ちすれば節約になる場合があります。"),
            ("However, a high price can also become an excuse to keep something unused.", "However, a high purchase price can create pressure to keep an item that no longer serves us.", "高く買ったことが、使わない物を手放せない理由になることもあります。"),
            ("Our idea of waste can change after our life or income changes.", "Our judgment of waste can shift when our income, responsibilities, or daily routine changes.", "収入や生活が変わると、無駄だと思うものも変わります。"),
            ("A realistic budget makes room for joy instead of treating it as a mistake.", "A sustainable budget can deliberately make room for pleasure rather than treating every enjoyable expense as a failure.", "現実的な予算なら、楽しみに使うお金も失敗ではなく計画に入れられます。"),
            ("The useful question is whether the spending still matches the life we want.", "The useful question is not whether others approve, but whether the spending still supports the life we want.", "大切なのは、他人の評価ではなく、その支出が望む生活に合っているかです。"),
        ],
        "prompts": [
            prompt("Extra spending", "楽しみのためのお金", "Do you ever spend money just for fun?", "楽しみのためだけにお金を使うことはありますか？", ["If yes, what kind of thing do you buy?", "If not, what do you prefer to save for?"], full="Do you ever spend money mainly for enjoyment?", full_followups=["If yes, what kind of expense is it?", "If not, what do you prefer to save for?"]),
            prompt("A recent expense", "最近考えた支出", "Have you thought about buying something extra recently?", "最近、必要ではない物を買おうか考えましたか？", ["If yes, what was it?", "If not, what is easy for you to skip?"], full="Have you considered any non-essential purchase recently?", full_followups=["If yes, what caught your attention?", "If not, what is easy for you to pass up?"]),
            prompt("A comfortable range", "答えられる範囲", "If you want to share, about how much can you spend on extras each month?", "答えられる範囲で、毎月、自由に使うお金をどのくらいにしていますか？", ["Has the amount changed recently?", "What makes it go up or down?"], full="If you're comfortable sharing, what range do you allow for extra spending each month?", full_followups=["Has that range changed recently?", "What usually makes it rise or fall?"]),
            prompt("When it feels worth it", "価値を感じるとき", "When does extra spending feel worth it to you?", "どんなとき、自由に使ったお金に価値があったと感じますか？", ["Which benefit from that spending lasts the longest?", "When would it feel like too much?"], full="When does discretionary spending feel worthwhile to you?", full_followups=["Which benefit lasts the longest?", "When would it stop feeling worthwhile?"]),
            prompt("A reason not to buy", "買わない理由", "What is one good reason not to buy something extra?", "必要ではない物を買わない理由を一つ挙げるなら、何ですか？", ["Which reason matters most to you?", "When might buying it still be okay?"], full="What is one good reason not to make a non-essential purchase?", full_followups=["How much does that reason matter to you?", "When might it not apply?"]),
            prompt("Your idea of waste", "自分が思う無駄", "What kind of spending do you think is a waste?", "あなたはどんな支出を無駄だと思いますか？", ["Why does it feel unnecessary?", "Could it be important to someone else?"], full_followups=["Why does it feel unnecessary?", "Could it be valuable to someone else?"]),
            prompt("A changed mind", "変わった考え", "Has your view of any kind of spending changed?", "ある支出について見方が変わったことはありますか？", ["If yes, what caused the change?", "If not, why has your view stayed the same?"], full="Has your view of any spending category changed?", full_followups=["If yes, what caused the change?", "If not, what keeps your view stable?"]),
            prompt("Your real priority", "本当の優先順位", "If your budget became tighter, is there any extra expense you would keep?", "予算が厳しくなったら、それでも残したい支出はありますか？", ["If yes, why that one?", "If not, what would you cut first?"], full="If your budget became tighter, is there any discretionary expense you would protect?", full_followups=["If yes, what makes it a priority?", "If not, what would you cut first?"]),
        ],
    },
    16: {
        "slug": "something-you-tried-for-the-first-time",
        "title": "Something you tried for the first time",
        "ko": "처음 해 본 것",
        "ja": "初めてやってみたこと",
        "goal": ("Let's tell the story of a recent first experience.", "最近の初めての体験について話しましょう。"),
        "outcomes": (("Retell a recent first", "最近の初めてを話す"), ("Compare expectation and reality", "予想と実際を比べる"), ("Choose the next first", "次の挑戦を考える")),
        "article_title": ("What first times teach us", "初めての体験が教えること"),
        "articles": [
            ("Daily routines become easier, but they can make our world feel smaller.", "Daily routines create useful stability, but they can gradually narrow the range of experiences we consider.", "日課は生活を楽にしますが、自分の世界を小さくすることもあります。"),
            ("Trying something new makes us pay attention again.", "A first attempt forces us to pay attention because familiar shortcuts no longer work.", "初めてのことをすると、もう一度よく注意するようになります。"),
            ("We usually imagine the experience before we actually have it.", "Before a new experience, we build expectations from other people's stories and incomplete information.", "新しい体験の前には、実際にするより先に頭の中で想像します。"),
            ("Nervousness can mean that the result matters to us.", "Nervousness does not always signal danger; it can show that the outcome matters to us.", "緊張は、その結果を大切に思っているしるしかもしれません。"),
            ("Clear instructions or a supportive person can make the first step easier.", "Clear guidance or a supportive companion can reduce the uncertainty of a first attempt.", "分かりやすい説明や支えてくれる人がいると、最初の一歩が楽になります。"),
            ("The real experience is often different from the version in our head.", "The actual experience often differs from our imagined version in both easier and harder ways.", "実際の体験は、頭の中で考えていたものと違うことがよくあります。"),
            ("Being bad at first can feel uncomfortable when we are used to being capable.", "Feeling like a beginner can be uncomfortable when we are used to being capable in daily life.", "普段はできることが多い人にとって、初心者の感覚は居心地が悪いことがあります。"),
            ("Trying it again shows whether the experience was only exciting because it was new.", "A second attempt reveals whether the activity has lasting value or was exciting only because it was novel.", "もう一度すると、新しいから楽しかっただけかどうかが分かります。"),
            ("Remembering first times helps us notice that we are still changing.", "Remembering recent firsts reminds us that personal growth does not end at a particular age.", "最近の初めてを覚えておくと、自分がまだ変わっていると気づけます。"),
            ("One new experience often points toward the next thing we want to try.", "One successful first experience often expands the range of things we are willing to try next.", "一つの新しい体験が、次に挑戦したいことにつながることがあります。"),
        ],
        "prompts": [
            prompt("A recent first", "最近の初めて", "Have you tried anything for the first time recently?", "最近、初めて試したことはありますか？", ["If yes, when did you do it?", "If not, what counts as a recent first for you?"]),
            prompt("Feeling new", "初めての感覚", "When did you last feel like a beginner?", "最後に初心者のように感じたのはいつですか？", ["What made it feel new?", "How did you respond to that feeling?"], full_followups=["What made the situation unfamiliar?", "How did you respond to that feeling?"]),
            prompt("Why people try", "試す理由", "What can finally make someone try something new?", "人がついに新しいことを試すきっかけは何だと思いますか？", ["Does another person's help matter?", "Can waiting make the first step harder?"], full="What can finally persuade someone to try something new?", full_followups=["How much does encouragement matter?", "Can a long delay make the first step harder?"]),
            prompt("Expectation and reality", "予想と実際", "Are new experiences usually what you expect?", "新しい体験は、普段、予想どおりですか？", ["What is often easier?", "What is often harder?"], full="How closely do new experiences usually match your expectations?", full_followups=["What tends to be easier than expected?", "What tends to be more difficult?"]),
            prompt("Trying again", "もう一度", "What makes you want to try something again?", "もう一度やってみたいと思うのは、どんなときですか？", ["What would you change the second time?", "Does doing it with someone help?"], full="What makes a first experience worth repeating?", full_followups=["What would you change the second time?", "How might a companion change it?"]),
            prompt("The first before that", "その前の初めて", "Can you remember another first-time experience?", "ほかの初めての体験を思い出せますか？", ["If yes, how was it different?", "If not, why are first times hard to remember?"]),
            prompt("Staying a beginner", "初心者でいること", "How do you feel when you're not good at something yet?", "まだ上手にできないとき、どんな気持ちになりますか？", ["What helps you continue?", "When do you decide to stop?"]),
            prompt("The next first", "次の初めて", "Is there anything you'd like to try next?", "次にやってみたいことはありますか？", ["If yes, what is stopping you now?", "If not, what makes your current routine work well?"]),
        ],
    },
    17: {
        "slug": "a-small-win-nobody-noticed",
        "title": "A small win nobody noticed",
        "ko": "아무도 알아주지 않은 작은 성과",
        "ja": "誰にも気づかれなかった小さな成功",
        "goal": ("Let's notice a small success and explain why it mattered.", "小さな成功に目を向け、なぜ大切だったか話しましょう。"),
        "outcomes": (("Name a quiet success", "静かな成功を話す"), ("Explain why it mattered", "大切だった理由を説明する"), ("Define a good month", "よい一か月を考える")),
        "article_title": ("Progress without applause", "褒められなくても進んでいること"),
        "articles": [
            ("Not all progress produces a result that other people can see.", "A great deal of meaningful progress produces no visible result for other people to recognize.", "大切な進歩のすべてが、他人に見える結果になるわけではありません。"),
            ("Finishing a delayed task or handling a hard day better can be a real win.", "Completing a delayed task or responding more calmly to a difficult day can represent genuine progress.", "先延ばしにしたことを終えたり、難しい一日にうまく対応したりするのも本当の成功です。"),
            ("These wins often look ordinary from the outside.", "Such wins often look completely ordinary to anyone who cannot see the effort behind them.", "こうした成功は、外から見ると普通のことに見えがちです。"),
            ("Praise feels good, but it is not the only proof that something mattered.", "External praise feels good, but it is an unreliable measure of whether an achievement mattered.", "褒められるのはうれしいですが、それだけが価値の証明ではありません。"),
            ("Comparing ourselves with other people can hide our own progress.", "Constant comparison can make gradual personal progress almost impossible to notice.", "他人と比べ続けると、自分の小さな進歩が見えにくくなります。"),
            ("Keeping a short record can make quiet improvement easier to see.", "A brief record of completed actions can make slow, private improvement more visible over time.", "終えたことを短く記録すると、静かな成長が見えやすくなります。"),
            ("A good month can contain both a small win and an ongoing problem.", "A small success and a serious ongoing difficulty can both be true during the same month.", "よいことと、まだうまくいかないことは、同じ月に両方ありえます。"),
            ("Sharing a win with one trusted person can help us value it.", "Sharing a quiet achievement with one trusted person can validate it without turning it into a performance.", "信頼できる人に小さな成功を話すと、その価値を感じやすくなります。"),
            ("Our definition of success should fit the situation we are actually in.", "A useful definition of success responds to our actual circumstances rather than an ideal version of life.", "成功の基準は、理想ではなく今の状況に合っている必要があります。"),
            ("Noticing small wins gives us evidence that change is already happening.", "Recognizing small wins gives us evidence that change is occurring before the final outcome arrives.", "小さな成功に気づくと、最終結果の前から変化が起きていると分かります。"),
        ],
        "prompts": [
            prompt("A quiet win", "静かな成功", "Have you had any small wins this month, whether or not anyone noticed?", "誰かが気づいたかどうかに関係なく、今月、小さな成功はありましたか？", ["If yes, what effort did it take?", "If not, what has made this month difficult?"]),
            prompt("Effort this month", "今月の努力", "What has taken effort this month, even if the result is not clear yet?", "まだ結果がはっきりしていなくても、今月、努力が必要だったことは何ですか？", ["What part required the most patience?", "What progress can you see so far?"]),
            prompt("Why progress matters", "進歩が大切な理由", "What kind of progress matters to you right now?", "今、どんな進歩があなたにとって大切ですか？", ["What would it make easier?", "Would the same progress have mattered last year?"]),
            prompt("Who understands", "分かってくれる人", "Who, if anyone, understands the effort you put in?", "あなたの努力を分かってくれる人がいるなら、誰ですか？", ["What would you need to explain to others?", "Would sharing it change how you feel?"]),
            prompt("Do you notice wins?", "成功に気づく？", "Do you usually notice your own small wins?", "普段、自分の小さな成功に気づきますか？", ["What helps you notice them?", "Which wins do you often miss?"]),
            prompt("What's still difficult", "まだ難しいこと", "What has been hardest this month, if anything?", "今月、難しかったことがあるなら、何ですか？", ["If something comes to mind, what still needs attention?", "If not, what helped the month go well?"]),
            prompt("Praise and motivation", "褒め言葉とやる気", "Does praise make you want to keep going?", "褒められると、続けたい気持ちになりますか？", ["If yes, whose praise matters most?", "What helps when nobody praises you?"], full="Does praise affect your motivation?", full_followups=["If it does, whose praise matters most?", "What keeps you going without it?"]),
            prompt("A good month", "よい一か月", "What would count as a good month for you now?", "今のあなたにとって、どんな一か月ならよい月ですか？", ["Which result matters most?", "What small sign would show progress?"]),
        ],
    },
    18: {
        "slug": "a-song-you-keep-playing",
        "title": "A song you keep playing",
        "ko": "계속 듣게 되는 노래",
        "ja": "何度も聴いている曲",
        "goal": ("Let's talk about a song that has become part of your life lately.", "最近の生活の一部になっている曲について話しましょう。"),
        "outcomes": (("Describe one song", "一曲を説明する"), ("Connect it to a memory", "思い出とのつながりを話す"), ("Build your year's playlist", "今年のプレイリストを考える")),
        "article_title": ("Why one song stays on repeat", "一曲を繰り返し聴く理由"),
        "articles": [
            ("Repeating a song lets us enjoy something familiar while still noticing new details.", "Repeated listening combines the comfort of familiarity with the pleasure of discovering new details.", "同じ曲を繰り返すと、安心感を楽しみながら新しい細部にも気づけます。"),
            ("Sometimes the sound matters more than the meaning of the words.", "Sometimes rhythm, tone, or production matters more to us than the literal meaning of the lyrics.", "歌詞の意味より、音そのものが大切なこともあります。"),
            ("A song can quickly become connected to a place, person, or period of life.", "A song can become strongly associated with a place, a person, or a particular period of life.", "曲はすぐに、場所や人、人生のある時期と結びつくことがあります。"),
            ("Hearing it later can bring back details we thought we had forgotten.", "Hearing it much later can recover sensory and emotional details we thought we had forgotten.", "あとで聴くと、忘れたと思っていた細かなことが戻ってくることがあります。"),
            ("We also choose music to change or support our mood.", "We often use music deliberately either to change our mood or to remain inside it.", "気分を変えたり、その気分を保ったりするために音楽を選ぶこともあります。"),
            ("A song for work may be different from a song for walking home.", "The music that supports concentration may be very different from the music that fits a walk home.", "仕事に合う曲と、帰り道に合う曲は違うかもしれません。"),
            ("Overplaying a song can temporarily weaken its emotional effect.", "Overplaying a song can temporarily weaken the emotional response that made us love it.", "聴きすぎると、その曲が持っていた感情的な力が一時的に弱くなることがあります。"),
            ("After a break, the same song may feel fresh again.", "After enough distance, the same track can recover its freshness and emotional force.", "しばらく離れると、同じ曲がまた新鮮に感じられます。"),
            ("A personal playlist can become a record of a year without using words.", "A personal playlist can preserve the emotional history of a year without explaining it directly.", "自分のプレイリストは、言葉を使わずに一年の記録になります。"),
            ("The song we repeat now may later become the fastest way back to this moment.", "The song we repeat now may eventually become the quickest route back to this period of our life.", "今繰り返している曲が、将来この時期を思い出す一番早い方法になるかもしれません。"),
        ],
        "prompts": [
            prompt("A current song", "最近の曲", "Is there a song you've been playing a lot lately?", "最近よく聴いている曲はありますか？", ["If yes, who is the artist?", "If not, what kind of sound fits your mood lately?"]),
            prompt("One detail", "一つの細部", "What sound or musical detail has caught your attention lately?", "最近、どんな音や音楽の細部が気になりましたか？", ["What makes it stand out?", "Does it come from a particular song?"]),
            prompt("How long it lasts", "どのくらい続く？", "How long do you usually stay interested in one song?", "一曲を気に入ると、普段どのくらい聴き続けますか？", ["How often do you play it?", "What makes you move to another song?"]),
            prompt("A memory", "思い出すこと", "Can music bring back a specific memory for you?", "音楽を聴いて、具体的な思い出が戻ることはありますか？", ["If yes, what comes back first?", "If not, what does music bring to mind?"], full="Can music bring back a particular memory for you?", full_followups=["If yes, which details return first?", "If not, what does music bring to mind?"]),
            prompt("When you play music", "音楽を聴くとき", "When do you usually listen to music?", "普段、いつ音楽を聴きますか？", ["What mood are you usually in?", "Does music change what you are doing?"]),
            prompt("An old repeat", "昔繰り返した曲", "Is there a song you played too much years ago?", "何年か前に聴きすぎた曲はありますか？", ["If yes, can you enjoy it again now?", "If not, what usually makes you tire of a song?"]),
            prompt("Sharing music", "音楽を共有すること", "Would you send a song that fits your current mood to anyone?", "今の気分に合う曲を誰かに送りたいですか？", ["What would make you share it or keep it private?", "What kind of response would you hope for?"]),
            prompt("Your year as a playlist", "一年のプレイリスト", "If you made a playlist of your year, what would go on it?", "今年のプレイリストを作るなら、何を入れますか？", ["Which song would open it?", "What part of the year is still missing?"]),
        ],
    },
    19: {
        "slug": "something-youve-been-putting-off",
        "title": "Something you've been putting off",
        "ko": "계속 미루고 있는 것",
        "ja": "ずっと先延ばしにしていること",
        "goal": ("Let's understand one delayed task and make the next action clear.", "先延ばしにしていることを理解し、次の行動を明確にしましょう。"),
        "outcomes": (("Describe the delayed task", "先延ばしにしていることを話す"), ("Find the real barrier", "本当の障害を見つける"), ("Make the next decision", "次の判断を決める")),
        "article_title": ("Why we keep delaying things", "先延ばしを続ける理由"),
        "articles": [
            ("Putting something off creates a gap between what we intend and what we do.", "Procrastination creates an uncomfortable gap between our stated intention and our actual behavior.", "先延ばしをすると、やりたいことと実際の行動の間に差ができます。"),
            ("The task is often large, unclear, boring, or emotionally difficult.", "The delayed task is often too large, poorly defined, tedious, or emotionally uncomfortable.", "その課題は大きすぎたり、不明確だったり、退屈だったり、気持ちの面で難しかったりします。"),
            ("Saying we have no time can hide a problem with the first step.", "Saying we lack time can conceal the fact that we do not know how to begin.", "時間がないと言いながら、実は始め方が分からない場合もあります。"),
            ("Avoiding the task gives quick relief but keeps the worry alive.", "Avoidance provides immediate relief while preserving the background anxiety the task creates.", "避けると一時的に楽になりますが、不安は残ります。"),
            ("The longer we wait, the task can start to feel like a judgment about us.", "The longer the delay continues, the task can begin to feel like evidence about our character.", "長く待つほど、その課題が自分の性格への評価のように感じられることがあります。"),
            ("Self-criticism usually adds more emotion without making the next action easier.", "Harsh self-criticism usually increases the emotional load without clarifying the next action.", "自分を責めると、次の行動が楽になるどころか、気持ちの負担が増えることが多いです。"),
            ("A step small enough to finish in ten minutes can get us moving again.", "Defining an action small enough to complete in ten minutes can restore momentum.", "10分で終えられる小さな行動を決めると、また動き始められます。"),
            ("Another person or a fixed time can make starting easier.", "A clear appointment or gentle accountability from another person can lower the barrier to starting.", "決まった時間やほかの人の助けがあると、始めやすくなります。"),
            ("Remembering a task we finally completed can show what helped before.", "Looking back at something we eventually completed can reveal which strategy actually helped.", "以前やっと終えたことを思い出すと、何が役立ったか分かります。"),
            ("Sometimes the honest solution is to decide not to do the task at all.", "Sometimes the most responsible solution is to consciously decide not to do the task rather than pretend it remains a priority.", "ときには、もうしないと決めることが正直な解決になる場合もあります。"),
        ],
        "prompts": [
            prompt("Still not done", "まだしていないこと", "Is there anything you've been meaning to do but haven't?", "ずっとやろうと思っていて、まだしていないことはありますか？", ["If yes, when did you first decide to do it?", "If not, what helps you act on tasks quickly?"]),
            prompt("What you do instead", "代わりにすること", "When you avoid a task, what do you tend to do instead?", "課題を避けるとき、代わりに何をすることが多いですか？", ["Does that activity actually feel relaxing?", "When does the task return to your mind?"]),
            prompt("How long", "どのくらい", "When a task gets delayed, how long does it usually stay undone?", "課題を先延ばしにすると、普段どのくらい終わらないままですか？", ["What makes the delay grow?", "How much does a deadline change it?"]),
            prompt("The real barrier", "本当の障害", "What usually stops you from starting?", "普段、何が始めることを止めますか？", ["Is the first step usually clear?", "Which feeling comes up most often?"]),
            prompt("If it never gets done", "ずっとしなかったら", "What can happen when a task never gets done?", "課題をずっと終えないと、何が起こりえますか？", ["Who else might have a problem?", "When might it be better to stop?"], full_followups=["Who else might be affected?", "When would dropping it be the better choice?"]),
            prompt("A past delay", "以前の先延ばし", "Have you ever finally done something you had put off?", "先延ばしにしていたことを、最後には終えた経験がありますか？", ["If yes, what finally made you start?", "If not, what usually ends a delay for you?"]),
            prompt("After a delay", "先延ばしのあと", "If you finish something late, how do you usually feel?", "遅れて何かを終えたとき、普段どんな気持ちになりますか？", ["Does the result match the worry?", "If this has not happened, how do you think you would feel?"], full="If you finish a delayed task, how do you usually feel?", full_followups=["Does the result usually match the worry?", "If you have not had that experience, how do you think you would feel?"]),
            prompt("The next decision", "次の判断", "If something gets delayed again, what could you do next?", "また何かを先延ばしにしたら、次に何ができますか？", ["If you continue, what is a ten-minute step?", "If you stop, why is that the right choice?"], full="If a task gets delayed again, what could you do next?", full_followups=["If you continue, what's a ten-minute step?", "If you drop it, what makes that the right decision?"]),
        ],
    },
    20: {
        "slug": "one-thing-you-always-carry",
        "title": "One thing you always carry",
        "ko": "항상 가지고 다니는 것",
        "ja": "いつも持ち歩いているもの",
        "goal": ("Let's use what's in your bag to talk about your daily life.", "かばんの中身から、日常生活について話しましょう。"),
        "outcomes": (("Describe what you carry", "持ち歩く物を説明する"), ("Explain how it has changed", "中身の変化を話す"), ("Connect it to your routine", "日課とのつながりを話す")),
        "article_title": ("The life inside a bag", "かばんの中にある生活"),
        "articles": [
            ("A bag holds the things we expect to need away from home.", "A bag is a portable collection of what we expect to need while we are away from home.", "かばんには、外出先で必要だと思う物を入れます。"),
            ("The things we use every day are usually easy to reach.", "Items used every day are usually kept in the easiest places to reach.", "毎日使う物は、たいてい取り出しやすい場所に入っています。"),
            ("Other items stay there for an emergency that may never happen.", "Other objects remain as preparation for an unlikely emergency that may never occur.", "ほかの物は、起こらないかもしれない緊急時のために入っています。"),
            ("Receipts and forgotten objects can stay in a bag for months because we never decide to remove them.", "Receipts and forgotten objects can remain for months because removing them requires a tiny decision.", "レシートや忘れた物は、出すか決めないまま何か月もかばんに残ることがあります。"),
            ("A heavy bag can show how many different situations we are trying to prepare for.", "A heavy bag can reveal how much uncertainty we try to manage by carrying extra options.", "かばんが重いと、いろいろな状況に備えようとしていることが分かります。"),
            ("The contents change when our work, health, or responsibilities change.", "The contents evolve as our work, health, technology, and responsibilities change.", "仕事や健康、責任が変わると、中身も変わります。"),
            ("Phones have replaced many separate tools, but they have also added chargers.", "Phones have replaced many separate tools while creating a new dependence on batteries and chargers.", "スマートフォンは多くの道具に取って代わりましたが、今度は充電器を持つ必要が生まれました。"),
            ("Some objects are useful mainly because they make us feel prepared.", "Some objects provide more psychological reassurance than practical value.", "実際に役立つより、持っていると安心する物もあります。"),
            ("Cleaning a bag forces us to decide what still belongs in our routine.", "Cleaning out a bag forces a small audit of what still belongs in our current routine.", "かばんを整理すると、今の生活にまだ必要な物か決めることになります。"),
            ("One ordinary object can tell a surprisingly detailed story about a person's day.", "One ordinary object can reveal a surprisingly detailed story about a person's habits, priorities, and day.", "普通の一つの物から、その人の一日について意外に詳しいことが分かります。"),
        ],
        "prompts": [
            prompt("A bag today", "今日のかばん", "Do you have a bag with you today?", "今日はかばんを持っていますか？", ["If yes, what kind of bag is it?", "If not, did you bring anything with you?"]),
            prompt("What you carry", "持ち歩く物", "When you go out, what do you usually carry, if anything?", "外出するとき、持ち歩く物があるなら何ですか？", ["Do you use a bag or your pockets?", "What do you sometimes choose not to take?"]),
            prompt("What's inside", "入っている物", "If you use a bag, what kinds of things are usually in it?", "かばんを使うなら、普段どんな物を入れますか？", ["If you use one, what kind takes the most space?", "If not, do you carry anything in your pockets?"], full_followups=["If you use one, which category takes the most space?", "If not, do you carry anything in your pockets?"]),
            prompt("What you use", "実際に使う物", "What do you use most when you are away from home?", "外出中、いちばんよく使う物は何ですか？", ["What would be hard to replace?", "What saves you the most time?"]),
            prompt("There for months", "何か月もある物", "If you use a bag, does anything stay there for months without use?", "かばんを使うなら、何か月も使わずに入れたままの物はありますか？", ["If yes, why is it still there?", "If not, what keeps your things organized?"]),
            prompt("Always forgotten", "いつも忘れる物", "Is there anything you often forget when you go out?", "外出するとき、よく忘れる物はありますか？", ["What helps you remember it?", "What do you do when it is missing?"]),
            prompt("How it changed", "変わった持ち物", "Has what you carry changed over the past few years?", "ここ数年で、持ち歩く物は変わりましたか？", ["If yes, what did you stop carrying?", "If not, why have your needs stayed the same?"], full_followups=["If yes, what did you stop carrying?", "If not, what has kept your needs stable?"]),
            prompt("What it says", "持ち物が語ること", "What do the things you carry every day say about your day?", "普段の持ち物から、あなたの一日について何が分かりますか？", ["What best shows your usual routine?", "What might someone get wrong?"], full="What might someone learn about your day from what you carry?", full_followups=["What best represents your routine?", "What might someone misunderstand?"]),
        ],
    },
}


def vocab(*, new="", recycled="", assumed="", receptive=""):
    """Return one variant's editorial vocabulary contract."""
    return {
        "new": new,
        "recycled": recycled,
        "assumed": assumed,
        "receptive": receptive,
    }


# Vocabulary ownership follows the language actually present in each rendering.
# Full-only article terms must not silently inflate the accessible contract, and
# tutor prompts are not assigned to Core merely because they contain a familiar
# grammatical word.
VOCABULARY = {
    10: {
        "accessible": vocab(
            new="curiosity|好奇心; experiment|試すこと",
            assumed="interest|興味; hobby|趣味; habit|習慣; video|動画; friend|友人; time|時間; progress|進歩; advice|助言; free time|自由時間",
            receptive="private|人に話さない; reaction|反応; encouragement|励まし",
        ),
        "full": vocab(
            new="curiosity|好奇心; experiment|試すこと",
            assumed="interest|興味; hobby|趣味; habit|習慣; video|動画; friend|友人; time|時間; progress|進歩; advice|助言; free time|自由時間",
            receptive="private|人に話さない; reaction|反応; trade-off|一方を得るための代償; enthusiasm|熱意; opportunity cost|機会費用; identity|自分らしさ; competent|十分にできる; encouragement|励まし; community|仲間; pastime|暇つぶし",
        ),
    },
    11: {
        "accessible": vocab(
            new="streaming|動画配信; binge-watch|一気見する; recommendation|おすすめ",
            assumed="show|番組; story|物語; character|登場人物; episode|話; series|シリーズ; ending|結末; mood|気分; sleep|睡眠; choice|選択; attention|注意; halfway|途中まで; rewarding|満足感のある",
            receptive="dropping|途中でやめる; satisfying|満足できる",
        ),
        "full": vocab(
            new="binge-watch|一気見する; recommendation|おすすめ",
            assumed="show|番組; story|物語; character|登場人物; episode|話; series|シリーズ; ending|結末; mood|気分; sleep|睡眠; choice|選択; attention|注意; halfway|途中まで",
            receptive="streaming service|配信サービス; obligation|義務; compelling|人を引きつける; enthusiasm|熱意; emotional experience|感情的な体験; plot|筋書き",
        ),
    },
    12: {
        "accessible": vocab(
            new="specific praise|具体的な褒め言葉",
            assumed="compliment|褒め言葉; praise|褒めること; criticism|批判; effort|努力; memory|記憶; ability|能力; comment|言葉; response|返事; kind|優しい",
            receptive="believable|信じられる; danger|危険",
        ),
        "full": vocab(
            new="specific praise|具体的な褒め言葉",
            assumed="compliment|褒め言葉; praise|褒めること; criticism|批判; effort|努力; memory|記憶; ability|能力; response|返事; recognize|気づく",
            receptive="credible|信じられる; self-promotion|自己宣伝; bias|偏り; sincere|心からの; threat|脅威; minimize|小さく扱う; overlooked|見落とされた; reshape|捉え直す",
        ),
    },
    13: {
        "accessible": vocab(
            new="backup plan|予備の案; fall through|予定がだめになる",
            assumed="weekend|週末; weather|天気; rest|休息; time|時間; place|場所; cost|費用; activity|活動; health|体調; alone|一人で",
            receptive="meaningful|意味のある; arranged|計画した; unplanned|予定外の",
        ),
        "full": vocab(
            new="backup plan|予備の案; fall through|予定がだめになる",
            assumed="weekend|週末; weather|天気; rest|休息; time|時間; place|場所; cost|費用; activity|活動; health|体調; responsibility|用事; expectation|期待; alone|一人で",
            receptive="anticipate|楽しみに待つ; solitude|一人の時間; coordination|調整; uncommitted|予定を入れていない; improvised|即席の; disrupt|中断させる; leisure|余暇",
        ),
    },
    14: {
        "accessible": vocab(
            new="barrier|障害",
            assumed="goal|目標; year|年; plan|計画; step|一歩; time|時間; pressure|プレッシャー; result|結果; action|行動; deadline|期限; fear|不安",
            receptive="vague|曖昧な; uncertainty|不確かさ",
        ),
        "full": vocab(
            new="barrier|障害",
            assumed="goal|目標; year|年; plan|計画; step|一歩; time|時間; pressure|プレッシャー; result|結果; action|行動; deadline|期限; fear|不安; judgment|評価; identity|自分らしさ",
            receptive="vague|曖昧な; postpone|先延ばしにする; accountability|やり遂げる責任感; priority|優先事項; ambiguous|曖昧な; non-negotiable|譲れない; observable|観察できる; outdated|今は合わない",
        ),
    },
    15: {
        "accessible": vocab(
            new="cost per use|一回あたりの費用; budget|予算",
            assumed="money|お金; spend|使う; price|値段; hobby|趣味; quality|品質; income|収入; value|価値; rent|家賃; payment|支払い; monthly|毎月",
            receptive="basic cost|基本的な費用; meaningful|意味のある",
        ),
        "full": vocab(
            new="cost per use|一回あたりの費用; budget|予算",
            assumed="money|お金; spend|使う; price|値段; hobby|趣味; quality|品質; income|収入; value|価値; rent|家賃; payment|支払い; category|分野; responsibility|責任",
            receptive="discretionary|自由に使える; recurring|繰り返す; durability|耐久性; sustainable|無理なく続けられる; replacement|買い替え; economical|経済的な; significance|重要性; irrational|不合理な; accumulate|積み重なる",
        ),
    },
    16: {
        "accessible": vocab(
            new="beginner|初心者; nervousness|緊張",
            assumed="first time|初めて; experience|体験; routine|日課; try|試す; result|結果; instruction|説明; expectation|予想; reality|実際; capable|できる",
            receptive="uncomfortable|落ち着かない",
        ),
        "full": vocab(
            new="first attempt|最初の挑戦; beginner|初心者",
            assumed="first time|初めて; experience|体験; routine|日課; try|試す; expectation|予想; reality|実際; growth|成長; capable|できる",
            receptive="nervousness|緊張; uncertainty|不確かさ; novel|新奇な; companion|一緒にする人; shortcut|慣れたやり方; lasting value|長く続く価値",
        ),
    },
    17: {
        "accessible": vocab(
            new="small win|小さな成功",
            assumed="win|成功; month|月; praise|褒めること; progress|進歩; problem|問題; result|結果; record|記録; comparison|比較; difficulty|難しさ; effort|努力",
            receptive="ongoing|続いている",
        ),
        "full": vocab(
            new="small win|小さな成功; motivation|やる気",
            assumed="win|成功; month|月; praise|褒めること; progress|進歩; result|結果; record|記録; comparison|比較; difficulty|難しさ; effort|努力",
            receptive="external praise|周囲からの評価; achievement|達成; validate|価値を認める; circumstance|状況; applause|拍手; gradual|少しずつの; performance|人に見せる行為; unreliable measure|信頼できない尺度",
        ),
    },
    18: {
        "accessible": vocab(
            new="on repeat|繰り返し; overplay|聴きすぎる",
            assumed="song|曲; music|音楽; mood|気分; playlist|プレイリスト; year|年; detail|細部; sound|音; artist|アーティスト; memory|思い出",
            receptive="emotional effect|感情への効果; familiar|なじみのある",
        ),
        "full": vocab(
            new="on repeat|繰り返し; overplay|聴きすぎる",
            assumed="song|曲; music|音楽; lyrics|歌詞; mood|気分; playlist|プレイリスト; year|年; detail|細部; sound|音; artist|アーティスト; memory|思い出; concentration|集中; familiarity|慣れ親しんだ感じ",
            receptive="production|音作り; associate|結びつける; emotional force|感情的な力; sensory|感覚の; emotional history|感情の記録",
        ),
    },
    19: {
        "accessible": vocab(
            new="put off|先延ばしにする; self-criticism|自己批判",
            recycled="avoid|避ける|CORE-63",
            assumed="task|課題; time|時間; worry|心配; action|行動; step|一歩; problem|問題; decide|決める; deadline|期限",
            receptive="judgment|評価; emotional difficulty|気持ちの難しさ",
        ),
        "full": vocab(
            new="put off|先延ばしにする; procrastination|先延ばし; self-criticism|自己批判",
            assumed="task|課題; time|時間; worry|心配; action|行動; step|一歩; decide|決める; deadline|期限; criticism|批判; strategy|方法; priority|優先事項",
            receptive="anxiety|不安; momentum|勢い; avoidance|回避; accountability|やる責任を支えること; tedious|退屈な; emotional load|感情的な負担; clarify|明確にする",
        ),
    },
    20: {
        "accessible": vocab(
            new="emergency|緊急時",
            assumed="bag|かばん; phone|スマートフォン; charger|充電器; receipt|レシート; work|仕事; day|一日; home|家; health|健康; responsibility|責任; routine|日課",
            receptive="uncertainty|不確かさ",
        ),
        "full": vocab(
            new="reassurance|安心感",
            assumed="bag|かばん; phone|スマートフォン; charger|充電器; receipt|レシート; work|仕事; day|一日; home|家; health|健康; technology|技術; battery|バッテリー; responsibility|責任; routine|日課; emergency|緊急時",
            receptive="portable|持ち運べる; audit|見直し; psychological|心理的な; uncertainty|不確かさ; priority|優先順位; practical|実用的な; dependence|依存; clean out|中身を整理する",
        ),
    },
}


# Stable semantic row identities make the accessible/full pairing reviewable:
# both variants render this exact order even when their wording and Japanese
# support differ.
CLAIM_ORDER = {
    10: ("curiosity-origin", "first-trigger", "visible-progress", "regular-habit", "community-support", "privacy-until-ready", "time-tradeoff", "progress-and-space", "stopping-is-valid", "interest-and-identity"),
    11: ("abundant-choice", "starting-is-hard", "opening-question", "character-pull", "personal-recommendation", "binge-cost", "dropping-is-valid", "mood-and-attention", "ending-reshapes-memory", "next-emotional-experience"),
    12: ("brief-praise-lasts", "specific-is-credible", "unseen-effort", "awkward-rejection", "accept-with-thanks", "criticism-bias", "remember-praise", "attention-to-effort", "timing-matters", "praise-reshapes-ability"),
    13: ("anticipation", "different-recovery", "rest-and-meaning", "coordination", "disruption", "backup-plan", "overscheduling", "open-time", "improvised-alternative", "weekend-reveals-need"),
    14: ("deadline-decides", "one-priority", "unclear-first-step", "small-action", "emotional-barrier", "release-old-goal", "accountability-and-pressure", "consistent-next-step", "act-this-week", "revise-with-information"),
    15: ("spending-shows-values", "recurring-costs", "outsider-judgment", "price-is-incomplete", "cost-per-use", "quality-and-durability", "sunk-cost-pressure", "judgment-can-change", "budget-for-joy", "spending-fits-life"),
    16: ("routine-narrows", "attention-returns", "expectations-first", "nerves-show-value", "support-lowers-uncertainty", "reality-differs", "beginner-discomfort", "second-attempt", "growth-continues", "one-first-leads-next"),
    17: ("progress-can-be-invisible", "ordinary-win", "effort-is-hidden", "praise-is-not-proof", "comparison-hides-progress", "record-progress", "win-and-problem-coexist", "trusted-sharing", "situational-success", "wins-show-change"),
    18: ("familiarity-and-detail", "sound-over-meaning", "song-association", "memory-recovery", "music-and-mood", "music-by-context", "overplaying", "distance-restores", "playlist-as-record", "song-returns-us"),
    19: ("intention-action-gap", "task-friction", "time-hides-unclear-start", "avoidance-relief", "delay-becomes-judgment", "criticism-adds-load", "small-step-restores", "support-lowers-barrier", "past-strategy", "conscious-drop"),
    20: ("portable-expectations", "easy-reach", "emergency-items", "forgotten-items", "weight-and-uncertainty", "contents-evolve", "phone-replaces-and-adds", "reassurance", "bag-audit", "object-reveals-day"),
}


REQUIRED_VOCABULARY = {
    10: ("private", "reaction", "trade-off", "experiment"),
    11: ("recommendation", "attention", "rewarding", "choice"),
    13: ("responsibility", "expectation"),
    14: ("deadline", "barrier", "judgment", "identity"),
    15: ("rent", "payment", "category", "responsibility"),
    16: ("expectation", "reality", "growth"),
    17: ("motivation", "comparison", "difficulty"),
    18: ("artist", "memory", "concentration", "familiarity"),
    19: ("deadline", "anxiety", "criticism", "strategy"),
    20: ("health", "technology", "battery", "responsibility", "routine"),
}


# Glosses are editorial comprehension decisions, not a quota. Each selected item
# carries a claim in a row that would otherwise be harder than the version's
# entry level; ordinary topic words remain unhighlighted.
GLOSSES = {
    10: {"accessible": {1: ("curiosity", "curiosity", "好奇心")}, "full": {7: ("opportunity cost", "opportunity cost", "機会費用")}},
    11: {"accessible": {1: ("Streaming", "streaming", "動画配信"), 6: ("Binge-watching", "binge-watch", "一気見する")}, "full": {6: ("Binge-watching", "binge-watch", "一気見する"), 7: ("obligation", "obligation", "義務")}},
    12: {"accessible": {6: ("Criticism", "criticism", "批判")}, "full": {2: ("credible", "credible", "信じられる")}},
    13: {"accessible": {6: ("backup plan", "backup plan", "予備の案")}, "full": {1: ("anticipate", "anticipate", "楽しみに待つ")}},
    14: {"accessible": {1: ("vague", "vague", "曖昧な")}, "full": {7: ("accountability", "accountability", "やり遂げる責任感")}},
    15: {"accessible": {5: ("Cost per use", "cost per use", "一回あたりの費用")}, "full": {1: ("discretionary", "discretionary", "自由に使える")}},
    16: {"accessible": {4: ("Nervousness", "nervousness", "緊張")}, "full": {7: ("beginner", "beginner", "初心者")}},
    17: {"accessible": {4: ("Praise", "praise", "褒めること")}, "full": {8: ("validate", "validate", "価値を認める")}},
    18: {"accessible": {9: ("playlist", "playlist", "プレイリスト")}, "full": {2: ("production", "production", "音作り")}},
    19: {"accessible": {1: ("Putting something off", "put off", "先延ばしにする")}, "full": {1: ("Procrastination", "procrastination", "先延ばし")}},
    20: {"accessible": {3: ("emergency", "emergency", "緊急時")}, "full": {8: ("reassurance", "reassurance", "安心感")}},
}


# Most paired rows express exactly the same claim naturally with one Japanese
# rendering. These overrides are required where the full row adds a material
# relation, condition, or implication that the accessible Japanese does not.
FULL_JA_OVERRIDES = {
    10: {
        1: "新しい興味は、本格的な計画ではなく、ふとした好奇心から始まることがよくあります。",
        2: "動画や友人の熱意、意外な結果だけで、一度試してみようと思うことがあります。",
        3: "最初は、小さな発見でも目に見える上達になるので、わくわくします。",
        4: "定期的に使う時間をきちんと守って初めて、その興味は習慣になっていきます。",
        5: "仲間から助言や道具、励ましを得ると、興味がさらに深まります。",
        6: "人に説明できるほど上手になったと感じるまで、新しい趣味を話さない人もいます。",
        8: "小さく具体的な進歩は、その興味に生活の中でどのくらい時間を使う価値があるか判断する助けになります。",
        10: "長く続けば、その興味は単なる暇つぶしではなく、自分らしさの一部になるかもしれません。",
    },
    11: {7: "見続けることが娯楽より義務のように感じられたら、途中でやめるのは自然な判断です。"},
    12: {
        1: "褒め言葉は数秒で終わっても、何年も記憶に残ることがあります。",
        10: "誠実でタイミングのよい一言が、その人自身の能力の捉え方を変えることがあります。",
    },
    13: {
        1: "週末に具体的な楽しみがあると、一週間の流れに区切りが生まれます。",
        4: "人と一緒の予定では、時間、場所、費用、期待の違いを調整する必要があります。",
        5: "天気、体調、予想外の用事で、よく考えた予定も変わることがあります。",
        10: "望む週末には、その時の生活に欠けているものが表れることがあります。",
    },
    14: {
        1: "期限があると、ぼんやりした願いが、実際の時間を使う決断に変わります。",
        3: "最初の行動が曖昧だったり、不快だったり、大きすぎたりすると、目標を先延ばしにしがちです。",
        5: "本当の障害は時間不足とは限らず、不安や自信のなさ、人の評価への恐れも関係します。",
        6: "今の自分らしさに合わない古い目標を意識して手放すと、今も大切なことのための余裕ができます。",
        7: "目標を人に話すと、やり遂げる責任感が生まれますが、望まないプレッシャーにもなりえます。",
        8: "最終結果よりも、次の一歩を着実に続けられるようになることが大切な場合もあります。",
        10: "新しい情報によって可能なことや価値のあることが変われば、本気の目標でも見直せます。",
    },
    15: {
        3: "趣味に使うお金は、その価値を理解しない人には不合理に見えることがあります。",
        4: "値段だけでは、役立ち方、節約できた時間、楽しさ、感情的な意味は測れません。",
        8: "収入、責任、日々の習慣が変わると、何を無駄だと判断するかも変わります。",
    },
    16: {
        2: "初めての挑戦では、慣れたやり方が通用しないため、もう一度よく注意することになります。",
        3: "新しい体験の前には、人の話や不完全な情報から予想を作ります。",
        4: "緊張は必ずしも危険のサインではなく、結果が自分にとって大切だという表れの場合もあります。",
        6: "実際の体験は、想像より楽な点も難しい点もあることがよくあります。",
        8: "二度目に試すと、その活動に長く続く価値があるのか、新しいから楽しかっただけなのかが分かります。",
        9: "最近の初めてを思い出すと、成長は特定の年齢で終わるわけではないと分かります。",
        10: "初めての体験がうまくいくと、次に挑戦してみようと思えることの幅が広がります。",
    },
    17: {
        3: "その努力を知らない人には、そのような成功はまったく普通に見えることがあります。",
        4: "人から褒められるのはうれしいものですが、それで達成の価値を正確に測れるとは限りません。",
        5: "絶えず他人と比べていると、自分の少しずつの進歩にほとんど気づけなくなります。",
        7: "小さな成功と、今も続く深刻な問題は、同じ月に両方ありえます。",
        8: "信頼できる人に静かな達成を話すと、人に見せる行為に変えずに、その価値を認められます。",
    },
    18: {
        2: "歌詞の文字どおりの意味より、リズムや声の調子、音作りが大切なこともあります。",
        4: "ずっとあとで聴くと、忘れたと思っていた感覚や感情の細部が戻ってくることがあります。",
        6: "集中しやすい音楽と、帰り道に合う音楽は大きく違うことがあります。",
        8: "十分な時間を置くと、同じ曲に新鮮さと感情を動かす力が戻ることがあります。",
        9: "自分のプレイリストは、直接説明しなくても一年の感情の歴史を残せます。",
    },
    19: {
        6: "厳しく自分を責めても次の行動は明確にならず、感情的な負担が増えることが多いです。",
        8: "明確な約束の時間や、ほかの人からの穏やかな働きかけが、始めるハードルを下げることがあります。",
        10: "まだ優先事項だと装い続けるより、意識してその課題をしないと決めるほうが責任ある場合もあります。",
    },
    20: {
        1: "かばんは、家を離れている間に必要だと思う物をまとめて持ち運べる入れ物です。",
        2: "毎日使う物は、たいてい最も取り出しやすい場所に入っています。",
        5: "余分な選択肢を持ち歩くことで、どれほど不確かなことに対処しようとしているかが、重いかばんに表れます。",
        6: "仕事、健康、技術、責任が変わるにつれて、かばんの中身も変化します。",
        7: "スマートフォンは多くの道具に取って代わった一方で、バッテリーと充電器への新たな依存も生みました。",
        10: "普通の一つの物から、その人の習慣、優先順位、一日について意外に詳しいことが分かります。",
    },
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def set_meta(head: str, name: str, value: str) -> str:
    pattern = rf'(<meta name="{re.escape(name)}" content=")[^"]*(")'
    return re.sub(pattern, lambda m: m.group(1) + esc(value) + m.group(2), head, count=1)


def set_proofread_complete(head: str) -> str:
    name = "podo:proofread-status"
    if f'name="{name}"' in head:
        return set_meta(head, name, "complete")
    marker = r'(<meta name="podo:content-version" content="[^"]+">)'
    return re.sub(
        marker,
        rf'\1\n  <meta name="{name}" content="complete">',
        head,
        count=1,
    )


def page(page_id: str, title: str, title_ja: str, body: str) -> str:
    return f'''    <div class="section" data-page-id="{page_id}">
      <h2 class="section-title">{esc(title)} <span class="title-ja">({esc(title_ja)})</span></h2>
{body}
    </div>\n'''


def extract_page(source: str, page_id: str) -> str:
    start = source.index(f'<div class="section" data-page-id="{page_id}">')
    next_section = source.find("\n    <div ", start + 1)
    end = source.index("\n  </div>", start) if next_section < 0 else next_section
    return "    " + source[start:end].strip() + "\n"


def marked_text(text: str, gloss) -> tuple[str, str]:
    if not gloss:
        return esc(text), ""
    surface, headword, meaning = gloss
    before, found, after = text.partition(surface)
    if not found:
        raise ValueError(f"gloss surface {surface!r} is absent from {text!r}")
    marked = f'{esc(before)}<span class="s-key">{esc(found)}</span>{esc(after)}'
    words = f'<span class="s-words"><span class="s-w"><b>{esc(headword)}</b>{esc(meaning)}</span></span>'
    return marked, words


def article_page(topic_no: int, topic: dict, variant: str) -> str:
    rows = []
    column = 0 if variant == "accessible" else 1
    for index, (article, claim_id) in enumerate(zip(topic["articles"], CLAIM_ORDER[topic_no], strict=True), start=1):
        en = article[column]
        ja = FULL_JA_OVERRIDES.get(topic_no, {}).get(index, article[2]) if variant == "full" else article[2]
        en_markup, words = marked_text(en, GLOSSES[topic_no][variant].get(index))
        rows.append(
            f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{esc(ja)}</span>{words}</span></div>'
        )
    title, title_ja = topic["article_title"]
    body = '''      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>
      <div class="tutor-note">Answer the learner's questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>
      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">
''' + "\n".join(rows) + '''
      </div>'''
    return page("article", title, title_ja, body)


def question_page(page_id: str, number: str, item: dict, variant: str) -> str:
    en = item[variant]
    followups = item[f"{variant}_followups"]
    lis = "".join(f"<li>{esc(value)}</li>" for value in followups)
    body = f'''      <p class="section-subtitle ask"><span class="q-n">{number}</span><span class="ko">{esc(en)}</span><span class="ja">{esc(item["ja"])}</span></p>
      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span><ul class="tn-more">{lis}</ul></div></div>
      <div class="fb" data-fb="{variant}-{page_id}"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'''
    return page(page_id, item["title"], item["title_ja"], body)


def build(topic_no: int, variant: str) -> str:
    topic = TOPICS[topic_no]
    canonical = CANONICAL[variant].read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{topic["slug"]}'
    level = "B1 accessible" if variant == "accessible" else "B2-C1 full"
    head = new_lesson.retarget(
        head,
        review_id=f"FT-{topic_no}", lesson_id=slug, level=level,
        title=topic["title"], title_ko=topic["ko"], title_ja=topic["ja"],
        version="2026-08-20",
    )
    head = set_proofread_complete(head)
    head = set_meta(head, "podo:vocabulary-status", "reviewed")
    vocabulary = VOCABULARY[topic_no][variant]
    head = set_meta(head, "podo:vocabulary:new", vocabulary["new"])
    head = set_meta(head, "podo:vocabulary:recycled", vocabulary["recycled"])
    head = set_meta(head, "podo:vocabulary:assumed", vocabulary["assumed"])
    head = set_meta(head, "podo:vocabulary:receptive", vocabulary["receptive"])

    goal_en, goal_ja = topic["goal"]
    outcome_rows = topic["outcomes"]
    rows = "".join(
        f'<div class="known-row"><span class="k">{esc(en)}</span><span class="j">{esc(ja)}</span></div>'
        for en, ja in outcome_rows
    )
    pages = [
        f'''    <div class="transition-page" data-page-id="lesson-goal" data-act="Me lately">
      <span class="transition-kicker">ME LATELY</span>
      <h2 class="transition-title">{esc(topic["title"])} <span class="title-ja">({esc(topic["ja"])})</span></h2>
      <p class="section-subtitle"><span class="ko">{esc(goal_en)}</span><span class="ja">{esc(goal_ja)}</span></p>
      <div class="known lines">{rows}</div>
    </div>\n''',
        article_page(topic_no, topic, variant),
        extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="transition-copy">全部答えなくても大丈夫です。一つの答えをゆっくり広げましょう。</p></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple(
        (f"q{i}", f"QUESTION {i}") for i in range(1, 7)
    )
    pages.extend(
        question_page(page_id, number, item, variant)
        for (page_id, number), item in zip(prompt_ids, topic["prompts"], strict=True)
    )
    pages.append(extract_page(canonical, "feedback"))
    output = TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"
    return new_lesson.redepth(head + "\n".join(pages) + foot, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="regenerate only paths owned by this narrow generator")
    args = parser.parse_args()
    written = 0
    for topic_no in TOPICS:
        for variant in ("accessible", "full"):
            slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
            output = TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {output.relative_to(ROOT)}")
            written += 1
    print(f"{written} Freetalking decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
