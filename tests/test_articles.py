import copy
from html import escape
import json
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET
from articles import load_articles, route

ROOT = Path(__file__).resolve().parents[1]


class ArticleTests(unittest.TestCase):
    def test_latest_is_on_homepage_and_all_articles_are_searchable(self):
        articles = load_articles(ROOT)
        home = (ROOT/'dist/index.html').read_text(encoding='utf-8')
        index = json.loads((ROOT/'dist/assets/search-index.json').read_text(encoding='utf-8'))
        self.assertIn(articles[0]['title'], home)
        for a in articles:
            row = next(r for r in index if r['url'] == route(a))
            self.assertIn(a['intro'][0], row['text'])
            self.assertEqual(row['type'], 'Article')

    def test_packets_have_public_media_and_do_not_claim_social_publication(self):
        for a in load_articles(ROOT):
            root = ROOT/'dist'/route(a).strip('/')
            packet = json.loads((root/'grok-packet.json').read_text(encoding='utf-8'))
            self.assertEqual(packet['social_publication_status'], 'prepared-not-confirmed')
            self.assertEqual(len(packet['images']), 1+sum('figure' in s for s in a['sections']))
            self.assertLessEqual(len(a['x_post'])+1+23, 280)
            for image in packet['images']:
                local = ROOT/'dist'/image['url'].removeprefix('https://neurasoft.us/')
                self.assertTrue(local.is_file())
                self.assertTrue(image['alt'])
            html = (root/'index.html').read_text(encoding='utf-8')
            self.assertIn(packet['images'][0]['url'], html)
            self.assertIn(escape(a['editorial_note'], quote=True), html)

    def test_feed_and_sitemap_are_unique_and_retain_historical_dates(self):
        articles = load_articles(ROOT)
        feed = ET.parse(ROOT/'dist/articles/feed.xml')
        self.assertEqual([n.text for n in feed.findall('./channel/item/link')], ['https://neurasoft.us'+route(a) for a in articles])
        ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        nodes = ET.parse(ROOT/'dist/sitemap.xml').findall('s:url',ns)
        locs=[n.find('s:loc',ns).text for n in nodes]
        self.assertEqual(len(locs),len(set(locs)))
        historical=next(n for n in nodes if '/journal/' in n.find('s:loc',ns).text and n.find('s:loc',ns).text!='https://neurasoft.us/journal/')
        self.assertEqual(historical.find('s:lastmod',ns).text,'2026-09-16')

    def test_future_drafts_sorting_duplicates_and_missing_media(self):
        original = load_articles(ROOT)[0]
        today = date.fromisoformat(original['date'])
        with tempfile.TemporaryDirectory(prefix='neurasoft-editorial-test-') as tmp:
            root=Path(tmp); content=root/'content/articles'; content.mkdir(parents=True)
            shutil.copytree(ROOT/'assets/articles',root/'assets/articles')
            def put(name, data):
                (content/name).write_text(json.dumps(data),encoding='utf-8')
            put('now.json',original)
            future=copy.deepcopy(original);future['slug']='future';future['date']='2099-01-01'
            put('future.json',future)
            draft=copy.deepcopy(original);draft['status']='draft';draft['slug']='draft'
            put('draft.json',draft)
            self.assertEqual([a['slug'] for a in load_articles(root,today)],[original['slug']])
            older=copy.deepcopy(original);older['slug']='older';older['date']=(today-timedelta(days=1)).isoformat()
            shutil.copytree(ROOT/'assets/articles'/original['slug'],root/'assets/articles/older')
            put('older.json',older)
            self.assertEqual([a['slug'] for a in load_articles(root,today)],[original['slug'],'older'])
            put('duplicate.json',original)
            with self.assertRaisesRegex(ValueError,'Duplicate'): load_articles(root,today)
            (content/'duplicate.json').unlink()
            (root/'assets/articles/older'/(older['hero']+'.png')).unlink()
            with self.assertRaisesRegex(ValueError,'Missing illustration'): load_articles(root,today)


if __name__=='__main__': unittest.main()
