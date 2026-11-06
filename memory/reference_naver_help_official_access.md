---
name: reference_naver_help_official_access
description: help.sell.smartstore.naver.com 내비게이션 구조로 1차 소스(FAQ 카테고리·공지) 접근 경로 확보 — "등록 정보 검토" 공식 FAQ 카테고리(11139) 발견, 단 상세 본문은 JS/Vue SPA라 engine으론 못 열림
metadata:
  type: reference
---

**배경:** 등록정책/검토필요 관련 서드파티 블로그(tokki-ai·sellerking.io 등)의 주장을 여러 번 검증하려 했지만
네이버 공식 공지·FAQ 원문은 계속 403/로그인월/SPA 라우트로 막혔다([[reference_naver_category_reorg_2026]]
2026-11-04 학습에서 `index.help`의 "최근 공지 10건" 위젯까지는 insane-search engine으로 뚫렸음).

**2026-11-05 — `index.help`의 좌측 내비게이션 전체가 FAQ 카테고리 링크 트리임을 확인:**

```bash
python3 -m engine "https://help.sell.smartstore.naver.com/index.help" --selector "a"
```

이 페이지의 `<a href="/faq/list.help?categoryId=N">` 링크들이 **판매자센터 메뉴 전체의 공식 분류 트리**다.
우리와 관련된 주요 categoryId:

| categoryId | 분류 |
|---|---|
| 541 | 상품 등록 |
| 542 | 상품 일괄등록 |
| 811 | 상품정보 검색품질(SEO) |
| **11139** | **등록 정보 검토** |
| 11140 | 검색 순위 진단 |
| 848 | 카탈로그 가격관리 |

**`categoryId=11139`("등록 정보 검토") 페이지까지는 engine으로 열렸고, 그 안의 FAQ 제목 목록(`data-content-no`)을
1차 소스로 확보:**

```bash
python3 -m engine "https://help.sell.smartstore.naver.com/faq/list.help?categoryId=11139"
```

| content-no | 제목 |
|---|---|
| 16889 | [등록 정보 검토] 상품 분석 기준이 어떻게 되나요? |
| 16890 | [등록 정보 검토] 신규로 등록한 상품이 등록 정보 검토 목록에서 보이지 않습니다. 왜 그런가요? |
| 16891 | [등록 정보 검토] 등록 정보 검토에서 노출되는 항목들은 필수로 수정을 해야 하나요? |
| 16892 | [등록 정보 검토] 항목별 노출되는 수정 버튼은 어떻게 표시되나요? |
| 16893 | [등록 정보 검토] 태그를 많이 등록하면 좋은가요? |
| 16894 | [등록 정보 검토] 등록 정보 검토 메뉴가 보이지 않습니다. 왜 그런가요? |

**🚨 한계 — 개별 FAQ 답변 본문은 못 열린다.** 목록 페이지의 `<a class="openable increase-content-read-count"
data-content-no="N">`는 클릭 시 JS로 AJAX 로드되는 아코디언이고, `/faq/content.help?faqId=N`·
`/faq/view.help?contentNo=N` 둘 다 시도했으나 둘 다 목록 페이지 자체를 다시 반환할 뿐 답변 텍스트는
안 나온다(정확한 AJAX 엔드포인트를 `.js` 리소스에서 못 찾음). **Playwright(브라우저 렌더)가 있어야
실제 답변 본문을 읽을 수 있다** — 이 환경엔 chrome-devtools MCP가 연결 안 돼 있어 다음에 가능한
세션(computer-use·claude-in-chrome 등 실브라우저 도구 연결된 세션)에서 재시도할 것.

**지금 당장 쓸 수 있는 것:** 제목 목록 자체가 "등록 정보 검토가 실존하는 공식 메커니즘이며, 네이버가
명시적으로 분류한 질문이 ①분석 기준 ②목록 노출 지연 ③필수수정 여부 ④수정 UI ⑤**태그 과다 등록**
⑥메뉴 비노출"이라는 사실은 확인됐다 — 이건 tokki-ai·sellerking.io 등의 "모델명/인증/원산지/AS/
미성년자 5개 필수" 주장을 반증하지도 완전히 증명하지도 않지만, "태그를 많이 등록하면 좋은가요?"가
네이버 스스로 FAQ로 만들 만큼 흔한 질문이라는 점은 §10 "10개 꽉 채우기 vs 5~7개" 논쟁에 참고가 된다
(답변 본문 미확보라 결론은 못 내림, 계속 보류 중인 §10 정책 유지).

**공지사항(개별 상세)도 같은 한계:** `index.help`의 "최근 10건" 목록은 열리지만, 개별 공지 상세는
`sell.smartstore.naver.com/#/center-notice/detail/N` 형태의 **Vue SPA 해시라우트**라 서버가 해시 뒤
콘텐츠를 다르게 안 내려줘서 engine/WebFetch 전부 무효. Playwright만 유효.

**How to apply:** 앞으로 등록정책/검토필요/태그 세션에서 1차 소스를 노리면 이 categoryId 트리부터
`list.help`로 열어 FAQ 제목을 스캔하고, 답변 본문이 필요하면 Playwright 연결된 세션으로 넘긴다
(메인 세션에 chrome-devtools 등 실브라우저 MCP가 연결돼 있는지 매번 확인). 서드파티 블로그보다
이 경로가 항상 우선.
