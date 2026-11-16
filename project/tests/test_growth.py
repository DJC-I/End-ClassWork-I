import math
import pytest
from backend import growth, seed
from backend.content import CONTENT


def test_expected_funnel_and_cac():
    r = growth.calculate(seed.GROWTH_CONFIG)
    assert [x["value"] for x in r["funnel"]] == [12000, 1440, 403.2, 201.6, 70.56]
    reach = (
        600 / 80 * 1000
        + 800 / 100 * 1000
        + 400 / 90 * 1000
        + 1000 / 200 * 1000
        + 200 / 250 * 1000
    )
    active = reach * 0.12 * 0.28 * 0.5
    assert r["channel_reach"] == round(reach, 2)
    assert r["cac"] == round(3000 / active, 2)
    d = {**seed.GROWTH_CONFIG, "visit_rate": 0}
    assert growth.calculate(d)["cac"] is None
    assert all(c["cac"] is None for c in growth.calculate(d)["channels"])


def test_budget_scenario_is_linear():
    c = seed.GROWTH_CONFIG
    r = growth.calculate(c)
    bigger = growth.calculate(
        {**c, "channels": [{**x, "budget": x["budget"] * 1.2} for x in c["channels"]]}
    )
    assert bigger["budget"] == r["budget"] * 1.2
    assert bigger["channel_active"] == pytest.approx(
        r["channel_active"] * 1.2, abs=0.01
    )
    assert bigger["cac"] == r["cac"]


def test_ab_swap_symmetry_and_insufficient_sample():
    r = growth.experiment(
        {"a_visitors": 200, "a_conversions": 30, "b_visitors": 200, "b_conversions": 40}
    )
    swapped = growth.experiment(
        {"a_visitors": 200, "a_conversions": 40, "b_visitors": 200, "b_conversions": 30}
    )
    assert r["difference_pp"] == 5
    assert r["p_value"] == swapped["p_value"]
    assert r["difference_pp"] == -swapped["difference_pp"]
    assert r["adequate"] and not r["significant"]
    tiny = growth.experiment(
        {"a_visitors": 10, "a_conversions": 1, "b_visitors": 10, "b_conversions": 7}
    )
    assert not tiny["adequate"] and not tiny["significant"]
    zero = growth.experiment(
        {"a_visitors": 100, "a_conversions": 0, "b_visitors": 100, "b_conversions": 0}
    )
    assert zero["p_value"] == 1 and zero["lift"] is None
    assert math.isfinite(zero["p_value"])


def test_plan_has_score_relevant_content():
    assert len(CONTENT["personas"]) == 4
    assert len(CONTENT["strategies"]) >= 6
    assert len(CONTENT["experiments"]) >= 3
    assert "D7" in CONTENT["schedule_note"]
    assert all(
        all(p[k] for k in ("need", "channel", "motivation", "barrier", "action"))
        for p in CONTENT["personas"]
    )


def test_task_dates_and_trial_counts_validate(client):
    t = client.get("/api/tasks").json()[0]
    t["end"] = "2026-01-01"
    assert client.put("/api/tasks/" + t["id"], json=t).status_code == 422
    c = client.get("/api/growth/config").json()
    c["channels"][0]["cpm"] = 0
    assert client.post("/api/growth/calculate", json=c).status_code == 422
    assert (
        client.post(
            "/api/growth/experiment",
            json={
                "a_visitors": 0,
                "a_conversions": 0,
                "b_visitors": 10,
                "b_conversions": 1,
            },
        ).status_code
        == 422
    )
