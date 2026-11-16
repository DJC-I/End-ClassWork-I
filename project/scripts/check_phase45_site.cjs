const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const fs=require('node:fs/promises');const path=require('node:path');
const ROOT=path.resolve(__dirname,'..'),QA=path.join(ROOT,'docs/phase4_5');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});const results=[];
 try{for(const [label,width,height] of [['desktop',1920,1080],['tablet',1024,768],['mobile',390,844]]){
  const page=await browser.newPage({viewport:{width,height}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8005/about');
  await page.getByRole('heading',{name:'技术与数据流',exact:true}).waitFor();
  await expect(page.locator('.methods-grid > .card')).toHaveCount(3);
  for(const name of ['技术与数据流','运输图与天气假设','模型与统计方法'])await expect(page.getByRole('heading',{name,exact:true})).toBeVisible();
  for(const removed of ['官方信息核实情况','打开用户提供的赛事入口','第一阶段只交付本地网站'])await expect(page.getByText(removed,{exact:false})).toHaveCount(0);
  await expect(page.locator('.page > .notice')).toHaveCount(0);
  await expect(page.locator('.global-notice')).toBeVisible();
  await expect(page.getByText('风险分是规则量表，不是事故概率。',{exact:false})).toBeVisible();
  await expect(page.locator('.methods-grid a[href="/docs"]')).toBeVisible();
  const layout=await page.locator('.methods-grid').evaluate(el=>{
   const grid=el.getBoundingClientRect(),cards=Array.from(el.children).map(c=>{const r=c.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};});
   return {grid:{x:grid.x,width:grid.width,bottom:grid.bottom},cards,pageWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,columns:getComputedStyle(el).gridTemplateColumns};
  });
  expect(layout.scrollWidth).toBeLessThanOrEqual(width+1);
  const last=layout.cards[2];expect(Math.abs(last.width-layout.grid.width)).toBeLessThan(2);
  expect(Math.abs(last.bottom-layout.grid.bottom)).toBeLessThan(2);
  for(const c of layout.cards){expect(c.x).toBeGreaterThanOrEqual(0);expect(c.right).toBeLessThanOrEqual(width+1);}
  if(label==='desktop'){expect(Math.abs(layout.cards[0].y-layout.cards[1].y)).toBeLessThan(2);expect(last.y-layout.cards[0].bottom).toBeLessThan(35);}
  if(label==='mobile')for(let i=1;i<3;i++){expect(layout.cards[i].y).toBeGreaterThan(layout.cards[i-1].y);expect(layout.cards[i].y-layout.cards[i-1].bottom).toBeLessThan(35);}
  await page.screenshot({path:path.join(QA,'about-'+label+'.png'),fullPage:true});
  expect(errors).toEqual([]);results.push({viewport:{width,height},layout,errors,removed_nodes_absent:true,remaining_cards:3});await page.close();
 }}finally{await browser.close();}
 await fs.writeFile(path.join(QA,'site-check.json'),JSON.stringify({passed:true,browser:'Microsoft Edge',base:'http://127.0.0.1:8005',production_build:true,results},null,2));console.log('Desktop/tablet/mobile source page checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
