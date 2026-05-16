---
name: setup
description: "sprote 플러그인 초기 설정 + 프로젝트 sprote 전환.
  '/sprote:setup', 'sprote 권한 설정해줘', '플러그인 초기 설정해줘', 'sprote 설치 후 설정해줘' 요청 시 반드시 이 스킬을 사용할 것.
  빈 프로젝트는 sprote harness 빌더로 처음부터 설계하고, 기존 프로젝트는 분석 후 sprote 구조로 전환한다.
  권한 누락 확인, 설정 재실행, 외부 plugin 안내 재요청, '프로젝트를 sprote로 변경', '기존 프로젝트 sprote 적용' 요청 시에도 사용."
---

# Sprote 초기 설정 + 프로젝트 전환

## 전체 흐름

```
Phase 0  환경 점검 (Python · 외부 plugin)
Phase 1  권한·hook 기본 설정 (~/.claude + .claude/settings.json)
Phase 2  프로젝트 상태 감지 → 분기
   ├─ 2-A 빈 프로젝트  → sprote harness 빌더 위임
   └─ 2-B 기존 프로젝트 → 분석 → 제안 → 승인 → 충돌 처리 → 적용
Phase 3  최종 보고
```

---

## Phase 0 — 환경 점검

### Step 0.1: Python 가용성 확인

```
python3 --version
```

실패 시 `python --version`. 결과에 따라 `PYTHON_CMD`를 `python3` / `python` / `none`로 결정한다.

사용자에게 한 줄 보고:
- 발견: `Python {버전} 확인 — 스크립트 모드`
- 미발견: `Python 미설치 — 네이티브 모드 (모든 기능 정상 동작)`

### Step 0.2: 외부 plugin·CLI + capability 감지

Bash로 다음을 순차 확인:

| 대상 | 검출 방법 | 용도 |
|-----|---------|-----|
| codex CLI | `which codex` | `capabilities.codex_cli` |
| gstack | `which gstack` 또는 `~/.claude/skills/gstack/` 존재 | 안내 |
| superpowers | `~/.claude/plugins/marketplaces/*/superpowers/` 존재 | 안내 |
| document-skills | `~/.claude/plugins/marketplaces/*/document-skills/` 존재 | 안내 |

**Capability 감지 (engine.json용):**

| Capability | 판정 |
|-----------|------|
| `codex_cli` | `which codex` 종료 코드 0 → true |
| `opus_review` | 가용 도구 목록에 `advisor` 존재 + Anthropic 환경(`ANTHROPIC_API_KEY` 또는 Claude Code 식별) → true. 불확실하면 사용자에게 확인 |
| `subagents` | `Agent` 도구 존재 → true. 호환 CLI에서는 별도 확인 필요 |

감지 결과는 Phase 2-B Step 5-[D]에서 engine.json에 명시 boolean으로 기록된다.
결과 요약은 Phase 3 최종 보고에서 출력.

---

## Phase 1 — 권한·hook 기본 설정

빈/기존 무관하게 항상 수행.

### Step 1.1: 글로벌 권한 설정

**PYTHON_CMD가 있는 경우:**

```
{PYTHON_CMD} "{CLAUDE_PLUGIN_ROOT}/scripts/setup-permissions.py"
```

**PYTHON_CMD=none (네이티브 폴백):**

Read 도구로 `~/.claude/settings.json` 읽기 → `permissions.allow` 배열에 누락된 항목만 추가 → Write.

추가 대상:

```json
["WebSearch", "WebFetch", "mcp__brave-search__brave_web_search", "mcp__brave-search__brave_local_search"]
```

### Step 1.2: 프로젝트 hook 설정

대상: `{PROJECT_ROOT}/.claude/settings.json`

Read → 기존 `hooks.PostToolUse` 배열에 아래 hook이 없으면 추가 (중복 금지):

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "FILE=$(jq -r '.tool_input.file_path // .tool_response.filePath' 2>/dev/null); if ! echo \"$FILE\" | grep -qE '\\.(html|htm|jsx|tsx|vue|svelte|css|scss|less)$'; then exit 0; fi; if ! command -v gstack &>/dev/null; then echo '{\"systemMessage\":\"gstack이 설치되지 않아 UI 검증을 건너뜁니다.\"}'; exit 0; fi; gstack screenshot \"$FILE\" 2>/dev/null || true",
      "statusMessage": "UI 화면 변경 감지 — gstack으로 검증 중...",
      "timeout": 60
    }
  ]
}
```

파일이 없으면 `{"hooks":{"PostToolUse":[...]}}` 형태로 생성.

### Step 1.3: advisor() 자동 게이트 hook 설정

advisor() 호출 시 세션당 한 번 강제 차단하여 `/compact` 실행을 유도한다.

**대상 파일**: `~/.claude/settings.json` (글로벌)

Read → 기존 `hooks.PreToolUse` 배열에 아래 hook이 없으면 추가 (중복 금지, `matcher: "advisor"` 기준):

```json
{
  "matcher": "advisor",
  "hooks": [
    {
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/advisor-compact-gate.sh"
    }
  ]
}
```

파일이 없으면 `{"hooks":{"PreToolUse":[...]}}` 형태로 생성. 기존 `PreToolUse` 배열이 있으면 항목만 추가.

**동작 요약:**
- 세션당 첫 advisor() 호출: 자동 차단 + `/compact` 안내 메시지
- 사용자가 `/compact` 실행 후 재요청: 통과 (마커 파일 `${TMPDIR}/sprote-advisor-ack-<session_id>`로 관리)

---

## Phase 2 — 프로젝트 상태 감지 + 분기

### Step 2.0: 빈 vs 기존 판정

다음을 Bash로 수집:

```bash
# 소스 파일 카운트 (주요 확장자)
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.java" \
  -o -name "*.swift" -o -name "*.php" -o -name "*.rb" \) \
  -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./_workspace/*" \
  2>/dev/null | wc -l

# 매니페스트 파일
ls package.json pyproject.toml go.mod Cargo.toml pom.xml composer.json 2>/dev/null

# 기존 sprote 흔적
ls -d .claude/agents/ .claude/sprote/ 2>/dev/null
ls CLAUDE.md README.md 2>/dev/null
```

**판정 규칙:**

```
빈 프로젝트 = (소스 파일 < 5) AND (매니페스트 없음) AND (.claude/agents/ 없음)
              AND (CLAUDE.md 없거나 빈 파일)
그 외 = 기존 프로젝트
```

**경계 케이스**: 소스 < 5인데 매니페스트는 있는 경우 등 → 사용자에게 `AskUserQuestion`으로 확인.

---

## Phase 2-A — 빈 프로젝트 흐름

### Step 2A.1: 프로젝트 설명 수집

`AskUserQuestion`:

```
"새 프로젝트를 sprote로 설계하시겠습니까?"
- 예, 어떤 프로젝트인지 설명할게요
- 아니요, 권한 설정만 마치겠습니다 (Phase 3로 이동)
```

진행 선택 시 추가 질문:

```
"한 줄로 프로젝트를 설명해주세요. (예: 'TypeScript로 e-commerce 백엔드 API')"
```

### Step 2A.2: sprote harness 위임

수집한 설명을 컨텍스트로 sprote 스킬 호출:

```
Skill(skill: "sprote", args: "harness 모드 — 빈 프로젝트 신규 설계. 설명: {user_description}")
```

sprote 스킬이 harness 파이프라인을 실행하여 `.claude/agents/`·`_workspace/`·CLAUDE.md 등을 생성한다. setup은 위임 후 결과를 사용자에게 한 줄 요약.

---

## Phase 2-B — 기존 프로젝트 흐름

### Step 2B.1: 코드베이스 분석

다음 정보를 수집하여 분석 보고서 작성:

| 카테고리 | 수집 방법 |
|---------|---------|
| 언어·프레임워크 | 매니페스트(`package.json`, `pyproject.toml` 등) Read |
| 디렉터리 구조 | `find . -maxdepth 2 -type d -not -path './node_modules*' -not -path './.git*'` |
| 도메인 키워드 | `src/`, `app/`, `lib/` 하위 디렉터리·주요 파일명에서 추출 |
| README 요약 | `README.md` Read (있을 시 상위 30줄) |
| 기존 `.claude/` | `ls -la .claude/` |
| 기존 `CLAUDE.md` | Read (있을 시 상위 50줄) |
| 기존 `docs/` | `ls docs/ 2>/dev/null` |

### Step 2B.2: sprote 전환 제안서 출력

수집 결과를 다음 형식으로 사용자에게 보여준다:

```
=== sprote 전환 분석 ===

프로젝트: {이름} ({언어/프레임워크})
도메인 키워드: {추출된 키워드 목록}
기존 상태:
- CLAUDE.md: {있음/없음 + 줄 수}
- .claude/agents/: {있음/없음 + 개수}
- docs/: {있음/없음}

전환 항목:
[A] CLAUDE.md 생성/병합 — sprote 스킬 라우팅·코딩 규칙·모델 전략 추가
[B] .claude/agents/ 구성 — sprote harness 빌더로 도메인 맞춤 에이전트 생성
[C] docs/ 표준 구조 — FILES.md, internal/ 디렉터리
[D] .claude/sprote/engine.json — 엔진 설정 초기화 (선택)
```

### Step 2B.3: 항목별 승인

`AskUserQuestion` (multiSelect=true):

```
"어떤 항목을 적용할까요?"
- A. CLAUDE.md 생성/병합
- B. 프로젝트 맞춤 에이전트 생성 (sprote harness 위임)
- C. docs/ 표준 구조
- D. engine.json 초기화
```

선택된 항목만 다음 단계로 진행.

### Step 2B.4: 충돌 확인 (선택된 항목별 반복)

각 항목에 대해 기존 파일과 충돌하면 `AskUserQuestion`:

```
"{파일명}이 이미 존재합니다. 어떻게 처리할까요?"
- 병합 — sprote 표준 섹션 중 누락된 부분만 추가 [추천]
- 덮어쓰기 — 기존 파일을 {파일명}.bak로 백업
- 스킵 — 이 항목 적용 안 함
```

### Step 2B.5: 적용

**[A] CLAUDE.md 생성/병합**
- 신규: Phase 2B.1 분석 결과를 기반으로 sprote 표준 템플릿(스킬 라우팅·모델 전략·코딩 규칙) 작성 → Write
- 병합: 기존 파일 Read → sprote 필수 섹션 중 누락된 것만 Edit으로 추가
  - 필수 섹션: `## 스킬 라우팅`, `## 모델 전략`, `## 코딩 행동 지침` (없으면 추가)

**[B] 에이전트 생성 — sprote harness 위임**

분석 결과를 컨텍스트로 sprote 스킬 호출:

```
Skill(skill: "sprote", args: "harness 모드 — 기존 프로젝트 전환.
컨텍스트:
- 언어/프레임워크: {언어}
- 디렉터리 구조: {요약}
- 도메인 키워드: {키워드}
- README 요약: {요약}
도메인 맞춤 에이전트를 .claude/agents/에 생성할 것.")
```

**[C] docs/ 표준 구조**
- `docs/FILES.md` Write (헤더만, 인벤토리는 추후 docs-keeper 에이전트가 갱신)
- `docs/internal/` 디렉터리 생성

```bash
mkdir -p docs/internal
```

**[D] engine.json 초기화**

Phase 0.2의 capability 감지 결과를 반영하여 `.claude/sprote/engine.json` Write:

```json
{
  "orchestrator_model": "sonnet",
  "runtime": "auto",
  "capabilities": {
    "codex_cli": "<감지 결과 true/false>",
    "opus_review": "<감지 결과 true/false>",
    "subagents": "<감지 결과 true/false>"
  }
}
```

**고정 분담**: Claude가 설계·코딩, **리뷰는 폴백 체인이 자동 결정**.
- 1순위: codex_cli=true → codex 리뷰·자동 수정
- 2순위: opus_review=true → Opus 권고 → Sonnet 패치
- 3순위: 둘 다 false → 동일 모델 재분석 + 신뢰도 경고

기존 `engine.json`에 `engine_mode` 필드가 있으면 무시(deprecated)하고 새 스키마로 덮어쓴다. 사용자에게 한 번만 안내:

```
ℹ️  engine_mode 필드는 v2.2.0부터 deprecated되어 제거되었습니다.
   리뷰 단계는 capability 폴백 체인이 자동 결정합니다.
```

---

## Phase 3 — 최종 보고

다음 항목을 종합하여 사용자에게 한 번에 보고:

```
=== sprote 설정 완료 ===

[Phase 1] 권한·hook
- 글로벌 권한 추가: {목록} (또는 "이미 설정됨")
- 프로젝트 hook 추가: gstack UI 검증 (또는 "이미 설정됨")

[Phase 2] {빈/기존} 프로젝트 처리
- {적용된 항목 목록}

[외부 plugin 감지 결과]
✓ codex CLI / gstack / superpowers / document-skills
✗ (미설치 항목 안내)

다음 단계:
- Claude Code 재시작 또는 /hooks 한 번 열기 (hook 적용)
- {기존 프로젝트인 경우}: sprote 스킬로 작업 시작 가능
- {외부 plugin 미설치 시}: 안내 메시지 출력
```

### 미설치 plugin 안내 (해당 시에만)

- **codex CLI**: `npm install -g @openai/codex` — Codex 분석·교차 검증·자동 수정 활성화
- **gstack**: https://github.com/garrytan/gstack — `/qa`·`/ship`·`/design-review` 위임 가능
- **superpowers·document-skills**: `/plugin marketplace add` 후 `/plugin install`

> **vendoring 없음**: sprote는 외부 plugin을 번들하지 않는다.

---

## 트러블슈팅

- **sprote 위임 실패** (Phase 2A.2, 2B.5-B): sprote 스킬 자체 트러블슈팅 가이드 참조 후 재시도. setup은 위임 결과만 보고.
- **빈/기존 판정 오류**: Phase 2.0 경계 케이스에서 사용자 확인 절차 강제.
- **CLAUDE.md 병합 충돌**: 자동 병합 불가능한 충돌은 사용자에게 diff 보여주고 수동 선택.
