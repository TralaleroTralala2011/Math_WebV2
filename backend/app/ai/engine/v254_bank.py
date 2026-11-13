"""Safe, on-demand restore for the VERSIONED, read-only V254 candidate bank.

The checked-in ZIP is the source of truth. This does not touch user accounts or
production data. The same manifest/checksum is used by scripts/restore_v254_bank.py.
"""
import hashlib
import json
import os
import tempfile
import threading
import zipfile
from pathlib import Path

_BANK_DIR = Path(__file__).resolve().parents[1] / 'storage'
_LOCK = threading.Lock()


def ensure_v254_bank():
    """Return bank path if present or safely restored; otherwise None.

    Never create a partially written SQLite filename visible to another request.
    The Render build normally restores the file earlier. This is fallback for
    manual/local starts and for a restart on an ephemeral filesystem.
    """
    db = _BANK_DIR / 'v254_candidates.sqlite'
    if db.is_file() and db.stat().st_size > 0:
        return db
    with _LOCK:
        if db.is_file() and db.stat().st_size > 0:
            return db
        archive = _BANK_DIR / 'v254_candidates.seed.zip'
        manifest = _BANK_DIR / 'v254_seed_manifest.json'
        if not archive.is_file() or not manifest.is_file():
            return None
        temp_name = None
        try:
            expected = json.loads(manifest.read_text(encoding='utf-8'))
            sha = hashlib.sha256()
            size = 0
            with zipfile.ZipFile(archive) as z:
                if z.namelist() != ['v254_candidates.sqlite']:
                    return None
                with z.open('v254_candidates.sqlite') as source:
                    with tempfile.NamedTemporaryFile(dir=_BANK_DIR, prefix='.v254-', suffix='.sqlite', delete=False) as temporary:
                        temp_name = temporary.name
                        for chunk in iter(lambda: source.read(1024 * 1024), b''):
                            temporary.write(chunk)
                            size += len(chunk)
                            sha.update(chunk)
            if size != expected.get('bytes') or sha.hexdigest() != expected.get('sha256'):
                return None
            os.replace(temp_name, db)
            temp_name = None
            return db
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            return None
        finally:
            if temp_name is not None:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
