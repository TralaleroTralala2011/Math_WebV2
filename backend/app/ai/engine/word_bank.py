"""Integrity-checked, read-only Word V60 candidate overlay.

Restore is atomic and never changes user data or existing V254/V59 banks.
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

DIR=Path(__file__).resolve().parents[1] / 'storage'
_LOCK=threading.Lock()


def ensure_word_bank():
    target=DIR / 'v60_word_candidates.sqlite'
    seed=DIR / 'v60_word_candidates.seed.zip'
    manifest_file=DIR / 'v60_word_manifest.json'
    if not seed.is_file() or not manifest_file.is_file():return None
    try:
        manifest=json.loads(manifest_file.read_text(encoding='utf8'))
    except (OSError,ValueError):return None
    expected_bytes=manifest.get('db_bytes')
    expected_sha=manifest.get('db_sha256')
    if not isinstance(expected_bytes,int) or not isinstance(expected_sha,str):return None

    def intact(path):
        try:
            if not path.is_file() or path.stat().st_size!=expected_bytes:return False
            h=hashlib.sha256()
            with path.open('rb') as handle:
                for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
            if h.hexdigest()!=expected_sha:return False
            with sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True) as db:
                return db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
        except (sqlite3.Error,OSError):return False
    if intact(target):return target
    with _LOCK:
        if intact(target):return target
        tmp=None
        try:
            with zipfile.ZipFile(seed) as z:
                if z.namelist()!=['v60_word_candidates.sqlite']:return None
                digest=hashlib.sha256();size=0
                with z.open('v60_word_candidates.sqlite') as source, tempfile.NamedTemporaryFile(
                    prefix='.word-v60-',suffix='.sqlite',dir=DIR,delete=False
                ) as out:
                    tmp=Path(out.name)
                    for chunk in iter(lambda:source.read(1024*1024),b''):
                        out.write(chunk);digest.update(chunk);size+=len(chunk)
            if size != expected_bytes or digest.hexdigest() != expected_sha:return None
            with sqlite3.connect(f'file:{tmp.as_posix()}?mode=ro',uri=True) as db:
                if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':return None
            os.replace(tmp,target);tmp=None
            return target
        except (OSError,sqlite3.Error,zipfile.BadZipFile,ValueError,KeyError):
            return None
        finally:
            if tmp is not None:
                try:tmp.unlink()
                except OSError:pass
