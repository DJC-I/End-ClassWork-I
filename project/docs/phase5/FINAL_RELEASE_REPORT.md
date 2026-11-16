# SkyRoute AI v1.0.0 最终发布与验收报告

核验日期：2026-11-16（UTC+8）。状态：源码、独立程序、三类材料ZIP和校验文件已正式发布，五项资产已通过实际公开下载复核。

## 源码与远端

- 仓库：https://github.com/DJC-I/End-ClassWork-I
- Release：https://github.com/DJC-I/End-ClassWork-I/releases/tag/v1.0.0
- 正式标签源码提交：`cb5c42d50c14d50238270d7a0c11b43935f6b7f7`。
- main后续仅追加发布结果与状态文档；正式标签保留原验收源码，不移动、不强制改写。
- 远端原始公开提交保留，旧本地私人历史未推送；新增通用项目署名。
- 手动Actions与v1.0.0标签Actions均成功；首次运行发现前端未先构建的顺序问题，修正后重新通过。

- push：https://github.com/DJC-I/End-ClassWork-I/actions/runs/43865136811（success；源码cb5c42d50c14d50238270d7a0c11b43935f6b7f7）。
- workflow_dispatch：https://github.com/DJC-I/End-ClassWork-I/actions/runs/43864370192（success；源码cb5c42d50c14d50238270d7a0c11b43935f6b7f7）。

## 发布资产

|公开下载名|字节|SHA-256|
|---|---:|---|
|SHA256SUMS.txt|423|`68e555048ccd3ac73a1dc7c0b94a9d3887dcd1674276c74a80897f875deb75f4`|
|SkyRoute-AI-v1.0.0-Campus-Submission.zip|31160226|`2d4240a30b2e06836ec6e26820dae1f38e92361ab6b7080b019b111575366015`|
|SkyRoute-AI-v1.0.0-Classroom-Presentation.zip|610145|`a358b051b532990e7b92f036094528f26aefc86e2d4c4d36d44a19dda4b112ea`|
|SkyRoute-AI-v1.0.0-Full-Delivery.zip|163444685|`ac155528fc725e87f73928d4b528ae8a460fb9032d4fca80cebe45622f7cbd95`|
|SkyRoute-AI-v1.0.0-Windows-x64.exe|131621358|`57ce5bb35bda4452680bf9c90733a255d90c36a2bfb23d225e6c1c9347b306b1`|

五项均通过实际公开下载、字节数和SHA-256核对；下载后的三个ZIP再次CRC校验通过。Release校验文件使用实际英文下载名。GitHub移除中文资产名称导致冲突，已采用唯一英文下载名与中文显示标签；本地正式ZIP及压缩包内部文件保留中文名称。

## 实际交付与测试

- EXE：Electron portable + 内置PyInstaller后端，131621358字节，无需外装Python/Node。203个解包文件与已测载荷一致；非管理员、最小PATH、中文空格移动路径和正常关闭实测。
- 后端30项、Edge业务4条、桌面业务20组通过；五路由实际自定义字体字形确认。安全升级后的依赖扫描已知漏洞为0。
- 两份赛事Word10/13页；两个视频170/175秒、1920×1080，中文自然合成女声与字幕，完整解码、21章节抽查。
- 课堂PPT12页及12页备注、单人讲稿8页1223字/360秒排期、答辩5页15问；操作与应急指南齐全。
- 本地完整目录`SkyRoute-AI-v1.0.0-Final/`共34文件，校园/课堂/Windows/开发/验收五类；三个ZIP CRC、包内33项哈希通过。源码以GitHub为准。

## 隐私与保全

- 首轮904工作文件、844本地可恢复Git对象；新增后复扫920工作文件；公开副本302文件项、最终目录及下载资产39文件项复扫均通过。
- P001个人路径改相对路径，P002 PPT作者Dux，P003保留既有公开署名和历史，P004公开XML设备名local-test；用户原件保留。字体已获明确公开再分发授权。
- 没有未解决隐私决定或检测到的待发布真实凭证。图像/音频检查范围有明确限制，不声称穷尽识别信息。
- 两Word/讲稿内容及PPT备注、图像保持；PPT仅核心作者属性改变。32项历史材料/数据库哈希保持，旧阶段文件未删除。

## 未验证范围与限制

未商业签名，可能出现SmartScreen信誉提示；未完成干净虚拟机、所有Windows版本、物理断网、Microsoft Office GUI、真人逐字听审、本人彩排或教室硬件验证。portable inspector直接附加超时已记录，完整自动化使用哈希一致载荷，单文件另做原生GUI。全部业务数据为教学模拟，真实天气、业务收益、官方路网与供应商模型调用未验收。

## 完成状态

- 已完成并验证：安全源码推送、Windows独立构建/关键运行测试、材料归档、隐私处理、两次Actions成功、正式v1.0.0、五资产公开下载哈希。
- 已完成但存在上述未验证范围：跨环境兼容、现场展示与完整人工媒体审听。
- 未完成的必需交付、等待隐私决定、工程阻塞：无。
- 发布后状态文档单独更新，不改变正式标签或已验证资产。
