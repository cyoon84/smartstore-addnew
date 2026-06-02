---
description: (배치) smartstore-investigate-new-item 의 products.json 소싱 리스트 → 스마트스토어 등록 4종 산출물 일괄 생성 + Slack 보고
argument-hint: [crawl 폴더 경로 또는 날짜 (생략 시 최신 crawl_*) / 옵션: 마진·배송·세금 오버라이드]
---

`smartstore-investigate-new-item` 조사 에이전트가 만든 **소싱 후보 리스트(`products.json`)** 를 받아,
한 번에 여러 SKU 의 스마트스토어(finchmart_ca) 등록 산출물 4종을 만들고 Slack 으로 보고한다.
입력: $ARGUMENTS

`/register-agents` 의 **메인 오케스트레이터 + 전문 서브에이전트** 모델을 그대로 따르되, **단건 dispatch 대신
배치 입력(products.json)** 을 소비한다. 산출물·규칙·저장 위치는 `/register` 계열과 100% 동일.

## 입력 소스
- 기본: `/Volumes/External/claude/smartstore-investigate-new-item/output/crawl_<날짜>/products.json`
  (인자 없으면 **가장 최근 `crawl_*` 폴더** 사용).
- 각 항목 필드: `store`(조사 출처), `folder`, `name_en`, `name_ko`, `brand`, `size`, `price`,
  `category`, `image_url`, `source`, `selling_point`, **`prices`**(walmart/loblaws/nofrills 채널별 가격 문자열).
- 같은 폴더의 `walmart/`·`loblaws/`·`nofrills/` 하위에 참고 이미지가 있을 수 있음.

## 가격 규칙 (이 커맨드 전용 — 사용자 지정)
채널별 `prices` 를 파싱해 **그 SKU 를 실제로 취급하는 매장 수**를 센다.
("미취급(PB)"·"미확인"·"동일맛 미취급"·낱봉 등 **다른 규격/미취급 표기는 카운트 제외**.)

| 취급 매장 수 | 원가(cost) | 마진(markup) |
|---|---|---|
| **2곳 이상** (셋 다 or 셋 중 둘) | 취급 매장 중 **가장 비싼 가격** | **+$1.50** |
| **1곳만** | 그 매장 가격 | **+$2.00** |

- 멀티팩 vs 낱봉처럼 **규격이 다르면 다른 SKU** — 동일 SKU 취급으로 세지 않는다 (예: Hawkins 36봉 멀티팩은 월마트만 → 1곳).
- 묶음가(2/$8 등)는 무시하고 **단품가** 사용 (LEARNED_RULES §8).
- 세금: **카테고리 자동** — 스낵/칩/캔디 = HST 13%, 커피·홍차·허브티 = 0% (사용자가 매번 확인 룰을 배치용으로 사전 확정. 단 애매한 카테고리는 사용자에게 확인).
- 배송비: 기본 **수량당 ₩15,000** (사용자 지시로 변경 가능 — `prices` 무관, 인자/대화로 오버라이드).
- 계산은 반드시 `scripts/price_calc.py std --cost <최고가> --markup <1.5|2.0> --fx <현재환율> --tax <0|13> --json`. 손계산 금지.

## 파이프라인 (순서 고정)
1. **리스트 로드·파싱** — products.json 읽어 각 SKU 의 취급 매장 수·최고가·세금 카테고리 산정. ASCII 슬러그 부여.
2. **환율 확인** — 현재 CAD→KRW 확인해서 `--fx` 에 사용.
3. **가격 일괄 계산** — 위 표대로 `price_calc.py` 로 전 SKU `sell_krw`·검산 확보.
4. **국내 시세(§0-A) — 선택적·브랜드품 위주.** 캐나다 PB(President's Choice·No Name)·캐나다 한정 NB 는
   "국내 미유통 — §0-A 스킵 적용" 1줄로 스킵. **국내 유통 가능성 있는 NB**(Tostitos·Ruffles·Tim Hortons·McCafe·
   Red Rose 등)만 `market-researcher` 병렬 호출 → 경쟁력 보고. **배송비가 도착가 열세의 원인이면 그 사실을 보고에 명시**
   (제품가 경쟁력과 분리해서). 명시적 GO 또는 사전 배치 승인 하에 진행.
5. **작성** — SKU 별 `listing-writer` 호출(병렬, 5개씩 배치 권장). 입력: products.json 항목 데이터 + 확정 sell_krw +
   배송규칙 + 슬러그 + 출처(일반 유통: 상품명에 국가·매장명 넣지 않음). 모델명 = `name_en`(영어 풀네임).
6. **조립·저장** — 메인이 `output/` 루트에 슬러그 prefix 로 3종 저장 후 `python3 scripts/organize_output.py --apply`
   → `output/new-item/<slug>/` 분류:
   - `<slug>_등록정보.md` (상품명·모델명·가격산식·검산·태그·카테고리·배송·이미지 URL·소싱 채널가 비교·§0-A 결과)
   - `<slug>_detail.html` (listing-writer fragment)
   - `<slug>_product_info.json` (products.json 원본 + price_calc `--json` pricing 블록 + 소싱 메타)
7. **Slack** — #new-item 에 배치 요약(제품·판매가·도착가·§0-A 신호) 전송. `scripts/slack_notify.py` 사용.

## 역할 분담 (절대)
- **메인(너)**: 파싱·매장수/최고가 산정·세금분류·가격계산(`price_calc.py`)·GO 게이트·product_info 조립·저장·Slack.
- **market-researcher**: §0-A 국내 시세(브랜드품). **listing-writer**: 상품명·모델명·태그·카테고리·detail.html.
- 가격·진실성(§9)은 메인 소유. 추출 안 된 필드는 비움. products.json 에 이미 데이터가 있으므로 URL 재크롤(product-extractor)은 보통 생략.

## 주의
- 서브에이전트는 사용자에게 못 묻는다 — 세금/배송/단위/GO 는 메인이 처리.
- 진행 상황은 TaskCreate/Update 로 단계 기록.
- 새 가격·태그 룰을 학습하면 `docs/LEARNED_RULES.md` + `memory/` 둘 다 갱신.
