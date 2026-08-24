#!/usr/bin/env python3
"""Find inline citations that AUTHORING.md § 인용한 표현 says must be quoted.

    python3 tools/authoring/check_quotes.py                    # the Korean drafts (default)
    python3 tools/authoring/check_quotes.py path/to/lesson.html ...
    python3 tools/authoring/check_quotes.py sandbox/drafts/en/tracks
    python3 tools/authoring/check_quotes.py --all              # every deck in the repo
    python3 tools/authoring/check_quotes.py --strict …         # + the punctuation rules

The rule: an expression the deck teaches, pulled into a sentence as-is, gets
wrapped — ‘ ’ inside .ko, 「 」 inside .ja. Straight quotes are never used.

Detection follows 42d1dd4's own heuristic: a run of *target-language script*
sitting inside Japanese prose is by definition a citation, so every such run in
a .ja span must already be inside 「 」. Where a .ja span is flagged, its paired
.ko span is printed too, because the two lines must be quoted in the same places.

Two corpora, two scripts
------------------------
In a Korean deck the taught expression is hangul, and hangul inside Japanese
prose can only be a citation — the heuristic needs no further qualification.

In an English deck the taught expression is Latin, and Latin inside Japanese
prose is very often *not* a citation: role labels (Me, Traveller), loanwords and
acronyms (AI, MBTI, SNS), and morphology labels (-ing 形) all read as Latin runs.
So the English side additionally requires the run to be an expression the deck
itself marks as taught — the `podo:title-en` meta, a `<b>`, a `span.ending`, or
the English half of a `.sent-hero`. That set is deliberately narrow; see
`README` note in `en_offenders()` for what it knowingly misses.

Which corpus a file belongs to is read off the deck (`podo:target-language`) or
its path, never a flag, so `--all` does the right thing per file.
"""
import argparse
import html
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]

TAG = re.compile(r"<[^>]+>")
# a .ja span is Japanese prose only if it actually contains kana
KANA = re.compile(r"[぀-ヿ]")
PAIR = re.compile(
    r'<span class="ko">(.*?)</span>\s*<span class="ja">(.*?)</span>', re.S)

HANGUL = re.compile(r"[가-힣]+(?:[\s··][가-힣]+)*[?!.]?")
# the Latin analogue: a word, or words joined by the punctuation English uses
# inside one expression (space, comma, hyphen, slash, apostrophe, blank "___")
LATIN = re.compile(
    r"[A-Za-z][A-Za-z0-9'’]*(?:[ ,\-–—/_.'’]+[A-Za-z0-9_][A-Za-z0-9'’]*)*[?!.]?")
LATIN_LETTER = re.compile(r"[A-Za-z]")

TARGET_LANG = re.compile(
    r'<meta[^>]*\bname="podo:target-language"[^>]*\bcontent="([^"]*)"')
TITLE_EN = re.compile(
    r'<meta[^>]*\bname="podo:title-en"[^>]*\bcontent="([^"]*)"')
BOLD = re.compile(r"<b>(.*?)</b>", re.S)
ENDING = re.compile(r'<span class="ending">(.*?)</span>', re.S)
SENT_HERO = re.compile(r'<div class="sent-hero[^"]*">(.*?)</div>', re.S)
KOREAN_SPAN = re.compile(r'<span class="korean">(.*?)</span>', re.S)

# a single Latin word is only ever reported when the deck marks that exact word
# as taught, and even then only if it is long enough not to be noise
MIN_SINGLE_WORD = 4


def strip(s):
    return html.unescape(TAG.sub("", s))


def spans(text, open_ch="「", close_ch="」"):
    """the character ranges already inside a quote pair"""
    out, depth, start = [], 0, None
    for i, c in enumerate(text):
        if c == open_ch:
            if depth == 0:
                start = i
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0 and start is not None:
                out.append((start, i))
                start = None
    return out


def _outside(text, pattern):
    """every match of `pattern` in `text` that is not already inside 「 」"""
    inside = spans(text)
    for m in pattern.finditer(text):
        a, b = m.span()
        if any(s <= a and b - 1 <= e for s, e in inside):
            continue
        yield m


def unquoted(ja):
    """Korean: every hangul run in a .ja span that is not inside 「 」"""
    return [m.group().strip() for m in _outside(ja, HANGUL)]


# ---------------------------------------------------------------- English side

def normalise(s):
    """fold an English expression to its comparable core"""
    s = html.unescape(s).lower()
    s = re.sub(r"[_…]+", " _ ", s)
    s = re.sub(r"[^a-z0-9'’_ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _latin_only(s):
    return bool(LATIN_LETTER.search(s)) and not KANA.search(s)


def taught_expressions(src):
    """the strings an English deck itself marks as the thing being taught.

    Four markers, all of them the deck's own claim about its target — not a
    guess made from the prose: the generated title, a `<b>`, a `span.ending`
    (the highlighted chunk of a model line), and the English half of a
    `.sent-hero` pattern card.
    """
    out = set()
    m = TITLE_EN.search(src)
    if m:
        out.add(normalise(m.group(1)))
    for pattern in (BOLD, ENDING):
        for m in pattern.finditer(src):
            text = strip(m.group(1))
            if _latin_only(text):
                out.add(normalise(text))
    for hero in SENT_HERO.finditer(src):
        for m in KOREAN_SPAN.finditer(hero.group(1)):
            text = strip(m.group(1))
            if _latin_only(text):
                out.add(normalise(text))
    return {s for s in out if s}


def _holds(haystack, needle):
    """word-boundary containment on normalised English"""
    return re.search(r"(?:^| )" + re.escape(needle) + r"(?:$| )",
                     haystack) is not None


def en_unquoted(ja, taught):
    """English: Latin runs in a .ja span that the deck marks as taught.

    Two passes. The first only accepts a run that matches the taught set — a
    multi-word run that contains or is contained by a multi-word taught
    expression, or a single word the deck bolds/highlights verbatim. The second
    pass runs only on a line the first already flagged: once a sentence is known
    to be citing, its other multi-word Latin runs are the contrast partner of
    that citation ("A は…、B は…") and need the same wrapping.

    Knowingly missed: a line whose *only* citations are contrast partners that
    the deck never marks as taught. Recovering those means trusting bare Latin
    in Japanese prose, which is exactly the rule that fires on every loanword.
    """
    runs = [(m.group().strip(), normalise(m.group()))
            for m in _outside(ja, LATIN)]
    runs = [(raw, norm) for raw, norm in runs if norm]

    hits, seen = [], set()
    for raw, norm in runs:
        words = norm.split()
        for t in taught:
            if len(words) >= 2 and len(t.split()) >= 2 and (
                    _holds(t, norm) or _holds(norm, t)):
                break
            if len(words) == 1 and norm == t and len(norm) >= MIN_SINGLE_WORD:
                break
        else:
            continue
        if norm not in seen:
            seen.add(norm)
            hits.append(raw)
    if not hits:
        return []
    for raw, norm in runs:
        if len(norm.split()) >= 2 and norm not in seen:
            seen.add(norm)
            hits.append(raw)
    return hits


# ------------------------------------------------------------- strict extras

# 조사는 밖에 둡니다 — ‘어때?’만, not ‘어때?만’
KO_PARTICLE_INSIDE = re.compile(r"[?!.][가-힣]{1,3}$")
JA_PARTICLE_INSIDE = re.compile(r"[?!.？！。][ぁ-んァ-ヶ]{1,3}$")
KO_QUOTE = re.compile(r"‘([^‘’]*)’")
JA_QUOTE = re.compile(r"「([^「」]*)」")
# 곧은 따옴표는 쓰지 않습니다
STRAIGHT = re.compile(r"'[^'\n]{1,60}'|\"[^\"\n]{1,60}\"")


def strict_notes(lang, ko, ja):
    """the documented rules the citation scan itself cannot see"""
    notes = []
    for m in STRAIGHT.finditer(ko):
        notes.append(f"straight quote in .ko: {m.group()}")
    for m in STRAIGHT.finditer(ja):
        notes.append(f"straight quote in .ja: {m.group()}")
    if lang != "kr":
        # the period/particle rules are written for Korean and Japanese
        # punctuation; English prose has its own (contested) convention and no
        # postpositional particles, so nothing here is portable to it.
        return notes
    for m in KO_QUOTE.finditer(ko):
        if KO_PARTICLE_INSIDE.search(m.group(1)):
            notes.append(f"particle inside the quote in .ko: {m.group()}")
        if m.group(1).endswith("."):
            notes.append(f"period inside the quote in .ko: {m.group()}")
    for m in JA_QUOTE.finditer(ja):
        if JA_PARTICLE_INSIDE.search(m.group(1)):
            notes.append(f"particle inside the quote in .ja: {m.group()}")
        if m.group(1).endswith("。"):
            notes.append(f"period inside the quote in .ja: {m.group()}")
    return notes


# ------------------------------------------------------------------- driving

def language_of(path, src):
    """which corpus a deck belongs to — the deck's own claim, then its path"""
    m = TARGET_LANG.search(src)
    if m:
        return "en" if m.group(1).strip().lower() == "en" else "kr"
    parts = [p.lower() for p in pathlib.Path(path).parts]
    if "en" in parts:
        return "en"
    if "kr" in parts or "ko" in parts:
        return "kr"
    return "en" if not re.search(r"[가-힣]", src) else "kr"


def deck_rows(path, src, strict=False):
    """(citations, ko, ja, notes) for every offending .ko/.ja pair"""
    lang = language_of(path, src)
    taught = taught_expressions(src) if lang == "en" else None
    rows = []
    for m in PAIR.finditer(src):
        ko, ja = strip(m.group(1)), strip(m.group(2))
        if not KANA.search(ja):
            continue
        hits = unquoted(ja) if lang == "kr" else en_unquoted(ja, taught)
        notes = strict_notes(lang, ko, ja) if strict else []
        if hits or notes:
            rows.append((hits, ko, ja, notes))
    return rows


def collect(roots):
    targets = []
    for r in roots:
        r = pathlib.Path(r)
        if r.is_dir():
            targets += sorted(p for p in r.rglob("*.html")
                              if "_archive" not in p.parts
                              and p.name != "viewer.html")
        elif r.exists():
            targets.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return [p for p in targets
            if PAIR.search(p.read_text(encoding="utf-8"))]


def main(paths, strict=False):
    total = 0
    for p in paths:
        src = pathlib.Path(p).read_text(encoding="utf-8")
        rows = deck_rows(p, src, strict)
        if rows:
            print(f"\n### {pathlib.Path(p).parent.name}  — {len(rows)} line(s)")
            for hits, ko, ja, notes in rows:
                print(f"  citations: {hits}")
                print(f"    ko: {ko[:150]}")
                print(f"    ja: {ja[:150]}")
                for n in notes:
                    print(f"    ! {n}")
        total += len(rows)
    print(f"\n{len(paths)} deck(s) · {total} line(s) with an unquoted citation")
    return 1 if total else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files or directories to scan")
    ap.add_argument("--all", action="store_true",
                    help="scan every deck in the repo")
    ap.add_argument("--strict", action="store_true",
                    help="also report straight quotes and misplaced "
                         "particles/periods inside an existing quote")
    args = ap.parse_args()

    if args.all:
        decks = collect([REPO])
    elif args.paths:
        decks = collect([pathlib.Path(p).resolve() for p in args.paths])
    else:
        decks = sorted(
            (REPO / "sandbox/drafts/kr/tracks").glob("**/lesson.html"))
    sys.exit(main([str(p) for p in decks], args.strict))
