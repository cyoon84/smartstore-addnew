---
name: feedback_todoist_parent_reuse_verify
description: Todoist 부모 재사용 전 fetch로 현재상태 확인 + reparent 후 projectId 리스팅으로 검증, 애매하면 한번에 확정
metadata:
  type: feedback
---

Todoist "사야할 제품들"/"수취인별 주문" 부모 ID를 이전 세션 요약이나 기억에서 그대로 가져다 쓰지 않는다. **재사용 전에 반드시 `fetch(task:<id>)`로 현재 checked·dueDate 상태를 확인**하고, 완료 상태면 `uncomplete-tasks` → 자식 reparent → `dueString` 갱신 순으로 §20-2 규칙대로 이어 쓴다.

**Why:** §20-2에 이미 "완료 여부 무관 기존 부모 재사용"이 명시돼 있었는데도, 검증 없이 요약 속 ID를 붙였다가 그게 직전 배치용으로 이미 완료 처리된 부모였음을 뒤늦게 발견 — 자식 13개가 고아로 떴다. 고치는 과정에서도 사용자의 짧은 메시지마다 "새로 만들자/재사용하자"를 즉흥적으로 뒤집으며 부모를 여러 번 만들었다 지웠다 했고, 거기에 `fetch(id)`는 존재를 보여주지만 실제 reparent는 안 되는 유령 태스크 버그까지 겹쳐 큰 혼란이 났다.

**How to apply:**
1. 부모 ID를 쓰기 전 항상 `fetch`로 현재 상태 확인 — 기억/요약을 그대로 믿지 않는다.
2. "새로 만들지 재사용할지"가 한 번이라도 헷갈리면 AskUserQuestion으로 그 자리에서 한 번에 확정받는다 — 여러 번 생성·삭제를 반복하지 않는다(구조 변경은 되돌리기 비용이 크다).
3. reparent(부모-자식 이동) 후에는 `find-tasks(projectId, limit:100)` 전체 리스팅으로 검증한다. `fetch(task:<id>)` 단건 조회는 신뢰하지 말 것 — 유령 태스크를 존재한다고 보여줄 수 있다. `update-tasks` 응답에 `parentId` 필드가 안 보이면 그 이동이 실패했다는 신호.
4. 여러 항목 동시 이동(batch update-tasks)이 실패하면 1건씩 개별 호출로 재시도 — 생성 직후 전파 지연으로 배치 호출만 실패하는 경우가 있었다.

관련: [[feedback_todoist_additional_order_dedup]] · [[feedback_todoist_due_date_parent_only]] · [[feedback_todoist_move_not_delete_recreate]]
