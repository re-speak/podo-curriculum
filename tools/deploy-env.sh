#!/usr/bin/env bash
#
# 한 환경에 적용한다. .cloudbuild/podo-curriculum-deploy.yml 의 apply-{dev,qa,stage,prod}
# 스텝 넷이 이 스크립트 하나를 공유한다.
#
# 왜 스텝이 넷인가: Cloud Build 의 스텝은 정적으로 선언돼야 하는데(콤마 목록으로 스텝을
# 만들어 낼 수 없다) 병렬로 돌리려면 스텝이 갈려 있어야 한다. 그래서 네 환경을 모두 선언해
# 두고, 이번 배포 대상이 아닌 스텝은 여기서 즉시 빠져나온다. 빈 스텝 하나는 몇 초고,
# 그 대가로 환경마다 로그와 소요 시간이 따로 남는다 — 어디서 느려졌는지 빌드 화면에서
# 그대로 보인다.
#
#   bash tools/deploy-env.sh <env> "<_DEPLOY_ENV 값>" [jobs]
#
set -eu

ENV_NAME="${1:?환경 이름이 필요하다 (dev|qa|stage|prod)}"
TARGETS="${2:?배포 대상 목록이 필요하다 (_DEPLOY_ENV 값 그대로)}"
JOBS="${3:-4}"

# 값 형식은 _DEPLOY_ENV 와 같다(콤마 구분). 목록으로 다루려고 공백으로 바꾼다.
TARGETS=" $(echo "$TARGETS" | tr ',' ' ') "

case "$TARGETS" in
  *" $ENV_NAME "*) ;;
  *) echo "$ENV_NAME 은 이번 배포 대상이 아니다 — 건너뛴다"; exit 0 ;;
esac

echo "══════════ $ENV_NAME ══════════"

# cloud-sdk:slim 의 python 은 PEP 668(externally-managed) 이라 시스템 설치를 막는다.
# 빌드 컨테이너는 일회용이라 venv 를 만들 이유가 없으므로 그 보호를 끈다.
pip install --break-system-packages --quiet -r tools/requirements.txt

# 인증은 Google OIDC ID 토큰이다. 저장하고 회전시킬 자격증명이 없다 — 메타데이터
# 서버에서 이 빌드 SA 의 토큰을 그때그때 받아 붙이고, grape 가 구글 공개키로 서명을
# 검증한다(수명 1시간). audience 는 호출할 바로 그 URL 이어야 한다 — 다른 서비스용으로
# 발급된 토큰의 재사용을 막는 장치라, curriculum.yaml 의 grapeSyncApi 와 정확히 같아야 한다.
SYNC_URL="$(python3 - "$ENV_NAME" <<'PY'
import sys, yaml
env = sys.argv[1]
print(yaml.safe_load(open('curriculum.yaml'))['spec']['environments'][env]['grapeSyncApi'])
PY
)"
echo "sync 대상: $SYNC_URL"

PODO_CURRICULUM_SYNC_TOKEN="$(curl -sf -H 'Metadata-Flavor: Google' \
  "http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=$SYNC_URL" || true)"
export PODO_CURRICULUM_SYNC_TOKEN

if [ -z "$PODO_CURRICULUM_SYNC_TOKEN" ]; then
  echo "OIDC 토큰을 받지 못했다 — 메타데이터 서버 접근 실패."
  # 여기서 성공으로 끝내면 아무것도 배포하지 않은 채 빌드가 초록으로 남는다. 그러면
  # main 은 새 덱을, 학습자는 옛 덱을 보는 상태가 되고 그걸 알려 줄 신호가 없다.
  # 배포 파이프라인의 초록은 "main 이 실제로 반영됐다"는 뜻이어야 한다.
  exit 1
fi

python3 tools/apply.py --env "$ENV_NAME" --jobs "$JOBS"
