---
name: project_weekly_new_sku_autopilot
description: 매주 목요일 밤 신규 SKU 자동발굴→§0-A→가격산정→카피→일괄엑셀까지 무인 완주하는 스케줄 작업(weekly-new-sku-autopilot)
metadata:
  type: project
---

**무엇:** scheduled-task `weekly-new-sku-autopilot` (매주 목 23:00, cron `0 23 * * 4`). 사람 확인 없이 신규 소싱 후보 발굴 → dedup → §0-A 국내시세 → 가격계산(price_calc.py) → 카피(listing-writer) → 저장 → `build_bulk_excel.py` → `bulk-excel-verifier` 검증까지 끝내, 금요일 아침 사용자가 바로 네이버에 올릴 수 있는 일괄등록 엑셀을 준비한다. 실제 네이버 업로드는 사용자가 직접 함 — 이 작업은 파일만 준비.

**Why:** 2026-07-23 사용자 지시 — "매주 금요일 아침마다 하나씩 바로 내가 올릴수있게 일괄파일을 만들어줘". AskUserQuestion으로 사장님과 함께 다음을 확정:
- 배치 규모: **1~2개 SKU/주** (많으면 리서치·에이전트 비용 커짐)
- §0-A 게이트: **자동 GO** — 경쟁력 있음 판정이면 사람 확인 없이 진행(기존 "매번 명시적 GO 필요" §0-A 원칙의 **이 무인 배치 전용 예외**). 박빙/안됨은 자동 제외, 강행 금지.
- 발굴 소스 3갈래: ①코스트코 sameday(기존 `farmer` 에이전트, 실브라우저, 부서 1개만 가볍게) ②구글검색→쇼핑 기반 트렌드/신제품 리서치 ③이미 등록된 그룹상품 라인업의 새 맛/용량 확장
- 실행 시각: 목요일 밤 23:00 (금요일 아침 전 여유 있게 완성)

**🔑 봇탐지 회피 — 월마트/로블로스 직접 반복크롤 금지, 구글검색→쇼핑 경유 (2026-07-23 사용자 명시):** "월마트사이트나 로블로스는 너무 후벼파면 봇차단 당할수있으니 일단 가격은 구글검색 > shopping으로 해서 뽑아내.. 아무튼 눈치껏 티안나게 잘 접근하도록". 가격 확인은 WebSearch(구글) 로 "<제품명> walmart.ca 가격" 류 쿼리 → 검색 스니펫/쇼핑 카드 우선, 스니펫 부족 시에만 해당 URL 1회 WebFetch(연속 재시도·같은 도메인 3회+ 연속 접근 금지). 코스트코는 기존 farmer 방식(실브라우저) 그대로 쓰되 **부서 1개만**(전수조사 금지) — 코스트코 자체는 사용자가 우려한 대상이 아니었지만 과도한 하베스트를 줄이는 방향으로 같이 제한.

**🔑 자동 GO는 §0-A 시세판단까지만 — 최종 업로드 여부는 항상 사람 (2026-07-23 추가 확인):** 사용자가 "금요일날 아침에 보고 내가 최종 yes/no 할게... 너가 만든 엑셀파일, 상세페이지 보고 바로 올릴건지 수정 필요한지"로 명확히 함. `bulk-excel-verifier` PASS 는 **엑셀 필드 정합성**만 보장하지 상품명·카피가 마음에 들지는 보장 안 함 — 그래서 Slack 보고에 일괄엑셀 경로뿐 아니라 **산출물 폴더 경로(`output/new-item/<slug>/`, detail.html·등록정보.md 포함)도 반드시 같이 준다.** "자동 GO"라는 이름 때문에 업로드까지 자동으로 오해하면 안 됨 — 실제로는 (a)§0-A 경쟁력 판단만 자동 (b)산출물 준비까지 무인 (c)"이대로 쓸지 고칠지"는 사장님이 금요일 아침 리뷰.

**How to apply:**
- 이 작업이 만든 배치(가격산식·§0-A 근거·검증결과)를 볼 때, 사람이 명시적으로 GO 안 준 건이라는 점 인지하고 필요시 재확인.
- 신규 SKU 후보 발굴 로직을 바꾸고 싶으면(배치 크기·소스·자동GO 기준) `~/.claude/scheduled-tasks/weekly-new-sku-autopilot/SKILL.md` 를 직접 수정하거나 `mcp__scheduled-tasks__update_scheduled_task` 사용.
- 로테이션/거절이력은 `output/new-item/_batch/weekly_autopilot_rotation.md` 에 누적(코스트코 부서 순환 + 탈락 후보 재추천 방지).
- 매주 결과(선정 SKU·가격·검증)는 Slack `#new-item` 통합 보고로 온다(다른 매일 재고체크 루틴들과 같은 채널).
- 기존 `/source-launch`(§14, `smartstore-investigate-new-item` 크롤 결과 소비) 와는 다른 흐름 — 이건 자체 발굴부터 무인으로 끝까지 간다는 점이 다름. `farmer`·`market-researcher`·`listing-writer`·`bulk-excel-verifier` 에이전트를 그대로 재사용.

[[project_source_launch_batch]] · [[feedback_domestic_price_check]] · [[feedback_bulk_upload_excel]]
