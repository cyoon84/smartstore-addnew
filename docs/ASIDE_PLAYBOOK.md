# ASIDE_PLAYBOOK — finchmart_ca 신상품 등록 (Aside 브라우저용)

> Aside 브라우저에서 이 프로젝트를 돌릴 때의 실행 절차. 사진/URL → 원가조사 → 이미지 → 네이버 이미지업로드 → 일괄엑셀 → 그룹 → 확인·Slack.
> 규칙 자체(가격·상품명·태그·상세 포맷)는 AGENTS.md / docs/LEARNED_RULES.md 가 정본. 여기는 "Aside에서 어떻게 하느냐"만.
> 새로 알게 된 건 해당 섹션에 계속 추가하고 맨 아래 History 에 한 줄 남긴다.

## 0. 입력 해석 (사용자 말투 → 동작)
- 사진 첨부 + "walmart $A→$B 세일" → 원가 = 세일가. 같은 라인이라도 세일 아닌 SKU는 실제 가격 확인 (예: Jell-O 푸딩은 $2.07 정가).
- "1불씩만 받고" → `price_calc.py std --cost X --markup 1 --tax T` (CAD $1 순마진, 수수료 6.6% gross-up).
- "순마진 N%" → `pct_net`. "무료배송" → 배송비를 판매가에 흡수.
- "배송비 10000원 개수 제한 없이" → 배송비유형 유료 10,000 + 묶음배송 가능(기본 묶음그룹, 가장 작은 배송비).
- "chatgpt한테 사진 보정" → Aside `imagegen.generate` (ChatGPT UI 아님 — 보고 때 명시).
- 세금: 기초식료품(젤리가루·푸딩믹스 등) 0%, 세제/생활용품 13%. 애매하면 가정하고 보고에 명시.
- "만들어줘/올려줘"면 끝까지 진행. 국내시세는 확인해서 보고만, GO 재확인 X.

## 1. 첨부 읽기
- 모든 첨부를 `read_file` 로 먼저 확인 (맛·용량·가격표 노출 여부).

## 2. Walmart.ca 조사
- 검색: `walmart.ca/en/search?q=...` 카드 텍스트에서 "Now $X, Was $Y".
- 상품페이지 `__NEXT_DATA__` → `props.pageProps.initialData.data.product` (name, upc, imageInfo.allImages, priceInfo.currentPrice/wasPrice), `.idml` (specifications, ingredients, longDescription).
- 원산지: 상자 뒷면 이미지에서 "PRODUCT OF U.S.A." 확인 (Kraft Heinz 제품 = 미국, origin_code 0204000).
- 온라인에 없는 매장 전용 SKU(예: 젤로 베리블루, 레몬 푸딩) → 같은 라인 가격으로 가정하고 보고에 표시, 원재료·UPC는 비워둠.

## 3. 국내 시세 + 카테고리
- `search.shopping.naver.com/ns/search?query=...` 본문 텍스트로 가격·배송비 비교.
- 경쟁 상품 카테고리: 상품 페이지 HTML의 `"wholeCategoryName"`.
- 카테고리 코드: `guide/일괄등록 guide/category_*.xls` (xlrd = session tmp/pylib, PYTHONPATH 지정).
- 그룹은 같은 카테고리만 묶을 수 있음 → 카테고리가 다르면 그룹 분리 (젤리 50022479 / 푸딩 50022539).

## 4. 이미지
- imagegen 프롬프트 (SKU당 1회, 4개씩 Promise.all): "Square 1:1… Brighten… Keep the box, logo and every printed word exactly… centered, ~80% width… Remove partial neighboring boxes… No price tags". 결과는 session artifacts 의 imagegen-*.png.
- 결과물 상자 비율이 제각각이라 PIL로 통일: 상자 bbox 눈대중 → side = boxW/0.88, 상자 중심 기준 정사각 crop → 1000×1000. 모자란 가장자리는 mirror pad (edge stretch는 줄무늬 생김). numpy 없음 → PIL 만.
- 추가이미지: Walmart 공식 이미지 `?odnHeight=1000&odnWidth=1000&odnBg=FFFFFF` 로 받아 흰 배경 1000×1000 pad. 공식 이미지 없는 SKU는 같은 라인 대표이미지 모음(라인업) 콜라주.
- **사용자 규칙 (2026-11-11): 대표이미지 포함 모든 매장 사진은 AI 재생성 금지 (토블론 대표·옆면 둘 다 "AI 티" 지적) — 원본 그대로 PIL 밝기 보정만** (gamma로 평균밝기 ~135, contrast 1.06, color 1.08, sharpness 1.1, 정사각은 **원본에서 정사각 crop** — 옆 상자·매장 배경이 보여도 OK. 블러/늘린 가장자리로 pad 금지: "옆에 크롭시킨 것처럼" 보인다고 지적됨 2026-11-11). imagegen은 작은 글씨를 다시 그려 "AI 티"가 남.
- iCloud 첨부 폴더는 REPL fs·read_file 둘 다 막힐 수 있음 → Bash `python3 -m http.server --bind 127.0.0.1` (yield) 로 띄우고 REPL `fetch` → `display`/imagegen `{data,mimeType}` 입력. 끝나면 서버 종료.
- 매장 가격표가 읽히면 반드시 crop/blur. 대표이미지 = 사장님 매장 사진.

## 5. 파일 권한 (Aside)
- 2026-11-12: 사용자가 맥 전체 디스크 접근 권한을 Aside에 허용 → 프로젝트 폴더(docs/output/memory) 쓰기 안정. 세션 tmp·Aside memory 폴더는 여전히 막힘(Aside 정책).
- 쓰기 실패("Operation not permitted")는 간헐적임. 권한 탓으로 단정하기 전에 같은 쓰기를 한 번 더 재시도할 것 (2026-11-11: 실패 직후 재시도로 성공).
- 세션 권한이 Read-only 면 모든 쓰기가 막힘 → 사용자에게 권한(Guard/Full access) 요청. Guard 면 Bash 로 프로젝트 쓰기 가능.
- REPL `fs.writeFile` 은 정책상 막힐 수 있음 → 쓰기는 Bash(heredoc/python/curl). 이미지 확인은 `read_file`, REPL `fs.readFile` 로 프로젝트 파일 읽기 가능.
- 작업 폴더: `output/new-item/_<name>_work/` (원본·imagegen 결과·시트).
- 파일 업로드는 setInputFiles 대신 DataTransfer 주입: REPL readFile→base64 → `page.evaluate` 로 File 생성 → `input.files = dt.files` + change 이벤트.

## 6. 네이버 이미지 업로드 (imgbb 금지)
- 일괄등록 `#/products/bulkadd` → "이미지 업로드" → "이미지 추가" → 포토업로더 팝업이 `tabs[1]` 로 뜸 (`page.context()` 없음).
- 팝업 `input.nmu_file` 에 DataTransfer 주입 (25장 한번에 OK) → "전송이 완료" → 닫기.
- 다이얼로그 그리드는 페이지당 20행 + 가상 스크롤: 스크롤 컨테이너 scrollTop 을 150px씩 내리며 `img.src` 수집 + 페이지 링크 클릭. `?type=` 제거 → `shop-phinf.pstatic.net/<date>_<n>/<id>_JPEG/<filename>`.

## 7. 산출물 + 엑셀
- Python 스크립트 하나로 SKU별 `_product_info.json`, `_detail.html`, `_등록정보.md` 생성 (output/new-item/<slug>/).
- bulk 블록: rep_image, add_images(네이버 shop-phinf URL 리스트 — 추가이미지 칸에 들어감), category_code, origin_code, maker, shipping_type/fee, gosi_model. unit_price {100,g,총g}.
- `PYTHONPATH=<session tmp>/pylib python3 scripts/build_bulk_excel.py --out output/new-item/_batch/<묶음>_bulk_upload.xlsx <slugs…>` → openpyxl 로 관부가세 포함·이미지·브랜드 검산.
- 엑셀 업로드: "엑셀 업로드" → `[role=dialog] input[type=file]` 에 DataTransfer 주입 → 업로드 → 결과 그리드에서 상품번호 읽기 (식품은 바로 판매중, 세제류는 판매중지로 올라옴).

- 원산지 미확인 수입품: 원산지코드 `03`(상세설명에 표시)은 **`원산지 직접입력` 칸(33열)에 값이 없으면 업로드 전체가 "작업 중 오류가 발생하였습니다"로 실패** → "상세설명 참조" 입력. 오류 나면 SKU 나눠 올려서 원인 행 찾기.

- **사용자 선호 (2026-11-12): 식품 상세에는 영양정보·원재료를 텍스트로 넣기** — 뒷면 사진은 유지하되, 라벨 텍스트를 뽑아 한글(영문 병기) 영양성분 표 + 원재료(한글 번역 + 영문 원문) + 알레르기 블록 추가. 맛이 여러 개면 맛별 블록. 표는 `<table>` 대신 div 행 + `float:right` 값 (flex는 미리보기 렌더러 위험). 사례: 리세스 빅컵 그룹 58138452.
- 그룹 상세가 "판매옵션별 등록"이면 옵션마다 같은 HTML을 넣어야 함(행별 "입력" → HTML 작성 textarea fill → 저장). 박스/맛별 사진은 각각 따로 넣고 "(A · B)"처럼 한 사진에 묶어 캡션 달지 말 것.

- **엑셀 셀 한도 32,767자**: 상세 HTML이 그보다 길면 일괄등록 때 뒷부분이 잘림(치리오스 6맛 영양표 33,898자 → "제품 정보" 이후 잘림, 2026-11-12). 긴 상세는 업로드 후 그룹/상품 수정의 HTML 작성 창에 전체 붙여넣기(창에는 한도 없음).

## 8. 그룹 전환 (새 그룹)
- `#/products/origin-list` → 기준 상품 행의 "그룹 전환" 버튼 → 다이얼로그(가능 옵션 구성 목록) → 다음 → `standard-group-product/setting`.
- 판매옵션명 드롭다운이 AI 추천값(예: 개당 용량 x 개당 수량 x 수량)으로 잡혀 있으니 바꿀 것: generic 클릭 → 옵션 텍스트(예: "맛 x 용량 x 수량") 좌표 클릭.
- "기존 상품 불러오기" → 행의 `.ag-selection-checkbox` 좌표 클릭 → `.ag-row-selected` 로 확인 (한 개씩 누락되기 쉬움) → 상품등록.
- 셀 입력 helper(typeCell): dblclick → 입력 → Space+Backspace → 드롭다운 정확일치 또는 "직접입력: X" 클릭. 막히면 "직접입력" 항목을 직접 찾아 클릭. REPL 리셋되면 closeWarn/cellOpen/pickPop/typeCell/readG 를 globalThis 로 다시 정의.
- 그룹상품명: "잠깐! 그룹상품명에 판매옵션값과 중복된 단어" 팝업이 떠 있으면 키 입력이 씹힘 → 닫기(화면 중앙 버튼) → 입력칸 좌표 클릭 → Meta+A → 다시 입력 → `inputValue()` 확인. 이름에 맛·용량을 넣지 말 것.
- 세제·생활용품: 상품 주요정보(2) 생활화학 인증 "승인/신고대상 아님" 라벨 좌표 클릭.
- 저장 → 확인 → "그룹상품 전환이 완료". 판매중지가 섞여 있으면 "판매중지 상품관리" → 체크 → 판매변경 → 판매중 → 확인.

## 9. 그룹 수정 마무리
- 그룹 id: origin-list 행 또는 그룹 목록. 수정 페이지는 새 탭으로 열 것 (setting 페이지에서 hash goto 하면 setting 으로 튕김).
- 묶음배송: 배송 요약 span("…묶음배송불가 / 유료…") 클릭 → "가능" 클릭 → 기본 배송비 묶음그룹.
- 태그(검색설정 토글): 사전 자동완성에 정확히 일치하는 것만 들어감, Enter 로 직접 추가 불가. 차단 팝업은 확인으로 닫기.
  - 통과: 대용량세제 빨래세제 드럼세탁기세제 캐나다직수입 빨래용품 고농축세제 냄새제거 살림템 편리한 운동복세탁 / 젤리만들기 디저트만들기 아이간식 간식만들기 수입간식 홈파티 홈카페 베이킹재료 어린이간식 수입과자
  - 차단: 세탁세제 캡슐세제 세탁볼 세탁용품 홈베이킹
  - 통과(11/11): 크리스마스선물 초콜릿선물 수입초콜렛 연말선물 크리스마스파티 개별포장 선물용초콜릿 밀크초콜릿 / 수입과자 초코칩쿠키 소프트쿠키 대용량과자 사무실간식 간식거리 외국과자 / 홀빈 향커피 홈카페 커피원두 코스트코원두 커피선물 원두선물 수입원두 드립커피
  - 차단(11/11): 원두커피 원두
  - 자동완성 없음: 푸딩만들기 푸딩가루 푸딩믹스 인스턴트푸딩 파티디저트 미국간식 디저트믹스 젤로푸딩 바닐라푸딩 초코푸딩 레몬푸딩 디저트재료 세탁캡슐 젤라틴파우더
- 저장 전 브랜드/제조사 확인 (그룹 저장 시 초기화될 수 있음). 사전에 있음: 젤로·크래프트하인즈, 게인·P&G.

## 9-1. 단독상품 수정 (상품수정 페이지)
- 수정 URL은 origin no: origin-list 에서 상품번호 행의 row-index 로 같은 행의 "수정" 버튼 좌표 클릭 (ref regex 매칭은 다른 행 잡을 수 있음). goto 대신 새 탭으로 열 것.
- 추가이미지 교체: `#optionalImages i[aria-label="이미지 수정"]` 좌표 클릭 → "내 사진" → `page.waitForEvent('filechooser')` → `setFiles({name,mimeType,buffer})` (버퍼 OK, 세션폴더 불필요). 교체 후 img.src 는 `https://sell.smartstore.naver.com/shop1.phinf.naver.net/...` 프록시 → 상세 HTML엔 `https://shop-phinf.pstatic.net/...` 로 바꿔 넣기.
- 상세 HTML: `textarea` 2번째 `fill()` 로 URL 치환.
- 단위가격 input `product.detailAttribute.unitCapacity.unitCapacity` — 카테고리 원칙 단위 안내문 따라 (초콜릿·쿠키 10g, 원두 100g).
- 판매기간: "판매기간" 행 설정함 라벨 좌표 → 프리셋(60일) → 종료 달력 아이콘 → 월 이동 → 날짜 → 시간(:59) 클릭. KST 기준.
- 묶음배송: 배송 요약 leaf("…묶음배송불가 / …") 클릭해 펼침 → 묶음배송 행의 "가능". (같은 화면의 "미성년자 구매 가능"과 헷갈리지 말 것)
- 저장: 하단 저장하기 → "상품수정이 완료되었습니다".

## 10. 확인 + 보고
- 구매자 페이지 `…/products/<no>?t=<ts>` : 제목·가격·배송·옵션 썸네일·브랜드·원산지·태그 확인 + 스크린샷.
- 등록정보.md 끝에 "등록 완료" 블록(상품번호·그룹·옵션·배송·엑셀 경로) 추가 → `python3 scripts/slack_notify.py --file` SKU마다.
- 보고: 표(그룹/옵션/상품번호/가격) + 가정한 것(세금, 온라인 미등록 SKU 원가, 원산지 근거) + 스크린샷.

## 참고 사례
- 게인 플링스 76개입 4종: 그룹 58028009, 13865523237~240, ₩48,600 무료배송.
- 젤로 젤리 5종 그룹 58037640 (13865911313~317, ₩2,320), 젤로 푸딩 3종 그룹 58037746 (13865911318~320, ₩3,140), 배송 10,000 묶음.

## History
- 2026-11-10: 게인 플링스 + 젤로 등록 흐름을 사용자 요청으로 플레이북화 (Aside).
- 2026-11-11: 코스트코 3종(베어포즈 13867689916, 토블론 13867691266, 자비다 크렘브륄레 13867689917). 옆면샷 AI 금지 규칙, 원산지 03 직접입력 필수, 상품수정 페이지 절차, 쓰기 실패 재시도 추가.
