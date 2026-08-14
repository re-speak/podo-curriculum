#!/usr/bin/env python3
"""Import generated authoring courses into their LANG_TYPE directory.

This is intentionally separate from sync-from-authoring.py. That sync mirrors
runtime, references, and sandbox material; it never makes an ordinary course
deployable. This importer maps the subject directory only:

    korean/tracks/<track>/courses/* -> courses/kr/*
    english/tracks/<track>/courses/* -> courses/en/*

The source course.yaml is copied byte-for-byte. In particular, countryCode is
the learner market and must survive unchanged; LANG_TYPE comes from the `kr` or
`en` destination directory. Only disabled manifests are accepted.

When an authored lesson has both lesson.yaml and lesson.html, it is packaged
into the two downstream deck slots using the existing track-deck transforms.
English currently has no lesson.yaml while prestudy is deferred, so its course
plans import without pretending those prototypes are deployable.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import shutil
import sys
import tempfile

import upstream

REPO = upstream.REPO
COUNTRY_CODE = re.compile(r"^  countryCode:\s*([A-Z]{2})\s*(?:#.*)?$", re.MULTILINE)
ENABLED = re.compile(r"^  enabled:\s*(true|false)\s*(?:#.*)?$", re.MULTILINE)
VALID_COUNTRY_CODES = {"KR", "JP"}


class ImportError_(Exception):
    pass


def _load_trial_module():
    path = pathlib.Path(__file__).parent / "import-trial-decks.py"
    spec = importlib.util.spec_from_file_location("import_trial_decks", path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError_(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["import_trial_decks"] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest(raw: bytes, source: pathlib.Path) -> str:
    text = raw.decode("utf-8")
    countries = COUNTRY_CODE.findall(text)
    if len(countries) != 1:
        raise ImportError_(
            f"{source}: expected exactly one spec.countryCode, found {len(countries)}")
    if countries[0] not in VALID_COUNTRY_CODES:
        raise ImportError_(
            f"{source}: countryCode must be KR or JP, got {countries[0]!r}")
    enabled = ENABLED.findall(text)
    if enabled != ["false"]:
        raise ImportError_(
            f"{source}: authoring imports must contain exactly one enabled: false")
    return countries[0]


def _asset(name: str, content_root: pathlib.Path) -> pathlib.Path:
    site = upstream.site_root(content_root)
    roots = (
        content_root / "trial" / "assets",
        site / "korean" / "trial" / "assets",
        REPO / "shared" / "assets",
    )
    for root in roots:
        hits = sorted(root.rglob(name)) if root.is_dir() else []
        if hits:
            return hits[0]
    raise ImportError_(f"asset not found: {name}")


def _build_deck(target: pathlib.Path, page: str, scripts: list[str], assets: list[str],
                content_root: pathlib.Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(page, encoding="utf-8")
    runtime = upstream.runtime_root(content_root)
    for sheet in ("lesson-card.css", "trial.css"):
        shutil.copyfile(runtime / "css" / sheet, target / sheet)
    for name in scripts:
        origin = ((REPO / "tools" / "deck-runtime" / "activities.js")
                  if name == "activities.js" else runtime / "js" / name)
        if not origin.is_file():
            raise ImportError_(f"script not found: {origin}")
        shutil.copyfile(origin, target / name)
    for name in assets:
        shutil.copyfile(_asset(name, content_root), target / name)


def import_course(plan: pathlib.Path, destination_root: pathlib.Path,
                  content_root: pathlib.Path, trial) -> tuple[str, int]:
    raw = plan.read_bytes()
    country_code = validate_manifest(raw, plan)
    cslug = plan.parent.name

    with tempfile.TemporaryDirectory(prefix=f"import-{cslug}-") as tmp:
        staged = pathlib.Path(tmp) / cslug
        staged.mkdir()
        (staged / "course.yaml").write_bytes(raw)

        lesson_count = 0
        lessons = plan.parent / "lessons"
        for deck in sorted(lessons.glob("*/lesson.html")) if lessons.is_dir() else []:
            manifest = deck.parent / "lesson.yaml"
            if not manifest.is_file():
                continue
            page, _tally = trial.statify(deck.read_text(encoding="utf-8"))
            page, scripts, assets = trial.flatten(page)
            out = staged / "lessons" / deck.parent.name
            out.mkdir(parents=True)
            shutil.copyfile(manifest, out / "lesson.yaml")
            for slot in ("lecture", "prestudy"):
                _build_deck(out / slot, page, scripts, assets, content_root)
            lesson_count += 1

        destination = destination_root / cslug
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(staged, destination)

    if (destination / "course.yaml").read_bytes() != raw:  # pragma: no cover
        raise ImportError_(f"{destination}: course.yaml changed during import")
    return country_code, lesson_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("track", help="authoring track name, e.g. 2-core-patterns")
    parser.add_argument("--language", choices=upstream.LANGUAGES, default="korean")
    parser.add_argument("--course", action="append", help="limit to a slug; repeatable")
    upstream.add_argument(parser)
    args = parser.parse_args()

    try:
        content = upstream.resolve(args.upstream, args.language)
        course_root = content / "tracks" / args.track / "courses"
        plans = sorted(course_root.glob("*/course.yaml")) if course_root.is_dir() else []
        if args.course:
            wanted = set(args.course)
            plans = [plan for plan in plans if plan.parent.name in wanted]
        if not plans:
            raise ImportError_(f"no matching course.yaml under {course_root}")

        code = upstream.LANGUAGES[args.language]
        destination = REPO / "courses" / code
        destination.mkdir(parents=True, exist_ok=True)
        trial = _load_trial_module()
        for plan in plans:
            country, lessons = import_course(plan, destination, content, trial)
            print(f"{code} · {plan.parent.name} · countryCode {country} · "
                  f"{lessons} deployable lesson(s)")
    except (upstream.UpstreamMissing, ImportError_, UnicodeDecodeError) as exc:
        print(f"✗ {exc}")
        return 1

    print("\nnow run: python3 tools/repoint-shared.py && "
          "python3 tools/validate.py --contract --env stage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
