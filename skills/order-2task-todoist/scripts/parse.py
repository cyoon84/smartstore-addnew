#!/usr/bin/env python3
"""
order-2task-todoist / parse.py

스마트스토어 출고 엑셀을 읽어 두 가지 관점으로 묶은 JSON을 표준출력에 뿌린다.
호출 Claude는 이 JSON을 받아 사용자에게 미리보기 후 Todoist MCP로 태스크를 만든다.

  1) shopping   = 상품(상품번호+옵션) 기준으로 전 주문 수량을 합산한 "사야할 제품들" 리스트
  2) recipients = 수취인명 기준으로 묶은 주문 (수취인 → 그 사람 품목들)

상품명은 한글(상품명 컬럼) 그대로 쓴다. 영문 변환/학습 사전 없음.

사용:
  python3 parse.py <엑셀경로> <비밀번호 (없으면 "")>

출력 (stdout, 1 line):
  {
    "shopping": [ {"product_id","option","kor_name","qty"} , ...],
    "recipients": [ {"name","items":[{"product_id","option","kor_name","qty"}]}, ...],
    "buyer_count": N,
    "shopping_line_count": M
  }
"""

import sys
import os
import json
import io

try:
    import msoffcrypto
    import pandas as pd
except ImportError as e:
    print(json.dumps({"error": f"dependency missing: {e}"}))
    sys.exit(1)


def decrypt_xlsx(path, password):
    """비번이 있으면 복호화. 암호화 안 된 파일이면 비번 무시하고 raw 사용."""
    with open(path, "rb") as f:
        if password:
            office = msoffcrypto.OfficeFile(f)
            try:
                office.load_key(password=password)
                buf = io.BytesIO()
                office.decrypt(buf)
                buf.seek(0)
                return buf
            except Exception:
                f.seek(0)
                return io.BytesIO(f.read())
        return io.BytesIO(f.read())


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: parse.py <xlsx_path> [password]"}))
        sys.exit(1)
    src = sys.argv[1]
    pwd = sys.argv[2] if len(sys.argv) > 2 else ""

    if not os.path.exists(src):
        print(json.dumps({"error": f"file not found: {src}"}))
        sys.exit(1)

    buf = decrypt_xlsx(src, pwd)

    # 스마트스토어 발주발송관리 시트는 첫 행이 안내문, 두 번째 행이 컬럼 헤더.
    try:
        df = pd.read_excel(buf, sheet_name="발주발송관리", header=1)
    except Exception:
        buf.seek(0)
        df = pd.read_excel(buf, header=1)

    required = ["구매자명", "수취인명", "상품번호", "상품명", "옵션정보", "수량", "주문번호"]
    for col in required:
        if col not in df.columns:
            print(json.dumps({"error": f"missing column: {col}", "available": list(df.columns)}))
            sys.exit(1)

    # --- 수취인별 묶기 (원본 행 순서 보존) ---
    # 같은 (수취인, 상품번호, 옵션, 주문번호) 조합은 수량 합산.
    rec_order = []
    rec_idx = {}
    rec_combo = {}  # (recipient, pid, opt, ord_no) -> item dict

    # --- 상품별 합산 (사야할 제품들) ---
    # 같은 (상품번호, 옵션) 은 전 주문에 걸쳐 수량 합산.
    shop_order = []
    shop_idx = {}  # (pid, opt) -> item dict

    for _, row in df.iterrows():
        recipient = str(row["수취인명"]).strip() or str(row["구매자명"]).strip()
        pid = str(row["상품번호"]).strip()
        opt = "" if pd.isna(row["옵션정보"]) else str(row["옵션정보"]).strip()
        kor_name = str(row["상품명"]).strip()
        qty = int(row["수량"]) if not pd.isna(row["수량"]) else 0
        ord_no = str(row["주문번호"]).strip()

        # 수취인별
        if recipient not in rec_idx:
            rec_idx[recipient] = {"name": recipient, "items": []}
            rec_order.append(recipient)
        rkey = (recipient, pid, opt, ord_no)
        if rkey in rec_combo:
            rec_combo[rkey]["qty"] += qty
        else:
            item = {"product_id": pid, "option": opt, "kor_name": kor_name, "qty": qty}
            rec_combo[rkey] = item
            rec_idx[recipient]["items"].append(item)

        # 상품 합산
        skey = (pid, opt)
        if skey in shop_idx:
            shop_idx[skey]["qty"] += qty
        else:
            sitem = {"product_id": pid, "option": opt, "kor_name": kor_name, "qty": qty}
            shop_idx[skey] = sitem
            shop_order.append(skey)

    shopping = [shop_idx[k] for k in shop_order]
    recipients = [rec_idx[r] for r in rec_order]

    print(json.dumps({
        "shopping": shopping,
        "recipients": recipients,
        "buyer_count": len(recipients),
        "shopping_line_count": len(shopping),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
