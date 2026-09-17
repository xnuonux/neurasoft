# Pick up here

**For an agent or engineer taking over neurasoft.us.** Written 2026-09-16.

This repository is the canonical source for the live site. It now **reproduces production
byte-for-byte** — that was not true before today, and the two defects that broke it are described
below so they are not reintroduced.

---

## The site is live

```
production   https://neurasoft.us   and   https://www.neurasoft.us
origin       https://neurasoft-research.pages.dev
host         Cloudflare Pages, project neurasoft-research, production branch main
nameservers  isabel.ns.cloudflare.com, mcgrory.ns.cloudflare.com
```

Edition 3: 37 HTML pages (36 content + a 404), seven preserved journal essays, two local
educational exhibits, three attributed research records, an architecture map.

## Build and verify

No npm install, no package install, Python standard library only.

```bash
python build.py                      # writes dist/
python tools/stage_cloudflare.py     # writes artifacts/cloudflare/ (dist minus _redirects)
```

Publish **only `artifacts/cloudflare/`** to the Pages project `neurasoft-research`, branch `main`.
Never publish the repository root, `private/`, or the portable preview.

Verify against production:

```bash
python tools/verify_release.py https://neurasoft-research.pages.dev
```

**Expect `"passed": true` and 49 files checked.** That is the acceptance gate — a fresh build of
this repo is byte-identical to what is served. If it is not, something below was reintroduced.

For the **custom domain** use `tools/verify_proxied_release.py` instead; the proxied domain carries
an edge injection that `verify_release.py` cannot tolerate (see below).

## Tests

```bash
python -m unittest discover -s tests    # 37 pass; 1 error if playwright is absent
node --test tests/search.test.cjs       # 6 pass
```

`tests/test_portable_browser.py` needs `playwright` and will error without it. That is an optional
browser dependency, not a defect.

---

## Two defects fixed today — do not reintroduce them

### 1. Line endings, and why `.gitattributes` is now load-bearing

`build.py` **copies** `assets/` into `dist/` verbatim, and Cloudflare serves those bytes. The
deployed assets are **LF**. This repo had `core.autocrlf=true` and no `.gitattributes`, so a
checkout produced **CRLF** assets — and a build from that checkout produced a site that differed
from production by one byte per line:

```
live   assets/site.js   18,017 bytes   0 CRLF, 232 LF
broken assets/site.js   18,249 bytes   232 CRLF, 0 LF
```

`.gitattributes` now pins `* text=auto eol=lf`. **Do not remove it**, and do not commit assets with
CRLF. Generated HTML is *written* by `write_text()` and is CRLF in production — that is expected
and correct; only the copied assets are pinned.

### 2. The build did not run under a default Windows locale

`build.py` and friends called `read_text()` / `write_text()` with no encoding, so Python used
cp1252 and died on UTF-8 content:

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d
```

The site had only ever been built with UTF-8 mode already on. **34 I/O calls** across the build
scripts and tests now pass `encoding='utf-8'` explicitly. Keep it that way — a new `read_text()`
without an encoding will break the build on any default-locale Windows machine, including a fresh
clone.

---

## Two open items, both Cloudflare dashboard settings

Neither is a code change. The build is correct and needs no redeploy.

**1. Email Address Obfuscation is rewriting the contact links.** Every `mailto:` on `/contact/`
and `/privacy/` is replaced with `/cdn-cgi/l/email-protection#…`:

| origin | `mailto:` | `email-protection` |
|---|---:|---:|
| `pages.dev` | 4 | 0 |
| `neurasoft.us` | **0** | **4** |

The decode script is same-origin so the site's `script-src 'self'` permits it, and the links work
with JavaScript on. **They do not without it**, which contradicts the documented behaviour that
contact links open an email draft with no backend.

Fix: **select the zone → Security → Settings → Email Address Obfuscation → off.**

**2. A Web Analytics beacon is injected and the site's own CSP blocks it.** 367 bytes of
`static.cloudflareinsights.com/beacon.min.js` appended to HTML on HTTP/1.1 requests. Free-plan
proxied domains have had this auto-injected by default since September 2025 — nobody enabled it.

Because the CSP is `script-src 'self'`, a browser refuses the script: **no tracking actually
occurs**, so the edition's no-tracking position holds in practice. What remains is a console
violation and a verifier that cannot pass against the custom domain.

Fix: **Analytics & Logs → Web Analytics → Manage Site → Advanced Options → JS Snippet injection.**
Note this is an *account*-level page, not inside the zone, and there are reports of Pages injecting
it with no working toggle. **Do not add the beacon host to `script-src`** as a workaround — that
weakens the CSP to enable tracking the edition disclaims.

---

## Boundaries to preserve

Taken from `START_HERE_CODEX_PUBLISH.md` and the release docs; they are editorial commitments, not
preferences.

- Warm ivory/sage throughout. No alternating dark sections. Headline: **For what a mind may
  become.**
- Neurasoft is the R&D sector for digital consciousness within **Eternities Inc**; Lunari sits
  alongside it. One programme.
- Both Observatory exhibits are **separate educational models** — not Luna, not the private Psyche
  Lab engine. They must stay labelled as such.
- **No asserted achieved consciousness**, no literal biological species classification, no
  fabricated endorsements or partnerships, no private transcripts, no inferred live results.
- A Psyche Lab result does **not** automatically become a Luna capability. The site carries that
  caveat; keep it.
- Contact links only open email drafts. There is no mail backend and none is needed.
- Research record dates remain **September 14, 2026**; publication prepared **September 16**.
- `private/` is review material and is never published. It is gitignored.

## Where the rest of the record is

- `README.md` — current edition, build layout, which module owns which pages
- `docs/release-2026-09-16.md` — the verified Cloudflare release and rollback
- `docs/domain-cutover-2026-09-16.md` — the completed DNS cutover and the two edge findings
- `docs/publication-edition-3.md` — the edition itself
- `VERIFICATION.md` and `START_HERE_CODEX_PUBLISH.md` — historical V2 evidence, **not** current
  deployment instructions

Rollback for the domain: restore the Namecheap BasicDNS nameservers
`dns1.registrar-servers.com` and `dns2.registrar-servers.com`. To change the site without touching
DNS, deploy a verified revision to the same Pages project.
