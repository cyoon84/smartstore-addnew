#!/usr/bin/env python3
"""제품 산출물(product_info.json + detail.html)을 네이버 스마트스토어 **일괄등록 엑셀** 한 줄로 변환한다.

가격계산·저장처럼 메인 오케스트레이터가 소유하는 결정론적 변환 단계.
listing-writer 가 만든 콘텐츠(상품명·detail.html) + 확정 가격을 받아 템플릿 칸에 매핑한다.

- 템플릿:        guide/일괄등록 guide/ExcelSaveTemplate_*.xlsx  (가장 최근 파일)
- 카테고리코드:  guide/일괄등록 guide/category_*.xls            (카테고리 경로 → 코드 자동 해석)
- 원산지코드:    기본 캐나다(0204006) 고정 — 전 상품 캐나다로 깔고 사용자가 수동 보정. bulk.origin_code 로만 덮어씀.
- 택배사코드:    guide/일괄등록 guide/delivery-companies_*.xls  (코드 검증)

데이터 출처(우선순위): product_info.json 의 `bulk` 오버라이드 → product_info 본문 파생값 → CONFIG 기본값.
스토어 기본값(CONFIG)은 사용자 학습 예제(웨버네추럴스 L라이신) 기준:
  우체국택배(EPOST) · 수량별 6개당 15,000 · 재고 1000 · 신상품 · 과세상품 · 관부가세 미포함.

사용:
  python3 scripts/build_bulk_excel.py <slug 또는 제품폴더경로>
  python3 scripts/build_bulk_excel.py webber_naturals_l_lysine_1000mg_140
  python3 scripts/build_bulk_excel.py --out /tmp/foo.xlsx output/new-item/<slug>

product_info.json 에 스토어 코드를 직접 박고 싶으면 `"bulk": {...}` 블록을 추가:
  "bulk": {
    "category_code": 50002615,      # 생략 시 category_proposed/fallback 경로로 자동 해석
    "origin_code": "0204006",       # 생략 시 origin.* 국가명으로 자동 해석
    "delivery_code": "EPOST",
    "shipping_type": "수량별", "shipping_fee": 15000, "shipping_qty": 6,
    "stock": 1000, "sale_price": 15800,
    "rep_image": "https://.../main.jpg",        # 대표이미지(필수) — 있으면 채움
    "return_fee": 5000, "exchange_fee": 5000    # 반품/교환배송비(조건부필수)
  }
"""
import argparse, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE_DIR = os.path.join(ROOT, "guide", "일괄등록 guide")
NEW_ITEM = os.path.join(ROOT, "output", "new-item")

# 배송방법 칸 구분자는 일반 콤마가 아니라 U+201A(‚) — 템플릿 원본과 동일해야 함
SHIP_METHOD = "택배‚ 소포‚ 등기"

# 해외사업자 제약: 영양제류는 카테고리 선택이 '기타건강보조식품'만 가능(아미노산 등 세분류 못 고름).
# product_info 가 영양제 세분류(아미노산 등)를 제안해도 이 코드로 강제 + 경고 안 띄움.
SUPPLEMENT_FORCED_CODE = 50002615   # 식품 > 건강식품 > 영양제 > 기타건강보조식품

# 스토어 기본값 (사용자 학습 예제 기준; bulk 오버라이드/product_info 파생값이 우선)
CONFIG = {
    "product_state": "신상품",
    "tax_type": "과세상품",            # 부가세
    "import_tax": "관부가세 미포함",     # 관부가세
    "unit_price_use": "N",            # 단위가격 사용여부
    "stock": 1000,
    "delivery_code": "EPOST",         # 우체국택배 (기본 — 사용자가 필요시 수동 변경)
    "origin_code": "0204006",         # 캐나다 (기본 — 전 상품 캐나다로 깔고 수동 보정)
    "shipping_type": "수량별",
    "shipping_fee": 15000,
    "shipping_qty": 6,                # 수량별부과-수량
    "shipping_pay": "선결제",          # 무조건 선결제 (사용자 지시 2026-06-07)
    "multi_origin": "N",
    # A/S·반품/교환 스토어 공통값 (항상 추가)
    "return_fee": 50000,
    "exchange_fee": 50000,
    "as_phone": "+16478010784",
    "as_guide": "수령시 파손된 제품에 한해 환불 가능합니다",
}

# 네이버 필드명(2행) → 데이터 dict 키. 컬럼 인덱스는 템플릿 2행에서 동적으로 찾는다.
FIELD = {
    "category_code": "카테고리코드",
    "title":        "상품명",
    "product_state":"상품상태",
    "sale_price":   "판매가",
    "unit_price_use":"단위가격 사용여부",
    "tax_type":     "부가세",
    "import_tax":   "관부가세",
    "stock":        "재고수량",
    "rep_image":    "대표이미지",
    "detail":       "상세설명",
    "brand":        "브랜드",
    "maker":        "제조사",
    "origin_code":  "원산지코드",
    "importer":     "수입사",
    "multi_origin": "복수원산지여부",
    "ship_method":  "배송방법",
    "delivery_code":"택배사코드",
    "shipping_type":"배송비유형",
    "shipping_fee": "기본배송비",
    "shipping_pay": "배송비 결제방식",
    "shipping_qty": "수량별부과-수량",
    "return_fee":   "반품배송비",
    "exchange_fee": "교환배송비",
    "as_phone":     "A/S 전화번호",
    "as_guide":     "A/S 안내",
}


def latest(pattern):
    files = sorted(glob.glob(os.path.join(GUIDE_DIR, pattern)))
    if not files:
        sys.exit(f"[!] 파일 없음: {pattern} (in {GUIDE_DIR})")
    return files[-1]


def load_lookup_xls(path):
    import xlrd
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    return [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]


def category_candidates(pinfo):
    """product_info 스키마 변형(register·source-launch 여러 버전)에서 카테고리 경로 후보를 모은다.
    키 이름이 제각각(category_proposed·naver_category·category_naver·category_naver_confirmed…)이라
    '>' 가 든 경로형 문자열만 우선순위로 수집. note/flag 류(프로즈)는 제외."""
    PRIORITY = ["category_naver_confirmed", "category_naver_corrected", "category_proposed",
                "naver_category", "category_naver", "category_naver_alt", "category", "category_fallback"]
    seen = []

    def add(v):
        if isinstance(v, str) and ">" in v and v.strip() not in seen:
            seen.append(v.strip())

    for k in PRIORITY:
        add(pinfo.get(k))
    for k, v in pinfo.items():                    # 그 외 categor* 키(노트/플래그 제외)도 훑기
        kl = k.lower()
        if "categor" in kl and "note" not in kl and "flag" not in kl:
            add(v)
    return seen


def resolve_category(rows, *paths):
    """'식품 > 건강식품 > 영양제 > 아미노산' 경로 → 코드. 여러 경로를 순서대로 시도."""
    by_leaf = {}   # 세분류 leaf -> (code, full)
    by_full = {}
    for r in rows[1:]:
        code = str(r[0]).split(".")[0]
        chain = [str(x).strip() for x in r[1:] if str(x).strip()]
        if not chain:
            continue
        full = " > ".join(chain)
        by_full[full] = code
        by_leaf.setdefault(chain[-1], (code, full))
    for i, p in enumerate(paths):
        if not p:
            continue
        if p.strip() in by_full:
            return by_full[p.strip()], p.strip(), (i > 0)   # 정확 매칭 (i>0 이면 fallback)
    # leaf 만 매칭 (경로 일부 다를 때)
    for i, p in enumerate(paths):
        if not p:
            continue
        leaf = p.strip().split(">")[-1].strip()
        if leaf in by_leaf:
            code, full = by_leaf[leaf]
            return code, full, (i > 0)          # i>0 이면 fallback 사용
    return None, None, False


def build_data(pinfo, detail_html, cat_rows, deliv_rows):
    bulk = pinfo.get("bulk", {})
    warn = []

    def pick(key, *fallbacks):
        if key in bulk and bulk[key] not in (None, ""):
            return bulk[key]
        for fb in fallbacks:
            if fb not in (None, ""):
                return fb
        return CONFIG.get(key)

    pricing = pinfo.get("pricing") or {}
    if not isinstance(pricing, dict):
        pricing = {}

    # register 스키마(product_name_ko·sell_price_krw·brand_ko)와
    # source-launch 스키마(title_ko·sell_krw·brand) 둘 다 읽는다.
    brand_ko = pinfo.get("brand_ko") or pinfo.get("brand")
    d = {}
    d["title"] = pick("title", pinfo.get("product_name_ko"), pinfo.get("title_ko"))
    # 판매가: pricing dict 내부 또는 최상위 키(스키마 변형: sell_price_krw·selling_price_krw·sell_krw) 모두 탐색
    d["sale_price"] = pick("sale_price",
                           pricing.get("sell_price_krw"), pricing.get("sell_krw"),
                           pinfo.get("sell_price_krw"), pinfo.get("selling_price_krw"), pinfo.get("sell_krw"))
    d["brand"] = pick("brand", brand_ko)
    d["maker"] = pick("maker", brand_ko)
    d["importer"] = pick("importer", brand_ko)
    d["product_state"] = pick("product_state")
    d["tax_type"] = pick("tax_type")
    d["import_tax"] = pick("import_tax")
    d["unit_price_use"] = pick("unit_price_use")
    d["stock"] = pick("stock")
    d["multi_origin"] = pick("multi_origin")
    d["ship_method"] = SHIP_METHOD
    d["delivery_code"] = pick("delivery_code")
    d["shipping_type"] = pick("shipping_type")
    d["shipping_fee"] = pick("shipping_fee")
    d["shipping_pay"] = pick("shipping_pay")
    d["shipping_qty"] = pick("shipping_qty")
    d["detail"] = detail_html
    d["rep_image"] = pick("rep_image")           # 보통 비어있음 → 사용자가 네이버에서 직접 업로드
    d["return_fee"] = pick("return_fee")         # 스토어 공통 50000
    d["exchange_fee"] = pick("exchange_fee")     # 스토어 공통 50000
    d["as_phone"] = pick("as_phone")             # A/S 전화번호 (스토어 공통)
    d["as_guide"] = pick("as_guide")             # A/S 안내 (스토어 공통)

    # 카테고리코드 — bulk 우선 / 영양제는 해외사업자 제약상 기타건강보조식품 강제 / 그 외 경로 자동해석
    cat_candidates = category_candidates(pinfo)   # 스키마 변형 전반에서 경로 수집
    cat_paths = " ".join(cat_candidates)
    if bulk.get("category_code"):
        d["category_code"] = bulk["category_code"]
    elif "영양제" in cat_paths or "건강식품" in cat_paths:
        d["category_code"] = SUPPLEMENT_FORCED_CODE          # 기타건강보조식품 (해외사업자 제약상 유일 선택)
        warn.append("카테고리: 영양제 → 기타건강보조식품(50002615) 적용 [해외사업자 제약]. "
                    "더 맞는 카테고리 가능하면 등록화면에서 수동 변경")
    else:
        code, full, used_fb = resolve_category(cat_rows, *cat_candidates)
        if code:
            d["category_code"] = int(code) if str(code).isdigit() else code
            if used_fb:
                warn.append(f"카테고리: 1순위 경로 미발견 → fallback '{full}'({code}) 사용. 등록화면 확인")
        else:
            warn.append("카테고리코드 자동해석 실패 — bulk.category_code 직접 지정 필요")

    # 원산지코드 — bulk 우선, 없으면 캐나다(0204006) 기본 고정 (전 상품 캐나다로 깔고 사용자 수동 보정)
    # (앞자리 0 보존 위해 문자열. 국가명 자동해석은 안 씀 — 사용자 지시로 캐나다 기본.)
    d["origin_code"] = str(bulk.get("origin_code") or CONFIG["origin_code"])

    # 택배사코드 검증
    valid_deliv = {str(r[0]) for r in deliv_rows[1:]}
    if d["delivery_code"] not in valid_deliv:
        warn.append(f"택배사코드 '{d['delivery_code']}' 가 코드 리스트에 없음 — 확인 필요")

    # 필수값 누락 경고 (구버전/미완성 product_info 방어)
    if not d.get("title"):
        warn.append("상품명(product_name_ko) 없음 — product_info 확인")
    if not d.get("sale_price"):
        warn.append("판매가(pricing.sell_price_krw) 없음 — product_info 확인")

    return d, warn


def write_excel(rows, out_path):
    """rows = 데이터 dict 의 리스트. 한 시트에 여러 SKU 를 3행부터 나열한다."""
    import openpyxl
    tpl = latest("ExcelSaveTemplate_*.xlsx")
    wb = openpyxl.load_workbook(tpl)
    ws = wb.worksheets[0]

    # 2행 필드명 → 컬럼 인덱스 매핑 (개행 제거 후 매칭)
    name2col = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=2, column=c).value
        if v:
            name2col[str(v).replace("\n", "").strip()] = c

    # 가이드 행(3~6) 삭제 → 데이터는 3행부터
    ws.delete_rows(3, 4)

    for i, d in enumerate(rows):
        r = 3 + i
        for key, val in d.items():
            if val in (None, ""):
                continue
            field = FIELD.get(key)
            col = name2col.get(field.replace("\n", "").strip()) if field else None
            if not col:
                continue
            ws.cell(row=r, column=col, value=val)
            if key == "origin_code":             # 앞자리 0 보존
                ws.cell(row=r, column=col).number_format = "@"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wb.save(out_path)
    return out_path


def find_folder(arg):
    if os.path.isdir(arg):
        return arg
    cand = os.path.join(NEW_ITEM, arg)
    if os.path.isdir(cand):
        return cand
    sys.exit(f"[!] 제품 폴더를 찾을 수 없음: {arg}")


def one_row(target, lookups):
    """제품 폴더 1개 → (slug, 데이터dict, 경고). source-launch 배치/단건 공통."""
    folder = find_folder(target)
    slug = os.path.basename(os.path.normpath(folder))
    pinfo_path = os.path.join(folder, f"{slug}_product_info.json")
    detail_path = os.path.join(folder, f"{slug}_detail.html")
    if not os.path.exists(pinfo_path):
        sys.exit(f"[!] product_info 없음: {pinfo_path}")
    if not os.path.exists(detail_path):
        sys.exit(f"[!] detail.html 없음: {detail_path}")
    pinfo = json.load(open(pinfo_path, encoding="utf-8"))
    detail_html = open(detail_path, encoding="utf-8").read().strip()
    d, warn = build_data(pinfo, detail_html, *lookups)
    return slug, folder, d, warn


def main():
    ap = argparse.ArgumentParser(description="제품 산출물 → 네이버 일괄등록 엑셀 (단건/배치)")
    ap.add_argument("targets", nargs="+",
                    help="slug 또는 제품 폴더 경로. 여러 개 주면 한 엑셀에 다 담음(source-launch 배치)")
    ap.add_argument("--out", help="출력 xlsx 경로. 배치(2개+)면 기본 output/new-item/_batch/bulk_upload_<날짜>.xlsx")
    args = ap.parse_args()

    lookups = (load_lookup_xls(latest("category_*.xls")),
               load_lookup_xls(latest("delivery-companies_*.xls")))

    results = [one_row(t, lookups) for t in args.targets]
    batch = len(results) > 1

    if batch:
        if args.out:
            out = args.out
        else:
            from datetime import date
            out = os.path.join(NEW_ITEM, "_batch", f"bulk_upload_{date.today().isoformat()}.xlsx")
    else:
        out = args.out or os.path.join(results[0][1], f"{results[0][0]}_bulk_upload.xlsx")

    write_excel([r[2] for r in results], out)

    print(f"✅ 생성: {out}  ({len(results)}개 SKU, 데이터 {len(results)}행)")
    for slug, _folder, d, warn in results:
        print(f"\n· {slug}")
        print(f"    상품명: {d.get('title')}")
        print(f"    카테고리 {d.get('category_code')} · 판매가 {d.get('sale_price')} · 원산지 {d.get('origin_code')} · "
              f"배송 {d.get('delivery_code')}/{d.get('shipping_type')} {d.get('shipping_fee')}")
        for w in warn:
            print(f"    ⚠️ {w}")
    print("\n📌 사용자 직접 처리: 대표이미지(W) — 네이버에서 직접 업로드 "
          "(반품/교환배송비·A/S 는 자동 채움)")


if __name__ == "__main__":
    main()
