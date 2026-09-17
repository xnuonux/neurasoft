"""Standalone preview integration checks, using offline Chromium, not hosted routes."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ok(name, condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition: raise AssertionError(name)

# Run directly; it is intentionally not an import-time unittest.
def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1050},reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content((ROOT.parent/'NEURASOFT_INTERACTIVE_PREVIEW.html').read_text(encoding='utf-8'),wait_until='load')
        frame=page.frame_locator('#site-frame')
        frame.locator('h1').wait_for()
        ok('Portable homepage rendered', 'Intelligence,' in frame.locator('h1').inner_text())
        frame.locator('.hero-copy a[href="/research/"]').click()
        frame.locator('h1').wait_for(); page.wait_for_timeout(150)
        ok('Internal research navigation works',page.locator('#preview-route').inner_text()=='/research/')
        frame.locator('#primary-nav a[href="/journal/"]').click();page.wait_for_timeout(150)
        ok('Journal route works', frame.locator('.journal-card').count()==7)
        frame.locator('.journal-card').first.click();page.wait_for_timeout(150)
        ok('Full article navigation works','/journal/' in page.locator('#preview-route').inner_text() and frame.locator('h1').is_visible())
        frame.locator('[data-search-open]').click();frame.locator('#site-search').fill('replay');page.wait_for_timeout(150)
        ok('Embedded index supports search',frame.locator('.search-result').count()>0)
        frame.locator('.search-close').click()
        frame.locator('#primary-nav a[href="/observatory/"]').click();page.wait_for_timeout(150)
        frame.locator('#run-exhibit').click();frame.locator('#replay-exhibit').click()
        ok('Portable model actually runs and replays','Exact replay:' in frame.locator('#exhibit-status').inner_text())
        frame.locator('#perturb-exhibit').click()
        ok('Portable counterfactual works','Largest response difference' in frame.locator('#exhibit-status').inner_text())
        with page.expect_download() as event:frame.locator('#export-exhibit').click()
        event.value.save_as(str(ROOT/'private/portable-exhibit-export.json'))
        data=json.loads((ROOT/'private/portable-exhibit-export.json').read_text(encoding='utf-8'))
        ok('Portable export preserves limits',data['illustrative_only'] and not data['connected_to_live_system'])
        page.set_viewport_size({'width':390,'height':844});page.locator('#preview-home').click();page.wait_for_timeout(150)
        ok('Portable mobile homepage has no overflow',page.frames[1].evaluate('document.documentElement.scrollWidth<=innerWidth'))
        frame.locator('.menu-toggle').click();ok('Portable mobile menu works',frame.locator('#primary-nav').is_visible())
        ok('Portable preview has no page errors',not errors)
        browser.close()
    (ROOT/'private/portable-browser-report.json').write_text(json.dumps({'mode':'Offline browser, embedded site, local assets; not production deployment','passed':len(checks),'checks':checks},indent=2), encoding='utf-8')
    print(f'{len(checks)} portable preview checks passed.')

if __name__=='__main__': main()
