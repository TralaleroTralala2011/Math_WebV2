"""V115 deployment-operator smoke, persisted-state, recovery and backup tests."""
from __future__ import annotations
import json
from pathlib import Path
import sqlite3
import threading

from question_factory import operations, storage, worker


def test_operator_bootstraps_full_catalog_without_fake_completion(tmp_path):
    data = tmp_path / 'data'
    first = operations.once(data, do_backup=True)
    status = first['status']
    assert status['topics'] == 150
    assert status['archetypes'] == 770
    assert status['pending_review_archetypes'] == 770
    assert status['approved_archetypes'] == 0
    assert status['verified_questions'] == 0
    assert first['jobs_enqueued_this_cycle'] == 0
    assert first['production_deployed'] is False
    progress = json.loads((data/'operations'/'progress-latest.json').read_text(encoding='utf-8'))
    assert progress['status'] == status
    assert (data/'backups'/first['backup']['created_at_utc']/'question_factory.sqlite3').exists()
    assert operations.once(data)['status']['archetypes'] == 770


def test_operator_queues_only_approved_methods_and_is_idempotent(tmp_path):
    data = tmp_path/'data'
    db = str(data/'question_factory.sqlite3')
    operations.once(data)
    storage.approve(db, 'v114-three_set_union', 'reviewed-by-human')
    second = operations.once(data)
    assert second['jobs_enqueued_this_cycle'] == 1
    assert second['status']['approved_archetypes'] == 1
    assert second['status']['pending_review_archetypes'] == 769
    assert operations.once(data)['jobs_enqueued_this_cycle'] == 0
    assert worker.run(db, workers=2) == 1
    assert storage.progress(db)['verified_questions'] == 10
    assert operations.once(data)['status']['verified_questions'] == 10


def test_sqlite_online_backup_includes_committed_wal_rows(tmp_path):
    db = tmp_path/'source.db'
    dst = tmp_path/'backups'/'saved.sqlite3'
    with sqlite3.connect(db) as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('CREATE TABLE IF NOT EXISTS details (n INTEGER)')
        conn.execute('INSERT INTO details VALUES(42)')
    assert operations.backup_sqlite(db, dst) is True
    with sqlite3.connect(dst) as conn:
        assert conn.execute('SELECT n FROM details').fetchone() == (42,)
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert operations.backup_sqlite(tmp_path/'missing.db', tmp_path/'missing_copy') is False


def test_operator_graceful_stop_respects_review_lock(tmp_path):
    data=tmp_path/'data'
    stop=threading.Event()
    stop.set()
    operations.loop(data, data/'question_factory.sqlite3', data/'backups', poll=5,
                    backup_every=60, stop=stop)
    assert not (data/'question_factory.sqlite3').exists()


def test_operator_does_not_change_existing_mathweb_data(tmp_path):
    data = tmp_path/'data'
    data.mkdir()
    db = data/'mathweb.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE preserved (secret TEXT)')
        conn.execute('INSERT INTO preserved VALUES(?)', ('unchanged',))
    result = operations.once(data, do_backup=True)
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT secret FROM preserved').fetchone() == ('unchanged',)
    target = data/'backups'/result['backup']['created_at_utc']/'mathweb.db'
    assert target.is_file()
    with sqlite3.connect(target) as conn:
        assert conn.execute('SELECT secret FROM preserved').fetchone() == ('unchanged',)


def test_backups_created_same_second_never_overwrite(tmp_path):
    data=tmp_path/'data'
    operations.once(data)
    db=data/'question_factory.sqlite3'
    a=operations.backups(data,db,data/'backups')
    b=operations.backups(data,db,data/'backups')
    assert a['created_at_utc'] != b['created_at_utc']
    assert (data/'backups'/a['created_at_utc']/'question_factory.sqlite3').is_file()
    assert (data/'backups'/b['created_at_utc']/'question_factory.sqlite3').is_file()
