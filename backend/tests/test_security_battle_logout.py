"""Regression for security defects found in the full-site audit."""
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app
from app.auth.routes import SECRET_KEY
from app.matchmaking.routes import init_matchmaking_tables
from app.admin_routes import ensure_admin_schema_and_account
from database import database as db


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "secure_mathweb.db"
    monkeypatch.setenv("MATHWEB_DB_PATH", str(db_path))
    monkeypatch.setenv("MATHWEB_AI_HISTORY_DB_PATH", str(tmp_path / "ai_history.sqlite3"))
    monkeypatch.setattr(db, "DATABASE_PATH", db_path)
    db.init_database()
    init_matchmaking_tables()
    ensure_admin_schema_and_account()
    with TestClient(app) as c:
        yield c


def register(client, username):
    res = client.post('/api/auth/register', json={'username': username, 'password': 'VeryStrongPass123'})
    assert res.status_code == 200, res.text
    return res.json()['user'], res.json()['token']


def test_signing_key_is_not_public_fallback():
    assert len(SECRET_KEY) >= 32
    assert SECRET_KEY != 'MATH_WEB_LOCAL_SECRET'


def test_logout_really_revokes_learner_token(client):
    _, token = register(client, 'LogoutTester')
    headers = {'Authorization': 'Bearer ' + token}
    assert client.get('/api/auth/me', headers=headers).status_code == 200
    response = client.post('/api/auth/logout', headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()['logged_out'] is True
    assert client.get('/api/auth/me', headers=headers).status_code == 401
    assert client.post('/api/auth/logout', headers=headers).status_code == 401


def test_logout_really_revokes_admin_token(client):
    from app.auth.routes import create_admin_token
    conn = db.get_connection()
    try:
        admin = conn.execute('SELECT id, username, auth_version FROM admin_accounts WHERE username=?',
                             ('admin19022011',)).fetchone()
        token = create_admin_token(admin['id'], admin['username'], admin['auth_version'])
    finally:
        conn.close()
    headers = {'Authorization': 'Bearer ' + token}
    assert client.get('/api/admin/users', headers=headers).status_code == 200
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    assert client.get('/api/admin/users', headers=headers).status_code in (401,403)


def test_websocket_requires_token_participation_and_uses_sqlite_matches(client):
    user1, t1 = register(client, 'BattleSocketAlpha')
    user2, t2 = register(client, 'BattleSocketBeta')
    user3, t3 = register(client, 'BattleSocketStranger')
    sent = client.post('/api/matchmaking/invite',
        headers={'Authorization':'Bearer '+t1},
        json={'player_id':user2['player_id']})
    assert sent.status_code == 200, sent.text
    match_id = sent.json()['match_id']
    route = f'/api/ai/battle/ws/{match_id}/{user1["id"]}'
    for url in (route, route + '?token=' + t3, route + '?token=' + t2):
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(url) as ws:
                ws.receive_json()
        assert exc.value.code == 1008
    with client.websocket_connect(route + '?token=' + t1) as ws:
        state = ws.receive_json()
        assert state['type'] == 'state'
        assert state['status'] == 'INVITED'
        assert state['progress']['answered'] == 0
        ws.send_json({'type': 'sync', 'fake_correct': 999})
        state = ws.receive_json()
        assert state['progress']['correct'] == 0
    # Guest cannot impersonate either participant, regardless of path.
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f'/api/ai/battle/ws/{match_id}/{user3["id"]}?token={t3}') as ws:
            ws.receive_json()
    assert exc.value.code == 1008


def test_database_reinitialization_does_not_recreate_or_reset_admin(client):
    from app.auth.routes import hash_password
    from app.admin_routes import ADMIN_USERNAME
    conn = db.get_connection()
    try:
        admin = conn.execute('SELECT id FROM admin_accounts WHERE username=?', (ADMIN_USERNAME,)).fetchone()
        assert admin is not None
        conn.execute('UPDATE admin_accounts SET password_hash=? WHERE id=?',
                     (hash_password('ChosenStrongAdminPassword_123'), admin['id']))
        conn.commit()
    finally:
        conn.close()
    db.init_database()
    ensure_admin_schema_and_account()
    result = client.post('/api/auth/login',
        json={'username': ADMIN_USERNAME, 'password': 'ChosenStrongAdminPassword_123'})
    assert result.status_code == 200, result.text
    assert result.json()['user']['role'] == 'admin'
    conn = db.get_connection()
    try:
        assert conn.execute('SELECT COUNT(*) FROM users WHERE username=?', (ADMIN_USERNAME,)).fetchone()[0] == 0
    finally:
        conn.close()
