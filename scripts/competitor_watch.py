#!/usr/bin/env python3
"""경쟁업체 가격 모니터링 워치리스트 관리.

워치리스트(guide/competitor_watch.json)는 scheduled-task 'competitor-price-monitor'가
매주 읽어서 네이버쇼핑 search_shop 으로 경쟁사 가격을 훑는다.
이 스크립트는 그 워치리스트를 사람이 손으로 안 고쳐도 되게 관리만 한다.

사용법:
    python3 scripts/competitor_watch.py --list
    python3 scripts/competitor_watch.py --add 13639846946 --query "팀홀튼 K컵 80개입"
    python3 scripts/competitor_watch.py --add 13639846946            # 검색어 자동 추정
    python3 scripts/competitor_watch.py --remove 13639846946

핵심 규칙 (§0-D · 2026-07-23 학습):
    경쟁사 가격은 반드시 **도착가(상품가 + 배송비)** 로 비교한다.
    네이버쇼핑 lprice 는 상품가라 배송비가 빠져 있어 그대로 비교하면 오판한다.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATCHLIST = os.path.join(ROOT, "guide", "competitor_watch.json")


def load_watchlist():
    with open(WATCHLIST, encoding="utf-8") as f:
        return json.load(f)


def save_watchlist(data):
    with open(WATCHLIST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def latest_product_csv():
    files = sorted(glob.glob(os.path.join(ROOT, "guide", "Product_*.csv")))
    if not files:
        sys.exit("guide/Product_*.csv 없음 — 스마트스토어에서 상품 리스트를 내려받아 두세요.")
    return files[-1]


def read_products():
    path = latest_product_csv()
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            with open(path, encoding=enc) as f:
                return list(csv.DictReader(f)), path
        except UnicodeDecodeError:
            continue
    sys.exit(f"인코딩 판별 실패: {path}")


def shipping_of(row):
    """CSV 한 행에서 1개 주문 기준 배송비(KRW)를 뽑는다."""
    kind = (row.get("배송비유형") or "").strip()
    if kind in ("무료", ""):
        return 0
    try:
        return int(float(row.get("기본배송비") or 0))
    except ValueError:
        return 0


def guess_query(name):
    """상품명에서 검색어 후보를 만든다 — 용량·수량·색상 같은 꼬리표를 떼고 앞쪽 핵심어만."""
    name = re.split(r"[,(]", name)[0]
    drop = re.compile(
        r"^(\d+(\.\d+)?(g|kg|ml|l|oz|정|캡슐|개입|개|매|팩|병|입)|x\s*\d+|\d+개입)$",
        re.IGNORECASE,
    )
    words = [w for w in name.split() if not drop.match(w)]
    return " ".join(words[:5])


def cmd_list(data):
    print(f"워치리스트 {len(data['watchlist'])}개  ({WATCHLIST})\n")
    for i, e in enumerate(data["watchlist"], 1):
        ship = e.get("our_shipping_krw", 0)
        ship_s = "무배" if not ship else f"+{ship:,}"
        print(f"{i:>2}. {e['sku']}")
        print(
            f"    상품가 {e['our_price_krw']:>8,} {ship_s:>9}"
            f"  →  도착가 {e['our_landed_krw']:>8,}"
        )
        print(f"    검색어 '{e['query']}'   상품번호 {e.get('product_id') or '-'}")
        for c in e.get("known_competitors", []):
            print(f"      · 기확인 경쟁사: {c}")
        print()


def cmd_add(data, product_id, query):
    if any(e.get("product_id") == product_id for e in data["watchlist"]):
        sys.exit(f"이미 워치리스트에 있음: {product_id}")

    rows, path = read_products()
    match = [r for r in rows if r.get("상품번호(스마트스토어)") == product_id]
    if not match:
        sys.exit(f"{os.path.basename(path)} 에서 상품번호 {product_id} 를 못 찾음")
    row = match[0]

    price = int(float(row.get("판매가") or 0))
    ship = shipping_of(row)
    name = row.get("상품명", "").strip()

    entry = {
        "sku": name[:60],
        "product_id": product_id,
        "query": query or guess_query(name),
        "our_price_krw": price,
        "our_shipping_krw": ship,
        "our_landed_krw": price + ship,
        "unit_note": "",
    }
    data["watchlist"].append(entry)
    save_watchlist(data)

    print(f"추가됨 ({os.path.basename(path)} 기준)")
    print(f"  {entry['sku']}")
    print(f"  상품가 {price:,} + 배송 {ship:,} = 도착가 {entry['our_landed_krw']:,}")
    print(f"  검색어 '{entry['query']}'")
    if not query:
        print("  ※ 검색어는 상품명에서 자동 추정 — 어색하면 --query 로 다시 지정하세요.")


def cmd_remove(data, product_id):
    before = len(data["watchlist"])
    data["watchlist"] = [e for e in data["watchlist"] if e.get("product_id") != product_id]
    if len(data["watchlist"]) == before:
        sys.exit(f"워치리스트에 없음: {product_id}")
    save_watchlist(data)
    print(f"제거됨: {product_id}  (남은 {len(data['watchlist'])}개)")


def main():
    ap = argparse.ArgumentParser(description="경쟁업체 모니터링 워치리스트 관리")
    ap.add_argument("--list", action="store_true", help="워치리스트 출력")
    ap.add_argument("--add", metavar="상품번호", help="판매목록 CSV에서 끌어와 추가")
    ap.add_argument("--query", help="--add 와 함께: 네이버쇼핑 검색어 직접 지정")
    ap.add_argument("--remove", metavar="상품번호", help="워치리스트에서 제거")
    args = ap.parse_args()

    data = load_watchlist()

    if args.add:
        cmd_add(data, args.add, args.query)
    elif args.remove:
        cmd_remove(data, args.remove)
    else:
        cmd_list(data)


if __name__ == "__main__":
    main()
