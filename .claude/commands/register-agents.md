---
description: (서브에이전트 모델) 사진/URL+가격으로 등록 4종 산출물 — 시세조사·추출·작성을 전문 에이전트로 분리 실행
argument-hint: [사진/URL + 가격 한 줄 또는 블록]
---

스마트스토어(finchmart_ca) 신규 상품 등록을, **메인 오케스트레이터 + 전문 서브에이전트** 모델로 실행한다. 입력: $ARGUMENTS

기존 `/register` 와 동일한 결과물을 내되, 무거운/격리 가능한 단계는 서브에이전트(`market-researcher`, `product-extractor`, `listing-writer`)에 위임한다. **너(메인)는 오케스트레이터다** — 사용자 대화·GO 게이트·가격계산·파일저장·Slack 은 직접 소유하고, 서브에이전트는 Agent 툴로 호출해 결과만 받는다.

## 실행 환경 — graceful degradation (중요)
이 모델은 두 환경에서 다르게 작동한다:
- **Claude Code (이 CLI / 데스크톱)** — Agent 툴로 서브에이전트를 **실제 spawn**해 격리 실행한다 (아래 절차 그대로).
- **Cowork (모바일 dispatch 착지) 등 spawn 불가 환경** — `.claude/agents/` 와 Agent 툴이 없을 수 있다. 그때는 **메인이 세 에이전트 파일(`market-researcher`·`product-extractor`·`listing-writer`)을 역할 플레이북으로 읽어 같은 순서로 인라인 수행**한다. 컨텍스트 격리는 못 얻지만 역할별 규칙·핸드오프 순서는 동일하게 적용. (Cowork 워크스페이스는 자체 `instructions.md` 의 "실행 엔진" 절을 따른다.)

즉 Agent 툴 사용이 가능하면 위임, 불가하면 인라인 — 산출물·규칙은 어느 쪽이든 동일하다.

## 역할 분담 (절대)
- **메인(너)**: 입력 파싱 / 세금·단위 확인 / **GO 게이트** / `price_calc.py` 가격계산 / product_info.json 조립 / output/ 저장 / Slack 전송.
- **market-researcher**: §0-A 국내 시세 조사 → 경쟁력 판단·선택지 반환 (결정은 너·사용자가).
- **product-extractor**: URL 크롤 → product_info JSON (가격필드 제외) 반환.
- **listing-writer**: 상품명·태그·카테고리·detail.html 작성 후 반환.

## 파이프라인 (순서 고정)

1. **입력 파싱** — 사진/URL, 원가, HST 여부, 배송비, 마진, 모드(single/group). dispatch 한 줄/블록 둘 다 인식. 빠진 항목만 묻고 모드 누락은 single. 세금·단위(CAD/KRW) 애매하면 **여기서 사용자에게 확인**(서브에이전트는 못 물어봄).

2. **(URL 있으면) 추출** — `product-extractor` 에이전트 호출(Agent 툴, subagent_type: product-extractor). 입력: URL. 결과 JSON 받기. 사진만 있으면 메인이 직접 사진 분석.

3. **가격 계산** — 반드시 `scripts/price_calc.py` 의 알맞은 모드(std/hst_incl/target_krw/target_cad/reverse/pct_net/shipping)로. 환율은 현재 시점 확인. 손계산 금지. `sell_krw`·검산값 확보.

4. **국내 시세 확인 (§0-A)** — "한국 미출시" 명시면 스킵하고 "국내 미유통 — §0-A 스킵 적용" 1줄 기록. 아니면 `market-researcher` 호출(입력: 제품명/사양 + 3번의 sell_krw + 배송규칙). 받은 보고서를 사용자에게 그대로 제시하고 **A)진행 B)가격조정 C)접기 → 명시적 GO 를 받는다. GO 전엔 산출물 생성 금지.**

5. **작성** — `listing-writer` 호출(입력: 추출 데이터/사진정보 + 확정 sell_krw·배송·모드 + 슬러그 + 출처 정보). 상품명·태그 후보·카테고리·detail.html fragment 받기.

6. **조립·저장** — 메인이 `output/` 루트에 슬러그 prefix로 저장 후 **`python3 scripts/organize_output.py --apply`** 실행 → `output/new-item/<slug>/` 로 분류:
   - `<ascii_slug>_등록정보.md` (상품명·가격산식·검산·태그·카테고리·배송·이미지 URL 리스트)
   - `<ascii_slug>_detail.html` (listing-writer 의 fragment)
   - `<ascii_slug>_product_info.json` (추출 JSON + price_calc 의 pricing 블록 `--json` 병합)
   같은 슬러그 덮어쓰기. 파일명 ASCII, 한국어는 내용에만.

7. **Slack** — 완료 후 `등록정보.md` 전체를 #new-item 에 전송.

## 주의
- 서브에이전트는 사용자에게 못 묻는다 — 모든 확인/결정/GO 는 메인이 처리.
- 가격은 절대 서브에이전트에 맡기지 않는다. `price_calc.py` 단일 소스.
- 데이터 진실성(§9): 추출 안 된 필드는 비워둔다. 가짜 데이터 금지.
- 진행 상황은 TodoWrite 로 단계별 기록.
