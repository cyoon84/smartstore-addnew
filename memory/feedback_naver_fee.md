---
name: 네이버 스마트스토어 수수료 6.6%
description: 스마트스토어 상품 가격 계산 시 항상 6.6% 수수료를 판매가에 gross-up으로 포함
type: feedback
originSessionId: 0dff62f1-9f86-4c15-9a25-83806397b95f
---
스마트스토어 판매가는 항상 네이버 수수료 6.6%를 차감 후 마진이 남도록 계산한다.

**계산식 (가격 규칙에 적용):**
```
sell_pre_fee = cost_original + markup            (CAD or USD 단위)
sell_original = sell_pre_fee / (1 - 0.066)       (수수료 gross-up)
sell_krw = ceil_10(sell_original × exchange_rate)
```

예시 (Chosen Foods Avocado Mayo, CAD $12.99 + $5 마진, 환율 1,083):
- 12.99 + 5 = 17.99
- 17.99 / 0.934 = 19.26 CAD
- 19.26 × 1083 = 20,859.85 → ceil_10 → ₩20,860

**Why:** 사용자가 "$5 남기고 싶다"고 할 때 그 $5는 네이버 수수료 차감 후의 순이익이어야 의미가 있음. 수수료 적용 안 하면 실제 수익이 6.6% 깎임. 사용자가 명시적으로 빼먹지 말라고 지적함.

**How to apply:** product-detail-page-ko 워크플로 가격 계산 단계에서 항상 자동 적용. product_info.json의 pricing 블록에 `platform_fee_rate: 0.066`도 함께 기록. 사용자가 "수수료 빼" / "수수료 0%"라고 명시한 경우만 예외.
