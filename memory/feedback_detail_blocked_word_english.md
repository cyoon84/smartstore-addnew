---
name: feedback_detail_blocked_word_english
description: 네이버 상세설명 금칙어 검사는 공백 제거 후 매칭 — 영문 제품유형명(Taco Seasoning Mix→tacoseasoningmix)이 금칙어로 걸릴 수 있음
metadata:
  type: feedback
---

네이버 스마트스토어는 **상세설명(상품상세)** 의 금칙어를 **공백을 제거한 뒤** 매칭한다. 그래서 detail.html 헤드라인 아래 넣는 **영문 풀네임 부제**(예: `Old El Paso Taco Seasoning Mix`)가 공백 제거 시 `tacoseasoningmix` 같은 토큰이 되어 **"등록불가 단어(…:기타) 포함"** 으로 업로드가 거부될 수 있다.

**Why:** [[feedback_detail_english_subtitle]] 룰은 헤드라인 아래 영문 부제 한 줄을 권장하지만, 영문 제품유형 조합어가 네이버 금칙어 사전과 충돌하면 상세설명 전체가 거부된다. 상품명·태그는 한글이라 무관 — **상세설명의 영문 조합어만 문제.**

**How to apply:**
- 업로드가 `<영문조합>:기타` 사유로 거부되면 → detail.html 에서 **그 영문 부제 줄을 제거**(헤드라인 한글은 유지). 본문에 같은 영문 조합이 더 있으면 같이 제거.
- 선제적으로: 영문 부제를 넣되 거부되면 빼는 식. 브랜드 영문(`Old El Paso`→`oldelpaso`)도 같은 위험 — 거부 시 영문 전부 제거.
- 일괄등록 엑셀 재생성 시 detail.html 만 고치고 `build_bulk_excel.py` 다시 돌리면 됨(상세설명 칸=detail.html 그대로).

> 2026-06-17 올드엘파소 타코 시즈닝 믹스 24g 3종 일괄등록 — 상세설명 영문 부제 `Old El Paso Taco Seasoning Mix (...)` 가 `tacoseasoningmix` 금칙어로 거부됨. 영문 부제 줄 제거 후 통과. [[feedback_detail_html_bare_fragment]]
