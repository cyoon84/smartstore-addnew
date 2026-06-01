---
name: percent-margin-pricing-pattern
description: "smartstore-addnew — 마진을 정액 CAD 대신 퍼센트(%)로 지정할 때 산식. 특히 \"수수료 감안 N%\" = 판매가 = 원가KRW ÷ (0.934 − N/100)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73ab758e-82cf-4d3c-bda7-8240d530a55c
---

smartstore-addnew 워크플로에서 사용자가 마진을 **퍼센트(%)**로 지정하는 경우의 산식. 기존엔 전부 정액 CAD 마진이었고, 2026-05-25 Kinder Kinderini 케이스가 첫 % 마진 건.

**규칙:** 사용자가 **"수수료 감안하고 N%"** / "수수료 빼고 N%" / "수수료 포함 N% 마진"이라고 하면 N%는 네이버 수수료 6.6% 차감 후의 **순마진(net margin)**이고 **판매가 대비** 비율이다. 이 경우 수수료 gross-up(÷0.934)을 따로 적용하지 않는다 — 0.934가 공식에 이미 들어가 있음.

**산식:**
```
판매가 = 원가KRW ÷ (0.934 − N/100)
원가KRW = cost_original(±HST) × 환율
최종 = round_100(판매가)
검산: 판매가 × 0.934 − 원가KRW = 순이익,  순이익 ÷ 판매가 = N%
```
빠른 분모: N=30 → ÷0.634, N=25 → ÷0.684, N=20 → ÷0.734.

**예시** — Kinder Kinderini 쿠키 (2026-05-25, 원가 6.97 CAD, HST 0%, FX 1,100, 순마진 30%): 원가KRW 7,667 ÷ 0.634 = 12,093 → ₩12,100. 검산 30.04% ✅.

**"마진 N%"만 있고 수수료 관계 불명확하면:** (a) 원가 대비 마크업 `원가×(1+N/100)` 또는 (b) 판매가 대비 마진율 `원가÷(1−N/100)` — 한국 관행상 보통 (b). 어느 쪽이든 산출물에 해석 명시하고 애매하면 확인. "수수료 감안" 표현 나오면 위 순마진 공식으로 확정.

**Why:** 정액 마진과 산식이 완전히 다름. "수수료 감안 N%"를 일반 §1 gross-up과 중복 적용하면 가격이 이중으로 부풀려짐. 자세한 사례·표는 프로젝트 LEARNED_RULES.md §11.

**How to apply:** 마진 입력이 %면 먼저 "수수료 감안" 여부 확인 → 맞으면 `판매가 = 원가KRW ÷ (0.934 − N/100)`, gross-up 별도 적용 금지. 관련 [[smartstore-addnew-price-pattern-dispatch-table]].
