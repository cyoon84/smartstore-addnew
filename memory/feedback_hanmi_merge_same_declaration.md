---
name: feedback-hanmi-merge-same-declaration
description: 한미 업로드용은 신고 내용(HS·영문명·브랜드·단가·팩수량)이 같으면 상품번호가 달라도 한 줄로 합쳐 수량 합산
metadata:
  type: feedback
---

한미 양식의 품목 단위는 네이버 상품번호가 아니라 **신고 내용**이다.
`convert.py` 가 수취인별로 `(HS CODE, 상품명(영문), 브랜드, 단가, 팩수량)` 을 키로 묶어 수량을 합산한다.
매핑이 없는 상품은 합치지 않고 `MISSING:` 으로 잡힌다.

**Why:** 2026-11-20 KAL SE MI — 팀홀튼 머그 캐나다/토론토가 둘 다 `CERAMIC MUG 16OZ` $20,
오레오 메이플/화이트퍼지가 둘 다 `COOKIE` $5 인데 상품번호가 달라 4줄로 나갔다.
사장님: *"CERAMIC MUG 16OZ 상품명, 단가 같으니까 수량 2로 해서 한줄로 / cookie도"*.

**How to apply:** 출력 xls 를 손으로 고치지 말고 `convert.py` 를 쓴다(§18-5 와 같은 원칙).
단 **합치는 건 한미 신고서뿐** — Todoist·정산·파이널 체크(§2.5)는 [[feedback_product_name_verbatim]]
대로 원본 상품명을 그대로 갈라서 본다. 실물은 캐나다/토론토, 메이플/화이트퍼지를 구분해 담아야 한다.
