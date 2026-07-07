---
name: project_inventory_list
description: 미리 사입한 재고 관리 엑셀 도구 scripts/build_inventory_list.py — 등록산출물/guide판매목록/수동 3단계로 채워 output/inventory/재고관리_<날짜>.xlsx 생성
metadata:
  type: project
---

**미리 사입(재고 보유)한 제품 관리 리스트** — 판매 등록과 별개로 실제 매입 물량·원가·재고를 추적한다.

**도구:** `scripts/build_inventory_list.py`
- `python3 scripts/build_inventory_list.py <상품ID·슬러그·한글이름>...` → `output/inventory/재고관리_<날짜>.xlsx`
- `--append <기존.xlsx>` 이어붙이기(기존 슬러그 스킵) · `--all` 등록 제품 전체 마스터 · `--list-file` 파일입력
- **3단계 자동채움:** ①등록 산출물(output/new-item/*/product_info.json → 원가·마진·카테고리) ②guide 판매목록(guide/Product_*.csv, 상품ID숫자/이름 → 상품명·판매가·판매URL, 여러 CSV 병합·최신 우선) ③미등록(상품명만 수동행)
- **컬럼:** 사입일·상품명·매입처·용량/규격·원가(현지)·원가통화·판매가(₩)·마진·사입단가(₩)·사입수량·판매수량·현재고(수식=사입−판매,판매공란=0)·유통기한·보관위치·재입고필요·판매URL·카테고리·슬러그·메모

**의미:** `원가(현지)`=매대/리스트 세전(CAD). `사입단가(₩)`=실 취득 landed 단가(세금포함·환율반영). 스토어 노출재고는 실재고와 무관 → 미기입.

**How to apply:** 사용자가 "사입한 제품 관리 리스트", "재고 리스트", 영수증+"사입" 주면 이 도구로 행 추가. 코스트코 원가 리베이트([[feedback_costco_price_adjustment]])·글리치/기프트카드/프로모 실원가 계산은 LEARNED_RULES §19. 일회성 windfall(글리치)은 원가에 baking 말고 메모 플래그, 재입고 원가는 매장가 기준.
