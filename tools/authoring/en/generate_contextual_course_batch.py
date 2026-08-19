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
2: dict(slug="answer-immigration-questions-clearly",title="Answer immigration questions clearly",ko="입국 심사 질문에 분명하게 답하기",ja="入国審査の質問にはっきり答える",role="Officer",scene="Passport control",scene_ja="入国審査",goal=("Give short, consistent information about your visit and accommodation.","訪問の目的と滞在先を短く一貫して伝えましょう。"),
 p1=rows(("{t}I'm here for{/t} a two-week holiday.","{t}2週間の休暇で来ました{/t}。","I'm here for|a two-week holiday."),("{t}I'm here for{/t} work.","{t}仕事で来ました{/t}。","I'm here for|work."),("{t}I'm here for{/t} a conference.","{t}会議で来ました{/t}。","I'm here for|a conference."),("{t}I'm here for{/t} a wedding.","{t}結婚式で来ました{/t}。","I'm here for|a wedding.")),
 p2=rows(("{t}I'm staying at{/t} the Central Hotel.","セントラルホテルに{t}泊まります{/t}。","I'm staying|at|the Central|Hotel."),("{t}I'm staying at{/t} an airport hotel.","空港のホテルに{t}泊まります{/t}。","I'm staying|at|an airport|hotel."),("{t}I'm staying at{/t} my friend's place.","友人の家に{t}泊まります{/t}。","I'm staying|at|my friend's|place."),("{t}I'm staying at{/t} an apartment downtown.","中心街のアパートに{t}泊まります{/t}。","I'm staying|at|an apartment|downtown.")),
 rules=(("Keep I'm here for together, then add the purpose of the trip.", "I'm here for をひとまとまりにし、そのあとに旅行の目的を続けます。"),("Use I'm staying at before a hotel or other accommodation.", "ホテルなどの滞在先の前に I'm staying at を使います。")), omit_reorder=(1, 2), expressions=(("return ticket","帰りの航空券"),("travelling for work","仕事での渡航")), receptive=(("What's the purpose of your visit?","Purpose of the trip","訪問の目的"),("How long will you stay?","Length of the stay","滞在期間"),("Where are you staying?","Accommodation","滞在先"),("Anything to declare?","Goods for customs","申告する品物")),
 partner=("What's the purpose of your visit?","And where are you staying?","How long will you stay?","Thank you. Enjoy your trip."), transfer=("Hotel reception","Do you have a reservation?","How many nights are you staying?","Perfect. Here is your room key.")),
3: dict(slug="confirm-a-number-you-did-not-hear",title="Confirm a number you did not hear",ko="못 들은 숫자 확인하기",ja="聞き取れなかった数字を確認する",role="Staff",scene="Airport information desk",scene_ja="空港の案内所",goal=("Repair a time or number before you act on it.","行動する前に、時刻や数字の聞き間違いを直しましょう。"),
 p1=rows(("{t}Sorry, could you say{/t} the departure time {t}again{/t}?","すみません、出発時刻を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the departure time|again?"),("{t}Sorry, could you say{/t} the gate number {t}again{/t}?","すみません、ゲート番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the gate number|again?"),("{t}Sorry, could you say{/t} the platform {t}again{/t}?","すみません、ホーム番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the platform|again?"),("{t}Sorry, could you say{/t} the bus number {t}again{/t}?","すみません、バス番号を{t}もう一度言ってもらえますか{/t}？","Sorry,|could you say|the bus number|again?")),
 p2=rows(("{t}Did you say{/t} two-forty {t}or{/t} two-fourteen?","{t}2時40分ですか、それとも{/t}2時14分ですか？","Did you say|two-forty|or|two-fourteen?"),("{t}Did you say{/t} gate fifteen {t}or{/t} gate fifty?","{t}15番ゲートですか、それとも{/t}50番ゲートですか？","Did you say|gate fifteen|or|gate fifty?"),("{t}Did you say{/t} platform thirteen {t}or{/t} platform thirty?","{t}13番ホームですか、それとも{/t}30番ホームですか？","Did you say|platform thirteen|or|platform thirty?"),("{t}Did you say{/t} bus fourteen {t}or{/t} bus forty?","{t}14番バスですか、それとも{/t}40番バスですか？","Did you say|bus fourteen|or|bus forty?")),
 rules=(("Put the detail you missed before again: Could you say the gate number again?", "聞き取れなかった内容を again の前に置き、Could you say the gate number again? の形にします。"),("Put the two possible numbers on either side of or.", "二つの候補を or の両側に置きます。")), expressions=(("just to confirm","念のため確認ですが"),("four-zero","4、0")), receptive=(("It leaves at two-forty.","Departure time","出発時刻"),("Go to gate fifteen.","Gate number","ゲート番号"),("Use platform thirteen.","Platform number","ホーム番号"),("Take bus fourteen.","Bus number","バス番号")),
 partner=("The airport bus leaves at two-forty.","It leaves from stop fifteen.","Yes, stop one-five.","Now you have the right time and stop."), transfer=("Train station","The train leaves at thirteen-forty.","It departs from platform fourteen.","Exactly: one-four.")),
4: dict(slug="choose-the-right-transport-ticket",title="Choose the right transport ticket",ko="알맞은 교통권 고르기",ja="目的に合う交通チケットを選ぶ",role="Clerk",scene="Station ticket counter",scene_ja="駅の切符売り場",goal=("Compare ticket options and select the one that fits your trip.","切符を比べて、移動に合うものを選びましょう。"),
 p1=rows(("{t}Is there a{/t} cheaper {t}option{/t}?","もっと安い{t}選択肢はありますか{/t}？","Is there a|cheaper|option?"),("{t}Is there an{/t} earlier {t}option{/t}?","もっと早い{t}選択肢はありますか{/t}？","Is there an|earlier|option?"),("{t}Is there a{/t} faster {t}option{/t}?","もっと速い{t}選択肢はありますか{/t}？","Is there a|faster|option?"),("{t}Is there a{/t} direct {t}option{/t}?","直行の{t}選択肢はありますか{/t}？","Is there a|direct|option?")),
 p2=rows(("{t}Which one is{/t} faster?","{t}どちらのほうが{/t}速いですか？","Which one is|faster?"),("{t}Which one is{/t} cheaper?","{t}どちらのほうが{/t}安いですか？","Which one is|cheaper?"),("{t}Which one is{/t} easier?","{t}どちらのほうが{/t}簡単ですか？","Which one is|easier?"),("{t}Which one is{/t} better for three trips?","3回乗るなら{t}どちらのほうがよいですか{/t}？","Which one is|better for three trips?")),
 omit_reorder=(2,),
 rules=(("Use a before a consonant sound and an before a vowel sound: a cheaper option, an earlier option.", "子音の音の前は a、母音の音の前は an を使い、a cheaper option、an earlier option の形にします。"),("Use Which one is before the comparison: faster, cheaper, or easier.", "比較する語の前に Which one is を置き、faster、cheaper、easier と続けます。")), expressions=(("one-way","片道"),("day pass","一日乗車券")), receptive=(("The day pass covers unlimited trips.","Unlimited local travel","市内の乗り放題"),("The express is twenty minutes faster.","Shorter journey","短い移動時間"),("The single ticket is one-way.","One journey","1回の乗車"),("You need a seat reservation.","Reserved seat required","座席指定が必要")),
 partner=("Where are you travelling today?","The day pass is cheaper if you make three trips.","The express is faster by twenty minutes.","The day pass sounds right for you."), transfer=("Airport rail desk","The local train costs less.","The express arrives much earlier.","All right. One express ticket.")),
5: dict(slug="ask-for-directions-and-confirm-the-route",title="Ask for directions and confirm the route",ko="길을 묻고 경로 확인하기",ja="道をたずねて行き方を確認する",role="Local",scene="Outside a station",scene_ja="駅の外",goal=("Get directions and confirm the step that prevents a wrong turn.","道を聞き、間違えないための大事な手順を確認しましょう。"),
 p1=rows(("{t}How do I get to{/t} the museum?","美術館には{t}どう行けばいいですか{/t}？","How do I|get to|the museum?"),("{t}How do I get to{/t} the hotel?","ホテルには{t}どう行けばいいですか{/t}？","How do I|get to|the hotel?"),("{t}How do I get to{/t} the airport?","空港には{t}どう行けばいいですか{/t}？","How do I|get to|the airport?"),("{t}How do I get to{/t} the bus stop?","バス停には{t}どう行けばいいですか{/t}？","How do I|get to|the bus stop?")),
 p2=rows(("{t}Do I{/t} take the north exit {t}first{/t}?","{t}最初に{/t}北口を出ますか？","Do I|take|the north exit|first?"),("{t}Do I{/t} cross the road {t}first{/t}?","{t}最初に{/t}道を渡りますか？","Do I|cross|the road|first?"),("{t}Do I{/t} turn left {t}first{/t}?","{t}最初に{/t}左へ曲がりますか？","Do I|turn|left|first?"),("{t}Do I{/t} take the bus {t}first{/t}?","{t}最初に{/t}バスに乗りますか？","Do I|take|the bus|first?")),
 rules=(("Keep get to together, then add the complete destination.", "get to をひとまとまりにし、そのあとに行き先を続けます。"),("Put first at the end to confirm the first step of the route.", "道順の最初の手順を確認するときは first を文末に置きます。")), expressions=(("across from","〜の向かいに"),("you can't miss it","すぐ分かります")), receptive=(("Take the north exit.","Use the north exit","北口を使う"),("Cross the road at the light.","Cross at the traffic light","信号で渡る"),("Take the number eight bus.","Use bus number eight","8番バスに乗る"),("It is across from the library.","Opposite the library","図書館の向かい")),
 partner=("Can I help you find something?","Take the north exit and then the number eight bus.","Exactly. The bus stop is across the road.","You can't miss the museum."), transfer=("City center","Walk past the bank and turn right.","Yes, turn right after the bank.","The hotel is on your left.")),
6: dict(slug="arrange-transport-to-your-accommodation",title="Arrange transport to your accommodation",ko="숙소까지 교통편 마련하기",ja="宿泊先までの移動を手配する",role="Staff",scene="Airport taxi desk",scene_ja="空港のタクシー受付",goal=("State your destination and confirm the time and cost before agreeing.","行き先を伝え、決める前に時間と料金を確認しましょう。"),
 p1=rows(("{t}Could you take us to{/t} the Central Hotel?","セントラルホテルまで{t}乗せていただけますか{/t}？","Could you|take us to|the Central Hotel?"),("{t}Could you take us to{/t} this address?","この住所まで{t}乗せていただけますか{/t}？","Could you|take us to|this address?"),("{t}Could you take me to{/t} the station?","駅まで{t}乗せていただけますか{/t}？","Could you|take me to|the station?"),("{t}Could you take me to{/t} Terminal Two?","第2ターミナルまで{t}乗せていただけますか{/t}？","Could you|take me to|Terminal Two?")),
 p2=rows(("{t}About how much will{/t} it {t}cost{/t}?","{t}料金はだいたいいくらですか{/t}？","About how much|will it|cost?"),("{t}About how much will{/t} the ride {t}cost{/t}?","移動の{t}料金はだいたいいくらですか{/t}？","About how much|will the ride|cost?"),("{t}About how much will{/t} a taxi {t}cost{/t}?","タクシーの{t}料金はだいたいいくらですか{/t}？","About how much|will a taxi|cost?"),("{t}About how much will{/t} that {t}cost{/t}?","それは{t}だいたいいくらかかりますか{/t}？","About how much|will that|cost?")),
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
}

DISTRACTORS = {
"Purpose of the trip":("Length of the trip","旅行の期間"),"Length of the stay":("Reason for the trip","旅行の目的"),"Accommodation":("Departure city","出発した都市"),"Goods for customs":("Carry-on size","機内持ち込み荷物の大きさ"),
"Departure time":("Arrival time","到着時刻"),"Gate number":("Seat number","座席番号"),"Platform number":("Train number","列車番号"),"Bus number":("Bus fare","バス運賃"),
"Unlimited local travel":("One express journey","急行の片道1回"),"Shorter journey":("Lower ticket price","安い切符"),"One journey":("Unlimited travel","乗り放題"),"Reserved seat required":("Any seat is available","自由に座れる"),
"Use the north exit":("Use the south exit","南口を使う"),"Cross at the traffic light":("Stay on this side","こちら側にいる"),"Use bus number eight":("Walk all the way","ずっと歩く"),"Opposite the library":("Behind the library","図書館の裏"),
"Estimated travel time":("Waiting time","待ち時間"),"Price will not change":("Price depends on the meter","料金はメーターで変わる"),"Starting meter price":("Total fixed price","定額の合計"),"Possible delay":("Guaranteed arrival time","到着時刻の保証"),
}

VOCAB = {
2:("return ticket|帰りの航空券; conference|会議; declare|申告する","hotel|ホテル; holiday|休暇; work|仕事","purpose|目的; accommodation|滞在先"),
3:("departure|出発; platform|ホーム; confirm|確認する","time|時刻; gate|ゲート; bus|バス","information desk|案内所"),
4:("one-way|片道; day pass|一日乗車券; express|急行","ticket|切符; trip|乗車; faster|より速い","reservation|予約"),
5:("north exit|北口; across from|〜の向かいに; route|経路","museum|美術館; bus stop|バス停; road|道","you can't miss it|すぐ分かる"),
6:("fixed fare|定額運賃; traffic|交通状況; address|住所","hotel|ホテル; taxi|タクシー; cost|料金","meter|メーター"),
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
        role,one,two,three=partner
        final=None
    else:
        role=d["role"]
        one,two,three,final=partner
    p1,j1,_=d["p1"][1 if transfer else 0]; p2,j2,_=d["p2"][1 if transfer else 0]
    mine1=core.inputs(p1,f"{prefix}-p1") if complete else core.marks(p1)
    mine2=core.inputs(p2,f"{prefix}-p2") if complete else core.marks(p2)
    jp1=core.marks(j1,"target") if complete else core.marks(j1)
    jp2=core.marks(j2,"target") if complete else core.marks(j2)
    mine_turn1 = core.answer_turn(ME,"Me",mine1,jp1) if complete else turn("me",ME,"Me",mine1,jp1)
    mine_turn2 = core.answer_turn(ME,"Me",mine2,jp2) if complete else turn("me",ME,"Me",mine2,jp2)
    turns=[turn("other",OTHER,role,esc(one),esc(partner_ja(one))),mine_turn1,turn("other",OTHER,role,esc(two),esc(partner_ja(two))),mine_turn2,turn("other",OTHER,role,esc(three),esc(partner_ja(three))),turn("me",ME,"Me","Thank you.","ありがとうございます。")]
    if final:
        turns.append(turn("other",OTHER,role,esc(final),esc(partner_ja(final))))
    return ''.join(turns)


def understand(d):
    blocks=[]
    for i,(line,sense,ja) in enumerate(d["receptive"]):
        wrong_en,wrong_ja=DISTRACTORS[sense]
        blocks.append(f'<div class="choose-row sentence receptive-choice" data-sync-id="understand-{i}" data-sync-kind="selection"><span class="translation">{esc(line)}</span><span class="choose-sentence"><span class="opt" data-sync-option="yes" data-correct><span class="choice-en">{esc(sense)}</span><small>{esc(ja)}</small></span><span class="opt" data-sync-option="no"><span class="choice-en">{esc(wrong_en)}</span><small>{esc(wrong_ja)}</small></span></span></div>')
    return core.section("understand","Understand","聞いてわかろう",'<p class="section-subtitle"><span class="ko">I will read each staff line. Choose what it means.</span><span class="ja">係員のセリフを読みます。意味を選びましょう。</span></p><div class="tutor-note">Read only the English header in each row.</div>'+''.join(blocks))


def build(n,d):
    source=PILOT.read_text(encoding="utf-8"); head,foot=new_lesson.split_shell(source); slug=f'{n:02d}-{d["slug"]}'
    head=set_vocab(new_lesson.retarget(head,review_id=f"CTX-{n}",lesson_id=slug,level="A2-B1",title=d["title"],title_ko=d["ko"],title_ja=d["ja"],version="2026-08-19").replace('content="todo"','content="reviewed"'),n)
    expr=''.join(f'<div class="model-line"><span class="korean">{esc(en)}</span><span class="translation">{esc(ja)}</span></div>' for en,ja in d["expressions"])
    pages=[core.section("situation-card","Your task","今回のミッション",f'<p class="section-subtitle"><span class="ko">{esc(d["goal"][0])}</span><span class="ja">{esc(d["goal"][1])}</span></p><div class="cast"><div class="cast-row">{avatar(ME,"Me")}<span>Traveller</span></div><div class="cast-row">{avatar(OTHER,d["role"])}<span>{esc(d["scene"])}</span></div></div>'),
      core.section("scene",esc(d["scene"]),esc(d["scene_ja"]),'<p class="section-subtitle"><span class="ko">Listen to the whole exchange first.</span><span class="ja">まず会話全体を聞きましょう。</span></p><div class="dialogue">'+conversation(d)+'</div>'),
      f'    <div class="transition-page" data-page-id="lesson-goal" data-act="Travel task"><span class="transition-kicker">GOAL</span><h2 class="transition-title">{esc(d["title"])} <span class="title-ja">({esc(d["ja"])})</span></h2><p class="section-subtitle"><span class="ko">{esc(d["goal"][0])}</span><span class="ja">{esc(d["goal"][1])}</span></p></div>\n',
      core.section("expressions","Useful expressions","使える表現",'<p class="section-subtitle"><span class="ko">These two expressions will help in the scene.</span><span class="ja">この場面で役立つ二つの表現です。</span></p><div class="model-list">'+expr+'</div>'),understand(d),
      f'    <div class="transition-page" data-page-id="part1-intro" data-act="Move 1"><span class="transition-kicker">MOVE 1</span><h2 class="transition-title">{esc(core.strip_marks(d["p1"][0][0]))}</h2></div>\n',core.teach("p1-teach",d["p1"],d["goal"]),core.read("p1-read",d["p1"]),core.section("p1-rule","How it works","形を見よう",f'<p class="section-subtitle"><span class="ko">{esc(d["rules"][0][0])}</span><span class="ja">{esc(d["rules"][0][1])}</span></p>'+core.rule_example(d["p1"])),core.lesson_reorder(d,1),core.fill("p1-fill",d["p1"]),core.translate("p1-translate",d["p1"]),core.section("p1-write","Your travel detail","自分の旅行情報",'<p class="section-subtitle"><span class="ko">Use the first move with a true or imagined travel detail.</span><span class="ja">一つ目の表現を、自分の旅行情報で使いましょう。</span></p><div class="task-block"><div class="answer-box tall"><span class="answer-label">自分の言葉で</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="p1-open" rows="2"></textarea></span></div></div>'),
      f'    <div class="transition-page" data-page-id="part2-intro" data-act="Move 2"><span class="transition-kicker">MOVE 2</span><h2 class="transition-title">{esc(core.strip_marks(d["p2"][0][0]))}</h2></div>\n',core.teach("p2-teach",d["p2"],d["goal"]),core.read("p2-read",d["p2"]),core.section("p2-rule","How it works","形を見よう",f'<p class="section-subtitle"><span class="ko">{esc(d["rules"][1][0])}</span><span class="ja">{esc(d["rules"][1][1])}</span></p>'+core.rule_example(d["p2"])),core.lesson_reorder(d,2),core.fill("p2-fill",d["p2"]),core.translate("p2-translate",d["p2"]),core.section("p2-write","Check one detail","一つ確認しよう",'<p class="section-subtitle"><span class="ko">Use the second move to check the detail that matters most.</span><span class="ja">二つ目の表現で、いちばん大切な情報を確認しましょう。</span></p><div class="task-block"><div class="answer-box tall"><span class="answer-label">自分の言葉で</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="p2-open" rows="2"></textarea></span></div></div>'),
      '    <div class="transition-page" data-page-id="part3-intro" data-act="Complete the task"><span class="transition-kicker">PUT IT TOGETHER</span><h2 class="transition-title">Complete the task <span class="title-ja">(用事を完了しよう)</span></h2></div>\n',
      core.section("p3-model","Replay the scene","場面をもう一度",'<p class="section-subtitle"><span class="ko">Read your lines while I read the other role.</span><span class="ja">自分のセリフを読み、私は相手役を読みます。</span></p><div class="dialogue">'+conversation(d)+'</div>'),
      core.section("p3-complete","Complete the scene","場面を完成しよう",'<p class="section-subtitle"><span class="ko">Say only the missing frame words.</span><span class="ja">空いている表現の部分だけを言いましょう。</span></p><div class="tutor-note">Write each target exactly as the learner says it.</div><div class="dialogue">'+conversation(d,True,"complete")+'</div>'),
      core.section("p3-freetalk","Compare experiences","経験を比べよう",f'<p class="section-subtitle"><span class="ko">How would you handle this situation on a real trip?</span><span class="ja">実際の旅行なら、この場面にどう対応しますか？</span></p><div class="dialogue"><div class="turn other"><span class="who"><span class="avatar icon">T</span><span class="who-name">Tutor</span></span><div class="bubble"><span class="korean">What would matter most to you here?</span><span class="translation">ここでは何をいちばん重視しますか？</span></div></div><div class="turn me"><span class="who"><span class="avatar icon">私</span><span class="who-name">Me</span></span><div class="bubble me"><div class="answer-box"><span class="answer-label">My answer</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-me" rows="2"></textarea></span></div></div></div><div class="turn me"><span class="who"><span class="avatar icon">私</span><span class="who-name">Me</span></span><div class="bubble me"><span class="korean">How about you?</span><span class="translation">あなたはどうですか？</span></div></div><div class="turn other"><span class="who"><span class="avatar icon">T</span><span class="who-name">Tutor</span></span><div class="bubble"><div class="answer-box"><span class="answer-label">Tutor\'s answer</span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-tutor" rows="2"></textarea></span></div></div></div></div>'),
      core.section("native-tip","A natural extra","自然な言い方",f'<p class="section-subtitle"><span class="ko">Add one of these only when it matches the situation.</span><span class="ja">場面に合うときだけ、どちらかを加えましょう。</span></p><div class="model-list">{expr}</div>'),
      core.section("transfer-scene",esc(d["transfer"][0]),"別の場面へ",'<p class="section-subtitle"><span class="ko">Use the same two moves in a different travel situation.</span><span class="ja">同じ二つの表現を別の旅行場面で使いましょう。</span></p><div class="dialogue">'+conversation(d,True,"transfer",True)+'</div>')]
    document=head+"\n".join(pages)+foot
    document=document.replace('data-page-id="situation-card"','data-page-id="situation-card" data-act="Travel task"',1)
    out=TRACK/"courses"/COURSE/"lessons"/slug/"lesson.html"; return out,new_lesson.redepth(document,out)


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh",action="store_true"); args=ap.parse_args()
    for n,d in LESSONS.items():
        out,text=build(n,d)
        if out.exists() and not args.refresh: raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS)} Contextual decks generated")
    return 0


if __name__=="__main__": raise SystemExit(main())
