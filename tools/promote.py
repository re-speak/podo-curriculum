#!/usr/bin/env python3
"""
Promote reviewed decks out of `sandbox/drafts/` into a deployable `courses/` course.

Promotion is the moment a draft becomes something a learner can be shown. It is
the only step that writes into `courses/`, so it is also where the two things
that make that safe live: the packaging transforms grape and lemonboard require,
and the gate that stops a removal here from stranding a live course.

    python3 tools/promote.py                       # every manifest in sandbox/drafts
    python3 tools/promote.py <manifest.yaml> …      # just these
    python3 tools/promote.py --check               # what would change; writes nothing

WHAT IT DOES, per deck

  1. audit    — resolve every `data-sync-id` to the kind lemonboard's binder will
                infer, statically. An id that resolves to nothing is dropped from
                the sync set with no error at runtime: the activity works on your
                screen and never reaches the other person. That is the failure
                this step exists to make loud.
  2. flatten  — `../../shared/js/x.js` → `x.js`, `../assets/**/y` → `y`, remote
                avatars → bundled local files. A deck ships as one flat GCS
                prefix, so two folders may not share a basename.
  3. bundle   — every referenced sheet, script and image is copied next to the
                deck. `build.py` later merges the sheets in link order.
  4. write    — `lesson.yaml` from the manifest.

  The directory is cleared first, so a deck retired from the manifest disappears
  here. That is what keeps promotion idempotent: run it twice, get the same tree.

WHY A MANIFEST

  This replaces `import-trial-decks.py` and `import-report-deck.py`, which were
  the same idea written twice — each welded to one course, each carrying its deck
  list as a literal in Python, and each with its own copy of `flatten`,
  `find_asset` and `build_deck` that had already drifted apart. A third course
  would have been a third copy.

  Putting the mapping in YAML beside the drafts makes a promotion a diff a content
  person can review, which is the property the rest of this repository is built on.

  See `schemas/promotion.schema.json` and any `promotion.yaml` under sandbox/drafts.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

import yaml

import model

REPO = pathlib.Path(__file__).resolve().parent.parent
DRAFTS = REPO / "sandbox" / "drafts"

SCRIPT_ROOT = REPO / "shared" / "js"
CSS_ROOT = REPO / "shared" / "css"
SHARED_ASSETS = REPO / "shared" / "assets"

SRC_RE = re.compile(r'\bsrc="([^"]+)"')
# Three shapes reach us: the canonical one, one that a formatter reordered and
# self-closed, and one that is minified onto a single line. Requiring the exact
# attribute order, or a trailing newline, skipped the last two and reported the
# deck as having no stylesheet at all. So: require both attributes in either
# order, and capture the surrounding whitespace rather than assume it — a deck
# that was one line stays one line, and an indented one keeps its indent.
LINK_RE = re.compile(
    r'(?P<lead>[ \t]*)<link(?=[^>]*\brel="stylesheet")[^>]*?\bhref="(?P<href>[^"]+)"[^>]*?/?>'
    r'(?P<tail>\n?)')
REMOTE = ("http://", "https://", "//", "data:", "#")

# A control that only exists after JavaScript runs is invisible to lemonboard's
# validator, which parses without executing scripts. It works in class and fails
# validation — or worse, resolves to no kind and silently desyncs. The authoring
# HTML must contain the real <input>/<textarea>/.build-zone.
SHELL_RE = re.compile(r'<span class="(?:slot|answer-space)"[^>]*\bdata-sync-id=')

# Bundled rather than fetched: a deck has to survive a locked-down classroom
# network, and these are the only images the sources leave on a remote host.
# Both already sit in shared/assets, so this needs no network either.
AVATARS = {
    "https://respeak-lemonade.s3.ap-northeast-2.amazonaws.com/test/hana-avatar.jpg":
        "hana-avatar.jpg",
    "https://respeak-lemonade.s3.ap-northeast-2.amazonaws.com/test/haruka-avatar.jpg":
        "haruka-avatar.jpg",
}

def draft_teaches(source: pathlib.Path) -> dict:
    """초안 lesson.html 옆에 있는 lesson.yaml 의 teaches.

    plan_courses.py 가 목차에서 적어 둔 값이고, 짝인 lesson.html 과 같은 폴더에 산다.
    초안 없이 courses/ 에 직접 쓴 과(체험 · 영어)는 이 파일이 없다 — 그때는 비운다."""
    path = source.parent / "lesson.yaml"
    if not path.is_file():
        return {}
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return (doc.get("spec") or {}).get("teaches") or {}


def yaml_teaches(teaches: dict | None) -> str:
    """초안의 teaches 를 lesson.yaml 본문에 넣을 수 있는 블록으로.

    비어 있으면 ` {}` 한 칸짜리로 접어서, 초안이 없는 과의 파일이 예전과 똑같이
    읽히게 둔다."""
    if not teaches:
        return " {}"
    body = yaml.safe_dump(teaches, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=10**6)
    return "\n" + "\n".join(f"    {line}" for line in body.rstrip("\n").splitlines())


def yaml_scalar(text: str) -> str:
    """One title, safe to drop into the template on the right of a `key:`.

    A title is prose and prose contains colons — "Backchanneling: empathy" wrote
    a `lesson.yaml` that no longer parsed, and the failure surfaced two tools
    later in whatever next read the file. json.dumps emits a double-quoted scalar
    with the escapes YAML wants, and plain ASCII strings come back unchanged, so
    the generated file keeps reading the way it always has.
    """
    return json.dumps(text, ensure_ascii=False)


LESSON_YAML = """\
apiVersion: podo.curriculum/v1
kind: Lesson
metadata:
  slug: {slug}

spec:
  week: {week}

  title:
    ko: {ko}
    en: {en}
    ja: {ja}

  decks:
    lecture:  {{ entry: lecture/index.html }}
    prestudy: {{ entry: prestudy/index.html }}

  # 초안 lesson.yaml 의 teaches 를 그대로 옮긴다 — plan_courses.py 가 목차에서 적어
  # 둔 값이고, 공개 카탈로그가 과마다 보여 주는 "이번에 배우는 것 · 목표" 가 이것이다.
  # 덱을 읽어서 쓰지는 않는다: 덱에서 읽어낸 것을 적으면 리뷰가 실제 덱이 아니라 이
  # 메타데이터를 검토하게 된다. 초안에 없으면 비워 둔다.
  teaches:{teaches}
  prerequisites: []
  source: {source}

# Generated by tools/promote.py from {manifest} — edit the draft and re-run.
"""


class PromoteFailed(Exception):
    pass


def rel(path: pathlib.Path) -> str:
    """Repo-relative for display, absolute when it sits outside (tests, odd roots)."""
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- #
# audit — lemonboard's kind resolution, run statically
# --------------------------------------------------------------------------- #

def resolve_kinds(raw: str) -> dict[str, str]:
    """sync-id -> the kind lemonboard's binder will infer, or raise.

    Mirrors html-sync/kinds.ts in order: an explicit data-sync-kind wins, then a
    form control is `value`, then a [data-sync-option] descendant is `selection`,
    then a data-sync-state attribute is `toggle`. Anything left resolves to
    nothing and is silently private, so it is an error here instead.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:                                        # pragma: no cover
        raise PromoteFailed(
            "beautifulsoup4 is required by this tool:  "
            "pip install -r tools/requirements.txt")

    soup = BeautifulSoup(raw, "html.parser")
    kinds: dict[str, str] = {}
    unresolved: list[str] = []

    for el in soup.select("[data-sync-id]"):
        sync_id = el["data-sync-id"]
        if sync_id in kinds:
            raise PromoteFailed(f"duplicate data-sync-id: {sync_id}")
        if el.has_attr("data-sync-kind"):
            kinds[sync_id] = el["data-sync-kind"]
        elif el.name in ("input", "textarea", "select"):
            kinds[sync_id] = "value"
        elif el.select_one("[data-sync-option]"):
            kinds[sync_id] = "selection"
        elif el.has_attr("data-sync-state"):
            kinds[sync_id] = "toggle"
        else:
            unresolved.append(f"<{el.name} data-sync-id=\"{sync_id}\">")

    if unresolved:
        raise PromoteFailed(
            "these carry data-sync-id but resolve to no kind — they would be "
            "dropped from the sync set with no error:\n    "
            + "\n    ".join(unresolved))
    if not kinds:
        raise PromoteFailed("no data-sync-id found at all; is this the right deck?")
    return kinds


# --------------------------------------------------------------------------- #
# flatten refs
# --------------------------------------------------------------------------- #

def flatten(raw: str) -> tuple[str, list[str], list[str], list[str]]:
    scripts: list[str] = []
    assets: list[str] = []
    sheets: list[str] = []
    origins: dict[str, str] = {}

    def claim(name: str, ref: str) -> None:
        """Flattening means one GCS prefix, so two folders cannot share a basename."""
        previous = origins.setdefault(name, ref)
        if previous != ref:
            raise PromoteFailed(
                f"basename collision on {name}: {previous} and {ref} would "
                f"flatten onto each other")

    # Rewrite first, then let one_src below pick the results up as ordinary local
    # refs — that way the bundling and the collision check have a single path.
    for url, name in AVATARS.items():
        raw = raw.replace(url, name)

    def one_src(match: re.Match) -> str:
        ref = match.group(1)
        if ref.startswith(REMOTE):
            return match.group(0)
        name = pathlib.PurePosixPath(ref).name
        claim(name, ref)
        (scripts if ref.endswith(".js") else assets).append(name)
        return f'src="{name}"'

    raw = SRC_RE.sub(one_src, raw)

    def one_link(match: re.Match) -> str:
        ref = match.group("href")
        if ref.startswith(REMOTE):
            return match.group(0)
        name = pathlib.PurePosixPath(ref).name
        claim(name, ref)
        sheets.append(name)
        lead = match.group("lead") or ("  " if match.group("tail") else "")
        return f'{lead}<link rel="stylesheet" href="{name}">{match.group("tail")}'

    raw, n = LINK_RE.subn(one_link, raw)
    if not sheets:
        raise PromoteFailed(f"no local stylesheet <link> found to rewrite ({n} seen)")

    left = SHELL_RE.findall(raw)
    if left:
        raise PromoteFailed(f"{len(left)} runtime-promoted shell(s) found; "
                            "write the real control into the HTML instead")

    return raw, sorted(set(sheets)), sorted(set(scripts)), sorted(set(assets))


# --------------------------------------------------------------------------- #
# bundle
# --------------------------------------------------------------------------- #

def find_asset(name: str, roots: tuple[pathlib.Path, ...]) -> pathlib.Path:
    for root in roots:
        hits = sorted(root.rglob(name)) if root.is_dir() else []
        if hits:
            return hits[0]
    where = " and ".join(rel(r) for r in roots)
    raise PromoteFailed(f"asset not found: {name}\n  looked in {where}")


def clean_generated_page(page: str) -> str:
    """Remove line-end whitespace from deploy output without changing a reviewed draft."""
    return re.sub(r"[ \t]+(?=\r?$)", "", page, flags=re.MULTILINE)


def build_deck(target: pathlib.Path, page: str, sheets: list[str],
               scripts: list[str], assets: list[str],
               asset_roots: tuple[pathlib.Path, ...]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(clean_generated_page(page), encoding="utf-8")

    for name in sheets:
        origin = CSS_ROOT / name
        if not origin.is_file():
            raise PromoteFailed(f"stylesheet not found: {origin}")
        shutil.copyfile(origin, target / name)

    for name in scripts:
        origin = SCRIPT_ROOT / name
        if not origin.is_file():
            raise PromoteFailed(f"script not found: {origin}")
        shutil.copyfile(origin, target / name)

    for name in assets:
        shutil.copyfile(find_asset(name, asset_roots), target / name)


# --------------------------------------------------------------------------- #
# the manifest
# --------------------------------------------------------------------------- #

class Manifest:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.rel = path.relative_to(REPO).as_posix()
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        if doc.get("kind") != "Promotion":
            raise PromoteFailed(f"{self.rel}: kind must be 'Promotion'")

        # Shape first, then the checks a schema cannot express (does the target
        # exist, is the source a directory, do the weeks run 1..N). Same split
        # model.py already uses for course.yaml and lesson.yaml.
        try:
            model.check_schema(doc, "promotion.schema.json", path)
        except SystemExit:
            raise
        except Exception as exc:
            raise PromoteFailed(f"{self.rel}: {exc}")

        spec = doc.get("spec") or {}
        target = (doc.get("metadata") or {}).get("target")
        if not target:
            raise PromoteFailed(f"{self.rel}: metadata.target is required")

        self.course = REPO / target
        if not (self.course / "course.yaml").is_file():
            raise PromoteFailed(
                f"{self.rel}: target has no course.yaml: {target}\n"
                "  promotion fills a course that already exists; create it first")

        source = spec.get("source")
        if not source:
            raise PromoteFailed(f"{self.rel}: spec.source is required")
        self.source = REPO / source
        if not self.source.is_dir():
            raise PromoteFailed(f"{self.rel}: spec.source is not a directory: {source}")

        # Where a flattened basename is looked up, in order. shared/assets is
        # always last so a draft-local image wins over a shared one of the name.
        roots = [REPO / p for p in (spec.get("assetRoots") or [])]
        self.asset_roots = tuple(roots + [SHARED_ASSETS])

        self.lessons = spec.get("lessons") or []
        if not self.lessons:
            raise PromoteFailed(f"{self.rel}: spec.lessons is empty")

        weeks = [l.get("week") for l in self.lessons]
        if sorted(weeks) != list(range(1, len(weeks) + 1)):
            raise PromoteFailed(
                f"{self.rel}: weeks must run 1..N with no gaps, got {sorted(weeks)}\n"
                "  CLASS_WEEK is contiguous; a gap makes a lesson unreachable")

    @property
    def enabled(self) -> bool:
        doc = yaml.safe_load((self.course / "course.yaml").read_text(encoding="utf-8"))
        return bool((doc.get("spec") or {}).get("enabled"))

    def existing_slugs(self) -> set[str]:
        root = self.course / "lessons"
        if not root.is_dir():
            return set()
        return {p.name for p in root.iterdir() if (p / "lesson.yaml").is_file()}

    def wanted_slugs(self) -> set[str]:
        return {l["slug"] for l in self.lessons}


# --------------------------------------------------------------------------- #
# the retirement gate
# --------------------------------------------------------------------------- #

def check_removals(man: Manifest, assume_yes: bool) -> None:
    """Refuse to strand a live course by deleting its lessons out from under it.

    apply.py is a pure upsert — it has no delete path and never reads back from
    grape. So removing a lesson here does not retire anything: the row keeps
    USE_YN='Y', keeps pointing at GCS content nobody manages any more, and the
    repository forgets it exists. The learner still sees it and the deploy is
    green. Retirement is `enabled: false`, deployed, and only then the directory.

    Enablement is a property of the course, not the lesson (there is no per-lesson
    USE_YN), so a removal is only dangerous when the whole course is live.
    """
    removed = sorted(man.existing_slugs() - man.wanted_slugs())
    if not removed or not man.enabled:
        return

    course = rel(man.course)
    print()
    print(f"  ⚠ {len(removed)} lesson(s) would disappear from {course}:")
    for slug in removed:
        print(f"      {slug}")
    print()
    print("    That course is enabled: true — it is live for learners right now.")
    print("    Deleting these does NOT retire them. apply.py never removes rows,")
    print("    so they would stay live in grape, unmanaged, pointing at content")
    print("    nobody updates. Retirement is enabled: false, deployed first.")
    print()

    if not sys.stdin.isatty() or assume_yes:
        # Never default-yes in CI. A non-interactive run that silently retires a
        # live course is the same class of bug this gate exists to prevent.
        raise PromoteFailed(
            "refusing to remove lessons from a live course in a non-interactive run.\n"
            f"  set enabled: false in {course}/course.yaml, deploy that, then re-run")

    try:
        answer = input("    Set enabled: false so the next deploy retires them "
                       "properly? [Y/n] ").strip().lower()
    except EOFError:
        # No one is there to answer. Refusing is the only safe reading — the
        # default is "yes, retire", and taking that from a closed stdin would
        # flip a live course off because nobody was watching.
        raise PromoteFailed("stdin closed before the question was answered; "
                            "nothing was written")
    if answer in ("", "y", "yes"):
        retire(man.course)
        raise PromoteFailed(
            f"{course} is now enabled: false — nothing else was written.\n"
            "  commit that, let it deploy, then re-run this to remove the lessons")

    raise PromoteFailed(
        "stopped. Removing these while the course is live would strand them.\n"
        f"  retire {course} first, or put the lessons back in the manifest")


def retire(course: pathlib.Path) -> None:
    """Flip `enabled: true` → `false` in place, keeping comments and layout."""
    path = course / "course.yaml"
    raw = path.read_text(encoding="utf-8")
    new, n = re.subn(r"^(\s*enabled:\s*)true\b", r"\1false", raw, count=1,
                     flags=re.MULTILINE)
    if not n:
        raise PromoteFailed(f"could not find `enabled: true` in {path}")
    path.write_text(new, encoding="utf-8")
    print(f"    ✓ wrote enabled: false to {rel(path)}")


# --------------------------------------------------------------------------- #

def promote(man: Manifest, dry_run: bool, assume_yes: bool) -> None:
    print(f"{man.rel}")
    print(f"  → {rel(man.course)}"
          f"  ({'enabled' if man.enabled else 'disabled'})")

    check_removals(man, assume_yes)

    lessons = man.course / "lessons"
    if not dry_run and lessons.exists():
        shutil.rmtree(lessons)

    for entry in man.lessons:
        slug, week = entry["slug"], entry["week"]
        source = entry["source"]
        deck = man.source / source
        if not deck.is_file():
            raise PromoteFailed(f"deck not found: {rel(deck)}")

        raw = deck.read_text(encoding="utf-8")
        kinds = resolve_kinds(raw)
        page, sheets, scripts, assets = flatten(raw)

        tally: dict[str, int] = {}
        for kind in kinds.values():
            tally[kind] = tally.get(kind, 0) + 1
        counts = ", ".join(f"{k} {v}" for k, v in sorted(tally.items()))
        print(f"  {slug:<24} sync: {counts:<34} "
              f"{len(sheets)} sheet(s), {len(scripts)} script(s), "
              f"{len(assets)} asset(s)")

        if dry_run:
            continue

        lesson = lessons / slug
        lesson.mkdir(parents=True, exist_ok=True)
        (lesson / "lesson.yaml").write_text(
            LESSON_YAML.format(
                slug=slug, week=week,
                teaches=yaml_teaches(draft_teaches(man.source / source)),
                source=rel(man.source / source),
                manifest=man.rel,
                **{lang: yaml_scalar(text) for lang, text in entry["title"].items()}),
            encoding="utf-8")

        # Both slots are mandatory — a lesson with only 수업용 leaves
        # PRESTUDY_LEMONBOARD_KEY empty and class creation fails at
        # /rooms/null/duplicate. The same deck fills both.
        for slot in ("lecture", "prestudy"):
            build_deck(lesson / slot, page, sheets, scripts, assets, man.asset_roots)


def discover() -> list[pathlib.Path]:
    return sorted(DRAFTS.rglob("promotion.yaml"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("manifests", nargs="*", type=pathlib.Path,
                    help="promotion.yaml to run (default: every one under sandbox/drafts)")
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    ap.add_argument("--yes", action="store_true",
                    help="do not prompt; fail instead if a live course would lose lessons")
    args = ap.parse_args()

    paths = [p.resolve() for p in args.manifests] or discover()
    if not paths:
        print("no promotion.yaml found under sandbox/drafts/")
        return 1

    try:
        for i, path in enumerate(paths):
            if i:
                print()
            promote(Manifest(path), args.check, args.yes)
    except PromoteFailed as exc:
        print(f"\n✗ {exc}")
        return 1

    if args.check:
        print("\n(--check — nothing written)")
    else:
        print("\nnow run:  python3 tools/validate.py --contract --env stage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
