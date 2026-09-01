---
name: feedback-hanmi-hs-code-food-210690
description: 한미 HS CODE — 음식·영양제는 21 이 아니라 210690 (2026-09-01 출고분부터)
metadata:
  type: feedback
---

한미택배 공지로 **음식·영양제 품목 HS CODE 가 `21` → `210690` 으로 변경**됐다 (2026-09-01 출고분부터).

- 대상: 식품·스낵·과자·커피·초콜릿·영양제 전부.
- `~/smartstore-project/templates/product-mapping.xlsx` 의 기존 `21` **211건을 일괄 변경 완료**
  (백업 `.bak_20260901`). hanmi-flow `convert.py` 가 이 매핑을 읽으므로 자동 반영된다.
- **새 SKU 를 매핑에 추가할 때 `21` 을 쓰지 말 것.**
- 다른 코드는 불변: 세제 `340120` · 플라스틱잡화 `392490` · 의류 `62` · 가방 `420212` ·
  신발 `640419` · 화장품 `330610`/`330499` · 기타잡화 캐치올 `761510`.

**Why:** 통관 코드가 틀리면 한미 등록·통관에서 걸린다. 매핑 파일이 유일한 소스라 여기만 고치면 전 배치에 적용된다.

**How to apply:** 매핑 누락 상품을 새로 추가할 때 식품/영양제면 `210690`. HS 코드 셀은 텍스트 서식
(`number_format='@'`)으로 넣어 앞자리 0 을 보존한다. [[feedback_hanmi_packing_fee]] · [[feedback_overseas_shipping_baseline]]
