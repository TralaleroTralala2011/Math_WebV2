"""Checks mathematical answers and format invariants for unpublished V141 research."""
import collections
import json
from pathlib import Path
import pytest
import build

DATA = Path(__file__).resolve().parent

def load(name):
    return [json.loads(line) for line in (DATA/name).read_text(encoding='utf-8').splitlines()]

@pytest.fixture(scope='module')
def records():
    return load('V141_CANDIDATE_METHODS.jsonl'),load('V141_VERIFIED_QUESTIONS.jsonl')

def test_distinct_method_ids_and_existing_catalog(records):
    methods, _ = records
    assert len(methods)==11 and len({m['method_id'] for m in methods})==11
    assert all(build.TOPICS[m['topic']]==m['grade'] for m in methods)

def test_each_method_has_ten_literal_unique_questions(records):
    methods, questions = records
    assert len(questions)==110 and len({q['question'] for q in questions})==110
    assert all(sum(q['method_id']==m['method_id'] for q in questions)==10 for m in methods)

def test_independent_math_oracle_for_every_answer(records):
    methods,questions=records
    assert len(questions)==110
    for i,m in enumerate(methods):
        for j in range(10):
            q=next(t for t in questions if t['id']==f'v141_{i:02d}_{j:02d}')
            statement,expected,independent,solution=build.oracle(i,j)
            assert build.same(expected, independent)
            assert q['canonical_answer']==build.pretty(expected)
            assert q['solution']==solution

def test_seven_two_one_distribution_each_method(records):
    methods,questions=records
    for m in methods:
        rows=[q for q in questions if q['method_id']==m['method_id']]
        assert collections.Counter(q['format'] for q in rows)=={
            'trac_nghiem':7,'tra_loi_ngan':2,'dung_sai':1}

def test_mcq_one_correct_and_plausible_symbolic_distractors(records):
    methods,questions=records
    for i,_ in enumerate(methods):
        for j in range(7):
            q=next(t for t in questions if t['id']==f'v141_{i:02d}_{j:02d}')
            _,value,_,_=build.oracle(i,j)
            opts=q['options']
            assert set(opts)==set('ABCD')
            assert len(set(opts.values()))==4
            assert [key for key,val in opts.items() if val==build.pretty(value)]==[q['correct_option']]
            assert q['answer']==q['correct_option']

def test_false_true_labels_and_short_answers(records):
    methods,questions=records
    for i,_ in enumerate(methods):
        for j in (7,8):
            q=next(t for t in questions if t['id']==f'v141_{i:02d}_{j:02d}')
            _,value,other,_=build.oracle(i,j)
            assert q['answer']==build.pretty(value)
            assert q['independent_check']==build.pretty(other)
        q=next(t for t in questions if t['id']==f'v141_{i:02d}_09')
        assert q['answer']==('Đúng' if i%2==0 else 'Sai')

def test_all_staged_pending_and_not_released(records):
    methods,questions=records
    for record in [*methods,*questions]:
        assert record['published'] is False
        assert record['independence_certified'] is False
        assert record['review_status']=='pending-expert-review'

def test_answers_vary_meaningfully_among_ten_examples(records):
    methods,questions=records
    assert all(len({q['canonical_answer'] for q in questions if q['method_id']==m['method_id']})>=8 for m in methods)

def test_invalid_math_equivalence_rejected():
    assert build.same(build.S.Integer(2),build.S.Integer(3)) is False
    assert build.same((build.S.Integer(1),build.S.Integer(2)),(build.S.Integer(2),build.S.Integer(1))) is False
