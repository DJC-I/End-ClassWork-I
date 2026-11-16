"""Real subprocess tests for prepared desktop boundary, not packaged EXE acceptance."""
import contextlib
import json
import os
from pathlib import Path
import queue
import secrets
import subprocess
import sys
import threading
import urllib.error
import urllib.request


@contextlib.contextmanager
def desktop_service(database):
    root = Path(__file__).resolve().parents[1]
    token = secrets.token_hex(32)
    env = dict(os.environ, SKYROUTE_DB=str(database), SKYROUTE_DESKTOP_TOKEN=token,
               PYTHONIOENCODING="utf-8")
    env.pop("OPENAI_API_KEY", None)
    proc = subprocess.Popen([sys.executable, str(root / "desktop/backend_entry.py")],
                            cwd=database.parent, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                            encoding="utf-8")
    messages = queue.Queue()
    threading.Thread(target=lambda: messages.put(proc.stdout.readline()), daemon=True).start()
    try:
        message = json.loads(messages.get(timeout=20))
        assert message["event"] == "ready"
        base = f'http://127.0.0.1:{message["port"]}'

        def call(path, *, headers=None, method="GET", data=None):
            request = urllib.request.Request(base + path, method=method,
                headers={"X-SkyRoute-Session": token, "Content-Type": "application/json", **(headers or {})},
                data=json.dumps(data).encode() if data is not None else None)
            try:
                response = urllib.request.urlopen(request, timeout=10)
            except urllib.error.HTTPError as exc:
                response = exc
            body = response.read()
            return response.status, body, dict(response.headers)

        yield call, base
    finally:
        if proc.poll() is None:
            proc.stdin.write("shutdown\n"); proc.stdin.flush(); proc.stdin.close()
        try:
            proc.wait(timeout=12)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait()
            raise AssertionError("Desktop service failed graceful shutdown")
        proc.stdout.close()
        assert proc.returncode == 0


def test_desktop_session_origin_and_debug_boundary(tmp_path):
    with desktop_service(tmp_path / "desktop.db") as (call, base):
        status, body, headers = call("/api/health")
        assert status == 200 and json.loads(body)["status"] == "ok"
        assert "frame-ancestors 'none'" in headers["content-security-policy"]
        assert call("/api/health", headers={"X-SkyRoute-Session": ""})[0] == 403
        assert call("/api/health", headers={"Origin": "https://example.invalid"})[0] == 403
        assert call("/api/health", headers={"Host": "example.invalid"})[0] == 403
        for path in ("/docs", "/redoc", "/openapi.json"):
            assert call(path)[0] == 404
        assert call("/", headers={"Origin": base})[0] == 200


def test_desktop_persistence_and_seed_isolation(tmp_path):
    database = tmp_path / "desktop.db"
    assert not database.exists()
    with desktop_service(database) as (call, _):
        status, body, _ = call("/api/growth/config")
        assert status == 200
        config = json.loads(body)
        original = config["channels"][0]["budget"]
        config["channels"][0]["budget"] = original + 111
        assert call("/api/growth/config", method="PUT", data=config)[0] == 200
    assert database.is_file()
    with desktop_service(database) as (call, _):
        assert json.loads(call("/api/growth/config")[1])["channels"][0]["budget"] == original + 111
        assert call("/api/demo/reset", method="POST")[0] == 200
        assert json.loads(call("/api/growth/config")[1])["channels"][0]["budget"] == original
