"""V139 regression: opt-in per-sequence anti-repeat and legacy migration."""
import hashlib
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from question_factory import api, storage


def sample_db(tmp_path, methods=2, questions_each=3):
    db = str(tmp_path / 'factory.sqlite3')
    storage.initialize(db)
    with storage.connect(db) as con, storage.transaction(con):
        con.execute('INSERT INTO topics(id,grade,name) VALUES (?,?,?)',('t-10',10,'Sample topic'))
        for m in range(methods):
            mid = f'example-{m}'
            con.execute('''INSERT INTO archetypes
               (id,topic_id,family,name,method_signature,difficulty,review_status)
               VALUES (?,?,?,?,?,?,?)''',(mid,'t-10',mid,mid,mid,'easy','approved'))
            for n in range(questions_each):
                qid = f'question-{m}-{n}'
                con.execute('''INSERT INTO questions(id,archetype_id,ordinal,fingerprint,
                    stem,answer,solution,params_json,difficulty,validation_json,status,verified_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (qid,mid,n,qid,'Question '+qid,str(n),'Solution '+qid,
                     '{}','easy','{}','verified',1.0))
    return db


def test_consecutive_methods_and_all_unique_questions(tmp_path):
    db=sample_db(tmp_path,methods=2,questions_each=3)
    seq='opaque_session_123456789'
    picked=[storage.create_answer_session(db,'t-10',sequence_key=seq) for _ in range(6)]
    assert len({r['id'] for r in picked}) == 6
    assert all(a['archetype_id'] != b['archetype_id'] for a,b in zip(picked,picked[1:]))
    with storage.connect(db) as con:
        row = con.execute('SELECT sequence_hash FROM answer_sessions LIMIT 1').fetchone()
        assert row['sequence_hash']==hashlib.sha256(seq.encode()).hexdigest()
        assert seq not in row['sequence_hash']


def test_single_method_fallback_avoids_question_repeat_until_exhaustion(tmp_path):
    db=sample_db(tmp_path,methods=1,questions_each=3)
    seq='opaque_session_abcdefgh'
    seen=[storage.create_answer_session(db,'t-10',sequence_key=seq)['id'] for _ in range(3)]
    assert len(set(seen))==3
    assert storage.create_answer_session(db,'t-10',sequence_key=seq)['id'] in seen


def test_legacy_without_key_still_works_and_answer_not_leaked(tmp_path):
    db=sample_db(tmp_path)
    with TestClient(api.create_app(db)) as client:
        r=client.get('/api/factory/next',params={'topic_id':'t-10'})
        assert r.status_code == 200
        data=r.json()
        assert 'answer' not in data and 'solution' not in data
        assert client.post('/api/factory/answer',json={'session_id':data['session_id'],'answer':'0'}).status_code==200
        assert client.post('/api/factory/answer',json={'session_id':data['session_id'],'answer':'0'}).status_code==404
        assert client.get('/api/factory/next',params={'topic_id':'t-10','sequence_key':'bad'}).status_code==422


def test_api_sequence_key_switches_methods(tmp_path):
    db=sample_db(tmp_path)
    with TestClient(api.create_app(db)) as client:
        rows=[client.get('/api/factory/next',params={'topic_id':'t-10',
             'sequence_key':'test_opaque_token_123456'}).json() for _ in range(6)]
    assert len({r['id'] for r in rows})==6
    assert all(a['archetype_id'] != b['archetype_id'] for a,b in zip(rows,rows[1:]))


def test_parallel_requests_do_not_repeat_unnecessarily(tmp_path):
    db=sample_db(tmp_path)
    seq='parallel_opaque_123456'
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda _:storage.create_answer_session(db,'t-10',sequence_key=seq),range(6)))
    assert len({r['id'] for r in rows})==6


def test_schema_migration_on_existing_answer_sessions(tmp_path):
    db=str(tmp_path/'older.sqlite3')
    with sqlite3.connect(db) as con:
        con.execute('''CREATE TABLE answer_sessions (
          session_id TEXT PRIMARY KEY, question_id TEXT NOT NULL,
          expires_at REAL NOT NULL, used_at REAL)''')
        con.execute('INSERT INTO answer_sessions VALUES (?,?,?,NULL)',('legacy','q0',123))
    storage.initialize(db)
    storage.initialize(db)
    with sqlite3.connect(db) as con:
        names={r[1] for r in con.execute('PRAGMA table_info(answer_sessions)')}
        assert {'sequence_hash','created_at'} <= names
        assert con.execute('SELECT session_id FROM answer_sessions').fetchone()[0]=='legacy'


def test_opaque_key_validation(tmp_path):
    db=sample_db(tmp_path)
    for key in ('short','abc\n'*10, 'x'*129, 'user@example.com', 'á'*20):
        with pytest.raises(ValueError):
            storage.create_answer_session(db,'t-10',sequence_key=key)
    assert storage.create_answer_session(db,'missing',sequence_key='opaque_session_123456789') is None


def test_rejected_question_can_be_reverified_after_verifier_fix(tmp_path):
    db=sample_db(tmp_path,methods=1,questions_each=1)
    with storage.connect(db) as con, storage.transaction(con):
        con.execute('DELETE FROM questions')
        con.execute('''INSERT INTO jobs(id,archetype_id,desired,updated_at)
                       VALUES (?,?,?,?)''',('job-1','example-0',1,1.0))
    data={'ordinal':0,'fingerprint':'fingerprint-0','stem':'Validated worked problem',
          'answer':'4','solution':'A sufficiently detailed step by step solution',
          'params':{'x':4},'difficulty':'easy'}
    with storage.connect(db) as con:
        job=storage.claim(con,'worker-A')
        assert job['id']=='job-1'
        storage.store_question(con,'job-1','worker-A',data,False,{'reason':'old verifier bug'})
        assert con.execute("SELECT status FROM questions").fetchone()[0]=='rejected'
        # A transient verifier failure triggers a retry of the same deterministic item.
        storage.fail(con,'job-1','worker-A',RuntimeError('retry'))
        con.execute("UPDATE jobs SET next_attempt_at=0 WHERE id='job-1'")
        job=storage.claim(con,'worker-B')
        assert job is not None
        storage.store_question(con,'job-1','worker-B',data,True,{'engine':'new independent oracle'})
        storage.finish(con,'job-1','worker-B')
        row=con.execute('SELECT status,validation_json FROM questions').fetchone()
        assert row['status']=='verified'
        assert 'previous_rejected_validation' in row['validation_json']
        assert con.execute("SELECT status FROM jobs").fetchone()[0]=='done'


def test_rejected_to_verified_still_obeys_hard_cap(tmp_path):
    db=sample_db(tmp_path,methods=1,questions_each=1)
    with storage.connect(db) as con, storage.transaction(con):
        con.execute("UPDATE questions SET status='rejected'")
        con.execute('''INSERT INTO jobs(id,archetype_id,desired,updated_at)
                       VALUES (?,?,?,?)''',('job-2','example-0',1,1.0))
    data={'ordinal':0,'fingerprint':'question-0-0','stem':'Question question-0-0',
          'answer':'0','solution':'A sufficiently detailed step by step solution',
          'params':{},'difficulty':'easy'}
    # Verify cap handling with a second, already-verified row.
    with storage.connect(db) as con, storage.transaction(con):
        con.execute('''INSERT INTO archetypes(id,topic_id,family,name,method_signature,
                    difficulty,review_status) VALUES (?,?,?,?,?,?,?)''',
                    ('example-extra','t-10','extra','Extra','extra','easy','approved'))
        con.execute('''INSERT INTO questions(id,archetype_id,ordinal,fingerprint,stem,
                    answer,solution,params_json,difficulty,validation_json,status,verified_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                    ('extra','example-extra',0,'extra','extra stem','1','worked','{}','easy','{}','verified',1.0))
    with storage.connect(db) as con:
        assert storage.claim(con,'worker-C') is not None
        storage.set_limit(db,1)
        with pytest.raises(storage.LimitReached):
            storage.store_question(con,'job-2','worker-C',data,True,{'ok':True})
        assert con.execute("SELECT status FROM questions WHERE id='question-0-0'").fetchone()[0]=='rejected'


def test_uneven_method_pool_prioritizes_unseen_questions(tmp_path):
    db=sample_db(tmp_path,methods=2,questions_each=4)
    with storage.connect(db) as con, storage.transaction(con):
        con.execute("DELETE FROM questions WHERE archetype_id='example-0' AND ordinal>0")
    seq='uneven_methods_123456789'
    rows=[storage.create_answer_session(db,'t-10',sequence_key=seq) for _ in range(5)]
    assert len({r['id'] for r in rows}) == 5
    assert set(r['archetype_id'] for r in rows) == {'example-0','example-1'}
