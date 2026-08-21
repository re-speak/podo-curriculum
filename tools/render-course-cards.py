#!/usr/bin/env python3
"""
체험 리포트의 코스 카드를 PNG 로 구워 `shared/assets` 에 넣는다.

원톡 상담 안내(podo-app#2440)가 체험 직후 학생에게 추천 코스 카드를 보낸다. 원톡 메시지에는
리치 카드가 없어 이미지로 보내야 하는데, 이 카드는 사진 셋과 겹친 말풍선으로 되어 있어
받는 쪽에서 다시 그릴 수가 없다. 그래서 **덱이 그린 것을 그대로 찍는다** — 카드 디자인의
정본은 언제나 `shared/js/report.js` + `shared/css/trial.css` 한 곳이고, 이 스크립트는
그 결과를 옮겨 담기만 한다.

    python3 tools/render-course-cards.py [--out DIR] [--scale 3] [--keep-korean]

카드에서 빼는 것 셋:
  - 회색 설명 줄(`.hy-cap`) — 확정 초안이 뺐다.
  - 진행 표시(`.hy-no`, 「3 / 4」) — 학생의 로드맵 위치라 코스마다 고정이 아니다.
  - 레슨 수 알약(`.hy-n`) — 핵심 패턴은 목표에 따라 값이 달라져(courseLen) 카드가 학생마다
    갈린다. 알약을 빼면 여섯 장 모두 코스당 한 장으로 고정된다. 기간은 채팅 말풍선이 말한다.

일본어: 덱은 내부 확인용 한국어판이라 `tools/course-card-ja.json` 의 문안으로 덮어쓴다.
덱 자체가 일본어가 되면 그 파일을 비우면 되고, 그때부터 이 스크립트는 찍기만 한다.

authoring 전용이다. build · validate · plan · apply 는 playwright 를 import 하지 않으므로
playwright 는 tools/requirements.txt 에 없다 — 휠이 41MB 라 게이트와 배포가 매번 받을
이유가 없다. 없으면 이 스크립트가 설치 명령을 찍어 준다.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DECK = REPO / "courses/kr/trial-lv1-hangul/lessons/01-trial-hangul/lecture/index.html"
OVERRIDES = REPO / "tools/course-card-ja.json"
DEFAULT_OUT = REPO / "shared/assets"

# 코스 하나를 화면에 세우는 법 — 덱의 니즈 답을 이렇게 고르면 로드맵의 step 번째 칸이 그 코스다.
# 세 조합이 여섯 코스를 모두 덮는다. (level 1 은 한글·핵심이 로드맵에 남게 하는 조건이다.)
PLANS = [
    {"why": "friend", "goal": "t7", "steps": {"hangul": 0, "core": 1, "banmal": 2}},
    {"why": "kpop", "goal": "t9", "steps": {"drama": 2, "free": 3}},
    {"why": "travel", "goal": "t9", "steps": {"travel": 2}},
]

# 카드에서 지우는 조각들. 지우는 이유는 모듈 docstring 에 있다.
STRIP = (".hy-cap", ".hy-no", ".hy-n")


def load_overrides() -> dict:
    if not OVERRIDES.exists():
        return {}
    return json.loads(OVERRIDES.read_text(encoding="utf-8")).get("courses", {})


def build_page_script(step: int, expect_deck: str, override: dict, strip: bool) -> str:
    """로드맵을 step 칸으로 옮기고, 문안을 덮어쓰고, 빼기로 한 조각을 지운다.

    실패하면 `{error: ...}` 를 돌려준다. 부르는 쪽이 그걸 보고 그 코스를 건너뛴다.
    """
    return f"""
    () => {{
      const road = document.querySelector('.road-card');
      const prev = road && road.querySelector('.rc-prev');
      const next = road && road.querySelector('.rc-next');
      if (!prev || !next) return {{ error: '로드맵을 찾지 못했습니다 (.road-card)' }};

      // 0 칸으로 되감고 step 칸 앞으로. 버튼은 양 끝에서 disabled 가 되므로(report.js
      // stepRoad) 횟수를 세는 대신 그것을 신호로 쓴다 — 로드맵이 길어져도 맞는다.
      for (let i = 0; i < 64 && !prev.disabled; i += 1) prev.click();
      if (!prev.disabled) return {{ error: '로드맵을 처음으로 되감지 못했습니다' }};
      for (let i = 0; i < {step} && !next.disabled; i += 1) next.click();

      const source = document.querySelector('.hy');
      if (!source) return {{ error: '카드를 찾지 못했습니다 (.hy)' }};

      // 덮어쓰기 전에 덱이 이 칸을 뭐라고 부르는지 본다. 칸 번호만 맞춰서는 부족하다 —
      // 어긋나도 제목·설명은 덮어써서 맞고 사진만 다른 코스가 되므로, 구운 결과를 눈으로
      // 보아도 걸리지 않는다. 이름이 다르면 여기서 멈춘다.
      const expect = {json.dumps(expect_deck, ensure_ascii=False)};
      const actual = String(source.querySelector('.hy-h b').textContent).trim();
      if (expect && actual !== expect) {{
        return {{ error: `{step} 칸은 「${{actual}}」 입니다 (기대: 「${{expect}}」)` }};
      }}

      // 덱은 슬라이드라 카드가 안 보이는 장에 있다. 같은 문서 안 오버레이로 복제하면
      // 스타일시트는 그대로 적용되면서 화면에 세울 수 있다 — 덱의 장 넘김에 기대지 않는다.
      document.querySelector('#__card_stage')?.remove();
      const stage = document.createElement('div');
      stage.id = '__card_stage';
      stage.setAttribute(
        'style',
        'position:fixed;inset:0;z-index:2147483647;background:#fff;display:flex;' +
          'align-items:flex-start;justify-content:flex-start;padding:24px',
      );
      const card = source.cloneNode(true);
      card.style.width = '286px';
      stage.appendChild(card);
      document.body.appendChild(stage);

      const override = {json.dumps(override, ensure_ascii=False)};
      if (override.title) card.querySelector('.hy-h b').textContent = override.title;
      if (override.outcome) card.querySelector('.hy-do').textContent = override.outcome;

      if ({str(strip).lower()}) {{
        for (const selector of {json.dumps(list(STRIP))}) {{
          card.querySelectorAll(selector).forEach((el) => el.remove());
        }}
      }}

      return {{
        title: card.querySelector('.hy-h b').textContent,
        outcome: card.querySelector('.hy-do').textContent,
      }};
    }}
    """


def render(out_dir: pathlib.Path, scale: int, keep_korean: bool) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright 가 없습니다. 이 스크립트 전용 의존성입니다:\n"
            "    python3 -m pip install playwright && python3 -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    if not DECK.exists():
        print(f"덱을 찾지 못했습니다: {DECK}", file=sys.stderr)
        return 2

    # 한 파일에서 둘을 읽는다: 덮어쓸 일본어 문안과, 맞는 코스인지 볼 덱 이름.
    # `--keep-korean` 은 덮어쓰기만 끄고 확인은 그대로 둔다 — 확인이야말로 늘 필요하다.
    catalog = load_overrides()
    overrides = {} if keep_korean else catalog
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 900, "height": 1400}, device_scale_factor=scale
        )
        page.goto(DECK.as_uri())
        page.wait_for_selector(".hy", state="attached", timeout=15_000)

        for plan in PLANS:
            # 니즈 답을 고르면 로드맵의 코스 구성이 정해진다. 덱은 슬라이드라 답 버튼도
            # 다른 장에 있어 보이지 않는다 — 보이는지 따지지 않고 DOM 에서 직접 누른다.
            answers = (("level", "1"), ("why", plan["why"]), ("goal", plan["goal"]), ("pace", "3"))
            page.evaluate(
                """(answers) => {
                    for (const [group, value] of answers) {
                        const button = document.querySelector(
                            `[data-group="${group}"] button[data-val="${value}"]`,
                        );
                        if (button) button.click();
                    }
                }""",
                [list(pair) for pair in answers],
            )

            for key, step in plan["steps"].items():
                target = out_dir / f"course-card-ja-{key}.png"

                info = page.evaluate(build_page_script(
                    step, catalog.get(key, {}).get("deck", ""), overrides.get(key, {}), True))
                if not info or info.get("error"):
                    reason = info.get("error") if info else "페이지가 아무것도 돌려주지 않았습니다"
                    print(f"  ! {key}: {reason}", file=sys.stderr)
                    continue

                card = page.query_selector("#__card_stage .hy")
                card.screenshot(path=str(target))
                written += 1
                print(f"  {target.name}  {info['title']} — {info['outcome']}")

            page.reload()
            page.wait_for_selector(".hy", state="attached", timeout=15_000)

        browser.close()

    expected = sum(len(plan["steps"]) for plan in PLANS)
    print(f"\n{written}/{expected}장을 {out_dir} 에 썼습니다.")
    if written != expected:
        # 다음 단계가 발행이다. 반쯤 구운 채로 0 을 돌려주면 그대로 태그에 실린다.
        print("✗ 일부를 굽지 못했습니다 — 발행하지 마십시오.", file=sys.stderr)
        return 1

    print("다음: curriculum.yaml 의 spec.sharedRuntime.version 을 올리고")
    print("      `python3 tools/publish-shared.py` 로 새 태그를 올린다.")
    print("      podo-app 은 @latest 를 보므로 배포가 따로 필요하지 않다.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT, help="PNG 를 쓸 곳 (기본 shared/assets)")
    parser.add_argument("--scale", type=int, default=3, help="배율 (기본 3)")
    parser.add_argument("--keep-korean", action="store_true", help="일본어 덮어쓰기 없이 덱 그대로 찍는다")
    args = parser.parse_args()
    return render(args.out, args.scale, args.keep_korean)


if __name__ == "__main__":
    raise SystemExit(main())
