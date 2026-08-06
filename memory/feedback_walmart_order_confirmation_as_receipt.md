---
name: feedback_walmart_order_confirmation_as_receipt
description: "Walmart.ca 'Thank you for shopping with us!' 주문확인 메일 = 품절 없으면 최종 영수증으로 취급"
metadata:
  type: feedback
---

Walmart.ca 직접주문(DoorDash 아닌 자체 배송)의 **"Thank you for shopping with us!" 주문확인 메일**은 본문에 "Order summary & receipt" 헤딩과 함께 Item subtotal·(있으면 Shipping·HST)·Total이 이미 다 나온다.

**판단 규칙 (2026-08-06 사용자 확정):**
- **품절 없이 주문한 물건이 다 있으면** → 이 주문확인 메일을 **그대로 최종 영수증으로 써도 된다**. "배송 완료" 메일까지 기다릴 필요 없음.
- **매장에 일부 품절이 있으면** → 나중에 **2차 영수증(조정본)**이 온다 — 그때 최종 금액이 갱신되니 그걸 최종으로 삼는다.
- 품절 여부는 배송완료 메일("Your Walmart order was delivered")의 품목 리스트를 최종 확인 시 대조하거나, 2차 금액조정 메일이 왔는지로 판단.

**품목명 추출 팁:** 주문확인 메일엔 품목별 **단가가 없고** 이미지 alt 텍스트로 품명만 나온다(`<img alt="상품명">`, 수량은 바로 앞 배지 `<p>N</p>`). 정규식으로 `width:16px;margin:0;">\s*(\d+)</p>.*?alt="([^"]+)"` 매칭하면 수량+품명 페어를 순서대로 뽑을 수 있음. 단가가 없으면 합계만으로 COGS 처리(품목별 안분 억지로 하지 말 것 — 근거 없는 숫자 만들지 않기).

> 2026-08-06 김정희+박수현 공동주문(Order #600000104248254, $58.25, 7품목) 사례 — 품절 없이 전량 확인, 주문확인 메일을 최종 영수증으로 COGS 반영.

관련: [[project_bookkeeper_expense_tracker]]
