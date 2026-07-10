#!/usr/bin/env python3
"""
build_sns_mz_kd.py — KD 라면(치즈라면 크래프트디너 KD) MZ 라인업 카드(4:5, 1080×1350).
build_sns_mz.py 의 croket 디자인(마커 헤드라인·말풍선·좌상단 로고·네이버 초록창 CTA) 재사용,
CSV/다우니 향 대신 KD 3맛(마일드·미디엄·엑스트라스파이시) content layer 로 교체.
캐러셀: 커버 → 맛3 → 💝 맛 추천 가이드 → 🛒 CTA.  이미지=로컬 제품컷(§9 검증분).
"""
import os,subprocess,shutil
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC="/private/tmp/claude-501/-Volumes-External-claude-smartstore-addnew/7c1ab932-c071-46eb-bc29-89c2b07fb57c/scratchpad/kd"
OUT=os.path.join(ROOT,"output","sns","kd_ramen_lineup_mz"); IMG=os.path.join(OUT,"imgs")
os.makedirs(IMG,exist_ok=True)
shutil.copy(os.path.join(ROOT,"guide","디자인 가이드","assets","logo-trim.png"),os.path.join(OUT,"logo.png"))
# 이미지 복사 (실사진 제품컷 + 조리 어피탈컷)
for s,d in [("off_c2.jpg","cover.jpg"),("IMG_3246.jpg","mild.jpg"),("IMG_3245.jpg","medium.jpg"),
            ("IMG_3247.jpg","spicy.jpg"),("off_c3.jpg","cta.jpg")]:
    shutil.copy(os.path.join(SRC,s),os.path.join(IMG,d))

W,H=1080,1350
STYLE=f"""<style>
@font-face{{font-family:'BMDOHYEON';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_one@1.1/BMDOHYEON.woff') format('woff');}}
@font-face{{font-family:'YgJalnan';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_four@1.2/JalnanOTF00.woff') format('woff');}}
@font-face{{font-family:'NanumSquareRound';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRoundEB.woff') format('woff');font-weight:800;}}
*{{box-sizing:border-box;margin:0;padding:0;}} body{{width:{W}px;height:{H}px;overflow:hidden;font-family:'NanumSquareRound',sans-serif;}}
.frame{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;}}
.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.40) 0%,rgba(0,0,0,0) 25%,rgba(0,0,0,0) 40%,rgba(0,0,0,.76) 100%);}}
.logo{{position:absolute;top:32px;left:36px;background:#fff;border-radius:16px;padding:9px 18px;box-shadow:0 6px 16px rgba(0,0,0,.28);}}
.logo img{{height:50px;width:auto;display:block;}}
.pick{{position:absolute;top:120px;left:36px;background:#e0322b;color:#fff;font-weight:800;font-size:30px;padding:12px 24px;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,.4);transform:rotate(-3deg);}}
.bubble{{position:absolute;top:58px;right:52px;max-width:560px;background:#fff;border-radius:28px;padding:24px 30px;font-size:35px;font-weight:800;color:#222;box-shadow:0 8px 22px rgba(0,0,0,.30);line-height:1.35;}}
.bubble:after{{content:'';position:absolute;bottom:-17px;right:74px;border:15px solid transparent;border-top-color:#fff;border-bottom:0;}}
.head{{position:absolute;left:52px;right:52px;bottom:258px;font-family:'BMDOHYEON','YgJalnan',sans-serif;font-size:80px;color:#fff;line-height:1.24;text-shadow:0 4px 16px rgba(0,0,0,.65);}}
.hl{{padding:4px 18px;border-radius:7px;-webkit-box-decoration-break:clone;box-decoration-break:clone;text-shadow:none;}}
.cap{{position:absolute;left:48px;right:48px;bottom:52px;background:#fff;border-radius:24px;padding:28px 32px;box-shadow:0 8px 24px rgba(0,0,0,.30);}}
.cap p{{font-size:31px;font-weight:800;color:#333;line-height:1.4;}}
</style>"""

def card(bg,bubble,head,cap,hlbg,ribbon=None,note=None):
    rib=f"<div class='pick'>{ribbon}</div>" if ribbon else ""
    notehtml=(f"<p style='font-size:23px;font-weight:700;color:#aaa;margin-top:10px;'>{note}</p>" if note else "")
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      f"<div class='frame'><img class='bg' src='{bg}'><div class='shade'></div>"
      f"<div class='logo'><img src='logo.png'></div>{rib}"
      f"<div class='bubble' style='border:5px solid {hlbg};'>{bubble}</div>"
      f"<div class='head'>{head}</div>"
      f"<div class='cap' style='border-left:16px solid {hlbg};'><p>{cap}</p>{notehtml}</div>"
      "</div></body></html>")

def guide_card():
    rows=[("🧀","치즈 폭탄 원하면","마일드 (엑스트라 치즈)","#e8a200"),
          ("👍","무난하게 다 좋으면","미디엄 (치즈 라면)","#2f6fd0"),
          ("🔥","매콤+느끼함 잡고 싶으면","엑스트라 스파이시","#e0322b"),
          ("🍺","맥주 안주로","엑스트라 스파이시","#e0322b"),
          ("🏕️","자취·야식·캠핑 한 끼","3가지 다 좋아요","#59a63a")]
    rh="".join(
      "<div style='display:flex;align-items:center;gap:16px;background:#fff7f4;border-radius:22px;padding:22px 26px;margin-bottom:17px;'>"
      f"<span style='font-size:44px;'>{e}</span>"
      f"<span style='font-size:32px;font-weight:800;color:#3a3a3a;flex:1;'>{p}</span>"
      f"<span style='font-size:26px;font-weight:800;color:#cfcfcf;'>→</span>"
      f"<span style='font-size:30px;font-weight:800;color:{c};text-align:right;'>{s}</span></div>"
      for e,p,s,c in rows)
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      "<div style='width:1080px;height:1350px;background:#fff7f4;padding:54px;'>"
      "<div style='width:100%;height:100%;background:#fff;border-radius:44px;box-shadow:0 10px 34px rgba(209,47,42,.10);padding:54px 48px;display:flex;flex-direction:column;'>"
      "<div style='text-align:center;margin-bottom:34px;'><span style='display:inline-flex;align-items:center;gap:12px;background:#fde8e3;color:#c9352f;font-size:38px;font-weight:800;padding:16px 38px;border-radius:999px;'>💝 이런 분께 이 맛 추천!</span></div>"
      "<div style='flex:1;'></div>"
      f"{rh}<div style='flex:1;'></div>"
      "<p style='text-align:center;font-size:28px;font-weight:800;color:#aaa;'>고민되면 마지막 장에서 바로 구매 👉</p>"
      "</div></div></body></html>")

def cta_card(bg):
    naver=("<div style='display:flex;width:90%;height:116px;border:5px solid #03C75A;border-radius:12px;overflow:hidden;background:#fff;margin:0 auto;'>"
      "<div style='flex:1;display:flex;align-items:center;padding:0 32px;gap:16px;'><span style='font-size:46px;font-weight:800;color:#222;'>캐나다 핀치마트</span><div style='flex:1;'></div><div style='width:0;height:0;border-left:14px solid transparent;border-right:14px solid transparent;border-top:18px solid #03C75A;'></div></div>"
      "<div style='width:124px;background:#03C75A;display:flex;align-items:center;justify-content:center;'><svg width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.4' stroke-linecap='round'><circle cx='10.5' cy='10.5' r='7'></circle><line x1='15.8' y1='15.8' x2='21' y2='21'></line></svg></div></div>")
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      f"<div class='frame'><img class='bg' src='{bg}'>"
      "<div class='shade' style='background:linear-gradient(180deg,rgba(0,0,0,.5),rgba(0,0,0,.55) 45%,rgba(0,0,0,.72));'></div>"
      "<div class='logo'><img src='logo.png'></div>"
      "<div style='position:absolute;left:54px;right:54px;top:47%;transform:translateY(-50%);text-align:center;'>"
      "<div style='font-family:BMDOHYEON,YgJalnan,sans-serif;font-size:74px;color:#fff;line-height:1.26;text-shadow:0 4px 16px rgba(0,0,0,.7);'>먹어보고 싶다면<br><span class='hl' style='background:#e0322b;color:#fff;'>지금 골라 담으세요</span> 🛒</div>"
      f"<div style='margin-top:46px;'>{naver}</div>"
      "<p style='font-size:32px;font-weight:800;color:#fff;margin-top:28px;text-shadow:0 2px 10px rgba(0,0,0,.7);'>프로필 링크 또는 네이버 검색 → KD 라면 3맛 👆</p>"
      "</div></div></body></html>")

manifest=[]
# 커버
open(os.path.join(OUT,"card00.html"),"w",encoding="utf-8").write(
  card("imgs/cover.jpg","캐나다에서 이제 막 나온 🍜",
       "치즈에 라면을 말았다?!<br><span class='hl' style='background:#e0322b;color:#fff;'>KD 치즈라면</span>",
       "크래프트 디너 만든 크래프트 하인즈의 신상 · 매운맛 3단계","#e0322b",
       note="※ 캐나다 한정 · 국내 미출시"))
manifest.append("card00.html")
# 맛 3종
FLAV=[
 ("mild.jpg","매운 거 못 먹어도 OK 🙆","치즈만 두 배로 진하게","엑스트라 치즈 · 마일드","가장 순한맛 · 치즈 폭탄 · 97g","#e8a200","#ffffff",None),
 ("medium.jpg","밸런스가 제일 좋아요 👍","고소함 + 적당한 매콤","치즈 라면 · 미디엄","치즈와 매콤함 밸런스 · 중간맛 · 95g","#2f6fd0","#ffffff",None),
 ("spicy.jpg","느끼한 거 싫어하면 🔥","매콤함이 느끼함을 확 잡아줘요","엑스트라 스파이시","제일 중독성 · 한국인 입맛에 딱 · 매운맛 · 97g","#e0322b","#ffffff","🌶️ 에디터 추천"),
]
for i,(img,bubble,h1,hl,cap,hlbg,hltc,ribbon) in enumerate(FLAV,1):
    head=f"{h1}<br><span class='hl' style='background:{hlbg};color:{hltc};'>{hl}</span>"
    n=f"card{i:02d}.html"
    open(os.path.join(OUT,n),"w",encoding="utf-8").write(card(f"imgs/{img}",bubble,head,cap,hlbg,ribbon=ribbon))
    manifest.append(n)
# 가이드 + CTA
open(os.path.join(OUT,"card98.html"),"w",encoding="utf-8").write(guide_card()); manifest.append("card98.html")
open(os.path.join(OUT,"card99.html"),"w",encoding="utf-8").write(cta_card("imgs/cta.jpg")); manifest.append("card99.html")

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for n in manifest:
    png=os.path.join(OUT,n.replace('.html','.png'))
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=1",
      f"--window-size={W},{H}","--virtual-time-budget=4000",f"--screenshot={png}",os.path.join(OUT,n)],
      stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print("DONE",len(manifest),"cards →",OUT)
