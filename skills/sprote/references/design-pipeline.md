---
name: design
description: "TTB 전용 UI/UX 디자인 자동화 팩토리.
  TTB·ttb·티티비 프로젝트에서 디자인 관련 요청 시 반드시 이 스킬을 사용할 것.
  artisan 원칙 기반으로 기획·구현·검토·교차검증을 자동화한다.
  트리거 조건: '티티비 UI 만들어줘', '티티비 디자인 검토해줘',
  '티티비 AI 안 티나게 개선해줘', '티티비 교차 검증해줘',
  '기존 페이지 리디자인해줘', '랜딩페이지 업그레이드해줘' 등.
  이전 결과 수정, 재설계, 개선 요청 시에도 사용."
---

# TTB Design Factory

디자인 컨텍스트 수집 → UX/UI 기획 → 구현 → 품질 검토의 전 과정을 자동화한다.
장인 정신(artisan) 기반 설계 원칙을 TTB 표준 워크플로우에 통합한 디자인 팩토리.

두 가지 실행 경로로 동작한다: **신규 생성** 또는 **리디자인(기존 페이지 업그레이드)**.

## 실행 모드

### 신규 생성 (기본)
| Phase | 모드 | 에이전트 | 엔진 | 역할 |
|-------|------|---------|------|------|
| Phase 1 (컨텍스트 수집) | 인라인 | — | — | 사용자와 직접 대화 |
| Phase 1.5 (외부 리서치) | 서브 에이전트 | search-analyst | **Haiku** | Brave Search 트렌드 수집 |
| Phase 2 (UX/UI 기획) | 서브 에이전트 | design-planner | **Codex** | 리서치 기반 브리프 설계 |
| Phase 3 (구현) | 서브 에이전트 | design-implementer | **Sonnet** | 코드 생성 + Haiku 검증 루프 |
| Phase 4 (품질 검토) | 서브 에이전트 | design-reviewer | **Opus** | 독립적 검토 |
| Phase 5 (교차 검증) | 서브 에이전트 | design-cross-validator | Opus + **Codex** | AI 편향 제거 판정 |

### 리디자인 (기존 페이지 업그레이드)
| Phase | 모드 | 역할 |
|-------|------|------|
| Phase R1 (감사) | 인라인 | 기존 파일 분석, 24항목 감사 |
| Phase R2 (개선 계획) | 서브 에이전트 | design-planner가 개선 브리프 작성 |
| Phase R3 (단계적 수정) | 서브 에이전트 | design-implementer가 우선순위 순서로 수정 |
| Phase R4 (검토) | 서브 에이전트 | design-reviewer → design-cross-validator |

**리디자인 트리거:** "리디자인해줘", "기존 페이지 개선해줘", "업그레이드해줘", "이 HTML 고쳐줘"

## 에이전트 구성

| 에이전트 | 타입 | 엔진 | 역할 | 출력 |
|---------|------|------|------|------|
| search-analyst | `general-purpose` | **Claude Haiku** | Brave Search 트렌드 리서치 | `_workspace/design/00_research.md` |
| design-planner | `codex:codex-rescue` | **Codex** | 리서치 기반 UX/UI 기획 + 디자인 브리프 | `_workspace/design/01_brief.md` |
| design-implementer | `general-purpose` | **Claude Sonnet** | 브리프 기반 UI 코드 생성 | 소스 파일 + `_workspace/design/02_build_report.md` |
| code-validator | `general-purpose` | **Claude Haiku** | 파일별 artisan 규칙 검증 | 인라인 결과 (MODIFY_HINTS) |
| design-reviewer | `general-purpose` | **Claude Sonnet** | 시각적 품질·접근성·안티패턴 검토 | `_workspace/design/03_review_report.md` |
| design-cross-validator | `general-purpose` | Claude Sonnet + Codex | Claude·Codex 교차 검증 + 전문 디자이너 감수성 판정 | `_workspace/design/04_cross_validation_report.md` |

## 워크플로우

### Phase 0: 컨텍스트 확인

1. `_workspace/design/` 디렉토리 존재 여부 확인
2. **[harness 모드 연계]** `_workspace/02_blueprint.md` 존재 여부 확인:
   - 존재하면 → harness 모드가 이미 실행된 상태. 하네스 아키텍처 컨텍스트를 design-planner에 전달
   - 미존재 → 독립 실행 모드 (연계 없음)
3. 실행 모드 결정:
   - **`_workspace/design/` 미존재** → 초기 실행. Phase 1로 진행
   - **`_workspace/design/` 존재 + 부분 수정 요청** → 부분 재실행:
     - 기획 재요청 → Phase 2부터 재실행
     - 구현 재요청 → Phase 3부터 재실행
     - 검토만 → Phase 4만 재실행
     - 교차검증만 → Phase 5만 재실행
   - **새 디자인 작업** → `_workspace/design_{YYYYMMDD_HHMMSS}/`로 이동 후 초기 실행
3. `.artisan.md` 존재 여부 확인:
   - 존재하면 디자인 컨텍스트 로드 → Phase 1 스킵 가능
   - 미존재 시 Phase 1 필수 실행
4. 교차 검증 실행 여부 확인:
   - 기본값: Phase 4 완료 후 항상 Phase 5 실행
   - 사용자가 "빠르게", "검토 생략", "교차검증 생략" 명시 시 → Phase 5 스킵 가능
   - 단, 최종 판정이 NEEDS_REVISION인 경우 Phase 5 스킵 불가

### Phase 1: 디자인 컨텍스트 수집

`.artisan.md`가 없거나 불완전한 경우 사용자에게 직접 질문한다.

**필수 확인 항목:**

```
1. 대상 사용자: 누가, 어떤 상황에서 사용하는가?
2. 브랜드 퍼스낼리티: 3단어로 표현하면?
3. 시각적 방향: 미니멀 / 볼드 / 에디토리얼 / 럭셔리 / 레트로 등
4. 라이트/다크 모드 선호 여부
5. 참고할 레퍼런스 사이트 (있으면)
6. 설계 변수 (미응답 시 기본값 사용):
   - DESIGN_VARIANCE 1–10 (기본 5): 대칭·보수적 ↔ 비대칭·실험적
   - MOTION_INTENSITY 1–10 (기본 5): 정적 ↔ 시네마틱 애니메이션
   - VISUAL_DENSITY 1–10 (기본 4): 럭셔리·여유 ↔ 데이터 밀집
   - LANDING_PURPOSE: conversion(기본) / brand / portfolio / saas / ecommerce
```

수집 완료 후 `.artisan.md`에 저장:

```markdown
## Design Context

### Users
[대상 사용자, 사용 컨텍스트, 주요 태스크]

### Brand Personality
[보이스, 톤, 3단어 퍼스낼리티, 감정적 목표]

### Aesthetic Direction
[시각적 톤, 레퍼런스, 안티-레퍼런스, 테마]

### Design Principles
[모든 디자인 결정을 이끌 3-5개 원칙]
```

### Phase 1.5: 외부 리서치 (Brave Search)

**실행 모드:** 서브 에이전트 (Claude Haiku)

`_workspace/design/00_research.md`가 이미 있으면 스킵한다.

```
Agent(
  description: "디자인 트렌드 외부 리서치",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "당신은 search-analyst입니다. agents/search-analyst.md의 지침을 따르세요.
           .artisan.md를 읽어 브랜드·도메인·대상 사용자를 파악한 후 아래 4개 쿼리를 실행하세요:
           1. '{제품 카테고리} UI UX design trends {현재 연도}'
           2. '{유사 서비스 또는 경쟁사} interface design examples'
           3. '{대상 사용자 유형} UX best practices {현재 연도}'
           4. '{핵심 기능} design pattern accessibility'

           Brave Search MCP 우선. 미설정 시 WebSearch로 폴백.
           결과를 _workspace/design/00_research.md에 저장하세요."
)
```

### Phase 1.8: Codex 가용성 확인

```bash
which codex
```

- **설치 확인 시**: Phase 2는 Codex로 실행, Phase 5(교차 검증) 실행
- **미설치 시**: Phase 2는 Claude Opus로 실행, **Phase 5 생략**

### Phase 2: UX/UI 기획

**Codex 설치 시:**
```
Agent(
  description: "UX/UI 디자인 기획",
  subagent_type: "codex:codex-rescue",
  model: "opus",
  prompt: "당신은 design-planner입니다. agents/design-planner.md의 지침을 따르세요.
           디자인 컨텍스트: .artisan.md
           외부 리서치 결과: _workspace/design/00_research.md
           디자인 요청: {사용자 요청 원문}
           대상 프로젝트 경로: {프로젝트 경로}
           [연계] 하네스 청사진: _workspace/02_blueprint.md (존재하면 읽어서 컨텍스트 활용)
           디자인 브리프를 작성하고 _workspace/design/01_brief.md에 저장하세요."
)
```

**Codex 미설치 시:**
```
Agent(
  description: "UX/UI 디자인 기획 (Claude Opus)",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 design-planner입니다. agents/design-planner.md의 지침을 따르세요.
           디자인 컨텍스트: .artisan.md
           외부 리서치 결과: _workspace/design/00_research.md
           디자인 요청: {사용자 요청 원문}
           대상 프로젝트 경로: {프로젝트 경로}
           [연계] 하네스 청사진: _workspace/02_blueprint.md (존재하면 읽어서 컨텍스트 활용)
           디자인 브리프를 작성하고 _workspace/design/01_brief.md에 저장하세요."
)
```

### Phase 3: 구현

**실행 모드:** 서브 에이전트 (Claude)

파일마다 Haiku 서브 에이전트(`code-validator`)로 artisan 검증 후 후처리한다.

```
Agent(
  description: "디자인 브리프 기반 UI 구현",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "당신은 design-implementer입니다. agents/design-implementer.md의 지침을 따르세요.
           디자인 브리프: _workspace/design/01_brief.md
           디자인 원칙 레퍼런스: skills/sprote/references/design-principles.md (기술 스택·설계 변수·금지 패턴 포함)
           대상 프로젝트 경로: {프로젝트 경로}
           설계 변수: DESIGN_VARIANCE={값} MOTION_INTENSITY={값} VISUAL_DENSITY={값} LANDING_PURPOSE={값}

           [출력 완전성 강제]
           - 플레이스홀더·TODO·생략 주석 절대 금지 (<!-- ... -->, // ..., [내용 동일] 등)
           - 모든 섹션을 실제 한국어 콘텐츠로 완성할 것
           - 토큰 한계 시 섹션 압축 금지 — 종료 지점에서 [PAUSED] 태그 후 중단
           - 기본 기술 스택: Tailwind CDN + Pretendard + Iconify Solar (MOTION_INTENSITY>5이면 Motion One 추가)

           파일 생성 시 Write/Edit 도구를 사용하세요.
           파일마다 Haiku code-validator 서브 에이전트를 실행하여
           artisan 규칙 위반을 검증하고 결과에 따라 수정 또는 재작성하세요.
           (agents/design-implementer.md Step 5-D, 5-E 참조)

           브리프에 따라 UI를 구현하고 _workspace/design/02_build_report.md를 작성하세요."
)
```

**모델 역할 분리:**

| 모델 | 역할 |
|------|------|
| Haiku 4.5 | artisan 규칙 검증 (`code-validator`) |
| Sonnet 4.6 | 코드 작성, 후처리 판단, REWRITE |

### Phase 4: 품질 검토

**실행 모드:** 서브 에이전트 (Claude)

```
Agent(
  description: "디자인 품질 검토",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 design-reviewer입니다. agents/design-reviewer.md의 지침을 따르세요.
           빌드 보고서: _workspace/design/02_build_report.md
           디자인 브리프: _workspace/design/01_brief.md
           디자인 원칙 레퍼런스: skills/sprote/references/design-principles.md
           대상 프로젝트 경로: {프로젝트 경로}
           품질 검토 후 _workspace/design/03_review_report.md를 작성하세요."
)
```

### Phase 5: Claude·Codex 교차 검증 (Codex 설치 시에만 실행)

**Codex 미설치 시: 이 단계를 완전히 생략하고 Phase 6으로 바로 이동한다.**

**실행 모드:** 서브 에이전트 (Claude — Codex 독립 리뷰 포함)

Phase 4의 Claude 리뷰와 Codex의 독립 리뷰를 비교하여, "AI가 만들었겠다"는 느낌을 완전히 제거한다.

```
Agent(
  description: "Claude·Codex 디자인 교차 검증",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 design-cross-validator입니다. agents/design-cross-validator.md의 지침을 따르세요.

           입력 파일:
           - Claude 리뷰: _workspace/design/03_review_report.md
           - 빌드 보고서: _workspace/design/02_build_report.md
           - 디자인 브리프: _workspace/design/01_brief.md
           - 디자인 원칙: skills/sprote/references/design-principles.md

           대상 프로젝트 경로: {프로젝트 경로}

           작업:
           1. Claude 리뷰(03_review_report.md)를 읽되 Codex에게 공유하지 않는다
           2. Codex CLI로 동일 소스 파일을 독립 리뷰한다 (agents/design-cross-validator.md의 codex_prompt 사용)
              - Codex 미설치 시: Claude 서브 에이전트로 Codex 관점 시뮬레이션
           3. 두 리뷰를 비교·분류 (BOTH_AGREE / CLAUDE_ONLY / CODEX_ONLY / DISAGREE)
           4. 전문 디자이너 감수성 8개 항목 판정
           5. _workspace/design/04_cross_validation_report.md 작성"
)
```

**Phase 5 실행 조건:**
- Codex 설치 + Phase 4 완료: 실행
- Codex 미설치: 생략
- 사용자가 명시적으로 "교차검증 생략"을 요청한 경우: 생략

### Phase 6: 결과 보고

1. 보고서 읽기:
   - `_workspace/design/04_cross_validation_report.md` 존재 시 읽기 (Phase 5 실행된 경우)
   - 없으면 `_workspace/design/03_review_report.md` 읽기 (Codex 미설치 또는 Phase 4까지만 완료)
2. 사용자에게 보고:
   - 구현된 파일 목록
   - **최종 판정:** HUMAN_QUALITY / BORDERLINE / AI_DETECTABLE
   - 디자인 헬스 스코어 (접근성·퍼포먼스·안티패턴)
   - 전문 디자이너 감수성 점수 (?/8)
   - P0/P1 이슈 + 최우선 수정 권고
   - 추천 후속 액션 (개선 요청 시 재실행 방법 포함)

## 데이터 흐름

```
[사용자 요청]
      ↓
.artisan.md (디자인 컨텍스트)
      ↓
[Phase 2: design-planner]
      ↓
_workspace/design/01_brief.md
      ↓
[Phase 3: design-implementer]
      ↓
소스 파일 + _workspace/design/02_build_report.md
      ↓
[Phase 4: design-reviewer (Claude)]
      ↓
_workspace/design/03_review_report.md
      ↓
[Phase 5: design-cross-validator]
      ├─ Claude 리뷰 읽기
      └─ Codex 독립 리뷰 실행
            ↓
_workspace/design/04_cross_validation_report.md
      ↓
[Phase 6: 결과 보고]
      ↓
최종 판정: HUMAN_QUALITY / BORDERLINE / AI_DETECTABLE
```

## 리디자인 워크플로우

기존 페이지를 처음부터 다시 만들지 않고 진단 후 목표 개선한다.

### Phase R1: 감사 (인라인)

1. 대상 파일 경로 확인 (HTML/CSS/TSX 등)
2. `design-principles.md` §16 감사 항목 24개를 순서대로 점검
3. 발견된 문제를 우선순위별로 분류:
   - **P0**: 폰트(Inter/Noto Sans KR), 색상(AI 팔레트), 출력 불완전
   - **P1**: 그래디언트 텍스트, border-left 스트라이프, 모든 요소 중앙 정렬
   - **P2**: 호버 상태 없음, 여백 불일치, 아이콘 일관성
   - **P3**: 한국어 자연스러움, 이징 함수

### Phase R2: 개선 브리프 작성

**Codex 설치 시:**
```
Agent(
  description: "리디자인 브리프 작성",
  subagent_type: "codex:codex-rescue",
  model: "opus",
  prompt: "당신은 design-planner입니다. agents/design-planner.md의 지침을 따르세요.
           감사 결과: {Phase R1 감사 결과}
           대상 파일: {파일 경로}
           디자인 원칙: skills/sprote/references/design-principles.md
           
           기존 코드를 분석하여 개선 브리프를 작성하세요:
           - 유지할 것 (브랜드 아이덴티티, 구조적 장점)
           - 교체할 것 (P0 → P1 → P2 → P3 순서)
           - 추가할 것 (누락된 프리미엄 패턴)
           _workspace/design/01_redesign_brief.md에 저장하세요."
)
```

**Codex 미설치 시:**
```
Agent(
  description: "리디자인 브리프 작성 (Claude Opus)",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "당신은 design-planner입니다. agents/design-planner.md의 지침을 따르세요.
           감사 결과: {Phase R1 감사 결과}
           대상 파일: {파일 경로}
           디자인 원칙: skills/sprote/references/design-principles.md
           
           기존 코드를 분석하여 개선 브리프를 작성하세요:
           - 유지할 것 (브랜드 아이덴티티, 구조적 장점)
           - 교체할 것 (P0 → P1 → P2 → P3 순서)
           - 추가할 것 (누락된 프리미엄 패턴)
           _workspace/design/01_redesign_brief.md에 저장하세요."
)
```

### Phase R3: 단계적 수정

```
Agent(
  description: "단계적 리디자인 구현",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "당신은 design-implementer입니다. agents/design-implementer.md의 지침을 따르세요.
           리디자인 브리프: _workspace/design/01_redesign_brief.md
           디자인 원칙: skills/sprote/references/design-principles.md
           대상 파일: {파일 경로}
           
           아래 순서로 수정하세요 (각 단계 완료 후 다음 단계 진행):
           1단계: 폰트 교체 → Pretendard + word-break: keep-all
           2단계: 색상 시스템 → OKLCH 팔레트, 악센트 1개로 통합
           3단계: 한국어 콘텐츠 → AI 클리셰 제거, 자연스러운 표현
           4단계: 호버·전환 → 서명 이징 곡선 적용
           5단계: 레이아웃 → 중앙 정렬 해소, Bento/비대칭 도입
           6단계: 애니메이션 → IntersectionObserver reveal 추가
           7단계: 최종 폴리시 → AI Slop 자가 테스트 14개 항목 확인
           
           [출력 완전성 강제] 플레이스홀더·생략 절대 금지.
           _workspace/design/02_redesign_report.md에 변경 내역 기록."
)
```

### Phase R4: 검토 (→ Phase 4, 5와 동일)

Phase R3 완료 후 일반 Phase 4 (design-reviewer) → Phase 5 (Codex 설치 시에만 실행) → Phase 6 (결과 보고)로 진행.

---

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| `.artisan.md` 없음 | Phase 1 강제 실행, 컨텍스트 없이 진행 금지 |
| design-planner 실패 | 사용자 요청 원문으로 간소화 브리프 생성 후 Phase 3 진행 |
| design-implementer 실패 | 실패 내용 빌드 보고서에 기록, 부분 구현으로 Phase 4 진행 |
| design-reviewer 실패 | 경고 후 Phase 5 생략, 사용자에게 수동 검토 요청 |
| design-cross-validator 실패 | 경고 후 03_review_report.md 기준으로 Phase 6 진행 |
| Codex 플러그인 미설치 | Phase 2, R2: Claude Opus로 대체. Phase 5: 완전 생략 |
| 리디자인 대상 파일 없음 | 파일 경로 재확인 요청 후 대기 |

## 테스트 시나리오

### 정상 흐름 (전체 파이프라인)

1. 사용자: "대시보드 UI 만들어줘. 프로젝트는 ~/my-app"
2. Phase 0: `_workspace/design/` 없음 + `.artisan.md` 없음 → Phase 1 실행
3. Phase 1: 사용자 인터뷰 → `.artisan.md` 생성 (설계 변수 포함)
4. Phase 2: design-planner → 대시보드 디자인 브리프
5. Phase 3: design-implementer → Dashboard.tsx 생성 (Pretendard + Iconify Solar + 서명 이징)
6. Phase 4: design-reviewer → 헬스 스코어 18/20, P1 이슈 1개
7. Phase 5: design-cross-validator → Claude·Codex 비교, 전문 디자이너 감수성 7/8
8. Phase 6: 결과 보고 (최종 판정: HUMAN_QUALITY) + 수정 안내

### 리디자인 흐름

1. 사용자: "이 랜딩페이지 리디자인해줘. ~/project/index.html"
2. Phase 0: 리디자인 모드 감지
3. Phase R1: 24항목 감사 → P0 2개(Inter, 시안 팔레트), P1 3개, P2 5개 발견
4. Phase R2: design-planner → 유지/교체/추가 브리프 작성
5. Phase R3: design-implementer → 7단계 순서로 수정
6. Phase 4–6: 검토 → 교차 검증 → 결과 보고

### 교차 검증에서 AI 패턴 추가 발견 시

1. Phase 4: design-reviewer → 헬스 스코어 17/20, P2 이슈만 있어 APPROVED_WITH_WARNINGS
2. Phase 5: design-cross-validator 실행
   - Codex 독립 리뷰에서 금지 폰트(Inter) 사용 추가 발견 (Claude 미감지)
   - 감수성 점수 4/8 (여백 의도성·마이크로카피 톤 FAIL)
3. Phase 5 결과: AI_DETECTABLE → NEEDS_REVISION 상향
4. Phase 6: "Phase 4 단독으로는 통과했지만 교차 검증에서 AI 패턴 발견" 보고

### 에러 흐름 (컨텍스트 미존재)

1. 사용자: "UI 만들어줘" (컨텍스트 없음)
2. Phase 0: `.artisan.md` 미존재 확인
3. Phase 1: 강제 인터뷰 실행
4. 컨텍스트 확보 후 정상 흐름 진행

## 디자인 원칙 참조

`skills/sprote/references/design-principles.md` — TTB artisan 디자인 원칙 요약.
