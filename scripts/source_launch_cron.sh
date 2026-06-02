#!/bin/bash
# launchd 가 매 시 30분에 실행(트리거). 실제 작업은 하루 1번만.
# 흐름: investigate 가 오전에 크롤 → 이 스크립트는 13:30부터 매시 점검,
#       오늘 날짜 crawl_<YYYY-MM-DD>/products.json 이 있으면 /source-launch 배치 실행.
#       아직 없으면(폴더 미생성) 스탬프를 안 찍고 종료 → 14:30·15:30… 다음 틱에서 재시도.
#       성공/실행 착수하면 스탬프 = 오늘 → 그날은 더 안 돈다.
# 시계 점프·정시 미발화 대비 anacron 방식(하루 1회 가드 + 따라잡기). 인증 Keychain 공유.
set -u
PROJECT="/Volumes/External/claude/smartstore-addnew"
INVESTIGATE="/Volumes/External/claude/smartstore-investigate-new-item"
CLAUDE="$HOME/.local/bin/claude"
LOG_DIR="$PROJECT/output/cron_logs"

# ── 하루 1회 가드 (스탬프는 내장디스크) ──
STAMP="$HOME/.finchmart_source_launch_lastrun"
TARGET_HOUR=13          # 13:30(오후 1:30) 첫 실행 — 트리거는 매시 30분, 13시 전 틱은 가드
TODAY="$(date +%Y%m%d)"
CRAWL_DATE="$(date +%Y-%m-%d)"
HOUR=$((10#$(date +%H)))          # 08/09 8진수 에러 방지

[ "$(cat "$STAMP" 2>/dev/null)" = "$TODAY" ] && exit 0   # 오늘 이미 처리함
[ "$HOUR" -lt "$TARGET_HOUR" ] && exit 0                  # 아직 10시 전

TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

# 외장볼륨 마운트 확인 (두 프로젝트 모두 /Volumes/External)
if [ ! -d "$PROJECT" ] || [ ! -d "$INVESTIGATE" ]; then
  echo "[$TS] 볼륨 미마운트? PROJECT=$PROJECT INVESTIGATE=$INVESTIGATE" >> "$LOG_DIR/launchd.err"
  exit 1   # 스탬프 안 찍음 → 다음 틱 재시도
fi

# ── 오늘 날짜 crawl 폴더 점검 ──
CRAWL_DIR="$INVESTIGATE/output/crawl_$CRAWL_DATE"
PRODUCTS="$CRAWL_DIR/products.json"
if [ ! -f "$PRODUCTS" ]; then
  echo "[$TS] crawl_$CRAWL_DATE/products.json 아직 없음 (hour=$HOUR) — 다음 시각 재시도" >> "$LOG_DIR/source_launch_wait.log"
  exit 0   # 스탬프 안 찍음 → 11시·12시…에 다시 확인
fi

# ── 찾음: 오늘 처리 착수 표시(중복 방지 먼저) 후 배치 실행 ──
echo "$TODAY" > "$STAMP"
LOG="$LOG_DIR/source_launch_$TS.log"
cd "$PROJECT" || exit 1

"$CLAUDE" -p "/source-launch $CRAWL_DIR" \
  --permission-mode bypassPermissions \
  --output-format text \
  > "$LOG" 2>&1
EXIT=$?

# 실패 시 Slack 경보 (성공 보고는 /source-launch 가 직접 #new-item 으로 보냄)
if [ $EXIT -ne 0 ]; then
  python3 "$PROJECT/scripts/slack_notify.py" \
    --text "⚠️ 소싱 배치(/source-launch) cron 실패 (exit $EXIT) — $TS · crawl_$CRAWL_DATE · 로그 $LOG" || true
fi
exit $EXIT
