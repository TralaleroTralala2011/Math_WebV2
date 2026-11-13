"""V47: two-account API regression and static dialog contract.
No external Render/GitHub request is made by this test suite.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from app.admin_routes import ensure_admin_schema_and_account
from app.presence.routes import is_user_online
from database import database as db


@pytest.fixture
def pair(tmp_path, monkeypatch):
    db_path = tmp_path / 'users.sqlite3'
    monkeypatch.setattr(db, 'DATABASE_PATH', db_path)
    monkeypatch.setenv('MATHWEB_DB_PATH', str(db_path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'hist.sqlite'))
    db.init_database()
    init_matchmaking_tables()
    ensure_admin_schema_and_account()
    with TestClient(app) as c:
        people = []
        for name in ('V47Alpha', 'V47Beta'):
            r = c.post('/api/auth/register', json={'username':name, 'password':'FakeTestPassword12'})
            assert r.status_code == 200, r.text
            data = r.json()
            people.append((data['user'], {'Authorization':'Bearer '+data['token']}))
        yield c, people[0], people[1]


def test_search_friends_presence_and_battle_player(pair):
    c, (a, ha), (b, hb) = pair
    assert c.post('/api/presence/heartbeat', headers=ha).status_code == 200
    assert c.post('/api/presence/heartbeat', headers=hb).status_code == 200
    found = c.get('/api/friends/search', params={'player_id':b['player_id']}, headers=ha)
    assert found.status_code == 200, found.text
    assert found.json()['online'] is True
    assert found.json()['friend_status'] is None
    player = c.get('/api/matchmaking/player', params={'player_id':b['player_id']}, headers=ha)
    assert player.status_code == 200, player.text
    assert player.json()['online'] is True
    assert c.post('/api/friends/request', json={'player_id':b['player_id']}, headers=ha).status_code == 200
    pending = c.get('/api/friends/search', params={'player_id':b['player_id']}, headers=ha)
    assert pending.json()['friend_status'] == 'pending'
    inbox = c.get('/api/friends/requests', headers=hb).json()
    assert len(inbox) == 1
    assert c.post(f"/api/friends/accept/{inbox[0]['id']}", headers=hb).status_code == 200
    accepted = c.get('/api/friends/search', params={'player_id':b['player_id']}, headers=ha)
    assert accepted.json()['is_friend'] is True
    friends = c.get('/api/friends', headers=ha)
    assert friends.status_code == 200 and friends.json()[0]['online'] is True


def test_random_match_two_users(pair):
    c, (a, ha), (b, hb) = pair
    first = c.post('/api/matchmaking/random/join', json={'grade':12}, headers=ha)
    assert first.status_code == 200, first.text
    assert first.json()['status'] == 'QUEUED'
    second = c.post('/api/matchmaking/random/join', json={'grade':12}, headers=hb)
    assert second.status_code == 200, second.text
    assert second.json()['status'] == 'MATCHED'
    mid = second.json()['match_id']
    assert c.get('/api/matchmaking/current', headers=ha).status_code == 200
    assert c.get(f'/api/matchmaking/match/{mid}', headers=ha).status_code == 200
    assert c.get(f'/api/matchmaking/match/{mid}', headers=hb).status_code == 200


def test_invite_alive_after_45_seconds(pair):
    c, (a, ha), (b, hb) = pair
    invited = c.post('/api/matchmaking/invite', json={'player_id': b['player_id']}, headers=ha)
    assert invited.status_code == 200, invited.text
    mid = invited.json()['match_id']
    old = (datetime.now(timezone.utc)-timedelta(seconds=45)).isoformat()
    with db.get_connection() as conn:
        conn.execute('UPDATE match_invites SET created_at=? WHERE match_id=?', (old, mid))
        conn.execute('UPDATE matches SET created_at=? WHERE id=?',(old,mid))
        conn.commit()
    inbox = c.get('/api/matchmaking/invites',headers=hb)
    assert inbox.status_code==200, inbox.text
    assert str(mid) in str(inbox.json())
    assert c.post(f'/api/matchmaking/match/{mid}/accept', headers=hb).status_code==200


def test_presence_grace_period():
    now=datetime.now(timezone.utc)
    assert is_user_online((now-timedelta(seconds=75)).isoformat())
    assert not is_user_online((now-timedelta(seconds=100)).isoformat())
    assert not is_user_online(None)


def test_popup_uses_top_layer_dialog_and_preserves_legacy_hooks():
    root=Path(__file__).resolve().parents[2]
    html=(root/'practice.html').read_text(encoding='utf8')
    assert '<dialog\n        class="knowledge-popup"\n        id="knowledgePopup"' in html
    assert '</dialog>' in html
    assert 'id="practiceOverlay"' in html
    assert 'js/practice-modal-v47.js' in html
    assert 'js/practise.js' in html
    assert 'practice-modal-hotfix-v46.js?v=1' not in html
