# 네이티브 폴백 절차

Python을 사용할 수 없을 때 Claude가 직접 실행하는 절차. 모든 도구 호출은 Claude의 내장 도구(Read/Write)를 사용한다.

## ensure-engine-json

1. Read 도구로 `{CLAUDE_PLUGIN_ROOT}/skills/sprote/engine.json` 읽기
2. `{project_root}/.claude/sprote/engine.json` 존재 여부 확인:
   - Read 도구로 해당 경로 읽기 시도 → 성공 시 이미 존재 → 스킵
3. 미존재 → Write 도구로 읽은 전역 engine.json 내용을 `{project_root}/.claude/sprote/engine.json`에 저장
4. 완료 후 사용자에게 한 줄 보고: "engine.json을 기본값으로 초기화했습니다 — 필요 시 수정하세요"

---

## ensure-coding-guidelines

1. Read 도구로 `{CLAUDE_PLUGIN_ROOT}/skills/sprote/references/coding-guidelines.md` 읽기
2. 파일 내용의 **4번째 줄부터 끝까지** 추출 (앞 3줄: `# 제목`, 빈줄, 부제 제거)
3. Read 도구로 `{project_path}/CLAUDE.md` 읽기 시도
   - 성공 시 → 기존 내용 보존
   - 파일이 없으면 → 기존 내용을 빈 문자열로 취급하고 계속 진행 (스킵 금지)
4. 내용에 `## 코딩 행동 지침` 포함 여부 확인
   - 포함됨 → 스킵 (이미 존재)
   - 미포함 → Write 도구로 CLAUDE.md를 아래 형식으로 작성:
     - 기존 내용이 있는 경우:
       ```
       ## 코딩 행동 지침

       {추출한 guidelines 본문}

       ---

       {기존 CLAUDE.md 전체 내용}
       ```
     - 기존 내용이 없는 경우 (파일 신규 생성):
       ```
       ## 코딩 행동 지침

       {추출한 guidelines 본문}
       ```
5. 완료 후 사용자에게 한 줄 보고 (신규 생성인지 추가인지 구분하여 표시)
