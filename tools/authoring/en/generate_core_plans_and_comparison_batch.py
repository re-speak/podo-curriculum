#!/usr/bin/env python3
"""Generate the missing CORE-37--47 plans-and-comparison lessons.

CORE-45 is an approved golden deck and is deliberately outside this generator.
Every semantic field below is course-owned: the shared Core renderer supplies
markup, but never invents meanings, choices, rules, dialogues, or native tips.
"""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_core_course_batch as core
import generate_core_first_exchanges_1_batch as shell
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-plans-and-comparison"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
NUMBERS = (37, 38, 39, 40, 41, 42, 43, 44, 46, 47)


def rows(*items):
    return items


LESSONS = {
    37: dict(
        slug="im-going-to-look-for-a-new-job", title="I'm going to look for a new job",
        ko="새 직장을 알아볼 거예요", ja="新しい仕事を探すつもりです",
        goal=("Exchange plans that were decided before this conversation.", "この会話の前に決めた予定を伝え合いましょう。"),
        p1=rows(
            ("I'm {t}going to look for{/t} a new job.", "新しい仕事を{t}探すつもりです{/t}。", "I'm going to|look for|a new job."),
            ("I'm {t}going to update{/t} my résumé.", "履歴書を{t}更新するつもりです{/t}。", "I'm going to|update|my résumé."),
            ("I'm {t}going to take{/t} an English course.", "英語の講座を{t}受けるつもりです{/t}。", "I'm going to|take|an English course."),
            ("I'm {t}going to move{/t} next month.", "来月{t}引っ越すつもりです{/t}。", "I'm going to|move|next month."),
        ),
        p2=rows(
            ("{t}What are you going to do{/t} about it?", "それについて{t}どうするつもりですか{/t}？", "What are you going to|do|about it?"),
            ("{t}What are you going to buy{/t} for the trip?", "旅行のために{t}何を買うつもりですか{/t}？", "What are you going to|buy|for the trip?"),
            ("{t}What are you going to study{/t} next?", "次は{t}何を勉強するつもりですか{/t}？", "What are you going to|study|next?"),
            ("{t}What are you going to cook{/t} tonight?", "今夜は{t}何を作るつもりですか{/t}？", "What are you going to|cook|tonight?"),
        ),
        omit_choice=(1, 2),
        rules=(("Keep going to before the planned action.", "前から決めている行動の前に going to を置きます。"), ("Move are before you, then keep going to before the action.", "質問では are を you の前に移し、行動の前には going to を置きます。")),
        prompt=("What is one change you would like to make in the next year? Why?", "これから一年で変えたいことは何ですか？理由も教えてください。"),
    ),
    38: dict(
        slug="let-me-help", title="Let me help", ko="제가 도와드릴게요", ja="私が手伝います",
        goal=("Offer help now and make one promise with a deadline.", "その場で手伝いを申し出て、期限つきの約束を一つしましょう。"),
        p1=rows(
            ("{t}Let me carry{/t} that for you.", "それ、{t}私が運びますよ{/t}。", "Let me|carry that|for you."),
            ("{t}Let me open{/t} the door for you.", "ドアは{t}私が開けますよ{/t}。", "Let me|open the door|for you."),
            ("{t}Let me check{/t} the time for you.", "時間は{t}私が確認します{/t}。", "Let me|check the time|for you."),
            ("{t}Let me call{/t} the hotel for you.", "ホテルには{t}私が電話します{/t}。", "Let me|call the hotel|for you."),
        ),
        p2=rows(
            ("{t}Don’t worry, I’ll send it{/t} by noon.", "心配しないで、正午までに{t}送ります{/t}。", "Don't worry,|I'll send it|by noon."),
            ("{t}Don’t worry, I’ll call you{/t} by six.", "心配しないで、6時までに{t}電話します{/t}。", "Don't worry,|I'll call you|by six."),
            ("{t}Don’t worry, I’ll finish it{/t} by Friday.", "心配しないで、金曜日までに{t}終わらせます{/t}。", "Don't worry,|I'll finish it|by Friday."),
            ("{t}Don’t worry, I’ll bring it{/t} by tomorrow.", "心配しないで、明日までに{t}持ってきます{/t}。", "Don't worry,|I'll bring it|by tomorrow."),
        ),
        omit_choice=(1, 2),
        rules=(("Use Let me plus a plain verb to offer to do the action yourself.", "自分がその行動をすると申し出るときは Let me のあとに動詞の原形を置きます。"), ("Use I’ll for a decision you make as you speak, then name the deadline.", "話しながら今決めたことには I’ll を使い、そのあとに期限を伝えます。")),
        prompt=("What kind of help do you appreciate most when you're busy?", "忙しいとき、どんな手助けが一番ありがたいですか？"),
    ),
    39: dict(
        slug="i-might-be-late", title="I might be late", ko="늦을지도 몰라요", ja="遅れるかもしれません",
        goal=("Warn about an uncertain problem and offer a fallback.", "起こるか分からない問題を伝えて、代わりの案を出しましょう。"),
        p1=rows(
            ("I {t}might be{/t} a bit late.", "少し{t}遅れるかもしれません{/t}。", "I|might be|a bit late."),
            ("I {t}might miss{/t} the train.", "電車に{t}乗り遅れるかもしれません{/t}。", "I|might miss|the train."),
            ("I {t}might need{/t} more time.", "もう少し時間が{t}必要かもしれません{/t}。", "I|might need|more time."),
            ("I {t}might stay{/t} home.", "家に{t}いるかもしれません{/t}。", "I|might stay|home."),
        ),
        p2=rows(
            ("{t}If you are, I’ll wait{/t} outside.", "{t}もしそうなら、外で待ちます{/t}。", "If you are,|I'll wait|outside."),
            ("{t}If you’re busy, I’ll call{/t} later.", "{t}もし忙しいなら、あとで電話します{/t}。", "If you're busy,|I'll call|later."),
            ("{t}If the train is late, I’ll wait{/t} here.", "{t}もし電車が遅れたら、ここで待ちます{/t}。", "If the train is late,|I'll wait|here."),
            ("{t}If the café is full, I’ll go{/t} somewhere else.", "{t}もしカフェが満席なら、別の場所へ行きます{/t}。", "If the café is full,|I'll go|somewhere else."),
        ),
        omit_choice=(2,),
        rules=(("Put a plain verb after might.", "might のあとは動詞の原形を置きます。"), ("Use If for the uncertain condition and I’ll for your response.", "起こるか分からない条件には If、その場合の対応には I’ll を使います。")),
        prompt=("Do you usually make a backup plan? Why or why not?", "普段、代わりの案を用意しますか？その理由も教えてください。"),
    ),
    40: dict(
        slug="you-should-get-some-rest", title="You should get some rest", ko="좀 쉬는 게 좋겠어요", ja="少し休んだほうがいいですよ",
        goal=("Give ordinary advice and say when action becomes necessary.", "ふつうの助言をして、いつ行動が必要になるかを伝えましょう。"),
        p1=rows(
            ("You {t}should get{/t} some rest.", "少し{t}休んだほうがいいです{/t}。", "You should|get some rest."),
            ("You {t}should drink{/t} some water.", "水を少し{t}飲んだほうがいいです{/t}。", "You should|drink some water."),
            ("You {t}should go{/t} home early.", "早めに家へ{t}帰ったほうがいいです{/t}。", "You should|go home early."),
            ("You {t}should sleep{/t} more tonight.", "今夜はもっと{t}寝たほうがいいです{/t}。", "You should|sleep more tonight."),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("{t}If it gets worse, you need to see{/t} a doctor.", "{t}悪化したら、医師に診てもらう必要があります{/t}。", "If it gets worse,|you need to|see a doctor."),
            ("{t}If you feel worse, you need to get help{/t}.", "{t}もっと具合が悪くなったら、助けを求める必要があります{/t}。", "If you feel worse,|you need to|get help."),
            ("{t}If you feel worse, you need to call home{/t}.", "{t}もっと具合が悪くなったら、家に電話する必要があります{/t}。", "If you feel worse,|you need to|call home."),
            ("{t}If it gets worse, you need to stop walking{/t}.", "{t}悪化したら、歩くのをやめる必要があります{/t}。", "If it gets worse,|you need to|stop walking."),
        ),
        omit_choice=(2,),
        rules=(("Use should plus a plain verb for an ordinary recommendation.", "ふつうの助言には should と動詞の原形を使います。"), ("Use need to when the action becomes necessary, not just a good idea.", "よい考えというだけでなく必要になった行動には need to を使います。")),
        prompt=("What's the best advice someone has ever given you?", "今までにもらった中で、一番よかった助言は何ですか？"),
    ),
    41: dict(
        slug="you-have-to-show-id", title="You have to show ID", ko="신분증을 보여줘야 해요", ja="身分証を見せる必要があります",
        goal=("Distinguish a requirement from something optional.", "必要なことと、しなくてもよいことを区別しましょう。"),
        p1=rows(
            ("You {t}have to show{/t} your ID.", "身分証を{t}見せる必要があります{/t}。", "You have to|show your ID."),
            ("You {t}have to wear{/t} a badge.", "バッジを{t}着ける必要があります{/t}。", "You have to|wear a badge."),
            ("You {t}have to book{/t} a time slot.", "時間枠を{t}予約する必要があります{/t}。", "You have to|book a time slot."),
            ("You {t}have to pay{/t} at the desk.", "受付で{t}支払う必要があります{/t}。", "You have to|pay at the desk."),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("But you {t}don't have to book{/t} ahead.", "でも、前もって{t}予約する必要はありません{/t}。", "But|you don't have to|book ahead."),
            ("But you {t}don't have to bring{/t} a photo.", "でも、写真を{t}持ってくる必要はありません{/t}。", "But|you don't have to|bring a photo."),
            ("But you {t}don't have to pay{/t} online.", "でも、オンラインで{t}支払う必要はありません{/t}。", "But|you don't have to|pay online."),
            ("But you {t}don't have to print{/t} the ticket.", "でも、チケットを{t}印刷する必要はありません{/t}。", "But|you don't have to|print the ticket."),
        ),
        omit_choice=(1, 2),
        rules=(("Use have to before a plain verb when a rule requires the action.", "決まりで必要な行動には have to と動詞の原形を使います。"), ("Don’t have to means optional. Mustn’t means forbidden; the two meanings are different.", "don’t have to は「しなくてもよい」、mustn’t は「してはいけない」です。この二つは意味が違います。")),
        prompt=("What is one rule you think makes life better? Why?", "生活をよくすると思う決まりは何ですか？理由も教えてください。"),
    ),
    42: dict(
        slug="dont-you-like-it", title="Don't you like it?", ko="그거 안 좋아해요?", ja="それ、好きじゃないんですか？",
        goal=("Answer a negative question without reversing the fact.", "否定疑問に、事実を逆にせず答えましょう。"),
        p1=rows(
            ("{t}Actually, I do.{/t} I {t}watch{/t} it every week.", "「この番組、好きじゃないんですか？」→ {t}いえ、好きです。{/t}毎週{t}見ています{/t}。", "Actually,|I do.|I watch it every week."),
            ("{t}Actually, I do.{/t} I {t}drink{/t} it every morning.", "「コーヒー、飲まないんですか？」→ {t}いえ、飲みます。{/t}毎朝{t}飲んでいます{/t}。", "Actually,|I do.|I drink it every morning."),
            ("{t}Actually, I do.{/t} I {t}work{/t} there on Fridays.", "「そこで働いていないんですか？」→ {t}いえ、働いています。{/t}金曜日はそこで{t}働いています{/t}。", "Actually,|I do.|I work there on Fridays."),
            ("{t}Actually, I do.{/t} I {t}cook{/t} it at home.", "「これ、作らないんですか？」→ {t}いえ、作ります。{/t}家で{t}作っています{/t}。", "Actually,|I do.|I cook it at home."),
        ),
        p2=rows(
            ("No, {t}I don’t.{/t} I {t}prefer comedies{/t}.", "「ドラマのほうが好きじゃないんですか？」→ {t}はい、好きではありません。{/t}{t}コメディーのほうが好きです{/t}。", "No,|I don't.|I prefer comedies."),
            ("No, {t}I don’t.{/t} I {t}prefer tea{/t}.", "「コーヒーのほうが好きじゃないんですか？」→ {t}はい、好きではありません。{/t}{t}紅茶のほうが好きです{/t}。", "No,|I don't.|I prefer tea."),
            ("No, {t}I don’t.{/t} I {t}prefer the other shop{/t}.", "「この店、好きじゃないんですか？」→ {t}はい、好きではありません。{/t}{t}もう一方の店のほうが好きです{/t}。", "No,|I don't.|I prefer the other shop."),
            ("No, {t}I don’t.{/t} I {t}prefer soup{/t}.", "「このサラダ、好きじゃないんですか？」→ {t}はい、好きではありません。{/t}{t}スープのほうが好きです{/t}。", "No,|I don't.|I prefer soup."),
        ),
        omit_choice=(1,),
        rules=(("Answer the fact: use I do when the positive fact is true.", "質問が否定形でも、肯定の事実が正しければ I do で答えます。"), ("Use I don’t only when the negative fact is true.", "否定の事実が正しいときだけ I don’t で答えます。")),
        prompt=("Have you ever misunderstood someone's yes or no? What happened?", "相手の yes や no を誤解したことはありますか？何がありましたか？"),
    ),
    43: dict(
        slug="its-a-small-quiet-cafe", title="It's a small, quiet café", ko="작고 조용한 카페예요", ja="小さくて静かなカフェです",
        goal=("Describe one thing with two useful details and its location.", "ものを役立つ二つの特徴と場所で説明しましょう。"),
        p1=rows(
            ("It’s a {t}small, quiet{/t} place.", "{t}小さくて静かな{/t}場所です。", "It's|a small, quiet place."),
            ("It’s a {t}bright, clean{/t} room.", "{t}明るくてきれいな{/t}部屋です。", "It's|a bright, clean room."),
            ("It’s a {t}small, friendly{/t} café.", "{t}小さくて親しみやすい{/t}カフェです。", "It's|a small, friendly café."),
            ("It’s a {t}big, busy{/t} shop.", "{t}大きくてにぎやかな{/t}店です。", "It's|a big, busy shop."),
        ),
        omit_reorder=(1,),
        omit_choice=(1, 2),
        p2=rows(
            ("It’s {t}near the station{/t}.", "{t}駅の近くです{/t}。", "It's|near|the station."),
            ("It’s {t}near the café{/t}.", "{t}カフェの近くです{/t}。", "It's|near|the café."),
            ("It’s {t}near the hotel{/t}.", "{t}ホテルの近くです{/t}。", "It's|near|the hotel."),
            ("It’s {t}near the bank{/t}.", "{t}銀行の近くです{/t}。", "It's|near|the bank."),
        ),
        rules=(("Put both adjectives before the noun; adjectives do not take plural -s.", "二つの形容詞は名詞の前に置き、複数でも形容詞に -s はつけません。"), ("Put near before the place you use as the landmark.", "目印にする場所の前に near を置きます。")),
        prompt=("What place makes you feel comfortable right away? Why?", "すぐに居心地がよいと感じる場所はどこですか？理由も教えてください。"),
    ),
    44: dict(
        slug="its-too-small", title="It's too small", ko="너무 작아요", ja="小さすぎます",
        goal=("Reject an option because it crosses a practical limit.", "実用上の限度を超えている理由を伝えて、選択肢を断りましょう。"),
        p1=rows(
            ("It’s {t}too small{/t} for me.", "私には{t}小さすぎます{/t}。", "It's|too small|for me."),
            ("It’s {t}too expensive{/t} for us.", "私たちには{t}高すぎます{/t}。", "It's|too expensive|for us."),
            ("It’s {t}too hot{/t} in here.", "ここは{t}暑すぎます{/t}。", "It's|too hot|in here."),
            ("It’s {t}too crowded{/t} for me.", "私には{t}混みすぎています{/t}。", "It's|too crowded|for me."),
        ),
        p2=rows(
            ("This one {t}isn’t big enough{/t}.", "これは{t}十分な大きさではありません{/t}。", "This one|isn't big enough."),
            ("This one {t}isn’t cheap enough{/t}.", "これは{t}十分安くありません{/t}。", "This one|isn't cheap enough."),
            ("This room {t}isn’t quiet enough{/t}.", "この部屋は{t}十分静かではありません{/t}。", "This room|isn't quiet enough."),
            ("This bag {t}isn’t light enough{/t}.", "このかばんは{t}十分軽くありません{/t}。", "This bag|isn't light enough."),
        ),
        omit_reorder=(2,),
        omit_choice=(1,),
        rules=(("Put too before the adjective when the amount causes a problem.", "程度が問題になるときは、形容詞の前に too を置きます。"), ("Put enough after the adjective when the amount falls short.", "程度が足りないときは、形容詞のあとに enough を置きます。")),
        prompt=("What is something you bought that almost worked—but not quite?", "買ったものの中で、惜しいけれど少し合わなかったものは何ですか？"),
    ),
    46: dict(
        slug="its-the-best-one-here", title="It's the best one here", ko="여기서 이게 제일 좋아요", ja="ここではこれが一番いいです",
        goal=("Identify the best option and state a preference.", "一番よい選択肢を示して、自分の好みを伝えましょう。"),
        p1=rows(
            ("It’s {t}the best{/t} one here.", "ここではこれが{t}一番いい{/t}です。", "It's|the best one|here."),
            ("It’s {t}the cheapest{/t} one here.", "ここではこれが{t}一番安い{/t}です。", "It's|the cheapest one|here."),
            ("It’s {t}the fastest{/t} one here.", "ここではこれが{t}一番速い{/t}です。", "It's|the fastest one|here."),
            ("It’s {t}the most comfortable{/t} one here.", "ここではこれが{t}一番快適{/t}です。", "It's|the most comfortable one|here."),
        ),
        p2=rows(
            ("I {t}prefer this one to{/t} that one.", "{t}あちらよりこちらのほうが好きです{/t}。", "I prefer|this one|to|that one."),
            ("I {t}prefer the window seat to{/t} the aisle seat.", "{t}通路側より窓側の席のほうが好きです{/t}。", "I prefer|the window seat|to|the aisle seat."),
            ("I {t}prefer the train to{/t} the bus.", "{t}バスより電車のほうが好きです{/t}。", "I prefer|the train|to|the bus."),
            ("I {t}prefer the small room to{/t} the big room.", "{t}大きい部屋より小さい部屋のほうが好きです{/t}。", "I prefer|the small room|to|the big room."),
        ),
        omit_choice=(2,),
        rules=(("Use the before every superlative. Add -est to short adjectives, put most before longer adjectives, and remember good becomes best.", "最上級の前には必ず the を置きます。短い形容詞には -est をつけ、長い形容詞の前には most を置き、good は best に変わることも覚えましょう。"), ("Use prefer A to B, not prefer A than B.", "A と B の好みを比べるときは prefer A to B の形にします。")),
        prompt=("When is the cheapest option not the best option?", "一番安い選択肢が一番よいとは限らないのは、どんなときですか？"),
    ),
    47: dict(
        slug="i-was-bored-during-the-movie", title="I was bored during the movie",
        ko="영화 보는 동안 지루했어요", ja="映画の間、退屈でした",
        goal=("Describe your reaction and the thing that caused it.", "自分の反応と、その原因になったものを説明しましょう。"),
        p1=rows(
            ("I was {t}bored{/t} during the movie.", "映画の間、私は{t}退屈していました{/t}。", "I was|bored|during the movie."),
            ("I was {t}excited{/t} during the game.", "試合の間、私は{t}わくわくしていました{/t}。", "I was|excited|during the game."),
            ("I was {t}surprised{/t} by the ending.", "結末に私は{t}驚きました{/t}。", "I was|surprised|by the ending."),
            ("I was {t}tired{/t} after the trip.", "旅行のあと、私は{t}疲れていました{/t}。", "I was|tired|after the trip."),
        ),
        p2=rows(
            ("The movie was really {t}boring{/t}.", "その映画は本当に{t}退屈でした{/t}。", "The movie|was really|boring."),
            ("The game was really {t}exciting{/t}.", "その試合は本当に{t}わくわくするものでした{/t}。", "The game|was really|exciting."),
            ("The ending was really {t}surprising{/t}.", "その結末は本当に{t}驚くものでした{/t}。", "The ending|was really|surprising."),
            ("The trip was really {t}tiring{/t}.", "その旅行は本当に{t}疲れるものでした{/t}。", "The trip|was really|tiring."),
        ),
        rules=(("Use -ed for the person who experiences the feeling.", "その気持ちを感じた人には -ed の形を使います。"), ("Use -ing for the thing that causes the feeling.", "その気持ちを起こさせるものには -ing の形を使います。")),
        prompt=("What movie, game, or trip gave you a strong reaction? Why?", "強く心を動かされた映画、試合、旅行は何ですか？理由も教えてください。"),
    ),
}


VOCAB = {
    37: dict(new="look for|探す; new job|新しい仕事; update|更新する; résumé|履歴書; move|引っ越す; next month|来月", recycled="", assumed="job|仕事; buy|買う; study|勉強する; cook|料理する; course|講座; online course|オンライン講座; plan|予定; English|英語; trip|旅行; tonight|今夜; about it|それについて", receptive="at some point|いつか; we'll see|どうなるか見てみよう; manager|上司; change jobs|転職する"),
    38: dict(new="noon|正午; bring|持ってくる; printer|プリンター", recycled="hotel|ホテル|CORE-7", assumed="carry|運ぶ; carry the box|箱を運ぶ; send|送る; send the files|ファイルを送る; finish|終える; call|電話する; box|箱; file|ファイル; door|ドア; email|メール; Friday|金曜日; tomorrow|明日; time|時間; need|必要とする", receptive="no rush|急がなくていい; I've got it|私に任せて; right away|すぐに; see you then|では、そのときに"),
    39: dict(new="might|〜かもしれない; a bit late|少し遅れる; miss|乗り遅れる; somewhere else|別の場所", recycled="busy|忙しい|CORE-30; café|カフェ|CORE-7", assumed="train|電車; wait|待つ; call|電話する; time|時間; plan|予定; concert|コンサート; home|家", receptive="just in case|念のため; let me know|知らせて; may|〜かもしれない; probably|たぶん"),
    40: dict(new="get some rest|少し休む; get worse|悪化する; get help|助けを求める; stop walking|歩くのをやめる", recycled="", assumed="need|必要とする; sleep|寝る; call|電話する; doctor|医師; water|水; home|家; night|夜; tonight|今夜", receptive="take care|お大事に; if I were you|私なら; maybe|たぶん"),
    41: dict(new="ID|身分証; badge|バッジ; book|予約する; time slot|時間枠; entrance|入口; print|印刷する; online|オンラインで", recycled="ticket|チケット|CORE-5; bring|持ってくる|CORE-38", assumed="ahead|前もって; photo|写真; museum|博物館; desk|受付", receptive="optional|任意の; required|必要な; you're allowed to|〜してよい; that's not allowed|それは禁止; mustn't|〜してはいけない; no need to|〜する必要はない"),
    42: dict(new="prefer|〜のほうが好き; documentary|ドキュメンタリー", recycled="coffee|コーヒー|CORE-9; shop|店|CORE-10", assumed="watch|見る; work|働く; cook|料理する; soup|スープ; comedy|コメディー; drama|ドラマ; TV|テレビ; show|番組; tea|紅茶; Friday|金曜日", receptive="negative question|否定疑問; actually|いえ・実は; not really|あまり"),
    43: dict(new="small|小さい; quiet|静かな; bright|明るい; clean|きれいな; friendly|親しみやすい; big|大きい", recycled="busy|忙しい・にぎやかな|CORE-30; café|カフェ|CORE-7; station|駅|CORE-7; hotel|ホテル|CORE-7; bank|銀行|CORE-7; restaurant|レストラン|CORE-10; shop|店|CORE-10", assumed="room|部屋; place|場所; apartment|アパート", receptive="a little|少し; not far from here|ここから遠くない; cozy|居心地のよい; peaceful|落ち着いた"),
    44: dict(new="enough|十分に; fit|合う; limit|限度; light|軽い; crowded|混んでいる; carry-on|機内持ち込み手荷物; cheap|安い", recycled="small|小さい|CORE-43; big|大きい|CORE-43; expensive|高い|CORE-19; hot|暑い|CORE-8; quiet|静かな|CORE-43; bag|かばん|CORE-5", assumed="size|サイズ; hotel|ホテル; room|部屋", receptive="it'll do|これで間に合う; not quite|あと少し; really|本当に"),
    46: dict(new="best|一番よい; bakery|パン屋; chocolate cake|チョコレートケーキ; fruit tart|フルーツタルト; window seat|窓側の席; aisle seat|通路側の席", recycled="prefer|〜のほうが好き|CORE-42; option|選択肢|CORE-45; cheap|安い|CORE-44; fast|速い|CORE-45; comfortable|快適な|CORE-45; hotel|ホテル|CORE-7; café|カフェ|CORE-7", assumed="train|電車; express|急行; local|各駅停車; bus|バス; room|部屋", receptive="by far|断然; if I had to choose|選ぶとしたら; probably|おそらく"),
    47: dict(new="bored|退屈した; boring|退屈な; excited|わくわくした; exciting|わくわくさせる; surprised|驚いた; surprising|驚くような; tiring|疲れる", recycled="tired|疲れた|CORE-30", assumed="movie|映画; trip|旅行; game|試合; ending|結末; concert|コンサート; museum|博物館", receptive="I'm not really into it|あまり好みではない; it's a bit much|少しきつい; not my thing|好みではない"),
}


KNOWN_WORDS = {
    37: (("ジョブ", "job"), ("コース", "course"), ("プラン", "plan")),
    38: (("ドア", "door"), ("ホテル", "hotel"), ("メール", "email")),
    39: (("トレイン", "train"), ("カフェ", "café"), ("コンサート", "concert")),
    40: (("ドクター", "doctor"), ("ナイト", "night"), ("ウォーター", "water")),
    41: (("ID", "ID"), ("チケット", "ticket"), ("ミュージアム", "museum")),
    42: (("コメディー", "comedy"), ("ドラマ", "drama"), ("テレビ", "TV")),
    43: (("カフェ", "café"), ("ホテル", "hotel"), ("レストラン", "restaurant")),
    44: (("バッグ", "bag"), ("サイズ", "size"), ("ホテル", "hotel")),
    46: (("オプション", "option"), ("ホテル", "hotel"), ("カフェ", "café")),
    47: (("ムービー", "movie"), ("ゲーム", "game"), ("コンサート", "concert")),
}


TRANSLATE_HINTS = {
    37: (("探す:look for; 新しい仕事:new job", "更新する:update; 履歴書:résumé", "講座:course", "引っ越す:move; 来月:next month"), ("それについて:about it", "買う:buy; 旅行:trip", "勉強する:study", "料理する:cook; 今夜:tonight")),
    38: (("運ぶ:carry", "ドア:door", "時間:time", "ホテル:hotel; 電話する:call"), ("送る:send; 正午:noon", "電話する:call", "終える:finish; 金曜日:Friday", "持ってくる:bring; 明日:tomorrow")),
    39: (("少し遅れる:a bit late", "乗り遅れる:miss; 電車:train", "時間:time", "家:home"), ("待つ:wait", "忙しい:busy; 電話する:call", "電車:train; 待つ:wait", "カフェ:café; 別の場所:somewhere else")),
    40: (("少し休む:get some rest", "水:water", "家:home", "寝る:sleep; 今夜:tonight"), ("悪化する:get worse; 医師:doctor", "悪化する:get worse; 助けを求める:get help", "悪化する:get worse; 家:home; 電話する:call", "悪化する:get worse; 歩くのをやめる:stop walking")),
    41: (("身分証:ID", "バッジ:badge", "予約する:book; 時間枠:time slot", "受付:desk"), ("予約する:book; 前もって:ahead", "写真:photo; 持ってくる:bring", "オンラインで:online", "印刷する:print; チケット:ticket")),
    42: (("見る:watch; 番組:show", "コーヒー:coffee", "働く:work; 金曜日:Friday", "料理する:cook"), ("好む:prefer; コメディー:comedy", "好む:prefer; 紅茶:tea", "好む:prefer; 店:shop", "好む:prefer; スープ:soup")),
    43: (("小さい:small; 静かな:quiet; 場所:place", "明るい:bright; きれいな:clean; 部屋:room", "小さい:small; 親しみやすい:friendly; カフェ:café", "大きい:big; にぎやかな:busy; 店:shop"), ("駅:station", "カフェ:café", "ホテル:hotel", "銀行:bank")),
    44: (("小さい:small", "高い:expensive", "暑い:hot", "混んでいる:crowded"), ("大きい:big", "安い:cheap", "静かな:quiet", "かばん:bag; 軽い:light")),
    46: (("一番よい:best", "安い:cheap", "速い:fast", "快適な:comfortable"), ("好む:prefer; 選択肢:option", "好む:prefer; 窓側の席:window seat; 通路側の席:aisle seat", "好む:prefer; 電車:train; バス:bus", "好む:prefer; 部屋:room")),
    47: (("退屈した:bored; 映画:movie", "わくわくした:excited; 試合:game", "驚いた:surprised; 結末:ending", "疲れた:tired; 旅行:trip"), ("退屈な:boring; 映画:movie", "わくわくさせる:exciting; 試合:game", "驚くような:surprising; 結末:ending", "疲れる:tiring; 旅行:trip")),
}
TRANSLATE_STAGES = {number: ("supported", "supported") for number in NUMBERS}


OPEN_MENUS = {
    37: (("探す:look for", "更新する:update", "引っ越す:move"), ("買う:buy", "勉強する:study", "料理する:cook")),
    38: (("箱を運ぶ:carry the box",), ("ファイルを送る:send the files", "正午:noon")),
    39: (("少し遅れる:a bit late", "乗り遅れる:miss", "忙しい:busy"), ("待つ:wait", "電話する:call", "別の場所:somewhere else")),
    40: (("少し休む:get some rest", "水:water", "寝る:sleep"), ("医師:doctor", "助けを求める:get help", "家:home")),
    41: (("身分証:ID", "バッジ:badge", "時間枠:time slot"), ("写真:photo", "印刷する:print", "オンラインで:online")),
    42: (("見る:watch", "コーヒー:coffee", "料理する:cook"), ("コメディー:comedy", "紅茶:tea", "スープ:soup")),
    43: (("小さい:small", "静かな:quiet", "明るい:bright", "きれいな:clean"), ("駅:station", "ホテル:hotel", "銀行:bank")),
    44: (("小さい:small", "高い:expensive", "混んでいる:crowded"), ("大きい:big", "静かな:quiet", "軽い:light")),
    46: (("一番よい:best", "安い:cheap", "速い:fast"), ("急行:express", "バス:bus")),
    47: (("退屈した:bored", "わくわくした:excited", "驚いた:surprised"), ("退屈な:boring", "わくわくさせる:exciting", "驚くような:surprising")),
}


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


SPECS = {
    37: semantic_spec(
        (("Use this for a plan you decided before this conversation.", "この会話より前に決めた予定を伝えるときに使います。"), ("Use this to ask what someone has already decided to do.", "相手がすでに何をすると決めているか聞くときに使います。")),
        (("Write one plan you have already decided on.", "すでに決めている予定を一つ書きましょう。"), ("Ask one real question about my plans.", "私の予定について本当に聞きたいことを一つ書きましょう。")),
        ((), ()),
        (("Keep going to before the planned action", "予定した行動の前に going to", "I’m + <b>going to</b> + 動詞の原形", "Earlier decision", "前から決めていたこと", ("I’m <b>going to</b> look for a new job.", "I’m <b>going to</b> update my résumé.")), ("Move are before you", "質問では are を you の前へ", "What + <b>are you going to</b> + 動詞の原形?", "Ask about the plan", "予定を聞く", ("What <b>are you going to</b> buy?", "What <b>are you going to</b> study?"))),
        ("With or without “about it”?", "about it のあり・なし", "Ask “What are you going to do?” about a general plan. Add “about it” when both people already know the problem.", "一般的な予定を聞くなら「What are you going to do?」と言います。二人ともすでに知っている問題について聞くなら「about it」を加えます。", ("General plan", "一般的な予定", "What are you going to do?", "何をするつもりですか？"), ("Known problem", "分かっている問題", "What are you going to do about it?", "それについてどうするつもりですか？")),
    ),
    38: semantic_spec(
        (("Use this when you offer to do something yourself right now.", "今その場で自分が何かをすると申し出るときに使います。"), ("Use this for a promise you decide to make as you speak.", "話しながら今決めた約束をするときに使います。")),
        (("Offer to help with one real task.", "実際の作業を一つ手伝うと申し出ましょう。"), ("Make one real promise and give its deadline.", "本当にできる約束を一つして、期限も伝えましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("それ、{t}私が運びますよ{/t}。", "Let me ", "carry", "to carry", " that for you."),
                ("ドアは{t}私が開けますよ{/t}。", "Let me ", "open", "to open", " the door for you."),
                ("時間は私が{t}確認します{/t}。", "Let me ", "check", "to check", " the time for you."),
                ("ホテルには私が{t}電話します{/t}。", "Let me ", "call", "to call", " the hotel for you."),
            )),
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("{t}今決めました。{/t}心配しないで、正午までに送ります。", "Don’t worry, ", "I’ll", "I'm going to", " send it by noon."),
                ("{t}今決めました。{/t}心配しないで、6時までに電話します。", "Don’t worry, ", "I’ll", "I'm going to", " call you by six."),
                ("{t}今決めました。{/t}心配しないで、金曜日までに終わらせます。", "Don’t worry, ", "I’ll", "I'm going to", " finish it by Friday."),
                ("{t}今決めました。{/t}心配しないで、明日までに持ってきます。", "Don’t worry, ", "I’ll", "I'm going to", " bring it by tomorrow."),
            )),
        ),
        (("Use a plain verb after Let me", "Let me のあとは動詞の原形", "<b>Let me</b> + 動詞の原形 + for you", "Offer now", "その場の申し出", ("<b>Let me carry</b> that for you.", "<b>Let me call</b> the hotel for you.")), ("Use I’ll for a new decision", "今決めたことには I’ll", "Don’t worry, + <b>I’ll</b> + 動詞 + 期限", "Decision made now", "今決めた約束", ("Don’t worry, <b>I’ll send</b> it by noon.", "Don’t worry, <b>I’ll bring</b> it tomorrow."))),
        ("Neutral or reassuring?", "ふつう・安心させる", "Both accept the task. “I’ve got it” adds a stronger sense that the other person can stop worrying.", "どちらも引き受ける言い方です。「I’ve got it」は、もう心配しなくてよいという安心感を強く加えます。", ("Simple acceptance", "ふつうに引き受ける", "Okay, I’ll do it.", "分かりました。やります。"), ("Reassuring acceptance", "安心させて引き受ける", "I’ve got it.", "私に任せてください。")),
    ),
    39: semantic_spec(
        (("Use might when something is possible but not certain.", "起こる可能性はあるものの、まだ確かでないときに might を使います。"), ("Use this to say what you will do if the uncertain thing happens.", "まだ確かでないことが起きた場合の対応を伝えるときに使います。")),
        (("Write one uncertain possibility for today.", "今日起こるかもしれないことを一つ書きましょう。"), ("Write one useful fallback for that possibility.", "その場合に役立つ代わりの案を一つ書きましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("少し{t}遅れるかもしれません{/t}。", "I ", "might be", "might to be", " a bit late."),
                ("電車に{t}乗り遅れるかもしれません{/t}。", "I ", "might miss", "might to miss", " the train."),
                ("もう少し時間が{t}必要かもしれません{/t}。", "I ", "might need", "might to need", " more time."),
                ("家に{t}いるかもしれません{/t}。", "I ", "might stay", "might to stay", " home."),
            )),
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("{t}もし{/t}そうなら、外で待ちます。", "", "If", "Because", " you are, I’ll wait outside."),
                ("{t}もし{/t}忙しいなら、あとで電話します。", "", "If", "Because", " you’re busy, I’ll call later."),
                ("{t}もし{/t}電車が遅れたら、ここで待ちます。", "", "If", "Because", " the train is late, I’ll wait here."),
                ("{t}もし{/t}カフェが満席なら、別の場所に行きます。", "", "If", "Because", " the café is full, I’ll go somewhere else."),
            )),
        ),
        (("Keep the verb plain after might", "might のあとは動詞の原形", "I + <b>might</b> + 動詞の原形", "Uncertain possibility", "まだ確かでないこと", ("I <b>might be</b> late.", "I <b>might need</b> more time.")), ("Connect condition and response", "条件と対応をつなぐ", "<b>If</b> + 条件, + <b>I’ll</b> + 対応", "Fallback", "起きた場合の対応", ("<b>If</b> you’re busy, <b>I’ll</b> call later.", "<b>If</b> the train is late, <b>I’ll</b> wait here."))),
        ("Might or may?", "might と may", "Both express possibility. “May” can sound a little more formal in an everyday warning.", "どちらも可能性を表します。日常の注意では「may」のほうが少し改まって聞こえることがあります。", ("Everyday warning", "日常の注意", "I might be late.", "遅れるかもしれません。"), ("Slightly more formal", "少し改まった言い方", "I may be late.", "遅れるかもしれません。")),
    ),
    40: semantic_spec(
        (("Use should for a helpful idea that the other person can consider.", "相手が考えられる助言を一つ伝えるときに should を使います。"), ("Use need to when the situation makes an action necessary.", "状況によって行動が必要になったときに need to を使います。")),
        (("Give one helpful piece of advice for a real situation.", "実際の状況に役立つ助言を一つ書きましょう。"), ("Write when stronger action would become necessary.", "より強い対応が必要になる条件を書きましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("少し{t}休んだほうがいいです{/t}。", "You ", "should get", "should to get", " some rest."),
                ("水を少し{t}飲んだほうがいいです{/t}。", "You ", "should drink", "should to drink", " some water."),
                ("早めに家へ{t}帰ったほうがいいです{/t}。", "You ", "should go", "should to go", " home early."),
                ("今夜はもっと{t}寝たほうがいいです{/t}。", "You ", "should sleep", "should to sleep", " more tonight."),
            )),
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("悪化したら、医師に診てもらう{t}必要があります{/t}。", "If it gets worse, you ", "need to", "should", " see a doctor."),
                ("もっと具合が悪くなったら、助けを求める{t}必要があります{/t}。", "If you feel worse, you ", "need to", "should", " get help."),
                ("もっと具合が悪くなったら、家に電話する{t}必要があります{/t}。", "If you feel worse, you ", "need to", "should", " call home."),
                ("悪化したら、歩くのをやめる{t}必要があります{/t}。", "If it gets worse, you ", "need to", "should", " stop walking."),
            )),
        ),
        (("Give advice with should", "should で助言する", "You + <b>should</b> + 動詞の原形", "Helpful idea", "役立つ考え", ("You <b>should get</b> some rest.", "You <b>should drink</b> some water.")), ("Name a necessary action", "必要な行動を伝える", "If it gets worse, + you <b>need to</b> + 動詞", "Necessary response", "必要になった対応", ("you <b>need to see</b> a doctor", "you <b>need to stop</b> walking"))),
        ("Direct or softer?", "直接・やわらかく", "Add “maybe” before should when you want the advice to sound less direct.", "助言をやわらかく伝えたいときは、should の前に「maybe」を加えます。", ("Direct advice", "直接的な助言", "You should get some rest.", "少し休んだほうがいいですよ。"), ("Softer suggestion", "やわらかい提案", "Maybe you should get some rest.", "少し休んだほうがいいかもしれません。")),
    ),
    41: semantic_spec(
        (("Use have to for an action that a rule requires.", "決まりで必要な行動を伝えるときに have to を使います。"), ("Use don’t have to when the action is optional.", "その行動をしてもしなくてもよいときに don’t have to を使います。")),
        (("Write one action that a real rule requires.", "実際の決まりで必要な行動を一つ書きましょう。"), ("Write one action that is genuinely optional.", "本当にしなくてもよい行動を一つ書きましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, suffix in (
                ("身分証を{t}見せる必要があります{/t}。", " show your ID."),
                ("バッジを{t}着ける必要があります{/t}。", " wear a badge."),
                ("時間枠を{t}予約する必要があります{/t}。", " book a time slot."),
                ("受付で{t}支払う必要があります{/t}。", " pay at the desk."),
            ) for prefix, correct, distractor in (("You ", "have to", "don't have to"),)),
            tuple((jp, prefix, correct, distractor, suffix) for jp, suffix in (
                ("でも、前もって{t}予約する必要はありません{/t}。", " book ahead."),
                ("でも、写真を{t}持ってくる必要はありません{/t}。", " bring a photo."),
                ("でも、オンラインで{t}支払う必要はありません{/t}。", " pay online."),
                ("でも、チケットを{t}印刷する必要はありません{/t}。", " print the ticket."),
            ) for prefix, correct, distractor in (("But you ", "don't have to", "have to"),)),
        ),
        (("Mark a requirement", "必要なことを示す", "You + <b>have to</b> + 動詞の原形", "Required", "しなければならない", ("You <b>have to show</b> your ID.", "You <b>have to wear</b> a badge.")), ("Optional is not forbidden", "任意と禁止は違う", "<b>don’t have to</b> ≠ <b>mustn’t</b>", "Optional vs forbidden", "任意・禁止", ("You <b>don’t have to</b> book ahead. = optional", "You <b>mustn’t</b> enter here. = forbidden"))),
        ("Full or conversational?", "完全な形・会話的な形", "“No need to” is a common conversational alternative to “You don’t have to.”", "「No need to」は「You don’t have to」の会話でよく使う言い換えです。", ("Complete sentence", "完全な文", "You don’t have to book ahead.", "前もって予約する必要はありません。"), ("Conversational shortcut", "会話で短く", "No need to book ahead.", "前もって予約しなくて大丈夫です。")),
    ),
    42: semantic_spec(
        (("Use I do when the positive fact is true, even after a negative question.", "否定疑問のあとでも、肯定の事実が正しければ I do を使います。"), ("Use I don’t when the negative fact is true, then add your real preference.", "否定の事実が正しければ I don’t を使い、本当の好みを続けます。")),
        (("Write one true positive answer to a negative question.", "否定疑問に対する本当の肯定の答えを書きましょう。"), ("Write one true negative answer and your alternative.", "本当の否定の答えと、代わりに好むものを書きましょう。")),
        (
            tuple((jp, "Actually, I ", "do", "don’t", suffix) for jp, suffix in (
                ("「この番組、好きじゃないんですか？」→ いえ、{t}好きです。{/t}毎週見ています。", ". I watch it every week."),
                ("「コーヒー、飲まないんですか？」→ いえ、{t}飲みます。{/t}毎朝飲んでいます。", ". I drink it every morning."),
                ("「そこで働いていないんですか？」→ いえ、{t}働いています。{/t}金曜日はそこで働いています。", ". I work there on Fridays."),
                ("「これ、作らないんですか？」→ いえ、{t}作ります。{/t}家で作っています。", ". I cook it at home."),
            )),
            tuple((jp, "No, I ", "don’t", "do", suffix) for jp, suffix in (
                ("「ドラマのほうが好きじゃないんですか？」→ {t}はい、好きではありません。{/t}コメディーのほうが好きです。", ". I prefer comedies."),
                ("「コーヒーのほうが好きじゃないんですか？」→ {t}はい、好きではありません。{/t}紅茶のほうが好きです。", ". I prefer tea."),
                ("「この店、好きじゃないんですか？」→ {t}はい、好きではありません。{/t}もう一方の店のほうが好きです。", ". I prefer the other shop."),
                ("「このサラダ、好きじゃないんですか？」→ {t}はい、好きではありません。{/t}スープのほうが好きです。", ". I prefer soup."),
            )),
        ),
        (("Answer the fact, not the negative wording", "否定形ではなく事実に答える", "好き・する → <b>Actually, I do.</b>", "Positive fact", "肯定の事実", ("Don’t you like it? → <b>Actually, I do.</b>", "Don’t you work there? → <b>Actually, I do.</b>")), ("Use don’t for the negative fact", "否定の事実には don’t", "好きではない・しない → <b>No, I don’t.</b>", "Negative fact", "否定の事実", ("Don’t you like it? → <b>No, I don’t.</b>", "Don’t you drink it? → <b>No, I don’t.</b>"))),
        ("Yes or actually?", "Yes と actually", "“Yes, I do” answers neutrally. “Actually, I do” gently corrects the other person’s expectation.", "「Yes, I do」は中立的な答えです。「Actually, I do」は相手の予想をやわらかく訂正します。", ("Neutral answer", "中立的に答える", "Yes, I do.", "はい、好きです。"), ("Correct an expectation", "予想を訂正する", "Actually, I do.", "いえ、実は好きです。")),
    ),
    43: semantic_spec(
        (("Use this to give two useful details before naming a thing.", "ものの名前の前に役立つ特徴を二つ加えるときに使います。"), ("Use near to locate the thing by a familiar landmark.", "よく分かる目印を使って場所を伝えるときに near を使います。")),
        (("Describe one real place with two useful details.", "実際の場所を役立つ二つの特徴で説明しましょう。"), ("Write where that place is using one landmark.", "目印を一つ使って、その場所がどこにあるか書きましょう。")),
        (
            (),
            tuple((jp, "It’s ", "near", "next to", suffix) for jp, suffix in (
                ("駅の{t}近くです{/t}。", " the station."),
                ("カフェの{t}近くです{/t}。", " the café."),
                ("ホテルの{t}近くです{/t}。", " the hotel."),
                ("銀行の{t}近くです{/t}。", " the bank."),
            )),
        ),
        (("Put the details before the noun", "特徴は名詞の前へ", "It’s + a + 形容詞, 形容詞 + 名詞", "Two details", "二つの特徴", ("a <b>small, quiet</b> place", "two <b>small, quiet</b> cafés")), ("Put near before the landmark", "目印の前に near", "It’s + <b>near</b> + the + 目印", "Nearby, not necessarily beside", "近く・真横とは限らない", ("It’s <b>near</b> the station.", "It’s <b>near</b> the hotel."))),
        ("Small or cozy?", "small と cozy", "“Small” only names size. “Cozy” adds the positive feeling that the place is comfortable and welcoming.", "「small」は大きさだけを表します。「cozy」は、居心地がよく温かいという肯定的な印象も加えます。", ("Size only", "大きさだけ", "It’s a small café.", "小さいカフェです。"), ("Positive feeling", "よい印象も加える", "It’s a cozy café.", "居心地のよいカフェです。")),
    ),
    44: semantic_spec(
        (("Use too before an adjective when the amount causes a problem.", "程度が問題になるほど大きいときに、形容詞の前に too を使います。"), ("Use adjective plus enough when the amount falls short of what you need.", "必要な程度に足りないときに、形容詞のあとに enough を置きます。")),
        (("Write why one real option goes beyond your limit.", "実際の選択肢が限度を超えている理由を書きましょう。"), ("Write what one real option does not have enough of.", "実際の選択肢に何が十分でないか書きましょう。")),
        (
            tuple((jp, "It’s ", "too", "really", suffix) for jp, suffix in (
                ("私には{t}小さすぎます{/t}。", " small for me."),
                ("私たちには{t}高すぎます{/t}。", " expensive for us."),
                ("ここは{t}暑すぎます{/t}。", " hot in here."),
                ("私には{t}混みすぎています{/t}。", " crowded for me."),
            )),
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("これは{t}十分な大きさではありません{/t}。", "This one isn’t ", "big enough", "enough big", "."),
                ("これは{t}十分安くありません{/t}。", "This one isn’t ", "cheap enough", "enough cheap", "."),
                ("この部屋は{t}十分静かではありません{/t}。", "This room isn’t ", "quiet enough", "enough quiet", "."),
                ("このかばんは{t}十分軽くありません{/t}。", "This bag isn’t ", "light enough", "enough light", "."),
            )),
        ),
        (("Put too before the adjective", "形容詞の前に too", "<b>too</b> + 形容詞 + for + 人", "Beyond the limit", "限度を超える", ("<b>too small</b> for me", "<b>too expensive</b> for us")), ("Put enough after the adjective", "形容詞のあとに enough", "isn’t + 形容詞 + <b>enough</b>", "Below the limit", "必要な程度に足りない", ("isn’t big <b>enough</b>", "isn’t quiet <b>enough</b>"))),
        ("Direct or softer?", "直接・やわらかく", "“It’s too small” gives a direct reason. “It’s not quite big enough” softens the same rejection.", "「It’s too small」は理由を直接伝えます。「It’s not quite big enough」は同じ断り方をやわらかくします。", ("Direct reason", "理由を直接伝える", "It’s too small.", "小さすぎます。"), ("Softer rejection", "やわらかく断る", "It’s not quite big enough.", "少し大きさが足りません。")),
    ),
    46: semantic_spec(
        (("Use a superlative to identify the best option in one group.", "一つのグループの中で最もよい選択肢を示すときに最上級を使います。"), ("Use prefer A to B to state which of two options you like more.", "二つのうちどちらがより好きか伝えるときに prefer A to B を使います。")),
        (("Write the best option in one real group.", "実際のグループで一番の選択肢を書きましょう。"), ("Compare two real options and state your preference.", "実際の二つの選択肢を比べて、好みを書きましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("ここではこれが{t}一番いい{/t}です。", "It’s the ", "best", "better", " one here."),
                ("ここではこれが{t}一番安い{/t}です。", "It’s the ", "cheapest", "cheaper", " one here."),
                ("ここではこれが{t}一番速い{/t}です。", "It’s the ", "fastest", "faster", " one here."),
                ("ここではこれが{t}一番快適{/t}です。", "It’s the ", "most comfortable", "more comfortable", " one here."),
            )),
            tuple((jp, prefix, "to", "than", suffix) for jp, prefix, suffix in (
                ("あちら{t}より{/t}こちらのほうが好きです。", "I prefer this one ", " that one."),
                ("通路側{t}より{/t}窓側の席のほうが好きです。", "I prefer the window seat ", " the aisle seat."),
                ("バス{t}より{/t}電車のほうが好きです。", "I prefer the train ", " the bus."),
                ("大きい部屋{t}より{/t}小さい部屋のほうが好きです。", "I prefer the small room ", " the big room."),
            )),
        ),
        (("Use -est or most", "-est・most を使い分ける", "good → <b>the best</b> / cheap → <b>the cheapest</b> / comfortable → <b>the most comfortable</b>", "One best option", "一番の選択肢", ("<b>the cheapest</b> one here", "<b>the most comfortable</b> one here")), ("Compare preferences with to", "好みの比較には to", "I + <b>prefer</b> + A + <b>to</b> + B", "Preference", "どちらが好きか", ("I <b>prefer</b> this one <b>to</b> that one.", "I <b>prefer</b> the train <b>to</b> the bus."))),
        ("Strong or cautious?", "強く・控えめに", "Add “by far” for a clear winner. Add “probably” when the choice is close.", "明らかに一番なら「by far」を加えます。差が小さく控えめに言うなら「probably」を加えます。", ("Clear winner", "明らかに一番", "It’s by far the best one.", "断然これが一番です。"), ("Close choice", "差が小さい", "It’s probably the best one.", "おそらくこれが一番です。")),
    ),
    47: semantic_spec(
        (("Use an -ed adjective for the person who experiences the feeling.", "その気持ちを感じた人を説明するときに -ed の形を使います。"), ("Use an -ing adjective for the thing that causes the feeling.", "その気持ちを起こさせるものを説明するときに -ing の形を使います。")),
        (("Write how one recent experience made you feel.", "最近の体験で自分がどう感じたか書きましょう。"), ("Write what that experience itself was like.", "その体験自体がどんなものだったか書きましょう。")),
        (
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("映画の間、私は{t}退屈していました{/t}。", "I was ", "bored", "boring", " during the movie."),
                ("試合の間、私は{t}わくわくしていました{/t}。", "I was ", "excited", "exciting", " during the game."),
                ("結末に私は{t}驚きました{/t}。", "I was ", "surprised", "surprising", " by the ending."),
                ("旅行のあと、私は{t}疲れていました{/t}。", "I was ", "tired", "tiring", " after the trip."),
            )),
            tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (
                ("その映画は本当に{t}退屈でした{/t}。", "The movie was really ", "boring", "bored", "."),
                ("その試合は本当に{t}わくわくするものでした{/t}。", "The game was really ", "exciting", "excited", "."),
                ("その結末は本当に{t}驚くものでした{/t}。", "The ending was really ", "surprising", "surprised", "."),
                ("その旅行は本当に{t}疲れるものでした{/t}。", "The trip was really ", "tiring", "tired", "."),
            )),
        ),
        (("Use -ed for the person", "人には -ed", "人 + be + 感情の形容詞<b>-ed</b>", "Person’s feeling", "人の気持ち", ("I was bor<b>ed</b>.", "I was surpris<b>ed</b>.")), ("Use -ing for the cause", "原因には -ing", "もの・体験 + be + 感情の形容詞<b>-ing</b>", "Cause of the feeling", "気持ちの原因", ("The movie was bor<b>ing</b>.", "The ending was surpris<b>ing</b>."))),
        ("Blunt or softer?", "直接・やわらかく", "“The movie was boring” is direct. “It wasn’t really my thing” softens a negative personal opinion.", "「The movie was boring」は直接的です。「It wasn’t really my thing」は否定的な個人の感想をやわらかくします。", ("Direct evaluation", "直接評価する", "The movie was boring.", "その映画は退屈でした。"), ("Softer personal opinion", "個人の感想としてやわらかく", "It wasn’t really my thing.", "あまり自分の好みではありませんでした。")),
    ),
}


# Open production is communicative rather than a generic request to "write one
# sentence."  Each prompt names both the reusable frame and the real-world job.
WRITE_PROMPTS = {
    37: (("Now use “I'm going to ___” to tell me one plan you have already decided on.", "では、「I'm going to ___」を使って、すでに決めている予定を一つ教えてください。"), ("Now use “What are you going to ___?” to ask me one real question about my plans.", "では、「What are you going to ___?」を使って、私の予定について本当に聞きたいことを一つ質問してください。")),
    38: (("Now use “Let me ___ for you” to offer help with one real task.", "では、「Let me ___ for you」を使って、実際の作業を一つ手伝うと申し出てください。"), ("Now use “Don't worry, I'll ___ by ___” to make one real promise with a deadline.", "では、「Don't worry, I'll ___ by ___」を使って、期限つきの本当の約束を一つしてください。")),
    39: (("Now use “I might ___” to name one real possibility for today.", "では、「I might ___」を使って、今日実際に起こるかもしれないことを一つ言ってください。"), ("Now use “If ___, I'll ___” to give one useful backup plan.", "では、「If ___, I'll ___」を使って、役に立つ代わりの案を一つ言ってください。")),
    40: (("Now use “You should ___” to give advice for one real problem.", "では、「You should ___」を使って、実際の問題に助言を一つしてください。"), ("Now use “If it gets worse, you need to ___” to name the necessary next step.", "では、「If it gets worse, you need to ___」を使って、悪化した場合に必要な次の行動を言ってください。")),
    41: (("Now use “You have to ___” to explain one real requirement.", "では、「You have to ___」を使って、実際に必要なことを一つ説明してください。"), ("Now use “You don't have to ___” to explain one genuinely optional action.", "では、「You don't have to ___」を使って、本当にしなくてもよい行動を一つ説明してください。")),
    42: (("Now use “Actually, I do. I ___” to give one true positive answer.", "では、「Actually, I do. I ___」を使って、本当の肯定の答えを一つ言ってください。"), ("Now use “No, I don't. I prefer ___” to give one true negative answer and your alternative.", "では、「No, I don't. I prefer ___」を使って、本当の否定の答えと、代わりに好きなものを言ってください。")),
    43: (("Now use “It's a ___, ___ place” to describe one real place with two useful details.", "では、「It's a ___, ___ place」を使って、実際の場所を役立つ二つの特徴で説明してください。"), ("Now use “It's near ___” to locate that place with a landmark.", "では、「It's near ___」を使って、目印を一つ挙げてその場所を説明してください。")),
    44: (("Now use “It's too ___” to explain why one real option crosses your limit.", "では、「It's too ___」を使って、実際の選択肢が自分の限度を超える理由を説明してください。"), ("Now use “It isn't ___ enough” to explain what one real option lacks.", "では、「It isn't ___ enough」を使って、実際の選択肢に何が足りないか説明してください。")),
    46: (("Now use “It's the ___ one here” to identify the best option in one real group.", "では、「It's the ___ one here」を使って、実際のグループの中で一番のものを一つ選んでください。"), ("Now use “I prefer ___ to ___” to compare two real options.", "では、「I prefer ___ to ___」を使って、実際の選択肢を二つ比べてください。")),
    47: (("Now use “I was ___ during / after ___” to describe your reaction to one recent experience.", "では、「I was ___ during / after ___」を使って、最近の体験に対する自分の反応を説明してください。"), ("Now use “The ___ was really ___” to describe what caused that feeling.", "では、「The ___ was really ___」を使って、その気持ちの原因を説明してください。")),
}


# Fill chips support only the lexical payload.  They never reveal the target
# grammar itself, so the learner still has to retrieve the lesson pattern.
FILL_HINTS = {
    37: ((('探す', 'look for'), ('更新する', 'update'), ('受ける', 'take'), ('引っ越す', 'move')), (('する', 'do'), ('買う', 'buy'), ('勉強する', 'study'), ('料理する', 'cook'))),
    38: ((('運ぶ', 'carry'), ('開ける', 'open'), ('確認する', 'check'), ('電話する', 'call')), (('送る', 'send'), ('電話する', 'call'), ('終える', 'finish'), ('持ってくる', 'bring'))),
    39: ((('少し遅れる', 'be a bit late'), ('乗り遅れる', 'miss'), ('必要になる', 'need'), ('家にいる', 'stay home')), (('外で待つ', 'wait outside'), ('あとで電話する', 'call later'), ('ここで待つ', 'wait here'), ('別の場所へ行く', 'go somewhere else'))),
    40: ((('少し休む', 'get some rest'), ('水を飲む', 'drink some water'), ('早く帰る', 'go home early'), ('もっと寝る', 'sleep more')), (('医師に診てもらう', 'see a doctor'), ('助けを求める', 'get help'), ('家に電話する', 'call home'), ('歩くのをやめる', 'stop walking'))),
    41: ((('身分証を見せる', 'show your ID'), ('バッジを着ける', 'wear a badge'), ('予約する', 'book'), ('受付で支払う', 'pay at the desk')), (('予約する', 'book'), ('写真を持ってくる', 'bring a photo'), ('オンラインで支払う', 'pay online'), ('印刷する', 'print'))),
    42: ((('見る', 'watch'), ('飲む', 'drink'), ('働く', 'work'), ('料理する', 'cook')), (('コメディー', 'comedies'), ('紅茶', 'tea'), ('もう一方の店', 'the other shop'), ('スープ', 'soup'))),
    43: (((('小さい', 'small'), ('静かな', 'quiet')), (('明るい', 'bright'), ('きれいな', 'clean')), (('小さい', 'small'), ('親しみやすい', 'friendly')), (('大きい', 'big'), ('にぎやかな', 'busy'))), (('駅', 'the station'), ('カフェ', 'the café'), ('ホテル', 'the hotel'), ('銀行', 'the bank'))),
    44: ((('小さい', 'small'), ('高い', 'expensive'), ('暑い', 'hot'), ('混んでいる', 'crowded')), (('大きい', 'big'), ('安い', 'cheap'), ('静かな', 'quiet'), ('軽い', 'light'))),
    46: (None, (('こちら', 'this one'), ('窓側の席', 'the window seat'), ('電車', 'the train'), ('小さい部屋', 'the small room'))),
    47: (None, None),
}

# Lexical chips are part of the lesson's vocabulary contract.  Declare any
# compound payload that is not already owned as assumed support, while leaving
# the target grammar itself out of the chips.
for number, page_hints in FILL_HINTS.items():
    owned = {
        entry.split("|", 1)[0].casefold()
        for value in VOCAB[number].values()
        for entry in filter(None, value.split("; "))
    }
    additions = []
    for page in page_hints:
        for row in page or ():
            pairs = (row,) if len(row) == 2 and all(isinstance(item, str) for item in row) else row
            for japanese, english in pairs:
                if english.casefold() not in owned:
                    additions.append(f"{english}|{japanese}")
                    owned.add(english.casefold())
    if additions:
        VOCAB[number]["assumed"] += "; " + "; ".join(additions)

for number in NUMBERS:
    SPECS[number]["writes"] = WRITE_PROMPTS[number]
    SPECS[number]["fill_hints"] = FILL_HINTS[number]
    choices = list(SPECS[number]["choices"])
    for part in LESSONS[number].get("omit_choice", ()):
        choices[part - 1] = ()
    SPECS[number]["choices"] = tuple(choices)

# A negative question is useful only if the learner must decide from the fact,
# not repeat the same polarity four times.  This checkpoint deliberately mixes
# positive and negative facts while keeping Part 1's redundant choice omitted.
SPECS[42]["choices"] = ((), (
    ("「コーヒー、飲まないんですか？」→ いえ、{t}飲みます{/t}。", "Actually, I ", "do", "don't", ". I drink it every morning."),
    ("「ドラマのほうが好きじゃないんですか？」→ {t}はい、好きではありません{/t}。", "No, I ", "don't", "do", ". I prefer comedies."),
    ("「そこで働いていないんですか？」→ いえ、{t}働いています{/t}。", "Actually, I ", "do", "don't", ". I work there on Fridays."),
    ("「このサラダ、好きじゃないんですか？」→ {t}はい、好きではありません{/t}。", "No, I ", "don't", "do", ". I prefer soup."),
))


def dlg(role, p1, p2, first, follow, close, last):
    """Store one exact six-turn exchange for the shared Core renderer."""
    return (role, p1, p2, first, follow, close, last)


DIALOGUES = {
    37: dict(
        model=dlg("Career adviser", 0, 1,
            ("Have you made any plans about work?", "仕事について何か計画を立てましたか？"),
            ("That sounds clear. Ask me about my trip.", "はっきりした計画ですね。私の旅行について聞いてください。"),
            ("A new bag. What are you going to do first?", "新しいかばんです。あなたはまず何をするつもりですか？"),
            ("I'm going to update my résumé.", "履歴書を更新するつもりです。")),
        wild=dlg("Classmate", 2, 2,
            ("Are you planning any classes this autumn?", "この秋、何か講座を受ける予定ですか？"),
            ("Nice. Ask about my next class.", "いいですね。私が次に受ける講座について聞いてください。"),
            ("Design. Which English course are you going to take?", "デザインです。どの英語講座を受けるつもりですか？"),
            ("I'm going to take an online course.", "オンライン講座を受けるつもりです。")),
    ),
    38: dict(
        model=dlg("Coworker", 0, 0,
            ("This box is heavier than I expected.", "この箱は思ったより重いです。"),
            ("Thanks. Can you send this file too?", "ありがとう。このファイルも送ってもらえますか？"),
            ("Great. Can I count on you?", "よかった。任せても大丈夫ですか？"),
            ("Don't worry, I'll send it by noon.", "心配しないで、正午までに送ります。")),
        wild=dlg("Hotel guest", 1, 3,
            ("My hands are full.", "両手がふさがっています。"),
            ("Thank you. Could you bring the key later?", "ありがとう。あとで鍵も持ってきてもらえますか？"),
            ("That works. Tomorrow is fine.", "それなら助かります。明日で大丈夫です。"),
            ("See you then.", "では、そのときに。")),
    ),
    39: dict(
        model=dlg("Friend", 0, 0,
            ("Can you meet me outside the station?", "駅の外で会えますか？"),
            ("Okay. What if I'm late too?", "分かりました。私も遅れたらどうしますか？"),
            ("Good. Do you expect a long delay?", "いいですね。大幅に遅れそうですか？"),
            ("I might be a bit late.", "少し遅れるかもしれません。")),
        wild=dlg("Concert friend", 1, 2,
            ("Will you get here before the concert?", "コンサートの前に着けそうですか？"),
            ("Then what will you do if the train is late?", "では、電車が遅れたらどうしますか？"),
            ("That backup works. Is the train connection tight?", "その代わりの案で大丈夫です。乗り換え時間は短いですか？"),
            ("I might miss the train.", "電車に乗り遅れるかもしれません。")),
    ),
    40: dict(
        model=dlg("Friend", 0, 0,
            ("I have a headache and feel tired.", "頭が痛くて疲れています。"),
            ("What should I do if it gets worse?", "悪化したらどうすればいいですか？"),
            ("So I shouldn't ignore it?", "つまり、放っておかないほうがいいですね？"),
            ("If it gets worse, you need to see a doctor.", "悪化したら、医師に診てもらう必要があります。")),
        wild=dlg("Hiking partner", 1, 1,
            ("I feel dizzy after that climb.", "あの登りのあと、めまいがします。"),
            ("And what if I feel worse?", "それで、もっと悪くなったらどうしますか？"),
            ("Okay, I'll stop and ask for help.", "分かりました。立ち止まって助けを求めます。"),
            ("Take care.", "お大事に。")),
    ),
    41: dict(
        model=dlg("Museum visitor", 0, 0,
            ("What do I need at the entrance?", "入口で何が必要ですか？"),
            ("Do I need to reserve a time before I come?", "来る前に時間を予約する必要がありますか？"),
            ("Good. So I can decide later?", "よかった。では、あとで決めてもいいですか？"),
            ("But you don't have to book ahead.", "でも、前もって予約する必要はありません。")),
        wild=dlg("Office visitor", 1, 1,
            ("Is there a rule for visitors?", "訪問者向けの決まりはありますか？"),
            ("Do I need to bring a photo as well?", "写真も持ってくる必要がありますか？"),
            ("Great. I'll bring my ID and get a badge.", "分かりました。身分証を持って行って、バッジを受け取ります。"),
            ("That's right.", "その通りです。")),
    ),
    42: dict(
        model=dlg("Friend", 0, 0,
            ("Don't you like this drama?", "このドラマ、好きじゃないの？"),
            ("Don't you prefer dramas to comedies?", "コメディーよりドラマのほうが好きじゃないの？"),
            ("Got it—you like this drama, but you prefer comedies.", "分かりました。このドラマは好きだけれど、コメディーのほうが好きなんですね。"),
            ("That's right.", "その通りです。")),
        wild=dlg("Coworker", 1, 1,
            ("Don't you like coffee?", "コーヒー、好きじゃないんですか？"),
            ("Don't you prefer coffee to tea?", "紅茶よりコーヒーのほうが好きじゃないんですか？"),
            ("Got it—tea is your first choice.", "分かりました。第一希望は紅茶なんですね。"),
            ("That's right.", "その通りです。")),
    ),
    43: dict(
        model=dlg("Friend", 0, 0,
            ("What's that café like?", "そのカフェはどんな感じですか？"),
            ("That sounds good. Where is it?", "よさそうですね。どこにありますか？"),
            ("Would it be good for studying?", "勉強するのによさそうですか？"),
            ("It's a small, quiet place.", "小さくて静かな場所です。")),
        wild=dlg("Prospective renter", 1, 2,
            ("What's the room like?", "その部屋はどんな感じですか？"),
            ("And where is the building?", "それで、建物はどこにありますか？"),
            ("So it's close to the hotel?", "では、ホテルの近くなんですね？"),
            ("That's right.", "その通りです。")),
    ),
    44: dict(
        model=dlg("Shop assistant", 0, 3,
            ("How about this carry-on bag?", "この機内持ち込みかばんはどうですか？"),
            ("Then how about this lighter bag?", "では、このもっと軽いかばんはどうですか？"),
            ("Would you like to try one more?", "もう一つ試しますか？"),
            ("Yes, please.", "はい、お願いします。")),
        wild=dlg("Hotel receptionist", 2, 2,
            ("How is your room?", "お部屋はどうですか？"),
            ("I'm sorry. Is it quiet enough?", "申し訳ありません。十分静かですか？"),
            ("Would you like a different room?", "別の部屋をご希望ですか？"),
            ("Yes, please.", "はい、お願いします。")),
    ),
    46: dict(
        model=dlg("Bakery clerk", 0, 0,
            ("Which dessert would you choose?", "どのデザートを選びますか？"),
            ("What about this one and that one?", "こちらとあちらではどうですか？"),
            ("So this is your first choice?", "では、これが第一希望ですか？"),
            ("Yes, it is.", "はい、そうです。")),
        wild=dlg("Travel partner", 3, 1,
            ("Which seat looks most comfortable?", "どの席が一番快適そうですか？"),
            ("Which do you prefer, the window or the aisle?", "窓側と通路側では、どちらが好きですか？"),
            ("Great. I'll take the aisle, then.", "いいですね。では私は通路側にします。"),
            ("Sounds good.", "いいですね。")),
    ),
    47: dict(
        model=dlg("Friend", 0, 0,
            ("How did you feel during the movie?", "映画の間、どう感じましたか？"),
            ("What was the movie itself like?", "映画自体はどんな感じでしたか？"),
            ("I understand why you felt that way.", "なぜそう感じたか分かりました。"),
            ("I'm not really into it.", "あまり好みではありません。")),
        wild=dlg("Sports fan", 1, 1,
            ("How did you feel during the game?", "試合の間、どう感じましたか？"),
            ("And what was the game itself like?", "それで、試合自体はどんな感じでしたか？"),
            ("No wonder you enjoyed it.", "楽しめたのも当然ですね。"),
            ("It was great.", "最高でした。")),
    ),
}


LIVE_SCENES = {
    number: (
        ("text", "other", "Tutor", LESSONS[number]["prompt"][0], LESSONS[number]["prompt"][1]),
        ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
        ("text", "me", "Me", "How about you?", "先生はどうですか？"),
        ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
    )
    for number in NUMBERS
}


# Free Talk is a conversation rather than another controlled pattern task, so
# it deliberately has no lexical menu or required target frame.
LIVE_HINTS = {number: {} for number in NUMBERS}


FINAL_LINE_OWNERSHIP = {
    37: {
        "model": ("I'm going to update my résumé.", "CORE-37 current pattern"),
        "wild": ("I'm going to take an online course.", "CORE-37 current frame"),
    },
    38: {
        "model": ("Don't worry, I'll send it by noon.", "CORE-38 current pattern"),
        "wild": ("See you then.", "CORE-29 supporting response"),
    },
    39: {
        "model": ("I might be a bit late.", "CORE-39 current pattern"),
        "wild": ("I might miss the train.", "CORE-39 current pattern"),
    },
    40: {
        "model": ("If it gets worse, you need to see a doctor.", "CORE-40 current pattern"),
        "wild": ("Take care.", "CORE-40 receptive closure"),
    },
    41: {
        "model": ("But you don't have to book ahead.", "CORE-41 current pattern"),
        "wild": ("That's right.", "CORE-7 supporting response"),
    },
    42: {
        "model": ("That's right.", "CORE-7 supporting response"),
        "wild": ("That's right.", "CORE-7 supporting response"),
    },
    43: {
        "model": ("It's a small, quiet place.", "CORE-43 current pattern"),
        "wild": ("That's right.", "CORE-7 supporting response"),
    },
    44: {
        "model": ("Yes, please.", "CORE-20 supporting response"),
        "wild": ("Yes, please.", "CORE-20 supporting response"),
    },
    46: {
        "model": ("Yes, it is.", "CORE-8 supporting response"),
        "wild": ("Sounds good.", "CORE-28 supporting response"),
    },
    47: {
        "model": ("I'm not really into it.", "CORE-47 receptive closure"),
        "wild": ("It was great.", "CORE-33 supporting response"),
    },
}
SUPPORT_LINE_OWNERS = {}


@contextlib.contextmanager
def patched_shell():
    """Give only this course's source tables to the approved renderer."""
    names = (
        "LESSONS", "VOCAB", "KNOWN_WORDS", "TRANSLATE_HINTS", "TRANSLATE_STAGES", "OPEN_MENUS",
        "SPECS", "DIALOGUES", "LIVE_SCENES", "LIVE_HINTS",
        "FINAL_LINE_OWNERSHIP", "SUPPORT_LINE_OWNERS", "COURSE", "PILOT",
    )
    previous = {name: getattr(shell, name) for name in names}
    values = {
        "LESSONS": LESSONS, "VOCAB": VOCAB, "KNOWN_WORDS": KNOWN_WORDS,
        "TRANSLATE_HINTS": TRANSLATE_HINTS, "TRANSLATE_STAGES": TRANSLATE_STAGES,
        "OPEN_MENUS": OPEN_MENUS,
        "SPECS": SPECS, "DIALOGUES": DIALOGUES, "LIVE_SCENES": LIVE_SCENES,
        "LIVE_HINTS": LIVE_HINTS, "FINAL_LINE_OWNERSHIP": FINAL_LINE_OWNERSHIP,
        "SUPPORT_LINE_OWNERS": SUPPORT_LINE_OWNERS, "COURSE": COURSE,
        "PILOT": PILOT,
    }
    for name, value in values.items():
        setattr(shell, name, value)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(shell, name, value)


def normalize_proofread_status(text, status="complete"):
    """Return one canonical proofread marker without changing other bytes."""
    text = re.sub(
        r'\n\s*<meta name="podo:proofread-status" content="[^"]*"\s*/?>',
        "", text,
    )
    title = "  <title>"
    if text.count(title) != 1:
        raise ValueError("expected exactly one head title marker")
    return text.replace(
        title,
        f'  <meta name="podo:proofread-status" content="{status}">\n{title}',
        1,
    )


def build(number, data):
    with patched_shell():
        out, text = shell.build(number, data)
    if number == 42:
        # The controlled rows retain their negative-question antecedents, while
        # dialogue bubbles show only the answer because the partner question is
        # already visible immediately above it.
        for page_id in ("p3-model", "p3-complete", "in-the-wild"):
            text, changed = re.subn(
                rf'(\n    <div class="section" data-page-id="{page_id}".*?'
                rf'(?=\n    <div class="(?:section|transition-page)" data-page-id=|\n  </main>))',
                lambda match: re.sub(r'「[^」]+？」→\s*', "", match.group(1)),
                text,
                count=1,
                flags=re.DOTALL,
            )
            if changed != 1:
                raise ValueError(f"CORE-42: could not normalize {page_id} answer translations")
    text = normalize_proofread_status(text)
    # Reorder grading normalizes punctuation but intentionally preserves the
    # apostrophe code point, so source typography must match ASCII chip text.
    text = text.replace("’", "'")
    text = re.sub(
        r'(<meta name="podo:content-version" content=")[^"]+("\s*/?>)',
        r'\g<1>2026-08-20\2', text, count=1,
    )
    return out, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if set(LESSONS) != set(NUMBERS):
        raise SystemExit("explicit lesson set mismatch")
    preserved = TRACK / "courses" / COURSE / "lessons/45-this-ones-cheaper/lesson.html"
    if not preserved.exists():
        raise SystemExit(f"missing preserved CORE-45: {preserved.relative_to(ROOT)}")
    print(f"preserved {preserved.relative_to(ROOT)}")
    for number in NUMBERS:
        out, text = build(number, LESSONS[number])
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(NUMBERS)} Core decks generated; CORE-45 bytes preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
