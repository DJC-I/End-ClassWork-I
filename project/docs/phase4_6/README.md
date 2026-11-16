# 第4.6阶段恢复与复现

最新可展示材料在 ../../deliverables/phase4_6；历史目录保留。完整设计见 ../PHASE4_6_DESIGN.md，验收见 ../PHASE4_6_ACCEPTANCE.md，逐页检查见 VISUAL_REVIEW.md。

源码：frontend/src/tokens.css、studio.css、design.ts及各页面组件。用户字体为frontend/public/fonts/user-pingfang.ttf，100%原TTF、400字重、约13MB；已有用户授权本项目直接使用，无第三方上传或字体改形。

网站常规启动仍为项目根 python scripts/start.py；离线已构建时加 --no-build。课堂隔离数据库与端口命令在新版演示操作清单。

本次测试服务8006使用.tools/phase4_6/preview.db；截图8007使用materials.db。复现脚本会重置这些演示库，不能指向原业务数据库。前端类型/构建：frontend目录npm run typecheck与npm run build；后端：.venv/Scripts/python.exe -m pytest；E2E：frontend目录npx playwright test --config playwright.phase46.config.ts；视觉：项目根node scripts/check_phase46.cjs round2。字体/全屏检查node scripts/check_phase46_font.cjs使用8007。

录制脚本scripts/record_phase46.cjs、assemble_phase46.py、verify_phase46_video.py、playback_phase46.cjs。录制画面来自Edge；剪辑使用FFmpeg，字幕64句，21镜头。音频源.tools/phase4_6/*_narration.wav逐字节等于第4.5阶段，禁止无故重新TTS。Python媒体脚本使用带Pillow的捆绑Python，并加载.tools/phase3/pydeps内PyAV。

截图scripts/capture_phase46_materials.cjs及capture_phase46_network.cjs使用独立8007库。文档scripts/update_phase46_documents.py做局部OOXML更新；scripts/finalize_phase46_slides.mjs检查PPT完整性、布局、原生表格、内嵌工作簿和重新导入。曾尝试artifact-tool往返导出，发现图表工作簿关系丢失，已改为保留原件包内结构的定点更新，最终验证通过。执行Node前设置RUNTIME_NODE_MODULES、RUNTIME_PYTHON为依赖加载器返回的捆绑绝对路径。完整材料入口为scripts/update_phase46_slides.mjs；随后用捆绑Python运行render_phase46.py docs、render_phase46.py slides。

final_checks_phase46.py复验基线40个文件、原配音、字体、布局、媒体、备注和页数。机器证据final-checks.json包含76项断言。所有交付物有SHA256SUMS.txt；它是本阶段校验清单，并非第五阶段打包。

第五阶段尚未执行。下一次需用户发送“继续第五阶段”。
