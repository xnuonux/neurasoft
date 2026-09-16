import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EditionTests(unittest.TestCase):
    def test_study_registry_drives_three_public_records(self):
        studies = json.loads((ROOT / 'content/studies.json').read_text(encoding='utf-8'))
        self.assertEqual(len({s['slug'] for s in studies}), 3)
        for study in studies:
            text = (ROOT / 'dist/studies' / study['slug'] / 'index.html').read_text(encoding='utf-8')
            for field in ('setup', 'intervention', 'result', 'limit', 'next'):
                self.assertIn(study[field], text)
            self.assertIn('Evidence & access', text)

    def test_full_content_index_has_no_site_chrome_or_private_refs(self):
        rows = json.loads((ROOT / 'dist/assets/search-index.json').read_text(encoding='utf-8'))
        self.assertEqual(len(rows), 36)
        for row in rows:
            self.assertTrue(row['text'], row['url'])
            self.assertNotIn('Primary navigation', row['text'])
            self.assertNotIn('psyche-lab PR', row['text'])
        luna = next(row for row in rows if row['url'] == '/luna/')
        self.assertIn('Room for the Last Note', luna['text'])

    def test_search_is_loaded_before_its_production_caller(self):
        text = (ROOT / 'dist/index.html').read_text(encoding='utf-8')
        self.assertLess(text.index('src="/assets/search.js"'), text.index('src="/assets/site.js"'))
        self.assertIn('NeurasoftSearch.searchPages(index,query)', (ROOT / 'assets/site.js').read_text(encoding='utf-8'))

    def test_motion_has_a_control_and_no_particle_renderer_target(self):
        text = (ROOT / 'dist/index.html').read_text(encoding='utf-8')
        self.assertIn('data-continuum', text)
        self.assertIn('data-pause-art', text)
        self.assertNotIn('data-field=', text)

    def test_architecture_has_small_screen_and_nonvisual_explanations(self):
        text = (ROOT / 'dist/architecture/index.html').read_text(encoding='utf-8')
        self.assertIn('architecture-mobile', text)
        self.assertIn('arch-desc', text)
        self.assertIn('Coupling to investigate', text)

    def test_glossary_does_not_equate_effect_and_measurement(self):
        text = (ROOT / 'dist/glossary/index.html').read_text(encoding='utf-8')
        self.assertNotIn('what was actually observed after an action', text)
        self.assertIn('an effect of an action', text)

    def test_historical_journal_dates_follow_the_source_record(self):
        notes = json.loads((ROOT / 'content/journal.json').read_text(encoding='utf-8'))
        from datetime import date
        for note in notes:
            d = date.fromisoformat(note['date'])
            label = f'{d.day:02d} {d.strftime("%b")} {d.year}'
            text = (ROOT / 'dist/journal' / note['slug'] / 'index.html').read_text(encoding='utf-8')
            self.assertTrue(label in text, f'{note["slug"]} must retain {label}')
