#!/usr/bin/env python3
"""상세페이지 4바이트 이모지 → 3바이트(BMP) 안전 기호 치환 (2026-07-31 신설).

배경: 네이버 상세는 **UTF-8 4바이트 문자(U+1F300 이상 + 국기 서로게이트 페어)를 흘린다.**
      국기는 `⊠⊠` 두부박스로, 나머지 그림 이모지는 통째로 사라진다.
      BMP(U+2xxx대, 3바이트)는 정상 렌더 — `☕`·`⚡` 실측 확인(2026-07-31 라이브 2건).

사용:
    python3 scripts/fix_detail_emoji.py --check                 # 전수 점검만
    python3 scripts/fix_detail_emoji.py --apply <slug> [...]    # 지정 슬러그 치환
    python3 scripts/fix_detail_emoji.py --apply --all           # 전 카탈로그 치환
    python3 scripts/fix_detail_emoji.py --diff <slug>           # 치환 전후 미리보기

치환 원칙:
  1) 국기(🇨🇦·🇺🇸 등)는 **삭제** — 대체 기호 없음, `⊠⊠` 의 원인
  2) 의미가 살아나는 것만 안전 BMP 기호로 매핑
  3) 매핑 없는 나머지는 **삭제** (뒤따르는 공백도 정리)
"""
import argparse
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW_ITEM = ROOT / "output" / "new-item"

# ── 안전(3바이트 BMP) 기호로 의미 매핑 ────────────────────────────────
SAFE = {
    # 정보/목록
    "📋": "▪", "📦": "▪", "📏": "▪", "📐": "▪", "🔢": "▪", "📌": "▪",
    "🏷": "▪", "🧾": "▪", "🔖": "▪", "📊": "▪", "📅": "▪", "📆": "▪",
    "🔗": "▪", "📞": "▪", "🔸": "▪", "🔹": "▪", "🔘": "▪",
    # 냉/온
    "🧊": "❄", "🥶": "❄", "🌡": "❄", "🔥": "★", "🌞": "☀", "🌅": "☀", "🌤": "☀",
    # 커피/음료
    "🍵": "☕", "🥤": "☕", "🥛": "☕", "🍶": "☕", "🥃": "☕",
    # 강조/추천
    "👍": "★", "👌": "★", "🎯": "★", "🏆": "★", "🥈": "★", "🏅": "★",
    "💯": "★", "🌟": "★", "✨": "✨", "🎉": "★", "🎊": "★",
    # 주의/금지
    "🚫": "❌", "⛔": "❌", "🚩": "⚠", "💡": "★",
    # 청결/세탁
    "🧼": "♻", "🧴": "♻", "🧺": "♻", "🧹": "♻", "🧽": "♻", "💧": "❄", "💦": "❄",
    # 사람/타겟 — 기호로 못 살리므로 삭제 대상(아래 DROP)
}

# 국기(Regional Indicator) 범위
FLAG = re.compile("[\U0001F1E6-\U0001F1FF]")


def convert(s: str):
    out = []
    changed = {}
    for ch in s:
        if len(ch.encode()) <= 3:
            out.append(ch)
            continue
        if FLAG.match(ch):
            changed[ch] = changed.get(ch, 0) + 1
            continue  # 국기 삭제
        rep = SAFE.get(ch)
        changed[ch] = changed.get(ch, 0) + 1
        if rep:
            out.append(rep)
        # 매핑 없으면 삭제
    t = "".join(out)
    # 이모지 삭제로 생긴 잔여 공백 정리 (여는 태그 직후 공백만 제거 — inline 간격은 보존)
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
        print(f"■ {a.diff}  4바이트 {sum(ch.values())}개 / {len(ch)}종")
        for c, n in sorted(ch.items(), key=lambda x: -x[1]):
            rep = "" if FLAG.match(c) else SAFE.get(c, "")
            print(f"   {c} U+{ord(c):04X} ×{n}  →  {rep or '(삭제)'}")
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
        print(f"{'수정' if a.apply else '검출'} {f.parent.name}: {sum(ch.values())}개({len(ch)}종)")
    print(f"\n{'수정' if a.apply else '검출'} 완료 — {tot}개 파일")


if __name__ == "__main__":
    main()
