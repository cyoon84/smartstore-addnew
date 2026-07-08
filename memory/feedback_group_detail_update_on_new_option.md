---
name: feedback_group_detail_update_on_new_option
description: 그룹상품에 새 맛/옵션 추가할 때마다 그룹 통합 상세(detail)도 반드시 업데이트 — 라인업에 새 옵션 반영
metadata:
  type: feedback
---

**그룹상품은 상세가 통합 1장 공유([[feedback_group_product_one_detail]])라, 새 맛·옵션(색상·용량 등)을 추가할 때마다 그 그룹의 통합 상세(detail.html)도 반드시 함께 업데이트한다.** 라인업 카드 섹션에 새 옵션(이미지+맛명+한줄설명+캡션)을 추가. 안 하면 옵션은 늘었는데 상세엔 안 보여 불일치 → 고객 혼란·신뢰 저하.

**How to apply:**
- 그룹에 옵션 추가 작업(등록·append) 시 체크리스트: ① 새 옵션 product_info/모델명 ② **그룹 통합 상세 라인업에 카드 추가** ③ 그룹 태그 커버리지 점검 ④ 그룹명이 새 옵션과 안 맞으면 일반화([[feedback_naver_group_lock]]).
- 그룹 통합 상세 파일 위치: `output/new-item/<group_slug>/<group_slug>_detail.html`. 새 맛 카드는 기존 카드 블록 복사 후 이미지 URL·맛명·설명 교체.
- **잊기 쉬운 단계** — 사용자가 "다른 맛 추가할 때 매번 그룹 상세 업데이트 잊지 말라"고 명시(2026-07-08 도리토스 4맛 그룹).

**Why:** 그룹은 옵션만 추가하면 판매는 되지만 상세는 자동 갱신 안 됨. 상세 라인업이 실제 옵션과 어긋나면 "이 맛 파나?" 혼선. 새 옵션 추가 = 상세 갱신 세트로 묶어 습관화. [[feedback_naver_group_lock]] · LEARNED_RULES §13-1
