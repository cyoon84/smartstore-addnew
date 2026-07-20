#!/usr/bin/env python3
"""YETI 푸어오버 아마존 재고 주 1회 체크 → Slack #new-item.
Coffee Stone 제외(Sport Chek 온라인 별도). insane-search engine 헤드리스 사용."""
import sys, subprocess, os, re, json, urllib.request

ENGINE_DIR = "/Users/chulhee-macmini/.claude/plugins/cache/gptaku-plugins/insane-search/0.9.1/skills/insane-search"
SLACK_CHANNEL = "C0B5F379DSB"  # #new-item

COLORS = [
    ("Black", "B0DS6KM3WW"),
    ("Navy", "B0DS6LPYBK"),
    ("White", "B0DS6ND1KG"),
    ("Rescue Red", "B0DS6LNPXW"),
    ("Cape Taupe", "B0FMKQ9XGP"),
]

def check(asin):
    try:
        out = subprocess.run(
            [sys.executable, "-m", "engine", f"https://www.amazon.ca/dp/{asin}", "--device", "desktop"],
            cwd=ENGINE_DIR, capture_output=True, text=True, timeout=120).stdout
    except Exception as e:
        return "ERROR", None
    price = None
    m = re.search(r'"priceAmount":([0-9.]+)', out)
    if m: price = float(m.group(1))
    # #availability 영역 텍스트만 판정 근거로 (페이지 타 영역 'unavailable' 오검출 방지)
    am = re.search(r'id="availability".{0,300}?', out, re.S)
    avail_txt = ""
    if am:
        avail_txt = re.sub(r"<[^>]*>", " ", am.group(0)).lower()
    has_cart = 'id="add-to-cart-button"' in out
    if "out of stock" in avail_txt or "unavailable" in avail_txt:
        return "OUT", price
    if "in stock" in avail_txt or ("only" in avail_txt and "left" in avail_txt) or has_cart:
        return "IN", price
    return "UNKNOWN", price

def main():
    lines = ["*🥤 YETI 푸어오버 아마존 재고 (주간)* — Coffee Stone 제외(Sport Chek)"]
    flag = False
    for name, asin in COLORS:
        st, price = check(asin)
        icon = {"IN":"✅","OUT":"🚨","UNKNOWN":"⚠️","ERROR":"⛔"}.get(st,"⚠️")
        pr = f"${price:.2f}" if price else "-"
        if st != "IN": flag = True
        lines.append(f"{icon} {name}: {st} · {pr}")
    if flag:
        lines.append("\n⚠️ 품절/이상 색상 있음 — 확인 필요")
    msg = "\n".join(lines)
    print(msg)
    # Slack 전송 — 프로젝트 slack_notify.py (webhook, MCP 불필요)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    notify = os.path.join(root, "scripts", "slack_notify.py")
    try:
        subprocess.run([sys.executable, notify, "--text", msg, "--raw"], timeout=30)
    except Exception as e:
        print("slack fail:", e)

if __name__ == "__main__":
    main()
