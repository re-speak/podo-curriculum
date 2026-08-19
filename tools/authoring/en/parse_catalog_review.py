#!/usr/bin/env python3
"""Validate copied native-review text against the current English TOCs.

This is intentionally an intake tool, not an automatic merger. It rejects stale
titles/model lines and emits structured JSON for human triage.

    python3 tools/authoring/en/parse_catalog_review.py review.txt
    python3 tools/authoring/en/parse_catalog_review.py review.txt --output review.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

import track_parsers


HEADER = "PODO ENGLISH CURRICULUM — NATIVE REVIEW"
SECTION = re.compile(r"^## (GENERAL|FLAGGED — \d+|COMMENTS, not flagged — \d+)$")
ENTRY = re.compile(r"^(CORE|CTX|FT)-(\d+)  (.+)$")


class ReviewError(ValueError):
    pass


def current_items() -> dict[str, dict]:
    items = {}
    for lesson in track_parsers.parse_core():
        items[lesson["id"]] = {"title": lesson["title"], "firstLine": lesson["models"][0]["model"]}
    for lesson in track_parsers.parse_contextual():
        items[lesson["id"]] = {"title": lesson["title"], "firstLine": lesson["models"][0]["model"]}
    for lesson in track_parsers.parse_freetalking():
        items[lesson["id"]] = {"title": lesson["title"], "firstLine": lesson["opening"]}
    return items


def parse(text: str, current: dict[str, dict] | None = None) -> dict:
    current = current or current_items()
    lines = text.replace("\r\n", "\n").splitlines()
    if not lines or lines[0].strip() != HEADER:
        raise ReviewError(f"review must start with {HEADER!r}")
    if len(lines) < 2 or not re.fullmatch(r"\d+ items · \d+ flagged · \d+ commented", lines[1].strip()):
        raise ReviewError("missing catalog count line")

    general: list[str] = []
    entries: list[dict] = []
    section = None
    i = 2
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if (heading := SECTION.match(line)):
            section = heading.group(1)
            i += 1
            continue
        if section == "GENERAL":
            general.append(line)
            i += 1
            continue
        match = ENTRY.match(line)
        if not match or section is None or section == "GENERAL":
            raise ReviewError(f"line {i + 1}: unexpected review text {line!r}")
        review_id = f"{match.group(1)}-{int(match.group(2))}"
        if review_id not in current:
            raise ReviewError(f"line {i + 1}: unknown review id {review_id}")
        title = match.group(3).strip()
        i += 1
        if i >= len(lines) or not lines[i].startswith("    says: "):
            raise ReviewError(f"line {i + 1}: {review_id} is missing its 'says:' snapshot")
        said = lines[i][10:].strip()
        i += 1
        comment_lines = []
        if i < len(lines) and lines[i].startswith("    → "):
            comment_lines.append(lines[i][6:])
            i += 1
            while i < len(lines) and lines[i].startswith("      "):
                comment_lines.append(lines[i][6:])
                i += 1
        snapshot = current[review_id]
        if title != snapshot["title"]:
            raise ReviewError(f"{review_id}: stale title; review has {title!r}, current TOC has {snapshot['title']!r}")
        if said != snapshot["firstLine"]:
            raise ReviewError(f"{review_id}: stale first line; review has {said!r}, current TOC has {snapshot['firstLine']!r}")
        entries.append({
            "id": review_id,
            "flagged": section.startswith("FLAGGED"),
            "title": title,
            "currentFirstLine": said,
            "comment": "\n".join(comment_lines).strip() or None,
        })

    ids = [entry["id"] for entry in entries]
    if len(ids) != len(set(ids)):
        duplicate = next(review_id for review_id in ids if ids.count(review_id) > 1)
        raise ReviewError(f"duplicate review entry {duplicate}")
    return {
        "formatVersion": 1,
        "source": "english/catalog.html copied native review",
        "general": "\n".join(general).strip() or None,
        "items": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    try:
        result = parse(args.review.read_text(encoding="utf-8"))
    except ReviewError as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            parser.error(f"refusing to overwrite {args.output}")
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output} — {len(result['items'])} item(s)")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
