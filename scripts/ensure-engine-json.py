#!/usr/bin/env python3
"""
대상 프로젝트에 .claude/ttb-agents/engine.json이 없으면 플러그인 기본값으로 생성한다.

사용법: python ensure-engine-json.py <project_path> [plugin_root]
"""

import pathlib
import shutil
import sys

project_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
plugin_root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(__file__).parent.parent

target = project_path / ".claude" / "ttb-agents" / "engine.json"
source = plugin_root / "skills" / "agents" / "engine.json"

if target.exists():
    print(f"[ttb-agents] engine.json 이미 존재 — 스킵: {target}")
    sys.exit(0)

if not source.exists():
    print(f"[ttb-agents] 오류: 기본 engine.json을 찾을 수 없습니다: {source}", file=sys.stderr)
    sys.exit(1)

target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, target)

print(f"[ttb-agents] engine.json을 생성했습니다: {target}")
