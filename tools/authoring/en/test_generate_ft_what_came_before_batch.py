from __future__ import annotations

import ast
import hashlib
import importlib.util
import pathlib
import re
import unittest


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_what_came_before_batch.py")
REPO = pathlib.Path(__file__).resolve().parents[3]
TRACK = REPO / "sandbox/drafts/en/tracks/3-freetalking"
TOC = TRACK / "toc"
VARIANTS = ("accessible", "full")

EXPECTED = {
    76: ("advice-you-kept-hearing-as-a-child", "What advice do adults often repeat to children?"),
    77: ("a-teacher-you-still-remember", "Which teacher—real or fictional—stands out to you most, and why?"),
    78: ("a-nickname-you-had-at-school", "What's the most memorable school nickname you've heard?"),
    79: ("something-you-hated-as-a-child-but-love-now", "Which food do many children dislike but learn to enjoy later?"),
    80: ("a-mistake-people-still-remind-you-about", "What kind of old mistake becomes a story people keep retelling?"),
    81: ("a-trip-that-went-wrong", "What travel problem makes the best story afterward?"),
    82: ("a-place-you-would-happily-visit-again", "Choose a place that deserves a return visit. What makes it worth going back?"),
    83: ("what-you-wanted-to-be-as-a-child", "Which childhood dream job is especially interesting to you?"),
    84: ("one-day-you-would-go-back-to", "You can visit one day in the past. Which day do you choose?"),
    85: ("a-turning-point-in-your-life", "What kind of moment can send a life in a completely different direction?"),
    86: ("what-you-were-like-as-a-child", "How can the same child seem completely different to different people?"),
    87: ("a-childhood-place-that-no-longer-exists", "Which vanished place—local, famous, or personal—would you bring back?"),
    88: ("something-you-were-completely-wrong-about", "What's a belief that many people once accepted but later proved wrong?"),
}

PROMPT_JOBS = {
    76: ("opening", "wording", "response", "reason", "hindsight", "inheritance", "nagging", "flip"),
    77: ("opening", "identity", "scene", "emotion", "learning", "hindsight", "message", "flip"),
    78: ("opening", "origin", "feeling", "meaning", "duration", "others", "boundary", "flip"),
    79: ("opening", "detail", "timing", "cause", "still-no", "reverse", "respect", "flip"),
    80: ("opening", "event", "witness", "repair", "reaction", "now", "change", "flip"),
    81: ("opening", "setting", "problem", "response", "company", "ending", "hindsight", "flip"),
    82: ("opening", "setting", "appeal", "company", "change", "plan", "risk", "flip"),
    83: ("opening", "image", "source", "change", "replacement", "connection", "hindsight", "flip"),
    84: ("opening", "setting", "purpose", "choice", "person", "message", "effect", "flip"),
    85: ("opening", "event", "awareness", "alternative", "influence", "difference", "judgment", "flip"),
    86: ("opening", "source", "agreement", "scene", "setting", "continuity", "fairness", "flip"),
    87: ("opening", "picture", "activity", "loss", "awareness", "replacement", "feeling", "flip"),
    88: ("opening", "belief", "duration", "source", "discovery", "reaction", "lesson", "flip"),
}

PROMPT_KEYS = {
    "job", "title", "title_ja", "accessible", "accessible_ja",
    "accessible_followups", "full", "full_ja", "full_followups", "safety",
}

DEFENSIVE_FALLBACK = re.compile(
    r"\b(?:if none|if no personal|if you (?:do not|have not)|family accounts are unavailable|"
    r"declin(?:e|ing)|private details|general example|imagined first visit|or can we use)\b",
    re.IGNORECASE,
)


def load_batch():
    spec = importlib.util.spec_from_file_location("ft_what_came_before", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


batch = load_batch()


def vocab_rows(number: int, category: str) -> tuple[tuple[str, ...], ...]:
    raw = batch.VOCABULARY[number][category]
    return tuple(
        tuple(piece.strip() for piece in row.split("|"))
        for row in raw.split(";") if row.strip()
    )


class SourceTests(unittest.TestCase):
    def test_authoritative_toc_briefs_and_course_routes(self):
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED))
        self.assertEqual(batch.VARIANTS, VARIANTS)
        for number, (slug, opening) in EXPECTED.items():
            brief = (TOC / f"FT-{number}.md").read_text(encoding="utf-8")
            self.assertIn(f'- **Opening:** "{opening}"', brief)
            self.assertIn(f'- **Can do:** "{opening}"', brief)
            self.assertEqual(batch.BRIEF_OPENINGS[number], opening)
            self.assertEqual(batch.TOPICS[number]["slug"], slug)
            self.assertEqual(batch.TOPICS[number]["prompts"][0]["accessible"], opening)
            for variant in VARIANTS:
                course = TRACK / f"courses/talk-what-came-before-{variant}/course.yaml"
                self.assertIn(f"slug: talk-what-came-before-{variant}", course.read_text(encoding="utf-8"))

    def test_articles_are_independently_authored_matched_pairs(self):
        all_claims = []
        for number in batch.TOPIC_NUMBERS:
            rows = batch.TOPICS[number]["articles"]
            self.assertEqual(len(rows), 10)
            for accessible, full, accessible_ja, full_ja in rows:
                all_claims.extend((accessible, full, accessible_ja, full_ja))
                self.assertTrue(accessible.endswith("."))
                self.assertTrue(full.endswith("."))
                self.assertTrue(accessible_ja.endswith("。"))
                self.assertTrue(full_ja.endswith("。"))
                self.assertNotEqual(accessible, full)
                self.assertNotEqual(accessible_ja, full_ja)
                self.assertLessEqual(len(accessible.split()), len(full.split()) + 4)
        self.assertEqual(len(all_claims), 520)
        self.assertEqual(len(all_claims), len(set(all_claims)))

    def test_prompts_are_unique_answerable_and_free_of_defensive_fallbacks(self):
        all_visible_questions = []
        for number in batch.TOPIC_NUMBERS:
            prompts = batch.TOPICS[number]["prompts"]
            self.assertEqual(tuple(item["job"] for item in prompts), PROMPT_JOBS[number])
            self.assertEqual(len(prompts), 8)
            topic_followups = {variant: [] for variant in VARIANTS}
            for item in prompts:
                self.assertEqual(set(item), PROMPT_KEYS)
                self.assertRegex(item["safety"], r"^[a-z]+(?:-[a-z]+)+$")
                self.assertNotEqual(item["accessible"], item["full"])
                self.assertNotEqual(item["accessible_ja"], item["full_ja"])
                for variant in VARIANTS:
                    main = item[variant]
                    japanese = item[f"{variant}_ja"]
                    followups = item[f"{variant}_followups"]
                    self.assertTrue(main.endswith(("?", ".")))
                    self.assertTrue(japanese.endswith(("？", "。")))
                    self.assertEqual(len(followups), 2)
                    self.assertTrue(all(question.endswith("?") for question in followups))
                    self.assertFalse(DEFENSIVE_FALLBACK.search(" ".join((main, *followups))))
                    self.assertLessEqual(len(main.replace("—", " ").split()), 22)
                    self.assertLessEqual(max(len(question.split()) for question in followups), 16)
                    all_visible_questions.append(main)
                    topic_followups[variant].extend(followups)
            for followups in topic_followups.values():
                self.assertEqual(len(followups), len(set(followups)))
        self.assertEqual(len(all_visible_questions), 208)
        self.assertEqual(len(all_visible_questions), len(set(all_visible_questions)))

    def test_openings_do_not_require_private_experience(self):
        expected_routes = {
            77: ("real or fictional",), 80: ("kind of old mistake",),
            81: ("travel problem",), 84: ("one day in the past",),
            85: ("kind of moment",), 87: ("local", "famous", "personal"),
            88: ("many people",),
        }
        for number, fragments in expected_routes.items():
            text = batch.TOPICS[number]["prompts"][0]["accessible"].casefold().replace("—", " ")
            for fragment in fragments:
                self.assertIn(fragment, text)
        combined = " ".join(batch.TOPICS[number]["prompts"][0]["accessible"] for number in batch.TOPIC_NUMBERS)
        self.assertNotRegex(combined.casefold(), r"\b(?:your mistake|your life|your family|have you been)\b")

    def test_variant_owned_glosses_are_selective_and_vocabulary_bound(self):
        empty_maps = 0
        for number in batch.TOPIC_NUMBERS:
            declared = {
                (term.casefold(), japanese)
                for category in ("new", "recycled", "assumed", "receptive")
                for term, japanese, *_owner in vocab_rows(number, category)
            }
            accessible = batch.GLOSSES[number]["accessible"]
            full = batch.GLOSSES[number]["full"]
            self.assertNotEqual(accessible, full)
            empty_maps += int(not accessible) + int(not full)
            for variant, column in (("accessible", 0), ("full", 1)):
                glosses = batch.GLOSSES[number][variant]
                self.assertLessEqual(len(glosses), 1)
                for row_number, (surface, term, japanese) in glosses.items():
                    self.assertIn((term.casefold(), japanese), declared)
                    self.assertIn(surface.casefold(), batch.TOPICS[number]["articles"][row_number - 1][column].casefold())
        self.assertGreaterEqual(empty_maps, 3)

    def test_claim_ids_and_vocabulary_ownership_are_consistent(self):
        ids = [claim for number in batch.TOPIC_NUMBERS for claim in batch.CLAIM_ORDER[number]]
        self.assertEqual(len(ids), 130)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(int(owner.split("-")[1]) <= 53 for owners in batch.REACHABLE_CORE_RETRIEVAL.values() for owner in owners))
        new_owner_count = 0
        for number in batch.TOPIC_NUMBERS:
            categories = {category: vocab_rows(number, category) for category in ("new", "recycled", "assumed", "receptive")}
            self.assertLessEqual(len(categories["new"]), 1)
            new_owner_count += len(categories["new"])
            self.assertTrue(categories["assumed"])
            self.assertTrue(categories["receptive"])
            terms = [row[0].casefold() for rows in categories.values() for row in rows]
            self.assertEqual(len(terms), len(set(terms)))
        self.assertEqual(new_owner_count, 12)

    def test_module_import_is_source_only(self):
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}

        def enclosing_function(node):
            while node in parents:
                node = parents[node]
                if isinstance(node, ast.FunctionDef):
                    return node.name
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"read_text", "read_bytes", "write_text", "mkdir", "exists", "open"}:
                self.assertIn(enclosing_function(node), {"build", "main"})

    def test_generated_decks_are_exact(self):
        for number, (slug, _opening) in EXPECTED.items():
            for variant in VARIANTS:
                path = TRACK / f"courses/talk-what-came-before-{variant}/lessons/{number:02d}-{slug}/lesson.html"
                self.assertTrue(path.exists(), path)
                self.assertEqual(path.read_text(encoding="utf-8"), batch.build(number, variant))

    def test_rendered_contract_keeps_article_prestudy_and_reciprocal_pool(self):
        for number, (slug, _opening) in EXPECTED.items():
            for variant in VARIANTS:
                source = (TRACK / f"courses/talk-what-came-before-{variant}/lessons/{number:02d}-{slug}/lesson.html").read_text(encoding="utf-8")
                self.assertEqual(source.count('data-page-id="'), 13)
                self.assertIn("Did you have any questions about the article?", source)
                self.assertIn("Use these pages as a flexible pool.", source)
                self.assertIn("share a brief real answer of your own", source)

    def test_source_digests(self):
        claims = [value for number in batch.TOPIC_NUMBERS for row in batch.TOPICS[number]["articles"] for value in row]
        prompts = [value for number in batch.TOPIC_NUMBERS for item in batch.TOPICS[number]["prompts"] for value in (item["job"], item["title"], item["title_ja"], item["accessible"], item["accessible_ja"], *item["accessible_followups"], item["full"], item["full_ja"], *item["full_followups"], item["safety"])]
        self.assertEqual(hashlib.sha256("\n".join(claims).encode()).hexdigest(), "64103ed6923554d1dce0f6bcda8e7cfb5eed03385250ce3ab88c7239d7b4554c")
        self.assertEqual(hashlib.sha256("\n".join(prompts).encode()).hexdigest(), "b983e3d59c3f79d9bea47164ed47e2763783d70cbc5bc8a95f604d68011663cb")


if __name__ == "__main__":
    unittest.main()
