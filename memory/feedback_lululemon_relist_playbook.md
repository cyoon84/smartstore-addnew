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
4. **이미지:** `images.lululemon.com/is/image/lululemon/<style_color>_<view>` 는 봇월 밖 → `curl -A ... wid=1600` 로 뷰 1/2/3 다운(placeholder <8KB 스킵). 사용자가 플리커 업로드→앨범 URL. 앨범에서 `a[aria-label]`(=파일명 `색상_뷰`) + 썸네일 `id_secret` 로 정적 `_b`(1024) URL 맵 구성 후 HEAD 검증. blissful_pink_2 처럼 누락 있으면 표시.
5. **색상별 단일상품 폴더**(`lululemon_<제품>_<oz>_<색상>`): 상품명에 색상 포함(§13-4) · 전용 **스타일드 데코 detail.html**([[feedback_detail_styled_deco_template]] §17, 색상명=대표색) · product_info `bulk`(category_code, `origin_code`, rep_image, add_images, `import_tax:"관부가세 포함"`).
6. **원산지:** 백투라이프 물병 = **베트남 `0200014`**(사용자 확인). 다른 라인은 라벨 Made in 재확인(중국 흔함, 단정 금지 §9).
7. **블랙·화이트 등 기존 등록분 = 상세/이미지만 킵, 일괄엑셀 제외.** OutOfStock 색상(예 Foam Cloud)도 제외.
8. **일괄엑셀**(신규 색상만) `build_bulk_excel.py <slugs> --out _batch/..._bulk_upload.xlsx` → **bulk-excel-verifier** 검증(§5-1).
9. **그룹명**(§13-1 색상 미포함) + 옵션명(색상만 or `<용량> <색상>`) + **태그**(물병/스포츠물병축 §10) + **카테고리**(텀블러 50004540 / 물병 50004567 / 보온·보냉병 50004578).
10. **재고 모니터 추가:** `output/new-item/lululemon_back_to_life_bottle_18oz/lulu_stock_monitor_config.json` 의 `monitors[]` 에 append(id·name·lululemon_url·registered_options[color_ko/en/style_color]) → 월간 점검(`lulu-stock-monthly-check`)이 자동 커버([[feedback_bulk_upload_excel]]).

관련: [[feedback_model_name_from_store]] · [[feedback_naver_category_snack]](카테고리 지어내기 금지) · [[feedback_detail_styled_deco_template]]
