# API与数据字典

实时可交互文档：http://127.0.0.1:8000/docs，离线契约快照openapi.json。通用错误：`{error:{code,message,details?}}`，422校验、404缺失、409重复/业务冲突、500内部错误、503未就绪。日志不打印请求体或密钥。

|实体|字段与单位|
|---|---|
|订单|id唯一ASCII编号；origin/destination节点ID；cargo general/cold/fragile；weight吨，0<值≤30；departure/deadline带时区ISO时间；priority 1–3；route节点数组；base_cost元；base_hours小时；status待发运/运输中/已送达|
|节点|id/name/city；x/y示意图位置；lat/lon地理近似；capacity单票载重上限吨|
|有向边|source/target；km模拟公路里程；hours正常时长；toll元；capacity单票上限吨；available独立可用性；corridor教学分组|
|天气|rain/snow mm/3h（雪为液态当量）；wind m/s；visibility km；temperature℃；valid_from/to；warning模拟标签；edge_factors/node_factors影响强度|
|运营|曝光假设次数；4逐层转化率0–1；渠道budget元、cpm元/千次；不输入实际统计则不产生实际成果|
|任务|id/title/owner角色/start/end日期/status/resources/outcome/metric；状态修改持久化|
|报告|UUID/kind/created_at UTC/data_version/disclaimer，以及完整输入和输出快照；不随业务参数变动|

请求示例：

```json
{"order_id":"SR-001","scenario_id":"rain","weights":{"cost":0.25,"time":0.35,"risk":0.4}}
```

POST /api/analysis返回order/scenario/risk/plans/recommendation/trace和报告元数据。不可行plan保留id/name/feasible=false/reason，不伪填数值。GET /api/risk/overview?scenario_id=rain按当前全部未送达订单汇总，risk_orders为风险≥25，high_risk≥50。

POST /api/simulation返回before/after、每订单名义场景结果、全部压力样本、种子与方法。GET /api/reports/{id}读取快照，后缀/download返回Markdown；前端报告支持打印。

导入POST /api/orders/import接受1–200条完整订单JSON数组，不覆盖现有编号，任何校验或唯一约束失败整批回滚。CSV用于导出查看；导入格式为JSON，示例data/orders.sample.json。

运营POST /api/growth/calculate实时计算；PUT /api/growth/config保存；/experiment输入a_visitors/a_conversions/b_visitors/b_conversions；/report读取当前任务与策略形成快照。

所有端点列表与结构由FastAPI OpenAPI生成，不维护第二套不一致的手写schema。任何未来真实气象适配必须保留来源、观测时间、预报有效期和授权说明；本版本未提供实况适配。
