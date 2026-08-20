#!/usr/bin/env python3
"""Generate the approved FT 2-6 and 8 accessible/full course pairs.

This is deliberately a narrow course-batch generator.  It preserves the approved
FT-1 shell and thirteen-page interaction contract while keeping topic content in
one reviewable data table.  Existing decks are never overwritten.
"""

from __future__ import annotations

import html
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/3-freetalking"
COURSE = "talk-between-two-countries"
CANONICAL = {
    "accessible": TRACK / "courses/talk-between-two-countries-accessible/lessons/01-this-surprised-me/lesson.html",
    "full": TRACK / "courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html",
}


TOPICS = {
    2: {
        "slug": "what-people-get-wrong-about-japan",
        "title": "What people often get wrong about Japan",
        "ko": "사람들이 일본에 대해 자주 오해하는 것",
        "ja": "日本についてよく誤解されること",
        "goal": ("Let's talk about an idea about Japan that does not match everyday reality.", "日本について、実際の日常とは合わないイメージを話しましょう。"),
        "opening": ("What do people from other countries assume about Japan that isn't true?", "外国の人が日本について思い込みがちで、実際とは違うことは何ですか？"),
        "article_title": ("How national images become shortcuts", "国のイメージが思い込みになるまで"),
        "article": [
            ("People often learn about Japan through a small number of films, news stories, and online posts.", "日本について、限られた映画やニュース、ネット投稿から知る人は少なくありません。"),
            ("Those sources usually show what is unusual or easy to remember, not ordinary life.", "そうした情報は、普通の日常よりも珍しくて覚えやすいものを見せがちです。"),
            ("A true detail can therefore grow into a claim about everyone.", "そのため、一部では本当のことが、全員に当てはまる話へ広がることがあります。"),
            ("For example, being polite does not mean that every person is quiet or formal.", "たとえば、礼儀正しいことは、全員が静かで堅いという意味ではありません。"),
            ("Regional, generational, and personal differences can be larger than visitors expect.", "地域、世代、個人による違いは、旅行者の予想より大きいことがあります。"),
            ("Some stereotypes sound positive, so people may not notice that they still flatten real lives.", "好意的に聞こえる固定観念もあるため、現実の生活を単純化していると気づきにくいことがあります。"),
            ("People inside a country also repeat simple stories about themselves.", "その国に住む人も、自分たちについて単純な話を繰り返すことがあります。"),
            ("One useful response is to replace 'Japanese people are' with a narrower question.", "「日本人は〜だ」を、もっと具体的な質問に置き換えることが役立ちます。"),
            ("We can ask where, when, and for whom an idea is actually true.", "その考えが、どこで、いつ、誰に当てはまるのかを聞くことができます。"),
            ("A better question leaves room for evidence instead of protecting the stereotype.", "よりよい質問は、固定観念を守るのではなく、事実を知る余地を残します。"),
        ],
        "gloss": {6: ("stereotypes", "stereotype", "固定観念"), 10: ("evidence", "evidence", "根拠")},
        "questions": [
            ("The common idea", "よくあるイメージ", "What do people often assume about Japan?", "日本について、どんな思い込みがよくありますか？", ["Where have you heard that idea most often?", "Which part sounds believable at first?"]),
            ("Where it comes from", "イメージの出どころ", "Where do you think that image comes from?", "そのイメージはどこから来ると思いますか？", ["Does media or personal experience matter more here?", "Why is that image easy to remember?"]),
            ("The reality", "実際のところ", "What is everyday reality actually like?", "実際の日常はどのようなものですか？", ["Who or where would be an exception?", "What example would make the difference clear?"]),
            ("Turn it around", "逆に考えよう", "What do you assume about my country?", "あなたは私の国について、どんなイメージを持っていますか？", ["How confident are you that it is true?", "What would you want to check with a local person?"]),
            ("A changed view", "変わった見方", "Have you ever realized you were wrong about a place?", "ある場所について、自分の考えが間違っていたと気づいたことはありますか？", ["What changed your mind?", "What part of your old view remained?"]),
            ("A better question", "よりよい質問", "What should visitors ask instead of making that assumption?", "思い込む代わりに、旅行者は何を聞くとよいですか？", ["Who would give the most useful answer?", "How might the answer differ across Japan?"]),
        ],
    },
    3: {
        "slug": "a-japanese-food-everyone-should-try",
        "title": "A Japanese food everyone should try",
        "ko": "모두가 먹어 봐야 할 일본 음식",
        "ja": "みんなに食べてほしい日本の料理",
        "goal": ("Let's choose one Japanese food and make me want to try it.", "日本の料理を一つ選び、食べてみたくなるように話しましょう。"),
        "opening": ("What food would you make me eat if I came to Japan?", "私が日本に来たら、何を食べさせたいですか？"),
        "article_title": ("Why a dish needs a story", "料理に物語が必要な理由"),
        "article": [
            ("A food recommendation is more useful when it explains an experience, not only a name.", "料理のおすすめは、名前だけでなく体験まで説明すると役に立ちます。"),
            ("The same dish can taste very different depending on the season, region, and place that serves it.", "同じ料理でも、季節、地域、出す店によって味は大きく変わります。"),
            ("Texture and smell may be more important than ingredients for a first-time visitor.", "初めて食べる人には、材料より食感や香りのほうが大切なことがあります。"),
            ("A local person also knows when the dish is at its best and what should be eaten with it.", "地元の人なら、その料理がいちばんおいしい時期や、一緒に食べるものも知っています。"),
            ("That context turns an unfamiliar food into something easier to imagine.", "そうした背景があると、知らない料理でも想像しやすくなります。"),
            ("Warnings can help too, especially when a flavor is strong or the eating method is unexpected.", "味が強かったり食べ方が意外だったりする場合は、注意点も役立ちます。"),
            ("However, changing every difficult feature may remove the character of the dish.", "ただし、難しい特徴を全部変えると、その料理らしさがなくなることがあります。"),
            ("A good host decides what can be adjusted and what should stay authentic.", "よい案内役は、変えてよい部分と、本来のまま残す部分を考えます。"),
            ("The best recommendation connects taste with a place, a person, or a memory.", "最高のおすすめは、味を場所、人、思い出と結びつけます。"),
            ("Then the visitor is not just trying food; they are sharing part of someone's life.", "そうすると旅行者は、料理だけでなく、その人の暮らしの一部も味わえます。"),
        ],
        "gloss": {3: ("Texture", "texture", "食感"), 8: ("authentic", "authentic", "本来のままの")},
        "questions": [
            ("Your choice", "あなたの一品", "What is the one food I have to try?", "私が絶対に食べるべき料理は何ですか？", ["Why did you choose it over other famous dishes?", "What is the first thing I would notice?"]),
            ("Taste and texture", "味と食感", "What does it taste and feel like?", "どんな味と食感ですか？", ["Which ingredient shapes the flavor most?", "What food could you compare the texture to?"]),
            ("The best moment", "いちばんおいしい時", "When and where is it best?", "いつ、どこで食べるのがいちばんですか？", ["Does the season change it?", "What kind of place should I avoid?"]),
            ("Who shares it", "一緒に食べる人", "Who do you usually eat it with?", "ふだん誰と一緒に食べますか？", ["What memory do you connect with it?", "Does your family eat it differently?"]),
            ("One warning", "一つの注意", "What should you warn a first-time visitor about?", "初めて食べる人に、何を注意しておきますか？", ["What mistake do visitors often make?", "What should they try before deciding they dislike it?"]),
            ("How much can change?", "どこまで変えられる？", "How much can you change the dish before it stops counting?", "どこまで変えたら、その料理ではなくなりますか？", ["Which part must stay the same?", "What change would you happily accept?"]),
        ],
    },
    4: {
        "slug": "a-table-manner-that-differs",
        "title": "A table manner that differs between countries",
        "ko": "나라마다 다른 식사 예절",
        "ja": "国によって違う食事のマナー",
        "goal": ("Let's compare one table habit and the meaning people give it.", "食卓での習慣を一つ比べ、その意味について話しましょう。"),
        "opening": ("Do you pick your bowl up when you eat?", "食べるとき、お椀を手に持ちますか？"),
        "article_title": ("The hidden rules at a table", "食卓にある見えないルール"),
        "article": [
            ("Table manners feel natural because people learn them long before they can explain them.", "食事のマナーは説明できるようになるずっと前から身につけるため、自然に感じられます。"),
            ("A small action can therefore carry very different meanings in two countries.", "そのため、小さな動作が二つの国でまったく違う意味を持つことがあります。"),
            ("Picking up a bowl may show good manners in one place and look unusual in another.", "お椀を持つことが、ある場所では礼儀正しく、別の場所では珍しく見えることがあります。"),
            ("The order of eating, sharing dishes, and starting a meal can also follow quiet rules.", "食べる順番、料理の分け方、食べ始める時にも、暗黙のルールがあります。"),
            ("Visitors often notice the rule only after someone reacts to them.", "旅行者は、誰かに反応されて初めてそのルールに気づくことがよくあります。"),
            ("Embarrassment makes the moment memorable, but it does not always explain the reason.", "恥ずかしさでその瞬間は記憶に残りますが、理由まで分かるとは限りません。"),
            ("Asking who taught the habit can reveal family, age, and regional differences.", "その習慣を誰に教わったか聞くと、家庭、世代、地域の違いが見えてきます。"),
            ("Some rules remain important while others are becoming flexible.", "今も大切なルールもあれば、柔軟になっているものもあります。"),
            ("Knowing the rule is useful, but understanding its purpose makes adaptation easier.", "ルールを知ることは役立ちますが、目的まで分かると合わせやすくなります。"),
            ("A respectful guest observes, asks, and avoids treating one table as a whole country.", "礼儀ある客は、よく見て、質問し、一つの食卓を国全体だと思わないようにします。"),
        ],
        "gloss": {6: ("Embarrassment", "embarrassment", "恥ずかしさ"), 9: ("adaptation", "adaptation", "適応")},
        "questions": [
            ("At your table", "あなたの食卓", "What other table habit is fixed in your home?", "あなたの家で決まっている食卓の習慣はほかに何ですか？", ["When do you notice someone doing it differently?", "Does the rule change for guests?"]),
            ("Who starts?", "誰が始める？", "Who usually starts eating first?", "ふつう誰が最初に食べ始めますか？", ["What happens if someone starts early?", "Is the rule different at a restaurant?"]),
            ("What feels rude?", "失礼に感じること", "What action at the table feels rude to you?", "食卓で何をされると失礼だと感じますか？", ["Why does that action bother people?", "Would you correct a visitor?"]),
            ("Across countries", "国をまたぐと", "What might be polite in my country but rude in yours?", "私の国では礼儀正しくても、あなたの国では失礼になることは何ですか？", ["How could a visitor discover that rule?", "Which misunderstanding would be hardest to repair?"]),
            ("Who taught you?", "誰に教わった？", "Who taught you your table manners?", "食事のマナーは誰に教わりましたか？", ["Which rule did they care about most?", "Have you kept all of their rules?"]),
            ("Still important?", "今も大切？", "Which table rules do people care less about now?", "今はあまり気にされなくなった食事のルールは何ですか？", ["Why has that rule weakened?", "Which rule should not disappear?"]),
        ],
    },
    5: {
        "slug": "a-place-you-would-show-a-visitor",
        "title": "A place you would show a visitor",
        "ko": "여행자에게 보여 주고 싶은 장소",
        "ja": "旅行者に案内したい場所",
        "goal": ("Let's plan one day somewhere meaningful, away from the famous sights.", "有名な観光地ではない、大切な場所での一日を考えましょう。"),
        "opening": ("If I visited for one day, where would you take me—not the famous place?", "私が一日だけ来たら、有名な場所以外のどこへ連れて行きますか？"),
        "article_title": ("The places a guidebook misses", "ガイドブックが見落とす場所"),
        "article": [
            ("Famous sights help visitors recognize a city, but ordinary places help them understand it.", "有名な観光地は街を知る助けになりますが、普通の場所は街を理解する助けになります。"),
            ("A neighborhood market, small park, or local café can show how people spend real time.", "近所の市場、小さな公園、地元のカフェは、人々の実際の過ごし方を見せてくれます。"),
            ("These places matter because someone has a personal reason to return to them.", "そうした場所が大切なのは、誰かが個人的な理由で何度も戻るからです。"),
            ("The best time of day may change the sounds, people, and atmosphere completely.", "いちばんよい時間帯によって、音、人、雰囲気がまったく変わることがあります。"),
            ("A visitor may miss the point unless the local person explains what to notice.", "地元の人が見るべき点を説明しなければ、旅行者は魅力に気づかないかもしれません。"),
            ("That explanation can reveal a memory, a routine, or a side of the city that is disappearing.", "その説明から、思い出、日課、消えつつある街の一面が見えることがあります。"),
            ("Showing a place also means deciding how much of it should stay private.", "場所を案内することは、どこまで秘密にしておくかを決めることでもあります。"),
            ("Too much attention can change the quiet character that made the place special.", "注目されすぎると、その場所を特別にした静かな個性が変わることがあります。"),
            ("A thoughtful host chooses a place that fits the visitor, not simply their own favorite.", "思いやりのある案内役は、自分の一番好きな場所ではなく、相手に合う場所を選びます。"),
            ("The result is a shared day rather than a list of sights.", "その結果、観光地のリストではなく、一緒に過ごした一日になります。"),
        ],
        "gloss": {4: ("atmosphere", "atmosphere", "雰囲気"), 9: ("thoughtful", "thoughtful", "思いやりのある")},
        "questions": [
            ("Your place", "あなたの場所", "Where would you take me for that one day?", "その一日、私をどこへ連れて行きますか？", ["What can I experience there that tourists usually miss?", "How far is it from where you live?"]),
            ("Why there?", "なぜそこ？", "Why is that place important to you?", "なぜその場所はあなたにとって大切ですか？", ["What memory do you connect with it?", "Would it matter as much without that memory?"]),
            ("How you found it", "見つけたきっかけ", "When did you first discover it?", "その場所を初めて知ったのはいつですか？", ["Who showed it to you?", "How has it changed since then?"]),
            ("Who goes with you?", "誰と行く？", "Who have you taken there before?", "これまで誰をそこへ連れて行きましたか？", ["Did they enjoy the same part you do?", "Who would not enjoy it?"]),
            ("What I might miss", "見落としそうなこと", "What would I not understand without your explanation?", "あなたの説明がなければ、私は何を理解できないと思いますか？", ["What should I pay attention to first?", "Is there a local rule I should know?"]),
            ("Turn the trip around", "旅を逆にする", "Where would you take me in my country if you could choose?", "選べるなら、私の国ではどこへ一緒に行きたいですか？", ["What do you hope to experience there?", "What would you want me to explain?"]),
        ],
    },
    6: {
        "slug": "a-word-that-doesnt-translate-neatly",
        "title": "A word that doesn't translate neatly",
        "ko": "깔끔하게 번역되지 않는 말",
        "ja": "ぴったり訳せない言葉",
        "goal": ("Let's explore a word whose meaning or feeling changes in translation.", "訳すと意味や感覚が変わる言葉について話しましょう。"),
        "opening": ("Have you learned any new English words recently?", "最近、新しい英単語を覚えましたか？"),
        "article_title": ("What gets lost between languages", "言語の間で失われるもの"),
        "article": [
            ("A dictionary can give an equivalent word without giving the same feeling.", "辞書は対応する言葉を示せても、同じ感覚までは伝えられないことがあります。"),
            ("Meaning also depends on who is speaking, their relationship, and the situation.", "意味は、話す人、相手との関係、状況にも左右されます。"),
            ("One Japanese word may therefore need a full English sentence in some contexts.", "そのため、日本語の一語が、場面によっては英語の一文を必要とすることがあります。"),
            ("The closest translation may be correct but sound warmer, colder, stronger, or more formal.", "いちばん近い訳でも、より温かく、冷たく、強く、または堅く聞こえることがあります。"),
            ("Speakers often solve the gap by explaining the situation around the word.", "話し手は、その言葉が使われる状況を説明して差を埋めることがよくあります。"),
            ("Examples show when the word is natural and when it would feel strange.", "例があると、その言葉が自然な時と、不自然に感じる時が分かります。"),
            ("Tone, timing, and shared knowledge can carry as much information as the word itself.", "口調、タイミング、共有している知識は、言葉そのものと同じくらい情報を伝えます。"),
            ("That is why a technically accurate subtitle can still feel wrong.", "そのため、技術的には正しい字幕でも、違和感があることがあります。"),
            ("Learning these gaps helps us notice assumptions built into our own language.", "こうした違いを学ぶと、自分の言語に含まれる前提にも気づけます。"),
            ("Translation is not only replacing words; it is choosing what the listener most needs to receive.", "翻訳は単語を置き換えるだけでなく、聞き手に最も必要なものを選ぶことです。"),
        ],
        "gloss": {1: ("equivalent", "equivalent", "対応するもの"), 8: ("technically", "technically", "厳密には")},
        "questions": [
            ("A new word", "新しい言葉", "Which new English word have you noticed recently?", "最近気になった新しい英単語は何ですか？", ["Where did you first hear or read it?", "Have you tried using it yourself?"]),
            ("What it really means", "本当の意味", "What does that word actually mean in context?", "その言葉は文脈の中で実際にどういう意味ですか？", ["What example makes the meaning clear?", "What common translation is misleading?"]),
            ("A Japanese example", "日本語の例", "Which Japanese word has no exact English match?", "英語にぴったり合う言葉がない日本語は何ですか？", ["What situation makes you want to use it?", "What English explanation comes closest?"]),
            ("Who you say it to", "誰に言う？", "Who can you naturally use that word with?", "その言葉は誰に自然に使えますか？", ["How would it change with a stranger?", "Would an older person use it differently?"]),
            ("Relationship and meaning", "関係と意味", "Why does the relationship change the meaning?", "なぜ相手との関係で意味が変わりますか？", ["What tone does the word carry?", "What could happen if someone used it in the wrong relationship?"]),
            ("Meaning or feeling?", "意味か感覚か", "Is a translation enough if the feeling is lost?", "感覚が失われても、訳として十分だと思いますか？", ["When does accuracy matter more than feeling?", "How would you preserve the feeling instead?"]),
        ],
    },
    8: {
        "slug": "how-you-spend-new-years-day",
        "title": "How you spend New Year's Day",
        "ko": "새해 첫날을 보내는 방법",
        "ja": "元日の過ごし方",
        "goal": ("Let's compare what New Year's Day really looks like in our lives.", "実際の元日の過ごし方を比べましょう。"),
        "opening": ("What do you actually do on New Year's Day?", "元日は実際に何をしますか？"),
        "article_title": ("Traditions that keep changing", "変わり続ける伝統"),
        "article": [
            ("New Year's traditions can look fixed even while families keep changing them.", "新年の伝統は、家庭が変え続けていても、決まったものに見えることがあります。"),
            ("Food, visits, television, and religious customs may all share the same day.", "料理、訪問、テレビ、宗教的な習慣が、同じ一日に重なることがあります。"),
            ("Two homes in the same town can follow very different routines.", "同じ町の二つの家庭でも、まったく違う過ごし方をすることがあります。"),
            ("Some activities are meaningful because people have repeated them since childhood.", "子どもの頃から繰り返してきたために、大切な意味を持つ行動もあります。"),
            ("Others continue mainly because relatives expect everyone to join.", "親族が全員の参加を期待するために続いているものもあります。"),
            ("Work schedules, travel, and smaller families have made many routines more flexible.", "仕事の予定、移動、家族の小規模化によって、多くの習慣が柔軟になりました。"),
            ("People may keep one symbolic part while dropping the time-consuming parts.", "時間のかかる部分をやめ、象徴的な一部だけ残す人もいます。"),
            ("Comparing childhood with the present reveals which traditions were chosen and which were inherited.", "子どもの頃と今を比べると、自分で選んだ伝統と受け継いだ伝統が見えてきます。"),
            ("A custom can survive by changing rather than by staying exactly the same.", "習慣は、まったく同じままでいるのではなく、変わることで残る場合があります。"),
            ("The most revealing question may be not what people do, but what they no longer do.", "いちばん多くを語る質問は、何をするかではなく、何をしなくなったかかもしれません。"),
        ],
        "gloss": {7: ("symbolic", "symbolic", "象徴的な"), 8: ("inherited", "inherit", "受け継ぐ")},
        "questions": [
            ("Your day", "あなたの一日", "Can you walk me through your New Year's Day?", "元日の一日を順番に教えてもらえますか？", ["What happens first after you wake up?", "Which part takes the most time?"]),
            ("What you eat", "食べるもの", "What do you usually eat that day?", "その日はふだん何を食べますか？", ["Who prepares it?", "Which dish would feel strange to skip?"]),
            ("Who you see", "会う人", "Who do you normally spend the day with?", "ふだん誰と元日を過ごしますか？", ["Does everyone stay for the whole day?", "Who do you contact even if you cannot meet?"]),
            ("Since childhood", "子どもの頃から", "What has changed since you were a child?", "子どもの頃から何が変わりましたか？", ["Why did that change happen?", "Which old part do you miss?"]),
            ("What you skip", "今はしないこと", "Which New Year's custom do you skip now?", "今はしなくなった新年の習慣は何ですか？", ["Who in your family still does it?", "Would you bring it back in the future?"]),
            ("My side", "私の国では", "What do you think happens on New Year's Day in my country?", "私の国では元日に何をすると思いますか？", ["Which part would you most like to compare?", "What might surprise you there?"]),
        ],
    },
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def page(page_id: str, title: str, title_ja: str, body: str) -> str:
    return f'''    <div class="section" data-page-id="{page_id}">
      <h2 class="section-title">{title} <span class="title-ja">({title_ja})</span></h2>
{body}
    </div>\n'''


def question_page(page_id: str, number: str, item, variant: str) -> str:
    title, title_ja, en, ja, followups = item
    lis = "".join(f"<li>{esc(q)}</li>" for q in followups)
    body = f'''      <p class="section-subtitle ask"><span class="q-n">{number}</span><span class="ko">{esc(en)}</span><span class="ja">{esc(ja)}</span></p>
      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span><ul class="tn-more">{lis}</ul></div></div>
      <div class="fb" data-fb="{variant}-{page_id}"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'''
    return page(page_id, esc(title), esc(title_ja), body)


def article_page(topic, variant: str) -> str:
    full_leads = (
        ("A useful starting point is this: ", False),
        ("Seen more broadly, ", True),
        ("One consequence is that ", True),
        ("In everyday practice, ", True),
        ("What is easy to overlook is that ", True),
        ("A further complication is that ", True),
        ("From another angle, ", True),
        ("The key nuance is that ", True),
        ("This matters because ", True),
        ("Taken together, the point is that ", True),
    )
    rows = []
    for index, (base_en, ja) in enumerate(topic["article"], start=1):
        en = base_en
        if variant == "full":
            lead, lower = full_leads[index - 1]
            en = lead + (base_en[:1].lower() + base_en[1:] if lower else base_en)
        gloss = topic["gloss"].get(index) if variant == "accessible" else None
        if variant == "full" and index == 6:
            gloss = ("complication", "complication", "複雑にする要素")
        elif variant == "full" and index == 8:
            gloss = ("nuance", "nuance", "微妙な違い")
        words = ""
        if gloss:
            surface, head, meaning = gloss
            en = en.replace(surface, f'<span class="s-key">{esc(surface)}</span>', 1)
            words = f'<span class="s-words"><span class="s-w"><b>{esc(head)}</b>{esc(meaning)}</span></span>'
        rows.append(
            f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}"><span class="s-line"><span class="s-ko">{en}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{esc(ja)}</span>{words}</span></div>'
        )
    title, title_ja = topic["article_title"]
    body = '''      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>
      <div class="tutor-note">Answer the learner's questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>
      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">
'''+"\n".join(rows)+'''\n      </div>'''
    return page("article", esc(title), esc(title_ja), body)


def extract_page(source: str, page_id: str) -> str:
    start = source.index(f'<div class="section" data-page-id="{page_id}">')
    next_section = source.find('\n    <div ', start + 1)
    end = source.index('\n  </div>', start) if next_section < 0 else next_section
    return "    " + source[start:end].strip() + "\n"


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
        version="2026-08-19",
    )
    head = head.replace('content="todo"', 'content="reviewed"')
    if variant == "accessible":
        new_vocab = "; ".join(
            f"{headword}|{meaning}" for _surface, headword, meaning in topic["gloss"].values()
        )
        receptive_vocab = ""
    else:
        new_vocab = ""
        receptive_vocab = "complication|複雑にする要素; nuance|微妙な違い"
    head = re.sub(r'(<meta name="podo:vocabulary:new" content=")[^"]*(")', rf'\g<1>{new_vocab}\2', head, count=1)
    head = re.sub(r'(<meta name="podo:vocabulary:assumed" content=")[^"]*(")', r'\g<1>Japan|日本; country|国; culture|文化; experience|経験\2', head, count=1)
    head = re.sub(r'(<meta name="podo:vocabulary:receptive" content=")[^"]*(")', rf'\g<1>{receptive_vocab}\2', head, count=1)
    goal_en, goal_ja = topic["goal"]
    opening_en, opening_ja = topic["opening"]
    q = topic["questions"]
    pages = [
        f'''    <div class="transition-page" data-page-id="lesson-goal" data-act="Between two countries">
      <span class="transition-kicker">BETWEEN TWO COUNTRIES</span>
      <h2 class="transition-title">{esc(topic["title"])} <span class="title-ja">({esc(topic["ja"])})</span></h2>
      <p class="section-subtitle"><span class="ko">{esc(goal_en)}</span><span class="ja">{esc(goal_ja)}</span></p>
      <div class="known lines"><div class="known-row"><span class="k">Give one concrete example</span><span class="j">具体的な例を一つ出す</span></div><div class="known-row"><span class="k">Explain why it matters</span><span class="j">なぜ大切か説明する</span></div><div class="known-row"><span class="k">Compare both countries</span><span class="j">二つの国を比べる</span></div></div>
    </div>\n''',
        article_page(topic, variant),
        extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="transition-copy">全部答えなくても大丈夫です。一つの答えをゆっくり広げましょう。</p></div>\n''',
        question_page("warm-1", "WARM-UP 1", ("Start here", "ここから", opening_en, opening_ja, [q[0][4][0], q[0][4][1]]), variant),
        question_page("warm-2", "WARM-UP 2", ("One example", "一つの例", q[0][2], q[0][3], q[0][4]), variant),
    ]
    pages.extend(question_page(f"q{i}", f"QUESTION {i}", item, variant) for i, item in enumerate(q, start=1))
    pages.append(extract_page(canonical, "feedback"))
    return new_lesson.redepth(head + "\n".join(pages) + foot, TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh", action="store_true",
        help="regenerate only the FT topic paths owned by this narrow generator",
    )
    args = parser.parse_args()
    written = 0
    for topic_no in TOPICS:
        for variant in ("accessible", "full"):
            slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
            out = TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"
            if out.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)}")
            written += 1
    print(f"{written} Freetalking decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
