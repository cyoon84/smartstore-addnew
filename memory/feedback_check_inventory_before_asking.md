---
name: feedback_check_inventory_before_asking
description: 🚨"재고 있나요/사야하나요" 묻기 전에 재고관리 엑셀부터 열어본다. 있으면 사입단가로 COGS + 판매수량 차감
metadata:
  type: feedback
---

**구매목록·Todoist "사야할 제품들"을 만들기 전, 그리고 사장님께 "이거 재고 있나요? 새로 사야 하나요?"
라고 묻기 전에 — `output/inventory/재고관리_*.xlsx` 를 먼저 연다.**

확인 없이 묻는 건 규칙을 지킨 게 아니라 판단을 떠넘긴 것이다.

**절차**
1. 재고관리 엑셀 최신본에서 **상품명 부분일치** 검색 (`~$` 로 시작하는 임시파일 제외).
2. 있으면 → **`사입단가(₩)` 로 COGS** 잡고, 시트 **`판매수량` +N** 차감,
   `메모` 에 `<날짜> <수취인> 주문(주문번호 …) 출고 — 재고 N 차감(현재고 M)` 기록.
3. 부분 재고면 `주문수량 − 재고 = 구매수량` 만 구매목록에.
4. 없을 때만 구매 대상.
5. ⚠️ 이름이 비슷해도 **향·맛·용량·옵션이 다르면 다른 SKU** — 차감 금지 ([[feedback_product_name_verbatim]]).

**Why:** 2026-08-31 최은숙 `캐나다 코스트코 대용량 세라비 모이스처라이징 크림 로션 453ml, 2개` —
재고 시트 23행에 **2026-07-29 Costco Downsview 사입분**(장은경 주문취소 → 재고전환, Costco Shop Card $25
적용해 실지출 $12.28, **사입단가 ₩13,299**)이 그대로 있었는데 확인 없이 *"구매 내역이 안 잡힙니다.
재고에 있나요, 새로 사야 하나요?"* 로 물었다. 사장님: *"사입 목록에 있잖아"* → ***"항상 물어본다"***.

**근본원인:** 이 규칙이 `docs/LEARNED_RULES.md` §0-∞ 본문에만 있고 `memory/` 독립 파일이 없어
**MEMORY.md 인덱스에 안 실렸다.** 세션 시작 시 자동 로드되는 건 네스프레소 전용
[[feedback_nespresso_stock_vs_purchase_check]] 뿐이라, 네스프레소는 챙기면서 일반 품목은 놓쳤다.
→ [[feedback_todoist_due_date_parent_only]] 와 **동일한 실패 구조**: LEARNED_RULES 에만 적고
memory 를 안 만들면 그 규칙은 다음 세션에서 사실상 안 보인다.

LEARNED_RULES §0-∞ · [[project_inventory_list]] · [[feedback_costco_price_adjustment]]
