"""Additive, read-only B56 bank overlay. Preserves the existing V254 SQLite bank."""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import tempfile
import threading
import zipfile
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / 'storage'
LOCK = threading.Lock()


def ensure_b56_bank():
    target = DIR / 'v254_b56_candidates.sqlite'
    seed = DIR / 'v254_b56_candidates.seed.zip'
    manifest = DIR / 'v254_b56_seed_manifest.json'
    if target.is_file() and target.stat().st_size > 0:
        return target
    with LOCK:
        if target.is_file() and target.stat().st_size > 0:
            return target
        if not seed.is_file() or not manifest.is_file():
            return None
        tmp = None
        try:
            expected = json.loads(manifest.read_text(encoding='utf8'))
            with zipfile.ZipFile(seed) as z:
                if z.namelist() != ['v254_b56_candidates.sqlite']:
                    return None
                digest = hashlib.sha256()
                size = 0
                with z.open('v254_b56_candidates.sqlite') as source, tempfile.NamedTemporaryFile(
                    dir=DIR, prefix='.b56-', suffix='.sqlite', delete=False
                ) as destination:
                    tmp = destination.name
                    for chunk in iter(lambda: source.read(1024 * 1024), b''):
                        size += len(chunk)
                        digest.update(chunk)
                        destination.write(chunk)
            if size != expected['bytes'] or digest.hexdigest() != expected['sha256']:
                return None
            with sqlite3.connect(f'file:{tmp}?mode=ro', uri=True) as con:
                if con.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    return None
            os.replace(tmp, target)
            tmp = None
            return target
        except (OSError, ValueError, KeyError, sqlite3.Error, zipfile.BadZipFile):
            return None
        finally:
            if tmp:
                try: os.unlink(tmp)
                except OSError: pass
