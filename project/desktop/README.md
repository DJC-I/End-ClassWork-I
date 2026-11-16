# Windows独立桌面程序

状态：用户隐私决定和字体公开分发授权已记录；已真实生成Windows x64独立EXE，详细发布状态以第五阶段验收和远端核验报告为准。

方案：Electron内置Chromium + electron-builder portable外壳 + PyInstaller onedir Python业务服务。单个可分发EXE运行时允许自动解压；无需用户安装Python、Node或WebView运行时。已评估pywebview，但它依赖系统WebView运行时，当前采用Electron以减少外部运行环境前提。

`backend_entry.py`不改变业务算法，使用操作系统分配的本机端口、每次启动随机会话令牌、Host/Origin检查、关闭调试文档、CSP和标准输入关闭协议。`main.cjs`限制渲染器权限、阻止应用内外部导航、禁止DevTools、单实例与隐藏子进程窗口。后端资源只允许包含生产前端及必要Python模块，不能包含开发数据库、.env、测试证据或私人文件。

数据库使用`%LOCALAPPDATA%/SkyRouteAI/skyroute.db`；由原业务初始化代码首次生成。第二次启动不得重置。测试应使用独立数据目录，不能覆盖现有数据库。

锁定Electron 45.3.3、electron-builder 26.18.0、PyInstaller 6.22.3与Python 3.12。执行`powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`后，输出`.tools/phase5/electron-dist/SkyRoute-AI-v1.0.0-Windows-x64.exe`。首次构建需要网络。`node scripts/test_desktop_phase5.cjs`验证完整桌面业务，`node scripts/audit_desktop_resources.cjs`检查ASAR。必要运行时许可随包保留。

portable外壳为32位启动器，内含64位Electron与Python载荷，目标Windows x64。已解包203个文件，与通过20组业务检查的win-unpacked应用逐文件SHA-256一致。单文件外壳不能直接用Playwright的Electron inspector启动协议附加，另用原生Windows GUI核验；该工具适配失败不计为通过。完整证据见`../docs/phase5/FUNCTIONAL_TEST_REPORT.md`。

没有商业代码签名，可能出现SmartScreen信誉提醒；无需关闭Defender。没有干净虚拟机、所有Windows版本或物理断网认证；最小PATH与无外网业务请求检查不等同于上述认证。
