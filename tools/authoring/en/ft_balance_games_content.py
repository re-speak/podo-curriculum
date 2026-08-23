"""Human-authored semantic content for FT107-121.

Article tails replace generic comparison advice with useful topic knowledge.
Question pools use concrete angles adapted from the approved Korean Balance
Games sequence, with independent English wording and aligned Japanese support.
"""


def q(job, title, title_ja, accessible, full, japanese, followups):
    return {
        "job": job, "title": title, "title_ja": title_ja,
        "accessible": accessible, "full": full,
        "accessible_ja": japanese, "full_ja": japanese,
        "accessible_followups": tuple(followups), "full_followups": (),
        "safety": f"topic-{job}",
    }


# Each row is Accessible English, Full English, and a Japanese rendering of the
# shared claim. The two English versions are independently phrased.
ARTICLE_HEADS = {
    107: (
        ("Money is most useful when it solves a cost that cannot wait.", "The marginal value of money rises sharply when an essential expense is urgent.", "お金は、待てない支出を解決するときに最も役立ちます。"),
        ("Free time matters most when sleep, health, or relationships are being squeezed.", "Time scarcity becomes serious when it erodes recovery, care, or sustained attention.", "自由な時間は、睡眠、健康、人間関係が圧迫されるときに特に重要です。"),
        ("A time-poor person may need free hours more than extra income.", "Being time-poor can make an additional free hour more valuable than a modest increase in income.", "時間に余裕がない人には、収入より自由な時間が必要な場合があります。"),
        ("Predictable hours can be more valuable than a larger number of uncertain free hours.", "Control and predictability determine whether nominal free time can actually be used.", "自由な時間は、量だけでなく、予測して使えるかどうかも大切です。"),
    ),
    108: (
        ("A broad social circle brings different information, ideas, and introductions.", "Weak ties often widen access to information and communities beyond a close circle.", "広い人間関係からは、さまざまな情報、考え、紹介を得られます。"),
        ("Close friends can notice a problem before someone asks for help.", "Intimacy makes subtle changes visible and can support care before an explicit request.", "親しい友人は、助けを求める前に問題に気づくことがあります。"),
        ("An inner circle is small enough for trust to grow through repeated contact.", "A reliable inner circle depends less on size than on repeated, mutual attention.", "親しい仲間の輪は小さいからこそ、繰り返す関わりの中で信頼が育ちます。"),
        ("Every friendship needs some attention, so a larger network changes how time is divided.", "Network size creates a maintenance cost because reciprocity and attention are limited resources.", "どの友情にも気づかいが必要なので、人間関係が広いほど時間の使い方も変わります。"),
    ),
    109: (
        ("Humidity can make moderate heat feel harder than a higher dry temperature.", "Thermal comfort depends on humidity, wind, shade, and night-time cooling as well as temperature.", "湿度が高いと、それほど高くない気温でも厳しく感じることがあります。"),
        ("Cold becomes more dangerous when wind, ice, or poor housing limits movement.", "Winter risk is shaped by wind chill, road conditions, housing quality, and access to heat.", "寒さは、風、氷、住まいの状態で移動が難しくなると、より危険になります。"),
        ("Seasonal extremes can make either option difficult rather than pleasant.", "Seasonal extremes expose the limits of both options once comfort becomes a question of health and infrastructure.", "季節の極端さによって、どちらも快適ではなく大変になることがあります。"),
        ("One permanent season would also change food, water, plants, and local work.", "A year without seasonal change would affect agriculture, water systems, ecosystems, and seasonal employment.", "一つの季節が続けば、食べ物、水、植物、地域の仕事も変わります。"),
    ),
    110: (
        ("Morning light helps set the body clock for the day.", "Light exposure is one of the strongest signals that shifts circadian timing.", "朝の光は、その日の体内時計を整える助けになります。"),
        ("Late-night focus can be real even when the next morning still starts early.", "Evening alertness does not remove the sleep debt created by fixed early obligations.", "夜に集中できても、翌朝早く始まれば睡眠不足になることがあります。"),
        ("A body clock can differ from the schedule a person has to follow.", "A person's body clock may conflict with institutional schedules without reflecting laziness or discipline.", "体内時計は、従わなければならない予定と合わないことがあります。"),
        ("Weekend sleep shifts can make Monday feel like travel across time zones.", "Large differences between workday and free-day sleep create a form of social jet lag.", "週末に睡眠時間が大きくずれると、月曜日に時差のような負担を感じます。"),
    ),
    111: (
        ("Flights and popular rooms become harder or more expensive to book near the date.", "Scarcity and dynamic pricing make some transport and accommodation costly to leave open.", "航空券や人気の部屋は、日程が近づくほど取りにくく、高くなることがあります。"),
        ("A flexible day can follow weather, energy, and local advice.", "Open time allows an itinerary to respond to weather, fatigue, closures, and information found locally.", "自由な一日は、天気、体力、現地の情報に合わせて変えられます。"),
        ("A last-minute plan works best when the important risks are already covered.", "A last-minute plan is easier to defend when safety, access, and the cost of failure have already been managed.", "直前の計画は、大切な危険への備えができているときにうまくいきます。"),
        ("Cancellation rules decide whether an early plan protects freedom or removes it.", "Refundability can turn advance booking from a commitment into a flexible option.", "キャンセルの条件によって、早い計画が自由を守るか、失わせるかが変わります。"),
    ),
    112: (
        ("Solo travellers make every decision, including the difficult ones.", "Independent travel offers autonomy while concentrating navigation, safety, and problem-solving in one person.", "一人旅では、難しい判断も含めて、すべて自分で決めます。"),
        ("A companion can share costs, attention, and responsibility.", "Travel partners can distribute financial, practical, and emotional load.", "同行者がいれば、費用、気づかい、責任を分けられます。"),
        ("A shared itinerary works only when both people can influence it.", "A genuinely shared itinerary requires negotiation rather than one person quietly following the other.", "共有する旅程は、両方の人が意見を出せるときにうまくいきます。"),
        ("Even people travelling together can plan a few hours apart.", "Intentional time apart can preserve autonomy without giving up companionship.", "誰かと旅行していても、数時間は別々に過ごせます。"),
    ),
    113: (
        ("A short distance can matter more than a large home when essential places are used every day.", "Daily access to work, care, education, and transport can outweigh additional private space.", "毎日使う場所が近いなら、広い家より短い移動のほうが大切な場合があります。"),
        ("Quiet surroundings do not guarantee access to health care, shops, or community.", "Low density can provide calm while increasing distance from essential services and social contact.", "静かな環境でも、医療、店、地域の人々に近いとは限りません。"),
        ("City access means reaching many needs without planning a long trip.", "City access can reduce the coordination cost of ordinary work, care, and social life.", "都会の利用しやすさとは、長い移動を計画せずに多くの用事を済ませられることです。"),
        ("A car can expand rural access while adding cost and dependence.", "Private transport can offset distance but creates financial, environmental, and mobility dependence.", "車があれば田舎で行ける場所は増えますが、費用と依存も増えます。"),
    ),
    114: (
        ("Indoor heat can become unsafe before it feels unbearable.", "Heat illness risk can rise indoors before discomfort alone signals the danger.", "室内の暑さは、耐えられないと感じる前に危険になることがあります。"),
        ("Internet access carries work, school, banking, messages, and emergency information.", "Connectivity now supports essential systems as well as entertainment and convenience.", "インターネットは、仕事、学校、銀行、連絡、緊急情報にも使われます。"),
        ("Cooling needs change with shade, insulation, airflow, and humidity.", "Building design and local climate determine how much mechanical cooling is necessary.", "冷房の必要性は、日陰、断熱、風通し、湿度で変わります。"),
        ("A power cut can remove internet and air conditioning at the same time.", "Grid failure exposes the dependence of both cooling and connectivity on resilient infrastructure.", "停電すると、インターネットとエアコンの両方が使えなくなることがあります。"),
    ),
    115: (
        ("Higher pay can create security without making an exhausting schedule sustainable.", "Compensation can reduce financial stress while leaving chronic workload and recovery problems unresolved.", "給料が高いと安心は増えますが、疲れる働き方を続けられるとは限りません。"),
        ("Control over start times and days off can matter as much as total hours.", "Schedule autonomy often shapes well-being independently of the number of contracted hours.", "始業時間や休みを選べることは、労働時間の長さと同じくらい大切です。"),
        ("Time autonomy means having real control over when work enters personal life.", "Time autonomy includes predictability, boundaries, and the ability to respond to care or health needs.", "時間の自由とは、仕事が私生活に入る時間を実際に調整できることです。"),
        ("A short demanding period needs an end date and time to recover.", "Temporary imbalance is safer when its purpose, limit, and recovery plan are explicit.", "忙しい期間を短くするなら、終わる時期と回復する時間が必要です。"),
    ),
    116: (
        ("Remote work can make quiet effort less visible to managers and teammates.", "Working remotely can reduce informal visibility even when measured output remains strong.", "在宅勤務では、静かに行う努力が上司や同僚に見えにくくなることがあります。"),
        ("Home and office networks may offer different levels of privacy and security.", "Sensitive work can depend on controlled devices, networks, and spaces that are not equally available everywhere.", "家と職場では、通信や情報の安全性が違う場合があります。"),
        ("Location flexibility can improve access for some disabilities or care needs.", "Location flexibility can support accessibility and care, although the right accommodation differs by person.", "場所を選べることは、障害や介護の必要がある人にとって働きやすさを高めることがあります。"),
        ("Heating, electricity, furniture, and internet costs move into the home during remote work.", "Remote work can transfer part of the employer's workspace cost to the worker's household.", "在宅勤務では、冷暖房、電気、家具、通信の費用を家庭が負担することがあります。"),
    ),
    117: (
        ("A familiar place can become a cue that tells the brain it is time to study.", "Repeated context can support concentration by making the start of a study routine more automatic.", "慣れた場所は、勉強を始める合図になることがあります。"),
        ("Short walks and planned breaks can reset attention in either place.", "The quality of a study session depends partly on movement and recovery, not only on the room.", "短い散歩や決めた休憩は、どちらの場所でも集中を戻す助けになります。"),
        ("Other people studying nearby can create gentle accountability.", "Gentle accountability from visible effort can support persistence without direct collaboration.", "近くで勉強する人がいると、自然に続けやすくなることがあります。"),
        ("A public study space limits private calls, speaking practice, and confidential work.", "Shared environments can restrict tasks that require speech, sensitive material, or control over interruption.", "公共の勉強場所では、私的な通話、声を出す練習、秘密の作業がしにくくなります。"),
    ),
    118: (
        ("A familiar seller can be easier to trust than an unknown marketplace account.", "Seller identity and accountability matter when platforms mix established retailers with unknown third parties.", "知らない出品者より、知っている店のほうが信頼しやすいことがあります。"),
        ("Online shopping can reveal purchase and browsing data to several companies.", "Digital purchases create records that may be shared across payment, advertising, and delivery systems.", "オンラインの買い物では、購入や閲覧の情報が複数の会社に残ることがあります。"),
        ("Delivery can improve access for people who cannot easily reach a shop.", "Online ordering can remove transport and mobility barriers that make physical retail inaccessible.", "配送は、店へ行くのが難しい人の買い物を助けます。"),
        ("Local stock can be limited even when a shop is convenient to visit.", "Physical access does not guarantee range, especially for specialised sizes, parts, or products.", "店へ行きやすくても、地域の在庫は少ない場合があります。"),
    ),
    119: (
        ("Sleep helps some memories become stronger while others fade.", "Memory consolidation during sleep preserves selected information rather than every experienced detail.", "睡眠中に強くなる記憶もあれば、薄れる記憶もあります。"),
        ("People often remember the meaning of an event better than its exact words or timing.", "Memory can preserve an event's gist while losing source, sequence, and verbal detail.", "人は、出来事の正確な言葉や順番より、意味をよく覚えていることがあります。"),
        ("A memory trigger can bring back a feeling before the full event is clear.", "A memory trigger may reactivate emotion before a person can place the memory in a coherent account.", "記憶のきっかけによって、出来事全体が分かる前に感情が戻ることがあります。"),
        ("Writing and photographs can preserve useful details without perfect recall.", "External records can support continuity and learning without requiring total biological memory.", "文章や写真なら、完全な記憶がなくても役立つ細部を残せます。"),
    ),
    120: (
        ("Keeping wealth secret can make honest conversations about money harder.", "Financial anonymity protects privacy while complicating openness in close relationships.", "富を秘密にすると、お金について正直に話すことが難しくなる場合があります。"),
        ("Respect based on a title can disappear faster than respect based on contribution.", "Status-based regard is less durable than respect grounded in conduct, competence, or service.", "肩書きによる尊敬は、貢献による尊敬より早く失われることがあります。"),
        ("Anonymity can protect privacy without removing responsibility.", "Anonymity can reduce unwanted exposure, although it does not erase accountability for choices that affect others.", "無名でいることは、責任をなくさずにプライバシーを守れます。"),
        ("Public recognition changes who can approach a person and how easily they can be left alone.", "Visibility can expand influence while narrowing control over access, attention, and ordinary privacy.", "人に知られると、近づいてくる人や、一人でいられる時間が変わります。"),
    ),
    121: (
        ("A skill learned deeply can make related skills easier to understand.", "Deep knowledge can transfer through shared principles, patterns, and methods of practice.", "一つの技能を深く学ぶと、関連する技能も理解しやすくなることがあります。"),
        ("Breadth helps a person notice when a problem belongs to another field.", "Cross-domain literacy improves problem framing even when a specialist must provide the final answer.", "幅広い知識があると、問題が別の分野に関係すると気づきやすくなります。"),
        ("A generalist can connect problems that specialists see separately.", "A strong generalist can translate across fields and recognize relationships that narrow expertise may miss.", "幅広い技能を持つ人は、専門家が別々に見る問題をつなげられます。"),
        ("Skills fade without use, so maintaining many abilities also takes time.", "Breadth carries a maintenance cost because unused competence decays and fields continue to change.", "技能は使わないと薄れるため、多くの能力を保つにも時間がかかります。"),
    ),
}

ARTICLE_TAILS = {
    107: (
        ("A higher income often comes with longer hours or more responsibility.", "Additional income may carry an obligation cost in longer hours, availability, or responsibility.", "収入が増えると、労働時間や責任も増えることがあります。"),
        ("Extra time can save money when it makes cooking, comparing prices, or doing repairs possible.", "Time can substitute for money when it allows planning, comparison, care, or practical work.", "時間に余裕があると、料理、価格比較、修理などでお金を節約できます。"),
        ("Money can also buy time through transport, delivery, or paid help.", "Money can convert into time by reducing travel, waiting, domestic work, or administrative effort.", "お金があれば、交通、配達、有料の助けによって時間を作ることもできます。"),
        ("Free hours do not feel free when worry or exhaustion fills them.", "Nominal free time has limited value when financial anxiety or fatigue consumes attention.", "心配や疲れでいっぱいなら、自由な時間があっても自由には感じられません。"),
        ("Health, family, and long-term plans can change which resource feels scarce.", "Life stage, care duties, health, and long-term goals can all redefine the more urgent shortage.", "健康、家族、長期的な計画によって、どちらが不足しているかは変わります。"),
        ("The useful goal is often enough money and enough time, not the maximum amount of either.", "A sustainable answer usually seeks an adequate floor for both resources rather than maximizing only one.", "大切なのは、どちらかを最大にすることより、十分なお金と十分な時間を確保することです。"),
    ),
    108: (
        ("Being known by many people can bring more invitations and more obligations.", "A wide network expands social opportunity while increasing requests, coordination, and claims on attention.", "多くの人に知られると、誘いが増える一方、応える必要も増えます。"),
        ("Close friendship needs repeated time, attention, and trust.", "Intimacy depends on sustained mutual attention rather than the number of names in a contact list.", "親しい友情には、繰り返す時間、気づかい、信頼が必要です。"),
        ("A hundred connections can still feel lonely when none is safe enough for honesty.", "Social reach does not prevent loneliness when no relationship supports vulnerability or dependable care.", "知り合いが百人いても、正直に話せる相手がいなければ孤独を感じます。"),
        ("Three close friends cannot meet every social or practical need.", "A small inner circle may offer depth while lacking the range needed for every interest, opportunity, or emergency.", "親しい友人三人だけで、すべての交流や実用的な必要を満たせるとは限りません。"),
        ("Moving, changing jobs, or entering a new community can make wider connections more valuable.", "Transitions increase the value of broad networks because information and belonging must be rebuilt quickly.", "引っ越し、転職、新しい地域への参加では、広いつながりの価値が高まります。"),
        ("Many people need a small trusted core and a wider circle around it.", "Healthy social lives often combine a dependable inner circle with looser relationships that provide range and renewal.", "多くの人には、信頼できる小さな中心と、その周りの広いつながりの両方が必要です。"),
    ),
    109: (
        ("Extreme heat and extreme cold can both become health risks.", "Once temperatures become extreme, the comparison shifts from comfort to health and safety.", "厳しい暑さも寒さも、健康上の危険になることがあります。"),
        ("Buildings and public transport change how difficult a season feels.", "Insulation, cooling, heating, and transport determine how strongly outdoor weather shapes daily life.", "建物や公共交通によって、季節の大変さは変わります。"),
        ("Long summer days create more outdoor time, but they can also disturb sleep.", "Extended daylight can support activity while making rest and temperature control harder.", "夏の長い日は外で過ごす時間を増やしますが、睡眠を妨げることもあります。"),
        ("Winter can offer quiet and snow activities while limiting movement.", "Winter supports some forms of rest and recreation but can restrict mobility and social contact.", "冬には静けさや雪の活動がありますが、移動が制限されることもあります。"),
        ("Energy cost matters when one season never ends.", "Permanent heating or cooling demand would make infrastructure and household cost central to the choice.", "一つの季節が続くなら、冷暖房のエネルギー費用が重要になります。"),
        ("The best climate depends on what people must do, not only what weather they enjoy.", "Climate preference changes with work, health, housing, transport, and the activities a person needs to maintain.", "よい気候は、好きな天気だけでなく、そこで何をする必要があるかで決まります。"),
    ),
    110: (
        ("A body clock influences when alertness and sleepiness arrive.", "Circadian timing affects attention, appetite, temperature, and the natural onset of sleep.", "体内時計は、集中しやすい時間や眠くなる時間に影響します。"),
        ("Sleep length matters as much as whether someone wakes early or late.", "An early schedule is not healthy by itself if it consistently reduces total sleep.", "早起きか遅起きかだけでなく、睡眠時間の長さも重要です。"),
        ("School, work, transport, and family often decide the schedule before preference does.", "Institutional timetables and care responsibilities can override a person's preferred rhythm.", "学校、仕事、交通、家族の予定が、好みより先に生活時間を決めることがあります。"),
        ("A consistent schedule is usually easier on the body than repeated large shifts.", "Regular sleep timing often supports recovery better than alternating sharply between early and late routines.", "大きく変わる生活より、一定した生活時間のほうが体には楽です。"),
        ("People sharing a home may need quiet at opposite times.", "Different rhythms in one household create practical negotiations over light, noise, meals, and shared time.", "同居する人の生活時間が違うと、静かにする時間も反対になることがあります。"),
        ("A good schedule fits both the body and the obligations that cannot move.", "The workable answer balances biological preference with fixed commitments and enough restorative sleep.", "よい生活時間は、体のリズムと動かせない予定の両方に合うものです。"),
    ),
    111: (
        ("Opening days, local holidays, and timed entry can shape a trip before transport does.", "Calendars and access rules can constrain an itinerary even when travel and lodging remain flexible.", "営業日、地域の祝日、入場時間によって、交通より先に旅程が決まることがあります。"),
        ("Spontaneity works better when changing direction is cheap and safe.", "Flexible travel becomes attractive when cancellation costs, safety risks, and access barriers are low.", "方向を変える費用や危険が小さいほど、行き当たりばったりの旅行がしやすくなります。"),
        ("Too many choices during a trip can create decision fatigue.", "Constantly deciding where to go, eat, or sleep can turn freedom into decision fatigue.", "旅行中に選択が多すぎると、決めることに疲れてしまいます。"),
        ("A detailed plan can reduce surprise as well as stress.", "Planning protects scarce experiences but may crowd out discoveries that only appear on the day.", "細かい計画はストレスを減らしますが、驚きも減らすことがあります。"),
        ("Travel companions often need agreement about what must be fixed and what can stay open.", "Shared travel works best when the group distinguishes non-negotiable bookings from flexible time.", "同行者とは、何を決め、何を自由にしておくか合意する必要があります。"),
        ("Many good trips use a planned backbone with open space around it.", "A hybrid itinerary can secure essential access while preserving room for weather, energy, and discovery.", "よい旅行の多くは、基本だけ計画し、その周りに自由な時間を残します。"),
    ),
    112: (
        ("Solo travel gives one person control over pace, meals, and changes of plan.", "Travelling alone concentrates decisions in one person and removes the need for constant coordination.", "一人旅では、速さ、食事、計画変更を自分で決められます。"),
        ("Company can make difficult moments safer and more enjoyable.", "A companion can provide practical support, shared attention, and emotional reassurance.", "同行者がいると、難しい場面がより安全で楽しくなります。"),
        ("Travelling together requires negotiation about money, energy, and interests.", "Shared travel creates coordination costs around budget, pace, privacy, and competing priorities.", "誰かとの旅行では、お金、体力、関心について調整が必要です。"),
        ("Being alone can feel peaceful in one place and isolating in another.", "The emotional cost of solitude depends on destination, duration, communication, and personal rhythm.", "一人でいることは、場所によって穏やかにも孤独にも感じられます。"),
        ("Sharing a room can save money while reducing privacy.", "A companion may lower transport and accommodation costs at the price of personal space.", "部屋を共有するとお金を節約できますが、プライバシーは減ります。"),
        ("Shared travel creates memories that can be discussed long after the trip ends.", "A companion becomes part of the record of a trip, adding another perspective to what happened.", "誰かとの旅行では、旅のあとも一緒に話せる思い出ができます。"),
    ),
    113: (
        ("Cities make work, transport, health care, and culture easier to reach.", "Urban density can reduce the time and coordination needed to access essential services and varied opportunities.", "都会では、仕事、交通、医療、文化にアクセスしやすくなります。"),
        ("That access often comes with higher housing costs and less private space.", "Urban convenience is frequently purchased through higher rent, smaller homes, noise, and crowding.", "その便利さには、住居費の高さや私的な空間の少なさが伴うことがあります。"),
        ("The countryside can offer quiet and space without guaranteeing an easy life.", "Lower density may provide calm and room while increasing travel, maintenance, and dependence on a car.", "田舎には静けさと空間がありますが、生活が必ず楽になるわけではありません。"),
        ("A small community can offer strong local ties while making privacy harder.", "Close local networks may provide belonging and practical help together with greater social visibility.", "小さな地域では人とのつながりが強い一方、プライバシーを保ちにくいことがあります。"),
        ("Remote work can change where someone is able to live, but not every other obligation.", "Location-flexible work widens residential choice only when care, education, health, and connectivity also fit.", "在宅勤務で住める場所は増えますが、ほかの義務までなくなるわけではありません。"),
        ("The right place often changes with health, family, transport, and life stage.", "Residential preference is dynamic because mobility, relationships, and essential services change over a lifetime.", "健康、家族、交通、人生の段階によって、合う場所は変わります。"),
    ),
    114: (
        ("Children, older people, and some medical conditions increase the risk from indoor heat.", "Heat exposure is not equally dangerous; age, health, medication, and mobility all affect risk.", "子ども、高齢者、特定の病気がある人は、室内の暑さによる危険が高くなります。"),
        ("Mobile data, home internet, and public Wi-Fi do not fail in exactly the same way.", "Different connection routes create partial backups, although coverage, cost, and power still limit them.", "モバイル通信、家庭のネット、公共Wi-Fiは、同じように止まるとは限りません。"),
        ("Fans help the body release heat, but they cannot make every hot room safe.", "Air movement improves comfort, yet extreme heat and humidity can exceed what fans can safely solve.", "扇風機は体の熱を逃がしますが、どんな暑い部屋でも安全にできるわけではありません。"),
        ("Libraries, community centres, and other cool spaces can change the choice.", "Public cooling spaces can reduce individual risk only when they are accessible during the hottest hours.", "図書館や公共施設など涼しい場所を使えるかどうかで、選択は変わります。"),
        ("A day offline can create rest, but forced disconnection can also block important duties.", "Disconnection may restore attention while simultaneously excluding people from essential systems.", "一日ネットを離れると休めますが、大切な用事ができなくなることもあります。"),
        ("The honest answer depends on season, safety, building quality, and what the internet is needed for.", "A responsible comparison separates optional convenience from essential cooling and essential connectivity.", "答えは、季節、安全、建物、ネットの用途によって変わります。"),
    ),
    115: (
        ("Salary is only one part of compensation; leave, health support, and retirement benefits also matter.", "Total compensation includes benefits, paid leave, insurance, retirement support, and risk—not salary alone.", "報酬には、給料だけでなく、休暇、健康支援、退職後の制度も含まれます。"),
        ("A shorter workday does not remove unpaid care or household work.", "Work-life balance must account for care and domestic labour that continues outside paid employment.", "労働時間が短くても、介護や家事などの無給の仕事はなくなりません。"),
        ("Long hours can remove the time needed to enjoy the income they produce.", "Additional earnings may lose practical value when work eliminates rest, relationships, and the time to use them.", "長時間働くと、得た収入を楽しむ時間がなくなることがあります。"),
        ("Low pay can also damage rest when every expense creates worry.", "Insufficient compensation can make nominal free time stressful and insecure.", "給料が低いと、出費の心配で休む時間も落ち着かなくなります。"),
        ("A lower-paid role can still be valuable when it builds skills, support, or future options.", "Career value may come through learning, mentorship, autonomy, or mobility rather than immediate compensation.", "給料が低い仕事でも、技能、支援、将来の選択肢が増えるなら価値があります。"),
        ("The better offer protects the needs that cannot be postponed.", "The decision should identify which financial, health, care, or career need is genuinely time-sensitive.", "よりよい条件は、後回しにできない必要を守るものです。"),
    ),
    116: (
        ("Some tasks need quiet concentration, while others improve through quick conversation.", "Location should follow task design: individual focus and rapid collaborative feedback need different conditions.", "静かな集中が必要な作業もあれば、短い会話でよくなる作業もあります。"),
        ("A short commute feels different from a long and unreliable one.", "Commute burden depends on duration, predictability, crowding, cost, and whether the time can be used.", "短い通勤と、長く不安定な通勤では負担が違います。"),
        ("Working from home requires suitable space, equipment, and boundaries.", "Remote work shifts the cost of space, connectivity, ergonomics, and interruption into the home.", "在宅勤務には、合う空間、設備、生活との境界が必要です。"),
        ("An office can support learning when people are available to help.", "Co-location particularly benefits informal learning when experienced colleagues are accessible rather than merely present.", "職場では、助けてくれる人が近くにいると学びやすくなります。"),
        ("Being in the same building does not automatically create useful collaboration.", "Office attendance has limited value when schedules, roles, or norms still prevent meaningful interaction.", "同じ建物にいても、必ずよい協働が生まれるわけではありません。"),
        ("A good hybrid plan decides which tasks need people together and which need quiet.", "Effective hybrid work coordinates location around purpose instead of assigning days without a reason.", "よいハイブリッド勤務は、一緒にする作業と静かにする作業を分けます。"),
    ),
    117: (
        ("A little background activity helps some people begin, while it distracts others.", "Moderate ambient stimulation can support attention for some learners and fragment it for others.", "少し周りに動きがあると始めやすい人も、気が散る人もいます。"),
        ("Leaving home can create a useful ritual for starting work.", "The journey to a separate place can act as a transition cue that home does not provide.", "家を出ることが、作業を始めるよい習慣になる場合があります。"),
        ("A café costs money and may not guarantee a seat, power, or quiet.", "Café study depends on repeated spending and uncertain access to space, electricity, and acceptable noise.", "カフェではお金がかかり、席、電源、静けさが必ずあるとは限りません。"),
        ("Home gives access to books, equipment, food, and privacy.", "A well-designed home setting offers control over materials, breaks, sound, lighting, and privacy.", "家では、本、設備、食事、プライバシーを利用しやすいです。"),
        ("Comfort at home can make it easier to postpone the task.", "The absence of external structure can turn domestic comfort into procrastination.", "家で快適すぎると、作業を先延ばしにしやすくなります。"),
        ("The best place can change with the task: reading, writing, memorising, and meeting are different.", "Different cognitive tasks benefit from different levels of control, stimulation, privacy, and equipment.", "読む、書く、覚える、話し合うでは、合う場所が違います。"),
    ),
    118: (
        ("Online reviews add information, but they do not remove uncertainty about fit or quality.", "Reviews broaden evidence while remaining vulnerable to selection bias, manipulation, and differences in personal use.", "オンラインのレビューは情報を増やしますが、サイズや品質の不確かさは残ります。"),
        ("A shop lets customers compare texture, size, colour, and comfort directly.", "Physical inspection provides sensory evidence that specifications and images cannot fully reproduce.", "店舗では、手触り、サイズ、色、使い心地を直接比べられます。"),
        ("The cheapest listed price may not be the lowest total cost after delivery and returns.", "Total purchase cost includes shipping, waiting, return friction, travel, and the risk of a poor match.", "表示価格が最安でも、配送や返品まで含めると総額は安くない場合があります。"),
        ("Online shopping saves travel time but can increase time spent searching.", "Digital convenience reduces physical travel while potentially expanding comparison and decision time.", "オンラインは移動時間を減らしますが、探す時間が増えることもあります。"),
        ("A local shop can provide immediate help, repair, or exchange.", "In-person retail may add after-sales service and accountability that are hard to value before a problem occurs.", "近くの店では、すぐに相談、修理、交換ができる場合があります。"),
        ("The best method depends on the product, urgency, price, and cost of being wrong.", "Purchase channel should match the information needed and the consequences of a mistaken choice.", "よい買い方は、商品、急ぎ、価格、買い間違いの負担で変わります。"),
    ),
    119: (
        ("Attention decides which parts of an event are likely to enter memory at all.", "Memory begins with selective attention, so many details are never encoded rather than later forgotten.", "そもそも何を記憶するかは、そのとき何に注意を向けたかで変わります。"),
        ("Painful memories can feel vivid even when ordinary details fade.", "Emotion can preserve the force of an experience while factual detail becomes incomplete.", "つらい記憶は、普通の細部が薄れても鮮明に感じられることがあります。"),
        ("Forgetting can protect attention, but it can also remove useful lessons.", "Letting details fade may reduce distress while weakening evidence, continuity, or learning.", "忘れることは心を守りますが、役立つ学びも失うことがあります。"),
        ("Forgetting some details can make the main pattern or lesson easier to see.", "Selective forgetting can support abstraction, although it may also discard evidence that later matters.", "細かいことを一部忘れると、全体のパターンや学びが見えやすくなることがあります。"),
        ("Remembering everything would also mean keeping every mistake and embarrassment clear.", "Perfect recall would preserve trivial pain and social mistakes alongside valuable knowledge.", "すべて覚えるなら、失敗や恥ずかしい出来事も鮮明に残ります。"),
        ("A good choice would protect useful memories while helping people live with painful ones.", "The better question is how to preserve learning and continuity while giving people agency and support around distressing memories.", "よい選択は、役立つ記憶を守りながら、つらい記憶とともに生きる人を支えるものです。"),
    ),
    120: (
        ("Wealth can create privacy and choice without creating trust or respect.", "Financial security expands private options, but social regard depends on conduct and contribution.", "富はプライバシーや選択肢を増やしますが、信頼や尊敬までは生みません。"),
        ("Respect can feel meaningful while also creating pressure to keep meeting expectations.", "Public regard can affirm contribution and simultaneously impose visibility, scrutiny, and role pressure.", "尊敬は意味を感じさせますが、期待に応え続ける圧力にもなります。"),
        ("An ordinary income can still support a secure life when needs and public services are stable.", "Income level cannot be judged apart from housing, health care, obligations, and the security provided by institutions.", "必要なものや公共サービスが安定していれば、普通の収入でも安心して暮らせます。"),
        ("Anonymity protects people from unwanted attention but can limit influence.", "Remaining unknown reduces exposure while making it harder to mobilise reputation for public impact.", "無名でいると不要な注目を避けられますが、影響力は小さくなる場合があります。"),
        ("Anonymous giving can help others without turning generosity into status.", "Private contribution can separate social benefit from recognition, branding, or personal prestige.", "名前を出さずに人を助ければ、善意を地位に変えずにすみます。"),
        ("Both money and reputation are fragile if a life depends on them alone.", "A resilient life needs relationships, purpose, privacy, and security beyond either wealth or public approval.", "お金も評判も、それだけに人生を頼ると不安定です。"),
    ),
    121: (
        ("Deep expertise grows through long practice and repeated feedback.", "Specialisation requires sustained deliberate practice and access to increasingly demanding feedback.", "深い専門性は、長い練習と繰り返すフィードバックで育ちます。"),
        ("Broad skills help when a problem crosses several fields.", "Breadth becomes valuable when coordination and translation matter more than isolated technical depth.", "幅広い技能は、問題が複数の分野にまたがるときに役立ちます。"),
        ("A team can combine specialists instead of asking one person to know everything.", "Organisations can distribute depth across specialists while relying on others to connect their work.", "チームなら、一人にすべてを求めず、複数の専門家を組み合わせられます。"),
        ("Trying several skills can reveal which one deserves deeper study.", "Exploration is not wasted breadth when it helps identify the field in which deeper investment is worthwhile.", "いくつかの技能を試すことで、深く学ぶべき一つが見つかります。"),
        ("A specialist still needs enough range to explain and apply their knowledge.", "Even narrow expertise depends on communication, judgment, and an understanding of adjacent fields.", "専門家にも、知識を説明し活用するための幅広さが必要です。"),
        ("The useful shape may be broad foundations with one or two deep strengths.", "A T-shaped profile combines cross-domain literacy with selected areas of genuine mastery.", "幅広い基礎と、一つか二つの深い強みを組み合わせる方法もあります。"),
    ),
}


QUESTION_POOLS = {
    107: (
        q("saved-time", "Time costs money", "時間で節約", "When have you chosen a slower option to save money?", "When have you chosen a slower option because it cost less?", "お金を節約するために、時間のかかる方法を選んだのはいつですか？", ("What did you save money on?", "Would you make the same choice again?")),
        q("free-hours", "Three free hours", "自由な三時間", "What would you do with three unexpected free hours?", "How would you spend three free hours with no plans?", "突然、自由な時間が三時間できたら、何をしますか？", ("What would you do first?", "Would you spend the time alone or with someone?")),
        q("choice", "Choose one", "どちらを選ぶ", "Which would help more tomorrow: extra time or extra money?", "Which would improve tomorrow more: extra time or extra money?", "明日、より役立つのは、自由な時間とお金のどちらですか？", ("What would it help you do?", "What is one good reason to choose the other option?")),
        q("first-change", "Money this month", "今月のお金", "What's one problem extra money could solve this month?", "What problem could extra money solve for you this month?", "今月、お金が増えたら解決できることは何ですか？", ("How urgent is it?", "Would a small amount help?")),
        q("opposite", "More free time", "自由な時間", "What part of life would extra time improve?", "Which part of your life would benefit most from extra time?", "自由な時間が増えたら、生活のどの部分がよくなりますか？", ("How would you use the time?", "Would one extra hour be enough to help?")),
        q("ten-hours", "Ten extra hours", "週に十時間", "Would you take a pay raise if it meant working ten more hours each week?", "Would a pay raise be worth ten extra work hours every week?", "給料が上がっても毎週十時間多く働くなら、引き受けますか？", ("What would those ten hours replace?", "Would a short-term schedule change your answer?")),
        q("future", "When time wins", "時間を選ぶとき", "When would you choose time even if you needed the money?", "When would time matter more even if money was tight?", "お金が必要でも、時間を選ぶのはどんなときですか？", ("What would the time protect?", "Would the choice be temporary or long-term?")),
    ),
    108: (
        q("slow-talk", "A long conversation", "ゆっくり話す", "What makes a long conversation with one friend feel worthwhile?", "Which quality allows one friendship to support a genuinely long conversation?", "一人の友人とゆっくり話すなら、何が大切ですか？", ("What makes it easy to be honest?", "Does frequency matter?")),
        q("crowd", "A room of strangers", "知らない人の集まり", "How do you start a conversation in a room full of strangers?", "What makes a large unfamiliar gathering easier to enter?", "知らない人が多い集まりでは、どう会話を始めますか？", ("What opening question works well?", "Which kind of event feels easiest?")),
        q("choice", "Choose a circle", "人間関係を選ぶ", "Would you choose a hundred friendly contacts or three close friends?", "Would you rather have a broad social network or a very small trusted circle?", "友人百人と親しい友人三人なら、どちらを選びますか？", ("What does your choice provide?", "What does the other side provide?")),
        q("daily-life", "Daily contact", "日常のつながり", "How would daily life change if you could keep only that kind of friendship?", "What would disappear from daily life if every relationship had the same level of closeness?", "その種類の友人関係だけなら、日常はどう変わりますか？", ("Who would you contact most often?", "Which kind of interaction would disappear?")),
        q("opposite", "When the other helps", "反対側が必要なとき", "When is the other kind of social circle more useful?", "Which situation gives the rejected kind of relationship a clear advantage?", "どんなときに、反対の人間関係のほうが役立ちますか？", ("What kind of support is needed?", "How quickly is it needed?")),
        q("new-city", "A new city", "新しい町", "Which circle would help more after moving to a new city?", "After arriving in a new city, would breadth or closeness matter first?", "新しい町へ引っ越したら、どちらの人間関係が先に役立ちますか？", ("How would you meet people?", "How long does closeness take to build?")),
        q("change", "What changes the answer", "答えを変えるもの", "What change in your social life could make you choose differently?", "Which loss or new opportunity would reverse your preferred social structure?", "人間関係にどんな変化があれば、反対を選びますか？", ("Would more free time matter?", "Would moving somewhere new matter?")),
    ),
    109: (
        q("hard-day", "A difficult weather day", "大変な天気", "What makes a very hot or very cold day difficult?", "Which practical burden makes extreme heat or cold hardest to manage?", "暑い日や寒い日を大変にするものは何ですか？", ("Does travel make it worse?", "Does sleep change?")),
        q("perfect-day", "Perfect weather", "完璧な天気", "What would you do outside on a day with perfect weather?", "How would you use a full day with your ideal temperature and light?", "完璧な天気の日なら、外で何をしたいですか？", ("Which outdoor place would you visit?", "How many hours would you stay outside?")),
        q("choice", "One season forever", "一つの季節", "Would you choose endless summer or endless winter?", "If one climate continued all year, would you keep summer or winter?", "終わらない夏と終わらない冬なら、どちらを選びますか？", ("Which activity shapes your answer?", "What is the best part of the other season?")),
        q("daily-life", "Everyday life", "毎日の生活", "How would everyday life change if your season never ended?", "Which routine would change most under a permanent summer or winter?", "選んだ季節が終わらなければ、日常はどう変わりますか？", ("What would happen to clothing?", "What would happen to outdoor plans?")),
        q("comfortable-home", "Perfect indoors", "家の中は快適", "Would your answer stay the same if every building and train were comfortable?", "If indoor temperature were always controlled, which outdoor difference would decide the choice?", "建物や交通機関がいつも快適でも、答えは同じですか？", ("Would daylight matter more?", "Would energy cost still matter?")),
        q("daylight", "Hours of daylight", "日の長さ", "Would equal daylight in both seasons change your answer?", "How much of your preference comes from daylight rather than temperature?", "夏と冬の日の長さが同じなら、選択は変わりますか？", ("Does light affect your mood?", "Does it affect your sleep?")),
        q("switch", "When you switch", "答えが変わる条件", "What weather condition would make you switch seasons?", "Which exact temperature, rain, or snow condition would reverse your choice?", "どんな天候なら、反対の季節を選びますか？", ("How long could you accept it?", "What would you do in that weather?")),
    ),
    110: (
        q("clear-head", "Your clearest hour", "頭がさえる時間", "When does your mind usually feel clearest?", "At what time does your attention tend to be most reliable?", "頭がいちばんさえるのは、何時ごろですか？", ("What kind of task fits that time?", "How long does the focus last?")),
        q("free-day", "A day with no schedule", "予定のない日", "When would you sleep and wake if tomorrow had no schedule?", "What sleep schedule would you choose with no external commitments tomorrow?", "明日何も予定がなければ、何時に寝て起きますか？", ("How much sleep would that give you?", "Would you keep the same schedule for a week?")),
        q("choice", "Early or late", "朝型か夜型", "Would you choose an early schedule or a late one?", "Would an early-morning rhythm or a late-night rhythm suit you better?", "朝型の生活と夜型の生活なら、どちらを選びますか？", ("When would you do your hardest work?", "What is attractive about the other schedule?")),
        q("whole-day", "A changed day", "一日の変化", "How would meals, exercise, and social time change with that schedule?", "Which parts of an ordinary day would shift under your chosen rhythm?", "その生活時間なら、食事、運動、人と会う時間はどう変わりますか？", ("What would be easiest to change?", "What would be hardest?")),
        q("housemate", "Opposite schedules", "同居人との時間", "How would you live with someone on the opposite schedule?", "What rules would make opposite rhythms workable in one home?", "反対の生活時間の人と暮らすなら、どう調整しますか？", ("When would the home need to be quiet?", "When would you spend time together?")),
        q("no-morning-duty", "No early obligation", "朝の予定なし", "Would you keep the same rhythm if you never had morning obligations?", "How much of your current rhythm would survive without fixed morning commitments?", "朝の予定がなくても、同じ生活時間を選びますか？", ("Would health affect the answer?", "Would social plans affect it?")),
        q("switch", "A schedule that changes you", "答えを変える予定", "What kind of schedule would make you switch to the other rhythm?", "Which fixed commitment would be strong enough to reverse your preferred rhythm?", "どんな予定なら、反対の生活時間を選びますか？", ("How long could you maintain it?", "How would you return to your usual rhythm?")),
    ),
    111: (
        q("surprise", "When a plan fails", "計画どおりでない時", "What can make a trip better after the original plan fails?", "When does an unexpected change improve a trip rather than ruin it?", "計画どおりにならなかった旅行を、よいものにするのは何ですか？", ("How quickly should the plan change?", "Can the surprise become a good memory?")),
        q("first-decision", "The first decision", "最初に決めること", "What would you decide first for a short trip tomorrow?", "Which single decision would you lock in first for a trip beginning tomorrow?", "明日短い旅行へ行くなら、最初に何を決めますか？", ("What could stay open?", "Would transport or accommodation come first?")),
        q("choice", "Plan or improvise", "計画かその場か", "Would you plan a three-day trip or decide as you go?", "For a short trip, would you protect certainty or leave room for improvisation?", "三日間の旅行なら、計画するのとその場で決めるのと、どちらがよいですか？", ("What would you book in advance?", "What would you leave undecided?")),
        q("month", "Every trip", "すべての旅行", "How would travel change if every trip had to follow your chosen style?", "What would become easier and harder if every trip used the same planning style?", "すべての旅行がそのスタイルなら、何が変わりますか？", ("Would preparation take longer?", "Would the trip feel freer?")),
        q("hotel-only", "Only the room is booked", "宿だけ予約", "Would you feel relaxed on a week-long trip with only the room booked?", "If accommodation were the only fixed part of a week-long trip, would that feel freeing or stressful?", "一週間の旅行で宿だけ予約してあれば、気楽ですか？", ("Would you also fix transport?", "What would you do on the first day?")),
        q("different-partner", "A different planner", "計画の違う同行者", "How would you travel with someone who plans very differently?", "Which decisions must two travellers settle when their planning styles conflict?", "計画のしかたが違う人と、どう旅行しますか？", ("What must be agreed in advance?", "Who decides when you disagree?")),
        q("switch", "A trip that changes the style", "答えを変える旅行", "What kind of trip would make you use the opposite style?", "Which destination, duration, or risk would reverse your planning preference?", "どんな旅行なら、反対のスタイルを選びますか？", ("Would a first visit matter?", "Would travelling alone matter?")),
    ),
    112: (
        q("alone-time", "Time alone", "一人の時間", "When does time alone improve a trip with other people?", "How can planned time apart protect a trip with companions?", "誰かとの旅行で、一人の時間が役立つのはどんなときですか？", ("How long should it be?", "How would you explain the need?")),
        q("share-view", "Share a view", "景色を共有", "Who would you want to share a beautiful view with?", "Which person would add the most to seeing an extraordinary place?", "すてきな景色を、誰と共有したいですか？", ("Would you send a photo?", "Would you want them there in person?")),
        q("choice", "Alone or together", "一人か誰かと", "Would you travel to a new place alone or with someone?", "For an unfamiliar destination, would independence or companionship matter more?", "初めての場所なら、一人と誰かとの旅行のどちらを選びますか？", ("Who would be the ideal companion?", "What is the best part of the other style?")),
        q("every-trip", "Every trip", "すべての旅行", "How would travel change if you could use only that style?", "What would you gain and lose if every future trip followed the same social format?", "これからすべての旅行がその形なら、何が変わりますか？", ("Who would make the decisions?", "Which travel experience would be lost?")),
        q("new-country", "Three days somewhere new", "初めての国で三日", "Would you spend three days in a new country alone?", "Would independence still win for three days in an unfamiliar country?", "初めての国で三日過ごすなら、一人で行きますか？", ("Would language change the answer?", "Would safety after dark matter?")),
        q("planner", "Someone else plans", "相手が計画", "Would your answer change if a trusted companion planned everything?", "If a trusted companion handled every arrangement, would company become more attractive?", "信頼できる同行者がすべて計画するなら、選択は変わりますか？", ("What would you still decide yourself?", "How much trust would that require?")),
        q("switch", "Destination and company", "旅先と同行者", "Which destination or companion would make you switch?", "What combination of place, duration, and companion would reverse your choice?", "どんな旅先や同行者なら、反対を選びますか？", ("Would trip length matter?", "Would the purpose of the trip matter?")),
    ),
    113: (
        q("convenience", "Nearby convenience", "近くの便利さ", "Which nearby service matters most in everyday life?", "Which form of local access saves the most time or difficulty each week?", "日常で、近くにあると最も助かるものは何ですか？", ("How often is it used?", "Could transport replace proximity?")),
        q("window", "Your window view", "窓からの景色", "What would you choose to see outside your window?", "Which view would improve an ordinary morning most?", "窓の外に何が見えたらうれしいですか？", ("Would you trade convenience for it?", "Would the answer change at night?")),
        q("choice", "City or countryside", "都会か田舎", "Would you choose a lively city or a quiet rural area?", "For daily life, would urban access or rural space matter more?", "日常生活なら、都会と田舎のどちらを選びますか？", ("What would you use most there?", "What is the strongest advantage of the other place?")),
        q("move", "After the move", "引っ越した後", "What would change first after moving to your chosen place?", "Which daily routine would shift most after moving to that setting?", "選んだ場所へ引っ越したら、最初に何が変わりますか？", ("Would travel time change?", "What would be hardest to adjust to?")),
        q("no-car", "Life without a car", "車なしの生活", "Which place works better without a car?", "Without access to a car, which setting remains practical?", "車なしで暮らすなら、都会と田舎のどちらですか？", ("How would you buy food?", "How would you reach health care?")),
        q("small-town", "A well-served small town", "便利な小さな町", "Would a small town with a hospital and shops change your answer?", "If a rural town had reliable services, which urban advantage would still matter?", "病院や店が近い小さな町なら、選択は変わりますか？", ("Which service would still be missing?", "How far could work or school be?")),
        q("switch", "Conditions for moving", "住む場所を変える条件", "What condition would make you choose the opposite place?", "Which change in transport, family, or health would reverse your residential preference?", "どんな生活条件なら、反対の場所を選びますか？", ("Would who you live with matter?", "How long would you stay?")),
    ),
    114: (
        q("outage", "One hour offline", "一時間オフライン", "What becomes difficult after one hour without internet?", "Which essential task fails first during a short internet outage?", "インターネットが一時間使えないと、最初に何が困りますか？", ("What could still be done offline?", "When would the outage become serious?")),
        q("cool-day", "A cool day offline", "涼しい日のオフライン", "How would you spend half a cool day without a phone?", "What would make a cool offline half-day restorative rather than inconvenient?", "涼しい日にスマホなしで半日過ごすなら、何をしますか？", ("Which offline place would you visit?", "What would you miss most?")),
        q("choice", "Choose one loss", "一つを諦める", "For one summer, would you give up internet or air conditioning?", "Which loss would be more manageable for one summer: connectivity or air conditioning?", "一夏の間、インターネットとエアコンのどちらを諦めますか？", ("Which duty shapes the answer?", "What makes the other loss harder?")),
        q("first-problem", "The first problem", "最初に困ること", "What would go wrong first during one day without your choice?", "Which ordinary system would fail first after a full day without the service you gave up?", "選んだものなしで一日過ごすと、最初に何が困りますか？", ("Would work or study be affected?", "Would anyone else be affected?")),
        q("cool-spring", "A cool spring day", "涼しい春の日", "On one cool spring day, which loss would be easier?", "If heat were not a safety issue for one day, which inconvenience would you accept?", "涼しい春の日に一日だけなら、どちらを諦めますか？", ("What would you do offline?", "Where could you go without air conditioning?")),
        q("safe-place", "A safe cool place", "安全に涼める場所", "Would a nearby safe, cool place change your summer answer?", "If reliable public cooling were available all day, would the balance change?", "近くに安全で涼しい場所があれば、夏の答えは変わりますか？", ("Would it need to open at night?", "How far could it be?")),
        q("switch", "Season and safety", "季節と安全", "Which season or safety condition would make you switch?", "What temperature or access condition would reverse the choice?", "どんな季節や安全条件なら、反対を選びますか？", ("How many hours would be safe?", "Which alternative space would be necessary?")),
    ),
    115: (
        q("good-rest", "A well-rested day", "しっかり休めた日", "What makes a day off feel genuinely restful?", "Which boundary allows rest to restore attention after work or study?", "しっかり休めたと感じるには、何が必要ですか？", ("What time must obligations end?", "What would you do with the evening?")),
        q("protected-time", "Time you protect", "守りたい時間", "Which part of the day would you refuse to give up?", "Which daily period is most important to protect from work?", "一日の中で、必ず守りたい自分の時間はいつですか？", ("What belongs in that time?", "How could you protect it during a busy week?")),
        q("choice", "Time or salary", "時間か給料", "Would you choose more free time or a higher income for the next year?", "Over the next year, would greater time autonomy or higher compensation matter more?", "これから一年、自由な時間と高い収入のどちらを選びますか？", ("Which need is more urgent?", "What is the main benefit of the other side?")),
        q("only-one", "Only one benefit", "一つだけ得る", "How would daily life change if you could gain only your choice?", "What would improve and deteriorate if only the chosen benefit increased?", "選んだ条件だけがよくなれば、日常はどう変わりますか？", ("Would working hours change?", "Which part of current life would be lost?")),
        q("nights-weekends", "Nights and weekends", "夜と週末", "Would high pay be worth frequently losing nights and weekends?", "How much compensation could justify regularly surrendering evenings and weekends?", "高い給料でも夜や週末をよく諦めるなら、受け入れますか？", ("Which commitment could not be sacrificed?", "Would three months feel different from three years?")),
        q("one-year", "Exactly one year", "一年だけ", "Would a clear one-year limit make high pay easier to choose?", "Does a fixed one-year horizon make a period of imbalance defensible?", "ちょうど一年だけなら、高い給料を選びやすくなりますか？", ("What would the year need to achieve?", "How would you recover afterward?")),
        q("switch", "A new responsibility", "新しい責任", "What new responsibility or goal would make you switch?", "Which financial, health, or care obligation would reverse your choice?", "どんな責任や目標ができたら、反対を選びますか？", ("How urgent would it need to be?", "Would the switch be temporary?")),
    ),
    116: (
        q("distraction", "At-home distraction", "家で気が散るもの", "What is the biggest distraction when working or studying at home?", "Which interruption most weakens focused work at home?", "家で仕事や勉強をするとき、いちばん邪魔になるものは何ですか？", ("How could the space be changed?", "Would another location solve it?")),
        q("commute-time", "Time without a commute", "通勤のない時間", "How would you use the time saved by removing a commute?", "What would become possible if daily travel time disappeared?", "通勤時間がなくなったら、その時間をどう使いますか？", ("Would you use it the same way every day?", "Would it improve rest or relationships?")),
        q("choice", "Home or shared workplace", "家か共有の職場", "For focused work, would you choose home or a shared workplace?", "Which setting better supports demanding work: home or a shared workplace?", "集中する仕事なら、家と共有の職場のどちらを選びますか？", ("Which task shapes the answer?", "What does the other place offer?")),
        q("one-place", "Every day in one place", "毎日同じ場所", "How would your day change if you had to use only that place?", "What would improve and decline if every working day happened in the same location?", "毎日その場所だけで働くなら、一日はどう変わりますか？", ("Would communication change?", "What would become inconvenient?")),
        q("quiet-office", "A quiet office nearby", "近くて静かな職場", "Would a quiet office fifteen minutes away change your answer?", "If the office guaranteed quiet and a fifteen-minute commute, would it gain the advantage?", "静かな職場が十五分の場所にあれば、選択は変わりますか？", ("Who would you want to meet there?", "What if the quiet seat disappeared?")),
        q("team-day", "One team day", "週一回のチーム日", "Would meeting the team only once a week be enough?", "Which activities belong on a single shared team day?", "週に一日だけチームに会うなら、十分ですか？", ("What should happen that day?", "Which tasks should stay at home?")),
        q("switch", "Task and space", "作業と空間", "Which task or space condition would make you switch locations?", "What change in collaboration, equipment, or home space would reverse your preference?", "どんな作業や空間なら、反対の場所を選びますか？", ("Would the people involved matter?", "Would the number of days matter?")),
    ),
    117: (
        q("best-focus", "Your best focus", "集中できる場所", "What makes a place easy to concentrate in?", "Which feature most reliably creates deep focus for you?", "集中しやすい場所には、どんな特徴がありますか？", ("Does sound help or hurt?", "Would you return there?")),
        q("one-hour", "One focused hour", "集中する一時間", "Where would you sit to finish one important task in an hour?", "Which setting would you choose for one demanding hour with a clear deadline?", "一時間で大切な作業を終えるなら、どこに座りますか？", ("What task would it be?", "Would a longer session change the place?")),
        q("choice", "Café or home", "カフェか家", "For two hours of serious study, would you choose a café or home?", "For a demanding two-hour study session, which setting would support better attention?", "二時間しっかり勉強するなら、カフェと家のどちらを選びますか？", ("What would you bring?", "What is the best feature of the other place?")),
        q("one-month", "One place for a month", "一か月同じ場所", "How would your routine change if you used only that place for a month?", "What habit would develop after a month of studying in only one setting?", "一か月その場所だけで勉強したら、習慣はどう変わりますか？", ("Would the start time change?", "What would happen when focus broke?")),
        q("drink-cost", "The price of a seat", "席にかかる費用", "Would you keep using a quiet café if you had to buy a drink every time?", "How much repeated spending is a productive study setting worth?", "静かなカフェでも毎回飲み物を買うなら、通い続けますか？", ("What if there were no seat?", "Would daily visits stay effective?")),
        q("home-desk", "A better home setup", "家の机と照明", "Would a good desk and lighting at home change your choice?", "If home gained an excellent desk, lighting, and fewer interruptions, would the café still win?", "家に良い机と照明ができたら、選択は変わりますか？", ("What else would the room need?", "Would you still visit cafés sometimes?")),
        q("switch", "Task and setting", "課題と場所", "Which task or room condition would make you switch places?", "What combination of task, noise, and duration would reverse your choice?", "どんな課題や空間なら、反対の場所を選びますか？", ("Would group work change it?", "Would a longer session change it?")),
    ),
    118: (
        q("photo-match", "The product photo", "商品写真", "What makes an online product feel trustworthy?", "Which evidence makes an online listing reliable enough to buy from?", "オンラインの商品を信頼するには、何が必要ですか？", ("How much do reviews matter?", "What would make you return it?")),
        q("urgent", "Needed today", "今日必要", "Where would you look first for something you needed today?", "If an item were essential today, which buying channel would you trust first?", "今日必要な物なら、最初にどこを探しますか？", ("Would price or certainty matter more?", "Could delivery be trusted?")),
        q("choice", "Online or in person", "ネットか店頭", "For an important purchase, would you buy online or in a shop?", "For a high-stakes purchase, would digital range or direct inspection matter more?", "大切な買い物なら、オンラインと店舗のどちらで買いますか？", ("Which product are you imagining?", "What is the other method better at?")),
        q("only-one", "Only one method", "一つの買い方", "How would shopping change if you could use only your chosen method?", "What convenience and information would disappear if only one purchase channel remained?", "選んだ買い方しか使えなければ、買い物はどう変わりますか？", ("How would you compare prices?", "How would returns work?")),
        q("cheap-return", "Cheaper but hard to return", "安いが返品困難", "Would you buy online if it were cheaper but hard to return?", "How large must the online saving be to justify difficult returns?", "ネットのほうが安くても返品が難しいなら、買いますか？", ("What would you check first?", "Would seeing it in a shop help?")),
        q("same-day", "Free delivery today", "当日無料配送", "Would free same-day delivery remove the reason to visit a shop?", "If delivery were free and immediate, which value would physical shops still provide?", "無料で当日に届くなら、店へ行く理由は残りますか？", ("Which products still need inspection?", "Would expert help matter?")),
        q("switch", "A product that changes the method", "買い方を変える商品", "Which product would make you use the other buying method?", "What combination of price, urgency, and uncertainty would reverse your choice?", "どんな商品なら、反対の買い方を選びますか？", ("Would clothing and electronics differ?", "Would a gift change the answer?")),
    ),
    119: (
        q("photo-memory", "A memory from a photo", "写真で戻る記憶", "What kind of happy memory can a photograph bring back?", "Why can a small visual cue restore a forgotten positive memory?", "写真を見ると、どんな楽しい記憶が戻ることがありますか？", ("Which detail returns first?", "Does the feeling return too?")),
        q("small-moment", "A small moment to keep", "残したい小さな出来事", "Which small ordinary moment is worth remembering for years?", "What makes an ordinary moment important enough to preserve?", "長く覚えていたい小さな出来事は何ですか？", ("Would you record it?", "Why could it matter later?")),
        q("choice", "Perfect recall or relief", "完全な記憶か安心", "Would you choose perfect recall or the ability to let painful memories fade?", "Would complete access to memory be worth losing the ability to let painful experiences soften?", "完全に覚えることと、つらい記憶を薄れさせることなら、どちらを選びますか？", ("What benefit decides it?", "What is valuable about the other ability?")),
        q("work-study", "Memory in learning", "学びと記憶", "How would perfect recall change learning or work?", "Which parts of study and work would improve—and which might become harder—with perfect recall?", "完全に覚えられたら、学習や仕事はどう変わりますか？", ("Would preparation time shrink?", "Could too much detail become distracting?")),
        q("all-vivid", "Every feeling stays vivid", "すべて鮮明", "Would you keep perfect recall if every embarrassment stayed vivid too?", "If trivial pain remained as vivid as valuable knowledge, would perfect recall still appeal?", "失敗や恥ずかしいことも鮮明に残るなら、完全な記憶を選びますか？", ("Would time make it easier?", "Which memory would be hardest to carry?")),
        q("lost-lesson", "When the lesson fades", "学びも薄れる", "Would your answer change if forgetting pain also weakened the lesson?", "If relief came with losing part of what the experience taught, would it remain worthwhile?", "つらさを忘れると学びも薄れるなら、選択は変わりますか？", ("How else could the lesson be kept?", "Could the same mistake happen again?")),
        q("switch", "A different kind of memory", "記憶の種類", "Which kind of memory would make you choose the other ability?", "What difference in usefulness, pain, or identity would reverse your choice?", "どんな記憶なら、反対の能力を選びますか？", ("Would ordinary details and major events differ?", "Would the answer change over time?")),
    ),
    120: (
        q("private-pride", "Private pride", "人に知られない誇り", "What can feel worth doing even when nobody knows?", "Which achievement keeps its value without recognition?", "誰にも知られなくても、価値があると感じることは何ですか？", ("Why does it matter privately?", "Would you ever tell someone?")),
        q("anonymous-help", "Anonymous help", "名前を出さない助け", "What good thing would you do without putting your name on it?", "Which contribution would be easier or better if it remained anonymous?", "名前を出さずによいことをするなら、何をしますか？", ("Who would benefit?", "Why might anonymity help?")),
        q("choice", "Wealth or respect", "富か尊敬", "Would you choose private wealth or respect on an ordinary income?", "Would financial freedom without recognition beat public respect without unusual wealth?", "裕福で無名の生活と、普通の収入で尊敬される生活のどちらを選びますか？", ("Which value decides it?", "What is attractive about the other life?")),
        q("daily-life", "An ordinary day", "普段の一日", "How would an ordinary day look in the life you chose?", "Which daily relationships and decisions would change under your chosen life?", "選んだ生活では、普段の一日はどのようになりますか？", ("Who would know you?", "How would money or reputation be managed?")),
        q("constant-rating", "Always being judged", "評価され続ける", "Would respect still appeal if people constantly judged you?", "How much public scrutiny would make respect feel like a burden?", "いつも人から評価されるなら、尊敬される生活を選びますか？", ("Which judgment would feel hardest?", "Could privacy be protected?")),
        q("family-knows", "Only family knows", "家族だけが知る", "Would your answer change if only your family knew about the wealth?", "If financial status stayed inside the family, would anonymity become easier to choose?", "家族だけが裕福だと知っているなら、選択は変わりますか？", ("How would family life change?", "What if friends found out?")),
        q("switch", "The price of visibility", "知られることの代償", "How much public attention would make you switch?", "At what level of exposure or insecurity would the other life become preferable?", "どの程度人に知られたら、反対の生活を選びますか？", ("Who knowing would matter most?", "Would the answer change for a fictional public figure?")),
    ),
    121: (
        q("recent-skill", "A skill that improved", "伸びた技能", "Which skill have you improved most recently?", "Which recent improvement came from the clearest practice and feedback?", "最近、いちばん伸びた技能は何ですか？", ("What kind of practice helped?", "What still feels difficult?")),
        q("three-skills", "A three-skill task", "三つの技能が必要な課題", "What task needs three different skills to go well?", "Which real task rewards breadth across several abilities?", "うまく行うために三つの技能が必要な課題は何ですか？", ("Which skill is hardest to replace?", "Could a team divide the work?")),
        q("choice", "Depth or breadth", "深さか広さ", "Would you master one skill or become good at many?", "Would exceptional depth in one field beat strong ability across several fields?", "一つの技能を極めるのと、多くの技能が得意になるのと、どちらを選びますか？", ("Which skill or group of skills do you imagine?", "What is the best part of the other path?")),
        q("one-year", "One year of practice", "一年の練習", "How would you use one year to build the ability you chose?", "What would a serious one-year learning plan prioritise under your chosen path?", "選んだ能力を伸ばすために、一年をどう使いますか？", ("How often would you practise?", "How would you measure progress?")),
        q("team", "Build a team", "チームを作る", "Would a team need more specialists or more generalists?", "Which mix of deep specialists and broad connectors makes a team resilient?", "チームには、専門家と幅広い技能を持つ人のどちらが多く必要ですか？", ("Who connects the specialists?", "Which role is hardest to hire?")),
        q("new-field", "A completely new field", "新しい分野", "Would you start broad or deep in a completely new field?", "When entering an unfamiliar field, how long should exploration continue before specialisation?", "まったく新しい分野なら、広く始めますか、深く始めますか？", ("What would you sample first?", "When would you commit to one area?")),
        q("switch", "A goal that changes the path", "進み方を変える目標", "Which goal would make you switch from depth to breadth, or the reverse?", "What change in task, team, or time horizon would reverse your learning strategy?", "どんな目標なら、深さと広さの選択を変えますか？", ("Would limited time favour one path?", "Would working alone change it?")),
    ),
}


_ORIGINAL_QUESTION_FOLLOWUPS = {
    number: {item["job"]: item["accessible_followups"] for item in items}
    for number, items in QUESTION_POOLS.items()
}


def _cq(job, title, title_ja, accessible, japanese, full=None):
    """Build a cold-open conversation prompt without adding language load."""
    return q(
        job, title, title_ja, accessible, accessible if full is None else full,
        japanese, (),
    )


# FT107 is the approved calibration pilot and stays byte-for-byte source
# equivalent.  The remaining pools use independent scenes and opinions rather
# than a sequence of references to "your choice" or "the other option."
QUESTION_POOLS.update({
    108: (
        _cq("slow-talk", "A long conversation", "長く話せる相手", "Who is easiest for you to talk to for hours?", "何時間でも話しやすい相手は誰ですか？"),
        _cq("crowd", "Meeting new people", "新しい人と会う", "What makes it easy to meet new people?", "新しい人と知り合いやすくするものは何ですか？"),
        _cq("choice", "Choose a circle", "人間関係を選ぶ", "For one difficult week, would you rather have a hundred friendly contacts or three close friends?", "大変な一週間なら、親しい知り合い百人と親友三人のどちらがよいですか？"),
        _cq("daily-life", "Many contacts, no close friend", "知り合いは多いが親友はいない", "What would be missing from life with many friendly contacts but no close friend?", "親しい知り合いは多くても親友がいない生活では、何が足りませんか？"),
        _cq("opposite", "A wide circle helps", "広い人間関係が役立つとき", "When is a wide circle more useful than a few close friends?", "少数の親友より、広い人間関係のほうが役立つのはどんなときですか？"),
        _cq("new-city", "Starting in a new city", "新しい町で始める", "After moving to a new city, would you build a wide circle or one close friendship first?", "新しい町へ移ったら、広い人間関係と一つの親しい友情のどちらを先に作りますか？"),
        _cq("change", "Help in a difficult week", "大変な週の助け", "During a difficult week, which helps more: small help from many people or steady help from one person?", "大変な一週間では、多くの人からの小さな助けと、一人からの続く助けのどちらが役立ちますか？"),
    ),
    109: (
        _cq("hard-day", "The harder weather", "より大変な天気", "Which is harder for you: a very hot day or a very cold day?", "とても暑い日ととても寒い日のどちらが大変ですか？"),
        _cq("perfect-day", "Perfect weather", "完璧な天気", "What would you do outside on a day with perfect weather?", "完璧な天気の日なら、外で何をしたいですか？"),
        _cq("choice", "One season forever", "一つの季節", "If one season had to last all year, would you choose summer or winter?", "一つの季節が一年中続くなら、夏と冬のどちらを選びますか？"),
        _cq("daily-life", "Summer every day", "毎日が夏", "Which daily habit would change most if summer never ended?", "夏が終わらなければ、どの日課が最も変わりますか？"),
        _cq("comfortable-home", "Perfect indoors", "家の中は快適", "If every indoor space were comfortable, which season would you choose?", "すべての室内が快適なら、どの季節を選びますか？"),
        _cq("daylight", "Warm and dark or cold and bright", "暖かく暗い日か寒く明るい日", "Would you rather have a warm dark day or a cold sunny day?", "暖かく暗い日と、寒く晴れた日のどちらがよいですか？"),
        _cq("switch", "Too much for a whole year", "一年中は無理な天気", "What's one weather condition you could not accept all year?", "一年中は受け入れられない天候を一つ挙げるとしたら何ですか？"),
    ),
    110: (
        _cq("clear-head", "Your clearest hour", "頭がさえる時間", "When does your mind usually feel clearest?", "頭がいちばんさえるのは、何時ごろですか？"),
        _cq("free-day", "No schedule tomorrow", "明日は予定なし", "When would you sleep and wake if tomorrow had no schedule?", "明日何も予定がなければ、何時に寝て起きますか？"),
        _cq("choice", "Early or late", "朝型か夜型", "For your most important tasks, would you rather start early or work late?", "最も大切な作業なら、早く始めるのと遅くまで取り組むのと、どちらがよいですか？"),
        _cq("whole-day", "Changing a routine", "日課を変える", "Which is hardest to change: sleep, meals, or social plans?", "睡眠、食事、人と会う予定のうち、最も変えにくいのはどれですか？"),
        _cq("housemate", "Opposite schedules", "反対の生活時間", "What rule helps two people with opposite sleep schedules share a home?", "睡眠時間が反対の二人が一緒に暮らすには、どんなルールが役立ちますか？"),
        _cq("no-morning-duty", "No morning duties", "朝の予定がない生活", "Would you become more of a night owl if you never had morning duties?", "朝の予定がまったくなければ、もっと夜型になりますか？"),
        _cq("switch", "A schedule that forces change", "変化を求める予定", "Which important responsibility can force someone to change their sleep schedule?", "どんな大切な責任が、睡眠時間を変えるきっかけになりますか？"),
    ),
    111: (
        _cq("surprise", "A good surprise", "よい予想外", "What kind of surprise can improve a trip?", "どんな予想外の出来事が、旅行をよくすることがありますか？"),
        _cq("first-decision", "The first decision", "最初の決定", "What would you decide first for a short trip tomorrow?", "明日短い旅行へ行くなら、最初に何を決めますか？"),
        _cq("choice", "Plan or decide later", "計画か現地で決めるか", "For a three-day trip, would you plan each day or decide as you go?", "三日間の旅行なら、毎日を計画するのと、その場で決めるのと、どちらがよいですか？"),
        _cq("month", "Too much planning", "計画しすぎる", "What can go wrong when every minute of a trip is planned?", "旅行の一分一分まで計画すると、何がうまくいかなくなることがありますか？"),
        _cq("hotel-only", "Only the room is booked", "宿だけ予約", "Would one hotel booking make you feel prepared for a week-long trip?", "一週間の旅行で宿だけ予約してあれば、準備できたと感じますか？"),
        _cq("different-partner", "Two travel styles", "二つの旅行スタイル", "Which two trip decisions should people agree on before travelling together?", "一緒に旅行する前に、どの二つのことを決めておくべきですか？"),
        _cq("switch", "A trip that needs a plan", "計画が必要な旅行", "What kind of trip needs a detailed plan?", "どんな旅行には詳しい計画が必要ですか？"),
    ),
    112: (
        _cq("alone-time", "The best part of solo travel", "一人旅のよさ", "What's the best part of travelling alone?", "一人旅の最もよいところは何ですか？"),
        _cq("share-view", "Share the view", "景色を共有", "Who would you want to share a beautiful view with?", "すてきな景色を、誰と共有したいですか？"),
        _cq("choice", "Alone or together", "一人か誰かと一緒か", "For a new destination, would you rather travel alone or with someone?", "初めての場所なら、一人と誰かとの旅行のどちらを選びますか？"),
        _cq("every-trip", "The hard part of company", "誰かとの旅行の難しさ", "What's the hardest part of travelling with other people?", "ほかの人と旅行する一番難しいところは何ですか？"),
        _cq("new-country", "Three days alone", "三日間一人", "Would you spend three days in a new country alone?", "初めての国で三日過ごすなら、一人で行きますか？"),
        _cq("planner", "Someone else plans", "ほかの人が計画", "How would a companion who planned everything change a trip?", "すべてを計画する同行者がいると、旅行はどう変わりますか？"),
        _cq("switch", "Better with company", "誰かと行くほうがよい場所", "What kind of destination is better with company?", "どんな旅先なら、誰かと一緒のほうがよいですか？"),
    ),
    113: (
        _cq("convenience", "A useful nearby service", "近くにほしいサービス", "Which nearby service matters most in everyday life?", "日常で、近くにあると最も助かるものは何ですか？"),
        _cq("window", "Outside your window", "窓の外", "What would you choose to see outside your window?", "窓の外に何が見えたらうれしいですか？"),
        _cq("choice", "City or quiet town", "都会か静かな町", "For daily life, would you rather live in a busy city or a quiet town?", "日常生活なら、にぎやかな都会と静かな町のどちらに住みたいですか？"),
        _cq("move", "What you would miss", "恋しくなるもの", "What would you miss first after moving from a city to the countryside?", "都会から田舎へ移ったら、最初に何が恋しくなりますか？"),
        _cq("no-car", "Living without a car", "車なしの生活", "Which place works better without a car: a city or the countryside?", "車なしで暮らすなら、都会と田舎のどちらがよいですか？"),
        _cq("small-town", "A well-equipped small town", "便利な小さな町", "Would a small town with a hospital and shops feel convenient enough?", "病院や店がある小さな町なら、十分便利に感じますか？"),
        _cq("switch", "Commute or quiet", "通勤か静けさ", "Which matters more: a short commute or a quiet home?", "短い通勤と静かな家のどちらが大切ですか？"),
    ),
    114: (
        _cq("outage", "One hour offline", "一時間オフライン", "What becomes difficult after one hour without internet?", "インターネットが一時間使えないと、最初に何が困りますか？"),
        _cq("cool-day", "A cool day offline", "涼しい日のオフライン", "How would you spend half a cool day without a phone?", "涼しい日にスマホなしで半日過ごすなら、何をしますか？"),
        _cq("choice", "Lose one for summer", "夏に一つを諦める", "For one summer, would you give up internet or air conditioning?", "一夏の間、インターネットとエアコンのどちらを諦めますか？"),
        _cq("first-problem", "One day without cooling", "冷房なしの一日", "What would be the first problem during one day without air conditioning?", "エアコンなしで一日過ごすと、最初に何が問題になりますか？"),
        _cq("cool-spring", "A cool spring day", "涼しい春の日", "On a cool spring day, would you rather lose internet or air conditioning?", "涼しい春の日なら、インターネットとエアコンのどちらを諦めますか？"),
        _cq("safe-place", "A nearby cool place", "近くの涼しい場所", "Would a safe, cool place nearby make a summer without air conditioning possible?", "近くに安全で涼しい場所があれば、エアコンなしの夏を過ごせますか？"),
        _cq("switch", "A need, not a comfort", "快適さではなく必要", "At what temperature does air conditioning become a need rather than a comfort?", "何度くらいから、エアコンは快適さではなく必要なものになりますか？"),
    ),
    115: (
        _cq("good-rest", "A restful day off", "休める休日", "What makes a day off feel genuinely restful?", "しっかり休めたと感じるには、何が必要ですか？"),
        _cq("protected-time", "Time you protect", "守りたい時間", "Which part of the day would you refuse to give up?", "一日の中で、必ず守りたい自分の時間はいつですか？"),
        _cq("choice", "Time or income", "時間か収入", "For the next year, would you choose more free time or a higher income?", "これから一年、自由な時間と高い収入のどちらを選びますか？"),
        _cq("only-one", "One extra free hour", "自由な時間を一時間", "What would improve first with one extra free hour every day?", "毎日自由な時間が一時間増えたら、最初に何がよくなりますか？"),
        _cq("nights-weekends", "High pay, fewer evenings", "高い給料と少ない夜時間", "Would high pay be worth often losing evenings and weekends?", "高い給料でも、夜や週末をよく失うなら受け入れますか？"),
        _cq("one-year", "One year only", "一年だけ", "Would a clear one-year limit make a demanding high-paid job easier to accept?", "大変でも高収入の仕事が一年だけなら、受け入れやすくなりますか？"),
        _cq("switch", "A new responsibility", "新しい責任", "Which new responsibility could make a higher salary more important?", "どんな新しい責任ができると、高い給料がより大切になりますか？"),
    ),
    116: (
        _cq("distraction", "At-home distraction", "家で気が散るもの", "What's the biggest distraction when working or studying at home?", "家で仕事や勉強をするとき、いちばん邪魔になるものは何ですか？"),
        _cq("commute-time", "No commute", "通勤なし", "How would you use the time saved by removing a commute?", "通勤時間がなくなったら、その時間をどう使いますか？"),
        _cq("choice", "Home or shared workplace", "家か共有の職場", "For focused work, would you choose home or a shared workplace?", "集中する仕事なら、家と共有の職場のどちらを選びますか？"),
        _cq("one-place", "The same place every day", "毎日同じ場所", "What's hardest about using the same place for work every day?", "毎日同じ場所で仕事をする一番難しいところは何ですか？"),
        _cq("quiet-office", "A quiet office nearby", "近くて静かな職場", "Would a quiet office fifteen minutes away be better than working at home?", "十五分の場所にある静かな職場は、在宅勤務よりよいですか？"),
        _cq("team-day", "Worth meeting in person", "会う価値のある作業", "Which task is worth meeting a team in person for?", "どんな作業なら、チームが直接会う価値がありますか？"),
        _cq("switch", "A better home setup", "よりよい在宅環境", "What feature would make home clearly better than an office?", "どんな特徴があれば、家のほうが職場より明らかによくなりますか？"),
    ),
    117: (
        _cq("best-focus", "A place for focus", "集中できる場所", "What makes a place easy to concentrate in?", "集中しやすい場所には、どんな特徴がありますか？"),
        _cq("one-hour", "One important hour", "大切な一時間", "Where would you sit to finish one important task in an hour?", "一時間で大切な作業を終えるなら、どこに座りますか？"),
        _cq("choice", "Café or home", "カフェか家", "For two hours of serious study, would you choose a café or home?", "二時間しっかり勉強するなら、カフェと家のどちらを選びますか？"),
        _cq("one-month", "The hard part of a café", "カフェの難しさ", "What's hardest about studying in a café?", "カフェで勉強する一番難しいところは何ですか？"),
        _cq("drink-cost", "Buying a drink", "飲み物を買う", "Would you keep using a quiet café if you had to buy a drink every time?", "静かなカフェでも毎回飲み物を買うなら、通い続けますか？"),
        _cq("home-desk", "A better home desk", "よりよい家の机", "Would a good desk and lighting at home make you stop using cafés?", "家に良い机と照明があれば、カフェを使わなくなりますか？"),
        _cq("switch", "A task for home", "家でする課題", "What kind of task is best done at home?", "どんな課題が、家でするのに最も合っていますか？"),
    ),
    118: (
        _cq("photo-match", "Trusting an online product", "オンライン商品への信頼", "What makes an online product feel trustworthy?", "オンラインの商品を信頼するには、何が必要ですか？"),
        _cq("urgent", "Needed today", "今日必要", "Where would you look first for something you needed today?", "今日必要な物なら、最初にどこを探しますか？"),
        _cq("choice", "Online or in a shop", "ネットか店頭", "For an important purchase, would you rather buy online or in a shop?", "大切な買い物なら、オンラインと店舗のどちらで買いますか？"),
        _cq("only-one", "If shops disappeared", "店がなくなったら", "What would you miss most if physical shops disappeared?", "実際の店がなくなったら、何が最も恋しくなりますか？"),
        _cq("cheap-return", "Cheaper but hard to return", "安いが返品困難", "Would you buy online if it were cheaper but hard to return?", "ネットのほうが安くても返品が難しいなら、買いますか？"),
        _cq("same-day", "Free delivery today", "当日無料配送", "Would free same-day delivery remove your reason to visit a shop?", "無料で当日に届くなら、店へ行く理由はなくなりますか？"),
        _cq("switch", "See it first", "先に実物を見る", "Which product would you never buy without seeing it in person?", "実物を見ずには絶対に買わない商品は何ですか？"),
    ),
    119: (
        _cq("photo-memory", "A memory from a photo", "写真で戻る記憶", "What kind of happy memory can a photograph bring back?", "写真を見ると、どんな楽しい記憶が戻ることがありますか？"),
        _cq("small-moment", "A small moment to keep", "残したい小さな出来事", "Which small ordinary moment is worth remembering for years?", "長く覚えていたい小さな出来事は何ですか？"),
        _cq("choice", "Perfect recall or relief", "完全な記憶か安心", "Would you rather remember every ordinary detail or be able to forget painful memories?", "普通の細部をすべて覚えることと、つらい記憶を忘れられることなら、どちらがよいですか？"),
        _cq("work-study", "What perfect memory makes easier", "完全な記憶で楽になること", "What would perfect memory make easier?", "完全な記憶があれば、何が楽になりますか？"),
        _cq("all-vivid", "Every embarrassment stays", "恥ずかしさも残る", "Would you want perfect memory if every embarrassment stayed vivid too?", "恥ずかしいことも鮮明に残るなら、完全な記憶がほしいですか？"),
        _cq("lost-lesson", "Forgetting pain and the lesson", "痛みと学びを忘れる", "Would forgetting pain be worth losing part of the lesson too?", "つらさを忘れる代わりに学びの一部も失うなら、その価値はありますか？"),
        _cq("switch", "A memory that can fade", "薄れてよい記憶", "Which kind of memory should be allowed to fade?", "どんな記憶は、薄れていってもよいですか？"),
    ),
    120: (
        _cq("private-pride", "Private pride", "人に知られない誇り", "What can feel worth doing even when nobody knows?", "誰にも知られなくても、価値があると感じることは何ですか？"),
        _cq("anonymous-help", "Anonymous help", "名前を出さない助け", "What good thing would you do without putting your name on it?", "名前を出さずによいことをするなら、何をしますか？"),
        _cq("choice", "Wealth or respect", "富か尊敬", "Would you rather be rich and unknown or respected on an average income?", "裕福で無名の生活と、平均的な収入で尊敬される生活のどちらがよいですか？"),
        _cq("daily-life", "Rich but unknown", "裕福だが無名", "What would an ordinary day look like if you were rich but nobody knew?", "裕福でも誰にも知られていなければ、普通の一日はどんな一日ですか？"),
        _cq("constant-rating", "Respected and judged", "尊敬と評価", "Would being respected still appeal if people constantly judged you?", "いつも人から評価されるなら、尊敬される生活は魅力的ですか？"),
        _cq("family-knows", "Respect from strangers", "知らない人からの尊敬", "Would public respect matter if the people closest to you did not admire you?", "親しい人に尊敬されなくても、世間からの尊敬は大切ですか？"),
        _cq("switch", "Privacy or recognition", "プライバシーか評価", "Which is harder to live without: privacy or recognition?", "プライバシーと人からの評価のうち、ないとより困るのはどちらですか？"),
    ),
    121: (
        _cq("recent-skill", "A skill you improved", "伸びた技能", "Which skill have you improved most recently?", "最近、いちばん伸びた技能は何ですか？"),
        _cq("three-skills", "A task that needs range", "幅広さが必要な課題", "What task needs three different skills to go well?", "うまく行うために三つの技能が必要な課題は何ですか？"),
        _cq("choice", "Depth or breadth", "深さか幅広さ", "Would you rather master one skill or become good at many?", "一つの技能を極めるのと、多くの技能が得意になるのと、どちらがよいですか？"),
        _cq("one-year", "One year to learn", "学ぶ一年", "With one year to learn, would you study one skill deeply or try five?", "学ぶ時間が一年あるなら、一つを深く学ぶのと五つを試すのと、どちらがよいですか？"),
        _cq("team", "A strong team", "強いチーム", "Does a strong team need more specialists or more generalists?", "強いチームには、専門家と幅広い技能を持つ人のどちらが多く必要ですか？"),
        _cq("new-field", "A new field", "新しい分野", "Would you explore widely or focus early in a completely new field?", "全く新しい分野なら、広く試すのと早く一つに集中するのと、どちらがよいですか？"),
        _cq("switch", "A goal that rewards range", "幅広さが役立つ目標", "Which goal rewards being good at many skills more than being great at one?", "一つを極めるより、多くの技能が得意なほうが役立つ目標は何ですか？"),
    ),
})

# Canonical openings for FT113 and FT120 are intentionally identical across
# levels. Give Full one additional plain-spoken angle so the pair still deepens
# the conversation without raising the register.
QUESTION_POOLS[113][3].update(
    full="Which part of city life would someone miss most after moving to a quiet town?",
    full_ja="静かな町へ引っ越したら、都会のどんな部分が最も恋しくなりますか？",
)
QUESTION_POOLS[120][5].update(
    full="Would respect from the public mean much if the people closest to you did not share it?",
    full_ja="世間から尊敬されても、身近な人が同じように思っていなければ、大きな意味がありますか？",
)

for _number in range(108, 122):
    for _item in QUESTION_POOLS[_number]:
        _item["accessible_followups"] = _ORIGINAL_QUESTION_FOLLOWUPS[_number][_item["job"]]

# A few jobs changed enough that their former probes no longer responded to
# the new printed answer.  Keep two distinct, answer-dependent moves.
_FOLLOWUP_REVISIONS = {
    (108, "change"): ("Why would that kind of help matter?", "When would the other kind of help be better?"),
    (111, "month"): ("Which part of the plan would feel restrictive?", "What would you deliberately leave open?"),
    (112, "every-trip"): ("Which difference between travellers causes the most friction?", "What could companions agree on before leaving?"),
    (112, "alone-time"): ("Which freedom matters most?", "What might feel lonely after a few days?"),
    (113, "move"): ("Which daily routine would become harder?", "What could a small town replace well?"),
    (115, "only-one"): ("How would you use the extra hour?", "Would one hour be enough to change the day?"),
    (117, "one-month"): ("Which café distraction is hardest to ignore?", "What makes the café worth using anyway?"),
    (120, "family-knows"): ("Whose respect matters most?", "Why might public respect still feel valuable?"),
    (113, "switch"): ("How much extra travel would you accept for a quieter home?", "When would convenience win?"),
    (116, "switch"): ("Why would that feature improve focus?", "What might an office still do better?"),
    (120, "switch"): ("Why is your choice hard to live without?", "When might the other need become more important?"),
}
for (_number, _job), _followups in _FOLLOWUP_REVISIONS.items():
    next(item for item in QUESTION_POOLS[_number] if item["job"] == _job)["accessible_followups"] = _followups


# Final spoken-question audit.  These overrides keep every page runnable from a
# cold open and make the probes respond to the learner's actual answer.
_FINAL_SEMANTIC_REPAIRS = {
    (108, "change"): {
        "title": "What a wide circle offers",
        "title_ja": "広い人間関係のよさ",
        "accessible": "What can a wide circle of friends offer that three close friends may not?",
        "full": "When can a wide circle be more useful than a small group of close friends?",
        "accessible_ja": "広い友人関係には、三人の親しい友人にはないどんなよさがありますか？",
        "full_ja": "広い友人関係が、少数の親しい友人より役立つのはどんなときですか？",
        "accessible_followups": ("Which situation makes that useful?", "What can a wide circle still fail to provide?"),
    },
    (110, "clear-head"): {
        "title": "Feeling ready to think",
        "title_ja": "考える準備が整うとき",
        "accessible": "What helps you feel awake and ready to think?",
        "full": "What usually helps your mind become clear and ready to work?",
        "accessible_ja": "頭が目覚めて、考える準備が整うには何が役立ちますか？",
        "full_ja": "頭がすっきりして作業の準備が整うには、普段何が役立ちますか？",
        "accessible_followups": ("Does light, food, movement, or quiet help most?", "What makes it harder?"),
    },
    (110, "whole-day"): {
        "accessible_followups": ("Why is that part hardest to move?", "Which small change could help?"),
    },
    (111, "surprise"): {
        "accessible_followups": ("Why can that surprise improve the trip?", "When would the same surprise be stressful?"),
    },
    (111, "different-partner"): {
        "accessible_followups": ("Which decision causes the most arguments?", "How could people compromise?"),
    },
    (111, "switch"): {
        "accessible_followups": ("What could go wrong without a plan?", "Which part could still stay flexible?"),
    },
    (112, "new-country"): {
        "title": "Enjoying time alone",
        "title_ja": "一人の時間を楽しむ",
        "accessible": "What would make three days alone in a new place enjoyable?",
        "full": "What would make three days alone somewhere new feel worthwhile?",
        "accessible_ja": "初めての場所で一人で過ごす三日間を、楽しくするものは何ですか？",
        "full_ja": "初めての場所で一人で過ごす三日間を、価値あるものにするのは何ですか？",
        "accessible_followups": ("Which part would you plan first?", "When might company still help?"),
    },
    (112, "switch"): {
        "accessible_followups": ("What makes company useful there?", "What kind of companion would fit?"),
    },
    (113, "switch"): {
        "title": "Services or quiet",
        "title_ja": "便利さか静けさ",
        "accessible": "Which matters more at home: easy access to services or peace and quiet?",
        "full": "For everyday life, which matters more: nearby services or a quiet home?",
        "accessible_ja": "暮らす場所では、便利なサービスへの行きやすさと静けさのどちらが大切ですか？",
        "full_ja": "日常生活では、近くの便利なサービスと静かな家のどちらが大切ですか？",
        "accessible_followups": ("Which service would you want nearby?", "What amount of noise would be too much?"),
    },
    (114, "cool-day"): {
        "accessible": "How would you spend half a cool day without internet?",
        "full": "How would you use half a cool day if the internet stopped working?",
        "accessible_ja": "涼しい日にインターネットなしで半日過ごすなら、何をしますか？",
        "full_ja": "涼しい日にインターネットが使えなくなったら、半日をどう過ごしますか？",
        "accessible_followups": ("Which offline activity would you choose?", "What online service would you miss first?"),
    },
    (114, "first-problem"): {
        "accessible_followups": ("Which daily routine would be affected first?", "What could make the day easier?"),
    },
    (114, "switch"): {
        "title": "A hard summer activity",
        "title_ja": "夏に大変な活動",
        "accessible": "Which summer activity is hardest without air conditioning?",
        "full": "Which part of an ordinary summer day becomes hardest without air conditioning?",
        "accessible_ja": "エアコンなしでは、夏のどんな活動が最も大変ですか？",
        "full_ja": "エアコンなしでは、夏の普通の一日のどの部分が最も大変になりますか？",
        "accessible_followups": ("What cooler place could help?", "What would make the problem less serious?"),
    },
    (117, "best-focus"): {
        "accessible_followups": ("Which feature helps you most?", "Which feature would distract you?"),
    },
    (117, "drink-cost"): {
        "accessible_followups": ("How often would the cost feel reasonable?", "What would make home the better choice?"),
    },
    (117, "switch"): {
        "accessible_followups": ("Why does home suit that task?", "What would improve the home setup?"),
    },
    (118, "photo-match"): {
        "accessible_followups": ("Which detail creates trust?", "What detail would make you doubt it?"),
    },
    (118, "only-one"): {
        "accessible_followups": ("Why would you miss that part?", "Could online shopping replace it at all?"),
    },
    (118, "switch"): {
        "accessible_followups": ("What do you need to check in person?", "What could make an online purchase safe enough?"),
    },
    (119, "lost-lesson"): {
        "title": "Letting a painful memory fade",
        "title_ja": "つらい記憶が薄れること",
        "accessible": "Would you rather remember a painful event less clearly or keep every detail?",
        "full": "Would you rather let a painful memory fade or keep every detail clear?",
        "accessible_ja": "つらい出来事を少し曖昧に覚えるのと、細部まですべて覚えるのと、どちらがよいですか？",
        "full_ja": "つらい記憶を薄れさせるのと、細部まではっきり残すのと、どちらがよいですか？",
        "accessible_followups": ("What could become easier if it faded?", "What might someone still want to remember?"),
    },
    (120, "anonymous-help"): {
        "title": "Helping without credit",
        "title_ja": "評価を求めない助け",
        "accessible": "When can doing something anonymously be better than receiving credit?",
        "full": "When can anonymous help matter more than public credit?",
        "accessible_ja": "名前を出さずに何かをするほうが、評価されるよりよいのはどんなときですか？",
        "full_ja": "名前を出さない助けが、人前で評価されることより大切なのはどんなときですか？",
        "accessible_followups": ("Who could benefit?", "What problem could anonymity avoid?"),
    },
    (120, "daily-life"): {
        "title": "Keeping wealth private",
        "title_ja": "富を秘密にする生活",
        "accessible": "What would an ordinary day look like if you were rich but kept your wealth private?",
        "full": "How might someone live differently if they were rich but kept their wealth private?",
        "accessible_ja": "裕福でもそのことを秘密にしていたら、普通の一日はどんな一日ですか？",
        "full_ja": "裕福でもそのことを秘密にしていたら、生活はどう変わるでしょうか？",
        "accessible_followups": ("Who, if anyone, would they tell?", "What would stay normal?"),
    },
    (121, "switch"): {
        "accessible_followups": ("Which different skills would the goal need?", "Where would deep expertise still help?"),
    },
}
for (_number, _job), _changes in _FINAL_SEMANTIC_REPAIRS.items():
    next(item for item in QUESTION_POOLS[_number] if item["job"] == _job).update(_changes)

_FINAL_REVIEW_REPAIRS = {
    (108, "slow-talk"): {
        "accessible": "Who, if anyone, is easy for you to talk to for hours?",
        "full": "Who, if anyone, can you talk to for hours without effort?",
        "accessible_ja": "何時間でも話しやすい相手がいるとしたら、誰ですか？",
        "full_ja": "無理なく何時間でも話せる相手がいるとしたら、誰ですか？",
        "accessible_followups": ("What makes a long conversation easy or difficult?", "Does knowing someone well matter?"),
    },
    (108, "change"): {
        "full": "How can a large social circle change the opportunities someone hears about?",
        "full_ja": "広い人間関係があると、知ることのできる機会はどう変わりますか？",
        "accessible_followups": ("Which opportunity is a good example?", "What kind of support still needs a close friend?"),
    },
    (110, "switch"): {
        "accessible_followups": ("Why could that responsibility change a schedule?", "What support might make the change easier?"),
    },
    (112, "share-view"): {
        "accessible": "Would you rather enjoy a beautiful view alone or share it with someone?",
        "full": "Would a beautiful view feel better alone or shared with someone?",
        "accessible_ja": "すてきな景色は、一人で楽しむのと誰かと共有するのと、どちらがよいですか？",
        "full_ja": "すてきな景色は、一人で見るのと誰かと共有するのと、どちらがよく感じられますか？",
        "accessible_followups": ("What is good about your choice?", "Would a photo change anything?"),
    },
    (113, "choice"): {
        "full_ja": "日常生活なら、にぎやかな都会と静かな町のどちらに住みたいですか？",
    },
    (113, "small-town"): {
        "accessible_followups": ("Which service might still be missing?", "How far would you be willing to travel for other needs?"),
    },
    (116, "one-place"): {
        "accessible": "Which part of a normal workday changes most between home and an office?",
        "full": "Which part of a workday changes most when someone moves between home and an office?",
        "accessible_ja": "家と職場では、普通の仕事日のどの部分が最も変わりますか？",
        "full_ja": "家と職場を行き来すると、仕事日のどの部分が最も変わりますか？",
        "accessible_followups": ("How does it change?", "Which place handles that part better?"),
    },
    (116, "quiet-office"): {
        "accessible_followups": ("Which part of the office would help most?", "What would still make home better?"),
    },
    (118, "same-day"): {
        "accessible_followups": ("Which products still need to be seen in person?", "Would expert help matter?"),
    },
    (120, "choice"): {
        "accessible_followups": ("Which part of that life matters most to you?", "What is attractive about the other life?"),
    },
    (120, "daily-life"): {
        "full": "How might you live differently if you were rich but kept your wealth private?",
        "full_ja": "裕福でもそのことを秘密にしていたら、生活はどう変わりますか？",
        "accessible_followups": ("Who, if anyone, would you tell?", "What would stay normal?"),
    },
}
for (_number, _job), _changes in _FINAL_REVIEW_REPAIRS.items():
    next(item for item in QUESTION_POOLS[_number] if item["job"] == _job).update(_changes)

# Final spoken-language pass.  These repairs remove the remaining hidden or
# abstract setups.  Every follow-up pair ends with a concrete question that
# still works after "I don't know", "none", or no matching experience.
_THREE_SECOND_MAIN_REPAIRS = {
    (109, "perfect-day"): {
        "full": "How would you spend a full day outside in perfect weather?",
        "full_ja": "完璧な天気の日を丸一日外で過ごすなら、何をしますか？",
    },
    (107, "first-change"): {
        "accessible": "What everyday cost could fifty extra dollars help with this month?",
        "full": "Which everyday cost could fifty extra dollars help cover this month?",
        "accessible_ja": "今月、追加の五十ドルでどんな日常の支出を助けられますか？",
        "full_ja": "今月、追加の五十ドルでどの日常の支出を補えますか？",
    },
    (107, "future"): {
        "accessible": "When might someone choose extra time even if money was tight?",
        "full": "When might someone protect free time even while money was tight?",
        "accessible_ja": "お金に余裕がなくても、どんなときに時間を選ぶでしょうか？",
        "full_ja": "お金に余裕がなくても、どんなときに自由な時間を守るでしょうか？",
    },
    (110, "no-morning-duty"): {
        "accessible": "Would you stay up later if you never had morning duties?",
        "full": "Would you stay up later if nothing required you to wake early?",
        "accessible_ja": "朝の用事がまったくなければ、もっと夜更かししますか？",
        "full_ja": "早起きする必要が何もなければ、もっと夜更かししますか？",
    },
    (111, "different-partner"): {
        "accessible": "Which trip decision should people agree on before travelling together?",
        "full": "Which trip decision should people settle before travelling together?",
        "accessible_ja": "一緒に旅行する前に、どの旅行の決め事に合意しておくべきですか？",
        "full_ja": "一緒に旅行する前に、どの旅行の決め事を決めておくべきですか？",
    },
    (115, "switch"): {
        "accessible": "Would caring for someone or facing a large bill make higher pay more important?",
        "full": "Would care duties or a large bill make higher pay more important?",
        "accessible_ja": "誰かのケアや大きな支払いが必要になったら、より高い給料が重要になりますか？",
        "full_ja": "ケアの責任や大きな支払いがあれば、より高い給料が重要になりますか？",
    },
    (118, "urgent"): {
        "accessible": "If you needed a phone charger today, would you look online or in a shop first?",
        "full": "If you needed a phone charger today, would you check online or visit a shop first?",
        "accessible_ja": "今日スマートフォンの充電器が必要なら、まずオンラインと店のどちらで探しますか？",
        "full_ja": "今日スマートフォンの充電器が必要なら、まずオンラインで確認しますか、それとも店へ行きますか？",
    },
    (117, "one-hour"): {
        "full": "Where would you work to finish one difficult task in an hour?",
        "full_ja": "難しい作業を一時間で終えるなら、どこで取り組みますか？",
    },
    (120, "anonymous-help"): {
        "accessible": "What's one good reason to help someone anonymously?",
        "full": "What's one good reason to help someone without taking public credit?",
        "accessible_ja": "名前を出さずに誰かを助けるよい理由は何ですか？",
        "full_ja": "人前で評価を受けずに誰かを助けるよい理由は何ですか？",
    },
    (120, "family-knows"): {
        "full": "Would public respect matter if the people closest to you did not respect you?",
        "full_ja": "最も近い人たちに尊敬されていなければ、世間からの尊敬は大切ですか？",
    },
    (121, "three-skills"): {
        "accessible": "What skills do you need to plan a good trip?",
        "full": "Which skills matter most when planning a complicated trip?",
        "accessible_ja": "よい旅行を計画するには、どんな技能が必要ですか？",
        "full_ja": "複雑な旅行を計画するとき、どんな技能が最も重要ですか？",
    },
    (121, "switch"): {
        "accessible": "When is being good at several skills better than mastering one?",
        "full": "When is being good at several skills more useful than mastering one?",
        "accessible_ja": "複数の技能が得意なことは、どんなときに一つを極めるよりよいですか？",
        "full_ja": "複数の技能が得意なことは、どんなときに一つを極めるより役立ちますか？",
    },
}
for (_number, _job), _changes in _THREE_SECOND_MAIN_REPAIRS.items():
    next(item for item in QUESTION_POOLS[_number] if item["job"] == _job).update(_changes)

_THREE_SECOND_FOLLOWUPS = {
    107: {
        "saved-time": ("What did the slower option save money on?", "Which usually costs less: walking or public transport?"),
        "free-hours": ("What would you do first?", "Which sounds better today: rest, errands, or fun?"),
        "choice": ("What would your choice help you do?", "Which disappears faster in a busy week: money or free time?"),
        "first-change": ("How urgent would that cost be?", "What's one everyday expense that often surprises people?"),
        "opposite": ("How would the extra time help?", "Which helps more after a tiring week: extra time or extra money?"),
        "ten-hours": ("What would those ten hours replace?", "Would you give up one evening a week for higher pay?"),
        "future": ("What would the extra time protect?", "Which would you protect first: sleep or income?"),
    },
    108: {
        "slow-talk": ("What makes a long conversation easy or difficult?", "Is a long conversation easier in person or on the phone?"),
        "crowd": ("What opening question works well?", "Where is it easier to meet people: a class, a party, or online?"),
        "choice": ("What kind of support would your choice provide?", "Who helps more in a crisis: close friends or many contacts?"),
        "daily-life": ("Which kind of interaction would disappear?", "Would you share good news with one close friend or a large group first?"),
        "opposite": ("What kind of support would a wide circle provide?", "Which helps more when job hunting: close friends or many contacts?"),
        "new-city": ("How would you meet people?", "Where would you start: work, a class, or a hobby group?"),
        "change": ("Which opportunity is a good example?", "Which brings more new information: one close friend or many contacts?"),
    },
    109: {
        "hard-day": ("Does travel make that weather harder?", "Which bothers you more: strong sun or cold wind?"),
        "perfect-day": ("Which outdoor place would you visit?", "Would you choose a park, a beach, or a city walk?"),
        "choice": ("Which activity shapes your answer?", "Which would be harder all year: heat or short winter days?"),
        "daily-life": ("How would outdoor plans change?", "Which changes more with summer: sleep or clothing?"),
        "comfortable-home": ("Would daylight still matter?", "Would you rather go outside in rain or snow?"),
        "daylight": ("Does light affect your mood?", "Which helps your mood more: warmth or sunlight?"),
        "switch": ("How long could you accept that weather?", "Which is harder to live with: humidity or ice?"),
    },
    110: {
        "clear-head": ("What makes it harder to feel alert?", "Which wakes you up faster: light, food, or movement?"),
        "free-day": ("How much sleep would that give you?", "Would you sleep later on a completely free day?"),
        "choice": ("When would you do your hardest work?", "Which is quieter for you: early morning or late night?"),
        "whole-day": ("Why is that part hardest to move?", "Which is easiest to move: a meal or a bedtime?"),
        "housemate": ("When would the home need to be quiet?", "Would you set quiet hours at night or in the morning?"),
        "no-morning-duty": ("Could staying up late affect your health?", "Would you still wake early on weekends?"),
        "switch": ("Why could that responsibility change a schedule?", "Which changes sleep faster: a new job or a new baby?"),
    },
    111: {
        "surprise": ("When would the same surprise be stressful?", "Would unexpected rain ruin a trip or make it memorable?"),
        "first-decision": ("What could stay open?", "Which would you book first: transport or a place to stay?"),
        "choice": ("What would you leave undecided?", "Which is worse: missing a booking or missing a surprise?"),
        "month": ("Which part of the plan would feel restrictive?", "Would you enjoy a trip with every meal booked?"),
        "hotel-only": ("What would you do on the first day?", "Would you feel calmer with transport booked too?"),
        "different-partner": ("How could people compromise?", "Which causes more arguments: money or timing?"),
        "switch": ("What could go wrong without a plan?", "Which needs more planning: a beach weekend or an international trip?"),
    },
    112: {
        "alone-time": ("Which freedom matters most?", "Would you enjoy one day alone in a new city?"),
        "share-view": ("What is good about your choice?", "Would you send someone a photo right away?"),
        "choice": ("Who would be the ideal companion?", "Which is easier with company: safety or decision-making?"),
        "every-trip": ("What could companions agree on before leaving?", "Which causes more conflict: money, food, or timing?"),
        "new-country": ("When might company still help?", "Would knowing the local language make solo travel easier?"),
        "planner": ("What would you still decide yourself?", "Would you let a close friend plan the whole weekend?"),
        "switch": ("What makes company useful there?", "Which feels safer with company: a city or a remote area?"),
    },
    113: {
        "convenience": ("How often would you use that service?", "Which would you want within walking distance: a supermarket or a train station?"),
        "window": ("Would you accept a longer commute for that view?", "Would you rather see trees or city lights?"),
        "choice": ("What would you use most in your chosen place?", "Which would you miss more: quiet or convenience?"),
        "move": ("Which daily routine would become harder?", "Which is harder without a car: shopping or seeing friends?"),
        "no-car": ("How would you buy food?", "Could you live comfortably without a car where you are?"),
        "small-town": ("Which service might still be missing?", "Which matters more nearby: a hospital or a train station?"),
        "switch": ("Which service would you want nearby?", "Would you accept more noise to live near a station?"),
    },
    114: {
        "outage": ("What could still be done offline?", "Which would you miss first: messages, maps, or payments?"),
        "cool-day": ("Which offline activity would you choose?", "Would you choose a walk, a book, or a movie?"),
        "choice": ("Would work, health, or family needs matter most?", "Which is more essential in hot weather: cooling or online access?"),
        "first-problem": ("What could make the day easier?", "Which suffers first in heat: sleep or concentration?"),
        "cool-spring": ("What would you do offline?", "Would you still need air conditioning on a cool day?"),
        "safe-place": ("Would the safe place need to open at night?", "Would a nearby library make the summer easier?"),
        "switch": ("What cooler place could help?", "Which is harder without cooling: sleeping or working?"),
    },
    115: {
        "good-rest": ("What would you stop doing on a restful day?", "Would you rather rest alone or spend time with people?"),
        "protected-time": ("How could you protect that time?", "Which would you protect first: sleep or social time?"),
        "choice": ("Which need is more urgent?", "What makes a week feel too busy?"),
        "only-one": ("How would the extra hour help?", "Would you use the extra hour for sleep, exercise, or family?"),
        "nights-weekends": ("Which commitment could not be sacrificed?", "Would losing every weekend be too much?"),
        "one-year": ("What would the year need to achieve?", "Would you accept the job for three months instead of a year?"),
        "switch": ("Would the higher pay be needed for long?", "Which cost could make higher pay urgent: rent, health care, or family care?"),
    },
    116: {
        "distraction": ("How could the space be changed?", "Which distracts more at home: noise, chores, or your phone?"),
        "commute-time": ("Would you use the time the same way every day?", "Would you use the saved commute time for rest, exercise, or something social?"),
        "choice": ("What kind of work are you imagining?", "Which is quieter for you: home or a workplace?"),
        "one-place": ("Does that part become easier or harder at home?", "Which changes more: focus or communication?"),
        "quiet-office": ("Which part of the office would help most?", "Would a short commute make the office more attractive?"),
        "team-day": ("What should happen that day?", "Which is easier in person: planning or solving a disagreement?"),
        "switch": ("Why would that feature improve focus?", "Would a private room make home clearly better?"),
    },
    117: {
        "best-focus": ("Which feature helps you most?", "Which helps more: silence or a little background noise?"),
        "one-hour": ("What important task would you choose?", "Would you choose a desk at home or a quiet cafe?"),
        "choice": ("What would you bring?", "Which place has fewer distractions for you?"),
        "one-month": ("What makes the cafe worth using anyway?", "Which cafe noise is hardest to ignore: music or conversations?"),
        "drink-cost": ("How often would the cost feel reasonable?", "Would one drink per visit feel reasonable?"),
        "home-desk": ("What else would the room need?", "Would you still visit a cafe for a change of mood?"),
        "switch": ("Why does home suit that task?", "Which needs more privacy: writing or a video call?"),
    },
    118: {
        "photo-match": ("Which detail creates trust?", "Which do you trust more: customer photos or star ratings?"),
        "urgent": ("Would price or certainty matter more?", "Would you pay more for the charger today?"),
        "choice": ("Which product are you imagining?", "Which would you inspect first: shoes or a phone?"),
        "only-one": ("Why would you miss that part?", "Which would you miss more: trying things on or asking staff?"),
        "cheap-return": ("What would you check first?", "Would you take the risk for a very cheap item?"),
        "same-day": ("Would expert help still matter?", "Would you still visit a shop to try on clothes?"),
        "switch": ("What do you need to check in person?", "Which is riskier online: clothes or electronics?"),
    },
    119: {
        "photo-memory": ("Which detail returns first?", "Which brings back more: a photo or a song?"),
        "small-moment": ("Why could that ordinary moment matter later?", "Would you record an ordinary day in a diary?"),
        "choice": ("How would your choice help in daily life?", "Would you rather keep a diary or delete one embarrassing photo?"),
        "work-study": ("Could too much detail become distracting?", "Would perfect memory help more at work or while studying?"),
        "all-vivid": ("Would embarrassing memories get easier with time?", "Would you want every embarrassing moment to stay clear?"),
        "lost-lesson": ("What could become easier if the painful memory faded?", "Can a photograph keep the facts without keeping every feeling?"),
        "switch": ("Would the answer change over time?", "Should an embarrassing memory fade faster than a happy one?"),
    },
    120: {
        "private-pride": ("Why is it worth doing without praise?", "Which feels better: private pride or public praise?"),
        "anonymous-help": ("Who could benefit?", "Would you donate anonymously if you could?"),
        "choice": ("Which part of that life matters most to you?", "Would you prefer a quiet day alone or being thanked in public?"),
        "daily-life": ("What would stay normal?", "Would you tell one close person about the money?"),
        "constant-rating": ("Which judgment would feel hardest?", "Would public respect be worth losing some privacy?"),
        "family-knows": ("Why might public respect still feel valuable?", "Which matters more: respect from family or from strangers?"),
        "switch": ("Why is that hard to live without?", "Would you leave social media for a month to protect your privacy?"),
    },
    121: {
        "recent-skill": ("What kind of practice helped?", "Which is easier to improve: cooking, exercise, or language?"),
        "three-skills": ("Which skill is hardest to replace?", "Which part is hardest: choosing a place, budgeting, or organizing?"),
        "choice": ("Which skill or group of skills do you imagine?", "What skill would you happily practise every week for a year?"),
        "one-year": ("How would you measure progress?", "Would you rather practise daily or try something new each week?"),
        "team": ("Who would connect the specialists?", "Would you rather hire one expert or three flexible people?"),
        "new-field": ("What would you sample first?", "Would you try several topics before choosing one?"),
        "switch": ("Where would deep expertise still help?", "When is broad knowledge more useful: planning or fixing one technical problem?"),
    },
}
for _number, _rows in _THREE_SECOND_FOLLOWUPS.items():
    for _job, _followups in _rows.items():
        next(item for item in QUESTION_POOLS[_number] if item["job"] == _job).update(
            accessible_followups=_followups,
        )
