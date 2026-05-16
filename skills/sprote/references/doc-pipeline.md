# Doc Pipeline (sprote doc 모드)

> 릴리스 노트·코드 리뷰 요약·CHANGELOG·기술 블로그 초안 생성. 단일 에이전트(doc-generator) 경량 흐름.

## 사전 조건

- 권한 사전 체크 완료 (라우터 SKILL.md Step 3까지)
- 소스 데이터 (git log·PR·diff·구현 설명) 확보

## Phase C1: 문서 유형 확인

사용자 요청에서 `doc_type`과 필요한 소스 데이터를 파악한다.

| 요청 패턴 | doc_type | 필요 데이터 |
|---------|---------|----------|
| 릴리스 노트, 배포 문서 | `release_notes` | git log 범위 또는 PR 목록 |
| 코드 리뷰 요약, PR 리뷰 | `code_review` | PR URL 또는 diff |
| 변경점 정리, CHANGELOG | `changelog` | 커밋 범위 |
| 기술 블로그, 포스트 초안 | `blog_draft` | 구현 설명 또는 코드 |

소스 데이터가 부족하면 사용자에게 먼저 요청한다.

## Phase C2: doc-generator 실행

```
Agent(
  description: "문서 초안 생성",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "당신은 doc-generator입니다. agents/doc-generator.md의 지침을 따르세요.
           project_root: {프로젝트 경로}
           doc_type: {release_notes | code_review | changelog | blog_draft}
           source_data: {원본 데이터}
           output_path: {출력 파일 경로}

           artisan 품질 기준으로 문서를 직접 작성하고 output_path에 저장하세요."
)
```

## Phase C3: 결과 보고

생성된 문서 경로와 주요 작성 내용을 사용자에게 보고한다.

## 데이터 흐름

```
[사용자 요청 + 소스 데이터]
     ↓
[Phase C2: doc-generator (Sonnet)]
  ├─ release_notes → 버전·하이라이트·변경점·마이그레이션 가이드
  ├─ code_review   → 발견 사항·심각도·권고
  ├─ changelog     → 카테고리별 변경 (feat·fix·chore)
  └─ blog_draft    → 도입·문제·해법·결과·향후 방향
     ↓
최종 문서 파일 (Write 저장)
```

## 참조

- 에이전트 정의: `agents/doc-generator.md`
