---
name: feedback_competitor_landed_price_compare
description: 경쟁사 가격은 lprice(상품가)가 아니라 도착가(상품가+배송비)로 비교 — 주간 competitor-price-monitor 루틴
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c4a53c03-c133-4174-bcd2-ce2e8dcec220
  modified: 2026-07-23T10:56:33.023Z
---

경쟁 셀러 가격을 우리 판매가와 비교할 때는 **항상 도착가 = 상품가 + 배송비** 기준으로 본다. 네이버쇼핑 `search_shop` 의 `lprice` 는 **배송비가 빠진 상품가**라, 그대로 비교하면 언더컷 오판이 난다.

**Why:** 2026-07-23 자비다 K컵 등록 중, 캐나다점빵의 자비다 네스프레소 60캡슐 `lprice ₩60,000` 을 보고 "우리 ₩71,000 이 ₩11,000 언더컷당함 — 대응 필요"로 보고했다. 사용자 정정: **"6만+9900임 점빵이꺼"** → 배송비 포함 도착가 ₩69,900 으로 사실상 동률이었다. 불필요한 가격 인하를 권고할 뻔했다.

**How to apply:**
- 우리 쪽도 같은 선상으로 — 무배면 판매가 그대로, 유료배송이면 배송비를 더해 도착가로.
- 규격이 다르면(30개입 vs 96개입) 도착가 직접비교 대신 **개당 단가**. 단 **개당 단가 열세 ≠ 경쟁력 없음** — 소용량은 진입가가 낮은 게 강점이라 개당이 비싼 건 정상. 이걸로 "안 됨" 판정하지 말 것.
- 상대 배송비가 ₩30,000 이상으로 과하면 검색노출 꼼수 의심 (네이버쇼핑은 상품가로 정렬 — [[feedback_demand_and_shipping_tactic]]).
- **대응 플래그는 경쟁사 도착가가 우리보다 5% 이상 낮을 때만.** 배송비를 못 구하면 "배송비 미확인"으로 두고 언더컷 단정 금지.

**주간 루틴:** 스케줄 작업 `competitor-price-monitor` (매주 월 10:30 → Slack `#new-item` + `output/competitor_watch_log.md`). 워치리스트는 `guide/competitor_watch.json`. **SKU 추가 시 새 스케줄 작업 만들지 말고** 워치리스트에만 — `python3 scripts/competitor_watch.py --add <상품번호> [--query "검색어"]`. 코스트코 재고체크([[feedback_costco_stock_check]])·룰루 파이널세일([[feedback_lululemon_relist_playbook]])과 같은 통합 루틴 패턴.
