---
name: feedback_imgbb_image_hosting
description: 상품 이미지 호스팅 = imgbb (Flickr 대체, 2026-07-21). API 업로드 방법·네이버 크기 규칙
metadata:
  type: feedback
---

**2026-07-21 부터 상품 이미지 호스팅은 imgbb (Flickr 대체).** 사용자: "이제 flickr 대체하자". 기존 등록분(webber·davidstea 등)의 Flickr URL(live.staticflickr.com)은 그대로 두고, **신규 제품부터 imgbb** 사용. imgbb 이미지 CDN = `i.ibb.co` (네이버 에디터 생존 §18 도메인으로 사용).

**API 키:** `~/.config/finchmart/imgbb_key` (리포 밖·gitignore 패턴, 북키퍼 크리덴셜과 동일 위치). **리포에 커밋 금지** — 공개 GitHub 노출 방지. 사용 시 `KEY=$(cat ~/.config/finchmart/imgbb_key)`.

**업로드 방법 (curl):**
```
base64 -i img.jpg | tr -d '\n' > /tmp/b64        # 단일 라인 base64
curl -s "https://api.imgbb.com/1/upload?key=$KEY&name=<이름>" --data-urlencode "image@/tmp/b64"
# 응답 JSON의 data.url 이 이미지 URL (i.ibb.co/...)
```
`--form "image=..."`·`<@` 문법은 실패 → **`--data-urlencode "image@파일"`**(base64 파일) 사용.

**🔑 무조건 JPEG 만 (URL 업로드 금지 — webp 변환됨, 2026-07-22 사용자 "jpeg만 받아"):** imgbb 는 `image=<원격URL>` 도 받지만(URL만 있어도 업로드 OK), **URL 업로드는 결과가 `.webp` 로 변환**돼 네이버가 거부할 위험이 있다. **반드시 로컬로 jpeg 를 받아(원본이 CDN이면 `?fmt=jpeg` 등으로 jpeg 강제) → base64 업로드** → `.jpg` i.ibb.co URL 확보. base64 업로드는 원본 포맷(jpg) 을 유지한다(응답 `data.image.extension:"jpg"` 확인). 즉 **"url만 있어도 업로드"는 되지만 쓰지 말 것 — 항상 다운로드→jpeg→base64.** (룰루 CDN 예: `images.lululemon.com/is/image/lululemon/<style_color>_<view>?wid=1000&fmt=jpeg` → 1000×1200 jpg → base64 업로드.)

**🔑 네이버 권장 크기 = 업로드 전 리사이즈 (imgbb thumb/medium 로는 안 나옴):** imgbb API 응답에 `thumb`(~180px)·`medium` URL 이 있으나 네이버 권장 1000×1000/750×1000 은 안 줌 → **PIL 로 미리 리사이즈 후 업로드**.
- **정사각형 → 1000×1000**
- **비정사각형 → height 1000 + 비례 width** (예: 3:4 세로 카톤 = 750×1000)
- (리사이즈 안 하고 원본 풀해상도 올려도 되지만, 대표이미지는 네이버 권장 크기가 표준.)

**🔑 앨범 지정 불가:** 공개 API 키는 업로드만 됨. 특정 앨범(ibb.co/album/xxx) 배치는 인증 세션(auth_token+album_id) 필요 → **계정 루트에 올라감**. 앨범 정리는 대시보드 수동(리스팅엔 URL만 쓰면 무관).

**🔑 가격표·내부 소싱 이미지는 공개 호스팅 업로드 금지** (Costco 가격표·매대 가격 이미지 등) — 내부용. product_info 에 원가만 기록.

**🔑 헬퍼 스크립트 = `scripts/imgbb_upload.py`:** `python3 scripts/imgbb_upload.py <폴더/파일...> [--full] [--prefix N]` → 네이버 크기 리사이즈+업로드+URL 출력. 폴더 통째로 OK. avif/webp/heic 변환. 매번 손 curl 말고 이거 사용.

**🔑 폰→맥 사진 경로 = iCloud Drive `~/Library/Mobile Documents/com~apple~CloudDocs/스스업로드/`:** 폰에서 사진 찍고 "파일에 저장 → 스스업로드"(제품별 하위폴더 권장). 맥에 낱개 파일로 싱크됨(iCloud "사진"/Photos 라이브러리는 DB라 부적합 — Drive 폴더 사용). 세션 열려있을 때 "넣었어" 하면 그 폴더 → imgbb_upload.py → 산출물 삽입. (완전자동 folder-watch 훅은 옵션, 미설정.)

**Why:** Flickr 대신 imgbb 로 전환(사용자 선호). How to apply: 신규 제품 이미지는 위 방법으로 imgbb 업로드, 네이버 크기 규칙 적용, product_info `bulk.rep_image`/`add_images` + detail 에 i.ibb.co URL. 첫 적용 = 타조 그린티 말차 라떼 946ml (2026-07-21). [[feedback_bulk_upload_excel]] · [[feedback_naver_field_limits]]
