---
name: sprote
description: "sprote(스프로테, 라틴어 어원: 너를 위해 존재한다) — 단일 진입점으로 6개 작업 모드를 라우팅한다.
  사용자 요청이 다음 중 어느 하나라도 매칭되면 반드시 이 스킬을 사용할 것.
  [harness 모드] '팀 구성해줘', '워크플로우 자동화', '하네스 만들어줘', '에이전트 추가', '재설계'
  [design 모드] 'UI 만들기', '디자인 검토', 'AI 안 티나게', '시각적 품질', '교차 검증'
  [code 모드] '파일 검색', '간단히 수정', '로그 분석', '테스트 실패 원인'
  [doc 모드] '릴리스 노트', '코드 리뷰 요약', '변경점 정리', '기술 블로그 초안'
  [pm 모드] '제품 기획', 'PRD 작성', '시장 조사', '로드맵', '경쟁사 분석'
  [sllm 모드] 'sLLM 에이전트', '소형 모델 자동화', 'Ollama 하네스', '9B 모델'
  이전 결과 수정·재실행·개선·팀원 추가 요청 시에도 사용."
---

# Sprote — 통합 진입점

너를 위해 존재한다. 한 스킬로 6개 작업을 라우팅한다.

## 동작 원칙

1. **모드 자동 분기**: 사용자 입력의 키워드·맥락으로 6개 모드 중 하나를 선택한다
2. **on-demand 로딩**: 선택된 모드의 파이프라인 문서만 명시적으로 `Read` 한다
3. **단일 출력 디렉터리**: 모든 산출물은 `{project}/_workspace/`에 저장한다

## 모드 라우팅 매트릭스

| 모드 | 트리거 키워드 | 파이프라인 문서 |
|------|------------|----------------|
| **harness** | 팀 구성, 워크플로우 자동화, 하네스, 에이전트 추가, 재설계 | `references/harness-pipeline.md` |
| **design** | UI 만들기, 디자인 검토, AI 안 티나게, 시각적 품질, artisan | `references/design-pipeline.md` |
| **code** | 파일 검색, 간단히 수정, 로그 분석, 테스트 실패 원인 | `references/code-pipeline.md` |
| **doc** | 릴리스 노트, 코드 리뷰 요약, 변경점 정리, 블로그 초안 | `references/doc-pipeline.md` |
| **pm** | 제품 기획, PRD, 시장 조사, 로드맵, 경쟁사 분석, INVEST | `references/pm-pipeline.md` |
| **sllm** | sLLM, 소형 모델 자동화, Ollama 하네스, 9B 모델 | `references/sllm-pipeline.md` |

**모드 결정이 모호하면**: 사용자에게 `AskUserQuestion`으로 명시적으로 묻는다. 추측으로 분기하지 않는다.

## 실행 절차 (모든 모드 공통)

### Step 1 — 모드 결정 및 파이프라인 문서 Read

선택된 모드에 따라 `references/{mode}-pipeline.md`를 `Read` 도구로 명시적으로 읽는다.

```
예시: harness 모드 → Read("skills/sprote/references/harness-pipeline.md")
```

해당 문서는 모드별 Phase, 에이전트 호출 순서, 출력 파일 명세, 트러블슈팅을 포함한다.

### Step 2 — 표준 문서 참조

작업 중 다음 참조 문서를 필요 시점에 Read한다:

| 시점 | 문서 |
|------|------|
| 하네스 산출물 표준 확인 | `references/sprote-standards.md` |
| 디자인 원칙·안티패턴 | `references/design-principles.md` |
| 생성 프로젝트의 CLAUDE.md 코딩 지침 | `references/coding-guidelines.md` |
| sLLM 10대 최적화 기법 | `references/sllm-optimizations.md` |
| PM 산출물 표준·INVEST | `references/pm-standards.md` |
| 라우팅 모호 시 의사결정 매트릭스 | `references/routing-matrix.md` |

### Step 3 — 파이프라인 실행

`references/{mode}-pipeline.md`의 Phase별 절차를 그대로 따른다.

- Phase 시작 전: 해당 mode 파이프라인 문서의 "사전 조건" 항목 확인
- 에이전트 호출: `Agent(subagent_type: "...", prompt: "...")` 형식
- 산출물: `_workspace/` 하위에 명세된 파일명으로 저장
- Phase 완료 시 사용자에게 한 줄 진행 보고

### Step 4 — 표준 검증 + 자동 수정 (폴백 체인)

작업 완료 시 형식 검증은 항상 수행하고, 의미 검증+수정은 capability에 따라 폴백한다.

#### 4.1 형식 검증 (read-only, 모든 환경 공통)

| 에이전트 | 엔진 | 권한 |
|---------|------|------|
| `validator` | Haiku | 보고서만 작성 |

산출물: `_workspace/{모드}_validator_report.md`

#### 4.2 의미 검증 + 수정 — 폴백 체인

**1순위: codex_cli = true** (기본)

| 에이전트 | 엔진 | 권한 |
|---------|------|------|
| `harness-cross-validator` (harness) | **Codex (write)** | 보고서 + 직접 패치 |
| `design-cross-validator` (design) | **Codex (write)** | 보고서 + 직접 패치 |

동작:
1. 리뷰 보고서를 `_workspace/05_cross_validation_report.md`(harness) 또는 `_workspace/cross_validation_report.md`(design)에 작성
2. P0·P1 항목은 직접 코드 패치 — `## Applied Patches` 섹션에 기록
3. P2·P3 항목은 권고만, 사용자 결정 위임
4. 패치 후 `validator` 1회 재호출 (회귀 차단)

안전장치: Codex sandbox `workspace-write` 모드, 외과적 변경 원칙, 패치 범위는 결함 직접 원인 파일로 제한.

**2순위: codex_cli = false AND opus_review = true** (Opus advisor 폴백)

| 단계 | 주체 | 동작 |
|------|------|------|
| 권고 생성 | Opus (advisor 메커니즘) | 구조화 권고 JSON 반환 — 직접 write 권한 없음 |
| 패치 적용 | Sonnet 오케스트레이터 | 권고 JSON을 받아 Edit/Write로 P0·P1 패치 적용 |
| 회귀 차단 | validator (Haiku) | 1회 재호출 |

Opus 출력 스키마 (강제):

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

산출물 동일: `_workspace/05_cross_validation_report.md`. `## Applied Patches` 섹션에 Sonnet이 적용한 변경 기록.

**3순위: 둘 다 false** (로컬 LLM 단독 — Single-engine review)

| 단계 | 주체 | 동작 |
|------|------|------|
| 재분석 | `orchestrator_model` 동일 모델 | red-team 역할 + 체크리스트 6차원 + 컨텍스트 격리 |
| 패치 적용 | 동일 모델 | 발견된 P0·P1만 패치 (사용자 확인 후) |

재호출 프롬프트 규칙:

1. **역할 전환**: "이전 산출물에 최소 1개 P0 결함이 있다고 가정. red team으로서 찾아내라"
2. **체크리스트 6차원**: 도메인 누락 / 역할 모순 / 표준 위반 / 트리거 충돌 / description 품질 / 테스트 가능성
3. **컨텍스트 격리**: 산출물 파일만 입력, 이전 reasoning·계획 문서 제외
4. **JSON 스키마 강제** (2순위와 동일 형식)
5. **신뢰도 태그**: 모호한 항목은 `[LOW_CONFIDENCE]` 부착

산출물 보고서 상단 자동 배너:

```
> ⚠️ Single-engine review: 이 검증은 동일 모델이 수행했습니다.
> Codex 또는 Opus 리뷰가 없으므로 P0·P1 항목은 사용자 확인을 권장합니다.
```

P0·P1 패치 적용 전 사용자에게 한 번 확인을 받는다 (1·2순위는 자동, 3순위만 확인 단계 추가).

각 모드 파이프라인 문서가 검증·수정 단계의 세부 명세를 포함한다.

## 엔진 설정

### 위치

```
프로젝트별 (우선 적용): {project_root}/.claude/sprote/engine.json
플러그인 기본값 (폴백):  ${CLAUDE_PLUGIN_ROOT}/skills/sprote/engine.json
```

### 설정 키 (v2.2.0+)

| 키 | 값 | 설명 |
|----|----|------|
| `orchestrator_model` | `opus` / `sonnet` / `haiku` | 메인 작업 모델 |
| `runtime` | `auto` / `claude` / `ollama` / `compatible_cli` | 런타임 자기 신고 |
| `capabilities.codex_cli` | `true` / `false` / `auto` | codex CLI 가용성 |
| `capabilities.opus_review` | `true` / `false` / `auto` | Anthropic Opus 라우팅 가용성 |
| `capabilities.subagents` | `true` / `false` / `auto` | Agent 도구 가용성 |

### 고정 분담

| 단계 | 주체 | 비고 |
|------|------|------|
| 설계·코딩·하네스 구현 | Claude (`orchestrator_model`) | 모든 환경 동일 |
| 경량 작업 (검증·문서·리서치) | Claude Haiku | subagents=false면 인라인 |
| **리뷰·수정** | **폴백 체인** (아래) | capability 따라 자동 결정 |

### 리뷰 폴백 체인

```
1순위: capabilities.codex_cli = true
       → codex-rescue 서브에이전트 (또는 codex CLI 직접 호출)
       → workspace-write sandbox에서 P0·P1 자동 패치

2순위: codex_cli = false AND opus_review = true
       → advisor 메커니즘으로 Opus 호출 (구조화 권고 반환)
       → Sonnet 오케스트레이터가 권고를 받아 Edit/Write로 P0·P1 패치 적용
       → validator 1회 재호출로 회귀 차단

3순위: 둘 다 false (로컬 LLM 단독)
       → 동일 모델 재호출 (red-team 역할 강제, 체크리스트 6차원)
       → 컨텍스트 격리: 산출물만 입력, 이전 reasoning 제외
       → 구조화 출력 (JSON 스키마) 강제
       → 산출물에 "⚠️ Single-engine review" 신뢰도 배너 자동 삽입
       → P0·P1 항목은 사용자 확인 권장
```

### Capability 자동 감지 (auto 값)

setup 스킬 Phase 0이 다음을 수행:

| Capability | 감지 방법 |
|-----------|----------|
| `codex_cli` | `which codex` 종료 코드 |
| `opus_review` | 가용 도구 목록에 `advisor` 또는 `Agent` + Anthropic 환경 |
| `subagents` | `Agent` 도구 시그니처 존재 여부 |

`auto` 값을 명시 boolean(`true`/`false`)으로 치환하여 engine.json 갱신.

### 설정 변경

```bash
# 프로젝트별 설정 생성
echo '{"orchestrator_model": "sonnet", "runtime": "auto", "capabilities": {"codex_cli": "auto", "opus_review": "auto", "subagents": "auto"}}' \
  > {project}/.claude/sprote/engine.json

# orchestrator_model 변경 시 세션 모델도 맞춰야 함
# /model <값> 실행
```

### Deprecated: engine_mode

기존 `engine_mode` 필드(`codex_analysis`·`opus_analysis`)는 v2.2.0부터 **deprecated**.
- 발견 시 한 번 안내 후 무시
- 동작은 폴백 체인이 자동 결정
- setup 재실행 시 자동 제거

Python 미가용 환경에서는 `references/native-fallback.md` 참조.

## 외부 plugin 위임 (bridge 모드)

setup 스킬이 감지한 외부 plugin(gstack 등)이 있으면 `bridge` 스킬을 통해 namespaced 호출이 가능하다:

```
Skill(skill: "gstack:qa")
Skill(skill: "gstack:ship")
```

자세한 사항은 `bridge` 스킬 참조. 외부 plugin이 설치되지 않은 경우 fallback 메시지를 표시한다.

## 트러블슈팅

### 모드 분기 실패

- 입력에 여러 모드 키워드가 섞여 있음 → `AskUserQuestion`으로 우선 모드 결정
- 새로운 작업 유형 → 사용자에게 가장 가까운 모드 추천 후 확인

### 에이전트 실행 실패

- Codex 미설치 → REVIEW 폴백 체인이 자동으로 `opus_advisor` 또는 `self_review`로 강등 (sprote-standards §9.3)
- 서브에이전트 타임아웃 → `_workspace/` 부분 산출물 확인 후 재시작 가능 여부 판단

### 산출물 검증 실패

- validator·cross-validator 보고서를 사용자에게 우선 전달
- 양쪽이 동의한 항목은 필수 수정, 단독 발견은 신뢰도 표기

## 에이전트 인벤토리

전체 에이전트 30개의 역할·엔진은 `docs/FILES.md` 참조. 모드별 에이전트 매핑은 각 `references/{mode}-pipeline.md`에 명세된다.

## 가치 명제

- **브랜드 통합**: 모든 작업은 sprote 하나로 진입
- **on-demand 로딩**: 라우터 스킬이 SKILL.md 250줄 + 필요한 references만 Read
- **단일 출력**: `_workspace/`로 산출물 일관 관리
- **외부 plugin 친화**: bridge skill로 gstack 등과 협업
