#!/usr/bin/env python3
"""Entry-floor-aware vocabulary provenance for canonical CTX 1-12."""

from __future__ import annotations

import pathlib
import re
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import vocabulary


ROOT = pathlib.Path(__file__).resolve().parents[3]
ENGLISH = ROOT / "sandbox/drafts/en"
CORE = ENGLISH / "tracks/1-core-patterns"
CONTEXTUAL = ENGLISH / "tracks/2-contextual-english"
REVIEW_ID = re.compile(r'<meta name="podo:review-id" content="([^"]+)">')


def canonical_contextual_path(number: int) -> pathlib.Path:
    course = (
        "ctx-travel-arrivals-transport"
        if number <= 6
        else "ctx-travel-hotels-food"
    )
    matches = list(
        (CONTEXTUAL / "courses" / course / "lessons").glob(
            f"{number:02d}-*/lesson.html"
        )
    )
    if len(matches) != 1:
        raise AssertionError(f"CTX-{number}: expected one canonical deck, found {matches}")
    return matches[0]


def source_by_review_id(review_id: str) -> tuple[pathlib.Path, str]:
    contextual = re.fullmatch(r"CTX-(\d+)", review_id)
    if contextual:
        path = canonical_contextual_path(int(contextual.group(1)))
        return path, path.read_text(encoding="utf-8")

    matches = []
    for path in CORE.rglob("lesson.html"):
        source = path.read_text(encoding="utf-8")
        match = REVIEW_ID.search(source)
        if match and match.group(1) == review_id:
            matches.append((path, source))
    if len(matches) != 1:
        raise AssertionError(f"{review_id}: expected one Core owner deck, found {matches}")
    return matches[0]


def entry_floor(number: int) -> int:
    brief = CONTEXTUAL / "toc" / f"CTX-{number}.md"
    match = re.search(
        r"\*\*Entry floor:\*\* Core (\d+)",
        brief.read_text(encoding="utf-8"),
    )
    if not match:
        raise AssertionError(f"CTX-{number}: brief has no Core entry floor")
    return int(match.group(1))


def owner_is_reachable(owner: str, number: int) -> bool:
    core_owner = re.fullmatch(r"CORE-(\d+)", owner)
    if core_owner:
        return int(core_owner.group(1)) <= entry_floor(number)
    contextual_owner = re.fullmatch(r"CTX-(\d+)", owner)
    if contextual_owner:
        return int(contextual_owner.group(1)) < number
    return False


def declarations(review_id: str) -> dict:
    path, source = source_by_review_id(review_id)
    return vocabulary.parse(source, source=path)["categories"]


class ContextualEarlyProvenanceTests(unittest.TestCase):
    def test_ctx1_canonical_pilot_has_the_reviewed_exact_classifications(self):
        categories = declarations("CTX-1")
        new = {entry["english"].casefold() for entry in categories["new"]}
        assumed = {entry["english"].casefold() for entry in categories["assumed"]}
        recycled = {
            entry["english"].casefold(): entry["source"]
            for entry in categories["recycled"]
        }
        self.assertIn("if possible", new)
        self.assertTrue({"would like", "could we have", "seat"}.issubset(assumed))
        self.assertEqual(recycled["window seat"], "CORE-46")
        self.assertEqual(recycled["aisle seat"], "CORE-46")

    def test_ctx7_to_12_repair_classifications_are_exact(self):
        expected = {
            7: (("reservation", "new", None), ("can we leave", "assumed", None),
                ("receipt", "recycled", "CORE-22")),
            8: (("doesn't work", "new", None), ("can we", "assumed", None)),
            9: (("contain", "new", None), ("I don't eat", "assumed", None)),
            10: (("ordered", "new", None), ("can I have", "assumed", None),
                 ("instead", "recycled", "CORE-14")),
            11: (("doesn't work", "recycled", "CTX-8"),
                 ("exchange", "new", None), ("bought", "recycled", "CORE-32")),
            12: (("can we move", "assumed", None), ("still", "recycled", "CORE-29"),
                 ("reservation", "recycled", "CTX-7")),
        }
        for number, entries in expected.items():
            categories = declarations(f"CTX-{number}")
            actual = {
                entry["english"].casefold(): (category, entry["source"])
                for category, items in categories.items()
                for entry in items
            }
            for word, category, owner in entries:
                self.assertEqual(actual[word.casefold()], (category, owner), (number, word))

    def test_every_recycled_item_cites_an_exact_reachable_new_owner(self):
        for number in range(1, 13):
            categories = declarations(f"CTX-{number}")
            for entry in categories["recycled"]:
                self.assertTrue(
                    owner_is_reachable(entry["source"], number),
                    (number, entry, entry_floor(number)),
                )
                owner = declarations(entry["source"])
                owner_words = {
                    item["english"].casefold() for item in owner["new"]
                }
                self.assertIn(entry["english"].casefold(), owner_words, (number, entry))

    def test_new_items_have_no_reachable_prior_declared_new_owner(self):
        owners: dict[str, set[str]] = {}
        for path in CORE.rglob("lesson.html"):
            source = path.read_text(encoding="utf-8")
            match = REVIEW_ID.search(source)
            if not match:
                continue
            for entry in vocabulary.parse(source, source=path)["categories"]["new"]:
                owners.setdefault(entry["english"].casefold(), set()).add(match.group(1))

        for number in range(1, 13):
            review_id = f"CTX-{number}"
            categories = declarations(review_id)
            for entry in categories["new"]:
                reachable = {
                    owner
                    for owner in owners.get(entry["english"].casefold(), set())
                    if owner_is_reachable(owner, number)
                }
                self.assertEqual(
                    reachable,
                    set(),
                    (number, entry, reachable, entry_floor(number)),
                )
            for entry in categories["new"]:
                owners.setdefault(entry["english"].casefold(), set()).add(review_id)


if __name__ == "__main__":
    unittest.main()
