# 공개 카탈로그의 커스텀 도메인

`tools/build-catalog.py` 가 만드는 공개 카탈로그를
`curriculum.podospeaking.com` 에서 서빙하기 위한 절차.

**지금 상태: 켜져 있다 (2026-08-21).** 사이트는
`https://curriculum.podospeaking.com/` 에서 돈다. 경로는 도메인이 붙든 안 붙든
같다 — `/korean-jp`, `/english-jp`.

남은 것은 **Enforce HTTPS** 하나다(아래 3번). 인증서는 이미 발급되어 https 가 200 을
주지만 강제가 꺼져 있어, http 로 온 요청은 http 로 서빙된다.

## CNAME 이 두 개다 — 이게 헷갈리는 지점

이름이 같지만 서로 다른 물건이고, **순서가 있다.**

| | 무엇 | 어디 | 누가 |
|---|---|---|---|
| **CNAME 파일** | "이 사이트를 이 도메인에서 서빙해 달라" 는 GitHub 에 대한 선언 | `gh-pages` 브랜치 뿌리 | `build-catalog.py` 가 쓴다 |
| **CNAME DNS 레코드** | 실제로 트래픽을 GitHub 으로 보내는 것 | Google Cloud DNS 의 `podospeaking.com` 존 | 사람이 넣는다 |

**DNS 레코드가 먼저다.** 순서를 뒤집으면 사이트가 죽는다 — 아래 참고.

## 켜는 순서

### 1. DNS 레코드를 넣는다 (사람) — 완료 2026-08-21

`podospeaking.com` 존은 Google Cloud DNS 에 있다
(`dig +short podospeaking.com NS` → `ns-cloud-b{1..4}.googledomains.com`).

```
Name:  curriculum
Type:  CNAME
TTL:   300
Data:  re-speak.github.io.        ← 끝의 점까지
```

넣은 뒤 **권한 네임서버에 직접** 물어 확인한다 (공개 리졸버는 없다는 답을 캐시하고 있을 수 있다):

```sh
dig +noall +answer @ns-cloud-b1.googledomains.com curriculum.podospeaking.com CNAME
```

답이 나오면 다음 단계로 간다. **답이 없으면 여기서 멈춘다.**

### 2. `CUSTOM_DOMAIN` 을 채우고 릴리스한다 — 완료 2026-08-21

`tools/build-catalog.py`:

```python
CUSTOM_DOMAIN = "curriculum.podospeaking.com"      # None 에서 바꾼다
```

그리고 평소의 두 단계 — `stage` 로 PR·머지, 그다음 `stage → main` 릴리스 PR·머지.
prod 배포의 `catalog` 스텝이 `gh-pages` 에 `CNAME` 을 쓰고, GitHub 이 그것을 읽어
저장소 설정의 커스텀 도메인을 켠다.

`gh-pages` 는 배포마다 통째로 force-push 되므로 `CNAME` 은 **매번 다시 쓰여야 한다.**
그래서 저장소 설정에만 손으로 넣어 두는 것으로는 부족하다 — 다음 배포가 지운다.

2026-08-21 에는 순서가 이랬다: DNS 가 풀린 것을 확인하고 **Settings → Pages 에 직접
도메인을 넣어** 즉시 켠 다음, 같은 릴리스에 `CUSTOM_DOMAIN` 을 담았다. 설정창으로 켜면
GitHub 이 `gh-pages` 에 `CNAME` 을 대신 커밋해 주어 그 자리에서 살아나지만, 그 커밋은
다음 prod 배포의 force-push 가 지운다. 설정창은 빠른 길일 뿐이고, 도메인을 계속 붙들고
있는 것은 `CUSTOM_DOMAIN` 이다.

### 3. HTTPS 를 켠다 (사람) — 남음

Settings → Pages 에서 DNS check 가 초록이 되면 **Enforce HTTPS** 를 체크한다.
DNS 가 확인되기 전에는 이 항목이 비활성이다.

```sh
gh api repos/re-speak/podo-curriculum/pages --jq '{cname,html_url,https_enforced}'
```

## 순서를 뒤집으면 무슨 일이 생기나

**2026-08-20 에 실제로 겪은 일이다.** DNS 없이 `CNAME` 파일을 먼저 올렸더니:

1. GitHub 이 `CNAME` 을 읽고 커스텀 도메인을 켰다
2. Pages 가 `re-speak.github.io/podo-curriculum/*` 를 전부
   `http://curriculum.podospeaking.com/*` 로 **301** 시키기 시작했다
3. 그 도메인은 풀리지 않는다 → **두 주소가 함께 막혔다**

DNS 를 기다리는 동안 사이트가 꺼진 것이 아니라, **CNAME 파일이 사이트를 껐다.**
Settings → Pages 는 그동안 "Your site is live at http://curriculum.podospeaking.com/"
이라고 표시한다 — 그건 CNAME 파일을 되읽어 준 것뿐이고, 그 아래 노란 상자
(`DNS check unsuccessful` / `InvalidDNSError`) 가 사실이다.

그래서 `CUSTOM_DOMAIN` 은 기본값이 `None` 이고, 값이 있을 때만 `CNAME` 을 쓴다.

## 망가졌을 때 되돌리는 법

증상: `re-speak.github.io/podo-curriculum/` 가 풀리지 않는 도메인으로 301 된다.

```sh
# 1. 즉시 복구 — 저장소 설정에서 도메인을 뗀다 (배포를 기다리지 않는다)
gh api --method PUT repos/re-speak/podo-curriculum/pages -f cname=

# 2. 확인
curl -s -o /dev/null -w '%{http_code}\n' https://re-speak.github.io/podo-curriculum/

# 3. 1번만으로는 다음 배포가 되돌린다. CUSTOM_DOMAIN 을 None 으로 되돌려 릴리스한다.
```

## URL 지도

| 경로 | 내용 |
|---|---|
| `/` | 언어 고르기 |
| `/korean-jp` | 한국어 트랙 카드 |
| `/korean-jp/catalog/<track>` | 그 트랙의 목차 (코스 = 단원) |
| `/english-jp` | 영어 트랙 카드 |
| `/{lang}/view/<course>/<lesson>/<slot>` | 덱 뷰어 |

링크에는 확장자가 없다. 파일은 `.html` 이고, GitHub Pages 가 확장자 없는 경로에
`.html` 을 붙여 찾아 준다. **로컬에서 확인할 때 `python3 -m http.server` 는 그렇게 하지
않는다** — 그래서 실제 서빙과 달라 보인다. Pages 규칙을 흉내 내려면 디렉터리 index 와
확장자 보정을 하는 핸들러로 띄워야 한다.

디렉터리 이름의 `-jp` 는 시장이다. 지금 모든 코스가 `countryCode: JP` 라서 그렇고,
다른 시장이 생기면 `korean-en` 을 옆에 세우면 된다. 이름은 `build-catalog.py` 의
`LANGUAGES[*]["dir"]` 이 원본이다.
