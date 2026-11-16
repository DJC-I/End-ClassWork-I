"""Inspect compiled code and resource contents without executing embedded code."""
import hashlib
import json
import marshal
from pathlib import Path
import re
import sys
import types
from PyInstaller.archive.readers import CArchiveReader

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / ".tools/phase5/pyinstaller-dist/skyroute-service"
OUT = ROOT / "docs/phase5"
pattern = re.compile(r"(?i)[a-z]:[\\/]+Users[\\/]+([^\\/\s\"'<>:,()\x00]+)")
bad = []
code_count = 0
upstream_examples = []
standard_source = (Path(sys.base_prefix) / 'Lib/ntpath.py').read_text(encoding='utf-8')
fixture_users = {m.group(1) for m in pattern.finditer(standard_source)}


def inspect_code(code, label):
    global code_count
    if isinstance(code, types.CodeType):
        code_count += 1
        if pattern.search(code.co_filename):
            bad.append({"entry": label, "kind": "absolute_user_co_filename"})
        for item in code.co_consts:
            inspect_code(item, label)
    elif isinstance(code, (tuple, list)):
        for item in code:
            inspect_code(item, label)
    elif isinstance(code, str) and pattern.search(code):
        bad.append({"entry": label, "kind": "absolute_user_string"})


archive = CArchiveReader(str(BUNDLE / "skyroute-service.exe"))
for name in archive.toc:
    if name == "PYZ.pyz":
        pyz = archive.open_embedded_archive(name)
        for module in pyz.toc:
            item = pyz.extract(module)
            inspect_code(item, module)
    elif name in {"backend_entry", "pyiboot01_bootstrap"}:
        inspect_code(marshal.loads(archive.extract(name)), name)
files = []
for p in BUNDLE.rglob("*"):
    if not p.is_file():
        continue
    rel = p.relative_to(BUNDLE).as_posix()
    if p.name == ".env" or p.suffix in {".db", ".sqlite", ".log"} or any(t in p.parts for t in {".git", ".venv", "node_modules"}):
        bad.append({"entry": rel, "kind": "forbidden_resource"})
    raw = p.read_bytes()
    for encoding in ("utf-8", "utf-16-le"):
        for match in pattern.finditer(raw.decode(encoding, "ignore")):
            user = match.group(1)
            if user == 'runneradmin' or (rel in {'_internal/base_library.zip', '_internal/python312.dll'} and user in fixture_users):
                upstream_examples.append({"entry": rel, "kind": 'public_upstream_CI_account_or_ntpath_documentation_fixture'})
            else:
                bad.append({"entry": rel, "kind": "absolute_user_resource_string", "encoding": encoding})
    files.append({"file": rel, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
font = BUNDLE / "_internal/frontend/dist/fonts/user-pingfang.ttf"
assert font.is_file()
assert hashlib.sha256(font.read_bytes()).hexdigest() == hashlib.sha256((ROOT / "frontend/public/fonts/user-pingfang.ttf").read_bytes()).hexdigest()
result = {"passed": not bad, "compiled_code_objects": code_count, "resource_files": len(files),
          "font_matches_user_original": True, "findings": bad, "upstream_generic_matches": len(upstream_examples), "inventory": files}
(OUT / "python-bundle-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "inventory"}))
assert not bad
