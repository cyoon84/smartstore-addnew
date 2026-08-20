---
name: feedback_nespresso_restock_ledger_flag_check
description: 네스프레소 Stock 재고 판단 전에 북키퍼 장부에 "⚠️ Restock탭 미반영" 플래그 걸린 항목부터 확인 — 안 그러면 재고부족을 지어내게 됨
metadata:
  type: feedback
---

네스프레소 캡슐 재고 부족 여부를 Stock 탭 숫자만 보고 판단하면 안 된다. `gmail-receipt-collector`/영수증 폴러는 **장부 기입까지만** 하고 Nespresso Vertuo Order 구글시트 Restock 탭 반영은 "사용자 확인 후"로 미뤄두는 케이스가 있다(§23 job 설계 — 장부와 정산 COGS는 자동, 재고관리 시트는 수동). 이 상태에서 Stock 탭만 보고 "재고부족"이라고 판단하면 실제로는 이미 사입해둔 대량 재고가 시트에 반영이 안 됐을 뿐인데 허위로 "사야할 제품들"에 재구매를 넣게 된다.

**2026-08-20 사례:** 이은정 주문 처리 중 Stock 탭에서 메이플 피칸 토론토 재고 -2를 보고 "재고부족, 2개 더 사야함"으로 Todoist에 추가했는데, 실제로는 2026-08-16 Nespresso Boutique Markville에서 $548.50(6종·35슬리브, 메이플피칸 80캡슐=8슬리브 포함) 대량 사입이 이미 있었고 장부에도 기록돼 있었지만 Restock 탭 반영이 누락된 상태였다. 사용자가 "8/16에 대량으로 산거 왜 구글시트에 업데이트 안하고 가짜정보를 주냐"고 지적. Restock 탭에 6종 중 누락된 5종(Coconut Vanilla만 이미 반영돼 있었음)을 추가하니 메이플피칸 재고가 -2→+6으로 정상화됨.

**Why:** 재고 판단의 진실은 Stock 탭이 아니라 "장부(COGS) 기입분이 전부 Restock에 반영됐는가"다. 장부에 있는데 시트에 없으면 그 차이만큼 Stock 숫자가 틀리다.

**How to apply:** 네스프레소 재고 부족/충분 판단(§23, nespresso-order 스킬 7번 절차) 전에, **북키퍼 장부에서 최근 Nespresso 관련 COGS 행을 훑어 "⚠️"·"Restock탭 반영" 문구가 남아있는 미반영 항목이 없는지 먼저 확인**한다(`grep -i "nespresso\|네스프레소" 장부.xlsx` 또는 openpyxl로 물건산거 탭 스캔). 미반영 항목이 있으면 그것부터 Restock 탭에 채운 뒤에 Stock 탭 잔여재고를 판단한다. 반영 완료 후 장부의 플래그 문구도 지워서 다음 확인 때 다시 헷갈리지 않게 한다.
