#!/usr/bin/env python3
"""
대상 프로젝트의 CLAUDE.md 맨 위에 코딩 행동 지침을 보장한다.
- 지침이 없으면 맨 상단에 삽입한다 (멱등성 보장).
- CLAUDE.md가 없으면 지침만으로 새로 생성한다.

사용법: python ensure-coding-guidelines.py <project_path>
"""

import pathlib
import sys

MARKER = "## 코딩 행동 지침"

project_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.cwd()
claude_md = project_path / "CLAUDE.md"

# 스크립트 위치 기준으로 플러그인 루트 계산
plugin_root = pathlib.Path(__file__).parent.parent
guidelines_src = plugin_root / "skills" / "agents" / "references" / "coding-guidelines.md"

if not guidelines_src.exists():
    print(f"[ttb-agents] 오류: 지침 소스 파일을 찾을 수 없습니다: {guidelines_src}", file=sys.stderr)
    sys.exit(1)

existing = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""

if MARKER in existing:
    print("[ttb-agents] 코딩 행동 지침 이미 존재 — 스킵")
    sys.exit(0)

# 파일 헤더 3줄(#제목, 빈줄, 부제) 제거 후 본문만 추출
lines = guidelines_src.read_text(encoding="utf-8").splitlines(keepends=True)
body = "".join(lines[3:]).strip()

if existing:
    content = f"{MARKER}\n\n{body}\n\n---\n\n{existing}"
    msg = f"[ttb-agents] CLAUDE.md 맨 위에 코딩 행동 지침을 추가했습니다: {claude_md}"
else:
    content = f"{MARKER}\n\n{body}\n"
    msg = f"[ttb-agents] CLAUDE.md를 코딩 행동 지침으로 새로 생성했습니다: {claude_md}"

claude_md.parent.mkdir(parents=True, exist_ok=True)
claude_md.write_text(content, encoding="utf-8")
print(msg)
