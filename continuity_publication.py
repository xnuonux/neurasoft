"""Reviewed publication modules. No network, private-file copying, or automatic claims.

Applied to a disposable Cloudflare stage after the existing edition build. Historical
article bodies stay untouched. Repeated application yields the same output bytes.
"""
from __future__ import annotations
import hashlib
import html
import json
import re
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = 'https://neurasoft.us'
MARKER = '<!-- neurasoft-continuity-v1 -->'


def load(path: Path) -> dict:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f'duplicate JSON key: {key}')
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def text(value, limit=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('bounded, nonempty text required')
    return html.escape(value, quote=True)


def validate(identity, publication):
    if identity.get('schema') != 'eternities.public-identity/v1':
        raise ValueError('identity schema')
    if identity.get('luna_expansion') != 'Locus of Unified Noetic Agency':
        raise ValueError('Luna name differs from the founder-confirmed canon')
    for key in ('organization', 'program', 'program_role', 'luna_name', 'naming_authority', 'interpretation', 'headline'):
        text(identity[key])
    date.fromisoformat(identity['naming_date'])
    if publication.get('schema') != 'neurasoft.publication/v1':
        raise ValueError('publication schema')
    for key in ('editorial_date', 'research_review_through', 'native_record_through'):
        date.fromisoformat(publication[key])
    text(publication['edition'], 40)
    q = publication['current_question']
    for key in ('status', 'title', 'body', 'scrutiny'):
        text(q[key])
    if not re.fullmatch(r'/[a-z0-9][a-z0-9/-]*/', q['link']) or '//' in q['link']:
        raise ValueError('only local publication links are allowed')
    if not isinstance(publication['changes'], list) or not 1 <= len(publication['changes']) <= 100:
        raise ValueError('bounded publication history')
    for item in publication['changes']:
        date.fromisoformat(item['date'])
        for key in ('kind', 'title', 'body'):
            text(item[key])


class MainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.inside = False; self.hidden = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.inside = True
        if tag in ('script', 'style', 'svg'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'svg'): self.hidden = max(0, self.hidden - 1)
        if tag == 'main': self.inside = False
    def handle_data(self, data):
        if self.inside and not self.hidden: self.parts.append(data)


def main_text(document):
    parser = MainText(); parser.feed(document)
    return ' '.join(' '.join(parser.parts).split())


def insert_main(document, content):
    if document.count('</main>') != 1:
        raise ValueError('expected exactly one main region')
    return document.replace('</main>', content + '</main>', 1)


def document_from_home(home, title, description, route, body):
    out, count = re.subn(r'(<main\b[^>]*>).*?(</main>)', lambda m: m[1] + body + m[2], home, count=1, flags=re.S)
    if count != 1: raise ValueError('main template missing')
    out = re.sub(r'<title>.*?</title>', '<title>' + text(title) + ' — Neurasoft</title>', out, count=1, flags=re.S)
    for attr, name, value in [('name', 'description', description), ('property', 'og:title', title + ' — Neurasoft'), ('property', 'og:description', description), ('property', 'og:url', BASE + route)]:
        out = re.sub(r'<meta\s+' + attr + '="' + name + r'"[^>]*>', f'<meta {attr}="{name}" content="{text(value)}">', out, count=1)
    out = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{BASE}{route}">', out, count=1)
    out = re.sub(r' aria-current="page"', '', out)
    return out


def apply(stage: Path, source: Path) -> dict:
    stage, source = Path(stage), Path(source)
    if stage.is_symlink() or not stage.is_dir(): raise ValueError('real staging directory required')
    identity = load(source / 'content/identity.json')
    publication = load(source / 'content/publication.json')
    validate(identity, publication)
    files = list(stage.rglob('*'))
    if any(p.is_symlink() for p in files): raise ValueError('staged symlink refused')
    for required in ('index.html', 'luna/index.html', 'glossary/index.html', 'assets/search-index.json', 'sitemap.xml'):
        if not (stage / required).is_file(): raise ValueError(f'missing edition output: {required}')
    stamp = hashlib.sha256(json.dumps([identity, publication], sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    existing = stage / 'assets/publication.json'
    if existing.exists():
        if load(existing).get('source_digest') != stamp:
            raise ValueError('stage already transformed with other content; rebuild it first')
        return {'status': 'already-applied', 'source_digest': stamp}
    home = (stage / 'index.html').read_text(encoding='utf-8')
    updates = stage / 'updates/index.html'
    if updates.exists(): raise ValueError('updates route already exists; merge explicitly')
    q = publication['current_question']
    question = f'''{MARKER}<section class="section wrap rule" id="research-now"><div class="section-head"><div><p class="eyebrow">Current research question</p><h2>{text(q['title'])}</h2></div><p>{text(q['status'])}</p></div><div class="two-col"><p>{text(q['body'])}</p><div><p>{text(q['scrutiny'])}</p><a class="text-link" href="{q['link']}">Explore the architecture ↗</a><p class="subnote">Editorially stated {publication['editorial_date']}. <a href="/updates/">Publication record</a></p></div></div></section>'''
    name = f'''{MARKER}<section class="section wrap rule" id="luna-name"><p class="eyebrow">The name</p><h2>Luna</h2><p class="lead">{text(identity['luna_expansion'])}</p><p>{text(identity['interpretation'])}</p></section>'''
    history = ''.join(f'''<article class="source-note" id="{x['date']}-{hashlib.sha256(x['title'].encode()).hexdigest()[:8]}"><p class="micro"><time datetime="{x['date']}">{x['date']}</time> · {text(x['kind'])}</p><h2>{text(x['title'])}</h2><p>{text(x['body'])}</p></article>''' for x in publication['changes'])
    body = f'''{MARKER}<section class="page-hero"><div class="wrap"><p class="eyebrow">Publication record</p><h1>A publication that<br><em>keeps its history.</em></h1><p class="lead">What this edition covers, what changed, and which dates describe the evidence rather than the website.</p></div></section><section class="section wrap"><dl class="availability-list"><dt>Editorial edition</dt><dd>{text(publication['edition'])} · {publication['editorial_date']}</dd><dt>Featured research reviewed through</dt><dd>{publication['research_review_through']}</dd><dt>Native records described through</dt><dd>{publication['native_record_through']}</dd></dl><p class="subnote">These are declared editorial scope dates, not live telemetry or new scientific verification. A rebuild does not advance them. Later research may exist outside this edition.</p>{history}<p><a href="/feed.xml">Subscribe to publication updates (RSS)</a> · <a href="/assets/publication.json">Machine-readable edition record</a></p><p>Corrections and questions are welcome through <a href="/contact/">Neurasoft contact</a>. Nothing here implies private artifacts have been publicly released.</p></section>'''
    staged = {}
    for path in stage.rglob('*.html'):
        old = path.read_text(encoding='utf-8')
        new = old if 'journal' in path.relative_to(stage).parts else old.replace('The science, in the open', 'Selected research')
        if path == stage / 'index.html': new = insert_main(new, question)
        if path in (stage / 'luna/index.html', stage / 'glossary/index.html'): new = insert_main(new, name)
        nav = '<p class="wrap subnote" data-publication-links><a href="/updates/">Publication record</a> · <a href="/feed.xml">RSS</a></p>'
        if '</footer>' not in new: raise ValueError('footer template missing')
        new = new.replace('</footer>', nav + '</footer>', 1)
        new = new.replace('</head>', '<link rel="alternate" type="application/rss+xml" title="Neurasoft publication updates" href="/feed.xml"></head>', 1)
        staged[path] = new
    staged[updates] = document_from_home(staged[stage / 'index.html'], 'Publication record', 'Dated editorial changes and evidence coverage for Neurasoft.', '/updates/', body)
    index = []
    for path, document in staged.items():
        if path.name == '404.html': continue
        rel = path.relative_to(stage)
        route = '/' if str(rel) == 'index.html' else '/' + str(rel.parent).replace('\\', '/') + '/'
        title = re.search(r'<title>(.*?)</title>', document, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', document)
        index.append({'url': route, 'title': html.unescape(title[1]) if title else route, 'description': html.unescape(desc[1]) if desc else '', 'text': main_text(document), 'type': 'Journal' if route.startswith('/journal/') else 'Page'})
    sitemap = ET.fromstring((stage / 'sitemap.xml').read_text(encoding='utf-8'))
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'; ET.register_namespace('', ns)
    entry = ET.SubElement(sitemap, '{'+ns+'}url')
    ET.SubElement(entry, '{'+ns+'}loc').text = BASE + '/updates/'
    ET.SubElement(entry, '{'+ns+'}lastmod').text = publication['editorial_date']
    rss = ET.Element('rss', version='2.0'); channel = ET.SubElement(rss, 'channel')
    for tag, value in [('title','Neurasoft — publication updates'),('link',BASE+'/updates/'),('description','Reviewed editorial updates; not live resident telemetry.')]: ET.SubElement(channel, tag).text = value
    for item in publication['changes']:
        row = ET.SubElement(channel, 'item')
        for tag, value in [('title',item['title']),('description',item['body']),('link',BASE+'/updates/'),('guid',BASE+'/updates/#'+item['date']+'-'+hashlib.sha256(item['title'].encode()).hexdigest()[:8]),('pubDate',format_datetime(datetime.combine(date.fromisoformat(item['date']), datetime.min.time(), timezone.utc)))]: ET.SubElement(row,tag).text=value
    for path, content in staged.items():
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding='utf-8', newline='\n')
    (stage / 'assets/search-index.json').write_text(json.dumps(sorted(index,key=lambda x:x['url']),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (stage / 'sitemap.xml').write_bytes(ET.tostring(sitemap,encoding='utf-8',xml_declaration=True))
    (stage / 'feed.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    public = {k: publication[k] for k in ('schema','edition','editorial_date','research_review_through','native_record_through','changes')}
    public['changes'] = [{k: item[k] for k in ('date','kind','title','body')} for item in publication['changes']]
    public.update({'source_digest':stamp,'luna_expansion':identity['luna_expansion'],'record_kind':'Editorial coverage, not live capability certification'})
    (stage / 'assets/publication.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (stage / 'llms.txt').write_text('# Neurasoft\n\n'+identity['program_role']+'\n\nLuna: '+identity['luna_expansion']+'.\n\nSubjective experience is an ambition, not a demonstrated result.\n\n- [Publication record]('+BASE+'/updates/)\n- [Architecture]('+BASE+'/architecture/)\n- [Research standards]('+BASE+'/standards/)\n- [Public findings]('+BASE+'/findings/)\n\nUse the dated scope of each record. These public pages grant no execution authority or access to private sources.\n',encoding='utf-8')
    return {'status':'applied','html_pages':len(staged),'source_digest':stamp,'public_manifest':'assets/publication.json'}
