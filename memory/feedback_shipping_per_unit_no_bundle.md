---
name: Shipping "per-unit N, no bundle rule" pattern
description: 사용자가 "배송비 N원 (몇 개당 그런 거 없이)" / "수량당 N원" 명시 시 번들 룰 없이 단순 곱셈 (1개 N원, 2개 2N원, 3개 3N원…). 네이버 배송 설정도 "수량당 N원"으로 등록.
type: feedback
originSessionId: 626bb7d0-2d38-45b3-92f5-7b96c476c259
---
**규칙:** 사용자가 **"배송비 N원 (몇 개당 그런 거 없이)"** 또는 **"수량당 N원"** / **"개당 N원, 묶음 없음"** 으로 명시하면 번들/묶음 룰 없는 **단순 곱셈** 적용 (1개=N원, 2개=2N원, 3개=3N원…).

**Why:** 단가 낮고 부피·무게 작은 SKU(미니 초콜릿 박스 등)는 묶음할인 의미가 없어서 사용자가 "몇 개당 그런 거 없이"라고 명시함. 2026-05-17 Nestlé Snack Size Collation 케이스에서 학습.

**How to apply:**
- product_info.json의 `shipping_policy.shipping_krw_per_unit = N`, `bundle_rule = null`
- 등록정보.md / products_master.csv `shipping_policy` 컬럼은 "**N원/수량당 (번들 없음)**"
- 기존 묶음할인 패턴 ("3개당 15,000원" 등 — Haribo 케이스)과 명확히 구분
- 사용자가 "묶음할인" / "M개당" 표현 쓰면 별도 패턴

**🔑 "수량당 N (단순 곱셈)" vs "flat N (균일)" 구분 (2026-06-20 트위즐러 케이스 — 정반대 주의):**
- **수량당/단순곱셈** ("수량당 N원", "몇 개당 그런 거 없이") → 네이버 **수량별, 부과수량(AP)=1**. 사면 살수록 N씩 늘어남(1개=N, 2개=2N).
- **flat/균일** ("그냥 flat N원", "균일 N원", "개수 상관없이 N원", "주문당/건당 N원") → 네이버 **유료, 부과수량(AP)=blank(공란)**. 몇 개를 사든 배송비 N원 한 번.
- 둘 다 "개당 없이" 류로 들리지만 의미가 반대. 구분 신호어: `flat`·`균일`·`개수 상관없이`·`수량 무관`·`주문당`·`건당` = **유료(AP 공란)**.
- 일괄엑셀: `bulk.shipping_type:"유료"`·`shipping_fee:N` 으로 명시하면 `build_bulk_excel.py` 가 AP 칸을 자동 공란 처리(수량별 유형 아닐 때). `resolve_shipping()` 도 위 신호어 문자열을 유료/공란으로 파싱. ([[feedback_bulk_upload_excel]])
- 사용자 명시: "트위즐러는 그냥 10000원 (개당 없이 그냥 flat — 이럴 때는 AP컬럼은 blank)".
