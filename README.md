# Neurasoft — Research Publication / Edition 3

Published on Cloudflare Pages, 16 September 2026. 37 HTML pages (36 content pages and a 404), seven preserved journal essays, two local educational exhibits, three attributed research records and an architecture map.

Read `docs/publication-edition-3.md` and `docs/release-2026-09-16.md` for the current release, then `docs/domain-cutover-2026-09-16.md` for the completed neurasoft.us cutover and two open Cloudflare dashboard actions (Email Address Obfuscation is rewriting the contact links; a CSP-blocked analytics beacon is being injected). The V2 handoff and its verification document remain historical evidence, not current deployment instructions.

Build: `python3 build.py`, then `python3 tools/stage_cloudflare.py`. No runtime package installation or npm build is needed. Publish **only `artifacts/cloudflare/`** to the Cloudflare Pages project `neurasoft-research`, branch `main`, using Wrangler. The stage omits Netlify's redirect file because Cloudflare serves the native 404 document. Do not publish the repository root or private review materials.

`edition_three.py` owns the current home, architecture, studies and final editorial amendments. `content/studies.json` is the study registry. `public_search.py` builds the complete main-content index.
`publication.py` owns the earlier expanded editorial pages, navigation and footer.
`build.py` owns the original research pages and journal generation, then invokes the publication and edition layers in that order.
`content/journal.json` holds the seven original notes. `assets/site.css` and `assets/site.js` contain the unified paper/sage theme and local interactions.
`tools/make_portable_preview.py` produces the single-file offline handoff. Do not deploy that preview instead of dist/.

Current verification: 37 Python tests and 6 JavaScript tests pass; 49 hosted files byte-match the build with required headers and a real custom 404. Connected-browser checks cover desktop/mobile presentation, navigation, search, motion pause and the local model/replay/intervention. The 150/40 browser-check counts in VERIFICATION.md belong to the imported V2 handoff and are not new execution claims.

The site is a public editorial publication, not a connection to Luna. No account, analytics, remote fonts, live resident data, or private code is required by public pages. Contact links open email drafts; they do not send mail.
