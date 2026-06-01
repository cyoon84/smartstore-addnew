#!/bin/bash
# 일회성 "깨어있음" 테스트 — 지정 시각에 SEO 리프레시 1회 실행 후 자기 자신(launchd 잡)을 제거.
# launchd가 무인으로 발화하는지(맥이 깨어있는지) 검증용. 발화 즉시 seo_test.log에 기록.
PROJECT="/Volumes/External/claude/smartstore-addnew"
LOG="$PROJECT/output/cron_logs/seo_test.log"
TS="$(date '+%Y-%m-%d %H:%M:%S')"
mkdir -p "$PROJECT/output/cron_logs"
echo "[$TS] ✅ seo-test FIRED (launchd 무인 발화 — 맥 깨어있음 확인)" >> "$LOG"

# 실제 SEO 리프레시 1회 (cron과 동일 래퍼)
/bin/bash "$PROJECT/scripts/seo_refresh_cron.sh"
echo "[$(date '+%H:%M:%S')] seo-test SEO 리프레시 종료(exit $?)" >> "$LOG"

# 일회성: 자기 자신 제거 (plist 삭제 + 언로드 → 내일 재발화 방지)
rm -f "$HOME/Library/LaunchAgents/com.finchmart.seo-test.plist"
launchctl bootout gui/$(id -u)/com.finchmart.seo-test 2>/dev/null
