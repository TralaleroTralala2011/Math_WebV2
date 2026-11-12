"""V15: official placement is evidence-based, not an unreviewed quiz masquerading as diagnosis."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import roadmap_v2_routes as roadmap
from app.question_factory_v2_routes import Candidate, validate_candidate
from database import database as db


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'v15.sqlite3')
    db.init_database()
    with TestClient(app) as c:yield c


def auth(client,username='V15Student'):
    r=client.post('/api/auth/register',json={'username':username,'password':'SafePass1234!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}


def test_placement_sampling_only_approved_when_three_tiers_ready(monkeypatch):
    topics=[{'id':'test_topic','title':'Kiểm tra mẫu','grade':10}]
    qs=[]
    for tier in roadmap.DIFFICULTY:
        for j in range(4):
            qs.append({'qid':f'{tier}-{j}','topic_id':'test_topic','difficulty':tier,'source':'qf2-approved'})
    qs.append({'qid':'candidate','topic_id':'test_topic','difficulty':None,'source':'lesson-candidate'})
    monkeypatch.setattr(roadmap,'pool',lambda topic,approved,reviews:list(qs))
    result=roadmap.select_placement_questions(topics,{}, {},rng=__import__('random').Random(3))
    assert len(result)==12
    assert all(q['source']=='qf2-approved' for q in result)
    quality=roadmap.assessment_quality(result,topics)
    assert quality['complete_three_tier_coverage'] is True
    assert quality['unreviewed_items']==0


def test_provisional_placement_does_not_open_official_topic_exam(client):
    headers=auth(client)
    r=client.post('/api/roadmap-v2/start',headers=headers,json={'grade':10,'mode':'placement'})
    assert r.status_code==200,r.text
    d=r.json()
    assert d['assessment_quality']['complete_three_tier_coverage'] is False
    assert all('correct' not in q for q in d['questions'])
    submitted=client.post('/api/roadmap-v2/submit/'+d['attempt_id'],headers=headers,json={'answers':{}})
    assert submitted.status_code==200,submitted.text
    result=submitted.json()
    assert result['verified_score']['total']==0
    assert result['roadmap_is_provisional'] is True
    assert all(s['verified_evidence']==0 for s in result['suggested_topics'])
    state=client.get('/api/roadmap-v2/status/10',headers=headers).json()
    assert state['placement_complete'] is True
    assert state['placement_validated'] is False
    assert state['placement_state']=='provisional'
    topic_id=result['roadmap_order'][0]
    response=client.post('/api/roadmap-v2/start',headers=headers,
                         json={'grade':10,'mode':'topic','topic_id':topic_id})
    assert response.status_code==409
    assert response.json()['detail']['reason']=='placement_not_validated'
    tutor=client.get('/api/roadmap-v2/tutor/10',headers=headers).json()
    assert tutor['topics_assessed']==0


def test_question_factory_rejects_equivalent_mcq_options(client):
    from app.question_factory_v2_routes import conn
    data=Candidate.model_validate({
        'grade':10,'topic_id':'menh_de_tap_hop',
        'title':'Bài kiểm tra lựa chọn tương đương toán học',
        'concept':'Tập hợp và giá trị của biểu thức',
        'method':'Đối chiếu đáp án trắc nghiệm với kết quả tính toán',
        'conditions':'Bốn phương án được cho dưới dạng số thực',
        'distinguishing':'Kiểm tra xem có hai đáp án đúng tương đương hay không',
        'questions':[{
            'question':f'Giá trị của một phần hai trong ví dụ {i} bằng bao nhiêu?',
            'question_type':'multiple_choice','difficulty':'nền tảng',
            'choices':['1/2','0.5','1/3','2/3'], 'correct_index':0,
            'answer':'1/2','explanation':'Ta có một phần hai bằng 0,5 theo định nghĩa phân số thập phân.'
        } for i in range(10)]})
    with conn() as c:
        with pytest.raises(Exception) as exc:validate_candidate(c,data)
    assert 'tương đương' in str(exc.value)


def test_all_1391_existing_lesson_questions_are_structurally_eligible():
    topics,lessons=roadmap._data()
    count=sum(len(lessons.get(t['id'],{}).get('quiz',[])) for t in topics)
    accepted=sum(roadmap._valid(q) for t in topics for q in lessons.get(t['id'],{}).get('quiz',[]))
    assert count==1391
    assert accepted==1391
    sample=next(t for t in topics if t['id']=='menh_de_tap_hop')
    qs=roadmap.pool(sample,approved_bank={},lesson_reviews={})
    assert any(q['question_type']=='written' for q in qs)
    assert any(q['question_type']=='true_false' for q in qs)
    assert all(q['correct'] is not None for q in qs)


def test_math_symbols_and_interval_endpoints_not_confused():
    from app.ai.engine.validator import options_equivalent
    from app.ai.engine.solver import equivalent
    from app.questions.answer_checker import grade_answer
    assert options_equivalent('1/2','0.5')
    assert not options_equivalent('[3;5]','(3;5)')
    assert not options_equivalent('R','r')
    assert equivalent('(3;5)','(3,5)')
    q={'question_type':'multiple_choice','options':['2R','R','S','r']}
    assert grade_answer(q,'R','R')
    assert not grade_answer(q,'r','R')
