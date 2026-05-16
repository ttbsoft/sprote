# sprote

> **너를 위해 존재한다** (라틴어 어원). Claude Code 통합 라우터 plugin — `sprote` 하나로 6개 작업 모드를 자동 분기한다.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 한 줄 요약

```
sprote 하나면 다 된다 — harness · design · code · doc · pm · sllm
```

이전 ttb-agents v1.x의 7개 분리 스킬을 **단일 라우터 + on-demand references**로 통합했다. 사용자는 더 이상 어떤 스킬을 호출해야 하는지 고민할 필요 없다.

## 설치

`~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "sprote-marketplace": {
      "source": {
        "source": "github",
        "repo": "ttbsoft/sprote"
      }
    }
  },
  "enabledPlugins": {
    "sprote@sprote-marketplace": true
  }
}
```

설치 후 `/sprote:setup` 한 번 실행으로 권한·외부 plugin 감지가 자동 수행된다.

## 6개 작업 모드

| 모드 | 트리거 예시 | 주 엔진 |
|------|-----------|--------|
| **harness** | 팀 구성, 워크플로우 자동화, 에이전트 추가 | Codex + Claude (이중 분석) |
| **design** | UI 만들기, 디자인 검토, AI 안 티나게 | Claude + Codex 교차 검증 |
| **code** | 파일 검색, 간단히 수정, 로그 분석, 테스트 실패 | Claude Haiku |
| **doc** | 릴리스 노트, 코드 리뷰 요약, 블로그 초안 | Claude Sonnet |
| **pm** | PRD 작성, 시장 조사, 로드맵 | Claude Opus/Sonnet |
| **sllm** | 9B 모델, Ollama, 소형 LLM 자동화 | Sonnet (10대 최적화) |

라우터가 입력 키워드로 mode를 자동 결정한다. 모호하면 사용자에게 확인을 묻는다.

## 자동 수정 권한 (v2.0 신규)

`harness-cross-validator`·`design-cross-validator`는 **리뷰뿐 아니라 P0·P1 결함을 직접 수정**한다 (Codex workspace-write sandbox). 패치 적용 내역은 보고서 `## Applied Patches` 섹션에 기록된다.

## 외부 plugin 통합

sprote는 외부 plugin을 번들하지 않는다. 설치된 plugin은 `bridge` 스킬로 namespaced 호출한다:

```
Skill(skill: "gstack:qa")
Skill(skill: "gstack:ship")
Skill(skill: "superpowers:brainstorming")
```

`/sprote:setup`이 gstack·superpowers·document-skills·codex CLI 설치 여부를 감지하고 안내한다.

## 스킬 구성 (5개)

| 스킬 | 역할 |
|------|------|
| `sprote` | 통합 라우터 — 6 mode 자동 분기 |
| `setup` | 권한 초기 설정 + 외부 plugin 감지·안내 |
| `review` | 산출물 검증 (TTB 표준) |
| `advisor` | Opus 에스컬레이션 (`/compact` 선행) |
| `bridge` | 외부 plugin 위임 호출 |

## 엔진 설정

`{project}/.claude/sprote/engine.json` (없으면 `/sprote:setup`이 자동 생성):

```json
{
  "orchestrator_model": "sonnet",
  "engine_mode": "codex_analysis"
}
```

| engine_mode | 분석 엔진 | 구현 엔진 |
|-------------|----------|----------|
| `codex_analysis` (기본) | Codex → Opus 폴백 | Claude Sonnet |
| `opus_analysis` | Claude Opus | Codex |

Codex 미설치 시 분석은 Opus로 자동 폴백, 교차 검증은 생략된다.

## 파일 구조

```
sprote/
├── .claude-plugin/
│   ├── plugin.json          (name: sprote, version: 2.0.0)
│   └── marketplace.json     (sprote-marketplace)
├── agents/                  (24개 — 분석·빌드·디자인·PM·sLLM)
├── skills/
│   ├── sprote/
│   │   ├── SKILL.md         (통합 라우터, 186줄)
│   │   ├── engine.json
│   │   └── references/      (14 모듈 — mode별 pipeline + 표준)
│   ├── setup/
│   ├── review/
│   ├── advisor/
│   └── bridge/
├── scripts/                 (Python 자동화)
├── docs/
│   ├── FILES.md             (소스 인벤토리)
│   ├── migration-from-ttb-agents.md
│   ├── skill-routing.md
│   └── model-strategy.md
└── tests/                   (73 테스트 — unit·integration·e2e)
```

## ttb-agents v1.x → sprote v2.0 마이그레이션

| v1 트리거 | v2 트리거 |
|----------|----------|
| `ttb-agents:agents` | `sprote` (harness 모드로 자동 분기) |
| `ttb-agents:design` | `sprote` (design 모드) |
| `ttb-agents:pm-workflow` | `sprote` (pm 모드) |
| `ttb-agents:sllm` | `sprote` (sllm 모드) |
| `ttb-agents:review` | `sprote:review` |
| `ttb-agents:advisor` | `sprote:advisor` |
| `ttb-agents:setup` | `sprote:setup` (+ 외부 plugin 감지 추가) |

자세한 매핑: [docs/migration-from-ttb-agents.md](docs/migration-from-ttb-agents.md)

> **Clean break**: Claude Code 마켓플레이스는 plugin name을 unique key로 사용한다. ttb-agents → sprote는 자동 업데이트되지 않으므로 **수동 재설치**가 필요하다.

## 라이선스

MIT — [LICENSE](LICENSE) 참조.

## 저장소

- GitHub: https://github.com/ttbsoft/sprote
- 이전 버전 (deprecated): [ttbcorp/claude-agents](https://github.com/ttbcorp/claude-agents) (v1.18.1까지)
