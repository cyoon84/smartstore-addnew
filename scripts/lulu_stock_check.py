#!/usr/bin/env python3
"""룰루레몬 공홈 재고 ↔ 스마트스토어 등록 옵션 매칭 점검 (월 1회).

왜 스크립트+브라우저 2단계인가:
  룰루레몬 공홈은 Akamai 봇차단(헤드리스 curl/WebFetch = 403 Access Denied).
  → 재고 수집은 **실브라우저(claude-in-chrome / Cowork)** 로만 가능.
  → 이 스크립트는 '수집된 재고 JSON' 을 받아 '등록 옵션' 과 대조하는 **비교 엔진**만 담당.

월간 실행 흐름 (트리거가 뜨면 에이전트가):
  1) 실브라우저로 config 의 각 lululemon_url 을 열고 아래 JS 로 variants 추출 → stock.json 저장
  2) python3 scripts/lulu_stock_check.py --config <config> --stock <stock.json> --slack
  3) 스크립트가 대조 리포트 → Slack #new-item

브라우저에서 실행할 추출 JS (claude-in-chrome javascript_tool):
  --------------------------------------------------------------------
  (()=>{const ld=[...document.querySelectorAll('script[type="application/ld+json"]')]
    .map(s=>{try{return JSON.parse(s.textContent)}catch(e){return null}})
    .find(j=>j&&j['@type']==='ProductGroup');
   if(!ld) return {error:'no ProductGroup'};
   return (ld.hasVariant||[]).map(v=>{const o=Array.isArray(v.offers)?(v.offers[0]||{}):(v.offers||{});
     return {color:v.color, sku:v.sku,
     style_color:(v.image||'').split('/lululemon/')[1]||'',   // 예: LU9BQPS_0001_1
     price:o.price||'',
     availability:(o.availability||'').split('/').pop()};});})();  // InStock / OutOfStock
  --------------------------------------------------------------------
  결과 배열을 stock.json 에 { "<monitor.id>": [...variants...] } 형태로 저장.

사용:
  python3 scripts/lulu_stock_check.py --config <config.json> --stock <stock.json> [--slack] [--out report.md]
  python3 scripts/lulu_stock_check.py --fetch-help          # 추출 JS 만 출력
"""
import argparse, json, os, sys, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def norm_style(s):
    """LU9BQPS_0001_1 / LU9BQPS_0001 → LU9BQPS_0001 (뷰 접미 제거)."""
    if not s: return ""
    parts = s.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else s

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def compare(monitor, variants):
    """등록 옵션 ↔ 공홈 variants 대조. (issues, lines) 반환."""
    # 공홈 재고를 style_color(뷰제거) 단위로 **집계**: 한 색상에 사이즈 변형이 여러 개라,
    # 사이즈 중 하나라도 InStock 이면 그 색상은 "재고 있음"(any-InStock 롤업).
    # (이전 버그: dict 덮어쓰기로 마지막 사이즈 재고상태만 남아 일부품절 색을 전체품절로 오판.)
    def agg():
        by_style, by_color = {}, {}
        for v in variants or []:
            av = (v.get("availability") or "").strip()
            inst = av.lower() == "instock"
            size = (v.get("size") or "").strip()
            for key, bucket in ((norm_style(v.get("style_color", "")), by_style),
                                ((v.get("color") or "").strip().lower(), by_color)):
                if not key:
                    continue
                b = bucket.setdefault(key, {"in": [], "out": [], "any": False})
                b["any"] = b["any"] or inst
                (b["in"] if inst else b["out"]).append(size or "?")
        return by_style, by_color
    live_by_style, live_by_color = agg()
    reg = monitor.get("registered_options", [])
    reg_styles = {norm_style(o.get("style_color", "")) for o in reg if o.get("style_color")}

    def size_note(b):
        if not b:
            return ""
        ins = [s for s in b["in"] if s != "?"]
        outs = [s for s in b["out"] if s != "?"]
        if not ins and not outs:
            return ""
        parts = []
        if ins:
            parts.append(f'재고 {len(ins)}: {", ".join(ins)}')
        if outs:
            parts.append(f'품절 {len(outs)}: {", ".join(outs)}')
        return f' [사이즈 {" / ".join(parts)}]'

    oos, partial, gone, ok = [], [], [], []
    for o in reg:
        st = norm_style(o.get("style_color", ""))
        ce = (o.get("color_en") or "").strip().lower()
        b = live_by_style.get(st) or live_by_color.get(ce)
        label = f'{o.get("color_ko","?")} ({o.get("color_en","?")})'
        if b is None:
            gone.append(label)          # 공홈에서 사라짐 = 단종 가능
        elif not b["any"]:
            oos.append(f'{label} → 전 사이즈 품절')   # 모든 사이즈 OOS
        else:
            note = size_note(b)
            # 사이즈 일부 품절이면 참고용 partial(이슈 아님 — 색상은 판매중)
            if [s for s in b["out"] if s != "?"]:
                partial.append(f'{label}{note}')
            else:
                ok.append(f'{label}{note}')
    # 공홈엔 InStock 인데 우리가 미등록인 신규 색
    new_colors = []
    seen_new = set()
    for v in variants or []:
        st = norm_style(v.get("style_color", ""))
        if (v.get("availability") or "").lower() == "instock" and st not in reg_styles and st not in seen_new:
            seen_new.add(st)
            new_colors.append(f'{v.get("color","?")} ({st}, ${v.get("price","?")})')

    issue = bool(oos or gone or new_colors)
    L = [f'*{monitor.get("name","(이름없음)")}*']
    L.append(f'  공홈: {monitor.get("lululemon_url","")}')
    if not variants:
        L.append('  ⚠️ 공홈 재고 수집 실패(빈 결과) — URL/차단 확인 필요')
        return True, L
    if gone:
        L.append(f'  🛑 공홈에서 사라짐(단종 의심) — *판매중지 검토*: {", ".join(gone)}')
    if oos:
        L.append(f'  ⚠️ 공홈 품절 — 등록중인데 재고 없음: {", ".join(oos)}')
    if new_colors:
        L.append(f'  ➕ 공홈 신규 재고(미등록) — 추가 기회: {", ".join(new_colors)}')
    if partial:
        L.append(f'  🟡 일부 사이즈 품절(색상은 판매중): {" · ".join(partial)}')
    L.append(f'  ✅ 정상 매칭({len(ok)}): {" · ".join(ok) if ok else "-"}')
    return issue, L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--stock")
    ap.add_argument("--slack", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--frequency", help="monitor 필터: daily / monthly (check_frequency 기준). 생략 시 전체")
    ap.add_argument("--fetch-help", action="store_true")
    a = ap.parse_args()
    if a.fetch_help:
        print(__doc__.split("브라우저에서 실행할 추출 JS")[1].split("결과 배열")[0])
        return
    if not a.config or not a.stock:
        sys.exit("--config 와 --stock 필요 (--fetch-help 로 추출 JS 확인)")

    cfg = load(a.config)
    stock = load(a.stock)
    today = datetime.date.today().isoformat()

    monitors = cfg.get("monitors", [])
    if a.frequency:
        monitors = [m for m in monitors if (m.get("check_frequency") or "monthly") == a.frequency]
    freq_label = f" [{a.frequency}]" if a.frequency else ""
    report = [f"# 룰루레몬 공홈 재고 ↔ 스마트스토어 옵션 점검{freq_label} ({today})", ""]
    any_issue = False
    for m in monitors:
        variants = stock.get(m.get("id")) or stock.get(m.get("lululemon_url")) or []
        issue, lines = compare(m, variants)
        any_issue = any_issue or issue
        report += lines + [""]
    if not any_issue:
        report.append("✅ 전 항목 정상 — 조치 필요 없음")

    text = "\n".join(report)
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    if a.slack:
        sn = os.path.join(ROOT, "scripts", "slack_notify.py")
        try:
            subprocess.run([sys.executable, sn, "--text", text], check=True)
        except Exception as e:
            print(f"[!] Slack 전송 실패: {e}", file=sys.stderr)
    # issue 있으면 exit 2 (스케줄러가 알림 판단에 활용 가능)
    sys.exit(2 if any_issue else 0)

if __name__ == "__main__":
    main()
