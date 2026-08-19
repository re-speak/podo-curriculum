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
 p2=rows(("{t}I usually{/t} finish work {t}around{/t} six.", "{t}ふだん{/t}6時{t}ごろ{/t}仕事を終えます。", "I usually|finish work|around|six."),("{t}I usually{/t} eat lunch {t}around{/t} twelve.", "{t}ふだん{/t}12時{t}ごろ{/t}昼食をとります。", "I usually|eat lunch|around|twelve."),("{t}I usually{/t} have dinner {t}around{/t} seven.", "{t}ふだん{/t}7時{t}ごろ{/t}夕食をとります。", "I usually|have dinner|around|seven."),("{t}I usually{/t} start work {t}around{/t} nine.", "{t}ふだん{/t}9時{t}ごろ{/t}仕事を始めます。", "I usually|start work|around|nine.")),
 rules=(("Use at before an exact clock time: at nine, at ten.", "正確な時刻の前には at を置き、at nine、at ten の形にします。"),("Put usually before the main verb, and use around before an approximate time.", "usually は動詞の前に置き、だいたいの時刻には around を使います。")), prompt=("What does a normal workday look like for you?", "ふだんの仕事の日はどんな一日ですか？"), partner=("Coworker", "What time do you normally start?", "And when do you usually finish?", "That is a long day."), tip=("every day", "毎日", "most days", "たいていの日")),
13: dict(slug="do-you-drink-coffee", title="Do you drink coffee?", ko="커피를 마셔요?", ja="コーヒーを飲みますか？", goal=("Ask about a habit and give a short answer with one detail.", "習慣についてたずね、短い答えに一つ情報を加えましょう。"),
 p1=rows(("{t}Do you{/t} drink coffee?", "コーヒーを{t}飲みますか{/t}？", "Do you|drink|coffee?"),("{t}Do you{/t} cook at home?", "家で{t}料理しますか{/t}？", "Do you|cook|at home?"),("{t}Do you{/t} work on weekends?", "週末に{t}働きますか{/t}？", "Do you|work|on weekends?"),("{t}Do you{/t} exercise every day?", "毎日{t}運動しますか{/t}？", "Do you|exercise|every day?")),
 p2=rows(("{t}Yes, I do.{/t} Every morning.", "{t}はい、します。{/t}毎朝です。", "Yes,|I do.|Every morning."),("{t}Yes, I do.{/t} At home.", "{t}はい、します。{/t}家でです。", "Yes,|I do.|At home."),("{t}Yes, I do.{/t} Every weekend.", "{t}はい、します。{/t}毎週末です。", "Yes,|I do.|Every weekend."),("{t}Yes, I do.{/t} Almost every day.", "{t}はい、します。{/t}ほぼ毎日です。", "Yes,|I do.|Almost every day.")),
 rules=(("Put do before you and keep the main verb plain.", "do を you の前に置き、後ろの動詞は原形のままにします。"),("Use Yes, I do or No, I don't as the short answer, then add one detail.", "短く答えるときは Yes, I do または No, I don't を使い、そのあとに一つ情報を加えます。")), prompt=("Ask me about one of my everyday habits.", "私の日常の習慣を一つたずねてください。"), partner=("Friend", "Ask me something about my routine.", "Yes, I do. How about you?", "Now we know one thing in common."), tip=("not really", "あまり", "all the time", "いつも")),
14: dict(slug="i-dont-drive-to-work", title="I don't drive to work", ko="차로 출근하지 않아요", ja="車で通勤しません", goal=("Contrast something you do with something you do not do.", "することと、しないことを対比して話しましょう。"),
 p1=rows(("{t}I don't{/t} drive to work.", "車で通勤{t}しません{/t}。", "I don't|drive|to work."),("{t}I don't{/t} eat breakfast.", "朝ごはんを{t}食べません{/t}。", "I don't|eat|breakfast."),("{t}I don't{/t} work on Sundays.", "日曜日は{t}働きません{/t}。", "I don't|work|on Sundays."),("{t}I don't{/t} drink tea.", "お茶は{t}飲みません{/t}。", "I don't|drink|tea.")),
 p2=rows(("I take the train {t}instead{/t}.", "{t}その代わり{/t}電車に乗ります。", "I|take|the train|instead."),("I have coffee {t}instead{/t}.", "{t}その代わり{/t}コーヒーを飲みます。", "I|have|coffee|instead."),("I work on Saturday {t}instead{/t}.", "{t}その代わり{/t}土曜日に働きます。", "I|work|on Saturday|instead."),("I drink water {t}instead{/t}.", "{t}その代わり{/t}水を飲みます。", "I|drink|water|instead.")),
 rules=(("Use don't before the plain verb to say what you do not do.", "しないことを言うときは、動詞の原形の前に don't を置きます。"),("Put instead after the alternative you choose.", "代わりにすることの後ろに instead を置きます。")), prompt=("Tell me one thing you do differently from most people.", "多くの人とは違う習慣を一つ教えてください。"), partner=("Coworker", "Do you drive to work?", "How do you get here, then?", "The train sounds easier."), tip=("not every day", "毎日ではない", "on weekends", "週末に")),
15: dict(slug="she-works-downtown", title="She works downtown", ko="그녀는 시내에서 일해요", ja="彼女は中心街で働いています", goal=("Exchange information about another person.", "別の人について情報をやり取りしましょう。"),
 p1=rows(("{t}She works{/t} downtown.", "彼女は中心街で{t}働いています{/t}。", "She|works|downtown."),("{t}He lives{/t} nearby.", "彼は近くに{t}住んでいます{/t}。", "He|lives|nearby."),("{t}She studies{/t} at night.", "彼女は夜に{t}勉強します{/t}。", "She|studies|at night."),("{t}He cooks{/t} at home.", "彼は家で{t}料理します{/t}。", "He|cooks|at home.")),
 p2=rows(("{t}Does she{/t} like it?", "彼女はそこが{t}好きですか{/t}？", "Does she|like|it?"),("{t}Does he{/t} work there?", "彼はそこで{t}働いていますか{/t}？", "Does he|work|there?"),("{t}Does she{/t} study English?", "彼女は英語を{t}勉強しますか{/t}？", "Does she|study|English?"),("{t}Does he{/t} cook often?", "彼はよく{t}料理しますか{/t}？", "Does he|cook|often?")),
 rules=(("With he or she, change the present-tense verb: usually add -s, with spelling changes such as study to studies.", "he や she では現在形の動詞を変え、通常は -s をつけ、study は studies のように綴りも変えます。"),("In a question, use does and return the main verb to its plain form.", "質問では does を使い、後ろの動詞は原形に戻します。")), prompt=("Tell me about someone you know, then let me ask about them.", "知っている人について話し、その人について私に質問させてください。"), partner=("Friend", "Where does your sister work?", "Does she like it there?", "It sounds like a good fit."), tip=("I think so.", "そうだと思います", "I don't know.", "分かりません")),
16: dict(slug="what-time-do-you-get-up", title="What time do you get up?", ko="몇 시에 일어나요?", ja="何時に起きますか？", goal=("Ask when and where a routine happens.", "習慣がいつ、どこで行われるかをたずねましょう。"),
 p1=rows(("{t}What time do you{/t} get up?", "{t}何時に{/t}起きますか？", "What time|do you|get up?"),("{t}What time do you{/t} start work?", "{t}何時に{/t}仕事を始めますか？", "What time|do you|start work?"),("{t}What time do you{/t} have lunch?", "{t}何時に{/t}昼食をとりますか？", "What time|do you|have lunch?"),("{t}What time do you{/t} get home?", "{t}何時に{/t}帰宅しますか？", "What time|do you|get home?")),
 p2=rows(("{t}Where do you usually{/t} have lunch?", "{t}ふだんどこで{/t}昼食をとりますか？", "Where|do you usually|have lunch?"),("{t}Where do you usually{/t} work?", "{t}ふだんどこで{/t}働きますか？", "Where|do you usually|work?"),("{t}Where do you usually{/t} exercise?", "{t}ふだんどこで{/t}運動しますか？", "Where|do you usually|exercise?"),("{t}Where do you usually{/t} study?", "{t}ふだんどこで{/t}勉強しますか？", "Where|do you usually|study?")),
 rules=(("Put What time first, then use do you plus the action.", "What time を最初に置き、その後ろを do you と動作の順にします。"),("Put Where first; usually stays before the main verb.", "Where を最初に置き、usually は動詞の前に置きます。")), prompt=("Ask me two questions about my daily routine.", "私の日課について二つ質問してください。"), partner=("Coworker", "What time do you usually get up?", "Where do you have lunch?", "Our schedules are quite different."), tip=("it depends", "場合によります", "most days", "たいていの日")),
17: dict(slug="how-often-do-you-exercise", title="How often do you exercise?", ko="얼마나 자주 운동해요?", ja="どのくらい運動しますか？", goal=("Ask how often something happens and answer approximately.", "頻度をたずね、だいたいの回数で答えましょう。"),
 p1=rows(("{t}How often do you{/t} exercise?", "{t}どのくらいの頻度で{/t}運動しますか？", "How often|do you|exercise?"),("{t}How often do you{/t} cook?", "{t}どのくらいの頻度で{/t}料理しますか？", "How often|do you|cook?"),("{t}How often do you{/t} travel?", "{t}どのくらいの頻度で{/t}旅行しますか？", "How often|do you|travel?"),("{t}How often do you{/t} call home?", "{t}どのくらいの頻度で{/t}家に電話しますか？", "How often|do you|call home?")),
 p2=rows(("{t}About{/t} twice {t}a week{/t}.", "{t}だいたい{/t}週{t}2回{/t}です。", "About|twice|a week."),("{t}About{/t} three times {t}a month{/t}.", "{t}だいたい{/t}月{t}3回{/t}です。", "About|three times|a month."),("{t}About{/t} once {t}a year{/t}.", "{t}だいたい{/t}年{t}1回{/t}です。", "About|once|a year."),("{t}About{/t} four times {t}a week{/t}.", "{t}だいたい{/t}週{t}4回{/t}です。", "About|four times|a week.")),
 rules=(("Put How often first, then use do you plus the action.", "How often を最初に置き、その後ろを do you と動作の順にします。"),("Keep twice a week and three times a month together; a week or a month means per week or per month.", "twice a week や three times a month はひとまとまりで使い、a week、a month は「1週間につき」「1か月につき」という意味になります。")), prompt=("Ask how often I do something, then compare our answers.", "私に頻度をたずね、二人の答えを比べてください。"), partner=("Friend", "How often do you exercise?", "What about on busy weeks?", "That is still pretty often."), tip=("every day", "毎日", "not very often", "あまり頻繁ではない")),
18: dict(slug="can-you-drive", title="Can you drive?", ko="운전할 수 있어요?", ja="運転できますか？", goal=("Ask about an ability and contrast what you can and cannot do.", "できることをたずね、できることとできないことを対比しましょう。"),
 p1=rows(("{t}Can you{/t} drive?", "運転{t}できますか{/t}？", "Can you|drive?"),("{t}Can you{/t} swim?", "泳ぐことが{t}できますか{/t}？", "Can you|swim?"),("{t}Can you{/t} cook?", "料理が{t}できますか{/t}？", "Can you|cook?"),("{t}Can you{/t} ski?", "スキーが{t}できますか{/t}？", "Can you|ski?")),
 omit_reorder=(1,),
 p2=rows(("{t}I can{/t} ride a bike, {t}but I can't{/t} drive.", "自転車には{t}乗れますが{/t}、運転は{t}できません{/t}。", "I can|ride a bike,|but I can't|drive."),("{t}I can{/t} walk, {t}but I can't{/t} run.", "歩くことは{t}できますが{/t}、走ることは{t}できません{/t}。", "I can|walk,|but I can't|run."),("{t}I can{/t} cook, {t}but I can't{/t} bake.", "料理は{t}できますが{/t}、お菓子作りは{t}できません{/t}。", "I can|cook,|but I can't|bake."),("{t}I can{/t} read it, {t}but I can't{/t} write it.", "読むことは{t}できますが{/t}、書くことは{t}できません{/t}。", "I can|read it,|but I can't|write it.")),
 rules=(("Use Can you plus a plain verb to ask about an ability.", "できるかたずねるときは Can you の後ろに動詞の原形を置きます。"),("Put a plain verb after both can and can't; use but to contrast the two abilities.", "can と can't の後ろはどちらも動詞の原形にし、二つを but で対比します。")), prompt=("Ask me about one ability, then tell me what you can do.", "私にできることを一つたずね、自分にできることも話してください。"), partner=("Friend", "Can you drive?", "What can you do well, then?", "That is useful too."), tip=("pretty well", "かなり上手に", "not yet", "まだ")),
19: dict(slug="how-much-is-this", title="How much is this?", ko="이거 얼마예요?", ja="これはいくらですか？", goal=("Ask a price and confirm a number you heard.", "値段をたずね、聞いた数字を確認しましょう。"),
 p1=rows(("{t}How much is{/t} this one?", "これは{t}いくらですか{/t}？", "How much|is this one?"),("{t}How much is{/t} that bag?", "あのかばんは{t}いくらですか{/t}？", "How much|is that bag?"),("{t}How much is{/t} the ticket?", "そのチケットは{t}いくらですか{/t}？", "How much|is the ticket?"),("{t}How much is{/t} a coffee?", "コーヒーは{t}いくらですか{/t}？", "How much|is a coffee?")),
 omit_reorder=(1,),
 p2=rows(("{t}Is that{/t} fifteen {t}or{/t} fifty?", "{t}それは{/t}15{t}ですか、それとも{/t}50ですか？", "Is that|fifteen|or|fifty?"),("{t}Is that{/t} thirteen {t}or{/t} thirty?", "{t}それは{/t}13{t}ですか、それとも{/t}30ですか？", "Is that|thirteen|or|thirty?"),("{t}Is that{/t} fourteen {t}or{/t} forty?", "{t}それは{/t}14{t}ですか、それとも{/t}40ですか？", "Is that|fourteen|or|forty?"),("{t}Is that{/t} sixteen {t}or{/t} sixty?", "{t}それは{/t}16{t}ですか、それとも{/t}60ですか？", "Is that|sixteen|or|sixty?")),
 rules=(("Use How much is plus the complete item to ask its price.", "値段をたずねるときは How much is の後ろに、品物をひとまとまりで置きます。"),("Use the frame Is that X or Y to check which of two numbers you heard.", "聞こえた数字を確認するときは Is that X or Y の形を使います。")), prompt=("Ask the price of something near you, then check the number I give.", "近くの物の値段をたずね、私が言う数字を確認してください。"), partner=("Clerk", "Can I help you?", "It is fifty dollars.", "Yes, five-zero."), tip=("That's a bit expensive.", "少し高いですね", "I'll take it.", "これにします")),
21: dict(slug="can-i-try-this-on", title="Can I try this on?", ko="이거 입어 봐도 돼요?", ja="これを試着してもいいですか？", goal=("Ask permission and answer a permission request.", "許可を求め、許可を求められたときにも答えましょう。"),
 p1=rows(("{t}Can I{/t} try this on?", "これを試着{t}してもいいですか{/t}？", "Can|I|try this|on?"),("{t}Can I{/t} sit here?", "ここに座っても{t}いいですか{/t}？", "Can|I|sit|here?"),("{t}Can I{/t} take a photo?", "写真を撮っても{t}いいですか{/t}？", "Can|I|take|a photo?"),("{t}Can I{/t} use this?", "これを使っても{t}いいですか{/t}？", "Can|I|use|this?")),
 p2=rows(("{t}Sure, you can{/t} take a photo.", "もちろん、写真を撮って{t}いいですよ{/t}。", "Sure,|you can|take|a photo."),("{t}Sure, you can{/t} sit here.", "もちろん、ここに座って{t}いいですよ{/t}。", "Sure,|you can|sit|here."),("{t}Sure, you can{/t} use this.", "もちろん、これを使って{t}いいですよ{/t}。", "Sure,|you can|use|this."),("{t}Sure, you can{/t} try it on.", "もちろん、試着して{t}いいですよ{/t}。", "Sure,|you can|try it|on.")),
 omit_reorder=(1,),
 rules=(("Use Can I plus a plain verb to ask permission for yourself.", "自分の許可を求めるときは Can I の後ろに動詞の原形を置きます。"),("Use You can plus a plain verb to give permission to the other person.", "相手に許可を与えるときは You can の後ろに動詞の原形を置きます。")), prompt=("Ask permission to do something in this room.", "この部屋で何かをする許可を求めてください。"), partner=("Clerk", "Let me know if you need anything.", "Yes, the fitting room is over there.", "Take your time."), tip=("Go ahead.", "どうぞ", "Sorry, not here.", "すみません、ここではできません")),
22: dict(slug="id-like-the-chicken-please", title="I'd like the chicken, please", ko="치킨으로 주세요", ja="チキンをお願いします", goal=("Order something politely in two common ways.", "よく使う二つの言い方で、丁寧に注文しましょう。"),
 p1=rows(("{t}I'd like{/t} the chicken, {t}please{/t}.", "チキンを{t}お願いします{/t}。", "I'd like|the chicken,|please."),("{t}I'd like{/t} the soup, {t}please{/t}.", "スープを{t}お願いします{/t}。", "I'd like|the soup,|please."),("{t}I'd like{/t} this one, {t}please{/t}.", "これを{t}お願いします{/t}。", "I'd like|this one,|please."),("{t}I'd like{/t} a ticket, {t}please{/t}.", "チケットを1枚{t}お願いします{/t}。", "I'd like|a ticket,|please.")),
 p2=rows(("{t}Can I have{/t} a coffee, {t}please{/t}?", "コーヒーを{t}いただけますか{/t}？", "Can I have|a coffee,|please?"),("{t}Can I have{/t} some water, {t}please{/t}?", "お水を{t}いただけますか{/t}？", "Can I have|some water,|please?"),("{t}Can I have{/t} the menu, {t}please{/t}?", "メニューを{t}いただけますか{/t}？", "Can I have|the menu,|please?"),("{t}Can I have{/t} a receipt, {t}please{/t}?", "レシートを{t}いただけますか{/t}？", "Can I have|a receipt,|please?")),
 rules=(("Keep I'd like together, add the complete item, and put please at the end.", "I'd like をひとまとまりにし、品物を続け、最後に please を置きます。"),("Use Can I have plus the complete item, and put please before the question mark.", "Can I have の後ろに品物を続け、疑問符の前に please を置きます。")), prompt=("Order one thing, then ask me for one extra item.", "一つ注文し、追加でもう一つ頼んでください。"), partner=("Server", "Are you ready to order?", "Anything to drink?", "Great. I will bring that soon."), tip=("This one, please.", "これをお願いします", "for here or to go?", "店内ですか、持ち帰りですか")),
23: dict(slug="two-cups-of-coffee", title="Two cups of coffee", ko="커피 두 잔", ja="コーヒーを2杯", goal=("Ask for an amount of something that is not counted directly.", "直接数えないものの量をたずねたり、頼んだりしましょう。"),
 p1=rows(("{t}Two cups of{/t} coffee, {t}please{/t}.", "コーヒーを{t}2杯お願いします{/t}。", "Two cups|of coffee,|please."),("{t}Two bottles of{/t} water, {t}please{/t}.", "水を{t}2本お願いします{/t}。", "Two bottles|of water,|please."),("{t}Two pieces of{/t} cake, {t}please{/t}.", "ケーキを{t}2切れお願いします{/t}。", "Two pieces|of cake,|please."),("{t}Two bowls of{/t} rice, {t}please{/t}.", "ご飯を{t}2杯お願いします{/t}。", "Two bowls|of rice,|please.")),
 p2=rows(("{t}How much{/t} rice {t}do we need{/t}?", "ご飯は{t}どのくらい必要ですか{/t}？", "How much|rice|do we|need?"),("{t}How much{/t} water {t}do we need{/t}?", "水は{t}どのくらい必要ですか{/t}？", "How much|water|do we|need?"),("{t}How much{/t} coffee {t}do we need{/t}?", "コーヒーは{t}どのくらい必要ですか{/t}？", "How much|coffee|do we|need?"),("{t}How much{/t} time {t}do we need{/t}?", "時間は{t}どのくらい必要ですか{/t}？", "How much|time|do we|need?")),
 rules=(("Count the container or piece, then keep of with the thing: two cups of coffee.", "容器や単位を数え、of と品物をつなげて two cups of coffee の形にします。"),("Use How much plus the non-count noun, then do we need?", "How much の後ろに直接数えない名詞を置き、最後に do we need? を続けます。")), prompt=("Plan drinks for two people and tell me how much we need.", "二人分の飲み物を考え、どのくらい必要か話してください。"), partner=("Clerk", "What can I get you?", "Would you like anything else?", "That will be twelve dollars."), tip=("a little", "少し", "a lot of", "たくさんの")),
24: dict(slug="sorry-can-you-say-that-again", title="Sorry, can you say that again?", ko="죄송하지만 다시 말해 주시겠어요?", ja="すみません、もう一度言ってもらえますか？", goal=("Ask for repetition or slower speech without stopping the conversation.", "会話を止めずに、繰り返しやゆっくり話すことを頼みましょう。"),
 p1=rows(("Sorry, {t}can you say{/t} that {t}again{/t}?", "すみません、それを{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|that|again?"),("Sorry, {t}can you say{/t} your name {t}again{/t}?", "すみません、名前を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|your name|again?"),("Sorry, {t}can you say{/t} the last part {t}again{/t}?", "すみません、最後の部分を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|the last part|again?"),("Sorry, {t}can you say{/t} 'shelf' {t}again{/t}?", "すみません、shelf を{t}もう一度言ってもらえますか{/t}？", "Sorry,|can you say|'shelf'|again?")),
 p2=rows(("{t}Can you speak{/t} more slowly?", "もう少しゆっくり{t}話してもらえますか{/t}？", "Can you|speak|more|slowly?"),("{t}Can you speak{/t} more clearly?", "もう少しはっきり{t}話してもらえますか{/t}？", "Can you|speak|more|clearly?"),("{t}Can you speak{/t} a little louder?", "もう少し大きな声で{t}話してもらえますか{/t}？", "Can you|speak|a little|louder?"),("{t}Can you speak{/t} more slowly, please?", "もう少しゆっくり{t}話してもらえますか{/t}？", "Can you|speak|more slowly,|please?")),
 rules=(("Use Can you say plus the missing detail, then put again at the end.", "Can you say の後ろに聞きたい内容を置き、最後に again を置きます。"),("Use Can you speak plus the change you need, such as more slowly.", "Can you speak の後ろに、more slowly のような必要な話し方を置きます。")), prompt=("Stop me naturally if you do not understand my next sentence.", "次の文が分からなければ、自然に私を止めてください。"), partner=("Staff", "The next train leaves from platform thirteen.", "Of course: platform one-three.", "Yes, that is right."), tip=("I didn't catch that.", "聞き取れませんでした", "a little louder", "もう少し大きな声で")),
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
12:("finish work|仕事を終える; eat lunch|昼食をとる; have dinner|夕食をとる; around|〜ごろ","start work|仕事を始める; usually|ふだん",""),
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

# These fields are deliberately authored, not inferred from the model sentences.
# A generator can safely render a reviewed pedagogical decision, but it cannot
# decide which contrast is worth teaching or what a native-use tip should add.
CANONICAL_SPECS = {
13: dict(
 meanings=(("Use this to ask whether a habit is part of someone's routine.", "習慣が日課の一部かどうかをたずねるときに使います。"), ("Use a short answer first, then add one useful detail.", "まず短く答え、そのあとに役立つ情報を一つ加えます。")),
 writes=(("Ask one habit question you really want answered.", "本当に答えを知りたい習慣の質問を一つ作りましょう。"), ("Answer one habit question about yourself, then add a true detail.", "自分の習慣について短く答え、本当の情報を一つ加えましょう。")),
 choices=(
  (("コーヒーを{t}飲みますか{/t}？", "", "Do you", "You do", " drink coffee?"), ("家で{t}料理しますか{/t}？", "", "Do you", "You do", " cook at home?"), ("週末に{t}働きますか{/t}？", "", "Do you", "You do", " work on weekends?"), ("毎日{t}運動しますか{/t}？", "", "Do you", "You do", " exercise every day?")),
  (("{t}はい、します。{/t}毎朝です。", "Yes, I ", "do", "am", ". Every morning."), ("{t}はい、します。{/t}家でです。", "Yes, I ", "do", "am", ". At home."), ("{t}はい、します。{/t}毎週末です。", "Yes, I ", "do", "am", ". Every weekend."), ("{t}はい、します。{/t}ほぼ毎日です。", "Yes, I ", "do", "am", ". Almost every day.")),
 ),
 rules=(("Put do before you", "do を you の前に", "<b>Do</b> + you + 動詞の原形 + ...?", "Habit question", "習慣についての質問", ("<b>Do you</b> drink coffee?", "<b>Do you</b> cook at home?")), ("Match the short answer", "短い答えを合わせよう", "Yes, I <b>do</b>. / No, I <b>don't</b>.", "Answer with do", "do で答える", ("Yes, I <b>do</b>. Every morning.", "No, I <b>don't</b>. Not very often."))),
 tip=("No, I don't or Not really?", "No, I don't と Not really", "Both are natural. Use “Not really” for a softer, less absolute no.", "どちらも自然です。やわらかく、完全な否定を避けるなら「Not really」を使います。", ("Direct answer", "はっきり答える", "No, I don't.", "いいえ、しません。"), ("Softer answer", "やわらかく答える", "Not really.", "あまりしません。")),
),
14: dict(
 meanings=(("Use this to say that something is not part of your routine.", "あることをふだんしないと伝えるときに使います。"), ("Use this to name the alternative you choose.", "代わりに選ぶことを伝えるときに使います。")),
 writes=(("Write one thing you do not normally do.", "ふだんしないことを一つ書きましょう。"), ("Write what you do instead.", "その代わりにすることを書きましょう。")),
 choices=(
  (("車で通勤{t}しません{/t}。", "I ", "don't", "doesn't", " drive to work."), ("朝ごはんを{t}食べません{/t}。", "I ", "don't", "doesn't", " eat breakfast."), ("日曜日は{t}働きません{/t}。", "I ", "don't", "doesn't", " work on Sundays."), ("お茶は{t}飲みません{/t}。", "I ", "don't", "doesn't", " drink tea.")),
  (("{t}その代わり{/t}電車に乗ります。", "I take the train ", "instead", "too", "."), ("{t}その代わり{/t}コーヒーを飲みます。", "I have coffee ", "instead", "too", "."), ("{t}その代わり{/t}土曜日に働きます。", "I work on Saturday ", "instead", "too", "."), ("{t}その代わり{/t}水を飲みます。", "I drink water ", "instead", "too", ".")),
 ),
 rules=(("Put don't before the action", "動作の前に don't", "I + <b>don't</b> + 動詞の原形", "Negative routine", "しない習慣", ("I <b>don't drive</b> to work.", "I <b>don't eat</b> breakfast.")), ("Put instead after the alternative", "代わりの行動の後ろに instead", "代わりの行動 + <b>instead</b>", "Chosen alternative", "代わりに選ぶこと", ("I take the train <b>instead</b>.", "I drink water <b>instead</b>."))),
 tip=("Don't or don't usually?", "don't と don't usually", "Use “don't” for a general no. Add “usually” when there are exceptions.", "基本的にしないなら「don't」を使います。例外があるなら「don't usually」を使います。", ("General no", "基本的にしない", "I don't drive to work.", "車で通勤しません。"), ("There are exceptions", "例外がある", "I don't usually drive to work.", "ふだんは車で通勤しません。")),
),
15: dict(
 meanings=(("Use this to say what another person regularly does.", "ほかの人がふだん何をするか伝えるときに使います。"), ("Use this to ask a follow-up question about that person.", "その人について続けて質問するときに使います。")),
 writes=(("Write one true sentence about someone you know.", "知っている人について本当の文を一つ書きましょう。"), ("Ask one follow-up question about that person.", "その人について続けて質問を一つ作りましょう。")),
 choices=(
  (("彼女は中心街で{t}働いています{/t}。", "She ", "works", "work", " downtown."), ("彼は近くに{t}住んでいます{/t}。", "He ", "lives", "live", " nearby."), ("彼女は夜に{t}勉強します{/t}。", "She ", "studies", "study", " at night."), ("彼は家で{t}料理します{/t}。", "He ", "cooks", "cook", " at home.")),
  (("彼女はそこが{t}好きですか{/t}？", "", "Does", "Do", " she like it?"), ("彼はそこで{t}働いていますか{/t}？", "", "Does", "Do", " he work there?"), ("彼女は英語を{t}勉強しますか{/t}？", "", "Does", "Do", " she study English?"), ("彼はよく{t}料理しますか{/t}？", "", "Does", "Do", " he cook often?")),
 ),
 rules=(("Change the verb with he or she", "he・she では動詞を変える", "he / she + 動詞<b>-s</b>", "Third-person routine", "ほかの人の習慣", ("She <b>works</b> downtown.", "He <b>lives</b> nearby.")), ("Use does, then the plain verb", "does の後ろは動詞の原形", "<b>Does</b> + he / she + 動詞の原形 + ...?", "Third-person question", "ほかの人への質問", ("<b>Does</b> she <b>like</b> it?", "<b>Does</b> he <b>work</b> there?"))),
 tip=("She works or she's working?", "She works と She's working", "Use the simple present for a regular situation and the -ing form for now or a temporary situation.", "ふだんのことには現在形、今または一時的なことには -ing 形を使います。", ("Regular situation", "ふだんのこと", "She works downtown.", "彼女は中心街で働いています。"), ("Now or temporary", "今・一時的", "She's working downtown this week.", "今週は中心街で働いています。")),
),
16: dict(
 meanings=(("Use this to ask for the clock time of a routine.", "日課の時刻をたずねるときに使います。"), ("Use this to ask for the usual place of a routine.", "日課をふだん行う場所をたずねるときに使います。")),
 writes=(("Ask for the time of one real routine.", "実際の日課を一つ選び、その時刻をたずねましょう。"), ("Ask where one routine usually happens.", "日課を一つ選び、ふだんどこでするかたずねましょう。")),
 choices=(
  (("{t}何時に{/t}起きますか？", "", "What time", "How often", " do you get up?"), ("{t}何時に{/t}仕事を始めますか？", "", "What time", "How often", " do you start work?"), ("{t}何時に{/t}昼食をとりますか？", "", "What time", "How often", " do you have lunch?"), ("{t}何時に{/t}帰宅しますか？", "", "What time", "How often", " do you get home?")),
  (("ふだん{t}どこで{/t}昼食をとりますか？", "", "Where", "When", " do you usually have lunch?"), ("ふだん{t}どこで{/t}働きますか？", "", "Where", "When", " do you usually work?"), ("ふだん{t}どこで{/t}運動しますか？", "", "Where", "When", " do you usually exercise?"), ("ふだん{t}どこで{/t}勉強しますか？", "", "Where", "When", " do you usually study?")),
 ),
 rules=(("Start with What time", "What time から始める", "<b>What time</b> + do you + 動作 + ?", "Ask for a clock time", "時刻をたずねる", ("<b>What time do you</b> get up?", "<b>What time do you</b> start work?")), ("Start with Where", "Where から始める", "<b>Where</b> + do you + usually + 動作 + ?", "Ask for the usual place", "ふだんの場所をたずねる", ("<b>Where do you usually</b> have lunch?", "<b>Where do you usually</b> work?"))),
 tip=("What time or when?", "What time と when", "Use “What time” when you want a clock time. “When” can invite a broader answer.", "時計の時刻を知りたいなら「What time」を使います。「When」はもっと幅広い答えにも使えます。", ("Clock time", "時計の時刻", "What time do you get up?", "何時に起きますか？"), ("Broader time", "幅広い時", "When do you exercise?", "いつ運動しますか？")),
),
17: dict(
 meanings=(("Use this to ask about frequency, not a clock time.", "時刻ではなく頻度をたずねるときに使います。"), ("Use this to give an approximate number of times per period.", "一定の期間あたりのおおよその回数を答えるときに使います。")),
 writes=(("Ask how often one real activity happens.", "実際の活動を一つ選び、頻度をたずねましょう。"), ("Give a true approximate frequency for one activity.", "活動を一つ選び、本当のおおよその頻度を答えましょう。")),
 choices=(
  (("{t}どのくらいの頻度で{/t}運動しますか？", "", "How often", "What time", " do you exercise?"), ("{t}どのくらいの頻度で{/t}料理しますか？", "", "How often", "What time", " do you cook?"), ("{t}どのくらいの頻度で{/t}旅行しますか？", "", "How often", "What time", " do you travel?"), ("{t}どのくらいの頻度で{/t}家に電話しますか？", "", "How often", "What time", " do you call home?")),
  (("だいたい週{t}2回{/t}です。", "About ", "twice", "two", " a week."), ("だいたい月{t}3回{/t}です。", "About ", "three times", "three time", " a month."), ("だいたい年{t}1回{/t}です。", "About ", "once", "one", " a year."), ("だいたい週{t}4回{/t}です。", "About ", "four times", "four time", " a week.")),
 ),
 rules=(("Start with How often", "How often から始める", "<b>How often</b> + do you + 動作 + ?", "Ask about frequency", "頻度をたずねる", ("<b>How often do you</b> exercise?", "<b>How often do you</b> cook?")), ("Build the frequency phrase", "頻度のまとまりを作る", "回数 + <b>a</b> + week / month / year", "Times per period", "期間あたりの回数", ("<b>twice a week</b>", "<b>three times a month</b>"))),
 tip=("Twice or a couple of times?", "twice と a couple of times", "Use “twice” for exactly two. “A couple of times” is often a more casual approximation.", "正確に2回なら「twice」を使います。会話でおおよそ2回なら「a couple of times」も使えます。", ("Exact", "正確", "I exercise twice a week.", "週に2回運動します。"), ("Casual estimate", "会話でのおおよそ", "I exercise a couple of times a week.", "週に2回くらい運動します。")),
),
18: dict(
 meanings=(("Use this to ask whether someone has an ability.", "あることができるかたずねるときに使います。"), ("Use this to contrast one ability with something you cannot do.", "できることと、できないことを対比するときに使います。")),
 writes=(("Ask about one ability you want to know.", "知りたい能力について一つたずねましょう。"), ("Contrast one thing you can do with one thing you cannot do.", "できることと、できないことを一つずつ対比しましょう。")),
 choices=(
  (("運転{t}できますか{/t}？", "", "Can", "Do", " you drive?"), ("泳ぐことが{t}できますか{/t}？", "", "Can", "Do", " you swim?"), ("料理が{t}できますか{/t}？", "", "Can", "Do", " you cook?"), ("スキーが{t}できますか{/t}？", "", "Can", "Do", " you ski?")),
  (("自転車には乗れますが、運転は{t}できません{/t}。", "I can ride a bike, but I ", "can't", "can", " drive."), ("歩くことはできますが、走ることは{t}できません{/t}。", "I can walk, but I ", "can't", "can", " run."), ("料理はできますが、お菓子作りは{t}できません{/t}。", "I can cook, but I ", "can't", "can", " bake."), ("読むことはできますが、書くことは{t}できません{/t}。", "I can read it, but I ", "can't", "can", " write it.")),
 ),
 rules=(("Put a plain verb after can", "can の後ろは動詞の原形", "<b>Can</b> + you + 動詞の原形 + ?", "Ability question", "できるかの質問", ("<b>Can you drive</b>?", "<b>Can you swim</b>?")), ("Contrast can and can't", "can と can't を対比する", "I <b>can</b> + 動作, but I <b>can't</b> + 動作", "Two abilities", "二つのできること", ("I <b>can</b> walk, but I <b>can't</b> run.", "I <b>can</b> cook, but I <b>can't</b> bake."))),
 tip=("Can't or can't yet?", "can't と can't yet", "Add “yet” when you expect or hope the ability may come later.", "今後できるようになる可能性や希望があるなら「yet」を加えます。", ("General inability", "一般的にできない", "I can't drive.", "運転できません。"), ("Maybe later", "今後はできるかも", "I can't drive yet.", "まだ運転できません。")),
),
19: dict(
 meanings=(("Use this to ask the price of one item.", "一つの品物の値段をたずねるときに使います。"), ("Use this to check which of two similar numbers you heard.", "似た二つの数字のどちらを聞いたか確認するときに使います。")),
 writes=(("Ask the price of one item you can see.", "見える品物を一つ選び、値段をたずねましょう。"), ("Check two similar numbers that could be misheard.", "聞き間違えそうな二つの数字を使って確認しましょう。")),
 choices=(
  (("これは{t}いくらですか{/t}？", "How ", "much", "many", " is this one?"), ("あのかばんは{t}いくらですか{/t}？", "How ", "much", "many", " is that bag?"), ("そのチケットは{t}いくらですか{/t}？", "How ", "much", "many", " is the ticket?"), ("コーヒーは{t}いくらですか{/t}？", "How ", "much", "many", " is a coffee?")),
  (("それは15{t}ですか、それとも{/t}50ですか？", "Is that fifteen ", "or", "and", " fifty?"), ("それは13{t}ですか、それとも{/t}30ですか？", "Is that thirteen ", "or", "and", " thirty?"), ("それは14{t}ですか、それとも{/t}40ですか？", "Is that fourteen ", "or", "and", " forty?"), ("それは16{t}ですか、それとも{/t}60ですか？", "Is that sixteen ", "or", "and", " sixty?")),
 ),
 rules=(("Use How much is with one item", "一つの品物には How much is", "<b>How much is</b> + 品物 + ?", "Ask a price", "値段をたずねる", ("<b>How much is</b> this one?", "<b>How much is</b> the ticket?")), ("Put or between the two numbers", "二つの数字の間に or", "Is that + X + <b>or</b> + Y + ?", "Check what you heard", "聞いた数字を確認する", ("Is that fifteen <b>or</b> fifty?", "Is that thirteen <b>or</b> thirty?"))),
 tip=("This or this one?", "this と this one", "Use “this one” when you are choosing among visible options. Plain “this” is enough when the item is already clear.", "見えている選択肢から選ぶなら「this one」を使います。品物が明らかなら「this」だけでも十分です。", ("Item is clear", "品物が明らか", "How much is this?", "これはいくらですか？"), ("Choosing among options", "選択肢から選ぶ", "How much is this one?", "これはいくらですか？")),
),
21: dict(
 meanings=(("Use this to ask permission for yourself.", "自分がしてもよいか許可を求めるときに使います。"), ("Use this to give the other person permission.", "相手に許可を与えるときに使います。")),
 writes=(("Ask permission for one thing you might do in this room.", "この部屋でするかもしれないことの許可を一つ求めましょう。"), ("Give or refuse permission for one action.", "一つの行動について、許可するか断る答えを作りましょう。")),
 choices=(
  (("これを試着{t}してもいいですか{/t}？", "", "Can", "Do", " I try this on?"), ("ここに座っても{t}いいですか{/t}？", "", "Can", "Do", " I sit here?"), ("写真を撮っても{t}いいですか{/t}？", "", "Can", "Do", " I take a photo?"), ("これを使っても{t}いいですか{/t}？", "", "Can", "Do", " I use this?")),
  (("もちろん、写真を撮って{t}いいですよ{/t}。", "Sure, you ", "can", "can't", " take a photo."), ("もちろん、ここに座って{t}いいですよ{/t}。", "Sure, you ", "can", "can't", " sit here."), ("もちろん、これを使って{t}いいですよ{/t}。", "Sure, you ", "can", "can't", " use this."), ("もちろん、試着して{t}いいですよ{/t}。", "Sure, you ", "can", "can't", " try it on.")),
 ),
 rules=(("Use Can I for your permission", "自分の許可には Can I", "<b>Can I</b> + 動詞の原形 + ...?", "Ask permission", "許可を求める", ("<b>Can I</b> try this on?", "<b>Can I</b> sit here?")), ("Use you can to give permission", "許可を与えるなら you can", "Sure, + you <b>can</b> + 動詞の原形", "Give permission", "許可を与える", ("Sure, you <b>can</b> take a photo.", "Sure, you <b>can</b> sit here."))),
 tip=("Can I or could I?", "Can I と Could I", "Both ask permission. “Could I” can sound a little more polite or tentative.", "どちらも許可を求めます。「Could I」は少し丁寧で控えめに聞こえます。", ("Neutral", "ふつう", "Can I try this on?", "これを試着してもいいですか？"), ("More tentative", "少し控えめ", "Could I try this on?", "これを試着してもよろしいですか？")),
),
22: dict(
 meanings=(("Use this to state your order politely.", "注文を丁寧に伝えるときに使います。"), ("Use this to ask for an item politely.", "品物を丁寧に頼むときに使います。")),
 writes=(("Choose one item and order it politely.", "品物を一つ選び、丁寧に注文しましょう。"), ("Ask for one extra item you might need.", "必要になりそうな追加の品物を一つ頼みましょう。")),
 choices=(
  (("チキンを{t}お願いします{/t}。", "", "I'd", "I", " like the chicken, please."), ("スープを{t}お願いします{/t}。", "", "I'd", "I", " like the soup, please."), ("これを{t}お願いします{/t}。", "", "I'd", "I", " like this one, please."), ("チケットを1枚{t}お願いします{/t}。", "", "I'd", "I", " like a ticket, please.")),
  (("コーヒーを{t}いただけますか{/t}？", "", "Can", "Do", " I have a coffee, please?"), ("お水を{t}いただけますか{/t}？", "", "Can", "Do", " I have some water, please?"), ("メニューを{t}いただけますか{/t}？", "", "Can", "Do", " I have the menu, please?"), ("レシートを{t}いただけますか{/t}？", "", "Can", "Do", " I have a receipt, please?")),
 ),
 rules=(("Keep I'd like together", "I'd like をひとまとまりに", "<b>I'd like</b> + 品物 + please.", "State an order", "注文を伝える", ("<b>I'd like</b> the chicken, please.", "<b>I'd like</b> a ticket, please.")), ("Use Can I have before the item", "品物の前に Can I have", "<b>Can I have</b> + 品物 + please?", "Ask for an item", "品物を頼む", ("<b>Can I have</b> a coffee, please?", "<b>Can I have</b> the menu, please?"))),
 tip=("I'd like or I'll have?", "I'd like と I'll have", "Both are natural orders. “I'd like” is gently polite; “I'll have” sounds confident once you have decided.", "どちらも自然な注文です。「I'd like」はやわらかく丁寧で、「I'll have」は決めた後のはっきりした言い方です。", ("Gently polite", "やわらかく丁寧", "I'd like the chicken, please.", "チキンをお願いします。"), ("Decision made", "注文を決めた", "I'll have the chicken, please.", "チキンにします。")),
),
23: dict(
 meanings=(("Use a container or piece word to count food and drink.", "容器や単位の語を使って食べ物や飲み物を数えるときに使います。"), ("Use this to ask the needed amount of a non-count noun.", "直接数えない名詞の必要量をたずねるときに使います。")),
 writes=(("Order a real amount of one food or drink.", "食べ物か飲み物を一つ選び、実際の量で注文しましょう。"), ("Ask how much of one thing you need.", "必要なものを一つ選び、どのくらい必要かたずねましょう。")),
 choices=(
  (("コーヒーを{t}2杯{/t}お願いします。", "Two ", "cups", "cup", " of coffee, please."), ("水を{t}2本{/t}お願いします。", "Two ", "bottles", "bottle", " of water, please."), ("ケーキを{t}2切れ{/t}お願いします。", "Two ", "pieces", "piece", " of cake, please."), ("ご飯を{t}2杯{/t}お願いします。", "Two ", "bowls", "bowl", " of rice, please.")),
  (("ご飯は{t}どのくらい{/t}必要ですか？", "How ", "much", "many", " rice do we need?"), ("水は{t}どのくらい{/t}必要ですか？", "How ", "much", "many", " water do we need?"), ("コーヒーは{t}どのくらい{/t}必要ですか？", "How ", "much", "many", " coffee do we need?"), ("時間は{t}どのくらい{/t}必要ですか？", "How ", "much", "many", " time do we need?")),
 ),
 rules=(("Count the container, then add of", "容器を数えて of を加える", "数 + 容器<b>-s</b> + <b>of</b> + 品物", "Count by container", "容器で数える", ("two <b>cups of</b> coffee", "two <b>bottles of</b> water")), ("Use How much with a non-count noun", "直接数えない名詞には How much", "<b>How much</b> + 名詞 + do we need?", "Ask the amount", "量をたずねる", ("<b>How much</b> rice do we need?", "<b>How much</b> water do we need?"))),
 tip=("Could we get...?", "Could we get ...?", "In a shared order, “Could we get...?” is a natural, softer way to ask the server.", "みんなの注文では「Could we get ...?」が自然で、やわらかい頼み方です。", ("Short order", "短い注文", "Two cups of coffee, please.", "コーヒーを2杯お願いします。"), ("Shared polite request", "みんなで丁寧に頼む", "Could we get two cups of coffee?", "コーヒーを2杯いただけますか？")),
),
24: dict(
 meanings=(("Use this when you need the same words repeated.", "同じ言葉をもう一度聞きたいときに使います。"), ("Use this when you need the speaker to change how they speak.", "相手に話し方を変えてほしいときに使います。")),
 writes=(("Ask for one detail to be repeated.", "聞き取れなかった情報を一つ、もう一度頼みましょう。"), ("Ask the speaker to change how they are speaking.", "相手に必要な話し方の変化を頼みましょう。")),
 choices=(
  (("すみません、それを{t}もう一度{/t}言ってもらえますか？", "Sorry, can you say that ", "again", "yet", "?"), ("すみません、名前を{t}もう一度{/t}言ってもらえますか？", "Sorry, can you say your name ", "again", "yet", "?"), ("すみません、最後の部分を{t}もう一度{/t}言ってもらえますか？", "Sorry, can you say the last part ", "again", "yet", "?"), ("すみません、shelf を{t}もう一度{/t}言ってもらえますか？", "Sorry, can you say 'shelf' ", "again", "yet", "?")),
  (("もう少し{t}ゆっくり{/t}話してもらえますか？", "Can you speak more ", "slowly", "slow", "?"), ("もう少し{t}はっきり{/t}話してもらえますか？", "Can you speak more ", "clearly", "clear", "?"), ("もう少し{t}大きな声で{/t}話してもらえますか？", "Can you speak a little ", "louder", "loud", "?"), ("もう少し{t}ゆっくり{/t}話してもらえますか？", "Can you speak more ", "slowly", "slow", ", please?")),
 ),
 rules=(("Put again at the end", "最後に again", "Sorry, + can you say + 内容 + <b>again</b>?", "Ask for repetition", "繰り返しを頼む", ("Can you say that <b>again</b>?", "Can you say your name <b>again</b>?")), ("Name the change after speak", "speak の後ろに必要な変化", "Can you speak + more / a little + 話し方?", "Change how they speak", "話し方を変えてもらう", ("Can you speak more <b>slowly</b>?", "Can you speak a little <b>louder</b>?"))),
 tip=("Sorry? or a full request?", "Sorry? と文での頼み方", "A rising “Sorry?” is a quick casual request. Use the full sentence when you want to be especially clear.", "語尾を上げた「Sorry?」は短くカジュアルです。特にはっきり頼みたいなら文全体を使います。", ("Quick and casual", "短くカジュアル", "Sorry?", "もう一度お願いします。"), ("Clear request", "はっきり頼む", "Sorry, can you say that again?", "すみません、もう一度言ってもらえますか？")),
),
}

# Live production cannot use one generic ask-back sequence: questions, answers,
# permission, ordering and repair create different turn logic. Each tuple is
# (kind, side, speaker, English or scaffold, Japanese or task).
LIVE_SCENES = {
13: (("text", "other", "Tutor", "Do you drink coffee?", "コーヒーを飲みますか？"), ("input", "me", "Me", "Yes, I do. ___. / No, I don't. ___.", "自分の本当の答え"), ("text", "me", "Me", "How about you?", "あなたはどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Yes, I do. ___ / No, I don't. ___", "先生の答え")),
14: (("text", "other", "Tutor", "Do you drive to work?", "車で通勤しますか？"), ("input", "me", "Me", "I don't ___. I ___ instead.", "自分の本当の習慣"), ("text", "me", "Me", "How about you?", "あなたはどうですか？"), ("input", "other", "Tutor", "Tutor's answer: I don't ___. I ___ instead.", "先生の答え")),
15: (("text", "other", "Tutor", "Tell me about someone you know.", "知っている人について教えてください。"), ("input", "me", "Me", "She / He ___.", "知っている人の本当の情報"), ("text", "other", "Tutor", "What would you like to ask about that person?", "その人について何を聞きたいですか？"), ("input", "me", "Me", "Does she / he ___?", "続けて聞きたい質問"), ("input", "other", "Tutor", "Tutor's answer", "先生の答え")),
16: (("text", "other", "Tutor", "Ask me about my routine.", "私の日課についてたずねてください。"), ("input", "me", "Me", "What time do you ___?", "聞きたい時刻"), ("input", "other", "Tutor", "Tutor's answer", "先生の答え"), ("input", "me", "Me", "Where do you usually ___?", "聞きたい場所"), ("input", "other", "Tutor", "Tutor's answer", "先生の答え")),
17: (("text", "other", "Tutor", "How often do you exercise?", "どのくらい運動しますか？"), ("input", "me", "Me", "About ___ times a ___.", "自分の本当の頻度"), ("text", "me", "Me", "How about you?", "あなたはどうですか？"), ("input", "other", "Tutor", "Tutor's answer: About ___ times a ___.", "先生の答え")),
18: (("text", "other", "Tutor", "Can you drive?", "運転できますか？"), ("input", "me", "Me", "I can ___, but I can't ___.", "自分のできること"), ("text", "me", "Me", "How about you?", "あなたはどうですか？"), ("input", "other", "Tutor", "Tutor's answer: I can ___, but I can't ___.", "先生の答え")),
19: (("text", "other", "Tutor", "Ask me the price of something here.", "ここにある物の値段を聞いてください。"), ("input", "me", "Me", "How much is ___?", "値段を知りたい物"), ("input", "other", "Tutor", "Tutor's answer: It's ___ dollars.", "先生の値段"), ("input", "me", "Me", "Is that ___ or ___?", "聞こえた数字を確認"), ("input", "other", "Tutor", "Tutor's answer: confirmation", "先生の確認")),
21: (("text", "other", "Tutor", "Ask permission to do something here.", "ここで何かをする許可を求めてください。"), ("input", "me", "Me", "Can I ___?", "ここでしたいこと"), ("input", "other", "Tutor", "Tutor's answer: Sure, you can. / Sorry, not here.", "先生の答え")),
22: (("text", "other", "Tutor", "Are you ready to order?", "ご注文はお決まりですか？"), ("input", "me", "Me", "I'd like ___, please.", "自分の注文"), ("text", "other", "Tutor", "Anything else?", "ほかにもありますか？"), ("input", "me", "Me", "Can I have ___, please?", "追加で頼む物"), ("text", "other", "Tutor", "Of course.", "かしこまりました。")),
23: (("text", "other", "Tutor", "What should we order?", "何を注文しましょうか？"), ("input", "me", "Me", "Two ___ of ___, please.", "注文する本当の量"), ("input", "me", "Me", "How much ___ do we need?", "必要な量をたずねる"), ("input", "other", "Tutor", "Tutor's answer", "先生の答え")),
24: (("text", "other", "Tutor", "The next train leaves from platform thirteen.", "次の電車は13番ホームから出ます。"), ("input", "me", "Me", "Sorry, can you say ___ again?", "聞き取れなかった部分"), ("text", "other", "Tutor", "Platform thirteen.", "13番ホームです。"), ("input", "me", "Me", "Can you speak more ___?", "必要な話し方"), ("text", "other", "Tutor", "Of course.", "もちろんです。")),
}


def esc(s): return html.escape(s, quote=True)
def strip_marks(s): return re.sub(r"\{/?t\}", "", s)
def marks(s, cls="ending"):
    return esc(s).replace("{t}", f'<span class="{cls}">').replace("{/t}", "</span>")

def set_vocab(head, number):
    # The canonical CORE-20 shell has its own recycled provenance. Generated
    # CORE 12-24 decks must explicitly own all four categories so that pilot
    # metadata cannot leak into them when the pilot is corrected.
    values = dict(zip(("new", "assumed", "receptive"), VOCAB[number]))
    values["recycled"] = ""
    for category, value in values.items():
        head=re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',rf'\g<1>{value}\2',head,count=1)
    return head


def set_proofread_status(head, status):
    marker = '<meta name="podo:vocabulary-status" content="reviewed">'
    proofread = f'<meta name="podo:proofread-status" content="{status}">'
    if marker not in head:
        raise ValueError("canonical shell has no reviewed vocabulary marker")
    return head.replace(marker, marker + "\n  " + proofread, 1)

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
    hero_en, hero_jp, _ = pattern[0]
    examples = "".join(
        f'<div><span class="korean">{marks(en)}</span>'
        f'<span class="translation">{marks(jp)}</span></div>'
        for en, jp, _ in pattern[1:3]
    )
    body = (
        '<p class="section-subtitle pattern-meaning">'
        '<span class="meaning-kicker">Meaning &amp; use <small>意味・使い方</small></span>'
        f'<span class="ko">{esc(meaning[0])}</span>'
        f'<span class="ja">{esc(meaning[1])}</span></p>'
        '<div class="sent-hero">'
        f'<span class="korean">{marks(hero_en)}</span>'
        f'<span class="translation">{marks(hero_jp)}</span></div>'
        f'<div class="sent-more">{examples}</div>'
    )
    return section(pid, "Today's pattern", "今日のパターン", body)


def rule_example(pattern):
    """Show a complete English example in the wrapping sentence component."""
    en, jp, _ = pattern[0]
    return (
        '<div class="model-list"><div class="model-line">'
        f'<span class="korean">{marks(en)}</span>'
        f'<span class="translation">{marks(jp)}</span>'
        '</div></div>'
    )


def read(pid, pattern):
    lines="".join(f'<div class="model-line"><span class="korean">{marks(en)}</span><span class="translation">{marks(jp)}</span></div>' for en,jp,_ in pattern)
    return section(pid,"Read the sentences","文を読もう",'<p class="section-subtitle"><span class="ko">Read the four sentences.</span><span class="ja">4つの文を読んでみましょう。</span></p><div class="model-list">'+lines+'</div>')


def reorder(pid, pattern):
    blocks=[]
    for i,(en,jp,chunks) in enumerate(pattern):
        choices="".join(f'<span class="choice" data-item-id="{pid}-{i}-{j}">{esc(c)}</span>' for j,c in enumerate(chunks.split("|")[::-1]))
        blocks.append(f'<div class="task-block"><div class="answer-box small"><span class="answer-label">{esc(strip_marks(jp))}</span><span class="answer-space build-zone" data-sync-id="{pid}-{i}" data-sync-kind="order" data-a="{esc(strip_marks(en))}"></span></div>{choices}</div>')
    return section(pid,"Build the sentence","文を組み立てよう",'<p class="section-subtitle"><span class="ko">Put the four meaning chunks in order.</span><span class="ja">4つの意味のまとまりを順番に並べましょう。</span></p>'+"".join(blocks))


BOUND_REORDER_CHIPS = {"a", "an", "the", "er"}


def validate_reorder_pattern(pattern):
    """Refuse mechanically padded chips before any HTML is written."""
    counts = {len(row[2].split("|")) for row in pattern}
    if len(counts) != 1 or not counts.issubset({3, 4}):
        raise ValueError(f"reorder needs one honest 3- or 4-chip shape, got {counts}")
    for _, _, chunk_source in pattern:
        for raw in chunk_source.split("|"):
            chip = raw.strip()
            word = chip.strip(".,?!").casefold()
            if not chip or re.fullmatch(r"[^A-Za-z0-9]+", chip):
                raise ValueError(f"punctuation-only reorder chip: {chip!r}")
            if word in BOUND_REORDER_CHIPS:
                raise ValueError(f"bound-word reorder chip: {chip!r}")


def lesson_reorder(d, part):
    """Omit a reorder when the frame has no honest three-unit build."""
    if part in d.get("omit_reorder", ()):
        return ""
    pattern = d[f"p{part}"]
    validate_reorder_pattern(pattern)
    count = len(pattern[0][2].split("|"))
    en = "three" if count == 3 else "four"
    ja = "3つ" if count == 3 else "4つ"
    page = reorder(f"p{part}-reorder", pattern)
    if count == 3:
        page = page.replace(
            f'data-page-id="p{part}-reorder"',
            f'data-page-id="p{part}-reorder" data-chunk-review="meaningful"',
            1,
        )
    return page.replace("Put the four meaning chunks in order.", f"Put the {en} meaning chunks in order.").replace("4つの意味のまとまり", f"{ja}の意味のまとまり")


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


def rule_page(pid, title, title_ja, script, script_ja, formula, heading, heading_ja, examples):
    example_html = "".join(f"<span>{example}</span>" for example in examples)
    return section(
        pid,
        title,
        title_ja,
        '<p class="section-subtitle">'
        f'<span class="ko">{esc(script)}</span><span class="ja">{esc(script_ja)}</span></p>'
        '<div class="batchim ending-rule"><div class="bt-box">'
        f'<span class="bt-eq"><span class="bt-out">{formula}</span></span>'
        f'<span class="bt-head">{esc(heading)}<small>{esc(heading_ja)}</small></span>'
        f'<span class="bt-ex">{example_html}</span>'
        '</div></div>',
    )


def choose_words(pid, title, title_ja, script, script_ja, rows):
    rendered = []
    for index, (japanese, prefix, correct, distractor, suffix) in enumerate(rows):
        options = [("correct", correct, True), ("other", distractor, False)]
        if index % 2:
            options.reverse()
        option_html = '<span class="sep">/</span>'.join(
            f'<span class="opt" data-sync-option="{kind}"'
            f'{" data-correct" if is_correct else ""}>{esc(text)}</span>'
            for kind, text, is_correct in options
        )
        rendered.append(
            '<div class="word-choice-card">'
            f'<span class="translation">{marks(japanese)}</span>'
            f'<span class="word-choice-sentence">{esc(prefix)}'
            f'<span class="choose-row word-choice" data-sync-id="{pid}-{index}" '
            f'data-sync-kind="selection" data-sync-state="chosen">{option_html}</span>'
            f'{esc(suffix)}</span></div>'
        )
    return section(
        pid,
        title,
        title_ja,
        '<p class="section-subtitle">'
        f'<span class="ko">{esc(script)}</span><span class="ja">{esc(script_ja)}</span></p>'
        f'<div class="word-choice-list">{"".join(rendered)}</div>',
    )


def live_avatar(name):
    return (
        '<span class="who"><span class="avatar icon">'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" '
        'd="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2.5c-4.7 0-8.5 2.6-8.5 5.8V22h17v-1.7c0-3.2-3.8-5.8-8.5-5.8Z"/></svg>'
        f'</span><span class="who-name">{esc(name)}</span></span>'
    )


def core12_pages(d):
    p1_meaning = (
        "Use this to say the exact time your workday begins.",
        "仕事を始める正確な時刻を伝えるときに使います。",
    )
    p2_meaning = (
        "Use this to say what normally happens at about a certain time.",
        "ふだん何をだいたい何時ごろするかを伝えるときに使います。",
    )

    goal = '''    <div class="transition-page" data-page-id="lesson-goal" data-act="Talking about routines">
      <span class="transition-kicker">GOAL</span>
      <h2 class="transition-title">I start work at nine <span class="title-ja">(9時に仕事を始めます)</span></h2>
      <p class="section-subtitle"><span class="ko">Say when your normal workday starts and finishes.</span><span class="ja">ふだんの仕事が何時に始まり、何時ごろ終わるかを話しましょう。</span></p>
      <div class="known lines">
        <div class="known-row"><span class="k">I start work at nine.</span><span class="j">9時に仕事を始めます。</span></div>
        <div class="known-row"><span class="k">I usually finish work around six.</span><span class="j">ふだん6時ごろ仕事を終えます。</span></div>
        <div class="known-row"><span class="k">How about you?</span><span class="j">あなたはどうですか？</span></div>
      </div>
    </div>
'''
    known = section(
        "words-you-know",
        "Words you already know",
        "もう知っている単語",
        '<p class="section-subtitle"><span class="ko">These words may look familiar. Let\'s say them in English.</span><span class="ja">見たことのある単語ですね。英語で言ってみましょう。</span></p>'
        '<div class="bridge">'
        '<div class="br-row"><span class="br-cn">スタート</span><span class="br-eq">→</span><span class="br-ko">start</span></div>'
        '<div class="br-row"><span class="br-cn">ワーク</span><span class="br-eq">→</span><span class="br-ko">work</span></div>'
        '<div class="br-row"><span class="br-cn">フィニッシュ</span><span class="br-eq">→</span><span class="br-ko">finish</span></div>'
        '</div>',
    )
    p1_intro = '''    <div class="transition-page" data-page-id="part1-intro" data-act="I start work at…">
      <span class="transition-kicker">PART 1</span>
      <h2 class="transition-title">I start work at ___.</h2>
      <p class="transition-copy">仕事を始める正確な時刻を言うパターンです。</p>
    </div>
'''
    p1_rule = rule_page(
        "p1-rule",
        "Use at with an exact time",
        "正確な時刻には at",
        'Keep "start work" together, and put "at" directly before the clock time.',
        '「start work」をひとまとまりにして、時計の時刻のすぐ前に「at」を置きます。',
        'I + <b>start work</b> + <b>at</b> + 時刻',
        "Exact clock time",
        "ぴったりの時刻",
        ("I <b>start work at</b> nine.", "I <b>start work at</b> ten."),
    )
    p1_choose = choose_words(
        "p1-choose",
        "Choose the exact time",
        "正しい時刻を選ぼう",
        "Read the Japanese, then choose the matching time.",
        "日本語を読んで、合う時刻を選びましょう。",
        (
            ("{t}8時{/t}に仕事を始めます。", "I start work at ", "eight", "ten", "."),
            ("{t}9時{/t}に仕事を始めます。", "I start work at ", "nine", "eleven", "."),
            ("{t}10時{/t}に仕事を始めます。", "I start work at ", "ten", "eight", "."),
            ("{t}11時{/t}に仕事を始めます。", "I start work at ", "eleven", "nine", "."),
        ),
    )
    p1_write = section(
        "p1-write",
        "Your real start time",
        "自分の始業時刻",
        '<p class="section-subtitle"><span class="ko">What time do you start work?</span><span class="ja">何時に仕事を始めますか？</span></p>'
        '<div class="task-block"><div class="answer-box tall">'
        '<span class="answer-label">I start work at ___.<span class="task">自分の時刻で</span></span>'
        '<span class="answer-space as-input"><textarea class="free-input" data-sync-id="p1-write" rows="2" spellcheck="false" maxlength="2000"></textarea></span>'
        '</div></div>',
    )

    p2_intro = '''    <div class="transition-page" data-page-id="part2-intro" data-act="I usually… around…">
      <span class="transition-kicker">PART 2</span>
      <h2 class="transition-title">I usually ___ around ___.</h2>
      <p class="transition-copy">ふだんすることと、だいたいの時刻を言うパターンです。</p>
    </div>
'''
    p2_rule = rule_page(
        "p2-rule",
        "Put each word in its place",
        "usually と around の位置",
        'Put "usually" before the action and "around" before the approximate time.',
        '「usually」は動作の前に、「around」はだいたいの時刻の前に置きます。',
        'I + <b>usually</b> + 動作 + <b>around</b> + 時刻',
        "Usual action and approximate time",
        "ふだんの動作＋だいたいの時刻",
        (
            "I <b>usually</b> finish work <b>around</b> six.",
            "I <b>usually</b> eat lunch <b>around</b> twelve.",
        ),
    )
    p2_choose = choose_words(
        "p2-choose",
        "Choose the natural word order",
        "自然な語順を選ぼう",
        'Choose the natural order for "usually" and the action.',
        '「usually」と動作の自然な順番を選びましょう。',
        (
            ("{t}ふだん{/t}6時ごろ仕事を終えます。", "I ", "usually finish", "finish usually", " work around six."),
            ("{t}ふだん{/t}12時ごろ昼食をとります。", "I ", "usually eat", "eat usually", " lunch around twelve."),
            ("{t}ふだん{/t}7時ごろ夕食をとります。", "I ", "usually have", "have usually", " dinner around seven."),
            ("{t}ふだん{/t}9時ごろ仕事を始めます。", "I ", "usually start", "start usually", " work around nine."),
        ),
    )
    p2_write = section(
        "p2-write",
        "Your real finish time",
        "自分の終業時刻",
        '<p class="section-subtitle"><span class="ko">When do you usually finish work?</span><span class="ja">ふだん何時ごろ仕事を終えますか？</span></p>'
        '<div class="task-block"><div class="answer-box tall">'
        '<span class="answer-label">I usually finish work around ___.<span class="task">自分の時刻で</span></span>'
        '<span class="answer-space as-input"><textarea class="free-input" data-sync-id="p2-write" rows="2" spellcheck="false" maxlength="2000"></textarea></span>'
        '</div></div>',
    )

    p1_en, p1_jp, _ = d["p1"][0]
    p2_en, p2_jp, _ = d["p2"][0]
    model_dialogue = "".join(
        (
            turn("other", OTHER, "Coworker", "What time do you start work?", "何時に仕事を始めますか？"),
            turn("me", ME, "Me", marks(p1_en), marks(p1_jp)),
            turn("other", OTHER, "Coworker", "And when do you usually finish work?", "では、ふだん何時ごろ仕事を終えますか？"),
            turn("me", ME, "Me", marks(p2_en), marks(p2_jp)),
            turn("other", OTHER, "Coworker", "That is a long day.", "長い一日ですね。"),
            turn("me", ME, "Me", "Yes, it is.", "はい、そうですね。"),
        )
    )
    complete_dialogue = "".join(
        (
            turn("other", OTHER, "Coworker", "What time do you start work?", "何時に仕事を始めますか？"),
            answer_turn(ME, "Me", inputs(p1_en, "dlg-p1"), marks(p1_jp, "target")),
            turn("other", OTHER, "Coworker", "And when do you usually finish work?", "では、ふだん何時ごろ仕事を終えますか？"),
            answer_turn(ME, "Me", inputs(p2_en, "dlg-p2"), marks(p2_jp, "target")),
            turn("other", OTHER, "Coworker", "That is a long day.", "長い一日ですね。"),
            turn("me", ME, "Me", "Yes, it is.", "はい、そうですね。"),
        )
    )
    p3_model = section(
        "p3-model",
        "Read the conversation",
        "会話を読もう",
        '<p class="section-subtitle"><span class="ko">Read your lines while I read the coworker.</span><span class="ja">自分のセリフを読み、私は同僚のパートを読みます。</span></p>'
        f'<div class="dialogue">{model_dialogue}</div>',
    )
    p3_complete = section(
        "p3-complete",
        "Complete the conversation",
        "会話をうめよう",
        '<p class="section-subtitle"><span class="ko">Say the missing pattern words.</span><span class="ja">空いているパターンの部分を言ってみましょう。</span></p>'
        '<div class="tutor-note">Write each target exactly as the learner says it.</div>'
        f'<div class="dialogue">{complete_dialogue}</div>',
    )
    tutor_avatar = live_avatar("Tutor")
    me_avatar = live_avatar("Me")
    p3_freetalk = section(
        "p3-freetalk",
        "Free talk",
        "フリートーク",
        '<p class="section-subtitle"><span class="ko">Tell me your times, then ask me too.</span><span class="ja">自分の時刻を答えて、それから私にも聞いてください。</span></p>'
        '<div class="dialogue">'
        f'<div class="turn other">{tutor_avatar}<div class="bubble"><span class="korean">What time do you start work?</span><span class="translation">何時に仕事を始めますか？</span></div></div>'
        f'<div class="turn me">{me_avatar}<div class="bubble me"><div class="answer-box small"><span class="answer-label">I start work at ___.<span class="task">自分の時刻で</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-start" rows="2" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>'
        f'<div class="turn other">{tutor_avatar}<div class="bubble"><span class="korean">When do you usually finish work?</span><span class="translation">ふだん何時ごろ仕事を終えますか？</span></div></div>'
        f'<div class="turn me">{me_avatar}<div class="bubble me"><div class="answer-box small"><span class="answer-label">I usually finish work around ___.<span class="task">自分の時刻で</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-finish" rows="2" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>'
        f'<div class="turn me">{me_avatar}<div class="bubble me"><span class="korean">How about you?</span><span class="translation">あなたはどうですか？</span></div></div>'
        f'<div class="turn other">{tutor_avatar}<div class="bubble"><div class="answer-box small"><span class="answer-label">Tutor\'s answer<span class="task">先生の答え</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-tutor" rows="2" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>'
        '</div>',
    )
    wild = section(
        "in-the-wild",
        "Out in the world",
        "実際の場面で",
        '<p class="section-subtitle"><span class="ko">Compare your Friday schedule with a coworker.</span><span class="ja">同僚と金曜日の予定を比べましょう。</span></p>'
        '<div class="dialogue">'
        + turn("other", OTHER, "Coworker", "What time do you start on Fridays?", "金曜日は何時に仕事を始めますか？")
        + answer_turn(ME, "Me", '<textarea class="free-input phrase-input" data-sync-id="wild-start" data-answer="I start work at" rows="1" autocomplete="off" spellcheck="false"></textarea> eight.', '8時に<span class="target">仕事を始めます</span>。')
        + turn("other", OTHER, "Coworker", "And when do you usually have dinner?", "では、ふだん何時ごろ夕食をとりますか？")
        + answer_turn(ME, "Me", '<textarea class="free-input phrase-input" data-sync-id="wild-usually" data-answer="I usually" rows="1" autocomplete="off" spellcheck="false"></textarea> have dinner <textarea class="free-input phrase-input" data-sync-id="wild-around" data-answer="around" rows="1" autocomplete="off" spellcheck="false"></textarea> seven.', '<span class="target">ふだん</span>7時<span class="target">ごろ</span>夕食をとります。')
        + turn("other", OTHER, "Coworker", "That sounds like a full day.", "忙しい一日になりそうですね。")
        + turn("me", ME, "Me", "Yes, every Friday.", "はい、毎週金曜日です。")
        + '</div>',
    )
    native_tip = section(
        "native-tip",
        "Around nine or nine-ish?",
        "around nine と nine-ish",
        '<p class="section-subtitle"><span class="ko">Both mean about nine. Use "nine-ish" in casual conversation.</span><span class="ja">どちらも9時ごろという意味です。「nine-ish」はカジュアルな会話で使います。</span></p>'
        '<div class="tutor-note">Read both versions so the learner can hear the casual tone of -ish.</div>'
        '<div class="nuance-compare">'
        '<div class="nuance-choice"><span class="nuance-when"><b>Any situation</b><small>どんな場面でも</small></span><span class="korean">I usually start <span class="ending">around nine</span>.</span><span class="translation">ふだん9時ごろ始めます。</span></div>'
        '<div class="nuance-or"><span>Pick by situation <small>場面で選ぶ</small></span></div>'
        '<div class="nuance-choice"><span class="nuance-when"><b>Casual conversation</b><small>カジュアルな会話で</small></span><span class="korean">I usually start <span class="ending">at nine-ish</span>.</span><span class="translation">ふだん9時くらいに始めます。</span></div>'
        '</div>',
    )

    return [
        goal,
        known,
        p1_intro,
        teach("p1-teach", d["p1"], p1_meaning),
        read("p1-read", d["p1"]),
        p1_rule,
        p1_choose,
        '    <!-- Reorder criterion: subject · action · time preposition · clock time. -->\n' + lesson_reorder(d, 1),
        fill("p1-fill", d["p1"]),
        translate("p1-translate", d["p1"]),
        p1_write,
        p2_intro,
        teach("p2-teach", d["p2"], p2_meaning),
        read("p2-read", d["p2"]),
        p2_rule,
        p2_choose,
        '    <!-- Reorder criterion: subject plus frequency · action · approximate-time marker · clock time. -->\n' + lesson_reorder(d, 2),
        fill("p2-fill", d["p2"]),
        translate("p2-translate", d["p2"]),
        p2_write,
        '''    <div class="transition-page" data-page-id="part3-intro" data-act="Talking about a workday"><span class="transition-kicker">PART 3</span><h2 class="transition-title">Your workday</h2><p class="transition-copy">二つのパターンを使って、一日の仕事の時間を話しましょう。</p></div>\n''',
        p3_model,
        p3_complete,
        p3_freetalk,
        wild,
        native_tip,
    ]


def avatar(src,name): return f'<span class="who"><img class="avatar" src="{src}" alt=""><span class="who-name">{name}</span></span>'
def turn(kind,src,name,en,jp): return f'<div class="turn {kind}">{avatar(src,name)}<div class="bubble {"me" if kind=="me" else ""}"><span class="korean">{en}</span><span class="translation">{jp}</span></div></div>'
def answer_turn(src,name,en,jp):
    return f'<div class="turn me">{avatar(src,name)}<div class="bubble me"><div class="answer-box"><span class="answer-label">{jp}</span><span class="answer-fill"><span class="korean">{en}</span></span></div></div></div>'
def partner_ja(line): return PARTNER_JA[line]


def dialogue(number, d, variant="model", complete=False, prefix="dlg"):
    role,p1_row,p2_row,first,follow,close,last=DIALOGUES[number][variant]
    a1,j1,_=d["p1"][p1_row]; a2,j2,_=d["p2"][p2_row]
    mine1=inputs(a1,f"{prefix}-p1") if complete else marks(a1)
    mine2=inputs(a2,f"{prefix}-p2") if complete else marks(a2)
    jp1=marks(j1,"target") if complete else marks(j1)
    jp2=marks(j2,"target") if complete else marks(j2)
    mine_turn1 = answer_turn(ME,"Me",mine1,jp1) if complete else turn("me",ME,"Me",mine1,jp1)
    mine_turn2 = answer_turn(ME,"Me",mine2,jp2) if complete else turn("me",ME,"Me",mine2,jp2)
    return ''.join([
      turn("other",OTHER,role,esc(first[0]),esc(first[1])),
      mine_turn1,
      turn("other",OTHER,role,esc(follow[0]),esc(follow[1])),
      mine_turn2,
      turn("other",OTHER,role,esc(close[0]),esc(close[1])),
      turn("me",ME,"Me",esc(last[0]),esc(last[1]))])


def canonical_pages(number, d):
    """Render one fully authored Core specification through the canonical arc."""
    spec = CANONICAL_SPECS[number]
    p1_en, p1_ja, _ = d["p1"][0]
    p2_en, p2_ja, _ = d["p2"][0]

    goal = f'''    <div class="transition-page" data-page-id="lesson-goal" data-act="Everyday English">
      <span class="transition-kicker">GOAL</span>
      <h2 class="transition-title">{esc(d["title"])} <span class="title-ja">({esc(d["ja"])})</span></h2>
      <p class="section-subtitle"><span class="ko">{esc(d["goal"][0])}</span><span class="ja">{esc(d["goal"][1])}</span></p>
      <div class="known lines"><div class="known-row"><span class="k">{marks(p1_en)}</span><span class="j">{marks(p1_ja)}</span></div><div class="known-row"><span class="k">{marks(p2_en)}</span><span class="j">{marks(p2_ja)}</span></div><div class="known-row"><span class="k">How about you?</span><span class="j">あなたはどうですか？</span></div></div>
    </div>\n'''

    def intro(part):
        model = strip_marks(d[f"p{part}"][0][0])
        return f'''    <div class="transition-page" data-page-id="part{part}-intro" data-act="Pattern {part}"><span class="transition-kicker">PART {part}</span><h2 class="transition-title">{esc(model)}</h2><p class="transition-copy">{esc(spec["meanings"][part - 1][1])}</p></div>\n'''

    def visual_rule(part):
        title, title_ja, formula, heading, heading_ja, examples = spec["rules"][part - 1]
        return rule_page(
            f"p{part}-rule", title, title_ja,
            d["rules"][part - 1][0], d["rules"][part - 1][1],
            formula, heading, heading_ja, examples,
        )

    def choose(part):
        return choose_words(
            f"p{part}-choose", "Choose the pattern", "パターンを選ぼう",
            "Choose only the words that complete the highlighted meaning.",
            "強調された意味に合う語だけを選びましょう。",
            spec["choices"][part - 1],
        )

    def write_page(part):
        model = strip_marks(d[f"p{part}"][0][0])
        prompt_en, prompt_ja = spec["writes"][part - 1]
        return section(
            f"p{part}-write", "Make it yours", "自分の文にしよう",
            f'<p class="section-subtitle"><span class="ko">{esc(prompt_en)}</span><span class="ja">{esc(prompt_ja)}</span></p>'
            '<div class="task-block"><div class="answer-box tall">'
            f'<span class="answer-label">{esc(model)}<span class="task">自分の情報に変えて</span></span>'
            f'<span class="answer-space as-input"><textarea class="free-input" data-sync-id="p{part}-write" rows="2" spellcheck="false" maxlength="2000"></textarea></span>'
            '</div></div>',
        )

    model_dialogue = dialogue(number, d)
    complete_dialogue = dialogue(number, d, complete=True)
    live_turns = []
    for index, (kind, side, speaker, english, japanese) in enumerate(LIVE_SCENES[number]):
        avatar_html = live_avatar(speaker)
        bubble_class = "bubble me" if side == "me" else "bubble"
        if kind == "text":
            live_turns.append(
                f'<div class="turn {side}">{avatar_html}<div class="{bubble_class}"><span class="korean">{esc(english)}</span><span class="translation">{esc(japanese)}</span></div></div>'
            )
        else:
            live_turns.append(
                f'<div class="turn {side}">{avatar_html}<div class="{bubble_class}"><div class="answer-box tall"><span class="answer-label">{esc(english)}<span class="task">{esc(japanese)}</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>'
            )
    live = '<div class="dialogue">' + ''.join(live_turns) + '</div>'

    tip_title, tip_ja, tip_script, tip_script_ja, left, right = spec["tip"]
    native_tip = section(
        "native-tip", tip_title, tip_ja,
        f'<p class="section-subtitle"><span class="ko">{esc(tip_script)}</span><span class="ja">{esc(tip_script_ja)}</span></p>'
        '<div class="nuance-compare">'
        f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(left[0])}</b><small>{esc(left[1])}</small></span><span class="korean">{esc(left[2])}</span><span class="translation">{esc(left[3])}</span></div>'
        '<div class="nuance-or"><span>Pick by meaning <small>意味で選ぶ</small></span></div>'
        f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(right[0])}</b><small>{esc(right[1])}</small></span><span class="korean">{esc(right[2])}</span><span class="translation">{esc(right[3])}</span></div>'
        '</div>',
    )

    return [
        goal, known_page(number), intro(1), teach("p1-teach", d["p1"], spec["meanings"][0]),
        read("p1-read", d["p1"]), visual_rule(1), choose(1), lesson_reorder(d, 1),
        fill("p1-fill", d["p1"]), translate("p1-translate", d["p1"]), write_page(1),
        intro(2), teach("p2-teach", d["p2"], spec["meanings"][1]), read("p2-read", d["p2"]),
        visual_rule(2), choose(2), lesson_reorder(d, 2), fill("p2-fill", d["p2"]),
        translate("p2-translate", d["p2"]), write_page(2),
        '    <div class="transition-page" data-page-id="part3-intro" data-act="Conversation"><span class="transition-kicker">PART 3</span><h2 class="transition-title">Use it in a conversation <span class="title-ja">(会話で使おう)</span></h2><p class="transition-copy">二つのパターンをつないで、相手と情報をやり取りしましょう。</p></div>\n',
        section("p3-model", "Read the conversation", "会話を読もう", '<p class="section-subtitle"><span class="ko">Read your lines while I read the other role.</span><span class="ja">自分のセリフを読み、私は相手役を読みます。</span></p><div class="dialogue">' + model_dialogue + '</div>'),
        section("p3-complete", "Complete the conversation", "会話を完成しよう", '<p class="section-subtitle"><span class="ko">Say only the missing pattern words.</span><span class="ja">空いているパターンの部分だけを言いましょう。</span></p><div class="tutor-note">Write each target exactly as the learner says it.</div><div class="dialogue">' + complete_dialogue + '</div>'),
        section("p3-freetalk", "Your real answer", "自分の答え", f'<p class="section-subtitle"><span class="ko">{esc(d["prompt"][0])}</span><span class="ja">{esc(d["prompt"][1])}</span></p>' + live),
        section("in-the-wild", "A new situation", "別の場面", '<p class="section-subtitle"><span class="ko">Use the same two patterns in a different conversation.</span><span class="ja">同じ二つのパターンを別の会話で使いましょう。</span></p><div class="dialogue">' + dialogue(number, d, "wild", True, "wild") + '</div>'),
        native_tip,
    ]


def build(number,d):
    source=PILOT.read_text(encoding="utf-8"); head,foot=new_lesson.split_shell(source)
    slug=f'{number:02d}-{d["slug"]}'
    head=new_lesson.retarget(head,review_id=f"CORE-{number}",lesson_id=slug,level="A1",title=d["title"],title_ko=d["ko"],title_ja=d["ja"],version="2026-08-19")
    head=set_vocab(head.replace('content="todo"','content="reviewed"'),number)
    head=set_proofread_status(head, "complete")
    pages = core12_pages(d) if number == 12 else canonical_pages(number, d)
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
