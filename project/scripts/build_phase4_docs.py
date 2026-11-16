"""Author one-presenter script and defense preparation with bundled python-docx."""
import json
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'deliverables/phase4';Q=R/'docs/phase4'
C=json.loads((Q/'content.json').read_text(encoding='utf-8'))
def fmt(sec):return f'{sec//60}:{sec%60:02d}'
def new(title,intro):
 d=Document();sec=d.sections[0];sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
 sec.top_margin=Inches(.72);sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.78)
 for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
  s=d.styles[name];s.font.name='Microsoft YaHei';s._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei');s.font.color.rgb=RGBColor(0,0,0)
  for ppr in s._element.findall(qn('w:pPr')):
   for border in ppr.findall(qn('w:pBdr')):ppr.remove(border)
 d.styles['Normal'].font.size=Pt(11);d.styles['Normal'].paragraph_format.line_spacing=1.25
 d.styles['Normal'].paragraph_format.space_after=Pt(7)
 d.styles['Title'].font.size=Pt(22);d.styles['Title'].font.bold=True
 d.styles['Heading 1'].font.size=Pt(16);d.styles['Heading 2'].font.size=Pt(13)
 for name in ['Heading 1','Heading 2']:
  d.styles[name].paragraph_format.space_before=Pt(12);d.styles[name].paragraph_format.space_after=Pt(7)
 d.core_properties.author='SkyRoute AI 课程作品';d.core_properties.title=title
 d.add_paragraph(title,'Title');d.add_paragraph(intro)
 p=sec.footer.paragraphs[0];p.alignment=2
 p.add_run('第 ');field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');p._p.append(field);p.add_run(' 页')
 return d
def label(d,title,text):
 p=d.add_paragraph();p.add_run(title+'  ').bold=True;p.add_run(text);return p
def timing_table(d):
 values=[['页码','主题','时间段','分配']]+[[str(s['number']),s['title'],fmt(s['start_seconds'])+'–'+fmt(s['end_seconds']),str(s['seconds'])+'秒'] for s in C['slides']]
 t=d.add_table(rows=0,cols=4);t.autofit=False
 widths=[.48,3.75,1.38,.70]
 for col,width in zip(t.columns,widths):col.width=Inches(width)
 for rowidx,row in enumerate(values):
  cells=t.add_row().cells
  for i,v in enumerate(row):
   cells[i].width=Inches(widths[i]);cells[i].text=v
   tcPr=cells[i]._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   tcPr.append(borders);sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'20384A' if rowidx==0 else ('F0F4F7' if rowidx%2==0 else 'FFFFFF'));tcPr.append(sh)
   for p in cells[i].paragraphs:
    p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4);p.paragraph_format.line_spacing=1.05
    for run in p.runs:
     run.font.size=Pt(9);run.font.color.rgb=RGBColor.from_string('FFFFFF' if rowidx==0 else '000000')
   cells[i].vertical_alignment=1
  if rowidx==0:
   repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 return t

d=new('课堂展示单人完整演讲稿','同一名学生从第1页讲到第12页，全程不换主讲。主讲人在开场口头补充本人真实姓名。总排期6分钟，包含两次简短网站演示与读图停顿；讲稿可直接逐字朗读。')
d.add_heading('时间与使用说明',1)
estimated=round(C['spoken_characters']/230*60+27)
d.add_paragraph(f"逐字稿共{C['spoken_characters']}个汉字、字母及数字，不含标点、空格和操作提示。正文按约230字/分钟估算需{C['spoken_characters']/230*60:.1f}秒，另预留27秒操作及停顿，约{estimated//60}分{estimated%60:02d}秒。各页排期合计360秒，余量用于数字读法、指示与切屏。该估算不是本人实测，须按本人语速彩排。")
d.add_paragraph('演讲时只读“逐字稿”段落，操作、时间、翻页和来源提示不读。第6页与第10页各预留12秒操作，第11页预留3秒读图。若切屏失败10秒内无法恢复，立即按原页截图继续，不延长总时长。')
timing_table(d)
for s in C['slides']:
 if s['number']%2==1:d.add_page_break()
 d.add_heading(f"第{s['number']}页 {s['title']}",1)
 label(d,'时间',f"{fmt(s['start_seconds'])}–{fmt(s['end_seconds'])}，本页{s['seconds']}秒；其中操作或停顿{s['pause_seconds']}秒。")
 label(d,'逐字稿',s['spoken'])
 label(d,'现场提示',s['demo'])
 label(d,'翻页与衔接',s['cue'])
 label(d,'应急',('网站失败直接指本页截图说明上述数值，省去切屏。' if s['number'] in [6,10] else '按PPT静态页面继续讲解，不临时打开外网。'))
d.add_page_break();d.add_heading('彩排与缩时备用稿',1)
d.add_paragraph('彩排记录由主讲学生填写：实际总时长____；第6页返回时间____；第10页返回时间____。若超过6分钟，优先减少重复解释，不加速读数。当前交付的6分钟是估算与分配，未代替学生实际彩排。')
d.add_paragraph('若现场只剩3分钟，取消全部切屏，依次展示第1、2、5、6、8、10、11、12页。每页控制约10、15、20、20、20、30、45、20秒，合计180秒。跳过页只在放映中略过，不删除源文件。')
d.add_paragraph('三分钟串讲：我的作品将平台运营与物流案例结合。运营先定位学生、开发者和行业人员，用一个暴雨冷链问题引导完成计算，再规划回访和复盘。三千元是预算假设，增长模型和A/B计算都已实现，但没有真实推广成效。物流部分把订单、天气时间窗和有向网络结合，比较原计划、提前、绕行和中转。暴雨一号冷链默认推荐绕行，成本一千二百四十二元，用时二点九五小时。三档严重度配对回放中，暴雨准时占比提高，暴雪仍有延误，正常天气成本增加六十八元。所有业务数据均为教学模拟，当前使用规则模式。下一步需要真实访谈、授权路网和天气位置数据，再做校准。谢谢。')
speech=O/'课堂展示_单人完整演讲稿.docx';d.save(speech)

d=new('答辩常见问题及参考回答','这份材料供同一名主讲学生在课堂问答时使用。回答先说明实际实现，再说明证据和边界。以下15问覆盖算法、AI、运营、数据真实性、工程验证与应用。每题可先说第一句，再按追问展开。')
for item in C['questions']:
 if item['number'] in [4,7,10,13]:d.add_page_break()
 d.add_heading(f"问题{item['number']} {item['question']}",2)
 d.add_paragraph(item['answer']);label(d,'核对位置',item['source'])
d.add_heading('回答时的数字与表述',1)
d.add_paragraph('重点数字：预算3000元；默认独立漏斗激活201.60；默认渠道激活432.51与CAC6.94元；A/B p=0.18821；SR-001暴雨风险47.15、绕行1242元与2.95h；正常模拟总成本增加68元。所有数字应同时说明假设与比较基准。')
d.add_paragraph('不使用“真实降本”“已增长用户”“已经合作”“已经取得官方网络”“大模型已调用”“风险已消除”等未经证实表述。课堂问题超出验证范围时，明确回答尚未验证，并指出需要补充的数据或实验。')
defense=O/'答辩常见问题及参考回答.docx';d.save(defense)
print('Authored two DOCX files; script characters',C['spoken_characters'],'questions',len(C['questions']))
