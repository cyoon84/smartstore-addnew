---
name: feedback_bulk_upload_excel
description: 등록 산출물 만든 뒤 네이버 일괄등록 엑셀(_bulk_upload.xlsx)도 build_bulk_excel.py 로 함께 생성. 메인 소유. 영양제는 해외사업자 제약상 기타건강보조식품 고정
metadata:
  type: feedback
---

등록 4종(등록정보·detail.html·product_info·이미지) 생성 후 **네이버 스마트스토어 일괄등록 엑셀** `<slug>_bulk_upload.xlsx` 도 5번째 산출물로 함께 만든다.

**🔑 단일상품+옵션(조합형) 지원 — 그룹상품 대안 (2026-07-05 클리어보틀 32oz 9색, 업로드 성공):** product_info 에 `options[]`(2개 이상) 있으면 `build_bulk_excel.py` 가 **1행 = 단일상품 + 다중옵션**으로 채운다: 상품명=`group_name_ko`(색상 미포함), 옵션형태=`조합형`, 옵션명=`색상`, 옵션값=각 `color_ko` **콤마(,) 구분**, 옵션가=`0,0,…`(균일), 옵션재고=`1000,…`(개수 정합). 부모 폴더에 **9색 통합 상세 1장**(`<slug>_detail.html`) + 부모 `bulk`(rep_image=대표색, add_images=나머지 색). **한 상품ID에 옵션 여럿 = 그룹상품(색상별 단일→병합)보다 관리 깔끔** — 상세 1장에 전 옵션 표기(옵션명 pill + 공식 풀네임 병기). **네이버 제약: ①상품명 50자 미만 권장(넘으면 "검색최적화" 태클) → 색상은 상품명 말고 옵션값으로 ②옵션값 각 25자 미만("옵션값N 25자보다 작게" 삐빅) → 긴 색상조합은 24자 이내로.** [[feedback_lululemon_relist_playbook]]

**🔑 진짜 2축 조합형(`option_axes`) + 옵션별 옵션가 — 네이버 템플릿 정식 포맷 (2026-07-13 룰루 메탈벤트테크 반팔, 10색×6사이즈):** 위 `options[]` 는 옵션값을 콤마로 나열한 **단일축**(또는 `"체리엠버 / M"` 결합축)이라 색상·사이즈가 한 드롭다운에 섞인다. **컬러·사이즈를 별도 축**으로 두려면 네이버 정식 2축 포맷(ExcelSaveTemplate 예시 r4)을 써야 한다:
- **옵션명 = 축이름 줄바꿈(`컬러\n사이즈`)** (최대 3축, 각 25자), **옵션값 = 축별 값(축은 `\n`, 값은 콤마: `빨강,노랑\nS,M,L`)**.
- **🔑 옵션가·옵션재고 = "첫번째 옵션값(1축) 기준" 콤마 리스트** (`0,100` / `10,20`) — 1축 각 값에 조합되는 전체(그 색상의 모든 사이즈)에 동일 적용. **→ 색상별 옵션가가 이 포맷으로 정확히 들어감**. 옵션가 범위: 판매가 1만↑ = **±50%** (79,000의 +29,600=+37.5% OK), **최소 1개는 0** 필수, 미입력=0.
- `build_bulk_excel.py` **`option_axes` 모드** 추가: `{"names":["컬러","사이즈"],"values":[[색상…10],[XS..XXL]],"axis1_price":[0,29600,…],"axis1_stock":[1000,…]}` → 옵션명/값 줄바꿈, 옵션가/재고는 1축(색상) 기준. (`option_axes` 있으면 우선, 없으면 기존 `options[]`. 결합축 `options[].option_add` per-옵션 옵션가도 지원.)
- **⚠️ 2축 full-grid 한계:** 사이즈축 공유라 **색상별 재고 사이즈 차이(체리엠버·핑크플레어=M·L·XL만)면 없는 조합이 available 로 생성** → 등록화면에서 그 조합만 삭제/재고0(product_info `invalid_combos_remove_in_editor` 에 기록). bulk 는 1축(색상) 단위 재고만 표현.
- **기준가+옵션가 패턴:** 판매가(기준가)=최저옵션(예 파이널세일 색 ₩79,000), 나머지 색상 옵션가 +차액. 대표이미지·1번 옵션(1축 1번값)=기준가 색상. [[feedback_lululemon_relist_playbook]]

**🔑 상품정보제공고시 품명/모델명/제조자 자동 채움 (2026-07-05):** `build_bulk_excel.py` 가 원래 상품정보제공고시(기타 재화) **품명·모델명·제조자 칸을 비워뒀는데**, 이제 **품명=한글 상품명 · 모델명=product_info `model_name`(영문 공식 풀네임) · 제조자=브랜드** 로 자동 채운다(FIELD 에 `gosi_name/gosi_model/gosi_maker` 추가, 헤더 개행 제거본으로 매칭). 공식 제품명(예 "lululemon Back to Life Clear Bottle 32oz *Straw Lid")이 모델명 칸에 들어가야 SEO/모델매칭에 유리. **🔑 모델명 칸 네이버 제약 2개 (`clean_gosi_model()` 처리):** ① **50자 미만**(에러 문구 "50자보다 작게"=strictly<50 → 49자 이하로 컷) ② **등록불가 특수문자 `\ * ? " < >` 제거**. 순서: 색상 접미(" - Color") 제거 → 금지문자 제거 → 공백정리 → 50자↑면 브랜드 접두(lululemon) 제거 → 49자 컷. (2026-07-05 연속 에러로 발견: 88자 → 특수문자 `*Straw Lid`의 별표 → "Back to Life Clear Bottle 32oz Straw Lid" 40자로 정착.) [[feedback_model_name_from_store]]

**Why:** 사용자가 네이버 일괄등록 템플릿(`guide/일괄등록 guide/ExcelSaveTemplate_*.xlsx`)에 직접 채운 L라이신 예제 + 코드 리스트 3종(category/originarea/delivery-companies)을 학습 소스로 줌. product_info + detail.html → 템플릿 칸 매핑은 결정론적 변환이라 listing-writer 가 아니라 **메인 오케스트레이터가 소유**(가격계산·저장과 같은 계열).

**How to apply:**
- 단건: `python3 scripts/build_bulk_excel.py <slug>` → 제품 폴더에 `<slug>_bulk_upload.xlsx`(1행).
- **배치(source-launch): 슬러그 여러 개를 한 번에 넘김 → 한 엑셀에 SKU 당 한 행** (기본 `output/new-item/_batch/bulk_upload_<날짜>.xlsx`). 여러 제품 한 파일로 일괄 업로드. source-launch 파이프라인 7단계(저장 직후, Slack 직전)에서 메인이 실행.
- **온디맨드 배치: 사용자가 "이 제품 이 제품 묶어서 일괄등록 엑셀 만들어줘"** 하면 → 말한 제품들을 `output/new-item/` 폴더명(슬러그)으로 매칭해 `build_bulk_excel.py <slug…> --out output/new-item/_batch/bulk_upload_<날짜>.xlsx` 배치 실행. 이미 등록 산출물 있는 제품을 임의로 골라 한 파일로 묶음. (사용자가 "일괄발송"이라 말해도 = 일괄**등록** 엑셀. 실제 주문 출고/송장은 hanmi-flow·epost-flow 로 별개.)
- 템플릿 1행(그룹헤더)·2행(필드명) 보존, 가이드 3~6행 삭제, 데이터는 3행부터.
- **상세설명(Y)칸 = detail.html 베어 fragment 그대로** 투입(`<p><strong><br>`).
- **원산지코드 텍스트(`@`)로 앞자리 0 보존** — **기본 캐나다 `0204006` 고정**(전 상품 캐나다로 깔고 사용자 1회 수동 보정. 자동 국가해석 안 씀), 택배사도 EPOST 기본 고정. `bulk.origin_code`/`delivery_code` 로만 덮어씀.
- **배송방법 구분자 U+201A(‚)** — `택배‚ 소포‚ 등기`(일반 콤마 아님).
- **해외사업자 제약: `건강식품>영양제` 하위는 `기타건강보조식품`(50002615) 고정** — 아미노산·비타민 등 세분류 선택 불가, fallback 아닌 정답. **단 절대규칙 아님(2026-06-23 콜라겐 예외):** `식품>다이어트식품` 하위 leaf 는 해외사업자도 직접 선택 가능 — **콜라겐=`식품>다이어트식품>콜라겐`(50007037)**(히알루론산 50007041·식이섬유 50001908 등 동 계열 가능, 등록화면 확인). 콜라겐/히알루론산류는 `건강식품>콜라겐`으로 잡아 강제하지 말고 다이어트식품 leaf 코드를 `bulk.category_code` 로 지정. (스크립트 영양제 강제는 cat 경로에 `영양제`·`건강식품` 포함 시만 발동 → 경로를 다이어트식품으로 두거나 bulk 코드 박으면 우회.)
- **🔑 관부가세(K) = 전 품목 `관부가세 포함` (2026-06-30 확정, 2026-07-05 재확인 — 식품/비식품 분기 폐기):** 핀치마트=국내발송 리셀러라 구매자 통관세 없음 → 식품·비식품(잡화·물병·가방·모자 등) 모두 `관부가세 포함`. CONFIG 기본이 `포함`이니 **`bulk.import_tax` 를 넣지 말 것**(넣으면 오버라이드). 비식품이라고 `미포함` 명시 금지 — 2026-07-05 32oz 클리어보틀에서 미포함 넣었다가 네이버 삐빅. 옛 "비식품=미포함" 문구 superseded.
- **배송비 = product_info 에서 SKU별 자동 도출 (2026-06-12, 2026-06-20 보강):** `resolve_shipping()` 이 `shipping` **또는 `shipping_policy`** dict(`per_unit_krw`/`shipping_krw_per_unit`→수량별 1개당 / `absorbed_into_price`·`naver_free:true`→무료 / dict 안 `bundle_rule` 에 `"M개당"` 있으면 우선)·`shipping_krw`/`policy` 문자열(`"M개당 N원"`→qty=M fee=N, `"개당 N원"`→qty=1, `균일/주문당/건당/수량 무관/개수 상관없이 N원`→**유료 fee=N qty=공란**, `무료/무배/흡수`→무료)을 파싱해 배송비유형·기본배송비·수량별부과수량을 채움. **유료·무료면 부과수량(AP)을 자동 공란**(수량별일 때만 AP 채움). 우선순위 **`bulk` 오버라이드 > resolve_shipping > CONFIG**. CONFIG `6개당 15,000` 은 shipping 정보 전무할 때만 쓰는 fallback — **전 SKU 에 일괄로 덮지 말 것**(이전 버그: 2026-06-20 `shipping_policy` dict 미인식으로 두 SKU 가 전부 CONFIG 로 덮임 → `from_dict()` 분기 추가로 해결). 판매가도 `calculation.sell_price_krw` 중첩 키까지 읽음.
- 스토어 기본값(shipping 부재 시 fallback): 우체국택배(EPOST)·수량별 6개당 15,000·**배송비 결제방식 `선결제`(무조건 — 착불 X, 2026-06-07 사용자 지시)**·재고 1000·신상품·과세상품·**관부가세 포함**(전 품목). **반품/교환배송비 각 50,000 · A/S 전화 `+16478010784` · A/S 안내 "수령시 파손된 제품에 한해 환불 가능합니다"**. SKU별은 product_info `bulk` 블록으로 오버라이드.
- **대표이미지(W) = 호스팅 URL 있으면 자동 입력 (2026-06-12):** 사용자가 Flickr 등에 올려 URL 주면 `bulk.rep_image`(또는 `images.rep_image_url`)에 넣어 자동 채움. URL 없을 때만 네이버 직접 업로드 수동 단계(블로커 아님). 매대 진열컷이면 깔끔한 제품컷 권장 1줄 안내하되 일단 채움. 반품/교환·A/S 는 CONFIG 로 자동.

[[feedback_naver_category_snack]] [[feedback_naver_category_toplevel_lock]] [[feedback_output_location]]

**🔑 완구/어린이제품 KC 인증 (2026-07-09 정정):** 완구=어린이제품 KC(**안전확인**) 대상. 일괄엑셀엔 KC 필드 없어 완구/유아/블록/레고/인형/키즈/출산·육아 업로드 시 자동 판매중지 → 네이버 편집서 인증정보 입력. **구매대행이면 '인증대상 아님', 직수입/사입 판매는 판매자가 KC 의무자라 리스크**(뭉뚱그리기 금지). 상세 [[feedback_kc_children_cert]]
