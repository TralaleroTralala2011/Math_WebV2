"""V51 scoped front-end and social regression contracts; V50 data untouched."""
from pathlib import Path
import re
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from database import database as db
import pytest

ROOT=Path(__file__).resolve().parents[2]

def test_legacy_practice_paths_are_identical_and_routable():
    a=(ROOT/'practice.html').read_bytes();b=(ROOT/'practise.html').read_bytes()
    assert a==b
    doc=BeautifulSoup(b,'html.parser')
    assert doc.select_one('#knowledgePopup') and doc.select_one('#knowledgeGrid')
    assert doc.select_one('dialog#knowledgePopup')
    assert any('practise.js' in (node.get('src') or '') for node in doc.select('script[src]'))
    nav=(ROOT/'js/neon-v5.js').read_text('utf8')
    assert "['practise.html','◎','Luyện tập']" in nav

def test_mobile_fixed_nav_both_ends():
    css=(ROOT/'css/v42-shared-navbar-flush.css').read_text('utf8')
    assert 'position:fixed!important;top:0!important' in css
    assert 'position:fixed!important;bottom:0!important' in css
    assert 'padding-top:62px!important' in css

def test_friend_incoming_pending_and_failed_request_retry():
    js=(ROOT/'js/account.js').read_text('utf8')
    assert 'profile.requester_id' in js and 'profile.relation_id' in js
    assert 'Chấp nhận lời mời' in js and 'acceptFriend(incomingRequestId)' in js
    assert 'if (!ok && addButton.isConnected)' in js

def test_battle_server_monotonic_timer_and_guard():
    js=(ROOT/'js/battle.js').read_text('utf8')
    assert 'serverSyncedAtMs + (performance.now() - performanceSyncedAtMs)' in js
    assert 'if (!currentMatchId || acceptingInvite) return;' in js
    assert 'getSyncedBattleNow() - gameStartedAt' in js

@pytest.fixture
def pair(tmp_path,monkeypatch):
    path=tmp_path/'v51.sqlite'
    monkeypatch.setenv('MATHWEB_DB_PATH',str(path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'hist.sqlite'))
    monkeypatch.setattr(db,'DATABASE_PATH',path)
    db.init_database();init_matchmaking_tables()
    with TestClient(app) as client:
        people=[]
        for name in ('V51Alpha','V51Beta'):
            r=client.post('/api/auth/register',json={'username':name,'password':'SafeTestPassword18!'})
            assert r.status_code==200,r.text
            d=r.json();people.append((d['user'],{'Authorization':'Bearer '+d['token']}))
        yield client,*people

def test_incoming_friend_search_can_identify_request_origin(pair):
    c,(a,ha),(b,hb)=pair
    r=c.post('/api/friends/request',json={'player_id':b['player_id']},headers=ha)
    assert r.status_code==200,r.text
    incoming=c.get('/api/friends/search',params={'player_id':a['player_id']},headers=hb)
    d=incoming.json()
    assert incoming.status_code==200
    assert d['friend_status']=='pending'
    assert d['requester_id']==d['id']
    assert d['relation_id']==r.json()['request_id']
    assert c.post(f"/api/friends/accept/{d['relation_id']}",headers=hb).status_code==200

def test_random_match_and_direct_invite_begin_with_shared_questions(pair):
    c,(a,ha),(b,hb)=pair
    x=c.post('/api/matchmaking/random/join',json={'grade':10},headers=ha)
    y=c.post('/api/matchmaking/random/join',json={'grade':10},headers=hb)
    assert x.status_code==y.status_code==200
    mid=y.json()['match_id']
    # STARTING transitions when the players enter their shared match.
    assert c.post(f'/api/matchmaking/match/{mid}/start',headers=ha).status_code==200
    p1=c.get(f'/api/matchmaking/match/{mid}',headers=ha).json()
    p2=c.get(f'/api/matchmaking/match/{mid}',headers=hb).json()
    assert p1['questions']==p2['questions'] and p1['grade']==10
    assert p1['started_at']==p2['started_at']
