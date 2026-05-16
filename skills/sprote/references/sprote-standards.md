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
| `ANALYSIS` | 도메인·로그·요구사항 분석 | 항상 Claude (`general-purpose` + `orchestrator_model`) |
| `IMPLEMENTATION` | 코드·파일 수정 | 항상 Claude (`general-purpose` + `orchestrator_model`) |
| `REVIEW` | 산출물 리뷰·수정 | engine.json `capabilities`로 폴백 체인 결정 (§9) |
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
- 분석·구현·리뷰 Agent 호출이 역할 변수 사용 (모델 하드코딩 없음)
- REVIEW 호출은 REVIEW_MODE 분기 처리 (§9.3 폴백 체인)
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

## 9. 런타임 엔진 해석 표준 (v2.2.0+)

생성된 자식 하네스는 **빌드 타임에 모델·엔진을 동결하지 않는다**. 오케스트레이터 SKILL.md는 매 실행마다 `engine.json`을 읽어 capability 폴백 체인으로 REVIEW 단계의 엔진을 결정한다.

**고정 분담**: ANALYSIS·IMPLEMENTATION은 항상 Claude가 담당. REVIEW만 폴백 체인.

### 9.1 engine.json 위치 및 스키마

```
{project_root}/.claude/sprote/engine.json
```

```json
{
  "orchestrator_model": "opus | sonnet | haiku",
  "runtime": "auto | claude | ollama | compatible_cli",
  "capabilities": {
    "codex_cli": "auto | true | false",
    "opus_review": "auto | true | false",
    "subagents": "auto | true | false"
  }
}
```

`engine_mode` 필드는 deprecated. 발견 시 무시하고 한 줄 안내.

### 9.2 역할 변수 매트릭스

ANALYSIS/IMPLEMENTATION은 고정. REVIEW만 capability로 결정.

| 역할 | SUBAGENT | MODEL | 비고 |
|------|----------|-------|------|
| ANALYSIS | `general-purpose` | `{orchestrator_model}` | 항상 Claude |
| IMPLEMENTATION | `general-purpose` | `{orchestrator_model}` | 항상 Claude |
| REVIEW | 폴백 체인 (§9.3) | 폴백 체인 (§9.3) | capability로 결정 |
| LEADER | `general-purpose` | `sonnet` | 고정 |
| LIGHT | `general-purpose` | `haiku` | 고정 |

### 9.3 REVIEW 폴백 체인

| 조건 | REVIEW_MODE | REVIEW_SUBAGENT | REVIEW_MODEL | 패치 적용 주체 |
|------|-------------|-----------------|--------------|--------------|
| `capabilities.codex_cli = true` | `codex` | `codex:codex-rescue` | (Codex 자체) | Codex (workspace-write) |
| `codex_cli=false`, `opus_review=true` | `opus_advisor` | `general-purpose` | `opus` | 오케스트레이터(Sonnet) |
| 둘 다 false | `self_review` | `general-purpose` | `{orchestrator_model}` | 오케스트레이터 자신 |

#### 9.3.1 opus_advisor 동작

1. REVIEW 단계에서 Opus advisor 호출 → 구조화 권고 JSON 배열 반환:

```json
[
  {
    "file": "agents/builder.md",
    "line_range": [42, 50],
    "current": "...",
    "suggested": "...",
    "severity": "P0|P1|P2|P3",
    "reason": "..."
  }
]
```

2. 오케스트레이터(Sonnet)가 P0·P1 항목을 Edit/Write로 패치 적용
3. 패치 후 validator(Haiku) 1회 재호출로 회귀 차단
4. 산출물에 `## Applied Patches` 섹션 기록

#### 9.3.2 self_review 동작 (Single-engine review)

같은 모델이 재호출되므로 자기 비판 한계 회피책 필수:

1. **역할 전환 프롬프트**: "이전 산출물에 최소 1개 P0 결함이 있다고 가정. red team으로서 찾아내라"
2. **체크리스트 6차원**: 도메인 누락 / 역할 모순 / 표준 위반 / 트리거 충돌 / description 품질 / 테스트 가능성
3. **컨텍스트 격리**: 산출물 파일만 입력, 이전 reasoning·계획 문서 제외
4. **JSON 스키마 강제**: 9.3.1과 동일 형식
5. **신뢰도 태그**: 모호한 항목은 `[LOW_CONFIDENCE]` 부착
6. **사용자 확인**: P0·P1 패치 적용 전 사용자에게 한 번 확인 (1·2순위는 자동, 3순위만 확인 단계)
7. **신뢰도 배너**: 산출물 보고서 상단에 자동 삽입

```
> ⚠️ Single-engine review: 이 검증은 동일 모델이 수행했습니다.
> Codex 또는 Opus 리뷰가 없으므로 P0·P1 항목은 사용자 확인을 권장합니다.
```

### 9.4 Phase -0.5 표준 블록 (오케스트레이터 SKILL.md 필수)

builder는 모든 자식 오케스트레이터 SKILL.md에 다음 블록을 **Phase 0 직전에** 삽입한다:

```markdown
### Phase -0.5: 엔진 해석 (런타임)

매 실행마다 `engine.json`을 읽어 REVIEW 단계의 엔진을 결정한다.

1. Read 도구로 `{project_root}/.claude/sprote/engine.json` 읽기
   - 파일 없으면 → sprote 스킬을 안내하고 중단
2. `orchestrator_model` 추출 → ANALYSIS·IMPLEMENTATION 변수 할당:
   - ANALYSIS_SUBAGENT = "general-purpose"
   - ANALYSIS_MODEL = {orchestrator_model}
   - IMPLEMENTATION_SUBAGENT = "general-purpose"
   - IMPLEMENTATION_MODEL = {orchestrator_model}
3. `capabilities` 추출 → REVIEW 변수 할당 (폴백 체인 §9.3 적용):
   - codex_cli=true → REVIEW_MODE=codex, REVIEW_SUBAGENT=codex:codex-rescue, REVIEW_MODEL=sonnet
   - opus_review=true → REVIEW_MODE=opus_advisor, REVIEW_SUBAGENT=general-purpose, REVIEW_MODEL=opus
   - else → REVIEW_MODE=self_review, REVIEW_SUBAGENT=general-purpose, REVIEW_MODEL={orchestrator_model}
4. `engine_mode` 필드 발견 시 한 줄 안내: "engine_mode는 deprecated, 무시됨"
5. `orchestrator_model`이 현재 세션 모델과 다르면 한 줄 경고 후 진행

해석 결과 한 줄 보고:
```
⚙️  엔진: ANALYSIS/IMPL={ANALYSIS_MODEL}, REVIEW={REVIEW_MODE}({REVIEW_MODEL})
```
```

### 9.5 builder 출력 규칙

- ANALYSIS·IMPLEMENTATION Agent 호출 → `{ANALYSIS_*}` / `{IMPLEMENTATION_*}` 변수 사용
- REVIEW Agent 호출 → `{REVIEW_*}` 변수 사용, REVIEW_MODE에 따라 분기 처리
- LEADER/LIGHT Agent 호출 → 고정 값 직접 사용
- `Agent(... model: "opus" ...)` 같은 하드코딩은 LEADER/LIGHT 외 모두 FAIL

### 9.6 폴백 정책

| 상황 | 처리 |
|------|------|
| engine.json 없음 | 사용자에게 `sprote:setup` 안내, 중단 |
| `capabilities.*` = `auto` 미해소 | setup이 감지 단계에서 명시 boolean으로 치환. 진입 시 `auto` 남아있으면 보수적으로 `false` 처리 |
| 1순위 codex 호출 1회성 실패 | 2순위(opus_advisor)로 강등, 산출물에 강등 사실 명시 |
| codex 토큰 소진/인증 만료 | 세션 전체에서 `capabilities.codex_cli=false`로 전환, 2순위로 영구 강등 |
| 2순위 opus_advisor 실패 | 3순위(self_review)로 강등 + 사용자 확인 단계 추가 |
| 3순위 self_review 신뢰도 부족 | 사용자에게 수동 검토 요청, 자동 패치 중단 |
| orchestrator_model 불일치 | 경고 출력 후 계속 진행 |
| `engine_mode` 필드 잔존 | 한 번 안내 후 무시. setup 재실행 시 자동 제거 |

### 9.7 강등 보고 형식

폴백 강등 발생 시 한 줄로 사용자에게 보고하고 산출물 파일 첫 줄에도 표시:

```
⚠️  REVIEW 강등: codex(사유: {token_quota|auth_expired|cli_missing}) → opus_advisor
```

```
⚠️  REVIEW 강등: opus_advisor(사유: API 호출 실패) → self_review (사용자 확인 필요)
```

### 9.8 복구

세션 내 자동 복구 없음. 사용자가 codex 인증·할당량 갱신 또는 API 환경 복구 후 새 세션에서 재시도. capability 강제 설정은 `engine.json`을 직접 수정.
