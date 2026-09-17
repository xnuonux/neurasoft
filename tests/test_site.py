import json, re, unittest, xml.etree.ElementTree as ET, tomllib
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tags=[];self.ids=[];self.links=[];self.refs=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag in ('script','img') and a.get('src'):self.refs.append(a['src'])
  if tag=='link' and a.get('rel') in ('stylesheet','icon'):self.refs.append(a.get('href',''))
class SiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pages=list(DIST.rglob('*.html'));cls.text={p:p.read_text(encoding='utf-8') for p in cls.pages};cls.docs={p:Document(t) for p,t in cls.text.items()};cls.joined='\n'.join(cls.text.values())
 def test_37_html_pages(self):self.assertEqual(len(self.pages),37)
 def test_7_full_journal_notes(self):self.assertEqual(len(list((DIST/'journal').glob('*/index.html'))),7)
 def test_every_page_has_one_h1(self):
  for p,d in self.docs.items():self.assertEqual(sum(t=='h1' for t,a in d.tags),1,str(p))
 def test_every_page_has_main(self):
  for p,d in self.docs.items():self.assertEqual(sum(t=='main' for t,a in d.tags),1,str(p))
 def test_unique_page_ids(self):
  for p,d in self.docs.items():self.assertEqual(len(d.ids),len(set(d.ids)),str(p))
 def test_internal_links_and_anchors(self):
  for p,d in self.docs.items():
   for href in d.links:
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    target=p if not u.path else (DIST/unquote(u.path.lstrip('/')))
    if target.is_dir():target=target/'index.html'
    self.assertTrue(target.is_file(),f'{p}: {href}')
    if u.fragment:self.assertIn(unquote(u.fragment),self.docs[target].ids,f'{p}: {href}')
 def test_asset_references_exist(self):
  for p,d in self.docs.items():
   for r in d.refs:self.assertTrue((DIST/r.lstrip('/')).is_file(),f'{p}: {r}')
 def test_social_image_exists(self):self.assertTrue((DIST/'assets/social.png').is_file())
 def test_correct_parent_structure(self):
  self.assertIn('Eternities Inc. is the parent company of Neurasoft and Lunari',self.text[DIST/'about/index.html'])
 def test_no_claimed_big_lab_affiliation(self):
  self.assertNotRegex(self.joined,r'(?i)(subsidiary of|backed by|partnered with) (Google|OpenAI|Anthropic)')
 def test_no_private_paths(self):self.assertNotRegex(self.joined,r'(?i)(D:/01-ETERNITIES|[A-Z]:\\|/mnt/data|xnuonux/|github\.com/xnuonux|PID\d|operationRevision|@@reload)')
 def test_no_credentials(self):self.assertNotRegex(self.joined,r'(sk-[A-Za-z0-9]{16}|ghp_[A-Za-z0-9]+|netlify-mcp\.netlify\.app/proxy/)')
 def test_private_directory_not_deployed(self):self.assertFalse((DIST/'private').exists())
 def test_no_source_bundle_in_public_tree(self):self.assertFalse(any(DIST.rglob('*.zip')))
 def test_article_source_dates(self):
  for p in (DIST/'journal').glob('*/index.html'):self.assertIn('Underlying record:',p.read_text(encoding='utf-8'))
 def test_articles_not_peer_reviewed(self):
  for p in (DIST/'journal').glob('*/index.html'):self.assertIn('Not peer reviewed',p.read_text(encoding='utf-8'))
 def test_observatory_boundary(self):self.assertIn('not the Psyche Lab engine',self.text[DIST/'observatory/index.html'])
 def test_no_external_assets(self):
  for d in self.docs.values():
   for r in d.refs:self.assertFalse(urlsplit(r).netloc)
 def test_no_forms_that_fake_delivery(self):
  self.assertNotIn('<form',self.joined)
 def test_search_index_targets(self):
  for row in json.loads((DIST/'assets/search-index.json').read_text(encoding='utf-8')):self.assertTrue((DIST/row['url'].strip('/')/'index.html').exists())
 def test_sitemap_xml(self):
  tree=ET.parse(DIST/'sitemap.xml');self.assertEqual(len(list(tree.getroot())),36)
 def test_publish_directory(self):
  config=tomllib.loads((ROOT/'netlify.toml').read_text(encoding='utf-8'));self.assertEqual(config['build']['publish'],'dist')
 def test_csp(self):self.assertIn("default-src 'self'",(DIST/'_headers').read_text(encoding='utf-8'))
 def test_no_inline_executable_script_or_style(self):
  for d in self.docs.values():
   for tag,a in d.tags:
    if tag=='script':self.assertIn('src',a)
    self.assertNotIn('style',a)
    self.assertFalse(any(k.startswith('on') for k in a))
 def test_all_article_sections_substantive(self):
  for note in json.loads((ROOT/'content/journal.json').read_text(encoding='utf-8')):
   self.assertGreaterEqual(len(note['sections']),4)
   self.assertGreater(len(' '.join(' '.join(s) for s in note['sections'])),1300)
 def test_design_has_reduced_motion_support(self):self.assertIn('prefers-reduced-motion:reduce',(DIST/'assets/site.css').read_text(encoding='utf-8'))
 def test_art_has_pause_controls(self):
  for p,text in self.text.items():
   if 'data-field=' in text:self.assertIn('data-pause-art',text,str(p))
if __name__=='__main__':unittest.main()
