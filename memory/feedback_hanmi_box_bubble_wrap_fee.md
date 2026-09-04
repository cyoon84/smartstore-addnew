---
name: feedback-hanmi-box-bubble-wrap-fee
description: 한미 박스비·에어캡 개당 $1 — 청구서 TOTAL에 없고 remaining balance로만 확인된다
metadata:
  type: feedback
---

**한미 배송비에는 `박스비`·`에어캡` 이 개당 $1.00 씩 별도로 붙는다.**
패킹료 $5([[feedback_hanmi_packing_fee]])와 **다른 항목** — 패킹은 인건비, 이건 자재비다.

```
실배송비($) = 8 + 4.5×(Paid−1kg) + 통관 1 + 패킹 5 + (박스비 + 에어캡 개수) × 1.00
```

**🚨 청구서 TOTAL 에는 안 들어가 있다.** 자재비는 `PAYMENT METHOD` 옆
**remaining balance(예치금 잔액)** 에만 반영되므로, TOTAL 만 보면 영원히 안 보인다.

**검산법:** `이전 잔액 − 이번 잔액 − 배송료 TOTAL = 자재비`. 0 이 아니면 원인을 찾는다.
> 2026-09-05 실측 — $620.59 − $361.75 − **$52.00**(박스 27 + 에어캡 25) = $206.84 ✅

**개수는 무게가 아니라 부피에 비례한다.**
파인솔 5.18L ×5(28kg) = 박스4 + 에어캡12 · 파인솔 1.41L ×12(18.5kg) = 박스5 + 에어캡10 ·
소액 단품(1kg) = 박스 2~3, 에어캡 0. 액체·부피 큰 품목일수록 에어캡이 붙는다.

**Why:** 이 항목을 몰라서 **두 배치를 ₩69,893 과대 계상**했다 —
9/1(박스 19개 $19.00) 순이익 161,437 → **142,718** · 9/4(52개 $52.00) 252,402 → **201,227**.
사장님이 *"박스비, 에어캡 칼럼도 봐"* → *"206.84 / 620.59는 remaining balance"* 로 짚어줘서 발견.

**How to apply:** 한미 오피셜을 읽을 때 **배송료 TOTAL 만 적고 넘어가지 않는다.**
①박스비·에어캡 컬럼을 같이 읽고 ②잔액 차감액으로 검산해 ③두 값이 맞아떨어질 때만 실배송비를 확정한다.
**청구서 TOTAL 이 곧 실지출이라고 가정하지 말 것** — 예치금에서 더 빠져나간다.

[[feedback_hanmi_packing_fee]] · [[feedback_overseas_shipping_baseline]] · [[feedback_hanmi_list_weight_not_paid_weight]] · [[project_order_settlement]]
