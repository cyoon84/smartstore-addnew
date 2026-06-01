---
name: Free shipping with absorbed shipping cost in product price
description: 사용자가 "무료배송 + N$ 흡수" / "배송비 N$ 상품가에 얹어서 무료배송" 표현 쓸 때 가격 산식에 N$를 포함하고 네이버에는 무료배송으로 등록
type: feedback
originSessionId: 88728986-54e2-45dd-b576-202219534974
---
네이버 스마트스토어 등록 시 사용자가 "무료배송으로 등록 + N CAD를 상품가에 얹어서 책정" 패턴을 지정하면 다음과 같이 처리.

**가격 산식:**
```
sell_pre_fee = (cost_pre_tax × (1 + tax_rate)) + markup + shipping_absorb
sell_original = sell_pre_fee / (1 - 0.066)        (네이버 수수료 gross-up)
sell_krw = round_100(sell_original × FX)
```

`shipping_absorb` (보통 9 CAD 등)는 **상품가에 흡수**되고, 네이버 등록 시 배송 정책은 **"무료배송"**으로 설정.

**예시:** Kirkland × Nature's Path Granola — 원가 10.99 CAD + HST 13% + 마진 5 + 배송흡수 9 = 26.4187 CAD → ÷0.934 → 28.2855 CAD → × FX → KRW 라운딩.

**Why:** 네이버에서 "무료배송" 노출은 클릭률·전환율을 끌어올림. 배송비는 카트 단계에서 할인처럼 보이는 효과가 있음. 이 패턴을 쓰는 상품군은 "1개당 합계 가격이 시각적으로 명료해야" 하는 경우 (예: 배송비 별도 부담을 꺼리는 식품·일반 카테고리).

**How to apply:**
- 사용자 메시지에 "무료배송", "무배", "배송비 N$ 상품가에 얹어"/"흡수" 같은 표현이 있으면 즉시 이 패턴 적용
- `product_info.json`에 `shipping_absorb_cad`, `shipping_policy.naver_free: true` 명시
- `등록정보.md` 가격표에 "배송비 흡수: +N CAD" 행 추가하고 배송정책 섹션은 "**무료배송**"
- 다른 가격 정책(4개당 15,000원 등)이 명시되지 않은 한 자동으로 이 패턴 유지
- 라운딩은 사용자가 별도 지정 없으면 100원 단위 (round_100)
