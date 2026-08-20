#!/usr/bin/env python3
"""Generate the explicit, reviewed CTX 7-12 hotels-and-food course batch."""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_core_course_batch as core
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/2-contextual-english"
COURSE = "ctx-travel-hotels-food"
PILOT = (
    TRACK
    / "courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html"
)
ME, OTHER = core.ME, core.OTHER

ROLE_JA = {
    "Receptionist": "受付係",
    "Server": "店員",
    "Clerk": "店員",
    "Host": "予約係",
    "Transfer Agent": "乗り継ぎ担当者",
    "Baggage Agent": "手荷物係",
    "Passenger": "乗客",
    "Museum Attendant": "美術館の受付係",
    "Property Manager": "管理担当者",
    "Buffet Attendant": "ビュッフェ係",
    "Deli Worker": "デリの店員",
    "Kiosk Clerk": "売店の店員",
    "Tour Agent": "ツアー係",
    "Travel Adviser": "旅行案内係",
    "Station Agent": "駅の手荷物係",
    "Bus Passenger": "バスの乗客",
}


def rows(*items):
    return items


LESSONS = {
    7: dict(
        slug="check-in-when-your-room-is-not-ready",
        title="Check in when your room is not ready",
        ko="객실 준비 전 체크인하기",
        ja="部屋の準備前にチェックインする",
        role="Receptionist",
        scene="Hotel reception before check-in time",
        scene_ja="チェックイン時間前のホテル受付",
        situation="予約を確認し、部屋を待つ間に荷物を安全に預けます。",
        goal=(
            "Confirm your booking and arrange a useful place for your bags while you wait.",
            "予約を確認し、待っている間に荷物を預ける場所を手配しましょう。",
        ),
        expressions=(("check-in time", "チェックイン時間"), ("luggage room", "荷物預かり室")),
        p1=dict(
            bridge="まず、予約者の名前を伝えて予約を確認します。",
            meaning=(
                "Use this to identify a booking by the name it was made under.",
                "予約時に使った名前を伝えて、予約を確認する表現です。",
            ),
            rows=rows(
                ("{t}I have a reservation{/t} {t}under{/t} Tanaka.", "田中{t}の名前で{/t}{t}予約しています{/t}。", "I have|a reservation|under Tanaka."),
                ("{t}I have a reservation{/t} {t}under{/t} Sato.", "佐藤{t}の名前で{/t}{t}予約しています{/t}。", "I have|a reservation|under Sato."),
                ("{t}I have a reservation{/t} {t}under{/t} Mori.", "森{t}の名前で{/t}{t}予約しています{/t}。", "I have|a reservation|under Mori."),
                ("{t}I have a reservation{/t} {t}under{/t} Kato.", "加藤{t}の名前で{/t}{t}予約しています{/t}。", "I have|a reservation|under Kato."),
            ),
            reorder_criterion="booking statement / booking noun / name phrase",
            rule=(
                "Keep “under” with the booking name",
                "under と予約名をひとまとまりに",
                "Use “under + booking name” as one constituent after “I have a reservation.”",
                "I have a reservation のあとに、under + 予約名を一つのまとまりとして置きます。",
                "I have + a reservation + under booking name",
                "Identify the booking",
                "予約を特定する",
                ("a reservation · under Tanaka", "a reservation · under Sato"),
            ),
            write=("Whose name would your hotel booking be under?", "「I have a reservation under ___」を使って、予約名を伝えましょう。"),
            write_frame="I have a reservation under ___",
            write_script="Use “I have a reservation under ___” to tell the receptionist the booking name.",
            translate_hints=(("田中", "Tanaka"), ("佐藤", "Sato"), ("森", "Mori"), ("加藤", "Kato")),
        ),
        p2=dict(
            bridge="次に、部屋を待つ間の荷物について具体的に頼みます。",
            meaning=(
                "Use this to ask permission to leave an item in a place until a stated time.",
                "指定した時間まで、ある場所に物を置いてよいか尋ねる表現です。",
            ),
            rows=rows(
                ("{t}Can we leave{/t} our bags {t}here until{/t} three?", "3時{t}まで{/t}荷物を{t}ここに置いてもいいですか{/t}？", "Can we leave|our bags|here|until three?"),
                ("{t}Can we leave{/t} our suitcases {t}here until{/t} four?", "4時{t}まで{/t}スーツケースを{t}ここに置いてもいいですか{/t}？", "Can we leave|our suitcases|here|until four?"),
                ("{t}Can we leave{/t} our backpacks {t}here until{/t} noon?", "正午{t}まで{/t}リュックを{t}ここに置いてもいいですか{/t}？", "Can we leave|our backpacks|here|until noon?"),
                ("{t}Can we leave{/t} the stroller {t}here until{/t} six?", "6時{t}まで{/t}ベビーカーを{t}ここに置いてもいいですか{/t}？", "Can we leave|the stroller|here|until six?"),
            ),
            reorder_criterion="request frame / item / location / until-time phrase",
            rule=(
                "Place the item before the waiting time",
                "荷物を先、時間をあとに",
                "Name what you want to leave, then use “here until” before the pickup time.",
                "預ける物を言い、受け取る時刻の前に here until を置きます。",
                "Can we leave + item + here until + time?",
                "Arrange temporary storage",
                "一時預かりを頼む",
                ("our bags · here until three", "our suitcases · here until four"),
            ),
            write=("What would you need the hotel to store, and until when?", "「Can we leave ___ here until ___?」を使って、預ける物と時間を伝えましょう。"),
            write_frame="Can we leave ___ here until ___?",
            write_script="Use “Can we leave ___ here until ___?” to say what you want stored and until when.",
            translate_hints=(("バッグ", "bag"), ("スーツケース", "suitcase"), ("リュック", "backpack"), ("ベビーカー", "stroller")),
        ),
        scene_turns=(
            ("other", "Welcome. How can I help?", "いらっしゃいませ。ご用件を伺います。"),
            ("target", 1, 0),
            ("other", "Yes, but your room won't be ready until three.", "はい。ただ、お部屋の準備は3時になります。"),
            ("target", 2, 0),
            ("other", "Of course. I'll give you a receipt.", "もちろんです。お預かり証をお渡しします。"),
            ("me", "Great. Thank you.", "助かります。ありがとうございます。"),
            ("other", "You can collect your bags here after three.", "3時以降にこちらで荷物をお受け取りください。"),
        ),
        receptive=(
            ("Your room won't be ready until three.", "The room will be available at three", "部屋は3時に利用できる", "The room is ready now", "部屋はもう準備できている"),
            ("I'll give you a receipt.", "You will get proof that the bags were stored", "荷物を預けた証明を受け取る", "You need to pay for the room now", "今すぐ部屋代を払う必要がある"),
            ("You can collect your bags here after three.", "Pick up the bags at reception after three", "3時以降に受付で荷物を受け取る", "The bags will be put in your room", "荷物は部屋に運ばれる"),
            ("Check-in time starts at three.", "Room access begins at three", "部屋に入れるのは3時から", "The hotel closes at three", "ホテルは3時に閉まる"),
        ),
        live=(
            "What is the best way to spend time when you arrive too early for check-in?",
            "チェックインより早く着いたら、どう過ごすのがいちばんいいですか？",
            "I have a reservation under ___. Can we leave ___ here until ___?",
            "予約を確認し、荷物を預ける自分の言い方",
            "Have you ever arrived before check-in?",
            "先生はチェックイン前に着いたことがありますか？",
        ),
        tip=(
            "Choose “bags” or “luggage”",
            "bags と luggage の使い分け",
            "Use “bags” for separate pieces; use “luggage” for the collection as a whole.",
            "一つ一つを指すなら bags、荷物全体をまとめて指すなら luggage を使います。",
            ("Separate pieces", "一つ一つの荷物", "Can we leave our bags here?", "バッグをここに置いてもいいですか？"),
            ("The collection", "荷物全体", "Can we leave our luggage here?", "荷物をここに置いてもいいですか？"),
        ),
        transfer_title="Checking in for a museum tour",
        transfer_ja="美術館ツアーの受付で",
        transfer_role="Museum Attendant",
        transfer_turns=(
            ("other", "Welcome to the tour desk. May I have your name?", "ツアー受付へようこそ。お名前をお願いします。"),
            ("target", 1, 1),
            ("other", "I found your reservation. The tour starts at noon.", "ご予約を確認しました。ツアーは正午開始です。"),
            ("target", 2, 2),
            ("other", "Yes. I'll give you two claim tags for the backpacks.", "はい。リュック用の引換札を2枚お渡しします。"),
            ("me", "Perfect. Thank you.", "助かります。ありがとうございます。"),
            ("other", "Bring the tags back here after the tour.", "ツアー後にこの受付へ引換札をお持ちください。"),
        ),
        vocab=(
            "check-in time|チェックイン時間; luggage room|荷物預かり室; reservation|予約",
            "",
            "hotel|ホテル; bag|バッグ; suitcase|スーツケース; backpack|リュック; stroller|ベビーカー; room|部屋; can we leave|置いてもいいですか; Tanaka|田中; Sato|佐藤; Mori|森; Kato|加藤",
            "collect|受け取る; claim tag|引換札; receipt|お預かり証",
        ),
    ),
    8: dict(
        slug="get-a-hotel-problem-fixed",
        title="Get a hotel problem fixed",
        ko="호텔 문제 해결 요청하기",
        ja="ホテルの問題を直してもらう",
        role="Receptionist",
        scene="Calling reception from a hot hotel room",
        scene_ja="暑いホテルの部屋から受付に電話する",
        situation="冷房の故障を具体的に伝え、解決しない場合は部屋の変更を頼みます。",
        goal=("Describe the malfunction and ask for a specific remedy.", "故障の内容を伝え、具体的な対応を頼みましょう。"),
        expressions=(("send someone up", "スタッフを部屋へ行かせる"), ("change rooms", "部屋を替える")),
        p1=dict(
            bridge="まず、何が使えないのかを短く伝えます。",
            meaning=("Use this to state that a device or facility is not functioning.", "機器や設備が動かないことを伝える表現です。"),
            rows=rows(
                ("The air conditioning {t}doesn't work{/t}.", "エアコンが{t}動きません{/t}。", "The air conditioning|doesn't work."),
                ("The shower {t}doesn't work{/t}.", "シャワーが{t}使えません{/t}。", "The shower|doesn't work."),
                ("The key card {t}doesn't work{/t}.", "キーカードが{t}使えません{/t}。", "The key card|doesn't work."),
                ("The bedside lamp {t}doesn't work{/t}.", "ベッド脇のランプが{t}つきません{/t}。", "The bedside lamp|doesn't work."),
            ),
            omit_reorder=True,
            omit_rule=True,
            rule=(
                "Name the faulty thing first",
                "故障している物を先に",
                "Put the faulty item before the intact phrase “doesn't work.”",
                "故障している物を先に言い、doesn't work はひとまとまりで続けます。",
                "faulty item + doesn't work",
                "Report the malfunction",
                "故障を伝える",
                ("The shower · doesn't work", "The key card · doesn't work"),
            ),
            write=("What hotel-room problem would you report first?", "「___ doesn't work」を使って、故障している物を伝えましょう。"),
            write_frame="___ doesn't work",
            write_script="Use “___ doesn't work” to identify the broken item.",
            translate_hints=(("エアコン", "air conditioning"), ("シャワー", "shower"), ("キーカード", "key card"), ("ベッド脇のランプ", "bedside lamp")),
        ),
        p2=dict(
            bridge="直らない場合は、必要な解決策をはっきり頼みます。",
            meaning=("Use this to ask whether your group can take a practical next step.", "自分たちが具体的な次の行動を取れるか尋ねる表現です。"),
            rows=rows(
                ("{t}Can we{/t} change rooms?", "部屋を替えることは{t}できますか{/t}？", "Can we|change rooms?"),
                ("{t}Can we{/t} move to another room?", "別の部屋へ移ることは{t}できますか{/t}？", "Can we|move to|another room?"),
                ("{t}Can we{/t} get another key card?", "別のキーカードをもらうことは{t}できますか{/t}？", "Can we|get|another key card?"),
                ("{t}Can we{/t} get a fan?", "扇風機を借りることは{t}できますか{/t}？", "Can we|get|a fan?"),
            ),
            omit_reorder=True,
            omit_rule=True,
            rule=(
                "Use “Can we” for a shared solution",
                "一緒の解決策なら Can we",
                "Keep “Can we” together, then name the action that would solve the problem.",
                "Can we をひとまとまりにし、そのあとに問題を解決する行動を続けます。",
                "Can we + solution?",
                "Request the remedy",
                "解決策を頼む",
                ("Can we · change rooms?", "Can we · get another key card?"),
            ),
            write=("What solution would you ask the hotel for?", "「Can we ___?」を使って、希望する解決策を頼みましょう。"),
            write_frame="Can we ___?",
            write_script="Use “Can we ___?” to ask for the solution you want.",
            translate_hints=(("部屋", "room"), ("別の部屋", "room"), ("キーカード", "key card"), ("扇風機", "fan")),
        ),
        scene_turns=(
            ("other", "Reception. How can I help?", "フロントです。ご用件を伺います。"),
            ("target", 1, 0),
            ("other", "I'll send someone up to look at it.", "スタッフを部屋へ向かわせて確認します。"),
            ("me", "Thank you, but the room is getting very hot.", "ありがとうございます。ただ、部屋がかなり暑くなっています。"),
            ("other", "It should take about ten minutes.", "10分ほどで確認できるはずです。"),
            ("target", 2, 0),
            ("other", "Yes. I'll hold another room for you.", "はい。別のお部屋を確保します。"),
            ("me", "That would be great. Thank you.", "助かります。ありがとうございます。"),
        ),
        receptive=(
            ("I'll send someone up to look at it.", "A staff member will come to inspect the problem", "スタッフが問題を確認しに来る", "You need to bring the unit downstairs", "機器を下の階へ持っていく必要がある"),
            ("I'll hold another room for you.", "A different room will be kept available", "別の部屋を確保してくれる", "Your current room will be cleaned", "今の部屋を掃除してくれる"),
            ("The engineer will be there in ten minutes.", "Help should arrive in ten minutes", "10分で担当者が来る", "The repair will take ten hours", "修理に10時間かかる"),
            ("There is no extra charge for the move.", "Changing rooms will not cost more", "部屋を替えても追加料金はない", "The new room costs more", "新しい部屋は料金が高い"),
        ),
        live=(
            "Which hotel-room problem would bother you most, and why?",
            "ホテルの部屋では、どんな問題がいちばん困りますか？なぜですか？",
            "The ___ doesn't work. Can we ___?",
            "故障と希望する解決策",
            "Have you ever had a problem with a hotel room?",
            "先生はホテルの部屋で困ったことがありますか？",
        ),
        tip=(
            "Describe a general fault or a problem right now",
            "一般的な故障か、今の不具合か",
            "Both are natural. “doesn't work” states the fault; “isn't working” focuses on the current situation.",
            "どちらも自然です。doesn't work は故障を、isn't working は今起きている不具合を強調します。",
            ("The fault", "故障そのもの", "The air conditioning doesn't work.", "エアコンが動きません。"),
            ("Right now", "今の不具合", "The air conditioning isn't working.", "エアコンが今動いていません。"),
        ),
        transfer_title="At a rental-apartment office",
        transfer_ja="貸しアパートの受付で",
        transfer_role="Property Manager",
        transfer_turns=(
            ("other", "How can I help with the apartment?", "アパートについて、どうされましたか？"),
            ("target", 1, 2),
            ("other", "I can reset the card, but the system is offline.", "カードをリセットできますが、今はシステムが停止しています。"),
            ("target", 2, 1),
            ("other", "Yes. Apartment 12 is ready.", "はい。12号室なら準備できています。"),
            ("me", "Great. We'll move our bags now.", "助かります。今から荷物を移します。"),
            ("other", "Here is the new key card.", "新しいキーカードです。"),
        ),
        vocab=(
            "air conditioning|エアコン; doesn't work|動かない",
            "",
            "hotel|ホテル; room|部屋; shower|シャワー; key card|キーカード; bedside lamp|ベッド脇のランプ; fan|扇風機; can we|できますか",
            "send someone up|スタッフを部屋へ行かせる; hold another room|別の部屋を確保する; malfunction|故障; remedy|対応",
        ),
    ),
    9: dict(
        slug="order-with-a-dietary-restriction",
        title="Order with a dietary restriction",
        ko="식이 제한을 알리고 주문하기",
        ja="食事制限を伝えて注文する",
        role="Server",
        scene="A restaurant with an unfamiliar menu",
        scene_ja="メニューがよく分からないレストラン",
        situation="アレルギーを明確に伝え、おすすめの料理に原因食材が入っていないか確認します。",
        goal=("State your dietary restriction and confirm that a recommendation is safe.", "食事制限を伝え、おすすめの料理が安全か確認しましょう。"),
        expressions=(("nut-free", "ナッツ不使用"), ("contains dairy", "乳製品が入っている")),
        p1=dict(
            bridge="最初に、避けなければならない食材をはっきり伝えます。",
            meaning=("Use this fixed phrase to name a real food allergy before ordering.", "注文前に、実際の食物アレルギーを伝える定型表現です。"),
            rows=rows(
                ("{t}I'm allergic to{/t} nuts.", "ナッツに{t}アレルギーがあります{/t}。", "I'm|allergic to|nuts."),
                ("{t}I'm allergic to{/t} shellfish.", "甲殻類に{t}アレルギーがあります{/t}。", "I'm|allergic to|shellfish."),
                ("{t}I'm allergic to{/t} dairy.", "乳製品に{t}アレルギーがあります{/t}。", "I'm|allergic to|dairy."),
                ("{t}I'm allergic to{/t} eggs.", "卵に{t}アレルギーがあります{/t}。", "I'm|allergic to|eggs."),
            ),
            omit_reorder=True,
            rule=(
                "Keep the allergy phrase intact",
                "アレルギーの表現はひとまとまり",
                "Treat “I'm allergic to” as one survival chunk and add only the allergen.",
                "I'm allergic to を一つのサバイバル表現として覚え、原因食材だけを続けます。",
                "I'm allergic to + allergen",
                "State the safety need",
                "安全上の必要を伝える",
                ("I'm allergic to · nuts", "I'm allergic to · shellfish"),
            ),
            write=(
                "If you have a real allergy, name it; otherwise, use “I don't eat ___.”",
                "実際のアレルギーがある場合だけ伝え、ない場合は I don't eat ___ を使いましょう。",
            ),
            write_scaffold="Real allergy: I'm allergic to ___. / Otherwise: I don't eat ___.",
            write_frame="I'm allergic to ___",
            write_script="If you have a real allergy, use “I'm allergic to ___.” Otherwise, use “I don't eat ___.”",
            translate_hints=(("ナッツ", "nuts"), ("甲殻類", "shellfish"), ("乳製品", "dairy"), ("卵", "eggs")),
        ),
        p2=dict(
            bridge="次に、おすすめの料理にその食材が入っていないか確認します。",
            meaning=("Use this to check whether a dish includes any amount of an ingredient.", "料理にその食材が少しでも含まれているか確認する表現です。"),
            rows=rows(
                ("{t}Does it contain any{/t} nuts?", "ナッツは{t}入っていますか{/t}？", "Does it contain|any nuts?"),
                ("{t}Does it contain any{/t} shellfish?", "甲殻類は{t}入っていますか{/t}？", "Does it contain|any shellfish?"),
                ("{t}Does it contain any{/t} dairy?", "乳製品は{t}入っていますか{/t}？", "Does it contain|any dairy?"),
                ("{t}Does it contain any{/t} eggs?", "卵は{t}入っていますか{/t}？", "Does it contain|any eggs?"),
            ),
            omit_reorder=True,
            rule=(
                "Put the ingredient after “any”",
                "食材は any のあと",
                "Keep the question frame together and place the ingredient at the end.",
                "質問の形をひとまとまりにし、確認する食材を最後に置きます。",
                "Does it contain any + ingredient?",
                "Check the dish",
                "料理を確認する",
                ("any nuts?", "any dairy?"),
            ),
            write=("Which ingredient would you check for?", "「Does it contain any ___?」を使って、確認したい食材を尋ねましょう。"),
            write_frame="Does it contain any ___?",
            write_script="Use “Does it contain any ___?” to ask about an ingredient.",
            translate_hints=(("ナッツ", "nuts"), ("甲殻類", "shellfish"), ("乳製品", "dairy"), ("卵", "eggs")),
        ),
        scene_turns=(
            ("other", "Are you ready to order?", "ご注文はお決まりですか？"),
            ("target", 1, 0),
            ("other", "Then I'd recommend the fish.", "それでしたら、魚料理がおすすめです。"),
            ("target", 2, 0),
            ("other", "No nuts, but the sauce contains dairy.", "ナッツは入っていませんが、ソースには乳製品が入っています。"),
            ("me", "Dairy is fine for me. I'll have the fish.", "乳製品は大丈夫です。魚料理をお願いします。"),
            ("other", "I'll mark the allergy on your order.", "ご注文にアレルギー情報を記載します。"),
        ),
        receptive=(
            ("I'd recommend the fish.", "The server suggests the fish", "店員は魚料理をすすめている", "The fish is unavailable", "魚料理は売り切れている"),
            ("The sauce contains dairy.", "There is dairy in the sauce", "ソースに乳製品が入っている", "The sauce is dairy-free", "ソースは乳製品不使用である"),
            ("I'll mark the allergy on your order.", "The kitchen will be told about the allergy", "厨房にアレルギー情報が伝わる", "The dish will be more expensive", "料理の値段が上がる"),
            ("The kitchen uses separate pans.", "The food is cooked in different cookware", "別の調理器具で調理する", "All dishes use the same pan", "すべて同じフライパンで調理する"),
        ),
        live=(
            "When you try a new restaurant, what do you check before ordering?",
            "初めてのレストランでは、注文前に何を確認しますか？",
            "Real allergy: I'm allergic to ___. / Otherwise: I don't eat ___. Then ask: Does it contain any ___?",
            "安全に使えるほうを選び、食材を確認",
            "Is there any ingredient you usually avoid?",
            "先生は普段避けている食材がありますか？",
        ),
        tip=(
            "Use “allergic” only for an allergy",
            "allergic は実際のアレルギーに",
            "Use “I'm allergic to” for a medical allergy; use “I don't eat” for a preference or choice.",
            "医学的なアレルギーには I'm allergic to、好みや選択で食べない場合は I don't eat を使います。",
            ("Medical allergy", "医学的なアレルギー", "I'm allergic to nuts.", "ナッツにアレルギーがあります。"),
            ("Preference or choice", "好み・選択", "I don't eat nuts.", "ナッツは食べません。"),
        ),
        transfer_title="At a hotel breakfast buffet",
        transfer_ja="ホテルの朝食会場で",
        transfer_role="Buffet Attendant",
        transfer_turns=(
            ("other", "Would you like some soup?", "スープはいかがですか？"),
            ("target", 1, 3),
            ("other", "Let me check the ingredient list.", "原材料表を確認します。"),
            ("target", 2, 3),
            ("other", "It doesn't contain eggs, but I'll check with the kitchen about cross-contact.", "卵は入っていませんが、交差接触について厨房に確認します。"),
            ("me", "Thank you. I'll wait for the kitchen's answer.", "ありがとうございます。厨房の確認を待ちます。"),
            ("other", "I'll come back as soon as they confirm.", "確認でき次第お戻りします。"),
        ),
        vocab=(
            "allergic|アレルギーがある; shellfish|甲殻類; dairy|乳製品; nut-free|ナッツ不使用; contain|含む",
            "",
            "restaurant|レストラン; nuts|ナッツ; fish|魚; sauce|ソース; eggs|卵; I don't eat|食べません",
            "recommend|すすめる; ingredient list|原材料表; separate pans|別の調理器具; cross-contact|交差接触",
        ),
    ),
    10: dict(
        slug="correct-an-order-politely",
        title="Correct an order politely",
        ko="주문 오류 정중하게 바로잡기",
        ja="注文の間違いを丁寧に直す",
        role="Server",
        scene="A café after the wrong drink arrives",
        scene_ja="違う飲み物が届いたカフェ",
        situation="注文した物と届いた物を対比し、正しい飲み物への交換を頼みます。",
        goal=("Identify the order error and ask for the correct item.", "注文の間違いを伝え、正しい品への交換を頼みましょう。"),
        expressions=(("the wrong order", "間違った注文"), ("no problem", "問題ありません")),
        p1=dict(
            bridge="まず、注文した物と届いた物を短く対比します。",
            meaning=("Use this fixed contrast to identify what you ordered and reject the item you received.", "注文した物を示し、届いた別の物ではないと伝える定型表現です。"),
            rows=rows(
                ("Sorry, {t}I ordered{/t} the iced coffee, {t}not{/t} the hot one.", "すみません、{t}注文したのは{/t}アイスコーヒーで、ホットコーヒー{t}ではありません{/t}。", "Sorry,|I ordered|the iced coffee,|not the hot one."),
                ("Sorry, {t}I ordered{/t} the tea, {t}not{/t} the coffee.", "すみません、{t}注文したのは{/t}紅茶で、コーヒー{t}ではありません{/t}。", "Sorry,|I ordered|the tea,|not the coffee."),
                ("Sorry, {t}I ordered{/t} the soup, {t}not{/t} the salad.", "すみません、{t}注文したのは{/t}スープで、サラダ{t}ではありません{/t}。", "Sorry,|I ordered|the soup,|not the salad."),
                ("Sorry, {t}I ordered{/t} sparkling water, {t}not{/t} still water.", "すみません、{t}注文したのは{/t}炭酸水で、普通の水{t}ではありません{/t}。", "Sorry,|I ordered|sparkling water,|not still water."),
            ),
            reorder_criterion="softener / order lead-in / correct item / not + received item",
            omit_rule=True,
            rule=(
                "Put the correct item before “not”",
                "正しい品を not の前に",
                "Name the item you ordered first, then put the incorrect item after “not.”",
                "先に注文した品を言い、間違って届いた品を not のあとに置きます。",
                "I ordered + correct item, not + wrong item",
                "Correct the contrast",
                "対比を直す",
                ("the iced coffee · not the hot one", "the tea · not the coffee"),
            ),
            write=("What order mix-up would you correct?", "「I ordered ___, not ___」を使って、注文の間違いを直しましょう。"),
            write_frame="I ordered ___, not ___",
            write_script="Use “I ordered ___, not ___” to correct the order.",
            translate_hints=(("アイスコーヒー", "iced coffee"), ("紅茶", "tea"), ("スープ", "soup"), ("炭酸水", "sparkling water")),
        ),
        p2=dict(
            bridge="次に、本当にほしい品を instead で頼み直します。",
            meaning=("Use this to request one replacement in place of the item you received.", "届いた品の代わりに、希望する品を一つ頼む表現です。"),
            rows=rows(
                ("{t}Can I have{/t} the iced one {t}instead{/t}?", "{t}代わりに{/t}アイスのほうを{t}いただけますか{/t}？", "Can I have|the iced one|instead?"),
                ("{t}Can I have{/t} the tea {t}instead{/t}?", "{t}代わりに{/t}紅茶を{t}いただけますか{/t}？", "Can I have|the tea|instead?"),
                ("{t}Can I have{/t} the soup {t}instead{/t}?", "{t}代わりに{/t}スープを{t}いただけますか{/t}？", "Can I have|the soup|instead?"),
                ("{t}Can I have{/t} sparkling water {t}instead{/t}?", "{t}代わりに{/t}炭酸水を{t}いただけますか{/t}？", "Can I have|sparkling water|instead?"),
            ),
            reorder_criterion="replacement request / desired item / instead",
            rule=(
                "Put “instead” at the end",
                "instead は最後に",
                "State the replacement after “Can I have” and place “instead” at the end.",
                "Can I have のあとに交換してほしい品を言い、instead を最後に置きます。",
                "Can I have + replacement + instead?",
                "Request the replacement",
                "交換を頼む",
                ("the iced one · instead", "the soup · instead"),
            ),
            write=("What would you ask for instead?", "「Can I have ___ instead?」を使って、代わりに欲しい物を頼みましょう。"),
            write_frame="Can I have ___ instead?",
            write_script="Use “Can I have ___ instead?” to ask for the replacement you want.",
            translate_hints=(("アイスコーヒー", "iced coffee"), ("紅茶", "tea"), ("スープ", "soup"), ("普通の水", "still water")),
        ),
        scene_turns=(
            ("other", "Here's your hot coffee.", "ホットコーヒーです。"),
            ("target", 1, 0),
            ("other", "I'm sorry—I picked up the wrong ticket.", "申し訳ありません。違う伝票を取ってしまいました。"),
            ("target", 2, 0),
            ("other", "Absolutely. It'll just take a minute.", "もちろんです。1分ほどお待ちください。"),
            ("me", "Thank you.", "ありがとうございます。"),
            ("other", "I'll bring it to your table.", "お席までお持ちします。"),
        ),
        receptive=(
            ("I picked up the wrong ticket.", "The server used another order slip", "店員は別の注文票を取った", "The café has lost your payment", "カフェは支払い記録をなくした"),
            ("It'll just take a minute.", "The replacement should be ready soon", "交換品はすぐにできる", "The café closes in one minute", "カフェは1分後に閉まる"),
            ("I'll bring it to your table.", "The server will deliver the replacement", "店員が交換品を席まで運ぶ", "You must order again at the counter", "カウンターで注文し直す必要がある"),
            ("No problem. I'll remake it.", "The drink will be prepared again", "飲み物を作り直してくれる", "The same drink will be reheated", "同じ飲み物を温め直す"),
        ),
        live=(
            "Which would bother you more: the wrong drink or the wrong meal?",
            "飲み物と食事なら、どちらを間違えられるほうが困りますか？",
            "I ordered ___, not ___. Can I have ___ instead?",
            "自分なら伝える注文と交換品",
            "Have you ever received the wrong order?",
            "先生は注文を間違えられたことがありますか？",
        ),
        tip=(
            "Open with “Sorry” or “Actually”",
            "Sorry と Actually の使い分け",
            "Use “Sorry” to flag a problem politely; use “Actually” for a softer factual correction.",
            "問題を丁寧に伝えるなら Sorry、事実をやわらかく訂正するなら Actually を使います。",
            ("Flagging a problem", "問題を伝える", "Sorry, I ordered the iced coffee.", "すみません、アイスコーヒーを注文しました。"),
            ("Correcting a detail", "情報を訂正する", "Actually, I ordered the iced coffee.", "実は、アイスコーヒーを注文しました。"),
        ),
        transfer_title="At a deli counter",
        transfer_ja="デリのカウンターで",
        transfer_role="Deli Worker",
        transfer_turns=(
            ("other", "Here's your salad.", "サラダです。"),
            ("target", 1, 2),
            ("other", "You're right. I read the order incorrectly.", "おっしゃる通りです。注文を読み間違えました。"),
            ("target", 2, 2),
            ("other", "Of course. The soup is ready now.", "もちろんです。スープはすぐにお渡しできます。"),
            ("me", "Great. Thank you for fixing it.", "助かります。直していただきありがとうございます。"),
            ("other", "Here you are. Sorry about the mix-up.", "どうぞ。間違えて申し訳ありませんでした。"),
        ),
        vocab=(
            "iced coffee|アイスコーヒー; sparkling water|炭酸水; still water|普通の水; ordered|注文した",
            "instead|その代わり|CORE-14",
            "coffee|コーヒー; tea|紅茶; soup|スープ; salad|サラダ; can I have|いただけますか",
            "wrong ticket|違う伝票; remake|作り直す; mix-up|取り違え",
        ),
    ),
    11: dict(
        slug="return-something-that-does-not-work",
        title="Return something that does not work",
        ko="고장 난 물건 반품하기",
        ja="動かない商品を返品する",
        role="Clerk",
        scene="A shop with a faulty travel adapter",
        scene_ja="故障した旅行用アダプターを持ってきた店",
        situation="購入時期と故障を説明し、動作確認した交換品を頼みます。",
        goal=("Explain the fault and request an exchange or refund.", "故障を説明し、交換または返金を頼みましょう。"),
        expressions=(("proof of purchase", "購入証明"), ("refund", "返金")),
        p1=dict(
            bridge="まず、いつ買った物にどんな問題があるのか説明します。",
            meaning=("Use this to connect a recent purchase with the problem you discovered.", "最近買った物と、見つかった問題をつなげて説明する表現です。"),
            rows=rows(
                ("{t}I bought{/t} this yesterday, {t}but{/t} it doesn't work.", "これは昨日{t}買いました{/t}{t}が{/t}、動きません。", "I bought this|yesterday,|but it doesn't work."),
                ("{t}I bought{/t} this charger this morning, {t}but{/t} it won't charge my phone.", "この充電器は今朝{t}買いました{/t}{t}が{/t}、携帯を充電できません。", "I bought this charger|this morning,|but it won't charge my phone."),
                ("{t}I bought{/t} this umbrella yesterday, {t}but{/t} it won't open.", "この傘は昨日{t}買いました{/t}{t}が{/t}、開きません。", "I bought this umbrella|yesterday,|but it won't open."),
                ("{t}I bought{/t} these headphones last week, {t}but{/t} one side is silent.", "このヘッドホンは先週{t}買いました{/t}{t}が{/t}、片方から音が出ません。", "I bought these headphones|last week,|but one side is silent."),
            ),
            reorder_criterion="purchase with object / purchase time / contrasting fault",
            rule=(
                "Connect the purchase and the fault with “but”",
                "購入と故障を but でつなぐ",
                "State what and when you bought it, then use “but” before the problem.",
                "何をいつ買ったかを伝え、問題の前に but を置きます。",
                "I bought + item/time, but + fault",
                "Explain why you returned",
                "返品理由を伝える",
                ("this yesterday · but it doesn't work", "this umbrella yesterday · but it won't open"),
            ),
            write=("What faulty purchase would you bring back?", "「I bought ___, but ___」を使って、買った物と問題を伝えましょう。"),
            write_frame="I bought ___, but ___",
            write_script="Use “I bought ___, but ___” to say what you bought and what is wrong.",
            translate_hints=(("昨日", "yesterday"), ("充電器", "charger"), ("傘", "umbrella"), ("ヘッドホン", "headphones")),
        ),
        p2=dict(
            bridge="次に、希望する交換先を具体的に伝えます。",
            meaning=("Use this to ask to replace one item with a specific alternative.", "ある商品を、具体的な別の商品に交換してもらえるか尋ねる表現です。"),
            rows=rows(
                ("{t}Can I exchange{/t} it {t}for{/t} another one?", "別の物{t}と{/t}{t}交換できますか{/t}？", "Can I exchange|it|for another one?"),
                ("{t}Can I exchange{/t} this charger {t}for{/t} a new one?", "この充電器を新品{t}と{/t}{t}交換できますか{/t}？", "Can I exchange|this charger|for a new one?"),
                ("{t}Can I exchange{/t} this umbrella {t}for{/t} a larger one?", "この傘をもっと大きい物{t}と{/t}{t}交換できますか{/t}？", "Can I exchange|this umbrella|for a larger one?"),
                ("{t}Can I exchange{/t} these headphones {t}for{/t} a different pair?", "このヘッドホンを別の物{t}と{/t}{t}交換できますか{/t}？", "Can I exchange|these headphones|for a different pair?"),
            ),
            reorder_criterion="exchange request / returned item / for + replacement",
            attached_prepositions=("for",),
            rule=(
                "Put the replacement after “for”",
                "交換先は for のあと",
                "Name the item you are returning first and the replacement after “for.”",
                "返品する品を先に言い、交換してほしい品を for のあとに置きます。",
                "exchange + returned item + for + replacement",
                "Name both sides of the exchange",
                "交換する二つを示す",
                ("exchange it · for another one", "exchange this charger · for a new one"),
            ),
            write=("What replacement would solve your problem?", "「Can I exchange ___ for ___?」を使って、交換したい物を伝えましょう。"),
            write_frame="Can I exchange ___ for ___?",
            write_script="Use “Can I exchange ___ for ___?” to say which exchange you want.",
            translate_hints=(("別の物", "another one"), ("充電器", "charger"), ("傘", "umbrella"), ("ヘッドホン", "headphones")),
        ),
        scene_turns=(
            ("other", "How can I help?", "ご用件を伺います。"),
            ("target", 1, 0),
            ("other", "Do you have the receipt?", "レシートはお持ちですか？"),
            ("me", "Yes, here it is.", "はい、こちらです。"),
            ("other", "We can exchange it or give you a refund.", "交換または返金ができます。"),
            ("target", 2, 0),
            ("other", "Yes. Let me test the replacement first.", "はい。まず交換品の動作を確認します。"),
        ),
        receptive=(
            ("Do you have the receipt?", "The clerk wants proof of purchase", "店員は購入証明を求めている", "The clerk wants the product manual", "店員は商品の説明書を求めている"),
            ("We can exchange it or give you a refund.", "You may choose a replacement or your money back", "交換か返金を選べる", "Only store credit is available", "店内クレジットしか選べない"),
            ("Let me test the replacement first.", "The clerk will check the new item before handing it over", "渡す前に交換品を確認する", "You must repair the old item yourself", "古い商品を自分で直す必要がある"),
            ("The refund will go back to your card.", "The money will be returned to the payment card", "支払いに使ったカードへ返金される", "You will receive cash immediately", "すぐに現金で返金される"),
        ),
        live=(
            "Would you prefer an exchange or a refund, and why?",
            "交換と返金なら、どちらがいいですか？なぜですか？",
            "I bought ___, but ___. Can I exchange ___ for ___?",
            "故障の説明と希望する交換",
            "Have you ever returned something that didn't work?",
            "先生は動かなかった物を返品したことがありますか？",
        ),
        tip=(
            "Name the fault more precisely",
            "故障をより具体的に伝える",
            "Use “doesn't work” for a general fault; use “won't turn on” when power is the exact problem.",
            "一般的な故障なら doesn't work、電源が入らない問題なら won't turn on を使います。",
            ("General fault", "一般的な故障", "It doesn't work.", "動きません。"),
            ("Power problem", "電源の問題", "It won't turn on.", "電源が入りません。"),
        ),
        transfer_title="At a station kiosk",
        transfer_ja="駅の売店で",
        transfer_role="Kiosk Clerk",
        transfer_turns=(
            ("other", "Is there a problem with the umbrella?", "傘に問題がありますか？"),
            ("target", 1, 2),
            ("other", "I see. This one is damaged.", "確認しました。こちらは壊れていますね。"),
            ("target", 2, 2),
            ("other", "Yes. I'll check that the larger one opens properly.", "はい。大きいほうがきちんと開くか確認します。"),
            ("me", "Thank you. That solves the problem.", "ありがとうございます。これで解決です。"),
            ("other", "Here is the replacement and your new receipt.", "交換品と新しいレシートです。"),
        ),
        vocab=(
            "proof of purchase|購入証明; refund|返金; replacement|交換品; exchange|交換する",
            "bought|buy の過去形|CORE-32; doesn't work|動かない|CTX-8",
            "receipt|レシート; charger|充電器; umbrella|傘; headphones|ヘッドホン; yesterday|昨日; another one|別の物",
            "store credit|店内クレジット; payment card|支払いカード; travel adapter|旅行用アダプター",
        ),
    ),
    12: dict(
        slug="change-a-booking-without-losing-it",
        title="Change a booking without losing it",
        ko="예약을 유지하며 시간 변경하기",
        ja="予約を残したまま時間を変更する",
        role="Host",
        scene="Calling a restaurant about a dinner reservation",
        scene_ja="夕食の予約についてレストランに電話する",
        situation="夕食の予約を1時間遅らせ、変更後の人数と時刻を確認します。",
        goal=("Request a booking change and confirm the revised details.", "予約の変更を頼み、変更後の内容を確認しましょう。"),
        expressions=(("under the name", "〜の名前で"), ("change the booking", "予約を変更する")),
        p1=dict(
            bridge="まず、今の予約を取り消さずに希望時刻へ動かします。",
            meaning=("Use this to ask whether an existing booking can be moved to a new time or date.", "今ある予約を、新しい時刻や日付へ動かせるか尋ねる表現です。"),
            rows=rows(
                ("{t}Can we move{/t} our reservation {t}to{/t} eight?", "予約を8時{t}に{/t}{t}変更できますか{/t}？", "Can we move|our reservation|to eight?"),
                ("{t}Can we move{/t} our booking {t}to{/t} Friday?", "予約を金曜日{t}に{/t}{t}変更できますか{/t}？", "Can we move|our booking|to Friday?"),
                ("{t}Can we move{/t} our reservation {t}to{/t} seven-thirty?", "予約を7時30分{t}に{/t}{t}変更できますか{/t}？", "Can we move|our reservation|to seven-thirty?"),
                ("{t}Can we move{/t} the tour {t}to{/t} Saturday?", "ツアーを土曜日{t}に{/t}{t}変更できますか{/t}？", "Can we move|the tour|to Saturday?"),
            ),
            reorder_criterion="change request / booking item / new time or date",
            rule=(
                "Put the new time after “to”",
                "新しい時刻は to のあと",
                "Name the existing booking first and place its new time or date after “to.”",
                "今の予約を先に言い、新しい時刻や日付を to のあとに置きます。",
                "Can we move + booking + to + new time?",
                "Keep the booking, change the slot",
                "予約を残して枠を変える",
                ("our reservation · to eight", "our booking · to Friday"),
            ),
            write=("Which booking would you move, and to when?", "「Can we move ___ to ___?」を使って、変更する予約と新しい日時を伝えましょう。"),
            write_frame="Can we move ___ to ___?",
            write_script="Use “Can we move ___ to ___?” to name the booking and its new time or date.",
            translate_hints=(("予約", "reservation"), ("予約", "booking"), ("予約", "reservation"), ("ツアー", "tour")),
        ),
        p2=dict(
            bridge="変更したあと、人数がそのままか確認します。",
            meaning=("Use this to confirm that a booking detail remains unchanged after the move.", "予約を動かしたあとも、ある情報が変わっていないか確認する表現です。"),
            rows=rows(
                ("{t}Is it still for{/t} four people?", "人数は{t}今も4人のままですか{/t}？", "Is it|still|for four people?"),
                ("{t}Is it still for{/t} two people?", "人数は{t}今も2人のままですか{/t}？", "Is it|still|for two people?"),
                ("{t}Is it still for{/t} six people?", "人数は{t}今も6人のままですか{/t}？", "Is it|still|for six people?"),
                ("{t}Is it still for{/t} three people?", "人数は{t}今も3人のままですか{/t}？", "Is it|still|for three people?"),
            ),
            reorder_criterion="booking reference / unchanged-state marker / party size",
            rule=(
                "Use “still” for an unchanged detail",
                "変わっていない情報には still",
                "Build the question in three parts: “Is it” + “still” + “for four people?”",
                "Is it + still + for four people? の3つのまとまりで質問を作ります。",
                "Is it + still + for four people?",
                "Confirm the party size",
                "人数を確認する",
                ("Is it · still · for four people?", "Is it · still · for two people?"),
            ),
            write=("How many people would you confirm?", "「Is it still for ___ people?」を使って、予約人数を確認しましょう。"),
            write_frame="Is it still for ___ people?",
            write_script="Use “Is it still for ___ people?” to confirm the number of people.",
            translate_hints=(("4人", "four people"), ("2人", "two people"), ("6人", "six people"), ("3人", "three people")),
        ),
        scene_turns=(
            ("other", "Good evening. How can I help?", "こんばんは。ご用件を伺います。"),
            ("me", "I have a reservation under Tanaka at seven.", "7時に田中の名前で予約しています。"),
            ("other", "Yes, I found it.", "はい、確認できました。"),
            ("target", 1, 0),
            ("other", "I can do eight-fifteen, but not eight.", "8時は難しいですが、8時15分なら可能です。"),
            ("me", "Eight-fifteen works for us.", "8時15分で大丈夫です。"),
            ("target", 2, 0),
            ("other", "Yes—four people at eight-fifteen. I've changed it to eight-fifteen.", "はい、8時15分に4名様です。予約を8時15分に変更しました。"),
        ),
        receptive=(
            ("I found it.", "The host located the reservation", "店員は予約を確認できた", "The host canceled the reservation", "店員は予約を取り消した"),
            ("I can do eight-fifteen, but not eight.", "8:15 is available, but 8:00 is not", "8時15分は空いているが、8時は空いていない", "Both 8:00 and 8:15 are available", "8時と8時15分の両方が空いている"),
            ("The kitchen closes at nine-thirty.", "Orders must be placed before 9:30", "9時30分より前に注文する必要がある", "The restaurant opens at 9:30", "レストランは9時30分に開く"),
            ("I've changed it to eight-fifteen.", "The new booking time is confirmed", "新しい予約時刻が確定した", "The booking is still at seven", "予約はまだ7時のままである"),
        ),
        live=(
            "Which booking detail do you always double-check, and why?",
            "予約では、どの情報を必ず再確認しますか？なぜですか？",
            "Can we move ___ to ___? Is it still for ___ people?",
            "自分なら変更して確認する内容",
            "What about you—which detail do you check first?",
            "先生はどの情報を最初に確認しますか？",
        ),
        tip=(
            "Use “move” neutrally or “push back” for later",
            "move と push back の使い分け",
            "Use “move” for either direction; use “push back” when the new time is later.",
            "前後どちらの変更にも move、遅い時刻への変更には push back を使います。",
            ("Either direction", "前後どちらでも", "Can we move our reservation to eight?", "予約を8時に変更できますか？"),
            ("Specifically later", "遅い時刻へ", "Can we push our reservation back to eight?", "予約を8時まで遅らせられますか？"),
        ),
        transfer_title="Changing a walking-tour booking",
        transfer_ja="ウォーキングツアーの予約変更",
        transfer_role="Tour Agent",
        transfer_turns=(
            ("other", "I found your Thursday walking tour.", "木曜日のウォーキングツアーを確認しました。"),
            ("target", 1, 1),
            ("other", "Yes. The Friday tour starts at ten.", "はい。金曜日のツアーは10時開始です。"),
            ("target", 2, 0),
            ("other", "Yes—Friday at ten for four people.", "はい、金曜日の10時に4名様です。"),
            ("me", "Perfect. Please make that change.", "完璧です。その内容で変更してください。"),
            ("other", "Done. I'll email the new confirmation.", "変更しました。新しい確認メールをお送りします。"),
        ),
        vocab=(
            "",
            "still|まだ・予定どおり|CORE-29; reservation|予約|CTX-7",
            "restaurant|レストラン; people|人; Friday|金曜日; Saturday|土曜日; tour|ツアー; can we move|変更できますか; booking|予約; four people|4人; two people|2人; six people|6人; three people|3人",
            "available time|空いている時刻; confirmation|確認メール; booking change|予約変更; party size|予約人数; push back|後ろへずらす",
        ),
    ),
}


AUTHORITATIVE = {
    7: (
        "Check in when your room is not ready",
        "I have a reservation under Tanaka.",
        "Can we leave our bags here until three?",
    ),
    8: (
        "Get a hotel problem fixed",
        "The air conditioning doesn't work.",
        "Can we change rooms?",
    ),
    9: (
        "Order with a dietary restriction",
        "I'm allergic to nuts.",
        "Does it contain any nuts?",
    ),
    10: (
        "Correct an order politely",
        "Sorry, I ordered the iced coffee, not the hot one.",
        "Can I have the iced one instead?",
    ),
    11: (
        "Return something that does not work",
        "I bought this yesterday, but it doesn't work.",
        "Can I exchange it for another one?",
    ),
    12: (
        "Change a booking without losing it",
        "Can we move our reservation to eight?",
        "Is it still for four people?",
    ),
}


def esc(value):
    return html.escape(str(value), quote=True)


def profile(name, source):
    return (
        f'<span class="who"><img class="avatar" src="{source}" alt="">'
        f'<span class="who-name">{esc(name)}</span></span>'
    )


def cast_row(source, name, description):
    return (
        f'<span class="cast-row"><img class="avatar" src="{source}" alt="">'
        f'<span class="cast-who">{esc(name)}<small>{esc(description)}</small></span></span>'
    )


def set_vocab(head, values):
    for category, value in zip(("new", "recycled", "assumed", "receptive"), values):
        head, replacements = re.subn(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{esc(value)}\2',
            head,
            count=1,
        )
        if replacements != 1:
            raise ValueError(f"canonical shell has no vocabulary field for {category}")
    return head


def validate_lesson(number, lesson):
    expected_title, expected_p1, expected_p2 = AUTHORITATIVE[number]
    if lesson["title"] != expected_title:
        raise ValueError(f"CTX-{number}: title differs from the generated brief")
    actual = tuple(
        core.strip_marks(lesson[f"p{part}"]["rows"][0][0]) for part in (1, 2)
    )
    if actual != (expected_p1, expected_p2):
        raise ValueError(f"CTX-{number}: required models differ from the generated brief: {actual}")
    if len(lesson["expressions"]) != 2 or len(lesson["receptive"]) != 4:
        raise ValueError(f"CTX-{number}: needs two expressions and four receptive checks")
    if not 5 <= len(lesson["scene_turns"]) <= 9:
        raise ValueError(f"CTX-{number}: opening scene needs 5-9 turns")
    if not 5 <= len(lesson["transfer_turns"]) <= 7:
        raise ValueError(f"CTX-{number}: transfer needs 5-7 turns")
    for turn_set, label in ((lesson["scene_turns"], "scene"), (lesson["transfer_turns"], "transfer")):
        targets = [turn for turn in turn_set if turn[0] == "target"]
        if len(targets) != 2 or {turn[1] for turn in targets} != {1, 2}:
            raise ValueError(f"CTX-{number}: {label} must use both patterns once")
    for part in (1, 2):
        pattern = lesson[f"p{part}"]
        if len(pattern["rows"]) != 4:
            raise ValueError(f"CTX-{number} p{part}: needs four closed rows")
        for preposition in pattern.get("attached_prepositions", ()):
            for _, _, chunk_source in pattern["rows"]:
                chunks = chunk_source.split("|")
                if preposition in chunks or not any(
                    chunk.startswith(f"{preposition} ") for chunk in chunks
                ):
                    raise ValueError(
                        f"CTX-{number} p{part}: attach {preposition!r} to its complement"
                    )
        if not pattern.get("omit_reorder"):
            core.validate_reorder_pattern(pattern["rows"])
        hints = pattern.get("translate_hints")
        if not hints or len(hints) != len(pattern["rows"]):
            raise ValueError(f"CTX-{number} p{part}: supported translation needs one lexical hint set per row")
        if not pattern.get("write_frame"):
            raise ValueError(f"CTX-{number} p{part}: open production needs an explicit stable write frame")
        if not pattern.get("write_script"):
            raise ValueError(f"CTX-{number} p{part}: open production needs an explicit communicative job")
    validate_reviewed_copy(number, lesson)


def validate_reviewed_copy(number, lesson):
    prompt_en, _, _, _, ask_en, _ = lesson["live"]
    for label, question in (("Tutor question", prompt_en), ("learner ask-back", ask_en)):
        if not question.strip().endswith("?"):
            raise ValueError(f"CTX-{number}: {label} must be a real question")
        if "___" in question or re.search(
            r"\b(?:what would you (?:say|ask)|imagine|report it|explain|use today's|say the pattern)\b",
            question,
            flags=re.IGNORECASE,
        ):
            raise ValueError(f"CTX-{number}: {label} must be conversation, not pattern production")


def render_roleplay(lesson, turns, *, highlight=False, complete=False, prefix, role=None):
    other_role = role or lesson["role"]
    rendered = []
    for index, turn_spec in enumerate(turns):
        kind = turn_spec[0]
        if kind == "target":
            _, part, row = turn_spec
            english, japanese, _ = lesson[f"p{part}"]["rows"][row]
            if complete:
                english_html = core.inputs(english, f"{prefix}-p{part}-{index}")
                japanese_html = core.marks(japanese, "target")
                rendered.append(core.answer_turn(ME, "Me", english_html, japanese_html))
            else:
                if highlight:
                    english_html = core.marks(english)
                    japanese_html = core.marks(japanese)
                else:
                    english_html = esc(core.strip_marks(english))
                    japanese_html = esc(core.strip_marks(japanese))
                rendered.append(core.turn("me", ME, "Me", english_html, japanese_html))
            continue

        _, english, japanese = turn_spec
        side = "me" if kind == "me" else "other"
        source = ME if side == "me" else OTHER
        speaker = "Me" if side == "me" else other_role
        rendered.append(core.turn(side, source, speaker, esc(english), esc(japanese)))
    return "".join(rendered)


def goal_page(lesson):
    return core.goal_page(
        title=lesson["title"], title_ja=lesson["ja"],
        can_do=lesson["goal"][0], can_do_ja=lesson["goal"][1],
        data_act="Travel task",
    )


def expressions_page(lesson):
    models = "".join(
        f'<div class="model-line"><span class="korean">{esc(english)}</span>'
        f'<span class="translation">{esc(japanese)}</span></div>'
        for english, japanese in lesson["expressions"]
    )
    return core.section(
        "expressions",
        "Useful expressions",
        "使える表現",
        '<p class="section-subtitle"><span class="ko">Please read each expression aloud.</span>'
        '<span class="ja">それぞれの表現を声に出して読んでください。</span></p>'
        f'<div class="model-list">{models}</div>',
    )


def understand_page(number, lesson):
    blocks = []
    for index, (line, correct_en, correct_ja, wrong_en, wrong_ja) in enumerate(lesson["receptive"]):
        options = [
            ("correct", correct_en, correct_ja, True),
            ("other", wrong_en, wrong_ja, False),
        ]
        if index % 2:
            options.reverse()
        choices = "".join(
            f'<span class="opt" data-sync-option="{kind}"{" data-correct" if correct else ""}>'
            f'<span class="choice-en">{esc(english)}</span><small>{esc(japanese)}</small></span>'
            for kind, english, japanese, correct in options
        )
        blocks.append(
            f'<div class="choose-row sentence receptive-choice" data-sync-id="ctx-{number}-understand-{index}" '
            f'data-sync-kind="selection" data-sync-state="chosen"><span class="translation">{esc(line)}</span>'
            f'<span class="choose-sentence">{choices}</span></div>'
        )
    return core.section(
        "understand",
        "Understand",
        "聞いてわかろう",
        f'<p class="section-subtitle"><span class="ko">I’ll read each {esc(lesson["role"].lower())} line. Choose what it means.</span>'
        f'<span class="ja">私が{esc(lesson.get("role_ja", ROLE_JA.get(lesson["role"], "相手役")))}のセリフを読みます。意味を選んでください。</span></p>'
        f'<div class="choose-list">{"".join(blocks)}</div>',
    )


def transition(part, pattern):
    model = core.strip_marks(pattern["rows"][0][0])
    purpose = pattern.get("transition_purpose", pattern.get("meaning"))
    if (
        not isinstance(purpose, (tuple, list))
        or len(purpose) != 2
        or not all(isinstance(value, str) and value.strip() for value in purpose)
    ):
        raise ValueError("transition needs an explicit aligned EN/JA purpose pair")
    move_en = purpose[0].strip().rstrip(". ") + "."
    move_ja = purpose[1].strip().rstrip("。 ") + "。"
    return f'''    <div class="transition-page" data-page-id="part{part}-intro" data-act="Move {part}">
      <span class="transition-kicker">MOVE {part}</span>
      <h2 class="transition-title">{esc(model)}</h2>
      <p class="section-subtitle"><span class="ko">{esc(move_en)} Read the line above aloud.</span><span class="ja">{esc(move_ja)} 上の文を声に出して読みましょう。</span></p>
      <div class="tutor-note">After the learner reads the line aloud, move on.</div>
    </div>
'''


def teach_page(part, pattern):
    hero_en, hero_ja, _ = pattern["rows"][0]
    examples = "".join(
        f'<div><span class="korean">{core.marks(english)}</span>'
        f'<span class="translation">{core.marks(japanese)}</span></div>'
        for english, japanese, _ in pattern["rows"][1:3]
    )
    return core.section(
        f"p{part}-teach",
        "Today's pattern",
        "今日のパターン",
        '<p class="section-subtitle pattern-meaning">'
        '<span class="meaning-kicker">Meaning &amp; use <small>意味・使い方</small></span>'
        f'<span class="ko">{esc(pattern["meaning"][0])}</span>'
        f'<span class="ja">{esc(pattern["meaning"][1])}</span></p>'
        '<div class="tutor-note">Briefly explain the meaning, then have the learner read each example aloud.</div>'
        f'<div class="sent-hero"><span class="korean">{core.marks(hero_en)}</span>'
        f'<span class="translation">{core.marks(hero_ja)}</span></div>'
        f'<div class="sent-more">{examples}</div>',
    )


def rule_page(part, pattern):
    title, title_ja, script, script_ja, formula, heading, heading_ja, examples = pattern["rule"]
    return core.rule_page(
        f"p{part}-rule",
        title,
        title_ja,
        script,
        script_ja,
        esc(formula),
        heading,
        heading_ja,
        tuple(esc(example) for example in examples),
    )


def reorder_page(part, pattern):
    if pattern.get("omit_reorder"):
        return ""
    rows_data = pattern["rows"]
    core.validate_reorder_pattern(rows_data)
    count = len(rows_data[0][2].split("|"))
    page = core.reorder(f"p{part}-reorder", rows_data)
    if count == 3:
        page = page.replace(
            f'data-page-id="p{part}-reorder"',
            f'data-page-id="p{part}-reorder" data-chunk-review="meaningful"',
            1,
        )
    return f'    <!-- Reorder criterion: {esc(pattern["reorder_criterion"])}. -->\n{page}'


def write_page(part, pattern):
    write_frame = pattern.get("write_frame", core.strip_marks(pattern["rows"][0][0]))
    write_script = pattern.get(
        "write_script", f'Now use “{write_frame}” to make your own sentence.'
    )
    write_script_ja = pattern.get("write_script_ja", pattern["write"][1])
    return core.section(
        f"p{part}-write",
        "Make it yours",
        "自分の場面で言おう",
        f'<p class="section-subtitle"><span class="ko">{esc(write_script)}</span>'
        f'<span class="ja">{esc(write_script_ja)}</span></p>'
        '<div class="tutor-note">Let the learner answer aloud before you capture and correct it.</div>'
        + core.feedback_compose(f"p{part}-write"),
    )


def freetalk_page(lesson):
    prompt_en, prompt_ja, scaffold, scaffold_ja, ask_en, ask_ja = lesson["live"]
    def live_text(side, speaker, english, japanese):
        bubble_class = "bubble me" if side == "me" else "bubble"
        return f'<div class="turn {side}">{core.live_avatar(speaker)}<div class="{bubble_class}"><span class="korean">{esc(english)}</span><span class="translation">{esc(japanese)}</span></div></div>'

    def live_input(side, speaker, sync_id, label, label_ja):
        bubble_class = "bubble me" if side == "me" else "bubble"
        return f'<div class="turn {side}">{core.live_avatar(speaker)}<div class="{bubble_class}"><div class="answer-box tall"><span class="answer-label">{esc(label)}<span class="task">{esc(label_ja)}</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="{sync_id}" rows="3" spellcheck="false" maxlength="2000"></textarea></span></div></div></div>'

    turns = (
        live_text("other", "Tutor", prompt_en, prompt_ja)
        + live_input("me", "Me", "p3-real-answer", "Student's answer", "自分の答え")
        + live_text("me", "Me", ask_en, ask_ja)
        + live_input("other", "Tutor", "p3-tutor-answer", "Tutor's answer", "先生の答え")
    )
    return core.section(
        "p3-freetalk",
        "Talk about the real situation",
        "本当の場面について話そう",
        '<p class="section-subtitle"><span class="ko">Let’s talk about this situation. Answer my question, then ask me too.</span>'
        '<span class="ja">この場面について話しましょう。私の質問に答えて、そのあと私にも聞いてください。</span></p>'
        '<div class="tutor-note">React naturally and follow the most interesting detail. Use today\'s pattern only if it fits.</div>'
        f'<div class="dialogue">{turns}</div>',
    )


def native_tip_page(lesson):
    title, title_ja, script, script_ja, left, right = lesson["tip"]
    return core.section(
        "native-tip",
        title,
        title_ja,
        f'<p class="section-subtitle"><span class="ko">{esc(script)}</span><span class="ja">{esc(script_ja)}</span></p>'
        '<div class="nuance-compare">'
        f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(left[0])}</b><small>{esc(left[1])}</small></span>'
        f'<span class="korean">{esc(left[2])}</span><span class="translation">{esc(left[3])}</span></div>'
        '<div class="nuance-or"><span>Pick by situation <small>場面で選ぶ</small></span></div>'
        f'<div class="nuance-choice"><span class="nuance-when"><b>{esc(right[0])}</b><small>{esc(right[1])}</small></span>'
        f'<span class="korean">{esc(right[2])}</span><span class="translation">{esc(right[3])}</span></div>'
        '</div>',
    )


def pages(number, lesson):
    role_ja = lesson.get("role_ja", ROLE_JA.get(lesson["role"], "相手役"))
    practice_role_ja = lesson.get("role_ja", "相手役")
    practice_role_intro_ja = (
        f"私は{practice_role_ja}です。"
        if lesson.get("role_ja")
        else "私は相手役をします。"
    )
    transfer_role_ja = lesson.get(
        "transfer_role_ja", ROLE_JA.get(lesson["transfer_role"], "相手役")
    )
    opening = render_roleplay(lesson, lesson["scene_turns"], prefix=f"ctx-{number}-scene")
    model = render_roleplay(
        lesson, lesson["scene_turns"], highlight=True, prefix=f"ctx-{number}-model"
    )
    complete = render_roleplay(
        lesson,
        lesson["scene_turns"],
        complete=True,
        prefix=f"ctx-{number}-complete",
    )
    transfer = render_roleplay(
        lesson,
        lesson["transfer_turns"],
        complete=True,
        prefix=f"ctx-{number}-transfer",
        role=lesson["transfer_role"],
    )
    result = [
        goal_page(lesson),
        core.section(
            "scene",
            lesson["scene"],
            lesson["scene_ja"],
            f'<p class="section-subtitle"><span class="ko">Let\'s role-play. You\'re the traveller, and I\'ll be the {esc(lesson["role"].lower())}.</span>'
            f'<span class="ja">ロールプレイをしましょう。あなたは旅行者、私は{esc(role_ja)}です。</span></p>'
            f'<div class="tutor-note">Start with the first {esc(lesson["role"])} line.</div>'
            f'<div class="dialogue">{opening}</div>',
        ),
        understand_page(number, lesson),
        expressions_page(lesson),
    ]
    for part in (1, 2):
        pattern = lesson[f"p{part}"]
        result.extend(
            [
                transition(part, pattern),
                teach_page(part, pattern),
                core.read(f"p{part}-read", pattern["rows"]),
                rule_page(part, pattern) if not pattern.get("omit_rule") else "",
                reorder_page(part, pattern),
                core.fill(f"p{part}-fill", pattern["rows"]) if not pattern.get("omit_fill") else "",
                core.translate(
                    f"p{part}-translate",
                    pattern["rows"],
                    hints=pattern.get("translate_hints"),
                    support_stage=pattern.get(
                        "translate_stage",
                        "supported" if pattern.get("translate_hints") else None,
                    ),
                ),
                write_page(part, pattern),
            ]
        )
    result.extend(
        [
            '    <div class="transition-page" data-page-id="part3-intro" data-act="Complete the task">'
            '<span class="transition-kicker">PUT IT TOGETHER</span><h2 class="transition-title">'
            'Complete the practical job <span class="title-ja">(用事を完了しよう)</span></h2>'
            '<p class="section-subtitle"><span class="ko">Now, let\'s return to the scene and complete the practical job.</span>'
            '<span class="ja">最初の場面に戻り、二つの表現で用事を最後まで完了しましょう。</span></p>'
            '<div class="tutor-note">Introduce the roleplay, then move on.</div></div>\n',
            core.section(
                "p3-model",
                "Replay the full scene",
                "場面をもう一度",
                f'<p class="section-subtitle"><span class="ko">I\'ll be the {esc(lesson["role"])}. Please read the Traveller lines aloud.</span>'
                f'<span class="ja">{esc(practice_role_intro_ja)}Traveller のセリフを声に出して読んでください。</span></p>'
                f'<div class="dialogue">{model}</div>',
            ),
            core.section(
                "p3-complete",
                "Complete the full scene",
                "場面を完成しよう",
                f'<p class="section-subtitle"><span class="ko">I’ll be the {esc(lesson["role"])}. Say each complete line, including the missing words.</span>'
                f'<span class="ja">{esc(practice_role_intro_ja)}空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。</span></p>'
                '<div class="tutor-note">Type only the missing words exactly as the learner says them.</div>'
                f'<div class="dialogue">{complete}</div>',
            ),
            freetalk_page(lesson),
            native_tip_page(lesson),
            core.section(
                "transfer-scene",
                lesson["transfer_title"],
                lesson["transfer_ja"],
                f'<p class="section-subtitle"><span class="ko">Let\'s role-play a new situation using the same two lines. I\'ll be the {esc(lesson["transfer_role"].lower())}.</span>'
                f'<span class="ja">同じ二つの表現を使って、別の場面でロールプレイをしましょう。私は{esc(transfer_role_ja)}です。</span></p>'
                f'<div class="dialogue">{transfer}</div>',
            ),
        ]
    )
    return [page for page in result if page]


def build(number, lesson):
    validate_lesson(number, lesson)
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{lesson["slug"]}'
    head = new_lesson.retarget(
        head,
        review_id=f"CTX-{number}",
        lesson_id=slug,
        level="B1",
        title=lesson["title"],
        title_ko=lesson["ko"],
        title_ja=lesson["ja"],
        version="2026-08-20",
    ).replace('content="todo"', 'content="reviewed"')
    head = set_vocab(head, lesson["vocab"])
    head = core.set_proofread_status(head, "complete")
    output = TRACK / "courses" / COURSE / "lessons" / slug / "lesson.html"
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
