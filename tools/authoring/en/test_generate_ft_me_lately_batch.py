from __future__ import annotations

import hashlib
import re
import unittest

import generate_ft_me_lately_batch as batch
import vocabulary


class FreetalkingMeLatelyBatchTests(unittest.TestCase):
    def test_batch_is_complete_and_explicit(self) -> None:
        self.assertEqual(list(batch.TOPICS), list(range(10, 21)))
        for topic_no, topic in batch.TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(len(topic["articles"]), 10)
                self.assertEqual(len(topic["prompts"]), 8)
                self.assertTrue(all(accessible != full for accessible, full, _ja in topic["articles"]))
                self.assertEqual(len(batch.CLAIM_ORDER[topic_no]), 10)
                self.assertEqual(len(set(batch.CLAIM_ORDER[topic_no])), 10)
                self.assertEqual(set(batch.GLOSSES[topic_no]), {"accessible", "full"})
                self.assertNotIn("new", topic)
                self.assertEqual(set(batch.VOCABULARY[topic_no]), {"accessible", "full"})
                for variant in ("accessible", "full"):
                    self.assertEqual(
                        set(batch.VOCABULARY[topic_no][variant]),
                        {"new", "recycled", "assumed", "receptive"},
                    )
                    # FT15 reuses the explicitly taught Core budget term in
                    # both language-load variants.
                    expected_recycled = (
                        "budget|予算|CORE-53" if topic_no == 15 else ""
                    )
                    self.assertEqual(
                        batch.VOCABULARY[topic_no][variant]["recycled"],
                        expected_recycled,
                    )
                all_vocabulary = " ".join(
                    batch.VOCABULARY[topic_no][variant][category]
                    for variant in ("accessible", "full")
                    for category in ("new", "recycled", "assumed", "receptive")
                )
                for required in batch.REQUIRED_VOCABULARY.get(topic_no, ()):
                    self.assertIn(required + "|", all_vocabulary)
                for item in topic["prompts"]:
                    for variant in ("accessible", "full"):
                        followups = item[f"{variant}_followups"]
                        self.assertIn(len(followups), (2, 3))
                        self.assertEqual(len(followups), len(set(followups)))
                        self.assertTrue(all(value.endswith("?") for value in followups))

    def test_variant_vocabulary_and_gloss_ownership(self) -> None:
        full_only = {
            10: {"opportunity cost", "identity", "competent"},
            11: {"streaming service", "obligation", "compelling"},
            12: {"credible", "self-promotion", "bias"},
            13: {"anticipate", "solitude", "coordination"},
            14: {"accountability", "ambiguous", "non-negotiable"},
            15: {"discretionary", "recurring", "durability"},
            16: {"uncertainty", "novel", "companion"},
            17: {"validate", "circumstance", "performance"},
            18: {"production", "sensory", "emotional history"},
            19: {"procrastination", "momentum", "emotional load"},
            20: {"reassurance", "audit", "dependence"},
        }
        self_criticism_topics = set()
        for topic_no in batch.TOPICS:
            for variant in ("accessible", "full"):
                rendered = batch.build(topic_no, variant)
                parsed = vocabulary.parse(rendered)
                categories = parsed["categories"]
                ownership = {
                    entry["english"].casefold(): category
                    for category, entries in categories.items()
                    for entry in entries
                }
                for _row, (_surface, headword, _ja) in batch.GLOSSES[topic_no][variant].items():
                    with self.subTest(topic=topic_no, variant=variant, gloss=headword):
                        self.assertIn(headword.casefold(), ownership)
                if "self-criticism" in ownership:
                    self_criticism_topics.add(topic_no)
            accessible_words = {
                part.split("|", 1)[0].strip().casefold()
                for value in batch.VOCABULARY[topic_no]["accessible"].values()
                for part in value.split(";") if part.strip()
            }
            self.assertTrue(full_only[topic_no].isdisjoint(accessible_words))
            accessible_glosses = {
                headword.casefold()
                for _row, (_surface, headword, _ja) in batch.GLOSSES[topic_no]["accessible"].items()
            }
            full_glosses = {
                headword.casefold()
                for _row, (_surface, headword, _ja) in batch.GLOSSES[topic_no]["full"].items()
            }
            overlap = len(accessible_glosses & full_glosses) / max(1, len(accessible_glosses))
            self.assertLessEqual(overlap, 0.70)
        self.assertEqual(self_criticism_topics, {19})

        ft19_accessible = batch.VOCABULARY[19]["accessible"]
        self.assertNotIn("avoid|避ける", ft19_accessible["new"])
        self.assertEqual(ft19_accessible["recycled"], "")
        self.assertIn("avoid|避ける", ft19_accessible["assumed"])

    def test_curated_no_answer_referent_regressions(self) -> None:
        # This is intentionally a small lexical regression net around the
        # reviewed failures; it does not pretend to prove semantic continuity.
        forbidden = {
            11: ("the show",),
            14: ("this goal", "that goal", "stopping you now"),
            15: ("this spending", "the spending", "purchase or non-purchase"),
            16: ("finally try it", "was it what", "do it again"),
            17: ("that effort", "small wins like this"),
            18: ("that sound or song", "does the song remind", "music like that"),
            19: ("after finishing a delayed task", "when a task is delayed again"),
            20: ("which of those things", "in your bag?"),
        }
        for topic_no, phrases in forbidden.items():
            later = " ".join(
                value
                for item in batch.TOPICS[topic_no]["prompts"][1:]
                for value in (item["accessible"], item["full"], *item["accessible_followups"], *item["full_followups"])
            ).casefold()
            for phrase in phrases:
                with self.subTest(topic=topic_no, phrase=phrase):
                    self.assertNotIn(phrase, later)

    def test_followups_do_not_encode_yes_no_caveat_branches(self) -> None:
        caveat = re.compile(r"^If (?:yes|not|so|it was|something|nothing|it does)\b", re.I)
        for topic_no, topic in batch.TOPICS.items():
            for item in topic["prompts"]:
                for variant in ("accessible", "full"):
                    for followup in item[f"{variant}_followups"]:
                        with self.subTest(topic=topic_no, variant=variant, followup=followup):
                            self.assertIsNone(caveat.search(followup))

    def test_accessible_prompts_exclude_reviewed_high_load_phrasing(self) -> None:
        prompts = " ".join(
            value
            for topic in batch.TOPICS.values()
            for item in topic["prompts"]
            for value in (item["accessible"], *item["accessible_followups"])
        ).casefold()
        for phrase in (
            "non-essential", "strongest argument", "purchase or non-purchase",
            "discretionary", "persuade", "non-negotiable", "motivation",
            "unfamiliar", "adapt", "recognition", "stable", "represents",
        ):
            self.assertNotIn(phrase, prompts)

    def test_final_independent_review_repairs_are_source_locked(self) -> None:
        ft11 = batch.TOPICS[11]
        self.assertEqual(
            ft11["prompts"][1]["accessible"],
            "When was the last time you watched an episode of a show?",
        )
        self.assertEqual(
            ft11["prompts"][6]["full_followups"],
            [
                "Which commitment would make you stop?",
                "What tends to happen when you ignore that limit?",
            ],
        )

        ft12 = batch.TOPICS[12]
        self.assertIn("general compliment", ft12["articles"][1][0])
        self.assertNotIn("sincere", ft12["prompts"][1]["full"].casefold())
        self.assertIn("いちばんうれしい", ft12["prompts"][1]["ja"])

        ft14 = batch.TOPICS[14]
        self.assertNotIn("than another", ft14["prompts"][2]["full"])
        self.assertEqual(
            ft14["prompts"][4]["accessible_followups"],
            ["Which goal changed most this year?", "What made you continue, change, or drop it?"],
        )
        self.assertEqual(
            ft14["prompts"][4]["full_followups"],
            ft14["prompts"][4]["accessible_followups"],
        )

        ft15 = batch.TOPICS[15]
        for followup in (
            *ft15["prompts"][2]["accessible_followups"],
            *ft15["prompts"][2]["full_followups"],
        ):
            self.assertNotIn("answer", followup.casefold())
            self.assertNotIn("skip", followup.casefold())
        self.assertEqual(
            ft15["prompts"][3]["accessible_followups"][0],
            "Which benefit from that spending lasts the longest?",
        )
        self.assertIn("one good reason", ft15["prompts"][4]["full"].casefold())
        self.assertNotIn("strongest argument", ft15["prompts"][4]["full"].casefold())

        self.assertEqual(
            batch.TOPICS[18]["articles"][6][0],
            "Overplaying a song can temporarily weaken its emotional effect.",
        )
        self.assertIn("get us moving again", batch.TOPICS[19]["articles"][6][0])
        self.assertIn("could you do next", batch.TOPICS[19]["prompts"][7]["full"])
        self.assertNotIn("will you decide", batch.TOPICS[19]["prompts"][7]["full"])

        ft20_accessible = [row[0] for row in batch.TOPICS[20]["articles"]]
        self.assertIn("decide to remove them", ft20_accessible[3])
        self.assertIn("different situations", ft20_accessible[4])

    def test_checked_in_decks_are_exact_generator_output(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            for variant in ("accessible", "full"):
                slug = f'{topic_no:02d}-{topic["slug"]}'
                path = batch.TRACK / "courses" / f"{batch.COURSE}-{variant}" / "lessons" / slug / "lesson.html"
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertTrue(path.is_file())
                    self.assertEqual(path.read_text(encoding="utf-8"), batch.build(topic_no, variant))
                    self.assertIn(
                        '<meta name="podo:proofread-status" content="complete">',
                        batch.build(topic_no, variant),
                    )

    def test_opening_matches_regenerated_authoritative_brief(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            brief = batch.TRACK / "toc" / f"FT-{topic_no}.md"
            source = brief.read_text(encoding="utf-8")
            opening = topic["prompts"][0]["accessible"]
            with self.subTest(topic=topic_no):
                self.assertIn(f'- **Opening:** "{opening}"', source)

    def test_pair_contract_and_page_inventory(self) -> None:
        expected_pages = ["lesson-goal", "article", "lesson-style", "talk-intro", "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6", "feedback"]
        for topic_no in batch.TOPICS:
            rendered = {variant: batch.build(topic_no, variant) for variant in ("accessible", "full")}
            for variant, source in rendered.items():
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(re.findall(r'data-page-id="([^"]+)"', source), expected_pages)
                    self.assertEqual(len(re.findall(r'class="sent" role="button"', source)), 10)
                    self.assertEqual(len(re.findall(r'class="section-subtitle ask"', source)), 8)
                    self.assertEqual(len(re.findall(r'class="fb" data-fb=', source)), 8)
                    self.assertNotIn("A useful starting point is this:", source)
                    self.assertNotIn("Seen more broadly,", source)
                    self.assertNotIn("Taken together, the point is that", source)
            accessible_claims = re.findall(r'data-claim-id="([^"]+)"', rendered["accessible"])
            full_claims = re.findall(r'data-claim-id="([^"]+)"', rendered["full"])
            self.assertEqual(accessible_claims, list(batch.CLAIM_ORDER[topic_no]))
            self.assertEqual(full_claims, list(batch.CLAIM_ORDER[topic_no]))
            accessible_ja = re.findall(r'<span class="s-ja">(.*?)</span>', rendered["accessible"])
            full_ja = re.findall(r'<span class="s-ja">(.*?)</span>', rendered["full"])
            for row in batch.FULL_JA_OVERRIDES.get(topic_no, {}):
                self.assertNotEqual(accessible_ja[row - 1], full_ja[row - 1])

    def test_paired_japanese_editorial_inventory(self) -> None:
        expected_override_rows = {
            10: {1, 2, 3, 4, 5, 6, 8, 10}, 11: {7}, 12: {1, 10},
            13: {1, 4, 5, 10}, 14: {1, 3, 5, 6, 7, 8, 10}, 15: {3, 4, 8},
            16: {2, 3, 4, 6, 8, 9, 10}, 17: {3, 4, 5, 7, 8},
            18: {2, 4, 6, 8, 9}, 19: {6, 8, 10}, 20: {1, 2, 5, 6, 7, 10},
        }
        self.assertEqual(
            {topic: set(rows) for topic, rows in batch.FULL_JA_OVERRIDES.items()},
            expected_override_rows,
        )
        accessible_12 = batch.build(12, "accessible")
        accessible_19 = batch.build(19, "accessible")
        accessible_20 = batch.build(20, "accessible")
        self.assertIn("たった一つの正直な言葉", accessible_12)
        self.assertIn("気持ちの負担が増える", accessible_19)
        self.assertIn("充電器を持つ必要が生まれました", accessible_20)
        self.assertIn("正確に測れるとは限りません", batch.build(17, "full"))
        self.assertIn("バッテリーと充電器への新たな依存", batch.build(20, "full"))

    def test_manual_ft9_pair_is_preserved_and_outside_generator_ownership(self) -> None:
        self.assertNotIn(9, batch.TOPICS)
        for variant, (path, expected) in batch.PRESERVED_FT9.items():
            with self.subTest(variant=variant):
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
                source = path.read_text(encoding="utf-8")
                self.assertIn('data-page-id="talk-intro"', source)
                self.assertEqual(source.count('data-fb-spoken-label="Student\'s sentence"'), 8)


if __name__ == "__main__":
    unittest.main()
