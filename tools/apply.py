#!/usr/bin/env python3
"""
Push the repo's desired state at grape, one course per request.

Nothing is remembered between runs. grape resolves each row by its natural key
(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK),
so this tool never has to carry ids forward — which means no lock file, and no
write-back step whose failure turns the next run into a duplicate course.

Grape stays the only writer. It already owns the GCS upload, the lemonboard room
lifecycle and the GT_CLASS_COURSE / le_tutor_curriculum writes; re-implementing
any of that here would mean two codebases drifting apart with production between
them. So this tool builds zips, states what it wants, and lets grape do it.

The request/response contract lives in docs/sync-contract.md.

    python3 tools/apply.py --env stage [--dry-run] [--only kr/hangul-lv1]

Auth is a Google OIDC ID token in PODO_CURRICULUM_SYNC_TOKEN — the deploy build
mints it off the metadata server, so there is no stored secret.
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


def build_manifest(curriculum: dict, course: model.Course) -> tuple[dict, dict]:
    """The desired state of one course, plus the zips that go with it.

    No ids ride along. grape resolves a row by its natural key
    (CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK),
    so nothing here has to remember what the last apply created — and there is no
    lock file to write back, which is what used to turn a failed apply into a
    duplicate course on the next run.
    """
    lang_cfg = curriculum["spec"]["languages"][course.lang]

    lessons = []
    zips: dict[str, pathlib.Path] = {}
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="curriculum-"))

    for lesson in course.lessons:
        if lesson.incomplete:
            print(f"  ! {lesson.slug}: skipped — missing {', '.join(lesson.incomplete)} deck")
            continue

        entry = {
            "slug": lesson.slug,
            "week": lesson.week,
            "title": lesson.spec["title"],
            "decks": {},
        }

        for slot, deck in sorted(lesson.decks.items()):
            zip_path, digest = build.package(deck.entry, tmpdir / lesson.slug / slot, quiet=True)
            # 매번 보낸다. digest 로 스킵하려면 지난번 값을 어딘가 기억해야 하는데, 그 기억이
            # 바로 없애려는 state lock 이다. 덱은 코스 전체가 십수 MB 라 매번 올려도 싸고,
            # 같은 키 덮어쓰기라 룸도 살아남는다.
            entry["decks"][slot] = {"digest": digest, "unchanged": False}
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

    failures = 0

    for course in courses:
        print(f"→ {course.key}")
        manifest, zips = build_manifest(curriculum, course)

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
        print(f"  ✓ cover {result['course']['coverId']} · "
              f"{len(result['course'].get('lessons', {}))} lesson row(s) · "
              f"{len(zips)} deck(s) uploaded")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
