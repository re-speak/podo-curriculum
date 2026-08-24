#!/usr/bin/env python3
"""Generate the explicit CTX 13-24 travel disruptions and social course batches."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_contextual_hotels_food_batch as base
import generate_core_course_batch as core
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/2-contextual-english"
PILOT = TRACK / "courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html"
COURSES = {
    range(13, 19): "ctx-travel-disruptions-urgent-problems",
    range(19, 25): "ctx-travel-independent-social",
}
ME, OTHER = core.ME, core.OTHER


def rows(*items):
    return items


LESSONS = {
    13: dict(
        slug="rebook-after-a-missed-connection",
        title="Rebook after a missed connection",
        ko="연결편을 놓친 뒤 재예약하기",
        ja="乗り継ぎに失敗したあと予約を取り直す",
        level="B1-B2",
        course_no=3,
        role="Transfer Agent",
        scene="At an airline transfer desk",
        scene_ja="航空会社の乗り継ぎカウンター",
        situation="旅行仲間と二人で移動中、最初の便の遅延で乗り継ぎに間に合わず、二人が到着できる別の旅程を確保します。",
        goal=("Explain the disruption and obtain a replacement itinerary for you and your travel companion.", "遅延の事情を説明し、旅行仲間と二人で到着できる代わりの旅程を確保しましょう。"),
        expressions=(("connecting flight", "乗り継ぎ便"), ("rebook us", "私たちを予約し直す")),
        p1=dict(
            bridge="まず、遅延と乗り継ぎ失敗のつながりを説明します。",
            meaning=("Use this to connect a delay with the journey it caused you to miss.", "遅延と、そのため乗れなかった移動をつなげて説明する表現です。"),
            rows=rows(
                ("Our first flight {t}was delayed, so we{/t} {t}missed{/t} our connection.", "最初の便が{t}遅れたため、私たちは{/t}乗り継ぎ便に{t}乗り遅れました{/t}。", "Our first flight|was delayed, so|we missed|our connection."),
                ("Our train {t}was delayed, so we{/t} {t}missed{/t} the ferry.", "電車が{t}遅れたため、私たちは{/t}フェリーに{t}乗り遅れました{/t}。", "Our train|was delayed, so|we missed|the ferry."),
                ("The airport bus {t}was delayed, so we{/t} {t}missed{/t} check-in.", "空港バスが{t}遅れたため、私たちは{/t}チェックインに{t}間に合いませんでした{/t}。", "The airport bus|was delayed, so|we missed|check-in."),
                ("Our earlier flight {t}was delayed, so we{/t} {t}missed{/t} the last shuttle.", "前の便が{t}遅れたため、私たちは{/t}最終シャトルに{t}乗り遅れました{/t}。", "Our earlier flight|was delayed, so|we missed|the last shuttle."),
            ),
            reorder_criterion="delayed journey / result link / missed action / missed connection",
            rule=("Link the disruption to its result", "遅延と結果をつなぐ", "Put the delayed journey first, then use “so we missed” before the lost connection.", "遅れた移動を先に言い、その結果乗れなかった便の前に so we missed を置きます。", "delayed journey + so we missed + connection", "Explain cause and result", "原因と結果を説明", ("flight · so we missed · connection", "train · so we missed · ferry")),
            write=("What delay could make you miss the next part of a trip?", "「___ was delayed, so we missed ___」を使って、遅れとその結果を伝えましょう。"),
            write_frame="___ was delayed, so we missed ___",
            write_script="Use “___ was delayed, so we missed ___” to explain the delay and missed connection.",
            translate_hints=(("最初の便", "first flight"), ("電車", "train"), ("空港バス", "airport bus"), ("前の便", "earlier flight")),
        ),
        p2=dict(
            bridge="次に、利用できる最も早い代替便を確認します。",
            meaning=("Use this fixed request to ask for the earliest replacement a travel agent can arrange.", "係員が手配できる最も早い代替便を尋ねる定型表現です。"),
            rows=rows(
                ("{t}What's the earliest{/t} flight {t}you can put us on{/t}?", "{t}いちばん早い{/t}便で、{t}乗せてもらえるのはどれですか{/t}？", "What's the earliest|flight|you can put us on?"),
                ("{t}What's the earliest{/t} train tomorrow morning {t}you can put us on{/t}?", "{t}いちばん早い{/t}明日の朝の電車で、{t}乗せてもらえるのはどれですか{/t}？", "What's the earliest|train tomorrow morning|you can put us on?"),
                ("{t}What's the earliest{/t} ferry {t}you can put us on{/t}?", "{t}いちばん早い{/t}フェリーで、{t}乗せてもらえるのはどれですか{/t}？", "What's the earliest|ferry|you can put us on?"),
                ("{t}What's the earliest{/t} connecting flight {t}you can put us on{/t}?", "{t}いちばん早い{/t}乗り継ぎ便で、{t}乗せてもらえるのはどれですか{/t}？", "What's the earliest|connecting flight|you can put us on?"),
            ),
            reorder_criterion="intact earliest-service request / transport / intact arrangement phrase",
            omit_reorder=True,
            omit_rule=True,
            rule=("Keep the replacement request intact", "代替便の依頼をひとまとまりに", "Retrieve the fixed request as a whole and change only the transport.", "定型の依頼をひとまとまりで使い、交通手段だけを変えます。", "What's the earliest + transport + you can put us on?", "Ask for the first replacement", "最初の代替便を頼む", ("earliest · flight", "earliest · train")),
            write=("Which replacement service would you ask for first?", "「What's the earliest ___ you can put us on?」を使って、最も早い代替便を尋ねましょう。"),
            write_frame="What's the earliest ___ you can put us on?",
            write_script="Use “What's the earliest ___ you can put us on?” to ask for the earliest replacement service.",
            translate_hints=(("便", "flight"), ("電車", "train"), ("フェリー", "ferry"), ("シャトル", "shuttle")),
        ),
        scene_turns=(
            ("other", "How can I help you both?", "お二人のご用件を伺います。"),
            ("target", 1, 0),
            ("other", "Let me see what else is available.", "ほかに利用できる便を確認します。"),
            ("target", 2, 0),
            ("other", "There's one at 6:40 with two seats left.", "6時40分の便に残り2席あります。"),
            ("me", "That works for us.", "それで大丈夫です。"),
            ("other", "I'll rebook you and print the new boarding passes.", "予約を取り直し、新しい搭乗券を印刷します。"),
        ),
        receptive=(
            ("Let me see what else is available.", "The agent will look for another itinerary", "係員は別の旅程を探す", "The agent needs an explanation of the delay", "係員は遅延の説明を求めている"),
            ("There's one at 6:40 with two seats left.", "A 6:40 service still has space for two", "6時40分の便に2席残っている", "The 6:40 service is already full", "6時40分の便はすでに満席である"),
            ("I'll rebook you.", "The agent will move you to another service", "係員が別の便に予約し直す", "You must buy the same journey again", "同じ旅程をもう一度購入する必要がある"),
            ("Your bags will be transferred automatically.", "Staff will move the checked bags for you", "預けた荷物は係員が移してくれる", "You must collect the bags before rebooking", "予約変更前に荷物を受け取る必要がある"),
        ),
        live=("After a delay, do you prefer the earliest arrival or the easiest route, and why?", "遅延後は、最も早い到着と楽な経路のどちらを選びますか？なぜですか？", "___ was delayed, so we missed ___. What's the earliest ___ you can put us on?", "遅延の説明と二人が乗れる代替便", "What matters most to you after a travel delay?", "先生は旅行の遅延後に何をいちばん重視しますか？"),
        tip=("Ask for the earliest or the next available service", "earliest と next available", "Use “earliest” when arrival time matters; use “next available” when any open replacement will do.", "到着時刻を優先するなら earliest、空いている次の便なら何でもよい場合は next available を使います。", ("Time matters", "到着時刻を優先", "What's the earliest flight you can put us on?", "乗せてもらえる最も早い便はどれですか？"), ("Any open replacement", "空いている便を優先", "What's the next available flight?", "次に空いている便はどれですか？")),
        transfer_title="At a rail-and-ferry help desk",
        transfer_ja="鉄道とフェリーの案内カウンターで",
        transfer_role="Travel Adviser",
        transfer_turns=(("other", "What happened to the two of you?", "お二人に何がありましたか？"), ("target", 1, 1), ("other", "The ferry company can move your booking.", "フェリー会社で予約を変更できます。"), ("target", 2, 2), ("other", "The 5:20 ferry has space, and your train ticket remains valid.", "5時20分のフェリーに空きがあり、鉄道の切符もそのまま使えます。"), ("me", "That gets us there tonight. Please book it.", "今夜中に着けます。その便をお願いします。"), ("other", "Done. Here is the replacement itinerary.", "手配できました。こちらが新しい旅程です。")),
        vocab=("connecting flight|乗り継ぎ便; rebook us|私たちを予約し直す; next available|次に空いている; delayed|遅れた", "miss|乗り遅れる|CORE-39", "flight|便; train|電車; ferry|フェリー; shuttle|シャトル; check-in|チェックイン; first flight|最初の便; airport bus|空港バス; earlier flight|前の便", "replacement itinerary|代わりの旅程; boarding pass|搭乗券; transfer automatically|自動で移される; remains valid|そのまま有効である"),
    ),
    14: dict(
        slug="report-missing-baggage-precisely",
        title="Report missing baggage precisely",
        ko="분실 수하물 정확히 신고하기",
        ja="見つからない荷物を正確に申告する",
        level="B1-B2", course_no=3, role="Baggage Agent",
        scene="At airport baggage services", scene_ja="空港の手荷物サービス窓口",
        situation="スーツケースが出てこないため、係員が追跡できる特徴を伝えます。",
        goal=("Report the missing bag and give details staff can use to trace it.", "荷物が見つからないことを伝え、追跡に使える特徴を説明しましょう。"),
        expressions=(("baggage tag", "手荷物タグ"), ("tracking number", "追跡番号")),
        p1=dict(
            bridge="まず、どの荷物が到着していないかを伝えます。",
            meaning=("Use this to report that an expected bag has not appeared.", "届くはずの荷物が出てこないことを伝える表現です。"),
            rows=rows(("My suitcase {t}hasn't arrived{/t}.", "スーツケースが{t}まだ届いていません{/t}。", "My suitcase|hasn't arrived."), ("My checked bag {t}hasn't arrived{/t}.", "預けたバッグが{t}まだ届いていません{/t}。", "My checked bag|hasn't arrived."), ("My duffel bag {t}hasn't arrived{/t}.", "ダッフルバッグが{t}まだ届いていません{/t}。", "My duffel bag|hasn't arrived."), ("My child's suitcase {t}hasn't arrived{/t}.", "子どものスーツケースが{t}まだ届いていません{/t}。", "My child's suitcase|hasn't arrived.")),
            omit_reorder=True,
            reorder_criterion="missing item / intact non-arrival frame",
            rule=("Put “hasn't arrived” after the missing bag", "見つからない荷物のあとに hasn't arrived", "Name the expected bag first, then state that it has not arrived.", "届くはずの荷物を先に言い、そのあとにまだ届いていないことを伝えます。", "missing bag + hasn't arrived", "Report non-arrival", "未着を伝える", ("suitcase · hasn't arrived", "checked bag · hasn't arrived")),
            write=("Which missing bag would you report?", "「My ___ hasn't arrived」を使って、見つからない荷物を伝えましょう。"),
            write_frame="My ___ hasn't arrived",
            write_script="Use “My ___ hasn't arrived” to identify the missing bag.",
            translate_hints=(("スーツケース", "suitcase"), ("預けたバッグ", "checked bag"), ("ダッフルバッグ", "duffel bag"), ("子どものスーツケース", "child's suitcase")),
        ),
        p2=dict(
            bridge="次に、色・大きさ・目印を一つの説明にまとめます。",
            meaning=("Use this to describe an item and add one feature that identifies it.", "物の特徴を説明し、見分けるための目印を一つ加える表現です。"),
            rows=rows(("{t}It's a{/t} large red case {t}with{/t} a yellow strap.", "黄色いストラップ{t}付きの{/t}大きな赤いケース{t}です{/t}。", "It's|a large red case|with a yellow strap."), ("{t}It's a{/t} small black case {t}with{/t} a white tag.", "白いタグ{t}付きの{/t}小さな黒いケース{t}です{/t}。", "It's|a small black case|with a white tag."), ("{t}It's a{/t} blue suitcase {t}with{/t} two stickers.", "ステッカーが2枚{t}付いた{/t}青いスーツケース{t}です{/t}。", "It's|a blue suitcase|with two stickers."), ("{t}It's a{/t} gray duffel bag {t}with{/t} green handles.", "緑の持ち手{t}付きの{/t}灰色のダッフルバッグ{t}です{/t}。", "It's|a gray duffel bag|with green handles.")),
            reorder_criterion="identification / complete item description / with + identifying feature",
            rule=("Add the identifying feature with “with”", "目印は with で加える", "Describe the item first, then add its identifying feature with “with.”", "先に物を説明し、目印となる特徴を 「with」 で加えます。", "It's a + description + with + feature", "Give staff a searchable detail", "探せる特徴を伝える", ("red case · with a yellow strap", "blue suitcase · with two stickers")),
            write=("How would you describe an imagined suitcase or bag?", "「It's a ___ with ___」を使って、荷物と目印を説明しましょう。"),
            write_frame="It's a ___ with ___",
            write_script="Use “It's a ___ with ___” to describe the bag and one clear feature.",
            translate_hints=(("黄色いストラップ", "yellow strap"), ("白いタグ", "white tag"), ("ステッカー", "stickers"), ("緑の持ち手", "green handles")),
        ),
        scene_turns=(("other", "How can I help?", "ご用件を伺います。"), ("target", 1, 0), ("other", "Can you describe it?", "どのような物か説明していただけますか？"), ("target", 2, 0), ("other", "Thank you. I'll start a trace now.", "ありがとうございます。今から追跡を始めます。"), ("me", "Here's my baggage tag and tracking number.", "こちらが手荷物タグと追跡番号です。"), ("other", "Your report is filed. We'll text you with an update.", "申告を受け付けました。状況をメッセージでお知らせします。")),
        receptive=(("I'll start a trace now.", "The agent will begin looking for the bag", "係員が荷物の捜索を始める", "The agent has already found the bag", "係員はすでに荷物を見つけている"), ("Your report is filed.", "The missing-bag report has been recorded", "紛失手荷物の申告が記録された", "You need to complete another report", "別の申告書を書く必要がある"), ("We'll text you with an update.", "Staff will send news to your phone", "係員が携帯に状況を送る", "You must return to the airport for news", "状況確認のため空港へ戻る必要がある"), ("Keep your baggage tag.", "Do not throw away the bag receipt", "手荷物タグを捨てずに持っておく", "Attach a new tag to the missing bag", "見つからない荷物に新しいタグを付ける")),
        live=("Which feature makes your bag easiest to recognize?", "自分のバッグは、どの特徴がいちばん見分けやすいですか？", "My ___ hasn't arrived. It's a ___ with ___.", "仮の見つからない荷物と目印", "What does your suitcase look like?", "先生のスーツケースはどんな見た目ですか？"),
        tip=("Say “case” or “suitcase”", "case と suitcase", "Use “suitcase” when the type matters; “case” is a natural shorter reference once the bag is clear.", "種類を明確にするなら suitcase、どの荷物か分かったあとは短く case と言えます。", ("Identifying the type", "種類を明確に", "It's a large red suitcase.", "大きな赤いスーツケースです。"), ("Referring to it again", "同じ荷物をもう一度指す", "It's a large red case.", "大きな赤いケースです。")),
        transfer_title="At a coach-station lost-bag desk", transfer_ja="長距離バス駅の手荷物窓口で", transfer_role="Station Agent",
        transfer_turns=(("other", "Which bag is missing from the coach?", "バスからどの荷物が見つかりませんか？"), ("target", 1, 2), ("other", "What does it look like?", "どのような外見ですか？"), ("target", 2, 3), ("other", "I found a matching bag at the previous station.", "前の駅で特徴の一致するバッグが見つかりました。"), ("me", "That's mine. How can I collect it?", "私の物です。どう受け取れますか？"), ("other", "We'll send it here on the next coach and call you.", "次のバスでこちらへ送り、お電話します。")),
        vocab=("baggage tag|手荷物タグ; tracking number|追跡番号; yellow strap|黄色いストラップ; duffel bag|ダッフルバッグ", "", "suitcase|スーツケース; checked bag|預けたバッグ; case|ケース; tag|タグ; stickers|ステッカー; handles|持ち手; child's suitcase|子どものスーツケース; white tag|白いタグ; green handles|緑の持ち手", "trace|追跡する; report is filed|申告が記録された; receipt|受取証"),
    ),
    15: dict(
        slug="recover-from-taking-the-wrong-train", title="Recover from taking the wrong train", ko="잘못 탄 열차에서 경로 회복하기", ja="間違った電車から正しい経路に戻る", level="B1-B2", course_no=3, role="Passenger",
        scene="On a train going the wrong way", scene_ja="反対方向へ進む電車の中", situation="駅名から方向の間違いに気づき、目的地へ戻る経路を確認します。", goal=("Verify the mistake and get a route back to your destination.", "乗り間違いを確認し、目的地へ戻る経路を教えてもらいましょう。"), expressions=(("wrong direction", "反対方向"), ("change at", "〜で乗り換える")),
        p1=dict(bridge="まず、乗る電車を間違えた可能性を伝えます。", meaning=("Use this to say that you believe you boarded the wrong service.", "違う便に乗ったと思うことを伝える表現です。"), rows=rows(("{t}I think I've taken{/t} {t}the wrong{/t} train.", "{t}違う{/t}電車に{t}乗ってしまったと思います{/t}。", "I think|I've taken|the wrong train."), ("{t}I think I've taken{/t} {t}the wrong{/t} bus for this route.", "この路線で{t}違う{/t}バスに{t}乗ってしまったと思います{/t}。", "I think|I've taken|the wrong bus for this route."), ("{t}I think I've taken{/t} {t}the wrong{/t} line.", "{t}違う{/t}路線に{t}乗ってしまったと思います{/t}。", "I think|I've taken|the wrong line."), ("{t}I think I've taken{/t} {t}the wrong{/t} train to the airport.", "空港行きで{t}違う{/t}電車に{t}乗ってしまったと思います{/t}。", "I think|I've taken|the wrong train to the airport.")), reorder_criterion="belief marker / taken-service action / wrong + transport", rule=("Keep “the wrong” with the transport", "the wrong と交通手段をまとめる", "Use “I've taken” before the complete phrase “the wrong + transport.”", "「I've taken」 のあとに 「the wrong」 + 交通手段をひとまとまりで置きます。", "I think + I've taken + the wrong transport", "State the suspected mistake", "間違いの可能性を伝える", ("I've taken · the wrong train", "I've taken · the wrong bus")), write=("Which service might you accidentally take?", "「I think I've taken the wrong ___」を使って、間違えた交通手段を伝えましょう。"), write_frame="I think I've taken the wrong ___", write_script="Use “I think I've taken the wrong ___” to say which transport you think you took by mistake.", translate_hints=(("電車", "train"), ("バス", "bus"), ("路線", "line"), ("フェリー", "ferry"))),
        p2=dict(bridge="次に、目的地へ戻る具体的な行き方を尋ねます。", meaning=("Use this to ask for the route back to a place you need to reach.", "必要な場所へ戻る道順を尋ねる表現です。"), rows=rows(("{t}How do I get back to{/t} Central Station?", "中央駅へは{t}どう戻ればいいですか{/t}？", "How do I|get back to|Central Station?"), ("{t}How do I get back to{/t} the airport?", "空港へは{t}どう戻ればいいですか{/t}？", "How do I|get back to|the airport?"), ("{t}How do I get back to{/t} the city centre?", "市内中心部へは{t}どう戻ればいいですか{/t}？", "How do I|get back to|the city centre?"), ("{t}How do I get back to{/t} the ferry terminal?", "フェリーターミナルへは{t}どう戻ればいいですか{/t}？", "How do I|get back to|the ferry terminal?")), reorder_criterion="question opening / get-back action / complete destination", rule=("Keep “get back to” with the destination", "get back to と目的地", "Use “get back to” before the place you need to reach again.", "もう一度たどり着きたい場所の前に 「get back to」 を置きます。", "How do I + get back to + destination?", "Ask for the recovery route", "戻る経路を尋ねる", ("get back to · Central Station", "get back to · the airport")), write=("Which destination would you need to get back to?", "「How do I get back to ___?」を使って、戻りたい場所への行き方を尋ねましょう。"), write_frame="How do I get back to ___?", write_script="Use “How do I get back to ___?” to ask how to return to your destination.", translate_hints=(("中央駅", "Central Station"), ("空港", "airport"), ("市内中心部", "city centre"), ("フェリーターミナル", "ferry terminal"))),
        scene_turns=(("other", "You look worried. Is everything okay?", "心配そうですね。大丈夫ですか？"), ("target", 1, 0), ("other", "Where are you trying to go?", "どこへ行こうとしていますか？"), ("me", "Central Station.", "中央駅です。"), ("target", 2, 0), ("other", "Get off at the next stop and cross the platform.", "次の駅で降りて、反対側のホームへ渡ってください。"), ("me", "So I change there and go back two stops. Thank you.", "そこで乗り換えて2駅戻るのですね。ありがとうございます。"), ("other", "Exactly. The next train leaves in five minutes.", "その通りです。次の電車は5分後に出ます。")),
        receptive=(("Where are you trying to go?", "The passenger is asking for your destination", "相手は行き先を尋ねている", "The passenger is asking where you boarded", "相手は乗った場所を尋ねている"), ("Get off at the next stop.", "Leave the train at the next station", "次の駅で電車を降りる", "Stay on the train to the end", "終点まで電車に乗り続ける"), ("Cross the platform.", "Move to the opposite side of the platform", "ホームの反対側へ移る", "Leave the station through the exit", "出口から駅を出る"), ("The next train leaves in five minutes.", "The return train departs soon", "戻る電車はまもなく出る", "The current train stops for five minutes", "今の電車が5分間停車する")),
        live=("When you get lost, do you ask a person or use a map first, and why?", "道に迷ったとき、先に人に聞きますか、それとも地図を使いますか？なぜですか？", "I think I've taken the wrong ___. How do I get back to ___?", "乗り間違いと戻りたい目的地", "What about you—what do you do first?", "先生はどうですか？最初に何をしますか？"),
        tip=("Say where you are or what you did", "今の状況と過去の行動", "Use “I'm on the wrong train” for your situation now; use “I took the wrong train” to describe the mistake.", "今の状況なら 「I'm on the wrong train」、乗り間違えた行動を説明するなら 「I took the wrong train」 を使います。", ("Situation now", "今の状況", "I'm on the wrong train.", "違う電車に乗っています。"), ("Past mistake", "過去の間違い", "I took the wrong train.", "違う電車に乗りました。")),
        transfer_title="On a city bus to the wrong district", transfer_ja="違う地区へ向かう市バスで", transfer_role="Bus Passenger", transfer_turns=(("other", "Are you looking for the museum?", "美術館を探していますか？"), ("target", 1, 1), ("other", "This bus is going east, not downtown.", "このバスは中心街ではなく東へ向かっています。"), ("target", 2, 2), ("other", "Get off at Market Street and take bus 8 in the other direction.", "マーケット通りで降り、反対方向の8番バスに乗ってください。"), ("me", "Got it. I'll change at Market Street.", "分かりました。マーケット通りで乗り換えます。"), ("other", "That bus stops directly outside the museum.", "そのバスは美術館のすぐ前に止まります。")),
        vocab=("wrong direction|反対方向; change at|〜で乗り換える; city centre|市内中心部", "platform|ホーム|CTX-3; station|駅|CORE-7", "train|電車; bus|バス; line|路線; ferry|フェリー; airport|空港; terminal|ターミナル; museum|美術館; Central Station|中央駅; ferry terminal|フェリーターミナル", "opposite side|反対側; going east|東へ向かう; route|経路"),
    ),
    16: dict(
        slug="find-an-item-you-may-have-left-behind", title="Find an item you may have left behind", ko="두고 온 물건 찾기", ja="置き忘れたかもしれない物を探す", level="B1-B2", course_no=3, role="Restaurant Manager", scene="Calling a restaurant after lunch", scene_ja="昼食後にレストランへ電話", situation="昼食時に財布を置き忘れた可能性を伝え、届いている物の特徴を確認します。", goal=("Explain where the item may be and help staff identify it.", "物を置き忘れた場所を説明し、係員が特定できる特徴を伝えましょう。"), expressions=(("lost property", "遺失物"), ("photo ID inside", "中に写真付き身分証がある")),
        p1=dict(bridge="まず、何をどこに置き忘れたと思うかを伝えます。", meaning=("Use this to say where you believe you left an item.", "物をどこに置き忘れたと思うかを伝える表現です。"), rows=rows(("{t}I think I left{/t} my wallet {t}at{/t} your restaurant.", "レストラン{t}に{/t}財布を{t}置き忘れたと思います{/t}。", "I think|I left my wallet|at your restaurant."), ("{t}I think I left{/t} my phone {t}at{/t} your café.", "カフェ{t}に{/t}携帯を{t}置き忘れたと思います{/t}。", "I think|I left my phone|at your café."), ("{t}I think I left{/t} my camera {t}at{/t} the ticket desk.", "切符売り場{t}に{/t}カメラを{t}置き忘れたと思います{/t}。", "I think|I left my camera|at the ticket desk."), ("{t}I think I left{/t} my glasses {t}at{/t} the hotel.", "ホテル{t}に{/t}眼鏡を{t}置き忘れたと思います{/t}。", "I think|I left my glasses|at the hotel.")), reorder_criterion="belief marker / left item / at + complete place", rule=("Put the item before the place", "物を先、場所をあとに", "Name the item after “I left” and its possible location after “at.”", "「I left」 のあとに物を、at のあとに置き忘れた可能性のある場所を置きます。", "I think I left + item + at + place", "Locate the possible loss", "置き忘れた場所を示す", ("my wallet · at your restaurant", "my camera · at the ticket desk")), write=("What item might you leave behind, and where?", "何をどこに置き忘れる可能性がありますか？")),
        p2=dict(bridge="次に、その特徴に合う物が届いているか尋ねます。", meaning=("Use this to ask whether somebody has delivered a matching lost item to staff.", "特徴の合う遺失物が係員に届けられているか尋ねる表現です。"), rows=rows(("{t}Has anyone handed in{/t} a brown leather wallet?", "茶色い革の財布が{t}届いていますか{/t}？", "Has anyone|handed in|a brown leather wallet?"), ("{t}Has anyone handed in{/t} a black phone case?", "黒い携帯ケースが{t}届いていますか{/t}？", "Has anyone|handed in|a black phone case?"), ("{t}Has anyone handed in{/t} a silver camera?", "銀色のカメラが{t}届いていますか{/t}？", "Has anyone|handed in|a silver camera?"), ("{t}Has anyone handed in{/t} a pair of blue glasses?", "青い眼鏡が{t}届いていますか{/t}？", "Has anyone|handed in|a pair of blue glasses?")), reorder_criterion="anyone question / intact hand-in action / complete item description", rule=("Keep “handed in” together", "handed in はひとまとまり", "Use “Has anyone handed in” before the complete description of the lost item.", "「Has anyone handed in」 のあとに、なくした物の特徴をまとめて続けます。", "Has anyone handed in + description?", "Ask about the found item", "届いた物を確認", ("handed in · a leather wallet", "handed in · a silver camera")), write=("How would you describe the missing item?", "見つからない物をどう説明しますか？")),
        scene_turns=(("other", "Hello. How can I help?", "お電話ありがとうございます。ご用件を伺います。"), ("target", 1, 0), ("other", "What does it look like?", "どのような外見ですか？"), ("me", "It's brown leather with my photo ID inside.", "茶色い革で、中に写真付き身分証が入っています。"), ("target", 2, 0), ("other", "Yes, we have one behind the counter.", "はい、カウンターの後ろでお預かりしています。"), ("me", "That's mine. I'll come back this afternoon.", "私の物です。今日の午後に取りに行きます。"), ("other", "Please bring some photo ID so we can confirm it's yours.", "ご本人の物か確認できるよう、写真付き身分証をお持ちください。")),
        receptive=(("What does it look like?", "The manager wants a description of the item", "店長は物の特徴を求めている", "The manager wants to know its price", "店長は物の値段を知りたい"), ("We have one behind the counter.", "A matching item is being kept at the restaurant", "特徴の合う物を店で保管している", "The item was sent to the police", "その物は警察へ送られた"), ("Please bring some photo ID.", "Take identification when you collect it", "受け取るときに身分証を持っていく", "Send a photo of the restaurant", "レストランの写真を送る"), ("Nothing matching that description has been handed in.", "Staff have not received an item like yours", "特徴の合う物は届いていない", "Staff found exactly the item you described", "説明した物が見つかった")),
        live=("Imagine you left something at a café. Call and ask whether it was handed in.", "カフェに物を置き忘れたとします。電話して、届いているか尋ねましょう。", "I think I left ___ at ___. Has anyone handed in ___?", "置き忘れた物・場所・特徴", "Which item would be hardest for you to replace while traveling?", "旅行中になくすと最も困る物は何ですか？"),
        tip=("Say “handed in” or “turned in”", "handed in と turned in", "Both mean that somebody gave a found item to staff; “handed in” is especially common in British English, and “turned in” in American English.", "どちらも拾った物を係員に届ける意味で、「handed in」 は特にイギリス英語、「turned in」 はアメリカ英語でよく使います。", ("Common in British English", "イギリス英語で一般的", "Has anyone handed in a wallet?", "財布が届いていますか？"), ("Common in American English", "アメリカ英語で一般的", "Has anyone turned in a wallet?", "財布が届いていますか？")),
        transfer_title="At a museum lost-property desk", transfer_ja="美術館の遺失物窓口で", transfer_role="Museum Attendant", transfer_turns=(("other", "What did you lose?", "何をなくしましたか？"), ("target", 1, 2), ("other", "Can you describe the camera?", "カメラの特徴を説明できますか？"), ("target", 2, 2), ("other", "Yes. A guard brought that camera here.", "はい。警備員がそのカメラをこちらへ届けました。"), ("me", "The serial number on this photo matches it.", "この写真の製造番号と一致します。"), ("other", "It matches. Please sign here, and I'll return it.", "一致しました。こちらに署名していただければ、お返しします。")),
        vocab=("handed in|届けられた; turned in|届けられた; leather|革製の; lost property|遺失物; photo ID|写真付き身分証", "wallet|財布|CORE-55", "phone|携帯; camera|カメラ; glasses|眼鏡; restaurant|レストラン; café|カフェ; hotel|ホテル", "behind the counter|カウンターの後ろ; serial number|製造番号"),
    ),
    17: dict(
        slug="challenge-an-unexpected-charge", title="Challenge an unexpected charge", ko="예상하지 못한 요금 이의 제기하기", ja="覚えのない請求を確認する", level="B1-B2", course_no=3, role="Receptionist", scene="At hotel checkout", scene_ja="ホテルのチェックアウト", situation="旅行仲間と泊まった部屋の請求書に二人とも使っていないミニバー料金があるため、根拠を示して削除を頼みます。", goal=("Question a charge on your shared bill and get it corrected.", "旅行仲間との共同の請求書にある覚えのない料金を確認し、直してもらいましょう。"), expressions=(("itemised bill", "明細付き請求書"), ("remove the charge", "料金を削除する")),
        p1=dict(bridge="まず、その料金が自分たちの利用分ではないと落ち着いて伝えます。", meaning=("Use this fixed frame to distance yourself from a charge without making an accusation.", "相手を責めずに、その料金が自分たちのものではないと伝える定型表現です。"), rows=rows(("{t}I don't think{/t} this minibar charge {t}is ours{/t}.", "このミニバー料金が{t}私たちのもの{/t}だ{t}とは思いません{/t}。", "I don't think|this minibar charge|is ours."), ("{t}I don't think{/t} these laundry charges {t}are ours{/t}.", "これらのランドリー料金が{t}私たちのもの{/t}だ{t}とは思いません{/t}。", "I don't think|these laundry charges|are ours."), ("{t}I don't think{/t} this breakfast charge {t}is ours{/t}.", "この朝食料金が{t}私たちのもの{/t}だ{t}とは思いません{/t}。", "I don't think|this breakfast charge|is ours."), ("{t}I don't think{/t} these parking charges {t}are ours{/t}.", "これらの駐車料金が{t}私たちのもの{/t}だ{t}とは思いません{/t}。", "I don't think|these parking charges|are ours.")), reorder_criterion="intact distancing frame / disputed charge / ownership phrase", omit_reorder=True, omit_rule=True, rule=("Keep the careful challenge intact", "丁寧な異議をひとまとまりに", "Retrieve the fixed challenge and change only the disputed charge.", "定型の異議表現をひとまとまりで使い、問題の料金だけを変えます。", "I don't think + charge + is ours", "Question without accusing", "責めずに確認する", ("minibar charge · is ours", "laundry charge · is ours")), write=("Which charge would you ask the hotel to explain?", "どの料金についてホテルに説明を求めますか？")),
        p2=dict(bridge="次に、確認してほしい記録を具体的に示します。", meaning=("Use this polite request to ask someone to verify one detail again.", "一つの情報をもう一度確認してもらう丁寧な依頼です。"), rows=rows(("{t}Could you check{/t} that {t}again{/t}?", "それを{t}もう一度{/t}{t}確認していただけますか{/t}？", "Could you check|that|again?"), ("{t}Could you check{/t} the minibar record {t}again{/t}?", "ミニバーの記録を{t}もう一度{/t}{t}確認していただけますか{/t}？", "Could you check|the minibar record|again?"), ("{t}Could you check{/t} the date {t}again{/t}?", "日付を{t}もう一度{/t}{t}確認していただけますか{/t}？", "Could you check|the date|again?"), ("{t}Could you check{/t} the room number {t}again{/t}?", "部屋番号を{t}もう一度{/t}{t}確認していただけますか{/t}？", "Could you check|the room number|again?")), reorder_criterion="polite check request / complete record detail / again", rule=("Put the detail before “again”", "確認する情報を again の前に", "Name the record to verify after “Could you check” and place “again” at the end.", "「Could you check」 のあとに確認する記録を言い、「again」 を最後に置きます。", "Could you check + detail + again?", "Request a second check", "再確認を頼む", ("check · the date · again", "check · the room number · again")), write=("Which bill detail would you ask staff to check again?", "請求書のどの情報をもう一度確認してもらいますか？")),
        scene_turns=(("other", "Are you both ready to check out?", "お二人ともチェックアウトの準備はできましたか？"), ("me", "Yes, but we have a question about this itemised bill.", "はい。ただ、この明細付き請求書について確認があります。"), ("target", 1, 0), ("other", "It shows two drinks on Tuesday.", "火曜日に飲み物が2本記録されています。"), ("me", "We weren't here on Tuesday.", "火曜日は二人ともホテルにいませんでした。"), ("target", 2, 0), ("other", "You're right. I'll remove it.", "おっしゃる通りです。料金を削除します。"), ("me", "Thank you. The total is correct now.", "ありがとうございます。これで合計が正しくなりました。")),
        receptive=(("It shows two drinks on Tuesday.", "The bill records two minibar drinks on Tuesday", "火曜日にミニバーの飲み物が2本記録されている", "The room includes two free drinks on Tuesday", "火曜日は飲み物が2本無料で付く"), ("I'll remove it.", "The disputed charge will be taken off the bill", "問題の料金を請求書から削除する", "The receptionist will move the charge to another room", "料金を別の部屋へ移す"), ("The total has been adjusted.", "The amount due has been corrected", "支払う合計額が修正された", "A second bill will arrive later", "あとで別の請求書が届く"), ("This charge came from room service.", "The billed item was recorded by room service", "その料金はルームサービスの記録から来ている", "The charge is a city tax", "その料金は市税である")),
        live=("You and a travel companion find a charge neither of you recognizes on your shared bill. Challenge it and request a check.", "旅行仲間との共同の請求書に、二人とも覚えのない料金があります。異議を伝え、再確認を頼みましょう。", "I don't think ___ is ours. Could you check ___ again?", "共同の請求書にある問題の料金と確認してほしい記録", "If you had a shared travel bill, which detail would you check first?", "旅行中の共同の請求書があるとしたら、最初にどの項目を確認しますか？"),
        tip=("Call it a “charge” or a “fee”", "charge と fee", "Use “charge” for an amount added to a bill; use “fee” for the stated cost of a service.", "請求書に加えられた金額なら charge、サービスに設定された料金なら fee を使います。", ("Added to a bill", "請求書に加算", "I don't recognize this charge.", "この請求には覚えがありません。"), ("Cost of a service", "サービスの料金", "Is there a late checkout fee?", "レイトチェックアウト料金はありますか？")),
        transfer_title="At a rental-car return desk", transfer_ja="レンタカーの返却カウンターで", transfer_role="Rental Agent", transfer_turns=(("other", "Here is the final bill for the car you both rented.", "お二人で借りた車の最終請求書です。"), ("target", 1, 3), ("other", "The system says the car returned after six.", "システムでは6時以降の返却になっています。"), ("target", 2, 2), ("other", "The gate record shows 5:42. I'll remove the late fee.", "ゲート記録は5時42分です。延滞料金を削除します。"), ("me", "Thank you. We'll pay the corrected total.", "ありがとうございます。修正後の合計を二人で支払います。"), ("other", "Done. Here is the updated receipt.", "完了しました。こちらが更新後の領収書です。")),
        vocab=("minibar charge|ミニバー料金; itemised bill|明細付き請求書; remove the charge|料金を削除する; late checkout fee|レイトチェックアウト料金; charge|料金", "bill|請求書|CORE-49", "laundry|ランドリー; breakfast|朝食; parking|駐車; date|日付; room number|部屋番号; total|合計", "adjusted|修正された; amount due|支払額; gate record|ゲート記録"),
    ),
    18: dict(
        slug="get-appropriate-medical-help", title="Get appropriate medical help", ko="상황에 맞는 의료 도움 받기", ja="症状に合った医療機関を案内してもらう", level="B1-B2", course_no=3, role="Pharmacist", scene="At a pharmacy", scene_ja="薬局の相談カウンター", situation="悪化している症状を伝え、医師の診察が必要か確認します。", goal=("Describe the problem and ask what level of help is appropriate.", "症状を説明し、どの医療機関へ行くべきか確認しましょう。"), expressions=(("getting worse", "悪化している"), ("walk-in clinic", "予約不要の診療所")),
        p1=dict(bridge="まず、症状と続いている期間をまとめて伝えます。", meaning=("Use this fixed frame to state continuing symptoms and their duration.", "続いている症状と期間を伝える定型表現です。"), rows=rows(("{t}I've had{/t} a fever and a cough {t}for{/t} three days.", "発熱と咳が{t}3日間{/t}{t}続いています{/t}。", "I've had|a fever and a cough|for|three days."), ("{t}I've had{/t} a sore throat {t}for{/t} two days.", "喉の痛みが{t}2日間{/t}{t}続いています{/t}。", "I've had|a sore throat|for|two days."), ("{t}I've had{/t} stomach pain {t}for{/t} a day.", "腹痛が{t}1日{/t}{t}続いています{/t}。", "I've had|stomach pain|for|a day."), ("{t}I've had{/t} this rash {t}for{/t} four days.", "この発疹が{t}4日間{/t}{t}続いています{/t}。", "I've had|this rash|for|four days.")), reorder_criterion="intact symptom-duration frame / symptoms / duration preposition / duration", omit_reorder=True, omit_rule=True, rule=("Keep the duration frame intact", "期間の表現をひとまとまりに", "Retrieve “I've had” and “for” as the fixed duration frame; change only the symptom and time.", "I've had と for を期間の定型表現として使い、症状と時間だけを変えます。", "I've had + symptom + for + duration", "State symptoms and duration", "症状と期間を伝える", ("fever and cough · for three days", "sore throat · for two days")), write=("Choose an imagined symptom and say how long it has lasted.", "仮の症状を一つ選び、どのくらい続いているか伝えましょう。")),
        p2=dict(bridge="次に、医師の診察が必要か専門家に判断を求めます。", meaning=("Use this to ask a professional whether a next step is advisable.", "次に取る行動が望ましいか、専門家に判断を求める表現です。"), rows=rows(("{t}Do you think I should{/t} see a doctor?", "医師に診てもらう{t}べきだと思いますか{/t}？", "Do you think I should|see|a doctor?"), ("{t}Do you think I should{/t} go to a clinic?", "診療所へ行く{t}べきだと思いますか{/t}？", "Do you think I should|go to|a clinic?"), ("{t}Do you think I should{/t} call a medical helpline?", "医療相談窓口へ電話する{t}べきだと思いますか{/t}？", "Do you think I should|call|a medical helpline?"), ("{t}Do you think I should{/t} seek urgent care?", "急ぎの診察を受ける{t}べきだと思いますか{/t}？", "Do you think I should|seek|urgent care?")), reorder_criterion="advice question / action / complete medical destination", rule=("Put the next step after “I should”", "次の行動は I should のあと", "Use “Do you think I should” before the medical action you are considering.", "検討している医療上の行動の前に 「Do you think I should」 を置きます。", "Do you think I should + medical action?", "Ask for an appropriate next step", "次の行動を尋ねる", ("see · a doctor", "go to · a clinic")), write=("Which kind of medical help would you ask about?", "どのような医療機関について尋ねますか？")),
        scene_turns=(("other", "How can I help today?", "今日はどうされましたか？"), ("target", 1, 0), ("other", "Any trouble breathing?", "息苦しさはありますか？"), ("me", "No, but the fever is getting worse.", "いいえ。ただ、熱が悪化しています。"), ("target", 2, 0), ("other", "Yes. There's a walk-in clinic two streets away.", "はい。2本先の通りに予約不要の診療所があります。"), ("me", "I'll go there now. Thank you.", "今からそこへ行きます。ありがとうございます。"), ("other", "If breathing becomes difficult, seek emergency help immediately.", "息苦しくなった場合は、すぐに緊急の医療支援を求めてください。")),
        receptive=(("Any trouble breathing?", "The pharmacist is asking whether breathing is difficult", "息苦しさがあるか尋ねている", "The pharmacist is asking whether you can walk", "歩けるか尋ねている"), ("There's a walk-in clinic two streets away.", "A nearby clinic can see patients without an appointment", "近くに予約なしで受診できる診療所がある", "The pharmacy has no medical services nearby", "近くに医療機関はない"), ("You should see a doctor today.", "The pharmacist recommends medical care today", "薬剤師は今日中の受診を勧めている", "The pharmacist says to wait another week", "薬剤師はもう1週間待つように言っている"), ("Seek emergency help immediately.", "Get urgent medical assistance without waiting", "待たずに緊急の医療支援を求める", "Book a routine visit for next month", "来月の通常診療を予約する")),
        live=("Imagine you have had a cough for two days and it is getting worse. Ask what to do.", "咳が2日続き、悪化しているとします。どうすべきか尋ねましょう。", "I've had ___ for ___. Do you think I should ___?", "仮の症状・期間・尋ねたい医療行動", "When you feel unwell while traveling, who do you contact first?", "旅行中に具合が悪くなったら、最初に誰へ連絡しますか？"),
        tip=("Say “getting worse” or “not getting better”", "getting worse と not getting better", "Use “getting worse” when symptoms are more severe; use “not getting better” when they have not improved.", "症状が強くなっているなら getting worse、改善していないなら not getting better を使います。", ("More severe", "悪化している", "My cough is getting worse.", "咳が悪化しています。"), ("No improvement", "改善していない", "My cough isn't getting better.", "咳がよくなりません。")),
        transfer_title="Calling a nurse at a travel clinic", transfer_ja="旅行者向け診療所の看護師に電話", transfer_role="Nurse", transfer_turns=(("other", "What symptoms are you calling about?", "どのような症状でお電話ですか？"), ("target", 1, 2), ("other", "Is the pain severe or getting worse?", "痛みは強いですか、それとも悪化していますか？"), ("me", "It's getting worse, but I can still drink water.", "悪化していますが、水は飲めます。"), ("target", 2, 1), ("other", "Yes. Come to the clinic now; I'll reserve the next assessment slot.", "はい。今すぐ診療所へ来てください。次の診察枠を確保します。"), ("me", "Thank you. I'll be there in twenty minutes.", "ありがとうございます。20分で着きます。")),
        vocab=("fever|発熱; cough|咳; walk-in clinic|予約不要の診療所; medical helpline|医療相談窓口; urgent care|急ぎの診察; getting worse|悪化している; not getting better|よくならない", "", "doctor|医師; clinic|診療所; sore throat|喉の痛み; stomach pain|腹痛; rash|発疹; three days|3日間", "trouble breathing|息苦しさ; emergency help|緊急の医療支援; assessment slot|診察枠"),
    ),
    19: dict(
        slug="get-a-recommendation-that-fits-your-priorities", title="Get a recommendation that fits your priorities", ko="우선순위에 맞는 추천 받기", ja="希望に合うおすすめを聞く", level="B2", course_no=4, role="Local", scene="Asking a local about a day trip", scene_ja="地元の人に日帰り先を相談", situation="旅行仲間と二人で、有名さより静かな景色を優先し、1日だけならどこを選ぶか地元の人に尋ねます。", goal=("State what you and your travel companion want and obtain a tailored recommendation.", "旅行仲間と二人の希望を伝え、それに合うおすすめを聞きましょう。"), expressions=(("off the beaten track", "穴場の"), ("worth the trip", "行く価値がある")),
        p1=dict(bridge="まず、求める雰囲気と避けたい雰囲気を対比します。", meaning=("Use this to contrast the quality you want with one you would rather avoid.", "求める特徴と避けたい特徴を対比して伝える表現です。"), rows=rows(("{t}We're looking for{/t} somewhere quiet {t}rather than{/t} touristy.", "観光地らしい場所{t}より{/t}、静かな所を{t}探しています{/t}。", "We're looking for|somewhere quiet|rather than|touristy."), ("{t}We're looking for{/t} somewhere local {t}rather than{/t} famous.", "有名な場所{t}より{/t}、地元らしい所を{t}探しています{/t}。", "We're looking for|somewhere local|rather than|famous."), ("{t}We're looking for{/t} a scenic walk {t}rather than{/t} a busy attraction.", "混んだ観光施設{t}より{/t}、景色のよい散歩道を{t}探しています{/t}。", "We're looking for|a scenic walk|rather than|a busy attraction."), ("{t}We're looking for{/t} a small town {t}rather than{/t} a resort.", "リゾート地{t}より{/t}、小さな町を{t}探しています{/t}。", "We're looking for|a small town|rather than|a resort.")), reorder_criterion="search frame / desired option / contrast marker / avoided option", rule=("Put the preferred quality before “rather than”", "希望を rather than の前に", "State what you want first and place the less suitable alternative after “rather than.”", "希望するものを先に言い、合わない選択肢を 「rather than」 のあとに置きます。", "looking for + preference + rather than + alternative", "State the selection criteria", "選ぶ基準を伝える", ("somewhere quiet · rather than touristy", "a scenic walk · rather than a busy attraction")), write=("What would you look for on a free travel day?", "旅行の自由時間なら、どんな場所を探しますか？")),
        p2=dict(bridge="次に、条件が一つなら相手が何を選ぶか尋ねます。", meaning=("Use this to ask for someone's choice under one clear limitation.", "一つのはっきりした条件のもとで、相手なら何を選ぶか尋ねる表現です。"), rows=rows(("{t}What would you choose if{/t} you only had one day?", "1日しかない{t}なら、何を選びますか{/t}？", "What would you choose if|you only had|one day?"), ("{t}What would you choose if{/t} the weather was clear?", "晴れている{t}なら、何を選びますか{/t}？", "What would you choose if|the weather was|clear?"), ("{t}What would you choose if{/t} you wanted quiet scenery?", "静かな景色を楽しみたい{t}なら、何を選びますか{/t}？", "What would you choose if|you wanted|quiet scenery?"), ("{t}What would you choose if{/t} you had no car?", "車がない{t}なら、何を選びますか{/t}？", "What would you choose if|you had|no car?")), reorder_criterion="intact conditional-choice question / condition subject and verb / limiting fact", rule=("Put the condition after “if”", "条件は if のあと", "Ask for the choice first, then add the condition after “if.”", "何を選ぶかを先に尋ね、そのあとに if で条件を加えます。", "What would you choose + if + condition?", "Ask for a tailored choice", "条件に合う選択を尋ねる", ("choose · if you only had one day", "choose · if you had no car")), write=("What one-day condition would shape your choice?", "どんな1日の条件で選択が変わりますか？")),
        scene_turns=(("other", "What kind of day trip are you two after?", "お二人はどんな日帰り旅行をお探しですか？"), ("target", 1, 0), ("other", "Then skip the main beach and go north.", "それなら主要ビーチを避けて北へ行くといいです。"), ("target", 2, 0), ("other", "The coastal walk, definitely.", "間違いなく海岸沿いの散歩道です。"), ("me", "That sounds perfect. How do we get there?", "よさそうです。二人でどう行けばいいですか？"), ("other", "Take bus 12 to North Bay. The trail starts across from the stop.", "12番バスでノースベイへ行ってください。道はバス停の向かいから始まります。")),
        receptive=(("Skip the main beach and go north.", "Avoid the busiest beach and travel north", "主要ビーチを避けて北へ向かう", "Visit the main beach before going south", "主要ビーチへ行ってから南へ向かう"), ("The coastal walk, definitely.", "The local strongly recommends the walk by the coast", "地元の人は海岸沿いの散歩道を強くすすめている", "The coastal walk is closed", "海岸沿いの散歩道は閉鎖されている"), ("It's off the beaten track.", "Few tourists visit the place", "観光客があまり行かない場所である", "The route is next to the main station", "その経路は中央駅のすぐそばにある"), ("It's worth the trip if the weather is clear.", "Good weather makes the journey worthwhile", "晴れていれば行く価値がある", "The trip is only possible in bad weather", "悪天候のときだけ行ける")),
        live=("You and a travel companion want a day trip. State your shared priorities and ask for one recommendation.", "旅行仲間と二人で日帰り旅行を探しています。二人の希望を伝え、おすすめを一つ尋ねましょう。", "We're looking for ___ rather than ___. What would you choose if ___?", "二人の希望・避けたい特徴・一つの条件", "What would you choose if you only had one day here?", "ここで1日しかなかったら何を選びますか？"),
        tip=("Say “touristy” or “popular with tourists”", "touristy と popular with tourists", "Use “touristy” casually, often with a negative tone; use “popular with tourists” for a neutral description.", "touristy は否定的な響きを含むカジュアルな言い方で、popular with tourists は中立的な説明です。", ("Casual and often negative", "カジュアルで否定的", "It's too touristy for us.", "私たちには観光地っぽすぎます。"), ("Neutral description", "中立的な説明", "It's popular with tourists.", "観光客に人気があります。")),
        transfer_title="Asking a hostel host about an evening out", transfer_ja="ホステルのスタッフに夜の過ごし方を相談", transfer_role="Hostel Host", transfer_turns=(("other", "What kind of place would the two of you like tonight?", "お二人は今夜どんな場所へ行きたいですか？"), ("target", 1, 1), ("other", "There's a neighborhood market away from the main square.", "中央広場から離れた所に地元の市場があります。"), ("target", 2, 3), ("other", "I'd choose the market. It's easy by tram and stays open late.", "私なら市場を選びます。路面電車で行きやすく、遅くまで開いています。"), ("me", "That fits us. Which tram should we take?", "二人の希望に合います。どの路面電車に乗ればいいですか？"), ("other", "Take tram 4 and get off at River Street.", "4番の路面電車でリバー通りまで行ってください。")),
        vocab=("touristy|観光地らしい; off the beaten track|穴場の; worth the trip|行く価値がある; quiet scenery|静かな景色; popular with tourists|観光客に人気がある", "quiet|静かな|CORE-43", "local|地元らしい; famous|有名な; attraction|観光施設; small town|小さな町; resort|リゾート; weather|天気; car|車", "day trip|日帰り旅行; coastal walk|海岸沿いの散歩道; neighborhood market|地元の市場; stays open late|遅くまで開いている"),
    ),
    20: dict(
        slug="join-a-group-activity-confidently", title="Join a group activity confidently", ko="그룹 활동에 자연스럽게 참여하기", ja="グループ活動に自然に加わる", level="B2", course_no=4, role="Guide", scene="At a walking-tour meeting point", scene_ja="ウォーキングツアーの集合場所", situation="一人で集合場所に着き、正しいグループを確認して自然に加わります。", goal=("Identify the group and establish a practical connection.", "正しいグループを確認し、自然に輪へ加わりましょう。"), expressions=(("meeting point", "集合場所"), ("come along", "一緒に来る")),
        p1=dict(bridge="まず、目の前の人たちが参加予定のグループか確認します。", meaning=("Use this to check that you have found the group for a specific activity.", "特定の活動に参加するグループを見つけたか確認する表現です。"), rows=rows(("{t}Is this{/t} the group {t}for{/t} the old-town tour?", "{t}これは{/t}旧市街ツアー{t}の{/t}グループですか？", "Is this|the group for|the old-town tour?"), ("{t}Is this{/t} the group {t}for{/t} the food tour?", "{t}これは{/t}フードツアー{t}の{/t}グループですか？", "Is this|the group for|the food tour?"), ("{t}Is this{/t} the group {t}for{/t} the morning hike?", "{t}これは{/t}朝のハイキング{t}の{/t}グループですか？", "Is this|the group for|the morning hike?"), ("{t}Is this{/t} the group {t}for{/t} the cooking class?", "{t}これは{/t}料理教室{t}の{/t}グループですか？", "Is this|the group for|the cooking class?")), reorder_criterion="identification question / group-for relation / complete activity", rule=("Put the activity after “the group for”", "活動は the group for のあと", "Use “the group for” before the complete name of the activity.", "活動名の前に the group for を置きます。", "Is this + the group for + activity?", "Identify the right group", "正しいグループを確認", ("group for · the old-town tour", "group for · the cooking class")), write=("Which group activity would you look for?", "どのグループ活動を探しますか？")),
        p2=dict(bridge="次に、その人たちと一緒に行ってよいか短く尋ねます。", meaning=("Use this casual request to ask permission to join an unfamiliar group.", "初対面のグループに加わってよいか尋ねるカジュアルな表現です。"), rows=rows(("{t}Mind if I{/t} join you?", "一緒に参加しても{t}いいですか{/t}？", "Mind if I|join you?"), ("{t}Mind if I{/t} walk with you?", "一緒に歩いても{t}いいですか{/t}？", "Mind if I|walk with you?"), ("{t}Mind if I{/t} sit here?", "ここに座っても{t}いいですか{/t}？", "Mind if I|sit here?"), ("{t}Mind if I{/t} come along?", "一緒に行っても{t}いいですか{/t}？", "Mind if I|come along?")), omit_reorder=True, reorder_criterion="intact permission opener / complete joining action", rule=("Put the joining action after “Mind if I”", "参加する行動は Mind if I のあと", "Keep “Mind if I” together and follow it with the action you want permission to take.", "「Mind if I」 をひとまとまりにし、そのあとに許可を求める行動を続けます。", "Mind if I + joining action?", "Ask to join casually", "自然に参加を頼む", ("Mind if I · join you?", "Mind if I · come along?")), write=("How would you ask to join the group?", "グループに加わるとき、どう尋ねますか？")),
        scene_turns=(("other", "Are you here for a tour?", "ツアーに参加されますか？"), ("target", 1, 0), ("other", "Yes. You're in the right place.", "はい。こちらで合っています。"), ("me", "Great. I came on my own.", "よかったです。一人で来ました。"), ("other", "Several people did. We're waiting over here.", "一人で来た方はほかにもいます。こちらで待っています。"), ("target", 2, 0), ("other", "Not at all—we were just introducing ourselves.", "もちろんです。ちょうど自己紹介をしていたところです。"), ("me", "Perfect. I'm Emi.", "よかったです。エミです。"), ("other", "Welcome, Emi. We start in five minutes.", "ようこそ、エミさん。5分後に出発します。")),
        receptive=(("You're in the right place.", "You have found the correct meeting point", "正しい集合場所に着いている", "The group has moved to another place", "グループは別の場所へ移動した"), ("We were just introducing ourselves.", "The group has just started introducing themselves", "グループはちょうど自己紹介を始めたところである", "The group has already finished the tour", "グループはすでにツアーを終えた"), ("We start in five minutes.", "The activity begins soon", "活動はまもなく始まる", "The guide will wait another hour", "ガイドはあと1時間待つ"), ("Feel free to come along.", "You are welcome to join the group", "自由にグループへ加わってよい", "You need a separate private guide", "別の個人ガイドが必要である")),
        live=("Imagine you arrive alone for a group activity. Check the group and ask to join.", "一人でグループ活動に着いたとします。グループを確認し、加わってよいか尋ねましょう。", "Is this the group for ___? Mind if I ___?", "活動名と参加したい行動", "Which group activity would you feel comfortable joining alone?", "一人でも参加しやすいグループ活動は何ですか？"),
        tip=("Ask with “Mind if I” or “Can I”", "Mind if I と Can I", "Use “Mind if I” for a relaxed social request; use “Can I” as a neutral choice in any ordinary situation.", "気軽な社交場面なら 「Mind if I」、一般的で中立的な依頼なら 「Can I」 を使います。", ("Relaxed social request", "気軽な社交場面", "Mind if I join you?", "一緒に参加してもいいですか？"), ("Neutral request", "中立的な依頼", "Can I join you?", "一緒に参加してもいいですか？")),
        transfer_title="At a cooking-class check-in", transfer_ja="料理教室の受付で", transfer_role="Class Host", transfer_turns=(("other", "Hi there. Can I help you?", "こんにちは。ご用件を伺います。"), ("target", 1, 3), ("other", "Yes. This is the evening class, and table three has space.", "はい。夜の教室です。3番テーブルに空きがあります。"), ("target", 2, 2), ("other", "Of course. Put on this apron and meet your table partners.", "もちろんです。このエプロンを着けて、同じテーブルの方と合流してください。"), ("me", "Thanks. Hi, everyone—I'm Emi.", "ありがとうございます。皆さん、こんにちは。エミです。"), ("other", "Welcome. Your ingredients are ready at table three.", "ようこそ。材料は3番テーブルに用意してあります。")),
        vocab=("meeting point|集合場所; come along|一緒に来る; on my own|一人で", "free|空いている|CORE-28", "group|グループ; tour|ツアー; hike|ハイキング; cooking class|料理教室; join|加わる; walk|歩く; sit|座る", "introducing ourselves|自己紹介している; table partners|同じテーブルの参加者"),
    ),
    21: dict(
        slug="make-a-plan-with-people-you-just-met", title="Make a plan with people you just met", ko="처음 만난 사람들과 약속 잡기", ja="初対面の人たちと予定を立てる", level="B2", course_no=4, role="Traveller", scene="After a walking tour", scene_ja="ウォーキングツアーが終わったあと", situation="旅行仲間と二人で、ツアーで会った旅行者を、断りやすさも残しながら夕食へ誘います。", goal=("Propose a plan with your travel companion and leave room for the other travellers to refuse.", "旅行仲間との予定を提案し、相手の旅行者たちが断りやすい余地も残しましょう。"), expressions=(("no pressure", "無理にとは言いません"), ("meet you there", "そこで会う")),
        p1=dict(bridge="まず、自分たちが考えている予定を軽く伝えます。", meaning=("Use this fixed frame to mention a possible plan without presenting it as decided; use “I'm” instead of “We're” when you are alone.", "一人なら We're の代わりに I'm を使って、まだ決定ではない予定を軽く伝える定型表現です。"), rows=rows(("{t}We're thinking of getting{/t} dinner nearby.", "この近くで夕食を{t}食べようと思っています{/t}。", "We're thinking of getting|dinner|nearby."), ("{t}We're thinking of getting{/t} lunch nearby.", "この近くで昼食を{t}食べようと思っています{/t}。", "We're thinking of getting|lunch|nearby."), ("{t}I'm thinking of getting{/t} coffee nearby.", "この近くでコーヒーを{t}飲もうと思っています{/t}。", "I'm thinking of getting|coffee|nearby."), ("{t}We're thinking of getting{/t} dessert nearby.", "この近くでデザートを{t}食べようと思っています{/t}。", "We're thinking of getting|dessert|nearby.")), reorder_criterion="intact tentative-plan chunk / food or drink / nearby", omit_rule=True, rule=("Keep the tentative plan intact", "予定の表現をひとまとまりに", "Retrieve “We're thinking of getting” as one fixed invitation lead-in and change only the plan; use “I'm” when you are alone.", "We're thinking of getting を誘いの前置きとしてひとまとまりで使い、予定だけを変えます。一人なら I'm を使います。", "We're/I'm thinking of getting + plan + nearby", "Mention the possible plan", "考えている予定を伝える", ("getting · dinner nearby", "getting · coffee nearby")), write=("What nearby plan could you suggest after an activity?", "活動のあと、近くで何をする予定を提案しますか？")),
        p2=dict(bridge="次に、相手の都合を尊重しながら参加を歓迎します。", meaning=("Use this to offer a warm invitation that depends on the other person's availability; use “me” when you are alone.", "一人なら us の代わりに me を使って、相手の都合を尊重しながら歓迎する表現です。"), rows=rows(("{t}You're welcome to{/t} join us {t}if you're free{/t}.", "{t}もし時間があれば{/t}、{t}よかったら一緒に参加しませんか{/t}。", "You're welcome to|join us|if you're free."), ("{t}You're welcome to{/t} come with me {t}if you have time{/t}.", "{t}もし時間があれば{/t}、{t}よかったら一緒に来ませんか{/t}。", "You're welcome to|come with me|if you have time."), ("{t}You're welcome to{/t} meet us there {t}if that works{/t}.", "{t}都合がよければ{/t}、{t}そこで合流してもらえたらうれしいです{/t}。", "You're welcome to|meet us there|if that works."), ("{t}You're welcome to{/t} bring a friend {t}if you'd like{/t}.", "{t}よければ{/t}、{t}友達も一緒にどうぞ{/t}。", "You're welcome to|bring a friend|if you'd like.")), reorder_criterion="welcome invitation / complete invited action / availability condition", rule=("Put the availability condition last", "都合の条件は最後に", "State the welcomed action first and add the condition with “if” at the end.", "歓迎する行動を先に言い、最後に if で相手の都合を加えます。", "You're welcome to + action + if + condition", "Invite without pressure", "押しつけずに誘う", ("join us · if you're free", "meet us there · if that works")), write=("Who would you invite, and what would you invite them to do?", "誰を何に誘いますか？")),
        scene_turns=(("other", "What are you and your friend doing after the tour?", "あなたと旅行仲間はツアーのあと何をしますか？"), ("target", 1, 0), ("other", "That sounds good. What time?", "よさそうですね。何時ですか？"), ("me", "Around seven.", "7時ごろです。"), ("target", 2, 0), ("other", "Thanks—I'd love to.", "ありがとう。ぜひ参加したいです。"), ("me", "Great. Let's meet outside the station at seven.", "では7時に駅の外で会いましょう。"), ("other", "Perfect. See you there.", "分かりました。そこで会いましょう。")),
        receptive=(("That sounds good. What time?", "The traveller likes the idea and asks when", "相手は提案を気に入り、時刻を尋ねている", "The traveller refuses because it is too late", "相手は遅すぎるため断っている"), ("I'd love to.", "The traveller is happy to accept", "相手は喜んで参加する", "The traveller needs more time to decide", "相手は決める時間が必要である"), ("See you there.", "The meeting place is understood", "待ち合わせ場所が確認できた", "The traveller wants you to pick them up", "相手は迎えに来てほしい"), ("No pressure if you already have plans.", "It is genuinely fine to decline the invitation", "すでに予定があれば断っても問題ない", "The invitation must be accepted now", "今すぐ誘いを受けなければならない")),
        live=("You and a travel companion want to invite someone you just met. Offer one simple plan without pressure. If you are alone, use “I'm” and “me.”", "旅行仲間と二人で、初対面の人を簡単な予定へ誘います。押しつけずに伝えましょう。一人なら I'm と me を使います。", "We're thinking of getting ___ nearby. You're welcome to ___ if ___. / Alone: I'm thinking of ___. You're welcome to come with me if ___.", "二人または一人で考えている予定・誘う行動・相手の都合", "What would you invite a new travel friend to do here?", "ここで新しく会った旅行者を何に誘いますか？"),
        tip=("Say “You're welcome to” or “Feel free to”", "You're welcome to と Feel free to", "Use “You're welcome to” for a warm invitation; use “Feel free to” when you want the choice to feel especially open.", "温かく誘うなら 「You're welcome to」、相手が自由に選べることを強調するなら 「Feel free to」 を使います。", ("Warm invitation", "温かい誘い", "You're welcome to join us.", "よかったら一緒にどうぞ。"), ("Very open choice", "自由に選べる", "Feel free to join us.", "よければ一緒にどうぞ。")),
        transfer_title="After a language-exchange event", transfer_ja="言語交流イベントのあと", transfer_role="Participant", transfer_turns=(("other", "You came on your own today. Are you heading back to the hotel now?", "今日は一人で来たのですね。もうホテルへ戻りますか？"), ("target", 1, 2), ("other", "I know a quiet café near the river.", "川の近くに静かなカフェを知っています。"), ("target", 2, 1), ("other", "I'd like that. I have time before my train.", "ぜひ行きたいです。電車まで時間があります。"), ("me", "Great. Let's walk over together.", "では一緒に歩いて行きましょう。"), ("other", "Perfect. Let's go.", "いいですね。行きましょう。")),
        vocab=("no pressure|無理にとは言わない; meet you there|そこで会う; feel free to|自由に〜する", "nearby|近くに|CORE-15; free|空いている|CORE-28", "dinner|夕食; lunch|昼食; coffee|コーヒー; dessert|デザート; join us|一緒に参加する; come with me|私と一緒に来る; bring a friend|友達を連れてくる", "heading back|戻るところ; language exchange|言語交流"),
    ),
    22: dict(
        slug="resolve-an-itinerary-disagreement", title="Resolve an itinerary disagreement", ko="여행 일정 의견 차이 조율하기", ja="旅程の意見の違いをまとめる", level="B2", course_no=4, role="Companion", scene="Planning the only free afternoon", scene_ja="唯一空いている午後の相談", situation="旅行仲間の希望を認めながら自分の希望も伝え、短い経路で妥協します。", goal=("Acknowledge the other preference and propose a workable compromise.", "相手の希望を認め、自分の希望も伝えて実行できる妥協案を出しましょう。"), expressions=(("meet halfway", "歩み寄る"), ("work for both of us", "二人に都合がよい")),
        p1=dict(bridge="まず、相手の理由を認めてから自分の希望を対比します。", meaning=("Use this to acknowledge someone's reason before stating a different preference.", "相手の理由を認めてから、異なる自分の希望を伝える表現です。"), rows=rows(("{t}I see why{/t} you want to go, {t}but I prefer{/t} staying nearby.", "行きたい理由は{t}分かりますが{/t}、私は近くにいるほうを{t}選びます{/t}。", "I see why|you want to go,|but I prefer|staying nearby."), ("{t}I see why{/t} you want the long route, {t}but I prefer{/t} the short one.", "長い経路を選びたい理由は{t}分かりますが{/t}、私は短いほうを{t}選びます{/t}。", "I see why|you want the long route,|but I prefer|the short one."), ("{t}I see why{/t} you want the museum, {t}but I prefer{/t} the market.", "美術館へ行きたい理由は{t}分かりますが{/t}、私は市場のほうを{t}選びます{/t}。", "I see why|you want the museum,|but I prefer|the market."), ("{t}I see why{/t} you want to leave early, {t}but I prefer{/t} a later start.", "早く出たい理由は{t}分かりますが{/t}、私は遅めの出発を{t}選びます{/t}。", "I see why|you want to leave early,|but I prefer|a later start.")), reorder_criterion="acknowledgment / other preference / contrast plus own preference / own option", rule=("Acknowledge before you contrast", "対比の前に相手を認める", "Put “I see why” before the other person's reason and “but I prefer” before your option.", "相手の理由の前に 「I see why」、自分の希望の前に 「but I prefer」 を置きます。", "I see why + their reason, but I prefer + my option", "Keep both preferences visible", "両方の希望を示す", ("I see why · you want to go", "but I prefer · staying nearby")), write=("Which two travel preferences could conflict?", "どんな二つの旅行の希望がぶつかることがありますか？")),
        p2=dict(bridge="次に、両方の希望を一部満たす具体案を出します。", meaning=("Use this fixed proposal to offer a compromise with two connected actions.", "二つの行動をつないだ妥協案を出す定型表現です。"), rows=rows(("{t}What if we{/t} did the short route and came back by six?", "短い経路にして6時までに戻るのは{t}どうですか{/t}？", "What if we|did the short route|and came back|by six?"), ("{t}What if we{/t} visited the museum and ate at the market?", "美術館へ行って市場で食事をするのは{t}どうですか{/t}？", "What if we|visited the museum|and ate|at the market?"), ("{t}What if we{/t} took a taxi and walked back?", "タクシーで行って歩いて戻るのは{t}どうですか{/t}？", "What if we|took a taxi|and walked|back?"), ("{t}What if we{/t} left at two and returned before dinner?", "2時に出て夕食前に戻るのは{t}どうですか{/t}？", "What if we|left at two|and returned|before dinner?")), reorder_criterion="intact compromise opener / first action / linked second action / time or place result", omit_rule=True, rule=("Keep the compromise opener intact", "妥協案の前置きをひとまとまりに", "Retrieve “What if we” as one proposal chunk and change the two actions.", "What if we を提案の定型表現として使い、二つの行動だけを変えます。", "What if we + action one + and + action two?", "Offer a workable compromise", "実行できる妥協案を出す", ("short route · came back by six", "museum · ate at the market")), write=("What two-part plan could meet both preferences?", "両方の希望を満たす二つの行動は何ですか？")),
        scene_turns=(("other", "Let's take the full mountain route.", "山の全コースに行きましょう。"), ("target", 1, 0), ("other", "I don't want to waste the afternoon, though.", "でも午後を無駄にしたくありません。"), ("target", 2, 0), ("other", "I can live with that.", "それなら受け入れられます。"), ("me", "Great. I'll download the short route.", "では短い経路をダウンロードします。"), ("other", "Then let's leave after lunch and be back by six.", "では昼食後に出発して6時までに戻りましょう。")),
        receptive=(("I don't want to waste the afternoon.", "The companion wants the free time to feel well used", "相手は空いている午後を有効に使いたい", "The companion wants to stay in all afternoon", "相手は午後ずっと中にいたい"), ("I can live with that.", "The companion accepts the compromise", "相手は妥協案を受け入れる", "The companion strongly rejects the plan", "相手は案を強く拒否する"), ("Let's meet halfway.", "Both people should give up part of their preference", "二人とも希望の一部を譲る", "One person should choose the whole plan", "一人が計画をすべて決める"), ("That works for both of us.", "The plan suits both travellers", "その案は二人に都合がよい", "The plan creates another conflict", "その案で別の対立が生まれる")),
        live=("You and a travel companion want different plans. Acknowledge theirs and offer a compromise.", "旅行仲間と希望が違います。相手の希望を認め、妥協案を出しましょう。", "I see why ___, but I prefer ___. What if we ___ and ___?", "相手の希望・自分の希望・二つの妥協行動", "What kind of compromise usually works for you when plans differ?", "予定が違うとき、自分にはどんな妥協案が合いますか？"),
        tip=("Say “I see why” or “I see your point”", "I see why と I see your point", "Use “I see why” to acknowledge someone's motivation; use “I see your point” to acknowledge their argument.", "相手の動機を認めるなら 「I see why」、相手の主張を認めるなら 「I see your point」 を使います。", ("Their motivation", "相手の動機", "I see why you want to go.", "行きたい理由は分かります。"), ("Their argument", "相手の主張", "I see your point about the timing.", "時間についての言い分は分かります。")),
        transfer_title="Choosing between a museum and a market", transfer_ja="美術館と市場のどちらへ行くか相談", transfer_role="Companion", transfer_turns=(("other", "I'd like to spend the whole afternoon at the museum.", "午後はずっと美術館で過ごしたいです。"), ("target", 1, 2), ("other", "We don't have time to do both properly.", "両方を十分楽しむ時間はありません。"), ("target", 2, 1), ("other", "That works for me. We get art and local food.", "それで大丈夫です。芸術と地元の食事を両方楽しめます。"), ("me", "Great. I'll book the museum entry for two.", "では美術館を2人分予約します。"), ("other", "And I'll find a market stall for dinner.", "私は市場で夕食の店を探します。")),
        vocab=("meet halfway|歩み寄る; work for both of us|二人に都合がよい; I see your point|言い分は分かる", "prefer|〜のほうが好き|CORE-42; route|道順|CORE-59", "nearby|近く; museum|美術館; market|市場; short route|短い経路; taxi|タクシー; dinner|夕食", "compromise|妥協; full route|全コース; waste the afternoon|午後を無駄にする; can live with that|それなら受け入れられる"),
    ),
    23: dict(
        slug="clear-up-a-cultural-misunderstanding", title="Clear up a cultural misunderstanding", ko="문화적 오해 풀기", ja="文化的な誤解を解く", level="B2", course_no=4, role="Host", scene="After dinner at a host's home", scene_ja="ホストの家で夕食を終えたあと", situation="料理を残したことで嫌いだと誤解されたため、自分の意図を責めずに説明します。", goal=("Repair an unintended social message without blaming the other person.", "意図しない伝わり方を、相手を責めずに修復しましょう。"), expressions=(("I didn't realise", "気づきませんでした"), ("no offence intended", "悪気はありません")),
        p1=dict(bridge="まず、伝えたかった意味と違って伝わった意味を対比します。", meaning=("Use this fixed correction to replace one interpretation with what you actually meant.", "誤って伝わった解釈を、本当に伝えたかった意味へ直す定型表現です。"), rows=rows(("I'm sorry—{t}I meant{/t} that I was full, {t}not{/t} that I disliked it.", "すみません。料理が嫌いという意味{t}ではなく{/t}、おなかがいっぱいだったという{t}意味です{/t}。", "I'm sorry—|I meant|that I was full,|not that I disliked it."), ("I'm sorry—{t}I meant{/t} that I was tired, {t}not{/t} that I was bored.", "すみません。退屈したという意味{t}ではなく{/t}、疲れていたという{t}意味です{/t}。", "I'm sorry—|I meant|that I was tired,|not that I was bored."), ("I'm sorry—{t}I meant{/t} that I needed a minute, {t}not{/t} that I wanted to leave.", "すみません。帰りたいという意味{t}ではなく{/t}、少し時間が必要だったという{t}意味です{/t}。", "I'm sorry—|I meant|that I needed a minute,|not that I wanted to leave."), ("I'm sorry—{t}I meant{/t} that I was surprised, {t}not{/t} that I was upset.", "すみません。腹を立てたという意味{t}ではなく{/t}、驚いたという{t}意味です{/t}。", "I'm sorry—|I meant|that I was surprised,|not that I was upset.")), reorder_criterion="softener / intact correction frame / intended and unintended meanings", omit_reorder=True, omit_rule=True, rule=("Keep the correction frame intact", "訂正の形をひとまとまりに", "Retrieve “I meant” and “not” as the fixed contrast; change only the two meanings.", "I meant と not を訂正の定型表現として使い、二つの意味だけを変えます。", "I meant + intended meaning, not + unintended meaning", "Replace the interpretation", "解釈を置き換える", ("full · not that I disliked it", "tired · not that I was bored")), write=("Which unintended meaning would you want to correct?", "どんな誤解を訂正したいですか？")),
        p2=dict(bridge="次に、よい意図はあったものの行動を間違えたと説明します。", meaning=("Use this to explain a good intention and acknowledge that the result went wrong.", "よい意図を説明しながら、結果がうまくいかなかったことを認める表現です。"), rows=rows(("{t}I was trying to{/t} be polite, {t}but{/t} I got it wrong.", "丁寧に{t}しようとしていました{/t}{t}が{/t}、やり方を間違えました。", "I was trying to|be polite,|but I got it wrong."), ("{t}I was trying to{/t} get some air, {t}but{/t} it looked like I wanted to leave.", "少し外の空気を吸おうと{t}していました{/t}{t}が{/t}、帰りたいように見えてしまいました。", "I was trying to|get some air,|but it looked like I wanted to leave."), ("{t}I was trying to{/t} show respect, {t}but{/t} I was too formal.", "敬意を示そうと{t}していました{/t}{t}が{/t}、堅すぎました。", "I was trying to|show respect,|but I was too formal."), ("{t}I was trying to{/t} help, {t}but{/t} I interrupted you.", "手伝おうと{t}していました{/t}{t}が{/t}、話を遮ってしまいました。", "I was trying to|help,|but I interrupted you.")), reorder_criterion="attempt frame / intended action / but + unintended result", rule=("Put the intention before the unintended result", "意図を先、結果をあとに", "State what you were trying to do first, then use “but” before what went wrong.", "しようとしていたことを先に言い、うまくいかなかった結果の前に but を置きます。", "I was trying to + intention, but + result", "Explain without shifting blame", "責任転嫁せず説明", ("trying to · be polite", "but · I got it wrong")), write=("What good intention could be misunderstood?", "どんなよい意図が誤解されることがありますか？")),
        scene_turns=(("other", "You hardly touched your dinner. Didn't you like it?", "夕食をほとんど食べませんでしたね。気に入りませんでしたか？"), ("target", 1, 0), ("other", "Oh. I thought you didn't like it.", "そうでしたか。気に入らなかったのだと思いました。"), ("target", 2, 0), ("other", "No harm done. Now I understand.", "大丈夫です。これで分かりました。"), ("me", "Dinner was delicious. Thank you for understanding.", "夕食はとてもおいしかったです。分かってくれてありがとうございます。"), ("other", "Of course. Would you like some tea?", "もちろんです。お茶はいかがですか？")),
        receptive=(("I thought you didn't like it.", "The host interpreted the uneaten food as dislike", "ホストは料理を残したことを嫌いという意味に受け取った", "The host knows you were already full", "ホストは満腹だったと分かっている"), ("No harm done.", "The host accepts the explanation and is not upset", "ホストは説明を受け入れ、怒っていない", "The host wants a formal apology later", "ホストはあとで正式な謝罪を求めている"), ("You hardly touched your dinner.", "You ate very little of the meal", "夕食をほとんど食べなかった", "You finished every part of the meal", "夕食をすべて食べ終えた"), ("No offence taken.", "The other person was not insulted", "相手は気を悪くしていない", "The other person wants to end the conversation", "相手は会話を終えたい")),
        live=("Imagine a polite action was misunderstood. Clarify what you meant and what went wrong.", "丁寧にした行動が誤解されたとします。本当の意図と間違いを説明しましょう。", "I'm sorry—I meant ___, not ___. I was trying to ___, but ___.", "謝意・本当の意味・誤解・意図・結果", "When a misunderstanding happens, do you explain it immediately or wait?", "誤解が起きたら、すぐ説明しますか、それとも待ちますか？"),
        tip=("Say “I meant” or “What I meant was”", "I meant と What I meant was", "Use “I meant” for a quick correction; use “What I meant was” when you want to reset the explanation more clearly.", "短く訂正するなら 「I meant」、説明をはっきりやり直すなら 「What 「I meant」 was」 を使います。", ("Quick correction", "短い訂正", "I meant that I was full.", "おなかがいっぱいだったという意味です。"), ("Clear reset", "説明をやり直す", "What I meant was that I was full.", "私が言いたかったのは、おなかがいっぱいだったということです。")),
        transfer_title="At a community craft workshop", transfer_ja="地域の工芸ワークショップで", transfer_role="Instructor", transfer_turns=(("other", "You stepped away. Did you want to leave the workshop?", "離れた所へ行きましたね。ワークショップを退出したかったのですか？"), ("target", 1, 2), ("other", "I thought stepping away meant you were leaving.", "離れたので、帰るつもりだと思いました。"), ("target", 2, 1), ("other", "Thanks for explaining. There's space for you at this table.", "説明してくれてありがとうございます。このテーブルに席があります。"), ("me", "Great. I'd like to continue with the group.", "よかったです。グループと一緒に続けたいです。"), ("other", "Of course. I'll bring your materials over.", "もちろんです。材料をこちらへ持ってきます。")),
        vocab=("I didn't realise|気づかなかった; no offence intended|悪気はない; got it wrong|やり方を間違えた; What I meant was|私が言いたかったのは; get some air|外の空気を吸う; full|満腹の", "", "polite|丁寧な; tired|疲れた; bored|退屈した; upset|腹を立てた; respect|敬意; formal|堅い; interrupted|話を遮った", "hardly touched|ほとんど食べなかった; no harm done|大丈夫; uncomfortable|居心地が悪い"),
    ),
    24: dict(
        slug="complain-firmly-without-becoming-hostile", title="Complain firmly without becoming hostile", ko="적대적이지 않게 단호히 항의하기", ja="攻撃的にならずにしっかり苦情を伝える", level="B2", course_no=4, role="Tour Manager", scene="At a tour-company office", scene_ja="ツアー会社の窓口", situation="広告より大幅に短かったツアーについて差を示し、釣り合う返金を求めます。", goal=("State the gap and request a proportionate remedy.", "説明との違いを示し、釣り合う対応を求めましょう。"), expressions=(("as advertised", "広告どおり"), ("partial refund", "一部返金")),
        p1=dict(bridge="まず、苦情の中心となる事実を一つに絞って示します。", meaning=("Use this to identify the single fact at the centre of a complaint.", "苦情の中心となる事実を一つ示す表現です。"), rows=rows(("{t}The main issue is that{/t} the tour was half the advertised length.", "ツアーが広告の半分の長さだった点が、{t}一番の問題です{/t}。", "The main issue is that|the tour was|half the advertised length."), ("{t}The main issue is that{/t} two advertised stops were skipped.", "広告にあった立ち寄り先が二つ省かれた点が、{t}一番の問題です{/t}。", "The main issue is that|two advertised stops|were skipped."), ("{t}The main issue is that{/t} the guide left after an hour.", "ガイドが1時間で帰ったのが{t}一番の問題です{/t}。", "The main issue is that|the guide left|after an hour."), ("{t}The main issue is that{/t} the boat never reached the island.", "船が島に着かなかった点が、{t}一番の問題です{/t}。", "The main issue is that|the boat never reached|the island.")), reorder_criterion="intact issue frame / concrete service fact / measurable gap or outcome", rule=("Put the concrete service gap after “that”", "具体的な差は that のあと", "Use “The main issue is that” before one specific, verifiable service failure.", "「The main issue is that」 のあとに、確認できる具体的な問題を一つ続けます。", "The main issue is that + concrete gap", "Keep the complaint factual", "事実に絞って伝える", ("tour · half the advertised length", "advertised stops · were skipped")), write=("Which one service gap would you make the main issue?", "どのサービスの差を一番の問題として伝えますか？")),
        p2=dict(bridge="次に、その事実に釣り合うと思う対応を落ち着いて求めます。", meaning=("Use this fixed frame to connect the circumstances with a remedy you consider proportionate.", "起きたことと、それに釣り合うと思う対応をつなげる定型表現です。"), rows=rows(("{t}Given{/t} what happened, {t}I think{/t} a partial refund {t}would be fair{/t}.", "今回のことを{t}考えると{/t}、一部返金が{t}妥当だと{/t}{t}思います{/t}。", "Given what happened,|I think|a partial refund|would be fair."), ("{t}Given{/t} the shorter tour, {t}I think{/t} a larger discount {t}would be fair{/t}.", "短くなったツアーを{t}考えると{/t}、もっと大きな割引が{t}妥当だと{/t}{t}思います{/t}。", "Given the shorter tour,|I think|a larger discount|would be fair."), ("{t}Given{/t} the missing stops, {t}I think{/t} a forty-percent refund {t}would be fair{/t}.", "立ち寄り先が省かれたことを{t}考えると{/t}、40パーセントの返金が{t}妥当だと{/t}{t}思います{/t}。", "Given the missing stops,|I think|a forty-percent refund|would be fair."), ("{t}Given{/t} what was advertised, {t}I think{/t} another tour {t}would be fair{/t}.", "広告の内容を{t}考えると{/t}、別のツアーの提供が{t}妥当だと{/t}{t}思います{/t}。", "Given what was advertised,|I think|another tour|would be fair.")), reorder_criterion="given-context / stance marker / requested remedy / proportionality judgment", omit_reorder=True, omit_rule=True, rule=("Keep the measured remedy frame intact", "落ち着いた要求をひとまとまりに", "Retrieve the fixed stance around a visible reason and remedy; do not unpack its internal grammar here.", "見えている理由と対応を囲む定型表現を使い、内部の文法はここでは広げません。", "Given + reason, I think + remedy + would be fair", "Request a proportionate remedy", "釣り合う対応を求める", ("Given what happened · partial refund", "Given the missing stops · forty-percent refund")), write=("What remedy would feel proportionate to the service gap?", "サービスの差に釣り合う対応は何だと思いますか？")),
        scene_turns=(("other", "What seems to be the problem with the tour?", "ツアーについて、どのような問題がありましたか？"), ("target", 1, 0), ("other", "I can offer you a ten-percent discount.", "10パーセントの割引をご用意できます。"), ("target", 2, 0), ("other", "Let me speak to my supervisor.", "上司に確認します。"), ("me", "Thank you. I'll wait here.", "ありがとうございます。こちらで待ちます。"), ("other", "My supervisor has approved a forty-percent refund.", "上司が40パーセントの返金を承認しました。"), ("me", "Thank you. That feels fair.", "ありがとうございます。それなら妥当だと思います。")),
        receptive=(("I can offer you a ten-percent discount.", "The first remedy reduces the price by ten percent", "最初の対応は料金を10パーセント下げる", "The company will refund the full price", "会社は全額を返金する"), ("Let me speak to my supervisor.", "The manager will ask a more senior person", "担当者が上司へ確認する", "You must contact the tour guide yourself", "自分でツアーガイドへ連絡する必要がある"), ("The refund has been approved.", "The company has agreed to return part of the payment", "会社が支払いの一部を返すことに同意した", "The complaint has been rejected", "苦情は拒否された"), ("The tour ran as advertised.", "The company says the delivered tour matched the description", "会社はツアーが説明どおりだったと言っている", "The company admits the tour was shorter", "会社はツアーが短かったと認めている")),
        live=("A tour delivered much less than advertised. State the main gap and request a fair remedy.", "ツアーが広告より大幅に少ない内容でした。中心の問題を示し、妥当な対応を求めましょう。", "The main issue is that ___. Given ___, I think ___ would be fair.", "中心の問題・根拠・求める対応", "What remedy would you think was fair in that situation?", "その状況なら、どんな対応が妥当だと思いますか？"),
        tip=("Request a review or a supervisor", "再検討と上司への確認", "Use “Could you review this?” for a neutral second look; use “I'd like this reviewed by a supervisor” for a firmer escalation.", "中立的に再確認を頼むなら Could you review this?、より強く上司への確認を求めるなら I'd like this reviewed by a supervisor を使います。", ("Neutral second look", "中立的な再確認", "Could you review this?", "これを再確認していただけますか？"), ("Firmer escalation", "より強い上申", "I'd like this reviewed by a supervisor.", "これを上司に確認していただきたいです。")),
        transfer_title="At a boat-trip operator's desk", transfer_ja="ボートツアー会社の窓口で", transfer_role="Operations Manager", transfer_turns=(("other", "What was missing from your boat trip?", "ボートツアーでは何が不足していましたか？"), ("target", 1, 1), ("other", "The weather forced us to change the route.", "天候のため経路を変更せざるを得ませんでした。"), ("target", 2, 2), ("other", "That's reasonable. I'll issue the forty-percent refund now.", "妥当です。今から40パーセントを返金します。"), ("me", "Thank you. Please send the confirmation by email.", "ありがとうございます。確認をメールで送ってください。"), ("other", "Done. The refund will return to your card within five days.", "完了しました。5日以内にカードへ返金されます。")),
        vocab=("as advertised|広告どおり; partial refund|一部返金; advertised length|広告上の長さ", "issue|問題|CORE-82; refund|返金|CTX-11", "tour|ツアー; discount|割引; fair|妥当な; supervisor|上司; island|島; boat|船", "proportionate remedy|釣り合う対応; approved|承認された; forced us to change|変更せざるを得なかった"),
    ),
}


# Human-reviewed operating copy and support for the bounded CTX 16-24 pass.
# Keeping this overlay explicit lets later review batches regenerate only their
# accepted slice without silently rewriting earlier lesson HTML.
REVIEWED_COPY_16_24 = {
    16: dict(
        role_ja="レストランの店長", transfer_role_ja="美術館の遺失物係",
        live=("Which item would be hardest for you to replace while travelling, and why?", "旅行中になくすと、いちばん困る物は何ですか？なぜですか？", "I think I left ___ at ___. Has anyone handed in ___?", "置き忘れた物・場所・特徴", "What about you—which item would be hardest to replace?", "先生はどうですか？いちばん代わりを用意しにくい物は何ですか？"),
        p1=dict(write_frame="I think I left ___ at ___", write_script="Use “I think I left ___ at ___” to say what you left and where.", write_script_ja="「I think I left ___ at ___」を使って、置き忘れた物と場所を伝えましょう。", translate_hints=(("財布", "wallet"), ("携帯", "phone"), ("カメラ", "camera"), ("眼鏡", "glasses"))),
        p2=dict(write_frame="Has anyone handed in ___?", write_script="Use “Has anyone handed in ___?” to ask whether a matching item was found.", write_script_ja="「Has anyone handed in ___?」を使って、特徴の合う物が届いているか尋ねましょう。", translate_hints=(("茶色い革", "brown leather"), ("黒い携帯ケース", "black phone case"), ("銀色", "silver"), ("青い眼鏡", "blue glasses"))),
    ),
    17: dict(
        role_ja="ホテルの受付係", transfer_role_ja="レンタカー係",
        live=("When you travel with someone, how do you keep track of shared expenses?", "誰かと旅行するとき、共通の支出をどう管理しますか？", "I don't think ___ is ours. Could you check ___ again?", "共同の請求書にある問題の料金と確認してほしい記録", "What about you—do you check every charge?", "先生はどうですか？請求を一つずつ確認しますか？"),
        p1=dict(write_frame="I don't think ___ is ours", write_script="After checking with your travel companion, use “I don't think ___ is ours” to question the charge without accusing staff.", write_script_ja="同行者と確認してから、「I don't think ___ is ours」を使って、相手を責めずに料金を確認しましょう。", translate_hints=(("ミニバー料金", "minibar charge"), ("ランドリー料金", "laundry charge"), ("朝食料金", "breakfast charge"), ("駐車料金", "parking charge"))),
        p2=dict(write_frame="Could you check ___ again?", write_script="Use “Could you check ___ again?” to ask staff to verify one bill detail.", write_script_ja="「Could you check ___ again?」を使って、請求書の情報をもう一度確認してもらいましょう。", translate_stage="checkpoint"),
    ),
    18: dict(
        role_ja="薬剤師", transfer_role_ja="看護師",
        live=("When you feel unwell while travelling, who would you contact first?", "旅行中に具合が悪くなったら、最初に誰へ連絡しますか？", "I've had ___ for ___. Do you think I should ___?", "仮の症状・期間・尋ねたい医療行動", "What about you—who would you contact?", "先生なら誰へ連絡しますか？"),
        p1=dict(write_frame="I've had ___ for ___", write_script="Choose an imagined symptom, then use “I've had ___ for ___” to say how long it has lasted.", write_script_ja="仮の症状を選び、「I've had ___ for ___」を使って、どのくらい続いているか伝えましょう。", translate_hints=(("発熱と咳", "fever and cough"), ("喉の痛み", "sore throat"), ("腹痛", "stomach pain"), ("発疹", "rash"))),
        p2=dict(write_frame="Do you think I should ___?", write_script="Use “Do you think I should ___?” to ask a professional about an imagined next step.", write_script_ja="「Do you think I should ___?」を使って、仮の次の行動について専門家に尋ねましょう。", translate_hints=(("医師に診てもらう", "see a doctor"), ("診療所へ行く", "go to a clinic"), ("医療相談窓口へ電話する", "call a medical helpline"), ("急ぎの診察を受ける", "seek urgent care"))),
    ),
    19: dict(
        role_ja="地元の人", transfer_role_ja="ホステルのスタッフ",
        live=("For a one-day trip, do you prefer a famous sight or a quieter local place, and why?", "日帰り旅行なら、有名な観光地と静かな地元の場所のどちらが好きですか？なぜですか？", "We're looking for ___ rather than ___. What would you choose if ___?", "二人の希望・避けたい特徴・一つの条件", "What kind of day trip do you enjoy most?", "先生はどんな日帰り旅行がいちばん好きですか？"),
        p1=dict(write_frame="We're looking for ___ rather than ___", write_script="Use “We're looking for ___ rather than ___” to state what your group wants and wants to avoid.", write_script_ja="「We're looking for ___ rather than ___」を使って、グループの希望と避けたい特徴を伝えましょう。", translate_hints=((("静かな所", "somewhere quiet"), ("観光地らしい", "touristy")), (("地元らしい所", "somewhere local"), ("有名な", "famous")), (("景色のよい散歩道", "a scenic walk"), ("混んだ観光施設", "a busy attraction")), (("小さな町", "a small town"), ("リゾート地", "a resort")))),
        p2=dict(write_frame="What would you choose if ___?", write_script="Use “What would you choose if ___?” to ask for one recommendation under a real condition.", write_script_ja="「What would you choose if ___?」を使って、条件に合うおすすめを一つ尋ねましょう。", translate_hints=(("1日しかない", "only had one day"), ("晴れている", "weather was clear"), ("静かな景色", "quiet scenery"), ("車がない", "had no car"))),
    ),
    20: dict(
        role_ja="ガイド", transfer_role_ja="料理教室の受付係",
        live=("Which group activity would you feel comfortable joining alone, and why?", "一人でも参加しやすいグループ活動は何ですか？なぜですか？", "Is this the group for ___? Mind if I ___?", "活動名と参加したい行動", "Have you ever joined a group activity while travelling?", "先生は旅行中にグループ活動へ参加したことがありますか？"),
        p1=dict(write_frame="Is this the group for ___?", write_script="Use “Is this the group for ___?” to check that you found the right activity.", write_script_ja="「Is this the group for ___?」を使って、正しい活動のグループか確認しましょう。", translate_hints=(("旧市街ツアー", "old-town tour"), ("フードツアー", "food tour"), ("朝のハイキング", "morning hike"), ("料理教室", "cooking class"))),
        p2=dict(write_frame="Mind if I ___?", write_script="Use “Mind if I ___?” to ask permission to join the group naturally.", write_script_ja="「Mind if I ___?」を使って、自然にグループへ加わってよいか尋ねましょう。", translate_hints=(("一緒に参加する", "join you"), ("一緒に歩く", "walk with you"), ("ここに座る", "sit here"), ("一緒に行く", "come along"))),
    ),
    21: dict(
        role_ja="旅行者", transfer_role_ja="参加者",
        live=("What would you invite a new travel friend to do, and why?", "旅先で新しく会った人を何に誘いたいですか？なぜですか？", "We're thinking of getting ___ nearby. You're welcome to ___ if ___. / Alone: I'm thinking of ___. You're welcome to come with me if ___.", "二人または一人で考えている予定・誘う行動・相手の都合", "What about you—what would you suggest?", "先生なら何を提案しますか？"),
        p1=dict(write_frame="We're/I'm thinking of ___ nearby", write_script="Use “We're thinking of ___ nearby” for a group, or “I'm thinking of ___ nearby” when you are alone, to suggest a plan.", write_script_ja="複数なら「We're thinking of ___ nearby」、一人なら「I'm thinking of ___ nearby」を使って、予定を提案しましょう。", translate_hints=(("夕食", "dinner"), ("昼食", "lunch"), ("コーヒー", "coffee"), ("デザート", "dessert"))),
        p2=dict(write_frame="You're welcome to ___ if ___", write_script="Use “You're welcome to ___ if ___” to invite someone while leaving room to decline.", write_script_ja="「You're welcome to ___ if ___」を使って、断りやすい余地を残して誘いましょう。", translate_hints=((("一緒に参加する", "join us"), ("時間があれば", "if you're free")), (("一緒に来る", "come with me"), ("時間があれば", "if you have time")), (("そこで合流する", "meet us there"), ("都合がよければ", "if that works")), (("友達も連れてくる", "bring a friend"), ("よければ", "if you'd like")))),
    ),
    22: dict(
        role_ja="旅行仲間", transfer_role_ja="旅行仲間",
        live=("When travel plans differ, what helps you find a compromise?", "旅行の希望が違うとき、どうすれば妥協案を見つけやすいですか？", "I see why ___, but I prefer ___. What if we ___ and ___?", "相手の希望・自分の希望・二つの妥協行動", "Are you usually flexible about travel plans?", "先生は旅行の予定について普段柔軟ですか？"),
        p1=dict(write_frame="I see why ___, but I prefer ___", write_script="Use “I see why ___, but I prefer ___” to acknowledge the other preference and state your own.", write_script_ja="「I see why ___, but I prefer ___」を使って、相手の希望を認めてから自分の希望を伝えましょう。", translate_hints=((("行きたい", "want to go"), ("近くにいる", "staying nearby")), (("長い経路", "the long route"), ("短いほう", "the short one")), (("美術館", "the museum"), ("市場", "the market")), (("早く出る", "leave early"), ("遅めの出発", "a later start")))),
        p2=dict(write_frame="What if we ___ and ___?", write_script="Use “What if we ___ and ___?” to propose a two-part compromise.", write_script_ja="「What if we ___ and ___?」を使って、二つの行動を組み合わせた妥協案を出しましょう。", translate_hints=((("短い経路", "the short route"), ("6時までに戻る", "come back by six")), (("美術館", "the museum"), ("市場で食事をする", "eat at the market")), (("タクシー", "a taxi"), ("歩いて戻る", "walk back")), (("2時に出る", "leave at two"), ("夕食前に戻る", "return before dinner")))),
    ),
    23: dict(
        role_ja="ホスト", transfer_role_ja="講師",
        live=("When a misunderstanding happens, do you clear it up immediately or wait, and why?", "誤解が起きたら、すぐ解きますか、それとも待ちますか？なぜですか？", "I'm sorry—I meant ___, not ___. I was trying to ___, but ___.", "謝意・本当の意味・誤解・意図・結果", "What helps you clear up a misunderstanding?", "先生は誤解を解くとき、何が役立つと思いますか？"),
        p1=dict(write_frame="I'm sorry—I meant ___, not ___", write_script="Use “I'm sorry—I meant ___, not ___” to replace the misunderstanding with what you intended.", write_script_ja="「I'm sorry—I meant ___, not ___」を使って、誤解された意味を本来の意図に直しましょう。", translate_hints=((("おなかがいっぱい", "full"), ("嫌いだった", "disliked it")), (("疲れていた", "tired"), ("退屈していた", "bored")), (("少し時間が必要", "needed a minute"), ("帰りたかった", "wanted to leave")), (("驚いた", "surprised"), ("腹を立てていた", "upset")))),
        p2=dict(write_frame="I was trying to ___, but ___", write_script="Use “I was trying to ___, but ___” to explain the good intention and the unintended result.", write_script_ja="「I was trying to ___, but ___」を使って、よい意図と意図しない結果を説明しましょう。", translate_hints=((("丁寧にする", "be polite"), ("間違えた", "got it wrong")), (("外の空気を吸う", "get some air"), ("帰りたいように見えた", "looked like I wanted to leave")), (("敬意を示す", "show respect"), ("堅すぎた", "was too formal")), (("手伝う", "help"), ("話を遮った", "interrupted you")))),
    ),
    24: dict(
        role_ja="ツアー会社の責任者", transfer_role_ja="運営責任者",
        live=("If a tour was disappointing, what response would feel fair to you?", "ツアーが期待外れだったら、どんな対応が妥当だと思いますか？", "The main issue is that ___. Given ___, I think ___ would be fair.", "中心の問題・根拠・求める対応", "Have you ever asked a company to fix a problem?", "先生は会社に問題への対応を頼んだことがありますか？"),
        p1=dict(write_frame="The main issue is that ___", write_script="Use “The main issue is that ___” to state one specific, verifiable service gap.", write_script_ja="「The main issue is that ___」を使って、確認できるサービスの問題を一つ伝えましょう。", translate_hints=(("広告の半分の長さ", "half the advertised length"), ("立ち寄り先が二つ省かれた", "two stops were skipped"), ("1時間で帰った", "left after an hour"), ("島に着かなかった", "never reached the island"))),
        p2=dict(write_frame="Given ___, I think ___ would be fair", write_script="Use “Given ___, I think ___ would be fair” to connect the facts with a proportionate remedy.", write_script_ja="「Given ___, I think ___ would be fair」を使って、事実と釣り合う対応を結びつけましょう。", translate_hints=((("今回のこと", "what happened"), ("一部返金", "a partial refund")), (("短くなったツアー", "the shorter tour"), ("もっと大きな割引", "a larger discount")), (("立ち寄り先が省かれた", "the missing stops"), ("40パーセントの返金", "a forty-percent refund")), (("広告の内容", "what was advertised"), ("別のツアー", "another tour")))),
    ),
}

for _number, _copy in REVIEWED_COPY_16_24.items():
    _lesson = LESSONS[_number]
    _lesson["role_ja"] = _copy["role_ja"]
    _lesson["transfer_role_ja"] = _copy["transfer_role_ja"]
    _lesson["live"] = _copy["live"]
    for _part in (1, 2):
        _lesson[f"p{_part}"].update(_copy[f"p{_part}"])

    # Hint chips are explicit in-lesson support, so every chip must also be
    # declared in the lesson's vocabulary ownership metadata.  Derive this
    # mechanically from the reviewed hint rows to prevent source/HTML drift.
    _owned_english = {
        _entry.split("|")[0].strip().casefold()
        for _category in _lesson["vocab"]
        for _entry in _category.split(";")
        if _entry.strip()
    }
    _support_additions = []
    for _part in (1, 2):
        for _hint_row in _lesson[f"p{_part}"].get("translate_hints", ()):
            if len(_hint_row) == 2 and all(isinstance(_item, str) for _item in _hint_row):
                _hint_row = (_hint_row,)
            for _japanese_hint, _english_hint in _hint_row:
                if _english_hint.casefold() not in _owned_english:
                    _support_additions.append(f"{_english_hint}|{_japanese_hint}")
                    _owned_english.add(_english_hint.casefold())
    if _support_additions:
        _vocab = list(_lesson["vocab"])
        _vocab[2] = "; ".join(filter(None, (_vocab[2], *_support_additions)))
        _lesson["vocab"] = tuple(_vocab)

AUTHORITATIVE = {
    13: ("Rebook after a missed connection", "Our first flight was delayed, so we missed our connection.", "What's the earliest flight you can put us on?"),
    14: ("Report missing baggage precisely", "My suitcase hasn't arrived.", "It's a large red case with a yellow strap."),
    15: ("Recover from taking the wrong train", "I think I've taken the wrong train.", "How do I get back to Central Station?"),
    16: ("Find an item you may have left behind", "I think I left my wallet at your restaurant.", "Has anyone handed in a brown leather wallet?"),
    17: ("Challenge an unexpected charge", "I don't think this minibar charge is ours.", "Could you check that again?"),
    18: ("Get appropriate medical help", "I've had a fever and a cough for three days.", "Do you think I should see a doctor?"),
    19: ("Get a recommendation that fits your priorities", "We're looking for somewhere quiet rather than touristy.", "What would you choose if you only had one day?"),
    20: ("Join a group activity confidently", "Is this the group for the old-town tour?", "Mind if I join you?"),
    21: ("Make a plan with people you just met", "We're thinking of getting dinner nearby.", "You're welcome to join us if you're free."),
    22: ("Resolve an itinerary disagreement", "I see why you want to go, but I prefer staying nearby.", "What if we did the short route and came back by six?"),
    23: ("Clear up a cultural misunderstanding", "I'm sorry—I meant that I was full, not that I disliked it.", "I was trying to be polite, but I got it wrong."),
    24: ("Complain firmly without becoming hostile", "The main issue is that the tour was half the advertised length.", "Given what happened, I think a partial refund would be fair."),
}


def course_for(number: int) -> str:
    for numbers, course in COURSES.items():
        if number in numbers:
            return course
    raise ValueError(f"CTX-{number}: no assigned course")


def validate_lesson(number, lesson):
    expected_title, expected_p1, expected_p2 = AUTHORITATIVE[number]
    if lesson["title"] != expected_title:
        raise ValueError(f"CTX-{number}: title differs from the generated brief")
    actual = tuple(core.strip_marks(lesson[f"p{part}"]["rows"][0][0]) for part in (1, 2))
    if actual != (expected_p1, expected_p2):
        raise ValueError(f"CTX-{number}: required models differ from the generated brief: {actual}")
    if len(lesson["expressions"]) != 2 or len(lesson["receptive"]) != 4:
        raise ValueError(f"CTX-{number}: needs two expressions and four receptive checks")
    if not 5 <= len(lesson["scene_turns"]) <= 9:
        raise ValueError(f"CTX-{number}: opening scene needs 5-9 turns")
    if not 5 <= len(lesson["transfer_turns"]) <= 7:
        raise ValueError(f"CTX-{number}: transfer needs 5-7 turns")
    for turns, label in ((lesson["scene_turns"], "scene"), (lesson["transfer_turns"], "transfer")):
        targets = [turn for turn in turns if turn[0] == "target"]
        if len(targets) != 2 or {turn[1] for turn in targets} != {1, 2}:
            raise ValueError(f"CTX-{number}: {label} must use both patterns once")
    for part in (1, 2):
        pattern = lesson[f"p{part}"]
        if len(pattern["rows"]) != 4:
            raise ValueError(f"CTX-{number} p{part}: needs four closed rows")
        if not pattern.get("omit_reorder"):
            core.validate_reorder_pattern(pattern["rows"])
    if 13 <= number <= 24:
        base.validate_reviewed_copy(number, lesson)
    if 13 <= number <= 15:
        for part in (1, 2):
            if not lesson[f"p{part}"].get("write_script"):
                raise ValueError(f"CTX-{number} p{part}: open production needs an explicit communicative job")
    if 16 <= number <= 24:
        if not lesson.get("role_ja") or not lesson.get("transfer_role_ja"):
            raise ValueError(f"CTX-{number}: reviewed roleplay needs explicit Japanese role labels")
        for part in (1, 2):
            pattern = lesson[f"p{part}"]
            for field in ("write_frame", "write_script", "write_script_ja"):
                if not pattern.get(field):
                    raise ValueError(f"CTX-{number} p{part}: missing reviewed {field}")
            hints = pattern.get("translate_hints")
            support_stage = pattern.get(
                "translate_stage", "supported" if hints else None
            )
            if support_stage == "supported":
                if not hints or len(hints) != len(pattern["rows"]):
                    raise ValueError(
                        f"CTX-{number} p{part}: supported translation needs lexical hints"
                    )
            elif support_stage == "checkpoint":
                if hints:
                    raise ValueError(
                        f"CTX-{number} p{part}: checkpoint translation must not have hints"
                    )
            else:
                raise ValueError(
                    f"CTX-{number} p{part}: translation needs a supported/checkpoint stage"
                )


def wrapping_fill(part, pattern):
    """Use the shared target-only fill component; target markers are the contract."""
    return core.fill(f"p{part}-fill", pattern["rows"])


def pages(number, lesson):
    rendered = base.pages(number, lesson)
    for part in (1, 2):
        page_id = f'data-page-id="p{part}-fill"'
        index = next(index for index, page in enumerate(rendered) if page_id in page)
        rendered[index] = wrapping_fill(part, lesson[f"p{part}"])
    return rendered


def build(number, lesson):
    validate_lesson(number, lesson)
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{lesson["slug"]}'
    head = new_lesson.retarget(
        head,
        review_id=f"CTX-{number}",
        lesson_id=slug,
        level=lesson["level"],
        title=lesson["title"],
        title_ko=lesson["ko"],
        title_ja=lesson["ja"],
        version="2026-08-20",
    ).replace('content="todo"', 'content="reviewed"')
    head = base.set_vocab(head, lesson["vocab"])
    head = core.set_proofread_status(head, "complete")
    output = TRACK / "courses" / course_for(number) / "lessons" / slug / "lesson.html"
    document = head + "\n".join(pages(number, lesson)) + foot
    return output, new_lesson.redepth(document, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, choices=LESSONS)
    args = parser.parse_args()
    selected = LESSONS.items() if args.lesson is None else ((args.lesson, LESSONS[args.lesson]),)
    for number, lesson in selected:
        output, text = build(number, lesson)
        if output.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    print(f"{len(LESSONS) if args.lesson is None else 1} Contextual decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
