# 第4.5阶段制作与复验

范围：来源页两处删除、自然女声重制两个参赛视频。新版放 `deliverables/phase4_5`，旧第三阶段与第四阶段交付原样保留，第五阶段未开始。

## 来源页

`frontend/src/App.tsx` 的About函数直接移除官方信息Card与底部阶段notice；未隐藏、未替换或迁移。`style.css`用 `.methods-grid > .card:last-child { grid-column: 1 / -1; }`让剩余第三张卡铺满行。共享图标、Card和notice还用于其他页面，不移除。

`npm run typecheck`与`npm run build`成功；`.venv/Scripts/python.exe -m pytest tests -q --junitxml=docs/phase4_5/pytest-results.xml`28通过。`node scripts/check_phase45_site.cjs`实际在生产服务8005上检查1920、1024、390宽度，保存截图及DOM/几何证据。

## 语音

隔离安装 `edge-tts==7.3.1` 及依赖在 `.tools/phase4_5/pydeps`，Python3.12运行。服务实际返回女声列表存 `voices.json`。选晓晓 `zh-CN-XiaoxiaoNeural`，运营+5%，物流+10%，默认音高。逐章节整段连续合成，服务返回SentenceBoundary用于同步SRT。保留原事实、数字与模拟边界，少量句子改为口语；无后期变调、atempo或旧音轨复用。

```powershell
$env:PYTHONUTF8='1'
python scripts/probe_phase45_voice.py
python scripts/prepare_phase45.py
```

这两步联网请求语音服务；输入仅为项目解说文字，无密钥。已完成后的MP4播放不需要网络。合成缓存以音色、语速及文本哈希判定，日志和源MP3/WAV在.tools；自然度属主观评价，未声称真人朗读或人工逐字听审。

## 真实重录与合成

项目根另开PowerShell，指定**独立任务库**，新一次全量录制应使用新库路径，不得使用业务库。以下路径为本次实际实例；已录制过的库不能当作初始默认参数再次录制：

```powershell
$env:SKYROUTE_DB=Join-Path (Get-Location) '.tools/phase4_5/recording.db'
$env:OPENAI_API_KEY=''
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8005
```

确认该端口确为任务库实例后依次执行：

```powershell
node scripts/check_phase45_site.cjs
node scripts/record_phase45.cjs growth
node scripts/record_phase45.cjs logistics
# $artifactPython为本机Codex托管runtime的dependencies/python/python.exe
& $artifactPython scripts/assemble_phase45.py growth
& $artifactPython scripts/assemble_phase45.py logistics
& $artifactPython scripts/verify_phase45.py
node scripts/playback_phase45.cjs
& $artifactPython scripts/report_phase45.py
```

编码沿用 `.tools/phase3/ffmpeg.exe` 的h264_nvenc，PyAV来自 `.tools/phase3/pydeps`，NumPy/Pillow来自托管runtime。各章节重新录制真实页面，生产源码无假数据替换；21镜头、1920×900原始画面不缩放，加章节条80像素及字幕区100像素，成1920×1080 25fps。按新旁白安排170/175秒，最终AAC响度规范化。

`verify_phase45.py`完整解码两条视频、检查字幕文本/时序、逐章节音轨波形对齐、输出接触表。`playback_phase45.cjs`以HTTP Range真实播放片头/中段/末尾并验证到达结尾。`report_phase45.py`检查旧交付20文件哈希、当前源码改动范围、三天气实际仿真结果、片尾删除内容，生成验收报告。需最终看图后再认定视觉检查完成。

`prior-deliverables.json`来自本阶段开始时原文件的实际哈希，不能重写它来掩盖旧文件变更。历史第四阶段verify_phase4.py包含“网站源码保持原样”断言，本次授权修改后该历史源码断言不再适用；用本阶段preservation-check.json核对既有交付不变，不能改历史证据凑通过。

最后更新PROJECT_STATUS/TASKS并停止。没有最终参赛ZIP、报名、上传或发布操作。
