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

**How to apply:** Codex QA 에 placeholder 는 FAIL 사유가 아니라고 명시해서 넘긴다. Aside 에 넘기는 프롬프트에는 슬러그·로컬
이미지 경로·placeholder 매핑·태그 후보·가격/배송·플레이북 경로를 다 넣는다(Aside 는 이 대화를 모른다). 진행은 약 60초마다 확인해 보고.
[[feedback_imgbb_image_hosting]] 은 이 흐름에서는 쓰지 않는다.
