#!/usr/bin/env python3
"""
수업 덱에서 페이지를 덜어내 예습 덱을 만든다.

    python3 tools/authoring/kr/make_prestudy.py <lesson-dir> [--keep id,id,...] [--check]

예습은 **수업 덱의 짧은 판**이다. 새로 그리지 않는다 — 같은 스타일시트, 같은
컴포넌트, 같은 페이저, 같은 마크업. 여기서 하는 일은 페이지를 빼는 것뿐이다.
그래서 세 가지가 공짜로 따라온다:

  · 부분집합 규칙이 **구조적으로** 참이다. 예습의 한국어는 수업 덱의 한국어와
    같은 글자다 — 지어낼 방법이 없다.
  · 디자인이 어긋날 수가 없다. 두 덱이 한 파일에서 나온다.
  · 수업 덱을 고치면 예습을 다시 뽑기만 하면 된다.

## 어디서 자르는가

`shared/ux-philosophy.md` 의 문장 학습 순서가 자를 자리를 이미 정해 놓았다:

    읽기 → 고르기 → 배열 → 빈칸 → 번역 → 쓰기
    └─── 혼자 되는 쪽 ────┘ └─ 상대가 있어야 하는 쪽 ─┘

**예습은 왼쪽 절반을, 수업은 오른쪽 절반을 가져간다.** 이것이 「설명은 예습이,
드릴은 수업이」를 페이지 단위로 옮긴 것이다. 우리 튜터는 일본어로 문법을 설명하지
못하지만 드릴은 잘한다 — 그러니 만들어 내는 쪽을 수업에 남긴다.

기본 규칙이 남기는 것: 목표·아는 단어·파트 도입·teach·rule·choose·reorder·model.
덜어내는 것: fill·translate·write, 3부의 만들어 내는 쪽(complete·freetalk),
**원어민 팁**, 그리고 **같이 읽어요(`-read`)**.

배열(`-reorder`)은 남긴다. 만들어 내는 쪽에 걸쳐 있지만 **혼자서 끝나는**
활동이다 — 조각을 눌러 맞추면 페이지가 스스로 맞았는지 알려 주므로 상대가
필요 없고, 빈칸·번역·쓰기와 달리 학습자가 한국어를 지어내지 않아도 된다.

「같이 읽어요」는 튜터와 소리 내어 주고받는 장이라 수업의 몫이다. 혼자서는
같은 문장을 한 번 더 보는 것에 그치고, 그 문장은 바로 앞 teach 장에 이미 있다.

원어민 팁은 튜터가 수업에서 덤으로 얹어 주는 것이다. 혼자 읽으면 그냥 정보가
하나 더 느는 것이고, 예습의 예산은 그런 데 쓰지 않는다.

3부의 **모델 대화(`-model`)는 남긴다.** 읽고 듣는 페이지라 받아들이는 쪽이고,
패턴이 실제 대화 안에서 어떻게 사는지를 수업 전에 한 번 보여 준다 — 그 자리에서
처음 만나면 튜터가 설명해 줘야 하는데, 그것이 우리 튜터가 못하는 일이다.

트랙마다 페이지 이름이 다르므로, 규칙이 안 맞으면 `--keep` 으로 직접 준다.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys

# 받아들이는 쪽 — 예습이 가져가는 페이지. 접미사로 맞춘다.
# `scene` 과 `expressions` 는 상황별 트랙의 알맹이다 — 오늘의 장면을 읽는 장과
# 그 장면의 표현 세 개. 둘 다 «읽는» 장이라 예습의 몫인데, 접미사 규칙에 안
# 걸려 170개 덱에서 통째로 빠져 있었다. 그 결과 뒤쪽 장이 「さっきの告白の瞬間です」
# 하고 없는 장을 가리켰다. `batchim` 도 같은 이유로 샜다(1과에서 받침을 처음
# 가르치는 장인데 빠지고는, 그 뒤 장이 「さっきのパッチムのルール」이라고 했다).
RECEPTIVE = ("-teach", "-rule", "-choose", "-reorder", "-intro", "-model",
             "scene", "expressions", "batchim")
# 이름 그대로 남기는 것들.
KEEP_EXACT = {"lesson-goal", "words-you-know"}
# 만들어 내는 쪽 — 수업에 남기는 페이지.
PRODUCTIVE = ("-fill", "-translate", "-write", "-complete", "-freetalk")
# 붙박이 키커의 일본어. 쌍둥이가 마크업에 없어서 표로 옮긴다.
KICKER_JA = {"목표": "ゴール", "정리": "まとめ", "복습": "ふくしゅう",
             "파트 1": "パート 1", "파트 2": "パート 2", "파트 3": "パート 3",
             "실전": "じっせん", "마지막 장면": "さいごの場面",
             "시즌 피날레": "シーズンフィナーレ",
             "질문 8개": "質問 8つ", "질문 6개": "質問 6つ"}

# 튜터가 옆에 있어야 말이 되는 «문장». 안내문에서 이것만 도려내고 나머지는 둔다.
#
# 덱마다 손으로 고칠 일이 아니라는 것이 484개 덱을 세어 보고 알게 된 사실이다:
# 걸리는 312건 중 230건이 아래 첫 두 줄, 곧 **같은 상용구**였다. 장면을 설명하는
# 첫 문장은 혼자 읽어도 맞는 말이므로 남기고, 튜터의 역할 분담만 지운다.
# 지우면 안 되고 **바꿔** 써야 하는 문장. 지우면 그 장의 안내문이 통째로 비거나
# (42과 p1-teach 가 그랬다) 학습자가 무엇을 해야 하는지 사라진다.
# 역할극 지시는 상황별 트랙 전체에 깔린 상용구다 — 106건 중 85건이 아래 셋이다.
TUTOR_REWRITE = {
    "これまでに習った表現で、最初の場面をもう一度演じてみましょうか。":
        "これまでに習った表現で、最初の場面をもう一度読んでみましょう。",
    "今度は意味がわかった状態で、もう一度演じてみましょうか？":
        "今度は意味がわかった状態で、もう一度読んでみましょう。",
    "今度は意味を理解して、もう一度演じます。":
        "今度は意味を理解して、もう一度読んでみましょう。",
    "役を分けて読みましょう。": "二人のせりふを続けて読んでみましょう。",
    "役を分けて会話を読みましょう。": "二人のせりふを続けて読んでみましょう。",
    "今日はこれを聞き取って、私にもこう言ってみましょう。":
        "今日はこの言い方を覚えて、自分でも言ってみましょう。",
    "この言葉、私がレッスンでずっと使っていました。":
        "この言葉は、レッスンでよく使います。",
    # 프리토킹의 읽을거리 — 210개 덱이 전부 같은 줄이다. 원래 문장은 수업 중에
    # 튜터가 묻는 말이라(과거형 + 一緒に), 혼자 읽으면 세 가지가 한꺼번에 어긋난다.
    # 게다가 **누르면 무엇이 나오는지를 말하지 않는다** — 이 장이 예습의 본체인데
    # 학습자가 안 누르고 끝낼 수 있다.
    "授業前に読んでいて気になったことはありましたか？ あればその文を押してください。一緒に見てみましょう。":
        "文を押すと、日本語の訳と単語の意味が出ます。わからない文は押して確かめましょう。",
}

TUTOR_SENTENCES = (
    "私が先にハナ役を読みます。",
    "よく聞いて、ハルカになって一緒に読んでみましょうか。",
    "私が読みます。",
    "今度は意味を理解して、私がソヒをやるので、もう一度演じてみましょうか？",
    "私が母をやります。",
    "1つずつ一緒に読んでみましょうか？",
)
# 남은 문장에서 이 표현이 보이면 새 상용구가 생긴 것이다 — 조용히 내보내지 않는다.
# 一緒に 는 넣지 않는다: 「一緒にする人なら하고です」처럼 문법 설명에도 쓰여서
# 경고가 소음이 된다.
# 경고 전용(지우지 않는다). 지우는 쪽(VOICE_SENT)보다 넓게 잡아, 새 상용구가
# 생겼을 때 조용히 나가지 않게 한다. 역할 지시(役で·演じ)는 「私」가 없어서
# 지우는 규칙에는 안 걸리지만 혼자서는 못 하는 말이라 여기서 드러낸다.
TUTOR_MARK = re.compile(r"私[がはのにと]|わたし|先生が|役[でをと]|演じ")


def keep_attr_order():
    """속성 순서를 원본 그대로 두는 직렬화기.

    bs4 는 기본적으로 속성을 알파벳순으로 내보낸다. 그러면
    `<link rel="stylesheet" href="…">` 이 `<link href="…" rel="stylesheet">` 이
    되는데, **GCS 로 올릴 때 덱을 합치는 머저는 rel 이 href 앞에 오는 형태만
    읽는다**(`validate.py` 의 패키징 검사가 이걸 잡는다). 순서가 뒤집힌 덱은
    빌드가 초록불인 채로 스타일 없이 배포된다.

    우리가 바꾸는 것은 페이지 목록뿐이고 속성은 손댈 이유가 없으므로, 파서를
    통과시키되 원본 순서를 그대로 돌려준다.
    """
    from bs4.formatter import HTMLFormatter

    class _KeepOrder(HTMLFormatter):
        def attributes(self, tag):
            return [(k, v) for k, v in tag.attrs.items()]

    return _KeepOrder()


def soup_of(path: pathlib.Path):
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        sys.exit("beautifulsoup4 가 필요하다:  pip3 install beautifulsoup4")
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


# ── 프리토킹 ────────────────────────────────────────────────────────
# 210개 덱이 전부 같은 13장이다: goal · article · lesson-style · talk-intro ·
# warm-1..2 · q1..6 · feedback.
#
# 이 트랙은 예습이 이미 전제되어 있다 — article 장의 안내문이 학습자에게
# 「授業前に読んでいて気になったことはありましたか」라고 묻는다. 수업 전에
# 읽고 온다는 것이 원래 설계다.
FREETALK_DROP = {
    "lesson-style",  # 「많이 말하기 / 교정받기」 — 수업 첫머리에 튜터와 정하는 것
    "feedback",      # 튜터가 수업 끝에 써 주는 칸
}


def freetalk_keep(pages) -> list[str]:
    """프리토킹: 읽을 거리와 질문을 미리 준다.

    질문(warm-1..2, q1..6)을 다 보여 주는 것이 요점이다. 프리토킹 수업에서
    학습자가 굳는 이유는 한국어가 모자라서가 아니라 **예고 없이** 질문을 받고
    그 자리에서 제2언어로 답을 지어야 해서다. 미리 보면 그 문제가 사라진다.
    """
    return [p["data-page-id"] for p in pages
            if p["data-page-id"] not in FREETALK_DROP]


# ── 한글 ────────────────────────────────────────────────────────────
# 글자마다 페이지 이름이 달라(consonant-h, pair-k-t, ...) 접미사 규칙이 안 통한다.
# 활동의 종류로 가른다.
# 소리가 있어야 성립하는 장을 가려내는 표지. **페이지 이름이 아니라 지시문을 본다.**
# 이름은 거짓말을 한다: `find-the-word` 는 「찾기」처럼 생겼지만 실제 지시문은
# 「私が単語を2つ言います。1つずつさがしてタップしてください」— 순수한 듣기 문제다.
# 이름으로 걸렀으면 그 장이 그대로 예습에 실려, 소리 없이는 풀 수 없는 페이지가
# 학습자 앞에 놓였을 것이다.
# 소리를 «듣고 답하는» 문제. 이 둘이 한 지시문에 같이 있으면 그 장은 소리 없이
# 풀 수가 없다 — 문제 자체가 소리이기 때문이다.
LISTEN_CUE = re.compile(r"聞いて|聞き分|声を聞|言います")
ANSWER_CUE = re.compile(r"タップ|さがし|探し|選ん|選び|作って|押して")

# 튜터의 목소리를 가리키는 문장. 장을 버릴 이유는 아니고, **그 문장만** 지운다.
# 「私が」만 보면 새는 것들이 있다: 「私のあとについて」「私と一緒に読んで」는
# 똑같이 옆에 사람이 있어야 하는 말인데 조사가 달라 안 걸렸다. 한글 덱 두 곳에서
# 그대로 살아남았다.
VOICE_SENT = re.compile(r"私[がのと]|まねして|真似して|一緒に読|あとについて")


def needs_audio(page) -> bool:
    """이 장의 **문제 자체가 소리인가.**

    이름으로는 알 수 없다 — `find-the-word` 는 「찾기」처럼 생겼지만 지시문은
    「私が単語を2つ言います。1つずつさがしてタップしてください」로, 순수한 듣기다.
    반대로 `combo-table` 은 「私が1行ずつ読みます」가 붙어 있어도 서른 자 표가
    본체라 눈으로 다 된다. **버릴 것은 「듣고 답하라」는 장뿐이고**, 나머지는
    그 문장만 지우면 된다.
    """
    for box in page.select(".section-subtitle"):
        text = box.get_text(" ", strip=True)
        for drop in TUTOR_SENTENCES:
            text = text.replace(drop, "")
        if LISTEN_CUE.search(text) and ANSWER_CUE.search(text):
            return True
        # 답할 거리가 아예 없는데 「よく聞いてみましょう」만 있는 장도 있다.
        # 들을 것이 없으니 학습자는 아무것도 못 한다 — 답하라는 말이 없다고
        # 통과시키면 그 장이 그대로 실린다(01/words-you-know 가 그랬다).
        if LISTEN_CUE.search(text) and not page.select(".opt, .tile, input, .kp-key"):
            return True
    return False


def hangul_keep(pages) -> list[str]:
    """한글: 소리 없이 혼자 되는 장만 남긴다.

    이 트랙은 소리가 본체라, 음성이 붙기 전까지 예습이 반쪽이다. 글자의 짜임을
    보는 장과 눌러서 스스로 채점되는 활동은 지금도 되지만, 듣고 고르는 장은
    안 된다 — 남겨 두면 학습자 앞에 **풀 수 없는 페이지**가 놓인다.
    """
    keep = [p["data-page-id"] for p in pages
            if not needs_audio(p)
            # 소리 내어 읽는 장(`*-reading`)도 뺀다. 혼자 읽을 수는 있어도
            # 맞게 읽었는지 알 방법이 없다 — 듣고 고쳐 주는 것이 튜터가 제일
            # 잘하는 일이고, 이 트랙에서는 그게 수업의 알맹이다. 여섯 장이라
            # 남기면 예산도 넘는다.
            and not re.search(r"read", p["data-page-id"])]
    return prune_orphan_intros(keep, [p["data-page-id"] for p in pages])


def prune_orphan_intros(keep: list[str], ids: list[str]) -> list[str]:
    """뒤에 아무것도 안 남은 파트 표지를 버린다.

    `words-intro` 다음의 단어 장이 전부 빠지면, 아무 데도 데려가지 않는 표지만
    남는다. 파트 도입은 다음 도입 전까지 내용 장이 하나라도 있어야 뜻이 있다.
    """
    order = {pid: i for i, pid in enumerate(ids)}
    intros = [k for k in keep if k.endswith("-intro")]
    drop = set()
    for intro in intros:
        after = [k for k in keep if order[k] > order[intro] and not k.endswith("-intro")]
        nxt = [k for k in intros if order[k] > order[intro]]
        limit = order[nxt[0]] if nxt else len(ids)
        if not [k for k in after if order[k] < limit]:
            drop.add(intro)
    return [k for k in keep if k not in drop]


def collapse_questions(soup) -> int:
    """프리토킹의 질문 장 여덟 개를 한 장으로 모은다.

    수업에서는 한 장에 한 질문이 맞다 — 튜터가 묻고, 학습자가 답하고, 그 답을
    그 자리에 받아 적는다. 예습에는 받아 적을 사람이 없어서 그 칸이 빠지고,
    남는 것은 «질문 하나만 놓인 빈 화면» 여덟 장이다.

    한 장에 모으면 학습자가 오늘 대화의 흐름을 한눈에 본다. 프리토킹에서
    학습자가 굳는 이유는 한국어가 모자라서가 아니라 예고 없이 질문을 받아서라,
    미리 통째로 보는 것이 그대로 대비가 된다.

    이것만은 «덜어내기»가 아니라 새 마크업이다. 그래서 새 컴포넌트를 만들지
    않고, 목표 장이 쓰는 `.known` 카드를 그대로 빌려 쓴다.
    """
    qs = [p for p in soup.select("[data-page-id]")
          if re.fullmatch(r"warm-\d+|q\d+", p["data-page-id"])]
    if len(qs) < 3:
        return 0

    page = soup.new_tag("div", attrs={"class": "section", "data-page-id": "questions"})
    h = soup.new_tag("h2", attrs={"class": "section-title"})
    h.append("授業で聞かれること")
    page.append(h)
    cap = soup.new_tag("p", attrs={"class": "section-subtitle"})
    ja = soup.new_tag("span", attrs={"class": "ja"})
    ja.append("この順番で聞かれます。答えを考えておくと、授業で止まりません。")
    cap.append(ja)
    page.append(cap)

    box = soup.new_tag("div", attrs={"class": "known lines"})
    for q in qs:
        ask = q.select_one(".section-subtitle.ask") or q.select_one(".section-subtitle")
        ko = ask.select_one(".ko") if ask else None
        jp = ask.select_one(".ja") if ask else None
        if ko is None:
            continue
        row = soup.new_tag("div", attrs={"class": "known-row"})
        k = soup.new_tag("span", attrs={"class": "k"})
        k.append(re.sub(r"\s+", " ", ko.get_text(" ", strip=True)))
        row.append(k)
        if jp is not None:
            j = soup.new_tag("span", attrs={"class": "j"})
            j.append(re.sub(r"\s+", " ", jp.get_text(" ", strip=True)))
            row.append(j)
        box.append(row)
    page.append(box)

    qs[0].insert_before(page)
    for q in qs:
        q.decompose()
    return len(qs)


# 체험 덱은 수업이 아니라 «판매»다 — 표지·인사·니즈 파악 장이 앞에 붙어 있고,
# 애초에 예습이 없는 물건이다. 페이지 이름으로 알아보고 거절한다.
TRIAL_MARK = {"cover", "greeting", "needs-intro", "trial-intro"}

# 튜터 전용 런타임. 두 번째 화면이 없으면 둘 다 할 일이 없다.
TUTOR_SCRIPTS = ("spotlight.js", "tutor-notes.js")

# 예습 덱이 자기 옆에 갖고 가는 스타일. **파일 이름은 반드시 `deck.css` 다.**
#  · grape 는 zip 안의 첫 .css 를 슬롯 이름으로 갈아 끼운다(build.py). 그래서
#    `prestudy.css` 라는 이름은 `repoint-shared.py` 의 FORBIDDEN 에 올라 있다 —
#    그 글자가 URL 한가운데서 치환되어 링크가 깨진다.
#  · `repoint-shared.py` 는 **로컬 스타일시트가 하나도 안 남았을 때만** 빈
#    deck.css 를 써 넣는다. 내용을 채운 deck.css 가 이미 있으면 그대로 둔다.
PRESTUDY_CSS = '''/* 티칭 모드 스위치(페이저의 T)를 감춘다. 예습에는 튜터가 없고, 다른 트랙에서
   이 스위치는 정답을 비춰 주는 물건이다 — 학습자 화면에 있을 이유가 없다.
   페이저는 런타임이 그리므로 마크업에서 지울 수가 없어 CSS 로 덮는다.
   `pager.js` 는 이 규칙을 «이 덱에는 티칭 모드가 없다»는 선언으로 읽어, 스위치를
   담던 날개(.pg-wing)까지 함께 접는다 — 여기서 버튼만 감추면 빈 날개가 페이저
   위로 손잡이처럼 솟아 있었다. */
.pg-teach { display: none !important; }
'''
PRESTUDY_CSS += '/* 예습 덱 전용 스타일. `make_prestudy.py` 가 덱 옆에 복사하고 링크를 건다.\n   파일럿 동안만 여기 있고, 확정되면 shared/css 로 옮겨 CDN 태그에 실린다\n   (AGENTS.md: 덱은 per-deck CSS 를 갖지 않는다).\n\n   지금 하는 일은 하나뿐이다. 예습은 수업 덱과 **같아 보여야** 하므로,\n   그 밖에는 아무것도 건드리지 않는다.\n\n   소리 관련 규칙(.has-say / .say)은 여기 있었다가 걷어냈다 — 음성은 나중에\n   따로 붙인다. 자리를 심는 도구는 `mark_prestudy_audio.py` 에 그대로 있고,\n   그때 이 파일에 규칙도 같이 돌아온다. */\n\n/* 튜터의 대사(.ko)를 걷어내면 파란 상자에 일본어만 남는다. 그런데 그 일본어는\n   원래 «보조» 로 조판돼 있어(작고 흐림), 유일한 줄이 되고도 부제처럼 읽힌다.\n   그 자리에 올려 준다 — 값은 시스템이 이미 쓰는 일본어 우선 조판과 같다.\n   `.needs-jp` 클래스 자체는 쓰지 않는다: 그건 체험 덱의 세일즈 장용이라\n   라임 배경이 딸려 오고, 라임은 브랜드 크롬만 뜻해야 한다. */\n.section-subtitle .ja {\n  color: var(--ink);\n  font-size: 16px;\n  font-weight: 700;\n  line-height: 24px;\n}\n'



def pick_rule(ids: list[str]):
    """덱의 페이지 이름만 보고 어느 트랙인지 알아낸다.

    코스 슬러그가 아니라 페이지 이름으로 고르는 이유: 도구가 받는 것은 레슨
    디렉토리 하나뿐이고, 같은 모양의 덱이면 어느 코스에 있든 같게 잘려야 한다.
    """
    if "article" in ids and "q1" in ids:
        return freetalk_keep, "freetalk"
    if any(i.endswith("-teach") for i in ids):
        return receptive_keep, "core/ctx"
    return hangul_keep, "hangul"


def receptive_keep(pages) -> list[str]:
    """기본 규칙으로 남길 페이지를 고른다."""
    ids = [p["data-page-id"] for p in pages] if not isinstance(pages[0], str) else list(pages)
    keep = []
    for pid in ids:
        if pid in KEEP_EXACT:
            keep.append(pid)
        elif any(pid.endswith(s) for s in PRODUCTIVE):
            continue
        elif any(pid.endswith(s) for s in RECEPTIVE):
            keep.append(pid)
    # 3부는 회화·롤플레이라 통째로 수업의 것이다. 그 파트의 내용 페이지가 하나도
    # 안 남았는데 도입만 남으면, 아무 데도 데려가지 않는 표지가 된다.
    #
    # 도입은 `part1-intro`, 그 파트의 내용은 `p1-teach` 로 이름이 붙는다 —
    # 그래서 앞자리를 그대로 비교하면 영영 안 맞는다. part1 → p1 로 맞춘 뒤 본다.
    def part_of(pid: str) -> str:
        return re.sub(r"^part(\d)", r"p\1", pid).split("-")[0]

    bodies = {part_of(pid) for pid in keep if not pid.endswith("-intro")}
    return [pid for pid in keep
            if pid in KEEP_EXACT or not pid.endswith("-intro")
            or part_of(pid) in bodies]


def strip_tutor(soup) -> None:
    """튜터가 있어야 뜻이 서는 것들을 걷어낸다.

    페이지만 덜어내면 **튜터의 장치가 그대로 따라온다.** 혼자 하는 화면에서
    그 셋은 전부 뜻을 잃는다:

    · 파란 상자의 `.ko` — 튜터가 소리 내어 읽는 대사다. 읽어 줄 사람이 없고,
      바로 밑에 같은 말을 하는 일본어가 이미 있다. 게다가 그 한국어 쪽이 굵고
      진해서, 일본어 학습자의 눈이 **못 읽는 글자에 먼저 간다.** 지우고 나면
      일본어가 그 자리(16px, 잉크, 볼드)로 올라온다.

      `.needs-jp` 를 켜면 안 된다. 그 클래스는 체험 덱의 「니즈 파악 세 장」용이라
      일본어를 앞세우는 김에 **라임 세일즈 배경까지 같이 온다** — 파란 스크립트
      상자가 통째로 라임 덩어리가 되고, 라임이 브랜드 크롬 말고 다른 것을 뜻하게
      된다. 활자 우선순위만 예습 스타일시트에서 따로 올린다.
    · 빨간 포인터(`spotlight.js`) — 두 화면에서 「여기요」를 가리키는 장치다.
      화면이 하나면 가리킬 상대가 없다.
    · 티칭 모드와 튜터 노트(`tutor-notes.js`, `.tutor-note`) — 진행 순서와 정답이
      들어 있는, 튜터 눈에만 보이는 메모다.
    · `.fb` / `.fb-adds` — 튜터가 학습자의 말을 받아 적고 고쳐 주는 칸.
    · `.anchor-ko` — 일본어 대응 표현을 한글로 적은 줄. 튜터가 일본어를 소리 내어
      말하라고 있는 것이라, 일본어 화자에게는 자기 말 옆의 못 읽는 글자다.

    페이지 제목은 한국어로 **남긴다**. 그건 이 시스템의 조판 규칙(한국어 제목 +
    괄호 안 일본어 훈)이고, 예습이 수업과 같아 보이게 하는 것의 일부다 —
    설명이 아니라 라벨이라 읽지 못해도 손해가 없다.
    """
    for line in soup.select(".section-subtitle > .ko"):
        line.decompose()
    for note in soup.select(".tutor-note"):
        note.decompose()
    # `.anchor-ko` 는 일본어 대응 표현(するとき)을 한글로 적어 둔 것이다 —
    # `ja_to_hangul.py` 가 만들고, **한국인 튜터가 일본어를 소리 내어 말하라고**
    # 있는 줄이다. 일본어 학습자가 혼자 읽을 때는 자기 모국어 옆에 붙은
    # 못 읽는 글자일 뿐이다.
    for anchor in soup.select(".anchor-ko"):
        anchor.decompose()
    # 프리토킹 질문 장의 피드백 칸(`학생 문장` · ＋교정 · ＋노트)은 수업 중에
    # **튜터가** 학습자의 말을 받아 적고 고쳐 주는 자리다. 혼자 있는 화면에서는
    # 고쳐 줄 사람이 없으므로 빈 칸과 눌러도 아무 일 없는 버튼만 남는다.
    for fb in soup.select(".fb, .fb-adds"):
        fb.decompose()

    # 목표 장의 예문 카드(`.known`)를 걷어낸다. 수업에서는 튜터가 이 세 줄을
    # 소리 내어 읽어 주며 「오늘 이런 걸 해요」를 들려주는 자리다. 혼자 보면
    # **아직 아무것도 안 배운 상태에서 완성된 문장 셋을 먼저 읽는** 셈이라,
    # 목표가 아니라 부담이 된다. 무엇을 배우는지는 바로 위 안내문이 이미 말한다.
    for goal in soup.select('[data-page-id="lesson-goal"] .known'):
        goal.decompose()

    drop_tutor_sentences(soup)
    japanese_only_labels(soup)
    for tag in soup.select("script[src]"):
        if any(x in tag["src"] for x in TUTOR_SCRIPTS):
            tag.decompose()



def drop_tutor_sentences(soup) -> None:
    """안내문에서 튜터의 역할 분담 문장만 도려낸다.

    한국어를 지워도 일본어 쌍둥이가 같은 말을 한다 — 「私が先にハナ役を読みます」.
    읽어 줄 「私」가 없으니 그 줄은 거짓말이다. 그런데 이건 덱마다 다른 문안이
    아니라 **상용구**다(484개 덱에서 312건 중 230건이 같은 두 문장). 그래서
    문장 단위로 목록에서 지운다 — 장면을 세우는 첫 문장은 혼자 읽어도 맞으므로
    남는다.
    """
    for ja in soup.select(".section-subtitle .ja"):
        text = ja.get_text(" ", strip=True)
        for old, new in TUTOR_REWRITE.items():
            text = text.replace(old, new)
        for drop in TUTOR_SENTENCES:
            text = text.replace(drop, "")
        # 남은 장 안에서 튜터의 목소리를 가리키는 «문장»만 골라 버린다.
        # 「私が先に読みます。」처럼 들려줄 사람이 있어야 성립하는 줄이다.
        kept = [x for x in re.split(r"(?<=。)", text) if x.strip() and not VOICE_SENT.search(x)]
        if len(kept) != len([x for x in re.split(r"(?<=。)", text) if x.strip()]):
            text = "".join(kept)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            ja.string = text
            if TUTOR_MARK.search(text):
                print(f"  ⚠ 튜터를 전제하는 새 문장: {text[:52]!r}\n"
                      f"    TUTOR_SENTENCES 에 넣거나 prestudy.overrides 로 고쳐라")
        else:
            box = ja.find_parent(class_="section-subtitle")
            (box or ja).decompose()


def japanese_deck_titles(soup) -> None:
    """일본어 짝이 없는 한국어 제목을, 덱이 이미 들고 있는 일본어로 갈아 끼운다.

    프리토킹의 읽을거리 제목은 덱마다 다른 편집 헤드라인이라(`번역이 안 되는 말 —
    빠지는 건 뜻이 아니라 온도`) `.title-ja` 짝이 없다. 그런데 **같은 파일 head 에
    이미 일본어 제목이 있다** — `<meta name="podo:title-ja">`. 새로 번역할 것이
    없으니 그것을 쓴다.

    페이저에 뜨는 액트 이름(`data-act`)도 한국어라, 고치지 않으면 학습자가 보는
    큰 글씨 셋 중 셋이 한국어가 된다.
    """
    meta = soup.select_one('meta[name="podo:title-ja"]')
    if meta is None or not meta.get("content"):
        return
    ja = meta["content"].strip()

    for page in soup.select('[data-page-id="article"]'):
        title = page.select_one(".section-title")
        if title is not None and not title.select_one(".title-ja"):
            title.clear()
            title.append(ja)

    for el in soup.select("[data-act]"):
        if re.search(r"[가-힣]", el["data-act"]):
            el["data-act"] = ja


def drop_empty_transitions(soup) -> None:
    """일본어가 한 글자도 없는 파트 표지를 버린다.

    파트 표지는 보통 한국어 제목 + `.title-ja` 짝 + 안내문으로 되어 있는데,
    둘 다 없는 표지가 섞여 있다(10과 `batchim-r-intro`: 제목이 「받침 ㄹ」뿐).
    라벨을 일본어로 바꿔 줄 재료가 없으니, 잘라 놓으면 까만 배경에 못 읽는
    한국어 한 줄만 뜬 장이 된다. 표지는 다음 장으로 데려가는 것이 일인데
    그 일을 못 하므로 버린다.
    """
    for page in soup.select(".transition-page[data-page-id]"):
        title = page.select_one(".transition-title")
        if title is None or title.select_one(".title-ja"):
            continue
        body = page.select_one(".transition-copy, .section-subtitle")
        if body is None or not body.get_text(strip=True):
            page.decompose()


def renumber_parts(soup) -> None:
    """살아남은 파트 표지의 번호를 1부터 다시 매긴다.

    파트 하나가 통째로 빠지면 「パート 1 → パート 3」처럼 구멍이 보인다.
    학습자는 자기가 뭘 빼먹었다고 읽지, 원래 없다고 읽지 않는다.
    """
    kickers = [k for k in soup.select(".transition-kicker")
               if re.fullmatch(r"パート\s*\d+", k.get_text(" ", strip=True))]
    for i, k in enumerate(kickers, 1):
        k.clear()
        k.append(f"パート {i}")


def japanese_only_labels(soup) -> None:
    """라벨에서 한국어를 걷어내고 일본어만 남긴다.

    한국어를 지워도 되는 자리와 절대 안 되는 자리를 마크업이 이미 구별해 준다:

      라벨   한국어 + **일본어 쌍둥이**(`.title-ja` 또는 `<small>`)
             「받침 있음 <small>パッチムあり</small>」 — 같은 말을 두 번 한다.
      내용   한국어 + **가나 읽기**(`.yomi`)
             「먹 → 먹을 때 <span class="yomi">モグル ッテ</span>」 — 배우는 것 자체다.

    그래서 일본어 쌍둥이가 있는 것만 골라 한국어를 버린다. 받침 설명이 여기 걸린다.
    `.bt-ex` 처럼 읽기만 달린 것은 손대지 않는다 — 거기 한국어가 이 과의 알맹이다.
    """
    for el in soup.select(".section-title, .transition-title"):
        twin = el.select_one(".title-ja")
        if twin is None:          # 형태 자체가 제목인 장(-(으)ㄹ 때)은 건드리지 않는다
            continue
        text = re.sub(r"^[（(]|[）)]$", "", twin.get_text(" ", strip=True)).strip()
        el.clear()
        el.append(text)

    # 키커에는 일본어 쌍둥이가 없다. 붙박이 라벨이라 종류가 몇 개 안 되므로
    # 표로 옮긴다. 표에 없는 한국어 키커는 조용히 지나가지 않고 경고를 낸다 —
    # 새 라벨이 생겼는데 아무도 모르는 채로 나가는 것이 제일 나쁘다.
    for el in soup.select(".transition-kicker"):
        text = el.get_text(" ", strip=True)
        if not re.search(r"[가-힣]", text):
            continue
        # 회차 번호(제3화, 쇼핑 여행 · 제3화)는 표에 적어 둘 것이 아니라 규칙이다.
        # 앞에 붙은 코스 이름은 버리고 회차만 남긴다 — 페이저 옆의 작은 라벨이라
        # 코스 이름까지 일본어로 옮길 자리가 없고, 학습자는 이미 그 코스 안에 있다.
        ep = re.search(r"제\s*(\d+)\s*화", text)
        if ep:
            el.clear()
            el.append(f"第{ep.group(1)}話")
            continue
        if text in KICKER_JA:
            el.clear()
            el.append(KICKER_JA[text])
        else:
            print(f"  ⚠ 일본어로 옮길 말을 모르는 키커: {text!r} — KICKER_JA 에 넣어라")

    for el in soup.select(".meaning-kicker, .bt-head"):
        twin = el.find("small")
        if twin is None:
            continue
        text = twin.get_text(" ", strip=True)
        el.clear()
        el.append(text)


def apply_overrides(soup, lesson: pathlib.Path) -> int:
    """`prestudy.overrides` 가 있으면 파란 상자의 일본어를 갈아 끼운다.

    걷어내는 것으로 안 되는 자리가 딱 하나 있다. 수업 덱의 안내문 중에는
    **튜터가 1인칭으로** 하는 말이 있고(「제가 하나 역할을 먼저 읽어 볼게요」),
    한국어를 지워도 그 일본어 쌍둥이가 같은 말을 그대로 한다 —
    「私が先にハナ役を読みます」. 읽어 줄 「私」가 없으므로 그 줄은 거짓말이 된다.

    자동으로 고칠 수 있는 문제가 아니라(문안이다) 손으로 적어 두고, 다시 뽑을
    때마다 다시 입힌다. 51과 기준으로 덱 하나에 한 줄이었다.

    형식 — 한 줄에 `page-id<TAB>새 일본어`:

        p3-model	ハナがハルカに一日の習慣を聞きます。まず音を聞いてみましょう。
    """
    f = lesson / "prestudy.overrides"
    if not f.exists():
        return 0
    done = 0
    for raw in f.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        pid, _, text = line.partition("\t")
        page = soup.select_one(f'[data-page-id="{pid.strip()}"]')
        if page is None:
            print(f"  ⚠ overrides: 없는 페이지 {pid.strip()}")
            continue
        ja = page.select_one(".section-subtitle .ja")
        if ja is None:
            print(f"  ⚠ overrides: {pid.strip()} 에 일본어 안내문이 없다")
            continue
        ja.string = text.strip()
        done += 1
    return done


def cut_in_place(deck: pathlib.Path, keep: list[str] | None = None,
                 lesson: pathlib.Path | None = None, quiet: bool = False) -> int:
    """이미 빌드된 예습 덱을 «그 자리에서» 잘라낸다. 남은 장 수를 돌려준다.

    `promote.py` 가 부른다. promote 는 두 슬롯에 같은 덱을 깔아 놓으므로,
    그중 prestudy 쪽을 이 함수가 예습으로 바꾼다 — 페이지를 덜어내고, 튜터의
    장치를 걷어내고, 라벨을 일본어로 만들고, 자기 deck.css 를 심는다.

    체험 덱이면 아무것도 하지 않고 0 을 돌려준다. 체험은 수업이 아니라 판매
    자료라 예습이 없고, 두 슬롯이 같은 덱인 지금 동작이 맞다.
    """
    html_path = deck / "index.html"
    soup = soup_of(html_path)
    pages = soup.select("[data-page-id]")
    if not pages:
        return 0
    ids = [p["data-page-id"] for p in pages]
    if TRIAL_MARK & set(ids):
        return 0

    # 트랙 판별은 **언제나** 페이지 이름으로 한다. keep 은 «어느 장을 남길지»만
    # 덮어쓴다. 예전에는 keep 이 오면 rule 을 "--keep" 으로 바꿔 버려서,
    # CLI 로 뽑은 프리토킹 덱만 질문 합치기를 건너뛰고 11장으로 나왔다 —
    # promote 경로와 CLI 경로가 다른 결과를 내는, 제일 나쁜 종류의 버그다.
    fn, rule = pick_rule(ids)
    wanted = set(keep) if keep is not None else set(fn(pages))

    # 액트 이름은 **아무것도 지우기 전에** 챙긴다. decompose() 한 태그는 attrs 가
    # None 이 되어 나중에 .get() 하면 터진다 — 질문 합치기가 여덟 장을 지운 뒤
    # 이 줄을 만나 실제로 터졌다.
    acts = [p.get("data-act") for p in pages]

    # 질문 모으기가 **먼저**다. strip_tutor 가 파란 상자의 `.ko` 를 지우는데,
    # 모으기는 그 한국어를 읽어 카드를 만든다 — 순서를 바꾸면 빈 장이 나온다.
    if rule == "freetalk" and collapse_questions(soup):
        # 합치면서 만든 장은 원래 목록에 없다. 넣어 주지 않으면 바로 아래
        # 지우기 루프가 방금 만든 장을 도로 지운다.
        wanted.add("questions")

    # **먼저 지운다.** 뒤따르는 손질(튜터 문장 걷어내기, 라벨 일본어화)은 문서
    # 전체를 훑으므로, 지우기를 나중에 하면 «어차피 빠질 장»을 두고 경고가 난다 —
    # 실제로 남지도 않을 p2-write 의 「今度は私に聞く番です」로 430건이 났다.
    # 경고 채널이 소음이 되면 진짜 경고가 묻힌다.
    for page in soup.select("[data-page-id]"):
        if page.get("data-page-id") not in wanted:
            page.decompose()

    strip_tutor(soup)
    if lesson is not None:
        apply_overrides(soup, lesson)
    drop_tutor_sentences(soup)
    japanese_only_labels(soup)
    drop_empty_transitions(soup)
    japanese_deck_titles(soup)

    survivors = soup.select("[data-page-id]")
    if survivors and not survivors[0].get("data-act"):
        first = next((a for a in acts if a), None)
        if first:
            survivors[0]["data-act"] = first

    # 번호는 **지운 뒤에** 다시 매긴다. 파트가 통째로 빠지면 「パート 1 →
    # パート 3」처럼 구멍이 보이고, 학습자는 자기가 빼먹었다고 읽는다.
    renumber_parts(soup)

    html_after_cut = soup.decode(formatter=keep_attr_order())

    # 장을 덜어내면 그 장만 쓰던 그림·아이콘이 주인을 잃는다(아바타, 삽화,
    # 아이콘 svg). promote 가 공유 자산을 덱 안으로 복사해 두는데 repoint 는
    # **자기가 CDN 으로 옮긴 것만** 지우므로, 아무도 안 부르는 파일은 그대로
    # 남아 zip 에 실린다 — 한 번 돌려 보니 432개였다.
    referenced = set(re.findall(r'(?:src|href)="([^"]+)"', html_after_cut))
    for f in deck.iterdir():
        if not f.is_file() or f.name in ("index.html", "deck.css"):
            continue
        if f.name not in referenced:
            f.unlink()

    # 스크립트 태그를 지웠으니 그 파일도 치운다. promote 가 공유 런타임을 덱
    # 안으로 복사해 두는데, repoint 는 **자기가 CDN 으로 옮긴 것만** 지운다 —
    # 아무도 안 부르는 파일은 주인이 없어 그대로 남아 zip 에 실린다.
    for name in TUTOR_SCRIPTS:
        orphan = deck / name
        if orphan.exists():
            orphan.unlink()

    (deck / "deck.css").write_text(PRESTUDY_CSS, encoding="utf-8")

    html = soup.decode(formatter=keep_attr_order())
    # 링크는 **문자열로** 심는다. bs4 로 만들면 속성이 알파벳순(href 먼저)으로
    # 나오는데, `repoint-shared.py` 의 LINK_RE 는 rel 이 href 앞에 오는 형태만
    # 잡는다. 못 잡으면 「로컬 스타일시트가 없다」고 판단해 **우리 deck.css 를
    # 빈 stub 으로 덮어쓰고** 링크를 하나 더 붙인다 — 조용히, 오류 없이.
    # 실제로 그렇게 당했다. 다른 도구가 읽을 마크업은 그 도구가 기대하는
    # 모양으로 쓴다.
    if 'href="deck.css"' not in html:
        html = html.replace("</head>",
                            '  <link rel="stylesheet" href="deck.css">\n</head>', 1)

    html_path.write_text(html, encoding="utf-8")
    if not quiet:
        print(f"    예습 {len(survivors)} 장  [{rule}]")
    return len(survivors)


def build(lesson: pathlib.Path, keep: list[str] | None, check: bool) -> int:
    """CLI: 수업 덱을 잘라 `<lesson>/prestudy/` 에 쓴다.

    자르는 절차는 `cut_in_place` 하나뿐이다 — promote 가 부르는 것과 **같은
    함수**다. 예전에는 여기에 같은 절차가 한 벌 더 있었는데, 그러면 한쪽만
    고쳐지고 두 덱이 조용히 달라진다.
    """
    lecture_dir = lesson / "lecture"
    lecture = lecture_dir / "index.html"
    if not lecture.exists():
        sys.exit(f"수업 덱이 없다: {lecture}")

    soup = soup_of(lecture)
    pages = soup.select("[data-page-id]")
    ids = [p["data-page-id"] for p in pages]
    if not ids:
        sys.exit("✗ data-page-id 가 없다. 이 덱은 이 도구로 자를 수 없다.")
    if TRIAL_MARK & set(ids):
        sys.exit("✗ 체험 덱은 예습을 만들지 않는다 — 수업이 아니라 판매 자료다.\n"
                 f"  ({', '.join(sorted(TRIAL_MARK & set(ids)))} 장이 있다)")

    if keep is not None:
        wanted, rule = keep, "--keep"
    else:
        fn, rule = pick_rule(ids)
        wanted = fn(pages)
    unknown = [k for k in wanted if k not in ids]
    if unknown:
        sys.exit("✗ 수업 덱에 없는 페이지: " + ", ".join(unknown))

    print(f"{lesson.name}:  수업 {len(ids)} 장 → 예습 {len(wanted)} 장  [{rule}]")
    for pid in ids:
        print(f"  {'남김' if pid in wanted else '   ·'}  {pid}")

    # 예산은 «합친 뒤» 장 수로 잰다. 프리토킹은 질문 여덟 장이 한 장이 되므로,
    # 합치기 전 숫자로 재면 210개 덱 전부가 경고를 뱉는다 — 그러면 ⚠ 라는
    # 채널이 소음이 되고, 진짜 경고(새 튜터 문장, 못 옮긴 키커)가 묻힌다.
    final = len(wanted)
    if rule == "freetalk":
        nq = len([k for k in wanted if re.fullmatch(r"warm-\d+|q\d+", k)])
        if nq >= 3:
            final = final - nq + 1
    lo, hi = (3, 6) if rule == "freetalk" else (10, 15)
    if not lo <= final <= hi:
        print(f"\n⚠ {final} 장 — 이 트랙의 예산은 {lo}–{hi} 장이다. "
              f"--keep 으로 조정하라.")

    if check:
        print("\n(--check — 아무것도 쓰지 않았다)")
        return 0

    out = lesson / "prestudy"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(lecture_dir, out)
    n = cut_in_place(out, keep=wanted, lesson=lesson, quiet=True)
    print(f"\n→ {out / 'index.html'}  ({n} 장)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("lesson", type=pathlib.Path,
                    help="lecture/ 를 품은 레슨 디렉토리")
    ap.add_argument("--keep", help="남길 data-page-id 목록 (쉼표로 구분)")
    ap.add_argument("--check", action="store_true", help="무엇이 잘릴지만 보여 준다")
    a = ap.parse_args()
    keep = [k.strip() for k in a.keep.split(",")] if a.keep else None
    return build(a.lesson.resolve(), keep, a.check)


if __name__ == "__main__":
    sys.exit(main())
