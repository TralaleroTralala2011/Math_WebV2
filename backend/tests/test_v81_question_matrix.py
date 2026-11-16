from app.ai.engine import assignment_quality as quality

def test_matrix_counts_and_never_claims_verification(monkeypatch):
    def eligible(grade, topic, level, kind, cap=500):
        return [{'source_id': f'{level}-{kind}-{i}'} for i in range(2 if kind == 'mixed' else 1)]
    monkeypatch.setattr(quality, 'eligible_assignment_questions', eligible)
    matrix = quality.assignment_bank_matrix(10, 'chia_du')
    assert set(matrix['levels']) == {'easy', 'medium', 'hard', 'expert'}
    assert matrix['levels']['medium']['mixed_distinct'] == 2
    assert matrix['levels']['hard']['true_false'] == 0
    assert matrix['verified_math_answers'] is False
