#!/usr/bin/env python3
"""Generate every deployable course cover from one Figma-derived visual system.

The editable inputs are the course manifests, this layout, and the transparent
motifs beside it.  The outputs live with each course as ``assets/cover.svg`` and
``assets/cover.png``; ``course.yaml`` points grape at the PNG.

    python3 tools/authoring/course_covers/generate.py
    python3 tools/authoring/course_covers/generate.py --check
    python3 tools/authoring/course_covers/generate.py --only kr/hangul-starter

**The cover is designed at 144x180, not at 864x1080.**  That is the size the
student app draws it (``apps/web/src/features/subscribes/ui/lesson-thumbnail.tsx``:
a 144 px card, ``aspect-[4/5]``, in a horizontal carousel).  Everything here is
authored as the card size times six, so a label that is 10 px on the card is 60
here.  The previous layout was composed at full size and carried an eyebrow, a
language pill and a footer track label that all landed under 7 px on the card —
they are gone.

What the cover says now, top to bottom:

  pill    the sub-family and the level — ``ドラマ 1 · 中級``, ``初級パターン 1``.
          The rail header already names the track, so the pill names the thing
          inside it that the header does not.
  title   the topic, in the language the course teaches.
  motif   unchanged.

Colour is no longer a hash.  ``palette_for`` reads a table: one fill per level
band on the core ladder, one per sub-family in the contextual track, one per
topic in free talking.  Nothing is a gradient of anything — a course and its
neighbour differ because they *are* different, not by a shade.
"""

from __future__ import annotations

import argparse
import base64
import html
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[3]
COURSES = ROOT / "courses"
MOTIFS = pathlib.Path(__file__).resolve().parent / "motifs"
WIDTH = 864
HEIGHT = 1080
SCALE = 6  # the card is 144x180; everything below is authored at that times six
THUMBNAIL = "assets/cover.png"


# ---------------------------------------------------------------- colour
#
# Every fill is a solid colour, and every group of courses that belongs together
# shares one.  The freetalking and hangul entries are computed rather than
# chosen: `measure_motifs.py` reports each motif's own colours and how light it
# is, and each fill is the one furthest from those colours in CIE Lab, at a depth
# set by how light the object is.  Re-derive them with that script if a motif
# changes.  The rest are set by hand, because they cover a family whose members
# use several different motifs and so have no single artwork to read.

CORE_BAND = {
    # The speech-bubble motif is 255deg and almost nothing else, so the ladder
    # walks 148 -> 180 -> 208 -> 240 -> 292 and only nears purple where the fill
    # is dark enough that the bubbles separate on lightness instead.
    "BEGINNER": "#28AA64",            # 148deg   3.0:1
    "UPPER_BEGINNER": "#1B9090",      # 180deg   3.9:1
    "INTERMEDIATE": "#1C71BB",        # 208deg   5.1:1
    "UPPER_INTERMEDIATE": "#4444D3",  # 240deg   7.0:1
    "ADVANCED": "#6F227A",            # 292deg   9.6:1
}

FAMILY_FILL = {
    "drama": "#D62056",     # 342deg  5.0:1
    "kpop": "#8F5CE2",      # 263deg  4.4:1
    "travel": "#1B8586",    # 180deg  4.4:1
    "banmal": "#DF6A11",    # 26deg   3.4:1
    "business": "#7535DB",  # 263deg  6.4:1
    "trial": "#33405F",     # a deep neutral, so all four trial motifs read on it
    "hangul": "#3C51CE",    # hangul   231deg  dE 97.8  (derived)
}

TALK_FILL = {
    # hue, then how far the fill sits from the motif's own colours in CIE Lab.
    # The floor is dE 45 — below that the ground starts to swallow the object.
    "me-lately": "#B42DA7",              # memories    306deg  dE 62.6
    "things-i-like": "#1B6B1B",          # thinking    120deg  dE 63.9
    "small-things": "#2C5AB1",           # thinking    219deg  dE 47.1
    "people-and-ties": "#1B646D",        # people      186deg  dE 46.0
    "love-and-marriage": "#982670",      # romance     321deg  dE 46.7
    "work-and-money": "#28A128",         # work-money  120deg  dE 61.7
    "between-two-countries": "#964CD2",  # countries   273deg  dE 68.3
    "what-if": "#256395",                # what-if     207deg  dE 50.0
    "what-came-before": "#C2305C",       # memories    342deg  dE 71.4
    "worth-thinking-about": "#1A6A4A",   # thinking    156deg  dE 66.9
    "balance-games": "#A6362A",          # balance       6deg  dE 86.8
}


# ---------------------------------------------------------------- families
#
# A family is the unit a learner compares within: the thing the rail header does
# not already say.  It drives the fill, the pill, and whether a course is
# numbered.

# The pill is chrome, so it is written in the language the learner is supported
# in — Japanese for both corpora, because both serve the JP market
# (`countryCode: JP`).  The title beside it is the language being taught.  That
# is the split the Korean covers already used and the English ones now match.
#
# It is also what makes the pill fit.  English level words are long: `Upper
# Intermediate` on its own is most of the 120 px a pill has, and
# `Business 4 · Upper Intermediate` overflows by a third.  `中上級` is three
# characters, and it is the word on the filter chip a JP learner is looking at.
#
# `フリートーク` is also what the trial report already calls this track
# (`tools/course-card-ja.json`).
FAMILY_LABEL = {
    "core": "パターン",
    "hangul": "ハングル",
    "trial": "体験",
    "drama": "ドラマ",
    "kpop": "K-POP",
    "travel": "旅行",
    "banmal": "タメ口",
    "business": "ビジネス",
    "talk": "フリートーク",
}

# The five words a learner already sees on the level filter, verbatim from
# podo-app `apps/web/src/shared/config/i18n/messages/{ko,ja,en}.json`
# (`subscribeList.filters.level.*`).  Taking them from there rather than parsing
# them out of the title is what makes the cover and the filter chip agree — and
# it is why CEFR is gone from the covers: `A2–B1` and `B1+` are not buckets the
# filter has, so a course could not be filtered to the level it claimed.
LEVEL_WORD = {"BEGINNER": "初級", "UPPER_BEGINNER": "初中級", "INTERMEDIATE": "中級",
              "UPPER_INTERMEDIATE": "中上級", "ADVANCED": "上級"}

# Families whose courses run in a fixed order, so the pill carries the position.
# Korean travel is not one of them — 식당 · 쇼핑 · 숙소 · 길 are four places on one
# trip, not four steps — but the English travel and business runs are ordered by
# classLevel from A2 to C1, so there the number is a fact rather than a promise.
NUMBERED = ("core", "drama", "kpop", "banmal", "business")


def numbered(lang: str, family: str) -> bool:
    return family in NUMBERED or (lang == "en" and family == "travel")


def family_of(lang: str, slug: str) -> str:
    if slug.startswith("trial-"):
        return "trial"
    if "hangul" in slug:
        return "hangul"
    if slug.startswith("core-"):
        return "core"
    if slug.startswith("talk-"):
        return "talk"
    if "drama" in slug:
        return "drama"
    if "kpop" in slug:
        return "kpop"
    if "banmal" in slug:
        return "banmal"
    if "business" in slug:
        return "business"
    if "travel" in slug:
        return "travel"
    return "talk"


def talk_topic_key(slug: str) -> str:
    """`talk-me-lately-advanced` -> `me-lately`, across both corpora's suffixes."""
    body = slug[len("talk-"):]
    for suffix in ("-intermediate", "-advanced", "-accessible", "-full"):
        if body.endswith(suffix):
            return body[: -len(suffix)]
    return body


def motif_for(lang: str, slug: str) -> str:
    if "hangul" in slug:
        return "hangul"
    if slug.startswith("trial-"):
        if "lv1" in slug:
            return "hangul" if lang == "kr" else "patterns"
        if "lv2" in slug:
            return "patterns"
        if "lv3" in slug:
            return "romance" if lang == "kr" else "travel"
        return "freetalk"
    if slug.startswith("core-"):
        if any(key in slug for key in ("daily-life", "experience")):
            return "memories"
        if any(key in slug for key in ("work", "diplomacy", "careful", "nuance")):
            return "business"
        if any(key in slug for key in ("plans", "stance")):
            return "what-if"
        return "patterns"
    if "kpop" in slug:
        return "kpop"
    if "travel-eating" in slug or "hotels-food" in slug:
        return "dining"
    if "travel-shopping" in slug:
        return "shopping"
    if "travel-staying" in slug:
        return "lodging"
    if "travel" in slug:
        return "travel"
    if "business" in slug:
        return "work-money" if any(k in slug for k in ("projects", "leadership")) else "business"
    if "drama" in slug:
        if any(key in slug for key in ("family", "friends", "boundaries")):
            return "people"
        if "long-distance" in slug:
            return "countries"
        return "romance"
    if "banmal" in slug:
        return "people"
    if slug.startswith("talk-"):
        key = talk_topic_key(slug)
        return {
            "balance-games": "balance", "between-two-countries": "countries",
            "love-and-marriage": "romance", "me-lately": "memories",
            "what-came-before": "memories", "people-and-ties": "people",
            "what-if": "what-if", "work-and-money": "work-money",
        }.get(key, "thinking")
    return "patterns"


def palette_for(lang: str, slug: str, difficulty: str) -> str:
    family = family_of(lang, slug)
    if family == "core":
        return CORE_BAND.get(difficulty, CORE_BAND["INTERMEDIATE"])
    if family == "talk":
        return TALK_FILL.get(talk_topic_key(slug), "#3055C1")
    return FAMILY_FILL[family]


def shade(fill: str, factor: float = 0.88) -> str:
    """The barely-there second stop, so a flat fill still has a direction."""
    r, g, b = (int(fill[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(max(0, round(c * factor)) for c in (r, g, b))


# ---------------------------------------------------------------- copy

def _parts(text: str) -> list[str]:
    return [part.strip() for part in text.split(" · ") if part.strip()]


def topic_of(lang: str, family: str, titles: dict, ladder: int | None) -> str:
    """The one phrase on the cover that names what this course is about.

    English manifests carry the new shape — ``(Beginner) Core · First words`` —
    so the topic is what follows the family.  Korean still carries the old
    ``Track · Topic · Level`` and is rewritten in its own pass; until then this
    keeps the two readable side by side.
    """
    if lang == "en":
        text = re.sub(r"^\([^)]*\)\s*", "", titles["en"])
        return _parts(text)[-1]
    parts = _parts(titles["ko"])
    if family == "core":
        return f"핵심 패턴 {ladder}" if ladder else parts[-1]
    if family in ("hangul", "trial"):
        return parts[0]
    return parts[1] if len(parts) > 1 else parts[0]


def cover_copy(lang: str, slug: str, titles: dict, difficulty: str,
               place: tuple[int, int] | None) -> tuple[str, str]:
    """(pill, title).

    One shape for both corpora: ``family [position] · level``.  The level word
    comes from ``difficulty`` through ``LEVEL_WORD``, never from the title — that
    is the only way the cover, the line under it and the filter chip can all say
    the same thing.

        ドラマ 2 · 中級   パターン 3 · 初級   旅行 1 · 中級   フリートーク · 上級
    """
    family = family_of(lang, slug)
    label = FAMILY_LABEL[family]
    level = LEVEL_WORD.get(difficulty, difficulty)
    ladder, band = place if place else (None, None)
    title = topic_of(lang, family, titles, ladder)

    if numbered(lang, family) and ladder:
        return f"{label} {ladder} · {level}", title
    return f"{label} · {level}", title


# ---------------------------------------------------------------- position
#
# Two families need to know where a course sits among its siblings, and the
# manifests do not say — `classLevel` does, because it is the catalogue order.

def positions(paths: list[pathlib.Path]) -> dict[pathlib.Path, tuple[int, int]]:
    """(position in the family, position inside this level band), in catalogue order.

    `classLevel` is the catalogue order, so it is what both counts read.  Only
    enabled courses count, so retiring one closes the gap instead of leaving a
    hole in the numbering.
    """
    rows = []
    for path in paths:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))["spec"]
        if not spec.get("enabled"):
            continue
        lang, slug = path.parts[-3], path.parent.name
        rows.append((lang, family_of(lang, slug), float(spec["classLevel"]),
                     spec.get("difficulty", ""), path))

    ladder: dict[pathlib.Path, int] = {}
    band: dict[pathlib.Path, int] = {}
    for key in {(lang, family) for lang, family, _, _, _ in rows}:
        run = sorted(r for r in rows if (r[0], r[1]) == key)
        for index, row in enumerate(run, start=1):
            ladder[row[4]] = index
        for difficulty in {r[3] for r in run}:
            inner = [r for r in run if r[3] == difficulty]
            for index, row in enumerate(inner, start=1):
                band[row[4]] = index
    return {path: (ladder[path], band[path]) for path in ladder}


# ---------------------------------------------------------------- layout

# Advance widths of Pretendard Bold, in em x 100, for ASCII 32-126 in order.
# Measured once with Pillow; baked so this file needs no font library. A guessed
# ratio is not good enough here — the pill is sized from this, and estimating a
# space at .42 when it is .23 is what made the pill stop hugging its text.
_ASCII_EM = (
    "2331386263966520393954652945283766476164666364586464282865656554877264727059"
    "5673722755665588717562756363647072996970643937394746485661566157376160262656"
    "26886059616139543760568255565539363965"
)
_CJK_EM = {"H": 0.938, "K": 0.938, "L": 0.864}  # hiragana/katakana, hangul


def char_width(char: str) -> float:
    """Advance width in em, at the weight the covers are set in."""
    code = ord(char)
    if 32 <= code <= 126:
        offset = (code - 32) * 2
        return int(_ASCII_EM[offset:offset + 2]) / 100
    if char == "\u00b7":
        return 0.28
    if 0x3040 <= code <= 0x30FF or 0xFF66 <= code <= 0xFF9F:
        return _CJK_EM["K"]
    if 0xAC00 <= code <= 0xD7A3 or 0x1100 <= code <= 0x11FF:
        return _CJK_EM["L"]
    if unicodedata.east_asian_width(char) in ("W", "F"):
        return 1.0
    return 0.55


def visual_width(text: str) -> float:
    return sum(char_width(c) for c in text)


def wrap(text: str, limit: float) -> list[str]:
    """At most two lines, breaking on whitespace and never inside a word."""
    if visual_width(text) <= limit:
        return [text]
    points = [m.start() for m in re.finditer(r"\s+", text)]
    if not points:
        return [text]
    _, _, point = min(
        (max(visual_width(text[:p]), visual_width(text[p:])),
         abs(visual_width(text[:p]) - visual_width(text[p:])), p)
        for p in points
    )
    first, second = text[:point].strip(), text[point:].strip()
    return [first, second] if first and second else [text]


def motif_href(course_root: pathlib.Path, motif: str) -> str:
    asset = MOTIFS / f"{motif}.png"
    return pathlib.Path(pathlib.os.path.relpath(asset, course_root / "assets")).as_posix()


def svg_for(course_path: pathlib.Path, doc: dict, place: tuple[int, int] | None) -> str:
    lang = course_path.parts[-3]
    slug = course_path.parent.name
    spec = doc["spec"]
    difficulty = spec.get("difficulty", "")
    motif = motif_for(lang, slug)
    fill = palette_for(lang, slug, difficulty)
    pill, title = cover_copy(lang, slug, spec["title"], difficulty, place)

    s = SCALE
    pad = 12 * s
    pill_h = round(18.5 * s)
    pill_y = 11 * s
    # The pill has the card's width minus its own margins, and nothing else.
    # Shrink rather than overflow — a clipped pill is worse than a small one.
    pill_room = (144 - 24) * s
    pill_font = 10 * s
    if (visual_width(pill) * pill_font + 16 * s) > pill_room:
        # No floor: the pill fitting is the invariant. If this ever shrinks far
        # enough to notice, the label is too long and the label is what to fix.
        pill_font = int((pill_room - 16 * s) / visual_width(pill))
    pill_w = round(visual_width(pill) * pill_font + 16 * s)

    title_font = 17 * s
    lines = wrap(title, 6.9)
    if len(lines) == 1 and visual_width(lines[0]) > 6.9:
        title_font = round(17 * s * 6.9 / visual_width(lines[0]))
    line_h = round(title_font * 1.16)
    title_top = pill_y + pill_h + round(5 * s)
    title_nodes = "\n".join(
        f'    <text x="{pad}" y="{title_top + round(title_font * .80) + i * line_h}"'
        f' class="title" font-size="{title_font}">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )

    motif_path = html.escape(motif_href(course_path.parent, motif))
    motif_x, motif_w = 16 * s, (144 - 16 - 4) * s
    motif_h, motif_bottom = 96 * s, 8 * s

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="430" y2="1080" gradientUnits="userSpaceOnUse">
      <stop stop-color="{fill}"/>
      <stop offset=".46" stop-color="{fill}"/>
      <stop offset="1" stop-color="{shade(fill)}"/>
    </linearGradient>
    <linearGradient id="scrim" x1="0" y1="0" x2="0" y2="{round(HEIGHT * .48)}" gradientUnits="userSpaceOnUse">
      <stop stop-color="#000000" stop-opacity=".26"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect width="{WIDTH}" height="{HEIGHT}" rx="48"/></clipPath>
    <style>
      text {{ font-family: Pretendard, "Hiragino Sans", sans-serif; }}
      .pill {{ fill: #fff; font-weight: 700; letter-spacing: -.2px; }}
      .title {{ fill: #fff; font-weight: 700; letter-spacing: -3px; }}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/>
    <circle cx="{round(78 * s)}" cy="{round(115 * s)}" r="{round(86 * s)}" fill="none" stroke="#FFFFFF" stroke-opacity=".075" stroke-width="{14 * s}"/>
    <rect width="{WIDTH}" height="{round(HEIGHT * .48)}" fill="url(#scrim)"/>

    <image x="{motif_x}" y="{HEIGHT - motif_bottom - motif_h}" width="{motif_w}" height="{motif_h}" preserveAspectRatio="xMidYMax meet" href="{motif_path}" xlink:href="{motif_path}"/>

    <rect x="{pad}" y="{pill_y}" width="{pill_w}" height="{pill_h}" rx="{pill_h // 2}" fill="#000000" fill-opacity=".42"/>
    <text x="{pad + round(8 * s)}" y="{pill_y + pill_h // 2 + round(pill_font * .35)}" class="pill" font-size="{pill_font}">{html.escape(pill)}</text>
{title_nodes}
  </g>
</svg>
'''


# ---------------------------------------------------------------- write

def ensure_thumbnail(raw: str) -> str:
    line = f"  thumbnail: {THUMBNAIL}"
    if re.search(r"(?m)^  thumbnail:", raw):
        return re.sub(r"(?m)^  thumbnail:.*$", line, raw)
    marker = "\n  tutorGroups:"
    if marker not in raw:
        raise RuntimeError("course manifest has no spec.tutorGroups insertion point")
    return raw.replace(marker, f"\n  thumbnail: {THUMBNAIL}\n{marker}", 1)


def png_dimensions(path: pathlib.Path) -> tuple[int, int]:
    raw = path.read_bytes()[:24]
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", raw[16:24])


def render(svg_path: pathlib.Path, png_path: pathlib.Path,
           resource_root: pathlib.Path | None = None) -> None:
    """Render with external motif PNGs embedded for librsvg.

    Browsers resolve the editable SVG's relative image href normally.  librsvg
    deliberately refuses a resource outside the SVG's own directory, so the
    deterministic render path substitutes a data URL in a temporary copy.
    """
    base = resource_root or svg_path.parent
    raw = svg_path.read_text(encoding="utf-8")

    def inline(match: re.Match[str]) -> str:
        attr, rel = match.group(1), match.group(2)
        payload = base64.b64encode((base / rel).resolve().read_bytes()).decode("ascii")
        return f'{attr}="data:image/png;base64,{payload}"'

    embedded = re.sub(r'((?:xlink:)?href)="([^"\n]+\.png)"', inline, raw)
    with tempfile.NamedTemporaryFile(suffix=".svg") as handle:
        handle.write(embedded.encode("utf-8"))
        handle.flush()
        subprocess.run(
            ["rsvg-convert", "--width", str(WIDTH), "--height", str(HEIGHT),
             "--output", str(png_path), handle.name],
            check=True,
        )


def discover() -> list[pathlib.Path]:
    return sorted(COURSES.glob("*/*/course.yaml"))


def generate(course_path: pathlib.Path, place: tuple[int, int] | None, check: bool) -> list[str]:
    raw = course_path.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    expected_manifest = ensure_thumbnail(raw)
    expected_svg = svg_for(course_path, doc, place)
    assets = course_path.parent / "assets"
    svg_path = assets / "cover.svg"
    png_path = assets / "cover.png"
    errors: list[str] = []

    if check:
        if raw != expected_manifest:
            errors.append(f"{course_path.relative_to(ROOT)}: thumbnail is missing or stale")
        if not svg_path.is_file() or svg_path.read_text(encoding="utf-8") != expected_svg:
            errors.append(f"{svg_path.relative_to(ROOT)}: generated SVG is stale")
        if not png_path.is_file():
            errors.append(f"{png_path.relative_to(ROOT)}: generated PNG is missing")
            return errors
        if png_dimensions(png_path) != (WIDTH, HEIGHT):
            errors.append(f"{png_path.relative_to(ROOT)}: expected {WIDTH}x{HEIGHT}")
        if png_path.stat().st_size >= 2 * 1024 * 1024:
            errors.append(f"{png_path.relative_to(ROOT)}: exceeds the 2 MiB cover cap")
        with tempfile.TemporaryDirectory() as tmp:
            probe_svg = pathlib.Path(tmp) / "cover.svg"
            probe_png = pathlib.Path(tmp) / "cover.png"
            probe_svg.write_text(expected_svg, encoding="utf-8")
            render(probe_svg, probe_png, svg_path.parent)
            if probe_png.read_bytes() != png_path.read_bytes():
                errors.append(f"{png_path.relative_to(ROOT)}: rendered PNG is stale")
        return errors

    assets.mkdir(parents=True, exist_ok=True)
    course_path.write_text(expected_manifest, encoding="utf-8")
    svg_path.write_text(expected_svg, encoding="utf-8")
    render(svg_path, png_path)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify without writing")
    parser.add_argument("--only", metavar="LANG/SLUG", help="generate one course")
    args = parser.parse_args()

    if shutil.which("rsvg-convert") is None:
        print("rsvg-convert is required", file=sys.stderr)
        return 2

    everything = discover()
    place = positions(everything)  # numbering always reads the whole catalogue
    paths = everything
    if args.only:
        wanted = COURSES / args.only / "course.yaml"
        paths = [path for path in paths if path == wanted]
        if not paths:
            print(f"unknown course: {args.only}", file=sys.stderr)
            return 2

    errors: list[str] = []
    for path in paths:
        errors.extend(generate(path, place.get(path), args.check))

    if errors:
        print("\n".join(f"ERROR {error}" for error in errors), file=sys.stderr)
        return 1
    verb = "verified" if args.check else "generated"
    print(f"{verb} {len(paths)} course covers at {WIDTH}x{HEIGHT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
