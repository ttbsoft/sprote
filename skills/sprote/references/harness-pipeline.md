# Harness Pipeline (sprote harness 모드)

> 팀·하네스·워크플로우 자동화 생성 파이프라인. Codex+Claude 이중 분석으로 청사진을 설계하고 실제 하네스 파일을 생성한다.

## 사전 조건

- 권한 사전 체크 및 engine.json 로딩이 완료된 상태 (라우터 SKILL.md Step 3까지 완료)
- `_workspace/` 디렉터리 상태 확인:
  - **미존재** → 초기 실행 (Phase 1부터)
  - **존재 + 부분 수정 요청** → 부분 재실행 (해당 Phase부터)
  - **존재 + 새 도메인** → `_workspace_{YYYYMMDD_HHMMSS}/`로 이동 후 초기 실행

## 부분 재실행 분기

`_workspace/` 존재 + 부분 수정 요청 시:

| 요청 유형 | 재실행 시작 Phase |
|---------|----------------|
| 도메인 분석 재요청 | Phase 2a |
| 청사진만 수정 | Phase 2b |
| 종합 검토 재요청 | Phase 2c |
| 파일 재생성 | Phase 3 |
| 문서만 갱신 | Phase 3b |
| 검증 재실행 | Phase 4 |

프로젝트 경로는 `_workspace/00_input/request.md`에서 읽는다.

## Phase 0.5: 디자인 브리프 연계 확인

`_workspace/design/01_brief.md` 존재 여부 확인:
- 존재 → design 모드가 이미 실행됨. 디자인 브리프를 analysis-leader에 전달
- 미존재 → 독립 실행 모드

## Phase 1: 입력 수집

1. 사용자로부터 확인:
   - **도메인 설명**: 어떤 작업을 자동화할 것인가?
   - **대상 프로젝트 경로**: 하네스 파일을 어디에 생성할 것인가?
   - **코드베이스 경로**: 분석할 기존 코드베이스가 있는가?

2. `_workspace/00_input/request.md`에 입력 저장

3. 대상 프로젝트의 CLAUDE.md 코딩 행동 지침 보완 (Python 실행 패턴):
   1. `python3 "{CLAUDE_PLUGIN_ROOT}/scripts/ensure-coding-guidelines.py" "{대상 프로젝트 경로}"` 시도
   2. 실패 시 `python "..."` 재시도
   3. 둘 다 실패 시 → `references/native-fallback.md` 절차 실행

## Phase 1.5: 외부 리서치 (Brave Search)

`_workspace/00_research.md`가 이미 있으면 스킵.

```
Agent(
  description: "도메인 기술 트렌드 외부 리서치",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "당신은 search-analyst입니다. agents/search-analyst.md의 지침을 따르세요.
           도메인 설명을 참고하여 아래 4개 쿼리를 실행하세요:
           1. '{도메인 설명} automation best practices {현재 연도}'
           2. '{도메인 설명} AI agent workflow patterns'
           3. '{도메인 설명} open source automation tools {현재 연도}'
           4. '{도메인 설명} industry standards regulations'

           Brave Search MCP 우선. 미설정 시 WebSearch로 폴백.
           결과를 _workspace/00_research.md에 저장하세요."
)
```

## Phase 2: 분석 리더 실행

**오케스트레이터 역할**: 실행 → 완료 보고 수신. 내부 파이프라인에 개입하지 않는다.

```
Agent(
  description: "분석 파이프라인 자율 실행",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "당신은 analysis-leader입니다. agents/analysis-leader.md의 지침을 따르세요.
           도메인 설명: {도메인 설명}
           코드베이스 경로: {코드베이스 경로 또는 '없음'}
           engine_mode: {engine_mode}   ← codex_analysis | opus_analysis
           [연계] 디자인 브리프: _workspace/design/01_brief.md (존재하면 읽어서 컨텍스트 활용)
           내부 파이프라인(search-analyst → domain-analyst → pattern-analyst → synthesis-reviewer)을
           자율적으로 실행하고 완료 후 SendMessage로 보고하세요."
)
```

analysis-leader의 SendMessage 수신 후 Phase 3으로 진행.

## Phase 3: 빌드 리더 실행

```
Agent(
  description: "빌드 파이프라인 자율 실행",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "당신은 build-leader입니다. agents/build-leader.md의 지침을 따르세요.
           대상 프로젝트 경로: {대상 프로젝트 경로}
           engine_mode: {engine_mode}   ← codex_analysis | opus_analysis
           내부 파이프라인(builder → [docs-keeper ∥ validator ∥ harness-cross-validator])을
           자율적으로 실행하고 완료 후 SendMessage로 보고하세요."
)
```

build-leader의 SendMessage 수신 후 Phase 4로 진행.

> harness-cross-validator는 **리뷰 + 자동 수정** 권한을 가진다. 라우터 SKILL.md "Step 4 — 표준 검증 + 자동 수정" 참조.

## Phase 4: 결과 보고

build-leader SendMessage에서 수신한 상태 + 검증 보고서를 사용자에게 최종 보고:

- 생성된 파일 목록 (`_workspace/03_build_report.md`)
- Codex 분석 단계 교차 검증 반영 사항 (`_workspace/02b_synthesis.md`)
- 형식 검증 결과 (`_workspace/04_validation_report.md` — APPROVED / APPROVED_WITH_WARNINGS / NEEDS_REVISION)
- 의미 교차 검증 + 자동 적용 패치 (`_workspace/05_cross_validation_report.md`)
- 양쪽 검증이 동의한 FAIL/P0/P1 항목은 반드시 수정 방법 안내

### 에이전트 트리 출력 (필수)

`{project_root}/.claude/agents/` 디렉터리의 에이전트 파일을 읽어 아래 형식으로 출력한다.

```
## 생성된 하네스팀 구조

오케스트레이터 (Claude {orchestrator_model})
├─ {리더1 에이전트명} ({모델})  ← {역할 한 줄}
│   ├─ {서브에이전트명} ({모델})  ← {역할 한 줄}
│   └─ {서브에이전트명} ({모델})  ← {역할 한 줄}
└─ {리더2 에이전트명} ({모델})  ← {역할 한 줄}
    ├─ {서브에이전트명} ({모델})  ← {역할 한 줄}
    ├─ {서브에이전트명} ({모델})  ← {역할 한 줄}  ┐ 병렬
    └─ {서브에이전트명} ({모델})  ← {역할 한 줄}  ┘
```

트리 구성 규칙:
- 에이전트 파일의 `subagent_type` 또는 `model` 필드로 모델명 표시
- `description`에서 "관리 주체" 또는 "오케스트레이터" 언급이 있으면 리더로 분류
- 병렬 실행 에이전트는 `┐ 병렬` / `┘` 마커로 표시
- 에이전트 파일이 없거나 읽기 실패 시 트리 출력 생략

`_workspace/` 보존 (삭제하지 않음).

## 데이터 흐름

```
[사용자 입력]
     ↓
_workspace/00_input/request.md
     ↓
[Phase 2: analysis-leader]
  ├─ domain-analyst (Codex)   → _workspace/01_domain_analysis.md
  ├─ pattern-analyst (Codex)  → _workspace/02_blueprint.md
  └─ synthesis-reviewer (Codex) → _workspace/02b_synthesis.md
  └─ SendMessage → 오케스트레이터
     ↓
[Phase 3: build-leader]
  ├─ builder (Claude) → .claude/agents/, SKILL.md, CLAUDE.md
  ├─ docs-keeper (Haiku) ──────────────┐
  ├─ validator (Haiku, 형식) ──────────┤ 병렬
  └─ harness-cross-validator (Codex, 의미+수정) ┘
  └─ SendMessage → 오케스트레이터
     ↓
[Phase 4: 결과 보고]
```

**오케스트레이터 개입 횟수**: 2회 (각 리더 실행 시만).

## 에러 핸들링

에러 복구는 각 리더 에이전트가 자체적으로 처리한다.

| 실패 주체 | 복구 주체 | 전략 |
|---------|---------|------|
| domain-analyst (Codex) | analysis-leader | general-purpose로 즉시 대체, 파일에 표시 |
| pattern-analyst | analysis-leader | 도메인 분석만으로 간소화 청사진 직접 작성 |
| synthesis-reviewer (Codex) | analysis-leader | 빈 synthesis 파일 생성 후 계속 |
| builder | build-leader | 부분 build_report 작성 후 docs/validator 진행 |
| docs-keeper | build-leader | 경고 기록, 검증 결과(둘)만으로 보고 |
| validator | build-leader | 경고 기록, cross-validator 결과로 대체 |
| harness-cross-validator (Codex) | build-leader | Opus 폴백 자동 실행, 그래도 실패 시 validator만으로 보고 |
| analysis-leader 전체 실패 | 오케스트레이터 | SendMessage 수신 → 사용자에게 실패 보고 |
| build-leader 전체 실패 | 오케스트레이터 | SendMessage 수신 → 사용자에게 실패 보고 |

## 참조

- 테스트 시나리오: `references/test-scenarios.md`
- 표준: `references/sprote-standards.md` (Codex 연계 지침 포함)
- 네이티브 폴백: `references/native-fallback.md`
