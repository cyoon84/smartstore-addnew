---
name: pre-sale-regular-price
description: "사용자가 \"세일전 가격으로 책정\"이라고 명시 시 매대 세일가 무시, 세일전 정상가를 원가로 채택 + 등록정보·product_info에 정상가/세일가 둘 다 기록"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2b40431d-a3c3-4131-b8f4-a06980e1f6f2
---

사용자가 **"X.XX 세일전 가격으로"** / **"세일 끝나도 안정적으로"** / **"정상가 기준으로 책정"** 으로 명시하면, 현재 매대 표시 세일가를 무시하고 세일전 정상가를 원가로 채택한다.

**Why:** 매장 세일은 일시적(예: Walmart "new lower price" 프로모션). 세일 종료 후에도 가격 변경 없이 운영하려면 정상가 기준 책정이 안정적. 세일 기간 동안은 실 마진이 더 커지는 효과. 2026-05-27 Downy Calm Lavender & Vanilla Bean Mega Sheet 케이스 — 매대 세일가 $10.99, 정상가 $15.99, 정상가로 책정.

**How to apply:**
- 가격 계산: 정상가 사용 (HST·마진·gross-up 평소 룰대로)
- `product_info.json`: `cost_original` = 정상가, `cost_pricing_basis: "pre-sale regular price"`, `current_sale_price_cad`·`regular_price_cad` 둘 다 기록, `tax_label`에 "(regular pre-sale price — 매대 세일가 $X / 정상가 $Y 기준)" 명시
- `등록정보.md`: "가격 책정 메모 — 세일전 정상가 채택" 섹션 + 정상가/세일가 모두 + 책정 사유 + 추적용 날짜
- 사용자 명시 없으면 평소대로 매대 표시가(세일가 포함) 그대로 사용

LEARNED_RULES.md §12 정식 룰화. 관련: [[naver-fee]], [[hst-zero-rated]], [[price-patterns]].
