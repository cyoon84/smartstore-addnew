---
name: feedback_costco_stock_check
description: 코스트코 한정품 재고 체크 = 실브라우저(Claude for Chrome) 스케줄 작업. 헤드리스는 Akamai 403, 매장별 재고는 브라우저로 패널 읽기. launchd 불가, scheduled-task로 매일 Slack 보고
metadata:
  type: feedback
---

**코스트코(.ca) 한정/리미티드 제품의 재고를 매일 자동 추적하는 방법** (2026-07-09 발작 캐나다스컵 케이스에서 확립).

**Why:** 코스트코 한정품(리미티드)은 언제 품절/단종될지 모른다 → "아직 살 수 있나 / 어느 매장에 있나"를 놓치면 사입 타이밍을 놓친다. 그래서 데일리 재고 체크가 필요.

**How to apply:**
- **코스트코.ca 는 Akamai 봇차단** — headless/curl/curl_cffi/insane-search engine 은 제품 페이지가 403(또는 흰 화면). **실브라우저(Claude for Chrome = claude-in-chrome MCP)만 통과.** (engine 이 첫 로드는 뚫기도 하나, 매장별 재고 패널은 클릭이 필요해 headless 로는 못 읽음.)
- 🔑 **실브라우저여도 제품 URL 직접 진입은 흰 화면(Akamai) — 사람처럼 홈에서 검색해 들어가야 통과 (2026-07-10 확인, 사용자 지시 "앞으로 계속 이 방식"):** 제품 URL 로 바로 navigate 하면 흰 화면이 반복되지만, **costco.ca 홈페이지 → 상단 "Search Costco" 검색창에 제품명 입력 → Return → 결과 카드의 제품 제목 링크 클릭** 흐름은 정상 통과한다. 스케줄 작업 SKILL.md 도 이 방식으로 갱신함(홈 navigate → 검색 → 결과클릭 → How To Get It 패널). 검색결과 0건이거나 "Show Out of Stock Items" 켜야만 뜨면 = 재고소진/단종 신호 → 🚨 품절 보고.
- **매장별(창고별) 재고**는 로그인 없이(incognito) 도 보인다 — 제품 페이지 "How To Get It" 의 창고명 링크를 클릭 → "Check Nearby Warehouses" 패널이 열리며 "매장이름 (X km) → In Stock at Warehouse" 로 GTA 근처 매장이 뜬다("In Stock at Nearby Warehouses" 필터에 뜨는 = 재고 있는 매장). 패널 스크롤로 전체 확인. **수량·API 불필요, 보이는 In Stock 텍스트만 읽으면 충분.**
- **자동화 = `mcp__scheduled-tasks__create_scheduled_task`** 로 매일(예: `0 8 * * *`), Claude for Chrome 로 페이지 열고 패널 읽어 **Slack #new-item(C0B5F379DSB)** 에 보고. 품절/단종(In Stock 0개·404)이면 🚨 강조. 차단·미연결이면 "수동 확인 필요"(로그인/자격증명 입력은 안전규칙상 금지).
- ⚠️ **launchd 크론은 불가** — 실브라우저를 못 몬다. scheduled-task 는 "앱이 열려 있을 때" 실행되고 Chrome 연결 필요. **첫 실행은 사용자가 "Run now"** 눌러 브라우저·Slack 도구 권한을 미리 승인(안 하면 매 실행 팝업으로 멈춤).
- 브라우저 재변동성: 짧은 시간 반복 재로드하면 Akamai 가 봇으로 막음(흰 화면). 하루 1회 단발 로드는 덜 걸림. 작업 프롬프트에 "흰화면이면 5초 wait 후 최대 2회 재시도" 넣음.
- 🔑 **센서 쿠키 워밍업 = 실브라우저인데도 상세/검색이 막힐 때의 핵심 대응 (2026-07-12 학습, dev.to Akamai 우회글 검토 후):** 실브라우저여도 홈 로드 직후 곧바로 상세/검색으로 넘어가면 Akamai `_abck` 센서 쿠키가 "사람 상호작용"으로 안 채워져 Access Denied 가 뜬다(curl/프록시 문제 아님 = **행동 패턴** 문제). → 홈에서 **검색 전에 8~12초 사람처럼 놀기**: `computer` action:`hover` 로 마우스를 여러 지점 이동 + `scroll` down/up 2~3회 + wait 체류. 그 뒤 검색창 클릭도 천천히(클릭→wait→type→wait), **Return(→/s? 검색결과 페이지)보다 자동완성 드롭다운의 제품 제안 줄을 직접 클릭**하는 게 덜 막힌다. **연속 reload 반복 금지(봇 플래그 키움) — 막히면 wait 후 홈부터 다시.** (dev.to 글의 curl-cffi TLS 임퍼스네이션·레지덴셜 프록시는 headless 스크래핑용이라 "매장별 재고 패널=클릭 필요" 우리 용도엔 안 맞음 — 우리는 이미 최강 방식인 실 Chrome 사용 중, 남은 레버는 행동 인간화뿐.)
- 🔑 **자동완성엔 뜨는데 상세만 Access Denied = "단종" 아니라 "봇차단"으로 구분 보고 (2026-07-12):** 홈 검색 자동완성 드롭다운에 제품명이 뜨면 카탈로그상 살아있다(단종 아님). 그 상태에서 상세/검색결과만 봇차단이면 실패 보고에 "자동완성엔 제품 있음=단종 아님, 상세만 봇차단"을 명시해 오탐(품절 오인)을 막는다.
- 🔑 **재고체크 끝나면 쓴 크롬 탭 다 닫기 (사용자 지시 2026-07-10):** 데일리 작업(및 온디맨드 재고체크)은 마지막에 `tabs_close_mcp` 로 열었던 탭을 닫는다. 재고체크 후 잔여 탭 남기지 않음. (작업 1단계에서 tabId 기억 → 6단계에서 닫기, 실패 종료 시에도.)
- 🔑 **특정 지점(Downsview·Markham) 재고는 "In Stock at Nearby Warehouses" 인근 패널만 믿지 말고 Find 박스로 그 지역을 직접 조회 (2026-07-15 학습, 사용자 정정):** 내 기본 창고(Thorncliffe) 기준 인근 재고 패널은 매장을 **일부만** 보여주고, In Stock 필터를 꺼도 목록에서 특정 매장을 **누락**시킨다 → 실제로는 재고 있는 매장(Markham)을 "품절"로 오판할 수 있다. 반드시 패널의 **`City, State, or Zip` (Find) 박스에 지역명(예 "Markham, ON" / "Downsview, ON") 입력 → Find** 로 그 지역을 중심으로 재조회하면 해당 창고의 정확한 In/Out(예: Markham 8.27km **In Stock at Warehouse**, Downsview 2.91km Out of Stock)이 나온다. **핵심 사입 지점(Downsview·Markham) 판정은 각각 Find 로 직접 확인**하고, Thorncliffe 인근 목록에 안 뜬다고 품절로 단정하지 말 것. (2026-07-15 하리보 해리포터: 인근 패널에 Markham 이 아예 안 떠서 "Downsview·Markham 둘 다 품절"로 오보 → 사용자 "Markham 재고 있는데?" 정정 → Find 로 Markham In Stock 확인.)
- ⚠️ **네트워크/쿠키/토큰/URL 쿼리스트링은 절대 출력 금지** — 콘텐츠 필터에 막힘. 오직 보이는 매장명·In Stock·가격 텍스트만.
- 🔑 **재고체크 대상 = 오직 사용자가 지정한 SKU 만. 내가 브랜드/카테고리로 넣거나 빼지 말 것 (사용자 지시 2026-07-15):** 커클랜드·웨버네추럴(Webber Naturals) 같은 상비 영양제류는 보통 어느 지점이든 상시 재고라 굳이 체크 안 해도 되지만 — **"이 브랜드는 무조건 상시 재고"로 단정하지 말 것.** 그런 상비류도 **잠깐 들어왔다 빠지는 한정 물량**이 있을 수 있다. 그래서 판단 기준은 브랜드가 아니라 **사용자가 체크하라고 명시한 SKU 인가**이다. `costco-stock-check` 루틴 제품 리스트에는 **사용자가 넣으라고 한 것만** 추가하고, 내가 임의로 상비 영양제를 추가하지도, "상시 재고니까"라며 특정 브랜드를 자동 제외하지도 않는다.

**참고 — 헤드리스로 되는 코스트코 API (온라인/상장 재고용, 매장별은 X):**
- 창고 목록: `GET ecom-api.costco.com/core/warehouse-locator/v1/warehouses.json?latitude=&longitude=&limit=50` (header `client-identifier: 7c71124c-7bf1-44db-bc9d-498584cd66e5`). 토론토 창고 예: Downsview 535·Thorncliffe Park 1316·Etobicoke 524·Scarborough 537/595·NW Toronto 1655·Vaughan.
- 온라인 재고: `POST ecom-api.costco.com/ebusiness/inventory/v1/inventorylevels/availability/batch/v2` (header `client-identifier: 481b1aec-aa3b-454b-b81b-48187e28f205`, body `{"distributionCenters":["535",…],"itemNumbers":["01957788"]}`). ⚠️ **item번호는 앞자리 0 포함**(예 `01957788`) — URL 카탈로그ID(4000380401)와 다름(이미지 URL `1957788-894__1` 에서 확인). programTypes 가 비면 창고전용 품목(온라인 재고 없음). **매장별 재고는 이 batch 로 안 나옴**(pickup·비배치 v2 는 403) → graphql/브라우저 필요.

예: 발작 캐나다스컵 907g (코스트코 item 1957788, $26.99) → 매일 8:04 GTA 매장 In Stock 을 Slack 보고. 작업 id `balzac-canadas-cup-costco-stock`. [[reference_balzac_coffee]]
