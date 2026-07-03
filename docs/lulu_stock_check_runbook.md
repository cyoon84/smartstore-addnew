# 룰루레몬 공홈 재고 ↔ 스마트스토어 옵션 점검 (월 1회)

## 왜 완전 자동(헤드리스)이 안 되나
룰루레몬 공홈은 Akamai 봇차단 — 헤드리스 `curl`/`WebFetch` = **403 Access Denied**, 자동화 Chrome도 `Bad Request(GE401001)`.
→ 재고 수집은 **실브라우저(claude-in-chrome / Cowork)** 로만 가능. 비교·리포트는 스크립트가 담당.

## 월간 실행 절차 (트리거가 뜨면 에이전트가)
1. **실브라우저 준비** — claude-in-chrome `list_connected_browsers` → 사용자 실제 Chrome 선택.
2. config 의 각 `lululemon_url` 을 열고(navigate) 아래 JS 실행(javascript_tool) → variants 추출:
   ```js
   (()=>{const ld=[...document.querySelectorAll('script[type="application/ld+json"]')]
     .map(s=>{try{return JSON.parse(s.textContent)}catch(e){return null}})
     .find(j=>j&&j['@type']==='ProductGroup');
    if(!ld) return {error:'no ProductGroup'};
    return (ld.hasVariant||[]).map(v=>{const o=Array.isArray(v.offers)?(v.offers[0]||{}):(v.offers||{});return {color:v.color, sku:v.sku,
      style_color:(v.image||'').split('/lululemon/')[1]||'',
      price:o.price||'',
      availability:(o.availability||'').split('/').pop()};});})();
   ```
   (`python3 scripts/lulu_stock_check.py --fetch-help` 로도 확인)
3. 결과를 `{ "<monitor.id>": [ ...variants... ] }` 형태로 `stock.json` 저장.
4. 대조 + Slack:
   ```
   python3 scripts/lulu_stock_check.py \
     --config output/new-item/lululemon_back_to_life_bottle_18oz/lulu_stock_monitor_config.json \
     --stock /tmp/lulu_stock.json --slack
   ```
   - 🛑 공홈에서 사라짐(단종) → **판매중지 검토**
   - ⚠️ 공홈 품절 → 등록중인데 재고 없음
   - ➕ 공홈 신규 재고(미등록) → 추가 기회
   - exit 2 = 이상 있음 / exit 0 = 정상

## 브라우저가 없을 때
실브라우저가 연결 안 돼 있으면 재고 수집 불가 → 사용자에게 "Chrome(코워크) 열어달라" 요청 후 재시도.

## 모니터 추가
`lulu_stock_monitor_config.json` 의 `monitors[]` 에 새 제품 추가(같은 스키마: id·name·lululemon_url·registered_options[color_ko/color_en/style_color]).
다른 룰루레몬 신규 등록건도 여기 누적하면 한 번에 점검.

## 스케줄
매월 1일 10:00 트리거 → 이 런북 절차 실행 (트리거 프롬프트에 절차 요약 포함).

## 🔑 파이널세일 = 매일 체크 (2026-07-04)
config 의 monitor 에 `check_frequency`: 정가 SKU=`monthly` / **FINAL SALE 색상 포함 SKU=`daily`**. 파이널세일은 재고 소진 시 즉시 사라져(재입고 없음) 팔던 옵션이 갑자기 품절될 수 있으니 매일 확인. daily 대상만 추려 매일, 전체는 월 1회.
