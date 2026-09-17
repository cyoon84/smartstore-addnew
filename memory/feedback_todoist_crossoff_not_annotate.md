---
name: feedback-todoist-crossoff-not-annotate
description: 사야할 제품들에 "구매완료/사입재고" 표기만 달고 끝내지 말 것 — 살 게 없으면 그 자리에서 complete-tasks
metadata:
  type: feedback
---

**`사야할 제품들` 항목은 "더 살 게 없어진" 순간 바로 `complete-tasks` 로 cross off 한다.**
표기(`✅ 구매완료`·`📦 사입재고 N개`)를 다는 것은 절반이고, 완료 처리까지가 한 동작이다.

cross off 조건 — 셋 중 하나면 즉시:
1. 영수증이 들어와 COGS 가 반영됐다
2. **전량 재고로 충당된다** (부분 재고면 구매분이 남으니 미완료 유지)
3. 이미 다른 주문·배치에서 구매가 끝났다

**Why:** 표기만 남기면 사장님이 "아직 사야 할 것" 으로 읽는다. 목록의 용도가 장보기인데
살 필요 없는 줄이 섞여 있으면 목록이 제 역할을 못 한다.

**🔑 왜 반복되나 (2026-09-16 실사고):** `📦`·`✅` 표기 규칙은 **order-2task-todoist 스킬 3단계**에 있고,
cross off 규칙은 **LEARNED_RULES §20-3** 에 있다. 스킬 체크리스트만 따라가면 표기에서 끊긴다.
§20-3 에 대응하는 memory 파일이 없어 세션 시작 시 로드되지도 않았다 — [[feedback_todoist_due_date_parent_only]]
와 **같은 실패 구조**(LEARNED_RULES 에만 적고 memory 를 안 만들면 다음 세션에서 사실상 안 보인다).

**How to apply:** Todoist `사야할 제품들` 에 서브태스크를 만들거나 갱신할 때마다, 표기를 다는 그 호출
직후에 해당 id 들을 모아 `complete-tasks` 를 부른다. `수취인별 주문` 쪽은 **절대 건드리지 않는다**
(사장님이 포장하며 직접 체크 — §20-3).

[[project_order_settlement]] · [[feedback_todoist_due_date_parent_only]] · [[feedback_todoist_additional_order_dedup]]
