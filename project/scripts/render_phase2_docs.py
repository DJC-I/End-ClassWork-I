"""Render Phase 2 with the packaged render_docx.py and an explicit isolated LO.

Usage (bundled Python):
  python scripts/render_phase2_docs.py --renderer PATH/render_docx.py --soffice PATH/soffice.exe
Never discovers or invokes the user's installed desktop LibreOffice.
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from pypdf import PdfReader

parser = argparse.ArgumentParser()
parser.add_argument("--renderer", required=True, type=Path)
parser.add_argument("--soffice", required=True, type=Path)
args = parser.parse_args()
assert args.renderer.is_file() and args.soffice.is_file()
root = Path(__file__).resolve().parents[1]
qa = root / "docs/phase2"
checks = json.loads((qa / "build_checks.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location("phase2_docx_renderer", args.renderer)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
renderer._resolve_soffice = lambda: str(args.soffice.resolve())
for entry, slug in zip(checks["outputs"], ("operations", "logistics")):
    target = qa / "render" / slug
    target.mkdir(parents=True, exist_ok=True)
    for stale in target.glob("page-*.png"):
        stale.unlink()
    sys.argv = [str(args.renderer), str(root / entry["file"]),
                "--output_dir", str(target), "--emit_pdf"]
    renderer.main()
    pages = sorted(target.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    assert len(pages) == len(PdfReader(next(target.glob("*.pdf"))).pages)
    entry["rendered_pages"] = len(pages)
    entry["render_directory"] = str(target.relative_to(root)).replace("\\", "/")
    print(f"{slug}: {len(pages)} pages", flush=True)
(qa / "render_checks.json").write_text(json.dumps({
    "renderer": str(args.renderer.resolve()),
    "soffice": str(args.soffice.resolve()),
    "bundled_libreoffice_available": False,
    "fallback": "Task-local official portable LibreOffice; no desktop installation used",
    "outputs": checks["outputs"],
}, ensure_ascii=False, indent=2), encoding="utf-8")
