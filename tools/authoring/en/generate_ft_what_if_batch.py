#!/usr/bin/env python3
"""Source specification for the paired FT 89-100 What If batch.

Importing this module is deliberately inert: it reads neither the protected FT-1
pilots nor any shared-runtime file.  Rendering remains available behind lazy
functions for the later, separately authorized render phase.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


COURSE = "talk-what-if"
TOPIC_NUMBERS = tuple(range(89, 101))
VARIANTS = ("accessible", "full")
TOPIC_FORMAT = {
    89: "story", 90: "choose", 91: "story", 92: "choose",
    93: "choose", 94: "choose", 95: "story", 96: "story",
    97: "story", 98: "story", 99: "story", 100: "choose",
}
SHARED_SOURCE = {number: (f"KR 9-{number - 88}" if number < 100 else "NEW → KR") for number in TOPIC_NUMBERS}

BRIEF_OPENINGS = {
    89: "Imagine you win a large lottery prize tomorrow. What would you do first?",
    90: "Which three useful objects would you take to a desert island?",
    91: "Whose daily life would you be curious to experience for one day?",
    92: "Which superpower would make ordinary life most interesting?",
    93: "Which food would be hardest for you to get tired of?",
    94: "If one everyday service were free for life, which would you choose?",
    95: "Which part of a week with no optional phone use would be hardest?",
    96: "If AI handled all your usual tasks, how would you use the free time?",
    97: "Which animal best represents your personality?",
    98: "Which country would offer the most interesting different upbringing?",
    99: "What would an ideal ordinary day look like ten years from now?",
    100: "Once everyone is safe, which possession would be hardest to lose?",
}

# The English condition and its Japanese interpretation are authored together.
# These contracts prevent a renderer or later edit from silently changing the
# kind of hypothetical (ability, counterfactual, reported guess, or projection).
MODAL_CONTRACT = {
    89: ("unexpected win; would, not a prediction", "もし大当たりしたら、実際に何をするか"),
    90: ("hypothetical choice; would take", "無人島に持っていくなら"),
    91: ("counterfactual exchange; would trade lives", "一日だけ人生を入れ替えるなら"),
    92: ("hypothetical choice and consequence", "超能力を選べるなら"),
    93: ("imagined ability; could eat, not medical ability", "もし一つの食べ物だけを食べ続けるなら。get sick of は病気ではなく飽きる"),
    94: ("counterfactual free access; would use", "もし一つを一生無料にできるなら"),
    95: ("practical ability; could manage seven days", "携帯電話なしで七日間過ごせるか"),
    96: ("AI does the paid task while salary remains; not job loss", "AIが仕事をしても同じ給料を受け取るなら"),
    97: ("reported hypothetical guess; people would choose", "自分を知る人ならどの動物を選びそうか"),
    98: ("counterfactual upbringing", "もし別の国で育っていたら"),
    99: ("future projection, not a promise", "十年後を想像すると"),
    100: ("safe hypothetical removal; would carry out", "安全に持ち出すなら"),
}

# Safety is part of the source model rather than an improvised tutor warning.
SCENARIO_GUARDS = {
    89: "No ticket, current job, purchase, disclosure, or future regret is assumed.",
    90: "No possession, near-pick, useless object, regret, or companion is assumed.",
    91: "A public, fictional, anonymous, or no-person answer is valid; private facts are never required.",
    92: "No easy choice is required; none, a downside, or a refused power remains valid.",
    93: "Allergy, religion, health, appetite, and eating-discomfort boundaries override the game without explanation.",
    94: "No current use, resale plan, legal assumption, or personal spending disclosure is required.",
    95: "Essential access, disability, care, safety, and work needs are valid; never frame phone use as addiction or failure.",
    96: "No paid role is assumed: study, care, unpaid work, or a general hypothetical are valid; this is not a job-loss forecast.",
    97: "No friends are assumed; familiar or public observers work, and the tutor supplies real traits before being classified.",
    98: "Do not assume Japan, migration, a visa, health details, or national stereotypes.",
    99: "No clear vision, companion, fixed plan, or immediate action is assumed.",
    100: "Every person and pet is already safe; leaving immediately is valid; nobody re-enters a fire.",
}

TOC_RETRIEVAL = {
    89: (("The first thing I'd do is ___.", ("CORE-66",), False), ("I probably wouldn't ___.", ("CORE-66",), False)),
    90: (("I'd take ___, ___ and ___.", ("CORE-66",), False), ("I'd regret leaving ___.", ("CORE-71",), False)),
    91: (("I'd want to be ___ for a day.", ("CORE-66",), False), ("Mainly to find out ___.", ("CORE-62",), False)),
    92: (("I'd go with ___.", ("CORE-66",), False), ("The problem would be ___.", ("CORE-98",), True)),
    93: (("I could live on ___.", ("CORE-66",), False), ("I'd get sick of ___ eventually.", ("CORE-66",), False)),
    94: (("I'd choose ___, easily.", ("CORE-46",), False), ("I'd use it more than ___.", ("CORE-45",), False)),
    95: (("I'd last about ___.", ("CORE-51",), True), ("The hardest part would be ___.", ("CORE-103",), True)),
    96: (("At first I'd ___.", ("CORE-66",), False), ("After a month I'd probably ___.", ("CORE-66",), False)),
    97: (("People would probably say ___.", ("CORE-66",), False), ("I'd rather be ___.", ("CORE-97",), False)),
    98: (("I'd want to grow up in ___.", ("CORE-66",), False), ("I'd probably be ___.", ("CORE-66",), False)),
    99: (("I'd like to be ___ing.", ("CORE-66",), False), ("As long as ___, I'd be happy.", (), True)),
    100: (("I'd grab ___.", ("CORE-66",), False), ("Everything else can be replaced.", ("CORE-65",), False)),
}
TOC_RETRIEVAL_AUDIT_ONLY = True


def prompt(job, title, title_ja, accessible, accessible_ja, accessible_followups, *, full, full_ja, full_followups, safety):
    return {
        "job": job, "title": title, "title_ja": title_ja,
        "accessible": accessible, "accessible_ja": accessible_ja,
        "accessible_followups": tuple(accessible_followups),
        "full": full, "full_ja": full_ja,
        "full_followups": tuple(full_followups), "safety": safety,
    }


def topic(*, slug, title, ko, ja, goal, article_title, articles, prompts):
    return locals()


# Each claim is (accessible EN, full EN, accessible JA, full JA).
TOPICS = {
    89: topic(
        slug="what-you-would-really-do-if-you-won-the-lottery",
        title="What you would really do if you won the lottery",
        ko="복권에 당첨되면 실제로 할 일",
        ja="宝くじに当たったら本当にすること",
        goal=("Let's imagine an unexpected jackpot and what would actually change.", "突然大当たりしたとき、実際に何が変わるかを想像しましょう。"),
        article_title=("What a sudden win reveals", "突然の大当たりで見えること"),
        articles=[
            ("A jackpot creates choices before it creates a plan.", "A sudden jackpot creates immediate choices long before it provides a sensible plan.", "大当たりすると、計画ができる前に多くの選択が生まれます。", "突然の大当たりは、現実的な計画を与えるより先に、すぐ決めるべき選択を生みます。"),
            ("The first action often shows what feels urgent now.", "The first imagined action often exposes what currently feels most urgent.", "最初にすることには、今いちばん急いで解決したいことが表れます。", "最初に思い浮かぶ行動には、今もっとも切迫していることが表れやすいです。"),
            ("Some people would tell others; some would stay quiet.", "Some people would share the news immediately, while others would protect their privacy.", "すぐ誰かに話す人もいれば、黙っている人もいます。", "すぐ知らせる人もいれば、自分のプライバシーを守ろうとする人もいます。"),
            ("More money does not decide whether work still matters.", "Financial freedom does not automatically settle whether paid or unpaid work still gives life structure.", "お金が増えても、仕事がまだ大切かどうかは自動的には決まりません。", "経済的に自由になっても、有給・無給の仕事が生活に必要な形を与えるかは自動的には決まりません。"),
            ("Buying something first is only one possible answer.", "A first purchase is only one response; waiting, helping, or changing nothing are equally possible.", "最初に何かを買うことだけが答えではありません。", "最初に買うだけでなく、待つ、誰かを助ける、何も変えないという答えもあります。"),
            ("A fast decision can feel different after the excitement fades.", "A decision made during the initial excitement may look different once the shock has passed.", "興奮が落ち着くと、急いで決めたことの見え方が変わる場合があります。", "最初の興奮の中で決めたことは、衝撃が過ぎると違って見えることがあります。"),
            ("Not everyone would regret the same kind of choice.", "Regret may come from acting too quickly, waiting too long, or not changing anything at all.", "何を後悔するかは人によって違います。", "急ぎすぎたこと、待ちすぎたこと、何も変えなかったことのどれも後悔になり得ます。"),
            ("A new normal could arrive quickly or take years.", "The unfamiliar life might become ordinary within weeks, or remain unsettled for years.", "新しい生活がすぐ普通になる人も、何年も落ち着かない人もいます。", "慣れない生活が数週間で日常になる場合も、何年も安定しない場合もあります。"),
            ("Money can remove limits without choosing a direction.", "Money can remove practical limits without supplying purpose, trust, or direction.", "お金は制限を減らせても、進む方向までは選んでくれません。", "お金は現実的な制約を減らせますが、目的や信頼、進む方向までは与えません。"),
            ("The useful question is what kind of life the win should support.", "The deeper question is which life the money should make possible rather than which object it should buy.", "大切なのは、そのお金でどんな生活を支えたいかという問いです。", "本質的なのは、何を買うかではなく、そのお金でどんな人生を可能にしたいかという問いです。"),
        ],
        prompts=[
            prompt("opening", "The first move", "最初の行動", BRIEF_OPENINGS[89], "明日大当たりします。実際に最初に何をしますか？", ("If no action comes immediately, what would you deliberately avoid doing?", "What makes that the safest first move?"), full=BRIEF_OPENINGS[89], full_ja="明日大当たりします。実際に最初に何をしますか？", full_followups=("If no immediate action comes to mind, what would you deliberately postpone?", "Which concern makes that the most sensible first move?"), safety="no-ticket-or-action-required"),
            prompt("reason", "Why first", "それを最初にする理由", "Why would that come first?", "なぜそれを最初にしますか？", ("Which problem or hope would it address?", "If your first move were to wait, what would you wait for?"), full="Why would that action take priority?", full_ja="なぜその行動を最優先にしますか？", full_followups=("Which immediate need or value would it serve?", "If waiting took priority, what information would you want first?"), safety="action-or-waiting"),
            prompt("disclosure", "Who knows", "誰に知らせるか", "Would you tell anyone about the jackpot?", "大当たりしたことを誰かに話しますか？", ("If yes, who would need to know first?", "If no, what would privacy protect?"), full="Would you disclose the jackpot to anyone?", full_ja="大当たりしたことを誰かに知らせますか？", full_followups=("If so, who would have a legitimate reason to know first?", "If not, which risk would privacy reduce?"), safety="tell-someone-or-no-one"),
            prompt("work", "Work after the win", "当選後の仕事", "Would you keep your current work, study, care, or routine?", "今の仕事、勉強、ケア、または日課を続けますか？", ("If there is no current role, what routine would you want?", "What would you keep even without financial pressure?"), full="Which parts of your current paid work, study, care, or routine would you keep?", full_ja="今の有給の仕事、勉強、ケア、または日課のどの部分を続けますか？", full_followups=("If no current role applies, which structure would you create?", "What would remain meaningful without financial pressure?"), safety="paid-unpaid-study-care-or-none"),
            prompt("purchase", "Buying or not buying", "買うか買わないか", "What, if anything, would you buy first?", "最初に買うものがあるとすれば、何ですか？", ("If you would buy something, what would change after it?", "If nothing, where would the money go first?"), full="What, if anything, would become your first purchase?", full_ja="最初の買い物になるものがあるとすれば、何ですか？", full_followups=("If there is a purchase, which part of life would it change?", "If there is none, which non-purchase use would come first?"), safety="purchase-or-no-purchase"),
            prompt("regret", "A possible regret", "後悔する可能性", "What choice might you regret—or do you expect no regret?", "どんな選択を後悔しそうですか。それとも、後悔しないと思いますか？", ("If a regret seems possible, what would cause it?", "If none does, what would keep the decision sound?"), full="Which choice could produce regret, if any?", full_ja="後悔につながる選択があるとすれば、どれですか？", full_followups=("If regret is possible, which later consequence would create it?", "If not, which principle would keep the decision defensible?"), safety="regret-or-no-regret"),
            prompt("normal", "A new normal", "新しい日常", "Would life feel different after the jackpot, or would you keep it mostly the same?", "大当たりのあと、生活は変わったと感じますか。それとも、ほとんど変えませんか？", ("If life changed, what would become ordinary first?", "If little changed, what would you deliberately keep the same?"), full="Would the jackpot create a different normal, or would you preserve most of your current life?", full_ja="大当たりで新しい日常が生まれますか。それとも、今の生活の大部分を保ちますか？", full_followups=("If life changed, which unfamiliar part would become routine first?", "If little changed, which part would you intentionally preserve?"), safety="changed-or-mostly-unchanged"),
            prompt("flip", "What money cannot choose", "お金では決められないこと", "What important part of life would the jackpot not solve?", "大当たりしても解決できない大切なことは何ですか？", ("What would that still require?", "Could the money make it easier without solving it?"), full="Which important part of life would remain unresolved by the jackpot?", full_ja="大当たりしても解決されない大切なことは何ですか？", full_followups=("What non-financial resource would it still require?", "Could money reduce the difficulty without resolving it?"), safety="non-financial-close"),
        ],
    ),
    90: topic(
        slug="three-things-you-would-take-to-a-desert-island", title="Three things you would take to a desert island", ko="무인도에 가져갈 세 가지", ja="無人島に持っていく三つの物",
        goal=("Let's choose three objects and test what is truly essential.", "三つの物を選び、本当に必要なものを考えましょう。"), article_title=("What makes an item essential", "物を必需品にするもの"),
        articles=[
            ("A desert-island list forces many needs into three objects.", "A desert-island list compresses survival, comfort, and identity into only three objects.", "無人島のリストでは、多くの必要を三つの物に絞ります。", "無人島のリストでは、生存、快適さ、自分らしさを三つの物に絞り込みます。"),
            ("An essential item solves a problem that cannot wait.", "An essential item addresses a need whose delay would carry a serious cost.", "必需品は、待てない問題を解決する物です。", "必需品とは、先延ばしにすると重大な結果が出る必要を満たす物です。"),
            ("Useful equipment may matter more than a favourite possession.", "Practical equipment can outrank a treasured possession when conditions are harsh.", "厳しい環境では、お気に入りの物より役立つ道具が大切かもしれません。", "厳しい状況では、大切な持ち物より実用的な道具が優先されることがあります。"),
            ("Comfort still matters because people need rest and hope.", "Comfort is not automatically frivolous; rest and hope can support endurance.", "休息や希望が必要なので、快適さも大切です。", "快適さは必ずしも無駄ではなく、休息や希望が耐える力を支えます。"),
            ("One object can sometimes do several jobs.", "A versatile object earns its place by meeting several different needs.", "一つの物がいくつもの役割を果たすこともあります。", "多用途の物は、複数の必要を満たすことで選ぶ価値が高まります。"),
            ("A nearly chosen object shows what the list leaves out.", "The object that almost made the list reveals which need was sacrificed.", "選びかけた物から、何を諦めたかが分かります。", "最後に外した物は、どの必要を犠牲にしたかを示します。"),
            ("A useless-looking object may have emotional value.", "An apparently useless object may protect memory, motivation, or a sense of self.", "役に立たなそうな物にも、気持ちの面で価値があるかもしれません。", "一見役に立たない物でも、記憶や意欲、自分らしさを守る場合があります。"),
            ("Leaving an object can be harder than choosing one.", "Regret often attaches to the meaningful object left behind rather than the practical object selected.", "選ぶことより、置いていく物を決めるほうが難しい場合があります。", "後悔は、選んだ実用品より、置いてきた大切な物に結びつくことがあります。"),
            ("A person is not an object and changes the whole problem.", "Adding a companion changes the scenario from inventory management to shared responsibility.", "人は物ではなく、一緒に行く人がいると問題全体が変わります。", "同行者が加わると、持ち物の管理ではなく、責任を分け合う状況に変わります。"),
            ("The best list depends on what the island already provides.", "No list is sensible until the environment and available resources are known.", "よいリストは、島に何があるかによって変わります。", "環境や利用できる資源が分からなければ、妥当なリストは作れません。"),
        ],
        prompts=[
            prompt("opening", "Three objects", "三つの物", BRIEF_OPENINGS[90], "物を三つ。どうぞ。", ("If none come quickly, which need would you solve first?", "Which item or need feels most essential?"), full=BRIEF_OPENINGS[90], full_ja="物を三つ。どうぞ。", full_followups=("If no objects come immediately, which need would you address first?", "Which selection or need is the most essential?"), safety="objects-or-needs-first"),
            prompt("reasons", "Why those three", "その三つの理由", "Why do your chosen objects—or your first need—deserve priority?", "選んだ物、または最初に満たしたい必要を、なぜ優先しますか？", ("What need does each answer meet?", "If you named one object or only a need, what would come next?"), full="What purpose gives each selection—or your first unresolved need—priority?", full_ja="それぞれの選択、またはまだ満たされていない最初の必要を優先するのは、どんな目的を果たすためですか？", full_followups=("Which need does each answer address?", "If you have one selection or only a priority so far, what should come next?"), safety="needs-one-or-three-items"),
            prompt("near-pick", "The near-pick", "選びかけた物", "What object or need, if any, nearly joined your answer?", "あなたの答えに入りかけた物や必要があるとすれば、何ですか？", ("If there was one, why did it lose its place?", "If not, what made your current priorities clear?"), full="Which object or need, if any, narrowly missed your current answer?", full_ja="今の答えにわずかに入らなかった物や必要があるとすれば、何ですか？", full_followups=("If one missed out, which trade-off removed it?", "If none did, what made the current priorities decisive?"), safety="near-pick-or-none"),
            prompt("useless", "The useless one", "役に立たない一つ", "Would you take anything that is not useful?", "役に立たない物も何か持っていきますか？", ("If yes, what emotional job would it do?", "If no, what comfort would you give up?"), full="Would any apparently useless object still earn a place?", full_ja="一見役に立たない物でも、選ぶ価値がありますか？", full_followups=("If so, which emotional need would it meet?", "If not, which form of comfort would you sacrifice?"), safety="useless-item-or-none"),
            prompt("regret", "Left behind", "置いていく物", "What might you regret leaving behind?", "置いていくと後悔しそうな物は何ですか？", ("If nothing, what makes your current priorities sufficient?", "If something, why could it not replace one answer?"), full="Which object could you regret excluding, if any?", full_ja="外すと後悔しそうな物があるとすれば、何ですか？", full_followups=("If none, why do the current priorities feel sufficient?", "If one, why could it not displace a current answer?"), safety="regret-or-none"),
            prompt("conditions", "What the island has", "島にあるもの", "What would you need to know about the island before changing your answer?", "答えを変える前に、島について何を知る必要がありますか？", ("Which resource would change one choice or priority?", "Which danger would make you rethink everything?"), full="Which unknown condition on the island could overturn your current priorities?", full_ja="島のどんな不明な条件によって、今の優先順位が変わり得ますか？", full_followups=("Which available resource would remove one selection or need?", "Which risk would force a complete rethink?"), safety="bounded-conditions"),
            prompt("companion", "One person", "一人の同行者", "If a person could come too, would you invite anyone?", "さらに一人連れていけるなら、誰かを誘いますか？", ("If yes, what would you share responsibility for?", "If no, what would be easier alone?"), full="If one companion were allowed, would you choose anyone?", full_ja="同行者を一人選べるなら、誰かを選びますか？", full_followups=("If so, which responsibility would you share?", "If not, which burden would be simpler alone?"), safety="companion-or-no-person"),
            prompt("flip", "Coming home", "帰ったあと", "After you came home, which chosen object would matter least—or, if you named only one need, would it still matter?", "帰宅後、選んだ物のうち最も重要でなくなるのはどれですか。それとも、必要を一つだけ挙げたなら、それは帰宅後も重要ですか？", ("If you chose several objects, why would one matter mainly on the island?", "If you named one need, why would it still matter—or stop mattering—at home?"), full="Which selection would lose most of its value after you returned—or, if you named only one need, would its value change at all?", full_ja="戻ったあと、どの選択が最も価値を失いますか。それとも、必要を一つだけ挙げたなら、その価値は変わりますか？", full_followups=("If you made several selections, which island condition gave one most of its value?", "If you named one need, what would make its value persist or disappear after the return?"), safety="one-three-or-needs-close"),
        ],
    ),
    91: topic(
        slug="someone-you-would-trade-lives-with-for-a-day", title="Someone you would trade lives with for a day", ko="하루 동안 인생을 바꿔 보고 싶은 사람", ja="一日だけ人生を入れ替えたい人",
        goal=("Let's explore another life for one day without requiring a real person's private details.", "実在の人の私生活を求めずに、別の人生を一日体験する想像を広げましょう。"), article_title=("What trading lives would reveal", "人生を入れ替えると見えること"),
        articles=[
            ("To trade lives is to borrow another person's ordinary day.", "To trade lives is to inhabit another person's ordinary constraints, access, and routine for a day.", "人生を入れ替えるとは、別の人の普通の一日を借りることです。", "人生を入れ替えるとは、別の人の日常の制約や機会、習慣を一日体験することです。"),
            ("A famous person is only one possible choice.", "The person need not be famous; an unfamiliar role can be just as revealing.", "有名人だけが選択肢ではありません。", "有名人である必要はなく、知らない役割も同じくらい多くを教えてくれます。"),
            ("A fictional or anonymous person protects privacy.", "A fictional figure, public role, or anonymous type can keep the thought experiment respectful.", "架空の人や匿名の人なら、プライバシーを守れます。", "架空の人物、公的な役割、匿名のタイプを選べば、思考実験を配慮あるものにできます。"),
            ("Curiosity may focus on freedom, pressure, skill, or routine.", "The attraction may be access, expertise, responsibility, pressure, or a completely different routine.", "興味は、自由、プレッシャー、能力、日課に向くかもしれません。", "魅力は、機会、専門性、責任、重圧、まったく違う日課にあるかもしれません。"),
            ("One day is long enough to notice limits but not understand a life.", "A day can expose constraints without granting enough context to judge an entire life.", "一日あれば制限には気づけますが、その人生全体は理解できません。", "一日で制約は見えても、その人生全体を判断できるほどの背景は得られません。"),
            ("Using the day for fun is different from using it to learn.", "Spending the day on pleasure would answer a different question from using it for investigation.", "楽しむために一日を使うのと、学ぶために使うのは違います。", "楽しみのために一日を使うのと、調べるために使うのでは、答える問いが異なります。"),
            ("Private information should remain private even in a fantasy.", "Curiosity does not justify invading private relationships, messages, or records, even in a hypothetical.", "想像の中でも、個人的な情報は守るべきです。", "仮定の話でも、好奇心を理由に私的な関係、メッセージ、記録へ立ち入るべきではありません。"),
            ("Telling the person afterward could change the meaning of the day.", "Disclosure afterward could turn private curiosity into a shared conversation or an unwanted intrusion.", "あとで本人に話すと、その一日の意味が変わるかもしれません。", "あとで知らせると、個人的な好奇心が共有の会話にも、望まれない侵入にもなり得ます。"),
            ("Wanting your own life back does not make the experiment pointless.", "Returning willingly can reveal which ordinary parts of one's own life are valuable.", "自分の人生に戻りたいと思っても、その体験が無意味になるわけではありません。", "喜んで自分の人生へ戻ることから、普段の生活の価値に気づくことがあります。"),
            ("The choice says as much about our questions as about the other person.", "The chosen life often reveals the experience or knowledge we currently feel we lack.", "誰を選ぶかは、その人だけでなく自分の疑問も表します。", "選んだ人生には、自分に今欠けていると感じる経験や知識が表れます。"),
        ],
        prompts=[
            prompt("opening", "Whose day", "誰の一日", BRIEF_OPENINGS[91], "一日だけ別の人の人生を生きるなら、誰ですか？", ("A fictional, public, or anonymous person is fine; what draws you to that life?", "If nobody fits, which role would you try instead?"), full=BRIEF_OPENINGS[91], full_ja="一日だけ別の人の人生を生きるなら、誰ですか？", full_followups=("A fictional, public, or anonymous person is enough; what makes that life revealing?", "If no individual fits, which role would you inhabit instead?"), safety="public-fictional-anonymous-or-no-person"),
            prompt("reason", "Why that life", "その人生を選ぶ理由", "Why would you trade lives with that person or role?", "なぜその人、または役割と人生を入れ替えたいですか？", ("Which experience would become available?", "Which pressure would you want to understand?"), full="Why would that person or role be worth inhabiting for a day?", full_ja="なぜその人、または役割の人生を一日体験する価値がありますか？", full_followups=("Which access or ability would become available?", "Which constraint would you want to understand from inside?"), safety="selected-person-or-role"),
            prompt("day", "Using the day", "一日の使い方", "What would you do first during that day?", "その一日で最初に何をしますか？", ("Would the first action be fun or useful?", "What would you avoid doing with someone else's life?"), full="How would you use the first part of that borrowed day?", full_ja="借りた一日の最初の時間をどう使いますか？", full_followups=("Would the priority be experience, investigation, or enjoyment?", "Which boundary would you refuse to cross?"), safety="bounded-use-no-private-access"),
            prompt("find-out", "What to learn", "知りたいこと", "What would you most want to find out?", "最も知りたいことは何ですか？", ("Could one day really answer it?", "What evidence would be fair to use?"), full="Which question would you most want the day to answer?", full_ja="その一日で、どの疑問への答えを最も知りたいですか？", full_followups=("Could a single day provide enough context?", "Which evidence could you gather without invading privacy?"), safety="knowledge-not-private-records"),
            prompt("surprise", "The unexpected part", "意外な部分", "What might be harder than it looks from outside?", "外から見るより難しそうなことは何ですか？", ("Which hidden responsibility might appear?", "What might be easier than expected?"), full="Which hidden constraint might challenge your outside view of that life?", full_ja="その人生を外から見た印象を変える、見えない制約は何でしょうか？", full_followups=("Which responsibility might only become visible from inside?", "Which assumed difficulty might prove easier?"), safety="no-claim-about-real-private-life"),
            prompt("tell", "Telling them", "本人に伝えるか", "If you chose a person, would you tell them afterward? If you chose only a role, would you share what you learned?", "人を選んだなら、あとで本人に伝えますか。役割だけを選んだなら、学んだことを誰かに話しますか？", ("For a person, what would be appropriate to share?", "For a role with no person, who, if anyone, could hear the general lesson?"), full="If you chose an individual, would you disclose the experience to them? If you chose only a role, would you share the general insight?", full_ja="個人を選んだなら、本人に体験を伝えますか。役割だけを選んだなら、一般的な気づきを誰かに共有しますか？", full_followups=("For an individual, which observation would be appropriate to share?", "For a role with no individual, who, if anyone, could hear the general insight?"), safety="person-role-or-private"),
            prompt("return", "Coming back", "戻ること", "Would you want your own life back at the end of the day?", "一日の終わりに、自分の人生へ戻りたいですか？", ("If yes, what would you value more?", "If no, which part of the borrowed life would be hard to leave?"), full="At the end of the exchange, would you willingly return to your own life?", full_ja="入れ替わりが終わるとき、進んで自分の人生へ戻りますか？", full_followups=("If so, which ordinary part would gain value?", "If not, which feature of the borrowed life would be hardest to surrender?"), safety="return-or-reluctance"),
            prompt("flip", "Someone choosing you", "自分が選ばれるなら", "What might someone want to learn by living your day?", "誰かがあなたの一日を生きるなら、何を知りたいと思いそうですか？", ("If nothing comes to mind, which routine might still surprise them?", "What would they misunderstand after only one day?"), full="Which question might another person hope to answer by inhabiting your day?", full_ja="別の人があなたの一日を生きるなら、どの疑問への答えを得たいと思うでしょうか？", full_followups=("If no special access comes to mind, which ordinary routine could still be revealing?", "Which conclusion would one day not justify?"), safety="self-without-private-disclosure"),
        ],
    ),
    92: topic(
        slug="the-superpower-you-would-choose", title="The superpower you would choose", ko="고르고 싶은 초능력", ja="選びたい超能力",
        goal=("Let's choose—or refuse—a superpower and examine its consequences.", "超能力を選ぶ、または選ばない理由と、その結果を考えましょう。"), article_title=("Every power changes the problem", "どの力も問題を変える"),
        articles=[
            ("A superpower is attractive because it removes an ordinary limit.", "A superpower appeals because it suspends an ordinary human constraint.", "超能力は、普通の制限をなくすので魅力的です。", "超能力は、普通の人間の制約を一時的になくすため魅力があります。"),
            ("The first use often reveals the real reason for choosing it.", "The imagined first use exposes the desire beneath the impressive ability.", "最初の使い方には、その力を選ぶ本当の理由が表れます。", "最初にどう使うかには、目立つ能力の奥にある願いが表れます。"),
            ("A useful power can still create a difficult responsibility.", "The more useful a power becomes, the harder it may be to refuse responsibility for using it.", "役立つ力でも、難しい責任が生まれることがあります。", "力が役立つほど、それを使う責任を断りにくくなるかもしれません。"),
            ("Keeping it secret protects privacy but limits help.", "Secrecy may protect the user while preventing open cooperation or accountability.", "秘密にすると自分を守れますが、助けられる範囲が狭くなります。", "秘密は使う人を守る一方、協力や責任の共有を難しくします。"),
            ("Telling people invites trust, pressure, and demands.", "Disclosure could create trust, but also surveillance, pressure, and competing demands.", "人に話すと、信頼だけでなく圧力や要求も生まれます。", "公表すると信頼が生まれる一方、監視、圧力、対立する要求も生じ得ます。"),
            ("Every advantage has a downside when it is always available.", "An ability that sounds liberating may become exhausting when it can never be switched off.", "いつでも使える利点には、必ず困る面もあります。", "自由に見える能力でも、止められなければ疲れるものになり得ます。"),
            ("Refusing a power can be a reasonable choice.", "Declining a power may be rational when its cost, temptation, or responsibility is too high.", "力を選ばないことも、もっともな選択です。", "代償、誘惑、責任が大きすぎるなら、能力を断るのは合理的です。"),
            ("The power most people choose may reflect a shared frustration.", "A popular choice can reveal a common limitation people most want to escape.", "多くの人が選ぶ力には、共通の不満が表れるかもしれません。", "人気のある力は、多くの人が逃れたい共通の制約を示すことがあります。"),
            ("A power can solve one problem while moving another elsewhere.", "Extraordinary ability rarely removes consequences; it redistributes them.", "一つの問題を解決しても、別の問題が生まれることがあります。", "特別な能力は結果をなくすのではなく、別の場所へ移すことが多いです。"),
            ("The best choice depends on the limits placed on the power.", "Duration, control, visibility, and reversibility can completely change the choice.", "いちばんよい力は、その力の制限によって変わります。", "持続時間、制御、公に見えるか、元に戻せるかで、選択は完全に変わります。"),
        ],
        prompts=[
            prompt("opening", "Three seconds", "三秒で選ぶ", BRIEF_OPENINGS[92], "超能力を一つ、三秒で選んでください。", ("If no power comes quickly, which ordinary limit bothers you most?", "Would choosing none feel safer?"), full=BRIEF_OPENINGS[92], full_ja="超能力を一つ、三秒で選んでください。", full_followups=("If no power comes immediately, which human constraint would you most like to suspend?", "Would declining every power be preferable?"), safety="quick-pick-or-none"),
            prompt("first-use", "The first use", "最初の使い方", "If you chose a power, what would you use it for first? If you chose none, what would you do about the ordinary limit instead?", "力を選んだなら、最初に何のために使いますか。何も選ばないなら、その普通の制約にどう対応しますか？", ("Who, if anyone, would benefit from that response?", "What would make it responsible?"), full="If you selected a power, what would its first deliberate use be? If you declined them all, how would you address the ordinary constraint instead?", full_ja="力を選んだなら、考えたうえで最初にどう使いますか。すべて断ったなら、その普通の制約には、代わりにどのような方法で対処しますか？", full_followups=("Who, if anyone, would be affected by that response?", "Which safeguard would make it responsible?"), safety="power-or-no-power-response"),
            prompt("secret", "Telling people", "人に話すか", "Would you tell anyone about your choice, including choosing none?", "何も選ばない場合も含め、自分の選択を誰かに話しますか？", ("If yes, who would need to know?", "If no, what would privacy protect?"), full="Would you disclose your decision, including a decision to reject every power?", full_ja="すべての力を断る判断も含め、自分の選択を誰かに公表しますか？", full_followups=("If so, who would have a legitimate reason to know?", "If not, which risk would privacy reduce?"), safety="choice-disclosure-or-privacy"),
            prompt("downside", "The downside", "困る点", "What would be the biggest problem with your chosen power—or the strongest reason to choose none?", "選んだ力の最大の問題、または何も選ばない最も強い理由は何ですか？", ("For a power, could you switch it off?", "For no power, which risk matters most?"), full="Which downside could outweigh your chosen power's benefit, or justify declining every power?", full_ja="どんな欠点なら、選んだ力の利点を上回る、またはすべての力を断る理由になりますか？", full_followups=("For a power, how much control would you have over it?", "For no power, which predictable risk is decisive?"), safety="power-downside-or-none"),
            prompt("refuse", "A power to refuse", "断りたい力", "Which superpower would you refuse?", "どの超能力なら断りますか？", ("What cost makes it unacceptable?", "Could a safer limit change your answer?"), full="Which apparently useful superpower would you decline?", full_ja="一見役に立ちそうでも、どの超能力なら断りますか？", full_followups=("Which cost or temptation makes it unacceptable?", "Would a strict limit make it tolerable?"), safety="refusal-valid"),
            prompt("popular", "Most people's choice", "多くの人の選択", "What power do you think most people would pick?", "多くの人はどの力を選ぶと思いますか？", ("What shared problem would it solve?", "Would people use it as they claim?"), full="Which power would probably attract the largest number of people?", full_ja="最も多くの人を引きつけそうな力はどれですか？", full_followups=("Which common frustration makes it attractive?", "How might real use differ from stated intentions?"), safety="general-social-guess"),
            prompt("limits", "One rule", "一つのルール", "What one rule would govern your power—or your decision not to have one?", "力を持つ場合、または持たないと決めた場合に、どんなルールを一つ設けますか？", ("Who would enforce the rule?", "What temptation or risk is it meant to stop?"), full="Which single principle would govern possessing a power or declining every power?", full_ja="力を持つ場合でも、すべての力を断る場合でも、どんな原則を一つ設けますか？", full_followups=("How could that principle be maintained?", "Which predictable temptation or risk is it designed to prevent?"), safety="power-or-none-principle"),
            prompt("flip", "Ordinary skill", "普通の能力", "What ordinary skill is better than a superpower in real life?", "現実では、どんな普通の能力が超能力より役立ちますか？", ("Why does it matter more?", "How can someone develop it?"), full="Which ordinary human ability would remain more valuable than a superpower?", full_ja="どんな普通の人間の能力が、超能力より価値を持ち続けますか？", full_followups=("Which real consequence makes it more valuable?", "How can that ability be strengthened without magic?"), safety="ordinary-skill-close"),
        ],
    ),
    93: topic(
        slug="the-one-food-you-could-eat-forever", title="The one food you could eat forever", ko="평생 먹을 수 있는 한 가지 음식", ja="一生食べ続けられる一つの食べ物",
        goal=("Let's test one imaginary food choice while keeping real dietary limits private.", "実際の食事上の制限は話さなくてもよいまま、一つの食べ物を選ぶ想像を試しましょう。"), article_title=("Why one food would stop being enough", "一つの食べ物では足りなくなる理由"),
        articles=[
            ("Choosing one food forever is a game, not dietary advice.", "Choosing one food forever is an impossible thought experiment, not nutritional or medical advice.", "一つの食べ物を永遠に選ぶのはゲームであり、食事の助言ではありません。", "一つの食べ物だけを永遠に選ぶのは不可能な思考実験であり、栄養や医療の助言ではありません。"),
            ("A familiar favourite may feel safer than an exciting dish.", "A dependable favourite may survive repetition better than an intense but exciting dish.", "刺激的な料理より、慣れた好物のほうが安心かもしれません。", "強く刺激的な料理より、安定した好物のほうが繰り返しに耐えられるかもしれません。"),
            ("Taste changes when there is no other option.", "Pleasure changes when variety disappears and the choice can no longer be refused.", "ほかの選択肢がなくなると、味の感じ方も変わります。", "種類がなくなり、その食べ物を断れなくなると、楽しさの質も変わります。"),
            ("To get sick of a food means to become tired of it here.", "Here, getting sick of a food means becoming bored with it, not becoming physically ill.", "ここで食べ物に「飽きる」とは、それにうんざりすることで、病気になる意味ではありません。", "ここで get sick of は食べ物に飽きるという意味で、体調を崩すという意味ではありません。"),
            ("Texture, smell, temperature, and routine all affect repetition.", "Repetition involves texture, aroma, temperature, timing, and memory as well as flavour.", "繰り返しには、味だけでなく食感、香り、温度、日課も影響します。", "繰り返しには、味だけでなく食感、香り、温度、時間、記憶も影響します。"),
            ("The food we nearly choose reveals what we would miss.", "A rejected second choice often identifies the kind of variety we would miss first.", "選びかけた別の食べ物から、何が恋しくなるか分かります。", "最後に外した第二候補から、最初に恋しくなる種類の変化が分かります。"),
            ("Giving up a food can be easy for practical or personal reasons.", "A food may be easy to surrender because of taste, access, cost, religion, allergy, or another private reason.", "実用的な理由や個人的な理由で、簡単に諦められる食べ物もあります。", "味、入手しやすさ、費用、宗教、アレルギー、その他の私的な理由で、手放しやすい食べ物もあります。"),
            ("A healthy but boring answer may last longer than a favourite.", "A less exciting but flexible choice may be more sustainable than the food we love most today.", "健康的でも退屈な答えのほうが、好物より長く続くかもしれません。", "刺激は少なくても応用しやすい食べ物のほうが、今いちばん好きな物より続けやすいかもしれません。"),
            ("Real dietary boundaries do not need to be explained for the game.", "No learner owes medical, religious, sensory, or eating-history details to justify declining the scenario.", "このゲームのために、実際の食事上の制限を説明する必要はありません。", "この仮定を断るために、医療、宗教、感覚、食事経験の詳細を説明する必要はありません。"),
            ("The thought experiment is really about variety and desire.", "The question reveals how variety, freedom, and scarcity shape desire more than it identifies a perfect food.", "この想像は、実は食べ物より、変化や欲求について考えるものです。", "この問いは完璧な食べ物を探すより、種類、自由、不足が欲求をどう変えるかを示します。"),
        ],
        prompts=[
            prompt("opening", "One food", "一つの食べ物", BRIEF_OPENINGS[93], "一つの食べ物だけを永遠に、ほかは何も食べられません。何を選びますか？", ("If the scenario does not work for you, which food would you keep most often instead?", "What makes that choice flexible?"), full=BRIEF_OPENINGS[93], full_ja="一つの食べ物だけを永遠に、ほかは何も食べられません。何を選びますか？", full_followups=("If the premise conflicts with a dietary boundary, which food would you simply keep most often instead?", "Which feature makes the choice sustainable?"), safety="dietary-boundary-or-hypothetical"),
            prompt("duration", "Before you got bored", "飽きるまで", "How long would it take before you got sick of it?", "それに飽きるまで、どのくらいかかりそうですか？", ("What part would become boring first?", "Could changing how it is served help?"), full="How long could you eat it before repetition made you get sick of it?", full_ja="繰り返しでその食べ物に飽きるまで、どのくらい食べ続けられますか？", full_followups=("Which sensory feature would become tiring first?", "Could a different preparation delay the boredom?"), safety="boredom-not-illness"),
            prompt("near-pick", "The second choice", "第二候補", "What, if anything, did you nearly choose?", "選びかけた別の食べ物があるとすれば、何ですか？", ("If there was one, why did it lose?", "If not, what made the first answer clear?"), full="Which alternative, if any, nearly replaced your first choice?", full_ja="最初の選択に代わりそうだった食べ物があるとすれば、何ですか？", full_followups=("If one nearly won, which weakness removed it?", "If none did, which advantage made the first choice decisive?"), safety="second-choice-or-none"),
            prompt("miss", "What you would miss", "恋しくなる食べ物", "What other kind of food would you miss most?", "ほかのどんな種類の食べ物がいちばん恋しくなりますか？", ("Would you miss a taste, texture, or occasion?", "When would the missing food matter most?"), full="Which kind of variety would you miss most?", full_ja="どんな種類の変化がいちばん恋しくなりますか？", full_followups=("Would the loss concern flavour, texture, temperature, or occasion?", "In which situation would that missing variety matter most?"), safety="no-specific-diet-disclosure"),
            prompt("give-up", "Easy to give up", "簡単に諦められる物", "What food could you give up easily, if any?", "簡単に諦められる食べ物があるとすれば、何ですか？", ("If one comes to mind, why does it matter so little?", "If none does, which food would be hardest to lose?"), full="Which food, if any, would be easiest to surrender permanently?", full_ja="永久に手放すのが最も簡単な食べ物があるとすれば、何ですか？", full_followups=("If one comes to mind, which feature makes it dispensable?", "If none does, which category would be most difficult to lose?"), safety="give-up-or-none"),
            prompt("healthy", "The boring answer", "退屈でも健康的な答え", "Would you choose a boring but healthy food instead?", "退屈でも健康的な食べ物を選びますか？", ("What would make that choice last?", "What enjoyment would you lose?"), full="Would a less exciting but more sustainable food change your answer?", full_ja="刺激は少なくても続けやすい食べ物なら、答えは変わりますか？", full_followups=("Which practical advantage would justify the change?", "Which source of enjoyment would be sacrificed?"), safety="no-health-judgment"),
            prompt("freedom", "Choosing again", "選び直せるなら", "How often would you need a chance to change the food?", "どのくらいの頻度で食べ物を変えられる必要がありますか？", ("Would once a year be enough?", "What would make you use the change early?"), full="What minimum chance to revise the choice would make the scenario tolerable?", full_ja="この状況を受け入れられるようにするには、最低どのくらい選び直す機会が必要ですか？", full_followups=("Would an annual reset preserve enough freedom?", "Which event would make you use the revision immediately?"), safety="bounded-revision"),
            prompt("flip", "Variety", "種類の大切さ", "Why can variety matter more than a favourite food?", "なぜ好物より種類の多さが大切になることがありますか？", ("What does variety give us besides taste?", "Where else does too much repetition change enjoyment?"), full="Why might freedom to vary matter more than any single favourite?", full_ja="なぜ一つの好物より、変化を選べる自由のほうが大切になり得ますか？", full_followups=("Which need does variety meet beyond flavour?", "In which other part of life does repetition reduce enjoyment?"), safety="general-reflective-close"),
        ],
    ),
    94: topic(
        slug="one-thing-you-would-make-free-forever", title="One thing you would make free forever", ko="평생 무료로 만들고 싶은 한 가지", ja="一生無料にしたい一つのもの",
        goal=("Let's choose one free-for-life option and test how it would actually be used.", "一生無料にする一つを選び、実際にどう使うか考えましょう。"), article_title=("When free changes behaviour", "無料が行動を変えるとき"),
        articles=[
            ("Free access changes more than the price.", "Permanent free access can change frequency, habits, expectations, and value as well as cost.", "無料になると、値段以外のことも変わります。", "永久に無料になると、費用だけでなく頻度、習慣、期待、価値も変わります。"),
            ("People may use a free service more even when they do not need it.", "Removing price can increase use even when the additional use creates little benefit.", "必要がなくても、無料なら使う回数が増えるかもしれません。", "価格をなくすと、追加の利用にほとんど利益がなくても使用が増える場合があります。"),
            ("The best choice depends on real use, not the highest price.", "The most expensive option is not necessarily the most valuable if it rarely fits daily life.", "最も高い物より、実際によく使う物のほうがよい選択かもしれません。", "最も高価な選択肢でも、日常に合わなければ最も価値があるとは限りません。"),
            ("Some people would choose for convenience; others for opportunity.", "A practical choice saves friction, while an aspirational choice may open experiences that were previously inaccessible.", "便利さで選ぶ人もいれば、新しい機会のために選ぶ人もいます。", "実用的な選択は手間を減らし、理想的な選択は今まで届かなかった経験を可能にします。"),
            ("A benefit can reach other people without being resold.", "Sharing access, time, or experience can spread the benefit without turning it into a resale business.", "転売しなくても、無料の利益をほかの人に広げられます。", "利用、時間、経験を共有すれば、転売せずに利益を広げられます。"),
            ("To resell means to sell something again after receiving it.", "Reselling free access raises legal, contractual, and fairness questions before it raises profit.", "転売するとは、受け取った物をもう一度売ることです。", "無料の利用権を転売するなら、利益より先に法律、契約、公平さの問題が生まれます。"),
            ("The boring answer may solve a larger everyday cost.", "An unexciting essential may create more lasting value than a glamorous luxury.", "退屈な答えでも、毎日の大きな費用を減らせるかもしれません。", "目立たない必需品のほうが、華やかなぜいたく品より長く価値を生む場合があります。"),
            ("Free use can still cost time, space, attention, or energy.", "A zero price does not eliminate the opportunity costs of time, space, attention, and environmental impact.", "値段がゼロでも、時間、場所、注意、エネルギーは必要です。", "価格がゼロでも、時間、空間、注意、環境への影響という機会費用はなくなりません。"),
            ("Not using the free option is also a valid result.", "Permanent access can reveal that scarcity, not genuine interest, created the original desire.", "無料でも使わないという結果もあります。", "永久に使えても利用しないなら、元の欲求は本当の興味より不足感から生まれた可能性があります。"),
            ("The choice reveals what we want more of in ordinary life.", "The useful question is which ordinary limitation the free option would actually remove.", "何を無料にするかで、日常にもっとほしいものが見えます。", "大切なのは、その無料の選択が日常のどの制限を実際になくすかです。"),
        ],
        prompts=[
            prompt("opening", "Free for life", "一生無料", BRIEF_OPENINGS[94], "コーヒー、タクシー、映画、飛行機のうち、一つが一生無料です。どれですか？", ("If none would help, what kind of option would?", "What makes your choice useful?"), full=BRIEF_OPENINGS[94], full_ja="コーヒー、タクシー、映画、飛行機のうち、一つが一生無料です。どれですか？", full_followups=("If none of the four would add value, which category would?", "Which practical or personal benefit supports your choice?"), safety="listed-choice-or-none"),
            prompt("use", "Real use", "実際の利用", "How often would you actually use it—often, rarely, or never?", "実際に使う頻度は、多いですか、少ないですか、それとも全く使いませんか？", ("If you would use it, which current limit would disappear?", "If never, what made you choose it—or would you switch?"), full="Would the free access change your behaviour often, rarely, or not at all?", full_ja="無料で利用できると、行動は頻繁に変わりますか、まれに変わりますか、それとも全く変わりませんか？", full_followups=("If use would increase, which current constraint would disappear?", "If it would never change your behaviour, what justifies keeping or revising the choice?"), safety="use-often-rarely-or-never"),
            prompt("week", "A changed week", "変わる一週間", "Would anything change in a normal week?", "普通の一週間で、何か変わりますか？", ("If yes, which day would change most?", "If nothing would change, why not?"), full="Which part of an ordinary week, if any, would change?", full_ja="普通の一週間で変わる部分があるとすれば、どこですか？", full_followups=("If something changed, which routine would be altered first?", "If nothing changed, what explains the lack of effect?"), safety="routine-or-no-change"),
            prompt("benefit", "Beyond you", "自分以外への利益", "Could anyone else benefit from your free option?", "その無料の選択で、自分以外の人も利益を得られますか？", ("If yes, how could you share it legally?", "If no, what makes the benefit personal?"), full="Who else, if anyone, could benefit without violating the rules?", full_ja="規則に反せずに利益を得られる人がほかにいるとすれば、誰ですか？", full_followups=("If someone could benefit, what legitimate form would sharing take?", "If nobody could, which feature makes the access non-transferable?"), safety="shared-or-personal-no-assumption"),
            prompt("boring", "The boring answer", "退屈でも正しい答え", "What is the boring but sensible choice?", "退屈でも賢い選択は何ですか？", ("Why might it beat your first answer?", "Would you really switch to it?"), full="Which unexciting option might be the most rational choice?", full_ja="刺激はなくても、最も合理的な選択はどれですか？", full_followups=("Which long-term cost could make it superior?", "Would rational value actually change your preference?"), safety="no-money-disclosure"),
            prompt("resell", "Reselling", "転売", "Would you try to resell any part of the free access?", "無料の利用権の一部を転売しようとしますか？", ("If yes, what rule would have to allow it?", "If no, what makes resale unfair or pointless?"), full="Under what condition, if any, would you try to resell the free access?", full_ja="無料の利用権を転売しようとする条件があるとすれば、どんな条件ですか？", full_followups=("Which legal or contractual permission would be necessary?", "Which fairness concern could still rule it out?"), safety="resale-legal-or-no-resale"),
            prompt("cost", "Still not free", "残る負担", "Would the free option cost you time, space, attention—or nothing if unused?", "無料の選択に時間、場所、注意が必要ですか。それとも、使わないなら負担はありませんか？", ("If there is a hidden cost, which one matters most?", "If there is none, does that strengthen or weaken the choice?"), full="Which non-financial cost would remain, or would non-use remove every practical cost?", full_ja="どんな金銭以外の負担が残りますか。それとも、使わなければ実際の負担はすべてなくなりますか？", full_followups=("If a hidden cost remains, which one could reverse the choice?", "If none remains, does that justify keeping an unused option?"), safety="cost-or-unused-no-cost"),
            prompt("flip", "Paying on purpose", "あえて払うもの", "Is there anything you would pay for even if a free version existed?", "無料のものがあっても、お金を払いたいものはありますか？", ("If yes, what extra value would payment buy?", "If no, what makes the free version enough?"), full="Which service or experience, if any, would make you reject a free alternative?", full_ja="無料の代わりを断るほどのサービスや経験があるとすれば、何ですか？", full_followups=("If one exists, which added value would justify paying?", "If none does, which quality makes free access sufficient?"), safety="pay-or-no-pay"),
        ],
    ),
    95: topic(
        slug="going-a-week-without-your-phone", title="Going a week without your phone", ko="일주일 동안 휴대전화 없이 지내기", ja="一週間、携帯電話なしで過ごすこと",
        goal=("Let's examine a phone-free week without judging essential access or support needs.", "必要な連絡や支援を否定せずに、携帯電話なしの一週間を考えましょう。"), article_title=("What a phone-free week would test", "携帯電話なしの一週間で試されること"),
        articles=[
            ("A digital detox means choosing time away from digital devices.", "A digital detox is a deliberate period away from digital devices, not a moral test of self-control.", "デジタルデトックスとは、デジタル機器から離れる時間を選ぶことです。", "デジタルデトックスとは、デジタル機器から意識的に離れる期間であり、自制心を測る道徳的なテストではありません。"),
            ("For some people, a phone is optional entertainment.", "For some people, much phone use is convenient or recreational rather than essential.", "人によっては、携帯電話は主に娯楽の道具です。", "人によっては、携帯電話の多くの利用は必要不可欠ではなく、便利さや娯楽のためです。"),
            ("For others, it is an access, safety, work, or care tool.", "For others, a phone provides accessibility, medical support, safety, paid work, or care coordination.", "別の人には、アクセス、安全、仕事、ケアのための道具です。", "別の人には、アクセシビリティ、医療支援、安全、有給の仕事、ケアの調整に必要な道具です。"),
            ("In this topic, what breaks first means what stops working first.", "Here, what breaks first refers to the first routine or system that fails, not physical damage.", "この話で「最初に駄目になるもの」とは、最初に機能しなくなるものを指します。", "ここで「最初に駄目になるもの」とは、物理的な破損ではなく、最初に機能しなくなる日課や仕組みを指します。"),
            ("Maps, payments, tickets, and messages have moved into one device.", "Modern infrastructure has concentrated navigation, payment, tickets, authentication, and communication in one device.", "地図、支払い、切符、メッセージが一つの機器に集まっています。", "現代の仕組みでは、移動、支払い、切符、認証、連絡が一つの機器に集中しています。"),
            ("Missing the phone is not the same as missing every app.", "The hardest loss may be one function, one person, or one source of reassurance rather than the device itself.", "携帯電話が恋しいことと、すべてのアプリが必要なことは同じではありません。", "最も困るのは機器そのものではなく、一つの機能、一人との連絡、安心感かもしれません。"),
            ("Less interruption could improve focus or rest.", "Fewer alerts could improve concentration, sleep, presence, or boredom tolerance.", "中断が減ると、集中や休息がよくなるかもしれません。", "通知が減ると、集中、睡眠、目の前への注意、退屈への耐性がよくなる可能性があります。"),
            ("A week without a phone may require another device or another person.", "A workable experiment may rely on replacement devices, printed information, or agreed human support.", "携帯電話なしの一週間には、別の機器や人の助けが必要かもしれません。", "実行できる実験には、代わりの機器、紙の情報、合意した人の支援が必要な場合があります。"),
            ("The longest past break may have been chosen or forced.", "Previous time offline may have come from travel, damage, illness, rules, preference, or no memorable example at all.", "過去に離れた時間は、自分で選んだ場合も、仕方なかった場合もあります。", "過去にオンラインから離れた理由は、旅行、故障、体調、規則、好み、または覚えている例がないことかもしれません。"),
            ("A useful experiment removes what is optional and protects what is essential.", "A responsible digital detox distinguishes discretionary habits from access and care needs.", "よい実験は、不要なものを減らし、必要なものを守ります。", "責任あるデジタルデトックスは、自由に減らせる習慣と、アクセスやケアの必要を区別します。"),
        ],
        prompts=[
            prompt("opening", "Seven days", "七日間", BRIEF_OPENINGS[95], "携帯電話なしで七日間過ごせますか？正直に答えてください。", ("If no-phone is not safe or accessible, which optional use could you pause?", "If yes, what makes it possible?"), full=BRIEF_OPENINGS[95], full_ja="携帯電話なしで七日間過ごせますか？正直に答えてください。", full_followups=("If going fully phone-free would block access, safety, care, or work, which discretionary use could you pause instead?", "If it is feasible, which condition makes it workable?"), safety="full-detox-or-bounded-pause"),
            prompt("breaks", "What stops working", "最初に機能しなくなること", "In your chosen no-phone or reduced-use experiment, what would stop working first—if anything?", "選んだ「携帯電話なし」または「利用を減らす」実験で、最初に機能しなくなるものがあるとすれば何ですか？", ("If something would stop, is it essential or only convenient?", "If nothing would stop, what keeps the experiment bounded?"), full="Within your selected phone-free or reduced-use experiment, which routine or system, if any, would fail first?", full_ja="選んだ「携帯電話なし」または「利用を減らす」実験で、最初に機能しなくなる日課や仕組みがあるとすれば、どれですか？", full_followups=("If one would fail, is that function essential, accessible support, or convenience?", "If none would fail, which boundary keeps the experiment workable?"), safety="bounded-breaks-is-nonliteral"),
            prompt("miss", "What you would miss", "恋しくなるもの", "During that experiment, what would you actually miss most—if anything?", "その実験中、実際に最も恋しくなるものがあるとすれば、何ですか？", ("Would it be a person, function, habit, or feeling?", "If nothing, is a full break simply easy for you, or does needed access remain?"), full="During the selected experiment, which function, connection, habit, or reassurance, if any, would you miss most?", full_ja="選んだ実験中、最も恋しくなる機能、つながり、習慣、または安心感があるとすれば、どれですか？", full_followups=("If one is missing, what need does it currently meet?", "If nothing is missing, is a full detox simply easy for you, or does essential access remain?"), safety="selected-experiment-or-none"),
            prompt("improve", "What might improve", "よくなりそうなこと", "What might improve during the week?", "その一週間で何がよくなりそうですか？", ("If nothing would improve, what makes the phone already balanced?", "If something would, when would you notice it?"), full="Which part of life might improve during a phone-free or reduced-phone week?", full_ja="携帯電話なし、または利用を減らした一週間で、生活のどの部分がよくなりそうですか？", full_followups=("If nothing would improve, which current boundary already works?", "If something would, what evidence would show the change?"), safety="improvement-or-no-change"),
            prompt("past", "A past break", "過去に離れた時間", "What is the longest you have gone without a phone—or without one optional use?", "携帯電話、または不要な使い方から最も長く離れたのはどのくらいですか？", ("If there is no example, when might a short break fit?", "If there is one, was it chosen or forced?"), full="What is your longest phone-free period, or your longest break from a nonessential use?", full_ja="携帯電話なしで過ごした最長の期間、または不要な利用から離れた最長の期間はどのくらいですか？", full_followups=("If no example comes to mind, which setting could support a short pause?", "If one exists, was the separation voluntary or imposed?"), safety="history-or-no-history"),
            prompt("support", "Making it work", "実行するための支え", "What would you need to make your chosen experiment work safely?", "選んだ実験を安全に実行するには何が必要ですか？", ("If an essential contact or tool is paused, what replaces it?", "If a full break needs no replacement, what makes that safe?", "If needed access stays available, what boundary protects it?"), full="Which tools, access arrangements, boundaries, or support would make the selected experiment responsible?", full_ja="選んだ実験を責任を持って実行するには、どんな道具、アクセスの準備、制限、または支援が必要ですか？", full_followups=("If an essential function is paused, which replacement preserves it?", "If a full detox needs no replacement, which condition makes that responsible?", "If essential access remains available, which boundary keeps the experiment meaningful?"), safety="access-care-work-protected"),
            prompt("boundary", "One use to keep", "残す一つの使い方", "Which phone use must remain available, or which optional use would you pause?", "利用できるよう残す必要がある携帯電話の使い方はどれですか。それとも、必須ではない使い方のうち、どれを一時休止しますか？", ("Which need makes that boundary appropriate?", "How would you keep the pause limited?"), full="Which phone function must remain available, or which discretionary use would you suspend?", full_ja="利用できるよう残す必要がある携帯電話の機能はどれですか。それとも、必須ではない使い方のうち、どれを一時的に停止しますか？", full_followups=("Which need makes that boundary proportionate?", "How would you keep the suspension limited rather than absolute?"), safety="essential-exception-valid"),
            prompt("flip", "After the week", "一週間のあと", "What phone habit, if any, would you change afterward?", "一週間のあと、変えたい携帯電話の習慣があるとすれば何ですか？", ("If none, what current habit works well?", "If one, what small change could last?"), full="Which habit, if any, would you redesign after the experiment?", full_ja="その実験のあと、見直したい習慣があるとすればどれですか？", full_followups=("If none, which existing boundary deserves to remain?", "If one, which modest change could be sustainable?"), safety="change-or-no-change"),
        ],
    ),
    96: topic(
        slug="what-you-would-do-if-ai-did-your-job", title="What you would do if AI did your job", ko="AI가 내 일을 한다면 할 일", ja="AIが自分の仕事をしたらすること",
        goal=("Let's imagine AI doing the task while the same salary remains, including routes for study, care, or no paid role.", "AIが仕事をしても同じ給料が続く状況を、勉強、ケア、有給の仕事がない場合も含めて想像しましょう。"), article_title=("When the task disappears but income remains", "作業がなくなり収入が残るとき"),
        articles=[
            ("In this scenario, AI does the work and the same salary continues.", "The thought experiment keeps the salary unchanged while AI performs the paid tasks; it is not a forecast of dismissal.", "この想像では、AIが仕事をしても同じ給料が続きます。", "この思考実験では、AIが有給の作業を行っても給料は変わらず、解雇の予測ではありません。"),
            ("People without a paid job can use study, care, unpaid work, or a general role.", "Learners without paid employment can map the scenario onto study, care, unpaid contribution, or a purely hypothetical role.", "有給の仕事がない人は、勉強、ケア、無給の活動、または一般的な役割で考えられます。", "有給で働いていない学習者は、勉強、ケア、無給の貢献、または完全な仮定の役割に置き換えられます。"),
            ("The first free Monday might feel like a holiday.", "The first unstructured Monday could feel liberating before the novelty disappears.", "最初の自由な月曜日は、休日のように感じるかもしれません。", "予定のない最初の月曜日は、珍しさが消えるまで解放されたように感じるかもしれません。"),
            ("After a month, the missing routine may matter more.", "After the initial relief, lost routine, social contact, progress, or responsibility may become more visible.", "一か月後には、なくなった日課のほうが気になるかもしれません。", "最初の安心のあと、日課、社会的なつながり、成長、責任を失ったことが見えやすくなります。"),
            ("A work identity is the part of self-understanding connected to work.", "Work identity describes how occupation, contribution, and expertise shape one's sense of self.", "仕事を通じた自己認識とは、仕事と結びついた自分の見方です。", "work identity とは、職業、貢献、専門性が自己認識をどう形作るかを表します。"),
            ("Not everyone builds identity through paid work.", "Meaning and identity may come primarily from relationships, care, community, learning, or creative activity.", "誰もが有給の仕事から自分らしさを得るわけではありません。", "意味や自己認識は、人間関係、ケア、地域、学び、創作活動から主に得られる場合もあります。"),
            ("Telling people about the arrangement could invite envy or doubt.", "Disclosing the arrangement could create curiosity, envy, disbelief, or questions about fairness.", "その状況を人に話すと、うらやましさや疑いが生まれるかもしれません。", "その状況を公にすると、好奇心、嫉妬、疑い、公平さへの疑問が生じる可能性があります。"),
            ("Starting something new gives free time a direction.", "A self-chosen project can replace some structure without copying the old job.", "新しいことを始めると、自由な時間に方向ができます。", "自分で選んだ活動は、以前の仕事を再現せずに一部の構造を置き換えられます。"),
            ("Doing the work yourself again may depend on meaning rather than money.", "A return to doing the tasks yourself might be motivated by mastery, service, community, or responsibility rather than income.", "また自分で仕事をする理由は、お金より意味かもしれません。", "また自分で作業をする理由は、収入より熟達、奉仕、共同体、責任かもしれません。"),
            ("The question separates what we do from why it matters.", "The scenario distinguishes the tasks a role contains from the human needs the role happens to meet.", "この問いは、何をするかと、なぜ大切かを分けます。", "この状況は、役割に含まれる作業と、その役割が満たしていた人間の必要を分けて考えさせます。"),
        ],
        prompts=[
            prompt("opening", "Monday", "月曜日", BRIEF_OPENINGS[96], "同じ給料で仕事はありません。月曜日をどう過ごしますか？", ("If no paid role applies, use study, care, unpaid work, or an imagined role; what would replace its first hour?", "What would feel best about the day?"), full=BRIEF_OPENINGS[96], full_ja="同じ給料で仕事はありません。月曜日をどう過ごしますか？", full_followups=("If no paid role applies, map the task to study, care, unpaid contribution, or a hypothetical role; what would replace the first working hour?", "Which part of the unstructured day would feel most liberating?"), safety="paid-study-care-unpaid-or-hypothetical"),
            prompt("month", "Month three", "三か月目", "What would your life look like in month three?", "三か月目の生活はどうなっていますか？", ("Which new routine would exist?", "What might have become difficult by then?"), full="How would the arrangement feel by the third month?", full_ja="三か月目には、その状況をどう感じていますか？", full_followups=("Which self-chosen structure would have emerged?", "Which missing function of the old role might become difficult?"), safety="relief-or-difficulty"),
            prompt("tell", "Telling people", "人に話すか", "Would you tell people that AI now did the tasks in your chosen role?", "選んだ役割の作業を今はAIがしていると、人に話しますか？", ("If yes, how would you explain the arrangement?", "If no, what reaction would you avoid?"), full="Would you disclose that AI performs the tasks in your selected paid, unpaid, study, care, or hypothetical role?", full_ja="選んだ有給・無給の仕事、勉強、ケア、または仮定の役割で、AIが作業を行っていると公にしますか？", full_followups=("If so, how would you explain the arrangement without inventing income?", "If not, which likely reaction would privacy prevent?"), safety="any-role-disclosure-or-privacy"),
            prompt("miss", "What work gave you", "仕事が与えていたもの", "What part of work, study, care, or routine might you miss?", "仕事、勉強、ケア、または日課のどの部分が恋しくなりそうですか？", ("If nothing, what would replace its structure?", "If something, which need did it meet?"), full="Which need met by the old work, study, care, or routine might remain unmet?", full_ja="以前の仕事、勉強、ケア、または日課が満たしていたどんな必要が、満たされないままになりそうですか？", full_followups=("If none, which new source of structure would be enough?", "If one remains, how did the old role satisfy it?"), safety="role-or-no-role"),
            prompt("start", "Starting something", "始めること", "What, if anything, would you start with the free time?", "自由な時間で始めることがあるとすれば、何ですか？", ("If something, why has it waited until now?", "If nothing, how would you protect open time?"), full="Which self-chosen project, if any, would give the new time direction?", full_ja="新しい時間に方向を与える、自分で選んだ活動があるとすれば何ですか？", full_followups=("If one emerges, which current barrier would disappear?", "If none, what value would unstructured time have?"), safety="project-or-open-time"),
            prompt("identity", "Work identity", "仕事を通じた自己認識", "How much is your identity connected to work or another role?", "自分らしさは、仕事や別の役割とどのくらい結びついていますか？", ("If little, what shapes it more?", "If strongly, what would remain after the tasks disappeared?"), full="How strongly does work identity—or identity through another role—shape how you see yourself?", full_ja="仕事を通じた自己認識、または別の役割を通じた自己認識は、自分の見方をどのくらい形作っていますか？", full_followups=("If weakly, which other source dominates?", "If strongly, which part would survive the loss of tasks?"), safety="work-identity-or-other-source"),
            prompt("return", "Going back", "戻るか", "Would you ever choose to do those tasks yourself again?", "いつか、その作業をまた自分ですることを選びますか？", ("If yes, what would bring you back?", "If no, where would meaning come from?"), full="Would you voluntarily return to the selected tasks even if AI continued to cover them?", full_ja="AIがその作業を続けてくれても、自分からまた取り組みますか？", full_followups=("If so, which non-financial value would draw you back?", "If not, which activity would provide meaning and contribution?"), safety="any-role-return-or-no-return"),
            prompt("flip", "What stays human", "人に残したいこと", "What task should people keep doing even if AI can do it?", "AIにできても、人が続けるべき作業は何ですか？", ("What human value would be lost?", "Could people and AI share it instead?"), full="Which task should remain meaningfully human even if automation becomes capable?", full_ja="自動化が可能になっても、どの作業は人が担う意味を残すべきですか？", full_followups=("Which relational or ethical value would disappear otherwise?", "Could a shared human-AI arrangement preserve it?"), safety="general-not-job-prophecy"),
        ],
    ),
    97: topic(
        slug="the-animal-your-friends-would-choose-for-you", title="The animal your friends would choose for you", ko="친구들이 나에게 골라 줄 동물", ja="自分を知る人が選びそうな動物",
        goal=("Let's use an animal comparison to explore how familiar or imagined observers see personality.", "身近な人または想像上の観察者が性格をどう見るか、動物の比較で考えましょう。"), article_title=("What an animal comparison can symbolize", "動物の比較が象徴するもの"),
        articles=[
            ("Animal comparisons turn personality into a quick picture.", "Animal comparisons compress a complicated personality into one memorable image.", "動物の比較は、性格をすぐ分かるイメージに変えます。", "動物の比較は、複雑な性格を一つの覚えやすいイメージにまとめます。"),
            ("To symbolize means to represent an idea or quality.", "To symbolize a trait is to stand for it through an image rather than describe it literally.", "象徴するとは、考えや特徴を表すことです。", "特徴を象徴するとは、文字どおり説明するのではなく、イメージを通してその特徴を表すことです。"),
            ("The same animal can symbolize different things to different people.", "An animal may represent loyalty in one context and dependence in another.", "同じ動物でも、人によって象徴することが違います。", "ある動物が一つの文脈では忠実さを、別の文脈では依存を表すことがあります。"),
            ("People who know us may notice habits we overlook.", "Familiar observers may recognize consistent habits that are invisible from inside our own routine.", "自分を知る人は、自分では見落とす習慣に気づくことがあります。", "身近な観察者は、自分の日課の中からは見えない一貫した習慣を認識することがあります。"),
            ("Not everyone has friends available for this question.", "The topic works with family, colleagues, classmates, a familiar public example, or an imagined observer; friendship is not required.", "この質問に答えるための友人がいるとは限りません。", "家族、同僚、クラスメート、公に知られた例、想像上の観察者でも話せるので、友人は必要ありません。"),
            ("Our own choice may differ because we value a different side of ourselves.", "Self-image may emphasize aspiration, while other people's choice reflects observed behaviour.", "自分の選択は、自分の別の面を大切にするので違うかもしれません。", "自己イメージは理想を強調し、ほかの人の選択は観察した行動を反映することがあります。"),
            ("The difference can be funny without being an insult.", "A useful comparison can reveal a mismatch without reducing a person to a fixed label.", "違いは、悪口でなくても面白く感じられます。", "役立つ比較は、人を固定したラベルにせずに、見方のずれを表せます。"),
            ("An animal we could never be shows where the comparison fails.", "Rejecting an animal clarifies which trait or stereotype feels fundamentally inaccurate.", "絶対に自分ではない動物から、比較の限界が分かります。", "ある動物を否定することで、どの特徴や固定観念が根本的に違うかが明確になります。"),
            ("Choosing an animal for someone else requires evidence.", "A fair comparison should follow real traits supplied by the person rather than a guess based on appearance.", "ほかの人に動物を選ぶには、根拠が必要です。", "公平な比較では、見た目の推測ではなく、その人が実際に示した特徴を使うべきです。"),
            ("The best comparison opens conversation instead of ending it.", "A good metaphor invites correction and explanation rather than claiming the final truth about a person.", "よい比較は会話を終わらせず、広げます。", "よい比喩は人について最終的な真実を主張せず、訂正や説明を招きます。"),
        ],
        prompts=[
            prompt("opening", "Their animal for you", "周りが選ぶ動物", BRIEF_OPENINGS[97], "あなたを知る人は、あなたにどの動物を選ぶと思いますか？", ("If no such person comes to mind, which imagined observer could make a fair guess?", "What trait would they notice first?"), full=BRIEF_OPENINGS[97], full_ja="あなたを知る人は、あなたにどの動物を選ぶと思いますか？", full_followups=("If no familiar observer comes to mind, which imagined or public perspective could support a fair guess?", "Which observed trait would drive the comparison?"), safety="familiar-imagined-or-no-observer"),
            prompt("agreement", "Your reaction", "その選択への反応", "If an animal was suggested, do you agree? If none was, what made the comparison difficult?", "動物が挙がったなら納得しますか。挙がらなかったなら、なぜ比較が難しかったのですか？", ("If you agree, which trait fits?", "If you disagree or had no animal, what does the comparison miss?"), full="If an animal comparison emerged, would you accept it? If none did, what prevented a fair comparison?", full_ja="動物の比較が挙がったなら、受け入れますか。挙がらなかったなら、公平な比較を難しくしたのは何ですか？", full_followups=("If you accept it, which behaviour supports it?", "If you reject it or had no comparison, which complexity did it fail to capture?"), safety="animal-or-no-comparison"),
            prompt("own-pick", "Your own animal", "自分で選ぶ動物", "Would you choose an animal for yourself, or choose none?", "自分に動物を選びますか。それとも、何も選びませんか？", ("If one fits, what does it symbolize for you?", "If none fits, what does every animal leave out?"), full="Would you select an animal as your own symbol, or reject the comparison?", full_ja="自分の象徴として動物を選びますか。それとも、その比較を断りますか？", full_followups=("If one fits, which quality does it symbolize?", "If none fits, which complexity defeats every single-animal metaphor?"), safety="self-choice-or-none"),
            prompt("difference", "Why the choices differ", "選択が違う理由", "Are your answer and the observer's answer different, the same, or both absent?", "自分と観察者の答えは違いますか、同じですか、それとも両方ともありませんか？", ("If different, what explains the gap?", "If the same or absent, what explains that result?"), full="Do the self-image and observer's comparison diverge, match, or remain unchosen?", full_ja="自分の見方と観察者の比較はずれますか、一致しますか、それともどちらも選ばれていませんか？", full_followups=("If they diverge, which visible behaviour or private intention explains the gap?", "If they match or remain unchosen, what explains that result?"), safety="difference-same-or-none"),
            prompt("never", "Not that animal", "絶対に違う動物", "What animal could you never be?", "自分には絶対に当てはまらない動物は何ですか？", ("Which trait makes it wrong?", "Could a different meaning of the animal change your answer?"), full="Which animal comparison would feel fundamentally inaccurate?", full_ja="どの動物の比較なら、根本的に自分と違うと感じますか？", full_followups=("Which associated trait creates the mismatch?", "Could another cultural meaning make the comparison more plausible?"), safety="rejected-comparison"),
            prompt("context", "A different setting", "別の場面", "Would another setting change the animal comparison—or would none fit anywhere?", "別の場面では動物の比較が変わりますか。それとも、どの場面でも当てはまりませんか？", ("If it changes, which behaviour changes the image?", "If none fits anywhere, which complexity remains?"), full="Would another setting produce a different comparison, the same one, or no fair animal comparison?", full_ja="別の場面なら、比較は変わりますか、同じですか、それとも公平な動物の比較はできませんか？", full_followups=("If it changes, which context-dependent behaviour alters the image?", "If it stays the same or absent, what explains that result?"), safety="different-same-or-no-comparison"),
            prompt("tutor-evidence", "Before choosing for me", "先生に選ぶ前に", "What would you need to know before choosing an animal for me?", "私に動物を選ぶ前に、何を知る必要がありますか？", ("Ask me for one or two real traits; after I answer, which animal fits them?", "What part of the comparison remains uncertain?"), full="Which evidence would you need before assigning an animal to me?", full_ja="私に動物を当てはめる前に、どんな根拠が必要ですか？", full_followups=("Ask me for one or two genuine traits; once I answer, which animal do they support?", "Which limit of the comparison should remain explicit?"), safety="tutor-supplies-traits-before-classification"),
            prompt("flip", "Beyond one animal", "一つの動物を超えて", "Why can one animal never describe a whole person?", "なぜ一つの動物だけでは、人全体を表せないのですか？", ("Which important quality gets left out?", "Would two animals be more honest?"), full="What does every single-animal metaphor leave out about a person?", full_ja="一つの動物の比喩は、人について何を必ず見落としますか？", full_followups=("Which contradiction cannot fit the label?", "Would combining two animals make the metaphor more accurate or merely more complicated?"), safety="anti-label-close"),
        ],
    ),
    98: topic(
        slug="growing-up-in-another-country", title="Growing up in another country", ko="다른 나라에서 자랐다면", ja="別の国で育っていたら",
        goal=("Let's imagine a different upbringing without assuming Japan, migration plans, or national stereotypes.", "日本、移住計画、国の固定観念を前提にせず、別の育った環境を想像しましょう。"), article_title=("How upbringing shapes possibilities", "育った環境が可能性を形作る方法"),
        articles=[
            ("Upbringing means the environment and experiences that shape someone while growing up.", "Upbringing includes the relationships, institutions, language, expectations, and material conditions that shape childhood.", "育った環境とは、成長中に人を形作る環境や経験です。", "upbringing には、子ども時代を形作る人間関係、制度、言語、期待、生活条件が含まれます。"),
            ("A country is not one single childhood.", "No country provides one uniform childhood across region, class, family, generation, or community.", "一つの国に、同じ子ども時代が一つだけあるわけではありません。", "どの国でも、地域、階層、家族、世代、共同体によって子ども時代は一様ではありません。"),
            ("The thought experiment needs a specific setting, not a stereotype.", "A useful counterfactual names a place and conditions without pretending to predict a national personality.", "この想像には、固定観念ではなく具体的な環境が必要です。", "役立つ反実仮想では、国民性を予測したふりをせず、場所と条件を具体的にします。"),
            ("Language could change how relationships and ideas are expressed.", "Growing up through another language could alter access, humour, memory, and social belonging.", "別の言語で育つと、人間関係や考えの表し方が変わるかもしれません。", "別の言語で育つと、機会、ユーモア、記憶、社会への所属感が変わる可能性があります。"),
            ("School systems can reward different skills and behaviour.", "Education systems distribute opportunity and define success in different, internally varied ways.", "学校制度によって、評価される能力や行動が違います。", "教育制度は、国内でも多様な形で機会を分け、成功を定義します。"),
            ("Family and community still matter inside any country.", "National context interacts with family, community, disability, wealth, and chance rather than replacing them.", "どの国でも、家族や地域の影響は残ります。", "国の背景は、家族、地域、障害、経済状況、偶然と関わり、置き換わるわけではありません。"),
            ("A different upbringing could change habits without changing every value.", "Some preferences might shift while temperament or central values remain recognizable.", "育った環境が違えば習慣は変わっても、すべての価値観が変わるとは限りません。", "好みが変わっても、気質や中心的な価値観は分かる形で残るかもしれません。"),
            ("Missing the place where we actually grew up can be complex.", "What someone would miss may be a person, language, food, season, routine, or nothing obvious.", "実際に育った場所を恋しく思う気持ちは、単純ではありません。", "恋しくなるものは、人、言語、食べ物、季節、日課、または特にないことかもしれません。"),
            ("Imagining another childhood is different from moving there now.", "A counterfactual upbringing does not imply a present desire or practical ability to migrate.", "別の子ども時代を想像することは、今移住することとは違います。", "別の育ち方を想像しても、今移住したいことや移住できることを意味しません。"),
            ("The exercise shows which parts of identity feel shaped and which feel chosen.", "The value of the question lies in separating circumstance, adaptation, chance, and deliberate choice.", "この想像から、自分のどの部分が環境で作られ、どの部分を選んだと感じるかが分かります。", "この問いの価値は、状況、適応、偶然、意識的な選択を分けて考えることにあります。"),
        ],
        prompts=[
            prompt("opening", "Another country", "別の国", BRIEF_OPENINGS[98], "同じ自分が、別の国で育っていたら。どこですか？", ("If no country comes to mind, which different setting would you imagine?", "What draws you to that setting rather than a stereotype?"), full=BRIEF_OPENINGS[98], full_ja="同じ自分が、別の国で育っていたら。どこですか？", full_followups=("If no country comes to mind, which contrasting upbringing would be revealing?", "Which specific condition attracts you rather than a national stereotype?"), safety="country-setting-or-none"),
            prompt("reason", "Why there", "そこを選ぶ理由", "Why would you choose that place or setting?", "なぜその場所、または環境を選びますか？", ("Which opportunity or experience matters?", "What do you not know enough about yet?"), full="Which concrete feature makes that place or setting worth imagining?", full_ja="どの具体的な特徴が、その場所や環境を想像する価値を生みますか？", full_followups=("Which opportunity, institution, language, or daily experience matters?", "Which uncertainty prevents a confident prediction?"), safety="specific-not-stereotyped"),
            prompt("difference", "A different you", "違う自分", "If you had grown up there, what might be different about you?", "もしそこで育っていたら、自分の何が違っていたと思いますか？", ("Which habit might change?", "Which value might stay the same?"), full="If you had grown up there, which part of your identity might have developed differently?", full_ja="もしそこで育っていたら、自分らしさのどの部分が違って育ったと思いますか？", full_followups=("Which habit or opportunity could plausibly shift?", "Which temperament or value might remain recognizable?"), safety="explicit-counterfactual"),
            prompt("miss", "What you would miss", "実際の育ちから恋しくなるもの", "What might you miss about where you actually grew up?", "実際に育った場所について、何が恋しくなりそうですか？", ("If nothing obvious, which familiar routine might still matter?", "Would you miss a person, place, language, or feeling?"), full="Which part of your actual upbringing might be hardest to lose?", full_ja="実際に育った環境のどの部分を失うのが最も難しそうですか？", full_followups=("If nothing obvious comes to mind, which ordinary familiarity might still matter?", "Would the loss concern relationship, place, language, routine, or belonging?"), safety="no-japan-assumption"),
            prompt("not-miss", "What you would not miss", "恋しくならないもの", "What part of your actual upbringing might you not miss?", "実際に育った環境のどの部分なら、恋しくならないかもしれませんか？", ("If none, what do you value about it?", "If something, what might replace it?"), full="Which element of your actual upbringing, if any, would you be relieved to leave behind?", full_ja="実際に育った環境の中で、手放せて安心するものがあるとすれば何ですか？", full_followups=("If none, which feature deserves appreciation?", "If one, which alternative could replace it?"), safety="critique-or-no-critique"),
            prompt("language", "Language and belonging", "言語と所属感", "Would that upbringing use the same language or another one, and how might that shape connection?", "その育った環境では同じ言語を使いますか、別の言語を使いますか。それは人とのつながり方をどう形作りそうですか？", ("If it were the same language, what else would shape belonging?", "If it were another language, what might become easier or harder to express?"), full="Would the imagined upbringing use the same language or another one, and how could that shape expression and belonging?", full_ja="想像した育った環境では同じ言語を使いますか、別の言語を使いますか。それは表現や所属感をどう形作り得ますか？", full_followups=("If the language were the same, which other social condition would shape belonging?", "If it were different, which meaning might become easier to access or harder to retain?"), safety="same-or-another-language"),
            prompt("move-now", "Growing up versus moving", "育つことと今移ること", "Would you actually want to move there now—or only imagine growing up there?", "実際に今そこへ移りたいですか。それとも、そこで育つことだけを想像したいですか？", ("If only imagined, what makes the present move different?", "If interested in moving, which non-private condition matters most?"), full="Does the imagined upbringing imply any present desire to move there?", full_ja="想像した育った環境は、今そこへ移りたい気持ちにもつながりますか？", full_followups=("If not, which difference separates childhood from present migration?", "If so, which general practical condition would matter most?"), safety="no-visa-health-or-migration-detail"),
            prompt("flip", "What stays yours", "変わらず自分のもの", "What part of you do you think would stay the same anywhere?", "どこで育っても、自分のどの部分は同じだと思いますか？", ("Why does that feel less shaped by place?", "Could another environment still change how it appears?"), full="Which part of your identity feels least dependent on where you were raised?", full_ja="自分らしさのどの部分が、育った場所に最も左右されないと感じますか？", full_followups=("Why does it seem more stable than circumstance?", "Could context still alter how that quality is expressed?"), safety="non-essentialist-close"),
        ],
    ),
    99: topic(
        slug="where-you-imagine-yourself-in-ten-years", title="Where you imagine yourself in ten years", ko="10년 뒤 상상하는 내 모습", ja="十年後に想像する自分",
        goal=("Let's build a flexible ten-year picture, including uncertainty, solitude, and no immediate plan.", "不確かさ、一人でいる可能性、すぐの計画がない場合も含めて、柔軟な十年後の姿を描きましょう。"), article_title=("A direction, not a prediction", "予測ではなく方向"),
        articles=[
            ("A ten-year picture is a direction, not a promise.", "A ten-year projection expresses a possible life direction rather than a prediction or commitment.", "十年後の姿は方向であり、約束ではありません。", "十年後の予想図は、予測や約束ではなく、あり得る人生の方向を表します。"),
            ("A life direction can exist without a detailed plan.", "Life direction names what feels worth moving toward even when the route remains unclear.", "人生の方向性は、詳しい計画がなくても持てます。", "life direction は、道筋が不明でも、どこへ進む価値を感じるかを示します。"),
            ("Some people see a clear room; others see only a feeling.", "A future image may be spatial and concrete, or it may consist only of values and atmosphere.", "具体的な場所を思い描く人もいれば、感覚だけを思い浮かべる人もいます。", "未来の像は具体的な場所の場合も、価値観や雰囲気だけの場合もあります。"),
            ("Not knowing where you will be is a complete answer.", "Genuine uncertainty is not a failure of imagination and should not be replaced with false certainty.", "どこにいるか分からないという答えも十分です。", "本当の不確かさは想像力の失敗ではなく、偽りの確信に置き換える必要はありません。"),
            ("Work is only one part of a future day.", "Paid work, study, care, rest, community, creativity, and ordinary routine can all organize a future day.", "仕事は未来の一日の一部にすぎません。", "有給の仕事、勉強、ケア、休息、地域、創作、普通の日課のどれも未来の一日を形作れます。"),
            ("Other people may be present, absent, or still unknown.", "A future picture need not assume a partner, family, colleagues, or any specific companion.", "周りに人がいる場合も、いない場合も、まだ分からない場合もあります。", "未来の像は、パートナー、家族、同僚、特定の同行者を前提にする必要はありません。"),
            ("Keeping something the same can be as important as changing it.", "Continuity can protect an identity, relationship, habit, or place that already works.", "何かを変えないことも、変えることと同じくらい大切です。", "継続することは、すでにうまくいく自分らしさ、関係、習慣、場所を守れます。"),
            ("Disappointment depends on values, not a perfect checklist.", "A future can diverge from the picture without becoming a failure, while one missing value may still matter deeply.", "失望するかどうかは、完璧なリストより価値観で決まります。", "未来が予想図と違っても失敗とは限りませんが、一つの大切な価値が欠けることは重大かもしれません。"),
            ("One action this year is optional, not proof of seriousness.", "A useful direction may suggest a present step, but uncertainty or rest can make no immediate action the honest answer.", "今年する一つの行動は任意で、本気の証明ではありません。", "方向から今の一歩が見える場合もありますが、不確かさや休息のため、今は何もしないのが正直な答えの場合もあります。"),
            ("The picture should be allowed to change as life changes.", "A flexible projection can guide choices without trapping the future self inside an outdated plan.", "生活が変われば、未来の姿も変えてよいのです。", "柔軟な予想図は、未来の自分を古い計画に閉じ込めずに、選択を導けます。"),
        ],
        prompts=[
            prompt("opening", "Ten years on", "十年後", BRIEF_OPENINGS[99], "同じ日付の十年後、どこに座っていますか？", ("If no place is clear, what feeling or value would you want around you?", "If a place appears, what makes it fit?"), full=BRIEF_OPENINGS[99], full_ja="同じ日付の十年後、どこに座っていますか？", full_followups=("If no setting is visible, which atmosphere or value would you want the day to have?", "If a setting is visible, which feature makes it meaningful?"), safety="clear-place-or-no-vision"),
            prompt("activity", "What you are doing", "していること", "What might you be doing in that future scene?", "その未来の場面で、何をしていそうですか？", ("If no activity is clear, what would you want the day to contain?", "Would it be paid work, study, care, rest, or something else?"), full="Which activity or purpose might organize that future day?", full_ja="どんな活動や目的が、その未来の一日を形作っていそうですか？", full_followups=("If no activity is clear, which quality would you want the day to have?", "Would its structure come from paid work, learning, care, rest, community, or another source?"), safety="activity-or-no-plan"),
            prompt("people", "Who is around", "周りにいる人", "Who, if anyone, is around you?", "周りに人がいるとすれば、誰ですか？", ("If someone is there, what kind of connection matters?", "If nobody is, what makes the scene comfortable or useful?"), full="Who, if anyone, shares that future scene?", full_ja="その未来の場面を一緒に過ごす人がいるとすれば、誰ですか？", full_followups=("If someone is present, which quality of the relationship matters?", "If no one is present, what gives the solitude meaning or ease?"), safety="companions-or-solitude"),
            prompt("same", "What stays the same", "変わらないこと", "Is there anything you would like to keep the same for ten years?", "十年間、変えずに保ちたいことはありますか？", ("If yes, why is it worth protecting?", "If nothing is clear, which uncertainty makes choosing difficult?"), full="Which part of your current life, if any, would you want to preserve?", full_ja="今の生活で残したい部分があるとすれば、どこですか？", full_followups=("If one is clear, which value makes that continuity important?", "If none is clear, which uncertainty prevents a choice?"), safety="continuity-or-no-answer"),
            prompt("disappoint", "What would disappoint you", "失望すること", "What missing part would disappoint you, if any?", "欠けていたら失望するものがあるとすれば、何ですか？", ("If one matters, which value is behind it?", "If none, what makes the picture flexible?"), full="Which absent value or condition, if any, would make the future disappointing?", full_ja="欠けていたら未来に失望する価値や条件があるとすれば、何ですか？", full_followups=("If one matters, why is it central rather than optional?", "If none does, which openness keeps the projection flexible?"), safety="disappointment-or-none"),
            prompt("direction", "Life direction", "人生の方向性", "Does the picture suggest a life direction, or is it still too unclear?", "その未来の姿は人生の方向性を示していますか。それとも、まだ不明確すぎますか？", ("If a direction appears, which value points that way?", "If none appears, what remains uncertain?"), full="Is a broader life direction visible beneath the details, or does genuine uncertainty remain?", full_ja="細かな内容の奥に大きな人生の方向性が見えますか。それとも、本当にまだ不確かですか？", full_followups=("If one is visible, which underlying value gives it force?", "If none is visible, which uncertainty should remain open?"), safety="direction-or-uncertainty"),
            prompt("this-year", "This year", "今年できること", "Is there one thing you want to do this year toward that direction—or toward making the picture clearer?", "その方向、または未来の姿をより明確にするため、今年したいことは一つありますか？", ("If there is a step, what makes it small enough to begin?", "If no action is right yet, what would need to become clearer first?"), full="Which action this year, if any, would support the direction or clarify the uncertainty?", full_ja="その方向を支える、または不確かさを明らかにするため、今年する行動があるとすれば何ですか？", full_followups=("If there is one, what makes it proportionate and realistic?", "If none is right yet, which uncertainty should resolve first?"), safety="action-or-no-action"),
            prompt("flip", "Changing the picture", "未来像を変えること", "If you have a ten-year picture, what would make you happily change it? If not, what might help one form?", "十年後の姿があるなら、何があれば喜んで変えますか。まだないなら、何があれば姿が見えてきそうですか？", ("For a picture, which new opportunity could matter more?", "For no picture, which experience or information could add clarity?"), full="What could justifiably overturn an existing projection, or help a still-unclear projection take shape?", full_ja="既にある予想図を変える十分な理由、またはまだ不明確な予想図を形作る助けになるものは何ですか？", full_followups=("For an existing projection, which opportunity could outweigh it?", "For an unclear projection, which experience or information could add definition?"), safety="picture-or-no-picture-close"),
        ],
    ),
    100: topic(
        slug="the-one-thing-you-would-save-in-a-fire", title="The one thing you would save in a fire", ko="불이 났을 때 구할 한 가지", ja="火事で持ち出す一つのもの",
        goal=("Everyone and every pet is already safe. Let's discuss one possible object—or leaving immediately—without re-entering a fire.", "人もペットもすでに安全です。火の中へ戻らず、一つの物、またはすぐ離れる選択について話しましょう。"), article_title=("Safety before possessions", "持ち物より安全"),
        articles=[
            ("In this scenario, every person and pet is already safe.", "The scenario begins only after every person and pet is safely outside.", "この想像では、人もペットもすでに安全です。", "この想像は、人もペットも全員安全に外へ出たあとから始まります。"),
            ("Nobody should re-enter a fire for an object.", "No possession justifies re-entering smoke or fire; emergency instructions take priority.", "物のために火の中へ戻ってはいけません。", "持ち物のために煙や火の中へ戻るべきではなく、緊急時の指示が最優先です。"),
            ("Leaving immediately with nothing is a valid answer.", "Immediate evacuation without retrieving anything is a complete and responsible choice.", "何も持たずにすぐ離れるのも正しい答えです。", "何も取りに行かず直ちに避難することは、十分で責任ある選択です。"),
            ("If one object is already within safe reach, the choice becomes meaningful.", "Only an object already on the safe exit route belongs in the thought experiment.", "安全に手が届く場所に一つ物がある場合だけ、選択を考えられます。", "安全な避難経路にすでにある物だけが、この思考実験の対象です。"),
            ("Irreplaceable means that something cannot truly be replaced.", "An irreplaceable object carries information, history, or meaning that no new copy can restore.", "かけがえのないとは、本当には置き換えられないことです。", "irreplaceable な物には、新しい物では戻せない情報、歴史、意味があります。"),
            ("Market price and personal value can point in opposite directions.", "The most expensive possession may matter less than a cheap object connected to memory or identity.", "市場の値段と個人的な価値は、反対になることがあります。", "最も高価な持ち物より、記憶や自分らしさと結びついた安い物のほうが大切な場合があります。"),
            ("Digital copies can make some records replaceable.", "Backups can protect photographs and documents, although the original object may still carry meaning.", "デジタルのコピーで、置き換えられる記録もあります。", "バックアップで写真や書類を守れますが、元の物に意味が残る場合もあります。"),
            ("Other people may save different things because their histories differ.", "A choice that looks strange from outside may be coherent once its personal history is known.", "人によって歴史が違うので、持ち出す物も違います。", "外から不思議に見える選択でも、その個人的な歴史を知れば筋が通る場合があります。"),
            ("Past loss can change what we protect now.", "Losing something before may increase care, or may teach that memory can survive without the object.", "過去に物を失った経験で、今守るものが変わる場合があります。", "以前何かを失った経験から、より大切に守ることも、物がなくても記憶は残ると学ぶこともあります。"),
            ("The safest lesson is preparation, not a faster rescue.", "Backups, inventories, alarms, and evacuation plans matter more than deciding what to retrieve during danger.", "いちばん安全な学びは、速く取りに行くことではなく準備です。", "危険なときに何を取りに行くかより、バックアップ、一覧、警報、避難計画のほうが重要です。"),
        ],
        prompts=[
            prompt("opening", "One thing", "一つの物", BRIEF_OPENINGS[100], "三十秒で一つ。何を持ち出しますか？", ("Everyone and every pet is already safe; if the safest action is to leave now, what makes that your answer?", "If one object is already on the exit route, why that one?"), full=BRIEF_OPENINGS[100], full_ja="三十秒で一つ。何を持ち出しますか？", full_followups=("With every person and pet already safe, if immediate evacuation is the only safe action, why is taking nothing the right answer?", "If one object is already within safe reach on the exit route, why would it matter most?"), safety="people-pets-safe-no-reentry"),
            prompt("reason", "Why that one", "それを選ぶ理由", "Why would that object be irreplaceable—or why would taking nothing be safest?", "なぜその物はかけがえがないのですか。それとも、なぜ何も持ち出さないことが最も安全ですか？", ("For an object, is its value practical, historical, or emotional?", "For taking nothing, which safety principle decides the answer?"), full="What makes an object irreplaceable, or makes immediate departure without one the only defensible choice?", full_ja="何が物をかけがえのないものにしますか。それとも、なぜ何も持ち出さずすぐ離れることだけが妥当な選択ですか？", full_followups=("For an object, does its value come from information, history, identity, or use?", "For taking nothing, which safety principle makes the decision defensible?"), safety="object-or-immediate-leave"),
            prompt("surprise", "Your own answer", "自分の答えへの驚き", "What, if anything, surprises you about your answer?", "自分の答えについて、意外に感じることがあるとすれば何ですか？", ("If nothing surprises you, what value made it predictable?", "If something does, what did you expect to choose?"), full="Which part of your own response, if any, is unexpected?", full_ja="自分の答えのどの部分が、意外だと感じますか？", full_followups=("If none, which stable value made the answer predictable?", "If something is unexpected, which alternative had you assumed would win?"), safety="surprise-or-none"),
            prompt("others", "A different choice", "ほかの人と違う選択", "What might another person take even if you would take nothing?", "自分は何も持ち出さない場合でも、ほかの人なら何を持ち出すかもしれませんか？", ("Why might it matter to them?", "Why would you still leave it?"), full="Which commonly valued possession might someone else take even if you would leave with nothing?", full_ja="自分は何も持ち出さなくても、ほかの人ならどの一般的に大切な持ち物を持ち出すかもしれませんか？", full_followups=("Which history could make it important to someone else?", "Which safety or value makes leaving it coherent for you?"), safety="general-no-owned-object-required"),
            prompt("loss", "A past loss", "過去に失った物", "Have you ever lost something important—or is there no example you want to discuss?", "大切な物を失ったことがありますか。それとも、話したい例はありませんか？", ("If yes, what made the loss matter?", "If no example, what kind of loss is generally hardest?"), full="Have you experienced the loss of an important object, or would you rather discuss loss generally?", full_ja="大切な物を失った経験がありますか。それとも、物を失うことを一般的に話しますか？", full_followups=("If there is an example, which meaning survived the object?", "If speaking generally, which type of object is hardest to replace?"), safety="personal-general-or-no-history"),
            prompt("lesson", "What loss teaches", "失うことから学ぶこと", "What can losing an object teach us?", "物を失うことから、何を学べますか？", ("Does it change what we protect?", "Can a memory remain without the object?"), full="What can the loss of a possession reveal about value and memory?", full_ja="持ち物を失うことから、価値や記憶について何が分かりますか？", full_followups=("How might it change later preparation?", "Under what condition can meaning survive without the original object?"), safety="general-reflection"),
            prompt("prepare", "Preparing safely", "安全な準備", "If you chose an object, how could you protect it beforehand? If you chose nothing, what general preparation still matters?", "物を選んだなら、事前にどう守れますか。何も選ばないなら、どんな一般的な準備が大切ですか？", ("For an object, would a backup, list, or safer storage help?", "For taking nothing, which evacuation preparation matters most?"), full="How could an object be protected beforehand, or which general preparation supports the choice to retrieve nothing?", full_ja="物は事前にどう守れますか。それとも、何も取りに行かない選択を支える一般的な準備は何ですか？", full_followups=("For an object, would duplication, documentation, or storage help most?", "For taking nothing, which evacuation step is realistic now?"), safety="object-or-general-preparation"),
            prompt("flip", "What cannot burn", "燃えないもの", "What important part of life cannot be saved or destroyed as an object?", "物として救ったり失ったりできない、人生の大切なものは何ですか？", ("How is it protected instead?", "Can an object still help us remember it?"), full="Which valuable part of life exists beyond any possession?", full_ja="どんな大切なものが、持ち物を超えて存在しますか？", full_followups=("What kind of care protects it?", "How can an object support it without becoming the value itself?"), safety="non-object-close"),
        ],
    ),
}


# The review layer below is the effective curriculum source.  Every prompt must
# work when the tutor skips directly to its page, so no question may depend on a
# prior selection or ask the learner to choose a defensive answer route first.
GOAL_REVISIONS = {
    89: ("Let's imagine how a large lottery win could change everyday life.", "宝くじで大当たりしたら、日常がどう変わるか想像しましょう。"),
    90: ("Let's choose what would matter most on a desert island.", "無人島で最も大切になるものを選びましょう。"),
    91: ("Let's explore what one day in another life could teach us.", "別の人生を一日体験すると何が分かるか考えましょう。"),
    92: ("Let's choose a superpower and examine its real consequences.", "超能力を一つ選び、実際にどんな結果が生まれるか考えましょう。"),
    93: ("Let's test what makes one food enjoyable over time.", "一つの食べ物を長く楽しめる条件について話しましょう。"),
    94: ("Let's choose one free service and explore how life would change.", "一つのサービスを無料にして、生活がどう変わるか考えましょう。"),
    95: ("Let's explore what a week with less phone use would change.", "携帯電話を減らす一週間で何が変わるか考えましょう。"),
    96: ("Let's imagine how we would use our time if AI handled routine tasks.", "AIが日常の作業をしたら、時間をどう使うか想像しましょう。"),
    97: ("Let's use animal comparisons to explore personality.", "動物の比較を使って、性格について話しましょう。"),
    98: ("Let's imagine how a different upbringing could shape a person.", "別の環境で育つと、人がどう変わるか想像しましょう。"),
    99: ("Let's imagine an ordinary day ten years from now.", "十年後の普通の一日を想像しましょう。"),
    100: ("Let's talk about possessions, memory, and safe preparation.", "持ち物、記憶、安全な備えについて話しましょう。"),
}
for _topic_no, _goal in GOAL_REVISIONS.items():
    TOPICS[_topic_no]["goal"] = _goal


ARTICLE_REVISIONS = {
    (93, 1): ("Choosing one food forever would remove every other source of variety.", "A one-food thought experiment removes choice and makes repetition the central problem.", "一つの食べ物を永遠に選ぶと、ほかのすべての変化がなくなります。", "一つの食べ物だけという想像では、選択肢がなくなり、繰り返しが中心の問題になります。"),
    (93, 9): ("Dietary boundaries change which food choices are realistic.", "Medical, religious, sensory, and ethical dietary boundaries shape which food choices are sustainable.", "食事上の制限によって、現実的に選べる食べ物は変わります。", "医療、宗教、感覚、倫理上の食事制限によって、続けられる食べ物の選択は変わります。"),
    (94, 9): ("Free access can reveal whether scarcity created the original desire.", "Permanent access can reveal whether genuine interest or scarcity created the original desire.", "いつでも無料で使えると、もともとの欲求が希少性から生まれたのか分かることがあります。", "永久に利用できると、本当の関心と希少性のどちらが、もともとの欲求を生んだのか分かることがあります。"),
    (95, 1): ("A digital detox means choosing a period with less optional device use.", "A digital detox is a deliberate period in which discretionary digital-device use is reduced.", "デジタルデトックスとは、任意のデジタル機器の利用を減らす期間を選ぶことです。", "デジタルデトックスとは、自由に減らせるデジタル機器の利用を意識的に減らす期間です。"),
    (95, 9): ("Time offline can reveal which phone functions are truly important.", "A period offline can distinguish essential access from convenient or habitual use.", "携帯電話を使わない時間があると、本当に大切な機能が分かります。", "オフラインの時間を過ごすと、必要な利用と、便利さや習慣による利用を区別できます。"),
    (96, 1): ("In this scenario, AI handles routine tasks while resources remain stable.", "The thought experiment keeps resources stable while AI performs routine tasks, creating time without an immediate financial penalty.", "この想像では、生活の条件が安定したまま、AIが日常の作業を行います。", "この想像では、生活の条件を安定させたままAIが日常の作業を行い、すぐに経済的な不利益を受けずに時間が生まれます。"),
    (96, 2): ("Daily roles include paid work, study, care, and unpaid contribution.", "The structure provided by a role may come from employment, study, care, domestic work, or community contribution.", "日々の役割には、有給の仕事、勉強、ケア、無給の貢献があります。", "役割が生む生活の形は、雇用、勉強、ケア、家事、地域への貢献から得られることがあります。"),
    (97, 5): ("Family, classmates, colleagues, and other observers may notice different traits.", "Different observers may emphasize different traits because they see a person in different settings.", "家族、同級生、同僚など、見る人によって気づく特徴は異なります。", "人を見る場面が異なるため、観察者によって重視する特徴も変わります。"),
    (98, 9): ("Growing up abroad would shape a person differently from moving abroad as an adult.", "A childhood abroad would shape language, memory, and identity differently from a migration decision made later in life.", "海外で育つことは、大人になってから海外へ移ることとは違う形で人をつくります。", "海外で過ごす子ども時代は、後の人生で移住を決めることとは異なる形で、言語、記憶、アイデンティティを形作ります。"),
    (99, 3): ("A future picture can begin with a place or with the feeling of the day.", "A future image may take shape through a concrete setting, an atmosphere, or the values present in an ordinary day.", "将来のイメージは、場所から始まることも、一日の気持ちから始まることもあります。", "将来のイメージは、具体的な場所、雰囲気、または普通の一日にある価値観から形になることがあります。"),
    (99, 4): ("Uncertainty can show which values matter before the details are clear.", "Uncertainty can make underlying values more visible even when the setting and route remain undefined.", "細かいことが決まっていなくても、不確かさから大切な価値観が見えることがあります。", "場所や道筋が決まっていなくても、不確かさによって基本的な価値観がよりはっきり見えることがあります。"),
    (99, 6): ("The amount of company and solitude changes the shape of a future day.", "The balance of connection and solitude influences how a future ordinary day feels and functions.", "人と過ごす時間と一人の時間の量で、将来の一日の形は変わります。", "人とのつながりと一人の時間のバランスは、将来の普通の一日の感じ方や過ごし方に影響します。"),
    (99, 9): ("A small experiment this year can test a possible future direction.", "A proportionate experiment can test a possible direction without turning a projection into a fixed commitment.", "今年、小さく試してみると、将来の方向を確かめられます。", "無理のない試みをすると、将来のイメージを固定した約束にせず、可能な方向を確かめられます。"),
    (100, 3): ("No possession is worth delaying a safe evacuation.", "Immediate evacuation takes priority over retrieving even an irreplaceable possession.", "どんな持ち物も、安全な避難を遅らせるほど大切ではありません。", "かけがえのない持ち物であっても、取りに行くことより、すぐ避難することが優先です。"),
}
for (_topic_no, _row_no), _row in ARTICLE_REVISIONS.items():
    TOPICS[_topic_no]["articles"][_row_no - 1] = _row


MAIN_REVISIONS = {
    (89, 1): ("Imagine you win a large lottery prize tomorrow. What would you do first?", "明日、宝くじで大当たりしたと想像してください。最初に何をしますか？", "Imagine receiving a life-changing lottery prize tomorrow. Which first decision would matter most?", "明日、人生を変えるほどの宝くじに当たったと想像してください。最初のどの決断が最も重要ですか？"),
    (89, 2): ("What should someone consider before making the first decision after a lottery win?", "宝くじに当たった後、最初の決断をする前に何を考えるべきですか？", "Which priority should guide the first decision after an unexpected financial windfall?", "予想外の大金を得た後、最初の決断を導くべき優先事項は何ですか？"),
    (90, 1): ("Which three useful objects would you take to a desert island?", "無人島に持っていく役立つ物を三つ選ぶとしたら何ですか？", "Which three objects would give you the best chance of managing life on a desert island?", "無人島で暮らすために最も役立つ三つの物は何ですか？"),
    (90, 2): ("Which need matters most when choosing objects for a desert island?", "無人島に持っていく物を選ぶとき、どの必要が最も大切ですか？", "Which underlying need should determine a desert-island packing list?", "無人島への持ち物リストを決めるべき基本的な必要は何ですか？"),
    (90, 3): ("Which object would be hardest to leave out of a three-object list?", "三つの物のリストから外すのが最も難しい物は何ですか？", "Which object would compete most strongly for the final place on a three-item list?", "三つの持ち物の最後の一枠を最も強く争う物は何ですか？"),
    (90, 6): ("What would you need to know about an island before choosing what to take?", "持っていく物を選ぶ前に、その島について何を知る必要がありますか？", "Which unknown condition on a desert island would most change what you packed?", "無人島のどの未知の条件が、持ち物を最も大きく変えますか？"),
    (90, 7): ("Would one companion make island life easier or more complicated?", "一人の仲間がいると、島での生活は楽になりますか、それとも複雑になりますか？", "How would one companion change the risks and responsibilities of island life?", "一人の仲間がいることで、島での危険と責任はどう変わりますか？"),
    (90, 8): ("Which useful island object would lose most of its value after returning home?", "島では役立っても、家に戻ると最も価値が下がる物は何ですか？", "Which survival object would have the lowest value once ordinary life resumed?", "普通の生活に戻った後、最も価値が低くなるサバイバル用品は何ですか？"),
    (91, 1): ("Whose daily life would you be curious to experience for one day?", "誰の日常生活を一日体験してみたいですか？", "Which person's or role's daily life would be most revealing to experience for one day?", "どの人、または役割の日常を一日体験すると、最も多くのことが分かりそうですか？"),
    (91, 2): ("What can make another person's daily life worth experiencing for one day?", "別の人の日常を一日体験する価値が生まれるのは何ですか？", "Which feature can make another person's or role's daily life especially instructive?", "別の人や役割の日常を特に学びの多いものにする特徴は何ですか？"),
    (91, 3): ("What would be the best use of the first hour in another person's life?", "別の人の人生を体験する最初の一時間を、どう使うのがよいですか？", "How should someone use the first hour of a one-day life exchange?", "一日だけ人生を入れ替えたとき、最初の一時間をどう使うべきですか？"),
    (91, 4): ("What question could one day in another life help answer?", "別の人生を一日体験すると、どんな疑問の答えが分かりますか？", "Which question could a one-day exchange answer better than outside observation?", "一日の人生交換によって、外から見るよりよく答えられる疑問は何ですか？"),
    (91, 5): ("What part of another person's daily life might be harder than it looks?", "別の人の日常で、外から見るより大変そうな部分は何ですか？", "Which hidden constraint could make an apparently attractive life difficult?", "一見魅力的な生活を難しくする、見えない制約は何ですか？"),
    (91, 6): ("Which lesson from a one-day life exchange would be appropriate to share afterward?", "一日の人生交換から得たどんな学びなら、その後、話してもよいですか？", "Which insight from a one-day exchange could be shared without violating privacy?", "一日の人生交換で得たどんな気づきなら、プライバシーを侵さずに共有できますか？"),
    (91, 7): ("What might make someone value their own ordinary life after a one-day exchange?", "一日の人生交換の後、自分の普通の生活を大切に感じるのはどんなことですか？", "Which ordinary feature of one's own life might gain value after a one-day exchange?", "一日の人生交換の後、自分の生活のどんな普通の特徴が大切に感じられそうですか？"),
    (91, 8): ("What could another person learn by experiencing one ordinary day in your life?", "別の人があなたの普通の一日を体験すると、何を学べますか？", "Which assumption might someone revise after experiencing one ordinary day in your life?", "あなたの普通の一日を体験すると、どんな思い込みを見直すかもしれませんか？"),
    (92, 1): ("Which superpower would make ordinary life most interesting?", "どの超能力が普通の生活を最も面白くしますか？", "Which superpower would create the most valuable change in ordinary life?", "どの超能力が普通の生活に最も価値のある変化をもたらしますか？"),
    (92, 2): ("What would be a responsible first use of a superpower?", "超能力を最初に責任を持って使うなら、何をしますか？", "Which first use would reveal whether a superpower could be handled responsibly?", "どんな最初の使い方なら、超能力を責任を持って扱えるか分かりますか？"),
    (92, 3): ("When should someone keep a superpower secret?", "超能力はどんなときに秘密にしておくべきですか？", "Which risks could justify keeping a superpower undisclosed?", "どんな危険があれば、超能力を公表しないことが正当化されますか？"),
    (92, 4): ("Which downside could make a useful superpower not worth having?", "役立つ超能力でも、持つ価値がなくなる欠点は何ですか？", "Which unintended consequence could outweigh a superpower's apparent benefit?", "どんな予期しない結果が、超能力の見かけの利点を上回りますか？"),
    (92, 7): ("What one rule should govern the use of any superpower?", "どんな超能力にも必要な一つのルールは何ですか？", "Which principle should govern the possession and use of extraordinary power?", "特別な力を持ち、使うことを導くべき原則は何ですか？"),
    (93, 1): ("Which food would be hardest for you to get tired of?", "どの食べ物なら、最も飽きにくいですか？", "Which food offers enough variety to remain enjoyable for the longest time?", "どの食べ物なら、最も長く楽しめるだけの変化がありますか？"),
    (93, 2): ("How does repetition change the enjoyment of a favourite food?", "同じ食べ物を繰り返すと、好きな食べ物の楽しさはどう変わりますか？", "What can make someone get sick of a favourite food after repeated exposure?", "好きな食べ物でも、繰り返し食べると飽きてしまうのはなぜですか？"),
    (93, 3): ("Which two foods would be the closest rivals for a long-term choice?", "長期的な選択で、最も競い合う二つの食べ物は何ですか？", "Which two foods would compete most strongly as sustainable long-term choices?", "長期的に続けられる選択として、最も強く競い合う二つの食べ物は何ですか？"),
    (93, 6): ("Would a healthy but less exciting food be a better long-term choice?", "健康的でもあまり刺激のない食べ物のほうが、長期的にはよい選択ですか？", "Could nutritional balance outweigh enjoyment in a long-term food choice?", "長期的な食べ物の選択では、栄養のバランスが楽しさより重要になり得ますか？"),
    (93, 7): ("How often would someone need a chance to change a long-term food choice?", "長期的な食べ物の選択を、どのくらいの頻度で変えられる必要がありますか？", "What interval for revising a permanent food choice would make the thought experiment tolerable?", "永久の食べ物の選択を見直せる間隔は、どのくらいならこの想像を受け入れられますか？"),
    (94, 1): ("If one everyday service were free for life, which would you choose?", "日常のサービスを一つ一生無料にできるなら、何を選びますか？", "Which service would create the greatest lifetime value if it were permanently free?", "どのサービスが永久に無料なら、生涯で最も大きな価値を生みますか？"),
    (94, 2): ("How often would a free service need to be used to make it valuable?", "無料のサービスは、どのくらい使えば価値がありますか？", "How much actual use would justify choosing one permanently free service?", "一つのサービスを永久に無料にする選択は、実際にどのくらい使えば正当化されますか？"),
    (94, 3): ("How could one free service change an ordinary week?", "一つの無料サービスで、普通の一週間はどう変わりますか？", "Which part of an ordinary week could permanent free access change most?", "永久に無料で利用できると、普通の一週間のどの部分が最も変わりますか？"),
    (94, 4): ("How could other people benefit from one person's free service?", "一人の無料サービスから、ほかの人はどう恩恵を受けられますか？", "When can non-transferable free access still create value for other people?", "譲渡できない無料の利用権でも、どんなときにほかの人へ価値を生みますか？"),
    (94, 5): ("Which boring service would be the most sensible one to make free?", "地味でも、無料にするのが最も賢いサービスは何ですか？", "Which unexciting service would offer the strongest practical lifetime return?", "どの地味なサービスが、生涯で最も大きな実用的利益をもたらしますか？"),
    (94, 6): ("When would reselling free access be fair or unfair?", "無料の利用権を転売することは、どんなときに公平、または不公平ですか？", "When would it be legitimate to resell access to a free service?", "無料サービスの利用権を転売することが正当になるのは、どんなときですか？"),
    (94, 7): ("What hidden costs can remain when a service is free?", "サービスが無料でも、どんな見えない負担が残りますか？", "Which non-financial costs can survive after a service becomes free?", "サービスが無料になっても残る、金銭以外の負担は何ですか？"),
    (94, 8): ("What would make a paid service better than a free alternative?", "有料のサービスが無料の代わりよりよくなるのは何ですか？", "Which added value could justify rejecting a free alternative?", "どんな追加価値があれば、無料の代わりを選ばないことが正当化されますか？"),
}
for (_topic_no, _prompt_no), (_a, _a_ja, _f, _f_ja) in MAIN_REVISIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible=_a, accessible_ja=_a_ja, full=_f, full_ja=_f_ja
    )

MORE_MAIN_REVISIONS = {
    (95, 1): ("Which part of a week with no optional phone use would be hardest?", "携帯電話の任意の利用をやめた一週間で、最も難しい部分は何ですか？", "Which challenge would define a week without discretionary phone use?", "携帯電話の自由に減らせる利用をやめた一週間では、どんな課題が中心になりますか？"),
    (95, 2): ("Which daily routine would be most disrupted by less phone use?", "携帯電話の利用を減らすと、どの日課が最も影響を受けますか？", "Which routine or system is most dependent on discretionary phone access?", "どの日課や仕組みが、携帯電話の任意の利用に最も依存していますか？"),
    (95, 3): ("Which useful phone function would be hardest to replace for a week?", "一週間、代わりを用意するのが最も難しい携帯電話の機能は何ですか？", "Which function, connection, or reassurance would be hardest to replace during a reduced-use week?", "利用を減らす一週間で、代わりを用意するのが最も難しい機能、つながり、安心は何ですか？"),
    (95, 5): ("When is the easiest time to put a phone away for a while?", "しばらく携帯電話を置いておくのに、最も簡単な時間はいつですか？", "Which setting makes a deliberate break from optional phone use most realistic?", "携帯電話の任意の利用を意識的に休むことが、最も現実的になる場面はどこですか？"),
    (95, 6): ("What support would make a reduced-phone week safe and practical?", "携帯電話を減らす一週間を安全で現実的にするには、どんな支えが必要ですか？", "Which tools, access arrangements, and boundaries would make a reduced-use experiment responsible?", "利用を減らす試みを責任あるものにするには、どんな道具、利用環境、境界が必要ですか？"),
    (95, 7): ("Which phone function should remain available during a reduced-use week?", "携帯電話の利用を減らす一週間でも、どの機能は使えるようにしておくべきですか？", "Which phone function should remain available during a deliberately reduced-use week?", "携帯電話の利用を意識的に減らす一週間でも、どの機能は使えるようにしておくべきですか？"),
    (95, 8): ("Which phone habit would be most useful to redesign?", "どの携帯電話の習慣を見直すと、最も役立ちますか？", "Which discretionary phone habit offers the greatest opportunity for sustainable change?", "携帯電話の自由に減らせる習慣のうち、持続的な変化につながる可能性が最も高いものは何ですか？"),
    (96, 1): ("If AI handled all your usual tasks, how would you use the free time?", "AIが普段の作業をすべてしたら、空いた時間をどう使いますか？", "If AI handled every routine task while resources stayed stable, what would give the new time direction?", "AIがすべての日常作業を行い、生活の条件が安定したままなら、新しい時間に方向を与えるものは何ですか？"),
    (96, 2): ("How might three months of extra unstructured time change a person?", "予定のない自由な時間が三か月続くと、人はどう変わりますか？", "How could three months of unstructured time affect motivation, routine, and well-being?", "予定のない時間が三か月続くと、意欲、日課、幸福にどう影響しますか？"),
    (96, 3): ("Should people tell others when AI handles most of their tasks?", "AIがほとんどの作業を行うとき、周りに伝えるべきですか？", "When should someone disclose that AI performs most of a role's tasks?", "AIが役割のほとんどの作業を行うことを、どんなときに公表すべきですか？"),
    (96, 5): ("Which self-chosen project could give unexpected free time direction?", "予想外に空いた時間に方向を与える、自分で選ぶプロジェクトは何ですか？", "Which self-directed project could replace the structure once supplied by routine tasks?", "日常の作業が与えていた生活の形を、どんな自主的なプロジェクトが代わりに作れますか？"),
    (96, 7): ("Which tasks might people still choose to do even when AI can handle them?", "AIができても、人が自分で続けたい作業は何ですか？", "Which tasks retain enough non-financial value for people to perform them voluntarily?", "どんな作業なら、金銭以外の価値が十分にあり、人が自ら続けますか？"),
    (97, 1): ("Which animal best represents your personality?", "どの動物があなたの性格を最もよく表しますか？", "Which animal metaphor captures one important part of your personality?", "どの動物の比喩が、あなたの性格の大切な一面を表しますか？"),
    (97, 2): ("Which personality trait is hardest to capture with an animal comparison?", "動物の比較で表すのが最も難しい性格の特徴は何ですか？", "Which complexity in a person's character resists a simple animal metaphor?", "人の性格のどんな複雑さが、単純な動物の比喩では表せませんか？"),
    (97, 4): ("Why might a person's animal choice differ from an observer's choice?", "本人が選ぶ動物と、周りが選ぶ動物が違うのはなぜですか？", "What can a gap between self-image and an observer's animal metaphor reveal?", "自己像と観察者の動物の比喩の違いから、何が分かりますか？"),
    (97, 6): ("How can the same person seem like different animals in different settings?", "同じ人が、場面によって違う動物のように見えるのはなぜですか？", "How can context produce different animal metaphors for the same person?", "状況によって、同じ人に異なる動物の比喩が生まれるのはなぜですか？"),
    (97, 7): ("I'll share three real traits about myself. Which animal do they suggest?", "私が自分の本当の特徴を三つ話します。どの動物が合いそうですか？", "I'll share three concrete traits from my life. Which animal metaphor fits them best?", "私の生活から具体的な特徴を三つ話します。どの動物の比喩が最も合いますか？"),
    (98, 1): ("Which country would offer the most interesting different upbringing?", "どの国で育つと、最も興味深い別の成長環境になりますか？", "Which country or setting would provide the most revealing contrast in upbringing?", "どの国や環境なら、育った環境の違いを最もよく考えられますか？"),
    (98, 2): ("Which feature makes a different place interesting for childhood?", "別の場所で子ども時代を過ごすことを面白くする特徴は何ですか？", "Which concrete condition makes an alternative upbringing worth examining?", "別の育った環境を考える価値が生まれる具体的な条件は何ですか？"),
    (98, 3): ("How can growing up in another country shape a person's identity?", "別の国で育つと、人のアイデンティティはどう形作られますか？", "Which parts of identity are most likely to develop differently across upbringings?", "育った環境が違うと、アイデンティティのどの部分が最も変わりやすいですか？"),
    (98, 6): ("How can the language of childhood shape expression and belonging?", "子ども時代の言語は、表現や所属感をどう形作りますか？", "How does the language of upbringing influence emotional expression and belonging?", "育ったときの言語は、感情表現と所属感にどう影響しますか？"),
    (98, 7): ("Why can imagining a childhood abroad feel different from moving abroad now?", "海外で育つ想像と、今海外へ移ることが違って感じられるのはなぜですか？", "Which differences separate a counterfactual upbringing from a present migration decision?", "別の国で育ったという反実仮想と、現在の移住の決定を分ける違いは何ですか？"),
    (99, 1): ("What would an ideal ordinary day look like ten years from now?", "十年後の理想的な普通の一日は、どんな一日ですか？", "Which features would define a satisfying ordinary day ten years from now?", "十年後の満足できる普通の一日を決める特徴は何ですか？"),
    (99, 2): ("Which activity or purpose could organize an ordinary future day?", "将来の普通の一日を形作る活動や目的は何ですか？", "Which purpose could give a future ordinary day structure and meaning?", "どんな目的が、将来の普通の一日に形と意味を与えますか？"),
    (99, 3): ("What balance of company and solitude would make a future day comfortable?", "将来の一日を快適にする、人との時間と一人の時間のバランスはどのようなものですか？", "Which balance between connection and solitude would support a satisfying future life?", "どんなつながりと一人の時間のバランスが、満足できる将来の生活を支えますか？"),
    (99, 6): ("What can reveal a broader life direction even when details are unclear?", "細かいことが不明でも、人生の大きな方向を示すものは何ですか？", "Which underlying values can reveal direction when a ten-year projection remains uncertain?", "十年後の予想が不確かでも、どんな基本的な価値観が方向を示しますか？"),
    (99, 7): ("What small action this year could make a future direction clearer?", "今年どんな小さな行動をすると、将来の方向が明確になりますか？", "Which proportionate action this year could test or clarify a possible future direction?", "今年どんな適切な行動をすると、将来の方向を試したり明確にしたりできますか？"),
    (99, 8): ("What new opportunity could make someone happily change a ten-year plan?", "どんな新しい機会があれば、十年計画を喜んで変えられますか？", "Which new evidence or opportunity could justifiably overturn a ten-year projection?", "どんな新しい根拠や機会があれば、十年後の予想を正当に変えられますか？"),
    (100, 1): ("Once everyone is safe, which possession would be hardest to lose?", "全員が安全になった後、失うのが最もつらい持ち物は何ですか？", "After every person and pet is safe, which possession would carry the greatest irreplaceable value?", "人もペットも全員安全になった後、どの持ち物が最もかけがえのない価値を持ちますか？"),
    (100, 2): ("What can make one possession feel irreplaceable?", "一つの持ち物が、かけがえのないものに感じられるのはなぜですか？", "Which forms of memory or meaning can make a possession irreplaceable?", "どんな記憶や意味が、持ち物をかけがえのないものにしますか？"),
    (100, 3): ("Which possession do people often value more than expected?", "人が予想以上に大切にすることが多い持ち物は何ですか？", "Which category of possession can reveal an unexpected priority?", "どんな種類の持ち物が、意外な優先事項を示しますか？"),
    (100, 5): ("Why can losing an ordinary object feel deeply important?", "普通の物を失っても、とても大切に感じられるのはなぜですか？", "How can the loss of an ordinary possession affect identity or memory?", "普通の持ち物を失うことが、アイデンティティや記憶にどう影響しますか？"),
    (100, 7): ("How can people protect important possessions before an emergency?", "緊急事態の前に、大切な持ち物をどう守れますか？", "Which preparation can protect irreplaceable information or possessions without delaying evacuation?", "避難を遅らせずに、かけがえのない情報や持ち物を守るには、どんな備えができますか？"),
}
for (_topic_no, _prompt_no), (_a, _a_ja, _f, _f_ja) in MORE_MAIN_REVISIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible=_a, accessible_ja=_a_ja, full=_f, full_ja=_f_ja
    )


def _clean_probe(probe: str) -> str:
    """Turn branch instructions into standalone optional tutor probes."""
    probe = re.sub(
        r"^(?:If|For|With) .+, ((?:what|which|who|how|why|when|where|does|do|is|are|would|could|can).*)$",
        r"\1",
        probe,
        flags=re.IGNORECASE,
    )
    probe = re.sub(
        r"^(?:A fictional, public, or anonymous person) (?:is fine|is enough);\s*",
        "",
        probe,
        flags=re.IGNORECASE,
    )
    return probe[:1].upper() + probe[1:]


for _topic in TOPICS.values():
    for _item in _topic["prompts"]:
        for _variant in VARIANTS:
            _key = f"{_variant}_followups"
            _item[_key] = tuple(_clean_probe(value) for value in _item[_key][:2])
        _item["safety"] = "standalone-hypothetical-or-opinion"


# These probes were read as conversation, not merely pattern-checked.  They are
# deliberately tied to the visible question on their own page and do not ask the
# learner to choose an answer route before the tutor can continue.
FOLLOWUP_REVISIONS = {
    (89, 3): (
        ("Who would have a practical reason to know?", "What benefit could privacy provide?"),
        ("Who would have a legitimate reason to know?", "Which consequence could careful disclosure prevent?"),
    ),
    (90, 2): (
        ("Which object would meet that need best?", "Which need would come next?"),
        ("Which object would address that need most reliably?", "Which secondary need should follow?"),
    ),
    (90, 3): (
        ("What would that object add to the list?", "Which trade-off would decide its place?"),
        ("Which capability would that object add?", "Which trade-off should determine the final place?"),
    ),
    (90, 5): (
        ("Why would that object still matter?", "Which practical need could keep it off a three-item list?"),
        ("Which unmet need makes that object memorable?", "Which practical priority could keep it outside a three-item limit?"),
    ),
    (91, 1): (
        ("Which part of that day would you most want to see?", "What might surprise you about the routine?"),
        ("Which part of that daily life would be most revealing?", "Which assumption might the experience challenge?"),
    ),
    (91, 6): (
        ("How could you describe the lesson without sharing private details?", "Who might find the lesson useful?"),
        ("How could you state the insight without exposing private information?", "Which audience could use that insight responsibly?"),
    ),
    (92, 1): (
        ("Which ordinary situation would improve most?", "What new problem could the power create?"),
        ("Which ordinary constraint would it remove?", "Which unintended consequence would need attention first?"),
    ),
    (92, 3): (
        ("Who might have a genuine reason to know?", "Which danger could secrecy reduce?"),
        ("Who could claim a legitimate need to know?", "Which foreseeable harm could non-disclosure prevent?"),
    ),
    (93, 1): (
        ("Which preparation would keep it interesting?", "What quality makes the choice flexible?"),
        ("Which variations would preserve its appeal?", "Which feature makes the choice sustainable?"),
    ),
    (93, 3): (
        ("What advantage does each food have?", "Which trade-off would decide between them?"),
        ("Which distinct advantage does each rival offer?", "Which criterion would settle the competition?"),
    ),
    (94, 1): (
        ("How often would you use it?", "What makes that service especially useful?"),
        ("Which recurring cost or difficulty would disappear?", "Which practical or personal benefit supports the choice?"),
    ),
    (94, 2): (
        ("Which service would meet that level of use?", "What could make frequent use less valuable?"),
        ("Which service could realistically reach that threshold?", "Which hidden cost could weaken its value?"),
    ),
    (94, 3): (
        ("Which day or routine would change most?", "What would you do with the time or money saved?"),
        ("Which weekly routine would be altered first?", "How would the saved resources be used?"),
    ),
    (94, 5): (
        ("Which long-term cost would it remove?", "Would practical value change what you preferred?"),
        ("Which recurring expense would make it superior?", "Could rational value overcome a less exciting experience?"),
    ),
    (94, 7): (
        ("Which hidden cost would matter most?", "How could a provider reduce that cost?"),
        ("Which non-financial cost could reverse the decision?", "What change would make the service worthwhile again?"),
    ),
    (95, 1): (
        ("Which routine would need a new plan?", "What could make that challenge manageable?"),
        ("Which routine would require the strongest replacement?", "Which condition could make the challenge workable?"),
    ),
    (95, 3): (
        ("What need does that function meet?", "What non-phone alternative could meet part of the need?"),
        ("Which practical or emotional need does it meet?", "Which alternative could preserve the essential benefit?"),
    ),
    (95, 4): (
        ("Which part of the day might feel calmer?", "What evidence would show a real improvement?"),
        ("Which current pressure might decrease?", "Which observable change would count as improvement?"),
    ),
    (95, 5): (
        ("What makes that time suitable for a break?", "How long would the break need to be useful?"),
        ("Which feature of that setting supports a deliberate pause?", "What duration would preserve the benefit without causing disruption?"),
    ),
    (95, 6): (
        ("Which tool or person could provide that support?", "How would it protect essential access?"),
        ("Which replacement system would provide that support?", "How would the arrangement preserve safety and accessibility?"),
    ),
    (95, 7): (
        ("Why should that function remain available?", "Which optional use could be limited around it?"),
        ("Which need makes continued access proportionate?", "Which discretionary use could be reduced without affecting that need?"),
    ),
    (96, 1): (
        ("Which activity would replace the first hour of routine tasks?", "What would give the day a satisfying rhythm?"),
        ("Which activity would replace the first block of routine work?", "Which source of structure would keep the day purposeful?"),
    ),
    (96, 3): (
        ("Who would be affected by the arrangement?", "What level of disclosure would be fair?"),
        ("Which stakeholders would be affected by the arrangement?", "What degree of transparency would be proportionate?"),
    ),
    (96, 5): (
        ("What would make the project meaningful?", "How much open time would you preserve?"),
        ("Which value would give the project direction?", "How would you balance the project with genuinely unstructured time?"),
    ),
    (96, 7): (
        ("What value comes from doing the task yourself?", "When would AI support still help?"),
        ("Which non-financial value comes from direct participation?", "Where could AI support the task without replacing that value?"),
    ),
    (97, 1): (
        ("Which trait does the animal represent?", "Where does the comparison stop working?"),
        ("Which trait does the metaphor illuminate?", "Which part of your personality remains outside the comparison?"),
    ),
    (97, 4): (
        ("Which visible behaviour might shape the observer's choice?", "Which private intention might shape the person's own choice?"),
        ("Which outward behaviour could explain the observer's metaphor?", "Which internal motive could explain the self-image?"),
    ),
    (97, 6): (
        ("Which setting changes the comparison most?", "Which trait remains visible everywhere?"),
        ("Which context-dependent behaviour alters the metaphor most?", "Which underlying characteristic remains stable across contexts?"),
    ),
    (97, 7): (
        ("Which trait has the strongest influence on your choice?", "What does the animal comparison fail to capture?"),
        ("Which concrete trait carries the greatest weight in your metaphor?", "Which limit of the comparison should remain explicit?"),
    ),
    (98, 1): (
        ("Which specific part of the upbringing interests you?", "What would you need to learn before making predictions?"),
        ("Which concrete condition creates the strongest contrast?", "Which uncertainty should prevent a stereotyped prediction?"),
    ),
    (99, 1): (
        ("Which part of the day would matter most?", "What would make the day feel ordinary rather than exceptional?"),
        ("Which feature would contribute most to satisfaction?", "What would make the day sustainable as a normal routine?"),
    ),
    (100, 1): (
        ("What memory or meaning gives it that value?", "How could you preserve part of that value beforehand?"),
        ("Which form of memory, history, or identity gives it that value?", "Which preparation could protect part of that value before an emergency?"),
    ),
    (100, 2): (
        ("Is the value practical, historical, or emotional?", "Could a copy preserve any part of it?"),
        ("Does the value come from information, history, identity, or use?", "Which part of that value could documentation preserve?"),
    ),
    (100, 3): (
        ("Why might people overlook its value?", "Which need or memory does it represent?"),
        ("Why can that category appear less important at first?", "Which hidden priority does it represent?"),
    ),
    (100, 5): (
        ("Which meaning could make an ordinary object important?", "Can the memory remain after the object is gone?"),
        ("Which connection to identity or memory could make the loss significant?", "How might the meaning survive without the original possession?"),
    ),
    (100, 7): (
        ("Would a backup, list, or safer storage help most?", "Which evacuation preparation should come first?"),
        ("Would duplication, documentation, or protected storage help most?", "Which evacuation step is both realistic and urgent?"),
    ),
}
for (_topic_no, _prompt_no), (_accessible, _full) in FOLLOWUP_REVISIONS.items():
    TOPICS[_topic_no]["prompts"][_prompt_no - 1].update(
        accessible_followups=_accessible,
        full_followups=_full,
    )


CLAIM_ORDER = {
    topic_no: tuple(f"ft{topic_no}-c{index:02d}" for index in range(1, 11))
    for topic_no in TOPIC_NUMBERS
}

# The track's productive entry floor is CORE-53.  Later Core moves are kept as
# audited TOC dependencies, never misrepresented as reachable vocabulary owners.
FUTURE_CORE_DEPENDENCIES = {
    89: ("CORE-66",),
    90: ("CORE-66", "CORE-71"),
    91: ("CORE-62", "CORE-66"),
    92: ("CORE-66", "CORE-98"),
    93: ("CORE-66",),
    96: ("CORE-66",),
    97: ("CORE-66", "CORE-97"),
    98: ("CORE-66",),
    99: ("CORE-66",),
    100: ("CORE-65", "CORE-66"),
}
REACHABLE_CORE_RETRIEVAL = {94: ("CORE-45", "CORE-46"), 95: ("CORE-51",)}

VOCABULARY = {
    89: {"new": "jackpot|大当たり", "recycled": "", "assumed": "win|当たる; lottery|宝くじ; money|お金; work|仕事; buy|買う; normal|普通の", "receptive": "financial freedom|経済的な自由; disclose|知らせる"},
    90: {"new": "essential item|必需品", "recycled": "", "assumed": "object|物; island|島; take|持っていく; useful|役に立つ; person|人", "receptive": "versatile|多用途の; symbolic value|象徴的な価値"},
    91: {"new": "trade lives|人生を入れ替える", "recycled": "", "assumed": "person|人; day|一日; life|人生; private|私的な; return|戻る", "receptive": "inhabit|体験する; intrusion|立ち入り"},
    92: {"new": "superpower|超能力", "recycled": "", "assumed": "power|力; choose|選ぶ; problem|問題; secret|秘密; refuse|断る", "receptive": "surveillance|監視; reversibility|元に戻せること"},
    93: {"new": "get sick of|飽きる", "recycled": "", "assumed": "food|食べ物; forever|永遠に; healthy|健康的な; choice|選択; miss|恋しくなる", "receptive": "dietary boundary|食事上の制限; sustainable|続けやすい"},
    94: {"new": "resell|転売する", "recycled": "", "assumed": "free|無料の; use|使う; week|一週間; benefit|利益; cost|費用", "receptive": "non-transferable|譲渡できない; opportunity cost|機会費用"},
    95: {"new": "digital detox|デジタル機器から離れること", "recycled": "", "assumed": "phone|携帯電話; week|一週間; routine|日課; safe|安全な; contact|連絡", "receptive": "accessibility|アクセシビリティ; discretionary|自由に減らせる"},
    96: {"new": "work identity|仕事を通じた自己認識", "recycled": "", "assumed": "AI|AI; salary|給料; work|仕事; study|勉強; care|ケア; routine|日課", "receptive": "automation|自動化; unstructured|予定のない"},
    97: {"new": "symbolize|象徴する", "recycled": "", "assumed": "animal|動物; people|人々; know|知る; choose|選ぶ; personality|性格", "receptive": "observer|観察者; metaphor|比喩"},
    98: {"new": "upbringing|育った環境", "recycled": "", "assumed": "country|国; grow up|育つ; language|言語; school|学校; family|家族", "receptive": "counterfactual|反実仮想; belonging|所属感"},
    99: {"new": "life direction|人生の方向性", "recycled": "", "assumed": "future|未来; ten years|十年; imagine|想像する; same|同じ; change|変える", "receptive": "projection|予想図; continuity|継続"},
    100: {"new": "irreplaceable|かけがえのない", "recycled": "", "assumed": "fire|火事; safe|安全な; object|物; lose|失う; save|持ち出す; pet|ペット", "receptive": "evacuation|避難; inventory|一覧"},
}

GLOSSES = {
    89: {"accessible": {1: ("jackpot", "jackpot", "大当たり")}, "full": {1: ("jackpot", "jackpot", "大当たり")}},
    90: {"accessible": {2: ("essential item", "essential item", "必需品")}, "full": {2: ("essential item", "essential item", "必需品")}},
    91: {"accessible": {1: ("trade lives", "trade lives", "人生を入れ替える")}, "full": {1: ("trade lives", "trade lives", "人生を入れ替える")}},
    92: {"accessible": {1: ("superpower", "superpower", "超能力")}, "full": {1: ("superpower", "superpower", "超能力")}},
    93: {"accessible": {4: ("get sick of", "get sick of", "飽きる")}, "full": {4: ("getting sick of", "get sick of", "飽きる")}},
    94: {"accessible": {6: ("resell", "resell", "転売する")}, "full": {6: ("Reselling", "resell", "転売する")}},
    95: {"accessible": {1: ("digital detox", "digital detox", "デジタル機器から離れること")}, "full": {1: ("A digital detox", "digital detox", "デジタル機器から離れること")}},
    96: {"accessible": {5: ("work identity", "work identity", "仕事を通じた自己認識")}, "full": {5: ("Work identity", "work identity", "仕事を通じた自己認識")}},
    97: {"accessible": {2: ("To symbolize", "symbolize", "象徴する")}, "full": {2: ("symbolize", "symbolize", "象徴する")}},
    98: {"accessible": {1: ("Upbringing", "upbringing", "育った環境")}, "full": {1: ("Upbringing", "upbringing", "育った環境")}},
    99: {"accessible": {2: ("life direction", "life direction", "人生の方向性")}, "full": {2: ("Life direction", "life direction", "人生の方向性")}},
    100: {"accessible": {5: ("Irreplaceable", "irreplaceable", "かけがえのない")}, "full": {5: ("An irreplaceable object", "irreplaceable", "かけがえのない")}},
}


def _render_dependencies():
    """Import renderer helpers only after an explicitly authorized render call."""
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415

    return base, new_lesson


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    _base, new_lesson = _render_dependencies()
    slug = f'{topic_no:02d}-{TOPICS[topic_no]["slug"]}'
    return (
        new_lesson.ENGLISH / "tracks/3-freetalking/courses"
        / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"
    )


def _set_pending(head: str) -> str:
    marker = '<meta name="podo:proofread-status" content="pending">'
    if re.search(r'<meta name="podo:proofread-status" content="(?:pending|complete)">', head):
        return re.sub(r'<meta name="podo:proofread-status" content="(?:pending|complete)">', marker, head, count=1)
    return head.replace('<meta name="podo:vocabulary-status"', marker + '\n  <meta name="podo:vocabulary-status"', 1)


def _article_page(topic_no: int, data: dict[str, object], variant: str, base) -> str:
    en_col, ja_col = (0, 2) if variant == "accessible" else (1, 3)
    rows = []
    for index, (article, claim_id) in enumerate(zip(data["articles"], CLAIM_ORDER[topic_no], strict=True), 1):
        en_markup, words = base.marked_text(article[en_col], GLOSSES[topic_no][variant].get(index))
        rows.append(
            '        <div class="sent" role="button" tabindex="0" '
            f'data-sync-option="s{index}" data-claim-id="{claim_id}">'
            f'<span class="s-line"><span class="s-ko">{en_markup}</span>'
            '<span class="s-mark" aria-hidden="true"></span></span>'
            f'<span class="s-open"><span class="s-ja">{base.esc(article[ja_col])}</span>{words}</span></div>'
        )
    title, title_ja = data["article_title"]
    body = (
        '      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span>'
        '<span class="ja">記事について何か質問はありましたか？</span></p>\n'
        '      <div class="tutor-note">Answer the learner\'s questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>\n'
        '      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">\n'
        + "\n".join(rows) + "\n      </div>"
    )
    return base.page("article", title, title_ja, body)


def _question_page(page_id: str, number: str, item: dict[str, object], variant: str, base) -> str:
    followups = item[f"{variant}_followups"]
    lis = "".join(f"<li>{base.esc(value)}</li>" for value in followups)
    japanese = item[f"{variant}_ja"]
    if sum(item[variant].count(mark) for mark in ".!?") == 1:
        japanese = japanese.replace("。", "、")
    body = (
        f'      <p class="section-subtitle ask"><span class="q-n">{number}</span>'
        f'<span class="ko">{base.esc(item[variant])}</span><span class="ja">{base.esc(japanese)}</span></p>\n'
        '      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">Follow up</span>'
        f'<ul class="tn-more">{lis}</ul></div></div>\n'
        f'      <div class="fb" data-fb="{variant}-{page_id}" data-fb-spoken-label="Student\'s sentence"></div>'
        '<div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button>'
        '<button class="fb-add" data-add="note" type="button">＋ Note</button></div>'
    )
    return base.page(page_id, item["title"], item["title_ja"], body)


def build(topic_no: int, variant: str) -> str:
    """Render one pair member only after the protected pilot gate is reopened."""
    if topic_no not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_no, variant))
    base, new_lesson = _render_dependencies()
    track = new_lesson.ENGLISH / "tracks/3-freetalking"
    canonical = (track / f"courses/talk-between-two-countries-{variant}" / "lessons/01-this-surprised-me/lesson.html").read_text(encoding="utf-8")
    data = TOPICS[topic_no]
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{data["slug"]}'
    head = new_lesson.retarget(
        head, review_id=f"FT-{topic_no}", lesson_id=slug,
        level="B1 accessible" if variant == "accessible" else "B2-C1 full",
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-21",
    )
    head = _set_pending(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])
    goal_en, goal_ja = data["goal"]
    pages = [
        base.ft_contract.goal_page(title=data["title"], title_ja=data["ja"], topic_en=goal_en, topic_ja=goal_ja, data_act="What if", kicker="WHAT IF"),
        _article_page(topic_no, data, variant, base),
        base.extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of your answers.</span><span class="ja">全部の質問に答える必要はありません。答えの中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Treat these pages as a pool, not a sequence. React or share briefly before choosing the next prompt, skip freely, and move to feedback with 2–3 minutes left.</div></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple((f"q{i}", f"QUESTION {i}") for i in range(1, 7))
    pages.extend(_question_page(page_id, number, item, variant, base) for (page_id, number), item in zip(prompt_ids, data["prompts"], strict=True))
    pages.append(base.extract_page(canonical, "feedback"))
    return new_lesson.redepth(head + "\n".join(pages) + foot, output_path(topic_no, variant))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    for topic_no in TOPIC_NUMBERS:
        for variant in VARIANTS:
            output = output_path(topic_no, variant)
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
