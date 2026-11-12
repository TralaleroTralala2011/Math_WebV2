"""New access-control, server-grading and roadmap coverage regressions."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from database import database as db
from app import admin_routes as admin
from app.roadmap_v2_routes import coverage, pool, _data


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'round5.db')
    db.init_database()
    admin.ensure_admin_schema_and_account()
    with TestClient(app) as c:yield c


def student(c,name):
    r=c.post('/api/auth/register',json={'username':name,'password':'Complex123!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}


def test_150_topic_inventory_and_placement_access(client):
    ha=student(client,'StudentA1')
    for grade,number in [(10,49),(11,51),(12,50)]:
        stats=coverage(grade)
        assert stats['topic_count']==number
        assert stats['topics_with_questions']==number
        assert stats['topics_meeting_3_per_tier']<number
    assert client.get('/api/roadmap-v2/catalog').status_code==401
    assert client.get('/api/admin/qf2/summary',headers=ha).status_code==403
    assert client.post('/api/roadmap-v2/start',json={'grade':10,'mode':'placement'}).status_code==401
    r=client.post('/api/roadmap-v2/start',headers=ha,json={'grade':10,'mode':'placement'})
    assert r.status_code==200,r.text
    d=r.json();assert len({q['topic_id'] for q in d['questions']})==49
    assert all('correct' not in q and 'explanation' not in q for q in d['questions'])
    assert client.post('/api/roadmap-v2/start',headers=ha,json={'grade':10,'mode':'topic','topic_id':'menh_de_tap_hop'}).status_code==403
    hb=student(client,'StudentB1')
    assert client.post('/api/roadmap-v2/submit/'+d['attempt_id'],headers=hb,json={'answers':{}}).status_code==404
    # Only the current student's token can access or grade their attempt.
    one=d['questions'][0]
    answers={one['qid']:0 if one['question_type']=='multiple_choice' else '0'}
    result=client.post('/api/roadmap-v2/submit/'+d['attempt_id'],headers=ha,json={'answers':answers})
    assert result.status_code==200,result.text
    data=result.json();assert data['total']==len(d['questions'])
    assert data['correct']+data['wrong']+data['skipped']==data['total']
    assert [q['number'] for q in data['review']]==list(range(1,len(d['questions'])+1))
    assert client.post('/api/roadmap-v2/submit/'+d['attempt_id'],headers=ha,json={'answers':answers}).status_code==409
    assert client.get('/api/roadmap-v2/status/10',headers=ha).json()['placement_complete'] is True
    assert client.get('/api/roadmap-v2/status/10',headers=hb).json()['placement_complete'] is False


def test_topic_exam_refuses_short_bank_without_fake_questions(client):
    ha=student(client,'StudentC1')
    d=client.post('/api/roadmap-v2/start',headers=ha,json={'grade':10,'mode':'placement'}).json()
    client.post('/api/roadmap-v2/submit/'+d['attempt_id'],headers=ha,json={'answers':{}})
    order=client.get('/api/roadmap-v2/latest/10',headers=ha).json()['result']['roadmap_order']
    from app.roadmap_v2_routes import _data
    t=next(t for t in _data()[0] if t['id']==order[0])
    response=client.post('/api/roadmap-v2/start',headers=ha,json={'grade':10,'mode':'topic','topic_id':t['id']})
    assert response.status_code==409 if len(pool(t))<30 else response.status_code==200
    if response.status_code==409:assert response.json()['detail']['required']==30


def test_question_factory_rejects_student_tokens_and_invalid_data(client):
    ha=student(client,'StudentD1')
    assert client.post('/api/admin/qf2/candidates',headers=ha,json={}).status_code==403 or client.post('/api/admin/qf2/candidates',headers=ha,json={}).status_code==422
