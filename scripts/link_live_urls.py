#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 전체 판매목록 CSV(guide/Product_*.csv) 와 output/new-item/<slug>/ 산출물을
상품명으로 매칭해, 일치하면 라이브 URL 을 다음 두 곳에 기록한다:
  - <slug>_product_info.json : live_url / live_product_id / live_status
  - <slug>_등록정보.md        : 제목 아래 '🟢 라이브:' 한 줄 (idempotent)

매칭 규칙:
  - 상품명 공백 제거 후 정확 일치 우선.
  - 그룹상품(CSV 가 '<그룹명>, <옵션1>, <옵션2>' 로 옵션을 덧붙임)은
    CSV 제목이 우리 제목으로 시작하면(prefix) 매칭.

사용:
  python3 scripts/link_live_urls.py            # 미리보기(dry-run)
  python3 scripts/link_live_urls.py --apply     # 실제 기록
  python3 scripts/link_live_urls.py --csv guide/Product_xxx.csv --apply
"""
import os, sys, re, csv, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_ITEM = os.path.join(ROOT, "output", "new-item")
SKIP = {"_batch", "_misc", "_dashboard", "_seo_refresh"}
STORE = "finchmart_ca"
URL = "https://smartstore.naver.com/{}/products/{}".format(STORE, "{}")


def _sales_csvs(guide_dir):
    """guide 판매목록 CSV — Product_*.csv + 스마트스토어상품_*.csv 둘 다, 파일명 날짜(YYYYMMDD_HHMMSS)순(오래된→최신). macOS 한글파일명 NFD/NFC 이슈 회피 위해 *.csv 글롭 후 NFC 정규화로 필터. (네이버 내보내기 이름 변경 2026-07-08 대응.)"""
    import re as _re, glob as _glob, os as _os, unicodedata as _ud
    out = []
    for p in _glob.glob(_os.path.join(guide_dir, "*.csv")):
        b = _ud.normalize("NFC", _os.path.basename(p))
        if b.startswith("Product_") or b.startswith("스마트스토어상품_"):
            out.append(p)
    def _k(p):
        m = _re.search(r"\d{8}_\d{6}", _os.path.basename(p))
        return m.group(0) if m else _os.path.basename(p)
    return sorted(out, key=_k)


def norm(s):
    return re.sub(r"\s+", "", (s or "")).lower()


def latest_csv():
    cands = _sales_csvs(os.path.join(ROOT, "guide"))
    return cands[-1] if cands else None


def load_csv(path):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r)
        i_name = header.index("상품명")
        i_id = header.index("상품번호(스마트스토어)")
        i_status = header.index("판매상태")
        for row in r:
            if len(row) <= max(i_name, i_id, i_status):
                continue
            name = row[i_name].strip()
            pid = row[i_id].strip()
            if not name or not pid:
                continue
            rows.append({"name": name, "norm": norm(name), "pid": pid,
                         "status": row[i_status].strip()})
    return rows


def deep_title(d):
    for k in ("title_ko", "product_name_ko", "title"):
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def match(our_norm, csv_rows):
    # 1) 정확 일치
    for c in csv_rows:
        if c["norm"] == our_norm:
            return c
    # 2) 그룹 prefix (CSV 가 옵션을 덧붙인 경우) — 우리 제목이 충분히 길 때만
    if len(our_norm) >= 8:
        cands = [c for c in csv_rows if c["norm"].startswith(our_norm)]
        if len(cands) == 1:
            return cands[0]
        # 여러 옵션행이 같은 그룹 → 첫 행(대표) 사용
        if len(cands) > 1:
            return sorted(cands, key=lambda c: len(c["norm"]))[0]
    return None


def update_md(md_path, url, apply):
    with open(md_path, encoding="utf-8") as f:
        txt = f.read()
    if "smartstore.naver.com/{}/products".format(STORE) in txt:
        return "already"
    lines = txt.splitlines()
    # 첫 비어있지 않은(제목) 줄 다음에 삽입
    insert_at = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            insert_at = i + 1
            break
    block = ["", "**🟢 라이브:** {}".format(url)]
    new = "\n".join(lines[:insert_at] + block + lines[insert_at:]) + "\n"
    if apply:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new)
    return "inserted"


def main():
    apply = "--apply" in sys.argv
    csv_path = None
    if "--csv" in sys.argv:
        csv_path = sys.argv[sys.argv.index("--csv") + 1]
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(ROOT, csv_path)
    csv_path = csv_path or latest_csv()
    if not csv_path or not os.path.exists(csv_path):
        print("❌ CSV 없음")
        sys.exit(1)
    csv_rows = load_csv(csv_path)
    print("📄 CSV: {}  ({}행)".format(os.path.relpath(csv_path, ROOT), len(csv_rows)))

    matched = unmatched = 0
    report = []
    for folder in sorted(glob.glob(os.path.join(NEW_ITEM, "*"))):
        if not os.path.isdir(folder) or os.path.basename(folder) in SKIP:
            continue
        cand = glob.glob(os.path.join(folder, "*_product_info.json"))
        if not cand:
            continue
        pinfo = cand[0]
        with open(pinfo, encoding="utf-8") as f:
            d = json.load(f)
        slug = os.path.basename(folder)
        title = deep_title(d) or slug
        m = match(norm(title), csv_rows)
        if not m:
            unmatched += 1
            report.append(("—", slug, title[:42]))
            continue
        matched += 1
        url = URL.format(m["pid"])
        # product_info.json 갱신
        changed = False
        if d.get("live_product_id") != m["pid"]:
            d["live_url"] = url
            d["live_product_id"] = m["pid"]
            d["live_status"] = m["status"]
            changed = True
        if apply and changed:
            with open(pinfo, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
        # 등록정보.md 갱신
        md = glob.glob(os.path.join(folder, "*등록정보.md"))
        md_state = update_md(md[0], url, apply) if md else "no-md"
        report.append((m["pid"], slug, "{}  [{}/{}]".format(title[:38], m["status"], md_state)))

    for pid, slug, info in report:
        print("  {:>14}  {:<46}  {}".format(pid, slug, info))
    print("\n{} 일치 / {} 미일치 (총 {})".format(matched, unmatched, matched + unmatched))
    print("모드: {}".format("APPLY (기록함)" if apply else "DRY-RUN (미리보기) — 적용하려면 --apply"))


if __name__ == "__main__":
    main()
