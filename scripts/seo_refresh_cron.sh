#!/bin/bash
# 매일 launchd 가 실행 — /seo-refresh 워크플로를 헤드리스로 돌린다.
# 인증은 Keychain 공유(claude -p). 권한은 무인용으로 bypass.
set -u
PROJECT="/Volumes/External/claude/smartstore-addnew"
CLAUDE="$HOME/.local/bin/claude"
LOG_DIR="$PROJECT/output/cron_logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/seo_refresh_$TS.log"

mkdir -p "$LOG_DIR"

# 외장볼륨 마운트 확인 (프로젝트가 /Volumes/External 에 있음)
if [ ! -d "$PROJECT" ]; then
  echo "[$TS] PROJECT 경로 없음(볼륨 미마운트?): $PROJECT" >> "$LOG_DIR/launchd.err"
  exit 1
fi

cd "$PROJECT" || exit 1

"$CLAUDE" -p "/seo-refresh" \
  --permission-mode bypassPermissions \
  --output-format text \
  > "$LOG" 2>&1
EXIT=$?

# 실패 시 Slack 으로 경보 (성공 알림은 /seo-refresh 가 직접 보냄)
if [ $EXIT -ne 0 ]; then
  python3 "$PROJECT/scripts/slack_notify.py" \
    --text "⚠️ SEO 리프레시 cron 실패 (exit $EXIT) — $TS · 로그 $LOG" || true
fi
exit $EXIT
