"""Account loss regressions. No tests touch the operator's real SQLite file."""
from __future__ import annotations

from pathlib import Path
import json
import sqlite3

import pytest

from database.persistence_guard import (
    check_account_continuity, configured_storage, create_snapshot,
    record_account_watermark, snapshot_status,
)


def _make_user_db(path: Path, count: int):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE)')
        db.executemany('INSERT INTO users(username) VALUES (?)', [(f'user_{x}',) for x in range(count)])


def test_render_without_disk_fails_closed(tmp_path):
    db = tmp_path / 'app' / 'mathweb.db'
    s = configured_storage(db, environ={'RENDER': 'true'}, mount_check=lambda _: False)
    assert not s['safe'] and not s['mount_verified']
    assert s['render_detected'] and s['concerns']


def test_render_even_with_paths_but_not_real_mount_fails(tmp_path):
    root=tmp_path/'data';root.mkdir()
    db=root/'mathweb.db'
    env={'RENDER':'true','MATHWEB_DATA_DIR':str(root),'MATHWEB_DB_PATH':str(db)}
    assert not configured_storage(db,environ=env,mount_check=lambda _:False)['safe']
    good=configured_storage(db,environ=env,mount_check=lambda _:True)
    assert good['safe'] and good['mount_verified']


def test_preexisting_users_do_not_disappear_silently(tmp_path):
    db=tmp_path/'mathweb.db'
    _make_user_db(db,35)
    record_account_watermark(db)
    assert snapshot_status(db)['accounts_high_watermark']==35
    db.rename(tmp_path/'old.sqlite')
    with pytest.raises(RuntimeError,match='database is absent'):
        check_account_continuity(db)
    _make_user_db(db,1)
    with pytest.raises(RuntimeError,match='count dropped'):
        check_account_continuity(db)


def test_snapshot_keeps_registered_accounts_and_is_not_destructive(tmp_path):
    db=tmp_path/'mathweb.db'
    _make_user_db(db,33)
    record_account_watermark(db)
    result=create_snapshot(db,force=True)
    assert result['created'] and result['accounts_in_snapshot']==33
    shots=list((tmp_path/'.mathweb_data_safety'/'snapshots').glob('*.sqlite3'))
    assert len(shots)==1
    with sqlite3.connect(shots[0]) as backup:
        assert backup.execute('SELECT COUNT(*) FROM users').fetchone()[0]==33
        assert backup.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    with sqlite3.connect(db) as live:
        assert live.execute('SELECT COUNT(*) FROM users').fetchone()[0]==33


def test_snapshots_do_not_replace_db_and_retention(tmp_path):
    db=tmp_path/'mathweb.db'
    _make_user_db(db,30)
    record_account_watermark(db)
    for _ in range(6):
        assert create_snapshot(db,force=True,max_snapshots=3)['created']
    assert snapshot_status(db)['snapshot_count']==3
    with sqlite3.connect(db) as live:
        assert live.execute('SELECT COUNT(*) FROM users').fetchone()[0]==30


def test_no_phantom_recovery_if_no_accounts_to_read(tmp_path):
    db=tmp_path/'absent.sqlite'
    assert create_snapshot(db)['created'] is False
    assert snapshot_status(db)['accounts_now'] is None


def test_admin_backup_rejects_restoring_snapshot_with_fewer_accounts(tmp_path, monkeypatch):
    # Use the already tested encrypted backup format; no production DB involved.
    from app import update_backup_routes as backups
    import tempfile
    from database.database import get_connection
    # Get a fully initialized test-only schema by copying the current DB.
    source_path=Path(__file__).resolve().parents[1]/'database'/'mathweb.db'
    live=tmp_path/'live.sqlite3'
    with sqlite3.connect(source_path) as src, sqlite3.connect(live) as dst:
        src.backup(dst)
    with sqlite3.connect(live) as c:
        c.execute("INSERT INTO users (username,player_id,password_hash,created_at) VALUES ('test_v79_user_a','v79-player-a','hash','2026-01-01')")
    monkeypatch.setattr(backups, '_paths', lambda: {'accounts': live})
    encrypted=tmp_path/'saved.mwbackup'
    backups.create_backup('super-strong-test-secret',encrypted)
    with sqlite3.connect(live) as c:
        c.execute("INSERT INTO users (username,player_id,password_hash,created_at) VALUES ('test_v79_user_b','v79-player-b','hash','2026-01-01')")
    with pytest.raises(ValueError,match='DỪNG KHÔI PHỤC'):
        backups.restore_backup(encrypted,'super-strong-test-secret')
    with sqlite3.connect(live) as c:
        assert c.execute("SELECT COUNT(*) FROM users WHERE username LIKE 'test_v79_user_%'").fetchone()[0] == 2


def test_render_startup_does_not_create_accounts_on_ephemeral_disk(tmp_path):
    import os
    import subprocess
    import sys
    backend=Path(__file__).resolve().parents[1]
    root=tmp_path/'not-mounted'
    db=root/'mathweb.db'
    env=dict(os.environ,
        RENDER='true',
        MATHWEB_ENV='production',
        MATHWEB_BOOTSTRAP_ADMIN_PASSWORD='test-password-long-and-not-public',
        MATHWEB_DATA_DIR=str(root),
        MATHWEB_DB_PATH=str(db),
        PYTHONPATH=str(backend))
    result=subprocess.run([sys.executable,'-c','import database.database'],env=env,
                          cwd=backend,text=True,capture_output=True,timeout=30)
    assert result.returncode != 0
    assert 'DATA PROTECTION' in result.stderr
    assert not db.exists()


def test_admin_storage_snapshot_requires_admin_token(tmp_path):
    import os
    import subprocess
    import sys
    backend=Path(__file__).resolve().parents[1]
    root=tmp_path/'local_data'
    root.mkdir()
    script='''
from app.main import app
from fastapi.testclient import TestClient
from database.database import get_connection
from app.auth.routes import create_admin_token
client=TestClient(app)
assert client.get('/api/admin/storage-status').status_code in (401,403)
assert client.post('/api/admin/storage/snapshot').status_code in (401,403)
with get_connection() as db:
  row=db.execute("SELECT id,username,auth_version FROM admin_accounts LIMIT 1").fetchone()
  token=create_admin_token(row['id'], row['username'], row['auth_version'])
headers={'Authorization': 'Bearer '+token}
status=client.get('/api/admin/storage-status',headers=headers)
assert status.status_code == 200,status.text
assert status.json()['accounts_now'] == 0,status.text
snap=client.post('/api/admin/storage/snapshot',headers=headers)
assert snap.status_code == 200,snap.text
assert snap.json()['ok']
print('admin_data_safety_ok')
'''
    env=dict(os.environ,
        MATHWEB_DATA_DIR=str(root),
        MATHWEB_DB_PATH=str(root/'mathweb.db'),
        MATHWEB_BOOTSTRAP_ADMIN_PASSWORD='test-only-admin-password-123456',
        PYTHONPATH=str(backend))
    for k in ('RENDER','RENDER_SERVICE_ID','RENDER_EXTERNAL_HOSTNAME','MATHWEB_ENV'):
        env.pop(k,None)
    result=subprocess.run([sys.executable,'-c',script],cwd=backend,env=env,
                          text=True,capture_output=True,timeout=45)
    assert result.returncode==0,result.stderr+result.stdout
    assert 'admin_data_safety_ok' in result.stdout


def test_cross_game_numeric_rewrites_are_rejected(tmp_path, monkeypatch):
    from app.ai.engine.question_history import QuestionHistory
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.sqlite3'))
    ledger=QuestionHistory()
    run='fixed_run_same_across_3_games'
    topic='remainder'
    first={'question':'Tìm số dư khi chia 127 cho 13.', 'form_id':'remainder-basic'}
    second={'question':'Tìm số dư khi chia 423 cho 17.', 'form_id':'remainder-basic'}
    third={'question':'Tìm số dư khi chia 423 cho 17.', 'form_id':'alternate-id'}
    assert ledger.claim_topic_run(run,topic,first)
    assert not ledger.claim_topic_run(run,topic,second)
    assert not ledger.claim_topic_run(run,topic,third)
    assert ledger.claim_topic_run('different_run',topic,second)
