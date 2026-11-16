# Prepared specification: build only after the privacy and font gates pass.
from pathlib import Path
import importlib.metadata
import sys

root = Path(SPECPATH).parent
license_data = [(str(Path(sys.base_prefix) / 'LICENSE.txt'), 'licenses/python')]
for line in (root / 'backend/requirements.lock.txt').read_text().splitlines():
    if not line or line.startswith('#') or '==' not in line:
        continue
    distribution = importlib.metadata.distribution(line.split('==')[0])
    for item in distribution.files or []:
        if item.name.lower().startswith(('license', 'copying')):
            license_data.append((str(distribution.locate_file(item)), 'licenses/' + distribution.metadata['Name']))
analysis = Analysis(
    [str(root / 'desktop/backend_entry.py')],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / 'frontend/dist'), 'frontend/dist'), *license_data],
    hiddenimports=['backend.main', 'uvicorn.logging', 'uvicorn.loops.auto',
                   'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets.auto',
                   'uvicorn.lifespan.on'],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['pytest', 'tkinter'], noarchive=False,
)
pyz = PYZ(analysis.pure)
executable = EXE(pyz, analysis.scripts, [], exclude_binaries=True,
                 name='skyroute-service', debug=False, strip=False, upx=False,
                 console=True, disable_windowed_traceback=False)
collect = COLLECT(executable, analysis.binaries, analysis.datas,
                  strip=False, upx=False, name='skyroute-service')
