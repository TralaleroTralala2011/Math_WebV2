"""V153 tests: no silent database reset, atomic restore, migration validation."""
import hashlib
import os
from pathlib import Path
import sqlite3
import sys

import pytest

from scripts.backup_sqlite import backup_all
from scripts.restore_sqlite import restore
from scripts.migrate_persistent_data import migrate
from database.data_paths import database_path
from question_factory.bootstrap import database_path as factory_database_path
from app.ai.engine.question_history import _database_path as history_database_path


def build_db(path, value, *, wal=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    if wal:
        conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('CREATE TABLE accounts (username TEXT PRIMARY KEY, xp INTEGER NOT NULL)')
    conn.execute('INSERT INTO accounts VALUES(?,?)', (path.stem, value))
    conn.commit()
    return conn


def xp(path):
    with sqlite3.connect(path) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        return conn.execute('SELECT xp FROM accounts').fetchone()[0]


def test_main_factory_history_resolve_external_path(tmp_path, monkeypatch):
    data = tmp_path / 'persistent'
    monkeypatch.setenv('MATHWEB_DATA_DIR', str(data))
    monkeypatch.delenv('QF_DB_PATH', raising=False)
    monkeypatch.delenv('MATHWEB_DB_PATH', raising=False)
    monkeypatch.delenv('MATHWEB_AI_HISTORY_DB_PATH', raising=False)
    assert database_path('mathweb.db') == data / 'mathweb.db'
    assert Path(factory_database_path()) == data / 'question_factory.sqlite3'
    assert history_database_path() == data / 'mathweb_ai_history.sqlite3'
    # An explicit override must remain higher priority than MATHWEB_DATA_DIR.
    monkeypatch.setenv('QF_DB_PATH', str(tmp_path / 'custom_qf.db'))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'custom_history.db'))
    assert Path(factory_database_path()) == tmp_path / 'custom_qf.db'
    assert history_database_path() == tmp_path / 'custom_history.db'


def test_dry_run_does_not_write_or_change_sources(tmp_path):
    src = tmp_path / 'legacy'
    conn = build_db(src / 'mathweb.db', 601)
    conn.close()
    original = hashlib.sha256((src / 'mathweb.db').read_bytes()).hexdigest()
    dst, backups = tmp_path / 'new_data', tmp_path / 'backup'
    result = migrate(src, dst, backups)
    assert result['mode'] == 'dry_run'
    assert result['files'] == ['mathweb.db']
    assert not dst.exists() and not backups.exists()
    assert hashlib.sha256((src / 'mathweb.db').read_bytes()).hexdigest() == original


def test_live_wal_snapshot_preserves_xp_and_multiple_databases(tmp_path):
    source = tmp_path / 'legacy'
    connections = [
        build_db(source / 'mathweb.db', 101, wal=True),
        build_db(source / 'question_factory.sqlite3', 202, wal=True),
        build_db(source / 'mathweb_ai_history.sqlite3', 303, wal=True),
    ]
    # Keep WAL readers/writers open during the snapshot; backups must use SQLite API.
    snapshot = backup_all(source, tmp_path / 'backups')
    restored = restore(snapshot, tmp_path / 'target')
    assert {p.name for p in restored} == {p.name for p in source.glob('*') if p.suffix in ('.db','.sqlite3')}
    assert [xp(tmp_path / 'target' / name) for name in
            ['mathweb.db','question_factory.sqlite3','mathweb_ai_history.sqlite3']] == [101,202,303]
    assert [xp(source / name) for name in
            ['mathweb.db','question_factory.sqlite3','mathweb_ai_history.sqlite3']] == [101,202,303]
    for conn in connections:
        conn.close()
    assert (snapshot / 'manifest.json').exists()


def test_migrate_two_dbs_then_refuses_second_install(tmp_path):
    src = tmp_path / 'legacy'
    a=build_db(src/'mathweb.db', 57)
    b=build_db(src/'question_factory.sqlite3', 89)
    a.close(); b.close()
    dest = tmp_path / 'data'; backups = tmp_path / 'backups'
    result = migrate(src, dest, backups, apply=True)
    assert result['mode'] == 'migrate'
    assert xp(dest/'mathweb.db') == xp(src/'mathweb.db') == 57
    assert xp(dest/'question_factory.sqlite3') == xp(src/'question_factory.sqlite3') == 89
    assert (Path(result['snapshot'])/'manifest.json').exists()
    with pytest.raises(FileExistsError):
        migrate(src, dest, backups, apply=True)
    assert xp(dest/'mathweb.db') == 57


def test_restore_is_atomic_if_install_fails(tmp_path, monkeypatch):
    src = tmp_path / 'legacy'
    c=build_db(src/'mathweb.db', 51)
    c.close()
    snap=backup_all(src, tmp_path/'backups')
    import scripts.restore_sqlite as module
    def fail_replace(*args,**kwargs):
        raise OSError('simulated failed commit')
    monkeypatch.setattr(module.os, 'replace', fail_replace)
    with pytest.raises(OSError, match='simulated failed commit'):
        module.restore(snap, tmp_path/'target')
    assert not (tmp_path/'target').exists()
    assert not list(tmp_path.glob('.mathweb-restore-*'))
    assert xp(src/'mathweb.db') == 51


def test_restore_to_existing_empty_dir_is_atomic(tmp_path):
    src=tmp_path/'legacy'
    c=build_db(src/'mathweb.db', 98);c.close()
    snap=backup_all(src,tmp_path/'backups')
    (tmp_path/'target').mkdir()
    assert xp(restore(snap,tmp_path/'target')[0]) == 98


def test_no_empty_or_nested_migrations(tmp_path):
    src=tmp_path/'legacy';src.mkdir()
    with pytest.raises(ValueError,match='No legacy'):
        migrate(src,tmp_path/'data',tmp_path/'backups',apply=True)
    c=build_db(src/'db.sqlite3',12);c.close()
    with pytest.raises(ValueError,match='separate'):
        migrate(src,src/'external',tmp_path/'backups')
    with pytest.raises(ValueError,match='separate'):
        migrate(src,tmp_path/'data',tmp_path/'data'/'backups')


def test_backup_files_private_on_posix(tmp_path):
    if os.name == 'nt':
        pytest.skip('POSIX permissions only')
    src=tmp_path/'legacy'
    c=build_db(src/'mathweb.db',12);c.close()
    snap=backup_all(src,tmp_path/'backups')
    assert snap.stat().st_mode & 0o077 == 0
    assert (snap/'mathweb.db').stat().st_mode & 0o077 == 0
    assert (snap/'manifest.json').stat().st_mode & 0o077 == 0
