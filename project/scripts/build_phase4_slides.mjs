import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='./.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const modules=process.env.RUNTIME_NODE_MODULES;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')).href).catch(async()=>{
 const {createRequire}=await import('node:module');const req=createRequire(path.join(modules,'__phase4__.cjs'));return import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
});
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const content=JSON.parse(await fs.readFile(path.join(ROOT,'docs/phase4/content.json'),'utf8'));
const audit=JSON.parse(await fs.readFile(path.join(ROOT,'docs/phase4/source-audit.json'),'utf8'));
const build=path.join(ROOT,'.tools/phase4/build');await fs.mkdir(build,{recursive:true});
const C={navy:'#0F1822',ink:'#182C3B',muted:'#566B79',green:'#B6F266',teal:'#137F83',paper:'#F7FAFC',rule:'#CAD6DE',white:'#FFFFFF',orange:'#A55622'};
const font='Microsoft YaHei';const pres=Presentation.create({slideSize:{width:1280,height:720}});
const frames=[];
function tx(s,text,x,y,w,h,size=26,color=C.ink,bold=false){
 const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=text;a.text.style={typeface:font,fontSize:size,color,bold,verticalAlignment:'top',autoFit:'none',insets:0,wrap:'square'};
 frames.push({slide:pres.slides.items.length,text,x,y,w,h,size});return a;
}
function rect(s,x,y,w,h,color){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:'none',width:0}});}
function line(s,y){rect(s,64,y,1152,1,C.rule);}
function base(i,dark=false){const s=pres.slides.add();s.background.fill=dark?C.navy:C.paper;const t=content.slides[i-1];
 if(i>1){tx(s,t.title,64,44,1150,62,41,dark?C.white:C.ink,true);line(s,124);}
 tx(s,String(i).padStart(2,'0')+' / 12',1118,673,100,26,16,dark?C.green:C.muted);
 s.speakerNotes.text=`第${i}页 ${t.title}\n时间 ${t.start_seconds}–${t.end_seconds}秒，本页${t.seconds}秒。\n逐字稿：${t.spoken}\n翻页：${t.cue}\n演示：${t.demo}\n依据：${t.source}\n全部运营数字为假设，物流数据为教学模拟。`;
 return s;
}
async function picture(s,file,x,y,w,h,alt){const bytes=await fs.readFile(path.join(ROOT,file));s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:file.endsWith('.jpg')?'image/jpeg':'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function table(s,values,x,y,w,h,widths,size=23){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});
 t.borders.assign({fill:C.rule,width:1,style:'solid'});
 for(let r=0;r<values.length;r++){t.rows[r].height=h/values.length;for(let c=0;c<values[0].length;c++)t.getCell(r,c).fill=r===0?C.ink:(r%2?C.white:'#EDF3F6');}
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({textStyle:{typeface:font,fontSize:size,color:C.ink},margins:{top:8,bottom:8,left:12,right:12},anchor:'center'});
 t.cells.block({row:0,column:0,rowCount:1,columnCount:values[0].length}).assign({textStyle:{typeface:font,fontSize:size,color:C.white,bold:true}});return t;}
function foot(s,text){tx(s,text,64,626,1120,36,18,C.muted);}
let s=base(1,true);
tx(s,'SkyRoute AI',64,65,760,95,76,C.green,true);
tx(s,'人工智能导论\n双赛题结课作品展示',64,189,1090,172,59,C.white,true);
tx(s,'DataClawHub平台运营方案\n气象物流风险预警与应对决策',68,414,1050,105,30,C.white);
tx(s,'北京物资学院  /  单人主讲  /  6分钟',68,586,1060,42,24,'#BDCBD7');

s=base(2);tx(s,'赛题一',64,174,500,52,34,C.teal,true);tx(s,'让用户理解平台并完成首次实践',64,239,525,90,33,C.ink,true);
tx(s,'四类用户画像\n运营路径与3000元预算假设\n可调漏斗与实验验证',64,364,530,153,29);
rect(s,630,170,1,387,C.rule);tx(s,'赛题二',686,174,500,52,34,C.teal,true);tx(s,'把天气预警转成可比较的方案',686,239,525,90,33,C.ink,true);
tx(s,'订单与模拟有向网络\n风险评分与四类运输方案\n固定方案配对压力回放',686,364,525,153,29);
foot(s,'连接点：用真实开发的物流案例承接运营体验，推广效果仍待真实数据验证。');

s=base(3);tx(s,'React + TypeScript',64,169,530,54,36,C.teal,true);tx(s,'页面交互、输入与可视化',64,227,530,44,28);tx(s,'REST API',64,304,530,46,32,C.muted,true);
tx(s,'FastAPI + Pydantic',64,385,530,52,36,C.teal,true);tx(s,'输入校验、增长与风险计算',64,446,530,44,28);
tx(s,'SQLite',735,169,440,52,36,C.teal,true);tx(s,'订单  任务  参数  报告\n保存输入快照，可追溯复查',735,233,466,105,28);
tx(s,'图算法与规则',735,391,440,52,36,C.teal,true);tx(s,'核心计算本地完成\n模型接口仅用于可选解释',735,453,466,100,28);
foot(s,'实际数据流：前端提交 → 后端校验与计算 → SQLite持久化 → 返回结果。');

s=base(4);table(s,[['用户','主要需求','拟议验证'],['大学生','低门槛上手与课程作品','8名学生访谈'],['AI开发者','复现样本与技术证据','方法与代码审阅'],['物流从业者','约束与方案取舍','业务流程访谈'],['数据从业者','来源与指标口径','数据字典审阅']],64,162,1152,365,[205,495,452],27);
tx(s,'画像来自方案研究，尚未完成真实访谈。',64,556,1130,47,30,C.teal,true);foot(s,'页面：/growth → 用户与运营策略。来源：当前网站内容与运营说明书。');

s=base(5);tx(s,'拉新与激活',64,164,580,47,33,C.teal,true);tx(s,'暴雨冷链问题吸引兴趣\n完成一次计算并查看报告',64,225,560,103,29);
tx(s,'留存与推荐',64,360,580,47,33,C.teal,true);tx(s,'D1答疑  D3约束挑战  D7复盘\n同题不同解，邀请同学复现',64,421,560,103,29);
table(s,[['资源','预算 / 元'],['校园社群','600'],['内容平台','800'],['开发者社区','400'],['校园活动','1000'],['AI制作','200'],['合计','3000']],696,164,520,376,[325,195],25);
foot(s,'预算、发布与合作均为拟议方案；案例完成、外链点击和官方注册分别统计。');

s=base(6);await picture(s,'docs/phase4/growth-demo.png',64,160,805,435,'真实网站可调漏斗，访问率20%，访问2400，独立曝光12000');
tx(s,'现场修改并保存',903,170,310,62,31,C.teal,true);tx(s,'校园预算\n600 → 900元\n\n访问率\n12% → 20%',903,250,300,230,28);
tx(s,'总预算3300元\n访问量2400次',903,516,300,80,29,C.ink,true);
foot(s,'真实截图：独立曝光模型；默认激活201.60。渠道模型另算CAC，覆盖未去重。');

s=base(7);table(s,[['假设分组','访问 / 人','完成 / 人','完成率'],['A组','200','30','15%'],['B组','200','40','20%']],64,173,690,210,[220,155,155,160],26);
tx(s,'p = 0.18821',823,179,390,65,39,C.teal,true);tx(s,'95%近似区间\n−2.431 至 12.431\n个百分点',823,278,390,143,29);
tx(s,'当前不能判断B组胜出',64,453,1130,63,41,C.ink,true);tx(s,'下一步：随机分流、固定指标与分析时点；样本量示例约800人/组。',64,545,1150,62,26);
foot(s,'实际后端计算的假设示例，非真实推广结果；需满足独立随机分组与近似条件。');

s=base(8);await picture(s,'docs/phase3/logistics-weather.png',64,160,800,430,'真实网站截图：暴雨场景的模拟运输网络与订单输入');
tx(s,'6 条订单',902,166,310,61,39,C.teal,true);tx(s,'7 个节点\n10 条有向连接',902,258,310,104,30);
tx(s,'天气时间窗\n货物敏感度\n到货时限与载重',902,419,310,145,28);
foot(s,'真实页面 /logistics。图和业务数据为教学模拟，连线表示拓扑，预警不等于封路。');

s=base(9);tx(s,'读取任务   读取天气与网络   识别风险',64,160,1140,50,30,C.teal,true);tx(s,'枚举可达路线   生成并评分   输出建议',64,218,1140,50,30,C.teal,true);
await picture(s,'docs/phase4/agent.png',64,294,760,294,'真实网站六步工具轨迹与规则解释');
tx(s,'算法决定数值',871,307,340,56,33,C.ink,true);tx(s,'图搜索、约束检查\n归一化与权重评分',871,377,340,93,27);
tx(s,'当前为规则模式\n真实模型调用未验证',871,503,340,86,27,C.teal,true);
foot(s,'工具输入输出和报告快照支持追溯；可选模型文字仍需核对算法表格。');

s=base(10);table(s,[['方案','时长 / h','成本 / 元','延误 / h','风险分'],...audit.analysis.plans.map(p=>[p.name,p.hours.toFixed(2),p.cost.toFixed(2),p.delay_hours.toFixed(2),p.risk.toFixed(2)])],64,164,1152,280,[300,185,230,230,207],25);
tx(s,'默认推荐经廊坊绕行',64,481,1120,56,37,C.teal,true);tx(s,'比暴雨原计划少115.01元  /  比无天气基准多62元',64,557,1140,47,28);
foot(s,'模拟SR-001冷链8吨，承诺13:35，权重成本/时间/风险=25/35/40；风险分非事故概率。');

s=base(11);const sims=['normal','rain','snow'].map(id=>audit.simulations[id]);
const chart=s.charts.add('bar',{position:{left:64,top:163,width:668,height:367},title:'模拟准时占比',titleTextStyle:{typeface:font,fontSize:26,fill:C.ink},categories:['正常','暴雨','暴雪大风'],series:[{name:'原计划',values:sims.map(a=>Number((a.before.on_time_rate/100).toFixed(4))),fill:'#95A6B4'},{name:'推荐方案',values:sims.map(a=>Number((a.after.on_time_rate/100).toFixed(4))),fill:C.teal}],barOptions:{direction:'column',grouping:'clustered',gapWidth:120},hasLegend:true,legend:{position:'bottom',textStyle:{typeface:font,fontSize:21,fill:C.ink}},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{typeface:font,fontSize:19,fill:C.muted},majorGridlines:{fill:C.rule,width:1}},xAxis:{textStyle:{typeface:font,fontSize:22,fill:C.ink}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.##%',textStyle:{typeface:font,fontSize:21,fill:C.ink}},chartFill:C.paper,plotAreaFill:C.paper});
applyPresentationChartFont(chart,{fontFamily:font});
table(s,[['天气','原成本/元','推荐成本/元'],...sims.map((a,i)=>[['正常','暴雨','暴雪'][i],a.before.total_cost.toFixed(2),a.after.total_cost.toFixed(2)])],775,183,441,241,[113,164,164],22);
tx(s,'正常成本增加68元\n暴雪平均延误仍0.1569h',775,461,450,100,26,C.orange,true);
tx(s,'6订单 × 3固定严重度 = 每侧18样本，名义天气先选定方案，扰动时不重选。',64,567,1150,42,24);
foot(s,'教学压力情景统计，非历史实绩；成本为三情景总额均值，高风险按名义场景计数。');

s=base(12,true);tx(s,'运营假设可以改\n运输取舍可以算\n计算依据可以查',64,166,670,239,48,C.white,true);
tx(s,'实际交付',814,174,390,56,33,C.green,true);tx(s,'完整本地网站\n2份说明书\n2个170秒参赛视频',814,252,390,148,30,C.white);
tx(s,'下一步：真实访谈、官方网络、天气与位置数据，再校准模型。',64,470,1130,100,30,'#BDCBD7');
tx(s,'谢谢  请老师提问',64,598,950,51,35,C.green,true);

await fs.writeFile(path.join(ROOT,'docs/phase4/slide-geometry.json'),JSON.stringify(frames,null,2));
const candidate=path.join(build,'candidate.pptx');await(await PresentationFile.exportPptx(pres)).save(candidate);
const final=path.join(ROOT,'deliverables/phase4/人工智能导论_双赛题结课作品展示.pptx');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:final,pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[4,5,7,10,11],requiredNativeChartOwnerSlides:[11],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},layoutArgs:['--expected-slide-size-emu','12192000,6858000',...[4,5,7,10,11].flatMap(n=>['--require-native-table-slide',String(n)])],receiptPath:path.join(ROOT,'docs/phase4/pptx-validation.json')});
console.log(JSON.stringify(result));
// The final PPTX is independently rendered through the isolated local LibreOffice.
console.log('Exported 12-slide classroom deck');
