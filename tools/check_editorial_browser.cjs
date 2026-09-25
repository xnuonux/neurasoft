// Run with an installed Playwright module; no downloads or installs.
const {chromium} = require(process.env.NEURASOFT_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const origin = process.argv[2] || 'http://127.0.0.1:8742';
const registry = fs.readdirSync(path.resolve(__dirname,'../content/articles')).filter(n=>n.endsWith('.json')).map(n=>JSON.parse(fs.readFileSync(path.resolve(__dirname,'../content/articles',n),'utf8'))).filter(a=>a.status==='publish' && fs.existsSync(path.resolve(__dirname,'../dist/articles',a.slug,'index.html'))).sort((a,b)=>b.date.localeCompare(a.date)||(b.published_at||b.date).localeCompare(a.published_at||a.date)||b.slug.localeCompare(a.slug));
assert(registry.length,'At least one published article is required');
const articleRoute='/articles/'+registry[0].slug+'/';
const output = path.resolve(__dirname, '../artifacts/editorial-browser');
fs.mkdirSync(output,{recursive:true});
(async () => {
  const browser = await chromium.launch({headless:true});
  const errors=[]; const results=[];
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    page.on('pageerror',e=>errors.push(e.message));
    for (const width of [1440,390]) {
      await page.setViewportSize({width,height:1000});
      for (const route of ['/', '/articles/', articleRoute]) {
        const response=await page.goto(origin+route,{waitUntil:'networkidle'});
        assert.equal(response.status(),200);
        assert.equal(await page.locator('h1').count(),1);
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        if(route==='/') {
          await page.locator('.dispatch-feature').scrollIntoViewIfNeeded();
          await page.locator('.dispatch-feature').screenshot({path:path.join(output,`homepage-feature-${width}.png`)});
        }
        if(route===articleRoute) {
          for(const img of await page.locator('main img').all()) {
            await img.scrollIntoViewIfNeeded();
            await img.evaluate(i=>i.decode());
            assert(await img.evaluate(i=>i.naturalWidth>0 && !!i.alt));
          }
          await page.evaluate(()=>scrollTo(0,0));
          await page.screenshot({path:path.join(output,`article-${width}.png`),fullPage:true});
          assert.equal(await page.locator('figure').count(),registry[0].sections.filter(s=>'figure' in s).length);
          await page.locator('a[href="#source-1"]').first().click();
          assert(page.url().endsWith('#source-1'));
        }
        results.push({width,route,passed:true});
      }
    }
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(origin);
    await page.locator('[data-search-open]').click();
    await page.locator('#site-search').fill(registry[0].title);
    await page.locator(`.search-result[href="${articleRoute}"]`).waitFor();
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({origin,results,search:true,pageErrors:errors},null,2));
    console.log(JSON.stringify({routesAndSizes:results.length,search:true,pageErrors:errors}));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
