"""Locate the authoring tree that `sync-from-authoring.py` and
`import-trial-decks.py` read from.

`podo-curriculum-public/korean` is where the Korean decks are written. Shared
files live one level above it at the authoring repository root: `runtime/`,
`viewer.html`, and `ux-philosophy.md`. Older checkouts kept `runtime/` inside
`korean/`; accepting both shapes lets a sync transition without silently reading
the wrong directory. This repo is the deployable form of the same content.

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


class UpstreamMissing(Exception):
    """Raised with a message that says how to fix it, not just what failed."""


def add_argument(parser) -> None:
    parser.add_argument(
        "--upstream",
        type=pathlib.Path,
        default=None,
        help=f"path to the authoring repo or its korean/ directory (or set ${ENV_VAR})",
    )


def resolve(explicit: pathlib.Path | None = None) -> pathlib.Path:
    tried: list[pathlib.Path] = []

    for candidate in _candidates(explicit):
        tried.append(candidate)
        content = _content_root(candidate)
        if content is not None:
            return content.resolve()

    where = "\n  ".join(str(p) for p in tried)
    raise UpstreamMissing(
        "cannot find the authoring tree (a repository with runtime/ and korean/trial/, "
        "or the legacy runtime/ + trial/ layout).\n"
        f"looked in:\n  {where}\n\n"
        f"pass --upstream /path/to/podo-curriculum-public, or export {ENV_VAR}."
    )


def _content_root(candidate: pathlib.Path) -> pathlib.Path | None:
    """Return the Korean content root for the current or legacy layout."""
    if ((candidate / "runtime").is_dir()
            and (candidate / "korean" / "trial").is_dir()):
        return candidate / "korean"
    if ((candidate / "trial").is_dir()
            and ((candidate / "runtime").is_dir()
                 or (candidate.parent / "runtime").is_dir())):
        return candidate
    return None


def site_root(content: pathlib.Path) -> pathlib.Path:
    """Root holding shared site files for a resolved Korean content directory."""
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
