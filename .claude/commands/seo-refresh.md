---
description: 판매중 상품에서 SEO 비부합 2개를 랜덤 선정해 상품명·상세를 재생성하고 Slack 알림
argument-hint: [선택: 개수 N (기본 2), sample M (기본 12)]
---

스마트스토어(finchmart_ca) **판매중 상품 중 네이버 SEO 가이드에 안 맞는 것**을 매일 골라
상품명·상세페이지를 새로 만들고 Slack 으로 알린다. 입력(선택): $ARGUMENTS

너는 오케스트레이터다. 무거운 단계는 서브에이전트(`seo-auditor`·`product-extractor`·`listing-writer`)에
위임하고, 샘플링·선정·저장·Slack·로그는 직접 소유한다. 서브에이전트 spawn 불가 환경이면
각 에이전트 파일을 역할 플레이북으로 읽어 인라인 수행(graceful degradation).

## 파이프라인

1. **샘플 추출** — `python3 scripts/seo_pick.py --sample 12 --seed <오늘날짜YYYYMMDD>` 실행.
   최신 `guide/Product_*.csv`(판매중·전시중, 이미 처리한 건 제외)에서 12개 후보 JSON 을 받는다.

2. **SEO 감사** — 후보 각각을 `seo-auditor` 로 감사(Agent 툴, subagent_type: seo-auditor).
   입력: 후보의 title_ko·category·brand·attributes **+ is_group/group_product_id**. 반환: 판정 + 위반 항목 + 우선순위 점수.
   병렬로 돌려도 됨. **그룹상품(is_group=True)은 상품명 콤마-옵션 형식을 위반으로 보지 않는다**(seo-auditor 규칙).

3. **비부합 2개 선정** — 감사 결과에서 **위반 있는 것만** 우선순위 점수 내림차순 정렬 → 상위 **2개**(인자로 N 주면 N개).
   비부합이 2개 미만이면 `--sample` 키워 한 번 더 추출·감사. 그래도 없으면 "오늘은 비부합 없음" 보고하고 종료.

4. **재생성** — 선정된 2개 각각:
   a. `product-extractor` 로 `live_url`(라이브 listing) 재추출 → 제품 사실(브랜드·사양·특징·원산지). 막히면 CSV 필드 + 이미지로 보강.
   b. `listing-writer` 로 새 상품명·태그 후보·detail.html 작성. **입력에 seo-auditor 의 위반 항목·개선 방향 + is_group 을 그대로 전달.**
      - 🔴 **그룹상품(is_group=True)**: 상품명을 새로 쓰지 않는다. 기존 `<그룹상품명>, <옵션1>, <옵션2>` 형식 **그대로 보존**(그룹명 잠김 [[feedback_naver_group_lock]]). **detail.html(+태그)만** 재생성하고, new_title = old_title 로 둔다.
      - 🟠 **묶음(서로 다른 상품) 플래그**: seo-auditor 가 "서로 다른 상품 묶기 — 수동 분리 필요"로 판정하면, **상품명을 합쳐 재작성하지 않는다.** 재생성을 건너뛰고 Slack 요약에 **"⚠️ 분리 필요(셀러 작업): <상품명>"**로 띄운다. 로그 violations 에 "묶음 — 분리 필요", new_title=old_title.
      - 일반(단일)상품: 상품명도 새로 작성.
   c. **`output/seo_refresh/`** 폴더에 저장: `<ascii_slug>_seo_등록정보.md`(전/후 상품명·위반사유·새 태그·카테고리·그룹여부), `<ascii_slug>_seo_detail.html`.
      ※ `_seo_` 접미사 + 전용 폴더. 가격 재계산은 하지 않는다(상품명·상세만).

5. **로그 기록** — `output/seo_refresh/seo_refresh_log.csv` 에 행 추가 (없으면 헤더 생성):
   `date,product_id,old_title,new_title,violations,detail_path`. 그룹상품은 new_title=old_title, violations 에 "그룹상품(상품명 보존)" 표기. 다음 실행에서 중복 선정 방지.

6. **Slack 알림** — 요약을 만들어 `python3 scripts/slack_notify.py --text "<요약>"` 로 전송.
   요약 형식(상품당):
   ```
   🔧 SEO 리프레시 (YYYY-MM-DD) — 2건
   1) [전] <old_title>
      [후] <new_title>
      위반: <핵심 사유 1~2개>  (그룹상품이면 "그룹상품 — 상세만 개선")
      파일: output/seo_refresh/<slug>_seo_등록정보.md
   2) ...
   ```

## 규칙
- 부합 상품을 억지로 건드리지 않는다(seo-auditor 가 "부합" 판정하면 제외). 멀쩡한 걸 바꾸면 SEO 손해.
- 데이터 진실성(§9): 재추출 안 된 사양은 비워둠. 가짜 데이터·미검증 활용팁 금지.
- 상품명 §5, 태그 §8/§10, detail.html §7(베어 fragment) 규칙 그대로.
- 가격·발송 설정은 건드리지 않는다(상품명·상세 SEO 만 대상).
- 진행 단계는 TodoWrite 로 기록.
