---
description: 새로 배운 규칙을 LEARNED_RULES + memory 에 함께 반영
argument-hint: [새 규칙 내용]
---

사용자가 알려준 새 규칙을 영구 반영한다. 입력: $ARGUMENTS

1. docs/LEARNED_RULES.md 의 알맞은 섹션에 사람이 읽기 좋게 추가(케이스·예시·날짜 포함).
2. **리포 `memory/`** 에 대응하는 feedback_*.md 파일을 만들거나 갱신 (CLAUDE.md 가 `@memory/` 로 임포트하는 리포 내 폴더 — 하네스 임시 memory 디렉토리 아님).
3. memory/MEMORY.md 인덱스에 한 줄 추가.
4. 가격 산식 규칙이면 scripts/price_calc.py 와 test_price_calc.py 도 갱신할지 검토.
5. **항상 마지막에 `git add -A && git commit && git push`** — learn 변경(LEARNED_RULES·memory·관련 스크립트)을 커밋·푸시해 영구 보존. (커밋 메시지 끝에 Co-Authored-By 라인 포함, main 직접 커밋 OK — 이 리포는 direct-to-main 워크플로.)
변경 요약을 한 줄로 보고.
