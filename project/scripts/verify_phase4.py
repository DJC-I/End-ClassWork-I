"""Check the final classroom files against audited source data and renderings."""
import hashlib,json,re,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from docx import Document
from pypdf import PdfReader
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4';O=R/'deliverables/phase4'
C=json.loads((Q/'content.json').read_text(encoding='utf-8'))
A=json.loads((Q/'source-audit.json').read_text(encoding='utf-8'))
V=json.loads((Q/'pptx-validation.json').read_text(encoding='utf-8'))
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(node):return ''.join(node.itertext())
def xmltext(node):return ''.join(t.text or '' for t in node.findall('.//a:t',NS))
checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'check':name,'passed':True})

ppt=O/'人工智能导论_双赛题结课作品展示.pptx'
check('Final PPTX hash matches finalization receipt',sha(ppt)==V['finalSha256'])
counts={'tables':0,'pictures':0,'charts':0,'notes':0}
slide_text=[]
with zipfile.ZipFile(ppt) as z:
 check('PPTX CRC integrity',z.testzip() is None)
 slides=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda s:int(re.search(r'(\d+)\.xml',s)[1]))
 check('Exactly twelve slides',len(slides)==12)
 for i,n in enumerate(slides,1):
  root=ET.fromstring(z.read(n));slide_text.append(xmltext(root))
  counts['tables']+=len(root.findall('.//a:tbl',NS));counts['pictures']+=len(root.findall('.//p:pic',NS));counts['charts']+=len(root.findall('.//c:chart',NS))
  note=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'));nt=xmltext(note);s=C['slides'][i-1]
  check(f'Slide {i} notes include full speech, action, transition and provenance',all(v in nt for v in [s['spoken'],s['demo'],s['cue'],s['source']]))
  counts['notes']+=1
 check('Five editable native tables, one chart and three actual screenshots',counts=={'tables':5,'pictures':3,'charts':1,'notes':12})
 media_hashes={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
 for rel in ['docs/phase4/growth-demo.png','docs/phase3/logistics-weather.png','docs/phase4/agent.png']:
  check('Embedded screenshot byte identity: '+rel,sha(R/rel) in media_hashes)
 chart_parts=[n for n in z.namelist() if re.fullmatch(r'.*/charts/chart\d+\.xml',n)]
 chart=ET.fromstring(z.read(chart_parts[0]));series=chart.findall('.//c:barChart/c:ser',NS)
 expected=[[round(A['simulations'][sid][key]['on_time_rate']/100,4) for sid in ['normal','rain','snow']] for key in ['before','after']]
 got=[[float(v.text) for v in s.findall('.//c:val//c:numCache/c:pt/c:v',NS)] for s in series]
 check('Native chart values equal recomputed simulation with four-decimal ratio rounding',got==expected)
 check('Chart includes embedded workbook',any(n.endswith('.xlsx') and '/embeddings/' in n for n in z.namelist()))

for plan in A['analysis']['plans']:
 for k in ['hours','cost','delay_hours','risk']:
  check(f'SR-001 table {plan["name"]} {k}',f'{plan[k]:.2f}' in slide_text[9])
for sid in ['normal','rain','snow']:
 for key in ['before','after']:
  check(f'Simulation cost {sid} {key}',f'{A["simulations"][sid][key]["total_cost"]:.2f}' in slide_text[10])
check('Budget sum is 3000',sum(c['budget'] for c in A['growth_default']['config']['channels'])==3000) if 'config' in A['growth_default'] else check('Budget is 3000',A['growth_default']['budget']==3000)
check('P value appears on slide',f'{A["experiment"]["p_value"]:.5f}' in slide_text[6])
speech=Document(O/'课堂展示_单人完整演讲稿.docx')
speech_text='\n'.join(p.text for p in speech.paragraphs)
spoken=[p.text.removeprefix('逐字稿  ') for p in speech.paragraphs if p.text.startswith('逐字稿  ')]
check('DOCX contains all twelve exact spoken paragraphs',spoken==[s['spoken'] for s in C['slides']])
characters=sum(len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s)) for s in spoken)
check('Character count and six-minute timing',characters==1223==C['spoken_characters'] and sum(s['seconds'] for s in C['slides'])==360)
check('Single presenter and fallback script',all(t in speech_text for t in ['全程不换主讲','三分钟串讲','翻页与衔接','现场提示']))
defense=Document(O/'答辩常见问题及参考回答.docx');defense_text='\n'.join(p.text for p in defense.paragraphs)
check('All fifteen questions and answers retained',len(C['questions'])==15 and all(q['question'] in defense_text and q['answer'] in defense_text for q in C['questions']))
for f in O.glob('*.docx'):
 with zipfile.ZipFile(f) as z:check('DOCX CRC integrity '+f.name,z.testzip() is None)
 for style in ['Title','Heading 1','Heading 2']:
  d=Document(f);check(f'Black headings {f.name} {style}',str(d.styles[style].font.color.rgb)=='000000')
checklist=(O/'演示操作清单.md').read_text(encoding='utf-8')
check('Three-minute fallback route agrees across files',all('第1、2、5、6、8、10、11、12页' in t for t in [speech_text,checklist]))
check('Contingency covers no website, no network and insufficient time',all(s in checklist for s in ['网站无法启动','网络不可用','时间不足']))
outputs=[]
for report in ['slides-render.json','docs-render.json']:
 for item in json.loads((Q/report).read_text(encoding='utf-8'))['outputs']:
  p=R/item['file'];pdf=R/item['pdf'];reader=PdfReader(pdf)
  check('Rendered page count '+p.name,len(reader.pages)==item['pages'])
  check('Rendered pages contain text '+p.name,all(len(page.extract_text().strip())>30 for page in reader.pages))
  outputs.append({'file':item['file'],'bytes':p.stat().st_size,'sha256':sha(p),'pages':item['pages']})
for old in A['documents']+A['videos']+A['source_files']:
 check('Prior/source file unchanged '+old['file'],sha(R/old['file'])==old['sha256'])
demo=json.loads((Q/'demo-check.json').read_text(encoding='utf-8'))
check('Isolated real Edge rehearsal passed with baseline and saved change',demo['passed'] and not demo['mocked'] and not demo['errors'] and not demo['external_requests'] and demo['baseline']['channels'][0]['budget']==600 and demo['config']['channels'][0]['budget']==900)
# Contact sheets support a final visual scan of the actual rendered slides.
for start in [1,7]:
 sheet=Image.new('RGB',(1920,1140),'#dfe5e9');draw=ImageDraw.Draw(sheet)
 for j,n in enumerate(range(start,start+6)):
  im=Image.open(Q/f'render/slides/slide-{n:02d}.png');im.thumbnail((948,533))
  x=(j%2)*960;y=(j//2)*380;im.thumbnail((640,360));sheet.paste(im,(x+10,y+20));draw.text((x+660,y+20),f'Slide {n}',fill='black')
 sheet.save(R/f'.tools/phase4/build/qa-slides-{start:02d}.png')
result={'phase':4,'passed':True,'outputs':outputs,'native_counts':counts,'spoken_characters':characters,'duration_allocation_seconds':360,'estimated_seconds_at_230_characters_per_minute_including_27_reserved':round(characters/230*60+27),'student_rehearsal_performed':False,'microsoft_office_gui_verified':False,'source_and_prior_artifacts_unchanged':True,'checks':checks}
(Q/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2));print('Assertions passed:',len(checks))
