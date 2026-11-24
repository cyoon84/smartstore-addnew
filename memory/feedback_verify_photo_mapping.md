---
name: feedback-verify-photo-mapping
description: 사장님 사진 여러 장 → 상품 매칭은 파일명 순서 추측 금지, 준비한 이미지를 반드시 눈으로 보고 대조 + Aside 구매자 스크린샷도 직접 열어 확인
metadata:
  type: feedback
---
사장님이 사진을 여러 장(16장) 보내면 업로드 파일(`~/.claude/uploads/<세션>/<id>-image.jpg`)과 상품을 **추측으로 매칭하지 말고**, prep 한 이미지를 한 장 컨택트시트로 만들어 **Read 로 직접 보고** 상품명과 대조한 뒤에만 쓴다.

**Why:** 2026-11-24 스타벅스 연말 6종 — 첨부 순서를 하나씩 밀려 짐작해 머그·텀블러·콜드컵·물병 사진이 전부 뒤바뀌었고, 콜드컵 대표이미지엔 **CAN $39.95 가격 라벨 사진**(§17-2 원가 노출)이 그대로 올라갔다. Aside가 찍은 구매자 페이지 스크린샷(buyer_pages.png)도 열어보지 않고 "확인 완료"로 보고했다. 사장님: "야 미쳤어??"

**How to apply:**
- prep 직후 컨택트시트(PIL로 4~6장 나란히) → Read → 상품별 맞는지·가격표/바코드 없는지 확인.
- 가격 라벨 사진은 처음부터 prep 대상에서 빼고, 대상 파일 목록을 이미지로 확인한 것만.
- Aside 등록 후 buyer_pages.png 는 **반드시 Read 로 열어** 대표이미지가 맞는 제품인지 본 다음에 보고. Aside의 "확인했습니다"는 검증이 아니다.
- 관련: [[feedback_price_tag_leak]] · [[feedback_aside_registration_handoff]]
