#!/usr/bin/env python3
"""Pedagogical audit of the freetalking track.

check_structure.py and tools/authoring/check_deck.py both verify *mechanics* —
tag balance, dead refs, duplicate sync-ids. Both reported 0 problems on a track
that contained a double-barrelled question, three 중급 decks whose page 2 was
byte-identical to the 고급 sibling, and page-2 lengths spanning 295–480 chars.

The reason 209 decks could drift in one commit is that the spec lived only as
prose in lesson-blueprint.md. This file is that prose made executable. When the
blueprint changes, change PROFILE in the same commit — and sample-lesson.html
too. The three are one spec in three forms.

    python3 tools/authoring/kr/check_freetalk.py              # blocking + warnings
    python3 tools/authoring/kr/check_freetalk.py <deck…>      # named decks
    python3 tools/authoring/kr/check_freetalk.py --warnings   # show soft findings
    python3 tools/authoring/kr/check_freetalk.py --write-baseline

Exit status is non-zero when a hard rule fails, so it works as a commit gate.
"""
import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KR = REPO / "sandbox/drafts/kr"
TRACKS = KR / "tracks"
TRACK = TRACKS / "4-freetalking"
BASELINE = Path(__file__).resolve().parent / "freetalk-baseline.json"

PROFILE = {
    # blueprint § 전체 골격 — 13장. article 은 예습 지문이다.
    # model-story 는 튜터가 소리 내어 읽던 옛 설계이고, 지금은 폐지 대상이다.
    "pages": ["lesson-goal", "article", "lesson-style", "talk-intro",
              "warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6", "feedback"],
    "page2_aliases": {"article", "model-story"},
    "questions": ["warm-1", "warm-2", "q1", "q2", "q3", "q4", "q5", "q6"],
    "article_sents": (10, 15),   # 혼자 읽는 글이므로 길이가 싸다
    "vocab_per_line": (2, 3),
    "followups": (2, 3),
    "goal_rows": 3,
    "levels": {"중급", "고급"},
    # 중급이 고급을 그대로 베끼면 두 레벨이 같은 덱이 된다. 판단이 필요하므로 경고다.
    "level_similarity_max": 0.90,
    # 중급이 고급의 어휘를 그대로 물려받으면 문장만 짧아지고 난이도는 그대로다.
    # 낮춰야 하는 것은 길이가 아니라 드문 어휘다(blueprint § 같은 과의 두 레벨).
    "level_vocab_overlap_max": 0.70,
}

COMMENT = re.compile(r"<!--.*?-->", re.S)
# 프롬프트의 낱말에는 조사가 붙어 있다("밥을"). 지문에는 "밥상"으로 나오므로
# 표면형만 비교하면 붙어 있는 낱말을 못 본다. 조사를 떼고 어간으로 견준다.
PARTICLE = "은는이가을를에의와과도만로으라고나랑서부터까지마다처럼보다"
TAGS = re.compile(r"<[^>]+>")


def text(html: str) -> str:
    return re.sub(r"\s+", " ", TAGS.sub("", html)).strip()


def blocks(src: str, cls: str) -> list[str]:
    """Every <div class="...cls..."> ... </div>, balanced."""
    out = []
    for m in re.finditer(r'<div class="[^"]*\b%s\b[^"]*"' % re.escape(cls), src):
        i, depth = m.start(), 0
        for t in re.finditer(r"<(/?)div\b", src[i:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                out.append(src[i:i + t.end() + 1])
                break
    return out


def page_map(src: str) -> dict[str, str]:
    marks = [(m.group(1), src.rfind("<div", 0, m.start()))
             for m in re.finditer(r'data-page-id="([^"]+)"', src)]
    out = {}
    for n, (pid, start) in enumerate(marks):
        end = marks[n + 1][1] if n + 1 < len(marks) else len(src)
        out[pid] = src[start:end]
    return out


def page2_sentences(block: str) -> list[str]:
    return [text(x) for x in
            re.findall(r'<span class="s-ko">(.*?)<span class="s-mark"', block, re.S)]


def audit(deck: Path, baseline: dict) -> tuple[list[str], list[str]]:
    deck = deck.resolve()
    src = COMMENT.sub("", deck.read_text(encoding="utf-8"))  # 주석 안의 예시 마크업을
    key = str(deck.relative_to(REPO)) if deck.is_relative_to(REPO) else deck.name
    exempt = set(baseline.get(key, []))   # 콘텐츠로 세지 않는다
    err, warn = [], []

    pages = page_map(src)
    ids = list(pages)

    # ---- page inventory ------------------------------------------------
    want = [p for p in PROFILE["pages"]]
    kind = "article" if "article" in pages else (
        "model-story" if "model-story" in pages else None)
    if kind is None:
        err.append("page 2 is neither article nor model-story")
    else:
        want = [kind if p == "article" else p for p in want]
    missing = [p for p in want if p not in ids]
    if missing:
        err.append("missing page(s): " + ", ".join(missing))
    extra = [p for p in ids if p not in want]
    if extra:
        err.append("unexpected page(s): " + ", ".join(extra))
    ordered = [p for p in ids if p in want]
    if ordered != [p for p in want if p in ids]:
        err.append("page order: " + " > ".join(ids))
    if kind == "model-story":
        if "page2-kind" in exempt:
            warn.append("page 2 is still model-story — pending conversion to a "
                        "prestudy article (page 2 is never read aloud)")
        else:
            err.append("page 2 is model-story; page 2 must be a prestudy article")

    first = re.search(r'data-page-id="([^"]+)"([^>]*)', src)
    if first and "data-act" not in first.group(2):
        err.append(f"first page {first.group(1)!r} carries no data-act")

    # ---- level ---------------------------------------------------------
    lvl = re.search(r'podo:level" content="([^"]*)', src)
    lvl = lvl.group(1) if lvl else ""
    if lvl not in PROFILE["levels"]:
        err.append(f"podo:level={lvl!r}")
    if "yomi" in src:
        err.append("kana reading present — banned in this track")

    # ---- lesson-goal ---------------------------------------------------
    if "lesson-goal" in pages:
        rows = re.findall(r'<div class="known-row">(.*?)</div>', pages["lesson-goal"], re.S)
        if len(rows) != PROFILE["goal_rows"]:
            err.append(f"lesson-goal has {len(rows)} known-row "
                       f"(want {PROFILE['goal_rows']})")
        for r in rows:
            if "?" in r or "？" in r:
                err.append(f"lesson-goal row is a question: {text(r)[:50]}")

    # ---- page 2 --------------------------------------------------------
    if kind:
        blk = pages[kind]
        sents = page2_sentences(blk)
        lo, hi = PROFILE["article_sents"]
        if not lo <= len(sents) <= hi:
            msg = f"page 2 has {len(sents)} sentences (want {lo}–{hi})"
            (warn if "page2-length" in exempt else err).append(
                msg + (" — pending backfill" if "page2-length" in exempt else ""))
        vlo, vhi = PROFILE["vocab_per_line"]
        for i, s in enumerate(blocks(blk, "sent"), 1):
            keys = len(re.findall(r'class="s-key"', s))
            ws = len(re.findall(r'class="s-w"', s))
            if keys != ws:
                err.append(f"s{i}: {ws} vocab entries but {keys} highlighted in the text")
            elif not vlo <= ws <= vhi:
                err.append(f"s{i}: {ws} vocab entries (want {vlo}–{vhi})")
            if 's-ja' not in s:
                err.append(f"s{i}: no Japanese translation")

    # ---- question pages ------------------------------------------------
    # blueprint § 겉도는 질문 규칙 3 — 「주제에서 벗어났다」의 유일하게 검사 가능한
    # 기준. 질문에 쓰인 명사·동사 하나 이상이 지문에 나와야 한다.
    art = "".join(page2_sentences(pages[kind])) if kind else ""
    flo, fhi = PROFILE["followups"]
    for qid in PROFILE["questions"]:
        if qid not in pages:
            continue
        pg = pages[qid]
        ask = re.search(r'class="section-subtitle ask">(.*?)</p>', pg, re.S)
        if not ask:
            err.append(f"{qid}: no .ask prompt")
            continue
        ko = re.search(r'<span class="ko">(.*?)</span>', ask.group(1), re.S)
        ja = re.search(r'<span class="ja">(.*?)</span>', ask.group(1), re.S)
        ko, ja = text(ko.group(1)) if ko else "", text(ja.group(1)) if ja else ""
        if not ko:
            err.append(f"{qid}: empty prompt")
        if not ja:
            err.append(f"{qid}: prompt has no Japanese translation")
        # 한 장에 하나. 명령형 프롬프트("…이야기해 주세요")도 프롬프트로 인정한다 —
        # 금지되는 것은 물음표가 아니라 한 장에 두 개를 묻는 것이다.
        n = ko.count("?") + ko.count("？")
        if n > 1:
            err.append(f"{qid}: {n} questions in one prompt — move the rest to the "
                       f"tutor note: {ko}")
        if ja and (ja.count("?") + ja.count("？")) != n:
            warn.append(f"{qid}: ko has {n} '?' but ja has "
                        f"{ja.count('?') + ja.count('？')}")
        def anchored(tok):
            stems = {tok[:n] for n in range(2, len(tok) + 1)}
            if len(tok) >= 2 and tok[1] in PARTICLE:
                stems.add(tok[:1])          # 한 음절 낱말 + 조사 (팀을, 밥을)
            return any(len(x) >= 2 and x in art or
                       (len(x) == 1 and x in art) for x in stems)
        if art and ko and not any(anchored(t) for t in re.findall(r"[가-힣]+", ko)):
            warn.append(f"{qid}: no word from this prompt appears in page 2 — "
                        f"off-topic? {ko}")
        notes = blocks(pg, "tutor-note")
        items = re.findall(r"<li>(.*?)</li>", notes[0], re.S) if notes else []
        if not flo <= len(items) <= fhi:
            err.append(f"{qid}: {len(items)} follow-up questions (want {flo}–{fhi})")
        # 코칭 문장은 예외적으로만. 안전·존중 사유는 '주의:' 로 시작한다.
        if notes:
            body = re.search(r'<div class="tn-body">(.*?)(?:<span class="tn-cap">|</div>)',
                             notes[0], re.S)
            line = text(body.group(1)) if body else ""
            if line and not line.startswith("주의:"):
                warn.append(f"{qid}: coaching line that is not a 주의: safety note "
                            f"— should this be here? {line[:60]}")
        if not re.search(r'<div class="fb" data-fb=', pg):
            err.append(f"{qid}: no .fb correction slot")
        if len(re.findall(r'class="fb-add"', pg)) != 2:
            err.append(f"{qid}: wants exactly two ＋ buttons (교정 · 노트)")

    return err, warn


def deck_paths(paths, every) -> list[Path]:
    """check_deck.py’s argument shape. A bare name that is no path on disk is a
    track under sandbox/drafts/kr/tracks — the form kr/AGENTS.md advertises."""
    roots = [KR] if every else [
        Path(p).resolve() if Path(p).exists() else TRACKS / p for p in paths] or [TRACK]
    out = []
    for r in roots:
        if r.is_dir():
            out += sorted(r.rglob("lesson.html"))
        elif r.exists():
            out.append(r)
        else:
            print(f"! no such path: {r}", file=sys.stderr)
    return out


def level_pairs(decks: list[Path]) -> list[tuple[str, Path, Path]]:
    seen = defaultdict(dict)
    for d in decks:
        course, lesson = d.parts[-4], d.parts[-2]
        for suf, lv in (("-advanced", "adv"), ("-intermediate", "int")):
            if course.endswith(suf):
                seen[(course[:-len(suf)], lesson)][lv] = d
    return [(f"{b} / {l}", v["adv"], v["int"])
            for (b, l), v in sorted(seen.items()) if len(v) == 2]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="deck files, directories, or track names")
    ap.add_argument("--all", action="store_true", help="every Korean deck in the repo")
    ap.add_argument("--warnings", action="store_true", help="print soft findings")
    ap.add_argument("--write-baseline", action="store_true",
                    help="record decks exempt from the pending-backfill rules")
    args = ap.parse_args()

    decks = deck_paths(args.paths, args.all)

    if args.write_baseline:
        out = {}
        # the baseline is the whole track's exemption list — writing it from a
        # subset would silently un-exempt every deck that was not named
        for d in sorted(TRACK.rglob("lesson.html")):
            src = COMMENT.sub("", d.read_text(encoding="utf-8"))
            pages = page_map(src)
            ex = []
            if "model-story" in pages:
                ex.append("page2-kind")
            k = "article" if "article" in pages else "model-story"
            if k in pages:
                n = len(page2_sentences(pages[k]))
                if not PROFILE["article_sents"][0] <= n <= PROFILE["article_sents"][1]:
                    ex.append("page2-length")
            if ex:
                out[str(d.relative_to(REPO))] = ex
        BASELINE.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"baseline: {len(out)} deck(s) exempt, pending backfill → {BASELINE.name}")
        return 0

    baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}

    errs = warns = 0
    for d in decks:
        e, w = audit(d, baseline)
        errs += len(e)
        warns += len(w)
        if e or (w and args.warnings):
            print(f"\n{d.relative_to(TRACK) if d.is_relative_to(TRACK) else d}")
            for x in e:
                print(f"  ✗ {x}")
            if args.warnings:
                for x in w:
                    print(f"  · {x}")

    # soft: a 중급 deck that never simplified its 고급 sibling
    stale, shared = [], []
    for name, adv, itm in level_pairs(decks):
        def vocab(p):
            t = COMMENT.sub("", p.read_text(encoding="utf-8"))
            pm = page_map(t)
            return set(re.findall(r'<span class="s-w"><b>(.*?)</b>',
                                  pm.get("article") or pm.get("model-story", "")))
        va, vi = vocab(adv), vocab(itm)
        if va and len(va & vi) / len(va) > PROFILE["level_vocab_overlap_max"]:
            shared.append((len(va & vi) / len(va), name))
        a = page2_sentences(page_map(COMMENT.sub("", adv.read_text(encoding="utf-8")))
                            .get("article") or
                            page_map(COMMENT.sub("", adv.read_text(encoding="utf-8")))
                            .get("model-story", ""))
        i = page2_sentences(page_map(COMMENT.sub("", itm.read_text(encoding="utf-8")))
                            .get("article") or
                            page_map(COMMENT.sub("", itm.read_text(encoding="utf-8")))
                            .get("model-story", ""))
        r = difflib.SequenceMatcher(None, " ".join(a), " ".join(i)).ratio()
        if r > PROFILE["level_similarity_max"]:
            stale.append((r, name))
    warns += len(shared)
    if shared and args.warnings:
        print("\n중급 reuses too much of 고급's vocabulary "
              f"(> {PROFILE['level_vocab_overlap_max']:.0%}) — shorter sentences, "
              "same rare words:")
        for r, name in sorted(shared, reverse=True):
            print(f"  · {r:.0%}  {name}")
    warns += len(stale)
    if stale and args.warnings:
        print("\n중급 page 2 barely differs from 고급 "
              f"(> {PROFILE['level_similarity_max']:.2f} similar):")
        for r, name in sorted(stale, reverse=True):
            print(f"  · {r:.2f}  {name}")

    print(f"\n{len(decks)} deck(s) · {errs} error(s) · {warns} warning(s)"
          + ("" if args.warnings else "   (--warnings to see the soft ones)"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
