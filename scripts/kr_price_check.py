#!/usr/bin/env python3
"""국내 시세 조회 폴백 (§0-A) — 2026-07-31 신설.

배경 (2026-07-31 확인):
  - 네이버 오픈API `shop.json` → **SE05 (Invalid search api)** 로 사망 → `scripts/naver_search.py shop` 불가
  - `search.shopping.naver.com` / `msearch.shopping.naver.com` → **418 차단**
  - `m.coupang.com` → 챌린지 페이지(빈 응답)
  - `search.11st.co.kr` / `browse.gmarket.co.kr` → 사실상 빈 응답
  - **`search.danawa.com` 은 정상 응답** (국내 최저가 집계) → 이걸 1차 채널로
  - 네이버 오픈API **blog / webkr / news 는 정상** → 국내 유통 여부·가격 언급 보조 신호

사용:
    python3 scripts/kr_price_check.py "킥킹호스 커피"
    python3 scripts/kr_price_check.py "팀홀튼 K컵" --danawa-only

⚠️ 다나와 가격도 **상품가(배송비 미포함)**. 도착가 비교는 §0-F 대로 배송비 별도 확인.
⚠️ 다나와는 식품 커버리지가 얕을 수 있음 — 0건이 곧 "국내 미유통" 확정은 아니다.
   반드시 naver blog/webkr 결과와 §0-A-1(한국 리브랜딩명) 을 같이 볼 것.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENGINE_DIR = Path.home() / ".claude/plugins/cache/gptaku-plugins/insane-search/0.9.1/skills/insane-search"
CONF = Path.home() / ".config" / "finchmart" / "naver_api.json"
TAG = re.compile(r"<[^>]+>")


def danawa(query: str):
    url = "https://search.danawa.com/dsearch.php?" + urllib.parse.urlencode({"query": query})
    try:
        out = subprocess.run(
            [sys.executable, "-m", "engine", url],
            cwd=ENGINE_DIR, capture_output=True, text=True, timeout=300,
        ).stdout
    except Exception as e:
        return None, f"engine 실패: {e}"
    names = re.findall(r'<p class="prod_name">\s*<a[^>]*>(.*?)</a>', out, re.S)
    prices = re.findall(r"<strong>([0-9,]{3,12})</strong>", out)
    rows = []
    for n, p in zip(names, prices):
        rows.append((TAG.sub("", n).strip(), int(p.replace(",", ""))))
    return rows, None


def naver_api(kind: str, query: str, display: int = 10):
    if not CONF.exists():
        return []
    c = json.loads(CONF.read_text())
    url = f"https://openapi.naver.com/v1/search/{kind}.json?" + urllib.parse.urlencode(
        {"query": query, "display": display}
    )
    req = urllib.request.Request(
        url,
        headers={"X-Naver-Client-Id": c["client_id"], "X-Naver-Client-Secret": c["client_secret"]},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode())
    except Exception:
        return []
    return [(TAG.sub("", i.get("title", "")), TAG.sub("", i.get("description", "")), i.get("link", "")) for i in d.get("items", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--danawa-only", action="store_true")
    a = ap.parse_args()

    print(f"■ 국내 시세 조회: {a.query}")
    print("⚠️ 가격 = 상품가(배송비 미포함). 도착가 비교는 §0-F.\n")

    rows, err = danawa(a.query)
    print("── 다나와(국내 최저가 집계)")
    if err:
        print("  ", err)
    elif not rows:
        print("   0건 — 국내 유통 신호 약함(단, 식품 커버리지 얕으므로 확정 아님)")
    else:
        for n, p in rows[:15]:
            print(f"   ₩{p:>9,}  {n[:70]}")

    if a.danawa_only:
        return

    for kind, label in (("blog", "네이버 블로그"), ("webkr", "네이버 웹문서")):
        items = naver_api(kind, a.query, 8)
        print(f"\n── {label} ({len(items)}건)")
        for t, d, l in items[:6]:
            print(f"   · {t[:60]}")
            if d:
                print(f"     {d[:110]}")


if __name__ == "__main__":
    main()
