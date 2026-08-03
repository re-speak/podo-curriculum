#!/usr/bin/env python3
"""
Push the repo's desired state at grape, one course per request, then record
what came back in the state lock.

Grape stays the only writer. It already owns the S3 upload, the lemonboard room
lifecycle and the GT_CLASS_COURSE / le_tutor_curriculum writes; re-implementing
any of that here would mean two codebases drifting apart with production between
them. So this tool builds zips, states what it wants, and lets grape do it.

The request/response contract lives in docs/sync-contract.md. Nothing here works
until that endpoint exists — see the README's "current status".

    python3 tools/apply.py --env stage [--dry-run] [--only kr/hangul-lv1]

Auth comes from PODO_CURRICULUM_SYNC_TOKEN.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import pathlib
import sys
import tempfile
import urllib.error
import urllib.request
import uuid

import build
import model
import plan as plan_mod

TOKEN_ENV = "PODO_CURRICULUM_SYNC_TOKEN"


class ApplyError(Exception):
    pass


def build_manifest(curriculum: dict, course: model.Course, tracked: dict | None) -> tuple[dict, dict]:
    """The desired state of one course, plus the zips that go with it.

    Known ids from the state lock ride along so grape updates the rows it made
    last time instead of inserting a second copy of the course.
    """
    lang_cfg = curriculum["spec"]["languages"][course.lang]
    tracked = tracked or {}
    tracked_lessons = tracked.get("lessons", {}) or {}

    lessons = []
    zips: dict[str, pathlib.Path] = {}
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="curriculum-"))

    for lesson in course.lessons:
        if lesson.incomplete:
            print(f"  ! {lesson.slug}: skipped — missing {', '.join(lesson.incomplete)} deck")
            continue

        known = tracked_lessons.get(lesson.slug, {})
        known_digests = known.get("digest", {}) or {}
        entry = {
            "slug": lesson.slug,
            "week": lesson.week,
            "title": lesson.spec["title"],
            "courseRowId": known.get("courseRowId"),
            "decks": {},
        }

        for slot, deck in sorted(lesson.decks.items()):
            zip_path, digest = build.package(deck.entry, tmpdir / lesson.slug / slot, quiet=True)
            unchanged = known_digests.get(slot) == digest
            entry["decks"][slot] = {
                "digest": digest,
                "unchanged": unchanged,          # grape skips the S3 write when true
                "roomKey": (known.get("lemonboard", {}) or {}).get(slot),
            }
            if not unchanged:
                zips[f"{lesson.slug}::{slot}"] = zip_path

        lessons.append(entry)

    manifest = {
        "apiVersion": "podo.curriculum/v1",
        "classType": curriculum["spec"]["classType"],
        "bookFormat": curriculum["spec"]["bookFormat"],
        "langType": lang_cfg["langType"],
        "course": {
            "slug": course.slug,
            "key": course.key,
            "coverId": tracked.get("coverId"),
            "curriculumType": course.spec["curriculumType"],
            "curriculumTypeKey": course.curriculum_type_key,
            "classLevel": course.spec["classLevel"],
            "lessonTime": course.spec["lessonTime"],
            "useYn": "Y" if course.spec.get("enabled") else "N",
            "difficulty": course.spec.get("difficulty", ""),
            "title": course.spec["title"],
            "description": course.spec.get("description", {}),
            "tutorGroups": course.spec.get("tutorGroups", {}),
        },
        "lessons": lessons,
    }
    return manifest, zips


def encode_multipart(manifest: dict, zips: dict[str, pathlib.Path]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    buf = io.BytesIO()

    def part(headers: str, payload: bytes):
        buf.write(f"--{boundary}\r\n{headers}\r\n\r\n".encode("utf-8"))
        buf.write(payload)
        buf.write(b"\r\n")

    part('Content-Disposition: form-data; name="manifest"\r\n'
         'Content-Type: application/json; charset=utf-8',
         json.dumps(manifest, ensure_ascii=False).encode("utf-8"))

    for key, path in sorted(zips.items()):
        lesson_slug, slot = key.split("::")
        part(f'Content-Disposition: form-data; name="zip[{lesson_slug}][{slot}]"; '
             f'filename="{lesson_slug}-{slot}.zip"\r\n'
             'Content-Type: application/zip',
             path.read_bytes())

    buf.write(f"--{boundary}--\r\n".encode("utf-8"))
    return buf.getvalue(), f"multipart/form-data; boundary={boundary}"


def post(url: str, manifest: dict, zips: dict[str, pathlib.Path], token: str) -> dict:
    body, content_type = encode_multipart(manifest, zips)
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": content_type, "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1500]
        raise ApplyError(f"grape returned {exc.code}\n{detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ApplyError(f"grape unreachable: {exc}") from exc


def record(state: dict, course: model.Course, manifest: dict, result: dict) -> None:
    """Fold grape's response back into the lock.

    Digests come from the manifest, not the response — they describe what we
    built and sent, so they are only truthful if we are the ones writing them.
    """
    returned = result["course"]
    entry = state["courses"].setdefault(course.key, {})
    entry["coverId"] = returned["coverId"]
    lessons = entry.setdefault("lessons", {})

    sent = {l["slug"]: l for l in manifest["lessons"]}
    for slug, info in returned.get("lessons", {}).items():
        row = lessons.setdefault(slug, {})
        row["courseRowId"] = info["courseRowId"]
        row["lemonboard"] = info.get("lemonboard", {})
        digest = row.setdefault("digest", {})
        for slot, deck in sent.get(slug, {}).get("decks", {}).items():
            digest[slot] = deck["digest"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", required=True)
    ap.add_argument("--only", help="apply a single course key, e.g. kr/hangul-lv1")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and print the manifest; send nothing")
    args = ap.parse_args()

    curriculum = model.load_curriculum()
    env_cfg = curriculum["spec"]["environments"][args.env]
    token = os.environ.get(TOKEN_ENV, "")
    if not token and not args.dry_run:
        sys.exit(f"{TOKEN_ENV} is not set")

    courses = [c for c in model.discover() if args.only in (None, c.key)]
    if not courses:
        sys.exit(f"no course matched {args.only!r}" if args.only else "no courses to apply")

    print(plan_mod.render(plan_mod.plan(args.env)))
    print()

    state = model.load_state(args.env)
    state.setdefault("courses", {})
    failures = 0

    for course in courses:
        print(f"→ {course.key}")
        manifest, zips = build_manifest(curriculum, course, state["courses"].get(course.key))

        if args.dry_run:
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
            print(f"  (dry run) would send {len(zips)} zip(s)")
            continue

        try:
            result = post(env_cfg["grapeSyncApi"], manifest, zips, token)
        except ApplyError as exc:
            print(f"  ✗ {exc}")
            failures += 1
            continue

        if not result.get("ok"):
            for err in result.get("errors", ["unknown error"]):
                print(f"  ✗ {err}")
            failures += 1
            continue

        for warning in result.get("warnings", []):
            print(f"  ~ {warning}")
        record(state, course, manifest, result)
        print(f"  ✓ cover {result['course']['coverId']} · "
              f"{len(result['course'].get('lessons', {}))} lesson row(s) · "
              f"{len(zips)} deck(s) uploaded")

    if not args.dry_run:
        # Written even on partial failure — the courses that did land must stay
        # tracked, or the retry creates duplicates of them.
        model.save_state(args.env, state)
        print(f"\nstate/{args.env}.lock.yaml updated")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
