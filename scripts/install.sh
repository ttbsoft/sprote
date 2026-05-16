#!/usr/bin/env bash
# sprote plugin installer — ~/.claude/settings.json에 marketplace + enabledPlugins 항목을 자동 추가한다.
# 멱등성 보장: 이미 설정된 경우 변경하지 않는다.
#
# 사용:
#   curl -fsSL https://raw.githubusercontent.com/ttbsoft/sprote/main/scripts/install.sh | bash
#   또는 로컬:
#   bash scripts/install.sh

set -euo pipefail

MARKETPLACE_NAME="sprote-marketplace"
PLUGIN_KEY="sprote@sprote-marketplace"
REPO="ttbsoft/sprote"
SETTINGS="${HOME}/.claude/settings.json"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[sprote/install] python3가 필요합니다. 먼저 설치해주세요." >&2
  exit 1
fi

mkdir -p "$(dirname "${SETTINGS}")"

python3 - "${SETTINGS}" "${MARKETPLACE_NAME}" "${PLUGIN_KEY}" "${REPO}" <<'PY'
import json
import pathlib
import sys

settings_path, marketplace, plugin_key, repo = sys.argv[1:5]
path = pathlib.Path(settings_path)

if path.exists():
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[sprote/install] settings.json 파싱 실패: {exc}", file=sys.stderr)
        sys.exit(1)
else:
    data = {}

changed = False

markets = data.setdefault("extraKnownMarketplaces", {})
desired_market = {"source": {"source": "github", "repo": repo}, "autoUpdate": True}
if markets.get(marketplace) != desired_market:
    markets[marketplace] = desired_market
    changed = True

enabled = data.setdefault("enabledPlugins", {})
if enabled.get(plugin_key) is not True:
    enabled[plugin_key] = True
    changed = True

if changed:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[sprote/install] {path} 갱신 완료")
else:
    print(f"[sprote/install] 이미 설치되어 있습니다 ({path})")
PY

cat <<EOF

[sprote/install] 설치 준비 완료.

다음 단계:
  1. Claude Code를 재시작하면 plugin이 자동 로드됩니다.
  2. Claude Code 안에서 다음을 실행하세요:
       /sprote:setup
     (권한·외부 plugin 감지 + engine.json 자동 생성)

EOF
