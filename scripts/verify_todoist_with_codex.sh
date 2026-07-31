#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <parsed.json> <todoist-draft.json>" >&2
  exit 2
fi

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

resolve_path() {
  if [[ "$1" = /* ]]; then
    printf '%s\n' "$1"
  else
    printf '%s\n' "$project_dir/$1"
  fi
}

parsed_path="$(resolve_path "$1")"
draft_path="$(resolve_path "$2")"

for input_path in "$parsed_path" "$draft_path"; do
  [[ -f "$input_path" ]] || {
    echo "Input file not found: $input_path" >&2
    exit 2
  }
done

command -v codex >/dev/null 2>&1 || {
  echo "Codex CLI is not available on PATH." >&2
  exit 127
}

playbook="$project_dir/.claude/agents/todoist-order-verifier.md"
report_dir="$project_dir/output/verification"
mkdir -p "$report_dir"
draft_stem="$(basename "$draft_path" .json)"
report_path="$report_dir/${draft_stem}_codex_report.md"

python3 "$project_dir/skills/order-2task-todoist/scripts/verify_draft.py" \
  "$parsed_path" "$draft_path"

prompt="$(cat <<EOF
Act as the independent read-only Todoist order QA.

Read and follow this playbook exactly:
$playbook

Compare:
- Parsed source JSON: $parsed_path
- Todoist draft JSON: $draft_path

Do not modify any file. Check every shopping and recipient item, including exact
character-for-character product names and full option strings. End with exactly:
TODOIST_VERDICT: PASS
or
TODOIST_VERDICT: FAIL
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
  echo "Codex did not produce a Todoist verification report." >&2
  exit 3
}

echo "Codex Todoist report: $report_path"
if grep -Eq '^TODOIST_VERDICT: PASS[[:space:]]*$' "$report_path"; then
  echo "TODOIST_VERDICT: PASS"
  exit 0
fi

echo "TODOIST_VERDICT: FAIL"
exit 1
