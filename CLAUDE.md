# smartstore-addnew — 네이버 스마트스토어(finchmart_ca) 상품 등록 에이전트

이 폴더는 캐나다/미국 → 한국 리셀러용 스마트스토어 상품 등록 워크플로를
Claude Code 에이전트로 운영하기 위한 프로젝트다. 이 `CLAUDE.md` 는 세션 시작 시
자동 로드된다. 아래 규칙은 **항상 적용**되며, 상세 규칙은 `@docs/...` 로 임포트한다.

스토어 ID: **finchmart_ca** · 상품 URL 패턴은 @memory/reference_smartstore_id.md 참고.

---

## 0. 무엇을 하는가

사용자가 **사진/URL + 가격 정보**를 주면 한 SKU에 대해 다음 4종 산출물을 만든다:

1. `<slug>_등록정보.md` — 네이버 등록용 전체 정보 (상품명·가격·태그·카테고리·배송)
2. `<slug>_detail.html` — 네이버 에디터 붙여넣기용 베어 HTML fragment
3. `<slug>_product_info.json` — 구조화 데이터 (가격 산식·검산 포함)
4. (참고 이미지) `<slug>_*.jpg`

URL 크롤 → 추출 → 가격 산정 → 렌더 파이프라인은 **`product-detail-page-ko` 스킬**이
담당한다 (`.claude/skills/product-detail-page-ko/`). 쇼핑 URL 이 들어오면 이 스킬을 쓴다.

---

## 1. 입력 받기

필요 항목: 사진/URL, 제품 원가, HST 적용여부, 배송비, 남기고 싶은 마진(% 또는 $), 모드(single/group).

폰에서 빠른 입력(dispatch)은 한 줄/블록 형식 둘 다 지원 — 빠진 항목만 묻고 모드 누락은
single 기본. 형식은 @docs/LEARNED_RULES.md §0-B, @memory/feedback_dispatch_template.md 참고.

**실행 엔진 플래그 (dispatch·일반 메시지 공통):** 입력에 **`엔진: agents`** (블록) 또는 끝에
**`/ agents`**·**`에이전트`** 토큰(한 줄)이 있으면 **서브에이전트 모델**로 실행한다 — 그때는
`.claude/commands/register-agents.md` 의 오케스트레이션(시세조사·추출·작성을 전문 에이전트에
위임, 가격계산·GO게이트·저장·Slack 은 메인이 소유)을 **읽어서 그대로 따른다**. 플래그가 없으면
아래 §2 기본 워크플로로 진행 (기존 동작 유지). dispatch 는 슬래시 커맨드를 확장하지 못하므로
이 플래그가 유일한 서브에이전트 진입점이다. **서브에이전트 spawn 이 불가한 환경(Cowork 등)에서는
메인이 세 에이전트 파일을 역할 플레이북으로 읽어 인라인 수행한다 (register-agents.md "실행 환경" 절).**

---

## 2. 워크플로 (순서 고정)

> 입력에 `엔진: agents` 플래그가 있으면 이 §2 대신 `.claude/commands/register-agents.md` 의
> 서브에이전트 오케스트레이션을 따른다 (위 §1 엔진 플래그 규칙). 산출물·규칙은 동일.

1. **국내 시세 먼저 확인 (§0-A, 필수).** 산출물 만들기 전에 쿠팡·네이버쇼핑에서 동일/유사
   SKU 시세를 확인하고 "가격 경쟁력 있음/박빙/안 됨" 한 줄 판단 + A)진행 B)가격조정 C)접기
   선택지를 제시한다. **명시적 GO 받은 뒤에만** 산출물 생성. 단, 사용자가 "한국 미출시/국내에
   안 판다"고 하면 스킵하고 "국내 미유통 — §0-A 스킵 적용" 1줄 명시.
2. 가격 규칙 확정 → **가격은 반드시 `scripts/price_calc.py` 로 계산** (§4 참고). 손계산 금지.
3. (URL 있으면) 스킬로 페이지 크롤·추출.
4. 상품명·태그·카테고리·상세본문 작성 (§5~§7 규칙).
5. 산출물 4종을 `output/` 에 평탄 저장 (§3).
6. 완료 후 `등록정보.md` 전체를 Slack `#new-item` 채널에 전송 (@memory/feedback_slack_delivery.md).

---

## 3. 출력 위치·파일명 규칙

- 저장 폴더: **`output/new-item/<ascii_slug>/`** (등록상품 제품별 폴더, 2026-05-31 변경 — 평탄→제품폴더). Downloads 사용 X.
- 파일명은 **ASCII 슬러그 prefix**: `<ascii_slug>_detail.html`, `<ascii_slug>_product_info.json`,
  `<ascii_slug>_등록정보.md`, 참고 이미지 `<ascii_slug>_*.jpg`. 한국어는 파일 **내용**에만.
- 저장 절차: 산출물을 **`output/` 루트에 슬러그 prefix로 쓴 뒤 `python3 scripts/organize_output.py --apply`** 실행 → `output/new-item/<slug>/` 로 자동 분류(반복 안전, 기존 슬러그 매칭+신규 폴더 생성). 같은 슬러그는 덮어쓰기.
- output/ 루트 구성: `new-item/`(등록상품), `seo_refresh/`(SEO 리프레시 §13-2), `cron_logs/`(로그), `new-item/_misc/`(슬러그 미매칭 참고이미지).

---

## 4. 가격 계산 — 항상 스크립트로 (절대 규칙)

가격 산식은 오류나기 쉬워 **`scripts/price_calc.py` 로 고정**했다. 직접 암산/필산하지 말고
해당 모드를 호출해서 나온 `sell_krw`·검산값을 그대로 쓴다. 공통: 네이버 수수료 6.6% gross-up.

| 사용자 입력 신호 | 모드 | 예시 |
|---|---|---|
| 세전 원가 + 마진(+세율) | `std` | `std --cost 12.99 --markup 5 --fx 1083 --tax 0` |
| "원가 HST 포함/tax-in" | `hst_incl` | `hst_incl --cost 16.99 --markup 3 --fx 1070 --tax 13` |
| "네이버에 N원에 올려" | `target_krw` | `target_krw --target 8000 --fx 1070` |
| "N CAD 로 맞춰" | `target_cad` | `target_cad --target 8 --fx 1070` |
| 목표 KRW + 원가 → 마진 역산 | `reverse` | `reverse --target 29900 --cost 16.99 --tax 13 --fx 1090` |
| "수수료 감안 N%" | `pct_net` | `pct_net --cost 6.97 --pct 30 --fx 1100 --tax 0` |
| 배송비 수량당 N원(묶음X) | `shipping` | `shipping --unit 5000 --qty 3` |

`--json` 을 붙이면 `product_info.json` 의 pricing 블록에 그대로 넣을 dict 가 나온다.
환율(`--fx`)은 **현재 시점 CAD→KRW 환율을 확인해서** 넣는다. 단위(CAD vs KRW) 애매하면
**먼저 사용자에게 확인** (§6 단위 해석 규칙). 각 모드의 산식 근거는 @docs/pricing_rules.md.

---

## 5. 상품명 규칙

- 50자 내외, 네이버 SEO 가이드 준수 (@memory/feedback_naver_title_seo_guide.md).
- 수치 사양은 라벨 결합 (23g → 단백질23g). 동의어 중복·판매처명 금지.
- 끝 출처 태그: **상품명에 국가(캐나다/미국)는 넣지 않는다** — 네이버가 원산지 필드 값을 `[원산지:캐나다]`로
  자동 표시하므로 중복(2026-05-31 갱신). 매장 한정 SKU만 매장명("코스트코") 유지, "정품"은 항상 제외
  (@memory/feedback_title_source_tag.md). 상품명에 넣은 출처는 본문에서 반복 X.
- 브랜드 한글 표기는 네이버 검색량 기준 (예: Chosen Foods → 초슨푸드).
- **모델명 필드 = 영어 원래 제품명**(공식 풀네임) 입력 — 영어/로마자 검색 매칭 + 적합도↑. 그룹은 옵션별 모델명 따로. **크롤 가능 환경(Cowork dispatch·URL)은 소스(Walmart 등)에서 직접 추출, 크롤 차단(데스크톱 사진만)이면 사용자에게 소스 확인 요청** — 추측 단정 금지(§9). (2026-05-31)

## 6. 가격/세금/단위 해석

- 세금은 **매번 물어본다** — 카테고리만 보고 자동 적용 금지. 사용자 제공 가격은 세전 가정.
- 참고 세율: 일반 13% / 소스·커피·쿠키 0% / 키즈의류·신발 5% (@memory/reference_hst_zero_rated.md).
- "N$/N불" 단위가 애매하면 한국 판매가 맥락에선 ₩N,000 1차 가정 후 확인 (LEARNED_RULES §6-1).

## 7. 상세페이지(detail.html) 포맷

- **베어 fragment.** 허용 태그 `<p> <strong> <br>` + 이모지만. `<div><style><script><table>
  <article><ul><h1~6><img>` 등 전부 금지 (네이버 에디터에서 제거됨).
- 섹션: 헤드라인 → 영문 부제 → 소개 → 핵심 포인트 → "이런 점이 좋아요" → "이런 분들께 추천".
- **제외:** 배송 안내, 마무리 인사 한 줄, 스펙 테이블, footer, 검증 안 된 활용 팁/레시피.
- 이미지는 HTML 에 박지 않고 URL 리스트로 등록정보.md 에 분리.
- 그룹상품은 옵션별 분리 X, 통합 1장. 자세한 포맷은 @docs/cowork_instructions_patch.md §5.

## 8. 네이버 태그 (10개)

(1) 차단 패턴(카테고리·브랜드·판매처명 단독) 거름 → (2) 검색량 검증된 키워드로 채움 →
(3) 직구 표현은 "직수입" 통일. 통과/거부 누적 사전은 @docs/LEARNED_RULES.md §10.
적용 불확실한 후보는 12~15개 넉넉히 제시하고 사용자가 입력 화면에서 확정.

## 9. 데이터 진실성

추출 안 된 필드는 **비워둠** — 그럴듯한 가짜 데이터 절대 금지. 리셀러가 고객용으로 그대로
올리므로 부정확한 활용 팁/원재료는 컴플레인·반품 리스크. 제조국 미명시면 원산지 단정 금지
(@memory/feedback_origin_vs_release_market.md).

---

## 학습 규칙 (전체) — 새 규칙 생기면 여기 + LEARNED_RULES 둘 다 갱신

@docs/LEARNED_RULES.md

## 메모리 인덱스

@memory/MEMORY.md
