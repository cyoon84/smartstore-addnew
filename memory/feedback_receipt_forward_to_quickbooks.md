---
name: feedback_receipt_forward_to_quickbooks
description: 영수증 처리에 "Aside로 QuickBooks(finchmart_to@qbodocs.com) 포워딩" 단계 추가 — 장부 기입과 세트
metadata:
  type: feedback
---

영수증을 처리할 때 **장부 기입과 QuickBooks 포워딩을 한 묶음으로** 한다.
포워딩은 **Aside 에 시킨다** — `aside exec --permission full-access` 로 사장님 Gmail 에서
그 영수증 메일을 **`finchmart_to@qbodocs.com`** 로 전달.

**Why:** 사장님 지시(2026-11-25, RCSS 건): *"영수증 도착하면 장부에 넣고 aside한테 quickbook으로
forwarding시켜."* QuickBooks Receipts 탭은 이메일 인입만 받는데, Gmail MCP 는 **드래프트까지만** 되고
발송이 안 돼 그동안 이 경로가 막혀 있었다([[project_qbo_receipt_upload]] 에서 Drive 업로드로 우회했다가
화질 문제로 폐기). **Aside 는 사장님 로그인 브라우저를 쓰므로 그냥 전달 버튼을 누르면 된다** —
막혀 있던 경로가 열린 것.

**How to apply — 영수증 1건 처리 순서:**
1. 정산 COGS 반영 (`order_settlement.py --add-cogs`)
2. 원본을 `output/receipts/<출고일>/` 에 복사
3. Todoist `사야할 제품들` cross off ([[feedback_todoist_crossoff_not_annotate]])
4. 북키퍼 장부 기입 (`add_expense.py`)
5. **🆕 Aside 로 QuickBooks 포워딩** — 그 메일을 `finchmart_to@qbodocs.com` 로 전달.
   프롬프트에 **메일 제목·발신자·날짜**를 적어 어느 메일인지 특정하고, **전달만** 하고
   답장·삭제·라벨 변경은 금지한다. 전달 완료를 보고받아 확인한다.

**🚨 PC Express(RCSS·No Frills·Loblaws)는 "주문 확인메일" 로 이 절차를 시작하지 않는다.**
확인메일은 `Estimated total` 이라 품목·금액이 바뀔 수 있다 — **실영수증이 온 뒤에** 1~5 를 돌린다
(§20-17, 2026-11-22 링클릴리저 90ml 누락 건).

관련: §20-1 · §20-3 (docs/LEARNED_RULES.md) · [[project_bookkeeper_expense_tracker]]
