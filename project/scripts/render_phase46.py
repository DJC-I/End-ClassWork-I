"""Render actual PPTX and both DOCX using task-local official portable LO."""
import argparse,importlib.util,json,os,subprocess,sys
from pathlib import Path
from pypdf import PdfReader
from pdf2image import convert_from_path
R=Path(__file__).resolve().parents[1];Q=R/'docs/phase4_6';O=R/'deliverables/phase4_6'
LO=R/'.tools/libreoffice/App/libreoffice/program/soffice.exe'
DOCSKILL=Path('./.codex/plugins/cache/openai-primary-runtime/documents/26.1112.11217/skills/documents')
parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['docs','slides']);args=parser.parse_args()
assert LO.is_file()
results=[]
if args.kind=='docs':
 spec=importlib.util.spec_from_file_location('renderer',DOCSKILL/'render_docx.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
 renderer._resolve_soffice=lambda:str(LO)
 # The Windows LO console emits a locale encoding, while Python UTF-8 mode is
 # enabled for Chinese file paths. Decode logs permissively; retain all errors.
 original_run=subprocess.run
 def decoded_run(*a,**kw):
  if kw.get('text') or kw.get('universal_newlines'):
   kw.setdefault('encoding','utf-8');kw.setdefault('errors','replace')
  return original_run(*a,**kw)
 renderer.subprocess.run=decoded_run
 for name,slug in [('DataClawHub平台运营方案','growth-manual'),('气象驱动物流运输风险预警与应对决策','logistics-manual'),('课堂展示_单人完整演讲稿','speech'),('答辩常见问题及参考回答','defense')]:
  target=Q/'render'/slug;target.mkdir(parents=True,exist_ok=True)
  for stale in target.glob('page-*.png'):stale.unlink()
  sys.argv=[str(DOCSKILL/'render_docx.py'),str(O/(name+'.docx')),'--output_dir',str(target),'--emit_pdf']
  renderer.main();pdf=next(target.glob('*.pdf'));count=len(PdfReader(pdf).pages)
  assert len(list(target.glob('page-*.png')))==count
  results.append(dict(file=(O/(name+'.docx')).relative_to(R).as_posix(),pages=count,renderer='packaged render_docx.py',pdf=pdf.relative_to(R).as_posix()))
else:
 target=Q/'render/slides';target.mkdir(parents=True,exist_ok=True)
 p=O/'人工智能导论_双赛题结课作品展示.pptx'
 profile=R/'.tools/phase4_6/lo-ppt-profile';profile.mkdir(parents=True,exist_ok=True)
 run=subprocess.run([str(LO),'-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','pdf:impress_pdf_Export','--outdir',str(target),str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
 (Q/'ppt-render.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
 assert run.returncode==0,run.stderr
 pdf=target/(p.stem+'.pdf');assert pdf.exists();doc=PdfReader(pdf)
 images=convert_from_path(str(pdf),dpi=108)
 for i,(page,img) in enumerate(zip(doc.pages,images)):
  img.save(target/f'slide-{i+1:02d}.png')
  (target/f'slide-{i+1:02d}.txt').write_text(page.extract_text(),encoding='utf-8')
 assert len(doc.pages)==12
 results.append(dict(file=p.relative_to(R).as_posix(),pages=len(doc.pages),renderer='task-local official portable LibreOffice Impress',pdf=pdf.relative_to(R).as_posix()))
for item in results:print(item['file'],item['pages'])
(Q/f'{args.kind}-render.json').write_text(json.dumps({'soffice':str(LO),'desktop_office_used':False,'outputs':results},ensure_ascii=False,indent=2),encoding='utf-8')
