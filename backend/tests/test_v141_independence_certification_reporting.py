"""Approval for question generation must not inflate independent-method progress."""
import json
from question_factory import storage


def test_approved_is_not_independently_certified(tmp_path):
    db = str(tmp_path / 'factory.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
        topic=con.execute('SELECT topic_id FROM archetypes WHERE id=?',(method,)).fetchone()[0]
    storage.approve(db,method,'reviewer')
    stats=storage.progress(db)
    assert stats['approved_archetypes']==1
    assert stats['certified_independent_types']==0
    assert stats['methods_remaining_uncertified']==300_000
    assert stats['target_ready_questions']==0
    assert stats['target_questions_remaining_qualified']==3_000_000
    t=next(x for x in storage.list_topics(db) if x['id']==topic)
    assert t['approved_types']==1 and t['certified_independent_types']==0
    assert t['type_shortfall']==2000
    assert t['question_shortfall']==20000


def test_independence_evidence_is_separate_from_approval(tmp_path):
    db = str(tmp_path / 'factory.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
        # A distinct external-review evidence record, not the ordinary approve flag.
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method,'human-reviewer',json.dumps({'method_proof':'comparison-reviewed','source':'local-test'}),1.0))
    stats=storage.progress(db)
    assert stats['approved_archetypes']==0
    assert stats['certified_independent_types']==0
    assert stats['certifications_without_approval']==1
    assert stats['methods_remaining_uncertified']==300_000


def test_initialize_preserves_legacy_tables_and_new_certificates(tmp_path):
    db = str(tmp_path / 'factory.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method,'reviewer','{}',2.0))
    storage.initialize(db)
    assert storage.progress(db)['certificate_records_total']==1
    assert storage.progress(db)['certified_independent_types']==0


def test_factory_catalog_exposes_uncertified_status(tmp_path):
    from fastapi.testclient import TestClient
    from question_factory.api import create_app
    db=str(tmp_path/'pilot.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
    storage.approve(db,method,'reviewer')
    client=TestClient(create_app(db))
    payload=client.get('/api/factory/catalog').json()
    assert payload['method_independence_certified'] is False
    assert payload['independent_types_certified']==0
    assert any(x['approved_types']>0 and x['certified_independent_types']==0 for x in payload['items'])


def test_verified_question_does_not_count_towards_final_target_without_method_cert(tmp_path):
    db = str(tmp_path / 'pilot.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method,topic=con.execute('SELECT id,topic_id FROM archetypes ORDER BY id LIMIT 1').fetchone()
        con.execute('''INSERT INTO questions
            (id,archetype_id,ordinal,fingerprint,stem,answer,solution,
             params_json,difficulty,validation_json,status,verified_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
            ('q-v141', method, 1, 'v141-unique', '1+1?', '2', '1+1=2',
             '{}','nền tảng','{}','verified', 1.0))
    status=storage.progress(db)
    assert status['verified_questions']==1
    assert status['target_ready_questions']==0
    with storage.connect(db) as con:
        con.execute('INSERT INTO independence_certifications VALUES (?,?,?,?)',
                    (method,'reviewer','{"compared_method_ids":[],"independence_reason":"A distinct mathematical strategy confirmed by independent comparison."}', 2.0))
    status=storage.progress(db)
    assert status['verified_questions']==1
    assert status['target_ready_questions']==0
    storage.approve(db,method,'reviewer')
    status=storage.progress(db)
    assert status['target_ready_questions']==1
    topic_status=next(x for x in storage.list_topics(db) if x['id']==topic)
    assert topic_status['certified_method_verified_questions']==1
    assert topic_status['question_shortfall']==19999
