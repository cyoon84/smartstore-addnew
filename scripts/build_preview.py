#!/usr/bin/env python3
"""등록 배치의 detail.html 을 한 장으로 묶어 렌더 검사용 미리보기를 만든다.

시각 QA(listing-visual-qa)가 브라우저로 열어 "고객이 뭘 보게 되는가"를 검사할 대상.
SKU 사이에 구분 헤더를 넣어 어느 상세인지 알 수 있게 한다.

사용:
    python3 scripts/build_preview.py <slug> [slug ...] [--out 경로]
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW = ROOT / "output" / "new-item"

HEAD = """<!doctype html>
<meta charset="utf-8">
<title>등록 상세 미리보기 — {n}종</title>
<style>
  body{{margin:0;padding:0;background:#e9e9e9;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif}}
  .sku-head{{max-width:860px;margin:34px auto 10px;padding:14px 20px;background:#222;color:#fff;
            border-radius:12px;font-size:15px;line-height:1.6}}
  .sku-head b{{font-size:18px}}
  .sku-head span{{color:#bbb}}
  .note{{max-width:860px;margin:0 auto 26px;padding:10px 20px;background:#fff6d9;border:1px solid #e8d48a;
        border-radius:10px;font-size:13px;color:#6b5300;line-height:1.6}}
</style>
<div class="note">⚠️ 검사용 미리보기입니다. 네이버 에디터 렌더와 100% 동일하지 않을 수 있으나,
이미지 로드·여백·모바일 폭·텍스트 잘림 판정에는 충분합니다. 실제 등록 시엔 각 SKU 의 detail.html 을 개별로 붙여넣습니다.</div>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()

    parts = [HEAD.format(n=len(a.slugs))]
    missing = []
    for s in a.slugs:
        d = NEW / s
        html = d / f"{s}_detail.html"
        info = d / f"{s}_product_info.json"
        if not html.exists():
            missing.append(str(html))
            continue
        meta = ""
        if info.exists():
            j = json.loads(info.read_text())
            pr = j.get("pricing", {})
            img = j.get("images", {})
            meta = (f'<b>{j.get("title_ko","?")}</b><br>'
                    f'<span>slug {s} · 판매가 ₩{pr.get("sell_price_krw",0):,} · '
                    f'{j.get("naver_category","?")} · 대표이미지 {img.get("rep_image_url","(없음)")}</span>')
        else:
            meta = f"<b>{s}</b>"
        parts.append(f'<div class="sku-head">{meta}</div>\n')
        parts.append(html.read_text())

    if missing:
        sys.exit("detail.html 없음:\n  " + "\n  ".join(missing))

    out = pathlib.Path(a.out) if a.out else (
        NEW / "_batch" / f"preview_{'_'.join(a.slugs)[:60]}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts))
    print(out)


if __name__ == "__main__":
    main()
