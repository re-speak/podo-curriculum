#!/usr/bin/env python3
"""
Push the repo's desired state at grape, one course per request.

Nothing is remembered between runs. grape resolves each row by its natural key
(CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK,
COUNTRY_CODE),
so this tool never has to carry ids forward — which means no lock file, and no
write-back step whose failure turns the next run into a duplicate course.

Grape stays the only writer. It already owns the GCS upload, the lemonboard room
lifecycle and the GT_CLASS_COURSE / le_tutor_curriculum writes; re-implementing
any of that here would mean two codebases drifting apart with production between
them. So this tool builds zips, states what it wants, and lets grape do it.

The request/response contract lives in docs/sync-contract.md.

    python3 tools/apply.py --env stage [--dry-run] [--only kr/hangul-lv1] [--jobs 4]

Auth is a Google OIDC ID token in PODO_CURRICULUM_SYNC_TOKEN — the deploy build
mints it off the metadata server, so there is no stored secret.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
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

# 코스는 서로 독립이고 요청도 코스당 하나라(docs/sync-contract.md), 순서대로 보낼 이유가
# 없다. 한 코스가 5초쯤 걸리는데 그 시간은 grape 안에서 GCS·레몬보드를 기다리는 시간이라
# 이쪽에서는 소켓만 잡고 있다 — 56 코스를 줄 세우면 그 대기가 그대로 합산된다.
#
# 기본값을 낮게 잡은 이유는 받는 쪽이다. 비프로덕션 grape 는 replica 1 · CPU 1 이고
# prod 도 2 뿐이며, prod grape 는 어드민 사용자도 함께 받는다. 배포가 어드민을 밀어내면
# 아낀 몇 분보다 비싸다.
DEFAULT_JOBS = 4


class ApplyError(Exception):
    pass


def build_manifest(curriculum: dict, course: model.Course, log=print
                   ) -> tuple[dict, dict, pathlib.Path | None]:
    """The desired state of one course, plus the zips and cover that go with it.

    No ids ride along. grape resolves a row by its natural key
    (CLASS_TYPE, LANG_TYPE, CURRICULUM_TYPE, LESSON_TIME, CLASS_LEVEL, CLASS_WEEK,
    COUNTRY_CODE),
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
            log(f"  ! {lesson.slug}: skipped — missing {', '.join(lesson.incomplete)} deck")
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
            "countryCode": course.spec["countryCode"],
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

    # 표지는 있으면 보내고 없으면 아무 말도 하지 않는다. 빈 값을 보내 "표지 없음"을
    # 주장하지 않는 것이 핵심이다 — grape 는 파트가 왔을 때만 BOOK_THUMBNAIL 을 쓰므로,
    # 레포가 모르는 표지(어드민에서 올린 것)가 배포로 지워지는 경로가 아예 없다.
    #
    # 매니페스트의 항목은 사람이 읽는 기록이다. 업로드 여부를 가르는 것은 cover 파트의
    # 존재 자체이고, 여기 digest 는 배포 로그에서 "그때 무엇이 올라갔나"를 답한다.
    cover = course.thumbnail
    if cover is not None:
        manifest["course"]["thumbnail"] = {
            "file": course.spec["thumbnail"],
            "digest": "sha256:" + hashlib.sha256(cover.read_bytes()).hexdigest(),
        }

    return manifest, zips, cover


def encode_multipart(manifest: dict, zips: dict[str, pathlib.Path],
                     cover: pathlib.Path | None) -> tuple[bytes, str]:
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

    if cover is not None:
        # 파일명은 검증된 확장자로 다시 짓는다. grape 는 이름을 쓰지 않고 확장자를 바이트로
        # 판정하므로 잃는 것이 없고, 반대로 보낸 이름을 그대로 실으면 따옴표가 섞인 파일명
        # 하나가 multipart 헤더를 깨뜨린다 — 문자 제한은 스키마에만 있고, jsonschema 가 없는
        # 환경에서는 그 검사가 통째로 건너뛰어진다(model.check_schema).
        part('Content-Disposition: form-data; name="cover"; '
             f'filename="cover{cover.suffix.lower()}"\r\n'
             'Content-Type: application/octet-stream',
             cover.read_bytes())

    buf.write(f"--{boundary}--\r\n".encode("utf-8"))
    return buf.getvalue(), f"multipart/form-data; boundary={boundary}"


def post(url: str, manifest: dict, zips: dict[str, pathlib.Path],
         cover: pathlib.Path | None, token: str) -> dict:
    body, content_type = encode_multipart(manifest, zips, cover)
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


def apply_course(curriculum: dict, course: model.Course, url: str, token: str,
                 dry_run: bool) -> tuple[bool, list[str]]:
    """Send one course. Returns (ok, the lines to print for it).

    Nothing is printed from here. Courses go out concurrently, so a print in the
    middle of one would land in the middle of another; collecting the lines and
    printing them together keeps each course's block intact and in course order.
    """
    lines = [f"→ {course.key}"]
    manifest, zips, cover = build_manifest(curriculum, course, log=lines.append)

    if dry_run:
        lines.append(json.dumps(manifest, indent=2, ensure_ascii=False))
        lines.append(f"  (dry run) would send {len(zips)} zip(s)"
                     + (f" and the cover {cover.name}" if cover else ""))
        return True, lines

    try:
        result = post(url, manifest, zips, cover, token)
    except ApplyError as exc:
        lines.append(f"  ✗ {exc}")
        return False, lines

    if not result.get("ok"):
        for err in result.get("errors", ["unknown error"]):
            lines.append(f"  ✗ {err}")
        return False, lines

    for warning in result.get("warnings", []):
        lines.append(f"  ~ {warning}")
    lines.append(f"  ✓ cover {result['course']['coverId']} · "
                 f"{len(result['course'].get('lessons', {}))} lesson row(s) · "
                 f"{len(zips)} deck(s) uploaded")
    # 표지를 보냈는데 URL 이 안 돌아오면 업로드가 실패한 것이다. grape 는 그걸 경고로
    # 처리하므로(코스 동기화 자체는 성공) 여기서 눈에 띄게 적어 둔다.
    if cover is not None:
        thumb = result["course"].get("thumbnail")
        lines.append(f"  ✓ cover image → {thumb}" if thumb
                     else "  ~ cover image was sent but grape reported no URL — see warnings")
    return True, lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", required=True)
    ap.add_argument("--only", help="apply a single course key, e.g. kr/hangul-lv1")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and print the manifest; send nothing")
    ap.add_argument("--jobs", type=int, default=DEFAULT_JOBS,
                    help=f"courses to send concurrently (default {DEFAULT_JOBS}); "
                         f"1 sends them one at a time")
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

    # dry run 은 코스마다 매니페스트를 통째로 찍는다. 동시에 돌 이유가 없고, 한 줄씩
    # 읽히는 편이 낫다.
    jobs = 1 if args.dry_run else max(1, min(args.jobs, len(courses)))
    if jobs > 1:
        print(f"({len(courses)} courses, {jobs} in flight)\n")

    def run(course: model.Course) -> tuple[bool, list[str]]:
        return apply_course(curriculum, course, env_cfg["grapeSyncApi"], token, args.dry_run)

    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        # map 은 제출 순서대로 돌려준다 — 동시에 나가도 로그는 코스 순서 그대로 남는다.
        # flush 는 빌드 로그 때문이다: 파이프로 나가면 파이썬이 블록 버퍼링이라, 없으면
        # 5분치 출력이 마지막에 한꺼번에 떨어져 어디서 멈췄는지 보이지 않는다.
        for ok, lines in pool.map(run, courses):
            print("\n".join(lines), flush=True)
            if not ok:
                failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
