---
name: project_bookkeeper_expense_tracker
description: profit-expense-tracker 북키퍼 — 영수증→지출 장부(7탭). 정산 프로세스와 병행 실행
metadata:
  type: project
---

**북키퍼 에이전트 = `/Volumes/External/claude/profit-expense-tracker/`** (smartstore-addnew 는 매출·정산, 여기는 비용·지출 측). 자체 `CLAUDE.md` 자동 로드.

**구조:**
- `장부.xlsx` — **수입 탭 `수입 (RBC)`** + 지출 7 탭(순서 고정): `식비 · 차 (기름) · 차 (주차) · 차 (maintenance etc) · 물건산거 (COGS) · Supply · monthly subscription`. 지출 컬럼 = `날짜 · merchant · subtotal · tax · total · method of payment · 영수증파일`. 수입 컬럼 = `날짜 · 내역 · 입금액(CAD) · 결제/출금원 · 메모`.
- `scripts/add_expense.py` — 지출 항목 추가 + 영수증 원본을 `receipts/<YYYY-MM>/` 로 그대로 복사(압축·인코딩 금지, §20-1 원칙). 카테고리 별칭(gas/기름·cogs/사입·subscription/구독 등). subtotal+tax=total 검산, 못 읽은 값은 비움(날조 금지 §9). **🔑 컬럼 = 날짜·merchant·subtotal·tax·total·method·영수증파일·**Note**(8번째). merchant=가게 이름만, 누구주문·품목·배치·결제흐름 등 상세는 전부 `Note` 컬럼(`--note`)에 (2026-07-21 사용자 "merchant엔 가게이름만, 나머지는 Note에, 어차피 회계사 관심없음"). `--note` 가 이제 merchant 에 안 붙고 Note 칸으로 감(기존 동작 변경). 기존 데이터도 마이그레이션으로 merchant→가게명/Note 분리 완료(깊이 인식 괄호·엠대시 split).**
- `scripts/add_income.py` — RBC 입금(매출) 기입.
- `scripts/build_pnl.py` — 회계년도/월 손익(P&L) 리포트 → `output/pnl/PNL_*.md`. `--fy 2026`(FY) 또는 `--from/--to`.
- `receipts/<YYYY-MM>/` — 월별 영수증 원본.

**🔑 손익(P&L) = 전부 CAD, RBC 입금이 매출 (2026-07-18 확정):** 실수익은 **RBC 계좌로 원할 때 CAD 출금** → **RBC 입금 CAD = 매출**. 네이버 정산(원화)은 smartstore 운영 추적용이고 북키퍼 P&L 과 **분리 — FX 환산 안 함**(RBC 출금이 이미 CAD 확정). 매출은 매달 **bank statement(RBC)** 에서 `수입 (RBC)` 탭에 기입. P&L = `매출(RBC) − 물건값COGS − 운영비`, 전부 CAD. **정산 원화를 P&L 에 안 끌어오므로 COGS 이중집계 없음** — 북키퍼는 RBC 기준 완전 독립 CAD 장부(초기 우려 해소). HST 세금 합 = ITC 참고.

**🔑 영수증은 "데이터 기입 + 원본 파일 저장" 세트 — 이메일도 예외 없음 (2026-07-18 사용자 지적):** 매칭·기입만 하고 끝내지 말 것. Gmail 영수증도 원본(주문 상세 PDF·첨부·이메일 렌더)을 `receipts/<YYYY-MM>/` 에 저장하고 장부 `영수증파일` 칸에 링크. 사진·PDF·이메일 다 동일. (Amazon Tim Hortons 매칭 때 데이터만 넣고 PDF 안 챙겨서 지적받음 → 저장·링크로 수정.) Gmail 자동수집 job 도 이 원칙(추출+원본저장).

**🔑 카드/결제정보 등 핵심정보 없으면 → "full invoice 별도로 찾아라" 알림 (2026-07-18):** 이메일 주문확인처럼 품목·총액만 있고 결제수단이 없으면 빈칸 방치 말고 상세 인보이스(Amazon order-document PDF 등, 카드정보 포함) 찾아달라고 사용자에게 알림. (Amazon Tim Hortons: 확인메일 카드정보 없음 → 상세 PDF 에서 Amex ****1002.)

**🔑 영수증 판별 사전 (사업 vs 개인, 2026-07-18):** **Amazon 은 주문자/배송지 이름으로 거른다** — 본인/사업=**CHULHEE**(North York, ONTARIO INC), **"Hana"(Mississauga)=친구 공유 Prime 이라 무시**(Anusol 치질크림 등). 개인 제외: 건강·약국용품·의류·의료서비스·보험(개인차)·투자·카드대금·환불/취소·마케팅. 사업: 주유(Shell)=`차 (기름)`, 자동차보험(belairdirect)=`차 (maintenance etc)`(전액 기록+메모, 사업분은 마일리지 비례 정산은 나중에/회계사, 보험료 HST 면세 tax $0). gmail-receipt-collector job 프롬프트에도 반영.

**🔑 영수증 종류별 처리 체인 (2026-07-18 확정):** 단계 1=북키퍼 장부 · 2=nespresso-order 스킬 · 3=Todoist(order-2task-todoist) · 4=정산(§20 출고일 배치). **네스프레소 영수증=1·2·3·4(풀체인)** / **그 외 구매(COGS/사입) 영수증=1·3·4**(nespresso-order 제외) / **그 외 expense(식비·차·Supply·구독)=1**(북키퍼만). 3·4 는 고객 주문 엮인 사입에만(그 사입이 채우는 고객주문 찾아 연결, §20-2 부모 재사용·§20-4 dedup). 자가소비분은 COGS 제외. 네스프레소 사입/주문나감/자가소비 구분은 사용자에게 물어봄(§23).

**🔑 매출원 2개 = 네이버 + 우버, 둘 다 같은 incorporation (2026-07-18·19):** 회사는 스마트스토어(네이버) + **우버** 운영 → RBC 에 네이버·우버 출금이 같이 쌓임. `수입 (RBC)` 탭 `출처(네이버/우버)` 로 구분(`add_income.py --source 네이버|우버`). **🔑 우버와 핀치마트는 같은 법인(incorporation)** — 우버 배달 운영(grocery shopping·reimburse 포함)도 **전부 이 장부에서 추적**한다(별개 사업 아님, 2026-07-19 사용자 확정). 우버 배달 reimburse 건을 "우버 쪽이라 안 다뤄도 되나" 로 빼지 말 것.

**🔑 우버이츠 grocery reimburse 대기 탭 + 우버 이메일 매칭 (2026-07-19):** 우버이츠 grocery 배달로 사서 **reimburse 받을 구매**(예: 코스트코를 우버이츠로 사서 나중에 환급)는 지출 7탭이 아니라 별도 탭 **`우버이츠 reimburse 대기`** 에 기입한다(`add_expense.py -c reimburse`, 별칭 reimburse/우버이츠/우버/리임버스). **이 탭은 `build_pnl.py` OPERATING_TABS·COGS 에 없어 P&L 에 안 잡힘**(환급받으면 net 0이라 정확 — 절대 넣지 말 것). **🔑 우버 reimburse 확인 이메일 처리:** Gmail 수집 중 우버에서 `A message from Uber` / `You'll be receiving CA$X for Order Number Y` (from email-support.uber.com, "NO RESPONSE NEEDED") 류 이메일이 오면 → **금액(CA$X)으로 `우버이츠 reimburse 대기` 탭 total 칸에서 매칭 행을 찾아 → `Notes` 칼럼(8열, 없으면 생성)에 order#(Y) 기입.** 매칭 금액이 탭에 없으면 → **날조 말고 "탭에 그 금액 없음"으로 사용자에게 플래그만.** 🔑 **영수증 없는 과거 우버 reimburse 이메일을 이메일 정보만으로 대기 탭에 백필하지 말 것 (2026-07-19 사용자 "그 이전꺼는 넣지마" · "어차피 이전꺼는 다 퀵북에했어").** 이유 = **cutover(2026-11-01) 전 과거 건은 이미 QuickBooks 에 기록됨**(QB 병행 기간). 북키퍼에 소급 입력하면 QB 와 이중기록. 북키퍼는 **지금부터 새로 발생하는 것**만(영수증 넣은 건) 추적. 대기 탭은 **실제 영수증을 우리가 넣은 건**만 추적한다(우버=핀치마트 같은 법인이지만, 영수증 없는 옛 reimburse 이메일까지 소급 기록하진 않음). 우버 이메일은 order#·금액 **매칭 확인용**(있는 행에 Notes 채우기)이지, 없는 행을 만들라는 게 아님. (2026-07-19 케이스: Gmail `from:uber.com "A message from Uber"` 5건 — 9E263 $39.84 만 No Frills Vaughan 영수증과 매칭돼 Notes 기입. 나머지 4건 $90.26·$15.08·$20.33·$28.24 는 영수증 없어 **한번 대기행 추가했다가 사용자 지시로 삭제**. 코스트코 $132.11 은 탭엔 있는데 우버 이메일 아직 안 옴. Notes 칼럼은 이때 신설.)

**🔑 이번 FY(~2026-10-31)는 병행 테스트 — 망설이지 말고 다 기입 (2026-07-21 사용자 "어차피 이 파일은 이번 FY에는 그냥 병행으로 테스트로 쓰는거니까 넣어"):** cutover(2026-11-01) 전까진 QuickBooks 가 공식이고 북키퍼는 병행 테스트 장부라, **이중집계·선불자산↔비용·정산 중복 같은 회계 순수성은 과하게 따지지 말고 관련 지출을 일단 다 북키퍼에 기입**한다. "정산에 이미 있으니 뺐다"·"기프트카드라 스킵" 식으로 망설이지 말 것 — 순수성 정리는 cutover 때/회계사가 한다. (단 명백한 자가소비분 제외·method 정확 기록 등 기본 규칙은 유지.) 예: Sudocrem $37.28(7/14 정산에 이미 있어도 북키퍼 COGS 10행에 기입). 캐비앗(정산 중복 주의 등)은 **1줄 참고로만** 달고 기입은 진행.

**🔑 `기프트카드 구매` 탭 = 선불자산, P&L 미포함 (2026-07-21 사용자 "기프트카드 구매한것도 따로 탭을 만들지"):** 기프트카드 할인구매(DoorDash 액면$200→$159.98·factor 0.7999 / Uber $100→$85·0.85)는 **현금 나갔지만 아직 비용 아닌 선불자산** → 별도 탭 `기프트카드 구매`(구매일·기프트카드·액면가·실구매가·할인·결제수단·영수증파일·메모)로 추적. **build_pnl OPERATING_TABS/COGS 에 없어 P&L 자동 제외** — 기프트카드로 결제한 주문은 이미 `물건산거(COGS)` 에 실현금(액면×factor)으로 잡히니, 구매액을 또 비용처리하면 이중집계라 P&L 엔 안 넣음(회계사가 선불자산↔비용 정리). 잔액추적 = [[project_inventory_list]] `output/inventory/기프트카드_잔액.md`(액면 기준 차감, DD 현 $13.64). 🔑 기프트카드 결제 주문은 **① 물건산거(COGS) 에 기록(method="DoorDash/Uber 기프트카드")** + **② 잔액파일 차감** 둘 다 — DoorDash order 를 "기프트카드라 장부 스킵"하면 안 됨(사용자 "아직 장부는 안적었는데?" 지적, Costco·Gas 는 넣고 DoorDash 만 뺀 게 비일관).

**한미 배송비 = 지출 탭 `배송비 (한미)` 신설 (2026-07-18):** 한미택배 배송비는 **일시불 디파짓을 카드로 선결제**(충전 후 차감) → 디파짓 충전 시 그 금액을 결제일자로 기입. 별칭 hanmi/한미/shipping. build_pnl OPERATING_TABS 에 포함.

**🔑 결제수단(Method of Payment) 사전 — 카드 끝자리로 정식명칭 매핑 (2026-07-20, 계속 누적):** 영수증에 카드 끝 4자리만 찍혀도 method 칸엔 **정식 카드명(+끝자리)** 으로 기입. 사용자 지시로 누적:
- **`*1002` = `AMEX Aeroplan Reserve Business (****1002 실물카드)`** (2026-07-20).
- **`*2201` = `AMEX Aeroplan Reserve Business (****2201 Apple Pay)`** (2026-07-20). **🔑 1002·2201 은 같은 카드** — 1002=실물카드 번호, 2201=Apple Pay 기기토큰 번호. 영수증에 2201 찍히면 = Apple Pay 탭, 1002 찍히면 = 실물카드. (Apple Pay→스벅앱충전 같은 추가 결제흐름 디테일 있으면 괄호로 보존: `(****2201 Apple Pay→스벅앱)`.)
- (앞으로 다른 끝자리 나오면 여기 추가.) add_expense `--method` 에 이 정식명칭을 넣는다. 기존 행도 끝자리로 찾아 정규화하되 결제흐름 디테일은 유지.

**개인계좌 결제:** 개인 카드/계좌(예: Tangerine 개인 chequing)면 method 에 "개인" 표기만. **식당 카드전표는 세액 미표시 → 팁 전 금액에서 HST 역계산**(온타리오 식당 13%, 예 23.67÷1.13=sub 20.95+HST 2.72, 팁은 비과세로 total 에만).

**🔑 세무 인정·공제 판단은 회계사 몫 (2026-07-18):** 식대 50% 규정·가수금/오너상환 분류·공제 여부 등 "인정" 판단은 북키퍼가 안 함(회계사 처리). 북키퍼는 영수증 사실(날짜·merchant·subtotal·tax·total·결제수단)만 정확히 기록 — 세무 코멘트 오지랖 금지. HST 역계산 등 영수증 금액을 정확히 옮기는 계산은 기록의 일부라 OK. (사용자: "인정 이런거는 회계사가 알아서 할테니까")

```
python3 scripts/add_expense.py -c 식비 -d 2026-07-18 -m "Costco" \
  --subtotal 45.20 --tax 5.88 --total 51.08 --method "Visa 6411" --receipt <경로>
```

**🔑 엑셀 컬럼 너비 = 매번 텍스트 다 보이게 넉넉히 (2026-07-20 사용자 지시):** 내가 만드는/수정하는 모든 엑셀 산출물(장부.xlsx·재고관리·정산 엑셀 등)은 저장 시 **컬럼 너비를 내용에 맞춰 자동 조정**한다(한글 2배 가중, 최대 ~90). `add_expense.py`·`add_income.py` 는 `autofit(wb)` 를 save 직전 호출해 자동 적용됨. openpyxl 로 직접 엑셀 편집·생성할 때도 저장 전 컬럼 폭을 max 내용 길이로 넓힐 것(merchant 등 긴 열이 잘려 보이지 않게).

**🔑 정산 프로세스와 병행 (2026-07-18 사용자 지시 "정산 프로세스 할 때 parallel로"):** 정산 세션에서 영수증 COGS 반영할 때(LEARNED §20-3의 1~3단계: order_settlement --add-cogs → output/receipts 복사 → Todoist cross off) **4번째로 이 장부에도 같은 영수증을 같은 턴에 병행 기입**한다. 정산 영수증(사입)은 보통 `물건산거 (COGS)` 탭. 영수증 원본은 정산의 `output/receipts/<출고일>/` 와 북키퍼의 `receipts/<YYYY-MM>/` **양쪽 다** 보관. 매출측 정산 COGS 와 지출측 장부는 목적이 달라 이중집계 아님.

**🔑 왜 QuickBooks 떠나나 (2026-07-19):** ①일부 카드(CIBC Costco Mastercard 등) QB 은행연동 자동캡처 안 됨→거래 누락 ②혼합결제(우버 기프트카드+신용카드 등) QB 표현 지저분 ③기타. → 북키퍼 요구: **카드 불문 영수증 기반 캡처** + **혼합·분할 결제를 method 칸에 명시**(예 `DD기프트카드 $33 + Visa $8`), 기프트카드 잔액 별도 추적. **🔑 스코프 = 비용처리(지출)만 — 고객 invoice 안 만듦(AR 불필요, 2026-07-19).** QB 도 비용처리만 썼음. 매출은 인보이스 아닌 RBC 실입금으로.

**🎯 목표 = QuickBooks 대체 (2026-07-18 사용자):** **다음 회계년도(2026-11-01~)부터 QuickBooks 를 해지하고 이 북키퍼(Claude)로 장부를 옮긴다.** 즉 지금(~2026-10-31)은 QB 병행 + 북키퍼 구축/테스트 기간, **2026-11-01 이 실제 cutover**. 회계년도 = **2026-11-01 ~ 2027-10-31**(캐나다 소규모 사업 FY). 완전 대체가 되려면 필요한 것: ① **누락 없는 지출 포착** → Gmail 영수증 자동수집 job 이 핵심(수동 업로드만으론 QB 대체 불가) ② 회계년도 단위 장부·리포트(카테고리별·월별 지출 요약, P&L 성격) ③ 세무 신고에 쓸 카테고리 정합성. → 기존 [[project_qbo_receipt_upload]](QBO Drive 업로드/API)는 **cutover 후 폐기 대상**(QB 자체를 안 쓰므로). Nov 1 다가오면 회계년도별 장부 파일(`장부_FY2027.xlsx` 등)·리포트 스크립트 구축.

**🔑 Gmail 영수증 라벨링 (2026-07-20 사용자 지시):** gmail-receipt-collector 루틴이 영수증을 분류하며 **`북키퍼/<카테고리>` Gmail 라벨**도 붙인다 — `북키퍼/우버이츠`·`북키퍼/COGS`·`북키퍼/네스프레소`·`북키퍼/식비`·`북키퍼/차`·`북키퍼/Supply`·`북키퍼/구독`·`북키퍼/홈오피스`·`북키퍼/개인`·`북키퍼/확인필요`(장부 카테고리 매핑). ⚠️ **Gmail 커넥터 읽기전용이라 create_label·label_message 가 "additional permissions" 오류** → 라벨 생성·부착은 **사용자가 Gmail 커넥터를 라벨/modify 권한으로 재연결**해야 작동(2026-07-20 미연결). 루틴 SKILL.md 에 라벨 단계 넣어둠(권한 생기면 자동, 없으면 그 run 스킵+Slack 1줄). 라벨 재부착 중복 무해. **🔑 우버 reimburse 이메일은 "전부"가 아니라 장부 매칭된 것만 라벨 (2026-07-20 사용자 "gmail 체크루틴때 해야지", "우리가 장부에 적은 우버 주문건 이메일부터만"):** `A message from Uber` reimburse 이메일에서 Order#(예 CA6AB·9E263·BAC41)를 뽑아 `장부.xlsx` `우버이츠 reimburse 대기` 시트 Notes(order#)에 **있을 때만** `북키퍼/우버이츠` 붙임. 장부에 없는 옛 배달기사 reimburse 등은 라벨링 X(라인 29 매칭 규칙과 동일 게이팅). 수동으로 옛날 것 200여건 라벨링하지 말 것(사용자 "이전꺼는 하지마"). 루틴 SKILL.md step 2-1 에 반영. (내가 처음 최상위 `Uber` 라벨을 새로 만들어 3건 붙였다가 → 표준 `북키퍼/우버이츠`로 교체·`Uber` 라벨은 비게 됨(MCP 로 라벨 삭제 불가, 사용자가 Gmail 에서 수동 삭제 가능).)

**🔑 영수증 "오프라인 캡처" 채널 = 플러스-주소 이메일 인박스 (2026-07-20 사용자 "A로", "진짜 퀵북 클론"):** 캡처(사진→클라우드 확정저장)와 처리(장부 기입)를 분리 — 폰으로 영수증 찍어 **`chulhee.y+receipt@gmail.com`** 로 메일/공유하면 맥 상태 무관하게 Gmail(클라우드)에 즉시 확정저장(유실 없음). = QuickBooks Receipts 탭(이메일 인입)의 클론. gmail-receipt-collector 루틴 step 1-0 이 `(deliveredto:chulhee.y+receipt@gmail.com OR to:chulhee.y+receipt@gmail.com)` 로 직접 검색(🔑 `to:` 포함=병행 포워딩[qbodocs+receipt 동시]도 잡음)해 수집(**자기발송=무조건 사업**, 판별사전 스킵), 라벨 `북키퍼/영수증-인박스`(Label_84)+카테고리라벨, 원본 저장. **🔑 첨부 원본은 반드시 `scripts/fetch_gmail_receipts.py`(IMAP 앱비밀번호)로 디스크 직접 기록 — Gmail MCP 는 첨부 바이너리 못 줌, 그리고 원본을 base64/Bash 도구출력으로 나르면 깨진다(사용자 "drive로 다 깨진 파일로 저장하던 너 전에 하는짓보니까 못믿겠어" — §20-1 Drive 저해상도 참사와 같은 원인).** 스크립트가 원본 바이트를 `open(wb)` 로 디스크 직접 저장(풀해상도·무손실·idempotent). **백엔드 2종 자동선택(사용자가 OAuth 선호 2026-07-20): ①OAuth(권장·평문비번 없음·`gmail.readonly`) — credentials.json `~/.config/finchmart/gmail_oauth_credentials.json`(GCP 콘솔서 Desktop OAuth 클라이언트 만들어 다운로드·본인을 테스트사용자로), 첫 실행 브라우저 동의(사용자 로그인, 내가 비번 안 봄)→token 자동캐시. ②IMAP 앱비밀번호(폴백) `~/.config/finchmart/gmail_app_password`.** 둘 다 `.gitignore`(`.gmail_oauth_*`·`.gmail_app_password`), 스크립트는 읽기만·**내가 크리덴셜 값을 보거나 타이핑 안 함**. libs: `google-api-python-client google-auth-oauthlib`(설치됨). 미설정이면 스크립트 에러→그 run 원본저장만 스킵(Gmail 라벨로 원본은 안전, 재실행). ⚠️ 사용자가 앱비번을 채팅에 노출한 적 있음 → 확인 끝나면 폐기·재발급 권고(값은 파일에만). **처리(장부 기입)는 여전히 사용자 확인 후 로컬**(캡처만 오프라인-비의존). ⚠️ Gmail **필터 생성은 MCP 불가** → 루틴이 필터 대신 플러스주소 직접검색(사용자가 Gmail 설정서 `to:...+receipt`→라벨 필터 수동으로 걸면 더 깔끔, 선택). 완전 무-맥(처리까지 자동)은 루틴 클라우드화가 추가과제. 새 리스팅 사진도 같은 채널로 확장 가능. [[project_qbo_receipt_upload]]

**예정:** Gmail 영수증 자동수집 scheduled job 을 여기로 통합(현재 미구현, add_expense.py 호출 방식으로 설계 — QB 대체의 핵심 선결 과제). 관련 [[project_order_settlement]] · [[project_qbo_receipt_upload]] · LEARNED §20-3.
