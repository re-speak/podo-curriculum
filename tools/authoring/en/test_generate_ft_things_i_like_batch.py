from __future__ import annotations

import html
import hashlib
import re
import unittest

import check_deck
import generate_ft_things_i_like_batch as batch
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


class FreetalkingThingsILikeBatchTests(unittest.TestCase):
    def test_source_inventory_is_explicit_and_paired(self) -> None:
        self.assertEqual(list(batch.TOPICS), list(range(21, 34)))
        self.assertEqual(set(batch.TOPICS), set(batch.CLAIM_ORDER))
        self.assertEqual(set(batch.TOPICS), set(batch.VOCABULARY))
        self.assertEqual(set(batch.TOPICS), set(batch.GLOSSES))
        self.assertEqual(set(batch.TOPICS), set(batch.ARTICLE_JA))
        for topic_no, topic in batch.TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(len(topic["articles"]), 10)
                self.assertEqual(len(topic["prompts"]), 8)
                self.assertEqual(len(batch.CLAIM_ORDER[topic_no]), 10)
                self.assertEqual(len(set(batch.CLAIM_ORDER[topic_no])), 10)
                self.assertTrue(all(accessible != full for accessible, full, _ja in topic["articles"]))
                self.assertEqual(set(batch.ARTICLE_JA[topic_no]), {"accessible", "full"})
                self.assertTrue(
                    all(
                        len(batch.ARTICLE_JA[topic_no][variant]) == 10
                        and all(batch.ARTICLE_JA[topic_no][variant])
                        for variant in ("accessible", "full")
                    )
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

    def test_reviewed_variant_japanese_override_inventory_is_exact(self) -> None:
        expected = {
            "accessible": (
                (21, 3), (21, 7), (21, 10),
                (22, 1), (22, 2), (22, 4), (22, 5), (22, 8), (22, 9), (22, 10),
                (23, 1), (23, 5), (23, 10),
                (24, 6), (24, 9),
                (25, 1), (25, 2), (25, 5), (25, 8), (25, 9), (25, 10),
                (26, 1), (26, 6), (26, 7), (26, 9),
                (27, 6), (27, 7), (27, 9),
                (28, 3), (28, 4), (28, 5), (28, 7),
                (29, 2), (29, 4), (29, 5), (29, 7),
                (30, 4), (30, 6), (30, 7), (30, 8), (30, 9), (30, 10),
                (31, 5), (31, 6), (31, 8), (31, 9), (31, 10),
                (32, 1), (32, 2), (32, 3), (32, 5), (32, 6), (32, 7),
                (33, 2), (33, 4), (33, 5), (33, 6), (33, 7), (33, 8), (33, 9),
            ),
            "full": (
                (21, 3), (21, 5), (21, 9), (22, 3),
                (23, 2), (23, 5), (23, 9), (24, 8),
                (25, 2), (25, 3), (25, 5), (25, 9),
                (26, 4), (26, 5), (28, 1), (28, 9),
                (30, 1), (31, 2), (33, 1), (33, 7),
            ),
        }
        actual = {
            variant: tuple(sorted(rows))
            for variant, rows in batch.ARTICLE_JA_OVERRIDES.items()
        }
        self.assertEqual(actual, expected)
        self.assertEqual({variant: len(rows) for variant, rows in actual.items()}, {"accessible": 60, "full": 20})

    def test_all_260_rendered_japanese_claims_match_reviewed_contract(self) -> None:
        rendered = []
        for variant in ("accessible", "full"):
            for topic_no in range(21, 34):
                rendered.extend(rendered_article_japanese(topic_no, variant))
        self.assertEqual(len(rendered), 260)
        self.assertEqual(
            hashlib.sha256("\n".join(rendered).encode("utf-8")).hexdigest(),
            "67a1365fb9357fc4506f2f2eca6d802a7c41f8399c852556e703cab9cbf9dd0b",
        )

    def test_page_article_prompt_and_feedback_contract(self) -> None:
        expected_pages = [
            "lesson-goal", "article", "lesson-style", "talk-intro",
            "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6",
            "feedback",
        ]
        for topic_no in batch.TOPICS:
            rendered = {
                variant: batch.build(topic_no, variant)
                for variant in ("accessible", "full")
            }
            for variant, source in rendered.items():
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(
                        re.findall(r'data-page-id="([^"]+)"', source),
                        expected_pages,
                    )
                    self.assertEqual(len(re.findall(r'class="sent" role="button"', source)), 10)
                    self.assertEqual(len(rendered_article_japanese(topic_no, variant)), 10)
                    self.assertEqual(len(re.findall(r'class="section-subtitle ask"', source)), 8)
                    self.assertEqual(len(re.findall(r'class="fb" data-fb=', source)), 8)
                    self.assertEqual(source.count("shared/js/feedback.js"), 1)
                    self.assertNotIn("<style", source)
                    self.assertNotIn("<script>\n", source)
                    self.assertNotIn("yomi.js", source)
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
                        article = batch.TOPICS[topic_no]["articles"][row - 1][
                            0 if variant == "accessible" else 1
                        ]
                        self.assertIn(surface, article)
                        self.assertIn(headword.casefold(), declared)
                        self.assertLessEqual(len(headword.split()), 3)

    def test_recycled_rows_match_real_earlier_owners_exactly(self) -> None:
        expected = {
            25: "restaurant|レストラン|CORE-10",
            27: "restaurant|レストラン|CORE-10",
            28: "recommendation|おすすめ|FT-11",
        }
        self.assertEqual(
            {
                topic_no: contract["recycled"]
                for topic_no, contract in batch.VOCABULARY.items()
                if contract["recycled"]
            },
            expected,
        )
        owner_paths = {
            "CORE-10": batch.TRACK.parent / "1-core-patterns/courses/core-first-exchanges-1/lessons/10-the-cafe-on-the-corner/lesson.html",
            "FT-11": batch.TRACK / "courses/talk-me-lately-accessible/lessons/11-a-show-you-cant-stop-watching/lesson.html",
        }
        for row in expected.values():
            english, japanese, owner = row.split("|")
            source = owner_paths[owner].read_text(encoding="utf-8")
            parsed = vocabulary.parse(source)
            exact_new = {
                (entry["english"], entry["japanese"])
                for entry in parsed["categories"]["new"]
            }
            with self.subTest(row=row):
                self.assertIn((english, japanese), exact_new)

    def test_new_owner_map_is_unique_before_ft21(self) -> None:
        expected = {
            21: ("rewatch",),
            22: ("gateway", "breakthrough"),
            23: ("soundtrack",),
            24: ("backup song", "vocal range"),
            25: ("craving",),
            26: ("food pairing", "acquired taste"),
            27: ("hidden gem", "word-of-mouth"),
            28: ("give away",),
            29: ("underestimate",),
            30: ("sentimental value", "keepsake"),
            31: ("wardrobe", "go-to outfit"),
            32: ("durable", "built to last"),
            33: ("courtesy",),
        }
        actual = {}
        for topic_no, contract in batch.VOCABULARY.items():
            actual[topic_no] = tuple(
                part.split("|", 1)[0]
                for part in contract["new"].split("; ")
                if part
            )
        self.assertEqual(actual, expected)

        earlier = []
        for path in batch.TRACK.parent.glob("*/courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            review = check_deck.meta_content(source, "podo:review-id") or ""
            if review.startswith("FT-") and int(review.split("-")[1]) >= 21:
                continue
            parsed = vocabulary.parse(source)
            earlier.extend(
                entry["english"].casefold()
                for entry in parsed["categories"]["new"]
            )
        for topic_no, words in expected.items():
            for word in words:
                with self.subTest(topic=topic_no, word=word):
                    self.assertNotIn(word.casefold(), earlier)

    def test_curated_semantic_and_no_answer_safety_locks(self) -> None:
        self.assertEqual(batch.TOPICS[26]["prompts"][0]["accessible"], "Pineapple on pizza — yes or no?")
        self.assertEqual(
            batch.TOPICS[23]["articles"][7],
            (
                "Shared spaces shape what we play and how much of our taste we reveal.",
                "Shared spaces shape both what we play and how much of our taste we reveal.",
                "共有する場所では、何を流すか、好みをどこまで見せるかが変わります。",
            ),
        )
        self.assertIn("If you are not in your room", batch.TOPICS[30]["prompts"][0]["accessible_followups"][0])
        self.assertIn("if anyone", batch.TOPICS[21]["prompts"][4]["accessible"].casefold())
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[21]["prompts"][4]["accessible_followups"]))
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[21]["prompts"][5]["accessible_followups"]))
        self.assertIn("if ever", batch.TOPICS[24]["prompts"][1]["accessible"].casefold())
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[24]["prompts"][1]["accessible_followups"]))
        self.assertEqual(
            batch.TOPICS[24]["prompts"][7]["accessible"],
            "Ask me about my voice, range, taste, and confidence, then recommend a karaoke song.",
        )
        self.assertIn("if ever", batch.TOPICS[25]["prompts"][1]["accessible"].casefold())
        self.assertTrue(batch.TOPICS[25]["prompts"][2]["accessible"].startswith("If you ate"))
        self.assertTrue(batch.TOPICS[25]["prompts"][4]["accessible"].startswith("If you shared"))
        self.assertIn("might you regret", batch.TOPICS[25]["prompts"][5]["accessible"])
        self.assertEqual(
            batch.TOPICS[25]["prompts"][3]["accessible_followups"],
            [
                "If you ever do, what tends to cause it?",
                "If you never do, what helps you avoid it?",
            ],
        )
        self.assertNotIn(
            "What usually causes it?",
            batch.TOPICS[25]["prompts"][3]["accessible_followups"],
        )
        for prompt_index in (3, 4, 5):
            followups = batch.TOPICS[26]["prompts"][prompt_index]["accessible_followups"]
            self.assertTrue(all(value.startswith("If ") for value in followups))
        self.assertNotIn("assume", batch.TOPICS[26]["prompts"][3]["accessible_followups"][1])
        self.assertIn("imagine", batch.TOPICS[27]["prompts"][0]["accessible_followups"][1])
        self.assertEqual(
            [item["accessible"] for item in batch.TOPICS[27]["prompts"][1:6]],
            [
                "What is the real or imagined restaurant like?",
                "Where is it, or where would it be?",
                "What do you order there, or what would you order?",
                "How did you find it, or how might someone discover it?",
                "Who have you taken there, or who would you take?",
            ],
        )
        self.assertIn("If not", batch.TOPICS[28]["prompts"][0]["accessible_followups"][1])
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[28]["prompts"][1]["accessible_followups"]))
        self.assertEqual(
            batch.TOPICS[28]["prompts"][7]["accessible"],
            "Ask me what I enjoy reading, then choose a book for me.",
        )
        self.assertEqual(
            batch.TOPICS[28]["prompts"][3]["accessible_followups"][1],
            "If you have not given it, what response would show that your choice worked?",
        )
        self.assertNotIn(
            "who might enjoy it",
            batch.TOPICS[28]["prompts"][3]["accessible_followups"][1],
        )
        self.assertIn("do not do", batch.TOPICS[29]["prompts"][0]["accessible_followups"][1])
        self.assertEqual(batch.TOPICS[29]["prompts"][1]["accessible"], "What do people actually do in that hobby?")
        self.assertIn("or how might", batch.TOPICS[29]["prompts"][3]["accessible"])
        self.assertIn("or think it would need", batch.TOPICS[29]["prompts"][4]["accessible"])
        self.assertIn("していないなら", batch.TOPICS[29]["prompts"][4]["ja"])
        self.assertNotIn("していなら", batch.TOPICS[29]["prompts"][4]["ja"])
        self.assertIn("If not", batch.TOPICS[30]["prompts"][5]["accessible_followups"][1])
        self.assertIn("if anyone", batch.TOPICS[30]["prompts"][4]["accessible"].casefold())
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[30]["prompts"][4]["accessible_followups"]))
        self.assertEqual(
            batch.TOPICS[30]["prompts"][2]["accessible_followups"],
            [
                "If someone else was involved, what did they add to the story?",
                "If nobody else was, what made the moment memorable?",
            ],
        )
        self.assertNotIn(
            "Who else was part of that moment?",
            batch.TOPICS[30]["prompts"][2]["accessible_followups"],
        )
        self.assertIn("if anything", batch.TOPICS[31]["prompts"][4]["accessible"].casefold())
        self.assertIn("if anyone", batch.TOPICS[31]["prompts"][6]["accessible"].casefold())
        self.assertEqual(
            batch.TOPICS[31]["prompts"][5]["accessible_followups"][1],
            "Could anyone wear it well, or is the item itself the problem?",
        )
        self.assertNotIn(
            "Who wears it well?",
            batch.TOPICS[31]["prompts"][5]["accessible_followups"],
        )
        self.assertIn("If not", batch.TOPICS[33]["prompts"][0]["accessible_followups"][1])
        self.assertIn("if ever", batch.TOPICS[33]["prompts"][1]["accessible"].casefold())
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[33]["prompts"][1]["accessible_followups"]))
        self.assertIn("end up on your plate", batch.TOPICS[33]["prompts"][1]["accessible_followups"][0])
        self.assertTrue(batch.TOPICS[33]["prompts"][5]["accessible"].startswith("Would you say"))
        self.assertTrue(all(value.startswith("If ") for value in batch.TOPICS[33]["prompts"][5]["accessible_followups"]))

    def test_reviewed_claim_rows_lock_exact_accessible_full_and_variant_japanese(self) -> None:
        expected = {
            (21, 3): (
                "We can relax and notice details when we no longer have to follow the plot.",
                "Once we no longer need to track the plot, we can notice quieter visual and emotional details.",
                "筋を追わなくてよくなると、くつろいで細かな点に気づけます。",
                "筋を追う必要がなくなると、映像や感情表現のさりげない細部に気づけます。",
            ),
            (21, 9): (
                "Rewatching can become a small ritual during stressful or unsettled times.",
                "A rewatch can become a reassuring ritual during stressful or unsettled periods.",
                "見返すことが、ストレスが多い時や落ち着かない時の小さな習慣になることがあります。",
                "見返すことが、ストレスが多い時や落ち着かない時に安心できる小さな習慣になることがあります。",
            ),
            (22, 2): (
                "A song, film, or game can feel exciting even when much of the language is unclear.",
                "A song, film, or game can be absorbing even when much of its language remains unclear.",
                "言葉の多くが分からなくても、歌や映画、ゲームにわくわくすることがあります。",
                "言葉の多くが分からなくても、歌や映画、ゲームに夢中になることがあります。",
            ),
            (23, 7): (
                "A song from years ago can bring back how we felt then for a moment.",
                "A song from years ago can briefly bring back how we felt at that time.",
                "何年も前の曲を聴くと、当時の気持ちが一瞬よみがえることがあります。",
                "何年も前の曲を聴くと、当時の気持ちが一瞬よみがえることがあります。",
            ),
            (23, 5): (
                "Lyrics can compete with reading or writing because both need language attention.",
                "Lyrics can interfere with reading or writing because both compete for the same language attention.",
                "歌詞も読み書きも言葉への集中を必要とするため、歌詞が読み書きの妨げになることがあります。",
                "歌詞も読み書きも言葉への集中を必要とするため、歌詞が読み書きの妨げになることがあります。",
            ),
            (24, 4): (
                "A familiar opening helps people recognize the song quickly.",
                "A recognizable opening lets everyone identify the song immediately.",
                "なじみのあるイントロなら、みんながすぐに何の曲か分かります。",
                "なじみのあるイントロなら、みんながすぐに何の曲か分かります。",
            ),
            (25, 3): (
                "A craving may point us toward salty, warm, or familiar food.",
                "A strong craving may pull us toward food that is salty, warm, rich, or deeply familiar.",
                "無性に何かを食べたい気持ちで、塩辛いもの、温かいもの、なじみのあるものを選ぶことがあります。",
                "無性に何かを食べたいときは、塩辛いもの、温かいもの、こってりしたものや、強くなじみを感じるものに手が伸びることがあります。",
            ),
            (25, 2): (
                "At that hour, convenience can matter more than a perfect meal.",
                "At that hour, speed and convenience often outweigh the idea of a balanced meal.",
                "その時間には、理想的な食事より手軽さが大切になることがあります。",
                "その時間には、バランスのよい食事より、速さや手軽さを優先しがちです。",
            ),
            (25, 5): (
                "Eating alone and sharing food can create very different late-night memories.",
                "A solitary snack and a shared late-night meal can carry completely different emotional meanings.",
                "一人で食べる夜食と、誰かと分けて食べる夜食では、まったく違う思い出が生まれます。",
                "一人で食べる軽食と誰かと囲む夜食では、込められる気持ちや意味がまったく違うことがあります。",
            ),
            (25, 9): (
                "Visitors may not understand why an ordinary dish feels perfect at that time.",
                "A visitor may miss why an ordinary dish feels exactly right in that particular late-night setting.",
                "旅行者には、なぜ普通の料理がその時間にはぴったりなのか分からないことがあります。",
                "旅行者には、なぜ普通の料理が、夜遅くのその場面にこそぴったりなのか分からないことがあります。",
            ),
            (28, 1): (
                "Giving a book away means making a guess about another person's interests.",
                "Giving a book away requires a careful guess about another person's interests, time, and attention.",
                "本を贈ることは、相手の興味を想像して選ぶことです。",
                "本を贈るときは、相手の興味だけでなく、その本を読む時間や集中力まで慎重に考える必要があります。",
            ),
            (28, 5): (
                "The recipient may feel pressure if the giver keeps asking whether they finished it.",
                "Repeatedly asking whether the recipient finished the book can turn a gift into an obligation.",
                "贈った人から読み終えたか何度も聞かれると、受け取った人はプレッシャーを感じることがあります。",
                "読み終えたか何度も聞くと、贈り物が義務のようになることがあります。",
            ),
            (29, 9): (
                "An honest invitation includes both the pleasure and the frustrating parts.",
                "An honest invitation explains both the pleasure and the frustrating parts instead of hiding them.",
                "正直に誘うなら、楽しさだけでなく、もどかしい部分も隠さず伝えます。",
                "正直に誘うなら、楽しさだけでなく、もどかしい部分も隠さず伝えます。",
            ),
            (30, 1): (
                "An ordinary object can become valuable because of the story attached to it.",
                "An ordinary object can become irreplaceable because of the personal history attached to it.",
                "普通の物でも、そこに結びついた物語によって、価値のあるものになります。",
                "普通の物でも、そこに結びついた個人的な歴史によって、かけがえのないものになります。",
            ),
            (31, 2): (
                "Comfort, weather, and daily routines often decide more than fashion.",
                "Comfort, climate, work, and daily routines often shape our choices more strongly than fashion does.",
                "流行よりも、着心地、天気、日課が服を決めることがよくあります。",
                "流行よりも、着心地、気候、仕事、日課のほうが服の選択に強く影響することがよくあります。",
            ),
            (33, 1): (
                "Food offered by another person can carry effort, welcome, and pride.",
                "Food offered by another person can carry effort, hospitality, family history, and pride.",
                "人から出された料理には、手間、歓迎の気持ち、誇りが込められていることがあります。",
                "人から出された料理には、手間、もてなしの気持ち、家族の歴史、誇りが込められていることがあります。",
            ),
            (33, 2): (
                "That meaning can make an honest dislike difficult to express.",
                "That social meaning can make a simple statement of dislike feel unexpectedly harsh.",
                "その意味があるため、嫌いだと正直に伝えにくくなることがあります。",
                "その意味があるため、嫌いだと正直に言うだけでも強く聞こえることがあります。",
            ),
            (33, 7): (
                "Hosts often prefer useful information to praise or enthusiasm that is obviously false.",
                "Thoughtful hosts often prefer useful information to praise or enthusiasm that is clearly insincere.",
                "もてなす人は、明らかに本心ではない褒め言葉や反応より、役立つ情報を好むことがあります。",
                "思いやりのあるホストは、明らかに本心ではない褒め言葉や反応より、役立つ情報を好むことがあります。",
            ),
        }
        rendered = {
            (topic_no, variant): rendered_article_japanese(topic_no, variant)
            for topic_no, _row in expected
            for variant in ("accessible", "full")
        }
        for (topic_no, row), (accessible, full, accessible_ja, full_ja) in expected.items():
            with self.subTest(topic=topic_no, row=row):
                self.assertEqual(
                    batch.TOPICS[topic_no]["articles"][row - 1][:2],
                    (accessible, full),
                )
                self.assertEqual(rendered[(topic_no, "accessible")][row - 1], accessible_ja)
                self.assertEqual(rendered[(topic_no, "full")][row - 1], full_ja)

        exact_full_locks = {
            (21, 5): "ほかの人と見ると、見慣れて気に留めなくなっていた場面に改めて気づけます。",
            (22, 3): "楽しさがあれば、反復を作業と感じることなく、同じ英語に何度も触れられます。",
        }
        for (topic_no, row), japanese in exact_full_locks.items():
            with self.subTest(topic=topic_no, row=row, variant="full"):
                self.assertEqual(rendered_article_japanese(topic_no, "full")[row - 1], japanese)

        self.assertNotIn("思いやり", rendered[(33, "accessible")][6])
        self.assertIn("思いやり", rendered[(33, "full")][6])

    def test_every_deck_passes_static_checker_after_review_completion(self) -> None:
        for topic_no in batch.TOPICS:
            for variant in ("accessible", "full"):
                path = batch.output_path(topic_no, variant)
                errors, warnings = check_deck.check(path)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(errors, [])
                    self.assertEqual(warnings, [])
                    self.assertIn(
                        '<meta name="podo:proofread-status" content="complete">',
                        path.read_text(encoding="utf-8"),
                    )


if __name__ == "__main__":
    unittest.main()
