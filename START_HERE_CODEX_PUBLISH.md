# START HERE — publish Neurasoft research publication edition 2

> Historical V2 handoff, preserved as supplied. For the current edition and Cloudflare deployment, start at README.md and docs/release-2026-09-16.md. The earlier Netlify hosting route below was tested but did not serve the new release; no domain was pointed there.

## Exact deliverables
- NEURASOFT_RESEARCH_SOURCE_V2.zip: editable project in `neurasoft/`, with source, tests, documentation, and built `dist/`.
- NEURASOFT_RESEARCH_DEPLOY_V2.zip: only the ready-built contents of `dist/` at the archive root.
- NEURASOFT_RESEARCH_PREVIEW_V2.html: complete self-contained 33-page preview for inspection; NOT the production document.

This supersedes the earlier 18-page prototype. It is not the Eternities 32-page site. Keep the two deployments separate.

## Integration
Find the actual Neurasoft source repository and compare current work before editing. Do not assume its repository name, erase a concurrent redesign, overwrite a running research program, or put this build into the Eternities production site. Preserve the existing deployment and identify its rollback.

Unzip the source, change into `neurasoft/`, and run `python3 build.py`. Python standard library only; no npm installation is necessary to generate the site. Commit the editable build files and content to the correct source repository. Preserve private/ as non-published review material, or store it separately under existing private conventions.

## Publish
The intended domain is https://neurasoft.us. The existing Netlify project observed earlier in this conversation was `ae4e0565-9944-4109-bb65-2d9a21ea6884`; verify through the current account that it is still the Neurasoft domain's actual project before using it. Do not create another site or change DNS merely because it is convenient.

Use build command `python3 build.py`, publish directory `dist`. Never publish the source root, private/, test outputs, source ledger, or this handoff. A manual deploy can use the deploy ZIP's extracted root without a build.

Create a preview first. Check the full navigation, both exhibits, local search, mobile menu, reduced motion, contact draft links, all source links, actual 404 behavior, headers and canonical domain on the hosted origin. Then use the user's publishing authority for a verified production deployment. Return the Git commit, deploy URL, production URL and actual verification result. If authority is unclear, keep the preview and ask before changing production.

## Preserve the intended experience
Warm ivory/sage throughout, no alternating dark sections. Main headline: For what a mind may become. Corporate relationship: Neurasoft and Lunari under Eternities Inc. Distinguish vision, research, and operational observations. No asserted achieved consciousness, literal biological species classification, fabricated endorsements/partnerships, private transcripts, or inferred live results. Research record dates remain September 14, 2026; publication prepared September 16.

Both Observatory exhibits are separate educational models, not Luna or the private Psyche Lab engine. They must remain labeled. The contact links only open email drafts; there is no website mail backend to activate. The site intentionally needs no provider credentials.

## Image status
Local procedural artwork and motion are included. The previously generated Runway stills are not part of this release because their bytes could not be retrieved. The entire site and preview remain self-contained rather than depending on expiring remote URLs. Do not present concept art as lab footage, measured telemetry, or an actual robot installation.
