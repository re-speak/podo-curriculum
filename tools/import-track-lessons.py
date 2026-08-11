#!/usr/bin/env python3
"""
Import a learning track's courses from the authoring tree.

Upstream now lays its tracks out in this repo's own shape — `tools/plan_courses.py`
over there cuts a track into courses against the table of contents and writes
`course.yaml` / `lesson.yaml` that already validate against `schemas/`. So this
tool **copies a plan rather than inventing one**, and the only work left is the
three transforms a deck needs to survive deployment.

    korean/tracks/<track>/courses/<course>/course.yaml
                                 /lessons/<slug>/lesson.yaml
                                 /lessons/<slug>/lesson.html

becomes

    courses/kr/<course>/course.yaml
                       /lessons/<slug>/lesson.yaml
                       /lessons/<slug>/{lecture,prestudy}/index.html

That is deliberately a different division of labour from `import-trial-decks.py`,
which owns four hand-listed decks and generates their metadata here. A track is
116 lessons; metadata generated on this side would need a table kept in step with
the authoring tree, and the two would disagree the first week nobody looked.

The deck transforms — static controls, flattened refs, bundled runtime — are
identical to the trial path and are imported from that module. Read its docstring
for why the static-control step exists; it is the subtle one, and getting it wrong
ships a deck that works in class and fails the merge gate.

**`course.yaml` is copied only when absent.** `enabled`, `classLevel` and
`tutorGroups` are decisions made in review over here; re-copying would revert
whoever made them. A drift is reported instead.

**Only lessons with a deck cross over.** Upstream plans the whole course in
`course.yaml` comments, but a lesson without `lesson.html` has no slug and
nothing to deploy. Weeks therefore run 1..N over what exists, which is what
`model._check_weeks` requires.

Order:

    python3 tools/sync-from-authoring.py
    python3 tools/import-track-lessons.py 2-core-patterns
    python3 tools/repoint-shared.py                    # local refs -> pinned CDN
    python3 tools/validate.py --contract --env stage
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import shutil
import sys

import upstream

REPO = upstream.REPO

# Test courses stay grouped at the bottom of courses/kr even when their source
# plan uses its original production-shaped slug.
COURSE_ALIASES = {
    "hangul-starter": "test-hangul-starter",
}


class CourseManifestError(Exception):
    pass


def _manifest_bytes(plan: pathlib.Path, source_slug: str, dest_slug: str) -> bytes:
    data = plan.read_bytes()
    if source_slug == dest_slug:
        return data

    old = f"  slug: {source_slug}\n".encode()
    if data.count(old) != 1:
        raise CourseManifestError(
            f"{plan}: expected exactly one metadata slug for {source_slug}"
        )
    return data.replace(old, f"  slug: {dest_slug}\n".encode(), 1)


def _load_trial_module():
    """Import `import-trial-decks.py` despite the hyphens in its name.

    Loading it rather than copying its transforms is the point: statify() in
    particular encodes why lemonboard's static validator needs real controls in
    the markup, and a second copy of that reasoning would rot out of step.
    """
    path = pathlib.Path(__file__).parent / "import-trial-decks.py"
    spec = importlib.util.spec_from_file_location("import_trial_decks", path)
    if spec is None or spec.loader is None:              # pragma: no cover
        sys.exit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["import_trial_decks"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("track", nargs="?", default="2-core-patterns",
                    help="authoring track name, e.g. 2-core-patterns")
    ap.add_argument("--course", action="append",
                    help="limit to these course slugs (repeatable)")
    upstream.add_argument(ap)
    args = ap.parse_args()

    try:
        src = upstream.resolve(args.upstream)
    except upstream.UpstreamMissing as exc:
        return _fail(str(exc))

    t = _load_trial_module()

    courses_dir = src / "tracks" / args.track / "courses"
    if not courses_dir.is_dir():
        return _fail(
            f"no courses/ in {src / 'tracks' / args.track}\n"
            f"  Run this upstream first:  python3 korean/tools/plan_courses.py "
            f"korean/tracks/{args.track}")

    plans = sorted(p for p in courses_dir.glob("*/course.yaml"))
    if args.course:
        plans = [p for p in plans if p.parent.name in set(args.course)]
    if not plans:
        return _fail("no matching course.yaml upstream")

    print(f"upstream: {src}\ntrack:    {args.track}\n")
    total_lessons = 0

    try:
        for plan in plans:
            cslug = plan.parent.name
            dest_slug = COURSE_ALIASES.get(cslug, cslug)
            dest = REPO / "courses" / "kr" / dest_slug
            dest.mkdir(parents=True, exist_ok=True)

            here = dest / "course.yaml"
            planned_manifest = _manifest_bytes(plan, cslug, dest_slug)
            if not here.is_file():
                here.write_bytes(planned_manifest)
                note = "course.yaml copied (enabled: false)"
            elif here.read_bytes() != planned_manifest:
                note = "course.yaml differs — kept ours (enabled/tutorGroups are review decisions)"
            else:
                note = "course.yaml in step"

            decks = sorted(p for p in (plan.parent / "lessons").glob("*/lesson.html")) \
                if (plan.parent / "lessons").is_dir() else []

            lessons_dir = dest / "lessons"
            if lessons_dir.exists():
                shutil.rmtree(lessons_dir)

            if not decks:
                print(f"  {dest_slug:<28} no decks written yet — {note}")
                continue

            print(f"  {dest_slug:<28} {note}")
            for deck in decks:
                slug = deck.parent.name
                lyaml = deck.parent / "lesson.yaml"
                if not lyaml.is_file():
                    raise t.ImportError_(
                        f"{slug}: lesson.html without lesson.yaml — re-run "
                        f"plan_courses.py upstream")

                page, tally = t.statify(deck.read_text(encoding="utf-8"))
                page, scripts, assets = t.flatten(page)

                out = lessons_dir / slug
                out.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(lyaml, out / "lesson.yaml")

                # Both slots are mandatory — a lesson with only 수업용 leaves
                # PRESTUDY_LEMONBOARD_KEY empty and class creation fails at
                # /rooms/null/duplicate. The same deck fills both.
                for slot in ("lecture", "prestudy"):
                    t.build_deck(out / slot, page, scripts, assets, src)

                counts = ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) or "none"
                print(f"    {slug:<26} controls: {counts:<34} "
                      f"{len(scripts)} script(s), {len(assets)} asset(s)")
                total_lessons += 1
    except (t.ImportError_, CourseManifestError) as exc:
        return _fail(str(exc))

    print(f"\n{total_lessons} lesson(s) across {len(plans)} course(s).\n"
          f"now run:  python3 tools/repoint-shared.py\n"
          f"     then python3 tools/validate.py --contract --env stage")
    return 0


def _fail(message: str) -> int:
    print(f"✗ {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
