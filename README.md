# Neurasoft — Research Publication / Edition 2

Prepared 2026-09-16. 33 HTML pages (32 content pages and a 404), seven journal essays, two local educational exhibits.

Build: `python3 build.py`. No runtime package installation or npm build is needed.
Publish **only `dist/`**. `netlify.toml` already uses that directory.
Read `START_HERE_CODEX_PUBLISH.md` before integrating or deploying.

`publication.py` owns the expanded editorial pages, new homepage, navigation and footer.
`build.py` owns the original research pages and journal generation, and invokes publication.py.
`content/journal.json` holds the seven original notes. `assets/site.css` and `assets/site.js` contain the unified paper/sage theme and local interactions.
`tools/make_portable_preview.py` produces the single-file offline handoff. Do not deploy that preview instead of dist/.

Verification: 27 static tests; 150 browser checks; 40 expanded-preview checks. See VERIFICATION.md for scope and limits.

The site is a public editorial publication, not a connection to Luna. No account, analytics, remote fonts, live resident data, or private code is required by public pages. Contact links open email drafts; they do not send mail.
