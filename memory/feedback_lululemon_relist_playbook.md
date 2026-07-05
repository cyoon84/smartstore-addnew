---
name: lululemon-relist-playbook
description: 룰루레몬 제품 재등록(리바이벌) 반복 워크플로 — 실브라우저 크롤·색상별 단일→그룹·스타일드 데코·재고 모니터
metadata:
  type: feedback
---

사용자가 품절/기존 룰루레몬 제품들을 **색상별 단일상품→그룹 병합 + 스타일드 데코 + 월간 재고점검** 방식으로 순차 재등록(리바이벌)한다. 새 룰루레몬 SKU 요청이 오면 아래 플레이북대로.

**Why:** 룰루레몬은 컬러/재고 변동이 잦아 단일 등록 후 그룹 옵션추가가 빠르고([[feedback_naver_group_lock]]), 공홈이 Akamai 봇차단이라 표준 크롤이 안 됨. 2026-07-02 백투라이프 물병 18oz(9색)·24oz(6색)에서 정립.

**How to apply (순서):**
1. **입력:** 공홈 URL(색상 포함) + 현재 스마트스토어 판매가·배송비.
2. **실브라우저 필수** (claude-in-chrome — 사용자 Chrome 선택). 헤드리스 curl/WebFetch·자동화 Chrome = 봇차단(403/GE401001). ProductGroup JSON-LD `hasVariant` 추출: `{color, sku, style_color(뷰접미 _1 제거), price, availability}`. **`offers` 는 배열/객체 둘 다 대응**(`Array.isArray(v.offers)?v.offers[0]:v.offers`). 추출 JS = `python3 scripts/lulu_stock_check.py --fetch-help`.
3. **가격 판단:** 현재 환율·HST 13%·수수료 6.6% 로 현재 판매가 역산 마진 확인([[feedback_naver_fee]]). 전 색상 균일가면 유지, 프리미엄 컬러(예 $44 vs $38)는 옵션가 상향. §0-A 는 기존 판매 재등록이라 스킵(국내 시세 재확인 불필요).
4. **이미지 — 🔑 CDN 직링크가 기본, 플리커는 폴백 (2026-07-04 골프파우치에서 개선):** `images.lululemon.com/is/image/lululemon/<style_color>_<view>` 는 봇월 밖. **네이버 일괄등록 대표이미지(W)·추가이미지·상세 img 가 이 CDN 직링크를 그대로 받아준다(골프파우치 실증)** → 그동안 필수였던 **플리커 수동 업로드 왕복(다운→업로드→앨범URL→맵→스왑) 전체를 스킵**(몇 분 세이브). `bulk.rep_image`/`add_images` 에 CDN URL 직접. **크기: `?hei=1000`(→833×1000, 네이버 권장 높이) 또는 `?wid=1000` 권장** — `wid=1600`(1600×1920)은 필요 이상. 룰루 컷은 5:6 세로형 흰배경. **폴백:** 네이버가 CDN 핫링크를 거부하면 그때 플리커 — 로컬 다운(`curl -A ... hei=1000`, placeholder <8KB 스킵)해 색상친화명(`<색상>_<뷰>.jpg`)으로 저장 + `_batch/..._FLICKR_폴백_매니페스트.md` 준비 → 사용자가 앨범 업로드→URL→`a[aria-label]`(파일명=색상_뷰)+썸네일 `id_secret` 로 `_b`(1024) 맵 구성→스왑. **상세 이미지 데코:** 색상별 매트 프레임(`border:2px solid <메인색>;background:<라이트틴트>;padding:9px;border-radius:14px`) 두르면 "브랜드 이미지 그대로 빼온" 느낌 제거([[feedback_detail_styled_deco_template]]).
5. **색상별 단일상품 폴더**(`lululemon_<제품>_<oz>_<색상>`): 상품명에 색상 포함(§13-4) · 전용 **스타일드 데코 detail.html**([[feedback_detail_styled_deco_template]] §17, 색상명=대표색) · product_info `bulk`(category_code, `origin_code`, rep_image, add_images, `import_tax:"관부가세 포함"`).
6. **원산지:** 백투라이프 물병 = **베트남 `0200014`**(사용자 확인). 다른 라인은 라벨 Made in 재확인(중국 흔함, 단정 금지 §9).
7. **블랙·화이트 등 기존 등록분 = 상세/이미지만 킵, 일괄엑셀 제외.** OutOfStock 색상(예 Foam Cloud)도 제외.
   - **🔑 시세비교 시 제목 아니라 사진으로 제품 동일성 확인 (2026-07-05 Clear vs Sport 32oz):** 룰루레몬은 같은 이름 계열에 **비주얼이 다른 변형**이 공존한다 — 예 "Back to Life **Clear** Bottle 32oz"(투명 트라이탄 옴브레) vs "Back to Life **Sport** Bottle 32oz"(불투명 솔리드). 국내 리스팅 제목엔 둘 다 "클리어"·"32oz"로 뒤섞여 뜨므로 **네이버쇼핑 이미지(phinf) 를 직접 받아 우리 소스 이미지와 대조**해야 가격 앵커를 올바로 잡는다. 한국 공홈/SSG ₩45,000 이 불투명 Sport 였고, 투명 Clear(우리 것)는 직구 ₩44,900~63,900 밴드로 별개였음 — 사진 안 봤으면 "가격 안 됨"으로 오판할 뻔. (relist 라 §0-A 스킵했어도, **가격이 의심되면 사진 대조로 재검증**.)
8. **일괄엑셀**(신규 색상만) `build_bulk_excel.py <slugs> --out _batch/..._bulk_upload.xlsx` → **bulk-excel-verifier** 검증(§5-1).
9. **그룹명**(§13-1 색상 미포함) + 옵션명(색상만 or `<용량> <색상>`) + **태그**(물병/스포츠물병축 §10) + **카테고리**(텀블러 50004540 / 물병 50004567 / 보온·보냉병 50004578).
   - **🔑 멀티컬러는 "단일상품+옵션" 방식이 그룹병합보다 나을 수 있음 (2026-07-05 클리어보틀 32oz 9색):** 색상별 단일→그룹병합 대신 **한 상품ID에 9색 옵션(조합형)** + **9색 통합 상세 1장**. product_info `options[]` → build_bulk_excel 1행(상품명=그룹명 색상미포함, 옵션값=color_ko 콤마구분). 상세엔 옵션명 pill + 공식 풀네임 병기([[feedback_bulk_upload_excel]] 단일상품+옵션 절).
   - **🔑 색상명 = 창작 금지, 공식명 기준 (2026-07-05 32oz 클리어보틀):** 색상 라벨을 임의로 지어내지 말 것(피치핑크·라즈베리 등 ❌). 룰루레몬 멀티톤 컬러웨이(예 "Pink Pearl/Passionate/Lavender Frost")는 **① 옵션값 = 각 컬러웨이의 "고유 구분 단어"**(서로 안 겹치는 공식 단어 하나, 예 Lavender Frost·Foam Cloud·Washed Yellow…) — 풀네임 그대로 쓰면 `Pink Pearl` 이 9색 중 5개에 반복→그룹 합침 노출 시 **"반복 단어 다수" 태클**(§13-1). **② 상세페이지엔 공식 풀네임** 표기(고객이 공홈과 대조, 정보 손실 0). 옵션값 짧게(스타벅스 그룹 "…커피 Blonde Espresso, 10개입, 1개" 처럼)라 그룹명(색상 미포함)은 짧게 유지되고 단품 상품명도 45자 내. build_bulk_excel: product_info `color_ko`=고유단어(옵션값) / `color_en`=풀네임 / detail color_pill 이 en(풀네임) 표기.
10. **재고 모니터 추가:** `output/new-item/lululemon_back_to_life_bottle_18oz/lulu_stock_monitor_config.json` 의 `monitors[]` 에 append(id·name·lululemon_url·registered_options[color_ko/en/style_color]) → 월간 점검(`lulu-stock-monthly-check`)이 자동 커버([[feedback_bulk_upload_excel]]).

관련: [[feedback_model_name_from_store]] · [[feedback_naver_category_snack]](카테고리 지어내기 금지) · [[feedback_detail_styled_deco_template]]
