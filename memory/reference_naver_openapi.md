---
name: reference-naver-openapi
description: "playmcp 네이버 MCP 제거 후 대체 — scripts/naver_search.py (네이버 오픈API), 크리덴셜 위치와 영향받은 자동화"
metadata: 
  node_type: memory
  type: reference
  originSessionId: c4a53c03-c133-4174-bcd2-ce2e8dcec220
  modified: 2026-07-28T00:46:52.402Z
---

**playmcp 에서 네이버 MCP(`search_shop`·`find_category`·`datalab_search`)가 제거됐다 (2026-07-27 확인).** 대체 = `scripts/naver_search.py` (네이버 오픈API 직접 호출).

```bash
python3 scripts/naver_search.py shop "검색어" --display 20 --sort asc
python3 scripts/naver_search.py blog|news|cafearticle "검색어"
python3 scripts/naver_search.py shop "검색어" --json      # 원본 JSON
```

- **크리덴셜:** `~/.config/finchmart/naver_api.json` (chmod 600). 리포 커밋 금지 — imgbb 키와 같은 자리.
- 반환 필드가 MCP 와 동일(`lprice`·`mallName`·`link`·`category1~4`·`total`)해서 **[[feedback_competitor_landed_price_compare]] 도착가 규칙과 §10 태그 검증 절차가 그대로 유효**하다. `lprice` = 상품가(배송비 제외) 함정도 동일 — 스크립트가 매 실행 시 경고를 출력한다.
- **수정한 자동화 2건:** `competitor-price-monitor`, `weekly-new-sku-autopilot`([[project_weekly_new_sku_autopilot]]).

**🔑 부수 발견 — 스케줄 작업은 폴더가 있어도 등록 안 돼 있을 수 있다.** `competitor-price-monitor` 는 `~/.claude/scheduled-tasks/` 에 SKILL.md 폴더가 있고 LEARNED_RULES §0-F 에도 "매주 월요일 10:30 운영 중"으로 적혀 있었지만, `list_scheduled_tasks` 에 없어서 **한 번도 안 돌고 있었다**. 2026-07-27 재등록. → **스케줄 작업을 문서화하거나 "돌고 있다"고 보고하기 전에 `list_scheduled_tasks` 로 실제 등록을 확인**할 것.

**🔑 후속 (2026-07-31) — `shop.json` 엔드포인트만 `SE05 (Invalid search api)` 로 사망할 수 있다.** blog/webkr/news/cafearticle 는 영향 없음. §0-A 국내 시세 확인용 상품검색이 막히면 `python3 scripts/kr_price_check.py "<검색어>" [--danawa-only]` 로 대체 — 다나와(search.danawa.com) 1차 + 네이버 blog/webkr 보조. 같은 시기 네이버쇼핑 웹(418 차단)·쿠팡(챌린지 페이지)·11번가·G마켓도 전부 막혀 §0-A 채널로 못 씀. 다나와 가격도 상품가(배송비 미포함)이고 식품 커버리지가 얕을 수 있어 0건이 "국내 미유통" 확정은 아님(§0-A-1 병행). 상세 = docs/LEARNED_RULES.md §0-G.

관련: [[reference_naver_search_mcp]](구 MCP 시절 노하우 — `total`≠태그검색량 등은 여전히 유효) · [[feedback_imgbb_image_hosting]](같은 크리덴셜 디렉터리)
