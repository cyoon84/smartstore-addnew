#!/bin/bash
# 모바일 dispatch(Cowork) 산출물을 이 프로젝트 output/ 으로 가져온다.
# 규칙: 여기 없는 파일만 복사(폴더 포함 어디든 같은 파일명 있으면 skip = 여기꺼 keep).
# 복사 후 제품별 폴더로 정리(organize_output.py). 순수 파일 작업 — Claude 불필요. 매일 23:30.
set -u
PROJECT="/Volumes/External/claude/smartstore-addnew"
SRC="/Volumes/External/claude/smartstore-project/output"          # Cowork 워크스페이스
DST="$PROJECT/output"
LOG_DIR="$DST/cron_logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/sync_$TS.log"
mkdir -p "$LOG_DIR"

if [ ! -d "$SRC" ]; then echo "[$TS] SRC 없음(볼륨 미마운트?): $SRC" >> "$LOG"; exit 1; fi
if [ ! -d "$DST" ]; then echo "[$TS] DST 없음: $DST" >> "$LOG"; exit 1; fi

# 이미 있는 파일명(하위 폴더 포함 전체) — 동일 파일명은 여기꺼 keep
EXISTING="$(find "$DST" -type f | sed 's#.*/##' | sort -u)"

copied=0
for f in "$SRC"/*; do
  [ -f "$f" ] || continue
  base="$(basename "$f")"
  case "$base" in
    *.html|*.json|*.md|*.jpg|*.jpeg|*.png) ;;   # 상품 산출물만(.py/.xlsx 등 제외)
    *) continue ;;
  esac
  if printf '%s\n' "$EXISTING" | grep -qxF "$base"; then
    continue   # 이미 있음 → keep
  fi
  cp -p "$f" "$DST/$base" && copied=$((copied+1)) && echo "COPIED $base" >> "$LOG"
done

# 새로 들어온 루트 파일 + 기존 루트 파일을 제품별 폴더로 정리
python3 "$PROJECT/scripts/organize_output.py" --apply >> "$LOG" 2>&1

echo "[$TS] sync 완료 — 새 파일 ${copied}개 복사 후 제품폴더 정리 (project→addnew)" >> "$LOG"
