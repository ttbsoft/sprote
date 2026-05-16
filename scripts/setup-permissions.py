#!/usr/bin/env python3
"""
ttb-agents 플러그인 필수 권한을 ~/.claude/settings.json에 자동 추가한다.
이미 존재하는 항목은 중복 추가하지 않는다 (멱등성 보장).
"""

import json
import pathlib
import sys

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
REQUIRED_PERMS = [
    "WebSearch",
    "WebFetch",
    "mcp__brave-search__brave_web_search",
    "mcp__brave-search__brave_local_search",
]

if not SETTINGS.exists():
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps({"permissions": {"allow": []}}), encoding="utf-8")

data = json.loads(SETTINGS.read_text(encoding="utf-8"))
data.setdefault("permissions", {}).setdefault("allow", [])

added = []
for perm in REQUIRED_PERMS:
    if perm not in data["permissions"]["allow"]:
        data["permissions"]["allow"].append(perm)
        added.append(perm)

SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if added:
    print("[ttb-agents/setup] 권한 추가됨:")
    for p in added:
        print(f"  + {p}")
else:
    print("[ttb-agents/setup] 필수 권한이 이미 모두 설정되어 있습니다.")
