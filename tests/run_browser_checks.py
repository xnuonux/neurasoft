"""Functional browser checks on locally injected static assets; no network deployment claim."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from browser_qa import load, ROOT, DIST, SHOTS
checks=[]
def ok(name,condition,detail=''):
 checks.append({'name':name,'passed':bool(condition),'detail':detail})
 if not condition:raise AssertionError(name+': '+str(detail))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1,reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 routes=['/']+['/'+str(f.parent.relative_to(DIST)).replace('\\','/')+'/' for f in DIST.glob('**/index.html') if f!=DIST/'index.html']
 for width in [390,1440]:
  page.set_viewport_size({'width':width,'height':844 if width==390 else 1050})
  for route in routes:
   load(page,route)
   ok(f'{route} at {width}px has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
   ok(f'{route} at {width}px has visible heading',page.locator('h1').is_visible())
 page.set_viewport_size({'width':390,'height':844});load(page)
 page.locator('.menu-toggle').click();ok('Mobile menu opens',page.locator('#primary-nav').is_visible())
 page.keyboard.press('Escape');ok('Escape closes mobile menu',not page.locator('#primary-nav').is_visible())
 page.locator('[data-search-open]').click();page.locator('#site-search').fill('memory');page.wait_for_timeout(100)
 ok('Search finds memory content',page.locator('.search-result').count()>0)
 ok('Search never renders raw query markup',page.locator('.search-results').locator('script').count()==0)
 page.keyboard.press('Escape');ok('Search dialog closes',not page.locator('.search-dialog').is_visible())
 load(page,'/journal/')
 page.locator('[data-filter="Methods"]').click();ok('Methods filter selects two notes',page.locator('.journal-card:visible').count()==2)
 page.locator('[data-filter="Engineering"]').click();ok('Engineering filter selects two notes',page.locator('.journal-card:visible').count()==2)
 page.locator('[data-filter="Perspective"]').click();ok('Perspective filter selects three notes',page.locator('.journal-card:visible').count()==3)
 page.locator('[data-filter="All"]').click();ok('All filter restores seven notes',page.locator('.journal-card:visible').count()==7)
 load(page,'/observatory/')
 page.locator('#export-exhibit').click();ok('Empty export is blocked','Run the model first' in page.locator('#exhibit-status').inner_text())
 page.locator('#run-exhibit').click();ok('Exhibit computes 96 steps','96 deterministic steps' in page.locator('#exhibit-status').inner_text())
 page.locator('#replay-exhibit').click();ok('Replay compares exact complete record','Exact replay: all recorded values match.' in page.locator('#exhibit-status').inner_text())
 page.locator('#perturb-exhibit').click();ok('Intervention produces counterfactual','Largest response difference' in page.locator('#exhibit-status').inner_text())
 with page.expect_download() as event:page.locator('#export-exhibit').click()
 downloaded=event.value;target=ROOT/'private/illustration-test-export.json';downloaded.save_as(str(target));data=json.loads(target.read_text())
 ok('Export marks illustration explicitly',data['illustrative_only'] is True and data['connected_to_live_system'] is False)
 ok('Export has full trajectories',len(data['baseline'])==len(data['counterfactual'])==96)
 ok('Histories equal before the intervention',data['baseline'][:32]==data['counterfactual'][:32])
 ok('Histories differ at intervention',data['baseline'][32]!=data['counterfactual'][32])
 page.locator('#memory-retention').fill('50');page.locator('#export-exhibit').click();ok('Changed controls cannot export stale run','Run the model first' in page.locator('#exhibit-status').inner_text())
 page.locator('#reset-exhibit').click();ok('Reset clears selected run',page.locator('#memory-retention').input_value()=='80' and 'No record is selected' in page.locator('#exhibit-status').inner_text())
 load(page,'/luna/');ok('Reduced-motion artwork begins paused',page.locator('[data-pause-art]').get_attribute('aria-pressed')=='true')
 page.locator('[data-pause-art]').click();ok('Explicit play override works',page.locator('[data-pause-art]').get_attribute('aria-pressed')=='false');page.locator('[data-pause-art]').click()
 # Refreshed captures, from the final source.
 for route,name in [('/','home'),('/research/','research'),('/luna/','luna'),('/journal/','journal'),('/observatory/','observatory')]:
  page.set_viewport_size({'width':1440,'height':1050});load(page,route)
  if route=='/observatory/':page.locator('#perturb-exhibit').click()
  page.evaluate("document.activeElement?.blur(); window.scrollTo(0,0)");page.wait_for_timeout(80)
  page.screenshot(path=str(SHOTS/(name+'-desktop.png')),full_page=True)
  if route=='/':page.screenshot(path=str(SHOTS/'hero-desktop.png'))
  page.set_viewport_size({'width':390,'height':844});load(page,route)
  page.evaluate("document.activeElement?.blur(); window.scrollTo(0,0)");page.wait_for_timeout(80)
  page.screenshot(path=str(SHOTS/(name+'-mobile.png')),full_page=True)
  if route=='/':page.screenshot(path=str(SHOTS/'hero-mobile.png'))
 ok('No JavaScript runtime errors',not errors,str(errors))
 browser.close()
report={'mode':'offline Chromium with injected built assets; no hosted or network test','checks':checks,'passed':len(checks),'failed':0,'pages_checked':len(routes),'viewports':[390,1440]}
(ROOT/'private/browser-report.json').write_text(json.dumps(report,indent=2))
print(f'{len(checks)} checks passed; {len(routes)} pages checked at 390 and 1440 px; zero page errors.')
