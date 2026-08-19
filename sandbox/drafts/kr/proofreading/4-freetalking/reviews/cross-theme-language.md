# 프리토킹 전체 테마 언어 일관성 검수

## 범위와 현재성

현재 `lesson.html`을 원본으로 다시 대조하고, 현재 `lessons.jsonl`의 182개 레코드(91개 고급·중급 짝, 10개 테마)를 대상으로 교차 테마 검수를 했다. 오래된 패킷 문구는 근거로 사용하지 않았다.

`python3 korean/tools/build_proofreading_packets.py korean/tracks/4-freetalking --check` 결과는 `✓ 182 decks · 10 packets are current`였다. 따라서 아래 수량과 문구는 현재 HTML과 일치한다.

검수 항목은 다음과 같다.

- 한국어·일본어에서 반복되는 역할명과 핵심 용어
- HTML의 한·영·일 제목, 계획 제목, 문서 `<title>`, 고급·중급 짝 제목
- 테마를 가로지르는 정확히 같은 질문·모델 문장
- 글자 3-gram과 문자열 유사도로 추린 근접 질문·모델 문장의 실제 의도와 대화 흐름

## 수량 검증과 메타데이터 결과

| 항목 | 결과 |
|---|---:|
| 현재 덱 | 182 |
| 고급·중급 짝 | 91 |
| 테마 | 10 |
| 계획 제목과 `podo:title-ko` 불일치 | 0 |
| 문서 `<title>`과 `podo:title-ko` 불일치 | 0 |
| 고급·중급 짝의 한·영·일 제목 불일치 | 0 |
| 서로 다른 테마 사이의 한·영·일 제목 충돌 | 0 |
| 서로 다른 테마 사이의 동일한 한국어 모델 본문 문장 | 0 |
| 서로 다른 테마 사이의 동일한 한국어 메인 질문 문자열 | 1 |

여기서 ‘메인 질문 문자열’은 `warm-1`, `warm-2`, `q1`~`q6`의 `question.ko`를 뜻한다. 한 문자열이 고급·중급 두 짝에 각각 들어 있어 실제 HTML 위치는 네 곳이다.

## 남은 고신뢰 결함

없음.

현재 자료에서 의미를 잘못 전달하거나 제목·메타데이터를 실제 덱과 다르게 식별하는 고신뢰 결함, 또는 다른 테마의 질문·모델 이야기를 실질적으로 복제한 고신뢰 결함은 발견하지 못했다. 따라서 이 검수에서 즉시 적용할 `source` / `pageId` / `field` / `current` / `suggested` 항목은 없다.

## 확인했지만 허용 가능한 반복

### 음악 주제의 동일한 몸풀기 질문

다음 네 위치의 질문과 일본어 지원이 정확히 같다.

- `korean/tracks/4-freetalking/courses/talk-me-lately-advanced/lessons/10-on-repeat/lesson.html` · `warm-1` · `question.ko`: `요즘 가장 자주 듣는 노래가 뭐예요?`
- `korean/tracks/4-freetalking/courses/talk-me-lately-intermediate/lessons/10-on-repeat/lesson.html` · `warm-1` · `question.ko`: `요즘 가장 자주 듣는 노래가 뭐예요?`
- `korean/tracks/4-freetalking/courses/talk-things-i-like-advanced/lessons/03-my-playlist/lesson.html` · `warm-2` · `question.ko`: `요즘 가장 자주 듣는 노래가 뭐예요?`
- `korean/tracks/4-freetalking/courses/talk-things-i-like-intermediate/lessons/03-my-playlist/lesson.html` · `warm-2` · `question.ko`: `요즘 가장 자주 듣는 노래가 뭐예요?`
- 네 위치의 `question.ja`: `最近いちばんよく聴く曲は何ですか？`

이 반복은 허용 가능하다. 두 질문 모두 음악 주제의 짧은 몸풀기이고, 이어지는 대화의 핵심은 다르다. `10-on-repeat`의 `q1`은 `그 노래를 계속 반복해서 듣게 되는 이유가 뭐예요?`, `03-my-playlist`의 `q1`은 `어떤 상황에서 어떤 노래를 들어요?`여서 각각 한 곡에 얽힌 이유와 상황별 선곡으로 갈라진다. 모델 본문에도 같은 문장은 없다.

### 공통 진행 문구

`제가 먼저 제 이야기를 해 볼게요. 잘 듣고, 궁금한 게 있으면 물어보세요.` 같은 source 도입문과 30초 진행 지침은 여러 테마에 반복되지만, 이는 모델 이야기의 내용이 아니라 의도된 수업 진행 계약이다. 실제 5줄 모델 본문에서는 교차 테마 정확 일치가 0개였고, 높은 유사도의 근접 일치도 발견되지 않았다.

## 불확실하거나 편집 판단이 필요한 항목

### 집 규칙과 어린 시절 잔소리의 비슷한 진입 질문

- `korean/tracks/4-freetalking/courses/talk-small-things-advanced/lessons/09-house-rule/lesson.html` · `warm-1` · `question.ko`: `어릴 때 집에서 자주 들은 말이 뭐예요?`
- 같은 중급 짝의 동일 위치와 문구
- `korean/tracks/4-freetalking/courses/talk-what-came-before-advanced/lessons/01-childhood-nagging/lesson.html` · `warm-1` · `question.ko`: `어릴 때 집에서 가장 자주 들은 말이 뭐예요?`
- 같은 중급 짝의 동일 위치와 문구

문장 유사도가 높아 같은 학습자가 두 수업을 들으면 비슷한 첫 답을 할 수 있다. 다만 이어지는 `q1`은 각각 `다른 집에는 없었던 우리 집만의 규칙은 뭐예요?`와 `어릴 때 제일 많이 들은 잔소리는 뭐였어요?`로 갈라지고, 전자는 집의 운영 규칙, 후자는 과거에 들은 말과 현재의 해석을 다룬다. 하나의 몸풀기만으로 고신뢰 중복 결함이라고 보기는 어렵다. 반복감을 더 줄이려는 편집 방향이 있을 때만 `house-rule`의 몸풀기를 현재 생활 장면 쪽으로 옮길 수 있다.

### 내부 역할명 `학생`·`학습자`·`튜터`

현재 투영의 한국어 텍스트에서 `학생`은 330회로 10개 테마에 나오고, `학습자`는 13회(주로 테마 1의 튜터 지침과 테마 7 모델 이야기), `튜터`는 16회(테마 1)에 나온다. 예를 들면 다음과 같다.

- `korean/tracks/4-freetalking/courses/talk-between-two-countries-advanced/lessons/01-what-surprised-me/lesson.html` · `q3` · `tutorGuidance.ko`: `학습자는 일본에서 직접 겪은 장면을 설명하고, 튜터는 비슷한 한국 장면을 하나 보태 주세요.`
- 같은 덱 · `model-story` · `source.tutorGuidance.ko`: `30초 안에 자연스럽게 들려주세요. 같은 길이의 실제 경험으로 바꿔도 되고, 학생이 바로 말하기 시작하면 줄여도 됩니다.`

세 단어의 지시 대상은 문맥에서 명확하고, `학습자`가 모델 이야기 속 직업상 고객을 가리키는 경우도 있어 일괄 치환하면 오히려 뜻을 바꿀 수 있다. 제품 전체의 내부 문체표에서 역할명을 하나로 정한 경우에만 위치별로 검토할 편집 항목이다.

### `이직` 제목과 넓어진 수업 범위

고급·중급 두 덱 모두 다음 제목을 쓴다.

- source: `korean/tracks/4-freetalking/courses/talk-work-and-money-advanced/lessons/08-why-i-wanted-a-change/lesson.html` 및 중급 짝
- `metadata` · `title.ko`: `이직을 고민하는 이유`
- `metadata` · `title.en`: `Why I wanted a change`
- `metadata` · `title.ja`: `仕事や勉強を変えたかった理由`

한국어 제목은 이직으로 좁고 일본어 제목과 실제 `lesson-goal`은 일·공부·생활 역할의 변화까지 넓다. 직장 경험이 없는 학습자도 답하게 하려는 의도와 계획 제목을 유지하려는 의도가 함께 보여, 단순 번역 오류로 확정하지 않았다. 제목 범위를 세 언어에서 완전히 맞출지는 기획·편집 판단이다.

### 일본어 제목 `人生映画`와 `人生の一冊`

- `korean/tracks/4-freetalking/courses/talk-things-i-like-advanced/lessons/01-life-changing-movie/lesson.html` 및 중급 짝 · `metadata` · `title.ja`: `人生映画`
- `korean/tracks/4-freetalking/courses/talk-things-i-like-advanced/lessons/08-life-changing-book/lesson.html` 및 중급 짝 · `metadata` · `title.ja`: `人生の一冊`

한국어 제목은 각각 `인생 영화`, `인생 책`이고 영어도 `My all-time movie`, `My all-time book`으로 짝을 이룬다. 일본어에서는 영화 쪽만 한국어식 합성어에 가깝고 책 쪽은 관용적인 표현이다. `人生の一本` 등으로 맞추면 자연스러울 수 있지만, 정확한 제품 어조와 학습자 투명성 중 무엇을 우선할지에 따라 선택이 달라져 고신뢰 수정으로 올리지 않았다.

## 핵심 용어 판정

- `AI`는 테마 7·9·10에서 한국어와 일본어 모두 `AI`로 유지된다. 현재 투영에 `인공지능`·`人工知能` 변형은 0개다.
- `SNS`는 테마 10에서 한국어와 일본어 모두 `SNS`로 유지된다. `소셜 미디어`·`ソーシャルメディア` 변형은 0개다.
- 반복되는 한국어 어휘의 일본어 gloss 차이는 대부분 `생각하다`의 `思う`/`考える`, `편하다`의 `楽だ`/`便利だ`처럼 실제 문장 문맥에 따른 의미 차이였다. 같은 용어를 잘못 옮긴 고신뢰 사례로 판정할 것은 없었다.

## 최종 판정

현재 182개 프리토킹 덱은 제목·메타데이터와 핵심 한·일 용어가 전체적으로 일관된다. 정확히 같은 교차 테마 질문은 음악 몸풀기 한 문장뿐이며 대화의 핵심 흐름은 분리되어 있고, 모델 본문 문장 복제는 없다. 남은 항목은 역할명 문체 통일, 비슷한 몸풀기 한 쌍, 일부 제목의 범위·어조처럼 제품 편집 기준이 있어야 결정할 수 있는 사항이다. 즉시 수정해야 할 고신뢰 결함은 없다.
