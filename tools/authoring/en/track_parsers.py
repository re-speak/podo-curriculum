#!/usr/bin/env python3
"""Parse the four English curriculum TOCs into one strict, shared shape.

The TOCs remain the source of truth.  Catalogs, coverage maps and lesson briefs
must consume this module instead of growing their own slightly different regex
parsers.  A format change raises ``ParseError``; silently dropping a lesson is
more dangerous than refusing to generate an artifact.
"""

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
TRACKS = ROOT / "tracks"


class ParseError(ValueError):
    pass


ITEM = re.compile(r"^\*\*(\d+)\. (.+?)\*\*(.*)$")
REVIEW_MODES = {"recognition", "controlled", "contrast", "transfer", "checkpoint"}


def slugify(text: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def _read(track: str) -> tuple[pathlib.Path, list[str]]:
    path = TRACKS / track / "table-of-contents.md"
    return path, path.read_text(encoding="utf-8").splitlines()


def _items(lines: list[str], *, after: str | None = None) -> list[tuple[int, str, str, list[str]]]:
    """Return ``number, heading, heading-tail, body`` for numbered bold items."""
    start = 0
    if after:
        try:
            start = next(i for i, line in enumerate(lines) if line.startswith(after))
        except StopIteration as exc:
            raise ParseError(f"missing curriculum marker {after!r}") from exc
    hits = [(i, m) for i, line in enumerate(lines[start:], start) if (m := ITEM.match(line))]
    out = []
    for k, (i, match) in enumerate(hits):
        end = hits[k + 1][0] if k + 1 < len(hits) else len(lines)
        # A trailing authoring appendix must not become part of the last item.
        for j in range(i + 1, end):
            if lines[j].startswith(("# Scope boundary", "## How an episode passes", "## Adding a topic", "## Notes for when")):
                end = j
                break
        out.append((int(match.group(1)), match.group(2).strip(), match.group(3).strip(), lines[i + 1:end]))
    return out


def _field(body: list[str], label: str, *, wrapped: bool = False) -> str | None:
    if wrapped:
        pattern = re.compile(rf"^\*{re.escape(label)}: (.+?)\*$")
    else:
        pattern = re.compile(rf"^-? ?\*{re.escape(label)}:\* (.+)$")
    for i, line in enumerate(body):
        match = pattern.match(line)
        if not match:
            continue
        value = [match.group(1).strip()]
        for following in body[i + 1:]:
            if not following.startswith("  "):
                break
            value.append(following.strip())
        return " ".join(value)
    return None


def _wrapped_field(body: list[str], label: str) -> str | None:
    """Read ``*Label:* value`` fields whose prose wraps as ordinary Markdown.

    Freetalking fields deliberately wrap at the repository line length.  Their
    continuation lines are not indented list content, so ``_field`` must remain
    strict for the other TOCs while this reader consumes prose up to the next
    field or paragraph boundary.
    """
    pattern = re.compile(rf"^\*{re.escape(label)}:\* (.+)$")
    for i, line in enumerate(body):
        match = pattern.match(line)
        if not match:
            continue
        value = [match.group(1).strip()]
        for following in body[i + 1:]:
            if not following.strip() or re.match(r"^\*[^*]+:\* ", following):
                break
            value.append(following.strip())
        return " ".join(value)
    return None


def _italic_paragraph(body: list[str], label: str) -> str | None:
    """Read ``*Label: ...*`` even when Markdown wraps it across lines."""
    for i, line in enumerate(body):
        match = re.match(rf"^\*{re.escape(label)}: (.*)$", line)
        if not match:
            continue
        first = match.group(1)
        if first.endswith("*"):
            return first[:-1].strip()
        value = [first]
        for following in body[i + 1:]:
            value.append(following.strip())
            if following.endswith("*"):
                break
        joined = " ".join(value)
        return joined[:-1].strip() if joined.endswith("*") else joined.strip()
    return None


def _owner_maps(lines: list[str]) -> tuple[dict[int, dict], dict[int, dict]]:
    """Map item numbers to their current H1 and H2 curriculum sections."""
    top: dict | None = None
    section: dict | None = None
    tops: dict[int, dict] = {}
    sections: dict[int, dict] = {}
    for line in lines:
        if line.startswith("# "):
            top = {"heading": line[2:].strip()}
        elif line.startswith("## "):
            section = {"heading": line[3:].strip()}
        elif (match := ITEM.match(line)):
            n = int(match.group(1))
            if top:
                tops[n] = dict(top)
            if section:
                sections[n] = dict(section)
    return tops, sections


def _require(value, path: pathlib.Path, number: int, label: str):
    if value is None or value == "" or value == []:
        raise ParseError(f"{path}: item {number} is missing {label}")
    return value


def _continuous(path: pathlib.Path, lessons: list[dict], expected: int, retired: frozenset[int] = frozenset()) -> None:
    numbers = [lesson["no"] for lesson in lessons]
    wanted = [number for number in range(1, expected + 1) if number not in retired]
    if numbers != wanted:
        suffix = f" except retired IDs {sorted(retired)}" if retired else ""
        raise ParseError(f"{path}: lesson numbers must be continuous 1..{expected}{suffix}; got {numbers[:5]}…{numbers[-5:]}")


def _review_registry(path: pathlib.Path, lines: list[str]) -> dict[str, dict]:
    registry = {}
    pattern = re.compile(r"^\| `([A-Z]+-\d{2})` \| (.+?) \| Core (\d+) \|$")
    for line in lines:
        if not (match := pattern.match(line)):
            continue
        target, description, introduced = match.groups()
        if target in registry:
            raise ParseError(f"{path}: duplicate spiral-review target {target}")
        registry[target] = {
            "id": target,
            "description": description,
            "introduced": int(introduced),
        }
    if not registry:
        raise ParseError(f"{path}: missing Japanese-L1 spiral review registry")
    return registry


def _spiral_reviews(
    path: pathlib.Path,
    number: int,
    value: str | None,
    registry: dict[str, dict],
) -> list[dict]:
    if not value:
        return []
    matches = re.findall(r"`([A-Z]+-\d{2}):([a-z]+)`", value)
    if not matches or len(matches) != value.count("`") // 2:
        raise ParseError(f"{path}: Core {number} has malformed Spiral review metadata: {value}")
    if len(matches) > 2:
        raise ParseError(f"{path}: Core {number} has more than two spiral-review targets")
    if len({target for target, _mode in matches}) != len(matches):
        raise ParseError(f"{path}: Core {number} repeats a spiral-review target")
    reviews = []
    for target, mode in matches:
        if target not in registry:
            raise ParseError(f"{path}: Core {number} references unknown spiral-review target {target}")
        if mode not in REVIEW_MODES:
            raise ParseError(f"{path}: Core {number} uses unknown spiral-review mode {mode}")
        meta = registry[target]
        if number <= meta["introduced"]:
            raise ParseError(
                f"{path}: Core {number} reviews {target} before or during its Core {meta['introduced']} introduction"
            )
        reviews.append({**meta, "mode": mode})
    return reviews


def _validate_core_spiral(path: pathlib.Path, lessons: list[dict], registry: dict[str, dict]) -> None:
    lesson_by_no = {lesson["no"]: lesson for lesson in lessons}
    for target, meta in registry.items():
        if meta["introduced"] not in lesson_by_no:
            raise ParseError(f"{path}: {target} has unknown introduction Core {meta['introduced']}")
        returns = [
            (lesson["no"], review["mode"])
            for lesson in lessons
            for review in lesson["spiralReviews"]
            if review["id"] == target
        ]
        if len(returns) < 3:
            raise ParseError(f"{path}: {target} needs at least three planned review returns; got {returns}")
        modes = {mode for _number, mode in returns}
        if len(modes) < 2:
            raise ParseError(f"{path}: {target} needs at least two review modes; got {sorted(modes)}")
        if not modes.intersection({"transfer", "checkpoint"}):
            raise ParseError(f"{path}: {target} never reaches transfer or checkpoint retrieval")
        if returns[0][0] > meta["introduced"] + 12:
            raise ParseError(f"{path}: {target} has no timely return after Core {meta['introduced']}")
        if not any(number >= meta["introduced"] + 8 for number, _mode in returns):
            raise ParseError(f"{path}: {target} has no delayed return eight or more lessons later")

    for index, lesson in enumerate(lessons):
        next_unit = lessons[index + 1]["unitNo"] if index + 1 < len(lessons) else None
        for review in lesson["spiralReviews"]:
            if review["mode"] == "checkpoint" and next_unit == lesson["unitNo"]:
                raise ParseError(
                    f"{path}: Core {lesson['no']} marks {review['id']} as checkpoint before the unit ends"
                )


def parse_core() -> list[dict]:
    path, lines = _read("1-core-patterns")
    tops, sections = _owner_maps(lines)
    review_registry = _review_registry(path, lines)
    lessons = []
    for number, heading, _tail, body in _items(lines, after="# Part 1"):
        title, sep, hint = heading.partition(" — ")
        models = []
        for line in body:
            match = re.match(r'^- "(.+?)" — `(.+?)`(.*)$', line)
            if match:
                models.append({
                    "model": match.group(1),
                    "pattern": match.group(2),
                    "reference": match.group(3).strip() or None,
                })
        section = sections.get(number, {}).get("heading", "")
        unit_match = re.match(r"Unit (\d+) · (.+?) · (\d+) lessons · \*\*(.+?)\*\*", section)
        _require(unit_match, path, number, "a valid Unit heading")
        part = tops.get(number, {}).get("heading", "")
        bounded_chunk = _field(body, "Bounded chunk")
        spiral_reviews = _spiral_reviews(path, number, _field(body, "Spiral review"), review_registry)
        lessons.append({
            "id": f"CORE-{number}", "no": number, "track": "1-core-patterns",
            "title": title, "canDo": _require(_field(body, "Can-do", wrapped=True) or hint if sep else None, path, number, "Can-do"),
            "models": _require(models, path, number, "two model/pattern lines"),
            "patterns": [model["pattern"] for model in models],
            "expressions": _require(_field(body, "Expressions"), path, number, "Expressions"),
            # Part 2 was drafted without learner-facing grammar lines. Preserve
            # that absence so generated audits can expose it; never invent one.
            "grammar": _field(body, "Grammar"),
            "fixedSupport": _field(body, "Fixed support"),
            "jp": _require(_field(body, "JP"), path, number, "JP"),
            "boundedChunk": bounded_chunk,
            "spiralReviews": spiral_reviews,
            "reviewRegistry": review_registry,
            "part": part,
            "unitNo": int(unit_match.group(1)), "unit": unit_match.group(2).strip(),
            "unitSize": int(unit_match.group(3)), "level": unit_match.group(4).strip(),
        })
        if len(models) != 2:
            raise ParseError(f"{path}: Core {number} has {len(models)} patterns, expected exactly 2")
    _continuous(path, lessons, 122, frozenset({4, 5, 6}))
    _validate_core_spiral(path, lessons, review_registry)
    return lessons


def parse_contextual() -> list[dict]:
    path, lines = _read("2-contextual-english")
    tops, sections = _owner_maps(lines)
    lessons = []
    for number, heading, _tail, body in _items(lines):
        course_heading = sections.get(number, {}).get("heading", "")
        course = re.match(r"Course (\d+) · (.+?) · (\d+) lessons · \*\*(.+?)\*\* · floor: Core (\d+)", course_heading)
        area_heading = tops.get(number, {}).get("heading", "")
        area = re.match(r"Area (\d+) · (.+)", area_heading)
        _require(course, path, number, "a valid Course heading")
        _require(area, path, number, "a valid Area heading")
        exchanges = []
        for i, line in enumerate(body):
            match = re.match(r'^- 私: "(.+?)" — `(.+?)`(.*?)$', line)
            if not match:
                continue
            reaction = re.match(r'^\s+→ (.+?): ["「](.+?)["」]$', body[i + 1]) if i + 1 < len(body) else None
            # Accept both ``Core 36, Core 56`` and the older shorthand
            # ``Core 36, 56``. References describe actual form ownership, so
            # silently dropping the second owner would corrupt author briefs.
            refs = []
            for group in re.findall(r"Core\s+(\d+(?:\s*,\s*(?:Core\s+)?\d+)*)", match.group(3)):
                refs.extend(int(n) for n in re.findall(r"\d+", group))
            exchanges.append({
                "model": match.group(1), "pattern": match.group(2),
                "coreRefs": refs, "chunk": "`chunk`" in match.group(3),
                "partner": reaction.group(1) if reaction else None,
                "reaction": reaction.group(2) if reaction else None,
            })
        scene = _italic_paragraph(body, "場面")
        can_do = _italic_paragraph(body, "Can-do")
        lessons.append({
            "id": f"CTX-{number}", "no": number, "track": "2-contextual-english",
            "title": heading, "scene": _require(scene, path, number, "場面"),
            "canDo": _require(can_do, path, number, "Can-do"),
            "models": exchanges, "patterns": [x["pattern"] for x in exchanges],
            "expressions": _field(body, "Expressions"), "understand": _field(body, "Understand"),
            "authorNote": _field(body, "Author note"),
            "areaNo": int(area.group(1)), "area": area.group(2).strip(),
            "courseNo": int(course.group(1)), "course": course.group(2).strip(),
            "courseSize": int(course.group(3)), "level": course.group(4).strip(),
            "floor": int(course.group(5)),
        })
        if len(exchanges) != 2 or any(not x["reaction"] for x in exchanges):
            raise ParseError(f"{path}: CTX {number} needs exactly 2 learner lines with partner reactions")
        for exchange in exchanges:
            late_refs = [ref for ref in exchange["coreRefs"] if ref > int(course.group(5))]
            if late_refs and not exchange["chunk"]:
                raise ParseError(
                    f"{path}: CTX {number} uses Core {late_refs} above its Core {course.group(5)} "
                    "course floor without marking the pattern as a bounded chunk"
                )
    _continuous(path, lessons, 60)
    return lessons


def parse_freetalking() -> list[dict]:
    path, lines = _read("3-freetalking")
    tops, _sections = _owner_maps(lines)
    theme_ladders: dict[int, str] = {}
    for i, line in enumerate(lines):
        theme_match = re.match(r"^# Theme (\d+) ·", line)
        if not theme_match:
            continue
        end = next((j for j in range(i + 1, len(lines)) if ITEM.match(lines[j]) or lines[j].startswith("# Theme ")), len(lines))
        intro = " ".join(part.strip() for part in lines[i + 1:end])
        climb = re.search(r"Climb: (.+?flips\.)", intro)
        if climb:
            theme_ladders[int(theme_match.group(1))] = climb.group(1).strip().rstrip("*")
    lessons = []
    for number, heading, tail, body in _items(lines):
        theme_heading = tops.get(number, {}).get("heading", "")
        theme = re.match(r"Theme (\d+) · (.+?) · `(.+?)`", theme_heading)
        _require(theme, path, number, "a valid Theme heading")
        full_heading = heading + " " + tail
        formats = re.findall(r"`(story|choose|両国|opinion)`", full_heading)
        if not formats:
            formats = [theme.group(3)]
        opening = _wrapped_field(body, "Opens")
        if not opening:
            balance = re.search(r"— \*(.+?)\*", full_heading)
            opening = balance.group(1) if balance else None
        theme_no = int(theme.group(1))
        moves = _wrapped_field(body, "Moves")
        lessons.append({
            "id": f"FT-{number}", "no": number, "track": "3-freetalking",
            "title": heading.split(" — ")[0].strip(), "canDo": opening,
            "opening": _require(opening, path, number, "Opens"),
            "ladder": _require(_wrapped_field(body, "Ladder") or theme_ladders.get(theme_no), path, number, "Ladder"),
            "moves": moves, "coreRefs": [int(n) for n in re.findall(r"Core (\d+)", moves or "")],
            "shared": _wrapped_field(body, "Shared"),
            "formats": _require(formats, path, number, "format tag"), "deep": "深く" in full_heading,
            "themeNo": theme_no, "theme": theme.group(2).strip(),
            "themeFormat": theme.group(3), "level": "Intermediate / Advanced versions",
        })
    _continuous(path, lessons, 121)
    return lessons


def parse_pronunciation() -> list[dict]:
    path, lines = _read("4-pronunciation")
    lessons = []
    part = None
    for line in lines:
        if (match := re.match(r"^## Part (\d+) · (.+)$", line)):
            part = {"no": int(match.group(1)), "title": match.group(2)}
        row = re.match(r"^\| \*\*(\d+)\. (.+?)\*\* \| (.+?) \| (.+?) \| (.+?) \|$", line)
        if not row:
            continue
        _require(part, path, int(row.group(1)), "Part heading")
        lessons.append({
            "id": f"PRON-{row.group(1)}", "no": int(row.group(1)), "track": "4-pronunciation",
            "title": row.group(2), "habit": row.group(3), "fix": row.group(4),
            "examples": row.group(5), "canDo": row.group(4), "partNo": part["no"],
            "part": part["title"], "level": "planning only",
        })
    _continuous(path, lessons, 12)
    return lessons


PARSERS = {
    "1-core-patterns": parse_core,
    "2-contextual-english": parse_contextual,
    "3-freetalking": parse_freetalking,
    "4-pronunciation": parse_pronunciation,
}


def parse_track(track: str | pathlib.Path) -> list[dict]:
    name = pathlib.Path(track).name
    try:
        return PARSERS[name]()
    except KeyError as exc:
        raise ParseError(f"no English TOC parser for {name!r}") from exc
