---
name: project-session-token-slimdown-20260804
description: 2026-08-04 weekly usage 76% 급증 대응 — 영수증폴러 주기 완화 + LEARNED_RULES.md 강제로드 슬림화
metadata:
  type: project
---

2026-08-04, 사용자가 "weekly usage 76%까지 치솟았"다고 지적해 원인을 찾은 결과 두 가지를 확정·실행함.

**원인 1 — `receipt-plus-address-poller` 스케줄 작업이 20분마다(화/금 오후는 1시간) 발동**, 매 발동마다 새 세션이 이 프로젝트의 전체 컨텍스트를 다시 로드. 하루 92개 세션, 290M 토큰, $163.

**원인 2 — `docs/LEARNED_RULES.md`가 `CLAUDE.md`에서 `@docs/LEARNED_RULES.md`로 강제 임포트**되어 이 프로젝트 폴더의 모든 세션(스케줄 작업 포함)마다 전체가 캐시로 재적재됨. 그중 §10(네이버 태그)이 655~1423줄(전체 2395줄의 32%, 약 21K 토큰)로 카테고리별 태그 통과/거부 사례가 계속 누적되는 순수 참고자료였음 — 태그 후보를 실제로 작성할 때만 필요하지 매 세션 필요한 게 아님.

**실행:**
1. `receipt-plus-address-poller` cron을 `*/20 * * * *`(화/금 저빈도 게이트 포함) → `0 */3 * * *`(3시간 간격, 게이트 로직 제거)로 변경.
2. `docs/LEARNED_RULES.md` §10의 카테고리별 누적 사례(680~1420줄)를 `memory/reference_naver_tag_dictionary.md`로 이동, §10에는 핵심 절차(3단계)·차단패턴과 그 memory 파일을 가리키는 포인터만 남김.
3. 결과: LEARNED_RULES.md 강제로드분 55,600 토큰 → 34,674 토큰(-37.6%).

**Why:** CLAUDE.md/LEARNED_RULES.md는 "매번 항상 적용"돼야 하는 안전규칙(§0-∞ 제품명 원본그대로, 가격산식, 카테고리 트리 등)과 "그 작업 할 때만 필요한" 참고자료(태그 카테고리별 사전)가 섞여 있었다. 후자를 강제로드에서 빼도 memory 시스템(MEMORY.md 인덱스 + on-demand Read)이 이미 있어 필요할 때 불러올 수 있어 안전하다고 판단.

**How to apply:**
- **새 태그 카테고리 학습이 생기면 `docs/LEARNED_RULES.md` §10에 직접 쌓지 말고 `memory/reference_naver_tag_dictionary.md`에 같은 형식(`**추가 학습 — <카테고리> (날짜):**`)으로 추가한다.** register/seo-refresh/source-launch 등 실제 태그 후보를 작성하는 작업 시작 시 이 memory 파일을 Read로 불러올 것 — MEMORY.md 인덱스에 등록돼 있음.
- 앞으로 LEARNED_RULES.md나 다른 강제임포트 문서에 "카테고리별/케이스별로 계속 쌓이기만 하는 참고자료" 섹션이 새로 생기면, 처음부터 memory/reference 파일로 분리해 강제로드를 피한다 — 이번처럼 나중에 통째로 이관하는 재작업을 줄인다.
- weekly usage가 다시 튀면 `npx ccusage@latest session --since <YYYYMMDD>`로 세션별 캐시 생성/읽기 토큰을 먼저 확인 — 세션 수가 비정상적으로 많으면(예: 90+) `mcp__scheduled-tasks__list_scheduled_tasks`로 스케줄 작업 빈도부터 의심.
