"""One-time non-destructive migration of legacy SQLite data to MATHWEB_DATA_DIR.

Always STOP the backend, Question Factory worker and any other SQLite writers
before migration. The default is a read-only plan; --apply makes a verified
SQLite-online backup and restores it into an entirely empty target directory.
The original databases are NEVER deleted, moved or modified by this tool.
After successful migration, configure MATHWEB_DATA_DIR to --destination.

python scripts/migrate_persistent_data.py --source-dir backend/database \\
  --destination /private/mathweb-data --backup-root /private/mathweb-backups
python scripts/migrate_persistent_data.py ... --apply
"""
import argparse
import json
from pathlib import Path

try:
    from .backup_sqlite import backup_all
    from .restore_sqlite import restore
except ImportError:  # direct script execution from backend/scripts
    from backup_sqlite import backup_all
    from restore_sqlite import restore


DB_SUFFIXES = {'.db', '.sqlite', '.sqlite3'}


def migrate(source_dir: Path, destination: Path, backup_root: Path, apply: bool = False, extra_files=()):
    raw_source = Path(source_dir).expanduser()
    if raw_source.is_symlink():
        raise ValueError('Refusing a symlinked source directory')
    source_dir = raw_source.resolve(strict=True)
    destination = Path(destination).expanduser().resolve()
    backup_root = Path(backup_root).expanduser().resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(source_dir)
    if (source_dir == destination or source_dir in destination.parents
            or destination in source_dir.parents or backup_root == source_dir
            or source_dir in backup_root.parents or backup_root == destination
            or destination in backup_root.parents or backup_root in destination.parents):
        raise ValueError('Source, destination and backup root must be separate and non-nested')
    # Never migrate into an existing populated data folder.
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise FileExistsError('Destination is not empty; existing user data must be preserved')
    candidates = sorted(p for p in source_dir.iterdir() if p.suffix in DB_SUFFIXES)
    if any(p.is_symlink() for p in candidates):
        raise ValueError('Refusing symbolic links in legacy data')
    sources = [p for p in candidates if p.is_file()]
    extras = [Path(p).expanduser() for p in extra_files]
    for extra in extras:
        if extra.is_symlink():
            raise ValueError('Refusing symbolic links in extra SQLite files')
        extra = extra.resolve(strict=True)
        if not extra.is_file() or extra.suffix not in DB_SUFFIXES:
            raise ValueError('Extra source must be a regular SQLite file')
        if (destination == extra or destination in extra.parents
                or backup_root == extra or backup_root in extra.parents):
            raise ValueError('Extra source must not be in destination or backup root')
    all_names = [p.name for p in sources+extras]
    if len(set(all_names)) != len(all_names):
        raise ValueError('Duplicate SQLite filename across source directories; manual reconciliation required')
    if not sources and not extras:
        raise ValueError('No legacy SQLite files to migrate')
    result = {
        'mode': 'migrate' if apply else 'dry_run',
        'source_dir': str(source_dir), 'destination': str(destination),
        'backup_root': str(backup_root),
        'files': all_names,
        'extra_files': [str(p.resolve()) for p in extras],
        'original_files_preserved': True,
    }
    if apply:
        snapshot = backup_all(source_dir, backup_root, extra_files=extras)
        try:
            installed = restore(snapshot, destination)
        except Exception:
            # Backup remains available for manual investigation; original is untouched.
            raise
        result['snapshot'] = str(snapshot)
        result['restored_files'] = [p.name for p in installed]
        result['manifest'] = str(snapshot / 'manifest.json')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', required=True, type=Path)
    p.add_argument('--destination', required=True, type=Path)
    p.add_argument('--backup-root', required=True, type=Path)
    p.add_argument('--include-file', type=Path, action='append', default=[],
                   help='Include a separate legacy DB (e.g. database/study_suite.sqlite3). '
                        'Can be repeated; filenames must be unique.')
    p.add_argument('--apply', action='store_true', help='Perform the migration; default is only a plan')
    args = p.parse_args()
    print(json.dumps(migrate(args.source_dir, args.destination, args.backup_root,
                             args.apply, args.include_file), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
