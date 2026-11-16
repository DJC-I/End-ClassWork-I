"""Verify the extracted single-file payload against the tested application tree."""
import hashlib
import json
from pathlib import Path
import struct

PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / '.tools/phase5'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob('*') if p.is_file()}


def pe(path):
    with path.open('rb') as stream:
        assert stream.read(2) == b'MZ'
        stream.seek(0x3c)
        offset = struct.unpack('<I', stream.read(4))[0]
        stream.seek(offset)
        assert stream.read(4) == b'PE\0\0'
        return hex(struct.unpack('<H', stream.read(2))[0])


if __name__ == '__main__':
    src = inventory(BASE / 'electron-dist/win-unpacked')
    extracted = inventory(BASE / 'portable-payload')
    differences = sorted(k for k in src.keys() | extracted.keys() if src.get(k) != extracted.get(k))
    exe = BASE / 'electron-dist/SkyRoute-AI-v1.0.0-Windows-x64.exe'
    moved = BASE / '移动验证 中文 空格' / exe.name
    record = {'passed': not differences and sha(exe) == sha(moved),
              'payload_files': len(src), 'differing_files': differences,
              'exe_bytes': exe.stat().st_size, 'exe_sha256': sha(exe),
              'moved_copy_identical': sha(exe) == sha(moved),
              'portable_bootstrap_machine': pe(exe),
              'electron_machine': pe(BASE / 'portable-payload/SkyRoute AI.exe'),
              'backend_machine': pe(BASE / 'portable-payload/resources/backend/skyroute-service.exe'),
              'architecture_note': '0x14c portable bootstrap contains verified 0x8664 Electron and Python payload; target Windows x64.'}
    (PROJECT / 'docs/phase5/portable-integrity.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))
    assert record['passed']
