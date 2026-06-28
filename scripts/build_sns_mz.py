#!/usr/bin/env python3
"""
build_sns_mz.py — 인스타 MZ/포토덤프 라인업 카드(4:5, 1080×1350) 생성기 (croket 스타일).

판매중 리스트(guide/Product_*.csv)에서 **그룹상품ID** 로 한 라인업의 제품들을 뽑아, 실사진
풀블리드 + 마커 헤드라인(형광펜) + 말풍선 + 하단 설명 + 좌상단 로고 + (해당 시) '청소왕 브라이언
추천템' 리본으로 카드뉴스를 만든다. 사이즈 변형은 향별 1장으로 dedupe, 대표이미지는 최대 용량 컷.

캐러셀: 커버(예고없이 추가/단종 디스클레이머 포함) → 향별 카드 → 💝 향 추천 가이드 → 🛒 마무리 CTA(네이버 초록창).

🔴 content layer(COPY/PICK/cover/guide)는 **시니어 마케터가 공식 페이지 팩트체크 후** 채운다.
   향 노트·무드는 추측·팩 공통 슬로건 번역 금지, 공식(downy.com 등) 검증분만.
   [[feedback_senior_copywriting_mindset]] · [[project_sns_mz_croket_style]]

사용:  python3 scripts/build_sns_mz.py [그룹ID] [출력폴더명]
  (기본: 50533349 = 다우니 언스토퍼블 / downy_unstopables_lineup_mz)
새 라인업은 COPY·PICK·cover/guide 내용을 그 라인업에 맞게 교체.
"""
import csv,glob,re,os,sys,subprocess,urllib.request,shutil
from collections import OrderedDict
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP_ID=sys.argv[1] if len(sys.argv)>1 else "50533349"
PART=sys.argv[2] if len(sys.argv)>2 else "1"   # '1'·'2'·'all' — 인스타 10장 제한 → 6+5 분할
PARTS={
 '1':("downy_unstopables_lineup_mz_part1","1편",['트와일라잇','파라다이스','베르가못','로즈허니','오렌지블라썸','오션미스트']),
 '2':("downy_unstopables_lineup_mz_part2","2편",['선셋','에이프릴','프레쉬 향기','씨사이드','유칼립투스']),
 'all':("downy_unstopables_lineup_mz","",[]),
}
OUTNAME,PARTLABEL,FEATURED=PARTS.get(PART,PARTS['1'])
OUT=os.path.join(ROOT,"output","sns",OUTNAME); IMG=os.path.join(OUT,"imgs")
os.makedirs(IMG,exist_ok=True)
shutil.copy(os.path.join(ROOT,"guide","디자인 가이드","assets","logo-trim.png"),os.path.join(OUT,"logo.png"))
f=sorted(glob.glob(os.path.join(ROOT,'guide','Product_2026*.csv')))[-1]
rows=list(csv.reader(open(f,encoding='utf-8-sig')))
G,NAME,IMGC=0,3,63
def grams(s):
    m=re.match(r'([\d.]+)\s*(kg|g)',s)
    return float(m.group(1))*(1000 if m.group(2)=='kg' else 1) if m else 0
hits=[r for r in rows[1:] if len(r)>63 and r[G].strip()==GROUP_ID]
scents=OrderedDict()
for r in hits:
    base=re.sub(r',\s*[\d.]+\s*(kg|g)\s*,\s*1개$','',r[NAME]).replace('다우니 향기부스터','').strip()
    m=re.search(r'([\d.]+\s*(?:kg|g))',r[NAME]); size=m.group(1) if m else '?'
    scents.setdefault(base,[]).append((grams(size),size,r[IMGC]))
COPY={
 '트와일라잇':("두 향이 어우러진 ✨","은은한 플로럴 향","트와일라잇 + 자스민","자스민·바닐라·스위트워터의 포근한 플로럴","#19b6b0","#ffffff"),
 '오렌지블라썸':("진한 향 부담된다면 🙋","가볍고 산뜻한 향","라이트 오렌지블라썸","시트러스+가벼운 꽃향, 0% 헤비퍼퓸·무염료","#ff9a3c","#ffffff"),
 '로즈허니':("향수처럼 고급진 빨래 🌹","숲처럼 깊고 고급스러운","로즈허니 No.26","장미·허니넥타·오크모스가 어우러진 우디 플로럴 럭셔리 향","#cda86a","#2a2012"),
 '프레쉬 향기':("깔끔한 게 진리 ✨","밝고 활기찬 프레시","언스토퍼블 프레쉬","오래가는 깨끗하고 산뜻한 프레시 향","#17c3b2","#ffffff"),
 '파라다이스':("여름 휴양지 향 🏝️","햇살 가득 트로피컬","언스토퍼블 파라다이스","써니·트로피컬·리프레싱, 산뜻하고 화사한 향","#8cc63f","#16320a"),
 '씨사이드':("집에서 스파 온 듯 🌊","바닷가 스파 무드","씨사이드 스파 2in1","유칼립투스+프레시 플로럴, 편안한 해변 향","#2aa6b2","#ffffff"),
 '유칼립투스':("상쾌함 끝판왕 🌿","시원한 우디 향","유칼립투스 No.9","유칼립투스·그린파인·시더우드의 우디 향","#62a64f","#ffffff"),
 '베르가못':("향수 같은 빨래 찾는다면 🖤","세련된 우디 시그니처","베르가못 No.37","베르가못·오리스·베티버, 우디하고 깊은 향","#8a7ec6","#ffffff"),
 '에이프릴':("다우니 시그니처 💗","포근한 플로럴 향","다우니 에이프릴 프레쉬","오래 지속되는 부드러운 플로럴 향","#ec7fa6","#ffffff"),
 '선셋':("두 향이 어우러진 🌅","트로피컬 시트러스","퓨전 선셋 & 시트러스","달콤한 넥타와 시트러스, 산뜻한 트로피컬","#ef6f3a","#ffffff"),
 '오션미스트':("바다 향 좋아하면 🌊","가볍고 시원한 오션","다우니 오션미스트","크리스프 레인·릴리·샌달우드의 시원한 향","#3aa6e0","#ffffff"),
}
PICK={'파라다이스','베르가못','트와일라잇','선셋'}  # 더 브라이언 영상 노출 (FEATURED 는 PARTS 에서)
def keyfor(base):
    for k in COPY:
        if k in base: return k
W,H=1080,1350
STYLE=f"""<style>
@font-face{{font-family:'BMDOHYEON';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_one@1.1/BMDOHYEON.woff') format('woff');}}
@font-face{{font-family:'YgJalnan';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_four@1.2/JalnanOTF00.woff') format('woff');}}
@font-face{{font-family:'NanumSquareRound';src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRoundEB.woff') format('woff');font-weight:800;}}
*{{box-sizing:border-box;margin:0;padding:0;}} body{{width:{W}px;height:{H}px;overflow:hidden;font-family:'NanumSquareRound',sans-serif;}}
.frame{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;}}
.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.36) 0%,rgba(0,0,0,0) 25%,rgba(0,0,0,0) 40%,rgba(0,0,0,.74) 100%);}}
.logo{{position:absolute;top:32px;left:36px;background:#fff;border-radius:16px;padding:9px 18px;box-shadow:0 6px 16px rgba(0,0,0,.28);}}
.logo img{{height:50px;width:auto;display:block;}}
.pick{{position:absolute;top:120px;left:36px;background:#e0322b;color:#fff;font-weight:800;font-size:30px;padding:12px 24px;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,.4);transform:rotate(-3deg);}}
.bubble{{position:absolute;top:58px;right:52px;max-width:540px;background:#fff;border-radius:28px;padding:24px 30px;font-size:35px;font-weight:800;color:#222;box-shadow:0 8px 22px rgba(0,0,0,.30);line-height:1.35;}}
.bubble:after{{content:'';position:absolute;bottom:-17px;right:74px;border:15px solid transparent;border-top-color:#fff;border-bottom:0;}}
.head{{position:absolute;left:52px;right:52px;bottom:258px;font-family:'BMDOHYEON','YgJalnan',sans-serif;font-size:86px;color:#fff;line-height:1.24;text-shadow:0 4px 16px rgba(0,0,0,.65);}}
.hl{{padding:4px 18px;border-radius:7px;-webkit-box-decoration-break:clone;box-decoration-break:clone;text-shadow:none;}}
.cap{{position:absolute;left:48px;right:48px;bottom:52px;background:#fff;border-radius:24px;padding:28px 32px;box-shadow:0 8px 24px rgba(0,0,0,.30);}}
.cap p{{font-size:31px;font-weight:800;color:#333;line-height:1.4;}}
</style>"""
def card(bg,bubble,head,cap,hlbg,pick=False,note=None):
    ribbon="<div class='pick'>🧹 청소왕 브라이언 추천템</div>" if pick else ""
    notehtml=(f"<p style='font-size:23px;font-weight:700;color:#aaa;margin-top:10px;'>{note}</p>" if note else "")
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      f"<div class='frame'><img class='bg' src='{bg}'><div class='shade'></div>"
      f"<div class='logo'><img src='logo.png'></div>{ribbon}"
      f"<div class='bubble' style='border:5px solid {hlbg};'>{bubble}</div>"
      f"<div class='head'>{head}</div>"
      f"<div class='cap' style='border-left:16px solid {hlbg};'><p>{cap}</p>{notehtml}</div>"
      "</div></body></html>")
def cta_card(bg):
    naver=("<div style='display:flex;width:90%;height:116px;border:5px solid #03C75A;border-radius:12px;overflow:hidden;background:#fff;margin:0 auto;'>"
      "<div style='flex:1;display:flex;align-items:center;padding:0 32px;gap:16px;'><span style='font-size:46px;font-weight:800;color:#222;'>캐나다 핀치마트</span><div style='flex:1;'></div><div style='width:0;height:0;border-left:14px solid transparent;border-right:14px solid transparent;border-top:18px solid #03C75A;'></div></div>"
      "<div style='width:124px;background:#03C75A;display:flex;align-items:center;justify-content:center;'><svg width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.4' stroke-linecap='round'><circle cx='10.5' cy='10.5' r='7'></circle><line x1='15.8' y1='15.8' x2='21' y2='21'></line></svg></div></div>")
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      f"<div class='frame'><img class='bg' src='{bg}'>"
      "<div class='shade' style='background:linear-gradient(180deg,rgba(0,0,0,.5),rgba(0,0,0,.55) 45%,rgba(0,0,0,.72));'></div>"
      "<div class='logo'><img src='logo.png'></div>"
      "<div style='position:absolute;left:54px;right:54px;top:47%;transform:translateY(-50%);text-align:center;'>"
      "<div style='font-family:BMDOHYEON,YgJalnan,sans-serif;font-size:76px;color:#fff;line-height:1.26;text-shadow:0 4px 16px rgba(0,0,0,.7);'>마음에 든 향,<br><span class='hl' style='background:#e0322b;color:#fff;'>지금 골라 담으세요</span> 🛒</div>"
      f"<div style='margin-top:46px;'>{naver}</div>"
      "<p style='font-size:32px;font-weight:800;color:#fff;margin-top:28px;text-shadow:0 2px 10px rgba(0,0,0,.7);'>프로필 링크 또는 네이버 검색 → 11가지 향 전부 👆</p>"
      "</div></div></body></html>")
def guide_card():
    rows=[("🌸","은은한 플로럴 향","트와일라잇+자스민","#1aa9a3"),
          ("🖤","향수 같은 고급 우디","N.26 · N.37","#8a7ec6"),
          ("🏝️","상큼한 트로피컬","파라다이스 · 선셋","#6faa1f"),
          ("🌊","시원한 바다·청량감","오션미스트 · N.9","#2f8fd6"),
          ("💗","익숙한 데일리 향","에이프릴프레쉬 · 프레쉬","#e06a96"),
          ("🙋","진한 향이 부담되면","라이트 오렌지블라썸","#f08a22")]
    rh="".join(
      "<div style='display:flex;align-items:center;gap:16px;background:#fff7f4;border-radius:22px;padding:22px 26px;margin-bottom:17px;'>"
      f"<span style='font-size:44px;'>{e}</span>"
      f"<span style='font-size:33px;font-weight:800;color:#3a3a3a;flex:1;'>{p}</span>"
      f"<span style='font-size:26px;font-weight:800;color:#cfcfcf;'>→</span>"
      f"<span style='font-size:31px;font-weight:800;color:{c};text-align:right;'>{s}</span></div>"
      for e,p,s,c in rows)
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"+STYLE+"</head><body>"
      "<div style='width:1080px;height:1350px;background:#fff7f4;padding:54px;'>"
      "<div style='width:100%;height:100%;background:#fff;border-radius:44px;box-shadow:0 10px 34px rgba(209,47,42,.10);padding:54px 48px;display:flex;flex-direction:column;'>"
      "<div style='text-align:center;margin-bottom:38px;'><span style='display:inline-flex;align-items:center;gap:12px;background:#fde8e3;color:#c9352f;font-size:38px;font-weight:800;padding:16px 38px;border-radius:999px;'>💝 이런 분께 이 향 추천!</span></div>"
      "<div style='flex:1;'></div>"
      f"{rh}<div style='flex:1;'></div>"
      "<p style='text-align:center;font-size:28px;font-weight:800;color:#aaa;'>고민되면 마지막 장에서 바로 구매 👉</p>"
      "</div></div></body></html>")
def dl(url,path):
    try: urllib.request.urlretrieve(url,path); return True
    except Exception as e: print("DL FAIL",e); return False
manifest=[]
# 커버 배경 = 이 편 첫 노출 향 이미지(없으면 N.26)
def first_feat_img():
    for base,lst in scents.items():
        k=keyfor(base)
        if k and (not FEATURED or k in FEATURED): return max(lst)[2]
    return max(scents['언스토퍼블 로즈허니 no.26'])[2]
dl(first_feat_img(),os.path.join(IMG,"cover.jpg"))
cover_bubble=(f"{PARTLABEL} · 향 골라보세요 🙆" if PARTLABEL else "향 많아서 못 고르겠다면 🙆")
cover_head="다우니 향기부스터<br><span class='hl' style='background:#3aa6e0;color:#fff;'>인기 향 11가지 총정리</span>"
open(os.path.join(OUT,"card00.html"),"w",encoding="utf-8").write(
  card("imgs/cover.jpg",cover_bubble,cover_head,"향별로 쭉 보여드려요 👇 (1·2편에서 11가지 전부)","#3aa6e0",
       note="※ 향 종류는 예고 없이 추가·단종될 수 있어요"))
manifest.append("card00.html")
idx=0
for base,lst in scents.items():
    k=keyfor(base)
    if not k: continue
    if FEATURED and k not in FEATURED: continue
    idx+=1
    bubble,h1,hl,capb,hlbg,hltc=COPY[k]
    rep=max(lst); sizes="·".join(dict.fromkeys(s for _,s,_ in sorted(lst,reverse=True)))
    img_path=f"imgs/s{idx}.jpg"; dl(rep[2],os.path.join(OUT,img_path))
    head=f"{h1}<br><span class='hl' style='background:{hlbg};color:{hltc};'>{hl}</span>"
    name=f"card{idx:02d}.html"
    open(os.path.join(OUT,name),"w",encoding="utf-8").write(card(img_path,bubble,head,f"{capb} · {sizes}",hlbg,pick=(k in PICK)))
    manifest.append(name)
# 향 고르기 가이드 + 라인업 마무리 CTA 카드
open(os.path.join(OUT,"card98.html"),"w",encoding="utf-8").write(guide_card())
manifest.append("card98.html")
open(os.path.join(OUT,"card99.html"),"w",encoding="utf-8").write(cta_card("imgs/cover.jpg"))
manifest.append("card99.html")
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for n in manifest:
    png=os.path.join(OUT,n.replace('.html','.png'))
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=1",f"--window-size={W},{H}","--virtual-time-budget=3500",f"--screenshot={png}",os.path.join(OUT,n)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print("DONE",len(manifest),"cards | PICK:",PICK)
