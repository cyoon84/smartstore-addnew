---
name: project_youtube_shorts_workflow
description: youtube-shorts-test 협업 — 스마트스토어 제품 세로 쇼츠(나레이션+자막) 만드는 워크플로
metadata:
  type: project
---

**smartstore-addnew × youtube-shorts-test 협업** — 등록 제품의 실촬영 클립으로 유튜브 세로 쇼츠(1080×1920) 제작. 프로젝트: `/Volumes/External/claude/youtube-shorts-test` (엔진 `shorts.mjs`, Node 내장모듈만 씀 → npm install 불필요, ffmpeg는 `bin/` 번들, .env에 ELEVENLABS_API_KEY).

**만드는 법:** `raw/<이름>/` 에 ① 세로 클립들(이름순 이어붙음) ② `script.txt`(문장당 1줄=나레이션+하단자막) → `node shorts.mjs "raw/<이름>"` → `output/<이름>.mp4`. TTS는 ElevenLabs, 매 실행 재생성(느림, ~2min+ → 타임아웃 300s).
- **overlays.json**: `{image, line, width, y}` — 특정 나레이션 **줄(line)** 동안 이미지 팝업(흰테+페이드). 줄 단위라, 한 줄에 여러 이미지 순차 띄우려면 그 줄을 여러 줄로 쪼갠다(예: 매운맛 마일드/미디엄/스파이시를 3줄로 → 맛별 제품샷).
- **texts.json**: 음성없는 텍스트(title/note).  `shorts.mjs` 상단: `VOICE_ID`(기본 George), `SPEED`(1.0=원본), `FADE_OUT`.

**🔑 학습 (KD 라면 쇼츠, 2026-07-10):**
- **음성 = George** (스마트스토어 채널용 = 사장 본캐 목소리 X, 기본값 그대로 OK).
- **존댓말(해요체)** — 스토어 공식 채널이라 반말 X.
- **가로 클립(1920×1080) → 세로 변환**: ffmpeg 블러배경(split→bg scale+crop+boxblur, fg scale=1080:-2 overlay center). 각 클립 트림(5~6초)해서 총길이=나레이션 근처로(전체 몽타주). 원본 오디오는 버리고 나레이션 대체.
- **정지 방지**: 나레이션>영상이면 shorts.mjs가 끝프레임 정지(tpad) → 클립을 길게(6초) 만들고, 렌더 후 **나레이션 끝+0.8초로 트림**해 정지·긴무음 없이.
- **조리법·사실 정확히(§9)**: "완성이에요"처럼 실제와 다른 단정 금지. 실제 조리(끓인물 6분→물따라내고 소스섞기)를 그대로. 브랜드/제조사(크래프트 디너/하인즈) 정확히.
- **🔑 기대 vs 현실 = 솔직한 소재**: 실촬영이 실패(물조절 실패로 국물 남음)면 숨기지 말고 **공홈 조리예시 사진 인서트 + "내 현실.. 물조절 실패 ㅠㅠ"**(GamjaFlower 손글씨체) 대조. 날조보다 진솔이 MZ 감성·신뢰. gag는 **1~2초만 짧게, 끝 페이드아웃 시작 전에 종료**(안 그러면 페이드 때 텍스트만 밝게 잔상). 재렌더 없이 완성본에 ffmpeg overlay+drawtext로 얹을 수 있음(단 페이드 위에 얹으면 잔상 → 깨끗한 베이스에 gag+페이드 한 번에).
- **컷별 나레이션 매핑**(수정용): work/<이름>/line_N.mp3 길이 ffprobe → LEAD1.2+누적+GAP0.35로 줄별 시각 계산 → 5~6초 클립에 매핑.

[[project_sns_mz_croket_style]] · [[feedback_senior_copywriting_mindset]] · [[reference_kd_ramen]]
