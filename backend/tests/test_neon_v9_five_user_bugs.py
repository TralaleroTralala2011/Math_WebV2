"""User-reported regressions: topic, answer correctness, uniqueness, grading and relogin."""
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.ai.engine.validator import validate, ValidationError
from app.ai.engine.service import AIQuestionService
from app.questions.answer_checker import grade_answer
from app.roadmap_v2_routes import grade_question
from database import database as db


def q(text='Tính 1/2 + 1/2.',options=None,answer='1',topic='g10_arithmetic'):
    return dict(id='regression',grade=10,topic=topic,difficulty='easy',
                question_type='multiple_choice',question=text,
                answer=answer,options=options or ['1','2','3','4'],solution='1/2 + 1/2 = 1')


def test_1_reject_topic_mismatch():
    with pytest.raises(ValidationError,match='topic_mismatch'):
        validate(q('Tính 2 + 3.', ['5','4','3','2'], '5', 'ham_so_bac_hai'))
    with pytest.raises(ValidationError,match='topic_mismatch'):
        validate({**q(), 'requested_topic':'another_topic'})


def test_2_reject_independently_provable_wrong_arithmetic_answer():
    with pytest.raises(ValidationError,match='wrong_arithmetic_answer'):
        validate(q('Tính 12 + 15.', ['26','27','28','29'], '26'))
    validate(q('Tính 12 + 15.', ['26','27','28','29'], '27'))


def test_3_two_correct_choices_not_accepted():
    with pytest.raises(ValidationError,match='mcq_equivalent_options'):
        validate(q(options=['1/2','0.5','2','3'],answer='2'))
    with pytest.raises(ValidationError,match='mcq_equivalent_options'):
        validate(q('Biểu thức nào bằng (x+1)^2?',
                   ['x²+2x+1','(x+1)^2','x²+1','x²+2x'], '(x+1)^2'))


def test_4_correct_answer_consistent_across_grade_engines():
    question={'question_type':'multiple_choice','options':['1','2','3','4'],'answer':'2'}
    for submitted in ['B', '2', 1, {'index':1}]:
        assert grade_answer(question,submitted)
        assert AIQuestionService.__new__(AIQuestionService)._check(question,submitted)
    # The visible answer '2' is NOT the third option (index 2).
    assert not grade_answer(question,2)
    assert grade_question({'question_type':'multiple_choice','choices':['1','2','3','4'],'correct':1},'2') == 'correct'
    assert grade_question({'question_type':'multiple_choice','choices':['1','2','3','4'],'correct':1},1) == 'correct'
    assert grade_answer({'question_type':'short_answer'},'6/2','3')
    assert grade_answer({'question_type':'short_answer'},'3 + 2i','3+2i')


def test_5_same_account_can_login_again_after_logout_and_database_restart(tmp_path,monkeypatch):
    path=tmp_path/'accounts.db'
    monkeypatch.setattr(db,'DATABASE_PATH',path)
    monkeypatch.setenv('MATHWEB_DB_PATH',str(path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.db'))
    db.init_database()
    credentials={'username':'SameAccount','password':'repeatPassword123'}
    with TestClient(app) as client:
        created=client.post('/api/auth/register',json=credentials)
        assert created.status_code==200,created.text
        account_id=created.json()['user']['id']
        for _ in range(2):
            login=client.post('/api/auth/login',json=credentials)
            assert login.status_code==200,login.text
            assert login.json()['user']['id']==account_id
            token=login.json()['token']
            assert client.post('/api/auth/logout',headers={'Authorization':'Bearer '+token}).status_code==200
    # Re-initialising a persistent SQLite database must never delete this account.
    db.init_database()
    with TestClient(app) as client:
        again=client.post('/api/auth/login',json=credentials)
        assert again.status_code==200, again.text
        assert again.json()['user']['id']==account_id
        assert client.post('/api/auth/register',json=credentials).status_code==400
