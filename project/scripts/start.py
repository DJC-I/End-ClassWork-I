"""One command bootstrap, build and run, with all files scoped to this project."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd=ROOT):
    subprocess.run([str(x) for x in args], cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev", action="store_true", help="Start backend reload and Vite together"
    )
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Use an existing production build offline",
    )
    args = parser.parse_args()
    py = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not py.exists():
        run([sys.executable, "-m", "venv", ROOT / ".venv"])
    stamp = ROOT / ".venv" / "skyroute-requirements.txt"
    requirements = ROOT / "backend" / "requirements.txt"
    if not stamp.exists() or stamp.read_bytes() != requirements.read_bytes():
        run([py, "-m", "pip", "install", "-r", requirements])
        stamp.write_bytes(requirements.read_bytes())
    if args.dev or not args.no_build:
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if not npm:
            raise SystemExit(
                "Node.js/npm is required for the first build. Install Node.js 22.12+."
            )
        if not (ROOT / "frontend/node_modules").exists():
            run([npm, "ci"], ROOT / "frontend")
        if not args.dev:
            run([npm, "run", "build"], ROOT / "frontend")
    if not args.dev and not (ROOT / "frontend/dist/index.html").exists():
        raise SystemExit("Missing frontend build. Run without --no-build once.")
    if args.dev and args.port != 8000:
        raise SystemExit(
            "Dev proxy expects backend port 8000; omit --port in dev mode."
        )
    print(
        f"SkyRoute local URL: http://127.0.0.1:{5173 if args.dev else args.port}",
        flush=True,
    )
    command = [
        py,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
    ]
    if args.dev:
        command += ["--reload"]
    frontend = None
    try:
        if args.dev:
            frontend = subprocess.Popen(
                [
                    shutil.which("node"),
                    str(ROOT / "frontend/node_modules/vite/bin/vite.js"),
                    "--host",
                    "127.0.0.1",
                ],
                cwd=ROOT / "frontend",
            )
        run(command)
    except KeyboardInterrupt:
        pass
    finally:
        if frontend is not None:
            frontend.terminate()
            frontend.wait(timeout=10)


if __name__ == "__main__":
    main()
