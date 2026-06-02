---
name: project_mobile_output_sync
description: 매일 23:30 Cowork(smartstore-project) output 산출물을 이 프로젝트 output 으로 no-clobber 복사하는 launchd 동기화
metadata:
  type: project
---

모바일 dispatch(Cowork)로 만든 상세페이지 등 산출물을 데스크톱 프로젝트로 모으는 자동 동기화 (2026-05-30 구축).

**규칙:** `smartstore-project/output/`(Cowork) → `smartstore-addnew/output/`(여기). **여기 없는 파일만 복사, 동일 파일명은 여기꺼 keep**(덮어쓰기 X = rsync `--ignore-existing`). 상품 산출물만(html/json/md/jpg/png), 잡파일(.py/.xlsx) 제외.

**구성:**
- 스크립트: `scripts/sync_mobile_output.sh` (rsync no-clobber, 로그 `output/cron_logs/sync_*.log`).
- launchd: `~/Library/LaunchAgents/com.finchmart.mobile-sync.plist` — **매 시 0분(`Minute=0`) = 매시간 실제 동기화**(가벼워서 무방, 최신 유지). 로드: `launchctl bootstrap gui/$(id -u) <plist>`. (2026-05-31 정시 미발화 대응으로 23:30→매시간 변경. 로그 7일 자동정리.)
- 순수 파일 복사라 Claude/헤드리스 불필요 — 가볍고 무료.

**전제:** 두 볼륨(`/Volumes/External`) 마운트 + 맥 로그인 상태. 스크립트가 SRC/DST 존재 체크. **+ launchd 외장볼륨 접근을 위한 FDA(`/bin/bash`·`/usr/bin/python3`) + plist std경로 내장디스크 필수** — 자세히 [[project_seo_refresh_automation]] "launchd+외장볼륨 필수 설정"(이거 안 하면 exit 78 조용히 실패).

**Why:** 현장 사진은 Cowork dispatch 로 처리(별도 워크스페이스에 저장)되므로, 데스크톱에서 전체 상품을 한곳에서 보려면 모아와야 함. 덮어쓰기 금지로 SEO 리프레시 등 데스크톱 작업물 보호. 관련 [[feedback_subagent_env_split]](output 폴더 두 개), [[project_seo_refresh_automation]](같은 launchd 패턴), [[feedback_output_location]].
