#!/usr/bin/env python3
"""사장님이 매장에서 찍은 사진 전용 — 크롭 없이 크기 조정 + 톤 보정만 한다.

사용:
  python3 scripts/prep_owner_photo.py <원본.jpg> <출력.jpg> [--long 1400]
  python3 scripts/prep_owner_photo.py --batch <원본1> <출력1> <원본2> <출력2> ...

규칙 (LEARNED_RULES §17-3-1, 2026-11-18 사장님 지시):
  - 사장님 사진은 절대 자르지 않는다. 전체 프레임을 비율 그대로 줄인다.
  - 보정은 밝기·대비·채도만. 흰 정사각 캔버스에 붙이기·여백 정리·확대도 금지.
  - 손에 든 컷이 있으면 그게 대표사진.
  - 크롭이 필요한 경우(가격표 노출 §17-2)는 이 스크립트로 하지 말고 사장님께 먼저 묻는다.
  - 공식 흰배경 렌더(월마트·코스트코 이미지)의 여백 정리는 이 스크립트 대상이 아니다.

이 스크립트에는 crop 옵션이 없다 — 일부러 없앴다.
"""
import argparse
import sys
from PIL import Image, ImageEnhance, ImageOps


def prep(src: str, out: str, long_edge: int = 1400) -> tuple[int, int]:
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    s = long_edge / max(w, h)
    if s < 1:
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.08)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Color(im).enhance(1.04)
    # 크롭이 끼어들지 않았는지 비율로 확인
    if abs(im.size[0] / im.size[1] - w / h) > 0.01:
        sys.exit(f"비율이 바뀜 — 크롭 금지 위반: {src}")
    im.save(out, quality=90)
    return im.size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--long", type=int, default=1400, help="긴 변 픽셀 (기본 1400)")
    ap.add_argument("--batch", action="store_true", help="<원본> <출력> 쌍을 여러 개 받는다")
    a = ap.parse_args()
    if len(a.paths) % 2:
        ap.error("<원본> <출력> 쌍으로 넘겨야 한다")
    for i in range(0, len(a.paths), 2):
        size = prep(a.paths[i], a.paths[i + 1], a.long)
        print(f"{a.paths[i + 1]}  {size[0]}x{size[1]}  (원본 비율 유지, 크롭 없음)")


if __name__ == "__main__":
    main()
