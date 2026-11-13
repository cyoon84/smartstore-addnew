---
name: feedback_inventory_current_stock_formula
description: 재고 판정은 현재고 칸이 아니라 사입수량−판매수량으로 — 수식이라 pandas 가 0 으로 읽고, 숫자면 하드코딩 착각치다
metadata:
  type: feedback
---

재고관리 엑셀(`output/inventory/재고관리_*.xlsx`)에서 **재고 유무를 `현재고` 칸으로 판정하지 않는다.
`사입수량 − 판매수량` 을 직접 계산한다.**

`현재고` 는 수식 `=J{행}-K{행}` 이다. pandas·openpyxl 로 읽으면 값이 아니라 수식 문자열이 나오고,
`pd.to_numeric(..., errors='coerce')` 에서 NaN 이 된다. 거기에 `fillna(0)` 을 붙이면
**재고가 있는 로트가 전부 "0" 으로 보인다.**

```python
# ❌
df['cur'] = pd.to_numeric(df['현재고'], errors='coerce').fillna(0)

# ✅
buy  = pd.to_numeric(df['사입수량'], errors='coerce').fillna(0)
sold = pd.to_numeric(df['판매수량'], errors='coerce').fillna(0)
df['cur'] = buy - sold
```

**반대 함정도 있다.** `현재고` 에 수식이 아니라 **숫자가 그대로 들어 있으면 과거 실사 때 사람이
하드코딩한 값**이라 실제 잔여와 어긋날 수 있다. 그래서 숫자든 수식이든 `사입−판매` 로 다시 세고,
**로트 메모의 출고 이력과 대조**한다. 어긋나면 메모가 정본이고 `현재고` 칸은 수식으로 복원한다.

**Why:** 2026-11-12 에 11/13 배치를 재조사하다 발견했다. 전날 **오스테오 조인트 이지·수도크림·
도브 센서티브 뷰티바 3건을 "재고 0, 구매 필요"로 보고**했는데 셋 다 재고가 있었다
(84행 1 · 55행 1 · 127행 1, 합 **₩86,850**). 원인이 정확히 위 `fillna(0)` 이었다 —
멀쩡한 재고를 두고 같은 걸 또 살 뻔했다.

같은 조사에서 반대 방향 오류도 나왔다. **7행 다우니 향기부스터 에이프릴프레쉬 680g** 은
`현재고` 에 옛 실사값 `2` 가 하드코딩돼 있었지만 사입 4 · 판매 4 에 메모상 7/17·9/18·9/29·10/2
전량 소진이라 **실잔여 0** 이었다. 그 숫자를 믿었으면 없는 재고를 COGS(₩17,298)로 잡을 뻔했다.

**How to apply:** 주문을 받아 구매목록·Todoist·COGS 를 만들기 전(그리고 사장님께
"재고 있나요" 라고 묻기 전 — [[feedback_check_inventory_before_asking]]) 재고 엑셀을 열 때,
`현재고` 칸은 아예 무시하고 `사입수량 − 판매수량` 으로 센다. 0 이 아니면 로트 메모를 읽어
출고 이력과 맞는지 확인하고, 그 로트의 **사입단가(₩)** 를 COGS 로 쓴다. 재고 시트에 행이
아예 없으면 장부 `물건산거 (COGS)` 탭도 훑는다(§0-∞).

[[feedback_check_inventory_before_asking]] · [[project_inventory_list]] ·
[[project_oneoff_hanmi_nespresso_stock_20260904]] · [[project_order_settlement]]
