---
name: feedback_never_ask_run_commands
description: 커맨드 실행을 사용자에게 절대 요청하지 말 것 — 내가 직접 실행. bash 프롬프트/허가 요청 금지
metadata:
  type: feedback
---

사용자에게 **커맨드를 직접 실행하라고 요청하지 않는다.** 필요한 bash/스크립트는 **내가 바로 실행**한다. (2026-07-19 사용자 명시: "don't ever ask me to run any commands", 그 전 "allow * 로 해")

**Why:** 반복 승인·수동 실행이 워크플로를 느리게 하고 번거롭다. 이 프로젝트는 성숙·신뢰된 리셀러 워크플로라 사용자가 전권 위임했다.

**How to apply:**
- 프로젝트 `.claude/settings.json` permissions.allow 에 `Bash`(전체 허용) 설정됨 → 모든 bash 프롬프트 없이 실행.
- "이 커맨드 실행해 주세요" / "터미널에서 ~ 돌리세요" 류 **금지**. 로컬에서 되는 건 내가 실행하고 결과만 보고.
- 예외(안전 규칙 유지): 외부 전송(Slack push 등 되돌리기 어려운 것)은 여전히 사후보고 원칙이되, 로컬 실행은 무조건 내가 함. 금융/자격증명 등 시스템 안전규칙은 불변.
- 새 컴퓨터/세션에서 프롬프트가 다시 뜨면 settings.json allow 에 `Bash` 있는지 확인, 없으면 추가. [[feedback_apply_without_asking]]
