from __future__ import annotations

import hashlib
import html
import re
import unittest
from unittest import mock

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_deck
import generate_ft_people_and_ties_batch as batch
import vocabulary


def productive_english(source: str) -> str:
    zones = re.findall(r'<span class="s-line"><span class="s-ko">(.*?)</span><span class="s-mark"', source, re.S)
    zones.extend(re.findall(r'<p class="section-subtitle ask">.*?<span class="ko">(.*?)</span><span class="ja">', source, re.S))
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", zone)) for zone in zones)


class FreetalkingPeopleAndTiesBatchTests(unittest.TestCase):
    def test_source_inventory_is_exact_explicit_and_excludes_ft49(self) -> None:
        self.assertEqual(batch.TOPIC_NUMBERS, (47, 48, 50, 51, 52, 53, 54, 55, 56))
        self.assertEqual(tuple(batch.TOPICS), batch.TOPIC_NUMBERS)
        self.assertNotIn(49, batch.TOPICS)
        self.assertEqual(set(batch.TOPICS), set(batch.CLAIM_ORDER))
        self.assertEqual(set(batch.TOPICS), set(batch.VOCABULARY))
        self.assertEqual(set(batch.TOPICS), set(batch.GLOSSES))
        for topic_no, data in batch.TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(len(data["articles"]), 10)
                self.assertTrue(all(len(row) == 4 for row in data["articles"]))
                self.assertTrue(all(a_en != f_en for a_en, f_en, _a_ja, _f_ja in data["articles"]))
                self.assertTrue(all(a_ja != f_ja for _a_en, _f_en, a_ja, f_ja in data["articles"]))
                self.assertEqual(len(data["prompts"]), 8)
                self.assertEqual(len(batch.CLAIM_ORDER[topic_no]), 10)
                self.assertGreaterEqual(sum(item["accessible_ja"] != item["full_ja"] for item in data["prompts"]), 3)
                for item in data["prompts"]:
                    self.assertNotEqual(item["accessible"], item["full"])
                    for variant in ("accessible", "full"):
                        followups = item[f"{variant}_followups"]
                        self.assertIn(len(followups), (2, 3))
                        self.assertEqual(len(followups), len(set(followups)))
                        self.assertTrue(all(value.endswith("?") for value in followups))

    def test_all_authored_claim_and_prompt_bytes_are_locked(self) -> None:
        claims, prompts = [], []
        for topic_no in batch.TOPIC_NUMBERS:
            for row in batch.TOPICS[topic_no]["articles"]:
                claims.extend(row)
            for item in batch.TOPICS[topic_no]["prompts"]:
                prompts.extend([
                    item["accessible"], item["accessible_ja"], *item["accessible_followups"],
                    item["full"], item["full_ja"], *item["full_followups"],
                ])
        self.assertEqual(len(claims), 360)
        self.assertEqual(hashlib.sha256("\n".join(claims).encode()).hexdigest(), "4470b9234f82ee4565e91599e1b22da2770be39f16e6d537c41ec42bd0436d25")
        self.assertEqual(len(prompts), 576)
        self.assertEqual(hashlib.sha256("\n".join(prompts).encode()).hexdigest(), "d9547d1d44e0e7aea4210dbc7fb6eebd377a837bf4805ab27c228f14d86b0193")

    def test_all_180_rendered_article_claims_have_exact_variant_japanese(self) -> None:
        japanese = []
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in ("accessible", "full"):
                source = batch.build(topic_no, variant)
                rendered = [html.unescape(value) for value in re.findall(r'<span class="s-open"><span class="s-ja">([^<]+)</span>', source)]
                expected = [row[2 if variant == "accessible" else 3] for row in batch.TOPICS[topic_no]["articles"]]
                self.assertEqual(rendered, expected)
                japanese.extend(rendered)
        self.assertEqual(len(japanese), 180)
        self.assertEqual(hashlib.sha256("\n".join(japanese).encode()).hexdigest(), "1f4898c1c10e4e9c0df820a8008f9b49a6b347c2bc988258954ba2dd64b34000")

    def test_checked_in_decks_are_exact_complete_generator_output(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in ("accessible", "full"):
                expected = batch.build(topic_no, variant)
                path = batch.output_path(topic_no, variant)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(path.read_text(encoding="utf-8"), expected)
                    self.assertEqual(expected.count('<meta name="podo:proofread-status" content="complete">'), 1)
                    self.assertNotIn('podo:proofread-status" content="pending', expected)

    def test_ft49_is_hash_guarded_and_outside_every_owned_output(self) -> None:
        batch.assert_preserved()
        owned = {batch.output_path(n, v) for n in batch.TOPIC_NUMBERS for v in ("accessible", "full")}
        for variant, (path, digest) in batch.PRESERVED.items():
            with self.subTest(variant=variant):
                self.assertNotIn(path, owned)
                self.assertEqual(batch.file_hash(path), digest)
        with mock.patch.object(batch, "file_hash", return_value="0" * 64):
            with self.assertRaisesRegex(SystemExit, "FT-49 accessible changed"):
                batch.assert_preserved()

    def test_page_shell_counts_controls_and_no_local_overrides(self) -> None:
        expected_pages = ["lesson-goal", "article", "lesson-style", "talk-intro", "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6", "feedback"]
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in ("accessible", "full"):
                source = batch.build(topic_no, variant)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(re.findall(r'data-page-id="([^"]+)"', source), expected_pages)
                    self.assertEqual(source.count('class="sent" role="button"'), 10)
                    self.assertEqual(source.count('class="section-subtitle ask"'), 8)
                    self.assertEqual(source.count('class="fb" data-fb='), 8)
                    self.assertEqual(source.count("shared/js/feedback.js"), 1)
                    self.assertNotIn("<style", source)
                    self.assertNotIn("<script>\n", source)
                    self.assertNotIn("yomi.js", source)
                    self.assertNotIn("data-choice-scope", source)

    def test_exact_brief_titles_openings_and_claim_ids(self) -> None:
        for topic_no, data in batch.TOPICS.items():
            brief = (batch.TRACK / "toc" / f"FT-{topic_no}.md").read_text(encoding="utf-8")
            with self.subTest(topic=topic_no):
                self.assertIn(f"# FT-{topic_no} · {data['title']}", brief)
                self.assertIn(f'- **Opening:** "{data["prompts"][0]["accessible"]}"', brief)
            for variant in ("accessible", "full"):
                self.assertEqual(re.findall(r'data-claim-id="([^"]+)"', batch.build(topic_no, variant)), list(batch.CLAIM_ORDER[topic_no]))

    def test_variant_japanese_is_rendered_from_its_matching_prompt(self) -> None:
        for topic_no, data in batch.TOPICS.items():
            for variant in ("accessible", "full"):
                source = batch.build(topic_no, variant)
                rendered = re.findall(r'<p class="section-subtitle ask">.*?<span class="ja">(.*?)</span></p>', source, re.S)
                self.assertEqual(len(rendered), 8)
                for item, actual in zip(data["prompts"], rendered, strict=True):
                    expected = item[f"{variant}_ja"]
                    if sum(item[variant].count(mark) for mark in ".!?") == 1:
                        expected = expected.replace("。", "、")
                    self.assertEqual(html.unescape(actual), expected)

    def test_question_pools_are_distinct_standalone_and_non_defensive(self) -> None:
        banned = (
            "if yes", "if not", "if none", "if nobody", "if something", "if it happened",
            "real or imagined", "familiar or imagined", "public or fictional", "public or imagined",
            "no recent message", "would you prefer to keep", "comfortable discussing",
        )
        for variant in ("accessible", "full"):
            global_mains, global_followup_sets, global_followups = [], [], []
            for topic_no, data in batch.TOPICS.items():
                mains = [item[variant] for item in data["prompts"]]
                followup_sets = [tuple(item[f"{variant}_followups"]) for item in data["prompts"]]
                followups = [value for values in followup_sets for value in values]
                corpus = " ".join((*mains, *followups)).casefold()
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(len(mains), len(set(mains)))
                    self.assertEqual(len(followup_sets), len(set(followup_sets)))
                    self.assertEqual(len(followups), len(set(followups)))
                    for phrase in banned:
                        self.assertNotIn(phrase, corpus)
                    self.assertTrue(all(question.endswith("?") for question in mains))
                global_mains.extend(mains)
                global_followup_sets.extend(followup_sets)
                global_followups.extend(followups)
            self.assertEqual(len(global_mains), len(set(global_mains)))
            self.assertEqual(len(global_followup_sets), len(set(global_followup_sets)))
            self.assertEqual(len(global_followups), len(set(global_followups)))

    def test_exact_accessible_openings_match_authoritative_briefs(self) -> None:
        expected = {
            47: "What helps a friendship last when life changes?",
            48: "Which is easier to misread at first: a quiet person or a very talkative person?",
            50: "Which activity feels hardest to do alone?",
            51: "You're seated next to someone you've never met. What do you ask?",
            52: "After an ordinary argument, who should reach out first?",
            53: "Why do people's social circles change over time?",
            54: "What makes someone easy to talk to?",
            55: "Which is easier to remember: a short piece of advice or a personal story?",
            56: "What makes someone the right person to call first in an emergency?",
        }
        self.assertEqual({n: row["prompts"][0]["accessible"] for n, row in batch.TOPICS.items()}, expected)

    def test_ft49_manual_pair_has_exact_repaired_contract(self) -> None:
        expected_openings = {
            "accessible": "What do people hope an MBTI result will explain?",
            "full": "What can make an MBTI result seem accurate?",
        }
        for variant, (path, _digest) in batch.PRESERVED.items():
            source = path.read_text(encoding="utf-8")
            prompts = re.findall(r'<p class="section-subtitle ask">.*?<span class="ko">(.*?)</span><span class="ja">', source, re.S)
            followups = [check_deck.plain_text(value) for value in re.findall(r'<li>(.*?)</li>', source, re.S)]
            with self.subTest(variant=variant):
                self.assertEqual(len(prompts), 8)
                self.assertEqual(html.unescape(prompts[0]), expected_openings[variant])
                self.assertEqual(len(prompts), len(set(prompts)))
                self.assertEqual(source.count('data-fb-spoken-label="Student\'s sentence"'), 8)
                self.assertIn("Treat these pages as a pool, not a sequence.", source)
                self.assertIn("Please read the title aloud.", source)
                self.assertNotIn('class="known lines"', source)
                self.assertEqual(len(followups), len(set(followups)))
                self.assertFalse(any(value.casefold().startswith(("if yes", "if not", "if none")) for value in followups))

    def test_round_two_old_unsafe_or_misaligned_copy_cannot_return(self) -> None:
        corpus = repr(batch.TOPICS)
        old_strings = (
            "still deserves to travel", "closest thing you'd try", "nearest equivalent you would attempt",
            "what useful advice have you ignored", "which sound advice have you chosen not to follow",
            "which decision made the advice relevant", "proved insufficient", "harmless example",
            "話せる害のない例", "身を守ろうとせずに話す", "第一印象を変える何が起きましたか",
            "頼れる人たち", "How would you adapt it to their situation?",
            "What do you actually discuss most?", "Which topics feel easy to discuss",
            "Was there one person or group you talked to most five years ago",
            "If one contact stood out, what connected you then?",
            "what purpose did it serve", "which purpose did it serve",
        )
        for old in old_strings:
            with self.subTest(old=old):
                self.assertNotIn(old.casefold(), corpus.casefold())

    def test_round_two_exact_bilingual_claim_and_metadata_locks(self) -> None:
        self.assertEqual(batch.TOPICS[47]["prompts"][7]["accessible_ja"], "よい友情に、自分は何を与えていますか？")
        self.assertEqual(batch.TOPICS[48]["prompts"][2]["accessible_ja"], "どのような証拠が、第一印象を変えることがありますか？")
        self.assertEqual(batch.TOPICS[50]["articles"][8][2], "ほかの人が一人で行動するのを見ると、その活動が自分にもできそうに感じます。")
        self.assertEqual(batch.TOPICS[52]["articles"][5][3], "自己弁護ばかりせずに話すために、少し距離が必要な人もいます。")
        self.assertIn("経験や意図を信頼", batch.TOPICS[55]["articles"][2][2])
        self.assertTrue(batch.TOPICS[56]["articles"][5][0].startswith("In the first few minutes"))
        self.assertIn("advice, coordination, and reassurance", batch.TOPICS[56]["articles"][6][0])
        self.assertIn("助言や手配、安心感", batch.TOPICS[56]["articles"][6][2])
        self.assertEqual(batch.VOCABULARY[56]["new"], "support network|人やサービスを含む支援体制")
        self.assertEqual(batch.GLOSSES[47]["accessible"][8], ("resentment", "resentment", "言えない不満"))
        self.assertEqual(batch.GLOSSES[56]["accessible"][10], ("support network", "support network", "人やサービスを含む支援体制"))
        self.assertEqual(
            batch.TOPICS[54]["prompts"][6]["accessible_followups"][0],
            "Why does that person become important?",
        )
        self.assertEqual(
            batch.TOPICS[54]["prompts"][6]["full_followups"][0],
            "Why does that person become important?",
        )

    def test_accessible_gloss_load_remains_small_after_required_repairs(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            with self.subTest(topic=topic_no):
                self.assertLessEqual(len(batch.GLOSSES[topic_no]["accessible"]), 2)

    def test_exact_new_owner_map_is_unique_and_same_in_both_variants(self) -> None:
        expected = {
            47: ("drift apart",), 48: ("first impression",), 50: ("comfort zone",),
            51: ("small talk", "conversation starter"), 52: ("make up", "reach out"),
            53: ("fade",), 54: ("stay in touch",), 55: ("pass on",),
            56: ("support network",),
        }
        actual = {n: tuple(part.split("|", 1)[0] for part in row["new"].split("; ") if part) for n, row in batch.VOCABULARY.items()}
        self.assertEqual(actual, expected)
        earlier_new = {}
        for path in batch.TRACK.parent.glob("*/courses/*/lessons/*/lesson.html"):
            source = path.read_text(encoding="utf-8")
            review = check_deck.meta_content(source, "podo:review-id") or ""
            if review.startswith("FT-") and int(review.split("-")[1]) >= 47:
                continue
            for entry in vocabulary.parse(source)["categories"]["new"]:
                earlier_new.setdefault(entry["english"].casefold(), []).append(review)
        for words in expected.values():
            for word in words:
                self.assertNotIn(word.casefold(), earlier_new)
        for topic_no in batch.TOPIC_NUMBERS:
            metas = []
            for variant in ("accessible", "full"):
                parsed = vocabulary.parse(batch.build(topic_no, variant))["categories"]
                metas.append(tuple((c, e["english"], e["japanese"], e["source"]) for c in vocabulary.CATEGORIES for e in parsed[c]))
            self.assertEqual(metas[0], metas[1])

    def test_exact_recycled_provenance_and_same_batch_dependency(self) -> None:
        expected = {
            47: "friend|友だち|CORE-2", 48: "",
            50: "", 51: "", 52: "", 53: "drift apart|疎遠になる|FT-47",
            54: "", 55: "", 56: "",
        }
        self.assertEqual({n: row["recycled"] for n, row in batch.VOCABULARY.items()}, expected)
        self.assertLess(batch.TOPIC_NUMBERS.index(47), batch.TOPIC_NUMBERS.index(53))

    def test_every_new_term_is_productively_visible_in_both_variants(self) -> None:
        for topic_no, contract in batch.VOCABULARY.items():
            terms = [part.split("|", 1)[0] for part in contract["new"].split("; ") if part]
            for variant in ("accessible", "full"):
                visible = productive_english(batch.build(topic_no, variant)).casefold()
                for term in terms:
                    with self.subTest(topic=topic_no, variant=variant, term=term):
                        self.assertRegex(visible, rf"(?<![a-z0-9]){re.escape(term.casefold())}(?![a-z0-9])")

    def test_visibility_does_not_count_glossary_headwords(self) -> None:
        source = batch.build(50, "accessible")
        mutated = source.replace('<span class="s-key">comfort zone</span>', '<span class="s-key">safe range</span>', 1)
        mutated = mutated.replace("your comfort zone", "your safe range").replace("person&#x27;s comfort zone", "person&#x27;s safe range")
        self.assertIn("<b>comfort zone</b>", mutated)
        self.assertNotRegex(productive_english(mutated).casefold(), r"(?<![a-z0-9])comfort zone(?![a-z0-9])")

    def test_glosses_are_exact_short_and_declared(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in ("accessible", "full"):
                data = vocabulary.parse(batch.build(topic_no, variant))["categories"]
                declared = {entry["english"].casefold() for entries in data.values() for entry in entries}
                for row, (surface, headword, _ja) in batch.GLOSSES[topic_no][variant].items():
                    article = batch.TOPICS[topic_no]["articles"][row - 1][0 if variant == "accessible" else 1]
                    self.assertIn(surface, article)
                    self.assertIn(headword.casefold(), declared)
                    self.assertLessEqual(len(headword.split()), 3)

    def test_every_deck_passes_static_checker_complete(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in ("accessible", "full"):
                errors, warnings = check_deck.check(batch.output_path(topic_no, variant))
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(errors, [])
                    self.assertEqual(warnings, [])
        for variant, (path, _digest) in batch.PRESERVED.items():
            errors, warnings = check_deck.check(path)
            with self.subTest(topic=49, variant=variant):
                self.assertEqual(errors, [])
                self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
