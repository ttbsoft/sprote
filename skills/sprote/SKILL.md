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

### Step 4 — 표준 검증 + 자동 수정

작업 완료 시 다음 검증·수정을 수행한다:

| 단계 | 에이전트 | 엔진 | 권한 |
|------|---------|------|------|
| 형식 검증 (read-only) | `validator` | Haiku | 보고서만 작성 |
| 의미 검증 + 수정 (harness 모드) | `harness-cross-validator` | **Codex (write 권한)** | 리뷰 보고서 작성 + 발견된 문제 직접 패치 |
| 디자인 검증 + 수정 (design 모드) | `design-cross-validator` | **Codex (write 권한)** | 리뷰 보고서 작성 + 발견된 문제 직접 패치 |

**Codex 리뷰+수정 동작 원칙**:

1. 먼저 리뷰 보고서를 `_workspace/05_cross_validation_report.md`(harness) 또는 `_workspace/cross_validation_report.md`(design)에 작성
2. 보고서의 P0·P1 항목은 직접 코드 패치를 적용 — 적용한 변경을 보고서 하단에 `## Applied Patches` 섹션으로 기록
3. P2·P3 항목은 보고서에 권고만 남기고 사용자 결정에 위임
4. 패치 적용 후 형식 검증(`validator`)을 1회 더 호출하여 회귀 차단
5. 모든 패치 내역은 git diff로 추적 가능해야 함 — 적용된 파일 경로를 보고서에 명시

**안전장치**:

- Codex sandbox는 `workspace-write` 모드로 실행 (저장소 외부 쓰기 금지)
- 패치 범위는 cross-validator가 발견한 결함의 직접 원인 파일로 제한
- 무관한 리팩토링·스타일 변경 금지 (외과적 변경 원칙 준수)
- 패치 후 회귀 발생 시 사용자에게 즉시 보고

각 모드 파이프라인 문서가 검증·수정 단계의 세부 명세를 포함한다.

## 엔진 설정

### 위치

```
프로젝트별 (우선 적용): {project_root}/.claude/sprote/engine.json
플러그인 기본값 (폴백):  ${CLAUDE_PLUGIN_ROOT}/skills/sprote/engine.json
```

### 설정 키

| 키 | 값 | 설명 |
|----|----|------|
| `orchestrator_model` | `opus` / `sonnet` / `haiku` | 오케스트레이터 실행 모델 |
| `engine_mode` | `codex_analysis` (기본) / `opus_analysis` | 분석/구현 엔진 조합 |

### 엔진 모드별 역할 분담

**codex_analysis (기본값)**

| 엔진 | 담당 |
|------|------|
| Codex (`codex:codex-rescue`) | 도메인 분석, 청사진 설계, 교차 검증 |
| Claude Sonnet | 하네스 파일 구현 (builder), 리더 관리 |
| Claude Haiku | 경량 작업: 리서치, 문서화, 형식 검증 |
| Claude Opus | Codex 미설치 시 분석·청사진 대체 실행 (`general-purpose`) |

> Codex 미설치 시: 도메인 분석·청사진은 Opus가 대체하고, 교차 검증은 생략한다.

**opus_analysis**

| 엔진 | 담당 |
|------|------|
| Claude Opus (`general-purpose`) | 도메인 분석, 청사진 설계, 교차 검증 |
| Codex (`codex:codex-rescue`) | 하네스 파일 구현 |
| Claude Sonnet | 리더 관리 |
| Claude Haiku | 경량 작업 |

### 설정 변경

```bash
# 프로젝트별 설정 생성
echo '{"orchestrator_model": "sonnet", "engine_mode": "codex_analysis"}' \
  > {project}/.claude/sprote/engine.json

# orchestrator_model 변경 시 세션 모델도 맞춰야 함
# /model <값> 실행
```

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

- Codex 미설치 → `engine_mode` 폴백 동작 확인 (`references/native-fallback.md`)
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
