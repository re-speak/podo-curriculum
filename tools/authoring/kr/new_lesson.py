#!/usr/bin/env python3
"""Stamp an empty deck skeleton for a new lesson.

    python3 tools/authoring/kr/new_lesson.py \
        --track 2-core-patterns --lesson 7 \
        --id core-07-daily-routine \
        --title "저는 매일 운동해요 · 하루 일과" \
        --act "매일 운동해요"

The skeleton is ~70 lines that must be byte-exact every time: the meta block, the
stylesheet links, and shared script bundle whose *load order is load-bearing*
(pager after activities, highlight after the ja→ko tooltips, stamp outside
.phone, …). Hand-copying that is pure downside — it is not creative work and a
silent reorder breaks the deck in ways that only show up on the other person's
screen.

So this does not hold a copy of the skeleton. It reads the track's canonical
deck and lifts the head and foot off it, which means the skeleton can never
drift from the real one and per-track differences (a hangul deck's extra
hangul-activities.js, shared feedback.js, a freetalk deck's freetalk-activities.js) come along for
free. Writing the pages is the only thing left to do. ``--copy-pages`` is the
narrow exception for promoting an already-finished sample into its planned
course slot without re-authoring it.
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

KOREAN = Path(__file__).resolve().parents[3] / "sandbox/drafts/kr"

# the one line at this exact indent is .phone's closing tag — pages are its
# direct children, so everything before the opener and after the closer is frame
PHONE_OPEN = '<div class="phone">'
PHONE_CLOSE_RE = re.compile(r"^  </div>\s*$")
# schemas/lesson.schema.json — metadata.slug. The deck sits in a directory of
# this name, so the id and the directory are one string.
SLUG_RE = re.compile(r"^[0-9]{2,3}-[a-z0-9]+(-[a-z0-9]+)*$")
# every relative ref out of the deck, so depth can be fixed after placement
REL_REF_RE = re.compile(r'((?:href|src)=")(?:\.\./)+(shared|runtime|trial)/')

# Where each ref name actually lives now. The runtime left the language tree
# for the repository root when authoring and deployment became one repo, so a
# ref out to it and a ref out to trial/assets no longer share a depth.
TARGETS = {
    "shared":  lambda repo: repo / "shared",
    "runtime": lambda repo: repo / "shared",
    "trial":   lambda repo: repo / "sandbox/drafts/kr/trial",
}

PLACEHOLDER = """
    <!-- ============================================================
         PAGES GO HERE — one .phone child per page, one activity per page.

         Plan the arc from  lesson-blueprint.md
         Take the content from  {brief}
         Copy component markup and tutor voice from the deck this
         skeleton came from — do not invent components.

         The first page must carry data-act, since the cover that used
         to supply it is a trial-only page and is not here.
         ============================================================ -->
"""


def lesson_brief(track_dir: Path, course: str, lesson_no: int) -> Path:
    """Return the course-scoped brief, with Core's legacy flat path as fallback."""
    scoped = track_dir / "toc" / course / f"lesson-{lesson_no:03d}.md"
    legacy = track_dir / "toc" / f"lesson-{lesson_no:03d}.md"
    return scoped if scoped.exists() or not legacy.exists() else legacy


def split_deck(deck: Path):
    """Return (head, pages, foot) from a canonical deck."""
    lines = deck.read_text(encoding="utf-8").splitlines(keepends=True)

    open_at = next((i for i, l in enumerate(lines) if PHONE_OPEN in l), None)
    if open_at is None:
        sys.exit(f"{deck}: no {PHONE_OPEN} — is this a lesson deck?")

    closes = [i for i, l in enumerate(lines) if PHONE_CLOSE_RE.match(l)]
    if len(closes) != 1:
        sys.exit(
            f"{deck}: expected exactly one '  </div>' closing .phone, found "
            f"{len(closes)}. The deck's indentation changed — fix this script "
            f"rather than guessing a boundary."
        )

    return (
        "".join(lines[: open_at + 1]),
        "".join(lines[open_at + 1 : closes[0]]),
        "".join(lines[closes[0] :]),
    )


def split_skeleton(deck: Path):
    """Return (head, foot) of a canonical deck — everything that isn't pages."""
    head, _, foot = split_deck(deck)
    return head, foot


def course_level(track_dir: Path, course: str) -> str:
    """The Korean level this course's decks must declare.

    It lives as a `# podo:level:` comment in the generated course.yaml rather
    than being passed per lesson. Whether a deck carries kana readings is
    decided by `<meta name="podo:level">`, so a default here would silently ship
    a 왕초급 deck labelled 초급 — and nothing downstream would complain.
    """
    plan = track_dir / "courses" / course / "course.yaml"
    if not plan.is_file():
        sys.exit(f"no course plan at {plan} — run tools/plan_courses.py first")
    m = re.search(r"^\s*#\s*podo:level:\s*(\S+)\s*$", plan.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"{plan} has no '# podo:level:' line — regenerate it with "
                 f"tools/plan_courses.py, or pass --level explicitly")
    return m.group(1)


def find_course(track_dir: Path, lesson_no: int) -> str:
    """Which planned course holds this 과, per plan_courses.py's comments."""
    # plan_courses.py writes one comment line per lesson: "#     6  ·  자음표 전체"
    # (✓ instead of · once a deck exists). Keep this in step with course_yaml().
    marker = re.compile(rf"^#\s+{lesson_no}\s+[·✓]", re.M)
    hits = [c.parent.name for c in sorted((track_dir / "courses").glob("*/course.yaml"))
            if marker.search(c.read_text(encoding="utf-8"))]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"no course plans 과 {lesson_no} — run tools/plan_courses.py first, "
                 f"or pass --course")
    sys.exit(f"과 {lesson_no} appears in several courses ({', '.join(hits)}) — pass --course")


def redepth(page: str, out: Path) -> str:
    """Rewrite `../…/runtime/…` and `../…/trial/…` for wherever the deck landed.

    The skeleton is lifted off a deck at the track root, but lessons live four
    levels deeper under courses/<course>/lessons/<slug>/. Getting this wrong
    gives a deck that renders unstyled with nothing in the console to explain it.

    **The two targets do not sit at the same level.** The runtime lives at the
    repository root under `shared/` so every language shares one copy, while
    `trial/assets/` stays inside the Korean drafts. Counting `../` by hand meant a
    single depth applied to both, which silently 404s one of them — so this
    resolves each ref against where its target actually is instead.
    """
    repo = Path(__file__).resolve().parents[3]

    def fix(m: "re.Match[str]") -> str:
        target = TARGETS[m.group(2)](repo)
        relative = Path(os.path.relpath(target, out.resolve().parent)).as_posix()
        return m.group(1) + relative + "/"

    return REL_REF_RE.sub(fix, page)


def retarget(head: str, *, lesson_id: str, level: str, titles: dict, version: str) -> str:
    """Swap the canonical deck's identity for the new lesson's.

    The three `podo:title-*` metas exist so the deck is self-describing: the
    production importer builds `lesson.yaml` from them rather than from a table
    it has to keep in step with 116 files. A title that lives in two places is a
    title that will disagree with itself.
    """
    subs = [
        (r'(<meta name="podo:lesson-id" content=")[^"]*(")', lesson_id),
        (r'(<meta name="podo:level" content=")[^"]*(")', level),
        (r'(<meta name="podo:content-version" content=")[^"]*(")', version),
        (r"(<title>).*?(</title>)", f"{titles['ko']} — PODO 韓国語"),
    ]
    for pattern, value in subs:
        head, n = re.subn(pattern, lambda m: m.group(1) + value + m.group(2), head, count=1)
        if not n:
            sys.exit(f"skeleton is missing the field matched by {pattern!r} — deck format changed")

    block = "".join(
        f'  <meta name="podo:title-{lang}" content="{titles[lang]}">\n'
        for lang in ("ko", "en", "ja")
    )
    head, n = re.subn(r"([ \t]*<title>)", block + r"\1", head, count=1)
    if not n:
        sys.exit("skeleton has no <title> to anchor the title metas to")
    return head


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--track", required=True, help="e.g. 2-core-patterns")
    ap.add_argument("--lesson", required=True, type=int, help="과 number, e.g. 7")
    ap.add_argument("--course", help="course slug under tracks/<track>/courses/ "
                                     "(default: the course whose plan holds this 과)")
    ap.add_argument("--id", required=True,
                    help="lesson slug AND podo:lesson-id — NN-english-words, e.g. 07-daily-routine. "
                         "NN is the 과 number; the schema requires this shape.")
    ap.add_argument("--title-ko", required=True, help="Korean title; also becomes <title>")
    ap.add_argument("--title-ja", required=True, help="Japanese title — the learner reads this one")
    ap.add_argument("--title-en", required=True, help="English title, for the admin course list")
    ap.add_argument("--level", help="override; normally read from the course plan")
    ap.add_argument("--from-deck", help="deck to lift the skeleton from (default: the track's sample-lesson.html)")
    ap.add_argument(
        "--copy-pages",
        action="store_true",
        help="copy the source deck's existing pages instead of stamping an empty skeleton; "
             "use only to promote an already-finished sample",
    )
    ap.add_argument("--out", help="output path (default: <track>/courses/<course>/lessons/<id>/lesson.html)")
    args = ap.parse_args()

    track_dir = KOREAN / "tracks" / args.track
    if not track_dir.is_dir():
        sys.exit(f"no such track: {track_dir}")

    source = Path(args.from_deck) if args.from_deck else track_dir / "sample-lesson.html"
    if not source.exists():
        sys.exit(f"no canonical deck at {source} — pass --from-deck")

    if not SLUG_RE.match(args.id):
        sys.exit(f"--id '{args.id}' is not a valid lesson slug.\n"
                 f"  Needs NN-english-words (e.g. {args.lesson:02d}-daily-routine); "
                 f"the deck's directory takes this name and the schema enforces it.")
    if not args.id.startswith(f"{args.lesson:02d}-"):
        sys.exit(f"--id '{args.id}' should start with '{args.lesson:02d}-' to match --lesson")

    course = args.course or find_course(track_dir, args.lesson)
    level = args.level or course_level(track_dir, course)
    brief = lesson_brief(track_dir, course, args.lesson)
    if not brief.is_file():
        sys.exit(
            f"no brief for {course} lesson {args.lesson} at {brief} — run "
            f"tools/build_lesson_briefs.py {track_dir} first, and check that "
            f"--course names the course that owns this lesson"
        )
    out = Path(args.out) if args.out else \
        track_dir / "courses" / course / "lessons" / args.id / "lesson.html"
    if out.exists():
        sys.exit(f"{out} already exists — delete it or pass a different --out")
    out.parent.mkdir(parents=True, exist_ok=True)

    head, pages, foot = split_deck(source)
    head = retarget(
        head,
        lesson_id=args.id,
        level=level,
        titles={"ko": args.title_ko, "en": args.title_en, "ja": args.title_ja},
        version=dt.date.today().isoformat(),
    )

    brief_hint = str(brief.relative_to(track_dir))
    body = pages if args.copy_pages else PLACEHOLDER.format(brief=brief_hint)
    page = redepth(head + body + foot, out)
    out.write_text(page, encoding="utf-8")

    broken = [r for r in re.findall(r'(?:href|src)="((?:\.\./)+[^"]+)"', page)
              if not (out.parent / r).resolve().is_file()]
    if broken:
        sys.exit(f"✗ {len(broken)} ref(s) do not resolve from {out}, e.g. {broken[0]}")

    def rel(p: Path) -> str:
        """Repo-relative when possible — --out may point anywhere."""
        try:
            return str(p.resolve().relative_to(KOREAN.parent))
        except ValueError:
            return str(p)

    print(f"wrote {rel(out)}")
    print(f"  skeleton from : {rel(source)}")
    print(f"  now read      : {rel(track_dir / 'lesson-blueprint.md')}")
    print(f"                  {rel(brief)}" + ("" if brief.exists() else "  (missing — run build_lesson_briefs.py)"))
    print(f"                  {rel(source)}  ← voice and components")


if __name__ == "__main__":
    main()
