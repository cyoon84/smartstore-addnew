---
name: project_agents_overview
description: smartstore-addnew 서브에이전트 5종 + 오케스트레이터 커맨드 로스터·역할 (Claude Code 데스크톱 전용)
metadata:
  type: project
---

서브에이전트는 **Claude Code 데스크톱 전용**([[feedback_subagent_env_split]]). 모바일 dispatch(Cowork)는 인라인.

## 서브에이전트 (`.claude/agents/`)
- **market-strategist** (신규) — 수요(충분히 팔리는지)·경쟁구도(해외직구 vs 국내)·**네이버 쇼핑 랭킹 상위 진입 전략**(적합도·인기도·신뢰도 3축). 읽기 전용. listing 재료(키워드축·셀링포인트·카테고리·가격 포지셔닝) 반환.
- **market-researcher** — §0-A 채널별 최저가 가격 경쟁력(쿠팡·네이버쇼핑). market-strategist 와 **보완**(가격 정밀비교 전담).
- **product-extractor** — 쇼핑 URL 크롤 → product_info JSON(가격필드 제외).
- **listing-writer** — 상품명·태그·카테고리·detail.html 작성(가격·전략 재료 입력).
- **seo-auditor** — 판매중 상품 SEO 감사(그룹 §13-1·묶음 §13-3·국가명 중복 규칙 인지).

## 오케스트레이터 커맨드 (`.claude/commands/`)
- **/register-agents** — 사진/URL+가격 → 등록 4종(researcher→extractor→writer). GO게이트·가격계산·저장·Slack 은 메인.
- **/market-launch** (신규) — 제품 → market-strategist(조사+랭킹전략, GO게이트) → (가격이면 researcher+price_calc) → listing-writer → `output/new-item/<slug>/` 저장 → Slack. "바로 올릴 제품정보+상세" 생성.
- **/seo-refresh** — 매일 17:00 launchd, 판매중 2개 SEO 감사·재생성([[project_seo_refresh_automation]]).
- 기존 /register, /price, /learn 유지.

**공통 규칙:** 가격은 `price_calc.py` 단일소스 / GO게이트 전 산출물 X / 저장은 루트→`organize_output.py`→new-item/<slug>/ / Slack 은 `slack_notify.py`(mrkdwn 변환) / 서브에이전트는 사용자에게 못 물음(확인·GO 는 메인).
