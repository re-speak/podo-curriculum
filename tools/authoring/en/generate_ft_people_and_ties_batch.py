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
        "869062e3aa75757c9d778f432b200d625e16313a90c43a1d99de2f7458a2a392",
    ),
    "full": (
        TRACK / "courses/talk-people-and-ties-full/lessons/49-how-accurate-is-your-mbti/lesson.html",
        "55534c6cec0d8a8401c541e77eb7587eed9aa933a252b07c7a13fad6170669a0",
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
 goal=("Let's talk about what helps friendships last as life changes.", "生活が変わっても友情が続く理由について話しましょう。"),
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
  prompt("What makes it last", "続く理由", "What helps a friendship last when life changes?", "生活が変わっても友情が続くために、何が役立ちますか？", ["Which change tests a friendship most?", "What can keep the connection steady?"], full="What enables a friendship to endure as both lives change?", full_ja="お互いの生活が変わっても友情が続くために、何が必要ですか？", full_followups=["Which kind of change tests the relationship most?", "What preserves a sense of connection?"]),
  prompt("How it begins", "始まり方", "How can a strong friendship begin?", "強い友情は、どのように始まるのでしょうか？", ["What gives two people something to talk about?", "When does friendliness become closeness?"], full="How does an ordinary meeting develop into a strong friendship?", full_ja="普通の出会いは、どのように強い友情へ変わるのでしょうか？", full_followups=["What creates the first meaningful connection?", "At what point does friendliness become genuine closeness?"]),
  prompt("Changing over time", "時間による変化", "How can a friendship change without becoming weaker?", "友情は、弱くならずにどのように変化できますか？", ["Which changes are healthy?", "What still needs to feel familiar?"], full="How can a friendship evolve without losing its strength?", full_ja="友情は、強さを失わずにどのように変化していけますか？", full_followups=["Which changes show healthy adaptation?", "What still needs to remain recognizable?"]),
  prompt("Staying connected", "つながりを保つ", "What keeps contact meaningful when both people are busy?", "お互いに忙しいとき、何が連絡を意味のあるものにしますか？", ["How much contact is enough?", "What shows care without creating pressure?"], full="What keeps contact meaningful during demanding periods in both people's lives?", full_ja="お互いの生活が忙しい時期に、何が連絡を意味のあるものにしますか？", full_followups=["How much contact sustains closeness?", "What demonstrates care without becoming an obligation?"]),
  prompt("What damages it", "友情を傷つけるもの", "Which behaviour damages a friendship most?", "どのような行動が、友情をいちばん傷つけますか？", ["Why does that cross a line?", "What would repair require?"], full="Which behaviour is most damaging to a friendship?", full_ja="友情に最も大きな損害を与えるのは、どのような行動ですか？", full_followups=["Why does it cross an important boundary?", "What would meaningful repair require?"]),
  prompt("Drifting apart", "疎遠になる", "Why do some friends drift apart even when nobody did anything wrong?", "誰も悪くなくても、友人同士が疎遠になるのはなぜですか？", ["Which life change reduces contact fastest?", "When is distance simply natural?"], full="Why do some friendships fade even when neither person is at fault?", full_ja="どちらも悪くなくても、友情が薄れていくのはなぜですか？", full_followups=["Which life change most quickly reduces contact?", "When is growing apart a natural transition?"]),
  prompt("Starting again", "関係を戻す", "When is a friendship worth trying to restart?", "友情をもう一度始める価値があるのは、どんなときですか？", ["What could the first message say?", "How can the contact stay low-pressure?"], full="When is a friendship worth trying to revive?", full_ja="友情をもう一度よみがえらせる価値があるのは、どのようなときですか？", full_followups=["What could reopen contact naturally?", "How can renewed contact avoid creating pressure?"]),
  prompt("What you bring", "自分が与えるもの", "What do you bring to a good friendship?", "よい友情に、自分は何を与えていますか？", ["Which contribution comes naturally to you?", "What would you like to do better?"], full="What do you contribute to a strong friendship?", full_ja="強い友情に、自分は何を与えていますか？", full_followups=["Which contribution comes most naturally to you?", "What would you still like to improve?"]),
 ]),
48: topic(
 slug="a-first-impression-that-was-completely-wrong", title="A first impression that was completely wrong", ko="완전히 틀렸던 첫인상", ja="まったく違っていた第一印象",
 goal=("Let's talk about why first impressions change.", "第一印象が変わる理由について話しましょう。"),
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
  prompt("Why it can be wrong", "間違う理由", "Why can a first impression be completely wrong?", "第一印象がまったく間違っていることがあるのは、なぜですか？", ["Which detail can be easy to misread?", "What important context is missing at first?"], full="Why can a confident first impression still be deeply inaccurate?", full_ja="確信のある第一印象でも、大きく間違うことがあるのはなぜですか？", full_followups=["Which detail is especially easy to misinterpret?", "What crucial context is unavailable at first?"]),
  prompt("What shapes it", "印象を作るもの", "Which details shape a first impression fastest?", "どのような細部が、第一印象を最も早く作りますか？", ["Why does that detail feel meaningful?", "How might the setting change it?"], full="Which signals shape an initial judgment most quickly?", full_ja="どのような合図が、最初の判断を最も早く作りますか？", full_followups=["Why does that signal appear revealing?", "How might the surrounding context alter it?"]),
  prompt("Evidence that changes it", "印象を変える証拠", "What kind of evidence can change a first impression?", "どのような証拠が、第一印象を変えることがありますか？", ["Can one action be enough?", "When does a pattern matter more?"], full="What kind of evidence is strong enough to overturn an initial impression?", full_ja="どのような証拠なら、最初の印象を覆すほど強いですか？", full_followups=["When can one action be decisive?", "When is a pattern more persuasive?"]),
  prompt("Fast or slow", "速い変化と遅い変化", "Why do some impressions change quickly while others change slowly?", "すぐ変わる印象と、ゆっくり変わる印象があるのはなぜですか？", ["What makes someone resist new evidence?", "What could speed up the change?"], full="Why are some first impressions revised quickly while others remain resistant?", full_ja="すぐ見直される第一印象と、なかなか変わらない第一印象があるのはなぜですか？", full_followups=["What makes a judgment resistant to contrary evidence?", "What might accelerate a fair revision?"]),
  prompt("Missing context", "足りない背景", "Which missing context makes first impressions unfair?", "どのような背景が足りないと、第一印象が不公平になりますか？", ["Could tiredness or nervousness explain the behaviour?", "What would you want to know before judging?"], full="Which missing context most often makes an initial judgment unfair?", full_ja="どのような背景が欠けると、最初の判断が最も不公平になりやすいですか？", full_followups=["Could fatigue or anxiety explain the behaviour?", "Which fact would you want before reaching a conclusion?"]),
  prompt("The other direction", "逆の変化", "How can a good first impression become worse?", "よい第一印象が、あとで悪くなるのはどのようなときですか？", ["Which warning sign is easy to overlook?", "How many examples would make the change fair?"], full="How can a favourable first impression deteriorate over time?", full_ja="好ましい第一印象が、時間とともに悪くなるのはどのようなときですか？", full_followups=["Which warning sign is commonly overlooked?", "How much evidence would justify the revision?"]),
  prompt("Judging quickly", "すぐ判断すること", "When is a quick first impression useful?", "すぐに持つ第一印象が役立つのは、どんなときですか？", ["When can it become unfair?", "What should make us pause?"], full="When can a rapid first impression be useful?", full_ja="すぐに持つ第一印象が役立つのは、どのようなときですか？", full_followups=["When does speed make the judgment unfair?", "Which signal should make us suspend judgment?"]),
  prompt("Easy to misread", "誤解されやすい点", "Which parts of a person are easiest to misread at first?", "人のどのような部分は、最初に誤解されやすいですか？", ["What impression might quietness create?", "Which quality takes longer to see?"], full="Which aspects of a person are most easily misread during a first meeting?", full_ja="初対面では、人のどのような面が最も誤解されやすいですか？", full_followups=["Which impression can quietness create?", "Which quality usually takes longer to recognize?"]),
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
  prompt("Where the line is", "一人でできる境界", "Which activity feels hardest to do alone?", "どのような活動が、一人ではいちばん難しく感じますか？", ["What makes it different from eating or shopping alone?", "Is the main issue safety, confidence, or enjoyment?"], full="Which activity lies furthest outside your comfort zone when done alone?", full_ja="一人でするとき、どの活動が自分の安心できる範囲から最も遠く感じますか？", full_followups=["What distinguishes it from ordinary solo activities?", "Is the main barrier safety, confidence, or enjoyment?"]),
  prompt("Why it feels bold", "大胆に感じる理由", "What makes a solo activity feel bold?", "一人での活動が大胆に感じられるのはなぜですか？", ["Which social reaction matters most?", "Which practical difficulty matters most?"], full="What makes one solo activity feel significantly bolder than another?", full_ja="一人での活動の中でも、特に大胆に感じるものがあるのはなぜですか？", full_followups=["How strongly do social expectations shape the feeling?", "Which practical obstacle carries the most weight?"]),
  prompt("Just outside the line", "境界の少し外", "Imagine one solo activity just outside your comfort zone. What would happen?", "自分の安心できる範囲を少し超える一人での活動を想像してください。何が起きそうですか？", ["Which moment would feel hardest?", "What could make the experience satisfying?"], full="Imagine a solo activity just beyond your current comfort zone. How might it unfold?", full_ja="今の安心できる範囲を少し超える一人での活動を想像してください。どのように進みそうですか？", full_followups=["Which moment would test you most?", "What could make the experience genuinely rewarding?"]),
  prompt("Freedom and pressure", "自由と負担", "What is the best and hardest part of doing an activity alone?", "何かを一人でするとき、いちばんよい点と難しい点は何ですか？", ["Which decisions become easier?", "Which problem would you rather share?"], full="What are the greatest freedom and the greatest pressure in doing an activity alone?", full_ja="何かを一人でするとき、最大の自由と最大の負担は何ですか？", full_followups=["Which decisions become simpler?", "Which responsibility would you prefer to share?"]),
  prompt("Comfort alone", "一人で平気な理由", "What makes some people comfortable doing more things alone?", "一人で多くのことをしても平気な人がいるのはなぜですか？", ["Which skill reduces uncertainty?", "How can past success change confidence?"], full="What enables some people to act alone with greater confidence?", full_ja="一人でもより自信を持って行動できる人がいるのはなぜですか？", full_followups=["Which skill reduces uncertainty most effectively?", "How does previous success reshape confidence?"]),
  prompt("A moving line", "変わった境界", "How can someone's line for doing things alone change over time?", "一人でできることの境界は、時間とともにどう変わりますか？", ["Which experience could expand it?", "What could make it smaller again?"], full="How can a person's boundary for solo activities shift over time?", full_ja="一人での活動に対する境界は、時間とともにどう変化しますか？", full_followups=["Which experience could expand the boundary?", "What might cause it to contract again?"]),
  prompt("A smaller step", "小さな一歩", "What smaller solo activity could prepare someone for the next one?", "次の挑戦に備えるために、どのような小さな一人での活動が役立ちますか？", ["How could the risk be reduced?", "What would show that the person is ready?"], full="Which smaller solo activity could prepare someone to go further?", full_ja="さらに挑戦するために、どのような小さな一人での活動が準備になりますか？", full_followups=["How could the experiment be made safer?", "Which sign would demonstrate readiness?"]),
  prompt("What would push it", "境界を広げる条件", "What helps expand a person's comfort zone?", "何があれば、人の安心できる範囲を広げられますか？", ["Would information, practice, or company matter most?", "Which boundary should still be respected?"], full="What conditions help expand a person's comfort zone responsibly?", full_ja="どのような条件があれば、人の安心できる範囲を無理なく広げられますか？", full_followups=["Would information, practice, or temporary support matter most?", "Which boundary should remain respected?"]),
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
  prompt("Easy to answer", "答えやすさ", "What makes an opening easy to answer?", "どのような最初の一言なら、答えやすいですか？", ["How specific should the question be?", "What lets the other person keep the reply short?"], full="What makes a small talk question inviting and easy to answer?", full_ja="どのような雑談の質問なら、答えやすく会話に入りやすいですか？", full_followups=["How specific should the opening be?", "What allows a brief reply without awkwardness?"]),
  prompt("A dead end", "続かなかった会話", "What kind of opening makes a conversation die quickly?", "どんな最初の一言だと、会話がすぐ終わりますか？", ["Is the problem the topic or the delivery?", "What might save it once?"], full="What kind of opening causes a conversation to stall immediately?", full_ja="どのような最初の一言だと、会話がすぐ止まりますか？", full_followups=["Is the problem usually the topic or the delivery?", "Which single follow-up might rescue it?"]),
  prompt("Reading the signals", "反応を読む", "Which signals show that a stranger wants to keep talking?", "どのような反応から、相手が会話を続けたいと分かりますか？", ["What can a short answer mean?", "Which signal suggests it is time to stop?"], full="Which signals indicate that a stranger is genuinely open to continuing the conversation?", full_ja="どのような反応から、相手が本当に会話を続けたいと分かりますか？", full_followups=["How should a brief answer be interpreted?", "Which signal suggests a graceful ending is appropriate?"]),
  prompt("When it fails", "失敗したとき", "What do you do when your opening does not work?", "最初の一言がうまくいかないとき、どうしますか？", ["Would you try one more question?", "How would you end politely?"], full="How do you respond when an opening fails to create a conversation?", full_ja="最初の一言から会話が続かなかったとき、どう対応しますか？", full_followups=["When is one more question appropriate?", "How would you close the exchange gracefully?"]),
  prompt("A useful starter", "使えるきっかけ", "What conversation starter could you actually use this week?", "今週、実際に使えそうな会話のきっかけは何ですか？", ["Where could you use it?", "What answer would help you continue?"], full="Which conversation starter could you realistically use this week?", full_ja="今週、現実的に使えそうな会話のきっかけは何ですか？", full_followups=["In which setting could you use it?", "Which reply would give you a natural next question?"]),
 ]),
52: topic(
 slug="how-you-make-up-after-an-argument", title="How you make up after an argument", ko="다툰 뒤 화해하는 방법", ja="けんかのあとの仲直りのしかた",
 goal=("Let's talk about what fair repair after an argument requires.", "けんかのあとに関係を公平に修復するために必要なことを話しましょう。"),
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
  prompt("Who moves first?", "先に動く人", "After an ordinary argument, who should reach out first?", "普通のけんかのあと、どちらが先に連絡するとよいですか？", ["Does reaching out mean accepting all the blame?", "What makes the first move difficult?"], full="After an ordinary argument, who should reach out and initiate contact?", full_ja="普通のけんかのあと、どちらが先に連絡を始めるべきですか？", full_followups=["Does initiating contact imply accepting sole responsibility?", "What makes the first move emotionally difficult?"]),
  prompt("How long", "かかる時間", "How much time helps people talk calmly after an argument?", "けんかのあと、落ち着いて話すためにどのくらい時間が役立ちますか？", ["What should happen during the pause?", "When does waiting make things worse?"], full="How much distance helps a calm conversation become possible after conflict?", full_ja="対立のあと、落ち着いた会話をするためにどのくらい距離を置くとよいですか？", full_followups=["How should the pause be used?", "When does distance begin to deepen the problem?"]),
  prompt("The first message", "最初のメッセージ", "What should the first message after an argument say?", "けんかのあとの最初の連絡では、何を伝えるとよいですか？", ["Should it name the argument immediately?", "How can it avoid sounding defensive?"], full="How should the first message after an argument be worded?", full_ja="けんかのあとの最初の連絡は、どのような言葉で伝えるとよいですか？", full_followups=["Should it identify the disagreement immediately?", "How can the tone avoid sounding defensive?"]),
  prompt("What lies beneath", "表面の下にあること", "What does a small everyday disagreement often hide beneath the surface?", "日常の小さな意見の違いの奥には、何が隠れていることがありますか？", ["Could the real issue be respect, time, or responsibility?", "How can people identify the deeper issue?"], full="What underlying issue can a minor everyday disagreement conceal?", full_ja="日常の小さな意見の違いは、どのような根本的な問題を隠すことがありますか？", full_followups=["Could the real issue involve respect, time, or responsibility?", "How can both people identify the deeper disagreement?"]),
  prompt("What repairs it", "修復に役立つこと", "What makes an apology feel real?", "どんな謝罪なら本気だと感じますか？", ["Which detail should it name?", "What action should follow the words?"], full="What makes an apology feel credible?", full_ja="どのような謝罪なら信頼できると感じますか？", full_followups=["How specific should the apology be?", "Which action should follow the words?"]),
  prompt("Still unresolved", "まだ解決していないこと", "Can some arguments remain unfixed without ending a relationship?", "解決しないけんかがあっても、関係は続けられますか？", ["Which differences can people accept?", "When is a new boundary needed?"], full="Can some disagreements remain unresolved without destroying a relationship?", full_ja="解決しない意見の違いがあっても、関係を壊さずにいられますか？", full_followups=["Which differences can a relationship absorb?", "When does the disagreement require a new boundary?"]),
  prompt("Not every repair", "仲直りしない選択", "When is making up not the right goal?", "仲直りを目標にしないほうがよいのは、どんなときですか？", ["What would need to change first?", "How can someone end contact respectfully?"], full="When is reconciliation not the appropriate goal?", full_ja="仲直りを目標にすることが適切ではないのは、どのようなときですか？", full_followups=["Which condition would need to change first?", "How can someone end contact respectfully?"]),
  prompt("The right way", "よい方法", "What's a fair way to make up after an ordinary argument?", "普通のけんかのあと、公平に仲直りするにはどうすればよいですか？", ["Who should speak first?", "How would you know the repair worked?"], full="What is a fair way to make up after an ordinary argument?", full_ja="普通のけんかのあと、公平に仲直りするにはどのような方法がありますか？", full_followups=["Who should initiate the conversation?", "Which sign would show that repair succeeded?"]),
 ]),
53: topic(
 slug="why-some-friendships-fade", title="Why some friendships fade", ko="어떤 우정이 멀어지는 이유", ja="友情が薄れていく理由",
 goal=("Let's talk about why friendships fade and how people can respond.", "友情が薄れる理由と、その変化への向き合い方について話しましょう。"),
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
  prompt("Changing circles", "変わる人間関係", "Why do people's social circles change over time?", "人間関係は、時間とともになぜ変わるのでしょうか？", ["Which life change has the biggest effect?", "Why can the change happen gradually?"], full="Why do social circles tend to change across different stages of life?", full_ja="人生の段階が変わると、人間関係も変わりやすいのはなぜですか？", full_followups=["Which transition reshapes a social circle most strongly?", "Why can the shift be difficult to notice at first?"]),
  prompt("Changing routines", "変わる習慣", "Which routines make friends see each other more or less often?", "どのような生活習慣によって、友人と会う回数が増えたり減ったりしますか？", ["Which routine is easiest to adjust?", "How can two busy schedules stay connected?"], full="Which routines most strongly increase or reduce contact between friends?", full_ja="どのような生活習慣が、友人同士の連絡を最も増やしたり減らしたりしますか？", full_followups=["Which routine is most realistic to change?", "How can incompatible schedules still leave room for connection?"]),
  prompt("Drifting apart", "疎遠になる", "How can friends drift apart while still caring about each other?", "お互いを大切に思っていても、友人同士が疎遠になるのはなぜですか？", ["What may disappear first: time, routine, or shared interests?", "What can still remain meaningful?"], full="How can two friends grow apart without losing all affection for each other?", full_ja="お互いへの思いを失わなくても、二人の友人が疎遠になるのはなぜですか？", full_followups=["Which connection tends to weaken first?", "What part of the friendship may still retain value?"]),
  prompt("Nobody's fault", "誰も悪くない変化", "When is a fading friendship nobody's fault?", "友情が薄れても、誰も悪くないと言えるのはどんなときですか？", ["Which changes happen without a clear choice?", "Why do people sometimes search for someone to blame?"], full="When is a fading friendship better explained by circumstance than by fault?", full_ja="友情が薄れる理由を、誰かの責任より状況の変化で説明できるのはどんなときですか？", full_followups=["Which circumstances change a relationship without deliberate action?", "Why can assigning blame feel simpler than accepting gradual change?"]),
  prompt("The main cause", "主な原因", "Which matters most: distance, time, or people changing?", "距離、時間、人の変化のうち、どれが最も大きいですか？", ["Can two causes reinforce each other?", "Which one is easiest to overcome?"], full="Which factor matters most: distance, limited time, or personal change?", full_ja="距離、時間の不足、人の変化のうち、どれが最も大きいですか？", full_followups=["How might two factors reinforce each other?", "Which one is most realistic to overcome?"]),
  prompt("Normal or a problem", "自然か問題か", "Is a fading friendship normal, or is it a problem?", "友情が薄れるのは自然なことですか。それとも問題ですか？", ["What makes the difference?", "When does acceptance become avoidance?"], full="Is a fading friendship a normal transition or a problem that deserves attention?", full_ja="友情が薄れるのは自然な変化ですか。それとも向き合うべき問題ですか？", full_followups=["Which condition separates the two?", "When does acceptance become avoidance?"]),
  prompt("Worth renewing", "関係を戻す価値", "When is a faded friendship worth trying to renew?", "薄れた友情をもう一度取り戻そうとする価値があるのは、どんなときですか？", ["What could a low-pressure first message say?", "Which response would show that both people are interested?"], full="What makes a faded friendship worth a genuine attempt at renewal?", full_ja="薄れた友情を本気で取り戻そうとする価値があるのは、どのようなときですか？", full_followups=["How could contact be reopened without creating pressure?", "Which response would suggest mutual interest in rebuilding the connection?"]),
  prompt("Responding to change", "変化への向き合い方", "How should people respond when a friendship fades?", "友情が薄れたとき、人はどのように向き合うとよいですか？", ["Which relationships deserve new effort?", "How can an old friendship still be valued without restarting it?"], full="How can people respond thoughtfully when a friendship begins to fade?", full_ja="友情が薄れ始めたとき、どのように向き合えばよいでしょうか？", full_followups=["Which relationships merit renewed effort?", "How can a friendship remain meaningful without being revived?"]),
 ]),
54: topic(
 slug="the-person-you-talk-to-most", title="The person you talk to most", ko="가장 많이 이야기하는 사람", ja="いちばんよく話す人",
 goal=("Let's talk about how contact patterns shape our relationships.", "連絡のしかたが人間関係に与える影響について話しましょう。"),
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
  prompt("A main contact", "よく話す相手", "What makes someone become the person you talk to most?", "どのようなことから、その人がいちばんよく話す相手になりますか？", ["How much does routine matter?", "Can practical need create closeness?"], full="What causes one person to become someone's primary conversational contact?", full_ja="どのような理由で、ある人がいちばんよく話す相手になるのでしょうか？", full_followups=["How strongly does routine shape that role?", "Can repeated practical contact develop into genuine closeness?"]),
  prompt("Why that person", "その相手である理由", "Why does one contact sometimes become more important than the others?", "ある連絡相手が、ほかの相手より大切になることがあるのはなぜですか？", ["Is the reason closeness, trust, or availability?", "Can that importance change quickly?"], full="Why does one contact sometimes become central within a wider network?", full_ja="多くの連絡先の中で、ある相手が中心になることがあるのはなぜですか？", full_followups=["Does centrality come mainly from trust, availability, or shared need?", "Which change could quickly alter that role?"]),
  prompt("A good rhythm", "よい頻度", "What contact rhythm feels sustainable for a close relationship?", "親しい関係を続けやすい連絡の頻度は、どのくらいですか？", ["How much silence can feel comfortable?", "When does frequent contact become pressure?"], full="What rhythm of contact can sustain closeness without creating pressure?", full_ja="負担を生まずに親しさを保てる連絡の頻度は、どのようなものですか？", full_followups=["How much silence can a strong relationship comfortably hold?", "When can frequent communication begin to feel obligatory?"]),
  prompt("Deeper connection", "関係を深める話題", "Which kinds of conversation deepen a connection?", "どのような会話が、人とのつながりを深めますか？", ["Does depth require personal disclosure?", "Can ordinary daily talk build closeness?"], full="Which kinds of conversation strengthen a relationship over time?", full_ja="どのような会話が、時間をかけて関係を深めますか？", full_followups=["Does a deeper connection always require personal disclosure?", "How can ordinary daily exchanges build trust?"]),
  prompt("Easy and difficult topics", "話しやすい話題と難しい話題", "What makes a topic easy or difficult to discuss with someone?", "ある話題が人と話しやすかったり、話しにくかったりするのはなぜですか？", ["How does trust change the answer?", "Can timing matter more than the topic itself?"], full="What makes certain subjects easy to discuss with one person but difficult with another?", full_ja="同じ話題でも、相手によって話しやすさが変わるのはなぜですか？", full_followups=["How does established trust shape the boundary?", "When does timing matter more than the subject itself?"]),
  prompt("Changing patterns", "変わる連絡のしかた", "Why do communication patterns change over time?", "連絡のしかたが時間とともに変わるのはなぜですか？", ["Which life change has the strongest effect?", "Can a new medium change the relationship too?"], full="Why do patterns of communication evolve as people's circumstances change?", full_ja="生活状況が変わると、連絡のしかたも変化するのはなぜですか？", full_followups=["Which transition has the strongest effect on contact?", "How can a new communication medium alter the relationship itself?"]),
  prompt("Life stages", "人生の段階", "How can a person's main contact change across different life stages?", "人生の段階によって、いちばんよく連絡する相手はどのように変わりますか？", ["Which stage changes the network most?", "What can an old main contact still mean?"], full="How can someone's central contacts shift across different stages of life?", full_ja="人生の段階が変わると、中心となる連絡相手はどのように移り変わりますか？", full_followups=["Which transition tends to reshape the network most?", "What significance can a former central contact retain?"]),
  prompt("Staying in touch", "連絡を続ける", "What helps two people stay in touch without making it a duty?", "義務に感じずに二人が連絡を続けるには、何が役立ちますか？", ["How much silence is comfortable?", "What kind of message is easy to answer?"], full="What helps two people stay in touch without turning contact into an obligation?", full_ja="連絡を義務にせず、二人がつながり続けるには何が役立ちますか？", full_followups=["How much silence can the relationship comfortably hold?", "Which kind of message invites an easy response?"]),
 ]),
55: topic(
 slug="advice-that-stayed-with-you", title="Advice that stayed with you", ko="마음에 남은 조언", ja="心に残っている助言",
 goal=("Let's talk about why some advice stays with people and deserves to be shared.", "心に残る助言と、それを人に伝える価値について話しましょう。"),
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
  prompt("Why it stays", "心に残る理由", "Why does some advice stay with people for years?", "何年たっても心に残る助言があるのはなぜですか？", ["Does the timing matter?", "Can a simple idea stay longer than a complex one?"], full="Why does certain advice remain memorable long after it is first heard?", full_ja="最初に聞いてから長い時間がたっても、心に残る助言があるのはなぜですか？", full_followups=["How strongly does the moment of hearing it matter?", "Why might a simple principle outlast a more complex message?"]),
  prompt("Memorable wording", "記憶に残る言葉", "What makes the wording of advice easy to remember?", "どのような言い方だと、助言を覚えやすくなりますか？", ["Should it be short?", "How can an image or example help?"], full="Which qualities make the wording of advice especially memorable?", full_ja="助言の言い方を特に記憶に残りやすくするのは、どのような特徴ですか？", full_followups=["How much does brevity contribute?", "Why can an image or concrete example strengthen the message?"]),
  prompt("Who says it", "言う人", "Why does the source of advice matter?", "誰から聞くかによって、助言の受け取り方が変わるのはなぜですか？", ["What creates trust in the speaker?", "Could the same words feel different from someone else?"], full="Why can the source of advice matter as much as the words themselves?", full_ja="助言では、言葉そのものと同じくらい、誰が言ったかが重要になるのはなぜですか？", full_followups=["What gives the speaker credibility?", "How might identical advice feel different from another source?"]),
  prompt("The right moment", "意味を持つ時", "When does advice become relevant to someone's life?", "助言がその人の生活に関係するようになるのは、どんなときですか？", ["Can useful advice arrive too early?", "What makes people notice it later?"], full="What makes advice suddenly relevant at a particular moment in someone's life?", full_ja="ある瞬間に、助言が急に自分に関係するように感じられるのはなぜですか？", full_followups=["Can valuable advice be given before someone is ready for it?", "Which change can make an old message newly visible?"]),
  prompt("Understanding later", "あとで分かること", "Why does some advice make sense only later?", "助言の意味があとになって分かることがあるのはなぜですか？", ["Which experience can change its meaning?", "Does understanding require agreeing?"], full="Why can experience make old advice clearer in hindsight?", full_ja="経験を重ねると、昔の助言が振り返って分かりやすくなるのはなぜですか？", full_followups=["Which kind of experience can change its interpretation?", "Can someone understand advice without ultimately agreeing with it?"]),
  prompt("When it helps", "役立つ時", "When does advice help, and when can it fail?", "助言はどんなときに役立ち、どんなときに役立たないのでしょうか？", ["How much does the situation matter?", "When should advice be adapted?"], full="Which conditions make advice useful, and which conditions expose its limits?", full_ja="どのような条件で助言は役立ち、どのような条件で限界が見えますか？", full_followups=["How strongly does context determine its usefulness?", "When should the underlying idea be adapted rather than followed literally?"]),
  prompt("Worth sharing", "伝える価値", "When is advice valuable enough to pass on?", "助言を人に伝える価値があるのは、どんなときですか？", ["What should you know about their situation first?", "How can you share it without sounding controlling?"], full="What makes a piece of advice valuable enough to pass on?", full_ja="ある助言を人に伝える価値があると判断するのは、どのようなときですか？", full_followups=["Which part of the person's situation should be understood first?", "How can advice be offered without becoming an instruction?"]),
  prompt("Advice ignored", "助言に従わない理由", "Why do people sometimes ignore sound advice?", "よい助言でも、人が従わないことがあるのはなぜですか？", ["Can the right message come at the wrong time?", "When is choosing differently reasonable?"], full="Why might people reject advice that appears sensible?", full_ja="もっともらしい助言でも、人が受け入れないことがあるのはなぜですか？", full_followups=["How can timing weaken an otherwise sound message?", "When can a different choice be reasonable despite the advice?"]),
 ]),
56: topic(
 slug="the-person-you-would-call-in-an-emergency", title="The person you would call in an emergency", ko="위급할 때 전화할 사람", ja="緊急時に電話する人",
 goal=("Let's talk about practical support and a reliable emergency network.", "実際に役立つ支えと、信頼できる緊急時の支援体制について話しましょう。"),
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
  prompt("First call", "最初の連絡先", "In an emergency, which need should determine the first call?", "緊急時には、どのような必要によって最初の連絡先を決めるべきですか？", ["Which problems require a professional service first?", "When is a trusted person the better first contact?"], full="In an emergency, which immediate need should determine the first point of contact?", full_ja="緊急時には、どのような差し迫った必要によって最初の連絡先を決めるべきですか？", full_followups=["Which situations require professional help before personal support?", "When is a trusted individual the more useful first contact?"]),
  prompt("The right first contact", "適切な最初の連絡先", "What makes a person or service the right first contact in an emergency?", "緊急時に、ある人やサービスが適切な最初の連絡先になるのはなぜですか？", ["What could they do immediately?", "Where would their ability end?"], full="Which qualities make a person or service the appropriate first point of contact in an emergency?", full_ja="緊急時の最初の連絡先として人やサービスを選ぶとき、どのような条件が重要ですか？", full_followups=["Which immediate need could they meet?", "Where would their expertise or role end?"]),
  prompt("What you would say", "伝えること", "What information would you give first?", "最初にどんな情報を伝えますか？", ["Which detail would help them act?", "What could wait until later?"], full="Which information would you communicate first?", full_ja="最初にどの情報を伝えますか？", full_followups=["Which detail would enable useful action?", "Which information could safely wait?"]),
  prompt("First steps", "最初の行動", "Imagine an ordinary, safe emergency. What should happen first?", "身近で安全に話せる緊急事態を想像してください。最初に何をするべきですか？", ["Which information is needed immediately?", "Who or which service should receive it?"], full="Imagine a manageable emergency. What sequence of first steps would be most effective?", full_ja="対応可能な緊急事態を想像してください。最初にどのような順序で行動するのが効果的ですか？", full_followups=["Which information must be established immediately?", "Which person or service should receive that information first?"]),
  prompt("A support role", "支える役割", "Which emergency support role can an ordinary person handle well?", "緊急時に、一般の人がうまく担える支援の役割は何ですか？", ["What practical help could they provide?", "When should they involve a professional?"], full="Which useful role can a non-professional realistically play during an emergency?", full_ja="緊急時に、専門家ではない人が現実的に担える役割は何ですか？", full_followups=["Which practical need could they reliably meet?", "At what point should responsibility pass to a professional?"]),
  prompt("Changing contacts", "変わる連絡先", "Why can a person's first-choice contact change over time?", "最初に連絡する相手が、時間とともに変わるのはなぜですか？", ["Which life change can reorder the network?", "What makes a contact remain reliable?"], full="Why might someone's preferred emergency contact change as circumstances evolve?", full_ja="状況の変化によって、緊急時に最初に連絡したい相手が変わるのはなぜですか？", full_followups=["Which transition can most strongly reorder the network?", "Which qualities allow one contact to remain dependable over time?"]),
  prompt("Distance", "距離", "How much does distance matter in an emergency?", "緊急時に、距離はどのくらい重要ですか？", ["Which help requires someone nearby?", "Which help can still come from far away?"], full="How does physical distance change the value of an emergency contact?", full_ja="物理的な距離は、緊急時の連絡先の価値をどのように変えますか？", full_followups=["Which forms of help require proximity?", "Which forms of support remain possible at a distance?"]),
  prompt("A stronger network", "より強い支援体制", "What could make a support network of people and services more reliable before an emergency?", "緊急事態の前に、人やサービスを含む支援体制をもっと確かにするには何ができますか？", ["Which contact detail should be easy to find?", "Which person or service needs a clear role?"], full="What would make a support network of people and services more resilient before an emergency occurs?", full_ja="緊急事態が起きる前に、人やサービスを含む支援体制をもっと強くするには何が必要ですか？", full_followups=["Which information should be immediately accessible?", "Which person's or service's role or limit should be clarified in advance?"]),
 ]),
}


CLAIM_ORDER = {number: tuple(f"{number}-{index:02d}" for index in range(1, 11)) for number in TOPIC_NUMBERS}
VOCABULARY = {
 47: {"new": "drift apart|疎遠になる", "recycled": "friend|友だち|CORE-2", "assumed": "friendship|友情; meet|出会う; change|変わる; listen|話を聞く; care|気にかける", "receptive": "put up with|我慢する; resentment|言えない不満; static|変化しない"},
 48: {"new": "first impression|第一印象", "recycled": "", "assumed": "person|人; seem|〜のように見える; think|思う; change|変わる; wrong|間違った", "receptive": "misleading|誤解を招く; candid|率直な; turn out|実際には〜だとわかる"},
 50: {"new": "comfort zone|安心してできる範囲", "recycled": "", "assumed": "alone|一人で; eat|食べる; cinema|映画館; travel|旅行する; safety|安全", "receptive": "autonomy|自分で決める自由; attainable|実現できそうな"},
 51: {"new": "small talk|雑談; conversation starter|会話のきっかけ", "recycled": "", "assumed": "stranger|知らない人; ask|聞く; conversation|会話; answer|答える; busy|忙しい", "receptive": "intrusive|立ち入りすぎた; low-pressure|負担の少ない"},
 52: {"new": "make up|仲直りする; reach out|連絡を取る", "recycled": "", "assumed": "argument|けんか; contact|連絡する; first|先に; apology|謝罪; relationship|関係", "receptive": "accountability|責任を引き受けること; reconciliation|仲直り"},
 53: {"new": "fade|薄れていく", "recycled": "drift apart|疎遠になる|FT-47", "assumed": "friendship|友情; five years ago|5年前; distance|距離; time|時間; fault|責任", "receptive": "dormant|休んでいる; diverge|別の方向へ進む"},
 54: {"new": "stay in touch|連絡を取り続ける", "recycled": "", "assumed": "message|メッセージを送る; talk|話す; person|人; often|よく; five years ago|5年前", "receptive": "logistical|予定調整の; intimate|親密な"},
 55: {"new": "pass on|人に伝える", "recycled": "", "assumed": "advice|助言; say|言う; remember|覚えている; understand|理解する; help|役立つ", "receptive": "in hindsight|あとから考えると; decisive|断定的な"},
 56: {"new": "support network|人やサービスを含む支援体制", "recycled": "", "assumed": "call|電話する; person|人; help|助け; tonight|今夜; distance|距離; emergency|緊急時; reliable|信頼できる", "receptive": "resilient|立て直しやすい; expertise|専門性"},
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
      <div class="fb" data-fb="{variant}-{page_id}" data-fb-spoken-label="Student's sentence"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'''
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
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-21")
    head = set_complete(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])
    goal_en, goal_ja = data["goal"]
    pages = [base.ft_contract.goal_page(
        title=data["title"], title_ja=data["ja"],
        topic_en=goal_en, topic_ja=goal_ja,
        data_act="People and ties", kicker="PEOPLE AND TIES",
    ), article_page(topic_no, data, variant), base.extract_page(canonical, "lesson-style"),
    '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of your answers.</span><span class="ja">全部の質問に答える必要はありません。答えの中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Treat these pages as a pool, not a sequence. React or share briefly before choosing the next prompt, skip freely, and move to feedback with 2–3 minutes left.</div></div>
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
