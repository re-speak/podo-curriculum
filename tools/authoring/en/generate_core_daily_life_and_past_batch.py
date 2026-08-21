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
        p1=rows(("{t}I'm{/t} {t}working{/t} from home today.", "今日は{t}在宅勤務を{/t}{t}しています{/t}。", "I'm working from home|today."), ("{t}I'm{/t} {t}studying{/t} at home today.", "今日は{t}家で勉強を{/t}{t}しています{/t}。", "I'm studying at home|today."), ("{t}I'm{/t} {t}taking it easy{/t} today.", "今日は{t}のんびり{/t}{t}しています{/t}。", "I'm taking it easy|today."), ("{t}I'm{/t} {t}cleaning{/t} the house today.", "今日は{t}家を掃除{/t}{t}しています{/t}。", "I'm cleaning the house|today.")),
        p2=rows(("{t}What are you{/t} {t}doing{/t}?", "{t}何を{/t}{t}していますか{/t}？", "What are you doing?"), ("{t}What are you{/t} {t}reading{/t}?", "{t}何を{/t}{t}読んでいますか{/t}？", "What are you reading?"), ("{t}What are you{/t} {t}making{/t}?", "{t}何を{/t}{t}作っていますか{/t}？", "What are you making?"), ("{t}What are you{/t} {t}watching{/t}?", "{t}何を{/t}{t}見ていますか{/t}？", "What are you watching?")), omit_reorder=(1, 2),
        rules=(("Use am plus -ing for something happening now.", "今していることには am と -ing を使います。"), ("Put are before you in the question, then use the -ing action.", "質問では are を you の前に置き、動作を -ing 形にします。")), prompt=("When do you focus best—at home or somewhere else? Why?", "家とそれ以外では、どこにいるときが一番集中できますか？理由も教えてください。")),
    26: dict(slug="i-usually-drive-but-today-im-walking", title="I usually drive, but today I'm walking", ko="보통 운전하지만 오늘은 걸어요", ja="普段は車ですが、今日は歩いています",
        goal=("Contrast your usual routine with what's different today.", "普段の習慣と今日だけ違うことを比べましょう。"),
        p1=rows(("I {t}usually drive{/t} to work.", "{t}普段は車で{/t}通勤します。", "I|usually drive|to work."), ("I {t}usually walk{/t} to work.", "{t}普段は歩いて{/t}通勤します。", "I|usually walk|to work."), ("I {t}usually take the train{/t} to work.", "{t}普段は電車で{/t}通勤します。", "I|usually take the train|to work."), ("I {t}usually work{/t} at home.", "{t}普段は家で働きます{/t}。", "I|usually work|at home.")),
        p2=rows(("{t}But today I'm{/t} {t}walking{/t}.", "{t}でも今日は{/t}{t}歩いています{/t}。", "But today I'm walking."), ("{t}But today I'm{/t} {t}driving{/t}.", "{t}でも今日は{/t}{t}車で行っています{/t}。", "But today I'm driving."), ("{t}But today I'm{/t} {t}biking{/t}.", "{t}でも今日は{/t}{t}自転車で行っています{/t}。", "But today I'm biking."), ("{t}But today I'm{/t} {t}working{/t}.", "{t}でも今日は{/t}{t}働いています{/t}。", "But today I'm working.")), omit_reorder=(2,), omit_choice=(1,),
        rules=(("Put usually before the plain action for a routine.", "習慣には usually を動作の原形の前に置きます。"), ("Use but today plus be and -ing for today's exception.", "今日だけ違うことには but today と be＋-ing を使います。")), prompt=("What is one part of your daily routine you would like to change? Why?", "毎日の習慣で変えたいことは何ですか？理由も教えてください。")),
    27: dict(slug="i-like-cooking", title="I like cooking", ko="요리하는 걸 좋아해요", ja="料理が好きです",
        goal=("Talk about activities you like and dislike.", "好きな活動と苦手な活動について話しましょう。"),
        p1=rows(("{t}I like{/t} {t}cooking{/t}.", "{t}料理すること{/t}が{t}好きです{/t}。", "I like|cooking."), ("{t}I like{/t} {t}walking{/t}.", "{t}歩くこと{/t}が{t}好きです{/t}。", "I like|walking."), ("{t}I like{/t} {t}reading{/t}.", "{t}読書{/t}が{t}好きです{/t}。", "I like|reading."), ("{t}I like{/t} {t}traveling{/t}.", "{t}旅行すること{/t}が{t}好きです{/t}。", "I like|traveling.")), omit_reorder=(1,),
        p2=rows(("{t}I love{/t} walking, {t}but I hate{/t} running.", "歩くのは{t}大好き{/t}ですが、走るのは{t}大嫌い{/t}です。", "I love walking,|but|I hate running."), ("{t}I love{/t} cooking, {t}but I hate{/t} cleaning.", "料理は{t}大好き{/t}ですが、掃除は{t}大嫌い{/t}です。", "I love cooking,|but|I hate cleaning."), ("{t}I love{/t} reading, {t}but I hate{/t} writing.", "読書は{t}大好き{/t}ですが、書くのは{t}大嫌い{/t}です。", "I love reading,|but|I hate writing."), ("{t}I love{/t} traveling, {t}but I hate{/t} flying.", "旅行は{t}大好き{/t}ですが、飛行機は{t}大嫌い{/t}です。", "I love traveling,|but|I hate flying.")),
        rules=(("After like, use the activity in its -ing form.", "like のあとには活動を -ing 形で続けます。"), ("Use love and hate to show stronger opposite feelings.", "love と hate で、より強い反対の気持ちを表します。")), prompt=("What hobby would you love to get better at? Why?", "もっと上達したい趣味は何ですか？理由も教えてください。")),
    28: dict(slug="are-you-free-on-friday", title="Are you free on Friday?", ko="금요일에 시간 있어요?", ja="金曜日は空いていますか？",
        goal=("Check availability and invite someone to do something.", "相手の都合を確認して、何かに誘いましょう。"),
        p1=rows(("{t}Are you free on{/t} Friday?", "{t}金曜日は空いていますか{/t}？", "Are you free|on Friday?"), ("{t}Are you free on{/t} Saturday?", "{t}土曜日は空いていますか{/t}？", "Are you free|on Saturday?"), ("{t}Are you free on{/t} Sunday?", "{t}日曜日は空いていますか{/t}？", "Are you free|on Sunday?"), ("{t}Are you free on{/t} Tuesday?", "{t}火曜日は空いていますか{/t}？", "Are you free|on Tuesday?")),
        p2=rows(("{t}Would you like to{/t} have dinner?", "{t}夕食を食べませんか{/t}？", "Would you like to|have dinner?"), ("{t}Would you like to{/t} have lunch?", "{t}ランチを食べませんか{/t}？", "Would you like to|have lunch?"), ("{t}Would you like to{/t} see a movie?", "{t}映画を見ませんか{/t}？", "Would you like to|see a movie?"), ("{t}Would you like to{/t} go for a walk?", "{t}散歩に行きませんか{/t}？", "Would you like to|go for a walk?")), omit_reorder=(1, 2), omit_choice=(1, 2),
        rules=(("Use on directly before a day of the week.", "曜日の直前には on を使います。"), ("Keep Would you like to together, then add the activity.", "Would you like to をひとまとまりにして、活動を続けます。")), prompt=("What is your ideal way to spend a free evening?", "自由な夜を過ごすなら、どんな過ごし方が理想ですか？")),
    29: dict(slug="im-meeting-sam-at-six", title="I'm meeting Sam at six", ko="6시에 샘을 만나요", ja="6時にサムと会います",
        goal=("State an arrangement you've already made.", "すでに決まっている予定を伝えましょう。"),
        p1=rows(("{t}I'm{/t} meeting Sam {t}at{/t} six.", "{t}6時に{/t}サムと{t}会います{/t}。", "I'm meeting Sam at six."), ("{t}I'm{/t} having lunch with Emi {t}at{/t} one.", "{t}1時に{/t}エミと{t}ランチを食べます{/t}。", "I'm having lunch with Emi at one."), ("{t}I'm{/t} seeing Ken {t}at{/t} seven.", "{t}7時に{/t}ケンと{t}会います{/t}。", "I'm seeing Ken at seven."), ("{t}I'm{/t} calling Yuki {t}at{/t} eight.", "{t}8時に{/t}ユキに{t}電話します{/t}。", "I'm calling Yuki at eight.")),
        p2=rows(("{t}Are you still{/t} coming on Tuesday?", "{t}火曜日は予定どおり{/t}来ますか？", "Are you still coming on Tuesday?"), ("{t}Are you still{/t} meeting us on Friday?", "{t}金曜日は予定どおり{/t}私たちに会いますか？", "Are you still meeting us on Friday?"), ("{t}Are you still{/t} working on Saturday?", "{t}土曜日は予定どおり{/t}仕事ですか？", "Are you still working on Saturday?"), ("{t}Are you still{/t} leaving on Sunday?", "{t}日曜日は予定どおり{/t}出発しますか？", "Are you still leaving on Sunday?")), omit_reorder=(1, 2),
        rules=(("Use be plus -ing for a plan already fixed in your diary.", "手帳に入っている決定済みの予定には be＋-ing を使います。"), ("Put still before the arranged -ing action to confirm it hasn't changed.", "予定が変わっていないか確かめるときは still を -ing の動作の前に置きます。")), prompt=("What would you most like to do this week? Why?", "今週いちばんしたいことは何ですか？理由も教えてください。")),
    30: dict(slug="i-was-really-tired-yesterday", title="I was really tired yesterday", ko="어제 정말 피곤했어요", ja="昨日は本当に疲れていました",
        goal=("Say how you or a place were in the past.", "過去の自分や場所の様子を言いましょう。"),
        p1=rows(("I {t}was{/t} really tired yesterday.", "昨日は本当に{t}疲れていました{/t}。", "I was|really tired|yesterday."), ("I {t}was{/t} very busy yesterday.", "昨日はとても{t}忙しかったです{/t}。", "I was|very busy|yesterday."), ("We {t}were{/t} at home yesterday.", "私たちは昨日{t}家にいました{/t}。", "We were|at home|yesterday."), ("They {t}were{/t} happy yesterday.", "彼らは昨日{t}うれしそうでした{/t}。", "They were|happy|yesterday.")),
        p2=rows(("There {t}were{/t} a lot of people.", "{t}人がたくさんいました{/t}。", "There were|a lot of people."), ("There {t}was{/t} a lot of traffic.", "{t}交通量が多かったです{/t}。", "There was|a lot of traffic."), ("There {t}were{/t} a lot of meetings.", "{t}会議がたくさんありました{/t}。", "There were|a lot of meetings."), ("There {t}was{/t} a big shop.", "{t}大きな店がありました{/t}。", "There was|a big shop.")), omit_reorder=(2,),
        rules=(("Use was with I, he, she, and it; use were with we and they.", "過去の状態では I・he・she・it に was、we・they に were を使います。"), ("Use There was for one thing and There were for plural things.", "一つのものには There was、複数のものには There were を使います。")), prompt=("What made yesterday a good or difficult day for you?", "昨日を良い一日、または大変な一日にしたのは何でしたか？")),
    31: dict(slug="i-went-out-last-night", title="I went out last night", ko="어젯밤에 나갔어요", ja="昨夜は出かけました",
        goal=("Say whether you went out or stayed in, with one detail.", "外出したか家にいたかを、詳しい情報と一緒に話しましょう。"),
        p1=rows(("I {t}went to{/t} a concert last night.", "昨夜はコンサートに{t}行きました{/t}。", "I went to|a concert|last night."), ("I {t}went to{/t} a restaurant last night.", "昨夜はレストランに{t}行きました{/t}。", "I went to|a restaurant|last night."), ("I {t}went to{/t} the gym last night.", "昨夜はジムに{t}行きました{/t}。", "I went to|the gym|last night."), ("I {t}went to{/t} a friend's house last night.", "昨夜は友人の家に{t}行きました{/t}。", "I went to|a friend's house|last night.")),
        p2=rows(("I {t}stayed home and{/t} watched a movie.", "{t}家にいて{/t}映画を見ました。", "I stayed home|and|watched a movie."), ("I {t}stayed home and{/t} cooked dinner.", "{t}家にいて{/t}夕食を作りました。", "I stayed home|and|cooked dinner."), ("I {t}stayed home and{/t} read a book.", "{t}家にいて{/t}本を読みました。", "I stayed home|and|read a book."), ("I {t}stayed home and{/t} cleaned the house.", "{t}家にいて{/t}家を掃除しました。", "I stayed home|and|cleaned the house.")), omit_choice=(1, 2),
        rules=(("Use went to plus a place for a finished trip out.", "終わった外出には went to と場所を使います。"), ("Use stayed home and a past action for an evening in.", "家で過ごした夜には stayed home and のあとに過去の動作を続けます。")), prompt=("Which do you prefer: a night out or a quiet night at home? Why?", "外出する夜と家で静かに過ごす夜では、どちらが好きですか？理由も教えてください。")),
    33: dict(slug="did-you-have-a-good-time", title="Did you have a good time?", ko="즐거운 시간 보냈어요?", ja="楽しかったですか？",
        goal=("Ask whether something happened and answer.", "過去の出来事についてたずね、答えましょう。"),
        p1=rows(("{t}Did you{/t} have a good time?", "楽しい時間を{t}過ごしましたか{/t}？", "Did you|have a good time?"), ("{t}Did you{/t} see the movie?", "その映画を{t}見ましたか{/t}？", "Did you|see the movie?"), ("{t}Did you{/t} go to the concert?", "コンサートに{t}行きましたか{/t}？", "Did you|go to the concert?"), ("{t}Did you{/t} meet Sam?", "サムに{t}会いましたか{/t}？", "Did you|meet Sam?")),
        p2=rows(("{t}Yes, we did.{/t} It was great.", "{t}はい、楽しかったです{/t}。最高でした。", "Yes, we did.|It was great."), ("{t}No, we didn't.{/t} We missed it.", "{t}いいえ、行けませんでした{/t}。間に合いませんでした。", "No, we didn't.|We missed it."), ("{t}Yes, we did.{/t} It was interesting.", "{t}はい、楽しかったです{/t}。面白かったです。", "Yes, we did.|It was interesting."), ("{t}No, we didn't.{/t} We stayed home.", "{t}いいえ、行きませんでした{/t}。家にいました。", "No, we didn't.|We stayed home.")), omit_reorder=(1, 2),
        rules=(("Did carries the past, so keep the main verb plain.", "過去は Did が表すので、主な動詞は原形にします。"), ("Use Yes, we did or No, we didn't, then add one past detail.", "Yes, we did または No, we didn't で答え、そのあとに過去の情報を一つ加えます。")), prompt=("What would make an ordinary day more enjoyable for you?", "どんなことがあれば、いつもの一日がもっと楽しくなりますか？")),
    34: dict(slug="i-didnt-sleep-well", title="I didn't sleep well", ko="잠을 잘 못 잤어요", ja="よく眠れませんでした",
        goal=("Give a negative answer about the past and add a reason.", "過去について否定で答え、理由を加えましょう。"),
        p1=rows(("{t}I didn't{/t} sleep well.", "よく{t}眠れませんでした{/t}。", "I didn't|sleep well."), ("{t}I didn't{/t} eat breakfast.", "朝食を{t}食べませんでした{/t}。", "I didn't|eat breakfast."), ("{t}I didn't{/t} go out.", "{t}外出しませんでした{/t}。", "I didn't|go out."), ("{t}I didn't{/t} finish the work.", "仕事を{t}終えませんでした{/t}。", "I didn't|finish the work.")),
        p2=rows(("{t}I had too much{/t} coffee.", "コーヒーを{t}飲みすぎました{/t}。", "I had|too much coffee."), ("{t}I had too much{/t} work.", "仕事が{t}多すぎました{/t}。", "I had|too much work."), ("{t}I had too much{/t} food.", "食べ物が{t}多すぎました{/t}。", "I had|too much food."), ("{t}I had too much{/t} homework.", "宿題が{t}多すぎました{/t}。", "I had|too much homework.")), omit_reorder=(1, 2), omit_choice=(2,),
        rules=(("Didn't carries the past, so use the plain verb after it.", "過去は didn't が表すので、そのあとは動詞の原形を使います。"), ("Use too much before an uncountable amount that caused a problem.", "問題になるほど多い不可算の量には too much を使います。")), prompt=("What usually helps you recover after a bad night's sleep?", "よく眠れなかった翌日は、何をすると回復できますか？")),
    35: dict(slug="first-we-ate-then-we-walked-around", title="First we ate, then we walked around", ko="먼저 먹고, 그다음 걸어 다녔어요", ja="まず食べて、それから歩き回りました",
        goal=("Put three finished events in a clear order.", "終わった三つの出来事を分かりやすい順番で話しましょう。"),
        p1=rows(("{t}First{/t} we ate, {t}and then{/t} we walked around.", "{t}まず{/t}食べて、{t}それから{/t}歩き回りました。", "First we ate,|and then|we walked around."), ("{t}First{/t} we had coffee, {t}and then{/t} we went shopping.", "{t}まず{/t}コーヒーを飲んで、{t}それから{/t}買い物に行きました。", "First we had coffee,|and then|we went shopping."), ("{t}First{/t} we saw the park, {t}and then{/t} we had lunch.", "{t}まず{/t}公園を見て、{t}それから{/t}昼食を食べました。", "First we saw the park,|and then|we had lunch."), ("{t}First{/t} we met Sam, {t}and then{/t} we took a taxi.", "{t}まず{/t}サムに会って、{t}それから{/t}タクシーに乗りました。", "First we met Sam,|and then|we took a taxi.")),
        p2=rows(("{t}In the end{/t}, we took a taxi home.", "{t}最後は{/t}タクシーで帰りました。", "In the end,|we took a taxi home."), ("{t}In the end{/t}, we walked home.", "{t}最後は{/t}歩いて帰りました。", "In the end,|we walked home."), ("{t}In the end{/t}, we had dinner.", "{t}最後は{/t}夕食を食べました。", "In the end,|we had dinner."), ("{t}In the end{/t}, we went home.", "{t}最後は{/t}家に帰りました。", "In the end,|we went home.")), omit_reorder=(2,), omit_choice=(1, 2),
        rules=(("Put First at the start, then and then before the second event.", "First を文頭に置き、二つ目の出来事の前に and then を置きます。"), ("Put In the end at the start of the final event.", "最後の出来事の文頭には In the end を置きます。")), prompt=("When a day does not go as planned, what do you usually do next?", "一日が予定どおりに進まないとき、普段は次に何をしますか？")),
    36: dict(slug="i-was-cooking-when-you-called", title="I was cooking when you called", ko="전화했을 때 요리 중이었어요", ja="電話をくれたとき、料理中でした",
        goal=("Say what was in progress when something else happened.", "別の出来事が起きたとき、何をしていたか言いましょう。"),
        p1=rows(("I {t}was cooking when{/t} you called.", "{t}あなたが電話したとき、私は料理をしていました{/t}。", "I was cooking|when|you called."), ("I {t}was walking when{/t} you arrived.", "{t}あなたが着いたとき、私は歩いていました{/t}。", "I was walking|when|you arrived."), ("I {t}was working when{/t} you texted.", "{t}あなたがメッセージを送ったとき、私は働いていました{/t}。", "I was working|when|you texted."), ("I {t}was sleeping when{/t} you knocked.", "{t}あなたがノックしたとき、私は寝ていました{/t}。", "I was sleeping|when|you knocked.")),
        p2=rows(("{t}While I was cooking{/t}, he set the table.", "{t}私が料理をしている間{/t}、彼は食卓を整えました。", "While I was cooking,|he set the table."), ("{t}While I was working{/t}, he made coffee.", "{t}私が仕事をしている間{/t}、彼はコーヒーを入れました。", "While I was working,|he made coffee."), ("{t}While I was cleaning{/t}, he cooked dinner.", "{t}私が掃除をしている間{/t}、彼は夕食を作りました。", "While I was cleaning,|he cooked dinner."), ("{t}While I was shopping{/t}, he called me.", "{t}私が買い物をしている間{/t}、彼は電話をくれました。", "While I was shopping,|he called me.")), omit_reorder=(2,),
        rules=(("Use was plus -ing for the longer action; put the interrupting past action after when.", "長く続いていた動作には was＋-ing、途中で起きた過去の動作には when を使います。"), ("Start with While plus the action in progress, then name the shorter finished action.", "While のあとに進行中の動作を置き、そのあとに短く終わった動作を言います。")), prompt=("What kind of interruption would bother you most? Why?", "どんな邪魔がいちばん気になりますか？理由も教えてください。")),
}


VOCAB = {
25: dict(new="right now|今すぐ; at the moment|今; work from home|在宅勤務をする; take it easy|のんびりする", recycled="", assumed="today|今日; work|働く; do|する; study|勉強する; clean|掃除する; make|作る; read|読む; watch|見る; home|家; house|家", receptive="What are you doing?|何をしていますか？"),
26: dict(new="usually|普段; walk|歩く; bike|自転車で行く; take the train|電車で行く", recycled="drive|運転する|CORE-14", assumed="today|今日; work|働く; at home|家で; home|家; train|電車; office|オフィス", receptive="every day|毎日; not today|今日は違う"),
27: dict(new="like|好き; love|大好き; hate|大嫌い; cooking|料理すること; walking|歩くこと; running|走ること; traveling|旅行すること", recycled="walk|歩く|CORE-26", assumed="cook|料理する; travel|旅行する; read|読む; reading|読書; cleaning|掃除; writing|書くこと; flying|飛行機に乗ること", receptive="What do you like doing?|何をするのが好きですか？; not really my thing|あまり好みではない"),
28: dict(new="free|空いている; Friday|金曜日; Saturday|土曜日; Sunday|日曜日; Tuesday|火曜日; Would you like to ...?|…しませんか？; Yes, I'd love to.|ぜひ。; Sorry, I can't.|すみません、無理です。", recycled="", assumed="dinner|夕食; lunch|昼食; movie|映画; walk|散歩; see|見る; go|行く; day|曜日", receptive="How about ...?|…はどうですか？"),
29: dict(new="meet|会う; still|まだ・予定どおり; See you then.|では、そのときに。", recycled="Tuesday|火曜日|CORE-28; Friday|金曜日|CORE-28; Saturday|土曜日|CORE-28; Sunday|日曜日|CORE-28", assumed="meeting Ken|ケンと会う; have lunch|昼食をとる; lunch|昼食; see|会う; call|電話する; come|来る; work|働く; leave|出発する; us|私たち; Sam|サム; Emi|エミ; Ken|ケン; Yuki|ユキ; one|1時; six|6時; seven|7時; eight|8時", receptive="What time?|何時ですか？; arrangement|決まった予定"),
30: dict(new="was|be の過去形; were|be の過去形; yesterday|昨日; tired|疲れた; busy|忙しい; a lot of|たくさんの; meeting|会議; traffic|交通量", recycled="shop|店|CORE-10", assumed="really|本当に; very|とても; at home|家で; home|家; happy|うれしい; people|人々; big|大きな", receptive="to be honest|正直に言うと; for some reason|なぜか"),
31: dict(new="went|go の過去形; stayed|stay の過去形; watched|watch の過去形; cooked|cook の過去形; cleaned|clean の過去形; concert|コンサート; last night|昨夜", recycled="restaurant|レストラン|CORE-10", assumed="movie|映画; dinner|夕食; read|読む; gym|ジム; book|本; friend|友人; friend's house|友人の家; house|家; home|家; It was fun.|楽しかったです。; Nothing special.|特に何も。", receptive=""),
33: dict(new="did|do の過去形; didn't|did not の短縮形; good time|楽しい時間; great|最高の; interesting|面白い; missed it|間に合わなかった; Not bad.|悪くない", recycled="was|be の過去形|CORE-30; went|go の過去形|CORE-31; stayed|stay の過去形|CORE-31; had|have の過去形|CORE-32; saw|see の過去形|CORE-32; concert|コンサート|CORE-31; meet|会う|CORE-29", assumed="stayed home|家にいた; have|過ごす; see|見る; go|行く; movie|映画; Sam|サム; fun|楽しい; nice|よい; home|家", receptive="How was it?|どうでしたか？"),
34: dict(new="didn't|～しなかった; sleep well|よく眠る; go out|外出する; too much|多すぎる; unfortunately|残念ながら; That's why.|だからです。", recycled="had|have の過去形|CORE-32; coffee|コーヒー|CORE-9", assumed="eat|食べる; finish|終える; breakfast|朝食; work|仕事; food|食べ物; homework|宿題", receptive="What happened?|どうしたのですか？"),
35: dict(new="ate|eat の過去形; met|meet の過去形; first|まず; and then|それから; in the end|最後には; walked around|歩き回った; finally|最後に", recycled="had|have の過去形|CORE-32; went|go の過去形|CORE-31; saw|see の過去形|CORE-32; took|take の過去形|CORE-32", assumed="walked home|歩いて帰った; taxi|タクシー; dinner|夕食; lunch|昼食; shopping|買い物; home|家; park|公園; Sam|サム; coffee|コーヒー", receptive="after that|そのあと"),
36: dict(new="when|…したとき; while|…している間; called|電話した; arrived|到着した; texted|メッセージを送った; knocked|ノックした; set the table|食卓を整えた; all of a sudden|突然", recycled="was|be の過去形|CORE-30; cooking|料理すること|CORE-27; walking|歩くこと|CORE-27; cleaned|clean の過去形|CORE-31; cooked|cook の過去形|CORE-31; coffee|コーヒー|CORE-9", assumed="working|働いている; sleeping|寝ている; cleaning|掃除中; shopping|買い物; dinner|夕食; table|テーブル; made|作った; happened|起きた; at that moment|そのとき", receptive=""),
}

PRODUCTIVE_VOCABULARY = {
25: {"work from home", "take it easy", "study", "clean", "do", "make", "read", "watch", "today", "home", "house"},
26: {"usually", "drive", "walk", "bike", "take the train", "work", "today", "at home"},
27: {"like", "love", "hate", "cooking", "walking", "running", "reading", "traveling", "cleaning", "writing", "flying"},
28: {"free", "friday", "saturday", "sunday", "tuesday", "dinner", "lunch", "movie", "walk", "see", "go"},
29: {"meet", "still", "meeting ken", "have lunch", "see", "call", "come", "work", "leave", "sam", "emi", "ken", "yuki", "one", "six", "seven", "eight"},
30: {"was", "were", "yesterday", "tired", "busy", "very", "a lot of", "meeting", "shop", "people", "traffic", "big", "happy", "at home"},
31: {"went", "stayed", "watched", "cooked", "cleaned", "concert", "restaurant", "movie", "dinner", "read", "gym", "book", "friend's house", "house", "home", "it was fun.", "nothing special."},
33: {"did", "didn't", "good time", "great", "interesting", "missed it", "not bad.", "was", "went", "stayed", "stayed home", "had", "saw", "concert", "meet", "have", "see", "go", "movie", "sam", "fun", "nice", "home"},
34: {"didn't", "sleep well", "go out", "too much", "had", "coffee", "eat", "finish", "breakfast", "work", "food", "homework"},
35: {"ate", "met", "first", "and then", "in the end", "walked around", "walked home", "had", "went", "saw", "took", "taxi", "dinner", "lunch", "shopping", "home", "park", "sam", "coffee"},
36: {"when", "while", "called", "arrived", "texted", "knocked", "set the table", "all of a sudden", "at that moment", "was", "cooking", "walking", "cleaned", "cooked", "coffee", "working", "sleeping", "shopping", "dinner", "happened"},
}

KNOWN_WORDS = {
25: (("ホーム", "home"), ("ワーク", "work"), ("ハウス", "house")), 26: (("トレイン", "train"), ("バイク", "bike"), ("ホーム", "home")), 27: (("クッキング", "cooking"), ("ランニング", "running"), ("トラベリング", "traveling")), 28: (("ディナー", "dinner"), ("ランチ", "lunch"), ("ムービー", "movie")), 29: (("サム", "Sam"), ("エミ", "Emi"), ("ケン", "Ken")), 30: (("ミーティング", "meeting"), ("ショップ", "shop"), ("ホーム", "home")), 31: (("コンサート", "concert"), ("レストラン", "restaurant"), ("ジム", "gym")), 33: (("コンサート", "concert"), ("ムービー", "movie"), ("サム", "Sam")), 34: (("コーヒー", "coffee"), ("ブレックファスト", "breakfast"), ("ワーク", "work")), 35: (("タクシー", "taxi"), ("ショッピング", "shopping"), ("コーヒー", "coffee")), 36: (("テーブル", "table"), ("ディナー", "dinner"), ("コーヒー", "coffee")),
}


CHOICE_CUES = {
    (25, 1): ("今日は{t}在宅勤務をしています{/t}。", "今日は{t}家で勉強しています{/t}。", "今日は{t}のんびりしています{/t}。", "今日は{t}家を掃除しています{/t}。"),
    (25, 2): ("何を{t}していますか{/t}？", "何を{t}読んでいますか{/t}？", "何を{t}作っていますか{/t}？", "何を{t}見ていますか{/t}？"),
    (26, 1): ("{t}普段は{/t}車で通勤します。", "{t}普段は{/t}歩いて通勤します。", "{t}普段は{/t}電車で通勤します。", "{t}普段は{/t}家で働きます。"),
    (26, 2): ("でも今日は{t}歩いています{/t}。", "でも今日は{t}車で行っています{/t}。", "でも今日は{t}自転車で行っています{/t}。", "でも今日は{t}働いています{/t}。"),
    (27, 1): ("{t}料理すること{/t}が好きです。", "{t}歩くこと{/t}が好きです。", "{t}読書{/t}が好きです。", "{t}旅行すること{/t}が好きです。"),
    (27, 2): ("{t}歩くのは大好き{/t}ですが、走るのは大嫌いです。", "{t}料理は大好き{/t}ですが、掃除は大嫌いです。", "{t}読書は大好き{/t}ですが、書くのは大嫌いです。", "{t}旅行は大好き{/t}ですが、飛行機は大嫌いです。"),
    (29, 1): ("6時にサムと{t}会います{/t}。", "1時にエミと{t}ランチを食べます{/t}。", "7時にケンと{t}会います{/t}。", "8時にユキに{t}電話します{/t}。"),
    (33, 2): ("{t}はい{/t}、楽しかったです。最高でした。", "{t}いいえ{/t}、行けませんでした。間に合いませんでした。", "{t}はい{/t}、楽しかったです。面白かったです。", "{t}いいえ{/t}、行きませんでした。家にいました。"),
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
      26: (("usually drive", "usually walk", "usually take the train", "usually work"), ("walking", "driving", "biking", "working")),
      27: (("cooking", "walking", "reading", "traveling"), ("love walking", "love cooking", "love reading", "love traveling")),
      28: (("Friday", "Saturday", "Sunday", "Tuesday"), ("have", "have", "see", "go")),
      29: (("meeting", "having", "seeing", "calling"), ("coming", "meeting", "working", "leaving")),
      30: (("was", "was", "were", "were"), ("were", "was", "were", "was")),
      31: (("went",)*4, ("stayed",)*4),
      33: (("have", "see", "go", "meet"), ("did", "didn't", "did", "didn't")),
      34: (("sleep", "eat", "go", "finish"), ("too much",)*4),
      35: (("First",)*4, ("In the end",)*4),
      36: (("was cooking", "was walking", "was working", "was sleeping"), ("was cooking", "was working", "was cleaning", "was shopping")),
    }[n]
    wrong = {
      25: (("work", "study", "take", "clean"), ("do", "read", "make", "watch")),
      26: (("drive usually", "walk usually", "take usually the train", "work usually"), ("walk", "drive", "bike", "work")),
      27: (("cook", "walk", "read", "travel"), ("like walking", "like cooking", "like reading", "like traveling")),
      28: (("Friday's", "Saturday's", "Sunday's", "Tuesday's"), ("having", "having", "seeing", "going")),
      29: (("meet", "have", "see", "call"), ("come", "meet", "work", "leave")),
      30: (("were", "were", "was", "was"), ("was", "were", "was", "were")),
      31: (("go",)*4, ("stay",)*4),
      33: (("had", "saw", "went", "met"), ("didn't", "did", "didn't", "did")),
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


WRITE_PROMPTS = {
25: (("Now use “I'm ___ing today” to say what you are doing today.", "では、「I'm ___ing today」を使って、今日していることを言ってください。"), ("Now use “What are you ___ing?” to ask me about one activity.", "では、「What are you ___ing?」を使って、私がしていることを一つたずねてください。")),
26: (("Now use “I usually ___” to describe one real routine.", "では、「I usually ___」を使って、本当の習慣を一つ話してください。"), ("Now use “But today I'm ___ing” to say what is different today.", "では、「But today I'm ___ing」を使って、今日だけ違うことを言ってください。")),
27: (("Now use “I like ___ing” to name one activity you genuinely enjoy.", "では、「I like ___ing」を使って、本当に好きな活動を一つ言ってください。"), ("Now use “I love ___ing, but I hate ___ing” to contrast two real preferences.", "では、「I love ___ing, but I hate ___ing」を使って、本当の好みを二つ対比してください。")),
28: (("Now use “Are you free on ___?” to check my availability on a real day.", "では、「Are you free on ___?」を使って、実際の曜日に私が空いているかたずねてください。"), ("Now use “Would you like to ___?” to invite me to do something specific.", "では、「Would you like to ___?」を使って、私を具体的な活動に誘ってください。")),
29: (("Now use “I'm ___ing ___ at ___” to tell me one fixed plan.", "では、「I'm ___ing ___ at ___」を使って、決まっている予定を一つ教えてください。"), ("Now use “Are you still ___ing on ___?” to confirm one of my plans.", "では、「Are you still ___ing on ___?」を使って、私の予定を一つ確認してください。")),
30: (("Now use “I was ___ yesterday” to describe your real state yesterday.", "では、「I was ___ yesterday」を使って、昨日の本当の様子を話してください。"), ("Now use “There was / were ___” to say what was around you.", "では、「There was / were ___」を使って、周りに何があったか言ってください。")),
31: (("Now use “I went to ___ last night” to name one place you went.", "では、「I went to ___ last night」を使って、行った場所を一つ言ってください。"), ("Now use “I stayed home and ___” to say what you did on a different evening.", "では、「I stayed home and ___」を使って、別の夜に家でしたことを言ってください。")),
33: (("Now use “Did you ___?” to ask me about one past event.", "では、「Did you ___?」を使って、過去の出来事を一つ私にたずねてください。"), ("Now use “Yes, we did” or “No, we didn't,” then add one true detail.", "では、「Yes, we did」または「No, we didn't」で答え、本当の情報を一つ加えてください。")),
34: (("Now use “I didn't ___” to say one thing you really did not do.", "では、「I didn't ___」を使って、本当にしなかったことを一つ言ってください。"), ("Now use “I had too much ___” to give a real or imagined reason.", "では、「I had too much ___」を使って、本当または想像の理由を一つ言ってください。")),
35: (("Now use “First ___, and then ___” to order the first two events in a real story.", "では、「First ___, and then ___」を使って、本当の話の最初の二つを順番に言ってください。"), ("Now use “In the end, ___” to give the final event.", "では、「In the end, ___」を使って、最後の出来事を言ってください。")),
36: (("Now use “I was ___ing when ___” to describe one interrupted action.", "では、「I was ___ing when ___」を使って、途中で別のことが起きた動作を一つ話してください。"), ("Now use “While I was ___ing, ___” to say what another person did at the same time.", "では、「While I was ___ing, ___」を使って、同じときに別の人がしたことを言ってください。")),
}

FILL_HINTS = {
25: ((("働く", "work"), ("勉強する", "study"), ("のんびりする", "take it easy"), ("掃除する", "clean")), (("する", "do"), ("読む", "read"), ("作る", "make"), ("見る", "watch"))),
26: ((("車で行く", "drive"), ("歩く", "walk"), ("電車で行く", "take the train"), ("働く", "work")), (("歩く", "walk"), ("車で行く", "drive"), ("自転車で行く", "bike"), ("働く", "work"))),
27: ((("料理する", "cook"), ("歩く", "walk"), ("読む", "read"), ("旅行する", "travel")), None),
36: ((("料理中", "cooking"), ("歩いている", "walking"), ("仕事中", "working"), ("寝ている", "sleeping")), (("料理中", "cooking"), ("仕事中", "working"), ("掃除中", "cleaning"), ("買い物中", "shopping"))),
}

for number in NUMBERS:
    SPECS[number]["writes"] = WRITE_PROMPTS[number]
    SPECS[number]["fill_hints"] = FILL_HINTS.get(number, (None, None))


TRANSLATE_HINTS = {
25: (("在宅勤務:work from home", "家:home; 勉強する:study", "のんびりする:take it easy", "家:house; 掃除する:clean"), ("", "読む:read", "作る:make", "見る:watch")),
26: (("車で行く:drive", "歩く:walk", "電車:train", "家で:at home; 働く:work"), ("歩く:walk", "車で行く:drive", "自転車で行く:bike", "働く:work")),
27: (("料理:cooking", "歩くこと:walking", "読書:reading", "旅行:traveling"), ("歩くこと:walking", "料理:cooking", "読書:reading", "旅行:traveling")),
28: (("金曜日:Friday", "土曜日:Saturday", "日曜日:Sunday", "火曜日:Tuesday"), ("夕食:dinner", "昼食:lunch", "映画:movie", "散歩:walk")),
29: (("サム:Sam; 6時:six", "エミ:Emi; 昼食:lunch; 1時:one", "ケン:Ken; 7時:seven", "ユキ:Yuki; 8時:eight"), ("火曜日:Tuesday", "金曜日:Friday", "土曜日:Saturday", "日曜日:Sunday")),
30: (("疲れた:tired", "忙しい:busy", "家で:at home", "うれしい:happy"), ("人々:people", "交通量:traffic", "会議:meeting", "大きな:big; 店:shop")),
31: (("コンサート:concert", "レストラン:restaurant", "ジム:gym", "友人の家:friend's house"), ("映画:movie", "夕食:dinner", "本:book", "家:house")),
33: (("楽しい時間:good time", "映画:movie", "コンサート:concert", "サム:Sam"), ("最高:great", "間に合わなかった:missed it", "面白い:interesting", "家にいた:stayed home")),
34: (("よく眠る:sleep well", "朝食:breakfast", "外出する:go out", "仕事:work"), ("コーヒー:coffee", "仕事:work", "食べ物:food", "宿題:homework")),
35: (("食べた:ate; 歩き回った:walked around", "コーヒー:coffee; 買い物:shopping", "公園:park; 昼食:lunch", "サム:Sam; タクシー:taxi"), ("タクシー:taxi", "家:home", "夕食:dinner", "家:home")),
36: (("料理:cooking; 電話した:called", "歩くこと:walking; 到着した:arrived", "仕事中:working; メッセージを送った:texted", "寝ている:sleeping; ノックした:knocked"), ("料理:cooking; 食卓を整える:set the table", "仕事中:working; コーヒー:coffee", "掃除した:cleaned; 夕食:dinner", "買い物:shopping; 電話した:called")),
}
TRANSLATE_STAGES = {n: ("supported", "supported") for n in NUMBERS}
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

# Free Talk is a genuine topic conversation, not another controlled-pattern
# worksheet. The learner answers one relevant question in their own words and
# naturally asks the tutor back; today's pattern is optional here.
LIVE_SCENES = {
    n: (
        ("text", "other", "Tutor", LESSONS[n]["prompt"][0], LESSONS[n]["prompt"][1]),
        ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
        ("text", "me", "Me", "How about you?", "先生はどうですか？"),
        ("input", "other", "Tutor", "Tutor's answer", "先生の本当の答え"),
    )
    for n in NUMBERS
}
LIVE_HINTS = {n: {} for n in NUMBERS}
SUPPORT_LINE_OWNERS = {28: "CORE-28 supporting expression", 29: "CORE-29 supporting expression", 31: "CORE-31 supporting expression", 33: "CORE-33 supporting expression", 34: "CORE-34 supporting expression", 36: "CORE-36 supporting expression"}
FINAL_LINE_OWNERSHIP = {n: {v: (DIALOGUES[n][v][6][0], SUPPORT_LINE_OWNERS.get(n, f"CORE-{n} current pattern")) for v in ("model","wild")} for n in NUMBERS}


@contextlib.contextmanager
def patched_shell():
    names = ("LESSONS","VOCAB","KNOWN_WORDS","TRANSLATE_HINTS","TRANSLATE_STAGES","OPEN_MENUS","SPECS","DIALOGUES","LIVE_SCENES","LIVE_HINTS","FINAL_LINE_OWNERSHIP","SUPPORT_LINE_OWNERS","COURSE","PILOT")
    old = {name: getattr(shell, name) for name in names}
    values = {"LESSONS":LESSONS,"VOCAB":VOCAB,"KNOWN_WORDS":KNOWN_WORDS,"TRANSLATE_HINTS":TRANSLATE_HINTS,"TRANSLATE_STAGES":TRANSLATE_STAGES,"OPEN_MENUS":OPEN_MENUS,"SPECS":SPECS,"DIALOGUES":DIALOGUES,"LIVE_SCENES":LIVE_SCENES,"LIVE_HINTS":LIVE_HINTS,"FINAL_LINE_OWNERSHIP":FINAL_LINE_OWNERSHIP,"SUPPORT_LINE_OWNERS":SUPPORT_LINE_OWNERS,"COURSE":COURSE,"PILOT":PILOT}
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
