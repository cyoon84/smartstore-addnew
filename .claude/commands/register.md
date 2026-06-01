---
description: 사진/URL + 가격 정보로 스마트스토어 상품 등록 4종 산출물 생성
argument-hint: [사진/URL + 가격 한 줄 또는 블록]
---

스마트스토어(finchmart_ca) 신규 상품 등록 워크플로를 실행한다. 입력: $ARGUMENTS

CLAUDE.md 의 워크플로(§2) 순서를 그대로 따른다:

1. **입력 파싱** — 사진/URL, 원가, HST 여부, 배송비, 마진, 모드(single/group). 빠진 항목만 묻고
   모드 누락은 single 기본. dispatch 한 줄/블록 형식 모두 인식.
2. **국내 시세 확인 (§0-A, 필수)** — 쿠팡·네이버쇼핑 검색으로 경쟁력 판단 한 줄 + A)진행
   B)가격조정 C)접기 선택지. "한국 미출시" 명시면 스킵하고 그 사실을 1줄 기록. **GO 받기 전 산출물 X.**
3. **가격 계산** — 반드시 scripts/price_calc.py 의 알맞은 모드로. 환율은 현재 시점 확인.
   단위(CAD/KRW) 애매하면 먼저 확인.
4. **(URL 있으면) 크롤·추출** — product-detail-page-ko 스킬 사용.
5. **작성** — 상품명(§5), 태그 10개(§8), 카테고리, detail.html 베어 fragment(§7).
6. **저장** — output/ 루트에 <ascii_slug>_등록정보.md / _detail.html / _product_info.json 저장 후 `python3 scripts/organize_output.py --apply` 실행 → output/new-item/<slug>/ 로 분류.
7. **완료 후** — 등록정보.md 전체를 Slack #new-item 에 전송.

데이터 진실성(§9): 추출 안 된 필드는 비워둔다. 가짜 데이터 금지.
