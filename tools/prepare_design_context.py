"""Mechanical, public-only design snapshot for the authored canvas preview."""
from pathlib import Path
import ast
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build
import publication
import edition_three

out = ROOT / '.superdesign/init'
out.mkdir(parents=True, exist_ok=True)
page = (ROOT / 'dist/index.html').read_text(encoding='utf-8')
header = re.search(r'<header.*?</header>', page, re.S).group(0)
footer = re.search(r'<footer.*?</footer>', page, re.S).group(0)
hero = re.search(r'<section class="hero wrap">.*?</section>', page, re.S).group(0)
primitives = []
code = (ROOT / 'build.py').read_text(encoding='utf-8')
for node in ast.parse(code).body:
    if isinstance(node, ast.FunctionDef) and node.name in ('link', 'page_hero', 'toc', 'note_card'):
        primitives.append(ast.get_source_segment(code, node))
docs = {
 'components.md': '# Native HTML primitives\n\nPython templates, not React. Full shared function source from build.py:\n```python\n' + '\n\n'.join(primitives) + '\n```\n\nThe original nested-arch logo is retained verbatim from assets/favicon.svg.\n',
 'layouts.md': '# Shared layout\n\nComplete rendered shared components. Source: publication.install, wrapped by edition_three.install. No sidebar.\n\n## Header\n```html\n' + header + '\n```\n\n## Footer\n```html\n' + footer + '\n```\n',
 'routes.md': '# Static route map\n\nThe builder generates directory/index.html routes with a shared header/footer. No client router.\n' + '\n'.join('- ' + str(p.relative_to(ROOT/'dist')).replace('index.html', '') + ' -> build.py / publication.py / edition_three.py' for p in (ROOT/'dist').rglob('index.html')) + '\n\nHome is a research invitation; findings has three comparative records; architecture distinguishes operating surfaces from experiments.\n',
 'theme.md': '# Design tokens\n\nWarm paper #f3f1e9; sage surface #e9ede2; ink #243c32; accent #365d47; muted #596458; line #cbd2c2. System sans + Georgia italic + monospace labels. Thin rules, 3-8px radii, no dark bands, no particle clouds. Max width1336px; mobile760px, legacy navigation820px. Motion is a slow SVG path accent with pause/reduced-motion/offscreen stops.\n\n## Full stylesheets\n' + '\n'.join(f'### {name}\n```css\n{(ROOT/name).read_text(encoding="utf-8")}\n```\n' for name in ('assets/site.css', 'assets/edition.css')),
 'pages.md': '# Page dependencies\n\nAll pages: build.py shell -> publication.py header/footer -> edition_three.py publication wrapper -> assets/site.css + assets/edition.css + assets/site.js + assets/search.js. No frontend package dependencies.\n\n## /\n- edition_three.render_home\n  - visuals.continuum\n  - visuals.study\n  - content/studies.json -> study_cards\n  - content/journal.json -> build.note_card\n## /architecture/\n- edition_three.render_architecture\n  - architecture_diagram and responsive text counterpart\n  - study_cards -> content/studies.json\n## /studies/*\n- edition_three.render_studies\n  - content/studies.json\n  - results_table\n## /findings/\n- edition_three.finish\n  - study_cards and journal cards\n## /luna/, /psyche-lab/, /standards/\n- build.py original page\n  - edition_three.amend_page adds episode, current research and definitions\n## /glossary/\n- publication.PAGES -> render_page\n## /observatory/\n- build.py exhibit\n  - assets/site.js transparent teaching model\n\nPublic search: public_search.py indexes final rendered main content only.\n',
 'extractable-components.md': '# Reusable components\n\n## Navigation\nSource: publication.install / edition_three.install. Category: layout. Prop: active page. Original logo, link labels, styles are fixed.\n\n## Footer\nSource: publication.install / edition_three.install. Category: layout. No props.\n\n## ResearchCard\nSource: edition_three.study_cards. Category: basic. Navigation URL and study content from the registry; no invented badges.\n\n## ContinuityIllustration\nSource: visuals.continuum. Category: basic. No page state or telemetry. Same conceptual line relationships and palette everywhere.\n\n## TextLink\nSource: build.link. Category: basic. Props: URL and label; arrow and styling fixed.\n',
}
for name, content in docs.items():
    (out/name).write_text(content, encoding='utf-8')
(ROOT/'.superdesign/design-system.md').write_text((ROOT/'DESIGN-SYSTEM.md').read_text(encoding='utf-8') + '\nEdition 3 replaces particle sculpture with authored conceptual diagrams and data-bearing comparison tables. Source identity remains unchanged.\n', encoding='utf-8')
# Direct-authoring canvas document: one desktop screen, no private data or scripts.
css = '\n'.join((ROOT/name).read_text(encoding='utf-8') for name in ('assets/site.css', 'assets/edition.css'))
preview = header + '<main>' + hero + '</main>'
preview = preview.replace(build.MARK, '<img src="https://vgbujcuwptvheqijyjbe.supabase.co/storage/v1/object/public/hmac-uploads/projects/6e2b9c45-6864-4199-9f98-998668b4a62b/brand-assets/assets-favicon.svg/favicon.svg" alt="" width="32" height="34">')
preview = re.sub(r'href="/([^"]*)"', r'href="https://neurasoft.us/\1"', preview)
counter = iter(range(1, 100))
preview = re.sub(r'<a ', lambda m: f'<a id="preview-link-{next(counter)}" ', preview)
preview = '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neurasoft / Scientific publication</title><style>' + css + '</style></head><body><div class="relative min-h-screen w-full">' + preview + '</div></body></html>'
tmp = ROOT/'.superdesign/tmp'
tmp.mkdir(exist_ok=True)
(tmp/'neurasoft-home.html').write_text(preview, encoding='utf-8')
print('Six design context documents and one public-only hero preview prepared.')
