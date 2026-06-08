#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
product_info.json 에 live_url 이 있는(=실제 판매중으로 확정된) 제품의 등록정보.md 첫 H1 아래에
'**🟢 라이브:** <url>' 라인을 추가한다. 이미 url 이 md 에 있으면 건너뜀(idempotent).

전체 판매 리스트(스토어 실판매)와 생성 리스트 매칭은 live_url 유무로 본다 — 셀러가 등록 후
product_info 에 live_url 을 채워두면 그게 '일치' 신호. 추측으로 url 을 만들지 않는다.

사용:  python3 scripts/add_live_url_to_md.py
"""
import os, re, json, glob, unicodedata

def find_md(d):
    """macOS NFD/NFC 혼재 대비 — listdir 후 정규화해서 '등록정보.md' 로 끝나는 파일 찾기."""
    for f in os.listdir(d):
        if unicodedata.normalize("NFC", f).endswith("등록정보.md"):
            return os.path.join(d, f)
    return None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_ITEM = os.path.join(ROOT, "output", "new-item")
SKIP = {"_batch", "_misc", "_dashboard", "_seo_refresh"}

added, already, no_md, no_url = [], [], [], []

for slug in sorted(os.listdir(NEW_ITEM)):
    if slug in SKIP:
        continue
    d = os.path.join(NEW_ITEM, slug)
    if not os.path.isdir(d):
        continue
    pj = glob.glob(os.path.join(d, "*_product_info.json"))
    if not pj:
        continue
    try:
        info = json.load(open(pj[0], encoding="utf-8"))
    except Exception:
        continue
    url = info.get("live_url")
    if not url:
        no_url.append(slug)
        continue
    status = info.get("live_status") or "판매중"
    md = find_md(d)
    if not md:
        no_md.append(slug)
        continue
    text = open(md, encoding="utf-8").read()
    if url in text:
        already.append(slug)
        continue
    line = f"**🟢 라이브({status}):** {url}"
    lines = text.split("\n")
    # 첫 H1(# ...) 다음에 빈 줄 + 라이브 라인 삽입. H1 없으면 맨 앞.
    idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), -1)
    if idx >= 0:
        insert_at = idx + 1
        block = ["", line]
        # H1 바로 다음이 이미 빈 줄이면 빈 줄 중복 피함
        if insert_at < len(lines) and lines[insert_at].strip() == "":
            block = ["", line]
        lines[insert_at:insert_at] = block
    else:
        lines[0:0] = [line, ""]
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    added.append(slug)

print(f"✅ live_url md 추가: {len(added)}건")
for s in added:
    print("   +", s)
print(f"· 이미 있음 {len(already)} · md없음(단일색 등) {len(no_md)}: {no_md} · live_url없음(미등록) {len(no_url)}")
