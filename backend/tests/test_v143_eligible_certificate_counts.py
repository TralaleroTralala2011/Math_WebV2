"""V143: malformed or unapproved certificate rows never advance final milestones."""
from question_factory import storage


def test_eligibility_filters_and_topic_counters(tmp_path):
    db=str(tmp_path/'q.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
        con.execute('INSERT INTO independence_certifications VALUES (?,?,?,?)',
                    (method,'reviewer','{"compared_method_ids":[],"independence_reason":"Independent solution structure compared with previously registered methods."}',1))
    before=storage.progress(db)
    assert before['certificate_records_total']==1
    assert before['certified_independent_types']==0
    assert before['topics_meeting_type_target']==0
    storage.approve(db,method,'reviewer')
    assert storage.progress(db)['certified_independent_types']==1
    with storage.connect(db) as con:
        con.execute('UPDATE independence_certifications SET evidence_json=?', ('{broken',))
    after=storage.progress(db)
    assert after['certified_independent_types']==0
    assert after['certifications_with_empty_evidence']==1
    assert all(t['certified_independent_types']==0 for t in storage.list_topics(db))
