---
name: project_receipt_20min_check_loop
description: chulhee.y+receipt@gmail.com + chulhee.y@gmail.com 직접수신 두 채널을 20분마다(화/금 오후는 1시간마다) 폴링해 북키퍼 장부에 기입 — 영구 스케줄 작업(scheduled-tasks), gmail-receipt-collector는 삭제됨
metadata: 
  node_type: memory
  type: project
  originSessionId: 659f3a28-dbe2-43f9-8de4-e5e120d7415f
---

사용자 지시(2026-07-21): **"20분마다 체크하는걸로"** — `chulhee.y+receipt@gmail.com` (플러스-주소 인박스, §24 [[project_bookkeeper_expense_tracker]])로 폰에서 포워딩/공유한 영수증 이메일을 **20분 간격으로 찾아 북키퍼 장부에 기입**한다.

**🔑 구현 = scheduled-tasks 영구 작업 (2026-07-22 전환, ScheduleWakeup 세션 루프 폐기).** 처음엔 ScheduleWakeup 자기-페이싱 세션 루프(delaySeconds 1200)로 구현했으나, **세션이 닫히면 예약된 wakeup이 그냥 조용히 스킵되고 다시 살아나지 않는** 구조적 한계로 2026-07-21 20:23 이후 다음날 낮까지 ~19시간 공백이 생김(그 사이 영수증 3건은 다른 경로로 처리됨). 사용자에게 "왜 안했어?" 지적받고 **scheduled-tasks(`mcp__scheduled-tasks__create_scheduled_task`)로 전환**해 세션/앱 상태와 무관하게 계속 돌도록 확정.

- **taskId:** `receipt-plus-address-poller` (`~/.claude/scheduled-tasks/receipt-plus-address-poller/SKILL.md`)
- **cron:** `*/20 * * * *`(20분마다 발동). 화/금 14:00~24:00 저빈도 규칙은 cron 자체를 나누지 않고 **프롬프트 안에서 자체 판별**한다 — 저빈도 구간이고 분(MM)≥20 이면 그 발동은 즉시 조용히 종료(사실상 매시 정각 발동분만 실행 = 1시간에 한 번).
- 기존 세션 루프의 절차(Gmail 검색 → 장부 대조 → 신규만 fetch_gmail_receipts.py 저장 + add_expense.py 기입 → 신규 있을 때만 Slack DM 보고)를 그대로 SKILL.md 프롬프트에 옮김. `gmail-receipt-collector`(매일 23:00, 인박스 전체 훑어 라벨링·보고만·기입 안 함)와는 별개 작업으로 공존 — 이쪽(`receipt-plus-address-poller`)만 플러스-주소 채널 한정 자동 기입을 한다.
- **레거시 절차(참고용, SKILL.md 본문과 동일 로직):**
1. Gmail `search_threads` query **`(deliveredto:chulhee.y+receipt@gmail.com OR to:chulhee.y+receipt@gmail.com) newer_than:2d`** — 🔑 **반드시 `to:` 포함**. `deliveredto:` 단독은 **병행 포워딩**(사용자가 한 메일을 `finchmart_to@qbodocs.com` + `chulhee.y+receipt@gmail.com` 동시 전송) 을 놓친다(Delivered-To 가 qbodocs 라서). 2026-07-22 이걸로 Costco 큐리그 사입·Anthropic·Blinkay 3건 놓칠 뻔 → `to:` 로 다 잡음. (`fetch_gmail_receipts.py` 는 이미 `(deliveredto OR to)` 씀.)
2. 각 메일이 **장부(/Volumes/External/claude/profit-expense-tracker/장부.xlsx)에 이미 기입됐는지 대조** — 영수증파일 경로(`receipts/<월>/..._<msgId>.*`) 또는 merchant+날짜+total 로. **신규만** 처리 (이중기입 금지).
3. 신규면: `scripts/fetch_gmail_receipts.py` 로 원본 무손실 저장(OAuth 우선, 디스크 직접기록) + `scripts/add_expense.py -c <카테고리>` 로 장부 기입. **플러스-주소로 직접 보낸 건 = 무조건 사업**(§24 판별 스킵), 사업/개인 애매하면 기입 전 사용자 확인.
4. 처리 내역 보고 후 다시 20분 ScheduleWakeup. 신규 없으면 조용히 재스케줄만.

**주의:**
- 네스프레소/COGS 영수증은 §24 처리 체인(장부→nespresso-order→Todoist→정산)까지 이어질 수 있음 — 이 폴링 작업은 1단계(장부 기입)까지만 하고, COGS/네스프레소 건은 Slack 보고에 "Todoist/정산 확인 필요" 로 플래그만 남긴다. 나머지는 사용자가 확인 세션에서 이어감.
- **scheduled-tasks 는 "앱이 열려 있을 때" 실행**된다(세션 창과는 무관, 앱 자체가 떠 있으면 됨). 앱이 닫혀 있으면 그 발동은 다음 앱 실행 시 밀려서 돈다 — 완전한 백그라운드 서버는 아니지만 개별 대화 세션보다 훨씬 안정적.

**🔑 출고일 오후 = 저빈도 예외 (2026-07-21 사용자 지시, 2026-07-22 scheduled-tasks 프롬프트에 반영):** **화요일 14:00~24:00**, **금요일 14:00~24:00** 구간에는 **1시간에 한 번만** 체크. 그 외 모든 시간(화/금 00:00~14:00 포함, 수/목/토/일 전체)은 **20분 간격**. cron 자체는 항상 20분(`*/20 * * * *`)이고, 저빈도 구간에서 분(MM)≥20인 발동은 SKILL.md 프롬프트 0단계에서 즉시 조용히 종료해 사실상 1시간에 한 번으로 만든다.
- **이유(사용자 명시, 2026-07-21):** 화/금은 **출고 나가는 날**(§20 출고일) — 그날 오후엔 한미/우체국 발송 처리·정산 작업이 몰려 있어 영수증 체크를 20분마다 자주 돌릴 필요가 없다.

> 첫 firing(2026-07-21, ScheduleWakeup 세션 루프 시절) — DoorDash Walmart 영수증(msg 19f8440d612bceca) 1건 발견했으나 오늘 아침 세션에서 이미 처리 완료 → 신규 없음, 재스케줄만.
> 2026-07-21 22:27 — 세션 루프로 Uber Eats(Costco Business Centre, Titan Packing Tape) $46.71 Supply 건 1건 신규 처리.
> 2026-07-21 20:23(화)부터 화/금 오후 저빈도(1시간) 규칙 적용 시작.
> 2026-07-22 — 세션 루프가 01:11 예약 이후 재기동 없이 ~19시간 공백(세션이 닫히면서 wakeup이 조용히 스킵됨). 그 사이 Costco 큐리그 사입·Anthropic 구독·Blinkay 주차 3건은 다른 경로로 이미 장부에 반영돼 있었음(사용자 "왜 안했어?" 지적) → **scheduled-tasks(`receipt-plus-address-poller`)로 전환**, 이 세션의 ScheduleWakeup 루프는 종료. [[project_bookkeeper_expense_tracker]]

## 🔑 2026-08-01 — 직접수신 채널(chulhee.y@gmail.com 본계정) 추가 + `gmail-receipt-collector` 삭제

사용자 지시: **"추가로 +recipt에 온거 말고 내 이메일(chulhee.y@gmail.com)로 다이렉트로 온 이메일에도 똑같은 액션 취해줘. 그럼 gmail receipt collector routine retire시킬게."** 위 §16의 "`gmail-receipt-collector`와는 별개 작업으로 공존" 문구는 이 시점에 **더 이상 유효하지 않음** — 그 작업은 이번에 삭제됐고, `receipt-plus-address-poller` 하나가 두 채널을 다 처리한다.

- **채널 A(플러스-주소)** — 기존 그대로 무조건 사업, 즉시 전체 체인.
- **채널 B(직접수신, 신규)** — 검색 `to:chulhee.y@gmail.com -to:chulhee.y+receipt@gmail.com (category:purchases OR receipt OR order OR invoice OR 영수증 OR 결제 OR payment) newer_than:2d`. 후보마다 `/Volumes/External/claude/profit-expense-tracker/CLAUDE.md` §5 "영수증 판별 사전"으로 **사업/개인/확인필요** 판정 — 사업만 전체 체인(원본저장+`add_expense.py` 기입), 확인필요는 원본만 저장(기입 보류), 개인은 완전 스킵. Amazon 이름 필터(CHULHEE만 사업)·Costco MasterCard 결제수단 오버라이드(품목과 무관 무조건 사업, [[feedback_costco_mastercard_always_business]])를 판정에 반영.
- **`fetch_gmail_receipts.py` 에 `--extra` 옵션 신규 추가** — `--addr` 하나만으론 채널 B(본계정 전체)가 인박스를 통째로 긁으므로, 판정 통과한 메시지의 Message-ID로 `--extra '-to:chulhee.y+receipt@gmail.com (rfc822msgid:<id> ...)'` 좁혀서 원본을 받는다.
- **`gmail-receipt-collector`(매일 23:00, 수집·라벨링·보고만) 는 `delete_scheduled_task` 로 삭제됨.** SKILL.md 파일은 복구용으로 디스크에 남음(`~/.claude/scheduled-tasks/gmail-receipt-collector/SKILL.md`). 그 작업의 Gmail 라벨 부착 기능(북키퍼/COGS 등)은 이번 이식에 포함 안 함.
- `/Volumes/External/claude/profit-expense-tracker/CLAUDE.md` §7("(예정) Gmail 영수증 자동 수집")도 "구현됨"으로 갱신.

[[project_bookkeeper_expense_tracker]]
