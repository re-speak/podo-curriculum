#!/usr/bin/env python3
"""Generate the English curriculum gateway and one review page per track.

    python3 tools/authoring/en/build_catalog.py

Outputs:
    english/catalog.html
    english/catalog/1-core-patterns.html
    english/catalog/2-contextual-english.html
    english/catalog/3-freetalking.html
    english/catalog/4-pronunciation.html

The four table-of-contents files remain the source of truth. Parsing is owned by
``track_parsers.py`` so the catalog, briefs, and audits cannot silently disagree.
"""

from __future__ import annotations

import json
from pathlib import Path

import track_parsers


ROOT = Path(__file__).resolve().parents[3] / "sandbox/drafts/en"
TOOLS = Path(__file__).resolve().parent
OUT = ROOT / "catalog.html"
OUT_DIR = ROOT / "catalog"

LEVELS = ["Pre-A1", "A1", "A2", "B1", "B1+", "B2", "C1", "Intermediate", "Advanced"]


def inline_text(value: str | None) -> str:
    """Remove the small amount of Markdown used inside TOC fields."""
    if not value:
        return ""
    return value.replace("`", "").replace("**", "").replace("*", "").strip()


def level_span(value: str) -> list[str]:
    if value == "Intermediate / Advanced versions":
        return ["Intermediate", "Advanced"]
    if value == "planning only":
        return []
    normalized = value.replace("–", " → ").replace("—", " → ")
    names = [part.strip() for part in normalized.split("→")]
    hits = [level for level in LEVELS if level in names]
    if len(hits) == 2:
        a, b = LEVELS.index(hits[0]), LEVELS.index(hits[1])
        return LEVELS[a:b + 1]
    return hits


def lesson(item: dict, *, kind: str) -> dict:
    models = []
    for model in item.get("models", []):
        models.append({
            "ex": model.get("model", ""),
            "pat": model.get("pattern", ""),
            "reply": (f'{model.get("partner")}: {model.get("reaction")}'
                      if model.get("reaction") else ""),
        })

    notes = []
    for label, key in (("Expressions", "expressions"), ("Grammar", "grammar"),
                       ("Japanese transfer", "jp"), ("Understand", "understand"),
                       ("Author note", "authorNote"),
                       ("Follow-up ladder", "ladder"), ("Useful moves", "moves"),
                       ("Japanese habit", "habit"), ("Examples", "examples")):
        if item.get(key):
            notes.append({"k": label, "v": inline_text(item[key])})

    primary = (models[0]["ex"] if models else item.get("opening")
               or item.get("fix") or item.get("canDo") or "")
    return {
        "id": item["id"], "n": item["no"], "title": item["title"],
        "can": inline_text(item.get("canDo")), "scene": inline_text(item.get("scene")),
        "pats": models, "notes": notes, "level": item.get("level", ""),
        "kind": kind, "primary": inline_text(primary),
        "deep": bool(item.get("deep")), "formats": item.get("formats", []),
        "floor": item.get("floor"), "fix": inline_text(item.get("fix")),
    }


def grouped(items: list[dict], key, make_group, kind: str) -> list[dict]:
    groups: list[dict] = []
    current = object()
    for item in items:
        owner = key(item)
        if owner != current:
            groups.append({**make_group(item), "lessons": []})
            current = owner
        groups[-1]["lessons"].append(lesson(item, kind=kind))
    return groups


def distribution(groups: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for group in groups:
        span = group.get("levels") or level_span(group.get("level", ""))
        for level in span:
            counts[level] = counts.get(level, 0) + len(group["lessons"])
    return counts


def build() -> dict:
    core = track_parsers.parse_core()
    contextual = track_parsers.parse_contextual()
    freetalking = track_parsers.parse_freetalking()
    pronunciation = track_parsers.parse_pronunciation()

    core_groups = grouped(
        core,
        lambda x: (x["part"], x["unitNo"]),
        lambda x: {"label": f'Unit {x["unitNo"]}', "title": x["unit"],
                   "subtitle": x["part"], "level": x["level"]},
        "core",
    )
    contextual_groups = grouped(
        contextual,
        lambda x: x["courseNo"],
        lambda x: {"label": f'Course {x["courseNo"]} · {x["area"]}',
                   "title": x["course"], "level": x["level"],
                   "meta": f'Core {x["floor"]} floor'},
        "contextual",
    )
    ft_groups = grouped(
        freetalking,
        lambda x: x["themeNo"],
        lambda x: {"label": f'Theme {x["themeNo"]}', "title": x["theme"],
                   "level": x["level"], "levels": ["Intermediate", "Advanced"],
                   "meta": x["themeFormat"]},
        "freetalking",
    )
    pronunciation_groups = grouped(
        pronunciation,
        lambda x: x["partNo"],
        lambda x: {"label": f'Part {x["partNo"]}', "title": x["part"],
                   "level": "planning only", "meta": "Planning stage"},
        "pronunciation",
    )

    specs = [
        {
            "id": "1-core-patterns", "no": 1, "name": "Core Patterns", "short": "Core",
            "glyph": "Aa", "status": "review", "accent": "#2b5fd9", "tint": "#eef2fd",
            "unitWord": "units", "itemWord": "lessons",
            "desc": "The main speaking sequence, from first introductions to precise argument. Each lesson pairs one practical outcome with two production patterns.",
            "note": "Review the model sentences first. Frames, grammar notes, and Japanese transfer notes explain why each item exists.",
            "stats": [(len(core), "lessons"), (len(core_groups), "units"),
                      (sum(len(x["models"]) for x in core), "patterns")],
            "groups": core_groups,
        },
        {
            "id": "2-contextual-english", "no": 2, "name": "Contextual English", "short": "Contextual",
            "glyph": "場", "status": "review", "accent": "#c22a5f", "tint": "#fdeff3",
            "unitWord": "courses", "itemWord": "lessons",
            "desc": "Standalone Travel and Business tasks that turn Core language into practical performance from low-intermediate upward.",
            "note": "Judge the practical coverage and each learner line together with its reply. Every lesson must work without story context from another lesson.",
            "stats": [(len(contextual), "lessons"), (len(contextual_groups), "courses"),
                      (len({x["areaNo"] for x in contextual}), "practical areas")],
            "groups": contextual_groups,
        },
        {
            "id": "3-freetalking", "no": 3, "name": "Freetalking", "short": "Freetalking",
            "glyph": "話", "status": "review", "accent": "#0080a8", "tint": "#e9f6fa",
            "unitWord": "themes", "itemWord": "topics",
            "desc": "A topic-led curriculum for sustained conversation, with an opening question, a follow-up ladder, and reusable speaking moves.",
            "note": "Each topic supports separate Intermediate and Advanced sessions. The ladder is a pool of routes, not a script to complete.",
            "stats": [(len(freetalking), "topics"), (len(ft_groups), "themes"), (2, "levels")],
            "groups": ft_groups,
        },
        {
            "id": "4-pronunciation", "no": 4, "name": "Pronunciation", "short": "Pronunciation",
            "glyph": "音", "status": "plan", "accent": "#69737d", "tint": "#f4f5f7",
            "unitWord": "parts", "itemWord": "lessons",
            "desc": "A closed list of the English sound and rhythm problems that most often reduce intelligibility for Japanese speakers.",
            "note": "Planning only: no lesson decks are authorized yet. The order follows impact on intelligibility rather than how famous a contrast is.",
            "stats": [(len(pronunciation), "lessons"), (len(pronunciation_groups), "parts"),
                      (0, "lesson decks")],
            "groups": pronunciation_groups,
        },
    ]

    for track in specs:
        track["stats"] = [{"v": value, "k": label} for value, label in track["stats"]]
        track["total"] = sum(len(group["lessons"]) for group in track["groups"])
        track["dist"] = distribution(track["groups"])
        track["span"] = [level for level in LEVELS if track["dist"].get(level)]

    return {
        "levels": LEVELS,
        "tracks": specs,
        "totals": {"tracks": len(specs), "items": sum(t["total"] for t in specs),
                   "review": sum(t["total"] for t in specs if t["status"] == "review"),
                   "units": sum(len(t["groups"]) for t in specs)},
    }


def render(template: str, data: dict, output: Path) -> None:
    source = (TOOLS / template).read_text(encoding="utf-8")
    output.write_text(source.replace("/*__DATA__*/null", json.dumps(
        data, ensure_ascii=False, separators=(",", ":"))), encoding="utf-8")


def main() -> int:
    data = build()
    OUT_DIR.mkdir(exist_ok=True)
    summaries = [{key: value for key, value in track.items() if key != "groups"}
                 for track in data["tracks"]]
    render("gateway_template.html", {**data, "tracks": summaries}, OUT)

    nav = [{key: track[key] for key in ("id", "no", "name", "short", "accent")}
           for track in data["tracks"]]
    review_index = {
        item["id"]: {"title": item["title"], "primary": item["primary"]}
        for track in data["tracks"] if track["status"] == "review"
        for group in track["groups"] for item in group["lessons"]
    }
    for track in data["tracks"]:
        render("track_template.html", {"levels": LEVELS, "track": track, "nav": nav,
                                       "review": review_index},
               OUT_DIR / f'{track["id"]}.html')

    counts = [track["total"] for track in data["tracks"]]
    print(f"wrote {OUT.relative_to(ROOT.parent)} + {OUT_DIR.relative_to(ROOT.parent)}/*.html "
          f"— {counts[0]} / {counts[1]} / {counts[2]} review items, {counts[3]} planned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
