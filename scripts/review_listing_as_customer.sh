#!/usr/bin/env bash
# 상세페이지 고객 관점 리뷰 — Codex 를 한국 20~50대 소비자 페르소나로 세워 읽힌다.
#
#   scripts/review_listing_as_customer.sh <slug> [slug ...]
#
# verify_listing_with_codex.sh(규칙 위반 검사)와 별개 축이다.
# 이건 "살 마음이 드는가 / AI 티가 나는가"만 본다. 업로드를 막지 않는 자문용.
set -euo pipefail

usage() { echo "Usage: $0 <slug> [slug ...]" >&2; exit 2; }
[[ $# -ge 1 ]] || usage

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v codex >/dev/null 2>&1 || {
  echo "Codex CLI is not available on PATH." >&2; exit 127; }

playbook="$project_dir/.claude/agents/listing-customer-review.md"
[[ -f "$playbook" ]] || { echo "Playbook not found: $playbook" >&2; exit 2; }

slug_lines=""
for slug in "$@"; do
  d="$project_dir/output/new-item/$slug"
  [[ -f "$d/${slug}_detail.html" ]] || { echo "detail.html not found in $d" >&2; exit 2; }
  slug_lines+="- $slug: $d"$'\n'
done

report_dir="$project_dir/output/verification"
mkdir -p "$report_dir"
stem="customer_$(date +%Y%m%d_%H%M%S)"
report_path="$report_dir/${stem}_review.md"

# 태그를 벗긴 순수 카피를 따로 만들어 준다 — 고객은 마크업을 보지 않는다.
copy_file="$report_dir/${stem}_copy.txt"
python3 - "$project_dir" "$copy_file" "$@" <<'PYEOF'
import html, pathlib, re, sys
root, out, slugs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3:]
buf = []
for slug in slugs:
    f = root / "output" / "new-item" / slug / f"{slug}_detail.html"
    raw = f.read_text()
    # 줄바꿈·블록 경계를 개행으로 — 안 그러면 "제목설명"으로 붙어 오탐이 난다
    raw = re.sub(r"<br\s*/?>", "\n", raw)
    raw = re.sub(r"</(p|div|h1|h2)>", "\n", raw)
    txt = re.sub(r"<[^>]+>", "", html.unescape(raw))
    txt = "\n".join(l.strip() for l in txt.split("\n") if l.strip())
    buf.append(f"===== {slug} =====\n{txt}\n")
out.write_text("\n".join(buf))
PYEOF

# 프롬프트는 인용 heredoc 으로만 만든다 — 본문에 어떤 문자가 들어가도 셸이 해석하지 못하게.
prompt_file="$report_dir/${stem}_prompt.txt"
{
  printf '%s\n\n%s\n%s\n\n%s\n%s\n\n%s\n%s\n' \
    "You are a CUSTOMER, not a QA checker. Read these listings the way a Korean shopper would." \
    "Persona playbook (follow it):" "$playbook" \
    "Tag-stripped copy (this is what the customer actually reads):" "$copy_file" \
    "SKU folders (images and product_info for reference):" "$slug_lines"
  cat <<'STATIC_PROMPT'
Write the report in Korean. Ground every criticism in a quoted sentence from the copy and
follow it with a concrete replacement sentence the seller could paste in as-is.

What matters, in order:
1. First-screen hook. Read only the top few lines. Would each persona keep scrolling?
   A hook that could be pasted onto any product in the category is a weak hook.
2. AI-written tells. Do not just say it feels artificial - point at the sentence and name the
   pattern: repeated sentence endings, uniform sentence length, stacked adjectives, literary
   connectives, unearned superlatives, formulaic closings, every section padded to exactly
   3 or 4 bullets, sentences ending in a bare noun.
3. Awkward flow. Topic jumps, repeated information across sections, tone whiplash between
   emotional copy and spec lists, transliterated words a Korean reader would not parse.
4. Missing purchase-decision info that would make the persona bounce or send a question.
   Do NOT ask the writer to invent facts - flag it as missing and note whether the owner
   could confirm it from the physical product.
5. Anything that reads as exaggeration and damages trust.

Hard limits:
- Never suggest adding ingredients, health effects, certifications or numbers that are not
  already documented. Rewrites may change wording and structure only.
- At most 5 criticisms per SKU, most damaging first. Drop mere matters of taste.
- Name one thing that already works well, so it can be reused in the next listing.

Do NOT launch a browser or any tooling beyond reading files. Layout, tags, image specs,
banned words and pricing are checked elsewhere - ignore them entirely here.

End with exactly one line, nothing after it:
자연스러움: 상
or
자연스러움: 중
or
자연스러움: 하
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

echo "Copy:    $copy_file"
echo "Report:  $report_path"
tail -1 "$report_path"
