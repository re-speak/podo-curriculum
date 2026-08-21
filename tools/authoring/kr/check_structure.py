#!/usr/bin/env python3
"""Structural audit of written lesson decks. Deterministic checks only —
the things an agent is expected to verify about itself and seven of them
did not live long enough to."""
import argparse
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"
DEFAULT = TRACKS / "2-core-patterns"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errs = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errs.append(f"stray </{tag}> line {self.getpos()[0]}")
        elif self.stack[-1][0] != tag:
            self.errs.append(
                f"</{tag}> line {self.getpos()[0]} closes <{self.stack[-1][0]}> "
                f"opened line {self.stack[-1][1]}")
            self.stack.pop()
        else:
            self.stack.pop()


def audit(deck: Path):
    src = deck.read_text(encoding="utf-8")
    bad = []

    b = Balance()
    b.feed(src)
    bad += b.errs[:3]
    if b.stack:
        bad.append("unclosed: " + ", ".join(f"<{t}> L{l}" for t, l in b.stack[:3]))

    # identity
    slug = deck.parent.name
    lid = re.search(r'podo:lesson-id" content="([^"]*)', src)
    if not lid or lid.group(1) != slug:
        bad.append(f"lesson-id {lid and lid.group(1)!r} != dir {slug!r}")
    lvl = re.search(r'podo:level" content="([^"]*)', src)
    for t in ("ko", "en", "ja"):
        if f'podo:title-{t}"' not in src:
            bad.append(f"missing podo:title-{t}")
    if "notranslate" not in src:
        bad.append("missing notranslate meta")

    # a deck ships no CSS or JS of its own
    if re.search(r"<style[\s>]", src):
        bad.append("inline <style>")
    for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", src, re.S):
        if m.group(1).strip():
            bad.append("inline <script>")
            break

    # Lemonboard validates the source HTML without running activities.js. A
    # synced placeholder span therefore has no resolvable kind even if runtime
    # code later replaces it with an input. Controls must be static in markup.
    legacy = re.findall(
        r'<span class="(?:slot|answer-space)"\s+data-sync-id="([^"]+)"', src)
    if legacy:
        bad.append(f"runtime-promoted control shell(s): {legacy[:3]}")

    # shared state must be uniquely addressed
    dup = [i for i, n in Counter(re.findall(r'data-sync-id="([^"]+)"', src)).items() if n > 1]
    if dup:
        bad.append(f"dup data-sync-id: {dup[:3]}")
    dpi = [i for i, n in Counter(re.findall(r'data-page-id="([^"]+)"', src)).items() if n > 1]
    if dpi:
        bad.append(f"dup data-page-id: {dpi[:3]}")

    # the first surviving page must carry the act the cover used to supply
    first = re.search(r'<[^>]*data-page-id="([^"]+)"([^>]*)>', src)
    if first and "data-act" not in first.group(2):
        bad.append(f"first page {first.group(1)!r} has no data-act")

    # refs
    for r in re.findall(r'(?:href|src)="((?:\.\./)+[^"]+)"', src):
        if not (deck.parent / r).resolve().is_file():
            bad.append(f"dead ref {r}")

    pages = len(re.findall(r"data-page-id=", src))
    return pages, (lvl.group(1) if lvl else "?"), src.count("yomi"), bad


def deck_paths(paths, every):
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [DEFAULT]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
args = ap.parse_args()

fails = 0
for d in deck_paths(args.paths, args.all):
    pages, lvl, yomi, bad = audit(d)
    if not pages:
        continue
    tag = "✓" if not bad else "✗"
    print(f"{tag} {d.parent.name:<26} {pages:>3}p  {lvl:<4} yomi={yomi:<4}")
    for x in bad:
        fails += 1
        print(f"    ! {x}")
print(f"\n{fails} problem(s)")
# Every finding here is mechanical — a stray tag, a duplicate sync id, a ref
# that resolves to nothing. None of them needs a human to decide, so they fail.
sys.exit(1 if fails else 0)
