# smartstore-addnew

네이버 스마트스토어(**finchmart_ca**) 상품 등록 워크플로를 **Claude Code 에이전트**로
운영하는 프로젝트. 기존 Cowork 프로젝트(`instructions.md` 를 앱 설정란에 붙여넣던 방식)를
폴더에서 바로 도는 코드 프로젝트로 변환한 것.

## 쓰는 법

이 폴더를 Claude Code 로 연다:
```bash
cd smartstore-addnew
claude
```
`CLAUDE.md` 가 세션 시작 시 자동 로드돼 워크플로·가격규칙·학습규칙이 전부 적용된다.

슬래시 명령:
- `/register <사진/URL + 가격>` — 등록 4종 산출물 생성 (전체 워크플로)
- `/price <원가/마진/환율 또는 목표가>` — 판매가만 즉시 계산
- `/learn <새 규칙>` — 배운 규칙을 LEARNED_RULES + memory 에 반영

## 구조

| 경로 | 내용 |
|------|------|
| `CLAUDE.md` | **중앙 에이전트 지침** (자동 로드). 워크플로·출력규칙·가격·상품명·태그·진실성 |
| `.claude/skills/product-detail-page-ko/` | URL 크롤 → 추출 → 렌더 스킬 |
| `.claude/commands/` | `/register` `/price` `/learn` 슬래시 명령 |
| `.claude/settings.json` | 프로젝트 권한 설정 |
| `scripts/price_calc.py` | **결정론적 가격 산정 엔진** (§1~§12 산식 코드화) |
| `scripts/test_price_calc.py` | 회귀 테스트 (LEARNED_RULES 실제 6케이스) |
| `docs/LEARNED_RULES.md` | 누적 학습 규칙 전문 (CLAUDE.md 가 import) |
| `docs/pricing_rules.md` | price_calc.py 모드별 산식 스펙 |
| `docs/instructions_original.md`, `docs/cowork_instructions_patch.md` | 원본 Cowork 지침 보관 |
| `memory/` | 학습 규칙 메모리 (MEMORY.md 인덱스 + feedback/reference) |
| `products_master.csv` | 등록 상품 마스터 |
| `output/` | 생성 산출물 (`.gitignore` 제외) |

## 가격 엔진

가격 산식은 손계산 오류가 잦아 `scripts/price_calc.py` 로 고정했다. 7개 모드
(std / hst_incl / target_krw / target_cad / reverse / pct_net / shipping).
```bash
python3 scripts/price_calc.py std --cost 12.99 --markup 5 --fx 1083 --tax 0
python3 scripts/test_price_calc.py   # 12/12 통과
```
산식 근거는 `docs/pricing_rules.md`, 전체 케이스는 `docs/LEARNED_RULES.md`.

## Cowork 프로젝트와의 관계

기존 Cowork 프로젝트(`smartstore-project` 폴더)는 **그대로 유지**된다. 이 폴더는 같은
지식(지침·스킬·메모리·학습규칙)을 Claude Code 구조로 옮긴 독립 사본이다. 규칙이 갱신되면
`/learn` 으로 이 폴더의 LEARNED_RULES + memory 를 갱신한다.

## Git (비공개 권장)

가격 규칙·스토어 ID 등 사업 정보가 있으므로 **private 저장소**로:
```bash
git init && git add -A && git commit -m "init: Claude Code agent structure"
```
