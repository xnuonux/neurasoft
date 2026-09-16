# Domain cutover record — neurasoft.us

Completing the release recorded in `release-2026-09-16.md`, which stopped at the Namecheap
nameserver step. Verified 2026-09-16 by Claude (Opus 5).

## The cutover completed

`neurasoft.us` now delegates to the prepared Cloudflare nameservers.

```
neurasoft.us  nameserver = isabel.ns.cloudflare.com
neurasoft.us  nameserver = mcgrory.ns.cloudflare.com
```

Resolving to Cloudflare anycast (`104.21.46.134`, `172.67.139.43`, and two IPv6). Apex, `www` and
the Pages origin all return HTTP 200. The registrar sign-in that blocked the previous session was
completed; no DNS approval was re-requested.

## Verification of the custom domain

The previous release verified `neurasoft-research.pages.dev`. **The custom domain had never been
verified**, and it does not serve identical bytes, because it is proxied through the Cloudflare
zone while `pages.dev` is not.

Checked all 49 public files on `https://neurasoft.us` and `https://www.neurasoft.us` against the
local `dist/` with SHA-256, using a browser user-agent:

| result | count |
|---|---:|
| byte-exact against the build | **46** |
| altered by the edge | **2** (`/contact/`, `/privacy/`) |
| redirect instead of document | **1** (`/404.html` → 308) |

Headers on every route checked: `content-security-policy` present, `x-content-type-options:
nosniff` present, `permissions-policy` present. An unknown route returns **HTTP 404** with the
real custom 404 document (`<title>Page not found — Neurasoft</title>`, 5,476 bytes). Apex, `www`
and `pages.dev` serve byte-identical homepages.

**The build is intact.** Both alterations are introduced by the Cloudflare edge, not by the
deployment.

## Finding 1 — Email Address Obfuscation has broken the contact links

Cloudflare's Email Address Obfuscation is enabled on the zone and rewrites every `mailto:` link.

| origin | `mailto:` links on /contact/ | `email-protection` links |
|---|---:|---:|
| `neurasoft-research.pages.dev` | **4** | 0 |
| `neurasoft.us` | **0** | **4** |
| `www.neurasoft.us` | **0** | **4** |
| local `dist/contact/index.html` | 4 | — |

Every `mailto:` is replaced with `/cdn-cgi/l/email-protection#<hex>`, and the visible address is
replaced with a `data-cfemail` attribute. `/privacy/` is affected the same way (+235 bytes);
`/contact/` grows by 475 bytes.

`/cdn-cgi/scripts/.../email-decode.min.js` returns HTTP 200 and is same-origin, so the site's
`script-src 'self'` policy permits it — **with JavaScript enabled the links are restored at
runtime and do work.**

**With JavaScript disabled they do not.** The contact address renders as an obfuscated string and
the links point at a Cloudflare redirect. This contradicts the documented behaviour that contact
links open an email draft with no backend, and it is a regression introduced by the cutover: the
same pages are correct on `pages.dev`.

## Finding 2 — a Web Analytics beacon is injected, and the site's own CSP blocks it

On HTTP/1.1 requests the edge appends 367 bytes to HTML documents:

```html
<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js/..."
        data-cf-beacon='{"version":"2024.11.0","token":"fc5a...","r":1,"spa":2}'
        crossorigin="anonymous"></script>
```

Not observed on HTTP/2 requests from `curl`, which is why the 49-file pass above shows it on zero
routes; it appeared consistently on every HTTP/1.1 fetch.

Two problems:

1. **It cannot work.** The site's CSP is `script-src 'self'`. `static.cloudflareinsights.com` is
   not `'self'`, so a browser receiving this document will refuse the script and log a CSP
   violation. The analytics collect nothing and every affected page load produces a console error.
2. **It is tracking.** `RELEASE-NOTES.md` states the edition adds no tracking, and `README.md`
   states no analytics are required by public pages. A zone-level beacon contradicts both.

## Finding 3 — `/404.html` returns 308

Requesting `/404.html` directly returns HTTP 308 with an empty body rather than the document.
Cloudflare Pages normalises the path. **Cosmetic**: unknown routes correctly return HTTP 404 with
the real custom 404 body, which is the behaviour that matters. No action proposed.

## Why the previous verifier reported a total failure

`tools/verify_release.py` compares raw bytes fetched with `urllib`, and reported 37 of 49 routes
mismatched on the custom domain. That is the beacon injection, not a bad deployment — `urllib`
sends HTTP/1.1, so every HTML route it fetched carried the extra 367 bytes.

Two consequences worth recording:

- **The tool cannot verify a proxied Cloudflare domain as written.** It is correct against
  `pages.dev` and will be correct against the custom domain again once the beacon is off.
- A default Python user-agent receives **HTTP 403** from the zone, so bot management is active on
  the custom domain and was not on `pages.dev`.

## Required actions, both in the Cloudflare dashboard

Neither is a code or deployment change; the build is correct and needs no redeploy.

1. **Disable Email Address Obfuscation** — Scrape Shield. Restores the `mailto:` links to the
   documented behaviour.
2. **Disable Web Analytics / the beacon** for this zone. It is CSP-blocked and therefore useless,
   and it contradicts the stated no-tracking position. The alternative — adding
   `static.cloudflareinsights.com` to `script-src` — is **not** recommended: it would weaken the
   CSP and introduce the tracking the edition explicitly disclaims.

Re-run `python tools/verify_release.py https://neurasoft.us` after both are off. It should then
report `passed: true` against the custom domain with no changes to the tool.

## Unchanged

No source, build, deployment or DNS record was modified in this verification pass. Nameservers,
the Cloudflare Pages project, the deployed commit and the zone's mail records were all left as
found. Rollback remains as recorded in `release-2026-09-16.md`: restore the Namecheap BasicDNS
nameservers `dns1.registrar-servers.com` and `dns2.registrar-servers.com`.
