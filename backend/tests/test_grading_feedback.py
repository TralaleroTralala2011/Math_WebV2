from app.questions.grading_feedback import grade_with_feedback


def test_numeric_equivalence_and_real_solution():
    q = {'question_type': 'short_answer', 'correct_answer': '1/2', 'solution': 'Chia cả tử và mẫu cho 2.'}
    r = grade_with_feedback(q, '0.5')
    assert r['is_correct'] is True
    assert r['explanation'] == q['solution']


def test_no_fabricated_solution():
    r = grade_with_feedback({'question_type': 'short_answer', 'answer': '3'}, '4')
    assert not r['is_correct'] and r['explanation'] is None and r['needs_solution_review']


def test_missing_key_not_graded():
    assert grade_with_feedback({'question_type': 'essay'}, 'anything')['status'] == 'ungradable'
