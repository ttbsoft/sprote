# Routing Matrix (sprote 모드 분기 가이드)

> 사용자 입력이 모호하거나 여러 모드 키워드가 섞여 있을 때 모드를 결정하는 의사결정 가이드.

## 단일 키워드 매칭

| 키워드 | 모드 | 비고 |
|--------|------|------|
| 팀 구성, 하네스, 워크플로우 자동화, 에이전트 추가, 재설계 | **harness** | |
| UI 만들기, 디자인 검토, AI 안 티나게, 시각적 품질, artisan | **design** | |
| 파일 검색, 간단히 수정, 로그 분석, 테스트 실패 원인 | **code** | 단일 파일·국소 변경에 한함 |
| 릴리스 노트, 코드 리뷰 요약, 변경점 정리, 블로그 초안 | **doc** | |
| 제품 기획, PRD, 시장 조사, 로드맵, 경쟁사 분석, INVEST | **pm** | |
| sLLM, 소형 모델 자동화, Ollama, 9B 모델 | **sllm** | |

## 복합 입력 결정 규칙

### 1. "UI 만들고 PRD도 작성" (design + pm)

기획이 우선이면 **pm 먼저 → design 후속**:

```
1. pm 모드 실행 → _workspace/pm/01_research.md ~ 04_validation.md
2. PRD 완료 후 → design 모드 실행 (PRD를 디자인 브리프 컨텍스트로 활용)
```

UI가 우선이면 design 먼저 후 PRD 보완. 사용자에게 `AskUserQuestion`으로 명시 확인.

### 2. "팀 만들고 UI도" (harness + design)

design 먼저 → harness 후속:

```
1. design 모드 → _workspace/design/01_brief.md 생성
2. harness 모드 → analysis-leader가 디자인 브리프를 컨텍스트로 활용
```

harness-pipeline.md Phase 0.5에서 디자인 브리프 자동 감지.

### 3. "수정해줘 + 릴리스 노트도" (code + doc)

code 먼저 → doc 후속:

```
1. code 모드 → 파일 수정 + docs-keeper로 FILES.md 갱신
2. doc 모드 → release_notes 또는 changelog 작성 (수정된 파일을 source_data로)
```

### 4. "에이전트 만들어줘" (harness vs sllm)

sLLM 키워드가 동반되면 **sllm**, 아니면 **harness**:

| 입력 | 모드 |
|------|------|
| "에이전트 만들어줘" | harness |
| "sLLM 에이전트 만들어줘", "9B 모델로 에이전트", "Ollama로 자동화" | sllm |

## 모호 시 명시 확인 패턴

```
AskUserQuestion(
  question: "어떤 작업을 먼저 진행할까요?",
  options: [
    {label: "{모드 A}", description: "{모드 A 산출물}"},
    {label: "{모드 B}", description: "{모드 B 산출물}"},
    {label: "둘 다 (순서: {권장 순서})", description: "{연계 흐름}"}
  ]
)
```

## 모드 매칭 실패 시

알려진 키워드 중 어느 것도 매칭되지 않으면:

1. 사용자에게 작업 유형을 추가로 묻는다
2. 가장 가까운 모드 1개를 추천하고 확인을 받는다
3. 명백히 sprote 범위 밖이면 (예: 일반 대화, 잡담) 스킬을 즉시 종료한다

## 외부 plugin 위임 분기

다음 키워드는 sprote 모드가 아닌 외부 plugin 위임:

| 키워드 | 외부 plugin | 호출 방식 |
|--------|------------|---------|
| 사이트 동작 QA, 테스트 시나리오 실행 | gstack `/qa` | `Skill(skill: "gstack:qa")` |
| 배포, ship, 릴리스 게이트 | gstack `/ship` | `Skill(skill: "gstack:ship")` |
| 시각 디자인 리뷰 (배포 단계) | gstack `/design-review` | `Skill(skill: "gstack:design-review")` |
| 컨텍스트 저장·복원 | gstack `/context-save`, `/context-restore` | namespaced |

외부 plugin이 설치되어 있지 않으면 setup 스킬이 안내 메시지를 표시한다.
