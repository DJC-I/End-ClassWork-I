"""Prepared desktop-only entry. No developer database, .env or credentials bundled.

This module is tested locally; final EXE packaging remains gated by privacy review.
"""
import json
import os
import secrets
import socket
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path


def run():
    token = os.environ.get("SKYROUTE_DESKTOP_TOKEN", "")
    if len(token) < 32:
        raise RuntimeError("Desktop session token is required")
    data = Path(os.environ["SKYROUTE_DB"]).resolve()
    data.parent.mkdir(parents=True, exist_ok=True)
    # Prevent accidental use of any developer environment file in the bundle.
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    if not getattr(sys, "frozen", False):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import uvicorn
    from starlette.responses import JSONResponse
    from backend.main import app

    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") not in {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}]
    app.docs_url = app.redoc_url = app.openapi_url = None
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    expected_host = f"127.0.0.1:{port}"

    @app.middleware("http")
    async def desktop_boundary(request, call_next):
        authorized = secrets.compare_digest(request.headers.get("x-skyroute-session", ""), token)
        if request.headers.get("host") != expected_host or not authorized:
            return JSONResponse({"error": {"code": "SESSION_REQUIRED", "message": "请从桌面窗口访问"}}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin != f"http://{expected_host}":
            return JSONResponse({"error": {"code": "ORIGIN_REJECTED", "message": "来源校验失败"}}, status_code=403)
        if request.url.path in {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}:
            return JSONResponse({"error": {"code": "HTTP_404", "message": "接口不存在"}}, status_code=404)
        response = await call_next(request)
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        return response

    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def ready_lifespan(instance):
        async with original_lifespan(instance):
            print(json.dumps({"event": "ready", "port": port}), flush=True)
            yield

    app.router.lifespan_context = ready_lifespan
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
                                         log_level="warning", access_log=False))

    def control():
        # Pipe closes when the Electron parent exits, including an unexpected exit.
        try:
            for line in sys.stdin:
                if line.strip() == "shutdown":
                    break
        finally:
            server.should_exit = True
            # A stuck request must not orphan the backend indefinitely.
            def hard_stop():
                time.sleep(8)
                os._exit(0)
            threading.Thread(target=hard_stop, daemon=True).start()

    threading.Thread(target=control, daemon=True).start()
    try:
        server.run(sockets=[listener])
    finally:
        listener.close()


if __name__ == "__main__":
    run()
