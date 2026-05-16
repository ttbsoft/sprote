# 테스트 시나리오

## 정상 흐름

1. 사용자: "이메일 자동화 하네스 만들어줘. 프로젝트 경로는 ~/email-project"
2. Phase 0: `_workspace/` 없음 → 초기 실행
3. Phase 1: 도메인="이메일 자동화", 경로=`~/email-project` 확인
4. Phase 2a: Codex domain-analyst → 이메일 파싱/분류/발송 작업 분석 → `01_domain_analysis.md`
5. Phase 2b: Claude pattern-analyst → 팬아웃/팬인 패턴 청사진 → `02_blueprint.md`
6. Phase 2c: Codex synthesis-reviewer → "오류 재시도 로직 누락" 등 보완점 도출 → `02b_synthesis.md`
7. Phase 3: builder → 청사진 + Codex 보완 반영하여 `~/email-project/.claude/` 파일들 생성
8. Phase 3b: docs-keeper → `~/email-project/docs/FILES.md` 생성
9. Phase 4: validator → PASS 9개, WARN 1개
10. Phase 5: 결과 보고

## 에러 흐름 (Codex 실패)

1. Phase 2a에서 Codex domain-analyst 실패
2. `general-purpose` 서브 에이전트로 domain-analyst 재실행 (대체 표시)
3. 나머지 Phase 정상 진행
4. Phase 5 보고 시 "Codex 대체 실행" 명시
