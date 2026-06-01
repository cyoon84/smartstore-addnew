# 가격 산식 스펙 (price_calc.py 가 구현하는 것)

이 문서는 `scripts/price_calc.py` 각 모드의 산식 근거다. 전체 케이스·예외·학습 맥락은
`LEARNED_RULES.md` (§0~§12) 에 있다. 여기는 코드가 고정한 핵심 공식만 정리.

공통 상수: `NAVER_FEE = 0.066`, `FEE_KEEP = 0.934`.
반올림: `ceil_10` = 10원 단위 올림(§1), `round_100` = 100원 단위 반올림(§5/§6/§11).

## `std` — cost-plus (§1 + §3)
```
cost_with_tax = cost × (1 + tax_rate)        # 세전 원가 + 세금
sell_pre_fee  = cost_with_tax + markup       # 마진
sell_original = sell_pre_fee / 0.934         # 수수료 gross-up
sell_krw      = ceil_10(sell_original × fx)
검산: (sell_krw × 0.934)/fx − cost_with_tax = 실 마진(CAD)
```
markup 의 의미는 "수수료 차감 후 남기고 싶은 순이익". 그래서 gross-up 필수.

## `hst_incl` — 원가에 HST 포함 (§5)
```
cost_with_tax = cost            # 가산 X (이미 포함)
sell_pre_fee  = cost + markup
sell_original = sell_pre_fee / 0.934
sell_krw      = round_100(sell_original × fx)
```
Costco 회원가 등 매대 표시가 세금 포함일 때. 다시 곱하면 원가가 13% 부풀려짐.

## `target_krw` — KRW 목표가 직접 (§6-2)
```
sell_krw       = target           # 그대로 listed price (post-fee)
after_fee_krw  = target × 0.934   # 실수령 (참고)
after_fee_cad  = after_fee_krw/fx # CAD 환산 (참고)
```
gross-up·환산 없음. "네이버에 N원에 올려" 류.

## `target_cad` — CAD 목표가 (§6-3)
```
sell_original = target / 0.934
sell_krw      = round_100(sell_original × fx)
```
"다른 라인업과 가격대 맞추기" 류 — 마진보다 가격 포지셔닝 우선. gross-up 은 적용.

## `reverse` — 목표 KRW + 원가 → 마진 역산 (§6-4)
```
after_fee_krw = target × 0.934
realized_cad  = after_fee_krw / fx
cost_with_tax = cost × (1 + tax_rate)
margin_cad    = realized_cad − cost_with_tax
margin_rate   = margin_cad / realized_cad
```
목표가를 직접 지정하면서 원가도 줬을 때 — listed price 는 target 그대로 두되 실효 마진을
역산해 기록·검산. 마진 코멘트: ≤$5 정상, >$5 는 미출시·한정·콜라보·굿즈면 합리적.

## `pct_net` — "수수료 감안 N%" 순마진 (§11-1)
```
cost_krw = cost × (1 + tax_rate) × fx
sell     = cost_krw / (0.934 − N/100)
sell_krw = round_100(sell)
검산: sell_krw × 0.934 − cost_krw = 순이익,  순이익/sell_krw = N%
```
N% 는 수수료 차감 후 판매가 대비 순마진. 따로 gross-up 안 함(이미 반영).
빠른 공식: 판매가 = 원가KRW ÷ (0.934 − N/100). (N=30→÷0.634, 25→÷0.684, 20→÷0.734)

## `shipping` — 배송비 수량당 단순 곱셈 (§7)
```
shipping_total = qty × unit      # 묶음 할인 없음
```
"배송비 N원 (몇 개당 그런 거 없이)" / "수량당 N원" 패턴. 묶음할인 패턴은 LEARNED_RULES §7 표 참고.

---

## 검증 (회귀 테스트)

`scripts/test_price_calc.py` 가 LEARNED_RULES 의 6개 실제 케이스를 검증한다:
Chosen Foods(§1) ₩20,860 · Aveeno(§5) ₩22,900 · Kellogg(§6-2) ₩8,000 ·
ACE 팀빗(§6-4) 마진 $6.42 · Kinder(§11-1) ₩12,100 · 배송 ₩15,000.
```
python3 scripts/test_price_calc.py
```
