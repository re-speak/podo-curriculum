"""Locate the authoring tree that `sync-from-authoring.py` and
`import-trial-decks.py` read from.

`beginner-curriculum/korean` is where the decks are written. It is a different
kind of tree from this one: every deck reaches one shared `runtime/`, nothing is
packaged, and it is edited continuously. This repo is the deployable form of the
same content. Keeping the path resolution in one place means neither tool
hardcodes somebody's laptop layout.

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
#   ~/Documents/podo_work/beginner-curriculum     <- upstream
DEFAULTS = (
    REPO.parent.parent / "podo_work" / "beginner-curriculum" / "korean",
    REPO.parent / "beginner-curriculum" / "korean",
)


class UpstreamMissing(Exception):
    """Raised with a message that says how to fix it, not just what failed."""


def add_argument(parser) -> None:
    parser.add_argument(
        "--upstream",
        type=pathlib.Path,
        default=None,
        help=f"path to beginner-curriculum/korean (or set ${ENV_VAR})",
    )


def resolve(explicit: pathlib.Path | None = None) -> pathlib.Path:
    tried: list[pathlib.Path] = []

    for candidate in _candidates(explicit):
        tried.append(candidate)
        if (candidate / "runtime").is_dir() and (candidate / "trial").is_dir():
            return candidate.resolve()

    where = "\n  ".join(str(p) for p in tried)
    raise UpstreamMissing(
        "cannot find the authoring tree (a directory holding runtime/ and trial/).\n"
        f"looked in:\n  {where}\n\n"
        f"pass --upstream /path/to/beginner-curriculum/korean, or export {ENV_VAR}."
    )


def _candidates(explicit: pathlib.Path | None):
    if explicit is not None:
        yield explicit
        return
    env = os.environ.get(ENV_VAR)
    if env:
        yield pathlib.Path(env)
        return
    yield from DEFAULTS
