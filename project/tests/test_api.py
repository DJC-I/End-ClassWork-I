from copy import deepcopy
from backend.seed import ORDERS
from backend import db


def test_health_bootstrap(client):
    assert client.get("/api/health").json()["status"] == "ok"
    d = client.get("/api/bootstrap").json()
    assert len(d["orders"]) == 6 and len(d["network"]["edges"]) == 10


def test_order_crud_persistence(client):
    o = deepcopy(ORDERS[0])
    o["id"] = "TEST-001"
    assert client.post("/api/orders", json=o).status_code == 201
    o["priority"] = 1
    assert client.put("/api/orders/TEST-001", json=o).status_code == 200
    assert db.get("orders", "TEST-001")["priority"] == 1
    assert client.get("/api/orders?q=TEST-001").json()[0]["id"] == "TEST-001"
    assert client.post("/api/orders", json=o).status_code == 409
    assert client.delete("/api/orders/TEST-001").status_code == 200
    assert client.get("/api/orders/TEST-001").status_code == 404


def test_invalid_orders(client):
    for delta in (
        {"weight": -1},
        {"deadline": "2026-11-15T08:00:00+08:00"},
        {"route": ["BJ", "TJ"]},
        {"weight": 29},
        {"base_hours": 5},
        {"base_cost": 1},
        {"departure": "2026-11-16T10:00:00"},
    ):
        o = {**ORDERS[0], **delta, "id": "INVALID"}
        r = client.post("/api/orders", json=o)
        assert r.status_code == 422, r.text
        assert "error" in r.json()


def test_import_atomicity(client):
    first = {**ORDERS[0], "id": "NEW-IMPORT"}
    r = client.post("/api/orders/import", json=[first, ORDERS[1]])
    assert r.status_code == 409
    assert client.get("/api/orders/NEW-IMPORT").status_code == 404
    assert client.post("/api/orders/import", json=[first]).json()["imported"] == 1
    assert "text/csv" in client.get("/api/orders/export").headers["content-type"]


def test_tasks_config_scenario_reset(client):
    task = client.get("/api/tasks").json()[0]
    task["status"] = "已完成"
    assert client.put("/api/tasks/" + task["id"], json=task).status_code == 200
    assert db.get("tasks", task["id"])["status"] == "已完成"
    assert (
        client.put("/api/scenarios/current", json={"scenario_id": "snow"}).status_code
        == 200
    )
    assert client.get("/api/bootstrap").json()["current_scenario"] == "snow"
    cfg = client.get("/api/growth/config").json()
    cfg["channels"][0]["budget"] = 900
    assert client.put("/api/growth/config", json=cfg).status_code == 200
    assert client.get("/api/growth/config").json()["channels"][0]["budget"] == 900
    assert client.post("/api/demo/reset").status_code == 200
    assert len(client.get("/api/orders").json()) == 6


def test_growth_report_and_errors(client):
    cfg = client.get("/api/growth/config").json()
    result = client.post("/api/growth/calculate", json=cfg).json()
    assert result["funnel"][1]["value"] == 1440
    assert result["budget"] == 3000
    report = client.post("/api/growth/report", json=cfg).json()
    assert client.get("/api/reports/" + report["id"]).json()["kind"] == "growth"
    assert "假设预算" in client.get("/api/reports/" + report["id"] + "/download").text
    cfg["visit_rate"] = 2
    assert client.post("/api/growth/calculate", json=cfg).status_code == 422
    bad = {"a_visitors": 5, "a_conversions": 6, "b_visitors": 5, "b_conversions": 1}
    assert client.post("/api/growth/experiment", json=bad).status_code == 422


def test_deleted_all_not_reseeded(client):
    for o in client.get("/api/orders").json():
        client.delete("/api/orders/" + o["id"])
    db.init()
    assert client.get("/api/orders").json() == []
