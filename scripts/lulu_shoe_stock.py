#!/usr/bin/env python3
"""룰루레몬 신발(색상 고정) 사이즈별 재고를 헤드리스로 체크.

룰루레몬 공홈은 Akamai 봇차단이지만 insane-search engine(로컬 real-Chrome)이 뚫어
ProductGroup JSON-LD 를 돌려준다 → 그 색상의 사이즈별 availability(InStock/OutOfStock) + 가격 파싱.

사용:
  python3 scripts/lulu_shoe_stock.py <URL> <color_code>
  # 예: python3 scripts/lulu_shoe_stock.py "https://shop.lululemon.com/.../prod11720557?color=71742" 71742

출력: JSON 한 줄 {name,color,price,currency,in_stock:[사이즈],out:[사이즈],total,ts...}
그 다음 이 결과를 Slack 등에 보고한다(스크립트는 파싱만, 보고는 호출측).
"""
import sys, os, re, json, glob, subprocess

def engine_dir():
    pats=[os.path.expanduser("~/.claude/plugins/cache/*/insane-search/*/skills/insane-search"),
          os.path.expanduser("~/.claude/plugins/**/insane-search/**/skills/insane-search")]
    for p in pats:
        h=sorted(glob.glob(p, recursive=True))
        if h: return h[-1]
    return None

def fetch(url):
    ed=engine_dir()
    if not ed: return None
    r=subprocess.run([sys.executable,"-m","engine",url], cwd=ed, capture_output=True, text=True, timeout=240)
    return r.stdout

def parse(html, color_code):
    blocks=re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S)
    pg=None
    for b in blocks:
        try: j=json.loads(b.strip())
        except: continue
        if j.get("@type")=="ProductGroup": pg=j; break
    if not pg: return None
    vs=pg.get("hasVariant") or []
    tgt=[v for v in vs if f"color={color_code}" in (v.get("url") or "")]
    name=pg.get("name"); color=tgt[0].get("color") if tgt else None
    in_stock, out, price, cur = [], [], None, None
    for v in tgt:
        sz=(v.get("name") or "").split(" - ")[-1]
        o=v.get("offers"); o=o[0] if isinstance(o,list) and o else (o or {})
        av=(o.get("availability") or "").split("/")[-1]
        price=price or o.get("price"); cur=cur or o.get("priceCurrency")
        (in_stock if av=="InStock" else out).append(sz)
    def key(s):
        try: return float(s)
        except: return 99
    return {"name":name,"color":color,"price":price,"currency":cur,
            "in_stock":sorted(in_stock,key=key),"out":sorted(out,key=key),
            "total":len(tgt)}

if __name__=="__main__":
    if len(sys.argv)<3:
        print(json.dumps({"error":"usage: lulu_shoe_stock.py <URL> <color_code>"})); sys.exit(1)
    url, color = sys.argv[1], sys.argv[2]
    html=fetch(url)
    if not html or len(html)<5000:
        print(json.dumps({"error":"fetch_failed","note":"engine 차단/실패 — 수동 확인"})); sys.exit(2)
    res=parse(html, color)
    if not res:
        print(json.dumps({"error":"parse_failed","note":"ProductGroup 없음 — 페이지구조 변경?"})); sys.exit(3)
    print(json.dumps(res, ensure_ascii=False))
