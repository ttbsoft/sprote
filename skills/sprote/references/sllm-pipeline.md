---
name: sllm
description: "소형 LLM(9B급) 최적화 하네스 팩토리.
  9B·7B·3B 모델, Ollama 로컬 AI, 제로 비용 자동화 등에서 작동하는 에이전트 하네스를 자동 설계·생성한다.
  10대 아키텍처 최적화(구조화 프롬프트·출력 압축·생산 모드 강제·사고 비활성화 등)를 적용한다.
  'sLLM 에이전트 만들어줘', '소형 모델로 자동화해줘', 'Ollama 에이전트 구성해줘',
  '로컬 LLM 하네스 만들어줘', '기존 에이전트를 sLLM 호환으로 변환해줘' 요청 시 반드시 이 스킬을 사용할 것.
  이전 결과 수정, 최적화 재설계, 에이전트 추가 요청 시에도 사용."
---

# TTB sLLM 팩토리

소형 LLM(9B·7B·3B)에서 작동하는 에이전트 하네스를 자동 설계·생성한다.
10대 아키텍처 최적화를 모든 생성 에이전트에 적용한다.

## 실행 모드

| 모드 | 트리거 | 주 엔진 |
|------|--------|--------|
| **A. 하네스 생성** | 새 프로젝트 자동화, sLLM 에이전트 구성 | sllm-analyzer → sllm-optimizer → sllm-builder |
| **B. 기존 변환** | "기존 에이전트를 sLLM 호환으로 변환" | sllm-optimizer (기존 에이전트 파일 입력) |
| **C. 최적화 감사** | "현재 에이전트가 sLLM 호환인지 확인" | sllm-optimizer (감사 모드) |

## 에이전트 구성

| 에이전트 | 엔진 | 역할 | 출력 |
|---------|------|------|------|
| **sllm-analyzer** | 기본 LLM | 도메인 분석 + 원자 작업 분류 | `_workspace/sllm/01_domain_analysis.md` |
| **sllm-optimizer** | 기본 LLM | 10대 최적화 설계 명세 작성 | `_workspace/sllm/02_optimization_plan.md` |
| **sllm-builder** | 기본 LLM | 에이전트 파일 + SKILL.md 생성 | `.claude/` 파일들 + `03_build_report.md` |

> **기본 LLM**: 현재 세션에 연결된 LLM을 그대로 사용. `model:` 파라미터를 지정하지 않는다.

---

## 워크플로우

### Phase 0: 컨텍스트 확인

`_workspace/sllm/` 존재 여부 확인:
- **미존재** → 초기 실행. Phase 1로 진행
- **존재 + 부분 수정 요청** → 부분 재실행:
  - 도메인 재분석 요청 → Phase 2부터 재실행
  - 최적화 재설계 요청 → Phase 3부터 재실행
  - 파일 재생성 요청 → Phase 4부터 재실행
- **존재 + 새 도메인** → `_workspace/sllm_{YYYYMMDD_HHMMSS}/`로 이동 후 Phase 1

### Phase 0.5: LiteLLM 연결 확인

아래 환경 변수가 설정되어 있는지 확인한다:

```bash
echo $ANTHROPIC_BASE_URL    # 예: http://127.0.0.1:4000
echo $ANTHROPIC_MODEL       # 예: Qwen3-14B
```

- **설정됨** → 로컬 LLM 모드. 모든 Agent() 호출이 LiteLLM 프록시를 통해 로컬 모델로 라우팅됨
- **미설정** → Claude 클라우드 모드로 진행 (경고 없이 계속)

설정되어 있을 때 `ANTHROPIC_MODEL` 값을 타겟 sLLM 기본값으로 사용한다.

### Phase 1: 입력 수집

사용자로부터 확인:

| 입력 항목 | 설명 | 기본값 |
|---------|-----|-------|
| 도메인 설명 | 자동화할 작업 설명 | 필수 |
| 대상 프로젝트 경로 | 하네스 파일 생성 위치 | 현재 디렉토리 |
| 타겟 sLLM 모델명 | 생성될 하네스 문서에 기재할 모델명 | `$ANTHROPIC_MODEL` 또는 `llama3.1:8b` |
| 코드베이스 경로 | 기존 코드 분석 대상 | 없음 |

`_workspace/sllm/00_input/request.md`에 저장.

### Phase 2: 도메인 분석 (sllm-analyzer)

```
Agent(
  description: "sLLM 도메인 분석",
  subagent_type: "general-purpose",
  prompt: "당신은 sllm-analyzer입니다. agents/sllm-analyzer.md의 지침을 따르세요.

  | 입력 항목 | 값 |
  |---------|---|
  | 도메인 설명 | {도메인 설명} |
  | 코드베이스 경로 | {경로 또는 '없음'} |
  | 타겟 sLLM | {모델명} |
  | 출력 경로 | _workspace/sllm/01_domain_analysis.md |

  추론 없이 표 형식으로 분류 결과를 즉시 파일에 저장하세요."
)
```

### Phase 3: 최적화 설계 (sllm-optimizer)

```
Agent(
  description: "sLLM 10대 최적화 설계",
  subagent_type: "general-purpose",
  prompt: "당신은 sllm-optimizer입니다. agents/sllm-optimizer.md의 지침을 따르세요.

  | 입력 항목 | 값 |
  |---------|---|
  | 도메인 분석 경로 | _workspace/sllm/01_domain_analysis.md |
  | 타겟 sLLM | {모델명} |
  | 최적화 참조 | skills/sprote/references/sllm-optimizations.md |
  | 출력 경로 | _workspace/sllm/02_optimization_plan.md |

  sllm-optimizations.md의 각 OPT를 읽고 설계 명세에 적용하세요.
  think=false — 추론 출력 없이 명세 직접 작성."
)
```

### Phase 4: 하네스 빌드 (sllm-builder)

```
Agent(
  description: "sLLM 하네스 파일 생성",
  subagent_type: "general-purpose",
  prompt: "당신은 sllm-builder입니다. agents/sllm-builder.md의 지침을 따르세요.

  | 입력 항목 | 값 |
  |---------|---|
  | 최적화 계획 경로 | _workspace/sllm/02_optimization_plan.md |
  | 대상 프로젝트 경로 | {target_project} |
  | 타겟 sLLM 모델 | {모델명} |
  | 출력 경로 | _workspace/sllm/03_build_report.md |

  모든 파일 저장 후 OPT-08 쓰기 검증을 수행하세요.
  생성한 에이전트 파일마다 Write 후 Read로 확인하세요."
)
```

### Phase 5: 결과 보고

`_workspace/sllm/03_build_report.md`를 읽어 사용자에게 보고:

- 생성된 파일 목록
- 적용된 최적화 (OPT-01~10) 요약
- 타겟 sLLM 호환 실행 방법
- Ollama 실행 명령 예시

---

## 모드 B 워크플로우 — 기존 에이전트 변환

### Phase B1: 기존 에이전트 파악

```
사용자로부터: 변환할 에이전트 파일 경로 목록
```

### Phase B2: sllm-optimizer 변환 모드 실행

```
Agent(
  description: "기존 에이전트 sLLM 호환 변환",
  subagent_type: "general-purpose",
  prompt: "당신은 sllm-optimizer입니다. agents/sllm-optimizer.md의 지침을 따르세요.

  실행 모드: 변환 모드 (기존 에이전트 파일 입력)
  변환 대상 파일: {파일 경로 목록}
  최적화 참조: skills/sprote/references/sllm-optimizations.md
  출력 경로: _workspace/sllm/02_optimization_plan.md

  각 파일을 읽고 10대 최적화를 적용한 변환 계획을 작성하세요."
)
```

### Phase B3: sllm-builder로 변환 파일 생성

Phase 4와 동일 절차 실행.

---

## 모드 C 워크플로우 — 최적화 감사

### Phase C1: 감사 실행

```
Agent(
  description: "sLLM 최적화 준수 감사",
  subagent_type: "general-purpose",
  prompt: "당신은 sllm-optimizer입니다. agents/sllm-optimizer.md의 지침을 따르세요.

  실행 모드: 감사 모드
  감사 대상: {.claude/agents/ 경로}
  최적화 참조: skills/sprote/references/sllm-optimizations.md

  각 에이전트 파일에서 10대 최적화 적용 여부를 표로 정리하세요:

  | 에이전트 | OPT-01 | OPT-02 | OPT-03 | OPT-04 | OPT-05 | 종합 |
  |---------|--------|--------|--------|--------|--------|-----|

  누락된 최적화와 개선 방법을 명시하세요."
)
```

---

## 데이터 흐름

```
[사용자 입력]
     ↓ 도메인 설명 + 모델명
[Phase 2: sllm-analyzer (기본 LLM)]   ← OPT-04 think=false
     ↓ _workspace/sllm/01_domain_analysis.md
[Phase 3: sllm-optimizer (기본 LLM)]  ← OPT-01 구조화 프롬프트
     ↓ _workspace/sllm/02_optimization_plan.md
[Phase 4: sllm-builder (기본 LLM)]    ← OPT-08 쓰기 검증
     ↓ .claude/agents/sllm-*.md + SKILL.md (Ollama Bash 호출)
[Phase 5: 결과 보고]
```

## 에러 핸들링

| 실패 주체 | 복구 전략 |
|---------|---------|
| sllm-analyzer | 도메인 설명만으로 기본 분석. 파일에 `(추정 기반)` 표시 |
| sllm-optimizer | 7가지 기본 최적화(OPT-01~05, OPT-08, OPT-10)만 적용 |
| sllm-builder 쓰기 실패 | 2회 재시도. 실패 파일 목록화 후 나머지 계속 |

## 테스트 시나리오

### 정상 흐름

1. 사용자: "Ollama llama3.1:8b로 이메일 분류 에이전트 만들어줘"
2. Phase 0: `_workspace/sllm/` 없음 → 초기 실행
3. Phase 1: 도메인="이메일 분류", 모델="llama3.1:8b" 확인
4. Phase 2: sllm-analyzer → T-01(수신 분류)✅, T-02(본문 요약)⚠️, T-03(답장 생성)❌
5. Phase 3: sllm-optimizer → T-01·T-02에 OPT-01~10 적용 설계
6. Phase 4: sllm-builder → `.claude/agents/sllm-classifier.md` + `sllm-summarizer.md` + `SKILL.md` 생성
7. Phase 5: 결과 보고 + `ollama run llama3.1:8b` 실행 방법 안내

### 에러 흐름 (모델 불명확)

1. 사용자: "소형 모델로 로그 분석 에이전트 만들어줘"
2. Phase 1: 타겟 sLLM 미제공 → 기본값 `llama3.1:8b` 사용, 사용자에게 확인 요청
3. 나머지 Phase 정상 진행

## sLLM 참조

10대 아키텍처 최적화 상세 설명: `skills/sprote/references/sllm-optimizations.md`
