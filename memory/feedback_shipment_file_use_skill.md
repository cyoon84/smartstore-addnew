---
name: feedback-shipment-file-use-skill
description: 발송처리 엑셀은 손으로 만들지 말고 hanmi-flow/epost-flow 의 match_invoices.py 로 — 1건이어도
metadata:
  type: feedback
---

**발송처리 파일을 원본 export 복사로 만들지 않는다. 무조건 스킬의 `match_invoices.py`.**

```bash
python3 ~/.claude/skills/hanmi-flow/scripts/match_invoices.py "<export>" "1111" "<한미_송장엑셀>"
```

송장 엑셀은 한미 배송리스트 상단 **`Tracking Number Download: Excel | CSV`** 로 받는다. 일부만 출고되면
export 를 그 인원으로 필터해 넘긴다.

**Why:** 원본 복사본은 시트명이 `발주발송관리` 로 남고 1행에 네이버 안내문(`◈ 다운로드 받은 파일로…`)이
그대로 있어 **업로드가 거부**된다(`발송처리 이름을 가지는 시트가 존재하지 않습니다`). 스킬은 새 워크북을
만들어 시트명 `발송처리` + 1행 헤더를 보장한다.

**How to apply:** 발송처리 파일이 필요하면 건수와 무관하게 스킬을 부른다. "1건뿐이니 직접" 이라는 판단
자체를 하지 않는다. (2026-09-09 — 9/7 1건을 수동 생성한 방식이 9/9 8건까지 이어져 거부됨. 한미 사이트를
열어 보고 있었으면서 Excel 다운로드 링크를 안 썼다.)

[[feedback_epost_upload_field_rules]] · §18-5 · §18-6
