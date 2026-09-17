"""Exercise the full embedded HTML in Chromium; no network or file-navigation claim."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
preview=ROOT.parent/'NEURASOFT_INTERACTIVE_PREVIEW.html'
checks=[]
def check(label,value):
 checks.append({'name':label,'passed':bool(value)})
 if not value:raise AssertionError(label)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 p=b.new_page(viewport={'width':1440,'height':960},reduced_motion='reduce')
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(preview.read_text(encoding='utf-8'),wait_until='load');f=p.frame_locator('#site-frame')
 check('Portable home','For what a mind' in f.locator('h1').inner_text())
 f.locator('a[href="/thesis/"]').first.click();p.wait_for_timeout(180)
 check('Portable thesis navigation','future of its own' in f.locator('h1').inner_text())
 f.locator('[data-search-open]').click();f.locator('#site-search').fill('robotics');p.wait_for_timeout(100)
 check('Search includes new pages',f.locator('.search-result').count()>0)
 f.locator('.search-close').click()
 p.evaluate("location.hash='/observatory/choice/'");p.wait_for_timeout(200)
 for button,status,count in [
 ('choice-act','has not been recovered','0'),('choice-recover','No action occurred','0'),
 ('choice-act','no unused authorization','0'),('choice-authorize','Still no action','0'),
 ('choice-authorize','not multiplied','0'),('choice-defer','Deferred','0'),
 ('choice-act','completed','1'),('choice-act','no unused authorization','1'),
 ('choice-restart','no action replayed','1'),('choice-authorize','Still no action','1'),
 ('choice-act','completed','2'),('choice-reset','New study','0')]:
  f.locator('#'+button).click();check(button+' '+status,status in f.locator('#choice-status').inner_text());check(button+' count '+count,f.locator('#choice-count').inner_text()==count)
 for route in ['/humanity/','/consciousness/','/digital-life/','/landscape/','/findings/','/reading-room/','/ideas/','/relationships/','/voices/','/outlook/']:
  p.evaluate('(r)=>location.hash=r',route);p.wait_for_timeout(140)
  check('Portable '+route,f.locator('h1').is_visible())
 p.set_viewport_size({'width':390,'height':844});p.evaluate("location.hash='/'");p.wait_for_timeout(200)
 check('Portable mobile no overflow',p.frames[1].evaluate('document.documentElement.scrollWidth<=innerWidth'))
 f.locator('.menu-toggle').click();check('Portable mobile navigation',f.locator('#primary-nav').is_visible());p.keyboard.press('Escape')
 p.screenshot(path='/mnt/data/NEURASOFT_RESEARCH_MOBILE.png',full_page=False)
 p.set_viewport_size({'width':1440,'height':1020});p.evaluate("location.hash='/thesis/'");p.wait_for_timeout(100);p.evaluate("location.hash='/'");p.wait_for_timeout(160)
 p.screenshot(path='/mnt/data/NEURASOFT_RESEARCH_HOMEPAGE.png',full_page=False)
 check('No runtime errors',not errors)
 b.close()
report={'mode':'Embedded preview HTML injected into Chromium; file URL navigation is environment-blocked and was not verified','checks':checks,'passed':len(checks),'failed':0,'runtime_errors':errors}
(ROOT/'private/expanded-preview-checks.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
print(len(checks),'additional preview/interaction checks passed')
