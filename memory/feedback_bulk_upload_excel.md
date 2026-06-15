---
name: feedback_bulk_upload_excel
description: 등록 산출물 만든 뒤 네이버 일괄등록 엑셀(_bulk_upload.xlsx)도 build_bulk_excel.py 로 함께 생성. 메인 소유. 영양제는 해외사업자 제약상 기타건강보조식품 고정
metadata:
  type: feedback
---

등록 4종(등록정보·detail.html·product_info·이미지) 생성 후 **네이버 스마트스토어 일괄등록 엑셀** `<slug>_bulk_upload.xlsx` 도 5번째 산출물로 함께 만든다.

**Why:** 사용자가 네이버 일괄등록 템플릿(`guide/일괄등록 guide/ExcelSaveTemplate_*.xlsx`)에 직접 채운 L라이신 예제 + 코드 리스트 3종(category/originarea/delivery-companies)을 학습 소스로 줌. product_info + detail.html → 템플릿 칸 매핑은 결정론적 변환이라 listing-writer 가 아니라 **메인 오케스트레이터가 소유**(가격계산·저장과 같은 계열).

**How to apply:**
- 단건: `python3 scripts/build_bulk_excel.py <slug>` → 제품 폴더에 `<slug>_bulk_upload.xlsx`(1행).
- **배치(source-launch): 슬러그 여러 개를 한 번에 넘김 → 한 엑셀에 SKU 당 한 행** (기본 `output/new-item/_batch/bulk_upload_<날짜>.xlsx`). 여러 제품 한 파일로 일괄 업로드. source-launch 파이프라인 7단계(저장 직후, Slack 직전)에서 메인이 실행.
- **온디맨드 배치: 사용자가 "이 제품 이 제품 묶어서 일괄등록 엑셀 만들어줘"** 하면 → 말한 제품들을 `output/new-item/` 폴더명(슬러그)으로 매칭해 `build_bulk_excel.py <slug…> --out output/new-item/_batch/bulk_upload_<날짜>.xlsx` 배치 실행. 이미 등록 산출물 있는 제품을 임의로 골라 한 파일로 묶음. (사용자가 "일괄발송"이라 말해도 = 일괄**등록** 엑셀. 실제 주문 출고/송장은 hanmi-flow·epost-flow 로 별개.)
- 템플릿 1행(그룹헤더)·2행(필드명) 보존, 가이드 3~6행 삭제, 데이터는 3행부터.
- **상세설명(Y)칸 = detail.html 베어 fragment 그대로** 투입(`<p><strong><br>`).
- **원산지코드 텍스트(`@`)로 앞자리 0 보존** — **기본 캐나다 `0204006` 고정**(전 상품 캐나다로 깔고 사용자 1회 수동 보정. 자동 국가해석 안 씀), 택배사도 EPOST 기본 고정. `bulk.origin_code`/`delivery_code` 로만 덮어씀.
- **배송방법 구분자 U+201A(‚)** — `택배‚ 소포‚ 등기`(일반 콤마 아님).
- **해외사업자 제약: 영양제 카테고리는 `기타건강보조식품`(50002615) 고정** — 아미노산 등 세분류 선택 불가. fallback 아니라 정답. 더 맞는 카테고리 가능하면 사용자가 등록화면 수동 변경.
- **관부가세(K) = 영양제·음식은 무조건 `관부가세 포함` (2026-06-12):** 카테고리가 식품(`식품` 하위 전부 — 음료·커피·스낵·과자 등) 또는 영양제·건강식품이면 K칸 자동 `관부가세 포함`. 비식품(생활용품·잡화 등)은 CONFIG 기본 `관부가세 미포함`. 스크립트가 cat_paths(`식품/영양제/건강식품/건강보조식품`)+영양제 강제코드 50002615 로 판정. `bulk.import_tax` 명시는 최우선.
- **배송비 = product_info 에서 SKU별 자동 도출 (2026-06-12):** `resolve_shipping()` 이 `shipping` dict(`per_unit_krw`→수량별 1개당 / `absorbed_into_price`→무료)·`shipping_krw`/`policy` 문자열(`"M개당 N원"`→qty=M fee=N, `"개당 N원"`→qty=1)을 파싱해 배송비유형·기본배송비·수량별부과수량을 채움. 우선순위 **`bulk` 오버라이드 > resolve_shipping > CONFIG**. CONFIG `6개당 15,000` 은 shipping 정보 전무할 때만 쓰는 fallback — **전 SKU 에 일괄로 덮지 말 것**(이전 버그). 판매가도 `calculation.sell_price_krw` 중첩 키까지 읽음.
- 스토어 기본값(shipping 부재 시 fallback): 우체국택배(EPOST)·수량별 6개당 15,000·**배송비 결제방식 `선결제`(무조건 — 착불 X, 2026-06-07 사용자 지시)**·재고 1000·신상품·과세상품·관부가세 미포함. **반품/교환배송비 각 50,000 · A/S 전화 `+16478010784` · A/S 안내 "수령시 파손된 제품에 한해 환불 가능합니다"**. SKU별은 product_info `bulk` 블록으로 오버라이드.
- **대표이미지(W) = 호스팅 URL 있으면 자동 입력 (2026-06-12):** 사용자가 Flickr 등에 올려 URL 주면 `bulk.rep_image`(또는 `images.rep_image_url`)에 넣어 자동 채움. URL 없을 때만 네이버 직접 업로드 수동 단계(블로커 아님). 매대 진열컷이면 깔끔한 제품컷 권장 1줄 안내하되 일단 채움. 반품/교환·A/S 는 CONFIG 로 자동.

[[feedback_naver_category_snack]] [[feedback_naver_category_toplevel_lock]] [[feedback_output_location]]
