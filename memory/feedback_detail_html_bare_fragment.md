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

- ✅ 허용: `<p>`, `<strong>`, `<br>`, 이모지, **`<img src="<외부 호스팅 URL>">`** (2026-06-12 확인 — 아래)
- ❌ 금지: `<div>`, `<style>`, `<script>`, `<table>`, `<tr>`, `<td>`, `<article>`, `<section>`, `<ul>`, `<li>`, `<h1>`~`<h6>`, `<head>`, `<body>`, `<html>`, `<!DOCTYPE>`
- 속성(class/style/id) 일체 없음. 인라인 스타일 X (단 `<img>`의 `src`/`alt`는 허용)
- 그리드/테이블/카드 레이아웃 시도하지 않음 — 네이버에서 다 제거됨

> **🔑 `<img>` 태그는 외부 호스팅 URL이면 네이버 에디터에서 생존 (2026-06-12 확인):** 그동안 `<img>`를 금지로 봤으나, `<img src="https://live.staticflickr.com/…_c.jpg">`처럼 **외부 호스팅 직링크**를 넣어 HTML 붙여넣기 하면 네이버 스마트에디터에서 **이미지가 그대로 표시됨**(카페윌리엄 케이스, 사용자 "성공" 확인). 호스팅 이미지 URL이 있으면 detail.html 본문 적절한 위치(보통 헤드라인+영문부제 아래 히어로)에 `<p><img src="URL" alt="상품명"></p>`로 직접 넣어도 된다. `<style>`/`<table>`/`<div>` 류는 여전히 제거되니 금지 유지. (data:/로컬 경로 src는 미검증 — 외부 호스팅 URL만 확인.)

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

- **호스팅 URL이 있으면** `<img src="<호스팅 URL>" alt="상품명">`로 detail.html 본문에 직접 박아도 됨 (2026-06-12 확인 — 네이버 에디터 생존). 적절한 위치: 헤드라인+영문부제 아래 히어로, 또는 섹션 사이.
- 호스팅 URL이 **없으면** 종전대로 박지 말고 이미지 URL을 `<slug>_등록정보.md`에 분리 기록 ([[feedback_naver_detail_format]]).
- 어느 경우든 대표이미지 URL은 `등록정보.md` + product_info `images`/`bulk.rep_image`에도 기록(일괄등록 엑셀 대표이미지 칸 자동 입력, [[feedback_bulk_upload_excel]]).

**Why:** Cowork 프로젝트 설정의 옛 §5가 풀 HTML(`grid-template-columns`·`<table>`·`<article class="option-detail">`)을 지시했는데, 네이버 에디터가 div/style/script/table을 다 제거해서 실제 등록 시 깨졌음. 모바일 dispatch는 워크스페이스 `instructions.md`(`<div>`/`<style>`/`<script>` 금지) 기준으로 베어 fragment를 만들어왔고, 사용자는 이쪽을 정답으로 통일하길 원함.

**How to apply:** 모든 모드(single/group/append)에서 detail.html 작성 시 위 규칙 적용. 그룹 모드라도 옵션별 카드/그리드/테이블 레이아웃 만들지 말고 `<p>` 한두 줄로 응축. 관련: [[feedback_output_location]], [[feedback_dispatch_template]]
