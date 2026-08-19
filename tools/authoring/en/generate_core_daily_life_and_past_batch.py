#!/usr/bin/env python3
"""Generate the explicit missing Core 25-36 daily-life batch.

CORE-32 is an already approved, separately authored canonical deck.  This
generator deliberately excludes it so refreshes cannot overwrite reviewed
source.  Every learner-facing decision for the other eleven decks is owned in
this file; the earlier Core generator is used only as the approved HTML shell.
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
COURSE = "core-daily-life-and-past"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
PRESERVED = TRACK / "courses/core-daily-life-and-past/lessons/32-we-went-out-for-dinner/lesson.html"
NUMBERS = (25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36)


def rows(*items):
    return items


LESSONS = {
    25: dict(slug="im-working-from-home-today", title="I'm working from home today", ko="오늘은 재택근무 중이에요", ja="今日は在宅勤務をしています",
        goal=("Say what you're doing at the moment.", "今していることを言いましょう。"),
        p1=rows(("I'm {t}working from home{/t} today.", "今日は{t}在宅勤務をしています{/t}。", "I'm working from home|today."), ("I'm {t}studying at home{/t} today.", "今日は{t}家で勉強しています{/t}。", "I'm studying at home|today."), ("I'm {t}taking it easy{/t} today.", "今日は{t}のんびりしています{/t}。", "I'm taking it easy|today."), ("I'm {t}cleaning the house{/t} today.", "今日は{t}家を掃除しています{/t}。", "I'm cleaning the house|today.")),
        p2=rows(("What are you {t}doing{/t}?", "何を{t}していますか{/t}？", "What are you doing?"), ("What are you {t}reading{/t}?", "何を{t}読んでいますか{/t}？", "What are you reading?"), ("What are you {t}making{/t}?", "何を{t}作っていますか{/t}？", "What are you making?"), ("What are you {t}watching{/t}?", "何を{t}見ていますか{/t}？", "What are you watching?")), omit_reorder=(1, 2),
        rules=(("Use am plus -ing for something happening now.", "今していることには am と -ing を使います。"), ("Put are before you in the question, then use the -ing action.", "質問では are を you の前に置き、動作を -ing 形にします。")), prompt=("Tell me what you're doing now, then ask me.", "今していることを話してから、私にも聞いてください。")),
    26: dict(slug="i-usually-drive-but-today-im-walking", title="I usually drive, but today I'm walking", ko="보통 운전하지만 오늘은 걸어요", ja="普段は車ですが、今日は歩いています",
        goal=("Contrast your usual routine with what's different today.", "普段の習慣と今日だけ違うことを比べましょう。"),
        p1=rows(("I {t}usually drive{/t} to work.", "{t}普段は車で{/t}通勤します。", "I|usually drive|to work."), ("I {t}usually walk{/t} to work.", "{t}普段は歩いて{/t}通勤します。", "I|usually walk|to work."), ("I {t}usually take the train{/t} to work.", "{t}普段は電車で{/t}通勤します。", "I|usually take the train|to work."), ("I {t}usually work{/t} at home.", "{t}普段は{/t}家で{t}働きます{/t}。", "I|usually work|at home.")),
        p2=rows(("But today I'm {t}walking{/t}.", "でも今日は{t}歩いています{/t}。", "But today I'm walking."), ("But today I'm {t}driving{/t}.", "でも今日は{t}車で行っています{/t}。", "But today I'm driving."), ("But today I'm {t}biking{/t}.", "でも今日は{t}自転車で行っています{/t}。", "But today I'm biking."), ("But today I'm {t}working{/t}.", "でも今日は{t}働いています{/t}。", "But today I'm working.")), omit_reorder=(2,),
        rules=(("Put usually before the plain action for a routine.", "習慣には usually を動作の原形の前に置きます。"), ("Use but today plus be and -ing for today's exception.", "今日だけ違うことには but today と be＋-ing を使います。")), prompt=("Tell me one usual routine and what's different today.", "普段の習慣と、今日だけ違うことを一つ話してください。")),
    27: dict(slug="i-like-cooking", title="I like cooking", ko="요리하는 걸 좋아해요", ja="料理が好きです",
        goal=("Talk about activities you like and dislike.", "好きな活動と苦手な活動について話しましょう。"),
        p1=rows(("I like {t}cooking{/t}.", "{t}料理すること{/t}が好きです。", "I like|cooking."), ("I like {t}walking{/t}.", "{t}歩くこと{/t}が好きです。", "I like|walking."), ("I like {t}reading{/t}.", "{t}読書{/t}が好きです。", "I like|reading."), ("I like {t}traveling{/t}.", "{t}旅行すること{/t}が好きです。", "I like|traveling.")), omit_reorder=(1,),
        p2=rows(("I {t}love{/t} walking, but I {t}hate{/t} running.", "歩くのは{t}大好き{/t}ですが、走るのは{t}大嫌い{/t}です。", "I love walking,|but|I hate running."), ("I {t}love{/t} cooking, but I {t}hate{/t} cleaning.", "料理は{t}大好き{/t}ですが、掃除は{t}大嫌い{/t}です。", "I love cooking,|but|I hate cleaning."), ("I {t}love{/t} reading, but I {t}hate{/t} writing.", "読書は{t}大好き{/t}ですが、書くのは{t}大嫌い{/t}です。", "I love reading,|but|I hate writing."), ("I {t}love{/t} traveling, but I {t}hate{/t} flying.", "旅行は{t}大好き{/t}ですが、飛行機は{t}大嫌い{/t}です。", "I love traveling,|but|I hate flying.")),
        rules=(("After like, use the activity in its -ing form.", "like のあとには活動を -ing 形で続けます。"), ("Use love and hate to show stronger opposite feelings.", "love と hate で、より強い反対の気持ちを表します。")), prompt=("Tell me one activity you like and one you don't.", "好きな活動と苦手な活動を一つずつ話してください。")),
    28: dict(slug="are-you-free-on-friday", title="Are you free on Friday?", ko="금요일에 시간 있어요?", ja="金曜日は空いていますか？",
        goal=("Check availability and invite someone to do something.", "相手の都合を確認して、何かに誘いましょう。"),
        p1=rows(("Are you free on {t}Friday{/t}?", "{t}金曜日{/t}は空いていますか？", "Are you free|on Friday?"), ("Are you free on {t}Saturday{/t}?", "{t}土曜日{/t}は空いていますか？", "Are you free|on Saturday?"), ("Are you free on {t}Sunday{/t}?", "{t}日曜日{/t}は空いていますか？", "Are you free|on Sunday?"), ("Are you free on {t}Tuesday{/t}?", "{t}火曜日{/t}は空いていますか？", "Are you free|on Tuesday?")),
        p2=rows(("Would you like to {t}have dinner{/t}?", "{t}夕食を食べませんか{/t}？", "Would you like to|have dinner?"), ("Would you like to {t}have lunch{/t}?", "{t}ランチを食べませんか{/t}？", "Would you like to|have lunch?"), ("Would you like to {t}see a movie{/t}?", "{t}映画を見ませんか{/t}？", "Would you like to|see a movie?"), ("Would you like to {t}go for a walk{/t}?", "{t}散歩に行きませんか{/t}？", "Would you like to|go for a walk?")), omit_reorder=(1, 2),
        rules=(("Use on directly before a day of the week.", "曜日の直前には on を使います。"), ("Keep Would you like to together, then add the activity.", "Would you like to をひとまとまりにして、活動を続けます。")), prompt=("Invite me to do something on a real day.", "実際の曜日を使って、私を何かに誘ってください。")),
    29: dict(slug="im-meeting-sam-at-six", title="I'm meeting Sam at six", ko="6시에 샘을 만나요", ja="6時にサムと会います",
        goal=("State an arrangement you've already made.", "すでに決まっている予定を伝えましょう。"),
        p1=rows(("I'm {t}meeting Sam at six{/t}.", "{t}6時にサムと会います{/t}。", "I'm meeting Sam at six."), ("I'm {t}having lunch with Emi at one{/t}.", "{t}1時にエミとランチを食べます{/t}。", "I'm having lunch with Emi at one."), ("I'm {t}seeing Ken at seven{/t}.", "{t}7時にケンと会います{/t}。", "I'm seeing Ken at seven."), ("I'm {t}calling Yuki at eight{/t}.", "{t}8時にユキに電話します{/t}。", "I'm calling Yuki at eight.")),
        p2=rows(("Are you still {t}coming on Tuesday{/t}?", "{t}火曜日は予定どおり来ますか{/t}？", "Are you still coming on Tuesday?"), ("Are you still {t}meeting us on Friday{/t}?", "{t}金曜日は予定どおり私たちに会いますか{/t}？", "Are you still meeting us on Friday?"), ("Are you still {t}working on Saturday{/t}?", "{t}土曜日は予定どおり仕事ですか{/t}？", "Are you still working on Saturday?"), ("Are you still {t}leaving on Sunday{/t}?", "{t}日曜日は予定どおり出発しますか{/t}？", "Are you still leaving on Sunday?")), omit_reorder=(1, 2),
        rules=(("Use be plus -ing for a plan already fixed in your diary.", "手帳に入っている決定済みの予定には be＋-ing を使います。"), ("Put still before the arranged -ing action to confirm it hasn't changed.", "予定が変わっていないか確かめるときは still を -ing の動作の前に置きます。")), prompt=("Tell me one fixed plan, then confirm one of mine.", "決まっている予定を一つ話してから、私の予定も確認してください。")),
    30: dict(slug="i-was-really-tired-yesterday", title="I was really tired yesterday", ko="어제 정말 피곤했어요", ja="昨日は本当に疲れていました",
        goal=("Say how you or a place were in the past.", "過去の自分や場所の様子を言いましょう。"),
        p1=rows(("I was {t}really tired{/t} yesterday.", "昨日は{t}本当に疲れていました{/t}。", "I was|really tired|yesterday."), ("I was {t}very busy{/t} yesterday.", "昨日は{t}とても忙しかったです{/t}。", "I was|very busy|yesterday."), ("I was {t}at home{/t} yesterday.", "昨日は{t}家にいました{/t}。", "I was|at home|yesterday."), ("I was {t}happy{/t} yesterday.", "昨日は{t}うれしかったです{/t}。", "I was|happy|yesterday.")),
        p2=rows(("There were a lot of {t}people{/t}.", "{t}人がたくさん{/t}いました。", "There were|a lot of people."), ("There were a lot of {t}cars{/t}.", "{t}車がたくさん{/t}ありました。", "There were|a lot of cars."), ("There were a lot of {t}meetings{/t}.", "{t}会議がたくさん{/t}ありました。", "There were|a lot of meetings."), ("There were a lot of {t}shops{/t}.", "{t}店がたくさん{/t}ありました。", "There were|a lot of shops.")), omit_reorder=(2,),
        rules=(("Use was with I, he, she, and it for a past state.", "過去の状態には I・he・she・it と was を使います。"), ("Use There were before a plural thing that existed.", "過去に複数のものがあったときは There were を使います。")), prompt=("Tell me how you were yesterday and what was around you.", "昨日の自分の様子と、周りに何があったかを話してください。")),
    31: dict(slug="i-went-out-last-night", title="I went out last night", ko="어젯밤에 나갔어요", ja="昨夜は出かけました",
        goal=("Say whether you went out or stayed in, with one detail.", "外出したか家にいたかを、詳しい情報と一緒に話しましょう。"),
        p1=rows(("I went to {t}a concert{/t} last night.", "昨夜は{t}コンサートに{/t}行きました。", "I went to|a concert|last night."), ("I went to {t}a restaurant{/t} last night.", "昨夜は{t}レストランに{/t}行きました。", "I went to|a restaurant|last night."), ("I went to {t}the gym{/t} last night.", "昨夜は{t}ジムに{/t}行きました。", "I went to|the gym|last night."), ("I went to {t}a friend's house{/t} last night.", "昨夜は{t}友人の家に{/t}行きました。", "I went to|a friend's house|last night.")),
        p2=rows(("I stayed home and {t}watched a movie{/t}.", "家にいて{t}映画を見ました{/t}。", "I stayed home|and|watched a movie."), ("I stayed home and {t}cooked dinner{/t}.", "家にいて{t}夕食を作りました{/t}。", "I stayed home|and|cooked dinner."), ("I stayed home and {t}read a book{/t}.", "家にいて{t}本を読みました{/t}。", "I stayed home|and|read a book."), ("I stayed home and {t}cleaned the house{/t}.", "家にいて{t}家を掃除しました{/t}。", "I stayed home|and|cleaned the house.")),
        rules=(("Use went to plus a place for a finished trip out.", "終わった外出には went to と場所を使います。"), ("Use stayed home and a past action for an evening in.", "家で過ごした夜には stayed home and のあとに過去の動作を続けます。")), prompt=("Tell me what you really did last night.", "昨夜、本当に何をしたか話してください。")),
    33: dict(slug="did-you-have-a-good-time", title="Did you have a good time?", ko="즐거운 시간 보냈어요?", ja="楽しかったですか？",
        goal=("Ask whether something happened and answer.", "過去の出来事についてたずね、答えましょう。"),
        p1=rows(("Did you {t}have a good time{/t}?", "{t}楽しかったですか{/t}？", "Did you|have a good time?"), ("Did you {t}see the movie{/t}?", "{t}その映画を見ましたか{/t}？", "Did you|see the movie?"), ("Did you {t}go to the concert{/t}?", "{t}コンサートに行きましたか{/t}？", "Did you|go to the concert?"), ("Did you {t}meet Sam{/t}?", "{t}サムに会いましたか{/t}？", "Did you|meet Sam?")),
        p2=rows(("Yes, we did. It was {t}great{/t}.", "はい。{t}最高でした{/t}。", "Yes, we did.|It was great."), ("Yes, we did. It was {t}fun{/t}.", "はい。{t}楽しかったです{/t}。", "Yes, we did.|It was fun."), ("Yes, we did. It was {t}interesting{/t}.", "はい。{t}面白かったです{/t}。", "Yes, we did.|It was interesting."), ("Yes, we did. It was {t}nice{/t}.", "はい。{t}よかったです{/t}。", "Yes, we did.|It was nice.")), omit_reorder=(1, 2),
        rules=(("Did carries the past, so keep the main verb plain.", "過去は Did が表すので、主な動詞は原形にします。"), ("Repeat did in the short answer, then add a past comment.", "短い答えでは did を繰り返し、そのあとに過去の感想を加えます。")), prompt=("Ask me about one past event, then give your own answer.", "過去の出来事を一つ私に聞いてから、自分の答えも言ってください。")),
    34: dict(slug="i-didnt-sleep-well", title="I didn't sleep well", ko="잠을 잘 못 잤어요", ja="よく眠れませんでした",
        goal=("Give a negative answer about the past and add a reason.", "過去について否定で答え、理由を加えましょう。"),
        p1=rows(("I didn't {t}sleep well{/t}.", "{t}よく眠れませんでした{/t}。", "I didn't|sleep well."), ("I didn't {t}eat breakfast{/t}.", "{t}朝食を食べませんでした{/t}。", "I didn't|eat breakfast."), ("I didn't {t}go out{/t}.", "{t}外出しませんでした{/t}。", "I didn't|go out."), ("I didn't {t}finish the work{/t}.", "{t}仕事を終えませんでした{/t}。", "I didn't|finish the work.")),
        p2=rows(("I had too much {t}coffee{/t}.", "{t}コーヒーを飲みすぎました{/t}。", "I had|too much coffee."), ("I had too much {t}work{/t}.", "{t}仕事が多すぎました{/t}。", "I had|too much work."), ("I had too much {t}food{/t}.", "{t}食べ物が多すぎました{/t}。", "I had|too much food."), ("I had too much {t}homework{/t}.", "{t}宿題が多すぎました{/t}。", "I had|too much homework.")), omit_reorder=(1, 2),
        rules=(("Didn't carries the past, so use the plain verb after it.", "過去は didn't が表すので、そのあとは動詞の原形を使います。"), ("Use too much before an uncountable amount that caused a problem.", "問題になるほど多い不可算の量には too much を使います。")), prompt=("Tell me one thing you didn't do and why.", "しなかったことを一つ、その理由と一緒に話してください。")),
    35: dict(slug="first-we-ate-then-we-walked-around", title="First we ate, then we walked around", ko="먼저 먹고, 그다음 걸어 다녔어요", ja="まず食べて、それから歩き回りました",
        goal=("Put three finished events in a clear order.", "終わった三つの出来事を分かりやすい順番で話しましょう。"),
        p1=rows(("First we {t}ate{/t}, and then we {t}walked around{/t}.", "まず{t}食べて{/t}、それから{t}歩き回りました{/t}。", "First we ate,|and then|we walked around."), ("First we {t}had coffee{/t}, and then we {t}went shopping{/t}.", "まず{t}コーヒーを飲んで{/t}、それから{t}買い物に行きました{/t}。", "First we had coffee,|and then|we went shopping."), ("First we {t}saw the park{/t}, and then we {t}had lunch{/t}.", "まず{t}公園を見て{/t}、それから{t}昼食を食べました{/t}。", "First we saw the park,|and then|we had lunch."), ("First we {t}met Sam{/t}, and then we {t}took a taxi{/t}.", "まず{t}サムに会って{/t}、それから{t}タクシーに乗りました{/t}。", "First we met Sam,|and then|we took a taxi.")),
        p2=rows(("In the end, we {t}took a taxi home{/t}.", "最後は{t}タクシーで帰りました{/t}。", "In the end,|we took a taxi home."), ("In the end, we {t}walked home{/t}.", "最後は{t}歩いて帰りました{/t}。", "In the end,|we walked home."), ("In the end, we {t}had dinner{/t}.", "最後は{t}夕食を食べました{/t}。", "In the end,|we had dinner."), ("In the end, we {t}went home{/t}.", "最後は{t}家に帰りました{/t}。", "In the end,|we went home.")), omit_reorder=(2,),
        rules=(("Put First at the start, then and then before the second event.", "First を文頭に置き、二つ目の出来事の前に and then を置きます。"), ("Put In the end at the start of the final event.", "最後の出来事の文頭には In the end を置きます。")), prompt=("Tell me three things you did in order.", "したことを三つ、順番に話してください。")),
    36: dict(slug="i-was-cooking-when-you-called", title="I was cooking when you called", ko="전화했을 때 요리 중이었어요", ja="電話をくれたとき、料理中でした",
        goal=("Say what was in progress when something else happened.", "別の出来事が起きたとき、何をしていたか言いましょう。"),
        p1=rows(("I was {t}cooking{/t} when you {t}called{/t}.", "あなたが{t}電話した{/t}とき、私は{t}料理をしていました{/t}。", "I was cooking|when|you called."), ("I was {t}walking{/t} when you {t}arrived{/t}.", "あなたが{t}着いた{/t}とき、私は{t}歩いていました{/t}。", "I was walking|when|you arrived."), ("I was {t}working{/t} when you {t}texted{/t}.", "あなたが{t}メッセージを送った{/t}とき、私は{t}働いていました{/t}。", "I was working|when|you texted."), ("I was {t}sleeping{/t} when you {t}knocked{/t}.", "あなたが{t}ノックした{/t}とき、私は{t}寝ていました{/t}。", "I was sleeping|when|you knocked.")),
        p2=rows(("While I was {t}cooking{/t}, he {t}set the table{/t}.", "私が{t}料理をしている間{/t}、彼は{t}テーブルを整えました{/t}。", "While I was cooking,|he set the table."), ("While I was {t}working{/t}, he {t}made coffee{/t}.", "私が{t}仕事をしている間{/t}、彼は{t}コーヒーを入れました{/t}。", "While I was working,|he made coffee."), ("While I was {t}cleaning{/t}, he {t}cooked dinner{/t}.", "私が{t}掃除をしている間{/t}、彼は{t}夕食を作りました{/t}。", "While I was cleaning,|he cooked dinner."), ("While I was {t}shopping{/t}, he {t}called me{/t}.", "私が{t}買い物をしている間{/t}、彼は{t}電話をくれました{/t}。", "While I was shopping,|he called me.")), omit_reorder=(2,),
        rules=(("Use was plus -ing for the longer action; put the interrupting past action after when.", "長く続いていた動作には was＋-ing、途中で起きた過去の動作には when を使います。"), ("Start with While plus the action in progress, then name the shorter finished action.", "While のあとに進行中の動作を置き、そのあとに短く終わった動作を言います。")), prompt=("Tell me what you were doing when something happened.", "何かが起きたとき、何をしていたか話してください。")),
}


VOCAB = {
25: dict(new="right now|今すぐ; at the moment|今; work from home|在宅勤務をする; take it easy|のんびりする", recycled="", assumed="today|今日; work|働く; do|する; study|勉強する; clean|掃除する; make|作る; read|読む; watch|見る; home|家; house|家", receptive="What are you doing?|何をしていますか？"),
26: dict(new="usually|普段; walk|歩く; bike|自転車で行く; take the train|電車で行く", recycled="drive|車で行く|CORE-14", assumed="today|今日; work|働く; at home|家で; home|家; train|電車; office|オフィス", receptive="every day|毎日; not today|今日は違う"),
27: dict(new="like|好き; love|大好き; hate|大嫌い; cooking|料理すること; walking|歩くこと; running|走ること; traveling|旅行すること", recycled="walk|歩く|CORE-26", assumed="read|読む; reading|読書; cleaning|掃除; writing|書くこと; flying|飛行機に乗ること", receptive="What do you like doing?|何をするのが好きですか？; not really my thing|あまり好みではない"),
28: dict(new="free|空いている; Friday|金曜日; Saturday|土曜日; Sunday|日曜日; Tuesday|火曜日; Would you like to ...?|…しませんか？; Yes, I'd love to.|ぜひ。; Sorry, I can't.|すみません、無理です。", recycled="", assumed="dinner|夕食; lunch|昼食; movie|映画; walk|散歩; see|見る; go|行く; day|曜日", receptive="How about ...?|…はどうですか？"),
29: dict(new="meet|会う; still|まだ・予定どおり; See you then.|では、そのときに。", recycled="Tuesday|火曜日|CORE-28; Friday|金曜日|CORE-28; Saturday|土曜日|CORE-28; Sunday|日曜日|CORE-28", assumed="meeting Ken|ケンと会う; have lunch|昼食をとる; lunch|昼食; see|会う; call|電話する; come|来る; work|働く; leave|出発する; us|私たち; Sam|サム; Emi|エミ; Ken|ケン; Yuki|ユキ; one|1時; six|6時; seven|7時; eight|8時", receptive="What time?|何時ですか？; arrangement|決まった予定"),
30: dict(new="was|be の過去形; were|be の過去形; yesterday|昨日; tired|疲れた; busy|忙しい; a lot of|たくさんの; meeting|会議", recycled="shop|店|CORE-10", assumed="really|本当に; very|とても; at home|家で; home|家; happy|うれしい; people|人々; cars|車", receptive="to be honest|正直に言うと; for some reason|なぜか"),
31: dict(new="went|go の過去形; stayed|stay の過去形; watched|watch の過去形; cooked|cook の過去形; cleaned|clean の過去形; concert|コンサート; last night|昨夜", recycled="restaurant|レストラン|CORE-10", assumed="movie|映画; dinner|夕食; read|読む; gym|ジム; book|本; friend|友人; friend's house|友人の家; house|家; home|家; It was fun.|楽しかったです。; Nothing special.|特に何も。", receptive=""),
33: dict(new="did|do の過去形; good time|楽しい時間; great|最高の; interesting|面白い; Not bad.|悪くない", recycled="was|be の過去形|CORE-30; went|go の過去形|CORE-31; had|have の過去形|CORE-32; saw|see の過去形|CORE-32; concert|コンサート|CORE-31; meet|会う|CORE-29", assumed="have|過ごす; see|見る; go|行く; movie|映画; Sam|サム; fun|楽しい; nice|よい", receptive="How was it?|どうでしたか？"),
34: dict(new="didn't|～しなかった; sleep well|よく眠る; go out|外出する; too much|多すぎる; unfortunately|残念ながら; That's why.|だからです。", recycled="had|have の過去形|CORE-32; coffee|コーヒー|CORE-9", assumed="eat|食べる; finish|終える; breakfast|朝食; work|仕事; food|食べ物; homework|宿題", receptive="What happened?|どうしたのですか？"),
35: dict(new="ate|eat の過去形; met|meet の過去形; first|まず; and then|それから; in the end|最後には; walked around|歩き回った; finally|最後に", recycled="had|have の過去形|CORE-32; went|go の過去形|CORE-31; saw|see の過去形|CORE-32; took|take の過去形|CORE-32", assumed="walked home|歩いて帰った; taxi|タクシー; dinner|夕食; lunch|昼食; shopping|買い物; home|家; park|公園; Sam|サム; coffee|コーヒー", receptive="after that|そのあと"),
36: dict(new="when|…したとき; while|…している間; called|電話した; arrived|到着した; texted|メッセージを送った; knocked|ノックした; set the table|食卓を整えた; all of a sudden|突然", recycled="was|be の過去形|CORE-30; cooking|料理すること|CORE-27; walking|歩くこと|CORE-27; cleaned|掃除した|CORE-31; cooked|料理した|CORE-31; coffee|コーヒー|CORE-9", assumed="working|働いている; sleeping|寝ている; shopping|買い物; dinner|夕食; table|テーブル; made|作った; happened|起きた; at that moment|そのとき", receptive=""),
}

PRODUCTIVE_VOCABULARY = {
25: {"work from home", "take it easy", "study", "clean", "do", "make", "read", "watch", "today", "home", "house"},
26: {"usually", "drive", "walk", "bike", "take the train", "work", "today", "at home"},
27: {"like", "love", "hate", "cooking", "walking", "running", "reading", "traveling", "cleaning", "writing", "flying"},
28: {"free", "friday", "saturday", "sunday", "tuesday", "dinner", "lunch", "movie", "walk", "see", "go"},
29: {"meet", "still", "meeting ken", "have lunch", "see", "call", "come", "work", "leave", "sam", "emi", "ken", "yuki", "one", "six", "seven", "eight"},
30: {"was", "were", "yesterday", "tired", "busy", "very", "a lot of", "meeting", "shop", "people", "cars", "happy", "at home"},
31: {"went", "stayed", "watched", "cooked", "cleaned", "concert", "restaurant", "movie", "dinner", "read", "gym", "book", "friend's house", "house", "home", "it was fun.", "nothing special."},
33: {"did", "good time", "great", "interesting", "not bad.", "was", "went", "had", "saw", "concert", "meet", "have", "see", "go", "movie", "sam", "fun", "nice"},
34: {"didn't", "sleep well", "go out", "too much", "had", "coffee", "eat", "finish", "breakfast", "work", "food", "homework"},
35: {"ate", "met", "first", "and then", "in the end", "walked around", "walked home", "had", "went", "saw", "took", "taxi", "dinner", "lunch", "shopping", "home", "park", "sam", "coffee"},
36: {"when", "while", "called", "arrived", "texted", "knocked", "set the table", "all of a sudden", "at that moment", "was", "cooking", "walking", "cleaned", "cooked", "coffee", "working", "sleeping", "shopping", "dinner", "happened"},
}

KNOWN_WORDS = {
25: (("ホーム", "home"), ("ワーク", "work"), ("ハウス", "house")), 26: (("トレイン", "train"), ("バイク", "bike"), ("ホーム", "home")), 27: (("クッキング", "cooking"), ("ランニング", "running"), ("トラベリング", "traveling")), 28: (("ディナー", "dinner"), ("ランチ", "lunch"), ("ムービー", "movie")), 29: (("サム", "Sam"), ("エミ", "Emi"), ("ケン", "Ken")), 30: (("ミーティング", "meeting"), ("ショップ", "shop"), ("ホーム", "home")), 31: (("コンサート", "concert"), ("レストラン", "restaurant"), ("ジム", "gym")), 33: (("コンサート", "concert"), ("ムービー", "movie"), ("サム", "Sam")), 34: (("コーヒー", "coffee"), ("ブレックファスト", "breakfast"), ("ワーク", "work")), 35: (("タクシー", "taxi"), ("ショッピング", "shopping"), ("コーヒー", "coffee")), 36: (("テーブル", "table"), ("ディナー", "dinner"), ("コーヒー", "coffee")),
}


CHOICE_CUES = {
    (26, 1): ("{t}普段は{/t}車で通勤します。", "{t}普段は{/t}歩いて通勤します。", "{t}普段は{/t}電車で通勤します。", "{t}普段は{/t}家で働きます。"),
    (27, 2): ("歩くのは{t}大好き{/t}ですが、走るのは大嫌いです。", "料理は{t}大好き{/t}ですが、掃除は大嫌いです。", "読書は{t}大好き{/t}ですが、書くのは大嫌いです。", "旅行は{t}大好き{/t}ですが、飛行機は大嫌いです。"),
    (35, 1): ("{t}まず{/t}食べて、それから歩き回りました。", "{t}まず{/t}コーヒーを飲んで、それから買い物に行きました。", "{t}まず{/t}公園を見て、それから昼食を食べました。", "{t}まず{/t}サムに会って、それからタクシーに乗りました。"),
    (36, 1): ("電話が来たとき、{t}料理をしていました{/t}。", "着いたとき、{t}歩いていました{/t}。", "メッセージが来たとき、{t}働いていました{/t}。", "ノックが聞こえたとき、{t}寝ていました{/t}。"),
    (36, 2): ("{t}料理をしている間{/t}、彼は食卓を整えました。", "{t}仕事をしている間{/t}、彼はコーヒーを入れました。", "{t}掃除をしている間{/t}、彼は夕食を作りました。", "{t}買い物をしている間{/t}、彼は電話をくれました。"),
}


def choice_rows(number, part, pattern, corrects, distractors):
    out = []
    cues = CHOICE_CUES.get((number, part), tuple(row[1] for row in pattern))
    for (_en, _ja, _chunks), ja, correct, distractor in zip(pattern, cues, corrects, distractors, strict=True):
        plain = core.strip_marks(_en)
        prefix, suffix = plain.split(correct, 1)
        out.append((ja, prefix, correct, distractor, suffix))
    return tuple(out)


def make_spec(n, meanings, writes, corrects, distractors, rule_details, tip):
    return dict(meanings=meanings, writes=writes,
        choices=(choice_rows(n, 1, LESSONS[n]["p1"], corrects[0], distractors[0]), choice_rows(n, 2, LESSONS[n]["p2"], corrects[1], distractors[1])),
        rules=rule_details, tip=tip)


def rule(title, ja, formula, head, head_ja, a, b): return (title, ja, formula, head, head_ja, (a, b))
def tip(title, ja, script, script_ja, left, right): return (title, ja, script, script_ja, left, right)


SPECS = {}
for n in NUMBERS:
    d = LESSONS[n]
    meanings = ((d["rules"][0][0], d["rules"][0][1]), (d["rules"][1][0], d["rules"][1][1]))
    writes = (("Write one true sentence with Pattern 1.", "パターン1で本当の文を一つ書きましょう。"), ("Write one true sentence with Pattern 2.", "パターン2で本当の文を一つ書きましょう。"))
    # Explicit word-level decisions; each correct item is a substring in its row.
    correct = {
      25: (("working", "studying", "taking", "cleaning"), ("doing", "reading", "making", "watching")),
      26: (("usually",)*4, ("walking", "driving", "biking", "working")),
      27: (("cooking", "walking", "reading", "traveling"), ("love",)*4),
      28: (("Friday", "Saturday", "Sunday", "Tuesday"), ("have", "have", "see", "go")),
      29: (("meeting", "having", "seeing", "calling"), ("coming", "meeting", "working", "leaving")),
      30: (("was",)*4, ("were",)*4),
      31: (("went",)*4, ("stayed",)*4),
      33: (("have", "see", "go", "meet"), ("great", "fun", "interesting", "nice")),
      34: (("sleep", "eat", "go", "finish"), ("too much",)*4),
      35: (("First",)*4, ("In the end",)*4),
      36: (("was cooking", "was walking", "was working", "was sleeping"), ("was cooking", "was working", "was cleaning", "was shopping")),
    }[n]
    wrong = {
      25: (("work", "study", "take", "clean"), ("do", "read", "make", "watch")),
      26: (("today",)*4, ("walk", "drive", "bike", "work")),
      27: (("cook", "walk", "read", "travel"), ("like",)*4),
      28: (("Friday's", "Saturday's", "Sunday's", "Tuesday's"), ("having", "having", "seeing", "going")),
      29: (("meet", "have", "see", "call"), ("come", "meet", "work", "leave")),
      30: (("were",)*4, ("was",)*4),
      31: (("go",)*4, ("stay",)*4),
      33: (("had", "saw", "went", "met"), ("greatly", "funny", "interest", "nicely")),
      34: (("slept", "ate", "went", "finished"), ("too many",)*4),
      35: (("Then",)*4, ("At first",)*4),
      36: (("cooked", "walked", "worked", "slept"), ("cooked", "worked", "cleaned", "shopped")),
    }[n]
    rd = (
      rule("See the operation", "形の変化を見よう", d["rules"][0][0], "Pattern 1", "パターン1", core.strip_marks(d["p1"][0][0]), core.strip_marks(d["p1"][1][0])),
      rule("See the operation", "形の変化を見よう", d["rules"][1][0], "Pattern 2", "パターン2", core.strip_marks(d["p2"][0][0]), core.strip_marks(d["p2"][1][0])),
    )
    tips = {
      25: tip("Right now or at the moment?", "right now と at the moment", "Both mean now; right now is more immediate, while at the moment sounds a little less urgent.", "どちらも「今」ですが、right now はより即時的で、at the moment は少し切迫感が弱い表現です。", ("Immediate", "まさに今", "I'm working right now.", "今まさに仕事中です。"), ("Current situation", "現在の状況", "I'm working at the moment.", "今は仕事中です。")),
      26: tip("Usually or every day?", "usually と every day", "Usually describes the normal pattern; every day says it happens on each day.", "usually は普段の傾向、every day は毎日起きることを表します。", ("Normal pattern", "普段の傾向", "I usually drive.", "普段は車で行きます。"), ("Each day", "毎日", "I drive every day, but not today.", "毎日車で行きますが、今日は違います。")),
      27: tip("Hate or not really my thing?", "hate と not really my thing", "Hate is strong; not really my thing is a softer, conversational way to say you don't enjoy an activity.", "hate は強い表現で、not really my thing は活動があまり好みではないとやわらかく伝える会話表現です。", ("Strong dislike", "強い苦手意識", "I hate running.", "走るのが大嫌いです。"), ("Softer dislike", "やわらかい言い方", "Running isn't really my thing.", "走るのはあまり好みではありません。")),
      28: tip("I'd love to or Sounds good?", "I'd love to と Sounds good", "Both accept an invitation; I'd love to sounds more enthusiastic.", "どちらも誘いを受ける表現ですが、I'd love to のほうが喜びが強く伝わります。", ("Warm acceptance", "喜んで受ける", "Yes, I'd love to.", "はい、ぜひ。"), ("Casual acceptance", "気軽に受ける", "Sounds good.", "いいですね。")),
      29: tip("Still coming?", "still coming のニュアンス", "Still checks that an arrangement remains unchanged; it doesn't mean the person is already traveling.", "still は、すでに移動中という意味ではなく、予定が変わっていないかを確認します。", ("Confirm the plan", "予定を再確認", "Are you still coming on Tuesday?", "火曜日は予定どおり来ますか？"), ("Ask about this moment", "今をたずねる", "Are you coming now?", "今、来ていますか？")),
      30: tip("To be honest or for some reason?", "to be honest と for some reason", "To be honest introduces a frank admission; for some reason says you don't know the cause.", "to be honest は率直に話す前置き、for some reason は原因が分からないときに使います。", ("Frank admission", "率直に言う", "To be honest, I was tired.", "正直に言うと、疲れていました。"), ("Unknown cause", "原因が分からない", "For some reason, I was tired.", "なぜか疲れていました。")),
      31: tip("Went out or went to...?", "went out と went to", "Went out gives the general idea; went to names the destination.", "went out は外出したこと全体、went to は行き先を伝えます。", ("General", "外出したことだけ", "I went out last night.", "昨夜は外出しました。"), ("Specific destination", "行き先も伝える", "I went to a concert.", "コンサートに行きました。")),
      33: tip("How was it?", "How was it?", "After a yes answer, ask for the person's impression with How was it.", "Yes の答えのあと、How was it? で自然に感想を聞けます。", ("Check whether it happened", "起きたか確認", "Did you see the movie?", "映画を見ましたか？"), ("Ask for an impression", "感想を聞く", "How was it?", "どうでしたか？")),
      34: tip("Unfortunately", "unfortunately の位置", "Put Unfortunately at the front when the bad result matters to the listener.", "残念な結果を伝えるときは、Unfortunately を文頭に置けます。", ("Plain fact", "事実だけ", "I didn't finish the work.", "仕事を終えませんでした。"), ("Signals bad news", "残念な知らせ", "Unfortunately, I didn't finish.", "残念ながら、終わりませんでした。")),
      35: tip("In the end or finally?", "in the end と finally", "In the end emphasizes the final result; finally emphasizes the last step or a long wait.", "in the end は最終的な結果、finally は最後の手順や長く待った末のことを強調します。", ("Final result", "最終的な結果", "In the end, we went home.", "結局、家に帰りました。"), ("Last step", "最後の手順", "Finally, we took a taxi.", "最後にタクシーに乗りました。")),
      36: tip("All of a sudden or at that moment?", "all of a sudden と at that moment", "All of a sudden emphasizes surprise; at that moment only locates the event in time.", "all of a sudden は突然だったことを強調し、at that moment はその時点を示すだけです。", ("Unexpected event", "突然の出来事", "All of a sudden, you called.", "突然、あなたから電話がありました。"), ("Point in time", "その時点", "At that moment, you called.", "そのとき、あなたから電話がありました。")),
    }[n]
    SPECS[n] = make_spec(n, meanings, writes, correct, wrong, rd, tips)


TRANSLATE_HINTS = {
25: (("在宅勤務:work from home", "家:home; 勉強する:study", "のんびりする:take it easy", "家:house; 掃除する:clean"), ("する:do", "読む:read", "作る:make", "見る:watch")),
26: (("車で行く:drive", "歩く:walk", "電車:train", "家で:at home; 働く:work"), ("歩く:walk", "車で行く:drive", "自転車で行く:bike", "働く:work")),
27: (("料理:cooking", "歩くこと:walking", "読書:reading", "旅行:traveling"), ("歩くこと:walking", "料理:cooking", "読書:reading", "旅行:traveling")),
28: (("金曜日:Friday", "土曜日:Saturday", "日曜日:Sunday", "火曜日:Tuesday"), ("夕食:dinner", "昼食:lunch", "映画:movie", "散歩:walk")),
29: (("サム:Sam; 6時:six", "エミ:Emi; 昼食:lunch; 1時:one", "ケン:Ken; 7時:seven", "ユキ:Yuki; 8時:eight"), ("火曜日:Tuesday", "金曜日:Friday", "土曜日:Saturday", "日曜日:Sunday")),
30: (("疲れた:tired", "忙しい:busy", "家で:at home", "うれしい:happy"), ("人々:people", "車:cars", "会議:meeting", "店:shop")),
31: (("コンサート:concert", "レストラン:restaurant", "ジム:gym", "友人の家:friend's house"), ("映画:movie", "夕食:dinner", "本:book", "家:house")),
33: (("楽しい時間:good time", "映画:movie", "コンサート:concert", "サム:Sam"), ("最高:great", "楽しい:fun", "面白い:interesting", "よい:nice")),
34: (("よく眠る:sleep well", "朝食:breakfast", "外出する:go out", "仕事:work"), ("コーヒー:coffee", "仕事:work", "食べ物:food", "宿題:homework")),
35: (("食べた:ate; 歩き回った:walked around", "コーヒー:coffee; 買い物:shopping", "公園:park; 昼食:lunch", "サム:Sam; タクシー:taxi"), ("タクシー:taxi", "家:home", "夕食:dinner", "家:home")),
36: (("料理:cooking; 電話した:called", "歩くこと:walking; 到着した:arrived", "仕事中:working; メッセージを送った:texted", "寝ている:sleeping; ノックした:knocked"), ("料理:cooking; 食卓を整える:set the table", "仕事中:working; コーヒー:coffee", "掃除した:cleaned; 夕食:dinner", "買い物:shopping; 電話した:called")),
}
OPEN_MENUS = {n: (TRANSLATE_HINTS[n][0][:3], TRANSLATE_HINTS[n][1][:3]) for n in NUMBERS}


def dlg(role, p1, p2, first, follow, close, last): return (role, p1, p2, first, follow, close, last)
DIALOGUES = {
25: dict(model=dlg("Coworker",0,1,("What are you doing right now?","今は何をしていますか？"),("I'm reading a report at the moment.","今はレポートを読んでいます。"),("A sales report. What are you doing after work?","営業レポートです。仕事のあとは何をしますか？"),("I'm taking it easy today.","今日はのんびりしています。")), wild=dlg("Friend",2,3,("What are you doing at the moment?","今は何をしているの？"),("I'm watching something at the moment.","今、何かを見ているよ。"),("A movie. What are you doing after that?","映画だよ。そのあとは何をするの？"),("I'm taking it easy today.","今日はのんびりしています。"))),
26: dict(model=dlg("Coworker",0,0,("How do you usually get to work?","普段はどうやって通勤しますか？"),("What's different today?","今日は何が違いますか？"),("And how do you travel most days?","では、普段はどうやって通勤しますか？"),("I usually drive to work.","普段は車で通勤します。")), wild=dlg("Coworker",2,2,("How do you usually get to work?","普段はどうやって通勤しますか？"),("And today?","今日は？"),("Sorry, how are you going today?","すみません、今日はどうやって行きますか？"),("But today I'm biking.","でも今日は自転車で行っています。"))),
27: dict(model=dlg("Friend",0,0,("What do you like doing?","何をするのが好き？"),("Anything you feel strongly about?","大好きなことや苦手なことは？"),("What do you like most?","一番好きなのは？"),("I like cooking.","料理が好きです。")), wild=dlg("Friend",3,3,("What do you like doing on vacation?","休暇中は何をするのが好き？"),("What about flying?","飛行機はどう？"),("So what do you like doing?","では、何をするのが好き？"),("I like traveling.","旅行が好きです。"))),
28: dict(model=dlg("Friend",0,0,("I don't have plans for Friday yet.","金曜日はまだ予定がないよ。"),("Yes, I am.","うん、空いているよ。"),("I'd love to. Would you like to see a movie afterward?","ぜひ。そのあと映画も見ない？"),("Yes, I'd love to.","うん、ぜひ。")), wild=dlg("Coworker",1,1,("Saturday might work for me.","土曜日なら都合がいいかもしれません。"),("Yes, I am.","はい、空いています。"),("Sorry, I can't have lunch. Are you free on Sunday?","すみません、ランチは無理です。日曜日は空いていますか？"),("Sorry, I can't.","すみません、無理です。"))),
29: dict(model=dlg("Friend",0,0,("What time are you meeting Sam?","サムとは何時に会うの？"),("I think we also have plans on Tuesday.","火曜日にも予定があったと思うよ。"),("Yes, I'm still coming.","うん、予定どおり行くよ。"),("See you then.","では、そのときに。")), wild=dlg("Coworker",1,1,("What time are you having lunch with Emi?","エミとは何時にランチですか？"),("I have our Friday meeting in my calendar.","金曜日の打ち合わせが予定に入っています。"),("Yes, Friday is unchanged.","はい、金曜日は変更ありません。"),("See you then.","では、そのときに。"))),
30: dict(model=dlg("Friend",0,0,("How were you yesterday?","昨日はどうだった？"),("Why was the station so busy?","なぜ駅はそんなに混んでいたの？"),("How did you feel after that?","そのあと、どんな様子だった？"),("I was really tired yesterday.","昨日は本当に疲れていました。")), wild=dlg("Coworker",1,2,("How were you yesterday?","昨日はどうでしたか？"),("What made work busy?","なぜ仕事が忙しかったのですか？"),("So how were you yesterday?","それで、昨日はどうでしたか？"),("I was very busy yesterday.","昨日はとても忙しかったです。"))),
31: dict(model=dlg("Friend",0,0,("Did you go out last night?","昨夜は外出したの？"),("What did you do the evening before?","その前の夜は何をしたの？"),("How was the concert?","コンサートはどうだった？"),("It was fun.","楽しかったです。")), wild=dlg("Coworker",1,1,("Where did you go last night?","昨夜はどこへ行きましたか？"),("What did you do the evening before?","その前の夜は何をしましたか？"),("How was the quiet evening at home?","家で過ごした静かな夜はどうでしたか？"),("Nothing special.","特に何も。"))),
33: dict(model=dlg("Friend",0,0,("My friends and I went to a party last night.","昨夜、友達とパーティーに行ったよ。"),("Yes, we did. Did you and your friends have a good time on your trip?","うん、楽しかったよ。あなたと友達も旅行は楽しかった？"),("How was the food there?","向こうの食事はどうだった？"),("Not bad.","悪くなかったです。")), wild=dlg("Coworker",2,2,("My friends and I went out on Friday.","金曜日に友達と出かけました。"),("Yes, we did. Did you and your coworkers have a good time at the movie?","はい、行きました。あなたと同僚も映画は楽しかったですか？"),("How was the movie?","映画はどうでしたか？"),("Not bad.","悪くなかったです。"))),
34: dict(model=dlg("Coworker",0,0,("You look tired. What happened?","疲れて見えます。どうしたの？"),("Why didn't you sleep well?","どうしてよく眠れなかったの？"),("So the coffee caused the problem?","つまり、コーヒーが原因だったの？"),("That's why I didn't sleep well.","だから、よく眠れませんでした。")), wild=dlg("Friend",2,3,("Did you go out yesterday?","昨日は外出した？"),("Why did you stay in?","なぜ家にいたの？"),("So the homework kept you home?","つまり、宿題があったから家にいたの？"),("That's why I didn't go out.","だから、外出しませんでした。"))),
35: dict(model=dlg("Friend",0,0,("What did you do downtown?","街では何をしたの？"),("What happened after that?","そのあとはどうなったの？"),("How did you get home in the end?","最後はどうやって帰ったの？"),("In the end, we took a taxi home.","最後はタクシーで帰りました。")), wild=dlg("Coworker",1,1,("Tell me about your afternoon.","午後のことを教えて。"),("What happened after that?","そのあとはどうなりましたか？"),("What did you do before the ending?","最後の前には何をしましたか？"),("First we had coffee, and then we went shopping.","まずコーヒーを飲んで、それから買い物に行きました。"))),
36: dict(model=dlg("Friend",0,0,("What were you doing when I called?","電話したとき何をしていたの？"),("What did he do while you were cooking?","あなたが料理中、彼は何をしたの？"),("Was my call expected?","私の電話は予想していた？"),("No—it happened all of a sudden.","ううん、突然だったよ。")), wild=dlg("Coworker",1,1,("What were you doing when I arrived?","私が着いたとき何をしていましたか？"),("What did he do while you were working?","仕事中、彼は何をしましたか？"),("When did he make coffee?","彼がコーヒーを入れたのはいつですか？"),("At that moment.","そのときです。"))),
}

LIVE_SCENES = {
25: (("text","other","Tutor","What are you doing today?","今日は何をしていますか？"),("input","me","Me","I'm ___ing today.","今日、本当にしていること"),("text","other","Tutor","Now ask what I'm doing.","今度は、私が何をしているか聞いてください。"),("input","me","Me","What are you ___ing?","聞きたい動作"),("input","other","Tutor","Tutor's answer","先生の本当の答え")),
26: (("text","other","Tutor","How do you usually get to work?","普段はどうやって通勤しますか？"),("input","me","Me","I usually ___.","本当の習慣"),("text","other","Tutor","What's different today?","今日は何が違いますか？"),("input","me","Me","But today I'm ___ing.","今日だけ違うこと"),("text","me","Me","How about you?","あなたはどうですか？"),("input","other","Tutor","Tutor's answer: usual routine and today's exception","先生の本当の習慣と今日だけ違うこと")),
27: (("text","other","Tutor","What do you like doing?","何をするのが好きですか？"),("input","me","Me","I like ___ing.","本当に好きな活動"),("text","other","Tutor","Name one activity you love and one you hate.","大好きな活動と苦手な活動を一つずつ言ってください。"),("input","me","Me","I love ___ing, but I hate ___ing.","自分の本当の好み"),("text","me","Me","What do you like doing?","あなたは何をするのが好きですか？"),("input","other","Tutor","Tutor's answer: real preferences","先生の本当の好み")),
28: (("text","other","Tutor","Ask whether I'm free on a real day.","実際の曜日を使って、私が空いているか聞いてください。"),("input","me","Me","Are you free on ___?","実際の曜日"),("input","other","Tutor","Tutor's answer: Say yes, or say no and name a day you are free.","はい、または、いいえのあとに空いている曜日を言う"),("text","other","Tutor","Use the day I said I was free, then invite me.","先生が空いていると言った曜日を使って、誘ってください。"),("input","me","Me","Would you like to ___?","先生が空いている日の実際の誘い"),("input","other","Tutor","Tutor's answer: Yes, I'd love to. / Sorry, I can't, and give a reason.","先生の本当の返事と理由")),
29: (("text","other","Tutor","Tell me one plan already in your diary.","手帳に入っている予定を一つ教えてください。"),("input","me","Me","I'm ___ing ___ at ___.","実際の決定済みの予定"),("text","other","Tutor","I'm meeting Ken on Tuesday.","私は火曜日にケンと会います。"),("text","other","Tutor","Use my activity and day to confirm my plan.","私の動作と曜日で、予定を確認してください。"),("input","me","Me","Are you still ___ing on ___?","先生の予定の meeting Ken と Tuesday"),("input","other","Tutor","Tutor's answer: Yes, I am. / No, I'm not, with the changed plan.","先生の本当の答えと変更後の予定")),
30: (("text","other","Tutor","How were you yesterday?","昨日はどうでしたか？"),("input","me","Me","I was ___ yesterday.","昨日の本当の様子"),("text","other","Tutor","What was there around you?","周りには何がありましたか？"),("input","me","Me","There were a lot of ___.","実際にたくさんあったもの"),("text","me","Me","How about you?","あなたはどうでしたか？"),("input","other","Tutor","Tutor's answer: past state and what was there","先生の昨日の様子と、周りにあったもの")),
31: (("text","other","Tutor","Tell me about one evening when you went out.","外出した夜について話してください。"),("input","me","Me","I went to ___ last night.","実際または言いたい行き先"),("text","other","Tutor","Now tell me about a different evening at home.","今度は別の、家で過ごした夜について話してください。"),("input","me","Me","I stayed home and ___.","家でしたこと"),("text","me","Me","What did you do last night?","あなたは昨夜、何をしましたか？"),("input","other","Tutor","Tutor's answer: one real past evening","先生の本当の昨夜の話")),
33: (("text","other","Tutor","Ask me about one past event.","過去の出来事を一つ私に聞いてください。"),("input","me","Me","Did you ___?","聞きたい出来事"),("input","other","Tutor","Tutor's answer: Yes, I did. / No, I didn't, with one detail.","先生の本当の答えと詳しい情報"),("text","other","Tutor","Think of something you did with friends. Did you and your friends have a good time?","友達としたことを思い出してください。あなたと友達は楽しかったですか？"),("input","me","Me","Yes, we did. It was ___.","自分と友達が実際に楽しんだ出来事の感想")),
34: (("text","other","Tutor","Tell me one thing you didn't do.","しなかったことを一つ教えてください。"),("input","me","Me","I didn't ___.","本当にしなかったこと"),("text","other","Tutor","What was the reason?","理由は何でしたか？"),("input","me","Me","I had too much ___.","本当の理由"),("text","me","Me","How about you?","あなたはどうですか？"),("input","other","Tutor","Tutor's answer: one thing you didn't do and a true reason","先生がしなかったことと本当の理由")),
35: (("text","other","Tutor","Tell me the first two events in order.","最初の二つの出来事を順番に話してください。"),("input","me","Me","First we ___, and then we ___.","実際の最初の二つ"),("text","other","Tutor","How did the story end?","最後はどうなりましたか？"),("input","me","Me","In the end, we ___.","実際の最後の出来事"),("text","me","Me","What did you do?","あなたは何をしましたか？"),("input","other","Tutor","Tutor's answer: three real events in order","先生の三つの本当の出来事")),
36: (("text","other","Tutor","What were you doing when something happened?","何かが起きたとき、何をしていましたか？"),("input","me","Me","I was ___ing when you ___ed.","進行中の動作と、先生がした短い動作"),("text","other","Tutor","What did he do during another activity?","別の活動中、彼は何をしましたか？"),("input","me","Me","While I was ___ing, he ___.","進行中の動作と、彼がした短い動作"),("text","me","Me","What were you doing?","あなたは何をしていましたか？"),("input","other","Tutor","Tutor's answer: one true interrupted action","先生の本当の出来事")),
}
LIVE_HINTS = {}
for n in NUMBERS:
    learner_inputs = [i for i, event in enumerate(LIVE_SCENES[n]) if event[0:2] == ("input", "me")]
    LIVE_HINTS[n] = {i: OPEN_MENUS[n][part] for part, i in enumerate(learner_inputs)}
LIVE_HINTS[29][4] = ("ケンと会う:meeting Ken", "火曜日:Tuesday")
SUPPORT_LINE_OWNERS = {28: "CORE-28 supporting expression", 29: "CORE-29 supporting expression", 31: "CORE-31 supporting expression", 33: "CORE-33 supporting expression", 34: "CORE-34 supporting expression", 36: "CORE-36 supporting expression"}
FINAL_LINE_OWNERSHIP = {n: {v: (DIALOGUES[n][v][6][0], SUPPORT_LINE_OWNERS.get(n, f"CORE-{n} current pattern")) for v in ("model","wild")} for n in NUMBERS}


@contextlib.contextmanager
def patched_shell():
    names = ("LESSONS","VOCAB","KNOWN_WORDS","TRANSLATE_HINTS","OPEN_MENUS","SPECS","DIALOGUES","LIVE_SCENES","LIVE_HINTS","FINAL_LINE_OWNERSHIP","SUPPORT_LINE_OWNERS","COURSE","PILOT")
    old = {name: getattr(shell, name) for name in names}
    values = {"LESSONS":LESSONS,"VOCAB":VOCAB,"KNOWN_WORDS":KNOWN_WORDS,"TRANSLATE_HINTS":TRANSLATE_HINTS,"OPEN_MENUS":OPEN_MENUS,"SPECS":SPECS,"DIALOGUES":DIALOGUES,"LIVE_SCENES":LIVE_SCENES,"LIVE_HINTS":LIVE_HINTS,"FINAL_LINE_OWNERSHIP":FINAL_LINE_OWNERSHIP,"SUPPORT_LINE_OWNERS":SUPPORT_LINE_OWNERS,"COURSE":COURSE,"PILOT":PILOT}
    for name, value in values.items(): setattr(shell, name, value)
    try: yield
    finally:
        for name, value in old.items(): setattr(shell, name, value)


def build(number, data):
    with patched_shell():
        out, text = shell.build(number, data)
    text = re.sub(r'\s*<meta name="podo:proofread-status" content="[^"]+">', '', text)
    text = text.replace(
        '<meta name="podo:vocabulary-status" content="reviewed">',
        '<meta name="podo:vocabulary-status" content="reviewed">\n  <meta name="podo:proofread-status" content="complete">',
        1,
    )
    text = text.replace('content="2026-08-20"', 'content="2026-08-21"', 1)
    return out, text


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh", action="store_true"); args = ap.parse_args()
    if set(LESSONS) != set(NUMBERS): raise SystemExit("explicit lesson set mismatch")
    if not PRESERVED.exists(): raise SystemExit(f"missing preserved CORE-32: {PRESERVED.relative_to(ROOT)}")
    for number in NUMBERS:
        out, text = build(number, LESSONS[number])
        if out.exists() and not args.refresh: raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text, encoding="utf-8"); print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(NUMBERS)} Core decks generated; CORE-32 preserved")
    return 0


if __name__ == "__main__": raise SystemExit(main())
