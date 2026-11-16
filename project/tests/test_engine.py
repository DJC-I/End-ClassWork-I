from copy import deepcopy
from datetime import timedelta
import pytest
from backend import engine, seed

W = {"cost": 0.25, "time": 0.35, "risk": 0.4}


def test_directed_reachability_and_capacity():
    g = seed.network()
    routes = engine.paths(g, "BJ", "TJ", 8)
    assert ["BJ", "TZ", "WQ", "TJ"] in routes
    assert ["BJ", "LF", "TJ"] in routes
    assert engine.paths(g, "TJ", "BJ", 8) == []
    assert all("JZ" not in r for r in engine.paths(g, "BJ", "TJ", 18))
    assert engine.paths(g, "BJ", "TJ", 29) == []
    g["edges"][0]["available"] = False
    assert all(not (r[:2] == ["BJ", "TZ"]) for r in engine.paths(g, "BJ", "TJ", 8))


def test_baseline_hand_calculation():
    o = seed.ORDERS[0]
    p = engine.evaluate(
        o, seed.SCENARIOS[0], seed.network(), o["route"], engine.parse(o["departure"])
    )
    assert p["hours"] == pytest.approx(0.65 + 1.25 + 0.7)
    assert p["distance"] == 160
    assert p["tolls"] == 98
    assert p["running_cost"] == 1082
    assert p["cost"] == 1180
    assert p["extra_cost"] == 0
    assert p["risk"] == 11  # base 5 + two priority steps * 3
    assert p["delay_hours"] == 0 and p["on_time"]


def test_rain_hand_calculation():
    o = seed.ORDERS[0]
    s = seed.SCENARIOS[1]
    # Rain=.320833, wind=.03, visibility=.064; all three edges inside window.
    severity = 0.35 * 55 / 60 + 0.15 * 4 / 20 + 0.10 * 3.2 / 5
    expected_extra = 2.2 * severity * (
        0.65 * 0.5 + 1.25 * 1 + 0.7 * 0.65
    ) + 0.25 * severity * (0.4 + 0.7)
    p = engine.evaluate(o, s, seed.network(), o["route"], engine.parse(o["departure"]))
    assert p["hours"] == pytest.approx(2.6 + expected_extra, abs=0.0001)
    assert p["cost"] == pytest.approx(1180 + expected_extra * 90, abs=0.01)
    assert p["delay_hours"] == pytest.approx(
        2.6 + expected_extra - 3.583333333, abs=0.0001
    )
    assert p["risk"] > 40


def test_effective_window_and_early_departure():
    o = seed.ORDERS[0]
    s = seed.SCENARIOS[1]
    p = engine.evaluate(
        o,
        s,
        seed.network(),
        o["route"],
        engine.parse(o["departure"]) + timedelta(days=1),
    )
    assert p["weather_extra_hours"] == 0
    assert all(x["exposure"] == 0 for x in p["segments"])
    early = engine.evaluate(
        o,
        s,
        seed.network(),
        o["route"],
        engine.parse(o["departure"]) - timedelta(hours=2),
        "early",
    )
    normal = engine.evaluate(
        o, s, seed.network(), o["route"], engine.parse(o["departure"])
    )
    assert early["hours"] < normal["hours"]
    assert early["strategy_cost"] == 196


def test_real_alternatives_and_inapplicable():
    d = engine.analyze(seed.ORDERS[0], seed.SCENARIOS[1], W, seed.network())
    feasible = [p for p in d["plans"] if p["feasible"] and p["id"] != "early"]
    assert len({tuple(p["route"]) for p in feasible}) == len(feasible)
    assert len(d["plans"]) == 4 and len(d["trace"]) == 6
    assert all(p["score"] >= 0 for p in d["plans"] if p["feasible"])
    o = deepcopy(seed.ORDERS[4])
    d = engine.analyze(o, seed.SCENARIOS[1], W, seed.network())
    assert not d["plans"][1]["feasible"]
    assert "回溯" in d["plans"][1]["reason"]


def test_weighted_score_and_no_zero_weight():
    o = seed.ORDERS[0]
    c = engine.analyze(
        o, seed.SCENARIOS[1], {"cost": 1, "time": 0, "risk": 0}, seed.network()
    )
    feasible = [p for p in c["plans"] if p["feasible"]]
    best = next(p for p in feasible if p["id"] == c["recommendation"]["id"])
    assert best["cost"] == min(p["cost"] for p in feasible)
    r = engine.analyze(
        o, seed.SCENARIOS[1], {"cost": 0, "time": 0, "risk": 1}, seed.network()
    )
    best = next(p for p in r["plans"] if p["id"] == r["recommendation"]["id"])
    assert best["risk"] == min(p["risk"] for p in r["plans"] if p["feasible"])
    with pytest.raises(ValueError):
        engine.analyze(
            o, seed.SCENARIOS[0], {"cost": 0, "time": 0, "risk": 0}, seed.network()
        )


def test_weather_does_not_close_edges_and_bad_route_rejected():
    g = seed.network()
    old = deepcopy(g)
    engine.analyze(seed.ORDERS[0], seed.SCENARIOS[2], W, g)
    assert old == g
    with pytest.raises(ValueError):
        engine.evaluate(
            seed.ORDERS[0],
            seed.SCENARIOS[0],
            g,
            ["BJ", "TJ"],
            engine.parse(seed.ORDERS[0]["departure"]),
        )
    g["edges"][0]["capacity"] = 1
    with pytest.raises(ValueError):
        engine.analyze(seed.ORDERS[0], seed.SCENARIOS[1], W, g)


@pytest.mark.parametrize("sid", [0, 1, 2])
def test_reproducible_simulation_and_aggregate(sid):
    a = engine.simulate(seed.ORDERS, seed.SCENARIOS[sid], W, seed.network())
    b = engine.simulate(seed.ORDERS, seed.SCENARIOS[sid], W, seed.network())
    assert a == b
    assert a["sample_count"] == 18
    for side in ("before", "after"):
        samples = a["samples"][side]
        assert a[side]["total_cost"] == round(sum(p["cost"] for p in samples) / 3, 2)
        assert a[side]["on_time_rate"] == round(
            100 * sum(p["on_time"] for p in samples) / 18, 2
        )
    # Each order uses the same selected strategy for all three perturbations.
    for i in range(0, 18, 3):
        assert len({p["id"] for p in a["samples"]["after"][i : i + 3]}) == 1


def test_scenario_impacts_change():
    normal = engine.simulate(seed.ORDERS, seed.SCENARIOS[0], W, seed.network())
    rain = engine.simulate(seed.ORDERS, seed.SCENARIOS[1], W, seed.network())
    snow = engine.simulate(seed.ORDERS, seed.SCENARIOS[2], W, seed.network())
    assert normal["before"]["on_time_rate"] == 100
    assert rain["before"]["average_delay"] > normal["before"]["average_delay"]
    assert snow["before"]["high_risk"] > normal["before"]["high_risk"]
    assert rain["after"]["average_delay"] < rain["before"]["average_delay"]


def test_analysis_simulation_report_and_rule_explanation(client):
    r = client.post(
        "/api/analysis",
        json={"order_id": "SR-001", "scenario_id": "rain", "weights": W},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert len(d["plans"]) == 4 and d["trace"][3]["output"]["count"] > 1
    assert client.get("/api/reports/" + d["id"]).json() == d
    assert "方案对比" in client.get("/api/reports/" + d["id"] + "/download").text
    explanation = client.post("/api/agent/explain", json={"report_id": d["id"]}).json()
    assert explanation["mode"] == "规则模式"
    s = client.post("/api/simulation", json={"scenario_id": "snow", "weights": W})
    assert s.status_code == 200 and s.json()["sample_count"] == 18
    assert (
        client.post(
            "/api/analysis",
            json={
                "order_id": "SR-001",
                "scenario_id": "rain",
                "weights": {"cost": 0, "time": 0, "risk": 0},
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/analysis", json={"order_id": "MISSING", "scenario_id": "rain"}
        ).status_code
        == 404
    )


def test_risk_overview_matches_order_evaluations(client):
    for scenario in ("normal", "rain", "snow"):
        r = client.get("/api/risk/overview?scenario_id=" + scenario)
        assert r.status_code == 200
        d = r.json()
        assert d["active_orders"] == 6
        assert d["risk_orders"] == sum(row["risk"] >= 25 for row in d["rows"])
        assert d["high_risk"] == sum(row["risk"] >= 50 for row in d["rows"])
        assert d["average_delay"] == round(
            sum(row["delay_hours"] for row in d["rows"]) / 6, 4
        )
    assert client.get("/api/risk/overview?scenario_id=unknown").status_code == 422


def test_completed_order_not_dispatched_and_empty_simulation(client):
    for o in client.get("/api/orders").json():
        o["status"] = "已送达"
        assert client.put("/api/orders/" + o["id"], json=o).status_code == 200
    assert (
        client.post(
            "/api/analysis", json={"order_id": "SR-001", "scenario_id": "rain"}
        ).status_code
        == 409
    )
    assert (
        client.post("/api/simulation", json={"scenario_id": "rain"}).status_code == 409
    )
    assert (
        client.get("/api/risk/overview?scenario_id=rain").json()["active_orders"] == 0
    )


def test_model_failure_uses_real_rules(client, monkeypatch):
    import httpx

    d = client.post(
        "/api/analysis", json={"order_id": "SR-001", "scenario_id": "rain"}
    ).json()

    async def unavailable(*args, **kwargs):
        raise httpx.ConnectError("simulated offline provider")

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-not-a-real-key")
    monkeypatch.setattr(httpx.AsyncClient, "post", unavailable)
    r = client.post("/api/agent/explain", json={"report_id": d["id"]})
    assert r.status_code == 200 and r.json()["mode"] == "规则降级"
    assert d["recommendation"]["name"] in r.json()["text"]
    assert "test-only" not in r.text


def test_compatible_provider_request_is_backend_only(client, monkeypatch):
    import httpx

    d = client.post(
        "/api/analysis", json={"order_id": "SR-001", "scenario_id": "rain"}
    ).json()
    sent = {}

    async def fake_provider(self, url, **kwargs):
        sent.update({"url": url, **kwargs})
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "choices": [
                    {"message": {"content": "模型测试解释；数字以方案表为准。"}}
                ]
            },
        )

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_provider)
    r = client.post("/api/agent/explain", json={"report_id": d["id"]}).json()
    assert r["mode"] == "模型解释（算法数据为准）"
    assert sent["url"] == "https://example.invalid/v1/chat/completions"
    assert sent["json"]["model"] == "test-model"
    assert sent["headers"]["Authorization"] == "Bearer test-only-key"
    assert "test-only-key" not in str(r)
