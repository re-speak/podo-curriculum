#!/usr/bin/env python3
"""Generate the explicit FT 47-56 People and Ties pairs, preserving FT-49."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ft_me_lately_batch as base
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/3-freetalking"
COURSE = "talk-people-and-ties"
TOPIC_NUMBERS = (47, 48, 50, 51, 52, 53, 54, 55, 56)
CANONICAL = {
    variant: TRACK / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html"
    for variant in ("accessible", "full")
}
PRESERVED = {
    "accessible": (
        TRACK / "courses/talk-people-and-ties-accessible/lessons/49-how-accurate-is-your-mbti/lesson.html",
        "5ef56b6b66ff7ada80587a9760c309efdbe3c9c5f794b2c5ee54fd4beb3dfb45",
    ),
    "full": (
        TRACK / "courses/talk-people-and-ties-full/lessons/49-how-accurate-is-your-mbti/lesson.html",
        "bc601a7090b9cac8aad8d812905c4950597aed5c9bc89eced5c1cdceb201a29d",
    ),
}
esc = base.esc


def prompt(title, title_ja, accessible, accessible_ja, followups, *, full, full_ja, full_followups):
    return {
        "title": title, "title_ja": title_ja,
        "accessible": accessible, "accessible_ja": accessible_ja,
        "full": full, "full_ja": full_ja,
        "accessible_followups": followups, "full_followups": full_followups,
    }


def topic(*, slug, title, ko, ja, goal, outcomes, article_title, articles, prompts):
    return locals()


# Every article row is (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
47: topic(
 slug="what-makes-a-friendship-last", title="What makes a friendship last", ko="오래가는 우정의 조건", ja="友情が長く続く理由",
 goal=("Let's talk about what makes a real or imagined friendship last.", "実際または想像の友情が長く続く理由について話しましょう。"),
 outcomes=(("Choose a real or imagined friendship", "実際または想像の友情を選ぶ"), ("Explain what could sustain it", "続くために必要なことを説明する"), ("Name your own contribution", "自分が与えるものを話す")),
 article_title=("What keeps a friendship going", "友情を続けるもの"),
 articles=[
  ("Long friendships rarely stay exactly the same.", "Long friendships endure without remaining static.", "長い友情も、ずっと同じ形のままとは限りません。", "長い友情は、変わらないからではなく、変化しながら続いていきます。"),
  ("People change jobs, homes, routines, and priorities.", "Jobs, homes, routines, and priorities can all shift over time.", "仕事や住む場所、生活習慣、優先することは変わります。", "仕事、住む場所、生活習慣、優先事項は、時間とともに変化します。"),
  ("A friendship lasts when both people make room for those changes.", "A friendship often lasts because both people allow the relationship to adapt.", "お互いの変化を受け入れられると、友情は続きやすくなります。", "双方が関係の変化を受け入れることで、友情は続きやすくなります。"),
  ("Frequent contact helps, but it is not the only measure of closeness.", "Regular contact can help, yet frequency alone does not define closeness.", "よく連絡を取ることは役立ちますが、親しさを測る唯一の基準ではありません。", "定期的な連絡は役立ちますが、頻度だけで親しさが決まるわけではありません。"),
  ("Some friends reconnect easily after months apart.", "Some friends resume an easy connection even after months of little contact.", "何か月も会わなくても、すぐ元のように話せる友人もいます。", "何か月もほとんど連絡しなくても、自然に関係を再開できる友人もいます。"),
  ("Shared history gives them context that new friends do not have.", "Shared history provides context that a newer relationship cannot yet offer.", "共通の思い出があると、新しい友人にはない理解が生まれます。", "共有してきた歴史は、新しい関係にはまだない理解を与えてくれます。"),
  ("History is not enough if one person stops listening or showing care.", "History alone cannot sustain a friendship when attention and care become one-sided.", "ただし、どちらかが話を聞かず、気にかけなくなれば、思い出だけでは続きません。", "ただし、関心や思いやりが一方通行になれば、共有した歴史だけでは友情を支えられません。"),
  ("Clear limits also protect a friendship from quiet resentment.", "Clear boundaries can protect a friendship from unspoken resentment.", "はっきりした限界があると、言えない不満から友情を守れます。", "明確な境界線は、口に出せない不満から友情を守ることがあります。"),
  ("People sometimes drift apart without either person doing anything wrong.", "People can drift apart because their lives diverge, without either person being at fault.", "どちらも悪くなくても、自然に疎遠になることがあります。", "どちらにも非がなくても、生活の方向が分かれて疎遠になることがあります。"),
  ("A lasting friendship is built by what both people keep bringing to it.", "A durable friendship depends on what both people continue to contribute.", "長く続く友情は、お互いが関係に与え続けるもので作られます。", "長く続く友情は、双方が関係に与え続けるものによって支えられます。"),
 ],
 prompts=[
  prompt("A lasting friend", "長く続く友人", "Think of a friend you've kept a long time. What are they like?", "長く付き合っている友人を思い浮かべてください。どんな人ですか？", ["If someone comes to mind, what do you value about them?", "If nobody does, what quality would you value in a long-term friend?"], full="Think of a friend you've kept for a long time. What are they like?", full_ja="長く付き合っている友人を思い浮かべてください。どのような人ですか？", full_followups=["If someone comes to mind, which quality do you value most?", "If nobody does, which quality would matter most in a long-term friend?"]),
  prompt("How you met", "出会い", "How did you meet—or how might that kind of friendship begin?", "どのように出会いましたか。または、そのような友情はどのように始まりそうですか？", ["For a real friendship, what was your first conversation about?", "For an imagined one, what might first give the two people something to discuss?"], full="How did you meet—or how might a friendship like that begin?", full_ja="どのように出会いましたか。または、そのような友情はどのように始まりそうですか？", full_followups=["For a real friendship, what first gave you something to discuss?", "For an imagined one, what might begin to create closeness?"]),
  prompt("Time together", "付き合いの長さ", "How long have you known each other—or how long would feel long to you?", "知り合ってどのくらいですか。または、自分にとって何年なら長い付き合いだと感じますか？", ["For a real friendship, what has changed during that time?", "For an imagined one, what would need to stay familiar as the years passed?"], full="How long have you known each other—or what duration would count as a long friendship to you?", full_ja="知り合ってどのくらいですか。または、自分にとってどのくらいなら長い友情だと言えますか？", full_followups=["For a real friendship, how has the relationship adapted over time?", "For an imagined one, what would need to remain familiar?"]),
  prompt("What keeps it going", "続く理由", "What keeps the real friendship going—or what would keep an imagined one strong?", "実際の友情は何によって続いていますか。または、想像した友情なら何が支えになりそうですか？", ["How do the two people show they care?", "What happens when life gets busy?"], full="What sustains the real friendship—or what would sustain an imagined one?", full_ja="実際の友情は何によって続いていますか。または、想像した友情なら何が支えになりそうですか？", full_followups=["How do both people demonstrate care?", "How does the relationship survive busy periods?"]),
  prompt("A deal-breaker", "受け入れられないこと", "What could you not put up with in a friendship?", "友情の中で、どうしても我慢できないことは何ですか？", ["Why would that cross a line?", "Could an apology repair it?"], full="What behaviour could you not tolerate in a friendship?", full_ja="友情の中で、どのような行動なら受け入れられませんか？", full_followups=["Why would that cross a boundary?", "Could a sincere apology repair the damage?"]),
  prompt("Drifting apart", "疎遠になる", "Have you drifted apart from anyone—or seen it happen to others?", "誰かと疎遠になったこと、またはほかの人に起きたのを見たことはありますか？", ["If yes, what changed first?", "If not, what commonly pulls friends apart?"], full="Have you drifted apart from anyone—or observed it happen to others?", full_ja="誰かと疎遠になったこと、またはほかの人に起きたのを見たことはありますか？", full_followups=["If yes, which change mattered first?", "If not, what commonly causes friends to diverge?"]),
  prompt("Starting again", "関係を戻す", "When is a friendship worth trying to restart?", "友情をもう一度始める価値があるのは、どんなときですか？", ["Who should make the first move?", "What would make contact feel natural?"], full="When is a friendship worth trying to revive?", full_ja="友情をもう一度よみがえらせる価値があるのは、どのようなときですか？", full_followups=["Who should make the first move?", "What would make renewed contact feel natural?"]),
  prompt("What you bring", "自分が与えるもの", "What do you bring to a good friendship?", "よい友情に、自分は何を与えていますか？", ["How would a friend describe that?", "What would you like to do better?"], full="What do you contribute to a strong friendship?", full_ja="強い友情に、自分は何を与えていますか？", full_followups=["How might a friend describe that contribution?", "What would you still like to improve?"]),
 ]),
48: topic(
 slug="a-first-impression-that-was-completely-wrong", title="A first impression that was completely wrong", ko="완전히 틀렸던 첫인상", ja="まったく違っていた第一印象",
 goal=("Let's examine a first impression and the evidence that changed it.", "第一印象と、それを変えた出来事について話しましょう。"),
 outcomes=(("Describe the first impression", "最初の印象を説明する"), ("Name what changed it", "印象を変えたことを話す"), ("Turn the lens on yourself", "自分への第一印象を考える")), article_title=("Why first impressions change", "第一印象が変わる理由"),
 articles=[
  ("A first impression forms before we know much about a person.", "A first impression forms from remarkably little information.", "第一印象は、相手をよく知る前に生まれます。", "第一印象は、驚くほど少ない情報から作られます。"),
  ("A voice, expression, or short reply can feel like strong evidence.", "A voice, expression, or brief reply can seem more revealing than it really is.", "声や表情、短い返事が、確かな証拠のように感じられることがあります。", "声や表情、短い返事が、実際以上にその人を表しているように見えることがあります。"),
  ("But the person may be tired, nervous, busy, or out of place.", "Yet the person may simply be tired, nervous, distracted, or outside their usual setting.", "しかし、その人は疲れていたり、緊張していたり、忙しかったりしただけかもしれません。", "しかし、その人は疲れていたり、緊張していたり、気が散っていたり、慣れない場にいただけかもしれません。"),
  ("One unusual moment can therefore create an unfair picture.", "An unrepresentative moment can therefore produce a confident but unfair judgment.", "そのため、普段と違う一瞬から、不公平なイメージができることがあります。", "そのため、普段を表さない一瞬から、自信はあっても不公平な判断が生まれることがあります。"),
  ("Repeated contact gives us more situations to compare.", "Repeated contact lets us compare behaviour across different situations.", "何度も会うと、違う場面での行動を比べられます。", "繰り返し会うことで、さまざまな状況での行動を比べられます。"),
  ("A generous action or honest conversation may change the picture quickly.", "One generous action or candid conversation may overturn the original picture.", "親切な行動や正直な会話で、印象がすぐ変わることもあります。", "思いやりのある行動や率直な会話で、最初の印象が覆ることもあります。"),
  ("Sometimes the change is slower and comes from a pattern.", "At other times, the revision is gradual and rests on a pattern rather than one event.", "一方で、何度かの行動を見て、ゆっくり印象が変わることもあります。", "一方で、一度の出来事ではなく行動の積み重ねから、徐々に印象が変わることもあります。"),
  ("A positive first impression can also turn out to be wrong.", "Favourable first impressions can turn out to be just as misleading.", "よい第一印象も、間違っていたと分かることがあります。", "好ましい第一印象も、同じように誤解を招くことがあります。"),
  ("Remembering our mistakes can make us slower to judge others.", "Remembering these revisions can make us more cautious about judging others quickly.", "自分の思い違いを覚えておくと、人をすぐに判断しにくくなります。", "こうした見直しを覚えておくと、人をすぐ判断することに慎重になれます。"),
  ("Other people are also forming incomplete first impressions of us.", "Meanwhile, other people are building equally incomplete first impressions of us.", "同時に、ほかの人も私たちについて不完全な第一印象を作っています。", "同時に、ほかの人も私たちについて、同じように不完全な第一印象を作っています。"),
 ],
 prompts=[
  prompt("Someone unexpected", "意外だった人", "Has anyone turned out completely different from how they first seemed?", "最初の印象とまったく違う人だったと分かったことはありますか？", ["If yes, who was the person to you?", "If not, which familiar or fictional example could you discuss?"], full="Has anyone turned out completely different from how they initially seemed?", full_ja="最初の印象とまったく違う人だったと分かったことはありますか？", full_followups=["If yes, what was your connection to the person?", "If not, which familiar or fictional example could you examine?"]),
  prompt("At first", "最初は", "What did you first think about that person or example?", "その人、または例について、最初はどう思いましたか？", ["Which detail created that impression?", "How certain did it feel?"], full="What was your initial impression of that person or example?", full_ja="その人、または例について、最初はどのような印象を持ちましたか？", full_followups=["Which detail shaped that impression?", "How confident were you in it?"]),
  prompt("The evidence", "変えた出来事", "What happened that changed the first impression?", "何が起きて、第一印象が変わりましたか？", ["Was it one moment or several?", "What did the person do differently?"], full="What evidence caused you to revise the first impression?", full_ja="どのような出来事によって、第一印象を見直しましたか？", full_followups=["Was the revision caused by one moment or a pattern?", "Which behaviour contradicted the original impression?"]),
  prompt("How long", "かかった時間", "How long did it take for the impression to change?", "印象が変わるまで、どのくらいかかりましたか？", ["Why did it take that long?", "Did anyone see the person differently sooner?"], full="How long did it take you to revise the impression?", full_ja="その印象を見直すまで、どのくらいかかりましたか？", full_followups=["What delayed or accelerated the change?", "Did anyone else recognize it sooner?"]),
  prompt("What you missed", "見落としていたこと", "Why was the first impression wrong?", "なぜ最初の印象は間違っていたのですか？", ["What context did you not have?", "Was any part of the first impression still fair?"], full="Why did the initial impression prove inaccurate?", full_ja="なぜ最初の印象は正確ではなかったのですか？", full_followups=["Which context was missing at first?", "Did any part of the initial impression remain valid?"]),
  prompt("The other direction", "逆の変化", "Has a good first impression ever become worse?", "よい第一印象が、あとで悪くなったことはありますか？", ["If yes, what changed it?", "If not, what warning sign might people miss?"], full="Has a favourable first impression ever deteriorated?", full_ja="よい第一印象が、あとで悪くなったことはありますか？", full_followups=["If yes, which evidence changed it?", "If not, which warning sign is easy to overlook?"]),
  prompt("Judging quickly", "すぐ判断すること", "When is a quick first impression useful?", "すぐに持つ第一印象が役立つのは、どんなときですか？", ["When can it become unfair?", "What should make us pause?"], full="When can a rapid first impression be useful?", full_ja="すぐに持つ第一印象が役立つのは、どのようなときですか？", full_followups=["When does speed make the judgment unfair?", "Which signal should make us suspend judgment?"]),
  prompt("People's view of you", "自分への第一印象", "What, if anything, do people get wrong about you at first?", "人は最初、自分について何か誤解しやすいですか。それとも、特にありませんか？", ["If something is misread, what creates that impression?", "If not, what do people usually understand correctly?"], full="What, if anything, do people commonly misread about you at first?", full_ja="人は最初、自分について何か誤解しやすいですか。それとも、特にありませんか？", full_followups=["If something is misread, which part of your manner creates it?", "If not, which quality do people usually recognize accurately?"]),
 ]),
50: topic(
 slug="something-you-would-never-do-alone", title="Something you would never do alone", ko="혼자서는 절대 하지 않을 일", ja="一人では絶対にしないこと",
 goal=("Let's find where being alone stops feeling comfortable and why.", "一人でできることの境界と、その理由について話しましょう。"),
 outcomes=(("Draw your line", "一人でできる範囲を決める"), ("Describe a real or imagined attempt", "実際または想像の挑戦を話す"), ("Name what could shift the line", "境界を変える条件を話す")), article_title=("Where the solo line comes from", "一人で行動する境界"),
 articles=[
  ("Being alone feels different in different activities.", "Solitude feels radically different depending on the activity.", "一人でいる感覚は、することによって変わります。", "一人でいる感覚は、活動の種類によって大きく変わります。"),
  ("Eating alone may feel ordinary while travelling alone feels difficult.", "Someone may dine alone comfortably yet find solo travel intimidating.", "一人での食事は普通でも、一人旅は難しく感じる人がいます。", "一人での食事は平気でも、一人旅には不安を感じる人がいます。"),
  ("The line depends partly on safety, cost, and unfamiliarity.", "The boundary often reflects safety, cost, unfamiliarity, and social expectations.", "その境界には、安全、費用、慣れているかどうかが関係します。", "その境界には、安全、費用、慣れのなさ、周囲の期待が関係します。"),
  ("It also depends on whether the activity is meant to be shared.", "It also depends on whether companionship is central to the activity's meaning.", "その活動を誰かと分かち合いたいかどうかも関係します。", "誰かと一緒にいることが、その活動の意味の中心かどうかも関係します。"),
  ("Doing something alone can bring freedom and control.", "Acting alone offers autonomy over pace, timing, and decisions.", "一人で行動すると、自由に決められます。", "一人で行動すると、速さ、時間、判断を自分で決められます。"),
  ("It can also make every problem feel like one person's responsibility.", "It can also concentrate every practical problem and decision on one person.", "一方で、問題を全部一人で引き受けるように感じることもあります。", "一方で、実際の問題や判断がすべて一人に集中します。"),
  ("A small successful attempt can expand a person's comfort zone.", "One manageable success can expand a person's comfort zone.", "小さな成功で、安心してできる範囲が広がることがあります。", "無理のない一度の成功で、安心してできる範囲が広がることがあります。"),
  ("A bad experience can move the line in the other direction.", "A frightening or exhausting experience can contract that boundary again.", "悪い経験で、その境界が逆に狭くなることもあります。", "怖い経験や疲れる経験で、その境界が再び狭くなることもあります。"),
  ("Another person's courage can make a solo activity seem possible.", "Seeing someone similar act alone can make the same choice feel attainable.", "ほかの人が一人で行動するのを見ると、その活動が自分にもできそうに感じます。", "自分に似た人が一人で行動するのを見ると、同じ選択が現実的に感じられます。"),
  ("The useful question is not whether solo is better, but where the choice feels right.", "The useful question is not whether independence is superior, but where it genuinely serves us.", "大切なのは一人がよいかではなく、どこまでなら自分に合うかです。", "大切なのは自立が優れているかではなく、どこまでなら本当に自分の役に立つかです。"),
 ],
 prompts=[
  prompt("Where's your line?", "どこまで一人で？", "Eating alone, cinema alone, travelling alone — where's your line?", "一人で食事、映画、一人旅。どこまでなら一人でできますか？", ["Which of the three feels easiest?", "Which one crosses your line?"], full="Eating alone, going to the cinema alone, travelling alone—where do you draw the line?", full_ja="一人で食事、映画、一人旅。どこに境界を引きますか？", full_followups=["Which of the three requires the least courage?", "Which one lies beyond your current boundary?"]),
  prompt("A recent example", "最近の例", "What's the boldest thing you've done alone—or one solo activity you'd realistically try?", "一人でした最も思い切ったこと、または現実的に一人で挑戦してみたいことは何ですか？", ["For a real experience, where did it happen?", "For a possible activity, what would make it manageable?"], full="What's the boldest thing you've done alone—or one solo activity you would realistically attempt?", full_ja="一人でした最も大胆なこと、または現実的に一人で挑戦したいことは何ですか？", full_followups=["For a real experience, where did it take place?", "For a possible activity, which condition would make it manageable?"]),
  prompt("What happened", "そのとき", "What happened in that real experience—or what might happen in the imagined one?", "実際の経験では何が起きましたか。または、想像した挑戦では何が起きそうですか？", ["Which moment would feel hardest?", "What could make it satisfying?"], full="What happened in the real experience—or what might unfold in the imagined one?", full_ja="実際の経験では何が起きましたか。または、想像した挑戦ではどのように進みそうですか？", full_followups=["Which moment would test you most?", "What could make the experience rewarding?"]),
  prompt("Freedom or pressure", "自由か負担か", "What is the best and hardest part of doing that alone?", "それを一人でする一番よい点と、一番難しい点は何ですか？", ["Which decisions become easier?", "Which problem would you rather share?"], full="What is the greatest freedom—and the greatest pressure—in doing that alone?", full_ja="それを一人でする最大の自由と、最大の負担は何ですか？", full_followups=["Which decisions become simpler?", "Which responsibility would you prefer to share?"]),
  prompt("Someone braver", "もっと勇気のある人", "Do you know anyone braver about doing things alone—or can you use a public or fictional example?", "一人で行動することに自分より勇気がある人を知っていますか。または、公に知られた人や架空の人物を例にできますか？", ["If someone comes to mind, what do they do differently?", "If nobody does, what would someone confident doing things alone do differently?"], full="Do you know anyone more comfortable acting alone—or can you use a public or fictional example?", full_ja="一人で行動することに自分より抵抗がない人を知っていますか。または、公に知られた人や架空の人物を例にできますか？", full_followups=["If someone comes to mind, which habit makes them seem confident?", "If nobody does, what would someone confident acting alone do differently?"]),
  prompt("A moving line", "変わった境界", "Has your line for doing things alone changed?", "一人でできることの境界は変わりましたか？", ["If yes, what moved it?", "If not, what has kept it stable?"], full="Has your boundary for doing things alone shifted over time?", full_ja="一人でできることの境界は、時間とともに変わりましたか？", full_followups=["If yes, which experience shifted it?", "If not, what has kept the boundary stable?"]),
  prompt("A smaller step", "小さな一歩", "What smaller solo activity could prepare you for the next one?", "次の挑戦に備えるために、どんな小さなことなら一人でできますか？", ["How would you reduce the risk?", "When would you know you were ready?"], full="Which smaller solo activity could prepare you to go further?", full_ja="さらに進む準備として、どのような小さなことなら一人でできますか？", full_followups=["How would you make the experiment safer?", "Which sign would show you were ready?"]),
  prompt("What would push it", "境界を広げる条件", "What would push your line further?", "何があれば、一人でできる範囲が広がりますか？", ["Would money, information, or practice matter most?", "Which activity would still remain outside it?"], full="What would expand your comfort zone further?", full_ja="何があれば、安心して一人でできる範囲がさらに広がりますか？", full_followups=["Would resources, information, or practice matter most?", "Which activity would still remain beyond it?"]),
 ]),
51: topic(
 slug="starting-a-conversation-with-a-stranger", title="Starting a conversation with a stranger", ko="낯선 사람과 대화 시작하기", ja="知らない人との会話の始め方",
 goal=("Let's build a natural opening and a graceful way out when it fails.", "自然な会話の始め方と、続かないときの終え方について話しましょう。"),
 outcomes=(("Choose an opening", "最初の一言を選ぶ"), ("Explain what to avoid", "避けたい話題を説明する"), ("Recover when it stalls", "会話が止まったときに対応する")), article_title=("How small talk opens a door", "雑談が会話を始めるしくみ"),
 articles=[
  ("Talking to a stranger begins with very little information.", "A conversation with a stranger begins under conditions of limited information.", "知らない人との会話は、相手の情報がほとんどない状態で始まります。", "知らない人との会話は、相手についての情報が限られた状態で始まります。"),
  ("A useful opening therefore comes from the situation around both people.", "A reliable opening usually draws on the immediate situation both people share.", "そのため、二人がいる状況から話題を選ぶと始めやすくなります。", "そのため、双方が共有する目の前の状況から始めると自然です。"),
  ("A delay, event, menu, or seat can provide a safe first topic.", "A delay, event, menu, or seating arrangement can provide a low-risk conversation starter.", "待ち時間や行事、メニュー、席などが安全な最初の話題になります。", "待ち時間、行事、メニュー、座席などが、負担の少ない会話のきっかけになります。"),
  ("The best question is easy to answer and not too personal.", "The best opening question is answerable without demanding private information.", "よい質問は答えやすく、個人的すぎません。", "よい最初の質問は、私的な情報を求めずに答えられるものです。"),
  ("The reply shows whether the other person wants to continue.", "The length and warmth of the reply signal whether the other person wants to continue.", "返事から、相手が会話を続けたいか分かります。", "返事の長さや温かさから、相手が会話を続けたいか分かります。"),
  ("A short answer is not always rejection; the person may be tired or busy.", "A brief answer is not necessarily rejection; the person may be tired, distracted, or occupied.", "短い返事でも、拒絶とは限りません。疲れていたり、忙しかったりする場合があります。", "短い返事でも拒絶とは限らず、疲れていたり、気が散っていたり、用事があったりします。"),
  ("One gentle follow-up is usually enough to test the conversation.", "One proportionate follow-up is usually enough to test whether there is mutual interest.", "会話が続くか確かめるには、軽い追加質問が一つあれば十分です。", "お互いに話す気があるか確かめるには、ほどよい追加質問が一つあれば十分です。"),
  ("If it still does not move, a polite ending protects both people.", "If the exchange still stalls, a graceful ending respects both people's attention.", "それでも続かなければ、丁寧に終えることでお互いに気まずくなりません。", "それでも会話が止まるなら、自然に終えることで双方の時間を尊重できます。"),
  ("People who seem good at small talk are often good at noticing signals.", "Skilled conversationalists are often distinguished less by wit than by attention to signals.", "雑談が上手な人は、相手の反応によく気づいています。", "会話が上手な人は、機知よりも相手の反応への注意によって際立つことが多いです。"),
  ("A failed opening is normal and does not need to become a bigger failure.", "An opening that goes nowhere is ordinary and need not become an awkward performance.", "会話が始まらないことは普通で、大きな失敗にする必要はありません。", "最初の一言が続かないのは普通で、気まずい失敗に広げる必要はありません。"),
 ],
 prompts=[
  prompt("Your opening", "最初の一言", "You're seated next to someone you've never met. What do you ask?", "会ったことのない人の隣に座っています。何を聞きますか？", ["Which shared detail could you mention?", "How would you keep it easy to answer?"], full="You're seated beside someone you've never met. How would you open the conversation?", full_ja="会ったことのない人の隣に座っています。どのように会話を始めますか？", full_followups=["Which shared detail would you use?", "How would you keep the opening low-pressure?"]),
  prompt("The setting", "場面", "Where would that opening work best?", "その最初の一言は、どんな場所で使いやすいですか？", ["What do both people already share there?", "Where would it feel less natural?"], full="In which setting would that opening work most naturally?", full_ja="その最初の一言は、どのような場面で最も自然に使えますか？", full_followups=["Which immediate context do both people share?", "In which setting would it feel intrusive?"]),
  prompt("What to avoid", "避けたい話題", "What would you avoid asking a stranger?", "知らない人には何を聞かないほうがよいですか？", ["Why could it feel too personal?", "Would the setting ever change that?"], full="Which topics would you avoid with a stranger?", full_ja="知らない人との会話では、どのような話題を避けますか？", full_followups=["Why might the topic feel intrusive?", "Could a different setting make it appropriate?"]),
  prompt("What has worked", "うまくいった一言", "Has an opening ever worked well for you—or in a conversation you observed?", "自分で、または見かけた会話で、最初の一言がうまくいったことはありますか？", ["If yes, what made the reply easy?", "If not, which familiar example might work?"], full="Has an opening ever worked especially well for you—or in an exchange you observed?", full_ja="自分で、または見かけたやり取りで、最初の一言が特にうまくいったことはありますか？", full_followups=["If yes, why was it easy to answer?", "If not, which familiar example seems effective?"]),
  prompt("A dead end", "続かなかった会話", "What kind of opening makes a conversation die quickly?", "どんな最初の一言だと、会話がすぐ終わりますか？", ["Is the problem the topic or the delivery?", "What might save it once?"], full="What kind of opening causes a conversation to stall immediately?", full_ja="どのような最初の一言だと、会話がすぐ止まりますか？", full_followups=["Is the problem usually the topic or the delivery?", "Which single follow-up might rescue it?"]),
  prompt("Someone skilled", "会話が上手な人", "Do you know someone good at small talk—or can you use a familiar public or imagined example?", "雑談が上手な人を知っていますか。または、公に知られた人や想像の例を使えますか？", ["If a person or example comes to mind, what signals do they notice?", "If none does, what would a skilled speaker notice?"], full="Have you observed someone skilled at small talk—or can you use a public or imagined example?", full_ja="雑談が上手な人を見たことがありますか。または、公に知られた人や想像の例を使えますか？", full_followups=["If a person or example comes to mind, which signals do they notice?", "If none does, what would make an imagined speaker skilful?"]),
  prompt("When it fails", "失敗したとき", "What do you do when your opening does not work?", "最初の一言がうまくいかないとき、どうしますか？", ["Would you try one more question?", "How would you end politely?"], full="How do you respond when an opening fails to create a conversation?", full_ja="最初の一言から会話が続かなかったとき、どう対応しますか？", full_followups=["When is one more question appropriate?", "How would you close the exchange gracefully?"]),
  prompt("A useful starter", "使えるきっかけ", "What conversation starter could you actually use this week?", "今週、実際に使えそうな会話のきっかけは何ですか？", ["Where could you use it?", "What answer would help you continue?"], full="Which conversation starter could you realistically use this week?", full_ja="今週、現実的に使えそうな会話のきっかけは何ですか？", full_followups=["In which setting could you use it?", "Which reply would give you a natural next question?"]),
 ]),
52: topic(
 slug="how-you-make-up-after-an-argument", title="How you make up after an argument", ko="다툰 뒤 화해하는 방법", ja="けんかのあとの仲直りのしかた",
 goal=("Let's talk about repairing a disagreement without assuming every conflict is the same.", "さまざまな対立を考えながら、関係を修復する方法について話しましょう。"),
 outcomes=(("Describe the first move", "最初の行動を説明する"), ("Explain what helps repair", "修復に役立つことを話す"), ("Choose a fair approach", "よい仲直りの方法を考える")), article_title=("What repair after conflict requires", "対立のあとの修復に必要なこと"),
 articles=[
  ("Arguments do not all need the same kind of repair.", "Conflicts vary, so repair cannot follow one universal script.", "けんかはすべて同じ方法で仲直りできるわけではありません。", "対立の形はさまざまで、修復に一つの決まった台本はありません。"),
  ("A small misunderstanding may need only a quick clarification.", "A minor misunderstanding may require little more than timely clarification.", "小さな誤解なら、すぐに説明するだけでよいことがあります。", "小さな誤解なら、適切なタイミングで説明するだけで十分なことがあります。"),
  ("A hurtful action may need time, responsibility, and a real apology.", "A harmful action may require time, accountability, and a specific apology.", "傷つける行動には、時間、責任、具体的な謝罪が必要な場合があります。", "人を傷つけた行動には、時間、責任を引き受けること、具体的な謝罪が必要な場合があります。"),
  ("Contacting first does not automatically mean admitting all the blame.", "Reaching out first is not the same as accepting sole responsibility.", "先に連絡しても、すべて自分が悪いと認めることにはなりません。", "先に連絡を取ることは、責任をすべて自分だけで負うこととは違います。"),
  ("It can simply mean that the relationship matters more than the silence.", "It may simply show that preserving the relationship matters more than prolonging the silence.", "沈黙を続けるより、関係を大切にしたいという意味にもなります。", "沈黙を長引かせるより、関係を守るほうが大切だと示すこともあります。"),
  ("Some people need a pause before they can speak calmly.", "Some people need distance before they can speak without defending themselves.", "落ち着いて話すために、少し時間が必要な人もいます。", "自己弁護ばかりせずに話すために、少し距離が必要な人もいます。"),
  ("Too much silence can make the original problem harder to name.", "An extended silence can add resentment and make the original issue harder to identify.", "沈黙が長すぎると、最初の問題を言葉にしにくくなります。", "沈黙が長引くと不満が加わり、もとの問題を見つけにくくなります。"),
  ("A good repair names the problem without trying to win it again.", "A constructive repair names the disagreement without reopening it as a contest.", "よい仲直りでは、もう一度勝とうとせずに問題を言葉にします。", "建設的な修復では、対立を勝負としてやり直さずに問題を言葉にします。"),
  ("Some relationships recover, while others need a new boundary.", "Some relationships recover fully; others require a firmer boundary or an ending.", "元に戻る関係もあれば、新しい境界が必要な関係もあります。", "完全に戻る関係もあれば、より明確な境界や終わりが必要な関係もあります。"),
  ("Making up is successful when the next interaction can be more honest.", "Repair succeeds when the next interaction can be safer and more honest.", "次の会話をもっと正直にできるなら、仲直りは成功です。", "次のやり取りをより安心して、正直にできるなら、修復は成功です。"),
 ],
 prompts=[
  prompt("Who moves first?", "先に動く人", "When you argue with someone close, who contacts who first?", "親しい人とけんかしたとき、どちらから先に連絡しますか？", ["If no close relationship or argument comes to mind, what seems fair in an ordinary imagined disagreement?", "In a real or imagined case, what makes the first move difficult?"], full="When you argue with someone close, who usually reaches out first?", full_ja="親しい人とけんかしたとき、普段はどちらから先に連絡を取りますか？", full_followups=["If no close relationship or argument comes to mind, which approach seems fairest in an ordinary imagined disagreement?", "In a real or imagined case, what makes initiating contact difficult?"]),
  prompt("How long", "かかる時間", "How long, if at all, do you need before you can talk calmly?", "落ち着いて話すまでに時間は必要ですか。必要なら、どのくらいですか？", ["If you take a pause, what do you do during it?", "If you do not, what helps you speak calmly right away?"], full="How much time, if any, do you need before a calm conversation becomes possible?", full_ja="落ち着いて話せるようになるまでに時間は必要ですか。必要なら、どのくらいですか？", full_followups=["If you take a pause, how do you use it?", "If you do not, what makes an immediate calm conversation possible?"]),
  prompt("The first message", "最初のメッセージ", "What would you say when you reach out in the first message?", "最初に連絡を取るメッセージで何と言いますか？", ["Would you name the argument immediately?", "How would you avoid sounding defensive?"], full="How would you word the first message when you reach out after an argument?", full_ja="けんかのあと、最初に連絡を取るメッセージをどのように書きますか？", full_followups=["Would you identify the disagreement immediately?", "How would you keep the tone from sounding defensive?"]),
  prompt("A real or safe example", "実際または話せる例", "What was a recent small disagreement—or what everyday example are you comfortable discussing?", "最近の小さな意見の違い、または差し支えなく話せる日常の例は何ですか？", ["If it was real, what was the disagreement really about?", "If it is a general example, what might happen afterward?"], full="What was a recent minor disagreement—or which everyday example are you comfortable examining?", full_ja="最近の小さな意見の違い、または差し支えなく話せる日常の例は何ですか？", full_followups=["If it was real, what was the underlying disagreement?", "If it is a general example, what might change afterward?"]),
  prompt("What repairs it", "修復に役立つこと", "What makes an apology feel real?", "どんな謝罪なら本気だと感じますか？", ["How specific should it be?", "What action should follow the words?"], full="What makes an apology feel credible?", full_ja="どのような謝罪なら信頼できると感じますか？", full_followups=["How specific should the apology be?", "Which action should follow the words?"]),
  prompt("Still unresolved", "まだ解決していないこと", "Can some arguments remain unfixed without ending a relationship?", "解決しないけんかがあっても、関係は続けられますか？", ["Which differences can people accept?", "When is a new boundary needed?"], full="Can some disagreements remain unresolved without destroying a relationship?", full_ja="解決しない意見の違いがあっても、関係を壊さずにいられますか？", full_followups=["Which differences can a relationship absorb?", "When does the disagreement require a new boundary?"]),
  prompt("Not every repair", "仲直りしない選択", "When is making up not the right goal?", "仲直りを目標にしないほうがよいのは、どんなときですか？", ["What would need to change first?", "How can someone end contact respectfully?"], full="When is reconciliation not the appropriate goal?", full_ja="仲直りを目標にすることが適切ではないのは、どのようなときですか？", full_followups=["Which condition would need to change first?", "How can someone end contact respectfully?"]),
  prompt("The right way", "よい方法", "What's the right way to make up after an ordinary argument?", "普通のけんかのあと、どのように仲直りするのがよいですか？", ["Who should speak first?", "How would you know the repair worked?"], full="What is a fair way to make up after an ordinary argument?", full_ja="普通のけんかのあと、どのように公平に仲直りできますか？", full_followups=["Who should initiate it?", "Which sign would show that the repair succeeded?"]),
 ]),
53: topic(
 slug="why-some-friendships-fade", title="Why some friendships fade", ko="어떤 우정이 멀어지는 이유", ja="友情が薄れていく理由",
 goal=("Let's explore why social circles change without forcing blame or disclosure.", "誰かを責めたり無理に話したりせずに、人間関係が変わる理由を考えましょう。"),
 outcomes=(("Compare two points in time", "二つの時期を比べる"), ("Separate causes from blame", "原因と責任を分ける"), ("Choose whether to act", "行動するか決める")), article_title=("Why connections fade", "つながりが薄れる理由"),
 articles=[
  ("Most social circles change even when nobody plans the change.", "Most social networks change without any deliberate decision to reshape them.", "人間関係は、誰も変えようとしなくても変わっていきます。", "人間関係は、誰かが意識して変えなくても形を変えていきます。"),
  ("A move, new job, family duty, or health issue can reduce contact.", "Relocation, work, care duties, or health can quietly reduce contact.", "引っ越し、仕事、家族の世話、健康の問題で連絡が減ることがあります。", "引っ越し、仕事、家族を支える役割、健康の問題で、連絡が静かに減ることがあります。"),
  ("The friendship may fade before either person notices a clear ending.", "A friendship may fade gradually, with no moment that either person recognizes as an ending.", "どちらも終わりに気づかないまま、友情が薄れることがあります。", "どちらも終わりだと認識する瞬間がないまま、友情が徐々に薄れることがあります。"),
  ("Distance matters, but different routines can create distance in the same city.", "Geography matters, yet incompatible routines can create distance even within one city.", "距離は関係しますが、同じ街でも生活習慣の違いで遠くなることがあります。", "物理的な距離は関係しますが、同じ街でも合わない生活習慣が隔たりを作ります。"),
  ("People also change what they need from friendship.", "People's expectations of friendship evolve with their circumstances.", "人は友情に求めるものも変わります。", "人が友情に求めるものは、状況とともに変化します。"),
  ("That change is not always a rejection of the other person.", "A changed need is not necessarily a judgment on the other person.", "その変化は、相手を拒絶することとは限りません。", "求めるものの変化は、必ずしも相手への否定的な判断ではありません。"),
  ("Sometimes one person did cause harm, and distance protects the other.", "Sometimes harm did occur, and greater distance is a necessary form of protection.", "誰かが傷つけたために、距離を置く必要がある場合もあります。", "実際に傷つける行動があり、距離を置くことが必要な自衛になる場合もあります。"),
  ("At other times, looking for fault creates a story that was never there.", "In other cases, assigning fault invents a conflict where gradual change is the fuller explanation.", "一方で、責任を探すことで、実際にはなかった対立を作ってしまうこともあります。", "一方で、責任を決めようとすると、徐々な変化で説明できることを対立にしてしまう場合もあります。"),
  ("Some faded friendships can be renewed with one honest message.", "Some dormant friendships can be renewed by one specific, low-pressure message.", "薄れた友情も、正直なメッセージ一つで戻ることがあります。", "休んでいた友情も、具体的で負担の少ないメッセージ一つで戻ることがあります。"),
  ("Others can be valued as part of the past without being restarted.", "Others can remain meaningful parts of the past without requiring renewal.", "再開しなくても、過去の大切な関係として残せる友情もあります。", "再開しなくても、過去の大切な関係として価値を持ち続ける友情もあります。"),
 ],
 prompts=[
  prompt("Then and now", "当時と今", "How many people did you see socially five years ago, compared to now?", "5年前と今では、個人的に会う人の数はどのくらい違いますか？", ["If a personal comparison works, would you say more, fewer, or about the same?", "If it does not, what familiar or imagined change in a social circle could you compare?"], full="How many people did you see socially five years ago, compared with now?", full_ja="5年前と今では、個人的に会う人の数はどのくらい違いますか？", full_followups=["If a personal comparison works, has the circle expanded, contracted, or stayed similar?", "If it does not, which familiar or imagined change in a social circle could you examine?"]),
  prompt("What changed", "変わったこと", "What changed in your real comparison—or in social life generally?", "自分の比較、または一般的な人間関係で、何が変わりましたか？", ["For your own comparison, was the change sudden or gradual?", "For a general example, which routine might change first?"], full="What changed in your own comparison—or in social life more generally?", full_ja="自分の比較、またはより一般的な人間関係で、何が変わりましたか？", full_followups=["For your own comparison, was the change abrupt or gradual?", "For a general example, which routine might shift first?"]),
  prompt("Who dropped off", "疎遠になった人", "Did you drift apart from anyone—or can you use a familiar example of two friends?", "誰かと疎遠になりましたか。または、二人の友人についての身近な例を使えますか？", ["For a real connection, what changed around the two people?", "For a familiar example, what commonly reduces contact between friends?"], full="Did you drift apart from anyone—or can you examine a familiar example of two friends?", full_ja="誰かと疎遠になりましたか。または、二人の友人についての身近な例を考えられますか？", full_followups=["For a real connection, which circumstances changed around the two people?", "For a familiar example, which factor commonly reduces contact between friends?"]),
  prompt("Fault or change", "責任か変化か", "In that real or familiar example, was anyone at fault, or was life changing?", "その実際または身近な例では、誰かに責任がありましたか。それとも生活が変わっただけですか？", ["In that example, what evidence would support blame?", "Which part could happen without anyone choosing it?"], full="In that real or familiar example, was anyone at fault, or was gradual life change the better explanation?", full_ja="その実際または身近な例では、誰かに責任がありましたか。それとも、徐々な生活の変化のほうがよい説明ですか？", full_followups=["In that example, which evidence would justify assigning responsibility?", "Which part could happen without deliberate choice?"]),
  prompt("The main cause", "主な原因", "Which matters most: distance, time, or people changing?", "距離、時間、人の変化のうち、どれが最も大きいですか？", ["Can two causes reinforce each other?", "Which one is easiest to overcome?"], full="Which factor matters most: distance, limited time, or personal change?", full_ja="距離、時間の不足、人の変化のうち、どれが最も大きいですか？", full_followups=["How might two factors reinforce each other?", "Which one is most realistic to overcome?"]),
  prompt("Normal or a problem", "自然か問題か", "Is a fading friendship normal, or is it a problem?", "友情が薄れるのは自然なことですか。それとも問題ですか？", ["What makes the difference?", "When does acceptance become avoidance?"], full="Is a fading friendship a normal transition or a problem that deserves attention?", full_ja="友情が薄れるのは自然な変化ですか。それとも向き合うべき問題ですか？", full_followups=["Which condition separates the two?", "When does acceptance become avoidance?"]),
  prompt("Reach out?", "連絡する？", "When is it worth contacting someone again?", "もう一度誰かに連絡する価値があるのは、どんなときですか？", ["What could the first message say?", "How could you keep it low-pressure?"], full="When is a faded connection worth trying to renew?", full_ja="薄れたつながりを、もう一度取り戻そうとする価値があるのはどんなときですか？", full_followups=["What specific message could reopen contact?", "How could you avoid creating pressure?"]),
  prompt("Overall", "全体として", "Overall, what should people do when a friendship fades?", "全体として、友情が薄れたとき、人はどうすればよいですか？", ["Which relationships deserve effort?", "Which ones can remain in the past?"], full="Overall, how should people respond when a friendship fades?", full_ja="全体として、友情が薄れたとき、人はどのように対応すればよいですか？", full_followups=["Which relationships deserve renewed effort?", "Which ones can be valued without being revived?"]),
 ]),
54: topic(
 slug="the-person-you-talk-to-most", title="The person you talk to most", ko="가장 많이 이야기하는 사람", ja="いちばんよく話す人",
 goal=("Let's compare one recent exchange with your broader contact pattern.", "最近のやり取りと、普段の連絡の形を比べましょう。"),
 outcomes=(("Choose a recent or familiar exchange", "最近または身近なやり取りを選ぶ"), ("Describe a contact pattern", "連絡の形を説明する"), ("Notice whether the pattern changed", "連絡の形が変わったか考える")), article_title=("What frequent contact reveals", "頻繁な会話から分かること"),
 articles=[
  ("The person we talk to most is not always the person we feel closest to.", "Our most frequent contact is not necessarily our most intimate relationship.", "いちばんよく話す人が、いちばん親しい人とは限りません。", "最も頻繁に連絡する相手が、必ずしも最も親しい相手とは限りません。"),
  ("Work, home, and daily routines shape who is available.", "Work, household structure, and routine strongly shape who is available to us.", "仕事、家庭、日課によって、話せる相手が決まります。", "仕事、家庭の形、日課によって、話せる相手が大きく決まります。"),
  ("Some frequent conversations are practical rather than personal.", "Some high-frequency exchanges are logistical rather than emotionally close.", "よくする会話でも、個人的ではなく用事だけの場合があります。", "頻繁なやり取りでも、感情的に親しいというより予定調整が中心の場合があります。"),
  ("Others move easily between small updates and serious worries.", "Other relationships move fluently between ordinary updates and serious concerns.", "日常の小さな話から深い悩みまで、自然に話せる関係もあります。", "日常の小さな近況から深刻な悩みまで、自然に行き来できる関係もあります。"),
  ("Messaging makes frequent contact possible without sharing a schedule.", "Messaging allows frequent contact without requiring two schedules to align.", "メッセージなら、同じ時間が空いていなくても頻繁に連絡できます。", "メッセージなら、二人の予定が合わなくても頻繁に連絡できます。"),
  ("Calls or face-to-face talks may carry more tone and detail.", "Calls and face-to-face conversations carry tone, pauses, and richer context.", "電話や対面の会話では、声の調子や細かな情報が伝わります。", "電話や対面の会話では、声の調子、間、より豊かな背景が伝わります。"),
  ("The main person can change when a job, home, or relationship changes.", "A change in work, home, or partnership can quickly reorder our most frequent contacts.", "仕事、住む場所、関係が変わると、よく話す相手も変わります。", "仕事、家庭、パートナー関係が変わると、よく話す相手の順番もすぐ変わります。"),
  ("Losing regular contact can reveal how much support it provided.", "The loss of routine contact can reveal support that had previously felt invisible.", "日常の連絡がなくなると、それがどれだけ支えだったか分かることがあります。", "いつもの連絡がなくなると、見えなかった支えに気づくことがあります。"),
  ("Staying in touch requires a rhythm both people can maintain.", "Staying in touch depends on a rhythm that neither person experiences as a burden.", "連絡を続けるには、二人が無理なく続けられる頻度が必要です。", "連絡を取り続けるには、どちらにも負担にならない頻度が必要です。"),
  ("The best measure may be not frequency but whether real things can be said.", "A better measure than frequency may be whether the relationship still holds honest conversation.", "大切なのは頻度より、本当のことを話せるかもしれません。", "頻度より、その関係で今も正直な話ができるかのほうが大切かもしれません。"),
 ],
 prompts=[
  prompt("Your last message", "最後のメッセージ", "Who did you last message, and what about?", "最後に誰に、何についてメッセージを送りましたか？", ["If it was automated or a group, what was the contact for?", "If no recent message comes to mind, what other contact or familiar example could you use?"], full="Who did you last message, and what was the exchange about?", full_ja="最後に誰にメッセージを送り、何についてやり取りしましたか？", full_followups=["If it was automated or a group, what purpose did the contact serve?", "If no recent message comes to mind, which other contact or familiar example could you examine?"]),
  prompt("Most often", "いちばんよく連絡する相手", "Is there one person, group, or service you contact most, or is your contact spread out?", "いちばんよく連絡する人、グループ、サービスがありますか。それとも、連絡先は分かれていますか？", ["If one contact stands out, is that because of closeness, need, or routine?", "If not, what determines who or what you contact on a given day?"], full="Is there one person, group, or service you contact most, or is communication spread across several contacts?", full_ja="最もよく連絡する人、グループ、サービスがありますか。それとも、複数の連絡先に分かれていますか？", full_followups=["If one contact stands out, does frequency come from closeness, need, or circumstance?", "If not, what determines the main contact on a given day?"]),
  prompt("How often", "頻度", "How often are you in touch with that main contact—or across your contacts overall?", "その主な相手、または連絡先全体とは、どのくらいの頻度でやり取りしますか？", ["If one contact stands out, who usually starts?", "If contact is spread out, what sets the rhythm?"], full="What rhythm do you maintain with that main contact—or across your contacts overall?", full_ja="その主な相手、または連絡先全体とは、どのような頻度でやり取りしますか？", full_followups=["If one contact stands out, who usually initiates?", "If communication is spread out, what determines its rhythm?"]),
  prompt("What you discuss", "話す内容や目的", "Across that contact pattern, what do you discuss—or what is the contact used for?", "その連絡の形では、何について話しますか。または、その連絡先を何に使いますか？", ["For a conversation, which topic comes up most?", "For an automated contact or service, what purpose does it serve?"], full="Across that pattern, which subjects do you discuss—or which purpose does the contact serve?", full_ja="その連絡の形では、どのような話題を話しますか。または、その連絡先はどのような目的で使いますか？", full_followups=["For a conversation, which subject dominates?", "For an automated contact or service, which need does it meet?"]),
  prompt("What you share", "話す内容や用件", "With that person, group, service, or other contact, what feels easy to discuss or handle?", "その人、グループ、サービス、またはほかの連絡先とは、どんな話題や用件なら扱いやすいですか？", ["If you discuss things, which topics feel comfortable?", "If not, which task or need is easy to handle through the contact?"], full="With that person, group, service, or other contact, which subjects or needs feel natural to handle?", full_ja="その人、グループ、サービス、またはほかの連絡先とは、どのような話題や用件なら自然に扱えますか？", full_followups=["If you have a conversation, which subjects feel comfortable?", "If not, which task or need is easy to handle through the contact?"]),
  prompt("Has it changed?", "変化", "Has the way you communicate changed over time?", "連絡のしかたは、時間とともに変わりましたか？", ["If it changed, what caused the shift?", "If it did not, what has kept it stable?"], full="Has your pattern of communication changed over time?", full_ja="連絡のしかたは、時間とともに変わりましたか？", full_followups=["If it changed, which circumstance drove the shift?", "If it did not, what has kept the pattern stable?"]),
  prompt("Five years ago", "5年前", "Five years ago, was there one main person, group, or service—or were contacts spread out?", "5年前に、主に連絡する人、グループ、サービスが一つありましたか。それとも、連絡先は分かれていましたか？", ["If one contact stood out, what role did that person, group, or service play then?", "If not, what shaped the mix of contacts—or what familiar historical example could you use?"], full="Five years ago, was there one main person, group, or service—or was communication distributed?", full_ja="5年前に、主な連絡先は人、グループ、サービスのどれか一つでしたか。それとも、複数に分かれていましたか？", full_followups=["If one contact stood out, what role did that person, group, or service play at that time?", "If not, what shaped the distribution—or which familiar historical example could you examine?"]),
  prompt("Staying in touch", "連絡を続ける", "What helps two people stay in touch without making it a duty?", "義務に感じずに二人が連絡を続けるには、何が役立ちますか？", ["How much silence is comfortable?", "What kind of message is easy to answer?"], full="What helps two people stay in touch without turning contact into an obligation?", full_ja="連絡を義務にせず、二人がつながり続けるには何が役立ちますか？", full_followups=["How much silence can the relationship comfortably hold?", "Which kind of message invites an easy response?"]),
 ]),
55: topic(
 slug="advice-that-stayed-with-you", title="Advice that stayed with you", ko="마음에 남은 조언", ja="心に残っている助言",
 goal=("Let's examine advice that stayed with you—or a familiar example—and decide whether it is worth passing on.", "心に残っている助言、または身近な例を取り上げ、人に伝える価値があるか考えましょう。"),
 outcomes=(("Choose real or familiar advice", "実際または身近な助言を選ぶ"), ("Explain why it lasted", "残った理由を説明する"), ("Decide whether to pass it on", "人に伝えるか決める")), article_title=("Why some advice stays", "助言が心に残る理由"),
 articles=[
  ("Advice often stays because of when we heard it, not only what it said.", "Advice often endures because of its timing, not merely its wording.", "助言は内容だけでなく、聞いたタイミングによって心に残ります。", "助言は言葉そのものだけでなく、聞いたタイミングによって残ります。"),
  ("A simple sentence can land differently during a difficult decision.", "An ordinary sentence can acquire unusual force during a difficult decision.", "難しい決断のときには、簡単な一言も違って響きます。", "難しい決断の中では、普通の一言が特別な力を持つことがあります。"),
  ("The speaker matters when we trust their experience or intentions.", "The source matters when we trust the speaker's experience, judgment, or care.", "相手の経験や意図を信頼していると、その人の言葉は大切になります。", "相手の経験、判断、思いやりを信頼していると、その言葉は大切になります。"),
  ("We may understand the words immediately but need years to understand their value.", "We may understand the literal message immediately while taking years to grasp its value.", "言葉はすぐ分かっても、その価値を理解するまで何年もかかることがあります。", "表面の意味はすぐ分かっても、その価値を理解するまで何年もかかることがあります。"),
  ("Good advice usually leaves room for the listener's real situation.", "Durable advice usually leaves room for context rather than pretending to be universal.", "よい助言は、聞く人の実際の状況に合わせる余地があります。", "長く役立つ助言は、すべてに当てはまるふりをせず、状況に合わせる余地があります。"),
  ("Bad advice may sound confident while ignoring cost, risk, or personality.", "Poor advice can sound decisive while ignoring cost, risk, power, or personality.", "悪い助言は自信があるように聞こえても、費用や危険、性格を無視することがあります。", "悪い助言は断定的に聞こえても、費用、危険、力関係、性格を無視することがあります。"),
  ("Ignoring advice does not always mean it was wrong.", "Advice can be sound even when the listener is not ready or the moment is wrong.", "助言に従わなくても、その助言が間違っていたとは限りません。", "聞く人に準備がない、または時期が違えば、よい助言でも従えないことがあります。"),
  ("Following advice also does not prove it caused the result.", "Following advice does not by itself prove that the advice produced the outcome.", "助言に従ったからといって、それが結果の原因だとは限りません。", "助言に従ったことだけでは、その助言が結果を生んだとは証明できません。"),
  ("When we pass advice on, we also pass our interpretation of it.", "Passing advice on inevitably carries our own interpretation and omissions.", "助言を人に伝えるとき、自分なりの解釈も一緒に伝えます。", "助言を人に伝えるとき、自分の解釈や省いた部分も必ず一緒に伝わります。"),
  ("The best test is whether the advice helps someone see a choice more clearly.", "A useful test is whether the advice clarifies a choice without taking ownership of it away.", "よい助言かどうかは、誰かが選択をはっきり見られるようになるかで分かります。", "よい助言かどうかは、相手から決定権を奪わずに選択を明確にできるかで分かります。"),
 ],
 prompts=[
  prompt("Words that stayed", "残っている言葉", "What's one thing someone said to you that you still repeat?", "誰かに言われたことで、今も繰り返している言葉は何ですか？", ["If something comes to mind, who said it?", "If nothing does, what familiar saying or general example could you use?"], full="Which advice has stayed with you—or which familiar example could you examine?", full_ja="心に残っている助言はありますか。または、どの身近な例を取り上げますか？", full_followups=["If advice comes to mind, who gave it?", "If none does, which familiar saying or general example could you examine?"]),
  prompt("The wording", "言葉", "What were the exact words—or how would you put the idea now?", "正確にはどんな言葉でしたか。または、今ならその考えをどう表しますか？", ["Which word carries the main point?", "Would another wording change the meaning?"], full="What was the original wording—or how would you formulate the idea now?", full_ja="元はどんな言葉でしたか。または、今ならその考えをどう表現しますか？", full_followups=["Which phrase carries the central idea?", "Would different wording alter its force?"]),
  prompt("The source", "言った人", "Who gave you the advice—or where did you hear it?", "誰からその助言をもらいましたか。または、どこで聞きましたか？", ["Why did that source matter?", "Would the same words work from someone else?"], full="Who gave you the advice—or what was its source?", full_ja="誰からその助言をもらいましたか。または、出どころは何でしたか？", full_followups=["Why did that source carry authority for you?", "Would the same words work from a different person?"]),
  prompt("The moment", "関係する場面", "What was happening when the advice became relevant—or when might it matter?", "その助言が関係するようになったとき、何が起きていましたか。または、どんな場面で関係しそうですか？", ["For a real case, what made the timing important?", "For a familiar example, when might the advice be needed?"], full="What was happening when the advice became relevant—or in which situation might it matter?", full_ja="その助言が関係するようになったとき、何が起きていましたか。または、どのような状況で関係しそうですか？", full_followups=["For a real case, why was the timing significant?", "For a familiar example, when might the advice be needed?"]),
  prompt("Understanding later", "あとで分かること", "Did you understand advice you actually heard then—or when might a familiar example become clear?", "自分が実際に聞いた助言は当時理解できましたか。または、身近な例ならいつ意味が分かりそうですか？", ["For a real case, what changed your understanding?", "For a familiar example, which experience might make it clearer?"], full="Did you grasp advice you actually heard immediately—or when might a familiar example make sense in hindsight?", full_ja="自分が実際に聞いた助言はすぐ理解できましたか。または、身近な例ならいつ振り返って意味が分かりそうですか？", full_followups=["For a real case, which experience changed your interpretation?", "For a familiar example, what might become clearer with distance?"]),
  prompt("Did it help?", "役に立つ？", "How has the advice helped someone—or how might it fail to help?", "その助言は人にどのように役立ちましたか。または、どのように役立たない可能性がありますか？", ["For a real case, which choice did it affect?", "For a familiar example, where might its limit be?"], full="In what way has the advice helped someone—or in which situation might it fail to help?", full_ja="その助言は人にどのように役立ちましたか。または、どのような状況では役立たない可能性がありますか？", full_followups=["For a real case, which decision did it influence?", "For a familiar example, where might its usefulness end?"]),
  prompt("Passing it on", "人に伝える", "Who, if anyone, would you pass on the advice to?", "その助言を人に伝えるなら、誰に伝えますか？", ["Who might benefit from it—or might nobody benefit?", "What would you adapt—or what makes it too specific to share?"], full="Under what conditions, if any, would you pass on the advice?", full_ja="その助言を人に伝えるなら、どのような条件ですか。それとも、伝えませんか？", full_followups=["Who might genuinely benefit—or might nobody benefit?", "How would you adapt it—or what makes it unsuitable to pass on?"]),
  prompt("Advice ignored", "従わなかった助言", "Have you ever ignored advice—or can you use a familiar example?", "助言に従わなかったことがありますか。または、身近な例を使えますか？", ["If it happened to you, what stopped you from following it?", "If it is a familiar example, why might someone choose differently?"], full="Have you ever chosen not to follow advice—or can you examine a familiar example?", full_ja="助言に従わないと決めたことがありますか。または、身近な例を取り上げられますか？", full_followups=["If it happened to you, which circumstance outweighed the advice?", "If it is a familiar example, why might someone choose differently?"]),
 ]),
56: topic(
 slug="the-person-you-would-call-in-an-emergency", title="The person you would call in an emergency", ko="위급할 때 전화할 사람", ja="緊急時に電話する人",
 goal=("Let's discuss practical support through a safe hypothetical, with no forced disclosure.", "無理に体験を話さず、安全な仮定を使って実際の支えについて話しましょう。"),
 outcomes=(("Choose a safe contact or service", "安全な連絡先やサービスを選ぶ"), ("Explain what support means", "必要な支えを説明する"), ("Consider distance and change", "距離や変化を考える")), article_title=("What an emergency contact represents", "緊急時の連絡先が表すもの"),
 articles=[
  ("An emergency call asks for more than sympathy.", "An emergency call often asks for practical judgment as well as emotional support.", "緊急時の電話では、共感だけでなく実際の助けも求めます。", "緊急時の電話では、感情的な支えだけでなく、実際の判断も求めることがあります。"),
  ("The right contact depends on the kind of problem.", "The appropriate contact depends on whether the problem is medical, practical, legal, or emotional.", "誰に連絡するかは、問題の種類によって変わります。", "連絡すべき相手は、医療、実務、法律、感情のどの問題かで変わります。"),
  ("A trusted person may know our needs but lack the right skill.", "A trusted person may understand us deeply while lacking the expertise the situation requires.", "信頼する人は自分を分かっていても、必要な技能がない場合があります。", "信頼する人は深く理解していても、その状況に必要な専門性がない場合があります。"),
  ("A professional service may be the safest first call.", "A professional or emergency service may therefore be the safest first point of contact.", "専門サービスや緊急サービスが最初の連絡先として安全なことがあります。", "そのため、専門機関や緊急サービスが最も安全な最初の連絡先になることがあります。"),
  ("After that, personal support can help with decisions and next steps.", "Personal support can then help us interpret information and manage the next steps.", "そのあと、身近な人が判断や次の行動を支えてくれます。", "そのあと、身近な人が情報を理解し、次の行動を進めるのを支えてくれます。"),
  ("In the first few minutes, reliability can matter more than emotional closeness.", "Practical reliability may matter more than emotional closeness in the first few minutes.", "最初の数分は、心の近さより、確実に対応してくれることが大切な場合があります。", "最初の数分は、感情的な近さより、実際に確実に対応できることが大切な場合があります。"),
  ("Distance limits physical help, but advice, coordination, and reassurance can still reach us.", "Distance limits physical help, although advice, coordination, and reassurance can still reach us.", "距離があると直接の助けは限られますが、助言や手配、安心感は届けられます。", "距離があると直接の助けは限られますが、助言、手配、安心感は届けられます。"),
  ("A move, illness, or relationship change can alter which people and services belong in a support network.", "A move, illness, or change in relationships can reorder the people and services in a support network.", "引っ越し、病気、人間関係の変化で、支援体制に含まれる人やサービスも変わります。", "引っ越し、病気、人間関係の変化で、支援体制に含まれる人やサービスの役割や順番も変わります。"),
  ("Some people do not have one obvious personal contact, and a service may be part of the answer.", "Not having one obvious personal contact is meaningful information; a professional service may be part of the answer.", "すぐ思い浮かぶ身近な人がいなくても、サービスを選ぶ方法があります。", "すぐ思い浮かぶ身近な人がいないことは大切な情報で、専門サービスも選択肢になります。"),
  ("A support network of people and services is stronger when roles and contact details are clear before a crisis.", "A support network of people and services becomes more resilient when roles, limits, and contact details are clear before a crisis.", "緊急事態の前に役割や連絡先が分かっていると、人やサービスを含む支援体制はもっと確かになります。", "危機の前に役割、限界、連絡先が明確なら、人やサービスを含む支援体制はより確かな支えになります。"),
 ],
 prompts=[
  prompt("First call", "最初の連絡先", "If something went badly wrong tonight, who's the first person you'd call?", "もし今夜、大きな問題が起きたら、最初に誰に電話しますか？", ["A safe hypothetical is enough; what kind of problem are you imagining?", "If no person comes to mind, which service would you contact first?"], full="If something went badly wrong tonight, who would be your first call?", full_ja="もし今夜、大きな問題が起きたら、最初に誰へ連絡しますか？", full_followups=["A safe hypothetical is enough; which kind of problem are you considering?", "If no individual comes to mind, which professional service would be first?"]),
  prompt("Why them", "その人を選ぶ理由", "Why would that person or service be the first choice?", "なぜその人、またはサービスを最初に選びますか？", ["What could they do immediately?", "What could they not do?"], full="Why would that person or service be your first point of contact?", full_ja="なぜその人、またはサービスを最初の連絡先にしますか？", full_followups=["Which immediate need could they meet?", "Where would their ability or role end?"]),
  prompt("What you would say", "伝えること", "What information would you give first?", "最初にどんな情報を伝えますか？", ["Which detail would help them act?", "What could wait until later?"], full="Which information would you communicate first?", full_ja="最初にどの情報を伝えますか？", full_followups=["Which detail would enable useful action?", "Which information could safely wait?"]),
  prompt("Needed before", "過去の必要", "Have you ever needed that kind of help—or can we keep it hypothetical?", "そのような助けが必要だったことはありますか。それとも仮定の話にしますか？", ["If real, what kind of support mattered?", "If hypothetical, which step seems hardest?"], full="Have you ever needed comparable help—or would you prefer to keep the discussion hypothetical?", full_ja="同じような助けが必要だったことはありますか。それとも仮定の話にしますか？", full_followups=["If real, which form of support mattered most?", "If hypothetical, which step appears most difficult?"]),
  prompt("Someone calling you", "自分に連絡する人", "Is there anyone who might call you for help—or what role could you handle?", "助けを求めて自分に連絡する人はいますか。または、自分ならどんな役割を担えますか？", ["What help could you realistically offer?", "When would you call a professional instead?"], full="Might anyone call you for help—or which support role could you realistically fill?", full_ja="助けを求めて自分に連絡する人はいますか。または、現実的にどのような支援の役割を担えますか？", full_followups=["Which help could you reliably provide?", "At what point would you involve a professional?"]),
  prompt("Has it changed?", "変わった連絡先", "Has your first-choice contact changed over time?", "最初に連絡する相手は、時間とともに変わりましたか？", ["If yes, what changed around you?", "If not, what makes the arrangement stable?"], full="Has your first-choice contact changed as your circumstances have changed?", full_ja="状況の変化とともに、最初に連絡する相手も変わりましたか？", full_followups=["If yes, which circumstance reordered your contacts?", "If not, what makes the arrangement durable?"]),
  prompt("Distance", "距離", "How much does distance matter in an emergency?", "緊急時に、距離はどのくらい重要ですか？", ["Which help requires someone nearby?", "Which help can still come from far away?"], full="How does physical distance change the value of an emergency contact?", full_ja="物理的な距離は、緊急時の連絡先の価値をどのように変えますか？", full_followups=["Which forms of help require proximity?", "Which forms of support remain possible at a distance?"]),
  prompt("A stronger network", "より強い支援体制", "What could make a support network of people and services more reliable before an emergency?", "緊急事態の前に、人やサービスを含む支援体制をもっと確かにするには何ができますか？", ["Which contact detail should be easy to find?", "Which person or service needs a clear role?"], full="What would make a support network of people and services more resilient before an emergency occurs?", full_ja="緊急事態が起きる前に、人やサービスを含む支援体制をもっと強くするには何が必要ですか？", full_followups=["Which information should be immediately accessible?", "Which person's or service's role or limit should be clarified in advance?"]),
 ]),
}


CLAIM_ORDER = {number: tuple(f"{number}-{index:02d}" for index in range(1, 11)) for number in TOPIC_NUMBERS}
VOCABULARY = {
 47: {"new": "drift apart|疎遠になる", "recycled": "friend|友だち|CORE-4", "assumed": "friendship|友情; meet|出会う; change|変わる; listen|話を聞く; care|気にかける", "receptive": "put up with|我慢する; resentment|言えない不満; static|変化しない"},
 48: {"new": "first impression|第一印象", "recycled": "turn out|実際には〜だとわかる|FT-1", "assumed": "person|人; seem|〜のように見える; think|思う; change|変わる; wrong|間違った", "receptive": "misleading|誤解を招く; candid|率直な"},
 50: {"new": "comfort zone|安心してできる範囲", "recycled": "", "assumed": "alone|一人で; eat|食べる; cinema|映画館; travel|旅行する; safety|安全", "receptive": "autonomy|自分で決める自由; attainable|実現できそうな"},
 51: {"new": "small talk|雑談; conversation starter|会話のきっかけ", "recycled": "", "assumed": "stranger|知らない人; ask|聞く; conversation|会話; answer|答える; busy|忙しい", "receptive": "intrusive|立ち入りすぎた; low-pressure|負担の少ない"},
 52: {"new": "make up|仲直りする; reach out|連絡を取る", "recycled": "", "assumed": "argument|けんか; contact|連絡する; first|先に; apology|謝罪; relationship|関係", "receptive": "accountability|責任を引き受けること; reconciliation|仲直り"},
 53: {"new": "fade|薄れていく", "recycled": "drift apart|疎遠になる|FT-47", "assumed": "friendship|友情; five years ago|5年前; distance|距離; time|時間; fault|責任", "receptive": "dormant|休んでいる; diverge|別の方向へ進む"},
 54: {"new": "stay in touch|連絡を取り続ける", "recycled": "", "assumed": "message|メッセージを送る; talk|話す; person|人; often|よく; five years ago|5年前", "receptive": "logistical|予定調整の; intimate|親密な"},
 55: {"new": "pass on|人に伝える", "recycled": "", "assumed": "advice|助言; say|言う; remember|覚えている; understand|理解する; help|役立つ", "receptive": "in hindsight|あとから考えると; decisive|断定的な"},
 56: {"new": "support network|人やサービスを含む支援体制", "recycled": "emergency|緊急時|FT-20; reliable|信頼できる|CORE-56", "assumed": "call|電話する; person|人; help|助け; tonight|今夜; distance|距離", "receptive": "resilient|立て直しやすい; expertise|専門性"},
}
GLOSSES = {
 47: {"accessible": {8: ("resentment", "resentment", "言えない不満"), 9: ("drift apart", "drift apart", "疎遠になる")}, "full": {1: ("static", "static", "変化しない"), 8: ("resentment", "resentment", "言えない不満")}},
 48: {"accessible": {8: ("turn out", "turn out", "実際には〜だとわかる")}, "full": {8: ("misleading", "misleading", "誤解を招く")}},
 50: {"accessible": {7: ("comfort zone", "comfort zone", "安心してできる範囲")}, "full": {5: ("autonomy", "autonomy", "自分で決める自由")}},
 51: {"accessible": {9: ("small talk", "small talk", "雑談")}, "full": {3: ("conversation starter", "conversation starter", "会話のきっかけ")}},
 52: {"accessible": {}, "full": {4: ("Reaching out", "reach out", "連絡を取る")}},
 53: {"accessible": {3: ("fade", "fade", "薄れていく")}, "full": {9: ("dormant", "dormant", "休んでいる")}},
 54: {"accessible": {9: ("Staying in touch", "stay in touch", "連絡を取り続ける")}, "full": {3: ("logistical", "logistical", "予定調整の")}},
 55: {"accessible": {}, "full": {}},
 56: {"accessible": {10: ("support network", "support network", "人やサービスを含む支援体制")}, "full": {3: ("expertise", "expertise", "専門性")}},
}


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_preserved() -> None:
    for variant, (path, expected) in PRESERVED.items():
        actual = file_hash(path)
        if actual != expected:
            raise SystemExit(f"FT-49 {variant} changed: expected {expected}, got {actual}")


def set_complete(head: str) -> str:
    name = "podo:proofread-status"
    if f'name="{name}"' in head:
        return base.set_meta(head, name, "complete")
    return re.sub(r'(<meta name="podo:content-version" content="[^"]+">)', rf'\1\n  <meta name="{name}" content="complete">', head, count=1)


def article_page(topic_no: int, data: dict, variant: str) -> str:
    en_col, ja_col = (0, 2) if variant == "accessible" else (1, 3)
    rows = []
    for index, (article, claim_id) in enumerate(zip(data["articles"], CLAIM_ORDER[topic_no], strict=True), 1):
        en_markup, words = base.marked_text(article[en_col], GLOSSES[topic_no][variant].get(index))
        rows.append(f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{esc(article[ja_col])}</span>{words}</span></div>')
    title, title_ja = data["article_title"]
    body = '''      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>
      <div class="tutor-note">Answer the learner's questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>
      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">
''' + "\n".join(rows) + '''
      </div>'''
    return base.page("article", title, title_ja, body)


def question_page(page_id: str, number: str, item: dict, variant: str) -> str:
    lis = "".join(f"<li>{esc(value)}</li>" for value in item[f"{variant}_followups"])
    japanese = item[f"{variant}_ja"]
    # A dash can join two alternatives into one English speaking turn. Japanese
    # uses a comma for that same turn; an internal full stop would make
    # script-lines.js interpret it as two separate instructions.
    if sum(item[variant].count(mark) for mark in ".!?") == 1:
        japanese = japanese.replace("。", "、")
    body = f'''      <p class="section-subtitle ask"><span class="q-n">{number}</span><span class="ko">{esc(item[variant])}</span><span class="ja">{esc(japanese)}</span></p>
      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span><ul class="tn-more">{lis}</ul></div></div>
      <div class="fb" data-fb="{variant}-{page_id}"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'''
    return base.page(page_id, item["title"], item["title_ja"], body)


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
    return TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"


def build(topic_no: int, variant: str) -> str:
    data = TOPICS[topic_no]
    canonical = CANONICAL[variant].read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{data["slug"]}'
    head = new_lesson.retarget(head, review_id=f"FT-{topic_no}", lesson_id=slug,
        level="B1 accessible" if variant == "accessible" else "B2-C1 full",
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-20")
    head = set_complete(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])
    goal_en, goal_ja = data["goal"]
    outcomes = "".join(f'<div class="known-row"><span class="k">{esc(en)}</span><span class="j">{esc(ja)}</span></div>' for en, ja in data["outcomes"])
    pages = [f'''    <div class="transition-page" data-page-id="lesson-goal" data-act="People and ties">
      <span class="transition-kicker">PEOPLE AND TIES</span>
      <h2 class="transition-title">{esc(data["title"])} <span class="title-ja">({esc(data["ja"])})</span></h2>
      <p class="section-subtitle"><span class="ko">{esc(goal_en)}</span><span class="ja">{esc(goal_ja)}</span></p>
      <div class="known lines">{outcomes}</div>
    </div>
''', article_page(topic_no, data, variant), base.extract_page(canonical, "lesson-style"),
    '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="transition-copy">全部答えなくても大丈夫です。一つの答えをゆっくり広げましょう。</p></div>
''']
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple((f"q{i}", f"QUESTION {i}") for i in range(1, 7))
    pages.extend(question_page(page_id, number, item, variant) for (page_id, number), item in zip(prompt_ids, data["prompts"], strict=True))
    pages.append(base.extract_page(canonical, "feedback"))
    return new_lesson.redepth(head + "\n".join(pages) + foot, output_path(topic_no, variant))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="regenerate only the 18 owned decks")
    args = parser.parse_args()
    assert_preserved()
    for topic_no in TOPIC_NUMBERS:
        for variant in ("accessible", "full"):
            output = output_path(topic_no, variant)
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {output.relative_to(ROOT)}")
    assert_preserved()
    print("18 Freetalking decks generated; FT-49 preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
