#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <bulk-excel.xlsx> <slug> [slug ...]" >&2
  exit 2
}

[[ $# -ge 2 ]] || usage

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
excel_arg="$1"
shift

if [[ "$excel_arg" = /* ]]; then
  excel_path="$excel_arg"
else
  excel_path="$project_dir/$excel_arg"
fi

[[ -f "$excel_path" ]] || {
  echo "Excel file not found: $excel_path" >&2
  exit 2
}

command -v codex >/dev/null 2>&1 || {
  echo "Codex CLI is not available on PATH." >&2
  exit 127
}

verifier_file="$project_dir/.claude/agents/bulk-excel-verifier.md"
[[ -f "$verifier_file" ]] || {
  echo "Verifier playbook not found: $verifier_file" >&2
  exit 2
}

slug_lines=""
for slug in "$@"; do
  product_dir="$project_dir/output/new-item/$slug"
  [[ -d "$product_dir" ]] || {
    echo "Product directory not found: $product_dir" >&2
    exit 2
  }
  slug_lines+="- $slug: $product_dir"$'\n'
done

report_dir="$project_dir/output/verification"
mkdir -p "$report_dir"
excel_stem="$(basename "$excel_path" .xlsx)"
report_path="$report_dir/${excel_stem}_codex_report.md"

prompt="$(cat <<EOF
You are the independent, read-only QA verifier for this repository.

First read and follow this playbook exactly:
$verifier_file

Verify this bulk-upload workbook:
$excel_path

Expected SKU folders:
$slug_lines
Rules:
- Do not edit, regenerate, rename, or delete any repository file.
- Inspect the workbook and source artifacts directly.
- Run only read-only checks.
- If an external image URL cannot be checked because network access is unavailable,
  mark that item UNVERIFIED and make the overall result FAIL; do not guess.
- Return the exact structured SKU-by-SKU PASS/FAIL format required by the playbook.
- End with exactly one machine-readable line:
  VERDICT: PASS
  or
  VERDICT: FAIL
EOF
)"

rm -f "$report_path"
codex exec \
  --cd "$project_dir" \
  --sandbox read-only \
  --ephemeral \
  --output-last-message "$report_path" \
  "$prompt"

[[ -s "$report_path" ]] || {
  echo "Codex did not produce a verification report." >&2
  exit 3
}

echo "Codex verification report: $report_path"

if grep -Eq '^VERDICT: PASS[[:space:]]*$' "$report_path"; then
  echo "VERDICT: PASS"
  exit 0
fi

echo "VERDICT: FAIL"
exit 1
