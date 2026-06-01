---
name: feedback-slack-delivery
description: 신규상품 등록 완료 후 등록정보.md 전체를 Slack
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1a936e6e-4c72-41e1-b70e-c9d0e26c891d
---

신규 스마트스토어 상품 등록 워크플로(smartstore-addnew)를 끝내면, 산출한 `_등록정보.md`의 **전체 내용(형식 A)**을 Slack **#new-item** 채널에도 보낸다.

**대상:** Slack 채널 `#new-item` (channel_id `C0B5F379DSB`, 워크스페이스 w1777975201-sap125741).
**형식:** A = 등록정보.md 전체 (상품명·가격·태그·상세카피·주의사항까지). 핵심 요약본(B) 아님.
**분할:** Slack 메시지 1건당 5000자 제한 → 등록정보가 길면 첫 메시지 + 스레드 답글로 이어 보낸다.
**전송 방법 (2026-05-31):** `scripts/slack_notify.py --file <등록정보.md>` 사용. Slack 은 표준 마크다운을 렌더 안 하므로(`#`·`**`·`|표|` 가 raw 기호로 깨져 가독성 X) 스크립트가 **.md 를 Slack mrkdwn 으로 자동 변환**(헤더→볼드, `**`→`*`, 표→`• *첫칸* — 헤더: 값` 불릿, `[t](u)`→`<u\|t>`, `---`→구분선) 후 webhook 전송. 변환 끄려면 `--raw`. (2026-05-31 사용자 피드백 — "markdown syntax 그대로 보내니 심볼 난무해서 읽기 힘들다".)

**Why:** 2026-05-24 사용자가 "모바일로 사진 보냈을 때 등록정보를 markdown으로 만들고 Slack으로도 보내달라"고 요청, 대상/형식으로 "#new-item 채널 / A" 명시.
**How to apply:** 매 등록 건 산출물 생성 직후 자동 수행. 사용자가 다른 채널·형식을 지정하거나 "Slack 보내지 마"라고 하면 그때만 예외.
