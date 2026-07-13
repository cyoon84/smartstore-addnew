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

**의류(티셔츠 등) 확장 — 첫 케이스 2026-07-13 메탈 벤트 테크 반팔 셔츠 Cherry Ember:**
- **파이널세일 의류 = 캐나다 세일가를 cost 로(§12-1).** cost=$54(FINAL SALE, 정가 $78), HST 13%(성인 의류). `pricing_mode:"final_sale_target_krw"`.
- **🔑 한국 공홈(lululemon.co.kr)에서 파는 제품이면 §0-A 앵커가 공홈가.** 공홈 정가 ₩93,000 **무료배송+무료반품**이 경쟁 기준. 단 **우리 색상(Cherry Ember)이 공홈 미취급이면 "직수입 전용색" 차별점**(공홈 색상 리스트를 ProductGroup JSON-LD 로 확인 — 겹치는지). 사용자 원칙 **"어쨌든 한국보다 싸야 산다"** → 배송포함가가 공홈가보다 낮게(예 상품가 ₩79,000+배송 ₩10,000=₩89,000 < ₩93,000). §0-D 로 상품가는 낮게(검색 lprice 정렬), 배송에 일부.
- **선택 색상 데이터 추출:** URL `?color=<코드>` 의 색상은 ProductGroup JSON-LD 에 없을 수 있음(전 색상 OOS 로 뜨기도). **`#__NEXT_DATA__` 를 walk 해서 `o.color.code===<코드>` 인 SKU 들의 `size/available/price{listPrice,salePrice,onSale}` 를 뽑는다**(사이즈별 재고+세일가 정확). `colorDriver` 에 `{color, sizes:[재고사이즈]}` 도 있음.
- **단일제품 + 사이즈 옵션:** 재고 있는 사이즈만 옵션(M·L·XL, 품절 XS/S/XXL 제외). product_info `options:[{option_label:"M"}...]` + `option_name:"사이즈"` → build_bulk_excel 조합형 1행(옵션값=M,L,XL). 카테고리 **패션의류>남성의류>티셔츠 50000830**(여성 50000803).
- **🔑 모델명 = 공식 JSON-LD name 그대로, URL 의 버전 접미(`3-MD`·"3.0") 붙이지 말 것** — 공식명에 없으면 근거없음(사용자 지적). `Metal Vent Tech Short-Sleeve Shirt Cherry Ember`.
- **🔑 사이즈 가이드(바디 사이즈)를 상세에 넣는다:** lululemon.co.kr PDP 의 **"사이즈 가이드" 버튼 클릭 → "바디 사이즈" 표**(한국사이즈/US/가슴둘레cm). 우리 판매 사이즈만 발췌(M 가슴둘레 99cm·L 106.5cm·XL 114cm). detail.html 에 styled 표(text rows, §18 table 대신). **"◯◯ 외 사이즈는 한국 공홈 확인" 류 문구 금지** — 그 색상이 한국에 있는 걸로 오해(사용자 지적).
- **배송비 파싱 주의:** `resolve_shipping` 은 pinfo **top-level** `shipping` 문자열을 읽음 → 개당 배송은 top-level `"shipping":"개당 10000원"` 넣어야 반영(bulk 안에만 넣으면 CONFIG 15,000 으로 덮임).
- **재고 모니터 — 파이널세일은 매일(월간 아님):** scheduled-task(`0 9 * * *`) 실브라우저로 `#__NEXT_DATA__` 색상코드 SKU 재고 확인 → Slack #new-item. 첫 실행 "Run now" 로 브라우저·Slack 권한 승인 필요(§22). **정가(재고품) 라인은 재고 모니터 불필요**(재입고 정상).

**정가(비세일) 다색 라인 — 2026-07-13 메탈 벤트 테크 정가 prod11710027(9색):**
- **🔑 "한국 공홈 미취급 색상"으로 표기, "캐나다 전용" 금지(§9):** 우리가 확인한 건 "한국 공홈 라인업에 없음"뿐. **미국 등 타 지역 취급 가능성 → "캐나다 전용/캐나다에만"은 근거없음**(사용자 지적 2026-07-13). 카피·필드 전부 "한국 공홈에 없는 색상"·"한국 미출시 색상"으로. 공홈 색상 리스트(ProductGroup JSON-LD `hasVariant` color)와 캐나다 색상 대조해 미취급색 식별.
- **정가색 가격:** cost=정가 $78(비세일)+HST13%=$88.14≈₩93,000(마진0). **한국 공홈 ₩93,000 무료배송이라 정가색은 우리가 더 싸게 못 함.** → "한국 공홈에 없는 색상 찾는 타깃"용으로 프리미엄 감수(마진 $8→₩108,600). 네이버 직구 셀러 프리미엄 밴드(₩106,000~174,000, Fetching·디어쇼퍼) 내면 합리적. (파이널세일색은 싸게, 정가색은 미취급색 프리미엄 — 두 전략 공존.)
- **🔑 배송비 "제한 없이 flat ₩10,000" = 유료(균일), 수량 무관:** 사용자가 "그냥 10000원에 제한 없이" 하면 **수량별(AP=1) 아니라 유료(AP 공란)**([[feedback_shipping_per_unit_no_bundle]]). product_info top-level `"shipping":"10000원 균일 (수량 무관)"` + `bulk.shipping_type:"유료"` → resolve_shipping 이 유료·AP공란. (룰루 relist 기본 배송을 flat ₩10,000 으로 통일.)
- **🔑 다색×사이즈 최종 = 단일제품 + `색상/사이즈` 결합 조합형(전 옵션 커버), 기준가 = 최저옵션 + 나머지 옵션가 (사용자 최종확정 2026-07-13):** 그룹상품/색상별 개별상품을 다 시도한 뒤 **그룹은 색상×사이즈 조합이 상품페이지를 도배**해서(너무 난잡) 폐기. **한 제품에 전 색상·사이즈를 결합 옵션(`색상 / 사이즈`)으로** 넣는다. 파이널세일색(Cherry Ember)을 **대표이미지·1번옵션·기준가(₩79,000)**로 두고, **나머지 색상은 옵션가 +₩29,600(=정가색 ₩108,600)**. → `build_bulk_excel` 에 옵션별 옵션가 지원 추가(`options[].option_add` 읽어 옵션가 칸 채움, 없으면 0). product_info `options:[{option_label:"체리엠버 / M","option_add":0}, {"option_label":"오션웨이브 / XS","option_add":29600}...]`, 판매가=기준가. 색상별 재고 사이즈 다르면 그 조합만(2축 full-grid 금지 §9). 상세는 통합 1장(색상 라인업 이미지, 대표색 §17). 폴더 `lululemon_metal_vent_tech_ss_all` 1개.
  - **🔑 옵션은 결합 단일축(`"체리엠버 / M"`)이 아니라 네이버 진짜 2축 조합형으로:** 네이버 일괄엑셀 템플릿 예시(ExcelSaveTemplate r4) = **옵션명 `컬러⏎사이즈`(줄바꿈 구분, 최대 3축), 옵션값 `빨강,노랑⏎S,M,L`(축은 줄바꿈, 값은 콤마), 옵션가 `0,100`·옵션재고 `10,20` = "첫번째 옵션값(1축) 기준" 콤마 리스트**(1축 각 값에 조합되는 전체에 동일 적용). → `build_bulk_excel` 에 `option_axes` 모드 추가: `{"names":["컬러","사이즈"],"values":[[색상…],[XS..XXL]],"axis1_price":[0,29600,…],"axis1_stock":[1000,…]}`. **색상별 옵션가가 1축 기준으로 정확히 들어감**(체리엠버 0=기준가, 나머지 +29600). 옵션가 범위: 판매가 1만↑ = ±50% (79,000의 +29,600=+37.5% OK), 최소 1개는 0.
  - **2축 full-grid 한계 = 색상별 재고 사이즈 차이:** 사이즈축이 공유라 체리엠버·핑크플레어의 XS·S·XXL(6조합)이 available 로 생성됨 → **등록화면에서 그 조합만 삭제/재고0**(product_info `invalid_combos_remove_in_editor` 에 기록). bulk 로는 1축(색상) 단위 재고만 → 사이즈별 제외는 수동.
  - 진행 이력(참고): 색상별 개별상품(→그룹 병합)·결합 단일축도 시도했으나 그룹 옵션 도배 + 결합축 UX 로 **단일제품 + 진짜 2축(컬러×사이즈) + 1축 옵션가**로 최종 확정. **룰루 다색 의류 기본 = 이 포맷.** [[feedback_bulk_upload_excel]]
- **이미지 색상별 CDN 스템 = styleColorId 의 `_`형(패딩 6자리, 단 4자리 코드는 무패딩):** 블랙 4780 → `LM3FT0S_4780`(무패딩, `_004780`은 0kb 빈파일), 화이트 → `LM3FT0S_012826`(6자리). fetch 로 kb>8 확인 후 채택.

관련: [[feedback_model_name_from_store]] · [[feedback_naver_category_snack]](카테고리 지어내기 금지) · [[feedback_detail_styled_deco_template]] · [[feedback_pre_sale_regular_price]](§12-1 파이널세일) · [[feedback_costco_stock_check]](재고 모니터 패턴)
