const { app, BrowserWindow, dialog, session, shell } = require('electron');
const { spawn } = require('node:child_process');
const { randomBytes } = require('node:crypto');
const path = require('node:path');
const fs = require('node:fs');

app.setName('SkyRouteAI');
const dataRoot = path.join(process.env.LOCALAPPDATA || path.join(app.getPath('appData'), '..', 'Local'), 'SkyRouteAI');
fs.mkdirSync(dataRoot, { recursive: true });
app.setPath('userData', dataRoot);
let backend, window, quitting = false, base;
const token = randomBytes(32).toString('hex');
const ownsLock = app.requestSingleInstanceLock();
if (!ownsLock) app.quit();
else {
  app.on('second-instance', () => { if (window) { window.restore(); window.show(); window.focus(); } });
  app.whenReady().then(start).catch(fail);
}

function fail() {
  dialog.showErrorBox('SkyRoute AI 启动失败', '本地服务未能启动。请检查用户数据目录是否可写，或关闭程序后重试。程序不会自动删除已有数据库。');
  app.quit();
}

async function start() {
  fs.mkdirSync(dataRoot, { recursive: true });
  const env = {};
  for (const key of ['SystemRoot', 'WINDIR', 'TEMP', 'TMP', 'LOCALAPPDATA', 'APPDATA', 'USERPROFILE', 'COMSPEC']) {
    if (process.env[key]) env[key] = process.env[key];
  }
  env.PATH = path.join(process.env.SystemRoot || 'C:\\Windows', 'System32');
  env.SKYROUTE_DB = path.join(dataRoot, 'skyroute.db');
  env.SKYROUTE_DESKTOP_TOKEN = token;
  env.PYTHON_DOTENV_DISABLED = '1';
  const executable = path.join(process.resourcesPath, 'backend', 'skyroute-service.exe');
  backend = spawn(executable, [], { cwd: dataRoot, env, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'] });
  const port = await new Promise((resolve, reject) => {
    let text = '';
    const timer = setTimeout(() => reject(new Error('startup timeout')), 40000);
    backend.once('error', reject);
    backend.once('exit', () => { clearTimeout(timer); reject(new Error('service exited')); });
    backend.stdout.on('data', chunk => {
      text += chunk.toString();
      const lines = text.split('\n'); text = lines.pop();
      for (const line of lines) {
        try {
          const message = JSON.parse(line);
          if (message.event === 'ready' && Number.isInteger(message.port)) {
            clearTimeout(timer); resolve(message.port);
          }
        } catch { /* Readiness uses an explicit JSON message only. */ }
      }
    });
    // Consume diagnostic output without persisting developer paths or secrets.
    backend.stderr.on('data', () => {});
  });
  base = `http://127.0.0.1:${port}`;
  const local = session.fromPartition('skyroute-local');
  local.setPermissionRequestHandler((_webContents, _permission, callback) => callback(false));
  local.setPermissionCheckHandler(() => false);
  local.webRequest.onBeforeSendHeaders((details, callback) => {
    if (details.url.startsWith(base + '/')) {
      details.requestHeaders['X-SkyRoute-Session'] = token;
      callback({ requestHeaders: details.requestHeaders });
    } else callback({ cancel: true });
  });
  window = new BrowserWindow({
    width: 1440, height: 960, minWidth: 960, minHeight: 640,
    show: false, backgroundColor: '#f3f5f4', title: 'SkyRoute AI', autoHideMenuBar: true,
    webPreferences: { session: local, nodeIntegration: false, contextIsolation: true,
      sandbox: true, webSecurity: true, devTools: false, spellcheck: false },
  });
  window.removeMenu();
  window.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(base + '/')) event.preventDefault();
  });
  window.webContents.setWindowOpenHandler(({ url }) => {
    // Only explicit user link actions may open a normal HTTPS source page.
    if (url.startsWith('https://')) void shell.openExternal(url);
    return { action: 'deny' };
  });
  window.once('ready-to-show', () => window.show());
  backend.on('exit', () => { if (!quitting) fail(); });
  await window.loadURL(base + '/');
}

app.on('window-all-closed', () => app.quit());
app.on('before-quit', event => {
  if (!backend || backend.exitCode !== null || quitting) return;
  event.preventDefault(); quitting = true;
  const timer = setTimeout(() => { backend.kill(); app.exit(0); }, 6000);
  backend.once('exit', () => { clearTimeout(timer); app.exit(0); });
  backend.stdin.on('error', () => {});
  backend.stdin.end('shutdown\n');
});
