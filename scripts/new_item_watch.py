#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
output/new-item/ 에 새 제품 폴더가 생기면(Cowork 동기화·source-launch cron·수동 등록 등)
Slack(#new-item)으로 알리고, 라이브 URL 매칭을 한 번 돌려 등록정보를 리프레시한다.

- 본 적 있는 슬러그 스냅샷: ~/.finchmart_newitem_seen
- 첫 실행(스냅샷 없음)은 기존 폴더를 전부 'seen' 으로 시드만 하고 알림 안 보냄(스팸 방지).
- 새 슬러그 발견 시: product_info 에서 제목·가격·모드 읽어 Slack 요약 전송 → live_url 매칭 갱신.
- launchd WatchPaths(output/new-item) 가 폴더 변화 시 호출. 반복 호출돼도 스냅샷으로 dedup.

실행:  python3 scripts/new_item_watch.py
"""
import os, sys, json, glob, subprocess, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_ITEM = os.path.join(ROOT, "output", "new-item")
SEEN = os.path.join(os.path.expanduser("~"), ".finchmart_newitem_seen")
SKIP = {"_batch", "_misc", "_dashboard", "_seo_refresh"}


def current_slugs():
    out = set()
    for s in os.listdir(NEW_ITEM):
        if s in SKIP:
            continue
        d = os.path.join(NEW_ITEM, s)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*_product_info.json")):
            out.add(unicodedata.normalize("NFC", s))
    return out


def info_of(slug):
    pj = glob.glob(os.path.join(NEW_ITEM, slug, "*_product_info.json"))
    if not pj:
        return slug, None, ""
    try:
        d = json.load(open(pj[0], encoding="utf-8"))
    except Exception:
        return slug, None, ""

    def find(keys):
        st = [d]
        while st:
            o = st.pop()
            if isinstance(o, dict):
                for k in keys:
                    if o.get(k) not in (None, "", [], {}):
                        return o[k]
                st += list(o.values())
            elif isinstance(o, list):
                st += o
        return None
    title = find(["title_ko", "product_name_ko", "title"]) or slug
    price = find(["sell_price_krw", "sell_krw", "selling_price_krw"])
    mode = find(["mode"]) or "single"
    return title, price, mode


def main():
    cur = current_slugs()
    if not os.path.exists(SEEN):
        open(SEEN, "w", encoding="utf-8").write("\n".join(sorted(cur)))
        print(f"[seed] 첫 실행 — {len(cur)}개 시드만, 알림 없음")
        return
    seen = set(x.strip() for x in open(SEEN, encoding="utf-8") if x.strip())
    new = sorted(cur - seen)
    # 스냅샷은 항상 현재로 갱신(삭제 반영)
    open(SEEN, "w", encoding="utf-8").write("\n".join(sorted(cur)))
    if not new:
        print("[ok] 새 제품 없음")
        return

    lines = [f"🆕 *새 등록상품 {len(new)}건* (output/new-item)"]
    for s in new[:20]:
        title, price, mode = info_of(s)
        p = f"₩{price:,}" if isinstance(price, (int, float)) else "가격미상"
        tag = "그룹" if mode == "group" else "단일"
        lines.append(f"• {title} — {p} ({tag})")
    if len(new) > 20:
        lines.append(f"…외 {len(new)-20}건")
    lines.append("→ 대시보드: http://localhost:4178 (열려 있으면 자동 갱신)")
    msg = "\n".join(lines)

    try:
        subprocess.run(["python3", os.path.join(ROOT, "scripts", "slack_notify.py"),
                        "--text", msg, "--raw"], check=False)
    except Exception as e:
        print("slack 전송 실패:", e)

    # 라이브 URL 매칭 리프레시(있으면 등록정보·product_info 갱신)
    for sc in ("link_live_urls.py", "add_live_url_to_md.py"):
        p = os.path.join(ROOT, "scripts", sc)
        if os.path.exists(p):
            subprocess.run(["python3", p], check=False)

    print(f"[notify] 새 제품 {len(new)}건 알림 전송:", ", ".join(new[:20]))


if __name__ == "__main__":
    main()
