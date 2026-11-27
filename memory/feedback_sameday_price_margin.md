---
name: feedback_sameday_price_margin
description: 코스트코 Same-Day(인스타카트) 배달가를 원가로 쓸 때는 마진 10% — 배달가가 이미 매장가보다 약 10% 비싸서 매장가 대비로는 20%
metadata:
  type: feedback
---

원가 소스가 **코스트코 Same-Day(sameday.costco.ca) 배달가**면 마진은 **+10%** 로 잡는다.
매장가 기준일 때의 +20% 와 결과가 비슷하게 맞춰진다.

**Why:** 사장님 2026-11-27 — *"이건 매장이 아니라 배달가격이니까 10% 마진, 그럼 매장가 대비 20%"*.
배달가에 이미 마크업이 붙어 있어서 거기에 20% 를 또 얹으면 이중으로 비싸진다.
([[feedback_store_price_margin_rationale]] 의 매장가+20% 와 같은 목표치를 다른 출발점에서 맞추는 것.)

**How to apply:** 매장 사진·매장가 → +20% / Same-Day·인스타카트 링크 → +10%.
`price_calc.py std --cost <배달가> --markup <배달가×세율×0.1> --tax <세율>`.
세금은 여전히 매번 확인(2026-11-27 리츠 비츠·리츠 퍼지 드리즐 둘 다 0%).
