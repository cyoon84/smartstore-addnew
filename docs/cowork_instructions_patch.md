# Cowork 프로젝트 설정 교체 텍스트

Cowork 앱 → smartstore-addnew 프로젝트 → 프로젝트 설정(Instructions)에서 아래 두 블록을 그대로 교체하세요.

---

## §3 폴더/파일 규칙 — 교체본

```
3. 폴더/파일 규칙

- 저장 위치: /Volumes/External/claude/smartstore-project/output/ (워크스페이스 안의 output 폴더, 데스크톱·모바일 dispatch 동일)
- 폴더 분리 X, 평탄 구조 — 슬러그를 prefix로 사용:
  - <ascii_slug>_detail.html
  - <ascii_slug>_product_info.json
  - <ascii_slug>_등록정보.md
  - 참고 이미지: <ascii_slug>_*.jpg 등 같은 폴더에
- ASCII 파일명 필수. 한국어는 파일 내부 콘텐츠에만.
- 같은 그룹은 같은 슬러그로 덮어쓰기 (append 시 동일 파일 재작성)
- ~/Downloads 사용 금지, 중첩 슬러그 폴더 만들지 않음
```

## §4 워크플로우 9단계 — 교체본

```
9. /Volumes/External/claude/smartstore-project/output/ 안에
   <slug>_detail.html + <slug>_product_info.json + <slug>_등록정보.md 평탄 저장
```

(앞 1~8단계는 그대로 둠)

## §5 HTML 포맷 — 교체본 (dispatch 형식으로 통일)

기존 §5는 풀 HTML 페이지(`grid-template-columns`, `<table>`, `<article class="option-detail">`)를 지시하는데, dispatch는 네이버 에디터에 그대로 붙여넣는 베어 fragment를 만듭니다. 데스크톱도 같은 형식으로 통일.

```
5. HTML 포맷 (detail.html — 네이버 에디터 붙여넣기용 베어 fragment)

- 허용 태그: <p>, <strong>, <br>. 이모지 자유롭게.
- 금지 태그: <div>, <style>, <script>, <table>, <tr>, <td>, <article>, <section>, <ul>, <li>, <h1>~<h6>, <img>, <head>, <body>, <html> (네이버에서 다 제거됨)
- 풀 HTML 문서 만들지 않음. <!DOCTYPE>, <head>, <body> 래퍼 없음. <p> fragment를 평탄하게 나열.
- CSS·class·style·id 속성 전부 없음.
- 이미지는 HTML에 박지 않음 — 별도 URL 리스트로 등록정보.md에 분리 ([[feedback_naver_detail_format]] 룰).

섹션 순서 (모드 공통):
1) 헤드라인 — <p><strong>🏷️ <상품명></strong></p>
2) 영문 부제 — <p><영문 풀네임></p>
3) <p><br></p> 공백
4) 상품 소개 — 1~2 문단
5) <p><br></p>
6) 핵심 포인트 — 이모지 + <strong>키워드</strong> + 설명 (4~6개)
7) <p><br></p>
8) (그룹/append 모드만) 옵션·용량 안내 — 카드 캡션 수준 한 줄로 응축 ([[feedback_group_detail_condensation]]). 그리드·테이블·아티클 사용 X. 옵션별 <p> 한두 줄로.
9) <p><br></p>
10) "이런 점이 좋아요" — 이모지 + <strong>키워드</strong> + 한 줄 (4~6개)
11) <p><br></p>
12) "이런 분들께 추천해요" — ✓ + 한 줄 (4~6개)

제외:
- 🚚 배송 안내 섹션 ([[feedback_detail_skip_shipping_outro]])
- 마무리 인사 한 줄 (자동 삽입 금지)
- 스펙 테이블·하단 footer
- 활용 팁·레시피 ([[feedback_no_usage_tips]])
```

## §6~§9 — 그대로 둠

기존 §6 product_info.json 구조, §7 이미지 처리, §8 크롤링, §9 데이터 진실성은 변경 없음.

---

## 왜 바뀌었나

기존 §3·§4가 `~/Downloads/<ascii_slug>/` 식 **Downloads 밑 중첩 슬러그 폴더**를 지시했는데, 모바일 dispatch는 워크스페이스 안의 `instructions.md`(`output 폴더 안에 저장`)를 따라서 `~/smartstore-addnew/output/`에 평탄 저장하고 있었음. 두 경로가 갈리면서 데스크톱 결과물이 Cowork 임시 outputs로 새거나 Downloads의 다른 위치로 흘러가는 일이 발생함. 모바일 동작을 정답으로 채택해서 통일.

워크스페이스 `instructions.md`도 이미 같은 규칙으로 업데이트 완료.
