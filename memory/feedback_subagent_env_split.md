---
name: feedback_subagent_env_split
description: 서브에이전트 모델은 Claude Code 데스크톱 전용. 모바일 현장 사진 dispatch 는 기존 Cowork 플로 그대로 — 두 환경 안 섞음
metadata:
  type: feedback
---

상품 등록 워크플로의 실행 환경은 둘로 갈라 운영한다 (2026-05-30 결정):

- **모바일 현장(사진 찍어서) → Cowork dispatch** = 기존 그대로. 서브에이전트 흉내/플래그 안 씀. Cowork 는 별도 컨텍스트 서브에이전트 spawn 기능이 없고 `.claude/agents/` 도 안 읽으므로, 거기에 `엔진: agents` 라우팅을 심지 않는다. (한 번 넣었다가 사용자 요청으로 되돌림.)
- **데스크톱 실험 → Claude Code `/register-agents`** = 진짜 서브에이전트(`market-researcher`·`product-extractor`·`listing-writer`)가 Agent 툴로 실제 spawn·격리되는 유일한 경로.

**Why:** 모바일 dispatch 는 Cowork 워크스페이스(`/Volumes/External/claude/smartstore-project/`)에 떨어지고 산출물도 거기 `output/` 에 저장된다. Cowork 의 "서브에이전트로 돌린다" narration 은 실제 위임이 아니라 인라인 수행을 그렇게 서술한 것일 뿐 — 진짜 격리는 Claude Code 에서만 일어난다.

**How to apply:** 서브에이전트/오케스트레이션 관련 변경은 `smartstore-addnew/.claude/`(Claude Code) 안에서만. Cowork `instructions.md` 엔 손대지 않는다. output 폴더 두 개 주의 — Claude Code=`smartstore-addnew/output/`, Cowork=`smartstore-project/output/`. 관련 [[feedback_output_location]], [[feedback_dispatch_template]].
