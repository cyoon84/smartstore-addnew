---
name: feedback-mapping-from-source-page
description: product-mapping 누락 상품은 소스 페이지를 먼저 열어 실제 제품명·단가를 쓴다 — 성분으로 카테고리 추측, 합계에서 단가 역산 금지
metadata:
  type: feedback
---

`convert.py` 가 `MISSING:` 을 뱉거나 캘거리 양식의 `제품 / 브랜드` 칸을 채울 때,
**성분·형제 품목만 보고 영문명이나 단가를 지어내지 않는다.** 소스 페이지를 열어 거기 적힌 것을 그대로 쓴다.

1. **소스 페이지를 먼저 연다** — costco.ca 는 `curl_cffi` impersonate=`chrome` 으로 200
   ([[feedback_source_price_verification]]), walmart.ca 는 Aside ([[feedback_walmart_lookup_via_aside]]),
   브랜드 Shopify 몰은 `products.json`.
2. **영문명 = 실제 제품명.** 용도 카테고리(`EYE VITAMIN`·`JOINT VITAMIN`)를 성분으로 추론해 짓지 않는다.
   🔑 형제 매핑이 정답이라는 보장이 없다 — 웨버네추럴스 8건 중 루테인 제아잔틴만 봐도
   하나는 `MULTIVITAMIN`, 하나는 `EYE VITAMIN` 이라 기준 자체가 없다.
3. **단가 = 영수증·상품페이지에 찍힌 숫자.** 합계에서 역산 금지. 안 보이면 "안 보인다"고 보고한다.
4. 소스를 열어도 확정 안 되면 **매핑에 넣기 전에 사장님께 묻는다** —
   order-2task-todoist·hanmi-flow 스킬의 "유추한 내용 보여주고 확인 요청" 절차를 건너뛰지 않는다.

**Why:** 2026-11-27 캘거리 배치에서 `웨버네추럴스 블루베리 플러스 빌베리 550mg 120캡슐 2병`(13887598214)이
매핑에 없자 "빌베리=눈" 이라는 상식만으로 `EYE VITAMIN / WEBBER NATURAL` 을 **확인 없이** 넣고 캘거리 파일까지 만들었다.
사장님: *"박수호 eye vitamin은 무슨근거로 한거야?"* → 코스트코 URL 을 던지며 ***"보고 유추좀 잘 하지??"***
열어보니 코스트코 분류는 **Antioxidants**(눈 카테고리 아님), 설명 첫 줄도 "provide a source of antioxidants",
눈 효능은 여러 용도 중 하나였고 **만성정맥부전(다리 혈행) 효능도 같이** 적혀 있었다.
정답은 카테고리가 아니라 **실제 제품명 `BLUEBERRY PLUS WITH BILBERRY`** 였다(사장님 제안) — 카테고리를 고민할 이유가 없었다.

같은 날 같은 실패를 또 했다: 11/25 월마트 영수증에 네스카페 골드 에스프레소 금액이 안 찍혀 있자
품목합 $54.89 에서 역산해 **$11.97** 로 올렸는데 주문상세 PDF 에는 **$15.97** 이었다.
둘 다 **열어볼 수 있는 1차 소스를 안 열고 추론으로 메운** 같은 실패다
([[feedback_source_price_verification]] · [[feedback_new_sku_dedup_product_id]] 의 "확인 실패 ≠ 없음" 과 같은 결).

**How to apply:** 매핑 누락을 만나면 소스 URL 부터 연다. 제품명을 찾으면 그걸 쓰고(카테고리 고민 불필요),
단가는 페이지·영수증의 숫자를 쓴다. 둘 중 하나라도 못 구하면 넣지 말고 보고한다.
LEARNED_RULES §18-5-2.
