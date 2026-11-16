const {chromium,expect}=require('../frontend/node_modules/@playwright/test');
const path=require('node:path');
(async()=>{
 const b=await chromium.launch({channel:'msedge',headless:true});
 const p=await b.newPage({viewport:{width:1920,height:1080},reducedMotion:'reduce'});
 await p.goto('http://127.0.0.1:8007/logistics');await p.evaluate(()=>document.fonts.ready);
 await p.getByRole('button',{name:'暴雨风险 主走廊降雨增强',exact:true}).click();
 await p.getByRole('button',{name:'运行风险分析',exact:true}).click();
 await expect(p.locator('.risk-number')).toContainText('47.15');
 await p.locator('.logistics-top').screenshot({path:path.resolve('docs/phase4_6/assets/network_wide.png')});
 await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
