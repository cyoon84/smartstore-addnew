---
name: project_receipt_20min_check_loop
description: 세션 중 20분마다 chulhee.y+receipt@gmail.com 신규 영수증을 찾아 북키퍼 장부에 기입하는 폴링 루프 (ScheduleWakeup)
metadata: 
  node_type: memory
  type: project
  originSessionId: 659f3a28-dbe2-43f9-8de4-e5e120d7415f
---

사용자 지시(2026-07-21): **"20분마다 체크하는걸로"** — `chulhee.y+receipt@gmail.com` (플러스-주소 인박스, §24 [[project_bookkeeper_expense_tracker]])로 폰에서 포워딩/공유한 영수증 이메일을 **20분 간격으로 찾아 북키퍼 장부에 기입**한다.

**구현 = ScheduleWakeup 자기-페이싱 루프 (delaySeconds 1200).** 세션이 살아있는 동안 20분마다 재-invoke. 매 firing 절차:
1. Gmail `search_threads` query `deliveredto:chulhee.y+receipt@gmail.com newer_than:2d`
2. 각 메일이 **장부(/Volumes/External/claude/profit-expense-tracker/장부.xlsx)에 이미 기입됐는지 대조** — 영수증파일 경로(`receipts/<월>/..._<msgId>.*`) 또는 merchant+날짜+total 로. **신규만** 처리 (이중기입 금지).
3. 신규면: `scripts/fetch_gmail_receipts.py` 로 원본 무손실 저장(OAuth 우선, 디스크 직접기록) + `scripts/add_expense.py -c <카테고리>` 로 장부 기입. **플러스-주소로 직접 보낸 건 = 무조건 사업**(§24 판별 스킵), 사업/개인 애매하면 기입 전 사용자 확인.
4. 처리 내역 보고 후 다시 20분 ScheduleWakeup. 신규 없으면 조용히 재스케줄만.

**주의:**
- 이 루프는 **세션 생존 중에만** 돈다. 세션 닫아도 계속 돌리려면 `gmail-receipt-collector` 스케줄 작업(현재 매일 23:00)을 20분 cron으로 바꾸는 옵션 — 아직은 세션 루프로 운영. 사용자가 영구 백그라운드 원하면 전환.
- 네스프레소/COGS 영수증은 §24 처리 체인(장부→nespresso-order→Todoist→정산)까지 이어질 수 있음 — 루프는 1단계(장부 기입)까지, 나머지는 사용자 확인 후.

> 첫 firing(2026-07-21) — DoorDash Walmart 영수증(msg 19f8440d612bceca) 1건 발견했으나 **오늘 아침 세션에서 이미 처리 완료**(COGS 탭 기입 + `receipts/2026-07/..._19f8440d612bceca.html` 저장) → 신규 없음, 재스케줄만. [[project_bookkeeper_expense_tracker]]
