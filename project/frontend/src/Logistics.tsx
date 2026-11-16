import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import {
  Play,
  FileText,
  Plus,
  Search,
  CloudRain,
  Wind,
  Eye,
  Thermometer,
  Snowflake,
  ArrowRight,
  Pencil,
  Trash2,
  Download,
  Upload,
  ShieldAlert,
  ChevronRight,
  Braces,
  Sparkles,
} from "lucide-react";
import { api, dt, num, money, cargoNames } from "./api";
import type {
  Bootstrap,
  Decision,
  Simulation,
  Order,
  Weights,
  Network,
  Scenario,
  RiskOverview,
} from "./types";
import {
  Card,
  Stat,
  SectionTitle,
  Badge,
  NetworkMap,
  Empty,
  PlanTable,
  ReportViewer,
  Modal,
  CompareChart,
  PlanSummary,
} from "./components";
interface Props {
  data: Bootstrap;
  reload: () => Promise<void>;
  notify: (s: string) => void;
}
export default function Logistics({ data, reload, notify }: Props) {
  const [sid, setSid] = useState(data.current_scenario),
    [oid, setOid] = useState(data.orders[0]?.id ?? ""),
    [weights, setWeights] = useState<Weights>({
      cost: 0.25,
      time: 0.35,
      risk: 0.4,
    }),
    [decision, setDecision] = useState<Decision | null>(null),
    [simulation, setSimulation] = useState<Simulation | null>(null),
    [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [report, setReport] = useState<Decision | Simulation | null>(null),
    [tab, setTab] = useState("decision"),
    [query, setQuery] = useState(""),
    [status, setStatus] = useState(""),
    [editor, setEditor] = useState<Order | null>(null),
    [isNew, setIsNew] = useState(false),
    [deleting, setDeleting] = useState<Order | null>(null),
    [importOpen, setImportOpen] = useState(false),
    [importText, setImportText] = useState(""),
    [explanation, setExplanation] = useState<{
      mode: string;
      text: string;
      notice?: string;
    } | null>(null),
    [question, setQuestion] = useState(
      "请解释推荐依据、适用限制与需要人工核实的事项。",
    );
  const [overview, setOverview] = useState<RiskOverview | null>(null),
    [overviewError, setOverviewError] = useState("");
  useEffect(() => {
    let active = true;
    setOverview(null);
    setOverviewError("");
    void api<RiskOverview>("/risk/overview?scenario_id=" + sid)
      .then((r) => {
        if (active) setOverview(r);
      })
      .catch((e) => {
        if (active) setOverviewError(e.message);
      });
    return () => {
      active = false;
    };
  }, [sid, data.orders]);
  const scenario =
    data.scenarios.find((s) => s.id === sid) ?? data.scenarios[0];
  const order = data.orders.find((o) => o.id === oid);
  useEffect(() => {
    setDecision(null);
    setSimulation(null);
    setExplanation(null);
  }, [data.orders]);
  useEffect(() => {
    setSid(data.current_scenario);
  }, [data.current_scenario]);
  useEffect(() => {
    if (!data.orders.some((o) => o.id === oid))
      setOid(data.orders[0]?.id ?? "");
  }, [data.orders, oid]);
  const run = async (label: string, f: () => Promise<void>) => {
    setBusy(label);
    setError("");
    try {
      await f();
    } catch (e) {
      setError((e as Error).message);
      notify((e as Error).message);
    } finally {
      setBusy("");
    }
  };
  const switchScenario = (s: string) =>
    void run("scenario", async () => {
      await api("/scenarios/current", "PUT", { scenario_id: s });
      setSid(s);
      setDecision(null);
      setSimulation(null);
      setExplanation(null);
      await reload();
    });
  const analyze = () =>
    void run("analysis", async () => {
      setDecision(
        await api<Decision>("/analysis", "POST", {
          order_id: oid,
          scenario_id: sid,
          weights,
        }),
      );
      setExplanation(null);
    });
  const simulate = () =>
    void run("simulation", async () => {
      setSimulation(
        await api<Simulation>("/simulation", "POST", {
          scenario_id: sid,
          weights,
        }),
      );
      setTab("simulation");
    });
  const newOrder = () => {
    setIsNew(true);
    setEditor({
      id: "SR-" + Date.now().toString().slice(-7),
      origin: "BJ",
      destination: "TJ",
      cargo: "general",
      weight: 8,
      departure: "2026-11-16T10:00:00+08:00",
      deadline: "2026-11-16T15:00:00+08:00",
      priority: 2,
      route: ["BJ", "TZ", "WQ", "TJ"],
      base_cost: 1180,
      base_hours: 2.6,
      status: "待发运",
    });
  };
  const selected = decision?.plans.find(
    (p) => p.id === decision.recommendation.id,
  );
  const filtered = data.orders.filter(
    (o) =>
      (!status || o.status === status) &&
      JSON.stringify(o).toLowerCase().includes(query.toLowerCase()),
  );
  const displayRoute = selected?.route ?? order?.route ?? [];
  return (
    <>
      <SectionTitle
        kicker="CHALLENGE 02 / WEATHER INTELLIGENCE"
        title="先看清风险，再决定怎么走"
        description="北京—天津教学运输走廊 · 基于图网络与可解释规则的运输方案比较"
        action={
          <>
            <button
              className="button secondary"
              onClick={simulate}
              disabled={!!busy || !data.orders.length}
            >
              <Play size={16} />
              {busy === "simulation" ? "仿真计算中…" : "运行情景仿真"}
            </button>
            <button
              className="button"
              onClick={analyze}
              disabled={!!busy || !order || order.status === "已送达"}
            >
              <Sparkles size={16} />
              {busy === "analysis" ? "分析计算中…" : "运行风险分析"}
            </button>
          </>
        }
      />
      <div className="stats">
        <Stat
          label="运输订单"
          value={data.orders.length}
          detail="SQLite实时业务记录"
          accent
        />
        <Stat
          label="当前天气场景"
          value={scenario.name}
          detail={scenario.warning}
        />
        <Stat
          label="中高风险订单"
          value={overview ? overview.risk_orders + " 单" : "计算中"}
          detail={
            overview
              ? "高风险 " +
                overview.high_risk +
                " 单 · 天气影响 " +
                overview.weather_affected +
                " 单"
              : "根据当前场景读取实际订单计算"
          }
        />
        <Stat
          label="平均预计原计划延误"
          value={overview ? num(overview.average_delay, 2) + " h" : "—"}
          detail="全部未送达订单 · 模拟时长差"
        />
      </div>
      <div className="scenario-strip">
        <span className="eyebrow">WEATHER / 模拟场景</span>
        <div className="scenario-options">
          {data.scenarios.map((s) => (
            <button
              className={sid === s.id ? "active" : ""}
              aria-pressed={sid === s.id}
              key={s.id}
              disabled={!!busy}
              onClick={() => switchScenario(s.id)}
            >
              {s.id === "normal" ? (
                <Thermometer size={17} />
              ) : s.id === "rain" ? (
                <CloudRain size={17} />
              ) : (
                <Snowflake size={17} />
              )}
              <span>
                {s.name}
                <small>{s.tag}</small>
              </span>
              {sid === s.id && <span className="status-dot" />}
            </button>
          ))}
        </div>
      </div>
      <div className="tabs" role="tablist" aria-label="物流工作台视图">
        {[
          ["decision", "风险与方案"],
          ["orders", "运输订单管理"],
          ["simulation", "情景仿真与回放"],
        ].map(([id, label]) => (
          <button
            role="tab"
            aria-selected={tab === id}
            key={id}
            className={tab === id ? "active" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      {decision && selected && tab === "decision" && (
        <div className="decision-brief" aria-label="当前决策摘要">
          <div>
            <small>
              {decision.order.id} / {decision.risk.level} {decision.risk.score}
            </small>
            <strong>{decision.recommendation.name}</strong>
          </div>
          <div>
            <small>推荐方案成本</small>
            <span className="brief-metric">{money(selected.cost)}</span>
          </div>
          <div>
            <small>运输时长 / 剩余风险</small>
            <span className="brief-metric">
              {num(selected.hours, 2)} h / {num(selected.risk)}
            </span>
          </div>
          <button className="button" onClick={() => setReport(decision)}>
            打开决策快照 <FileText size={16} />
          </button>
        </div>
      )}
      {error && (
        <div role="alert" className="error-box">
          {error}
        </div>
      )}
      {tab === "decision" ? (
        <>
          <Card
            title="受影响订单与节点"
            eyebrow="LIVE RISK OVERVIEW"
            action={<Badge>原计划逐单评估</Badge>}
          >
            {overviewError ? (
              <p role="alert" className="error-text">
                {overviewError}
              </p>
            ) : overview ? (
              <>
                <div className="risk-order-list">
                  {overview.rows
                    .filter((r) => r.affected_edges.length > 0)
                    .map((r) => (
                      <button
                        key={r.order_id}
                        className={oid === r.order_id ? "selected" : ""}
                        onClick={() => {
                          setOid(r.order_id);
                          setDecision(null);
                          setExplanation(null);
                        }}
                      >
                        <strong>{r.order_id}</strong>
                        <Badge
                          tone={
                            r.level === "高风险"
                              ? "orange"
                              : r.level === "低风险"
                                ? "green"
                                : ""
                          }
                        >
                          {r.level} {r.risk}
                        </Badge>
                        <small>
                          延误 {num(r.delay_hours, 2)} h · 影响节点{" "}
                          {r.affected_nodes.join(" / ") || "区段影响"}
                        </small>
                      </button>
                    ))}
                </div>
                {!overview.weather_affected && (
                  <p>当前模拟天气未影响任何未送达订单区段。</p>
                )}
                <p className="source">
                  {overview.source}；点击订单卡片切换分析对象。
                </p>
              </>
            ) : (
              <p>正在评估当前场景的全部未送达订单…</p>
            )}
          </Card>
          <div className="grid logistics-top">
            <Card
              title="运输网络与天气影响"
              eyebrow="SIMULATED CORRIDOR"
              action={<Badge tone="orange">非导航路网</Badge>}
            >
              <NetworkMap
                network={data.network}
                scenario={scenario}
                route={displayRoute}
                affected={decision?.risk.affected_edges}
              />
              {selected && <PlanSummary plan={selected} />}
              <div className="network-weather">
                <Weather scenario={scenario} />
              </div>
            </Card>
            <Card title="订单与决策偏好" eyebrow="CONTEXT">
              <label>
                选择分析订单
                <select
                  aria-label="分析订单"
                  value={oid}
                  onChange={(e) => {
                    setOid(e.target.value);
                    setDecision(null);
                    setExplanation(null);
                  }}
                >
                  {data.orders.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.id} · {cargoNames[o.cargo]} · {o.weight}t · {o.status}
                    </option>
                  ))}
                </select>
              </label>
              {order ? (
                <div className="order-context">
                  <p>
                    <span>承诺送达</span>
                    <strong>{dt(order.deadline)}</strong>
                  </p>
                  <p>
                    <span>原计划</span>
                    <strong>{order.route.join(" → ")}</strong>
                  </p>
                  <p>
                    <span>成本 / 时长</span>
                    <strong>
                      {money(order.base_cost)} / {order.base_hours} h
                    </strong>
                  </p>
                </div>
              ) : (
                <p>暂无订单，请先新增。</p>
              )}
              <div className="weight-head">
                决策权重 <span>自动按总和归一化</span>
              </div>
              {(["cost", "time", "risk"] as const).map((k, i) => (
                <label className="weight-control" key={k}>
                  <span>
                    {["成本", "运输时间", "剩余风险"][i]}
                    <strong>{Math.round(weights[k] * 100)}%</strong>
                  </span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    aria-label={["成本权重", "时间权重", "风险权重"][i]}
                    value={weights[k] * 100}
                    onChange={(e) => {
                      setWeights({
                        ...weights,
                        [k]: Number(e.target.value) / 100,
                      });
                      setDecision(null);
                      setSimulation(null);
                      setExplanation(null);
                    }}
                  />
                </label>
              ))}
              <button
                className="button full"
                disabled={!!busy || !order || order.status === "已送达"}
                onClick={analyze}
              >
                开始计算 <ArrowRight size={16} />
              </button>
            </Card>
          </div>
          {decision ? (
            <>
              <div className="grid risk-grid">
                <Card
                  title="风险评估与影响区段"
                  eyebrow="EXPLAINABLE RISK"
                  action={
                    <Badge
                      tone={
                        decision.risk.level === "低风险" ? "green" : "orange"
                      }
                    >
                      {decision.risk.level}
                    </Badge>
                  }
                >
                  <div className="risk-number">
                    <span>{decision.risk.score}</span>
                    <small>/ 100 规则风险分</small>
                    <ShieldAlert size={32} />
                  </div>
                  <div className="risk-bar">
                    <i style={{ width: decision.risk.score + "%" }} />
                  </div>
                  <ul className="reason-list">
                    {decision.risk.reasons.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                  <div className="chips">
                    {decision.risk.affected_edges.length ? (
                      decision.risk.affected_edges.map((e) => (
                        <Badge tone="orange" key={e}>
                          {e}
                        </Badge>
                      ))
                    ) : (
                      <Badge tone="green">无天气影响区段</Badge>
                    )}
                  </div>
                  <details>
                    <summary>计算依据与公式</summary>
                    <ul>
                      {decision.risk.basis.map((b) => (
                        <li key={b}>{b}</li>
                      ))}
                    </ul>
                  </details>
                </Card>
                <Card
                  title="当前权重下的推荐"
                  eyebrow="RECOMMENDATION"
                  className="recommendation"
                >
                  <Badge tone="green">来自实际算法计算</Badge>
                  <h2>{decision.recommendation.name}</h2>
                  <p>{decision.recommendation.reason}</p>
                  {selected && (
                    <div className="stats two">
                      <Stat
                        label="推荐运输成本"
                        value={money(selected.cost)}
                        detail={"增量 " + money(selected.extra_cost)}
                      />
                      <Stat
                        label="推荐运输时长"
                        value={num(selected.hours, 2) + " h"}
                        detail={dt(selected.arrival) + " 到货"}
                      />
                    </div>
                  )}
                  <button
                    className="button secondary"
                    onClick={() => setReport(decision)}
                  >
                    <FileText size={16} />
                    查看决策报告
                  </button>
                </Card>
              </div>
              <Card
                title="四类应对策略，逐项对比"
                eyebrow="PLAN COMPARISON"
                action={<Badge>数值与当前报告快照一致</Badge>}
              >
                <PlanTable decision={decision} />
                <p className="source">
                  综合分越低越优。不可行策略保留原因，不用重复路线伪装新方案。准时为本次模型估算，风险分不是事故概率。
                </p>
              </Card>
              <Card
                title="分析智能体：有流程，也有记录"
                eyebrow="AGENT WORKFLOW"
                action={<Badge tone="green">{data.health.mode}</Badge>}
              >
                <div className="agent-steps">
                  {decision.trace.map((t, i) => (
                    <div key={t.tool}>
                      <span>{i + 1}</span>
                      {t.tool}
                      {i < decision.trace.length - 1 && (
                        <ChevronRight size={16} />
                      )}
                    </div>
                  ))}
                </div>
                <div className="grid two">
                  <div>
                    {decision.trace.map((t) => (
                      <details key={t.tool}>
                        <summary>
                          <Braces size={15} />
                          {t.tool} · 工具输入输出
                        </summary>
                        <pre>
                          {JSON.stringify(
                            { input: t.input, output: t.output },
                            null,
                            2,
                          )}
                        </pre>
                      </details>
                    ))}
                  </div>
                  <div className="inset">
                    <h3>基于计算快照的解释</h3>
                    <p>
                      外部模型仅解释现有计算，无密钥仍可输出规则依据。模型文字不替代方案表中的数值。
                    </p>
                    <label>
                      你的问题
                      <textarea
                        aria-label="智能体问题"
                        rows={3}
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                      />
                    </label>
                    <button
                      className="button secondary"
                      disabled={!!busy}
                      onClick={() =>
                        void run("explain", async () =>
                          setExplanation(
                            await api("/agent/explain", "POST", {
                              report_id: decision.id,
                              question,
                            }),
                          ),
                        )
                      }
                    >
                      <Sparkles size={15} />
                      {busy === "explain" ? "生成中…" : "生成分析解释"}
                    </button>
                    {explanation && (
                      <div className="explanation">
                        <Badge>{explanation.mode}</Badge>
                        <p>{explanation.text}</p>
                        {explanation.notice && (
                          <small>{explanation.notice}</small>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            </>
          ) : (
            <Card>
              <Empty>
                选择订单和模拟天气，点击“运行风险分析”，获得风险依据、四类方案与可追溯工具记录。
              </Empty>
            </Card>
          )}
        </>
      ) : tab === "orders" ? (
        <>
          <Card
            title="运输订单台账"
            eyebrow="ORDER MANAGEMENT"
            action={
              <div className="actions">
                <a
                  className="button secondary small"
                  href="/api/orders/export"
                  download
                >
                  <Download size={15} />
                  导出CSV
                </a>
                <button
                  className="button secondary small"
                  onClick={() => setImportOpen(true)}
                >
                  <Upload size={15} />
                  导入JSON
                </button>
                <button className="button small" onClick={newOrder}>
                  <Plus size={15} />
                  新增订单
                </button>
              </div>
            }
          >
            <div className="filter-row">
              <label className="search-input">
                <Search size={17} />
                <input
                  placeholder="搜索订单、节点或状态"
                  aria-label="查询订单"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <select
                aria-label="订单状态筛选"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="">全部运输状态</option>
                <option>待发运</option>
                <option>运输中</option>
                <option>已送达</option>
              </select>
              <span className="source">共 {filtered.length} 条</span>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>订单 / 货物</th>
                    <th>起终点 / 路线</th>
                    <th>发运 / 承诺送达</th>
                    <th>重量 / 优先级</th>
                    <th>成本 / 时长</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((o) => (
                    <tr key={o.id}>
                      <td>
                        <strong>{o.id}</strong>
                        <small>{cargoNames[o.cargo]}</small>
                      </td>
                      <td>
                        {o.origin} → {o.destination}
                        <small>{o.route.join(" → ")}</small>
                      </td>
                      <td>
                        {dt(o.departure)}
                        <small>{dt(o.deadline)}</small>
                      </td>
                      <td>
                        {o.weight} t<small>P{o.priority}</small>
                      </td>
                      <td>
                        {money(o.base_cost)}
                        <small>{o.base_hours} h</small>
                      </td>
                      <td>
                        <Badge tone={o.status === "运输中" ? "blue" : ""}>
                          {o.status}
                        </Badge>
                      </td>
                      <td>
                        <div className="actions">
                          <button
                            className="icon-button"
                            aria-label={"分析" + o.id}
                            title="分析订单"
                            onClick={() => {
                              setOid(o.id);
                              setDecision(null);
                              setTab("decision");
                            }}
                          >
                            <ArrowRight size={15} />
                          </button>
                          <button
                            className="icon-button"
                            aria-label={"编辑" + o.id}
                            onClick={() => {
                              setIsNew(false);
                              setEditor({ ...o });
                            }}
                          >
                            <Pencil size={15} />
                          </button>
                          <button
                            className="icon-button"
                            aria-label={"删除" + o.id}
                            onClick={() => setDeleting(o)}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!filtered.length && (
              <Empty>没有匹配订单，可清除筛选或新增运输计划。</Empty>
            )}
          </Card>
          <div className="notice">
            订单校验包含：非负成本与有效载重、带时区时间顺序、图中有向路径连续、每段及节点运力、基准时长一致。种子订单均为教学模拟。
          </div>
        </>
      ) : (
        <>
          <div className="notice">
            固定种子版本，0.85 / 1 /
            1.15倍天气严重度配对压力回放。结果是模型场景统计，不是历史实绩或真实准时概率。
          </div>
          {simulation ? (
            <>
              <div className="grid two">
                <Card title="准时与延误" eyebrow="BEFORE / AFTER">
                  <CompareChart
                    unit="%"
                    data={[
                      {
                        name: "模拟准时率",
                        原计划: simulation.before.on_time_rate,
                        优化方案: simulation.after.on_time_rate,
                      },
                    ]}
                  />
                  <div className="comparison-line">
                    <span>平均延误</span>
                    <strong>
                      {num(simulation.before.average_delay, 2)} h{" "}
                      <ArrowRight size={15} />{" "}
                      {num(simulation.after.average_delay, 2)} h
                    </strong>
                  </div>
                </Card>
                <Card title="成本与剩余风险" eyebrow="COST / RISK">
                  <CompareChart
                    unit="元"
                    data={[
                      {
                        name: "平均情景总成本",
                        原计划: simulation.before.total_cost,
                        优化方案: simulation.after.total_cost,
                      },
                    ]}
                  />
                  <div className="comparison-line">
                    <span>高风险订单（名义场景）</span>
                    <strong>
                      {simulation.before.high_risk} 单 <ArrowRight size={15} />{" "}
                      {simulation.after.high_risk} 单
                    </strong>
                  </div>
                  <div className="comparison-line">
                    <span>优化后额外成本</span>
                    <strong>{money(simulation.after.extra_cost)}</strong>
                  </div>
                </Card>
              </div>
              <Card
                title="逐订单对比"
                action={
                  <button
                    className="button secondary small"
                    onClick={() => setReport(simulation)}
                  >
                    <FileText size={15} />
                    查看仿真报告
                  </button>
                }
              >
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>订单</th>
                        <th>推荐方案</th>
                        <th>原延误 / h</th>
                        <th>优化延误 / h</th>
                        <th>原成本 / 元</th>
                        <th>优化成本 / 元</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simulation.rows.map((r) => (
                        <tr key={r.order_id}>
                          <td>{r.order_id}</td>
                          <td>{r.plan}</td>
                          <td>{num(r.before_delay, 2)}</td>
                          <td>{num(r.after_delay, 2)}</td>
                          <td>{money(r.before_cost)}</td>
                          <td>{money(r.after_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="source">
                  {simulation.method} · 种子 {simulation.seed}
                </p>
              </Card>
            </>
          ) : (
            <Card>
              <Empty>
                点击右上“运行情景仿真”，使用当前天气和权重，对全部未送达订单进行配对回放。
              </Empty>
              <button
                className="button"
                disabled={!!busy || !data.orders.length}
                onClick={simulate}
              >
                <Play size={16} />
                运行当前情景
              </button>
            </Card>
          )}
        </>
      )}
      {report && (
        <ReportViewer report={report} onClose={() => setReport(null)} />
      )}
      {editor && (
        <OrderEditor
          initial={editor}
          network={data.network}
          isNew={isNew}
          busy={!!busy}
          onClose={() => setEditor(null)}
          onSave={(o) =>
            void run("save", async () => {
              await api(
                isNew ? "/orders" : "/orders/" + o.id,
                isNew ? "POST" : "PUT",
                o,
              );
              await reload();
              setEditor(null);
              notify("订单已通过业务校验并保存");
            })
          }
        />
      )}
      {deleting && (
        <Modal title="删除运输订单" onClose={() => setDeleting(null)}>
          <p>确认删除本地订单 {deleting.id}？历史报告仍保留当时的输入快照。</p>
          <div className="actions end">
            <button
              className="button secondary"
              onClick={() => setDeleting(null)}
            >
              取消
            </button>
            <button
              className="button danger"
              disabled={!!busy}
              onClick={() =>
                void run("delete", async () => {
                  await api("/orders/" + deleting.id, "DELETE");
                  await reload();
                  setDeleting(null);
                  notify("订单已删除");
                })
              }
            >
              确认删除
            </button>
          </div>
        </Modal>
      )}
      {importOpen && (
        <Modal title="批量导入JSON订单" onClose={() => setImportOpen(false)}>
          <p>
            粘贴符合订单契约的JSON数组，每次1–200条；全部校验通过后原子写入，编号重复则整批回滚。字段格式见
            /docs。
          </p>
          <textarea
            aria-label="JSON订单数据"
            rows={12}
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder="[{...订单字段...}]"
          />
          <div className="actions end">
            <button
              className="button secondary"
              onClick={() => setImportOpen(false)}
            >
              取消
            </button>
            <button
              className="button"
              disabled={!!busy}
              onClick={() =>
                void run("import", async () => {
                  const input: unknown = JSON.parse(importText);
                  await api("/orders/import", "POST", input);
                  await reload();
                  setImportOpen(false);
                  setImportText("");
                  notify("订单导入成功");
                })
              }
            >
              校验并导入
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
function Weather({ scenario: s }: { scenario: Scenario }) {
  return (
    <>
      <div className="weather-warning">
        <CloudRain size={19} />
        <span>{s.warning}</span>
      </div>
      <div className="weather-grid">
        {[
          [CloudRain, "降雨", s.rain, "mm/3h"],
          [Snowflake, "降雪", s.snow, "mm/3h"],
          [Wind, "风速", s.wind, "m/s"],
          [Eye, "能见度", s.visibility, "km"],
          [Thermometer, "温度", s.temperature, "℃"],
        ].map(([Icon, label, v, unit]) => {
          const I = Icon as typeof CloudRain;
          return (
            <div key={String(label)}>
              <I size={15} />
              <small>{String(label)}</small>
              <strong>
                {String(v)} <em>{String(unit)}</em>
              </strong>
            </div>
          );
        })}
      </div>
      <p className="source">
        有效期：{dt(s.valid_from)}—{dt(s.valid_to)}
        （北京时间）；教学模拟预警，不代表封路。
      </p>
    </>
  );
}
function OrderEditor({
  initial,
  network,
  isNew,
  busy,
  onClose,
  onSave,
}: {
  initial: Order;
  network: Network;
  isNew: boolean;
  busy: boolean;
  onClose: () => void;
  onSave: (o: Order) => void;
}) {
  const [o, setO] = useState(initial),
    [route, setRoute] = useState(initial.route.join(",")),
    [formError, setFormError] = useState("");
  const local = (s: string) =>
    new Date(new Date(s).getTime() + 8 * 3600000).toISOString().slice(0, 16);
  const submit = (e: FormEvent) => {
    e.preventDefault();
    setFormError("");
    const nodes = route
      .split(/[,，>→\s]+/)
      .filter(Boolean)
      .map((s) => s.toUpperCase());
    const edges = nodes
      .slice(0, -1)
      .map((n, i) =>
        network.edges.find((e) => e.source === n && e.target === nodes[i + 1]),
      );
    if (edges.some((e) => !e) || nodes.length < 2) {
      setFormError("路线包含不存在的单向连接，请按图中箭头填写。");
      return;
    }
    onSave({
      ...o,
      route: nodes,
      base_hours: Number(edges.reduce((s, e) => s + e!.hours, 0).toFixed(2)),
    });
  };
  return (
    <Modal title={isNew ? "新增运输订单" : "编辑运输订单"} onClose={onClose}>
      <form onSubmit={submit}>
        <div className="form-grid">
          <label>
            订单编号
            <input
              required
              aria-label="订单编号"
              value={o.id}
              disabled={!isNew}
              onChange={(e) => setO({ ...o, id: e.target.value })}
            />
          </label>
          <label>
            货物类型
            <select
              aria-label="货物类型"
              value={o.cargo}
              onChange={(e) =>
                setO({ ...o, cargo: e.target.value as Order["cargo"] })
              }
            >
              {Object.entries(cargoNames).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <label>
            起点
            <select
              aria-label="起点"
              value={o.origin}
              onChange={(e) => setO({ ...o, origin: e.target.value })}
            >
              {network.nodes.map((n) => (
                <option value={n.id} key={n.id}>
                  {n.id} {n.city}
                </option>
              ))}
            </select>
          </label>
          <label>
            终点
            <select
              aria-label="终点"
              value={o.destination}
              onChange={(e) => setO({ ...o, destination: e.target.value })}
            >
              {network.nodes.map((n) => (
                <option value={n.id} key={n.id}>
                  {n.id} {n.city}
                </option>
              ))}
            </select>
          </label>
          <label>
            重量 / 吨
            <input
              required
              type="number"
              min="0.01"
              max="30"
              step="0.01"
              aria-label="重量"
              value={o.weight}
              onChange={(e) => setO({ ...o, weight: Number(e.target.value) })}
            />
          </label>
          <label>
            优先级
            <select
              aria-label="优先级"
              value={o.priority}
              onChange={(e) => setO({ ...o, priority: Number(e.target.value) })}
            >
              <option value="1">P1 常规</option>
              <option value="2">P2 重要</option>
              <option value="3">P3 紧急</option>
            </select>
          </label>
          <label>
            发运时间 / 北京时间
            <input
              required
              type="datetime-local"
              aria-label="发运时间"
              value={local(o.departure)}
              onChange={(e) =>
                setO({ ...o, departure: e.target.value + ":00+08:00" })
              }
            />
          </label>
          <label>
            承诺送达 / 北京时间
            <input
              required
              type="datetime-local"
              aria-label="承诺送达时间"
              value={local(o.deadline)}
              onChange={(e) =>
                setO({ ...o, deadline: e.target.value + ":00+08:00" })
              }
            />
          </label>
          <label>
            原计划成本 / 元
            <input
              required
              type="number"
              min="1"
              step="0.01"
              aria-label="原计划成本"
              value={o.base_cost}
              onChange={(e) =>
                setO({ ...o, base_cost: Number(e.target.value) })
              }
            />
          </label>
          <label>
            运输状态
            <select
              aria-label="运输状态"
              value={o.status}
              onChange={(e) =>
                setO({ ...o, status: e.target.value as Order["status"] })
              }
            >
              <option>待发运</option>
              <option>运输中</option>
              <option>已送达</option>
            </select>
          </label>
        </div>
        <label>
          计划路线 / 节点ID逗号分隔
          <input
            required
            aria-label="计划路线"
            value={route}
            onChange={(e) => setRoute(e.target.value)}
          />
        </label>
        <p className="source">
          时长由真实执行的图中边基准时长之和自动计算。示例
          BJ,TZ,WQ,TJ；BJ,LF,TJ。成本不得低于通行费。
        </p>
        {formError && (
          <p role="alert" className="error-text">
            {formError}
          </p>
        )}
        <div className="actions end">
          <button type="button" className="button secondary" onClick={onClose}>
            取消
          </button>
          <button className="button" type="submit" disabled={busy}>
            校验并保存订单
          </button>
        </div>
      </form>
    </Modal>
  );
}
