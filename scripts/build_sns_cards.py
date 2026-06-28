#!/usr/bin/env python3
"""
build_sns_cards.py — 인스타 카드뉴스(1080×1080) 4장 + 캡션 생성기.

레이아웃·디자인 토큰(캐나다 핀치마트 공지 스타일: 코랄레드 #e0483f + 크림핑크 #fff7f4,
잘난체 헤드라인 + 나눔스퀘어라운드 본문, 둥근/점선 카드, 네이버 초록창 CTA, 푸터 로고)을
이 스크립트가 결정론적으로 소유한다. 시니어 카피(후킹·특징·추천·CTA·캡션)는 spec JSON 으로 받는다.

사용:
  python3 scripts/build_sns_cards.py <spec.json> [--no-render]

spec.json 스키마:
{
  "slug": "downy_fusions_twilight_jasmine",
  "out_dir": "output/sns/<slug>",            # 생략 시 자동
  "product_image": "URL 또는 로컬경로",        # 커버용 클린 제품컷 권장
  "cover": {
    "hook": "한 스쿱이면,<br>빨래가 온종일 좋은 향 🌙",   # 베네핏 후킹(제품명 X)
    "sub": "두 가지 향을 한 알에 담은 향기부스터",
    "title": "다우니 언스토퍼블 퓨전 2in1",
    "scent": "🌙 트와일라잇 + 자스민",
    "sizes": "📦 303g · 598g"                  # 옵션 여러 개면 다 표기
  },
  "features": [ {"icon":"🌸","title":"두 가지 향을 한 알에","body":"..."}, ... 2~3개 ],
  "recommendations": ["...","...","..."],       # 2~3개
  "cta": { "hook":"우리집 빨래에<br>두 가지 향을 더하다", "search":"캐나다 핀치마트" },
  "caption": "전체 캡션 텍스트(해시태그 포함)"      # 선택 — caption.txt 로 저장
}

규칙(시니어 SNS): 후킹 커버 + 넘김 유도, 특징·추천 개수 균형, 쉬운 한글(영어 음역 X),
원산지 ≠ 캐나다면 '캐나다 직수입' 배지 금지, 푸터는 로고만, CTA=네이버 초록창+프로필 링크.
"""
import json, os, sys, shutil, subprocess, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_SRC = os.path.join(ROOT, "guide", "디자인 가이드", "assets", "logo-trim.png")

FONTS = """
@font-face{font-family:'YgJalnan';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_four@1.2/JalnanOTF00.woff') format('woff');font-weight:normal;}
@font-face{font-family:'NanumSquareRound';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff') format('woff');font-weight:normal;}
@font-face{font-family:'NanumSquareRound';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRoundB.woff') format('woff');font-weight:700;}
@font-face{font-family:'NanumSquareRound';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRoundEB.woff') format('woff');font-weight:800;}
*{box-sizing:border-box;margin:0;padding:0;}
body{width:1080px;height:1080px;background:#fff7f4;font-family:'NanumSquareRound',sans-serif;overflow:hidden;}
.wrap{width:1080px;height:1080px;padding:54px;}
.card{width:100%;height:100%;background:#fff;border-radius:44px;box-shadow:0 10px 34px rgba(209,47,42,.10);display:flex;flex-direction:column;}
.tag{display:inline-flex;align-items:center;gap:14px;background:#fde8e3;color:#c9352f;font-size:38px;font-weight:800;padding:16px 40px;border-radius:999px;}
"""

def doc(body):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{FONTS}</style></head><body>{body}</body></html>"

FOOTER = ('<div style="flex:1;"></div>'
          '<div style="display:flex;align-items:center;justify-content:center;border-top:2px dashed #f1c6bd;padding-top:38px;">'
          '<img src="logo.png" style="height:74px;width:auto;"></div>')

def card_cover(c):
    pills = (f'<span style="background:#fff1ec;color:#3a3a3a;font-size:27px;font-weight:800;padding:11px 24px;border-radius:999px;">{c["scent"]}</span>'
             + (f'<span style="background:#fde8e3;color:#c9352f;font-size:27px;font-weight:800;padding:11px 24px;border-radius:999px;">{c["sizes"]}</span>' if c.get("sizes") else ""))
    return doc(
      '<div class="wrap"><div class="card" style="padding:50px 56px;align-items:center;">'
      '<img src="logo.png" style="width:210px;height:auto;margin-bottom:14px;">'
      f'<h1 style="font-family:\'YgJalnan\',sans-serif;font-size:60px;color:#e0483f;text-align:center;line-height:1.22;margin-bottom:6px;">{c["hook"]}</h1>'
      f'<p style="font-size:29px;font-weight:800;color:#888;margin-bottom:10px;">{c.get("sub","")}</p>'
      '<img src="product.jpg" style="height:418px;width:auto;object-fit:contain;">'
      f'<p style="font-family:\'YgJalnan\',sans-serif;font-size:38px;color:#3a3a3a;margin:18px 0 14px;text-align:center;">{c["title"]}</p>'
      f'<div style="display:flex;gap:12px;margin-bottom:18px;">{pills}</div>'
      '<div style="flex:1;"></div>'
      '<div style="font-size:31px;font-weight:800;color:#e0483f;">오른쪽으로 넘겨보세요 👉</div>'
      '</div></div>')

def card_features(feats):
    boxes = ""
    for i, f in enumerate(feats):
        mb = "0" if i == len(feats) - 1 else "22px"
        boxes += (f'<div style="background:#fffaf3;border:2.5px dashed #f1c6bd;border-radius:26px;padding:30px 36px;margin-bottom:{mb};">'
                  f'<div style="display:flex;align-items:center;gap:20px;margin-bottom:12px;">'
                  f'<span style="font-size:54px;">{f["icon"]}</span>'
                  f'<span style="font-family:\'YgJalnan\',sans-serif;font-size:42px;color:#e0483f;">{f["title"]}</span></div>'
                  f'<p style="font-size:33px;font-weight:700;color:#444;line-height:1.45;">{f["body"]}</p></div>')
    return doc(
      '<div class="wrap"><div class="card" style="padding:52px 56px;justify-content:center;">'
      '<div style="text-align:center;margin-bottom:40px;"><div class="tag">✨ 제품 특징</div>'
      '<h1 style="font-family:\'YgJalnan\',sans-serif;font-size:48px;color:#3a3a3a;margin-top:24px;">이래서 특별해요</h1></div>'
      f'{boxes}</div></div>')

def card_recs(recs):
    rows = ""
    for i, r in enumerate(recs):
        rows += (f'<div style="display:flex;align-items:center;gap:28px;background:#fff1ec;border-radius:26px;padding:38px 40px;margin-bottom:26px;">'
                 f'<div style="flex:none;width:78px;height:78px;border-radius:999px;background:#e0483f;color:#fff;font-family:\'YgJalnan\',sans-serif;font-size:42px;display:flex;align-items:center;justify-content:center;">{i+1}</div>'
                 f'<p style="font-size:38px;font-weight:800;color:#3a3a3a;line-height:1.4;">{r}</p></div>')
    return doc(
      '<div class="wrap"><div class="card" style="padding:60px;">'
      '<div style="text-align:center;margin-bottom:44px;"><div class="tag">💝 이런 분들께 추천드려요</div></div>'
      f'{rows}{FOOTER}</div></div>')

def card_cta(c, cover):
    search = c["search"]
    box = (
      '<div style="display:flex;width:100%;height:128px;border:5px solid #03C75A;border-radius:12px;overflow:hidden;background:#fff;">'
      '<div style="flex:1;display:flex;align-items:center;padding:0 40px;gap:20px;">'
      f'<span style="font-size:52px;font-weight:800;color:#222;letter-spacing:-.01em;">{search}</span>'
      '<div style="flex:1;"></div>'
      '<div style="width:0;height:0;border-left:15px solid transparent;border-right:15px solid transparent;border-top:20px solid #03C75A;"></div></div>'
      '<div style="width:140px;background:#03C75A;display:flex;align-items:center;justify-content:center;">'
      '<svg width="74" height="74" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="7"></circle><line x1="15.8" y1="15.8" x2="21" y2="21"></line></svg></div></div>')
    return doc(
      '<div class="wrap"><div class="card" style="padding:54px 58px;align-items:center;">'
      '<div style="display:inline-block;background:#fde8e3;color:#c9352f;font-size:30px;font-weight:800;padding:13px 34px;border-radius:999px;margin:18px 0 28px;">🛒 지금 만나보세요</div>'
      f'<h1 style="font-family:\'YgJalnan\',sans-serif;font-size:62px;color:#e0483f;text-align:center;line-height:1.25;margin-bottom:18px;">{c["hook"]}</h1>'
      f'<p style="font-size:33px;font-weight:800;color:#555;text-align:center;line-height:1.5;">{cover["title"]}<br><span style="color:#888;font-weight:700;font-size:29px;">{cover["scent"].lstrip("🌙 ").strip()} · {cover.get("sizes","").lstrip("📦 ").strip()}</span></p>'
      '<div style="flex:1;"></div>'
      '<p style="font-size:36px;font-weight:800;color:#3a3a3a;margin-bottom:24px;">🛒 지금 구매하기 — 네이버에서 검색!</p>'
      f'{box}'
      '<p style="font-size:28px;font-weight:700;color:#999;margin-top:22px;">또는 프로필 링크에서 바로 구매하실 수 있어요</p>'
      f'{FOOTER.replace("flex:1;","flex:1;",1)}</div></div>')

def fetch_image(src, dst):
    if src.startswith("http"):
        urllib.request.urlretrieve(src, dst)
    else:
        shutil.copy(src if os.path.isabs(src) else os.path.join(ROOT, src), dst)

def find_chrome():
    cands = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             shutil.which("google-chrome"), shutil.which("chromium")]
    return next((c for c in cands if c and os.path.exists(c)), None)

def render(html_path, png_path, chrome):
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1080,1080",
                    "--virtual-time-budget=3000", f"--screenshot={png_path}", html_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_render = "--no-render" in sys.argv
    if not args:
        sys.exit("usage: build_sns_cards.py <spec.json> [--no-render]")
    spec = json.load(open(args[0], encoding="utf-8"))
    slug = spec["slug"]
    out = spec.get("out_dir") or os.path.join(ROOT, "output", "sns", slug)
    os.makedirs(out, exist_ok=True)
    shutil.copy(LOGO_SRC, os.path.join(out, "logo.png"))
    fetch_image(spec["product_image"], os.path.join(out, "product.jpg"))

    cards = {
        "card1.html": card_cover(spec["cover"]),
        "card2.html": card_features(spec["features"]),
        "card3.html": card_recs(spec["recommendations"]),
        "card4.html": card_cta(spec["cta"], spec["cover"]),
    }
    for name, html in cards.items():
        open(os.path.join(out, name), "w", encoding="utf-8").write(html)
    if spec.get("caption"):
        open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(spec["caption"])

    pngs = []
    if not no_render:
        chrome = find_chrome()
        if not chrome:
            sys.exit("[!] Chrome 미발견 — --no-render 로 HTML 만 생성하거나 Chrome 설치 필요")
        for n in (1, 2, 3, 4):
            h = os.path.join(out, f"card{n}.html"); p = os.path.join(out, f"card{n}.png")
            render(h, p, chrome)
            pngs.append(p)

    print(f"✅ SNS 카드 생성: {out}")
    print(f"   HTML 4장" + ("" if no_render else " + PNG 4장(1080×1080)"))
    if spec.get("caption"):
        print("   caption.txt 저장")
    for p in pngs:
        ok = os.path.exists(p)
        print(f"   {'✓' if ok else '✗'} {os.path.basename(p)}")

if __name__ == "__main__":
    main()
