---
name: feedback_aside_registration_handoff
description: 리스팅 워크플로 변경(2026-11-17) — 메인은 카피·가격·로컬 이미지·엑셀·Codex QA까지, 네이버 이미지업로드·일괄등록·마무리는 aside exec 에 넘긴다
metadata:
  type: feedback
---

사진/가격을 받으면 메인(Claude Code)은 상품명·상세·product_info·등록정보·일괄엑셀을 만들고 Codex QA 까지 마친다.
**사진은 imgbb 에 올리지 않는다** — 밝기 보정·정사각 크롭한 로컬 jpg 만 만들고, 상세 HTML 과 `bulk.rep_image`/`add_images`
에는 `{{IMG_REP}}` 같은 placeholder 를 넣는다(`product_info.images.local_files` 에 매핑).

Codex `VERDICT: PASS` 후 `aside exec` 로 Aside 를 불러 `docs/ASIDE_PLAYBOOK.md` 대로:
네이버 일괄등록 화면 이미지업로드 → shop-phinf URL 로 placeholder 치환 → `build_bulk_excel.py` 재생성 →
엑셀 업로드 → 태그·브랜드 카탈로그·묶음배송 등 마무리 → 구매자 페이지 확인 → 상품번호 기록·Slack.

**Why:** 사장님 지시 "기존 워크플로에서는 사진으로 제품명·상세 작업(사진 올리는거 말고), codex QA 까지 마무리되면
aside 호출해서 네이버 일괄등록·이미지 업로드·나머지 다 하라". Claude Code 는 네이버 셀러센터·상품페이지에 접근이 막혀 있고
(reference_smartstore_page_access_blocked), Aside 는 사장님 로그인 브라우저를 쓴다.

**🔑 실행은 항상 `aside exec --permission full-access` (사장님 승인 2026-11-17).** 기본(Guard)은 프로젝트 밖 폴더 접근 때
사용자에게 묻는데, CLI 세션엔 물을 상대가 없어 `/Volumes/External/claude/smartstore-addnew/` 읽기·쓰기가 전부 막힌다
(첫 시도 세션 nP3RJLPQDwJvIREL 이 플레이북도 못 열고 종료). Aside 에는 폴더 허용목록 설정이 없다(`aside settings` 는
save-sessions·computer-use·analytics 뿐). 프롬프트에는 작업 범위를 프로젝트 폴더 + 네이버 셀러센터로 못박는다.

**🔑 이미지 = ChatGPT 보정 (2026-11-17 추가).** 대표·상세 이미지는 `scripts/chatgpt_retouch.sh <원본> <출력> rep|detail`
(Codex 경유 gpt-image)로 **톤과 제품 크기·위치만** 맞춘다. 글자·로고·포장은 그대로, 가격표는 제거. 이 보정은 메인 단계에서 하고,
Codex QA 에 원본 대비 라벨 글자가 다시 그려지거나 바뀌지 않았는지 대조시킨다. (11/11 "AI 재생성 금지" 는 imagegen 으로 사진을
새로 그린 데 대한 지적이었고, 이번 지시는 보정 범위만 허용한 것 — 결과에 글자 변형·"AI 티"가 보이면 PIL 보정본으로 되돌린다.)
> 실사례: 팀홀튼 캔(글자 크고 선명)은 깨끗하게 나왔지만, 바운티 바(작은 열량 배지 "?00 per serving"이 흐림)는
> **"140 per 28g"·"57g" 을 새로 지어 그렸다** → 폐기, PIL 보정본 사용. **작거나 흐린 글자가 있는 사진은 보정 결과를 원본과
> 반드시 확대 대조**하고, 하나라도 다르면 버린다.

**🔑 Aside 완료 보고 = product_info 갱신 확인 (2026-11-17 추가).** Aside 프롬프트에 "등록 완료 후 product_info.json 에
live_product_id·live_url 을 쓰고, 마지막 줄에 `PRODUCT_INFO_UPDATED: <slug> <상품번호>` 를 남겨라" 를 넣는다.
메인은 그 줄을 받으면 파일을 다시 열어 값이 들어갔는지 확인하고 `claude_skus.py --tag <번호> --claude --slug <slug>` 로 레지스트리 등록.

**🔑 내가 못 여는 건 사장님께 묻지 말고 Aside 에 시킨다 (2026-11-17 사장님: "너가 못한것들도 다 aside한테 요청해").**
네이버 셀러센터 설정값(예: 기존 상품의 배송비 몇 개당), 스마트스토어 상품페이지(429), 네이버쇼핑·쿠팡 검색, walmart.ca 등
봇차단 사이트, 로그인 필요한 화면 → `aside exec` 로 조회해서 답을 받아 쓴다. 사장님께는 **실물 라벨처럼 Aside 도 볼 수 없는 것**만 묻는다.
(2026-11-17 바운티: 에어로 42g 배송 묶음 개수를 사장님께 물었다가 지적받음.)

**How to apply:** Codex QA 에 placeholder 는 FAIL 사유가 아니라고 명시해서 넘긴다. Aside 에 넘기는 프롬프트에는 슬러그·로컬
이미지 경로·placeholder 매핑·태그 후보·가격/배송·플레이북 경로를 다 넣는다(Aside 는 이 대화를 모른다). 진행은 약 60초마다 확인해 보고.
[[feedback_imgbb_image_hosting]] 은 이 흐름에서는 쓰지 않는다.
