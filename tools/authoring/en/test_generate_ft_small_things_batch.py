from __future__ import annotations

import hashlib
import html
import re
import unittest

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

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
                # The article is the load-bearing differentiation: every claim is
                # independently authored at the two levels. Short, natural talk
                # questions may stay identical when a forced rewrite would only
                # add thesaurus load rather than intellectual value.
                self.assertNotEqual(
                    batch.GLOSSES[topic_no]["accessible"],
                    batch.GLOSSES[topic_no]["full"],
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

    def test_prompt_pools_are_distinct_answerable_and_non_defensive(self) -> None:
        defensive = re.compile(
            r"^(?:if\s+(?:yes|not|no|none|nothing|someone|nobody|one|something|they|you|it)\b|"
            r"if\s+there\s+(?:is|isn't|are|aren't)\b)",
            flags=re.IGNORECASE,
        )
        cross_page_referent = re.compile(
            r"\bthat (?:rule|moment|memory|habit|example|story|person|place|situation)\b",
            flags=re.IGNORECASE,
        )
        for topic_no, topic in batch.TOPICS.items():
            for variant in ("accessible", "full"):
                prompts = [item[variant] for item in topic["prompts"]]
                followup_sets = [tuple(item[f"{variant}_followups"]) for item in topic["prompts"]]
                all_followups = [value for values in followup_sets for value in values]
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(len(prompts), len(set(prompts)))
                    self.assertEqual(len(followup_sets), len(set(followup_sets)))
                    self.assertEqual(len(all_followups), len(set(all_followups)))
                    self.assertTrue(all(value.endswith(("?", ".")) for value in prompts))
                    self.assertFalse(any(defensive.search(value) for value in all_followups))
                    self.assertFalse(any(cross_page_referent.search(value) for value in prompts))
                    self.assertFalse(any("real or imagined" in value.casefold() for value in prompts))
                    self.assertFalse(any("say whether" in value.casefold() for value in prompts))

        exact_openings = {
            34: "What's one tiny thing that can become surprisingly annoying?",
            35: "What's one fact about you that's interesting but not useful?",
            36: "What's something people often do at home but hide in public?",
            37: "It's raining and you have no plans. What happens?",
            38: "When you feel completely drained, what tends to help most?",
            39: "What do you really do when you're stressed—not what you should do?",
            40: "Which superstition do you know best, whether or not you follow it?",
            41: "Imagine a Saturday with no plans. How would it begin?",
            42: "What's a household rule that makes sense in one family but seems strange elsewhere?",
            43: "Why can a harmless embarrassing moment replay for years?",
            44: "What kind of moment makes you laugh out loud?",
            45: "What time did you go to bed last night?",
            46: "What personal rule can make life easier?",
        }
        self.assertEqual(
            {topic_no: topic["prompts"][0]["accessible"] for topic_no, topic in batch.TOPICS.items()},
            exact_openings,
        )
        self.assertEqual(
            batch.TOPICS[43]["prompts"][1]["accessible"],
            "What's one harmless awkward moment that people often replay?",
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
            (34, 3): (
                "How can someone raise a minor irritation without making it sound disproportionate?",
                "ささいな不満を大げさに聞こえないように伝えるには、どのような言い方がよいですか？",
            ),
            (37, 5): (
                "Which situation involving rain would be most difficult to manage?",
                "雨の日のどのような状況が、いちばん大変そうですか？",
            ),
            (38, 7): (
                "What advice would you offer someone who felt completely exhausted?",
                "完全に疲れ切っている人に、何と伝えますか？",
            ),
            (39, 5): (
                "In which situation is your usual coping response most counterproductive?",
                "いつものストレスへの対処が、いちばん役に立たないのはどんなときですか？",
            ),
            (44, 6): (
                "What allows a funny story to survive the act of retelling?",
                "面白い話が、語り直しても面白さを保つのはなぜですか？",
            ),
        }
        for (topic_no, prompt_index), contract in expected.items():
            with self.subTest(topic=topic_no, prompt=prompt_index):
                item = batch.TOPICS[topic_no]["prompts"][prompt_index]
                self.assertEqual((item["full"], item["ja"]), contract)

    def test_reviewed_prompt_japanese_is_exact_and_natural(self) -> None:
        expected = {
            (34, 3): "ささいな不満を大げさに聞こえないように伝えるには、どのような言い方がよいですか？",
            (35, 7): "自分についての少し変わった事実を、楽しい自己紹介でどう使いますか？",
            (36, 7): "害のない私的な習慣を人に見せないほうがよいのは、どのようなときですか？",
            (39, 3): "人は、ストレスがあるときにすることを、普段どのくらい正直に話すでしょうか？",
            (40, 1): "その迷信に従ったり破ったりすると、何が起きるとされていますか？",
            (42, 1): "家庭の変わった決まりは、日常の中でどのように使われますか？",
            (43, 1): "人が何度も思い出しやすい、害のない気まずい場面を一つ挙げてください。",
            (43, 2): "年齢によって、恥ずかしい記憶の感じ方はどう変わりそうですか？",
            (43, 3): "誰も気づかなくても、なぜ恥ずかしい出来事を強く感じるのでしょうか？",
            (43, 4): "恥ずかしい出来事について、ほかの人は何を覚えていそうですか？",
            (44, 5): "どのような笑いが、自分にはいちばん楽しみにくいですか？",
            (45, 7): "無理なく続けられ、しっかり休むことにもつながる、眠る前の過ごし方はどのようなものですか？",
            (46, 1): "役立つ自分のルールは、どのくらい厳しくするとよいですか？",
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
