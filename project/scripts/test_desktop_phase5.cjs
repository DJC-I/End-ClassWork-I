/* Real packaged Electron tests. Test data is isolated; no developer DB is used. */
const { _electron, expect } = require('../frontend/node_modules/@playwright/test');
const fs = require('node:fs/promises'), path = require('node:path');
const ROOT = path.resolve(__dirname, '..'), OUT = path.join(ROOT, 'docs/phase5');
const executable = process.argv[2] ? path.resolve(process.argv[2]) : path.join(ROOT, '.tools/phase5/electron-dist/win-unpacked/SkyRoute AI.exe');
const userRoot = path.join(ROOT, '.tools/phase5/桌面测试 空格路径');
const checks = [], errors = [], external = [];
async function launch() {
  const env = { ...process.env, LOCALAPPDATA: userRoot, PATH: path.join(process.env.SystemRoot, 'System32') };
  delete env.OPENAI_API_KEY; delete env.OPENAI_BASE_URL; delete env.OPENAI_MODEL;
  const app = await _electron.launch({ executablePath: executable, env, timeout: 60000 });
  const page = await app.firstWindow();
  page.on('pageerror', e => errors.push(e.message));
  await page.waitForURL('http://127.0.0.1:*/**');
  await page.locator('h1').waitFor();
  const base = new URL(page.url()).origin;
  page.on('request', r => { if (!r.url().startsWith(base + '/') && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) external.push(new URL(r.url()).protocol); });
  const go = route => page.goto(base + route);
  const api = (route, method = 'GET', data) => page.evaluate(async ({ route, method, data }) => {
    const response = await fetch('/api' + route, { method, headers: { 'Content-Type': 'application/json' }, body: data === undefined ? undefined : JSON.stringify(data) });
    return { status: response.status, data: await response.json() };
  }, { route, method, data });
  return { app, page, base, go, api };
}
const mark = name => checks.push({ name, passed: true });
(async () => {
  await fs.mkdir(OUT, { recursive: true });
  let { app, page, go, api } = await launch();
  try {
    await api('/demo/reset', 'POST'); await go('/');
    await expect(page.locator('h1')).toContainText('把复杂风险'); mark('首页真实图形窗口');
    for (const route of ['/', '/growth', '/logistics', '/demo', '/about']) {
      await go(route); await page.evaluate(() => document.fonts.ready);
      expect(await page.evaluate(() => document.fonts.check('16px "SkyRoute User"'))).toBe(true);
      const cdp = await page.context().newCDPSession(page);
      await cdp.send('DOM.enable');
      await cdp.send('CSS.enable');
      const document = await cdp.send('DOM.getDocument');
      const node = await cdp.send('DOM.querySelector', { nodeId: document.root.nodeId, selector: 'h1' });
      const fonts = await cdp.send('CSS.getPlatformFontsForNode', { nodeId: node.nodeId });
      expect(fonts.fonts.some(f => f.isCustomFont && f.familyName === 'iOS27苹方HK' && f.glyphCount > 0)).toBe(true);
      await cdp.detach();
      expect(await page.locator('svg').count()).toBeGreaterThan(0);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      mark(route + ' 路由/字体/图形/无整页溢出');
    }
    await expect(page.locator('.methods-grid > .card')).toHaveCount(3);
    await expect(page.getByText('官方信息核实情况', { exact: true })).toHaveCount(0);
    await expect(page.locator('.methods-grid + .notice')).toHaveCount(0); mark('两处过时组件未恢复');
    await expect(page.getByText('桌面版本关闭API调试入口。', { exact: false })).toBeVisible();
    await expect(page.locator('a[href="/docs"]')).toHaveCount(0); mark('桌面界面不提供失效调试链接');
    await go('/growth'); await page.getByRole('tab', { name: '预算与增长模型' }).click();
    await page.getByLabel('校园社群预算', { exact: true }).fill('900');
    await page.getByLabel('访问率', { exact: true }).fill('20');
    await expect(page.locator('.stat').first()).toContainText('3,300');
    await expect(page.locator('.funnel-numbers')).toContainText('2,400');
    await page.getByRole('button', { name: '保存参数', exact: true }).click();
    await expect(page.getByRole('status')).toContainText('已保存'); mark('预算/漏斗计算与保存');
    await page.screenshot({ path: path.join(OUT, 'desktop-growth.png') });
    await page.getByRole('tab', { name: '实验与执行' }).click();
    await page.getByRole('button', { name: '计算实验差异', exact: true }).click();
    await expect(page.locator('.experiment-result')).toContainText('0.18821'); mark('A/B真实计算');
    await page.getByRole('button', { name: '生成运营报告', exact: true }).click();
    await expect(page.getByRole('dialog')).toContainText('假设预算');
    await page.keyboard.press('Escape'); mark('运营报告与弹窗');
    await go('/logistics');
    for (const [button, scenario] of [['正常天气 晴朗 / 通行稳定', 'normal'], ['暴雨风险 主走廊降雨增强', 'rain'], ['暴雪与大风 多节点复合影响', 'snow']]) {
      await page.getByRole('button', { name: button, exact: true }).click();
      await page.getByRole('button', { name: '运行风险分析', exact: true }).click();
      await expect(page.locator('.recommended-row')).toBeVisible();
      const computed = (await api('/analysis', 'POST', { order_id: 'SR-001', scenario_id: scenario })).data;
      await expect(page.locator('.recommended-row')).toContainText(computed.recommendation.name);
      if (scenario === 'rain') {
        await expect(page.locator('.risk-number')).toContainText('47.15');
        await expect(page.locator('.recommended-row')).toContainText('1,242');
        await page.screenshot({ path: path.join(OUT, 'desktop-logistics.png') });
      }
      await page.getByRole('button', { name: '生成分析解释', exact: true }).click();
      await expect(page.locator('.explanation')).toContainText('规则模式');
      await page.getByRole('button', { name: '运行情景仿真', exact: true }).click();
      await expect(page.getByRole('heading', { name: '逐订单对比', exact: true })).toBeVisible();
      const result = (await api('/simulation', 'POST', { scenario_id: scenario })).data;
      expect(Number.isFinite(result.after.on_time_rate)).toBe(true);
      await page.getByRole('tab', { name: '风险与方案', exact: true }).click();
      mark(scenario + ' 风险/四方案/规则解释/仿真');
    }
    await page.getByRole('button', { name: '运行风险分析', exact: true }).click();
    await page.getByRole('button', { name: '查看决策报告', exact: true }).click();
    await expect(page.getByRole('dialog')).toContainText('SR-001');
    await page.keyboard.press('Escape'); mark('决策报告真实快照');
    await page.getByRole('tab', { name: '运输订单管理' }).click();
    await page.getByRole('button', { name: '新增订单', exact: true }).click();
    await page.getByRole('dialog').getByLabel('订单编号', { exact: true }).fill('DESKTOP-ORDER');
    await page.getByRole('dialog').getByLabel('重量', { exact: true }).fill('9');
    await page.getByRole('button', { name: '校验并保存订单' }).click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    const order = (await api('/orders/DESKTOP-ORDER')).data;
    order.base_cost = 1400;
    expect((await api('/orders/DESKTOP-ORDER', 'PUT', order)).status).toBe(200);
    expect((await api('/orders/DESKTOP-ORDER')).data.base_cost).toBe(1400);
    mark('订单真实新增/读取/修改');
    await go('/demo'); await page.getByRole('button', { name: '开始计时', exact: true }).click();
    await expect(page.locator('.demo-time')).toContainText('00:01');
    await page.getByRole('button', { name: '暂停计时', exact: true }).click(); mark('课堂演示与计时');
    await app.close();
    ({ app, page, go, api } = await launch());
    expect((await api('/growth/config')).data.channels[0].budget).toBe(900);
    expect((await api('/orders/DESKTOP-ORDER')).data.base_cost).toBe(1400); mark('关闭后重启保留修改');
    expect((await api('/demo/reset', 'POST')).status).toBe(200);
    expect((await api('/growth/config')).data.channels[0].budget).toBe(600); mark('重置功能');
    expect(errors).toEqual([]); expect(external).toEqual([]); mark('无页面错误/无外网业务请求');
  } finally { await app.close(); }
  await fs.writeFile(path.join(OUT, 'desktop-e2e.json'), JSON.stringify({ passed: true, executable: path.basename(executable), noPythonNodeInPath: true, isolatedData: true, checks, errors, external, limitations: ['Loopback-only policy tested; physical network adapter was not disabled.'] }, null, 2));
  console.log('PASS packaged desktop:', checks.length, 'groups');
})().catch(async e => {
  await fs.writeFile(path.join(OUT, 'desktop-e2e-failure.txt'), String(e)); console.error(e.message); process.exit(1);
});
