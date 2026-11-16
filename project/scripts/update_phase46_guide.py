from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4_6';O=R/'deliverables/phase4_6'
p=Q/'timeline.json';j=json.loads(p.read_text(encoding='utf-8'));j['phase']='4.6';j['narration_source']='phase4_5 original WAV, byte-identical';p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
s=(R/'deliverables/phase4/演示操作清单.md').read_text(encoding='utf-8')
s=s.replace('两条170秒视频','170秒与175秒的两条视频').replace('.tools\\phase4\\classroom.db','.tools\\phase4_6\\classroom.db').replace('8004','8008').replace('8005','8009').replace('deliverables/phase3','deliverables/phase4_6').replace('第三阶段实际网站录制','第4.6阶段新版界面的真实网站录制').replace('视频各170秒','视频分别170秒、175秒').replace('第四阶段验收后停止','第4.6阶段验收后停止')
s=s.replace('网站部分历史介绍仍写第一阶段状态，当前实际交付以PROJECT_STATUS.md为准，不把该旧文字作为当前文件清单。','该页仅保留技术与数据流、运输图与天气假设、模型与统计方法三张卡片；官方核实卡与过时阶段框已移除。')
s=s.replace('滚至“四类应对策略，逐项对比”','先读顶部决策摘要，再滚至“四类应对策略，逐项对比”')
def tm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
g,l=j['videos'];gd={x['id']:x for x in g['scenes']};ld={x['id']:x for x in l['scenes']}
s=s.replace('01:40–01:59 参数修改；01:59–02:15 A/B',f"{tm(gd['adjust']['start'])}–{tm(gd['adjust']['end'])} 参数修改；{tm(gd['experiment']['start'])}–{tm(gd['experiment']['end'])} A/B")
s=s.replace('00:43–01:16 风险与四方案；01:48–02:19 暴雨/暴雪；02:19–02:34 正常成本代价',f"{tm(ld['risk']['start'])}–{tm(ld['plans']['end'])} 风险与四方案；{tm(ld['rain']['start'])}–{tm(ld['snow']['end'])} 暴雨/暴雪；{tm(ld['normal']['start'])}–{tm(ld['normal']['end'])} 正常成本代价")
s=s.replace('## 标准6分钟操作','可在 `/demo` 使用“开始计时 / 暂停计时 / 归零”，并用“打开增长演示 / 打开物流演示”快速切换；顶部“进入全屏”可用于投影。离开演示页后计时组件会重新初始化，请以讲稿时间表为准。\n\n## 标准6分钟操作')
(O/'演示操作清单.md').write_text(s,encoding='utf-8');print('Guide synchronized')
