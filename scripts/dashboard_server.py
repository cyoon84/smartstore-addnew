#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
finchmart_ca 등록상품 뷰어 — 무의존성 Python 서버 (빌트인 http.server 만 사용).

문서(docs) 스타일: 좌측 접이식 사이드바(제품목록 → 클릭 시 폴더 파일 펼침) → 파일 클릭 시 우측 본문.
  .md = 경량 마크다운 렌더 / .html = iframe / .json = 정렬출력 / 이미지 = <img> / .xlsx = 다운로드

실행:  python3 scripts/dashboard_server.py [port]    (기본 4178)
종료:  Ctrl+C
"""
import os, re, json, sys, mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_ITEM = os.path.join(ROOT, "output", "new-item")
SKIP = {"_batch", "_misc", "_dashboard", "_seo_refresh"}
IMG_RE = re.compile(r"\.(jpg|jpeg|png|webp|gif)$", re.I)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4178


def deep_find(obj, keys):
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] not in (None, "", [], {}):
                return obj[k]
        for v in obj.values():
            r = deep_find(v, keys)
            if r not in (None, "", [], {}):
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = deep_find(v, keys)
            if r not in (None, "", [], {}):
                return r
    return None


def to_int(v):
    if isinstance(v, (int, float)):
        return int(v)
    if isinstance(v, str):
        m = re.search(r"\d[\d,]*", v)
        if m:
            return int(m.group(0).replace(",", ""))
    return None


def list_products():
    out = []
    for slug in os.listdir(NEW_ITEM):
        if slug in SKIP:
            continue
        d = os.path.join(NEW_ITEM, slug)
        if not os.path.isdir(d):
            continue
        files = os.listdir(d)
        pj = next((f for f in files if f.endswith("_product_info.json")), None)
        title, price, mode, reg = slug, None, "single", ""
        if pj:
            try:
                data = json.load(open(os.path.join(d, pj), encoding="utf-8"))
                title = deep_find(data, ["title_ko", "product_name_ko", "title"]) or slug
                price = to_int(deep_find(data, ["sell_price_krw", "sell_krw", "selling_price_krw", "sale_price_krw"]))
                mode = deep_find(data, ["mode"]) or "single"
                reg = deep_find(data, ["registered_at"]) or ""
            except Exception:
                pass
        out.append({"slug": slug, "title": title, "price": price, "mode": mode,
                    "registered": reg, "nfiles": len(files)})
    out.sort(key=lambda r: (r["registered"] or "", r["slug"]), reverse=True)
    return out


def list_files(slug):
    d = os.path.join(NEW_ITEM, slug)
    order = {"md": 0, "html": 1, "json": 2, "xlsx": 3, "image": 4, "other": 5}

    def typ(f):
        l = f.lower()
        if l.endswith(".md"): return "md"
        if l.endswith(".html"): return "html"
        if l.endswith(".json"): return "json"
        if l.endswith(".xlsx"): return "xlsx"
        if IMG_RE.search(l): return "image"
        return "other"
    rows = [{"name": f, "type": typ(f), "size": os.path.getsize(os.path.join(d, f))}
            for f in os.listdir(d) if not f.startswith(".")]
    rows.sort(key=lambda r: (order[r["type"]], r["name"]))
    return rows


def safe_path(slug, name):
    p = os.path.normpath(os.path.join(NEW_ITEM, slug or "", name or ""))
    return p if p.startswith(NEW_ITEM) else None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # 조용히
        pass

    def _send(self, code, ctype, body, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path == "/":
                return self._send(200, "text/html; charset=utf-8", PAGE)
            if u.path == "/api/products":
                return self._send(200, "application/json; charset=utf-8",
                                  json.dumps(list_products(), ensure_ascii=False))
            if u.path == "/api/files":
                return self._send(200, "application/json; charset=utf-8",
                                  json.dumps(list_files(unquote(q.get("slug", [""])[0])), ensure_ascii=False))
            if u.path == "/raw":
                fp = safe_path(unquote(q.get("slug", [""])[0]), unquote(q.get("name", [""])[0]))
                if not fp or not os.path.isfile(fp):
                    return self._send(404, "text/plain; charset=utf-8", "not found")
                ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
                if fp.lower().endswith(".md"):
                    ctype = "text/plain; charset=utf-8"
                extra = {}
                if fp.lower().endswith(".xlsx"):
                    extra["Content-Disposition"] = f'attachment; filename="{os.path.basename(fp)}"'
                with open(fp, "rb") as f:
                    return self._send(200, ctype, f.read(), extra)
            return self._send(404, "text/plain; charset=utf-8", "not found")
        except Exception as e:
            return self._send(500, "text/plain; charset=utf-8", "error: " + str(e))


PAGE = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>finchmart_ca · 등록상품</title>
<style>
:root{--bg:#fff;--side:#fafbfc;--line:#ebedf0;--txt:#2d2f36;--mut:#8a909c;--acc:#4f7cff;--acc-bg:#eef3ff;--grp:#e8810c;--code:#f6f7f9;}
*{box-sizing:border-box;}
body{margin:0;height:100vh;display:flex;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;background:var(--bg);color:var(--txt);font-size:14px;}
#left{width:300px;min-width:240px;max-width:42%;background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;}
#brand{padding:16px 18px 12px;font-size:16px;font-weight:700;color:var(--acc);display:flex;align-items:center;gap:8px;}
#brand .cnt{margin-left:auto;font-size:11px;color:var(--mut);font-weight:400;}
#qbox{padding:0 14px 12px;}
#q{width:100%;background:#fff;border:1px solid var(--line);color:var(--txt);padding:8px 11px;border-radius:8px;font-size:13px;}
#list{overflow:auto;flex:1;padding:4px 0 30px;}
.sec-label{font-size:11px;letter-spacing:.04em;color:#aab0bc;text-transform:uppercase;padding:14px 18px 6px;}
.item{}
.it-head{padding:7px 16px 7px 18px;cursor:pointer;display:flex;gap:8px;align-items:center;color:#4a4f59;}
.it-head:hover{color:var(--txt);}
.it-head.active{color:var(--acc);font-weight:600;}
.it-title{flex:1;min-width:0;font-size:13px;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.it-head.active .it-title{white-space:normal;}
.caret{color:#b8bdc8;font-size:10px;transition:transform .15s;}
.item.open .caret{transform:rotate(90deg);}
.dot{font-size:10px;}
.dot.group{color:var(--grp);}
.files{display:none;padding:2px 0 8px;}
.item.open .files{display:block;}
.file{padding:5px 16px 5px 38px;font-size:12.5px;cursor:pointer;color:#6b7280;display:flex;gap:7px;align-items:center;}
.file:hover{background:#f0f2f5;color:var(--txt);}
.file.sel{color:var(--acc);background:var(--acc-bg);box-shadow:inset 2px 0 0 var(--acc);}
.ficon{width:15px;text-align:center;}
.fsize{margin-left:auto;color:#b8bdc8;font-size:10.5px;}
.meta-line{padding:1px 16px 6px 38px;font-size:11px;color:var(--mut);display:flex;gap:8px;align-items:center;}
.price{color:#1f8a4c;font-weight:600;}
#right{flex:1;display:flex;flex-direction:column;overflow:hidden;}
#rhead{padding:11px 26px;border-bottom:1px solid var(--line);font-size:12.5px;color:var(--mut);display:flex;gap:12px;align-items:center;}
#rhead #rtitle{color:var(--txt);font-weight:600;}
#rhead a{color:var(--acc);text-decoration:none;}
#view{flex:1;overflow:auto;padding:30px 42px;max-width:920px;}
#view.pad0{padding:0;max-width:none;}
.placeholder{color:var(--mut);padding:70px 20px;text-align:center;}
.md h1{font-size:24px;margin:.2em 0 .6em;}
.md h2{font-size:19px;margin-top:1.4em;padding-bottom:5px;border-bottom:1px solid var(--line);}
.md h3{font-size:15.5px;margin-top:1.2em;}
.md table{border-collapse:collapse;margin:14px 0;font-size:13px;width:100%;}
.md th,.md td{border:1px solid var(--line);padding:7px 11px;text-align:left;vertical-align:top;}
.md th{background:#f6f8fb;font-weight:600;}
.md code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12.5px;color:#c7254e;}
.md pre{background:var(--code);border:1px solid var(--line);border-radius:8px;padding:14px;overflow:auto;}
.md pre code{background:none;padding:0;color:var(--txt);}
.md blockquote{border-left:3px solid var(--acc);margin:12px 0;padding:4px 16px;color:#6b7280;background:#f9fafb;}
.md a{color:var(--acc);}
.md ul,.md ol{padding-left:24px;}
.md li{margin:4px 0;}
.md hr{border:none;border-top:1px solid var(--line);margin:22px 0;}
.md p{line-height:1.7;}
.json{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;white-space:pre;color:#2d2f36;}
iframe{width:100%;height:100%;border:0;background:#fff;}
img.preview{max-width:100%;height:auto;border-radius:8px;border:1px solid var(--line);}
</style></head>
<body>
<div id="left">
  <div id="brand">🛒 등록상품 <span class="cnt" id="cnt"></span></div>
  <div id="qbox"><input id="q" type="search" placeholder="상품명·슬러그 검색…"></div>
  <div class="sec-label">DOCUMENTATION</div>
  <div id="list"></div>
</div>
<div id="right">
  <div id="rhead"><span id="rtitle">파일을 선택하세요</span><span id="rdl"></span></div>
  <div id="view"><div class="placeholder">← 왼쪽에서 제품을 클릭해 폴더를 펼치고, 파일을 선택하면 여기에 표시됩니다.</div></div>
</div>
<script>
let PRODUCTS=[];
const $=s=>document.querySelector(s);
const esc=s=>s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const won=n=>n?"₩"+n.toLocaleString("ko-KR"):"";
const ICON={md:"📄",html:"🌐",json:"🧩",xlsx:"📊",image:"🖼",other:"📎"};
async function load(){PRODUCTS=await(await fetch("/api/products")).json();renderList();}
function renderList(){
  const q=$("#q").value.trim().toLowerCase();
  const rows=PRODUCTS.filter(p=>!q||(p.title+" "+p.slug).toLowerCase().includes(q));
  $("#cnt").textContent=`${rows.length}/${PRODUCTS.length}`;
  const list=$("#list");list.innerHTML="";
  for(const p of rows){
    const it=document.createElement("div");it.className="item";
    const head=document.createElement("div");head.className="it-head";
    head.innerHTML=`<span class="caret">▶</span><span class="dot${p.mode==="group"?" group":""}">●</span><span class="it-title">${esc(p.title)}</span>`;
    const files=document.createElement("div");files.className="files";
    const meta=document.createElement("div");meta.className="meta-line";
    meta.innerHTML=`${p.mode==="group"?"그룹":"단일"} ${p.price?`· <span class="price">${won(p.price)}</span>`:"· 가격미상"} ${p.registered?"· "+p.registered:""}`;
    files.appendChild(meta);
    head.addEventListener("click",()=>toggle(it,files,p.slug));
    it.appendChild(head);it.appendChild(files);list.appendChild(it);
  }
}
async function toggle(it,filesEl,slug){
  const open=it.classList.contains("open");
  document.querySelectorAll(".item.open").forEach(x=>{if(x!==it)x.classList.remove("open");});
  document.querySelectorAll(".it-head.active").forEach(x=>x.classList.remove("active"));
  if(open){it.classList.remove("open");return;}
  it.classList.add("open");it.querySelector(".it-head").classList.add("active");
  if(!filesEl.dataset.loaded){
    const files=await(await fetch("/api/files?slug="+encodeURIComponent(slug))).json();
    for(const f of files){
      const fe=document.createElement("div");fe.className="file";
      fe.innerHTML=`<span class="ficon">${ICON[f.type]||"📎"}</span><span>${esc(f.name.replace(slug+"_",""))}</span><span class="fsize">${(f.size/1024).toFixed(0)}KB</span>`;
      fe.addEventListener("click",e=>{e.stopPropagation();
        filesEl.querySelectorAll(".file.sel").forEach(x=>x.classList.remove("sel"));fe.classList.add("sel");openFile(slug,f);});
      filesEl.appendChild(fe);
    }
    filesEl.dataset.loaded="1";
  }
}
async function openFile(slug,f){
  const url="/raw?slug="+encodeURIComponent(slug)+"&name="+encodeURIComponent(f.name);
  $("#rtitle").textContent=f.name;$("#rdl").innerHTML=`· <a href="${url}" target="_blank" download>다운로드</a>`;
  const view=$("#view");view.className="";view.innerHTML="로딩…";
  if(f.type==="image"){view.classList.add("pad0");view.innerHTML=`<div style="padding:26px"><img class="preview" src="${url}"></div>`;return;}
  if(f.type==="xlsx"){view.innerHTML=`<div class="placeholder">📊 엑셀은 미리보기 불가 — <a href="${url}" download style="color:var(--acc)">다운로드</a> 해서 여세요.</div>`;return;}
  if(f.type==="html"){view.classList.add("pad0");view.innerHTML=`<iframe src="${url}"></iframe>`;return;}
  const txt=await(await fetch(url)).text();
  if(f.type==="json"){let s=txt;try{s=JSON.stringify(JSON.parse(txt),null,2);}catch{}view.innerHTML=`<div class="json">${esc(s)}</div>`;return;}
  if(f.type==="md"){view.innerHTML=`<div class="md">${mdToHtml(txt)}</div>`;return;}
  view.innerHTML=`<pre>${esc(txt)}</pre>`;
}
function mdToHtml(src){
  const lines=src.replace(/\r/g,"").split("\n");let out=[],i=0;
  const inline=s=>esc(s).replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>');
  while(i<lines.length){let l=lines[i];
    if(/^\s*```/.test(l)){const buf=[];i++;while(i<lines.length&&!/^\s*```/.test(lines[i])){buf.push(lines[i]);i++;}i++;out.push("<pre><code>"+esc(buf.join("\n"))+"</code></pre>");continue;}
    if(/^#{1,6}\s/.test(l)){const m=l.match(/^(#{1,6})\s+(.*)$/);out.push(`<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`);i++;continue;}
    if(/^\s*---\s*$/.test(l)){out.push("<hr>");i++;continue;}
    if(/^\s*>\s?/.test(l)){const buf=[];while(i<lines.length&&/^\s*>\s?/.test(lines[i])){buf.push(lines[i].replace(/^\s*>\s?/,""));i++;}out.push("<blockquote>"+inline(buf.join(" "))+"</blockquote>");continue;}
    if(/^\s*\|.*\|\s*$/.test(l)&&i+1<lines.length&&/^\s*\|[\s:|-]+\|\s*$/.test(lines[i+1])){
      const row=s=>s.trim().replace(/^\||\|$/g,"").split("|").map(c=>c.trim());
      const head=row(l);i+=2;const body=[];
      while(i<lines.length&&/^\s*\|.*\|\s*$/.test(lines[i])){body.push(row(lines[i]));i++;}
      let t="<table><thead><tr>"+head.map(h=>`<th>${inline(h)}</th>`).join("")+"</tr></thead><tbody>";
      for(const r of body)t+="<tr>"+r.map(c=>`<td>${inline(c)}</td>`).join("")+"</tr>";
      out.push(t+"</tbody></table>");continue;}
    if(/^\s*[-*]\s+/.test(l)){const buf=[];while(i<lines.length&&/^\s*[-*]\s+/.test(lines[i])){buf.push(lines[i].replace(/^\s*[-*]\s+/,""));i++;}out.push("<ul>"+buf.map(x=>`<li>${inline(x)}</li>`).join("")+"</ul>");continue;}
    if(/^\s*\d+\.\s+/.test(l)){const buf=[];while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){buf.push(lines[i].replace(/^\s*\d+\.\s+/,""));i++;}out.push("<ol>"+buf.map(x=>`<li>${inline(x)}</li>`).join("")+"</ol>");continue;}
    if(l.trim()===""){i++;continue;}
    const buf=[];while(i<lines.length&&lines[i].trim()!==""&&!/^\s*(#{1,6}\s|---\s*$|>\s?|\||[-*]\s|\d+\.\s|```)/.test(lines[i])){buf.push(lines[i]);i++;}
    out.push("<p>"+inline(buf.join(" "))+"</p>");}
  return out.join("\n");
}
$("#q").addEventListener("input",renderList);
load();
</script>
</body></html>"""

if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"✅ 등록상품 뷰어 실행 중 → http://localhost:{PORT}")
    print("   (종료: Ctrl+C)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n종료")
