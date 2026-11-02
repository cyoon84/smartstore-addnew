#!/usr/bin/env python3
"""
캘거리 직접 드랍(CJ대한통운) 송장번호를 스마트스토어 출고 파일에 채워 발송처리 엑셀을 만든다.

한미·우체국과 달리 캘거리는 송장 엑셀을 받지 않고 사장님이 CJ 접수 후
`송장번호 이름` 형태로 번호만 알려준다. 그래서 송장 파일 대신 이름=번호 쌍을 인자로 받는다.

사용법:
    python3 calgary_match_invoices.py <스마트스토어_경로> <비밀번호> 최재원=595046765662 전명희=... 정미원=...

출력: ~/smartstore-project/output/발송처리/스마트스토어_발송처리_<YYYYMMDD>-캘거리CJ.xlsx

LEARNED §18-6 — 발송처리 파일은 손으로 만들지 않는다. 원본 export 를 복사해 번호만 채우면
시트명(`발주발송관리`)과 1행 안내문 때문에 네이버가 업로드를 거부한다. 이 스크립트가
시트명을 `발송처리` 로 바꾸고 1행을 지우되 2행 헤더는 병합 해제 후 복원한다.
"""
import io
import os
import sys
from datetime import datetime

import msoffcrypto
from openpyxl import load_workbook

COURIER = "CJ대한통운"  # delivery-companies 코드리스트: CJGLS


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: calgary_match_invoices.py <smartstore_path> <password> 이름=송장번호 [...]",
            file=sys.stderr,
        )
        sys.exit(1)

    smartstore_file = sys.argv[1]
    password = sys.argv[2]

    name_to_tracking = {}
    for arg in sys.argv[3:]:
        if "=" not in arg:
            print(f"ERROR: '{arg}' 는 이름=송장번호 형식이 아니다", file=sys.stderr)
            sys.exit(1)
        name, tracking = arg.split("=", 1)
        name_to_tracking[name.strip()] = tracking.strip()

    # 스마트스토어 복호화
    decrypted = io.BytesIO()
    with open(os.path.expanduser(smartstore_file), "rb") as f:
        if password:
            office_file = msoffcrypto.OfficeFile(f)
            office_file.load_key(password=password)
            office_file.decrypt(decrypted)
            decrypted.seek(0)
        else:
            decrypted = io.BytesIO(f.read())
    wb = load_workbook(decrypted)
    ws = wb.active

    # 실제 헤더는 2행
    col_index = {}
    for col in range(1, ws.max_column + 1):
        v = ws.cell(2, col).value
        if v:
            col_index[v] = col

    song_jang_col = col_index.get("송장번호")
    taekbae_col = col_index.get("택배사")
    name_col = col_index.get("수취인명")

    filled = 0
    unmatched = []
    matched_names = []
    seen_matched = set()
    used = set()
    for row in range(3, ws.max_row + 1):
        name = ws.cell(row, name_col).value
        if not name:
            continue
        nm = str(name).strip()
        tracking = name_to_tracking.get(nm)
        if tracking:
            # 송장번호는 텍스트로 넣는다(앞자리 0 보존·지수표기 방지)
            cell = ws.cell(row, song_jang_col)
            cell.value = tracking
            cell.number_format = "@"
            if taekbae_col:
                ws.cell(row, taekbae_col).value = COURIER
            filled += 1
            used.add(nm)
            if nm not in seen_matched:
                matched_names.append(nm)
                seen_matched.add(nm)
        else:
            unmatched.append(nm)

    # 1행(안내문) 삭제 + 2행 헤더 보존 (hanmi-flow 와 같은 처리)
    header_values = {c: ws.cell(2, c).value for c in range(1, ws.max_column + 1)}
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= 2:
            ws.unmerge_cells(str(rng))
    ws.delete_rows(1)
    for c, v in header_values.items():
        if v is not None:
            ws.cell(1, c).value = v
    ws.title = "발송처리"

    today = datetime.now().strftime("%Y%m%d")
    output_dir = os.path.expanduser("~/smartstore-project/output/발송처리")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir, f"스마트스토어_발송처리_{today}-캘거리CJ.xlsx"
    )
    wb.save(output_path)

    print(f"DONE:{output_path}:{filled}")
    if matched_names:
        print("RECIPIENTS:" + "|".join(matched_names))
    if unmatched:
        print("UNMATCHED:" + "|".join(sorted(set(unmatched))))
    leftover = sorted(set(name_to_tracking) - used)
    if leftover:
        print("NO_ORDER_FOR:" + "|".join(leftover))


if __name__ == "__main__":
    main()
