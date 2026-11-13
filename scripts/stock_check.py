#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""재고관리 엑셀에서 상품명 부분일치로 잔여 재고를 조회한다.

왜 이 스크립트가 있는가 (LEARNED_RULES §0-∞ · memory/feedback_inventory_current_stock_formula.md):

재고관리 엑셀의 `현재고` 칸은 수식 `=J{행}-K{행}` 이다. pandas 로 읽으면 값이 아니라 수식
문자열이 나오고 `to_numeric(errors='coerce')` 에서 NaN 이 된다. 거기에 `fillna(0)` 을 붙이면
재고가 있는 로트가 전부 "0" 으로 보인다 — 2026-11-11 에 실제로 이 실수로 오스테오·수도크림·
도브 3건(₩86,850)을 "재고 0, 구매 필요"로 잘못 보고했다.

반대로 `현재고` 에 숫자가 그대로 있으면 과거 실사 때 사람이 하드코딩한 값이라 실제 잔여와
어긋날 수 있다(7행 다우니 에이프릴프레쉬 680g: 하드코딩 2 vs 실잔여 0).

그래서 이 스크립트는 **항상 `사입수량 − 판매수량`** 으로 세고, `현재고` 칸에 하드코딩 숫자가
남아 있으면 ⚠️ 로 표시한다. 재고 조회는 손으로 pandas 를 쓰지 말고 이걸 쓴다.

사용법:
    python3 scripts/stock_check.py 오스테오 수도크림 도브
    python3 scripts/stock_check.py --all            # 잔여 1 이상 전부
"""
import glob
import os
import sys

from openpyxl import load_workbook

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV_GLOB = os.path.join(REPO, 'output', 'inventory', '재고관리_*.xlsx')

COL_DATE = '사입일'
COL_NAME = '상품명'
COL_VENDOR = '매입처'
COL_UNIT = '사입단가(₩)'
COL_BUY = '사입수량'
COL_SOLD = '판매수량'
COL_CUR = '현재고'
COL_MEMO = '메모'


def latest_inventory():
    paths = [p for p in glob.glob(INV_GLOB) if not os.path.basename(p).startswith('~$')]
    if not paths:
        sys.exit('재고관리 엑셀을 찾지 못했습니다: %s' % INV_GLOB)
    return sorted(paths)[-1]


def num(v):
    if v is None or v == '':
        return 0.0
    if isinstance(v, str):
        if v.startswith('='):      # 수식 — 값이 아니다
            return None
        v = v.replace(',', '').strip()
        if not v:
            return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def rows(path):
    ws = load_workbook(path, data_only=False).active
    hdr = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(hdr) if h}
    out = []
    for r in range(2, ws.max_row + 1):
        vals = [c.value for c in ws[r]]
        if not vals or not vals[idx.get(COL_NAME, 1)]:
            continue
        get = lambda k: vals[idx[k]] if k in idx and idx[k] < len(vals) else None
        buy, sold = num(get(COL_BUY)) or 0.0, num(get(COL_SOLD)) or 0.0
        raw_cur = get(COL_CUR)
        out.append({
            'row': r,
            'date': str(get(COL_DATE))[:10],
            'name': str(get(COL_NAME)),
            'vendor': str(get(COL_VENDOR) or ''),
            'unit': get(COL_UNIT),
            'buy': buy,
            'sold': sold,
            'left': buy - sold,                                   # 🔑 유일한 진실
            'hardcoded': not (isinstance(raw_cur, str) and str(raw_cur).startswith('=')),
            'raw_cur': raw_cur,
            'memo': str(get(COL_MEMO) or ''),
        })
    return out


def show(rec):
    flag = ''
    if rec['hardcoded']:
        hc = num(rec['raw_cur'])
        if hc is not None and hc != rec['left']:
            flag = '  ⚠️ 현재고 칸 하드코딩 %g ≠ 실잔여 %g — 수식(=J%d-K%d)으로 복원 필요' % (
                hc, rec['left'], rec['row'], rec['row'])
    unit = '₩%s' % format(int(rec['unit']), ',') if num(rec['unit']) else '단가미기재'
    print('  %3d행 %s | %s' % (rec['row'], rec['date'], rec['name'][:52]))
    print('        매입처 %s · %s · 사입 %g − 판매 %g = **잔여 %g**%s' % (
        rec['vendor'][:28] or '-', unit, rec['buy'], rec['sold'], rec['left'], flag))
    if rec['memo']:
        print('        메모 … %s' % rec['memo'][-170:].replace('\n', ' '))


def main():
    args = [a for a in sys.argv[1:] if a != '--all']
    show_all = '--all' in sys.argv[1:]
    if not args and not show_all:
        sys.exit(__doc__)

    path = latest_inventory()
    print('재고 파일: %s' % os.path.relpath(path, REPO))
    print('🔑 잔여 = 사입수량 − 판매수량 (현재고 칸은 수식이라 믿지 않는다)\n')
    data = rows(path)

    if show_all:
        hits = [r for r in data if r['left'] > 0]
        print('=== 잔여 1 이상 %d건 ===' % len(hits))
        for r in sorted(hits, key=lambda x: -x['left']):
            show(r)
        return

    for kw in args:
        hits = [r for r in data if kw in r['name']]
        print('=== "%s" — %d건 ===' % (kw, len(hits)))
        if not hits:
            print('  재고 행 없음 → 장부 `물건산거 (COGS)` 탭도 상품명으로 grep 할 것 (§0-∞)')
        for r in hits:
            show(r)
        live = sum(r['left'] for r in hits)
        print('  → 합계 잔여 %g%s\n' % (live, '' if live else '  (구매 대상)'))


if __name__ == '__main__':
    main()
