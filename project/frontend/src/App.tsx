import { useEffect, useState, useCallback } from "react";
import {
  ArrowUpRight,
  ArrowRight,
  LayoutDashboard,
  TrendingUp,
  Route,
  Play,
  BookOpen,
  Maximize,
  Minimize,
  Menu,
  X,
  RotateCcw,
  Activity,
  Layers3,
  ShieldCheck,
  Check,
  Triangle,
  WifiOff,
} from "lucide-react";
import { api } from "./api";
import type { Bootstrap } from "./types";
import {
  Card,
  Stat,
  SectionTitle,
  NetworkMap,
  Badge,
  Modal,
} from "./components";
import Growth from "./Growth";
import Logistics from "./Logistics";

const nav = [
  { path: "/", name: "总览门户", sub: "Overview", icon: LayoutDashboard },
  {
    path: "/growth",
    name: "增长运营工作台",
    sub: "Growth strategy",
    icon: TrendingUp,
  },
  {
    path: "/logistics",
    name: "气象物流决策",
    sub: "Weather intelligence",
    icon: Route,
  },
  { path: "/demo", name: "课堂演示", sub: "Guided demo", icon: Play },
  {
    path: "/about",
    name: "方法与数据来源",
    sub: "Method & sources",
    icon: BookOpen,
  },
];
export default function App() {
  const [path, setPath] = useState(window.location.pathname),
    [data, setData] = useState<Bootstrap | null>(null),
    [error, setError] = useState(""),
    [toast, setToast] = useState(""),
    [mobile, setMobile] = useState(false),
    [fullscreen, setFullscreen] = useState(false),
    [reset, setReset] = useState(false),
    [busy, setBusy] = useState(false);
  const notify = useCallback((s: string) => setToast(s), []);
  const load = useCallback(async () => {
    setError("");
    try {
      setData(await api<Bootstrap>("/bootstrap"));
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);
  useEffect(() => {
    void load();
    const p = () => setPath(window.location.pathname);
    const f = () => setFullscreen(!!document.fullscreenElement);
    window.addEventListener("popstate", p);
    document.addEventListener("fullscreenchange", f);
    return () => {
      window.removeEventListener("popstate", p);
      document.removeEventListener("fullscreenchange", f);
    };
  }, [load]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 4500);
    return () => clearTimeout(t);
  }, [toast]);
  const go = (p: string) => {
    history.pushState({}, "", p);
    setPath(p);
    setMobile(false);
    window.scrollTo({ top: 0 });
  };
  const full = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      notify("当前浏览器不支持全屏，请使用 F11");
    }
  };
  const doReset = async () => {
    setBusy(true);
    try {
      await api("/demo/reset", "POST");
      await load();
      setReset(false);
      notify("教学数据已重置；订单、任务、参数和报告恢复初始状态");
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className={"app " + (mobile ? "nav-open" : "")} data-page={path}>
      <a className="skip-link" href="#workspace-content">
        跳至正文
      </a>
      <aside className="sidebar">
        <a
          href="/"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            go("/");
          }}
        >
          <span className="brand-mark">
            <Triangle size={25} />
          </span>
          <span>
            SkyRoute<span className="brand-ai">AI</span>
            <small>天气智运 · 增长决策</small>
          </span>
        </a>
        <div className="workspace-tag">
          <span className="status-dot" />
          校园竞赛工作空间<span>V1.0</span>
        </div>
        <span className="nav-label">WORKSPACE / 工作台</span>
        <nav aria-label="主要导航">
          {nav.map((n) => (
            <a
              key={n.path}
              aria-current={path === n.path ? "page" : undefined}
              href={n.path}
              className={path === n.path ? "active" : ""}
              onClick={(e) => {
                e.preventDefault();
                go(n.path);
              }}
            >
              <n.icon size={19} />
              <span>
                {n.name}
                <small>{n.sub}</small>
              </span>
              {path === n.path && <span className="nav-active-dot" />}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-card">
            <WifiOff size={18} />
            <strong>本地优先，稳定演示</strong>
            <p>
              核心流程无需模型密钥
              <br />
              所有业务数据存储于 SQLite
            </p>
            <Badge tone="green">{data?.health.mode ?? "连接中"}</Badge>
          </div>
          <div className="team-line">
            <span className="avatar">SR</span>
            <div>
              人工智能导论<small>北京物资学院 · 课程作品</small>
            </div>
          </div>
        </div>
      </aside>
      {mobile && (
        <div className="nav-overlay" onClick={() => setMobile(false)} />
      )}
      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-expanded={mobile}
              aria-label="切换导航"
              onClick={() => setMobile(!mobile)}
            >
              {mobile ? <X /> : <Menu />}
            </button>
            <span>工作空间</span>
            <span>/</span>
            <strong>{nav.find((n) => n.path === path)?.name ?? "页面"}</strong>
          </div>
          <div className="top-actions">
            <span className="top-date">
              2026.11.16 <span>教学数据基准日</span>
            </span>
            <span className="status-live">
              <i />
              本地服务
            </span>
            <button
              className="icon-button"
              aria-label={fullscreen ? "退出全屏" : "进入全屏"}
              title="课堂投影全屏"
              onClick={() => void full()}
            >
              {fullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
            </button>
          </div>
        </header>
        <div className="page" id="workspace-content" tabIndex={-1}>
          <div className="global-notice">
            <span>
              <span className="status-dot" />
              教学模拟工作空间
            </span>
            <span>物流、气象与增长测算均为模拟或假设 · 不用于真实运输调度</span>
            <button onClick={() => go("/about")}>
              查看依据 <ArrowUpRight size={13} />
            </button>
          </div>
          {error ? (
            <div className="load-state">
              <h2>连接服务失败</h2>
              <p role="alert">{error}</p>
              <button className="button" onClick={() => void load()}>
                重新连接
              </button>
              <p>
                请先启动后端：python -m uvicorn backend.main:app --host
                127.0.0.1 --port 8000
              </p>
            </div>
          ) : !data ? (
            <div className="load-state">
              <div className="spinner" />
              <p>正在读取本地业务数据…</p>
            </div>
          ) : path === "/growth" ? (
            <Growth data={data} reload={load} notify={notify} />
          ) : path === "/logistics" ? (
            <Logistics data={data} reload={load} notify={notify} />
          ) : path === "/demo" ? (
            <Demo go={go} reset={() => setReset(true)} busy={busy} />
          ) : path === "/about" ? (
            <About />
          ) : path === "/" ? (
            <Home data={data} go={go} />
          ) : (
            <div className="load-state">
              <h2>页面不存在</h2>
              <button className="button" onClick={() => go("/")}>
                返回首页
              </button>
            </div>
          )}
          <footer>
            <span>SkyRoute AI · 双赛题本地教学应用</span>
            <span>数据可追溯 · 计算可解释 · 结果可复现</span>
          </footer>
        </div>
      </main>
      {toast && (
        <div role="status" className="toast">
          <Check size={17} />
          {toast}
          <button aria-label="关闭提示" onClick={() => setToast("")}>
            <X size={15} />
          </button>
        </div>
      )}
      {reset && (
        <Modal title="重置教学演示数据" onClose={() => setReset(false)}>
          <p>
            此操作只重置本项目数据库，将删除你在应用中新增的订单、任务与历史报告，恢复六条模拟订单及初始运营参数。
          </p>
          <div className="actions end">
            <button
              className="button secondary"
              onClick={() => setReset(false)}
            >
              取消
            </button>
            <button
              className="button"
              disabled={busy}
              onClick={() => void doReset()}
            >
              <RotateCcw size={16} />
              {busy ? "重置中…" : "确认重置教学数据"}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
function Home({ data, go }: { data: Bootstrap; go: (p: string) => void }) {
  const scenario = data.scenarios.find((s) => s.id === data.current_scenario)!;
  return (
    <>
      <div className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <span className="tiny-line" /> SKYROUTE / DECISION STUDIO
          </span>
          <h1>
            把复杂风险，
            <br />
            变成清楚的<span>下一步。</span>
          </h1>
          <p>
            一个工作空间，连接增长策略与运输决策。
            <br />
            一套可解释、可交互、可离线演示的双赛题工作台。
          </p>
          <div className="actions">
            <button className="button" onClick={() => go("/demo")}>
              <Play size={16} fill="currentColor" />
              开始课堂演示
              <ArrowUpRight size={17} />
            </button>
            <button
              className="button secondary"
              onClick={() => go("/logistics")}
            >
              进入决策工作台
              <ArrowRight size={16} />
            </button>
          </div>
          <div className="hero-meta">
            <span>
              <ShieldCheck size={15} />
              规则引擎可执行
            </span>
            <span>
              <Layers3 size={15} />
              双赛题独立展示
            </span>
            <span>
              <Activity size={15} />
              输入输出可追溯
            </span>
          </div>
        </div>
        <div className="hero-network">
          <div className="hero-network-head">
            <span className="eyebrow">THE CORRIDOR / 京津走廊</span>
            <Badge tone="orange">{scenario.name} · 教学模拟</Badge>
          </div>
          <NetworkMap network={data.network} scenario={scenario} />
          <div className="network-caption">
            <strong>
              {data.network.nodes.length} 个节点 / {data.network.edges.length}{" "}
              条有向连接
            </strong>
            <span>与决策工作台使用同一网络数据</span>
          </div>
        </div>
      </div>
      <div className="stats">
        <Stat
          label="竞赛业务模块"
          value="02"
          detail="运营增长 + 气象物流"
          accent
        />
        <Stat
          label="模拟运输订单"
          value={String(data.orders.length).padStart(2, "0")}
          detail="数据来自本地业务数据库"
        />
        <Stat
          label="区域运输节点"
          value={String(data.network.nodes.length).padStart(2, "0")}
          detail="北京—天津模拟走廊"
        />
        <Stat label="可复现场景" value="03" detail="正常 · 暴雨 · 暴雪大风" />
      </div>
      <div className="section-heading">
        <h2>从问题到行动的两个工作台</h2>
        <span>一套平台 · 两条完整业务链</span>
      </div>
      <div className="grid two">
        <button
          className="workspace-card growth-entry"
          onClick={() => go("/growth")}
        >
          <div className="workspace-top">
            <span className="workspace-icon">
              <TrendingUp />
            </span>
            <Badge>赛题一 / 运营方案</Badge>
            <ArrowUpRight />
          </div>
          <h2>增长有策略，执行有依据</h2>
          <p>
            用户画像、渠道预算、增长漏斗、运营排期与 A/B
            实验，将想法变成可衡量的行动计划。
          </p>
          <div className="mini-funnel">
            <i style={{ width: "100%" }}>曝光</i>
            <i style={{ width: "78%" }}>访问</i>
            <i style={{ width: "55%" }}>激活</i>
            <i style={{ width: "32%" }}>留存</i>
          </div>
          <div className="workspace-footer">
            DataClawHub 增长运营工作台
            <span>
              进入工作台 <ArrowRight size={16} />
            </span>
          </div>
        </button>
        <button
          className="workspace-card logistics-entry"
          onClick={() => go("/logistics")}
        >
          <div className="workspace-top">
            <span className="workspace-icon blue">
              <Route />
            </span>
            <Badge>赛题二 / AI 应用</Badge>
            <ArrowUpRight />
          </div>
          <h2>预见天气，优化每一程</h2>
          <p>
            将气象、订单与图网络串联，计算受影响区段，比较四类运输应对策略，验证优化价值。
          </p>
          <div className="mini-flow">
            气象输入 <ArrowRight size={17} /> 风险评估 <ArrowRight size={17} />{" "}
            方案决策 <ArrowRight size={17} /> 仿真验证
          </div>
          <div className="workspace-footer">
            气象驱动物流风险预警系统
            <span>
              进入工作台 <ArrowRight size={16} />
            </span>
          </div>
        </button>
      </div>
      <div className="grid home-bottom">
        <Card
          title="从输入到行动，保留每一步依据"
          eyebrow="SYSTEM / EXPLAINABLE BY DESIGN"
        >
          <div className="system-chain">
            {[
              ["01", "业务输入", "订单、天气场景、增长假设"],
              ["02", "校验与计算", "图搜索、规则评分、统计检验"],
              ["03", "方案与报告", "比较结果、工具轨迹、输入快照"],
            ].map(([n, t, d]) => (
              <div key={n}>
                <span>{n}</span>
                <div>
                  <h3>{t}</h3>
                  <p>{d}</p>
                </div>
                <ArrowRight size={20} />
              </div>
            ))}
          </div>
          <button className="text-button" onClick={() => go("/about")}>
            了解计算方法与数据边界 <ArrowRight size={16} />
          </button>
        </Card>
        <Card title="为可靠演示而构建" eyebrow="BUILT TO WORK">
          <div className="feature-list">
            {[
              [
                "01",
                "真实的前后端链路",
                "React + FastAPI，业务数据落在SQLite。",
              ],
              [
                "02",
                "有依据的决策过程",
                "可达路径、成本公式、风险依据与工具轨迹。",
              ],
              [
                "03",
                "透明的数据边界",
                "模拟气象、假设增长，不把目标当成成果。",
              ],
            ].map(([n, t, d]) => (
              <div key={n}>
                <span>{n}</span>
                <div>
                  <h4>{t}</h4>
                  <p>{d}</p>
                </div>
              </div>
            ))}
          </div>
          <button className="text-button" onClick={() => go("/about")}>
            查看技术与数据说明 <ArrowUpRight size={16} />
          </button>
        </Card>
      </div>
    </>
  );
}
function Demo({
  go,
  reset,
  busy,
}: {
  go: (p: string) => void;
  reset: () => void;
  busy: boolean;
}) {
  const [elapsed, setElapsed] = useState(0);
  const [running, setRunning] = useState(false);
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => setElapsed((t) => t + 1), 1000);
    return () => window.clearInterval(timer);
  }, [running]);
  return (
    <div className="demo-page">
      <SectionTitle
        kicker="CLASSROOM / GUIDED DEMO"
        title="课堂演示，沿着这条路径"
        description="先重置教学数据，再完成两道赛题。步骤与真实功能对应，可在无模型密钥时复现。"
        action={
          <button className="button secondary" onClick={reset} disabled={busy}>
            <RotateCcw size={16} />
            重置演示数据
          </button>
        }
      />
      <div className="demo-console">
        <div>
          <span className="eyebrow">PRESENTATION DESK / 单人讲解</span>
          <p>6分钟讲解 · 两次现场操作 · 无网络也可完成核心流程</p>
        </div>
        <div className="demo-time" aria-label="演示计时">
          {String(Math.floor(elapsed / 60)).padStart(2, "0")}:
          {String(elapsed % 60).padStart(2, "0")}
        </div>
        <div className="actions">
          <button className="button secondary" onClick={() => go("/growth")}>
            打开增长演示
          </button>
          <button className="button secondary" onClick={() => go("/logistics")}>
            打开物流演示
          </button>
          <button
            className="button secondary"
            onClick={() => setRunning(!running)}
          >
            {running ? "暂停计时" : "开始计时"}
          </button>
          <button
            className="button secondary"
            onClick={() => {
              setRunning(false);
              setElapsed(0);
            }}
          >
            归零
          </button>
        </div>
      </div>
      <div className="grid two">
        <Card title="01 / 平台增长运营" eyebrow="约 90 秒">
          <ol className="demo-steps">
            <li>
              <strong>洞察用户</strong>
              <p>打开运营工作台，查看四类用户画像和完整运营策略。</p>
            </li>
            <li>
              <strong>调整假设</strong>
              <p>
                将校园社群预算从600改为900元；调整访问转化率，观察预算和漏斗变化，点击保存。
              </p>
            </li>
            <li>
              <strong>检查实验</strong>
              <p>
                切到“实验与执行”，输入A组200/30、B组200/40，阅读置信区间与样本提醒。
              </p>
            </li>
            <li>
              <strong>落实行动</strong>
              <p>编辑运营任务状态，生成运营报告，查看并下载可追溯的计划。</p>
            </li>
          </ol>
          <button className="button" onClick={() => go("/growth")}>
            进入赛题一 <ArrowRight size={16} />
          </button>
        </Card>
        <Card title="02 / 气象物流决策" eyebrow="约 120 秒">
          <ol className="demo-steps">
            <li>
              <strong>选择模拟天气</strong>
              <p>打开物流工作台，选择“暴雨风险”，选中SR-001。</p>
            </li>
            <li>
              <strong>运行风险分析</strong>
              <p>点击“运行风险分析”，查看风险依据、受影响线路和四类方案。</p>
            </li>
            <li>
              <strong>比较可执行方案</strong>
              <p>调整成本、时间、风险权重后重新计算；展开智能体工具轨迹。</p>
            </li>
            <li>
              <strong>验证与报告</strong>
              <p>
                运行情景仿真，比较准时率、延误、成本与高风险数量，再查看决策报告。
              </p>
            </li>
          </ol>
          <button className="button" onClick={() => go("/logistics")}>
            进入赛题二 <ArrowRight size={16} />
          </button>
        </Card>
      </div>
      <div className="notice">
        投影提示：右上角可进入全屏。所有日期为固定教学基准，不读取在线天气。重置会清除本项目自建业务记录和报告；可先下载需要保留的报告。
      </div>
    </div>
  );
}
function About() {
  return (
    <>
      <SectionTitle
        kicker="TRANSPARENCY / METHODS"
        title="每个结果，都有边界与依据"
        description="清楚区分已实现能力、教学假设、待核实信息与真实业务结果。"
      />
      <div className="grid two methods-grid">
        <Card title="技术与数据流">
          <div className="stack-flow">
            React + TypeScript → REST API → FastAPI → SQLite
          </div>
          <p>
            前端负责交互与可视化，后端校验并持久化。图算法与天气规则产生决策数值，可选模型仅解释已计算的快照。无密钥时为规则模式，不伪装大模型推理。
          </p>
          <p>
            {/\bElectron\//.test(navigator.userAgent) ? (
              <>桌面版本关闭API调试入口。</>
            ) : (
              <>
                API交互规范可在本地{" "}
                <a href="/docs" target="_blank" rel="noreferrer">
                  /docs
                </a>{" "}
                查看。
              </>
            )}
            所有模拟时间统一使用北京时间（UTC+8）。
          </p>
        </Card>
        <Card title="运输图与天气假设">
          <p>
            北京、通州、廊坊、武清、蓟州、宝坻、天津为近似地理位置；连接、方向、距离、耗时、费用、运力为版本化教学配置。示意线条不代表真实公路，公里数不用直线距离代替。
          </p>
          <p>
            正常、暴雨、暴雪大风为固定时间窗的模拟天气。天气预警只影响模拟速度、成本和风险，不自动封路。每条方案都校验图连通、方向和载重。
          </p>
          <p>
            提前发运只对待发运订单适用。运输中订单缺少实时位置，其他方案只能视作计划级反事实比较，执行前需人工调度确认。
          </p>
        </Card>
        <Card title="模型与统计方法">
          <p>
            按通行区段与天气有效期重叠量计算损失，叠加降雨、降雪、大风、能见度、温度、货物敏感度、优先级与时限。风险分是规则量表，不是事故概率。
          </p>
          <p>
            方案按当前候选集成本、时长、风险做最小最大归一化后加权。压力回放使用0.85、1、1.15倍严重度，固定输入、配对比较，不宣称真实准时概率。
          </p>
          <p>
            运营漏斗和渠道覆盖是独立假设模型；覆盖未去重。A/B为双侧两比例z检验，样本不足不下结论，未开展真实推广或签订合作。
          </p>
        </Card>
      </div>
    </>
  );
}
