#!/usr/bin/env python3
"""룰루레몬 공홈 재고를 **insane-search engine**(로컬 Playwright real-Chrome, Akamai 우회)로 헤드리스 수집.

기존엔 실브라우저(claude-in-chrome) 세션이 있어야 했지만, insane-search 플러그인의 engine 이
Akamai Bot Manager 를 로컬 real-Chrome 으로 뚫어 raw HTML 을 돌려주므로 **완전 헤드리스 자동화** 가능.

흐름: config 의 각 monitor lululemon_url → `python3 -m engine <URL>` (insane-search) → raw HTML →
ProductGroup JSON-LD 의 hasVariant 파싱 → {"<monitor.id>":[variants]} 를 --out 에 저장.
그 다음 lulu_stock_check.py --stock <out> 로 대조.

사용:
  python3 scripts/lulu_stock_fetch.py --config <config.json> --out /tmp/lulu_stock.json [--frequency daily|monthly]

전제: insane-search 플러그인 설치 + engine/templates 의 Playwright/Patchright(chrome) 설치됨.
"""
import argparse, glob, json, os, re, subprocess, sys

def find_engine_dir():
    pats = [
        os.path.expanduser("~/.claude/plugins/cache/*/insane-search/*/skills/insane-search"),
        os.path.expanduser("~/.claude/plugins/**/insane-search/**/skills/insane-search"),
    ]
    for p in pats:
        hits = sorted(glob.glob(p, recursive=True))
        if hits:
            return hits[-1]  # 최신 버전 경로
    return None

def fetch_html(engine_dir, url, timeout=220):
    r = subprocess.run([sys.executable, "-m", "engine", url],
                       cwd=engine_dir, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.returncode

def parse_variants(raw):
    blocks = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', raw, re.S)
    for b in blocks:
        try:
            j = json.loads(b.strip())
        except Exception:
            continue
        if isinstance(j, dict) and j.get("@type") == "ProductGroup":
            out = []
            for v in j.get("hasVariant", []):
                o = v.get("offers")
                o = o[0] if isinstance(o, list) else (o or {})
                out.append({
                    "color": v.get("color"),
                    "sku": v.get("sku"),
                    "size": v.get("size"),
                    "style_color": (v.get("image") or "").split("/lululemon/")[-1],
                    "price": o.get("price", ""),
                    "availability": (o.get("availability") or "").split("/")[-1],
                })
            return out
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frequency", help="daily / monthly (check_frequency 필터). 생략 시 전체")
    a = ap.parse_args()

    engine_dir = find_engine_dir()
    if not engine_dir:
        sys.exit("[!] insane-search engine 경로를 못 찾음 — 플러그인 설치 확인")

    cfg = json.load(open(a.config, encoding="utf-8"))
    monitors = cfg.get("monitors", [])
    if a.frequency:
        monitors = [m for m in monitors if (m.get("check_frequency") or "monthly") == a.frequency]

    stock, fails = {}, []
    for m in monitors:
        mid, url = m.get("id"), m.get("lululemon_url")
        if not url:
            continue
        try:
            raw, rc = fetch_html(engine_dir, url)
            variants = parse_variants(raw)
            if variants:
                stock[mid] = variants
                print(f"· {mid}: {len(variants)} variants (rc={rc})")
            else:
                fails.append(mid); print(f"⚠️ {mid}: ProductGroup JSON-LD 파싱 실패 (rc={rc})")
        except Exception as e:
            fails.append(mid); print(f"⚠️ {mid}: {e}")

    json.dump(stock, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n저장: {a.out} ({len(stock)} monitor) · 실패 {len(fails)}: {fails}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
