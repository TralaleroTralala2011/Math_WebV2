"""Regression: coded divisibility must be a genuine single true/false question."""
from copy import deepcopy

import pytest
from app.ai.engine.question_format_v82 import adapt_question
from app.ai.engine.validator import validate, ValidationError
from app.questions.answer_checker import grade_answer


def base(n=11680, d=40, answer='1'):
    return {
        'id': 'regression-binary-1', 'grade': 10, 'topic':'REMAINDER',
        'difficulty':'easy', 'question_type':'multiple_choice',
        'question':f'Hỏi {n} có chia hết cho {d} không? Mã 1 nếu có, 0 nếu không.',
        'answer':answer, 'options':['1','2','0','3'],
        'solution':'Lấy số dư.', 'source':'150_CHU_DE_WORD',
        'form_id':'V254-REMAINDER-001'
    }


def test_divisible_true_word_source_preserved_and_graded():
    original=base()
    raw=deepcopy(original)
    result=adapt_question(original)
    assert original==raw # source never mutated
    assert result['question']=='11680 có chia hết cho 40 không?'
    assert result['source_question_original']==raw['question']
    assert result['source_answer_original']=='1'
    assert result['options']==['Đúng','Sai']
    assert result['answer']=='Đúng'
    assert result['answer_mode']=='binary_boolean'
    assert result['question_type']=='true_false'
    validate(result)
    assert grade_answer(result,'Đúng') is True
    assert grade_answer(result,'Sai') is False
    assert 'số dư bằng 0' in result['solution'].lower()


def test_not_divisible_false_answer_and_explanation():
    q=adapt_question(base(11681,40,'0'))
    assert q['answer']=='Sai'
    assert grade_answer(q,'Sai') is True
    assert grade_answer(q,'Đúng') is False
    validate(q)
    assert 'số dư bằng 1' in q['solution'].lower()

@pytest.mark.parametrize('numerator,denominator,answer',[
    (11680,40,'0'),(11681,40,'1'),(11680,40,'2'),
    (11680,0,'1'),(11680,40,'True')
])
def test_reject_wrong_or_unsafe_coded_answer(numerator,denominator,answer):
    assert adapt_question(base(numerator,denominator,answer)) is None


def test_do_not_rewrite_math_that_is_not_binary():
    original={'question':'Số dư khi chia 11681 cho 40 là bao nhiêu?', 'answer':'1'}
    assert adapt_question(original) is original


def test_do_not_accept_an_unrecognized_coded_question():
    q=base()
    q['question']='Hỏi x có chia hết cho 40 không? Mã 1 nếu có, 0 nếu không.'
    assert adapt_question(q) is None


def test_validator_still_rejects_invalid_true_false():
    q=adapt_question(base())
    q['options']=['Đúng','Đúng']
    with pytest.raises(ValidationError, match='tf_binary_options'):
        validate(q)


def test_normal_mcq_and_short_answer_unchanged():
    mcq=base()
    mcq['question']='Số dư của 11681 khi chia cho 40 là bao nhiêu?'
    mcq['answer']='1'
    assert adapt_question(mcq) is mcq
    validate(mcq)
    short=base()
    short['question']='Số dư khi chia 11681 cho 40 là bao nhiêu?'
    short['answer']='1'
    short['question_type']='short_answer'
    short['options']=[]
    assert adapt_question(short) is short
    validate(short)


def test_word_true_false_about_student_claim():
    q=base(760,10,'Đúng')
    q['question']='ĐÚNG / SAI: Hỏi 760 có chia hết cho 10 không? Mã 1 nếu có, 0 nếu không. Một học sinh trả lời: 1.'
    q['question_type']='short_answer'
    q['options']=[]
    shown=adapt_question(q)
    assert shown['answer']=='Đúng'
    assert 'chọn mã 1' in shown['question']
    validate(shown)
    assert grade_answer(shown,'Đúng')
    assert not grade_answer(shown,'Sai')


def test_word_true_false_wrong_student_code_is_false():
    q=base(8910,33,'Sai')
    q['question']='ĐÚNG / SAI: Hỏi 8910 có chia hết cho 33 không? Mã 1 nếu có, 0 nếu không. Một học sinh đưa ra kết quả 2. Nhận định này đúng hay sai?'
    q['question_type']='short_answer';q['options']=[]
    shown=adapt_question(q)
    assert shown['answer']=='Sai'
    assert 'mã 2' in shown['question']
    validate(shown)
    assert grade_answer(shown,'Sai')
    q['answer']='Đúng'
    assert adapt_question(q) is None
