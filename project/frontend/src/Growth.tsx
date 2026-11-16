import { chartTheme } from "./design";
import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import {
  TrendingUp,
  Save,
  FileText,
  Plus,
  ArrowRight,
  FlaskConical,
  Pencil,
  Trash2,
  Users,
  Target,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { api, money, num } from "./api";
import {
  Card,
  Stat,
  SectionTitle,
  Badge,
  Modal,
  ReportViewer,
} from "./components";
import type {
  Bootstrap,
  GrowthConfig,
  GrowthResult,
  GrowthReport,
  Task,
  ExperimentResult,
} from "./types";
const rateFields = [
  ["visit_rate", "访问率"],
  ["register_rate", "注册率"],
  ["activate_rate", "激活率"],
  ["retain_rate", "7日留存率"],
] as const;
interface Props {
  data: Bootstrap;
  reload: () => Promise<void>;
  notify: (s: string) => void;
}
export default function Growth({ data, reload, notify }: Props) {
  const [tab, setTab] = useState("strategy"),
    [config, setConfig] = useState<GrowthConfig>(data.growth),
    [result, setResult] = useState<GrowthResult | null>(null),
    [calcError, setCalcError] = useState(""),
    [report, setReport] = useState<GrowthReport | null>(null),
    [busy, setBusy] = useState(false),
    [task, setTask] = useState<Task | null>(null),
    [newTask, setNewTask] = useState(false),
    [deleting, setDeleting] = useState<Task | null>(null),
    [experiment, setExperiment] = useState({
      a_visitors: 200,
      a_conversions: 30,
      b_visitors: 200,
      b_conversions: 40,
    }),
    [expResult, setExpResult] = useState<ExperimentResult | null>(null);
  useEffect(() => {
    setConfig(data.growth);
  }, [data.growth]);
  useEffect(() => {
    let alive = true;
    const t = setTimeout(() => {
      void api<GrowthResult>("/growth/calculate", "POST", config)
        .then((r) => {
          if (alive) {
            setResult(r);
            setCalcError("");
          }
        })
        .catch((e) => {
          if (alive) {
            setResult(null);
            setCalcError(e.message);
          }
        });
    }, 200);
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, [config]);
  const run = async (f: () => Promise<void>) => {
    setBusy(true);
    try {
      await f();
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const save = () =>
    void run(async () => {
      await api("/growth/config", "PUT", config);
      await reload();
      notify("运营预算与转化率已保存至SQLite");
    });
  const generate = () =>
    void run(async () => {
      setReport(await api<GrowthReport>("/growth/report", "POST", config));
    });
  const changeTask = async (t: Task) => {
    await api("/tasks/" + t.id, "PUT", t);
    await reload();
    notify("运营任务已保存");
  };
  const createTask = () => {
    setNewTask(true);
    setTask({
      id: "G-" + Date.now().toString().slice(-7),
      title: "",
      owner: "运营负责人",
      start: "2026-11-16",
      end: "2026-11-18",
      status: "待开始",
      resources: "",
      outcome: "",
      metric: "",
    });
  };
  const expRun = () =>
    void run(async () => {
      setExpResult(
        await api<ExperimentResult>("/growth/experiment", "POST", experiment),
      );
    });
  const personaIcons = [Users, TrendingUp, Target, Sparkles];
  return (
    <>
      <SectionTitle
        kicker="CHALLENGE 01 / GROWTH STUDIO"
        title="让增长策略，落到每一步"
        description="从用户洞察到预算、漏斗与验证。所有增长数值为计划假设，尚未开展真实推广。"
        action={
          <>
            <button className="button secondary" onClick={save} disabled={busy}>
              <Save size={16} />
              保存参数
            </button>
            <button className="button" onClick={generate} disabled={busy}>
              <FileText size={16} />
              生成运营报告
            </button>
          </>
        }
      />
      <div className="stats">
        <Stat
          label="计划总预算"
          value={money(result?.budget)}
          detail="可调渠道与制作预算"
          accent
        />
        <Stat
          label="预计渠道覆盖"
          value={num(result?.channel_reach, 0)}
          detail="曝光次数 · 跨渠道未去重"
        />
        <Stat
          label="预计激活用户"
          value={num(result?.channel_active)}
          detail="渠道测算 · 假设人数"
        />
        <Stat
          label="预计激活获客成本"
          value={money(result?.cac)}
          detail="元/人 · 非实际获客成效"
        />
      </div>
      <div className="tabs" role="tablist" aria-label="运营工作台视图">
        {[
          ["strategy", "用户与运营策略"],
          ["model", "预算与增长模型"],
          ["execution", "实验与执行"],
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
      {tab === "strategy" ? (
        <>
          <Card
            title="先把平台价值讲清楚"
            eyebrow="POSITIONING"
            className="positioning"
          >
            <div>
              <Badge tone="green">拟议定位 / 校园切入</Badge>
              <h2>从“想学AI”到“用AI解决物流问题”</h2>
              <p>{data.content.platform}</p>
              <div className="chips">
                <Badge>用一个案例完成首次价值体验</Badge>
                <Badge>小范围验证后再扩量</Badge>
                <Badge>合作与效果均待执行</Badge>
              </div>
            </div>
            <div className="positioning-mark">
              <TrendingUp size={64} />
            </div>
          </Card>
          <div className="section-heading">
            <h2>四类用户，四条触达路径</h2>
            <span>研究假设 · 待真实访谈验证</span>
          </div>
          <div className="grid two persona-grid">
            {data.content.personas.map((p, i) => {
              const Icon = personaIcons[i % 4];
              return (
                <Card key={p.name} className="persona">
                  <div className="persona-header">
                    <span className="workspace-icon">
                      <Icon />
                    </span>
                    <div>
                      <h3>{p.name}</h3>
                      <span className="source">{p.tag}</span>
                    </div>
                  </div>
                  <dl>
                    <dt>需求与动机</dt>
                    <dd>
                      {p.need}；{p.motivation}
                    </dd>
                    <dt>触达渠道</dt>
                    <dd>{p.channel}</dd>
                    <dt>转化障碍</dt>
                    <dd>{p.barrier}</dd>
                    <dt>运营动作</dt>
                    <dd>{p.action}</dd>
                  </dl>
                </Card>
              );
            })}
          </div>
          <div className="section-heading">
            <h2>完整运营策略链</h2>
            <span>拉新 → 激活 → 留存 → 推荐</span>
          </div>
          <div className="grid two strategy-grid">
            {data.content.strategies.map((s, i) => (
              <Card
                key={s.title}
                title={s.title}
                eyebrow={"STRATEGY 0" + (i + 1)}
              >
                <p>{s.detail}</p>
                <div className="metric-line">
                  <Target size={15} />
                  {s.metric}
                </div>
              </Card>
            ))}
          </div>
          <Card title="创新玩法与AI工具" eyebrow="EXECUTION DESIGN">
            <div className="chips">
              {data.content.innovation?.map((t) => (
                <Badge key={t}>{t}</Badge>
              ))}
            </div>
            <div className="grid three">
              {data.content.ai_tools.map((t) => (
                <div className="inset" key={t.name}>
                  <h4>{t.name}</h4>
                  <p>{t.use}</p>
                  <small>{t.boundary}</small>
                </div>
              ))}
            </div>
          </Card>
          <div className="next-step">
            <span>下一步：把策略变成可调整的预算与转化假设。</span>
            <button
              className="button secondary"
              onClick={() => setTab("model")}
            >
              打开增长模型 <ArrowRight size={16} />
            </button>
          </div>
        </>
      ) : tab === "model" ? (
        <>
          <div className="grid growth-model">
            <Card
              title="可调增长漏斗"
              eyebrow="FUNNEL / ASSUMPTIONS"
              action={<Badge tone="orange">假设模型</Badge>}
            >
              <div className="funnel-controls">
                <label>
                  独立曝光假设 / 次
                  <input
                    type="number"
                    min="0"
                    max="100000000"
                    aria-label="曝光假设"
                    value={config.exposure}
                    onChange={(e) =>
                      setConfig({ ...config, exposure: Number(e.target.value) })
                    }
                  />
                </label>
                {rateFields.map(([key, label]) => (
                  <label key={key}>
                    {label} / %
                    <div className="range-row">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="1"
                        aria-label={label + "滑块"}
                        value={config[key] * 100}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            [key]: Number(e.target.value) / 100,
                          })
                        }
                      />
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="1"
                        aria-label={label}
                        value={Number((config[key] * 100).toFixed(2))}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            [key]: Number(e.target.value) / 100,
                          })
                        }
                      />
                    </div>
                  </label>
                ))}
              </div>
              <p className="source">
                漏斗逐层相乘，保留小数以表达期望人数。独立曝光假设与右侧渠道覆盖分别测算。
              </p>
            </Card>
            <Card title="从触达到留存" eyebrow="CONVERSION FLOW">
              <div className="funnel-chart">
                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                  <BarChart
                    layout="vertical"
                    data={result?.funnel ?? []}
                    margin={{ top: 15, bottom: 15, left: 0, right: 30 }}
                  >
                    <XAxis
                      type="number"
                      tick={{ fill: "#5b6d78", fontSize: 11 }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={70}
                      tick={{ fill: "#405663" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={chartTheme.tooltip}
                      cursor={{ fill: "#11665e08" }}
                    />
                    <Bar
                      isAnimationActive={false}
                      dataKey="value"
                      name="假设人数/次数"
                      radius={[0, 5, 5, 0]}
                    >
                      {(result?.funnel ?? []).map((_, i) => (
                        <Cell key={i} fill={chartTheme.funnel[i]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="funnel-numbers">
                {result?.funnel.map((f) => (
                  <div key={f.name}>
                    <small>{f.name}</small>
                    <strong>{num(f.value)}</strong>
                  </div>
                ))}
              </div>
            </Card>
          </div>
          <Card
            title="推广渠道与预算分配"
            eyebrow="BUDGET PLANNER"
            action={<Badge>所有单价可调 · 元 / 千次曝光</Badge>}
          >
            <div className="budget-allocation" aria-label="预算比例条">
              {config.channels.map((c, i) => (
                <span
                  key={c.name}
                  title={`${c.name}：${money(c.budget)}`}
                  style={{
                    flex: c.budget,
                    background: chartTheme.funnel[i % 5],
                  }}
                />
              ))}
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>渠道</th>
                    <th>预算 / 元</th>
                    <th>CPM / 元</th>
                    <th>预计覆盖 / 次</th>
                    <th>预计激活 / 人</th>
                    <th>激活CAC / 元</th>
                  </tr>
                </thead>
                <tbody>
                  {config.channels.map((c, i) => (
                    <tr key={c.name}>
                      <td>
                        <strong>{c.name}</strong>
                      </td>
                      <td>
                        <input
                          type="number"
                          min="0"
                          aria-label={c.name + "预算"}
                          value={c.budget}
                          onChange={(e) =>
                            setConfig({
                              ...config,
                              channels: config.channels.map((v, j) =>
                                j === i
                                  ? { ...v, budget: Number(e.target.value) }
                                  : v,
                              ),
                            })
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          min="1"
                          aria-label={c.name + "CPM"}
                          value={c.cpm}
                          onChange={(e) =>
                            setConfig({
                              ...config,
                              channels: config.channels.map((v, j) =>
                                j === i
                                  ? { ...v, cpm: Number(e.target.value) }
                                  : v,
                              ),
                            })
                          }
                        />
                      </td>
                      <td>{num(result?.channels[i]?.reach)}</td>
                      <td>{num(result?.channels[i]?.active)}</td>
                      <td>{money(result?.channels[i]?.cac)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="notice compact">
              预算情景对比：当前预算 {money(result?.budget)}
              ；预算均增加20%（CPM与转化率不变）时，预计激活{" "}
              {num((result?.channel_active ?? 0) * 1.2)} 人、预算{" "}
              {money((result?.budget ?? 0) * 1.2)}
              ，单位获客成本保持不变。此线性假设未考虑饱和与重复覆盖。
            </div>
            <p className="source">{result?.source}</p>
            {calcError && (
              <p role="alert" className="error-text">
                {calcError}
              </p>
            )}
          </Card>
          <div className="next-step">
            <span>参数变更已即时计算；点击右上“保存参数”后可跨刷新保留。</span>
            <button
              className="button secondary"
              onClick={() => setTab("execution")}
            >
              验证增长实验 <ArrowRight size={16} />
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="grid two">
            <Card
              title="A/B实验计算器"
              eyebrow="VALIDATION / ASSUMED DATA"
              action={<FlaskConical size={19} />}
            >
              <p>
                比较两组假设转化数据。真实执行应随机分流、固定窗口，并预先声明主要指标。
              </p>
              <div className="form-grid">
                {(
                  [
                    ["a_visitors", "A组参与人数"],
                    ["a_conversions", "A组转化人数"],
                    ["b_visitors", "B组参与人数"],
                    ["b_conversions", "B组转化人数"],
                  ] as const
                ).map(([k, label]) => (
                  <label key={k}>
                    {label}
                    <input
                      type="number"
                      min={k.endsWith("visitors") ? "1" : "0"}
                      aria-label={label}
                      value={experiment[k]}
                      onChange={(e) => {
                        setExperiment({
                          ...experiment,
                          [k]: Number(e.target.value),
                        });
                        setExpResult(null);
                      }}
                    />
                  </label>
                ))}
              </div>
              <button className="button" onClick={expRun} disabled={busy}>
                计算实验差异 <ArrowRight size={15} />
              </button>
              {expResult && (
                <div className="experiment-result">
                  <Badge tone={expResult.significant ? "green" : "orange"}>
                    {expResult.adequate ? "样本近似条件满足" : "样本不足"}
                  </Badge>
                  <div
                    className="experiment-bars"
                    aria-label="A和B的实际计算转化率"
                  >
                    {[
                      ["A", expResult.a_rate],
                      ["B", expResult.b_rate],
                    ].map(([name, rate]) => (
                      <div key={name}>
                        <span>{name}</span>
                        <i style={{ width: `${Number(rate) * 100}%` }} />
                        <span>{num(Number(rate) * 100)}%</span>
                      </div>
                    ))}
                  </div>
                  <h3>转化差异 {num(expResult.difference_pp, 2)} 个百分点</h3>
                  <p>
                    A {num(expResult.a_rate * 100)}% / B{" "}
                    {num(expResult.b_rate * 100)}% · 双侧 p={expResult.p_value}
                  </p>
                  <p>95%近似区间：[{expResult.ci95_pp.join(", ")}] 个百分点</p>
                  <p>{expResult.conclusion}</p>
                  <p>
                    检测5个百分点差异，粗估每组需 {expResult.sample_per_arm}{" "}
                    人（功效80%）。
                  </p>
                  <small>{expResult.source}</small>
                </div>
              )}
            </Card>
            <Card title="从假设到证据的实验设计" eyebrow="GROWTH EXPERIMENTS">
              {data.content.experiments.map((e) => (
                <div className="experiment-item" key={e.title}>
                  <h4>{e.title}</h4>
                  <p>
                    <strong>假设：</strong>
                    {e.hypothesis}
                  </p>
                  <p>
                    <strong>执行：</strong>
                    {e.method}
                  </p>
                  <p className="source">停止/复盘：{e.stop}</p>
                </div>
              ))}
            </Card>
          </div>
          <Card
            title="运营排期与执行看板"
            eyebrow="ACTION BOARD / PERSISTED"
            action={
              <button className="button secondary small" onClick={createTask}>
                <Plus size={15} />
                新增任务
              </button>
            }
          >
            <p className="source">
              {data.content.schedule_note}{" "}
              负责人为计划角色，非真实成员贡献声明。
            </p>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>任务 / 资源</th>
                    <th>负责角色</th>
                    <th>时间</th>
                    <th>成果 / 指标</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {data.tasks.map((t) => (
                    <tr key={t.id}>
                      <td>
                        <strong>{t.title}</strong>
                        <small>{t.resources}</small>
                      </td>
                      <td>{t.owner}</td>
                      <td>
                        {t.start}
                        <small>至 {t.end}</small>
                      </td>
                      <td>
                        {t.outcome}
                        <small>{t.metric}</small>
                      </td>
                      <td>
                        <select
                          aria-label={t.title + "状态"}
                          value={t.status}
                          onChange={(e) =>
                            void run(() =>
                              changeTask({
                                ...t,
                                status: e.target.value as Task["status"],
                              }),
                            )
                          }
                        >
                          <option>待开始</option>
                          <option>进行中</option>
                          <option>已完成</option>
                        </select>
                      </td>
                      <td>
                        <div className="actions">
                          <button
                            aria-label={"编辑" + t.title}
                            className="icon-button"
                            onClick={() => {
                              setNewTask(false);
                              setTask({ ...t });
                            }}
                          >
                            <Pencil size={15} />
                          </button>
                          <button
                            aria-label={"删除" + t.title}
                            className="icon-button"
                            onClick={() => setDeleting(t)}
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
            {data.tasks.length === 0 && (
              <p className="empty">暂无任务，请新增执行计划。</p>
            )}
          </Card>
          <Card title="复盘机制" eyebrow="LEARN & ITERATE">
            <div className="grid three">
              {data.content.review.map((r, i) => (
                <div className="inset" key={r}>
                  <span className="eyebrow">0{i + 1}</span>
                  <p>{r}</p>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
      {report && (
        <ReportViewer report={report} onClose={() => setReport(null)} />
      )}
      {task && (
        <TaskEditor
          initial={task}
          isNew={newTask}
          onClose={() => setTask(null)}
          onSave={(t) =>
            run(async () => {
              await api(
                newTask ? "/tasks" : "/tasks/" + t.id,
                newTask ? "POST" : "PUT",
                t,
              );
              await reload();
              setTask(null);
              notify("任务已持久化保存");
            })
          }
          busy={busy}
        />
      )}
      {deleting && (
        <Modal title="删除运营任务" onClose={() => setDeleting(null)}>
          <p>删除“{deleting.title}”？只影响本地教学数据库。</p>
          <div className="actions end">
            <button
              className="button secondary"
              onClick={() => setDeleting(null)}
            >
              取消
            </button>
            <button
              className="button danger"
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  await api("/tasks/" + deleting.id, "DELETE");
                  await reload();
                  setDeleting(null);
                  notify("任务已删除");
                })
              }
            >
              确认删除
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
function TaskEditor({
  initial,
  isNew,
  onClose,
  onSave,
  busy,
}: {
  initial: Task;
  isNew: boolean;
  onClose: () => void;
  onSave: (t: Task) => void;
  busy: boolean;
}) {
  const [t, setT] = useState(initial);
  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSave(t);
  };
  return (
    <Modal title={isNew ? "新增运营任务" : "编辑运营任务"} onClose={onClose}>
      <form onSubmit={submit}>
        <div className="form-grid">
          {(
            [
              "id",
              "title",
              "owner",
              "start",
              "end",
              "resources",
              "outcome",
              "metric",
            ] as const
          ).map((k, i) => (
            <label key={k}>
              {
                [
                  "任务编号",
                  "任务名称",
                  "负责人角色",
                  "开始日期",
                  "结束日期",
                  "所需资源",
                  "预期成果",
                  "衡量指标",
                ][i]
              }
              <input
                type={k === "start" || k === "end" ? "date" : "text"}
                value={t[k]}
                required={["id", "title", "owner", "start", "end"].includes(k)}
                disabled={k === "id" && !isNew}
                onChange={(e) => setT({ ...t, [k]: e.target.value })}
              />
            </label>
          ))}
          <label>
            状态
            <select
              value={t.status}
              onChange={(e) =>
                setT({ ...t, status: e.target.value as Task["status"] })
              }
            >
              <option>待开始</option>
              <option>进行中</option>
              <option>已完成</option>
            </select>
          </label>
        </div>
        <div className="actions end">
          <button type="button" className="button secondary" onClick={onClose}>
            取消
          </button>
          <button className="button" disabled={busy} type="submit">
            <Save size={15} />
            保存任务
          </button>
        </div>
      </form>
    </Modal>
  );
}
