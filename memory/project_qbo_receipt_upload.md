---
name: project-qbo-receipt-upload
description: QuickBooks 영수증 인입 — 🔑채택 방식=Google Drive receipt-qb/<출고일> 업로드(완전자동, 정산COGS와 동시처리). API(qbo_auth/qbo_receipt)는 샌드박스 검증 완료·Production 보류
metadata:
  type: project
---

QuickBooks Online 영수증 인입 연동 (2026-07-11 구축).

**🔑 채택된 방식 = Google Drive 업로드 (2026-07-11 최종 — 이메일 드래프트 방식 대체):**
- 영수증을 Drive **`receipt-qb/<YYYY-MM-DD>/`** 폴더에 업로드. 루트 폴더 = `receipt-qb`(id `1gK52zZ4XKcOvTWGw8cjXJG0HDVzFw3xE`, 2026-04부터 운영 중), 하위에 날짜 폴더(`2026-07-11` 형식).
- **완전 자동:** Drive MCP `create_file`로 폴더 생성(mimeType `application/vnd.google-apps.folder`) + 이미지 업로드(`base64Content` + `disableConversionToGoogleType:true`) 모두 동작 확인. 사용자 클릭 불필요.
- **워크플로:** 영수증 받으면(정산 COGS 반영 시) → 그 날짜 폴더 확인/생성 → 영수증 파일 업로드. 파일명은 매장·내용 식별 가능하게.
- (기각된 안: ①이메일 포워딩 finchmart_to@qbodocs.com — Gmail MCP가 드래프트까지만 가능해 사용자가 전송 클릭해야 함 ②Mail.app osascript — 사용자 거절. 참고: Gmail create_draft는 설명과 달리 첨부 지원 확인됨.)

**API 방식 (샌드박스 검증 완료, Production 보류):**

**구성:**
- `config/qbo_credentials.json` — client_id/secret·app_id·environment·redirect_uri (gitignored, chmod 600)
- `config/qbo_tokens.json` — access/refresh 토큰 + realm_id (gitignored, 자동 refresh)
- `scripts/qbo_auth.py` — OAuth2 인증. `--status` 상태확인, `--refresh` 갱신, `--manual` 콜백서버 없이 URL 붙여넣기. 리다이렉트 `http://localhost:8400/callback` (Intuit 포털에 등록됨)
- `scripts/qbo_receipt.py` — 영수증 업로드: ①Vendor 조회/생성 ②Purchase 생성 ③Attachable multipart 업로드+링크. `--list-accounts`/`--list-vendors` 조회 지원. stdlib only.

**사용 예:**
```
python3 scripts/qbo_receipt.py <영수증.jpg> --amount 45.67 --date 2026-07-07 \
  --vendor "Costco Wholesale Canada" --payment-account "Mastercard" \
  --expense-account "Cost of Goods Sold" --memo "7/10 출고 COGS"
```

**핵심 지식:**
- QBO "Receipts 탭"(OCR 인박스)은 공식 API 없음 — 우회는 이메일 포워딩. 우리는 정산 워크플로([[project_order_settlement]])가 이미 영수증을 파싱하므로 Purchase+Attachable 방식이 정답(리뷰 단계 불필요).
- Attachable 업로드 = multipart(`file_metadata_01` JSON + `file_content_01` base64), `AttachableRef`로 Purchase 링크.
- refresh_token 수명 ~100일 — 갱신할 때마다 연장되므로 주기적 사용이면 재인증 불필요.

**⚠️ 현재 상태: Development(샌드박스) 키** — 연결된 회사 = "Sandbox Company US a12e"(realm 9341457442247135), 실장부 아님. 실장부 연결하려면 Intuit 포털에서 **Production 키** 발급 후 config 교체(environment: production) + 재인증 필요. Production 리다이렉트는 https 필수라 localhost 거부 시 `--manual` 모드 사용. 샌드박스 테스트: Purchase Id 145 + 첨부 성공(2026-07-11).

**Production 전환 준비 상태 (2026-07-11):**
- 법적 페이지(EULA·privacy·disconnect·index) = **`gh-pages` 브랜치**에 푸시됨 (영문, FinchMart private 앱 명시). GitHub Pages 켜면 `https://cyoon84.github.io/smartstore-addnew/eula.html` 등으로 서빙.
- Intuit 폼 주의: **Host domain 필드는 `https://`·경로 없이 도메인만**(`cyoon84.github.io`) — 전체 URL 넣으면 "Enter a valid host domain" 거부. 나머지 URL 필드는 https:// 포함.
- 사용자 결정: 지금은 샌드박스 테스트까지만. **Production은 나중에 진짜 도메인 사서 진행** (github.io 공유 도메인 거부 가능성 회피). 도메인 사면 → GitHub Pages 커스텀 도메인 연결 → Intuit 폼 재입력 → Compliance 설문(40분, 답변 초안 지원) → Production 키 발급 → config 교체+재인증.

**🔑 정산 COGS + Drive 업로드 = 한 번에 같이 처리 (2026-07-11 사용자 지시):** 영수증 받으면 ①`order_settlement.py --add-cogs "라벨=금액"`으로 그 출고일 정산에 반영 ②같은 영수증 파일을 Drive `receipt-qb/<출고일>/`에 업로드. 둘 다 자동, 사용자 클릭 불필요. Drive 폴더명은 **출고일**(화/금, [[project_order_settlement]] 기준) 사용 — 영수증 받은 날짜가 아님. 2026-07-14 출고분(김하나 ₩96,622) 영수증 대기 중, 사용자가 "내일 할게"(2026-07-12)로 보류.

**다음 단계(후보):** 정산 `--add-cogs` 시 QBO Purchase 자동 생성 연동(API Production 전환 후), Production 키 전환(도메인 구매 후).
