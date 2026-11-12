"""Read-only audit of parallel SQLite copies: does NOT merge or expose accounts.

Example: python backend/scripts/audit_legacy_databases.py --root . --output V154_RELEASE/DATABASE_LOCATION_AUDIT.json

The backend uses backend/database by default, but extracted historical copies may
contain different users. This tool reports counts, SHA-256, and *aggregate*
overlap counts only. Never use it to choose, copy, or overwrite a live database.
Stop all database writers first if you need a reliable point-in-time inventory.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sqlite3

SUFFIXES = {'.db', '.sqlite', '.sqlite3'}
TABLES = ('users', 'game_results', 'friends', 'messages', 'notifications',
          'question_sessions', 'match_invites', 'matches', 'admin_question_bank')


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def _examine(path):
    entry = {'bytes': path.stat().st_size, 'sha256': digest(path), 'tables': {},
             'integrity': 'not_checked'}
    if path.is_symlink():
        # Do not read arbitrary external data via symlinks.
        return {'status': 'refused_symlink', 'tables': {}}
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=2) as connection:
        connection.execute('PRAGMA query_only=ON')
        entry['integrity'] = connection.execute('PRAGMA integrity_check').fetchone()[0]
        names = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for name in TABLES:
            if name in names:
                entry['tables'][name] = connection.execute('SELECT COUNT(*) FROM ' + name).fetchone()[0]
        users = set()
        if 'users' in names:
            columns = {row[1] for row in connection.execute('PRAGMA table_info(users)')}
            # Only aggregate intersections in memory; never print identifying fields.
            key = 'username' if 'username' in columns else ('player_id' if 'player_id' in columns else None)
            if key:
                users = {str(value) for (value,) in connection.execute('SELECT ' + key + ' FROM users') if value is not None}
    return entry, users


def audit(root: Path):
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    rows, keys = [], {}
    for path in sorted(root.rglob('*')):
        if path.suffix not in SUFFIXES or '.venv' in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append({'relative_path': rel, 'status': 'refused_symlink'})
            continue
        if not path.is_file():
            continue
        try:
            record, users = _examine(path)
            rows.append({'relative_path': rel, **record})
            if 'users' in record['tables']:
                keys[rel] = users
        except (sqlite3.Error, OSError, ValueError) as error:
            rows.append({'relative_path': rel, 'status': 'unreadable',
                         'error_type': type(error).__name__})
    overlaps = []
    for a, b in itertools.combinations(sorted(keys), 2):
        overlaps.append({'left': a, 'right': b,
                         'matching_usernames_count': len(keys[a] & keys[b]),
                         'left_only_count': len(keys[a] - keys[b]),
                         'right_only_count': len(keys[b] - keys[a])})
    primary = [r for r in rows if r['relative_path'].endswith('mathweb.db') and 'users' in r.get('tables',{})]
    return {
        'mode': 'read_only_no_merge', 'files_found': len(rows),
        'accounts_bearing_databases': len(primary),
        'parallel_db_warning': len({r['sha256'] for r in primary}) > 1,
        'databases': rows,
        'account_overlap_aggregates': overlaps,
        'caution': ('Account overlap by username does NOT certify identity. '
                    'Never merge, delete, or overwrite databases without a separate '
                    'validated migration and a verified private backup. '
                    'SQLite WAL must be checkpointed for a reliable stopped-server inventory.'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.root)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + '\n', encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
