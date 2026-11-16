param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
function Checked([string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Build step failed: $Program" }
}
$review = Get-Content -LiteralPath (Join-Path $projectRoot 'privacy-decision.json') -Raw | ConvertFrom-Json
if (-not $review.personal_information_decided -or -not $review.font_redistribution_authorized) {
    throw 'Public build requires recorded privacy and font redistribution decisions.'
}
Checked $Python @('-m', 'venv', '.tools/phase5/build-venv')
$buildPython = Join-Path $projectRoot '.tools/phase5/build-venv/Scripts/python.exe'
Checked $buildPython @('-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'backend/requirements.lock.txt', '-r', 'desktop/requirements-build.txt')
Push-Location frontend
try {
    Checked 'npm.cmd' @('ci', '--no-audit', '--no-fund')
    Checked 'npm.cmd' @('run', 'typecheck')
    Checked 'npm.cmd' @('run', 'build')
} finally { Pop-Location }
Checked $buildPython @('-m', 'PyInstaller', '--noconfirm', '--clean', '--distpath', '.tools/phase5/pyinstaller-dist', '--workpath', '.tools/phase5/pyinstaller-build', 'desktop/skyroute-service.spec')
Push-Location desktop
try {
    Checked 'npm.cmd' @('ci', '--no-audit', '--no-fund')
    Checked 'node.exe' @('node_modules/electron/install.js')
    Checked 'npm.cmd' @('run', 'build:portable')
} finally { Pop-Location }
$exe = Join-Path $projectRoot '.tools/phase5/electron-dist/SkyRoute-AI-v1.0.0-Windows-x64.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Portable EXE missing' }
$sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $exe).Hash.ToLowerInvariant()
Write-Output "Built SkyRoute-AI-v1.0.0-Windows-x64.exe SHA256=$sha"
