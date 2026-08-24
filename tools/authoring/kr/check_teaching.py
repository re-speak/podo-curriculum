#!/usr/bin/env python3
"""Verify the seven rules that govern every teaching surface in a deck.

They exist because an audit of 535 뜻과 쓰임 boxes found the same four habits
everywhere, and none of them is visible while you are writing one deck:

  1  ANCHOR      a pN-teach box is the .anchor slot plus ONE spoken sentence.
                 The Japanese equivalent lives in .anchor-ja with its Hangul
                 reading in .anchor-ko; the sentence that used to quote the
                 Japanese inline is gone. Prose has no floor, and where the
                 author could not name a Japanese counterpart the sentence grew
                 into a paragraph — every deck in core-upper-intermediate-1/2
                 and core-advanced-1 had no anchor and ran 149-154 자 against a
                 beginner median of 94.

  2  SPOKEN JA   no Japanese script in a line the tutor reads aloud (.ko,
                 .tutor-note is exempt — see below). Korean tutors are not
                 assumed to read Japanese, and 313 spoken lines handed them
                 kana to say out loud. If the Japanese is useful, it belongs in
                 .tutor-note WITH a Hangul reading in parentheses.

  3  LESSON REF  no lesson numbers, anywhere — prose, tutor notes, diagram
                 labels, chips. Neither a tutor nor a learner can resolve "90과"
                 on sight. Name the form instead.

  4  TAIL        no boilerplate close. 제가 읽을게요. 잘 듣고 따라 읽어 보세요.
                 was identical on 246 of 255 boxes: 21% of the median box
                 carrying no information a tutor does not already have.

  5  LENGTH      a teach box's spoken line stays at or under LIMIT 자. The
                 blueprint has asked for two sentences since it was written and
                 got 3% compliance, because prose does not hold a line. This is
                 the number that does.

  6  COUNT       no sentence whose whole content is a count of what is already
                 on the screen. 「네 문장이에요.」 stood on 126 read-along pages
                 beside the four sentences it was counting, and 「네 개예요.」 on
                 five more. Rule 4 deliberately left these alone — a count
                 folded INTO an instruction (네 문장을 따라 읽어 보세요) is that
                 page's instruction — so this rule fires only on a sentence that
                 is nothing but the count. A find-all page is exempt: there the
                 number is the stop condition, not a description ('웨'로 읽는
                 글자를 모두 눌러 보세요. 세 개예요.).

  7  COPY        settled, exact Hangul-track copy conventions extracted from
                 repeated native review: name mixed real-world items as words,
                 omit visible setup narration, use the established listening
                 prompt, and make recovery-note subjects explicit.

Rule 5's budget is deliberately loose (the contextual track's own median is 48)
— it is a backstop against paragraphs, not a style gauge.

  python3 tools/authoring/kr/check_teaching.py                    # whole repo
  python3 tools/authoring/kr/check_teaching.py <deck…>            # named decks
  python3 tools/authoring/kr/check_teaching.py 2-core-patterns    # one track
  python3 tools/authoring/kr/check_teaching.py --rule ref         # one rule
"""
import argparse
import re
import sys
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"

LIMIT = 60            # 자, the spoken line of an anchored teach box
UNANCHORED_LIMIT = 90 # 자, a box with no anchor — it carries the meaning too
# A rule page's subtitle is the tutor's line while pointing at a diagram, so it
# needs more room than a teach box. 90 was the corpus's own 75th percentile —
# a backstop that flags a quarter of all rule pages is measuring the median,
# not the outliers. The real rule for these pages is qualitative (a subtitle
# never recites what the diagram beside it already draws) and cannot be a
# length; 105 is p90, which catches the paragraphs.
RULE_LIMIT = 105

TAG = re.compile(r"<[^>]+>")
PID = re.compile(r'data-page-id="([^"]+)"')
KO = re.compile(r'<span class="ko">(.*?)</span>', re.S)
TUTOR = re.compile(r'<div class="tutor-note">(.*?)</div>', re.S)
PM = re.compile(r'<p class="section-subtitle pattern-meaning"[^>]*>(.*?)</p>', re.S)
SUB = re.compile(r'<p class="section-subtitle"[^>]*>(.*?)</p>', re.S)
ANCHOR = re.compile(r'<span class="anchor">\s*<span class="anchor-ja">(.*?)</span>'
                    r'\s*<span class="anchor-ko">(.*?)</span>\s*</span>', re.S)

# kana, kanji, halfwidth katakana. NOT the 「」 quotes, which are punctuation.
JA_SCRIPT = re.compile(r"[぀-ヿ㐀-䶿一-鿿ｦ-ﾟ]")
# 「N과」 / 「N課」 / 「68~70과」.
# The first version ended in (?![가-힣]) to keep the particle 과 out. That was
# wrong twice over: it silently skipped every real reference written 68과에서는
# or 66과의 — 과 followed by Hangul is the NORMAL shape — and it did not
# exclude the particle anyway, because "파트 1과 똑같아요" has a space after 과.
# 과 as a conjunctive particle is genuinely ambiguous with 과 as "lesson", so
# the one form this curriculum actually writes is excluded by name below.
LESSON_REF = re.compile(r"(?<![가-힣0-9])\d+\s*[~～\-–]?\s*\d*\s*[과課]")
PARTICLE_CTX = re.compile(r"파트\s*$")
TAIL = re.compile(r"(제가 읽을게요|읽어 드릴게요|들려 드릴게요|잘 듣고 따라 읽어|"
                  r"따라 읽어 ?보세요|한 번에 읽을게요|이어서 읽을게요)")

# A sentence that is only a count. 「네 문장이에요」 / 「세 개예요」 — no verb,
# no instruction, nothing the learner cannot see by looking.
BARE_COUNT = re.compile(
    r"^(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|스무|\d+)\s*"
    r"(개|문장|줄|가지)(이에요|예요|입니다)[.!]?$")
# …unless the line asks the learner to find them all, where the count is what
# tells them when to stop hunting rather than what they are looking at.
FIND_ALL = re.compile(r"모두.*(눌러|골라|찾)")

RULES = ("anchor", "spoken-ja", "ref", "tail", "length", "count", "copy")

# Hangul copy conventions extracted from repeated native-review feedback. These
# are deliberately exact and track-scoped: broader wording choices still need
# human judgment, while these phrases have one established replacement.
HANGUL_COPY = (
    (re.compile(r"간판 읽기|한국에 있다고 상상해 보세요\. 간판"),
     "마무리 활동은 ‘단어 읽기’ 말투로 통일함"),
    (re.compile(r"(?:이번엔 |이번에도 |이제 )?색(?:도)?이? 없(?:고|어요)"),
     "화면에서 보이는 색 제거를 대본으로 설명함"),
    (re.compile(r"위에 (?:쓴|쓰여져)"),
     "‘위에 쓰여 있는’으로 자연스럽게 지칭함"),
    (re.compile(r"제가 읽(?:을게요|어 볼게요)\. 듣고 맞는 쪽을 눌러 보세요\."),
     "튜터 모델링 뒤에는 ‘잘 듣고’를 씀"),
    (re.compile(r"말만 할게요\. 듣고 글자 세 개"),
     "듣고 만들기도 ‘잘 듣고’로 통일함"),
    (re.compile(r"(?<!정답으로 )표시된 (?:쪽|단어|두 글자|세 개)"),
     "튜터 메모는 ‘정답으로 표시된’으로 대상을 분명히 함"),
)


def strip(s):
    return re.sub(r"\s+", " ", TAG.sub("", s)).strip()


QUOTE_OPEN, QUOTE_CLOSE = "“‘「『", "”’」』"


def sentences(t):
    """Count sentences the way shared/js/script-lines.js does.

    These decks cite expressions mid-sentence — 장소는 ‘어디예요?’예요 — so a
    naive split on .!? reports two sentences where the tutor says one. Same
    trap the migration script hit; the fix is the same: punctuation inside a
    quote does not end a sentence, and in Korean the mark must be followed by
    whitespace or end-of-string because a citation is glued to its particle.
    """
    out, cur, depth = [], "", 0
    for i, ch in enumerate(t):
        cur += ch
        if ch in QUOTE_OPEN:
            depth += 1
        elif ch in QUOTE_CLOSE and depth:
            depth -= 1
        elif ch in ".!?" and not depth:
            if i + 1 >= len(t) or t[i + 1].isspace():
                out.append(cur.strip())
                cur = ""
    if cur.strip():
        out.append(cur.strip())
    return out


def pages(src):
    """(page-id, chunk) for every data-page-id in document order"""
    idx = [(m.start(), m.group(1)) for m in PID.finditer(src)]
    for i, (pos, pid) in enumerate(idx):
        end = idx[i + 1][0] if i + 1 < len(idx) else len(src)
        yield pid, src[pos:end]


COMMENT = re.compile(r"<!--.*?-->", re.S)


def check(path, want):
    # Authoring comments are not a teaching surface. They are written in
    # English and discuss the lesson — "they are 과 3 과 1 material" tripped the
    # lesson-number rule on a deck that had no reference in it at all.
    src = COMMENT.sub("", Path(path).read_text(encoding="utf-8"))
    path_s = str(Path(path).as_posix())
    needs_anchor = "/2-core-patterns/" in path_s
    is_hangul = "/1-hangul/" in path_s or "trial-1-hangul" in path_s
    out = []

    def hit(rule, pid, detail, text):
        if rule in want:
            out.append((rule, pid, detail, text))

    for pid, chunk in pages(src):
        pm = PM.search(chunk)

        # ---- rule 1: a teach box carries an anchor slot and one sentence ----
        # The anchor is required in 2-core-patterns, where the Japanese
        # equivalent was already in the deck (183 boxes quoted it inline, and
        # the ones that had stopped quoting it are exactly the ones that grew
        # to 150 자). It is NOT required in 3-contextual-korean: no box there
        # contains a word of Japanese, so nothing is being moved — an anchor
        # would mean authoring 208 new Japanese lines for a Japanese-native
        # audience, which is translation work and a separate decision. That
        # track's problem is register, which no character count can see.
        if pm:
            inner = pm.group(1)
            ko = strip(KO.search(inner).group(1)) if KO.search(inner) else ""
            anchored = bool(ANCHOR.search(inner))
            if needs_anchor:
                if not anchored:
                    hit("anchor", pid, "뜻과 쓰임 상자에 .anchor 슬롯이 없음", ko)
                elif not strip(ANCHOR.search(inner).group(2)):
                    hit("anchor", pid, ".anchor-ko 읽기가 비어 있음", ko)
            # an anchored box has one job left; an unanchored one still has to
            # say what the form is as well as when to reach for it
            cap, maxs = (LIMIT, 1) if anchored else (UNANCHORED_LIMIT, 2)
            n = len(sentences(ko))
            if n > maxs:
                hit("anchor", pid, f"말하는 줄이 {n}문장 ({maxs}문장 이하여야 함)", ko)
            if len(ko) > cap:
                hit("length", pid, f"{len(ko)}자 > {cap}", ko)

        # ---- rule 5b: a rule page's subtitle ----
        elif "rule" in pid:
            sb = SUB.search(chunk)
            if sb:
                ko = strip(KO.search(sb.group(1)).group(1)) if KO.search(sb.group(1)) else ""
                if len(ko) > RULE_LIMIT:
                    hit("length", pid, f"{len(ko)}자 > {RULE_LIMIT}", ko)

        # ---- rule 2: no Japanese in a line the tutor says out loud ----
        # .anchor-ja is the one place Japanese belongs — it is shown, not said,
        # and .anchor-ko is what the tutor reads. .tutor-note is never read
        # aloud, so Japanese is allowed there (with a reading, rule 2b).
        body = ANCHOR.sub("", chunk)
        for m in KO.finditer(body):
            ko = strip(m.group(1))
            if JA_SCRIPT.search(ko):
                found = "".join(sorted(set(JA_SCRIPT.findall(ko))))
                hit("spoken-ja", pid, f"소리 내어 읽는 줄에 일본어 [{found}]", ko)

            # ---- rule 6: a sentence that only counts what is on screen ----
            if not FIND_ALL.search(ko):
                for sent in sentences(ko):
                    if BARE_COUNT.match(sent):
                        hit("count", pid, f"화면을 세기만 하는 문장 ‘{sent}’", ko)

        # ---- rule 2b: Japanese in a tutor note needs its Hangul reading ----
        for m in TUTOR.finditer(chunk):
            note = strip(m.group(1))
            if is_hangul and re.search(r"(?:^|[.!?]\s+)막히면\b", note):
                hit("copy", pid, "누가 막히는지 ‘학생이’를 밝힘", note)
            for run in re.finditer(r"[぀-ヿ㐀-䶿一-鿿]+", note):
                if not run.group().strip("っーぁぃぅぇぉゃゅょ"):
                    continue          # 촉음·장음부호는 제 소리가 없다
                # Japanese punctuation may sit between the word and its
                # reading — 「時間ありますか？(지칸아리마스카)」
                after = note[run.end():run.end() + 4].lstrip("？！。、」』")
                if not after.startswith("(") and not after.startswith("（"):
                    hit("spoken-ja", pid,
                        f"튜터 노트의 ‘{run.group()}’에 한글 읽기가 없음", note)
                    break

        # ---- rule 3: lesson numbers, in any element on the page ----
        for m in LESSON_REF.finditer(chunk):
            if PARTICLE_CTX.search(chunk[max(0, m.start() - 12):m.start()]):
                continue                      # 파트 1과 — the particle 과
            seg = strip(chunk[max(0, m.start() - 60):m.end() + 30])
            hit("ref", pid, f"‘{m.group().strip()}’ 참조", seg)

        # ---- rule 4: the boilerplate close ----
        # Only inside a 뜻과 쓰임 box. On a pN-read page "네 문장을 천천히 따라
        # 읽어 보세요" is the page's actual instruction, not boilerplate — the
        # first cut of this rule flagged 238 of those and the number was
        # meaningless until the scope was right.
        if pm:
            ko = strip(KO.search(pm.group(1)).group(1)) if KO.search(pm.group(1)) else ""
            if TAIL.search(ko):
                hit("tail", pid, "상투적 마무리", ko)

        # ---- rule 7: settled Hangul-track copy conventions ----
        if is_hangul:
            visible = strip(chunk)
            for pattern, detail in HANGUL_COPY:
                m = pattern.search(visible)
                if m:
                    hit("copy", pid, detail, m.group())

    return out


def deck_paths(paths, every):
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [TRACKS]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
    ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
    ap.add_argument("--rule", help=f"one of {', '.join(RULES)}")
    args = ap.parse_args(argv)

    want = set(RULES)
    if args.rule:
        want = {args.rule}
        bad = want - set(RULES)
        if bad:
            print(f"unknown rule {bad}; pick from {RULES}")
            return 2
    paths = deck_paths(args.paths, args.all)

    tally, decks = Counter(), Counter()
    for p in paths:
        rows = check(p, want)
        if not rows:
            continue
        print(f"\n### {Path(p).parents[2].name}/{Path(p).parent.name}")
        for rule, pid, detail, text in rows:
            print(f"  [{rule:<9}] {pid:<18} {detail}")
            if text:
                print(f"      {text[:120]}")
            tally[rule] += 1
        decks[Path(p).parents[2].name] += len(rows)

    total = sum(tally.values())
    print(f"\n{len(paths)} deck(s) · {total} finding(s)")
    for r in RULES:
        if r in want:
            print(f"   {r:<10}{tally[r]}")
    if decks:
        print("\n  worst decks:")
        for d, n in decks.most_common(8):
            print(f"   {d:<48}{n}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
