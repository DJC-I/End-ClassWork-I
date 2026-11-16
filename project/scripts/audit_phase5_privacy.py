"""Local, non-destructive review. Reports masked evidence only; never approves release.

Scans tracked files, selected runtime outputs, all locally recoverable Git objects,
Office XML (including nested workbooks), PDFs and SQLite read-only snapshots.
Images/audio/video require an additional visual/listening review.
"""
import collections
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "project"
OUT = PROJECT / "docs/phase5"
sys.path.insert(0, str(PROJECT / ".tools/phase5/pydeps"))

PATTERNS = {
    "device_identifier": re.compile(r'''\bhostname\s*=\s*["'](?!local-test["'])([^"']+)["']''', re.I),
    "local_user_path": re.compile(r"(?i)(?:[a-z]:[\\/]+Users[\\/]+|/ho" r"me/)([^\\/\s\"<>:,]+)"),
    "email": re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])"),
    "mobile_candidate": re.compile(r"(?<![\w.])1[3-9]\d{9}(?![\w.])"),
    "identity_candidate": re.compile(r"(?<![\w.])[1-9]\d{5}(?:19|20)\d{9}[\dXx](?!\w)"),
    "credential_candidate": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AKIA[A-Z0-9]{16})"),
    "credential_assignment": re.compile(r'''(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|cookie|session[_-]?token)\s*["']?\s*[:=]\s*["']([^\s"'<>]{12,})'''),
    "identity_label": re.compile(r"(?:姓名|学号|手机|邮箱|微信|QQ号|宿舍|组员|成员姓名)[：:]\s*([^\s<，。；|]{2,40})"),
}
findings = []
properties = []
inventory = []
errors = []
counts = collections.Counter()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def masked(kind, value):
    if kind.startswith("credential"):
        return "[疑似凭证，未显示原值]"
    if kind == "email":
        a, b = value.split("@", 1)
        return a[:1] + "***@" + ("users.noreply.github.com" if b == "users.noreply.github.com" else "***")
    if kind == "local_user_path":
        return "<user:" + value[:1] + "***>"
    return value[:1] + "***" + (value[-1:] if len(value) > 5 else "")


def text_scan(text, location, scope):
    for kind, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            value = m.group(1) if m.lastindex else m.group()
            if kind == "credential_assignment" and any(x in value.lower() for x in ("example", "your_", "dummy", "placeholder", "getenv", "os.env", "test", "你的", "模拟")):
                continue
            findings.append({"kind": kind, "scope": scope, "location": location,
                             "line": text.count("\n", 0, m.start()) + 1,
                             "masked": masked(kind, value),
                             "value_fingerprint": hashlib.sha256(value.encode()).hexdigest()[:12]})


def archive_scan(data, location, scope, depth=0):
    if depth > 3:
        errors.append({"location": location, "reason": "archive depth limit"})
        return
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for entry in z.infolist():
            if entry.is_dir():
                continue
            loc = location + "!" + entry.filename
            text_scan(entry.filename, loc + ":filename", scope)
            suffix = Path(entry.filename).suffix.lower()
            if suffix in {".xml", ".rels", ".txt", ".json", ".csv", ".md", ".srt", ".vtt", ".html"}:
                raw = z.read(entry).decode("utf-8", "replace")
                text_scan(raw, loc, scope)
                if suffix == ".xml":
                    try:
                        tree = ET.fromstring(raw)
                        text_scan("\n".join(tree.itertext()), loc + ":text", scope)
                        for el in tree.iter():
                            key = el.tag.rsplit("}", 1)[-1]
                            if key in {"creator", "lastModifiedBy", "Company", "Manager", "author", "Author"} and el.text:
                                properties.append({"location": loc, "field": key,
                                                   "masked": masked("property", el.text),
                                                   "generic": el.text in {"Codex", "python-docx", "AI课程作品", "课程作品", "SkyRoute AI", "AI Course Project"},
                                                   "scope": scope})
                            for attr, value in el.attrib.items():
                                if attr.rsplit("}", 1)[-1] in {"author", "authorId", "displayName", "initials"}:
                                    properties.append({"location": loc, "field": attr,
                                                       "masked": masked("property", value), "scope": scope})
                    except ET.ParseError:
                        pass
            elif suffix in {".docx", ".pptx", ".xlsx", ".zip"}:
                archive_scan(z.read(entry), loc, scope, depth + 1)
            elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
                counts["office_embedded_images"] += 1
            counts["archive_members"] += 1


TEXT_EXT = {".md", ".txt", ".py", ".ts", ".tsx", ".js", ".cjs", ".mjs", ".json", ".xml", ".css", ".html", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".lock", ".cmd", ".ps1", ".csv", ".srt", ".svg", ".log", ".env", ".example", ".gitignore", ".vtt", ".spec"}


def scan(data, location, scope):
    suffix = Path(location).suffix.lower()
    counts["files_" + scope] += 1
    text_scan(location, location + ":filename", scope)
    if suffix in {".docx", ".pptx", ".xlsx", ".zip"} or data[:4] == b"PK\x03\x04":
        try:
            archive_scan(data, location, scope)
        except Exception as exc:
            errors.append({"location": location, "reason": type(exc).__name__})
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            for i, page in enumerate(reader.pages):
                text_scan(page.extract_text() or "", f"{location}:page{i+1}", scope)
            if reader.metadata:
                text_scan(str(reader.metadata), location + ":metadata", scope)
                for key in ("/Author", "/Creator"):
                    if reader.metadata.get(key):
                        properties.append({"location": location, "field": key,
                                           "masked": masked("property", str(reader.metadata[key])), "scope": scope})
        except Exception as exc:
            errors.append({"location": location, "reason": type(exc).__name__})
    elif suffix in TEXT_EXT or (len(data) < 2000000 and b"\x00" not in data[:8192]):
        text_scan(data.decode("utf-8", "replace"), location, scope)
    elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        try:
            from PIL import Image
            with Image.open(io.BytesIO(data)) as img:
                text_scan(str(img.info) + str(dict(img.getexif())), location + ":metadata", scope)
            counts["image_metadata"] += 1
        except Exception as exc:
            errors.append({"location": location, "reason": type(exc).__name__})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tracked = [x.decode("utf-8") for x in git("ls-files", "-z").split(b"\0") if x]
    selected = set(tracked)
    for folder in ("frontend/dist", "database", "docs", "deliverables"):
        for p in (PROJECT / folder).rglob("*"):
            if p.is_file() and "phase5" not in p.relative_to(PROJECT).parts:
                selected.add(p.relative_to(ROOT).as_posix())
    for folder in ("backend", "frontend/src", "scripts", "desktop", "tests"):
        for p in (PROJECT / folder).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts and "node_modules" not in p.parts:
                selected.add(p.relative_to(ROOT).as_posix())
    if (PROJECT / ".env").is_file():
        selected.add("project/.env")
    for loc in sorted(selected):
        p = ROOT / loc
        if not p.is_file():
            continue
        data = p.read_bytes()
        inventory.append({"path": loc, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "tracked": loc in tracked})
        if data[:16] == b"SQLite format 3\x00":
            try:
                with sqlite3.connect(p.as_uri() + "?mode=ro", uri=True) as con:
                    for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                        name = row[0]
                        safe = name.replace('"', '""')
                        for idx, record in enumerate(con.execute(f'SELECT * FROM "{safe}"')):
                            text_scan(json.dumps(record, ensure_ascii=False), f"{loc}:table:{name}:row:{idx+1}", "runtime")
                counts["sqlite_databases"] += 1
            except Exception as exc:
                errors.append({"location": loc, "reason": type(exc).__name__})
        else:
            scan(data, loc, "working")
    # Includes reachable refs, fetched remote history, reflogs and dangling objects.
    names = {}
    for line in git("rev-list", "--objects", "--all", "--reflog").decode("utf-8", "replace").splitlines():
        bits = line.split(" ", 1)
        names.setdefault(bits[0], bits[1] if len(bits) > 1 else "")
    objects = git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype) %(objectsize)").decode().splitlines()
    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for row in objects:
        sha, kind, size = row.split()
        counts["git_objects"] += 1
        if kind not in {"blob", "commit", "tag"}:
            continue
        proc.stdin.write((sha + "\n").encode()); proc.stdin.flush()
        header = proc.stdout.readline().decode().split()
        data = proc.stdout.read(int(header[2])); proc.stdout.read(1)
        if kind == "blob":
            scan(data, f"git:{sha[:12]}:{names.get(sha, 'unreachable-blob')}", "history")
        else:
            text_scan(data.decode("utf-8", "replace"), f"git:{sha}:{kind}", "git_metadata")
    proc.stdin.close(); proc.wait()
    # Do not record absolute input paths or any unmasked values.
    result = {"scope": "local review; no publication authorization", "counts": dict(counts),
              "tracked_file_count": len(tracked), "inventory_file_count": len(inventory),
              "findings": findings, "document_properties": properties, "errors": errors,
              "limitations": ["Pattern scan cannot establish identity or completeness.",
                              "Image pixels and spoken media require separate inspection.",
                              "No EXE or final ZIP exists yet; post-build rescan required.",
                              "Dependency environments/tools are excluded from proposed release."]}
    (OUT / "privacy-scan.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "input-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(inventory), "tracked": len(tracked), "counts": counts,
                      "finding_counts": collections.Counter(f["kind"] for f in findings),
                      "property_records": len(properties), "errors": errors}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
