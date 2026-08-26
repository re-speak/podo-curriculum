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

  pill    the sub-family and the level — ``ドラマ 1 · 中級``, ``パターン 5 · 初中級``.
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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import course_naming  # noqa: E402  (path set above)
from course_naming import cover_copy, family_of  # noqa: E402


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
    "hangul": "#1A6D1A",   # hangul  120deg  6.41:1  echo, second colour
}

TALK_FILL = {
    # The artwork's own colour, deepened until the object separates on lightness.
    # Where several land on one hue they fan out inside it — four blues twenty
    # degrees apart, not a blue and a green. Re-derive with `measure_motifs.py --fills`.
    "me-lately":           "#247998",  # memories    196deg   4.87:1  echo, 4 on this hue (fanned 14 deg)
    "things-i-like":       "#8149D4",  # thinking    264deg   5.46:1  echo, second colour, 5 on this hue (fanned 6 deg)
    "small-things":        "#8C2CBC",  # thinking    280deg   6.56:1  echo, second colour, 5 on this hue (fanned 10 deg)
    "people-and-ties":     "#A82F28",  # people        4deg   6.77:1  echo, 2 on this hue (fanned 4 deg)
    "love-and-marriage":   "#A0254B",  # romance     342deg   7.34:1  echo, 2 on this hue (fanned 4 deg)
    "work-and-money":      "#5B8CD9",  # work-money  217deg    3.4:1  echo, second colour, 4 on this hue (fanned 7 deg)
    "between-two-countries":"#1D7D74",  # countries   174deg    4.9:1  echo, 4 on this hue (fanned 21 deg)
    "what-if":             "#3D51D1",  # what-if     232deg   6.38:1  echo, 5 on this hue (fanned 23 deg)
    "what-came-before":    "#4F53D6",  # memories    238deg   5.97:1  echo, 4 on this hue (fanned 28 deg)
    "worth-thinking-about":"#8A2292",  # thinking    296deg   7.66:1  echo, second colour, 5 on this hue (fanned 26 deg)
    "balance-games":       "#5844D3",  # balance     248deg    6.6:1  echo, 5 on this hue (fanned 7 deg)
}


# ---------------------------------------------------------------- families
#
# A family is the unit a learner compares within: the thing the rail header does
# not already say.  It drives the fill, the pill, and whether a course is
# numbered.

# The pill words, the level words, the family names and the ladder position all
# live in ../course_naming.py, because the line under the card and the PR gate
# read the same ones. A table that only the cover read is how the cover came to
# say 初級 on a course the filter called UPPER_BEGINNER. What is left here is the
# colour, which nothing outside this file has an opinion about.


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


def svg_for(course_path: pathlib.Path, doc: dict, rung: int | None) -> str:
    lang = course_path.parts[-3]
    slug = course_path.parent.name
    spec = doc["spec"]
    difficulty = spec.get("difficulty", "")
    motif = motif_for(lang, slug)
    fill = palette_for(lang, slug, difficulty)
    pill, title = cover_copy(lang, slug, spec["title"], difficulty, rung)

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


def generate(course_path: pathlib.Path, rung: int | None, check: bool) -> list[str]:
    raw = course_path.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    expected_manifest = ensure_thumbnail(raw)
    expected_svg = svg_for(course_path, doc, rung)
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


def rungs_for(paths: list[pathlib.Path]) -> dict[pathlib.Path, int]:
    """`course_naming.ladder`, keyed by path — the only thing this script has."""
    rows = [course_naming.Row(path.parts[-3], path.parent.name,
                              float(spec["classLevel"]), spec.get("difficulty", ""),
                              bool(spec.get("enabled")), spec["title"])
            for path, spec in ((p, yaml.safe_load(p.read_text(encoding="utf-8"))["spec"])
                               for p in paths)]
    place = course_naming.ladder(rows)
    return {path: place[(path.parts[-3], path.parent.name)] for path in paths
            if (path.parts[-3], path.parent.name) in place}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify without writing")
    parser.add_argument("--only", metavar="LANG/SLUG", help="generate one course")
    args = parser.parse_args()

    if shutil.which("rsvg-convert") is None:
        print("rsvg-convert is required", file=sys.stderr)
        return 2

    everything = discover()
    rungs = rungs_for(everything)  # numbering always reads the whole catalogue
    paths = everything
    if args.only:
        wanted = COURSES / args.only / "course.yaml"
        paths = [path for path in paths if path == wanted]
        if not paths:
            print(f"unknown course: {args.only}", file=sys.stderr)
            return 2

    errors: list[str] = []
    for path in paths:
        errors.extend(generate(path, rungs.get(path), args.check))

    if errors:
        print("\n".join(f"ERROR {error}" for error in errors), file=sys.stderr)
        return 1
    verb = "verified" if args.check else "generated"
    print(f"{verb} {len(paths)} course covers at {WIDTH}x{HEIGHT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
