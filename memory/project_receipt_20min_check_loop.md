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
1. Gmail `search_threads` query **`(deliveredto:chulhee.y+receipt@gmail.com OR to:chulhee.y+receipt@gmail.com) newer_than:2d`** — 🔑 **반드시 `to:` 포함**. `deliveredto:` 단독은 **병행 포워딩**(사용자가 한 메일을 `finchmart_to@qbodocs.com` + `chulhee.y+receipt@gmail.com` 동시 전송) 을 놓친다(Delivered-To 가 qbodocs 라서). 2026-07-22 이걸로 Costco 큐리그 사입·Anthropic·Blinkay 3건 놓칠 뻔 → `to:` 로 다 잡음. (`fetch_gmail_receipts.py` 는 이미 `(deliveredto OR to)` 씀.)
2. 각 메일이 **장부(/Volumes/External/claude/profit-expense-tracker/장부.xlsx)에 이미 기입됐는지 대조** — 영수증파일 경로(`receipts/<월>/..._<msgId>.*`) 또는 merchant+날짜+total 로. **신규만** 처리 (이중기입 금지).
3. 신규면: `scripts/fetch_gmail_receipts.py` 로 원본 무손실 저장(OAuth 우선, 디스크 직접기록) + `scripts/add_expense.py -c <카테고리>` 로 장부 기입. **플러스-주소로 직접 보낸 건 = 무조건 사업**(§24 판별 스킵), 사업/개인 애매하면 기입 전 사용자 확인.
4. 처리 내역 보고 후 다시 20분 ScheduleWakeup. 신규 없으면 조용히 재스케줄만.

**주의:**
- 이 루프는 **세션 생존 중에만** 돈다. 세션 닫아도 계속 돌리려면 `gmail-receipt-collector` 스케줄 작업(현재 매일 23:00)을 20분 cron으로 바꾸는 옵션 — 아직은 세션 루프로 운영. 사용자가 영구 백그라운드 원하면 전환.
- 네스프레소/COGS 영수증은 §24 처리 체인(장부→nespresso-order→Todoist→정산)까지 이어질 수 있음 — 루프는 1단계(장부 기입)까지, 나머지는 사용자 확인 후.

**🔑 출고일 오후 = 저빈도 예외 (2026-07-21 사용자 수정):** **화요일 14:00~24:00**, **금요일 14:00~24:00** 구간에는 **1시간에 한 번만** 체크(delaySeconds 3600). 그 외 모든 시간(화/금 00:00~14:00 포함, 수/목/토/일 전체)은 기존대로 **20분 간격**(delaySeconds 1200). 매 firing 시 `date` 로 실제 요일·시각 확인 후 이 창에 해당하면 3600, 아니면 1200으로 재스케줄.
- **판별:** bash `date "+%A %H"` (또는 동일) 로 요일·시(0~23) 확인. 요일이 Tuesday 또는 Friday 이고 시가 14~23 이면 hourly, 그 외는 20분.
- **이유(사용자 명시, 2026-07-21):** 화/금은 **출고 나가는 날**(§20 출고일) — 그날 오후엔 한미/우체국 발송 처리·정산 작업이 몰려 있어 영수증 체크를 20분마다 자주 돌릴 필요가 없다.

> 첫 firing(2026-07-21) — DoorDash Walmart 영수증(msg 19f8440d612bceca) 1건 발견했으나 **오늘 아침 세션에서 이미 처리 완료**(COGS 탭 기입 + `receipts/2026-07/..._19f8440d612bceca.html` 저장) → 신규 없음, 재스케줄만. [[project_bookkeeper_expense_tracker]]
> 2026-07-21 20:23(화) 사용자가 화/금 오후 저빈도(1시간) 규칙 추가 지시 → 이후 firing부터 적용.
