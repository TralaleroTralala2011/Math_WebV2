"""V50 regressions for the specific bug reports, independent of live Render data."""
from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from database import database as db

ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture
def pair(tmp_path,monkeypatch):
    db_path=tmp_path/'v50.sqlite'
    monkeypatch.setenv('MATHWEB_DB_PATH',str(db_path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'hist.sqlite'))
    monkeypatch.setattr(db,'DATABASE_PATH',db_path)
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as client:
        accounts=[]
        for username in ('V50Alpha','V50Beta'):
            r=client.post('/api/auth/register',json={'username':username,'password':'TempTestPassword8!'})
            assert r.status_code==200,r.text
            d=r.json(); accounts.append((d['user'],{'Authorization':'Bearer '+d['token']}))
        yield client,*accounts

def test_both_practice_routes_have_same_preferred_interface_and_working_dialog():
    a=(ROOT/'practice.html').read_text('utf8')
    b=(ROOT/'practise.html').read_text('utf8')
    assert a==b
    s=BeautifulSoup(a,'html.parser')
    popup=s.find(id='knowledgePopup')
    assert popup is not None and popup.name=='dialog'
    assert s.find(id='practiceOverlay') and s.find(id='popupClose')
    assert s.find(id='knowledgeGrid')
    assert s.find(id='learningCoach')  # preferred practise interface
    assert any('practice-modal-v47.js' in (x.get('src') or '') for x in s.select('script[src]'))
    assert any('js/practise.js' in (x.get('src') or '') for x in s.select('script[src]'))
    assert 'CHỌN CHẾ ĐỘ LUYỆN TẬP' in a


def test_friend_ui_ids_bound_to_account_logic():
    doc=BeautifulSoup((ROOT/'account.html').read_text('utf8'),'html.parser')
    js=(ROOT/'js/account.js').read_text('utf8')
    for element in ('friendPlayerId','searchFriendButton','friendSearchResult','friendList','friendRequests'):
        assert doc.find(id=element), element
        assert ('"'+element+'"') in js,element
    assert 'loadFriends().catch(console.warn)' in js


def test_friend_request_accept_visible_to_both_accounts(pair):
    c,(u1,h1),(u2,h2)=pair
    assert c.get('/api/friends/search',params={'player_id':u2['player_id']},headers=h1).status_code==200
    request=c.post('/api/friends/request',json={'player_id':u2['player_id']},headers=h1)
    assert request.status_code==200,request.text
    inbox=c.get('/api/friends/requests',headers=h2)
    assert inbox.status_code==200 and len(inbox.json())==1
    accept=c.post('/api/friends/accept/'+str(inbox.json()[0]['id']),headers=h2)
    assert accept.status_code==200,accept.text
    assert any(friend['player_id']==u2['player_id'] for friend in c.get('/api/friends',headers=h1).json())
    assert any(friend['player_id']==u1['player_id'] for friend in c.get('/api/friends',headers=h2).json())


def test_accept_invite_starts_two_client_match_atomically_and_syncs_timer(pair):
    c,(u1,h1),(u2,h2)=pair
    sent=c.post('/api/matchmaking/invite',json={'player_id':u2['player_id'],'grade':10},headers=h1)
    assert sent.status_code==200,sent.text
    mid=sent.json()['match_id']
    incoming=c.get('/api/matchmaking/invites',headers=h2)
    assert incoming.status_code==200 and incoming.json()['count']>=1
    r=c.post(f'/api/matchmaking/match/{mid}/accept',headers=h2)
    assert r.status_code==200,r.text
    assert r.json()['status']=='PLAYING'
    assert r.json()['started_at'] and r.json()['duration_seconds']==300
    p1=c.get(f'/api/matchmaking/match/{mid}',headers=h1)
    p2=c.get(f'/api/matchmaking/match/{mid}',headers=h2)
    assert p1.status_code==p2.status_code==200
    for info in (p1.json(),p2.json()):
        assert info['status']=='PLAYING'
        assert info['started_at']==r.json()['started_at']
        assert info['duration_seconds']==300
        assert info['server_now']
        assert info['questions']
        assert not any('answer' in q or 'solution' in q for q in info['questions'])
    assert p1.json()['questions']==p2.json()['questions']
    # Old client start endpoint must be safe/idempotent after accept.
    assert c.post(f'/api/matchmaking/match/{mid}/start',headers=h1).status_code==200


def test_mobile_shared_nav_contract():
    css=(ROOT/'css/v42-shared-navbar-flush.css').read_text('utf8')
    assert 'position:fixed!important;top:0!important' in css
    assert '.mw-v5-navdock {' in css and 'position:fixed!important;bottom:0!important' in css
    for name in ('account.html','battle.html','practice.html','practise.html'):
        assert 'v42-shared-navbar-flush.css' in (ROOT/name).read_text('utf8')


def test_legacy_random_join_with_empty_post_body(pair):
    c,(u1,h1),(u2,h2)=pair
    first=c.post('/api/matchmaking/random/join',headers=h1)
    assert first.status_code==200,first.text
    second=c.post('/api/matchmaking/random/join',headers=h2)
    assert second.status_code==200,second.text
    assert second.json()['status']=='MATCHED'
