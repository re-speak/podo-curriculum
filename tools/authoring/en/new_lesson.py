#!/usr/bin/env python3
"""Stamp an empty English lesson from an approved canonical deck.

The tool copies only the deck shell: metadata, shared styles, ``.phone`` frame,
pager and load-order-bearing scripts. It never copies lesson pages and never
overwrites an existing file.
"""

from __future__ import annotations

import argparse
import datetime as dt
from html.parser import HTMLParser
import os
import pathlib
import re


ENGLISH = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
REPO = pathlib.Path(__file__).resolve().parents[3]
PHONE_OPEN = '<div class="phone">'
PHONE_CLOSE = re.compile(r"^  </div>\s*$")
SLUG = re.compile(r"^(\d{2,3})-[a-z0-9]+(?:-[a-z0-9]+)*$")
REL_SHARED = re.compile(r'((?:href|src)=")(?:(?:\.\./)+)(shared|runtime|korean|kr)/')
FEEDBACK_SCRIPT = re.compile(
    r'^[ \t]*<script src="(?:\.\./)+shared/js/feedback\.js"></script>[ \t]*\n?',
    re.MULTILINE,
)
ACTIVITIES_SCRIPT = re.compile(
    r'^(?P<indent>[ \t]*)<script src="(?P<shared>(?:\.\./)+shared)/js/activities\.js"></script>[ \t]*$',
    re.MULTILINE,
)


class FeedbackControlParser(HTMLParser):
    """Find live data-fb controls, excluding inert markup-shaped text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.found = False
        self.template_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "template":
            self.template_depth += 1
            return
        if not self.template_depth and any(name == "data-fb" for name, _ in attrs):
            self.found = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.template_depth and tag != "template" and any(name == "data-fb" for name, _ in attrs):
            self.found = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "template" and self.template_depth:
            self.template_depth -= 1


def has_feedback_control(page: str) -> bool:
    parser = FeedbackControlParser()
    parser.feed(page)
    parser.close()
    return parser.found

# Where each ref name actually lives now that authoring and deployment share a
# repository: the runtime at the root under shared/, the language trees under
# the sandbox.
TARGETS = {
    "shared": "shared",
    "runtime": "shared",
    "korean": "sandbox/drafts/kr",
    "kr": "sandbox/drafts/kr",
}
PLACEHOLDER = """

    <!-- ============================================================
         PAGES GO HERE — one .phone child per page, one activity per page.

         Plan the arc from lesson-blueprint.md.
         Take curriculum content and sequence guardrails from {brief}.
         Copy component composition and tutor voice from the canonical deck;
         never invent a new shared component inside a lesson assignment.
         ============================================================ -->

"""

CANONICAL_DECKS = {
    "1-core-patterns": pathlib.Path(
        "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
    ),
    "2-contextual-english": pathlib.Path(
        "courses/ctx-travel-arrivals-transport/lessons/01-check-in-and-request-a-seat/lesson.html"
    ),
}


def split_shell(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    body = next((i for i, line in enumerate(lines) if re.match(r"^<body>\s*$", line)), None)
    opened = next((i for i, line in enumerate(lines) if PHONE_OPEN in line), None)
    closes = [i for i, line in enumerate(lines) if PHONE_CLOSE.match(line)]
    if body is None or opened is None or len(closes) != 1 or closes[0] <= opened:
        raise ValueError("canonical deck no longer has one recognisable <body> / .phone shell")
    # Deliberately omit canonical lesson comments between <body> and .phone.
    head = "".join(lines[:body + 1]) + "  " + PHONE_OPEN + "\n"
    foot = "".join(lines[closes[0]:])
    return head, foot


def attr(value: str) -> str:
    """Escape only what a double-quoted HTML attribute cannot hold literally."""
    return value.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def retarget(head: str, *, review_id: str, lesson_id: str, level: str, title: str,
             title_ko: str, title_ja: str, version: str) -> str:
    # podo:title-{ko,en,ja} is the deck's name in GT_CLASS_COURSE's three name
    # columns, and the app picks one by the learner's locale — so `ja` is the
    # one this Japanese-market track puts on screen. Stamping all three here is
    # what keeps a written deck from reaching the catalogue unnamed.
    substitutions = [
        (r'(<meta name="podo:lesson-id" content=")[^"]*(")', lesson_id),
        (r'(<meta name="podo:review-id" content=")[^"]*(")', review_id),
        (r'(<meta name="podo:level" content=")[^"]*(")', level),
        (r'(<meta name="podo:content-version" content=")[^"]*(")', version),
        (r'(<meta name="podo:title-ko" content=")[^"]*(")', attr(title_ko)),
        (r'(<meta name="podo:title-en" content=")[^"]*(")', attr(title)),
        (r'(<meta name="podo:title-ja" content=")[^"]*(")', attr(title_ja)),
        (r"(<title>).*?(</title>)", title + " — PODO English"),
    ]
    for pattern, value in substitutions:
        head, count = re.subn(pattern, lambda m: m.group(1) + value + m.group(2), head, count=1)
        if count != 1:
            raise ValueError(f"canonical deck is missing required identity field {pattern!r}")
    # Vocabulary is editorial lesson content, not shell content. Keep the four
    # category slots but force the writer to classify the new deck from zero.
    head, count = re.subn(
        r'(<meta name="podo:vocabulary:(?:new|recycled|assumed|receptive)" content=")[^"]*(")',
        r"\1\2",
        head,
    )
    if count != 4:
        raise ValueError(f"canonical deck has {count} vocabulary categories, expected 4")
    head, count = re.subn(
        r'(<meta name="podo:vocabulary-status" content=")[^"]*(")',
        r"\1todo\2",
        head,
        count=1,
    )
    if count != 1:
        raise ValueError("canonical deck is missing podo:vocabulary-status")
    return head


def redepth(page: str, out: pathlib.Path) -> str:
    # feedback.js owns only ``data-fb`` controls.  Canonical Core and
    # Contextual pilots use those controls, but their footer is also the shell
    # for generated decks whose bodies often do not.  Resolve the optional
    # runtime only after the final body exists so a content-specific pilot
    # script cannot leak into every generated lesson.
    page = FEEDBACK_SCRIPT.sub("", page)
    if has_feedback_control(page):
        activities = ACTIVITIES_SCRIPT.search(page)
        if not activities:
            raise ValueError("data-fb control requires activities.js before feedback.js")
        feedback = (
            f'{activities.group("indent")}<script src="{activities.group("shared")}'
            '/js/feedback.js"></script>'
        )
        page = page[:activities.end()] + "\n" + feedback + page[activities.end():]

    def replace(match: re.Match) -> str:
        target = REPO / TARGETS[match.group(2)]
        relative = pathlib.Path(os.path.relpath(target, out.parent)).as_posix()
        return match.group(1) + relative + "/"
    return REL_SHARED.sub(replace, page)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", required=True, choices=("1-core-patterns", "2-contextual-english", "3-freetalking"))
    parser.add_argument("--review-id", required=True, help="stable TOC id, e.g. CORE-31")
    parser.add_argument("--course", required=True, help="provisional course directory")
    parser.add_argument("--lesson", required=True, type=int)
    parser.add_argument("--id", required=True, help="directory and podo:lesson-id, e.g. 31-past-action")
    parser.add_argument("--title", required=True,
                        help="English deck title; must match the generated brief heading")
    parser.add_argument("--title-ko", required=True,
                        help="Korean title — grape's admin label for this lesson")
    parser.add_argument("--title-ja", required=True,
                        help="Japanese title — what a JP-market learner sees in the catalogue")
    parser.add_argument("--level", required=True, help="podo:level value")
    parser.add_argument(
        "--from-deck",
        help="approved canonical lesson.html; Core and Contextual default to their approved pilots",
    )
    parser.add_argument("--out", help="override output lesson.html")
    args = parser.parse_args()

    match = SLUG.fullmatch(args.id)
    if not match or int(match.group(1)) != args.lesson:
        parser.error(f"--id must start with lesson {args.lesson:02d} (for example {args.lesson:02d}-useful-name)")
    expected_prefix = {"1-core-patterns": "CORE", "2-contextual-english": "CTX", "3-freetalking": "FT"}[args.track]
    if args.review_id != f"{expected_prefix}-{args.lesson}":
        parser.error(f"--review-id must be {expected_prefix}-{args.lesson} for this track and lesson")

    track = ENGLISH / "tracks" / args.track
    brief = track / "toc" / f"{args.review_id}.md"
    if not brief.is_file():
        parser.error(f"missing generated brief {brief}; run build_lesson_briefs.py first")
    if args.from_deck:
        source = pathlib.Path(args.from_deck)
    elif args.track in CANONICAL_DECKS:
        source = track / CANONICAL_DECKS[args.track]
    else:
        parser.error(
            "Freetalking has two approved language-load shells; pass the matching "
            "accessible or full canonical deck with --from-deck"
        )
    if not source.is_file():
        parser.error(f"canonical deck not found: {source}")

    out = pathlib.Path(args.out) if args.out else track / "courses" / args.course / "lessons" / args.id / "lesson.html"
    if out.exists():
        parser.error(f"refusing to overwrite existing deck: {out}")

    head, foot = split_shell(source.read_text(encoding="utf-8"))
    head = retarget(
        head,
        review_id=args.review_id,
        lesson_id=args.id,
        level=args.level,
        title=args.title,
        title_ko=args.title_ko,
        title_ja=args.title_ja,
        version=dt.date.today().isoformat(),
    )
    page = redepth(head + PLACEHOLDER.format(brief=brief.relative_to(track)) + foot, out)
    if re.search(r'<script\b[^>]*\bsrc="[^"]*yomi\.js"', page, re.I) or re.search(
        r'class="[^"]*\byomi\b[^"]*"', page, re.I
    ):
        parser.error("canonical shell contains forbidden English yomi support")
    refs = re.findall(r'(?:href|src)="((?:\.\./)+[^"#]+)"', page)
    broken = [ref for ref in refs if not (out.parent / ref).resolve().is_file()]
    if broken:
        parser.error(f"generated shell has {len(broken)} broken reference(s), first: {broken[0]}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    print(f"  shell: {source.relative_to(REPO) if source.is_relative_to(REPO) else source}")
    print(f"  brief: {brief.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
