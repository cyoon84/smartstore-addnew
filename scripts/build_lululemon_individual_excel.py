#!/usr/bin/env python3
"""룰루레몬 에브리웨어 벨트백 나노 + 에브리웨어 백팩 나노 — 컬러별 **개별 단일상품** 일괄등록 엑셀.

기존 그룹 product_info(2종)를 소스로, 색상 옵션을 풀어 SKU(=색상)당 한 행씩 만든다.
(사용자가 네이버에서 직접 그룹으로 묶을 예정 — 업로드는 개별 단일상품으로.)

build_bulk_excel.build_data / write_excel 를 그대로 재사용한다. 각 색상 행은
정규화된 synthetic single-item pinfo 로 만들어 카테고리/배송/세금 해석을 태운다.

- 상세설명(Y) = 제품별 공통 detail.html (벨트백 공통 1장 / 백팩 공통 1장)
- 대표이미지(W) = 색상별 Flickr 호스팅 URL (사진 실물 판독으로 매핑)
- 상품명 = 단일상품이므로 각 색상명을 제목에 포함 (LEARNED_RULES §13-4)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_bulk_excel as bbe

ROOT = bbe.ROOT
NEW_ITEM = bbe.NEW_ITEM

# 두 제품의 공통값 (기존 product_info 확정): 전 색상 ₩44,300 · HST13% · 배송 수량당 ₩10,000
SELL_KRW = 44300
SHIPPING = {"per_unit_krw": 10000}        # 수량당 10,000원 (묶음 X)
BRAND_KO = "룰루레몬"

# 제품 정의: base 폴더(공통 detail.html 소스) + base 제목 + 카테고리 + 색상별 (라벨, Flickr URL)
PRODUCTS = [
    {
        "base_slug": "lululemon_everywhere_belt_bag_nano",
        "base_title": "룰루레몬 에브리웨어 벨트백 나노 미니 파우치 키링 동전지갑",
        "category": "패션잡화 > 지갑 > 동전지갑",
        "colors": [
            ("Blissful Pink", "55345459910_bd4aaedd6f_b"),   # 벨트백 나노 핑크 (골드) — 공식색명 사용자확정
            ("White",         "55345258529_9c4a6a424c_b"),   # 벨트백 나노 화이트
            ("Black",         "55345258524_2a95d4dda6_b"),   # 벨트백 나노 블랙 (실버)
        ],
    },
    {
        "base_slug": "lululemon_everywhere_backpack_nano",
        "base_title": "룰루레몬 에브리웨어 백팩 나노 미니 키링 파우치",
        "category": "패션잡화 > 여성가방 > 백팩",
        "colors": [
            ("Blissful Pink", "55344112122_920fa0346e_b"),   # 백팩 나노 핑크 (골드) — 공식색명 사용자확정(PIAR 판독 무시)
            ("Black",         "55345459915_7affa92cf8_b"),   # 백팩 나노 블랙 (실버)
        ],
    },
]

FLICKR = "https://live.staticflickr.com/65535/{}.jpg"


def main():
    lookups = (bbe.load_lookup_xls(bbe.latest("category_*.xls")),
               bbe.load_lookup_xls(bbe.latest("delivery-companies_*.xls")))

    rows, report = [], []
    for prod in PRODUCTS:
        folder = os.path.join(NEW_ITEM, prod["base_slug"])
        detail_path = os.path.join(folder, f"{prod['base_slug']}_detail.html")
        detail_html = open(detail_path, encoding="utf-8").read().strip()

        for label, img in prod["colors"]:
            title = f"{prod['base_title']} {label}"
            syn = {
                "title_ko": title,
                "sell_price_krw": SELL_KRW,
                "brand_ko": BRAND_KO,
                "category_naver": prod["category"],
                "shipping": dict(SHIPPING),
                "bulk": {"rep_image": FLICKR.format(img)},
            }
            d, warn = bbe.build_data(syn, detail_html, *lookups)
            rows.append(d)
            report.append((f"{prod['base_slug']}__{label}", d, warn))

    out = os.path.join(NEW_ITEM, "_batch", "lululemon_nano_individual_bulk_upload.xlsx")
    bbe.write_excel(rows, out)

    print(f"✅ 생성: {out}  ({len(rows)}개 색상 SKU, 데이터 {len(rows)}행)")
    for name, d, warn in report:
        print(f"\n· {name}")
        print(f"    상품명: {d.get('title')} ({len(d.get('title',''))}자)")
        print(f"    카테고리 {d.get('category_code')} · 판매가 {d.get('sale_price')} · 원산지 {d.get('origin_code')}")
        print(f"    배송 {d.get('delivery_code')}/{d.get('shipping_type')} {d.get('shipping_fee')}"
              f"{('  수량별부과 '+str(d.get('shipping_qty'))) if d.get('shipping_qty') else ''} · 결제 {d.get('shipping_pay')}")
        print(f"    대표이미지 {d.get('rep_image')}")
        print(f"    관부가세 {d.get('import_tax')} · 부가세 {d.get('tax_type')}")
        for w in warn:
            print(f"    ⚠️ {w}")


if __name__ == "__main__":
    main()
