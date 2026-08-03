---
name: feedback_receipt_poller_tab_and_pending_match
description: "폴러 자동수집 영수증은 탭 분류 오류 + pending 재주문 매칭 누락 둘 다 검산해야 함 — merchant명만 보고 무관 처리 금지"
metadata:
  type: feedback
---

`receipt-plus-address-poller`/`fetch_gmail_receipts.py` 가 영수증을 북키퍼 장부에 자동 기입해도, 그 자동 분류를 그대로 믿으면 안 된다. 매번 영수증 COGS를 반영할 때 두 가지를 검산한다:

1. **탭 분류가 맞는지.** 사입(COGS) 영수증인데 `물건산거 (COGS)` 대신 `식비` 같은 무관 탭에 들어갈 수 있다. merchant명(약국·편의점 등)만 보고 폴러가 오판할 수 있으므로, 장부에 새로 들어온 항목이 예상 탭에 있는지 확인. 잘못돼 있으면 그 탭에서 삭제하고 올바른 탭으로 행 자체를 옮긴다(메모만 고치는 게 아님).
2. **그 배치의 "품절/재주문 필요" pending 목록과 항상 대조.** 새 영수증의 merchant가 낯설어도(예: 평소 안 가는 약국) "무관"으로 단정하지 말고, 날짜·수량·품목 라인이 미완료 항목과 맞는지 본다. 맞으면 재주문일 확률이 높다.

**Why:** 2026-08-02 8/4 배치 — 전재은 주문 중 No Frills 배송에서 Twigz Buttery Herb & Garlic×2가 품절돼 "재주문 필요"로 남아 있었다. 같은 날 Rexall에서 TWIGZ PRETZEL×2($6.78)를 산 영수증이 폴러로 들어왔는데, `식비` 탭에 잘못 들어갔고 memo도 "채널A 자동수집"이라고만 적혀 있어 그냥 무관한 간식 구매로 넘겼다. 사용자가 "check receipt from rexall again idiot"이라고 직접 지적할 때까지 발견 못 함 — 실제로는 정확히 그 재주문(같은 날, 같은 수량 2, 같은 제품 라인)이었다.

**How to apply:** 영수증 COGS 반영 흐름(§20-3, §20-12) 매 단계에서 이 두 검산을 습관화한다. 특히 배치 안에 미완료(품절/재주문) 플래그가 있는 상태에서 새 영수증이 들어오면, 그 목록부터 먼저 열어 대조한 뒤 "무관"으로 분류할지 판단한다.

관련: [[project_batch_20260804_wip]] · [[feedback_receipt_auto_reconcile]] · [[project_receipt_20min_check_loop]]
