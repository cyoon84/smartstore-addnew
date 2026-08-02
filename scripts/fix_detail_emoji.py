#!/usr/bin/env python3
"""상세페이지 국기 이모지 제거 (2026-07-31 신설, 2026-08-02 범위 축소).

배경: 처음엔 "네이버가 4바이트 문자를 전부 흘린다"고 보고 **모든 4바이트 이모지를 BMP 기호로
      치환**했다. **이건 과잉이었다.**

      2026-08-02 사장님 실측: 단일 4바이트 이모지(🍁·🥄·📦·🍯)는 네이버 에디터 붙여넣기·
      미리보기 모두 정상. 깨지는 건 **국기(Regional Indicator 2자 결합 = 8바이트)뿐**이고
      `⊠⊠` 두부박스로 나온다.

      → 사장님 지시(2026-08-02): *"밋밋한 기호 쓰지말자"*. 멀쩡한 이모지를 `▪`·`★` 같은
      무미건조한 기호로 바꾸면 상세가 밋밋해진다. **국기만 제거하고 나머지는 손대지 않는다.**

사용:
    python3 scripts/fix_detail_emoji.py --check                 # 전수 점검만
    python3 scripts/fix_detail_emoji.py --apply <slug> [...]    # 지정 슬러그 국기 제거
    python3 scripts/fix_detail_emoji.py --apply --all           # 전 카탈로그 국기 제거
    python3 scripts/fix_detail_emoji.py --diff <slug>           # 전후 미리보기

치환 원칙:
  1) 국기(🇨🇦·🇺🇸 등)는 **삭제** — 대체 기호 없음, `⊠⊠` 의 원인
  2) 그 외 이모지는 **전부 보존** (§17-6, [[feedback_naver_emoji_bytes]])
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW_ITEM = ROOT / "output" / "new-item"

# 국기(Regional Indicator) 범위 — 유일한 제거 대상
FLAG = re.compile("[\U0001F1E6-\U0001F1FF]")


def convert(s: str):
    """국기 이모지만 제거한다. 다른 이모지는 그대로 둔다."""
    out = []
    changed = {}
    for ch in s:
        if FLAG.match(ch):
            changed[ch] = changed.get(ch, 0) + 1
            continue  # 국기 삭제
        out.append(ch)
    t = "".join(out)
    # 국기 삭제로 생긴 잔여 공백 정리 (여는 태그 직후 공백만 제거 — inline 간격은 보존)
    t = re.sub(r"(<(?:p|strong|span|div|h1|h2)\b[^>]*>)[ ]+", r"\1", t)
    t = re.sub(r"[ ]{2,}", " ", t)
    return t, changed


def details(slugs=None):
    if slugs:
        return [NEW_ITEM / s / f"{s}_detail.html" for s in slugs]
    return sorted(NEW_ITEM.glob("*/*_detail.html"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--diff", metavar="SLUG")
    a = ap.parse_args()

    if a.diff:
        f = NEW_ITEM / a.diff / f"{a.diff}_detail.html"
        s = f.read_text()
        t, ch = convert(s)
        print(f"■ {a.diff}  국기 {sum(ch.values())}자 / {len(ch)}종")
        for c, n in sorted(ch.items(), key=lambda x: -x[1]):
            print(f"   {c} U+{ord(c):04X} ×{n}  →  (삭제)")
        for a1, b1 in zip(s.splitlines(), t.splitlines()):
            if a1 != b1:
                print("\n  - " + a1.strip()[:150])
                print("  + " + b1.strip()[:150])
        return

    files = details(a.slugs if a.slugs and not a.all else None)
    tot = 0
    for f in files:
        if not f.exists():
            print("없음:", f, file=sys.stderr)
            continue
        s = f.read_text()
        t, ch = convert(s)
        if not ch:
            continue
        tot += 1
        if a.apply:
            f.write_text(t)
        print(f"{'수정' if a.apply else '검출'} {f.parent.name}: 국기 {sum(ch.values())}자({len(ch)}종)")
    print(f"\n{'수정' if a.apply else '검출'} 완료 — {tot}개 파일")


if __name__ == "__main__":
    main()
