# 새 덱 만들기 — 컴포넌트와 뼈대

새 과를 만들 때 **CSS 도 자바스크립트도 쓰지 않습니다.** 아래 마크업을 얹으면
배선(입력·채점·공유·페이지 넘김)은 공유 스크립트가 합니다. 새 클래스를 만들기
전에 이 목록에 이미 있는 것을 먼저 찾아보세요 — 어휘가 하나 늘 때마다 덱 사이의
일관성이 한 칸씩 줄어듭니다.

설계 원칙은 [`ux-philosophy.md`](../ux-philosophy.md) 에 있습니다.
이 문서는 **무엇을 쓸 수 있는가**만 적습니다.

> **그래도 새 컴포넌트를 만들었다면, 이름을 `runtime/js/spotlight.js` 의 `SPOT`
> 목록에 넣으세요.** 그 목록에 있는 것만 튜터가 빨간 링으로 짚을 수 있고, 빠뜨려도
> 아무 에러가 나지 않습니다 — 그 블록만 조용히 안 켜집니다. 블록 안에서 따로 짚을
> 이름이 있는 부품(예: 규칙 카드 안의 글자 하나)도 같이 넣으면 됩니다. 한 겹씩
> 들어가는 방식이라 부품을 넣는다고 블록을 못 짚게 되지는 않습니다.
> 이유는 [`ux-philosophy.md` § The shared pointer](../ux-philosophy.md) 에 있습니다.

---

## 1 · 파일 뼈대

경로는 `korean/trial/lessons/deck.html` 처럼 **저장소 루트에서 세 단계 아래**에 있는 덱
기준입니다. 한 단계 위(`korean/tracks/2-core-patterns/`)에 두면 `../` 하나를 빼고,
실제 레슨 자리(`korean/tracks/<t>/courses/<c>/lessons/<slug>/`)는 일곱 단계라
`../` 가 일곱 개입니다.

> **`runtime/` 은 이제 저장소 루트에 있습니다** — `korean/` 안이 아닙니다. 한국어와 영어
> 커리큘럼이 같은 런타임을 씁니다. `trial/assets/` 는 옮기지 않았으므로 그대로 `korean/`
> 안에 있고, 그쪽 경로는 예전과 같습니다.

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google" content="notranslate">        <!-- 없으면 크롬이 ja/ko 를 섞어 망가뜨린다 -->
  <meta name="podo:lesson-id" content="trial-2-selfintro">
  <meta name="podo:content-version" content="2026-08-05">
  <title>…</title>
  <link rel="stylesheet" href="../../../runtime/css/lesson-card.css">
  <link rel="stylesheet" href="../../../runtime/css/trial.css">
</head>
<body>
  <div class="phone">
    … 페이지들 …
  </div>

  <!-- 페이저 (스크러버 포함) -->
  <nav class="pager" data-sync-id="deck-page" data-sync-kind="page">
    <input class="pg-scrub" type="range" min="0" max="0" step="1" value="0" aria-label="페이지 이동">
    <button class="pg-btn pg-prev" type="button" aria-label="이전 페이지">←</button>
    <div class="pg-mid"><span class="pg-label"><b class="pg-act">—</b><span class="pg-n">—</span></span></div>
    <button class="pg-btn pg-teach" type="button" aria-label="티칭 모드">T</button>
    <button class="pg-btn pg-next" type="button" aria-label="다음 페이지">→</button>
  </nav>

  <img class="stamp-art" src="../assets/well-done.svg" alt="">   <!-- .phone 바깥! -->

  <script src="../../../runtime/js/activities.js"></script>
  <script src="../../../runtime/js/feedback.js"></script>     <!-- 문장 피드백을 쓰는 덱 -->
  <script src="../../../runtime/js/pager.js"></script>
  <script src="../../../runtime/js/script-lines.js"></script>
  <script src="../../../runtime/js/spotlight.js"></script>
  <script src="../../../runtime/js/tutor-notes.js"></script>
  <script src="../../../runtime/js/highlight.js"></script>
  <script src="../../../runtime/js/stamp.js"></script>
  <script src="../../../runtime/js/yomi.js"></script>          <!-- 발음 표기를 쓰는 덱만 -->
</body>
</html>
```

**로드 순서는 지켜야 합니다.** `activities` → `feedback`(쓰는 덱만) → `pager`(티칭 모드가 activities 가 만든
유령 답을 부른다) → `script-lines` → `tutor-notes`(페이지를 다 센 뒤에 칸을 끼운다) →
`highlight`(글자에 긋는 형광펜 — 마크업이 다 선 뒤에 `<mark>` 를 끼운다) → `stamp`.

과의 성격에 따라 `activities.js` 바로 뒤에 한 줄을 더합니다:

| 과 | 추가 |
| --- | --- |
| 한글(자모·음절) | `runtime/js/hangul-activities.js` |
| Core·Contextual·자유 대화의 문장 피드백 | `runtime/js/feedback.js` |
| 자유 대화(고르기·예습 지문) | `runtime/js/freetalk-activities.js` |

---

## 1-2 · 체험 레슨 풀덱 (`full-trials/`)

풀덱은 **레슨 덱에 앞뒤 열다섯 장을 두른 것**입니다. 레슨은 `lessons/` 의 것을
그대로 쓰고, 감싸는 페이지는 네 덱이 모두 같은 것을 씁니다.

```
cover · greeting
  needs-intro · needs-why · needs-goal · needs-pace          ← 니즈 파악 4장
  … 레슨 전체(trial-intro … todays-result) …
  report-intro · report                                       ← 리포트 2장
  info-intro · info-podo · info-about · plan-curriculum ·
  info-tutors · plan-price · plan-switch · info-price-all ·
  info-faq                                                    ← 안내(판매) 9장
closing
```

- 감싸는 페이지의 CSS 는 `runtime/css/trial.css` 의 「FULL TRIAL」 절에 있습니다.
- 리포트의 레벨 체크·항목별 진단·로드맵 배선은 `runtime/js/report.js` 입니다.
  풀덱은 `activities.js` 다음에 이 줄을 하나 더 답니다.
- 감싸는 페이지는 레슨과 무관한 판매 자료라, 새 풀덱을 만들 때는 다른 풀덱에서
  이 열다섯 장을 그대로 복사해 오면 됩니다.

---

## 2 · 페이지 (`.phone` 의 자식 하나 = 한 장)

모든 페이지에 **`data-page-id`** 를 답니다. 공유되는 것은 순서가 아니라 이 id 라서,
나중에 페이지를 끼워 넣어도 상대 화면이 어긋나지 않습니다.

| 무엇 | 마크업 |
| --- | --- |
| 표지 | `<div class="brand-page" data-page-id="cover">` + `.podo-badge` + `.brand-title` |
| 파트 구분(라임) | `<div class="brand-page divider">` + `.brand-mascot` + `.brand-title` + `.brand-sub` |
| 파트 전환(어두운) | `<div class="transition-page" data-act="N이에요 / 예요">` + `.transition-kicker` + `.transition-title` + `.transition-copy` |
| 학습 페이지 | `<div class="section" data-page-id="p1-teach">` |
| 마무리 | `<div class="brand-page end">` |

`data-act` 는 페이저 왼쪽에 뜨는 장 이름입니다. 붙인 페이지에서 새 장이 시작됩니다.

어두운 `partN-intro` 는 문법 설명 상자가 아니라 호흡과 장면을 잇는 페이지입니다.
`.transition-copy` 에는 일본어 장면 다리 한 줄만 두고, 뜻과 쓰임은 다음 학습 페이지로
옮깁니다.

### 학습 페이지 한 장의 구조

```html
<div class="section" data-page-id="p1-fill">
  <h2 class="section-title">빈칸을 채워요 <span class="title-ja">(空欄をうめよう)</span></h2>
  <p class="section-subtitle"><span class="ko">…</span><span class="ja">…</span></p>
  <div class="tutor-note">학생이 말한 대로 빈칸에 적어 주세요.</div>   <!-- 튜터만, 선택 -->
  … 활동 하나 …
</div>
```

패턴을 처음 가르치는 `pN-teach` 는 일반 지시문 대신 이 이중 언어 상자로 시작합니다.

```html
<p class="section-subtitle pattern-meaning">
  <span class="meaning-kicker">뜻과 쓰임 <small>意味・使い方</small></span>
  <span class="anchor">                          <!-- 2-core-patterns 만 -->
    <span class="anchor-ja">~はずがない</span>
    <span class="anchor-ko">하즈가나이</span>
  </span>
  <span class="ko">언제 손이 가는지 한 문장.</span>
  <span class="ja">同じ内容の日本語。</span>
</p>
```

파란 면은 튜터가 읽는 한국어이고, 안쪽의 밝은 일본어 줄은 학생에게 짚어 줄 정확한
대역입니다. 별개의 새 설명을 일본어 줄에 더하지 않습니다. 형태를 만드는 법은 `pN-rule`
에서 다룹니다.

`.anchor` 는 **코어 패턴 트랙에만** 붙입니다. `.anchor-ja` 가 이 형태의 일본어 대응,
`.anchor-ko` 가 그 일본어를 한글로 읽은 것입니다 — 한국어 튜터가 가나를 읽을 수 있다고
가정하지 않기 때문입니다. 읽기는 손으로 쓰지 말고 `korean/tools/ja_to_hangul.py` 로 뽑으세요.
앵커가 붙으면 `.ko` 는 한 문장 60자, 안 붙으면 두 문장 90자입니다. 자세한 근거는 각 트랙의
`lesson-blueprint.md` 에 있습니다.

### 가르치는 면에 걸리는 여섯 가지 (`check_teaching.py`)

덱을 쓰고 나면 `python3 korean/tools/check_teaching.py <deck…>` 를 돌립니다.

1. **앵커** — 코어 트랙의 `pN-teach` 는 `.anchor` 슬롯 + 말하는 줄 한 문장.
2. **소리 내어 읽는 줄에 일본어 금지** — `.ko` 안에 가나·한자를 넣지 않습니다. 도움이 되는
   일본어라면 `.tutor-note` 로 옮기고 괄호 안에 한글 읽기를 답니다 — `‘ですね(데스네)’면 ‘네요’예요`.
3. **과 번호 금지** — 본문, 튜터 노트, 도식 라벨, 칩 어디에도 쓰지 않습니다. 튜터도 학습자도
   「90과」를 그 자리에서 알아볼 수 없습니다. 번호 대신 형태를 이름으로 부릅니다.
4. **상투적 마무리 금지** — `제가 읽을게요. 잘 듣고 따라 읽어 보세요.` 는 255장 중 246장에서
   글자 하나 다르지 않았습니다. 튜터는 한 번 배우면 됩니다.
5. **길이** — 위의 60/90자, 그리고 규칙 페이지 부제는 105자.
6. **화면을 세기만 하는 문장 금지** — `네 문장이에요.` 는 그 네 문장 옆에서 126장에
   서 있었습니다. 학습자가 보면 아는 것을 말로 옮기기만 하는 문장은 자리만 차지합니다.
   **세는 말이 지시문 안에 들어간 것은 다릅니다** — `네 문장을 따라 읽어 보세요` 는 그
   페이지의 지시문이고, 이 규칙은 **문장 전체가 숫자뿐일 때만** 걸립니다. 모두 찾는
   활동은 예외입니다: `‘웨’로 읽는 글자를 모두 눌러 보세요. 세 개예요.` 에서 숫자는
   그만 찾아도 된다는 신호라 화면을 옮겨 적은 것이 아닙니다.

규칙 페이지 부제에는 성격상 하나가 더 붙습니다. **부제는 바로 밑의 도식이 이미 그린 것을
말로 다시 읽지 않습니다.** 「받침이 없으면 X, 있으면 Y」는 `.batchim` 이 이미 세 상자로
그려 놓은 내용이고, 부제는 도식이 말할 수 없는 것 하나를 더합니다. 이건 글자 수로 잡히지
않아 사람이 봐야 합니다.

- 제목은 **한국어 먼저**, 일본어는 괄호 안 `.title-ja`.
- `.section-subtitle` 은 **튜터가 소리 내어 읽는 줄**입니다(`blue-100` 은 이 뜻 하나뿐).
  `.ko` 가 읽는 말, `.ja` 는 그 번역 — 둘은 **같은 문장**이어야 합니다.
- **문장 안에 인용한 표현은 따옴표로 묶습니다** — 한국어는 `‘ ’`, 일본어는 `「 」`.
  아래 「인용한 표현」 절을 보세요.
- `.tutor-note` 는 스크립트 바로 밑에 붙는 튜터 전용 띠입니다. 한국어로 씁니다.
- **활동은 한 장에 하나.** 두 종류를 한 화면에 섞지 않습니다.

### 인용한 표현 — `‘ ’` 와 `「 」`

가르치는 표현을 문장 안에 그대로 끌어다 쓰는 일이 아주 잦습니다. 그 표현은
**따옴표로 묶습니다** — `.ko` 안에서는 `‘ ’`, `.ja` 안에서는 `「 」`.

```html
<!-- 안 묶으면: 어디서 표현이 끝나고 설명이 시작되는지 눈으로 잡히지 않습니다 -->
<span class="ko">도대체 왜 그랬어?는 이유를 강하게 요구해요.</span>
<span class="ja">도대체 왜 그랬어?は理由を強く求めます。</span>

<!-- 묶으면: 인용한 말과 그것을 설명하는 말이 갈립니다 -->
<span class="ko">‘도대체 왜 그랬어?’는 이유를 강하게 요구해요.</span>
<span class="ja">「도대체 왜 그랬어?」は理由を強く求めます。</span>
```

**왜 이 두 짝인가.** 한국어 줄은 한국어 관례를 따르고, 일본어 줄은 일본어
관례를 따릅니다. 곧은 따옴표(`"` `'`)는 쓰지 않습니다 — 여는 것과 닫는 것이
같은 글자라 기계가 짝을 셀 수 없고, `runtime/js/script-lines.js` 가 인용
안쪽의 부호를 건너뛸 때 그 깊이를 셉니다.

**어디까지 묶는가.** 조사는 밖에 둡니다 — `‘어때?’만`, `‘뭐예요?’를` 이지
`‘어때?만’` 이 아닙니다. 인용한 것은 표현이고, 조사는 그 표현을 설명하는
문장의 일부입니다.

**한쪽만 묶지 않습니다.** 같은 표현을 `.ko` 에서 묶었으면 `.ja` 에서도 묶습니다.
두 줄은 같은 문장이므로 인용 자리도 같아야 합니다.

**문장을 통째로 인용하면 마침표는 닫는 따옴표 밖에 둡니다.**

```html
<!-- 어긋남: 한국어는 점이 안쪽, 일본어는 바깥쪽 → 끊기는 자리가 달라집니다 -->
<span class="ko">제가 소문 하나를 낼게요. ‘선생님이 안 쓴대요.’ 믿기세요?</span>
<span class="ja">うわさをひとつ流します。「先生は使わないそうです」。信じられますか？</span>

<!-- 맞음: 양쪽 다 바깥 -->
<span class="ko">제가 소문 하나를 낼게요. ‘선생님이 안 쓴대요’. 믿기세요?</span>
<span class="ja">うわさをひとつ流します。「先生は使わないそうです」。信じられますか？</span>
```

인용 안쪽의 부호는 문장을 끝내지 않으므로, 점을 안에 두면 그 뒤의 말까지
한 문장으로 붙습니다. 일본어는 `」。` 로 바깥에 두는 것이 관례라 이 자리에서
양쪽이 갈라집니다.

**부호로 끝나는 인용은 특히 그렇습니다.** `‘몇 살이에요?’를` 처럼 물음표가
표현 안에 있으면, 묶지 않았을 때 문장이 거기서 끝난 것처럼 읽힙니다.
`script-lines.js` 는 이제 조사가 붙은 부호를 문장 끝으로 세지 않지만, 그건
기계가 넘어가는 것일 뿐 **읽는 사람에게는 여전히 안 보입니다.**

---

## 3 · 활동 컴포넌트

### 읽기 (받아들이기)

```html
<div class="model-list">
  <div class="model-line"><span class="korean">저는 학생<span class="ending">이에요</span>.</span><span class="translation">私は学生<span class="ending">です</span>。</span></div>
</div>
```

### 패턴 카드 + 변형

```html
<div class="sent-hero">                       <!-- .topic 을 더하면 보라(은/는) 카드 -->
  <span class="korean">저는 다나카<span class="ending">예요</span>.</span>
  <span class="translation">私は田中<span class="ending">です</span>。</span>
</div>
<div class="sent-more">                       <!-- 카드 밑에 붙는 회색 트레이 -->
  <div><span class="korean">…</span><span class="translation">…</span></div>
</div>
```

### 고르기 (둘 중 하나)

```html
<div class="choose-list">
  <div class="choose-row sentence" data-sync-id="p1-choice-student" data-sync-kind="selection" data-sync-state="chosen">
    <span class="translation">私は学生です。</span>
    <span class="choose-sentence">저는 학생<span class="opt" data-sync-option="ieyo" data-correct>이에요.</span><span class="sep">/</span><span class="opt" data-sync-option="yeyo">예요.</span></span>
  </div>
</div>
```

정답은 오가지 않습니다 — 고른 쪽만 공유하고 `data-correct` 로 각자 채점합니다.
고른 것을 다시 누르면 아무것도 안 고른 상태로 돌아갑니다(맞혔든 틀렸든).
되돌리기는 곧 "빈 집합"이라 상대 화면에서도 같이 풀립니다.

### 빈칸 채우기 / 번역 / 자유 작문

```html
<div class="task-block">
  <div class="answer-box">                     <!-- .tall 이면 자유 작문 높이 -->
    <span class="answer-label">私は学生<span class="target ending">です</span>。</span>
    <span class="answer-fill"><span class="korean">저는 학생<input class="slot-input" type="text" data-sync-id="p1-fill-student" data-answer="이에요" autocomplete="off" spellcheck="false">.</span></span>
    <span class="hint"><span class="hint-chip">学生:학생</span></span>   <!-- 칸 안에 넣으면 아래 띠가 된다 -->
  </div>
</div>
```

- 입력 컨트롤은 HTML에 처음부터 실제 `<input>`·`<textarea>`로 적습니다. Lemonboard
  검증기는 스크립트를 실행하지 않으므로, `<span>` 껍데기를 로드 후 입력칸으로 바꾸면
  검증기와 수업 화면이 서로 다른 DOM을 보게 됩니다.
- `.slot-input`의 `data-answer`가 **정답**입니다. `data-sync-id`는 실제 입력칸에 둡니다.
- 빈칸이 **문장 한 토막**이어도(대화 채우기처럼 서술어 전체를 말하게 하는 자리) 그냥
  `.slot-input` 입니다. 크기를 지정하는 클래스는 없습니다 — 로드될 때 답을 실제로 그려 보고
  그 너비로 칸을 잡으므로, 앞말이 짧으면 한 줄에 들어가고 길면 알아서 아랫줄로
  넘어갑니다. 공유 런타임이 칸과 대화 턴을 현재 답 상자 너비 안에 제한하므로, 긴 답을
  억지로 짧게 쪼개거나 덱별 폭 스타일을 만들지 마세요. 넘어간 칸이 윗글에 붙어 보이지
  않도록 `.dialogue .answer-fill` 의 줄
  간격이 넉넉하게 잡혀 있으니, 여백을 따로 손대지 마세요.
- 문장 전체를 채점하는 칸은 `.answer-space.as-input` 안의
  `input.space-input[data-answer]`, 자유 작문칸은 같은 껍데기 안의
  `textarea.free-input`입니다. 자유 작문에는 `maxlength="2000"`을 둡니다.
- **머리띠(`.answer-label`)는 아래 한국어의 일본어 번역입니다.** 세 장만 지나면 학습자는
  이 자리를 그렇게 읽습니다. 번역할 것이 없어(아직 한국어가 없고 학습자가 지어냅니다)
  **할 일**을 적어야 하면 `.task` 를 답니다 — 「やること」 배지가 CSS 에서 붙고 글자 무게가
  한 단 내려갑니다. 띠 전체가 지시면 `<span class="answer-label task">`, 번역 뒤에 지시가
  덧붙는 형태면 번역은 그대로 두고 지시만 `<span class="task">` 로 감쌉니다.
  괄호로만 구분하지 마세요 — 괄호는 번역문 안에도 나옵니다.
- **힌트는 어휘만**(`JP:KO`), 조사나 어미는 넣지 않습니다. 그리고 **답 칸 안에** 둡니다.
- **힌트 칩은 그 빈칸의 답에 실제로 쓰이는 낱말만** 답니다. 화면에 이미 찍혀 있는 말
  (`네! 일본에 ▁?` 의 일본)은 힌트가 아니라 소음이고, 있어야 할 낱말을 밀어냅니다.
  자유 작문 칸은 답이 정해져 있지 않으므로, 고를 수 있는 어휘를 그대로 늘어놓습니다.

### 말한 문장 피드백

Core·Contextual의 `p1-write`·`p2-write`와 자유 대화 질문은 같은 피드백 활동을 씁니다.
튜터가 `학생 문장`에 들은 대로 적으면 `교정`이 같은 내용으로 따라 채워지고, 고친 자리만
diff로 남습니다. `＋ 교정`과 `＋ 노트`로 필요한 만큼 아래에 덧붙일 수 있습니다.

```html
<div class="fb-compose">
  <div class="fb" data-fb="p1-write-answer">
    <span class="fb-task">自分の状況で一文作ろう</span> <!-- 별도 발화 과제가 있을 때만 -->
    <span class="hint"><span class="hint-chip">座る:앉다</span></span>
  </div>
  <div class="fb-adds">
    <button class="fb-add" data-add="fix" type="button">＋ 교정</button>
    <button class="fb-add" data-add="note" type="button">＋ 노트</button>
  </div>
</div>
```

`.fb-task`와 `.hint`는 로드될 때 첫 피드백 카드의 머리와 바닥으로 들어갑니다. 뒤에 카드를
더 열어도 힌트는 첫 카드에만 남습니다. 한 페이지에 서로 다른 발화 과제가 여러 개라면
각 과제에 고유한 `data-fb`를 가진 `.fb-compose`를 하나씩 둡니다.

### 문장 만들기 (칩 배열)

```html
<div class="task-block">
  <div class="answer-box small">
    <span class="answer-label">私は日本人です。</span>
    <span class="answer-space build-zone" data-sync-id="p2-order-japanese" data-sync-kind="order" data-a="저는 일본 사람이에요"></span>
  </div>
  <span class="choice" data-item-id="japanese">일본 사람</span>
  <span class="choice" data-item-id="me">저는</span>
  <span class="choice" data-item-id="ieyo">이에요</span>
</div>
```

### 대화

```html
<div class="dialogue">
  <div class="turn other"><span class="who"><img class="avatar" src="…" alt=""><span class="who-name">ハナ</span></span>
    <div class="bubble"><span class="korean">…</span><span class="translation">…</span></div></div>
  <div class="turn me">… <div class="bubble me">…</div></div>
</div>
```

이야기 인물은 사진 아바타, 튜터/학생 연습은 기본 아이콘 아바타를 씁니다.
학생 말풍선(`.bubble.me`)은 초록 틴트만 받고 초록 테두리는 받지 않습니다.

말풍선이 **적는 칸**이면 `.bubble` 안에 `.answer-box` 하나만 넣습니다 — 말풍선 껍데기는
스스로 사라지고 답 상자가 곧 말풍선이 됩니다(상자 안에 상자를 만들지 마세요). 어느 쪽이든
쓸 수 있습니다: 학생 차례면 머리띠가 초록(`.bubble.me`), 튜터가 직접 답을 적는 자리면
회색입니다.

Contextual Korean의 `p3-freetalk` 은 반드시 네 차례로 닫습니다: **선생님 질문 → 학생 답변 →
학생 질문 → 선생님 답변**. 마지막은 설명 문구가 아니라 아래의 편집 가능한 튜터 칸입니다.

```html
<div class="turn other"><span class="who">…<span class="who-name">선생님</span></span>
  <div class="bubble"><div class="answer-box small">
    <span class="answer-label">先生の答え</span>
    <span class="answer-space as-input"><textarea class="free-input" data-sync-id="p3-freetalk-tutor-answer" rows="2" spellcheck="false" maxlength="2000"></textarea></span>
  </div></div></div>
```

### 설명용 도식

| 무엇 | 마크업 |
| --- | --- |
| 받침 규칙 | `.batchim` > `.bt-box` > `.bt-eq`(`.bt-syl` 또는 `.bt-syls` + `.bt-arrow` + `.bt-out`) + `.bt-head` + `.bt-ex` |
| 억양(끝 올리기/내리기) | `.pitch` > `.pi-card` > `.korean` + `.pi-curve`(SVG) + `.translation` |
| 한자 다리 | `.bridge` > `.br-row` > `.br-cn` + `.br-eq` + `.br-ko` |
| 바꿔 말하기(원어민 팁) | `.swap` > `.swap-row` > `.translation` + `.sw-from` + `.sw-to` |
| 상황별 뉘앙스(원어민 팁) | `.nuance-compare` > `.nuance-choice` ×2 + 가운데 `.nuance-or` |
| 오늘의 성과 | `.combi`(명사 은행 × 어미) + `.payoff`(큰 숫자) |

받침 도식을 어미(주황) 색으로 쓰려면 `.batchim.ending-rule` 을 씁니다.

**`.bt-syl` 은 정확히 한 음절만 받습니다.** 그 한 음절의 받침이나 모음이 분기의 시각적
근거일 때만 씁니다(`먹`, `하`, `들`). `계속하`, `말하`, `참다`처럼 여러 음절이나 사전형을
넣으면 고정된 한 음절 타일 안에서 글자가 줄바꿈되어 자리(seat)와 겹칩니다. 사전형·완전한
낱말·소리 분기를 보여 주지 않는 입력은 `.bt-word` 로 묶고, 소리 분기라면 전체 낱말은
`.bt-ex` 에 둔 채 결정하는 마지막 음절만 `.bt-syl` 에 둡니다.

**글자 도식에서 색이 앉는 자리는 규칙이 정해집니다.** `.bt-syl` 의 자리(seat)는 글자 뒤에
깔리는 것이지 글자를 칠하는 것이 아니고, 무엇으로 갈리는 규칙이냐에 따라 위치가 다릅니다.

| 규칙이 갈리는 것 | 클래스 | 자리 | 예 |
| --- | --- | --- | --- |
| 받침 | `.on` / `.off` | 바닥 | 먹 · 보 |
| 모음 (ㅏ ㅓ ㅣ …) | `.vowel` | 오른쪽 세로획 | 앉 · 먹 |
| 모음 (ㅗ ㅜ ㅡ ㅛ ㅠ) | `.vowel.under` | 가운데 가로띠 | 놀 |

글자를 그대로 두고 캡션에만 「ㅏ · ㅗ」라고 적으면, 정작 어디를 보라는 건지가 화면에
없습니다. 바닥 자리를 모음에 쓰지 마세요 — 같은 덱 앞쪽에서 이미 받침을 뜻합니다
(그리고 `.under` 를 쓰는 글자는 그 바닥에 자기 받침을 깔고 있습니다).

**규칙이 모음 두 개를 덮으면 둘 다 그립니다.** `.bt-eq` 안에 `.bt-syls` 로 어간 타일을
나란히 놓으면 화살표 하나가 둘을 동시에 받습니다 — 「ㅏ · ㅗ」인데 앉만 보이면 ㅗ 는
각주가 됩니다. **두 타일 사이에는 고르기 줄과 같은 `.sep`(`/`) 를 넣으세요** — 붙여 놓으면
한 낱말로 읽힙니다(앉 놀 → 앉놀). 타일은 두 장이 되면서 한 단 작아지고, 480px 아래에서
한 번 더 작아집니다.
가로 폭이 이 컴포넌트에서 가장 빠듯한 자리이니 예를 바꾸면 360px 폭에서 다시 재세요.
ㅗ 예는 축약되지 않는 어간으로 고릅니다 — 보다·오다는 봐도·와도가 되어 규칙을 깹니다.

**`.swap` 은 "같은 문장을 원어민은 이렇게 말한다"를 그립니다.** 위 줄(`.sw-from`)이 평범한
쪽, 아래 줄(`.sw-to`)이 학습자가 가져갈 쪽이고, 바뀐 조각만 `.ending`/`.topic` 으로
표시합니다. 화살표는 CSS 가 붙이므로 마크업에 적지 않습니다. 결과만 두 개 보여주고
설명은 글로 쓰는 카드(옛 `.card` + `.tip` + `.example-card`)로 돌아가지 마세요 — 상자가
세 겹이 되고, 정작 무엇이 바뀌었는지는 학습자가 되짚어야 합니다.

**`.nuance-compare` 는 발음 표기를 달 수 없습니다.** `.nuance-choice` 는 `> .korean` 과
`> .translation` 만 스타일이 있고, 시트에 기본 `.yomi` 규칙이 없어서 그 안에 넣은 `.yomi` 는
본문 크기 그대로 나옵니다. 이 컴포넌트는 발음 표기를 안 다는 트랙(3-contextual, 중급)에서
왔기 때문입니다. 초중급 덱에서 쓸 때는 두 카드에서 읽기를 빼고, 필요하면 튜터 대본 쪽에
넣으세요. 규칙은 런타임 큐에 있습니다.

둘 다 맞고 상황에 따라 고르는 표현은 `.swap` 이 아니라 `.nuance-compare` 를 씁니다.
각 `.nuance-choice` 의 `.nuance-when` 에 한국어 상황 이름과 일본어 설명을 함께 적고,
가운데 `.nuance-or` 는 `상황에 따라 <small>場面で選ぶ</small>` 로 둡니다. 두 카드의 시각적
무게는 같아야 하며 화살표를 넣지 않습니다. `.swap` 은 실제 한 방향 교정이나 명백한
바꿔 말하기일 때만 남겨 둡니다.

### 발음 표기 (`.yomi`)

**발음 표기는 초중급까지입니다.** 가나 읽기는 한글을 아직 못 읽는 사람을 위한 받침대라,
**왕초급 · 초급 · 초중급** 덱에만 답니다. **중급부터는 달지 않습니다** — 거기서부터 한글 읽기는
학습자가 이미 가진 기술이고, 덱이 대신 읽어 주면 그 연습을 빼앗습니다. 덱의 레벨은 파일 안
`<meta name="podo:level">` 에 적혀 있으니, 읽기를 달기 전에 그것부터 확인하세요
(레벨 표는 [`AGENTS.md`](./AGENTS.md) 에 있습니다).

레벨이 맞는 덱에서는 **학습자가 소리 내어 말하는 한국어** 밑에 가나 읽기를 답니다.
클래스 하나뿐이고, 자리는 그 한국어 **바로 뒤**입니다.

```html
<span class="korean">저는 학생<span class="ending">이에요</span>.</span>
<span class="yomi">チョヌン ハクセンイエヨ</span>
```

- 붙는 곳: `.model-line` · `.sent-hero`/`.sent-more` · `.bubble` · `.pi-card` ·
  `.bt-out`/`.bt-ex` · `.choice`/`.choose-word` · `.answer-fill` ·
  `.example-card` · `.combi` 타일 · `.brand-title`/`.transition-title`.
- **안 붙는 곳**: `.section-title`(옆의 `.title-ja` 가 이미 무슨 장인지 말한다),
  `.section-subtitle`(튜터가 읽는 줄), `.tutor-note`, `.slot-input`·`.space-input`·
  `.free-input`·`.build-zone`(정답 또는 입력 컨트롤).
- **둘 중 하나를 고르는 알약(`.opt`)에는 넣지 않습니다.** 거기 들어가는 것은 그 장이
  방금 가르친 패턴뿐이라(이에요/예요, 은/는) 고를 때쯤엔 도움이 아니라 2em 짜리
  과녁 안의 두 번째 줄이 되고, 네 줄이면 한눈에 보던 것이 문단이 됩니다. 옆의 **낱말**
  (`.choose-word`)은 그대로 답니다. 칩 배열(`.choice`)은 넓어서 둘 다 들어갑니다.
- 힌트 칩 안에서는 줄이 바뀌지 않고 뒤에 붙습니다 —
  `<span class="hint-chip">学生:학생<span class="yomi">ハクセン</span></span>`.
- 빈칸이 있는 문장은 보이는 부분만 읽고 빈칸은 `＿＿＿` 로 둡니다 —
  `チョヌン ハクセン ＿＿＿`.
- 표기는 **철자가 아니라 소리**입니다: 회사원이에요 → `フェサウォニエヨ`(연음),
  시작할게요 → `シジャカルケヨ`. 어절 사이는 반각 공백으로 띕니다.
- 스위치는 `runtime/js/yomi.js` 가 **읽기가 있는 페이지마다** 하나씩 놓습니다
  (마크업에 쓸 것은 없습니다 — `<script src>` 한 줄이면 됩니다). 이름은
  「よみがな」, 학습자의 말입니다: 페이저 안의 기호였을 때는 덱의 장치로 읽혀서
  자기가 끌 수 있는 줄 몰랐습니다.
- 자리는 **제목과 같은 줄**입니다. `.section-title` 을 `.page-head` 로 감싸고 그
  오른쪽 끝에 붙이므로, 제목이 길어지면 스위치 앞에서 줄이 바뀔 뿐 밑으로 파고들지
  않습니다(모서리에 띄우는 방식은 언젠가 긴 제목에 깔립니다). 맞출 제목이 없는
  표지·전환 페이지에서만 `.corner` 로 오른쪽 위 모서리에 띄웁니다.
- 상태는 `body.no-yomi` 하나라 한 장에서 끄면 전부 꺼지고, **티칭 모드와 달리
  공유합니다**(`data-sync-kind="yomi"`). 읽기를 끄는 것은 답을 여는 일이 아니라
  수업의 합의라서, 튜터가 껐는데 학습자 화면이 그대로면 그 말이 성립하지 않습니다.
- 채점은 `.yomi` 를 빼고 한국어만 봅니다(`activities.js` 의 `koText`). 새 활동을 만들 때
  칩·칸의 글자를 읽어야 하면 `textContent` 가 아니라 그 함수를 쓰세요.
- **읽기에 자리를 내주는 규칙은 반드시 `body:not(.no-yomi)` 로 묶습니다.** `:has()` 와
  `+` 는 구조를 보는 선택자라 스위치가 읽기를 숨겨도 계속 맞고, 그러면 카드가 바닥
  여백을 잃습니다(`.model-line`·`.bubble` 의 `padding-bottom: 0` 이 그랬습니다).
  끈 상태는 읽기를 넣기 전의 화면과 **픽셀 단위로 같아야** 합니다 — 두 상태를 모두
  렌더해서 확인하세요.

---

## 4 · 색과 간격

색은 **하나에 하나의 뜻**입니다. 새 뜻을 얹는 순간 페이지가 안 읽힙니다.

| 색 | 뜻 |
| --- | --- |
| `green-500` / `green-100` | 상태 — 고름·정답·활성 |
| `blue-100` | 튜터가 소리 내어 읽는 줄 |
| `blue-200` | 그 밑에 붙는 튜터 전용 메모 |
| `lime` | 브랜드 크롬(브랜드 페이지·페이저) — 상태로 쓰지 않는다 |
| `gray-200` | 보통의 테두리 |
| 점선 회색 | "여기에 쓴다" |
| 주황(`--ending-*`) / 보라(`--topic-*`) | 어미 / 조사 — 지금 가르치는 조각 |

간격은 토큰 하나가 정합니다: **`--item-gap`(16px)** — 한 활동 안에서 반복되는
항목 사이의 거리. 스크립트 상자와 활동 사이는 26px 로 모든 페이지가 같습니다.
새 컴포넌트의 CSS 는 `runtime/css/` 안에서 삽니다 — 덱 안에 `<style>` 을 두지 않습니다.
컴포넌트를 새로 만들 때 `gap` 을 직접 적지 말고 `var(--item-gap)` 을 쓰세요.

---

## 5 · 공유(레몬보드)

- **`data-sync-id` 가 있는 요소만 공유됩니다.** id 가 없으면 그 칸은 각자의 것입니다.
- 정답/오답은 절대 공유하지 않습니다 — 고른 값만 보내고 판정은 양쪽이 각자 합니다.
- 티칭 모드(답 보기)는 공유하지 않습니다.
- 자세한 계약은 [`interaction-protocol.md`](./interaction-protocol.md).

---

## 6 · 만든 뒤 확인

1. 브라우저 480px 폭에서 **전 페이지를 눈으로** 봅니다(시각 문서입니다).
2. 페이저 스크러버로 끝까지 넘겨 가로 넘침이 없는지 봅니다.
3. 티칭 모드(T)를 켜서 유령 답과 튜터 메모가 뜨는지 봅니다.
4. 레몬보드에 올릴 zip 은 이 레포에서 만들지 않습니다 — `podo-curriculum` 의
   `tools/build.py` 가 배포 파이프라인의 일부로 처리합니다(`docs/packaging.md`).
