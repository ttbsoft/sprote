---
name: bridge
description: "sprote에서 외부 plugin 스킬을 namespaced 호출로 위임하는 브리지.
  사용자가 'qa 돌려줘', 'ship 해줘', 'design-review 받아줘', 'investigate 해줘' 등 외부 plugin(gstack 등) 명령을 sprote 컨텍스트에서 호출하면 이 스킬을 사용한다.
  '/sprote bridge qa', '/sprote bridge ship', 'gstack 명령 위임', '외부 plugin 호출' 요청 시에도 사용.
  외부 plugin 재호출, 위임 재실행, 매핑 수정, 설치 안내 다시 보여달라는 요청 시에도 사용.
  외부 plugin이 설치되어 있지 않으면 설치 안내를 출력한다 (vendoring 없음)."
---

# Sprote Bridge

> sprote는 외부 plugin을 번들하지 않는다. 이 스킬은 설치된 외부 plugin 스킬을 **namespaced 호출**로 위임한다.

## 동작 원칙

1. **namespace 필수**: 외부 plugin 스킬은 반드시 `<plugin-name>:<skill-name>` 형식으로 호출한다 (예: `gstack:qa`)
2. **설치 감지 우선**: 호출 전에 plugin 설치 여부를 감지하고, 미설치 시 안내 메시지를 출력한다
3. **vendoring 없음**: 외부 plugin을 sprote 안에 복사하지 않는다. 사용자가 직접 설치한 버전이 사용된다
4. **위임만 수행**: bridge는 호출 라우팅만 담당하고, 실제 작업은 외부 스킬이 처리한다

## 위임 매핑

### gstack 위임

| sprote 트리거 | 위임 대상 | 용도 |
|--------------|----------|------|
| qa 돌려줘, 사이트 동작 QA, 시나리오 테스트 | `gstack:qa` | 사이트 동작 검증 |
| ship 해줘, 배포, 릴리스 게이트 | `gstack:ship` | 배포 파이프라인 |
| design-review 받아줘, 시각 디자인 리뷰 | `gstack:design-review` | 배포 단계 디자인 리뷰 |
| investigate 해줘, 버그 조사 | `gstack:investigate` | 버그·이슈 조사 |
| context-save, 작업 저장 | `gstack:context-save` | 세션 컨텍스트 저장 |
| context-restore, 작업 복원 | `gstack:context-restore` | 세션 컨텍스트 복원 |

### superpowers 위임 (설치 시)

| sprote 트리거 | 위임 대상 |
|--------------|----------|
| 브레인스토밍 | `superpowers:brainstorming` |
| TDD로 진행 | `superpowers:test-driven-development` |
| 디버깅 도와줘 | `superpowers:systematic-debugging` |
| 병렬로 작업해줘 | `superpowers:dispatching-parallel-agents` |

### document-skills 위임 (설치 시)

| sprote 트리거 | 위임 대상 |
|--------------|----------|
| docx로 변환 | `document-skills:docx` |
| pptx로 만들어줘 | `document-skills:pptx` |
| PDF로 변환 | `document-skills:pdf` |

## 실행 절차

### Step 1: 위임 대상 식별

사용자 입력에서 트리거 키워드를 매칭하여 `{plugin}:{skill}` 형식의 대상을 결정한다.

매칭 실패 시:
- 가장 유사한 sprote 모드를 추천 (예: "design-review" → "sprote design 모드의 review 단계로 진행할까요?")
- 명백히 외부 plugin 위임이 필요한데 트리거 매칭이 안 되면 사용자에게 `AskUserQuestion`으로 확인

### Step 2: 외부 plugin 설치 감지

위임 대상의 plugin이 설치되어 있는지 확인한다:

```bash
# gstack
which gstack 2>/dev/null || ls -d ~/.claude/skills/gstack 2>/dev/null

# Claude Code plugin 등록 확인
/plugin list   # 또는 ~/.claude/plugins/marketplaces/*/{plugin-name}/ 디렉터리 확인
```

설치되어 있으면 Step 3, 미설치면 Step 4로 분기.

### Step 3: namespaced 호출

```
Skill(skill: "gstack:qa")
Skill(skill: "gstack:ship")
Skill(skill: "superpowers:brainstorming")
```

호출 후 외부 스킬이 자체 워크플로우로 동작한다. bridge는 추가 개입하지 않는다.

### Step 4: 미설치 fallback 안내

다음 메시지를 출력하고 대안을 제시한다:

```
⚠ {plugin-name} 미설치

설치 방법:
  - gstack:        curl -fsSL https://garryslist.org/gstack/install.sh | bash
  - superpowers:   /plugin marketplace add anthropic/superpowers && /plugin install superpowers
  - document-skills: /plugin marketplace add anthropic/document-skills && /plugin install document-skills

또는 sprote 내장 모드로 진행:
  - qa 대신 sprote code 모드 (test_failure)
  - design-review 대신 sprote design 모드 (Phase 3 리뷰)
  - docx/pptx 변환 → 별도 처리 안 됨, 외부 plugin 설치 필요
```

대안 sprote 모드가 적용 가능하면 자동으로 라우터 SKILL.md로 위임한다.

## 트러블슈팅

### 호출은 성공했는데 결과가 이상함

외부 plugin의 워크플로우는 sprote와 다를 수 있다. bridge는 호출만 위임하므로 결과 해석은 사용자가 직접 한다.

### 외부 plugin 버전 불일치

`/plugin list`로 설치된 버전 확인. 외부 plugin 업데이트는 사용자가 직접 수행한다 (sprote가 관여하지 않음).

### namespace 누락 호출 실패

`Skill(skill: "qa")` 같은 unqualified 호출은 동작하지 않을 수 있다. 반드시 `Skill(skill: "gstack:qa")` 형식으로 호출한다.

## 참조

- sprote 라우터: `skills/sprote/SKILL.md`
- 외부 plugin 감지·안내: `skills/setup/SKILL.md` Step 4
