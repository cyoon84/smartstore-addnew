---
name: pre-sale-regular-price
description: "매대 세일가가 식별되면(SAVE/정가 동시표시 등) 기본값으로 세일전 정상가를 원가로 채택(2026-06-02 디폴트 격상) + 등록정보·product_info에 정상가/세일가 둘 다 기록"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2b40431d-a3c3-4131-b8f4-a06980e1f6f2
---

**🔑 디폴트 (2026-06-02 격상):** 매대/페이지에서 **세일가가 식별되면**(예: "SAVE $3", "new lower price", 세일가+정가 동시 표시, "정가 ~~$X~~ → $Y") 사용자 명시가 없어도 **세일전 정상가를 원가로 채택**한다. (이전엔 "세일전 가격으로" 사용자 명시가 있을 때만 적용 → 이제 디폴트.) 사용자가 **"세일가로 책정해"**라고 명시할 때만 세일가 사용.

**Why:** 매장 세일은 일시적(예: Walmart "new lower price" 프로모션). 세일 종료 후에도 가격 변경 없이 운영하려면 정상가 기준 책정이 안정적. 세일 기간 동안은 실 마진이 더 커지는 효과.

**케이스:**
- 2026-05-27 Downy Calm Mega Sheet — 매대 세일가 $10.99 / 정상가 $15.99 → 정상가 책정 (당시엔 사용자 명시).
- 2026-06-02 Tetley Orange Pekoe 144티백 — 로블로 세일가 $8.99(SAVE $3) / 정가 $11.99 → 정가 $11.99 책정. 사용자 "이제 앞으로도 정가로 계산해"로 디폴트 격상.

**How to apply:**
- 가격 계산: 정상가 사용 (HST·마진·gross-up 평소 룰대로, `price_calc.py --cost <정상가>`)
- `product_info.json`: `cost_original` = 정상가, `cost_pricing_basis: "pre-sale regular price"`, `current_sale_price_cad`·`regular_price_cad` 둘 다 기록, `tax_label`/`sale_note`에 "(매대 세일가 $X / 정상가 $Y 기준)" 명시
- `등록정보.md`: "가격 책정 메모 — 세일전 정상가 채택" 섹션 + 정상가/세일가 모두 + 책정 사유 + 추적용 날짜
- 세일가 식별 안 되면(단일가만 표시) 평소대로 그 표시가 사용.

**🔑 예외 — Final Sale(파이널세일)은 세일가에서 마진 계산 (2026-07-04, §12-1):** 위 디폴트(세일가 식별→**정상가** 채택)의 **반대 예외**. 상품이 **"Final Sale"**(영구 클리어런스·단종 처분, 정상가 복귀 없음, `Final Sale`/`WMTM`/`Sale $X / Regular $Y`+재고소진)이면 **세일가를 `cost_original` 로** 채택. 일반 세일(일시 프로모션·Summer Sale 배너)은 정상가, **final sale 은 세일가**. 이유: final sale 은 재입고·정상가 복귀가 없어 실 매입가=세일가. 산식은 std 동일(어떤 가격을 cost 로 넣느냐만 다름 — price_calc 변경 불필요). product_info `pricing_mode:"final_sale_cost_plus"`·`cost_basis:"FINAL SALE $X (정가 $Y)"`. **같은 제품에 정가/파이널세일 색상 혼재면 색상별 baseline 다름** → 판매가 상이. (2026-07-04 룰루레몬 라켓백: 파이널세일 Club Blue/White $129→₩203,000 / 정가 색 $198→₩269,000.)

LEARNED_RULES.md §12·§12-1 정식 룰화. 관련: [[naver-fee]], [[hst-zero-rated]], [[price-patterns]].
