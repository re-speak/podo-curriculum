#!/usr/bin/env python3
"""The authored question bank for the English Freetalking track.

Eleven batch generators own eleven different topic-data shapes. This module is
the reviewable override layer for conversation repairs that need to survive
regeneration. Full is authored first as the strongest conversation; Accessible
changes only when that exact line creates a genuine B1 barrier. Identical rows
are intentional and valid.

This module is that place.  A row here overrides whatever a generator's own
topic table would have produced for one page of one variant, so a question is
authored once, next to its sibling, and read by both the generators and
``tools/authoring/check_freetalk_questions.py``.

    BANK[topic_no][page_id][variant] = (title, title_ja, prompt, prompt_ja, followups)

``apply`` is the only integration point: each generator calls it on the HTML it
has just built, and pages with no row are left exactly as they were.  That keeps
the migration incremental — an unconverted topic still generates from its own
table — while making the converted ones impossible to drift apart unnoticed.
"""

from __future__ import annotations

import html
import pathlib
import re

try:
    from ft_content_overrides import QUESTION_OVERRIDES, TOPIC_OVERRIDES
except ImportError:  # The bank remains usable while a proposal batch is being assembled.
    QUESTION_OVERRIDES = {}
    TOPIC_OVERRIDES = {}

PAGES = ("warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6")

# Full is the canonical conversation. Accessible differs only where the Full
# prompt creates a concrete B1 language or processing barrier. Every exception
# here is therefore an editorial decision, not an automatic level rewrite.
ACCESSIBLE_ADAPTATIONS = {
    (6, "q1"),
    (5, "warm-1"),
    (5, "warm-2"),
    (5, "q1"),
    (5, "q2"),
    (5, "q6"),
    (38, "warm-1"),
    (38, "q5"),
    (104, "q6"),
}
VARIANTS = ("accessible", "full")

LABELS = {
    "warm-1": "WARM-UP 1",
    "warm-2": "WARM-UP 2",
    "q1": "QUESTION 1",
    "q2": "QUESTION 2",
    "q3": "QUESTION 3",
    "q4": "QUESTION 4",
    "q5": "QUESTION 5",
    "q6": "QUESTION 6",
}

VOCABULARY_OVERRIDES = {
    9: {"new": "worth the money|値段に見合う"},
    38: {
        "accessible": {"new": "", "recycled": "exhausted|疲れ切った|CORE-52"},
        "full": {"new": "drained|疲れ切った"},
    },
    42: {"new": "family rule|家族のルール"},
    54: {"new": "stay close|親しさを保つ"},
    55: {"new": ""},
    63: {"new": ""},
}


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


BANK: dict[int, dict[str, dict[str, tuple]]] = {}


def rows(topic_no: int, page_id: str):
    """Return the two authored variants of one page, or None when unconverted."""
    return BANK.get(topic_no, {}).get(page_id)


def has(topic_no: int) -> bool:
    return topic_no in BANK


def apply(source: str, topic_no: int, variant: str) -> str:
    """Rewrite every banked question page of one built deck.

    The generators differ in how they assemble a deck but agree on what a
    question page looks like once assembled, so this works on the rendered HTML
    rather than on eleven incompatible topic tables.
    """
    if topic_no not in BANK and topic_no not in QUESTION_OVERRIDES and topic_no not in TOPIC_OVERRIDES:
        return source
    source = re.sub(
        r'(<meta name="podo:proofread-status" content=")[^"]*(")',
        r'\g<1>pending\2',
        source,
        count=1,
    )
    if topic_no in TOPIC_OVERRIDES:
        source = _replace_topic(source, topic_no, TOPIC_OVERRIDES[topic_no], variant)
    source = _replace_vocabulary(source, topic_no, variant)

    pages = dict(BANK.get(topic_no, {}))
    pages.update(QUESTION_OVERRIDES.get(topic_no, {}))
    if topic_no in TOPIC_OVERRIDES:
        pages.update(TOPIC_OVERRIDES[topic_no].get("questions", {}))
    for page_id, variants in pages.items():
        # Full is the authored source. An Accessible row is active only when
        # its exact page is recorded as a real B1 adaptation; older batch data
        # still contains now-retired "make every pair differ" rewrites.
        if variant == "accessible" and not _has_explicit_accessible(topic_no, page_id):
            item = variants["full"]
        else:
            item = variants.get(variant) or variants["full"]
        title, title_ja, prompt, prompt_ja, followups = item
        source = _replace_page(source, page_id, title, title_ja, prompt, prompt_ja, followups)
    return source


def _replace_topic(source: str, topic_no: int, topic: dict, variant: str) -> str:
    title_en = topic["title_en"]
    title_ja = topic["title_ja"]
    title_ko = topic["title_ko"]
    for language, value in (("en", title_en), ("ja", title_ja), ("ko", title_ko)):
        source = re.sub(
            rf'(<meta name="podo:title-{language}" content=")[^"]*(")',
            lambda match, value=value: f'{match.group(1)}{_esc(value)}{match.group(2)}',
            source,
            count=1,
        )
    source = re.sub(r'<title>.*?</title>', f'<title>{_esc(title_en)} — PODO English</title>', source, count=1)

    goal_start, goal_end = _page_bounds(source, "lesson-goal")
    goal = source[goal_start:goal_end]
    goal = re.sub(
        r'(<h2 class="transition-title">).*?(</h2>)',
        lambda match: (
            f'{match.group(1)}{_esc(title_en)} '
            f'<span class="title-ja">({_esc(title_ja)})</span>{match.group(2)}'
        ),
        goal,
        count=1,
        flags=re.S,
    )
    if "goal_en" in topic:
        goal_en = topic["goal_en"].strip()
        if not goal_en.lower().startswith("let"):
            goal_en = f"Let's {goal_en[0].lower()}{goal_en[1:]}"
        if not goal_en.endswith((".", "?", "!")):
            goal_en += "."
        goal_en += " Please read the title aloud."
        goal_ja = topic["goal_ja"].strip()
        if not goal_ja.endswith("。"):
            goal_ja += "。"
        goal_ja += "タイトルを声に出して読んでください。"
        goal = re.sub(
            r'(<p class="section-subtitle"><span class="ko">).*?(</span><span class="ja">).*?(</span></p>)',
            lambda match: (
                f'{match.group(1)}{_esc(goal_en)}{match.group(2)}'
                f'{_esc(goal_ja)}{match.group(3)}'
            ),
            goal,
            count=1,
            flags=re.S,
        )
    source = source[:goal_start] + goal + source[goal_end:]

    if "articles" in topic:
        article_start, article_end = _page_bounds(source, "article")
        article = source[article_start:article_end]
        article = re.sub(
            r'(<h2 class="section-title">).*?(</h2>)',
            lambda match: (
                f'{match.group(1)}{_esc(topic["article_title_en"])} '
                f'<span class="title-ja">({_esc(topic["article_title_ja"])})</span>{match.group(2)}'
            ),
            article,
            count=1,
            flags=re.S,
        )
        rows = []
        for index, (full_en, accessible_en, japanese) in enumerate(topic["articles"], start=1):
            english = accessible_en if variant == "accessible" else full_en
            rows.append(
                '        <div class="sent" role="button" tabindex="0" '
                f'data-sync-option="s{index}" data-claim-id="ft-{topic_no}-replacement-{index}">'
                '<span class="s-line"><span class="s-ko">'
                f'{_esc(english)}</span><span class="s-mark" aria-hidden="true"></span></span>'
                f'<span class="s-open"><span class="s-ja">{_esc(japanese)}</span></span></div>'
            )
        article = re.sub(
            r'(<div class="sents" data-sync-id="article-open"[^>]*>).*?(\n      </div>)',
            lambda match: f'{match.group(1)}\n' + "\n".join(rows) + match.group(2),
            article,
            count=1,
            flags=re.S,
        )
        source = source[:article_start] + article + source[article_end:]

        for field in ("new", "recycled", "assumed", "receptive"):
            value = "conversation|会話; experience|経験; choice|選択" if field == "assumed" else ""
            source = re.sub(
                rf'(<meta name="podo:vocabulary:{field}" content=")[^"]*(")',
                lambda match, value=value: f'{match.group(1)}{value}{match.group(2)}',
                source,
                count=1,
            )
    return source


def _replace_vocabulary(source: str, topic_no: int, variant: str) -> str:
    override = VOCABULARY_OVERRIDES.get(topic_no)
    if not override:
        return source
    values = override.get(variant, override)
    for field, value in values.items():
        source = re.sub(
            rf'(<meta name="podo:vocabulary:{field}" content=")[^"]*(")',
            lambda match, value=value: f'{match.group(1)}{value}{match.group(2)}',
            source,
            count=1,
        )
    return source


def _page_bounds(source: str, page_id: str) -> tuple[int, int]:
    marker = f'data-page-id="{page_id}"'
    marker_at = source.find(marker)
    if marker_at < 0:
        raise SystemExit(f"question bank: page {page_id!r} missing from deck")
    start = source.rfind('<div ', 0, marker_at)
    end = source.find('\n    <div ', marker_at)
    if end < 0:
        end = source.index('\n  </div>', marker_at)
    return start, end


def normalize_course_pairs(track: pathlib.Path, course: str) -> int:
    """Make Full the source question pool, preserving only explicit B1 adaptations."""
    accessible_root = track / "courses" / f"{course}-accessible" / "lessons"
    full_root = track / "courses" / f"{course}-full" / "lessons"
    changed = 0
    for accessible_path in sorted(accessible_root.glob("*/lesson.html")):
        full_path = full_root / accessible_path.parent.name / "lesson.html"
        if not full_path.exists():
            continue
        accessible = accessible_path.read_text(encoding="utf-8")
        full = full_path.read_text(encoding="utf-8")
        review = re.search(r'<meta name="podo:review-id" content="FT-(\d+)">', full)
        if not review:
            raise SystemExit(f"question bank: missing FT review id in {full_path}")
        topic_no = int(review.group(1))
        accessible = normalize_accessible_pair(full, accessible, topic_no)
        if accessible != accessible_path.read_text(encoding="utf-8"):
            accessible_path.write_text(accessible, encoding="utf-8")
            changed += 1
    return changed


def normalize_accessible_pair(full: str, accessible: str, topic_no: int) -> str:
    """Return an Accessible deck whose question pool follows the Full source.

    This is pure so a batch generator can enforce the pair contract before it
    writes anything. ``normalize_course_pairs`` remains the bulk repair path
    for already-rendered courses.
    """
    for page_id in PAGES:
        if _has_explicit_accessible(topic_no, page_id):
            continue
        accessible = _copy_question_bundle(full, accessible, page_id)
    return accessible


def _has_explicit_accessible(topic_no: int, page_id: str) -> bool:
    return (topic_no, page_id) in ACCESSIBLE_ADAPTATIONS


def _copy_question_bundle(full: str, accessible: str, page_id: str) -> str:
    full_start, full_end = _page_bounds(full, page_id)
    lower_start, lower_end = _page_bounds(accessible, page_id)
    full_page = full[full_start:full_end]
    lower_page = accessible[lower_start:lower_end]
    patterns = (
        r'<h2 class="section-title">.*?</h2>',
        r'<p class="section-subtitle ask">.*?</p>',
        r'<ul class="tn-more">.*?</ul>',
    )
    for pattern in patterns:
        source_match = re.search(pattern, full_page, flags=re.S)
        if not source_match:
            raise SystemExit(f"question bank: missing question bundle field on {page_id}")
        lower_page, count = re.subn(
            pattern,
            lambda _match, replacement=source_match.group(0): replacement,
            lower_page,
            count=1,
            flags=re.S,
        )
        if count != 1:
            raise SystemExit(f"question bank: could not normalize {page_id}")
    return accessible[:lower_start] + lower_page + accessible[lower_end:]


def _replace_page(source, page_id, title, title_ja, prompt, prompt_ja, followups):
    start = source.find(f'<div class="section" data-page-id="{page_id}">')
    if start < 0:
        raise SystemExit(f"question bank: page {page_id!r} missing from deck")
    end = source.find('\n    <div ', start + 1)
    if end < 0:
        end = source.index('\n  </div>', start)
    block = source[start:end]

    block = re.sub(
        r'(<h2 class="section-title">).*?(</h2>)',
        lambda m: f'{m.group(1)}{_esc(title)} <span class="title-ja">({_esc(title_ja)})</span>{m.group(2)}',
        block,
        count=1,
        flags=re.S,
    )
    block = re.sub(
        r'(<span class="q-n">[^<]+</span>)<span class="ko">.*?</span><span class="ja">.*?</span>',
        lambda m: f'{m.group(1)}<span class="ko">{_esc(prompt)}</span><span class="ja">{_esc(prompt_ja)}</span>',
        block,
        count=1,
        flags=re.S,
    )
    lis = "".join(f"<li>{_esc(q)}</li>" for q in followups)
    block = re.sub(
        r'(<ul class="tn-more">).*?(</ul>)',
        lambda m: f'{m.group(1)}{lis}{m.group(2)}',
        block,
        count=1,
        flags=re.S,
    )
    return source[:start] + block + source[end:]

# ---------------------------------------------------------------------------
# Authored pilot topics. Read a row top-to-bottom: the two variants of one page
# sit next to each other, so an Accessible adaptation can be reviewed against
# its Full source rather than written in isolation.
# ---------------------------------------------------------------------------

BANK[3] = {
    "warm-1": {
        "accessible": ("Something good lately", "最近おいしかったもの",
            "What's the best thing you've eaten recently?", "最近食べた中で、いちばんおいしかったものは何ですか？",
            ["Where did you eat it?", "What did you eat yesterday?"]),
        "full": ("Worth the trip", "わざわざ行く価値",
            "What's the last thing you ate that was worth going out of your way for?", "最近食べたもので、わざわざ出かける価値があったものは何ですか？",
            ["What made it worth the trip?", "Would you go back just for that?"]),
    },
    "warm-2": {
        "accessible": ("How it tastes", "どんな味",
            "How would you describe the taste to me?", "その味を私にどう説明しますか？",
            ["Is it sweet, salty, or something else?", "Is it soft or crunchy?"]),
        "full": ("Sell it to me", "売り込む",
            "How would you describe that dish to someone who has never had it?", "それを食べたことがない人に、その料理をどう説明しますか？",
            ["What would make me order it?", "What would you not mention?"]),
    },
    "q1": {
        "accessible": ("One dish for me", "私に一つ",
            "If I came to Japan, what would you make me eat first?", "私が日本に来たら、まず何を食べさせますか？",
            ["Why that one first?", "Where would we go to eat it?"]),
        "full": ("Only one meal", "一食だけなら",
            "If I could only eat one Japanese meal in my life, what should it be?", "一生に一度だけ日本の食事をするなら、何を食べるべきですか？",
            ["Why that over something more famous?", "Who would disagree with your choice?"]),
    },
    "q2": {
        "accessible": ("When and where", "いつ、どこで",
            "When is that dish at its best?", "その料理は、いつがいちばんおいしいですか？",
            ["Does the season change it?", "At home or in a restaurant?"]),
        "full": ("Changed abroad", "海外で変わる",
            "What would ruin that dish if a foreign restaurant changed it?", "海外の店がその料理を変えるとしたら、何を変えたら台無しですか？",
            ["What has to stay the same?", "Have you eaten a bad version of it?"]),
    },
    "q3": {
        "accessible": ("Who you eat it with", "誰と食べる",
            "Who do you usually eat it with?", "それはふだん誰と食べますか？",
            ["Did someone introduce it to you?", "Do you ever eat it alone?"]),
        "full": ("Too famous", "有名すぎる",
            "Which famous Japanese dish gets more attention than it deserves?", "有名な日本料理で、評価が高すぎると思うものは何ですか？",
            ["What do visitors miss because of it?", "What should get that attention instead?"]),
    },
    "q4": {
        "accessible": ("A warning", "注意すること",
            "What should I know before I try it?", "食べる前に、私は何を知っておくべきですか？",
            ["Does it smell strong?", "How do people eat it — chopsticks, hands, a spoon?"]),
        "full": ("A warning", "忠告しておくこと",
            "Which Japanese food would you warn me about before I ordered it?", "私が注文する前に、忠告しておきたい日本料理は何ですか？",
            ["What catches people out — the smell, the texture, or the look?", "Did it take you time to like it?"]),
    },
    "q5": {
        "accessible": ("From my country", "私の国から",
            "What food from my country do you want to try?", "私の国の料理で、食べてみたいものは何ですか？",
            ["Where did you hear about it?", "Have you seen it anywhere in Japan?"]),
        "full": ("A straight trade", "交換するなら",
            "What do you think I get wrong about Japanese food?", "日本の食べ物について、私が誤解していそうなことは何だと思いますか？",
            ["Where does that idea come from?", "What would you show them instead?"]),
    },
    "q6": {
        "accessible": ("The opposite", "逆に",
            "Now the opposite — what famous Japanese food do you not really like?", "逆に、有名な日本料理で、あまり好きではないものは何ですか？",
            ["What don't you like about it?", "Do your friends agree with you?"]),
        "full": ("The opposite", "逆に",
            "Now the opposite — which famous Japanese dish would you tell me to skip?", "逆に、私に「食べなくていい」と言いたい有名な日本料理はどれですか？",
            ["Where would you send me instead?", "Why do you think it got famous?"]),
    },
}

BANK[4] = {
    "warm-1": {
        "accessible": ("Your last meal with someone", "最近の食事",
            "Who did you last eat a meal with?", "最近、誰と食事をしましたか？",
            ["Where were you?", "What did you eat?"]),
        "full": ("Caught out", "迷った場面",
            "When were you last unsure what to do at someone else's table?", "人の家や店の食卓で、どうすればいいか迷ったのはいつですか？",
            ["What did you do in the end?", "Did anyone notice?"]),
    },
    "warm-2": {
        "accessible": ("At that table", "その食卓で",
            "What do you always do at the table without thinking about it?", "食卓で、何も考えずにいつもしていることは何ですか？",
            ["Do you say anything before you start?", "What do you do with your bowl or your hands?"]),
        "full": ("Reading the table", "場を読む",
            "How do you work out the rules at an unfamiliar table?", "慣れない食卓では、ルールをどうやって見抜きますか？",
            ["Who do you watch first?", "Has that ever gone wrong?"]),
    },
    "q1": {
        "accessible": ("Normal at home", "家では普通",
            "What do you do at the table that feels completely normal to you?", "食卓で、自分にとってはまったく普通だと感じることは何ですか？",
            ["Who taught you that?", "Do your friends do it too?"]),
        "full": ("Strangest to me", "私には奇妙に見えること",
            "Which of your table habits would look strangest to me?", "あなたの食卓の習慣で、私にはいちばん奇妙に見えそうなものは何ですか？",
            ["What does it actually mean?", "Would you drop it at my table?"]),
    },
    "q2": {
        "accessible": ("Who starts", "誰から始める",
            "In your family, who starts eating first?", "あなたの家では、誰が最初に食べ始めますか？",
            ["What do you say before eating?", "Is it different in a restaurant?"]),
        "full": ("Eating with your boss", "上司との食事",
            "At a meal with your boss, what would you change about how you eat?", "上司との食事では、食べ方の何を変えますか？",
            ["What would you never change?", "Who decides when the meal is over?"]),
    },
    "q3": {
        "accessible": ("A difference you saw", "気づいた違い",
            "Have you ever eaten with someone from another country?", "ほかの国の人と食事をしたことがありますか？",
            ["What did they do differently?", "What would you like to ask me about my table?"]),
        "full": ("Rude or just different", "失礼か、違うだけか",
            "When is a table habit rude, and when is it just different?", "食卓の習慣が失礼なときと、ただ違うだけのときの違いは何ですか？",
            ["Has someone judged you unfairly for it?", "Would you correct a visitor at your table?"]),
    },
    "q4": {
        "accessible": ("Home and restaurant", "家と店",
            "Do you eat differently at home and in a restaurant?", "家と店では、食べ方が変わりますか？",
            ["Which one is more relaxed?", "What exactly changes?"]),
        "full": ("Whose rules win", "どちらのやり方",
            "When you and I eat together, whose table rules should we follow?", "あなたと私が一緒に食べるとき、どちらのやり方に合わせますか？",
            ["Does it change if you're the host?", "Who usually gives way?"]),
    },
    "q5": {
        "accessible": ("Who taught you", "誰に教わった",
            "Who taught you your table manners?", "食事のマナーは、誰に教わりましたか？",
            ["Were they strict about it?", "Do you still follow all of it?"]),
        "full": ("Worth defending", "守る価値",
            "Which Japanese table rule would you defend to a foreigner?", "外国人に対して、守る価値があると言える日本の食事マナーはどれですか？",
            ["What's the reason behind it?", "Which one is hardest to defend?"]),
    },
    "q6": {
        "accessible": ("The opposite", "逆に",
            "Now the opposite — is there a table rule you were taught but don't follow?", "逆に、教わったけれど守っていない食事のルールはありますか？",
            ["When did you stop?", "Would you follow it in front of your family?"]),
        "full": ("The opposite", "逆に",
            "Now the opposite — which table rule would you quietly drop?", "逆に、あなたなら静かにやめてしまいたい食事のルールはどれですか？",
            ["Who still cares about it?", "What would be lost?"]),
    },
}

BANK[9] = {
    "warm-1": {
        "accessible": ("The last thing you bought", "最近買ったもの",
            "What's the last thing you bought for yourself?", "最近、自分のために買ったものは何ですか？",
            ["When did you buy it?", "Roughly how much was it?"]),
        "full": ("Talked into it", "自分を納得させて",
            "What's the last thing you bought after hesitating?", "最近、迷ったすえに買ったものは何ですか？",
            ["What were you unsure about?", "Were you right in the end?"]),
    },
    "warm-2": {
        "accessible": ("Before you bought it", "買う前",
            "How long did you think about it before you bought it?", "買うまでに、どのくらい迷いましたか？",
            ["What were you worried about?", "Did anyone push you to buy it?"]),
        "full": ("Your own test", "自分の基準",
            "What makes you decide a purchase was worth it?", "買ってよかったと思う決め手は何ですか？",
            ["When did you last break your own rule?", "Where did that rule come from?"]),
    },
    "q1": {
        "accessible": ("Worth the money", "買ってよかったもの",
            "What have you bought that was really worth the money?", "買ってよかったと本当に思うものは何ですか？",
            ["How often do you use it?", "Would you buy it again?"]),
        "full": ("Earned it back", "元が取れたもの",
            "Which of your purchases has earned its price back?", "これまでの買い物で、値段の元が取れたと言えるものはどれですか？",
            ["How do you know?", "What would have happened if you'd bought the cheap version?"]),
    },
    "q2": {
        "accessible": ("In your day", "毎日の中で",
            "When do you use it most?", "それをいちばんよく使うのはいつですか？",
            ["What did you use before it?", "Could you live without it now?"]),
        "full": ("Changed the routine", "習慣を変えたもの",
            "Which purchase changed a routine instead of just adding to your things?", "物が増えただけでなく、習慣そのものを変えた買い物はどれですか？",
            ["What did it replace?", "Would you notice if it disappeared tomorrow?"]),
    },
    "q3": {
        "accessible": ("What changed", "変わったこと",
            "What changed in your day after you bought it?", "それを買ってから、毎日の何が変わりましたか？",
            ["Did anyone else notice?", "Was that what you expected?"]),
        "full": ("Cheap twice", "安物買いの銭失い",
            "Which do you regret more: buying cheap twice, or overpaying once?", "安物を二度買うのと、一度高く払いすぎるのと、どちらを後悔しますか？",
            ["Which have you done more often?", "What did that teach you?"]),
    },
    "q4": {
        "accessible": ("The price", "値段を見たとき",
            "How did you feel when you first saw the price?", "最初に値段を見たとき、どう感じましたか？",
            ["Did you wait for a sale?", "Do you still think about the price?"]),
        "full": ("Whose advice", "誰の意見",
            "Whose spending advice do you actually take?", "お金の使い方について、あなたが本当に聞き入れるのは誰の意見ですか？",
            ["Why theirs and not someone else's?", "When did you ignore it?"]),
    },
    "q5": {
        "accessible": ("Next", "次に買うもの",
            "What do you want to buy next?", "次に買いたいものは何ですか？",
            ["What's stopping you?", "Who would you ask about it?"]),
        "full": ("Sell it to me", "売り込む",
            "What would you say to someone who thought it was too expensive?", "「それは高すぎる」と言う人に、あなたは何と答えますか？",
            ["What is your strongest reason?", "Has anyone actually said that to you?"]),
    },
    "q6": {
        "accessible": ("The opposite", "逆に",
            "Now the opposite — what did you buy and then regret?", "逆に、買ったあとで後悔したものは何ですか？",
            ["What made you regret it?", "Where is it now?"]),
        "full": ("The opposite", "逆に",
            "Now the opposite — what did you buy that turned out to be a mistake?", "逆に、買ってみて失敗だったものは何ですか？",
            ["Was it the wrong thing, or the wrong time?", "Did you tell anyone?"]),
    },
}

BANK[11] = {
    "warm-1": {
        "accessible": ("Right now", "今見ているもの",
            "Are you watching anything at the moment?", "今、何か見ている作品はありますか？",
            ["What's it called?", "What was the last thing you finished?"]),
        "full": ("Keeping you up", "夜更かしの原因",
            "What's currently keeping you up later than you planned?", "今、予定より夜更かしさせている作品は何ですか？",
            ["How many episodes in are you?", "When did it get its hooks in?"]),
    },
    "warm-2": {
        "accessible": ("How far in", "どこまで見た",
            "How far into it are you?", "今、どのあたりまで見ましたか？",
            ["How long have you been watching it?", "How many episodes in one sitting?"]),
        "full": ("The hook", "引きの作り方",
            "What makes you start the next episode instead of stopping?", "止めずに次の話を再生してしまうのは、なぜですか？",
            ["Does that still work on you?", "When does it stop working?"]),
    },
    "q1": {
        "accessible": ("Why you keep going", "見続ける理由",
            "Why do you keep watching it?", "なぜ見続けてしまうのですか？",
            ["What happens at the end of each episode?", "Is it the story or the people?"]),
        "full": ("Good, or just started", "面白いから？始めたから？",
            "Are you still watching because it's good, or because you started?", "まだ面白いから見ているのですか、始めてしまったから見ているのですか？",
            ["How many episodes do you give a show?", "What was the last one you abandoned?"]),
    },
    "q2": {
        "accessible": ("One character", "好きな人物",
            "Which character do you like most?", "いちばん好きな登場人物は誰ですか？",
            ["What do they do that you like?", "Who do you not like?"]),
        "full": ("Defending someone", "擁護したくなる人物",
            "Which character would you defend to someone who hated them?", "嫌っている人に対して、あなたが擁護したくなる登場人物は誰ですか？",
            ["What do people get wrong about them?", "Who do you find it hard to defend?"]),
    },
    "q3": {
        "accessible": ("Alone or together", "一人か誰かと",
            "Do you watch it alone or with someone?", "それは一人で見ますか、誰かと見ますか？",
            ["Does that change how you watch?", "Who would you watch it with?"]),
        "full": ("Weekly or all at once", "週一か一気見か",
            "Which ruins a story more for you: waiting a week, or watching eight in a row?", "物語を台無しにするのは、一週間待つことと、八話一気に見ること、あなたにとってはどちらですか？",
            ["Which do you actually do?", "Which show proved your point?"]),
    },
    "q4": {
        "accessible": ("Late night", "夜更かし",
            "How late have you stayed up watching something?", "何かを見ていて、何時まで起きていたことがありますか？",
            ["What happened the next day?", "Do you still do it?"]),
        "full": ("The ending", "結末",
            "Which ending were you angry about?", "結末に腹が立った作品は何ですか？",
            ["What should it have done instead?", "Did it ruin the rest for you?"]),
    },
    "q5": {
        "accessible": ("Recommending it", "勧めるなら",
            "Who would you recommend it to?", "それを誰に勧めたいですか？",
            ["What would you tell them about it?", "Would I like it?"]),
        "full": ("Sell it to me", "売り込む",
            "How would you get someone to start watching it?", "どうやって人にその作品を見始めさせますか？",
            ["What would you tell them first?", "Who would not enjoy it?"]),
    },
    "q6": {
        "accessible": ("The opposite", "逆に",
            "Now the opposite — what did you finish but wouldn't recommend?", "逆に、最後まで見たけれど人には勧めない作品は何ですか？",
            ["Why did you keep going?", "Where did it go wrong?"]),
        "full": ("The opposite", "逆に",
            "Now the opposite — which popular show did you give up on?", "逆に、人気があるのに途中でやめた作品は何ですか？",
            ["How far did you get?", "What would make you go back?"]),
    },
}

BANK[16] = {
    "warm-1": {
        "accessible": ("Something new", "初めてのこと",
            "What's something you tried for the first time this year?", "今年、初めてやってみたことは何ですか？",
            ["When was that?", "What did you do last weekend that was new?"]),
        "full": ("A complete beginner", "まったくの初心者",
            "What's the last thing you were a complete beginner at?", "最近、まったくの初心者として始めたことは何ですか？",
            ["How long ago was that?", "How long did the beginner feeling last?"]),
    },
    "warm-2": {
        "accessible": ("That day", "その日",
            "Who were you with that day?", "その日は誰と一緒でしたか？",
            ["Where did you go?", "Whose idea was it?"]),
        "full": ("Who saw you", "見られること",
            "Who was watching while you were bad at it?", "下手なところを、誰に見られていましたか？",
            ["Did that change how you tried?", "Would you rather have gone alone?"]),
    },
    "q1": {
        "accessible": ("Before you started", "始める前",
            "How did you feel before you started?", "始める前は、どんな気持ちでしたか？",
            ["Were you nervous or excited?", "Did you nearly cancel?"]),
        "full": ("What you got wrong", "見当違いだったこと",
            "What did you get completely wrong about it beforehand?", "始める前、そのことについて完全に見当違いだったことは何ですか？",
            ["Where did that idea come from?", "Who could have told you?"]),
    },
    "q2": {
        "accessible": ("The surprise", "意外だったこと",
            "What was different from what you expected?", "想像していたことと、何が違いましたか？",
            ["Was it easier or harder?", "What did nobody tell you?"]),
        "full": ("Being bad in public", "人前で下手なこと",
            "Where don't you mind being bad at something in front of people?", "人前で下手でも気にならないのは、どんな場面ですか？",
            ["Where would you never risk it?", "Has that changed as you got older?"]),
    },
    "q3": {
        "accessible": ("How you did", "できばえ",
            "Were you a complete beginner, or had you tried something similar?", "まったくの初心者でしたか、それとも似たことをやったことがありましたか？",
            ["Were you any good at it?", "Who was better than you?"]),
        "full": ("How many tries", "何回試すか",
            "How many tries do you give something before you decide it's not for you?", "自分に向いていないと判断するまでに、何回試しますか？",
            ["What did you quit too early?", "What did you stick with too long?"]),
    },
    "q4": {
        "accessible": ("Again?", "もう一度",
            "Would you do it again?", "もう一度やりますか？",
            ["What would you do differently?", "Who would you take with you?"]),
        "full": ("Alone or with someone", "一人か経験者と",
            "Is a first time better alone, or with someone who's done it before?", "初めてのことは、一人でやるのと、経験者と一緒にやるのと、どちらがいいですか？",
            ["Which did you do?", "When does help get in the way?"]),
    },
    "q5": {
        "accessible": ("Next one", "次は",
            "What do you want to try next?", "次は何をやってみたいですか？",
            ["What's stopping you?", "When could you actually do it?"]),
        "full": ("Talk me into it", "私を誘うなら",
            "What would you say to someone who was nervous about trying it?", "それを試すのが不安な人に、あなたは何と言いますか？",
            ["What would you warn them about?", "What would they need to bring?"]),
    },
    "q6": {
        "accessible": ("The opposite", "逆に",
            "Now the opposite — what did you try once and never again?", "逆に、一度やって二度とやらなかったことは何ですか？",
            ["What put you off?", "Would you try it with a different person?"]),
        "full": ("The opposite", "逆に",
            "Now the opposite — what did you only need to try once?", "逆に、一度試せば十分だったことは何ですか？",
            ["What exactly put you off?", "Do you regret trying it at all?"]),
    },
}

# The first pilot was written under an incorrect "every pair must differ"
# contract. The content-lead review corrected that: these Accessible lines are
# the more natural, immediately answerable questions, and none contains a real
# B1 barrier. They therefore become the Full source questions too. Keeping this
# normalization beside the pilot data makes the correction explicit while the
# broader corpus is migrated into this bank.
for _topic_no in (3, 4, 9, 11, 16):
    for _page in BANK[_topic_no].values():
        _page["full"] = _page["accessible"]
