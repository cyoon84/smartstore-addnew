---
name: feedback_todoist_move_not_delete_recreate
description: Todoist 배치 이동 요청 = 삭제 후 재생성 절대 금지, 항상 parentId 재배정(완료된 태스크는 uncomplete→move→complete)으로만 처리
metadata:
  type: feedback
---

"화요일 거 옮겨라"·"금요일로 넘겨라" 같은 배치 이동 요청을 받으면, 기존 태스크를 지우고 새로 만드는(delete + 재생성) 방식을 **절대 쓰지 않는다.** 항상 **`update-tasks`로 `parentId`만 바꿔서 이동**한다.

**완료(checked) 상태인 태스크는 `update-tasks`의 parentId 변경이 `404 Tasks not found`로 실패한다** — Todoist API가 완료된 태스크의 parent 변경을 막기 때문. 이 경우 순서:
1. `uncomplete-tasks`로 되살린다
2. `update-tasks`로 `parentId`를 새 부모로 바꾼다
3. `complete-tasks`로 다시 완료 처리한다

**적용 사례 (2026-08-20):** 8/18(화) 배치 발송 완료된 수취인 13명 + 구매품목 9건이 계속 진행중인 "사야할 제품들"/"수취인별 주문" 공용 부모 밑에 완료 상태로 눌러앉아 있어서, 부모 due date를 금요일로 옮길 때마다 화요일 완료분까지 같이 딸려 보이는 문제가 생겼다. 해결책은 "8/18(화) 사야할 제품들"·"8/18(화) 수취인별 주문"이라는 **날짜별 아카이브 부모를 새로 만들고, 화요일 몫만 그쪽으로 reparent**하는 것 — 삭제 후 재작성이 아니라 순수 이동. 사용자가 처음엔 삭제 시도(uncomplete 없이 update-tasks 호출 후 404 나는 걸 보고 다른 방법 찾으려 함)를 보고 "지우고 복사하다가 더 일 키우지 말라"고 지적, uncomplete→move→complete 3단계로 깔끔히 해결.

**Why:** 삭제 후 재생성은 완료이력(completedAt)·생성일(addedAt)·연결된 서브태스크 구조를 잃어버릴 위험이 있고, 실수로 원본을 지웠는데 복사가 실패하면 데이터가 통째로 날아간다. reparent는 되돌릴 수 있고 데이터 손실이 없다.

**How to apply:** Todoist에서 "옮겨줘"·"이동" 요청이 오면:
- 활성(미완료) 태스크 → `update-tasks`로 `parentId`만 변경.
- 완료(checked) 태스크 → `uncomplete-tasks` → `update-tasks`(parentId) → `complete-tasks` 3단계.
- 새 배치 아카이브가 필요하면 `add-tasks`로 최상위(또는 적절한 위치) 부모 하나만 만들고, 그 밑으로 옮긴다. 기존 항목의 콘텐츠·서브태스크는 절대 재입력하지 않는다.
