#!/usr/bin/env python3
"""튜터 대본 말투 검사 — 한국어 덱 전용.

AUTHORING.md 의 「모든 트랙의 튜터 말투」를 검사 가능한 형태로 강제한다. 기준 자체는
tone-standard.json 에 있고, 이 파일은 그 표를 덱에 대어 볼 뿐이다.

    python3 tools/authoring/kr/check_tone.py                 # sandbox/drafts/kr 전체
    python3 tools/authoring/kr/check_tone.py <경로> ...       # 파일이나 디렉토리
    python3 tools/authoring/kr/check_tone.py --fix           # 튜터 시범 줄만 고친다
    python3 tools/authoring/kr/check_tone.py --mixed         # 아직 안 정해진 동사까지 센다

두 가지를 본다.

1. **튜터 시범 줄** (`제가 … 읽어 볼게요` → `제가 … 읽을게요`). 한국어 두 형태 모두
   일본어가 「私が読みます」로 같아서 한국어만 고치면 된다. `--fix` 가 고치는 건 이것뿐이다.

2. **학습자 지시** (`눌러 보세요` / `채워 볼까요?`). 조용한 화면 동작은 명령형,
   소리 내어 하는 활동은 권유형이다. **자동으로 고치지 않는다** — 같은 뜻의 일본어 짝이
   코퍼스 안에서 일관되지 않아서(「채워 볼까요?」 226줄의 일본어가 「てみましょう」다),
   기계적으로 바꾸면 한쪽만 맞고 다른 쪽이 틀어진다. 사람이 두 언어를 같이 보고 고쳐야 한다.

`--fix` 는 초안(`sandbox/`)만 고친다. `courses/` 는 promote.py 가 소유하므로 손대지 않는다.
"""

import argparse
import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STANDARD = pathlib.Path(__file__).with_name("tone-standard.json")
DEFAULT = ROOT / "sandbox/drafts/kr"

COMMENT = re.compile(r"<!--.*?-->", re.S)
# 덱의 한국어가 실제로 사는 자리. 태그를 건너뛰지 않으므로 한 요소 안의 텍스트만 본다.
KO_SPAN = re.compile(r'<span class="ko">([^<]+)</span>')
TUTOR_NOTE = re.compile(r'<div class="tutor-note">([^<]+)</div>')
SUBTITLE = re.compile(r'<p class="section-subtitle[^"]*">(.*?)</p>', re.S)


def load():
    return json.loads(io.open(STANDARD, encoding="utf-8").read())


def korean_runs(html):
    """덱에서 튜터가 말하는 한국어 텍스트만 뽑는다. (텍스트, 종류) 목록."""
    html = COMMENT.sub("", html)
    out = []
    for m in KO_SPAN.finditer(html):
        out.append((m.group(1), "ko"))
    for m in TUTOR_NOTE.finditer(html):
        out.append((m.group(1), "note"))
    for m in SUBTITLE.finditer(html):
        # 자막 안의 <span class="ko"> 는 위에서 이미 셌다. 태그가 없는 것만 줍는다.
        inner = m.group(1)
        if "<span" not in inner and re.search(r"[가-힣]", inner):
            out.append((re.sub(r"\s+", " ", inner).strip(), "subtitle"))
    return out


def tutor_hits(text, rewrite):
    """제가 … <soft> 형태를 찾는다. 반환: (찾은 형태, 바꿀 형태)."""
    for soft, plain in rewrite.items():
        # 제가 ~ 사이에 다른 문장 끝이 끼면 같은 문장이 아니다.
        if re.search(r"제가[^.!?]{0,24}" + re.escape(soft), text):
            yield soft, plain


def learner_hits(text, settled, exclude):
    """굳어진 동사가 반대 형태로 쓰인 자리를 찾는다."""
    for verb, want in settled.items():
        if verb in exclude:
            continue
        other = "보세요" if want == "볼까요?" else "볼까요?"
        pat = re.escape(verb) + r" " + re.escape(other).replace(r"\?", r"\?")
        if re.search(pat, text):
            yield verb, other, want


def scan(paths, std, want_mixed=False):
    tutor, learner, mixed = [], [], []
    rewrite = std["tutorDemo"]["rewrite"]
    settled = std["learner"]["settled"]
    exclude = set(std["learner"]["exclude"])
    mixed_verbs = std["learner"]["mixed"]
    for p in paths:
        html = io.open(p, encoding="utf-8").read()
        for text, kind in korean_runs(html):
            for soft, plain in tutor_hits(text, rewrite):
                tutor.append((p, text, soft, plain))
            for verb, got, want in learner_hits(text, settled, exclude):
                learner.append((p, text, verb, got, want))
            if want_mixed:
                for v in mixed_verbs:
                    for form in ("보세요", "볼까요?"):
                        if f"{v} {form}" in text:
                            mixed.append((p, v, form))
    return tutor, learner, mixed


def fix(paths, std):
    """튜터 시범 줄만 고친다. 학습자 쪽은 손대지 않는다 — 모듈 docstring 참고."""
    rewrite = std["tutorDemo"]["rewrite"]
    changed = 0
    touched = []
    for p in paths:
        if "sandbox/" not in str(p):
            continue  # courses/ 는 promote.py 가 소유한다
        src = io.open(p, encoding="utf-8").read()
        out = src
        for soft, plain in rewrite.items():
            out = re.sub(
                r"(제가[^.!?<]{0,24}?)" + re.escape(soft),
                lambda m: m.group(1) + plain,
                out,
            )
        if out != src:
            n = sum(
                1
                for _ in re.finditer(
                    r"제가[^.!?<]{0,24}?" + re.escape(list(rewrite)[0]), src
                )
            )
            io.open(p, "w", encoding="utf-8").write(out)
            changed += n
            touched.append(p)
    return changed, touched


def rel(p):
    try:
        return str(pathlib.Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", type=pathlib.Path)
    ap.add_argument("--fix", action="store_true", help="튜터 시범 줄을 고친다 (sandbox 만)")
    ap.add_argument("--mixed", action="store_true", help="아직 안 정해진 동사도 센다")
    a = ap.parse_args()

    roots = a.paths or [DEFAULT]
    files = []
    for r in roots:
        files += sorted(r.rglob("*.html")) if r.is_dir() else [r]
    if not files:
        sys.exit("검사할 html 이 없다: %s" % ", ".join(str(r) for r in roots))

    std = load()

    if a.fix:
        n, touched = fix(files, std)
        print("튜터 시범 줄 %d 곳을 %d 개 파일에서 고쳤다." % (n, len(touched)))
        print("학습자 지시는 고치지 않았다 — 일본어 짝을 같이 봐야 한다. --fix 없이 다시 돌려 목록을 봐라.")
        return 0

    tutor, learner, mixed = scan(files, std, a.mixed)

    if tutor:
        print("\n튜터 시범 줄 — 평서형이어야 한다 (--fix 로 고칠 수 있다)")
        seen = {}
        for p, text, soft, plain in tutor:
            seen.setdefault((soft, plain), []).append(p)
        for (soft, plain), ps in seen.items():
            print("  %s → %s   %d 곳 / %d 파일" % (soft, plain, len(ps), len(set(ps))))
            for p in sorted(set(ps))[:3]:
                print("      %s" % rel(p))
            if len(set(ps)) > 3:
                print("      … 외 %d 개 파일" % (len(set(ps)) - 3))

    if learner:
        print("\n학습자 지시 — 굳어진 형태와 어긋난다 (손으로 고쳐라: 일본어도 같이)")
        for p, text, verb, got, want in learner:
            print("  %s: %s %s → %s %s" % (rel(p), verb, got, verb, want))
            print("      %s" % text[:78])

    if a.mixed and mixed:
        agg = {}
        for _, v, form in mixed:
            agg.setdefault(v, {}).setdefault(form, 0)
            agg[v][form] += 1
        print("\n아직 안 정해진 동사 — settled 로 옮기려면 사람이 정해야 한다")
        for v, forms in sorted(agg.items(), key=lambda x: -sum(x[1].values())):
            print(
                "  %-6s %s"
                % (v, "  ".join("%s×%d" % (f, n) for f, n in sorted(forms.items())))
            )

    print(
        "\n%d 파일 · 튜터 %d · 학습자 %d"
        % (len(files), len(tutor), len(learner))
    )
    return 1 if (tutor or learner) else 0


if __name__ == "__main__":
    sys.exit(main())
