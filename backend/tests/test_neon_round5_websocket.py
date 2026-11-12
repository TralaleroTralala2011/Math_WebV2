"""Exercise the authenticated WS transport while retaining REST persistence."""
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app
from database import database as db
from app.matchmaking.routes import init_matchmaking_tables

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'chat_round5.sqlite3')
    db.init_database();init_matchmaking_tables()
    with TestClient(app) as c:yield c


def register(client,name):
    r=client.post('/api/auth/register',json={'username':name,'password':'SafePass1234'})
    assert r.status_code==200,r.text
    return r.json()['user'],r.json()['token']


def befriend(client,a,at,b,bt):
    assert client.post('/api/friends/request',json={'player_id':b['player_id']},headers={'Authorization':'Bearer '+at}).status_code==200
    req=client.get('/api/friends/requests',headers={'Authorization':'Bearer '+bt}).json()[0]
    assert client.post('/api/friends/accept/'+str(req['id']),headers={'Authorization':'Bearer '+bt}).status_code==200


def test_websocket_two_clients_receive_persisted_chat(client):
    a,at=register(client,'WSUserAlpha1')
    b,bt=register(client,'WSUserBeta2')
    befriend(client,a,at,b,bt)
    with client.websocket_connect('/api/live/chat/'+str(b['id'])) as ws_a:
        ws_a.send_json({'type':'auth','token':at})
        assert ws_a.receive_json()['type']=='ready'
        with client.websocket_connect('/api/live/chat/'+str(a['id'])) as ws_b:
            ws_b.send_json({'type':'auth','token':bt})
            assert ws_b.receive_json()['type']=='ready'
            response=client.post(f'/api/chat/{b["id"]}/messages',json={'content':'Xin chào qua WS'},headers={'Authorization':'Bearer '+at})
            assert response.status_code==200,response.text
            packet_a=ws_a.receive_json();packet_b=ws_b.receive_json()
            assert packet_a['type']==packet_b['type']=='message'
            assert packet_b['message']['content']=='Xin chào qua WS'
            assert packet_b['message']['id']==response.json()['id']


def test_websocket_requires_valid_user_and_friendship(client):
    a,at=register(client,'WSUserGamma3')
    b,bt=register(client,'WSUserDelta4')
    with client.websocket_connect('/api/live/chat/'+str(b['id'])) as ws:
        ws.send_json({'type':'auth','token':at})
        with pytest.raises(WebSocketDisconnect) as exc:ws.receive_json()
        assert exc.value.code==1008
