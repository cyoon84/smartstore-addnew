---
name: feedback_hangtag_parking_check
description: "hangTag(주차 앱) 영수증도 매번 이메일 체크 때 같이 확인 — 북키퍼 차(주차) 탭"
metadata:
  type: feedback
---

주문 발주발송 파일 처리하면서 이메일 확인할 때, **hangTag 주차 영수증**(`support@hangtag.io`, 제목 "hangTag Parking Receipt")도 항상 같이 챙긴다.

**Why:** `receipt-plus-address-poller`(3시간 간격)가 chulhee.y@gmail.com 직접수신 메일도 훑어 대부분 자동으로 북키퍼 `차 (주차)` 탭에 넣어주지만(2026-08-05 hangTag $10.00 건도 폴러가 이미 캐치해 반영돼 있었음), **폴러가 전부 잡는다는 보장은 없다**(같은 날 Walmart.ca 직접주문 영수증은 폴러가 놓쳐 수동으로 찾아 넣어야 했음). 그러니 "오늘 주문 처리" 세션에서 이메일을 볼 때 hangTag도 검색해서 이미 장부에 있는지 확인하고, 없으면 직접 추가한다.

**확인 방법:**
```
search_threads query: "hangtag OR \"Hang Tag\" newer_than:2d"
```
찾으면 `add_expense.py -c "차 (주차)" ...` 로 넣기 전에 먼저 장부에 같은 날짜+total 이 이미 있는지 확인(스크립트가 중복이면 자동 스킵하고 `--force` 없이는 안 들어감 — 이게 정상 동작).

**추출할 필드:** Purchase Number · Lot(주차장 위치) · Start/End 시간 · Vehicle(BRXT814-ON) · Card 끝자리 · Total Amount(Taxes/Fees 포함) — subtotal = Total − Taxes.

관련: [[project_bookkeeper_expense_tracker]]
