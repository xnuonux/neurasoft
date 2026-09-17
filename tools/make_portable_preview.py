"""Create a transport-only single-file preview. Never deploy this instead of dist/."""
from pathlib import Path
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
OUT = ROOT.parent / 'NEURASOFT_INTERACTIVE_PREVIEW.html'

def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

css = (DIST / 'assets/site.css').read_text(encoding='utf-8')
js = (DIST / 'assets/site.js').read_text(encoding='utf-8')
index = json.loads((DIST / 'assets/search-index.json').read_text(encoding='utf-8'))
icon = 'data:image/svg+xml;base64,' + base64.b64encode((DIST/'assets/favicon.svg').read_bytes()).decode()
pages = {}
for path in sorted(DIST.rglob('*.html')):
    route = '/' + str(path.parent.relative_to(DIST)).replace('\\', '/').strip('./') + '/'
    if route == '//': route = '/'
    if path.name == '404.html': route = '/404/'
    text = path.read_text(encoding='utf-8')
    text = text.replace('<link rel="stylesheet" href="/assets/site.css">', '<style>' + css + '</style>')
    text = text.replace('href="/assets/favicon.svg"', 'href="'+icon+'"')
    text = re.sub(r'<script\s+src="/assets/site.js"\s+defer></script>', '', text)
    adapter = '''
const previewIndex = INDEX;
window.fetch = async function(url) {
  if (String(url) === '/assets/search-index.json') return {ok:true,json:async()=>previewIndex};
  throw new Error('This local preview does not make network requests.');
};
document.addEventListener('click', function(e) {
  const a=e.target.closest('a[href]'); if(!a || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
  const raw=a.getAttribute('href');
  if(raw.startsWith('#')) {const target=document.getElementById(decodeURIComponent(raw.slice(1)));if(target){e.preventDefault();target.scrollIntoView();if(raw==='#main')target.focus({preventScroll:true});}return;}
  const url=new URL(raw, 'https://neurasoft.usROUTE');
  if(url.origin==='https://neurasoft.us') {e.preventDefault();parent.postMessage({type:'neurasoft-preview-route',route:url.pathname+url.hash},'*');}
  else if(url.protocol==='http:'||url.protocol==='https:'){a.target='_blank';a.rel='noopener noreferrer';}
}, true);
'''.replace('INDEX', safe_json(index)).replace('ROUTE', route)
    text = text.replace('</body>', '<script>'+adapter+'\n'+js+'</script></body>')
    pages[route] = text

shell = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neurasoft — Interactive local preview</title><meta name="description" content="The complete Neurasoft research website, packaged as a self-contained local preview."><style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;background:#f4f3ec;color:#172a26;font:12px Arial,sans-serif}.preview-bar{height:32px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;background:#172a26;color:#eef0e5;gap:12px}.preview-bar button{background:transparent;color:inherit;border:0;cursor:pointer;padding:4px 8px;font:inherit}.preview-bar button:focus-visible{outline:1px solid #d8ed7f}#preview-route{opacity:.75;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.preview-label{white-space:nowrap}iframe{display:block;border:0;width:100%;height:calc(100dvh - 32px)}noscript{display:block;padding:40px;font-size:18px} @media(max-width:600px){.preview-bar{padding:0 6px;font-size:10px}#preview-route{max-width:32vw}}
</style></head><body><div class="preview-bar"><div><button id="preview-home" type="button" aria-label="Return to preview homepage">Neurasoft</button><button id="preview-back" type="button" aria-label="Go back">← Back</button></div><span id="preview-route">/</span><span class="preview-label">Local preview · Not the live domain</span></div><iframe id="site-frame" title="Neurasoft website preview" allow="clipboard-write"></iframe><noscript>This interactive preview requires JavaScript. The accompanying website package contains fully readable static pages.</noscript><script type="application/json" id="preview-pages">PAGES_JSON</script><script>
'use strict';
const pages=JSON.parse(document.getElementById('preview-pages').textContent);
const frame=document.getElementById('site-frame');
let active='';
function go(route){if(typeof route!=='string'||!route.startsWith('/')||route.startsWith('//'))return;location.hash=route;if(active!==route)render(route);}
function render(raw){let [path,...fragments]=raw.split('#');if(!path.startsWith('/'))path='/';if(!path.endsWith('/'))path+='/';const known=Object.hasOwn(pages,path);const selected=known?path:'/404/';active=raw;document.getElementById('preview-route').textContent=known?raw:'/404/';frame.onload=function(){const doc=frame.contentDocument;if(!doc)return;document.title=doc.title+' · Local preview';if(fragments.length){const target=doc.getElementById(decodeURIComponent(fragments.join('#')));target?.scrollIntoView();}else frame.contentWindow.scrollTo(0,0);};frame.srcdoc=pages[selected];}
window.addEventListener('message',e=>{if(e.source===frame.contentWindow&&e.data?.type==='neurasoft-preview-route')go(e.data.route);});
window.addEventListener('hashchange',()=>render(location.hash.slice(1)||'/'));
document.getElementById('preview-home').onclick=()=>go('/');document.getElementById('preview-back').onclick=()=>history.back();
render(location.hash.slice(1)||'/');
</script></body></html>'''.replace('PAGES_JSON', safe_json(pages))
OUT.write_text(shell, encoding='utf-8')
print(f'{OUT}: {len(pages)} embedded pages, {OUT.stat().st_size:,} bytes')
