# SkyRoute decision 报告

报告编号：ee3eaec2-ec0a-40ec-a201-fae4305d1838

生成时间：2026-11-16T07:41:33.010801+00:00

数据版本：skyroute-synthetic-v1

教学模拟，不能用于真实调度或作为实际运营成效。预警不等于封路。

## 订单 SR-001

天气：暴雨风险

风险原因：模拟暴雨橙色预警，模拟天气在3个原计划区段有效，增加运输1.97小时；冷链货物敏感系数1.25，天气延时增加温控成本；P3优先级；预计延误0.98小时；气象预警不等于封路；连接按独立available字段校验

## 方案对比

|方案|可用|时长h|成本元|延误h|风险分|

|---|---|---|---|---|---|

|原计划运输|True|4.5667|1357.01|0.9834|47.15|

|提前发运|True|3.0253|1414.28|0|16.42|

|绕行运输|True|2.95|1242.0|0|11.0|

|调整中转节点|True|4.1232|1413.09|0.5399|25.96|

推荐：绕行运输。在当前可行方案和权重下综合分0.000最低；估算时长2.95h、成本1242.00元、风险11.0/100、延误0.00h。权重反映偏好，不保证全部指标同时改善。

## 完整计算与输入快照

```json

{
  "id": "ee3eaec2-ec0a-40ec-a201-fae4305d1838",
  "kind": "decision",
  "created_at": "2026-11-16T07:41:33.010801+00:00",
  "data_version": "skyroute-synthetic-v1",
  "disclaimer": "教学模拟，不能用于真实调度或作为实际运营成效。预警不等于封路。",
  "order": {
    "id": "SR-001",
    "origin": "BJ",
    "destination": "TJ",
    "cargo": "cold",
    "weight": 8,
    "departure": "2026-11-16T10:00:00+08:00",
    "deadline": "2026-11-16T13:35:00+08:00",
    "priority": 3,
    "route": [
      "BJ",
      "TZ",
      "WQ",
      "TJ"
    ],
    "base_cost": 1180,
    "base_hours": 2.6,
    "status": "待发运"
  },
  "scenario": {
    "id": "rain",
    "name": "暴雨风险",
    "tag": "主走廊降雨增强",
    "description": "通州—武清区段降速风险，预警不代表封路。",
    "valid_from": "2026-11-16T10:00:00+08:00",
    "valid_to": "2026-11-16T18:00:00+08:00",
    "rain": 55,
    "snow": 0,
    "wind": 12,
    "visibility": 1.8,
    "temperature": 8,
    "warning": "模拟暴雨橙色预警",
    "edge_factors": {
      "BJ-TZ": 0.5,
      "TZ-WQ": 1,
      "WQ-TJ": 0.65,
      "WQ-BD": 0.6,
      "LF-WQ": 0.35
    },
    "node_factors": {
      "WQ": 0.7,
      "TZ": 0.4
    },
    "source": "教学模拟 v1；降雨量单位mm/3h"
  },
  "weights": {
    "cost": 0.25,
    "time": 0.35,
    "risk": 0.4
  },
  "risk": {
    "score": 47.15,
    "level": "中风险",
    "reasons": [
      "模拟暴雨橙色预警，模拟天气在3个原计划区段有效，增加运输1.97小时",
      "冷链货物敏感系数1.25，天气延时增加温控成本",
      "P3优先级；预计延误0.98小时",
      "气象预警不等于封路；连接按独立available字段校验"
    ],
    "affected_edges": [
      "BJ-TZ",
      "TZ-WQ",
      "WQ-TJ"
    ],
    "delay_hours": 0.9834,
    "basis": [
      "S=min(1.5,.35×雨/60+.35×雪/20+.15×max(风-8,0)/20+.10×max(5-能见度,0)/5+.05×max(-温度,0)/10)。系数为教学假设。",
      "每段额外h=基准h×2.2×S×区段系数×基准通行窗天气重叠比例 + .25h×S×目的节点系数×节点窗重叠比例。逐段累积到货时间。",
      "风险=min(100,5+65×时长加权天气暴露×货物敏感度+20×min(延误h/2,1)+3×(优先级-1))，不是事故概率。",
      "成本=(原成本-原通行费)/原里程×新里程+新通行费+策略费用+天气额外h×(65元/h+冷链25元/h)。提前100+12元/吨；绕行65元；中转90+8元/吨且加.4h。",
      "成本/时长/风险分别min-max归一化，按权重归一化求加权和，越低越优。先从每类策略内部选最优路线，再比较四类候选。",
      "提前假设货物与司机提前2h就绪；运输中方案为计划级反事实，需要实时位置和人工调度确认。"
    ]
  },
  "plans": [
    {
      "id": "original",
      "name": "原计划运输",
      "feasible": true,
      "route": [
        "BJ",
        "TZ",
        "WQ",
        "TJ"
      ],
      "departure": "2026-11-16T10:00:00+08:00",
      "arrival": "2026-11-16T14:34:00.209400+08:00",
      "hours": 4.5667,
      "cost": 1357.01,
      "extra_cost": 177.01,
      "delay_hours": 0.9834,
      "risk": 47.15,
      "on_time": false,
      "distance": 160,
      "segments": [
        {
          "edge": "BJ-TZ",
          "base_hours": 0.65,
          "exposure": 0.20742,
          "weather_overlap": 1,
          "extra_hours": 0.33809
        },
        {
          "edge": "TZ-WQ",
          "base_hours": 1.25,
          "exposure": 0.41483,
          "weather_overlap": 1,
          "extra_hours": 1.21339
        },
        {
          "edge": "WQ-TJ",
          "base_hours": 0.7,
          "exposure": 0.26964,
          "weather_overlap": 1,
          "extra_hours": 0.41525
        }
      ],
      "weather_extra_hours": 1.96672,
      "strategy_cost": 0,
      "weather_cost": 177.01,
      "transfer_hours": 0,
      "running_cost": 1082.0,
      "tolls": 98,
      "score": 0.916894
    },
    {
      "id": "early",
      "name": "提前发运",
      "feasible": true,
      "route": [
        "BJ",
        "TZ",
        "WQ",
        "TJ"
      ],
      "departure": "2026-11-16T08:00:00+08:00",
      "arrival": "2026-11-16T11:01:31.163942+08:00",
      "hours": 3.0253,
      "cost": 1414.28,
      "extra_cost": 234.28,
      "delay_hours": 0,
      "risk": 16.42,
      "on_time": true,
      "distance": 160,
      "segments": [
        {
          "edge": "BJ-TZ",
          "base_hours": 0.65,
          "exposure": 0.0,
          "weather_overlap": 0.0,
          "extra_hours": 0.0
        },
        {
          "edge": "TZ-WQ",
          "base_hours": 1.25,
          "exposure": 0.0,
          "weather_overlap": 0.0,
          "extra_hours": 0.04356
        },
        {
          "edge": "WQ-TJ",
          "base_hours": 0.7,
          "exposure": 0.2479,
          "weather_overlap": 0.91937,
          "extra_hours": 0.38177
        }
      ],
      "weather_extra_hours": 0.42532,
      "strategy_cost": 196,
      "weather_cost": 38.28,
      "transfer_hours": 0,
      "running_cost": 1082.0,
      "tolls": 98,
      "assumption": "假设货物与司机可提前2小时就绪；未由真实调度确认。",
      "score": 0.326274
    },
    {
      "id": "detour",
      "name": "绕行运输",
      "feasible": true,
      "route": [
        "BJ",
        "LF",
        "TJ"
      ],
      "departure": "2026-11-16T10:00:00+08:00",
      "arrival": "2026-11-16T12:57:00+08:00",
      "hours": 2.95,
      "cost": 1242.0,
      "extra_cost": 62.0,
      "delay_hours": 0,
      "risk": 11.0,
      "on_time": true,
      "distance": 160,
      "segments": [
        {
          "edge": "BJ-LF",
          "base_hours": 1.15,
          "exposure": 0.0,
          "weather_overlap": 1,
          "extra_hours": 0.0
        },
        {
          "edge": "LF-TJ",
          "base_hours": 1.8,
          "exposure": 0.0,
          "weather_overlap": 1,
          "extra_hours": 0.0
        }
      ],
      "weather_extra_hours": 0.0,
      "strategy_cost": 65,
      "weather_cost": 0.0,
      "transfer_hours": 0,
      "running_cost": 1082.0,
      "tolls": 95,
      "score": 0.0
    },
    {
      "id": "transfer",
      "name": "调整中转节点",
      "feasible": true,
      "route": [
        "BJ",
        "LF",
        "WQ",
        "TJ"
      ],
      "departure": "2026-11-16T10:00:00+08:00",
      "arrival": "2026-11-16T14:07:23.652300+08:00",
      "hours": 4.1232,
      "cost": 1413.09,
      "extra_cost": 233.09,
      "delay_hours": 0.5399,
      "risk": 25.96,
      "on_time": false,
      "distance": 160,
      "segments": [
        {
          "edge": "BJ-LF",
          "base_hours": 1.15,
          "exposure": 0.0,
          "weather_overlap": 1,
          "extra_hours": 0.0
        },
        {
          "edge": "LF-WQ",
          "base_hours": 1.05,
          "exposure": 0.14519,
          "weather_overlap": 1,
          "extra_hours": 0.40799
        },
        {
          "edge": "WQ-TJ",
          "base_hours": 0.7,
          "exposure": 0.26964,
          "weather_overlap": 1,
          "extra_hours": 0.41525
        }
      ],
      "weather_extra_hours": 0.82324,
      "strategy_cost": 154,
      "weather_cost": 74.09,
      "transfer_hours": 0.4,
      "running_cost": 1082.0,
      "tolls": 103,
      "score": 0.667792
    }
  ],
  "recommendation": {
    "id": "detour",
    "name": "绕行运输",
    "reason": "在当前可行方案和权重下综合分0.000最低；估算时长2.95h、成本1242.00元、风险11.0/100、延误0.00h。权重反映偏好，不保证全部指标同时改善。"
  },
  "trace": [
    {
      "tool": "读取运输任务",
      "input": {
        "order_id": "SR-001"
      },
      "output": {
        "id": "SR-001",
        "origin": "BJ",
        "destination": "TJ",
        "cargo": "cold",
        "weight": 8,
        "departure": "2026-11-16T10:00:00+08:00",
        "deadline": "2026-11-16T13:35:00+08:00",
        "priority": 3,
        "route": [
          "BJ",
          "TZ",
          "WQ",
          "TJ"
        ],
        "base_cost": 1180,
        "base_hours": 2.6,
        "status": "待发运"
      }
    },
    {
      "tool": "读取天气与网络",
      "input": {
        "scenario_id": "rain",
        "version": "skyroute-synthetic-v1"
      },
      "output": {
        "weather": {
          "id": "rain",
          "name": "暴雨风险",
          "tag": "主走廊降雨增强",
          "description": "通州—武清区段降速风险，预警不代表封路。",
          "valid_from": "2026-11-16T10:00:00+08:00",
          "valid_to": "2026-11-16T18:00:00+08:00",
          "rain": 55,
          "snow": 0,
          "wind": 12,
          "visibility": 1.8,
          "temperature": 8,
          "warning": "模拟暴雨橙色预警",
          "edge_factors": {
            "BJ-TZ": 0.5,
            "TZ-WQ": 1,
            "WQ-TJ": 0.65,
            "WQ-BD": 0.6,
            "LF-WQ": 0.35
          },
          "node_factors": {
            "WQ": 0.7,
            "TZ": 0.4
          },
          "source": "教学模拟 v1；降雨量单位mm/3h"
        },
        "node_count": 7,
        "edge_count": 10
      }
    },
    {
      "tool": "识别区段风险",
      "input": {
        "severity_parts": {
          "rain": 0.32083333333333336,
          "snow": 0.0,
          "wind": 0.03,
          "visibility": 0.06400000000000002,
          "temperature": 0.0
        },
        "severity": 0.41483,
        "cargo": "cold",
        "deadline": "2026-11-16T13:35:00+08:00"
      },
      "output": {
        "risk": 47.15,
        "segments": [
          {
            "edge": "BJ-TZ",
            "base_hours": 0.65,
            "exposure": 0.20742,
            "weather_overlap": 1,
            "extra_hours": 0.33809
          },
          {
            "edge": "TZ-WQ",
            "base_hours": 1.25,
            "exposure": 0.41483,
            "weather_overlap": 1,
            "extra_hours": 1.21339
          },
          {
            "edge": "WQ-TJ",
            "base_hours": 0.7,
            "exposure": 0.26964,
            "weather_overlap": 1,
            "extra_hours": 0.41525
          }
        ]
      }
    },
    {
      "tool": "枚举可达路线",
      "input": {
        "origin": "BJ",
        "destination": "TJ",
        "weight": 8
      },
      "output": {
        "routes": [
          [
            "BJ",
            "LF",
            "TJ"
          ],
          [
            "BJ",
            "LF",
            "WQ",
            "BD",
            "TJ"
          ],
          [
            "BJ",
            "LF",
            "WQ",
            "TJ"
          ],
          [
            "BJ",
            "TZ",
            "JZ",
            "BD",
            "TJ"
          ],
          [
            "BJ",
            "TZ",
            "WQ",
            "BD",
            "TJ"
          ],
          [
            "BJ",
            "TZ",
            "WQ",
            "TJ"
          ]
        ],
        "count": 6
      }
    },
    {
      "tool": "生成并评分方案",
      "input": {
        "weights": {
          "cost": 0.25,
          "time": 0.35,
          "risk": 0.4
        },
        "strategies": [
          "original",
          "early",
          "detour",
          "transfer"
        ]
      },
      "output": [
        {
          "id": "original",
          "name": "原计划运输",
          "feasible": true,
          "route": [
            "BJ",
            "TZ",
            "WQ",
            "TJ"
          ],
          "departure": "2026-11-16T10:00:00+08:00",
          "arrival": "2026-11-16T14:34:00.209400+08:00",
          "hours": 4.5667,
          "cost": 1357.01,
          "extra_cost": 177.01,
          "delay_hours": 0.9834,
          "risk": 47.15,
          "on_time": false,
          "distance": 160,
          "segments": [
            {
              "edge": "BJ-TZ",
              "base_hours": 0.65,
              "exposure": 0.20742,
              "weather_overlap": 1,
              "extra_hours": 0.33809
            },
            {
              "edge": "TZ-WQ",
              "base_hours": 1.25,
              "exposure": 0.41483,
              "weather_overlap": 1,
              "extra_hours": 1.21339
            },
            {
              "edge": "WQ-TJ",
              "base_hours": 0.7,
              "exposure": 0.26964,
              "weather_overlap": 1,
              "extra_hours": 0.41525
            }
          ],
          "weather_extra_hours": 1.96672,
          "strategy_cost": 0,
          "weather_cost": 177.01,
          "transfer_hours": 0,
          "running_cost": 1082.0,
          "tolls": 98,
          "score": 0.916894
        },
        {
          "id": "early",
          "name": "提前发运",
          "feasible": true,
          "route": [
            "BJ",
            "TZ",
            "WQ",
            "TJ"
          ],
          "departure": "2026-11-16T08:00:00+08:00",
          "arrival": "2026-11-16T11:01:31.163942+08:00",
          "hours": 3.0253,
          "cost": 1414.28,
          "extra_cost": 234.28,
          "delay_hours": 0,
          "risk": 16.42,
          "on_time": true,
          "distance": 160,
          "segments": [
            {
              "edge": "BJ-TZ",
              "base_hours": 0.65,
              "exposure": 0.0,
              "weather_overlap": 0.0,
              "extra_hours": 0.0
            },
            {
              "edge": "TZ-WQ",
              "base_hours": 1.25,
              "exposure": 0.0,
              "weather_overlap": 0.0,
              "extra_hours": 0.04356
            },
            {
              "edge": "WQ-TJ",
              "base_hours": 0.7,
              "exposure": 0.2479,
              "weather_overlap": 0.91937,
              "extra_hours": 0.38177
            }
          ],
          "weather_extra_hours": 0.42532,
          "strategy_cost": 196,
          "weather_cost": 38.28,
          "transfer_hours": 0,
          "running_cost": 1082.0,
          "tolls": 98,
          "assumption": "假设货物与司机可提前2小时就绪；未由真实调度确认。",
          "score": 0.326274
        },
        {
          "id": "detour",
          "name": "绕行运输",
          "feasible": true,
          "route": [
            "BJ",
            "LF",
            "TJ"
          ],
          "departure": "2026-11-16T10:00:00+08:00",
          "arrival": "2026-11-16T12:57:00+08:00",
          "hours": 2.95,
          "cost": 1242.0,
          "extra_cost": 62.0,
          "delay_hours": 0,
          "risk": 11.0,
          "on_time": true,
          "distance": 160,
          "segments": [
            {
              "edge": "BJ-LF",
              "base_hours": 1.15,
              "exposure": 0.0,
              "weather_overlap": 1,
              "extra_hours": 0.0
            },
            {
              "edge": "LF-TJ",
              "base_hours": 1.8,
              "exposure": 0.0,
              "weather_overlap": 1,
              "extra_hours": 0.0
            }
          ],
          "weather_extra_hours": 0.0,
          "strategy_cost": 65,
          "weather_cost": 0.0,
          "transfer_hours": 0,
          "running_cost": 1082.0,
          "tolls": 95,
          "score": 0.0
        },
        {
          "id": "transfer",
          "name": "调整中转节点",
          "feasible": true,
          "route": [
            "BJ",
            "LF",
            "WQ",
            "TJ"
          ],
          "departure": "2026-11-16T10:00:00+08:00",
          "arrival": "2026-11-16T14:07:23.652300+08:00",
          "hours": 4.1232,
          "cost": 1413.09,
          "extra_cost": 233.09,
          "delay_hours": 0.5399,
          "risk": 25.96,
          "on_time": false,
          "distance": 160,
          "segments": [
            {
              "edge": "BJ-LF",
              "base_hours": 1.15,
              "exposure": 0.0,
              "weather_overlap": 1,
              "extra_hours": 0.0
            },
            {
              "edge": "LF-WQ",
              "base_hours": 1.05,
              "exposure": 0.14519,
              "weather_overlap": 1,
              "extra_hours": 0.40799
            },
            {
              "edge": "WQ-TJ",
              "base_hours": 0.7,
              "exposure": 0.26964,
              "weather_overlap": 1,
              "extra_hours": 0.41525
            }
          ],
          "weather_extra_hours": 0.82324,
          "strategy_cost": 154,
          "weather_cost": 74.09,
          "transfer_hours": 0.4,
          "running_cost": 1082.0,
          "tolls": 103,
          "score": 0.667792
        }
      ]
    },
    {
      "tool": "输出决策建议",
      "input": {
        "scoring": "归一化成本/时长/风险加权"
      },
      "output": {
        "id": "detour",
        "name": "绕行运输",
        "reason": "在当前可行方案和权重下综合分0.000最低；估算时长2.95h、成本1242.00元、风险11.0/100、延误0.00h。权重反映偏好，不保证全部指标同时改善。"
      }
    }
  ]
}

```