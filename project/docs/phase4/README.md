# 第四阶段恢复与复验

用户交付在 `deliverables/phase4`。12页PPT、8页讲稿、5页答辩、演示操作清单及验收报告；主讲1223字，逐页分配360秒，15问。

证据：`source-audit.json`来源/旧文件哈希与重算，`demo-check.json`独立库实际Edge操作，`pptx-validation.json`原生PPT结构和重新导入，`verification.json`最终86项断言，`VISUAL_REVIEW.md`逐页检查，`render/`实际PDF与PNG预览。

## 工具链

本机使用Codex托管runtime自带Python、python-docx、pypdf、pdf2image、Node、Playwright与 `@oai/artifact-tool`；字体Microsoft YaHei。隔离的官方LibreOfficePortable在 `.tools/libreoffice/App/libreoffice/program/soffice.exe`。未修改系统Office安装，也没有验证Microsoft Office GUI。

设置 `RUNTIME_NODE_MODULES` 为runtime的 `dependencies/node/node_modules`，`RUNTIME_PYTHON` 为该runtime的 `dependencies/python/python.exe`，并设置 `PYTHONUTF8=1`。依次运行：

```powershell
& $env:RUNTIME_PYTHON scripts/audit_phase4.py
& $env:RUNTIME_PYTHON scripts/prepare_phase4.py
& $env:RUNTIME_PYTHON scripts/build_phase4_docs.py
# Node运行scripts/build_phase4_slides.mjs，随后：
& $env:RUNTIME_PYTHON scripts/render_phase4.py slides
& $env:RUNTIME_PYTHON scripts/render_phase4.py docs
& $env:RUNTIME_PYTHON scripts/verify_phase4.py
```

PPT finalizer保护已有最终文件与回执；需要重建时先将这两项移至 `.tools/phase4/build/` 下新的版本备份位置，再生成。不得直接覆盖或删除唯一交付。三张来源截图字节与最终PPT嵌入图片一致，重新截图后须重新构建、渲染和验证，不能只替换证据图片。

浏览器复验前按演示操作清单启动8004，**SKYROUTE_DB仅指向 `.tools/phase4/demo.db`**，核心规则模式。`node scripts/check_phase4_demo.cjs --verify-only` 会恢复独立库的600元/12%，再改900元/20%验证保存；不会覆盖PPT所用截图。无此参数会重新截图，仅在计划重建时使用。

`audit_phase4.py`需第三阶段AV依赖 `.tools/phase3/pydeps` 以重新读MP4抽帧。新环境先按对应阶段说明准备依赖。不要为了文档复验在用户业务库执行浏览器重置。网站源码及前三阶段文件本阶段未改，未重跑全套网站测试。

第四阶段完成后停止；第五阶段最终复验和打包需用户另发继续指令。
