---
name: detail-html-skip-shipping-section-and-outro
description: "상세페이지 detail.html 작성 시 \"🚚 배송 안내\" 섹션 + 마무리 인사 한 줄 자동 삽입 금지 (instructions.md 명시 룰)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 07a1afa3-0219-41ed-9f5f-e63003e83b0c
---

스마트스토어 상세페이지(`detail.html`) 작성 시 다음 섹션은 **자동으로 넣지 않는다**:

1. **🚚 배송 안내 섹션 전체** — 한미택배·무료배송·예상 도착일·상온 배송 안내 등 일체 배송 관련 단락
2. **마무리 인사 한 줄** — "오늘부터 한층 풍성해지는 아침을…", "올여름 가족과 함께 시원하게…" 등 클로징 문구
3. **Footer / 하단 안내문** — 일반 안내·CS 문구·서명류

**Why:** `smartstore-addnew/instructions.md` 의 "제외할 섹션"에 이미 명시되어 있는 룰. 배송 안내는 네이버 스마트스토어 상품 페이지의 "배송/교환/반품" 영역에서 자동 노출되므로 상세 본문에 중복 기재 X. 사용자가 직접 제거하는 작업 반복(2026-05-18 Dr Pepper Freezies 케이스에서 확인)을 막기 위함.

**How to apply:**
- 새 detail.html 만들 때 표준 섹션 목록: 헤드라인 → (영문 부제) → 후크 → 상품 소개 → ✨이런 점이 좋아요 → 🙆이런 분들께 추천해요 → 📋제품 정보
- 위 7개 섹션에서 끝맺음. 🚚 배송 안내·마무리 인사 절대 X
- 등록정보.md(`_등록정보.md`)에는 배송정책을 표 형태로 별도 기록(사용자가 네이버 등록 입력값으로 참조). 본문 detail.html에만 안 들어가는 것.

**관련:** [[feedback_no_usage_tips]] (활용 팁/레시피 섹션 금지)
