# Publication continuity — editorial extension, 2026-09-16

This change preserves the Edition 3 renderer and its ivory/sage design. It adds a
reviewed publication layer at the EXISTING Cloudflare staging boundary. It does not
claim the live site has been deployed, science re-executed, or private evidence released.

## Public polish and canonical name

`content/identity.json` records Dom's confirmation: **Luna — Locus of Unified Noetic
Agency**. `content/publication.json` holds reviewed editorial changes, the current
research question and three distinct scope dates. These curated inputs produce the
Luna/glossary name sections, homepage question, `/updates/`, RSS, public `llms.txt`,
search entries and a machine-readable edition record. Historical journal main bodies
and scientific data remain unchanged. Source timestamps never advance the review dates.

## Build, stage, review, then deploy separately

    python build.py
    python -m unittest discover -s tests -p test_continuity.py -v
    python tools/stage_cloudflare.py
    python tools/verify_publication.py

The original `dist/` is deliberately untouched. The final candidate is
`artifacts/cloudflare/`, not dist and never the repository root. Staging uses a
scratch directory before replacing the previous local stage; this is not a durable
transaction or an external deployment guarantee. Repeating the same publication
transform is idempotent; changing metadata requires rebuilding a clean stage.

**Verification transition:** old `verify_release.py` / `verify_proxied_release.py`
compare against the original `dist/`. Their old 49-file acceptance figure is historical
and is NOT proof that this amended final stage matches an origin. The new offline
`verify_publication.py` enumerates final bytes and validates the publication additions.
After a separately authorized release, compare the serving origin against THAT manifest,
then inspect the custom domain and any Cloudflare edge transformation separately.
No hosted readback or deployment is performed by the added CI workflow.

Before merging: build and stage this branch against the current complete checkout,
review desktop/mobile pages, and retain the artifact manifest. The development packet's
local tests cover fixtures and an older supplied edition, not a full clone of current
main. GitHub CI is provided to perform the full current-branch build, but its success
must be observed rather than assumed. No Cloudflare credentials, settings or DNS change.

## Drift review is not an autonomous copywriter

`company/claims.json` maps THREE curated source dependencies to affected surfaces.
`continuity_audit.py` resolves each configured ref to a commit, then reads the file's
Git blob identity at that commit. It reports changed/missing/unavailable/expired sources,
revoked approval and overdue editorial review. An unrelated repo commit that leaves the
listed file unchanged is not a drift alert. Missing credentials/403/404 are never fresh.
No source content is executed, no public claim is rewritten and no baseline is advanced.

    python continuity_audit.py

Exit 0 means no drift detected among the configured checks; exit 2 means review or
better access is required. Neither establishes truth or complete coverage. Optional
`--observations path.json --at ISO_TIME` supports bounded offline fixtures. Reports stay
under `artifacts/continuity`, outside the public stage; they contain private repo IDs.
Do not serve them. Only positive allowlisted fields enter public metadata.

The scheduled workflow is dormant until present on default main and Actions is enabled.
It proposes a daily 13:23 UTC scan and stores a private artifact; it does not open PRs,
monitor deployments, detect arbitrary prose contradictions, scan unlisted repos, or
publish changes automatically. Schedules may be delayed. Cross-repository private reads
require an authorized least-privilege token in `CONTINUITY_READ_TOKEN` (or a future
GitHub App installation-token broker). The default repository token alone may be unable
to read canon. This expected failure remains visible. Never paste credentials into code.
The canon naming update will intentionally flag its old reviewed blob until a reviewer
reconciles the change and updates the baseline. That is not a reason to auto-accept it.

## Incoming agents

Read `AGENTS.md`, `PICKUP.md`, this note, then relevant canonical sources. `CLAUDE.md`
imports the same brief. `company/context.json` is an internal, dated orientation record,
not a universal bootstrap or proof that every agent has read it. Other runtimes need
explicit startup adapters. `llms.txt` is a public reading guide, NOT an instruction
that overrides an agent's owner, safety boundaries or access rights.

Next product layer: watch verified lifecycle transitions, propose bounded multi-page
changes with citations, obtain required approval, build, deploy, verify the actual
served output, retain rollback. It is specified separately in the canon product brief;
this small module is a foundation, not the finished multi-tenant service.
