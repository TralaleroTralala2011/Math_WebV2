"""Update backup/restore regression. Separate subprocess prevents touching real user data."""
import os
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_encrypted_backup_announcement_and_restore(tmp_path):
    store = tmp_path / 'data'
    store.mkdir()
    env = dict(os.environ, PYTHONPATH=str(BACKEND), MATHWEB_DATA_DIR=str(store),
               MATHWEB_DB_PATH=str(store/'mathweb.db'),
               MATHWEB_AI_HISTORY_DB_PATH=str(store/'history.sqlite3'),
               MATHWEB_BOOTSTRAP_ADMIN_PASSWORD='test-only-bootstrap-credential-change-me',
               PYTHONDONTWRITEBYTECODE='1')
    script = r'''
import os
from pathlib import Path
from fastapi.testclient import TestClient
from database.database import get_connection, init_database
init_database()
from app.main import app
from app.auth.routes import create_admin_token
from app.update_backup_routes import _paths
import sqlite3

with get_connection() as db:
    admin=db.execute("SELECT * FROM admin_accounts WHERE username='admin19022011'").fetchone()
    token=create_admin_token(admin['id'],admin['username'],admin['auth_version'])
    cols={r['name'] for r in db.execute('PRAGMA table_info(users)')}
    user_data={'username':'learning_sample','player_id':'MW-123456-987','password_hash':'example_hash_not_actual_password','created_at':'2026-11-14T00:00:00+00:00'}
    keys=list(user_data)
    db.execute(f"INSERT INTO users({','.join(keys)}) VALUES({','.join('?' for _ in keys)})",tuple(user_data.values()))
    user_id=db.execute("SELECT id FROM users WHERE username='learning_sample'").fetchone()['id']
    db.execute('UPDATE users SET xp=1234 WHERE id=?',(user_id,))
    db.commit()

progress_path = _paths()['learning_progress'];progress_path.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(progress_path) as db:
    db.execute('CREATE TABLE IF NOT EXISTS regression_user_state (user_id INTEGER, progress TEXT)')
    db.execute('INSERT INTO regression_user_state VALUES (?,?)',(user_id,'chapter42'))

client=TestClient(app)
unauthorized=client.post('/api/admin/update/backup',data={'passphrase':'strong-secret-phrase-456789'})
assert unauthorized.status_code in (401,403),unauthorized.text
header={'Authorization':'Bearer '+token}
backup=client.post('/api/admin/update/backup',headers=header,data={'passphrase':'strong-secret-phrase-456789'})
assert backup.status_code==200,backup.text
assert backup.content.startswith(b'MWB1')
assert b'learning_sample' not in backup.content
tampered=bytearray(backup.content);tampered[-25]^=1
corrupt=client.post('/api/admin/update/restore',headers=header,data={'passphrase':'strong-secret-phrase-456789','confirmation':'KHOI PHUC DU LIEU'},files={'file':('sample.mwbackup',bytes(tampered),'application/octet-stream')})
assert corrupt.status_code==422,corrupt.text
assert client.post('/api/admin/update/announce').status_code in (401,403)
bad=client.post('/api/admin/update/restore',headers=header,data={'passphrase':'wrong-but-long-passphrase', 'confirmation':'KHOI PHUC DU LIEU'},files={'file':('sample.mwbackup',backup.content,'application/octet-stream')})
assert bad.status_code==422,bad.text

notice=client.post('/api/admin/update/announce',headers=header)
assert notice.status_code==200,notice.text
with get_connection() as db:
    assert db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND type='system_update'",(user_id,)).fetchone()[0]>=1
    db.execute('UPDATE users SET xp=9 WHERE id=?',(user_id,))
    db.commit()
with sqlite3.connect(progress_path) as db:
    db.execute("UPDATE regression_user_state SET progress='lost'")

denied=client.post('/api/admin/update/restore',headers=header,data={'passphrase':'strong-secret-phrase-456789', 'confirmation':'no'},files={'file':('sample.mwbackup',backup.content,'application/octet-stream')})
assert denied.status_code==422
restore=client.post('/api/admin/update/restore',headers=header,data={'passphrase':'strong-secret-phrase-456789', 'confirmation':'KHOI PHUC DU LIEU'},files={'file':('sample.mwbackup',backup.content,'application/octet-stream')})
assert restore.status_code==200,restore.text
assert 'accounts' in restore.json()['restored']
with get_connection() as db:
    assert db.execute('SELECT xp FROM users WHERE id=?',(user_id,)).fetchone()['xp']==1234
    assert db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND type='system_update'",(user_id,)).fetchone()[0]>=1
with sqlite3.connect(progress_path) as db:
    assert db.execute('SELECT progress FROM regression_user_state WHERE user_id=?',(user_id,)).fetchone()[0]=='chapter42'
print('TEST_ADMIN_UPDATE_SUCCESS')
'''
    result = subprocess.run([sys.executable, '-c', script], cwd=BACKEND, env=env,
                            text=True, capture_output=True, timeout=115)
    assert result.returncode == 0, result.stdout + '\n' + result.stderr
    assert 'TEST_ADMIN_UPDATE_SUCCESS' in result.stdout
