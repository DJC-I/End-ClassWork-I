"""Calculations for planning assumptions, never claimed campaign outcomes."""

import math


def calculate(data):
    values = [float(data["exposure"])]
    for key in ("visit_rate", "register_rate", "activate_rate", "retain_rate"):
        values.append(values[-1] * data[key])
    names = ["曝光", "访问", "注册", "激活", "7日留存"]
    budget = sum(c["budget"] for c in data["channels"])
    reach = sum(c["budget"] / c["cpm"] * 1000 for c in data["channels"])
    product = data["visit_rate"] * data["register_rate"] * data["activate_rate"]
    channels = []
    for c in data["channels"]:
        exposure = c["budget"] / c["cpm"] * 1000
        active = exposure * product
        channels.append(
            {
                **c,
                "reach": round(exposure, 2),
                "active": round(active, 2),
                "cac": round(c["budget"] / active, 2) if active else None,
            }
        )
    return {
        "funnel": [{"name": n, "value": round(v, 2)} for n, v in zip(names, values)],
        "budget": round(budget, 2),
        "channel_reach": round(reach, 2),
        "channel_active": round(reach * product, 2),
        "channel_retained": round(reach * product * data["retain_rate"], 2),
        "cac": round(budget / (reach * product), 2) if reach * product else None,
        "channels": channels,
        "source": "全部为计划假设；曝光模型与渠道测算分别展示，覆盖量未去重，非实际获客",
        "assumptions": data,
    }


def experiment(d):
    n1, n2, x1, x2 = (
        d["a_visitors"],
        d["b_visitors"],
        d["a_conversions"],
        d["b_conversions"],
    )
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se0 if se0 else 0
    p_value = math.erfc(abs(z) / math.sqrt(2)) if se0 else 1
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    adequate = min(x1, n1 - x1, x2, n2 - x2) >= 10
    # Approximate two-sided alpha=.05, power=.8 sample size for a 5pp MDE.
    baseline = max(0.01, min(0.99, p1))
    sample = math.ceil(2 * (1.96 + 0.84) ** 2 * baseline * (1 - baseline) / 0.05**2)
    return {
        "a_rate": p1,
        "b_rate": p2,
        "difference_pp": round((p2 - p1) * 100, 3),
        "lift": (p2 / p1 - 1) if p1 else None,
        "p_value": round(p_value, 5),
        "ci95_pp": [
            round((p2 - p1 - 1.96 * se) * 100, 3),
            round((p2 - p1 + 1.96 * se) * 100, 3),
        ],
        "adequate": adequate,
        "significant": adequate and p_value < 0.05,
        "sample_per_arm": sample,
        "conclusion": (
            "样本不足：每组成功与失败数至少10，当前不能可靠判断。"
            if not adequate
            else (
                "在独立随机分组与固定样本假设下有统计差异，需验证业务价值。"
                if p_value < 0.05
                else "当前没有足够证据认为两组存在差异。"
            )
        ),
        "source": "假设输入的双侧两比例z检验；95%正态近似区间；非真实运营结论。样本量按5个百分点MDE、80%功效估算，未做多重检验。",
    }
