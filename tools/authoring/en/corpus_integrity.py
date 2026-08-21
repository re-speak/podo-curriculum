#!/usr/bin/env python3
"""Audit cross-deck English corpus contracts without trusting batch generators."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
import os
import pathlib
import re
import sys
from urllib.parse import urlsplit


REPO = pathlib.Path(__file__).resolve().parents[3]
TRACKS = REPO / "sandbox/drafts/en/tracks"
TRACK_NAMES = {
    "1-core-patterns": "CORE",
    "2-contextual-english": "CTX",
    "3-freetalking": "FT",
}
SUPERSEDED_PROTOTYPE = (
    "2-contextual-english/courses/arriving-and-getting-settled/lessons/"
    "01-the-room-is-fine-but/lesson.html"
)
REVIEW_ID = re.compile(r"^(CORE|CTX|FT)-([1-9][0-9]*)$", re.ASCII)
ENTRY_FLOOR = re.compile(r"^- \*\*Entry floor:\*\* Core (\d+)\s*$", re.M)
TOKEN = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
INERT = {"head", "script", "style", "template", "noscript"}
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

EXPECTED_ACTIVE_NUMBERS = {
    "1-core-patterns": frozenset(range(1, 123)) - frozenset({4, 5, 6}),
    "2-contextual-english": frozenset(range(1, 61)),
    "3-freetalking": frozenset(range(1, 122)),
}

# These are the only pre-stable Freetalking articles.  Each waiver is bound to
# both a physical path and its logical review id.  It waives only claim ids:
# status, row count, option ids, vocabulary, feedback and uniqueness remain
# mandatory, and a waived article must contain *zero* claim ids.
LEGACY_FT_CLAIM_WAIVERS = {
    **{
        f"3-freetalking/courses/talk-between-two-countries-{variant}/lessons/"
        f"{number:02d}-{slug}/lesson.html": f"FT-{number}"
        for variant in ("accessible", "full")
        for number, slug in (
            (1, "this-surprised-me"),
            (2, "what-people-get-wrong-about-japan"),
            (3, "a-japanese-food-everyone-should-try"),
            (4, "a-table-manner-that-differs"),
            (5, "a-place-you-would-show-a-visitor"),
            (6, "a-word-that-doesnt-translate-neatly"),
            (7, "japan-does-especially-well"),
            (8, "how-you-spend-new-years-day"),
        )
    },
    **{
        f"3-freetalking/courses/talk-me-lately-{variant}/lessons/"
        "09-a-purchase-that-was-worth-it/lesson.html": "FT-9"
        for variant in ("accessible", "full")
    },
    **{
        f"3-freetalking/courses/talk-people-and-ties-{variant}/lessons/"
        "49-how-accurate-is-your-mbti/lesson.html": "FT-49"
        for variant in ("accessible", "full")
    },
}

# Cross-variant category/load differences are normal.  A same-spelling row with
# different Japanese, however, is a different sense and must be reviewed
# explicitly.  Production starts with no waivers; exact exception sets can be
# injected into isolated audits/tests and, if ever approved, added here as an
# explicit corpus decision.
FT_PAIR_SENSE_EXCEPTIONS: frozenset[
    tuple[str, str, tuple[str, str, str], tuple[str, str, str]]
] = frozenset()

FT_SCRIPT_SEQUENCE = (
    "activities.js",
    "feedback.js",
    "freetalk-activities.js",
    "pager.js",
    "script-lines.js",
    "spotlight.js",
    "tutor-notes.js",
    "highlight.js",
    "stamp.js",
)

# Productive matching is whole-token/whole-phrase.  Only documented alternates
# belong here; a substring or an arbitrary object inserted into a phrasal verb
# is never inferred.
PHRASE_ALTERNATIVES: dict[str, tuple[str, ...]] = {
    "push back": ("push it back", "pushed it back", "pushing it back"),
    "documentary": ("documentaries",),
    "fall through": ("fell through", "falls through", "fallen through"),
    "make up": ("made up", "makes up", "making up"),
    "plan": ("plans", "planned", "planning"),
    "delay": ("delays", "delayed", "delaying"),
    "turn out": ("turns out", "turned out", "turning out"),
    "would rather": ("i'd rather", "we'd rather", "they'd rather", "you'd rather"),
    "would rather not": ("i'd rather not", "we'd rather not", "they'd rather not", "you'd rather not"),
    "handover": ("handovers",),
    "binge-watch": ("binge-watches", "binge-watched", "binge-watching"),
    "recommendation": ("recommendations",),
    "assumption": ("assumptions",),
    "expectation": ("expectations",),
    "passport": ("passports",),
    "small win": ("small wins",),
    "overplay": ("overplays", "overplayed", "overplaying"),
    "rewatch": ("rewatches", "rewatched", "rewatching"),
    "inherit": ("inherits", "inherited", "inheriting"),
    "break up": ("breaks up", "broke up", "broken up", "breaking up"),
    "lock in": ("locks in", "locked in", "locking in"),
    "declare": ("declares", "declared", "declaring"),
    "fit": ("fits", "fitted", "fitting"),
    "not getting better": ("isn't getting better", "wasn't getting better"),
    "do not": ("don't",),
    "does not": ("doesn't",),
    "did not": ("didn't",),
    "it is": ("it's",),
    "we are": ("we're",),
    "we have": ("we've",),
    "would not": ("wouldn't",),
    "could not": ("couldn't",),
    "should not": ("shouldn't",),
}


@dataclass(frozen=True)
class VocabEntry:
    english: str
    japanese: str
    source: str | None = None


@dataclass
class ParsedDeck:
    path: pathlib.Path
    audit_root: pathlib.Path
    relative: str
    track: str
    review_id: str
    number: int
    curriculum_status: str
    lesson_ids: list[str]
    proofread_statuses: list[str]
    vocabulary_statuses: list[str]
    categories: dict[str, list[VocabEntry]]
    productive_text: str
    ids: dict[str, list[str]]
    feedback_controls: list[str]
    script_events: list[ScriptEvent]
    article_rows: list[dict[str, str]]

    @property
    def superseded(self) -> bool:
        return self.curriculum_status == "superseded"


@dataclass
class _Frame:
    tag: str
    classes: set[str]
    attrs: dict[str, str]
    page_id: str | None
    hidden: bool


@dataclass
class ScriptEvent:
    position: int
    src: str | None
    attrs: tuple[tuple[str, str], ...]
    startend: bool
    closed: bool = False


class _DeckHTMLParser(HTMLParser):
    """Parse only live HTML tags and visible text; inert markup stays inert."""

    def __init__(self, track: str) -> None:
        super().__init__(convert_charrefs=True)
        self.track = track
        self.stack: list[_Frame] = []
        self.metas: dict[str, list[str]] = defaultdict(list)
        self.ids: dict[str, list[str]] = defaultdict(list)
        self.feedback_controls: list[str] = []
        self.script_events: list[ScriptEvent] = []
        self.article_rows: list[dict[str, str]] = []
        self.productive_parts: list[str] = []
        self.event_index = 0
        self._handling_startend = False
        self._open_scripts: list[ScriptEvent | None] = []

    def _inside(self, tag: str | None = None, class_name: str | None = None) -> bool:
        return any(
            (tag is None or frame.tag == tag)
            and (class_name is None or class_name in frame.classes)
            for frame in self.stack
        )

    def _page_id(self) -> str | None:
        for frame in reversed(self.stack):
            if frame.page_id:
                return frame.page_id
        return None

    def _inert(self) -> bool:
        return any(frame.tag in INERT or frame.hidden for frame in self.stack)

    def _tutor_private(self) -> bool:
        return any(
            "tutor-note" in frame.classes
            or "tn-more" in frame.classes
            or "teacher-only" in frame.classes
            for frame in self.stack
        )

    def _japanese_support(self) -> bool:
        return any(
            frame.classes.intersection({"translation", "ja", "j", "title-ja", "task", "target"})
            for frame in self.stack
        )

    def _learner_zone(self) -> bool:
        classes = set().union(*(frame.classes for frame in self.stack)) if self.stack else set()
        if classes.intersection({
            "korean", "k", "choice", "opt", "word-choice-sentence",
            "answer-label", "answer-fill", "hint-chip", "sent-hero",
            "sent-more", "model-line", "known-row", "bt-ex", "ending",
            "ask", "prompt", "question", "reorder-list", "build-zone",
        }):
            return True
        return any(frame.attrs.get("data-sync-option") is not None for frame in self.stack)

    def _productive_prompt(self) -> bool:
        page_id = self._page_id() or ""
        production_page = (
            page_id.endswith("-write")
            or page_id.endswith("-freetalk")
            or page_id in {"live", "p3-freetalk"}
        )
        return production_page and self._inside(class_name="section-subtitle") and self._inside(class_name="ko")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.event_index += 1
        attr = {name.casefold(): value or "" for name, value in attrs}
        classes = set(attr.get("class", "").split())
        inert_before = self._inert()
        metadata_blocked = any(
            frame.tag in {"script", "style", "template", "noscript"} or frame.hidden
            for frame in self.stack
        )
        normalized_style = re.sub(r"\s+", "", attr.get("style", ""), flags=re.UNICODE).casefold()
        hidden = (
            "hidden" in attr
            or "inert" in attr
            or attr.get("aria-hidden", "").strip().casefold() == "true"
            or "display:none" in normalized_style
            or "visibility:hidden" in normalized_style
            or bool(classes.intersection({"answer-key", "answer-reveal", "sr-only", "visually-hidden"}))
        )

        if tag == "meta" and not metadata_blocked and not hidden:
            name = attr.get("name")
            if name:
                self.metas[name].append(attr.get("content", ""))

        # Script execution is not content visibility: a script under <head> or
        # a hidden/inert container still executes.  Only parser-fallback
        # containers that suppress execution (template/noscript) are ignored.
        script_blocked = any(frame.tag in {"template", "noscript"} for frame in self.stack)
        script_event: ScriptEvent | None = None
        if tag == "script" and not script_blocked:
            script_event = ScriptEvent(
                position=self.event_index,
                src=attr.get("src") or None,
                attrs=tuple((name.casefold(), value or "") for name, value in attrs),
                startend=self._handling_startend,
            )
            self.script_events.append(script_event)
        if tag == "script" and not self._handling_startend:
            self._open_scripts.append(script_event)

        if not inert_before and tag != "template":
            if not hidden:
                for key, bucket in (
                    ("data-page-id", "page"),
                    ("data-sync-id", "sync"),
                    ("data-fb", "feedback"),
                    ("data-claim-id", "claim"),
                ):
                    if key in attr:
                        self.ids[bucket].append(attr[key])
            if "data-fb" in attr and not hidden:
                self.feedback_controls.append(attr["data-fb"])
            page_id = attr.get("data-page-id") or self._page_id()
            if (
                self.track == "3-freetalking"
                and page_id == "article"
                and tag == "div"
                and "sent" in classes
                and not hidden
            ):
                self.article_rows.append({
                    "option": attr.get("data-sync-option", ""),
                    "claim": attr.get("data-claim-id", ""),
                })

        frame = _Frame(
            tag=tag,
            classes=classes,
            attrs=attr,
            page_id=attr.get("data-page-id"),
            hidden=hidden,
        )
        if tag not in VOID:
            self.stack.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._handling_startend = True
        self.handle_starttag(tag, attrs)
        self._handling_startend = False
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            event = self._open_scripts.pop() if self._open_scripts else None
            if event is not None:
                event.closed = True
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if (
            not data.strip()
            or self._inert()
            or self._inside(class_name="s-words")
            or self._tutor_private()
        ):
            return
        if self.track == "3-freetalking":
            page_id = self._page_id()
            in_article = page_id == "article" and self._inside(class_name="s-line")
            in_question = (
                page_id in {"warm-1", "warm-2", *(f"q{i}" for i in range(1, 7))}
                and self._inside("p", "ask")
                and self._inside("span", "ko")
            )
            if in_article or in_question:
                self.productive_parts.append(data)
            return

        in_other_turn = self._inside(class_name="other") and self._inside(class_name="turn")
        if (
            not in_other_turn
            and not self._japanese_support()
            and (self._learner_zone() or self._productive_prompt())
        ):
            self.productive_parts.append(data)


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(token.replace("’", "'").casefold() for token in TOKEN.findall(value))


def phrase_forms(term: str, alternatives: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    """Return exact reviewed whole-token forms; never guess morphology."""
    base = _tokens(term)
    forms = {base}
    for value in (*PHRASE_ALTERNATIVES.get(term.casefold(), ()), *alternatives):
        tokens = _tokens(value)
        if tokens:
            forms.add(tokens)
    return {form for form in forms if form}


def phrase_visible(term: str, text: str, alternatives: tuple[str, ...] = ()) -> bool:
    """Match a productive term as a whole phrase, never as a substring."""
    haystack = _tokens(text)
    for needle in phrase_forms(term, alternatives):
        width = len(needle)
        if any(haystack[index:index + width] == needle for index in range(len(haystack) - width + 1)):
            return True
    return False


def _parse_vocab_entries(raw: str, category: str, label: str) -> tuple[list[VocabEntry], list[str]]:
    entries: list[VocabEntry] = []
    errors: list[str] = []
    for item in filter(None, (part.strip() for part in raw.split(";"))):
        fields = [part.strip() for part in item.split("|")]
        wanted = 3 if category == "recycled" else 2
        if len(fields) != wanted or any(not field for field in fields):
            errors.append(f"{label}: malformed {category} vocabulary entry {item!r}")
            continue
        source = fields[2] if category == "recycled" else None
        if source and not REVIEW_ID.fullmatch(source):
            errors.append(f"{label}: recycled owner {source!r} is not a stable review id")
        entries.append(VocabEntry(fields[0], fields[1], source))
    return entries, errors


def parse_deck(
    path: pathlib.Path,
    source: str,
    *,
    tracks_root: pathlib.Path = TRACKS,
    audit_root: pathlib.Path | None = None,
) -> tuple[ParsedDeck | None, list[str]]:
    audit_root = (audit_root or tracks_root.parents[3]).resolve()
    try:
        relative_path = path.relative_to(tracks_root)
    except ValueError:
        relative_path = path
    relative = relative_path.as_posix()
    parts = relative_path.parts
    track = parts[0] if parts else ""
    label = relative
    errors: list[str] = []
    if track not in TRACK_NAMES:
        return None, [f"{label}: unknown English track"]
    parser = _DeckHTMLParser(track)
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:  # HTMLParser failures should identify the deck.
        return None, [f"{label}: HTML parse failed: {exc}"]

    review_values = parser.metas.get("podo:review-id", [])
    if len(review_values) != 1 or not REVIEW_ID.fullmatch(review_values[0]):
        return None, [f"{label}: expected exactly one valid podo:review-id"]
    review_id = review_values[0]
    prefix, raw_number = REVIEW_ID.fullmatch(review_id).groups()
    if prefix != TRACK_NAMES[track]:
        errors.append(f"{label}: {review_id} does not match track {track}")

    lesson_dir = parts[-2] if len(parts) >= 2 else ""
    expected_prefix = f"{int(raw_number):02d}"
    if not re.fullmatch(
        re.escape(expected_prefix) + r"-[a-z0-9]+(?:-[a-z0-9]+)*",
        lesson_dir,
        re.ASCII,
    ):
        errors.append(f"{label}: lesson path number/slug does not match {review_id}")
    lesson_ids = parser.metas.get("podo:lesson-id", [])
    if len(lesson_ids) != 1 or lesson_ids[0] != lesson_dir:
        errors.append(f"{label}: expected exactly one podo:lesson-id matching {lesson_dir!r}")

    curriculum = parser.metas.get("podo:curriculum-status", [])
    if len(curriculum) > 1:
        errors.append(f"{label}: duplicate podo:curriculum-status metadata")
    curriculum_status = curriculum[0] if curriculum else "active"
    if curriculum_status not in {"active", "superseded"}:
        errors.append(f"{label}: unknown podo:curriculum-status {curriculum_status!r}")

    categories: dict[str, list[VocabEntry]] = {}
    for category in ("new", "recycled", "assumed", "receptive"):
        values = parser.metas.get(f"podo:vocabulary:{category}", [])
        if len(values) != 1:
            errors.append(f"{label}: expected exactly one podo:vocabulary:{category} meta")
            categories[category] = []
            continue
        categories[category], entry_errors = _parse_vocab_entries(values[0], category, label)
        errors.extend(entry_errors)

    seen_categories: dict[str, str] = {}
    for category, entries in categories.items():
        local: set[str] = set()
        for entry in entries:
            key = entry.english.casefold()
            if key in local:
                errors.append(f"{label}: duplicate {category} vocabulary entry {entry.english!r}")
            local.add(key)
            if key in seen_categories and seen_categories[key] != category:
                errors.append(
                    f"{label}: {entry.english!r} appears in both "
                    f"{seen_categories[key]} and {category} vocabulary"
                )
            seen_categories.setdefault(key, category)

    return ParsedDeck(
        path=path,
        audit_root=audit_root,
        relative=relative,
        track=track,
        review_id=review_id,
        number=int(raw_number),
        curriculum_status=curriculum_status,
        lesson_ids=lesson_ids,
        proofread_statuses=parser.metas.get("podo:proofread-status", []),
        vocabulary_statuses=parser.metas.get("podo:vocabulary-status", []),
        categories=categories,
        productive_text=" ".join(parser.productive_parts),
        ids=dict(parser.ids),
        feedback_controls=parser.feedback_controls,
        script_events=parser.script_events,
        article_rows=parser.article_rows,
    ), errors


def discover(tracks_root: pathlib.Path = TRACKS) -> list[pathlib.Path]:
    return sorted(
        path for path in tracks_root.glob("*/courses/*/lessons/*/lesson.html")
        if "_archive" not in path.parts
    )


def _canonical_shared_script_name(deck: ParsedDeck, src: str) -> str | None:
    """Resolve an external runtime src to this audit root's exact shared file."""
    expected_by_src = {
        os.path.relpath(
            (deck.audit_root / "shared" / "js" / filename).resolve(),
            deck.path.parent.resolve(),
        ).replace(os.sep, "/"): filename
        for filename in FT_SCRIPT_SEQUENCE
    }
    filename = expected_by_src.get(src)
    if filename is None:
        return None
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not parsed.path:
        return None
    if parsed.path.startswith("/") or "\\" in parsed.path:
        return None
    expected = (deck.audit_root / "shared" / "js" / filename).resolve()
    expected_rel = os.path.relpath(expected, deck.path.parent.resolve()).replace(os.sep, "/")
    if src != expected_rel or parsed.path != expected_rel:
        return None
    target = (deck.path.parent / pathlib.PurePosixPath(parsed.path)).resolve()
    if target != expected:
        return None
    return filename


def _feedback_issues(deck: ParsedDeck) -> list[str]:
    errors: list[str] = []
    expected_names = set(FT_SCRIPT_SEQUENCE)
    for event in deck.script_events:
        if event.src is None:
            errors.append(f"{deck.relative}: inline script is not canonical")
        if event.startend or not event.closed:
            errors.append(f"{deck.relative}: external script must use a normal paired tag")
        if event.src is not None and event.attrs != (("src", event.src),):
            errors.append(f"{deck.relative}: external script must have exactly one src attribute")

    script_identities = [
        _canonical_shared_script_name(deck, event.src) if event.src is not None else None
        for event in deck.script_events
    ]
    for event, identity in zip(deck.script_events, script_identities):
        if event.src is None:
            continue
        apparent = urlsplit(event.src).path.replace("\\", "/").rsplit("/", 1)[-1]
        if apparent in expected_names and identity != apparent:
            errors.append(f"{deck.relative}: noncanonical shared script src {event.src!r}")
    if deck.track == "3-freetalking" and tuple(script_identities) != FT_SCRIPT_SEQUENCE:
        errors.append(
            f"{deck.relative}: external script sequence must be exactly "
            + " < ".join(FT_SCRIPT_SEQUENCE)
            + f" (found {script_identities!r})"
        )
    def named(filename: str) -> list[ScriptEvent]:
        return [
            event for event, identity in zip(deck.script_events, script_identities)
            if identity == filename
        ]

    feedback = named("feedback.js")
    activities = named("activities.js")
    freetalk = named("freetalk-activities.js")
    pager = named("pager.js")
    ft_tail = [
        ("script-lines.js", named("script-lines.js")),
        ("spotlight.js", named("spotlight.js")),
        ("tutor-notes.js", named("tutor-notes.js")),
        ("highlight.js", named("highlight.js")),
        ("stamp.js", named("stamp.js")),
    ]
    for filename, events, wanted in (
        ("activities.js", activities, 1),
        ("freetalk-activities.js", freetalk, 1 if deck.track == "3-freetalking" else 0),
        ("pager.js", pager, 1),
    ):
        if len(events) != wanted:
            errors.append(f"{deck.relative}: expected exactly {wanted} {filename} script(s) (found {len(events)})")
    if deck.track == "3-freetalking":
        for filename, events in ft_tail:
            if len(events) != 1:
                errors.append(
                    f"{deck.relative}: expected exactly 1 {filename} script(s) (found {len(events)})"
                )
    if deck.feedback_controls:
        if len(feedback) != 1:
            errors.append(f"{deck.relative}: {len(deck.feedback_controls)} live data-fb control(s) require exactly one feedback.js (found {len(feedback)})")
        elif len(activities) == len(pager) == 1:
            if deck.track == "3-freetalking" and len(freetalk) == 1:
                ordered = [activities, feedback, freetalk, pager, *(events for _, events in ft_tail)]
                valid = all(len(events) == 1 for events in ordered) and all(
                    left[0].position < right[0].position for left, right in zip(ordered, ordered[1:])
                )
                expected = (
                    "activities.js < feedback.js < freetalk-activities.js < pager.js < "
                    "script-lines.js < spotlight.js < tutor-notes.js < highlight.js < stamp.js"
                )
            elif deck.track != "3-freetalking":
                valid = activities[0].position < feedback[0].position < pager[0].position
                expected = "activities.js < feedback.js < pager.js"
            else:
                valid = False
                expected = "activities.js < feedback.js < freetalk-activities.js < pager.js"
            if not valid:
                errors.append(f"{deck.relative}: script order must be {expected}")
    elif feedback:
        errors.append(f"{deck.relative}: feedback.js is present without a live data-fb control")
    elif len(activities) == len(pager) == 1:
        if deck.track == "3-freetalking":
            errors.append(f"{deck.relative}: canonical Freetalking deck requires a live data-fb control")
        elif not activities[0].position < pager[0].position:
            errors.append(f"{deck.relative}: script order must be activities.js < pager.js")
    return errors


def _id_issues(deck: ParsedDeck) -> list[str]:
    errors: list[str] = []
    for kind in ("page", "sync", "feedback", "claim"):
        values = deck.ids.get(kind, [])
        blank = sum(not value.strip() for value in values)
        duplicates = sorted(value for value, count in Counter(values).items() if value and count > 1)
        if blank:
            errors.append(f"{deck.relative}: {blank} blank {kind} id(s)")
        if duplicates:
            errors.append(f"{deck.relative}: duplicate {kind} id(s): {', '.join(duplicates)}")
    return errors


def _freetalk_claim_issues(deck: ParsedDeck) -> list[str]:
    if deck.track != "3-freetalking":
        return []
    errors: list[str] = []
    rows = deck.article_rows
    if not 10 <= len(rows) <= 15:
        errors.append(f"{deck.relative}: Freetalking article must have 10–15 stable rows (found {len(rows)})")
        return errors
    expected_options = [f"s{index}" for index in range(1, len(rows) + 1)]
    actual_options = [row["option"] for row in rows]
    if actual_options != expected_options:
        errors.append(f"{deck.relative}: article options must be unique sequential s1…sN")
    claims = [row["claim"] for row in rows]
    waiver_review = LEGACY_FT_CLAIM_WAIVERS.get(deck.relative)
    if waiver_review is not None:
        if waiver_review != deck.review_id:
            errors.append(
                f"{deck.relative}: legacy claim waiver is bound to {waiver_review}, not {deck.review_id}"
            )
        if any(claims):
            errors.append(f"{deck.relative}: legacy claim waiver requires exactly zero data-claim-id values")
    else:
        if any(not claim for claim in claims) or len(set(claims)) != len(claims):
            errors.append(f"{deck.relative}: modern Freetalking article rows need unique stable data-claim-id values")
    return errors


def _entry_floor(
    deck: ParsedDeck,
    briefs: dict[str, str] | None,
    tracks_root: pathlib.Path,
) -> int | None:
    if deck.track != "2-contextual-english":
        return None
    if briefs is None:
        brief = tracks_root / deck.track / "toc" / f"{deck.review_id}.md"
        text = brief.read_text(encoding="utf-8") if brief.is_file() else ""
    else:
        text = briefs.get(deck.review_id, "")
    match = ENTRY_FLOOR.search(text)
    return int(match.group(1)) if match else None


def _reachable(deck: ParsedDeck, source: str, floor: int | None) -> bool:
    match = REVIEW_ID.fullmatch(source)
    if not match:
        return False
    prefix, raw_number = match.groups()
    number = int(raw_number)
    if deck.track == "1-core-patterns":
        return prefix == "CORE" and number < deck.number
    if deck.track == "2-contextual-english":
        return (prefix == "CORE" and floor is not None and number <= floor) or (
            prefix == "CTX" and number < deck.number
        )
    return (prefix == "CORE" and number <= 53) or (prefix == "FT" and number < deck.number)


def audit_sources(
    sources: dict[pathlib.Path, str],
    *,
    tracks_root: pathlib.Path = TRACKS,
    audit_root: pathlib.Path | None = None,
    briefs: dict[str, str] | None = None,
    status_mode: str = "authoring",
    require_full_manifest: bool = False,
    pair_sense_exceptions: frozenset[
        tuple[str, str, tuple[str, str, str], tuple[str, str, str]]
    ] = FT_PAIR_SENSE_EXCEPTIONS,
) -> tuple[list[ParsedDeck], list[str]]:
    """Audit an in-memory corpus and return parsed records plus exact errors."""
    audit_root = (audit_root or tracks_root.parents[3]).resolve()
    decks: list[ParsedDeck] = []
    errors: list[str] = []
    for path in sorted(sources, key=lambda item: item.as_posix()):
        deck, parse_errors = parse_deck(
            path,
            sources[path],
            tracks_root=tracks_root,
            audit_root=audit_root,
        )
        errors.extend(parse_errors)
        if deck:
            decks.append(deck)

    if status_mode not in {"authoring", "release"}:
        raise ValueError("status_mode must be 'authoring' or 'release'")

    superseded = [deck for deck in decks if deck.superseded]
    if len(superseded) != 1:
        errors.append(f"corpus: expected exactly one superseded prototype (found {len(superseded)})")
    elif superseded[0].relative != SUPERSEDED_PROTOTYPE or superseded[0].review_id != "CTX-1":
        errors.append(
            "corpus: superseded record must be the sole canonical CTX-1 prototype at "
            f"{SUPERSEDED_PROTOTYPE}"
        )
    active = [deck for deck in decks if not deck.superseded]

    owners_by_review: dict[str, list[tuple[ParsedDeck, VocabEntry]]] = defaultdict(list)
    for deck in active:
        allowed_statuses = {"pending", "complete"} if status_mode == "authoring" else {"complete"}
        if len(deck.proofread_statuses) != 1 or deck.proofread_statuses[0] not in allowed_statuses:
            value = deck.proofread_statuses if deck.proofread_statuses else "missing"
            expected = "pending/complete" if status_mode == "authoring" else "complete"
            errors.append(f"{deck.relative}: active deck needs exactly one {expected} proofread status (found {value})")
        if deck.vocabulary_statuses != ["reviewed"]:
            errors.append(f"{deck.relative}: active deck needs exactly one reviewed vocabulary status")

        errors.extend(_id_issues(deck))
        errors.extend(_feedback_issues(deck))
        errors.extend(_freetalk_claim_issues(deck))

        for entry in deck.categories["new"]:
            owners_by_review[deck.review_id].append((deck, entry))
            if not phrase_visible(entry.english, deck.productive_text):
                errors.append(f"{deck.relative}: new term {entry.english!r} is absent from track-appropriate productive text")

    # A/F pairing is a logical-deck contract, not a generator convention.
    ft_by_review: dict[str, list[ParsedDeck]] = defaultdict(list)
    for deck in active:
        if deck.track == "3-freetalking":
            ft_by_review[deck.review_id].append(deck)
    for review_id, group in sorted(ft_by_review.items()):
        if len(group) != 2:
            continue
        accessible = next((deck for deck in group if "-accessible/lessons/" in deck.relative), None)
        full = next((deck for deck in group if "-full/lessons/" in deck.relative), None)
        if accessible is None or full is None:
            continue
        normalized_a = accessible.relative.replace("-accessible/lessons/", "-{variant}/lessons/")
        normalized_f = full.relative.replace("-full/lessons/", "-{variant}/lessons/")
        if normalized_a != normalized_f:
            errors.append(f"corpus: {review_id} accessible/full physical pair paths do not match")
        def vocabulary_map(deck: ParsedDeck) -> dict[str, tuple[str, str, str]]:
            return {
                entry.english.casefold(): (category, entry.japanese, entry.source or "")
                for category, entries in deck.categories.items()
                for entry in entries
            }

        a_map = vocabulary_map(accessible)
        f_map = vocabulary_map(full)
        for english in sorted(set(a_map).intersection(f_map)):
            a_category, a_ja, a_owner = a_map[english]
            f_category, f_ja, f_owner = f_map[english]
            sense_key = (
                review_id,
                english,
                (a_category, a_ja, a_owner),
                (f_category, f_ja, f_owner),
            )
            if a_ja != f_ja and sense_key not in pair_sense_exceptions:
                errors.append(
                    f"corpus: {review_id} accessible/full {english!r} has unreviewed "
                    f"sense rows {(a_category, a_ja, a_owner)!r} vs {(f_category, f_ja, f_owner)!r}"
                )
        accessible_claims = [row["claim"] for row in accessible.article_rows]
        full_claims = [row["claim"] for row in full.article_rows]
        a_waived = accessible.relative in LEGACY_FT_CLAIM_WAIVERS
        f_waived = full.relative in LEGACY_FT_CLAIM_WAIVERS
        if a_waived != f_waived:
            errors.append(f"corpus: {review_id} accessible/full legacy claim waiver must be symmetric")
        if not a_waived and not f_waived and accessible_claims != full_claims:
            errors.append(f"corpus: {review_id} accessible/full ordered claim ids differ")

    for deck in active:
        floor = _entry_floor(deck, briefs, tracks_root)
        if deck.track == "2-contextual-english" and floor is None:
            errors.append(f"{deck.relative}: missing Contextual brief entry floor")

        # Ownership is lane-specific and bilingual.  A spelling with a different
        # Japanese meaning is a distinct sense/POS, not a duplicate owner.
        for entry in deck.categories["new"]:
            prior_candidates: list[tuple[ParsedDeck, VocabEntry]] = []
            for candidate_group in owners_by_review.values():
                for candidate in candidate_group:
                    owner_deck, owner_entry = candidate
                    if owner_deck is deck:
                        continue
                    if owner_entry.english.casefold() != entry.english.casefold() or owner_entry.japanese != entry.japanese:
                        continue
                    if deck.track == "3-freetalking" and owner_deck.track == "3-freetalking":
                        deck_variant = "accessible" if "-accessible/lessons/" in deck.relative else "full"
                        owner_variant = "accessible" if "-accessible/lessons/" in owner_deck.relative else "full"
                        if deck_variant != owner_variant:
                            continue
                    if _reachable(deck, owner_deck.review_id, floor):
                        prior_candidates.append(candidate)
            if prior_candidates:
                prior_deck, _prior_entry = sorted(
                    prior_candidates,
                    key=lambda candidate: (candidate[0].number, candidate[0].relative),
                )[0]
                errors.append(
                    f"{deck.relative}: duplicate new owner for {entry.english!r}|{entry.japanese}; "
                    f"reachable prior owner {prior_deck.review_id} at {prior_deck.relative}"
                )

        for entry in deck.categories["recycled"]:
            candidates = owners_by_review.get(entry.source or "", [])
            if deck.track == "3-freetalking" and (entry.source or "").startswith("FT-"):
                variant = "accessible" if "-accessible/lessons/" in deck.relative else "full"
                candidates = [
                    candidate for candidate in candidates
                    if f"-{variant}/lessons/" in candidate[0].relative
                ]
            if not candidates:
                errors.append(f"{deck.relative}: recycled {entry.english!r} names nonexistent active owner {entry.source}")
                continue
            english_matches = [candidate for candidate in candidates if candidate[1].english.casefold() == entry.english.casefold()]
            exact = [candidate for candidate in english_matches if candidate[1].japanese == entry.japanese]
            if not exact:
                if english_matches:
                    expected = sorted({candidate[1].japanese for candidate in english_matches})
                    errors.append(
                        f"{deck.relative}: recycled {entry.english!r} has Japanese {entry.japanese!r}; "
                        f"owner {entry.source} declares {expected!r}"
                    )
                else:
                    errors.append(f"{deck.relative}: owner {entry.source} does not declare {entry.english!r} as new")
                continue
            if not _reachable(deck, entry.source or "", floor):
                errors.append(f"{deck.relative}: recycled owner {entry.source} is not reachable at {deck.review_id}")

    if require_full_manifest:
        errors.extend(_logical_inventory_issues(decks, expected=EXPECTED_ACTIVE_NUMBERS))

    return decks, sorted(set(errors))


def _logical_inventory_issues(
    decks: list[ParsedDeck],
    *,
    expected: dict[str, frozenset[int]] | None = None,
) -> list[str]:
    """Validate the canonical logical deck set, separate from physical files."""
    errors: list[str] = []
    superseded = {deck.relative for deck in decks if deck.superseded}
    if superseded != {SUPERSEDED_PROTOTYPE}:
        errors.append(
            "corpus: superseded prototype set differs from the sole canonical exception "
            f"(found {sorted(superseded)!r})"
        )

    active = [deck for deck in decks if not deck.superseded]
    by_track_review: dict[tuple[str, str], list[ParsedDeck]] = defaultdict(list)
    for deck in active:
        by_track_review[(deck.track, deck.review_id)].append(deck)
    for (track, review_id), group in sorted(by_track_review.items()):
        if track != "3-freetalking":
            if len(group) != 1:
                errors.append(f"corpus: {review_id} has {len(group)} active physical decks; expected one")
            continue
        variants = [
            "accessible" if "/courses/" in deck.relative and "-accessible/lessons/" in deck.relative
            else "full" if "/courses/" in deck.relative and "-full/lessons/" in deck.relative
            else "unknown"
            for deck in group
        ]
        if Counter(variants) != Counter({"accessible": 1, "full": 1}):
            errors.append(
                f"corpus: {review_id} must have exactly one accessible and one full deck "
                f"(found {sorted(variants)!r})"
            )

    for track, prefix in TRACK_NAMES.items():
        numbers = sorted({deck.number for deck in active if deck.track == track})
        wanted = expected.get(track) if expected is not None else None
        if wanted is not None and set(numbers) != set(wanted):
            missing = sorted(set(wanted) - set(numbers))
            extra = sorted(set(numbers) - set(wanted))
            errors.append(
                f"corpus: {prefix} expected manifest differs "
                f"(missing {missing!r}; extra {extra!r})"
            )
        elif numbers and numbers != (
            [number for number in range(1, numbers[-1] + 1) if number not in {4, 5, 6}]
            if track == "1-core-patterns" else list(range(1, numbers[-1] + 1))
        ):
            errors.append(f"corpus: {prefix} logical review-id sequence has a numbering gap")
    return errors


def audit_corpus(
    tracks_root: pathlib.Path = TRACKS,
    *,
    audit_root: pathlib.Path | None = None,
    status_mode: str = "authoring",
) -> tuple[list[ParsedDeck], list[str]]:
    paths = discover(tracks_root)
    decks, errors = audit_sources(
        {path: path.read_text(encoding="utf-8") for path in paths},
        tracks_root=tracks_root,
        audit_root=audit_root,
        status_mode=status_mode,
        require_full_manifest=True,
    )
    return decks, sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracks", type=pathlib.Path, default=TRACKS)
    parser.add_argument("--release", action="store_true", help="require complete proofread status")
    args = parser.parse_args()
    decks, errors = audit_corpus(
        args.tracks.resolve(),
        status_mode="release" if args.release else "authoring",
    )
    active = sum(not deck.superseded for deck in decks)
    print(f"{len(decks)} English HTML record(s): {active} active + {len(decks) - active} superseded")
    for error in errors:
        print(f"✗ {error}")
    print(f"{len(errors)} integrity error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
