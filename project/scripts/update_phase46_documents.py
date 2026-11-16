"""Focused OOXML updates: preserve original pagination, notes and editable objects."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from lxml import etree as E
from PIL import Image, ImageOps
import json, posixpath

R=Path(__file__).resolve().parents[1]; Q=R/'docs/phase4_6'; O=R/'deliverables/phase4_6'; A=Q/'assets'
O.mkdir(exist_ok=True)
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','w':W}
reports=[]
def xmlbytes(e):return E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
def fit_image(file,size):
 im=Image.open(file).convert('RGB'); out=ImageOps.pad(im,size,method=Image.Resampling.LANCZOS,color='white');b=BytesIO();out.save(b,format='PNG');return b.getvalue()
def replace_paragraphs(data,changes):
 root=E.fromstring(data)
 for p in root.findall('.//w:p',NS):
  nodes=p.findall('.//w:t',NS);old=''.join(t.text or '' for t in nodes);new=old
  for a,b in changes:new=new.replace(a,b)
  if new!=old and nodes:
   nodes[0].text=new
   for n in nodes[1:]:n.text=''
 return xmlbytes(root)
def save_parts(source,destination,changes):
 with ZipFile(source) as src,ZipFile(destination,'w',ZIP_DEFLATED) as out:
  for item in src.infolist():out.writestr(item,changes.get(item.filename,src.read(item.filename)))

# Compose two actual browser captures; no UI is drawn or reconstructed.
top=Image.open(A/'risk_recommendation.png').convert('RGB');bottom=Image.open(A/'plans_table.png').convert('RGB')
combined=Image.new('RGB',(max(top.width,bottom.width),top.height+bottom.height+24),'white')
combined.paste(top,(0,0));combined.paste(bottom,(0,top.height+24));combined.save(A/'plans_rain.png')

specs=[
 ('phase2','DataClawHub平台运营方案',{'image1.png':'growth_model.png'},[
  ('图1 第一阶段实际运营工作台截图裁切','图1 第4.6阶段真实运营工作台截图'),
  ('第三阶段视频和第四阶段课件未在本阶段启动。','本文保留赛事核查记录，展示截图已同步至第4.6阶段。'),
  ('[3] docs/PHASE1_ACCEPTANCE.md 及运营截图。','[3] docs/PHASE1_ACCEPTANCE.md；docs/phase4_6/assets。')]),
 ('phase2','气象驱动物流运输风险预警与应对决策',{'image3.png':'agent_rain.png','image4.png':'network_wide.png','image5.png':'plans_rain.png'},[
  ('第一阶段Edge截图','第4.6阶段Edge截图'),('图中绿色线路','图中蓝绿色线路'),
  ('右侧记录暴雨55mm/3h、风速12m/s、能见度1.8km及订单承诺时间。','地图下方天气栏记录暴雨55mm/3h、风速12m/s、能见度1.8km；右侧显示订单承诺时间。'),
  ('本节及下节图片均为第一阶段实际应用截图的裁切，只去除无关页面区域，没有重绘UI或修改结果。原始文件为docs/screenshots/logistics-rain.png。','本节及下节为第4.6阶段真实网站截图，仅裁切或留白适配，未重绘UI或修改结果。原图见docs/phase4_6/assets。'),
  ('本阶段从相同函数重算全部文档引用场景指标，并与已保存结果逐项比较；没有把历史测试描述成重新执行全部网站测试。','第4.6阶段重跑28项后端测试、4条浏览器流程及两轮多尺寸检查；文档指标与既有计算保持一致。')]),
 ('phase4','课堂展示_单人完整演讲稿',{},[
  ('滚至“四类应对策略，逐项对比”','先看顶部决策摘要，再看“四类应对策略，逐项对比”')]),
 ('phase4','答辩常见问题及参考回答',{},[
  ('第四阶段重算数据并在隔离数据库复验两条展示流程，未重跑全套测试。','第4.6阶段再次通过28项后端测试、4条Edge业务流程及两轮四尺寸视觉检查。'),
  ('docs/PHASE1_ACCEPTANCE.md；docs/phase4/demo-check.json','docs/PHASE4_6_ACCEPTANCE.md；docs/phase4_6'),
  ('两个170秒视频','170秒与175秒的两个视频')])]
for phase,name,images,texts in specs:
 src=R/'deliverables'/phase/(name+'.docx');dst=O/(name+'.docx');changes={}
 with ZipFile(src) as z:
  changes['word/document.xml']=replace_paragraphs(z.read('word/document.xml'),texts)
  for old,new in images.items():
   part='word/media/'+old;changes[part]=(A/new).read_bytes()
   doc=E.fromstring(changes['word/document.xml']);rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
   rid=next(r.get('Id') for r in rels if r.get('Target')=='media/'+old)
   for drawing in doc.findall('.//w:drawing',NS):
    if not any(b.get('{'+NS['r']+'}embed')==rid for b in drawing.findall('.//a:blip',NS)):continue
    newimage=Image.open(A/new)
    for extent in drawing.iter():
     if E.QName(extent).localname in ['extent','ext'] and extent.get('cx'):
      extent.set('cy',str(round(int(extent.get('cx'))*newimage.height/newimage.width)))
   changes['word/document.xml']=xmlbytes(doc)
 save_parts(src,dst,changes);reports.append({'file':dst.relative_to(R).as_posix(),'updated_images':images,'text_replacements':len(texts)})

# Preserve the original native chart's embedded workbook, all five tables and twelve notes.
src=R/'deliverables/phase4/人工智能导论_双赛题结课作品展示.pptx';dst=R/'.tools/phase4_6/build/candidate.pptx';changes={}
colors={'0F1822':'172C3C','B6F266':'D7EBE3','137F83':'11665E','F7FAFC':'F3F5F4'}
with ZipFile(src) as z:
 for n in z.namelist():
  if not n.endswith('.xml') or not n.startswith('ppt/'):continue
  e=E.fromstring(z.read(n));modified=False
  for c in e.findall('.//a:srgbClr',NS):
   if c.get('val','').upper() in colors:c.set('val',colors[c.get('val').upper()]);modified=True
  for t in e.findall('.//a:t',NS):
   if t.text and '2个170秒参赛视频' in t.text:t.text=t.text.replace('2个170秒参赛视频','2个参赛视频\n170秒 / 175秒');modified=True
  if n.startswith('ppt/notesSlides/notesSlide'):
   body=e.find('.//p:sp[p:txBody]/p:txBody',NS)
   if body is not None:
    p=E.SubElement(body,'{'+NS['a']+'}p');run=E.SubElement(p,'{'+NS['a']+'}r');E.SubElement(run,'{'+NS['a']+'}t').text='第4.6阶段同步：操作路径不变；新版真实截图；保留第4.5阶段女声，视频170/175秒；方法页仅保留三张正常信息卡。';modified=True
  if modified:changes[n]=xmlbytes(e)
 for number,new in [(6,'growth_model.png'),(8,'network_wide.png'),(9,'agent_rain.png')]:
  e=E.fromstring(z.read(f'ppt/slides/slide{number}.xml'));pic=e.find('.//p:pic',NS)
  blip=pic.find('.//a:blip',NS);rid=blip.get('{'+NS['r']+'}embed')
  rels=E.fromstring(z.read(f'ppt/slides/_rels/slide{number}.xml.rels'))
  target=next(r.get('Target') for r in rels if r.get('Id')==rid)
  media=target.lstrip('/') if target.startswith('/') else posixpath.normpath('ppt/slides/'+target)
  old=Image.open(BytesIO(z.read(media)));changes[media]=fit_image(A/new,old.size)
save_parts(src,dst,changes)
reports.append({'file':dst.relative_to(R).as_posix(),'pptx_update':'focused OOXML; original workbook/tables/notes preserved','updated_slides':[6,8,9,12]})
(Q/'material-updates.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated four DOCX and PPTX candidate; historical originals untouched')
