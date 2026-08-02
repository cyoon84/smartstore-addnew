#!/usr/bin/env python3
"""네이버 데이터랩 — 수요(§0-D) 판정용.

검색 API 의 `shop.json` 은 2026-07 기준 404 SE05 로 사망했지만
**데이터랩(검색어트렌드 · 쇼핑인사이트)은 정상**이다. 가격은 kr_price_check.py(다나와),
수요는 이 스크립트로 나눠서 본다.

크리덴셜: ~/.config/finchmart/naver_api.json (리포 커밋 금지)

사용:
    # 검색어 트렌드 — 여러 키워드 상대 비교 (100 = 구간 내 최대)
    python3 scripts/naver_datalab.py trend "프링글스" "스키틀즈" [--months 12]

    # 브랜드 한글표기 확정용 (§2 — 검색량 최다 표기 채택)
    python3 scripts/naver_datalab.py trend "애티튜드" "에티튜드"

    # 쇼핑인사이트 — 특정 카테고리 안에서 키워드 클릭추이
    python3 scripts/naver_datalab.py shopping "스키틀즈" --cat 50000006

    # 성별·연령 분해
    python3 scripts/naver_datalab.py shopping "프링글스" --cat 50000006 --by gender

주요 카테고리 코드: 식품 50000006 · 생활건강 50000008 · 화장품미용 50000002
                  출산육아 50000005 · 패션잡화 50000001 · 스포츠레저 50000007
"""
import argparse
import calendar
import datetime as _dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# NAVER API HUB 우선 · 개발자센터 폴백 (scripts/naver_api.py 가 처리)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import naver_api as NV


def post(path, body):
    """path: 'search' | 'shopping/category/keywords'"""
    try:
        if path == "search":
            return NV.trend([g["groupName"] for g in body["keywordGroups"]],
                            body["startDate"], body["endDate"], body["timeUnit"])
        return NV.shopping_keywords(body["category"],
                                    [k["name"] for k in body["keyword"]],
                                    body["startDate"], body["endDate"], body["timeUnit"])
    except NV.NaverAPIError as e:
        sys.exit(str(e))


def span(months, today=None):
    """오늘 기준 N개월 구간. 데이터랩은 전일까지만 제공하므로 어제를 끝으로."""
    end = (today or _dt.date.today()) - _dt.timedelta(days=1)
    y, m = end.year, end.month - months + 1
    while m <= 0:
        m += 12
        y -= 1
    return f"{y}-{m:02d}-01", end.isoformat()


def bar(v, w=34):
    return "█" * max(0, round(v / 100 * w))


def show(results, label):
    print(f"\n{label}  (100 = 구간 내 최대)\n")
    peak = {}
    for g in results:
        t = g.get("title") or g.get("keyword", "?")
        data = g.get("data", [])
        if not data:
            print(f"  {t:<18} (데이터 없음 — 검색량 미미)")
            continue
        peak[t] = max(d["ratio"] for d in data)
        last = data[-1]["ratio"]
        print(f"  {t:<18} 최근 {last:>5.1f}  최대 {peak[t]:>5.1f}  {bar(last)}")
    if len(peak) > 1:
        top = max(peak, key=peak.get)
        print(f"\n  → 최다: '{top}'")
        for k, v in sorted(peak.items(), key=lambda x: -x[1])[1:]:
            if v > 0:
                print(f"     '{top}' 이 '{k}' 의 {peak[top]/v:.1f}배")
            else:
                print(f"     '{k}' 는 사실상 0 (검색 수요 없음)")
    print("\n  ⚠️ 상대지수다. 절대 검색량이 아니라 '구간 내 최대 대비 비율'이라")
    print("     키워드 간 비교는 유효하지만 다른 조회 결과와는 비교 불가.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["trend", "shopping"])
    ap.add_argument("keywords", nargs="+")
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--cat", default="50000006", help="쇼핑인사이트 카테고리 코드 (기본 식품)")
    ap.add_argument("--by", choices=["age", "gender", "device"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    s, e = span(a.months)
    if a.mode == "trend":
        body = {"startDate": s, "endDate": e, "timeUnit": "month",
                "keywordGroups": [{"groupName": k, "keywords": [k]} for k in a.keywords[:5]]}
        d = post("search", body)
        label = f"■ 검색어 트렌드 ({s} ~ {e})"
    else:
        path = "shopping/category/keywords"
        body = {"startDate": s, "endDate": e, "timeUnit": "month", "category": a.cat,
                "keyword": [{"name": k, "param": [k]} for k in a.keywords[:5]]}
        if a.by:
            path += "/" + a.by
            body["keyword"] = body["keyword"][:1]      # 분해 조회는 키워드 1개
        d = post(path, body)
        label = f"■ 쇼핑인사이트 category={a.cat} ({s} ~ {e})" + (f" · {a.by} 분해" if a.by else "")

    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        show(d.get("results", []), label)


if __name__ == "__main__":
    main()
