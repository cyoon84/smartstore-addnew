---
name: no-french-in-detail
description: 캐나다 이중언어 라벨이어도 상세페이지·상품명·등록정보에 프랑스어 표기 일절 사용 금지
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a4e8e355-5663-4b02-b658-59a58ea27bce
---

캐나다 제품 패키지에 영어/프랑스어가 병기되어 있어도 (예: Rich·Riche, Same Delicious Taste / Même goût délicieux, café instantané), 산출물에는 영어만 사용. 프랑스어는 부제·바디카피·feature bullet 어디에도 넣지 않음.

**Why:** 한국 고객은 프랑스어에 관심 없음. 캐나다 이중언어 라벨이라는 사실 자체도 본문에서 강조하지 않음 (이전에 "영어·프랑스어 병기 라벨" bullet 넣었다가 제거 지시 받음).

**How to apply:**
- 부제: "Nescafé Rich Instant Coffee" ✅ / "Nescafé Rich · Riche Instant Coffee" ❌
- 인용구: 영문 카피만 인용 ("Same Delicious Taste" ✅ / "Même goût délicieux" ❌)
- 스펙·맛 표기도 영어만: "메이플 (Maple)" ✅ / "메이플 (Maple / Érable)" ❌
- 캐나다 매장 사진(코스트코·로블로 등)에서 프랑스어 OCR 했더라도 한국어 변환 시 프랑스어 부분은 버림

**🔑 예외 — 사진에 불어가 그대로 보이는 경우엔 캡션으로 설명한다 (2026-08-05 사장님 지시로 완화):**
원래는 "영어·프랑스어 병기" 언급 자체를 금지했는데, **라벨 클로즈업처럼 사진에 `MILD/DOUCE` 가 그대로
찍혀 있으면 설명이 없는 쪽이 더 혼란**을 준다(다른 시장 제품인가? 오배송인가?). 그래서:
- ❌ **불어 단어를 카피로 쓰는 것** — 여전히 금지 (부제·스펙·bullet·인용구)
- ✅ **사진에 보이는 불어를 캡션에서 한국어로 설명** — 허용
  예: `라벨에 TACO BELL · SAUCE MILD · 207 mL 이 표기되어 있습니다. 캐나다에서 파는 제품이라 영어와 불어가 함께 적혀 있습니다`
- 단, **핵심포인트 bullet 로 만들지는 말 것** — 셀링포인트가 아니라 오해 방지용 각주다.
  (2026-08-05: `영문·불문 이중 표기` 를 핵심포인트로 넣었다가 반려 → `캐나다 정규 패키지` 로 바꿨다가 그것도 반려.
   결론: bullet 로는 넣지 않고, 사진 캡션에서만 설명한다.)

연관: [[feedback_brand_ko_names]], [[feedback_no_source_repeat]]
