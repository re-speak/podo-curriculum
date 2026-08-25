#!/usr/bin/env python3
"""Measure each motif's own colours, so a background can be chosen against the artwork.

The output is the ``MOTIF_COLOUR`` table in ``generate.py``. It is committed rather
than computed at generation time for two reasons: ``generate.py`` stays free of a
Pillow dependency (it only needs ``rsvg-convert``), and a reviewer can see the hues
in the diff instead of having to trust a measurement they cannot see.

Re-run it only when a motif PNG changes:

    python3 tools/authoring/course_covers/measure_motifs.py

What it reports per motif:

  colours    the artwork's own colours — one per hue bin it actually spends area
             on, averaged and weighted by saturation x lightness so highlights
             and outlines do not vote
  lightness  mean lightness of the opaque pixels. A pale object needs a deeper
             ground to separate from it; a dark one needs a lighter ground.

**The ground echoes the artwork.** It takes the artwork's own strongest colour and
deepens it until the object separates on lightness rather than on hue — the way a
pink phone sits on deep wine and a blue suitcase on teal. Five of the seven
hand-set family fills had already landed there by eye, which is why drama,
business and travel read as cohesive.

Two things can stop an echo, and then the ground steps to the artwork's next
colour rather than to an unrelated one:

  mud       hues from about 9 to 94 degrees turn to brown or olive once they are
            deep enough to hold white text, so a yellow lightbulb cannot have a
            yellow ground. It takes the purple of its own question marks instead.
  a sibling two courses cannot ship the same fill, and the toy artwork is mostly
            blue and purple, so echoes cluster. They fan out **inside** the
            neighbourhood the artwork put them in — a band of four blues becomes
            four blues twenty degrees apart, not a blue and a green. Depth stays
            where the object needs it, because that is what keeps the object off
            the ground.

Run it to re-derive the tables in `generate.py`:

    python3 tools/authoring/course_covers/measure_motifs.py --fills
"""

from __future__ import annotations

import colorsys
import pathlib
from collections import defaultdict

from PIL import Image

MOTIFS = pathlib.Path(__file__).resolve().parent / "motifs"
BIN = 15


def to_lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """sRGB 0-255 to CIE Lab, D65. Enough for "are these two colours alike"."""
    def linear(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def measure(path: pathlib.Path) -> tuple[dict[int, float], float]:
    image = Image.open(path).convert("RGBA")
    image.thumbnail((160, 160))
    raw = image.tobytes()
    pixels = [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]
    bins: dict[int, float] = defaultdict(float)
    sums: dict[int, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    total = 0.0
    lights: list[float] = []
    for r, g, b, a in pixels:
        if a < 200:
            continue
        hue, light, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        lights.append(light)
        if sat < 0.28 or not 0.12 < light < 0.88:
            continue
        weight = sat * light
        key = int(hue * 360) // BIN * BIN % 360
        bins[key] += weight
        for i, channel in enumerate((r, g, b)):
            sums[key][i] += channel * weight
        total += weight
    hues = {k: v / total for k, v in bins.items()} if total else {}
    colours = {k: tuple(c / bins[k] for c in sums[k]) for k in bins}
    return hues, (sum(lights) / len(lights) if lights else 0.5), colours


def dominant(path: pathlib.Path, floor: float = 0.08):
    """The artwork's own colours, as Lab, biggest area first."""
    hues, light, colours = measure(path)
    keep = sorted(((m, h) for h, m in hues.items() if m >= floor), reverse=True)
    return [to_lab(colours[h]) for _, h in keep], light, [(h, m) for m, h in keep]


# Hues that still read as a colour once they are deep enough to hold white text.
MUD = range(9, 95)


def deepens_well(hue: int) -> bool:
    return hue % 360 not in MUD


def gap(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def echo_hue(motif: str) -> tuple[float, str]:
    """The artwork's own colour — its strongest, or the strongest that is not mud.

    A yellow lightbulb cannot have a yellow ground, so it takes the purple of its
    own question marks. That is still an echo: the colour is in the picture.
    """
    ranked = dominant(MOTIFS / f"{motif}.png")[2]
    for hue, _share in ranked:
        if deepens_well(hue):
            return hue, "echo" if hue == ranked[0][0] else "echo, second colour"
    return ranked[0][0], "no colour in the artwork survives being deepened"


def main() -> None:
    print(f"{'motif':12} {'colours (hue @ share)':40} lightness")
    for path in sorted(MOTIFS.glob("*.png")):
        _, light, ranked = dominant(path)
        shown = " ".join(f"{h}@{m:.0%}" for h, m in ranked)
        print(f"{path.stem:12} {shown:40} {light:.3f}")


def fills() -> None:
    """Propose the derived tables in generate.py, in catalogue order."""
    import colorsys
    import math

    def hex_of(hue: float, sat: float, light: float) -> str:
        r, g, b = colorsys.hls_to_rgb(hue / 360, light, sat)
        return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))

    def contrast(hexv: str) -> float:
        channels = [int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 1.05 / (0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2] + 0.05)

    def solve(hue: float, sat: float, target: float) -> float:
        lo, hi = 0.02, 0.88
        for _ in range(60):
            mid = (lo + hi) / 2
            if contrast(hex_of(hue, sat, mid)) < target:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    # A pale object needs a deeper ground to separate from it; a dark one needs a
    # lighter ground. This is what lets an echo stay an echo without dissolving.
    def depth(motif: str) -> float:
        return round(3.4 + (dominant(MOTIFS / f"{motif}.png")[1] - 0.45) * 11.0, 2)

    # Freetalking, in classLevel order, then the one hangul course.
    plan = [
        ("me-lately", "memories"), ("things-i-like", "thinking"), ("small-things", "thinking"),
        ("people-and-ties", "people"), ("love-and-marriage", "romance"),
        ("work-and-money", "work-money"), ("between-two-countries", "countries"),
        ("what-if", "what-if"), ("what-came-before", "memories"),
        ("worth-thinking-about", "thinking"), ("balance-games", "balance"),
        ("hangul", "hangul"),
    ]
    chosen = [(key, motif) + echo_hue(motif) for key, motif in plan]

    # Anything landing within 22 degrees is one colour to the eye. A band fans out
    # across a span of its own, so four blues become four blues rather than a blue
    # and a green — the echo survives the crowding.
    bands: list[list[int]] = []
    for index, (_key, _motif, hue, _why) in enumerate(chosen):
        for band in bands:
            if gap(hue, chosen[band[0]][2]) < 22:
                band.append(index)
                break
        else:
            bands.append([index])

    def circular_mean(hues: list[float]) -> float:
        # 0 and 345 average to 352, not to 172. Sum unit vectors, not degrees.
        x = sum(math.cos(math.radians(h)) for h in hues)
        y = sum(math.sin(math.radians(h)) for h in hues)
        return math.degrees(math.atan2(y, x)) % 360

    fan: dict[int, float] = {}
    for band in bands:
        centre = circular_mean([chosen[i][2] for i in band])
        span = min(64.0, 22.0 * (len(band) - 1))
        # Fan in the order the artwork already sits in, so nobody crosses past a
        # sibling and ends up further from its own colour than it started.
        band = sorted(band, key=lambda i: (chosen[i][2] - centre + 540) % 360)
        for step, index in enumerate(band):
            offset = -span / 2 + (span * step / (len(band) - 1) if len(band) > 1 else 0)
            fan[index] = (centre + offset) % 360

    # Courses that share a motif share a silhouette too, so they take a step in
    # depth on top of the fan. Everything else keeps the depth its object asked for.
    step_of: dict[int, float] = {}
    for motif in {m for _, m, _, _ in chosen}:
        group = [i for i, (_, m, _, _) in enumerate(chosen) if m == motif]
        for rank, index in enumerate(group):
            step_of[index] = (rank - (len(group) - 1) / 2) * 1.1

    print(f"{'key':24} {'fill':9} {'motif':11} {'hue':>5} {'depth':>7}  how it was chosen")
    for index, (key, motif, hue, why) in enumerate(chosen):
        target = round(max(3.0, min(10.4, depth(motif) + step_of[index])), 2)
        placed = fan[index]
        band = [b for b in bands if index in b][0]
        note = why + (f", {len(band)} on this hue" if len(band) > 1 else "")
        moved = f" (fanned {gap(placed, hue):.0f} deg)" if gap(placed, hue) >= 1 else ""
        print(f'    "{key}":{" " * (20 - len(key))}"{hex_of(placed, 0.62, solve(placed, 0.62, target))}",'
              f'  # {motif:11} {placed:3.0f}deg  {target:>5}:1  {note}{moved}')


if __name__ == "__main__":
    import sys
    fills() if "--fills" in sys.argv else main()
