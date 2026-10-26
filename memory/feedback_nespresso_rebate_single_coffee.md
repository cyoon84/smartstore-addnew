---
name: feedback-nespresso-rebate-single-coffee
description: 네스프레소 Last Chance Rebate 는 "coffees" 표기여도 한 종류 전용 — 안분 금지, 사장님께 확인
metadata:
  type: feedback
---

**네스프레소 영수증의 `Last Chance Rebate - coffees` 는 복수형이어도 실제로는 한 커피에만 적용된다.**
지불액 비율로 안분하지 말고 **그 품목에서 직접 차감**한다.

**Why:** 리베이트·프로모는 품목 전용 할인이지 공통비가 아니다(§19-3 — 세금·배송 같은 오버헤드만 안분).
안분하면 슬리브 단가가 양쪽 다 틀어져서, 그 캡슐이 나가는 주문들의 손익이 통째로 어긋난다.

**How to apply:** 어느 커피인지는 영수증에 안 나온다 → **사장님께 확인하고 확정**한다.
확인 전에는 안분값을 임시로 쓰되 "확인 필요"로 플래그하고, 답이 오면 재계산 + 재고 시트 단가까지 갱신.

- 2026-10-02 — 사장님: *"rebate는 tanzania만 적용된다"*
- 2026-10-21 — 사장님: *"유자만 적용된거야"* (10/20 주문, −$22.50)
  안분 유자 ₩4,813·메이플 ₩11,935 → 실제 **유자 ₩4,134·메이플 ₩14,648**

[[project_nespresso_workflow_settlement]] · [[feedback_cogs_fx_purchase_date]]
