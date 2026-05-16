# 마이그레이션 가이드: 런타임 엔진 해석

> 적용 대상: ttb-agents v1.16 이전에 생성된 자식 하네스
> 관련 표준: `skills/agents/references/ttb-standards.md` §6, §9

## 배경

v1.16 이전 builder는 모든 Agent 호출에 `model: "opus"`를 하드코딩했다. 그 결과 자식 프로젝트의 `{project}/.claude/ttb-agents/engine.json`을 수정해도 분석·구현 분기가 변하지 않았다. v1.16부터 builder는 분석·구현 역할을 변수 플레이스홀더로 출력하고, 자식 오케스트레이터는 매 실행마다 `engine.json`을 읽어 엔진을 결정한다.

## 영향 범위

- **새로 생성되는 하네스**: 자동으로 신규 표준 적용 — 조치 불필요
- **이미 배포된 하네스**: 하드코딩된 상태로 남음 — 아래 절차로 마이그레이션

## 마이그레이션 절차 (권장: 재빌드)

### 1. 기존 하네스 백업

```
{project}/.claude/agents/   → backup/agents/
{project}/.claude/skills/   → backup/skills/
```

### 2. ttb-agents:agents 재실행

소비자 프로젝트에서 다음 중 하나를 입력:

- "이 프로젝트 티티비팀으로 자동화해줘"
- "티티비팀 다시 만들어줘"

`_workspace/`가 이미 존재하면 부분 재실행 모드로 진입한다. 청사진을 다시 쓰려면 `_workspace/02_blueprint.md`를 삭제하거나 `_workspace_old/`로 옮긴다.

### 3. 결과 확인

생성된 오케스트레이터 SKILL.md에 다음이 포함되어야 한다:

- `### Phase -0.5: 엔진 해석` 블록
- 분석·구현 Agent 호출에 `{ANALYSIS_SUBAGENT}` / `{ANALYSIS_MODEL}` / `{IMPLEMENTATION_SUBAGENT}` / `{IMPLEMENTATION_MODEL}` 변수
- LEADER/LIGHT 호출만 `sonnet` / `haiku` 고정 명시

`/ttb-agents:review`로 자동 검증 가능.

### 4. 동작 확인

`{project}/.claude/ttb-agents/engine.json`의 `engine_mode`를 `codex_analysis` ↔ `opus_analysis`로 토글하고 같은 작업을 두 번 실행해 라우팅이 달라지는지 확인.

## 보조 절차 (수동 패치)

재빌드가 어려우면 오케스트레이터 SKILL.md만 수동 패치:

1. SKILL.md 상단 (Phase 0 직전)에 §9.3 표준 블록을 그대로 삽입
2. 분석·구현 Agent 호출의 하드코딩된 `model: "opus"` / `subagent_type: "..."` 를 변수로 치환:

   ```diff
   - subagent_type: "codex:codex-rescue",
   - model: "opus",
   + subagent_type: "{ANALYSIS_SUBAGENT}",
   + model: "{ANALYSIS_MODEL}",
   ```

3. `_workspace/`에 청사진이 있으면 각 에이전트 정의에 `role:` 필드 추가
4. validator로 검증

## 폴백 동작

- `engine.json` 없음 → 자식 오케스트레이터가 사용자에게 `ttb-agents:agents` 실행을 안내하고 중단
- `codex:codex-rescue` 일반 호출 실패 (1회성) → `general-purpose` + `sonnet`로 즉시 대체, 산출물에 대체 사실 명시
- **Codex 토큰 소진 / 할당량 초과 / 인증 만료** → 세션 전체에서 Codex 영구 비활성화 (CLAUDE_ONLY 모드, TTB §9.6).
  - `codex_analysis`: 분석=Sonnet / 구현=Sonnet
  - `opus_analysis`: 분석=Opus / 구현=Sonnet
  - 사용자 별도 조치 불필요. 산출물 첫 줄에 `⚠️  Codex 사용 불가 (사유: ...) — Claude-only 모드로 진행` 표시
  - 복구는 Codex 인증·할당량 갱신 후 새 세션에서
- `engine_mode` 값 비정상 → 기본값 `codex_analysis`로 폴백 + 한 줄 경고

## 회귀 테스트

본 변경에 대한 회귀 테스트:

```
tests/integration/test_engine_runtime_resolution.py
```

`pytest tests/integration/test_engine_runtime_resolution.py -q` 로 검증.
