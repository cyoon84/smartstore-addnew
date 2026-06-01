---
name: detail-html-bare-fragment-format
description: detail.html은 데스크톱·모바일 dispatch 둘 다 네이버 에디터 붙여넣기용 베어 fragment 형식 (p/strong/br + 이모지)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0ed2f71d-65d3-4eac-96e5-69bfb42ba44c
---

`<slug>_detail.html`은 풀 HTML 페이지가 아니라 **네이버 스마트스토어 에디터에 그대로 붙여넣는 베어 fragment**다. 데스크톱·모바일 dispatch 동일.

## 허용 / 금지

- ✅ 허용: `<p>`, `<strong>`, `<br>`, 이모지
- ❌ 금지: `<div>`, `<style>`, `<script>`, `<table>`, `<tr>`, `<td>`, `<article>`, `<section>`, `<ul>`, `<li>`, `<h1>`~`<h6>`, `<img>`, `<head>`, `<body>`, `<html>`, `<!DOCTYPE>`
- 속성(class/style/id) 일체 없음. 인라인 스타일 X
- 그리드/테이블/카드 레이아웃 시도하지 않음 — 네이버에서 다 제거됨

## 섹션 순서

1. 헤드라인 — `<p><strong>🏷️ <상품명></strong></p>`
2. 영문 부제 한 줄 ([[feedback_detail_english_subtitle]])
3. `<p><br></p>`
4. 상품 소개 1~2 문단
5. `<p><br></p>`
6. 핵심 포인트 (이모지 + `<strong>` 키워드 + 설명) 4~6개
7. `<p><br></p>`
8. (그룹/append만) 옵션·용량 — 한 줄 응축 ([[feedback_group_detail_condensation]])
9. `<p><br></p>`
10. "이런 점이 좋아요" 4~6개
11. `<p><br></p>`
12. "이런 분들께 추천해요" ✓ 4~6개

## 제외

- 🚚 배송 안내 ([[feedback_detail_skip_shipping_outro]])
- 마무리 인사 한 줄
- 스펙 테이블·footer
- 활용 팁·레시피 ([[feedback_no_usage_tips]])
- 상품명에 들어간 출처/매장 태그 반복 ([[feedback_no_source_repeat]])

## 이미지

`<img>` 태그로 박지 않음. 이미지 URL은 `<slug>_등록정보.md`에 분리 ([[feedback_naver_detail_format]]).

**Why:** Cowork 프로젝트 설정의 옛 §5가 풀 HTML(`grid-template-columns`·`<table>`·`<article class="option-detail">`)을 지시했는데, 네이버 에디터가 div/style/script/table을 다 제거해서 실제 등록 시 깨졌음. 모바일 dispatch는 워크스페이스 `instructions.md`(`<div>`/`<style>`/`<script>` 금지) 기준으로 베어 fragment를 만들어왔고, 사용자는 이쪽을 정답으로 통일하길 원함.

**How to apply:** 모든 모드(single/group/append)에서 detail.html 작성 시 위 규칙 적용. 그룹 모드라도 옵션별 카드/그리드/테이블 레이아웃 만들지 말고 `<p>` 한두 줄로 응축. 관련: [[feedback_output_location]], [[feedback_dispatch_template]]
