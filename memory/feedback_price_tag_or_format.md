---
name: Canadian supermarket price tag "N/X.XX OR Y.YY EA" format
description: Loblaws/Superstore/No Frills 매대 가격표 "N/X.XX OR Y.YY EA" 양식 = N개 묶음 X.XX 또는 단품 Y.YY. 기본 해석은 단품가(Y.YY) 사용. 첫 자리 숫자 OCR 오인 흔함.
type: feedback
originSessionId: 626bb7d0-2d38-45b3-92f5-7b96c476c259
---
**규칙:** Loblaws / Real Canadian Superstore / Independent / No Frills 등 캐나다 슈퍼마켓 가격표 양식 **"N/X.XX OR Y.YY EA"** 는 항상 다음을 의미:
- **N개 묶음 X.XX** (멀티-바이 프로모 가격)
- **단품 Y.YY EA** (단품 정상가)
- 정상은 `Y.YY > X.XX / N` — 묶음 사면 개당 더 쌈

**기본 해석:** **단품가(Y.YY)** 를 cost_original로 사용. 우리가 재구매할 때 단품 살 가능성 더 높음, 보수적 산정.

**Why:** 2026-05-17 Nestlé Snack Size Collation 케이스에서 학습. 초기 사진 OCR "2/15.50 OR 3.2 EA"로 잘못 해석 → 사용자 정정 "2/$5.50 OR $3.20 EA". 가격은 산식 근본 입력이라 잘못된 단가 가정 시 모든 산출물 다시 만들어야 함.

**How to apply:**
- OCR 결과 `Y.YY < X.XX / N` (단품가가 묶음 개당가보다 낮음) 나오면 **OCR 오인 의심** → 사용자에게 가격표 사진 / 정확한 숫자 확정 요청
- 첫 자리 숫자(1·8·5·6 등) 오인이 흔함 — 사진 각도/조명/스티커 겹침 등
- 사용자가 명시적으로 "멀티-바이로 산다 / 묶음가 적용"이라고 하면 X.XX/N을 cost로 사용. 아니면 기본 단품가(Y.YY)
- product_info.json `cost_source` 필드에 가격표 원문 표기와 해석 노트 기록
