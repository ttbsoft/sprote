# ttb-agents → sprote v2.0 마이그레이션 가이드

> **Clean break**: ttb-agents v1.x는 종착(v1.18.x), sprote v2.0은 신규 plugin으로 별도 설치한다.
> Claude Code 마켓플레이스는 plugin name을 unique key로 사용하므로, 자동 업데이트는 동작하지 않는다.

---

## 마이그레이션 절차 (사용자)

### Step 1: ttb-agents 제거 (선택)

v1.x를 그대로 두어도 충돌하지 않는다. 정리하려면:

```
/plugin uninstall ttb-agents
```

### Step 2: sprote 신규 설치

```
/plugin marketplace add ttbsoft/sprote
/plugin install sprote@sprote-marketplace
```

### Step 3: 권한 설정

설치 후 sprote setup 스킬을 한 번 실행한다:

```
/sprote:setup
```

자동 처리 항목:
- `~/.claude/settings.json`에 WebSearch·WebFetch·Brave Search 권한 추가
- 프로젝트별 `.claude/sprote/engine.json` 초기화
- 외부 plugin(gstack 등) 설치 감지·안내

### Step 4: 프로젝트별 engine.json 이전

기존 `{project}/.claude/ttb-agents/engine.json`이 있다면 새 경로로 이전:

```bash
mv {project}/.claude/ttb-agents/engine.json {project}/.claude/sprote/engine.json
rmdir {project}/.claude/ttb-agents
```

---

## 트리거 매핑

### 스킬 진입점

| v1.x 트리거 | v2.0 트리거 | 비고 |
|------------|------------|------|
| `ttb-agents:agents` | `sprote` | 통합 라우터 — 자동으로 mode 분기 |
| `ttb-agents:design` | `sprote` | design 모드로 분기 |
| `ttb-agents:pm-workflow` | `sprote` | pm 모드로 분기 |
| `ttb-agents:sllm` | `sprote` | sllm 모드로 분기 |
| `ttb-agents:review` | `sprote:review` | 그대로 유지 |
| `ttb-agents:advisor` | `sprote:advisor` | 그대로 유지 |
| `ttb-agents:setup` | `sprote:setup` | 그대로 유지 + 외부 plugin 감지 추가 |
| (없음) | `sprote:bridge` | 신규 — 외부 plugin namespaced 호출 |

### 키워드 → mode 분기 (v2.0)

| 키워드 | mode |
|--------|------|
| 팀 구성, 하네스, 워크플로우 자동화, 에이전트 추가 | **harness** |
| UI 만들기, 디자인 검토, AI 안 티나게 | **design** |
| 파일 검색, 간단히 수정, 로그 분석, 테스트 실패 | **code** |
| 릴리스 노트, 코드 리뷰 요약, 변경점 정리 | **doc** |
| 제품 기획, PRD, 시장 조사, 로드맵 | **pm** |
| sLLM, 소형 모델 자동화, Ollama | **sllm** |

라우터 자동 분기 — 사용자가 mode를 명시할 필요 없음.

---

## 파일 경로 변경

소비 프로젝트(`.claude/`) 측면:

| v1.x 경로 | v2.0 경로 |
|----------|----------|
| `.claude/ttb-agents/engine.json` | `.claude/sprote/engine.json` |
| `_workspace/` (변경 없음) | `_workspace/` |

플러그인 내부 (참조용):

| v1.x | v2.0 |
|------|------|
| `skills/agents/SKILL.md` | `skills/sprote/SKILL.md` (라우터) + `references/harness-pipeline.md` |
| `skills/design/SKILL.md` | `skills/sprote/references/design-pipeline.md` |
| `skills/pm-workflow/SKILL.md` | `skills/sprote/references/pm-pipeline.md` |
| `skills/sllm/SKILL.md` | `skills/sprote/references/sllm-pipeline.md` |
| `skills/agents/references/ttb-standards.md` | `skills/sprote/references/sprote-standards.md` |
| `subagent_type: "ttb-agents:..."` | `subagent_type: "sprote:..."` |

---

## 동작 변경 사항

### Cross-validator 자동 수정 권한

v1.x에서 `harness-cross-validator`와 `design-cross-validator`는 **리뷰만** 수행했다.
v2.0부터는 발견된 **P0·P1 결함을 직접 패치**한다:

- Codex sandbox: `workspace-write`
- 패치 적용 내역은 보고서 `## Applied Patches` 섹션에 기록
- 패치 후 `validator` 1회 재실행 (회귀 차단)
- P2·P3은 권고만, 사용자 결정에 위임
- 외과적 변경 원칙: 무관한 리팩토링 금지

### 외부 plugin 통합

v2.0부터 외부 plugin(gstack 등)을 namespaced 호출로 활용 가능:

```
Skill(skill: "gstack:qa")
Skill(skill: "gstack:ship")
Skill(skill: "superpowers:brainstorming")
```

자세한 사항은 `skills/bridge/SKILL.md` 참조.

> **vendoring 없음**: sprote는 외부 plugin을 번들하지 않는다. 사용자가 직접 설치한 버전이 사용된다.

---

## 호환성 정책

- v1.x → v2.0 자동 마이그레이션 도구는 제공하지 않는다 (clean break)
- v1.x는 v1.18.x에서 종착되며 보안 패치를 받지 않는다
- v2.0 이후 추가 기능·버그 수정은 sprote 저장소에서만 발생

---

## 참조

- README.md — sprote 소개·전체 사용법
- `skills/sprote/SKILL.md` — 통합 라우터 동작 명세
- `skills/sprote/references/routing-matrix.md` — 복합 입력 분기 가이드
