#!/usr/bin/env python3
"""Read the author-declared vocabulary contract from an English lesson deck."""

from __future__ import annotations

import html as html_lib
import pathlib
import re


CATEGORIES = ("new", "recycled", "assumed", "receptive")
META = re.compile(r'<meta\s+name="podo:vocabulary:([a-z-]+)"\s+content="([^"]*)"\s*/?>')
STATUS = re.compile(r'<meta\s+name="podo:vocabulary-status"\s+content="([^"]*)"\s*/?>')
WAIVER = re.compile(r'<meta\s+name="podo:vocabulary-waiver"\s+content="([^"]*)"\s*/?>')
HINT_CHIP = re.compile(r'<span class="hint-chip"[^>]*>(.*?)</span>', re.S)
TAG = re.compile(r"<[^>]+>")


class VocabularyError(ValueError):
    pass


def _entries(raw: str, category: str) -> list[dict[str, str | None]]:
    entries = []
    for item in filter(None, (part.strip() for part in html_lib.unescape(raw).split(";"))):
        fields = [part.strip() for part in item.split("|")]
        wanted = 3 if category == "recycled" else 2
        if len(fields) != wanted or any(not field for field in fields):
            shape = "English|Japanese|source" if category == "recycled" else "English|Japanese"
            raise VocabularyError(f"{category} entry {item!r} must be {shape}")
        if category == "recycled" and not re.fullmatch(r"(?:CORE|CTX|FT)-\d+", fields[2]):
            raise VocabularyError(
                f"recycled entry {item!r} must name an earlier stable source id"
            )
        entries.append({
            "english": fields[0],
            "japanese": fields[1],
            "source": fields[2] if category == "recycled" else None,
        })
    return entries


def parse(text: str, *, source: pathlib.Path | str = "deck") -> dict:
    status = STATUS.search(text)
    if not status:
        raise VocabularyError(f"{source}: missing podo:vocabulary-status")

    matches = list(META.finditer(text))
    names = [match.group(1) for match in matches]
    duplicates = sorted(name for name in set(names) if names.count(name) > 1)
    if duplicates:
        raise VocabularyError(f"{source}: duplicate vocabulary categories: {', '.join(duplicates)}")
    found = {match.group(1): match.group(2) for match in matches}
    missing = [category for category in CATEGORIES if category not in found]
    unknown = sorted(set(found) - set(CATEGORIES))
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unknown:
            details.append(f"unknown {', '.join(unknown)}")
        raise VocabularyError(f"{source}: invalid vocabulary categories ({'; '.join(details)})")

    categories = {category: _entries(found[category], category) for category in CATEGORIES}
    seen: dict[str, str] = {}
    for category, entries in categories.items():
        for entry in entries:
            key = entry["english"].casefold()
            if key in seen:
                raise VocabularyError(
                    f"{source}: {entry['english']!r} appears in both {seen[key]} and {category}"
                )
            seen[key] = category

    waiver = WAIVER.search(text)
    return {
        "status": html_lib.unescape(status.group(1)).strip(),
        "categories": categories,
        "waiver": html_lib.unescape(waiver.group(1)).strip() if waiver else "",
    }


def load_result(data: dict) -> tuple[str, str] | None:
    """Return ``(severity, message)`` when the normal eight-word cap is exceeded."""
    count = len(data["categories"]["new"])
    if count <= 8:
        return None
    message = f"{count} new content words — the normal ceiling is 8"
    if data["waiver"]:
        return "warning", f"{message}; waiver: {data['waiver']}"
    return "error", f"{message}; add a reasoned podo:vocabulary-waiver or reduce the load"


def hint_words(text: str) -> set[str]:
    """Return English values from the learner-facing ``Japanese:English`` hint chips."""
    words = set()
    for body in HINT_CHIP.findall(text):
        plain = html_lib.unescape(TAG.sub("", body)).strip()
        if ":" not in plain:
            raise VocabularyError(f"hint chip {plain!r} must be Japanese:English")
        japanese, english = (part.strip() for part in plain.rsplit(":", 1))
        if not japanese or not english:
            raise VocabularyError(f"hint chip {plain!r} must be Japanese:English")
        words.add(english.casefold())
    return words
