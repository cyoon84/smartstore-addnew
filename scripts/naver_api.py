#!/usr/bin/env python3
"""네이버 API 공용 클라이언트 — NAVER API HUB(NCP) 우선, 개발자센터 폴백.

배경 (2026-07-31):
  네이버 개발자센터 공지 32530 으로 **쇼핑·책·전문자료 검색 API 가 2026-07-31 영구 종료**됐다
  (대체 없음). 나머지 검색 API·검색어트렌드·쇼핑인사이트는 **NAVER API HUB 로 이관**되며
  개발자센터 지원은 **2027-06-30 까지**다. 그래서 이 모듈은 API HUB 를 기본으로 쓰고,
  실패하면 개발자센터 키로 폴백한다.

크리덴셜 (둘 다 ~/.config/finchmart/, chmod 600, 리포 커밋 금지):
  naver_apihub.json  {"client_id","client_secret"}   ← API HUB (NCP)
  naver_api.json     {"client_id","client_secret"}   ← 개발자센터 (레거시, 2027-06-30 만료)

API HUB 엔드포인트 (2026-07-31 실측 확인):
  검색          GET  /search/v1/{blog|webkr|image|news|kin|cafearticle|encyc}
  검색어트렌드   POST /search-trend/v1/search
  쇼핑인사이트   POST /shopping/v1/categories
                POST /shopping/v1/category/keywords
  ※ shop·book·doc 은 API HUB 에도 없음 (404) — 국내 시세는 scripts/kr_price_check.py(다나와) 사용
  ※ 콘솔에서 체크하지 않은 API 는 401 "이 Application에서 활성화되어 있지 않음" 을 돌려준다
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONF_DIR = Path.home() / ".config" / "finchmart"
HUB_BASE = "https://naverapihub.apigw.ntruss.com"
LEGACY_BASE = "https://openapi.naver.com/v1"

# 개발자센터에서 영구 종료된 검색 종류 (API HUB 에도 없음)
DEAD_KINDS = {"shop", "book", "doc"}

HUB_SEARCH = "/search/v1/{kind}"
HUB_TREND = "/search-trend/v1/search"
HUB_SHOP_CATS = "/shopping/v1/categories"
HUB_SHOP_KEYWORDS = "/shopping/v1/category/keywords"


class NaverAPIError(RuntimeError):
    pass


def _creds(name):
    p = CONF_DIR / name
    if not p.exists():
        return None
    c = json.loads(p.read_text())
    return c.get("client_id"), c.get("client_secret")


def _hub_headers(json_body=False):
    c = _creds("naver_apihub.json")
    if not c:
        return None
    h = {"X-NCP-APIGW-API-KEY-ID": c[0], "X-NCP-APIGW-API-KEY": c[1]}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def _legacy_headers(json_body=False):
    c = _creds("naver_api.json")
    if not c:
        return None
    h = {"X-Naver-Client-Id": c[0], "X-Naver-Client-Secret": c[1]}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def _call(url, headers, body=None, timeout=15):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def search(kind, query, display=20, start=1, sort=None):
    """검색 API. API HUB 우선, 실패 시 개발자센터 폴백."""
    if kind in DEAD_KINDS:
        raise NaverAPIError(
            f"'{kind}' 검색 API 는 2026-07-31 영구 종료됐다 (네이버 공지 32530, 대체 없음).\n"
            f"국내 시세는 `python3 scripts/kr_price_check.py \"<검색어>\"` (다나와) 를 쓸 것.")
    params = {"query": query, "display": display, "start": start}
    if sort:
        params["sort"] = sort
    qs = urllib.parse.urlencode(params)

    h = _hub_headers()
    if h:
        try:
            return _call(f"{HUB_BASE}{HUB_SEARCH.format(kind=kind)}?{qs}", h)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:160]
            if e.code != 401:
                raise NaverAPIError(f"API HUB {e.code}: {detail}")
            hub_err = detail          # 401 = 콘솔 미활성 → 폴백 시도
    else:
        hub_err = "크리덴셜 없음"

    h = _legacy_headers()
    if not h:
        raise NaverAPIError(f"API HUB 실패({hub_err}) + 개발자센터 크리덴셜 없음")
    try:
        return _call(f"{LEGACY_BASE}/search/{kind}.json?{qs}", h)
    except urllib.error.HTTPError as e:
        raise NaverAPIError(
            f"API HUB 401({hub_err}) → NCP 콘솔에서 '{kind}' API 를 활성화할 것.\n"
            f"개발자센터 폴백도 실패: {e.code} {e.read().decode()[:120]}")


def trend(keywords, start_date, end_date, time_unit="month"):
    """검색어 트렌드 (상대지수 100 = 구간 내 최대)."""
    body = {"startDate": start_date, "endDate": end_date, "timeUnit": time_unit,
            "keywordGroups": [{"groupName": k, "keywords": [k]} for k in keywords[:5]]}
    h = _hub_headers(True)
    if h:
        try:
            return _call(HUB_BASE + HUB_TREND, h, body)
        except urllib.error.HTTPError as e:
            if e.code != 401:
                raise NaverAPIError(f"API HUB {e.code}: {e.read().decode()[:160]}")
    h = _legacy_headers(True)
    if not h:
        raise NaverAPIError("검색어트렌드 호출 불가 — 크리덴셜 확인")
    return _call(f"{LEGACY_BASE}/datalab/search", h, body)


def shopping_keywords(category, keywords, start_date, end_date, time_unit="month"):
    """쇼핑인사이트 — 카테고리 내 키워드 클릭추이."""
    body = {"startDate": start_date, "endDate": end_date, "timeUnit": time_unit,
            "category": category,
            "keyword": [{"name": k, "param": [k]} for k in keywords[:5]]}
    h = _hub_headers(True)
    if h:
        try:
            return _call(HUB_BASE + HUB_SHOP_KEYWORDS, h, body)
        except urllib.error.HTTPError as e:
            if e.code != 401:
                raise NaverAPIError(f"API HUB {e.code}: {e.read().decode()[:160]}")
    h = _legacy_headers(True)
    if not h:
        raise NaverAPIError("쇼핑인사이트 호출 불가 — 크리덴셜 확인")
    return _call(f"{LEGACY_BASE}/datalab/shopping/category/keywords", h, body)


def which_backend():
    """현재 어떤 백엔드가 살아있는지 진단."""
    out = {}
    h = _hub_headers()
    if h:
        for k in ("blog", "webkr", "image"):
            try:
                _call(f"{HUB_BASE}/search/v1/{k}?query=test&display=1", h, timeout=8)
                out[f"hub:{k}"] = "ok"
            except urllib.error.HTTPError as e:
                out[f"hub:{k}"] = f"{e.code}"
    h = _legacy_headers()
    if h:
        try:
            _call(f"{LEGACY_BASE}/search/blog.json?query=test&display=1", h, timeout=8)
            out["legacy:blog"] = "ok (2027-06-30 만료)"
        except urllib.error.HTTPError as e:
            out["legacy:blog"] = f"{e.code}"
    return out


if __name__ == "__main__":
    print("■ 네이버 API 백엔드 진단")
    for k, v in which_backend().items():
        print(f"  {'✅' if v.startswith('ok') else '❌'} {k:<16} {v}")
    print(f"\n  ⛔ 영구 종료(대체 없음): {', '.join(sorted(DEAD_KINDS))} — 공지 32530")
    print("     국내 시세는 scripts/kr_price_check.py (다나와)")
