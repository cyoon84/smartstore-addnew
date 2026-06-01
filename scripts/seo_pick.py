#!/usr/bin/env python3
"""guide/ 의 최신 Product_*.csv 에서 SEO 감사용 상품을 랜덤 샘플로 뽑는다.

- 판매중·전시중만 대상
- 이미 처리한 상품(output/seo_refresh_log.csv 의 product_id)은 제외 (전부 소진되면 자동 리셋)
- 결과를 JSON 으로 stdout 출력 → 오케스트레이터(/seo-refresh)가 seo-auditor 로 감사

사용:
  python3 scripts/seo_pick.py --sample 12          # 감사용 후보 12개 랜덤
  python3 scripts/seo_pick.py --sample 12 --seed 20260531   # 재현용 시드(날짜 등)
"""
import argparse, csv, glob, json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, "guide")
SEO_DIR = os.path.join(ROOT, "output", "seo_refresh")   # SEO 전용 출력 폴더
LOG = os.path.join(SEO_DIR, "seo_refresh_log.csv")
STORE_ID = "finchmart_ca"


def latest_csv():
    files = sorted(glob.glob(os.path.join(GUIDE, "Product_*.csv")))
    if not files:
        sys.exit("guide/Product_*.csv 없음")
    return files[-1]  # 파일명에 날짜시간 → 사전순 = 최신순


def done_ids():
    if not os.path.exists(LOG):
        return set()
    with open(LOG, encoding="utf-8") as f:
        return {r["product_id"] for r in csv.DictReader(f) if r.get("product_id")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--seed", default=None)
    a = ap.parse_args()
    if a.seed:
        random.seed(a.seed)

    os.makedirs(SEO_DIR, exist_ok=True)   # 출력·로그 폴더 보장
    path = latest_csv()
    with open(path, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f)
                if r.get("판매상태") == "판매중" and r.get("전시상태") == "전시중"]

    done = done_ids()
    pool = [r for r in rows if r["상품번호(스마트스토어)"] not in done]
    reset = False
    if len(pool) < a.sample:          # 다 돌았으면 리셋(전체에서 다시)
        pool, reset = rows, True

    picks = random.sample(pool, min(a.sample, len(pool)))
    out = []
    for r in picks:
        pid = r["상품번호(스마트스토어)"]
        cat = " > ".join(x for x in (r.get("대분류"), r.get("중분류"),
                                     r.get("소분류"), r.get("세분류")) if x)
        group_no = (r.get("그룹상품번호") or "").strip()
        out.append({
            "product_id": pid,
            "title_ko": r.get("상품명", ""),
            "category": cat,
            "brand": r.get("브랜드명") or r.get("제조사명") or "",
            "model": r.get("모델명", ""),
            "attributes": r.get("상품속성", ""),
            "image_url": r.get("대표이미지 URL", ""),
            "live_url": f"https://smartstore.naver.com/{STORE_ID}/products/{pid}",
            # 그룹상품: 상품명이 '<그룹상품명>, <옵션1>, <옵션2>' 형식 + 그룹명은 생성 후 잠김.
            # is_group=True 면 상품명을 평탄 재작성 X, 옵션 구조 보존, detail 만 개선.
            "group_product_id": group_no,
            "is_group": bool(group_no),
        })
    print(json.dumps({
        "source_csv": os.path.basename(path),
        "total_selling": len(rows),
        "already_done": len(done),
        "pool_reset": reset,
        "candidates": out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
