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


GENERATOR = pathlib.Path(__file__).with_name("generate_ft_balance_games_batch.py")
REPO = pathlib.Path(__file__).resolve().parents[3]
TRACKS = REPO / "sandbox/drafts/en/tracks"
TOC = TRACKS / "3-freetalking/toc"
PILOTS = tuple(TRACKS / f"3-freetalking/courses/talk-between-two-countries-{v}/lessons/01-this-surprised-me/lesson.html" for v in ("accessible", "full"))
EXPECTED = {
    107: ("more-money-or-more-time", "If tomorrow came with one extra hour or fifty extra dollars, which would help more?"),
    108: ("a-hundred-friends-or-three-close-ones", "For one difficult week, would you rather have a hundred friendly contacts or three close friends?"),
    109: ("endless-summer-or-endless-winter", "If one season had to last all year, would you choose summer or winter?"),
    110: ("morning-person-or-night-owl", "For your most important tasks, would you rather start early or work late?"),
    111: ("a-planned-trip-or-a-spontaneous-one", "For a three-day trip, would you plan each day or decide as you go?"),
    112: ("travelling-alone-or-with-other-people", "For a new destination, would you rather travel alone or with someone?"),
    113: ("life-in-the-city-or-the-countryside", "For daily life, would you rather live in a busy city or a quiet town?"),
    114: ("a-summer-without-internet-or-air-conditioning", "For one summer, would you give up internet or air conditioning?"),
    115: ("better-work-life-balance-or-a-higher-salary", "For the next year, would you choose more free time or a higher income?"),
    116: ("working-from-home-or-going-into-the-office", "For focused work, would you choose home or a shared workplace?"),
    117: ("studying-in-a-cafe-or-at-home", "For two hours of serious study, would you choose a café or home?"),
    118: ("shopping-online-or-in-a-shop", "For an important purchase, would you rather buy online or in a shop?"),
    119: ("remembering-everything-or-forgetting-bad-memories", "Would you rather remember every ordinary detail or be able to forget painful memories?"),
    120: ("being-rich-and-anonymous-or-respected-on-an-ordinary-income", "Would you rather be rich and unknown or respected on an average income?"),
    121: ("being-great-at-one-thing-or-good-at-many", "Would you rather master one skill or become good at many?"),
}
PROMPT_KEYS = {"job", "title", "title_ja", "accessible", "accessible_ja", "accessible_followups", "full", "full_ja", "full_followups", "safety"}
SOURCE_DIGEST = "ef7434d019a464eaadefc31d6e08d479313c818e0996f5a16d163ffe2220c0cc"
batch = None


def load_batch():
    global batch
    if batch is None:
        name = f"{__package__}.generate_ft_balance_games_batch" if __package__ else "generate_ft_balance_games_batch"
        batch = importlib.import_module(name)
    return batch


def vocabulary_rows(raw):
    if isinstance(raw, str):
        return tuple(tuple(piece.strip() for piece in row.split("|")) for row in raw.split(";") if row.strip())
    return tuple(tuple(piece for piece in row) for row in raw)


class AAImportSafety(unittest.TestCase):
    def test_isolated_import_reads_nothing_and_loads_no_renderer(self):
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
try: m=importlib.import_module('generate_ft_balance_games_batch')
finally: builtins.open=bo; pathlib.Path.open=po; pathlib.Path.read_text=rt; pathlib.Path.read_bytes=rb
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pilots}
print(json.dumps({'calls':calls,'before':before,'after':after,'renderers':[n for n in ('new_lesson','generate_ft_me_lately_batch') if n in sys.modules],'root':hasattr(m,'ROOT')}))
'''
        result = subprocess.run([sys.executable, "-c", script, str(GENERATOR.parent), *(str(p) for p in PILOTS)], check=True, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["calls"], [])
        self.assertEqual(evidence["before"], evidence["after"])
        self.assertEqual(evidence["renderers"], [])
        self.assertFalse(evidence["root"])


class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_batch()

    def test_authoritative_toc_briefs_and_course_identity(self):
        self.assertEqual(batch.TOPIC_NUMBERS, tuple(EXPECTED))
        toc = (TRACKS / "3-freetalking/table-of-contents.md").read_text()
        for number, (slug, opening) in EXPECTED.items():
            self.assertEqual(batch.TOPICS[number]["slug"], slug)
            self.assertEqual(batch.BRIEF_OPENINGS[number], opening)
            self.assertEqual(batch.TOPICS[number]["prompts"][2]["accessible"], opening)
            self.assertIn(f'*"{opening}"*', toc)
            brief = (TOC / f"FT-{number}.md").read_text()
            self.assertIn(f'- **Opening:** "{opening}"', brief)
            self.assertIn("- **Format:** choose", brief)
        for variant, difficulty, level in (("accessible", "INTERMEDIATE", 'classLevel: "3100.109"'), ("full", "ADVANCED", 'classLevel: "3100.110"')):
            source = (TRACKS / f"3-freetalking/courses/talk-balance-games-{variant}/course.yaml").read_text()
            self.assertIn(f"difficulty: {difficulty}", source)
            self.assertIn(level, source)
            self.assertIn("enabled: false", source)

    def test_all_articles_are_aligned_independent_and_unique(self):
        accessible_seen, full_seen, claim_ids = set(), set(), []
        for number, topic in batch.TOPICS.items():
            self.assertEqual(len(topic["articles"]), 10)
            self.assertEqual(len(batch.CLAIM_ORDER[number]), 10)
            claim_ids.extend(batch.CLAIM_ORDER[number])
            for accessible, full, accessible_ja, full_ja in topic["articles"]:
                self.assertTrue(accessible.endswith("."))
                self.assertTrue(full.endswith("."))
                self.assertTrue(accessible_ja.endswith("。"))
                self.assertTrue(full_ja.endswith("。"))
                self.assertNotEqual(accessible, full)
                self.assertNotIn(accessible, accessible_seen)
                self.assertNotIn(full, full_seen)
                accessible_seen.add(accessible); full_seen.add(full)
        self.assertEqual(len(claim_ids), 150)
        self.assertEqual(len(claim_ids), len(set(claim_ids)))

    def test_prompts_are_natural_unique_answerable_and_reciprocal(self):
        banned = re.compile(r"if (?:the learner|none\b|not\b|yes\b|no\b)|general example|hypothetical case|private details|decline (?:to answer|the question)|opt out|fallback|no personal|keep .* private", re.I)
        main_questions = {variant: set() for variant in batch.VARIANTS}
        for topic_number, topic in batch.TOPICS.items():
            prompts = topic["prompts"]
            jobs = tuple(item["job"] for item in prompts)
            self.assertEqual(len(jobs), len(set(jobs)))
            self.assertEqual(jobs[-1], "tutor")
            for item in prompts:
                self.assertEqual(set(item), PROMPT_KEYS)
                for variant in batch.VARIANTS:
                    main = item[variant]
                    followups = item[f"{variant}_followups"]
                    self.assertRegex(item[f"{variant}_ja"], r"[？。]$")
                    self.assertEqual(len(followups), 2)
                    self.assertEqual(len(set(followups)), 2)
                    self.assertTrue(all(question.endswith("?") for question in followups))
                    self.assertNotRegex(" ".join((main, *followups)), banned)
                    if item["job"] != "tutor":
                        self.assertNotIn(main, main_questions[variant])
                        main_questions[variant].add(main)
            self.assertEqual(prompts[-1]["accessible"], "Ask your tutor which option they would choose and why.")
            self.assertEqual(prompts[-1]["full"], "Ask your tutor which option they would choose and why.")
            self.assertGreaterEqual(sum(item["accessible"] != item["full"] for item in prompts), 2)
        self.assertEqual({variant: len(values) for variant, values in main_questions.items()}, {variant: 105 for variant in batch.VARIANTS})

    def test_followups_are_independent_across_variants_and_topics(self):
        followups = {variant: [] for variant in batch.VARIANTS}
        for topic in batch.TOPICS.values():
            for item in topic["prompts"]:
                for variant in batch.VARIANTS:
                    followups[variant].extend(item[f"{variant}_followups"])
        for values in followups.values():
            self.assertEqual(len(values), 240)
            self.assertEqual(len(set(values)), 240)

    def test_no_generic_comparison_templates_or_technical_placeholders(self):
        boilerplate = re.compile(
            r"When is .* clearly the better choice|What does .* offer that .* cannot|"
            r"Which downside of|What do people often overlook when comparing|"
            r"At what point would you switch between|fictional memory trigger|"
            r"hypothetical financial-security band",
            re.I,
        )
        for topic in batch.TOPICS.values():
            visible = " ".join(
                [text for row in topic["articles"] for text in row]
                + [text for item in topic["prompts"] for text in (
                    item["accessible"], item["full"], item["accessible_ja"], item["full_ja"],
                    *item["accessible_followups"], *item["full_followups"],
                )]
            )
            self.assertNotRegex(visible, boilerplate)

    def test_glosses_are_selective_variant_owned_and_surface_exact(self):
        for number in batch.TOPIC_NUMBERS:
            self.assertNotEqual(batch.GLOSSES[number]["accessible"], batch.GLOSSES[number]["full"])
            declared = {english.casefold() for category in ("new", "recycled", "assumed", "receptive") for english, _japanese in vocabulary_rows(batch.VOCABULARY[number][category])}
            for variant, column in (("accessible", 0), ("full", 1)):
                self.assertLessEqual(len(batch.GLOSSES[number][variant]), 1)
                for row_number, (surface, term, _japanese) in batch.GLOSSES[number][variant].items():
                    self.assertIn(surface, batch.TOPICS[number]["articles"][row_number - 1][column])
                    self.assertIn(term.casefold(), declared)

    def test_rendered_contract_is_exactly_generated_and_reciprocal(self):
        for number in batch.TOPIC_NUMBERS:
            for variant in batch.VARIANTS:
                rendered = batch.build(number, variant)
                self.assertEqual(rendered, batch.output_path(number, variant).read_text())
                self.assertEqual(rendered.count('data-page-id="'), 13)
                self.assertEqual(rendered.count('data-claim-id="'), 10)
                self.assertEqual(rendered.count('data-fb-spoken-label="Student\'s sentence"'), 8)
                self.assertEqual(rendered.count('<meta name="podo:proofread-status" content="complete">'), 1)
                self.assertNotIn('<meta name="podo:proofread-status" content="pending">', rendered)
                self.assertRegex(rendered, r'<meta name="podo:title-ko"[^>]*>\n  <meta name="podo:title-en"[^>]*>\n  <meta name="podo:title-ja"[^>]*>\n  <meta name="podo:proofread-status" content="complete">')
                self.assertIn("Did you have any questions about the article?", rendered)
                self.assertIn("Let's follow the most interesting parts of the conversation.", rendered)
                self.assertIn("share a brief real answer or relevant perspective of your own", rendered)
                self.assertIn("Ask your tutor which option they would choose and why.", rendered)
                self.assertIn("Answer first, then follow up", rendered)
                self.assertNotRegex(rendered, r"聞いてください、")

    def test_output_routes_without_shell_reads(self):
        original = batch._render_dependencies
        calls = []
        english = pathlib.Path("/audit/sandbox/drafts/en")
        batch._render_dependencies = lambda: (calls.append(1) or object(), types.SimpleNamespace(ENGLISH=english))
        old = pathlib.Path.read_text
        pathlib.Path.read_text = lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("shell read"))
        try:
            with self.assertRaises(ValueError):
                batch.output_path(107, "bogus")
            for number, (slug, _opening) in EXPECTED.items():
                for variant in batch.VARIANTS:
                    expected = english / f"tracks/3-freetalking/courses/talk-balance-games-{variant}/lessons/{number:02d}-{slug}/lesson.html"
                    self.assertEqual(batch.output_path(number, variant), expected)
        finally:
            pathlib.Path.read_text = old
            batch._render_dependencies = original
        self.assertEqual(len(calls), 30)

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

    def test_source_digest(self):
        payload = {str(number): {"articles": topic["articles"], "prompts": topic["prompts"], "glosses": batch.GLOSSES[number]} for number, topic in batch.TOPICS.items()}
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, SOURCE_DIGEST)


if __name__ == "__main__":
    unittest.main()
