const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const fs=require('node:fs/promises'),path=require('node:path');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'docs/phase4_6'),BASE='http://127.0.0.1:8006';
const round=process.argv[2]||'round1';
(async()=>{
 await fs.mkdir(path.join(OUT,round),{recursive:true});
 const b=await chromium.launch({channel:'msedge',headless:true});
 const results=[],errors=[],external=[];
 const c=await b.newContext({reducedMotion:'reduce'});
 const p=await c.newPage();
 p.on('pageerror',e=>errors.push(e.message));
 p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 p.on('request',r=>{if(!r.url().startsWith(BASE)&&!r.url().startsWith('data:'))external.push(r.url())});
 await p.request.post(BASE+'/api/demo/reset');
 for(const [w,h] of [[1920,1080],[1440,900],[1366,768],[390,844]]){
  await p.setViewportSize({width:w,height:h});
  for(const route of ['/','/growth','/logistics','/demo','/about']){
   const slug=route==='/'?'home':route.slice(1);
   await p.goto(BASE+route);await p.locator('h1').waitFor();await p.evaluate(()=>document.fonts.ready);
   await p.waitForTimeout(500);
   const check=async(name)=>{
    const d=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,font:document.fonts.check('14px "SkyRoute User"'),family:getComputedStyle(document.body).fontFamily,faces:[...document.fonts].map(f=>({family:f.family,status:f.status})),tables:[...document.querySelectorAll('.table-scroll')].map(el=>({client:el.clientWidth,scroll:el.scrollWidth}))}));
    expect(d.scroll,name+' overflow').toBeLessThanOrEqual(w);expect(d.font).toBeTruthy();expect(d.faces.some(f=>f.family==='SkyRoute User'&&f.status==='loaded')).toBeTruthy();
    await p.screenshot({path:path.join(OUT,round,`${w}-${name}.png`),fullPage:true});
    results.push({viewport:{w,h},page:name,...d});
   };
   await check(slug);
   if(route==='/growth'){
    await p.getByRole('tab',{name:'预算与增长模型',exact:true}).click();await expect(p.locator('.funnel-numbers')).toContainText('1,440');await check('growth-model');
    await p.getByRole('tab',{name:'实验与执行',exact:true}).click();await p.getByRole('button',{name:'计算实验差异',exact:true}).click();await expect(p.locator('.experiment-result')).toContainText('0.18821');await check('growth-execution');
    await p.getByRole('button',{name:'新增任务',exact:true}).click();await check('task-modal');
    const first=p.getByRole('button',{name:'关闭弹窗',exact:true});await expect(first).toBeFocused();await p.keyboard.press('Shift+Tab');expect(await p.evaluate(()=>!!document.activeElement.closest('[role=dialog]'))).toBeTruthy();await p.keyboard.press('Escape');await expect(p.getByRole('dialog')).toHaveCount(0);
   }
   if(route==='/logistics'){
    await p.getByRole('button',{name:'运行风险分析',exact:true}).click();await expect(p.locator('.recommended-row')).toBeVisible();await check('logistics-decision');
    await p.getByRole('button',{name:'生成分析解释',exact:true}).click();await expect(p.locator('.explanation')).toContainText('规则模式');
    await p.getByRole('button',{name:'查看决策报告',exact:true}).click();await check('decision-report');await p.keyboard.press('Escape');
    await p.getByRole('button',{name:'运行情景仿真',exact:true}).click();await expect(p.getByRole('heading',{name:'逐订单对比',exact:true})).toBeVisible();await check('simulation');
    await p.getByRole('tab',{name:'运输订单管理',exact:true}).click();await check('orders');await p.getByRole('button',{name:'新增订单',exact:true}).click();await check('order-modal');await p.keyboard.press('Escape');
   }
   if(route==='/about'){
    await expect(p.locator('.methods-grid > .card')).toHaveCount(3);
    await expect(p.getByText('官方信息核实情况',{exact:true})).toHaveCount(0);
    await expect(p.getByText('打开用户提供的赛事入口',{exact:true})).toHaveCount(0);
    await expect(p.locator('.methods-grid + .notice')).toHaveCount(0);
   }
   if(route==='/demo'){
    await p.getByRole('button',{name:'开始计时',exact:true}).click();await expect(p.locator('.demo-time')).toContainText('00:01');await p.getByRole('button',{name:'暂停计时',exact:true}).click();await p.getByRole('button',{name:'归零',exact:true}).click();await expect(p.locator('.demo-time')).toContainText('00:00');
   }
  }
 }
 expect(errors).toEqual([]);expect(external).toEqual([]);
 await fs.writeFile(path.join(OUT,`${round}-checks.json`),JSON.stringify({results,errors,external},null,2));
 await b.close();console.log('PASS',round,results.length,'views');
})().catch(e=>{console.error(e);process.exit(1)});
