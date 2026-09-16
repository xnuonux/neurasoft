# Neurasoft research publication — verification

> Imported V2 verification testimony, not a fresh execution record for edition 3. Current locally executed checks and hosting verification are documented in docs/publication-edition-3.md and docs/release-2026-09-16.md. Historical counts and failures below are retained.

Edition prepared September 16, 2026.

## Passed
- 27 static checks: 33 pages, unique IDs, link targets, source isolation, metadata, local assets, search index, sitemap, security header/configuration presence.
- 150 browser checks using built HTML/CSS/JavaScript injected into local Chromium: 32 content pages at 390px and 1440px; heading visibility, horizontal overflow, menu/search/journal filtering, original model/replay/intervention/export behavior, motion controls and zero observed page errors.
- 40 expanded-preview checks: route changes through the single-file preview, new-page search, ten deep routes, mobile navigation/overflow, and explicit state-machine behavior for recovery, single-use permission, deferral, action, repeat blocking, simulated restart and reset. Zero observed runtime errors.

## Preserved failures / limits
The original static suite initially failed only its old counts (18 pages / 17 sitemap URLs). Those expectations were updated to the actual expanded scope (33 / 32), not removed. All remaining checks passed before and after that count update.
Direct file:// navigation is blocked by this environment's browser administration policy. The complete preview HTML was therefore exercised via Playwright set_content. This verifies the embedded page logic, not a hosted production origin or Windows file navigation.
A prior attempt to retrieve generated remote stills failed at network connection. They are not embedded or required; the build uses local procedural art.
The final CSS-only layout correction restores the introductory section gutter and moves a decorative label. The static suite was rerun, and the final preview checks exercised the corrected build.
No production upload, DNS change, GitHub push, runtime Luna access, live lab experiment, independent research replication, formal accessibility certification, Safari/Firefox test, or performance benchmark is claimed.

## Commands
```
python3 build.py
python3 -m unittest discover -s tests -p test_site.py -v
python3 tests/run_browser_checks.py
python3 tools/make_portable_preview.py
python3 tests/check_expanded_preview.py
```
Browser tests need Python Playwright and a Chromium executable. The built public site needs neither dependency.
