🚨 **원가·규격은 1차 소스 2개로 교차확인한다. 검색 스니펫 가격은 시점 불명 캐시다.**

**① 검색 스니펫 가격 금지.** WebSearch 요약에 뜬 가격·재고는 언제 크롤한 것인지 알 수 없어
**이미 끝난 세일이 살아있는 것처럼 보인다.** 원가 후보는 **서로 다른 1차 소스 2곳**에서 확인하고,
교차확인이 안 되면 그 후보를 버린다([[feedback_new_sku_dedup_product_id]] 와 같은 원칙).

> 2026-08-21 웨버 아스타잔틴 — 스니펫 `"Price: $51.99 (after $13 off, was $64.99)"` 를 믿고 세일가로
> 산출물을 만들려 했다. 사장님이 *"세일가 51.99는 무슨 기준으로 한거지??"* 로 묻지 않았으면
> **존재하지 않는 가격**으로 등록할 뻔했다. 실제는 `aggregatedDiscountAmt: 0` · $64.99 · `OutOfStock`.
> 반대로 같은 날 에티튜드 데오드란트는 공식몰 $12.95 + well.ca $12.99 가 일치해 원가를 확정했다.

**② `costco.ca` 는 `curl_cffi` 로 열린다 — "403" 기록은 폐기.**
```python
from curl_cffi import requests
r = requests.get(costco_url, impersonate="chrome", timeout=45)   # 200
```
JSON-LD `offers.price`(정가) · `displayPrice.aggregatedDiscountAmt`(0이면 세일 아님) ·
`availability`(OutOfStock 여부) · `Item <번호>` · `Online Only` 배지를 그대로 읽는다.
⚠️ 온라인가 ≠ 창고 매대가(K2+D3: 온라인 $27.99 vs 창고 $24.99).

**접근성 실측 (2026-08-21):** ✅ costco.ca · metro.ca · safeway.ca · gianttiger.ca · well.ca ·
ca.attitudeliving.com / ❌ walmart.ca(봇페이지) · yourindependentgrocer.ca(403) · smartstore.naver.com(429).

**③ 공식몰 옵션 표기 ≠ 라벨이면 라벨이 정본.** 제품컷을 확대해 용량·향 표기를 육안 판독하고
사이트 메타값과 대조한다. 어긋나면 라벨을 쓰고 `product_info.size_correction` 에 근거를 남긴다.
> 에티튜드 데오드란트 — 공식몰 Format 옵션 `85g` vs 라벨 `75 g / 2.64 OZ`. 국내 리스팅도 75g →
> **75g 채택.** 85g 은 같은 브랜드 Super Leaves 라인 용량이었다(라인이 다르면 용량도 다르다).

**④ 커클랜드는 "한국 코스트코가 취급하나" 를 먼저 본다.** 커클랜드는 코스트코 코리아에도 유통망이
있어 한국 매대에 있으면 진다. 우리가 이긴 커클랜드(믹스넛버터·코코넛오일·피스타치오·그래놀라·
프로바이오틱)는 전부 한국 코스트코 미취급 품목이었다. **웨버네추럴스는 캐나다 코스트코 전용이라
한국에 아예 없어서** 8종이 다 통했다 → **영양제는 커클랜드보다 웨버를 먼저 뒤진다.**
> 2026-08-21 커클랜드 코엔자임Q10 200mg 225정 — 국내 직구 ₩69,840~86,800 만 보고 "우위" 로 판정했으나
> **한국 코스트코가 400mg×240캡을 ₩31,550~34,800** 에 판매 중. 함량 2배·정수 더 많고 가격은 2/3 → 탈락.

LEARNED_RULES §0-G-3 · §0-G-4 · §0-G-5. 관련: [[feedback_new_sku_dedup_product_id]] ·
[[feedback_domestic_price_check]] · [[reference_naver_openapi]]
