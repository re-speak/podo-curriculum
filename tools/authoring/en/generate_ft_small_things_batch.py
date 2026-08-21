#!/usr/bin/env python3
"""Generate the explicit FT 34-46 Small Things accessible/full pairs.

This narrow source owns only the 26 matched decks in talk-small-things. Each
article row stores independently reviewed accessible/full English and Japanese,
and each prompt owns a natural, answerable continuation rather than a defensive
branch or generic fallback.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ft_me_lately_batch as base
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/3-freetalking"
COURSE = "talk-small-things"
CANONICAL = {
    variant: TRACK / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html"
    for variant in ("accessible", "full")
}
prompt = base.prompt
esc = base.esc


def topic(*, slug, title, ko, ja, goal, outcomes, article_title, articles, prompts):
    return {
        "slug": slug,
        "title": title,
        "ko": ko,
        "ja": ja,
        "goal": goal,
        "outcomes": outcomes,
        "article_title": article_title,
        "articles": articles,
        "prompts": prompts,
    }


# Article rows are (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
    34: topic(
        slug="a-tiny-thing-that-always-annoys-you",
        title="A tiny thing that always annoys you",
        ko="늘 신경 쓰이는 사소한 것",
        ja="いつも気になるささいなこと",
        goal=("Let's talk about why tiny things can become surprisingly annoying.", "ささいなことが意外なほど気になる理由について話しましょう。"),
        outcomes=(("Name the tiny annoyance", "ささいな不満を一つ挙げる"), ("Describe the last time", "直近の場面を説明する"), ("Turn the complaint around", "自分の側にも目を向ける")),
        article_title=("Why tiny things get to us", "ささいなことが気になる理由"),
        articles=[
            ("A tiny irritation can become more annoying when it happens again and again.", "A minor irritation can become disproportionately annoying through repetition.", "ささいないら立ちでも、何度も繰り返されると、いっそう気になります。", "小さな不快感でも、繰り返されることで実際以上に気になるものになります。"),
            ("We notice it quickly because we already expect it to happen.", "Anticipating the irritation makes us notice it almost before it happens.", "また起きると思っているので、すぐに気づきます。", "また起きると身構えているため、実際に起きる前から気づくようになります。"),
            ("The problem may feel bigger when fixing it would be easy.", "An irritation often feels worse when the solution appears obvious and effortless.", "簡単に直せそうなことほど、大きな問題のように感じることがあります。", "解決策が明らかで手間もかからないように見えると、不快感はさらに強くなりがちです。"),
            ("Shared spaces create many small conflicts about noise, order, and timing.", "Shared spaces create endless points of friction over noise, order, timing, and attention.", "共有する場所では、音や片づけ、タイミングをめぐる小さな衝突が多く生まれます。", "共有空間では、音、秩序、タイミング、周囲への配慮をめぐって、細かな摩擦が絶えません。"),
            ("Other people may honestly not notice the thing that bothers us.", "Other people may be genuinely unaware of the detail that feels impossible for us to ignore.", "自分が気になることに、ほかの人は本当に気づいていない場合があります。", "自分には無視できない細部でも、ほかの人は本当に意識していないことがあります。"),
            ("Saying something can solve the problem, but it can also sound too serious.", "Mentioning it may solve the problem, yet the complaint can sound out of proportion to its cause.", "伝えれば解決するかもしれませんが、大げさに聞こえることもあります。", "口にすれば解決する一方で、原因の小ささに比べて不満が大げさに聞こえることもあります。"),
            ("A joke can make a small complaint easier to hear.", "Humour can make a petty complaint easier to hear without hiding the real request.", "冗談を交えると、ささいな不満も受け止めてもらいやすくなります。", "ユーモアを使えば、本当のお願いを隠さずに、細かな不満を伝えやすくなります。"),
            ("Our own habits probably annoy other people too.", "The uncomfortable balance is that our own unnoticed habits probably irritate someone else.", "自分の習慣も、きっとほかの人を困らせています。", "厄介なのは、自分では気づかない習慣も、きっと誰かをいら立たせているということです。"),
            ("Stress and tiredness can make a tiny annoyance feel much worse.", "Stress and fatigue reduce our patience and magnify otherwise harmless annoyances.", "ストレスや疲れがあると、ささいなことがずっと気になりやすくなります。", "ストレスや疲労で我慢する余裕がなくなると、普段なら害のないことまで大きく感じられます。"),
            ("A useful question is whether the problem needs action or just patience.", "The useful question is whether the irritation calls for a request, a change in routine, or simple tolerance.", "大切なのは、行動が必要なのか、少し我慢すればよいのかを考えることです。", "その不快感に必要なのが、お願いなのか、習慣の変更なのか、それとも受け流すことなのかを見極めるのが大切です。"),
        ],
        prompts=[
            prompt("One tiny annoyance", "ささいな不満", "What's one tiny thing that can become surprisingly annoying?", "意外なほど気になることがある、ささいなことは何ですか？", ["When does it stand out most?", "Why can such a small detail get under someone's skin?"]),
            prompt("Where it happens", "起きる場所", "Where does this kind of annoyance usually happen?", "そのようなささいな不満は、たいていどこで起きますか？", ["Who is most likely to notice it?", "What makes that setting matter?"]),
            prompt("Hard to ignore", "無視しにくい点", "Which part is hardest to ignore?", "どの部分がいちばん無視しにくいですか？", ["Is repetition the real problem, or something else?", "How could two people react differently?"]),
            prompt("How to mention it", "伝え方", "What's the best way to mention a tiny annoyance without making it sound huge?", "ささいな不満を大げさに聞こえないように伝えるには、どのような言い方がよいですか？", ["Would humour help or make the request less clear?", "What exact request could solve the problem?"], full="How can someone raise a minor irritation without making it sound disproportionate?"),
            prompt("Worth speaking up", "伝える価値", "When is a small complaint worth speaking up about?", "ささいな不満でも、どのようなときは伝える価値がありますか？", ["What could happen if nobody mentions it?", "Where would you draw the line?"]),
            prompt("Our own habits", "自分の習慣", "Which everyday habit is hardest for people to notice in themselves?", "日常の習慣のうち、自分ではいちばん気づきにくいものは何ですか？", ["How could someone point it out kindly?", "What might make the person defensive?"]),
            prompt("Stress and patience", "ストレスと我慢", "Why do small annoyances grow when people are stressed or tired?", "ストレスや疲れがあると、なぜささいなことがもっと気になるのでしょうか？", ["Which annoyances become easier to ignore after a rest?", "How can someone reset before reacting?"]),
            prompt("Fix or ignore", "直すか受け流すか", "Which tiny annoyance deserves action, and which is better ignored?", "どのささいな不満には対応し、どの不満は受け流すほうがよいですか？", ["What is the smallest useful fix?", "What would patience look like here?"], full="Which minor irritation genuinely deserves action, and which calls for tolerance?"),
        ],
    ),
    35: topic(
        slug="a-useless-fact-about-you",
        title="A useless fact about you",
        ko="나에 관한 쓸모없는 사실",
        ja="自分についての役に立たない事実",
        goal=("Let's talk about facts that are interesting even when they aren't useful.", "役に立たなくても面白い事実について話しましょう。"),
        outcomes=(("Share one harmless fact", "気軽な事実を一つ話す"), ("Explain how it became true", "そうなった経緯を説明する"), ("Choose a surprising fact", "意外な事実を選ぶ")),
        article_title=("The value of useless facts", "役に立たない事実の価値"),
        articles=[
            ("Personal trivia does not help with work or daily tasks.", "A piece of personal trivia has no obvious utility in work or daily life.", "役に立たない事実は、仕事や日常の用事には役立ちません。", "役に立たない個人的な事実には、仕事や日常生活での明らかな実用性がありません。"),
            ("It can still make a conversation more personal and memorable.", "Its lack of utility can make a conversation feel more personal and memorable.", "それでも、会話を個人的で印象に残るものにできます。", "実用性がないからこそ、会話がより個人的で記憶に残るものになります。"),
            ("Small facts often reveal habits, tastes, or old interests.", "Trivial details often reveal habits, tastes, and abandoned interests more clearly than a formal introduction.", "小さな事実から、習慣や好み、昔の興味が見えることがあります。", "ささいな細部は、かしこまった自己紹介よりも、習慣や好み、以前の興味をはっきり表すことがあります。"),
            ("Some personal facts are about skills that were useful once but no longer matter.", "Some personal trivia describes practical skills whose original usefulness has faded.", "昔は役に立ったものの、今は必要なくなった技能についての事実もあります。", "個人的な雑学の中には、もともとの実用性が薄れた技能についてのものもあります。"),
            ("Others come from a coincidence we happened to remember.", "Others survive only because a coincidence was strange enough to remember.", "たまたま覚えていた偶然から生まれるものもあります。", "奇妙で記憶に残る偶然だったからこそ残っているものもあります。"),
            ("The best useless facts are harmless and easy to explain.", "A good useless fact is harmless, concise, and revealing without becoming too private.", "よい役に立たない事実は、害がなく、簡単に説明できます。", "よい役に立たない事実は、害がなく簡潔で、私的になりすぎずに人柄を表します。"),
            ("They give other people an easy way to ask a follow-up question.", "They provide an easy conversational hook for a genuine follow-up question.", "そのような事実があると、相手も続けて質問しやすくなります。", "そのような事実は、自然な追加質問につながる会話のきっかけになります。"),
            ("A fact can feel useless to us but interesting to someone else.", "Usefulness depends on context; what feels pointless to us may fascinate someone else.", "自分には役に立たなくても、ほかの人には面白い場合があります。", "役立つかどうかは状況次第で、自分には無意味でも、ほかの人には魅力的かもしれません。"),
            ("Useful facts tell people what we can do; useless ones show another side.", "Useful facts advertise competence, while useless ones often reveal character.", "役に立つ事実はできることを伝え、役に立たない事実は別の一面を見せます。", "役に立つ事実が能力を示す一方で、役に立たない事実は人柄を表すことがよくあります。"),
            ("One odd detail can make an ordinary introduction feel real.", "One well-chosen oddity can make an otherwise predictable introduction feel genuinely human.", "少し変わった一つの細部で、普通の自己紹介が自然に感じられます。", "一つのうまく選んだ変わった事実で、ありきたりな自己紹介にも人間味が生まれます。"),
        ],
        prompts=[
            prompt("One useless fact", "役に立たない事実", "What's one fact about you that's interesting but not useful?", "自分について、面白いけれど役には立たない事実は何ですか？", ["How did you discover it?", "What question might it make someone ask?"]),
            prompt("Since when", "いつから？", "How long has that fact been true?", "その事実は、いつから当てはまりますか？", ["Did it happen by accident or by choice?", "What was different before?"]),
            prompt("Who would be surprised", "驚きそうな人", "Who would be most surprised by that fact?", "その事実を知って、いちばん驚きそうな人は誰ですか？", ["What would they guess instead?", "Why has the fact never come up?"]),
            prompt("Why useless", "役に立たない理由", "What makes the fact useless?", "その事実は、なぜ役に立たないのですか？", ["Could it help in one unusual situation?", "Why is it worth remembering anyway?"]),
            prompt("How it became true", "そうなった経緯", "How might an unusual fact about you come about?", "あなたについての少し変わった事実は、どんな経緯で生まれそうですか？", ["Could one turning point create it?", "Which part of your story would explain it best?"]),
            prompt("A useful fact", "役に立つ事実", "What's one genuinely useful fact about you?", "自分について、本当に役に立つ事実は何ですか？", ["When does it become useful?", "Who benefits from knowing it?"]),
            prompt("A conversation starter", "会話のきっかけ", "Which useless facts make the best conversation starters?", "どのような役に立たない事実が、会話のよいきっかけになりますか？", ["What makes one easy to ask about?", "When would a fact feel too personal?"]),
            prompt("A playful introduction", "楽しい自己紹介", "How would you use an unusual fact about yourself in a playful introduction?", "自分についての少し変わった事実を、楽しい自己紹介でどう使いますか？", ["What exact sentence would you say?", "What follow-up would keep the conversation going?"]),
        ],
    ),
    36: topic(
        slug="a-habit-you-only-have-at-home",
        title="A habit you only have at home",
        ko="집에서만 하는 습관",
        ja="家でだけする習慣",
        goal=("Let's talk about the habits people keep for home.", "家でだけする習慣について話しましょう。"),
        outcomes=(("Describe a private habit", "人前ではしない習慣を説明する"), ("Trace where it came from", "その習慣の始まりをたどる"), ("Decide what stays private", "どこまで人に見せるか考える")),
        article_title=("Why home changes our behaviour", "家で行動が変わる理由"),
        articles=[
            ("At home, we do not have to manage every small impression.", "At home, we can relax the constant work of managing other people's impressions.", "家では、細かな印象をいつも気にする必要がありません。", "家では、他人からどう見られるかを絶えず管理する負担から解放されます。"),
            ("That freedom creates habits we would never show in public.", "That privacy produces habits we would edit or suppress in public.", "その気楽さから、人前では見せない習慣が生まれます。", "その私的な空間によって、人前なら直したり抑えたりする習慣が生まれます。"),
            ("Some habits are comfortable, while others are simply silly.", "Some private habits provide comfort; others survive because they are harmless and amusing.", "落ち着く習慣もあれば、ただおかしいだけの習慣もあります。", "安心感を与える私的な習慣もあれば、害がなく面白いから残っているものもあります。"),
            ("We may not notice a home habit until another person sees it.", "A home habit can remain invisible to us until someone else witnesses it.", "家での習慣は、誰かに見られるまで自分でも気づかないことがあります。", "家での習慣は、ほかの人に目撃されるまで、自分には見えないままのことがあります。"),
            ("People who live together often develop their own small rules.", "People who share a home gradually create private routines and unspoken rules.", "一緒に暮らす人は、自分たちだけの小さな決まりを作ることがあります。", "同じ家で暮らす人たちは、少しずつ独自の習慣や暗黙のルールを作ります。"),
            ("A habit can feel normal until we compare homes.", "A routine feels universal until another household reveals a completely different norm.", "ほかの家と比べるまでは、自分の習慣が普通に感じられます。", "別の家庭でまったく違う基準を知るまでは、自分の習慣を誰にでも共通だと思いがちです。"),
            ("Privacy also lets us practise things before showing anyone.", "Privacy gives us room to rehearse, experiment, and fail before anyone is watching.", "人に見せる前に、家で練習できることもあります。", "私的な空間なら、誰かに見られる前に練習し、試し、失敗できます。"),
            ("Some habits disappear when our home or routine changes.", "Private habits often disappear when living arrangements or daily routines change.", "住む場所や日課が変わると、なくなる習慣もあります。", "住まい方や日々の流れが変わると、私的な習慣も消えることがよくあります。"),
            ("Others stay because they are part of how we rest.", "Other habits persist because they have become part of our personal recovery ritual.", "休むための方法になっていて、続く習慣もあります。", "一方で、自分なりの回復の儀式になっているため、続く習慣もあります。"),
            ("The question is not whether the habit is strange, but whether it causes harm.", "The useful boundary is not normal versus strange, but harmless privacy versus behaviour that affects others.", "大切なのは変かどうかではなく、害があるかどうかです。", "大切な境界は、普通か変かではなく、害のない私的な習慣か、他人に影響する行動かという点です。"),
        ],
        prompts=[
            prompt("A home-only habit", "家だけの習慣", "What's something people often do at home but hide in public?", "家ではよくするけれど、人前では見せないことは何ですか？", ["Why does home make it feel normal?", "Which example seems most harmless?"]),
            prompt("One example", "一つの例", "Choose one home-only habit and describe a typical moment.", "家でだけする習慣を一つ選び、よくある場面を説明してください。", ["What would another person notice first?", "Why does the habit fit at home?"]),
            prompt("How it begins", "始まり方", "How can a home-only habit begin?", "家でだけする習慣は、どのように始まるのでしょうか？", ["What need might it meet?", "What could make it last for years?"]),
            prompt("Someone sees it", "見られたとき", "How might someone react if they saw the habit?", "その習慣を見た人は、どのように反応しそうですか？", ["What could make the reaction kind instead of judgmental?", "What would be worth explaining?"]),
            prompt("Shared routines", "一緒に暮らす人の習慣", "Why do people living together develop unusual routines?", "一緒に暮らす人たちは、なぜ独特の習慣を作るのでしょうか？", ["What problem might a routine solve?", "How can it become invisible to the people doing it?"]),
            prompt("A household surprise", "家庭の意外な習慣", "What's a household habit that could seem unusual somewhere else?", "別の家庭では変わって見えそうな、家の習慣は何ですか？", ["What context makes it understandable?", "What might surprise a visitor?"]),
            prompt("A changing routine", "変わる習慣", "Which home-only habit could disappear after a change in routine?", "生活の流れが変わると、どのような家だけの習慣がなくなりそうですか？", ["What change could end it?", "Why might another habit survive?"]),
            prompt("Keep it private", "私的なままにする", "When is it reasonable to keep a harmless private habit to yourself?", "害のない私的な習慣を人に見せないほうがよいのは、どのようなときですか？", ["What makes privacy reasonable?", "When does a private habit become someone else's concern?"]),
        ],
    ),
    37: topic(
        slug="what-you-do-on-a-rainy-day",
        title="What you do on a rainy day",
        ko="비 오는 날 하는 일",
        ja="雨の日にすること",
        goal=("Let's build a rainy day from the first drop to the perfect ending.", "雨の降り始めから理想の終わりまで、雨の日を組み立てて話しましょう。"),
        outcomes=(("Describe a rainy-day routine", "雨の日の過ごし方を説明する"), ("Recall one rain memory", "雨の思い出を一つ話す"), ("Design the perfect day", "理想の雨の日を考える")),
        article_title=("What rain changes", "雨が変えるもの"),
        articles=[
            ("Rain changes the speed and shape of an ordinary day.", "Rain quietly changes the pace, route, and atmosphere of an ordinary day.", "雨は、普通の一日の速さや形を変えます。", "雨は、普通の一日のペースや道順、雰囲気を静かに変えます。"),
            ("Plans outside may shrink, move indoors, or disappear.", "Outdoor plans may be shortened, moved indoors, postponed, or abandoned altogether.", "外の予定は、短くなったり、室内に移ったり、なくなったりします。", "屋外の予定は短縮されたり、室内へ移されたり、延期されたり、完全に中止されたりします。"),
            ("An empty day can make the sound of rain feel relaxing.", "With no urgent plans, the sound of rain can create a rare sense of permission to slow down.", "急ぐ予定がない日は、雨の音が落ち着いて感じられます。", "急ぐ予定がなければ、雨音によって、ゆっくりしてよいという珍しい安心感が生まれます。"),
            ("The same weather feels very different when we have to travel.", "The same rain becomes far less romantic when we have to commute, carry things, or arrive on time.", "移動しなければならないと、同じ天気でもまったく違って感じます。", "通勤したり、荷物を運んだり、時間どおりに着く必要があると、同じ雨でもずっと現実的な負担になります。"),
            ("Warm food and dry clothes become more comforting on a wet day.", "Warm food, dry clothes, and a sheltered room gain extra emotional value on a wet day.", "雨の日は、温かい食べ物や乾いた服がいつも以上に心地よく感じられます。", "雨の日には、温かい食べ物、乾いた服、雨をしのげる部屋に、いつも以上の安心感が生まれます。"),
            ("Rain can give us an excuse to return to quiet hobbies.", "Rain can provide a socially acceptable excuse to return to neglected indoor hobbies.", "雨は、静かな趣味に戻るきっかけになります。", "雨は、しばらく離れていた室内の趣味に戻る、自然な言い訳を与えてくれます。"),
            ("It can also make a small delay feel much more stressful.", "It can also multiply the stress of a delay by making every part of the journey less predictable.", "雨は、少しの遅れをずっと大きなストレスにすることもあります。", "一方で、移動のあらゆる部分が予測しにくくなり、少しの遅れのストレスを増幅させることもあります。"),
            ("A downpour often stays in our memory because of one clear sound, smell, or place.", "A downpour often remains memorable because of one vivid sound, smell, route, or place where we sheltered.", "土砂降りは、はっきりした音や匂い、場所とともに記憶に残ることがよくあります。", "土砂降りは、鮮明な音や匂い、通った道、雨宿りした場所とともに記憶に残ることがよくあります。"),
            ("A rainy day feels ideal when we are comfortable and nothing urgent needs attention.", "The ideal rainy day depends on comfort, safety, and the absence of an urgent obligation.", "心地よく過ごせて、急いで対応することがなければ、雨の日も理想的に感じられます。", "理想の雨の日には、心地よさと安全、そして急いで果たす義務がないことが欠かせません。"),
            ("Weather does not decide the whole day, but it changes what feels possible.", "Weather does not determine the whole day, but it reshapes which choices feel easy, difficult, or inviting.", "天気だけで一日が決まるわけではありませんが、できそうなことは変わります。", "天気が一日すべてを決めるわけではありませんが、どの選択が楽か、難しいか、魅力的かを変えます。"),
        ],
        prompts=[
            prompt("No plans, just rain", "予定のない雨の日", "It's raining and you have no plans. What happens?", "雨が降っていて、予定はありません。どう過ごしますか？", ["What do you do first?", "What would make you leave home anyway?"]),
            prompt("The atmosphere", "雨の日の雰囲気", "What sound, smell, or view would set the mood?", "どのような音や匂い、景色が、その日の雰囲気を作りますか？", ["Which detail feels most relaxing?", "Which one could become annoying?"]),
            prompt("How rain feels", "雨への気持ち", "What do you enjoy—or dislike—about rainy days?", "雨の日のどのようなところが好き、または苦手ですか？", ["How does the feeling change when you have to travel?", "Which kind of rain affects your mood most?"]),
            prompt("Rainy-day food", "雨の日の食べ物", "What's the best food for a rainy day?", "雨の日にいちばん合う食べ物は何ですか？", ["What makes it fit the weather?", "Would you cook it or get it elsewhere?"]),
            prompt("What gets cancelled", "中止になること", "What kind of plan would you cancel because of rain?", "雨なら、どのような予定を中止しますか？", ["What amount of rain would change your decision?", "Could the plan move indoors instead?"]),
            prompt("A difficult situation", "大変な雨の場面", "Which rainy situation would be hardest to deal with?", "雨の日のどのような状況が、いちばん大変そうですか？", ["What would make it manageable?", "Which detail would stay in your memory?"], full="Which situation involving rain would be most difficult to manage?"),
            prompt("A better day", "よくなる一日", "How can rain improve an ordinary day?", "雨は、普通の一日をどのようによくすることがありますか？", ["Which plan might become better indoors?", "Who might enjoy the change most?"]),
            prompt("The perfect rainy day", "理想の雨の日", "What would your perfect rainy day look like?", "理想の雨の日は、どのような一日ですか？", ["How much company would fit the day?", "What one thing would ruin it?"], full="What would your ideal rainy day look like?"),
        ],
    ),
    38: topic(
        slug="what-helps-when-youre-exhausted",
        title="What helps when you're exhausted",
        ko="완전히 지쳤을 때 도움이 되는 것",
        ja="くたくたのときに助けになるもの",
        goal=("Let's talk about what actually helps when your energy is gone.", "気力がなくなったとき、本当に助けになることについて話しましょう。"),
        outcomes=(("Name what helps", "助けになるものを挙げる"), ("Separate help from habit", "本当に効くものを見分ける"), ("Offer realistic advice", "現実的な助言をする")),
        article_title=("Recovery is not one thing", "回復の形は一つではない"),
        articles=[
            ("Being exhausted can mean needing sleep, quiet, food, or emotional space.", "Exhaustion can signal a need for sleep, silence, nutrition, distance, or emotional support.", "くたくたなときに必要なのは、睡眠、静けさ、食事、心の余裕などさまざまです。", "疲れ切っている状態は、睡眠、静けさ、栄養、距離、感情的な支えが必要だという合図かもしれません。"),
            ("The thing that feels easiest is not always the thing that restores us.", "The easiest response in the moment is not necessarily the one that restores our energy.", "その場でいちばん楽なことが、本当に回復させてくれるとは限りません。", "その瞬間にいちばん簡単な対処が、必ずしもエネルギーを回復させるものとは限りません。"),
            ("Scrolling can feel like rest while keeping the mind busy.", "Passive scrolling can imitate rest while continuing to occupy an overstimulated mind.", "画面を眺めることは休みに感じても、頭は動き続けています。", "受け身で画面を見続けることは休息に似ていますが、刺激を受けすぎた頭を占有し続けます。"),
            ("A short walk can help one person and feel impossible to another.", "A brief walk may regulate one person's energy while feeling completely unrealistic to another.", "短い散歩が助けになる人もいれば、とても無理に感じる人もいます。", "短い散歩で調子が整う人もいれば、まったく現実的でないと感じる人もいます。"),
            ("Practical help can matter more than encouraging words.", "When capacity is low, practical help may matter more than well-meant encouragement.", "余裕がないときは、励ましの言葉より具体的な助けが大切なことがあります。", "対応する力が残っていないときは、善意の励ましより実際的な助けのほうが重要な場合があります。"),
            ("People who know us well may notice tiredness before we do.", "People who know our normal behaviour may recognize exhaustion before we name it ourselves.", "自分をよく知る人は、自分より先に疲れに気づくことがあります。", "普段の自分を知る人は、自分が言葉にする前に疲れ切っていることに気づく場合があります。"),
            ("Trying to be productive can make recovery take longer.", "Treating recovery as another productivity task can delay the recovery itself.", "回復中まで生産的でいようとすると、回復に時間がかかることがあります。", "回復まで生産性の課題として扱うと、かえって回復そのものが遅れることがあります。"),
            ("A method that worked once may not fit a different kind of tiredness.", "A strategy that worked once may fail when the source or depth of exhaustion changes.", "一度効いた方法でも、別の種類の疲れには合わないことがあります。", "一度うまくいった方法でも、疲れの原因や深さが変われば効かないことがあります。"),
            ("Good advice begins by asking what the tired person can manage.", "Useful support begins by asking what the exhausted person has the capacity to do.", "よい助言は、疲れている人に何ができそうかを聞くことから始まります。", "役立つ支えは、疲れ切った人に今できる余力がどのくらいあるかを尋ねることから始まります。"),
            ("Sometimes the honest answer is that rest alone is not enough.", "Sometimes persistent exhaustion is information that ordinary rest is no longer enough.", "正直に言えば、休むだけでは足りない場合もあります。", "疲れが長く続くこと自体が、普通の休息だけでは足りないという情報になる場合もあります。"),
        ],
        prompts=[
            prompt("What actually helps", "本当に助けになるもの", "When you feel completely drained, what tends to help most?", "すっかり気力を使い果たしたとき、何がいちばん助けになりやすいですか？", ["How quickly can you tell it's helping?", "What kind of exhaustion needs something different?"], full="When you're completely drained, what tends to restore your energy most effectively?"),
            prompt("What you need first", "最初に必要なもの", "What do you usually need first: rest, food, quiet, or company?", "普段、最初に必要なのは休息、食事、静けさ、それとも人と過ごすことですか？", ["What does that need change first?", "When might a different choice work better?"]),
            prompt("Signs of recovery", "回復のサイン", "How can you tell when a recovery habit is working?", "回復のための習慣が効いていると、どう分かりますか？", ["Which change appears first in your body or mood?", "How long does the effect need to last?"]),
            prompt("Welcome help", "うれしい助け", "What kind of help feels welcome when someone is exhausted?", "誰かが疲れ切っているとき、どのような助けならうれしく感じますか？", ["What kind of help can feel like more work?", "How should someone offer it?"]),
            prompt("What makes it worse", "悪化させるもの", "What makes exhaustion worse for you?", "何があると、疲れがもっとひどくなりますか？", ["Which part can you control?", "What do other people often misunderstand about it?"]),
            prompt("What uses your energy", "気力を使うもの", "What usually uses up your energy fastest?", "普段、何をするといちばん早く気力を使い切りますか？", ["What early sign appears?", "What helps you preserve some energy?"]),
            prompt("Help or distraction", "回復？気晴らし？", "How do you tell real recovery from a distraction?", "本当の回復と、ただの気晴らしをどう見分けますか？", ["How do you feel afterward?", "Can the same activity be either one?"]),
            prompt("Advice that fits", "合う助言", "What would you tell someone who felt completely exhausted?", "完全に疲れ切っている人に、何と伝えますか？", ["What would you ask before giving advice?", "Which common suggestion would you avoid?"], full="What advice would you offer someone who felt completely exhausted?"),
        ],
    ),
    39: topic(
        slug="what-you-really-do-when-youre-stressed",
        title="What you really do when you're stressed",
        ko="스트레스를 받을 때 실제로 하는 일",
        ja="ストレスがあるとき実際にすること",
        goal=("Let's compare what you really do with what you wish you did.", "ストレスがあるとき実際にすることと、理想の対処を比べましょう。"),
        outcomes=(("Describe the real reaction", "実際の反応を説明する"), ("Judge whether it helps", "役立つか考える"), ("Choose one realistic change", "現実的な変化を一つ選ぶ")),
        article_title=("Our real stress habits", "本当のストレス習慣"),
        articles=[
            ("Advice about stress is often easier to give than to follow.", "Advice about stress is usually much easier to offer than to apply under pressure.", "ストレスへの助言は、実行するより人に言うほうが簡単です。", "ストレスへの助言は、重圧の中で実行するよりも、人に伝えるほうがはるかに簡単です。"),
            ("Under pressure, we return to habits that require little thought.", "Under pressure, we default to familiar behaviours that demand almost no decision-making.", "プレッシャーがあると、あまり考えなくてよい習慣に戻ります。", "重圧がかかると、判断をほとんど必要としない慣れた行動に頼りがちです。"),
            ("A coping response can calm us briefly but create another problem later.", "A coping response may provide immediate relief while quietly creating a later cost.", "ストレスへの対処は、少し落ち着かせても、あとで別の問題を作ることがあります。", "ストレスへの対処は、すぐ楽にしてくれる一方で、後の負担をひそかに生むことがあります。"),
            ("We may avoid a task, eat, clean, complain, or become very quiet.", "We may procrastinate, snack, clean obsessively, vent, withdraw, or overwork.", "仕事を避けたり、食べたり、掃除したり、不満を言ったり、黙ったりします。", "先延ばしにしたり、間食したり、過度に掃除したり、不満を吐き出したり、引きこもったり、働きすぎたりします。"),
            ("The same action can help in one situation and hurt in another.", "The same behaviour can regulate stress in one context and deepen avoidance in another.", "同じ行動でも、ある場面では助けになり、別の場面では悪化させます。", "同じ行動でも、ある状況ではストレスを整え、別の状況では回避を深めることがあります。"),
            ("People sometimes describe the healthy habit they wish they had.", "We sometimes report the healthy response we admire rather than the behaviour we actually repeat.", "人は、実際の習慣ではなく、できたらよいと思う健康的な方法を話すことがあります。", "実際に繰り返す行動ではなく、自分が理想とする健康的な反応を話してしまうことがあります。"),
            ("Honesty makes it easier to see the real pattern.", "Naming the unflattering truth makes the actual pattern visible enough to change.", "正直に話すと、本当のパターンが見えやすくなります。", "格好のよくない事実を言葉にすると、本当のパターンが変えられるほどはっきり見えてきます。"),
            ("A small replacement is often more realistic than a perfect routine.", "A modest substitute is usually more sustainable than an idealized stress-management routine.", "完璧な習慣より、小さな代わりの行動のほうが現実的です。", "理想化されたストレス管理の習慣より、控えめな代替行動のほうが続けやすいものです。"),
            ("Old stress habits can return during a difficult period.", "Even retired coping habits can reappear when pressure becomes unusually intense.", "大変な時期には、昔のストレス習慣が戻ることがあります。", "やめたはずの対処習慣でも、重圧が特に強くなると再び現れることがあります。"),
            ("Progress may mean noticing the habit earlier, not removing it completely.", "Improvement may mean recognizing the pattern sooner rather than eliminating it forever.", "改善とは、完全になくすことではなく、早く気づくことかもしれません。", "改善とは、その習慣を永遠になくすことではなく、より早くパターンに気づくことかもしれません。"),
        ],
        prompts=[
            prompt("The honest answer", "正直な答え", "What do you really do when you're stressed—not what you should do?", "ストレスがあるとき、するべきことではなく、実際には何をしますか？", ["What appears first in your behaviour?", "What helps you stay steady?"]),
            prompt("When it appears", "現れやすい時", "When does that reaction show up most often?", "その反応は、どのようなときにいちばん現れやすいですか？", ["What level of stress brings it out?", "When does the pattern stay quiet?"]),
            prompt("Help and cost", "助けと代償", "What does the habit help with, and what does it make worse?", "その習慣は何の助けになり、何を悪化させますか？", ["How long does the relief last?", "What cost appears later?"]),
            prompt("What people say", "人が話すこと", "How honestly do people usually describe what they do under stress?", "人は、ストレスがあるときにすることを、普段どのくらい正直に話すでしょうか？", ["Which response sounds better than it really is?", "Why might someone keep the real habit private?"], full="How accurately do people describe their own coping responses under stress?"),
            prompt("Then and now", "以前と今", "How has the way you handle stress changed over the past five years?", "ここ5年で、ストレスへの対処法はどう変わりましたか？", ["Which part has improved?", "Which part has stayed stubborn?"]),
            prompt("What makes it worse", "悪化する条件", "When is your usual stress response most unhelpful?", "いつものストレスへの対処が、いちばん役に立たないのはどんなときですか？", ["Which responsibility becomes harder?", "Who else can be affected?"], full="In which situation is your usual coping response most counterproductive?"),
            prompt("A realistic alternative", "現実的な代わり", "What would you realistically like to do instead?", "代わりに、現実的には何をしたいですか？", ["What is the smallest possible version?", "What would make it easier to choose?"]),
            prompt("Notice it sooner", "早く気づく", "What sign could help you notice stress earlier?", "どのようなサインがあれば、もっと早くストレスに気づけますか？", ["What could you do at that first sign?", "Which sign is easiest to ignore?"], full="What signal could help you recognize stress sooner?"),
        ],
    ),
    40: topic(
        slug="a-superstition-you-follow-anyway",
        title="A superstition you follow anyway",
        ko="믿지는 않아도 따르는 미신",
        ja="信じていなくても従う迷信",
        goal=("Let's talk about why superstitions survive even when people doubt them.", "人が疑っていても迷信が残る理由について話しましょう。"),
        outcomes=(("Explain one superstition", "迷信を一つ説明する"), ("Separate belief from habit", "信じることと習慣を分ける"), ("Share a local example", "身近な例を紹介する")),
        article_title=("Belief, habit, and luck", "信念、習慣、運"),
        articles=[
            ("A superstition connects an action or sign with luck without clear proof.", "A superstition links an action, object, or sign to an outcome without reliable evidence.", "迷信は、はっきりした証拠なしに、行動やしるしと運を結びつけます。", "迷信は、確かな根拠なしに、行動や物、しるしを結果と結びつけます。"),
            ("People can follow one without fully believing it.", "People may follow a superstition even while saying they do not believe what it predicts.", "人は、完全に信じていなくても迷信に従うことがあります。", "迷信が予告することは信じないと言いながらも、それに従う人はいます。"),
            ("The action may be easy, while ignoring it feels strangely risky.", "The ritual may cost almost nothing, while breaking it creates a small but persistent discomfort.", "従うのは簡単でも、無視すると妙に不安に感じます。", "その行動にはほとんど負担がない一方で、破ると小さいながら消えない不安が生まれます。"),
            ("Many superstitions are learned from family, friends, or school.", "Superstitions often travel through families, peer groups, workplaces, and childhood warnings.", "多くの迷信は、家族や友人、学校から学びます。", "迷信は、家庭、友人関係、職場、子どものころの注意を通して伝わることがよくあります。"),
            ("Some began as practical warnings that lost their explanation.", "Some may preserve an old practical warning after its original explanation has disappeared.", "実用的な注意から始まり、理由だけが忘れられたものもあります。", "もともとの説明が消えたあとも、昔の実用的な注意だけを残しているものもあります。"),
            ("Others survive because the story is memorable and easy to repeat.", "Others survive because a vivid story is easier to transmit than a careful explanation.", "印象的で繰り返しやすい話だから残るものもあります。", "丁寧な説明より鮮明な物語のほうが伝えやすいため、残っているものもあります。"),
            ("Breaking a superstition can feel like testing luck on purpose.", "Deliberately breaking a superstition can feel like volunteering for an unnecessary test of luck.", "迷信を破ることは、わざと運を試すように感じられます。", "迷信を意図的に破ることは、必要もないのに自分から運試しをするように感じられます。"),
            ("Different places give the same number, animal, or object different meanings.", "The same number, animal, or household object can carry opposite meanings across cultures.", "同じ数字や動物、物でも、場所によって意味が違います。", "同じ数字、動物、家庭用品でも、文化によって正反対の意味を持つことがあります。"),
            ("Learning the story matters more than laughing at the rule.", "Understanding the social story is usually more interesting than judging whether the rule is rational.", "その決まりを笑うより、背景の話を知るほうが大切です。", "その決まりが合理的かを判断するより、社会的な背景を理解するほうがたいてい面白いものです。"),
            ("Even a skeptic may keep one ritual because it feels familiar.", "Even a committed skeptic may preserve one ritual because familiarity can be emotionally reassuring.", "迷信を疑う人でも、なじみがあるという理由で一つの習慣を続けることがあります。", "強く疑う人でも、なじみが心を落ち着かせるため、一つの習慣を残すことがあります。"),
        ],
        prompts=[
            prompt("A familiar superstition", "よく知る迷信", "Which superstition do you know best, whether or not you follow it?", "従っているかどうかに関係なく、いちばんよく知っている迷信は何ですか？", ["What action or sign is involved?", "Where did you first hear it?"]),
            prompt("What should happen", "起きるとされること", "What is supposed to happen when someone follows—or breaks—it?", "その迷信に従ったり破ったりすると、何が起きるとされていますか？", ["Which outcome sounds most dramatic?", "How is the rule passed on?"]),
            prompt("Why it survives", "残る理由", "Why do people keep following a superstition they doubt?", "人は、疑っている迷信にもなぜ従い続けるのでしょうか？", ["What feeling makes the habit hard to drop?", "How can family or tradition matter?"]),
            prompt("A believable part", "信じられる部分", "What part of a superstition can feel believable even to a skeptic?", "迷信のどのような部分なら、疑う人にも信じられそうですか？", ["Could coincidence strengthen the belief?", "Might the rule contain practical wisdom?"], full="Which element of a superstition can remain plausible even to a skeptic?"),
            prompt("Break it on purpose", "わざと破る", "What would make you break a superstition on purpose?", "どのような理由があれば、迷信をわざと破りますか？", ["Would any uneasy feeling remain?", "What evidence would matter most?"]),
            prompt("A Japanese example", "日本の例", "What's a Japanese superstition an outsider might not know?", "外国の人が知らなさそうな日本の迷信は何ですか？", ["Where might they encounter it?", "What background would help them understand it?"]),
            prompt("The strangest one", "いちばん不思議なもの", "What's the strangest superstition you know?", "知っている中で、いちばん不思議な迷信は何ですか？", ["Which detail keeps it in people's minds?", "Which part is hardest to explain?"], full="What's the most unusual superstition you've encountered?"),
            prompt("One to keep", "残したいもの", "Which superstition is worth keeping as a tradition?", "どの迷信は、伝統として残す価値がありますか？", ["What story would survive with it?", "How would you keep it from becoming harmful?"], full="Which superstition deserves to survive as a tradition?"),
        ],
    ),
    41: topic(
        slug="what-a-free-saturday-looks-like",
        title="What a free Saturday looks like",
        ko="아무 일정 없는 토요일",
        ja="予定のない土曜日",
        goal=("Let's talk about what makes a free Saturday feel satisfying.", "予定のない土曜日を満足できる一日にするものについて話しましょう。"),
        outcomes=(("Describe the day's rhythm", "一日の流れを説明する"), ("Name what protects the day", "その日を守る条件を話す"), ("Notice what's missing", "足りないものに気づく")),
        article_title=("The shape of free time", "自由時間の形"),
        articles=[
            ("A completely unstructured day can feel restful or strangely difficult.", "An entirely unstructured day can feel liberating, unsettling, or both.", "予定がまったく決まっていない日は、休まることもあれば、妙に難しく感じることもあります。", "予定がまったくない一日は、解放感と落ち着かなさの両方をもたらすことがあります。"),
            ("Without a deadline, the morning may start much later than planned.", "Without an external deadline, the morning can expand far beyond our intention.", "締め切りがないと、朝は予定よりずっと遅く始まることがあります。", "外から決められた期限がないと、朝の時間は思っていた以上に長く伸びることがあります。"),
            ("One fixed ritual can give the rest of the day a useful shape.", "A single reliable ritual can provide enough structure for the rest of the day to remain flexible.", "一つ決まった習慣があると、残りの一日に形が生まれます。", "一つの確かな習慣があるだけで、残りを自由にしながら一日に十分な形を与えられます。"),
            ("Doing nothing is different from choosing to rest.", "Unplanned inactivity does not always provide the same recovery as deliberate rest.", "何もしないことと、休むことを選ぶのは違います。", "予定なく動かないことは、意識して休むことと同じ回復をもたらすとは限りません。"),
            ("A small errand can either start the day or interrupt it.", "A minor errand can create momentum or break the sense of freedom, depending on when it happens.", "小さな用事は、一日を始めるきっかけにも、邪魔にもなります。", "小さな用事でも、行う時間によって、一日の勢いを作ったり、自由な感覚を壊したりします。"),
            ("Messages from other people can turn open time into a shared plan.", "A message can instantly convert private open time into a social commitment.", "誰かからの連絡で、空いていた時間が一緒の予定に変わります。", "一通のメッセージで、自分だけの自由時間がすぐに人との約束へ変わります。"),
            ("The ideal balance between company and solitude changes from week to week.", "The right balance between company and solitude depends on what the week has already demanded.", "人と過ごす時間と一人の時間の理想的なバランスは、週ごとに変わります。", "人と過ごす時間と一人の時間の適切なバランスは、その週にすでに何を求められたかで変わります。"),
            ("Sundays can feel different because Monday is already closer.", "Sunday carries a different emotional weight because the next week's demands are already visible.", "日曜日は月曜日が近いので、土曜日とは違って感じます。", "日曜日は次の週の予定がすでに見えているため、土曜日とは違う心理的な重さがあります。"),
            ("Free days change as our responsibilities and energy change.", "Our version of a free day evolves with age, responsibility, health, and available energy.", "責任や元気の量が変わると、自由な日の過ごし方も変わります。", "自由な一日の形は、年齢、責任、健康、使えるエネルギーとともに変化します。"),
            ("What feels missing from a free day can show what we need.", "What feels missing from a free day may reveal what our ordinary routines fail to provide.", "自由な日に足りないと感じるものは、自分に必要なものを示します。", "自由な日に足りないと感じるものから、普段の生活では満たせていないことが見える場合があります。"),
        ],
        prompts=[
            prompt("A free Saturday", "予定のない土曜日", "Imagine a Saturday with no plans. How would it begin?", "予定のない土曜日を想像してください。どのように始めますか？", ["What time would the day really start?", "Which part would you refuse to rush?"]),
            prompt("The open morning", "自由な朝", "What would you do once the morning opened up?", "自由に使える朝になったら、何をしますか？", ["Would you stay home or go somewhere?", "What mood would you want for the day?"]),
            prompt("A routine worth keeping", "続けたい習慣", "What makes one routine worth keeping even on a free day?", "自由な日でも、一つの習慣を続ける価値があるのはなぜですか？", ["How can it anchor the day?", "When would you happily skip it?"]),
            prompt("What would ruin it", "台無しにするもの", "What would ruin that kind of Saturday?", "そのような土曜日を台無しにするものは何ですか？", ["Could you recover the day afterward?", "Which interruption would be acceptable?"]),
            prompt("Saturday and Sunday", "土曜と日曜", "Why can a free Sunday feel different from a free Saturday?", "予定のない日曜日は、なぜ土曜日と違って感じるのでしょうか？", ["When does Monday enter your thoughts?", "Which day is easier to enjoy fully?"]),
            prompt("Five years apart", "5年間の違い", "How would your ideal free weekend differ from one five years ago?", "理想の予定のない週末は、5年前とどう違いますか？", ["What would change most?", "Which older part would you bring back?"]),
            prompt("Company and solitude", "人と一人の時間", "How much company would fit a truly free day?", "本当に自由な一日には、どのくらい人と過ごす時間が合いますか？", ["What kind of company fits best?", "What does solitude add?"]),
            prompt("The right balance", "ちょうどよいバランス", "What balance of plans and freedom makes a weekend satisfying?", "どのくらい予定と自由があると、満足できる週末になりますか？", ["When does planning become too much?", "How much empty time feels refreshing?"], full="What balance between structure and freedom makes a weekend genuinely satisfying?"),
        ],
    ),
    42: topic(
        slug="a-rule-that-only-made-sense-in-your-family",
        title="A rule that only made sense in your family",
        ko="우리 집에서만 통했던 규칙",
        ja="自分の家でだけ通じた決まり",
        goal=("Let's talk about why household rules make sense in one home and seem strange in another.", "家庭の決まりが、ある家では自然で別の家では不思議に見える理由について話しましょう。"),
        outcomes=(("Explain the household rule", "家庭の決まりを説明する"), ("Describe discovering the difference", "違いに気づいた場面を話す"), ("Choose what to carry forward", "残したいものを選ぶ")),
        article_title=("Every home makes a small culture", "どの家庭にも小さな文化がある"),
        articles=[
            ("Every household develops rules that feel obvious inside it.", "Every household develops rules that appear self-evident to the people living within it.", "どの家庭にも、その中では当然に感じられる決まりがあります。", "どの家庭にも、そこで暮らす人には自明に見える決まりが生まれます。"),
            ("Some rules solve a practical problem that outsiders cannot see.", "Some rules respond to a practical constraint that is invisible outside the household.", "家の外の人には見えない実用的な問題を解決する決まりもあります。", "家庭の外からは見えない実際的な制約に対応する決まりもあります。"),
            ("Others continue long after the original reason disappears.", "Other rules survive as habits long after their original purpose has vanished.", "もともとの理由がなくなったあとも続く決まりもあります。", "別の決まりは、最初の目的が消えたあとも習慣として残ります。"),
            ("Children often assume every home works the same way.", "Children naturally mistake household customs for universal rules.", "子どもは、どの家も同じようにしていると思いがちです。", "子どもは家庭の習慣を、誰にでも共通する決まりだと思い込みがちです。"),
            ("A visit to another home can reveal the difference suddenly.", "One visit, meal, or sleepover can suddenly expose how local a familiar rule is.", "ほかの家を訪れると、その違いに急に気づくことがあります。", "一度の訪問や食事、泊まりで、慣れた決まりがどれほどその家だけのものか突然分かります。"),
            ("The discovery can be funny, embarrassing, or surprisingly emotional.", "Discovering the difference can produce amusement, embarrassment, defensiveness, or relief.", "その発見は、面白かったり、恥ずかしかったり、意外に感情的だったりします。", "違いに気づくと、面白さ、恥ずかしさ、反発、安心などが生まれることがあります。"),
            ("We may keep a rule even after we stop agreeing with its reason.", "We may reproduce a household rule automatically even after rejecting the logic behind it.", "理由に納得しなくなっても、その決まりを続けることがあります。", "背景の理屈を否定したあとでも、家庭の決まりを無意識に再現することがあります。"),
            ("Another family's strange rule may be perfectly sensible in context.", "A rule that seems bizarre elsewhere may become entirely reasonable once its context is known.", "別の家庭の変わった決まりも、背景を知れば納得できるかもしれません。", "ほかでは奇妙に見える決まりでも、その背景が分かれば完全に合理的になることがあります。"),
            ("Passing a rule on is a choice, not an automatic duty.", "Carrying a rule into the next household is a deliberate choice rather than an inherited obligation.", "決まりを次に伝えることは、当然の義務ではなく選択です。", "決まりを次の家庭へ持ち込むことは、受け継いだ義務ではなく、意識的な選択です。"),
            ("The rules people remember become part of a family's story.", "The rules retold years later become part of the story a family tells about itself.", "覚えている決まりは、その家庭の物語の一部になります。", "何年後も語られる決まりは、その家族が自分たちについて語る物語の一部になります。"),
        ],
        prompts=[
            prompt("A household rule", "家庭の決まり", "What's a household rule that makes sense in one family but seems strange elsewhere?", "ある家庭では自然でも、別の場所では不思議に見える決まりは何ですか？", ["What problem might it solve?", "Why might an outsider misunderstand it?"]),
            prompt("How it works", "決まりの内容", "How would an unusual household rule work day to day?", "家庭の変わった決まりは、日常の中でどのように使われますか？", ["Who would be expected to follow it?", "What might happen when someone forgets?"]),
            prompt("Discovering differences", "違いに気づく時", "How do people discover that other households have different rules?", "人は、ほかの家庭に違う決まりがあると、どのように気づくのでしょうか？", ["Which situation reveals the difference fastest?", "What reaction might follow?"]),
            prompt("Understanding the rule", "決まりを理解する", "What makes an unfamiliar household rule feel reasonable?", "知らない家庭の決まりが、納得できるようになるのはどのようなときですか？", ["Which missing context matters most?", "What value might the rule protect?"]),
            prompt("Worth keeping", "残す価値", "Which family rules are worth keeping as an adult?", "どのような家庭の決まりは、大人になっても残す価値がありますか？", ["What purpose do they still serve?", "How might they need updating?"]),
            prompt("Where rules differ", "決まりが違う分野", "Which area of home life creates the most different rules?", "家庭生活のどの分野で、いちばん違う決まりが生まれますか？", ["Why does that area vary so much?", "Which difference could cause conflict?"]),
            prompt("Explaining it", "説明の仕方", "How should a household explain a rule to a guest?", "家庭の決まりを、来客にどのように説明するとよいですか？", ["Which rule needs advance warning?", "Where should the household stay flexible?"]),
            prompt("Known for", "覚えられる決まり", "What small rule should a household be known for?", "家庭は、どのような小さな決まりで知られるとよいですか？", ["What value would the rule express?", "How could it stay flexible?"]),
        ],
    ),
    43: topic(
        slug="an-embarrassing-memory-that-comes-back-at-night",
        title="An embarrassing memory that comes back at night",
        ko="밤이면 떠오르는 창피한 기억",
        ja="夜になると思い出す恥ずかしい記憶",
        goal=("Let's talk about why harmless embarrassing memories can stay with us.", "害のない恥ずかしい記憶が残り続ける理由について話しましょう。"),
        outcomes=(("Give a safe real or general example", "無理のない実例または一般的な例を挙げる"), ("Explain why such memories return", "そのような記憶が戻る理由を説明する"), ("Rejudge it from today", "今の視点で見直す")),
        article_title=("Why awkward memories return", "気まずい記憶が戻る理由"),
        articles=[
            ("An embarrassing moment can resurface long after everyone else has forgotten it.", "An embarrassing moment can resurface vividly long after every witness has forgotten it.", "恥ずかしい場面は、ほかの人が忘れたあとも、ふいによみがえることがあります。", "恥ずかしい場面は、その場にいた全員が忘れたあとも、鮮明によみがえることがあります。"),
            ("Quiet moments give the mind space to replay unfinished feelings.", "Quiet moments give the mind room to replay experiences that still feel emotionally unresolved.", "静かな時間には、まだ残っている気持ちを頭の中で繰り返しやすくなります。", "静かな時間には、感情的にまだ整理できていない経験を頭の中で再生する余地が生まれます。"),
            ("We remember our own mistake more clearly than other people's reactions.", "We often remember our own mistake in detail while exaggerating how much other people noticed.", "人の反応より、自分の失敗のほうをはっきり覚えています。", "自分の失敗は細かく覚えている一方で、周りの人が実際以上に注目していたように思いがちです。"),
            ("The memory may return when a new situation feels similar.", "A new social situation can reactivate an old memory through one small resemblance.", "似た新しい場面があると、その記憶が戻ることがあります。", "新しい人間関係の場面で小さな共通点があると、昔の記憶が再び動き出すことがあります。"),
            ("What felt terrible at fifteen may look ordinary years later.", "An event that felt catastrophic at fifteen may look painfully ordinary from adulthood.", "15歳のときに最悪だと思ったことも、何年か後には普通に見えるかもしれません。", "15歳では大惨事に感じた出来事も、大人の目にはつらいほどありふれたものに見えるかもしれません。"),
            ("Telling the story can turn shame into something shared and funny.", "Retelling the story can convert private shame into shared recognition or humour.", "人に話すと、恥ずかしさが共感や笑いに変わることがあります。", "語り直すことで、個人的な恥ずかしさが、共感やユーモアへ変わることがあります。"),
            ("But nobody should have to share a memory that still feels unsafe.", "A conversation does not require disclosing a memory that remains painful, private, or unsafe.", "今もつらい記憶を、無理に話す必要はありません。", "会話のために、今も苦しい、私的な、または安心して話せない記憶を明かす必要はありません。"),
            ("A small awkward moment can be enough for a good story.", "A harmless social faux pas often makes a better story than a deeply painful event.", "ささいな気まずい場面だけでも、十分によい話になります。", "害のないちょっとした失礼のほうが、深くつらい出来事よりも話にしやすいものです。"),
            ("We are usually kinder to another person's old mistake than to our own.", "We routinely offer other people more perspective and compassion than we grant ourselves.", "人の昔の失敗には、自分の失敗よりやさしくなれます。", "私たちは、自分に対してよりも、ほかの人には広い視野と思いやりを持って接することがよくあります。"),
            ("The memory may stay, but its meaning can still change.", "The event cannot be edited, but its meaning and emotional weight can continue to change.", "記憶は残っても、その意味は変わることがあります。", "出来事そのものは変えられなくても、その意味や感情的な重さは変わり続けます。"),
        ],
        prompts=[
            prompt("Why it replays", "思い出す理由", "Why can a harmless embarrassing moment replay for years?", "害のない恥ずかしい出来事が、何年も思い出されるのはなぜですか？", ["What kind of moment tends to stick?", "Why can night make it feel louder?"]),
            prompt("A safe example", "話しやすい例", "What's one harmless awkward moment that people often replay?", "人が何度も思い出しやすい、害のない気まずい場面を一つ挙げてください。", ["Where is the awkward turning point?", "Why can a small mistake feel so memorable?"]),
            prompt("Age and perspective", "年齢と見方", "How might age change the way an embarrassing memory feels?", "年齢によって、恥ずかしい記憶の感じ方はどう変わりそうですか？", ["What does experience help someone understand?", "Which moments feel bigger when people are young?"]),
            prompt("Nobody noticed", "誰も気づかない時", "Why can an embarrassing moment feel intense even when nobody notices?", "誰も気づかなくても、なぜ恥ずかしい出来事を強く感じるのでしょうか？", ["How does self-image matter?", "What reaction might someone imagine?"]),
            prompt("Another person's memory", "ほかの人の記憶", "What would another person probably remember from an embarrassing moment?", "恥ずかしい出来事について、ほかの人は何を覚えていそうですか？", ["How might their view differ?", "Which detail would they probably forget?"]),
            prompt("What brings it back", "思い出すきっかけ", "What kinds of trigger bring old embarrassment back?", "どのようなきっかけで、昔の恥ずかしさを思い出しますか？", ["Could a place, sound, or situation trigger it?", "Why do quiet moments leave more room for it?"], full="What kinds of trigger cause old embarrassment to resurface?"),
            prompt("What you'd say now", "今なら言うこと", "What would you say to someone replaying an old mistake?", "昔の失敗を何度も思い出している人に、何と伝えますか？", ["What might they be taking too seriously?", "Which lesson would actually help?"]),
            prompt("Funny later", "あとで笑える時", "When can an embarrassing memory become funny?", "恥ずかしい記憶は、どのようなときに笑えるものになりますか？", ["What can change the tone?", "What makes laughter kind rather than dismissive?"]),
        ],
    ),
    44: topic(
        slug="something-that-made-you-laugh-out-loud",
        title="Something that made you laugh out loud",
        ko="소리 내어 웃게 한 것",
        ja="声を出して笑ったこと",
        goal=("Let's talk about what makes real laughter happen.", "本当に笑うのはどのようなときか、話しましょう。"),
        outcomes=(("Reconstruct the funny moment", "笑った場面を再現する"), ("Explain why it worked", "面白かった理由を説明する"), ("Compare different humour", "笑いの好みを比べる")),
        article_title=("Why laughter is hard to explain", "笑いを説明するのが難しい理由"),
        articles=[
            ("Real laughter often arrives before we can explain the joke.", "We often laugh for real before we consciously understand what made something funny.", "本当の笑いは、なぜ面白いか説明する前に出ることがあります。", "何が面白かったのかを意識して理解する前に、本当に笑ってしまうことがよくあります。"),
            ("Timing can matter as much as the words themselves.", "A pause, interruption, or perfectly delayed reaction can matter as much as the words.", "言葉そのものと同じくらい、タイミングが大切です。", "間や割り込み、絶妙に遅れた反応が、言葉と同じくらい重要なことがあります。"),
            ("A serious situation can become funny when one small thing goes wrong.", "A serious situation can become hilarious when one small detail breaks the expected pattern.", "真面目な場面でも、小さなことがうまくいかないと面白くなることがあります。", "真面目な場面でも、一つの細部が予想された流れを崩すと、大笑いにつながることがあります。"),
            ("Shared history makes some jokes almost impossible to translate.", "Shared history can compress years of context into a joke that outsiders cannot decode.", "共通の思い出があると、ほかの人には説明しにくい笑いが生まれます。", "共有した歴史があると、何年分もの背景が一つの冗談に詰まり、外の人には理解できなくなります。"),
            ("Laughter can be contagious, making an ordinary moment funnier.", "Laughter is contagious; another person's reaction can amplify an otherwise ordinary moment.", "ほかの人が笑うと、普通の場面ももっと面白く感じられます。", "笑いはうつるため、ほかの人の反応で、普通なら何でもない場面がさらに面白くなります。"),
            ("Trying too hard to be funny can make a room uncomfortable.", "Visible effort can make humour feel forced and leave the room less relaxed.", "面白くしようとしすぎると、その場が気まずくなることがあります。", "頑張って笑わせようとしているのが見えると、ユーモアが不自然になり、その場がかえって緊張します。"),
            ("Different people laugh at stories, language, mistakes, or absurd situations.", "Our humour may respond to storytelling, wordplay, a social faux pas, absurdity, or recognition.", "人によって、物語、言葉、失敗、変な状況など、笑うものが違います。", "人の笑いは、物語、言葉遊び、ちょっとした失礼、ばかばかしさ、共感など、さまざまなものに反応します。"),
            ("A joke that works once may fail when it is repeated.", "Surprise is often part of the mechanism, so repetition can remove what made the joke work.", "一度面白かった冗談も、繰り返すとうまくいかないことがあります。", "驚きが笑いの仕組みの一部なので、繰り返すと面白さの理由が失われることがあります。"),
            ("Explaining a funny moment requires enough context, but not every detail.", "Retelling a funny moment requires selective context: enough to set the pattern, but not enough to bury the turn.", "面白い場面を話すには、十分な背景が必要ですが、細部を全部話す必要はありません。", "面白い場面を語り直すには、流れが分かるだけの背景は必要ですが、肝心の転換を埋もれさせるほど多くは要りません。"),
            ("The funniest person is often the one who notices what everyone else missed.", "The funniest person in a group may be the one who notices and names the detail everyone else overlooked.", "いちばん面白い人は、ほかの人が見逃したことに気づく人かもしれません。", "集団でいちばん面白い人は、全員が見逃した細部に気づいて言葉にする人かもしれません。"),
        ],
        prompts=[
            prompt("Real laughter", "本当に笑う時", "What kind of moment makes you laugh out loud?", "どのような瞬間に、声を出して笑いますか？", ["What usually catches you off guard?", "What is different about a real laugh?"]),
            prompt("The setup", "笑いの準備", "What needs to happen before a funny moment works?", "面白い瞬間が成立する前に、何が必要ですか？", ["How much context is enough?", "Where does surprise enter?"]),
            prompt("Other people's laughter", "ほかの人の笑い", "How can another person's reaction make something funnier?", "ほかの人の反応で、どうしてさらに面白くなるのでしょうか？", ["When does laughter become contagious?", "Can a reaction be funnier than the original joke?"]),
            prompt("What matters most", "いちばん大切なもの", "Which matters most to you in humour: timing, words, or the situation?", "笑いでは、タイミング、言葉、状況のどれが自分にとっていちばん大切ですか？", ["What example shows that best?", "Would everyone understand the humour?"]),
            prompt("What usually works", "普段笑うもの", "What kind of humour works reliably on you?", "どのような笑いなら、普段から自分に合いますか？", ["What example fits your taste?", "When can the same style fail?"]),
            prompt("Hard to enjoy", "楽しみにくい笑い", "Which kind of humour is hardest for you to enjoy?", "どのような笑いが、自分にはいちばん楽しみにくいですか？", ["What makes it uncomfortable or dull?", "Could the right person make it work better?"]),
            prompt("Retelling it", "話し直す", "What makes a funny story survive being retold?", "面白い話が、語り直しても面白さを保つのはなぜですか？", ["Which detail is essential?", "Which background detail should be cut?"], full="What allows a funny story to survive the act of retelling?"),
            prompt("A funny person", "面白い人", "What quality makes someone genuinely funny?", "どのような特徴があると、その人は本当に面白いと感じますか？", ["What do funny people notice well?", "When does trying too hard stop working?"]),
        ],
    ),
    45: topic(
        slug="your-real-bedtime",
        title="Your real bedtime",
        ko="실제로 잠드는 시간",
        ja="実際に寝る時間",
        goal=("Let's talk about what shapes your real bedtime and the rest you get.", "実際に眠る時間と、取れる休息を左右するものについて話しましょう。"),
        outcomes=(("Describe last night's sleep timing", "昨夜の睡眠の時間帯を話す"), ("Trace what shaped it", "睡眠の時間を左右したものをたどる"), ("Judge what actually helps", "本当に役立つことを考える")),
        article_title=("The gap before sleep", "眠るまでのずれ"),
        articles=[
            ("The time we plan to sleep and the time we actually fall asleep are often different.", "The time we intend to sleep often differs from the moment sleep actually begins.", "寝ようと思う時間と、実際に眠りにつく時間は、よくずれます。", "眠ろうと考えている時間と、実際に眠り始める瞬間は、しばしば一致しません。"),
            ("The last hour of the day can disappear into one more small task.", "The final hour can dissolve into a chain of tasks that each seem too small to postpone.", "一日の最後の一時間は、もう一つの小さな用事で消えることがあります。", "一日の最後の一時間は、どれも先延ばしにするほどではないと思える用事の連鎖に消えることがあります。"),
            ("Phones make it easy to continue a day that has already ended.", "Phones remove the natural stopping points that once signaled the end of the day.", "スマートフォンがあると、もう終わった一日を簡単に続けられます。", "スマートフォンは、以前なら一日の終わりを知らせていた自然な区切りをなくします。"),
            ("Late evening may be the first time that feels completely our own.", "For some people, late evening is the only time free from requests, duties, and other people's schedules.", "夜遅くが、初めて完全に自分の時間だと感じることがあります。", "人によっては、夜遅くが、お願いや義務、他人の予定から解放される唯一の時間です。"),
            ("That freedom makes going to bed feel like giving something up.", "When private time is scarce, sleep can feel like surrendering the only part of the day we control.", "その自由があると、寝ることが何かを手放すように感じられます。", "自分だけの時間が少ないと、睡眠は自分で決められる一日の唯一の部分を手放すように感じられます。"),
            ("A late night matters differently before a free day and a busy one.", "The cost of a late night depends heavily on the next morning's obligations and recovery time.", "夜更かしの影響は、翌日が休みか忙しいかで違います。", "夜更かしの負担は、翌朝の義務や回復に使える時間によって大きく変わります。"),
            ("Trying to fix sleep with a strict rule can work briefly and then fail.", "A rigid sleep rule may produce short-term compliance without addressing what keeps bedtime late.", "厳しい決まりで睡眠を直そうとしても、短期間で終わることがあります。", "厳格な睡眠ルールは、就寝が遅くなる原因に向き合わないまま、短期的に従わせるだけかもしれません。"),
            ("A small routine can help us wind down before sleep.", "A modest ritual can help us wind down by creating the transition that willpower alone fails to provide.", "眠る前の小さな習慣があると、ゆっくり気持ちを落ち着けやすくなります。", "ささやかな習慣があると、意志の力だけでは作れない切り替えが生まれ、眠る前にゆっくり気持ちを落ち着けられます。"),
            ("The useful change may be earlier in the evening, not at bedtime.", "The most effective intervention may happen hours before bed, when the evening is still being shaped.", "役立つ変化は、寝る時間ではなく、もっと早い夜の時間にあるかもしれません。", "最も効果的な対策は、就寝時ではなく、夜の流れがまだ作られている数時間前に行われるかもしれません。"),
            ("The real goal is enough rest, not a perfect-looking routine.", "The meaningful goal is sustainable rest rather than a routine that merely appears disciplined.", "本当の目標は、完璧に見える習慣ではなく、十分に休むことです。", "大切な目標は、きちんとして見える習慣ではなく、続けられる休息です。"),
        ],
        prompts=[
            prompt("Last night's bedtime", "昨夜の就寝時間", "What time did you go to bed last night?", "昨夜は何時に寝ましたか？", ["What time did you want to sleep?", "What decided what actually happened?"]),
            prompt("The last hour", "最後の一時間", "How did you spend the last hour before trying to sleep?", "眠ろうとする前の最後の一時間を、どのように過ごしましたか？", ["Did the activity have a clear stopping point?", "Why was it easy or hard to stop?"]),
            prompt("Your sleep pattern", "睡眠のパターン", "How predictable is your bedtime from day to day?", "毎日の就寝時間は、どのくらい予測できますか？", ["What causes the biggest variation?", "Which part stays fairly stable?"]),
            prompt("Does it matter?", "問題になる？", "How does the time you sleep—or miss sleep—affect the following day?", "眠る時間、または眠れないことは、その後の一日にどう影響しますか？", ["Which part of the day changes first?", "When does an unusual sleep time matter less?"]),
            prompt("Changing the schedule", "時間帯を変える", "Which change to your sleep schedule would be most worth trying?", "あなたの睡眠の時間帯で、いちばん試す価値がある変化は何ですか？", ["Why could the change be worthwhile?", "What would make it difficult to maintain?"]),
            prompt("What gets in the way", "邪魔するもの", "What most often delays or shifts your sleep?", "何が原因で、眠る時間が遅れたりずれたりしますか？", ["Is it a task, a habit, or needed private time?", "Which part could happen at a different time?"]),
            prompt("A useful change", "役立つ変化", "Which small change seems most likely to improve your rest?", "どの小さな変化が、休息をいちばん改善できそうですか？", ["Why does it seem realistic?", "What obstacle would it need to overcome?"]),
            prompt("A realistic routine", "現実的な習慣", "What would a realistic, restful wind-down routine look like for you?", "無理なく続けられ、しっかり休むことにもつながる、眠る前の過ごし方はどのようなものですか？", ["When would you start to wind down?", "What would you deliberately leave until later?"]),
        ],
    ),
    46: topic(
        slug="a-personal-rule-you-never-break",
        title="A personal rule you never break",
        ko="절대 어기지 않는 개인 원칙",
        ja="絶対に破らない自分のルール",
        goal=("Let's talk about how personal rules can make repeated decisions easier.", "自分のルールが、繰り返す判断をどのように楽にするか話しましょう。"),
        outcomes=(("State a real or possible rule", "実際のルールまたは考えられるルールを述べる"), ("Explain where it came from", "その始まりを説明する"), ("Test its limits", "例外や限界を考える")),
        article_title=("Rules we choose for ourselves", "自分で選ぶルール"),
        articles=[
            ("A personal rule turns a repeated decision into a clear boundary.", "A personal rule converts a recurring decision into a boundary that no longer needs daily debate.", "自分のルールは、繰り返す判断を明確な境界に変えます。", "自分のルールは、何度も繰り返す判断を、毎日迷わなくてよい境界へ変えます。"),
            ("It can protect time, money, health, relationships, or peace of mind.", "Such a boundary may protect time, money, health, relationships, dignity, or peace of mind.", "そのルールは、時間、お金、健康、人間関係、心の平穏を守れます。", "そのような境界は、時間、お金、健康、人間関係、尊厳、心の平穏を守ることがあります。"),
            ("Many strong rules begin after one experience we do not want to repeat.", "Many strict rules are written in response to one experience whose cost we refuse to repeat.", "厳しいルールの多くは、二度と経験したくない出来事のあとに生まれます。", "厳しいルールの多くは、二度と同じ代償を払わないために、ある経験をきっかけに作られます。"),
            ("The rule makes future choices faster, but too much rigidity can become a problem.", "The rule reduces decision fatigue, yet its clarity can harden into unnecessary rigidity.", "そのルールは今後の判断を速くしますが、融通が利かなすぎると問題になることがあります。", "そのルールは判断の疲れを減らす一方で、その明確さが不要な融通のなさへ変わることがあります。"),
            ("An exception does not always destroy the value of a rule.", "A carefully chosen exception may clarify the rule's purpose rather than weaken it.", "例外があっても、そのルールの価値がなくなるとは限りません。", "慎重に選んだ例外は、ルールを弱めるのではなく、その目的を明確にする場合があります。"),
            ("Other people may see a boundary as strange when they do not know its history.", "A boundary can look excessive to people who cannot see the experience behind it.", "背景を知らない人には、その境界が変に見えることがあります。", "その背景にある経験が見えない人には、境界が行きすぎに見えることがあります。"),
            ("Explaining the reason can be useful, but nobody owes every detail.", "Explaining a boundary can help cooperation, although its full personal history remains private.", "理由を説明すると役立ちますが、すべての細部を話す必要はありません。", "境界を説明すれば協力しやすくなりますが、その個人的な背景をすべて明かす必要はありません。"),
            ("Some rules outlive the problem they were designed to solve.", "Some personal rules remain long after the risk, relationship, or stage of life has changed.", "解決するはずだった問題がなくなったあとも残るルールがあります。", "危険や人間関係、人生の段階が変わったあとも、個人的なルールが残ることがあります。"),
            ("Reviewing a rule is different from breaking it carelessly.", "Reconsidering a rule deliberately is different from abandoning it under temporary pressure.", "ルールを見直すことと、軽く破ることは違います。", "ルールを意識して考え直すことは、一時的な圧力で捨てることとは違います。"),
            ("The best rule still serves a clear purpose today.", "A durable personal rule remains connected to a purpose we can still name and defend today.", "よいルールには、今でも明確な役割があります。", "長く続ける価値のある自分のルールは、今も言葉にして説明できる目的と結びついています。"),
        ],
        prompts=[
            prompt("A useful personal rule", "役立つ自分ルール", "What personal rule can make life easier?", "どのような自分のルールが、生活を楽にできますか？", ["Which repeated decision could it simplify?", "What boundary would it create?"]),
            prompt("How strict", "厳しさ", "How strict should a useful personal rule be?", "役立つ自分のルールは、どのくらい厳しくするとよいですか？", ["Which exception would be reasonable?", "How would someone know the boundary was crossed?"]),
            prompt("Where rules come from", "ルールの始まり", "What experience can turn a preference into a firm rule?", "どのような経験が、好みをはっきりしたルールに変えるのでしょうか？", ["What could become the turning point?", "Which cost is the rule meant to prevent?"]),
            prompt("A reasonable exception", "納得できる例外", "When is breaking a personal rule reasonable?", "どのようなときは、自分のルールを破ってもよいですか？", ["What separates an exception from an excuse?", "What should happen afterward?"]),
            prompt("What others see", "ほかの人の見方", "Why can someone else's personal rule seem strange?", "ほかの人の自分ルールが、なぜ不思議に見えることがあるのでしょうか？", ["Which missing context could explain it?", "When might the rule be more common than it seems?"]),
            prompt("Explain or keep private", "説明する？", "How much of the reason would you explain to someone affected by the rule?", "そのルールの影響を受ける人に、理由をどこまで説明しますか？", ["What do they genuinely need to know?", "Which detail can remain private?"]),
            prompt("Still useful", "今も役立つか", "How can you tell whether a personal rule is still useful?", "自分のルールが今も役立っているか、どう判断できますか？", ["What evidence supports keeping it?", "Which change would justify revising it?"], full="How can someone evaluate whether a personal rule still serves its purpose?"),
            prompt("A rule to try", "試したいルール", "What personal rule would be worth trying this month?", "今月、どのような自分のルールを試す価値がありますか？", ["What is the smallest workable version?", "How would you test whether it helps?"]),
        ],
    ),
}


CLAIM_ORDER = {
    number: tuple(f"{number}-{index:02d}" for index in range(1, 11))
    for number in TOPICS
}


VOCABULARY = {
    34: {"new": "irritation|いら立ち", "recycled": "", "assumed": "small|ささいな; annoy|いら立たせる; notice|気づく; noise|音; habit|習慣; patience|我慢", "receptive": "friction|摩擦; disproportionate|実際以上に大きい"},
    35: {"new": "trivia|雑学", "recycled": "", "assumed": "fact|事実; useful|役に立つ; remember|覚えている; skill|技能; introduction|自己紹介", "receptive": "utility|実用性; oddity|変わった事実"},
    36: {"new": "private habit|人前では見せない習慣", "recycled": "", "assumed": "home|家; family|家族; public|人前; rule|決まり; privacy|私的な空間; harmless|害のない", "receptive": "suppress|抑える; rehearse|練習する"},
    37: {"new": "downpour|激しい雨", "recycled": "", "assumed": "rain|雨; plan|予定; food|食べ物; clothes|服; travel|移動する; memory|記憶", "receptive": "shelter|雨宿り; obligation|義務"},
    38: {"new": "drained|くたくたの", "recycled": "", "assumed": "tired|疲れた; sleep|睡眠; quiet|静けさ; food|食事; help|助け; advice|助言", "receptive": "overstimulated|刺激を受けすぎた; capacity|余力"},
    39: {"new": "coping response|ストレスへの対処", "recycled": "", "assumed": "stress|ストレス; habit|習慣; avoid|避ける; help|役立つ; change|変える; pressure|プレッシャー", "receptive": "procrastinate|先延ばしにする; sustainable|続けやすい"},
    40: {"new": "superstition|迷信; skeptic|疑う人", "recycled": "", "assumed": "believe|信じる; luck|運; rule|決まり; break|破る; number|数字; tradition|伝統", "receptive": "ritual|決まった行動; rational|合理的な"},
    41: {"new": "unstructured|予定が決まっていない", "recycled": "", "assumed": "Saturday|土曜日; Sunday|日曜日; plan|予定; morning|朝; free time|自由時間; alone|一人で", "receptive": "solitude|一人の時間; momentum|勢い"},
    42: {"new": "household rule|家庭の決まり", "recycled": "", "assumed": "home|家; family|家族; normal|普通の; strange|変な; child|子ども; reason|理由", "receptive": "unspoken|暗黙の; inherited|受け継いだ"},
    43: {"new": "resurface|再び思い出される", "recycled": "", "assumed": "embarrassing|恥ずかしい; memory|記憶; night|夜; remember|覚えている; funny|面白い; safe|安心して話せる", "receptive": "unresolved|整理できていない; compassion|思いやり"},
    44: {"new": "contagious|人にうつる", "recycled": "", "assumed": "laugh|笑う; joke|冗談; funny|面白い; person|人; story|話; timing|タイミング", "receptive": "wordplay|言葉遊び; absurdity|ばかばかしさ"},
    45: {"new": "wind down|ゆっくり一日を終える", "recycled": "", "assumed": "bedtime|寝る時間; sleep|眠る; phone|スマートフォン; evening|夜; morning|朝; routine|習慣", "receptive": "stopping point|区切り; sustainable|続けられる"},
    46: {"new": "rigidity|融通のなさ", "recycled": "", "assumed": "personal rule|自分のルール; choice|選択; boundary|境界; strict|厳しい; exception|例外; purpose|目的", "receptive": "dignity|尊厳; decision fatigue|判断の疲れ"},
}


GLOSSES = {
    34: {"accessible": {1: ("irritation", "irritation", "いら立ち")}, "full": {4: ("friction", "friction", "摩擦")}},
    35: {"accessible": {}, "full": {1: ("utility", "utility", "実用性")}},
    36: {"accessible": {}, "full": {2: ("suppress", "suppress", "抑える")}},
    37: {"accessible": {8: ("downpour", "downpour", "激しい雨")}, "full": {5: ("sheltered", "shelter", "雨宿り"), 8: ("downpour", "downpour", "激しい雨")}},
    38: {"accessible": {1: ("exhausted", "drained", "くたくたの")}, "full": {3: ("overstimulated", "overstimulated", "刺激を受けすぎた")}},
    39: {"accessible": {3: ("coping response", "coping response", "ストレスへの対処")}, "full": {3: ("coping response", "coping response", "ストレスへの対処"), 4: ("procrastinate", "procrastinate", "先延ばしにする")}},
    40: {"accessible": {10: ("skeptic", "skeptic", "疑う人")}, "full": {3: ("ritual", "ritual", "決まった行動")}},
    41: {"accessible": {1: ("unstructured", "unstructured", "予定が決まっていない")}, "full": {5: ("momentum", "momentum", "勢い")}},
    42: {"accessible": {1: ("household", "household rule", "家庭の決まり")}, "full": {9: ("inherited", "inherited", "受け継いだ")}},
    43: {"accessible": {1: ("resurface", "resurface", "再び思い出される")}, "full": {2: ("unresolved", "unresolved", "整理できていない")}},
    44: {"accessible": {}, "full": {5: ("contagious", "contagious", "人にうつる")}},
    45: {"accessible": {8: ("wind down", "wind down", "ゆっくり一日を終える")}, "full": {3: ("stopping points", "stopping point", "区切り"), 8: ("wind down", "wind down", "ゆっくり一日を終える")}},
    46: {"accessible": {4: ("rigidity", "rigidity", "融通のなさ")}, "full": {4: ("decision fatigue", "decision fatigue", "判断の疲れ")}},
}


def set_complete(head: str) -> str:
    name = "podo:proofread-status"
    if f'name="{name}"' in head:
        return base.set_meta(head, name, "complete")
    return re.sub(
        r'(<meta name="podo:content-version" content="[^"]+">)',
        rf'\1\n  <meta name="{name}" content="complete">',
        head,
        count=1,
    )


def article_page(topic_no: int, topic_data: dict, variant: str) -> str:
    rows = []
    en_column = 0 if variant == "accessible" else 1
    ja_column = 2 if variant == "accessible" else 3
    for index, (article, claim_id) in enumerate(
        zip(topic_data["articles"], CLAIM_ORDER[topic_no], strict=True), start=1
    ):
        en = article[en_column]
        ja = article[ja_column]
        en_markup, words = base.marked_text(en, GLOSSES[topic_no][variant].get(index))
        rows.append(
            f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{esc(ja)}</span>{words}</span></div>'
        )
    title, title_ja = topic_data["article_title"]
    body = '''      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>
      <div class="tutor-note">Answer the learner's questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>
      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">
''' + "\n".join(rows) + '''
      </div>'''
    return base.page("article", title, title_ja, body)


def build(topic_no: int, variant: str) -> str:
    topic_data = TOPICS[topic_no]
    canonical = CANONICAL[variant].read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{topic_data["slug"]}'
    level = "B1 accessible" if variant == "accessible" else "B2-C1 full"
    head = new_lesson.retarget(
        head,
        review_id=f"FT-{topic_no}",
        lesson_id=slug,
        level=level,
        title=topic_data["title"],
        title_ko=topic_data["ko"],
        title_ja=topic_data["ja"],
        version="2026-08-21",
    )
    head = set_complete(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])

    goal_en, goal_ja = topic_data["goal"]
    pages = [
        base.ft_contract.goal_page(
            title=topic_data["title"], title_ja=topic_data["ja"],
            topic_en=goal_en, topic_ja=goal_ja,
            data_act="Small things", kicker="SMALL THINGS",
        ),
        article_page(topic_no, topic_data, variant),
        base.extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of your answers.</span><span class="ja">全部の質問に答える必要はありません。答えの中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Treat these pages as a pool, not a sequence. React or share briefly before choosing the next prompt, skip freely, and move to feedback with 2–3 minutes left.</div></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple(
        (f"q{i}", f"QUESTION {i}") for i in range(1, 7)
    )
    pages.extend(
        base.question_page(page_id, number, item, variant)
        for (page_id, number), item in zip(prompt_ids, topic_data["prompts"], strict=True)
    )
    pages.append(base.extract_page(canonical, "feedback"))
    output = output_path(topic_no, variant)
    return new_lesson.redepth(head + "\n".join(pages) + foot, output)


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    topic_data = TOPICS[topic_no]
    slug = f'{topic_no:02d}-{topic_data["slug"]}'
    return TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="regenerate only this narrow batch")
    args = parser.parse_args()
    written = 0
    for topic_no in TOPICS:
        for variant in ("accessible", "full"):
            output = output_path(topic_no, variant)
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
