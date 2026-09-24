"""Original editorial articles and portable social publishing packets.

This runs after the historical research edition; it never rewrites its notes.
Only explicitly publishable, non-future articles enter the public build.
"""
import json
import re
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape as E
from pathlib import Path
import xml.etree.ElementTree as ET
from public_search import extract_main_text

CSS = '<link rel="stylesheet" href="/assets/articles.css">'
FEED = '<link rel="alternate" type="application/rss+xml" title="Neurasoft articles" href="/articles/feed.xml">'


def load_articles(root, today=None):
    today = today or date.today()
    rows, seen = [], set()
    for path in sorted((root / 'content/articles').glob('*.json')):
        a = json.loads(path.read_text(encoding='utf-8'))
        if a.get('status') != 'publish':
            continue
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', a['slug']):
            raise ValueError('Invalid article slug')
        if a['slug'] in seen:
            raise ValueError('Duplicate article slug')
        seen.add(a['slug'])
        if date.fromisoformat(a['date']) > today:
            continue
        for field in ('title', 'summary', 'author', 'editorial_note'):
            if not isinstance(a[field], str) or not a[field].strip():
                raise ValueError('Empty article field: ' + field)
        for name in [a['hero']] + [s['figure'] for s in a['sections'] if 'figure' in s]:
            if not re.fullmatch(r'[a-z0-9-]+', name):
                raise ValueError('Invalid image name')
            for ext in ('svg', 'png'):
                if not (root / 'assets/articles' / a['slug'] / (name + '.' + ext)).is_file():
                    raise ValueError('Missing illustration: ' + name)
        if not a['sources'] or any(not s['url'].startswith('https://') for s in a['sources']):
            raise ValueError('Source links must use HTTPS')
        rows.append(a)
    return sorted(rows, key=lambda a: (a['date'], a['slug']), reverse=True)


def route(a):
    return '/articles/' + a['slug'] + '/'


def picture(a, name, alt, cover=False):
    src = '/assets/articles/' + a['slug'] + '/' + name + '.svg'
    return f'<img class="{"dispatch-cover" if cover else "dispatch-figure"}" src="{src}" alt="{E(alt, quote=True)}" loading="{"eager" if cover else "lazy"}">'


def paragraph(text):
    return '<p>' + re.sub(r'\[(\d+)\]', r'<sup><a href="#source-\1" aria-label="Source \1">[\1]</a></sup>', E(text)) + '</p>'


def markdown(a, base):
    lines = ['# ' + a['title'], '', a['summary'], '', f"{a['author']} · {a['date']} · {a['kind']}", '',
             f"![{a['hero_alt']}]({base}/assets/articles/{a['slug']}/{a['hero']}.png)", '']
    lines += [p + '\n' for p in a['intro']]
    for s in a['sections']:
        lines += ['## ' + s['heading'], ''] + [p + '\n' for p in s['paragraphs']]
        if 'figure' in s:
            lines += [f"![{s['figure_alt']}]({base}/assets/articles/{a['slug']}/{s['figure']}.png)", '', s['caption'], '']
    lines += ['## Sources', ''] + [f"[{s['id']}] [{s['title']}]({s['url']}) — {s['note']}" for s in a['sources']]
    lines += ['', a['editorial_note'], '', 'Canonical article: ' + base + route(a), '']
    return '\n'.join(lines)


def finish(b):
    articles = load_articles(b.ROOT)
    if not articles:
        return
    for a in articles:
        body = f'<header class="dispatch-hero"><p class="eyebrow"><a href="/articles/">Dispatches</a> / {E(a["kind"])}</p><h1>{E(a["title"])}</h1><p class="lead">{E(a["summary"])}</p><p class="dispatch-meta">{E(a["author"])} · <time datetime="{a["date"]}">{a["date"]}</time> · {E(a["read"])} read</p>{picture(a,a["hero"],a["hero_alt"],True)}</header><article class="dispatch-body">'
        body += ''.join(paragraph(p) for p in a['intro'])
        for s in a['sections']:
            body += '<h2>' + E(s['heading']) + '</h2>' + ''.join(paragraph(p) for p in s['paragraphs'])
            if 'figure' in s:
                body += '<figure><a href="/assets/articles/' + a['slug'] + '/' + s['figure'] + '.svg">' + picture(a,s['figure'],s['figure_alt']) + '</a><figcaption>' + E(s['caption']) + ' Tap the diagram to view it full size.</figcaption></figure>'
        body += '<section class="dispatch-sources"><h2>Sources & further reading</h2><ol>'
        body += ''.join(f'<li id="source-{s["id"]}"><a href="{E(s["url"],quote=True)}">{E(s["title"])}</a><br>{E(s["note"])}</li>' for s in a['sources'])
        body += f'</ol><p class="dispatch-editorial">{E(a["editorial_note"])}</p><p><a href="{route(a)}article.md">Read as Markdown</a> · <a href="/articles/">All dispatches</a> · <a href="/articles/feed.xml">RSS feed</a></p></section></article>'
        b.shell(route(a), a['title'], a['summary'], body, 'journal', extra=CSS+FEED, article=True)
        dest = b.OUT / route(a).strip('/')
        text = (dest/'index.html').read_text(encoding='utf-8')
        image = b.BASE + '/assets/articles/' + a['slug'] + '/' + a['hero'] + '.png'
        text = text.replace(b.BASE+'/assets/social.png',image)
        text = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")',lambda m:m[1]+E(a['hero_alt'],quote=True)+m[2],text)
        text = text.replace('</head>',f'<meta property="article:published_time" content="{a["date"]}"></head>')
        (dest/'index.html').write_text(text,encoding='utf-8')
        (dest/'article.md').write_text(markdown(a,b.BASE),encoding='utf-8')
        figures = [{'file':a['hero']+'.png','alt':a['hero_alt'],'role':'cover'}] + [{'file':s['figure']+'.png','alt':s['figure_alt'],'caption':s['caption'],'role':'inline'} for s in a['sections'] if 'figure' in s]
        for f in figures:
            f['url'] = b.BASE+'/assets/articles/'+a['slug']+'/'+f['file']
        packet = {'schema':'neurasoft-editorial-packet-v1','id':a['date']+'-'+a['slug'],'title':a['title'],'publish':'auto','date':a['date'], 'canonical_url':b.BASE+route(a),'markdown_url':b.BASE+route(a)+'article.md','images':figures,'x_post':a['x_post']+'\n'+b.BASE+route(a),'linkedin_post':a['linkedin_post']+'\n'+b.BASE+route(a),'social_publication_status':'prepared-not-confirmed','instructions':'Publish this original article with cover and inline images in the indicated order. Use native X Article if available; otherwise publish the supplied short post linking to Neurasoft. Publish the LinkedIn adaptation with the cover and canonical link. Check account queue for this packet id and URL before posting. Do not invent research results or remove the conceptual-diagram labels. Record returned post URLs; do not treat receipt of this packet as publication.'}
        (dest/'grok-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cards = ''.join(f'<article class="dispatch-card"><a href="{route(a)}">{picture(a,a["hero"],a["hero_alt"])}</a><div><p class="dispatch-meta">{a["date"]} · {E(a["kind"])}</p><h2><a href="{route(a)}">{E(a["title"])}</a></h2><p>{E(a["summary"])}</p></div></article>' for a in articles)
    b.shell('/articles/','Dispatches','Illustrated essays on minds, machines, and the questions that stay with us.',b.page_hero('Neurasoft / Dispatches','Stay curious.','Illustrated essays on minds, machines, and the questions that stay with us.','Dispatches')+'<div class="dispatch-list">'+cards+'<a href="/articles/feed.xml">Subscribe by RSS</a></div>','journal',extra=CSS+FEED)
    a=articles[0]
    feature=f'<section class="dispatch-feature wrap" aria-label="Latest article"><div class="dispatch-feature-inner"><div><p class="eyebrow">Fresh from Neurasoft</p><p class="dispatch-label">{a["date"]} · {E(a["kind"])}</p><h2><a href="{route(a)}">{E(a["title"])}</a></h2><p>{E(a["summary"])}</p><div class="actions"><a class="text-link" href="{route(a)}">Read the illustrated essay ↗</a><a class="text-link" href="/articles/">All dispatches</a></div></div><a href="{route(a)}">{picture(a,a["hero"],a["hero_alt"])}</a></div></section>'
    home=b.OUT/'index.html'
    text=home.read_text(encoding='utf-8')
    marker='<section class="wrap intro-band">'
    if text.count(marker)!=1:
        raise ValueError('Homepage insertion point changed; review integration')
    home.write_text(text.replace(marker,feature+marker,1).replace('</head>',CSS+FEED+'</head>'),encoding='utf-8')
    journal=b.OUT/'journal/index.html'
    journal.write_text(journal.read_text(encoding='utf-8').replace('</main>','<section class="wrap section"><h2>New illustrated essays</h2><p><a class="text-link" href="/articles/">Read the latest dispatches ↗</a></p></section></main>'),encoding='utf-8')
    rows=json.loads((b.OUT/'assets/search-index.json').read_text(encoding='utf-8'))
    by_url={r['url']:r for r in rows}
    for row in b.SEARCH:
        if row['url'].startswith('/articles/'):
            by_url[row['url']]={**row,'type':'Article'}
    for r in by_url.values():
        r['text']=extract_main_text((b.OUT/r['url'].strip('/')/'index.html').read_text(encoding='utf-8'))
    (b.OUT/'assets/search-index.json').write_text(json.dumps(list(by_url.values()),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',ns)
    tree=ET.parse(b.OUT/'sitemap.xml'); root=tree.getroot()
    changed={'/','/journal/','/articles/'}
    for node in root:
        if node.find('{'+ns+'}loc').text.removeprefix(b.BASE) in changed:
            node.find('{'+ns+'}lastmod').text=articles[0]['date']
    for url,day in [('/articles/',articles[0]['date'])]+[(route(a),a['date']) for a in articles]:
        node=ET.SubElement(root,'{'+ns+'}url')
        ET.SubElement(node,'{'+ns+'}loc').text=b.BASE+url
        ET.SubElement(node,'{'+ns+'}lastmod').text=day
    tree.write(b.OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
    for k,v in [('title','Neurasoft dispatches'),('link',b.BASE+'/articles/'),('description','Illustrated essays on minds, machines, and the questions that stay with us.')]:
        ET.SubElement(channel,k).text=v
    for a in articles:
        item=ET.SubElement(channel,'item')
        for k,v in [('title',a['title']),('link',b.BASE+route(a)),('guid',b.BASE+route(a)),('description',a['summary']),('pubDate',format_datetime(datetime.fromisoformat(a['date']).replace(tzinfo=timezone.utc)))]:
            ET.SubElement(item,k).text=v
    ET.ElementTree(rss).write(b.OUT/'articles/feed.xml',encoding='utf-8',xml_declaration=True)
    (b.OUT/'articles/inbox.json').write_text(json.dumps({'schema':'neurasoft-editorial-inbox-v1','articles':[{'id':a['date']+'-'+a['slug'],'date':a['date'],'title':a['title'],'packet_url':b.BASE+route(a)+'grok-packet.json'} for a in articles]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Editorial: {len(articles)} articles; homepage, archive, search, RSS and Grok packets updated.')
