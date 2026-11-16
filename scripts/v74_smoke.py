"""Non-destructive V74 checks. Uses a fresh temporary SQLite DB ONLY."""
from __future__ import annotations
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = '''
import sys
sys.path.insert(0, 'backend')
from fastapi.testclient import TestClient
from app.main import app
origin={'Origin':'https://tralalerotralala2011.github.io'}
with TestClient(app) as c:
  assert c.get('/health').status_code == 200
  assert c.options('/api/admin/users/1',headers={**origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'authorization,content-type'}).headers['access-control-allow-origin']==origin['Origin']
  register=c.post('/api/auth/register',json={'username':'qa_v74_user','password':'TempTestPass123'})
  assert register.status_code == 200, register.text
  login=c.post('/api/auth/login',json={'username':'qa_v74_user','password':'TempTestPass123'})
  assert login.status_code == 200, login.text
  headers={**origin,'Authorization':'Bearer '+login.json()['token']}
  event={'event_id':'v74-test-event-00000001','event_type':'question_answered','topic':'day_so','question_text':'1 + 1 = ?', 'selected_answer':'2','is_correct':True,'progress':5}
  r=c.post('/api/activity/events',json=event,headers=headers)
  assert r.status_code==201 and not r.json()['verified'],r.text
  r=c.post('/api/activity/events',json=event,headers=headers)
  assert r.status_code==201 and r.json()['duplicate']
  assert c.post('/api/activity/events',json=event,headers=origin).status_code == 401
  admin=c.post('/api/auth/login',json={'username':'admin19022011','password':'SmokeAdminPassword123'})
  assert admin.status_code == 200, admin.text
  adminheaders={**origin,'Authorization':'Bearer '+admin.json()['token']}
  assert c.get('/api/admin/storage-status',headers=adminheaders).status_code == 200
  d=c.get('/api/admin/users/1',headers=adminheaders)
  assert d.status_code==200 and d.json()['activity_total']==1,d.text
  assert d.headers['access-control-allow-origin']==origin['Origin']
  print('V74 smoke: CORS, auth, activity, dedup, admin, storage all passed.')
'''

with tempfile.TemporaryDirectory(prefix='mathweb_v74_smoke_') as td:
  env=os.environ.copy()
  env.update({
    'MATHWEB_DATA_DIR':td,
    'MATHWEB_DB_PATH':str(Path(td)/'accounts.db'),
    'MATH_WEB_SECRET_KEY':'smoke-test-only-strong-secret-1234567890-abcdef',
    'MATHWEB_BOOTSTRAP_ADMIN_PASSWORD':'SmokeAdminPassword123',
  })
  completed=subprocess.run([sys.executable,'-c',SCRIPT],cwd=str(ROOT),env=env,check=False)
  raise SystemExit(completed.returncode)
