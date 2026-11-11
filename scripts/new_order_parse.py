#!/usr/bin/env python3
"""스마트스토어 발주/발송관리 엑셀(비번 1111) → 수취인별 JSON (상품주문번호 포함).

사용법: python3 scripts/new_order_parse.py <엑셀경로> [비밀번호=1111]
출력(JSON 한 줄):
{"rows": N, "recipients": [{"name":..., "items":[{"order_item_no","product_id","kor_name","option","qty"}]}]}
- 헤더 2행, 데이터 3행~ (비번 걸린 파일은 msoffcrypto 복호화).
- 상품명·옵션은 원문 그대로. 같은 (수취인, 상품주문번호)는 한 줄.
- 같은 (수취인, 상품번호, 옵션)이 서로 다른 상품주문번호로 여러 줄이면 각각 별도 항목 유지 (dedup 은 상품주문번호 기준).
"""
import io
import json
import sys
from collections import OrderedDict

import msoffcrypto
from openpyxl import load_workbook


def main():
    path = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else "1111"
    buf = io.BytesIO()
    with open(path, "rb") as f:
        try:
            of = msoffcrypto.OfficeFile(f)
            of.load_key(password=password)
            of.decrypt(buf)
            buf.seek(0)
        except Exception:
            f.seek(0)
            buf = io.BytesIO(f.read())
    ws = load_workbook(buf).active
    ci = {ws.cell(2, c).value: c for c in range(1, ws.max_column + 1) if ws.cell(2, c).value}

    def get(r, k):
        return ws.cell(r, ci[k]).value if k in ci else None

    rec = OrderedDict()
    n = 0
    for r in range(3, ws.max_row + 1):
        name = get(r, "수취인명") or get(r, "구매자명")
        if not name:
            continue
        n += 1
        name = str(name).strip()
        item = {
            "order_item_no": str(get(r, "상품주문번호") or ""),
            "product_id": str(get(r, "상품번호") or ""),
            "kor_name": str(get(r, "상품명") or "").strip(),
            "option": str(get(r, "옵션정보") or "").strip(),
            "qty": int(get(r, "수량") or 0),
        }
        rec.setdefault(name, OrderedDict())[item["order_item_no"] or len(rec[name])] = item
    out = {
        "rows": n,
        "recipients": [{"name": k, "items": list(v.values())} for k, v in rec.items()],
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
