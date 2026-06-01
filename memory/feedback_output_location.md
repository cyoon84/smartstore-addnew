---
name: smartstore-addnew-output-location
description: smartstore-addnew 프로젝트 산출물은 데스크톱·모바일 둘 다 워크스페이스 output 폴더에 평탄하게 저장
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0ed2f71d-65d3-4eac-96e5-69bfb42ba44c
---

> **🔴 2026-05-31 갱신 — 두 환경 구분 + 제품별 폴더(new-item/):**
> - **Cowork(모바일 dispatch)** → `smartstore-project/output/` 에 **평탄** 저장 (Cowork 자체는 이대로 유지 — 아래 원문 규칙).
> - **Claude Code(데스크톱 /register·/register-agents·SEO)** → `smartstore-addnew/output/new-item/<ascii_slug>/` **제품별 폴더**. 저장은 `output/` 루트에 슬러그 prefix로 쓴 뒤 `python3 scripts/organize_output.py --apply` 로 `new-item/<slug>/` 분류.
> - **동기화(매일 23:30, sync_mobile_output.sh)** → Cowork 평탄본을 smartstore-addnew 로 가져온 뒤 `organize_output.py` 로 `new-item/<slug>/` 정리. 동일 파일명은 여기꺼 keep.
> - smartstore-addnew/output 루트 구성: `new-item/`(등록상품), `seo_refresh/`(SEO), `cron_logs/`(로그), `new-item/_misc/`(슬러그 미매칭 이미지). 관련 [[project_mobile_output_sync]], [[project_seo_refresh_automation]].

---

(아래는 Cowork 측 평탄 저장 원문 — 여전히 Cowork 환경엔 유효)

smartstore-addnew 프로젝트의 모든 상세페이지 산출물은 데스크톱이든 모바일 dispatch든 **동일하게** 아래 위치에 저장한다.

## 저장 위치

```
/Volumes/External/claude/smartstore-project/output/
```

(Cowork 마운트 기준 — 워크스페이스 안의 `output/` 폴더)

## 파일명 규칙

폴더 분리 X, 평탄 구조. 슬러그를 prefix로 사용:

- `<ascii_slug>_detail.html`
- `<ascii_slug>_product_info.json`
- `<ascii_slug>_등록정보.md`
- 참고 이미지가 있으면 `<ascii_slug>_*.jpg` 식으로 같은 폴더에

예: `aveeno_baby_lotion_532ml_detail.html`, `aveeno_baby_lotion_532ml_product_info.json`, `aveeno_baby_lotion_532ml_등록정보.md`

## 금지

- `~/Downloads/<slug>/` 식으로 Downloads에 새 폴더 만들지 말 것 (Cowork 마운트 밖)
- `output/<slug>/index.html` 식 중첩 폴더 만들지 말 것 (평탄 구조 유지)
- Cowork outputs 스크래치패드에만 저장하고 끝내지 말 것 — 반드시 워크스페이스 `output/`로

**Why:** 데스크톱에서는 프로젝트 설정의 옛 instructions가 `~/Downloads/<ascii_slug>/`를 가리키고 있었고, 모바일은 워크스페이스 `instructions.md`(`output` 폴더 안에 저장)를 따라서 두 경로가 갈렸음. 사용자는 모바일 동작을 정답으로 보고 양쪽을 통일하길 원함.

**How to apply:** 모든 dispatch/single/group/append 모드에서 저장 시 위 경로·파일명 규칙 그대로 사용. `present_files`로 공유할 때도 이 경로 사용. 관련: [[feedback_dispatch_template]]
