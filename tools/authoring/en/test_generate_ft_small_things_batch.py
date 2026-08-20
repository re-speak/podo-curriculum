from __future__ import annotations

import hashlib
import html
import re
import unittest

import check_deck
import generate_ft_small_things_batch as batch
import vocabulary


def rendered_article_japanese(topic_no: int, variant: str) -> tuple[str, ...]:
    source = batch.build(topic_no, variant)
    return tuple(
        html.unescape(value)
        for value in re.findall(
            r'<span class="s-open"><span class="s-ja">([^<]+)</span>',
            source,
        )
    )


def productive_english(source: str) -> str:
    """Return article claims and learner-facing discussion prompts, not glosses."""
    zones = re.findall(
        r'<span class="s-line"><span class="s-ko">(.*?)</span><span class="s-mark"',
        source,
        flags=re.DOTALL,
    )
    zones.extend(
        re.findall(
            r'<p class="section-subtitle ask">.*?<span class="ko">(.*?)</span><span class="ja">',
            source,
            flags=re.DOTALL,
        )
    )
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", zone))
        for zone in zones
    )


class FreetalkingSmallThingsBatchTests(unittest.TestCase):
    def test_source_inventory_is_explicit_paired_and_differentiated(self) -> None:
        self.assertEqual(list(batch.TOPICS), list(range(34, 47)))
        self.assertEqual(set(batch.TOPICS), set(batch.CLAIM_ORDER))
        self.assertEqual(set(batch.TOPICS), set(batch.VOCABULARY))
        self.assertEqual(set(batch.TOPICS), set(batch.GLOSSES))
        for topic_no, topic in batch.TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(len(topic["articles"]), 10)
                self.assertEqual(len(topic["prompts"]), 8)
                self.assertEqual(len(batch.CLAIM_ORDER[topic_no]), 10)
                self.assertEqual(len(set(batch.CLAIM_ORDER[topic_no])), 10)
                self.assertTrue(all(len(article) == 4 for article in topic["articles"]))
                self.assertTrue(all(a_en != f_en for a_en, f_en, _a_ja, _f_ja in topic["articles"]))
                self.assertTrue(all(a_ja != f_ja for _a_en, _f_en, a_ja, f_ja in topic["articles"]))
                self.assertGreaterEqual(
                    sum(item["accessible"] != item["full"] for item in topic["prompts"]),
                    3,
                )
                self.assertEqual(set(batch.GLOSSES[topic_no]), {"accessible", "full"})
                self.assertEqual(
                    set(batch.VOCABULARY[topic_no]),
                    {"new", "recycled", "assumed", "receptive"},
                )
                for item in topic["prompts"]:
                    for variant in ("accessible", "full"):
                        followups = item[f"{variant}_followups"]
                        self.assertIn(len(followups), (2, 3))
                        self.assertEqual(len(followups), len(set(followups)))
                        self.assertTrue(all(value.endswith("?") for value in followups))

    def test_checked_in_decks_are_exact_complete_generator_output(self) -> None:
        for topic_no in batch.TOPICS:
            for variant in ("accessible", "full"):
                path = batch.output_path(topic_no, variant)
                expected = batch.build(topic_no, variant)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertTrue(path.is_file())
                    self.assertEqual(path.read_text(encoding="utf-8"), expected)
                    self.assertEqual(
                        expected.count('<meta name="podo:proofread-status" content="complete">'),
                        1,
                    )
                    self.assertNotIn('podo:proofread-status" content="pending', expected)

    def test_all_260_rendered_japanese_claims_match_reviewed_contract(self) -> None:
        rendered = []
        for variant in ("accessible", "full"):
            for topic_no in range(34, 47):
                rendered.extend(rendered_article_japanese(topic_no, variant))
        self.assertEqual(len(rendered), 260)
        self.assertEqual(
            hashlib.sha256("\n".join(rendered).encode("utf-8")).hexdigest(),
            "f87d2890495b8d8f2353cc17d55ff845f904faf886cbc25b3ca98eee4070481a",
        )

    def test_critical_claims_lock_exact_variant_meaning(self) -> None:
        expected = {
            (34, 6): (
                "Saying something can solve the problem, but it can also sound too serious.",
                "Mentioning it may solve the problem, yet the complaint can sound out of proportion to its cause.",
                "伝えれば解決するかもしれませんが、大げさに聞こえることもあります。",
                "口にすれば解決する一方で、原因の小ささに比べて不満が大げさに聞こえることもあります。",
            ),
            (35, 6): (
                "The best useless facts are harmless and easy to explain.",
                "A good useless fact is harmless, concise, and revealing without becoming too private.",
                "よい役に立たない事実は、害がなく、簡単に説明できます。",
                "よい役に立たない事実は、害がなく簡潔で、私的になりすぎずに人柄を表します。",
            ),
            (36, 10): (
                "The question is not whether the habit is strange, but whether it causes harm.",
                "The useful boundary is not normal versus strange, but harmless privacy versus behaviour that affects others.",
                "大切なのは変かどうかではなく、害があるかどうかです。",
                "大切な境界は、普通か変かではなく、害のない私的な習慣か、他人に影響する行動かという点です。",
            ),
            (37, 4): (
                "The same weather feels very different when we have to travel.",
                "The same rain becomes far less romantic when we have to commute, carry things, or arrive on time.",
                "移動しなければならないと、同じ天気でもまったく違って感じます。",
                "通勤したり、荷物を運んだり、時間どおりに着く必要があると、同じ雨でもずっと現実的な負担になります。",
            ),
            (38, 9): (
                "Good advice begins by asking what the tired person can manage.",
                "Useful support begins by asking what the exhausted person has the capacity to do.",
                "よい助言は、疲れている人に何ができそうかを聞くことから始まります。",
                "役立つ支えは、疲れ切った人に今できる余力がどのくらいあるかを尋ねることから始まります。",
            ),
            (39, 6): (
                "People sometimes describe the healthy habit they wish they had.",
                "We sometimes report the healthy response we admire rather than the behaviour we actually repeat.",
                "人は、実際の習慣ではなく、できたらよいと思う健康的な方法を話すことがあります。",
                "実際に繰り返す行動ではなく、自分が理想とする健康的な反応を話してしまうことがあります。",
            ),
            (40, 2): (
                "People can follow one without fully believing it.",
                "People may follow a superstition even while saying they do not believe what it predicts.",
                "人は、完全に信じていなくても迷信に従うことがあります。",
                "迷信が予告することは信じないと言いながらも、それに従う人はいます。",
            ),
            (41, 4): (
                "Doing nothing is different from choosing to rest.",
                "Unplanned inactivity does not always provide the same recovery as deliberate rest.",
                "何もしないことと、休むことを選ぶのは違います。",
                "予定なく動かないことは、意識して休むことと同じ回復をもたらすとは限りません。",
            ),
            (42, 9): (
                "Passing a rule on is a choice, not an automatic duty.",
                "Carrying a rule into the next household is a deliberate choice rather than an inherited obligation.",
                "決まりを次に伝えることは、当然の義務ではなく選択です。",
                "決まりを次の家庭へ持ち込むことは、受け継いだ義務ではなく、意識的な選択です。",
            ),
            (43, 7): (
                "But nobody should have to share a memory that still feels unsafe.",
                "A conversation does not require disclosing a memory that remains painful, private, or unsafe.",
                "今もつらい記憶を、無理に話す必要はありません。",
                "会話のために、今も苦しい、私的な、または安心して話せない記憶を明かす必要はありません。",
            ),
            (44, 9): (
                "Explaining a funny moment requires enough context, but not every detail.",
                "Retelling a funny moment requires selective context: enough to set the pattern, but not enough to bury the turn.",
                "面白い場面を話すには、十分な背景が必要ですが、細部を全部話す必要はありません。",
                "面白い場面を語り直すには、流れが分かるだけの背景は必要ですが、肝心の転換を埋もれさせるほど多くは要りません。",
            ),
            (45, 5): (
                "That freedom makes going to bed feel like giving something up.",
                "When private time is scarce, sleep can feel like surrendering the only part of the day we control.",
                "その自由があると、寝ることが何かを手放すように感じられます。",
                "自分だけの時間が少ないと、睡眠は自分で決められる一日の唯一の部分を手放すように感じられます。",
            ),
            (46, 5): (
                "An exception does not always destroy the value of a rule.",
                "A carefully chosen exception may clarify the rule's purpose rather than weaken it.",
                "例外があっても、そのルールの価値がなくなるとは限りません。",
                "慎重に選んだ例外は、ルールを弱めるのではなく、その目的を明確にする場合があります。",
            ),
            (35, 4): (
                "Some personal facts are about skills that were useful once but no longer matter.",
                "Some personal trivia describes practical skills whose original usefulness has faded.",
                "昔は役に立ったものの、今は必要なくなった技能についての事実もあります。",
                "個人的な雑学の中には、もともとの実用性が薄れた技能についてのものもあります。",
            ),
            (41, 10): (
                "What feels missing from a free day can show what we need.",
                "What feels missing from a free day may reveal what our ordinary routines fail to provide.",
                "自由な日に足りないと感じるものは、自分に必要なものを示します。",
                "自由な日に足りないと感じるものから、普段の生活では満たせていないことが見える場合があります。",
            ),
            (43, 8): (
                "A small awkward moment can be enough for a good story.",
                "A harmless social faux pas often makes a better story than a deeply painful event.",
                "ささいな気まずい場面だけでも、十分によい話になります。",
                "害のないちょっとした失礼のほうが、深くつらい出来事よりも話にしやすいものです。",
            ),
            (44, 1): (
                "Real laughter often arrives before we can explain the joke.",
                "We often laugh for real before we consciously understand what made something funny.",
                "本当の笑いは、なぜ面白いか説明する前に出ることがあります。",
                "何が面白かったのかを意識して理解する前に、本当に笑ってしまうことがよくあります。",
            ),
            (44, 7): (
                "Different people laugh at stories, language, mistakes, or absurd situations.",
                "Our humour may respond to storytelling, wordplay, a social faux pas, absurdity, or recognition.",
                "人によって、物語、言葉、失敗、変な状況など、笑うものが違います。",
                "人の笑いは、物語、言葉遊び、ちょっとした失礼、ばかばかしさ、共感など、さまざまなものに反応します。",
            ),
            (45, 1): (
                "The time we plan to sleep and the time we actually fall asleep are often different.",
                "The time we intend to sleep often differs from the moment sleep actually begins.",
                "寝ようと思う時間と、実際に眠りにつく時間は、よくずれます。",
                "眠ろうと考えている時間と、実際に眠り始める瞬間は、しばしば一致しません。",
            ),
            (46, 3): (
                "Many strong rules begin after one experience we do not want to repeat.",
                "Many strict rules are written in response to one experience whose cost we refuse to repeat.",
                "厳しいルールの多くは、二度と経験したくない出来事のあとに生まれます。",
                "厳しいルールの多くは、二度と同じ代償を払わないために、ある経験をきっかけに作られます。",
            ),
            (46, 10): (
                "The best rule still serves a clear purpose today.",
                "A durable personal rule remains connected to a purpose we can still name and defend today.",
                "よいルールには、今でも明確な役割があります。",
                "長く続ける価値のある自分のルールは、今も言葉にして説明できる目的と結びついています。",
            ),
            (37, 8): (
                "A downpour often stays in our memory because of one clear sound, smell, or place.",
                "A downpour often remains memorable because of one vivid sound, smell, route, or place where we sheltered.",
                "土砂降りは、はっきりした音や匂い、場所とともに記憶に残ることがよくあります。",
                "土砂降りは、鮮明な音や匂い、通った道、雨宿りした場所とともに記憶に残ることがよくあります。",
            ),
            (37, 9): (
                "A rainy day feels ideal when we are comfortable and nothing urgent needs attention.",
                "The ideal rainy day depends on comfort, safety, and the absence of an urgent obligation.",
                "心地よく過ごせて、急いで対応することがなければ、雨の日も理想的に感じられます。",
                "理想の雨の日には、心地よさと安全、そして急いで果たす義務がないことが欠かせません。",
            ),
            (43, 3): (
                "We remember our own mistake more clearly than other people's reactions.",
                "We often remember our own mistake in detail while exaggerating how much other people noticed.",
                "人の反応より、自分の失敗のほうをはっきり覚えています。",
                "自分の失敗は細かく覚えている一方で、周りの人が実際以上に注目していたように思いがちです。",
            ),
            (43, 9): (
                "We are usually kinder to another person's old mistake than to our own.",
                "We routinely offer other people more perspective and compassion than we grant ourselves.",
                "人の昔の失敗には、自分の失敗よりやさしくなれます。",
                "私たちは、自分に対してよりも、ほかの人には広い視野と思いやりを持って接することがよくあります。",
            ),
        }
        for (topic_no, row), contract in expected.items():
            with self.subTest(topic=topic_no, row=row):
                self.assertEqual(batch.TOPICS[topic_no]["articles"][row - 1], contract)
                self.assertEqual(rendered_article_japanese(topic_no, "accessible")[row - 1], contract[2])
                self.assertEqual(rendered_article_japanese(topic_no, "full")[row - 1], contract[3])

    def test_page_article_prompt_feedback_and_script_contract(self) -> None:
        expected_pages = [
            "lesson-goal", "article", "lesson-style", "talk-intro",
            "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6",
            "feedback",
        ]
        for topic_no in batch.TOPICS:
            rendered = {variant: batch.build(topic_no, variant) for variant in ("accessible", "full")}
            for variant, source in rendered.items():
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(re.findall(r'data-page-id="([^"]+)"', source), expected_pages)
                    self.assertEqual(len(re.findall(r'class="sent" role="button"', source)), 10)
                    self.assertEqual(len(re.findall(r'class="section-subtitle ask"', source)), 8)
                    self.assertEqual(len(re.findall(r'class="fb" data-fb=', source)), 8)
                    self.assertEqual(source.count("shared/js/feedback.js"), 1)
                    self.assertNotIn("<style", source)
                    self.assertNotIn("<script>\n", source)
                    self.assertNotIn("yomi.js", source)
                    self.assertNotIn("data-choice-scope", source)
            self.assertEqual(
                re.findall(r'data-claim-id="([^"]+)"', rendered["accessible"]),
                list(batch.CLAIM_ORDER[topic_no]),
            )
            self.assertEqual(
                re.findall(r'data-claim-id="([^"]+)"', rendered["full"]),
                list(batch.CLAIM_ORDER[topic_no]),
            )

    def test_openings_and_titles_match_authoritative_briefs(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            brief = (batch.TRACK / "toc" / f"FT-{topic_no}.md").read_text(encoding="utf-8")
            opening = topic["prompts"][0]["accessible"]
            with self.subTest(topic=topic_no):
                self.assertIn(f"# FT-{topic_no} · {topic['title']}", brief)
                self.assertIn(f'- **Opening:** "{opening}"', brief)
                self.assertEqual(topic["prompts"][0]["full"], opening)

    def test_glosses_are_short_exact_and_declared(self) -> None:
        for topic_no in batch.TOPICS:
            for variant in ("accessible", "full"):
                source = batch.build(topic_no, variant)
                categories = vocabulary.parse(source)["categories"]
                declared = {
                    entry["english"].casefold()
                    for entries in categories.values()
                    for entry in entries
                }
                for row, (surface, headword, _ja) in batch.GLOSSES[topic_no][variant].items():
                    with self.subTest(topic=topic_no, variant=variant, row=row):
                        article = batch.TOPICS[topic_no]["articles"][row - 1][0 if variant == "accessible" else 1]
                        self.assertIn(surface, article)
                        self.assertIn(headword.casefold(), declared)
                        self.assertLessEqual(len(headword.split()), 3)

    def test_new_owner_map_is_unique_before_ft34(self) -> None:
        expected = {
            34: ("irritation",), 35: ("trivia",), 36: ("private habit",),
            37: ("downpour",), 38: ("drained",),
            39: ("coping response",), 40: ("superstition", "skeptic"),
            41: ("unstructured",), 42: ("household rule",),
            43: ("resurface",), 44: ("contagious",),
            45: ("wind down",), 46: ("rigidity",),
        }
        actual = {
            topic_no: tuple(
                part.split("|", 1)[0]
                for part in contract["new"].split("; ")
                if part
            )
            for topic_no, contract in batch.VOCABULARY.items()
        }
        self.assertEqual(actual, expected)
        self.assertTrue(all(not contract["recycled"] for contract in batch.VOCABULARY.values()))

        earlier_new = {}
        for path in batch.TRACK.parent.glob("*/courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            review = check_deck.meta_content(source, "podo:review-id") or ""
            if review.startswith("FT-") and int(review.split("-")[1]) >= 34:
                continue
            for entry in vocabulary.parse(source)["categories"]["new"]:
                earlier_new.setdefault(entry["english"].casefold(), []).append(
                    (review, entry["japanese"])
                )
        for topic_no, words in expected.items():
            for word in words:
                with self.subTest(topic=topic_no, word=word):
                    self.assertNotIn(word.casefold(), earlier_new)

    def test_answer_safe_branch_contracts_lock_risky_chains(self) -> None:
        exact = {
            (34, 0): ("If one comes to mind, where does it happen?", "If none does, which familiar or imagined complaint could you use—for example, loud typing?"),
            (35, 0): ("If one comes to mind, how would you prove it?", "If none does, what harmless fact could someone use as an example?"),
            (36, 0): ("If something comes to mind, what makes home feel safe for it?", "If nothing does, what harmless habit could someone keep private?"),
            (38, 3): ("If someone helps, what do they actually do?", "If nobody does, what kind of help would be welcome?"),
            (40, 0): ("If there is, what do you avoid?", "If there is not, which superstition do you hear most often?"),
            (42, 0): ("If one comes to mind, what was the rule?", "If none does, what rule from another household surprised you?"),
            (43, 0): ("If a safe example comes to mind, how would you name it briefly?", "If none does, what harmless mistake do people often replay?"),
            (44, 0): ("If a moment comes to mind, where were you?", "If none does, what usually comes closest to making you laugh?"),
            (46, 0): ("If there is, how would you state the rule simply?", "If there is not, what decision would benefit from a clear rule?"),
        }
        for (topic_no, prompt_index), followups in exact.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                item = batch.TOPICS[topic_no]["prompts"][prompt_index]
                self.assertEqual(tuple(item["accessible_followups"]), followups)
                self.assertEqual(tuple(item["full_followups"]), followups)

        self.assertIn("real or imagined habit", batch.TOPICS[36]["prompts"][1]["accessible"])
        self.assertIn("real or borrowed rule", batch.TOPICS[42]["prompts"][1]["accessible"])
        self.assertIn("safe real or general example", batch.TOPICS[43]["prompts"][1]["accessible"])
        self.assertIn("real or possible rule", batch.TOPICS[46]["prompts"][1]["accessible"])

        downstream = {
            (34, 1): "Say when you last noticed or heard about the real issue—or when the imagined one could happen.",
            (34, 2): "Which exact part seems most irritating, and to whom?",
            (34, 3): "Say whether anyone affected by the real issue spoke up—or what a person in the imagined case might say.",
            (34, 4): "For the real issue, does anyone else agree—or in the imagined case, might other people agree?",
            (35, 1): "Say how long the real fact has been true—or how long the imagined one would have been true.",
            (35, 2): "Who knows—or might know—that fact, if anyone?",
            (35, 4): "How was that fact discovered or learned—or how could it be?",
            (35, 6): "Go back to the useless fact from the start: would that real or imagined example surprise people?",
            (35, 7): "Would you use that same useless fact in a playful introduction?",
            (39, 3): "What do you tell people you do when you're stressed? Say whether you have one usual answer, it varies, or the topic has never come up.",
            (41, 7): "How does the free Saturday you described compare with your ideal one?",
            (42, 7): "What small rule should a household be known for?",
            (43, 3): "Who saw it—or who might see a situation like that?",
            (43, 4): "What might another person remember from the real event or notice in the general example?",
            (43, 5): "What brings that real memory back—or could bring a similar memory back?",
            (43, 6): "What would you tell the person in that memory—or someone in that situation?",
            (43, 7): "Could that real memory—or a harmless example—be funny later?",
            (45, 1): "What were you doing just before bed—or while you stayed awake?",
            (45, 2): "Do you have a regular bedtime pattern right now?",
            (45, 3): "How does the time you sleep—or miss sleep—affect the following day?",
            (45, 4): "Have you tried to change your sleep schedule?",
            (45, 5): "What most often delays or shifts your sleep?",
            (46, 6): "How would you check whether the rule serves—or could serve—you?",
        }
        for (topic_no, prompt_index), text in downstream.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                self.assertEqual(batch.TOPICS[topic_no]["prompts"][prompt_index]["accessible"], text)

        negative_contract = "\n".join(
            value
            for topic_no in (34, 35, 36, 39, 42, 43, 45, 46)
            for item in batch.TOPICS[topic_no]["prompts"]
            for value in (
                item["accessible"],
                item["full"],
                *item["accessible_followups"],
                *item["full_followups"],
            )
        )
        for forbidden in (
            "Why do fewer people remember",
            "What assumption would it challenge",
            "How has the habit changed since then",
            "Why is one version easier to share",
            "what made you stop?",
            "your future household",
            "why has your own memory lasted",
            "What do you do when it returns",
            "What has helped you keep it",
            "evidence would support keeping it",
            "later than planned",
            "Has anyone affected by it ever said anything?",
            "Has anyone affected by it ever raised the issue?",
            "Does anyone else agree that it's irritating, as far as you know?",
            "Would that real or imagined fact surprise people?",
            "Would you use that real or imagined fact in a playful introduction?",
            "do you give no standard answer",
            "if you tell them anything at all",
            "why do you leave the real response private or unexplained",
            "What do you usually tell people you do when you're stressed—or does your answer change each time?",
            "What do you usually tell other people about your stress response—or is there no stable version?",
        ):
            self.assertNotIn(forbidden, negative_contract)

        variant_contracts = {
            (34, 3): (
                "Say whether anyone affected by the real issue spoke up—or what a person in the imagined case might say.",
                "Explain whether anyone affected by the real issue raised it—or what someone in the imagined case might say.",
            ),
            (34, 4): (
                "For the real issue, does anyone else agree—or in the imagined case, might other people agree?",
                "For the real issue, does anyone else agree—or in the imagined case, would others be likely to agree?",
            ),
            (35, 6): (
                "Go back to the useless fact from the start: would that real or imagined example surprise people?",
                "Returning to the original useless fact, would that real or imagined example genuinely surprise people?",
            ),
            (35, 7): (
                "Would you use that same useless fact in a playful introduction?",
                "Would you use that same useless fact in a playful introduction?",
            ),
            (39, 3): (
                "What do you tell people you do when you're stressed? Say whether you have one usual answer, it varies, or the topic has never come up.",
                "How do you describe your stress response to other people? Say whether your account is consistent, varies, or the subject has never come up.",
            ),
        }
        for (topic_no, prompt_index), contract in variant_contracts.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                item = batch.TOPICS[topic_no]["prompts"][prompt_index]
                self.assertEqual((item["accessible"], item["full"]), contract)

        self.assertIn("have you never followed it", batch.TOPICS[42]["prompts"][4]["accessible_followups"][1])
        self.assertIn("still only an idea", batch.TOPICS[46]["prompts"][3]["accessible_followups"][1])
        self.assertIn("If you did not", batch.TOPICS[45]["prompts"][0]["accessible_followups"][1])
        self.assertIn("gets to someone", batch.TOPICS[34]["goal"][0])
        self.assertIn("share or imagine", batch.TOPICS[35]["goal"][0])
        self.assertIn("people who followed it", batch.TOPICS[42]["goal"][0])
        self.assertIn("can refuse to disappear", batch.TOPICS[43]["goal"][0])
        self.assertIn("meant or needed to sleep", batch.TOPICS[45]["goal"][0])
        self.assertIn("or one that might help", batch.TOPICS[46]["goal"][0])

        followup_contracts = {
            (34, 3): (
                "If someone spoke about the real issue, what did they say?",
                "If the case is imagined—or nobody spoke—what might keep someone silent?",
            ),
            (34, 4): (
                "If someone agrees or might agree, what would they notice?",
                "If nobody agrees or seems likely to, why could people's reactions differ?",
            ),
            (35, 6): (
                "If it would, what makes it surprising?",
                "If it would not, why might it sound ordinary to other people?",
            ),
            (35, 7): (
                "If you would, what follow-up would you hope to hear?",
                "If you would not, what kind of fact would you use instead?",
            ),
            (39, 3): (
                "If you have a usual answer, how does it compare with what you really do?",
                "If it varies, what changes what you say?",
                "If the topic has never come up, what would you say if it did?",
            ),
            (41, 7): (
                "If they differ, what would you add or remove?",
                "If they match, what makes the day work so well?",
            ),
        }
        for (topic_no, prompt_index), contract in followup_contracts.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                self.assertEqual(
                    tuple(batch.TOPICS[topic_no]["prompts"][prompt_index]["accessible_followups"]),
                    contract,
                )

    def test_every_new_term_is_learner_visible_in_both_variants(self) -> None:
        for topic_no, contract in batch.VOCABULARY.items():
            new_terms = [part.split("|", 1)[0] for part in contract["new"].split("; ") if part]
            for variant in ("accessible", "full"):
                visible_text = productive_english(batch.build(topic_no, variant))
                for term in new_terms:
                    with self.subTest(topic=topic_no, variant=variant, term=term):
                        pattern = rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])"
                        self.assertRegex(visible_text.casefold(), pattern.casefold())

    def test_new_term_visibility_does_not_count_the_glossary_headword(self) -> None:
        source = batch.build(37, "full")
        mutated = source.replace(
            '<span class="s-key">downpour</span>',
            '<span class="s-key">heavy rain</span>',
            1,
        )
        self.assertIn("<b>downpour</b>", mutated)
        self.assertNotRegex(
            productive_english(mutated).casefold(),
            r"(?<![a-z0-9])downpour(?![a-z0-9])",
        )

    def test_full_prompt_rewrites_preserve_the_shared_japanese_operation(self) -> None:
        expected = {
            (35, 5): (
                "Which fact about you has genuine practical value?",
                "自分について、本当に役に立つ事実は何ですか？",
            ),
            (37, 2): (
                "Do rainy days generally appeal to you?",
                "普段、雨の日は好きですか？",
            ),
            (38, 7): (
                "What advice would you offer someone who felt completely exhausted?",
                "完全に疲れ切っている人に、何と伝えますか？",
            ),
            (41, 5): (
                "What was a free weekend like for you five years ago?",
                "5年前の予定のない週末は、どのようなものでしたか？",
            ),
            (45, 7): (
                "What would a realistic and genuinely restful wind-down routine look like for you?",
                "無理なく続けられ、しっかり休むことにもつながる、眠る前の過ごし方はどのようなものですか？",
            ),
        }
        for (topic_no, prompt_index), contract in expected.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                item = batch.TOPICS[topic_no]["prompts"][prompt_index]
                self.assertEqual((item["full"], item["ja"]), contract)

    def test_reviewed_prompt_japanese_is_exact_and_natural(self) -> None:
        expected = {
            (34, 1): "実際の問題なら最後に気づいたり話を聞いたりしたのはいつか、想像した問題ならいつ起こりそうかを話してください。",
            (34, 3): "実際の問題なら困っている人は何か伝えたのか、想像した例ならその人は何と言いそうかを話してください。",
            (34, 4): "実際の問題ならほかにも同意する人はいますか、想像した例なら同意する人はいそうですか？",
            (35, 1): "実際の事実ならいつからそうなのか、想像した例ならいつからという設定なのかを話してください。",
            (35, 6): "最初に挙げた役に立たない事実に戻ると、その実際の例、または想像した例を聞いて人は驚きそうですか？",
            (35, 7): "その同じ役に立たない事実を、楽しい自己紹介で使いたいですか？",
            (39, 3): "ストレスがあるときに何をするか、人にはどう話しますか。いつも同じ答えか、その時々で変わるか、それとも一度も話題になったことがないかも話してください。",
            (40, 1): "自分が従っている迷信、またはよく知っている迷信には、どのような決まりがありますか？",
            (42, 1): "自分の家庭、またはほかの家庭で知ったその決まりは、どのような内容でしたか？",
            (45, 7): "無理なく続けられ、しっかり休むことにもつながる、眠る前の過ごし方はどのようなものですか？",
        }
        for (topic_no, prompt_index), japanese in expected.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                self.assertEqual(batch.TOPICS[topic_no]["prompts"][prompt_index]["ja"], japanese)

    def test_every_deck_passes_static_checker_with_complete_status(self) -> None:
        for topic_no in batch.TOPICS:
            for variant in ("accessible", "full"):
                path = batch.output_path(topic_no, variant)
                errors, warnings = check_deck.check(path)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(errors, [])
                    self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
