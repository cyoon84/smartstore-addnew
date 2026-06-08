#!/usr/bin/env node
/*
 * finchmart_ca 등록상품 뷰어 — 무의존성 Node 서버 (빌트인 http/fs/path 만 사용)
 *
 * 문서(docs) 스타일: 좌측 접이식 사이드바(제품목록 → 클릭 시 폴더 파일 펼침) → 파일 클릭 시 우측 본문.
 *   .md = 경량 마크다운 렌더 / .html = iframe / .json = 정렬출력 / 이미지 = <img> / .xlsx = 다운로드
 *
 * 실행:  node scripts/dashboard_server.js [port]    (기본 4178)
 * 종료:  Ctrl+C
 */
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.dirname(__dirname);
const NEW_ITEM = path.join(ROOT, "output", "new-item");
const SKIP = new Set(["_batch", "_misc", "_dashboard", "_seo_refresh"]);
const PORT = parseInt(process.argv[2] || "4178", 10);

const MIME = {
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
  ".webp": "image/webp", ".gif": "image/gif", ".html": "text/html; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".md": "text/plain; charset=utf-8",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ".csv": "text/csv; charset=utf-8", ".txt": "text/plain; charset=utf-8",
};
const IMG_RE = /\.(jpg|jpeg|png|webp|gif)$/i;

function deepFind(obj, keys) {
  if (obj && typeof obj === "object") {
    if (!Array.isArray(obj)) {
      for (const k of keys) {
        const v = obj[k];
        if (v !== undefined && v !== null && v !== "" && !(Array.isArray(v) && !v.length)) return v;
      }
    }
    for (const v of Object.values(obj)) {
      const r = deepFind(v, keys);
      if (r !== undefined && r !== null && r !== "") return r;
    }
  }
  return null;
}
function toInt(v) {
  if (typeof v === "number") return Math.round(v);
  if (typeof v === "string") { const m = v.match(/\d[\d,]*/); if (m) return parseInt(m[0].replace(/,/g, ""), 10); }
  return null;
}

function listProducts() {
  const out = [];
  for (const slug of fs.readdirSync(NEW_ITEM)) {
    if (SKIP.has(slug)) continue;
    const dir = path.join(NEW_ITEM, slug);
    let st; try { st = fs.statSync(dir); } catch { continue; }
    if (!st.isDirectory()) continue;
    const files = fs.readdirSync(dir);
    const pj = files.find(f => f.endsWith("_product_info.json"));
    let title = slug, price = null, mode = "single", registered = "", live = "";
    if (pj) {
      try {
        const d = JSON.parse(fs.readFileSync(path.join(dir, pj), "utf-8"));
        title = deepFind(d, ["title_ko", "product_name_ko", "title"]) || slug;
        price = toInt(deepFind(d, ["sell_price_krw", "sell_krw", "selling_price_krw", "sale_price_krw"]));
        mode = deepFind(d, ["mode"]) || "single";
        registered = deepFind(d, ["registered_at"]) || "";
        live = deepFind(d, ["live_url"]) || "";
      } catch {}
    }
    out.push({ slug, title, price, mode, registered, live, nfiles: files.length });
  }
  out.sort((a, b) => (a.title || "").localeCompare(b.title || "", "ko"));  // A-Z · ㄱ-ㅎ
  return out;
}

function listFiles(slug) {
  const dir = path.join(NEW_ITEM, slug);
  const files = fs.readdirSync(dir).filter(f => !f.startsWith("."));
  const typ = (f) => {
    const l = f.toLowerCase();
    if (l.endsWith(".md")) return "md";
    if (l.endsWith(".html")) return "html";
    if (l.endsWith(".json")) return "json";
    if (l.endsWith(".xlsx")) return "xlsx";
    if (IMG_RE.test(l)) return "image";
    return "other";
  };
  const order = { md: 0, html: 1, json: 2, xlsx: 3, image: 4, other: 5 };
  return files.map(f => ({ name: f, type: typ(f), size: fs.statSync(path.join(dir, f)).size }))
              .sort((a, b) => (order[a.type] - order[b.type]) || a.name.localeCompare(b.name));
}

function safePath(slug, name) {
  const rp = path.normalize(path.join(NEW_ITEM, slug || "", name || ""));
  return rp.startsWith(NEW_ITEM) ? rp : null;
}
function json(res, obj) { res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" }); res.end(JSON.stringify(obj)); }

const server = http.createServer((req, res) => {
  const u = new URL(req.url, `http://localhost:${PORT}`);
  try {
    if (u.pathname === "/") { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(PAGE); return; }
    if (u.pathname === "/api/products") { json(res, listProducts()); return; }
    if (u.pathname === "/api/files") { json(res, listFiles(u.searchParams.get("slug"))); return; }
    if (u.pathname === "/raw") {
      const fp = safePath(u.searchParams.get("slug"), u.searchParams.get("name"));
      if (!fp || !fs.existsSync(fp)) { res.writeHead(404); res.end("not found"); return; }
      const ext = path.extname(fp).toLowerCase();
      const headers = { "Content-Type": MIME[ext] || "application/octet-stream" };
      if (ext === ".xlsx") headers["Content-Disposition"] = `attachment; filename="${path.basename(fp)}"`;
      res.writeHead(200, headers);
      fs.createReadStream(fp).pipe(res);
      return;
    }
    res.writeHead(404); res.end("not found");
  } catch (e) { res.writeHead(500); res.end("error: " + e.message); }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`✅ 등록상품 뷰어 실행 중 → http://localhost:${PORT}`);
  console.log(`   (종료: Ctrl+C)`);
});

const PAGE = String.raw`<!DOCTYPE html>
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
let SIG="";
async function load(){
  try{
    const r=await(await fetch("/api/products")).json();
    const sig=r.length+":"+r.map(x=>x.slug+(x.live?"*":"")).join(",");
    if(sig!==SIG){const first=SIG==="";SIG=sig;PRODUCTS=r;renderList();
      if(!first)flash(r.length);}
  }catch(e){}
}
function flash(n){const b=$("#cnt");if(b){b.style.color="#1f8a4c";setTimeout(()=>b.style.color="",1500);}}
function renderList(){
  const q=$("#q").value.trim().toLowerCase();
  const rows=PRODUCTS.filter(p=>!q||(p.title+" "+p.slug).toLowerCase().includes(q));
  $("#cnt").textContent=rows.length+"/"+PRODUCTS.length;
  const list=$("#list");list.innerHTML="";
  for(const p of rows){
    const it=document.createElement("div");it.className="item";
    const head=document.createElement("div");head.className="it-head";
    head.innerHTML='<span class="caret">▶</span><span class="it-title">'+esc(p.title)+(p.live?' <span title="판매중" style="font-size:9px">🟢</span>':"")+'</span>';
    const files=document.createElement("div");files.className="files";
    const meta=document.createElement("div");meta.className="meta-line";
    meta.innerHTML=(p.mode==="group"?"그룹":"단일")+" "+(p.price?'· <span class="price">'+won(p.price)+'</span>':"· 가격미상")+" "+(p.registered?"· "+p.registered:"")+(p.live?' · <a href="'+p.live+'" target="_blank" style="color:#1f8a4c">🟢 라이브</a>':"");
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
      fe.innerHTML='<span class="ficon">'+(ICON[f.type]||"📎")+'</span><span>'+esc(f.name.replace(slug+"_",""))+'</span><span class="fsize">'+(f.size/1024).toFixed(0)+'KB</span>';
      fe.addEventListener("click",e=>{e.stopPropagation();
        filesEl.querySelectorAll(".file.sel").forEach(x=>x.classList.remove("sel"));fe.classList.add("sel");openFile(slug,f);});
      filesEl.appendChild(fe);
    }
    filesEl.dataset.loaded="1";
  }
}
async function openFile(slug,f){
  const url="/raw?slug="+encodeURIComponent(slug)+"&name="+encodeURIComponent(f.name);
  $("#rtitle").textContent=f.name;$("#rdl").innerHTML='· <a href="'+url+'" target="_blank" download>다운로드</a>';
  const view=$("#view");view.className="";view.innerHTML="로딩…";
  if(f.type==="image"){view.classList.add("pad0");view.innerHTML='<div style="padding:26px"><img class="preview" src="'+url+'"></div>';return;}
  if(f.type==="xlsx"){view.innerHTML='<div class="placeholder">📊 엑셀은 미리보기 불가 — <a href="'+url+'" download style="color:var(--acc)">다운로드</a> 해서 여세요.</div>';return;}
  if(f.type==="html"){view.classList.add("pad0");view.innerHTML='<iframe src="'+url+'"></iframe>';return;}
  const txt=await(await fetch(url)).text();
  if(f.type==="json"){let s=txt;try{s=JSON.stringify(JSON.parse(txt),null,2);}catch{}view.innerHTML='<div class="json">'+esc(s)+'</div>';return;}
  if(f.type==="md"){view.innerHTML='<div class="md">'+mdToHtml(txt)+'</div>';return;}
  view.innerHTML="<pre>"+esc(txt)+"</pre>";
}
function mdToHtml(src){
  const BT=String.fromCharCode(96);
  const fence=s=>s.replace(/^\s+/,"").slice(0,3)===BT+BT+BT;
  const codeRe=new RegExp(BT+"([^"+BT+"]+)"+BT,"g");
  const lines=src.replace(/\r/g,"").split("\n");let out=[],i=0;
  const inline=s=>esc(s).replace(codeRe,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>');
  while(i<lines.length){let l=lines[i];
    if(fence(l)){const buf=[];i++;while(i<lines.length&&!fence(lines[i])){buf.push(lines[i]);i++;}i++;out.push("<pre><code>"+esc(buf.join("\n"))+"</code></pre>");continue;}
    if(/^#{1,6}\s/.test(l)){const m=l.match(/^(#{1,6})\s+(.*)$/);out.push("<h"+m[1].length+">"+inline(m[2])+"</h"+m[1].length+">");i++;continue;}
    if(/^\s*---\s*$/.test(l)){out.push("<hr>");i++;continue;}
    if(/^\s*>\s?/.test(l)){const buf=[];while(i<lines.length&&/^\s*>\s?/.test(lines[i])){buf.push(lines[i].replace(/^\s*>\s?/,""));i++;}out.push("<blockquote>"+inline(buf.join(" "))+"</blockquote>");continue;}
    if(/^\s*\|.*\|\s*$/.test(l)&&i+1<lines.length&&/^\s*\|[\s:|-]+\|\s*$/.test(lines[i+1])){
      const row=s=>s.trim().replace(/^\||\|$/g,"").split("|").map(c=>c.trim());
      const head=row(l);i+=2;const body=[];
      while(i<lines.length&&/^\s*\|.*\|\s*$/.test(lines[i])){body.push(row(lines[i]));i++;}
      let t="<table><thead><tr>"+head.map(h=>"<th>"+inline(h)+"</th>").join("")+"</tr></thead><tbody>";
      for(const r of body)t+="<tr>"+r.map(c=>"<td>"+inline(c)+"</td>").join("")+"</tr>";
      out.push(t+"</tbody></table>");continue;}
    if(/^\s*[-*]\s+/.test(l)){const buf=[];while(i<lines.length&&/^\s*[-*]\s+/.test(lines[i])){buf.push(lines[i].replace(/^\s*[-*]\s+/,""));i++;}out.push("<ul>"+buf.map(x=>"<li>"+inline(x)+"</li>").join("")+"</ul>");continue;}
    if(/^\s*\d+\.\s+/.test(l)){const buf=[];while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){buf.push(lines[i].replace(/^\s*\d+\.\s+/,""));i++;}out.push("<ol>"+buf.map(x=>"<li>"+inline(x)+"</li>").join("")+"</ol>");continue;}
    if(l.trim()===""){i++;continue;}
    const buf=[];while(i<lines.length&&lines[i].trim()!==""&&!fence(lines[i])&&!/^\s*(#{1,6}\s|---\s*$|>\s?|\||[-*]\s|\d+\.\s)/.test(lines[i])){buf.push(lines[i]);i++;}
    out.push("<p>"+inline(buf.join(" "))+"</p>");}
  return out.join("\n");
}
$("#q").addEventListener("input",renderList);
load();
setInterval(load,20000);  // 새 제품 자동 감지·리프레시(20초)
</script>
</body></html>`;
