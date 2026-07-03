---
name: reference-naver-search-mcp
description: 네이버 검색 MCP(PlayMCP/isnow890) — §0-A 국내시세·태그 프록시 자동화. search_shop total≠입력화면 검색량 주의
metadata:
  type: reference
---

**연동됨 (2026-07-03, PlayMCP 호스팅):** "네이버 검색 mcp"(isnow890) — 툴 접두어 `mcp__…__NaverSearch-*`. 22개 툴: 검색(웹·뉴스·블로그·카페·**쇼핑**·이미지·지식iN·책·백과·전문·지역) + 데이터랩(검색어트렌드·쇼핑인사이트). github.com/isnow890/naver-search-mcp / playmcp.kakao.com/mcp/154.

**주 용도:**
- **`search_shop`** — §0-A 국내 시세 확인(그동안 한국 커머스 JS렌더+봇차단으로 막혔던 걸 대체). `query`+`display`+`sort(sim/date)`. 응답에 `total`(등록상품수)·items(title·lprice·mallName·brand·category1~4). 채널별 최저가·경쟁 셀러·카테고리 신호 확인.
- 태그 후보의 **인기/경쟁 프록시**로도 씀(각 후보 `search_shop` → `total` 비교).
- `find_category`·`datalab_shopping_*` — 카테고리코드·쇼핑인사이트 트렌드.

**🔑🔑 결정적 주의 — `search_shop` 의 `total` ≠ 태그 입력화면 "월 검색량":**
`total`은 네이버쇼핑 **등록상품 수(공급/경쟁)** 지, 검색 수요가 아니다. 2026-07-03 헤드밴드 케이스에서 `total` 랭킹은 `스포츠헤어밴드`(41만건)를 1위로 봤지만 **실제 입력화면 검색량은 `헬스헤드밴드`(265만)·`테니스헤드밴드`(243만)가 압도** — proxy 가 표기 갈림(`헤드밴드`vs`헤어밴드`)·수요를 완전히 놓침.
→ **`total` 은 죽은 태그(`국내미유통` 13건)·중복(`스포츠머리띠`=`스포츠헤어밴드`) 거르는 용도로만.** 검색량 순위·표기 갈림·최종 통과는 **태그 입력화면에서 확인**이 정답([[feedback_naver_tags]] §10).

**활용 예:** §0-A 는 이제 `search_shop` 로 자동화 — 국내 최저가·룰루레몬코리아 공식가·색상 라인업 차이(한국 Black만)까지 잡아 "접기→니치로 살리기" 전환. [[feedback_lululemon_relist_playbook]] · [[feedback_domestic_price_check]]

**설정:** PlayMCP 호스팅(원격 HTTP MCP, 사용자 카카오 로그인+토큰). 자체 호스팅 대안=`@isnow890/naver-search-mcp`(npx, `NAVER_CLIENT_ID`/`NAVER_CLIENT_SECRET`).

**🔑 한계 2 — `search_shop`은 상품가(lprice)만 주고 배송비는 안 준다 (2026-07-04):** 직구셀러가 §0-D 꼼수(상품가↓+배송↑)를 쓰면 MCP엔 낮은 상품가만 잡혀 **실제 총액을 놓친다**. 예: 바이바잉바이 lprice ₩60,500이지만 실제 배송 ₩39,900 → 총액 ₩100,400. → **§0-A 시세비교는 lprice만 믿지 말고, 유력 경쟁 리스팅은 실제 배송비를 확인(사용자 스크린샷/직접)해 총액으로 비교.** 특히 직구셀러는 숨은 고배송 가정. [[feedback_demand_and_shipping_tactic]]
