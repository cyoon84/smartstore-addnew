#!/bin/bash
# 일회성(one-shot) 소싱 배치 실행 — 사용자 요청으로 특정 시각(18:00)에 1회만 실행.
# 정규 cron(source_launch_cron.sh)의 "하루 1회 스탬프 가드"를 우회해 강제 실행하고,
# 끝나면 자기 launchd 잡(plist)을 unload+삭제해 다시는 안 돈다.
set -u
PROJECT="/Volumes/External/claude/smartstore-addnew"
INVESTIGATE="/Volumes/External/claude/smartstore-investigate-new-item"
CLAUDE="$HOME/.local/bin/claude"
LOG_DIR="$PROJECT/output/cron_logs"
LABEL="com.finchmart.source-launch-oneshot"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

CRAWL_DATE="$(date +%Y-%m-%d)"
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

self_remove() {
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null
  rm -f "$PLIST" 2>/dev/null
}

if [ ! -d "$PROJECT" ] || [ ! -d "$INVESTIGATE" ]; then
  echo "[$TS] 볼륨 미마운트 — one-shot 중단" >> "$LOG_DIR/launchd.err"
  self_remove; exit 1
fi

CRAWL_DIR="$INVESTIGATE/output/crawl_$CRAWL_DATE"
PRODUCTS="$CRAWL_DIR/products.json"
if [ ! -f "$PRODUCTS" ]; then
  echo "[$TS] one-shot: crawl_$CRAWL_DATE/products.json 없음 — 실행 안 함" >> "$LOG_DIR/source_launch_wait.log"
  python3 "$PROJECT/scripts/slack_notify.py" \
    --text "⚠️ 18:00 일회성 소싱 배치 — 오늘자 crawl_$CRAWL_DATE/products.json 이 없어 실행 못 함 ($TS)" || true
  self_remove; exit 0
fi

LOG="$LOG_DIR/source_launch_oneshot_$TS.log"
cd "$PROJECT" || { self_remove; exit 1; }

"$CLAUDE" -p "/source-launch $CRAWL_DIR" \
  --permission-mode bypassPermissions \
  --output-format text \
  > "$LOG" 2>&1
EXIT=$?

if [ $EXIT -ne 0 ]; then
  python3 "$PROJECT/scripts/slack_notify.py" \
    --text "⚠️ 18:00 일회성 소싱 배치(/source-launch) 실패 (exit $EXIT) — $TS · crawl_$CRAWL_DATE · 로그 $LOG" || true
fi

self_remove
exit $EXIT
