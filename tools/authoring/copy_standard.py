#!/usr/bin/env python3
"""Enforce the settled copy decisions a native proofreader already made once.

A proofreading round produces two things: corrections to the lines that were
read, and a *reason* those lines were wrong. Only the first has ever landed in
this repository. The second evaporated, so the next batch of decks re-grew the
same habit and the same colleague wrote the same comment again — 이번엔 진짜 was
softened once in PR #89, was still standing in 88 places, and came back in PR
#116 on four separate courses across four separate days.

This check is the second half. Each rule names a decision a human made, quotes
the evidence, and then holds the whole corpus to it.

Two rule kinds, because a bilingual deck has two kinds of mistake:

  run    a phrase anywhere in the visible text, scoped by the classes of the
         elements above it. 덩어리 is wrong in an instruction the learner reads
         and right in a tutor note about prosody, and only the scope can tell
         those apart.

  pair   a Korean line and its Japanese line inside one bilingual block, decided
         together. This kind exists because the corpus proved it has to: of the
         88 decks that still said 이번엔 진짜, 85 said 本当 in Japanese and the two
         that had been corrected said 본인 / ご自身. Correct one side and the deck
         now teaches two different things to the tutor and the learner, and
         nothing reports it.

The rules are per-language data, not code:

    tools/authoring/kr/copy-standard.json
    tools/authoring/en/copy-standard.json

The mechanism is shared because it is not about Korean. Any curriculum that gets
proofread accumulates settled wording, and a rule filed under one language is a
rule the other language re-derives a week later.

    python3 tools/authoring/copy_standard.py                 # both languages
    python3 tools/authoring/copy_standard.py --lang kr       # one language
    python3 tools/authoring/copy_standard.py --rule chunk    # one rule
    python3 tools/authoring/copy_standard.py --fix           # rewrite decks
    python3 tools/authoring/copy_standard.py --list          # print the standard

`--fix` only applies a rule that carries an exact replacement. A rule with no
replacement is a judgment the tool refuses to make for you: it reports the line
and the reviewer's reasoning and stops.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DRAFTS = REPO / "sandbox/drafts"
LANGS = ("kr", "en")

# A comment, a tag, or a run of text between them. Decks are generated,
# well-formed and script-free, so a scanner is enough and pulls in no dependency
# the CI image would have to install. Comments come first in the alternation
# because authoring notes inside them are prose, and prose full of the very
# words these rules hunt for — the first cut of this scanner reported a note
# explaining why 덩어리 is the right word there.
TOKEN = re.compile(r"<!--.*?-->"
                   r"|<(/?)([a-zA-Z][\w-]*)((?:\"[^\"]*\"|'[^']*'|[^>\"'])*?)(/?)>"
                   r"|([^<]+)", re.S)
CLASSES = re.compile(r"""\bclass\s*=\s*["']([^"']*)["']""")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
OPAQUE = {"script", "style"}  # markup, never copy


class Run:
    """One text run plus the element classes open above it."""

    __slots__ = ("text", "start", "end", "classes")

    def __init__(self, text, start, end, classes):
        self.text, self.start, self.end, self.classes = text, start, end, classes

    def scoped(self, allow, deny):
        if deny and self.classes & deny:
            return False
        return not allow or bool(self.classes & allow)


def runs(src):
    """Every text run in `src`, tagged with the classes of its ancestors."""
    out, stack, opaque = [], [], 0
    for m in TOKEN.finditer(src):
        if m.group().startswith("<!--"):
            continue
        text = m.group(5)
        if text is not None:
            if not opaque and text.strip():
                seen = frozenset().union(*(c for _, c in stack)) if stack else frozenset()
                out.append(Run(text, m.start(5), m.end(5), seen))
            continue
        closing, name = m.group(1), m.group(2).lower()
        attrs, self_closing = m.group(3), m.group(4)
        if closing:
            if name in OPAQUE:
                opaque = max(0, opaque - 1)
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
            continue
        if name in VOID or self_closing:
            continue
        if name in OPAQUE:
            opaque += 1
        cls = CLASSES.search(attrs)
        stack.append((name, frozenset(cls.group(1).split()) if cls else frozenset()))
    return out


def blocks(src, container, left, right):
    """Bilingual blocks: (whole span, left text span, right text span).

    `container` is the class on the wrapping element; `left`/`right` are the
    classes on the two language spans inside it. Returned as offsets so an edit
    can be spliced back without re-serialising the deck.
    """
    pat = re.compile(rf'<(\w+)[^>]*\bclass="[^"]*\b{re.escape(container)}\b[^"]*"[^>]*>(.*?)</\1>',
                     re.S)
    # Blank out comments in place so a commented-out block is never matched and
    # every offset below still points at the real file.
    masked = re.sub(r"<!--.*?-->", lambda m: " " * len(m.group()), src, flags=re.S)
    out = []
    for m in pat.finditer(masked):
        inner, base = m.group(2), m.start(2)
        found = {}
        for side, cls in (("left", left), ("right", right)):
            s = re.search(rf'<span class="{re.escape(cls)}">(.*?)</span>', inner, re.S)
            if s:
                found[side] = (base + s.start(1), base + s.end(1), s.group(1))
        if "left" in found:
            out.append((m.start(), found["left"], found.get("right")))
    return out


class Rule:
    def __init__(self, raw):
        self.id = raw["id"]
        self.why = raw["why"]
        self.kind = raw.get("kind", "run")
        self.manual = raw.get("manual")
        self.exempt = re.compile(raw["exempt"]) if raw.get("exempt") else None
        if self.kind == "glossary":
            self.allow = frozenset(raw.get("only_in", ()))
            self.deny = frozenset(raw.get("never_in", ()))
            self.glosses = raw["glosses"]
            self.find = re.compile("|".join(map(re.escape, self.glosses)))
            return
        if self.kind == "run":
            self.allow = frozenset(raw.get("only_in", ()))
            self.deny = frozenset(raw.get("never_in", ()))
            self.edits = [(re.compile(e["from"]), e["to"]) for e in raw.get("fix", ())]
            # A mechanical rule reports exactly what it would rewrite. Deriving
            # `find` from the replacements is not a convenience — a hand-written
            # `find` that is broader than the fixes makes the rule fire on its own
            # output, and the gate then never goes green no matter how many decks
            # you correct.
            self.find = re.compile(raw["find"]) if "find" in raw else re.compile(
                "|".join(f"(?:{e['from']})" for e in raw["fix"]))
        else:
            self.container = raw.get("container", "section-subtitle")
            self.left = raw.get("left", "ko")
            self.right = raw.get("right", "ja")
            self.find = re.compile(raw["find"])
            self.cases = [(re.compile(c["when"]),
                           [(re.compile(e["from"]), e["to"]) for e in c.get("left", ())],
                           [(re.compile(e["from"]), e["to"]) for e in c.get("right", ())])
                          for c in raw.get("cases", ())]

    @property
    def fixable(self):
        if self.kind == "glossary":
            return True
        return bool(self.edits) if self.kind == "run" else bool(self.cases)

    @staticmethod
    def _apply(text, edits):
        for pattern, to in edits:
            text = pattern.sub(to, text)
        return text

    def run_hits(self, run):
        if self.exempt and self.exempt.search(run.text):
            return []
        if not run.scoped(self.allow, self.deny):
            return []
        return [m.group() for m in self.find.finditer(run.text)]

    def pair_case(self, ko):
        for when, left, right in self.cases:
            if when.search(ko):
                return left, right
        return None


def load(lang):
    path = REPO / "tools/authoring" / lang / "copy-standard.json"
    if not path.exists():
        return []
    return [Rule(r) for r in json.loads(path.read_text(encoding="utf-8"))["rules"]]


PAGE_ID = re.compile(r'data-page-id="')


def is_deck(p):
    """check_deck.py's test: any page carrying data-page-id.

    Globbing for `lesson.html` — which every Korean check did — silently misses
    every trial deck, because those are named for their track
    (`trial/full-trials/trial-1-hangul.html`). They are the first lesson a
    prospect ever sees and nothing had ever checked their copy; PR #116's
    reviewer found 위에 쓴 대로 there, a phrasing the Hangul track had had a rule
    against for months.
    """
    if {"_archive", "archive"} & set(p.parts) or p.name.startswith("_"):
        return False
    if p.name == "viewer.html":
        return False
    try:
        return bool(PAGE_ID.search(p.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError):
        return False


def deck_paths(lang):
    root = DRAFTS / lang
    return sorted(p for p in root.rglob("*.html") if is_deck(p)) if root.exists() else []


TAG = re.compile(r"<[^>]+>")


def plain(s):
    return re.sub(r"\s+", " ", TAG.sub("", s)).strip()


def scan(path, rules, fix):
    src = path.read_text(encoding="utf-8")
    found, edits = [], []

    run_rules = [r for r in rules if r.kind == "run"]
    if run_rules:
        for run in runs(src):
            new = run.text
            for rule in run_rules:
                hits = rule.run_hits(run)
                if not hits:
                    continue
                for hit in hits:
                    found.append((rule, hit, plain(run.text)))
                if fix and rule.fixable:
                    new = rule._apply(new, rule.edits)
            if fix and new != run.text:
                edits.append((run.start, run.end, new))

    for rule in (r for r in rules if r.kind == "glossary"):
        # A gloss counts only if the learner has already met it. The vocabulary
        # strip glosses 생카 and 택포 on a later page, and the reviewer still
        # asked what they meant — so the test is position, not presence: the
        # first learner-facing use must be at or after a glossed one.
        for term, gloss in rule.glosses.items():
            glossed = [m.start() for m in
                       re.finditer(re.escape(term) + r"\s*[(（]", src)]
            first = min(glossed) if glossed else None
            for run in runs(src):
                if not run.scoped(rule.allow, rule.deny):
                    continue
                m = re.search(re.escape(term) + r"(?!\s*[(（])", run.text)
                if not m:
                    continue
                at = run.start + m.start()
                if first is not None and first <= at:
                    break
                found.append((rule, term, plain(run.text)))
                if fix:
                    edits.append((at, at + len(term), term + gloss))
                break

    for rule in (r for r in rules if r.kind == "pair"):
        for _, (ls, le, ltext), right in blocks(src, rule.container, rule.left, rule.right):
            ko = plain(ltext)
            if not rule.find.search(ko):
                continue
            if rule.exempt and rule.exempt.search(ko):
                continue
            found.append((rule, rule.find.search(ko).group(), ko))
            if not fix:
                continue
            case = rule.pair_case(ko)
            if not case:
                continue
            left_edits, right_edits = case
            new_left = rule._apply(ltext, left_edits)
            if new_left != ltext:
                edits.append((ls, le, new_left))
            if right and right_edits:
                rs, re_, rtext = right
                new_right = rule._apply(rtext, right_edits)
                if new_right != rtext:
                    edits.append((rs, re_, new_right))

    if fix and edits:
        # Splice from the end so earlier offsets stay valid. Overlaps cannot
        # happen: a run and a bilingual span are disjoint text nodes.
        for start, end, new in sorted(edits, key=lambda e: e[0], reverse=True):
            src = src[:start] + new + src[end:]
        path.write_text(src, encoding="utf-8")
    return found


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files or directories")
    ap.add_argument("--lang", choices=LANGS, help="one curriculum (default: both)")
    ap.add_argument("--rule", help="one rule id")
    ap.add_argument("--fix", action="store_true", help="apply the exact replacements")
    ap.add_argument("--list", action="store_true", help="print the standard and exit")
    ap.add_argument("--quiet", action="store_true", help="counts only")
    args = ap.parse_args(argv)

    langs = [args.lang] if args.lang else list(LANGS)

    if args.list:
        for lang in langs:
            rules = load(lang)
            print(f"\n=== {lang} — {len(rules)} rule(s) ===")
            for r in rules:
                print(f"\n  [{'fix ' if r.fixable else 'read'}] {r.id}   ({r.kind})")
                print(f"      {r.why}")
                if r.manual:
                    print(f"      → {r.manual}")
        return 0

    total, tally, hit_decks, manual = 0, Counter(), set(), Counter()
    for lang in langs:
        rules = load(lang)
        if args.rule:
            rules = [r for r in rules if r.id == args.rule]
            if not rules:
                continue
        if args.paths:
            targets = []
            for p in map(Path, args.paths):
                targets += sorted(p.rglob("lesson.html")) if p.is_dir() else [p]
        else:
            targets = deck_paths(lang)
        for path in targets:
            found = scan(path, rules, args.fix)
            if not found:
                continue
            hit_decks.add(path)
            rel = path.relative_to(REPO)
            if not args.quiet:
                print(f"\n### {rel.parent.parent.parent.name}/{rel.parent.name}")
            for rule, hit, line in found:
                total += 1
                tally[rule.id] += 1
                if not rule.fixable:
                    manual[rule.id] += 1
                if not args.quiet:
                    verb = "fixed" if (args.fix and rule.fixable) else "  •  "
                    print(f"  [{verb}] {rule.id:<26} {hit}")
                    print(f"           {line[:112]}")

    print(f"\n{total} finding(s) in {len(hit_decks)} deck(s)")
    for rid, n in tally.most_common():
        note = "   (needs a human)" if manual.get(rid) == n else ""
        print(f"   {rid:<28}{n}{note}")
    if args.fix:
        print("\napplied every exact replacement; rules with no replacement are untouched")
        return 0
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
