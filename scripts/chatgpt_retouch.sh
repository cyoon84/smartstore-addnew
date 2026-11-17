#!/usr/bin/env bash
# ChatGPT(Codex, gpt-image)로 매장 사진 톤·제품 비율만 보정한다.
# 사용: scripts/chatgpt_retouch.sh <원본.jpg> <출력.jpg> [rep|detail]
#   rep    : 1000x1000 정사각, 제품이 화면 폭의 약 80%
#   detail : 세로 3:4 (1050x1400), 라벨 면이 화면을 채우게
set -euo pipefail
[[ $# -ge 2 ]] || { echo "Usage: $0 <in.jpg> <out.jpg> [rep|detail]" >&2; exit 2; }
in="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
out_dir="$(cd "$(dirname "$2")" && pwd)"; out="$out_dir/$(basename "$2")"
kind="${3:-rep}"
[[ -f "$in" ]] || { echo "not found: $in" >&2; exit 2; }
if [[ "$kind" == rep ]]; then
  frame="Output a square 1:1 image, 1000x1000. The main product fills about 80% of the frame width, centered."
else
  frame="Output a portrait 3:4 image, 1050x1400. The product face shown in the photo fills the frame so the printed label is large and readable."
fi
work="$(mktemp -d)"
cp "$in" "$work/source.jpg"
codex exec --sandbox workspace-write --skip-git-repo-check -C "$work" -i "$work/source.jpg" - <<PROMPT
Edit the attached store photo with gpt-image and save the result as $work/result.jpg (JPEG).
This is a retouch, not a redesign. Only:
- even out the tone: natural brightness, white balance, mild contrast, no stylized filter
- reframe so the product size and position are consistent: $frame
Keep the product exactly as photographed: same package, logo, colors and every printed word, number and symbol. Do not redraw, translate, sharpen into new letters, or add anything.
Remove any store price tag, shelf label or barcode sticker if visible. Do not add text, props, shadows or backgrounds that were not there.
When done, reply with the saved path only.
PROMPT
[[ -f "$work/result.jpg" || -f "$work/result.png" ]] || { echo "retouch failed: no result in $work" >&2; exit 1; }
python3 - "$work" "$out" <<'PY'
import sys, glob
from PIL import Image
w, out = sys.argv[1], sys.argv[2]
src = (glob.glob(w + "/result.jpg") + glob.glob(w + "/result.png"))[0]
Image.open(src).convert("RGB").save(out, quality=90)
print(out)
PY
