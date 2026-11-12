"""Verify generated numeric instances stay within one pending type."""
import re
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import admin_routes
from app.auth.routes import create_admin_token
from app.question_factory_v2_routes import build_parabola_vertex_candidate,norm,norm_exact
from app.roadmap_v2_routes import pool,_data
from database import database as db


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'neon-v6-generator.db')
    db.init_database()
    admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as c:yield c


def headers():
    c=db.get_connection()
    try:row=c.execute('SELECT id,username,auth_version FROM admin_accounts LIMIT 1').fetchone()
    finally:c.close()
    return {'Authorization':'Bearer '+create_admin_token(row['id'],row['username'],row['auth_version'])}


def test_one_form_ten_distinct_correct_vertex_questions():
    form=build_parabola_vertex_candidate()
    assert form.grade==10 and form.topic_id=='ham_so_bac_hai'
    assert len(form.questions)==10
    assert len({norm_exact(q.question) for q in form.questions})==10
    assert len({norm(q.question) for q in form.questions})==1  # numeric changes are NOT new types
    for q in form.questions:
        a,b,c=map(int,re.search(r'y = (-?\d+)x² \+ \((-?\d+)\)x \+ \((-?\d+)\)',q.question).groups())
        h,k=map(int,re.search(r'\((-?\d+); (-?\d+)\)',q.answer).groups())
        assert a!=0 and -b==2*a*h and a*h*h+b*h+c==k
        assert q.choices[q.correct_index]==q.answer
        assert len(set(q.choices))==4 and len(q.explanation)>=24


def test_generator_admin_only_pending_and_deduplicated(client):
    endpoint='/api/admin/qf2/generate/parabola-vertex'
    assert client.post(endpoint).status_code in (401,403)
    student=client.post('/api/auth/register',json={'username':'StudentV6','password':'Complex123!'})
    assert student.status_code==200
    sh={'Authorization':'Bearer '+student.json()['token']}
    assert client.post(endpoint,headers=sh).status_code==403
    auth=headers()
    topic=next(t for t in _data()[0] if t['id']=='ham_so_bac_hai')
    before=len(pool(topic))
    r=client.post(endpoint,headers=auth)
    assert r.status_code==200,r.text
    assert r.json()['generated_types']==1 and r.json()['generated_questions']==10
    assert r.json()['status']=='pending_review'
    assert len(pool(topic))==before  # no auto publication
    assert client.post(endpoint,headers=auth).status_code==409
