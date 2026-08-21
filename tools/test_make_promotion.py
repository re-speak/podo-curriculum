from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest

import yaml


TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

SPEC = importlib.util.spec_from_file_location("make_promotion",
                                              TOOLS / "make-promotion.py")
assert SPEC and SPEC.loader
mk = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mk
SPEC.loader.exec_module(mk)


HEAD = (
    '<meta name="podo:title-ko" content="아홉 시에 일을 시작해요">\n'
    '<meta name="podo:title-en" content="I start work at nine">\n'
    '<meta name="podo:title-ja" content="9時に仕事を始めます">\n'
)
BODY = (
    '<link rel="stylesheet" href="../../shared/css/lesson-card.css">\n'
    '<input class="space-input" data-sync-id="a" data-answer="nine">\n'
    '<script src="../../shared/js/activities.js"></script>\n'
)
DECK = HEAD + BODY


class TitleTests(unittest.TestCase):
    """Titles are read, never invented — the whole point of deriving the manifest."""

    def test_reads_all_three(self):
        got = mk.titles(DECK, pathlib.Path("d.html"))
        self.assertEqual(got, {"ko": "아홉 시에 일을 시작해요",
                               "en": "I start work at nine",
                               "ja": "9時に仕事を始めます"})

    def test_names_the_missing_language_rather_than_guessing(self):
        raw = DECK.replace('<meta name="podo:title-ja" content="9時に仕事を始めます">\n', "")
        with self.assertRaisesRegex(mk.MakeFailed, "podo:title-ja"):
            mk.titles(raw, pathlib.Path("d.html"))

    def test_empty_content_is_as_missing_as_no_tag(self):
        raw = DECK.replace('content="I start work at nine"', 'content="  "')
        with self.assertRaisesRegex(mk.MakeFailed, "podo:title-en"):
            mk.titles(raw, pathlib.Path("d.html"))

    def test_survives_reordered_attributes(self):
        raw = '<meta content="X" name="podo:title-en">'
        self.assertEqual(mk.TITLE_RE["en"].search(raw).group(1), "X")

    def test_unescapes_entities(self):
        raw = DECK.replace('content="I start work at nine"',
                           'content="Refills &amp; extras"')
        self.assertEqual(mk.titles(raw, pathlib.Path("d.html"))["en"],
                         "Refills & extras")


class OrderTests(unittest.TestCase):
    """Lexicographic order hands week 11 to the wrong deck once lessons pass 100.

    courses/kr/core-upper-intermediate-1 runs 90..101, so this is the live case
    rather than a hypothetical one.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / "a-course"
        (self.root / "lessons").mkdir(parents=True)
        (self.root / "course.yaml").write_text(
            "spec:\n  enabled: false\n", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def deck(self, slug: str) -> None:
        d = self.root / "lessons" / slug
        d.mkdir()
        (d / "lesson.html").write_text(DECK, encoding="utf-8")

    def draft(self) -> mk.Draft:
        draft = mk.Draft.__new__(mk.Draft)
        draft.path = self.root
        draft.rel = "a-course"
        draft.lessons_dir = self.root / "lessons"
        return draft

    def test_orders_numerically_not_lexicographically(self):
        for slug in ("90-surely-cold-outside", "100-far-from-it", "91-i-tried-it"):
            self.deck(slug)
        self.assertEqual([s for s, _ in self.draft().decks()],
                         ["90-surely-cold-outside", "91-i-tried-it", "100-far-from-it"])

    def test_ignores_a_planned_lesson_with_no_deck_yet(self):
        self.deck("01-one")
        (self.root / "lessons" / "02-not-written-yet").mkdir()
        self.assertEqual([s for s, _ in self.draft().decks()], ["01-one"])

    def test_rejects_a_directory_name_the_schema_would_refuse(self):
        self.deck("Not_A_Slug")
        with self.assertRaisesRegex(mk.MakeFailed, "NN-english-words"):
            self.draft().decks()


class AuditTests(unittest.TestCase):
    """promote.py's own checks, run at manifest time so a bad deck fails early."""

    def test_rejects_a_sync_id_that_resolves_to_no_kind(self):
        raw = DECK + '<span data-sync-id="silent">x</span>'
        with self.assertRaisesRegex(mk.MakeFailed, "resolve to no kind"):
            mk.audit(raw, pathlib.Path("d.html"), (mk.promote.SHARED_ASSETS,))

    def test_rejects_a_runtime_promoted_shell(self):
        # A kind of its own, so it clears resolve_kinds and reaches flatten's check.
        raw = DECK + '<span class="slot" data-sync-id="shell" data-sync-kind="value">x</span>'
        with self.assertRaisesRegex(mk.MakeFailed, "runtime-promoted shell"):
            mk.audit(raw, pathlib.Path("d.html"), (mk.promote.SHARED_ASSETS,))

    def test_reports_an_asset_no_root_can_resolve(self):
        raw = DECK + '<img src="../x/nowhere-at-all.png">'
        with self.assertRaisesRegex(mk.MakeFailed, "nowhere-at-all.png"):
            mk.audit(raw, pathlib.Path("d.html"), (mk.promote.SHARED_ASSETS,))

    def test_resolves_shared_assets_without_an_extra_root(self):
        raw = DECK + '<img src="../../kr/trial/assets/well-done.svg">'
        self.assertEqual(mk.audit(raw, pathlib.Path("d.html"),
                                  (mk.promote.SHARED_ASSETS,)), ["well-done.svg"])


class RenderTests(unittest.TestCase):
    def draft(self) -> mk.Draft:
        draft = mk.Draft.__new__(mk.Draft)
        draft.lang = "en"
        draft.slug = "a-course"
        draft.lessons_dir = mk.DRAFTS / "en" / "x" / "lessons"
        return draft

    def entry(self, slug: str, week: int) -> dict:
        return {"source": f"{slug}/lesson.html", "slug": slug, "week": week,
                "title": {"ko": "제목: 하나", "en": "One", "ja": "ひとつ"}}

    def test_output_parses_and_keeps_a_colon_in_a_title(self):
        text = mk.render(self.draft(), [self.entry("01-one", 1)], [])
        doc = yaml.safe_load(text)
        self.assertEqual(doc["metadata"]["target"], "courses/en/a-course")
        self.assertEqual(doc["spec"]["lessons"][0]["title"]["ko"], "제목: 하나")

    def test_omits_assetroots_when_shared_assets_is_enough(self):
        self.assertNotIn("assetRoots", mk.render(self.draft(),
                                                 [self.entry("01-one", 1)], []))

    def test_emits_assetroots_when_given(self):
        doc = yaml.safe_load(mk.render(self.draft(), [self.entry("01-one", 1)],
                                       ["sandbox/drafts/kr/trial/assets"]))
        self.assertEqual(doc["spec"]["assetRoots"], ["sandbox/drafts/kr/trial/assets"])

    def test_titles_stay_readable_rather_than_escaped(self):
        # The manifest is meant to be reviewed by a content person; 가 is not.
        self.assertIn("제목: 하나", mk.render(self.draft(), [self.entry("01-one", 1)], []))


class LanguageGateTests(unittest.TestCase):
    """An undeclared language is a KeyError in apply.py — after the merge."""

    def test_accepts_declared_languages(self):
        mk.check_language({"kr", "en"})

    def test_rejects_an_undeclared_one(self):
        with self.assertRaisesRegex(mk.MakeFailed, "declares no language zz"):
            mk.check_language({"zz"})


class RepoTests(unittest.TestCase):
    """The manifests in the tree must be what this tool would write today."""

    def test_english_manifests_match_their_decks(self):
        checked = 0
        for path in sorted((mk.DRAFTS / "en").rglob("promotion.yaml")):
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            source = mk.REPO / doc["spec"]["source"]
            weeks = [l["week"] for l in doc["spec"]["lessons"]]
            self.assertEqual(weeks, list(range(1, len(weeks) + 1)), path)
            for lesson in doc["spec"]["lessons"]:
                deck = source / lesson["source"]
                self.assertTrue(deck.is_file(), deck)
                self.assertEqual(mk.titles(deck.read_text(encoding="utf-8"), deck),
                                 lesson["title"], deck)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
