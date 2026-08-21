#!/usr/bin/env python3
"""
Derive a course's `promotion.yaml` from the decks sitting beside it.

    python3 tools/make-promotion.py sandbox/drafts/en/tracks/1-core-patterns/courses/core-first-exchanges-2
    python3 tools/make-promotion.py --lang en                 # every course draft that has decks
    python3 tools/make-promotion.py --lang en --check         # report; write nothing
    python3 tools/make-promotion.py --lang en --scaffold-target
    python3 tools/make-promotion.py --lang en --force         # regenerate manifests that exist

WHY THIS EXISTS

  The manifest is the reviewable part of a promotion, but nothing in it is a
  judgement call. The deck list is whatever `lessons/<slug>/lesson.html` exists,
  the week is the position in that list, and the three titles are already in the
  deck's own `<meta name="podo:title-{ko,en,ja}">`. The Korean catalogue's 49
  manifests were written in one bulk commit; hand-writing another set for English
  is exactly the third copy `tools/promote.py`'s docstring is about.

  So this reads the decks and writes the manifest. What it will not do is invent
  anything — a deck with no title metas is an error naming that deck, never a
  guessed title. Same decks in, same manifest out.

WHAT IT DELIBERATELY DOES NOT OWN

  `courses/<lang>/<slug>/course.yaml`. `promote.py` requires the target to exist
  already, so that a course's identity (`classLevel`, `lessonTime`, `countryCode`
  — the natural key grape matches on) and its `enabled` flag stay a human act.
  `--scaffold-target` copies the draft's `course.yaml` into place for a course
  that has none, and refuses when the target already exists or when the draft
  says `enabled: true`: a new course arrives switched off and is enabled
  deliberately, in its own diff.

ORDER IS NUMERIC, NOT LEXICOGRAPHIC

  `100-far-from-it` sorts before `90-surely-cold-outside` as a string, which
  would hand week 11 to the wrong deck in every course whose lesson numbers cross
  100. `courses/kr/core-upper-intermediate-1` is that course today, so the
  ordering key is the integer prefix.

A NOTE ON THE KOREAN MANIFESTS

  They predate this tool and carry hand-written Korean commentary, and ~42 of
  their decks never got title metas. Regenerating one with --force would drop the
  commentary, and for those decks it would fail outright rather than write a
  manifest with no titles. There is no reason to run this over `sandbox/drafts/kr`
  and it refuses to touch an existing manifest without --force.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import model
import promote

REPO = pathlib.Path(__file__).resolve().parent.parent
DRAFTS = REPO / "sandbox" / "drafts"
COURSES = REPO / "courses"

LANGS = ("ko", "en", "ja")

# schemas/promotion.schema.json — `slug`. The integer prefix is the sort key.
SLUG_RE = re.compile(r"^(?P<n>[0-9]{2,3})-(?P<rest>[a-z0-9]+(?:-[a-z0-9]+)*)$")

# sandbox/drafts/<lang>/…/courses/<course-slug>
TARGET_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def meta_re(name: str) -> re.Pattern[str]:
    """`<meta name=… content=…>` with the two attributes in either order.

    Written the way promote.py's LINK_RE is, and for the same reason: requiring a
    fixed attribute order silently skipped decks a formatter had reordered, and
    the deck then read as having no title at all.
    """
    return re.compile(
        rf'<meta(?=[^>]*\bname="{re.escape(name)}")[^>]*?\bcontent="([^"]*)"[^>]*>')


TITLE_RE = {lang: meta_re(f"podo:title-{lang}") for lang in LANGS}


class MakeFailed(Exception):
    pass


def rel(path: pathlib.Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def yaml_scalar(text: str) -> str:
    """One title, safe on the right of a `key:` — promote.py's rule, same reason.

    A title is prose and prose contains colons. `ensure_ascii=False` keeps the
    Korean and Japanese readable in the diff, which is the point of putting the
    manifest under review in the first place.
    """
    return json.dumps(text, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# read one deck
# --------------------------------------------------------------------------- #

def titles(raw: str, deck: pathlib.Path) -> dict[str, str]:
    """The three titles the deck declares, or an error naming what is missing."""
    found: dict[str, str] = {}
    missing: list[str] = []
    for lang in LANGS:
        match = TITLE_RE[lang].search(raw)
        # An empty content= is as unusable as no tag at all, and far easier to
        # ship by accident — a generator that filled the attribute with nothing.
        if not match or not match.group(1).strip():
            missing.append(f"podo:title-{lang}")
        else:
            found[lang] = html.unescape(match.group(1)).strip()
    if missing:
        raise MakeFailed(
            f"{rel(deck)}: no usable {', '.join(missing)}\n"
            "  titles come from the deck, so add the meta there rather than "
            "writing one into the manifest")
    return found


def audit(raw: str, deck: pathlib.Path, roots: tuple[pathlib.Path, ...]) -> list[str]:
    """Run promote.py's own checks now, so a bad deck fails here and not later.

    Returns the asset basenames the deck needs. Sharing promote's `flatten` is
    the point — a manifest whose assets it cannot resolve is a manifest that
    writes cleanly and then fails the moment anyone promotes it.
    """
    try:
        promote.resolve_kinds(raw)
        _page, _sheets, _scripts, assets = promote.flatten(raw)
    except promote.PromoteFailed as exc:
        raise MakeFailed(f"{rel(deck)}: {exc}")

    unresolved = []
    for name in assets:
        try:
            promote.find_asset(name, roots)
        except promote.PromoteFailed:
            unresolved.append(name)
    if unresolved:
        raise MakeFailed(
            f"{rel(deck)}: no asset found for {', '.join(unresolved)}\n"
            f"  looked in {' and '.join(rel(r) for r in roots)}\n"
            "  pass --asset-root <dir under sandbox/drafts> for the folder holding it")
    return assets


# --------------------------------------------------------------------------- #
# one course draft
# --------------------------------------------------------------------------- #

class Draft:
    """A course directory under sandbox/drafts: course.yaml plus lessons/."""

    def __init__(self, path: pathlib.Path):
        self.path = path.resolve()
        self.rel = rel(self.path)

        try:
            inner = self.path.relative_to(DRAFTS)
        except ValueError:
            raise MakeFailed(f"{self.rel}: not under {rel(DRAFTS)}")
        if not inner.parts:
            raise MakeFailed(f"{self.rel}: expected sandbox/drafts/<lang>/…/<course>")

        self.lang = inner.parts[0]
        self.slug = self.path.name
        if not TARGET_RE.match(self.slug):
            raise MakeFailed(
                f"{self.rel}: course directory name is the deployed slug and must "
                "be lowercase-hyphenated")

        self.course_yaml = self.path / "course.yaml"
        if not self.course_yaml.is_file():
            raise MakeFailed(
                f"{self.rel}: no course.yaml — this is not a course draft")

        self.lessons_dir = self.path / "lessons"
        self.target = COURSES / self.lang / self.slug
        self.manifest_path = self.path / "promotion.yaml"

    def decks(self) -> list[tuple[str, pathlib.Path]]:
        """(slug, lesson.html) in week order — the integer prefix, not the string."""
        if not self.lessons_dir.is_dir():
            return []

        found = []
        for child in sorted(self.lessons_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            deck = child / "lesson.html"
            if not deck.is_file():
                # Not an error: plan_courses.py scaffolds the directory when the
                # lesson is planned, and the deck is written later.
                continue
            if not SLUG_RE.match(child.name):
                raise MakeFailed(
                    f"{rel(child)}: directory name is the lesson slug and must be "
                    "NN-english-words (schemas/promotion.schema.json)")
            found.append((child.name, deck))

        found.sort(key=lambda pair: (int(SLUG_RE.match(pair[0])["n"]),
                                     SLUG_RE.match(pair[0])["rest"]))
        return found

    def enabled(self) -> bool:
        doc = yaml.safe_load(self.course_yaml.read_text(encoding="utf-8")) or {}
        return bool((doc.get("spec") or {}).get("enabled"))


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #

HEADER = """\
apiVersion: podo.curriculum/v1
kind: Promotion
metadata:
  target: {target}

spec:
  # One lesson owns one directory — lesson.html, and the lesson.yaml promote.py
  # generates beside it. So source is lessons/, and each deck is a path under it.
  source: {source}
"""

FOOTER = """\

# Generated by tools/make-promotion.py from the decks under {source}.
# Add a deck and re-run with --force; the week is its position in the list.
# The three titles are read from each deck's <meta name="podo:title-*"> — to
# change one, edit the deck and regenerate, never this file.
"""


def render(draft: Draft, entries: list[dict], asset_roots: list[str]) -> str:
    source = rel(draft.lessons_dir)
    out = [HEADER.format(target=f"courses/{draft.lang}/{draft.slug}", source=source)]

    if asset_roots:
        out.append("  # Where a flattened basename is looked up, before shared/assets.\n")
        out.append("  assetRoots:\n")
        out.extend(f"    - {root}\n" for root in asset_roots)

    out.append("\n  lessons:\n")
    for entry in entries:
        out.append(f"    - source: {entry['source']}\n")
        out.append(f"      slug: {entry['slug']}\n")
        out.append(f"      week: {entry['week']}\n")
        out.append("      title:\n")
        for lang in LANGS:
            out.append(f"        {lang}: {yaml_scalar(entry['title'][lang])}\n")

    out.append(FOOTER.format(source=source))
    return "".join(out)


def build(draft: Draft, asset_roots: list[str]) -> str | None:
    """The manifest text for this draft, or None when it has no decks yet."""
    decks = draft.decks()
    if not decks:
        return None

    roots = tuple(REPO / r for r in asset_roots) + (promote.SHARED_ASSETS,)
    entries = []
    for week, (slug, deck) in enumerate(decks, start=1):
        raw = deck.read_text(encoding="utf-8")
        audit(raw, deck, roots)
        entries.append({
            "source": f"{slug}/lesson.html",
            "slug": slug,
            "week": week,
            "title": titles(raw, deck),
        })

    text = render(draft, entries, asset_roots)

    # Round-trip through the schema promote.py will check anyway. A manifest this
    # tool writes must never be one promote.py then refuses.
    doc = yaml.safe_load(text)
    try:
        model.check_schema(doc, "promotion.schema.json", draft.manifest_path)
    except SystemExit:
        raise
    except Exception as exc:
        raise MakeFailed(f"{draft.rel}: generated manifest is invalid: {exc}")

    return text


# --------------------------------------------------------------------------- #
# the target course
# --------------------------------------------------------------------------- #

def scaffold(draft: Draft, dry_run: bool) -> None:
    """Copy the draft's course.yaml into courses/, for a course that has none.

    Byte-identical, which is what the 49 Korean courses already are — the draft
    is where a course's identity is authored and reviewed, and copying keeps one
    of them from drifting from the other.
    """
    target_yaml = draft.target / "course.yaml"
    if target_yaml.is_file():
        return

    if draft.enabled():
        raise MakeFailed(
            f"{draft.rel}: course.yaml says enabled: true, so scaffolding it would "
            "create a live course in one step\n"
            "  set enabled: false, scaffold and promote, then enable it in its own diff")

    print(f"    + {rel(target_yaml)}  (enabled: false)")
    if dry_run:
        return
    draft.target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(draft.course_yaml, target_yaml)


def check_language(langs: set[str]) -> None:
    """Every language used must be declared in curriculum.yaml.

    apply.py does `curriculum["spec"]["languages"][course.lang]` with no fallback,
    so an undeclared language is a KeyError during deploy — after the PR is merged,
    which is the worst place to find out.
    """
    doc = yaml.safe_load((REPO / "curriculum.yaml").read_text(encoding="utf-8"))
    declared = set((doc.get("spec") or {}).get("languages") or {})
    missing = sorted(langs - declared)
    if missing:
        raise MakeFailed(
            f"curriculum.yaml declares no language {', '.join(missing)}\n"
            "  spec.languages is what apply.py reads for LANG_TYPE; a course under "
            f"courses/{missing[0]}/ would fail the deploy, not the PR")


# --------------------------------------------------------------------------- #

def discover(lang: str | None) -> list[pathlib.Path]:
    """Course drafts: a directory holding both course.yaml and lessons/."""
    root = DRAFTS / lang if lang else DRAFTS
    if not root.is_dir():
        raise MakeFailed(f"no such drafts tree: {rel(root)}")
    return sorted(p.parent for p in root.rglob("course.yaml")
                  if (p.parent / "lessons").is_dir())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("drafts", nargs="*", type=pathlib.Path,
                    help="course directories under sandbox/drafts/")
    ap.add_argument("--lang", help="every course draft under sandbox/drafts/<lang>/")
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    ap.add_argument("--force", action="store_true",
                    help="regenerate a promotion.yaml that already exists")
    ap.add_argument("--scaffold-target", action="store_true",
                    help="copy course.yaml into courses/ when the target has none")
    ap.add_argument("--asset-root", action="append", default=[], metavar="DIR",
                    help="extra folder to resolve a flattened asset basename from; "
                         "repeatable, searched before shared/assets")
    args = ap.parse_args()

    if args.drafts and args.lang:
        print("✗ name drafts or pass --lang, not both")
        return 1

    asset_roots = []
    for root in args.asset_root:
        path = pathlib.Path(root)
        if not (REPO / path).is_dir():
            print(f"✗ --asset-root is not a directory: {root}")
            return 1
        asset_roots.append(pathlib.PurePosixPath(path).as_posix())

    try:
        paths = [p.resolve() for p in args.drafts] or discover(args.lang)
        if not paths:
            print("no course drafts found")
            return 1

        drafts = [Draft(p) for p in paths]
        check_language({d.lang for d in drafts})

        written = skipped = empty = 0
        for draft in drafts:
            # Decide whether to touch this manifest before doing the work to build
            # it. Auditing first meant a sweep over a tree of finished courses
            # died on the first deck needing an --asset-root it was never going to
            # rewrite anyway.
            exists = draft.manifest_path.is_file()
            if exists and not args.force:
                print(f"{draft.rel}\n    ~ promotion.yaml exists — --force to regenerate")
                skipped += 1
                continue

            text = build(draft, asset_roots)
            if text is None:
                empty += 1
                continue

            n = text.count("\n      slug: ")

            verb = "rewrite" if exists else "write"
            print(f"{draft.rel}\n    {verb} promotion.yaml  "
                  f"({n} lesson{'s' if n != 1 else ''} → courses/{draft.lang}/{draft.slug})")

            if args.scaffold_target:
                scaffold(draft, args.check)
            elif not (draft.target / "course.yaml").is_file():
                print(f"    ! {rel(draft.target)}/course.yaml does not exist — "
                      "promote.py will refuse; pass --scaffold-target")

            if not args.check:
                draft.manifest_path.write_text(text, encoding="utf-8")
            written += 1

    except MakeFailed as exc:
        print(f"\n✗ {exc}")
        return 1

    print(f"\n{written} manifest(s), {skipped} left alone, "
          f"{empty} course(s) with no deck yet")
    if args.check:
        print("(--check — nothing written)")
    elif written:
        print("now run:  python3 tools/promote.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
