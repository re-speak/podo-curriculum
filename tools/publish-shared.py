#!/usr/bin/env python3
"""
Publish `shared/{css,js}` to the public mirror as an immutable tag.

Decks do not carry their own copy of the shared runtime any more; they point at
`spec.sharedRuntime` in curriculum.yaml. That URL has to be live *before* a deck
referencing it ships, so this is a step an author runs, not something CI does on
merge. A merge-triggered publisher would invert the order and leave a window where
`main` holds decks pointing at a tag nobody pushed yet — 404 at class time, silent,
on the learner's screen only.

    publish  →  repoint decks  →  PR  →  merge

Nothing here is automated for the same reason nothing stores a token: it uses your
own git credentials, so there is no secret to rotate (docs/sync-contract.md).

Tags are immutable. Re-running with the same version and the same content is a
no-op; re-running with the same version and *different* content is an error, not
a force-push — a deck already pinned to that tag would silently change underneath
a live class.

    python3 tools/publish-shared.py [--dry-run]
"""

from __future__ import annotations

import argparse
import filecmp
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

import model

# `assets` joined css and js when the Korean catalogue landed. Every deck ships as
# one flat GCS prefix, so an image used by 500 lessons was copied 500 times: two
# avatars alone accounted for 191 MB of a 320 MB tree, and every deploy pushed all
# of it to every environment again. The runtime had already solved this — the same
# immutable tag now carries the images that `shared/` owns.
#
# Only what shared/ owns moves. A lesson-specific image stays in its deck, and
# `repoint-shared.py` keeps a local copy whose bytes differ from shared's even when
# the basename matches.
MIRRORED = ("css", "js", "assets")


class PublishError(Exception):
    pass


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise PublishError(f"{' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def tree_differs(a: pathlib.Path, b: pathlib.Path) -> list[str]:
    """Names that differ between two directories, compared by content."""
    names = {p.name for p in a.iterdir() if p.is_file()} | \
            {p.name for p in b.iterdir() if p.is_file()} if a.is_dir() and b.is_dir() else set()
    if not a.is_dir():
        return ["<missing in published tag>"]
    if not b.is_dir():
        return sorted(p.name for p in a.iterdir() if p.is_file())
    out = []
    for name in sorted(names):
        pa, pb = a / name, b / name
        if not pa.is_file() or not pb.is_file() or not filecmp.cmp(pa, pb, shallow=False):
            out.append(name)
    return out


def verify_cdn(base: str, join: str, version: str, rel: str, local: pathlib.Path) -> str:
    """Fetch one published file and compare bytes. Proves the whole chain, not just the push."""
    url = f"{base.rstrip('/')}{join}{version}/{rel}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            served = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        return f"  ~ CDN not serving {rel} yet ({exc}) — tags can take a moment to propagate"
    if served != local.read_bytes():
        return f"  ✗ {url}\n    served {len(served)} bytes, local has {local.stat().st_size} — MISMATCH"
    return f"  ✓ {url}  ({len(served)} bytes, matches local)"


def purge_latest(shared: pathlib.Path, repo: str) -> None:
    """`@latest` 를 보는 소비자를 위해 엣지 캐시를 비운다.

    덱은 태그를 고정해 보므로 이 함수가 필요 없다. 필요한 쪽은 원톡 상담 안내다 —
    코스 카드를 `@latest` 로 받아 가는데(podo-app `course-card-asset.ts`), 그 별칭은
    jsDelivr 엣지에서 12시간 캐시된다. 비우지 않으면 새로 구운 카드가 반나절 동안
    학생에게 닿지 않는다.

    실패해도 발행 자체는 이미 끝났으므로 경고만 남기고 넘어간다 — 12시간 뒤에는
    어차피 저절로 새 파일이 나간다.
    """
    cards = sorted((shared / "assets").glob("course-card-*.png"))
    if not cards:
        return

    print()
    for card in cards:
        path = f"/gh/{repo}@latest/assets/{card.name}"
        try:
            with urllib.request.urlopen(f"https://purge.jsdelivr.net{path}", timeout=20) as response:
                ok = json.loads(response.read()).get("status") == "finished"
            print(f"purged  : {card.name}" if ok else f"purge?  : {card.name} (엣지가 아직 비우는 중)")
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            print(f"purge!  : {card.name} — {error} (12시간 뒤 저절로 갱신됩니다)", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="say what would be pushed, touch nothing")
    args = ap.parse_args()

    try:
        curriculum = model.load_curriculum()
    except model.ValidationError as exc:
        print(f"✗ {exc}")
        return 1

    rt = curriculum["spec"].get("sharedRuntime")
    if not rt:
        print("✗ curriculum.yaml has no spec.sharedRuntime — nothing to publish")
        return 1

    repo, version = rt["repo"], rt["version"]
    base, join = rt["baseUrl"], rt.get("join", "@")
    shared = model.REPO / "shared"
    url = f"https://github.com/{repo}.git"

    print(f"mirror  : {repo}")
    print(f"version : {version}")
    print(f"source  : shared/{{{','.join(MIRRORED)}}}")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        clone = pathlib.Path(tmp) / "mirror"
        try:
            run(["git", "clone", "--quiet", url, str(clone)])
        except PublishError as exc:
            print(f"✗ cannot clone {url}\n{exc}")
            return 1

        tags = run(["git", "tag", "--list"], cwd=clone).split()

        # ---- already published? then this must be a no-op, or a version bump ----
        if version in tags:
            run(["git", "checkout", "--quiet", f"tags/{version}"], cwd=clone)
            drift = []
            for sub in MIRRORED:
                drift += [f"{sub}/{n}" for n in tree_differs(shared / sub, clone / sub)]
            if not drift:
                print(f"✓ {version} is already published and matches shared/ — nothing to do")
                for sub, rel in (("css", "css/trial.css"), ("js", "js/activities.js")):
                    if (shared / rel).is_file():
                        print(verify_cdn(base, join, version, rel, shared / rel))
                return 0
            print(f"✗ tag {version} already exists but shared/ has changed since it was cut:")
            for d in drift:
                print(f"    {d}")
            print()
            print("  Tags are immutable on purpose — a deck already pinned to this tag would")
            print("  change underneath a live class. Bump spec.sharedRuntime.version in")
            print("  curriculum.yaml, then run this again.")
            return 1

        # ---- new tag ----
        for sub in MIRRORED:
            dst = clone / sub
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(shared / sub, dst)

        changed = run(["git", "status", "--porcelain"], cwd=clone)
        files = sorted(p.name for sub in MIRRORED for p in (shared / sub).iterdir() if p.is_file())

        if args.dry_run:
            print(f"would publish {len(files)} file(s) and tag {version}:")
            for line in (changed.splitlines() or ["  (mirror already matches shared/)"]):
                print(f"  {line}")
            print(f"\n(dry run — nothing pushed)")
            return 0

        if changed:
            run(["git", "add", "-A"], cwd=clone)
            run(["git", "-c", "user.email=podo@day1company.co.kr",
                 "-c", "user.name=podo-curriculum",
                 "commit", "--quiet", "-m",
                 f"chore: podo-curriculum/shared 를 {version} 으로 미러한다"], cwd=clone)
            run(["git", "push", "--quiet", "origin", "HEAD:main"], cwd=clone)
            print(f"pushed  : {len(changed.splitlines())} change(s) to main")
        else:
            print("pushed  : nothing — mirror main already matches shared/")

        run(["git", "tag", version], cwd=clone)
        run(["git", "push", "--quiet", "origin", version], cwd=clone)
        print(f"tagged  : {version}")
        print()

        for rel in ("css/trial.css", "js/activities.js"):
            if (shared / rel).is_file():
                print(verify_cdn(base, join, version, rel, shared / rel))

        purge_latest(shared, repo)

    print()
    print(f"✓ published. Now repoint the decks:  python3 tools/repoint-shared.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
