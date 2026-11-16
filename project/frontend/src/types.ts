export type Cargo = "general" | "cold" | "fragile";
export interface Order {
  id: string;
  origin: string;
  destination: string;
  cargo: Cargo;
  weight: number;
  departure: string;
  deadline: string;
  priority: number;
  route: string[];
  base_cost: number;
  base_hours: number;
  status: "待发运" | "运输中" | "已送达";
}
export interface Task {
  id: string;
  title: string;
  owner: string;
  start: string;
  end: string;
  status: "待开始" | "进行中" | "已完成";
  resources: string;
  outcome: string;
  metric: string;
}
export interface Node {
  id: string;
  name: string;
  city: string;
  x: number;
  y: number;
  lat: number;
  lon: number;
  capacity: number;
}
export interface Edge {
  id: string;
  source: string;
  target: string;
  km: number;
  hours: number;
  toll: number;
  capacity: number;
  available: boolean;
  corridor: string;
}
export interface Network {
  nodes: Node[];
  edges: Edge[];
  version: string;
  source: string;
}
export interface Scenario {
  id: string;
  name: string;
  tag: string;
  description: string;
  valid_from: string;
  valid_to: string;
  rain: number;
  snow: number;
  wind: number;
  visibility: number;
  temperature: number;
  warning: string;
  edge_factors: Record<string, number>;
  node_factors: Record<string, number>;
  source: string;
}
export interface Weights {
  cost: number;
  time: number;
  risk: number;
}
export interface GrowthConfig {
  exposure: number;
  visit_rate: number;
  register_rate: number;
  activate_rate: number;
  retain_rate: number;
  channels: { name: string; budget: number; cpm: number }[];
}
export interface GrowthResult {
  funnel: { name: string; value: number }[];
  budget: number;
  channel_reach: number;
  channel_active: number;
  channel_retained: number;
  cac: number | null;
  channels: {
    name: string;
    budget: number;
    cpm: number;
    reach: number;
    active: number;
    cac: number | null;
  }[];
  source: string;
}
export interface Content {
  platform: string;
  verified?: string[];
  personas: {
    name: string;
    tag: string;
    need: string;
    channel: string;
    motivation: string;
    barrier: string;
    action: string;
  }[];
  strategies: { title: string; detail: string; metric: string }[];
  experiments: {
    title: string;
    hypothesis: string;
    method: string;
    stop: string;
  }[];
  review: string[];
  ai_tools: { name: string; use: string; boundary: string }[];
  sources: string;
  innovation?: string[];
  schedule_note?: string;
}
export interface Bootstrap {
  network: Network;
  scenarios: Scenario[];
  current_scenario: string;
  orders: Order[];
  tasks: Task[];
  growth: GrowthConfig;
  content: Content;
  health: { status: string; engine_ready: boolean; mode: string };
}
export interface Risk {
  score: number;
  level: string;
  reasons: string[];
  affected_edges: string[];
  delay_hours: number;
  basis: string[];
}
export interface Plan {
  id: string;
  name: string;
  feasible: boolean;
  reason?: string;
  route?: string[];
  departure?: string;
  arrival?: string;
  hours?: number;
  cost?: number;
  extra_cost?: number;
  delay_hours?: number;
  risk?: number;
  on_time?: boolean;
  score?: number;
  distance?: number;
  segments?: { edge: string; exposure: number; extra_hours: number }[];
}
export interface Trace {
  tool: string;
  input: unknown;
  output: unknown;
}
export interface Decision {
  id: string;
  kind: "decision";
  created_at: string;
  order: Order;
  scenario: Scenario;
  risk: Risk;
  plans: Plan[];
  recommendation: { id: string; name: string; reason: string };
  weights: Weights;
  trace: Trace[];
  disclaimer: string;
}
export interface Metrics {
  on_time_rate: number;
  average_delay: number;
  total_cost: number;
  extra_cost: number;
  high_risk: number;
}
export interface Simulation {
  id: string;
  kind: "simulation";
  created_at: string;
  scenario: Scenario;
  before: Metrics;
  after: Metrics;
  rows: {
    order_id: string;
    before_delay: number;
    after_delay: number;
    before_cost: number;
    after_cost: number;
    plan: string;
  }[];
  seed: string;
  method: string;
  disclaimer: string;
}
export interface GrowthReport {
  id: string;
  kind: "growth";
  created_at: string;
  metrics: GrowthResult;
  tasks: Task[];
  plan: Content;
  disclaimer: string;
}
export type Report = Decision | Simulation | GrowthReport;
export interface ExperimentResult {
  a_rate: number;
  b_rate: number;
  difference_pp: number;
  lift: number | null;
  p_value: number;
  ci95_pp: number[];
  adequate: boolean;
  significant: boolean;
  sample_per_arm: number;
  conclusion: string;
  source: string;
}
export interface RiskOverview {
  scenario_id: string;
  active_orders: number;
  weather_affected: number;
  risk_orders: number;
  high_risk: number;
  average_delay: number;
  rows: {
    order_id: string;
    status: string;
    risk: number;
    level: string;
    delay_hours: number;
    affected_edges: string[];
    affected_nodes: string[];
  }[];
  source: string;
}
