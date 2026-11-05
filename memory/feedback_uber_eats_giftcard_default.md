---
name: feedback-uber-eats-giftcard-default
description: Uber Eats 결제는 기본이 Uber Cash(기프트카드) — COGS 에 factor 0.7999 를 기본 적용한다
metadata:
  type: feedback
---

**Uber Eats 영수증의 COGS 는 액면이 아니라 `액면 × 0.7999`(기프트카드 실현금)로 잡는다.**
사장님이 "기프트카드 썼다"고 안 적어도 **기본값이 기프트카드**다.

**Why:** 2026-09-16 이후 Uber Cash 는 코스트코에서 액면 $200 을 $159.98 에 산 기프트카드로
채워져 있다(factor 0.7999, `output/inventory/기프트카드_잔액.md`). 액면으로 잡으면 COGS 가
**20% 과대계상**되고 그 배치 순이익이 그만큼 적게 보고된다.

🔑 **영수증에 카드 청구가 찍혀 있어도 기프트카드일 수 있다.** 2026-11-04 코스트코 Etobicoke 건은
Mastercard ****3189 로 $103.62 + $5.00 이 찍혔다가 **같은 날 밤 전액 환불되고 Uber Cash 로 재결제**됐다.
영수증 Payments 섹션을 끝까지 읽어 Refund 줄이 있는지 본다.

> 2026-11-05 실사고 — 11/4 코스트코 영수증에 사장님이 *"used uber gift card"* 를 적어줘서 factor 를
> 붙이다가, 같은 Uber Cash 결제인 **11/2 Food Basics $78.18 · 11/3 코스트코 비즈니스센터 $56.37**
> 두 건이 액면 그대로 잡혀 있는 걸 발견했다. 확인 요청 → 사장님 **"다 기프트 카드야"**.
> 11/3 배치 COGS 가 ₩604,730 → ₩578,857 로 ₩25,873 내려가고 순이익이 ₩271,566 → **₩297,443**,
> 마진율 23.7% → 26.0% 가 됐다. 순이익 1위도 박충서에서 이재중(+₩38,711)으로 뒤집혔다.
> 노션 요약표·recap 까지 이미 올라간 뒤라 소급 정정이 네 군데(장부·정산 md·cogs.json·노션)로 번졌다.

**How to apply:**
1. Uber Eats 영수증을 장부에 넣을 때 결제수단 칸에 `Uber Cash (기프트카드 factor 0.7999 → 실현금 $X)`
   형식으로 적는다. 카드명만 적고 끝내지 않는다.
2. COGS 는 품목별 도착원가(액면)를 먼저 구하고 **마지막에 ×0.7999** 한다. FX 는 §19-3-1 대로 구매일 기준.
3. `output/inventory/기프트카드_잔액.md` 의 Uber 사용내역에 그 건을 바로 추가한다.
4. 기프트카드가 **아닌** 경우(현금·카드 직결제)에만 예외로 액면을 쓰고, 그때는 사장님께 확인한 근거를 메모에 남긴다.

[[feedback_doordash_giftcard_balance]] · [[feedback_cogs_fx_purchase_date]] · [[project_bookkeeper_expense_tracker]]
