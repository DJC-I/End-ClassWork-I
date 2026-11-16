"""Produce acceptance from actual site, voice, rendering and playback evidence."""
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4_5';O=R/'deliverables/phase4_5'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
V=load(Q/'verification.json');P=load(Q/'playback.json');S=load(Q/'site-check.json');B=load(Q/'timeline.json')
assert V['technical_passed'] and P['passed'] and S['passed']
prior=load(Q/'prior-deliverables.json')
for f in prior:assert hashlib.sha256((R/f['file']).read_bytes()).hexdigest()==f['sha256'],f['file']
for v in B['videos']:
 for s in v['scenes']:
  for a,b in zip(s['speech'],s['speech'][1:]):assert a['end']<=b['start']
for sid in ['normal','rain','snow']:
 new=load(Q/f'{sid}-recorded-simulation.json');old=load(R/f'docs/phase3/{sid}-recorded-simulation.json')
 assert new['before']==old['before'] and new['after']==old['after']
source_before=load(R/'docs/phase4/source-audit.json')['source_files'];changed=[]
for f in source_before:
 if hashlib.sha256((R/f['file']).read_bytes()).hexdigest()!=f['sha256']:changed.append(f['file'])
assert set(changed)=={'frontend/src/App.tsx','frontend/src/style.css'}
app=(R/'frontend/src/App.tsx').read_text(encoding='utf-8')
old=subprocess.check_output(['git','show','e5b30eb:project/frontend/src/App.tsx'],encoding='utf-8')
assert old.split('function About()')[0]==app.split('function About()')[0]
for banned in ['官方信息核实情况','打开用户提供的赛事入口','第一阶段只交付本地网站']:assert banned not in app
logistics=load(Q/'logistics-recording.json');limits=next(s for s in logistics['scenes'] if s['id']=='limits')
assert '官方信息核实情况' not in limits['body'] and '第一阶段只交付本地网站' not in limits['body']
assert all(k in limits['body'] for k in ['技术与数据流','运输图与天气假设','模型与统计方法'])
preservation={'passed':True,'prior_deliverable_count':len(prior),'all_prior_deliverables_unchanged':True,'website_changed_files':changed,'App_before_About_unchanged':True,'three_simulations_match_phase3':True,'rerecorded_limits_has_no_removed_components':True,'fourth_phase_outputs_unchanged':True,'fifth_phase_started':False}
(Q/'preservation-check.json').write_text(json.dumps(preservation,ensure_ascii=False,indent=2),encoding='utf-8')
out=['# 第4.5阶段验收报告','','本阶段完成来源页两处UI删除及两个参赛视频自然女声重制；第五阶段未启动，未制作最终压缩包。','','## 实际成片','','目录：`./project\\deliverables\\phase4_5`。','','|文件|时长|分辨率|字节|配音语速|','|---|---|---|---|---|']
for r,v in zip(V['outputs'],B['videos']):out.append(f"|{Path(r['file']).name}|{r['duration']:.3f}秒|{r['width']}×{r['height']}|{r['bytes']:,}|{v['voice_rate']}|")
out+=['','两条均H.264、yuv420p、25fps，AAC 48kHz双声道；烧录中文字幕，同时附同名SRT、解说稿与分镜脚本。新成片在phase4_5，第三阶段原文件没有覆盖。','','## 来源页修改','','- `frontend/src/App.tsx` 中直接删除整张“官方信息核实情况”Card，包括标题、全部正文、赛事链接与容器；删除About底部绿色阶段提示框及容器。不是CSS隐藏，没有替代卡片，没有将长篇核实内容转移到其他页面。','- 剩余三张卡片内容保持原样：技术与数据流、运输图与天气假设、模型与统计方法。全站教学模拟标识、本地API入口、风险/统计边界均保留。','- `style.css`仅新增来源页作用域的末张卡片跨列，桌面2+1铺满、移动单列；无空白网格占位。共享Card、ArrowUpRight、notice样式仍被其他页面使用，保留以免破坏页面。','- 当前网站只改App.tsx与style.css；App中About之前的页面和组件字节相同。其余业务源码、后端及第四阶段交付未改。','','## 自然女声制作','','实际调用在线语音合成，使用`edge-tts 7.3.1`和返回的女声`zh-CN-XiaoxiaoNeural`，接口标注Microsoft Xiaoxiao Online (Natural)，Warm音色。正文为用户项目说明，不含密钥。没有使用Huihui Desktop旧音轨，也没有变调或后期加速旧音轨。','', '各章节整段连续合成，保留句内停顿与上下文韵律；只有章节之间补充少量静音。运营语速+5%，物流+10%，保持pitch默认，避免为挤时长而截断语音。物流初次+5%版本正文176.424秒，连同章节停顿会超目标，因此重新合成+10%版本，正文168.504秒，加停顿成片175秒；运营正文158.472秒，成片170秒。','', '少量解说句改为自然口语，所有关键数值及模拟/计划边界保留。字幕按服务实际SentenceBoundary建立，服务相邻句窗口约50毫秒重叠已裁齐到下一句起点，避免双字幕重叠；没有按字数均分字幕。该方案减少旧式逐句TTS的重启感，仍是合成旁白，不能保证任何听众主观上完全察觉不到AI。没有宣称真人录音或人工逐字听审。','','## 实际验证','','|项目|结果|','|---|---|','|前端类型检查|npm run typecheck成功|','|生产构建|npm run build成功，生产页面使用新构建|','|后端回归|28项pytest通过，0失败；证据pytest-results.xml|','|来源页实际打开|真实Edge在1920×1080、1024×768、390×844检查；两处DOM不存在，剩3卡；无页面异常、横向溢出或空占位|','|真实网站重录|21个场景，运营10、物流11；隔离数据库8005实例；实际输入/分析/解释/报告/仿真，无响应mock；浏览器错误及外网请求为空|','|片尾页面|物流第11镜头录制删减后的来源页，保留三卡，已核对录制body与画面|','|三场景结果|本次实际HTTP仿真before/after与第三阶段一致|']
for r in V['outputs']:
 score=min(a['correlation'] for a in r['audio_alignment_checks']);offset=max(abs(a['best_audio_offset_ms']) for a in r['audio_alignment_checks'])
 out.append(f"|{Path(r['file']).stem}媒体|完整解码{r['decoded_video_frames']}帧；FFmpeg双流解码与Edge实际播放到结尾通过；{r['srt_sentences']}句字幕一致；章节音轨抽查相关最低{score:.6f}、最大偏移{offset:.0f}毫秒|")
out+=['|既有交付保护|第二/三/四阶段20个交付文件哈希不变；第四阶段PPT及两DOCX完整保留|','','全场景画面抽帧与关键1080p帧已检查，见`docs/phase4_5/VISUAL_REVIEW.md`。技术波形相关用于验证音轨合成和时间对齐，不等同于人耳对自然度的评分。Microsoft Edge播放检查及完整解码通过，不代表所有播放器、教室投影与扬声器均验证。','','## 真实边界与剩余事项','','本阶段要求的两处删除与两个新MP4均完成，无音轨缺失或假视频。网站仍为教学模拟，运营未实投，真实模型未验证；风险和成本结论没有改写成真实业务收益。自然度采用神经网络女声及连贯段落改善，最终主观音色喜好由使用者确认。','','第四阶段既有演示清单中关于/about旧阶段文字的说明现在仅属历史记录；当前页面不再显示该提示。保留旧交付原件，没有为本次删除去改写既有PPT、Word或旧视频。课堂默认引用最新视频时使用本目录；旧视频只供比较。','','未做第五阶段最终复验打包、报名、上传或发布。验收完成后停止，等待明确的“继续第五阶段”。','','## 可复验记录','','`docs/phase4_5`保存真实录制、语音目录、时间轴、三场景输出、来源页多尺寸截图、完整解码、Edge播放、保留文件哈希与机器报告。制作说明见README.md。原始WebM、MP3/WAV和中间片段在Git忽略的`.tools/phase4_5`。','','## 成片SHA256','','```text']
out += [f"{r['sha256']}  {Path(r['file']).name}" for r in V['outputs']]
out += ['```','']
report='\n'.join(out)
(O/'第4.5阶段验收报告.md').write_text(report,encoding='utf-8');(R/'docs/PHASE4_5_ACCEPTANCE.md').write_text(report,encoding='utf-8')
(O/'manifest.txt').write_text('\n'.join(sorted(p.name for p in O.iterdir() if p.is_file() and p.name!='manifest.txt'))+'\n',encoding='utf-8')
print('Acceptance and preservation checks passed; report generated')
