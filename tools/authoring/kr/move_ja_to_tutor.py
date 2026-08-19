#!/usr/bin/env python3
"""Move Japanese out of the tutor's spoken line and into .tutor-note, with a reading.

A Korean tutor is not assumed to read Japanese, and 313 spoken lines across the
curriculum handed them kana to say out loud. Most are a vocabulary gloss stuck
onto the end of a page instruction:

    이번엔 혼자 읽어 보세요. 네 문장이에요. ‘전혀’는 '全然', ‘별로’는 'あまり'예요.

The instruction is the tutor's line. The gloss is reference — useful when the
learner stumbles, useless as speech, and unreadable to the person holding the
script. So the gloss sentence moves to .tutor-note and every Japanese run in it
gets its Hangul reading in parentheses.

Two glosses were also answer keys: reading "‘は’면 ‘는’, ‘も’면 ‘도’" aloud solves
every row of the choose activity underneath before the learner chooses. Moving
them is a pedagogy fix as much as a legibility one.

Only sentences that CONTAIN Japanese move. A page whose whole instruction is
Japanese-laden comes back unhandled rather than being emptied.

  python3 tools/authoring/kr/move_ja_to_tutor.py             # report
  python3 tools/authoring/kr/move_ja_to_tutor.py --apply
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ja_to_hangul import reading            # noqa: E402
from check_teaching import sentences        # noqa: E402

REPO = Path(__file__).resolve().parents[3]
PARA = re.compile(r'<p class="section-subtitle[^"]*"[^>]*>(.*?)</p>', re.S)
KO = re.compile(r'<span class="ko">(.*?)</span>', re.S)
JA = re.compile(r'<span class="ja">(.*?)</span>', re.S)
ANCHOR = re.compile(r'<span class="anchor">.*?</span>\s*</span>', re.S)
JA_SCRIPT = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")
RUN = re.compile(r"[぀-ヿ㐀-䶿一-鿿]+")


def ja_sentences(t):
    return [x.strip() for x in re.split(r"(?<=[。！？])", t) if x.strip()]


def annotate(s):
    """‘전혀’는 '全然'예요  →  ‘전혀’는 ‘全然(젠젠)’예요"""
    def one(m):
        h, un = reading(m.group())
        # っ and ー carry no syllable of their own — a reading of "" would print
        # as っ() and say nothing
        return m.group() if un or "?" in h or not h else f"{m.group()}({h})"
    s = RUN.sub(one, s)
    # the decks quote these with straight marks; AUTHORING wants ‘ ’
    return re.sub(r"'([^']{1,40})'", r"‘\1’", s)


def process(src):
    """-> (new src, moved, unhandled)"""
    moved, unhandled = [], []
    out, last = [], 0
    for m in PARA.finditer(src):
        inner = m.group(1)
        body = ANCHOR.sub("", inner)
        km, jm = KO.search(body), JA.search(body)
        if not km or not JA_SCRIPT.search(re.sub("<[^>]+>", "", km.group(1))):
            continue
        ko = re.sub(r"\s+", " ", re.sub("<[^>]+>", "", km.group(1))).strip()
        ja = re.sub(r"\s+", " ", re.sub("<[^>]+>", "", jm.group(1))).strip() if jm else ""
        ks, js = sentences(ko), ja_sentences(ja)
        if len(ks) != len(js):
            unhandled.append(("ko/ja 문장 수가 달라 짝을 못 맞춤", ko))
            continue
        keep = [(k, j) for k, j in zip(ks, js) if not JA_SCRIPT.search(k)]
        drop = [k for k in ks if JA_SCRIPT.search(k)]
        if not keep:
            unhandled.append(("일본어를 빼면 남는 문장이 없음", ko))
            continue
        new_ko, new_ja = " ".join(k for k, _ in keep), "".join(j for _, j in keep)
        note = annotate(" ".join(drop))
        rebuilt = (inner
                   .replace(km.group(1), new_ko)
                   .replace(jm.group(1), new_ja))
        out.append((m.start(), m.end(),
                    f'<p class="section-subtitle{re.match(r"<p class=.section-subtitle([^\"]*)", m.group(0)).group(1)}">'
                    f'{rebuilt}</p>\n      <div class="tutor-note">{note}</div>'))
        moved.append((ko, new_ko, note))
    for a, b, txt in reversed(out):
        src = src[:a] + txt + src[b:]
    return src, moved, unhandled


def main(argv):
    apply_ = "--apply" in argv
    paths = [a for a in argv if not a.startswith("--")] or [
        str(p) for p in sorted((REPO / "sandbox/drafts/kr/tracks").glob("**/lesson.html"))]
    nm = nu = 0
    for f in paths:
        p = Path(f)
        src = p.read_text(encoding="utf-8")
        new, moved, unhandled = process(src)
        if moved and apply_:
            p.write_text(new, encoding="utf-8")
        for ko, new_ko, note in moved:
            print(f"  {p.parent.name}\n    말: {new_ko}\n    튜터: {note}")
        for why, ko in unhandled:
            print(f"  {p.parent.name}  ✗ {why}\n    {ko[:120]}")
        nm += len(moved)
        nu += len(unhandled)
    print(f"\n{nm} gloss(es) moved · {nu} need a person")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
