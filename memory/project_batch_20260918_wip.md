---
name: project-batch-20260918-wip
description: 9/18(금) 배치 이월분 — 박영근 콜게이트 오주문 반품 후 재구매, Walmart 콜게이트 반품 환불 추적
metadata:
  type: project
---

**박영근** (9/15 발주발송 `20260914_1452`, 상품번호 11966126277)
- 주문: `콜게이트 토탈 화이트닝 미백 치약 120ml x 3개 세트 민트향` × 2 (배송비 ₩15,000)
- 2026-09-14 Walmart #600000116762435 에 **Colgate Total Active Prevention Clean Mint** 3x120ml ×2($15.94, $2 할인 후)가 잘못 담겼다 — 화이트닝 아님.
- 사장님 결정(2026-09-15): **Clean Mint 반품 → Whitening 재구매 → 금요일(9/18) 배치로 출고.**
- 올바른 제품: `Colgate Total Active Prevention Whitening Toothpaste, Mint, Value pack 3x120ml`(7/30 Walmart) 또는 Amazon.ca `Colgate Total Whitening 3x120mL` $7.97(8/28).
- 9/15 한미 업로드·정산·워드에서 제외 완료. **한미 사이트의 박영근 건(#1305263, 송장 6080091171701)은 사장님이 2026-09-15 삭제함** → 그 송장번호는 폐기, 재사용하지 말 것.
- **금요일 처리법:** 네이버에서 발송처리를 안 했으니 박영근 주문은 발주발송 화면에 그대로 남아 **9/18 export 에 자동으로 다시 잡힌다.** 삭제된 한미 건을 되살릴 필요 없이 hanmi-flow 1단계를 평소대로 돌리면 새 접수 행과 새 송장번호가 생긴다. export 에 안 보이면 그때 이 메모로 수기 포함.
- 9/15 발송처리 파일에도 박영근은 없다 — 네이버 발송처리를 올릴 때 박영근이 빠져 있는 게 정상.

**Walmart #600000116762435 — ✅ 환불 확인·상계 완료 (2026-09-17)**
- 최종영수증: 진성준(다우니 언스토퍼블 퓨전 선셋앤시트러스 598g×1) + 조윤범(링클릴리저 90ml×1) = **9/15 배치 COGS**.
- 콜게이트 Clean Mint 3x120ml×2 ($15.94+HST$2.07=$18.01) 반품 → 2026-09-17 "Your refund was issued" 메일로 환불 확정(msgId 1a0acb2dca5e3ebd).
- 장부(물건산거 COGS) 171행을 순액으로 정정: $44.74 → **$26.73**(subtotal $23.65 / tax $3.08). 환불영수증 `receipts/2026-09/2026-09-17_Walmart_refund_600000116762435_1a0acb2dca5e3ebd.txt` 저장.

**How to apply:** 9/18 배치 처리할 때 이 파일부터 확인. 박영근 COGS 는 재구매한 Whitening 영수증 기준(§19-3-1 구매일 FX).
[[project_order_settlement]] · [[feedback_product_name_verbatim]]

**✅ 박영근 재구매 완료 (2026-09-18 확인)**
- 2026-09-16 19:59 **Walmart Scarborough #3159** 매장에서 `TTL WT 3PK`(UPC 058000142430 = Colgate Total **Whitening** 3x120ml) $7.97×2 + HST $2.07 = **$18.01** (AMEX 2201) 재구매.
- 같은 매장 20:08 ECOM #600000116762435 Clean Mint 반품 CREDIT $18.01 — 장부 171행에 이미 순액 반영돼 있어 재기입 안 함.
- 장부 COGS 180행 · 9/18 정산 COGS ₩17,672 (FX 981.24, 9/16) 반영. Todoist 박영근 콜게이트 cross off.
- 이 이월 건은 종결. 이용득 콜게이트 ×3 은 Walmart.ca #600000111447791(9/17)로 별도 충당.

**🕐 9/18 → 다음 배치 이월 (2026-09-18)**
- **배수철** 블루제이스 류현진 유니폼 ALT2/99/XL ×1 (무배) · **김영선** 커클랜드 크리미 아몬드 버터 765g ×1 — 둘 다 미구매라 오늘 못 나감.
- 9/18 정산은 `--exclude-recipient 배수철 --exclude-recipient 김영선` 로 돌렸다(재실행 시 반드시 같이). 발송처리 안 하므로 다음 export 에 자동으로 다시 잡힌다.
- Todoist: 두 수취인 + 사야할 2줄을 `🕐 이월 대기` 부모로 이동.
