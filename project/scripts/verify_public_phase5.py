"""Check actual proposed publication copies. Never sanitizes or publishes files."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("privacy", PROJECT / "scripts/audit_phase5_privacy.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
parser = argparse.ArgumentParser()
parser.add_argument("paths", nargs="+")
parser.add_argument("--output", default="docs/phase5/public-rescan.json")
args = parser.parse_args()
count = 0
properties = []
for root_string in args.paths:
    root = Path(root_string)
    candidates = sorted(root.rglob("*")) if root.is_dir() else [root]
    for p in candidates:
        if not p.is_file() or any(part in {".git", "node_modules", ".venv", "__pycache__"} for part in p.relative_to(root if root.is_dir() else root.parent).parts):
            continue
        count += 1
        loc = root.name + "/" + (p.relative_to(root).as_posix() if root.is_dir() else p.name)
        audit.scan(p.read_bytes(), loc, "public_candidate")
        if p.suffix == ".pptx":
            with zipfile.ZipFile(p) as archive:
                core = ET.fromstring(archive.read("docProps/core.xml"))
                for el in core:
                    field = el.tag.rsplit("}", 1)[-1]
                    if field in {"creator", "lastModifiedBy"}:
                        assert el.text == "Dux", "PPT attribution differs from explicit decision"
                        properties.append({"file": p.name, "field": field, "authorized_value": "Dux"})
forbidden = [f for f in audit.findings if f["kind"] in {"device_identifier", "local_user_path", "credential_candidate", "credential_assignment", "mobile_candidate", "identity_candidate", "identity_label"}]
emails = [f for f in audit.findings if f["kind"] == "email"]
# Public upstream legal notices and recording IDs require human classification;
# the scanner does not pretend every email-shaped match is a private mailbox.
result = {"passed": not forbidden and not audit.errors, "files": count,
          "forbidden_findings": forbidden, "email_shaped_matches": len(emails),
          "office_attribution": properties, "errors": audit.errors,
          "scope": [Path(x).name for x in args.paths],
          "limitations": "No pixel OCR or speech recognition; complementary documented visual review required."}
output = PROJECT / args.output
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != 'office_attribution'}, ensure_ascii=False))
if not result["passed"]:
    sys.exit(1)
