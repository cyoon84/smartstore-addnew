#!/usr/bin/env python3
"""output/ 루트의 산출물을 제품별 폴더로 분류한다 (반복 실행 안전·idempotent).

- 슬러그는 `_등록정보.md`·`_product_info.json`·`_detail.html` 파일에서 추출.
- 각 루트 파일을 **최장 prefix 슬러그**의 폴더로 이동: output/<slug>/<file>.
- 어느 슬러그에도 안 붙는 파일 → output/_misc/.
- 하위 폴더(seo_refresh, cron_logs, _misc, 기존 제품폴더)는 건드리지 않음.

사용:
  python3 scripts/organize_output.py          # dry-run (미리보기)
  python3 scripts/organize_output.py --apply   # 실제 이동
"""
import argparse, os, re, shutil, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
NEW_ITEM = os.path.join(OUT, "new-item")     # 등록상품 제품 폴더들이 들어가는 곳
SLUG_SUFFIXES = ["_등록정보.md", "_product_info.json", "_detail.html"]


def root_files():
    # output/ 루트에 새로 떨어진 산출물 파일들(등록/동기화가 여기에 씀)
    return [f for f in os.listdir(OUT)
            if os.path.isfile(os.path.join(OUT, f)) and not f.startswith(".")]


def slugs(files):
    s = set()
    for f in files:
        for suf in SLUG_SUFFIXES:
            if f.endswith(suf):
                s.add(f[:-len(suf)])
                break
    # 이미 new-item/ 에 있는 제품 폴더명도 슬러그 후보 (동기화로 들어온 새 파일 매칭용)
    if os.path.isdir(NEW_ITEM):
        for d in os.listdir(NEW_ITEM):
            if os.path.isdir(os.path.join(NEW_ITEM, d)) and not d.startswith("."):
                s.add(d)
    return s


def assign(f, slug_list):
    """파일명에 대해 가장 긴 prefix 슬러그 반환 (경계는 _ 또는 . )."""
    best = None
    for s in slug_list:
        if f == s or f.startswith(s + "_") or f.startswith(s + "."):
            if best is None or len(s) > len(best):
                best = s
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    files = root_files()
    slug_list = sorted(slugs(files), key=len, reverse=True)
    plan = defaultdict(list)
    misc = []
    for f in files:
        s = assign(f, slug_list)
        (plan[s] if s else misc).append(f)

    moved = 0
    for slug, fs in sorted(plan.items()):
        dest = os.path.join(NEW_ITEM, slug)
        for f in fs:
            src = os.path.join(OUT, f)
            if a.apply:
                os.makedirs(dest, exist_ok=True)
                shutil.move(src, os.path.join(dest, f))
            moved += 1
        print(f"  new-item/{slug}/  ({len(fs)}개)")
    if misc:
        dest = os.path.join(NEW_ITEM, "_misc")
        for f in misc:
            if a.apply:
                os.makedirs(dest, exist_ok=True)
                shutil.move(os.path.join(OUT, f), os.path.join(dest, f))
        print(f"  new-item/_misc/  ({len(misc)}개): {', '.join(misc[:8])}{' …' if len(misc)>8 else ''}")

    print(f"\n{'이동' if a.apply else 'DRY-RUN'}: {len(plan)}개 제품 폴더, {moved}개 파일"
          + (f", _misc {len(misc)}개" if misc else ""))
    if not a.apply:
        print("→ 실제 적용: python3 scripts/organize_output.py --apply")


if __name__ == "__main__":
    main()
