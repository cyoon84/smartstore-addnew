---
name: feedback_walmart_lookup_via_aside
description: 월마트(walmart.ca) 가격·재고·검색은 무조건 Aside — 상품페이지가 curl_cffi 로 열려도 내 검색 파싱은 false negative 가 난다
metadata:
  type: feedback
---

**월마트 조회는 전부 `aside exec` 로 넘긴다.** 내가 직접 검색하지 않는다.
내 `curl_cffi` 는 **Aside 가 준 URL 로 사진을 받아 라벨을 눈으로 읽는 보조 용도만** ([[feedback_verify_photo_mapping]]).

**Why:** walmart.ca 는 `curl_cffi` impersonate="chrome" 으로 **상품페이지가 200 으로 열린다**(338KB 정상,
`__NEXT_DATA__` 에서 `Size`·`Assembled Product Weight`·`og:image` 까지 뽑힘). 그걸 보고 "월마트는 이제 내가
직접 된다" 고 판단해 **검색까지 직접 돌린 것**이 사고 원인이다. 상품페이지 fetch 와 검색 결과 파싱은 별개다 —
내 파서는 `__NEXT_DATA__` 에서 `name`+`price` 키를 가진 dict 를 긁어 **검색 결과 전체를 담지 못한다.**

> 2026-11-25 — 정예은 주문의 리츠를 찾느라 `ritz holiday`·`ritz fudge covered`·`ritz chocolate fudge crackers`
> 를 내 파서로 돌리고 **"월마트 온라인엔 리츠 홀리데이가 안 잡힙니다"** 라고 사장님께 단정 보고했다. 실제로는
> `RITZ Fudge Covered Crackers, Baked in Canada`(item **6000203824246**, 212g $2.98, LIMITED EDITION)가
> 멀쩡히 있었고 사장님이 URL 을 직접 던지며 *"이 멍청아"* → **"너 검색 못하니까 월마트는 무조건 aside한테 시켜."**

**How to apply:**
- 월마트 가격·재고·검색·제품 유무 판정 → `aside exec --permission full-access` (프롬프트에 URL·확인항목 명시).
- 🔑 **"없다 / 안 잡힌다" 는 부정 판정을 내 검색 결과만으로 내리지 않는다** — §25-1 [[feedback_new_sku_dedup_product_id]]
  "확인 실패 ≠ 없음" 과 같은 구조. fetch 200 은 **그 페이지가 열렸다**는 뜻일 뿐 **검색이 완전하다**는 뜻이 아니다.
- 다른 사이트도 같은 선으로 구분한다: **상품페이지 직접 fetch 가 되는 것**(코스트코·메트로·Shopify 몰)과
  **그 사이트 검색을 신뢰할 수 있는 것**은 별개다.
- 월마트 사양창에 **용량 항목이 아예 없는 제품이 흔하다**(리츠 212g·226g 둘 다 `Size` 없음) — 그때는 라벨 사진과
  설명문으로 확인하고 **"사양 표기 아님"** 을 명시한다 ([[feedback_source_price_verification]]).

관련: §0-G-6 (docs/LEARNED_RULES.md) · [[feedback_aside_registration_handoff]]
