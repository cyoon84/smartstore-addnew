---
name: feedback_settlement_slack_dm
description: 정산 순이익 확정 시 Slack DM — 나는 확정 시, 김아름은 한미 최종 배송비 확인 후 딱 한 번만
metadata:
  type: feedback
---

출고일 정산(`output/settlement/정산_<date>.md`)의 순이익이 확정되면 정산 요약(매출·COGS·실배송비·순이익)을 **Slack DM**으로 보낸다. 손익 숫자라 팀 채널(#all-핀치마트 등) 금지, **DM 한정**.

**받는 사람 · 발송 시점 (2026-07-10 정정):**
- **Chul(나) `U0B1TFC186Q`** — 순이익 확정될 때. (추정 잠정단계는 파일 기록만, 안 보냄.)
- **🔑 김아름 `U0B696MML21`(r0430@naver.com)** — **한미에서 최종 배송비 리스트가 실제로 와서 확인된 뒤, 딱 한 번만.** 추정 무게 기반 잠정단계에선 김아름에게 **보내지 말 것**(그 단계는 나에게만).

**Why:** 김아름에겐 왔다갔다 하는 잠정치 말고 **확정된 최종 손익 한 번**만 전달. (2026-07-10 오늘 김아름에게 추정 "일단 공식" 단계 + 한미 최종 단계 **두 번** 보낸 실수 → 앞으로 김아름은 한미 최종 확인 후 1회.)

**How to apply:** 한미 최종 배송비 리스트 도착·확인 → `order_settlement.py --shipping-cost <실값>` 으로 순이익 최종 기록 → 요약을 `slack_send_message` 로 **U0B1TFC186Q + U0B696MML21** 각 DM. 그 전(추정) 단계엔 U0B1TFC186Q 에게만. [[project_order_settlement]]
