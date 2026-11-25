---
name: feedback_grocery_no_substitute
description: 온라인 식료품 주문(PC Express·Instacart·Walmart 등)은 무조건 Do not substitute — 자동 대체는 그대로 오배송
metadata:
  type: feedback
---

**온라인 식료품 장바구니는 모든 줄을 `Do not substitute`(대체 안 함)로 둔다.** 예외 없음.
담은 직후 **대체 설정까지 확인하는 것이 담기 작업의 일부**다 — 담았다고 끝이 아니다.

**Why:** 사이트 기본값이 품목에 따라 **`Choose a substitute for me`(알아서 대체품 보내기)** 로 들어간다.
우리는 **고객이 지정한 그 SKU** 를 사서 한국으로 보내는 구조라, 매장이 임의로 바꿔 보낸 물건이
그대로 **오배송**이 된다 — 향·맛·용량이 다른 물건이 와도 모르고 나간다. §0-∞(제품명 원본 그대로)의
**구매 단계 버전**이다. 사장님 지시(2026-11-25): **"무조건 do not substitute"**.

> 2026-11-25 정예은 RCSS 장바구니 — 5줄 중 **크레페 100g ×2** 와 **데카던트 1kg** 두 줄이
> 사이트 기본값 `Choose a substitute for me` 로 들어가 있었다(나머지 3줄은 기본이 Do not substitute).
> 담기만 하고 넘어갔으면 품절 시 다른 쿠키가 와서 그대로 발송될 뻔했다.

**How to apply:**
- Aside 로 장바구니를 담을 때 프롬프트에 **"모든 줄 대체설정을 Do not substitute 로"** 를 같이 넣는다.
- 담은 뒤 보고에 **줄별 대체설정 값**을 받아서 전부 `Do not substitute` 인지 확인한다.
- 품절이면 대체품을 받지 말고 **"품절" 로 보고** → 다른 매장에서 사거나 사장님 판단
  ([[feedback_check_inventory_before_asking]] 처럼 임의 판단 금지).
- PC Express(RCSS·No Frills·Loblaws)뿐 아니라 Instacart·Walmart·Uber 등 **대체 옵션이 있는 모든 채널**에 적용.

관련: [[feedback_product_name_verbatim]] · [[feedback_walmart_lookup_via_aside]]
