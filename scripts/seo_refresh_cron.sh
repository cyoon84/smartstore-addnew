#!/bin/bash
# launchd 가 매 시 0분에 실행(트리거). 실제 작업은 하루 1번만 — 17시 이후 첫 틱에서.
# 시계 점프·정시 미발화 대비 anacron 방식(하루 1회 가드 + 따라잡기). 인증 Keychain 공유.
set -u
PROJECT="/Volumes/External/claude/smartstore-addnew"
CLAUDE="$HOME/.local/bin/claude"
LOG_DIR="$PROJECT/output/cron_logs"

# ── 하루 1회 가드 (스탬프는 내장디스크) ──
STAMP="$HOME/.finchmart_seo_lastrun"
TARGET_HOUR=17
TODAY="$(date +%Y%m%d)"
HOUR=$((10#$(date +%H)))          # 08/09 8진수 에러 방지
[ "$(cat "$STAMP" 2>/dev/null)" = "$TODAY" ] && exit 0   # 오늘 이미 실행함
[ "$HOUR" -lt "$TARGET_HOUR" ] && exit 0                  # 아직 17시 전
echo "$TODAY" > "$STAMP"                                  # 실행 표시(중복 방지 먼저)

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
