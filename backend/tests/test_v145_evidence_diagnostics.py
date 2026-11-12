"""V145: distinguish JSON-shaped evidence from documented method comparison."""
import json
from question_factory import storage


def test_missing_method_comparison_is_visible(tmp_path):
    db = str(tmp_path / 'test.sqlite')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method = con.execute('SELECT id FROM archetypes LIMIT 1').fetchone()[0]
    storage.approve(db, method, 'reviewer')
    with storage.connect(db) as con:
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method, 'reviewer', '{"x":1}', 1.0))
    result = storage.progress(db)
    assert result['certifications_without_method_comparison'] == 1
    assert result['certified_independent_types'] == 0  # incomplete comparison cannot advance milestone
    with storage.connect(db) as con:
        con.execute('UPDATE independence_certifications SET evidence_json=? WHERE archetype_id=?',
                    (json.dumps({'compared_method_ids': [],
                                 'independence_reason': 'A distinct proof strategy requiring a separate mathematical invariant.'}), method))
    assert storage.progress(db)['certifications_without_method_comparison'] == 0
    assert storage.progress(db)['certified_independent_types'] == 1


def test_invalid_evidence_is_flagged(tmp_path):
    db = str(tmp_path / 'test.sqlite')
    storage.initialize(db)
    storage.seed_samples(db)
    with storage.connect(db) as con:
        method = con.execute('SELECT id FROM archetypes LIMIT 1').fetchone()[0]
    storage.approve(db, method, 'reviewer')
    with storage.connect(db) as con:
        con.execute('INSERT INTO independence_certifications VALUES(?,?,?,?)',
                    (method, 'reviewer', 'not json', 1.0))
    result = storage.progress(db)
    assert result['certifications_without_method_comparison'] == 1
    assert result['certified_independent_types'] == 0
