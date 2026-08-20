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


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_worth_thinking_batch.py")
REPO = pathlib.Path(__file__).resolve().parents[3]
TRACKS = REPO / "sandbox/drafts/en/tracks"
TOC = TRACKS / "3-freetalking/toc"
PILOTS = tuple(
    TRACKS
    / f"3-freetalking/courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html"
    for variant in ("accessible", "full")
)
EXPECTED = {
    101: ("how-long-should-a-social-media-break-last", "How long does a social-media break need to be before it changes anything?"),
    102: ("what-ai-gets-wrong-about-human-work", "Which part of human work is easiest for AI to misunderstand?"),
    103: ("how-much-money-is-enough", "What does ‘enough money’ need to make possible?"),
    104: ("is-there-a-best-age-to-be", "Which life stage seems most attractive to freeze in time?"),
    105: ("a-decision-worth-revisiting", "Which decision from history, fiction or everyday life could have been handled differently?"),
    106: ("what-speaking-english-has-made-you-notice", "What difference between English and Japanese has become more noticeable since you started speaking English?"),
}
NEW = {
    101: ("time sink", "時間を奪うもの"),
    102: ("blind spot", "見落としやすい点"),
    103: ("financial cushion", "金銭的な余裕"),
    104: ("life stage", "人生の段階"),
    105: ("second-guess", "後になって判断を疑う"),
    106: ("word choice", "言葉の選び方"),
}
PROMPT_KEYS = {
    "job", "title", "title_ja", "accessible", "accessible_ja",
    "accessible_followups", "full", "full_ja", "full_followups", "safety",
}
PROMPT_JOBS = {
    101: ("opening", "miss", "deletion", "value", "cost", "model", "teen", "flip"),
    102: ("opening", "reason", "evidence", "strength", "blind-spot", "boundary", "future", "flip"),
    103: ("opening", "change", "same", "example", "happiness", "attention", "definition", "flip"),
    104: ("opening", "good", "bad", "now", "loss", "condition", "best", "flip"),
    105: ("opening", "alternative", "workability", "result", "tradeoff", "context", "regret", "flip"),
    106: ("opening", "notice", "direction", "people", "difficulty", "surprise", "identity", "flip"),
}
batch = None


def load_batch():
    global batch
    if batch is None:
        name = f"{__package__}.generate_ft_worth_thinking_batch" if __package__ else "generate_ft_worth_thinking_batch"
        batch = importlib.import_module(name)
    return batch


def vocab_rows(number, category):
    raw = load_batch().VOCABULARY[number][category]
    return tuple(tuple(piece.strip() for piece in row.split("|")) for row in raw.split(";") if row.strip())


class AAImportSafety(unittest.TestCase):
    def test_isolated_import_has_no_filesystem_or_pilot_dependency(self):
        self.assertIsNone(batch)
        script = r'''
import builtins,hashlib,importlib,json,pathlib,sys
folder=pathlib.Path(sys.argv[1]); pilots=[pathlib.Path(p) for p in sys.argv[2:]]
sys.path.insert(0,str(folder)); before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pilots}
calls=[]; bo=builtins.open; po=pathlib.Path.open; rt=pathlib.Path.read_text; rb=pathlib.Path.read_bytes
def blocked(name):
 def f(*a,**k): calls.append(name); raise AssertionError(name)
 return f
builtins.open=blocked('open'); pathlib.Path.open=blocked('Path.open'); pathlib.Path.read_text=blocked('read_text'); pathlib.Path.read_bytes=blocked('read_bytes')
try: m=importlib.import_module('generate_ft_worth_thinking_batch')
finally: builtins.open=bo; pathlib.Path.open=po; pathlib.Path.read_text=rt; pathlib.Path.read_bytes=rb
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pilots}
print(json.dumps({'calls':calls,'before':before,'after':after,'renderers':[n for n in ('new_lesson','generate_ft_me_lately_batch') if n in sys.modules],'root':hasattr(m,'ROOT')}))
'''
        result = subprocess.run(
            [sys.executable, "-c", script, str(GENERATOR.parent), *(str(p) for p in PILOTS)],
            check=True, capture_output=True, text=True,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["calls"], [])
        self.assertEqual(evidence["before"], evidence["after"])
        self.assertEqual(evidence["renderers"], [])
        self.assertFalse(evidence["root"])


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_batch()

    def test_authoritative_briefs_courses_retrieval_and_identity(self):
        self.assertEqual(batch.COURSE, "talk-worth-thinking-about")
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED))
        self.assertTrue(batch.TOC_RETRIEVAL_AUDIT_ONLY)
        for number, (slug, opening) in EXPECTED.items():
            brief = (TOC / f"FT-{number}.md").read_text()
            self.assertIn(f'# FT-{number} · {batch.TOPICS[number]["title"]}', brief)
            self.assertIn(f'- **Opening:** "{opening}"', brief)
            self.assertIn("- **Format:** opinion", brief)
            self.assertIn(batch.SHARED_SOURCE[number], brief)
            self.assertEqual(batch.BRIEF_OPENINGS[number], opening)
            self.assertEqual(batch.TOPICS[number]["slug"], slug)
            self.assertEqual(batch.TOPICS[number]["prompts"][0]["accessible"], opening)
        for variant, difficulty, level in (
            ("accessible", "INTERMEDIATE", 'classLevel: "3100.099"'),
            ("full", "ADVANCED", 'classLevel: "3100.100"'),
        ):
            source = (TRACKS / f"3-freetalking/courses/talk-worth-thinking-about-{variant}/course.yaml").read_text()
            self.assertIn(f"difficulty: {difficulty}", source)
            self.assertIn(level, source)
            self.assertIn("enabled: false", source)

    def test_articles_are_independently_authored_aligned_claim_pairs(self):
        seen_accessible = set()
        seen_full = set()
        for number, topic in batch.TOPICS.items():
            self.assertEqual(len(topic["articles"]), 10, number)
            for accessible, full, accessible_ja, full_ja in topic["articles"]:
                self.assertTrue(accessible.endswith("."))
                self.assertTrue(full.endswith("."))
                self.assertTrue(accessible_ja.endswith("。"))
                self.assertTrue(full_ja.endswith("。"))
                self.assertNotEqual(accessible, full)
                self.assertNotEqual(accessible_ja, full_ja)
                self.assertNotIn(accessible, seen_accessible)
                self.assertNotIn(full, seen_full)
                seen_accessible.add(accessible)
                seen_full.add(full)
        self.assertEqual(len(seen_accessible), 60)
        self.assertEqual(len(seen_full), 60)

    def test_prompts_are_unique_standalone_and_not_defensive_branches(self):
        all_main = set()
        banned = re.compile(
            r"if (?:you|the learner|none|not|yes|no)|general example|hypothetical case|"
            r"private details|decline|opt out|fallback|or none|no change yet",
            re.I,
        )
        for number, topic in batch.TOPICS.items():
            prompts = topic["prompts"]
            self.assertEqual(len(prompts), 8)
            self.assertEqual(tuple(item["job"] for item in prompts), PROMPT_JOBS[number])
            for item in prompts:
                self.assertEqual(set(item), PROMPT_KEYS)
                self.assertRegex(item["safety"], r"^[a-z]+(?:-[a-z]+)+$")
                self.assertNotEqual(item["accessible"], item["full"])
                self.assertNotEqual(item["accessible_ja"], item["full_ja"])
                for variant in batch.VARIANTS:
                    main = item[variant]
                    followups = item[f"{variant}_followups"]
                    self.assertTrue(main.endswith("?"), (number, variant, main))
                    self.assertEqual(len(followups), 2)
                    self.assertEqual(len(set(followups)), 2)
                    self.assertTrue(all(question.endswith("?") for question in followups))
                    self.assertNotRegex(" ".join((main, *followups)), banned)
                    self.assertNotIn(main, all_main)
                    all_main.add(main)
        self.assertEqual(len(all_main), 96)

    def test_glosses_are_selective_variant_owned_and_surface_exact(self):
        for number in batch.TOPIC_NUMBERS:
            accessible = batch.GLOSSES[number]["accessible"]
            full = batch.GLOSSES[number]["full"]
            self.assertNotEqual(accessible, full)
            self.assertLessEqual(len(accessible), 1)
            self.assertLessEqual(len(full), 1)
            declared = {
                english.casefold()
                for category in ("new", "recycled", "assumed", "receptive")
                for english, _japanese in vocab_rows(number, category)
            }
            for variant, column in (("accessible", 0), ("full", 1)):
                for row_number, (surface, term, _japanese) in batch.GLOSSES[number][variant].items():
                    self.assertIn(surface, batch.TOPICS[number]["articles"][row_number - 1][column])
                    self.assertIn(term.casefold(), declared)

    def test_claim_ids_vocabulary_and_entry_floor_are_explicit(self):
        ids = [claim for number in batch.TOPIC_NUMBERS for claim in batch.CLAIM_ORDER[number]]
        self.assertEqual(len(ids), 60)
        self.assertEqual(len(ids), len(set(ids)))
        for number in batch.TOPIC_NUMBERS:
            self.assertEqual(vocab_rows(number, "new"), (NEW[number],))
            visible = " ".join(value for row in batch.TOPICS[number]["articles"] for value in row[:2])
            self.assertRegex(visible, re.compile(re.escape(NEW[number][0]), re.I))
        self.assertTrue(all(int(owner.split("-")[1]) <= 53 for owners in batch.REACHABLE_CORE_RETRIEVAL.values() for owner in owners))

    def test_rendered_contract_is_reciprocal_and_exactly_generated(self):
        for number in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                rendered = batch.build(number, variant)
                self.assertEqual(rendered, batch.output_path(number, variant).read_text())
                self.assertEqual(rendered.count('data-page-id="'), 13)
                self.assertIn('data-page-id="article"', rendered)
                self.assertEqual(rendered.count('data-claim-id="'), 10)
                self.assertIn("Did you have any questions about the article?", rendered)
                self.assertNotIn("Read the article", rendered)
                self.assertIn("Let's follow the most interesting parts of the conversation.", rendered)
                self.assertIn("share a brief real answer or relevant perspective of your own", rendered)
                self.assertIn("Skip freely", rendered)
                self.assertEqual(rendered.count('data-fb-spoken-label="Student\'s sentence"'), 8)

    def test_output_routes_without_shell_reads(self):
        original = batch._render_dependencies
        calls = []
        english = pathlib.Path("/audit/sandbox/drafts/en")
        batch._render_dependencies = lambda: (calls.append(1) or object(), types.SimpleNamespace(ENGLISH=english))
        old = pathlib.Path.read_text
        pathlib.Path.read_text = lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("shell read"))
        try:
            with self.assertRaises(ValueError):
                batch.output_path(101, "bogus")
            for number, (slug, _opening) in EXPECTED.items():
                for variant in batch.VARIANTS:
                    expected = english / f"tracks/3-freetalking/courses/talk-worth-thinking-about-{variant}/lessons/{number:02d}-{slug}/lesson.html"
                    self.assertEqual(batch.output_path(number, variant), expected)
        finally:
            pathlib.Path.read_text = old
            batch._render_dependencies = original
        self.assertEqual(len(calls), 12)

    def test_module_io_is_lazy(self):
        tree = ast.parse(GENERATOR.read_text())
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

    def test_source_digests(self):
        claims = [value for number in batch.TOPIC_NUMBERS for row in batch.TOPICS[number]["articles"] for value in row]
        prompts = [
            value
            for number in batch.TOPIC_NUMBERS
            for item in batch.TOPICS[number]["prompts"]
            for value in (
                item["job"], item["title"], item["title_ja"], item["accessible"],
                item["accessible_ja"], *item["accessible_followups"], item["full"],
                item["full_ja"], *item["full_followups"], item["safety"],
            )
        ]
        self.assertEqual(hashlib.sha256("\n".join(claims).encode()).hexdigest(), "ae3e7ab485e78153f149a839be14c056d457518d829316c8c2b931033a4b345f")
        self.assertEqual(hashlib.sha256("\n".join(prompts).encode()).hexdigest(), "17236baa905b5c19ac19a2332b0630be3fd2a87dd2626ad57c9d18fda4683e81")


if __name__ == "__main__":
    unittest.main()
