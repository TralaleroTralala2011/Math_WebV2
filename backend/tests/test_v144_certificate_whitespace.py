"""V144: semantic empty JSON evidence is not a certificate."""
import pytest
from question_factory import storage

@pytest.mark.parametrize('evidence', ['{}', '{ }', '{\n  }', ' { "x": 1 } ', '[]', 'null', 'invalid'])
def test_evidence_integrity(tmp_path, evidence):
    db=str(tmp_path/'db.sqlite')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method=con.execute('SELECT id FROM archetypes ORDER BY id LIMIT 1').fetchone()[0]
    storage.approve(db, method, 'reviewer')
    with storage.connect(db) as con:
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',(method,'reviewer',evidence,1.0))
    result=storage.progress(db)
    expected=0  # nonempty JSON alone does not establish method independence
    assert result['certified_independent_types']==expected
    assert result['certifications_with_empty_evidence']==int(evidence.strip() != '{ "x": 1 }')
