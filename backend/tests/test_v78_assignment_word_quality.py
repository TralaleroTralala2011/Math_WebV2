import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import admin_routes
from app.ai.engine.assignment_quality import eligible_assignment_questions, content_signature, math_method_family
from database import database as database_module
from app.matchmaking.routes import init_matchmaking_tables


def test_019_word_source_has_only_relevant_nonrepeated_originals():
    rows=eligible_assignment_questions(10,'he_bat_phuong_trinh','medium','mixed')
    assert 0<len(rows)<30
    assert len(rows)==len({content_signature(r['question']) for r in rows})
    assert len(rows)==len({math_method_family('he_bat_phuong_trinh',r['question']) for r in rows})
    assert all('x' in r['question'] and 'y' in r['question'] for r in rows)
    assert all('Một bạn biến đổi a(' not in r['question'] for r in rows)
    assert all(r['source']=='150_CHU_DE_WORD' and r['source_word'].endswith('.docx') for r in rows)
    assert eligible_assignment_questions(10,'he_bat_phuong_trinh','expert','mixed')==[]
    assert eligible_assignment_questions(10,'he_bat_phuong_trinh','medium','multiple_choice')==[]
    assert all('Mệnh đề thứ hai được suy ra' not in r['question'] for r in rows)

@pytest.fixture
def client_with_users(tmp_path,monkeypatch):
    db=tmp_path/'v78.db'
    monkeypatch.setenv('MATHWEB_DB_PATH',str(db))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.db'))
    monkeypatch.setattr(database_module,'DATABASE_PATH',db)
    database_module.init_database()
    init_matchmaking_tables()
    monkeypatch.setattr(admin_routes,'BOOTSTRAP_PASSWORD','TestOnlyAdminPass2026')
    admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as client:
        reg=client.post('/api/auth/register',json={'username':'V78student','password':'safePass123'})
        assert reg.status_code==200,reg.text
        al=client.post('/api/auth/login',json={'username':'admin19022011','password':'TestOnlyAdminPass2026'})
        assert al.status_code==200,al.text
        yield client, {'Authorization':'Bearer '+al.json()['token']}, {'Authorization':'Bearer '+reg.json()['token']},reg.json()['user']['id'],db

def test_bad_assignment_rejected_before_creation(client_with_users):
    c,admin,student,uid,db=client_with_users
    bad=c.post('/api/admin/learning/assignments',headers=admin,json={
        'title':'AI TAP HOC','grade':10,'topic':'he_bat_phuong_trinh',
        'difficulty':'expert','question_type':'mixed','question_count':30,'student_ids':[uid]
    })
    assert bad.status_code==422,bad.text
    assert '0 câu' in bad.json()['detail']
    with sqlite3.connect(db) as con:
        assert con.execute('select count(*) from learning_assignments').fetchone()[0]==0
    status=c.get('/api/admin/learning/assignment-bank/status',headers=admin,
        params={'grade':10,'topic':'he_bat_phuong_trinh','difficulty':'medium'})
    assert status.status_code==200,status.text
    assert 0<status.json()['eligible_distinct_count']<30


def test_legacy_bad_ai_homework_quarantined_and_source_exact(client_with_users,monkeypatch):
    c,admin,student,uid,db=client_with_users
    # Ensure fallback AI is not called even if configured.
    from app.ai.routes import service
    monkeypatch.setattr(service,'generate_set',lambda *a,**k:(_ for _ in ()).throw(AssertionError('AI fallback must not run')))
    created=c.post('/api/admin/learning/assignments',headers=admin,json={
        'title':'Luyện đúng chủ đề','grade':10,'topic':'he_bat_phuong_trinh',
        'difficulty':'medium','question_type':'short_answer','question_count':4,'student_ids':[uid]
    })
    assert created.status_code==200,created.text
    aid=created.json()['id']
    old=[{'question':'Một bạn biến đổi a(5+1) thành 11. a=2?', 'answer':'12','options':[], 'source':'AI runtime'}]
    with sqlite3.connect(db) as con:
        con.execute("UPDATE learning_assignment_targets SET status='in_progress',questions_json=? WHERE assignment_id=? and user_id=?",(json.dumps(old),aid,uid))
    started=c.post(f'/api/admin/learning/assignments/{aid}/start',headers=student,json={})
    assert started.status_code==200,started.text
    q=started.json()['questions']
    assert len(q)==4
    assert all('Một bạn biến đổi' not in r['question'] for r in q)
    with sqlite3.connect(db) as con:
        captured=con.execute('select old_questions_json from learning_assignment_quarantine where assignment_id=?',(aid,)).fetchone()
        assert captured is not None and json.loads(captured[0])==old
        original=[json.loads(row[0]) for row in con.execute('select questions_json from learning_assignment_targets where assignment_id=?',(aid,))][0]
    assert all(x['question']==y['question'] for x,y in zip(q,original))
    assert all(x['source_word'].endswith('.docx') for x in original)
    assert all('answer' not in x for x in q)


def test_invalid_existing_30_never_repeats_bad_prompts(client_with_users):
    c,admin,student,uid,db=client_with_users
    with sqlite3.connect(db) as con:
        admin_id=con.execute('select id from admin_accounts').fetchone()[0]
        row=con.execute("INSERT INTO learning_assignments(title,description,grade,topic,difficulty,question_type,question_count,due_at,status,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('AI TAP HOC','',10,'he_bat_phuong_trinh','expert','mixed',30,None,'published',admin_id,'2026-11-16','2026-11-16'))
        aid=row.lastrowid
        con.execute("INSERT INTO learning_assignment_targets(assignment_id,user_id,status,questions_json) VALUES(?,?,'in_progress',?)",(aid,uid,json.dumps([{'question':'Một bạn biến đổi a(3+1) thành 7','answer':'8','options':[]}])))
    res=c.post(f'/api/admin/learning/assignments/{aid}/start',headers=student,json={})
    assert res.status_code==422,res.text
    assert '0 câu' in res.json()['detail']
    with sqlite3.connect(db) as con:
        record=con.execute('select status,questions_json from learning_assignment_targets where assignment_id=?',(aid,)).fetchone()
        assert record==('assigned','[]')
        assert con.execute('select count(*) from learning_assignment_quarantine where assignment_id=?',(aid,)).fetchone()[0]==1

def test_admin_can_repair_broken_30_question_assignment_without_erasing_old_copy(client_with_users):
    c,admin,student,uid,db=client_with_users
    with sqlite3.connect(db) as con:
        aid=con.execute("INSERT INTO learning_assignments(title,description,grade,topic,difficulty,question_type,question_count,due_at,status,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('AI TAP HOC','',10,'he_bat_phuong_trinh','expert','mixed',30,None,'published',1,'2026-11-16','2026-11-16')).lastrowid
        con.execute("INSERT INTO learning_assignment_targets(assignment_id,user_id,status,questions_json) VALUES(?,?,'in_progress',?)",(aid,uid,json.dumps([{'question':'bad generated question','answer':'fake'}])))
    impossible=c.put(f'/api/admin/learning/assignments/{aid}/repair',headers=admin,json={'difficulty':'expert','question_type':'mixed','question_count':30})
    assert impossible.status_code==422,impossible.text
    good=c.put(f'/api/admin/learning/assignments/{aid}/repair',headers=admin,json={'difficulty':'medium','question_type':'short_answer','question_count':3})
    assert good.status_code==200,good.text
    with sqlite3.connect(db) as con:
        assert con.execute('select count(*) from learning_assignment_quarantine where assignment_id=?',(aid,)).fetchone()[0]==1
    started=c.post(f'/api/admin/learning/assignments/{aid}/start',headers=student,json={})
    assert started.status_code==200,started.text
    assert len(started.json()['questions'])==3
