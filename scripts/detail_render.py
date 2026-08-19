#!/usr/bin/env python3
"""§17 표준 스타일드 데코 상세 렌더러.

`output/new-item/post_honey_bunches_of_oats_almonds_1_4kg/` 레퍼런스 프레임을 코드로 고정한 것.
그동안 세션 scratchpad 에 두고 썼는데 임시폴더가 정리되면 매번 사라져서 리포에 올렸다.

사용:
    from scripts.detail_render import detail, R, RD, band, figure, pill
    html = detail(dict(eyebrow=..., h1=..., h2=..., intro=[...], points=[(이모지,키워드,설명)...],
                       img=..., alt=..., cap=..., [img2/alt2/cap2],
                       spec=[(이모지,라벨,값)...], good=[...], who=[...],
                       avoid=[(조건, 이유)...]))

규칙:
  · 전부 inline style (§17 — <style> 블록·class·id 금지, flex 미검증)
  · 국기 이모지 금지(§17-6). 단일 4바이트 이모지는 허용.
  · 불어 금지(§ no-french) — 카피·스펙·캡션에 영어 표기만.
  · 스펙 구분자는 콜론(`라벨 : 값`).
"""

R  = "#e0483f"   # 브랜드 레드
RD = "#c9352f"   # 진한 레드


def band(title, grey=False):
    """섹션 헤더 말풍선 + 삼각 꼬리."""
    c  = "#8d8d8d" if grey else R
    sh = "rgba(0,0,0,.12)" if grey else "rgba(224,72,63,.18)"
    return (f'<p style="margin:0 0 12px"><span style="display:inline-block;background:{c};color:#fff;'
            f'border-radius:16px;padding:12px 34px;font-size:26px;font-weight:700;'
            f'box-shadow:0 4px 10px {sh}">{title}</span></p>'
            f'<div style="width:0;height:0;border-left:11px solid transparent;'
            f'border-right:11px solid transparent;border-top:13px solid {c};margin:0 auto 22px"></div>')


def figure(src, alt, cap, gap=34):
    """이미지 + 캡션. 캡션은 필수 — 이미지 연속 나열 금지(§17-1)."""
    return ('<div style="margin:0 0 10px">'
            f'<img src="{src}" alt="{alt}" style="max-width:100%;border-radius:16px;display:block;'
            'box-shadow:0 8px 22px rgba(0,0,0,.08)"></div>\n'
            f'<p style="margin:0 0 {gap}px;font-size:20px;color:#999">▲ {cap}</p>')


def pill(text, tone="peach"):
    bg, fg = ("#fde8e3", RD) if tone == "peach" else ("#ffe9b3", "#9a6a00")
    return (f'<span style="display:inline-block;background:{bg};color:{fg};border-radius:999px;'
            f'padding:4px 14px;font-size:19px;font-weight:700;vertical-align:middle">{text}</span>')


SPEC_BAND = band("제품 정보")   # 섹션 삽입용 앵커


def detail(d):
    P = []
    P.append('<div style="background:#fff7f4;max-width:860px;margin:0 auto;padding:4%;'
             'border-radius:28px;box-shadow:0 1px 3px rgba(0,0,0,.08)">')
    P.append('<div style="background:#ffffff;border-radius:24px;padding:7% 5% 6%;text-align:center;'
             'font-size:26px;line-height:1.65;color:#3a3a3a;word-break:keep-all;'
             'box-shadow:0 6px 20px rgba(209,47,42,.06)">')
    P.append(f'<p style="margin:0 0 20px;line-height:1.5"><span style="background:#fff1ec;color:{RD};'
             f'border:1px solid #f3d3cd;border-radius:999px;padding:9px 20px;font-size:21px;'
             f'font-weight:700;display:inline-block;margin:0 4px 8px">{d["eyebrow"]}</span></p>')
    P.append(f'<h1 style="font-size:40px;font-weight:800;letter-spacing:-1px;margin:0 0 14px;'
             f'color:#222">{d["h1"]}</h1>')
    P.append(f'<div style="width:60px;height:4px;background:{R};margin:0 auto 16px;'
             f'border-radius:2px"></div>')
    P.append(f'<h2 style="font-size:20px;font-weight:600;color:#b98c86;margin:0 0 30px;'
             f'letter-spacing:.3px">{d["h2"]}</h2>')

    P.append('<div style="background:#fff7f4;border:1px solid #f3d3cd;border-radius:18px;'
             'padding:26px 22px;margin:0 0 34px;text-align:left">')
    for i, t in enumerate(d["intro"]):
        m = "0" if i == len(d["intro"]) - 1 else "0 0 12px"
        P.append(f'<p style="margin:{m};font-size:23px">{t}</p>')
    P.append('</div>')

    P.append(band("핵심 포인트"))
    P.append('<div style="background:#fff7f4;border-radius:18px;padding:14px 26px;margin:0 0 34px;'
             'text-align:left;box-shadow:0 3px 12px rgba(224,72,63,.05)">')
    for i, (e, kw, ds) in enumerate(d["points"]):
        br = "" if i == len(d["points"]) - 1 else ";border-bottom:1px solid #f3d3cd"
        P.append(f'<div style="padding:20px 0{br}">'
                 f'<strong style="color:{R};font-size:25px">{e} {kw}</strong><br>'
                 f'<span style="color:#555;font-size:22px">{ds}</span></div>')
    P.append('</div>')

    P.append(figure(d["img"], d["alt"], d["cap"]))
    if d.get("img2"):
        P.append(figure(d["img2"], d["alt2"], d["cap2"]))

    P.append(SPEC_BAND)
    P.append('<div style="background:#fffaf3;border:1px dashed #f1c6bd;border-radius:18px;'
             'padding:24px 26px;margin:0 0 34px;text-align:left">')
    for i, (e, lb, v) in enumerate(d["spec"]):
        m = "0" if i == len(d["spec"]) - 1 else "0 0 12px"
        P.append(f'<p style="margin:{m};font-size:23px">{e} <strong>{lb}</strong> : {v}</p>')
    P.append('</div>')

    P.append(band("이런 점이 좋아요"))
    P.append('<div style="text-align:left;margin:0 0 34px">')
    for i, t in enumerate(d["good"]):
        m = "0" if i == len(d["good"]) - 1 else "0 0 16px"
        P.append(f'<p style="margin:{m};font-size:24px">'
                 f'<span style="display:inline-block;width:31px;height:31px;line-height:31px;'
                 f'border-radius:999px;background:{R};color:#fff;font-size:16px;font-weight:700;'
                 f'text-align:center;vertical-align:middle;margin-right:9px">{i+1}</span>{t}</p>')
    P.append('</div>')

    P.append(band("이런 분들께 추천해요"))
    P.append('<div style="text-align:left;margin:0 0 34px;font-size:24px">')
    for i, t in enumerate(d["who"]):
        m = "0" if i == len(d["who"]) - 1 else "0 0 14px"
        P.append(f'<p style="margin:{m}">✓ {t}</p>')
    P.append('</div>')

    P.append(band("이런 경우엔 다른 걸 추천해요", grey=True))
    P.append('<div style="background:#f4f4f4;border-radius:18px;padding:24px 26px;margin:0 0 20px;'
             'text-align:left;font-size:23px;color:#555">')
    for i, (a, rest) in enumerate(d["avoid"]):
        m = "0" if i == len(d["avoid"]) - 1 else "0 0 14px"
        P.append(f'<p style="margin:{m}">❌ <strong>{a}</strong>, {rest}</p>')
    P.append('</div>')

    P.append('</div>\n</div>')
    return "\n".join(P) + "\n"


def selfcheck(html):
    """등록 전 자가검사 — 국기 이모지·em dash·불어 흔적."""
    flags = [c for c in html if 0x1F1E6 <= ord(c) <= 0x1F1FF]
    fr = [w for w in ("Lait", "Caféin", "Arachide", "FABRIQUÉ", "Contient", "Élevé",
                      "POIDS", "Torréfi", "Biologique", "Douce") if w in html]
    return dict(flag_emoji=flags, em_dash=html.count("—"), french=fr,
                four_byte=sorted({c for c in html if len(c.encode()) > 3}))


if __name__ == "__main__":
    print(__doc__)
