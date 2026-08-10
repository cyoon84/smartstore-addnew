#!/usr/bin/env bash
# 등록 상세페이지 시각 QA — Codex 를 독립 읽기전용 검사자로 호출한다.
#
#   scripts/verify_listing_with_codex.sh <slug> [slug ...]
#
# bulk-excel-verifier(엑셀 셀 값 대조)와 별개다. 이건 "고객이 뭘 보게 되는가"만 본다.
# 두 검사 다 VERDICT: PASS 를 받아야 사장님께 완료 보고를 할 수 있다.
set -euo pipefail

usage() { echo "Usage: $0 <slug> [slug ...]" >&2; exit 2; }
[[ $# -ge 1 ]] || usage

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v codex >/dev/null 2>&1 || {
  echo "Codex CLI is not available on PATH." >&2; exit 127; }

playbook="$project_dir/.claude/agents/listing-visual-qa.md"
[[ -f "$playbook" ]] || { echo "Playbook not found: $playbook" >&2; exit 2; }

slug_lines=""
for slug in "$@"; do
  d="$project_dir/output/new-item/$slug"
  [[ -d "$d" ]] || { echo "Product directory not found: $d" >&2; exit 2; }
  [[ -f "$d/${slug}_detail.html" ]] || { echo "detail.html not found in $d" >&2; exit 2; }
  slug_lines+="- $slug: $d"$'\n'
done

# 렌더용 미리보기 생성
report_dir="$project_dir/output/verification"
mkdir -p "$report_dir"
stem="visual_$(date +%Y%m%d_%H%M%S)"
preview="$report_dir/${stem}_preview.html"
python3 "$project_dir/scripts/build_preview.py" "$@" --out "$preview" >/dev/null
report_path="$report_dir/${stem}_codex_report.md"

# 이미지를 로컬로 미러링 — Codex 는 read-only 샌드박스라 네트워크가 막혀 있다.
# 원격 URL 을 직접 못 열면 이미지 검사가 전부 UNVERIFIED 로 죽으므로 먼저 받아둔다.
# 🔑 회차별 폴더로 분리 — 공용 폴더에 쌓이면 검사자가 무관한 이미지까지 전부 열어 느려진다
img_dir="$report_dir/_images/${stem}"
mkdir -p "$img_dir"
# 오래된 미러 폴더 정리 (최근 5회분만 유지)
ls -dt "$report_dir"/_images/visual_* 2>/dev/null | tail -n +6 | xargs -r rm -rf
python3 - "$project_dir" "$img_dir" "$@" <<'PYEOF'
import json, pathlib, re, sys, urllib.request
root, img_dir, slugs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3:]
for slug in slugs:
    d = root / "output" / "new-item" / slug
    urls = []
    info = d / f"{slug}_product_info.json"
    if info.exists():
        j = json.loads(info.read_text()).get("images", {})
        urls.append(j.get("rep_image_url"))
        urls += j.get("additional_image_urls", [])
    html = d / f"{slug}_detail.html"
    if html.exists():
        urls += re.findall(r'<img src="([^"]+)"', html.read_text())
    for u in dict.fromkeys(x for x in urls if x):
        f = img_dir / f"{slug[:18]}__{u.split('/')[-1]}"
        if f.exists():
            continue
        try:
            urllib.request.urlretrieve(u, f)
        except Exception as e:
            print(f"MIRROR-FAIL {u} {e}", file=sys.stderr)
PYEOF

# 이전 회차 지적사항이 있으면 이어붙여 "고쳐졌는지" 추적
# 🔑 같은 SKU 를 다룬 보고서만 고른다 — 단순히 최신 파일을 집으면 무관한 SKU 리포트가 딸려가
#    검사자가 "이전 결함과 대조 불가"를 결함으로 올린다 (2026-08-10 발견).
prev=""
for _cand in $(ls -t "$report_dir"/visual_*_codex_report.md 2>/dev/null || true); do
  [[ "$_cand" == "$report_path" ]] && continue
  for _s in "$@"; do
    if grep -qF -- "$_s" "$_cand" 2>/dev/null; then prev="$_cand"; break 2; fi
  done
done
prev_block=""
if [[ -n "$prev" && "$prev" != "$report_path" ]]; then
  prev_block=$(cat <<EOF

Previous verification round (check whether each defect was actually fixed;
call out any regression or unaddressed item explicitly):
$prev
EOF
)
fi

prompt_file="$report_dir/${stem}_prompt.txt"
{
  printf '%s\n\n%s\n%s\n\n%s\n%s\n\n%s\n%s%s\n' \
    "Read-only VISUAL QA. Another agent authored these listings; verify what a customer sees." \
    "Playbook (follow it, but prioritise as below):" "$playbook" \
    "Mirrored images (open THESE; network is blocked, never curl):" "$img_dir" \
    "SKU folders:" "$slug_lines" "$prev_block"
  cat <<'STATIC_PROMPT'
PRIORITY — work through these, then stop and write the report:
1. *** PRICE-TAG LEAK — highest priority, automatic FAIL. ***
   Open every mirrored image and look for ANY readable price: shelf tags (electronic or paper),
   promo tags ("SAVE $3"), unit-price lines ("1.409 per 100 G"), store SKU/barcode labels,
   receipts, price signage. A readable price in a store photo IS OUR PURCHASE COST and must
   never reach the customer. Blurred/unreadable background tags are fine. If unsure whether a
   number is legible, call it FAIL — this leak is irreversible.
   (2026-08-01: a Costco shelf shot with a legible "5.99" shipped past QA; the owner caught it.)
2. Open every mirrored image. For each: is the product identifiable from that photo alone?
   Does the alt text and the "▲" caption in detail.html match what the photo actually shows?
3. PRODUCT WHOLENESS (playbook A-2). Is the product fully inside the frame, or is it cut off?
   A bottle/tube/box whose cap, base or side edge runs off the frame = FAIL. This happens when
   someone crops a tall product to force a squarer aspect ratio. Judge the REP image strictly -
   it is the first thing a shopper sees.
   EXCEPTION: a deliberate label close-up is fine IF the caption says so (e.g. "라벨에 ... 표기되어
   있습니다"). So decide "cut off" vs "close-up" by whether the caption declares it.
4. Blank-padding ratio of BODY images only (rep_image is exempt). >25% = FAIL.
5. Forbidden wording / spec mismatch vs product_info.json.
   NOT-IN-LABEL IS NOT A LIE. Rule 9 forbids inventing product-specific facts (nutrition
   numbers, certifications, origin, efficacy). It does NOT forbid ordinary category knowledge.
   Example that PASSES: pumpkin spice is a North American autumn seasonal flavour. That is
   common knowledge even though the label never says autumn. Check the category_context block
   in product_info.json; if the basis is recorded there, accept it. Ask yourself: is this a
   claim unique to THIS product, or something anyone familiar with the category knows? If the
   latter, pass it. When unsure, report a warning instead of FAIL.
6. COPY-QUALITY PATTERNS (playbook section D). These are mechanical checks, not taste:
   a) em dash U+2014 anywhere in body or alt text = FAIL. Must use commas or split sentences.
   b) Translationese: bullet sentences ending in a bare noun (구성 / 질감 / 조합 / 용량 / 에디션)
      instead of a verb. Also modifier-first order like "라벨 표기 기준 한 병당 30g".
      Spec-block labels such as "중량 · 425g" are exempt - those are not sentences.
   c) Honorific inconsistency inside the recommendation list (좋아하시는 분 vs 선호하는 분).
   d) Filler items in the negative-recommendation block. Ask: would a person matching this
      sentence actually have added the product to cart and then returned it? If not, it is
      filler and must be cut. Fewer items is fine. Known-bad examples: "wants a
      year-round flavour", "uncomfortable with added vitamins", restating a regulatory label
      (Supplemented Food) as if it were a consumer concern.
   e) Store name mismatch: any store named in the eyebrow pill, body, or tags must match
      source_store in product_info.json. If source_store is blank or says needs-checking but
      the page still names a store, that is FAIL. Store-prefixed tags count too.
   f) Emoji: ONLY regional-indicator flag emoji are FAIL (they render as tofu boxes on Naver).
      Single 4-byte emoji are allowed - do not flag them.
   g) Origin: a brand native to its own country (Tim Hortons, BeaverTails) may use the brand
      country as origin without a MADE IN label. Only multinational or contract-manufactured
      brands require the label.
7. KOREAN SPELLING DICTIONARY (playbook section E). Mechanical string match, not judgement.
   Any of these WRONG forms anywhere (title, body, alt, caption, tag candidates) = FAIL.
   Report where it appears.
      켈틀칩 -> 케틀칩        그래놀라 -> 그라놀라      초즌푸드 -> 초슨푸드
      시사이드스파 -> 씨사이드 스파                     디제스티브 -> 다이제스티브
      스머커즈 -> 스머커스    데이비스티 -> 데이비드티  알더블유가르시아 -> RW가르시아
      로우꿀 -> 생꿀          언패스처라이즈드 -> 비가열
   Loanwords NOT in this table must NOT be failed. If a spelling looks suspicious but is not
   listed, raise it as a warning only - the correct form is decided by search volume, not by you.
Network is blocked by design — that is NOT a defect. Judge images from the mirrors only;
never mark an image UNVERIFIED just because the remote URL was unreachable.

Do NOT launch a browser, Playwright or node_repl — none exist here and it burns the run.
LAYOUT IS OUT OF SCOPE: do not check or mention mobile widths, pixel overflow, horizontal
scroll or text clipping. The main agent measures those in a real browser. Never FAIL on them.

Keep the report short. Per SKU: a compact image table, then a defect list.
End with exactly one line: VERDICT: PASS  or  VERDICT: FAIL
STATIC_PROMPT
} > "$prompt_file"
prompt="$(cat "$prompt_file")"

# codex exec 는 자체 타임아웃이 없다 — 네트워크·레이트리밋에 걸리면 무한정 매달린다.
# macOS 에 GNU timeout 이 없으므로 워치독을 직접 건다. CODEX_TIMEOUT 로 조절(기본 600초).
run_codex_with_timeout() {
  local limit="${CODEX_TIMEOUT:-600}"
  codex exec "$@" &
  local pid=$!
  ( sleep "$limit"; kill -9 "$pid" 2>/dev/null ) &
  local watchdog=$!
  disown "$watchdog" 2>/dev/null || true   # 종료 시 "Terminated" 잡음 억제
  local rc=0
  wait "$pid" || rc=$?
  kill "$watchdog" 2>/dev/null || true
  return $rc
}

rm -f "$report_path"
run_codex_with_timeout \
  --cd "$project_dir" \
  --sandbox read-only \
  --ephemeral \
  --output-last-message "$report_path" \
  "$prompt"

[[ -s "$report_path" ]] || { echo "Codex did not produce a report (타임아웃 ${CODEX_TIMEOUT:-600}초 초과 또는 실패). 잠시 후 재시도." >&2; exit 3; }

echo "Preview:  $preview"
echo "Report:   $report_path"

if grep -Eq '^VERDICT: PASS[[:space:]]*$' "$report_path"; then
  echo "VERDICT: PASS"
  exit 0
fi
echo "VERDICT: FAIL"
exit 1
