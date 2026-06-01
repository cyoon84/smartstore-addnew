---
name: detail-html-english-subtitle-under-headline
description: "상세페이지 헤드라인 바로 아래에 영문 풀네임 한 줄 부제 추가 (예 \"Dr Pepper Freezies - Dr Pepper Soda Flavour - 48 x 42 ml\")"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 07a1afa3-0219-41ed-9f5f-e63003e83b0c
---

스마트스토어 상세페이지 `detail.html` 헤드라인(이모지 + 한글 상품명) 바로 다음 줄에 **영문 풀네임 부제 한 줄**을 추가한다.

**형식:**
```
<p><strong>🥤 한글 상품명</strong></p>
<p>English Full Product Name - Variant - Pack Size</p>
<p><br></p>
<p>후크 한 줄...</p>
```

**예시 (Dr Pepper Freezies, 2026-05-18):**
- 한글 헤드라인: 🥤 닥터페퍼 프리지스 얼려먹는 슬러시 아이스바
- 영문 부제: Dr Pepper Freezies - Dr Pepper Soda Flavour - 48 x 42 ml

**Why:** 한국 직구·해외 셀러 신뢰도 어필 + 정품 원문 표기로 검색 매칭 + 마니아층(브랜드 영문 키워드 검색 사용자) 유입. 사용자가 직접 추가한 패턴(2026-05-18 Dr Pepper Freezies 최종본 확인).

**How to apply:**
- 영문 부제 구성: `브랜드/제품 영문 풀네임 - 변형/플레이버 - 용량/팩수` 순
- `<strong>` 굵게 처리 X (헤드라인보다 작은 비중)
- `<br>` 한 줄 뒤 본문 후크로 자연스럽게 연결

**관련:** [[feedback_detail_skip_shipping_outro]]
