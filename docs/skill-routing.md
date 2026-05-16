# 스킬 라우팅

요청이 스킬과 매칭되면 **Skill 도구를 첫 번째 행동으로 실행**한다.
직접 답변하거나 다른 도구를 먼저 실행하지 않는다.

## ttb-agents 스킬

| 요청 유형 | 스킬 |
|---------|------|
| 프로젝트 팀 구성, 워크플로우 자동화, 릴리스 노트, 코드 작업 | `ttb-agents:agents` |
| 하네스 수정, 에이전트 추가·수정, 팀 재설계, 팀원 추가, 개선 요청 | `ttb-agents:agents` |
| UI 만들기, 디자인 검토, AI 안 티나게 개선, 교차 검증 | `ttb-agents:design` |
| 제품 기획, PRD 작성, 시장 조사, 로드맵 수립 | `ttb-agents:pm-workflow` |
| sLLM 에이전트 생성, 소형 모델 자동화, Ollama 하네스 | `ttb-agents:sllm` |
| 하네스 검증, TTB 표준 확인, 에이전트 파일 검토 | `ttb-agents:review` |
| 권한 설정 초기화 (첫 설치 후) | `ttb-agents:setup` |
| 막혔을 때, 어려운 결정, Opus에 물어봐, 어드바이저 | `ttb-agents:advisor` |

> ttb-agents 외부 스킬(gstack 등) 라우팅은 사용자 글로벌 `~/.claude/CLAUDE.md`에서 관리한다.
> 본 플러그인 문서에는 포함하지 않는다.
