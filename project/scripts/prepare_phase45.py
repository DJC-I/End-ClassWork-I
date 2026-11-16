"""Generate connected neural narration, real-boundary captions and scene timings."""
import asyncio,hashlib,json,re,subprocess,sys,wave
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'.tools/phase4_5';Q=R/'docs/phase4_5';O=R/'deliverables/phase4_5'
sys.path.insert(0,str(W/'pydeps'))
import edge_tts
FF=R/'.tools/phase3/ffmpeg.exe';RATE=24000;VOICE='zh-CN-XiaoxiaoNeural';SPEED='+5%'
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def norm(t):return re.sub(r'[^\w\u4e00-\u9fff]','',t).lower()
async def main():
 board=json.loads((R/'docs/phase3/storyboard.json').read_text(encoding='utf-8'));board.update(phase='4.5',voice=VOICE,voice_rates={'growth':'+5%','logistics':'+10%'},target_seconds_by_video={'growth':170,'logistics':175})
 board.pop('target_seconds',None)
 # Small oral edits preserve all figures and avoid turning plans into outcomes.
 edits={('growth','position',0):'这是DataClawHub平台运营方案。',
 ('growth','channels',2):'这些合作、发布和经费都还在计划中，目前没有真实投放成果。',
 ('growth','adjust',1):'页面会重新计算，总预算变成三千三百元，漏斗访问量变成二千四百。',
 ('growth','report',2):'网站已经能操作和复现，推广有没有效果，还要通过真实实验来验证。',
 ('logistics','agent',2):'外部大模型还没有实际验证，解释文字也需要和计算结果核对。',
 ('logistics','limits',2):'下一步还要拿到官方网络，接入真实天气、位置和共享运力，再校准模型。'}
 for v in board['videos']:
  speed='+5%' if v['id']=='growth' else '+10%'
  v['voice_rate']=speed
  for s in v['scenes']:
   for i in range(len(s['lines'])):s['lines'][i]=edits.get((v['id'],s['id'],i),s['lines'][i])
   text=''.join(s['lines']);folder=W/'speech';folder.mkdir(parents=True,exist_ok=True)
   stem=folder/f"{v['id']}_{s['id']}";mp3=stem.with_suffix('.mp3');meta=stem.with_suffix('.jsonl');wav=stem.with_suffix('.wav');receipt=stem.with_suffix('.receipt.json')
   key=hashlib.sha256((VOICE+speed+text).encode()).hexdigest()
   if not(receipt.exists() and json.loads(receipt.read_text())['key']==key and mp3.exists() and wav.exists()):
    for attempt in range(3):
     try:
      await edge_tts.Communicate(text,VOICE,rate=speed,boundary='SentenceBoundary',connect_timeout=15,receive_timeout=45).save(str(mp3),str(meta));break
     except Exception:
      if attempt==2:raise
      await asyncio.sleep(2)
    subprocess.run([str(FF),'-v','error','-i',str(mp3),'-ar',str(RATE),'-ac','1','-c:a','pcm_s16le','-y',str(wav)],check=True)
    receipt.write_text(json.dumps({'key':key,'voice':VOICE,'rate':speed,'text':text},ensure_ascii=False),encoding='utf-8')
   with wave.open(str(wav),'rb') as f:pcm=f.readframes(f.getnframes());samples=f.getnframes()
   events=[json.loads(line) for line in meta.read_text(encoding='utf-8').splitlines()];events=[e for e in events if e['type']=='SentenceBoundary']
   assert norm(''.join(e['text'] for e in events))==norm(text),(v['id'],s['id'],events)
   s.update(speech_source=str(wav.relative_to(R)).replace('\\','/'),speech_samples=samples,speech_seconds=samples/RATE,boundaries=events)
   print(v['id'],s['id'],round(samples/RATE,2),'seconds connected speech',flush=True)
  speech_samples=sum(s['speech_samples'] for s in v['scenes']);target=170*RATE
  if target-speech_samples<len(v['scenes'])*int(.5*RATE):target=175*RATE
  assert target-speech_samples>=len(v['scenes'])*int(.5*RATE),(v['id'],speech_samples/RATE)
  spare=target-speech_samples;base=spare//len(v['scenes']);cursor=0;pieces=[];subs=[]
  for i,s in enumerate(v['scenes']):
   extra=base+(spare%len(v['scenes']) if i==len(v['scenes'])-1 else 0);lead=min(round(.3*RATE),extra//2)
   s['start']=cursor/RATE;pieces.append(b'\0\0'*lead);cursor+=lead;s['audio_start']=cursor/RATE
   with wave.open(str(R/s['speech_source']),'rb') as f:pieces.append(f.readframes(f.getnframes()))
   s['speech']=[]
   for e in s['boundaries']:
    start=s['audio_start']+e['offset']/1e7;end=min(s['audio_start']+s['speech_seconds'],start+e['duration']/1e7)
    assert start<end
    line={'text':e['text'],'start':start,'end':end};s['speech'].append(line);subs.append(line)
   # Service sentence windows may overlap the next boundary by 50ms.
   # Keep the measured starts; close the earlier subtitle at the next start.
   for a,b in zip(s['speech'],s['speech'][1:]):a['end']=min(a['end'],b['start'])
   cursor+=s['speech_samples'];pieces.append(b'\0\0'*(extra-lead));cursor+=extra-lead
   s['end']=cursor/RATE;s['duration']=s['end']-s['start']
  assert cursor==target
  with wave.open(str(W/f"{v['id']}_narration.wav"),'wb') as f:f.setparams((1,2,RATE,0,'NONE','not compressed'));f.writeframes(b''.join(pieces))
  v['duration']=cursor/RATE;v['speech_seconds']=speech_samples/RATE
  (O/f"{v['name']}.srt").write_text('\n\n'.join(f"{i}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text']}" for i,s in enumerate(subs,1))+'\n',encoding='utf-8-sig')
  (O/f"{v['name']}_解说稿.md").write_text(f"# {v['name']}解说稿\n\n中文神经网络合成女声：晓晓。按章节连续生成，语速{speed}，未通过变调或后期加速冒充自然语音。总长{v['duration']:.3f}秒。\n\n"+'\n\n'.join('## '+s['title']+'\n\n'+''.join(s['lines']) for s in v['scenes']),encoding='utf-8')
  (O/f"{v['name']}_分镜脚本.md").write_text(f"# {v['name']}分镜\n\n真实网站录制，1920×1080，25fps；字幕时间来自实际合成服务句子边界，非均分字数。\n\n|时间|章节|实际操作|\n|---|---|---|\n"+'\n'.join(f"|{stamp(s['start'])}–{stamp(s['end'])}|{s['title']}|{s['action']}|" for s in v['scenes']),encoding='utf-8')
  print('TOTAL',v['id'],v['duration'],'speech',v['speech_seconds'],flush=True)
 (Q/'timeline.json').write_text(json.dumps(board,ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
