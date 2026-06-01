---
name: product-detail-page-ko
description: Use this skill whenever the user provides any shopping product URL (Walmart, Amazon, AliExpress, Target, Costco, eBay, or other e-commerce site) and wants a Korean-language 상세페이지, product detail page, reseller listing, 스마트스토어/쿠팡 페이지, or HTML product description generated from it. Trigger for phrases like "상세페이지 만들어줘", "이 URL로 상품 페이지", "크롤해서 상품 정보 가져와", "제품명·가격·이미지 뽑아줘", "월마트 URL 줄테니까", "Amazon 링크로 listing", "product URL to detail page", or any variant where a commerce link should become a polished Korean HTML listing. Also trigger when the user just wants to extract product title/price/images/description/ingredients from a commerce URL — extraction and detail-page rendering share the same pipeline, so even an extraction-only request should use this skill. Make sure to reach for this skill even if the user doesn't explicitly say "detail page"; if a shopping URL goes in and a listing or summary comes out, this is the right tool.
---

# product-detail-page-ko

> **Claude Code 환경 노트 (smartstore-addnew):** 이 스킬은 원래 Cowork 용으로 작성됐다.
> 이 프로젝트에서는 (1) 산출물 저장 위치는 **프로젝트 `output/` 폴더 평탄 저장**이 정답이다
> (CLAUDE.md §3). 아래 본문의 `~/Downloads`·`request_cowork_directory`·서브폴더 지침보다
> CLAUDE.md 가 우선한다. (2) 가격 계산은 본문의 즉석 산식 대신 **`scripts/price_calc.py`** 를 쓴다.
> (3) `present_files` 대신 결과 파일 경로를 사용자에게 알린다. 크롤·추출(Chrome) 절차와
> site-specific 셀렉터(references/)는 그대로 유효하다.


Turn a shopping-site product URL into a Korean-language HTML 상세페이지 plus a structured `product_info.json`. Designed for cross-border resellers (e.g., Canada/US → Korea) who need to repackage a foreign listing into a clean Korean product page quickly.

## When this skill runs

User gives a product URL from Walmart, Amazon, AliExpress, Target, Costco, eBay, or any e-commerce site, and wants a detail page, listing, or structured extraction. Pricing rules (markup, shipping, tax) almost always vary per batch of products, so **always confirm them before rendering** (see "Pricing rules" below).

## The workflow at a glance

1. Clarify pricing rules + output folder with `AskUserQuestion`.
2. Ensure a mounted target folder (usually `~/Downloads`) via `request_cowork_directory`.
3. Fetch the page. Try `mcp__workspace__web_fetch` first; if it fails or the domain isn't allowed, fall back to Claude in Chrome.
4. Extract product data (title, price, image URLs, bullets, specs, ingredients, allergens, rating).
5. Apply the pricing rules to compute the selling price.
6. Render the HTML detail page from the template and write `product_info.json` alongside it.
7. Save everything to an ASCII-named subfolder inside the mounted target folder, then present the files.

Each step has some quirks that waste time if you don't know them in advance. Read through the sections below before starting.

## Step 1 — Clarify pricing rules

Pricing is the one thing the user will almost never repeat the same way twice. Ask the following questions with `AskUserQuestion` before touching the page. Group them into one tool call so the user answers once, not four times:

- **Markup**: flat amount (e.g., +$5 CAD) vs percentage vs fixed KRW amount.
- **Tax (HST/GST/VAT)**: applied or not, and the rate if applied.
- **Shipping**: flat per-item, tiered (e.g., ₩15,000 per 4 items), or included in price.
- **Output currency**: same as source (CAD/USD) vs converted to KRW — and if KRW, what exchange rate to use.

If the user has answered these earlier in the conversation, just confirm with one compact question ("이 규칙 그대로 적용할까요?") rather than re-asking everything.

## Step 2 — Ensure the target folder is mounted

`present_files` can only surface files inside a mounted workspace folder. If nothing is mounted yet, call `mcp__cowork__request_cowork_directory` with `path: "~/Downloads"` (or whichever folder the user named). Once mounted, write files to that path using `Write` — not to the scratch outputs directory, which the user cannot see.

Inside the mounted folder, create one subfolder per product, named with **ASCII only** (non-ASCII filenames currently fail `present_files`). Example: `~/Downloads/oreo_cakesters_detail/OREO_Cakesters_detail.html`.

## Step 3 — Fetch the page

Try the cheap path first:

```
mcp__workspace__web_fetch(url: <product-url>)
```

If it returns `Redirect was cancelled`, `host not on allowlist`, or a 403/503, the site is blocking scrapers and you need a real browser. Fall back to Claude in Chrome:

1. Get tab context: `mcp__Claude_in_Chrome__tabs_context_mcp(createIfEmpty: true)`
2. Navigate the tab: `mcp__Claude_in_Chrome__navigate(tabId: <id>, url: <product-url>)`
3. Pull the readable body: `mcp__Claude_in_Chrome__get_page_text(tabId: <id>)` — this gives you title, description, price, rating, specs, ingredients in one shot.
4. Pull the image URLs and any fields not in the plain text via `mcp__Claude_in_Chrome__javascript_tool`. See `references/extraction.md` for selectors and working snippets per site.

If Chrome isn't installed yet, tell the user to install the "Claude in Chrome" extension — this skill is dead in the water without it whenever `web_fetch` is blocked, which is the common case for Walmart/Amazon/Costco.

## Step 4 — Extract the data

Aim for a `product_info.json` that looks like this. Leave fields empty rather than inventing them:

```json
{
  "source": "Walmart Canada",
  "source_url": "...",
  "product_id": "...",
  "title_en": "...",
  "title_ko": "...",
  "brand": "...",
  "seller": "...",
  "rating": 4.0,
  "review_count": 113,
  "pricing": {
    "cost_original": 4.98,
    "cost_currency": "CAD",
    "markup": 5.00,
    "markup_currency": "CAD",
    "sell_original": 9.98,
    "sell_krw": null,
    "exchange_rate": null,
    "tax_applied": false,
    "shipping_rule": "4개당 ₩15,000"
  },
  "specs": { },
  "description_bullets_en": [ ],
  "description_bullets_ko": [ ],
  "ingredients_en": "",
  "ingredients_ko": "",
  "allergens": { "contains": [], "may_contain": [] },
  "images": [ ],
  "reviews": [ ]
}
```

Korean translations (`title_ko`, `description_bullets_ko`, `ingredients_ko`) should be natural, not literal — Korean shoppers expect a readable listing, not Google Translate output. Keep the English originals alongside so resellers can verify.

## Step 5 — Apply pricing

Compute the selling price deterministically so the user can reproduce it:

- `sell_original = cost_original + markup` (when markup currency matches cost currency)
- `sell_krw = round(sell_original * exchange_rate)` (when converting)
- Shipping/tax lines are shown in the HTML as separate rows, not folded into the unit price — resellers need to see them broken out.

Write the math into the HTML explicitly (e.g., "원가 $4.98 + 마진 $5 = $9.98"). This is what the user actually uses the page for.

## Step 6 — Render the HTML

Use `assets/template.html` as the starting point. It's a self-contained, mobile-friendly Korean product page with sections for gallery, price card, shipping box, description bullets, specs table, ingredients, allergen warning, and review summary. Swap in the extracted values; don't redesign it every time.

Two things worth keeping:
- **Images are referenced from the source CDN** (e.g., `i5.walmartimages.com/...`). This avoids the base64 transport restrictions in `javascript_tool` and keeps image quality at full resolution. The user can right-click → Save Image inside the rendered HTML if they need local JPGs.
- **Strip query strings from image URLs** before writing them into the HTML — the extraction tool blocks responses that include query strings, so you'll want to do this anyway.

## Step 7 — Save and present

Write `index.html` (or `<product>_detail.html`) and `product_info.json` into the per-product folder, then call `mcp__cowork__present_files` with both paths. If `present_files` errors on "not accessible", it usually means either (a) the folder isn't mounted, or (b) the filename contains non-ASCII characters — rename and retry.

## Pricing rules cheat sheet

Common patterns this user has used before (confirm don't assume):

- Markup: flat **+$5 CAD** per item.
- Tax: **HST not applied** (for ambient-temperature groceries under certain thresholds in some Canadian provinces).
- Shipping: **₩15,000 per 4 items** (Korean reseller pricing).
- Currency: keep as CAD in the headline price, show KRW equivalent if exchange rate given.

## Gotchas — read these

See `references/gotchas.md` for the full list. Short version of the ones that bite most often:

- `javascript_tool` silently blocks responses that look like base64-encoded data **or** contain long query strings. Strip query strings with `.split('?')[0]` before returning URLs. Don't try to transport image bytes back through it.
- Heavy pages can freeze the renderer and cause a 45s CDP timeout. If that happens, open the specific resource (e.g., the image URL) in its own tab and query from there.
- `mcp__workspace__web_fetch` has a hard allowlist. Walmart CDN (`i5.walmartimages.com`) is not on it. Use Chrome for anything off the list.
- Browser-triggered downloads via blob URL + `<a download>` are unreliable — Chrome sometimes swallows them without a user gesture. Don't rely on them for the primary deliverable. Reference CDN URLs in the HTML instead and let the user save images from the rendered page.
- `present_files` fails if the filename contains non-ASCII characters (Korean, emoji, etc.). ASCII-safe filenames only.

## Site-specific extraction notes

See `references/extraction.md` for DOM selectors, JSON-LD paths, and known traps for Walmart, Amazon, AliExpress, and a generic fallback.
