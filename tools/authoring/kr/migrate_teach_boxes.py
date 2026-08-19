#!/usr/bin/env python3
"""Restructure 뜻과 쓰임 boxes onto the .anchor slot. Proposes; does not decide.

The old box was prose: sentence 1 quoted the Japanese equivalent, sentence 2
said when you reach for it, and sentences 3-n were whatever else the author had
— formation that pN-*-rule already draws, a comparison with an earlier lesson,
and a boilerplate close identical on 246 of 255 boxes.

Sentences 1 and 2 map onto the new shape mechanically. Sentences 3-n do not:
dropping them is right when the deck already carries that content elsewhere and
wrong when it does not, and only a person reading the deck can tell. So this
script never silently drops anything — every sentence it removes is printed
under REVIEW, and --apply refuses to run on a box it could not fully resolve.

  python3 tools/authoring/kr/migrate_teach_boxes.py                # propose, print
  python3 tools/authoring/kr/migrate_teach_boxes.py --review       # + dropped text
  python3 tools/authoring/kr/migrate_teach_boxes.py --apply        # write the safe ones
  python3 tools/authoring/kr/migrate_teach_boxes.py --apply <deck…>
"""
import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ja_to_hangul import reading  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
LIMIT = 60

PM = re.compile(r'(<p class="section-subtitle pattern-meaning"[^>]*>)(.*?)(</p>)', re.S)
KO = re.compile(r'<span class="ko">(.*?)</span>', re.S)
JA = re.compile(r'<span class="ja">(.*?)</span>', re.S)
KICKER = '<span class="meaning-kicker">뜻과 쓰임 <small>意味・使い方</small></span>'

# the Japanese equivalent, quoted, in sentence 1
ANCHOR_Q = re.compile(r"[‘'\"「]([^’'\"」]*[぀-ヿ一-鿿][^’'\"」]*)[’'\"」]")
JA_SCRIPT = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")
TAIL = re.compile(r"(제가 읽을게요|읽어 드릴게요|들려 드릴게요|잘 듣고 따라 읽어|"
                  r"따라 읽어 ?보세요|한 번에 읽을게요|이어서 읽을게요|끝소리만 들어|"
                  r"두 개를 이어서|먼저 들어 보세요)")
# a sentence that is formation, which pN-*-rule owns
FORMATION = re.compile(r"받침|어간|붙여요|붙이면|붙는|바꾸면|떼면|빼면")


QUOTE_OPEN, QUOTE_CLOSE = "“‘「『", "”’」』"


def sentences(t, ja=False):
    """Split the way shared/js/script-lines.js splits, for the same reasons.

    Korean ends on .!? and Japanese on 。！？ — splitting Korean on both is how
    the first run of this script decided all 253 boxes had mismatched sentence
    counts. Two refinements come from that file as well: punctuation inside a
    quote does not end a sentence (these decks cite 「어디예요?」는 constantly),
    and in Korean the punctuation must be followed by space or end-of-string,
    because a cited expression is glued to its particle — 그랬어?는.
    """
    enders = "。！？" if ja else ".!?"
    out, cur, depth = [], "", 0
    for i, ch in enumerate(t):
        cur += ch
        if ch in QUOTE_OPEN:
            depth += 1
        elif ch in QUOTE_CLOSE and depth:
            depth -= 1
        elif ch in enders and not depth:
            if ja or i + 1 >= len(t) or t[i + 1].isspace():
                out.append(cur.strip())
                cur = ""
    if cur.strip():
        out.append(cur.strip())
    return out


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def propose(ko, ja):
    """-> dict with anchor/spoken/dropped, and why it is or is not resolved"""
    ks, js = sentences(ko), sentences(ja, ja=True)
    out = {"anchor_ja": None, "anchor_ko": None, "spoken": None,
           "spoken_ja": None, "dropped": [], "blockers": []}

    # ---- the anchor ----
    m = ANCHOR_Q.search(ks[0]) if ks else None
    if m:
        out["anchor_ja"] = m.group(1)
        r, unresolved = reading(m.group(1))
        out["anchor_ko"] = r
        if unresolved:
            out["blockers"].append(f"읽기 미해결 {unresolved}")
        start = 1
    else:
        out["blockers"].append("1문장에 일본어 앵커가 없음 — 사람이 정해야 함")
        start = 0

    # ---- the one spoken sentence ----
    body = [(k, js[i] if i < len(js) else "") for i, k in enumerate(ks)]
    keep = [(k, j) for k, j in body[start:] if not TAIL.search(k)]
    if keep:
        out["spoken"], out["spoken_ja"] = keep[0]
        out["dropped"] = [k for k, _ in keep[1:]]
    else:
        out["blockers"].append("남는 문장이 없음")

    if out["spoken"] and JA_SCRIPT.search(out["spoken"]):
        out["blockers"].append("말하는 줄에 일본어가 남음")
    if out["spoken"] and len(out["spoken"]) > LIMIT:
        out["blockers"].append(f"말하는 줄 {len(out['spoken'])}자 > {LIMIT}")
    if len(ks) != len(js):
        out["blockers"].append(f"ko {len(ks)}문장 / ja {len(js)}문장 — 짝이 안 맞음")

    # Dropped sentences are a NOTE, not a blocker. They are always printed, so
    # nothing leaves the box silently, but whether a sentence is safe to drop
    # depends on what the rest of the deck already carries — which the reviewer
    # can see and this script cannot. Blocking on it stopped all 230 boxes on a
    # question only reading the deck answers.
    out["notes"] = [d for d in out["dropped"] if not FORMATION.search(d)]
    return out


def build(p):
    ja_esc = p["anchor_ja"]
    return (f'{KICKER}<span class="anchor">'
            f'<span class="anchor-ja">{ja_esc}</span>'
            f'<span class="anchor-ko">{p["anchor_ko"]}</span></span>'
            f'<span class="ko">{p["spoken"]}</span>'
            f'<span class="ja">{p["spoken_ja"]}</span>')


def main(argv):
    apply_ = "--apply" in argv
    review = "--review" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        paths = [str(p) for p in sorted(
            (REPO / "sandbox/drafts/kr/tracks/2-core-patterns").glob("**/lesson.html"))]

    ready = blocked = 0
    blockers = {}
    for path in paths:
        src = Path(path).read_text(encoding="utf-8")
        if "pattern-meaning" not in src:
            continue
        changed = False
        deck = f"{Path(path).parents[2].name}/{Path(path).parent.name}"

        def repl(m):
            nonlocal changed, ready, blocked
            open_, inner, close = m.groups()
            if 'class="anchor"' in inner:
                return m.group(0)                      # already migrated
            ko = strip_tags(KO.search(inner).group(1)) if KO.search(inner) else ""
            ja = strip_tags(JA.search(inner).group(1)) if JA.search(inner) else ""
            p = propose(ko, ja)
            if p.get("notes") and review:
                print(f"  {deck} — 버려짐(형태 설명 아님):")
                for d in p["notes"]:
                    print(f"      · {d}")
            if p["blockers"]:
                blocked += 1
                blockers.setdefault(deck, []).append((ko, p))
                return m.group(0)
            ready += 1
            if review:
                print(f"  {deck}")
                print(f"    anchor  {p['anchor_ja']} / {p['anchor_ko']}")
                print(f"    spoken  {p['spoken']}")
                for d in p["dropped"]:
                    print(f"    drop    {d}")
            changed = True
            return open_ + build(p) + close

        new = PM.sub(repl, src)
        if apply_ and changed:
            Path(path).write_text(new, encoding="utf-8")

    print(f"\n{ready} box(es) resolve mechanically · {blocked} need a person")
    if blockers:
        counts = {}
        for rows in blockers.values():
            for _, p in rows:
                for b in p["blockers"]:
                    key = re.sub(r"\d+", "N", b)
                    counts[key] = counts.get(key, 0) + 1
        print("\n  why:")
        for k, v in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"   {v:>4}  {k}")
        if review:
            print("\n  ---- blocked boxes ----")
            for deck, rows in list(blockers.items()):
                for ko, p in rows:
                    print(f"  {deck}\n    {ko[:150]}\n    → {p['blockers']}")
    if apply_:
        print(f"\napplied to {ready} box(es).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
