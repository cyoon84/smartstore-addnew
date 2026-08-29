---
name: feedback_receipt_sender_allowlist
description: 영수증 폴러는 +receipt 수신 외에 가맹점 원본 발신자 allowlist 로도 수집 — 포워딩 깜빡해도 잡힘. 마케팅 공유주소는 넣지 말 것
metadata:
  type: feedback
---

`fetch_gmail_receipts.py` 는 원래 **`+receipt` 주소로 들어온 것만** 수집했다. 사장님이 포워딩을 깜빡하거나
**다른 주소로만 포워딩하면 그 영수증은 통째로 새어나간다.** → **가맹점 원본 발신자 allowlist** 를 추가해 메운다.

**구현:** `SENDER_ALLOWLIST` + `build_query()` (OAuth·IMAP 양쪽 쿼리 공용)
```
(deliveredto:ADDR OR to:ADDR OR from:<가맹점1> OR from:<가맹점2> …)
```

| 발신자 | 대상 |
|---|---|
| `receipts@e.lululemon.com` | lululemon 매장 e-receipt |
| `no-reply@sameday.costco.ca` | Costco Same-Day (Instacart) |
| `noreply@walmart.ca` | Walmart.ca 주문/배송 |
| `identification@nespresso.com` | Nespresso 주문확인 |
| `support@hangtag.io` | hangTag 주차 |

**Why:** 2026-08-29 — **8/26 lululemon Bloor St.(#220) Order #505 영수증($85.88, Back to Life Sport Bottle
18oz Straw Lid PIAR 핑크펄 ×2)** 이 `finchmart_to@qbodocs.com` 으로만 포워딩돼 폴러가 못 잡았고 장부에도 없었다.
내가 한국발송 리스트에서 그 물병을 "구매내역 미확인"으로 남겨뒀는데 사장님이 *"lululemon receipt 8/26에 두개
보낸거 확인안했냐"* 로 직접 짚어줘서야 발견. 같은 창(8/26~8/28) 재실행 시 16건 중 **5건을 새로 수집**.
같은 날 **5/25 Costco Same-Day(#20187069957417396, backdated 사입) 영수증도 장부에 없던 것**이 드러나
소급 기입했고(장부 141행), allowlist 덕에 그 원본 HTML 도 자동 확보됐다.

**How to apply:**
- 새 가맹점을 추가할 땐 **그 주소가 거래 영수증만 보내는지 먼저 확인**한다.
- 🚨 마케팅과 발신주소를 공유하는 곳(`CostcoNews@digital.costco.ca`·`offers@em.walmart.ca` 등)은
  **넣으면 인박스 전체가 딸려온다** — 절대 금지.
- 중복은 `add_expense.py` 가 자동 스킵하므로 allowlist 확대에 따른 이중기입 위험은 없다.
- 과거 누락분이 의심되면 `--since/--until` 로 그 구간을 재실행하면 소급 수집된다.

LEARNED_RULES §20-20 · [[project_receipt_20min_check_loop]] · [[feedback_receipt_poller_tab_and_pending_match]] · [[project_bookkeeper_expense_tracker]]
