"""Protect external persistent users from repeated legacy Admin bootstrapping."""
import os
import subprocess
import sys

BACKEND=__import__('pathlib').Path(__file__).resolve().parents[1]


def subprocess_backend(tmp_path, script, *, production=False, password=None):
    data=tmp_path/'persistent'; data.mkdir(exist_ok=True)
    env=os.environ.copy()
    env.update({'MATHWEB_DATA_DIR':str(data),'MATHWEB_DB_PATH':str(data/'mathweb.db'),
                'MATHWEB_AI_HISTORY_DB_PATH':str(data/'ai_history.sqlite3'),
                'QF_DB_PATH':str(data/'qf.sqlite3'),'PYTHONPATH':str(BACKEND),'PYTHONDONTWRITEBYTECODE':'1'})
    if production:env['MATHWEB_ENV']='production'
    else:env.pop('MATHWEB_ENV',None)
    if password is None:env.pop('MATHWEB_BOOTSTRAP_ADMIN_PASSWORD',None)
    else:env['MATHWEB_BOOTSTRAP_ADMIN_PASSWORD']=password
    return subprocess.run([sys.executable,'-c',script],env=env,cwd=BACKEND,text=True,capture_output=True,timeout=25)


def test_reinit_does_not_recreate_admin_or_duplicate_player_id(tmp_path):
    code='''
from database.database import init_database,get_connection
from app.main import app
with get_connection() as c:
    old_count=c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    dedicated=c.execute("SELECT COUNT(*) FROM admin_accounts WHERE username='admin19022011'").fetchone()[0]
    assert dedicated==1
for _ in range(3):init_database()
with get_connection() as c:
    assert c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == old_count
    assert c.execute("SELECT COUNT(*) FROM admin_accounts WHERE username='admin19022011'").fetchone()[0] == 1
    assert c.execute("SELECT COUNT(*) FROM users WHERE username='admin19022011'").fetchone()[0] == 0
print('repeated_init_no_admin_shadow')
'''
    run=subprocess_backend(tmp_path,code)
    assert run.returncode == 0,run.stderr+run.stdout
    assert 'repeated_init_no_admin_shadow' in run.stdout


def test_production_requires_nondefault_admin_bootstrap_secret(tmp_path):
    fail=subprocess_backend(tmp_path,"import database.database", production=True)
    assert fail.returncode != 0
    assert 'non-default MATHWEB_BOOTSTRAP_ADMIN_PASSWORD' in fail.stderr
    okay=subprocess_backend(tmp_path,"import database.database;print('success')",production=True,
                            password='v157_testing_not_a_real_password_123')
    assert okay.returncode==0,okay.stderr
