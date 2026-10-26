---
name: feedback_nespresso_invoice_store_credit
description: 네스프레소 invoice 의 ACOMPTE/DEPOSIT 이 Total 과 다르면 차액은 store credit — 장부 기입액은 원 주문의 기입 여부로 갈린다
metadata:
  type: feedback
---

네스프레소 invoice 하단 **`ACOMPTE/DEPOSIT`** 칸이 **`Total`** 과 다르면, 그 차액은 **store credit 적용분**이다.
불이행된 주문이 환불이 아니라 **store credit 으로 전환**되는 경우가 있고, 그 credit 이 다음 invoice 에 붙는다.
`ACOMPTE/DEPOSIT` = 실제 카드 결제액 · `Total − ACOMPTE` = 적용된 credit.

**Why:** 2026-10-26 invoice `211617383` 에서 Total $159.40 / ACOMPTE $101.02 / 차액 $58.38 이 안 맞아
"부분결제인지 확인 필요" 로만 플래그해뒀다. 사장님 한 줄로 바로 풀렸다 —
*"이전에 58.38$ 주문 (yorkdale store pickup - 209951120)이 이행되지 못해서 credit으로 들어간거야"*.
차액을 추측하거나 그냥 넘기면 결제수단·현금흐름이 틀리게 기록되고, 더 나쁘게는 **이중계상**이 난다.

**How to apply:**
1. **COGS 배분은 건드리지 않는다.** 품목 단가(캡슐당 × 수량)는 `Total` 기준으로 찍혀 있어 수취인별 원가는 그대로다.
   바뀌는 건 결제수단·현금흐름 표기뿐이다.
2. **장부 기입액은 그 credit 의 원 주문이 이미 장부에 있는지로 갈린다:**
   - **기입돼 있다** → 이번 invoice 는 **현금분(ACOMPTE)만** 잡는다. Total 로 넣으면 원 주문 행과 겹쳐 이중계상.
   - **미기입이다** → **Total 전액**이 맞다. 두 시점 현금 합이 그대로 Total 이다.
3. 원 주문 행을 찾으면 **그 행 메모도 같이 닫는다** — "취소 예정" 같은 미결 표현을
   "환불이 아니라 credit 전환, N행에 적용" 으로 바꿔야 다음 세션에서 같은 추적을 반복하지 않는다.
4. **차액의 출처는 추측하지 말고 사장님께 물어본다.** invoice 에는 원 주문번호가 안 찍힌다.

> 2026-10-26 실제 처리 — 그 9/30 주문은 장부 212행 메모에 "취소 예정 — 장부 미기입, 되돌릴 것 없음" 으로
> 남아 있었다(실제로는 취소가 아니라 credit 전환). **미기입이었으므로** 283행을 $159.40 전액으로 두고
> 결제수단만 `AMEX $101.02 + Nespresso store credit $58.38 (order 209951120 불이행분)` 으로 적었고,
> 212행 메모를 닫았다. COGS 는 이하나 ₩78,075 · 윤동환 ₩73,280 · 류승희 ₩29,336 그대로.

관련: [[project_nespresso_workflow_settlement]] · [[feedback_nespresso_rebate_single_coffee]] ·
[[project_bookkeeper_expense_tracker]] · [[feedback_ledger_excel_is_source_of_truth]]
(LEARNED_RULES §23)
