---
name: Smartstore-addnew price pattern dispatch table
description: HST 가산/포함, 배송비 패턴(개당 분배·무배 흡수·추가 흡수) — 사용자가 짧게 말해도 정확한 패턴으로 분류하는 마스터 테이블
type: feedback
originSessionId: 9d77a800-022e-4377-9d3c-7cf1db7d7e4a
---
smartstore-addnew 워크플로에서 사용자가 가격 정보를 짧게 보낼 때, 다음 패턴 분류표로 즉시 산식 확정.

## 공통 산식

```
sell_pre_fee = cost_with_tax + markup + shipping_absorb   (개당 분배 패턴은 shipping_absorb=0)
sell_original = sell_pre_fee / (1 - 0.066)                (네이버 수수료 6.6% gross-up — 메모리 §feedback_naver_fee)
sell_krw = round_100(sell_original × FX_CAD_KRW)
```

## A. HST 가산 여부 (cost_with_tax 결정)

| 사용자 표현 | 산식 | tax_label 표기 |
| --- | --- | --- |
| "$X+HST" / "HST 별도" / "세전 X" / 기본 (명시 없으면 매번 물어봄) | `cost_with_tax = X × 1.13` | `HST 13%` |
| "HST 포함 X" / "tax-in X" / "세금 포함 X" | `cost_with_tax = X` (그대로) | `HST 13% (included in cost)` |
| "HST 0%" / "면세" / "zero-rated" (소스·커피·쿠키 등) | `cost_with_tax = X` | `HST 0%` |
| "GST 5%" (키즈 의류·신발) | `cost_with_tax = X × 1.05` | `GST 5%` |

세금 명시 없으면 매번 묻는다 (§reference_hst_zero_rated).

## B. 배송비 패턴 (shipping_absorb 및 네이버 배송정책 결정)

| 사용자 표현 | shipping_absorb | 네이버 배송정책 | 비고 |
| --- | --- | --- | --- |
| "N개에 X원 배송비" / "개당 X원" | **0** (가격에 안 얹음) | `유료 X원 / 개` (또는 묶음당) | 배송비는 별도 청구. sell_pre_fee = cost_with_tax + markup |
| "실 배송비 N불" + "네이버 무료배송" | **N CAD** | `무료배송` | 실 배송원가 N을 상품가에 흡수. 사용자가 "실 배송비"라고 명시 |
| "물건값에 N$ 추가" + "무료배송" / "배송비 N$ 흡수" / "N$ 얹어서 무배" | **N CAD** | `무료배송` | B와 동일 산식. 사용자 표현만 다를 뿐 같은 패턴 |
| "무료배송" 만 있고 N 없음 | 사용자에게 흡수액 묻는다 | `무료배송` | 흡수 없이 무배는 마진 손해라 거의 안 함 |

B는 모두 메모리 §feedback_free_shipping_absorb 와 동일. 시각적으로 "무배" 노출 효과 (클릭률·전환율↑).

## 처리 시 항상 함께 기록

`product_info.json`:
- `cost_original`, `tax_rate`, `tax_label`, `cost_with_tax`
- `markup`, `shipping_absorb_cad` (없으면 생략 또는 0)
- `sell_pre_fee`, `platform_fee_rate: 0.066`, `sell_original`
- `exchange_rate_cad_krw`, `exchange_rate_date`, `sell_krw_raw`, `sell_price_krw`
- `shipping_policy: { naver_free: bool, absorbed_cad: N, ... }`

`등록정보.md` 가격표에 6단계 표기:
1. 원가 (세전 또는 세포함 명시)
2. HST 처리 (가산 / 포함 / 0%)
3. 마진
4. 배송비 흡수 (해당 시)
5. 수수료 gross-up
6. FX → 100원 라운딩

## 사례

| 상품 | cost | tax | markup | ship | sell_krw |
| --- | --- | --- | --- | --- | --- |
| Granola (2026-05-15) | 10.99 | HST 0% | 5 | +9 (무배) | ₩29,100 |
| Webber Enzymes | 19.99 | HST 13% (별도) | 5 | 3,750원/개 | ₩31,900 |
| Kraft PB Thins | 21.99 | HST 13% (별도) | 5 | 5,000원/개 | ₩34,800 |
| Aveeno Baby Lotion (2026-05-16) | 16.99 | HST 포함 | 3 | 5,000원/개 | ₩22,900 |
| Cetaphil Baby Gift Pack (2026-05-16) | 44.99 | HST 13% (별도) | 5 | +12 (무배) | ₩77,700 |

## How to apply

- 사용자 메시지에서 (1) 세금 단서 (2) 배송 단서를 두 축으로 분류해 산식 즉시 확정.
- 두 축 모두 모호하면 AskUserQuestion으로 둘만 정확히 묻고 진행.
- 라운딩은 별도 지정 없으면 100원 단위 (round-to-nearest).
- 환율은 매 등록 시점 확인 (Yahoo/Wise 일중 평균).

## Why

사용자가 폰에서 짧은 메시지로 워크플로 트리거 시(`feedback_dispatch_template`) "44.99+HST / 마진 5 / 실 배송비 12 / 무배" 같이 한 줄로 보내면 즉시 분류·산출 가능해야 함. 매번 세분 패턴을 재해석하면 답이 흔들림. 이 테이블이 분류 단일 진입점.

세 가지 개별 메모리(§feedback_naver_fee, §feedback_hst_included_cost, §feedback_free_shipping_absorb)는 각 항목 상세 — 본 테이블은 dispatch.
