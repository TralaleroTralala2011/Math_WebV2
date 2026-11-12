"""NEON V8: no unreviewed exam material, accurate coverage and role isolation."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.roadmap_v2_routes import coverage, pool, _data
from app.admin_routes import ensure_admin_schema_and_account
from app.auth.routes import create_admin_token
from database import database as db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DATABASE_PATH',tmp_path/'v8.db')
    db.init_database()
    ensure_admin_schema_and_account()
    with TestClient(app) as c:
        yield c


def admin_auth():
    c=db.get_connection()
    try:
        r=c.execute('SELECT id,username,auth_version FROM admin_accounts LIMIT 1').fetchone()
    finally:
        c.close()
    return {'Authorization':'Bearer '+create_admin_token(r['id'],r['username'],r['auth_version'])}


def student_auth(c):
    r=c.post('/api/auth/register',json={'username':'V8Learner','password':'SafePass1234!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}


def test_only_checked_tiers_count_towards_diagnostic_coverage(client):
    for grade,n in ((10,49),(11,51),(12,50)):
        stats=coverage(grade)
        assert stats['topic_count']==n
        assert stats['topics_meeting_3_per_tier']==0
        assert stats['topics_with_30_certified']==0
        for t in stats['topics']:
            assert t['certified']==0
            assert sum(t['by_difficulty'].values())==0
            assert t['unlabeled']==t['available']
    topic=next(t for t in _data()[0] if t['id']=='ham_so_bac_hai')
    candidates=pool(topic)
    assert len(candidates)>=30
    assert all(q['source']=='lesson-candidate' and q['difficulty'] is None for q in candidates)


def test_admin_grade_coverage_is_protected_and_not_inflated(client):
    sh=student_auth(client)
    assert client.get('/api/admin/qf2/coverage-detail',headers=sh).status_code==403
    assert client.get('/api/admin/qf2/coverage-detail').status_code in (401,403)
    ah=admin_auth()
    r=client.get('/api/admin/qf2/coverage-detail',headers=ah)
    assert r.status_code==200,r.text
    data=r.json()
    assert data['topic_count']==150
    assert data['certified_topic_exams']==0
    assert data['total_missing_certified_questions']==4500
    assert data['total_tier_gaps']==1350
    assert all(t['missing_to_30']==30 for t in data['topics'])
    assert client.get('/api/admin/qf2/coverage-detail?grade=11',headers=ah).json()['topic_count']==51
    assert client.get('/api/admin/qf2/coverage-detail?grade=13',headers=ah).status_code==422


def test_placement_quality_warning_and_admin_cannot_take_student_exam(client):
    ah=admin_auth()
    assert client.post('/api/roadmap-v2/start',headers=ah,json={'grade':10,'mode':'placement'}).status_code==403
    sh=student_auth(client)
    r=client.post('/api/roadmap-v2/start',headers=sh,json={'grade':10,'mode':'placement'})
    assert r.status_code==200,r.text
    data=r.json()
    assert data['assessment_quality']['complete_three_tier_coverage'] is False
    assert data['assessment_quality']['unreviewed_items']>0
    result=client.post('/api/roadmap-v2/submit/'+data['attempt_id'],headers=sh,json={'answers':{}})
    assert result.status_code==200,result.text
    summary=result.json()
    assert summary['diagnostic_completeness']['three_tiers_complete'] is False
    assert summary['verified_question_count']==0
    assert len(summary['review'])==summary['total']


def test_unreviewed_items_never_unlock_topic_exam(client):
    sh=student_auth(client)
    r=client.post('/api/roadmap-v2/start',headers=sh,json={'grade':10,'mode':'placement'}).json()
    result=client.post('/api/roadmap-v2/submit/'+r['attempt_id'],headers=sh,json={'answers':{}}).json()
    target=result['roadmap_order'][0]
    response=client.post('/api/roadmap-v2/start',headers=sh,json={'grade':10,'mode':'topic','topic_id':target})
    assert response.status_code==409,response.text
    assert response.json()['detail']['available']==0
    assert response.json()['detail']['required']==30


def test_v8_stylesheet_present_on_active_pages():
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    assert (root/'css/neon-v8.css').is_file()
    for name in ('index.html','learn.html','learning-path.html','battle.html','chat.html','admin.html'):
        assert 'css/neon-v8.css?v=8' in (root/name).read_text(encoding='utf-8')


def test_frontend_server_denies_private_files_but_keeps_public_assets():
    import importlib.util,functools
    from threading import Thread
    from http.server import ThreadingHTTPServer
    from urllib.request import urlopen,Request
    from urllib.error import HTTPError
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    spec=importlib.util.spec_from_file_location('mw_secure_static',root/'scripts/serve_frontend.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(module.MathWebStaticHandler,directory=str(root)))
    runner=Thread(target=server.serve_forever,daemon=True);runner.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}'
        with urlopen(base+'/js/roadmap-v5.js') as r:
            assert r.status==200
        for suffix in ('/backend/database/mathweb.db','/backend/database/.mathweb_hmac_secret',
                       '/backend/app/main.py','/scripts/serve_frontend.py','/mathweb_work/backend/',
                       '/.gitignore','/backend%2Fdatabase%2Fmathweb.db'):
            for method in ('GET','HEAD'):
                with pytest.raises(HTTPError) as exc:
                    urlopen(Request(base+suffix,method=method))
                assert exc.value.code==404,(suffix,method)
    finally:
        server.shutdown();server.server_close();runner.join(timeout=5)
