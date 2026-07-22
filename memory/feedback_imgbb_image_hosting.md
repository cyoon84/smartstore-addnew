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

**🔑 네이버 권장 크기 = 업로드 전 리사이즈 (imgbb thumb/medium 로는 안 나옴):** imgbb API 응답에 `thumb`(~180px)·`medium` URL 이 있으나 네이버 권장 1000×1000/750×1000 은 안 줌 → **PIL 로 미리 리사이즈 후 업로드**.
- **정사각형 → 1000×1000**
- **비정사각형 → height 1000 + 비례 width** (예: 3:4 세로 카톤 = 750×1000)
- (리사이즈 안 하고 원본 풀해상도 올려도 되지만, 대표이미지는 네이버 권장 크기가 표준.)

**🔑 앨범 지정 불가:** 공개 API 키는 업로드만 됨. 특정 앨범(ibb.co/album/xxx) 배치는 인증 세션(auth_token+album_id) 필요 → **계정 루트에 올라감**. 앨범 정리는 대시보드 수동(리스팅엔 URL만 쓰면 무관).

**🔑 가격표·내부 소싱 이미지는 공개 호스팅 업로드 금지** (Costco 가격표·매대 가격 이미지 등) — 내부용. product_info 에 원가만 기록.

**Why:** Flickr 대신 imgbb 로 전환(사용자 선호). How to apply: 신규 제품 이미지는 위 방법으로 imgbb 업로드, 네이버 크기 규칙 적용, product_info `bulk.rep_image`/`add_images` + detail 에 i.ibb.co URL. 첫 적용 = 타조 그린티 말차 라떼 946ml (2026-07-21). [[feedback_bulk_upload_excel]] · [[feedback_naver_field_limits]]
