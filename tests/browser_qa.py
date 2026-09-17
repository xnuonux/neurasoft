"""Offline Chromium QA. Assets are injected from dist; no hosted deployment is implied."""
from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SHOTS=ROOT.parent/'neurasoft-preview'
SHOTS.mkdir(exist_ok=True)

def load(page,route='/'):
 path=DIST/'index.html' if route=='/' else DIST/route.strip('/')/'index.html'
 page.goto('about:blank')
 content=path.read_text(encoding='utf-8')
 content=re.sub(r'<link\b[^>]+>', '', content)
 content=re.sub(r'<script\b.*?</script>', '', content, flags=re.S)
 page.set_content(content,wait_until='domcontentloaded')
 page.add_style_tag(content=(DIST/'assets/site.css').read_text(encoding='utf-8'))
 index=json.loads((DIST/'assets/search-index.json').read_text(encoding='utf-8'))
 page.evaluate('index => {window.fetch = async url => {if(url!=="/assets/search-index.json") throw new Error("Unexpected network request"); return {ok:true,json:async()=>index};};}',index)
 page.add_script_tag(content=(DIST/'assets/site.js').read_text(encoding='utf-8'))
 page.wait_for_timeout(160)

if __name__=='__main__':
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=b.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1,reduced_motion='reduce')
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  load(page)
  page.screenshot(path=str(SHOTS/'home-desktop.png'),full_page=True)
  page.screenshot(path=str(SHOTS/'hero-desktop.png'))
  print('desktop overflow',page.evaluate('document.documentElement.scrollWidth > innerWidth'),'errors',errors)
  page.set_viewport_size({'width':390,'height':844});load(page)
  page.screenshot(path=str(SHOTS/'home-mobile.png'),full_page=True)
  print('mobile overflow',page.evaluate('document.documentElement.scrollWidth > innerWidth'))
  load(page,'/observatory/');page.locator('#run-exhibit').click();page.locator('#perturb-exhibit').click()
  page.screenshot(path=str(SHOTS/'observatory-mobile.png'),full_page=True)
  print(page.locator('#exhibit-status').inner_text(),'errors',errors)
  b.close()
