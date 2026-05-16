---
name: pm-workflow
description: "PM 자동화 워크플로우 팩토리. 시장 조사·경쟁사 분석·유저 인터뷰부터 PRD 작성,
  로드맵 수립, 요구사항 검증까지 4단계 파이프라인을 자동 실행한다.
  제품 기획, PRD 작성, 로드맵, 시장 조사, 경쟁사 분석, 유저 스토리, 요구사항 문서를 요청하면
  반드시 이 스킬을 사용할 것.
  이전 결과 수정, 단계 재실행, PRD 보완, 로드맵 업데이트, 검증 재실행 요청 시에도 사용."
---

# PM Workflow

제품 아이디어부터 검증된 PRD와 실행 가능한 로드맵까지 4단계 파이프라인을 자동 실행한다.

## 실행 모드

| 모드 | 트리거 | 동작 |
|------|--------|------|
| **전체 실행** | 새 제품 아이디어, `_workspace/` 미존재 | Phase 1~4 순차 실행 |
| **단계 재실행** | "로드맵만 다시", "PRD 수정", "검증 다시" | 해당 Phase만 재실행 |
| **새 제품** | `_workspace/` 존재 + 새 아이디어 | 기존 백업 후 전체 실행 |

## 에이전트 구성

| 에이전트 | 타입 | 모델 | 역할 | 출력 |
|---------|------|------|------|------|
| research-analyst | `general-purpose` | Haiku | 시장·경쟁사·유저 문제 조사 | `_workspace/01_research.md` |
| prd-writer | `general-purpose` | Opus | PRD 작성 (INVEST 기준) | `_workspace/02_prd.md` |
| roadmap-planner | `general-purpose` | Opus | MoSCoW 로드맵 + 의존성 | `_workspace/03_roadmap.md` |
| prd-validator | `general-purpose` | Haiku | 교차 검증 + 이슈 분류 | `_workspace/04_validation.md` |

## 워크플로우

### Phase 0: 컨텍스트 확인

1. `_workspace/` 디렉토리 존재 여부 확인
2. 실행 모드 결정:
   - `_workspace/` 미존재 → 초기 실행. `_workspace/00_input/` 생성 후 Phase 1로 진행
   - `_workspace/` 존재 + "로드맵만", "PRD 수정", "검증만" 등 재실행 요청 → 해당 Phase만 실행
   - `_workspace/` 존재 + 새 제품 아이디어 → `_workspace_{YYYYMMDD_HHMMSS}/`로 백업 후 Phase 1
3. `_workspace/00_input/request.md` 생성 (사용자 요청 원문 저장):
   ```
   # 제품 기획 요청
   {사용자가 입력한 원문 내용}
   ```
4. `_workspace/00_input/interviews/` 경로 안내: 유저 인터뷰 파일이 있으면 해당 경로에 배치하도록 사용자에게 알림

### Phase 1: research-analyst 실행

```
Agent(
  description: "시장·경쟁사·유저 문제 조사",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 research-analyst입니다. agents/research-analyst.md의 지침을 따르세요.

           대상 프로젝트 경로: {대상 프로젝트 경로}

           1. _workspace/00_input/request.md를 읽어 조사 방향을 파악하세요.
           2. _workspace/00_input/interviews/ 경로를 탐색하여 인터뷰 파일이 있으면 읽고 요약하세요.
           3. 시장 조사, 경쟁사 분석, 유저 페인 포인트를 조사하세요.
           4. 완료 후 _workspace/01_research.md를 작성하세요."
)
```

완료 후 `_workspace/01_research.md` 존재 확인.
실패 시: 빈 조사 결과 파일 생성 후 Phase 2 진행 ("외부 조사 없음" 명시).

### Phase 2: prd-writer 실행

`_workspace/01_research.md` 확인 후 진행.

```
Agent(
  description: "PRD 작성",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 prd-writer입니다. agents/prd-writer.md의 지침을 따르세요.

           대상 프로젝트 경로: {대상 프로젝트 경로}

           1. skills/sprote/references/pm-standards.md를 먼저 읽으세요 (필수).
           2. _workspace/01_research.md를 읽어 시장 컨텍스트를 파악하세요.
           3. _workspace/00_input/request.md를 읽어 초기 요구사항을 파악하세요.
           4. pm-standards.md의 PRD 템플릿 구조와 INVEST 기준을 적용하여 PRD를 작성하세요.
           5. 완료 후 _workspace/02_prd.md를 작성하세요."
)
```

완료 후 `_workspace/02_prd.md` 존재 확인.
실패 시: 파이프라인 중단, 사용자에게 오류 보고 (PRD 없이 하위 단계 불가).

### Phase 3: roadmap-planner 실행

`_workspace/02_prd.md` 확인 후 진행.

```
Agent(
  description: "MoSCoW 로드맵 및 의존성 설계",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 roadmap-planner입니다. agents/roadmap-planner.md의 지침을 따르세요.

           대상 프로젝트 경로: {대상 프로젝트 경로}

           1. _workspace/02_prd.md를 읽어 기능 요구사항을 파악하세요.
           2. _workspace/01_research.md를 읽어 시장 컨텍스트를 우선순위 결정에 반영하세요.
           3. skills/sprote/references/pm-standards.md의 로드맵 형식과 MoSCoW 기준을 적용하세요.
           4. 완료 후 _workspace/03_roadmap.md를 작성하세요."
)
```

완료 후 `_workspace/03_roadmap.md` 존재 확인.
실패 시: PRD만 반환, 로드맵 생략 알림.

### Phase 4: prd-validator 실행

`_workspace/02_prd.md`, `_workspace/03_roadmap.md` 확인 후 진행.

```
Agent(
  description: "PRD 및 로드맵 교차 검증",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 prd-validator입니다. agents/prd-validator.md의 지침을 따르세요.

           대상 프로젝트 경로: {대상 프로젝트 경로}

           1. _workspace/02_prd.md를 읽으세요.
           2. _workspace/03_roadmap.md를 읽으세요.
           3. _workspace/01_research.md를 읽으세요 (기준 검증용).
           4. skills/sprote/references/pm-standards.md의 INVEST 체크리스트와 검증 패턴을 적용하세요.
           5. 이슈를 [HIGH]/[MEDIUM]/[LOW]로 분류하고 _workspace/04_validation.md를 작성하세요."
)
```

완료 후 `_workspace/04_validation.md` 존재 확인.
실패 시: 검증 없이 PRD + 로드맵 반환, 수동 검토 권고.

### Phase 5: 결과 보고

`_workspace/04_validation.md`를 읽어 사용자에게 요약 보고:

```
## PM Workflow 완료

### 생성 산출물
- 조사 결과: _workspace/01_research.md
- PRD: _workspace/02_prd.md
- 로드맵: _workspace/03_roadmap.md
- 검증 보고서: _workspace/04_validation.md

### 검증 요약
- 전체 판정: {APPROVED | APPROVED_WITH_WARNINGS | NEEDS_REVISION}
- [HIGH] 이슈: {N}개
- [MEDIUM] 이슈: {N}개

### 다음 단계
{APPROVED → 개발 착수 준비 완료 메시지}
{APPROVED_WITH_WARNINGS → 권고 이슈 목록 및 개선 제안}
{NEEDS_REVISION → [HIGH] 이슈 목록 + 재실행 안내}
```

**재실행 옵션 (NEEDS_REVISION 또는 [HIGH] 이슈 발생 시):**
- [HIGH] 이슈가 있을 경우, 사용자에게 재실행 여부를 묻는다.
- 사용자가 동의하면 해당 단계(prd-writer 또는 roadmap-planner)를 **최대 1회** 재실행한다.
- 재실행 후에도 [HIGH] 이슈가 남아 있으면 이슈 목록과 함께 결과를 반환하고 수동 수정을 권고한다. 재실행을 반복하지 않는다.

## 데이터 흐름

```
_workspace/00_input/request.md
_workspace/00_input/interviews/ (있는 경우)
        ↓
research-analyst (Haiku)
        ↓
_workspace/01_research.md
        ↓
prd-writer (Opus) ←── pm-standards.md (PRD 템플릿)
        ↓
_workspace/02_prd.md
        ↓
roadmap-planner (Opus) ←── _workspace/01_research.md (시장 컨텍스트)
                       ←── pm-standards.md (로드맵 형식)
        ↓
_workspace/03_roadmap.md
        ↓
prd-validator (Haiku) ←── _workspace/02_prd.md
                      ←── _workspace/01_research.md (기준 검증)
                      ←── pm-standards.md (INVEST 체크리스트)
        ↓
_workspace/04_validation.md
```

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| research-analyst 실패 | 빈 조사 결과로 계속 진행, prd-writer에 "조사 없음" 명시 |
| prd-writer 실패 | 파이프라인 중단, 사용자에게 오류 보고 (PRD 없이 하위 단계 불가) |
| roadmap-planner 실패 | PRD만 반환, "로드맵 생성 실패" 알림 |
| prd-validator 실패 | 검증 없이 PRD + 로드맵 반환, 수동 검토 권고 |
| [HIGH] 이슈 발생 | 사용자에게 재실행 여부 확인, 동의 시 최대 1회 재실행 후 종료 |
| `_workspace/` 쓰기 권한 없음 | 오류 즉시 보고, 경로 확인 요청 |

## 테스트 시나리오

### 시나리오 1: 정상 실행 (신규 제품 아이디어)
- 입력: "B2B SaaS 일정 관리 도구 기획해줘"
- 기대 동작: Phase 0~4 순차 실행, 4개 파일 모두 생성
- 기대 출력: APPROVED 또는 APPROVED_WITH_WARNINGS 판정

### 시나리오 2: 단계 재실행
- 입력: `_workspace/02_prd.md` 존재 상태에서 "로드맵만 다시 짜줘"
- 기대 동작: Phase 0에서 "로드맵 재실행" 감지 → Phase 3만 실행
- 기대 출력: `_workspace/03_roadmap.md` 갱신, 기존 PRD 유지

### 시나리오 3: research-analyst 실패
- 상황: 웹 검색 도구 미설정
- 기대 동작: 빈 조사 결과로 Phase 2 진행, prd-writer에 "외부 조사 없음" 명시
- 기대 출력: PRD와 로드맵은 생성, 검증 보고서에 "조사 부재" WARN 기록

### 시나리오 4: 검증 [HIGH] 이슈 재실행
- 상황: prd-validator가 [HIGH] 이슈 3개 탐지
- 기대 동작: 사용자에게 재실행 여부 확인 → 동의 시 prd-writer 1회 재실행 → 결과 반환
- 기대 출력: 재실행 후 [HIGH] 이슈 감소 여부와 무관하게 결과 반환 (무한 루프 방지)
