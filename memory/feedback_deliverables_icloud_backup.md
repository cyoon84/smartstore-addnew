---
name: feedback_deliverables_icloud_backup
description: 산출물(엑셀·상세 등)은 SendUserFile 전송 + iCloud Drive 핀치마트_산출물 폴더에 백업 복사 (리모트/폰 접근용)
metadata:
  type: feedback
---

**산출물을 만들 때마다 iCloud Drive 폴더에도 백업 복사한다** (사용자 확정 2026-07-22 "백업 삼아 ㅇㅇ").

**Why:** 맥미니가 집에 있고 사용자는 사무실/외부라, 리모트 세션에서 **SendUserFile 채팅 다운로드가 안 되는 이슈**가 있음(2026-07-22 팀홀튼 디카페인 엑셀 다운 실패). iCloud Drive 는 폰 파일앱에서 바로 접근되므로 **어디서든 산출물 확보** 가능. (통째 클라우드 이전은 실브라우저 크롤·computer-use 때문에 불가 — 하이브리드로, 딜리버러블만 클라우드 접근.)

**How to apply:**
- **폴더:** `~/Library/Mobile Documents/com~apple~CloudDocs/핀치마트_산출물/` (iCloud Drive. 폰 = 파일앱 → iCloud Drive → 핀치마트_산출물). 사진 업로드용 `스스업로드` 폴더와 같은 iCloud, 방향만 반대(우리→사용자).
- **언제:** 일괄등록/일괄수정 엑셀·detail.html·그룹세팅·매니페스트 등 **사용자에게 SendUserFile 로 보내는 딜리버러블은 그 폴더에도 `cp`** (백업 + 리모트 접근). SendUserFile 을 대체하는 게 아니라 **병행**(둘 다).
- **파일명:** iCloud 사본은 **한글 알아보기 쉬운 이름**으로(예 `팀홀튼디카페인_일괄등록.xlsx`, `온마이레벨토트백_일괄수정.xlsx`) — 폰에서 뭐가 뭔지 바로 구분되게. (원본 output/ 는 ascii 슬러그 유지 §3, iCloud 사본만 한글 별칭.)
- 동기화 몇 초~1분. 내부 소싱/가격표 이미지 등 민감파일은 넣지 않음(딜리버러블만).

관련: [[feedback_send_files_to_user]] · [[feedback_imgbb_image_hosting]](스스업로드 폴더 = 반대방향)
