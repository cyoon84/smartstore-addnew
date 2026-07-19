---
name: project_bookkeeper_expense_tracker
description: profit-expense-tracker 북키퍼 — 영수증→지출 장부(7탭). 정산 프로세스와 병행 실행
metadata:
  type: project
---

**북키퍼 에이전트 = `/Volumes/External/claude/profit-expense-tracker/`** (smartstore-addnew 는 매출·정산, 여기는 비용·지출 측). 자체 `CLAUDE.md` 자동 로드.

**구조:**
- `장부.xlsx` — **수입 탭 `수입 (RBC)`** + 지출 7 탭(순서 고정): `식비 · 차 (기름) · 차 (주차) · 차 (maintenance etc) · 물건산거 (COGS) · Supply · monthly subscription`. 지출 컬럼 = `날짜 · merchant · subtotal · tax · total · method of payment · 영수증파일`. 수입 컬럼 = `날짜 · 내역 · 입금액(CAD) · 결제/출금원 · 메모`.
- `scripts/add_expense.py` — 지출 항목 추가 + 영수증 원본을 `receipts/<YYYY-MM>/` 로 그대로 복사(압축·인코딩 금지, §20-1 원칙). 카테고리 별칭(gas/기름·cogs/사입·subscription/구독 등). subtotal+tax=total 검산, 못 읽은 값은 비움(날조 금지 §9).
- `scripts/add_income.py` — RBC 입금(매출) 기입.
- `scripts/build_pnl.py` — 회계년도/월 손익(P&L) 리포트 → `output/pnl/PNL_*.md`. `--fy 2026`(FY) 또는 `--from/--to`.
- `receipts/<YYYY-MM>/` — 월별 영수증 원본.

**🔑 손익(P&L) = 전부 CAD, RBC 입금이 매출 (2026-07-18 확정):** 실수익은 **RBC 계좌로 원할 때 CAD 출금** → **RBC 입금 CAD = 매출**. 네이버 정산(원화)은 smartstore 운영 추적용이고 북키퍼 P&L 과 **분리 — FX 환산 안 함**(RBC 출금이 이미 CAD 확정). 매출은 매달 **bank statement(RBC)** 에서 `수입 (RBC)` 탭에 기입. P&L = `매출(RBC) − 물건값COGS − 운영비`, 전부 CAD. **정산 원화를 P&L 에 안 끌어오므로 COGS 이중집계 없음** — 북키퍼는 RBC 기준 완전 독립 CAD 장부(초기 우려 해소). HST 세금 합 = ITC 참고.

**🔑 영수증은 "데이터 기입 + 원본 파일 저장" 세트 — 이메일도 예외 없음 (2026-07-18 사용자 지적):** 매칭·기입만 하고 끝내지 말 것. Gmail 영수증도 원본(주문 상세 PDF·첨부·이메일 렌더)을 `receipts/<YYYY-MM>/` 에 저장하고 장부 `영수증파일` 칸에 링크. 사진·PDF·이메일 다 동일. (Amazon Tim Hortons 매칭 때 데이터만 넣고 PDF 안 챙겨서 지적받음 → 저장·링크로 수정.) Gmail 자동수집 job 도 이 원칙(추출+원본저장).

**🔑 카드/결제정보 등 핵심정보 없으면 → "full invoice 별도로 찾아라" 알림 (2026-07-18):** 이메일 주문확인처럼 품목·총액만 있고 결제수단이 없으면 빈칸 방치 말고 상세 인보이스(Amazon order-document PDF 등, 카드정보 포함) 찾아달라고 사용자에게 알림. (Amazon Tim Hortons: 확인메일 카드정보 없음 → 상세 PDF 에서 Amex ****1002.)

**🔑 영수증 종류별 처리 체인 (2026-07-18 확정):** 단계 1=북키퍼 장부 · 2=nespresso-order 스킬 · 3=Todoist(order-2task-todoist) · 4=정산(§20 출고일 배치). **네스프레소 영수증=1·2·3·4(풀체인)** / **그 외 구매(COGS/사입) 영수증=1·3·4**(nespresso-order 제외) / **그 외 expense(식비·차·Supply·구독)=1**(북키퍼만). 3·4 는 고객 주문 엮인 사입에만(그 사입이 채우는 고객주문 찾아 연결, §20-2 부모 재사용·§20-4 dedup). 자가소비분은 COGS 제외. 네스프레소 사입/주문나감/자가소비 구분은 사용자에게 물어봄(§23).

**🔑 매출원 2개 = 네이버 + 우버 (2026-07-18):** 회사는 스마트스토어(네이버) + **우버** 운영 → RBC 에 네이버·우버 출금이 같이 쌓임. `수입 (RBC)` 탭 `출처(네이버/우버)` 로 구분(`add_income.py --source 네이버|우버`).

**한미 배송비 = 지출 탭 `배송비 (한미)` 신설 (2026-07-18):** 한미택배 배송비는 **일시불 디파짓을 카드로 선결제**(충전 후 차감) → 디파짓 충전 시 그 금액을 결제일자로 기입. 별칭 hanmi/한미/shipping. build_pnl OPERATING_TABS 에 포함.

**개인계좌 결제:** 개인 카드/계좌(예: Tangerine 개인 chequing)면 method 에 "개인" 표기만. **식당 카드전표는 세액 미표시 → 팁 전 금액에서 HST 역계산**(온타리오 식당 13%, 예 23.67÷1.13=sub 20.95+HST 2.72, 팁은 비과세로 total 에만).

**🔑 세무 인정·공제 판단은 회계사 몫 (2026-07-18):** 식대 50% 규정·가수금/오너상환 분류·공제 여부 등 "인정" 판단은 북키퍼가 안 함(회계사 처리). 북키퍼는 영수증 사실(날짜·merchant·subtotal·tax·total·결제수단)만 정확히 기록 — 세무 코멘트 오지랖 금지. HST 역계산 등 영수증 금액을 정확히 옮기는 계산은 기록의 일부라 OK. (사용자: "인정 이런거는 회계사가 알아서 할테니까")

```
python3 scripts/add_expense.py -c 식비 -d 2026-07-18 -m "Costco" \
  --subtotal 45.20 --tax 5.88 --total 51.08 --method "Visa 6411" --receipt <경로>
```

**🔑 정산 프로세스와 병행 (2026-07-18 사용자 지시 "정산 프로세스 할 때 parallel로"):** 정산 세션에서 영수증 COGS 반영할 때(LEARNED §20-3의 1~3단계: order_settlement --add-cogs → output/receipts 복사 → Todoist cross off) **4번째로 이 장부에도 같은 영수증을 같은 턴에 병행 기입**한다. 정산 영수증(사입)은 보통 `물건산거 (COGS)` 탭. 영수증 원본은 정산의 `output/receipts/<출고일>/` 와 북키퍼의 `receipts/<YYYY-MM>/` **양쪽 다** 보관. 매출측 정산 COGS 와 지출측 장부는 목적이 달라 이중집계 아님.

**🎯 목표 = QuickBooks 대체 (2026-07-18 사용자):** **다음 회계년도(2026-11-01~)부터 QuickBooks 를 해지하고 이 북키퍼(Claude)로 장부를 옮긴다.** 즉 지금(~2026-10-31)은 QB 병행 + 북키퍼 구축/테스트 기간, **2026-11-01 이 실제 cutover**. 회계년도 = **2026-11-01 ~ 2027-10-31**(캐나다 소규모 사업 FY). 완전 대체가 되려면 필요한 것: ① **누락 없는 지출 포착** → Gmail 영수증 자동수집 job 이 핵심(수동 업로드만으론 QB 대체 불가) ② 회계년도 단위 장부·리포트(카테고리별·월별 지출 요약, P&L 성격) ③ 세무 신고에 쓸 카테고리 정합성. → 기존 [[project_qbo_receipt_upload]](QBO Drive 업로드/API)는 **cutover 후 폐기 대상**(QB 자체를 안 쓰므로). Nov 1 다가오면 회계년도별 장부 파일(`장부_FY2027.xlsx` 등)·리포트 스크립트 구축.

**예정:** Gmail 영수증 자동수집 scheduled job 을 여기로 통합(현재 미구현, add_expense.py 호출 방식으로 설계 — QB 대체의 핵심 선결 과제). 관련 [[project_order_settlement]] · [[project_qbo_receipt_upload]] · LEARNED §20-3.
