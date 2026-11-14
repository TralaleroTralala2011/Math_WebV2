"""V53 focused regressions: no original files deleted; both players select 1-3 topics."""
import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables
from app.ai.routes import service
from database import database as db

ROOT=Path(__file__).resolve().parents[2]

@pytest.fixture
def pair(tmp_path, monkeypatch):
    path=tmp_path/'users.sqlite'
    monkeypatch.setenv('MATHWEB_DB_PATH',str(path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'hist.sqlite'))
    monkeypatch.setattr(db,'DATABASE_PATH',path)
    db.init_database();init_matchmaking_tables()
    with TestClient(app) as client:
        users=[]
        for name in ('V53Alpha','V53Beta'):
            response=client.post('/api/auth/register',json={'username':name,'password':'TempTestPassword8!'})
            assert response.status_code==200,response.text
            body=response.json();users.append((body['user'],{'Authorization':'Bearer '+body['token']}))
        yield client,*users


def test_source_preserved_and_new_bank_restores():
    from app.ai.engine.b56_bank import ensure_b56_bank
    source=ROOT/'question_bank_v254_source/Question_Bank_V254_B56_BO_SUNG_CO_KIEM_TRA.zip'
    manifest=json.loads((ROOT/'backend/app/ai/storage/v254_b56_seed_manifest.json').read_text('utf8'))
    with zipfile.ZipFile(source) as bank:
        assert bank.testzip() is None
        assert sum(n.lower().endswith('.docx') for n in bank.namelist())==150
    assert manifest['counts']['indexed']>=80000
    assert manifest['status']=='candidate_not_independently_certified'
    recovered=ensure_b56_bank()
    assert recovered and recovered.exists()
    for grade,topic in ((10,'chia_du'),(11,'cap_so_cong'),(12,'mat_cau')):
        # This is not a certification of each candidate's mathematical truth.
        result=service._v254_candidates(grade,topic,'medium','short_answer')
        assert isinstance(result,list)


def test_dual_confirmation_and_one_to_three_choices(pair):
    client,(a,ha),(b,hb)=pair
    send=client.post('/api/matchmaking/invite',headers=ha,json={'player_id':b['player_id'],'grade':10})
    assert send.status_code==200,send.text
    mid=send.json()['match_id']
    original=client.get(f'/api/matchmaking/match/{mid}',headers=ha).json()
    assert original['status']=='INVITED' and not original['started_at'] and not original['questions']
    accepted=client.post(f'/api/matchmaking/match/{mid}/accept',headers=hb)
    assert accepted.status_code==200 and accepted.json()['status']=='SELECTING'
    assert client.post(f'/api/matchmaking/match/{mid}/topics',headers=ha,json={'topics':[]}).status_code==422
    assert client.post(f'/api/matchmaking/match/{mid}/topics',headers=ha,json={'topics':['chia_du']*4}).status_code==422
    assert client.post(f'/api/matchmaking/match/{mid}/topics',headers=ha,json={'topics':['unknown_grade_topic']}).status_code==422
    first=client.post(f'/api/matchmaking/match/{mid}/topics',headers=ha,json={'topics':['chia_du']})
    assert first.status_code==200 and first.json()['status']=='SELECTING',first.text
    waiting=client.get(f'/api/matchmaking/match/{mid}',headers=ha).json()
    assert waiting['started_at'] is None and waiting['topic_selection']['my_ready']
    assert not client.get(f'/api/matchmaking/match/{mid}',headers=hb).json()['topic_selection']['my_ready']
    second=client.post(f'/api/matchmaking/match/{mid}/topics',headers=hb,json={'topics':['chia_du','menh_de_tap_hop']})
    assert second.status_code==200,second.text
    assert second.json()['status']=='PLAYING'
    matches=[client.get(f'/api/matchmaking/match/{mid}',headers=h).json() for h in (ha,hb)]
    assert all(m['status']=='PLAYING' and m['started_at']==second.json()['started_at'] for m in matches)
    assert matches[0]['questions']==matches[1]['questions']
    assert matches[0]['questions'] and len({q['question'] for q in matches[0]['questions']})==len(matches[0]['questions'])
    assert all('answer' not in q and 'solution' not in q for q in matches[0]['questions'])
    assert client.post(f'/api/matchmaking/match/{mid}/topics',headers=hb,json={'topics':['chia_du']}).json()['started_at']==second.json()['started_at']


def test_random_pair_has_no_running_clock_until_both_choose(pair):
    client,(a,ha),(b,hb)=pair
    assert client.post('/api/matchmaking/random/join',headers=ha,json={'grade':10}).json()['status']=='QUEUED'
    joined=client.post('/api/matchmaking/random/join',headers=hb,json={'grade':10})
    assert joined.status_code==200 and joined.json()['status']=='MATCHED'
    mid=joined.json()['match_id']
    for h in (ha,hb):
        match=client.get(f'/api/matchmaking/match/{mid}',headers=h).json()
        assert match['status']=='SELECTING' and match['started_at'] is None
        assert not match['questions']
    assert client.post(f'/api/matchmaking/match/{mid}/start',headers=ha).status_code==400
    topics=client.get('/api/matchmaking/topic-catalog',headers=ha,params={'grade':10})
    assert topics.status_code==200
    names={x['id'] for x in topics.json()['topics']}
    assert 'chia_du' in names and 'chia_het' in names
