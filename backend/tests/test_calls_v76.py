"""V76 WebRTC signalling integration checks, no production database used."""
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.chat import calls


def test_friends_only_call_signalling(monkeypatch):
    users={'alpha':{'id':1,'username':'An'},'beta':{'id':2,'username':'Bình'}}
    monkeypatch.setattr(calls,'get_current_user',lambda auth: users[auth.removeprefix('Bearer ')])
    def friend_only(a,b):
        if {a,b}!={1,2}:
            raise HTTPException(status_code=403)
    monkeypatch.setattr(calls,'validate_chat_target',friend_only)
    calls._sockets.clear();calls._calls.clear();calls._last_invite.clear()
    app=FastAPI();app.include_router(calls.router)
    origin={'origin':'https://tralalerotralala2011.github.io'}
    with TestClient(app) as client:
        with client.websocket_connect('/api/live/calls',headers=origin) as a:
            a.send_json({'type':'auth','token':'alpha'});assert a.receive_json()['type']=='ready'
            with client.websocket_connect('/api/live/calls',headers=origin) as b:
                b.send_json({'type':'auth','token':'beta'});assert b.receive_json()['type']=='ready'
                a.send_json({'type':'call-request','peer_id':2,'mode':'video'})
                incoming=b.receive_json(); assert incoming['type']=='incoming-call'
                cid=incoming['call_id'];assert incoming['mode']=='video'
                ringing=a.receive_json();assert ringing['type']=='call-ringing' and ringing['call_id']==cid
                b.send_json({'type':'call-accept','call_id':cid})
                assert a.receive_json()['type']=='call-accepted'
                offer={'type':'offer','sdp':'v=0\r\n'}
                a.send_json({'type':'call-offer','call_id':cid,'payload':offer})
                assert b.receive_json()['payload']==offer
                answer={'type':'answer','sdp':'v=0\r\n'}
                b.send_json({'type':'call-answer','call_id':cid,'payload':answer})
                assert a.receive_json()['payload']==answer
                ice={'candidate':'candidate:abc','sdpMid':'0','sdpMLineIndex':0}
                b.send_json({'type':'call-ice','call_id':cid,'payload':ice})
                assert a.receive_json()['payload']==ice
                a.send_json({'type':'call-end','call_id':cid})
                assert b.receive_json()['type']=='call-ended'
                assert not calls._calls
    calls._sockets.clear(); calls._calls.clear()


def test_call_cannot_be_placed_to_strangers(monkeypatch):
    monkeypatch.setattr(calls,'get_current_user',lambda auth:{'id':1,'username':'An'})
    monkeypatch.setattr(calls,'validate_chat_target',lambda a,b: (_ for _ in ()).throw(HTTPException(status_code=403)))
    calls._sockets.clear();calls._calls.clear();calls._last_invite.clear()
    app=FastAPI();app.include_router(calls.router)
    with TestClient(app) as client:
        with client.websocket_connect('/api/live/calls',headers={'origin':'https://tralalerotralala2011.github.io'}) as ws:
            ws.send_json({'type':'auth','token':'alpha'})
            assert ws.receive_json()['type']=='ready'
            ws.send_json({'type':'call-request','peer_id':2,'mode':'audio'})
            assert ws.receive_json()['type']=='call-error'
    assert not calls._calls
    calls._sockets.clear()
