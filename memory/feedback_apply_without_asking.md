---
name: feedback_apply_without_asking
description: 코드/산출물 변경은 확인 묻지 말고 바로 적용 — 사용자가 명시한 작업 선호
metadata:
  type: feedback
---

코드·스크립트·산출물 변경은 **확인을 묻지 말고 바로 적용**한다. (2026-06-08 사용자 지시 "just apply the code without asking")

**Why:** 사용자는 빠른 반복을 원함. 매번 "이렇게 할까요?" 확인을 받는 것보다 합리적 기본값으로 바로 실행하고 결과를 보고하는 걸 선호.

**How to apply:**
- 의도가 분명하면 AskUserQuestion·확인 질문 없이 바로 편집/실행하고 결과만 보고.
- 합리적 기본값을 고르고 "X로 했음"이라고 사후 명시.
- 단, 되돌리기 어렵거나 외부로 나가는 행위(Slack 전송, 푸시, 삭제, 대량 변경)는 예외적으로 한 번 확인 — 그 외 로컬 코드/파일 작업은 묻지 않는다.
