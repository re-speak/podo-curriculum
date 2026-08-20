#!/usr/bin/env python3
"""Generate the independently reviewable CTX 25-36 Contextual batch."""

from __future__ import annotations

import argparse
import html
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
ME, OTHER = core.ME, core.OTHER

COURSES = {
    range(25, 31): ("ctx-travel-complex-decisions", "C1", "TRAVEL ENGLISH", "Traveller", "旅行者"),
    range(31, 37): ("ctx-business-workplace-essentials", "B1", "BUSINESS ENGLISH", "Colleague", "同僚"),
}


def rows(*items):
    return items


def pattern(*, bridge, meaning, rows_, rule, write, omit_rule=False, omit_reorder=False):
    return dict(
        bridge=bridge,
        meaning=meaning,
        rows=rows_,
        rule=rule,
        write=write,
        omit_rule=omit_rule,
        omit_reorder=omit_reorder,
        reorder_criterion="consistent meaningful clause chunks",
    )


LESSONS = {
    25: dict(
        slug="escalate-a-cancellation-with-clear-priorities",
        title="Escalate a cancellation with clear priorities",
        ko="취소 상황에서 우선순위를 분명히 말하기",
        ja="欠航時に優先事項を明確に伝える",
        role="Airline Agent",
        scene="At an airline service desk after a cancellation",
        scene_ja="欠航後の航空会社サービスカウンター",
        situation="代替便では大切な予定に間に合わないため、譲れない条件を伝え、別ルートを探してもらいます。",
        goal=("State the arrival time you cannot compromise on and secure a workable route.", "譲れない到着時刻を伝え、実行可能な別ルートを確保しましょう。"),
        expressions=(("earliest possible arrival", "最も早い到着"), ("alternative routing", "別ルート")),
        p1=pattern(
            bridge="まず、何を最優先するかを一文ではっきり示します。",
            meaning=("Use this to name the one priority that should drive the decision.", "判断の基準にすべき最優先事項を一つ示す表現です。"),
            rows_=rows(
                ("{t}What matters most is{/t} arriving before tomorrow morning.", "最も重要なのは、明日の朝までに{t}到着することです{/t}。", "What matters most|is arriving|before tomorrow morning."),
                ("{t}What matters most is{/t} reaching Tokyo tonight.", "最も重要なのは、今夜東京に{t}着くことです{/t}。", "What matters most|is reaching Tokyo|tonight."),
                ("{t}What matters most is{/t} making the morning meeting.", "最も重要なのは、朝の会議に{t}間に合うことです{/t}。", "What matters most|is making|the morning meeting."),
                ("{t}What matters most is{/t} getting there by nine.", "最も重要なのは、9時までに{t}到着することです{/t}。", "What matters most|is getting there|by nine."),
            ),
            rule=("Put the deciding priority after “is”", "判断の基準は is のあと", "Name only the result that the new option must protect.", "新しい選択肢で守るべき結果だけを示します。", "What matters most + is + priority", "Set the priority", "優先事項を示す", ("is · arriving before morning", "is · reaching Tokyo tonight")),
            write=("What arrival condition would matter most to you?", "到着について、あなたが最優先する条件は何ですか？"),
        ),
        p2=pattern(
            bridge="次に、その条件を満たせそうな別ルートを具体的に頼みます。",
            meaning=("Use this to ask an agent to search via a specific connecting city.", "特定の都市を経由する経路を係員に探してもらう表現です。"),
            rows_=rows(
                ("{t}Could you check routes through{/t} another city?", "別の都市を{t}経由するルートを確認していただけますか{/t}？", "Could you check|routes through|another city?"),
                ("{t}Could you check routes through{/t} Seoul?", "ソウルを{t}経由するルートを確認していただけますか{/t}？", "Could you check|routes through|Seoul?"),
                ("{t}Could you check routes through{/t} Osaka?", "大阪を{t}経由するルートを確認していただけますか{/t}？", "Could you check|routes through|Osaka?"),
                ("{t}Could you check routes through{/t} a nearby airport?", "近くの空港を{t}経由するルートを確認していただけますか{/t}？", "Could you check|routes through|a nearby airport?"),
            ),
            rule=("Keep the route and its connection together", "ルートと経由地をセットに", "Put the city or airport directly after “through.”", "through の直後に都市や空港を置きます。", "Could you check + routes through + place?", "Ask for another search", "別の検索を頼む", ("routes through · Seoul", "routes through · a nearby airport")),
            write=("Which connecting city or airport would you ask the agent to check?", "どの経由地を確認してもらいますか？"),
        ),
        scene_turns=(
            ("other", "The next direct flight arrives tomorrow afternoon.", "次の直行便は明日の午後に到着します。"),
            ("target", 1, 0),
            ("other", "Understood. A connection might get you there earlier.", "承知しました。乗り継ぎ便なら、より早く到着できる可能性があります。"),
            ("target", 2, 1),
            ("other", "Yes. There is a Seoul connection arriving at nine tonight.", "はい。ソウル経由で今夜9時に到着する便があります。"),
            ("me", "That works. Please book that route.", "それなら間に合います。そのルートで予約してください。"),
        ),
        receptive=(
            ("The next direct flight arrives tomorrow afternoon.", "The direct option misses tomorrow morning", "直行便では明日の朝に間に合わない", "The direct option arrives tonight", "直行便は今夜到着する"),
            ("A connection might get you there earlier.", "A connecting route could improve the arrival time", "乗り継ぎなら到着が早まる可能性がある", "Only the direct route is available", "直行便しか利用できない"),
            ("There is a Seoul connection arriving at nine tonight.", "The Seoul route meets the stated deadline", "ソウル経由なら希望時刻に間に合う", "The Seoul route arrives tomorrow night", "ソウル経由は明日の夜に着く"),
            ("The fare difference is covered because of the cancellation.", "The rerouting will not cost extra", "欠航による変更なので追加料金はない", "The traveler must buy a new full-price ticket", "新しい正規運賃の航空券を買う必要がある"),
        ),
        live=("A trip is cancelled. Name one arrival condition you would protect.", "旅行が中止になりました。譲れない到着条件を一つ伝えてください。", "What matters most is ___. Could you check routes through ___? / If you have no such trip: I don't have a current trip, but I'd prioritize ___.", "実際の予定がなければ、仮の優先事項を答えてもかまいません。", "When travel changes, what matters most to you?", "旅行が変更になったとき、先生は何を最優先しますか？"),
        tip=("Use “nonstop” in everyday US travel", "米語では nonstop が自然", "“Direct” can include a stop; “nonstop” means the plane does not stop en route.", "direct は途中で着陸する場合もあり、nonstop は途中で止まらない便を指します。", ("No stop", "途中で止まらない", "Is there a nonstop flight?", "直行便はありますか？"), ("Same flight number", "同じ便名", "Is there a direct flight?", "直行便はありますか？")),
        transfer_title="Rebooking a cancelled train journey",
        transfer_ja="運休した列車の旅程を変更する",
        transfer_role="Rail Agent",
        transfer_turns=(("other", "The next direct train reaches Kyoto tomorrow at noon.", "次の直通列車は明日の正午に京都へ着きます。"), ("target", 1, 3), ("other", "A transfer may get you there before nine.", "乗り換えれば9時前に着ける可能性があります。"), ("target", 2, 2), ("other", "Yes. The Osaka route arrives at eight-thirty.", "はい。大阪経由なら8時30分に着きます。"), ("me", "Perfect. Please change my ticket.", "それでお願いします。切符を変更してください。")),
        vocab=("alternative routing|別ルート; nonstop|途中で止まらない", "what matters most|最も重要なこと|CORE-103; could you check|確認していただけますか|CORE-24; route|ルート|CORE-59", "city|都市; morning|朝; tonight|今夜; flight|便", "fare difference|運賃差額; connection|乗り継ぎ"),
    ),
    26: dict(
        slug="document-an-incident-for-insurance", title="Document an incident for insurance", ko="보험을 위해 사건을 기록하기", ja="保険申請のために事故を記録する", role="Insurance Agent", scene="Reporting a stolen camera by phone", scene_ja="盗難に遭ったカメラを電話で届け出る", situation="確実に分かる事実と推測を分けて伝え、保険申請に必要な記録を作ります。", goal=("Separate confirmed facts from uncertainty and obtain the documents for a claim.", "確認できている事実と不確かな点を分け、保険申請の書類をそろえましょう。"), expressions=(("police report", "警察の届出書"), ("supporting documents", "添付書類")),
        p1=pattern(bridge="まず、最後に確実に持っていた場所を伝えます。", meaning=("Use “definitely” to mark the last fact you know is true.", "definitely を使って、確実に分かっている最後の事実を示します。"), rows_=rows(("I {t}definitely had{/t} it {t}at the station{/t}.", "駅では{t}確実に持っていました{/t}。", "I definitely had|it|at the station."), ("I {t}definitely had{/t} it {t}at the hotel{/t}.", "ホテルでは{t}確実に持っていました{/t}。", "I definitely had|it|at the hotel."), ("I {t}definitely had{/t} the bag {t}at the café{/t}.", "カフェではそのバッグを{t}確実に持っていました{/t}。", "I definitely had|the bag|at the café."), ("I {t}definitely had{/t} my wallet {t}before lunch{/t}.", "昼食前には財布を{t}確実に持っていました{/t}。", "I definitely had|my wallet|before lunch.")), rule=("Use “definitely” only for a confirmed fact", "definitely は確認済みの事実に", "Attach a reliable place or time to the fact.", "確実な場所や時刻を事実に添えます。", "I + definitely had + item + place/time", "Record what is known", "確実な情報を記録", ("definitely had it · at the station", "definitely had the bag · at the café")), write=("Where did you last know the item was with you?", "その品を確実に持っていた最後の場所はどこですか？")),
        p2=pattern(bridge="次に、可能性はあるものの断定できない点を伝えます。", meaning=("Use this to report a possible event without presenting it as a fact.", "可能性のある出来事を、事実と断定せずに伝える表現です。"), rows_=rows(("It {t}may have been taken{/t} on the train, {t}but I can't be certain{/t}.", "列車内で{t}盗まれた可能性がありますが、確かではありません{/t}。", "It may have been taken|on the train,|but I can't be certain."), ("It {t}may have been left{/t} in the taxi, {t}but I can't be certain{/t}.", "タクシーに{t}置き忘れた可能性がありますが、確かではありません{/t}。", "It may have been left|in the taxi,|but I can't be certain."), ("It {t}may have been taken{/t} at the café, {t}but I can't be certain{/t}.", "カフェで{t}盗まれた可能性がありますが、確かではありません{/t}。", "It may have been taken|at the café,|but I can't be certain."), ("It {t}may have been lost{/t} near the station, {t}but I can't be certain{/t}.", "駅の近くで{t}紛失した可能性がありますが、確かではありません{/t}。", "It may have been lost|near the station,|but I can't be certain.")), rule=("Pair the possibility with a limit", "可能性と不確かさをセットに", "State what may have happened, then explicitly limit the claim.", "起きた可能性を述べたあと、断定できないことを明示します。", "may have + event, but + can't be certain", "Protect the accuracy", "正確さを保つ", ("may have been taken · but I can't be certain", "may have been left · but I can't be certain")), write=("What possibility would you report without claiming it as fact?", "事実と断定せずに、どの可能性を伝えますか？")),
        scene_turns=(("other", "When did you last know you had the camera?", "カメラを確実に持っていた最後の時点はいつですか？"), ("target", 1, 0), ("other", "What do you think happened after that?", "そのあと何が起きたと思いますか？"), ("target", 2, 0), ("other", "I'll record the station as confirmed and the train as a possibility. Please send the police report and proof of purchase.", "駅は確認済み、列車内は可能性として記録します。警察の届出書と購入証明を送ってください。"), ("me", "Understood. I'll send both documents today.", "分かりました。今日、両方の書類を送ります。")),
        receptive=(("When did you last know you had the camera?", "The agent wants the last confirmed time", "最後に確認できた時点を尋ねている", "The agent wants a guess about the thief", "犯人についての推測を求めている"), ("I'll record the station as confirmed and the train as a possibility.", "The report will distinguish fact from uncertainty", "記録では事実と可能性を分ける", "The report will state that the theft happened at the station", "駅で盗まれたと断定する"), ("Please send the police report and proof of purchase.", "Two supporting documents are required", "2種類の添付書類が必要", "No documents are needed", "書類は必要ない"), ("Keep the original receipts.", "The claimant should retain the original documents", "原本を保管しておく", "The claimant should throw away the receipts", "レシートを捨てる")),
        live=("Think of a lost item, real or imaginary. Separate one fact from one possibility.", "実際または架空の紛失物について、事実と可能性を一つずつ分けて話してください。", "I definitely had ___ at ___. It may have ___, but I can't be certain. / If nothing comes to mind: I've never lost anything valuable.", "思い当たる例がなければ、なくしたことがないと答えてかまいません。", "Have you ever had to report a lost item?", "先生は紛失物を届け出たことがありますか？"),
        tip=("Say “stolen” for the item, “robbed” for the person", "物には stolen、人には robbed", "A camera is stolen; a person is robbed.", "カメラなどの物は stolen、人が被害に遭う場合は robbed を使います。", ("The item", "物", "My camera was stolen.", "カメラを盗まれました。"), ("The person", "人", "I was robbed.", "強盗に遭いました。")),
        transfer_title="Reporting a missing laptop to hotel security", transfer_ja="なくなったノートPCをホテルの警備に届け出る", transfer_role="Security Officer", transfer_turns=(("other", "Where did you last see the laptop?", "ノートPCを最後に見たのはどこですか？"), ("target", 1, 1), ("other", "Do you know what happened after you checked out?", "チェックアウト後に何が起きたか分かりますか？"), ("target", 2, 1), ("other", "I'll mark the hotel as confirmed and the taxi as unconfirmed.", "ホテルは確認済み、タクシーは未確認として記録します。"), ("me", "Good. Please email me the incident number.", "分かりました。事故番号をメールしてください。")),
        vocab=("supporting documents|添付書類; police report|警察の届出書; incident number|事故番号", "definitely|確実に|CORE-32; may have|した可能性がある|CORE-72; certain|確かな|CORE-65; proof of purchase|購入証明|CTX-11", "camera|カメラ; train|列車; station|駅; hotel|ホテル", "claim|保険申請; confirmed|確認済み; unconfirmed|未確認"),
    ),
    27: dict(
        slug="advocate-for-an-accessibility-requirement", title="Advocate for an accessibility requirement", ko="접근성 요구 사항을 분명히 요청하기", ja="アクセシビリティ要件を明確に求める", role="Hotel Manager", scene="At a hotel with an inaccessible reserved room", scene_ja="予約した部屋が利用できないホテル", situation="事前に確認した段差のないアクセスが用意されていないため、必須条件を明確にし、今夜の代案を求めます。", goal=("Make the essential access requirement non-negotiable and obtain a usable room tonight.", "必須のアクセス条件を明確にし、今夜利用できる部屋を確保しましょう。"), expressions=(("reasonable accommodation", "合理的配慮"), ("at your expense", "そちらの負担で")),
        p1=pattern(bridge="まず、希望ではなく必須条件だと明確にします。", meaning=("Use this fixed line to correct any attempt to treat an essential need as a preference.", "必須の要件を単なる希望として扱われないようにする定型表現です。"), rows_=rows(("{t}To be clear, step-free access is essential, not optional{/t}.", "{t}はっきり申し上げると、段差のないアクセスは必須で、任意ではありません{/t}。", "To be clear,|step-free access|is essential,|not optional."), ("{t}To be clear, an accessible bathroom is essential, not optional{/t}.", "{t}はっきり申し上げると、バリアフリーの浴室は必須で、任意ではありません{/t}。", "To be clear,|an accessible bathroom|is essential,|not optional."), ("{t}To be clear, elevator access is essential, not optional{/t}.", "{t}はっきり申し上げると、エレベーターの利用は必須で、任意ではありません{/t}。", "To be clear,|elevator access|is essential,|not optional."), ("{t}To be clear, a ground-floor room is essential, not optional{/t}.", "{t}はっきり申し上げると、1階の部屋は必須で、任意ではありません{/t}。", "To be clear,|a ground-floor room|is essential,|not optional.")), rule=("Keep the clarification intact", "明確化の表現はひとまとまり", "Change only the requirement inside this firm but professional line.", "強くても丁寧なこの文では、要件だけを入れ替えます。", "To be clear + requirement + is essential, not optional", "Protect the requirement", "要件を守る", ("step-free access · is essential", "elevator access · is essential")), write=("Which access requirement would you need the hotel to guarantee?", "ホテルに保証してもらう必要があるアクセス条件は何ですか？"), omit_rule=True),
        p2=pattern(bridge="次に、曖昧な約束ではなく、今夜使える代案を尋ねます。", meaning=("Use this fixed question to require a concrete alternative for the current situation.", "現在の状況に対する具体的な代案を求める定型質問です。"), rows_=rows(("{t}What alternative can you offer us tonight{/t}?", "{t}今夜、どのような代案を提示していただけますか{/t}？", "What alternative|can you offer us|tonight?"), ("{t}What alternative can you offer us now{/t}?", "{t}今、どのような代案を提示していただけますか{/t}？", "What alternative|can you offer us|now?"), ("{t}What accessible room can you offer us tonight{/t}?", "{t}今夜、どのバリアフリー客室を提供できますか{/t}？", "What accessible room|can you offer us|tonight?"), ("{t}What nearby hotel can you offer us tonight{/t}?", "{t}今夜、近くのどのホテルを手配できますか{/t}？", "What nearby hotel|can you offer us|tonight?")), rule=("Ask for an offer, not another promise", "約束ではなく提案を求める", "Name the usable alternative and the time it is needed.", "利用できる代案と必要な時刻を示します。", "What + alternative + can you offer + time?", "Get a concrete option", "具体案を得る", ("alternative · tonight", "accessible room · now")), write=("What concrete alternative would solve the access problem tonight?", "今夜のアクセス問題を解決する具体的な代案は何ですか？"), omit_rule=True),
        scene_turns=(("other", "I'm sorry. We can try to move you tomorrow.", "申し訳ありません。明日なら部屋を移せるよう調整します。"), ("target", 1, 0), ("other", "I understand. The room we assigned has three steps.", "承知しました。割り当てた部屋には3段の階段があります。"), ("target", 2, 0), ("other", "We can move you to our sister hotel and cover the taxi and rate difference.", "系列ホテルへ移り、タクシー代と料金差額はこちらで負担できます。"), ("me", "That meets our needs. Please arrange it now.", "それなら必要条件を満たします。今すぐ手配してください。")),
        receptive=(("We can try to move you tomorrow.", "The first offer does not solve tonight's need", "最初の提案では今夜の必要を満たせない", "A suitable room is ready now", "適切な部屋が今すぐ利用できる"), ("The room we assigned has three steps.", "The assigned room is not step-free", "割り当てられた部屋には段差がある", "The assigned room has elevator access", "割り当てられた部屋はエレベーターを利用できる"), ("We can move you to our sister hotel.", "The manager offers another property", "系列の別ホテルを提案している", "The manager asks the guest to leave without help", "手配なしで退去するよう求めている"), ("We'll cover the taxi and rate difference.", "The hotel will pay the extra costs", "追加費用はホテルが負担する", "The guest must pay every extra cost", "追加費用はすべて宿泊客が払う")),
        live=("Name an accommodation that would make a trip usable for you or someone you know.", "自分や身近な人が旅行する際に必要な配慮を一つ挙げてください。", "To be clear, ___ is essential, not optional. What alternative can you offer us tonight? / If none applies: I don't currently need a special accommodation.", "必要な配慮がなければ、今は特別な配慮は必要ないと答えてかまいません。", "What makes a hotel easy for you to use?", "先生にとって使いやすいホテルの条件は何ですか？"),
        tip=("Use “accessible,” not “handicapped”", "handicapped ではなく accessible", "For rooms and facilities, “accessible” is the respectful current term.", "客室や設備には、現在一般的で配慮のある accessible を使います。", ("Current term", "現在の表現", "an accessible room", "バリアフリー客室"), ("Specific need", "具体的な必要", "step-free access", "段差のないアクセス")),
        transfer_title="Requesting access at a conference venue", transfer_ja="会議会場でアクセスを求める", transfer_role="Venue Coordinator", transfer_turns=(("other", "The main entrance lift is out of service today.", "正面入口のリフトは本日故障しています。"), ("target", 1, 2), ("other", "I understand. The service entrance has a working lift.", "承知しました。搬入口のリフトは利用できます。"), ("target", 2, 1), ("other", "I can meet you there now and escort you to the hall.", "今そちらへ伺い、会場までご案内できます。"), ("me", "Thank you. That solution works for us.", "ありがとうございます。その方法なら大丈夫です。")),
        vocab=("step-free access|段差のないアクセス; reasonable accommodation|合理的配慮; accessible|利用しやすい; at your expense|そちらの負担で", "offer|提示する|CORE-45; tonight|今夜|CORE-9; meet you there|そこで会う|CTX-21", "hotel|ホテル; room|部屋; bathroom|浴室; elevator|エレベーター", "sister hotel|系列ホテル; rate difference|料金差額"),
    ),
    28: dict(
        slug="resolve-conflicting-booking-information", title="Resolve conflicting booking information", ko="상충하는 예약 정보를 해결하기", ja="食い違う予約情報を解決する", role="Hotel Clerk", scene="At check-in with conflicting breakfast information", scene_ja="朝食情報が食い違うチェックイン", situation="確認メールとホテルのシステムの内容が違うため、食い違いを示し、解決内容を書面で確認します。", goal=("Show the discrepancy and leave with written confirmation of the solution.", "情報の食い違いを示し、解決内容を書面で受け取りましょう。"), expressions=(("booking confirmation", "予約確認書"), ("discrepancy", "食い違い")),
        p1=pattern(bridge="まず、二つの情報源がどう食い違っているかを一文で示します。", meaning=("Use this fixed contrast to put two conflicting records side by side.", "食い違う二つの記録を並べて示す定型表現です。"), rows_=rows(("{t}My confirmation says breakfast is included, whereas your system says it isn't{/t}.", "{t}確認書には朝食込みとありますが、そちらのシステムでは含まれていません{/t}。", "My confirmation says|breakfast is included,|whereas your system says|it isn't."), ("{t}My email says parking is included, whereas your system says it isn't{/t}.", "{t}メールには駐車場込みとありますが、そちらのシステムでは含まれていません{/t}。", "My email says|parking is included,|whereas your system says|it isn't."), ("{t}My voucher says two nights, whereas your system says one{/t}.", "{t}バウチャーには2泊とありますが、そちらのシステムでは1泊です{/t}。", "My voucher says|two nights,|whereas your system says|one."), ("{t}My confirmation says a double room, whereas your system says a single{/t}.", "{t}確認書にはダブルルームとありますが、そちらのシステムではシングルです{/t}。", "My confirmation says|a double room,|whereas your system says|a single.")), rule=("Keep each source with its information", "情報源と内容をセットに", "Use the fixed contrast to show exactly what each record says.", "定型の対比で、それぞれの記録内容を正確に示します。", "source A says + detail, whereas + source B says + conflict", "Expose the discrepancy", "食い違いを示す", ("confirmation says · included", "system says · it isn't")), write=("Which two records would you compare, and what differs?", "どの二つの記録を比べ、何が違いますか？"), omit_rule=True),
        p2=pattern(bridge="次に、合意した解決内容を書面に残してもらいます。", meaning=("Use this to request a written record of the agreed solution.", "合意した解決内容を書面で残してもらう表現です。"), rows_=rows(("{t}Could you confirm in writing{/t} how this will be resolved?", "これをどう解決するか、{t}書面で確認していただけますか{/t}？", "Could you confirm|in writing|how this will be resolved?"), ("{t}Could you confirm in writing{/t} that breakfast is included?", "朝食が含まれることを{t}書面で確認していただけますか{/t}？", "Could you confirm|in writing|that breakfast is included?"), ("{t}Could you confirm in writing{/t} the revised price?", "修正後の料金を{t}書面で確認していただけますか{/t}？", "Could you confirm|in writing|the revised price?"), ("{t}Could you confirm in writing{/t} the room type?", "部屋タイプを{t}書面で確認していただけますか{/t}？", "Could you confirm|in writing|the room type?")), rule=("Put the record format before the detail", "記録方法を内容の前に", "Keep “in writing” beside “confirm,” then name the detail.", "in writing を confirm とセットにし、そのあとに確認内容を続けます。", "Could you confirm + in writing + detail?", "Create a record", "記録を残す", ("confirm in writing · the revised price", "confirm in writing · the room type")), write=("Which part of the solution would you want in writing?", "解決内容のどの部分を書面に残してもらいますか？")),
        scene_turns=(("other", "Our system shows that breakfast costs extra.", "当ホテルのシステムでは朝食は別料金になっています。"), ("target", 1, 0), ("other", "I can see the discrepancy in your email. We'll honor the included breakfast.", "メールの食い違いを確認できました。朝食込みの条件を適用します。"), ("target", 2, 0), ("other", "Yes. I'll email a note confirming breakfast for both mornings.", "はい。2日分の朝食を確認する文面をメールします。"), ("me", "Thank you. That resolves it.", "ありがとうございます。これで解決です。")),
        receptive=(("Our system shows that breakfast costs extra.", "The hotel record excludes breakfast", "ホテル側の記録では朝食は別料金", "The hotel record includes free breakfast", "ホテル側の記録では朝食は無料"), ("We'll honor the included breakfast.", "The hotel accepts the condition in the confirmation", "ホテルは確認書の条件を認める", "The hotel cancels the breakfast", "ホテルは朝食を取り消す"), ("I'll email a note confirming breakfast for both mornings.", "The solution will be documented by email", "解決内容はメールで記録される", "The guest must ask again each morning", "毎朝もう一度頼む必要がある"), ("There will be no extra charge.", "The guest will not pay more", "追加料金はかからない", "The guest must pay at checkout", "チェックアウト時に支払う必要がある")),
        live=("Think of a reservation detail you would verify against a confirmation.", "確認書と照合したい予約内容を一つ考えてください。", "My confirmation says ___, whereas your system says ___. Could you confirm in writing ___? / If you have no booking: I don't have a booking to check right now.", "予約がなければ、今は確認する予約がないと答えてかまいません。", "Which booking detail do you always save in writing?", "先生は予約のどの情報を必ず書面で保存しますか？"),
        tip=("Use “honor” for keeping an agreed term", "合意条件を守る honor", "Here, “honor” means accept and provide the price or benefit previously promised.", "ここで honor は、以前に約束した料金や特典を認めて提供する意味です。", ("Keep the term", "条件を守る", "We'll honor that rate.", "その料金を適用します。"), ("Check the record", "記録を確認", "Let me check the confirmation.", "確認書を確認します。")),
        transfer_title="Resolving a rental-car price discrepancy", transfer_ja="レンタカー料金の食い違いを解決する", transfer_role="Rental Agent", transfer_turns=(("other", "Our system shows a daily parking charge.", "システムでは駐車料金が1日ごとにかかります。"), ("target", 1, 1), ("other", "You're right. Your email includes parking at no extra charge.", "おっしゃる通りです。メールでは駐車料金込みです。"), ("target", 2, 2), ("other", "Certainly. I'll email the revised total now.", "承知しました。修正後の合計を今メールします。"), ("me", "Great. I'll keep that with the rental agreement.", "ありがとうございます。レンタル契約書と一緒に保管します。")),
        vocab=("booking confirmation|予約確認書; discrepancy|食い違い; honor|条件を認める", "confirm in writing|書面で確認する|CORE-60; breakfast|朝食|CORE-4; price|料金|CORE-19", "email|メール; system|システム; room|部屋; parking|駐車場", "revised total|修正後の合計; rental agreement|レンタル契約書"),
    ),
    29: dict(
        slug="make-a-safety-decision-with-incomplete-information", title="Make a safety decision with incomplete information", ko="불완전한 정보로 안전 결정을 내리기", ja="不完全な情報で安全な判断をする", role="Tour Operator", scene="Calling about a remote excursion in severe weather", scene_ja="悪天候時の遠隔地ツアーについて電話する", situation="主催者が中止していなくても安全とは限らないため、不確かな情報の中で延期を選びます。", goal=("Challenge a weak safety assumption and choose the lower-risk option.", "根拠の弱い安全判断を問い直し、よりリスクの低い選択をしましょう。"), expressions=(("err on the side of caution", "安全側に判断する"), ("weather advisory", "気象注意報")),
        p1=pattern(bridge="まず、『中止されていない＝安全』とは限らないと指摘します。", meaning=("Use this fixed line to reject a conclusion that the available fact does not prove.", "分かっている事実だけでは証明できない結論を退ける定型表現です。"), rows_=rows(("{t}The fact that it hasn't been cancelled doesn't necessarily mean it's safe{/t}.", "{t}中止されていないからといって、必ずしも安全とは限りません{/t}。", "The fact that|it hasn't been cancelled|doesn't necessarily mean|it's safe."), ("{t}The fact that the road is open doesn't necessarily mean it's safe{/t}.", "{t}道路が開いているからといって、必ずしも安全とは限りません{/t}。", "The fact that|the road is open|doesn't necessarily mean|it's safe."), ("{t}The fact that others are going doesn't necessarily mean it's safe{/t}.", "{t}ほかの人が行くからといって、必ずしも安全とは限りません{/t}。", "The fact that|others are going|doesn't necessarily mean|it's safe."), ("{t}The fact that the warning is old doesn't necessarily mean it's safe{/t}.", "{t}警告が古いからといって、必ずしも安全とは限りません{/t}。", "The fact that|the warning is old|doesn't necessarily mean|it's safe.")), rule=("Keep the caution frame intact", "慎重な判断の枠はひとまとまり", "Change the apparent reassurance, not the logic of the caution.", "安心材料に見える部分だけを変え、慎重な判断の論理は保ちます。", "The fact that + apparent reassurance + doesn't necessarily mean + safe", "Question the inference", "推論を問い直す", ("not cancelled · not necessarily safe", "road open · not necessarily safe")), write=("Which reassuring fact would not be enough to prove safety?", "安全を証明するには不十分だと思う安心材料は何ですか？"), omit_rule=True),
        p2=pattern(bridge="次に、情報が足りない中で選ぶ安全側の行動を伝えます。", meaning=("Use this fixed preference to choose caution over an avoidable risk.", "避けられる危険より慎重な選択を優先する定型表現です。"), rows_=rows(("{t}Overall, I'd rather postpone than take the risk{/t}.", "{t}総合的に考えると、危険を冒すより延期したいです{/t}。", "Overall,|I'd rather postpone|than take the risk."), ("{t}Overall, I'd rather turn back than take the risk{/t}.", "{t}総合的に考えると、危険を冒すより引き返したいです{/t}。", "Overall,|I'd rather turn back|than take the risk."), ("{t}Overall, I'd rather wait than take the risk{/t}.", "{t}総合的に考えると、危険を冒すより待ちたいです{/t}。", "Overall,|I'd rather wait|than take the risk."), ("{t}Overall, I'd rather cancel than take the risk{/t}.", "{t}総合的に考えると、危険を冒すより中止したいです{/t}。", "Overall,|I'd rather cancel|than take the risk.")), rule=("Keep the safer preference intact", "安全側の選択はひとまとまり", "Change only the safer action that replaces the risk.", "危険を避けるための安全な行動だけを入れ替えます。", "Overall + I'd rather + safer action + than take the risk", "Choose caution", "慎重な選択をする", ("rather postpone · than take the risk", "rather wait · than take the risk")), write=("What safer action would you choose in uncertain conditions?", "状況が不確かなとき、どの安全な行動を選びますか？"), omit_rule=True),
        scene_turns=(("other", "The excursion hasn't been cancelled, so it should be fine.", "ツアーは中止されていないので、大丈夫なはずです。"), ("target", 1, 0), ("other", "That's fair. The latest advisory warns of flash flooding.", "おっしゃる通りです。最新の注意報では鉄砲水への警戒が出ています。"), ("target", 2, 0), ("other", "I can move your booking to Saturday without a fee.", "手数料なしで土曜日に予約を変更できます。"), ("me", "Please do that. We'll check the advisory again on Friday.", "そうしてください。金曜日に注意報をもう一度確認します。")),
        receptive=(("It hasn't been cancelled, so it should be fine.", "The operator assumes that no cancellation means safety", "中止されていないことを安全の根拠にしている", "The operator confirms that conditions were inspected", "現地状況を確認済みだと保証している"), ("The latest advisory warns of flash flooding.", "Official guidance identifies a serious weather risk", "公的な情報が重大な気象リスクを示している", "The advisory says the weather is clear", "注意報では天候は良好だとしている"), ("I can move your booking to Saturday without a fee.", "Postponing will not cost extra", "延期しても追加料金はない", "Saturday is fully booked", "土曜日は満席である"), ("We'll check the advisory again on Friday.", "They will use updated information before going", "出発前に最新情報を確認する", "They will ignore future warnings", "今後の警告は無視する")),
        live=("Think of an activity that weather could make unsafe.", "天候によって危険になり得る活動を考えてください。", "The fact that ___ doesn't necessarily mean it's safe. Overall, I'd rather ___ than take the risk. / If none applies: I don't have an outdoor plan right now.", "該当する予定がなければ、今は屋外の予定がないと答えてかまいません。", "When do you usually decide to cancel an outdoor plan?", "先生はどんなときに屋外の予定を中止しますか？"),
        tip=("Use “advisory” below “warning”", "warning より弱い advisory", "An advisory signals possible hazardous conditions; a warning signals a more immediate or severe threat.", "advisory は危険の可能性、warning はより差し迫った、または深刻な危険を示します。", ("Possible hazard", "危険の可能性", "a weather advisory", "気象注意報"), ("More serious threat", "より重大な危険", "a weather warning", "気象警報")),
        transfer_title="Deciding whether to drive through mountain snow", transfer_ja="山間部の雪道を運転するか判断する", transfer_role="Rental Agent", transfer_turns=(("other", "The mountain road is open, so you can still drive through.", "山道は開いているので、まだ通行できます。"), ("target", 1, 1), ("other", "The forecast now says heavy snow after six.", "最新予報では6時以降に大雪となっています。"), ("target", 2, 2), ("other", "I can extend the rental until tomorrow morning at no charge.", "追加料金なしで明日の朝までレンタルを延長できます。"), ("me", "Let's do that. We'll leave after the road is checked.", "そうしましょう。道路の確認後に出発します。")),
        vocab=("err on the side of caution|安全側に判断する; weather advisory|気象注意報; flash flooding|鉄砲水", "necessarily|必ずしも|CORE-117; rather|むしろ|CORE-117; safe|安全な|CORE-65; cancel|中止する|CORE-36", "road|道路; Saturday|土曜日; snow|雪; morning|朝", "hazardous|危険な; severe threat|重大な危険"),
    ),
    30: dict(
        slug="give-useful-advice-after-a-complicated-trip", title="Give useful advice after a complicated trip", ko="복잡한 여행 후 유용한 조언하기", ja="複雑な旅行のあとで役立つ助言をする", role="Colleague", scene="Talking to a colleague planning the same route", scene_ja="同じルートを計画する同僚との会話", situation="実体験をもとに、乗り継ぎの余裕とそのルートを選ぶ条件を具体的に助言します。", goal=("Turn a difficult travel experience into specific, conditional advice.", "大変だった旅行経験を、具体的で条件付きの助言に変えましょう。"), expressions=(("with hindsight", "振り返ってみると"), ("build in extra time", "余裕時間を見込む")),
        p1=pattern(bridge="まず、一番役に立つ改善策を具体的にすすめます。", meaning=("Use this to present one recommendation as the main takeaway from your experience.", "自分の経験から得た最も重要な助言を一つ示す表現です。"), rows_=rows(("{t}What I'd recommend is{/t} allowing an extra day for the connection.", "私が{t}おすすめするのは{/t}、乗り継ぎに1日余分に取ることです。", "What I'd recommend|is allowing|an extra day|for the connection."), ("{t}What I'd recommend is{/t} booking the morning train in advance.", "私が{t}おすすめするのは{/t}、朝の列車を事前に予約することです。", "What I'd recommend|is booking|the morning train|in advance."), ("{t}What I'd recommend is{/t} taking the morning ferry if possible.", "私が{t}おすすめするのは{/t}、できれば朝のフェリーを利用することです。", "What I'd recommend|is taking|the morning ferry|if possible."), ("{t}What I'd recommend is{/t} checking the visa rules early.", "私が{t}おすすめするのは{/t}、ビザの規則を早めに確認することです。", "What I'd recommend|is checking|the visa rules|early.")), rule=("Put the practical action after “is”", "実用的な行動は is のあと", "Give one action the listener can actually take.", "相手が実際に取れる行動を一つ示します。", "What I'd recommend + is + action", "Give the takeaway", "要点を助言する", ("is · allowing an extra day", "is · taking the morning ferry")), write=("What single action would you recommend for a difficult route?", "難しいルートについて、どんな行動を一つすすめますか？")),
        p2=pattern(bridge="次に、そのルートを選んでもよい条件をはっきり示します。", meaning=("Use this to recommend an option only when the listener meets an important condition.", "重要な条件を満たす場合に限って選択肢をすすめる表現です。"), rows_=rows(("{t}I'd only take that route if{/t} you have some flexibility.", "ある程度予定を調整できる{t}場合にだけ、そのルートを選びます{/t}。", "I'd only take|that route|if you have|some flexibility."), ("{t}I'd only book that flight if{/t} you can stay an extra night.", "もう1泊できる{t}場合にだけ、その便を予約します{/t}。", "I'd only book|that flight|if you can stay|an extra night."), ("{t}I'd only use that airport if{/t} you have a long connection.", "乗り継ぎ時間が長い{t}場合にだけ、その空港を使います{/t}。", "I'd only use|that airport|if you have|a long connection."), ("{t}I'd only travel in winter if{/t} you can change your dates.", "日程を変更できる{t}場合にだけ、冬に旅行します{/t}。", "I'd only travel|in winter|if you can change|your dates.")), rule=("Put the required condition after “if”", "必要条件は if のあと", "Make the condition specific enough to guide the listener's decision.", "相手が判断できるよう、条件を具体的にします。", "I'd only + option + if + condition", "Limit the advice", "助言に条件を付ける", ("take that route · if you have flexibility", "book that flight · if you can stay")), write=("Under what condition would you still recommend the route?", "どんな条件なら、そのルートをすすめますか？")),
        scene_turns=(("other", "I'm thinking of taking the same three-flight route you used.", "あなたが使ったのと同じ3便乗り継ぎのルートを考えています。"), ("target", 1, 0), ("other", "Was the connection really that unreliable?", "乗り継ぎは本当にそれほど不安定でしたか？"), ("me", "Yes. One delay cost me the next flight.", "はい。1便の遅れで次の便に乗れませんでした。"), ("target", 2, 0), ("other", "I can't change my dates, so I'll choose the direct route instead.", "日程を変えられないので、代わりに直行ルートを選びます。")),
        receptive=(("I'm thinking of taking the same three-flight route.", "The colleague is considering the complicated itinerary", "同僚は複雑な旅程を検討している", "The colleague has already completed the trip", "同僚はすでに旅行を終えた"), ("One delay cost me the next flight.", "A delay caused a missed connection", "遅延で乗り継ぎに失敗した", "The next flight waited for the traveler", "次の便が旅行者を待った"), ("I can't change my dates.", "The colleague lacks schedule flexibility", "同僚は日程を変えられない", "The colleague can add several days", "同僚は数日追加できる"), ("I'll choose the direct route instead.", "The advice changes the colleague's choice", "助言を受けて別のルートを選ぶ", "The colleague ignores the risk", "同僚はリスクを無視する")),
        live=("Give advice about a route you know, or use an imaginary one.", "知っているルートについて助言するか、架空のルートで答えてください。", "What I'd recommend is ___. I'd only take that route if ___. / If you do not travel: I don't travel much, but I'd recommend ___.", "旅行しない場合は、旅行経験が少ないと伝えてから仮の助言をしてください。", "What travel advice would you give me?", "先生なら私にどんな旅行の助言をしますか？"),
        tip=("Use “build in” for planned buffer time", "余裕時間を組み込む build in", "“Build in extra time” means add the buffer when you make the plan, not after a delay.", "build in extra time は、遅延後ではなく計画時に余裕時間を組み込む意味です。", ("Plan the buffer", "余裕を計画", "Build in an extra hour.", "1時間余裕を見込んでください。"), ("React later", "あとで対応", "Allow more time next time.", "次回はもっと時間を取ってください。")),
        transfer_title="Advising a friend about a difficult ferry route", transfer_ja="難しいフェリールートについて友人に助言する", transfer_role="Friend", transfer_turns=(("other", "I'm planning the island ferry route you took last winter.", "去年の冬にあなたが使った島へのフェリールートを計画しています。"), ("target", 1, 2), ("other", "Does the first morning flight make a difference?", "朝一番の便なら違いがありますか？"), ("target", 2, 3), ("other", "My dates are fixed, so I'll travel in spring instead.", "日程は固定なので、代わりに春に旅行します。"), ("me", "That should make the trip much easier.", "そのほうが旅はずっと楽になるはずです。")),
        vocab=("with hindsight|振り返ってみると; build in extra time|余裕時間を見込む; flexibility|調整の余地", "what I'd recommend|私がおすすめすること|CORE-103; only if|場合にだけ|CORE-66; route|ルート|CORE-59", "flight|便; airport|空港; winter|冬; morning|朝", "buffer time|余裕時間; unreliable|不安定な"),
    ),
    31: dict(
        slug="introduce-your-role-on-a-new-project", title="Introduce your role on a new project", ko="새 프로젝트에서 역할 소개하기", ja="新しいプロジェクトで役割を紹介する", role="Project Lead", scene="A kickoff call with a new project team", scene_ja="新しいプロジェクトのキックオフ通話", situation="自分の担当と主に連携するチームを伝え、何について連絡してほしいかを明確にします。", goal=("Introduce your remit so the new team knows when to contact you.", "担当範囲を紹介し、どんなときに連絡すればよいかをチームに伝えましょう。"), expressions=(("nice to e-meet you", "オンラインでお会いできてうれしいです"), ("point of contact", "窓口担当者")),
        p1=pattern(bridge="まず、自分が担当する仕事を一つ伝えます。", meaning=("Use this to name the work that belongs to your role.", "自分の役割として担当する仕事を示す表現です。"), rows_=rows(("{t}I'm responsible for{/t} the project schedule.", "プロジェクトの予定を{t}担当しています{/t}。", "I'm responsible for|the project schedule|on this project."), ("{t}I'm responsible for{/t} the weekly report.", "週次報告を{t}担当しています{/t}。", "I'm responsible for|the weekly report|on this project."), ("{t}I'm responsible for{/t} client updates.", "顧客への進捗共有を{t}担当しています{/t}。", "I'm responsible for|client updates|on this project."), ("{t}I'm responsible for{/t} the final review.", "最終確認を{t}担当しています{/t}。", "I'm responsible for|the final review|on this project.")), rule=("Keep “responsible for” with the duty", "responsible for と担当業務をセットに", "Name the specific work, not only your job title.", "役職名だけでなく、具体的な担当業務を示します。", "I'm responsible for + duty", "Define your remit", "担当範囲を示す", ("responsible for · the schedule", "responsible for · client updates")), write=("What should this project team contact you about?", "このプロジェクトで、どんなことについてあなたに連絡すればよいですか？")),
        p2=pattern(bridge="次に、普段いちばん連携する相手を伝えます。", meaning=("Use this to identify the team you collaborate with most often.", "最も頻繁に連携するチームを示す表現です。"), rows_=rows(("{t}I mainly work with{/t} the design team.", "主にデザインチームと{t}一緒に働いています{/t}。", "I mainly work with|the design team|on this project."), ("{t}I mainly work with{/t} the sales team.", "主に営業チームと{t}一緒に働いています{/t}。", "I mainly work with|the sales team|on this project."), ("{t}I mainly work with{/t} the finance team.", "主に財務チームと{t}一緒に働いています{/t}。", "I mainly work with|the finance team|on this project."), ("{t}I mainly work with{/t} the engineering team.", "主にエンジニアリングチームと{t}一緒に働いています{/t}。", "I mainly work with|the engineering team|on this project.")), rule=("Put the collaborator after “with”", "連携相手は with のあと", "Use a team or group of people after the intact frame.", "ひとまとまりの表現のあとに、チームや人の集団を続けます。", "I mainly work with + team", "Name the collaboration", "連携相手を示す", ("work with · the design team", "work with · the sales team")), write=("Which team do you work with most often?", "どのチームと最もよく連携しますか？")),
        scene_turns=(("other", "Welcome to the kickoff. Could you introduce your role?", "キックオフへようこそ。担当を紹介してもらえますか？"), ("target", 1, 0), ("other", "Great. Who will you coordinate with most?", "分かりました。主にどのチームと連携しますか？"), ("target", 2, 0), ("other", "Perfect. We'll send schedule questions to you and copy design.", "では、日程の質問はあなたに送り、デザインチームもCCに入れます。"), ("me", "Sounds good. Nice to e-meet everyone.", "分かりました。皆さん、オンラインでお会いできてうれしいです。")),
        receptive=(("Could you introduce your role?", "The lead wants to know the learner's responsibility", "担当業務を尋ねている", "The lead wants the learner's home address", "自宅住所を尋ねている"), ("Who will you coordinate with most?", "The lead asks about the main partner team", "主な連携チームを尋ねている", "The lead asks who approves vacation", "休暇を承認する人を尋ねている"), ("We'll send schedule questions to you.", "The learner will be the schedule contact", "日程に関する窓口になる", "Design will handle every schedule question", "日程の質問はすべてデザインが担当する"), ("We'll copy design.", "The design team will also receive the message", "デザインチームにもメールが届く", "The design team will be removed from the project", "デザインチームはプロジェクトから外れる")),
        live=("Introduce your real project role, or choose an imaginary one.", "実際のプロジェクトでの役割を紹介するか、架空の役割を選んでください。", "I'm responsible for ___. I mainly work with ___. / If you have no project: I'm not on a project right now, but I'd like to work with ___.", "プロジェクトがなければ、今は参加していないと伝えてから希望を答えてください。", "What are you responsible for, and who do you mainly work with?", "先生は何を担当し、主に誰と働いていますか？"),
        tip=("Use “remit” for an area of responsibility", "担当範囲を表す remit", "“Role” can mean your position; “remit” focuses on the work you are responsible for.", "role は立場、remit は担当する仕事の範囲に焦点を当てます。", ("Position", "立場", "What's your role?", "役割は何ですか？"), ("Responsibility area", "担当範囲", "What's your remit?", "担当範囲は何ですか？")),
        transfer_title="Introducing your role at a client workshop", transfer_ja="顧客ワークショップで役割を紹介する", transfer_role="Client Manager", transfer_turns=(("other", "Before we start, what will you handle today?", "始める前に、今日は何を担当しますか？"), ("target", 1, 2), ("other", "And which internal team supports those updates?", "その進捗共有を支える社内チームはどこですか？"), ("target", 2, 1), ("other", "Good. I'll send questions to you and the sales team.", "分かりました。質問はあなたと営業チームに送ります。"), ("me", "Perfect. I'm happy to be your point of contact.", "ありがとうございます。窓口を担当します。")),
        vocab=("project schedule|プロジェクト予定; kickoff|キックオフ; point of contact|窓口担当者; remit|担当範囲", "responsible for|担当している|CORE-81; mainly work with|主に連携する|CORE-81; team|チーム|CORE-81", "project|プロジェクト; design|デザイン; sales|営業; report|報告", "coordinate|連携する; copy|CCに入れる"),
    ),
    32: dict(
        slug="repair-a-bad-connection-during-a-call", title="Repair a bad connection during a call", ko="통화 연결 문제 해결하기", ja="通話の接続不良を立て直す", role="Meeting Host", scene="A video call when the audio cuts out", scene_ja="音声が途切れるビデオ通話", situation="音声が途切れた位置を示し、聞き取れなかった締め切りをもう一度言ってもらいます。", goal=("Identify where the audio failed and recover the missed deadline accurately.", "音声が途切れた箇所を示し、聞き逃した締め切りを正確に確認しましょう。"), expressions=(("you're breaking up", "音声が途切れています"), ("close of business", "営業時間終了時")),
        p1=pattern(bridge="まず、どこから聞こえなかったかを具体的に伝えます。", meaning=("Use this to pinpoint the last word you heard before the connection failed.", "接続が切れる直前に聞こえた最後の言葉を示す表現です。"), rows_=rows(("Sorry, you {t}cut out after{/t} 'Friday'.", "すみません、「Friday」のあとで{t}音声が途切れました{/t}。", "Sorry,|you cut out|after 'Friday'."), ("Sorry, you {t}cut out after{/t} 'budget'.", "すみません、「budget」のあとで{t}音声が途切れました{/t}。", "Sorry,|you cut out|after 'budget'."), ("Sorry, you {t}cut out after{/t} 'send it'.", "すみません、「send it」のあとで{t}音声が途切れました{/t}。", "Sorry,|you cut out|after 'send it'."), ("Sorry, you {t}cut out after{/t} 'the client'.", "すみません、「the client」のあとで{t}音声が途切れました{/t}。", "Sorry,|you cut out|after 'the client'.")), rule=("Name the last clear words after “after”", "最後に聞こえた語は after のあと", "Quote the final words you actually heard.", "実際に最後まで聞こえた言葉を引用します。", "Sorry + you cut out after + last clear words", "Locate the gap", "聞こえなかった箇所を示す", ("cut out after · Friday", "cut out after · the client")), write=("What last clear word would you quote?", "最後に聞こえたどの言葉を引用しますか？")),
        p2=pattern(bridge="次に、必要な情報だけをもう一度言ってもらいます。", meaning=("Use this to ask specifically for the missed deadline rather than the whole discussion.", "会話全体ではなく、聞き逃した締め切りだけをもう一度尋ねる表現です。"), rows_=rows(("{t}Could you repeat{/t} the deadline?", "締め切りを{t}もう一度言っていただけますか{/t}？", "Could you repeat|the deadline|for me?"), ("{t}Could you repeat{/t} the date?", "日付を{t}もう一度言っていただけますか{/t}？", "Could you repeat|the date|for me?"), ("{t}Could you repeat{/t} the last point?", "最後の点を{t}もう一度言っていただけますか{/t}？", "Could you repeat|the last point|for me?"), ("{t}Could you repeat{/t} the client name?", "顧客名を{t}もう一度言っていただけますか{/t}？", "Could you repeat|the client name|for me?")), rule=("Name only the information you missed", "聞き逃した情報だけを示す", "A specific noun makes the repair faster and more accurate.", "具体的な名詞を使うと、より早く正確に聞き直せます。", "Could you repeat + missed information?", "Repair the gap", "聞き逃しを修復", ("repeat · the deadline", "repeat · the client name")), write=("Which piece of information would you ask them to repeat?", "どの情報をもう一度言ってもらいますか？")),
        scene_turns=(("other", "Please send the revised slides by Friday—", "修正版のスライドを金曜日までに送ってください。それから—"), ("target", 1, 0), ("other", "Of course. I said the final deadline has changed.", "もちろんです。最終締め切りが変更になったと言いました。"), ("target", 2, 0), ("other", "The deadline is Friday at five your time.", "締め切りは、あなたの時間で金曜日の5時です。"), ("me", "Got it. Friday at five my time.", "分かりました。私の時間で金曜日の5時ですね。")),
        receptive=(("Please send the revised slides by Friday—", "The speaker begins giving a delivery deadline", "提出期限を伝え始めている", "The speaker cancels the slide deck", "スライド資料を取り消している"), ("Friday at close of business.", "The deadline is the end of Friday's workday", "締め切りは金曜日の業務終了時", "The deadline is Friday morning", "締め切りは金曜日の朝"), ("Friday at five your time.", "The time is stated in the listener's time zone", "聞き手側の時刻で5時", "The time is stated in the speaker's time zone", "話し手側の時刻で5時"), ("Got it.", "The listener now understands the deadline", "聞き手は締め切りを理解した", "The connection is still completely silent", "接続はまだ完全に無音である")),
        live=("Imagine one detail drops out of a call. Repair the gap precisely.", "通話で一つの情報が聞こえなかったと想定し、具体的に聞き直してください。", "Sorry, you cut out after '___.’ Could you repeat ___? / If your calls are usually clear: My calls are usually clear, but I'd say ___.", "普段問題がなければ、通常は明瞭だと伝えてから仮に答えてください。", "What do you say when a call starts breaking up?", "先生は通話が途切れ始めたら何と言いますか？"),
        tip=("Use “cut out” for a gap, “break up” for repeated gaps", "一度なら cut out、繰り返すなら break up", "“You cut out” points to one missing stretch; “you're breaking up” describes ongoing choppy audio.", "you cut out は一度の欠落、you're breaking up は音声が継続的に途切れる状態です。", ("One gap", "一度の欠落", "You cut out after Friday.", "Friday のあとで途切れました。"), ("Ongoing problem", "続く問題", "You're breaking up.", "音声が途切れています。")),
        transfer_title="Repairing a phone call with a supplier", transfer_ja="取引先との電話を立て直す", transfer_role="Supplier", transfer_turns=(("other", "About the replacement budget—", "交換品の予算についてですが—"), ("target", 1, 1), ("other", "I said the budget approval is still pending.", "予算の承認はまだ保留中だと言いました。"), ("target", 2, 2), ("other", "Certainly. The last point was that shipping starts after approval.", "承知しました。最後の点は、承認後に発送が始まるということです。"), ("me", "Thanks. I'll note that in the update.", "ありがとうございます。進捗報告に記載します。")),
        vocab=("cut out|音声が途切れる; break up|音声が途切れ続ける; close of business|営業時間終了時", "repeat|繰り返す|CORE-24; deadline|締め切り|CORE-82; Friday|金曜日|CORE-9", "call|通話; date|日付; client|顧客; slides|スライド", "choppy audio|途切れがちな音声"),
    ),
    33: dict(
        slug="schedule-across-time-zones", title="Schedule across time zones", ko="시차를 고려해 일정 잡기", ja="時差をまたいで日程を決める", role="Project Partner", scene="Scheduling a call across three countries", scene_ja="3か国をまたぐ通話の日程調整", situation="最初の候補が自分には深夜になることを伝え、全員が参加できる別の時間を提案します。", goal=("Explain the local-time conflict and agree on a workable meeting slot.", "現地時刻の問題を伝え、参加可能な会議時間に合意しましょう。"), expressions=(("your time", "そちらの時間で"), ("calendar invite", "カレンダー招待")),
        p1=pattern(bridge="まず、提案された時刻が自分の現地時間では何時か伝えます。", meaning=("Use this fixed line to show the local-time consequence of a proposed slot.", "提案された時間が自分の現地時間でどうなるかを示す定型表現です。"), rows_=rows(("{t}That would be midnight for me{/t}.", "{t}それだと私には深夜0時になります{/t}。", "That would be|midnight|for me."), ("{t}That would be 2 a.m. for me{/t}.", "{t}それだと私には午前2時になります{/t}。", "That would be|2 a.m.|for me."), ("{t}That would be 6 a.m. for me{/t}.", "{t}それだと私には午前6時になります{/t}。", "That would be|6 a.m.|for me."), ("{t}That would be during lunch for me{/t}.", "{t}それだと私には昼休み中になります{/t}。", "That would be|during lunch|for me.")), rule=("Keep the local-time line intact", "現地時刻の文はひとまとまり", "Change only the actual local time or conflict.", "実際の現地時刻や都合の悪い時間だけを変えます。", "That would be + local time + for me", "Expose the conflict", "時差の問題を示す", ("midnight · for me", "during lunch · for me")), write=("What local time would make a proposed meeting difficult?", "どの現地時刻だと会議が難しくなりますか？"), omit_rule=True),
        p2=pattern(bridge="次に、より参加しやすい具体的な時間を提案します。", meaning=("Use this fixed request to move the meeting to a specific alternative slot.", "会議を具体的な別の時間へ動かす定型の依頼です。"), rows_=rows(("{t}Could we move it to Friday morning instead{/t}?", "{t}代わりに金曜日の朝へ変更できますか{/t}？", "Could we move it|to Friday morning|instead?"), ("{t}Could we move it to Thursday afternoon instead{/t}?", "{t}代わりに木曜日の午後へ変更できますか{/t}？", "Could we move it|to Thursday afternoon|instead?"), ("{t}Could we move it to nine your time instead{/t}?", "{t}代わりにそちらの時間の9時へ変更できますか{/t}？", "Could we move it|to nine your time|instead?"), ("{t}Could we move it to next Monday instead{/t}?", "{t}代わりに来週月曜日へ変更できますか{/t}？", "Could we move it|to next Monday|instead?")), rule=("Keep the new slot after “to”", "新しい時間は to のあと", "Add “instead” to mark the slot as a replacement.", "instead を加えて、代わりの時間であることを示します。", "Could we move it + to new slot + instead?", "Offer the replacement", "代案を提示", ("to Friday morning · instead", "to nine your time · instead")), write=("Which alternative time would work across the time zones?", "時差をまたいで都合のよい代わりの時間はいつですか？"), omit_rule=True),
        scene_turns=(("other", "Could everyone meet Thursday at three p.m. London time?", "全員、ロンドン時間の木曜日午後3時に会えますか？"), ("target", 1, 0), ("other", "Thanks for catching that. What time would work better?", "気づいてくれてありがとうございます。何時ならよいですか？"), ("target", 2, 0), ("other", "Friday morning works in all three locations. I'll send the invite.", "金曜日の朝なら3地域すべてで大丈夫です。招待を送ります。"), ("me", "Great. Please include each local time in the invite.", "ありがとうございます。招待には各現地時刻を入れてください。")),
        receptive=(("Thursday at three p.m. London time?", "The proposed slot is stated in London's time zone", "提案時刻はロンドン時間で示されている", "The slot is already in everyone's local time", "全員の現地時間で示されている"), ("Thanks for catching that.", "The partner appreciates the time-zone correction", "時差の問題への指摘に感謝している", "The partner rejects the correction", "時差の指摘を拒否している"), ("Friday morning works in all three locations.", "The replacement is acceptable across the three regions", "代案は3地域すべてで参加可能", "Only one location can attend", "1地域しか参加できない"), ("I'll send the invite.", "The agreed time will be added to the calendar", "合意した時間がカレンダーに送られる", "The meeting remains unscheduled", "会議は未定のままである")),
        live=("Choose a real or imaginary cross-time-zone meeting.", "実際または架空の時差をまたぐ会議を選んでください。", "That would be ___ for me. Could we move it to ___ instead? / If you never schedule globally: I don't schedule across time zones, but ___ would be difficult.", "海外との日程調整をしない場合は、経験がないと伝えてから仮に答えてください。", "Which meeting time is easiest for you?", "先生にとって最も参加しやすい会議時間はいつですか？"),
        tip=("Write the time zone, not just the city", "都市名だけでなくタイムゾーンを記載", "Calendar invites are clearer with a time-zone label such as JST or UTC.", "カレンダー招待では、JST や UTC などのタイムゾーン表記があると明確です。", ("Local label", "現地表記", "Friday, 9 a.m. JST", "金曜日 午前9時 JST"), ("Shared reference", "共通基準", "Friday, 00:00 UTC", "金曜日 00:00 UTC")),
        transfer_title="Rescheduling a global training session", transfer_ja="国際研修の日程を変更する", transfer_role="Training Coordinator", transfer_turns=(("other", "The training is set for Tuesday at five p.m. New York time.", "研修はニューヨーク時間の火曜日午後5時です。"), ("target", 1, 1), ("other", "That's too late for your region. What do you suggest?", "そちらの地域には遅すぎますね。何時がよいですか？"), ("target", 2, 2), ("other", "Nine my time works for every office. I'll update the invite.", "こちらの9時なら全拠点で大丈夫です。招待を更新します。"), ("me", "Thanks. Please list UTC as well.", "ありがとうございます。UTCも記載してください。")),
        vocab=("time zone|タイムゾーン; midnight|深夜0時; calendar invite|カレンダー招待; UTC|協定世界時", "move it to|変更する|CORE-60; Friday|金曜日|CORE-9; morning|朝|CORE-3", "meeting|会議; Thursday|木曜日; Monday|月曜日; lunch|昼食", "local time|現地時刻; region|地域"),
    ),
    34: dict(
        slug="request-the-correct-file-and-explain-why", title="Request the correct file and explain why", ko="올바른 파일을 요청하고 이유 설명하기", ja="正しいファイルを依頼して理由を伝える", role="Designer", scene="Finding an outdated presentation in a shared folder", scene_ja="共有フォルダに古い資料がある場面", situation="共有フォルダの資料が古いため、最新版を受け取り、ほかの人が迷わないよう古いファイルも差し替えてもらいます。", goal=("Get the current file and prevent the outdated copy from being reused.", "最新版を受け取り、古いコピーが再利用されないようにしましょう。"), expressions=(("latest version", "最新版"), ("version history", "変更履歴")),
        p1=pattern(bridge="まず、作業に必要な最新版を丁寧に頼みます。", meaning=("Use this to request the most current copy of a file.", "ファイルの最も新しい版を依頼する表現です。"), rows_=rows(("{t}Could you send me{/t} the latest version?", "最新版を{t}送っていただけますか{/t}？", "Could you send me|the latest version|today?"), ("{t}Could you send me{/t} the final slides?", "最終版のスライドを{t}送っていただけますか{/t}？", "Could you send me|the final slides|today?"), ("{t}Could you send me{/t} the updated budget?", "更新済みの予算を{t}送っていただけますか{/t}？", "Could you send me|the updated budget|today?"), ("{t}Could you send me{/t} the approved file?", "承認済みのファイルを{t}送っていただけますか{/t}？", "Could you send me|the approved file|today?")), rule=("Put the needed file after “send me”", "必要なファイルは send me のあと", "Name the version precisely so the sender can identify it.", "送信者が特定できるよう、版を正確に示します。", "Could you send me + exact file?", "Get the right copy", "正しいコピーを受け取る", ("send me · the latest version", "send me · the approved file")), write=("Which exact file version do you need?", "どの版のファイルが必要ですか？")),
        p2=pattern(bridge="次に、共有フォルダの古いファイルも差し替えてもらいます。", meaning=("Use this follow-up to request a second action that prevents the same mix-up.", "同じ取り違えを防ぐため、二つ目の対応を頼む表現です。"), rows_=rows(("Yes, so {t}could you also replace{/t} the one in the shared folder?", "はい、それでは共有フォルダのものも{t}差し替えていただけますか{/t}？", "Yes, so|could you also replace|the one|in the shared folder?"), ("Yes, so {t}could you also replace{/t} the old attachment today?", "はい、それでは古い添付ファイルも今日{t}差し替えていただけますか{/t}？", "Yes, so|could you also replace|the old attachment|today?"), ("Yes, so {t}could you also replace{/t} the draft online?", "はい、それではオンラインの下書きも{t}差し替えていただけますか{/t}？", "Yes, so|could you also replace|the draft|online?"), ("Yes, so {t}could you also replace{/t} the copy in the project folder?", "はい、それではプロジェクトフォルダのコピーも{t}差し替えていただけますか{/t}？", "Yes, so|could you also replace|the copy|in the project folder?")), rule=("Use “also” for the linked second action", "関連する二つ目の対応には also", "Connect the cleanup request to the file you just received.", "受け取ったファイルに関連する整理の依頼としてつなげます。", "Yes, so + could you also replace + old copy?", "Prevent reuse", "再利用を防ぐ", ("also replace · the old attachment", "also replace · the copy online")), write=("Which outdated copy should be replaced as well?", "古いコピーをどこで差し替える必要がありますか？")),
        scene_turns=(("other", "The presentation is in the shared folder.", "資料は共有フォルダにあります。"), ("me", "That file still has last month's prices.", "そのファイルには先月の料金が残っています。"), ("target", 1, 0), ("other", "Yes. I have the approved deck on my laptop.", "はい。承認済みの資料が手元のPCにあります。"), ("target", 2, 0), ("other", "Absolutely. I'll send the final deck and replace the old file now.", "もちろんです。最終版を送り、古いファイルも今差し替えます。")),
        receptive=(("The presentation is in the shared folder.", "The designer points to the shared copy", "共有されているコピーを示している", "The designer says no file exists", "ファイルは存在しないと言っている"), ("That file still has last month's prices.", "The shared copy contains outdated information", "共有コピーの情報は古い", "The shared copy has today's approved prices", "共有コピーには本日の承認済み料金がある"), ("I have the approved deck on my laptop.", "A newer approved copy is available", "より新しい承認済み版がある", "Every copy has been deleted", "すべてのコピーが削除された"), ("I'll replace the old file now.", "The shared folder will be corrected", "共有フォルダが更新される", "The outdated copy will stay in place", "古いコピーはそのまま残る")),
        live=("Think of a file you might need from a colleague.", "同僚から受け取る必要がありそうなファイルを考えてください。", "Could you send me ___? Yes, so could you also replace ___? / If you do not share files: I don't share work files, but I'd ask for ___.", "仕事のファイルを共有しない場合は、そのことを伝えてから仮に答えてください。", "How do you keep shared files current?", "先生は共有ファイルをどのように最新版に保っていますか？"),
        tip=("Use “latest” until a file is approved", "承認前は latest", "“Latest” means most recent; “final” suggests that no more changes are expected.", "latest は最も新しい版、final は今後変更しない予定の版を示します。", ("Still changing", "まだ変更中", "the latest version", "最新版"), ("Approved endpoint", "承認済みの最終版", "the final version", "最終版")),
        transfer_title="Replacing an outdated contract template", transfer_ja="古い契約書テンプレートを差し替える", transfer_role="Operations Partner", transfer_turns=(("other", "I attached the contract template from the team drive.", "チームドライブの契約書テンプレートを添付しました。"), ("me", "That copy still has the old address.", "そのコピーには古い住所が残っています。"), ("target", 1, 3), ("other", "Yes. I have the approved file from legal.", "はい。法務承認済みのファイルがあります。"), ("target", 2, 3), ("other", "Sure. I'll send it and replace the project-folder copy.", "承知しました。送付し、プロジェクトフォルダのコピーも差し替えます。")),
        vocab=("latest version|最新版; version history|変更履歴; shared folder|共有フォルダ", "could you send me|送っていただけますか|CORE-20; could you also|追加でしていただけますか|CORE-20; final version|最終版|CORE-83", "file|ファイル; slides|スライド; project|プロジェクト; laptop|ノートPC", "outdated|古い; approved deck|承認済み資料"),
    ),
    35: dict(
        slug="give-a-concise-progress-update", title="Give a concise progress update", ko="간결하게 진행 상황 보고하기", ja="簡潔に進捗を報告する", role="Team Lead", scene="Giving a thirty-second weekly update", scene_ja="30秒の週次進捗報告", situation="完了した作業を数で示し、次に必要な二つの対応を簡潔に伝えます。", goal=("Give a brief update with measurable progress and a clear next step.", "測定できる進捗と明確な次の行動を短く報告しましょう。"), expressions=(("on track", "予定どおり"), ("outstanding items", "未完了項目")),
        p1=pattern(bridge="まず、全体のうち完了した数を具体的に伝えます。", meaning=("Use this to quantify completed work in a short status update.", "短い進捗報告で、完了した作業を数で示す表現です。"), rows_=rows(("We {t}finished three of the five{/t} reviews.", "5件のレビューのうち3件を{t}終えました{/t}。", "We finished|three|of the five reviews."), ("We {t}finished four of the six{/t} interviews.", "6件の面談のうち4件を{t}終えました{/t}。", "We finished|four|of the six interviews."), ("We {t}finished two of the three{/t} reports.", "3本のレポートのうち2本を{t}終えました{/t}。", "We finished|two|of the three reports."), ("We {t}finished seven of the eight{/t} checks.", "8項目の確認のうち7項目を{t}終えました{/t}。", "We finished|seven|of the eight checks.")), rule=("Put the completed count before the total", "完了数を全体数の前に", "Use “of” to connect completed work to the full set.", "of を使って、完了数と全体数をつなぎます。", "finished + completed number + of + total", "Quantify progress", "進捗を数で示す", ("three · of the five", "four · of the six")), write=("What countable work could you report as completed?", "数で示せる完了済みの作業は何ですか？")),
        p2=pattern(bridge="次に、これから必要な対応を優先順に示します。", meaning=("Use this to state the immediate actions that follow the progress update.", "進捗報告に続く、直近の必要な行動を示す表現です。"), rows_=rows(("Next, we {t}need to confirm{/t} the budget and timeline.", "次に、予算とスケジュールを{t}確認する必要があります{/t}。", "Next,|we need to confirm|the budget|and timeline."), ("Next, we {t}need to confirm{/t} the owner and deadline.", "次に、担当者と締め切りを{t}確認する必要があります{/t}。", "Next,|we need to confirm|the owner|and deadline."), ("Next, we {t}need to confirm{/t} the date and location.", "次に、日付と場所を{t}確認する必要があります{/t}。", "Next,|we need to confirm|the date|and location."), ("Next, we {t}need to confirm{/t} the price and scope.", "次に、料金と範囲を{t}確認する必要があります{/t}。", "Next,|we need to confirm|the price|and scope.")), rule=("Use “Next” to mark the action", "次の行動は Next で示す", "Name only the immediate items that still need confirmation.", "まだ確認が必要な直近の項目だけを示します。", "Next + we need to confirm + items", "Move the update forward", "次の行動へ進める", ("confirm · budget and timeline", "confirm · owner and deadline")), write=("Which two items need confirmation next?", "次に確認する必要がある二つの項目は何ですか？")),
        scene_turns=(("other", "Can you give us the short version of this week's progress?", "今週の進捗を短く報告してもらえますか？"), ("target", 1, 0), ("other", "Good. Are we still on track for the launch?", "順調ですね。公開予定にはまだ間に合いますか？"), ("me", "Yes, but two items are still outstanding.", "はい。ただし、まだ2項目が未完了です。"), ("target", 2, 0), ("other", "Understood. I'll set up a budget and timeline check this afternoon.", "分かりました。今日の午後に予算とスケジュールの確認を設定します。")),
        receptive=(("Give us the short version.", "The lead wants a concise summary", "簡潔な要約を求めている", "The lead wants every background detail", "背景をすべて詳しく求めている"), ("Are we still on track for the launch?", "The lead asks whether the schedule is healthy", "公開予定どおり進んでいるか尋ねている", "The lead asks who designed the launch page", "公開ページのデザイナーを尋ねている"), ("Two items are still outstanding.", "Two tasks remain unfinished", "2項目がまだ未完了", "Every task is complete", "すべて完了している"), ("I'll set up a budget and timeline check.", "The lead creates a concrete follow-up", "具体的な確認の場を設定する", "The lead postpones all decisions indefinitely", "すべての判断を無期限に延期する")),
        live=("Give a real or imaginary thirty-second project update.", "実際または架空のプロジェクトについて30秒で進捗を報告してください。", "We finished ___ of the ___. Next, we need to confirm ___. / If you have no project: I don't have a current project, but a sample update is ___.", "プロジェクトがなければ、今はないと伝えてから例を作ってください。", "What are you working on, and what comes next?", "先生は何に取り組んでいて、次に何をしますか？"),
        tip=("Use “outstanding” for work still open", "未完了を表す outstanding", "In project updates, “outstanding” often means unresolved or not yet completed, not excellent.", "進捗報告の outstanding は、多くの場合「素晴らしい」ではなく「未解決・未完了」を意味します。", ("Project status", "進捗状況", "Two items are outstanding.", "2項目が未完了です。"), ("Praise", "高い評価", "The work is outstanding.", "仕事は素晴らしいです。")),
        transfer_title="Updating a client on an event plan", transfer_ja="イベント計画の進捗を顧客に報告する", transfer_role="Client", transfer_turns=(("other", "Can you give me a quick update on the event plan?", "イベント計画の進捗を簡単に教えてもらえますか？"), ("target", 1, 2), ("other", "Good. What still needs attention?", "順調ですね。まだ何を確認する必要がありますか？"), ("target", 2, 1), ("other", "I'll confirm the owner today, and you can lock the deadline tomorrow.", "今日担当者を確認します。明日は締め切りを確定できます。"), ("me", "Perfect. I'll send the updated plan after that.", "ありがとうございます。そのあと更新版の計画を送ります。")),
        vocab=("on track|予定どおり; outstanding items|未完了項目; scope|範囲", "finished|終えた|CORE-32; need to|必要がある|CORE-40; budget|予算|CORE-53; timeline|予定表|CORE-107", "review|レビュー; report|レポート; date|日付; price|料金", "short version|短い要約; measurable|測定できる"),
    ),
    36: dict(
        slug="report-a-technical-blocker-usefully", title="Report a technical blocker usefully", ko="기술적 장애 요인을 유용하게 보고하기", ja="技術的なブロッカーを具体的に報告する", role="Demo Lead", scene="One hour before a client demo", scene_ja="顧客デモの1時間前", situation="共有環境にアクセスできないことと、今朝から変わったエラー内容を伝え、すぐに対応できる担当者につなぎます。", goal=("Report the blocker with enough evidence for the team to act immediately.", "チームがすぐ対応できるだけの情報を添えてブロッカーを報告しましょう。"), expressions=(("permission error", "権限エラー"), ("blocking the demo", "デモを妨げている")),
        p1=pattern(bridge="まず、できない操作と対象を短く伝えます。", meaning=("Use this to state the exact system or environment you cannot enter.", "アクセスできないシステムや環境を正確に示す表現です。"), rows_=rows(("I {t}can't access{/t} the demo environment.", "デモ環境に{t}アクセスできません{/t}。", "I can't access|the demo environment|right now."), ("I {t}can't access{/t} the shared folder.", "共有フォルダに{t}アクセスできません{/t}。", "I can't access|the shared folder|right now."), ("I {t}can't access{/t} the test account.", "テストアカウントに{t}アクセスできません{/t}。", "I can't access|the test account|right now."), ("I {t}can't access{/t} the client dashboard.", "顧客ダッシュボードに{t}アクセスできません{/t}。", "I can't access|the client dashboard|right now.")), rule=("Put the blocked resource after “access”", "利用できない対象は access のあと", "Name the exact resource instead of saying only that the system is broken.", "システムが壊れているとだけ言わず、対象を正確に示します。", "I can't access + resource", "Identify the blocker", "ブロッカーを特定", ("access · the demo environment", "access · the test account")), write=("Which exact resource is blocking your work?", "どの具体的な対象が作業を止めていますか？")),
        p2=pattern(bridge="次に、最後に動いた時点と今のエラーを対比します。", meaning=("Use this to show what changed between the last successful attempt and now.", "最後に成功した時点と現在の違いを示す表現です。"), rows_=rows(("It {t}worked this morning, but now I get{/t} a permission error.", "今朝は{t}動きましたが、今は{/t}権限エラーが出ます。", "It worked|this morning,|but now I get|a permission error."), ("It {t}worked yesterday, but now I get{/t} a login error.", "昨日は{t}動きましたが、今は{/t}ログインエラーが出ます。", "It worked|yesterday,|but now I get|a login error."), ("It {t}worked before lunch, but now I get{/t} a blank screen.", "昼食前は{t}動きましたが、今は{/t}空白画面が出ます。", "It worked|before lunch,|but now I get|a blank screen."), ("It {t}worked on my laptop, but now I get{/t} an access error.", "自分のPCでは{t}動きましたが、今は{/t}アクセスエラーが出ます。", "It worked|on my laptop,|but now I get|an access error.")), rule=("Contrast the last success with the current error", "最後の成功と現在のエラーを対比", "Give the team a time boundary and the exact symptom.", "チームが調査できるよう、時点と具体的な症状を伝えます。", "worked + last time, but now + current error", "Make the report actionable", "対応可能な報告にする", ("worked this morning · now permission error", "worked yesterday · now login error")), write=("When did it last work, and what happens now?", "最後に動いたのはいつで、今は何が起きますか？")),
        scene_turns=(("other", "Is the demo setup ready for the client call?", "顧客との通話に向けてデモの準備はできていますか？"), ("target", 1, 0), ("other", "What changed since the last successful login?", "最後にログインできたときから何が変わりましたか？"), ("target", 2, 0), ("other", "That gives me enough to act. I'll restore your demo access now.", "対応に必要な情報がそろいました。今すぐデモ環境へのアクセスを復旧します。"), ("me", "Thanks. I'll retest it before the client joins.", "ありがとうございます。顧客が参加する前に再テストします。")),
        receptive=(("Is the demo setup ready?", "The lead asks whether the client demo can proceed", "顧客デモを実施できるか尋ねている", "The lead asks who designed the product", "製品のデザイナーを尋ねている"), ("What changed since the last successful login?", "The lead wants evidence about when the failure began", "障害が始まった時点の手がかりを求めている", "The lead asks for a new password choice", "新しいパスワード案を求めている"), ("That gives me enough to act.", "The report contains actionable detail", "報告には対応できる具体性がある", "The report contains no useful information", "報告には役立つ情報がない"), ("I'll restore your demo access now.", "The lead will fix the permission immediately", "今すぐ権限を復旧する", "The demo is cancelled permanently", "デモを永久に中止する")),
        live=("Describe a real or imaginary technical blocker with a before-and-now contrast.", "実際または架空の技術的な問題を、以前と現在の対比で説明してください。", "I can't access ___. It worked ___, but now I get ___. / If nothing is blocked: Nothing is blocked right now, but a useful report would be ___.", "問題がなければ、今は何も止まっていないと伝えてから例を作ってください。", "What detail helps you diagnose a technical problem?", "先生は技術的な問題を調べるとき、どの情報が役立ちますか？"),
        tip=("Report the symptom, not a guessed cause", "推測した原因ではなく症状を報告", "“I get a permission error” is evidence; “the server is broken” may only be a guess.", "I get a permission error は観察した事実ですが、the server is broken は推測にすぎない場合があります。", ("Observed symptom", "確認した症状", "I get a permission error.", "権限エラーが出ます。"), ("Unverified cause", "未確認の原因", "The server must be broken.", "サーバーが壊れているはずです。")),
        transfer_title="Reporting a blocked training account", transfer_ja="研修用アカウントの障害を報告する", transfer_role="IT Support", transfer_turns=(("other", "Can you open the training materials for today's session?", "今日の研修資料を開けますか？"), ("target", 1, 2), ("other", "When did that account last work?", "そのアカウントが最後に動いたのはいつですか？"), ("target", 2, 1), ("other", "Thanks. I'll reset the login and send you a new link.", "ありがとうございます。ログインをリセットし、新しいリンクを送ります。"), ("me", "Great. I'll test the account before training starts.", "ありがとうございます。研修開始前にアカウントを確認します。")),
        vocab=("demo environment|デモ環境; permission error|権限エラー; blocker|作業を止める問題", "can't access|アクセスできない|CORE-18; worked|動いた|CORE-32; now|今|CORE-14", "folder|フォルダ; account|アカウント; morning|朝; laptop|ノートPC", "restore access|アクセスを復旧する; symptom|症状"),
    ),
}

# Re-mark fixed frame words so late completion leaves names, times, quantities,
# places, and other scene facts visibly printed. Japanese marks mirror the
# communicative operation even when Japanese word order makes the cue split.
def _mark_parts(text, parts):
    plain = core.strip_marks(text)
    for part in sorted(parts, key=len, reverse=True):
        if part not in plain:
            raise ValueError(f"cannot mark {part!r} inside {plain!r}")
        plain = plain.replace(part, f"{{t}}{part}{{/t}}", 1)
    return plain


def _remark(number, part, english_parts, japanese_parts):
    updated = []
    for index, (english, japanese, chunks) in enumerate(LESSONS[number][f"p{part}"]["rows"]):
        en_parts = english_parts(core.strip_marks(english), index)
        ja_parts = japanese_parts(core.strip_marks(japanese), index)
        updated.append((_mark_parts(english, en_parts), _mark_parts(japanese, ja_parts), chunks))
    LESSONS[number][f"p{part}"]["rows"] = tuple(updated)


_remark(25, 1, lambda _s, _i: ("What matters most is",), lambda _s, _i: ("最も重要なのは",))
_remark(26, 1, lambda _s, _i: ("definitely had",), lambda _s, _i: ("確実に持っていました",))
_remark(26, 2,
        lambda s, _i: (re.search(r"may have been \w+", s).group(0), "but I can't be certain"),
        lambda s, _i: (re.search(r"[^、]+可能性があります", s).group(0), "確かではありません"))
_remark(27, 1, lambda _s, _i: ("To be clear,", "is essential, not optional"),
        lambda _s, _i: ("はっきり申し上げると、", "必須で、任意ではありません"))
_remark(27, 2, lambda s, _i: (re.search(r"^What .+ can you offer us", s).group(0),),
        lambda s, _i: (re.sub(r"^(今夜、|今、)", "", s).rstrip("？"),))
_remark(28, 1, lambda s, _i: (re.search(r"^My \w+ says", s).group(0), "whereas your system says"),
        lambda s, _i: (re.search(r"^.+とありますが", s).group(0), re.search(r"そちらのシステムでは", s).group(0)))
_remark(29, 1, lambda _s, _i: ("The fact that", "doesn't necessarily mean"),
        lambda _s, _i: ("からといって、必ずしも", "とは限りません"))
_remark(29, 2, lambda _s, _i: ("Overall, I'd rather", "than take the risk"),
        lambda _s, _i: ("総合的に考えると、", "危険を冒すより"))
_remark(32, 1, lambda _s, _i: ("cut out after",),
        lambda s, _i: (s.rstrip("。").removeprefix("すみません、"),))
_remark(33, 1, lambda _s, _i: ("That would be", "for me"),
        lambda _s, _i: ("それだと私には", "になります"))
_remark(33, 2, lambda _s, _i: ("Could we move it to", "instead"),
        lambda _s, _i: ("代わりに", "へ変更できますか"))
_remark(35, 1, lambda _s, _i: ("finished", "of the"),
        lambda _s, _i: ("のうち", "終えました"))
_remark(36, 2, lambda _s, _i: ("worked", "but now I get"),
        lambda _s, _i: ("動きました", "が、今は", "が出ます"))


# These short intact chunks have only two honest meaning units. A three-chip
# reorder would require padding them with words that are not in the sentence.
for _number, _parts in {25: (2,), 27: (1, 2), 28: (1,), 29: (1, 2), 31: (1, 2), 32: (2,), 33: (1, 2), 34: (1,), 36: (1,)}.items():
    for _part in _parts:
        LESSONS[_number][f"p{_part}"]["omit_reorder"] = True

for _number, _parts in {25: (2,), 27: (1, 2), 28: (1,), 29: (1, 2), 31: (1,), 33: (1, 2)}.items():
    for _part in _parts:
        LESSONS[_number][f"p{_part}"]["omit_rule"] = True

CHUNK_OWNERS = {
    (25, 2): ("CORE-24",), (27, 1): (), (27, 2): (), (28, 1): (),
    (29, 1): (), (29, 2): ("CORE-117",), (31, 1): ("CORE-81",),
    (33, 1): (), (33, 2): ("CORE-60",),
}
VISIBLE_PRIOR_CTX_OWNERS = {"meet you there|そこで会う|CTX-21"}

# Vocabulary ownership follows each lesson's entry floor. Later Core owners are
# documented above for bounded treatment, not mislabeled as already learned.
LESSONS[29]["vocab"] = (
    "err on the side of caution|安全側に判断する; weather advisory|気象注意報; flash flooding|鉄砲水; necessarily|必ずしも; would rather|〜のほうがよい",
    "safe|安全な|CORE-65; cancel|中止する|CORE-36", LESSONS[29]["vocab"][2], LESSONS[29]["vocab"][3],
)
LESSONS[31]["vocab"] = (
    "project schedule|プロジェクト予定; kickoff|キックオフ; point of contact|窓口担当者; remit|担当範囲; responsible for|担当している; mainly|主に",
    "work with|一緒に働く|CORE-12", LESSONS[31]["vocab"][2], LESSONS[31]["vocab"][3],
)
LESSONS[32]["vocab"] = (
    "cut out|音声が途切れる; break up|音声が途切れ続ける; close of business|営業時間終了時; deadline|締め切り",
    "repeat|繰り返す|CORE-24; Friday|金曜日|CORE-9", LESSONS[32]["vocab"][2], LESSONS[32]["vocab"][3],
)
LESSONS[33]["vocab"] = (
    "time zone|タイムゾーン; midnight|深夜0時; calendar invite|カレンダー招待; UTC|協定世界時; move it to|変更する",
    "Friday|金曜日|CORE-9; morning|朝|CORE-3", LESSONS[33]["vocab"][2], LESSONS[33]["vocab"][3],
)


LESSONS[34]["vocab"] = (
    "latest version|最新版; version history|変更履歴; shared folder|共有フォルダ; final version|最終版",
    "could you send me|送っていただけますか|CORE-20; could you also|追加でしていただけますか|CORE-20",
    LESSONS[34]["vocab"][2], LESSONS[34]["vocab"][3],
)
LESSONS[35]["vocab"] = (
    "on track|予定どおり; outstanding items|未完了項目; scope|範囲; budget|予算; timeline|予定表; deadline|締め切り; owner|担当者",
    "finished|終えた|CORE-32; need to|必要がある|CORE-40", LESSONS[35]["vocab"][2], LESSONS[35]["vocab"][3],
)
LESSONS[31]["tip"] = (
    "Use “in charge of” for day-to-day control", "日々の管理には in charge of",
    "“Responsible for” names your duty; “in charge of” suggests you direct the work or people.",
    "responsible for は担当業務を示し、in charge of は仕事や人を取りまとめる立場を示します。",
    ("Your duty", "担当業務", "I'm responsible for the schedule.", "予定を担当しています。"),
    ("Directing the work", "仕事を取りまとめる", "I'm in charge of the launch.", "公開作業を取りまとめています。"),
)
LESSONS[31]["vocab"] = (
    LESSONS[31]["vocab"][0].replace("remit|担当範囲", "in charge of|取りまとめている"),
    LESSONS[31]["vocab"][1], LESSONS[31]["vocab"][2], LESSONS[31]["vocab"][3],
)
LESSONS[32]["vocab"] = (
    LESSONS[32]["vocab"][0], LESSONS[32]["vocab"][1], LESSONS[32]["vocab"][2],
    "choppy audio|途切れがちな音声",
)
LESSONS[32]["live"] = (
    LESSONS[32]["live"][0], LESSONS[32]["live"][1],
    "Sorry, you cut out after “___.” Could you repeat ___? / If your calls are usually clear: My calls are usually clear, but I'd say ___.",
    *LESSONS[32]["live"][3:],
)

# Independent-review repairs.  The live tasks below use one shared response
# path for both real and imaginary situations, so either truthful choice still
# retrieves both lesson frames instead of escaping into an unrelated sentence.
LIVE_FRAME_CONTRACTS = {
    25: ("What matters most is", "Could you check routes through"),
    26: ("I definitely had", "It may have", "but I can't be certain"),
    27: ("To be clear,", "is essential, not optional", "What alternative can you offer me"),
    28: ("My confirmation says", "whereas your system says", "Could you confirm in writing"),
    29: ("The fact that", "doesn't necessarily mean it's safe", "Overall, I'd rather", "than take the risk"),
    30: ("What I'd recommend is", "I'd only take that route if"),
    31: ("I'm responsible for", "I mainly work with"),
    33: ("That would be", "for me", "Could we move it to", "instead"),
    32: ("Sorry, you cut out after", "Could you repeat"),
    35: ("We finished", "of the", "Next, we need to confirm"),
    36: ("I can't access", "It worked", "but now I get"),
}

_live_repairs = {
    25: (
        "Use a real or imaginary cancelled trip. State the arrival condition and ask for another route.",
        "実際または架空の欠航を想定し、譲れない到着条件を伝えて別ルートを頼んでください。",
        "Real or imaginary: What matters most is ___. Could you check routes through ___?",
        "実際の予定でも架空の予定でも、二つの表現を使って答えましょう。",
        "When travel changes, what matters most to you?",
        "旅行が変更になったとき、先生は何を最優先しますか？",
    ),
    26: (
        "Use a real or imaginary lost item. Separate one confirmed fact from one possibility.",
        "実際または架空の紛失物について、確認できる事実と可能性を一つずつ分けてください。",
        "Real or imaginary: I definitely had ___ at ___. It may have ___, but I can't be certain.",
        "実際の経験でも架空の場面でも、二つの表現を使って答えましょう。",
        "Have you ever had to report a lost item? You can describe an imaginary case if not.",
        "先生は紛失物を届け出たことがありますか？ なければ架空の例で答えてください。",
    ),
    27: (
        "Use a real or imaginary access need. State the requirement and ask for a usable alternative.",
        "実際または架空のアクセス上の必要を想定し、必須条件を伝えて利用できる代案を求めてください。",
        "Real or imaginary: To be clear, ___ is essential, not optional. What alternative can you offer me ___?",
        "実際の必要でも架空の場面でも、二つの表現を使って答えましょう。",
        "What real or imaginary feature would make a hotel easy for you to use?",
        "実際または架空の条件として、どんな設備があればホテルを利用しやすいですか？",
    ),
    28: (
        "Use a real or imaginary reservation discrepancy. Compare the records and request written confirmation.",
        "実際または架空の予約情報の食い違いを想定し、記録を比較して書面での確認を求めてください。",
        "Real or imaginary: My confirmation says ___, whereas your system says ___. Could you confirm in writing ___?",
        "実際の予約でも架空の予約でも、二つの表現を使って答えましょう。",
        "For a real or imaginary booking, which detail would you want confirmed in writing?",
        "実際または架空の予約で、どの情報を書面で確認してもらいたいですか？",
    ),
    29: (
        "Use a real or imaginary weather risk. Challenge the weak assumption and choose the safer action.",
        "実際または架空の悪天候を想定し、根拠の弱い判断を問い直して安全側の行動を選んでください。",
        "Real or imaginary: The fact that ___ doesn't necessarily mean it's safe. Overall, I'd rather ___ than take the risk.",
        "実際の予定でも架空の予定でも、二つの表現を使って答えましょう。",
        "If weather made a plan unsafe, what would make you cancel or postpone it?",
        "天候で予定が危険になったら、どんな状況で中止または延期しますか？",
    ),
    30: (
        "Use a real or imaginary difficult route. Give one recommendation and the condition for taking it.",
        "実際または架空の難しいルートを想定し、一つの助言とそのルートを選ぶ条件を伝えてください。",
        "Real or imaginary: What I'd recommend is ___. I'd only take that route if ___.",
        "実際の経験でも架空の場面でも、二つの表現を使って答えましょう。",
        "What travel advice would you give me for a real or imaginary difficult route?",
        "実際または架空の難しいルートについて、先生ならどんな助言をしますか？",
    ),
    31: (
        "Use a real or imaginary project. Introduce your responsibility and main partner team.",
        "実際または架空のプロジェクトを想定し、担当業務と主な連携チームを紹介してください。",
        "Real or imaginary: I'm responsible for ___. I mainly work with ___.",
        "実際の役割でも架空の役割でも、二つの表現を使って答えましょう。",
        "For a real or imaginary project, what would you be responsible for, and which team would you work with?",
        "実際または架空のプロジェクトで、先生は何を担当し、どのチームと連携しますか？",
    ),
    33: (
        "Use a real or imaginary cross-time-zone meeting. State the local-time conflict and propose another slot.",
        "実際または架空の時差をまたぐ会議を想定し、現地時刻の問題と別の時間を伝えてください。",
        "Real or imaginary: That would be ___ for me. Could we move it to ___ instead?",
        "実際の会議でも架空の会議でも、二つの表現を使って答えましょう。",
        "Which real or imaginary meeting time would be easiest for you?",
        "実際または架空の会議なら、先生にとって何時が最も参加しやすいですか？",
    ),
    32: (
        "Use a real or imaginary bad connection. Identify the last clear words and recover the missed detail.",
        "実際または架空の接続不良を想定し、最後に聞こえた言葉を示して聞き逃した情報を確認してください。",
        "Real or imaginary: Sorry, you cut out after “___.” Could you repeat ___?",
        "実際の経験でも架空の場面でも、二つの表現を使って答えましょう。",
        "For a real or imaginary call, what would you say when the audio cuts out?",
        "実際または架空の通話で音声が途切れたら、先生は何と言いますか？",
    ),
    35: (
        "Use a real or imaginary project. Report measurable progress and the next item to confirm.",
        "実際または架空のプロジェクトを想定し、数で示せる進捗と次に確認する項目を報告してください。",
        "Real or imaginary: We finished ___ of the ___. Next, we need to confirm ___.",
        "実際のプロジェクトでも架空のプロジェクトでも、二つの表現を使って答えましょう。",
        "For a real or imaginary project, what progress and next step would you report?",
        "実際または架空のプロジェクトで、どんな進捗と次の行動を報告しますか？",
    ),
    36: (
        "Use a real or imaginary technical blocker. Name the resource and contrast the last success with the current error.",
        "実際または架空の技術的な問題を想定し、対象と最後に動いた時点、現在のエラーを伝えてください。",
        "Real or imaginary: I can't access ___. It worked ___, but now I get ___.",
        "実際の問題でも架空の問題でも、二つの表現を使って答えましょう。",
        "For a real or imaginary technical problem, which detail would help you diagnose it?",
        "実際または架空の技術的な問題で、どの情報が診断に役立ちますか？",
    ),
}
for _number, _live in _live_repairs.items():
    LESSONS[_number]["live"] = _live

# CTX34 needs the colleague's real answer between the two requests; the second
# request is only coherent after the colleague confirms the current file.
LESSONS[34]["live_sequence"] = dict(
    prompt=(
        "Name a real or imaginary current file that I can send you, and a shared copy that I can replace.",
        "私があなたに送れる実際または架空の最新版と、私が差し替えられる共有コピーを一つずつ挙げてください。",
    ),
    request1=("Could you send me ___?", "必要な最新版を具体的に頼みましょう。"),
    reply1=("Tutor's answer — confirm availability: Yes, I can send ___.", "送れることを先生が実際に確認：はい、___を送れます。"),
    request2=("Yes, so could you also replace ___?", "最初の返事を受け、古いコピーの差し替えも頼みましょう。"),
    reply2=("Tutor's answer", "差し替え依頼への先生の本当の答え"),
    ask=("If you shared work files, how would you keep them current?", "仕事のファイルを共有するとしたら、先生はどうやって最新版に保ちますか？"),
)

# Exact semantic and provenance corrections from the independent review.
LESSONS[30]["transfer_turns"] = (
    LESSONS[30]["transfer_turns"][0], LESSONS[30]["transfer_turns"][1],
    ("other", "Would you still take that ferry route in winter?", "それでも冬にそのフェリールートを利用しますか？"),
    LESSONS[30]["transfer_turns"][3], LESSONS[30]["transfer_turns"][4], LESSONS[30]["transfer_turns"][5],
)
LESSONS[26]["transfer_ja"] = "ホテル警備に紛失PCを届け出る"
LESSONS[30]["transfer_ja"] = "難しいフェリー経路を助言する"
LESSONS[32]["goal_title"] = "Repair a bad connection on a call"
LESSONS[32]["goal_breaks"] = {1: "すみません、"}

# CTX27 is one traveller speaking for themself.  Keep the request singular in
# every model, chunk, rule, replay, transfer, and live scaffold.
_p27_rows = []
for _english, _japanese, _chunks in LESSONS[27]["p2"]["rows"]:
    _p27_rows.append((_english.replace("offer us", "offer me"), _japanese, _chunks.replace("offer us", "offer me")))
LESSONS[27]["p2"]["rows"] = tuple(_p27_rows)
LESSONS[27]["p2"]["rule"] = tuple(
    value.replace("offer us", "offer me") if isinstance(value, str) else value
    for value in LESSONS[27]["p2"]["rule"]
)
LESSONS[25]["tip"] = (
    "Use “nonstop” for a flight with no stops", "途中で止まらない便には nonstop",
    "A direct flight can stop while keeping the same flight number; a nonstop flight does not stop en route.",
    "direct は同じ便名のまま途中で着陸することがありますが、nonstop は目的地まで途中で着陸しません。",
    ("No stop", "途中で着陸しない", "Is there a nonstop flight?", "途中で着陸しない便はありますか？"),
    ("Same flight number", "同じ便名", "Is there a direct flight?", "同じ便名で行ける便はありますか？"),
)
LESSONS[31]["goal"] = (
    "Introduce your responsibilities so the new team knows when to contact you.",
    "担当範囲を紹介し、どんなときに連絡すればよいかをチームに伝えましょう。",
)
_p31_rule = list(LESSONS[31]["p1"]["rule"])
_p31_rule[5] = "Define your responsibilities"
LESSONS[31]["p1"]["rule"] = tuple(_p31_rule)

LESSONS[27]["vocab"] = (
    LESSONS[27]["vocab"][0] + "; essential|必須の; optional|任意の; alternative|代案",
    LESSONS[27]["vocab"][1], LESSONS[27]["vocab"][2], LESSONS[27]["vocab"][3],
)
LESSONS[29]["vocab"] = (
    LESSONS[29]["vocab"][0] + "; postpone|延期する; turn back|引き返す; take the risk|危険を冒す",
    LESSONS[29]["vocab"][1], LESSONS[29]["vocab"][2], LESSONS[29]["vocab"][3],
)
LESSONS[34]["vocab"] = (
    LESSONS[34]["vocab"][0] + "; replace|差し替える",
    LESSONS[34]["vocab"][1].replace("; could you also|追加でしていただけますか|CORE-20", ""),
    LESSONS[34]["vocab"][2], LESSONS[34]["vocab"][3],
)
LESSONS[35]["vocab"] = (
    LESSONS[35]["vocab"][0].replace("; deadline|締め切り", ""),
    LESSONS[35]["vocab"][1] + "; confirm|確認する|CTX-3; deadline|締め切り|CTX-32",
    LESSONS[35]["vocab"][2], LESSONS[35]["vocab"][3],
)

# Entry-floor vocabulary corrections.  These items occur in learner-produced
# examples or native-tip practice, so they cannot remain implicit.
LESSONS[25]["vocab"] = (
    LESSONS[25]["vocab"][0] + "; direct|直行の",
    LESSONS[25]["vocab"][1], LESSONS[25]["vocab"][2], LESSONS[25]["vocab"][3],
)
LESSONS[26]["vocab"] = (
    LESSONS[26]["vocab"][0] + "; robbed|強盗に遭った",
    LESSONS[26]["vocab"][1] + "; stolen|盗まれた|CORE-65",
    LESSONS[26]["vocab"][2], LESSONS[26]["vocab"][3],
)
LESSONS[33]["vocab"] = (
    LESSONS[33]["vocab"][0].replace("midnight|深夜0時; ", ""),
    LESSONS[33]["vocab"][1] + "; midnight|深夜0時|CORE-10",
    LESSONS[33]["vocab"][2], LESSONS[33]["vocab"][3],
)


def _finalize_vocab(number, *, new=(), recycled=(), assumed=()):
    """Apply the actual-owner audit after all narrower vocabulary repairs."""
    lesson = LESSONS[number]
    new_items = [item for item in lesson["vocab"][0].split("; ") if item]
    assumed_items = [item for item in lesson["vocab"][2].split("; ") if item]
    for item in new:
        if item not in new_items:
            new_items.append(item)
    for item in assumed:
        if item not in assumed_items:
            assumed_items.append(item)
    lesson["vocab"] = (
        "; ".join(new_items),
        "; ".join(recycled),
        "; ".join(assumed_items),
        lesson["vocab"][3],
    )


# `recycled` is reserved for a term whose cited deck actually declares that
# exact term as new and is reachable from this lesson's brief entry floor.
# Familiar compositional language with no lexical metadata owner stays
# `assumed`; genuinely new productive language is owned here.
_finalize_vocab(25,
    new=("what matters most|最も重要なこと",),
    recycled=("route|ルート|CORE-59",),
    assumed=("could you check|確認していただけますか",))
_finalize_vocab(26,
    new=("definitely|確実に", "certain|確かな"),
    recycled=("proof of purchase|購入証明|CTX-11", "stolen|盗まれた|CORE-65"),
    assumed=("may have|した可能性がある",))
_finalize_vocab(27,
    new=("offer|提示する",),
    recycled=("meet you there|そこで会う|CTX-21",),
    assumed=("tonight|今夜",))
_finalize_vocab(28,
    new=("confirm in writing|書面で確認する",),
    recycled=("price|料金|CORE-19",),
    assumed=("breakfast|朝食",))
_finalize_vocab(29,
    recycled=("cancel|中止する|CORE-71",),
    assumed=("safe|安全な",))
_finalize_vocab(30,
    new=("what I'd recommend|私がおすすめすること",),
    recycled=("route|ルート|CORE-59",),
    assumed=("only if|場合にだけ",))
_finalize_vocab(31, recycled=(), assumed=("work with|一緒に働く",))
_finalize_vocab(32,
    recycled=("repeat|繰り返す|CORE-24", "Friday|金曜日|CORE-28"))
_finalize_vocab(33,
    recycled=("Friday|金曜日|CORE-28", "midnight|深夜0時|CORE-10"),
    assumed=("morning|朝",))
_finalize_vocab(34, recycled=(), assumed=("could you send me|送っていただけますか",))
_finalize_vocab(35,
    recycled=("confirm|確認する|CTX-3", "deadline|締め切り|CTX-32"),
    assumed=("finished|終えた", "need to|必要がある"))
_finalize_vocab(36,
    new=("can't access|アクセスできない",),
    recycled=("now|今|CORE-3",),
    assumed=("worked|動いた",))


def _replace_japanese_rows(number, part, japanese_rows):
    current = LESSONS[number][f"p{part}"]["rows"]
    if len(current) != len(japanese_rows):
        raise ValueError(f"CTX-{number} p{part}: Japanese repair row count drift")
    LESSONS[number][f"p{part}"]["rows"] = tuple(
        (english, japanese, chunks)
        for (english, _, chunks), japanese in zip(current, japanese_rows)
    )


# Exact one-to-one bilingual cues.  Variable facts remain outside the target
# span; each Japanese span expresses only its matching English blank.
_replace_japanese_rows(28, 1, (
    "{t}確認書の記載は{/t}「朝食込み」{t}ですが、そちらのシステムの記載は{/t}「朝食なし」です。",
    "{t}メールの記載は{/t}「駐車場込み」{t}ですが、そちらのシステムの記載は{/t}「駐車料金別」です。",
    "{t}バウチャーの記載は{/t}「2泊」{t}ですが、そちらのシステムの記載は{/t}「1泊」です。",
    "{t}確認書の記載は{/t}「ダブルルーム」{t}ですが、そちらのシステムの記載は{/t}「シングル」です。",
))
_remark(28, 1, lambda s, _i: (re.search(r"^My \w+ says", s).group(0), "whereas your system says"),
        lambda s, _i: (re.search(r"^[^「]+", s).group(0), "ですが、そちらのシステムの記載は"))

_replace_japanese_rows(29, 1, tuple(
    japanese for japanese in (
        "中止されていない{t}という事実だけでは{/t}、安全だということには{t}必ずしもなりません{/t}。",
        "道路が開いている{t}という事実だけでは{/t}、安全だということには{t}必ずしもなりません{/t}。",
        "ほかの人が行く{t}という事実だけでは{/t}、安全だということには{t}必ずしもなりません{/t}。",
        "警告が古い{t}という事実だけでは{/t}、安全だということには{t}必ずしもなりません{/t}。",
    )
))
_remark(29, 1, lambda _s, _i: ("The fact that", "doesn't necessarily mean"),
        lambda _s, _i: ("という事実だけでは", "必ずしもなりません"))

_replace_japanese_rows(29, 2, (
    "{t}総合的に考えると、私が望むのは{/t}延期であり、{t}危険を冒すことではありません{/t}。",
    "{t}総合的に考えると、私が望むのは{/t}引き返すことであり、{t}危険を冒すことではありません{/t}。",
    "{t}総合的に考えると、私が望むのは{/t}待つことであり、{t}危険を冒すことではありません{/t}。",
    "{t}総合的に考えると、私が望むのは{/t}中止であり、{t}危険を冒すことではありません{/t}。",
))
_remark(29, 2, lambda _s, _i: ("Overall, I'd rather", "than take the risk"),
        lambda _s, _i: ("総合的に考えると、私が望むのは", "危険を冒すことではありません"))

_replace_japanese_rows(32, 1, tuple(
    f"すみません、「{word}」{{t}}のあとで音声が途切れました{{/t}}。"
    for word in ("Friday", "budget", "send it", "the client")
))
_remark(32, 1, lambda _s, _i: ("cut out after",), lambda _s, _i: ("のあとで音声が途切れました",))

_replace_japanese_rows(33, 1, (
    "{t}それなら{/t}{t}私にとっては{/t}深夜0時になります。",
    "{t}それなら{/t}{t}私にとっては{/t}午前2時になります。",
    "{t}それなら{/t}{t}私にとっては{/t}午前6時になります。",
    "{t}それなら{/t}{t}私にとっては{/t}昼休み中になります。",
))
_remark(33, 1, lambda _s, _i: ("That would be", "for me"),
        lambda _s, _i: ("それなら", "私にとっては"))

_replace_japanese_rows(36, 2, (
    "今朝は{t}動きました{/t}{t}が、今表示されるのは{/t}権限エラーです。",
    "昨日は{t}動きました{/t}{t}が、今表示されるのは{/t}ログインエラーです。",
    "昼食前は{t}動きました{/t}{t}が、今表示されるのは{/t}空白画面です。",
    "自分のPCでは{t}動きました{/t}{t}が、今表示されるのは{/t}アクセスエラーです。",
))
_remark(36, 2, lambda _s, _i: ("worked", "but now I get"),
        lambda _s, _i: ("動きました", "が、今表示されるのは"))


# Human-reviewed operating copy and production support for the bounded
# CTX25-36 pass.  Keep this explicit so later regeneration cannot silently
# restore generic write prompts, scenario-production free talk, or unowned
# lexical hints.
REVIEWED_COPY_25_36 = {
    25: dict(
        role_ja="航空会社の係員", transfer_role_ja="鉄道会社の係員",
        live=("When a trip changes suddenly, what do you protect first: time, cost, or comfort?", "旅行が急に変更になったら、時間・費用・快適さのどれを最優先しますか？", "Your real priority and reason", "自分が本当に優先することと理由", "What about you—which one do you protect first?", "先生はどうですか？どれを最優先しますか？"),
        p1=dict(write_frame="What matters most is ___", write_script="Use “What matters most is ___” to state the arrival condition you cannot compromise on.", write_script_ja="「What matters most is ___」を使って、譲れない到着条件を伝えましょう。", translate_hints=(("明日の朝までに到着する", "arriving before tomorrow morning"), ("今夜東京に着く", "reaching Tokyo tonight"), ("朝の会議に間に合う", "making the morning meeting"), ("9時までに到着する", "getting there by nine"))),
        p2=dict(write_frame="Could you check routes through ___?", write_script="Use “Could you check routes through ___?” to ask the agent to check one connecting place.", write_script_ja="「Could you check routes through ___?」を使って、一つの経由地を通るルートを確認してもらいましょう。", translate_hints=(("別の都市", "another city"), ("ソウル", "Seoul"), ("大阪", "Osaka"), ("近くの空港", "a nearby airport"))),
    ),
    26: dict(
        role_ja="保険会社の担当者", transfer_role_ja="警備員",
        live=("Do you keep receipts for valuable travel items? Why or why not?", "旅行中の高価な物のレシートは保管しますか？なぜですか？", "Your real habit and reason", "自分の本当の習慣と理由", "What about you—do you keep them?", "先生はどうですか？保管しますか？"),
        p1=dict(write_frame="I definitely had ___ at ___", write_script="Use “I definitely had ___ at ___” to report the last fact you can confirm.", write_script_ja="「I definitely had ___ at ___」を使って、最後に確認できた事実を伝えましょう。", translate_hints=(("駅で", "at the station"), ("ホテルで", "at the hotel"), ("カフェでそのバッグ", "the bag at the café"), ("昼食前に財布", "my wallet before lunch"))),
        p2=dict(write_frame="It may have ___, but I can't be certain", write_script="Use “It may have ___, but I can't be certain” to report a possibility without presenting it as fact.", write_script_ja="「It may have ___, but I can't be certain」を使って、事実と断定せずに可能性を伝えましょう。", translate_hints=(("列車内で", "on the train"), ("タクシーに", "in the taxi"), ("カフェで", "at the café"), ("駅の近くで", "near the station"))),
    ),
    27: dict(
        role_ja="ホテルの責任者", transfer_role_ja="会場の担当者",
        live=("When choosing a hotel, which feature makes the biggest difference to your comfort?", "ホテルを選ぶとき、快適さに最も影響する設備は何ですか？", "One feature and why it matters to you", "一つの設備と、それが大切な理由", "What about you—which feature do you check first?", "先生はどうですか？最初にどの設備を確認しますか？"),
        p1=dict(write_frame="To be clear, ___ is essential, not optional", write_script="Use “To be clear, ___ is essential, not optional” to state one access requirement that must be met.", write_script_ja="「To be clear, ___ is essential, not optional」を使って、必ず満たす必要があるアクセス条件を一つ伝えましょう。", translate_hints=(("段差のないアクセス", "step-free access"), ("バリアフリーの浴室", "an accessible bathroom"), ("エレベーターの利用", "elevator access"), ("1階の部屋", "a ground-floor room"))),
        p2=dict(write_frame="What alternative can you offer me ___?", write_script="Use “What alternative can you offer me ___?” to ask for a usable alternative at the time you need it.", write_script_ja="「What alternative can you offer me ___?」を使って、必要な時間に利用できる代案を尋ねましょう。", translate_stage="checkpoint"),
    ),
    28: dict(
        role_ja="ホテルの受付係", transfer_role_ja="レンタカー係",
        live=("Which booking detail do you always double-check before a trip, and why?", "旅行前に必ず再確認する予約情報は何ですか？なぜですか？", "One booking detail and your reason", "一つの予約情報と理由", "What about you—which detail do you check first?", "先生はどうですか？最初に何を確認しますか？"),
        p1=dict(write_frame="My ___ says ___, whereas your system says ___", write_script="Use “My ___ says ___, whereas your system says ___” to compare the two conflicting records.", write_script_ja="「My ___ says ___, whereas your system says ___」を使って、食い違っている二つの記録を比べましょう。", translate_hints=((("朝食込み", "breakfast is included"), ("朝食なし", "it isn't")), (("駐車場込み", "parking is included"), ("駐車料金別", "it isn't")), (("2泊", "two nights"), ("1泊", "one")), (("ダブルルーム", "a double room"), ("シングル", "a single")))),
        p2=dict(write_frame="Could you confirm in writing ___?", write_script="Use “Could you confirm in writing ___?” to ask for written confirmation of the solution.", write_script_ja="「Could you confirm in writing ___?」を使って、解決内容を書面で確認してもらいましょう。", translate_hints=(("どう解決するか", "how this will be resolved"), ("朝食が含まれること", "that breakfast is included"), ("修正後の料金", "the revised price"), ("部屋タイプ", "the room type"))),
    ),
    29: dict(
        role_ja="ツアー会社の担当者", transfer_role_ja="レンタカー係",
        live=("When weather changes a trip, are you more likely to postpone it or change the plan?", "天候で旅行に影響が出たら、延期しますか、それとも予定を変えますか？", "Your safer choice and reason", "自分が選ぶ安全側の行動と理由", "What about you—what would you usually do?", "先生はどうですか？普段ならどうしますか？"),
        p1=dict(write_frame="The fact that ___ doesn't necessarily mean ___", write_script="Use “The fact that ___ doesn't necessarily mean ___” to challenge one weak safety assumption.", write_script_ja="「The fact that ___ doesn't necessarily mean ___」を使って、安全についての根拠が弱い判断を一つ問い直しましょう。", translate_hints=(("中止されていない", "it hasn't been cancelled"), ("道路が開いている", "the road is open"), ("ほかの人が行く", "others are going"), ("警告が古い", "the warning is old"))),
        p2=dict(write_frame="Overall, I'd rather ___ than take the risk", write_script="Use “Overall, I'd rather ___ than take the risk” to state the safer action you choose.", write_script_ja="「Overall, I'd rather ___ than take the risk」を使って、安全側で選ぶ行動を伝えましょう。", translate_hints=(("延期する", "postpone"), ("引き返す", "turn back"), ("待つ", "wait"), ("中止する", "cancel"))),
    ),
    30: dict(
        role_ja="同僚", transfer_role_ja="友人",
        live=("What piece of travel advice has actually helped you?", "実際に役立った旅行のアドバイスは何ですか？", "One useful piece of advice and why it helped", "役立ったアドバイスを一つと、その理由", "What about you—which advice has helped you most?", "先生はどうですか？どんなアドバイスが最も役立ちましたか？"),
        p1=dict(write_frame="What I'd recommend is ___", write_script="Use “What I'd recommend is ___” to give one practical recommendation from experience.", write_script_ja="「What I'd recommend is ___」を使って、経験から得た実用的な助言を一つ伝えましょう。", translate_hints=(("乗り継ぎに1日余分に取る", "allowing an extra day for the connection"), ("朝の列車を事前に予約する", "booking the morning train in advance"), ("できれば朝のフェリーを利用する", "taking the morning ferry if possible"), ("ビザの規則を早めに確認する", "checking the visa rules early"))),
        p2=dict(write_frame="I'd only ___ if ___", write_script="Use “I'd only ___ if ___” to state the condition that would make the route acceptable.", write_script_ja="「I'd only ___ if ___」を使って、そのルートを選べる条件を伝えましょう。", translate_hints=(("予定を調整できる", "have some flexibility"), ("もう1泊できる", "can stay an extra night"), ("乗り継ぎ時間が長い", "have a long connection"), ("日程を変更できる", "can change your dates"))),
    ),
    31: dict(
        role_ja="プロジェクト責任者", transfer_role_ja="顧客側の責任者",
        live=("On a new project, which responsibility would you most enjoy taking on?", "新しいプロジェクトなら、どの担当業務を最もやってみたいですか？", "One responsibility and why it appeals to you", "一つの担当業務と、興味を持つ理由", "What about you—which responsibility do you enjoy?", "先生はどうですか？どの担当業務が好きですか？"),
        p1=dict(write_frame="I'm responsible for ___", write_script="Use “I'm responsible for ___” to tell the team what they should contact you about.", write_script_ja="「I'm responsible for ___」を使って、どの業務について自分に連絡すればよいか伝えましょう。", translate_hints=(("プロジェクトの予定", "the project schedule"), ("週次報告", "the weekly report"), ("顧客への進捗共有", "client updates"), ("最終確認", "the final review"))),
        p2=dict(write_frame="I mainly work with ___", write_script="Use “I mainly work with ___” to name your main partner team.", write_script_ja="「I mainly work with ___」を使って、主に連携するチームを伝えましょう。", translate_hints=(("デザインチーム", "the design team"), ("営業チーム", "the sales team"), ("財務チーム", "the finance team"), ("エンジニアリングチーム", "the engineering team"))),
    ),
    32: dict(
        role_ja="会議の進行役", transfer_role_ja="取引先",
        live=("Which is more frustrating on a call: bad audio or a frozen screen, and why?", "通話では、音声不良と画面停止のどちらがより困りますか？なぜですか？", "Your choice and a brief reason", "自分の選択と短い理由", "What about you—which one bothers you more?", "先生はどうですか？どちらのほうが困りますか？"),
        p1=dict(write_frame="Sorry, you cut out after ___", write_script="Use “Sorry, you cut out after ___” to identify the last words you heard clearly.", write_script_ja="「Sorry, you cut out after ___」を使って、最後にはっきり聞こえた言葉を伝えましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="Could you repeat ___?", write_script="Use “Could you repeat ___?” to ask for the exact detail you missed.", write_script_ja="「Could you repeat ___?」を使って、聞き逃した情報を具体的にもう一度尋ねましょう。", translate_hints=(("締め切り", "the deadline"), ("日付", "the date"), ("最後の点", "the last point"), ("顧客名", "the client name"))),
    ),
    33: dict(
        role_ja="プロジェクトの相手", transfer_role_ja="研修担当者",
        live=("Do you prefer early or late meetings when working across time zones, and why?", "時差のある相手との会議は、早い時間と遅い時間のどちらがよいですか？なぜですか？", "Your preferred time and reason", "希望する時間と理由", "What about you—which time do you prefer?", "先生はどうですか？どの時間がよいですか？"),
        p1=dict(write_frame="That would be ___ for me", write_script="Use “That would be ___ for me” to explain the proposed time in your local time.", write_script_ja="「That would be ___ for me」を使って、提案された時間が自分の現地時刻で何時か伝えましょう。", translate_hints=(("深夜0時", "midnight"), ("午前2時", "2 a.m."), ("午前6時", "6 a.m."), ("昼休み中", "during lunch"))),
        p2=dict(write_frame="Could we move it to ___ instead?", write_script="Use “Could we move it to ___ instead?” to propose one workable alternative time.", write_script_ja="「Could we move it to ___ instead?」を使って、参加できる別の時間を一つ提案しましょう。", translate_hints=(("金曜日の朝", "Friday morning"), ("木曜日の午後", "Thursday afternoon"), ("そちらの時間の9時", "nine your time"), ("来週月曜日", "next Monday"))),
    ),
    34: dict(
        role_ja="デザイナー", transfer_role_ja="運用担当者",
        live=("How do you tell which shared file is the latest version?", "共有ファイルのどれが最新版か、どう見分けますか？", "Your real method and one useful detail", "自分の実際の方法と役立つ情報を一つ", "What about you—how do you keep files current?", "先生はどうですか？どうやって最新版に保ちますか？"),
        p1=dict(write_frame="Could you send me ___?", write_script="Use “Could you send me ___?” to request the exact current file you need.", write_script_ja="「Could you send me ___?」を使って、必要な最新版のファイルを具体的に頼みましょう。", translate_hints=(("最新版", "the latest version"), ("最終版のスライド", "the final slides"), ("更新済みの予算", "the updated budget"), ("承認済みのファイル", "the approved file"))),
        p2=dict(write_frame="Yes, so could you also replace ___?", write_script="Use “Yes, so could you also replace ___?” to ask for the outdated shared copy to be replaced too.", write_script_ja="「Yes, so could you also replace ___?」を使って、古い共有コピーも差し替えてもらいましょう。", translate_hints=(("共有フォルダのもの", "the one in the shared folder"), ("古い添付ファイル", "the old attachment"), ("オンラインの下書き", "the draft online"), ("プロジェクトフォルダのコピー", "the copy in the project folder"))),
    ),
    35: dict(
        role_ja="チームリーダー", transfer_role_ja="顧客",
        live=("When you hear a progress update, which detail matters most to you?", "進捗報告を聞くとき、どの情報が最も重要ですか？", "One useful detail and why it matters", "役立つ情報を一つと、それが重要な理由", "What about you—which detail do you listen for?", "先生はどうですか？どの情報に注目しますか？"),
        p1=dict(write_frame="We finished ___ of the ___", write_script="Use “We finished ___ of the ___” to report measurable completed progress.", write_script_ja="「We finished ___ of the ___」を使って、完了した進捗を数で報告しましょう。", translate_hints=((("3件", "three"), ("5件", "five"), ("レビュー", "reviews")), (("4件", "four"), ("6件", "six"), ("面談", "interviews")), (("2本", "two"), ("3本", "three"), ("レポート", "reports")), (("7項目", "seven"), ("8項目", "eight"), ("確認", "checks")))),
        p2=dict(write_frame="Next, we need to confirm ___", write_script="Use “Next, we need to confirm ___” to name the items that must be checked next.", write_script_ja="「Next, we need to confirm ___」を使って、次に確認する項目を伝えましょう。", translate_hints=((("予算", "the budget"), ("スケジュール", "timeline")), (("担当者", "the owner"), ("締め切り", "deadline")), (("日付", "the date"), ("場所", "location")), (("料金", "the price"), ("範囲", "scope")))),
    ),
    36: dict(
        role_ja="デモ担当者", transfer_role_ja="ITサポート担当者",
        live=("What information helps you solve a technical problem fastest?", "技術的な問題を最も早く解決するのに役立つ情報は何ですか？", "One diagnostic detail and why it helps", "診断に役立つ情報を一つと、その理由", "What about you—which detail do you ask for first?", "先生はどうですか？最初にどの情報を尋ねますか？"),
        p1=dict(write_frame="I can't access ___", write_script="Use “I can't access ___” to name the exact resource blocking your work.", write_script_ja="「I can't access ___」を使って、作業を止めている対象を具体的に伝えましょう。", translate_hints=(("デモ環境", "the demo environment"), ("共有フォルダ", "the shared folder"), ("テストアカウント", "the test account"), ("顧客ダッシュボード", "the client dashboard"))),
        p2=dict(write_frame="It worked ___, but now I get ___", write_script="Use “It worked ___, but now I get ___” to contrast the last success with the current error.", write_script_ja="「It worked ___, but now I get ___」を使って、最後に動いた時点と現在のエラーを対比しましょう。", translate_hints=((("今朝", "this morning"), ("権限エラー", "a permission error")), (("昨日", "yesterday"), ("ログインエラー", "a login error")), (("昼食前", "before lunch"), ("空白画面", "a blank screen")), (("自分のPC", "on my laptop"), ("アクセスエラー", "an access error")))),
    ),
}


for _number, _copy in REVIEWED_COPY_25_36.items():
    _lesson = LESSONS[_number]
    _lesson["role_ja"] = _copy["role_ja"]
    _lesson["transfer_role_ja"] = _copy["transfer_role_ja"]
    _lesson["live"] = _copy["live"]
    _lesson.pop("live_sequence", None)
    for _part in (1, 2):
        _lesson[f"p{_part}"].update(_copy[f"p{_part}"])

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

# Keep every receptive check owned by the tutor's role. The former final item
# was the learner's generic "Got it," which tested neither listening nor a
# useful workplace consequence.
LESSONS[32]["receptive"] = LESSONS[32]["receptive"][:3] + ((
    "I'll resend the deadline in the chat.",
    "The speaker will provide the deadline in writing",
    "話し手は締め切りをチャットで送り直す",
    "The speaker refuses to repeat the deadline",
    "話し手は締め切りの言い直しを断る",
),)

AUTHORITATIVE = {
    25: ("Escalate a cancellation with clear priorities", "What matters most is arriving before tomorrow morning.", "Could you check routes through another city?"),
    26: ("Document an incident for insurance", "I definitely had it at the station.", "It may have been taken on the train, but I can't be certain."),
    27: ("Advocate for an accessibility requirement", "To be clear, step-free access is essential, not optional.", "What alternative can you offer me tonight?"),
    28: ("Resolve conflicting booking information", "My confirmation says breakfast is included, whereas your system says it isn't.", "Could you confirm in writing how this will be resolved?"),
    29: ("Make a safety decision with incomplete information", "The fact that it hasn't been cancelled doesn't necessarily mean it's safe.", "Overall, I'd rather postpone than take the risk."),
    30: ("Give useful advice after a complicated trip", "What I'd recommend is allowing an extra day for the connection.", "I'd only take that route if you have some flexibility."),
    31: ("Introduce your role on a new project", "I'm responsible for the project schedule.", "I mainly work with the design team."),
    32: ("Repair a bad connection during a call", "Sorry, you cut out after 'Friday'.", "Could you repeat the deadline?"),
    33: ("Schedule across time zones", "That would be midnight for me.", "Could we move it to Friday morning instead?"),
    34: ("Request the correct file and explain why", "Could you send me the latest version?", "Yes, so could you also replace the one in the shared folder?"),
    35: ("Give a concise progress update", "We finished three of the five reviews.", "Next, we need to confirm the budget and timeline."),
    36: ("Report a technical blocker usefully", "I can't access the demo environment.", "It worked this morning, but now I get a permission error."),
}


def esc(value):
    return html.escape(str(value), quote=True)


def course_for(number):
    for numbers, config in COURSES.items():
        if number in numbers:
            return config
    raise ValueError(f"CTX-{number}: no course mapping")


def normalize_words(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def validate_lesson(number, lesson):
    title, first, second = AUTHORITATIVE[number]
    actual = (lesson["title"],) + tuple(core.strip_marks(lesson[f"p{part}"]["rows"][0][0]) for part in (1, 2))
    if actual != (title, first, second):
        raise ValueError(f"CTX-{number}: authoritative title/models drifted: {actual}")
    if len(lesson["scene_turns"]) != 6 or len(lesson["transfer_turns"]) != 6:
        raise ValueError(f"CTX-{number}: scene and transfer must each be exactly six purposeful turns")
    for label, turns in (("scene", lesson["scene_turns"]), ("transfer", lesson["transfer_turns"])):
        targets = [turn for turn in turns if turn[0] == "target"]
        if len(targets) != 2 or {turn[1] for turn in targets} != {1, 2}:
            raise ValueError(f"CTX-{number}: {label} must retrieve both patterns exactly once")
        if turns[-1][0] == "other" and turns[-1][1].rstrip().endswith("?"):
            raise ValueError(f"CTX-{number}: {label} ends on an unresolved question")
    if len(lesson["expressions"]) != 2 or len(lesson["receptive"]) != 4:
        raise ValueError(f"CTX-{number}: needs two expressions and four receptive checks")
    for part in (1, 2):
        p = lesson[f"p{part}"]
        if len(p["rows"]) != 4:
            raise ValueError(f"CTX-{number} p{part}: needs four rows")
        if not p.get("omit_reorder"):
            core.validate_reorder_pattern(p["rows"])
            for english, _, chunk_source in p["rows"]:
                if normalize_words(core.strip_marks(english)) != normalize_words(" ".join(chunk_source.split("|"))):
                    raise ValueError(f"CTX-{number} p{part}: reorder chips do not rebuild {core.strip_marks(english)!r}")
    new_items = [item for item in lesson["vocab"][0].split("; ") if item]
    if len(new_items) > 8:
        raise ValueError(f"CTX-{number}: {len(new_items)} new vocabulary items exceeds cap")
    prior_ctx_items = {
        item for field in lesson["vocab"] for item in field.split("; ")
        if re.search(r"\|CTX-(?:1[3-9]|2[0-4])$", item)
    }
    if not prior_ctx_items.issubset(VISIBLE_PRIOR_CTX_OWNERS):
        raise ValueError(f"CTX-{number}: cites unverified CTX13-24 provenance: {prior_ctx_items}")
    base.validate_reviewed_copy(number, lesson)
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
    if number == 35 and "confirm|確認する|CTX-3" not in lesson["vocab"][1]:
        raise ValueError("CTX-35: productive confirm must recycle its actual CTX-3 owner")
    if number == 35 and "deadline|締め切り|CTX-32" not in lesson["vocab"][1]:
        raise ValueError("CTX-35: deadline must recycle the earlier reachable CTX-32 owner")
    if number == 31 and "remit" in " ".join((lesson["goal"][0], lesson["p1"]["rule"][5], lesson["tip"][2])):
        raise ValueError("CTX-31: learner-facing unowned remit remains")


def wrapping_fill(part, pattern):
    """Use the shared target-only fill component; target markers are the contract."""
    return core.fill(f"p{part}-fill", pattern["rows"])


def wrapping_translate(part, pattern):
    return core.translate(
        f"p{part}-translate",
        pattern["rows"],
        hints=pattern.get("translate_hints"),
        support_stage=pattern.get(
            "translate_stage",
            "supported" if pattern.get("translate_hints") else None,
        ),
    )


def freetalk_page(lesson):
    return base.freetalk_page(lesson)


def goal_page(number, lesson):
    return core.goal_page(
        title=lesson["title"], title_ja=lesson["ja"],
        can_do=lesson["goal"][0], can_do_ja=lesson["goal"][1],
        data_act="Travel task" if number <= 30 else "Business task",
    )
def pages(number, lesson):
    learner_role = course_for(number)[3]
    learner_role_ja = course_for(number)[4]
    role_ja = lesson["role_ja"]
    transfer_role_ja = lesson["transfer_role_ja"]
    opening = base.render_roleplay(lesson, lesson["scene_turns"], prefix=f"ctx-{number}-scene")
    model = base.render_roleplay(lesson, lesson["scene_turns"], highlight=True, prefix=f"ctx-{number}-model")
    complete = base.render_roleplay(lesson, lesson["scene_turns"], complete=True, prefix=f"ctx-{number}-complete")
    transfer = base.render_roleplay(lesson, lesson["transfer_turns"], complete=True, prefix=f"ctx-{number}-transfer", role=lesson["transfer_role"])
    result = [
        goal_page(number, lesson),
        core.section("scene", lesson["scene"], lesson["scene_ja"],
            f'<p class="section-subtitle"><span class="ko">Let\'s role-play. You\'re the {esc(learner_role.lower())}, and I\'ll be the {esc(lesson["role"].lower())}.</span>'
            f'<span class="ja">ロールプレイをしましょう。あなたは{esc(learner_role_ja)}、私は{esc(role_ja)}です。</span></p>'
            f'<div class="tutor-note">Start with the first {esc(lesson["role"])} line.</div>'
            f'<div class="dialogue">{opening}</div>'),
        base.understand_page(number, lesson), base.expressions_page(lesson),
    ]
    for part in (1, 2):
        p = lesson[f"p{part}"]
        result.extend([
            base.transition(part, p), base.teach_page(part, p), core.read(f"p{part}-read", p["rows"]),
            "" if p.get("omit_rule") else base.rule_page(part, p),
            base.reorder_page(part, p), wrapping_fill(part, p), wrapping_translate(part, p), base.write_page(part, p),
        ])
    result.extend([
        '    <div class="transition-page" data-page-id="part3-intro" data-act="Complete the task">'
        '<span class="transition-kicker">PUT IT TOGETHER</span><h2 class="transition-title">'
        'Complete the practical job <span class="title-ja">(用事を完了しよう)</span></h2>'
        '<p class="section-subtitle"><span class="ko">Now, let\'s return to the scene and complete the practical job.</span>'
        '<span class="ja">最初の場面に戻り、二つの表現で用事を最後まで完了しましょう。</span></p>'
        '<div class="tutor-note">Introduce the roleplay, then move on.</div></div>\n',
        core.section("p3-model", "Replay the full scene", "場面をもう一度",
            f'<p class="section-subtitle"><span class="ko">I\'ll be the {esc(lesson["role"].lower())}. Please read your lines aloud.</span>'
            f'<span class="ja">私は{esc(role_ja)}です。自分のセリフを声に出して読んでください。</span></p>'
            f'<div class="dialogue">{model}</div>'),
        core.section("p3-complete", "Complete the full scene", "場面を完成しよう",
            f'<p class="section-subtitle"><span class="ko">I’ll be the {esc(lesson["role"].lower())}. Say each complete line, including the missing words.</span>'
            f'<span class="ja">私は{esc(role_ja)}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。</span></p>'
            '<div class="tutor-note">Type only the missing words exactly as the learner says them.</div>'
            f'<div class="dialogue">{complete}</div>'),
        freetalk_page(lesson), base.native_tip_page(lesson),
        core.section("transfer-scene", lesson["transfer_title"], lesson["transfer_ja"],
            f'<p class="section-subtitle"><span class="ko">Let\'s role-play a new situation using the same two lines. I\'ll be the {esc(lesson["transfer_role"].lower())}.</span>'
            f'<span class="ja">同じ二つの表現を使って、別の場面でロールプレイをしましょう。私は{esc(transfer_role_ja)}です。</span></p>'
            f'<div class="dialogue">{transfer}</div>'),
    ])
    return [page for page in result if page]


def build(number, lesson):
    validate_lesson(number, lesson)
    course, level, _, _, _ = course_for(number)
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{lesson["slug"]}'
    head = new_lesson.retarget(head, review_id=f"CTX-{number}", lesson_id=slug, level=level,
        title=lesson["title"], title_ko=lesson["ko"], title_ja=lesson["ja"], version="2026-08-20")
    head = head.replace('content="todo"', 'content="reviewed"')
    head = base.set_vocab(head, lesson["vocab"])
    head = core.set_proofread_status(head, "complete")
    output = TRACK / "courses" / course / "lessons" / slug / "lesson.html"
    return output, new_lesson.redepth(head + "\n".join(pages(number, lesson)) + foot, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, choices=LESSONS)
    args = parser.parse_args()
    selected = LESSONS.items() if args.lesson is None else ((args.lesson, LESSONS[args.lesson]),)
    for number, lesson in selected:
        output, source = build(number, lesson)
        if output.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(source, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    print(f"{len(LESSONS) if args.lesson is None else 1} Contextual decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
