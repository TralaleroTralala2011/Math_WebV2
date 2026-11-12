"""NEON V7 regression: reviewed lessons, saved placement, generators, security, UI."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import admin_routes
from app.auth.routes import create_admin_token
from app.qf2_verified_generators import all_candidates
from app.question_factory_v2_routes import Candidate, norm_exact
from app.roadmap_v2_routes import _data, pool, grade_question, coverage
from database import database as db

ROOT=Path(__file__).resolve().parents[2]


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'v7.db')
    db.init_database();admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as c:yield c


def admin_headers():
    c=db.get_connection()
    try:r=c.execute('SELECT id,username,auth_version FROM admin_accounts LIMIT 1').fetchone()
    finally:c.close()
    return {'Authorization':'Bearer '+create_admin_token(r['id'],r['username'],r['auth_version'])}


def student(c,name):
    r=c.post('/api/auth/register',json={'username':name,'password':'Complex123!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}


def test_9_generators_90_questions_with_varied_formats_and_tiers():
    forms=[Candidate.model_validate(x) for x in all_candidates()]
    assert len(forms)==8 and sum(len(x.questions) for x in forms)==80
    assert {f.grade for f in forms}=={10,11,12}
    for form in forms:
        assert len(form.questions)==10
        assert len({norm_exact(q.question) for q in form.questions})==10
        assert [q.question_type for q in form.questions].count('multiple_choice')==7
        assert [q.question_type for q in form.questions].count('written')==2
        assert [q.question_type for q in form.questions].count('true_false')==1
        assert [q.difficulty for q in form.questions].count('nền tảng')==4
        assert [q.difficulty for q in form.questions].count('trung cấp')==3
        assert [q.difficulty for q in form.questions].count('nâng cao')==3
        for q in form.questions:
            assert q.explanation and len(q.explanation)>=24
            if q.question_type=='multiple_choice':
                assert len(q.choices)==len(set(q.choices))==4
                assert q.choices[q.correct_index]==q.answer


def test_batch_admin_only_idempotent_no_auto_publish(client):
    sh=student(client,'V7Student1')
    path='/api/admin/qf2/generate/verified-batch'
    assert client.post(path,headers=sh).status_code==403
    ah=admin_headers()
    topic=next(t for t in _data()[0] if t['id']=='so_phuc')
    before=len(pool(topic))
    r=client.post(path,headers=ah)
    assert r.status_code==200,r.text
    assert r.json()['created_forms']==9 and r.json()['created_questions']==90
    assert len(pool(topic))==before
    assert client.post(path,headers=ah).json()['already_present']==9
    catalog=client.get('/api/admin/qf2/generate/catalog',headers=ah).json()
    assert len(catalog['generators'])==9
    assert client.get('/api/admin/qf2/coverage',headers=sh).status_code==403


def test_review_existing_lesson_tier_and_reject_bad_question(client):
    ah=admin_headers();sh=student(client,'V7Student2')
    t=next(t for t in _data()[0] if t['id']=='menh_de_tap_hop')
    before=len(pool(t))
    endpoint='/api/admin/qf2/lesson-questions/menh_de_tap_hop/0/review'
    payload={'approved':True,'difficulty':'nền tảng','independently_checked':False,
             'notes':'Đã kiểm tra đối chiếu tất cả các lựa chọn và lời giải.'}
    assert client.post(endpoint,headers=sh,json=payload).status_code==403
    assert client.post(endpoint,headers=ah,json=payload).status_code==409
    payload['independently_checked']=True
    assert client.post(endpoint,headers=ah,json=payload).status_code==200
    assert pool(t)[0]['difficulty']=='nền tảng'
    assert coverage(10)['topics'][0]['by_difficulty']['nền tảng']>=1
    payload['approved']=False
    assert client.post(endpoint,headers=ah,json=payload).status_code==200
    assert len(pool(t))==before-1
    assert client.get('/api/admin/qf2/lesson-queue?grade=10&limit=10',headers=sh).status_code==403
    q=client.get('/api/admin/qf2/lesson-queue?grade=10&limit=10',headers=ah).json()
    assert q['total']>=10 and q['reviewed']>=1


def test_placement_draft_saved_resume_and_user_isolation(client):
    alice=student(client,'V7Student3');bob=student(client,'V7Student4')
    exam=client.post('/api/roadmap-v2/start',headers=alice,json={'grade':10,'mode':'placement'}).json()
    one=exam['questions'][0]
    assert 'correct' not in one and 'explanation' not in one
    endpoint='/api/roadmap-v2/draft/'+exam['attempt_id']
    answers={one['qid']:0}
    assert client.post(endpoint,headers=bob,json={'answers':answers}).status_code==404
    assert client.post(endpoint,headers=alice,json={'answers':{'invalid-id':0}}).status_code==422
    assert client.post(endpoint,headers=alice,json={'answers':answers}).json()['saved']
    resumed=client.post('/api/roadmap-v2/start',headers=alice,json={'grade':10,'mode':'placement'}).json()
    assert resumed['resumed'] and resumed['draft_answers']==answers
    assert 'correct' not in resumed['questions'][0]
    assert client.post('/api/roadmap-v2/submit/'+exam['attempt_id'],headers=alice,json={'answers':answers}).status_code==200
    assert client.post(endpoint,headers=alice,json={'answers':answers}).status_code==409


def test_true_false_complex_and_fraction_grading():
    for expected,answer in [('Đúng','true'),('Sai',False)]:
        assert grade_question({'question_type':'true_false','correct':expected},answer)=='correct'
    for expected,answer in [('3+2i','3 + 2i'),('2-3i','2 - 3i'),('0+0i','0'),('3','6/2')]:
        assert grade_question({'question_type':'written','correct':expected},answer)=='correct'
    assert grade_question({'question_type':'written','correct':'3+2i'},'3-2i')=='wrong'


def test_real_activity_heatmap_never_invents_streak(client):
    sh=student(client,'V7Student5')
    assert client.get('/api/games/activity-heatmap').status_code in (401,403)
    r=client.get('/api/games/activity-heatmap',headers=sh)
    assert r.status_code==200,r.text
    d=r.json();assert len(d['days'])==84
    assert sum(x['sessions'] for x in d['days'])==0
    assert d['timezone']=='Asia/Ho_Chi_Minh'


def test_all_active_games_have_neon_v7_assets_and_mobile_nav():
    pages=list((ROOT/'games').rglob('*.html'))
    assert len(pages)==529
    for p in pages:
        html=p.read_text(encoding='utf-8')
        assert 'neon-v7-game.css?v=7' in html,p
        assert 'neon-v7-game.js?v=7' in html,p
    for name in ('css/neon-v7.css','css/neon-v7-game.css','js/neon-v7-game.js',
                 'js/neon-v7-experience.js','js/admin-neon-v7.js'):
        assert (ROOT/name).is_file(),name
    admin=(ROOT/'admin.html').read_text(encoding='utf-8')
    assert 'admin-neon-v7.js' in admin
    for page in ('index.html','learn.html','learning-path.html','battle.html','chat.html'):
        assert 'admin-neon-v7.js' not in (ROOT/page).read_text(encoding='utf-8')
