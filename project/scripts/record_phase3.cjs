// Actual Edge website recordings. No response mocks or altered website content.
const { chromium, expect } = require('../frontend/node_modules/@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const { performance } = require('node:perf_hooks');
const ROOT = path.resolve(__dirname, '..');
const QA = path.join(ROOT, 'docs/phase3');
const WORK = path.join(ROOT, '.tools/phase3');
const BASE = 'http://127.0.0.1:8000';
const selected = process.argv[2];
let video, scene, page, context, browser;
let evidence = { base: BASE, browser: 'Microsoft Edge via Playwright', viewport: { width:1920,height:900 }, mocked_responses:false, scenes:[], errors:[], external_requests:[], responses:[] };
const card = name => page.locator('section.card').filter({has:page.getByRole('heading',{name,exact:true})});
const pause = ms => page.waitForTimeout(ms);
async function focus(locator, offset=28) {
  await locator.first().waitFor({state:'visible'});
  await locator.first().evaluate((el, off)=>window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-off,behavior:'smooth'}), offset);
  await pause(700);
  await page.mouse.move(1750, 860);
}
async function click(locator) { await locator.hover(); await pause(300); await locator.click(); }
async function model() { await page.getByRole('tab',{name:'预算与增长模型',exact:true}).click(); await expect(page.locator('.funnel-numbers')).toContainText('12,000'); }
async function experiments() { await page.getByRole('tab',{name:'实验与执行',exact:true}).click(); }
async function analyze() {
  await page.getByRole('button',{name:'运行风险分析',exact:true}).click();
  await expect(page.locator('.risk-number')).toContainText('47.15');
}
async function scenario(name) {
  await page.getByRole('button',{name}).click();
  await expect(page.getByRole('button',{name})).toBeEnabled();
}
async function simulate() {
  const response = page.waitForResponse(r=>r.url().endsWith('/api/simulation')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'运行情景仿真',exact:true}).click();
  const r = await response; expect(r.ok()).toBeTruthy();
  await expect(page.getByRole('heading',{name:'逐订单对比',exact:true})).toBeVisible();
  await focus(page.locator('.grid.two').filter({has:page.getByRole('heading',{name:'准时与延误',exact:true})}));
  return r.json();
}
async function setup() {
  await page.goto(BASE + (video.id==='growth'?'/growth':'/logistics'));
  await expect(page.locator('.stat').first()).not.toContainText('—');
  await pause(750);
  if(video.id==='growth') {
    if(scene.id==='position') await focus(card('先把平台价值讲清楚'));
    if(scene.id==='personas') await focus(page.getByRole('heading',{name:'四类用户，四条触达路径',exact:true}));
    if(scene.id==='strategy') await focus(page.getByRole('heading',{name:'完整运营策略链',exact:true}));
    if(scene.id==='channels') await focus(card('创新玩法与AI工具'));
    if(['funnel','budget','adjust'].includes(scene.id)) await model();
    if(scene.id==='funnel') { await expect(page.locator('.funnel-numbers')).toContainText('1,440'); await focus(page.locator('.growth-model')); }
    if(scene.id==='budget') { await expect(page.locator('.stat').first()).toContainText('3,000'); await focus(card('推广渠道与预算分配')); }
    if(scene.id==='adjust') await focus(card('推广渠道与预算分配'));
    if(['experiment','execution','report'].includes(scene.id)) await experiments();
    if(scene.id==='experiment') await focus(card('A/B实验计算器'));
    if(scene.id==='execution') await focus(card('运营排期与执行看板'));
  } else {
    if(scene.id==='overview') await expect(page.locator('.risk-order-list button').first()).toBeVisible();
    if(scene.id==='orders') { await page.getByRole('tab',{name:'运输订单管理',exact:true}).click(); await focus(card('运输订单台账')); }
    if(scene.id==='weather') await focus(page.locator('.logistics-top'));
    if(scene.id==='risk') { await focus(page.getByRole('button',{name:'运行风险分析',exact:true})); }
    if(['plans','agent','report'].includes(scene.id)) {
      await analyze();
      await focus(card(scene.id==='plans'?'四类应对策略，逐项对比':scene.id==='agent'?'分析智能体：有流程，也有记录':'当前权重下的推荐'));
    }
    if(['rain','snow','normal'].includes(scene.id)) {
      if(scene.id==='rain') await scenario('暴雨风险 主走廊降雨增强');
      if(scene.id==='snow') await scenario('暴雪与大风 多节点复合影响');
      if(scene.id==='normal') await scenario('正常天气 晴朗 / 通行稳定');
    }
    if(scene.id==='limits') {
      await page.getByRole('link',{name:'方法与数据来源 Method & sources'}).click();
      await pause(500);
    }
  }
  await page.mouse.move(1750,860);
  await pause(450);
}
async function action() {
  if(video.id==='growth') {
    if(scene.id==='position') { await pause(1800); await focus(card('先把平台价值讲清楚')); }
    if(scene.id==='personas') { await pause(3500); await page.mouse.wheel(0,170); await pause(900); }
    if(scene.id==='strategy') { await pause(4000); await page.mouse.wheel(0,230); await pause(900); }
    if(scene.id==='channels') { await pause(3500); await page.mouse.wheel(0,140); await pause(900); }
    if(scene.id==='funnel') await pause(3500);
    if(scene.id==='budget') { await pause(5000); await focus(page.locator('.stats').first()); }
    if(scene.id==='adjust') {
      await pause(500);
      await click(page.getByLabel('校园社群预算',{exact:true}));
      await page.getByLabel('校园社群预算',{exact:true}).fill('900');
      await pause(1300);
      await focus(page.locator('.growth-model'));
      await click(page.getByLabel('访问率',{exact:true}));
      await page.getByLabel('访问率',{exact:true}).fill('20');
      await expect(page.locator('.funnel-numbers')).toContainText('2,400');
      await expect(page.locator('.stat').first()).toContainText('3,300');
      await pause(1700);
      await page.getByRole('button',{name:'保存参数',exact:true}).click();
      await expect(page.getByRole('status')).toContainText('已保存');
      await focus(page.locator('.stats').first());
    }
    if(scene.id==='experiment') {
      await pause(400);
      await click(page.getByRole('button',{name:'计算实验差异',exact:true}));
      await expect(page.locator('.experiment-result')).toContainText('0.18821');
      await expect(page.locator('.experiment-result')).toContainText('当前没有足够证据');
      await focus(card('A/B实验计算器'));
    }
    if(scene.id==='execution') { await pause(3500); await focus(card('从假设到证据的实验设计')); await pause(4000); await focus(card('运营排期与执行看板')); }
    if(scene.id==='report') {
      await pause(350);
      await click(page.getByRole('button',{name:'生成运营报告',exact:true}));
      await expect(page.getByRole('dialog')).toContainText('假设预算');
      await pause(2500);
      const download=page.waitForEvent('download');
      await page.getByRole('link',{name:'下载报告',exact:true}).click();
      await (await download).saveAs(path.join(QA,'growth-recorded-report.md'));
      await pause(1000);
      await page.getByRole('dialog').evaluate(el=>el.scrollTo({top:220,behavior:'smooth'}));
    }
  } else {
    if(scene.id==='overview') { await pause(4500); await focus(card('受影响订单与节点')); }
    if(scene.id==='orders') {
      await pause(400); await click(page.getByLabel('查询订单',{exact:true})); await page.getByLabel('查询订单',{exact:true}).fill('SR-001');
      await expect(page.getByRole('row').filter({hasText:'SR-001'})).toContainText('13:35');
      await pause(3500); await page.getByLabel('查询订单',{exact:true}).fill(''); await pause(500);
    }
    if(scene.id==='weather') { await pause(5000); await page.mouse.wheel(0,150); await pause(700); }
    if(scene.id==='risk') { await pause(400); await click(page.getByRole('button',{name:'运行风险分析',exact:true})); await expect(page.locator('.risk-number')).toContainText('47.15'); await focus(page.locator('.risk-grid')); }
    if(scene.id==='plans') {
      await expect(page.locator('.recommended-row')).toContainText('1,242');
      await pause(4000); await focus(card('当前权重下的推荐')); await pause(2500); await focus(card('四类应对策略，逐项对比'));
    }
    if(scene.id==='agent') {
      await pause(1000); await click(page.getByRole('button',{name:'生成分析解释',exact:true}));
      await expect(page.locator('.explanation')).toContainText('规则模式'); await pause(1700);
      await focus(card('分析智能体：有流程，也有记录'));
    }
    if(scene.id==='report') {
      await pause(350); await click(page.getByRole('button',{name:'查看决策报告',exact:true}));
      await expect(page.getByRole('dialog')).toContainText('方案对比'); await pause(2500);
      const dl=page.waitForEvent('download'); await page.getByRole('link',{name:'下载报告',exact:true}).click();
      await (await dl).saveAs(path.join(QA,'logistics-recorded-report.md'));
      await page.getByRole('dialog').evaluate(el=>el.scrollTo({top:530,behavior:'smooth'}));
    }
    if(['rain','snow','normal'].includes(scene.id)) {
      await pause(500); const sim=await simulate();
      const expected={rain:[38.89,100,7360.68,7160.35],snow:[22.22,66.67,7574.93,7555.6],normal:[100,100,6740,6808]}[scene.id];
      expect([sim.before.on_time_rate,sim.after.on_time_rate,sim.before.total_cost,sim.after.total_cost]).toEqual(expected);
      await fs.writeFile(path.join(QA,`${scene.id}-recorded-simulation.json`),JSON.stringify(sim,null,2));
    }
    if(scene.id==='limits') { await pause(3000); await page.mouse.wheel(0,470); await pause(1000); }
  }
  await page.mouse.move(1750,860);
}
(async()=>{
  const board=JSON.parse(await fs.readFile(path.join(QA,'timeline.json'),'utf8'));
  video=board.videos.find(v=>v.id===selected); if(!video)throw new Error('Pass growth or logistics');
  browser=await chromium.launch({channel:'msedge',headless:true});
  try {
    for(scene of video.scenes) {
      context=await browser.newContext({viewport:{width:1920,height:900},deviceScaleFactor:1,recordVideo:{dir:path.join(WORK,'raw',video.id),size:{width:1920,height:900}},reducedMotion:'reduce'});
      page=await context.newPage();
      page.on('pageerror',e=>evidence.errors.push({scene:scene.id,message:e.message}));
      page.on('console',m=>{if(m.type()==='error')evidence.errors.push({scene:scene.id,message:m.text()});});
      page.on('request',r=>{if(!r.url().startsWith(BASE)&&!r.url().startsWith('data:'))evidence.external_requests.push(r.url());});
      page.on('response',async r=>{if(r.url().includes('/api/')&&r.status()>=400)evidence.errors.push({scene:scene.id,status:r.status(),url:r.url()});});
      await setup();
      const started=performance.now();
      await action();
      const spent=(performance.now()-started)/1000;
      if(spent>scene.duration-.5)throw new Error(`${scene.id} action too long ${spent}/${scene.duration}`);
      await pause((scene.duration-spent)*1000);
      await page.screenshot({path:path.join(QA,`${video.id}-${scene.id}.png`)});
      const recording=page.video();
      const elapsed=(performance.now()-started)/1000;
      const body=await page.locator('body').innerText();
      await context.close();
      const raw=await recording.path();
      evidence.scenes.push({id:scene.id,title:scene.title,raw:path.relative(ROOT,raw).replaceAll('\\','/'),duration:scene.duration,tail_seconds:elapsed,body,action_seconds:spent});
      await fs.writeFile(path.join(QA,`${video.id}-recording.json`),JSON.stringify(evidence,null,2));
      console.log(`${video.id}/${scene.id}: ${scene.duration.toFixed(2)}s recorded`);
    }
    expect(evidence.errors).toEqual([]); expect(evidence.external_requests).toEqual([]);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
