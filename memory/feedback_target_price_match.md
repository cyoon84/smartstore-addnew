---
name: ""
metadata: 
  node_type: memory
  originSessionId: 1517accd-0ea4-42c4-b971-bc318f0da6fe
---

사용자가 **"가격 N$로 맞춰"** / **"네이버에 N(원)에 올려"** / **"다른 X 제품과 가격대 맞춰"** 라고 명시하면 원가/마진 계산을 **스킵**하고 N을 **목표가**로 사용한다.

## 1) 단위 해석 (먼저 확정)

1. **"N원" / 숫자만 + "원"** → **KRW (post-fee listed price)** — gross-up·환산 없음
2. **"N$" / "N불"** + 한국 판매가 맥락(네이버 노출가, 라인업 매칭) → **1차 해석 ₩N,000 (천원 단위)** 로 가정. 한 자릿수 $는 한국 일상에서 "N천원"으로 자주 쓰임.
3. **"N CAD" / "N 캐나다 달러"** 또는 원가/마진 맥락 → **CAD**, gross-up·환산 적용
4. 1·2·3 어느 쪽인지 애매하면 **반드시 사용자에게 확인** (잘못 책정하면 마진·전환 양쪽 깨짐)

## 2) KRW 직접 지정

```
sell_price_krw = N                       (사용자 지정 그대로)
실 수령가 = N × 0.934                       (수수료 차감 후)
실 수령가_CAD = (N × 0.934) ÷ FX            (참고용)
```

### 2-1) 목표가 직접 지정 + 원가 있음 → 실 마진 **역산** 기록

목표 판매가를 직접 지정하면서 **원가(±HST)도 함께 준 경우**: cost-plus는 스킵하되 실효 마진을 역산해 등록정보·product_info에 반드시 기록.
```
realized_cad  = (target_krw × 0.934) ÷ FX
cost_with_tax = cost_original × (1 + tax_rate)
실 마진       = realized_cad − cost_with_tax        (+ 마진율, 합리성 1줄 코멘트)
```
마진이 일반 식품대($2~5)를 초과해도 한국 미출시·한정·콜라보·굿즈/컬렉터블이면 가격 탄력성 커서 $6~도 합리적 — 무조건 과하다고 보지 말 것. product_info: `verification.method:"reverse_margin"`, `markup`에 역산값+"역산", `margin_comment`에 합리성 판단. 2026-05-20 Tim Hortons ACE 팀빗 홀더 케이스에서 룰화 (LEARNED_RULES §6-4).

## 3) CAD 목표가

```
target_sell_pre_fee = N CAD
sell_original = N / 0.934                 (gross-up)
sell_krw = round_100(sell_original × FX)
```

**Why:** "라인업 매칭" 같은 요구는 마진보다 **가격 포지셔닝**이 우선. 단위 오해 한 번이 마진/전환 양쪽 다 망치는 비싼 실수 — 2026-05-17 Kellogg's Frosted Flakes 케이스에서 "8$"를 8 CAD로 해석해 ₩9,200 책정 → 사용자가 "그냥 네이버에 8000원" 정정 → 한 자릿수 $ + 한국 판매가 맥락은 ₩N,000 우선 가정으로 룰 보강.

**How to apply:**
- "N$" + 한국 판매가 맥락 → ₩N,000 1차 가정, 의심되면 1줄로 사용자 확인
- "N원" 명시 → KRW post-fee 그대로, gross-up·환산 없음
- "N CAD" 명시 → gross-up 적용
- product_info.json: `pricing_mode: "target_match"`, `target_currency: "KRW"|"CAD"`, `target_value: N`
- "gross-up 빼" 명시한 경우만 gross-up 미적용
