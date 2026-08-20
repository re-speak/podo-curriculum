#!/usr/bin/env python3
"""
The PR gate. Everything that could break a live lesson, checked before merge.

Six layers, cheapest first:

  1. schema      — course.yaml / lesson.yaml against JSON Schema
  2. structure   — slugs match directories, weeks run 1..N
  3. package     — every deck actually builds, with the GCS-flattening audit
  4. contract    — the built HTML through lemonboard's own data-sync validator
  5. runtime     — every pinned shared-runtime URL is live and matches shared/
  6. retirement  — nothing live vanished from courses/ without being switched off

Layer 4 needs network and is skipped without --contract, because the contract is
owned by lemonboard and grape calls the same endpoint at upload time. Running it
here just moves the failure from "someone tried to deploy" to "someone opened a PR".

Layer 5 exists because the shared runtime left the zip. A deck now names a tag on
a public mirror, and the two ways that goes wrong are both silent in class:

  - the tag was never published, so every activity 404s
  - shared/ was edited and the tag was not re-cut, so the deck runs stale code

Both look fine on the author's screen. So the check is: the URL serves, and the
bytes it serves are the bytes in shared/. It fail-opens on network trouble and 5xx
like layer 4 — a CDN blip must not block a PR — but a 404 or a byte mismatch blocks.

Layer 6 exists because apply.py has no delete path. It is a pure upsert: it walks
the courses that exist, posts a manifest, and never reads back from grape. So a
course deleted from this repository does not get retired — its rows keep USE_YN='Y',
keep pointing at GCS content nobody manages any more, and the repository forgets
they exist. The deploy goes green and the learner still sees the course.

Retirement is `enabled: false`, deployed, and only then the directory. That rule is
enforceable without any new grape endpoint, because the previous commit is the
record: compare against the merge base and fail when something that was live is now
absent. `tools/promote.py` enforces the same rule at the only place that removes
lessons; this catches a `courses/` edited by hand, which promote never sees.

There is one legitimate way around it, so there is a way to say so. A course can be
retired **out of band** — the rows deleted and the GCS objects cleaned up directly,
which is the only option when class history hangs off a row and `enabled: false` is
not enough. Declare it with a trailer on any commit in the range:

    Retired-course: courses/kr/intermediate-test

Without an escape hatch a gate that is occasionally wrong gets switched off rather
than used, and the trailer keeps the claim next to the change where a reviewer sees
it — the same reason the plan comment lives on the PR.

    python3 tools/validate.py [--contract] [--env stage] [--base origin/main]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

import yaml

import build
import model

LEMONBOARD_KEY_ENV = "PODO_LEMONBOARD_API_KEY"
REPO = model.REPO


def _fail(message: str) -> int:
    print(f"\u2717 {message}")
    return 1


def check_enabled_is_earned(course: model.Course) -> list[str]:
    """A course cannot be USE_YN='Y' while any lesson is unfinished.

    This is the only place an incomplete lesson fails the build. An unfinished
    lesson in a course that is still disabled is just work in progress — failing
    on it would mean a course could not be committed until it was finished,
    which is the opposite of what a repo is for. plan marks those blocked and
    apply skips them.
    """
    if not course.spec.get("enabled"):
        return []
    if not course.lessons:
        return [f"{course.key}: enabled: true but the course has no lessons"]
    holes = course.incomplete
    if holes:
        names = ", ".join(l.slug for l in holes)
        return [f"{course.key}: enabled: true but these lessons are missing a deck — {names}"]
    return []


def _catalog():
    """build-catalog.py 를 이름 그대로 불러온다 — 하이픈 때문에 import 문이 안 된다."""
    global _CATALOG
    if _CATALOG is None:
        spec = importlib.util.spec_from_file_location(
            "build_catalog", model.REPO / "tools" / "build-catalog.py")
        _CATALOG = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_CATALOG)
    return _CATALOG


_CATALOG = None


def check_catalog_placement(course: model.Course) -> list[str]:
    """이 코스가 공개 카탈로그의 어디에 놓이는지 정해지는가.

    카탈로그는 배포 게이트가 아니다 — .cloudbuild 의 catalog 스텝은 allowFailure 라,
    빌드가 죽어도 교재 배포는 초록으로 지나가고 사이트만 직전 것으로 멈춘다. 그래서
    레벨이나 묶음을 못 정하는 코스가 들어오면 아무도 모르는 채 카탈로그가 낡는다.
    여기서 미리 막아 PR 에서 보이게 한다.

    enabled 인 코스만 본다. 카탈로그는 그것만 싣는다.
    """
    if not course.spec.get("enabled"):
        return []
    cat, problems = _catalog(), []
    for place in (cat.course_level, cat.course_family):
        try:
            place(course)
        except model.ValidationError as exc:
            problems.append(str(exc))
    return problems


def validate_contract(html: str, api: str, label: str, key: str) -> list[str]:
    """Run the built HTML through lemonboard's data-sync contract validator.

    Fail-open on network trouble and 5xx, matching grape's own behaviour
    (class_course_ps.php:342) — an unavailable validator must not block work.
    A 4xx verdict is a real contract violation and does block.

    A response without an `ok` field is treated as a hard failure, not as a pass.
    Grape fail-opens there, but grape is authenticated and interactive; here the
    same case is almost always a bad token, and silently passing would mean the
    contract gate stops running with nobody noticing — which is the exact failure
    mode this repo exists to prevent.
    """
    url = api.rstrip("/") + "/api/v1/lesson-html/validate"
    req = urllib.request.Request(
        url,
        data=json.dumps({"html": html}).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            print(f"  ~ {label}: contract validator unavailable ({exc.code}) — skipped")
            return []
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return [f"{label}: contract validator rejected the request ({exc.code})"]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  ~ {label}: contract validator unreachable ({exc}) — skipped")
        return []

    if payload.get("ok") is True:
        return []

    if "ok" not in payload:
        detail = payload.get("message") or payload.get("code") or json.dumps(payload)[:200]
        return [f"{label}: contract validator did not return a verdict — {detail}"]

    problems = []
    for issue in payload.get("issues", []):
        text = issue.get("message", "unknown contract violation")
        where = issue.get("syncId") or issue.get("rule") or ""
        if issue.get("severity", "error") == "error":
            problems.append(f"{label}: {text}" + (f"  [{where}]" if where else ""))
        else:
            print(f"  ~ {label}: warning — {text}")
    return problems


def pinned_urls(html: str, prefix: str) -> list[str]:
    """Every src=/href= in the built html that points at our shared-runtime host."""
    return [m.group(1) for m in re.finditer(r'\b(?:src|href)="([^"]+)"', html)
            if m.group(1).startswith(prefix)]


def check_runtime_urls(urls: set[str], rt: dict) -> list[str]:
    """Layer 5. Each unique URL: serves, and serves exactly what shared/ holds.

    Fail-open on network trouble and 5xx, matching layer 4 — a jsDelivr blip is not
    a reason nobody can merge. A 404 or a byte mismatch is a real defect and blocks:
    the first means the tag was never published, the second means shared/ moved on
    without the tag being re-cut.
    """
    problems: list[str] = []
    for url in sorted(urls):
        # .../<version>/css/trial.css -> shared/css/trial.css
        rel = "/".join(url.split("/")[-2:])
        local = model.REPO / "shared" / rel
        if not local.is_file():
            problems.append(f"pinned URL has no counterpart in shared/: {url}")
            continue
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                served = resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code >= 500:
                print(f"  ~ runtime: {rel} — CDN unavailable ({exc.code}), skipped")
                continue
            problems.append(
                f"pinned runtime {url} returned {exc.code} — "
                f"publish the tag first (python3 tools/publish-shared.py)")
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"  ~ runtime: {rel} — CDN unreachable ({exc}), skipped")
            continue
        if served != local.read_bytes():
            problems.append(
                f"pinned runtime {url} serves {len(served)} bytes but shared/{rel} "
                f"has {local.stat().st_size} — bump spec.sharedRuntime.version and republish")
        else:
            print(f"  ✓ runtime  — {rel} ({len(served)} bytes, matches shared/)")
    return problems


def declared_retirements(base: str) -> set[str]:
    """Courses a commit in `base..HEAD` claims were retired out of band.

    `enabled: false` then delete is the normal path, but it is not always available:
    when class history hangs off a row, the row cannot be deleted at all and gets
    switched off directly instead. Someone doing that work in the database and in
    GCS has done the retirement properly — they just did not do it through a deploy,
    and nothing in the tree can tell. So they declare it, and the declaration sits in
    the history next to the deletion it explains.
    """
    try:
        log = subprocess.run(["git", "log", "--format=%B", f"{base}..HEAD"],
                             cwd=REPO, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    if log.returncode != 0:
        return set()
    return {line.split(":", 1)[1].strip()
            for line in log.stdout.splitlines()
            if line.strip().startswith("Retired-course:")}


def check_retirements(base: str) -> list[str]:
    """Fail when a course that was `enabled: true` at `base` is gone now.

    Reads the baseline out of git rather than off disk, so it works the same in CI
    (where the branch is checked out fresh) and locally. Anything that stops us
    reading the baseline — a shallow clone, an unknown ref, no git at all — is a
    skip, not a failure: this layer protects against a specific mistake, and it
    must not become a reason a PR cannot be validated at all.
    """
    try:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", base, "courses/"],
            cwd=REPO, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        print(f"\n  ~ retirement — cannot run git; skipped")
        return []
    if listing.returncode != 0:
        print(f"\n  ~ retirement — no baseline at {base}; skipped")
        return []

    was = sorted({line[:line.index("/course.yaml")]
                  for line in listing.stdout.splitlines()
                  if line.endswith("/course.yaml")})
    if not was:
        print(f"\n  ~ retirement — {base} has no courses; skipped")
        return []

    problems: list[str] = []
    gone = [c for c in was if not (REPO / c / "course.yaml").is_file()]
    declared = declared_retirements(base)
    print(f"\nretirement  (vs {base} · {len(was)} course(s) then, {len(gone)} gone now)")

    for course in gone:
        show = subprocess.run(["git", "show", f"{base}:{course}/course.yaml"],
                              cwd=REPO, capture_output=True, text=True, timeout=30)
        if show.returncode != 0:
            continue
        try:
            spec = (yaml.safe_load(show.stdout) or {}).get("spec") or {}
        except yaml.YAMLError:
            continue
        if not spec.get("enabled"):
            print(f"  \u2713 {course} — was already disabled")
        elif course in declared:
            print(f"  \u2713 {course} — was live; declared retired out of band")
        else:
            problems.append(
                f"{course}: was enabled: true at {base} and is gone now — "
                f"deleting it does not retire it. apply.py never removes rows, so "
                f"it stays live in grape pointing at content nobody updates. Set "
                f"enabled: false, let that deploy, then delete the directory. If the "
                f"rows and objects were already cleaned up by hand, say so with a "
                f"`Retired-course: {course}` trailer on a commit in this range.")
            print(f"  \u2717 {course} — was live, now absent")

    if not gone:
        print("  \u2713 nothing removed")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--contract", action="store_true",
                    help="also run each built deck through lemonboard's validator (needs network)")
    ap.add_argument("--env", default="stage", help="which state lock to check against")
    ap.add_argument("--base", default=os.environ.get("PODO_VALIDATE_BASE", "origin/main"),
                    help="git ref to compare against for the retirement check")
    args = ap.parse_args()

    curriculum = model.load_curriculum()
    api = curriculum["spec"]["environments"][args.env]["lemonboardApi"]

    # The validator is authenticated (grape sends the same bearer key from
    # $conf_{dev,prod}_lemonboard_key). Asking for --contract without one would
    # otherwise "pass" every deck on an auth rejection, so refuse up front.
    key = os.environ.get(LEMONBOARD_KEY_ENV, "")
    if args.contract and not key:
        return _fail(f"--contract needs {LEMONBOARD_KEY_ENV} "
                     f"(the lemonboard API key for {args.env}); "
                     f"drop --contract to run every other check")

    try:
        courses = model.discover()
    except model.ValidationError as exc:
        print(f"✗ {exc}")
        return 1

    if not courses:
        print("no courses found under courses/ — nothing to validate")
        return 0

    problems: list[str] = []

    # Layer 5 setup. A deck that still bundles its own runtime simply has no URL on
    # this prefix and is not checked — leaving a course on its bundled copy stays a
    # legitimate choice, it just opts out of the CDN, not out of validation.
    rt = curriculum["spec"].get("sharedRuntime")
    runtime_prefix = rt["baseUrl"].rstrip("/") if rt else None
    want_pin = f"{runtime_prefix}{rt.get('join', '@')}{rt['version']}/" if rt else None
    seen_urls: set[str] = set()

    for course in courses:
        print(f"\n{course.key}  ({course.lang_type} · {course.spec['curriculumType']} · "
              f"{course.spec['countryCode']} · "
              f"level {course.spec['classLevel']} · {len(course.lessons)} lesson(s))")
        problems += check_enabled_is_earned(course)
        problems += check_catalog_placement(course)

        # model 이 이미 검사했다(없는 파일·잘못된 포맷·크기 초과는 여기 오기 전에 죽는다).
        # 남은 일은 보여 주는 것뿐이다 — 표지는 diff 로 확인할 수 없는 몇 안 되는 값이다.
        if course.thumbnail:
            print(f"  ✓ cover    — {course.spec['thumbnail']} "
                  f"({course.thumbnail.stat().st_size // 1024} KB)")

        for lesson in course.lessons:
            for slot, deck in sorted(lesson.decks.items()):
                label = f"{course.key}/{lesson.slug}/{slot}"
                if not deck.exists:
                    print(f"  · {slot:<8} — no deck yet")
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        _, digest = build.package(deck.entry, pathlib.Path(tmp), quiet=True)
                    except build.BuildError as exc:
                        problems.append(f"{label}: {exc}")
                        print(f"  ✗ {slot:<8} — build failed")
                        continue
                    print(f"  ✓ {slot:<8} — {digest[7:19]}")
                    built = (pathlib.Path(tmp) / build.HTML_NAME).read_text(encoding="utf-8")
                    if args.contract:
                        problems += validate_contract(built, api, label, key)
                    if runtime_prefix:
                        for url in pinned_urls(built, runtime_prefix):
                            if not url.startswith(want_pin):
                                problems.append(
                                    f"{label}: pins {url} but curriculum.yaml declares "
                                    f"{rt['version']} — run tools/repoint-shared.py")
                            else:
                                seen_urls.add(url)

    if seen_urls:
        print(f"\nshared runtime  ({rt['version']} · {len(seen_urls)} distinct file(s) pinned)")
        problems += check_runtime_urls(seen_urls, rt)

    problems += check_retirements(args.base)

    print()
    if problems:
        print(f"✗ {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  • {p}")
        return 1

    incomplete = sum(len(c.incomplete) for c in courses)
    if incomplete:
        print(f"✓ valid — but {incomplete} lesson(s) still missing a deck, so they will not deploy")
    else:
        print("✓ valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
