---
name: feedback_ledger_excel_is_source_of_truth
description: 기록은 북키퍼 장부.xlsx 가 정본 — output/ 밑 md 파일에만 적고 장부를 안 건드리면 두 곳이 어긋난다
metadata:
  type: feedback
---

**사장님이 "장부"라고 하면 `/Volumes/External/claude/profit-expense-tracker/장부.xlsx` 다.**
`output/inventory/*.md` 같은 보조 노트가 아니다.

## 사고 (2026-08-19)

우버 그로서리 reimbursement 를 `output/inventory/우버_그로서리_reimbursement.md` 와
장부의 **「우버이츠 reimburse 대기」 탭** 두 곳에서 관리하고 있었다.
나는 md 만 갱신하고 장부는 손도 안 댔다.

- 사장님: *"장부 우버이츠 reimburse 대기가 마지막 entry에 8/13이 마지막인데, 맞아?"*
- 나: md 를 보고 **"다 들어가 있습니다"** 라고 답함 → 사장님 *"안들어갔는데 뭔 헛소리야?"*
- 실제로 장부 탭엔 **6건 누락**. 그중 2건은 md 에 CONFIRMED 로 적혀 있으면서 장부엔 아예 없었다
  (8/8 Walmart $197.00 · 8/9 Sephora $183.06 — 금액도 큰 건).

**두 번 틀렸다.** ①장부 대신 md 를 갱신 ②사장님이 짚어줬는데도 md 를 근거로 "들어갔다"고 우김.

## 규칙

- **기록은 장부.xlsx 에 넣는다.** md/마크다운은 절차 설명·읽는 법 안내용이지 데이터 저장소가 아니다.
- **같은 데이터를 두 곳에 두지 않는다.** 이미 두 곳이면 하나를 폐기 안내로 바꾸고 정본을 명시한다.
- **"장부에 있냐"는 질문엔 장부 파일을 직접 열어서 답한다.** 다른 파일을 근거로 답하지 않는다.
- 상태가 필요하면 **엑셀 안에서 보이게** 한다 — 우버 탭은 Note 컬럼 앞에
  `[확정 YYYY-MM-DD · order XXXXX]` / `[대기 · 확정메일 미수신]` 토큰을 붙였다.
- ⚠️ 우버 탭 Note 의 **order# 는 지우지 말 것** — `gmail-receipt-collector` 가 그 문자열로 라벨 게이팅을 한다.

[[project_bookkeeper_expense_tracker]] · [[feedback_uber_grocery_reimbursement_tracking]]
