"""Check final DOCX structure, coverage, source values and rendered page counts."""
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "docs/phase2"
build = json.loads((QA / "build_checks.json").read_text(encoding="utf-8"))
render = json.loads((QA / "render_checks.json").read_text(encoding="utf-8"))
requirements = [
    ["项目摘要", "平台研究", "需求分析", "用户画像", "运营目标", "核心策略", "渠道规划", "执行方案", "时间排期", "预算", "增长实验", "数据假设", "风险复盘", "结论"],
    ["项目摘要", "问题背景", "需求", "系统架构", "技术栈", "数据来源", "风险模型", "AI智能体设计", "优化算法", "页面截图", "功能演示", "测试结果", "模拟结果分析", "局限性", "未来优化", "结论"],
]
results = []
for i, (b, r) in enumerate(zip(build["outputs"], render["outputs"])):
    path = ROOT / b["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == b["sha256"] == r["sha256"]
    with ZipFile(path) as z:
        assert z.testzip() is None
        xml = z.read("word/document.xml").decode("utf-8")
        assert "<w:pBdr" not in xml
        assert "<w:pBdr" not in z.read("word/styles.xml").decode("utf-8")
        assert "oai-mem-citation" not in xml and "TODO" not in xml
    d = Document(path)
    text = "\n".join([p.text for p in d.paragraphs] + [c.text for t in d.tables for row in t.rows for c in row.cells])
    flat = re.sub(r"\s+", "", text)
    assert all(x in flat for x in requirements[i]), [x for x in requirements[i] if x not in flat]
    assert len(d.inline_shapes) == (1 if i == 0 else 5)
    assert "模拟" in text and "未" in text
    assert "2026年11月16日" in text
    for st in ("Title", "Subtitle", "Heading 1", "Heading 2"):
        assert str(d.styles[st].font.color.rgb) == "000000"
    title = [p for p in d.paragraphs if p.style.name == "Title"]
    assert len(title) == 1
    assert r["rendered_pages"] == b["expected_pages"]
    rdir = ROOT / r["render_directory"]
    pdfs = list(rdir.glob("*.pdf"))
    assert len(pdfs) == 1
    pdf = PdfReader(pdfs[0])
    assert len(pdf.pages) == b["expected_pages"]
    page_text = [p.extract_text() or "" for p in pdf.pages]
    assert all(len(x.strip()) > 10 for x in page_text), "blank or near-blank page"
    assert len(list(rdir.glob("page-*.png"))) == len(pdf.pages)
    # Final text remains readable/searchable in the rendering, with no replacement glyphs.
    assert "\ufffd" not in "".join(page_text)
    if i == 0:
        assert "3000" in text and "3300" in text and "0.18821" in text
        assert "800人" in text and "432.51" in text
    else:
        assert "1357.01" in text and "1242.00" in text and "47.15" in text
        assert xml.count("<m:oMath>") == 0
        assert (QA / "figures/severity_equation.png").is_file()
        assert (QA / "figures/risk_equation.png").is_file()
        for value in ("7360.68", "7160.35", "7574.93", "7555.60"):
            assert value in text
    results.append({"file": b["file"], "sha256": b["sha256"], "pages": len(pdf.pages),
                    "requirements_checked": requirements[i], "tables": len(d.tables),
                    "images": len(d.inline_shapes), "zip_valid": True,
                    "rendered_pdf_text_valid": True, "page_text_lengths": [len(x) for x in page_text]})
# A completed phase remains verifiable after separately authorized later phases.
assert not list((ROOT / "deliverables/phase2").rglob("*.mp4"))
assert not list((ROOT / "deliverables/phase2").rglob("*.pptx"))
(QA / "verification.json").write_text(json.dumps({"passed": True, "phase": 2, "outputs": results,
    "later_phase_artifacts_created": False, "visual_review_record": "docs/phase2/VISUAL_REVIEW.md"}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"passed": True, "outputs": [{"file": r["file"], "pages": r["pages"]} for r in results]}, ensure_ascii=False, indent=2))
