---
name: Group product — one unified detail page, not per-option
description: 그룹상품(사이즈/맛 옵션) 상세페이지는 옵션별 분리하지 말고 한 장으로 통합 작성
type: feedback
originSessionId: 4e68369f-e5cc-4b30-9fe7-25cf8bc36689
---
그룹상품으로 등록하는 SKU는 옵션(사이즈·맛·색상 등)이 여러 개여도 **상세페이지(detail.html)는 통합 1장**으로 작성한다. 옵션별로 별도 detail.html을 만들지 않는다.

**Why:** 2026-05-18 Nescafé Gold Espresso 그룹상품 케이스에서 학습 — 100g·200g 옵션 각각 별도 detail.html을 만들었더니 사용자가 "한 상세페이지에서 둘 다 커버하게 워딩 바꿔" 로 정정. 네이버 그룹상품은 상품 1개에 옵션이 붙는 구조이므로 상세페이지도 한 장이 자연스럽고, 옵션 간 cross-sell도 같은 페이지 안에서 처리하는 게 좋음.

**How to apply:**
- 그룹상품 detail.html은 옵션 공통 USP(브랜드·라인·성분·인증·원산지)를 메인 컨텐츠로 작성.
- 본문 안에 "사이즈 안내" / "옵션 안내" 섹션을 두고, 옵션별 포지셔닝(예: 100g=입문, 200g=대용량)을 한 줄씩만 명시. 구매자가 옵션에서 선택하도록 유도.
- "이런 분들께 추천해요" 섹션은 모든 옵션 사용자 시나리오를 한 번에 커버.
- 파일명은 사이즈/옵션 접미사 빼고 `{sku_base}_detail.html` 형식으로 통합 (예: `nescafe_gold_espresso_detail.html`).
- 단일제품에서 그룹상품으로 전환 시 기존 옵션별 detail.html은 superseded 처리하고 통합본만 사용.

**예외:** 옵션이 브랜드·맛·정체성까지 다른 경우 (예: 같은 모델명이지만 한정판 vs 정규판이 본질적으로 다른 컨셉)에는 분리 검토. 단순 사이즈/용량 옵션은 항상 통합.
