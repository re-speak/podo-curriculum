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

A background is then scored by its perceptual distance from those colours, not
by hue angle. Hue angle was the first attempt and it does not work: greens sprawl
across 90-170 degrees and still read as one colour, so a ground 51 degrees off a
green globe is still a green ground. CIE Lab distance says so and hue arithmetic
does not.
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


def main() -> None:
    print(f"{'motif':12} {'colours (hue @ share)':40} lightness")
    for path in sorted(MOTIFS.glob("*.png")):
        _, light, ranked = dominant(path)
        shown = " ".join(f"{h}@{m:.0%}" for h, m in ranked)
        print(f"{path.stem:12} {shown:40} {light:.3f}")


if __name__ == "__main__":
    main()
