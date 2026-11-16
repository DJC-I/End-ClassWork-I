import { chartTheme } from "./design";
import { useEffect, useRef, useId, type ReactNode } from "react";
import {
  X,
  ArrowUpRight,
  Download,
  Printer,
  Route,
  Clock3,
  ShieldCheck,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { dt, money, num, cargoNames } from "./api";
import type { Network, Scenario, Report, Decision, Plan } from "./types";

export function Card({
  title,
  eyebrow,
  action,
  children,
  className = "",
}: {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={"card " + className}>
      {(title || action) && (
        <div className="card-head">
          <div>
            {eyebrow && <span className="eyebrow">{eyebrow}</span>}
            <h3>{title}</h3>
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
export function Stat({
  label,
  value,
  detail,
  accent = false,
}: {
  label: string;
  value: ReactNode;
  detail: string;
  accent?: boolean;
}) {
  return (
    <div className={"stat " + (accent ? "stat-accent" : "")}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty">
      <Route size={28} />
      <p>{children}</p>
    </div>
  );
}
export function Badge({
  children,
  tone = "",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
export function SectionTitle({
  kicker,
  title,
  description,
  action,
}: {
  kicker: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="section-title">
      <div>
        <span className="eyebrow">{kicker}</span>
        <h1>
          {title}
          <span className="title-dot">.</span>
        </h1>
        <p>{description}</p>
      </div>
      <div className="actions">{action}</div>
    </div>
  );
}
export function Modal({
  title,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  const dialog = useRef<HTMLDivElement>(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const focusable = () =>
      Array.from(
        dialog.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),summary,[tabindex="0"]',
        ) ?? [],
      ).filter((el) => el.getClientRects().length > 0);
    focusable()[0]?.focus();
    const f = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeRef.current();
      if (e.key === "Tab") {
        const items = focusable();
        const first = items[0],
          last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", f);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", f);
      document.body.style.overflow = prev;
      previous?.focus();
    };
  }, []);
  return (
    <div
      className="modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={dialog}
        className={"modal " + (wide ? "modal-wide" : "")}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="modal-head">
          <h2>{title}</h2>
          <button
            className="icon-button"
            aria-label="关闭弹窗"
            onClick={onClose}
          >
            <X />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
export function NetworkMap({
  network,
  scenario,
  route = [],
  affected = [],
}: {
  network: Network;
  scenario: Scenario;
  route?: string[];
  affected?: string[];
}) {
  const arrowId = useId();
  const routeEdges = new Set(
    route.slice(0, -1).map((n, i) => n + "-" + route[i + 1]),
  );
  return (
    <div
      className="network-wrap"
      tabIndex={0}
      aria-label="运输网络，可横向滚动"
    >
      <div className="map-grid" />
      <svg
        viewBox="0 0 880 435"
        className="network"
        role="img"
        aria-label="北京天津模拟运输网络拓扑图"
      >
        <defs>
          <marker
            id={arrowId}
            viewBox="0 0 10 10"
            refX="30"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#607382" />
          </marker>
        </defs>
        <text x="40" y="40" className="map-region">
          BEIJING — TIANJIN / SIMULATED NETWORK
        </text>
        {network.edges.map((e) => {
          const a = network.nodes.find((n) => n.id === e.source)!;
          const b = network.nodes.find((n) => n.id === e.target)!;
          const chosen = routeEdges.has(e.id);
          const bad =
            affected.includes(e.id) || (scenario.edge_factors[e.id] ?? 0) > 0.5;
          return (
            <g key={e.id}>
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                className={
                  chosen
                    ? "map-line selected"
                    : bad
                      ? "map-line warning"
                      : "map-line"
                }
                markerEnd={`url(#${arrowId})`}
              />
              <text
                x={(a.x + b.x) / 2}
                y={(a.y + b.y) / 2 + (e.id === "LF-TJ" ? 68 : -9)}
                textAnchor="middle"
                className="map-distance"
              >
                {e.km} km
              </text>
            </g>
          );
        })}
        {network.nodes.map((n) => {
          const bad = (scenario.node_factors[n.id] ?? 0) > 0.5;
          return (
            <g key={n.id}>
              <circle
                cx={n.x}
                cy={n.y}
                r="22"
                fill={bad ? "#f5e3d0" : "#e3efe9"}
                stroke={bad ? "#a45026" : "#11665e"}
                strokeWidth="1.3"
              />
              <circle
                cx={n.x}
                cy={n.y}
                r="5"
                fill={bad ? "#a45026" : "#11665e"}
              />
              <text
                x={n.x}
                y={n.y + 42}
                textAnchor="middle"
                className="map-label"
              >
                {n.name}
              </text>
              <text
                x={n.x}
                y={n.y + 59}
                textAnchor="middle"
                className="map-code"
              >
                {n.id} / {n.capacity} t
              </text>
            </g>
          );
        })}
      </svg>
      <div className="map-legend">
        <span>
          <i className="lime" />
          选中方案
        </span>
        <span>
          <i className="orange" />
          天气影响
        </span>
        <span>
          <i className="gray" />
          模拟可用连接
        </span>
      </div>
      <p className="source">
        教学拓扑图 · 单向连接 · 线条非真实道路，km为模拟路程，预警不等于封路
      </p>
    </div>
  );
}
export function CompareChart({
  data,
  unit = "",
}: {
  data: Record<string, string | number>[];
  unit?: string;
}) {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <BarChart
          data={data}
          margin={{ left: 0, right: 10, top: 15, bottom: 0 }}
        >
          <CartesianGrid stroke="#d9e1e2" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fill: "#5b6d78", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#5b6d78", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            unit={unit}
            width={55}
          />
          <Tooltip
            contentStyle={chartTheme.tooltip}
            cursor={{ fill: "#11665e08" }}
          />
          <Legend />
          <Bar
            isAnimationActive={false}
            name="原计划"
            dataKey="原计划"
            fill={chartTheme.before}
            radius={[4, 4, 0, 0]}
          />
          <Bar
            isAnimationActive={false}
            name="优化方案"
            dataKey="优化方案"
            fill={chartTheme.after}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export function PlanTable({ decision }: { decision: Decision }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>应对方案</th>
            <th>路径 / 发运</th>
            <th>运输 / 到货</th>
            <th>成本 / 增量</th>
            <th>延误 / 风险</th>
            <th>综合分↓</th>
          </tr>
        </thead>
        <tbody>
          {decision.plans.map((p) => (
            <tr
              key={p.id}
              className={
                p.id === decision.recommendation.id ? "recommended-row" : ""
              }
            >
              <td>
                <strong>{p.name}</strong>
                {p.id === decision.recommendation.id && (
                  <Badge tone="green">推荐</Badge>
                )}
              </td>
              {p.feasible ? (
                <>
                  <td>
                    <span>{p.route?.join(" → ")}</span>
                    <small>{dt(p.departure)} 发运</small>
                  </td>
                  <td>
                    {num(p.hours, 2)} h<small>{dt(p.arrival)} 到货</small>
                  </td>
                  <td>
                    {money(p.cost)}
                    <small>增量 {money(p.extra_cost)}</small>
                  </td>
                  <td>
                    {num(p.delay_hours, 2)} h
                    <small>
                      风险 {num(p.risk)} / 100 · {p.on_time ? "准时" : "延误"}
                    </small>
                  </td>
                  <td>{num(p.score, 3)}</td>
                </>
              ) : (
                <td colSpan={5}>
                  <Badge tone="muted">不适用</Badge> {p.reason}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export function ReportViewer({
  report,
  onClose,
}: {
  report: Report;
  onClose: () => void;
}) {
  const selected =
    report.kind === "decision"
      ? report.plans.find((p) => p.id === report.recommendation.id)
      : undefined;
  return (
    <Modal
      title={
        report.kind === "growth"
          ? "运营策略报告"
          : report.kind === "decision"
            ? "气象物流决策报告"
            : "情景仿真报告"
      }
      onClose={onClose}
      wide
    >
      <div className="report-toolbar">
        <span className="source">
          快照 {report.id.slice(0, 8)} · {dt(report.created_at)}
        </span>
        <div className="actions">
          <a
            className="button secondary"
            href={"/api/reports/" + report.id + "/download"}
            download
          >
            <Download size={15} />
            下载报告
          </a>
          <button className="button secondary" onClick={() => window.print()}>
            <Printer size={15} />
            打印
          </button>
        </div>
      </div>
      <div className="report-body">
        <div className="notice">{report.disclaimer}</div>
        {report.kind === "decision" ? (
          <>
            <h3>
              {report.order.id} · {cargoNames[report.order.cargo]} ·{" "}
              {report.order.weight} t
            </h3>
            <p>
              模拟天气：{report.scenario.name}；{report.scenario.warning}
              ；有效期 {dt(report.scenario.valid_from)}—
              {dt(report.scenario.valid_to)}。
            </p>
            <p>
              原计划：{report.order.route.join(" → ")}，
              {dt(report.order.departure)} 发运，承诺{" "}
              {dt(report.order.deadline)} 送达。
            </p>
            <div className="stats three">
              <Stat
                label="原计划风险"
                value={report.risk.score + "/100"}
                detail={report.risk.level}
              />
              <Stat
                label="推荐方案成本"
                value={money(selected?.cost)}
                detail="含天气及策略增量"
              />
              <Stat
                label="推荐方案时长"
                value={num(selected?.hours, 2) + " h"}
                detail={"延误 " + num(selected?.delay_hours, 2) + " h"}
              />
            </div>
            <h3>评估依据</h3>
            <ul>
              {report.risk.reasons.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
            <ul>
              {report.risk.basis.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
            <h3>方案对比</h3>
            <PlanTable decision={report} />
            <h3>推荐：{report.recommendation.name}</h3>
            <p>{report.recommendation.reason}</p>
            <details>
              <summary>完整工具输入输出</summary>
              <pre>{JSON.stringify(report.trace, null, 2)}</pre>
            </details>
          </>
        ) : report.kind === "growth" ? (
          <>
            <h3>平台研究与用户定位</h3>
            <p>{report.plan.platform}</p>
            <div className="stats three">
              <Stat
                label="假设预算"
                value={money(report.metrics.budget)}
                detail="渠道与AI制作资源"
              />
              <Stat
                label="预计激活"
                value={num(report.metrics.channel_active) + " 人"}
                detail="未去重覆盖模型"
              />
              <Stat
                label="预计激活CAC"
                value={money(report.metrics.cac)}
                detail="假设成本 / 预计激活人数"
              />
            </div>
            <h3>用户画像</h3>
            {report.plan.personas.map((p) => (
              <p key={p.name}>
                <strong>{p.name}：</strong>
                {p.need}；通过{p.channel}触达；{p.action}
              </p>
            ))}
            <h3>运营行动</h3>
            {report.plan.strategies.map((s) => (
              <p key={s.title}>
                <strong>{s.title}：</strong>
                {s.detail}；衡量：{s.metric}
              </p>
            ))}
            <h3>渠道与预算</h3>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>渠道</th>
                    <th>预算</th>
                    <th>预计覆盖</th>
                    <th>预计激活</th>
                  </tr>
                </thead>
                <tbody>
                  {report.metrics.channels.map((c) => (
                    <tr key={c.name}>
                      <td>{c.name}</td>
                      <td>{money(c.budget)}</td>
                      <td>{num(c.reach)} 次</td>
                      <td>{num(c.active)} 人</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3>执行排期</h3>
            {report.tasks.map((t) => (
              <p key={t.id}>
                {t.start}—{t.end} · {t.title} · {t.owner} · {t.status} ·{" "}
                {t.metric}
              </p>
            ))}
            <h3>增长验证与复盘</h3>
            {report.plan.experiments.map((e) => (
              <p key={e.title}>
                {e.title}：{e.hypothesis}；{e.method}；停止条件：{e.stop}
              </p>
            ))}
            {report.plan.review.map((r) => (
              <p key={r}>{r}</p>
            ))}
          </>
        ) : (
          <>
            <h3>{report.scenario.name} · 配对压力回放</h3>
            <p>{report.method}</p>
            <CompareChart
              data={[
                {
                  name: "模拟准时率 %",
                  原计划: report.before.on_time_rate,
                  优化方案: report.after.on_time_rate,
                },
              ]}
            />
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>订单</th>
                    <th>推荐</th>
                    <th>原延误h</th>
                    <th>优化延误h</th>
                    <th>原成本</th>
                    <th>优化成本</th>
                  </tr>
                </thead>
                <tbody>
                  {report.rows.map((r) => (
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
            <p>版本/种子：{report.seed}</p>
          </>
        )}
      </div>
    </Modal>
  );
}
export function PlanSummary({ plan }: { plan: Plan }) {
  return (
    <div className="plan-summary">
      <Route size={20} />
      <div>
        <strong>{plan.name}</strong>
        <p>{plan.route?.join(" → ")}</p>
      </div>
      <span>
        <Clock3 size={14} /> {num(plan.hours, 2)} h
      </span>
      <span>
        <ShieldCheck size={14} /> {num(plan.risk)}分
      </span>
      <ArrowUpRight size={18} />
    </div>
  );
}
