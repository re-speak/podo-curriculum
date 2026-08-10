#!/usr/bin/env python3
"""
Import a learning track's lessons from the authoring tree into a course.

`import-trial-decks.py` moves four hand-listed trial decks. This moves a *track*
— `korean/tracks/<track>/lesson-NNN.html`, of which 2-core-patterns alone plans
116 — so nothing here may require a per-lesson table. Two consequences:

  * **Decks are discovered, not listed.** Every `lesson-NNN.html` in the track is
    a lesson, ordered by its number.
  * **Titles come out of the deck.** Each carries `podo:title-{ko,en,ja}`, written
    by upstream's `tools/new_lesson.py`. A title kept in a table over here would
    drift from the deck it names, and nobody would notice which one was right.

The three transforms a deck needs to survive deployment — static controls,
flattened refs, bundled runtime — are identical to the trial path, so they are
imported from that module rather than restated. Read its docstring for why the
static-control step exists; it is the subtle one, and getting it wrong ships a
deck that works in class and fails the merge gate.

**Weeks are positional, not lesson numbers.** `model._check_weeks` requires
1..N with no gaps, so importing 과 7 and 과 8 gives weeks 1 and 2. The lesson
number stays visible in the slug and in `spec.source`.

**This script owns `lessons/` completely** — it clears the directory each run, so
a deck retired upstream disappears here. It writes `course.yaml` only when absent:
`enabled`, `classLevel` and `tutorGroups` are operational decisions that get made
in review, and regenerating them would quietly revert somebody.

Order, same as the trial path:

    python3 tools/sync-from-authoring.py
    python3 tools/import-track-lessons.py 2-core-patterns
    python3 tools/repoint-shared.py kr/core-patterns-test   # local refs -> pinned CDN
    python3 tools/validate.py --contract --env stage
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import shutil
import sys

import upstream

REPO = upstream.REPO

LESSON_RE = re.compile(r"^lesson-(\d+)\.html$")
TITLE_RE = re.compile(r'<meta name="podo:title-(ko|en|ja)" content="([^"]*)">')
LEVEL_RE = re.compile(r'<meta name="podo:level" content="([^"]*)">')
ID_RE = re.compile(r'<meta name="podo:lesson-id" content="([^"]*)">')
SLUG_OK = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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


# Which authoring track becomes which course. classLevel is part of the natural
# key grape upserts on, so changing one is a new course, not an edit — 999.x is
# the test band (taiken-trial 999.100, hangul-trial-test 999.200).
TRACKS = {
    "2-core-patterns": {
        "course": "core-patterns-test",
        "classLevel": "999.300",
        "curriculumType": "BASIC",
        "difficulty": "BEGINNER",
        "title": {
            "ko": "핵심 문법 패턴 (테스트)",
            "en": "Core grammar patterns (test)",
            "ja": "コア文法パターン（テスト）",
        },
        "description": {
            "ko": "일본어 화자를 위한 핵심 문법 패턴 트랙. 한 과에 패턴 두 개, "
                  "받아들이기에서 발화까지 한 장씩.",
            "ja": "日本語話者のためのコア文法パターン。1課につきパターン2つ、"
                  "受け取るところから話すところまで1ページずつ。",
        },
    },
}

COURSE_YAML = """\
apiVersion: podo.curriculum/v1
kind: Course
metadata:
  # 출처는 beginner-curriculum 의 korean/tracks/{track} — 오소링 트리에서
  # runtime/ 을 공유하던 덱들을, 각자 자기 폴더 안에서 완결되게 평탄화하고
  # 런타임에 승격되던 입력칸을 마크업에 적어 넣은 것이 이 코스다.
  slug: {slug}

spec:
  curriculumType: {curriculum_type}
  # 자연키의 일부다 — 바꾸면 같은 코스의 수정이 아니라 다른 코스가 된다.
  classLevel: "{class_level}"
  lessonTime: 25
  # 검수 전까지는 false. true 로 바꾸는 순간 apply 가 학습자에게 노출시킨다.
  enabled: false
  difficulty: {difficulty}

  title:
    ko: {t_ko}
    en: {t_en}
    ja: {t_ja}

  description:
    ko: {d_ko}
    ja: {d_ja}

  tutorGroups:
    allowRandom: []
    assignedOnly: []

# Scaffolded once by tools/import-track-lessons.py. Not regenerated — enabled,
# classLevel and tutorGroups are review decisions and would be reverted.
"""

LESSON_YAML = """\
apiVersion: podo.curriculum/v1
kind: Lesson
metadata:
  slug: {slug}

spec:
  week: {week}

  title:
    ko: {t_ko}
    en: {t_en}
    ja: {t_ja}

  decks:
    lecture:  {{ entry: lecture/index.html }}
    prestudy: {{ entry: prestudy/index.html }}

  # 덱을 옮겨 온 것이라 teaches/outcome 은 비워 둔다 — 무엇을 가르치는지는
  # 저쪽 toc/{brief} 가 원본이고, 여기 옮겨 적으면 리뷰가 덱이 아니라 이
  # 메타데이터를 검토하게 된다.
  teaches: {{}}
  prerequisites: []
  source: beginner-curriculum korean/tracks/{track}/{source}

# Generated by tools/import-track-lessons.py — edit the deck upstream and re-run.
"""


def read_titles(raw: str, source: str) -> dict[str, str]:
    found = dict(TITLE_RE.findall(raw))
    missing = [k for k in ("ko", "en", "ja") if not found.get(k)]
    if missing:
        raise SystemExit(
            f"✗ {source}: missing <meta name=\"podo:title-{{{','.join(missing)}}}\">.\n"
            f"  The importer builds lesson.yaml from these. Add them upstream, or "
            f"regenerate the deck with tools/new_lesson.py --title-ko/--title-ja/--title-en."
        )
    return {k: v.replace(":", "﹕") for k, v in found.items()}  # keep YAML scalars safe


def discover(track_dir: pathlib.Path) -> list[tuple[int, pathlib.Path]]:
    out = []
    for p in sorted(track_dir.iterdir()):
        m = LESSON_RE.match(p.name)
        if m:
            out.append((int(m.group(1)), p))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("track", nargs="?", default="2-core-patterns",
                    help=f"authoring track name ({', '.join(TRACKS)})")
    upstream.add_argument(ap)
    args = ap.parse_args()

    cfg = TRACKS.get(args.track)
    if cfg is None:
        return _fail(f"unknown track '{args.track}' — add it to TRACKS in this file")

    try:
        src = upstream.resolve(args.upstream)
    except upstream.UpstreamMissing as exc:
        return _fail(str(exc))

    t = _load_trial_module()

    track_dir = src / "tracks" / args.track
    if not track_dir.is_dir():
        return _fail(f"track not found upstream: {track_dir}")

    decks = discover(track_dir)
    if not decks:
        return _fail(
            f"no lesson-NNN.html in {track_dir}\n"
            f"  (sample-lesson.html is the authoring sample, not a deliverable lesson)")

    course = REPO / "courses" / "kr" / cfg["course"]
    print(f"upstream: {src}\ncourse:   {course.relative_to(REPO)}\n")

    course.mkdir(parents=True, exist_ok=True)
    course_yaml = course / "course.yaml"
    if not course_yaml.is_file():
        course_yaml.write_text(COURSE_YAML.format(
            track=args.track, slug=cfg["course"],
            curriculum_type=cfg["curriculumType"], class_level=cfg["classLevel"],
            difficulty=cfg["difficulty"],
            t_ko=cfg["title"]["ko"], t_en=cfg["title"]["en"], t_ja=cfg["title"]["ja"],
            d_ko=cfg["description"]["ko"], d_ja=cfg["description"]["ja"],
        ), encoding="utf-8")
        print(f"  course.yaml scaffolded (enabled: false)\n")

    lessons = course / "lessons"
    if lessons.exists():
        shutil.rmtree(lessons)

    try:
        for week, (number, entry) in enumerate(decks, start=1):
            raw = entry.read_text(encoding="utf-8")
            titles = read_titles(raw, entry.name)
            level = (LEVEL_RE.search(raw) or [None, "?"])[1]

            page, tally = t.statify(raw)
            page, scripts, assets = t.flatten(page)

            # The deck already names itself — `core-07-daily-routine` reads in a
            # directory listing where `07-lesson-007` does not, and it keeps the
            # authoring id and the deployed slug the same string.
            m = ID_RE.search(raw)
            if not m or not SLUG_OK.match(m.group(1)):
                raise SystemExit(
                    f"✗ {entry.name}: podo:lesson-id is missing or not a slug "
                    f"({m.group(1) if m else 'absent'!r}). It becomes the lesson "
                    f"directory name, so it must be lowercase kebab-case.")
            slug = m.group(1)
            lesson = lessons / slug
            lesson.mkdir(parents=True, exist_ok=True)
            (lesson / "lesson.yaml").write_text(LESSON_YAML.format(
                slug=slug, week=week, track=args.track, source=entry.name,
                brief=f"lesson-{number:03d}.md",
                t_ko=titles["ko"], t_en=titles["en"], t_ja=titles["ja"],
            ), encoding="utf-8")

            # Both slots are mandatory — a lesson with only 수업용 leaves
            # PRESTUDY_LEMONBOARD_KEY empty and class creation fails at
            # /rooms/null/duplicate. The same deck fills both.
            for slot in ("lecture", "prestudy"):
                t.build_deck(lesson / slot, page, scripts, assets, src)

            counts = ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) or "none"
            print(f"  week {week}  {slug:<22} {level:<5} controls: {counts:<34} "
                  f"{len(scripts)} script(s), {len(assets)} asset(s)")
    except t.ImportError_ as exc:
        return _fail(str(exc))

    print(f"\n{len(decks)} lesson(s) imported.\nnow run:  "
          f"python3 tools/repoint-shared.py kr/{cfg['course']}\n"
          f"     then python3 tools/validate.py --contract --env stage")
    return 0


def _fail(message: str) -> int:
    print(f"✗ {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
