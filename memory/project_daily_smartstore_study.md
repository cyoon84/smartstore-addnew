---
name: project_daily_smartstore_study
description: 매일 저녁 구글/네이버에서 스마트스토어 SEO·상세페이지·정책 관련 최신 글을 검색·정독하고, 배운 점을 Slack 다이제스트로 보고하며 LEARNED_RULES 개선안을 제안하는 데일리 자동화 루틴
metadata:
  type: project
---

사용자 지시(2026-07-06): **"매일 저녁마다 구글/네이버에서 스마트스토어 관련 검색 후 공부하면서 개선해보자."**

**목적:** 네이버 스마트스토어 SEO·상세페이지·검색 알고리즘·등록 정책은 자주 바뀐다. 매일 저녁 최신 정보를 학습해 우리 워크플로(§5 상품명·§8/§10 태그·§15 카테고리·§17 상세)를 지속 개선한다.

**루틴 내용:**
1. 구글/네이버(+ WebSearch·insane-search·naver search MCP)에서 "스마트스토어 상위노출/상세페이지/SEO/네이버 AI 검색/등록 정책" 등 최신 글 검색.
2. 유용한 글 2~3편 정독 → 핵심 실행 포인트 추출.
3. **우리 현황과 대조** — 이미 하는 것 / 갭 판정.
4. **Slack `#new-item`에 다이제스트** — 오늘 배운 것 + 우리에게 적용할 구체 개선안 2~3개.
5. 저위험·명백 개선은 LEARNED_RULES/메모리에 바로 반영 제안(큰 변경은 사장님 확인 후).

**구현:** 기존 데일리 자동화(SEO 리프레시 launchd 17:00, [[project_seo_refresh_automation]])와 동일하게 **launchd 저녁 잡**으로 헤드리스 실행. 첫 학습 소스: [tokki-ai.com/blog](https://tokki-ai.com/blog) (6편 정독 완료 → §17-1 체류시간 설계 5요소 도출).

**연관:** [[feedback_detail_styled_deco_template]] · [[feedback_senior_copywriting_mindset]] · LEARNED_RULES §17-1.
