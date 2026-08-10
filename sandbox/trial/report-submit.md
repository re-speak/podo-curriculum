# 체험 리포트 저장 — 보내는 값의 규격

`shared/js/report-submit.js` 가 「리포트 저장」 버튼에서 내보내는 값과, 그것이
`le_level_test` 의 어느 칸으로 가는지를 적는다. 규격을 고칠 때 함께 고쳐야 하는
곳이 세 레포에 흩어져 있어서 — 덱(여기), 보드(lemonboard), 앱(podo-app) —
어느 하나만 바뀌면 버튼이 조용히 아무 일도 하지 않는다.

## 왜 덱이 백엔드를 직접 부르지 않는가

두 가지를 덱이 모르기 때문이다.

- **인증.** 덱에는 로그인 세션이 없다. 토큰은 앱의 httpOnly 쿠키에 있어서
  스크립트가 읽지 못한다.
- **누구의 리포트인가.** 덱은 어느 수업에나 그대로 실리는 문서라 학생·수업이
  누구인지 모른다.

그래서 **보내는 값에 식별자를 담지 않는다.** 덱이 아는 척 실어 보내면 앱은 그
값을 믿을지 말지를 정해야 하고, 믿는 순간 남의 리포트에 붙일 길이 열린다.
덱은 리포트만 보내고, 누구의 것인지는 앱이 자기가 아는 수업에서 채운다.

## 경로

```
HTML 덱  ──postMessage──▶  보드(lemonboard)  ──postMessage──▶  앱(podo-web / tutor-web)
                                                                      │
                                                          server action (httpOnly 쿠키)
                                                                      ▼
                                                                podo-backend
                                                                      ▼
                                                                le_level_test
```

덱은 보드 안에 `srcDoc` 으로 실리므로 덱의 부모는 언제나 보드다. 앱은 그보다 한
단 위에 있어서 보드가 중계한다.

`srcDoc` 문서에는 자기 주소가 없다(`about:srcdoc`). `location.search` 가 비어
있어 **URL 로는 아무것도 받을 수 없고**, 덱에 무언가를 넘기는 창구는 보드가
주입하는 `window.PODO_REPORT_CONTEXT` 하나뿐이다.

> **보드가 `parentOrigin` 을 주입하지 않으면 덱은 아무것도 보내지 않는다.**
> `srcDoc` 문서의 `location.origin` 은 `"null"` 이라 폴백이 되지 못한다 —
> 하네스로 실측한 결과이고, 주입 없이 저장을 누르면 버튼은
> 「저장은 수업방 안에서만 돼요」 에서 멈춘다. 보드 구현에서 가장 빠뜨리기 쉬운
> 한 줄이다.

## 덱 → 부모

```js
{
  source: "podo-trial-report",
  type: "submit",
  requestId: "rep-<base36>-<rand>",   // 응답을 짝지을 id
  payload: { ... }                     // 아래 표
}
```

`targetOrigin` 은 `PODO_REPORT_CONTEXT.parentOrigin` → `location.origin` 순으로
정한다. **`"*"` 로는 보내지 않는다** — 리포트에는 학생이 상담에서 한 이야기가
들어 있어서, 받는 창을 특정하지 못하면 보내지 않는 편이 맞다.

### payload

| 키               | 값                                         |
| ---------------- | ------------------------------------------ |
| `source`         | `"korean-trial-report"`                    |
| `reportVersion`  | `2`                                        |
| `levelTest`      | `le_level_test` 의 평면 칸 (아래)          |
| `reportSnapshot` | `window.podoReport.snapshot()` 결과 그대로 |

`levelTest` → `le_level_test` 컬럼 대응:

| payload          | 컬럼              | 비고                                                                                                           |
| ---------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `language`       | `language`        | 이 덱은 항상 `"KO"`                                                                                            |
| `level`          | `level`           | 튜터가 고른 종합 레벨                                                                                          |
| `levelName`      | `level_name`      | 레벨표가 `report.js` 클로저 안에 있어 백엔드가 스스로 채울 수 없다. 어드민 목록이 읽는 칸이라 비워 두지 않는다 |
| `reason`         | `reason`          | 학습 동기(복수 선택)                                                                                           |
| `listening`      | `listening`       |                                                                                                                |
| `fluency`        | `fluency`         |                                                                                                                |
| `pronunciation`  | `pronunciation`   |                                                                                                                |
| `reportSnapshot` | `report_snapshot` |                                                                                                                |
| `reportVersion`  | `report_version`  |                                                                                                                |

**앱이 채우는 칸** — `student_id`, `class_id`, `student_name`. 덱은 보내지 않는다.

**아무도 채우지 않는 칸** — `job`, `study_method`, `url`. 이 덱에는 대응하는
입력이 없다. 덱이 `null` 로라도 넣어 두면 받는 쪽에서 "덱이 보낸 빈 값"과 "덱이
모르는 값"이 구별되지 않으므로, 키 자체를 넣지 않는다.

### reportSnapshot

`report.js` 의 `snapshot()` 이 짓는다. 담는 것은 **입력뿐이다** — 리포트가
학생에게 보여 주는 것(레벨 문안·항목 문장·코멘트·기간·코스 순서)은 거의 전부
그 입력에서 계산해 낸 것이고, 앱에서 리포트를 다시 열 때도 같은 `report.js` 가
같은 계산을 한다. 결과까지 저장하면 같은 값이 두 곳에 살게 되고, 둘이 어긋나는
날 어느 쪽이 맞는지 아무도 모른다.

```js
{
  kind: "podo-korean-trial-report",
  schemaVersion: 1,
  capturedAt: "<ISO8601>",
  deck: { lessonId, contentVersion },   // 어느 판으로 그린 것인가
  answers:    { why: [], goal, pace },  // 학습자가 고른 것
  assessment: { level, areas: {...} },  // 튜터가 판정한 것
  plan:       { perWeek }               // 상담에서 합의한 페이스
}
```

`deck.contentVersion` 을 함께 남기는 이유: 계산의 재료(레벨표·문안)는 고쳐지는
것이라, 나중에 다시 그린 리포트가 그날 학생이 본 것과 다를 수 있다. 어느 판으로
그린 것인지는 알 수 있어야 한다.

## 부모 → 덱

```js
{
  source: "podo-trial-report",
  type: "result",
  requestId: "<보낸 것과 같은 id>",
  ok: true | false,
  error: "<사람이 읽을 한 줄>"   // ok:false 일 때만
}
```

덱은 **보낸 곳에서 온 답**(`event.origin === targetOrigin`)이고 **지금 기다리는
요청의 id** 와 맞을 때만 화면을 바꾼다. 한 번 실패하고 다시 누르는 흐름이
흔해서, 늦게 온 답이 그다음 요청의 결과로 읽히면 안 된다.

답이 15초 안에 오지 않으면 실패로 처리하고 버튼을 되살린다. 이 계약을 모르는
옛 보드에서도 버튼이 「보내는 중」 에 멈춰 있지 않게 하기 위한 것이다 — 튜터는
상담을 끝내는 중이라 기다릴 시간이 없고, 다시 누르는 편이 낫다.

## 저장 전 검증

`window.podoReport.missing()` 이 빈 배열일 때만 버튼이 눌린다. 반쯤 빈 리포트가
저장되는 것이 가장 나쁜 결과라서다 — 되살릴 때 무엇이 비었는지 알 수 없다.

## 저장 버튼이 뜨는 조건

`.rep-send` 는 **teaching 모드에서만** 보인다(`pager.js` 의 `T` 버튼이
`body.teaching` 을 토글한다). 앱이 role 을 주입하지 않으므로 **학습자도 `T` 를
누르면 이 블록이 보인다.** 저장이 튜터의 일이라는 것은 화면이 아니라 **서버의
권한 검증으로 보장해야 한다.**
