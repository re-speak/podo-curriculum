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
            ("I'm {t}going to{/t} look for a new job.", "新しい仕事を{t}探すつもりです{/t}。", "I'm going to|look for|a new job."),
            ("I'm {t}going to{/t} update my résumé.", "履歴書を{t}更新するつもりです{/t}。", "I'm going to|update|my résumé."),
            ("I'm {t}going to{/t} take an English course.", "英語の講座を{t}受けるつもりです{/t}。", "I'm going to|take|an English course."),
            ("I'm {t}going to{/t} move next month.", "来月{t}引っ越すつもりです{/t}。", "I'm going to|move|next month."),
        ),
        p2=rows(
            ("{t}What are you going to{/t} do about it?", "それについて{t}どうするつもりですか{/t}？", "What are you going to|do|about it?"),
            ("{t}What are you going to{/t} buy for the trip?", "旅行のために{t}何を買うつもりですか{/t}？", "What are you going to|buy|for the trip?"),
            ("{t}What are you going to{/t} study next?", "次は{t}何を勉強するつもりですか{/t}？", "What are you going to|study|next?"),
            ("{t}What are you going to{/t} cook tonight?", "今夜は{t}何を作るつもりですか{/t}？", "What are you going to|cook|tonight?"),
        ),
        omit_choose=(1, 2),
        rules=(("Keep going to before the planned action.", "前から決めている行動の前に going to を置きます。"), ("Move are before you, then keep going to before the action.", "質問では are を you の前に移し、行動の前には going to を置きます。")),
        prompt=("Tell me one plan you have already made, then ask about mine.", "すでに決めている予定を一つ話して、私の予定も聞いてください。"),
    ),
    38: dict(
        slug="let-me-help", title="Let me help", ko="제가 도와드릴게요", ja="私が手伝います",
        goal=("Offer help now and make one promise with a deadline.", "その場で手伝いを申し出て、期限つきの約束を一つしましょう。"),
        p1=rows(
            ("{t}Let me{/t} carry that for you.", "それ、{t}私が運びますよ{/t}。", "Let me|carry that|for you."),
            ("{t}Let me{/t} open the door for you.", "ドアは{t}私が開けますよ{/t}。", "Let me|open the door|for you."),
            ("{t}Let me{/t} check the time for you.", "時間は{t}私が確認します{/t}。", "Let me|check the time|for you."),
            ("{t}Let me{/t} call the hotel for you.", "ホテルには{t}私が電話します{/t}。", "Let me|call the hotel|for you."),
        ),
        p2=rows(
            ("{t}Don’t worry, I’ll{/t} send it by noon.", "心配しないで、正午までに{t}送ります{/t}。", "Don't worry,|I'll send it|by noon."),
            ("{t}Don’t worry, I’ll{/t} call you by six.", "心配しないで、6時までに{t}電話します{/t}。", "Don't worry,|I'll call you|by six."),
            ("{t}Don’t worry, I’ll{/t} finish it by Friday.", "心配しないで、金曜日までに{t}終わらせます{/t}。", "Don't worry,|I'll finish it|by Friday."),
            ("{t}Don’t worry, I’ll{/t} bring it tomorrow.", "心配しないで、明日{t}持ってきます{/t}。", "Don't worry,|I'll bring it|tomorrow."),
        ),
        rules=(("Use Let me plus a plain verb to offer to do the action yourself.", "自分がその行動をすると申し出るときは Let me のあとに動詞の原形を置きます。"), ("Use I’ll for a decision you make as you speak, then name the deadline.", "話しながら今決めたことには I’ll を使い、そのあとに期限を伝えます。")),
        prompt=("Offer to help me now, then make a promise about a second task.", "今できる手助けを申し出てから、別の作業について約束してください。"),
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
            ("{t}If{/t} you are, {t}I’ll{/t} wait outside.", "{t}もし{/t}そうなら、外で{t}待ちます{/t}。", "If you are,|I'll wait|outside."),
            ("{t}If{/t} you’re busy, {t}I’ll{/t} call later.", "{t}もし{/t}忙しいなら、あとで{t}電話します{/t}。", "If you're busy,|I'll call|later."),
            ("{t}If{/t} the train is late, {t}I’ll{/t} wait here.", "{t}もし{/t}電車が遅れたら、ここで{t}待ちます{/t}。", "If the train is late,|I'll wait|here."),
            ("{t}If{/t} the café is full, {t}I’ll{/t} go somewhere else.", "{t}もし{/t}カフェが満席なら、別の場所に{t}行きます{/t}。", "If the café is full,|I'll go|somewhere else."),
        ),
        rules=(("Put a plain verb after might; do not add to or -s.", "might のあとは to や -s をつけず、動詞の原形を置きます。"), ("Use If for the uncertain condition and I’ll for your response.", "起こるか分からない条件には If、その場合の対応には I’ll を使います。")),
        prompt=("Tell me one thing that might change today, then agree on a backup.", "今日変わるかもしれないことを一つ話して、代わりの案を一緒に決めてください。"),
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
            ("{t}If it gets worse, you need to{/t} see a doctor.", "{t}悪化したら、医師に診てもらう必要があります{/t}。", "If it gets worse,|you need to|see a doctor."),
            ("{t}If you feel worse, you need to{/t} get help.", "{t}もっと具合が悪くなったら、助けを求める必要があります{/t}。", "If you feel worse,|you need to|get help."),
            ("{t}If you feel worse, you need to{/t} call home.", "{t}もっと具合が悪くなったら、家に電話する必要があります{/t}。", "If you feel worse,|you need to|call home."),
            ("{t}If it gets worse, you need to{/t} stop walking.", "{t}悪化したら、歩くのをやめる必要があります{/t}。", "If it gets worse,|you need to|stop walking."),
        ),
        rules=(("Use should plus a plain verb for an ordinary recommendation.", "ふつうの助言には should と動詞の原形を使います。"), ("Use need to when the action becomes necessary, not just a good idea.", "よい考えというだけでなく必要になった行動には need to を使います。")),
        prompt=("Tell me about a small problem, then give me one piece of advice too.", "小さな困りごとを話してから、私にも一つ助言してください。"),
    ),
    41: dict(
        slug="you-have-to-show-id", title="You have to show ID", ko="신분증을 보여줘야 해요", ja="身分証を見せる必要があります",
        goal=("Distinguish a requirement from something optional.", "必要なことと、しなくてもよいことを区別しましょう。"),
        p1=rows(
            ("You {t}have to{/t} show your ID.", "身分証を{t}見せる必要があります{/t}。", "You have to|show your ID."),
            ("You {t}have to{/t} wear a badge.", "バッジを{t}着ける必要があります{/t}。", "You have to|wear a badge."),
            ("You {t}have to{/t} book a time slot.", "時間枠を{t}予約する必要があります{/t}。", "You have to|book a time slot."),
            ("You {t}have to{/t} pay at the desk.", "受付で{t}支払う必要があります{/t}。", "You have to|pay at the desk."),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("But you {t}don't have to{/t} book ahead.", "でも、前もって{t}予約する必要はありません{/t}。", "But|you don't have to|book ahead."),
            ("But you {t}don't have to{/t} bring a photo.", "でも、写真を{t}持ってくる必要はありません{/t}。", "But|you don't have to|bring a photo."),
            ("But you {t}don't have to{/t} pay online.", "でも、オンラインで{t}支払う必要はありません{/t}。", "But|you don't have to|pay online."),
            ("But you {t}don't have to{/t} print the ticket.", "でも、チケットを{t}印刷する必要はありません{/t}。", "But|you don't have to|print the ticket."),
        ),
        rules=(("Use have to before a plain verb when a rule requires the action.", "決まりで必要な行動には have to と動詞の原形を使います。"), ("Don’t have to means optional. Mustn’t means forbidden; the two meanings are different.", "don’t have to は「しなくてもよい」、mustn’t は「してはいけない」です。この二つは意味が違います。")),
        prompt=("Explain one real rule you follow and one thing that is optional.", "実際に守っている決まりを一つと、しなくてもよいことを一つ説明してください。"),
    ),
    42: dict(
        slug="dont-you-like-it", title="Don't you like it?", ko="그거 안 좋아해요?", ja="それ、好きじゃないんですか？",
        goal=("Answer a negative question without reversing the fact.", "否定疑問に、事実を逆にせず答えましょう。"),
        p1=rows(
            ("{t}Actually, I do.{/t} I watch it every week.", "「この番組、好きじゃないんですか？」→ {t}いえ、好きです。{/t}毎週見ています。", "Actually,|I do.|I watch it every week."),
            ("{t}Actually, I do.{/t} I drink it every morning.", "「コーヒー、飲まないんですか？」→ {t}いえ、飲みます。{/t}毎朝飲んでいます。", "Actually,|I do.|I drink it every morning."),
            ("{t}Actually, I do.{/t} I work there on Fridays.", "「そこで働いていないんですか？」→ {t}いえ、働いています。{/t}金曜日はそこで働いています。", "Actually,|I do.|I work there on Fridays."),
            ("{t}Actually, I do.{/t} I cook it at home.", "「これ、作らないんですか？」→ {t}いえ、作ります。{/t}家で作っています。", "Actually,|I do.|I cook it at home."),
        ),
        p2=rows(
            ("No, {t}I don’t.{/t} I prefer comedies.", "「ドラマのほうが好きじゃないんですか？」→ いいえ、{t}そうではありません。{/t}コメディーのほうが好きです。", "No,|I don't.|I prefer comedies."),
            ("No, {t}I don’t.{/t} I prefer tea.", "「コーヒーのほうが好きじゃないんですか？」→ いいえ、{t}そうではありません。{/t}紅茶のほうが好きです。", "No,|I don't.|I prefer tea."),
            ("No, {t}I don’t.{/t} I prefer the other shop.", "「この店、好きじゃないんですか？」→ いいえ、{t}好きではありません。{/t}もう一方の店のほうが好きです。", "No,|I don't.|I prefer the other shop."),
            ("No, {t}I don’t.{/t} I prefer soup.", "「このサラダ、好きじゃないんですか？」→ いいえ、{t}好きではありません。{/t}スープのほうが好きです。", "No,|I don't.|I prefer soup."),
        ),
        rules=(("Answer the fact: use I do when the positive fact is true.", "質問が否定形でも、肯定の事実が正しければ I do で答えます。"), ("Use I don’t only when the negative fact is true.", "否定の事実が正しいときだけ I don’t で答えます。")),
        prompt=("Ask me a negative question, then answer one about your real preference.", "私に否定疑問を一つ聞いてから、自分の本当の好みについても答えてください。"),
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
        omit_choose=(1,),
        p2=rows(
            ("It’s {t}near{/t} the station.", "駅の{t}近くです{/t}。", "It's|near|the station."),
            ("It’s {t}near{/t} the café.", "カフェの{t}近くです{/t}。", "It's|near|the café."),
            ("It’s {t}near{/t} the hotel.", "ホテルの{t}近くです{/t}。", "It's|near|the hotel."),
            ("It’s {t}near{/t} the bank.", "銀行の{t}近くです{/t}。", "It's|near|the bank."),
        ),
        rules=(("Put both adjectives before the noun; adjectives do not take plural -s.", "二つの形容詞は名詞の前に置き、複数でも形容詞に -s はつけません。"), ("Put near before the place you use as the landmark.", "目印にする場所の前に near を置きます。")),
        prompt=("Describe one real place with two details, then tell me where it is.", "実際の場所を二つの特徴で説明してから、どこにあるかも教えてください。"),
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
        rules=(("Put too before the adjective when the amount causes a problem.", "程度が問題になるときは、形容詞の前に too を置きます。"), ("Put enough after the adjective when the amount falls short.", "程度が足りないときは、形容詞のあとに enough を置きます。")),
        prompt=("Tell me why one real option does not work for you.", "実際の選択肢が自分に合わない理由を一つ話してください。"),
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
            ("I {t}prefer{/t} this one {t}to{/t} that one.", "あちら{t}より{/t}こちらのほうが{t}好きです{/t}。", "I prefer|this one|to|that one."),
            ("I {t}prefer{/t} the window seat {t}to{/t} the aisle seat.", "通路側{t}より{/t}窓側の席のほうが{t}好きです{/t}。", "I prefer|the window seat|to|the aisle seat."),
            ("I {t}prefer{/t} the train {t}to{/t} the bus.", "バス{t}より{/t}電車のほうが{t}好きです{/t}。", "I prefer|the train|to|the bus."),
            ("I {t}prefer{/t} the small room {t}to{/t} the big room.", "大きい部屋{t}より{/t}小さい部屋のほうが{t}好きです{/t}。", "I prefer|the small room|to|the big room."),
        ),
        rules=(("Use the before every superlative. Add -est to short adjectives, put most before longer adjectives, and remember good becomes best.", "最上級の前には必ず the を置きます。短い形容詞には -est をつけ、長い形容詞の前には most を置き、good は best に変わることも覚えましょう。"), ("Use prefer A to B, not prefer A than B.", "A と B の好みを比べるときは prefer A to B の形にします。")),
        prompt=("Name the best option for you, then ask which option I prefer.", "自分にとって一番よい選択肢を言ってから、私の好みも聞いてください。"),
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
        prompt=("Tell me how one recent experience made you feel and what it was like.", "最近の体験でどう感じたかと、それがどんなものだったかを話してください。"),
    ),
}


VOCAB = {
    37: dict(new="look for|探す; new job|新しい仕事; update|更新する; résumé|履歴書; move|引っ越す; next month|来月", recycled="", assumed="job|仕事; buy|買う; study|勉強する; cook|料理する; course|講座; online course|オンライン講座; plan|予定; English|英語; trip|旅行; tonight|今夜", receptive="at some point|いつか; we'll see|どうなるか見てみよう; manager|上司; change jobs|転職する"),
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
    37: (("探す:look for; 新しい仕事:new job", "更新する:update; 履歴書:résumé", "受ける:course", "引っ越す:move; 来月:next month"), ("予定:plan", "買う:buy; 旅行:trip", "勉強する:study", "料理する:cook; 今夜:tonight")),
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
                ("{t}今決めました。{/t}心配しないで、明日持ってきます。", "Don’t worry, ", "I’ll", "I'm going to", " bring it tomorrow."),
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
                ("「ドラマのほうが好きじゃないんですか？」→ いいえ、{t}そうではありません。{/t}コメディーのほうが好きです。", ". I prefer comedies."),
                ("「コーヒーのほうが好きじゃないんですか？」→ いいえ、{t}そうではありません。{/t}紅茶のほうが好きです。", ". I prefer tea."),
                ("「この店、好きじゃないんですか？」→ いいえ、{t}好きではありません。{/t}もう一方の店のほうが好きです。", ". I prefer the other shop."),
                ("「このサラダ、好きじゃないんですか？」→ いいえ、{t}好きではありません。{/t}スープのほうが好きです。", ". I prefer soup."),
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


GOAL_EXCHANGES = {
    37: (("I’m going to look for a new job.", "新しい仕事を探すつもりです。"), ("What are you going to do first?", "まず何をするつもりですか？"), ("I’m going to update my résumé.", "履歴書を更新するつもりです。")),
    38: (("Let me carry that for you.", "それは私に運ばせてください。"), ("Thanks. Can you send this too?", "ありがとう。これも送ってもらえますか？"), ("Don’t worry, I’ll send it by noon.", "心配しないで、正午までに送ります。")),
    39: (("I might be a bit late.", "少し遅れるかもしれません。"), ("If you are, I’ll wait outside.", "もしそうなら、外で待ちます。"), ("Thanks. I’ll let you know.", "ありがとう。連絡します。")),
    40: (("I have a headache.", "頭が痛いです。"), ("You should get some rest.", "少し休んだほうがいいですよ。"), ("If it gets worse, you need to see a doctor.", "悪化したら、医師に診てもらう必要があります。")),
    41: (("You have to show your ID.", "身分証を見せる必要があります。"), ("Do I have to book ahead?", "前もって予約する必要がありますか？"), ("No, you don’t have to book ahead.", "いいえ、前もって予約する必要はありません。")),
    42: (("Don’t you like this show?", "この番組、好きじゃないんですか？"), ("Actually, I do. I watch it every week.", "いえ、好きです。毎週見ています。"), ("What about that one?", "あちらはどうですか？")),
    43: (("What’s the café like?", "そのカフェはどんな感じですか？"), ("It’s a small, quiet place.", "小さくて静かな場所です。"), ("It’s near the station.", "駅の近くです。")),
    44: (("How about this bag?", "このかばんはどうですか？"), ("It’s too small for me.", "私には小さすぎます。"), ("This one isn’t big enough either.", "こちらも十分な大きさではありません。")),
    46: (("Which one is best?", "どれが一番いいですか？"), ("It’s the best one here.", "ここではこれが一番いいです。"), ("I prefer this one to that one.", "あちらよりこちらのほうが好きです。")),
    47: (("How was the movie?", "映画はどうでしたか？"), ("I was bored during the movie.", "映画の間、退屈していました。"), ("The movie was really boring.", "その映画は本当に退屈でした。")),
}


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
            ("Thanks. Can you send the files too?", "ありがとう。ファイルも送ってもらえますか？"),
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
    37: (("text", "other", "Tutor", "Tell me one plan you've already decided on.", "すでに決めている予定を一つ教えてください。"), ("input", "me", "Me", "I'm going to ___.", "自分がすでに決めた予定"), ("text", "me", "Me", "What are you going to do next?", "次は何をするつもりですか？"), ("input", "other", "Tutor", "Tutor's answer: I'm going to ___.", "先生の本当の予定")),
    38: (("text", "other", "Tutor", "I need to carry this box.", "この箱を運ぶ必要があります。"), ("input", "me", "Me", "Let me ___ for you.", "箱について今すぐできる手助け"), ("text", "other", "Tutor", "Thanks. I also need to send these files by noon. Can you do that?", "ありがとう。このファイルも正午までに送る必要があります。お願いできますか？"), ("input", "me", "Me", "Don't worry, I'll ___ by ___.", "ファイルについての約束と期限"), ("text", "me", "Me", "Can you help me with something too?", "私のことも手伝ってもらえますか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の申し出")),
    39: (("text", "other", "Tutor", "Tell me one thing that might change today.", "今日変わるかもしれないことを一つ教えてください。"), ("input", "me", "Me", "I might ___.", "本当に起こるかもしれないこと"), ("text", "other", "Tutor", "Now give a backup for one uncertain condition.", "今度は、不確かな条件に対する代わりの案を言ってください。"), ("input", "me", "Me", "If ___, I'll ___.", "条件とその場合の対応"), ("text", "me", "Me", "What might change for you today?", "先生は今日、何が変わるかもしれませんか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の可能性と代わりの案")),
    40: (("text", "other", "Tutor", "I didn't sleep well last night. What should I do?", "昨夜よく眠れませんでした。どうしたらいいですか？"), ("input", "me", "Me", "You should ___.", "役に立つ現実的な助言"), ("text", "other", "Tutor", "What if I feel worse later?", "あとでもっと具合が悪くなったらどうしたらいいですか？"), ("input", "me", "Me", "If it gets worse, you need to ___.", "悪化した場合に必要な行動"), ("text", "me", "Me", "I have a headache. What should I do?", "頭が痛いです。どうしたらいいですか？"), ("input", "other", "Tutor", "Tutor's answer: You should ___.", "先生の役に立つ現実的な助言")),
    41: (("text", "other", "Tutor", "Explain one real rule you follow.", "実際に守っている決まりを一つ説明してください。"), ("input", "me", "Me", "You have to ___.", "本当に必要な行動"), ("text", "other", "Tutor", "What is optional there?", "そこで、しなくてもよいことは何ですか？"), ("input", "me", "Me", "But you don't have to ___.", "本当にしなくてもよい行動"), ("text", "me", "Me", "What is one rule you follow?", "先生が守っている決まりは何ですか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の決まりと任意のこと")),
    42: (("text", "other", "Tutor", "Don't you like coffee?", "コーヒー、好きじゃないんですか？"), ("input", "me", "Me", "Actually, I do. / No, I don't. I prefer ___.", "自分の事実に合う答え"), ("text", "me", "Me", "Don't you like ___?", "先生の好みについて否定疑問を一つ"), ("input", "other", "Tutor", "Tutor's answer: Actually, I do. / No, I don't.", "先生の本当の好み")),
    43: (("text", "other", "Tutor", "Describe one real place you know.", "知っている実際の場所を一つ説明してください。"), ("input", "me", "Me", "It's a ___, ___ place. It's near ___.", "役立つ二つの特徴と目印"), ("text", "me", "Me", "What is a place you know like?", "先生が知っている場所はどんな感じですか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の場所の特徴と位置")),
    44: (("text", "other", "Tutor", "Think of one real option that doesn't work for you.", "自分に合わない実際の選択肢を一つ考えてください。"), ("input", "me", "Me", "It's too ___ for me.", "限度を超えている理由"), ("text", "other", "Tutor", "Now describe something that falls short.", "今度は、必要な程度に足りないものを説明してください。"), ("input", "me", "Me", "This one isn't ___ enough.", "何が十分でないか"), ("text", "me", "Me", "What option doesn't work for you?", "先生に合わない選択肢は何ですか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の選択と理由")),
    46: (("text", "other", "Tutor", "Three ways to the airport: express—35 min; local—60 min; bus—¥1,800.", "空港までの三つの方法です。急行は35分、各駅停車は60分、バスは1,800円です。"), ("input", "me", "Me", "It's the ___ one here.", "fastest または cheapest を使った答え"), ("text", "other", "Tutor", "Now compare the express and the bus.", "今度は急行とバスを比べてください。"), ("input", "me", "Me", "I prefer ___ to ___.", "急行とバスについての自分の好み"), ("text", "me", "Me", "Which do you prefer, the express or the bus?", "急行とバスでは、どちらが好きですか？"), ("input", "other", "Tutor", "Tutor's answer: I prefer ___ to ___.", "先生の本当の好み")),
    47: (("text", "other", "Tutor", "Think of one recent experience.", "最近の体験を一つ思い出してください。"), ("input", "me", "Me", "I was ___ during / after ___.", "自分が本当に感じたこと"), ("text", "other", "Tutor", "What was the experience itself like?", "その体験自体はどんな感じでしたか？"), ("input", "me", "Me", "The ___ was really ___.", "気持ちを起こさせた体験の特徴"), ("text", "me", "Me", "How did a recent experience make you feel?", "最近の体験で、先生はどう感じましたか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の本当の気持ちと原因")),
}


LIVE_HINTS = {}
for number in NUMBERS:
    learner_inputs = [
        index for index, event in enumerate(LIVE_SCENES[number])
        if event[0:2] == ("input", "me")
    ]
    menus = OPEN_MENUS[number]
    LIVE_HINTS[number] = {
        index: menus[min(part, len(menus) - 1)]
        for part, index in enumerate(learner_inputs)
    }


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
        "LESSONS", "VOCAB", "KNOWN_WORDS", "TRANSLATE_HINTS", "OPEN_MENUS",
        "SPECS", "DIALOGUES", "LIVE_SCENES", "LIVE_HINTS",
        "FINAL_LINE_OWNERSHIP", "SUPPORT_LINE_OWNERS", "COURSE", "PILOT",
    )
    previous = {name: getattr(shell, name) for name in names}
    values = {
        "LESSONS": LESSONS, "VOCAB": VOCAB, "KNOWN_WORDS": KNOWN_WORDS,
        "TRANSLATE_HINTS": TRANSLATE_HINTS, "OPEN_MENUS": OPEN_MENUS,
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
    for part in data.get("omit_choose", ()):
        text, removed = re.subn(
            rf'\n    <div class="section" data-page-id="p{part}-choose".*?'
            rf'(?=\n    <div class="(?:section|transition-page)" data-page-id=|\n  </main>)',
            "", text, count=1, flags=re.DOTALL,
        )
        if removed != 1:
            raise ValueError(f"CORE-{number}: could not remove intentionally omitted p{part}-choose")
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
    preserved_text = preserved.read_text(encoding="utf-8")
    normalized_preserved = normalize_proofread_status(preserved_text)
    if normalized_preserved != preserved_text:
        if not args.refresh:
            raise SystemExit(f"refusing to update status in {preserved.relative_to(ROOT)}")
        preserved.write_text(normalized_preserved, encoding="utf-8")
        print(f"normalized {preserved.relative_to(ROOT)}")
    for number in NUMBERS:
        out, text = build(number, LESSONS[number])
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(NUMBERS)} Core decks generated; CORE-45 content preserved and status normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
