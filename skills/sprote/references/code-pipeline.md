# Code Pipeline (sprote code 모드)

> 파일 검색·간단 수정·로그 분석·테스트 실패 원인 요약. 단일 에이전트(code-worker)로 빠르게 처리하고 에스컬레이션은 오케스트레이터가 직접 처리한다.

## 사전 조건

- 권한 사전 체크 완료 (라우터 SKILL.md Step 3까지)
- engine.json 로딩은 선택 (code 모드는 단일 에이전트 경량 흐름)

## Phase B1: 작업 유형 확인

사용자 요청에서 `task_type`과 `project_root`를 파악한다.

| 요청 패턴 | task_type |
|---------|---------|
| 파일 찾아줘, 어디 있어, 검색해줘 | `file_search` |
| 수정해줘, 바꿔줘, 리팩토링 | `simple_modify` |
| 로그 분석, 에러 패턴, 오류 빈도 | `log_analysis` |
| 테스트 실패, 실패 원인, 왜 떨어져 | `test_failure` |

## Phase B2: code-worker 실행

```
Agent(
  description: "로컬 코드 작업",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "당신은 code-worker입니다. agents/code-worker.md의 지침을 따르세요.
           project_root: {프로젝트 경로}
           task_type: {file_search | simple_modify | log_analysis | test_failure}
           target: {대상 파일·디렉터리·로그}
           request: {사용자 요청 원문}

           에스컬레이션 조건이 감지되면 즉시 작업을 중단하고 이유를 반환하세요."
)
```

## Phase B3: 파일 수정 후 docs-keeper 실행

`task_type`이 `simple_modify`이고 code-worker가 실제로 파일을 수정한 경우에만 실행한다.
`file_search`, `log_analysis`, `test_failure`는 파일을 변경하지 않으므로 스킵한다.

```
Agent(
  description: "수정 파일 docs/FILES.md 갱신",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "당신은 docs-keeper입니다. agents/docs-keeper.md의 지침을 따르세요.
           project_root: {프로젝트 경로}
           changed_files:
             - action: modified
               path: {code-worker가 수정한 파일 경로}
               summary: {code-worker 반환값에서 추출한 변경 요약}
               change_reason: {사용자 요청 원문}
           완료 후 갱신된 docs/FILES.md 경로를 반환하세요."
)
```

## Phase B4: 에스컬레이션 처리

code-worker가 에스컬레이션을 반환하면 오케스트레이터(Claude)가 직접 처리한다.

에스컬레이션 트리거:
- 아키텍처 판단 필요
- 복잡한 리팩토링 (여러 파일 영향)
- 테스트 수정 (구현 변경이 정당한지 판단 필요)
- 보안·성능 트레이드오프

## 데이터 흐름

```
[사용자 요청]
     ↓
[Phase B2: code-worker (Claude Haiku)]
  ├─ file_search   → 파일 목록 + 코드 스니펫
  ├─ simple_modify → 수정된 파일
  ├─ log_analysis  → 오류 패턴 분류표
  └─ test_failure  → 실패 원인 요약 + 수정 힌트
     ↓ 에스컬레이션 감지 시
[Claude 직접 처리]
     ↓ simple_modify 성공 시
[Phase B3: docs-keeper (Haiku)]
  └─ docs/FILES.md 갱신
```

## 참조

- 에이전트 정의: `agents/code-worker.md`, `agents/docs-keeper.md`
