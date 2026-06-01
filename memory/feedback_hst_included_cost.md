---
name: HST-included cost — skip HST gross-up
description: 사용자가 "원가 HST 포함" 또는 "HST included"라고 명시하면 HST를 추가로 더하지 않고 cost를 그대로 sell_pre_fee 계산에 투입
type: feedback
originSessionId: dd723718-a945-4ed3-9895-822c0b6a7489
---
원가가 이미 HST를 포함한 가격이라고 사용자가 명시한 경우(예: "HST 포함 16.99 CAD", "tax-in price"), HST 13%를 다시 곱해서 cost를 키우지 않는다. 그대로 마진을 더하고 네이버 수수료 6.6% gross-up만 적용.

**Why:** 일부 매장(Costco 회원가, Loblaws 일부 회원가, Wholesale 가격)은 매대 표시가 세금 포함 가격으로 나오기도 함. 평소 룰(가격은 세전)을 그대로 적용하면 사용자가 받는 마진이 13%만큼 부풀려진 계산이 되어 실제보다 비싼 한국 판매가가 나옴.

**How to apply:**
- 사용자가 가격 줄 때 "HST 포함" / "tax-in" / "세금 포함" 같은 단서 있으면 HST 가산 스킵.
- 그래도 `tax_label`에는 "HST 13% (included in cost)" 또는 "HST included" 로 표기해서 추후 추적 가능.
- 산출식: `(cost_with_tax_already + markup) / 0.934 × FX_KRW → round_100`
- 명시 안 되어 있으면 평소대로 세금 매번 물어보고 세전으로 처리.

**예시** — Aveeno Baby Lotion 532mL (2026-05-16):
- 원가 16.99 CAD (HST 포함) + 마진 3 CAD = 19.99 CAD pre-fee
- 19.99 / 0.934 = 21.4026 CAD
- × 1,070 KRW = 22,901 → round_100 → ₩22,900
