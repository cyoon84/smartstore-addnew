# Extraction Playbook

Site-specific selectors and patterns for pulling product data out of commerce pages via Claude in Chrome. Treat these as starting points — e-commerce sites change their DOM often, so if a selector fails, fall back to `get_page_text` + readable parsing and try to grab what you can.

## General approach

Prefer `get_page_text` for narrative content (title, bullets, ingredients, reviews). It strips chrome and returns the core article text, which is usually 80% of what you need for a detail page.

Use `javascript_tool` only for things that need the live DOM: image URLs, structured data blobs (JSON-LD, `__NEXT_DATA__`), or specific attributes. Keep returns small and sanitized:

```javascript
// Always strip query strings from image URLs — javascript_tool blocks responses containing query strings.
img.src.split('?')[0]
```

If a JS response comes back `[BLOCKED]`, it's one of:
- base64-looking content (anywhere in the response)
- URL-encoded or query-string-like content
- large contiguous alphanumeric blobs

Chunk it, strip it, or just pipe through `get_page_text` instead.

## Walmart (walmart.ca / walmart.com)

**Page text**: `get_page_text` reliably returns title, price, rating, "About this item" bullets, specs, ingredients, and a few reviews. Parse for:
- Price: look for `Current price is CAD$X.XX` or `$X.XX`
- Rating: `X stars out of Y reviews` or `(X.Y)|Y`
- Specs: "Specifications" section ends before "Ingredients" or "More details"
- Ingredients: "Ingredients:" prefix, ends at "Contains:" or "May Contain:"

**Images** (JavaScript):
```javascript
(() => {
  const out = new Set();
  const candidates = document.querySelectorAll(
    'div[data-testid="media-thumbnail"] img, ' +
    'div[data-testid="hero-image-container"] img, ' +
    'div[data-testid="media-gallery"] img'
  );
  candidates.forEach(img => {
    const src = img.currentSrc || img.src || '';
    if (src && /walmartimages/i.test(src)) out.add(src.split('?')[0]);
  });
  // Fallback: images inside the same subtree as <h1>
  const title = document.querySelector('h1');
  if (title) {
    let el = title;
    for (let i = 0; i < 6 && el && el.parentElement; i++) el = el.parentElement;
    if (el) el.querySelectorAll('img').forEach(img => {
      const src = img.currentSrc || img.src || '';
      if (src && /walmartimages/i.test(src)) out.add(src.split('?')[0]);
    });
  }
  return Array.from(out).slice(0, 10).join('\n');
})()
```

**Traps**:
- `document.querySelectorAll('script[type="application/ld+json"]')` sometimes returns stringified JSON with query strings embedded — `javascript_tool` will block the entire response. Don't return raw JSON-LD; extract fields and return plain strings.
- Walmart image CDN (`i5.walmartimages.com`) is **not** on the `web_fetch` allowlist. Don't try to download images that way. Either (a) reference the CDN URL directly in the HTML (preferred), or (b) navigate a separate tab to the image URL and fetch from same-origin inside the browser.
- The DOM also contains "Similar items" and "Customer Also Bought" images. Filter to the primary gallery using the selectors above or by proximity to `<h1>`.

## Amazon (amazon.com / amazon.ca / amazon.co.jp)

Amazon is more aggressive about bot blocking than Walmart. Expect:
- CAPTCHA on cold navigation — user may need to solve it manually in the tab once per session.
- A/B-tested DOM — selectors that work one day may not the next. Always have a `get_page_text` fallback.

**Page text** is usually enough for title (`#productTitle`), price (`#corePriceDisplay_desktop_feature_div`), bullets (`#feature-bullets`), and description (`#productDescription`).

**Images** (JavaScript):
```javascript
(() => {
  // Amazon stashes the image gallery in window.ImageBlockATF.data or a colorImages JSON
  const out = new Set();
  // Main image
  const main = document.querySelector('#landingImage, #imgBlkFront, #main-image');
  if (main) out.add((main.currentSrc || main.src).split('?')[0]);
  // Thumbnails
  document.querySelectorAll('#altImages img, li.imageThumbnail img').forEach(img => {
    let src = (img.currentSrc || img.src || '').split('?')[0];
    // Amazon thumbnails use ._SS40_ etc. suffixes; strip to get full-size
    src = src.replace(/\._[^.]+_\./, '.');
    if (src) out.add(src);
  });
  return Array.from(out).slice(0, 10).join('\n');
})()
```

**Traps**:
- Amazon variants (size, color) change the URL and image set. If the user gave a specific variant URL, don't click around — stay on that variant.
- Price is often split across nodes (`<span class="a-price-whole">`, `<span class="a-price-fraction">`). Concatenate carefully.
- Some pages require scroll to load the image gallery lazy-loaded. If images are missing, scroll with `window.scrollTo(0, document.body.scrollHeight)` then re-query after a short delay.

## AliExpress / Temu

- Heavy JS hydration — wait a beat after `navigate` before querying.
- Price varies by shipping country; the URL often contains a locale hint, respect it.
- Images are usually on `ae01.alicdn.com` or `img.kwcdn.com`. Same rule: reference the CDN URL in HTML rather than trying to download.
- Descriptions are often image-only (no text). In that case, list the detail images in the HTML gallery and note that the "description is in the images" in `product_info.json`.

## Target, Costco, eBay, and generic fallback

Generic recipe when site-specific selectors aren't known:

1. `get_page_text` → parse title from the page `<h1>` equivalent, price from any `$X.XX` near the top of the text, bullets from any list-looking section.
2. JSON-LD sweep:
   ```javascript
   (() => {
     const nodes = document.querySelectorAll('script[type="application/ld+json"]');
     const hits = [];
     nodes.forEach(n => {
       try {
         const d = JSON.parse(n.textContent);
         const arr = Array.isArray(d) ? d : [d];
         arr.forEach(x => {
           if (x['@type'] === 'Product' || (Array.isArray(x['@type']) && x['@type'].includes('Product'))) {
             hits.push({
               name: x.name || '',
               brand: (x.brand && (x.brand.name || x.brand)) || '',
               sku: x.sku || '',
               priceCurrency: x.offers && x.offers.priceCurrency,
               price: x.offers && x.offers.price,
               rating: x.aggregateRating && x.aggregateRating.ratingValue,
               reviewCount: x.aggregateRating && x.aggregateRating.reviewCount,
               imageCount: Array.isArray(x.image) ? x.image.length : (x.image ? 1 : 0)
             });
           }
         });
       } catch(e) {}
     });
     return JSON.stringify(hits);
   })()
   ```
   This gives you a clean structured summary on most modern e-commerce pages.
3. For images when JSON-LD is missing: grab all `img[src]` under the top 3 ancestors of `<h1>`, filter out site-logo URLs.
4. If all else fails, ask the user to paste the product title/price manually — don't fabricate data.

## Sanity checks before rendering

- Title is non-empty and plausibly a product name (not "Loading..." or "Access Denied").
- Price is a number, not a string like "See price in cart".
- At least one image URL.
- If any of these are missing, say so in chat before writing the HTML. It's fine to render a partial page as a placeholder, but the user should know.
