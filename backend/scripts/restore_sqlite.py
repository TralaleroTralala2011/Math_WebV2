"""Verify an SQLite backup, then atomically publish it to an EMPTY data directory.

Use while the backend is stopped. No existing database is overwritten. The
whole directory is staged as a sibling so a failed copy never leaves partial
published databases. Usage:
  python scripts/restore_sqlite.py --snapshot /backups/<stamp> --destination /data
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import sqlite3
import tempfile


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def restore(snapshot: Path, destination: Path):
    snapshot = Path(snapshot).resolve(strict=True)
    destination = Path(destination).expanduser().resolve()
    if snapshot == destination or snapshot in destination.parents or destination in snapshot.parents:
        raise ValueError('Snapshot and destination must be separate directories')
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise FileExistsError('Destination is not empty; existing data will not be overwritten')
    manifest = json.loads((snapshot / 'manifest.json').read_text(encoding='utf-8'))
    records = manifest.get('files')
    if not isinstance(records, list) or not records:
        raise ValueError('No database files in manifest')
    names = set()
    for entry in records:
        if not isinstance(entry, dict):
            raise ValueError('Invalid database manifest entry')
        name = entry.get('name')
        if (not isinstance(name, str) or not name or name != Path(name).name
                or name != PureWindowsPath(name).name
                or Path(name).suffix not in ('.db', '.sqlite', '.sqlite3') or name in names):
            raise ValueError('Invalid or duplicate database filename')
        names.add(name)
        src = snapshot / name
        if not src.is_file() or src.is_symlink():
            raise ValueError(f'Missing or linked database: {name}')
        checksum = entry.get('sha256')
        if (type(entry.get('bytes')) is not int or entry['bytes'] < 1
                or not isinstance(checksum, str) or len(checksum) != 64
                or any(char not in '0123456789abcdef' for char in checksum)
                or src.stat().st_size != entry['bytes'] or _sha256(src) != checksum):
            raise ValueError(f'Checksum mismatch: {name}')
        try:
            with sqlite3.connect(src.as_uri() + '?mode=ro', uri=True) as conn:
                if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError(f'Corrupt SQLite database: {name}')
        except sqlite3.DatabaseError as exc:
            raise ValueError(f'Corrupt SQLite database: {name}') from exc
    # A sibling stage prevents partial commits even if a disk write or rename fails.
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.mathweb-restore-', dir=destination.parent))
    try:
        for entry in records:
            name = entry['name']
            target = stage / name
            with (snapshot / name).open('rb') as source, target.open('xb') as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
            target.chmod(0o600)
            if _sha256(target) != entry['sha256']:
                raise ValueError(f'Staged copy checksum mismatch: {name}')
        # Check one last time before the single directory-level commit.
        if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
            raise FileExistsError('Destination changed during restore; refusing overwrite')
        # On POSIX, os.replace supports replacing an empty destination directory;
        # on Windows, remove the verified-empty directory first.
        if os.name == 'nt' and destination.exists():
            destination.rmdir()
        os.replace(stage, destination)
        return [destination / entry['name'] for entry in records]
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', required=True, type=Path)
    p.add_argument('--destination', required=True, type=Path)
    args = p.parse_args()
    print('\n'.join(map(str, restore(args.snapshot, args.destination))))


if __name__ == '__main__':
    main()
