"""Consistent SQLite backups using SQLite online backup API, never copying live WAL files.
Usage: python scripts/backup_sqlite.py --source-dir /persistent/data --destination /safe/backups
"""
import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def backup_all(source: Path, destination: Path, extra_files=()):
    source = Path(source).expanduser()
    # Refuse aliases to external folders. Backups should never follow a linked
    # source directory or linked database into unrelated/private files.
    if source.is_symlink():
        raise ValueError('Refusing a symlinked source directory')
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise NotADirectoryError(source)
    destination = Path(destination).expanduser().resolve()
    if (source == destination or source in destination.parents
            or destination in source.parents):
        raise ValueError('Backup destination must be separate from the live data directory')
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    snapshot = destination / stamp
    snapshot.mkdir(mode=0o700)
    manifest = {'created_utc': stamp, 'source': str(source), 'files': []}
    try:
        regular = [p for p in sorted(source.iterdir()) if p.suffix in ('.db', '.sqlite', '.sqlite3')]
        extras = [Path(p).expanduser() for p in extra_files]
        seen = set()
        for db in regular + extras:
            if db.suffix not in ('.db', '.sqlite', '.sqlite3'):
                raise ValueError(f'Invalid SQLite filename: {db.name}')
            if db.is_symlink():
                raise ValueError(f'Refusing linked SQLite database: {db.name}')
            if db in extras and not db.is_file():
                raise FileNotFoundError(db)
            if not db.is_file():
                continue
            if db.name in seen:
                raise ValueError(f'Duplicate SQLite filename across sources: {db.name}')
            seen.add(db.name)
            if destination == db.resolve() or destination in db.resolve().parents:
                raise ValueError('Cannot back up from within the backup destination')
            target = snapshot / db.name
            with sqlite3.connect(f'file:{db.as_posix()}?mode=ro', uri=True) as src, sqlite3.connect(target) as dst:
                src.backup(dst)
                result = dst.execute('PRAGMA integrity_check').fetchone()[0]
                if result != 'ok':
                    raise RuntimeError(f'{db.name}: integrity_check={result}')
            target.chmod(0o600)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            manifest['files'].append({'name': db.name, 'sha256': digest, 'bytes': target.stat().st_size, 'integrity': 'ok'})
        if not manifest['files']:
            raise ValueError('No SQLite databases found in source directory')
        manifest_file = snapshot / 'manifest.json'
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        manifest_file.chmod(0o600)
        return snapshot
    except Exception:
        # Preserve partial snapshot for investigation; do not claim success.
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    args = p.parse_args()
    print(backup_all(args.source_dir, args.destination))

if __name__ == '__main__':
    main()
