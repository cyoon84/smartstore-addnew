---
name: feedback-made-to-order
description: 일부 SKU는 재고 없이 주문 접수 후 현지 매입하는 made-to-order 방식 — 네이버 발송예정일을 길게 설정
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73ad613f-b8d4-47fa-a8d3-98e2d6de72aa
---

사용자가 특정 SKU를 **"재고 없이 주문 들어오면 그때 구매"**, **"재고 쌓을 계획 없음"** 이라고 하면 그 상품은 **made-to-order(주문 후 현지 매입)** 방식이다.

**Why:** 2026-05-20 Nespresso 버츄오 리치 초콜릿 케이스 — 한국 품절 SKU라 재고를 쌓지 않고 주문이 들어오면 캐나다에서 매입해 발송. 발송예정일을 짧게 잡으면 (현지 매입 + 한미택배 국제배송) 시간 때문에 배송 지연 클레임이 난다. 품절·희소 포지셔닝 상품에서 자주 쓰는 운영 방식.

**How to apply:**
- 상품 등록 시 fulfillment 모델을 확인하고, made-to-order면 `등록정보.md`·`product_info.json`에 기록.
- 네이버 등록 시 **발송예정일/발송기한을 현지 매입 + 국제배송 시간을 반영해 여유 있게 설정**하도록 등록정보 주의사항에 명시.
- 공급 리스크(현지 재고 소진·가격 변동)도 함께 메모 — 재고를 안 들고 있으므로 현지에서 못 사면 발송 불가.
- 상세페이지 본문에는 배송 안내를 넣지 않음([[feedback-detail-skip-shipping-outro]]) — 발송 리드타임은 네이버 발송예정일 필드로만 처리.
