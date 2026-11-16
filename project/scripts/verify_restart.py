"""Independent real HTTP subprocess persistence check; temporary DB only."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def check():
    with tempfile.TemporaryDirectory(prefix="skyroute-restart-") as directory:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        env = {**os.environ, "SKYROUTE_DB": str(Path(directory) / "restart.db")}

        def call(path, method="GET", body=None):
            req = urllib.request.Request(
                base + path,
                method=method,
                data=json.dumps(body).encode() if body is not None else None,
                headers={"Content-Type": "application/json"},
            )
            return json.load(urllib.request.urlopen(req, timeout=5))

        def start():
            p = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(80):
                try:
                    call("/api/health")
                    return p
                except OSError:
                    if p.poll() is not None:
                        raise RuntimeError("Test server exited")
                    time.sleep(0.1)
            p.terminate()
            p.wait()
            raise RuntimeError("Test server startup timeout")

        p = start()
        try:
            task = call("/api/tasks")[0]
            task["outcome"] = "restart-persistence-proof"
            call("/api/tasks/" + task["id"], "PUT", task)
            cfg = call("/api/growth/config")
            cfg["channels"][0]["budget"] = 912
            call("/api/growth/config", "PUT", cfg)
            report = call(
                "/api/analysis", "POST", {"order_id": "SR-001", "scenario_id": "rain"}
            )
        finally:
            p.terminate()
            p.wait(timeout=10)
        p = start()
        try:
            assert call("/api/tasks")[0]["outcome"] == "restart-persistence-proof"
            assert call("/api/growth/config")["channels"][0]["budget"] == 912
            assert (
                call("/api/reports/" + report["id"])["recommendation"]
                == report["recommendation"]
            )
            output = {
                "passed": True,
                "method": "Real HTTP, stop process, start second process on same isolated SQLite file",
                "checks": ["task", "growth_config", "decision_report_snapshot"],
                "production_database_modified": False,
            }
            (ROOT / "docs/restart-results.json").write_text(
                json.dumps(output, indent=2), encoding="utf-8"
            )
            print(json.dumps(output))
        finally:
            p.terminate()
            p.wait(timeout=10)


if __name__ == "__main__":
    check()
