import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";
const evidence = "../docs/screenshots";
test.beforeEach(async ({ request }) => {
  expect((await request.post("/api/demo/reset")).ok()).toBeTruthy();
});

test("赛题一：预算漏斗保存、实验、任务、报告下载", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "把复杂风险， 变成清楚的下一步。" }),
  ).toBeVisible();
  await mkdir(evidence, { recursive: true });
  await page.screenshot({ path: evidence + "/home.png", fullPage: true });
  await page
    .getByRole("link", { name: "增长运营工作台 Growth strategy" })
    .click();
  await expect(
    page.getByRole("heading", { name: "大学生", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "物流及供应链从业者", exact: true }),
  ).toBeVisible();
  await page.getByRole("tab", { name: "预算与增长模型" }).click();
  await page.getByLabel("校园社群预算", { exact: true }).fill("900");
  await page.getByLabel("访问率", { exact: true }).fill("20");
  await expect(page.locator(".stat").first()).toContainText("3,300");
  await expect(page.locator(".funnel-numbers")).toContainText("2,400");
  await page.getByRole("button", { name: "保存参数", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("已保存");
  await page.reload();
  await page.getByRole("tab", { name: "预算与增长模型" }).click();
  await expect(page.getByLabel("校园社群预算", { exact: true })).toHaveValue(
    "900",
  );
  await expect(page.getByLabel("访问率", { exact: true })).toHaveValue("20");
  await expect(page.locator(".stat").first()).toContainText("3,300");
  await expect(page.locator(".funnel-numbers")).toContainText("2,400");
  await page.screenshot({
    path: evidence + "/growth-model.png",
    fullPage: true,
  });
  await page.getByRole("tab", { name: "实验与执行" }).click();
  await page.getByRole("button", { name: "计算实验差异", exact: true }).click();
  await expect(page.locator(".experiment-result")).toContainText("5 个百分点");
  await page.getByLabel("A组参与人数").fill("10");
  await page.getByLabel("A组转化人数").fill("1");
  await page.getByLabel("B组参与人数").fill("10");
  await page.getByLabel("B组转化人数").fill("7");
  await page.getByRole("button", { name: "计算实验差异", exact: true }).click();
  await expect(page.locator(".experiment-result")).toContainText("样本不足");
  await page.getByLabel("核实队伍资格与平台能力状态").selectOption("已完成");
  await expect(page.getByRole("status")).toContainText("已保存");
  expect((await (await request.get("/api/tasks")).json())[0].status).toBe(
    "已完成",
  );
  await page.getByRole("button", { name: "新增任务", exact: true }).click();
  const form = page.getByRole("dialog", { name: "新增运营任务" });
  await form.getByLabel("任务编号").fill("G-E2E");
  await form.getByLabel("任务名称").fill("测试执行任务");
  await form.getByLabel("衡量指标").fill("1条核验记录");
  await form.getByRole("button", { name: "保存任务", exact: true }).click();
  await expect(form).not.toBeVisible();
  await expect(page.getByText("测试执行任务", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "编辑测试执行任务", exact: true })
    .click();
  await page.getByRole("dialog").getByLabel("预期成果").fill("实际保存验证");
  await page.getByRole("button", { name: "保存任务", exact: true }).click();
  await expect(
    page.getByRole("row").filter({ hasText: "测试执行任务" }),
  ).toContainText("实际保存验证");
  expect(
    (await (await request.get("/api/tasks")).json()).find(
      (t: { id: string }) => t.id === "G-E2E",
    ).outcome,
  ).toBe("实际保存验证");
  await page.getByRole("button", { name: "生成运营报告", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("假设预算");
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "下载报告", exact: true }).click();
  expect((await download).suggestedFilename()).toMatch(/skyroute-.*\.md/);
  await page.screenshot({
    path: evidence + "/growth-report.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "关闭弹窗", exact: true }).click();
  await page
    .getByRole("button", { name: "删除测试执行任务", exact: true })
    .click();
  await page.getByRole("button", { name: "确认删除", exact: true }).click();
  await expect(
    page.getByText("测试执行任务", { exact: true }),
  ).not.toBeVisible();
  expect(errors).toEqual([]);
});

test("赛题二：三天气、四方案、规则智能体、仿真与报告", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.goto("/logistics");
  await page.getByRole("button", { name: "正常天气 晴朗 / 通行稳定" }).click();
  await page.getByRole("button", { name: "运行风险分析", exact: true }).click();
  await expect(page.locator(".risk-number")).toContainText("11");
  await page.getByRole("button", { name: "暴雨风险 主走廊降雨增强" }).click();
  await page.getByRole("button", { name: "运行风险分析", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "四类应对策略，逐项对比", exact: true }),
  ).toBeVisible();
  const computed = await (
    await request.post("/api/analysis", {
      data: { order_id: "SR-001", scenario_id: "rain" },
    })
  ).json();
  await expect(page.locator(".recommended-row")).toContainText(
    computed.recommendation.name,
  );
  await expect(
    page.getByRole("heading", { name: "受影响订单与节点", exact: true }),
  ).toBeVisible();
  const riskSummary = await (
    await request.get("/api/risk/overview?scenario_id=rain")
  ).json();
  await expect(page.locator(".risk-order-list button")).toHaveCount(
    riskSummary.weather_affected,
  );
  const risk = await page.locator(".risk-number").innerText();
  expect(risk).not.toMatch(/^11\s/);
  await expect(page.locator("tbody tr")).toHaveCount(4);
  await page.getByRole("button", { name: "生成分析解释", exact: true }).click();
  await expect(page.locator(".explanation")).toContainText("规则模式");
  await page.screenshot({
    path: evidence + "/logistics-rain.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "查看决策报告", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("SR-001");
  await expect(page.getByRole("dialog")).toContainText("方案对比");
  const down = page.waitForEvent("download");
  await page.getByRole("link", { name: "下载报告", exact: true }).click();
  expect((await down).suggestedFilename()).toMatch(/\.md$/);
  await page.getByRole("button", { name: "关闭弹窗", exact: true }).click();
  await page.getByRole("button", { name: "运行情景仿真", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "逐订单对比", exact: true }),
  ).toBeVisible();
  await expect(page.locator("tbody tr")).toHaveCount(6);
  await page.screenshot({
    path: evidence + "/simulation-rain.png",
    fullPage: true,
  });
  const rain = await (
    await request.post("/api/simulation", { data: { scenario_id: "rain" } })
  ).json();
  expect(rain.after.on_time_rate).toBeGreaterThan(rain.before.on_time_rate);
  await page.getByRole("button", { name: "暴雪与大风 多节点复合影响" }).click();
  await page.getByRole("button", { name: "运行情景仿真", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(6);
  await page.getByRole("button", { name: "查看仿真报告", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("暴雪与大风");
  await page.getByRole("button", { name: "关闭弹窗", exact: true }).click();
  await page.getByRole("tab", { name: "风险与方案", exact: true }).click();
  await page.getByLabel("分析订单", { exact: true }).selectOption("SR-005");
  await page.getByRole("button", { name: "运行风险分析", exact: true }).click();
  await expect(page.locator("tbody tr").nth(1)).toContainText("不适用");
  await page.getByLabel("成本权重", { exact: true }).fill("100");
  await page.getByLabel("时间权重", { exact: true }).fill("0");
  await page.getByLabel("风险权重", { exact: true }).fill("0");
  await expect(page.locator(".recommended-row")).not.toBeVisible();
  await page.getByRole("button", { name: "运行风险分析", exact: true }).click();
  const byCost = await (
    await request.post("/api/analysis", {
      data: {
        order_id: "SR-005",
        scenario_id: "snow",
        weights: { cost: 1, time: 0, risk: 0 },
      },
    })
  ).json();
  await expect(page.locator(".recommended-row")).toContainText(
    byCost.recommendation.name,
  );
  expect(errors).toEqual([]);
});

test("订单新增编辑筛选、运力错误与CSV导出", async ({ page, request }) => {
  await page.goto("/logistics");
  await page.getByRole("tab", { name: "运输订单管理" }).click();
  await page.getByRole("button", { name: "新增订单", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("订单编号", { exact: true }).fill("E2E-ORDER");
  await dialog.getByLabel("重量", { exact: true }).fill("29");
  await dialog.getByRole("button", { name: "校验并保存订单" }).click();
  await expect(page.getByRole("status")).toContainText("运力不足");
  await dialog.getByLabel("重量", { exact: true }).fill("9");
  await dialog.getByRole("button", { name: "校验并保存订单" }).click();
  await expect(dialog).not.toBeVisible();
  await page.getByLabel("查询订单").fill("E2E-ORDER");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await page
    .getByRole("button", { name: "编辑E2E-ORDER", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByLabel("原计划成本", { exact: true })
    .fill("1400");
  await page.getByRole("button", { name: "校验并保存订单" }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  expect(
    (await (await request.get("/api/orders/E2E-ORDER")).json()).base_cost,
  ).toBe(1400);
  const csv = page.waitForEvent("download");
  await page.getByRole("link", { name: "导出CSV", exact: true }).click();
  expect((await csv).suggestedFilename()).toBe("skyroute-orders.csv");
  await page
    .getByRole("button", { name: "删除E2E-ORDER", exact: true })
    .click();
  await page.getByRole("button", { name: "确认删除", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(0);
  const sample = await (await request.get("/api/orders/SR-001")).json();
  sample.id = "IMPORTED-E2E";
  await page.getByRole("button", { name: "导入JSON", exact: true }).click();
  await page.getByLabel("JSON订单数据").fill(JSON.stringify([sample]));
  await page.getByRole("button", { name: "校验并导入", exact: true }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await page.getByLabel("查询订单").fill("IMPORTED-E2E");
  await expect(page.locator("tbody tr")).toHaveCount(1);
});

test("演示重置、手机宽度与无外部请求", async ({ page }) => {
  const external: string[] = [];
  page.on("request", (r) => {
    if (
      !r.url().startsWith("http://127.0.0.1:8000") &&
      !r.url().startsWith("data:")
    )
      external.push(r.url());
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "开始课堂演示", exact: true }).click();
  await page.getByRole("button", { name: "重置演示数据", exact: true }).click();
  await page
    .getByRole("button", { name: "确认重置教学数据", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("已重置");
  await page.getByRole("button", { name: "进入赛题一", exact: true }).click();
  await page.getByRole("tab", { name: "预算与增长模型" }).click();
  await expect(page.getByLabel("校园社群预算", { exact: true })).toHaveValue(
    "600",
  );
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: evidence + "/mobile-growth.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "切换导航", exact: true }).click();
  await page
    .getByRole("link", { name: "气象物流决策 Weather intelligence" })
    .click();
  await expect(
    page.getByRole("heading", { name: "先看清风险，再决定怎么走." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "运行风险分析", exact: true }).click();
  await expect(page.locator(".recommended-row")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: evidence + "/mobile-logistics.png",
    fullPage: true,
  });
  expect(external).toEqual([]);
});
