---
name: feedback-receipt-auto-reconcile
description: "영수증은 poller가 이미 장부에 자동 기입 — \"넣었어\" 말 대신 pending_receipts.py 훅으로 자동 인식"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 52ed35d6-89f5-45ce-8e36-a4c535203b9c
  modified: 2026-07-23T11:07:59.508Z
---

영수증은 스케줄 작업 `receipt-plus-address-poller`(20분마다)가 이미 **북키퍼 장부에 자동 기입**한다. 사용자가 매번 "영수증 넣었어"라고 말해줄 필요 없이, **장부 ↔ 정산 대사**로 미반영분을 스스로 찾아낸다.

**Why:** 2026-07-23 사용자 — "영수증 루틴 한거 어떻게 자동으로 인식하는 방법 없어? 매번 넣었어! 이렇게 안해도". 실제로 그 시점 장부엔 7/23 Amazon 다우니 No.37 영수증이 이미 들어와 있었는데 정산엔 반영이 안 돼 있었다.

**How to apply:**
- `python3 scripts/pending_receipts.py` (smartstore-addnew) — 장부 `물건산거 (COGS)` 탭 ↔ `output/settlement/_receipts_reflected.json` 대사 → 미반영 목록 + 출고일 후보.
- `.claude/settings.json` 의 **SessionStart · UserPromptSubmit 훅**이 `--quiet` 로 자동 실행 — 미반영 있을 때만 컨텍스트에 뜬다(없으면 무출력).
- 정산 반영 후 **반드시** `--mark "<날짜|merchant|total>" --batch <출고일>` (재고전환은 `--batch 재고`, 대상아님은 `제외`).
- `order_settlement.py` 는 md 의 `<!-- 수기 섹션 (재실행해도 보존) -->` 아래를 덮어쓰지 않는다.

**🔑 2026-07-24 — "정산 반영도 자동화" 시도했다가 즉시 롤백.** `settlement-auto-reconcile` 무인 스케줄 작업(30분 cron)을 만들어 확실한 매칭만 자동 반영하도록 했으나, 사용자가 **"뭔가 routine이랑 이거랑 제대로 연결이 안되면 routine을 할 이유가 없는데"** 라고 지적 → 즉시 삭제. 확정된 방식:
- **이메일 수집·장부 자동기입은 그대로 유지**("이메일은 원래 하던대로 하고") — `receipt-plus-address-poller` 변경 없음.
- **정산 반영은 "정산해!" 라이브 트리거로만.** 사용자가 "정산해!"라고 부르면 그 세션에서 `pending_receipts.py` 확인 + 최신 발주발송 export 대조([[feedback_settlement_latest_export_only]] 안전규칙 적용)해서 반영. 무인 크론이 배경에서 판단하며 도는 구조는 폐기 — 고객명 매칭·배치 선정·FX 확정 같은 판단을 헤드리스로 신뢰하기 어렵다는 게 이유.

LEARNED_RULES §20-12·§20-15. 관련: [[project_receipt_20min_check_loop]] · [[project_bookkeeper_expense_tracker]] · [[project_order_settlement]] · [[feedback_settlement_latest_export_only]]
