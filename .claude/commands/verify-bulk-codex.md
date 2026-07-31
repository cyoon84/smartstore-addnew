---
description: Codex를 독립 읽기 전용 QA로 호출해 일괄등록 엑셀을 검증
argument-hint: <엑셀 경로> <slug> [slug ...]
---

일괄등록 엑셀을 Codex 독립 QA에게 위임해 검증한다. 입력: `$ARGUMENTS`

## 실행

1. 입력에서 첫 번째 값을 엑셀 경로, 나머지를 대상 SKU 슬러그로 해석한다.
2. 아래 명령을 실행한다.

```bash
bash scripts/verify_bulk_with_codex.sh <엑셀 경로> <slug> [slug ...]
```

3. 생성된 `output/verification/<엑셀명>_codex_report.md`를 읽고 사용자에게 결과를 요약한다.

## 판정 후 처리

- `VERDICT: PASS`: 업로드 가능 단계로 진행한다.
- `VERDICT: FAIL`: 보고서가 구분한 책임에 따라 수정한다.
  - 상품명·태그·detail 등 콘텐츠 문제 → listing-writer 재호출
  - 가격·이미지·관부가세·엑셀 매핑 문제 → 메인 오케스트레이터가 수정
- 수정 후 엑셀을 재생성하고 같은 명령으로 다시 검증한다.
- PASS 전에는 Slack 완료 전송이나 업로드 가능 안내를 하지 않는다.

Codex 검수 단계에서는 파일 수정, 커밋, 푸시를 허용하지 않는다.
