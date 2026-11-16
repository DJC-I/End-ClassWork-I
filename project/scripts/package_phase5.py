"""Assemble approved copies and verify ZIP members; no network actions."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
MATERIALS = PROJECT / ".tools/phase5/public-materials"
PUBLIC = PROJECT / ".tools/phase5/public-repo"
FINAL = ROOT / "SkyRoute-AI-v1.0.0-Final"
ASSETS = ROOT / "release-assets"
EXE_NAME = "SkyRoute-AI-v1.0.0-Windows-x64.exe"


def sha(p):
    with p.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write(folder, name, text):
    (folder / name).write_text(text, encoding="utf-8")


def make_zip(folder, name, prefix=""):
    path = ASSETS / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                archive.write(p, prefix + p.relative_to(folder).as_posix())
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
    return path


def main():
    decision = json.loads((PROJECT / "privacy-decision.json").read_text(encoding="utf-8"))
    assert decision["personal_information_decided"] and decision["font_redistribution_authorized"]
    assert decision.get("device_information_decided"), "New device metadata decision is still required"
    for name in ("01_校园赛正式提交", "02_课堂展示", "03_Windows桌面程序", "04_源码与开发", "05_验收与校验"):
        (FINAL / name).mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    campus = FINAL / "01_校园赛正式提交"
    classroom = FINAL / "02_课堂展示"
    windows = FINAL / "03_Windows桌面程序"
    dev = FINAL / "04_源码与开发"
    qa = FINAL / "05_验收与校验"
    for src_name, dest_name in [
        ("DataClawHub平台运营方案.docx", "赛题一_DataClawHub平台运营方案.docx"),
        ("气象驱动物流运输风险预警与应对决策.docx", "赛题二_气象物流AI风险决策系统.docx"),
        ("赛题一_DataClawHub平台运营方案.mp4", "赛题一_DataClawHub平台运营方案.mp4"),
        ("赛题二_气象物流AI风险决策系统.mp4", "赛题二_气象物流AI风险决策系统.mp4")]:
        copy(MATERIALS / src_name, campus / dest_name)
    for src in MATERIALS.iterdir():
        if src.suffix == ".srt" or src.name.endswith(("_解说稿.md", "_分镜脚本.md")):
            copy(src, campus / "字幕与脚本" / src.name)
    for src_name, dest_name in [
        ("人工智能导论_双赛题结课作品展示.pptx", "人工智能导论_双赛题结课作品展示.pptx"),
        ("课堂展示_单人完整演讲稿.docx", "课堂展示_单人演讲稿.docx"),
        ("答辩常见问题及参考回答.docx", "答辩问题及参考答案.docx"),
        ("演示操作清单.md", "课堂演示操作指南.md")]:
        copy(MATERIALS / src_name, classroom / dest_name)
    exe = PROJECT / ".tools/phase5/electron-dist" / EXE_NAME
    assert exe.stat().st_size > 1000000
    copy(exe, windows / EXE_NAME)
    copy(exe, ASSETS / EXE_NAME)
    write(windows, "Windows使用说明.md", """# Windows使用说明

双击同目录EXE，等待自动解压和本地服务就绪即可。无需安装Python、Node、SQLite服务或WebView。程序默认规则模式，核心流程离线可用。

用户数据在`%LOCALAPPDATA%/SkyRouteAI/skyroute.db`，不要在程序运行时改动数据库。首次自动初始化，关闭后再次启动保留修改；课堂页面明确确认后可重置教学场景。移动EXE不会改变同一Windows用户的数据目录。正常关闭窗口后业务服务一起退出。

未进行商业代码签名，系统可能显示SmartScreen信誉提醒；不需要关闭Defender。请从指定GitHub Release下载并核对SHA256SUMS。Windows 10/11 x64，推荐1440×900以上分辨率和约1GB空闲磁盘。未认证所有Windows版本或干净虚拟机。

若启动失败，先检查临时目录及用户数据目录是否可写，关闭重复实例后重试；程序不会自动删除已有数据库。需要备份时，退出程序后复制上述数据库。桌面版没有调试文档与模型密钥输入；可选外部模型请在源码网站版按.env.example配置。
""")
    write(classroom, "课堂应急方案.md", """# 课堂应急方案

提前解压材料并试播两个本地MP4。演讲由同一名学生完成，PPT12页、逐页排期360秒；约5分46秒是语速估算，仍需本人彩排。

- 网站启动失败：先用独立EXE；若仍失败，使用PPT真实截图并播放两个本地视频的预算实验/物流方案章节。
- 无网络：核心规则演示及本地材料不依赖网络，不点击外部数据源，不演示真实大模型调用。
- 时间不足：保留PPT第1、4、6、9、10、12页，直接展示预算改动及暴雨SR-001绕行方案；明确数据均为教学模拟。
- 音响或播放故障：使用烧录字幕或逐字稿讲解，采用PPT及Word静态结果，不谎称现场调用成功。

操作路径：`/demo`→赛题一→预算与增长模型；`/logistics`→暴雨风险→运行风险分析→方案/规则解释→情景仿真。桌面版方法页不提供API调试入口。
""")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PUBLIC).decode().strip()
    write(dev, "GitHub仓库说明.md", f"# 源码与版本\n\n仓库：https://github.com/DJC-I/End-ClassWork-I\n\n正式标签：v1.0.0。源码快照提交：`{commit}`。完整源码以仓库为准；不在材料ZIP中重复复制开发环境。\n\n公开源码从原有公开main提交继续，没有上传旧本地私人历史，也没有force push。历史私有材料保留在本地，正式提交使用本包最新版。\n")
    for src_name in ("README.md", "THIRD_PARTY_NOTICES.md", "CHANGELOG.md"):
        copy(PUBLIC / src_name, dev / src_name)
    copy(PUBLIC / "project/ARCHITECTURE.md", dev / "ARCHITECTURE.md")
    copy(PUBLIC / "project/desktop/README.md", dev / "桌面构建说明.md")
    copy(PUBLIC / "project/docs/PHASE4_6_DESIGN.md", dev / "设计系统.md")
    copy(PUBLIC / "PRIVACY_REVIEW.md", qa / "隐私审查摘要.md")
    for name in ("FINAL_AUDIT.md", "FUNCTIONAL_TEST_REPORT.md", "SECURITY_REVIEW.md", "KNOWN_LIMITATIONS.md", "PHASE5_ACCEPTANCE.md"):
        copy(PUBLIC / "project/docs/phase5" / name, qa / name)
    copy(PUBLIC / "RELEASE_NOTES.md", FINAL / "RELEASE_NOTES.md")
    write(FINAL, "README.md", """# SkyRoute AI v1.0.0 完整交付

01为校园赛正式材料，02为单人课堂展示，03为无需Python/Node的Windows独立程序，04为源码入口与技术说明，05为真实验收、隐私与校验记录。

全部物流、天气、运营与增长数据均为教学模拟。两条视频170/175秒、1920×1080，中文合成女声及烧录字幕；不是实际运输业绩或真人录音。

正式源码和下载：https://github.com/DJC-I/End-ClassWork-I/releases/tag/v1.0.0 。原始私有文件保留，当前目录为按明确决定整理的公开副本。PPT作者署名Dux已获授权。

请先阅读03的使用说明及05的已知限制。05/SHA256SUMS.txt覆盖包内其余文件（校验文件自身不自校验）；Release根SHA256SUMS.txt覆盖四个下载资产。发布文件清单.json不包含其自身及校验文件，以避免循环哈希。
""")
    listing = [{"file": p.relative_to(FINAL).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
               for p in sorted(FINAL.rglob("*")) if p.is_file() and p.name not in {"SHA256SUMS.txt", "发布文件清单.json"}]
    write(FINAL, "发布文件清单.json", json.dumps({"version": "v1.0.0", "source_commit": commit, "files": listing}, ensure_ascii=False, indent=2))
    sums = "\n".join(f"{sha(p)}  {p.relative_to(FINAL).as_posix()}" for p in sorted(FINAL.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt") + "\n"
    write(qa, "SHA256SUMS.txt", sums)
    assets = [ASSETS / EXE_NAME,
              make_zip(campus, "SkyRoute-AI-v1.0.0-校园赛正式提交材料.zip"),
              make_zip(classroom, "SkyRoute-AI-v1.0.0-课堂展示材料.zip"),
              make_zip(FINAL, "SkyRoute-AI-v1.0.0-完整交付包.zip", FINAL.name + "/")]
    write(ASSETS, "SHA256SUMS.txt", "\n".join(f"{sha(p)}  {p.name}" for p in assets) + "\n")
    manifest = [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in [*assets, ASSETS / "SHA256SUMS.txt"]]
    (PROJECT / "docs/phase5/release-assets.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"final_files": len(listing)+2, "release_assets": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
