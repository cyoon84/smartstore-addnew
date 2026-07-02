---
name: reference-design-guide
description: 스토어 디자인 가이드 위치와 브랜드 색상 팔레트/폰트/공지 원본 (guide/디자인 가이드/)
metadata:
  type: reference
---

**위치:** `guide/디자인 가이드/` (gitignore 됨, 로컬만)

**파일:**
- `스마트스토어 공지 최종.dc.html` — 공지사항 원본(배송 안내 + 개인통관고유부호 강화). 860px 캔버스. 상세엔 안 붙임(사용자 지시), 별도 이미지/공지로 운용.
- `폰트 비교.dc.html` — 폰트 후보 비교
- `스마트스토어 공지.dc.html` — 공지 이전본
- `assets/logo.png`·`logo-trim.png` — 로고 / `uploads/` 이미지

**브랜드 색상 팔레트:**
- 메인 레드 `#e0483f` · 진한레드 `#c9352f`
- 피치 배경 `#fff7f4` · `#fff1ec` · `#fde8e3` / 크림 `#fffaf3`
- 테두리 피치 `#f3d3cd` · `#f1c6bd`
- 텍스트 `#3a3a3a`(제목) · `#444` · `#555`(본문)
- 노랑 뱃지 `#ffe9b3` / 글자 `#9a6a00` · 링크 블루 `#2f6fd1`

**폰트(공지·배너용, @font-face CDN):** 제목 `YgJalnan`, 본문 `NanumSquareRound`. ⚠️ **상세페이지엔 폰트 적용 불가** — 상세는 색·레이아웃만 이 팔레트로 통일([[feedback_detail_styled_deco_template]]).

**적용:** 상세페이지 스타일드 데코([[feedback_detail_styled_deco_template]], LEARNED §17)는 이 레드 팔레트를 기준으로 통일.
