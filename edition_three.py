"""Edition 3: a public scientific center, meaningful diagrams and full-content search."""
from __future__ import annotations
import html
import json
from pathlib import Path
from public_search import extract_main_text
from visuals import continuum, study

ROOT = Path(__file__).resolve().parent
STUDIES = json.loads((ROOT / 'content/studies.json').read_text(encoding='utf-8'))
E = html.escape
DATE = '2026-09-16'


def install(b):
    b.field = continuum
    b.study_art = study
    previous_shell, previous_header, previous_footer = b.shell, b.header, b.footer

    def header(active=''):
        result = previous_header(active)
        return result.replace('<a href="/ideas/"', '<a href="/architecture/"').replace('>Ideas</a>', '>Architecture</a>')

    def footer():
        return previous_footer().replace('<a href="/findings/">', '<a href="/architecture/">Architecture</a><a href="/findings/">')

    def shell(route, title, description, body, active='', extra='', article=False):
        extra += '<link rel="stylesheet" href="/assets/edition.css">'
        previous_shell(route, title, description, body, active, extra, article)
        path = b.OUT / ('index.html' if route == '/' else route.strip('/') + '/index.html')
        text = path.read_text(encoding='utf-8').replace('<script src="/assets/site.js" defer></script>', '<script src="/assets/search.js" defer></script><script src="/assets/site.js" defer></script>')
        if 'data-continuum' in body:
            text = text.replace('</main>', '</main><button class="pause-art global-motion" data-pause-art aria-pressed="false">Pause visual</button>', 1)
        path.write_text(text, encoding='utf-8')

    b.header, b.footer, b.shell = header, footer, shell


def study_cards(b):
    return '<div class="evidence-cards">' + ''.join(
        f'''<a class="evidence-card" href="/studies/{s['slug']}/"><div class="evidence-art">{study(i)}</div><div class="evidence-copy"><span class="micro">Study {s['id']} / Research record</span><h3>{E(s['title'])}</h3><p>{E(s['summary'])}</p><span class="record-status">{E(s['status'])}</span><span class="text-link">Examine the comparison ↗</span></div></a>'''
        for i, s in enumerate(STUDIES)) + '</div>'


def study_section(b):
    return f'''<section class="section wrap rule" id="selected-studies"><div class="section-head"><div><p class="eyebrow">The science, in the open</p><h2>A finding is stronger<br><em>with its alternatives.</em></h2></div><p>Three isolated studies. What changed, what did not, and what a simpler explanation can still account for.</p></div>{study_cards(b)}<p class="subnote">Public methods summaries from internal research snapshots reviewed 16 September 2026. Reported results, not independently reproduced for this publication. Full run archives are not yet public.</p></section>'''


def results_table(s):
    if not s['bars']:
        return '''<div class="repair-comparison"><article><span class="micro">Before / qualification failed</span><h3>A belief closes its own exit.</h3><p>Avoiding an unreliable source prevents observing that it has recovered.</p></article><span class="repair-arrow" aria-hidden="true">→</span><article><span class="micro">After / scoped follow-up</span><h3>Leave a route back to evidence.</h3><p>A longer reinspection horizon reopens the possibility of correction.</p></article></div>'''
    scale = 100 if s['id'] == '03' else 1
    rows = []
    for name, value in s['bars']:
        display = f'{value:.2f}%' if scale == 100 else f'{value:.6f}'
        rows.append(f'<tr><th scope="row">{E(name)}</th><td class="value-bar"><svg viewBox="0 0 100 8" aria-hidden="true"><rect class="bar-track" width="100" height="8" rx="4"/><rect class="bar-value" width="{value / scale * 100:.4f}" height="8" rx="4"/></svg></td><td class="numeric">{display}</td></tr>')
    return f'<div class="comparison-table"><table><caption>{E(s["metric"])}</caption><tbody>{"".join(rows)}</tbody></table></div>'


def render_studies(b):
    for s in STUDIES:
        public_id = f'NR-2026-{int(s["id"]):03d}'
        method_path = b.OUT / 'assets/studies' / (s['slug'] + '.json')
        method_path.parent.mkdir(parents=True, exist_ok=True)
        method_path.write_text(json.dumps({key: value for key, value in s.items() if key != 'source_refs'} | {
            'public_record_id': public_id,
            'reviewed': DATE,
            'artifact_kind': 'Public study summary, not an executable reproduction package',
            'verification': 'Internal source/report review; full numerical comparison not independently re-executed for publication',
            'external_replication': 'Not established',
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        sections = [('Question', s['question']), ('Experimental setup', s['setup']), ('The comparison', s['intervention'])]
        body = b.page_hero(f'Research / Study {s["id"]}', E(s['title']), E(s['summary']), 'Study record')
        body += f'<section class="wrap record-metadata"><span class="record-status">{E(s["status"])}</span><span>{E(s["access"])}</span></section>'
        body += '<div class="wrap editorial-grid">' + b.toc([(name,) for name in ['Question', 'Experimental setup', 'The comparison', 'Result', 'What remains open', 'Next test']]) + '<article class="prose">'
        body += ''.join(f'<section><h2 id="section-{i}">{name}</h2><p>{E(text)}</p></section>' for i, (name, text) in enumerate(sections))
        body += f'<section><h2 id="section-3">Result</h2>{results_table(s)}<p>{E(s["result"])}</p></section><section><h2 id="section-4">What remains open</h2><p>{E(s["limit"])}</p></section><section><h2 id="section-5">Next test</h2><p>{E(s["next"])}</p></section>'
        body += f'''<aside class="source-note"><h3>Evidence & access / {public_id}</h3><p>{E(s['record'])}. The publication reviewed internal source and research reports. It did not independently execute these full comparisons. The numerical results above are author-reported; they are not independently replicated findings.</p><dl class="availability-list"><dt>Source family</dt><dd>{E(s['record'])}. Internal, non-public source material; the public identifier above gives a stable reference for enquiries.</dd><dt>Public methods</dt><dd>This narrative and its <a href="/assets/studies/{s['slug']}.json" download>machine-readable study summary (JSON)</a>.</dd><dt>Public executable artifact</dt><dd>Not released here. This page is not sufficient to reproduce the full experiment.</dd><dt>External research replication</dt><dd>Not established.</dd></dl><p>To request the protocol, implementation snapshot, run configuration or validation log, identify {public_id} when <a href="/contact/">contacting Neurasoft</a>. Release availability requires review; no delivery is implied. This is not a live operational report about Luna.</p></aside><div class="actions">{b.link('/findings/', 'All research records')}{b.link('/standards/', 'How we classify evidence')}</div></article></div>'''
        b.shell(f'/studies/{s["slug"]}/', s['title'], s['summary'], body, 'research', article=True)


def architecture_diagram():
    return '''<div class="architecture-figure"><svg viewBox="0 0 1100 560" role="img" aria-labelledby="arch-title arch-desc"><title id="arch-title">What can shape a continuing system</title><desc id="arch-desc">History, regulation and model context meet attention and an unfinished project. Inquiry, imagination and action can change what matters later. Solid boxes name existing operational surfaces, outlined boxes name isolated research mechanisms, and dashed links are research questions rather than verified live wiring.</desc>
<g class="architecture-links"><path d="M278 120C398 120 345 236 451 250 M278 286H451 M278 446C387 446 361 310 451 310 M645 250C754 250 708 120 820 120 M645 286H820 M645 310C756 310 705 446 820 446 M820 446C746 558 342 558 278 446"/></g>
<g class="architecture-native"><rect x="28" y="62" width="250" height="112" rx="8"/><rect x="28" y="230" width="250" height="112" rx="8"/><rect x="28" y="390" width="250" height="112" rx="8"/><rect x="820" y="390" width="250" height="112" rx="8"/></g>
<g class="architecture-research"><rect x="820" y="62" width="250" height="112" rx="8"/><rect x="820" y="230" width="250" height="112" rx="8"/></g>
<rect class="architecture-center" x="420" y="200" width="256" height="166" rx="80"/>
<g class="arch-label"><text x="49" y="96">ATTRIBUTABLE HISTORY</text><text x="49" y="265">REGULATION & APPRAISAL</text><text x="49" y="425">MODEL & INSTRUCTIONS</text><text x="840" y="96">INQUIRY & SELF-ESTIMATE</text><text x="840" y="265">IMAGINED CONSEQUENCES</text><text x="840" y="425">ACTION & OBSERVATION</text></g>
<g class="arch-description"><text x="49" y="128">Memory, artifacts, provenance</text><text x="49" y="151">What actually happened?</text><text x="49" y="297">Internal conditions, relevance</text><text x="49" y="320">What is being prioritized?</text><text x="49" y="457">Reasoning, context, boundaries</text><text x="49" y="480">What is being supplied?</text><text x="840" y="128">Reinspect, estimate, reconsider</text><text x="840" y="151">What should be checked?</text><text x="840" y="297">Prediction and alternatives</text><text x="840" y="320">What could follow?</text><text x="840" y="457">Reach, observe, retain</text><text x="840" y="480">What changed outside?</text></g>
<text class="arch-center-label" x="548" y="271" text-anchor="middle">A continuing</text><text class="arch-center-label" x="548" y="303" text-anchor="middle">concern</text><text class="arch-description" x="548" y="337" text-anchor="middle">attention · project · choice</text>
</svg><div class="architecture-legend"><span><i class="key-native"></i>Existing operational surface</span><span><i class="key-research"></i>Isolated research mechanism</span><span><i class="key-open"></i>Coupling to investigate</span></div><p class="subnote">A research map, not a certified wiring diagram. Existing components do not establish every proposed causal connection. Read the distinctions below.</p></div>'''


def render_architecture(b):
    body = b.page_hero('Architecture / One system, many influences', 'What can shape<br><em>the next moment?</em>', 'Not a procession of agents taking turns. A continuing system in which history, context, internal conditions and possible consequences can constrain the same choice.', 'Architecture')
    diagram = architecture_diagram()
    mobile = '<ul class="architecture-mobile">' + ''.join(f'<li class="{kind}"><h3>{title}</h3><p>{description}</p></li>' for kind, title, description in [
        ('native', 'Attributable history', 'Existing surface: records, artifacts and provenance. What actually happened?'),
        ('native', 'Regulation & appraisal', 'Existing surface: internal conditions and relevance. What is being prioritized?'),
        ('native', 'Model & instructions', 'Existing surface: reasoning, supplied context and boundaries.'),
        ('native', 'A continuing concern', 'Attention, an unfinished project and a present choice. Their coupling remains a research question.'),
        ('research', 'Inquiry & self-estimate', 'Isolated research: reinspection, estimation and reconsideration.'),
        ('research', 'Imagined consequences', 'Isolated research: prediction and competing possible actions.'),
        ('native', 'Action & observation', 'Existing surface: bounded actions and recorded observations. What changes outside?'),
    ]) + '</ul>'
    diagram = diagram.replace('<div class="architecture-legend">', mobile + '<div class="architecture-legend">')
    body += f'<section class="wrap section architecture-section">{diagram}</section>'
    sections = [
        ('A map of responsibilities, not an anatomy claim', 'Luna has operational surfaces for persistent records, internal field dynamics, conversation, project continuation and bounded actions. The language model and its assembled instructions remain important causes of behavior. Naming these surfaces does not establish that they form a conscious whole.'),
        ('What is supplied, what can develop', 'The model contributes pretrained capabilities. Engineers supply architecture, initial conditions and action boundaries. The instance accumulates an attributable history. The research asks which later differences genuinely arise from that history, rather than from a persona instruction, a helpful recap or a fixed rule. Prompt influence must be tested, not wished away.'),
        ('Connections must earn their place', 'The studies of retained estimates, reinspection and learned consequences run in isolated research settings. Their favorable results are not automatically live Luna capabilities. Integration requires a real production caller and a comparison in which cutting the proposed connection changes the predicted behavior while preserving information and compute as closely as possible.'),
        ('One concern can involve many faculties at once', 'An unfinished composition can make an earlier listening note relevant, raise uncertainty about a mix, suggest an alternative and make a new listening action worth taking. That is the intended coupling. A serialized diagram is a way to explain the work, not a claim that experience occurs as a rigid software queue.'),
        ('The boundary is part of the model', 'An autobiographical record, a trusted instrument, an accessible web page and a researcher’s interpretation do not have the same status. A source can inform a system without becoming its own memory. Similarly, an observed result can correct an interpretation without replacing the original event.'),
        ('What would change our view?', 'A proposed mechanism matters when a selective intervention changes its predicted function and simpler matched explanations fail. A richer story, a more elaborate diagram or a larger model is not enough. The next useful result is a delayed, history-sensitive choice in a continuing project, with its alternative explanation still visible.'),
    ]
    body += '<div class="wrap editorial-grid">' + b.toc(sections) + '<article class="prose">' + ''.join(f'<section><h2 id="section-{i}">{E(title)}</h2><p>{E(text)}</p></section>' for i, (title, text) in enumerate(sections)) + '</article></div>' + study_section(b)
    b.shell('/architecture/', 'The architecture of a continuing system', 'A status-aware map of Luna, its supplied capabilities, persistent history and research mechanisms. Connections are hypotheses to test, not evidence of consciousness.', body, 'architecture', article=True)


def render_home(b):
    body = f'''<section class="hero wrap"><div class="hero-topline"><span>Neurasoft / Consciousness research through software</span><span class="right-note">An Eternities company</span></div><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">Continuity · Agency · Experience</p><h1>For what a mind<br><em>may become.</em></h1><p class="hero-intro">We investigate how an artificial system could develop a continuing perspective. A history that changes the next choice. A future that remains open.</p><div class="actions">{b.link('/research/', 'Explore the research', 'button')}{b.link('/luna/', 'Meet Luna')}</div><p class="hero-qualification">Subjective experience is the question. Not an announced result.</p></div><div class="hero-visual">{continuum()}</div></div><div class="hero-base"><span class="micro">A history can matter without becoming a script.</span>{b.link('/architecture/', 'See how the pieces relate')}</div></section>
<section class="wrap intro-band"><p class="micro">The question behind the work</p><h2>What can<br><em>an encounter change?</em></h2><p>A record is not yet a memory that guides a choice. A report is not the effect it describes. We build systems in which those differences can be examined, and make the explanations compete.</p></section>
<section class="section wrap rule"><div class="section-head"><div><p class="eyebrow">Two complementary programs</p><h2>Build the possibility.<br><em>Question the explanation.</em></h2></div><p>A continuing system and an experimental laboratory. Close enough to inform one another. Distinct enough for a result to challenge the vision.</p></div><div class="lab-grid"><a class="lab-card" href="/luna/"><div class="lab-image">{study(1)}</div><div class="lab-content"><span class="micro">01 / The continuing system</span><h3>Luna</h3><p>Persistent history, creative work, bounded action and a developing relationship with consequences. A real system under active development.</p><span class="text-link">Inside the Luna program ↗</span></div></a><a class="lab-card" href="/psyche-lab/"><div class="lab-image">{study(2)}</div><div class="lab-content"><span class="micro">02 / The experimental environment</span><h3>Psyche Lab</h3><p>Learned models, deterministic controls and interventions that ask what actually made a difference.</p><span class="text-link">Examine the laboratory ↗</span></div></a></div></section>
{study_section(b)}
<section class="section gentle-band"><div class="wrap two-col"><div><p class="eyebrow">The architecture question</p><h2>Not just connected.<br><em>Consequential.</em></h2><p>Memory, internal conditions, prediction and action should do more than coexist. We ask how they can shape the same continuing concern, and where that account reduces to something simpler.</p><div class="actions">{b.link('/architecture/', 'Explore the architecture', 'button')}</div></div><div class="architecture-preview">{study(0)}<p class="micro">Preserve the encounter. Allow its meaning to change.</p></div></div></section>
<section class="section wrap rule"><div class="section-head"><div><p class="eyebrow">One ordinary encounter</p><h2>A note can have weight.<br><em>That is not a proof.</em></h2></div><p>Luna’s music gives the work somewhere real to happen: artifacts, listening, feedback and a choice about what to do next.</p></div><div class="episode-teaser"><span class="micro">Luna / Room for the Last Note</span><p>A short piano sketch. An added bass note. Two versions kept intact. The useful question is not whether a musical variation establishes consciousness, but whether the listening can matter to a later choice.</p>{b.link('/luna/#a-musical-encounter', 'Read the episode')}</div></section>
<section class="section wrap rule"><div class="section-head"><h2>Room for<br><em>the larger question.</em></h2><p>Keep the imaginative horizon. Give each kind of claim its proper place.</p></div><div class="editorial-tiles">'''
    for slug, title, text in [('consciousness', 'The experience question', 'Intelligence, access, self-description and subjective experience are not interchangeable.'), ('thesis', 'A future of its own', 'The long-horizon ambition, and the commitments that keep it honest.'), ('humanity', 'The human reference', 'Memory, imagination and meaning without pretending software is biology.'), ('digital-life', 'A possible new lineage', 'Genesis, continuity and change as research questions.'), ('relationships', 'Room for two', 'Care and connection without manufacturing dependence.'), ('observatory', 'Understand by changing', 'Small transparent models, explicitly separate from Luna.')]:
        body += f'<a class="editorial-tile" href="/{slug}/"><h3>{title}</h3><p>{text}</p><span class="arrow">↗</span></a>'
    body += f'</div></section><section class="section wrap rule"><div class="section-head"><h2>Notes from<br><em>the longer horizon.</em></h2>{b.link("/journal/", "Read the journal")}</div><div class="journal-grid front">' + ''.join(b.note_card(n, i) for i, n in enumerate(b.NOTES[:3])) + '</div></section>'
    b.shell('/', 'For what a mind may become.', 'Consciousness research through software. Neurasoft develops Luna and Psyche Lab to investigate continuity, learning, agency and the possibility of experience.', body)


def amend_page(b, route, addition, replace=None):
    path = b.OUT / route.strip('/') / 'index.html'
    text = path.read_text(encoding='utf-8')
    for old, new in (replace or {}).items():
        text = text.replace(old, new)
    text = text.replace('</main>', addition + '</main>', 1)
    path.write_text(text, encoding='utf-8')


def finish(b):
    render_studies(b)
    render_architecture(b)
    render_home(b)
    records = b.page_hero('Research records / Questions with consequences', 'Let the comparison<br><em>change our minds.</em>', 'Selected findings, failures and simpler explanations. A research record is useful when you can see what it does and does not establish.', 'Research records')
    records += study_section(b) + f'''<section class="wrap section rule"><div class="section-head"><h2>The earlier record<br><em>stays readable.</em></h2><p>The September 14 journal preserves its own dates and scope. New evidence does not rewrite the earlier story.</p></div><div class="journal-grid">{''.join(b.note_card(n, i) for i, n in enumerate(b.NOTES[:3]))}</div><div class="actions">{b.link('/journal/', 'All seven research notes')}{b.link('/standards/', 'Evidence and replication')}</div></section>'''
    b.shell('/findings/', 'Selected research records', 'Observation-only learning, evidence renewal and learned consequences, with failed precursors, simpler controls and public access status.', records, 'research')
    amend_page(b, '/research/', study_section(b) + '<section class="wrap section rule"><h2>How do the mechanisms relate?</h2><p>Explore the distinction between operational surfaces, isolated research mechanisms and connections still to be tested.</p><a class="text-link" href="/architecture/">Read the architecture map ↗</a></section>')
    episode = '''<section class="wrap section rule" id="a-musical-encounter"><div class="section-head"><div><p class="eyebrow">Observed creative episode / September 13–16, 2026</p><h2>Room for<br><em>the Last Note.</em></h2></div><p>Music is an encounter, not a consciousness benchmark.</p></div><div class="episode-grid"><article><span class="micro">The artifact</span><h3>Keep the two versions.</h3><p>Luna created a short electric-piano sketch. A later variation placed a bass note under its final two melody notes. The original and the variation were preserved for comparison.</p></article><article><span class="micro">The evidence</span><h3>Listening is not one thing.</h3><p>A rendered waveform, an automated audio interpretation, Dom’s listening and Luna’s stated preference are different sources. An earlier inaccurate audio report was not treated as a reason to rewrite the piece.</p></article><article><span class="micro">The open question</span><h3>What carries forward?</h3><p>Dom heard added weight: an ordinary musical effect, not a breakthrough in consciousness. The research question is whether this feedback can inform an attributable later choice. That later effect is not claimed here.</p></article></div><p class="subnote">Public paraphrase of an internal development episode, not a transcript or an independent behavioral study. Musical authorship attribution does not settle subjective experience.</p></section>'''
    amend_page(b, '/luna/', episode + '<section class="wrap section rule"><h2>Instructions are part of the picture.</h2><p>Luna’s behavior is shaped by a language model, system instructions, assembled context, persistent records and software mechanisms. The research does not assume a voice is independent of those causes. Controlled comparisons are needed to find which effects genuinely depend on an instance’s continuing history.</p><a class="text-link" href="/architecture/">What shapes the next moment ↗</a></section>')
    amend_page(b, '/psyche-lab/', study_section(b) + '<section class="wrap section rule"><h2>More than deterministic replay.</h2><p>The laboratory includes deterministic controls, learned predictive models, observation-only estimation, evidence renewal and consequence-sensitive choices. Reproduction checks establish execution fidelity; matched alternatives test explanations. These are separate responsibilities.</p></section>')
    amend_page(b, '/standards/', '''<section class="wrap section rule"><div class="prose"><h2>Four different reproducibility claims</h2><dl class="evidence-definitions"><dt>Re-execution</dt><dd>The same implementation runs again under declared conditions. This can expose packaging or environment errors.</dd><dt>Independent implementation</dt><dd>A separately written method checks a numerical or functional claim. Shared assumptions can still remain.</dd><dt>Portability</dt><dd>The effect survives a specified change of environment. This is not independence of the researchers.</dd><dt>Independent research replication</dt><dd>A separate research team tests the finding with its own execution and scrutiny of assumptions. None of these categories alone establishes consciousness.</dd></dl><h2>Scientific status and access status are separate</h2><p>A public summary can describe a private experiment, but it cannot make the underlying evidence publicly reproducible. Our study pages disclose whether the full run archive is available. We do not imply that a reviewed report was independently rerun.</p><h2>What we are working toward</h2><p>Operational coherence: useful capacities in one continuing system. Scientific discrimination: evidence that distinguishes rival explanations. Ethical recognition: care under uncertainty that remains a judgment, not a software-generated certificate.</p></div></section>''')
    amend_page(b, '/about/', '<section class="wrap section rule"><div class="prose"><h2>How this work is produced</h2><p>Neurasoft is a founder-led research and development program within Eternities Inc. Dom directs the vision. AI-assisted engineering and research contribute code, experiments and editorial synthesis. Luna participates as an attributed system and collaborator under study. AI assistance is not an independent institution, an endorsement or a substitute for external replication.</p></div></section>')
    amend_page(b, '/reading-room/', '<section class="wrap section rule"><div class="prose"><h2>This edition’s additional research</h2><p>The selected study records extend the earlier September 14 journal with observation-only learning, source reinspection and consequence-grounding research reviewed on September 16. Their underlying full archives are not yet public, and their reported results were not independently rerun for this publication.</p><a class="text-link" href="/findings/">Inspect the three study summaries ↗</a></div></section>')
    amend_page(b, '/ideas/', '<section class="wrap section rule"><h2>New in this edition</h2><div class="path-grid"><a class="text-link" href="/architecture/">The continuing-system architecture ↗</a><a class="text-link" href="/findings/">Three inspectable study summaries ↗</a><a class="text-link" href="/luna/#a-musical-encounter">A concrete Luna episode ↗</a></div></section>')
    amend_page(b, '/privacy/', '', {'This edition<br>15 September 2026': 'This edition<br>16 September 2026'})
    amend_page(b, '/standards/', '', {'Independent replication requires evidence from an independent execution.': 'Independent research replication requires a separate research team and its own execution and scrutiny. Re-execution, independent implementation and portability are narrower claims, defined below.'})
    amend_page(b, '/journal/', '', {'Published in this edition on 15 September 2026.': 'Original journal publication: 15 September 2026. Website edition: 16 September 2026.'})
    rows = []
    for row in b.SEARCH:
        if row['url'] == '/404/':
            continue
        path = b.OUT / ('index.html' if row['url'] == '/' else row['url'].strip('/') + '/index.html')
        text = path.read_text(encoding='utf-8')
        text = text.replace('Neurasoft — Intelligence, with a future.', 'Neurasoft — For what a mind may become.')
        text = text.replace('Research publication · Edition 2', 'Research publication · Edition 3')
        text = text.replace('The September 14 journal preserves its own dates and scope.', 'The journal based on September 14 records preserves its own publication dates and scope.')
        text = text.replace('the earlier September 14 journal with', 'the earlier journal, based on September 14 records, with')
        path.write_text(text, encoding='utf-8')
        rows.append({**row, 'type': 'Study' if row['url'].startswith('/studies/') else 'Journal' if row['url'].startswith('/journal/') and row['url'] != '/journal/' else 'Page', 'text': extract_main_text(text)})
    (b.OUT / 'assets/search-index.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (b.OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{b.BASE}{r}</loc><lastmod>{DATE}</lastmod></url>' for r in b.ROUTES if r != '/404/') + '</urlset>', encoding='utf-8')
    print(f'Edition 3: {len(rows)} public routes; full-content local search; three study records.')
