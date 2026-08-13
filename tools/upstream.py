"""Locate the authoring tree that `sync-from-authoring.py` and
`import-trial-decks.py` read from.

`podo-curriculum-public` holds one directory per subject language —
`korean/`, `english/` — and the files they share sit at the repository root:
`runtime/`, `viewer.html`, `ux-philosophy.md`. Older checkouts kept `runtime/`
inside `korean/` and had no second language at all; accepting both shapes lets a
sync transition without silently reading the wrong directory. This repo is the
deployable form of the same content.

**A language is named, never guessed.** `resolve()` takes the language it is
looking for and fails if that directory is absent, rather than falling back to
whichever tree happens to exist. Guessing is how a Korean sync would quietly
overwrite an English destination — the two trees have the same internal shape
(`tracks/*/table-of-contents.md`) and differ only by the directory above them.

Resolution order:

  1. --upstream on the command line
  2. $PODO_AUTHORING_ROOT
  3. the default sibling layout below

Nothing here is read by build · validate · plan · apply. A missing authoring
tree cannot affect the merge gate — it only stops a re-sync.
"""
from __future__ import annotations

import os
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

ENV_VAR = "PODO_AUTHORING_ROOT"

# How the two repos sit on a typical checkout:
#   ~/Documents/podo_repository/podo-curriculum   <- here
#   ~/Documents/podo_work/podo-curriculum-public <- upstream
DEFAULTS = (
    REPO.parent.parent / "podo_work" / "podo-curriculum-public",
    REPO.parent / "podo-curriculum-public",
    # Pre-rename fallback for older local checkouts.
    REPO.parent.parent / "podo_work" / "beginner-curriculum",
    REPO.parent / "beginner-curriculum",
)

# Upstream directory name -> the code this repo files its content under, which is
# also `courses/<code>/` and GT_CLASS_COURSE.LANG_TYPE lowercased (tools/model.py).
# The code is the subject being taught, not the market: English for Japan-market
# learners is `en` here and `countryCode: JP` on the course.
LANGUAGES = {"korean": "kr", "english": "en"}
DEFAULT_LANGUAGE = "korean"

# What makes a directory a language's content root. `tracks/` is the one thing
# every language has; `trial/` is Korean's 체험 tree, and is what the pre-split
# layout carried at its own root.
MARKERS = ("tracks", "trial")


class UpstreamMissing(Exception):
    """Raised with a message that says how to fix it, not just what failed."""


def add_argument(parser) -> None:
    parser.add_argument(
        "--upstream",
        type=pathlib.Path,
        default=None,
        help=f"path to the authoring repo or one language directory (or set ${ENV_VAR})",
    )


def resolve(explicit: pathlib.Path | None = None,
            language: str = DEFAULT_LANGUAGE) -> pathlib.Path:
    if language not in LANGUAGES:
        raise UpstreamMissing(
            f"unknown language {language!r}; known: {', '.join(sorted(LANGUAGES))}")

    tried: list[pathlib.Path] = []

    for candidate in _candidates(explicit):
        tried.append(candidate)
        content = _content_root(candidate, language)
        if content is not None:
            return content.resolve()

    where = "\n  ".join(str(p) for p in tried)
    raise UpstreamMissing(
        f"cannot find the {language} authoring tree (a repository with runtime/ and "
        f"{language}/tracks/, or the legacy runtime/ + trial/ layout).\n"
        f"looked in:\n  {where}\n\n"
        f"pass --upstream /path/to/podo-curriculum-public, or export {ENV_VAR}."
    )


def available(explicit: pathlib.Path | None = None) -> dict[str, pathlib.Path]:
    """Every known language that actually has a content root upstream.

    English exists as a directory long before it exists as a course, so a sync
    over "all languages" has to mean "all the ones that are there" — not a fixed
    list that starts failing the day someone checks out an older authoring tree.
    """
    found: dict[str, pathlib.Path] = {}
    for language in LANGUAGES:
        try:
            found[language] = resolve(explicit, language)
        except UpstreamMissing:
            continue
    return found


def _has_content(candidate: pathlib.Path) -> bool:
    return any((candidate / marker).is_dir() for marker in MARKERS)


def _content_root(candidate: pathlib.Path, language: str) -> pathlib.Path | None:
    """Return one language's content root for the current or legacy layout."""
    # Current: the repository root, holding runtime/ next to the language dirs.
    if (candidate / "runtime").is_dir() and _has_content(candidate / language):
        return candidate / language
    if not _has_content(candidate):
        return None
    # The language directory itself, passed straight to --upstream. Its *name*
    # has to match: a candidate is never accepted for a language it is not,
    # or `--upstream …/korean --language english` would silently sync Korean.
    if candidate.name == language and (candidate.parent / "runtime").is_dir():
        return candidate
    # Legacy: korean/ *was* the repository root, carrying its own runtime/ and
    # no sibling languages. Only the default language ever lived in that shape.
    if language == DEFAULT_LANGUAGE and (candidate / "runtime").is_dir():
        return candidate
    return None


def site_root(content: pathlib.Path) -> pathlib.Path:
    """Root holding the files every language shares, given one content directory."""
    return content.parent if (content.parent / "runtime").is_dir() else content


def runtime_root(content: pathlib.Path) -> pathlib.Path:
    return site_root(content) / "runtime"


def _candidates(explicit: pathlib.Path | None):
    if explicit is not None:
        yield explicit
        return
    env = os.environ.get(ENV_VAR)
    if env:
        yield pathlib.Path(env)
        return
    yield from DEFAULTS
