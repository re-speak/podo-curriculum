#!/usr/bin/env bash
#
# 브랜치 보호를 건다. **조직 admin 권한이 있는 계정으로 한 번만 실행하면 된다.**
#
# 왜 스크립트인가: 이 저장소는 머지가 곧 배포다. stage 에 머지하면 stage·qa·dev 에,
# main 에 머지하면 프로덕션에 그대로 적용된다. 그런데 2026-08-19 기준 두 브랜치 모두
# 보호가 전혀 없었다 — 룰셋 목록이 비어 있고 protection 조회가 404 였다. 즉 push 권한만
# 있으면 누구나 main 에 직접 밀어 수업 중인 학습자가 보는 것을 바꿀 수 있었다.
#
# README 가 "stage → main PR 이 곧 릴리스이고 그 리뷰가 게이트다" 라고 말하는 설계 전체가
# 이 설정 하나에 얹혀 있다. 그래서 이걸 문서가 아니라 실행 가능한 스크립트로 남긴다.
#
#   ./tools/setup-branch-protection.sh
#
# 되돌리려면 GitHub → Settings → Rules → Rulesets 에서 두 룰셋을 지우면 된다.

set -euo pipefail

REPO="${REPO:-re-speak/podo-curriculum}"

# Cloud Build 가 PR 에 올리는 체크 이름. podo-infra 의 트리거 설정과 같아야 한다.
# 이름이 어긋나면 "존재하지 않는 체크를 영원히 기다리는" PR 이 되므로, 아래 확인 절차를
# 반드시 거친다.
CHECK="${CHECK:-podo-curriculum-validate}"

echo "대상 저장소: $REPO"

if ! gh api "repos/$REPO" --jq '.permissions.admin' | grep -q true; then
  cat >&2 <<'MSG'
admin 권한이 없다. 이 스크립트는 조직 owner 또는 저장소 admin 계정으로 실행해야 한다.
(GitHub 은 권한이 없는 admin 엔드포인트에 403 이 아니라 404 를 준다.)

현재 admin 인 사람: sinsayer, cohemm
  gh auth switch  # 로 계정을 바꾼 뒤 다시 실행한다
MSG
  exit 1
fi

# 실제로 PR 에 올라온 적 있는 체크 이름을 보여준다. 여기 CHECK 가 없으면 아직 한 번도
# 돈 적이 없다는 뜻이고, 그대로 걸면 머지가 막힌다.
echo
echo "최근 PR 에서 관측된 체크 이름:"
gh api "repos/$REPO/commits/stage/check-runs" --jq '.check_runs[].name' 2>/dev/null | sort -u | sed 's/^/  /' || echo "  (없음)"
echo
echo "필수로 걸 체크: $CHECK"
read -r -p "이 이름이 위 목록에 있거나, 곧 생길 것이 확실한가? [y/N] " ok
[ "$ok" = "y" ] || { echo "중단한다. CHECK=<이름> 으로 다시 실행하거나, 체크 없이 걸려면 CHECK= 로 비운다."; exit 1; }

ruleset() {
  local branch="$1" approvals="$2" name="$3"
  local checks=""

  if [ -n "$CHECK" ]; then
    checks=$(cat <<JSON
,
    { "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [ { "context": "$CHECK" } ]
      } }
JSON
)
  fi

  # deletion / non_fast_forward: 브랜치를 지우거나 force-push 로 역사를 갈아엎는 경로를 막는다.
  #   배포 기록이 곧 브랜치 역사라, 되감기는 "무엇이 나갔는지"를 지우는 것과 같다.
  # pull_request: 직접 push 를 막는다. 이게 이 스크립트의 본체다.
  #   required_approving_review_count 는 stage 0 / main 1 이다 — 아래 호출부 주석 참고.
  cat > /tmp/ruleset-"$branch".json <<JSON
{
  "name": "$name",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/$branch"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": $approvals,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash", "merge"]
      } }$checks
  ]
}
JSON

  echo "→ $branch 룰셋 생성 ($name, 승인 $approvals 건 필요)"
  gh api "repos/$REPO/rulesets" -X POST --input /tmp/ruleset-"$branch".json \
    --jq '"  생성됨: id=\(.id) \(.name)"'
}

# stage — 승인 0건.
#
# PR 은 강제하되 사람을 기다리지는 않게 한다. stage 는 비프로덕션 셋(stage·qa·dev)을
# 채우는 브랜치이고, 여기서 실수하는 비용이 싼 것이 이 환경의 존재 이유다. 승인을
# 요구하면 초안 한 건마다 다른 사람을 붙잡아야 하고, 그러면 사람들이 게이트를 우회할
# 방법을 찾기 시작한다. PR 자체가 강제되는 것만으로 plan 코멘트를 보게 되고 —
# "머지하면 무엇이 배포되는가"를 눈으로 확인하는 것이 여기서 필요한 전부다.
ruleset stage 0 "stage-gate"

# main — 승인 1건.
#
# 여기 머지하면 수업 중인 학습자가 보는 것이 즉시 바뀐다. README 의 표현대로 stage → main
# PR 이 곧 릴리스이고 그 리뷰가 유일한 게이트다. 자기 PR 은 자기가 승인할 수 없으므로,
# 이 1건이 "혼자 프로덕션에 밀어넣을 수 없다"를 보장한다.
ruleset main 1 "main-release-gate"

cat <<'MSG'

완료. 확인:
  gh api repos/re-speak/podo-curriculum/rulesets --jq '.[] | "\(.name)\t\(.enforcement)"'

이제부터:
  - stage / main 으로의 직접 push 는 거부된다.
  - 두 브랜치 모두 PR 을 거쳐야 하고, 검증 체크가 통과해야 머지된다.
  - main 은 추가로 다른 사람의 승인 1건이 필요하다.
  - CODEOWNERS 는 리뷰어를 자동으로 붙이되 막지는 않는다(.github/CODEOWNERS 주석 참고).
MSG
