---
name: Skip §0-A domestic price check when "not sold in Korea"
description: 사용자가 "한국에 안 판다"/"국내 미출시"/"한국 미출시" 명시하면 국내 시세 확인 스텝 자동 스킵
type: feedback
originSessionId: 4869fd33-61f1-4706-9ec2-d9ab39aebc17
---
사용자가 메시지에서 **"이건 한국에 안 파는 제품"**, **"국내에 없다"**, **"국내 미출시"**, **"한국 미출시"** 등의 표현으로 명시하면 §0-A 국내 시세 확인 스텝(쿠팡/네이버 검색 → GO/STOP 판단)을 **자동 스킵**하고 책정한 가격 패턴 그대로 진행한다.

**Why:** 비교할 국내 시세 자체가 없으므로 §0-A 절차가 의미 없음. 한정판/미출시 SKU는 비교 가격이 없는 것이 오히려 셀링 포인트. (2026-05-17 Kellogg's Frosted Flakes Cookies & Crème Milkshake 케이스에서 학습 — Cookies & Crème Milkshake 변형은 한국 미출시 한정판이라 쿠팡·네이버 시세 비교 불가.)

**How to apply:** "한국에 안 판다" 류 멘트가 메시지에 있으면 시세 확인 자동 스킵. 단, 보고에는 "국내 미유통 — §0-A 스킵 적용" 1줄 명시. 사용자가 명시 안 한 경우 평소 §0-A 적용.
