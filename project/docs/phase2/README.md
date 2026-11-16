# 第二阶段文档构建与检查

本目录保存两份Word的构建依据、实际截图裁切、渲染和验收证据。最终可提交文件在`deliverables/phase2`。只执行第二阶段，没有制作第三阶段视频或第四阶段课件。

## 原始依据

- 要求：`docs/ORIGINAL_REQUEST.txt`第二阶段。
- 第一阶段状态与16项验收：`PROJECT_STATUS.md`、`TASKS.md`、`docs/PHASE1_ACCEPTANCE.md`。
- 平台研究：`docs/OFFICIAL_REVIEW.md`、`docs/SOURCES.md`，核查日期2026-11-16；文档没有声称重新核查全部官方页面。
- 计算源：`backend/seed.py`、`content.py`、`growth.py`、`engine.py`。构建脚本只读导入，不打开或重置生产SQLite。
- 网站测试：第一阶段28项pytest、4条Edge流程及真实进程重启记录。本阶段读取原始机器证据，不将其称为重新跑过全部网站测试。

## 构建

通过Codex工作区依赖查询使用随应用提供的Python及python-docx、Pillow、pypdf、pdf2image。不要用系统Python替代文档依赖环境。

```powershell
$artifactPython = 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
& $artifactPython scripts\build_phase2_docs.py
```

重新构建后必须重新渲染、检查全部页面、运行验证，新的文件哈希不可沿用旧记录。

## 渲染

当前Windows工作区依赖包未附LibreOffice。没有调用用户桌面安装；使用从Document Foundation官方归档获取的独立Portable运行时，仅处理本项目生成的文件，解压于被Git忽略的`.tools/libreoffice`，不注册系统组件。

归档地址：`https://downloadarchive.documentfoundation.org/libreoffice/old/25.2.7.2/portable/LibreOfficePortablePrevious_25.2.7_MultilingualStandard.paf.exe`

官方SHA256：`b6d087e03d21080f91549dc75760e97c57a7268c07a06112ab255a5b66a4dfc8`。

使用文档技能自带`render_docx.py`，传入绝对路径的独立soffice，不搜索或退回桌面LibreOffice。Poppler来自工作区依赖包。实际运行路径与页数记录在`render_checks.json`。

```powershell
& $artifactPython scripts\render_phase2_docs.py --renderer './.codex\plugins\cache\openai-primary-runtime\documents\26.1112.11217\skills\documents\render_docx.py' --soffice '<独立Portable目录中的soffice.exe绝对路径>'
& $artifactPython scripts\verify_phase2_docs.py
```

`render/operations`、`render/logistics`中的PNG与PDF仅用于排版检查，不替代最终DOCX。逐页视觉记录见`VISUAL_REVIEW.md`。

## 截图来源

仅使用第一阶段真实浏览器截图，按原始像素裁切，不改写UI或数字。坐标由构建脚本固定，左上为原点：

|文档插图|原始文件|裁切坐标 左 上 右 下|
|---|---|---|
|运营测算|docs/screenshots/growth-model.png|285 270 1402 1118|
|物流网络|docs/screenshots/logistics-rain.png|285 943 1402 1705|
|风险与方案|docs/screenshots/logistics-rain.png|285 1720 1402 2672|
|智能体工具|docs/screenshots/logistics-rain.png|285 2690 1402 3245|

运营截图是预算3300元、访问率20%的交互情景；文档默认预算为3000元，两者分别说明。物流图为SR-001、暴雨、默认权重，不把提前策略预设为赢家。

## 自动检查范围

构建时重算漏斗、渠道、A/B、四方案和三场景仿真，逐项对照第一阶段场景结果。最终验证检查DOCX包结构、章节、截图与公式图数量、数字、黑色标题、哈希、实际渲染页数、非空页面及后续阶段产物缺席。视觉检查补充判断字形、表格边界、分页和截图可读性，不能用文字抽取替代。

首轮原生OMML公式在此Portable渲染器中显示为空，因此最终用工作区Pillow配合Windows Cambria字体排版两张高分辨率公式图，分子分母、分数线和运算符均完整。它们是图片，不宣称为原生可编辑数学对象；参数定义与模型说明仍是可编辑正文。完整公式也保留在计算源码和网站依据中。
