---
name: detail-styled-deco-template
description: 상세페이지는 inline CSS 스타일드 데코 가능(네이버가 div/style/h1/h2/말풍선 유지). 브랜드 레드 팔레트+말풍선 헤더+색상별 대표색, 폰트선택은 불가
metadata:
  type: feedback
---

**2026-07-02 확인 — 네이버 스마트에디터가 `<div>` 래퍼 + inline `style=` + `<h1>/<h2>` + border 삼각형(말풍선 꼬리)을 붙여넣기 후 그대로 유지한다** (finchmart_ca, 사용자 직접 확인). 기존 "detail.html 은 베어 fragment(p/strong/br/img)만" 절대규칙([[feedback_detail_html_bare_fragment]])은 **완화** — 사용자가 폰트크기·정렬·색·박스·말풍선 스타일을 요청하면 **inline-CSS 스타일드 상세**로 만든다.

**Why:** 룰루레몬 백투라이프 물병 상세를 꾸미는 과정에서, div/style/h1/h2/box-shadow/border-radius/삼각형꼬리가 전부 네이버에서 살아남는 걸 확인. 브랜드 톤(레드)으로 통일한 스타일드 상세가 베어 fragment보다 전환에 유리.

**🔑 커머스 API 공식 필터로 재확인 (2026-07-05, discussions/3442):** 일괄등록/API 상세설명은 **전역 영향 태그만 차단 — `HTML·META·SCRIPT·STYLE(블록)·BODY·HEAD`.** 허용 태그 공식 목록은 없고 "보안 위험 or 전역 UI 변동" 요소만 제거. 우리 상세는 `div·span·inline style=·h1·h2·img·p·strong·br`만 → 차단 0 → **에디터 붙여넣기(§17)뿐 아니라 일괄등록 API 업로드도 안전.** 차단 "STYLE"=`<style>` 블록 태그, inline `style=` 속성은 별개(전역 영향 없음).

**🔑 매번 `word-break:keep-all` 로 단어 중간 끊김 방지 (2026-07-05 표준 규칙):** 한글은 기본 `word-break`가 글자 단위라 데스크탑에서 **단어가 중간에 끊긴다**. 안쪽 카드 div style 에 **`word-break:keep-all`** 을 넣으면(자식 텍스트 상속) 어절 단위로만 줄바꿈 → 전 스타일드 상세에 항상 포함. 데스크탑·모바일 둘 다 렌더 테스트로 확인(모바일 375px 에서 860px 프레임은 max-width 로 축소, 이미지 max-width:100%, 콘텐츠박스 max-width:640px 축소 → 반응형 OK).

**🔑 가운데정렬 인트로 문단은 균형 `<br>` 로 다듬기 (2026-07-05 르끌레르):** 긴 문장을 큰 폰트(26px)+가운데정렬로 그냥 흘리면 자연 줄바꿈이 들쭉날쭉해 **spacing 이 거슬린다**. 인트로는 **문장마다 비슷한 길이의 2줄로 수동 `<br>`** + **문장 사이 빈 줄**(추가 `<br>` 또는 margin)로 끊고, 필요하면 인트로만 폰트 23px·line-height 1.5 로 살짝 타이트하게. (사용자가 직접 이렇게 다듬어 확정.)

**How to apply:**
- **모든 스타일은 inline `style=` 속성으로만.** `<style>`블록·외부CSS·class/id·`display:flex`(미검증)·`::after`(불가)는 X. 말풍선 꼬리는 `<div style="width:0;height:0;border-left/right:9px solid transparent;border-top:11px solid #e0483f">` 삼각형으로.
- **폰트 선택 불가** — 상세는 font-family 못 고름(가이드 폰트 미적용). 색·레이아웃만.
- 이미지 src 는 외부 호스팅 URL만([[feedback_detail_html_bare_fragment]] 2026-06-12).

**표준 데코 구조 (LEARNED_RULES §17):**
- 래퍼 `<div style="font-size:19px;line-height:1.7;color:#3a3a3a;text-align:center;max-width:860px;margin:0 auto">`
- 헤더: `<h1>`(27~28px 800, 색상명만 대표색) + 레드 액센트바(46×3px `#e0483f`) + `<h2>` 영문부제(14px `#b98c86`)
- 섹션 헤더 = 말풍선(레드 라벨 `border-radius:14px` + 삼각 꼬리)
- 박스: 핵심포인트/이런점이 `#fff7f4`+솔리드`#f3d3cd` · 추천 `#fffaf3`+점선`#f1c6bd` · 용량 pill `#fde8e3`/`#c9352f` · 강조 `<strong style="color:#e0483f">`

**색상명 = 대표색 (레드로 색상명 강조 X — "블랙인데 레드" 아이러니):** 블랙#222 · 화이트#9a9a9a · 아이비그로브#4a7c59 · 로터스라벤더#8a7cc0 · 체리엠버#c0392b · 비치볼블루#2f80d0 · 핑크류#e75f8a~#d96a8a.

**팔레트 출처:** [[reference_design_guide]] (guide/디자인 가이드/). **공지사항은 상세에 붙이지 않음**(사용자 2026-07-02).

**🔑 표준 refine 프레임 확정 (2026-07-03, "앞으로 이걸로 가는거다") — 전 상세 기본:** 레퍼런스 = `output/new-item/post_honey_bunches_of_oats_almonds_1_4kg/*_detail.html`.
- **2겹 프레임(공지와 동일):** 외곽 피치밴드 `background:#fff7f4;padding:32px;border-radius:28px;box-shadow:0 1px 3px rgba(0,0,0,.08)` + 안쪽 흰 라운드카드 `background:#fff;border-radius:24px;padding:46px 34px 42px;box-shadow:0 6px 20px rgba(209,47,42,.06)`. 하드 레드 실선 ❌, 은은한 피치 프레임 ✅.
- 아이브로우 피치 pill(제목 위) + 핵심포인트 2줄행(키워드 볼드↵설명, `border-bottom:#f3d3cd` 구분선) + 이런점이 번호뱃지(레드 원) + 이미지 `border-radius:16px`+그림자 + 말풍선 라벨 그림자.
- **국가 카피 = 캐나다 기준:** 원산지 필드가 미국이어도 상세 아이브로우/카피는 "캐나다 직수입"(소싱), "미국 인기" 류 금지(핀치마트=캐나다 브랜드, 사용자 2026-07-03).
- **글씨 크기 = 공지사항급(2026-07-03 "다 키워 공지랑 같게"):** 카드 본문 base **26px**·h1 **40px**·h2 20px·아이브로우 21px·말풍선라벨 26px·핵심키워드25/설명22·리스트24·번호뱃지 31px원·용량pill 24·알레르기 19. 구 19px 본문은 반려. 상세 세부·전체 CSS는 LEARNED_RULES §17.
