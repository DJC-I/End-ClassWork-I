"""Shared classroom narrative, timed script, source notes and defense answers."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]; Q=R/'docs/phase4'; O=R/'deliverables/phase4'
Q.mkdir(parents=True,exist_ok=True); O.mkdir(parents=True,exist_ok=True)
def slide(title,seconds,spoken,cue,source,demo='本页不切换网站',pause=0):
 return dict(title=title,seconds=seconds,spoken=spoken,cue=cue,source=source,demo=demo,pause_seconds=pause)
slides=[
 slide('人工智能导论 双赛题结课作品展示',15,'老师、同学们好。我今天独立介绍SkyRoute AI。作品把平台运营方案和气象物流决策放在同一个网站中，重点说明做了什么、怎样计算，以及结果的适用范围。','介绍后翻至项目背景。','README.md；两份Word说明书'),
 slide('两个赛题 共用一个可体验的案例',20,'赛题一讨论怎样帮助用户理解并使用DataClawHub，赛题二讨论天气变化后的运输选择。我的连接点是一个可操作的物流案例：先让用户获得首次体验，再用预算和实验方法判断推广方案是否值得继续。','说完“继续”翻页。','backend/content.py；第二阶段运营说明书'),
 slide('前端交互 后端计算 本地保存',25,'网站前端使用React和TypeScript，负责页面、表格与图形。FastAPI校验输入并完成增长、风险和方案计算，SQLite保存订单、任务、参数和报告。报告保留当次输入快照，方便复查。核心流程可以离线运行，模型解释是可选项。','指向后端计算与SQLite，再翻页。','backend/main.py、db.py；frontend/src/App.tsx、api.ts'),
 slide('四类用户的需求与验证方式',25,'运营方案区分四类用户。学生需要低门槛上手，开发者需要代码和复现证据，物流从业者关注业务约束，数据从业者关注来源与口径。当前画像是研究假设，后续拟访谈八名同学，并邀请行业人员审阅流程，再修改内容和入口。','强调“拟访谈”，翻至运营方案。','backend/content.py personas；第二阶段运营说明书'),
 slide('先完成一次体验 再安排回访',30,'运营路径从暴雨冷链问题切入，引导用户完成计算并查看报告，再安排入门答疑、第三天挑战和第七天复盘。五类资源预算合计三千元，先做小范围验证。经费、合作和发布均是计划，尚未执行。案例完成与官方平台注册也要分别统计。','指预算表，翻页并准备第一次演示。','backend/content.py strategies；backend/seed.py GROWTH_CONFIG'),
 slide('增长模型支持修改参数并保存',40,'这里展示真实增长工作台。默认独立曝光一万二千次，预计激活二百零一点六人。现在把校园预算改为九百元，访问率改为百分之二十，访问量变为二千四百，预算变为三千三百元，保存后可以保留。渠道模型另算获客成本，覆盖没有去重，两个模型不能混用。','演示结束Alt+Tab返回PPT，再翻页。','backend/growth.py calculate；docs/phase4/demo-check.json；growth-demo.png','/growth → 预算与增长模型：校园社群预算600改900，访问率12改20，保存参数；观察访问2400与总预算3300。准备阶段先恢复这两个字段至600和12。',12),
 slide('A/B示例差异尚不显著',25,'实验示例中，两组各二百人，分别完成三十和四十人。差异虽然有五个百分点，但P值约零点一八八，置信区间跨零，不能宣布第二组胜出。后续需要随机分流、固定分析时点，并按目标差异估算样本量；第七天留存还需等待真实观察。','指出“不能宣布胜出”，转入物流赛题。','backend/growth.py experiment；docs/phase4/source-audit.json'),
 slide('天气信息需要落到具体订单',25,'物流场景的痛点是：看到天气预警之后，仍不知道哪些订单会延误，也难以比较提前、绕行和中转。网站用六条模拟订单、七个节点和十条有向连接说明这一过程。分析既看天气发生时间，也看货物敏感度、到货时限和单票载重约束。','指网络与订单，翻至工具流程。','backend/seed.py；docs/phase3/logistics-weather.png'),
 slide('六步工具链保留计算依据',30,'分析流程分六步，依次读取任务、读取天气与网络、识别风险、枚举可达路线、生成并评分、输出建议。数字来自图算法和规则。当前没有验证真实大模型调用，现场使用规则解释。保留工具输入输出，可以追溯推荐原因，也避免把一段流畅文字当成计算证据。','指规则模式，再翻页准备第二次演示。','backend/engine.py analyze；backend/main.py explain；docs/phase4/agent.png'),
 slide('暴雨冷链订单的四方案比较',40,'以一号冷链订单为例，暴雨下原计划风险四十七点一五分，延误约零点九八小时。运行分析后，默认权重推荐经廊坊绕行，用时二点九五小时，成本一千二百四十二元。相对受天气影响的原计划少约一百一十五元，但比无天气基准多六十二元。风险分只是规则量表。','返回PPT后指出两种成本基准，再翻页。','backend/engine.py；docs/phase4/source-audit.json analysis；plans.png','/logistics → 暴雨风险 → 选择SR-001 → 运行风险分析 → 四类应对策略。成本/时间/风险权重25/35/40；确认47.15、绕行、1242。',12),
 slide('固定方案压力回放保留成本代价',55,'仿真先在名义天气下选定方案，再固定方案，用零点八五、一和一点一五三档严重度配对回放，每侧十八个样本。暴雨准时占比从百分之三十八点八九变为百分之一百，暴雪从百分之二十二点二二变为百分之六十六点六七，暴雪仍有延误。正常天气准时占比不变，总成本增加六十八元，说明推荐体现权重取舍。这里的准时占比和费用都是模型压力情景统计，不能当作真实业务收益。','留出读图停顿，最后翻至总结。','backend/engine.py simulate；docs/phase4/source-audit.json simulations','本页默认使用PPT静态结果；答辩可进入/logistics，分别选三场景并点击运行情景仿真。',3),
 slide('可复现的双赛题作品与下一步',30,'这次作品的价值，是把运营假设、可执行的物流案例和可追溯计算放到一起。前三阶段已有网站、两份说明书和两个视频，第一阶段记录了二十八项后端测试与四条浏览器流程通过。下一步需要真实访谈、官方网络、天气和位置数据，再校准模型。我希望先把边界讲清楚，再讨论实际应用。谢谢，请老师提问。','停留此页答辩；不继续第五阶段。','docs/PHASE1_ACCEPTANCE.md；docs/PHASE2_ACCEPTANCE.md；docs/PHASE3_ACCEPTANCE.md')
]
questions=[
 ('没有调用大模型 为什么称为AI项目','本作品把知识规则、图搜索、多目标评分与工具流程用于决策支持，属于可解释的教学实现。当前真实运行的是规则模式。兼容模型接口仅用于解释计算快照，真实供应商调用尚未验证，不能宣称训练了模型或获得大模型推理效果。','backend/engine.py；backend/main.py /api/agent/explain'),
 ('风险分怎样算 能解释为事故概率吗','严重度按降雨、降雪、风速、能见度和低温计算。逐段结合通行时间窗与天气重叠，再叠加货物敏感度、延误和优先级。风险公式为min(100,5+65×时长加权暴露×敏感度+20×min(延误h/2,1)+3×(优先级−1))。系数为教学设定，风险分尚未校准，不能解释成事故概率。','backend/engine.py severity、evaluate、analyze'),
 ('推荐路线是全局最优吗','当前只对小型有向图枚举可达简单路线，检验连接、可用状态与单票运力。先在策略类别内选代表，再对四类候选的成本、时长、风险做min-max归一化和加权评分，越低越好。结果受候选集和权重影响，不能声称真实大规模运输网络的全局最优。','backend/engine.py routes、generate、rank'),
 ('为什么绕行更便宜 额外成本又增加','暴雨SR-001原计划受天气影响的成本为1357.01元，绕行1242元，少115.01元。无天气原计划基准为1180元，绕行比该基准多62元。两句话比较的基准不同，报告应同时给出。费用来自配置里程、通行费、策略费用与天气时间成本。','docs/phase4/source-audit.json analysis'),
 ('为什么正常天气优化后反而贵','默认权重成本0.25、时长0.35、风险0.40，不是只追求最低费用。正常场景中某单选择更短时长的绕行，模拟总成本6740元变为6808元。增加68元是需要保留的代价；实际采用前应让调度员确认权重和预算。','backend/engine.py rank；source-audit.json simulations.normal'),
 ('仿真是否存在事后挑选最优的偏差','程序先在名义天气下确定方案，再固定路径与发运时间，在0.85、1、1.15倍严重度下回放，不随扰动重新选择。六订单乘三档共18个样本每侧，属于配对压力场景，不是随机抽样、蒙特卡洛估计或真实准时概率。固定压力场景也不能证明对未见天气有效。','backend/engine.py simulate'),
 ('数据真实可靠吗 官方路网拿到了吗','本地订单、连接、里程、运力、费用和天气全部为教学模拟，图形是拓扑示意。官方工具包下载控件没有可用href，尚未取得指定网络。网站截图与算法运行真实存在，但截图中的业务数据仍是模拟，不能混淆这两个层次。','README.md；docs/OFFICIAL_REVIEW.md；backend/seed.py'),
 ('为什么不能说用户增长了432人','432.51是渠道预算与CPM推算覆盖量后，乘访问、注册、激活率得到的假设期望量。覆盖量未去重，也没有真实平台注册授权数据。独立曝光漏斗的激活201.60来自另一套曝光假设。当前没有真实投放、访谈、注册、合作或留存效果。','backend/growth.py calculate；backend/content.py'),
 ('A/B提升五个百分点 为什么不采用B','A为30/200等于15%，B为40/200等于20%。双侧两比例z检验p=0.18821，95%近似区间为[-2.431,12.431]个百分点，跨过零，因此没有足够证据判断差异。独立随机分组和固定样本是前提；以15%基线、5个百分点MDE和80%功效粗估每组800人，仍需按真实设计复核。','backend/growth.py experiment'),
 ('怎样验证画像与运营方案','拟先访谈八名学生，记录上手障碍，再用单一主指标开展文案或上手清单实验。案例激活定义为完成一次计算并查看报告，外链点击、官方注册需分别统计。采用同意后的匿名汇总数据；D7回访到期后再判断留存，未执行内容不写成已完成。','backend/content.py personas、experiments、strategies'),
 ('运输中订单还能提前发运吗','不能。程序对运输中订单禁用提前发运。由于没有实时位置，绕行或中转仅作原始计划级反事实比较，不能直接下发调度。运力也只核验单票，不计算多个订单同时占用车队容量。真实应用需接入位置、时窗、司机、车辆和共享运力。','backend/engine.py generate；README.md 数据与算法边界'),
 ('如何防止模型编造数字和泄露密钥','核心数字先由后端确定，模型只收到计算快照并生成解释，前端仍展示算法表格。密钥只在后端环境配置，缺密钥直接规则模式，请求失败返回规则降级。提示约束不能保证模型永不编造，仍需核对输出且不能据文字自动执行运输。真实接口和隐私治理还需进一步验证。','backend/main.py explain；.env.example'),
 ('系统怎样保存数据 测试做到了哪一步','SQLite存储订单、任务、参数和报告，输入通过Pydantic校验，批量导入事务回滚。第一阶段记录28项pytest、4条Edge流程及重启持久化通过。第四阶段重算数据并在隔离数据库复验两条展示流程，未重跑全套测试。不能把这些测试等同生产稳定性、并发容量或所有教室设备兼容。','docs/PHASE1_ACCEPTANCE.md；docs/phase4/demo-check.json'),
 ('网站或网络不可用怎么办','已安装依赖和前端构建时，核心本地规则流程无需外网。提前打开PPT、网站和本地视频。网站10秒内恢复不了就返回第6、10、11页截图与数据讲解，不在课堂安装依赖。视频可作为已有录制证据，播放前明确说明；6分钟内不完整播放两个170秒视频。','演示操作清单.md'),
 ('怎样应用到真实物流业务','先取得授权路网与天气观测，接入订单、位置、运力及道路可用性，再用历史样本校准延误和风险，进行时间外验证与人工试用。还需鉴权、审计、备份、并发控制和异常处置。现阶段展示的是可复现原型，尚无真实降本收益或生产部署证据。','README.md；第二阶段物流说明书 局限性与未来方向')
]
elapsed=0
for s,seconds in zip(slides,[19,25,28,25,26,41,25,25,28,41,44,33]):s['seconds']=seconds
for i,s in enumerate(slides,1):
 s['number']=i;s['start_seconds']=elapsed;elapsed+=s['seconds'];s['end_seconds']=elapsed
 s['spoken_characters']=len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s['spoken']))
assert elapsed==360
payload={'phase':4,'slides':slides,'questions':[{'number':i,'question':q,'answer':a,'source':src} for i,(q,a,src) in enumerate(questions,1)],'seconds':elapsed,'spoken_characters':sum(s['spoken_characters'] for s in slides),'character_definition':'仅逐字稿的汉字、字母和数字，不含标点、空格、操作与翻页提示','reserved_seconds':sum(s['pause_seconds'] for s in slides)}
(Q/'content.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k not in ['slides','questions']},ensure_ascii=False))
