"""V140 regression: safe mathematical answer equivalence and absent V122 source."""
from question_factory.grading import answers_equivalent
from question_factory import storage, operations
from question_factory.api import create_app
from fastapi.testclient import TestClient


def check(expected, received):
    value, scope=answers_equivalent(expected,received)
    assert value, (expected,received,scope)
    assert scope != 'normalized_text', (expected,received,scope)


def test_scalar_assignment_equivalence():
    check('2', 'x=2')
    check('x=2', '2')
    check('x = 1/2', 'x = 0.5')
    check('3.5', 'x=3,5')
    assert answers_equivalent('x=2','y=2')[0] is False
    assert answers_equivalent('x=2','x=3')[0] is False


def test_ordered_pair_semicolon_and_assignments():
    check('(x,y)=(7;5)', '(7;5)')
    check('(x,y)=(7;5)', 'x=7; y=5')
    check('(x,y)=(7;5)', 'x=7, y=5')
    check('(2; sqrt(9))', '(2; 3)')
    check('(x,y)=(1/2;4)', '(x,y)=(0.5;4)')
    assert answers_equivalent('(x,y)=(7;5)','(y,x)=(7;5)')[0] is False
    assert answers_equivalent('(7;5)','(5;7)')[0] is False
    assert answers_equivalent('(7;5)','(7,5)')[0] is False
    assert answers_equivalent('(x,y)=(7;5)','x=7;y=6')[0] is False


def test_safe_fallback_and_malicious_input():
    assert answers_equivalent('Đúng','đúng') == (True,'normalized_text')
    assert answers_equivalent('2','__import__("os")')[0] is False
    assert answers_equivalent('2','sqrt(-1)')[0] is False
    assert answers_equivalent('x=2','x=2; z=1')[0] is False
    assert answers_equivalent('(x,y)=(2;3)', '(x,x)=(2;3)')[0] is False
    assert answers_equivalent('2','2**100000')[0] is False


def test_session_grading_accepts_assignment_without_leaking_answer(tmp_path):
    db=str(tmp_path/'grade.sqlite3')
    storage.initialize(db)
    with storage.connect(db) as con, storage.transaction(con):
        con.execute("INSERT INTO topics VALUES ('t',10,'Test')")
        con.execute("INSERT INTO archetypes (id,topic_id,family,name,method_signature,difficulty,review_status) VALUES ('m','t','f','n','s','easy','approved')")
        con.execute("INSERT INTO questions VALUES ('q','m',0,'fp','Giải tìm x','2','Suy ra x=2','{}','easy','{}','verified',1)")
    with TestClient(create_app(db)) as client:
        response=client.get('/api/factory/next',params={'topic_id':'t'})
        assert response.status_code==200
        entry=response.json()
        assert 'answer' not in entry and 'solution' not in entry
        graded=client.post('/api/factory/answer',json={'session_id':entry['session_id'],'answer':'x=2'})
        assert graded.status_code==200 and graded.json()['is_correct'] is True
        assert graded.json()['grading_scope']=='single_variable_equivalence'
        assert client.post('/api/factory/answer',json={'session_id':entry['session_id'],'answer':'2'}).status_code==404


def test_optional_v122_can_be_absent_without_crash(tmp_path):
    assert storage.seed_v122(str(tmp_path/'factory.sqlite3')) == 0


def test_operator_reports_missing_opted_in_v122(monkeypatch,tmp_path):
    monkeypatch.setenv('QF_ENABLE_V122_CANDIDATES','1')
    monkeypatch.delenv('QF_ENABLE_V123_CANDIDATES',raising=False)
    data=tmp_path/'datadir'
    result=operations.once(data,auto_enqueue=False)
    assert result['registered_v122_blueprints']==0
    assert result['v122_requested'] is True
    assert result['v122_source_available'] is False
    assert result['v122_skipped_missing_source'] is True
    assert (data/'operations'/'progress-latest.json').exists()
