#!/usr/bin/env python3
"""Generate the approved missing CTX 2-6 travel-course lessons."""

from __future__ import annotations

import argparse
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_lesson
import generate_core_course_batch as core

ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/2-contextual-english"
COURSE = "ctx-travel-arrivals-transport"
PILOT = TRACK / "courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html"
ME, OTHER = core.ME, core.OTHER


def rows(*items): return items


LESSONS = {
2: dict(slug="answer-immigration-questions-clearly",title="Answer immigration questions clearly",ko="입국 심사 질문에 분명하게 답하기",ja="入国審査の質問にはっきり答える",role="Officer",role_ja="入国審査官",scene="Passport control",scene_ja="入国審査",goal=("Give short, consistent information about your visit and accommodation.","訪問の目的と滞在先を短く一貫して伝えましょう。"),
 preserve_approved_understand=True,
 meanings=(("Use this to say why you are visiting.", "訪問の目的を伝えるときに使います。"), ("Use this to say where you are staying.", "滞在先を伝えるときに使います。")),
 writes=(("Now use “I’m here for ___” to give the real or imaginary purpose of your trip.", "では、「I’m here for ___」を使って、実際または想像の旅行の目的を伝えましょう。"), ("Now use “I’m staying at ___” to say where you would stay.", "では、「I’m staying at ___」を使って、どこに泊まるか伝えましょう。")),
 closing=("Two weeks.", "2週間です。"), live=("Answer my question, then ask me too.", "私の質問に答えて、それから私にも聞いてください。"),
 live_exchange=(("text", "other", "Tutor", "Which immigration question would be hardest for you to answer quickly, and why?", "入国審査で、すぐ答えるのがいちばん難しそうな質問は何ですか？なぜですか？"), ("input", "me", "Me", "Student's answer", "自分の答え"), ("text", "me", "Me", "Which question would be hardest for you?", "先生にはどの質問がいちばん難しそうですか？"), ("input", "other", "Tutor", "Tutor's answer", "先生の答え")),
 p1=rows(("{t}I'm here for{/t} a two-week holiday.","{t}2週間の休暇で来ました{/t}。","I'm here for|a two-week holiday."),("{t}I'm here for{/t} work.","{t}仕事で来ました{/t}。","I'm here for|work."),("{t}I'm here for{/t} a conference.","{t}会議で来ました{/t}。","I'm here for|a conference."),("{t}I'm here for{/t} a wedding.","{t}結婚式で来ました{/t}。","I'm here for|a wedding.")),
 p2=rows(("{t}I'm staying at{/t} the Central Hotel.","セントラルホテルに{t}泊まります{/t}。","I'm staying|at|the Central|Hotel."),("{t}I'm staying at{/t} an airport hotel.","空港のホテルに{t}泊まります{/t}。","I'm staying|at|an airport|hotel."),("{t}I'm staying at{/t} my friend's place.","友人の家に{t}泊まります{/t}。","I'm staying|at|my friend's|place."),("{t}I'm staying at{/t} an apartment downtown.","中心街のアパートに{t}泊まります{/t}。","I'm staying|at|an apartment|downtown.")),
    translate_hints=(
      (("休暇", "holiday"), ("仕事", "work"), ("会議", "conference"), ("結婚式", "wedding")),
      (("セントラルホテル", "Central Hotel"), ("空港ホテル", "airport hotel"), ("友人の家", "friend's place"), ("中心街のアパート", "apartment downtown")),
    ),
 rules=(("Say I'm here for, then add the purpose of your trip.", "I'm here for のあとに旅行の目的を続けます。"),("Say I'm staying at, then add your hotel or other accommodation.", "I'm staying at のあとにホテルなどの滞在先を続けます。")),
 rule_visuals=(("Add the purpose of your trip", "旅行の目的を続ける", "Keep “I'm here for” together, then add why you are visiting.", "「I'm here for」をひとまとまりにして、訪問の目的を続けます。", "<b>I'm here for</b> + 旅行の目的", "Purpose of your trip", "旅行の目的", ("<b>I'm here for</b> work.", "<b>I'm here for</b> a holiday.")), ("Add where you're staying", "滞在先を続ける", "Keep “I'm staying at” together, then add your hotel or other accommodation.", "「I'm staying at」をひとまとまりにして、ホテルなどの滞在先を続けます。", "<b>I'm staying at</b> + 滞在先", "Your accommodation", "滞在先", ("<b>I'm staying at</b> a hotel.", "<b>I'm staying at</b> my friend's place."))),
 omit_reorder=(1, 2), expressions=(), receptive=(("What's the purpose of your visit?","Purpose of the trip","訪問の目的"),("How long will you stay?","Length of the stay","滞在期間"),("Where are you staying?","Accommodation","滞在先"),("Anything to declare?","Goods for customs","申告する品物")),
 partner=("What's the purpose of your visit?","And where are you staying?","How long will you stay?","Thank you. Enjoy your trip."), transfer=("Travel insurance call","What brings you to the city?","And where are you staying?","Thanks. I've updated your travel details."), transfer_role="Travel insurance agent", transfer_role_ja="旅行保険の担当者",
 tip=("For work or on business?", "for work と on business", "Both are natural. “I’m here on business” is a common answer at immigration.", "どちらも自然です。入国審査では「I’m here on business」もよく使います。", ("Everyday", "日常的", "I’m here for work.", "仕事で来ました。"), ("At immigration", "入国審査で", "I’m here on business.", "出張で来ました。"))),
3: dict(slug="confirm-a-number-you-did-not-hear",title="Confirm a number you did not hear",ko="못 들은 숫자 확인하기",ja="聞き取れなかった数字を確認する",role="Staff",scene="Airport information desk",scene_ja="空港の案内所",goal=("Repair a time or number before you act on it.","行動する前に、時刻や数字の聞き間違いを直しましょう。"),
 role_ja="案内係", meanings=(("Use this to ask someone to repeat one detail.", "一つの情報をもう一度言ってもらう表現です。"), ("Use this to confirm which of two similar numbers you heard.", "似た二つの数字のどちらかを確認する表現です。")),
 writes=(("Now use “Sorry, could you say ___ again?” to ask for one detail again.", "「Sorry, could you say ___ again?」を使って、もう一度聞きたい情報を頼みましょう。"), ("Now use “Did you say ___ or ___?” to check two possible numbers.", "「Did you say ___ or ___?」を使って、聞こえた二つの数字を確認しましょう。")),
 translate_hints=((('出発時刻','departure time'),('ゲート番号','gate number'),('ホーム番号','platform'),('バス番号','bus number')),(('2時40分','two-forty'),('15番ゲート','gate fifteen'),('13番ホーム','platform thirteen'),('14番バス','bus fourteen'))),
 live=("Which travel number is easiest for you to mishear, and why?", "旅行中の数字で、いちばん聞き間違えやすいものと、その理由は何ですか？"), live_exchange=(("text","other","Tutor","Which travel number is easiest for you to mishear, and why?","旅行中の数字で、いちばん聞き間違えやすいものと、その理由は何ですか？"),("input","me","Me","Student's answer","自分の答え"),("text","me","Me","Which number is hardest for you to catch?","先生はどの数字がいちばん聞き取りにくいですか？"),("input","other","Tutor","Tutor's answer","先生の答え")), transfer_role="Station clerk", transfer_role_ja="駅員",
 p1=rows(("{t}Sorry, could you say{/t} the departure time {t}again{/t}?","{t}すみません{/t}、出発時刻を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the departure time|again?"),("{t}Sorry, could you say{/t} the gate number {t}again{/t}?","{t}すみません{/t}、ゲート番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the gate number|again?"),("{t}Sorry, could you say{/t} the platform {t}again{/t}?","{t}すみません{/t}、ホーム番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the platform|again?"),("{t}Sorry, could you say{/t} the bus number {t}again{/t}?","{t}すみません{/t}、バス番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the bus number|again?")),
 p2=rows(("{t}Did you say{/t} two-forty {t}or{/t} two-fourteen?","{t}2時40分ですか{/t}、{t}それとも{/t}2時14分ですか？","Did you say|two-forty|or|two-fourteen?"),("{t}Did you say{/t} gate fifteen {t}or{/t} gate fifty?","{t}15番ゲートですか{/t}、{t}それとも{/t}50番ゲートですか？","Did you say|gate fifteen|or|gate fifty?"),("{t}Did you say{/t} platform thirteen {t}or{/t} platform thirty?","{t}13番ホームですか{/t}、{t}それとも{/t}30番ホームですか？","Did you say|platform thirteen|or|platform thirty?"),("{t}Did you say{/t} bus fourteen {t}or{/t} bus forty?","{t}14番バスですか{/t}、{t}それとも{/t}40番バスですか？","Did you say|bus fourteen|or|bus forty?")),
 rules=(("Put the detail you missed before again: Could you say the gate number again?", "聞き取れなかった内容を again の前に置き、Could you say the gate number again? の形にします。"),("Put the two possible numbers on either side of or.", "二つの候補を or の両側に置きます。")), expressions=(("just to confirm","念のため確認ですが"),("four-zero","4、0")), receptive=(("It leaves at two-forty.","Departure time","出発時刻"),("Go to gate fifteen.","Gate number","ゲート番号"),("Use platform thirteen.","Platform number","ホーム番号"),("Take bus fourteen.","Bus number","バス番号")),
 partner=("The airport bus leaves at two-forty.","It leaves from stop fifteen.","Yes, stop one-five.","Now you have the right time and stop."), transfer=("Train station","The train leaves at thirteen-forty.","It departs from platform fourteen.","Exactly: one-four.")),
4: dict(slug="choose-the-right-transport-ticket",title="Choose the right transport ticket",ko="알맞은 교통권 고르기",ja="目的に合う交通チケットを選ぶ",role="Clerk",scene="Station ticket counter",scene_ja="駅の切符売り場",goal=("Compare ticket options and select the one that fits your trip.","切符を比べて、移動に合うものを選びましょう。"),
 role_ja="窓口係", meanings=(("Use this to ask whether another kind of ticket is available.", "別の種類の切符があるか尋ねる表現です。"), ("Use this to compare two choices.", "二つの選択肢を比べる表現です。")),
 writes=(("Now use “Is there a/an ___ option?” to ask for an alternative.", "「Is there a/an ___ option?」を使って、別の選択肢を尋ねましょう。"), ("Now use “Which one is ___?” to compare two tickets.", "「Which one is ___?」を使って、二つの切符を比べましょう。")),
 translate_hints=((('安い','cheaper'),('早い','earlier'),('速い','faster'),('直行','direct')),(('速い','faster'),('安い','cheaper'),('簡単','easier'),('3回の乗車','three trips'))),
 live=("When you buy a ticket, what matters most: price, speed, or flexibility?", "切符を買うとき、料金・速さ・自由度のどれをいちばん重視しますか？"), live_exchange=(("text","other","Tutor","When you buy a ticket, what matters most: price, speed, or flexibility?","切符を買うとき、料金・速さ・自由度のどれをいちばん重視しますか？"),("input","me","Me","Student's answer","自分の答え"),("text","me","Me","What matters most to you when you buy a ticket?","先生は切符を買うとき何をいちばん重視しますか？"),("input","other","Tutor","Tutor's answer","先生の答え")), transfer_role="Rail clerk", transfer_role_ja="鉄道の窓口係",
 p1=rows(("{t}Is there a{/t} cheaper {t}option{/t}?","もっと安い{t}選択肢は{/t}{t}ありますか{/t}？","Is there a|cheaper|option?"),("{t}Is there an{/t} earlier {t}option{/t}?","もっと早い{t}選択肢は{/t}{t}ありますか{/t}？","Is there an|earlier|option?"),("{t}Is there a{/t} faster {t}option{/t}?","もっと速い{t}選択肢は{/t}{t}ありますか{/t}？","Is there a|faster|option?"),("{t}Is there a{/t} direct {t}option{/t}?","直行の{t}選択肢は{/t}{t}ありますか{/t}？","Is there a|direct|option?")),
 p2=rows(("{t}Which one is{/t} faster?","{t}どちらのほうが{/t}速いですか？","Which one is|faster?"),("{t}Which one is{/t} cheaper?","{t}どちらのほうが{/t}安いですか？","Which one is|cheaper?"),("{t}Which one is{/t} easier?","{t}どちらのほうが{/t}簡単ですか？","Which one is|easier?"),("{t}Which one is{/t} better for three trips?","3回乗るなら{t}どちらのほうがよいですか{/t}？","Which one is|better for three trips?")),
 omit_reorder=(2,),
 rules=(("Use a before a consonant sound and an before a vowel sound: a cheaper option, an earlier option.", "子音の音の前は a、母音の音の前は an を使い、a cheaper option、an earlier option の形にします。"),("Use Which one is before the comparison: faster, cheaper, or easier.", "比較する語の前に Which one is を置き、faster、cheaper、easier と続けます。")), expressions=(("one-way","片道"),("day pass","一日乗車券")), receptive=(("The day pass covers unlimited trips.","Unlimited local travel","市内の乗り放題"),("The express is twenty minutes faster.","Shorter journey","短い移動時間"),("The single ticket is one-way.","One journey","1回の乗車"),("You need a seat reservation.","Reserved seat required","座席指定が必要")),
 partner=("Where are you travelling today?","The day pass is cheaper if you make three trips.","The express is faster by twenty minutes.","The day pass sounds right for you."), transfer=("Airport rail desk","The local train costs less.","The express arrives much earlier.","All right. One express ticket.")),
5: dict(slug="ask-for-directions-and-confirm-the-route",title="Ask for directions and confirm the route",ko="길을 묻고 경로 확인하기",ja="道をたずねて行き方を確認する",role="Local",scene="Outside a station",scene_ja="駅の外",goal=("Get directions and confirm the step that prevents a wrong turn.","道を聞き、間違えないための大事な手順を確認しましょう。"),
 role_ja="地元の人", meanings=(("Use this to ask how to reach a place.", "目的地への行き方を尋ねる表現です。"), ("Use this to check the first step in a route.", "道順の最初の手順を確認する表現です。")),
 writes=(("Now use “How do I get to ___?” to ask for directions.", "「How do I get to ___?」を使って、行きたい場所への道を尋ねましょう。"), ("Now use “Do I ___ first?” to confirm the first step.", "「Do I ___ first?」を使って、最初の手順を確認しましょう。")),
 translate_hints=((('美術館','museum'),('ホテル','hotel'),('空港','airport'),('バス停','bus stop')),(('北口','north exit'),('道を渡る','cross the road'),('左へ曲がる','turn left'),('バスに乗る','take the bus'))),
 live=("When you get lost, do you ask someone or check a map first?", "道に迷ったら、先に人に聞きますか、それとも地図を確認しますか？"), live_exchange=(("text","other","Tutor","When you get lost, do you ask someone or check a map first? Why?","道に迷ったら、先に人に聞きますか、それとも地図を確認しますか？なぜですか？"),("input","me","Me","Student's answer","自分の答え"),("text","me","Me","What do you do first when you get lost?","先生は道に迷ったら最初に何をしますか？"),("input","other","Tutor","Tutor's answer","先生の答え")), transfer_role="Local", transfer_role_ja="地元の人",
 p1=rows(("{t}How do I get to{/t} the museum?","美術館には{t}どう行けばいいですか{/t}？","How do I|get to|the museum?"),("{t}How do I get to{/t} the hotel?","ホテルには{t}どう行けばいいですか{/t}？","How do I|get to|the hotel?"),("{t}How do I get to{/t} the airport?","空港には{t}どう行けばいいですか{/t}？","How do I|get to|the airport?"),("{t}How do I get to{/t} the bus stop?","バス停には{t}どう行けばいいですか{/t}？","How do I|get to|the bus stop?")),
 p2=rows(("{t}Do I{/t} take the north exit {t}first{/t}?","{t}最初に{/t}北口を{t}出ますか{/t}？","Do I|take|the north exit|first?"),("{t}Do I{/t} cross the road {t}first{/t}?","{t}最初に{/t}道を{t}渡りますか{/t}？","Do I|cross|the road|first?"),("{t}Do I{/t} turn left {t}first{/t}?","{t}最初に{/t}左へ{t}曲がりますか{/t}？","Do I|turn|left|first?"),("{t}Do I{/t} take the bus {t}first{/t}?","{t}最初に{/t}バスに{t}乗りますか{/t}？","Do I|take|the bus|first?")),
 rules=(("Keep get to together, then add the complete destination.", "get to をひとまとまりにし、そのあとに行き先を続けます。"),("Put first at the end to confirm the first step of the route.", "道順の最初の手順を確認するときは first を文末に置きます。")), expressions=(("across from","〜の向かいに"),("you can't miss it","すぐ分かります")), receptive=(("Take the north exit.","Use the north exit","北口を使う"),("Cross the road at the light.","Cross at the traffic light","信号で渡る"),("Take the number eight bus.","Use bus number eight","8番バスに乗る"),("It is across from the library.","Opposite the library","図書館の向かい")),
 partner=("Can I help you find something?","Take the north exit and then the number eight bus.","Exactly. The bus stop is across the road.","You can't miss the museum."), transfer=("City center","Walk past the bank and turn right.","Yes, turn right after the bank.","The hotel is on your left.")),
6: dict(slug="arrange-transport-to-your-accommodation",title="Arrange transport to your accommodation",ko="숙소까지 교통편 마련하기",ja="宿泊先までの移動を手配する",role="Staff",scene="Airport taxi desk",scene_ja="空港のタクシー受付",goal=("State your destination and confirm the time and cost before agreeing.","行き先を伝え、決める前に時間と料金を確認しましょう。"),
 role_ja="タクシー受付係", meanings=(("Use this to ask a driver to take you or your group somewhere.", "自分や同行者を目的地まで乗せてもらう表現です。"), ("Use this to ask for an approximate price.", "おおよその料金を尋ねる表現です。")),
 writes=(("Now use “Could you take me/us to ___?” to give a destination.", "「Could you take me/us to ___?」を使って、行き先を伝えましょう。"), ("Now use “About how much will ___ cost?” to ask the price.", "「About how much will ___ cost?」を使って、おおよその料金を尋ねましょう。")),
 translate_hints=((('セントラルホテル','Central Hotel'),('この住所','this address'),('駅','station'),('第2ターミナル','Terminal Two')),(('料金','it'),('移動','ride'),('タクシー','taxi'),('それ','that'))),
 live=("What do you always check before getting into a taxi in another country?", "海外でタクシーに乗る前に、必ず確認したいことは何ですか？"), live_exchange=(("text","other","Tutor","What do you always check before getting into a taxi in another country?","海外でタクシーに乗る前に、必ず確認したいことは何ですか？"),("input","me","Me","Student's answer","自分の答え"),("text","me","Me","What do you check before a taxi ride?","先生はタクシーに乗る前に何を確認しますか？"),("input","other","Tutor","Tutor's answer","先生の答え")), transfer_role="Hotel receptionist", transfer_role_ja="ホテルの受付係",
 p1=rows(("{t}Could you take us to{/t} the Central Hotel?","セントラルホテルまで{t}乗せていただけますか{/t}？","Could you|take us to|the Central Hotel?"),("{t}Could you take us to{/t} this address?","この住所まで{t}乗せていただけますか{/t}？","Could you|take us to|this address?"),("{t}Could you take me to{/t} the station?","駅まで{t}乗せていただけますか{/t}？","Could you|take me to|the station?"),("{t}Could you take me to{/t} Terminal Two?","第2ターミナルまで{t}乗せていただけますか{/t}？","Could you|take me to|Terminal Two?")),
 p2=rows(("{t}About how much will{/t} it {t}cost{/t}?","{t}料金はだいたいいくら{/t}{t}ですか{/t}？","About how much|will it|cost?"),("{t}About how much will{/t} the ride {t}cost{/t}?","移動の{t}料金はだいたいいくら{/t}{t}ですか{/t}？","About how much|will the ride|cost?"),("{t}About how much will{/t} a taxi {t}cost{/t}?","タクシーの{t}料金はだいたいいくら{/t}{t}ですか{/t}？","About how much|will a taxi|cost?"),("{t}About how much will{/t} that {t}cost{/t}?","それは{t}だいたいいくら{/t}{t}かかりますか{/t}？","About how much|will that|cost?")),
 rules=(("Use take me or take us before to plus the destination.", "行き先の前に take me または take us と to を置きます。"),("Put the thing being priced between will and cost.", "料金をたずねるものを will と cost の間に置きます。")), expressions=(("fixed fare","定額運賃"),("depending on traffic","交通状況によって")), receptive=(("It takes about forty minutes.","Estimated travel time","所要時間の目安"),("The fare is fixed.","Price will not change","料金は変わらない"),("The meter starts at five euros.","Starting meter price","メーターの初乗り"),("Traffic is heavy today.","Possible delay","遅れる可能性")),
 partner=("Where do you need to go?","That is about forty minutes from here.","Between forty and fifty euros, depending on traffic.","A car will be ready in five minutes."), transfer=("Hotel front desk","Where would you like to go?","It takes about twenty minutes.","The fixed fare is thirty euros.")),
}

PARTNER_JA = {
"What's the purpose of your visit?":"訪問の目的は何ですか？","And where are you staying?":"滞在先はどこですか？","How long will you stay?":"どのくらい滞在しますか？","Thank you. Enjoy your trip.":"ありがとうございます。よい旅を。",
"The airport bus leaves at two-forty.":"空港バスは2時40分に出ます。","It leaves from stop fifteen.":"15番乗り場から出ます。","Yes, stop one-five.":"はい、乗り場は1、5です。","Now you have the right time and stop.":"これで正しい時刻と乗り場が分かりましたね。",
"Where are you travelling today?":"今日はどこまで行きますか？","The day pass is cheaper if you make three trips.":"3回乗るなら一日乗車券のほうが安いです。","The express is faster by twenty minutes.":"急行のほうが20分速いです。","The day pass sounds right for you.":"一日乗車券が合いそうですね。",
"Can I help you find something?":"どこかお探しですか？","Take the north exit and then the number eight bus.":"北口を出て、8番バスに乗ってください。","Exactly. The bus stop is across the road.":"その通りです。バス停は道の向かいです。","You can't miss the museum.":"美術館はすぐ分かります。",
"Where do you need to go?":"どこまで行きますか？","That is about forty minutes from here.":"ここから約40分です。","Between forty and fifty euros, depending on traffic.":"交通状況によりますが、40〜50ユーロです。","A car will be ready in five minutes.":"5分で車をご用意します。",
"Do you have a reservation?":"ご予約はありますか？","How many nights are you staying?":"何泊のご予定ですか？","Perfect. Here is your room key.":"承知しました。こちらがルームキーです。",
"The train leaves at thirteen-forty.":"電車は13時40分に出ます。","It departs from platform fourteen.":"14番ホームから出発します。","Exactly: one-four.":"その通りです。1、4です。",
"The local train costs less.":"普通列車のほうが安いです。","The express arrives much earlier.":"急行のほうがかなり早く着きます。","All right. One express ticket.":"分かりました。急行券を1枚ですね。",
"Walk past the bank and turn right.":"銀行を通り過ぎて右に曲がってください。","Yes, turn right after the bank.":"はい、銀行の先を右です。","The hotel is on your left.":"ホテルは左手にあります。",
"Where would you like to go?":"どちらまで行きますか？","It takes about twenty minutes.":"約20分かかります。","The fixed fare is thirty euros.":"定額で30ユーロです。",
"What brings you to the city?":"この街には何のために来ましたか？","Thanks. I've updated your travel details.":"ありがとうございます。旅行情報を更新しました。",
}

DISTRACTORS = {
"Purpose of the trip":("Length of the trip","旅行の期間"),"Length of the stay":("Reason for the trip","旅行の目的"),"Accommodation":("Departure city","出発した都市"),"Goods for customs":("Carry-on size","機内持ち込み荷物の大きさ"),
"Departure time":("Arrival time","到着時刻"),"Gate number":("Seat number","座席番号"),"Platform number":("Train number","列車番号"),"Bus number":("Bus fare","バス運賃"),
"Unlimited local travel":("One express journey","急行の片道1回"),"Shorter journey":("Lower ticket price","安い切符"),"One journey":("Unlimited travel","乗り放題"),"Reserved seat required":("Any seat is available","自由に座れる"),
"Use the north exit":("Use the south exit","南口を使う"),"Cross at the traffic light":("Stay on this side","こちら側にいる"),"Use bus number eight":("Walk all the way","ずっと歩く"),"Opposite the library":("Behind the library","図書館の裏"),
"Estimated travel time":("Waiting time","待ち時間"),"Price will not change":("Price depends on the meter","料金はメーターで変わる"),"Starting meter price":("Total fixed price","定額の合計"),"Possible delay":("Guaranteed arrival time","到着時刻の保証"),
}

VOCAB = {
2:("conference|会議","hotel|ホテル; holiday|休暇; work|仕事; wedding|結婚式; Central Hotel|セントラルホテル; airport hotel|空港ホテル; friend's place|友人の家; apartment downtown|中心街のアパート","purpose|目的; accommodation|滞在先; return ticket|帰りの航空券; declare|申告する"),
3:("departure|出発; platform|ホーム; confirm|確認する","time|時刻; gate|ゲート; bus|バス; departure time|出発時刻; gate number|ゲート番号; bus number|バス番号; two-forty|2時40分; gate fifteen|15番ゲート; platform thirteen|13番ホーム; bus fourteen|14番バス","information desk|案内所"),
4:("one-way|片道; day pass|一日乗車券; express|急行","ticket|切符; trip|乗車; faster|より速い; cheaper|より安い; earlier|より早い; direct|直行; easier|より簡単; three trips|3回の乗車","reservation|予約"),
5:("north exit|北口; across from|〜の向かいに","museum|美術館; hotel|ホテル; airport|空港; bus stop|バス停; road|道; cross the road|道を渡る; turn left|左へ曲がる; take the bus|バスに乗る","you can't miss it|すぐ分かる; route|経路"),
6:("fixed fare|定額運賃; address|住所","hotel|ホテル; taxi|タクシー; cost|料金; Central Hotel|セントラルホテル; this address|この住所; station|駅; Terminal Two|第2ターミナル; it|それ; ride|移動; that|それ; traffic|交通状況","meter|メーター"),
}


def esc(s): return html.escape(s,quote=True)
def avatar(src,name): return f'<span class="who"><img class="avatar" src="{src}" alt=""><span class="who-name">{esc(name)}</span></span>'
def turn(kind,src,name,en,jp): return f'<div class="turn {kind}">{avatar(src,name)}<div class="bubble {"me" if kind=="me" else ""}"><span class="korean">{en}</span><span class="translation">{jp}</span></div></div>'
def partner_ja(line): return PARTNER_JA[line]

def set_vocab(head,n):
    import re
    for category,value in zip(("new","assumed","receptive"),VOCAB[n]):
        head=re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',rf'\g<1>{value}\2',head,count=1)
    return head


def conversation(d,complete=False,prefix="scene",transfer=False):
    partner=d["transfer"] if transfer else d["partner"]
    if transfer:
        _,one,two,three=partner
        role=d.get("transfer_role", partner[0])
        final=None
    else:
        role=d["role"]
        one,two,three,final=partner
    patterns = (d["p1"], d["p2"])
    p1,j1,_=patterns[0][1 if transfer else 0]; p2,j2,_=patterns[1][1 if transfer else 0]
    mine1=core.inputs(p1,f"{prefix}-p1") if complete else core.marks(p1)
    mine2=core.inputs(p2,f"{prefix}-p2") if complete else core.marks(p2)
    jp1=core.marks(j1,"target") if complete else core.marks(j1)
    jp2=core.marks(j2,"target") if complete else core.marks(j2)
    mine_turn1 = core.answer_turn(ME,"Me",mine1,jp1) if complete else turn("me",ME,"Me",mine1,jp1)
    mine_turn2 = core.answer_turn(ME,"Me",mine2,jp2) if complete else turn("me",ME,"Me",mine2,jp2)
    closing_en, closing_ja = d.get("closing", ("Thank you.", "ありがとうございます。"))
    if transfer:
        closing_en, closing_ja = "Thank you.", "ありがとうございます。"
    turns=[turn("other",OTHER,role,esc(one),esc(partner_ja(one))),mine_turn1,turn("other",OTHER,role,esc(two),esc(partner_ja(two))),mine_turn2,turn("other",OTHER,role,esc(three),esc(partner_ja(three))),turn("me",ME,"Me",esc(closing_en),esc(closing_ja))]
    if final:
        turns.append(turn("other",OTHER,role,esc(final),esc(partner_ja(final))))
    return ''.join(turns)


def understand(d):
    blocks=[]
    for i,(line,sense,ja) in enumerate(d["receptive"]):
        wrong_en,wrong_ja=DISTRACTORS[sense]
        if d.get("preserve_approved_understand"):
            blocks.append(f'<div class="choose-row sentence receptive-choice" data-sync-id="understand-{i}" data-sync-kind="selection"><span class="translation">{esc(line)}</span><span class="choose-sentence"><span class="opt" data-sync-option="yes" data-correct><span class="choice-en">{esc(sense)}</span><small>{esc(ja)}</small></span><span class="opt" data-sync-option="no"><span class="choice-en">{esc(wrong_en)}</span><small>{esc(wrong_ja)}</small></span></span></div>')
            continue
        options = [
            f'<span class="opt" data-sync-option="correct" data-correct><span class="choice-en">{esc(sense)}</span><small>{esc(ja)}</small></span>',
            f'<span class="opt" data-sync-option="other"><span class="choice-en">{esc(wrong_en)}</span><small>{esc(wrong_ja)}</small></span>',
        ]
        if i % 2:
            options.reverse()
        blocks.append(f'<div class="choose-row sentence receptive-choice" data-sync-id="understand-{i}" data-sync-kind="selection"><span class="translation">{esc(line)}</span><span class="choose-sentence">{"".join(options)}</span></div>')
    if d.get("preserve_approved_understand"):
        return core.section("understand","Understand","聞いてわかろう",'<p class="section-subtitle"><span class="ko">I will read each staff line. Choose what it means.</span><span class="ja">係員のセリフを読みます。意味を選びましょう。</span></p><div class="tutor-note">Read each English staff line aloud.</div>'+''.join(blocks))
    role=d["role"].lower()
    role_ja=d.get("role_ja", "相手役")
    return core.section("understand","Understand","聞いてわかろう",f'<p class="section-subtitle"><span class="ko">I’ll read each {esc(role)} line. Choose what it means.</span><span class="ja">私が{esc(role_ja)}のセリフを読みます。意味を選んでください。</span></p>'+''.join(blocks))


def live_exchange(d):
    turns=[]
    for index,(kind,side,speaker,english,japanese) in enumerate(d.get("live_exchange", ())):
        avatar_html=core.live_avatar(speaker)
        bubble_class="bubble me" if side == "me" else "bubble"
        if kind == "text":
            turns.append(f'<div class="turn {side}">{avatar_html}<div class="{bubble_class}"><span class="korean">{esc(english)}</span><span class="translation">{esc(japanese)}</span></div></div>')
        else:
            turns.append(f'<div class="turn {side}">{avatar_html}<div class="{bubble_class}"><div class="answer-box tall"><span class="answer-label">{esc(english)}<span class="task">{esc(japanese)}</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>')
    return '<div class="dialogue">'+''.join(turns)+'</div>' if turns else ""


def build(n,d):
    source=PILOT.read_text(encoding="utf-8"); head,foot=new_lesson.split_shell(source); slug=f'{n:02d}-{d["slug"]}'
    head=set_vocab(new_lesson.retarget(head,review_id=f"CTX-{n}",lesson_id=slug,level="A2-B1",title=d["title"],title_ko=d["ko"],title_ja=d["ja"],version="2026-08-20").replace('content="todo"','content="reviewed"'),n)
    expr=''.join(f'<div class="model-line"><span class="korean">{esc(en)}</span><span class="translation">{esc(ja)}</span></div>' for en,ja in d["expressions"])
    meanings=d.get("meanings", (d["goal"], d["goal"]))
    writes=d.get("writes", (("Now, make your own sentence with the first pattern.", "では、一つ目のパターンを使って自分の文を作りましょう。"), ("Now, make your own sentence with the second pattern.", "では、二つ目のパターンを使って自分の文を作りましょう。")))
    role_ja=d.get("role_ja", "相手役")
    live=d.get("live", ("What would matter most to you in this situation, and why?", "この場面では、何をいちばん大切にしますか？なぜですか？"))
    transfer_role=d.get("transfer_role", d["transfer"][0])
    transfer_role_ja=d.get("transfer_role_ja", "相手役")
    scene_script=d.get("scene_script", (f"Let's role-play {d['scene'].lower()}. You're the traveller, and I'll be the {d['role'].lower()}.", f"{d['scene_ja']}のロールプレイをしましょう。あなたは旅行者、私は{role_ja}です。"))
    rule_visuals=d.get("rule_visuals")
    fill_rows=(d["p1"], d["p2"])
    for part, pattern in enumerate(fill_rows, start=1):
        core.validate_controlled_pattern(pattern, label=f"CTX-{n} p{part}")
    translate_hints=d.get("translate_hints", (None, None))
    p1_rule=(core.rule_page("p1-rule", *rule_visuals[0]) if rule_visuals else core.section("p1-rule","How it works","形を見よう",f'<p class="section-subtitle"><span class="ko">{esc(d["rules"][0][0])}</span><span class="ja">{esc(d["rules"][0][1])}</span></p>'+core.rule_example(d["p1"])))
    p2_rule=(core.rule_page("p2-rule", *rule_visuals[1]) if rule_visuals else core.section("p2-rule","How it works","形を見よう",f'<p class="section-subtitle"><span class="ko">{esc(d["rules"][1][0])}</span><span class="ja">{esc(d["rules"][1][1])}</span></p>'+core.rule_example(d["p2"])))
    live_dialogue=live_exchange(d)
    pages=[core.goal_page(title=d["title"], title_ja=d["ja"], can_do=d["goal"][0], can_do_ja=d["goal"][1], data_act="Travel task"),
      core.section("scene",esc(d["scene"]),esc(d["scene_ja"]),f'<p class="section-subtitle"><span class="ko">{esc(scene_script[0])}</span><span class="ja">{esc(scene_script[1])}</span></p><div class="tutor-note">Begin with the first {esc(d["role"])} line.</div><div class="dialogue">'+conversation(d)+'</div>'),
      understand(d)]
    if expr:
        pages.append(core.section("expressions","Useful expressions","使える表現",'<p class="section-subtitle"><span class="ko">Please read each expression aloud.</span><span class="ja">それぞれの表現を声に出して読んでください。</span></p><div class="model-list">'+expr+'</div>'))
    pages.extend([
      f'    <div class="transition-page" data-page-id="part1-intro" data-act="Move 1"><span class="transition-kicker">MOVE 1</span><h2 class="transition-title">{esc(core.strip_marks(d["p1"][0][0]))}</h2><p class="section-subtitle"><span class="ko">First, let\'s practice the first useful line from the scene.</span><span class="ja">まず、場面で使った一つ目の表現を練習しましょう。</span></p><div class="tutor-note">Introduce the first line, then move on.</div></div>\n',core.teach("p1-teach",d["p1"],meanings[0]),core.read("p1-read",d["p1"]),p1_rule,core.lesson_reorder(d,1),core.fill("p1-fill",fill_rows[0]),core.translate("p1-translate",d["p1"],hints=translate_hints[0],support_stage="supported" if translate_hints[0] is not None else None),core.section("p1-write","Make it yours","自分の文にしよう",f'<p class="section-subtitle"><span class="ko">{esc(writes[0][0])}</span><span class="ja">{esc(writes[0][1])}</span></p><div class="tutor-note">Let the learner answer aloud before you capture it. React first, then add only a useful correction.</div>'+core.feedback_compose("p1-open")),
      f'    <div class="transition-page" data-page-id="part2-intro" data-act="Move 2"><span class="transition-kicker">MOVE 2</span><h2 class="transition-title">{esc(core.strip_marks(d["p2"][0][0]))}</h2><p class="section-subtitle"><span class="ko">Next, let\'s practice the second useful line from the scene.</span><span class="ja">次に、場面で使った二つ目の表現を練習しましょう。</span></p><div class="tutor-note">Introduce the second line, then move on.</div></div>\n',core.teach("p2-teach",d["p2"],meanings[1]),core.read("p2-read",d["p2"]),p2_rule,core.lesson_reorder(d,2),core.fill("p2-fill",fill_rows[1]),core.translate("p2-translate",d["p2"],hints=translate_hints[1],support_stage="supported" if translate_hints[1] is not None else None),core.section("p2-write","Make it yours","自分の文にしよう",f'<p class="section-subtitle"><span class="ko">{esc(writes[1][0])}</span><span class="ja">{esc(writes[1][1])}</span></p><div class="tutor-note">Let the learner answer aloud before you capture it. React first, then add only a useful correction.</div>'+core.feedback_compose("p2-open")),
      '    <div class="transition-page" data-page-id="part3-intro" data-act="Complete the task"><span class="transition-kicker">PUT IT TOGETHER</span><h2 class="transition-title">Complete the task <span class="title-ja">(用事を完了しよう)</span></h2><p class="section-subtitle"><span class="ko">Now, let\'s use both lines in the complete scene.</span><span class="ja">では、二つの表現を使って場面を最後まで進めましょう。</span></p><div class="tutor-note">Introduce the roleplay, then move on.</div></div>\n',
      core.section("p3-model","Replay the scene","場面をもう一度",f'<p class="section-subtitle"><span class="ko">I\'ll be the {esc(d["role"].lower())}. Please read the Me lines aloud.</span><span class="ja">私は{esc(role_ja)}役をします。Me のセリフを声に出して読んでください。</span></p><div class="dialogue">'+conversation(d)+'</div>'),
      core.section("p3-complete","Complete the scene","場面を完成しよう",f'<p class="section-subtitle"><span class="ko">I’ll be the {esc(d["role"].lower())}. Say each complete line, including the missing words.</span><span class="ja">私は{esc(role_ja)}役をします。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。</span></p><div class="tutor-note">Type only the missing words exactly as the learner says them.</div><div class="dialogue">'+conversation(d,True,"complete")+'</div>'),
      core.section("p3-freetalk","Talk about the real situation","本当の場面について話そう",f'<p class="section-subtitle"><span class="ko">{esc(live[0])}</span><span class="ja">{esc(live[1])}</span></p><div class="tutor-note">React to the answer and follow the most interesting detail. Invite today\'s pattern only if it fits naturally.</div>'+(live_dialogue or core.feedback_compose("p3-real-answer")))])
    if "tip" in d:
        title,title_ja,script,script_ja,left,right=d["tip"]
        pages.append(core.section("native-tip",title,title_ja,f'<p class="section-subtitle"><span class="ko">{esc(script)}</span><span class="ja">{esc(script_ja)}</span></p><div class="nuance-compare"><div class="nuance-choice"><span class="nuance-when"><b>{esc(left[0])}</b><small>{esc(left[1])}</small></span><span class="korean">{esc(left[2])}</span><span class="translation">{esc(left[3])}</span></div><div class="nuance-or"><span>Pick by situation <small>場面で選ぶ</small></span></div><div class="nuance-choice"><span class="nuance-when"><b>{esc(right[0])}</b><small>{esc(right[1])}</small></span><span class="korean">{esc(right[2])}</span><span class="translation">{esc(right[3])}</span></div></div>'))
    pages.append(core.section("transfer-scene",esc(d["transfer"][0]),"別の場面へ",f'<p class="section-subtitle"><span class="ko">Let\'s role-play a different situation. I\'ll be the {esc(transfer_role.lower())}.</span><span class="ja">別の場面でロールプレイをしましょう。私は{esc(transfer_role_ja)}役です。</span></p><div class="dialogue">'+conversation(d,True,"transfer",True)+'</div>'))
    document=head+"\n".join(pages)+foot
    out=TRACK/"courses"/COURSE/"lessons"/slug/"lesson.html"; return out,new_lesson.redepth(document,out)


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh",action="store_true"); ap.add_argument("--lesson", type=int, choices=LESSONS); args=ap.parse_args()
    selected = LESSONS.items() if args.lesson is None else ((args.lesson, LESSONS[args.lesson]),)
    for n,d in selected:
        out,text=build(n,d)
        if out.exists() and not args.refresh: raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS) if args.lesson is None else 1} Contextual decks generated")
    return 0


if __name__=="__main__": raise SystemExit(main())
