---
description: price_calc.py 로 스마트스토어 판매가 즉시 계산
argument-hint: [원가/마진/환율/세금 또는 목표가]
---

scripts/price_calc.py 를 사용해 판매가를 계산한다. 입력: $ARGUMENTS

CLAUDE.md §4 의 모드 매핑 표로 알맞은 모드를 고른다 (std / hst_incl / target_krw /
target_cad / reverse / pct_net / shipping). 손계산 금지 — 반드시 스크립트 호출.

- 환율(--fx)은 현재 시점 CAD→KRW 를 확인해서 넣는다.
- 단위(CAD vs KRW)가 애매하면 계산 전에 사용자에게 확인.
- 결과의 sell_krw 와 검산값을 보고하고, 필요하면 --json 으로 product_info 블록을 출력.
