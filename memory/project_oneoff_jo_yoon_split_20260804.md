---
name: project_oneoff_jo_yoon_split_20260804
description: "조현근·윤기순 네스카페 20개 one-off 분할 구매·발송 — 7/31과 8/4에 5+5씩"
metadata:
  node_type: memory
  type: project
  modified: 2026-07-30
---

# 조현근·윤기순 네스카페 one-off 분할 처리

> 🚨 **한미 송장 생성 중요:** 다음 발주목록 엑셀에 윤기순 주문이 다시 포함되어 있어도
> 윤기순은 2026-08-04 출고분이므로 이번 송장에서는 반드시 제외(ignore)한다.

## Claude가 내일 반드시 알아야 할 핵심

원본 스마트스토어 export에는 아래처럼 수취인별 주문이 각각 10개로 보인다.

- 조현근: French Vanilla 10
- 윤기순: Hazelnut 10

하지만 두 수취인은 사실상 같은 고객의 총 주문이며, 고객이 맛을 섞어서 두 번 나누어
발송해도 된다고 명시했다. 따라서 **원본 수취인별 옵션 배정 그대로 보내면 안 된다.**

고객 요청:

> 헤이즐넛 10개, 바닐라 10개를 주문했으며 섞어서 보내도 되고 총수량만 맞으면 됨.

## 확정된 구매·발송 일정

### 2026-07-31 금요일

- `사야할 제품들` 부모(due 7/31)
  - Hazelnut 5
  - French Vanilla 5
- `수취인별 주문` 부모(due 7/31)
  - 조현근
    - Hazelnut 5
    - French Vanilla 5

### 2026-08-04 화요일

- 별도 `사야할 제품들` 부모(due 8/4)
  - Hazelnut 5
  - French Vanilla 5
- 별도 `수취인별 주문` 부모(due 8/4)
  - 윤기순
    - Hazelnut 5
    - French Vanilla 5

## 절대 규칙

1. 총 구매량과 총 발송량은 각각 Hazelnut 10 + French Vanilla 10이어야 한다.
2. 7/31과 8/4에 각 맛 5개씩 나눈다.
3. due date는 `사야할 제품들`, `수취인별 주문` 최상위 부모에만 둔다.
4. 수취인과 상품 하위 task에는 due date/deadline을 넣지 않는다.
5. 상품명과 `종류: Hazelnut` / `종류: French Vanilla` 옵션을 축약하거나 바꾸지 않는다.
6. 다음 export에 원본 수량 10개씩이 다시 보여도 Todoist를 10+10씩으로 되돌리거나 중복 추가하지 않는다.
7. 실제 구매·발송 완료 여부는 각 날짜의 Todoist 체크 상태를 기준으로 판단한다.

## 현재 Todoist 최종 구조

- 7/31 `사야할 제품들`: 두 맛 5개씩 — **7/30 DoorDash 구매 완료 체크**
- 7/31 `수취인별 주문` → 조현근 → 두 맛 5개씩
- 8/4 `사야할 제품들`: 두 맛 5개씩
- 8/4 `수취인별 주문` → 윤기순 → 두 맛 5개씩

## 2026-07-30 구매·정산 반영

- Food Basics via DoorDash: Hazelnut 5 + French Vanilla 5 전량 입고
- 영수증 순 결제: DoorDash Credits $54.33 + AMEX ****1002 $6.86 = $61.19
- tax $0.57은 DoorDash Credits로 환불
- 크레딧 실현계수 0.7999 적용 실제 현금원가: $50.32
- 7/31 정산 COGS: Hazelnut ₩27,248 + French Vanilla ₩27,247 = **₩54,495**
- 영수증: `output/receipts/2026-07-31/2026-07-30_DoorDash_FoodBasics_Nescafe_5plus5.pdf`
- **8/4 윤기순분 5+5는 아직 미구매이므로 체크하거나 수량을 줄이지 말 것.**
