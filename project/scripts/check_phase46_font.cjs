const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const fs=require('node:fs/promises');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const p=await browser.newPage({viewport:{width:1366,height:768},reducedMotion:'reduce'});
 const cdp=await p.context().newCDPSession(p);await cdp.send('DOM.enable');await cdp.send('CSS.enable');
 const pages=[],text=[];
 for(const route of ['/','/growth','/logistics','/demo','/about']){
  await p.goto('http://127.0.0.1:8007'+route);await p.evaluate(()=>document.fonts.ready);
  await expect(p.locator('h1')).toBeVisible();
  const {root}=await cdp.send('DOM.getDocument');
  const {nodeId}=await cdp.send('DOM.querySelector',{nodeId:root.nodeId,selector:'h1'});
  const {fonts}=await cdp.send('CSS.getPlatformFontsForNode',{nodeId});
  expect(fonts.some(f=>f.isCustomFont&&f.glyphCount>0)).toBeTruthy();
  text.push(await p.locator('body').innerText());pages.push({route,heading_fonts:fonts});
 }
 await p.goto('http://127.0.0.1:8007/demo');
 await p.getByRole('button',{name:'进入全屏',exact:true}).click();
 await expect.poll(()=>p.evaluate(()=>!!document.fullscreenElement)).toBe(true);
 await p.evaluate(()=>document.exitFullscreen());
 await p.setViewportSize({width:390,height:844});
 await p.goto('http://127.0.0.1:8007/logistics');
 const menu=p.getByRole('button',{name:'切换导航',exact:true});
 await menu.click();await expect(menu).toHaveAttribute('aria-expanded','true');
 await p.getByRole('link',{name:'增长运营工作台 Growth strategy',exact:true}).click();
 await expect(p).toHaveURL(/growth$/);await expect(menu).toHaveAttribute('aria-expanded','false');
 await p.goto('http://127.0.0.1:8007/logistics');
 const map=p.locator('.network-wrap');
 await map.scrollIntoViewIfNeeded();await map.focus();await p.keyboard.press('ArrowRight');
 await expect.poll(()=>map.evaluate(e=>e.scrollLeft)).toBeGreaterThan(0);
 const mapScroll=await map.evaluate(e=>({width:e.clientWidth,scrollWidth:e.scrollWidth,left:e.scrollLeft}));
 expect(mapScroll.scrollWidth).toBeGreaterThan(mapScroll.width);expect(mapScroll.left).toBeGreaterThan(0);
 await fs.writeFile('docs/phase4_6/font-browser.json',JSON.stringify({passed:true,pages,fullscreen:true,mobile_navigation:true,keyboard_map_scroll:mapScroll,visible_text:text.join('\n')},null,2));
 await browser.close();console.log('Actual custom font glyphs, fullscreen, mobile navigation and keyboard map scroll passed');
})().catch(e=>{console.error(e);process.exit(1)});
