---
name: reference_health_canada_fop_warning
description: 캐나다 포장 앞면의 Health Canada "High in / Élevé en" 경고(포화지방·당·나트륨) — 상세 카피엔 안 옮기되 사진에 보이므로 사장님께 고지한다
metadata:
  type: reference
---

캐나다에서 파는 가공식품 상당수는 앞면에 **Health Canada 전면표시(FOP)** 돋보기 마크가 붙는다.

```
🔍 High in / Élevé en
   Sat fat / Gras sat.      (포화지방)
   Sugars  / Sucres         (당)
   Sodium  / Sodium         (나트륨)
   ─────────────
   Health Canada / Santé Canada
```

기준치를 넘는 품목에 **법으로 강제**되는 표시다. 스낵·초콜릿·캔디·가공육·즉석식품에서 자주 본다.

## 우리 워크플로에서 어떻게 다루나

- **상세 카피에는 옮기지 않는다.** 캐나다 규제 표시이지 제품 결함이 아니고, 한국 표시기준과 다르다.
  번역해 넣으면 없는 경고를 우리가 만들어내는 셈.
- **그렇다고 숨기지도 않는다.** `product_info` 의 `label_notes` 에 사실로 기록한다(§9).
- **🔑 사진에는 그대로 보인다.** 앞면 컷을 쓰면 고객 눈에 띄어 문의가 올 수 있다 →
  **등록정보에 한 줄로 고지하고, 지울지 말지는 사장님께 묻는다.** 임의로 지우지도, 그냥 넘어가지도 않는다.
- 지우기로 하면 §17-2 SKU 라벨 제거와 같은 방식(텍스처 복사 + 톤 보정)으로 처리하거나 다른 각도 컷으로 교체.

## 사례

2026-08-10 어웨이크 카페인 초콜릿 8개입 파우치 — 앞면 우상단 `High in Sat fat / Élevé en Gras sat.`
50개입 코스트코 박스와 32개입 혼합 봉지에는 없었다(같은 브랜드라도 **포장 규격마다 다르다** — 컷마다 확인할 것).

[[feedback_price_tag_leak]] · [[feedback_naver_field_limits]]
