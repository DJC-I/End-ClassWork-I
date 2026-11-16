from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .seed import NODES, EDGES


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Order(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    origin: str
    destination: str
    cargo: Literal["general", "cold", "fragile"]
    weight: float = Field(gt=0, le=30)
    departure: datetime
    deadline: datetime
    priority: int = Field(ge=1, le=3)
    route: list[str] = Field(min_length=2, max_length=12)
    base_cost: float = Field(gt=0, le=1000000)
    base_hours: float = Field(gt=0, le=240)
    status: Literal["待发运", "运输中", "已送达"] = "待发运"

    @model_validator(mode="after")
    def validate_business(self):
        if not self.departure.tzinfo or not self.deadline.tzinfo:
            raise ValueError("发运与交付时间必须带时区")
        if self.deadline <= self.departure:
            raise ValueError("承诺送达时间必须晚于发运时间")
        node_map = {n["id"]: n for n in NODES}
        if self.origin not in node_map or self.destination not in node_map:
            raise ValueError("未知运输节点")
        if (
            self.origin == self.destination
            or self.route[0] != self.origin
            or self.route[-1] != self.destination
        ):
            raise ValueError("路线端点必须与订单起终点一致且不同")
        if len(set(self.route)) != len(self.route):
            raise ValueError("计划路线不允许重复节点")
        emap = {(e["source"], e["target"]): e for e in EDGES}
        edges = []
        for a, b in zip(self.route, self.route[1:]):
            if (a, b) not in emap or not emap[(a, b)]["available"]:
                raise ValueError(f"无可用连接：{a} → {b}")
            edge = emap[(a, b)]
            if self.weight > min(
                edge["capacity"], node_map[a]["capacity"], node_map[b]["capacity"]
            ):
                raise ValueError(f"{edge['id']} 运力不足")
            edges.append(edge)
        if abs(self.base_hours - sum(e["hours"] for e in edges)) > 0.011:
            raise ValueError("原计划时长必须等于图中路线基准时长之和")
        if self.base_cost < sum(e["toll"] for e in edges):
            raise ValueError("原计划成本不得低于模拟通行费用之和")
        return self


class Task(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    title: str = Field(min_length=1, max_length=200)
    owner: str = Field(min_length=1, max_length=80)
    start: date
    end: date
    status: Literal["待开始", "进行中", "已完成"]
    resources: str = Field(max_length=500)
    outcome: str = Field(max_length=500)
    metric: str = Field(max_length=500)

    @model_validator(mode="after")
    def dates(self):
        if self.end < self.start:
            raise ValueError("任务结束日期不得早于开始日期")
        return self


class Channel(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    budget: float = Field(ge=0, le=1000000)
    cpm: float = Field(gt=0, le=1000000)


class Growth(StrictModel):
    exposure: int = Field(ge=0, le=100000000)
    visit_rate: float = Field(ge=0, le=1)
    register_rate: float = Field(ge=0, le=1)
    activate_rate: float = Field(ge=0, le=1)
    retain_rate: float = Field(ge=0, le=1)
    channels: list[Channel] = Field(min_length=1, max_length=20)


class Experiment(StrictModel):
    a_visitors: int = Field(gt=0, le=10000000)
    a_conversions: int = Field(ge=0)
    b_visitors: int = Field(gt=0, le=10000000)
    b_conversions: int = Field(ge=0)

    @model_validator(mode="after")
    def counts(self):
        if self.a_conversions > self.a_visitors or self.b_conversions > self.b_visitors:
            raise ValueError("转化人数不能超过参与人数")
        return self


class Weights(StrictModel):
    cost: float = Field(default=0.25, ge=0, le=1)
    time: float = Field(default=0.35, ge=0, le=1)
    risk: float = Field(default=0.4, ge=0, le=1)

    @model_validator(mode="after")
    def nonzero(self):
        if self.cost + self.time + self.risk <= 0:
            raise ValueError("至少一项决策权重必须大于0")
        return self


class AnalysisRequest(StrictModel):
    order_id: str
    scenario_id: Literal["normal", "rain", "snow"]
    weights: Weights = Field(default_factory=Weights)


class SimulationRequest(StrictModel):
    scenario_id: Literal["normal", "rain", "snow"]
    weights: Weights = Field(default_factory=Weights)


class ScenarioRequest(StrictModel):
    scenario_id: Literal["normal", "rain", "snow"]


class ExplainRequest(StrictModel):
    report_id: str
    question: str = Field(
        default="请解释推荐依据、适用限制与需要人工核实的事项。",
        min_length=1,
        max_length=1000,
    )
