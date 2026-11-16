from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4_6';O=R/'deliverables/phase4_6'
report=(R/'docs/PHASE4_6_ACCEPTANCE.md').read_text(encoding='utf-8')
(O/'第4.6阶段验收报告.md').write_text(report,encoding='utf-8')
v=json.loads((Q/'verification.json').read_text(encoding='utf-8'))
lines=['# 第4.6阶段视频检验报告','','两条视频为真实Edge操作重录，使用新版网站。晓晓女声WAV逐字节沿用第4.5阶段，无重新TTS。','', '|文件|时长|分辨率|帧数|大小|字幕|','|---|---:|---|---:|---:|---:|']
for x in v['outputs']:
 lines.append(f"|{Path(x['file']).name}|{x['duration']:.3f}秒|{x['width']}×{x['height']}|{x['decoded_video_frames']}|{x['bytes']:,}字节|{x['srt_sentences']}句|")
lowest=min(a['correlation'] for x in v['outputs'] for a in x['audio_alignment_checks'])
lines+=['','H.264 25fps、yuv420p；AAC 48kHz双声道。两个成片视频/音频完整解码通过，FFmpeg整文件解码无错误，字幕逐句与解说时间轴一致。21个章节配音抽样最佳偏移均0毫秒，最低相关系数'+str(lowest)+'。','', 'Edge经本地HTTP Range实际播放片头、中间、结尾并触发ended，视频帧增长正常。21个章节中点的成片截图已目视复核，真实计算/规则模式/教学模拟说明保留。图表数值与原后端一致，没有假页面或假功能。','', '解说稿、分镜和SRT就在本目录。哈希见SHA256SUMS.txt；完整机器结果docs/phase4_6/verification.json、playback.json、各recording/assembly.json；成片联系图docs/phase4_6/growth-contact.jpg、logistics-contact.jpg。','', '配音仍是神经网络合成女声，不冒充真人或人工逐字听审；未在教室音响设备测试。视频各170/175秒，均小于180秒。未执行第五阶段打包。']
(O/'视频检验报告.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
status=R/'PROJECT_STATUS.md';s=status.read_text(encoding='utf-8')
old='更新日期：2026-11-16。当前阶段：**第4.5阶段补充修改与女声视频重制已完成并通过本地验收；第五阶段未开始，等待“继续第五阶段”**。'
new='更新日期：2026-11-16。当前阶段：**第4.6阶段全站视觉重构、自定义字体及材料同步已完成并通过本地验收；第五阶段未开始，等待“继续第五阶段”**。'
s=s.replace(old,new)
addition='''## 第4.6阶段最新成果

- 分支codex/skyroute-phase4-6，稳定基线7c08fc8。五条路由与增长/物流全部子模块采用纸白、墨蓝、克制蓝绿的运行决策工作室视觉；全局导航、表单、表格、弹窗、图表、地图和报告统一。首页使用实际网络，物流增加真实计算决策摘要，课堂增加计时与快捷入口。
- 用户ZIP内100%比例TTF已实际集成，iOS27苹方HK、400字重、13,168,700字节，49,330 cmap；用户明确授权直接使用。原ZIP/源码/dist哈希相同；811种检查字符无缺字，五路由CDP确认实际自定义字形。没有等待字体/授权阻塞，没有第三方上传。
- tsc和生产构建通过；28项pytest、4条完整Edge业务流程通过。两轮各52个视图覆盖1920×1080/1440×900/1366×768/390×844，末次地图标注调整后再验52视图。无整页横向溢出、页面异常或外网请求；模态焦点、全屏、手机导航与地图键盘滚动通过。
- 最新交付全部在deliverables/phase4_6：两个MP4为170/175秒、1920×1080，21镜头重录且保留4.5女声原WAV；附两份解说、两份分镜、两份SRT和视频检验报告。完整解码4250/4375帧、64句字幕、21章对齐0ms与Edge播放到结尾通过。
- 同目录同步两份Word说明书10/13页、PPT12页（3真实截图、5原生表格、1图表/XLSX、12页原备注保留）、单人讲稿8页（正文1223字、360秒排期、估算5分46秒）、答辩5页15问、演示操作清单与验收报告。48页实际渲染并图像复核，截图/描述与新版一致。
- 76项材料保全断言通过，基线40个历史文件/后端源码/原业务数据库不变；所有新输出独立保存，未覆盖前阶段文件。官方核实卡与过时阶段框未恢复。详情docs/PHASE4_6_ACCEPTANCE.md、docs/PHASE4_6_DESIGN.md、docs/phase4_6/README.md。
- 验收范围为本地Edge/LibreOffice/解码与结构检查；未虚报Microsoft Office GUI、真人逐字听审、本人彩排或教室硬件测试。字体约13MB首载；真实天气/供应商模型调用/真实推广等既有业务边界保留。第五阶段没有执行。

'''
if '## 第4.6阶段最新成果' not in s:s=s.replace('## 已知限制 / 待人工',addition+'## 已知限制 / 待人工')
s=s.replace('收到“继续第五阶段”后才开始最终复验与打包。','当前应使用deliverables/phase4_6最新版材料与演示操作清单；恢复另读docs/PHASE4_6_ACCEPTANCE.md及docs/phase4_6/README.md。收到“继续第五阶段”后才开始最终复验与打包。')
status.write_text(s,encoding='utf-8')
tasks=R/'TASKS.md';s=tasks.read_text(encoding='utf-8')
if '## 第4.6阶段 全站视觉重构与字体' not in s:s+='''

## 第4.6阶段 全站视觉重构与字体

- [x] 审计五路由、子模块、共享组件、字体和历史成果；Git分支与基线40文件哈希保全
- [x] 独立制定运行决策工作室设计，统一Token、布局、字体、图表和语义色
- [x] 串行重构导航、首页、增长运营、物流决策、网络/表格/图表、课堂、方法、弹窗和全局状态
- [x] 加载用户ZIP原100%TTF，400字重、预加载/回退；实际CDP字形和字符覆盖通过，用户已授权
- [x] 两轮各52视图与末次52视图，多尺寸真实浏览器检查、键盘、全屏、导航、无溢出/异常/外网请求
- [x] 28项后端、4条Edge完整业务回归、类型检查和生产构建通过，算法与原业务库未改
- [x] 重录21个新版网页镜头，保留4.5原女声音轨，170/175秒1080p；全解码/64句字幕/对齐/真实播放通过
- [x] 同步两份说明书、PPT、单人讲稿、答辩与操作清单，保留历史文件和12页原备注/原生表格图表
- [x] 48页真实渲染与图像复核；76材料保全断言；验收报告、路径、页数、时长、哈希和限制记录
- [x] 更新README、PROJECT_STATUS、TASKS与设计/恢复说明；第五阶段未启动

第4.6阶段本地验收通过。Microsoft Office桌面GUI、学生本人彩排、真人逐字听审与教室硬件验证未冒充完成。停止于本阶段，等待“继续第五阶段”。
'''
tasks.write_text(s,encoding='utf-8')
readme=R/'README.md';s=readme.read_text(encoding='utf-8')
s=s.replace('第4.5阶段来源页删减与自然女声重制均已交付并完成本地验收','第4.5阶段女声重制与第4.6阶段全站视觉/字体/材料同步均已交付并完成本地验收')
s=s.replace('**最新视频在`deliverables/phase4_5`**','**第4.5阶段历史视频在`deliverables/phase4_5`**')
intro='''**当前最新版网站与展示材料：第4.6阶段。** 纸白/墨蓝/蓝绿统一界面，真实加载用户提供的苹方HK原TTF。最新两份Word、两个1080p视频（170/175秒，保留4.5女声）、12页PPT、8页单人讲稿、5页答辩、SRT/分镜/解说与演示清单在`deliverables/phase4_6`。历史目录完整保留。28项后端测试、4条Edge业务流程、两轮各52视图和最终52视图、多尺寸/字体/全屏检查通过；48页材料渲染复核，76项保全断言通过。设计见`docs/PHASE4_6_DESIGN.md`，验收与恢复见`docs/PHASE4_6_ACCEPTANCE.md`、`docs/phase4_6/README.md`。第五阶段未执行。

'''
if '**当前最新版网站与展示材料：第4.6阶段。**' not in s:s=s.replace('## Windows 一键运行',intro+'## Windows 一键运行')
readme.write_text(s,encoding='utf-8')
arch=R/'ARCHITECTURE.md';s=arch.read_text(encoding='utf-8')
if '## 第4.6阶段前端设计层' not in s:s+='\n\n## 第4.6阶段前端设计层\n\n前端业务API与计算接口保持不变。tokens.css定义色彩/字体/间距等，studio.css负责统一布局及组件状态，design.ts共享图表主题；style.css仅作为入口。用户原TTF在public/fonts，预加载并通过--font-ui全站继承，图表显式使用同族。Modal统一焦点管理，NetworkMap直接展示真实bootstrap网络并支持小屏键盘滚动；首页复用相同网络。设计、字体与多尺寸验收见docs/PHASE4_6_DESIGN.md及docs/PHASE4_6_ACCEPTANCE.md。\n'
arch.write_text(s,encoding='utf-8')
for file in O.glob('*_解说稿.md'):
 s=file.read_text(encoding='utf-8');s=s.replace('按章节连续生成','沿用第4.5阶段按章节连续生成的原音轨');file.write_text(s,encoding='utf-8')
for file in O.glob('*_分镜脚本.md'):
 s=file.read_text(encoding='utf-8').replace('真实网站录制，','第4.6阶段新版真实网站录制，');file.write_text(s,encoding='utf-8')
files=sorted(p for p in O.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt')
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in files)+'\n',encoding='utf-8')
print('Updated reports/status/tasks/readme/architecture;',len(files),'deliverable checksums')
