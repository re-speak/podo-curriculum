from __future__ import annotations

import ast
import hashlib
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys
import types
import unittest


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_love_and_marriage_batch.py")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
TOC_ROOT = REPO_ROOT / "sandbox/drafts/en/tracks/3-freetalking/toc"
REVIEW_ROOT = REPO_ROOT / "sandbox/drafts/en/page-reviews"
TRACKS = REPO_ROOT / "sandbox/drafts/en/tracks"
PILOTS = (
    TRACKS / "3-freetalking/courses/talk-between-two-countries-accessible/lessons/01-this-surprised-me/lesson.html",
    TRACKS / "3-freetalking/courses/talk-between-two-countries-full/lessons/01-this-surprised-me/lesson.html",
)

EXPECTED_TOPICS = {
    57: ("a-little-thing-that-makes-you-like-someone", "A little thing that makes you like someone"),
    58: ("a-relationship-deal-breaker", "A relationship deal-breaker"),
    59: ("something-you-could-never-compromise-on-in-a-partner", "Something you could never compromise on in a partner"),
    60: ("a-relationship-habit-you-know-you-should-change", "A relationship habit you know you should change"),
    61: ("one-thing-your-wedding-would-have-to-include", "One thing your wedding would have to include"),
    62: ("a-breakup-that-was-hard-to-get-over", "A breakup that was hard to get over"),
    63: ("choosing-not-to-marry-or-have-children", "Choosing not to marry or have children"),
}
EXPECTED_OPENINGS = {
    57: "What's something small that makes you like someone?",
    58: "Which is harder to forgive: a lie, an insult, or a broken promise?",
    59: "What's one thing you could never compromise on in a partner?",
    60: "Which relationship habit do you think is hardest to change?",
    61: "If you had a wedding tomorrow, what's the one thing you'd insist on?",
    62: "Why can some breakups be so hard to get over?",
    63: "Why might someone choose not to marry or have children?",
}
EXPECTED_FORMATS = {57: "story", 58: "story", 59: "story", 60: "story", 61: "story", 62: "story", 63: "opinion"}
EXPECTED_SHARED = {number: f"KR 6-{number - 56}" for number in EXPECTED_TOPICS}
EXPECTED_RETRIEVAL = {
    57: (("It's usually something small, like ___.", ("CORE-43",), False), ("I didn't expect to ___.", (), True)),
    58: (("The moment someone says ___, I'm done.", ("CORE-58",), False), ("I couldn't get past ___.", (), True)),
    59: (("I could live without ___, but not ___.", ("CORE-66", "CORE-56"), False), ("It's not negotiable.", (), True)),
    60: (("I know I ___ too much.", ("CORE-17",), False), ("I've got better at ___ing.", ("CORE-49",), False)),
    61: (("I'd definitely want ___.", ("CORE-66",), False), ("I'd rather not ___.", ("CORE-97",), False)),
    62: (("It took me ___ to ___.", ("CORE-51",), True), ("Looking back, I should have ___.", ("CORE-71",), False)),
    63: (("I can see why ___.", ("CORE-62",), False), ("To be fair, ___.", ("CORE-93",), False)),
}
EXPECTED_NEW = {
    57: ("small gesture", "ささやかな行動"),
    58: ("deal-breaker", "どうしても受け入れられないこと"),
    59: ("compromise on", "〜について妥協する"),
    60: ("shut down", "心を閉ざす"),
    61: ("wedding tradition", "結婚式の習慣"),
    62: ("get over", "立ち直る"),
    63: ("social pressure", "社会的な圧力"),
}
EXPECTED_RECYCLED = {
    57: (("small", "小さい", "CORE-43"),),
    58: (), 59: (),
    60: (("too much", "多すぎる", "CORE-34"),),
    61: (), 62: (), 63: (),
}
PROMPT_KEYS = {
    "job", "title", "title_ja", "accessible", "accessible_ja",
    "accessible_followups", "full", "full_ja", "full_followups", "safety",
}

batch = None


def _batch_module_name() -> str:
    if __package__:
        return f"{__package__}.generate_ft_love_and_marriage_batch"
    return "generate_ft_love_and_marriage_batch"


def _load_batch():
    global batch
    if batch is None:
        batch = importlib.import_module(_batch_module_name())
    return batch


def _load_vocabulary():
    if __package__:
        return importlib.import_module(f"{__package__}.vocabulary")
    return importlib.import_module("vocabulary")


def _article_corpus(topic_no: int, variant: str) -> str:
    module = _load_batch()
    column = 0 if variant == "accessible" else 1
    return " ".join(row[column] for row in module.TOPICS[topic_no]["articles"])


def _visible_prompt_corpus(topic_no: int, variant: str) -> str:
    """Only the rendered question counts; tutor-private follow-ups never do."""
    module = _load_batch()
    return " ".join(item[variant] for item in module.TOPICS[topic_no]["prompts"])


def _vocab_rows(topic_no: int, category: str) -> tuple[tuple[str, ...], ...]:
    module = _load_batch()
    raw = module.VOCABULARY[topic_no][category]
    return tuple(tuple(part.strip() for part in row.split("|")) for row in raw.split(";") if row.strip())


def _review_id(source: str) -> str:
    match = re.search(r'<meta name="podo:review-id" content="([^"]+)">', source)
    if not match:
        raise AssertionError("deck has no canonical review id")
    return match.group(1)


class AAImportSafetyTests(unittest.TestCase):
    def test_import_isolated_before_any_batch_import_and_preserves_pilots(self) -> None:
        self.assertIsNone(batch)
        script = r'''
import builtins, hashlib, importlib, json, pathlib, sys
generator_dir = pathlib.Path(sys.argv[1])
pilots = tuple(pathlib.Path(value) for value in sys.argv[2:])
sys.path.insert(0, str(generator_dir))
before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in pilots}
calls = []
original_builtin_open = builtins.open
original_path_open = pathlib.Path.open
original_read_text = pathlib.Path.read_text
original_read_bytes = pathlib.Path.read_bytes
def blocked(name):
    def call(*args, **kwargs):
        calls.append(name + ":" + str(args[0] if args else ""))
        raise AssertionError("filesystem access during source-module import")
    return call
builtins.open = blocked("open")
pathlib.Path.open = blocked("Path.open")
pathlib.Path.read_text = blocked("Path.read_text")
pathlib.Path.read_bytes = blocked("Path.read_bytes")
try:
    module = importlib.import_module("generate_ft_love_and_marriage_batch")
finally:
    builtins.open = original_builtin_open
    pathlib.Path.open = original_path_open
    pathlib.Path.read_text = original_read_text
    pathlib.Path.read_bytes = original_read_bytes
after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in pilots}
print(json.dumps({
    "calls": calls,
    "before": before,
    "after": after,
    "renderer_modules": [name for name in ("generate_ft_me_lately_batch", "new_lesson") if name in sys.modules],
    "has_root": hasattr(module, "ROOT"),
    "has_track": hasattr(module, "TRACK"),
}, sort_keys=True))
'''
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(
            [sys.executable, "-c", script, str(GENERATOR.parent), *(str(path) for path in PILOTS)],
            check=True, capture_output=True, text=True, env=env,
        )
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["calls"], [])
        self.assertEqual(evidence["before"], evidence["after"])
        self.assertEqual(evidence["renderer_modules"], [])
        self.assertFalse(evidence["has_root"])
        self.assertFalse(evidence["has_track"])


class FreetalkingLoveAndMarriageSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_batch()

    def test_authoritative_briefs_lock_openings_formats_sources_and_moves(self) -> None:
        self.assertEqual(batch.TOPIC_FORMAT, EXPECTED_FORMATS)
        self.assertEqual(batch.SHARED_SOURCE, EXPECTED_SHARED)
        self.assertEqual(batch.TOC_RETRIEVAL, EXPECTED_RETRIEVAL)
        self.assertTrue(batch.TOC_RETRIEVAL_AUDIT_ONLY)
        self.assertEqual(batch.BRIEF_OPENINGS, EXPECTED_OPENINGS)
        for topic_no in EXPECTED_TOPICS:
            brief = (TOC_ROOT / f"FT-{topic_no}.md").read_text(encoding="utf-8")
            with self.subTest(topic=topic_no):
                self.assertIn("The track TOC is authoritative.", brief)
                self.assertIn(f'- **Format:** {EXPECTED_FORMATS[topic_no]}', brief)
                self.assertIn(f'- **Opening:** "{EXPECTED_OPENINGS[topic_no]}"', brief)
                self.assertIn(f'- **Shared source:** {EXPECTED_SHARED[topic_no]}', brief)
                for move, owners, is_chunk in EXPECTED_RETRIEVAL[topic_no]:
                    self.assertIn(f"`{move}`", brief)
                    for owner in owners:
                        self.assertIn(owner.replace("CORE-", "Core "), brief)
                    if is_chunk:
                        self.assertIn("`chunk`", brief)

    def test_exact_topic_inventory_identity_and_visible_openings(self) -> None:
        self.assertEqual(batch.COURSE, "talk-love-and-marriage")
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED_TOPICS))
        self.assertEqual(tuple(batch.TOPICS), batch.TOPIC_NUMBERS)
        for topic_no, (slug, title) in EXPECTED_TOPICS.items():
            opening = batch.TOPICS[topic_no]["prompts"][0]["accessible"]
            with self.subTest(topic=topic_no):
                self.assertEqual(batch.TOPICS[topic_no]["slug"], slug)
                self.assertEqual(batch.TOPICS[topic_no]["title"], title)
                self.assertEqual(opening, EXPECTED_OPENINGS[topic_no])

    def test_all_70_claims_use_exact_four_column_schema(self) -> None:
        rows = 0
        for topic in batch.TOPICS.values():
            self.assertEqual(len(topic["articles"]), 10)
            for row in topic["articles"]:
                rows += 1
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 4)
                self.assertTrue(all(isinstance(value, str) and value for value in row))
                accessible, full, accessible_ja, full_ja = row
                self.assertTrue(accessible.endswith("."))
                self.assertTrue(full.endswith("."))
                self.assertTrue(accessible_ja.endswith("。"))
                self.assertTrue(full_ja.endswith("。"))
                self.assertNotEqual(accessible, full)
                self.assertNotEqual(accessible_ja, full_ja)
        self.assertEqual(rows, 70)

    def test_all_56_prompts_have_exact_keys_types_and_jobs(self) -> None:
        total = 0
        for topic in batch.TOPICS.values():
            prompts = topic["prompts"]
            self.assertEqual(len(prompts), 8)
            self.assertEqual(prompts[0]["job"], "opening")
            self.assertEqual(prompts[-1]["job"], "flip")
            self.assertEqual(len({item["job"] for item in prompts}), 8)
            for item in prompts:
                total += 1
                self.assertEqual(set(item), PROMPT_KEYS)
                for key in PROMPT_KEYS - {"accessible_followups", "full_followups"}:
                    self.assertIsInstance(item[key], str)
                    self.assertTrue(item[key])
                for variant in batch.VARIANTS:
                    self.assertEqual(item[variant].count("?"), 1)
                    self.assertEqual(item[f"{variant}_ja"].count("？"), 1)
                    followups = item[f"{variant}_followups"]
                    self.assertIsInstance(followups, tuple)
                    self.assertIn(len(followups), (2, 3))
                    self.assertEqual(len(followups), len(set(followups)))
                    self.assertTrue(all(isinstance(value, str) and value.endswith("?") for value in followups))
        self.assertEqual(total, 56)

    def test_claim_ids_are_stable_ordered_and_pair_identical(self) -> None:
        all_ids = []
        for topic_no in batch.TOPIC_NUMBERS:
            expected = tuple(f"ft{topic_no}-c{index:02d}" for index in range(1, 11))
            self.assertEqual(batch.CLAIM_ORDER[topic_no], expected)
            all_ids.extend(expected)
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_reviewed_bilingual_claim_repairs_are_exact(self) -> None:
        exact = {
            (58, 3): (
                "A cruel joke can reveal disrespect even when the speaker calls it humour.",
                "Calling a remark a joke does not remove the contempt or disrespect it may reveal.",
                "残酷な冗談をユーモアだと呼んでも、相手への敬意のなさが表れることがあります。",
                "発言を「冗談」と呼んでも、そこに表れた軽蔑や敬意の欠如が消えるわけではありません。",
            ),
            (58, 6): (
                "Ending an interaction quickly can protect an important boundary.",
                "Ending an interaction immediately can be a legitimate way to protect a serious boundary.",
                "やり取りをすぐに終えることが、大切な境界線を守る方法になる場合があります。",
                "やり取りを直ちに終えることが、重大な境界線を守る正当な方法になることもあります。",
            ),
            (59, 5): (
                "Experience can make a long list of requirements shorter or more precise.",
                "Experience may shrink an unrealistic checklist while making a few essential boundaries more precise.",
                "経験によって、条件の長いリストが短くなったり、より具体的になったりします。",
                "経験を重ねると、現実的でない条件のリストが短くなる一方、少数の大切な境界線がより明確になることがあります。",
            ),
            (60, 1): (
                "Relationship habits often appear most clearly under stress.",
                "Relationship patterns often become most visible when stress reduces our patience and flexibility.",
                "関係の中での癖は、ストレスがあるときにはっきり表れることがよくあります。",
                "ストレスで忍耐力や柔軟性が低下すると、関係の中の傾向が最も見えやすくなります。",
            ),
            (60, 5): (
                "Shame can make us defensive instead of helping us change.",
                "When feedback produces shame, defensiveness may protect the habit rather than correct it.",
                "恥ずかしさが強いと、変わるよりも身構えてしまうことがあります。",
                "指摘によって恥ずかしさが強まると、防御的な反応がその癖を直すどころか守ってしまうことがあります。",
            ),
            (60, 7): (
                "Progress is not perfect, and an old habit may return in a hard week.",
                "Improvement is rarely linear; an old pattern may reappear when circumstances become difficult.",
                "改善は完璧には進まず、大変な週には昔の癖が戻ることもあります。",
                "改善は一直線ではなく、状況が厳しくなると古い傾向が再び表れることがあります。",
            ),
            (61, 3): (
                "Guests, cost, family wishes, and tradition can pull the plan in different directions.",
                "Guest expectations, budget, family wishes, and tradition can create competing demands.",
                "招待客、費用、家族の希望、伝統によって、計画が別々の方向に引っ張られることがあります。",
                "招待客の期待、予算、家族の希望、伝統から、互いに競合する要求が生じることがあります。",
            ),
            (62, 1): (
                "There is no correct amount of time to get over a breakup.",
                "Recovery from a breakup has no universal schedule or correct emotional pace.",
                "別れから立ち直るのに、誰にでも当てはまる正しい期間はありません。",
                "別れからの回復には、誰にでも当てはまる予定や、「正しい」と言える感情の進み方はありません。",
            ),
            (63, 3): (
                "Reasons can include desire, health, money, care work, freedom, or values.",
                "Choices may reflect desire, health, finances, caregiving, freedom, relationships, or deeply held values.",
                "理由には、希望、健康、費用、人を支える責任、自由、価値観などがあります。",
                "選択には、希望、健康、経済状況、誰かを支える責任、自由、人間関係、強い価値観が関わります。",
            ),
            (63, 6): (
                "Relatives may worry about loneliness, regret, or family continuity.",
                "Family concern may focus on future loneliness, regret, care, or continuity across generations.",
                "家族は、将来の孤独や後悔、家族のつながりが続くかどうかを心配する場合があります。",
                "家族は、将来の孤独、後悔、ケア、家族が次の世代へ続くかどうかを心配することがあります。",
            ),
        }
        required = {
            (60, 1): ("忍耐力や柔軟性が低下",),
            (60, 5): ("指摘によって恥ずかしさが強まる",),
            (60, 7): ("改善は完璧には進まず", "改善は一直線ではなく"),
            (61, 3): ("計画が別々の方向に引っ張られる", "互いに競合する要求"),
            (62, 1): ("正しい期間", "「正しい」と言える感情の進み方"),
            (63, 3): ("人を支える責任", "誰かを支える責任"),
            (63, 6): ("家族のつながりが続くかどうか", "家族が次の世代へ続くかどうか"),
        }
        for key, row in exact.items():
            self.assertEqual(batch.TOPICS[key[0]]["articles"][key[1] - 1], row)
        for key, fragments in required.items():
            row = batch.TOPICS[key[0]]["articles"][key[1] - 1]
            for fragment in fragments:
                self.assertIn(fragment, " ".join(row[2:]))

    def obsolete_critical_prompt_en_aja_fja_rows_are_exact(self) -> None:
        exact = {
            (57, 1): (
                "What's something small that makes you like someone?", "どんな小さなことで、人を好きになりますか？",
                "Which small gesture or quality can make you start liking someone?", "どんな小さな特徴や行動がきっかけで、人を好きになり始めますか？",
            ),
            (57, 2): (
                "What might that small detail suggest about the person?", "その小さな点から、その人についてどんなことを感じますか？",
                "What might you infer from that small quality or gesture?", "その小さな特徴や行動から、どんなことを感じ取りますか？",
            ),
            (57, 3): (
                "Have you ever told the person that you liked that small thing about them—or would you keep it to yourself?", "その小さなところが好きだと本人に伝えたことはありますか。それとも、自分の中だけにしておきますか？",
                "Have you ever named that small attraction to the person, or would you leave it unspoken?", "その小さな魅力を本人に伝えたことはありますか。それとも、言葉にせずにおきますか？",
            ),
            (59, 4): (
                "Has your list of important qualities changed, stayed the same, or have you never kept a list?", "大切な特徴のリストは変わりましたか、変わっていませんか、それとも、もともとリストを作っていませんか？",
                "Has your list of essential qualities evolved, remained stable, or have you never maintained a list?", "大切な特徴のリストは変化しましたか、変わらずにいますか、それとも、そもそもリストを持っていませんか？",
            ),
            (60, 7): (
                "If it is your habit, what could you do instead; if it is a general example, what could the person do?", "自分の癖なら自分が、一般的な例ならその人が、代わりに何をできますか？",
                "If the pattern is yours, which replacement behaviour could you use; in a general case, which response could the person use?", "自分の傾向なら自分が、一般的な例ならその人が、どの代替行動を使えますか？",
            ),
            (60, 8): (
                "For your own case or a general example, which healthy relationship habit is worth keeping?", "自分の例でも一般的な例でも、続ける価値があるのはどの健全な関係の習慣ですか？",
                "For your own case or a general example, which healthy pattern should remain while the unhelpful one changes?", "自分の例でも一般的な例でも、役立たない傾向を変える間、残すべきなのはどの健全な傾向ですか？",
            ),
            (61, 1): (
                "If you had a wedding tomorrow, what's the one thing you'd insist on?", "もし明日結婚式をするとしたら、絶対に入れたいものを一つ挙げるとしたら何ですか？",
                "If you were holding a wedding tomorrow, which single element would be essential?", "もし明日結婚式を行うなら、欠かせない要素を一つ選ぶとしたら何ですか？",
            ),
            (62, 1): (
                "As much as you want to say — what's the hardest one you've been through? A personal, familiar, fictional, or general example is fine, and you may skip specifics.", "話せる範囲で、経験した中でいちばん立ち直るのが難しかった別れはどんなものでしたか？ 自分の経験、身近な話、作品、一般的な例のどれでもよく、具体的な話は省けます。",
                "As much as feels safe, which breakup was hardest to recover from? A personal, familiar, fictional, or general case is welcome, and specifics may remain private.", "安心して話せる範囲で、立ち直るのが最も難しかった別れはどれですか？ 自分の経験、身近な話、作品、一般的な事例のどれでもよく、具体的な内容は伏せられます。",
            ),
            (62, 2): (
                "What can change after a relationship ends?", "関係が終わったあと、何が変わることがありますか？",
                "Which immediate changes can follow the end of a relationship?", "関係が終わった直後には、どのような変化が起こり得ますか？",
            ),
            (62, 3): (
                "What affects how long it takes to recover from a breakup?", "別れから立ち直るまでの時間には、何が影響しますか？",
                "Which factors shape the pace of recovery after a relationship ends?", "関係が終わったあとの回復の速さは、どのような要因に左右されますか？",
            ),
            (62, 4): (
                "What affects whether someone tells other people about a breakup?", "別れについて誰かに話すかどうかには、何が影響しますか？",
                "Which factors influence whether someone seeks support after a breakup?", "別れたあとに支えを求めるかどうかは、どのような要因に左右されますか？",
            ),
            (62, 7): (
                "What would you tell the person in your example—or someone in general—at the beginning of a breakup?", "自分の例の人、または一般的な誰かに、別れたばかりの時点で何を伝えますか？",
                "What would you tell the person in your case—or someone in general—at the earliest stage of a breakup?", "自分の事例の人、または一般的な誰かに、別れの最も早い段階で何を伝えますか？",
            ),
            (63, 2): (
                "What reason does the person in that real, familiar, or public example give, if any?", "その実際、身近、または公に知られた例の人は、理由があるとすれば何と説明していますか？",
                "What reason, if any, is given in that real, familiar, or public example?", "その実際、身近、または公に知られた例では、理由があるとすれば何ですか？",
            ),
            (63, 5): (
                "How can family or social expectations influence decisions about marriage or children?", "家族や社会の期待は、結婚や子どもについての決定にどう影響しますか？",
                "How do family and social expectations shape decisions about marriage or parenthood?", "家族や社会の期待は、結婚や親になることについての決定をどう左右しますか？",
            ),
            (63, 8): (
                "How can people respond respectfully to decisions about marriage or children?", "結婚や子どもについての決定に、どうすれば敬意を持って応じられますか？",
                "What makes a response to decisions about marriage or parenthood genuinely respectful?", "結婚や親になることについての決定に対して、真に敬意ある応答とはどのようなものですか？",
            ),
        }
        for (topic_no, prompt_no), expected in exact.items():
            item = batch.TOPICS[topic_no]["prompts"][prompt_no - 1]
            actual = (item["accessible"], item["accessible_ja"], item["full"], item["full_ja"])
            self.assertEqual(actual, expected)

    def obsolete_reviewed_followups_deepen_instead_of_repeating_or_administering(self) -> None:
        exact = {
            (57, 1): (
                ("In what situation does it become noticeable?", "What first draws your attention to it?"),
                ("In which situation does the gesture or quality become noticeable?", "What first makes it stand out?"),
            ),
            (60, 7): (
                ("For your own habit, what might get in the way the first time you try the new response?", "For a general example, what support could make the replacement easier?"),
                ("For your own pattern, which obstacle could block the replacement under stress?", "For a general case, what support could make the replacement sustainable?"),
            ),
            (62, 1): (
                ("For a personal example, which part feels safe to discuss?", "For a familiar, fictional, or general example, what made the ending difficult?"),
                ("For a personal case, which aspect feels safe to examine?", "For a familiar, fictional, or general case, what made the ending difficult?"),
            ),
            (62, 2): (
                ("In a personal, familiar, or fictional example, what changed first?", "Without a specific example, which consequence often appears first?"),
                ("In a personal, familiar, or fictional case, which immediate consequence mattered most?", "Without a specific case, which consequence tends to emerge first?"),
            ),
            (62, 3): (
                ("If recovery moved forward in the example, what showed that change?", "If it is ongoing or not getting easier yet, what makes progress hard to judge?", "Without a specific example, which factor generally changes the timeline?"),
                ("If recovery progressed in the case, which sign marked that change?", "If it remains ongoing or stalled, what makes progress difficult to assess?", "Without a specific case, which factor generally shapes the timeline most strongly?"),
            ),
            (62, 4): (
                ("In a personal, familiar, or fictional example, who knew and what support helped?", "If the experience stayed private or the discussion is general, what can make privacy feel necessary?"),
                ("In a personal, familiar, or fictional case, which form of support was available?", "If the experience remained private or the case is general, what purpose can privacy serve?"),
            ),
            (63, 5): (
                ("If your own family is relevant, how is the expectation expressed?", "If there is no family context or discussion to draw on, which wider social expectation matters?", "If personal details are private or the answer is general, which boundary keeps the discussion respectful?"),
                ("If your own family is relevant, how is the expectation communicated?", "If there is no family context or discussion to draw on, which broader social expectation carries weight?", "If personal details remain private or the case is general, which boundary should the conversation respect?"),
            ),
            (63, 8): (
                ("For a settled choice, how should a response work whether it matches yours or differs?", "For an undecided or private choice, what should nobody demand?", "In a general discussion, which comment keeps the conversation neutral?"),
                ("For a settled choice, how should the response work whether it aligns with yours or diverges?", "For an unresolved or private choice, which explanation should nobody demand?", "In a general discussion, which wording preserves neutrality?"),
            ),
        }
        for (topic_no, prompt_no), (accessible, full) in exact.items():
            item = batch.TOPICS[topic_no]["prompts"][prompt_no - 1]
            self.assertEqual(item["accessible_followups"], accessible)
            self.assertEqual(item["full_followups"], full)

        q7 = batch.TOPICS[60]["prompts"][6]
        accessible_general = q7["accessible_followups"][1].casefold()
        full_general = q7["full_followups"][1].casefold()
        self.assertIn("support", accessible_general)
        self.assertIn("support", full_general)
        self.assertNotIn("evidence", accessible_general + " " + full_general)

        q1 = batch.TOPICS[62]["prompts"][0]
        q2 = batch.TOPICS[62]["prompts"][1]
        q1_corpus = " ".join((q1["accessible"], *q1["accessible_followups"], q1["full"], *q1["full_followups"])).casefold()
        q2_corpus = " ".join((q2["accessible"], *q2["accessible_followups"], q2["full"], *q2["full_followups"])).casefold()
        self.assertIn("difficult", q1_corpus)
        for event_word in ("change", "consequence", "after", "first"):
            self.assertIn(event_word, q2_corpus)
        for repeated_cause in ("difficult", "get over", "recovery", "loss"):
            self.assertNotIn(repeated_cause, q2_corpus)

    def test_learner_prompts_are_substantive_and_practically_readable(self) -> None:
        learner_mains = []
        for topic in batch.TOPICS.values():
            for item in topic["prompts"]:
                for variant in batch.VARIANTS:
                    english = item[variant]
                    japanese = item[f"{variant}_ja"]
                    learner_mains.append(english.casefold())
                    self.assertLessEqual(len(english.split()), 30)
                    self.assertLessEqual(len(english), 165)
                    self.assertLessEqual(len(japanese), 82)
        corpus = " ".join(learner_mains)
        for old in (
            "would you like to use a real person",
            "would you prefer a real person",
            "for the route you chose",
            "for the route you selected",
            "or are you speaking generally",
            "or are you examining the timing in general",
            "would you describe an expectation",
            "would you examine an expectation",
            "say there is no relevant family context",
            "answer generally",
            "answer in general terms",
        ):
            self.assertNotIn(old, corpus)

    def test_reviewed_prompts_are_standalone_unique_and_not_defensive(self) -> None:
        mains = []
        followups = []
        banned = (
            "if yes", "if not", "if it ", "if they ", "if someone ",
            "if nobody", "if none", "for a real", "for a general",
            "real or imagined", "real or hypothetical", "general example",
            "familiar example", "fictional example", "you may use",
            "is enough", "comes to mind",
        )
        referent_openers = ("that ", "this ", "the person in", "in your example")
        for topic in batch.TOPICS.values():
            for item in topic["prompts"]:
                self.assertEqual(item["safety"], "standalone-opinion-or-scenario")
                for variant in batch.VARIANTS:
                    main = item[variant]
                    folded = main.casefold()
                    self.assertFalse(folded.startswith(referent_openers), main)
                    self.assertFalse(any(phrase in folded for phrase in banned), main)
                    mains.append(folded)
                    for followup in item[f"{variant}_followups"]:
                        followups.append(followup.casefold())
                        self.assertFalse(any(phrase in followup.casefold() for phrase in banned), followup)
        self.assertEqual(len(mains), 112)
        self.assertEqual(len(mains), len(set(mains)))
        self.assertEqual(len(followups), len(set(followups)))

    def test_accessible_and_full_are_intellectually_paired_but_independently_worded(self) -> None:
        for topic in batch.TOPICS.values():
            for item in topic["prompts"]:
                self.assertNotEqual(item["accessible"], item["full"])
                self.assertNotEqual(item["accessible_ja"], item["full_ja"])
                self.assertNotEqual(item["accessible_followups"], item["full_followups"])
            for accessible, full, accessible_ja, full_ja in topic["articles"]:
                self.assertNotEqual(accessible, full)
                self.assertNotEqual(accessible_ja, full_ja)

    def test_openings_are_answerable_without_relationship_history(self) -> None:
        self.assertEqual(
            {number: batch.TOPICS[number]["prompts"][0]["accessible"] for number in batch.TOPIC_NUMBERS},
            EXPECTED_OPENINGS,
        )
        corpus = " ".join(EXPECTED_OPENINGS.values()).casefold()
        for assumed in ("your partner", "your relationship", "have you ever", "do you know anyone"):
            self.assertNotIn(assumed, corpus)

    def obsolete_reviewed_semantic_chain_locks_and_old_copy_negatives(self) -> None:
        p57 = batch.TOPICS[57]["prompts"]
        self.assertEqual(p57[1]["job"], "meaning")
        self.assertEqual(p57[1]["accessible"], "What might that small detail suggest about the person?")
        self.assertIn("what would make you hold back", p57[2]["full_followups"][1].casefold())

        p59 = batch.TOPICS[59]["prompts"][3]
        for variant in batch.VARIANTS:
            chain = " ".join((p59[variant], *p59[f"{variant}_followups"])).casefold()
            states = ("changed", "same", "no list") if variant == "accessible" else ("evolved", "stable", "no list")
            for state in states:
                self.assertIn(state, chain)

        for index in (6, 7):
            p60 = batch.TOPICS[60]["prompts"][index]
            for variant in batch.VARIANTS:
                chain = " ".join((p60[variant], *p60[f"{variant}_followups"])).casefold()
                self.assertIn("your own", chain)
                self.assertIn("general", chain)

        opening62 = batch.TOPICS[62]["prompts"][0]
        for route in ("personal", "familiar", "fictional", "general", "skip"):
            self.assertIn(route, opening62["accessible"].casefold())
        duration62 = batch.TOPICS[62]["prompts"][2]
        for variant in batch.VARIANTS:
            chain = " ".join((duration62[variant], *duration62[f"{variant}_followups"])).casefold()
            states = ("moved forward", "ongoing", "not getting easier", "general") if variant == "accessible" else ("progress", "ongoing", "stall", "general")
            for state in states:
                self.assertIn(state, chain)

        p63 = batch.TOPICS[63]["prompts"]
        self.assertIn("public example", p63[1]["accessible"].casefold())
        for variant in batch.VARIANTS:
            family = " ".join((p63[4][variant], *p63[4][f"{variant}_followups"])).casefold()
            for state in ("family", "no ", "discussion", "general"):
                self.assertIn(state, family)
            close = " ".join((p63[7][variant], *p63[7][f"{variant}_followups"])).casefold()
            for state in ("settled", "private", "general"):
                self.assertIn(state, close)
            self.assertTrue("undecided" in close or "unresolved" in close)
            self.assertTrue("matches" in close or "aligns" in close)
            self.assertTrue("differs" in close or "diverges" in close)

        opening61 = batch.TOPICS[61]["prompts"][0]
        self.assertNotIn("which one", repr(opening61["accessible_followups"]).casefold())
        self.assertNotIn("which matters most", repr(opening61["full_followups"]).casefold())
        self.assertIn("value", " ".join(opening61["accessible_followups"]).casefold())

        corpus = repr(batch.TOPICS).casefold()
        for old in (
            "what is one small gesture that you find appealing", "what restraint is involved",
            "ending a conversation quickly", "leaving immediately can be", "非現実的な条件表",
            "上達は完璧ではなく", "介護、自由、価値観", "whose choice is different from yours",
            "a life choice they would not make themselves",
            "what can make a breakup difficult to get over",
            "which kind of loss can make recovery difficult",
            "what can make the end of a relationship particularly difficult to recover from",
            "which form of loss can complicate recovery",
        ):
            self.assertNotIn(old.casefold(), corpus)

    def obsolete_sensitive_routes_and_neutral_ft63_are_explicit(self) -> None:
        for topic_no in batch.SENSITIVE_TOPICS:
            for item in batch.TOPICS[topic_no]["prompts"]:
                self.assertRegex(item["safety"], r"^[a-z]+(?:-[a-z]+)+$")
                self.assertNotIn(item["safety"], {"personal-only", "required-disclosure"})
        corpus63 = repr(batch.TOPICS[63]).casefold()
        for advocacy in (
            "people should marry", "people should not marry", "everyone should have children",
            "nobody should have children", "the better life path", "convince them", "selfish choice",
        ):
            self.assertNotIn(advocacy, corpus63)
        for required in ("separate decisions", "both, one, neither", "remain unsure", "nobody owes a complete explanation", "without advocacy"):
            self.assertIn(required, corpus63)

    def obsolete_breakup_topic_never_requires_private_identity_or_dates(self) -> None:
        corpus = repr(batch.TOPICS[62]).casefold()
        for phrase in (
            "name your ex", "your ex's name", "when exactly did you break up", "who broke up with whom",
            "tell us everything", "you have to share", "why did your partner leave you",
        ):
            self.assertNotIn(phrase, corpus)
        self.assertIn("skip specifics", corpus)
        self.assertIn("does not require disclosing identities", corpus)

    def test_actual_checkpoint9_owner_registry_proves_reachability(self) -> None:
        vocabulary = _load_vocabulary()
        registries = {variant: [] for variant in ("accessible", "full")}
        for path in sorted(TRACKS.glob("1-core-patterns/courses/*/lessons/*/lesson.html")):
            source = path.read_text(encoding="utf-8")
            if 'podo:curriculum-status" content="superseded"' in source:
                continue
            review_id = _review_id(source)
            if not review_id.startswith("CORE-") or int(review_id.split("-")[1]) > 53:
                continue
            parsed = vocabulary.parse(source, source=path)
            for row in parsed["categories"]["new"]:
                exact = (str(row["english"]), str(row["japanese"]), review_id, path)
                for variant in registries:
                    registries[variant].append(exact)

        for variant in registries:
            for path in sorted(TRACKS.glob(f"3-freetalking/courses/*-{variant}/lessons/*/lesson.html")):
                source = path.read_text(encoding="utf-8")
                review_id = _review_id(source)
                if not review_id.startswith("FT-") or int(review_id.split("-")[1]) > 56:
                    continue
                parsed = vocabulary.parse(source, source=path)
                for row in parsed["categories"]["new"]:
                    registries[variant].append((str(row["english"]), str(row["japanese"]), review_id, path))

        for variant, rows in registries.items():
            self.assertTrue(rows)
            self.assertTrue(all("2-contextual-english" not in path.parts for *_row, path in rows))
            self.assertTrue(all(not owner.startswith("CORE-") or int(owner.split("-")[1]) <= 53 for _en, _ja, owner, _path in rows))
            lane = {(english.casefold(), japanese) for english, japanese, _owner, _path in rows}
            for topic_no in batch.TOPIC_NUMBERS:
                identity = (EXPECTED_NEW[topic_no][0].casefold(), EXPECTED_NEW[topic_no][1])
                self.assertNotIn(identity, lane)
                lane.add(identity)

        for topic_no, expected_rows in EXPECTED_RECYCLED.items():
            self.assertEqual(_vocab_rows(topic_no, "recycled"), expected_rows)
            for english, japanese, owner in expected_rows:
                for variant in registries:
                    matches = [(en, ja, source_id) for en, ja, source_id, _path in registries[variant] if source_id == owner and en.casefold() == english.casefold()]
                    self.assertEqual(matches, [(english, japanese, owner)])

    def test_declared_vocabulary_is_unique_and_new_is_visibly_productive(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            self.assertEqual(set(batch.VOCABULARY[topic_no]), {"new", "recycled", "assumed", "receptive"})
            self.assertEqual(_vocab_rows(topic_no, "new"), (EXPECTED_NEW[topic_no],))
            categories = {}
            for category in ("new", "recycled", "assumed", "receptive"):
                for row in _vocab_rows(topic_no, category):
                    english = row[0].casefold()
                    self.assertNotIn(english, categories)
                    categories[english] = category
            term = EXPECTED_NEW[topic_no][0]
            pattern = re.compile(rf"(?<![a-z]){re.escape(term)}(?![a-z])", re.IGNORECASE)
            for variant in batch.VARIANTS:
                visible = _article_corpus(topic_no, variant) + " " + _visible_prompt_corpus(topic_no, variant)
                self.assertRegex(visible, pattern)

        fake = {
            "articles": [("Visible text.", "Visible full text.", "見える。", "見える。")],
            "prompts": [{"accessible": "Visible question?", "full": "Visible full question?", "accessible_followups": ("Private target term?",), "full_followups": ("Private target term?",)}],
        }
        for variant, column in (("accessible", 0), ("full", 1)):
            visible = " ".join(row[column] for row in fake["articles"]) + " " + " ".join(item[variant] for item in fake["prompts"])
            self.assertNotIn("target term", visible.casefold())

    def test_future_core_dependencies_are_audited_not_falsely_recycled(self) -> None:
        self.assertEqual(batch.FUTURE_CORE_DEPENDENCIES, {
            58: ("CORE-58",), 59: ("CORE-56", "CORE-66"), 61: ("CORE-66", "CORE-97"),
            62: ("CORE-71",), 63: ("CORE-62", "CORE-93"),
        })
        self.assertEqual(batch.REACHABLE_CORE_RETRIEVAL, {57: ("CORE-43",), 60: ("CORE-17", "CORE-49"), 62: ("CORE-51",)})
        recycled = " ".join(batch.VOCABULARY[number]["recycled"] for number in batch.TOPIC_NUMBERS)
        for owners in batch.FUTURE_CORE_DEPENDENCIES.values():
            for owner in owners:
                self.assertNotIn(owner, recycled)

    def test_glosses_are_variant_specific_bounded_and_surface_exact(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            self.assertEqual(set(batch.GLOSSES[topic_no]), set(batch.VARIANTS))
            for variant, entries in batch.GLOSSES[topic_no].items():
                column = 0 if variant == "accessible" else 1
                self.assertLessEqual(len(entries), 2)
                for row_number, (surface, lemma, japanese) in entries.items():
                    self.assertIn(surface, batch.TOPICS[topic_no]["articles"][row_number - 1][column])
                    self.assertTrue(lemma)
                    self.assertRegex(japanese, r"[ぁ-んァ-ヶ一-龠]")

    def obsolete_goals_do_not_force_relationship_history(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            goal_en, goal_ja = batch.TOPICS[topic_no]["goal"]
            self.assertTrue(goal_en.endswith("."))
            self.assertTrue(goal_ja.endswith("。"))
        self.assertIn("without requiring a personal partner story", batch.TOPICS[59]["goal"][0])
        self.assertIn("real, past, or general", batch.TOPICS[60]["goal"][0])
        self.assertIn("including the option of no wedding", batch.TOPICS[61]["goal"][0])
        self.assertIn("only as much personal detail as feels safe", batch.TOPICS[62]["goal"][0])
        self.assertIn("without arguing for one life path", batch.TOPICS[63]["goal"][0])

    def test_output_paths_are_exact_for_all_14_without_reading_a_shell(self) -> None:
        original = batch._render_dependencies
        calls = []
        english = pathlib.Path("/audit/sandbox/drafts/en")
        batch._render_dependencies = lambda: (calls.append("lazy") or object(), types.SimpleNamespace(ENGLISH=english))
        original_read_text = pathlib.Path.read_text
        pathlib.Path.read_text = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("output_path read a shell"))
        try:
            for topic_no, (slug, _title) in EXPECTED_TOPICS.items():
                for variant in batch.VARIANTS:
                    expected = english / f"tracks/3-freetalking/courses/talk-love-and-marriage-{variant}/lessons/{topic_no:02d}-{slug}/lesson.html"
                    self.assertEqual(batch.output_path(topic_no, variant), expected)
        finally:
            pathlib.Path.read_text = original_read_text
            batch._render_dependencies = original
        self.assertEqual(calls, ["lazy"] * 14)

    def test_checked_in_decks_are_exact_generator_output(self) -> None:
        render = getattr(batch, "build")
        paths = []
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                path = batch.output_path(topic_no, variant)
                paths.append(path)
                self.assertTrue(path.is_file())
                self.assertEqual(path.read_text(encoding="utf-8"), render(topic_no, variant))
        self.assertEqual(len(paths), 14)
        self.assertEqual(len(paths), len(set(paths)))

    def test_rendered_decks_keep_the_approved_conversation_shell(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                source = batch.output_path(topic_no, variant).read_text(encoding="utf-8")
                self.assertEqual(source.count('data-page-id="'), 13)
                self.assertIn('content="2026-08-21"', source)
                self.assertIn("Treat these pages as a pool, not a sequence.", source)
                self.assertIn("React or share briefly before choosing the next prompt", source)
                self.assertIn("Student's sentence", source)
                self.assertNotIn("If yes", source)
                self.assertNotIn("If not", source)

    def test_hash_bound_ledgers_cover_exact_pages_and_semantic_prompts(self) -> None:
        page_review = importlib.import_module(
            f"{__package__}.page_review" if __package__ else "page_review"
        )
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                lesson = batch.output_path(topic_no, variant)
                review_path = REVIEW_ROOT / f"FT-{topic_no}-{variant}.page-review.json"
                markdown_path = review_path.with_suffix(".md")
                review = json.loads(review_path.read_text(encoding="utf-8"))
                self.assertEqual(review["lessonSha256"], page_review.sha256(lesson))
                self.assertEqual([page["pageId"] for page in review["pages"]], page_review.page_ids(lesson))
                self.assertEqual(review["stages"]["generated"], "pass")
                self.assertEqual(review["stages"]["mechanicalValidation"], "pass")
                self.assertEqual(review["stages"]["humanPageAudit"], "pass")
                self.assertEqual(review["stages"]["ownerApproval"], "pending")
                self.assertTrue(all(page["verdict"] == "pass" for page in review["pages"]))
                self.assertTrue(all(page["visual360"] == page["visual480"] for page in review["pages"]))
                self.assertTrue(all(page["visual360"] in {"pending", "pass"} for page in review["pages"]))
                self.assertEqual(markdown_path.read_text(encoding="utf-8"), page_review.markdown(review))
                prompt_pages = review["pages"][4:12]
                expected = [item[variant] for item in batch.TOPICS[topic_no]["prompts"]]
                self.assertEqual(
                    [page["evidence"]["substantivePrompts"][0] for page in prompt_pages],
                    expected,
                )

    def test_module_io_and_renderer_imports_remain_lazy(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        tree = ast.parse(source)
        parents = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent

        def enclosing_function(node):
            while node in parents:
                node = parents[node]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return node.name
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"read_text", "read_bytes", "write_text", "mkdir", "exists", "open"}:
                self.assertIn(enclosing_function(node), {"build", "main"})
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported = {alias.name for alias in node.names}
                if imported & {"new_lesson", "generate_ft_me_lately_batch"}:
                    self.assertEqual(enclosing_function(node), "_render_dependencies")
        self.assertNotIn("CANONICAL =", source)

    def test_renderer_contract_is_complete_and_source_tests_never_build(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('content="complete"', source)
        self.assertNotIn('content="pending"', source)
        test_tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
        build_calls = [
            node for node in ast.walk(test_tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "batch" and node.func.attr == "build"
        ]
        self.assertEqual(build_calls, [])

    def test_authored_source_digests_are_locked(self) -> None:
        claims = []
        prompts = []
        for topic_no in batch.TOPIC_NUMBERS:
            for row in batch.TOPICS[topic_no]["articles"]:
                claims.extend(row)
            for item in batch.TOPICS[topic_no]["prompts"]:
                prompts.extend([
                    item["job"], item["title"], item["title_ja"], item["accessible"], item["accessible_ja"],
                    *item["accessible_followups"], item["full"], item["full_ja"], *item["full_followups"], item["safety"],
                ])
        self.assertEqual(hashlib.sha256("\n".join(claims).encode()).hexdigest(), "fa631f32c716fabf5f5458ad5c1da7d1dcb8d0fa5edf29594bfabdf3ef39273f")
        self.assertEqual(hashlib.sha256("\n".join(prompts).encode()).hexdigest(), "52bb2acf443b554e0a7918acb574fb0ba95f70584ece268a6aa8b9f3f2812153")
        self.assertEqual(hashlib.sha256(repr(batch.VOCABULARY).encode()).hexdigest(), "5411c539ff9f25b791eb14443245b9dd317d84bcadf009b906d514d6a18c45e6")


if __name__ == "__main__":
    unittest.main()
