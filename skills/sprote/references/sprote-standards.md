# TTB Skill Factory 표준

TTB가 생성하는 모든 Claude Code 플러그인(스킬/하네스)에 적용되는 품질 표준.

## 목차

1. [파일 구조 표준](#1-파일-구조-표준)
2. [스킬 작성 표준](#2-스킬-작성-표준)
3. [에이전트 정의 표준](#3-에이전트-정의-표준)
4. [오케스트레이터 표준](#4-오케스트레이터-표준)
5. [언어 및 명명 표준](#5-언어-및-명명-표준)
6. [모델 설정 표준](#6-모델-설정-표준)
7. [Codex 연계 표준](#7-codex-연계-표준)
8. [검증 기준](#8-검증-기준)
9. [런타임 엔진 해석 표준](#9-런타임-엔진-해석-표준)

---

## 1. 파일 구조 표준

```
{프로젝트}/
├── CLAUDE.md                          # 하네스 포인터 + 변경 이력
└── .claude/
    ├── agents/
    │   └── {역할명}.md                # kebab-case
    └── skills/
        └── {스킬명}/                  # kebab-case
            ├── SKILL.md
            └── references/            # 조건부 로딩 문서
                └── {도메인}.md
```

**금지:**
- `.claude/commands/` 생성 — 커맨드는 사용하지 않음
- `README.md`, `CHANGELOG.md` 등 부가 문서 생성 (스킬 내부)
- 파일명에 대문자, 공백, 언더스코어 사용

---

## 2. 스킬 작성 표준

### Frontmatter

```yaml
---
name: {스킬명}          # 소문자 kebab-case
description: "..."      # 아래 기준 충족 필수
---
```

### Description 필수 조건

1. **초기 트리거 키워드**: 스킬이 하는 일을 구체적으로 나열
2. **후속 작업 키워드**: "다시 실행", "수정", "업데이트", "보완", "개선" 포함
3. **길이**: 2~4 문장, 약 50~100 단어
4. **어조**: 적극적("pushy") — "반드시 이 스킬을 사용할 것"

**나쁜 예:**
```yaml
description: "데이터를 처리하는 스킬"
```

**좋은 예:**
```yaml
description: "사용자 데이터를 읽어 분석 보고서를 생성하는 스킬.
  데이터 분석, 통계 요약, 시각화, 이상값 탐지 등을 수행한다.
  데이터 파일을 언급하거나 분석을 요청하면 반드시 이 스킬을 사용할 것.
  이전 분석 결과 수정, 재분석, 업데이트 요청 시에도 사용."
```

### 본문 기준

- **500줄 이내** — 초과 시 references/로 분리
- **명령형 어조** — "~한다", "~하라"
- **Why-First** — 규칙보다 이유를 먼저 설명
- 이미 Claude가 아는 일반 지식은 포함하지 않음

---

## 3. 에이전트 정의 표준

각 에이전트는 `.claude/agents/{name}.md`에 정의한다. 빌트인 타입(`general-purpose`, `Explore`, `Plan`)이라도 파일을 생성한다.

### 필수 섹션

```markdown
---
name: {에이전트명}
description: {한 줄 역할 설명}
---

# {에이전트명}

## 핵심 역할
## 작업 원칙
## 입력/출력 프로토콜
## 에러 핸들링
## 팀 통신 프로토콜   ← 팀 모드에서만 필수
```

### 팀 통신 프로토콜 형식

```markdown
## 팀 통신 프로토콜

### 수신 대상
- {에이전트명}으로부터: {어떤 정보}

### 발신 대상
- {에이전트명}에게: {어떤 정보 + 언제}

### 협업 방식
(분쟁 해결, 합의 방법 명시)
```

---

## 4. 오케스트레이터 표준

오케스트레이터는 스킬의 특수한 형태. `.claude/skills/{name}/SKILL.md`에 생성.

### 필수 포함 항목

| 항목 | 위치 | 설명 |
|------|------|------|
| `## 실행 모드` | 상단 | 팀/서브/하이브리드 명시 |
| `## 에이전트 구성` | 상단 | 팀원 표 (이름, 타입, 역할, 스킬, 출력) |
| Phase 0: 컨텍스트 확인 | 워크플로우 첫 번째 | `_workspace/` 분기 로직 |
| `## 데이터 흐름` | 워크플로우 후 | 에이전트 간 데이터 이동 다이어그램 |
| `## 에러 핸들링` | 데이터 흐름 후 | 상황별 전략 표 |
| `## 테스트 시나리오` | 마지막 | 정상 1 + 에러 1 이상 |

### Phase 0 표준 구조

```markdown
### Phase 0: 컨텍스트 확인

1. `_workspace/` 디렉토리 존재 여부 확인
2. 실행 모드 결정:
   - `_workspace/` 미존재 → 초기 실행. Phase 1로 진행
   - `_workspace/` 존재 + 부분 수정 요청 → 해당 에이전트만 재호출
   - `_workspace/` 존재 + 새 입력 → `_workspace_{YYYYMMDD_HHMMSS}/`로 이동 후 Phase 1
```

### 중간 산출물 경로 컨벤션

```
_workspace/
├── 00_input/          # 사용자 입력 저장
├── {phase}_{agent}_{artifact}.md
└── (최종 산출물은 사용자 지정 경로)
```

---

## 5. 언어 및 명명 표준

| 항목 | 규칙 |
|------|------|
| 파일명 | kebab-case (소문자 + 하이픈) |
| 에이전트명 | kebab-case |
| 스킬명 | kebab-case |
| SKILL.md 본문 | 한국어 우선, 코드/기술 용어는 영문 유지 |
| 에이전트 파일 본문 | 한국어 우선 |
| 코드 주석 | 한국어 |
| 변수/함수명 | 영문 camelCase 또는 snake_case (언어 컨벤션 따름) |

---

## 6. 모델 설정 표준

**모든 Agent 호출은 역할(role) 기준으로 모델·subagent_type을 결정한다.** 빌드 타임에 모델을 하드코딩하지 않으며, `engine.json`을 런타임에 해석해 분기한다(상세는 §9).

### 역할 분류

| 역할 | 의미 | 해석 규칙 |
|------|------|---------|
| `ANALYSIS` | 도메인·로그·요구사항 분석 | engine.json `engine_mode`로 런타임 해석 |
| `IMPLEMENTATION` | 코드·파일 수정 | engine.json `engine_mode`로 런타임 해석 |
| `LEADER` | 파이프라인 자율 관리 | 항상 `general-purpose` + `sonnet` 고정 |
| `LIGHT` | 리서치·문서화·검증 | 항상 `general-purpose` + `haiku` 고정 |

### Agent 호출 형식

`ANALYSIS` / `IMPLEMENTATION` 역할은 Phase -0.5에서 결정된 변수를 사용한다:

```
Agent(
  description: "...",
  subagent_type: "{ANALYSIS_SUBAGENT}",   ← Phase -0.5 결과 (예: codex:codex-rescue)
  model: "{ANALYSIS_MODEL}",              ← Phase -0.5 결과 (예: opus)
  prompt: "..."
)
```

`LEADER` / `LIGHT` 역할은 고정 값을 직접 명시한다:

```
Agent(
  description: "...",
  subagent_type: "general-purpose",
  model: "sonnet",                        ← LEADER 고정
  prompt: "..."
)
```

### 금지 사항

- 분석·구현 Agent 호출에 모델을 하드코딩하지 않는다 (`model: "opus"` 직접 명시 금지).
- TeamCreate 멤버에도 동일 규칙을 적용한다. 분석·구현 멤버의 model 필드는 Phase -0.5 변수로 채운다.

---

## 7. Codex 연계 표준

TTB Skill Factory는 Codex와 Claude를 역할 분리하여 이중 분석 체계를 운영한다.

### 역할 분리 원칙

| 엔진 | 역할 | 강점 |
|------|------|------|
| **Codex** | 도메인 분석, 종합 검토 | 코드 관점 독립 분석, 편향 분리 |
| **Claude** | 아키텍처 설계, 파일 생성, 검증 | 패턴 설계 능력, 파일 작성 품질 |

### Codex 서브 에이전트 사용 규칙

1. Codex 에이전트는 `subagent_type: "codex:codex-rescue"`로 호출한다.
2. TeamCreate 팀원으로 Codex를 직접 추가하지 않는다. Codex는 항상 서브 에이전트로 실행.
3. Codex 에이전트 실패 시 `general-purpose` 서브 에이전트로 대체하고 산출물 파일에 대체 사실을 명시한다.

### Codex 에이전트 정의 파일 필수 항목

Codex로 실행되는 에이전트의 `.md` 파일에 반드시 포함:

```markdown
**실행 타입:** `codex:codex-rescue` (오케스트레이터가 Agent 도구로 호출)
```

```markdown
## 비고
이 에이전트는 서브 에이전트로 실행된다. 팀 통신(SendMessage)을 사용하지 않으며,
결과를 파일로 저장하면 오케스트레이터가 수집한다.
```

### 이중 분석 데이터 흐름

```
Codex(도메인 분석) → 파일 → Claude(아키텍처 설계) → 파일 → Codex(종합 검토) → 파일 → Claude(생성)
```

Claude는 Codex 분석을 입력으로 읽고 아키텍처를 설계한다. Codex는 Claude 설계를 검토하여 보완점을 도출한다. 이 순환이 단방향이므로 Phase 간 명확한 파일 경로 전달이 필수다.

### 분석 결과 상충 처리

Codex와 Claude의 분석이 상충할 때:
- synthesis-reviewer가 상충 내용을 `02b_synthesis.md`에 명시한다
- builder는 `[HIGH]` 보완 사항을 우선 반영한다
- 판단하기 어려운 상충은 사용자에게 확인 요청한다

---

## 8. 검증 기준

하네스 생성 완료 후 validator가 확인하는 기준:

### PASS (문제 없음)
- 모든 필수 파일 존재
- SKILL.md 500줄 이내
- Description에 초기 + 후속 키워드 포함
- Phase 0 포함
- 오케스트레이터 SKILL.md에 **Phase -0.5 (엔진 해석) 블록 포함** (§9)
- 분석·구현 Agent 호출이 역할 변수 사용 (모델 하드코딩 없음)
- LEADER/LIGHT 역할만 고정 모델(sonnet/haiku) 명시 허용
- CLAUDE.md에 `## 코딩 행동 지침` 섹션 존재 (4개 항목 모두 포함, 파일 맨 위에 위치)

### WARN (권고 사항)
- SKILL.md 400~500줄 범위 (가급적 분리 권장)
- description이 다소 짧음 (트리거는 되지만 경계 케이스 미포함)
- 팀 통신 프로토콜이 약함

### FAIL (수정 필수)
- 에이전트 정의 파일 없음 (빌트인 타입이라도)
- Phase 0 미포함
- description이 너무 모호하여 트리거 불가
- `.claude/commands/` 파일 생성됨
- 오케스트레이터 SKILL.md에 Phase -0.5 (엔진 해석) 블록 누락
- 분석·구현 Agent 호출에 모델이 하드코딩됨 (역할 변수 미사용)
- CLAUDE.md에 `## 코딩 행동 지침` 섹션 없음
- `## 코딩 행동 지침`이 CLAUDE.md 맨 위에 있지 않음 (다른 섹션 뒤에 위치)

---

## 9. 런타임 엔진 해석 표준

생성된 자식 하네스는 **빌드 타임에 모델·엔진을 동결하지 않는다**. 오케스트레이터 SKILL.md는 매 실행마다 `engine.json`을 읽어 분석·구현 역할의 엔진을 결정한다.

### 9.1 engine.json 위치

```
{project_root}/.claude/sprote/engine.json
```

스키마:
```json
{
  "orchestrator_model": "opus | sonnet | haiku",
  "engine_mode": "codex_analysis | opus_analysis"
}
```

### 9.2 해석 매트릭스

| engine_mode | ANALYSIS subagent_type | ANALYSIS model | IMPLEMENTATION subagent_type | IMPLEMENTATION model |
|---|---|---|---|---|
| `codex_analysis` (기본) | `codex:codex-rescue` | (Codex 자체) | `general-purpose` | `sonnet` |
| `opus_analysis` | `general-purpose` | `opus` | `codex:codex-rescue` | (Codex 자체) |

> Codex 호출은 `subagent_type: "codex:codex-rescue"` 사용. model 필드는 무시되지만 일관성을 위해 `sonnet`으로 채운다.

### 9.3 Phase -0.5 표준 블록 (오케스트레이터 SKILL.md 필수)

builder는 모든 자식 오케스트레이터 SKILL.md에 다음 블록을 **Phase 0 직전에** 삽입한다:

```markdown
### Phase -0.5: 엔진 해석 (런타임)

매 실행마다 `engine.json`을 읽어 분석·구현 역할의 엔진을 결정한다.

1. Read 도구로 `{project_root}/.claude/sprote/engine.json` 읽기
   - 파일 없으면 → sprote 스킬을 안내하고 중단
2. `engine_mode` 추출 후 아래 표로 변수 할당:

   | engine_mode | ANALYSIS_SUBAGENT | ANALYSIS_MODEL | IMPLEMENTATION_SUBAGENT | IMPLEMENTATION_MODEL |
   |---|---|---|---|---|
   | codex_analysis | codex:codex-rescue | sonnet | general-purpose | sonnet |
   | opus_analysis | general-purpose | opus | codex:codex-rescue | sonnet |

3. `orchestrator_model`이 현재 세션 모델과 다르면 한 줄 경고 후 진행
4. **세션 플래그 `CODEX_AVAILABLE` 초기화**: 기본 `true`. §9.6 감지 신호 발생 시 `false`로 전환되며, 이후 모든 Codex 역할이 `general-purpose` + `sonnet`로 자동 대체된다 (CLAUDE_ONLY 모드).
5. Codex 1회성 폴백: `codex:codex-rescue` 호출이 일반 사유로 실패 시 → `general-purpose` + `sonnet`로 즉시 대체하고 한 줄 보고. 토큰 소진/할당량 초과/인증 만료 신호가 함께 감지되면 `CODEX_AVAILABLE=false`로 전환 (§9.6).
6. 이후 모든 Phase의 Agent 호출에서 `{ANALYSIS_*}` / `{IMPLEMENTATION_*}` 변수를 사용 (단, `CODEX_AVAILABLE=false`이면 Codex가 들어갈 자리는 §9.6 대체 매트릭스로 치환)

해석 결과 한 줄 보고 형식:
```
⚙️  엔진: ANALYSIS={ANALYSIS_SUBAGENT}/{ANALYSIS_MODEL}, IMPLEMENTATION={IMPLEMENTATION_SUBAGENT}/{IMPLEMENTATION_MODEL}
```
```

### 9.4 builder 출력 규칙

- 분석·구현 역할 Agent 호출 → 변수 플레이스홀더 사용
- LEADER/LIGHT 역할 Agent 호출 → 고정 값 직접 사용
- `Agent(... model: "opus" ...)` 같은 하드코딩은 LEADER/LIGHT가 아닌 한 모두 FAIL

### 9.5 폴백 정책

| 상황 | 처리 |
|------|------|
| engine.json 없음 | 사용자에게 `sprote` 스킬로 초기화 안내, 중단 |
| engine_mode 값 비정상 | 기본값 `codex_analysis`로 폴백 + 한 줄 경고 |
| codex:codex-rescue 일반 호출 실패 (1회성) | `general-purpose` + `sonnet`로 즉시 대체, 산출물에 대체 사실 명시 |
| **codex 토큰 소진 / 할당량 초과 / 인증 만료** | **세션 전체에서 Codex 영구 비활성화 (CLAUDE_ONLY 모드 — §9.6)** |
| orchestrator_model 불일치 | 경고 출력 후 계속 진행 (중단하지 않음) |

### 9.6 Codex 토큰 소진 폴백 (CLAUDE_ONLY 모드)

Codex가 토큰 소진·할당량 초과·인증 만료 등의 이유로 더 이상 사용 불가능할 때, 오케스트레이터는 세션 플래그 `CODEX_AVAILABLE=false`를 설정하고 이후 모든 Codex 역할을 Claude로 대체한다.

#### 감지 신호 (다음 중 하나 이상 발생 시)

- 응답에 `rate_limit_exceeded`, `quota_exceeded`, `token_quota`, `429`, `payment required`, `subscription expired`, `authentication failed`, `unauthorized` 키워드 포함
- 같은 호출이 2회 연속 실패하며 동일한 인증/할당 관련 에러 반환
- Codex CLI 자체가 `command not found` 또는 비정상 종료

#### 대체 매트릭스 (CODEX_AVAILABLE=false 시)

| engine_mode | ANALYSIS 대체 | IMPLEMENTATION 대체 |
|---|---|---|
| `codex_analysis` (분석=Codex) | `general-purpose` + `sonnet` | (변경 없음 — 원래 Sonnet) |
| `opus_analysis` (구현=Codex) | (변경 없음 — 원래 Opus) | `general-purpose` + `sonnet` |

> 두 모드 모두 **분석=Opus 또는 Sonnet, 구현=Sonnet** 의 "Claude-only" 조합으로 수렴한다. 사용자가 의도한 분석·구현 분리 자체는 유지되며, Codex만 빠진 형태로 진행된다.

#### 보고 형식

대체 활성화 시 한 줄로 사용자에게 보고하고, 모든 산출물 파일 첫 줄에도 표시:

```
⚠️  Codex 사용 불가 (사유: {token_quota|auth_expired|cli_missing|...}) — Claude-only 모드로 진행
```

#### 복구

세션 내에서는 자동 복구하지 않는다. 사용자가 Codex 인증·할당량을 갱신한 뒤 새 세션에서 재시도하거나, `engine.json`의 `engine_mode`를 직접 변경한다.
