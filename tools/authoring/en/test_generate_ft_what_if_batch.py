from __future__ import annotations

import ast
import importlib
import json
import pathlib
import re
import unittest


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_what_if_batch.py")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
TRACK = REPO_ROOT / "sandbox/drafts/en/tracks/3-freetalking"
TOC_ROOT = TRACK / "toc"
REVIEW_ROOT = REPO_ROOT / "sandbox/drafts/en/page-reviews"

EXPECTED_TOPICS = {
    89: ("what-you-would-really-do-if-you-won-the-lottery", "What you would really do if you won the lottery"),
    90: ("three-things-you-would-take-to-a-desert-island", "Three things you would take to a desert island"),
    91: ("someone-you-would-trade-lives-with-for-a-day", "Someone you would trade lives with for a day"),
    92: ("the-superpower-you-would-choose", "The superpower you would choose"),
    93: ("the-one-food-you-could-eat-forever", "The one food you could eat forever"),
    94: ("one-thing-you-would-make-free-forever", "One thing you would make free forever"),
    95: ("going-a-week-without-your-phone", "Going a week without your phone"),
    96: ("what-you-would-do-if-ai-did-your-job", "What you would do if AI did your job"),
    97: ("the-animal-your-friends-would-choose-for-you", "The animal your friends would choose for you"),
    98: ("growing-up-in-another-country", "Growing up in another country"),
    99: ("where-you-imagine-yourself-in-ten-years", "Where you imagine yourself in ten years"),
    100: ("the-one-thing-you-would-save-in-a-fire", "The one thing you would save in a fire"),
}

EXPECTED_OPENINGS = {
    89: "Imagine you win a large lottery prize tomorrow. What would you do first?",
    90: "What would feel hardest about your first day on a desert island?",
    91: "Whose daily life would you be curious to experience for one day?",
    92: "Which superpower would make ordinary life most interesting?",
    93: "Which food would be hardest for you to get tired of?",
    94: "If one everyday service were free for life, which would you choose?",
    95: "Which phone feature would you miss most for one week?",
    96: "If AI handled your usual tasks for a week, what would you do with the extra time?",
    97: "Which animal best represents your personality?",
    98: "If you had grown up in another country, which one would you choose?",
    99: "What would an ideal ordinary day look like ten years from now?",
    100: "Once everyone is safe, which possession would be hardest to lose?",
}

EXPECTED_LADDERS = {
    89: "first decision → guiding priority → disclosure and privacy → meaningful routines → first purchase → possible regret → a new normal → what money cannot solve",
    90: "hardest first-day problem → three useful objects → most important need → final-place trade-off → emotional value → regretted omission → missing island facts → one companion → value after returning",
    91: "one life or role → what makes it instructive → first hour → question it could answer → hidden difficulty → shareable insight → valuing ordinary life → what someone might learn from yours",
    92: "interesting power → responsible first use → secrecy → decisive downside → power to refuse → popular power → governing rule → ordinary skill with greater value",
    93: "durable choice → effect of repetition → two close rivals → missing variety → easy food to give up → nutrition versus enjoyment → revision interval → why variety matters",
    94: "lifetime service → use threshold → ordinary week → benefit to others → sensible boring choice → fair resale rules → hidden costs → value worth paying for",
    95: "hardest part → disrupted routine → hardest function to replace → possible improvement → best time for a break → safe support → essential function → habit worth redesigning",
    96: "first use of time → three unstructured months → disclosure → role function that remains → self-chosen project → identity → tasks people still choose → work that should stay human",
    97: "one animal metaphor → trait it cannot capture → accept or reject the comparison → self-image and observer gap → inaccurate animal → context changes → classify the tutor's real traits → why one metaphor is incomplete",
    98: "contrasting upbringing → concrete condition → identity → what would be missed → what might not be missed → language and belonging → childhood versus adult migration → what might remain stable",
    99: "ideal ordinary day → organizing purpose → company and solitude → continuity → missing value → broader direction → small test this year → new evidence that could change the plan",
    100: "irreplaceable possession → source of value → unexpected category → another person's choice → ordinary object and memory → what loss teaches → preparation before danger → value beyond objects",
}

EXPECTED_PAGE_IDS = (
    "lesson-goal", "article", "lesson-style", "talk-intro", "warm-1", "warm-2",
    "q1", "q2", "q3", "q4", "q5", "q6", "feedback",
)

BANNED_ROUTE_LANGUAGE = re.compile(
    r"\b(?:if yes|if not|if no|if none|if nobody|if someone|if one exists|"
    r"if there is one|no .{0,30} comes? (?:quickly|to mind)|selected answer|"
    r"current answer|previous answer|answer generally|is enough|equally valid)\b",
    re.IGNORECASE,
)


def _module_name() -> str:
    if __package__:
        return f"{__package__}.generate_ft_what_if_batch"
    return "generate_ft_what_if_batch"


batch = importlib.import_module(_module_name())


class WhatIfSourceTests(unittest.TestCase):
    def test_exact_inventory_and_authoritative_briefs(self) -> None:
        self.assertEqual(batch.COURSE, "talk-what-if")
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED_TOPICS))
        self.assertEqual(tuple(batch.TOPICS), batch.TOPIC_NUMBERS)
        self.assertEqual(batch.BRIEF_OPENINGS, EXPECTED_OPENINGS)
        for topic_no, (slug, title) in EXPECTED_TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(batch.TOPICS[topic_no]["slug"], slug)
                self.assertEqual(batch.TOPICS[topic_no]["title"], title)
                self.assertEqual(batch.TOPICS[topic_no]["prompts"][0]["accessible"], EXPECTED_OPENINGS[topic_no])
                brief = (TOC_ROOT / f"FT-{topic_no}.md").read_text(encoding="utf-8")
                self.assertIn(f"# FT-{topic_no} · {title}", brief)
                self.assertIn(f'- **Opening:** "{EXPECTED_OPENINGS[topic_no]}"', brief)
                self.assertIn(f"- **Question ladder:** {EXPECTED_LADDERS[topic_no]}", brief)
                self.assertIn("The track TOC is authoritative.", brief)

    def test_goals_are_simple_positive_can_dos(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            en, ja = topic["goal"]
            with self.subTest(topic=topic_no):
                self.assertTrue(en.startswith("Let's "))
                self.assertLessEqual(len(en), 86)
                self.assertRegex(ja, r"[ぁ-んァ-ヶ一-龠]")
                self.assertIsNone(BANNED_ROUTE_LANGUAGE.search(en))
                self.assertNotRegex(en.casefold(), r"\bdo not\b|\bno answer\b|\bwithout requiring\b")

    def test_articles_are_complete_bilingual_and_independently_authored(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            self.assertEqual(len(topic["articles"]), 10)
            self.assertEqual(
                batch.CLAIM_ORDER[topic_no],
                tuple(f"ft{topic_no}-c{index:02d}" for index in range(1, 11)),
            )
            for index, row in enumerate(topic["articles"], 1):
                with self.subTest(topic=topic_no, row=index):
                    self.assertEqual(len(row), 4)
                    self.assertTrue(all(value.strip() for value in row))
                    self.assertNotEqual(row[0], row[1])
                    self.assertNotEqual(row[2], row[3])
                    self.assertRegex(row[2] + row[3], r"[ぁ-んァ-ヶ一-龠]")
                    self.assertNotRegex(
                        row[0] + row[1],
                        r"\b(?:the learner|a learner) (?:can|may) (?:discuss|examine|use)\b",
                    )

    def test_glosses_are_selective_variant_owned_and_case_exact(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            vocabulary = {
                part.split("|", 1)[0].strip().casefold()
                for rows in batch.VOCABULARY[topic_no].values()
                for part in rows.split(";")
                if part.strip()
            }
            for variant in batch.VARIANTS:
                col = 0 if variant == "accessible" else 1
                glosses = batch.GLOSSES[topic_no][variant]
                self.assertGreaterEqual(len(glosses), 1)
                self.assertLessEqual(len(glosses), 2)
                for row_no, (surface, headword, japanese) in glosses.items():
                    with self.subTest(topic=topic_no, variant=variant, row=row_no):
                        self.assertIn(surface, topic["articles"][row_no - 1][col])
                        self.assertEqual(sum(surface in row[col] for row in topic["articles"]), 1)
                        self.assertIn(headword.casefold(), vocabulary)
                        self.assertRegex(japanese, r"[ぁ-んァ-ヶ一-龠]")

    def test_prompt_pool_is_globally_unique_and_free_of_defensive_routes(self) -> None:
        mains: dict[str, list[str]] = {variant: [] for variant in batch.VARIANTS}
        followups: dict[str, list[str]] = {variant: [] for variant in batch.VARIANTS}
        for topic_no, topic in batch.TOPICS.items():
            self.assertEqual(len(topic["prompts"]), 8)
            jobs = [item["job"] for item in topic["prompts"]]
            self.assertEqual(len(jobs), len(set(jobs)))
            for prompt_no, item in enumerate(topic["prompts"], 1):
                for variant in batch.VARIANTS:
                    main = item[variant]
                    probes = item[f"{variant}_followups"]
                    with self.subTest(topic=topic_no, prompt=prompt_no, variant=variant):
                        self.assertTrue(main.endswith("?"))
                        self.assertEqual(len(probes), 2)
                        self.assertTrue(all(value.endswith("?") for value in probes))
                        self.assertIsNone(BANNED_ROUTE_LANGUAGE.search(main))
                        self.assertTrue(all(BANNED_ROUTE_LANGUAGE.search(value) is None for value in probes))
                        self.assertNotRegex(main, r"^(?:And|What about|How about|Why that|When was that|Who was that)\b")
                        self.assertLessEqual(len(main), 180)
                        self.assertTrue(all(len(value) <= 160 for value in probes))
                        mains[variant].append(main.casefold())
                        followups[variant].extend(value.casefold() for value in probes)
        for values in mains.values():
            self.assertEqual((len(values), len(set(values))), (96, 96))
        for values in followups.values():
            self.assertEqual((len(values), len(set(values))), (192, 192))

    def test_accessible_and_full_are_paired_but_not_copied(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            different = 0
            for prompt_no, item in enumerate(topic["prompts"], 1):
                with self.subTest(topic=topic_no, prompt=prompt_no):
                    different += item["accessible"] != item["full"]
                    self.assertEqual(
                        item["accessible"] != item["full"],
                        item["accessible_ja"] != item["full_ja"],
                    )
                    self.assertEqual(len(item["accessible_followups"]), len(item["full_followups"]))
            self.assertGreaterEqual(different, 2)

    def test_import_keeps_renderer_and_filesystem_lazy(self) -> None:
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent

        def enclosing(node: ast.AST) -> str | None:
            while node in parents:
                node = parents[node]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return node.name
            return None

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported = {alias.name for alias in node.names}
                if imported & {"new_lesson", "generate_ft_me_lately_batch"}:
                    self.assertEqual(enclosing(node), "_render_dependencies")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"read_text", "write_text", "mkdir", "exists"}:
                    self.assertIn(enclosing(node), {"build", "main"})


class WhatIfRenderedTests(unittest.TestCase):
    def test_output_paths_are_exact_and_distinct(self) -> None:
        paths = [
            batch.output_path(topic_no, variant)
            for topic_no in batch.TOPIC_NUMBERS
            for variant in batch.VARIANTS
        ]
        self.assertEqual(len(paths), 24)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all("talk-what-if-" in path.as_posix() for path in paths))
        self.assertTrue(all("/lessons/" in path.as_posix() for path in paths))

    def test_checked_in_decks_equal_exact_generator_output(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                path = batch.output_path(topic_no, variant)
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertTrue(path.is_file())
                    self.assertEqual(path.read_text(encoding="utf-8"), batch.build(topic_no, variant))

    def test_rendered_shell_has_one_job_per_page_and_reciprocal_pool(self) -> None:
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                source = batch.output_path(topic_no, variant).read_text(encoding="utf-8")
                page_ids = tuple(re.findall(r'data-page-id="([^"]+)"', source))
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(page_ids, EXPECTED_PAGE_IDS)
                    self.assertIn('content="2026-08-21"', source)
                    self.assertEqual(source.count('<meta name="podo:proofread-status" content="complete">'), 1)
                    self.assertNotIn('<meta name="podo:proofread-status" content="pending">', source)
                    self.assertIn("Treat these pages as a pool, not a sequence.", source)
                    self.assertIn("React or share briefly before choosing the next prompt", source)
                    self.assertEqual(source.count("Student's sentence"), 8)
                    self.assertNotRegex(source, r"\bIf yes\b|\bIf not\b|\bIf no\b")

    def test_hash_bound_ledgers_cover_exact_pages_and_prompt_evidence(self) -> None:
        page_review = importlib.import_module(
            f"{__package__}.page_review" if __package__ else "page_review"
        )
        for topic_no in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                lesson = batch.output_path(topic_no, variant)
                review_path = REVIEW_ROOT / f"FT-{topic_no}-{variant}.page-review.json"
                markdown_path = review_path.with_suffix(".md")
                review = json.loads(review_path.read_text(encoding="utf-8"))
                with self.subTest(topic=topic_no, variant=variant):
                    self.assertEqual(review["lessonSha256"], page_review.sha256(lesson))
                    self.assertEqual(
                        [page["pageId"] for page in review["pages"]],
                        page_review.page_ids(lesson),
                    )
                    self.assertEqual(review["stages"]["generated"], "pass")
                    self.assertEqual(review["stages"]["mechanicalValidation"], "pass")
                    self.assertEqual(review["stages"]["humanPageAudit"], "pass")
                    self.assertEqual(review["stages"]["ownerApproval"], "pass")
                    self.assertTrue(all(page["verdict"] == "pass" for page in review["pages"]))
                    self.assertTrue(all(page["visual360"] == page["visual480"] for page in review["pages"]))
                    self.assertTrue(all(page["visual360"] in {"pending", "pass"} for page in review["pages"]))
                    self.assertEqual(markdown_path.read_text(encoding="utf-8"), page_review.markdown(review))
                    expected = [item[variant] for item in batch.TOPICS[topic_no]["prompts"]]
                    self.assertEqual(
                        [page["evidence"]["substantivePrompts"][0] for page in review["pages"][4:12]],
                        expected,
                    )


if __name__ == "__main__":
    unittest.main()
