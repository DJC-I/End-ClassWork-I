# 第五阶段安全检查

2026-11-16，本机Windows x64。没有关闭或改变系统安全功能。

## 依赖修复及复验

依赖扫描发现旧AnyIO/Starlette以及构建链minimatch的已知问题，已将后端锁定至AnyIO 4.14.2、Starlette 1.3.1；Electron 45.3.3、electron-builder 26.18.0及minimatch override 11.0.1。修复后重新执行业务回归。

`backend-dependency-audit-final.json`覆盖25个Python依赖、0条已知漏洞；前端生产及全依赖npm audit均0；桌面构建链npm audit为0。检查受当前漏洞库范围限制，不等同于未来持续无漏洞。pip check通过。

## 本地服务边界

随机端口只绑定127.0.0.1；随机会话头、Host/Origin验证、CSP、无调试文档；Electron sandbox/contextIsolation开启，nodeIntegration/DevTools关闭。请求限制同源，外部HTTPS来源页仅由用户显式链接操作打开。默认不调用外部模型，不内置密钥、不读取开发.env；父进程关闭后服务退出，用户数据写LOCALAPPDATA。

新增真实子进程测试验证未授权、错误Host/Origin、调试路由、授权API、SQLite首次初始化、跨进程重启与退出。桌面20组工作流补充真实UI、业务链路和无外网业务请求检查。

## 资源与隐私

ASAR仅包含main.cjs与package.json，与已审计源码字节相同；Python包检查23534个代码对象及130项资源，没有开发者私人路径、.env、原业务数据库或开发缓存。上游标准库公共文档示例和公共CI通用账户按来源归类。

最终portable解包203个文件，与通过业务测试的win-unpacked载荷逐文件SHA-256完全一致。x64 Electron和Python载荷真实存在。公开副本按P001至P004决定脱敏，原件保留；旧本地私人Git历史不推送，保留已有远端公开提交。完整扫描与Office/视频范围见根目录PRIVACY_REVIEW.md。

未进行商业代码签名、动态恶意软件沙箱或所有第三方二进制的逐函数审计；不由SHA匹配推导绝对安全。运行时许可随包保留，下载后应核对SHA256SUMS。
