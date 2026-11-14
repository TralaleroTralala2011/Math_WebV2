"""Read-only V59 overlay with atomic SHA-verified restoration.

All source V254/B56 databases remain untouched. On ephemeral Render instances
this overlay may be reconstructed from its checked-in seed ZIP.
"""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import tempfile
import threading
import zipfile
from pathlib import Path

_STORAGE = Path(__file__).resolve().parents[1] / 'storage'
_LOCK = threading.Lock()
_READY = False


def ensure_v59_bank():
    global _READY
    path = _STORAGE/'v59_screened_additions.sqlite'
    manifest_path = _STORAGE/'v59_screened_additions_manifest.json'
    seed_path = _STORAGE/'v59_screened_additions.seed.zip'
    with _LOCK:
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf8'))
            if _READY and path.is_file():
                return path
            if path.is_file() and path.stat().st_size == manifest.get('bytes') and hashlib.sha256(path.read_bytes()).hexdigest() == manifest.get('sha256'):
                with sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True) as conn:
                    if conn.execute('PRAGMA quick_check').fetchone()[0] == 'ok':
                        _READY = True
                        return path
            if not seed_path.is_file():return None
            tmp=None
            try:
                sha=hashlib.sha256();total=0
                with zipfile.ZipFile(seed_path) as z:
                    if z.namelist()!=['v59_screened_additions.sqlite']:return None
                    with z.open('v59_screened_additions.sqlite') as source, tempfile.NamedTemporaryFile(
                        dir=_STORAGE, prefix='.v59-', suffix='.sqlite', delete=False
                    ) as target:
                        tmp=target.name
                        for chunk in iter(lambda:source.read(1024*1024),b''):
                            target.write(chunk);sha.update(chunk);total+=len(chunk)
                if total!=manifest['bytes'] or sha.hexdigest()!=manifest['sha256']:return None
                with sqlite3.connect(f'file:{tmp}?mode=ro',uri=True) as conn:
                    if conn.execute('PRAGMA quick_check').fetchone()[0]!='ok':return None
                os.replace(tmp,path);tmp=None;_READY=True
                return path
            finally:
                if tmp:
                    try:os.unlink(tmp)
                    except OSError:pass
        except (OSError,KeyError,TypeError,ValueError,sqlite3.Error,zipfile.BadZipFile):return None
