import asyncio,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'.tools/phase4_5';sys.path.insert(0,str(W/'pydeps'))
import edge_tts
async def main():
 voices=await edge_tts.list_voices()
 selected=[v for v in voices if v['ShortName'] in ['zh-CN-XiaoxiaoNeural','zh-CN-XiaoyiNeural']]
 (R/'docs/phase4_5/voices.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
 text='我们把天气预警和运输订单放在一起，看看哪些地方会受影响，再比较成本和时效。这里的结果来自教学模拟，不能当成真实业务收益。'
 for voice in selected:
  name=voice['ShortName'];c=edge_tts.Communicate(text,name,rate='+5%',boundary='SentenceBoundary')
  await c.save(str(W/(name+'.mp3')),str(W/(name+'.jsonl')))
  print('Generated',name,flush=True)
asyncio.run(main())
