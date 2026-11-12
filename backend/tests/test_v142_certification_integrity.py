"""V142: reveal weak certificate records instead of silently treating them as proof."""
from question_factory import storage


def test_unapproved_and_empty_evidence_are_flagged(tmp_path):
    db=str(tmp_path/'audit.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method,'reviewer','{}',1.0))
    result=storage.progress(db)
    assert result['certifications_without_approval']==1
    assert result['certifications_with_empty_evidence']==1
    assert result['certification_integrity_warnings']==2


def test_approved_nonempty_evidence_has_no_basic_integrity_warnings(tmp_path):
    db=str(tmp_path/'audit.sqlite3')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
    storage.approve(db,method,'reviewer')
    with storage.connect(db) as con:
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method,'reviewer','{"comparison":"reviewed by separate process"}',1.0))
    result=storage.progress(db)
    assert result['certification_integrity_warnings']==0
