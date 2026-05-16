# 파일 인벤토리

> 마지막 갱신: 2026-05-16 (v2.0.0 sprote)
> 본 문서는 sprote 플러그인 **소스 파일** 인벤토리이다. 테스트 캐시·임시 산출물·`.git/`은 제외한다.

---

## 메타 / 루트

| 경로 | 역할 |
|------|------|
| `README.md` | 플러그인 소개, 에이전트·스킬 테이블, 파일 구조 |
| `CLAUDE.md` | 본 저장소 작업 지침 (스킬 라우팅, 코딩 행동 지침, 참조 문서 인덱스) |
| `LICENSE` | MIT License |
| `.claude-plugin/plugin.json` | 플러그인 메타데이터 (name: sprote, version 2.0.0) |
| `.claude-plugin/marketplace.json` | 마켓플레이스 메타 (sprote-marketplace) |
| `.deploy-exclude` | 배포 패키지 제외 목록 |
| `.gitignore` | git 무시 패턴 (Python 캐시 등) |
| `pytest.ini` | pytest 설정 |
| `.claude/sprote/engine.json` | **(로컬 전용)** 본 저장소를 소비 프로젝트가 참조할 때 사용되는 기본 엔진 설정. 배포 패키지에는 포함하지 않는다 |

---

## agents/ — 서브 에이전트 정의 (24개)

### 분석·빌드 파이프라인 (sprote harness 모드)

| 파일 | 역할 | 엔진 |
|------|------|------|
| `agents/analysis-leader.md` | 분석 파이프라인 자율 관리 (domain-analyst → pattern-analyst → synthesis-reviewer) | Sonnet |
| `agents/build-leader.md` | 빌드 파이프라인 자율 관리 (builder → docs-keeper ∥ validator ∥ harness-cross-validator) | Sonnet |
| `agents/domain-analyst.md` | 도메인·요구사항 분석 | Codex |
| `agents/pattern-analyst.md` | 아키텍처 청사진 설계 | Codex |
| `agents/synthesis-reviewer.md` | 도메인 분석 + 청사진 교차 검증 | Codex |
| `agents/builder.md` | 하네스 파일 생성 (SKILL.md, 에이전트 .md, 오케스트레이터) | Sonnet |
| `agents/docs-keeper.md` | docs/FILES.md 자동 유지 | Haiku |
| `agents/validator.md` | TTB 형식·표준 검증 (read-only) | Haiku |
| `agents/harness-cross-validator.md` | 청사진 의미 교차 검증 + P0·P1 자동 패치 (workspace-write) | Codex |
| `agents/search-analyst.md` | Brave Search 외부 리서치 | Haiku |
| `agents/code-worker.md` | sprote code 모드 — 파일 검색·수정·로그 분석·테스트 실패 요약 | Haiku |
| `agents/doc-generator.md` | sprote doc 모드 — 릴리스 노트·리뷰 요약·블로그 초안 | Sonnet |

### 디자인 파이프라인 (sprote design 모드)

| 파일 | 역할 | 엔진 |
|------|------|------|
| `agents/design-planner.md` | UX/UI 기획, 디자인 브리프 작성 | Sonnet (Codex 호출) |
| `agents/design-implementer.md` | 디자인 브리프 기반 UI 코드 구현 | Sonnet |
| `agents/design-reviewer.md` | 디자인 품질 검토 (artisan 기준) | Sonnet |
| `agents/design-cross-validator.md` | Claude·Codex 교차 검증 + P0·P1 자동 패치 (workspace-write) | Sonnet+Codex |
| `agents/code-validator.md` | 디자인 코드 artisan 규칙 검증 | Haiku |

### PM 파이프라인 (sprote pm 모드)

| 파일 | 역할 | 엔진 |
|------|------|------|
| `agents/research-analyst.md` | 시장·경쟁사·유저 문제 조사 (Phase 1) | Sonnet |
| `agents/prd-writer.md` | PRD 작성 (INVEST 기준) (Phase 2) | Sonnet |
| `agents/roadmap-planner.md` | 로드맵·MoSCoW·의존성 매핑 (Phase 3) | Sonnet |
| `agents/prd-validator.md` | PRD·로드맵 교차 검증 (Phase 4) | Sonnet |

### sLLM 파이프라인 (sprote sllm 모드)

| 파일 | 역할 | 엔진 |
|------|------|------|
| `agents/sllm-analyzer.md` | sLLM 호환 도메인 분석 (원자 작업 단위 식별) | Haiku |
| `agents/sllm-optimizer.md` | 10대 아키텍처 최적화 설계 | Sonnet |
| `agents/sllm-builder.md` | 최적화 계획 기반 하네스 생성 + 쓰기 검증 | Sonnet |

---

## skills/ — 사용자 진입점 스킬 (5개)

| 파일 | 트리거 |
|------|--------|
| `skills/sprote/SKILL.md` | **통합 라우터** — 6 mode 자동 분기 (harness·design·code·doc·pm·sllm) |
| `skills/setup/SKILL.md` | 권한·hook 설정 + 프로젝트 sprote 전환 (빈/기존 분기, harness 위임) |
| `skills/review/SKILL.md` | 하네스 검증·TTB 표준 확인 |
| `skills/advisor/SKILL.md` | Opus 에스컬레이션·어드바이저 호출 |
| `skills/bridge/SKILL.md` | 외부 plugin 스킬 namespaced 위임 (gstack:qa 등) |

### sprote references (14개 모듈)

| 파일 | 역할 |
|------|------|
| `skills/sprote/engine.json` | sprote 엔진 설정 기본값 (orchestrator_model, runtime, capabilities) |
| `skills/sprote/references/routing-matrix.md` | 복합 입력·외부 plugin 위임 결정 가이드 |
| `skills/sprote/references/harness-pipeline.md` | harness 모드 파이프라인 (Phase 1-4) |
| `skills/sprote/references/design-pipeline.md` | design 모드 파이프라인 |
| `skills/sprote/references/code-pipeline.md` | code 모드 파이프라인 (file_search·simple_modify·log_analysis·test_failure) |
| `skills/sprote/references/doc-pipeline.md` | doc 모드 파이프라인 (release_notes·code_review·changelog·blog_draft) |
| `skills/sprote/references/pm-pipeline.md` | pm 모드 파이프라인 (4 Phase) |
| `skills/sprote/references/sllm-pipeline.md` | sllm 모드 파이프라인 |
| `skills/sprote/references/sprote-standards.md` | sprote 표준 (Codex 연계 지침, §9 런타임 해석) |
| `skills/sprote/references/coding-guidelines.md` | 생성된 프로젝트 CLAUDE.md에 삽입되는 코딩 행동 지침 |
| `skills/sprote/references/native-fallback.md` | Python 미가용 시 폴백 절차 |
| `skills/sprote/references/test-scenarios.md` | 정상·에러 흐름 예시 |
| `skills/sprote/references/design-principles.md` | artisan 디자인 원칙·안티패턴 |
| `skills/sprote/references/pm-standards.md` | PRD 템플릿·INVEST 체크리스트·심각도 |
| `skills/sprote/references/sllm-optimizations.md` | 10대 sLLM 최적화 기법 명세 |

---

## scripts/ — 자동화 스크립트

| 파일 | 역할 |
|------|------|
| `scripts/setup-permissions.py` | `~/.claude/settings.json`에 sprote 필수 권한 추가 (멱등) |
| `scripts/advisor-compact-gate.sh` | advisor() PreToolUse hook — 세션당 첫 호출 차단 후 `/compact` 안내 |
| `scripts/ensure-engine-json.py` | `{project}/.claude/sprote/engine.json` 보장 (멱등) |
| `scripts/ensure-coding-guidelines.py` | 대상 CLAUDE.md 맨 위에 코딩 행동 지침 삽입 (멱등) |
| `scripts/deploy.sh` | 배포 자동화 (`.deploy-exclude` 적용) |
| `scripts/install.sh` | 원격 한 줄 설치 스크립트 (curl pipe) |

> Python 미가용 환경에서는 SKILL.md의 **네이티브 폴백**(Read/Write 도구 직접 사용)으로 동작한다.

---

## docs/ — 사용자 문서

| 파일 | 역할 |
|------|------|
| `docs/FILES.md` | (본 문서) 소스 파일 인벤토리 |
| `docs/skill-routing.md` | 요청 → 스킬 매핑 규칙 |
| `docs/model-strategy.md` | 모델 선택 가이드, advisor() 에스컬레이션 |
| `docs/migration-from-ttb-agents.md` | v1.x → v2.0 마이그레이션 가이드 |
| `docs/migration-engine-runtime.md` | engine.json 런타임 해석 도입 마이그레이션 노트 |
| `docs/internal/git-workflow.md` | (내부) git 원격 설정 & 배포 스크립트 |
| `docs/internal/version-management.md` | (내부) 버전 업데이트 & README 동기화 규칙 |

---

## tests/ — 테스트 스위트

| 디렉터리 | 범위 |
|---------|------|
| `tests/unit/` | 에이전트·스킬·플러그인 설정 단위 검증 |
| `tests/integration/` | 크로스 레퍼런스, engine.json 런타임 해석, 저장소 위생 |
| `tests/e2e/` | sprote 표준 종단 검증 |

> 인벤토리에서는 개별 테스트 파일을 나열하지 않는다. `pytest --collect-only` 출력을 참고할 것.
