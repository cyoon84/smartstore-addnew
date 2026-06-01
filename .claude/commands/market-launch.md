---
description: 제품 → 네이버 수요·경쟁 조사 + 랭킹 상위 진입 전략 → 전략 기반 상세페이지·제품정보 생성 (바로 업로드용)
argument-hint: [사진/URL/제품명 (+ 선택: 원가·세금·마진·배송)]
---

제품을 받아 **시장조사 + 랭킹 전략**을 세우고, 그 전략대로 **바로 올릴 수 있는 상세페이지·제품정보**를 만든다. 입력: $ARGUMENTS

너는 오케스트레이터다. 무거운/격리 가능한 단계는 서브에이전트에 위임하고, 사용자 대화·GO 게이트·가격계산·저장·Slack 은 직접 소유한다. 서브에이전트 spawn 불가 환경이면 각 에이전트 파일을 역할 플레이북으로 읽어 인라인 수행(graceful degradation, register-agents.md 참고).

## 역할 분담
- **메인(너)**: 입력 파싱 / GO 게이트 / `price_calc.py` / 저장·organize / Slack.
- **market-strategist**(신규): 수요·경쟁구도 조사 + 네이버 랭킹 진입 전략 + listing 재료 반환.
- **market-researcher**: §0-A 채널별 최저가 가격 경쟁력 (가격 관련일 때 보완 호출).
- **product-extractor**: URL 크롤 → product_info JSON.
- **listing-writer**: 전략 재료를 받아 상품명·태그·카테고리·detail 작성.

## 파이프라인 (순서 고정)

1. **입력 파싱** — 사진/URL/제품명, (선택)원가·세금·마진·배송. 세금·단위 애매하면 여기서 확인.

2. **(URL 있으면) 추출** — `product-extractor` 호출 → 제품 사실. 사진만이면 메인이 분석.

3. **시장조사·전략** — `market-strategist` 호출(입력: 제품 식별정보). 반환: 수요 판단 / 경쟁구도 / 랭킹 진입 전략 / listing 재료(키워드축·카테고리·셀링포인트·가격 포지셔닝) / GO 판단.

4. **(가격 관련이면) §0-A + 가격** — 원가가 주어졌으면 `price_calc.py` 로 판매가 계산하고, `market-researcher` 로 채널별 최저가 가격 경쟁력까지 보완 확인. (전략의 "가격 포지셔닝"과 교차검증.)

5. **GO 게이트** — market-strategist 전략 + (있으면) market-researcher 가격 보고를 사용자에게 제시하고 **A)진행 B)전략·가격 조정 C)스킵 → 명시적 GO**. GO 전 산출물 생성 금지. ("한국 미출시"면 §0-A 스킵 표기.)

6. **작성** — `listing-writer` 호출(입력: 추출/사진 데이터 + **market-strategist 의 키워드축·셀링포인트·카테고리·가격 포지셔닝** + 확정 가격·모드·슬러그). 전략을 반영한 상품명·태그·카테고리·detail.html 받기.

7. **저장·정리** — `output/` 루트에 슬러그 prefix 로 `<slug>_등록정보.md`/`_detail.html`/`_product_info.json` 저장 후 **`python3 scripts/organize_output.py --apply`** → `output/new-item/<slug>/` 분류. 등록정보엔 **랭킹 전략 요약**(키워드·차별화·리뷰/가격 전략)도 1섹션 포함.

8. **Slack** — `python3 scripts/slack_notify.py --file <new-item/<slug>/<slug>_등록정보.md>` 로 #new-item 전송(mrkdwn 자동변환).

## 규칙
- 상품명 §5(국가명은 원산지필드), 태그 §8/§10, detail §7 베어 fragment, 그룹 §13-1, 데이터 진실성 §9 그대로.
- 가격은 `price_calc.py` 단일 소스. 전략은 가격을 "포지셔닝 권고"로만 제시.
- 서브에이전트는 사용자에게 못 묻는다 — 모든 확인/GO 는 메인.
- 진행 단계 TodoWrite 기록.
