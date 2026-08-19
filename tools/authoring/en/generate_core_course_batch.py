#!/usr/bin/env python3
"""Generate the approved missing Core 12-24 course lessons from the Core shell."""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_lesson

ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-first-exchanges-2"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
ME = "https://respeak-lemonade.s3.ap-northeast-2.amazonaws.com/test/haruka-avatar.jpg"
OTHER = "https://respeak-lemonade.s3.ap-northeast-2.amazonaws.com/test/hana-avatar.jpg"


def rows(*items):
    return items


LESSONS = {
12: dict(slug="i-start-work-at-nine", title="I start work at nine", ko="아홉 시에 일을 시작해요", ja="9時に仕事を始めます", goal=("Say what you regularly do and when.", "ふだんすることと、その時間を言いましょう。"),
 p1=rows(("{t}I start work at{/t} nine.", "9時に{t}仕事を始めます{/t}。", "I|start work|at|nine."),("{t}I start work at{/t} eight.", "8時に{t}仕事を始めます{/t}。", "I|start work|at|eight."),("{t}I start work at{/t} ten.", "10時に{t}仕事を始めます{/t}。", "I|start work|at|ten."),("{t}I start work at{/t} eleven.", "11時に{t}仕事を始めます{/t}。", "I|start work|at|eleven.")),
 p2=rows(("{t}I usually{/t} finish {t}around{/t} six.", "{t}ふだん{/t}6時{t}ごろ{/t}仕事を終えます。", "I usually|finish|around|six."),("{t}I usually{/t} eat {t}around{/t} seven.", "{t}ふだん{/t}7時{t}ごろ{/t}食べます。", "I usually|eat|around|seven."),("{t}I usually{/t} leave {t}around{/t} eight.", "{t}ふだん{/t}8時{t}ごろ{/t}出ます。", "I usually|leave|around|eight."),("{t}I usually{/t} get home {t}around{/t} nine.", "{t}ふだん{/t}9時{t}ごろ{/t}帰宅します。", "I usually|get home|around|nine.")),
 rule=("Put frequency words before the verb; use at for an exact clock time and around for an approximate time.", "頻度を表す語は動詞の前に置き、正確な時刻には at、だいたいの時刻には around を使います。"), prompt=("What does a normal workday look like for you?", "ふだんの仕事の日はどんな一日ですか？"), partner=("Coworker", "What time do you normally start?", "And when do you usually finish?", "That is a long day."), tip=("every day", "毎日", "most days", "たいていの日")),
13: dict(slug="do-you-drink-coffee", title="Do you drink coffee?", ko="커피를 마셔요?", ja="コーヒーを飲みますか？", goal=("Ask about a habit and give a short answer with one detail.", "習慣についてたずね、短い答えに一つ情報を加えましょう。"),
 p1=rows(("{t}Do you{/t} drink coffee?", "コーヒーを{t}飲みますか{/t}？", "Do you|drink|coffee|?"),("{t}Do you{/t} cook at home?", "家で{t}料理しますか{/t}？", "Do you|cook|at home|?"),("{t}Do you{/t} work on weekends?", "週末に{t}働きますか{/t}？", "Do you|work|on weekends|?"),("{t}Do you{/t} exercise every day?", "毎日{t}運動しますか{/t}？", "Do you|exercise|every day|?")),
 p2=rows(("{t}Yes, I do.{/t} Every morning.", "{t}はい、します。{/t}毎朝です。", "Yes,|I do.|Every|morning."),("{t}Yes, I do.{/t} At home.", "{t}はい、します。{/t}家でです。", "Yes,|I do.|At|home."),("{t}Yes, I do.{/t} Every weekend.", "{t}はい、します。{/t}毎週末です。", "Yes,|I do.|Every|weekend."),("{t}Yes, I do.{/t} Almost every day.", "{t}はい、します。{/t}ほぼ毎日です。", "Yes,|I do.|Almost|every day.")),
 rule=("Put do at the front of the question and keep the main verb plain.", "質問では do を前に置き、後ろの動詞は原形のままにします。"), prompt=("Ask me about one of my everyday habits.", "私の日常の習慣を一つたずねてください。"), partner=("Friend", "Ask me something about my routine.", "Yes, I do. How about you?", "Now we know one thing in common."), tip=("not really", "あまり", "all the time", "いつも")),
14: dict(slug="i-dont-drive-to-work", title="I don't drive to work", ko="차로 출근하지 않아요", ja="車で通勤しません", goal=("Contrast something you do with something you do not do.", "することと、しないことを対比して話しましょう。"),
 p1=rows(("{t}I don't{/t} drive to work.", "車で通勤{t}しません{/t}。", "I don't|drive|to|work."),("{t}I don't{/t} eat breakfast.", "朝ごはんを{t}食べません{/t}。", "I don't|eat|breakfast|."),("{t}I don't{/t} work on Sundays.", "日曜日は{t}働きません{/t}。", "I don't|work|on Sundays|."),("{t}I don't{/t} drink tea.", "お茶は{t}飲みません{/t}。", "I don't|drink|tea|.")),
 p2=rows(("I take the train {t}instead{/t}.", "{t}その代わり{/t}電車に乗ります。", "I|take|the train|instead."),("I have coffee {t}instead{/t}.", "{t}その代わり{/t}コーヒーを飲みます。", "I|have|coffee|instead."),("I work on Saturday {t}instead{/t}.", "{t}その代わり{/t}土曜日に働きます。", "I|work|on Saturday|instead."),("I drink water {t}instead{/t}.", "{t}その代わり{/t}水を飲みます。", "I|drink|water|instead.")),
 rule=("Use don't plus the plain verb; put instead after the alternative.", "don't の後ろは動詞の原形にし、代わりの行動の後ろに instead を置きます。"), prompt=("Tell me one thing you do differently from most people.", "多くの人とは違う習慣を一つ教えてください。"), partner=("Coworker", "Do you drive to work?", "How do you get here, then?", "The train sounds easier."), tip=("not every day", "毎日ではない", "on weekends", "週末に")),
15: dict(slug="she-works-downtown", title="She works downtown", ko="그녀는 시내에서 일해요", ja="彼女は中心街で働いています", goal=("Exchange information about another person.", "別の人について情報をやり取りしましょう。"),
 p1=rows(("{t}She works{/t} downtown.", "彼女は中心街で{t}働いています{/t}。", "She|works|down|town."),("{t}He lives{/t} nearby.", "彼は近くに{t}住んでいます{/t}。", "He|lives|near|by."),("{t}She studies{/t} at night.", "彼女は夜に{t}勉強します{/t}。", "She|studies|at|night."),("{t}He cooks{/t} at home.", "彼は家で{t}料理します{/t}。", "He|cooks|at|home.")),
 p2=rows(("{t}Does she{/t} like it?", "彼女はそこが{t}好きですか{/t}？", "Does|she|like|it?"),("{t}Does he{/t} work there?", "彼はそこで{t}働いていますか{/t}？", "Does|he|work|there?"),("{t}Does she{/t} study English?", "彼女は英語を{t}勉強しますか{/t}？", "Does|she|study|English?"),("{t}Does he{/t} cook often?", "彼はよく{t}料理しますか{/t}？", "Does|he|cook|often?")),
 rule=("Add -s for he or she; in a question, does carries the -s and the main verb is plain.", "he や she では動詞に -s をつけ、質問では does が -s を担うので動詞は原形にします。"), prompt=("Tell me about someone you know, then let me ask about them.", "知っている人について話し、その人について私に質問させてください。"), partner=("Friend", "Where does your sister work?", "Does she like it there?", "It sounds like a good fit."), tip=("I think so.", "そうだと思います", "I don't know.", "分かりません")),
16: dict(slug="what-time-do-you-get-up", title="What time do you get up?", ko="몇 시에 일어나요?", ja="何時に起きますか？", goal=("Ask when and where a routine happens.", "習慣がいつ、どこで行われるかをたずねましょう。"),
 p1=rows(("{t}What time do you{/t} get up?", "{t}何時に{/t}起きますか？", "What time|do you|get|up?"),("{t}What time do you{/t} start work?", "{t}何時に{/t}仕事を始めますか？", "What time|do you|start|work?"),("{t}What time do you{/t} have lunch?", "{t}何時に{/t}昼食をとりますか？", "What time|do you|have|lunch?"),("{t}What time do you{/t} get home?", "{t}何時に{/t}帰宅しますか？", "What time|do you|get|home?")),
 p2=rows(("{t}Where do you usually{/t} have lunch?", "{t}ふだんどこで{/t}昼食をとりますか？", "Where|do you usually|have|lunch?"),("{t}Where do you usually{/t} work?", "{t}ふだんどこで{/t}働きますか？", "Where|do you usually|work|?"),("{t}Where do you usually{/t} exercise?", "{t}ふだんどこで{/t}運動しますか？", "Where|do you usually|exercise|?"),("{t}Where do you usually{/t} study?", "{t}ふだんどこで{/t}勉強しますか？", "Where|do you usually|study|?")),
 rule=("Put the question word first, then use the same do-you question order.", "疑問詞を最初に置き、その後ろは do you の語順にします。"), prompt=("Ask me two questions about my daily routine.", "私の日課について二つ質問してください。"), partner=("Coworker", "What time do you usually get up?", "Where do you have lunch?", "Our schedules are quite different."), tip=("it depends", "場合によります", "most days", "たいていの日")),
17: dict(slug="how-often-do-you-exercise", title="How often do you exercise?", ko="얼마나 자주 운동해요?", ja="どのくらい運動しますか？", goal=("Ask how often something happens and answer approximately.", "頻度をたずね、だいたいの回数で答えましょう。"),
 p1=rows(("{t}How often do you{/t} exercise?", "{t}どのくらいの頻度で{/t}運動しますか？", "How often|do you|exercise|?"),("{t}How often do you{/t} cook?", "{t}どのくらいの頻度で{/t}料理しますか？", "How often|do you|cook|?"),("{t}How often do you{/t} travel?", "{t}どのくらいの頻度で{/t}旅行しますか？", "How often|do you|travel|?"),("{t}How often do you{/t} call home?", "{t}どのくらいの頻度で{/t}家に電話しますか？", "How often|do you|call|home?")),
 p2=rows(("{t}About{/t} twice {t}a week{/t}.", "{t}だいたい{/t}週{t}2回{/t}です。", "About|twice|a|week."),("{t}About{/t} three times {t}a month{/t}.", "{t}だいたい{/t}月{t}3回{/t}です。", "About|three times|a|month."),("{t}About{/t} once {t}a year{/t}.", "{t}だいたい{/t}年{t}1回{/t}です。", "About|once|a|year."),("{t}About{/t} four times {t}a week{/t}.", "{t}だいたい{/t}週{t}4回{/t}です。", "About|four times|a|week.")),
 rule=("Learn twice a week and three times a month as complete frequency chunks.", "twice a week や three times a month は、頻度を表すまとまりとして覚えます。"), prompt=("Ask how often I do something, then compare our answers.", "私に頻度をたずね、二人の答えを比べてください。"), partner=("Friend", "How often do you exercise?", "What about on busy weeks?", "That is still pretty often."), tip=("every day", "毎日", "not very often", "あまり頻繁ではない")),
18: dict(slug="can-you-drive", title="Can you drive?", ko="운전할 수 있어요?", ja="運転できますか？", goal=("Ask about an ability and contrast what you can and cannot do.", "できることをたずね、できることとできないことを対比しましょう。"),
 p1=rows(("{t}Can you{/t} drive?", "運転{t}できますか{/t}？", "Can|you|drive|?"),("{t}Can you{/t} swim?", "泳ぐことが{t}できますか{/t}？", "Can|you|swim|?"),("{t}Can you{/t} cook?", "料理が{t}できますか{/t}？", "Can|you|cook|?"),("{t}Can you{/t} ski?", "スキーが{t}できますか{/t}？", "Can|you|ski|?")),
 p2=rows(("{t}I can{/t} ride a bike, {t}but I can't{/t} drive.", "自転車には{t}乗れますが{/t}、運転は{t}できません{/t}。", "I can|ride a bike,|but I can't|drive."),("{t}I can{/t} walk, {t}but I can't{/t} run.", "歩くことは{t}できますが{/t}、走ることは{t}できません{/t}。", "I can|walk,|but I can't|run."),("{t}I can{/t} cook, {t}but I can't{/t} bake.", "料理は{t}できますが{/t}、お菓子作りは{t}できません{/t}。", "I can|cook,|but I can't|bake."),("{t}I can{/t} read it, {t}but I can't{/t} write it.", "読むことは{t}できますが{/t}、書くことは{t}できません{/t}。", "I can|read it,|but I can't|write it.")),
 rule=("Can carries the grammar, so the next verb stays plain—never add to or -s.", "can が文法を担うので、次の動詞は原形のままにし、to や -s はつけません。"), prompt=("Ask me about one ability, then tell me what you can do.", "私にできることを一つたずね、自分にできることも話してください。"), partner=("Friend", "Can you drive?", "What can you do well, then?", "That is useful too."), tip=("pretty well", "かなり上手に", "not yet", "まだ")),
19: dict(slug="how-much-is-this", title="How much is this?", ko="이거 얼마예요?", ja="これはいくらですか？", goal=("Ask a price and confirm a number you heard.", "値段をたずね、聞いた数字を確認しましょう。"),
 p1=rows(("{t}How much is{/t} this one?", "これは{t}いくらですか{/t}？", "How much|is|this|one?"),("{t}How much is{/t} that bag?", "あのかばんは{t}いくらですか{/t}？", "How much|is|that|bag?"),("{t}How much is{/t} the ticket?", "そのチケットは{t}いくらですか{/t}？", "How much|is|the|ticket?"),("{t}How much is{/t} a coffee?", "コーヒーは{t}いくらですか{/t}？", "How much|is|a|coffee?")),
 p2=rows(("{t}Is that{/t} fifteen {t}or{/t} fifty?", "{t}それは{/t}15{t}ですか、それとも{/t}50ですか？", "Is that|fifteen|or|fifty?"),("{t}Is that{/t} thirteen {t}or{/t} thirty?", "{t}それは{/t}13{t}ですか、それとも{/t}30ですか？", "Is that|thirteen|or|thirty?"),("{t}Is that{/t} fourteen {t}or{/t} forty?", "{t}それは{/t}14{t}ですか、それとも{/t}40ですか？", "Is that|fourteen|or|forty?"),("{t}Is that{/t} sixteen {t}or{/t} sixty?", "{t}それは{/t}16{t}ですか、それとも{/t}60ですか？", "Is that|sixteen|or|sixty?")),
 rule=("Use how much is for the price; use is that X or Y to check a number before acting.", "値段には how much is、数字の確認には is that X or Y を使います。"), prompt=("Ask the price of something near you, then check the number I give.", "近くの物の値段をたずね、私が言う数字を確認してください。"), partner=("Clerk", "Can I help you?", "It is fifty dollars.", "Yes, five-zero."), tip=("That's a bit expensive.", "少し高いですね", "I'll take it.", "これにします")),
21: dict(slug="can-i-try-this-on", title="Can I try this on?", ko="이거 입어 봐도 돼요?", ja="これを試着してもいいですか？", goal=("Ask permission and answer a permission request.", "許可を求め、許可を求められたときにも答えましょう。"),
 p1=rows(("{t}Can I{/t} try this on?", "これを試着{t}してもいいですか{/t}？", "Can|I|try this|on?"),("{t}Can I{/t} sit here?", "ここに座っても{t}いいですか{/t}？", "Can|I|sit|here?"),("{t}Can I{/t} take a photo?", "写真を撮っても{t}いいですか{/t}？", "Can|I|take|a photo?"),("{t}Can I{/t} use this?", "これを使っても{t}いいですか{/t}？", "Can|I|use|this?")),
 p2=rows(("{t}Sure, you can{/t} take a photo.", "もちろん、写真を撮って{t}いいですよ{/t}。", "Sure,|you can|take|a photo."),("{t}Sure, you can{/t} sit here.", "もちろん、ここに座って{t}いいですよ{/t}。", "Sure,|you can|sit|here."),("{t}Sure, you can{/t} use this.", "もちろん、これを使って{t}いいですよ{/t}。", "Sure,|you can|use|this."),("{t}Sure, you can{/t} try it on.", "もちろん、試着して{t}いいですよ{/t}。", "Sure,|you can|try it|on.")),
 rule=("Can I asks permission for me; you can gives permission to the other person.", "Can I は自分の許可を求め、you can は相手に許可を与えます。"), prompt=("Ask permission to do something in this room.", "この部屋で何かをする許可を求めてください。"), partner=("Clerk", "Let me know if you need anything.", "Yes, the fitting room is over there.", "Take your time."), tip=("Go ahead.", "どうぞ", "Sorry, not here.", "すみません、ここではできません")),
22: dict(slug="id-like-the-chicken-please", title="I'd like the chicken, please", ko="치킨으로 주세요", ja="チキンをお願いします", goal=("Order something politely in two common ways.", "よく使う二つの言い方で、丁寧に注文しましょう。"),
 p1=rows(("{t}I'd like{/t} the chicken, {t}please{/t}.", "チキンを{t}お願いします{/t}。", "I'd like|the chicken,|please|."),("{t}I'd like{/t} the soup, {t}please{/t}.", "スープを{t}お願いします{/t}。", "I'd like|the soup,|please|."),("{t}I'd like{/t} this one, {t}please{/t}.", "これを{t}お願いします{/t}。", "I'd like|this one,|please|."),("{t}I'd like{/t} a ticket, {t}please{/t}.", "チケットを1枚{t}お願いします{/t}。", "I'd like|a ticket,|please|.")),
 p2=rows(("{t}Can I have{/t} a coffee, {t}please{/t}?", "コーヒーを{t}いただけますか{/t}？", "Can I have|a coffee,|please|?"),("{t}Can I have{/t} some water, {t}please{/t}?", "お水を{t}いただけますか{/t}？", "Can I have|some water,|please|?"),("{t}Can I have{/t} the menu, {t}please{/t}?", "メニューを{t}いただけますか{/t}？", "Can I have|the menu,|please|?"),("{t}Can I have{/t} a receipt, {t}please{/t}?", "レシートを{t}いただけますか{/t}？", "Can I have|a receipt,|please|?")),
 rule=("Keep I'd like as one ordering frame; after Can I, use the plain verb have.", "I'd like は注文のまとまりとして覚え、Can I の後ろは原形の have にします。"), prompt=("Order one thing, then ask me for one extra item.", "一つ注文し、追加でもう一つ頼んでください。"), partner=("Server", "Are you ready to order?", "Anything to drink?", "Great. I will bring that soon."), tip=("This one, please.", "これをお願いします", "for here or to go?", "店内ですか、持ち帰りですか")),
23: dict(slug="two-cups-of-coffee", title="Two cups of coffee", ko="커피 두 잔", ja="コーヒーを2杯", goal=("Ask for an amount of something that is not counted directly.", "直接数えないものの量をたずねたり、頼んだりしましょう。"),
 p1=rows(("{t}Two cups of{/t} coffee, {t}please{/t}.", "コーヒーを{t}2杯お願いします{/t}。", "Two cups|of coffee,|please|."),("{t}Two bottles of{/t} water, {t}please{/t}.", "水を{t}2本お願いします{/t}。", "Two bottles|of water,|please|."),("{t}Two pieces of{/t} cake, {t}please{/t}.", "ケーキを{t}2切れお願いします{/t}。", "Two pieces|of cake,|please|."),("{t}Two bowls of{/t} rice, {t}please{/t}.", "ご飯を{t}2杯お願いします{/t}。", "Two bowls|of rice,|please|.")),
 p2=rows(("{t}How much{/t} rice {t}do we need{/t}?", "ご飯は{t}どのくらい必要ですか{/t}？", "How much|rice|do we|need?"),("{t}How much{/t} water {t}do we need{/t}?", "水は{t}どのくらい必要ですか{/t}？", "How much|water|do we|need?"),("{t}How much{/t} coffee {t}do we need{/t}?", "コーヒーは{t}どのくらい必要ですか{/t}？", "How much|coffee|do we|need?"),("{t}How much{/t} time {t}do we need{/t}?", "時間は{t}どのくらい必要ですか{/t}？", "How much|time|do we|need?")),
 rule=("Count the container or piece for non-count nouns: a cup of, a bottle of, or a piece of.", "直接数えない名詞は、a cup of、a bottle of、a piece of のように容器や単位を数えます。"), prompt=("Plan drinks for two people and tell me how much we need.", "二人分の飲み物を考え、どのくらい必要か話してください。"), partner=("Clerk", "What can I get you?", "Would you like anything else?", "That will be twelve dollars."), tip=("a little", "少し", "a lot of", "たくさんの")),
24: dict(slug="sorry-can-you-say-that-again", title="Sorry, can you say that again?", ko="죄송하지만 다시 말해 주시겠어요?", ja="すみません、もう一度言ってもらえますか？", goal=("Ask for repetition or slower speech without stopping the conversation.", "会話を止めずに、繰り返しやゆっくり話すことを頼みましょう。"),
 p1=rows(("Sorry, {t}can you say{/t} that {t}again{/t}?", "すみません、それを{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|that|again?"),("Sorry, {t}can you say{/t} your name {t}again{/t}?", "すみません、名前を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|your name|again?"),("Sorry, {t}can you say{/t} the last part {t}again{/t}?", "すみません、最後の部分を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|the last part|again?"),("Sorry, {t}can you say{/t} 'shelf' {t}again{/t}?", "すみません、shelf を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|'shelf'|again?")),
 p2=rows(("{t}Can you speak{/t} more slowly?", "もう少しゆっくり{t}話してもらえますか{/t}？", "Can you|speak|more|slowly?"),("{t}Can you speak{/t} more clearly?", "もう少しはっきり{t}話してもらえますか{/t}？", "Can you|speak|more|clearly?"),("{t}Can you speak{/t} a little louder?", "もう少し大きな声で{t}話してもらえますか{/t}？", "Can you|speak|a little|louder?"),("{t}Can you speak{/t} more slowly, please?", "もう少しゆっくり{t}話してもらえますか{/t}？", "Can you|speak|more slowly,|please?")),
 rule=("Use Can you plus a plain verb; say exactly what you need repeated or changed.", "Can you の後ろは動詞の原形にし、何を繰り返すか、どう変えてほしいかを具体的に言います。"), prompt=("Stop me naturally if you do not understand my next sentence.", "次の文が分からなければ、自然に私を止めてください。"), partner=("Staff", "The next train leaves from platform thirteen.", "Of course: platform one-three.", "Yes, that is right."), tip=("I didn't catch that.", "聞き取れませんでした", "a little louder", "もう少し大きな声で")),
}

PARTNER_JA = {
"What time do you normally start?":"ふだん何時に始めますか？","And when do you usually finish?":"では、ふだん何時に終わりますか？","That is a long day.":"長い一日ですね。",
"Ask me something about my routine.":"私の日課について何か聞いてください。","Yes, I do. How about you?":"はい、します。あなたは？","Now we know one thing in common.":"共通点が一つ分かりましたね。",
"Do you drive to work?":"車で通勤しますか？","How do you get here, then?":"では、どうやってここへ来ますか？","The train sounds easier.":"電車のほうが楽そうですね。",
"Where does your sister work?":"お姉さんはどこで働いていますか？","Does she like it there?":"彼女はそこで働くのが好きですか？","It sounds like a good fit.":"彼女に合っていそうですね。",
"What time do you usually get up?":"ふだん何時に起きますか？","Where do you have lunch?":"どこで昼食をとりますか？","Our schedules are quite different.":"私たちの予定はかなり違いますね。",
"How often do you exercise?":"どのくらい運動しますか？","What about on busy weeks?":"忙しい週はどうですか？","That is still pretty often.":"それでもかなり多いですね。",
"Can you drive?":"運転できますか？","What can you do well, then?":"では、何が上手にできますか？","That is useful too.":"それも役に立ちますね。",
"Can I help you?":"何かお手伝いしましょうか？","It is fifty dollars.":"50ドルです。","Yes, five-zero.":"はい、5、0です。",
"Let me know if you need anything.":"何か必要なら教えてください。","Yes, the fitting room is over there.":"はい、試着室はあちらです。","Take your time.":"ごゆっくりどうぞ。",
"Are you ready to order?":"ご注文はお決まりですか？","Anything to drink?":"お飲み物はいかがですか？","Great. I will bring that soon.":"かしこまりました。すぐお持ちします。",
"What can I get you?":"何になさいますか？","Would you like anything else?":"ほかにもご注文はありますか？","That will be twelve dollars.":"12ドルです。",
"The next train leaves from platform thirteen.":"次の電車は13番ホームから出ます。","Of course: platform one-three.":"もちろんです。ホームは1、3です。","Yes, that is right.":"はい、それで合っています。",
}

# Each roleplay deliberately defines its own conversational bridge.  The model
# and transfer exchanges use different practice rows so "A new situation" is
# real transfer, not the model dialogue with empty fields pasted over it.
# Tuple shape: role, p1 row, p2 row, opening, bridge, closing, learner reply.
DIALOGUES = {
12: dict(
 model=("Coworker",0,0,("What time do you normally start?","ふだん何時に始めますか？"),("And when do you usually finish?","では、ふだん何時に終わりますか？"),("That is a long day.","長い一日ですね。"),("It is, but I am used to it.","そうですね。でも慣れています。")),
 wild=("Coworker",1,1,("What time do you start on Fridays?","金曜日は何時に仕事を始めますか？"),("What about dinner?","夕食はどうですか？"),("That sounds like a full day.","忙しい一日になりそうですね。"),("Yes, Fridays are busy.","はい、金曜日は忙しいです。"))),
13: dict(
 model=("Friend",0,0,("What would you like to know about my routine?","私の日課について何を知りたいですか？"),("Yes, every morning. How about you?","はい、毎朝です。あなたは？"),("Then we have that in common.","では、それが共通点ですね。"),("It looks like we do.","そうみたいですね。")),
 wild=("Friend",1,1,("Ask me about another habit.","ほかの習慣について聞いてください。"),("Yes, most evenings. What about you?","はい、たいていの夜にします。あなたは？"),("Cooking at home is convenient.","家で料理するのは便利ですね。"),("I think so too.","私もそう思います。"))),
14: dict(
 model=("Coworker",0,0,("Do you drive to work?","車で通勤しますか？"),("How do you get here, then?","では、どうやってここへ来ますか？"),("The train sounds easier.","電車のほうが楽そうですね。"),("It usually is.","たいていはそうです。")),
 wild=("Friend",1,1,("Do you usually eat breakfast?","ふだん朝ごはんを食べますか？"),("What do you have in the morning, then?","では、朝は何を飲みますか？"),("Coffee is quick, at least.","少なくともコーヒーなら手軽ですね。"),("Exactly.","その通りです。"))),
15: dict(
 model=("Friend",0,0,("Tell me about your sister's job.","お姉さんの仕事について教えてください。"),("What would you like to know about it?","その仕事について何を知りたいですか？"),("Yes, she likes it a lot.","はい、とても気に入っています。"),("That is good to hear.","それはよかったです。")),
 wild=("Friend",1,1,("Where does your brother live?","弟さんはどこに住んでいますか？"),("Is there anything else you want to ask?","ほかに聞きたいことはありますか？"),("Yes, he works near his home.","はい、家の近くで働いています。"),("That sounds convenient.","便利そうですね。"))),
16: dict(
 model=("Coworker",0,0,("Ask me about my morning routine.","私の朝の日課について聞いてください。"),("Around seven. What else would you like to know?","7時ごろです。ほかに何を知りたいですか？"),("Usually at the cafe downstairs.","ふだんは下のカフェです。"),("Thanks. Our schedules are different.","ありがとう。私たちの予定は違いますね。")),
 wild=("Coworker",1,1,("What else would you like to know about my day?","私の一日について、ほかに何を知りたいですか？"),("At nine. You can ask me one more thing.","9時です。もう一つ聞いてください。"),("I usually work from home.","ふだんは在宅で働きます。"),("That sounds comfortable.","快適そうですね。"))),
17: dict(
 model=("Friend",0,0,("Ask me about exercise.","運動について聞いてください。"),("Usually twice a week. How about you?","ふだんは週2回です。あなたは？"),("That is still pretty often.","それでもかなり多いですね。"),("I try to keep it regular.","続けるようにしています。")),
 wild=("Friend",1,1,("Ask me about another weekly habit.","別の毎週の習慣について聞いてください。"),("I cook most days. How often do you cook?","ほぼ毎日料理します。あなたはどのくらい料理しますか？"),("Three times a month is a start.","月3回でもいいスタートですね。"),("I want to do it more often.","もっと頻繁にしたいです。"))),
18: dict(
 model=("Friend",0,0,("Ask me about something I can do.","私にできることについて聞いてください。"),("No, I cannot. How about you?","いいえ、できません。あなたは？"),("Riding a bike is useful too.","自転車に乗れるのも便利ですね。"),("I use it all the time.","いつも使っています。")),
 wild=("Friend",1,1,("Ask me about a different ability.","別のできることについて聞いてください。"),("Yes, I can. What can you do?","はい、できます。あなたは何ができますか？"),("Walking is still good exercise.","歩くのもいい運動ですね。"),("That is true.","確かにそうですね。"))),
19: dict(
 model=("Clerk",0,0,("Can I help you?","何かお手伝いしましょうか？"),("It is fifty dollars.","50ドルです。"),("Yes, five-zero.","はい、5、0です。"),("Thanks for confirming.","確認してくれてありがとうございます。")),
 wild=("Clerk",1,1,("Is there something you would like to see?","何かご覧になりますか？"),("That bag is thirty dollars.","あのかばんは30ドルです。"),("Thirty: three-zero.","30、3、0です。"),("Got it. Thank you.","分かりました。ありがとうございます。"))),
21: dict(
 model=("Friend",0,0,("This jacket might fit you.","このジャケットは合うかもしれません。"),("Of course. Can I take a photo?","もちろん。写真を撮ってもいいですか？"),("Thanks. The jacket looks good.","ありがとう。そのジャケット、似合っています。"),("I like it too.","私も気に入りました。")),
 wild=("Friend",1,1,("There is an empty chair here.","ここに空いている椅子があります。"),("Sure. Can I sit next to you?","どうぞ。隣に座ってもいいですか？"),("Great. Now we can talk.","よかった。これで話せますね。"),("Have a seat.","どうぞ座ってください。"))),
22: dict(
 model=("Server",0,0,("Are you ready to order?","ご注文はお決まりですか？"),("Certainly. Anything to drink?","かしこまりました。お飲み物はいかがですか？"),("Great. I will bring that soon.","かしこまりました。すぐお持ちします。"),("Thank you.","ありがとうございます。")),
 wild=("Server",1,1,("What would you like today?","今日は何になさいますか？"),("Good choice. Would you like anything else?","いいですね。ほかにもご注文はありますか？"),("Of course. I will bring both.","かしこまりました。両方お持ちします。"),("Thanks.","ありがとうございます。"))),
23: dict(
 model=("Friend",0,0,("Let's order the drinks first.","まず飲み物を注文しましょう。"),("Good. Now let's plan the rest of the meal.","いいですね。では残りの食事を考えましょう。"),("Enough for four people.","4人分あれば十分です。"),("Got it.","分かりました。")),
 wild=("Friend",1,1,("What should we get for the trip?","旅行用に何を買いましょうか？"),("Okay. We should check the other supplies too.","分かりました。ほかの物も確認しましょう。"),("About six bottles altogether.","全部で6本くらいです。"),("I will put them on the list.","リストに入れておきます。"))),
24: dict(
 model=("Staff",0,0,("The next train leaves from platform thirteen.","次の電車は13番ホームから出ます。"),("Of course: platform one-three.","もちろんです。ホームは1、3です。"),("Yes. I will speak more slowly.","はい。もっとゆっくり話します。"),("Thank you.","ありがとうございます。")),
 wild=("Staff",1,1,("My name is Christopher Bell.","私の名前はクリストファー・ベルです。"),("Certainly: Christopher Bell.","もちろんです。クリストファー・ベルです。"),("Of course. Chris-to-pher Bell.","もちろんです。クリス・ト・ファー・ベルです。"),("Now I have it. Thanks.","分かりました。ありがとうございます。"))),
}

VOCAB = {
12:("finish|終える; around|〜ごろ","start|始める; work|仕事; usually|ふだん",""),
13:("habit|習慣; exercise|運動する","coffee|コーヒー; cook|料理する; weekend|週末","routine|日課"),
14:("instead|その代わり; drive|運転する","train|電車; breakfast|朝食; water|水",""),
15:("downtown|中心街; nearby|近くに","work|働く; live|住む; study|勉強する","fit|合うこと"),
16:("get up|起きる; get home|帰宅する","time|時刻; lunch|昼食; usually|ふだん","schedule|予定"),
17:("twice|2回; once|1回","week|週; month|月; year|年; exercise|運動する","frequency|頻度"),
18:("ability|能力; ride|乗る; bake|焼く","drive|運転する; swim|泳ぐ; cook|料理する",""),
19:("price|値段; expensive|高い","ticket|チケット; bag|かばん; coffee|コーヒー","dollar|ドル"),
21:("permission|許可; fitting room|試着室","photo|写真; sit|座る; use|使う","take your time|ごゆっくり"),
22:("receipt|レシート; to go|持ち帰り","chicken|チキン; soup|スープ; menu|メニュー","for here|店内で"),
23:("bottle|ボトル; piece|一切れ; bowl|茶碗","coffee|コーヒー; water|水; rice|ご飯","container|容器"),
24:("repeat|繰り返す; clearly|はっきり; louder|より大きな声で","name|名前; platform|ホーム; slowly|ゆっくり","catch|聞き取る"),
}


def esc(s): return html.escape(s, quote=True)
def strip_marks(s): return re.sub(r"\{/?t\}", "", s)
def marks(s, cls="ending"):
    return esc(s).replace("{t}", f'<span class="{cls}">').replace("{/t}", "</span>")

def set_vocab(head, number):
    for category,value in zip(("new","assumed","receptive"),VOCAB[number]):
        head=re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',rf'\g<1>{value}\2',head,count=1)
    return head

def known_page(number):
    entries=[]
    for field in VOCAB[number][:2]:
        for item in field.split("; "):
            if "|" in item:
                en,ja=item.split("|",1); entries.append((ja,en))
    cards="".join(f'<div class="known-row"><span class="j">{esc(ja)}</span><span class="k">{esc(en)}</span></div>' for ja,en in entries[:3])
    return section("words-you-know","Words you know","知っている単語",'<p class="section-subtitle"><span class="ko">Say the words you recognize, then use them in the lesson.</span><span class="ja">知っている単語を言って、レッスンで使いましょう。</span></p><div class="known lines">'+cards+'</div>')


def inputs(s, prefix):
    out=[]; pos=0
    for i,m in enumerate(re.finditer(r"\{t\}(.*?)\{/t\}", s)):
        out.append(esc(s[pos:m.start()])); ans=m.group(1)
        out.append(f'<textarea class="free-input phrase-input" data-sync-id="{prefix}-{i}" data-answer="{esc(ans)}" rows="1" autocomplete="off" spellcheck="false"></textarea>')
        pos=m.end()
    out.append(esc(s[pos:])); return "".join(out)


def section(pid,title,ja,body):
    return f'''    <div class="section" data-page-id="{pid}"><h2 class="section-title">{title} <span class="title-ja">({ja})</span></h2>{body}</div>\n'''


def teach(pid, pattern, meaning):
    lines="".join(f'<div class="model-line"><span class="korean">{marks(en)}</span><span class="translation">{marks(jp)}</span></div>' for en,jp,_ in pattern[:3])
    body=f'<p class="section-subtitle pattern-meaning"><span class="ko">{esc(meaning[0])}</span><span class="ja">{esc(meaning[1])}</span></p><div class="model-lines">{lines}</div>'
    return section(pid,"See the pattern","パターンを見よう",body)


def rule_example(pattern):
    """Show a complete English example in the wrapping sentence component."""
    en, jp, _ = pattern[0]
    return (
        '<div class="model-lines"><div class="model-line">'
        f'<span class="korean">{marks(en)}</span>'
        f'<span class="translation">{marks(jp)}</span>'
        '</div></div>'
    )


def read(pid, pattern):
    lines="".join(f'<div class="model-line"><span class="korean">{marks(en)}</span><span class="translation">{marks(jp)}</span></div>' for en,jp,_ in pattern)
    return section(pid,"Read the sentences","文を読もう",'<p class="section-subtitle"><span class="ko">Read the four sentences.</span><span class="ja">4つの文を読んでみましょう。</span></p><div class="model-lines">'+lines+'</div>')


def reorder(pid, pattern):
    blocks=[]
    for i,(en,jp,chunks) in enumerate(pattern):
        choices="".join(f'<span class="choice" data-item-id="{pid}-{i}-{j}">{esc(c)}</span>' for j,c in enumerate(chunks.split("|")[::-1]))
        blocks.append(f'<div class="task-block"><div class="answer-box small"><span class="answer-label">{esc(strip_marks(jp))}</span><span class="answer-space build-zone" data-sync-id="{pid}-{i}" data-sync-kind="order" data-a="{esc(strip_marks(en))}"></span></div>{choices}</div>')
    return section(pid,"Build the sentence","文を組み立てよう",'<p class="section-subtitle"><span class="ko">Put the four meaning chunks in order.</span><span class="ja">4つの意味のまとまりを順番に並べましょう。</span></p>'+"".join(blocks))


def fill(pid, pattern):
    blocks=[]
    for r,(en,jp,_) in enumerate(pattern):
        fields=[]; pos=0
        for i,m in enumerate(re.finditer(r"\{t\}(.*?)\{/t\}",en)):
            fields.append(esc(en[pos:m.start()])); ans=m.group(1)
            fields.append(f'<input class="slot-input" type="text" data-sync-id="{pid}-{r}-{i}" data-answer="{esc(ans)}" autocomplete="off" spellcheck="false">'); pos=m.end()
        fields.append(esc(en[pos:]))
        blocks.append(f'<div class="task-block"><div class="answer-box"><span class="answer-label">{marks(jp,"target ending")}</span><span class="answer-fill"><span class="korean">{"".join(fields)}</span></span></div></div>')
    return section(pid,"Fill the frame","空欄をうめよう",'<p class="section-subtitle"><span class="ko">Complete only the highlighted pattern.</span><span class="ja">強調されたパターンだけを空欄に入れましょう。</span></p><div class="tutor-note">Write the learner\'s answer exactly as they say it.</div>'+"".join(blocks))


def translate(pid, pattern):
    blocks="".join(f'<div class="task-block"><div class="answer-box"><span class="answer-label">{esc(strip_marks(jp))}</span><span class="answer-space as-input"><input class="space-input" type="text" data-sync-id="{pid}-{i}" data-answer="{esc(strip_marks(en))}" autocomplete="off" spellcheck="false"></span></div></div>' for i,(en,jp,_) in enumerate(pattern))
    return section(pid,"Say it in English","英語にしよう",'<p class="section-subtitle"><span class="ko">Read the Japanese, then say the whole sentence in English.</span><span class="ja">日本語を見て、文をまるごと英語で言いましょう。</span></p>'+blocks)


def avatar(src,name): return f'<span class="who"><img class="avatar" src="{src}" alt=""><span class="who-name">{name}</span></span>'
def turn(kind,src,name,en,jp): return f'<div class="turn {kind}">{avatar(src,name)}<div class="bubble {"me" if kind=="me" else ""}"><span class="korean">{en}</span><span class="translation">{jp}</span></div></div>'
def partner_ja(line): return PARTNER_JA[line]


def dialogue(number, d, variant="model", complete=False, prefix="dlg"):
    role,p1_row,p2_row,first,follow,close,last=DIALOGUES[number][variant]
    a1,j1,_=d["p1"][p1_row]; a2,j2,_=d["p2"][p2_row]
    mine1=inputs(a1,f"{prefix}-p1") if complete else marks(a1)
    mine2=inputs(a2,f"{prefix}-p2") if complete else marks(a2)
    jp1=marks(j1,"target") if complete else marks(j1)
    jp2=marks(j2,"target") if complete else marks(j2)
    return ''.join([
      turn("other",OTHER,role,esc(first[0]),esc(first[1])),
      turn("me",ME,"Me",mine1,jp1),
      turn("other",OTHER,role,esc(follow[0]),esc(follow[1])),
      turn("me",ME,"Me",mine2,jp2),
      turn("other",OTHER,role,esc(close[0]),esc(close[1])),
      turn("me",ME,"Me",esc(last[0]),esc(last[1]))])


def build(number,d):
    source=PILOT.read_text(encoding="utf-8"); head,foot=new_lesson.split_shell(source)
    slug=f'{number:02d}-{d["slug"]}'
    head=new_lesson.retarget(head,review_id=f"CORE-{number}",lesson_id=slug,level="A1",title=d["title"],title_ko=d["ko"],title_ja=d["ja"],version="2026-08-19")
    head=set_vocab(head.replace('content="todo"','content="reviewed"'),number)
    goal_en,goal_ja=d["goal"]
    pages=[f'''    <div class="transition-page" data-page-id="lesson-goal" data-act="Everyday English"><span class="transition-kicker">GOAL</span><h2 class="transition-title">{esc(d["title"])} <span class="title-ja">({esc(d["ja"])})</span></h2><p class="section-subtitle"><span class="ko">{esc(goal_en)}</span><span class="ja">{esc(goal_ja)}</span></p><div class="known lines"><div class="known-row"><span class="k">Notice two useful frames</span><span class="j">二つの表現に気づく</span></div><div class="known-row"><span class="k">Build and complete them</span><span class="j">組み立てて完成する</span></div><div class="known-row"><span class="k">Use them in a conversation</span><span class="j">会話で使う</span></div></div></div>\n''',
      known_page(number),
      f'    <div class="transition-page" data-page-id="part1-intro" data-act="Pattern 1"><span class="transition-kicker">PATTERN 1</span><h2 class="transition-title">{esc(strip_marks(d["p1"][0][0]))}</h2></div>\n',
      teach("p1-teach",d["p1"],d["goal"]),read("p1-read",d["p1"]),
      section("p1-rule","One useful rule","一つのルール",f'<p class="section-subtitle"><span class="ko">{esc(d["rule"][0])}</span><span class="ja">{esc(d["rule"][1])}</span></p>'+rule_example(d["p1"])),
      reorder("p1-reorder",d["p1"]),fill("p1-fill",d["p1"]),translate("p1-translate",d["p1"]),
      section("p1-write","Make it yours","自分の文にしよう",f'<p class="section-subtitle"><span class="ko">{esc(d["prompt"][0])}</span><span class="ja">{esc(d["prompt"][1])}</span></p><div class="task-block"><div class="answer-box tall"><span class="answer-label">自分の言葉で</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="p1-write" rows="2" spellcheck="false"></textarea></span></div></div>'),
      f'    <div class="transition-page" data-page-id="part2-intro" data-act="Pattern 2"><span class="transition-kicker">PATTERN 2</span><h2 class="transition-title">{esc(strip_marks(d["p2"][0][0]))}</h2></div>\n',
      teach("p2-teach",d["p2"],d["goal"]),read("p2-read",d["p2"]),
      section("p2-rule","Connect the idea","言い方をつなげよう",'<p class="section-subtitle"><span class="ko">Use the second frame to answer, add detail, or check the first idea.</span><span class="ja">二つ目の表現で答えたり、情報を加えたり、最初の内容を確認したりしましょう。</span></p>'+rule_example(d["p2"])),
      reorder("p2-reorder",d["p2"]),fill("p2-fill",d["p2"]),translate("p2-translate",d["p2"]),
      section("p2-write","Add your detail","自分の情報を加えよう",f'<p class="section-subtitle"><span class="ko">Answer the question with a true detail about you.</span><span class="ja">自分について本当の情報を加えて答えましょう。</span></p><div class="task-block"><div class="answer-box tall"><span class="answer-label">自分の言葉で</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="p2-write" rows="2" spellcheck="false"></textarea></span></div></div>'),
      '    <div class="transition-page" data-page-id="part3-intro" data-act="Conversation"><span class="transition-kicker">PUT IT TOGETHER</span><h2 class="transition-title">Use both patterns <span class="title-ja">(二つを一緒に使おう)</span></h2></div>\n',
      section("p3-model","Read the conversation","会話を読もう",'<p class="section-subtitle"><span class="ko">Read your lines while I read the other role.</span><span class="ja">自分のセリフを読み、私は相手役を読みます。</span></p><div class="dialogue">'+dialogue(number,d)+'</div>'),
      section("p3-complete","Complete the conversation","会話を完成しよう",'<p class="section-subtitle"><span class="ko">Say only the missing pattern words.</span><span class="ja">空いているパターンの部分だけを言いましょう。</span></p><div class="tutor-note">Write each target exactly as the learner says it.</div><div class="dialogue">'+dialogue(number,d,complete=True)+'</div>'),
      section("p3-freetalk","Your real answer","自分の答え",f'<p class="section-subtitle"><span class="ko">{esc(d["prompt"][0])}</span><span class="ja">{esc(d["prompt"][1])}</span></p><div class="dialogue"><div class="turn other"><span class="who"><span class="avatar icon">T</span><span class="who-name">Tutor</span></span><div class="bubble"><span class="korean">{esc(d["prompt"][0])}</span><span class="translation">{esc(d["prompt"][1])}</span></div></div><div class="turn me"><span class="who"><span class="avatar icon">私</span><span class="who-name">Me</span></span><div class="bubble me"><div class="answer-box tall"><span class="answer-label">Use today&#39;s patterns</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-me" rows="2" spellcheck="false"></textarea></span></div></div></div><div class="turn me"><span class="who"><span class="avatar icon">私</span><span class="who-name">Me</span></span><div class="bubble me"><span class="korean">How about you?</span><span class="translation">あなたはどうですか？</span></div></div><div class="turn other"><span class="who"><span class="avatar icon">T</span><span class="who-name">Tutor</span></span><div class="bubble"><div class="answer-box"><span class="answer-label">Tutor\'s answer</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-tutor" rows="2" spellcheck="false"></textarea></span></div></div></div></div>'),
      section("in-the-wild","A new situation","別の場面",'<p class="section-subtitle"><span class="ko">Use the same two patterns in a fresh conversation.</span><span class="ja">同じ二つのパターンを別の会話で使いましょう。</span></p><div class="dialogue">'+dialogue(number,d,"wild",True,"wild")+'</div>'),
      section("native-tip","Two useful extras","使える表現",f'<p class="section-subtitle"><span class="ko">Choose the expression that fits what you really mean.</span><span class="ja">本当に言いたいことに合う表現を選びましょう。</span></p><div class="model-lines"><div class="model-line"><span class="korean">{esc(d["tip"][0])}</span><span class="translation">{esc(d["tip"][1])}</span></div><div class="model-line"><span class="korean">{esc(d["tip"][2])}</span><span class="translation">{esc(d["tip"][3])}</span></div></div>')]
    out=TRACK/"courses"/COURSE/"lessons"/slug/"lesson.html"
    return out,new_lesson.redepth(head+"\n".join(pages)+foot,out)


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh",action="store_true"); args=ap.parse_args()
    for n,d in LESSONS.items():
        out,text=build(n,d)
        if out.exists() and not args.refresh: raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS)} Core decks generated")
    return 0


if __name__=="__main__": raise SystemExit(main())
