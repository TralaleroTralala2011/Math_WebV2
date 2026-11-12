"""Integration regression: two authenticated sockets, disconnect, reconnect and state sync.
This does not replace an actual two-browser UI test.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from app.admin_routes import ensure_admin_schema_and_account
from database import database as db
import pytest

@pytest.fixture
def connected_users(tmp_path,monkeypatch):
    db_path=tmp_path/'reconnect.sqlite3'
    monkeypatch.setenv('MATHWEB_DB_PATH',str(db_path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.sqlite3'))
    monkeypatch.setattr(db,'DATABASE_PATH',db_path)
    db.init_database();init_matchmaking_tables();ensure_admin_schema_and_account()
    with TestClient(app) as client:
        people=[]
        for name in ('V23ReconnectAlpha','V23ReconnectBeta'):
            r=client.post('/api/auth/register',json={'username':name,'password':'TestPasswordV23!123'})
            assert r.status_code==200,r.text
            item=r.json();people.append((item['user'],item['token']))
        yield client,*people

def test_two_players_disconnect_reconnect_and_resync(connected_users):
    c,(a,token_a),(b,token_b)=connected_users
    ha={'Authorization':'Bearer '+token_a}
    hb={'Authorization':'Bearer '+token_b}
    invite=c.post('/api/matchmaking/invite',headers=ha,json={'player_id':b['player_id']})
    assert invite.status_code==200,invite.text
    mid=invite.json()['match_id']
    assert c.post(f'/api/matchmaking/match/{mid}/accept',headers=hb).status_code==200
    assert c.post(f'/api/matchmaking/match/{mid}/start',headers=ha).status_code==200
    url_a=f'/api/ai/battle/ws/{mid}/{a["id"]}?token={token_a}'
    url_b=f'/api/ai/battle/ws/{mid}/{b["id"]}?token={token_b}'
    with c.websocket_connect(url_a) as wa:
        assert wa.receive_json()['type']=='state'
        with c.websocket_connect(url_b) as wb:
            assert wb.receive_json()['type']=='state'
        # B has disconnected; A can still request authoritative match state.
        wa.send_json({'type':'sync'})
        assert any(wa.receive_json().get('type')=='state' for _ in range(4))
        with c.websocket_connect(url_b) as wb2:
            assert wb2.receive_json()['type']=='state'
            wb2.send_json({'type':'sync'})
            assert any(wb2.receive_json().get('type')=='state' for _ in range(4))
