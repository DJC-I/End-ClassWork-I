"""Read actual Phase 2/3 artifacts and recompute all classroom evidence."""
import hashlib, json, sys
from pathlib import Path
from docx import Document
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'docs/phase4'; QA.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'.tools/phase3/pydeps'))
import av
from backend import engine, growth, seed
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
docs=[]
for old in json.loads((ROOT/'docs/phase2/verification.json').read_text(encoding='utf-8'))['outputs']:
    p=ROOT/old['file']; assert sha(p)==old['sha256']; d=Document(p)
    text='\n'.join([p.text for p in d.paragraphs]+[' | '.join(c.text for c in r.cells) for t in d.tables for r in t.rows])
    (QA/(p.stem+'_来源全文.txt')).write_text(text,encoding='utf-8')
    docs.append({'file':old['file'],'sha256':sha(p),'characters':len(text),'pages':old['pages']})
videos=[]
for v,slug in zip(json.loads((ROOT/'docs/phase3/verification.json').read_text(encoding='utf-8'))['outputs'],['growth','logistics']):
    p=ROOT/v['file']; assert sha(p)==v['sha256']; c=av.open(str(p)); stream=c.streams.video[0]
    duration=float(stream.duration*stream.time_base)
    frames=[]
    for second in [5,80,150]:
        c.seek(int(second/stream.time_base),stream=stream)
        for f in c.decode(stream):
            if f.time>=second:
                target=QA/f'{slug}-video-{second}.png';f.to_image().save(target);frames.append(target.relative_to(ROOT).as_posix());break
    videos.append({'file':v['file'],'sha256':sha(p),'seconds':duration,'width':stream.width,'height':stream.height,'codec':stream.codec_context.name,'audio':c.streams.audio[0].codec_context.name,'sample_frames':frames})
    c.close()
g=growth.calculate(seed.GROWTH_CONFIG)
adjust=json.loads(json.dumps(seed.GROWTH_CONFIG));adjust['channels'][0]['budget']=900;adjust['visit_rate']=.20
experiment=growth.experiment({'a_visitors':200,'a_conversions':30,'b_visitors':200,'b_conversions':40})
weights={'cost':.25,'time':.35,'risk':.4}
order=next(o for o in seed.ORDERS if o['id']=='SR-001')
analysis=engine.analyze(order,next(s for s in seed.SCENARIOS if s['id']=='rain'),weights,seed.network())
simulations={s['id']:engine.simulate(seed.ORDERS,s,weights,seed.network()) for s in seed.SCENARIOS}
for sid,result in simulations.items():
    old=json.loads((ROOT/f'docs/phase3/{sid}-recorded-simulation.json').read_text(encoding='utf-8'))
    assert old['before']==result['before'] and old['after']==result['after']
sources=[]
for p in sorted((ROOT/'backend').glob('*.py'))+sorted((ROOT/'frontend/src').rglob('*')):
    if p.is_file():sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
audit={'phase':4,'documents':docs,'videos':videos,'source_files':sources,'all_prior_artifacts_unchanged':True,'historical_tests_not_rerun':True,'growth_default':g,'growth_adjusted':growth.calculate(adjust),'experiment':experiment,'analysis':analysis,'simulations':simulations}
(QA/'source-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'documents':docs,'videos':videos,'growth_budget':g['budget'],'experiment':experiment,'simulation_recomputed_matches_phase3':True},ensure_ascii=False,indent=2))
