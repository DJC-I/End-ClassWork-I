"""Preservation, media and material assertions for Phase 4.6."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json,re
R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4_6';O=R/'deliverables/phase4_6'
sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)});assert condition,name
baseline=json.loads((Q/'baseline-hashes.json').read_text(encoding='utf-8'))
for name,digest in baseline.items():check('preserved '+name,sha((R/name).read_bytes())==digest)
for vid in ['growth','logistics']:
 check('unchanged phase4.5 narration '+vid,(R/f'.tools/phase4_5/{vid}_narration.wav').read_bytes()==(R/f'.tools/phase4_6/{vid}_narration.wav').read_bytes())
for round in ['round1','round2']:
 data=json.loads((Q/(round+'-checks.json')).read_text(encoding='utf-8'))
 check(round+' 52 views',len(data['results'])==52 and not data['errors'] and not data['external'])
 check(round+' actual font and no overflow',all(x['font'] and x['scroll']<=x['width'] for x in data['results']))
v=json.loads((Q/'verification.json').read_text(encoding='utf-8'));check('video technical pass',v['technical_passed'])
p=json.loads((Q/'playback.json').read_text(encoding='utf-8'));check('actual video playback',p['passed'])
f=json.loads((Q/'font-final.json').read_text(encoding='utf-8'));check('font original loaded with full observed coverage',f['unchanged_from_user_zip'] and f['dist_copy_equal'] and not f['missing_characters'])
check('font platform glyphs/fullscreen/mobile/keyboard',json.loads((Q/'font-browser.json').read_text(encoding='utf-8'))['passed'])
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
name='人工智能导论_双赛题结课作品展示.pptx'
with ZipFile(R/'deliverables/phase4'/name) as old,ZipFile(O/name) as new:
 check('pptx no corrupt members',new.testzip() is None)
 for n in old.namelist():
  if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml'):
   original=E.fromstring(old.read(n)).xpath('//a:t/text()',namespaces=ns)
   updated=E.fromstring(new.read(n)).xpath('//a:t/text()',namespaces=ns)
   check('retained complete notes '+n,all(t in updated for t in original))
  if n.startswith('ppt/embeddings/') or n.startswith('ppt/charts/'):
   # Chart colors may change; quantitative text and workbook remain untouched.
   if n.endswith('.xlsx'):check('retained chart workbook '+n,new.read(n)==old.read(n))
 for i in [6,8,9]:
  part=['ppt/media/image.png','ppt/media/image2.png','ppt/media/image3.png'][[6,8,9].index(i)]
  check('updated screenshot slide '+str(i),old.read(part)!=new.read(part))
for name in ['DataClawHub平台运营方案','气象驱动物流运输风险预警与应对决策','课堂展示_单人完整演讲稿','答辩常见问题及参考回答']:
 with ZipFile(O/(name+'.docx')) as z:check('docx intact '+name,z.testzip() is None)
with ZipFile(O/'课堂展示_单人完整演讲稿.docx') as z:
 e=E.fromstring(z.read('word/document.xml'));spoken=[]
 for p in e.findall('.//w:p',ns):
  text=''.join(p.xpath('.//w:t/text()',namespaces=ns))
  if text.startswith('逐字稿  '):spoken.append(text[len('逐字稿  '):])
 count=len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',''.join(spoken)))
 check('12 pages of narration retained',len(spoken)==12);check('speech 1223 characters',count==1223)
renders=json.loads((Q/'docs-render.json').read_text(encoding='utf-8'))
check('Word pages 10/13/8/5',[x['pages'] for x in renders['outputs']]==[10,13,8,5])
check('12 rendered slides',len(list((Q/'render/slides').glob('slide-*.png')))==12)
check('no final phase5 zip created',not list(O.glob('*.zip')))
(Q/'final-checks.json').write_text(json.dumps({'passed':True,'assertions':len(checks),'baseline_files':len(baseline),'speech_characters':count,'checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(checks),'assertions passed;',len(baseline),'original files preserved')
