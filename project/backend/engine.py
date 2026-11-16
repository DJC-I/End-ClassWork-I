"""Deterministic synthetic directed-graph teaching model, not real dispatch."""

from copy import deepcopy
from datetime import datetime, timedelta
from math import isclose

READY = True
SEED = "skyroute-v1-fixed-stress-085-100-115"
NAMES = {
    "original": "原计划运输",
    "early": "提前发运",
    "detour": "绕行运输",
    "transfer": "调整中转节点",
}


def parse(s):
    return datetime.fromisoformat(s)


def edges_for(route, graph):
    emap = {(e["source"], e["target"]): e for e in graph["edges"]}
    result = []
    for a, b in zip(route, route[1:]):
        e = emap.get((a, b))
        if e is None or not e["available"]:
            raise ValueError(f"不可达连接 {a} → {b}")
        result.append(e)
    return result


def paths(graph, origin, destination, weight):
    """All capacity-constrained simple directed routes for the small corridor."""
    caps = {n["id"]: n["capacity"] for n in graph["nodes"]}
    if (
        origin not in caps
        or destination not in caps
        or weight > min(caps[origin], caps[destination])
    ):
        return []
    result = []

    def visit(node, route):
        if node == destination:
            result.append(route)
            return
        for e in sorted(graph["edges"], key=lambda e: e["id"]):
            if (
                e["source"] == node
                and e["available"]
                and e["target"] not in route
                and weight <= min(e["capacity"], caps[e["target"]])
            ):
                visit(e["target"], route + [e["target"]])

    visit(origin, [origin])
    return result


def severity(weather, multiplier=1):
    parts = {
        "rain": 0.35 * weather["rain"] / 60,
        "snow": 0.35 * weather["snow"] / 20,
        "wind": 0.15 * max(weather["wind"] - 8, 0) / 20,
        "visibility": 0.10 * max(5 - weather["visibility"], 0) / 5,
        "temperature": 0.05 * max(-weather["temperature"], 0) / 10,
    }
    return min(1.5, sum(parts.values()) * multiplier), parts


def overlap_fraction(start, hours, valid_from, valid_to):
    if hours <= 0:
        return 0
    end = start + timedelta(hours=hours)
    overlap = max(
        0, (min(end, valid_to) - max(start, valid_from)).total_seconds() / 3600
    )
    return min(1, overlap / hours)


def evaluate(order, weather, graph, route, depart, strategy="original", multiplier=1):
    edges = edges_for(route, graph)
    nodes = {n["id"]: n for n in graph["nodes"]}
    if (
        not edges
        or route[0] != order["origin"]
        or route[-1] != order["destination"]
        or len(set(route)) != len(route)
    ):
        raise ValueError("无效运输路线")
    if any(
        order["weight"]
        > min(
            e["capacity"],
            nodes[e["source"]]["capacity"],
            nodes[e["target"]]["capacity"],
        )
        for e in edges
    ):
        raise ValueError("运输路径运力不足")
    sev, _ = severity(weather, multiplier)
    start, finish = parse(weather["valid_from"]), parse(weather["valid_to"])
    cursor = depart
    weather_hours, exposure_sum = 0.0, 0.0
    segments = []
    cargo_sensitivity = {"general": 1, "cold": 1.25, "fragile": 1.15}[order["cargo"]]
    for e in edges:
        # Base traversal window avoids a circular implicit forecast equation.
        overlap = overlap_fraction(cursor, e["hours"], start, finish)
        exposure = sev * weather["edge_factors"].get(e["id"], 0) * overlap
        node_overlap = overlap_fraction(
            cursor + timedelta(hours=e["hours"]), 0.25, start, finish
        )
        node_loss = (
            0.25 * sev * weather["node_factors"].get(e["target"], 0) * node_overlap
        )
        extra = e["hours"] * 2.2 * exposure + node_loss
        weather_hours += extra
        exposure_sum += exposure * e["hours"]
        segments.append(
            {
                "edge": e["id"],
                "base_hours": e["hours"],
                "exposure": round(exposure, 5),
                "weather_overlap": round(overlap, 5),
                "extra_hours": round(extra, 5),
            }
        )
        cursor += timedelta(hours=e["hours"] + extra)
    transfer_hours = 0.4 if strategy == "transfer" else 0
    cursor += timedelta(hours=transfer_hours)
    hours = (cursor - depart).total_seconds() / 3600
    delay = max(0, (cursor - parse(order["deadline"])).total_seconds() / 3600)
    distance = sum(e["km"] for e in edges)
    orig_edges = edges_for(order["route"], graph)
    orig_km = sum(e["km"] for e in orig_edges)
    orig_toll = sum(e["toll"] for e in orig_edges)
    running_cost = (order["base_cost"] - orig_toll) / orig_km * distance
    strategy_cost = {
        "original": 0,
        "early": 100 + 12 * order["weight"],
        "detour": 65,
        "transfer": 90 + 8 * order["weight"],
    }[strategy]
    weather_cost = weather_hours * (65 + (25 if order["cargo"] == "cold" else 0))
    total_cost = (
        running_cost + sum(e["toll"] for e in edges) + strategy_cost + weather_cost
    )
    avg_exposure = exposure_sum / sum(e["hours"] for e in edges)
    risk = min(
        100,
        5
        + 65 * avg_exposure * cargo_sensitivity
        + 20 * min(delay / 2, 1)
        + 3 * (order["priority"] - 1),
    )
    return {
        "id": strategy,
        "name": NAMES[strategy],
        "feasible": True,
        "route": route,
        "departure": depart.isoformat(),
        "arrival": cursor.isoformat(),
        "hours": round(hours, 4),
        "cost": round(total_cost, 2),
        "extra_cost": round(total_cost - order["base_cost"], 2),
        "delay_hours": round(delay, 4),
        "risk": round(risk, 2),
        "on_time": delay < 1e-8,
        "distance": distance,
        "segments": segments,
        "weather_extra_hours": round(weather_hours, 5),
        "strategy_cost": round(strategy_cost, 2),
        "weather_cost": round(weather_cost, 2),
        "transfer_hours": transfer_hours,
        "running_cost": round(running_cost, 2),
        "tolls": sum(e["toll"] for e in edges),
    }


def rank(plans, weights):
    feasible = [p for p in plans if p["feasible"]]
    if not feasible:
        raise ValueError("没有可行方案")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("权重之和必须大于0")
    bounds = {
        k: (min(p[f] for p in feasible), max(p[f] for p in feasible))
        for k, f in (("cost", "cost"), ("time", "hours"), ("risk", "risk"))
    }
    for p in feasible:
        score = 0
        for k, field in (("cost", "cost"), ("time", "hours"), ("risk", "risk")):
            lo, hi = bounds[k]
            normalized = 0 if isclose(hi, lo) else (p[field] - lo) / (hi - lo)
            score += normalized * weights[k] / total
        p["score"] = round(score, 6)
    return min(feasible, key=lambda p: (p["score"], p["cost"], p["hours"], p["id"]))


def generate(order, weather, weights, graph):
    routes = paths(graph, order["origin"], order["destination"], order["weight"])
    if order["route"] not in routes:
        raise ValueError("原计划不满足图可达性或运力约束")
    depart = parse(order["departure"])
    original = evaluate(order, weather, graph, order["route"], depart)
    if order["status"] == "待发运":
        early = evaluate(
            order, weather, graph, order["route"], depart - timedelta(hours=2), "early"
        )
        early["assumption"] = "假设货物与司机可提前2小时就绪；未由真实调度确认。"
    else:
        early = {
            "id": "early",
            "name": NAMES["early"],
            "feasible": False,
            "reason": "运输中或已送达，不能回溯提前发运",
        }
    original_edges = {e["id"] for e in edges_for(order["route"], graph)}
    detour_routes = [
        r
        for r in routes
        if r != order["route"]
        and not original_edges.intersection(e["id"] for e in edges_for(r, graph))
    ]
    detours = [
        evaluate(order, weather, graph, r, depart, "detour") for r in detour_routes
    ]
    detour = (
        deepcopy(rank(detours, weights))
        if detours
        else {
            "id": "detour",
            "name": NAMES["detour"],
            "feasible": False,
            "reason": "有向图与载重条件下，没有完全避开原计划区段的可达绕行路线",
        }
    )
    transfer_routes = [
        r
        for r in routes
        if r != order["route"]
        and r != detour.get("route")
        and set(r[1:-1]) - set(order["route"][1:-1])
    ]
    transfers = [
        evaluate(order, weather, graph, r, depart, "transfer") for r in transfer_routes
    ]
    transfer = (
        deepcopy(rank(transfers, weights))
        if transfers
        else {
            "id": "transfer",
            "name": NAMES["transfer"],
            "feasible": False,
            "reason": "无不同于原计划和绕行、且新增中转节点的可达路线，或替代节点运力不足",
        }
    )
    plans = [original, early, detour, transfer]
    best = rank(plans, weights)
    return plans, best, routes


def analyze(order, weather, weights, graph):
    plans, best, routes = generate(order, weather, weights, graph)
    original = plans[0]
    affected = [
        s["edge"]
        for s in original["segments"]
        if s["exposure"] > 0 or s["extra_hours"] > 0
    ]
    reasons = []
    if affected:
        reasons.append(
            f"{weather['warning']}，模拟天气在{len(affected)}个原计划区段有效，增加运输{original['weather_extra_hours']:.2f}小时"
        )
    else:
        reasons.append("原计划通行时段内未命中模拟天气影响区段")
    reasons.append(
        {
            "general": "普通货物敏感系数1.00",
            "cold": "冷链货物敏感系数1.25，天气延时增加温控成本",
            "fragile": "易碎货物敏感系数1.15，需关注低能见度与装卸稳定性",
        }[order["cargo"]]
    )
    reasons.append(
        f"P{order['priority']}优先级；预计{'延误'+str(round(original['delay_hours'],2))+'小时' if not original['on_time'] else '在承诺时限内到货'}"
    )
    if order["status"] == "运输中":
        reasons.append(
            "运输中缺少实时位置，其他方案只做原始计划级反事实比较，不可直接执行；提前发运不适用"
        )
    if weather["id"] != "normal":
        reasons.append("气象预警不等于封路；连接按独立available字段校验")
    sev, parts = severity(weather)
    score = original["risk"]
    basis = [
        "S=min(1.5,.35×雨/60+.35×雪/20+.15×max(风-8,0)/20+.10×max(5-能见度,0)/5+.05×max(-温度,0)/10)。系数为教学假设。",
        "每段额外h=基准h×2.2×S×区段系数×基准通行窗天气重叠比例 + .25h×S×目的节点系数×节点窗重叠比例。逐段累积到货时间。",
        "风险=min(100,5+65×时长加权天气暴露×货物敏感度+20×min(延误h/2,1)+3×(优先级-1))，不是事故概率。",
        "成本=(原成本-原通行费)/原里程×新里程+新通行费+策略费用+天气额外h×(65元/h+冷链25元/h)。提前100+12元/吨；绕行65元；中转90+8元/吨且加.4h。",
        "成本/时长/风险分别min-max归一化，按权重归一化求加权和，越低越优。先从每类策略内部选最优路线，再比较四类候选。",
        "提前假设货物与司机提前2h就绪；运输中方案为计划级反事实，需要实时位置和人工调度确认。",
    ]
    recommendation = {
        "id": best["id"],
        "name": best["name"],
        "reason": f"在当前可行方案和权重下综合分{best['score']:.3f}最低；估算时长{best['hours']:.2f}h、成本{best['cost']:.2f}元、风险{best['risk']:.1f}/100、延误{best['delay_hours']:.2f}h。权重反映偏好，不保证全部指标同时改善。",
    }
    if best["id"] == "early":
        recommendation["reason"] += "需人工确认货物、司机及装卸时窗可提前。"
    trace = [
        {
            "tool": "读取运输任务",
            "input": {"order_id": order["id"]},
            "output": deepcopy(order),
        },
        {
            "tool": "读取天气与网络",
            "input": {"scenario_id": weather["id"], "version": graph["version"]},
            "output": {
                "weather": deepcopy(weather),
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
            },
        },
        {
            "tool": "识别区段风险",
            "input": {
                "severity_parts": parts,
                "severity": round(sev, 5),
                "cargo": order["cargo"],
                "deadline": order["deadline"],
            },
            "output": {"risk": score, "segments": original["segments"]},
        },
        {
            "tool": "枚举可达路线",
            "input": {
                "origin": order["origin"],
                "destination": order["destination"],
                "weight": order["weight"],
            },
            "output": {"routes": routes, "count": len(routes)},
        },
        {
            "tool": "生成并评分方案",
            "input": {"weights": deepcopy(weights), "strategies": list(NAMES)},
            "output": deepcopy(plans),
        },
        {
            "tool": "输出决策建议",
            "input": {"scoring": "归一化成本/时长/风险加权"},
            "output": recommendation,
        },
    ]
    return {
        "order": deepcopy(order),
        "scenario": deepcopy(weather),
        "weights": deepcopy(weights),
        "risk": {
            "score": score,
            "level": "高风险" if score >= 50 else "中风险" if score >= 25 else "低风险",
            "reasons": reasons,
            "affected_edges": affected,
            "delay_hours": original["delay_hours"],
            "basis": basis,
        },
        "plans": plans,
        "recommendation": recommendation,
        "trace": trace,
    }


def simulate(orders, weather, weights, graph):
    if not orders:
        raise ValueError("没有可仿真订单")
    before_samples, after_samples, rows, nominal_before, nominal_after = (
        [],
        [],
        [],
        [],
        [],
    )
    for o in orders:
        plans, best, _ = generate(o, weather, weights, graph)
        nominal_before.append(plans[0])
        nominal_after.append(best)
        for multiplier in (0.85, 1, 1.15):
            # Fixed nominal decision prevents hindsight re-optimization in replay.
            before_samples.append(
                evaluate(
                    o,
                    weather,
                    graph,
                    o["route"],
                    parse(o["departure"]),
                    "original",
                    multiplier,
                )
            )
            after_samples.append(
                evaluate(
                    o,
                    weather,
                    graph,
                    best["route"],
                    parse(best["departure"]),
                    best["id"],
                    multiplier,
                )
            )
        rows.append(
            {
                "order_id": o["id"],
                "before_delay": plans[0]["delay_hours"],
                "after_delay": best["delay_hours"],
                "before_cost": plans[0]["cost"],
                "after_cost": best["cost"],
                "plan": best["name"],
            }
        )

    def metrics(samples, nominal):
        return {
            "on_time_rate": round(
                100 * sum(p["on_time"] for p in samples) / len(samples), 2
            ),
            "average_delay": round(
                sum(p["delay_hours"] for p in samples) / len(samples), 4
            ),
            "total_cost": round(sum(p["cost"] for p in samples) / 3, 2),
            "extra_cost": round(sum(p["extra_cost"] for p in samples) / 3, 2),
            "high_risk": sum(p["risk"] >= 50 for p in nominal),
        }

    return {
        "scenario": deepcopy(weather),
        "weights": deepcopy(weights),
        "before": metrics(before_samples, nominal_before),
        "after": metrics(after_samples, nominal_after),
        "rows": rows,
        "seed": SEED,
        "order_count": len(orders),
        "sample_count": len(before_samples),
        "method": "固定输入，0.85/1/1.15严重度配对回放；推荐在名义天气下先选定，扰动时不重选，避免事后最优。准时率为订单×3压力情景的准时占比，成本为三情景总成本均值，高风险为名义场景风险≥50的订单数。非历史实测。",
        "inputs": {
            "orders": deepcopy(orders),
            "graph_version": graph["version"],
            "multipliers": [0.85, 1, 1.15],
        },
        "samples": {"before": before_samples, "after": after_samples},
    }
