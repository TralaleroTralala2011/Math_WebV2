"""Single-host, resumable MATH_WEB Question Factory operations.

This is a *scheduler*, not a mathematical content generator or an autonomous
software developer. It registers existing candidates, queues only reviewed
methods, writes an atomic progress snapshot, and takes SQLite-consistent
backups. No unreviewed type is automatically approved, no paid API is called.

Usage: python -m question_factory.operations --mode once --data-dir /data
       python -m question_factory.operations --mode loop --data-dir /data
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import signal
import sqlite3
import tempfile
import threading
import time

from . import storage
from .bootstrap import initialize_factory

LOG = logging.getLogger('mathweb.factory.operations')


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _write_json_atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix='.report-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def backup_sqlite(source: Path, target: Path) -> bool:
    """Use SQLite's online backup API, never copy a live WAL database as files.

    Returns False if the source doesn't exist. The temp backup is integrity
    checked before being atomically installed. No source DB is changed.
    """
    if not source.is_file():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.db-backup-', suffix='.sqlite3', dir=target.parent)
    os.close(fd)
    try:
        with closing(sqlite3.connect(f'file:{source}?mode=ro', uri=True, timeout=30)) as src:
            with closing(sqlite3.connect(tmp, timeout=30)) as dst:
                src.backup(dst, pages=100, sleep=0.05)
                result = dst.execute('PRAGMA integrity_check').fetchone()[0]
                if result != 'ok':
                    raise RuntimeError(f'backup integrity failed: {source.name}: {result}')
        os.chmod(tmp, 0o600)
        os.replace(tmp, target)
        return True
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def backups(data_dir: Path, db_path: Path, backup_root: Path, label: str | None = None) -> dict:
    """Create a consistent per-database snapshot with a manifest.

    Backup is *single-host* and intended for a controlled pilot. For production
    also export backups off-host and verify restorability on a schedule.
    """
    stamp = label or _utc_stamp()
    # A manual backup and the scheduler may run within the same second.
    # Never overwrite an earlier backup or fail solely on timestamp reuse.
    for index in range(1000):
        candidate = stamp if index == 0 else f'{stamp}-{index:03d}'
        folder = backup_root / candidate
        try:
            folder.mkdir(parents=True, exist_ok=False)
            stamp = candidate
            break
        except FileExistsError:
            if label is not None:
                raise
    else:
        raise RuntimeError('could not reserve unique backup directory')
    sources = [db_path, data_dir / 'mathweb.db', data_dir / 'mathweb_ai_history.sqlite3']
    manifest = {'created_at_utc': stamp, 'databases': []}
    for src in sources:
        saved = folder / src.name
        if backup_sqlite(src, saved):
            manifest['databases'].append({'source': str(src), 'saved_as': saved.name, 'bytes': saved.stat().st_size})
    if not manifest['databases']:
        raise RuntimeError('no databases available for backup')
    _write_json_atomic(folder / 'manifest.json', manifest)
    return manifest


def once(data_dir: Path, db_path: Path | None = None, backup_root: Path | None = None,
         *, do_backup: bool = False, auto_enqueue: bool = True) -> dict:
    """Idempotent cycle: sync catalog/candidates; enqueue only approved types.

    Operators can call repeatedly; it never approves candidates or changes
    an existing MATH_WEB feature database.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_path or data_dir / 'question_factory.sqlite3'
    initialize_factory(str(db_path))
    registered_113 = storage.seed_curated(str(db_path))
    registered_114 = storage.seed_v114(str(db_path))
    registered_116 = storage.seed_v116(str(db_path))
    registered_117 = storage.seed_v117(str(db_path))
    registered_118 = storage.seed_v118(str(db_path))
    registered_119 = storage.seed_v119(str(db_path))
    registered_120 = storage.seed_v120(str(db_path))
    registered_121 = storage.seed_v121(str(db_path))
    # Explicit opt-in keeps earlier V121 installations/tests unchanged.
    register_v122 = os.environ.get('QF_ENABLE_V122_CANDIDATES','0') == '1'
    from importlib.util import find_spec
    v122_source_available = find_spec('question_factory.v122_research') is not None
    registered_122 = storage.seed_v122(str(db_path)) if register_v122 else 0
    if register_v122 and not v122_source_available:
        LOG.warning('V122 opt-in requested, but no V122 generator is bundled; skipping 0 records')
    # V123 forms reuse existing core methods and are NOT independently certified.
    # Opt-in registration is only for human-review staging, not auto-approval.
    register_v123 = os.environ.get('QF_ENABLE_V123_CANDIDATES','0') == '1'
    registered_123 = storage.seed_v123(str(db_path)) if register_v123 else 0
    jobs = storage.enqueue(str(db_path), per_type=10) if auto_enqueue else 0
    status = storage.progress(str(db_path))
    snapshot = {
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'source_version': 'V115 base + V116/V117/V118/V119/V120/V121/V122/V123 candidate methods',
        'registered_v113_blueprints': registered_113,
        'registered_v114_blueprints': registered_114,
        'registered_v116_blueprints': registered_116,
        'registered_v117_blueprints': registered_117,
        'registered_v118_blueprints': registered_118,
        'registered_v119_blueprints': registered_119,
        'registered_v120_blueprints': registered_120,
        'registered_v121_blueprints': registered_121,
        'registered_v122_blueprints': registered_122,
        'v122_requested': register_v122,
        'v122_source_available': v122_source_available,
        'v122_skipped_missing_source': register_v122 and not v122_source_available,
        'registered_v123_composite_candidates': registered_123,
        'jobs_enqueued_this_cycle': jobs,
        'status': status,
        'certification_note': (
            'Registered/approved blueprint IDs are NOT certified as unique '
            'mathematical methods. Only reviewed methods are enqueued; '
            'a correct numeric answer is not a full pedagogical audit.'
        ),
        'production_deployed': False,
    }
    if do_backup:
        snapshot['backup'] = backups(data_dir, db_path, backup_root or (data_dir / 'backups'))
    _write_json_atomic(data_dir / 'operations' / 'progress-latest.json', snapshot)
    return snapshot


def loop(data_dir: Path, db_path: Path, backup_root: Path,
         poll: int = 300, backup_every: int = 86400, stop: threading.Event | None = None) -> None:
    if poll < 5 or backup_every < 60:
        raise ValueError('poll >= 5 and backup_every >= 60 required')
    stop = stop or threading.Event()
    if threading.current_thread() is threading.main_thread():
        def shutdown(_signum, _frame):
            stop.set()
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
    last_backup = 0.0
    errors = 0
    while not stop.is_set():
        try:
            now = time.monotonic()
            create_backup = now - last_backup >= backup_every or last_backup == 0
            status = once(data_dir, db_path, backup_root, do_backup=create_backup)
            if create_backup:
                last_backup = now
            errors = 0
            LOG.info('factory cycle: queued %s, approved %s, verified %s',
                     status['jobs_enqueued_this_cycle'], status['status']['approved_archetypes'],
                     status['status']['verified_questions'])
        except Exception:
            errors += 1
            LOG.exception('factory operator failed; retrying without approving any method')
        delay = min(poll * (2 ** min(errors, 4)), 3600)
        stop.wait(delay)


def main(argv=None):
    parser = argparse.ArgumentParser(description='MATH_WEB V115 single-host factory operator')
    parser.add_argument('--mode', choices=['once', 'loop', 'backup'], default='once')
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('QF_DATA_DIR', '/data')))
    parser.add_argument('--db', type=Path, default=None)
    parser.add_argument('--poll', type=int, default=300, help='seconds between cycles (loop)')
    parser.add_argument('--backup-every', type=int, default=86400)
    args = parser.parse_args(argv)
    data_dir = args.data_dir.expanduser().resolve()
    db = args.db or Path(os.environ.get('QF_DB_PATH', str(data_dir / 'question_factory.sqlite3')))
    backup_dir = data_dir / 'backups'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    if args.mode == 'loop':
        loop(data_dir, db, backup_dir, args.poll, args.backup_every)
    elif args.mode == 'backup':
        print(json.dumps(backups(data_dir, db, backup_dir), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(once(data_dir, db, backup_dir, do_backup=True), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
