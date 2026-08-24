#!/usr/bin/env python3
"""Author and render paired Freetalking FT 107-121 balance-game decks.

Importing this module remains source-only. Repository and canonical-shell reads
stay behind ``build``/``output_path``/``main`` so the reviewed language can be
audited independently from rendering.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    from .ft_balance_games_content import ARTICLE_HEADS, ARTICLE_TAILS, QUESTION_POOLS
    from .ft_balance_games_followups import FULL_FOLLOWUPS, RECIPROCAL_FOLLOWUPS
except ImportError:
    from ft_balance_games_content import ARTICLE_HEADS, ARTICLE_TAILS, QUESTION_POOLS
    from ft_balance_games_followups import FULL_FOLLOWUPS, RECIPROCAL_FOLLOWUPS


COURSE = "talk-balance-games"
TOPIC_NUMBERS = tuple(range(107, 122))
VARIANTS = ("accessible", "full")
TOPIC_FORMAT = {number: "choose" for number in TOPIC_NUMBERS}
SENSITIVE_TOPICS = frozenset(TOPIC_NUMBERS)
TOC_RETRIEVAL_AUDIT_ONLY = True

BALANCE_CONTRACT = {
    "interaction": "spoken-discussion-no-binary-ui",
    "states": ("option-a", "option-b", "depends-or-both", "neither-or-no-personal-example"),
    "prompt_jobs": ("opening", "real-scene", "use-chosen", "opposite", "condition", "cost", "threshold", "flip"),
    "claim_roles": ("both-defensible", "values", "new-language", "option-a-case", "option-b-case", "trade-off", "opposite-history", "changed-condition", "four-state-honesty", "flip-point"),
    "ladder": "pick -> real scene -> use -> opposite -> changed condition -> cost -> exact flip point",
}

BRIEF_OPENINGS = {
    107: "If tomorrow came with one extra hour or fifty extra dollars, which would help more?",
    108: "For one difficult week, would you rather have a hundred friendly contacts or three close friends?",
    109: "If one season had to last all year, would you choose summer or winter?",
    110: "For your most important tasks, would you rather start early or work late?",
    111: "For a three-day trip, would you plan each day or decide as you go?",
    112: "For a new destination, would you rather travel alone or with someone?",
    113: "For daily life, would you rather live in a busy city or a quiet town?",
    114: "For one summer, would you give up internet or air conditioning?",
    115: "For the next year, would you choose more free time or a higher income?",
    116: "For focused work, would you choose home or a shared workplace?",
    117: "For two hours of serious study, would you choose a café or home?",
    118: "For an important purchase, would you rather buy online or in a shop?",
    119: "Would you rather remember every ordinary detail or be able to forget painful memories?",
    120: "Would you rather be rich and unknown or respected on an average income?",
    121: "Would you rather master one skill or become good at many?",
}

FULL_OPENINGS = {
    107: "Which would improve tomorrow more: an extra hour of free time or fifty extra dollars?",
    108: "During a difficult week, would a wide circle of friendly contacts or three close friends matter more?",
    109: "If the same season continued all year, would you prefer permanent summer or permanent winter?",
    110: "When the work matters most, do you function better early in the morning or late at night?",
    111: "For a short trip, would you rather follow a plan or make decisions as you go?",
    112: "When visiting somewhere new, would you rather travel independently or with company?",
    113: "For daily life, would you rather live in a busy city or a quiet town?",
    114: "If you had to lose one for a summer, would you choose internet or air conditioning?",
    115: "Over the next year, would greater control of your time or a higher income matter more?",
    116: "For work that requires concentration, would home or a shared workplace suit you better?",
    117: "For two demanding hours of study, would a café or your home support better focus?",
    118: "For an important purchase, would you trust an online order or a shop more?",
    119: "Would you prefer perfect recall of ordinary details or the ability to let painful memories fade?",
    120: "Would you rather be rich and unknown or respected on an average income?",
    121: "Would you rather become excellent at one skill or good at many?",
}

OPENINGS_JA = {
    107: "明日、自由な時間が一時間増えるか、五十ドル増えるなら、どちらがより役立ちますか？",
    108: "大変な一週間なら、顔見知りの友人百人と親しい友人三人のどちらがよいですか？",
    109: "一つの季節が一年中続くなら、夏と冬のどちらを選びますか？",
    110: "大切なことをするとき、朝早く始めるのと夜遅く取り組むのと、どちらがよいですか？",
    111: "三日間の旅行なら、毎日計画するのと、その場で決めるのと、どちらがよいですか？",
    112: "初めての場所へ行くなら、一人旅と誰かとの旅行のどちらがよいですか？",
    113: "日常生活なら、にぎやかな都会と静かな町のどちらに住みたいですか？",
    114: "一夏の間、インターネットとエアコンのどちらかを諦めるなら、どちらにしますか？",
    115: "これから一年、自由な時間と高い収入のどちらを選びますか？",
    116: "集中して作業するなら、家と共有の職場のどちらを選びますか？",
    117: "二時間しっかり勉強するなら、カフェと家のどちらを選びますか？",
    118: "大切な買い物なら、オンラインと店舗のどちらで買いますか？",
    119: "日常の細かいことをすべて覚えるのと、つらい記憶を忘れられるのと、どちらを選びますか？",
    120: "裕福で無名の生活と、平均的な収入で尊敬される生活のどちらがよいですか？",
    121: "一つの技能を極めるのと、多くの技能が得意になるのと、どちらを選びますか？",
}

FULL_OPENINGS_JA = {
    107: "明日をよりよくするのは、自由な時間が一時間増えることと、五十ドル増えることのどちらですか？",
    108: "大変な一週間により頼りになるのは、広い友人関係と親しい友人三人のどちらですか？",
    109: "同じ季節が一年中続くなら、終わらない夏と終わらない冬のどちらがよいですか？",
    110: "重要な作業では、朝早くと夜遅くのどちらのほうが力を発揮できますか？",
    111: "短い旅行なら、計画に従うのと、その場で決めるのと、どちらがよいですか？",
    112: "初めての場所を訪れるなら、一人で行くのと誰かと行くのと、どちらがよいですか？",
    113: "日常生活なら、にぎやかな都会と静かな町のどちらに住みたいですか？",
    114: "一夏の間どちらかを失うなら、インターネットとエアコンのどちらにしますか？",
    115: "これから一年では、時間の裁量と高い収入のどちらがより大切ですか？",
    116: "集中が必要な仕事には、家と共有の職場のどちらがより合いますか？",
    117: "難しい勉強を二時間するなら、カフェと家のどちらが集中しやすいですか？",
    118: "大切な買い物なら、オンライン注文と店のどちらをより信頼しますか？",
    119: "日常の細部を完全に覚えるのと、つらい記憶を薄れさせられるのと、どちらがよいですか？",
    120: "世間に知られない裕福な生活と、普通の収入で尊敬される生活のどちらを選びますか？",
    121: "一つの技能の深い専門性と、多くの技能にわたる幅広い能力のどちらを伸ばしたいですか？",
}

SHARED_SOURCE = {
    **{number: f"KR 11-{number - 106}" for number in range(107, 121)},
    121: "NEW → KR",
}

# Theme 11 deliberately supplies no fixed Core retrieval moves: these are
# spoken choices, not disguised grammar drills. The empty per-topic contract is
# explicit so a later renderer cannot silently invent a target frame.
TOC_RETRIEVAL = {number: () for number in TOPIC_NUMBERS}

# Safety labels belong to the prompt frame, not the scene noun. These three
# topics already carry an explicit opt-out in their opening, so neutral nouns
# prevent awkward strings such as "imagined ... imagined purchase."
SCENE_NOUNS = {
    118: ("purchase decision", "購入の判断"),
    119: ("case involving memory", "記憶に関する事例"),
    120: ("life shaped by wealth or recognition", "富や評価に左右される人生"),
}


def prompt(job, title, title_ja, accessible, accessible_ja, accessible_followups, *, full, full_ja, full_followups, safety):
    return {
        "job": job,
        "title": title,
        "title_ja": title_ja,
        "accessible": accessible,
        "accessible_ja": accessible_ja,
        "accessible_followups": accessible_followups,
        "full": full,
        "full_ja": full_ja,
        "full_followups": full_followups,
        "safety": safety,
    }


def tutor_prompt(number, data):
    """End each pool with a reciprocal learner-to-tutor exchange."""
    accessible_followups, full_followups = RECIPROCAL_FOLLOWUPS[number]
    return prompt(
        "tutor",
        "Hear your tutor's choice",
        "チューターの選択を聞く",
        "Ask your tutor which option they would choose and why.",
        "チューターならどちらを選ぶか、その理由も聞いてください。",
        accessible_followups,
        full="Ask your tutor which option they would choose and why.",
        full_ja="チューターならどちらを選ぶか、その理由も聞いてください。",
        full_followups=full_followups,
        safety="reciprocal-tutor-answer",
    )


# Final spoken review: remove abstract packaging, give every no-answer path a
# concrete foothold, and keep Full depth in the answer rather than the syntax.
FINAL_ONE_HEARING_REPAIRS = {
    (107, "saved-time"): dict(
        accessible="Would you take a slower route to save money?",
        accessible_ja="お金を節約するためなら、時間のかかる道を選びますか？",
        full="Would you take a slower route to save money?",
        full_ja="お金を節約するためなら、時間のかかる道を選びますか？",
        accessible_followups=("How much extra time would be acceptable?", "Which usually costs less: walking or public transport?"),
        full_followups=("How much extra time would be acceptable?", "Which usually costs less: walking or public transport?"),
    ),
    (108, "daily-life"): dict(
        accessible="What would be missing if you knew many people but had no close friends?",
        accessible_ja="知り合いは多くても親しい友人がいないとしたら、何が足りませんか？",
        full="What would be missing if you knew many people but had no close friends?",
        full_ja="知り合いは多くても親しい友人がいないとしたら、何が足りませんか？",
        accessible_followups=("Who would you call after a bad day?", "Would you rather share good news with one person or a large group?"),
        full_followups=("Who would you call after a bad day?", "Would you rather share good news with one person or a large group?"),
    ),
    (110, "whole-day"): dict(
        accessible_followups=("Why is that hardest to change?", "Would changing your sleep schedule affect your mood?"),
        full_followups=("Why is that hardest to change?", "Would changing your sleep schedule affect your mood?"),
    ),
    (112, "choice"): dict(
        accessible_followups=("What would be easier alone?", "When would company help?"),
        full_followups=("What would be easier alone?", "When would company help?"),
    ),
    (112, "new-country"): dict(
        full="What would make three days alone somewhere new enjoyable?",
        full_ja="初めての場所で一人で過ごす三日間を、楽しくするものは何ですか？",
    ),
    (113, "convenience"): dict(
        title="What you want nearby",
        title_ja="近くにほしいもの",
        accessible="What do you most want within walking distance of your home?",
        accessible_ja="家から歩いて行ける場所に、何がいちばんほしいですか？",
        full="What do you most want within walking distance of your home?",
        full_ja="家から歩いて行ける場所に、何がいちばんほしいですか？",
        accessible_followups=("How often would you use it?", "Would a ten-minute walk feel close enough?"),
        full_followups=("How often would you use it?", "Would a ten-minute walk feel close enough?"),
    ),
    (116, "team-day"): dict(
        accessible_followups=("What would the team need to do together?", "Which is easier in person: planning or solving a disagreement?"),
        full_followups=("What would the team need to do together?", "Which is easier in person: planning or solving a disagreement?"),
    ),
    (116, "switch"): dict(
        title="Feeling connected at home",
        title_ja="在宅でもつながりを感じること",
        accessible="What can make a workday at home feel less lonely?",
        accessible_ja="在宅勤務の日に孤独を感じにくくするには、何が役立ちますか？",
        full="What can make a workday at home feel less lonely?",
        full_ja="在宅勤務の日に孤独を感じにくくするには、何が役立ちますか？",
        accessible_followups=("Would a short call with a coworker help?", "Which would help more: lunch outside or an online chat?"),
        full_followups=("Would a short call with a coworker help?", "Which would help more: lunch outside or an online chat?"),
    ),
    (117, "best-focus"): dict(
        accessible_followups=("Do you focus better alone or around other people?", "Which helps more: silence or a little background noise?"),
        full_followups=("Do you focus better alone or around other people?", "Which helps more: silence or a little background noise?"),
    ),
    (117, "choice"): dict(
        full="For two hours of serious study, would you choose a café or home?",
        full_ja="二時間しっかり勉強するなら、カフェと家のどちらを選びますか？",
    ),
    (117, "drink-cost"): dict(
        accessible_followups=("Would you stay longer to make the drink feel worth it?", "Would a free library be a better choice?"),
        full_followups=("Would you stay longer to make the drink feel worth it?", "Would a free library be a better choice?"),
    ),
    (117, "switch"): dict(
        full="Which task needs the privacy or equipment you have at home?",
        full_ja="家にあるプライバシーや道具が必要なのは、どんな課題ですか？",
    ),
    (118, "photo-match"): dict(
        accessible="What makes you trust a product you see online?",
        accessible_ja="オンラインで見た商品を信頼できるのは、どんなときですか？",
        full="What makes you trust a product you see online?",
        full_ja="オンラインで見た商品を信頼できるのは、どんなときですか？",
        accessible_followups=("Does a clear return policy matter?", "Which do you trust more: customer photos or star ratings?"),
        full_followups=("Does a clear return policy matter?", "Which do you trust more: customer photos or star ratings?"),
    ),
    (118, "same-day"): dict(
        accessible="Would you still visit a shop if same-day delivery were free?",
        accessible_ja="当日配送が無料でも、店へ行きますか？",
        full="Would you still visit a shop if same-day delivery were free?",
        full_ja="当日配送が無料でも、店へ行きますか？",
    ),
    (119, "all-vivid"): dict(
        accessible_followups=("Would embarrassing memories get easier with time?", "Which would bother you more: old mistakes or useless details?"),
        full_followups=("Would embarrassing memories get easier with time?", "Which would bother you more: old mistakes or useless details?"),
    ),
    (119, "lost-lesson"): dict(
        title="Memory and arguments",
        title_ja="記憶と口論",
        accessible="Would perfect memory make arguments easier or harder?",
        accessible_ja="何でも覚えていたら、口論は楽になりますか、それとも難しくなりますか？",
        full="Would perfect memory help solve arguments or keep them going?",
        full_ja="何でも覚えていたら、口論を解決しやすくなりますか、それとも長引かせますか？",
        accessible_followups=("Would remembering the exact words help?", "Is it sometimes better to forget a small mistake?"),
        full_followups=("Would remembering the exact words help?", "Is it sometimes better to forget a small mistake?"),
    ),
    (121, "recent-skill"): dict(
        title="Recent progress",
        title_ja="最近の上達",
        accessible="Which skill, if any, have you improved recently?",
        accessible_ja="最近、上達した技能があるとしたら何ですか？",
        full="Which skill, if any, have you improved recently?",
        full_ja="最近、上達した技能があるとしたら何ですか？",
        accessible_followups=("What helped you improve?", "Which is easier to improve: cooking, exercise, or language?"),
        full_followups=("What helped you improve?", "Which is easier to improve: cooking, exercise, or language?"),
    ),
    (121, "team"): dict(
        accessible="On a small team, who helps more: a specialist or someone who can do several jobs?",
        accessible_ja="小さなチームでは、一人の専門家と、いくつもの仕事ができる人のどちらが役立ちますか？",
        full="On a small team, who helps more: a specialist or someone who can do several jobs?",
        full_ja="小さなチームでは、一人の専門家と、いくつもの仕事ができる人のどちらが役立ちますか？",
        accessible_followups=("Why would that person help the team?", "Can a flexible worker help when a teammate is absent?"),
        full_followups=("Why would that person help the team?", "Can a flexible worker help when a teammate is absent?"),
    ),
    (121, "new-field"): dict(
        accessible="Which new skill would you rather learn: cooking, photography, or first aid?",
        accessible_ja="新しく学ぶなら、料理、写真、応急手当のどれがよいですか？",
        full="Which new skill would you rather learn: cooking, photography, or first aid?",
        full_ja="新しく学ぶなら、料理、写真、応急手当のどれがよいですか？",
        accessible_followups=("Why would that skill be useful?", "Which is easiest to practise at home: cooking, photography, or first aid?"),
        full_followups=("Why would that skill be useful?", "Which is easiest to practise at home: cooking, photography, or first aid?"),
    ),
}


def topic_prompts(number, data):
    """Use the reviewed choice from the brief inside the topic-specific pool."""
    pool = [dict(item) for item in QUESTION_POOLS[number]]
    for item in pool:
        item["full_followups"] = (
            FULL_FOLLOWUPS[number][item["job"]]
            if number == 107
            else item["accessible_followups"]
        )
    pool[2].update(
        accessible=BRIEF_OPENINGS[number],
        accessible_ja=OPENINGS_JA[number],
        full=FULL_OPENINGS[number],
        full_ja=FULL_OPENINGS_JA[number],
    )
    for item in pool:
        changes = FINAL_ONE_HEARING_REPAIRS.get((number, item["job"]))
        if changes:
            item.update(**changes)
    return tuple(pool) + (tutor_prompt(number, data),)


RAW_TOPICS = {
    107: dict(slug="more-money-or-more-time", title="More money or more time?", ko="더 많은 돈, 더 많은 시간?", ja="もっとお金、それとももっと時間？", a="more money", b="more time", a_ja="もっとお金", b_ja="もっと時間", value_a="financial room", value_b="usable hours", value_a_ja="金銭的な余裕", value_b_ja="自由に使える時間", scene="week with too many demands", scene_ja="用事が多すぎる一週間", condition="the amount of free time or money", condition_ja="自由な時間やお金の量", condition_full="resources and obligations", condition_full_ja="資源と義務", threshold="amount", threshold_ja="量", threshold_full="resource level", threshold_full_ja="資源の水準", a_when="an urgent cost must be covered", a_when_ja="急な支出に対応する必要がある", a_when_full="financial pressure limits essential choices", a_when_full_ja="金銭的な圧力で必要な選択が制限される", b_when="rest or attention is missing", b_when_ja="休息や集中する時間が足りない", b_when_full="time scarcity damages health or relationships", b_when_full_ja="時間不足が健康や人間関係を損なう", new_claim=("A time-poor person may need free hours more than extra income.", "Being time-poor can make an additional free hour more valuable than a modest increase in income.", "時間に余裕がない人には、収入より自由な時間が必要な場合があります。", "時間に余裕がないと、少しの収入増より、自由な一時間のほうが価値を持つことがあります。"), opening_ja="今、もっと必要なのはお金と時間のどちらですか？", opening_ja_full="今の状況で、より必要なのはお金と時間のどちらですか？", fallback="A general or imagined week is fine.", fallback_ja="一般的な、または想像上の一週間でもかまいません。", fallback_full="Use a general or hypothetical case instead of private finances.", fallback_ja_full="個人のお金の話ではなく、一般的または仮定の事例でもかまいません。"),
    108: dict(slug="a-hundred-friends-or-three-close-ones", title="A hundred friends or three close ones?", ko="친구 백 명, 가까운 친구 세 명?", ja="友人百人、それとも親しい友人三人？", a="a hundred friends", b="three close friends", a_ja="百人の友人", b_ja="三人の親しい友人", value_a="reach", value_b="trust", value_a_ja="広いつながり", value_b_ja="信頼", scene="social situation", scene_ja="人間関係の場面", condition="time and trust", condition_ja="時間と信頼", condition_full="available attention and mutual responsibility", condition_full_ja="使える時間と互いの責任", threshold="number of dependable relationships", threshold_ja="頼れる関係の数", threshold_full="level of dependable support", threshold_full_ja="頼れる支援の水準", a_when="many weak connections create useful access", a_when_ja="広く緩いつながりが役立つ", a_when_full="reach and diverse information matter more than intimacy", a_when_full_ja="親密さより広がりや多様な情報が重要になる", b_when="trust and regular support matter", b_when_ja="信頼と継続的な支えが大切になる", b_when_full="mutual care requires sustained attention", b_when_full_ja="互いのケアに継続的な注意が必要になる", new_claim=("An inner circle is small enough for trust to grow through repeated contact.", "A reliable inner circle depends less on size than on repeated, mutual attention.", "親しい仲間の輪は小さいからこそ、繰り返す関わりの中で信頼が育ちます。", "信頼できる親しい仲間の輪は、人数より、繰り返される相互の関わりに支えられます。"), opening_ja="実際には、たくさんの友人と少数の親しい友人のどちらがいますか？", opening_ja_full="実際の人間関係は、広い友人関係と少数の親しい関係のどちらに近いですか？", fallback="A public, fictional, or imagined social circle is fine.", fallback_ja="公の例、架空の例、想像上の人間関係でもかまいません。", fallback_full="Use a public or hypothetical network instead of private relationships.", fallback_ja_full="個人的な関係ではなく、公の例や仮定の人間関係でもかまいません。"),
    109: dict(slug="endless-summer-or-endless-winter", title="Endless summer or endless winter?", ko="끝없는 여름, 끝없는 겨울?", ja="終わらない夏、それとも冬？", a="endless summer", b="endless winter", a_ja="終わらない夏", b_ja="終わらない冬", value_a="warmth and long days", value_b="cool air and quiet seasons", value_a_ja="暖かさと長い日", value_b_ja="涼しさと静かな季節", scene="day shaped by difficult weather", scene_ja="厳しい天気に左右された一日", condition="temperature and daylight", condition_ja="気温と日照時間", condition_full="climate, infrastructure, and daily obligations", condition_full_ja="気候、設備、日々の義務", threshold="temperature", threshold_ja="気温", threshold_full="climate condition", threshold_full_ja="気候条件", a_when="cold creates the larger burden", a_when_ja="寒さの負担のほうが大きい", a_when_full="warmth expands safe, usable outdoor time", a_when_full_ja="暖かさによって安全に屋外で過ごせる時間が増える", b_when="heat makes rest and work difficult", b_when_ja="暑さで休息や仕事が難しくなる", b_when_full="cooler conditions protect sleep and concentration", b_when_full_ja="涼しい環境が睡眠と集中を守る", new_claim=("Seasonal extremes can make either option difficult rather than pleasant.", "Seasonal extremes expose the limits of both options once comfort becomes a question of health and infrastructure.", "季節の極端さによって、どちらも快適ではなく大変になることがあります。", "季節が極端になると、快適さが健康や設備の問題になり、どちらの選択にも限界が見えます。"), opening_ja="どちらか一つを選んでから、いちばん苦手な季節について話してください。", opening_ja_full="一つ選び、最もつらかった季節の経験を話してください。", fallback="A familiar or imagined climate is fine.", fallback_ja="身近な、または想像上の気候でもかまいません。", fallback_full="A public or hypothetical climate case is equally valid.", fallback_ja_full="公に知られた例や仮定の気候でもかまいません。"),
    110: dict(slug="morning-person-or-night-owl", title="Morning person or night owl?", ko="아침형 인간, 올빼미형 인간?", ja="朝型、それとも夜型？", a="being a morning person", b="being a night owl", a_ja="朝型であること", b_ja="夜型であること", value_a="early energy", value_b="late focus", value_a_ja="朝の活力", value_b_ja="夜の集中", scene="day with a fixed start time", scene_ja="開始時刻が決まった一日", condition="sleep and schedule", condition_ja="睡眠と予定", condition_full="biological rhythm and social schedule", condition_full_ja="体のリズムと社会的な予定", threshold="wake-up time", threshold_ja="起床時刻", threshold_full="required start time", threshold_full_ja="必要な開始時刻", a_when="important work begins early", a_when_ja="大切な活動が早く始まる", a_when_full="the schedule rewards reliable early attention", a_when_full_ja="予定上、朝の安定した集中が求められる", b_when="quiet late hours protect focus", b_when_ja="静かな夜の時間が集中を守る", b_when_full="later hours provide uninterrupted cognitive space", b_when_full_ja="遅い時間に中断されない思考の余地がある", new_claim=("A body clock can differ from the schedule a person has to follow.", "A person's body clock may conflict with institutional schedules without reflecting laziness or discipline.", "体内時計は、従わなければならない予定と合わないことがあります。", "体内時計が制度上の予定と合わなくても、怠惰さや規律の問題とは限りません。"), opening_ja="今日、実際に何時に起きましたか？", opening_ja_full="今日は実際に何時に起き、それは普段のリズムに合っていましたか？", fallback="Another day or an imagined schedule is fine.", fallback_ja="別の日や想像上の予定でもかまいません。", fallback_full="Use another day or a hypothetical schedule if today is not representative.", fallback_ja_full="今日が普段と違うなら、別の日や仮定の予定でもかまいません。"),
    111: dict(slug="a-planned-trip-or-a-spontaneous-one", title="A planned trip or a spontaneous one?", ko="계획 여행, 즉흥 여행?", ja="計画的な旅、それとも気ままな旅？", a="a planned trip", b="a spontaneous trip", a_ja="計画的な旅行", b_ja="行き当たりばったりの旅行", value_a="certainty", value_b="flexibility", value_a_ja="確実さ", value_b_ja="柔軟さ", scene="trip or local outing", scene_ja="旅行や近場の外出", condition="time, money, and responsibility", condition_ja="時間、お金、責任", condition_full="risk, access, and fixed commitments", condition_full_ja="リスク、利用条件、固定された予定", threshold="planning time", threshold_ja="計画に使える時間", threshold_full="level of uncertainty", threshold_full_ja="不確実さの水準", a_when="bookings or access are limited", a_when_ja="予約や利用条件に制限がある", a_when_full="failure would carry a high financial or practical cost", a_when_full_ja="失敗した場合の金銭的、実際的な負担が大きい", b_when="the cost of changing direction is low", b_when_ja="方向を変える負担が小さい", b_when_full="flexibility creates more value than certainty", b_when_full_ja="確実さより柔軟さのほうが価値を生む", new_claim=("A last-minute plan can still be responsible when the risks are small.", "A last-minute plan is not automatically careless when access, cost, and obligations remain manageable.", "直前の計画でも、リスクが小さければ責任ある選択になれます。", "直前に立てた計画でも、利用条件、費用、義務を管理できるなら、必ずしも無責任ではありません。"), opening_ja="最近の旅行を思い出してください。計画的でしたか、それとも行き当たりばったりでしたか？", opening_ja_full="最近の旅行や外出は、計画的でしたか、それとも行き当たりばったりでしたか？", fallback="If you have not travelled, use a local outing or imagined trip.", fallback_ja="旅行経験がなければ、近場の外出や想像上の旅行でもかまいません。", fallback_full="A local, familiar, public, or hypothetical trip can replace personal travel.", fallback_ja_full="個人の旅行ではなく、近場、身近、公の例、仮定の旅行でもかまいません。"),
    112: dict(slug="travelling-alone-or-with-other-people", title="Travelling alone or with other people?", ko="혼자 여행, 함께 여행?", ja="一人旅、それとも誰かと一緒？", a="travelling alone", b="travelling with other people", a_ja="一人で旅行すること", b_ja="ほかの人と旅行すること", value_a="independence", value_b="shared support", value_a_ja="自立性", value_b_ja="共有できる支え", scene="trip or outing", scene_ja="旅行や外出", condition="safety, purpose, and company", condition_ja="安全、目的、同行者", condition_full="risk, coordination, and emotional needs", condition_full_ja="リスク、調整、感情面の必要", threshold="amount of coordination", threshold_ja="必要な調整の量", threshold_full="coordination burden", threshold_full_ja="調整の負担", a_when="the traveller wants full control of the pace", a_when_ja="旅行者が過ごす速さを自分で決めたい", a_when_full="autonomy matters more than shared support", a_when_full_ja="共有の支えより自立性が重要になる", b_when="shared help improves safety or enjoyment", b_when_ja="助け合いで安全や楽しさが増す", b_when_full="mutual support offsets the cost of coordination", b_when_full_ja="互いの支えが調整の負担を上回る", new_claim=("A shared itinerary can prevent conflict without controlling every hour.", "A shared itinerary can establish common priorities while leaving room for separate interests.", "共有する旅程があれば、すべての時間を決めなくても衝突を防げます。", "共有する旅程は、別々の関心を楽しむ余地を残しながら、共通の優先事項を決められます。"), opening_ja="最近の旅行では、一人でしたか、それともほかの人と一緒でしたか？", opening_ja_full="最近の旅行や外出では、一人でしたか、それともほかの人と一緒でしたか？", fallback="If you have not travelled, use a local outing or imagined traveller.", fallback_ja="旅行経験がなければ、近場の外出や想像上の旅行者でもかまいません。", fallback_full="Use a familiar, public, or hypothetical traveller instead of personal travel.", fallback_ja_full="個人の旅行ではなく、身近、公の例、仮定の旅行者でもかまいません。"),
    113: dict(slug="life-in-the-city-or-the-countryside", title="Life in the city or the countryside?", ko="도시 생활, 시골 생활?", ja="都会暮らし、それとも田舎暮らし？", a="city life", b="country life", a_ja="都会の生活", b_ja="田舎の生活", value_a="access", value_b="space and quiet", value_a_ja="利用しやすさ", value_b_ja="空間と静けさ", scene="living situation", scene_ja="暮らしの場面", condition="transport, care, and work", condition_ja="交通、ケア、仕事", condition_full="access, obligations, and social ties", condition_full_ja="利用条件、義務、人とのつながり", threshold="travel time", threshold_ja="移動時間", threshold_full="access cost", threshold_full_ja="利用するための負担", a_when="daily services need to be nearby", a_when_ja="日常のサービスが近くに必要になる", a_when_full="dense access reduces essential travel and isolation", a_when_full_ja="高い利便性が必要な移動や孤立を減らす", b_when="space and quiet improve daily life", b_when_ja="空間と静けさが生活をよくする", b_when_full="lower density supports the person's preferred pace and environment", b_when_full_ja="低い密度が望む生活の速さや環境を支える", new_claim=("City access can matter more than city excitement.", "City access may be valuable because it reduces friction around care, transport, and essential services, not because urban life is exciting.", "都会の刺激より、都会の利用しやすさのほうが大切な場合があります。", "都会の価値は刺激ではなく、ケア、交通、必要なサービスを利用する負担が減ることにある場合があります。"), opening_ja="今どこに住んでいて、それは自分で選んだことですか？", opening_ja_full="今住んでいる場所は、自分で選んだ結果ですか？", fallback="A familiar, public, or imagined place is fine.", fallback_ja="身近、公の例、想像上の場所でもかまいません。", fallback_full="Use a general or hypothetical resident instead of private circumstances.", fallback_ja_full="個人的な事情ではなく、一般的または仮定の住民の例でもかまいません。"),
    114: dict(slug="a-summer-without-internet-or-air-conditioning", title="A summer without internet or air conditioning?", ko="인터넷 없는 여름, 에어컨 없는 여름?", ja="ネットなしの夏、それともエアコンなし？", a="a summer without internet", b="a summer without air conditioning", a_ja="インターネットなしの夏", b_ja="エアコンなしの夏", value_a="physical comfort", value_b="digital access", value_a_ja="身体的な快適さ", value_b_ja="デジタルな利用環境", scene="hot week", scene_ja="暑い一週間", condition="heat and internet dependence", condition_ja="暑さとインターネットへの依存", condition_full="climate, health, work, and communication needs", condition_full_ja="気候、健康、仕事、連絡の必要", threshold="temperature or connection need", threshold_ja="気温や接続の必要性", threshold_full="health or access risk", threshold_full_ja="健康や利用環境のリスク", a_when="reliable cooling matters more than being connected", a_when_ja="接続より安定した冷房が大切になる", a_when_full="heat poses a health risk and offline alternatives make disconnection manageable", a_when_full_ja="暑さが健康上の危険になり、オフラインの代替手段で接続なしでも過ごせる", b_when="the climate is mild and internet access is essential", b_when_ja="気候が穏やかでインターネット接続が必要になる", b_when_full="safe cooling alternatives remain available and connectivity supports essential obligations", b_when_full_ja="安全に涼める代替手段があり、接続が重要な義務を支える", new_claim=("Cooling can be a health need rather than a luxury.", "Reliable cooling becomes essential infrastructure when heat threatens sleep, work, or health.", "涼しくすることは、ぜいたくではなく健康上の必要になり得ます。", "暑さが睡眠、仕事、健康を脅かすとき、安定した冷房は不可欠な設備になります。"), opening_ja="夏の間ずっと、インターネットなしとエアコンなしならどちらですか？", opening_ja_full="夏の間ずっと、インターネットなしとエアコンなしのどちらを選びますか？", fallback="A familiar or imagined summer is fine.", fallback_ja="身近な、または想像上の夏でもかまいません。", fallback_full="Use a public or hypothetical climate and access case.", fallback_ja_full="公の例や仮定の気候・利用環境でもかまいません。"),
    115: dict(slug="better-work-life-balance-or-a-higher-salary", title="Better work-life balance or a higher salary?", ko="더 나은 워라밸, 더 높은 급여?", ja="よりよい生活との両立、それとも高い給料？", a="better work-life balance", b="a higher salary", a_ja="よりよい仕事と生活の両立", b_ja="より高い給料", value_a="time autonomy", value_b="financial capacity", value_a_ja="時間の自由", value_b_ja="金銭的な余力", scene="work, study, or care arrangement", scene_ja="仕事、学習、ケアの場面", condition="hours, pay, and responsibility", condition_ja="時間、報酬、責任", condition_full="financial need, control over time, and career risk", condition_full_ja="金銭的な必要、時間の裁量、キャリア上のリスク", threshold="salary difference", threshold_ja="給料の差", threshold_full="compensation gap", threshold_full_ja="報酬の差", a_when="time pressure is causing real harm", a_when_ja="時間の圧力が実際の負担を生んでいる", a_when_full="control over time protects health or essential responsibilities", a_when_full_ja="時間の裁量が健康や重要な責任を守る", b_when="additional income covers an essential need", b_when_ja="追加収入が必要な支出を支える", b_when_full="compensation materially expands security or choice", b_when_full_ja="報酬が安心や選択肢を実質的に増やす", new_claim=("Time autonomy can matter as much as the number of hours worked.", "Time autonomy changes whether working hours can coexist with care, health, and other obligations.", "時間の自由は、働く時間の長さと同じくらい大切な場合があります。", "時間の裁量によって、労働時間とケア、健康、ほかの義務を両立できるかが変わります。"), opening_ja="今の仕事でより得られるのは、時間とお金のどちらですか？", opening_ja_full="今の仕事や役割では、時間とお金のどちらをより得られますか？", fallback="If you do not have a current job, use work, study, care, or a general example.", fallback_ja="今の仕事がなければ、仕事、学習、ケア、一般的な例でもかまいません。", fallback_full="Use a general or hypothetical role instead of private employment or income.", fallback_ja_full="個人の雇用や収入ではなく、一般的または仮定の役割でもかまいません。"),
    116: dict(slug="working-from-home-or-going-into-the-office", title="Working from home or going into the office?", ko="재택근무, 사무실 출근?", ja="在宅勤務、それとも出社？", a="working from home", b="going into the office", a_ja="在宅で働くこと", b_ja="職場へ行くこと", value_a="control and reduced travel", value_b="shared space and quick coordination", value_a_ja="裁量と移動の削減", value_b_ja="共有空間と素早い調整", scene="work or study week", scene_ja="仕事や学習の一週間", condition="space, travel, and collaboration", condition_ja="空間、移動、協働", condition_full="task type, home conditions, and team dependence", condition_full_ja="作業の種類、家の環境、チームへの依存", threshold="commute or coordination need", threshold_ja="通勤や調整の必要性", threshold_full="coordination benefit", threshold_full_ja="調整による利益", a_when="the home environment supports focused work", a_when_ja="家の環境が集中を支える", a_when_full="autonomy and reduced travel outweigh coordination costs", a_when_full_ja="裁量と移動削減の利益が調整の負担を上回る", b_when="shared equipment or rapid coordination matters", b_when_ja="共有設備や素早い調整が大切になる", b_when_full="co-location materially improves access, learning, or decisions", b_when_full_ja="同じ場所にいることで利用、学習、判断が実質的によくなる", new_claim=("Hybrid work can separate tasks that need shared space from tasks that need quiet.", "A deliberate hybrid work pattern can match location to task instead of treating one location as universally superior.", "ハイブリッド勤務なら、共有空間が必要な作業と静けさが必要な作業を分けられます。", "意図的なハイブリッド勤務では、一つの場所を常に優れているとせず、作業に場所を合わせられます。"), opening_ja="今週は、在宅勤務と出社のどちらが多かったですか？", opening_ja_full="今週は、在宅勤務と職場へ行くことのどちらが多かったですか？", fallback="If neither applies, use study, care, a familiar role, or an imagined week.", fallback_ja="どちらも当てはまらなければ、学習、ケア、身近な役割、想像上の一週間でもかまいません。", fallback_full="Use a general or hypothetical role instead of assuming office work.", fallback_ja_full="職場勤務を前提にせず、一般的または仮定の役割でもかまいません。"),
    117: dict(slug="studying-in-a-cafe-or-at-home", title="Studying in a café or at home?", ko="카페 공부, 집 공부?", ja="カフェで勉強、それとも家？", a="studying in a café", b="studying at home", a_ja="カフェで勉強すること", b_ja="家で勉強すること", value_a="external structure", value_b="control and privacy", value_a_ja="外から得る区切り", value_b_ja="裁量とプライバシー", scene="concentration session", scene_ja="集中した場面", condition="noise, space, and task", condition_ja="音、空間、課題", condition_full="sensory conditions, accountability, and task demands", condition_full_ja="感覚的な環境、区切り、課題の要求", threshold="noise level", threshold_ja="音の大きさ", threshold_full="level of distraction", threshold_full_ja="気が散る度合い", a_when="leaving home creates useful structure", a_when_ja="家を出ることがよい区切りになる", a_when_full="ambient activity supports attention without interrupting it", a_when_full_ja="周囲の活動が邪魔せず集中を支える", b_when="privacy or control over the space matters", b_when_ja="プライバシーや空間の自由が大切になる", b_when_full="the task requires control, equipment, or sustained privacy", b_when_full_ja="課題に環境の裁量、設備、継続的なプライバシーが必要になる", new_claim=("Deep focus depends on the fit between the person, task, and setting.", "Deep focus is not tied to one location; it emerges when the setting matches the task and the person's attention pattern.", "深い集中は、人、課題、場所の相性で変わります。", "深い集中は一つの場所に決まるのではなく、環境が課題とその人の注意の特徴に合うと生まれます。"), opening_ja="最後に本当に集中できたとき、どこにいましたか？", opening_ja_full="最後に深く集中できたとき、どこにいましたか？", fallback="A work, hobby, familiar, or imagined concentration scene is fine.", fallback_ja="仕事、趣味、身近な例、想像上の集中場面でもかまいません。", fallback_full="Use any real or hypothetical focus task instead of assuming formal study.", fallback_ja_full="正式な学習を前提にせず、実際または仮定の集中課題でもかまいません。"),
    118: dict(slug="shopping-online-or-in-a-shop", title="Shopping online or in a shop?", ko="온라인 쇼핑, 매장 쇼핑?", ja="オンライン、それとも店で買い物？", a="shopping online", b="shopping in a shop", a_ja="オンラインで買うこと", b_ja="店舗で買うこと", value_a="range and convenience", value_b="direct inspection", value_a_ja="品ぞろえと便利さ", value_b_ja="実物の確認", scene="purchase or imagined purchase", scene_ja="購入または想像上の購入", condition="price, urgency, and uncertainty", condition_ja="価格、急ぎ、分からない点", condition_full="information quality, delivery risk, and sensory judgment", condition_full_ja="情報の質、配送リスク、感覚による判断", threshold="price or delivery time", threshold_ja="価格や配送時間", threshold_full="difference in total cost or certainty", threshold_full_ja="総費用や確実さの差", a_when="range or delivery saves meaningful time", a_when_ja="品ぞろえや配送で大きく時間を節約できる", a_when_full="search range and convenience outweigh uncertainty about the item", a_when_full_ja="品ぞろえと便利さが商品への不確かさを上回る", b_when="fit, quality, or immediate access matters", b_when_ja="合うか、品質、すぐ使えることが大切になる", b_when_full="direct inspection reduces a costly mismatch", b_when_full_ja="実物の確認で大きな買い間違いを減らせる", new_claim=("An in-store check can prevent a return when fit or texture matters.", "An in-store inspection can reduce uncertainty that specifications and reviews cannot remove.", "サイズや手触りが大切なら、店舗での確認によって返品を防げます。", "店舗で実物を確認すると、仕様やレビューだけではなくせない不確かさを減らせます。"), opening_ja="最後に何を買い、オンラインと店舗のどちらで買いましたか？", opening_ja_full="最後に買った物は何で、オンラインと店舗のどちらを使いましたか？", fallback="If nothing comes to mind, use a familiar or imagined purchase.", fallback_ja="思い浮かばなければ、身近な例や想像上の購入でもかまいません。", fallback_full="A public or hypothetical purchase can replace personal spending.", fallback_ja_full="個人の支出ではなく、公の例や仮定の購入でもかまいません。"),
    119: dict(slug="remembering-everything-or-forgetting-bad-memories", title="Remembering everything or forgetting bad memories?", ko="모두 기억하기, 나쁜 기억 잊기?", ja="すべて覚える、それとも嫌な記憶を忘れる？", a="remembering everything", b="forgetting bad memories", a_ja="すべてを覚えていること", b_ja="つらい記憶を忘れること", value_a="continuity and learning", value_b="relief", value_a_ja="つながりと学び", value_b_ja="苦しさからの解放", scene="fictional or general memory case", scene_ja="架空または一般的な記憶の事例", condition="harm, learning, and consent", condition_ja="苦しさ、学び、本人の意思", condition_full="psychological cost, identity, and control", condition_full_ja="心の負担、自分らしさ、本人の裁量", threshold="level of harm", threshold_ja="苦しさの程度", threshold_full="psychological burden", threshold_full_ja="心理的な負担", a_when="the memory protects learning or an important connection", a_when_ja="記憶が学びや大切なつながりを守る", a_when_full="continuity and evidence matter more than relief", a_when_full_ja="苦しさの軽減よりつながりや事実が重要になる", b_when="the memory causes repeated harm without useful control", b_when_ja="記憶が役立つ裁量なしに繰り返し苦しさを生む", b_when_full="relief from involuntary distress outweighs access to detail", b_when_full_ja="細部を覚えることより意思に反する苦しさからの解放が重要になる", new_claim=("A memory trigger can bring back a feeling before the full event is clear.", "A memory trigger may reactivate emotion before a person can place the memory in a coherent account.", "記憶のきっかけによって、出来事全体が分かる前に感情が戻ることがあります。", "記憶のきっかけは、出来事を一つの話として整理できる前に、感情を再び呼び起こすことがあります。"), opening_ja="すべてを覚えていることと、最悪の記憶を忘れることなら、どちらを選びますか？", opening_ja_full="すべてを覚えていることと、最もつらい記憶を忘れることなら、どちらを選びますか？", fallback="Keep personal memories private; a fictional or general case is fine.", fallback_ja="個人的な記憶は話さず、架空または一般的な事例でもかまいません。", fallback_full="Use a fictional, public, or hypothetical case instead of personal disclosure.", fallback_ja_full="個人的な開示ではなく、架空、公の例、仮定の事例でもかまいません。"),
    120: dict(slug="being-rich-and-anonymous-or-respected-on-an-ordinary-income", title="Being rich and anonymous or respected on an ordinary income?", ko="부유하고 무명, 평범한 수입과 존중?", ja="裕福で無名、それとも普通の収入で尊敬？", a="being rich and anonymous", b="being respected on an ordinary income", a_ja="裕福で無名であること", b_ja="普通の収入で尊敬されること", value_a="private freedom", value_b="social regard", value_a_ja="私的な自由", value_b_ja="周囲からの敬意", scene="public, fictional, or imagined life", scene_ja="公の例、架空、想像上の人生", condition="security, privacy, and responsibility", condition_ja="安心、プライバシー、責任", condition_full="wealth, recognition, accountability, and exposure", condition_full_ja="富、評価、説明責任、注目", threshold="income or public attention", threshold_ja="収入や注目の量", threshold_full="level of security or exposure", threshold_full_ja="安心や注目の水準", a_when="privacy and financial security are the main needs", a_when_ja="プライバシーと金銭的な安心が主な必要になる", a_when_full="wealth expands choice without creating unacceptable isolation", a_when_full_ja="富が受け入れられない孤立を生まず選択肢を増やす", b_when="trusted contribution matters more than wealth", b_when_ja="富より信頼される貢献が大切になる", b_when_full="social regard reflects meaningful contribution rather than status alone", b_when_full_ja="周囲の敬意が地位だけでなく意味ある貢献を表す", new_claim=("Anonymity can protect privacy without removing responsibility.", "Anonymity can reduce unwanted exposure, although it does not erase accountability for choices that affect others.", "無名でいることは、責任をなくさずにプライバシーを守れます。", "無名でいることは不要な注目を減らせますが、他者に影響する選択への説明責任まではなくしません。"), opening_ja="裕福で無名か、普通の収入で尊敬されるか、どちらを選びますか？", opening_ja_full="裕福で無名であることと、普通の収入で尊敬されることなら、どちらを選びますか？", fallback="Use a public, fictional, or imagined person; no income details are needed.", fallback_ja="公の人、架空、想像上の人物でもよく、収入の詳細は必要ありません。", fallback_full="Keep income and status private by using a public or hypothetical case.", fallback_ja_full="公の例や仮定の事例を使い、収入や地位は個人的に話さなくてかまいません。"),
    121: dict(slug="being-great-at-one-thing-or-good-at-many", title="Being great at one thing or good at many?", ko="한 가지에 뛰어나기, 여러 가지를 잘하기?", ja="一つに秀でる、それとも多くをこなす？", a="being great at one thing", b="being good at many things", a_ja="一つのことにとても優れること", b_ja="多くのことが得意であること", value_a="depth", value_b="range", value_a_ja="深さ", value_b_ja="広さ", scene="skill or role", scene_ja="技能や役割", condition="goal, team, and time", condition_ja="目標、チーム、時間", condition_full="task complexity, collaboration, and learning horizon", condition_full_ja="課題の複雑さ、協働、学ぶ期間", threshold="required depth", threshold_ja="必要な深さ", threshold_full="specialization requirement", threshold_full_ja="専門性の必要度", a_when="a difficult task rewards deep expertise", a_when_ja="難しい課題に深い専門性が役立つ", a_when_full="the cost of shallow knowledge is high", a_when_full_ja="浅い知識による負担が大きい", b_when="changing tasks require flexible support", b_when_ja="変わる課題に柔軟な対応が必要になる", b_when_full="coordination across domains creates more value than narrow mastery", b_when_full_ja="狭い熟達より分野をまたぐ調整が価値を生む", new_claim=("A generalist can connect problems that specialists see separately.", "A strong generalist can translate across fields and recognize relationships that narrow expertise may miss.", "幅広い技能を持つ人は、専門家が別々に見る問題をつなげられます。", "優れたジェネラリストは、分野の間をつなぎ、狭い専門性では見落とす関係に気づけます。"), opening_ja="今、何か一つにとても優れていますか、それとも多くのことが得意ですか？", opening_ja_full="今の自分は、一つにとても優れることと、多くのことが得意であることのどちらに近いですか？", fallback="A familiar, public, or imagined person is fine.", fallback_ja="身近、公の例、想像上の人物でもかまいません。", fallback_full="Use a public or hypothetical role instead of judging yourself.", fallback_ja_full="自分を評価せず、公の例や仮定の役割でもかまいません。"),
}


# The brief openings for these topics establish a fact, not a preference.  The
# two follow-ups keep that fact separate from the provisional A/B comparison;
# page 2 then carries both states forward instead of silently rewriting the
# learner's life as a choice.
FACTUAL_BRIDGES = {
    108: (("What does that real network give you now?", "Separately, would you prefer a wider circle, a smaller close circle, both, or neither?"), ("Which observable feature describes the learner's real network?", "As a provisional preference, would a wider network, a smaller close circle, both, or neither fit better?"), "Think of a situation involving that real network—or a public or imagined one. Which arrangement would fit that situation better?", "その実際の人間関係、または公の例や想像上の例について考えてください。広い交友関係、少数の親しい関係、両方、どちらでもない、のどれがその場面に合いますか？"),
    110: (("What made today's actual time necessary or possible?", "Separately, which schedule would fit you better: a morning schedule, a night schedule, both, or neither?"), ("Which constraint explains today's actual wake-up time?", "As a provisional preference, would a morning schedule, a night schedule, both, or neither fit better?"), "Use today, another real day, or an imagined schedule. Which schedule would fit the demands of that day?", "今日、別の実際の日、または想像上の予定を使ってください。その日の必要に合うのは、朝型の生活、夜型の生活、両方、どちらでもない、のどれですか？"),
    111: (("What actually made that trip planned or spontaneous?", "For a separate future or imagined trip, which style would you prefer?"), ("Which fact made the real trip planned or spontaneous?", "As a provisional preference for another trip, would planning, spontaneity, both, or neither fit?"), "Use that actual trip or a separate imagined one. Which travel style fit—or would fit—its needs?", "その実際の旅行、または別の想像上の旅行を使ってください。その必要に合った、または合うのはどの旅行スタイルですか？"),
    112: (("What actually made travelling alone or with others work on that trip?", "For another real or imagined trip, which arrangement would you prefer?"), ("Which fact explains the actual travel arrangement?", "As a provisional preference for another trip, would solo travel, company, both, or neither fit?"), "Use that actual trip or a separate imagined outing. Which company arrangement fit—or would fit—its purpose?", "その実際の旅行、または別の想像上の外出を使ってください。その目的に合った、または合うのは、一人、誰かと一緒、両方、どちらでもない、のどれですか？"),
    113: (("What factors shaped where you live, whether or not you chose it?", "Separately, which setting would suit a future or imagined situation?"), ("Which constraints explain the actual location, without assuming it was chosen?", "As a provisional preference for another situation, would city life, country life, both, or neither fit?"), "Use the place where you live without treating it as a choice—or use a public or imagined resident. Which setting fits that situation?", "今住んでいる場所を自分で選んだとは限らない形で使うか、公の例や想像上の住民を使ってください。その状況に合うのは都市、田舎、両方、どちらでもない、のどれですか？"),
    115: (("What do the actual hours and pay make possible now?", "For a separate future or hypothetical paid role, which side would you prefer?"), ("Which observable feature describes the actual role's time and pay?", "As a provisional preference for another paid role, would balance, salary, both, or neither fit?"), "Use the current role, another paid role, or a hypothetical paid role. Which side fits that role's needs?", "現在の仕事、別の有給の役割、または仮定の有給の役割を使ってください。その役割の必要に合うのは、ワークライフバランス、より高い給料、両方、どちらでもない、のどれですか？"),
    116: (("Which actual tasks were done at home or in a shared workplace?", "For a separate familiar or hypothetical role, which location would fit better?"), ("Which task requirements explain the actual locations used this week?", "As a provisional preference for another suitable role, would home, a shared workplace, both, or neither fit?"), "Use a familiar, public, or hypothetical paid or volunteer role where both locations are possible. Which location fits its tasks?", "在宅と共有の職場の両方が可能な、身近な例、公の例、または仮定の有給・ボランティアの役割を使ってください。作業に合うのはどの場所ですか？"),
    117: (("What conditions supported that actual concentration?", "For a separate task, would a café, home, both, or neither fit better?"), ("Which observable conditions supported the actual focus?", "As a provisional preference for another task, would a café, home, both, or neither fit?"), "Use that real task or a separate work, hobby, or imagined task. Which setting fit—or would fit—it?", "その実際の課題、または別の仕事、趣味、想像上の課題を使ってください。カフェ、家、両方、どちらでもない、のどれがその課題に合いますか？"),
    118: (("What actually decided the buying method last time?", "For a separate next or imagined purchase, which method would you prefer?"), ("Which observable constraint decided the actual buying method?", "As a provisional preference for another purchase, would online, a shop, both, or neither fit?"), "Use that actual purchase or a separate public or imagined purchase. Which method fit—or would fit—its needs?", "その実際の購入、または別の公の例や想像上の購入を使ってください。オンライン、店舗、両方、どちらでもない、のどれがその必要に合いますか？"),
    121: (("What evidence supports that description of your current skills?", "For a separate future or imagined role, which skill pattern would you prefer?"), ("Which observable evidence supports the actual skill description?", "As a provisional preference for another role, would depth, range, both, or neither fit?"), "Use a current skill fact without treating it as a choice—or use a public or imagined role. Which skill pattern fits that role?", "現在の技能の事実を選択だと扱わずに使うか、公の例や想像上の役割を使ってください。その役割に合うのは深い専門性、幅広い技能、両方、どちらでもない、のどれですか？"),
}

DECISION_VARIABLES = {
    107: ("weekly free hours", "一週間の自由な時間"), 108: ("the number of dependable relationships", "頼れる人間関係の数"),
    109: ("outdoor temperature", "外気温"), 110: ("required wake-up time", "必要な起床時刻"),
    111: ("the amount of advance planning", "事前に必要な計画の量"), 112: ("the need for shared coordination", "他の人との調整の必要度"),
    113: ("travel time to essential services", "必要なサービスまでの移動時間"), 114: ("safe indoor temperature", "安全な室温"),
    115: ("weekly discretionary hours", "一週間で自由に使える時間"), 116: ("commute time", "通勤時間"),
    117: ("background noise level", "周囲の騒音の大きさ"), 118: ("total purchase cost", "購入にかかる総額"),
    119: ("how much a memory affects daily life", "記憶が日常生活に与える影響"),
    120: ("the level of financial security", "経済的な安心度"), 121: ("weekly practice hours", "一週間の練習時間"),
}


def _cost_contract(number, data):
    a, b, aj, bj = data["a"], data["b"], data["a_ja"], data["b_ja"]
    if number == 114:
        return (
            "After safe cooling is guaranteed, what is the cost of losing internet, losing air conditioning, or using a workable mix?",
            "Treat unsafe heat as a health boundary, not a trade-off. Once safe cooling is available, what opportunity cost follows from each workable route?",
            "安全に涼める状態を確保した上で、インターネットを失うこと、エアコンを失うこと、実行可能な組み合わせのそれぞれにどんな負担がありますか？",
            "危険な暑さは損得の問題ではなく、健康上の限界として扱います。安全に涼める状態で、実行可能な各案にどんな機会費用がありますか？",
            ("Which workable cost is acceptable?", "Which route becomes unavailable if safe cooling cannot be guaranteed?"),
            ("Which sacrifice remains proportionate after the health boundary is met?", "Which option is invalid because safe cooling is unavailable?"),
        )
    if number == 119:
        return (
            "In the fictional case, what is lost under the remember-everything route, the forget-bad-memories route, an answer where both seem equally applicable, or neither route?",
            "In this explicitly fictional premise, compare the opportunity cost of each route, including equal applicability or neither, without treating memory as a real voluntary intervention.",
            "この架空の事例で、すべてを覚える場合、つらい記憶を忘れる場合、両方が同程度に当てはまる場合、どちらでもない場合に、それぞれ何が失われますか？",
            "実際に記憶を意思で操作できるとは考えず、明確に架空の設定として、両方が同程度に当てはまる場合やどちらも合わない場合も含め、各案の機会費用を比べてください。",
            ("Which fictional cost matters most?", "If neither route fits, what makes the premise incomplete?"),
            ("Which fictional sacrifice is proportionate to the benefit?", "If neither route is coherent, which missing safeguard explains that?"),
        )
    impossible_both = number in {109, 120}
    both_clause = "If the two options cannot literally happen together, treat 'both' as equal applicability, not simultaneous action. " if impossible_both else ""
    both_clause_ja = "二つを同時に実現できない場合、「両方」は同時に行うことではなく、どちらも同程度に当てはまることとして扱います。" if impossible_both else ""
    return (
        both_clause + f"What would a person give up by favouring {a}, favouring {b}, treating the options as equally applicable, or using a hypothetical case where neither fits?",
        both_clause + f"Compare the opportunity cost of favouring {a}, favouring {b}, treating the options as equally applicable, and using a bounded hypothetical case where neither fits.",
        both_clause_ja + f"{aj}、{bj}、両方が同程度に当てはまる場合、そしてどちらも合わない仮定の場合で、それぞれ何を手放しますか？",
        both_clause_ja + f"{aj}、{bj}、両方が同程度に当てはまる場合、どちらも合わない限定的な仮定の場合の機会費用を比べてください。",
        ("Which state's cost is acceptable in that case?", "Which cost makes that state unavailable?"),
        ("Which sacrifice remains proportionate in each applicable state?", "Which state is ruled out, and by what cost?"),
    )


# Normalize concepts that are states or schedules, not voluntary identities.
RAW_TOPICS[110].update(a="a morning schedule", b="a night schedule", a_ja="朝型の生活", b_ja="夜型の生活")
RAW_TOPICS[120].update(a="private wealth", b="respect on an ordinary income", a_ja="無名で裕福な生活", b_ja="普通の収入で得る尊敬")
RAW_TOPICS[121].update(a="deep expertise in one skill", b="broad ability across many skills", a_ja="一つの技能の深い専門性", b_ja="多くの技能にわたる幅広い能力")
RAW_TOPICS[115].update(
    fallback="If you do not have a current job, use a familiar, public, or hypothetical paid role.",
    fallback_ja="現在仕事をしていなければ、身近な例、公の例、または仮定の有給の役割を使ってください。",
)
RAW_TOPICS[116].update(
    fallback="If neither applies, use a familiar, public, or hypothetical role where both locations are possible.",
    fallback_ja="どちらも当てはまらなければ、両方の場所が可能な身近な例、公の例、または仮定の役割を使ってください。",
)
RAW_TOPICS[119].update(
    b_when="the fictional premise treats relief as more important than access to every detail",
    b_when_ja="架空の設定で、すべての細部を覚えることより苦しさの軽減を重く見る",
    b_when_full="the explicitly fictional case places relief above access to every detail",
    b_when_full_ja="明確に架空の事例で、すべての細部に触れることより苦しさの軽減を重く見る",
)
RAW_TOPICS[118].update(b_when_ja="商品が合うか、品質、すぐに使えることが大切になる")
RAW_TOPICS[110].update(opening_ja_full="今日は実際に何時に起きましたか？")
RAW_TOPICS[113].update(opening_ja_full="今どこに住んでいて、その場所は自分で選んだ結果ですか？")
RAW_TOPICS[112].update(
    fallback_ja_full="個人的な旅行を話さず、身近な例、公の例、または仮定の旅行者を使ってください。",
)
RAW_TOPICS[111].update(fallback_ja_full="個人的な旅行を話さず、近場の外出、身近な例、公の例、または仮定の旅行を使ってください。")
RAW_TOPICS[113].update(fallback_ja="身近な場所、公の例、または想像上の場所でもかまいません。")
RAW_TOPICS[120].update(fallback_ja="公に知られた人、架空の人、または想像上の人物でもかまいません。収入の詳細は必要ありません。")
RAW_TOPICS[121].update(fallback_ja="身近な人、公に知られた人、または想像上の人物でもかまいません。")
RAW_TOPICS[114].update(
    scene_prompt="First guarantee a safe indoor temperature. Then use a real, public, or imagined hot week: did losing internet, losing air conditioning, a workable mix, or neither route fit?",
    scene_prompt_ja="まず安全な室温を確保してください。その上で、実際の、公の、または想像上の暑い一週間で、インターネットを失う、エアコンを失う、実行可能な組み合わせ、どちらでもない、のどれが合うか考えてください。",
    scene_prompt_full="Treat unsafe heat as a firm health boundary. In a concrete public or hypothetical hot week with safe cooling, which workable route fits best?",
    scene_prompt_ja_full="危険な暑さは健康上の明確な限界として扱います。安全に涼める具体的な公の例や仮定の暑い一週間で、どの実行可能な案が最も合いますか？",
)
RAW_TOPICS[119].update(
    scene_prompt="Use a fictional or general case involving memory. In that premise, did remembering everything, forgetting bad memories, equal applicability, or neither fit better?",
    scene_prompt_ja="記憶に関する架空または一般的な事例を使ってください。その設定で、すべてを覚える、つらい記憶を忘れる、両方が同程度に当てはまる、どちらでもない、のどれがより合いますか？",
    scene_prompt_full="Use an explicitly fictional, public, or hypothetical memory premise instead of personal disclosure. Which route is most defensible in that premise?",
    scene_prompt_ja_full="個人的な開示ではなく、明確に架空の、公の、または仮定の記憶の設定を使ってください。その設定で、どの案が最も妥当ですか？",
)

for _number, _data in RAW_TOPICS.items():
    _data["decision_variable"], _data["decision_variable_ja"] = DECISION_VARIABLES[_number]
    _data["cost_contract"] = _cost_contract(_number, _data)
    if _number in FACTUAL_BRIDGES:
        _a_fus, _f_fus, _scene, _scene_ja = FACTUAL_BRIDGES[_number]
        if "both" not in _a_fus[1].casefold():
            _a_fus = (_a_fus[0], _a_fus[1].removesuffix("?") + ", or would both or neither fit?")
        _data.update(
            opening_followups=_a_fus, opening_followups_full=_f_fus,
            scene_prompt=_scene, scene_prompt_ja=_scene_ja,
            scene_prompt_full=_scene.replace("Think of", "Use").replace("Which", "For that separate case, which", 1),
            scene_prompt_ja_full="より具体的に、" + _scene_ja,
        )


TOPICS = {}
for _number, _data in RAW_TOPICS.items():
    _visible_data = {
        key: value for key, value in _data.items()
        if not key.startswith("fallback") and not key.startswith("opening_ja")
        and key not in {"cost_contract", "scene_prompt", "scene_prompt_ja", "scene_prompt_full", "scene_prompt_ja_full", "opening_followups", "opening_followups_full"}
    }
    TOPICS[_number] = {
        **_visible_data,
        "goal": (f"Let's compare {_data['a']} and {_data['b']}, then explain what could change your choice.", f"{_data['a_ja']}と{_data['b_ja']}を比べ、何が変われば選択も変わるか話しましょう。"),
        "article_title": ("What makes the choice change", "選択を変えるもの"),
        "articles": tuple(
            (accessible, full, japanese, japanese)
            for accessible, full, japanese in ARTICLE_HEADS[_number]
        ) + tuple(
            (accessible, full, japanese, japanese)
            for accessible, full, japanese in ARTICLE_TAILS[_number]
        ),
        "prompts": topic_prompts(_number, _data),
    }

CLAIM_ORDER = {number: tuple(f"ft{number}-c{index:02d}" for index in range(1, 11)) for number in TOPIC_NUMBERS}

NEW = {
    107: ("time-poor", "時間に余裕がない"), 108: ("inner circle", "親しい仲間の輪"), 109: ("seasonal extremes", "季節の極端さ"),
    110: ("body clock", "体内時計"), 111: ("last-minute plan", "直前の計画"), 112: ("shared itinerary", "共有する旅程"),
    113: ("city access", "都会の利用しやすさ"), 114: ("cooling", "涼しくすること"), 115: ("time autonomy", "時間の自由"),
    116: ("location flexibility", "場所を選べること"), 117: ("gentle accountability", "自然な継続のしやすさ"), 118: ("delivery", "配送"),
    119: ("memory trigger", "記憶のきっかけ"), 120: ("anonymity", "無名でいること"), 121: ("generalist", "幅広い技能を持つ人"),
}

VOCABULARY = {
    number: {
        "new": (NEW[number],),
        "recycled": (),
        "assumed": ((data["a"], data["a_ja"]), (data["b"], data["b_ja"])),
        "receptive": tuple(row for row in (
            ("trade-off", "両立しにくい関係"),
            ("less-favoured", "あまり重視しない"),
            ("opportunity cost", "機会費用"),
            (data["value_a"], data["value_a_ja"]),
            (data["value_b"], data["value_b_ja"]),
            (data["decision_variable"], data["decision_variable_ja"]),
        ) if row != NEW[number]),
    }
    for number, data in RAW_TOPICS.items()
}

def _new_surface(number, column):
    text = TOPICS[number]["articles"][2][column]
    match = re.search(re.escape(NEW[number][0]), text, re.I)
    if not match:
        raise ValueError((number, text, NEW[number][0]))
    return match.group()


def _full_gloss(number):
    return {1: ("trade-off", "trade-off", "両立しにくい関係")} if "trade-off" in TOPICS[number]["articles"][0][1] else {}


GLOSSES = {
    number: {
        "accessible": {3: (_new_surface(number, 0), NEW[number][0], NEW[number][1])},
        "full": _full_gloss(number),
    }
    for number in TOPIC_NUMBERS
}


def _vocabulary_meta(rows):
    return "; ".join("|".join(row) for row in rows)


def _render_dependencies():
    """Load renderer code lazily so importing the reviewed source stays pure."""
    authoring = pathlib.Path(__file__).parent
    if str(authoring) not in sys.path:
        sys.path.insert(0, str(authoring))
    import generate_ft_me_lately_batch as base  # noqa: PLC0415
    import new_lesson  # noqa: PLC0415
    return base, new_lesson


def output_path(topic_number, variant):
    if topic_number not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_number, variant))
    _base, new_lesson = _render_dependencies()
    course = f"{COURSE}-{variant}"
    slug = TOPICS[topic_number]["slug"]
    return new_lesson.ENGLISH / "tracks" / "3-freetalking" / "courses" / course / "lessons" / f"{topic_number:02d}-{slug}" / "lesson.html"


def _set_complete(head: str) -> str:
    marker = '<meta name="podo:proofread-status" content="complete">'
    head = re.sub(r'\n\s*<meta name="podo:proofread-status" content="(?:pending|complete)">', "", head)
    title_ja = re.search(r'(^\s*<meta name="podo:title-ja" content="[^"]*">\n)', head, re.MULTILINE)
    if not title_ja:
        raise ValueError("title-ja meta is required before proofread status")
    return head[:title_ja.end()] + f"  {marker}\n" + head[title_ja.end():]


def _article_page(topic_number, data, variant, base):
    en_col, ja_col = (0, 2) if variant == "accessible" else (1, 3)
    rows = []
    for index, (article, claim_id) in enumerate(zip(data["articles"], CLAIM_ORDER[topic_number], strict=True), 1):
        en_markup, words = base.marked_text(article[en_col], GLOSSES[topic_number][variant].get(index))
        rows.append(f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{base.esc(article[ja_col])}</span>{words}</span></div>')
    title, title_ja = data["article_title"]
    body = '      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>\n      <div class="tutor-note">Answer the learner\'s questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article.</div>\n      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">\n' + "\n".join(rows) + "\n      </div>"
    return base.page("article", title, title_ja, body)


def _question_page(page_id, number, item, variant, base):
    followups = "".join(f"<li>{base.esc(value)}</li>" for value in item[f"{variant}_followups"])
    japanese = item[f"{variant}_ja"]
    note_label = "Answer first, then follow up" if item["job"] == "tutor" else "Follow up"
    body = f'      <p class="section-subtitle ask"><span class="q-n">{number}</span><span class="ko">{base.esc(item[variant])}</span><span class="ja">{base.esc(japanese)}</span></p>\n      <div class="tutor-note"><div class="tn-body"><span class="tn-cap">{note_label}</span><ul class="tn-more">{followups}</ul></div></div>\n      <div class="fb" data-fb="{variant}-{page_id}" data-fb-spoken-label="Student\'s sentence"></div><div class="fb-adds"><button class="fb-add" data-add="fix" type="button">＋ Correction</button><button class="fb-add" data-add="note" type="button">＋ Note</button></div>'
    return base.page(page_id, item["title"], item["title_ja"], body)


def build(topic_number, variant):
    if topic_number not in TOPIC_NUMBERS or variant not in VARIANTS:
        raise ValueError((topic_number, variant))
    base, new_lesson = _render_dependencies()
    track = new_lesson.ENGLISH / "tracks/3-freetalking"
    canonical = (track / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html").read_text(encoding="utf-8")
    data = TOPICS[topic_number]
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_number:02d}-{data["slug"]}'
    head = new_lesson.retarget(
        head, review_id=f"FT-{topic_number}", lesson_id=slug,
        level="B1 accessible" if variant == "accessible" else "C1 full",
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-21",
    )
    head = _set_complete(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", _vocabulary_meta(VOCABULARY[topic_number][category]))
    goal_en, goal_ja = data["goal"]
    pages = [
        base.ft_contract.goal_page(
            title=data["title"], title_ja=data["ja"], topic_en=goal_en,
            topic_ja=goal_ja, data_act="Balance game", kicker="BALANCE GAME",
        ),
        _article_page(topic_number, data, variant, base),
        base.extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of the conversation.</span><span class="ja">全部の質問に答える必要はありません。会話の中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Use these pages as a flexible pool. Ask one question, react naturally, and share a brief real answer or relevant perspective of your own when it adds to the exchange. Skip freely and move to feedback with 2–3 minutes left.</div></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple((f"q{i}", f"QUESTION {i}") for i in range(1, 7))
    pages.extend(_question_page(page_id, number, item, variant, base) for (page_id, number), item in zip(prompt_ids, data["prompts"], strict=True))
    pages.append(base.extract_page(canonical, "feedback"))
    import ft_question_bank  # noqa: PLC0415
    return ft_question_bank.apply(new_lesson.redepth(head + "\n".join(pages) + foot, output_path(topic_number, variant)), topic_number, variant)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    for topic_number in TOPIC_NUMBERS:
        for variant in VARIANTS:
            output = output_path(topic_number, variant)
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_number, variant), encoding="utf-8")
            print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
