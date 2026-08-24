#!/usr/bin/env python3
"""Generate every deployable course cover from one Figma-derived visual system.

The editable inputs are the course manifests, this layout, and the transparent
motifs beside it.  The outputs live with each course as ``assets/cover.svg`` and
``assets/cover.png``; ``course.yaml`` points grape at the PNG.

    python3 tools/authoring/course_covers/generate.py
    python3 tools/authoring/course_covers/generate.py --check
    python3 tools/authoring/course_covers/generate.py --only kr/hangul-starter
"""

from __future__ import annotations

import argparse
import base64
import hashlib
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
THUMBNAIL = "assets/cover.png"


PALETTES = {
    # The first six are the fills measured from Figma node 1367:5422.
    "green":  ("#69CD73", "#43B95B", "#B7F0BC"),
    "purple": ("#7637E0", "#5120B9", "#BCA0F7"),
    "orange": ("#EE6619", "#C94A0B", "#FFC092"),
    "pink":   ("#F37297", "#D94A78", "#FFC0D2"),
    "navy":   ("#1A2D5E", "#101C42", "#7184B8"),
    "red":    ("#F0473D", "#C93632", "#FFAAA4"),
    # A travel extension of the same saturated/soft-highlight grammar.
    "blue":   ("#2F9AE4", "#176FBB", "#A9D9FA"),
}


MOTIF_PALETTES = {
    "hangul": ("green",),
    "patterns": ("green", "purple", "orange"),
    "kpop": ("pink", "purple"),
    "romance": ("pink", "red", "navy"),
    "travel": ("blue", "orange"),
    "dining": ("orange", "red"),
    "shopping": ("pink", "purple"),
    "lodging": ("navy", "blue"),
    "business": ("purple", "navy"),
    "freetalk": ("red", "pink", "navy"),
    "balance": ("purple", "orange"),
    "countries": ("blue", "green"),
    "work-money": ("navy", "orange"),
    "thinking": ("orange", "purple"),
    "memories": ("navy", "purple"),
    "people": ("green", "blue", "pink"),
    "what-if": ("purple", "navy"),
}


def stable_index(text: str, count: int) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16) % count


def discover() -> list[pathlib.Path]:
    return sorted(COURSES.glob("*/*/course.yaml"))


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
        if "makeup" in slug:
            return "patterns"
        return "romance"
    if "banmal" in slug:
        return "people"
    if "balance-games" in slug:
        return "balance"
    if "between-two-countries" in slug:
        return "countries"
    if "love-and-marriage" in slug:
        return "romance"
    if "me-lately" in slug or "what-came-before" in slug:
        return "memories"
    if "people-and-ties" in slug:
        return "people"
    if "what-if" in slug:
        return "what-if"
    if "work-and-money" in slug:
        return "work-money"
    if "worth-thinking-about" in slug or "small-things" in slug or "things-i-like" in slug:
        return "thinking"
    if slug.startswith("talk-"):
        return "freetalk"
    return "patterns"


def palette_for(slug: str, difficulty: str, motif: str) -> str:
    choices = list(MOTIF_PALETTES[motif])
    if difficulty == "ADVANCED":
        dark = [p for p in choices if p in ("navy", "purple", "red")]
        if dark:
            choices = dark
    elif difficulty in ("BEGINNER", "UPPER_BEGINNER"):
        light = [p for p in choices if p in ("green", "orange", "pink", "blue")]
        if light:
            choices = light
    return choices[stable_index(slug, len(choices))]


def cover_copy(lang: str, slug: str, titles: dict) -> tuple[str, str, str, str]:
    target_key = "ko" if lang == "kr" else "en"
    parts = [part.strip() for part in titles[target_key].split(" · ") if part.strip()]
    ja_parts = [part.strip() for part in titles["ja"].split(" · ") if part.strip()]
    if slug.startswith("trial-"):
        topic = parts[0]
        level = " · ".join(ja_parts[1:])
        track = "TRIAL"
    elif slug == "hangul-starter":
        topic = parts[0]
        level = " · ".join(ja_parts[1:])
        track = "HANGUL"
    elif slug.startswith("core-") and lang == "kr":
        topic = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        level = ja_parts[0]
        track = "CORE"
    else:
        topic = parts[1] if len(parts) > 1 else parts[0]
        level = " · ".join(ja_parts[2:]) if len(ja_parts) > 2 else ""
        if slug.startswith("core-"):
            track = "CORE"
        elif slug.startswith("talk-"):
            track = "TALK"
        elif "business" in slug:
            track = "BUSINESS"
        elif "travel" in slug:
            track = "TRAVEL"
        else:
            track = "SCENE"
    language = "KOREAN" if lang == "kr" else "ENGLISH"
    return language, track, topic, level


def visual_width(text: str) -> float:
    width = 0.0
    for char in text:
        if char.isspace():
            width += 0.5
        elif unicodedata.east_asian_width(char) in ("W", "F", "A"):
            width += 1.0
        else:
            width += 0.62
    return width


def split_title(text: str) -> list[str]:
    if visual_width(text) <= 9.4:
        return [text]
    break_chars = ("と", "の", "・", "への", "を")
    candidates: list[tuple[float, int]] = []
    total = visual_width(text)
    for i in range(1, len(text)):
        if text[i - 1] in break_chars or text[i] in break_chars:
            candidates.append((abs(visual_width(text[:i]) - total / 2), i))
    if candidates:
        _, point = min(candidates)
    else:
        target = total / 2
        point = min(range(1, len(text)), key=lambda i: abs(visual_width(text[:i]) - target))
    first, second = text[:point].strip(), text[point:].strip()
    return [first, second] if first and second else [text]


def title_size(lines: list[str]) -> int:
    widest = max(visual_width(line) for line in lines)
    if widest <= 6.5:
        return 88
    if widest <= 8.4:
        return 78
    return 68


def motif_href(course_root: pathlib.Path, motif: str) -> str:
    asset = MOTIFS / f"{motif}.png"
    return pathlib.Path(pathlib.os.path.relpath(asset, course_root / "assets")).as_posix()


def svg_for(course_path: pathlib.Path, doc: dict) -> str:
    lang = course_path.parts[-3]
    slug = course_path.parent.name
    spec = doc["spec"]
    motif = motif_for(lang, slug)
    palette_name = palette_for(slug, spec.get("difficulty", ""), motif)
    base, dark, highlight = PALETTES[palette_name]
    language, track, topic, level = cover_copy(lang, slug, spec["title"])
    lines = split_title(topic)
    font_size = title_size(lines)
    line_height = int(font_size * 1.05)
    title_y = 204
    title_nodes = "\n".join(
        f'    <text x="84" y="{title_y + i * line_height}" class="title" font-size="{font_size}">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    level_y = title_y + len(lines) * line_height + 28
    level_text = html.escape(level or spec.get("difficulty", ""))
    motif_path = html.escape(motif_href(course_path.parent, motif))
    sequence = f"{lang.upper()} · {track}"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="bg" x1="92" y1="50" x2="780" y2="1050" gradientUnits="userSpaceOnUse">
      <stop stop-color="{highlight}" stop-opacity=".24"/>
      <stop offset=".38" stop-color="{base}"/>
      <stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(650 790) rotate(112) scale(510 470)" gradientUnits="userSpaceOnUse">
      <stop stop-color="#FFFFFF" stop-opacity=".19"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="card"><rect width="864" height="1080" rx="48"/></clipPath>
    <style>
      text {{ font-family: Pretendard, "Hiragino Sans", sans-serif; }}
      .eyebrow {{ fill: #fff; font-size: 34px; font-weight: 800; letter-spacing: 1.2px; }}
      .title {{ fill: #fff; font-weight: 900; letter-spacing: -2.5px; }}
      .level {{ fill: #fff; fill-opacity: .72; font-size: 35px; font-weight: 700; letter-spacing: -.8px; }}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="864" height="1080" fill="url(#bg)"/>
    <circle cx="716" cy="708" r="322" fill="none" stroke="#FFFFFF" stroke-opacity=".07" stroke-width="92"/>
    <circle cx="695" cy="713" r="178" fill="none" stroke="#000000" stroke-opacity=".055" stroke-width="54"/>
    <path d="M-46 897C137 735 268 826 403 698C552 558 646 424 934 468" fill="none" stroke="#FFFFFF" stroke-opacity=".055" stroke-width="64" stroke-linecap="round"/>
    <rect width="864" height="1080" fill="url(#glow)"/>

    <text x="84" y="105" class="eyebrow">{html.escape(sequence)}</text>
    <rect x="678" y="66" width="106" height="58" rx="29" fill="#000000" fill-opacity=".22"/>
    <text x="731" y="105" text-anchor="middle" fill="#FFFFFF" font-size="26" font-weight="800">{html.escape(language[:2])}</text>
{title_nodes}
    <text x="86" y="{level_y}" class="level">{level_text}</text>

    <image x="166" y="390" width="760" height="640" preserveAspectRatio="xMidYMid meet" href="{motif_path}" xlink:href="{motif_path}"/>

    <text x="84" y="1004" fill="#FFFFFF" font-size="31" font-weight="900" letter-spacing="1.4">PODO</text>
    <text x="780" y="1004" text-anchor="end" fill="#FFFFFF" fill-opacity=".58" font-size="24" font-weight="700">{html.escape(track)}</text>
  </g>
</svg>
'''


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


def generate(course_path: pathlib.Path, check: bool) -> list[str]:
    raw = course_path.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    expected_manifest = ensure_thumbnail(raw)
    expected_svg = svg_for(course_path, doc)
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

    paths = discover()
    if args.only:
        wanted = COURSES / args.only / "course.yaml"
        paths = [path for path in paths if path == wanted]
        if not paths:
            print(f"unknown course: {args.only}", file=sys.stderr)
            return 2

    errors: list[str] = []
    for path in paths:
        errors.extend(generate(path, args.check))

    if errors:
        print("\n".join(f"ERROR {error}" for error in errors), file=sys.stderr)
        return 1
    verb = "verified" if args.check else "generated"
    print(f"{verb} {len(paths)} course covers at {WIDTH}x{HEIGHT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
