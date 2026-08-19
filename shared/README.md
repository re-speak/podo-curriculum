# shared — 덱이 불러 쓰는 것 전부

이 폴더에 있는 것이 **레슨 덱이 실행할 때 불러오는 파일의 전부**입니다. 나머지
(마크업·문서·패키저·참고 자료)는 이 폴더 밖에 있고, 덱은 그것들 없이도 돌아갑니다.

```
shared/
  css/   lesson-card.css   디자인 시스템 — 모든 트랙이 쓴다
         trial.css         체험 레슨 트랙의 시트 (lesson-card.css 다음에 로드)
  js/    activities.js     정적 입력칸·고르기·문장 만들기 + lessonSync 스텁
         feedback.js       말한 문장·교정·diff·추가 노트 (Core·Contextual·자유 대화 공통)
         pager.js          페이지 넘김·스크러버·티칭 모드
         hangul-activities.js / freetalk-activities.js / report.js / report-consult.js
                           과 성격별 활동
         report-submit.js  리포트를 백엔드에 남기는 버튼 (report.js 뒤에 로드)
         highlight.js · spotlight.js · stamp.js · tutor-notes.js · script-lines.js
                           모든 덱이 공통으로 얹는 것들
```

## 왜 한 폴더인가

**이 폴더는 저장소 루트에 있습니다 — 어느 언어 폴더에도 속하지 않습니다.** 한국어와
영어 커리큘럼이 같은 런타임을 쓰기 때문입니다. `korean/trial/assets/` 는 옮기지
않았으므로 여전히 한국어 폴더 안에 있고, 덱에서 두 경로의 `../` 개수가 하나 다릅니다.

**배포 저장소와 CDN으로 미러링할 대상이 정확히 이 폴더입니다.** 여기서는 덱이 상대
경로로 부르고(`../../../shared/js/pager.js`), `podo-curriculum`의
`sync-from-authoring.py --runtime-only`가 이 폴더를 `shared/{css,js}`로 그대로
옮깁니다. 그 사본을 `publish-shared.py`가 불변 태그로 공개 미러에 게시하고,
`repoint-shared.py`가 배포 덱을 그 태그로 가리킵니다.

공개해도 되는 것만 둡니다 — 여기 있는 파일에는 교재 스캔도, 가격도, 내부 메모도
없습니다. 그런 것이 이 폴더에 들어가려 하면 그건 런타임이 아닙니다.

## 배포할 때

1. 이 저장소에서 런타임을 수정·검증하고 먼저 커밋합니다.
2. `podo-curriculum`의 stage 기반 브랜치에서 `sync-from-authoring.py --runtime-only`를
   실행해 `shared/`가 이 폴더와 같은지 확인합니다.
3. `curriculum.yaml`의 `spec.sharedRuntime.version`을 올린 뒤
   `publish-shared.py`를 먼저 실행합니다. 태그는 불변이라 이미 게시한 버전을
   덮어쓰지 않습니다.
4. `repoint-shared.py`로 덱을 새 태그에 고정하고 stage 검증·배포 뒤 production으로
   승격합니다. 배포 중인 덱은 명시적으로 repoint하기 전까지 이전 태그를 계속 씁니다.

## 규칙

- **덱은 인라인 CSS·JS 를 갖지 않습니다.** 새로 필요한 것이 생기면 여기에
  넣고 공유합니다. 한 덱에만 둔 수정은 그 덱에만 남습니다 — 스크러버와
  스크롤바 자리가 실제로 그렇게 한 덱에만 있었습니다.
- **공유 토큰을 먼저 씁니다.** 색·간격·테두리처럼 `lesson-card.css`의 `:root`에
  이미 의미 토큰이 있으면 그 변수를 쓰고 값을 다시 적지 않습니다. 덱이나 트랙에
  로컬 변수를 만들거나, 리터럴 하나를 감추기 위한 일회성 변수를 만들지 않습니다.
  여러 컴포넌트에서 반복되는 새 의미 역할이 생겼을 때만 `:root` 토큰을 추가하고
  그 역할의 모든 사용처를 함께 옮깁니다.
- **입력 컨트롤은 HTML에 정적으로 존재합니다.** `activities.js`는
  `input.slot-input`, `input.space-input`, `textarea.free-input`, `.build-zone`을
  새로 만들거나 다른 태그로 바꾸지 않고 동작만 연결합니다. Lemonboard의 정적
  검증기와 수업 중 라이브 바인더가 같은 DOM을 보게 하는 계약입니다.
- **로드 순서가 있습니다.** `activities` → `feedback`(쓰는 덱만) → `pager` → `script-lines` →
  `spotlight` → `tutor-notes` → `highlight` → `stamp`. 이유는 각 파일 머리말에
  적혀 있고, 덱 뼈대는 [`AUTHORING.md`](../korean/AUTHORING.md) 에 있습니다.
- **생성되는 튜터 UI는 목표 언어 메타를 읽습니다.** 영어 덱은
  `<meta name="podo:target-language" content="en">`을 선언하고, `feedback.js`,
  `tutor-notes.js`, `stamp.js`, `trial.css`가 영어 튜터 문구를 선택합니다. 메타가 없거나
  다른 값이면 기존 한국어 문구가 기본값입니다. `<html lang="ja">`는 학습자 지원 언어라
  이 분기에 사용하지 않습니다.
- **CSS 는 두 장이 한 벌입니다.** `lesson-card.css` 다음에 트랙 시트. 패키저가
  링크 순서대로 이어 붙이므로 순서가 곧 캐스케이드입니다.
