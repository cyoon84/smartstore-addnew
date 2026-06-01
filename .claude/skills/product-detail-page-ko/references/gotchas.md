# Gotchas

Things that wasted time during the first run of this workflow. Read before starting so you don't rediscover them.

## javascript_tool response filter

The Chrome extension's `javascript_tool` has an opaque content filter that will replace your entire response with `[BLOCKED: ...]` if the output looks like:

- **Base64 data** — even partial. 5,000 chars of base64 is enough to trip the filter. There is no safe way to return binary data through this tool. Don't try to transport image bytes back as base64 or hex; they will be blocked.
- **Query strings / URL-encoded fragments** — if your return value contains URLs with `?key=value` fragments, the whole response can be blocked. Strip them with `.split('?')[0]` before returning. This applies to image URLs, product URLs, anything.
- **Cookies / session-token-looking strings** — long alphanumeric runs are risky; sanitize or chunk.

Practical rules:
- Always post-process URLs: `url.split('?')[0]`
- Always return small, human-readable strings
- If you need bytes out of the browser, don't — reference the resource URL in the HTML instead, or navigate to it in a new tab and let the browser's native save-image UX handle it

## web_fetch allowlist

`mcp__workspace__web_fetch` has a fixed allowlist. As of writing, the allowed shopping-related domains include `*.walmart.ca` and `www.walmart.ca`. Most image CDNs (`i5.walmartimages.com`, `m.media-amazon.com`, `ae01.alicdn.com`, etc.) are not on it and return `cowork-egress-blocked`.

Implications:
- You cannot download product images via `web_fetch` for most sites.
- You cannot bypass blocks by using `curl` or `wget` in bash — the workspace egress is filtered at the network level.
- Reference CDN URLs directly in the HTML. This is reliable and preserves image quality. Ask the user to right-click → Save Image if they need local copies.

## Renderer freezes

If the product page is heavy (lots of JS, ad iframes, React hydration), a `javascript_tool` call that does `fetch()` from inside the product tab can hang and hit the 45-second CDP timeout. Signs: the prior call worked, then a slightly bigger one times out; subsequent calls on the same tab also time out.

Workarounds in order of preference:
1. Do expensive fetches in a **separate tab** opened directly on the resource URL (same-origin fetch then works without CORS and without the product-page JS thrashing).
2. Add an `AbortController` with a 10s timeout so a hang fails fast instead of hitting 45s.
3. Navigate the product tab away (e.g., to `about:blank`) and back if it seems stuck.

## Browser download unreliability

Triggering downloads via `<a download href=blob:...>` followed by `a.click()` works about 80% of the time in practice, but sometimes Chrome silently refuses because there's no user gesture, or saves to a non-default location. Don't make the deliverable depend on these.

Preferred pattern:
- Keep image references as CDN URLs in the HTML (always works).
- If the user specifically asks for local image files, trigger the downloads as a best-effort extra and tell them to check `~/Downloads`; if the files aren't there, fall back to the right-click-save instruction.

## present_files path requirements

`mcp__cowork__present_files` needs:
- The path to be inside a mounted workspace folder. Files in the scratch outputs directory are not visible to the user.
- ASCII-only filenames. Non-ASCII characters (Korean, Chinese, emoji) cause "not accessible on the user's computer" errors.

Before presenting:
1. Ensure `mcp__cowork__request_cowork_directory` has mounted the target (`~/Downloads` is a safe default).
2. Use ASCII filenames like `OREO_Cakesters_detail.html`. If the user wants a Korean filename, rename at the very end after presenting — or skip `present_files` and just tell them the path.

## get_page_text returns adjacent content too

On a product page, `get_page_text` often includes "Similar items" and "Customer Also Bought" sections — sometimes hundreds of other products. The target product data is usually near the top and again near the bottom ("Product details", "Specifications", "Ingredients"). Parse conservatively:

- Match the title from the page `<title>` tag first; use it to locate the corresponding block in the body text.
- Stop extracting bullets when you see "Similar items", "Customer Also Bought", "You may also like", or "Related".

## Don't fabricate

If a field can't be extracted (e.g., ingredients missing, price says "See price in cart"), leave it blank in `product_info.json` and in the HTML. Never fill in plausible-sounding fake data — resellers use this page directly for customer-facing listings. A missing ingredients section is fine. An invented one is a lawsuit.
