from __future__ import annotations

import ast
import importlib
import json
import pathlib
import re
import unittest


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_work_and_money_batch.py")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
TRACK = REPO_ROOT / "sandbox/drafts/en/tracks/3-freetalking"
TOC_ROOT = TRACK / "toc"
REVIEW_ROOT = REPO_ROOT / "sandbox/drafts/en/page-reviews"

EXPECTED_TOPICS = {
    64: ("what-you-did-with-your-first-paycheck", "What you did with your first paycheck"),
    65: ("something-you-were-proud-to-finish", "Something you were proud to finish"),
    66: ("a-moment-when-you-felt-successful", "A moment when you felt successful"),
    67: ("something-youre-trying-to-get-better-at", "Something you're trying to get better at"),
    68: ("what-you-do-with-money-you-dont-spend", "What you do with money you don't spend"),
    69: ("a-different-career-you-might-have-chosen", "A different career you might have chosen"),
    70: ("how-ai-has-changed-your-work", "How AI has changed your work"),
    71: ("a-time-you-seriously-considered-changing-careers", "A time you seriously considered changing careers"),
    72: ("someone-you-learned-a-lot-from", "Someone you learned a lot from"),
    73: ("what-a-normal-work-or-school-day-looks-like-where-you-live", "What a normal work or school day looks like where you live"),
    74: ("what-your-workday-actually-looks-like", "What your workday actually looks like"),
    75: ("one-thing-you-would-change-about-your-work-or-school", "One thing you would change about your work or school"),
}

EXPECTED_OPENINGS = {
    64: "What are some memorable ways people use their first paycheck?",
    65: "Which feels better: finishing a long job or fixing a small annoying problem?",
    66: "Which small success feels best: arriving on time, cooking well, or finishing a task?",
    67: "What skill would you most like to improve?",
    68: "Besides spending it, what can people do with money?",
    69: "Which career would you be curious to try for one year?",
    70: "Which everyday task has AI changed the most?",
    71: "What makes someone seriously consider changing careers?",
    72: "What makes a manager, teacher, or coach worth learning from?",
    73: "What time do people usually finish work or school where you live?",
    74: "Choose any recent two-hour period. What filled that time?",
    75: "What would you change about a place where people work or study?",
}

EXPECTED_PAGE_IDS = (
    "lesson-goal", "article", "lesson-style", "talk-intro", "warm-1", "warm-2",
    "q1", "q2", "q3", "q4", "q5", "q6", "feedback",
)

BANNED_ROUTE_LANGUAGE = re.compile(
    r"\b(?:if yes|if not|if someone|if nobody|if none|for a real|for a general|"
    r"real or|familiar or|hypothetical|imagined|general example|you may|"
    r"is enough|equally valid|is welcome|answer generally)\b",
    re.IGNORECASE,
)


def _module_name() -> str:
    if __package__:
        return f"{__package__}.generate_ft_work_and_money_batch"
    return "generate_ft_work_and_money_batch"


batch = importlib.import_module(_module_name())


class WorkAndMoneySourceTests(unittest.TestCase):
    def test_exact_inventory_and_authoritative_briefs(self) -> None:
        self.assertEqual(batch.COURSE, "talk-work-and-money")
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED_TOPICS))
        self.assertEqual(tuple(batch.TOPICS), batch.TOPIC_NUMBERS)
        self.assertEqual(batch.BRIEF_OPENINGS, EXPECTED_OPENINGS)
        for topic_no, (slug, title) in EXPECTED_TOPICS.items():
            with self.subTest(topic=topic_no):
                self.assertEqual(batch.TOPICS[topic_no]["slug"], slug)
                self.assertEqual(batch.TOPICS[topic_no]["title"], title)
                brief = (TOC_ROOT / f"FT-{topic_no}.md").read_text(encoding="utf-8")
                self.assertIn(f"# FT-{topic_no} · {title}", brief)
                self.assertIn(f'- **Opening:** "{EXPECTED_OPENINGS[topic_no]}"', brief)
                self.assertIn("The track TOC is authoritative.", brief)

    def test_goals_are_simple_positive_can_dos(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            en, ja = topic["goal"]
            with self.subTest(topic=topic_no):
                self.assertTrue(en.startswith("Let's "))
                self.assertLessEqual(len(en), 82)
                self.assertRegex(ja, r"[ぁ-んァ-ヶ一-龠]")
                self.assertIsNone(BANNED_ROUTE_LANGUAGE.search(en))
                self.assertNotRegex(en.casefold(), r"\bwithout\b|\bdo not\b|\bno-use\b")

    def test_articles_are_complete_bilingual_and_variant_authored(self) -> None:
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

    def test_ft74_article_title_is_mobile_concise(self) -> None:
        self.assertEqual(
            batch.TOPICS[74]["article_title"],
            ("The work behind the results", "結果を支える仕事"),
        )
        self.assertLessEqual(len(batch.TOPICS[74]["article_title"][0]), 32)
        self.assertLessEqual(len(batch.TOPICS[74]["article_title"][1]), 14)

    def test_ft74_effective_output_omits_stale_routing_copy(self) -> None:
        stale_literals = (
            "If nine to eleven was not a work period",
            "A different two-hour period, a familiar case, or a general example",
            "If that time does not fit",
            "or a familiar example",
            "If it changed",
            "If it stayed",
        )
        for variant in batch.VARIANTS:
            rendered = batch.build(74, variant)
            with self.subTest(variant=variant):
                for literal in stale_literals:
                    self.assertNotIn(literal, rendered)

    def test_glosses_are_selective_variant_owned_and_case_exact(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            vocabulary = {
                english.casefold()
                for rows in batch.VOCABULARY[topic_no].values()
                for english, _japanese in rows
            }
            for variant in batch.VARIANTS:
                col = 0 if variant == "accessible" else 1
                glosses = batch.GLOSSES[topic_no][variant]
                self.assertGreaterEqual(len(glosses), 1)
                self.assertLessEqual(len(glosses), 2)
                for row_no, (surface, headword, japanese) in glosses.items():
                    with self.subTest(topic=topic_no, variant=variant, row=row_no):
                        self.assertIn(surface, topic["articles"][row_no - 1][col])
                        self.assertEqual(
                            sum(surface in row[col] for row in topic["articles"]), 1
                        )
                        self.assertIn(headword.casefold(), vocabulary)
                        self.assertRegex(japanese, r"[ぁ-んァ-ヶ一-龠]")

    def test_prompt_pool_is_globally_unique_and_free_of_defensive_routes(self) -> None:
        mains: list[str] = []
        followups: list[str] = []
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
                        self.assertTrue(all(len(value) <= 150 for value in probes))
                        mains.append(main.casefold())
                        followups.extend(value.casefold() for value in probes)
        self.assertEqual(len(mains), 192)
        self.assertEqual(len(mains), len(set(mains)))
        self.assertEqual(len(followups), 384)
        self.assertEqual(len(followups), len(set(followups)))

    def test_accessible_and_full_are_paired_but_not_copied(self) -> None:
        for topic_no, topic in batch.TOPICS.items():
            for prompt_no, item in enumerate(topic["prompts"], 1):
                with self.subTest(topic=topic_no, prompt=prompt_no):
                    self.assertNotEqual(item["accessible"], item["full"])
                    self.assertNotEqual(item["accessible_ja"], item["full_ja"])
                    self.assertEqual(
                        len(item["accessible_followups"]),
                        len(item["full_followups"]),
                    )

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


class WorkAndMoneyRenderedTests(unittest.TestCase):
    def test_output_paths_are_exact_and_distinct(self) -> None:
        paths = [
            batch.output_path(topic_no, variant)
            for topic_no in batch.TOPIC_NUMBERS
            for variant in batch.VARIANTS
        ]
        self.assertEqual(len(paths), 24)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all("talk-work-and-money-" in path.as_posix() for path in paths))
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
                    self.assertNotRegex(source, r"\bIf yes\b|\bIf not\b")

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
                    self.assertEqual(review["stages"]["ownerApproval"], "pending")
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
