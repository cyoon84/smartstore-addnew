---
name: naver-detail-text-image-format
description: 네이버 상세페이지 최종 산출물은 standalone HTML 말고 텍스트(붙여넣기용)+이미지(분리) 형식으로 줄 것
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53570034-4f7e-4940-a2fa-27fa0e902192
---

상세페이지 작업의 최종 산출물을 standalone HTML 파일로 끝내지 말 것. 네이버 스마트에디터 ONE은 `<style>` 블록·스크립트를 모두 제거하므로 index.html을 그대로 올리면 디자인이 깨진다. 사용자가 실제로 쓰는 형식은 **"텍스트 + 이미지 분리"** — 섹션별 본문 문구는 붙여넣기용 플레인 텍스트로, 상품 이미지는 CDN URL 목록으로 따로 제공.

**Why:** 사용자가 index.html 산출물을 받고 "이렇게 HTML로 줘도 네이버 상세페이지에 그대로 쓰지도 못해"라고 명시 (2026-05-22). 출력 형식 선택지를 물었더니 "텍스트 + 이미지 분리"를 골랐다.

**How to apply:** index.html + product_info.json은 [[product-detail-page workflow]] 대로 디자인 원본/메타데이터로 계속 만들되, 추가로 `naver_detail_copy.txt` 같은 파일에 ①~⑦ 배치 순서대로 【이미지】URL / 【텍스트】본문 블록을 정리해 제공한다. 텍스트는 마크다운 기호 없이 플레인하게(굵게는 사용자가 에디터에서 직접). 이미지는 §7대로 다운로드하지 말고 CDN URL + 우클릭 저장 안내. 작업 시작 시 출력 형식을 미리 확인하면 재작업을 줄일 수 있다.
