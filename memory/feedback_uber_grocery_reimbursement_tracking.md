---
name: feedback_uber_grocery_reimbursement_tracking
description: "우버 그로서리 reimbursement — 영수증 먼저 기록, 확정메일 오면 나중에 매칭"
metadata:
  type: feedback
---

사장님이 Uber 배달파트너 활동 중 그로서리 대납 주문 영수증을 채널A(`chulhee.y+receipt@gmail.com`)로 포워딩("Uber grocery"/"Uber reimbursement"/"Receipt uber grocery" 등 제목)하면, **스마트스토어 COGS와 무관**(개인 우버 사이드 정산)이라 장부에 원가로 기입하지 않는다 — 이 원칙은 그대로 유지.

**2026-08-06 신규 규칙 — "일단 하고 나중에 확인메일 오면 매칭":**
- 영수증 포워딩을 발견하면 **곧바로 승인확정 메일(`A message from Uber`, `*.email-support.uber.com` 발신, "You'll be receiving CA$X.XX for Order Number XXXXX")을 찾으려 하지 말고**, `output/inventory/우버_그로서리_reimbursement.md` 에 PENDING 한 줄로 기록만 해둔다.
- 나중에(같은 세션이든 다음 세션이든) `A message from Uber` 확정 메일이 오면, 날짜·금액으로 가장 가까운 PENDING 행을 찾아 CONFIRMED 로 갱신 + 금액·Order Number 채운다.
- 이 확정 메일들은 발신 주소가 매번 다른 랜덤 문자열(`contact_<uuid>@email-support.uber.com`)이라 **from 검색이 아니라 subject:"A message from Uber" + 날짜범위**로 찾는다.

**Why:** 2026-08-06 세션에서 사용자가 "우버 영수증도 확인해줘"라고 해서 검색했는데 최근 포워딩 1건(8/6 02:38)에 대한 확정 메일이 아직 안 와서 이전 확정 메일(347DD $66.72)과 잘못 묶어 보고했다가 "하나 더있어... 이놈아"로 지적받음. **포워딩과 확정메일은 시차가 있고 항상 1:1로 바로 안 붙는다** — 무리하게 즉시 매칭하려 하지 말고 트래커에 PENDING으로 남겨두는 게 맞다.

관련: [[project_bookkeeper_expense_tracker]]
