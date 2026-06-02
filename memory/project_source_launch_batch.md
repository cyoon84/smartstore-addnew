---
name: project_source_launch_batch
description: /source-launch 배치 커맨드 — investigate products.json → 등록 산출물. 매장수 기반 가격규칙 + 정액배송이 저단가품 경쟁력 죽임
metadata:
  type: project
---

`smartstore-investigate-new-item` 조사 에이전트가 만든 `output/crawl_<날짜>/products.json`(월마트/loblaws/nofrills
채널별 가격 포함 소싱 후보)을 받아 한 번에 여러 SKU 의 스마트스토어 등록 산출물 4종을 만드는 배치 커맨드
**`/source-launch`** (2026-06-01 신설). register-agents 오케스트레이션 그대로 — 메인이 파싱·가격·GO·저장·Slack,
listing-writer 가 카피, market-researcher 가 브랜드품 §0-A.

**가격 규칙(사용자 지정):** 취급 매장 수 = 2곳 이상 → 최고가 + **$1.50** 마진 / 1곳만 → 그 가격 + **$2.00**.
"미취급(PB)"·"동일맛 미취급"·낱봉(다른 규격) 은 카운트 제외. 묶음가 무시·단품가. 세금 자동(스낵 13%/커피·티 0%).
배송비 기본 수량당 ₩15,000(임시·가변). 계산은 `price_calc.py std`.

**Why:** 조사→등록 파이프라인을 반복 실행 가능하게 커맨드화. 가격 산정을 채널 시세에서 보수적으로(최고가=재구매 최악 원가) 도출.

**How to apply:** products.json 들어오면 매장수 산정→최고가/마진→price_calc→PB·캐나다한정NB는 §0-A 스킵·국내유통가능 NB만 조사→listing-writer→`output/new-item/<slug>/` 저장→Slack #new-item.

**자동 스케줄 (2026-06-02 변경, 기존 10시→13:30):** investigate 가 오전 크롤 → 이 배치는 **매일 13:30(오후 1:30)부터** 자동 실행.
launchd `com.finchmart.source-launch`(매시 **:30** 트리거) + `scripts/source_launch_cron.sh`(anacron식 하루1회 가드, `TARGET_HOUR=13`).
스크립트가 오늘자 `crawl_<YYYY-MM-DD>/products.json` 존재를 확인 — 있으면 `claude -p "/source-launch <dir>"`
헤드리스 실행 후 스탬프(`~/.finchmart_source_launch_lastrun`); **없으면 스탬프 안 찍고 종료 → 14:30·15:30… 다음 틱 재시도**.
실패 시 Slack 경보. 대기 로그 `output/cron_logs/source_launch_wait.log`. (seo-refresh·mobile-sync 와 동일 launchd 패턴.)

**핵심 인사이트:** 2026-06-01 첫 배치(15종)에서 정액 배송비 ₩15,000 이 스낵·칩 등 저단가/부피품의 도착가 경쟁력을
죽인다는 게 드러남 — 브랜드품 §0-A 5종 전부 "가격으로 안 됨", 공통 원인이 제품가가 아니라 배송비였음. 국내는
무료배송 보편. **배송비 정책(묶음·무배흡수)이 이 배치의 핵심 레버.** 자세한 내용·룰은 [[LEARNED_RULES]] §14,
가격 패턴은 [[feedback_price_patterns]], 오케스트레이션은 [[project_agents_overview]].
