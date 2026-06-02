---
name: project_seo_refresh_automation
description: 매일 17:00 판매중 상품 2개를 SEO 감사·재생성하는 launchd 자동화 시스템 구성·운영
metadata:
  type: project
---

판매중 상품의 상품명·상세를 네이버 SEO 가이드에 맞게 매일 자동 개선하는 시스템 (2026-05-30 구축).

**흐름:** launchd(매일 17:00) → `scripts/seo_refresh_cron.sh` → `claude -p "/seo-refresh" --permission-mode bypassPermissions`(헤드리스) → 오케스트레이터가 `seo_pick.py`로 최신 `guide/Product_*.csv`에서 12개 랜덤 샘플(판매중·미처리) → `seo-auditor` 병렬 감사 → 위반 점수 상위 2개 → `product-extractor`로 라이브 재추출 → `listing-writer`로 상품명·detail 재생성 → **`output/seo_refresh/<slug>_seo_*`** 저장 + `output/seo_refresh/seo_refresh_log.csv` 기록 → `slack_notify.py`로 #new-item 전송.

**🔴 그룹상품 규칙 (LEARNED_RULES §13-1):** CSV `그룹상품번호` 있는 행 = 그룹상품(상품명 = `<그룹상품명>, <옵션1>, <옵션2>`, 그룹명 생성 후 잠김 [[feedback_naver_group_lock]]). `seo_pick.py` 가 `is_group` 실어보냄 → **상품명 평탄 재작성 금지, detail·태그만 개선, new_title=old_title.** seo-auditor 는 콤마-옵션 형식을 위반으로 안 봄. 출력은 `output/seo_refresh/` 전용 폴더(§13-2).

**🟠 묶음(서로 다른 상품) 규칙 (§13-3):** 그룹 아닌데 종류가 다른 제품이 한 listing 에 묶이면(카푸치노+핫초코 등) **자동 병합 X** → seo-auditor "수동 분리 필요" 플래그, 오케스트레이터는 재생성 건너뛰고 Slack "⚠️ 분리 필요"로 보고. 분리는 셀러 작업.

**구성 요소:**
- 에이전트: `.claude/agents/seo-auditor.md`(신규) + product-extractor + listing-writer 재사용.
- 커맨드: `.claude/commands/seo-refresh.md` (수동 실행 `/seo-refresh` 도 동일).
- 스크립트: `scripts/seo_pick.py`(샘플·중복제외), `scripts/slack_notify.py`(webhook), `scripts/seo_refresh_cron.sh`(래퍼).
- launchd: `~/Library/LaunchAgents/com.finchmart.seo-refresh.plist` — **매 시 0분(`Minute=0`) 트리거**, 래퍼 `seo_refresh_cron.sh`가 **하루 1회 가드**(17시 이후 첫 틱에만 실행, 스탬프 `~/.finchmart_seo_lastrun`, 놓치면 다음 시각 따라잡음). 로드: `launchctl bootstrap gui/$(id -u) <plist>`. ⚠️ **정시(Hour=17) StartCalendarInterval이 이 머신 시계 불규칙으로 미발화하던 것 → 매시간 트리거+가드(anacron 방식)로 변경(2026-05-31).**
- Slack webhook: `scripts/.slack_webhook`(gitignore). CLI: `~/.local/bin/claude` v2.1.158 네이티브, 인증은 Keychain 공유.

**🔴 launchd + 외장볼륨 필수 설정 (2026-05-31 디버깅 확정 — 안 하면 cron 조용히 실패):**
1. **Full Disk Access**(시스템설정→개인정보보호→전체 디스크 접근)에 **`/bin/bash`·`/usr/bin/python3`·`~/.local/bin/claude`** 추가. launchd 자식 프로세스는 기본적으로 `/Volumes/External` 접근이 "Operation not permitted"로 막힘 → FDA 줘야 외장 읽기/쓰기 가능.
2. **plist `StandardOutPath`/`StandardErrorPath`는 내장디스크(`~/Library/Logs/`)에.** 이 std 파일은 launchd 데몬 자신이 여는데 launchd엔 FDA가 없어 외장 경로면 잡이 **exit 78** 실패. (스크립트 자체 로그는 bash가 외장 `output/cron_logs/`에 정상 기록.)
> 증상: `runs`는 올라가는데 아무 일 안 됨 / exit 78. 진단: 홈에 둔 테스트 스크립트로 `ls /Volumes/External` → "Operation not permitted" 확인. Bash 툴 수동 실행은 부모(터미널) FDA로 되지만 **launchd 경로는 별개 — 반드시 launchd kickstart로 실측**.

**전제/한계:**
- 맥 켜짐 + macOS 사용자 **로그인** 상태여야 함(Keychain 접근). 프로젝트가 `/Volumes/External`(외장)이라 볼륨 마운트 필요 — 래퍼가 체크. (+위 FDA·std경로 설정 필수.)
- 헤드리스에선 브라우저 MCP 없어 라이브 스마트스토어 크롤이 차단될 수 있음(이미지 미확보). 데이터 진실성(§9)대로 가짜로 안 채움. 개선 여지: CSV의 `대표이미지 URL` 활용.
- 중복 방지: `seo_refresh_log.csv`의 product_id 제외, 다 소진되면 자동 리셋.
- 새 상품 리스트는 `guide/Product_YYYYMMDD_HHMMSS.csv`(한국시간)로 갱신 — **판매중 ≥ 50 인 '전체 목록' 중 파일명 사전순 최신**을 채택(2026-05-31 가드: 수정한 몇 개만 담긴 부분 export가 더 늦게 올라와도 seo_pick이 거기에 안 속음).

**Why:** 등록 후 방치된 상품명이 SEO 미달이면 노출 손해. 매일 2개씩 점진 개선. 관련 [[feedback_naver_title_seo_guide]], [[feedback_subagent_env_split]](서브에이전트=Claude Code 전용), [[feedback_slack_delivery]].
