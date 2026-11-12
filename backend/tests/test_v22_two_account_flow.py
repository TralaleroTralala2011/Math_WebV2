"""V22: API-level two-user integration regression. Browser UI is NOT covered."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from app.admin_routes import ensure_admin_schema_and_account
from database import database as db

@pytest.fixture
def users(tmp_path, monkeypatch):
    db_path = tmp_path / 'mathweb_e2e.sqlite3'
    monkeypatch.setenv('MATHWEB_DB_PATH', str(db_path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'ai.sqlite3'))
    monkeypatch.setattr(db, 'DATABASE_PATH', db_path)
    db.init_database(); init_matchmaking_tables(); ensure_admin_schema_and_account()
    with TestClient(app) as c:
        people = []
        for name in ['QAUserV22Alpha', 'QAUserV22Beta']:
            r = c.post('/api/auth/register',json={'username':name,'password':'TestPasswordV22!123'})
            assert r.status_code == 200, r.text
            d=r.json();people.append((d['user'],{'Authorization':'Bearer '+d['token']}))
        yield c,people[0],people[1]

def test_battle_invite_accept_start_two_users(users):
    c,(a,ha),(b,hb)=users
    r=c.post('/api/matchmaking/invite',headers=ha,json={'player_id':b['player_id']});assert r.status_code == 200,r.text
    mid=r.json()['match_id']
    assert c.get(f'/api/matchmaking/match/{mid}',headers=ha).status_code == 200
    unauthorized=c.post(f'/api/matchmaking/match/{mid}/accept',headers=ha)
    assert unauthorized.status_code in (403,404,409),unauthorized.text
    r=c.post(f'/api/matchmaking/match/{mid}/accept',headers=hb)
    assert r.status_code == 200,r.text
    r=c.post(f'/api/matchmaking/match/{mid}/start',headers=ha)
    assert r.status_code == 200,r.text
    for headers in (ha,hb):
        assert c.get(f'/api/matchmaking/match/{mid}',headers=headers).status_code == 200
        assert c.get(f'/api/matchmaking/match/{mid}/progress',headers=headers).status_code == 200

def test_friends_chat_notifications_two_users(users):
    c,(a,ha),(b,hb)=users
    r=c.post('/api/friends/request',headers=ha,json={'player_id':b['player_id']});assert r.status_code == 200,r.text
    inbox=c.get('/api/friends/requests',headers=hb);assert inbox.status_code == 200,inbox.text
    requests=inbox.json(); assert requests,requests
    rid=requests[0]['id']
    accepted=c.post(f'/api/friends/accept/{rid}',headers=hb);assert accepted.status_code == 200,accepted.text
    sent=c.post(f'/api/chat/{b["id"]}/messages',headers=ha,json={'content':'V22 test chat message'})
    assert sent.status_code == 200,sent.text
    msgs=c.get(f'/api/chat/{a["id"]}/messages',headers=hb)
    assert msgs.status_code == 200,msgs.text
    assert 'V22 test chat message' in str(msgs.json())
    bell=c.get('/api/notifications/unread-count',headers=hb)
    assert bell.status_code == 200,bell.text

def test_battle_full_match_skip_finishes(users):
    c,(a,ha),(b,hb)=users
    invited=c.post('/api/matchmaking/invite',headers=ha,json={'player_id':b['player_id']})
    assert invited.status_code == 200,invited.text
    mid=invited.json()['match_id']
    assert c.post(f'/api/matchmaking/match/{mid}/accept',headers=hb).status_code == 200
    assert c.post(f'/api/matchmaking/match/{mid}/start',headers=ha).status_code == 200
    for i in range(10):
        for header in (ha,hb):
            r=c.post(f'/api/matchmaking/match/{mid}/skip',headers=header,json={'question_index':i})
            assert r.status_code == 200,(i,r.status_code,r.text)
    result=c.get(f'/api/matchmaking/match/{mid}/result',headers=ha)
    assert result.status_code == 200,result.text
    assert 'FINISHED' in str(result.json()).upper(),result.json()

def test_battle_two_authenticated_websocket_connections(users):
    c,(a,ha),(b,hb)=users
    invited=c.post('/api/matchmaking/invite',headers=ha,json={'player_id':b['player_id']})
    assert invited.status_code == 200,invited.text
    mid=invited.json()['match_id']
    assert c.post(f'/api/matchmaking/match/{mid}/accept',headers=hb).status_code==200
    assert c.post(f'/api/matchmaking/match/{mid}/start',headers=ha).status_code==200
    tok1=ha['Authorization'].split(' ',1)[1];tok2=hb['Authorization'].split(' ',1)[1]
    with c.websocket_connect(f'/api/ai/battle/ws/{mid}/{a["id"]}?token={tok1}') as wa:
        assert wa.receive_json()['type']=='state'
        with c.websocket_connect(f'/api/ai/battle/ws/{mid}/{b["id"]}?token={tok2}') as wb:
            assert wb.receive_json()['type']=='state'
            wa.send_json({'type':'sync'})
            assert any(wa.receive_json().get('type')=='state' for _ in range(3))
            wb.send_json({'type':'sync'})
            assert any(wb.receive_json().get('type')=='state' for _ in range(3))
