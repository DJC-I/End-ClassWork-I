# SkyRoute AI 架构决策（角色1，2026-11-16）

仅执行第一阶段，采用同一实例的六角色串行协作：1架构 → 3后端 → 2前端 → 4算法 → 5运营 → 6测试。没有并行子智能体，不代表真实学生贡献。

## 技术选择

- React + TypeScript + Vite，Lucide 图标、Recharts 图表、CSS 设计变量。使用成熟组件和自主 CSS，避免增加离线演示依赖。
- Python 3.12 + FastAPI + Pydantic，SQLite 标准库，参数化 SQL；无需数据库服务、ORM 或云账号。
- 开发 Vite `/api` 代理；生产 FastAPI 托管编译前端，同源 `127.0.0.1:8000`，仅监听本机。
- 数据库存储订单、运营任务、模型参数、当前场景、分析运行及报告。分析快照带输入和工具记录，报告始终对应当次输入。
- 模型是可选解释层，所有数值由确定性算法计算。无密钥规则模式可完成全部演示。配置仅后端读取。

## 数据和业务契约

所有时间使用带 `+08:00` 的 ISO 8601，重量吨、距离千米、时长小时、金额人民币。天气和物流网络完全为教学模拟，不声称真实道路里程、封路或实际运行结果。网络是有向连接的模拟可通行运输图；几何线条仅作拓扑展示。

订单：id、origin、destination、cargo（general/cold/fragile）、weight、departure、deadline、priority（1–3）、route（节点ID数组）、base_cost、base_hours、status。新增/修改校验时间先后、路径连续性、端点、运力和距离成本下限；删除及导入均有一致事务。

场景：normal/rain/snow，气象要素、有效期、边/节点影响映射。预警只提高速度损失和风险，不自动移除道路。不可用连接或运力独立建模。

风险引擎按各边通行时间与天气有效期重叠计算气象影响，货物、优先级、时限共同决定剩余风险。通过图枚举实际可达简单路径，比较原计划、提前2小时、避开原走廊的绕行、途经替代中转节点。不同策略必须有不同路线或明确不适用原因。方案按成本/时间/风险归一化加权推荐。

仿真使用确定性的0.85/1/1.15天气严重度压力回放，固定种子版本，指标为模型情景下的模拟准时占比，绝非真实概率或历史观测。原计划与优化使用相同订单和扰动。

## REST 契约 v1

统一错误 `{error:{code,message,details?}}`，422校验、404不存在、409业务冲突、503算法/模型不可用。OpenAPI 自动生成 `/docs`。

|接口|用途|
|---|---|
|GET /api/health|数据库连通、算法及模型模式|
|GET /api/bootstrap|网络、场景、订单、运营任务、运营内容、配置|
|GET/POST /api/orders; GET/PUT/DELETE /api/orders/{id}|订单CRUD|
|POST /api/orders/import; GET /api/orders/export|事务JSON导入和CSV导出|
|GET /api/network; GET /api/scenarios; PUT /api/scenarios/current|网络与持久化场景|
|POST /api/analysis|风险、方案、推荐及工具轨迹，存运行快照|
|POST /api/simulation|批量前后对比与逐订单结果，持久化|
|GET /api/risk/overview|当前场景下逐订单影响节点/区段、风险与延误及汇总|
|GET /api/reports/{id}; GET /api/reports/{id}/download|报告快照及Markdown导出|
|POST /api/agent/explain|基于已存分析的可选模型解释及规则降级|
|POST /api/growth/calculate; POST /api/growth/experiment|漏斗、渠道预算及两比例实验|
|GET/PUT /api/growth/config; POST /api/growth/report|运营配置保存和运营报告|
|GET/POST /api/tasks; PUT/DELETE /api/tasks/{id}|运营任务持久化|
|POST /api/demo/reset|仅重置本项目教学数据库|

## 页面与验收

门户 `/`，运营 `/growth`，物流 `/logistics`，演示 `/demo`，方法与来源 `/about`。两赛题可独立展示。报告用页面对话框、下载和打印。全站加载/失败/空状态、键盘表单、移动端导航、投影全屏。

评分映射：用户洞察→4画像；策略完整性→拉新/激活/留存/推荐内容；执行→持久化看板与预算；增长验证→漏斗与A/B不确定性；物流完整性→CRUD/图/风险/四方案/回放/报告；AI→带输入输出的工具工作流及规则模式；落地→本地启动、数据与边界说明。

可验证条件：实际运行pytest（风险、成本、可达性、边界、API、持久化）；tsc和Vite构建；自动浏览器走通双题、场景变化、表单保存、报告和重置；检查控制台、移动宽度。不得以文件存在代替运行证据。


## 第4.6阶段前端设计层

前端业务API与计算接口保持不变。tokens.css定义色彩/字体/间距等，studio.css负责统一布局及组件状态，design.ts共享图表主题；style.css仅作为入口。用户原TTF在public/fonts，预加载并通过--font-ui全站继承，图表显式使用同族。Modal统一焦点管理，NetworkMap直接展示真实bootstrap网络并支持小屏键盘滚动；首页复用相同网络。设计、字体与多尺寸验收见docs/PHASE4_6_DESIGN.md及docs/PHASE4_6_ACCEPTANCE.md。
