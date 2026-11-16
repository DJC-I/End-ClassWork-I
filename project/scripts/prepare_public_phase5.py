"""Prepare an approved, independent release copy; never rewrite private originals."""
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "project"
STAGE = PROJECT / ".tools/phase5/public-repo"
MATERIALS = PROJECT / ".tools/phase5/public-materials"
USER_PATH = re.compile(r"(?i)[a-z]:[\\/]+Users[\\/]+[^\\/\s\"<>:,]+[\\/]*")


def relative_paths(text):
    # Known project-root prefix first, then private home-relative references.
    current = str(ROOT)
    for prefix in (current.replace("\\", "\\\\"), current.replace("\\", "/"), current):
        text = re.sub(re.escape(prefix) + r"(?:[\\/]+)?", "./", text, flags=re.I)
    text = USER_PATH.sub("./", text)
    return re.sub(r'''(\bhostname\s*=\s*["'])[^"']*(["'])''', r'\1local-test\2', text, flags=re.I)


def office(data, pptx):
    result = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as src, zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            content = src.read(info)
            if info.filename.endswith((".xml", ".rels")):
                content = relative_paths(content.decode("utf-8")).encode("utf-8")
            if pptx and info.filename == "docProps/core.xml":
                tree = ET.fromstring(content)
                for name in ("{http://purl.org/dc/elements/1.1/}creator", "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy"):
                    el = tree.find(name)
                    if el is None:
                        el = ET.SubElement(tree, name)
                    el.text = "Dux"
                content = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
            dst.writestr(info, content)
    return result.getvalue()


TEXT = {".md", ".py", ".ts", ".tsx", ".js", ".cjs", ".mjs", ".json", ".xml", ".css", ".html", ".yml", ".yaml", ".txt", ".cmd", ".ps1", ".toml", ".ini", ".gitignore", ".example", ".srt", ".svg", ".spec"}


def copy_public(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    if src.suffix in {".docx", ".pptx"}:
        data = office(data, src.suffix == ".pptx")
    elif src.suffix.lower() in TEXT or src.name in {".gitignore", "start.cmd"}:
        data = relative_paths(data.decode("utf-8-sig")).encode("utf-8")
    dst.write_bytes(data)


def main():
    assert json.loads((PROJECT / "privacy-decision.json").read_text(encoding="utf-8"))["font_redistribution_authorized"]
    STAGE.mkdir(parents=True, exist_ok=True)
    MATERIALS.mkdir(parents=True, exist_ok=True)
    paths = [p.decode() for p in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0") if p]
    paths += [str(p.relative_to(ROOT)).replace("\\", "/") for folder in ("desktop", "scripts", "tests") for p in (PROJECT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and "node_modules" not in p.parts]
    paths += ["project/privacy-decision.json"]
    paths += [str(p.relative_to(ROOT)).replace("\\", "/") for p in (PROJECT / "docs/phase5").rglob("*") if p.is_file() and p.suffix in TEXT]
    paths += ["project/frontend/playwright.phase5.config.cjs"]
    count = 0
    for loc in sorted(set(paths)):
        rel = Path(loc)
        if rel.parts[0] != "project" or "deliverables" in rel.parts:
            continue
        if "docs" in rel.parts:
            if rel.name == "desktop-e2e-failure.txt":
                continue
            # Keep technical text and current screenshots; historical media/render
            # evidence remains private instead of bloating public source history.
            if rel.suffix not in TEXT and not ("phase4_6" in rel.parts and "assets" in rel.parts):
                continue
            if rel.suffix == ".log":
                continue
        if "database" in rel.parts or "node_modules" in rel.parts or rel.suffix == ".pyc":
            continue
        if (ROOT / rel).is_file():
            copy_public(ROOT / rel, STAGE / rel)
            count += 1
    for name in ("README.md", "CHANGELOG.md", "RELEASE_NOTES.md", "THIRD_PARTY_NOTICES.md", "PRIVACY_REVIEW.md", ".gitignore", ".github/workflows/release.yml"):
        copy_public(ROOT / name, STAGE / name)
        count += 1
    for src in (PROJECT / "deliverables/phase4_6").iterdir():
        if src.is_file() and src.name != "SHA256SUMS.txt":
            copy_public(src, MATERIALS / src.name)
    guide = MATERIALS / "演示操作清单.md"
    text = guide.read_text(encoding="utf-8")
    text = text.replace("## 上课前准备", "## 桌面正式版快速开始\n\n优先双击独立EXE，无需终端或依赖安装；从课堂演示页进入增长与物流。窗口关闭后服务一起退出。下方源码命令为开发备用；桌面版不提供/docs调试页。视频在完整交付包01目录，PPT与讲稿在02目录。使用个人数据前先备份，重置仅用于教学库。\n\n## 上课前准备")
    text = text.replace("第4.6阶段验收后停止，等待“继续第五阶段”。", "发布版使用上述独立EXE和本目录最新版课堂材料。")
    text = text.replace("`/docs` → 后端接口说明。", "`/docs` → 源码网站版接口说明，桌面版关闭。")
    guide.write_text(text, encoding="utf-8")
    records = [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
               for p in sorted(MATERIALS.iterdir()) if p.is_file()]
    (PROJECT / "docs/phase5/public-materials-manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"source_files": count, "material_files": len(records), "private_originals_modified": False}))


if __name__ == "__main__":
    main()
