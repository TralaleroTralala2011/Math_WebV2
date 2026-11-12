"""Ensure a registered username may be used for repeat login without re-registering."""
from fastapi.testclient import TestClient
from app.main import app
from database import database as db
from app.matchmaking.routes import init_matchmaking_tables

def test_repeat_login_same_account(tmp_path,monkeypatch):
    path=tmp_path/'persistent.db'
    monkeypatch.setattr(db,'DATABASE_PATH',path)
    monkeypatch.setenv('MATHWEB_DB_PATH',str(path))
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as client:
        created=client.post('/api/auth/register',json={'username':'StudentReturning','password':'safePass123'})
        assert created.status_code==200,created.text
        token=created.json()['token']
        assert client.get('/api/auth/me',headers={'Authorization':'Bearer '+token}).status_code==200
        logout=client.post('/api/auth/logout',headers={'Authorization':'Bearer '+token})
        assert logout.status_code==200,logout.text
        again=client.post('/api/auth/login',json={'username':'StudentReturning','password':'safePass123'})
        assert again.status_code==200,again.text
        assert client.get('/api/auth/me',headers={'Authorization':'Bearer '+again.json()['token']}).status_code==200
        assert client.post('/api/auth/register',json={'username':'StudentReturning','password':'safePass123'}).status_code in (400,409)
