"""Build Phase 2 only. Run with the Codex bundled Python (python-docx/Pillow).

Read-only imports of canonical calculation modules; never opens the production DB.
Figures are crops of Phase 1 actual screenshots; no regenerated UI or values.
"""
from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.content import CONTENT
from backend.engine import analyze, simulate
from backend.growth import calculate, experiment
from backend.seed import EDGES, GROWTH_CONFIG, NODES, ORDERS, SCENARIOS, network

OUT = ROOT / "deliverables" / "phase2"
QA = ROOT / "docs" / "phase2"
ASSETS = QA / "figures"
for p in (OUT, QA, ASSETS):
    p.mkdir(parents=True, exist_ok=True)

WEIGHTS = {"cost": .25, "time": .35, "risk": .4}
GROWTH = calculate(deepcopy(GROWTH_CONFIG))
AB = experiment({"a_visitors": 200, "a_conversions": 30,
                 "b_visitors": 200, "b_conversions": 40})
RAIN = analyze(deepcopy(ORDERS[0]), SCENARIOS[1], WEIGHTS, network())
SIMS = [simulate(deepcopy(ORDERS), s, WEIGHTS, network()) for s in SCENARIOS]
OLD = json.loads((ROOT / "docs/scenario-results.json").read_text(encoding="utf-8"))
for new, old in zip(SIMS, OLD):
    assert new["before"] == old["before"] and new["after"] == old["after"]
assert RAIN["recommendation"]["id"] == "detour"
assert GROWTH["budget"] == 3000
suite = ET.parse(ROOT / "docs/pytest-results.xml").getroot().find("testsuite")
assert suite is not None and suite.get("tests") == "28" and suite.get("failures") == "0"
e2e = json.loads((ROOT / "docs/e2e-results.json").read_text(encoding="utf-8"))["stats"]
assert e2e["expected"] == 4 and e2e["unexpected"] == 0 and e2e["skipped"] == 0
assert json.loads((ROOT / "docs/restart-results.json").read_text())["passed"]


def crop(name, source, box):
    path = ROOT / "docs/screenshots" / source
    im = Image.open(path)
    assert 0 <= box[0] < box[2] <= im.width and 0 <= box[1] < box[3] <= im.height
    im.crop(box).save(ASSETS / name)


crop("growth_model.png", "growth-model.png", (285, 270, 1402, 1118))
crop("network_rain.png", "logistics-rain.png", (285, 943, 1402, 1705))
crop("plans_rain.png", "logistics-rain.png", (285, 1720, 1402, 2672))
crop("agent_rain.png", "logistics-rain.png", (285, 2690, 1402, 3245))


def set_font(style, size, bold=False):
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = False
    style.font.underline = False
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def make_doc(title, subtitle):
    d = Document()
    # The bundled default template carries a blue Title border and italic
    # subtitle. Remove inherited decoration explicitly, not just direct runs.
    for border in list(d.styles.element.xpath(".//w:pBdr")):
        border.getparent().remove(border)
    sec = d.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(.72), Inches(.68)
    sec.left_margin = sec.right_margin = Inches(.78)
    set_font(d.styles["Normal"], 11)
    d.styles["Normal"].paragraph_format.line_spacing = 1.25
    d.styles["Normal"].paragraph_format.space_after = Pt(7)
    for key, size in (("Title", 25), ("Subtitle", 14), ("Heading 1", 17), ("Heading 2", 12.5)):
        set_font(d.styles[key], size, key != "Subtitle")
        d.styles[key].paragraph_format.space_before = Pt(10)
        d.styles[key].paragraph_format.space_after = Pt(9)
    set_font(d.styles["Caption"], 9)
    d.styles["Caption"].paragraph_format.space_after = Pt(8)
    d.styles["Caption"].paragraph_format.line_spacing = 1.1
    d.core_properties.title = title
    d.core_properties.subject = "北京物资学院 人工智能导论课程结课作品 第二阶段"
    d.core_properties.author = ""
    d.core_properties.last_modified_by = ""
    d.core_properties.created = datetime(2026, 11, 16, tzinfo=timezone.utc)
    d.core_properties.modified = datetime(2026, 11, 16, tzinfo=timezone.utc)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)
    for _ in range(3):
        d.add_paragraph()
    d.add_paragraph(title, "Title")
    d.add_paragraph(subtitle, "Subtitle")
    d.add_paragraph("北京物资学院  人工智能导论", "Subtitle")
    d.add_paragraph("SkyRoute AI 天气智运与增长决策平台")
    d.add_paragraph("2026年11月16日")
    d.add_paragraph()
    return d


def p(d, text, style=None):
    return d.add_paragraph(text, style)


def page(d, title):
    heading = d.add_heading(title, 1)
    heading.paragraph_format.page_break_before = True


def h(d, title):
    d.add_heading(title, 2)


def table(d, headers, rows, widths):
    t = d.add_table(rows=1, cols=len(headers))
    t.autofit = False
    for col, width in zip(t.columns, widths):
        col.width = Inches(width)
    for cell, width, value in zip(t.rows[0].cells, widths, headers):
        cell.width = Inches(width)
        cell.text = str(value)
    for row in rows:
        for c, width, value in zip(t.add_row().cells, widths, row):
            c.width = Inches(width)
            c.text = str(value)
    for ri, row in enumerate(t.rows):
        props = row._tr.get_or_add_trPr()
        no_split = OxmlElement("w:cantSplit")
        props.append(no_split)
        if ri == 0:
            repeat = OxmlElement("w:tblHeader")
            props.append(repeat)
        for ci, c in enumerate(row.cells):
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = c._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for side in ("top", "left", "bottom", "right"):
                element = OxmlElement("w:" + side)
                for k, v in (("val", "single"), ("sz", "5"), ("color", "D9D9D9")):
                    element.set(qn("w:" + k), v)
                borders.append(element)
            cp.append(borders)
            margins = OxmlElement("w:tcMar")
            for side, value in (("top", "85"), ("bottom", "85"), ("left", "95"), ("right", "95")):
                element = OxmlElement("w:" + side)
                element.set(qn("w:w"), value)
                element.set(qn("w:type"), "dxa")
                margins.append(element)
            cp.append(margins)
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "20384F" if ri == 0 else ("F1F5F8" if ri % 2 == 0 else "FFFFFF"))
            cp.append(shade)
            for par in c.paragraphs:
                par.paragraph_format.line_spacing = 1.13
                par.paragraph_format.space_after = Pt(2)
                par.paragraph_format.space_before = Pt(2)
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == len(headers)-1 else WD_ALIGN_PARAGRAPH.CENTER
                for run in par.runs:
                    run.font.size = Pt(10)
                    run.font.bold = ri == 0
                    run.font.color.rgb = RGBColor.from_string("FFFFFF" if ri == 0 else "000000")
    d.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


def figure(d, filename, caption, width=6.7):
    par = d.add_paragraph()
    par.paragraph_format.space_after = Pt(4)
    par.paragraph_format.keep_with_next = True
    shape = par.add_run().add_picture(str(ASSETS / filename), width=Inches(width))
    shape._inline.docPr.set("descr", caption)
    p(d, caption, "Caption")


def equation(d, key):
    # Portable LO dropped OMML in the first render. Typeset genuine stacked
    # fractions at high resolution with the bundled Pillow and Windows math font.
    # These are formula images, deliberately not advertised as native equations.
    font_path = Path("C:/Windows/Fonts/cambria.ttc")
    main = ImageFont.truetype(str(font_path), 60)
    small = ImageFont.truetype(str(font_path), 49)
    lines = ([
        ["S = min(1.5, 0.35 × ", ("r", "60"), " + 0.35 × ", ("s", "20"),
         " + 0.15 × ", ("max(v − 8, 0)", "20")],
        ["       + 0.10 × ", ("max(5 − q, 0)", "5"),
         " + 0.05 × ", ("max(−T, 0)", "10"), ")"],
    ] if key == "severity" else [
        ["R = min(100, 5 + 65Ec + 20min(", ("d", "2"), ", 1) + 3(P − 1))"]
    ])
    def width(token):
        return max(small.getlength(x) for x in token) + 18 if isinstance(token, tuple) else main.getlength(token)
    canvas_width = int(max(sum(width(t) for t in line) for line in lines)) + 40
    im = Image.new("RGB", (canvas_width, len(lines) * 150 + 20), "white")
    draw = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        x, y = 20., 80 + i * 150
        for token in line:
            w = width(token)
            if isinstance(token, tuple):
                draw.text((x + w/2, y - 12), token[0], font=small, fill="black", anchor="mb")
                draw.line((x+4, y, x+w-4, y), fill="black", width=3)
                draw.text((x + w/2, y + 9), token[1], font=small, fill="black", anchor="mt")
            else:
                draw.text((x, y + 3), token, font=main, fill="black", anchor="lm")
            x += w
    target = ASSETS / (key + "_equation.png")
    im.save(target, dpi=(360, 360))
    par = d.add_paragraph()
    shape = par.add_run().add_picture(str(target), width=Inches(min(6.7, canvas_width/330)))
    shape._inline.docPr.set("descr", "天气严重度公式含雨雪风能见度温度" if key == "severity" else "货物时限与优先级的规则风险公式")
    par.paragraph_format.space_after = Pt(8)


def refs(d, kind):
    p(d, "[1] DataClawHub 官方赛事页及赛事规则，第一阶段核查日期2026年11月16日。完整网址见文末来源。", "Caption")
    if kind == "growth":
        p(d, "[2] 项目源码 backend/content.py、backend/seed.py、backend/growth.py；[3] docs/PHASE1_ACCEPTANCE.md 及运营截图。", "Caption")
    else:
        p(d, "[2] 项目源码 backend/seed.py、backend/engine.py、backend/main.py；[3] docs/scenario-results.json 与第一阶段测试和截图证据。", "Caption")


g = make_doc("DataClawHub平台运营方案", "赛题一  课程结课作品说明书")
p(g, "本方案以校园用户第一次完成可解释物流AI案例为切入点，将用户洞察、推广内容、渠道预算、转化漏斗和增长实验连接到同一个运营工作台。")
p(g, "已完成可交互工作台与确定性测算；访谈、推广、合作、经费和实际增长均待真实团队执行与验证。")
p(g, "团队信息说明  成员姓名与实际贡献由团队提交前填写。研发六角色记录不代表六名学生的贡献认定。", "Caption")
p(g, "阅读顺序  平台研究与摘要 → 用户画像 → 目标与策略 → 渠道与AI工具 → 执行排期 → 预算漏斗 → 增长验证 → 工作台证据 → 数据风险与结论", "Caption")

page(g, "1 项目摘要与平台研究")
p(g, "方案建议先验证校园新手的首次价值，再决定是否扩大投入。围绕“暴雨来临时，冷链订单怎样比较运输方案”这一具体问题，提供入门清单、可离线体验的案例与带计算依据的报告，帮助用户判断平台和赛事是否适合自己。")
p(g, "SkyRoute AI已实现四类画像、六项策略、漏斗与渠道预算测算、A/B计算、任务看板和报告。用户可以修改参数并保存，重新打开仍可读取。工作台提供方案推演和执行管理能力，尚未取得真实推广数据。")
h(g, "1.1 已观察的平台定位")
p(g, "第一阶段通过浏览器读取的官方赛事正文将DataClawHub描述为面向AI与物流产业的开源协作社区，连接任务、数据、工具与开发者。页面可见展品、Toolkits、知识库及竞赛入口。本方案围绕这些已观察入口提出内容和触达设计；入口可见并不等于其完整能力已验证。[1]")
h(g, "1.2 研究边界与验证顺序")
p(g, "当前缺少官方用户规模、活跃度、真实转化率和付费能力数据，也没有实际访谈记录。因此画像属于待验证的需求假设。先核实规则与平台操作，再拟议访谈8名同学，记录其需求、首次操作失败位置与放弃原因，用原始记录修订方案。")
p(g, "官方资源列表包含参赛工具包，但第一阶段检查时下载元素缺少有效链接，未取得包内指定网络。平台真实注册和激活统计也未获授权；无法得到数据时，只报告外链点击和本案例完成量，不能由此推算真实平台注册。")
h(g, "1.3 需求分析与核心卖点")
p(g, "学生需要把课程知识转为可展示作品，开发者需要可复现的业务问题，行业人员关注输入是否可信、结果能否解释。可传播的卖点是“用一个清楚的问题看到AI与物流的结合”，具体由本作品展示数据边界、方案比较和计算轨迹；不将本作品能力宣称为官方平台既有功能。")
p(g, "两题各占赛事成绩50%。赛题一按用户洞察20、策略完整性25、执行设计20、增长验证25、复盘表达10分设计内容。[1] 用户研究、可调模型与实验方法分别为这些维度提供可评审材料。")

page(g, "2 用户画像与需求验证")
for i, person in enumerate(CONTENT["personas"], 1):
    h(g, f"2.{i} {person['name']}")
    p(g, f"需求与动机：{person['need']}；{person['motivation']}。主要障碍：{person['barrier']}。")
    p(g, f"触达渠道：{person['channel']}。对应动作：{person['action']}。")
p(g, "画像验证采用同一提纲：最近一次AI实践任务是什么、在哪一步受阻、需要什么证据才愿意尝试、能否独立完成一次案例。按角色记录差异与反例，不用少量受访者替代整个平台人群，也不编造用户原话。", "Caption")

page(g, "3 运营目标与核心策略")
h(g, "3.1 目标口径")
p(g, "短期目标是确认需求与首次价值，形成可追溯的渠道和完成记录；3000元预算、12000次曝光以及各层转化率均为计划情景。核心观察指标建议为“有效访问后完成计算并查看报告的比例”。真实平台注册、平台激活与本案例激活必须分开记录。")
table(g, ["层次", "拟议指标", "判定要求"], [
    ("触达", "12000次曝光", "计划假设；渠道汇总次数，不能当独立用户数"),
    ("首次价值", "案例完成率", "同一匿名用户完成计算且查看报告；排除测试流量"),
    ("持续使用", "D7回访35%", "假设；第7天再次完成案例，同一标识跟踪"),
    ("推荐", "每激活用户0.2次", "假设；仅统计自愿推荐，去除自点与重复"),
], [1, 1.45, 4.49])
h(g, "3.2 拉新 激活 留存与推荐")
p(g, "拉新以冷链暴雨问题切入，内容末尾给出清楚的案例体验入口和官方赛事入口。先用一个问题筛选有兴趣的人，再邀请试用；不同渠道保留独立匿名来源码。")
p(g, "激活采用五步引导：核验官方规则、明确自己的需求、切换正常与暴雨、运行分析、查看并保存报告。第一次完成应能回答“为什么推荐此方案”，把等待、错误和疑问作为改进依据。")
p(g, "留存设计D1入门答疑、D3改变载重或时限的小任务、D7复盘分享。联系必须事先同意，官方未验证的提醒能力不作承诺。推荐玩法采用“同题不同解”：调整权重、解释取舍，再邀请同学复现。")
p(g, "资源策略先做不花钱的规则核实与访谈，预算计算通过后也不等于经费获批。内容策略以两篇案例文章和一份FAQ为起点，保留模拟标签和方法来源。以上分别对应网站中的六项运营策略。[2]")

page(g, "4 渠道规划与AI工具使用")
table(g, ["渠道", "内容与行动入口", "拟议衡量方式"], [
    ("校园社群", "课程实践清单和物流问题；邀请完成一次案例", "来源码访问与完成量；先获管理员同意"),
    ("内容平台", "问题短文和案例图；引导查看方法", "有效访问及制作耗时，不只统计点赞"),
    ("开发者社区", "图算法、输入样本、测试证据；邀请复现", "复现反馈与有效问题，遵守板块规则"),
    ("校园活动", "小型上手说明与现场尝试", "参加数、独立完成数与失败原因"),
    ("AI辅助内容", "标题、FAQ、图文草稿的制作支持", "制作时间及人工核验；避免与发布渠道重复计量"),
], [1.15, 2.8, 2.99])
h(g, "4.1 可直接执行的内容草案")
p(g, "校园帖题目为“用一个天气物流案例完成AI课程实践”；技术帖题目为“从有向图到可解释风险：一个离线物流原型”；行业帖题目为“预警不是封路：如何比较运输备选方案”。内容顺序为业务问题、案例输入、方案差异、模拟边界、体验行动。发布和联系由真实成员在获许可渠道执行。")
h(g, "4.2 AI工具与人工复核")
for item in CONTENT["ai_tools"]:
    p(g, f"{item['name']}：{item['use']} {item['boundary']}")
h(g, "4.3 创新玩法")
p(g, "走廊决策挑战让参与者在同一订单上使用不同权重，解释为何选择成本、时间或风险；方法卡片随结果保留输入、单位与局限；学生、开发者和行业人员可围绕同一问题提供不同反馈。共创及校企协作均属拟议，不宣称已有合作、官方证书、积分或学分奖励。")

page(g, "5 执行方案与时间排期")
p(g, "执行看板按角色分配任务，包含起止时间、状态、资源、预期成果和指标。角色可以由同一真实成员兼任，姓名和贡献由团队确认；软件中的演示状态不能作为真实业务完成凭证。")
table(g, ["时间", "角色与任务", "交付和检查"], [
    ("11月16至17日", "项目协调 核实人数与平台能力", "保存规则确认记录；未确认前不认定六人合规"),
    ("11月16至17日", "用户研究 拟议8次校园访谈", "经同意的匿名记录；梳理3类障碍，保留反例"),
    ("11月16至18日", "内容运营 两篇内容与FAQ", "AI草稿后人工核验；渠道授权和来源标注"),
    ("11月17至18日", "增长实验 小样本文案测试", "固定分组与结束规则；保留匿名原始计数"),
    ("11月18至19日", "质量验收 复盘与课堂检查", "核对报告、参数及操作入口；提交由用户处理"),
    ("11月24日后", "用户研究 D7回访复盘", "若17日招募，24日才到第7天；提交前无结果"),
], [1.1, 2.5, 3.34])
h(g, "5.1 一次小范围试验的操作顺序")
p(g, "先冻结实验假设、主要指标、分组规则和样本量；检查内容与渠道许可；用少量自愿参与者排查操作故障，再按预定规则运行。每天核对人数、事件定义、支出及失败反馈，结束时统一分析，保留继续、修改或停止的理由。")
p(g, "资源包括离线案例、内容草稿、访谈提纲、匿名计数表与场地。场地、社群、教师和校友渠道均需另行落实，不能把拟议资源写成已获得支持。费用由实际负责人批准后执行。")
h(g, "5.2 关键日期")
p(g, "第一阶段核查的官方页面列报名截止为2026年11月17日23时59分、视频提交截止为11月18日23时59分，页面未明确时区且赛程暂定，应由团队按正式通知核实；11月19日课堂展示来自课程任务书。第三阶段视频和第四阶段课件未在本阶段启动。[1]")

page(g, "6 预算与转化漏斗")
p(g, "默认预算总额为3000元，尚未获批或支出。CPM表示每千次预计覆盖的假设成本。AI内容制作也按等效CPM计入，便于课堂比较；实际投放需拆开制作成本与媒体费用，避免重复计算覆盖。")
table(g, ["渠道", "预算元", "CPM元", "预计覆盖次", "预计激活数"], [
    (c["name"], f"{c['budget']:.0f}", f"{c['cpm']:.0f}", f"{c['reach']:,.2f}", f"{c['active']:.2f}")
    for c in GROWTH["channels"]
], [1.65, .8, .85, 1.65, 1.99])
p(g, f"渠道预算模型合计覆盖{GROWTH['channel_reach']:,.2f}次、预计激活{GROWTH['channel_active']:.2f}、预计D7留存{GROWTH['channel_retained']:.2f}；每激活获客成本CAC为{GROWTH['cac']:.2f}元。不同渠道可能重叠，覆盖未去重，预测不代表实际用户。")
h(g, "6.1 独立曝光漏斗")
table(g, ["阶段", "逐层转化假设", "测算量"], [
    ("曝光", "独立输入", "12000"), ("访问", "12%", "1440"),
    ("注册", "28%", "403.20"), ("激活", "50%", "201.60"),
    ("7日留存", "35%", "70.56"),
], [1.5, 2.6, 2.84])
p(g, "各层数量等于上一层数量乘以本层转化率；小数是期望量，实际观察人数只能为整数。独立漏斗的12000次曝光与渠道模型的覆盖合计是两个独立情景，不能混用其分母或把两者强行拼接。")
h(g, "6.2 预算情景与决策")
p(g, "网站可把校园预算600元调为900元，同时将访问率12%调为20%，总预算变为3300元、独立漏斗访问量变为2400。若其他假设固定，预算对预计覆盖线性增长；现实中的边际单价、饱和和受众重复尚未建模，不能据此承诺线性增长。")

page(g, "7 增长实验与效果验证")
for i, ex in enumerate(CONTENT["experiments"], 1):
    h(g, f"7.{i} {ex['title'].split(' / ')[1]}")
    p(g, ex["hypothesis"] + ex["method"])
    p(g, "结束与异常处理：" + ex["stop"])
h(g, "7.4 计算器示例与判读")
p(g, f"假设A组200人中30人完成，B组200人中40人完成。完成率15%与20%，差异为+5个百分点，相对提升约33.33%。双侧两比例z检验p值为{AB['p_value']:.5f}，95%差值区间为[{AB['ci95_pp'][0]:.3f}, {AB['ci95_pp'][1]:.3f}]个百分点，跨过0，当前不能判定B胜出。")
p(g, f"计算器以每组成功和失败数均至少10作为正态近似检查；通过这一检查不代表样本足以检出目标差异。按A组基线15%、最小差异5个百分点、双侧显著性水平5%与80%功效，近似估算每组需{AB['sample_per_arm']}人；400人的示例仍可能功效不足。")
p(g, "实际试验还需独立随机分组、同一人只计一次、固定主要指标及分析时点。48小时截止时若未达到预定样本，只报告探索结果；不按中途显著性提前结束，不把不同渠道流量直接当随机实验。多实验比较的校正尚未实现，正式分析应另行设计。")

page(g, "8 工作台功能与实际界面")
figure(g, "growth_model.png", "图1 第一阶段实际运营工作台截图裁切  校园预算900元 访问率20% 总预算3300元", width=6.6)
p(g, "此图展示真实表单、预算与图表结果，属于参数调整后的情景。默认3000元预算的重算数值见第6节，不能将截图视为默认值或真实投放结果。")
h(g, "8.1 可复现的操作")
p(g, "进入/growth后查看四类画像与策略，切到增长测算，修改预算与转化率并保存，刷新确认保持；输入A/B计数，读取区间与样本提示；在执行看板修改任务状态，再生成运营报告并下载或打印。")
p(g, "上述路径在第一阶段真实Edge测试中通过，报告保存当次参数和任务快照。运营内容、计算与持久化由后端提供；文档数值另从默认种子与同一计算函数重算。[2][3]")

page(g, "9 数据假设 风险复盘与结论")
h(g, "9.1 数据与口径")
p(g, "平台定位、导航和规则来自第一阶段的官方页面观察记录；用户需求来自待验证的角色假设；曝光、单价、转化率、预算和实验计数均为计划输入。未开展实际访谈、渠道投放、平台注册统计或D7观察。网页任务CRUD属于工程功能，不证明真实运营任务已经执行。")
table(g, ["风险", "应对及复盘动作"], [
    ("平台能力或资格不明", "先核实平台流程及3至5人规则与界面容量冲突，保存人工结论"),
    ("小样本与重复流量", "保留匿名计数、固定分析时点、报告区间；不夸大差异"),
    ("预算与CPM偏差", "先核实经费；小额试验校准单价、去重及边际成本后再扩量"),
    ("隐私 授权与AI失真", "联系须同意；不输入个人或客户隐私；人工核对内容与承诺"),
    ("提交前无法观察D7", "明确未完成，按17日招募则24日后复盘，不补写虚假结果"),
], [1.8, 5.14])
h(g, "9.2 复盘机制与结论")
p(g, "每日用15分钟检查漏斗定义、花费和失败反馈；实验结束时核对分组、样本、区间和业务收益；11月19日复盘工程与执行准备，D7另排后续。CAC超过团队事先确定的阈值或证据不足时，先修改人群、内容或首次体验。结论写明继续、修改、停止及理由，不追求必然增长。")
p(g, "本方案把校园首次价值、渠道资源、预算模型和增长验证连接成可操作流程，网站已完成交互与持久化验收。下一步应由真实团队落实资格、授权与访谈，再以实际计数替换假设，判断平台触达是否有效。")
h(g, "9.3 来源与对应材料")
refs(g, "growth")
p(g, "官方赛事网址 https://dataclawhub.com/competitions/80dc6014-49d7-43a0-b2cc-4b1670481efc", "Caption")
p(g, "课程Word要求与11月19日课堂安排来自用户任务书 docs/ORIGINAL_REQUEST.txt；官方能力边界见 docs/OFFICIAL_REVIEW.md 与 docs/SOURCES.md。", "Caption")


l = make_doc("气象驱动物流运输风险预警与应对决策", "赛题二  课程结课作品说明书")
p(l, "本作品在北京至天津教学运输走廊中，以天气时间窗、货物属性和承诺时限识别订单风险，计算四类备选方案，并保留决策输入、算法结果和工具轨迹。")
p(l, "规则模式可离线完成分析和仿真。当前路网、天气和成本均为教学模拟；模型结果用于课程演示与方法验证。")
p(l, "团队信息说明  成员姓名与实际贡献由团队提交前填写。研发角色不等同真实学生贡献。", "Caption")
p(l, "阅读顺序  摘要需求 → 架构 → 数据网络 → 天气订单 → 风险模型 → 优化算法 → 智能体 → 页面截图 → 演示测试 → 仿真 → 局限与结论", "Caption")

page(l, "1 项目摘要 问题背景与需求")
p(l, "天气预警只描述天气风险，调度还需判断哪些区段与订单在有效时段内受影响，以及提前、绕行或换中转是否值得。原型把这些问题连接为可解释的计算流程，供课程展示和方案比较。")
p(l, "系统已实现订单管理、有向网络、三天气场景、风险总览、四策略比较、六步分析轨迹、配对仿真与报告。默认暴雨案例SR-001推荐绕行BJ至LF至TJ，运输2.95小时、成本1242元、规则风险11分；结论来自实际算法，不预先指定赢家。")
table(l, ["需求", "当前实现与验收入口"], [
    ("读取预报 预警与计划", "加载normal/rain/snow固定天气与6条订单，字段含有效期与货物属性"),
    ("识别影响区段 节点与订单", "逐段天气暴露与节点损失；风险总览可选择订单"),
    ("比较多种应对", "原计划、提前2小时、绕行、新中转；不适用保留原因"),
    ("计算时间 成本与剩余风险", "确定性公式和可调权重；支持查看依据与完整输入输出"),
    ("模拟验证并展示指标", "同一订单与压力情景配对比较准时占比、延误、成本与风险"),
    ("可用性与可追溯", "本地一键启动、SQLite快照、无密钥规则模式、下载与打印"),
], [2.1, 4.84])
h(l, "1.1 验收范围")
p(l, "第一阶段16项本地网站验收已通过，后端28项测试与真实Edge的4条流程均有机器证据。网络符合官方工具包、真实气象接入、真实大模型联通与生产调度效果尚未验收，不以本地测试替代这些结论。[3]")
p(l, "赛题二六项评分20/30/20/15/10/5分分别对应问题理解、可运行闭环、规则与工具流程、可复现比较、接入边界和展示证据。两赛题各占50%。[1]")

page(l, "2 系统架构与技术栈")
table(l, ["层次", "技术与职责"], [
    ("浏览器", "React 19、TypeScript、Vite；Recharts、Lucide和CSS变量实现图表、拓扑与表单"),
    ("服务层", "Python 3.12、FastAPI、Pydantic；REST、输入校验、错误响应与静态资源托管"),
    ("计算层", "engine.py图枚举、天气时间窗、风险与成本、归一化评分和配对仿真"),
    ("数据层", "SQLite标准库；订单、运营任务、配置、场景选择和报告快照持久化"),
    ("可选解释层", "后端OpenAI兼容接口；解释已存快照，失败则返回规则依据"),
], [1.35, 5.59])
h(l, "2.1 请求如何流动")
p(l, "浏览器提交订单编号、场景和权重；FastAPI读取SQLite订单与版本化场景，调用规则引擎；引擎检查有向连接与单票运力，生成方案并评分；服务保存输入输出快照，返回可视化结果。报告按运行编号读取，后续修改订单不会改写既有报告。")
p(l, "开发模式由Vite代理/api，生产模式由FastAPI同源托管构建文件，仅监听127.0.0.1:8000。选择SQLite和单体服务是为了零配置本地演示，核心链路无需云账号、地图服务或模型API。")
h(l, "2.2 接口与异常处理")
table(l, ["接口", "作用"], [
    ("GET /api/bootstrap", "读取网络、场景、订单、任务和参数"),
    ("POST /api/analysis", "逐单分析、四方案、推荐与工具轨迹"),
    ("GET /api/risk/overview", "当前场景下逐单风险、影响与汇总"),
    ("POST /api/simulation", "批量配对仿真与逐单结果"),
    ("GET /api/reports/{id}", "读取不可随当前参数漂移的报告快照"),
    ("POST /api/agent/explain", "按报告编号生成规则或可选模型解释"),
], [2.85, 4.09])
p(l, "订单CRUD、事务JSON导入与CSV导出另有独立接口。统一错误包含code与message，校验失败422、记录不存在404、业务冲突409，内部错误500，算法未就绪503；具体结构以docs/openapi.json和运行时/docs为准。")

page(l, "3 数据来源与运输网络")
p(l, "数据版本为skyroute-synthetic-v1。7个节点是北京BJ、通州TZ、廊坊LF、武清WQ、蓟州JZ、宝坻BD、天津TJ；坐标仅为地理近似。连接、里程、正常时长、费用及运力全部由backend/seed.py明确给出，是教学假设。")
table(l, ["有向边", "km", "基准h", "通行费元", "单票上限t"], [
    (f"{e['source']}→{e['target']}", e["km"], f"{e['hours']:.2f}", e["toll"], e["capacity"])
    for e in EDGES
], [1.65, 1, 1.2, 1.5, 1.59])
p(l, "节点单票上限依次为BJ30、TZ25、LF22、WQ25、JZ12、BD18、TJ30吨。可行路线必须逐边存在、available为真且订单重量不超过经过节点和边的上限；图中没有反向边时不能反向行驶。")
h(l, "3.1 道路与资源的真实性边界")
p(l, "地图几何只表达有向拓扑，不证明真实公路连接，展示线长也不参与里程计算。天气预警不自动改变available字段。官方工具包未取得，不能声称这些节点与道路遵循官方指定网络；取得资源后应核对连接、时间与费用并重新运行验收。[1][2]")
p(l, "本模型验证单票是否超限，没有同时分配车辆、车次、共享仓容或累计节点容量；多个订单各自可行不代表整批资源可同时执行。")

page(l, "4 天气场景与运输订单")
table(l, ["要素", "正常", "暴雨", "暴雪大风"], [
    ("雨 mm/3h", 0, 55, 0), ("雪 mm/3h", 0, 0, 18),
    ("风 m/s", 3, 12, 22), ("能见度 km", 15, 1.8, .6),
    ("温度 ℃", 12, 8, -7), ("有效时间", "10至18时", "10至18时", "8至20时"),
], [2.1, 1.5, 1.5, 1.84])
p(l, "天气日期均为2026年11月16日、时区+08:00；降雪量为液态当量。暴雨影响主走廊与武清、通州节点；暴雪大风影响主走廊、北侧路线及多个节点。影响系数取自种子映射表，没有实况或历史预报含义。")
table(l, ["订单", "货物与吨数", "原路线", "发运至截止", "基准元"], [
    ("SR-001", "冷链8", "BJ TZ WQ TJ", "10:00至13:35", 1180),
    ("SR-002", "普通12", "BJ TZ WQ TJ", "11:00至16:00", 1250),
    ("SR-003", "易碎5", "TZ WQ TJ", "10:30至13:00", 880),
    ("SR-004", "普通18", "BJ LF TJ", "12:00至18:00", 1380),
    ("SR-005", "冷链10", "BJ TZ WQ TJ", "09:30至12:30", 1320),
    ("SR-006", "易碎4", "LF WQ TJ", "11:30至14:00", 730),
], [1.05, 1.05, 1.7, 2.14, 1])
p(l, "6条订单的优先级依次为3、2、3、1、3、2。SR-005为运输中，其余待发运。输入还含唯一编号、起终点、承诺时间、base_hours与状态；计算时长按边累计，base_hours作为原计划基准记录。已送达订单不作为待调度对象。")
h(l, "4.1 数据输入与校验")
p(l, "支持新增、编辑、查询、筛选和删除，检查正重量、费用、时区、发运与承诺时间顺序、路线端点、连续性和运力。导入为1至200条完整订单的JSON数组，任意记录错误整批回滚；CSV用于导出查看，不作为当前导入格式。")

page(l, "5 天气暴露与风险模型")
p(l, "规则模型先计算天气严重度，再依据运输基准通行窗与预警有效期的重叠计算每段暴露，逐段累计天气延时和到达时间。所有系数为教学假设，未以事故或运输样本校准。[2]")
h(l, "5.1 天气严重度与时间窗")
equation(l, "severity")
p(l, "r、s为雨雪mm/3h，v为风速m/s，q为能见度km，T为温度℃。每段暴露等于S乘区段影响系数和基准通行窗重叠比例。比例为交集时长除基准段时长，限制在0至1。节点窗为基准到节点后的0.25小时。")
p(l, "每段额外时长为基准段时长乘2.2乘段暴露，再加0.25小时乘S、目的节点系数及节点窗重叠比例。下一段起始时间包含上一段实际累计延时。用基准窗而非未知的延时后通行窗计算本段暴露，避免隐式循环；不等同真实交通传播模型。")
h(l, "5.2 货物 时限与风险等级")
equation(l, "risk")
p(l, "E为按基准时长加权的区段天气暴露，c为货物敏感度，普通1、冷链1.25、易碎1.15；d为超过承诺到货时间的延误小时，P为优先级1至3。低风险小于25，中风险25至不足50，高风险不低于50。R是规则风险指数，不是事故概率。")
h(l, "5.3 SR001暴雨手算对应")
p(l, "默认SR-001天气严重度为0.414833。原路线BJ至TZ至WQ至TJ，正常2.6小时；天气增加约1.9667小时，到达14时34分，超过13时35分约0.9834小时，风险47.15分。影响区段是BJ-TZ、TZ-WQ、WQ-TJ，节点影响含TZ与WQ。")
p(l, "界面总览的风险与延误来自逐单计算，选中订单后可查看区段依据。预警表示速度损失与暴露提高，不能自动推导封路、停运或真实损失。")

page(l, "6 多方案生成与优化算法")
p(l, "算法以深度优先遍历枚举容量约束下的简单有向路径，禁止重复节点。适用于当前7节点的小图，路径数在大图可能快速增长，当前未实现大规模车队优化。")
table(l, ["策略", "生成规则与条件"], [
    ("原计划", "按原路线与发运时间计算；输入必须可达且不过载"),
    ("提前发运", "待发运订单在原路线提前2小时；假设货物、司机和装卸可提前就绪"),
    ("绕行", "候选路径与原路线不共享有向边，在该类候选中按权重选择"),
    ("调整中转", "新增不同中间节点，且不与原路线和已选绕行重复；该类内部择优"),
], [1.2, 5.74])
h(l, "6.1 时间与成本")
p(l, "总时长为各边基准时长、天气额外时长之和，调整中转另加0.4小时。成本先将原成本扣除原通行费，按原里程折为单位里程运行成本，再乘新里程，加新通行费、策略费和天气成本。")
p(l, "策略费：原计划0，提前为100元加每吨12元，绕行65元，中转为90元加每吨8元。天气成本为天气额外小时乘65元/小时，冷链再增加25元/小时。额外成本以订单原基准成本为参照，和“相对受天气影响的原方案节省额”不同。")
h(l, "6.2 评分与推荐")
p(l, "成本、总运输时长、风险分别在当前可行候选内做min-max归一化；同一指标全相等则该项为0。权重按总和归一化后求加权和，越小越优。默认成本0.25、时长0.35、风险0.40；同分依次按成本、时长和策略ID稳定排序。")
p(l, "先分别选绕行和中转类内最优路线，再对四类代表评分。评分依赖候选集合，存在相对排序变化；它不是全图所有策略联合优化的保证，也不把延误单独设为硬约束或评分维度。权重变化可能改变赢家。")
p(l, "运输中无法回溯提前发运；缺少当前位置时其余方案只作原始计划级反事实比较。无可行替代时保留不适用原因，不能填造路线和数值。")

page(l, "7 AI智能体设计与可追溯性")
table(l, ["工具步骤", "输入", "输出"], [
    ("读取运输任务", "订单编号", "完整订单快照"),
    ("读取天气与网络", "场景编号与图版本", "天气要素 节点数 边数"),
    ("识别区段风险", "严重度分项 货物 时限", "逐段暴露和原计划风险"),
    ("枚举可达路线", "起终点与重量", "满足连接和单票运力的路径"),
    ("生成并评分方案", "策略与决策权重", "四类候选及指标"),
    ("输出决策建议", "归一化评分规则", "推荐策略与可解释理由"),
], [1.6, 2.4, 2.94])
p(l, "这是有固定工具顺序、输入输出和报告快照的规则分析智能体。数值由Python计算，界面可展开每一步，不依赖自由生成文本来决定成本或路径。")
h(l, "7.1 可选大模型与降级")
p(l, "OPENAI_API_KEY、OPENAI_BASE_URL和OPENAI_MODEL仅由后端环境读取。解释接口向兼容的chat/completions提交用户问题与算法快照，要求只解释既有结果、不编造数字或封路信息。无密钥返回规则模式；超时、错误或空响应返回规则降级，25秒超时不阻断已完成分析。")
p(l, "第一阶段只验证了mock兼容请求与异常回退，没有真实供应商调用。自然语言解释仍可能失真，应以结构化方案表为准。模型输入来自订单快照，未来接入真实业务还需评估数据授权与脱敏。")
figure(l, "agent_rain.png", "图1 实际智能体页面裁切  六步工具轨迹与规则解释  第一阶段Edge截图", width=6.55)

page(l, "8 关键页面截图与网络输入")
figure(l, "network_rain.png", "图2 实际物流页面裁切  暴雨网络与天气  SR001冷链8吨 默认权重", width=6.7)
p(l, "图中绿色线路为本次推荐的BJ至LF至TJ，橙色线标示天气影响，灰线为模拟可用连接。节点位置和连线仅为拓扑示意，里程来自种子配置。右侧记录暴雨55mm/3h、风速12m/s、能见度1.8km及订单承诺时间。")
h(l, "8.1 风险总览与数据对应")
p(l, "当前场景6单，其中4单规则风险达到25，0单达到50，5单受天气影响。页面平均预计原计划延误约0.58小时为名义场景的逐单汇总；第11节压力仿真使用三种扰动，口径不同，不能把看板均值当作仿真全部样本结果。")
h(l, "8.2 输入与结果的关联")
p(l, "选择订单后运行风险分析，页面将读取其原路线和截止时间。调整权重后重新运行，推荐和路线一起变化；报告保留当次天气、权重、四方案与解释依据。输入错误由后端返回明确提示，不能只改变界面数字。")
p(l, "本节及下节图片均为第一阶段实际应用截图的裁切，只去除无关页面区域，没有重绘UI或修改结果。原始文件为docs/screenshots/logistics-rain.png。", "Caption")

page(l, "9 关键页面截图与方案比较")
figure(l, "plans_rain.png", "图3 实际风险与四方案页面裁切  原计划风险47.15 推荐绕行风险11", width=6.55)
table(l, ["方案", "时长h", "成本元", "延误h", "风险"], [
    (plan["name"], f"{plan['hours']:.4f}", f"{plan['cost']:.2f}", f"{plan['delay_hours']:.4f}", f"{plan['risk']:.2f}")
    for plan in RAIN["plans"]
], [1.75, 1.15, 1.45, 1.35, 1.24])
p(l, "绕行总成本相对1180元无天气基准增加62元，但比暴雨原计划1357.01元节省115.01元；运输时长减少约1.6167小时，消除名义场景延误。提前发运仍可行，但其费用和风险使其在默认权重下未胜出。", "Caption")

page(l, "10 功能演示与测试结果")
h(l, "10.1 可复现的本地操作")
p(l, "在项目目录运行python scripts/start.py；已有依赖和生产构建可用--no-build。浏览器访问127.0.0.1:8000，从首页进入物流模块，选择暴雨和SR-001，保持默认权重并运行风险分析。查看影响区段、四方案、推荐与六步工具记录，再打开决策报告下载或打印。")
p(l, "切换正常、暴雨、暴雪大风分别运行仿真，比较原计划和优化；选SR-005检查提前方案不适用。订单管理可新增、编辑、筛选、导入JSON和导出CSV。需要恢复固定种子时才使用课堂演示重置，重置会清除本项目自建业务数据和报告，应先保存所需内容。")
h(l, "10.2 第一阶段实际验收证据")
table(l, ["检查", "已记录结果与范围"], [
    ("后端测试", "28通过 0失败；API、事务回滚、公式、可达性、运力、时窗、权重与报告"),
    ("真实Edge流程", "4通过 0失败 0跳过；双题主链、订单、切天气、报告、手机宽度与重置"),
    ("类型与生产构建", "TypeScript与Vite通过；依赖检查无冲突"),
    ("重启持久化", "真实进程停止再启动；同一隔离SQLite的任务、预算和报告保持"),
    ("模型接口", "mock请求和失败回退通过；真实供应商连通及解释质量未验证"),
    ("实际页面检查", "桌面1440×1000、手机390×844；全屏进入退出及页面图表检查"),
], [1.4, 5.54])
p(l, "第一阶段证据为docs/pytest-results.xml、e2e-results.json、restart-results.json及PHASE1_ACCEPTANCE.md。本阶段从相同函数重算全部文档引用场景指标，并与已保存结果逐项比较；没有把历史测试描述成重新执行全部网站测试。")
p(l, "浏览器范围仅为本机Windows Edge；没有覆盖Safari、Firefox或全部设备。打印入口调用标准浏览器打印，未向物理打印机输出。运行成功不代表生产安全或真实调度效果已验收。")

page(l, "11 配对仿真与模拟结果分析")
p(l, "对6单先在名义天气下选择策略，随后固定路线、发运时刻和策略，在天气严重度0.85、1、1.15倍下配对回放；每侧18个样本，扰动时不重新选择最优方案。种子标识skyroute-v1-fixed-stress-085-100-115，方法可复现。[2][3]")
table(l, ["场景", "准时占比%", "均延误h", "总成本元", "高风险单"], [
    (s["scenario"]["name"], f"{s['before']['on_time_rate']:.2f}→{s['after']['on_time_rate']:.2f}",
     f"{s['before']['average_delay']:.4f}→{s['after']['average_delay']:.4f}",
     f"{s['before']['total_cost']:.2f}→{s['after']['total_cost']:.2f}",
     f"{s['before']['high_risk']}→{s['after']['high_risk']}") for s in SIMS
], [1.2, 1.45, 1.55, 1.85, .89])
p(l, "箭头为原计划至优化。准时占比和平均延误按18个样本统计；总成本是3个压力情景中6单总成本的均值；高风险为名义天气风险不低于50的订单数，非18样本计数。额外成本均以6单原基准总成本6740元为参照。")
table(l, ["场景", "原额外成本元", "优化额外成本元", "相对受天气原计划节省元"], [
    (s["scenario"]["name"], f"{s['before']['extra_cost']:.2f}", f"{s['after']['extra_cost']:.2f}", f"{s['before']['total_cost']-s['after']['total_cost']:.2f}") for s in SIMS
], [1.3, 1.65, 1.65, 2.34])
h(l, "11.1 结果含义与取舍")
p(l, "正常天气准时占比保持100%，优化成本增加68元，说明默认权重愿意支付部分费用换取更短运输时长。暴雨准时占比提高61.11个百分点，总成本减少200.33元；暴雪大风提高44.45个百分点，仍有延误，不能宣称风险全部消失。")
p(l, "这些结果只证明本模型能按输入改变方案、并在固定压力情景中比较取舍。样本是同一批合成订单的重复扰动，不是独立历史运输记录；不作统计显著性或真实收益推断。没有额外假设改用过去已知最优，也没有隐藏正常天气成本上升。")

page(l, "12 局限性 未来优化与结论")
h(l, "12.1 当前局限性")
p(l, "路网、费用、运力与天气全部模拟，官方工具包符合性待核；规则权重和风险分未校准，时间窗计算简化了交通与装卸传播。没有实时位置、车队共享容量、司机工时、班次和道路管制数据。运输中订单的替代方案是原始计划级反事实，不能直接派车执行。")
p(l, "候选枚举面向小图，先类内选代表再跨类评分不保证全局最优。风险分不是概率，准时指标不是预测置信度；模拟改善不能作为真实业务承诺。外部模型解释仅mock验证，文本不能替代结构化计算证据。")
h(l, "12.2 按依赖顺序优化")
table(l, ["方向", "实施与验收要求"], [
    ("官方网络与真实来源", "取得指定工具包；逐边对照连接、里程和时间，保留来源版本后重跑"),
    ("气象与道路接入", "记录发布时刻、有效期和授权；道路可用性独立于预警，测试过期与缺失"),
    ("真实业务校准", "脱敏历史订单回放；分离训练和验证，比较时长误差、延误与成本偏差"),
    ("资源与运输中决策", "接入当前位置、司机工时及共享运力，约束剩余路线并作联合调度"),
    ("大图与解释评估", "引入受约束路径搜索；真实模型连通后核验数字忠实度与异常降级"),
], [1.8, 5.14])
h(l, "12.3 结论")
p(l, "原型已把天气读取、订单影响识别、可解释风险、四方案比较、配对仿真与报告连接成可运行闭环，无模型密钥仍可演示。课程价值在于让输入、规则和取舍可检查；后续是否具备生产价值，应由真实数据、共享资源约束和业务回放验证。")
h(l, "12.4 来源与对应材料")
refs(l, "logistics")
p(l, "官方赛事网址 https://dataclawhub.com/competitions/80dc6014-49d7-43a0-b2cc-4b1670481efc", "Caption")
p(l, "字段与接口详见docs/API_AND_DATA.md、docs/openapi.json；规则核查见docs/OFFICIAL_REVIEW.md。课程要求来自docs/ORIGINAL_REQUEST.txt。", "Caption")


FILES = [(g, "DataClawHub平台运营方案.docx"),
         (l, "气象驱动物流运输风险预警与应对决策.docx")]
manifest = {"phase": 2, "date": "2026-11-16", "outputs": [],
            "calculation_checks": {"growth": GROWTH, "ab": AB,
                "rain_plans": RAIN["plans"],
                "simulation": [{"scenario": s["scenario"]["id"], "before": s["before"], "after": s["after"]} for s in SIMS]},
            "prior_evidence": {"pytest_passed": 28, "e2e_passed": 4, "restart_passed": True},
            "phase3_started": False}
for d, name in FILES:
    path = OUT / name
    d.save(path)
    with ZipFile(path) as z:
        assert z.testzip() is None
        xml = ET.fromstring(z.read("word/document.xml"))
        assert xml.tag.endswith("document")
    text = "\n".join(par.text for par in d.paragraphs)
    assert "结论" in text and "假设" in text
    manifest["outputs"].append({"file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size,
        "tables": len(d.tables), "images": len(d.inline_shapes),
        "paragraphs": len(d.paragraphs), "expected_pages": 10 if d is g else 13})
(QA / "build_checks.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "manifest.txt").write_text("\n".join(name for _, name in FILES) + "\n", encoding="utf-8")
(OUT / "SHA256SUMS.txt").write_text("\n".join(
    e["sha256"] + "  " + Path(e["file"]).name for e in manifest["outputs"]
) + "\n", encoding="utf-8")
print(json.dumps({"outputs": manifest["outputs"], "ab": AB, "growth": {k:GROWTH[k] for k in ("budget", "channel_reach", "channel_active", "cac")}}, ensure_ascii=False, indent=2))
