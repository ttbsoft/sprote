---
name: review
description: "TTB 표준 검증 전문가.
  현재 프로젝트의 하네스 파일(.claude/agents/, .claude/skills/)을 읽고 TTB 표준 준수 여부를 점검한다.
  '/ttb-agents:review', '하네스 검증해줘', 'TTB 표준 확인해줘', '에이전트 파일 검토해줘' 요청 시 반드시 이 스킬을 사용할 것.
  이전 검증 결과 재확인, 특정 파일만 재검증 요청 시에도 사용."
---

# TTB Review

현재 프로젝트의 하네스 산출물을 읽고 TTB 표준 기준으로 검증하여 PASS/WARN/FAIL 보고서를 생성한다.

## 에이전트 구성

| 에이전트 | 타입 | 엔진 | 역할 | 출력 |
|---------|------|------|------|------|
| validator | `general-purpose` | **Claude Haiku** | TTB 표준 검증 + 보고서 작성 | `_workspace/review_report.md` |

## 워크플로우

### Phase 0: 컨텍스트 확인

1. 대상 프로젝트 경로 파악:
   - 사용자가 경로를 명시한 경우 → 해당 경로 사용
   - 미명시 시 → 현재 디렉토리(`./`) 사용

2. `.claude/` 디렉토리 존재 여부 확인:
   - 미존재 → "하네스 파일이 없습니다. `/ttb-agents:agents`로 먼저 하네스를 생성하세요." 안내 후 종료
   - 존재 → Phase 1로 진행

3. `_workspace/review_report.md` 존재 여부 확인:
   - 존재 + 재검증 요청 아님 → 기존 보고서 내용 사용자에게 요약 후 종료
   - 미존재 또는 재검증 요청 → Phase 1 진행

### Phase 0.5: CLAUDE.md 코딩 행동 지침 보완

아래 Python 실행 패턴으로 실행한다:

1. `python3 "{CLAUDE_PLUGIN_ROOT}/scripts/ensure-coding-guidelines.py" "{프로젝트 경로}"` 시도
2. 실패 시 `python "{CLAUDE_PLUGIN_ROOT}/scripts/ensure-coding-guidelines.py" "{프로젝트 경로}"` 시도
3. 둘 다 실패 시 → **네이티브 폴백**: `skills/agents/SKILL.md`의 [네이티브 폴백 절차](#네이티브-폴백-ensure-coding-guidelines) 실행

출력 확인:
- "이미 존재" → Phase 1로 바로 진행
- "추가했습니다" → 사용자에게 한 줄 보고 후 Phase 1로 진행
- CLAUDE.md 없음 → Phase 1로 바로 진행 (validator가 FAIL 기록)

> 이미 존재하지만 맨 위가 아닌 경우는 수정하지 않는다 — validator가 FAIL로 기록한다.

### Phase 1: validator 실행

```
Agent(
  description: "TTB 표준 검증",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "당신은 validator입니다. agents/validator.md의 지침을 따르세요.

           대상 프로젝트 경로: {프로젝트 경로}
           TTB 표준 참조: skills/agents/references/ttb-standards.md

           아래 순서로 검증하세요:
           1. {프로젝트 경로}/.claude/agents/ 하위 에이전트 정의 파일 전체 읽기
           2. {프로젝트 경로}/.claude/skills/ 하위 SKILL.md 전체 읽기
           3. TTB 표준(ttb-standards.md)의 체크리스트 기준으로 각 파일 검증
           4. PASS/WARN/FAIL 분류 후 _workspace/review_report.md 작성

           _workspace/03_build_report.md가 있으면 참조하고, 없으면 파일을 직접 읽어 검증하세요."
)
```

### Phase 2: 결과 보고

`_workspace/review_report.md`를 읽어 사용자에게 요약 보고:

- 전체 통계: PASS N개 / WARN N개 / FAIL N개
- FAIL 항목: 파일명 + 수정 방법
- WARN 항목: 파일명 + 권고 사항
- 최종 판정: **APPROVED** / **APPROVED_WITH_WARNINGS** / **NEEDS_REVISION**

FAIL 항목이 있으면 `/ttb-agents:agents`로 재생성하거나 수동으로 수정하는 방법을 안내한다.

## 데이터 흐름

```
[사용자 요청]
      ↓
Phase 0: .claude/ 존재 확인
      ↓
Phase 0.5: CLAUDE.md 코딩 행동 지침 보완
  ├─ 지침 미존재 → 맨 위에 삽입 후 사용자 보고
  └─ 지침 존재 → 스킵
      ↓
[Phase 1: validator (Haiku)]
  ├─ .claude/agents/*.md 읽기
  ├─ .claude/skills/*/SKILL.md 읽기
  └─ TTB 표준 체크리스트 적용
      ↓
_workspace/review_report.md
      ↓
[Phase 2: 결과 요약 보고]
```

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| `.claude/` 미존재 | 하네스 생성 안내 후 종료 |
| 파일 읽기 실패 | FAIL로 기록하고 나머지 검증 계속 |
| validator 에이전트 실패 | Claude가 직접 체크리스트 기준으로 검증 |

## 테스트 시나리오

### 정상 흐름

1. 사용자: `/ttb-agents:review` (또는 "하네스 검증해줘")
2. Phase 0: `.claude/agents/` + `.claude/skills/` 존재 확인
3. Phase 1: validator → 에이전트 파일 N개, SKILL.md M개 검증
4. Phase 2: "PASS 12 / WARN 2 / FAIL 0 — APPROVED_WITH_WARNINGS" 보고

### 에러 흐름 (하네스 없음)

1. 사용자: `/ttb-agents:review`
2. Phase 0: `.claude/` 미존재
3. "하네스 파일이 없습니다. `/ttb-agents:agents`로 먼저 하네스를 생성하세요." 안내 후 종료
