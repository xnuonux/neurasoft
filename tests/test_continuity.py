import copy, hashlib, json, re, tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
from continuity_publication import apply, validate, load, main_text
from continuity_audit import evaluate, observe, key, validate_manifest
ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,9,16,12,tzinfo=timezone.utc)

class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.source=self.root/'source';self.stage=self.root/'stage'
  (self.source/'content').mkdir(parents=True);(self.stage/'assets').mkdir(parents=True)
  for name in ('identity.json','publication.json'):(self.source/'content'/name).write_bytes((ROOT/'content'/name).read_bytes())
  for route in ('','luna','glossary','journal/original'):
   p=self.stage/route/'index.html';p.parent.mkdir(parents=True,exist_ok=True)
   p.write_text('<!doctype html><html><head><title>Original</title><meta name="description" content="Original"><meta property="og:title" content="Original"><meta property="og:url" content="https://neurasoft.us/"><link rel="canonical" href="https://neurasoft.us/"></head><body><main id="main"><h1>For what a mind may become.</h1><p>The science, in the open</p><p>Dated record: September 14, 2026.</p></main><footer><a href="/contact/">Contact</a></footer></body></html>',encoding='utf-8')
  (self.stage/'assets/search-index.json').write_text('[]',encoding='utf-8')
  (self.stage/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://neurasoft.us/</loc><lastmod>2026-09-16</lastmod></url></urlset>',encoding='utf-8')
 def run_stage(self):return apply(self.stage,self.source)
 def read(self,path):return (self.stage/path).read_text(encoding='utf-8')
 def test_name_on_luna_and_glossary(self):
  self.run_stage()
  for name in ('luna/index.html','glossary/index.html'):self.assertIn('Locus of Unified Noetic Agency',self.read(name))
 def test_home_headline_and_new_question(self):
  self.run_stage();x=self.read('index.html');self.assertIn('For what a mind may become.',x);self.assertIn('Current research question',x);self.assertNotIn('The science, in the open',x)
 def test_search_contains_acronym_and_updates(self):
  self.run_stage();entries=json.loads(self.read('assets/search-index.json'));self.assertTrue(any(x['url']=='/luna/' and 'Locus of Unified Noetic Agency' in x['text'] for x in entries));self.assertTrue(any(x['url']=='/updates/' for x in entries))
 def test_review_dates_not_build_clock(self):
  self.run_stage();p=json.loads(self.read('assets/publication.json'));self.assertEqual(p['research_review_through'],'2026-09-16');self.assertEqual(p['native_record_through'],'2026-09-14')
 def test_historical_date_preserved(self):
  before=main_text(self.read('journal/original/index.html'));self.run_stage();self.assertEqual(before,main_text(self.read('journal/original/index.html')))
 def test_original_input_config_unchanged(self):
  before=(self.source/'content/publication.json').read_bytes();self.run_stage();self.assertEqual(before,(self.source/'content/publication.json').read_bytes())
 def test_repeated_build_idempotent(self):
  self.run_stage();before={p.relative_to(self.stage):p.read_bytes() for p in self.stage.rglob('*') if p.is_file()};self.run_stage();self.assertEqual(before,{p.relative_to(self.stage):p.read_bytes() for p in self.stage.rglob('*') if p.is_file()})
 def test_changed_metadata_requires_clean_stage(self):
  self.run_stage();p=self.source/'content/publication.json';d=json.loads(p.read_text());d['edition']='new';p.write_text(json.dumps(d));self.assertRaises(ValueError,self.run_stage)
 def test_rss_parse_and_real_anchors(self):
  self.run_stage();rss=ET.fromstring(self.read('feed.xml'));guid=rss.findtext('./channel/item/guid');self.assertIn('id="'+guid.split('#')[1]+'"',self.read('updates/index.html'))
 def test_sitemap_includes_updates(self):
  self.run_stage();self.assertIn('https://neurasoft.us/updates/',self.read('sitemap.xml'))
 def test_public_json_excludes_extra_private_fields(self):
  p=self.source/'content/publication.json';d=json.loads(p.read_text());d['secret']='private-example';d['changes'][0]['internal_url']='private-example';p.write_text(json.dumps(d));self.run_stage();self.assertNotIn('private-example',self.read('assets/publication.json'))
 def test_current_question_html_escaped(self):
  p=self.source/'content/publication.json';d=json.loads(p.read_text());d['current_question']['body']='<script>danger()</script>';p.write_text(json.dumps(d));self.run_stage();self.assertNotIn('<script>danger()',self.read('index.html'));self.assertIn('&lt;script&gt;',self.read('index.html'))
 def test_network_relative_link_rejected(self):
  i=load(self.source/'content/identity.json');p=load(self.source/'content/publication.json');p['current_question']['link']='//evil/';self.assertRaises(ValueError,validate,i,p)
 def test_name_cannot_silently_drift(self):
  i=load(self.source/'content/identity.json');p=load(self.source/'content/publication.json');i['luna_expansion']='something else';self.assertRaises(ValueError,validate,i,p)
 def test_missing_required_page_fails(self):
  (self.stage/'luna/index.html').unlink();self.assertRaises(ValueError,self.run_stage)
 def test_existing_updates_not_overwritten(self):
  p=self.stage/'updates/index.html';p.parent.mkdir();p.write_text('existing');self.assertRaises(ValueError,self.run_stage);self.assertEqual(p.read_text(),'existing')
 def test_symlink_refused(self):
  try:(self.stage/'link').symlink_to(self.source)
  except OSError:self.skipTest('symlink not supported by host')
  self.assertRaises(ValueError,self.run_stage)
 def test_duplicate_json_keys_rejected(self):
  p=self.root/'duplicate.json';p.write_text('{"a":1,"a":2}');self.assertRaises(ValueError,load,p)
 def test_scripts_not_in_search(self):self.assertEqual(main_text('<main>Hello<script>private code</script><svg><text>geometry</text></svg>World</main>'),'Hello World')
 def test_public_orientation_no_private_urls(self):
  self.run_stage();llms=self.read('llms.txt');self.assertNotIn('github.com/xnuonux',llms);self.assertNotIn('drive.google',llms)

class AuditTests(unittest.TestCase):
 def setUp(self):
  self.m=load(ROOT/'company/claims.json');self.obs={key(s):{'status':'observed','blob':s['reviewed_blob'],'commit':'a'*40,'observed_at':NOW.isoformat()} for c in self.m['claims'] for s in c['sources']}
 def run_audit(self):return evaluate(self.m,self.obs,NOW)
 def test_unchanged(self):self.assertFalse(self.run_audit()['review_required'])
 def test_changed_blob_needs_review(self):next(iter(self.obs.values()))['blob']='b'*40;self.assertTrue(self.run_audit()['review_required'])
 def test_unrelated_commit_no_file_change(self):next(iter(self.obs.values()))['commit']='b'*40;self.assertFalse(self.run_audit()['review_required'])
 def test_missing_access_not_fresh(self):next(iter(self.obs.values()))['status']='unavailable';self.assertTrue(self.run_audit()['review_required'])
 def test_deleted_or_hidden_file_not_fresh(self):next(iter(self.obs.values()))['status']='missing';self.assertIn('source-missing-or-inaccessible',self.run_audit()['claims'][0]['reasons'])
 def test_absent_observation_not_fresh(self):self.obs={};self.assertTrue(self.run_audit()['review_required'])
 def test_expired_observation_not_fresh(self):next(iter(self.obs.values()))['observed_at']=(NOW-timedelta(days=2)).isoformat();self.assertTrue(self.run_audit()['review_required'])
 def test_future_observation_not_fresh(self):next(iter(self.obs.values()))['observed_at']=(NOW+timedelta(seconds=1)).isoformat();self.assertTrue(self.run_audit()['review_required'])
 def test_revoked_approval_not_reinstated(self):self.m['claims'][0]['approval']='revoked';self.assertIn('approval-revoked',self.run_audit()['claims'][0]['reasons'])
 def test_overdue_review_even_when_bytes_same(self):self.m['claims'][0]['reviewed_at']='2026-01-01T00:00:00Z';self.assertIn('review-overdue',self.run_audit()['claims'][0]['reasons'])
 def test_never_advance_review_date(self):original=copy.deepcopy(self.m);self.run_audit();self.assertEqual(original,self.m)
 def test_no_token_makes_no_freshness_claim(self):obs=observe(self.m,None,NOW);self.assertTrue(all(x['status']=='unavailable' for x in obs.values()))
 def test_output_never_autopublishes(self):self.assertFalse(self.run_audit()['automatic_publication'])
 def test_path_escape_rejected(self):self.m['claims'][0]['sources'][0]['path']='../bad';self.assertRaises(ValueError,validate_manifest,self.m)
 def test_duplicate_id_rejected(self):self.m['claims'][1]['id']=self.m['claims'][0]['id'];self.assertRaises(ValueError,validate_manifest,self.m)

 def test_symlink_git_source_not_accepted(self):
  from unittest.mock import patch
  def remote(path,token):
   if '/commits/' in path:return {'sha':'a'*40,'commit':{'tree':{'sha':'b'*40}}}
   return {'tree':[{'path':'canon','type':'tree','mode':'040000','sha':'c'*40},{'path':'luna.md','type':'blob','mode':'120000','sha':'d'*40}]}
  self.m['claims']=self.m['claims'][:1]
  with patch('continuity_audit.github_json',side_effect=remote):result=observe(self.m,'test-only',NOW)
  self.assertTrue(all(x['status']=='unavailable' for x in result.values()))
 def test_truncated_git_tree_not_fresh(self):
  from unittest.mock import patch
  def remote(path,token):
   if '/commits/' in path:return {'sha':'a'*40,'commit':{'tree':{'sha':'b'*40}}}
   return {'tree':[],'truncated':True}
  with patch('continuity_audit.github_json',side_effect=remote):result=observe(self.m,'test-only',NOW)
  self.assertTrue(all(x['status']=='unavailable' for x in result.values()))
 def test_regular_git_file_bound_to_commit(self):
  from unittest.mock import patch
  self.m['claims']=self.m['claims'][:1];source=self.m['claims'][0]['sources'][0]
  def remote(path,token):
   if '/commits/' in path:return {'sha':'a'*40,'commit':{'tree':{'sha':'b'*40}}}
   if path.endswith('b'*40):return {'tree':[{'path':'canon','type':'tree','mode':'040000','sha':'c'*40}]}
   return {'tree':[{'path':'luna.md','type':'blob','mode':'100644','sha':source['reviewed_blob']}]}
  with patch('continuity_audit.github_json',side_effect=remote):result=observe(self.m,'test-only',NOW)
  self.assertEqual(result[key(source)]['commit'],'a'*40)
  self.assertFalse(evaluate(self.m,result,NOW)['review_required'])

if __name__=='__main__':unittest.main()
