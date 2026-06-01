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
- launchd: `~/Library/LaunchAgents/com.finchmart.seo-refresh.plist` (Hour=17 Min=0). 로드: `launchctl bootstrap gui/$(id -u) <plist>`, 해제: `launchctl bootout gui/$(id -u)/com.finchmart.seo-refresh`.
- Slack webhook: `scripts/.slack_webhook`(gitignore). CLI: `~/.local/bin/claude` v2.1.158 네이티브, 인증은 Keychain 공유.

**전제/한계:**
- 맥 켜짐 + macOS 사용자 **로그인** 상태여야 함(Keychain 접근). 프로젝트가 `/Volumes/External`(외장)이라 볼륨 마운트 필요 — 래퍼가 체크.
- 헤드리스에선 브라우저 MCP 없어 라이브 스마트스토어 크롤이 차단될 수 있음(이미지 미확보). 데이터 진실성(§9)대로 가짜로 안 채움. 개선 여지: CSV의 `대표이미지 URL` 활용.
- 중복 방지: `seo_refresh_log.csv`의 product_id 제외, 다 소진되면 자동 리셋.
- 새 상품 리스트는 `guide/Product_YYYYMMDD_HHMMSS.csv`(한국시간)로 갱신 — 파일명 사전순 최신이 자동 채택.

**Why:** 등록 후 방치된 상품명이 SEO 미달이면 노출 손해. 매일 2개씩 점진 개선. 관련 [[feedback_naver_title_seo_guide]], [[feedback_subagent_env_split]](서브에이전트=Claude Code 전용), [[feedback_slack_delivery]].
