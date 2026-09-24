# Neurasoft daily dispatches

Owner: Dom. Authorized September 24, 2026: make one illustrated article daily,
publish on neurasoft.us with a fresh homepage entry, and prepare it for Grok Bot
to publish on X and LinkedIn. This is a separate lane from Resident engineering.

## Voice and editorial scope

Lead with something a curious stranger can recognize, then give them a question,
example or insight worth sharing. Warm, lucid, intellectually adventurous. About
800–1,400 words when the subject earns it; a shorter substantive piece is fine.
Prefer a sharp argument over technical specifications, slogans or hype. Topics
can range across AI, minds, memory, agency, creativity, technology and daily life.
Vary the subject and format. Do not repackage yesterday's essay each day.

Ground changing facts in current primary sources. Keep sources near claims and
link a short reading list. Separate observed results, hypotheses, analogies and
founder ambitions. Never announce consciousness, fabricated experiments or
unmeasured performance. Public research pages and approved public material can
inform articles; private transcripts, unpublished lab details, source code,
personal data and credentials cannot be copied into them.

Create a distinctive original 1200×630 cover and one or two useful visual
explainers. Code/SVG is suitable for diagrams; image generation is suitable for
illustration. Use actual cited data for quantitative charts, or label a conceptual
diagram clearly. Never disguise invented numbers as results. Match the site's
ivory/sage visual identity without reusing the same diagram regardless of topic.
Provide meaningful alt text, captions, SVG and social-ready PNG. Inspect rendered
desktop and phone versions. Disclose AI-assisted editorial authorship accurately.

## Source and build

Canonical repo: xnuonux/neurasoft. Working lane:
`C:/dev/.worktrees/neurasoft-daily` on `editorial/daily-dispatch-20260924`.
Before each run fetch, check clean state/ownership and inspect the last article,
publication receipts and open changes. Do not deploy stale branch snapshots over
newer production content. The unrelated draft PR1 is not part of this lane.

Add `content/articles/YYYY-MM-DD-slug.json`, following the first article's schema,
and media under `assets/articles/<slug>/`. `status: publish` explicitly includes
an article; future-dated entries and drafts stay out of public output. `articles.py`
runs after the historical publication layers, generates `/articles/`, every
article, RSS, searchable content and a newest-first homepage feature. Original
research notes keep their dates and scope. No frontend runtime dependency added.

Build and stage:

```
python build.py
python -m unittest discover -s tests -p test_articles.py
python -m unittest discover -s tests -p test_site.py
python -m unittest discover -s tests -p test_edition.py
python -m unittest discover -s tests -p test_public_search.py
node --test tests/search.test.cjs
python tools/stage_cloudflare.py
```

Run `tools/check_editorial_browser.cjs` with an installed Playwright module
(set NEURASOFT_PLAYWRIGHT_MODULE if not installed in this checkout). It uses a
local server at 127.0.0.1:8742 by default and checks the newest built article. The old standalone
portable-preview Python browser script needs a different environment and is not
part of these checks. Do not claim it ran.

Commit and push scoped changes. Publish only `artifacts/cloudflare/` using the
already authenticated Wrangler and existing Pages project `neurasoft-research`.
Preview on a non-main deployment branch; verify before production `--branch main`.
Preserve unrelated edits and open PRs. Record exact source commit, deployment
URL/id, article URL, dates and checks in `docs/editorial-releases/`. A successful
build or preview is not proof that the public domain updated. Verify both.

## Grok Bot handoff

Public discovery endpoint: https://neurasoft.us/articles/inbox.json

Each entry links to its `grok-packet.json`: title, stable date/slug id, canonical
URL, full original Markdown URL, ordered PNG image URLs, alt text/captions, X
short post and LinkedIn adaptation. No secret or private material is in this
public handoff. RSS at https://neurasoft.us/articles/feed.xml is also available.

Dom's screenshot shows a GB `x-articles/inbox/` workflow and a webhook, but its
actual filesystem/repo/webhook endpoint has **not** been provided or verified.
Until connected, public availability and a local zip mean packet prepared, not
GB delivery or social publication. Do not guess webhook URLs or post to an
unidentified account. Once Dom supplies the endpoint, read its README/contract,
deliver once per packet id, and record acknowledgment separately from post URLs.
GB can alternatively poll the public inbox after 09:30 America/Chicago daily.

The packet authorizes publication (`publish: auto`) under Dom's explicit request.
GB should check its account queue for the packet id/canonical URL, publish a native
X Article if available, otherwise use the short post + link, and use the LinkedIn
adaptation with cover and link. Keep sources and figure labels. Record actual
post URLs. Never claim a post exists merely because a packet was accepted.

## Daily run and idempotency

Target 09:00 America/Chicago, every day. This is a local Codex heartbeat, so an
available local host/app is required; it is not an always-on hosted scheduler.
One article per local calendar day. Inspect committed registry, published inbox
and release receipts first; if today's article exists, repair an incomplete
publish/handoff instead of creating a duplicate. Do not retry an uncertain
social submission until status is checked. A research/factual gap can result in
a truthful shorter essay, never invented evidence. No cloud rental, provider
campaign or new paid service is authorized by this routine.

An automated daily article is not guaranteed audience growth. Track actual
impressions, saves, thoughtful replies and click-through only when GB returns
those metrics; do not report likes or popularity without data.
