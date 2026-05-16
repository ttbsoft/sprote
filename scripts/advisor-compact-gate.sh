#!/usr/bin/env bash
# advisor() PreToolUse 게이트.
# 세션당 첫 호출은 차단하고 /compact 실행을 안내한다.
# 사용자가 /compact 후 재요청하면 통과한다.

set -euo pipefail

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null || true)

if [ -z "$SESSION_ID" ]; then
  exit 0
fi

MARKER_DIR="${TMPDIR:-/tmp}"
MARKER="${MARKER_DIR}/sprote-advisor-ack-${SESSION_ID}"

if [ -f "$MARKER" ]; then
  exit 0
fi

touch "$MARKER"

cat <<'JSON'
{
  "decision": "block",
  "reason": "advisor() 호출 전 토큰 절감을 위해 /compact를 먼저 실행해주세요.\n\n  /compact\n\n실행 후 advisor()를 다시 요청하면 통과합니다. (세션당 한 번만 차단)"
}
JSON
