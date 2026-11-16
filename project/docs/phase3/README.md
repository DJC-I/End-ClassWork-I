# 第三阶段视频制作与恢复

最终文件在deliverables/phase3。两条170秒成片均为实际网站浏览器录像，加中文合成旁白、章节栏与中文字幕；没有制作第四阶段课件或第五阶段压缩包。

## 实际工具

- 网站：当前项目React生产构建与FastAPI，Microsoft Edge由项目Playwright驱动；网站源文件未为录制伪造内容，没有mock接口。
- 录制数据：独立SQLite `.tools/phase3/recording.db`，通过SKYROUTE_DB指定；原有database/skyroute.db不参与录制。OPENAI_API_KEY置空，实际运行规则模式。
- 配音：本机System.Speech Microsoft Huihui Desktop，语速Rate=3，24kHz单声道16bit WAV。先逐句真实合成，再按每句实际采样数生成字幕；没有使用云TTS或购买服务。
- 视频：独立工具`.tools/phase3/ffmpeg.exe`，本机现有imageio-ffmpeg v9.0.2程序复制到项目，实际检测libass、loudnorm及NVENC编码可用；Playwright自动获取其FFmpeg录制组件。
- 媒体检查：项目隔离`.tools/phase3/pydeps/av` 19.0.2；NumPy与Pillow采用工作区Python依赖。工具、原始录像、中间片段和配音均在Git忽略的.tools目录。

## 制作顺序

使用PowerShell、当前项目目录。`$artifactPython`为随工作区提供的Python：

```powershell
$artifactPython = 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe'
& $artifactPython scripts\prepare_phase3.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\synthesize_phase3.ps1 -Rate 3
& $artifactPython scripts\timeline_phase3.py
```

新录制前使用新的项目专用数据库文件，保留旧业务数据库。另开终端运行：

```powershell
$env:SKYROUTE_DB = './project\.tools\phase3\recording-new.db'
$env:OPENAI_API_KEY = ''
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

必须确认8000端口服务确为该隔离实例。初始运营预算须为3000元、访问率12%，默认天气暴雨。录制脚本会实际修改隔离库内参数、保存报告；不要在用户业务实例上运行。

```powershell
node scripts\record_phase3.cjs growth
node scripts\record_phase3.cjs logistics
& $artifactPython scripts\assemble_phase3.py growth
& $artifactPython scripts\assemble_phase3.py logistics
& $artifactPython scripts\verify_phase3.py
node scripts\playback_phase3.cjs
& $artifactPython scripts\audit_phase3_sources.py
```

解说、分镜及字幕由storyboard.json和timeline.json追溯。各场景单独录制，剪去页面加载与准备时段，保留真正操作及计算；不循环静态截图假装操作。原始1920×900录像不缩放、不改数字，置于成片80—980像素高度；顶部80像素为章节栏，底部100像素放字幕。25fps，H.264 yuv420p及48kHz双声道AAC，MP4 faststart。

## 验证证据

- source-audit.json：实际网站源文件与Word哈希、前两阶段机器证据复核。
- growth-recording.json、logistics-recording.json：21镜头实际操作记录、页面文字、浏览器错误与外部请求检查。
- 三份recorded-simulation.json和两份recorded-report.md：本轮真实请求的结果与下载。
- 两份assembly.json：原始WebM、裁切起点、场景输出帧数与最终哈希。
- verification.json：完整解码、流参数、64句字幕、逐镜头配音波形对齐。
- playback.json：Edge实际打开成片，片头/中段/末尾均正常播放并解码，无媒体错误。
- samples、contact图片与VISUAL_REVIEW.md：各章节画面、字幕及目视记录。
- deliverables/phase3/视频检验报告.md：用户可读的验收与限制。

重生成成片后必须重新解码、播放和检查画面，不能沿用旧哈希或旧验证。已完成的前两阶段原始验收记录按历史证据保留，本阶段未重跑所有网站单元测试。
