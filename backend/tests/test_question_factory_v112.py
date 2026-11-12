import concurrent.futures
import time
import pytest
from fastapi.testclient import TestClient
from question_factory import storage, worker, engine
from question_factory.api import create_app


@pytest.fixture
def db(tmp_path):
    p=str(tmp_path/'factory.sqlite')
    storage.initialize(p)
    storage.seed_samples(p)
    return p


def approve_all(db):
    from question_factory.catalog import SAMPLES
    for _,_,_,items in SAMPLES:
        for slug,*_ in items:
            storage.approve(db,slug,'independent-reviewer')


def test_generator_and_independent_verifier():
    from question_factory.catalog import SAMPLES
    for _,_,_,items in SAMPLES:
        for _,family,_,_,difficulty in items:
            seen=set()
            for n in range(10):
                q=engine.generate(family,n,difficulty)
                valid,reason=engine.independently_verify(q)
                assert valid, (family,n,reason)
                assert q['fingerprint'] not in seen, (family,n)
                seen.add(q['fingerprint'])
                tampered=dict(q,answer='999999999999')
                assert engine.independently_verify(tampered)[0] is False


def test_no_approval_means_no_published_questions(db):
    assert storage.enqueue(db,10)==0
    assert worker.run(db,workers=4)==0
    assert storage.progress(db)['verified_questions']==0


def test_parallel_workers_and_repeated_run_are_idempotent(db):
    approve_all(db)
    assert storage.enqueue(db,10)==9
    assert storage.enqueue(db,10)==0
    assert worker.run(db,workers=4)==9
    state=storage.progress(db)
    assert state['verified_questions']==90
    assert state['job_status']=={'done':9}
    assert len(storage.read_questions(db,'10-phuong-trinh',50))==20
    assert worker.run(db,workers=4)==0
    assert storage.progress(db)['verified_questions']==90


def test_crashed_worker_lease_recovery(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    con=storage.connect(db)
    job=storage.claim(con,'worker-will-crash',lease_sec=0.02)
    assert job
    q=engine.generate('linear_equation',0,'nền tảng',seed_key='10-phuong-trinh:linear-equation')
    valid,metadata=engine.independently_verify(q)
    storage.store_question(con,job['id'],'worker-will-crash',q,valid,metadata)
    con.close()
    time.sleep(0.04)
    assert worker.process_one(db,'replacement-worker')
    assert storage.progress(db)['verified_questions']==10
    assert storage.progress(db)['job_status']=={'done':1}


def test_pause_and_resume(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    storage.set_paused(db,True)
    assert worker.run(db,workers=3)==0
    storage.set_paused(db,False)
    assert worker.run(db,workers=3)==1


def test_budget_in_questions(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    storage.set_limit(db,3)
    assert worker.run(db,workers=1)==1
    assert storage.progress(db)['verified_questions']==3
    assert storage.progress(db)['job_status']=={'pending':1}
    storage.set_limit(db,0)
    # A failure has a short bounded retry delay; force its next attempt ready.
    con=storage.connect(db)
    con.execute('UPDATE jobs SET next_attempt_at=0 WHERE status="pending"')
    con.close()
    assert worker.run(db,workers=1)==1
    assert storage.progress(db)['verified_questions']==10


def test_type_semantics_uniqueness_and_admin_auth(db):
    app=create_app(db,admin_token='test-secret')
    client=TestClient(app)
    assert client.get('/api/factory/health').status_code==200
    assert client.post('/api/factory/admin/enqueue',json={'per_type':10}).status_code==403
    assert client.post('/api/factory/admin/types/linear-equation/approve',
                       headers={'X-Admin-Token':'test-secret'},json={'reviewer':'reviewer'}).status_code==200
    assert client.post('/api/factory/admin/enqueue',
                       headers={'X-Admin-Token':'test-secret'},json={'per_type':10}).json()['jobs_enqueued']==1
    assert worker.run(db,workers=2)==1
    r=client.get('/api/factory/topics/10-phuong-trinh/questions')
    assert r.status_code==200
    assert len(r.json()['items'])==10
    with pytest.raises(Exception):
        con=storage.connect(db)
        try:
            con.execute("""INSERT INTO archetypes(id,topic_id,family,name,method_signature,difficulty)
                     VALUES('fake','10-phuong-trinh','linear_equation','new','inverse-linear-operations','nền tảng')""")
        finally: con.close()


def test_different_topic_read_is_isolated(db):
    approve_all(db)
    storage.enqueue(db,2)
    worker.run(db,workers=2)
    assert len(storage.read_questions(db,'11-dao-ham'))==2
    assert storage.read_questions(db,'nonexistent')==[]


def test_cost_reservation_ceiling_is_transactional(db):
    assert storage.reserve_cost(db,'api-request-1',1) is False
    storage.set_cost_limit(db,100)
    assert storage.reserve_cost(db,'api-request-1',60) is True
    assert storage.reserve_cost(db,'api-request-1',60) is True
    assert storage.reserve_cost(db,'api-request-2',50) is False
    with pytest.raises(ValueError):
        storage.settle_cost(db,'api-request-1',61)
    storage.settle_cost(db,'api-request-1',30)
    assert storage.reserve_cost(db,'api-request-1',60) is False
    assert storage.reserve_cost(db,'api-request-2',60) is True
    assert storage.progress(db)['cost_reserved_cents']==60
    with pytest.raises(ValueError):
        storage.set_cost_limit(db,80)
    storage.settle_cost(db,'api-request-2',55)
    assert storage.progress(db)['cost_used_cents']==85
    assert storage.progress(db)['cost_reserved_cents']==0
    assert storage.reserve_cost(db,'api-request-3',20) is False
    assert storage.reserve_cost(db,'api-request-3',15) is True
    storage.release_cost(db,'api-request-3')
    assert storage.progress(db)['cost_reserved_cents']==0


def test_public_api_does_not_leak_correct_answers(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    worker.run(db,workers=1)
    client=TestClient(create_app(db,admin_token='secret'))
    public=client.get('/api/factory/topics/10-phuong-trinh/questions').json()['items']
    assert len(public)==10
    assert all('answer' not in q and 'solution' not in q for q in public)
    private=client.get('/api/factory/admin/topics/10-phuong-trinh/questions',
                       headers={'X-Admin-Token':'secret'}).json()['items']
    assert len(private)==10
    assert all('answer' in q and 'solution' in q for q in private)


def test_topics_import_validates_count_and_rolls_back(db,tmp_path):
    import json
    from question_factory.topic_import import import_topics
    filename=tmp_path/'topics.json'
    data=[{'id':'new-toan-10','grade':10,'name':'Chủ đề mới 10'},
          {'id':'new-toan-11','grade':11,'name':'Chủ đề mới 11'}]
    filename.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError):
        import_topics(db,filename,expected_count=150)
    assert import_topics(db,filename,expected_count=2)==2
    data.append({'id':'new-toan-11','grade':11,'name':'Trùng'})
    filename.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError):
        import_topics(db,filename,expected_count=3)
    con=storage.connect(db)
    assert con.execute('SELECT COUNT(*) FROM topics').fetchone()[0]==9
    con.close()


def test_real_catalog_has_exact_150_topics(tmp_path):
    from question_factory.bootstrap import initialize_factory
    path=str(tmp_path/'real-catalog.sqlite3')
    initialize_factory(path)
    state=storage.progress(path)
    assert state['topics']==150
    assert state['archetypes']==0  # must not fabricate 300,000 independent methods
    assert state['verified_questions']==0
    assert len(storage.list_topics(path))==150
    assert sum(t['grade']==10 for t in storage.list_topics(path))==49
    assert sum(t['grade']==11 for t in storage.list_topics(path))==51
    assert sum(t['grade']==12 for t in storage.list_topics(path))==50
    assert len(storage.list_topics(path))==len({t['id'] for t in storage.list_topics(path)})


def test_one_time_answer_session_prevents_answer_leaks_and_replay(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    assert worker.run(db,workers=2)==1
    client=TestClient(create_app(db,admin_token='test-secret'))
    next_response=client.get('/api/factory/next',params={'topic_id':'10-phuong-trinh','surface':'battle'})
    assert next_response.status_code==200,next_response.text
    body=next_response.json()
    assert body['surface']=='battle'
    assert 'answer' not in body and 'solution' not in body
    assert 'correct_answer' not in body
    session=body['session_id']
    graded=client.post('/api/factory/answer',json={'session_id':session,'answer':'bad-answer'})
    assert graded.status_code==200
    assert graded.json()['is_correct'] is False
    assert 'correct_answer' in graded.json() and 'solution' in graded.json()
    replay=client.post('/api/factory/answer',json={'session_id':session,'answer':'bad-answer'})
    assert replay.status_code==404
    assert client.get('/api/factory/next',params={'topic_id':'does-not-exist'}).status_code==404


def test_factory_router_in_main_without_changing_existing_routes():
    from app.main import app
    paths={x.path for x in app.routes}
    assert '/api/factory/progress' in paths
    assert '/api/factory/next' in paths
    assert '/api/factory/answer' in paths
    assert '/api/matchmaking/invite' in paths
    assert '/api/auth/register' in paths
    assert '/api/friends/request' in paths


def test_demo_preserves_official_catalog_150(tmp_path):
    from question_factory.bootstrap import initialize_factory
    path=initialize_factory(str(tmp_path/'official.sqlite3'))
    storage.seed_samples(path)
    state=storage.progress(path)
    assert state['topics']==150
    assert state['archetypes']==9
    assert state['approved_archetypes']==0
    storage.approve(path,'linear-equation','teacher')
    assert storage.enqueue(path)==1
    assert worker.run(path,workers=2)==1
    assert len(storage.read_questions(path,'phuong_trinh'))==10


def test_terminalizes_expired_lease_on_final_attempt(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10,max_attempts=1)
    con=storage.connect(db)
    job=storage.claim(con,'abandoned',lease_sec=0.01)
    assert job
    time.sleep(0.04)
    assert storage.claim(con,'replacement',lease_sec=2) is None
    con.close()
    assert storage.progress(db)['job_status']=={'failed':1}


def test_multiple_types_of_same_verified_family_avoid_identical_streams(db):
    # Same implementation family is NOT automatically a distinct independent
    # mathematical method. This only tests stream isolation and fingerprinting.
    first=engine.generate('linear_equation',0,'nền tảng',seed_key='topic-1:type-1')
    second=engine.generate('linear_equation',0,'nền tảng',seed_key='topic-2:type-2')
    assert first['fingerprint'] != second['fingerprint']
    assert engine.independently_verify(first)[0]
    assert engine.independently_verify(second)[0]


def test_active_session_capacity_is_bounded(db):
    storage.approve(db,'linear-equation','reviewer')
    storage.enqueue(db,10)
    worker.run(db,workers=2)
    first=storage.create_answer_session(db,'10-phuong-trinh',max_active_sessions=1)
    assert first
    with pytest.raises(storage.LimitReached):
        storage.create_answer_session(db,'10-phuong-trinh',max_active_sessions=1)
    assert storage.submit_answer_session(db,first['session_id'],'5')
    assert storage.create_answer_session(db,'10-phuong-trinh',max_active_sessions=1)
