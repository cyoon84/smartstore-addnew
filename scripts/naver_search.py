#!/usr/bin/env python3
"""네이버 오픈API 검색 (playmcp 네이버 MCP 대체, 2026-07-27).

크리덴셜: ~/.config/finchmart/naver_api.json  (리포에 커밋 금지)

사용:
    python3 scripts/naver_search.py shop "팀홀튼 버라이어티 K컵" [--display 30] [--sort sim|asc|dsc]
    python3 scripts/naver_search.py blog "팀홀튼 K컵 후기"
    python3 scripts/naver_search.py shop "..." --json      # 원본 JSON

shop 결과는 도착가 비교(§0-F)를 위해 lprice(=상품가, 배송비 미포함)임을 항상 표시한다.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CONF = Path.home() / ".config" / "finchmart" / "naver_api.json"
ENDPOINT = "https://openapi.naver.com/v1/search/{kind}.json"
TAG = re.compile(r"<[^>]+>")


def creds():
    if not CONF.exists():
        sys.exit(f"크리덴셜 없음: {CONF}")
    c = json.loads(CONF.read_text())
    return c["client_id"], c["client_secret"]


def search(kind, query, display=20, start=1, sort=None):
    cid, sec = creds()
    params = {"query": query, "display": display, "start": start}
    if sort:
        params["sort"] = sort
    url = ENDPOINT.format(kind=kind) + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:300]}")


def clean(s):
    return TAG.sub("", s or "").replace("&amp;", "&").replace("&quot;", '"')


def show_shop(data, query):
    items = data.get("items", [])
    print(f"검색어: {query}   총 {data.get('total', 0):,}건 중 {len(items)}건")
    print("⚠️ lprice = 상품가(배송비 미포함). 도착가 비교는 배송비를 따로 확인할 것 (§0-F)\n")
    for i, it in enumerate(items, 1):
        cat = " > ".join(
            x for x in (it.get(f"category{n}") for n in (1, 2, 3, 4)) if x
        )
        mall = it.get("mallName") or "-"
        print(f"{i:>2}. ₩{int(it['lprice']):>9,}  {clean(it['title'])[:60]}")
        print(f"     {mall}  |  {cat}")
        print(f"     {it.get('link', '')}")


def show_generic(data, query):
    items = data.get("items", [])
    print(f"검색어: {query}   총 {data.get('total', 0):,}건 중 {len(items)}건\n")
    for i, it in enumerate(items, 1):
        print(f"{i:>2}. {clean(it.get('title'))}")
        desc = clean(it.get("description"))
        if desc:
            print(f"     {desc[:150]}")
        print(f"     {it.get('link', '')}  {it.get('postdate', '')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", help="shop | blog | news | cafearticle | webkr ...")
    ap.add_argument("query")
    ap.add_argument("--display", type=int, default=20)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--sort", default=None, help="shop: sim|date|asc|dsc")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    data = search(a.kind, a.query, a.display, a.start, a.sort)
    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif a.kind == "shop":
        show_shop(data, a.query)
    else:
        show_generic(data, a.query)


if __name__ == "__main__":
    main()
