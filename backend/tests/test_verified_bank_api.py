import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.verified_bank_routes import load_bank, catalog, next_question, submit_answer, Submit, check_numeric_equivalence

def test_bank_inventory():
    b = load_bank()
    assert len(b) >= 1510
    assert len({(r['grade'], r['topic'], r['question']) for r in b}) == len(b)
    assert catalog()['distinct_forms'] >= 145

def test_numeric():
    assert check_numeric_equivalence('1/2', '0.5')
    assert check_numeric_equivalence('0,5', '1/2')
    assert not check_numeric_equivalence('2/3', '1/2')

def test_session_one_time_and_solution():
    q = next_question()
    assert 'answer' not in q and 'solution' not in q
    row = next(r for r in load_bank() if r['question'] == q['question'])
    result = submit_answer(Submit(session_id=q['session_id'], answer=str(row['answer'])))
    assert result['is_correct'] and result['solution']
    from fastapi import HTTPException
    try:
        submit_answer(Submit(session_id=q['session_id'], answer=str(row['answer'])))
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        assert False

def test_no_match():
    from fastapi import HTTPException
    try:
        next_question(grade=999)
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        assert False
