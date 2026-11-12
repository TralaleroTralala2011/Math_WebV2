"""Fixed grade-specific papers: immutable, private, audited, evidence-based."""
import random
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import roadmap_v2_routes as roadmap
from app.fixed_placement import (load_blueprint, assemble_fixed_paper, digest,
                                  wilson_interval, evidence_profile)
from app.placement_psychometrics import evaluate_fixed_paper
from database import database as db
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def make_question(topic, tier, i, *, source='qf2-approved', kind='multiple_choice'):
    # Distinct question text and no answer-key leak in public()
    return {'qid':f'{topic["id"]}:{tier}:{i}', 'topic_id':topic['id'],
            'title':topic['title'],'grade':topic['grade'], 'difficulty':tier,
            'question':f'Bài {i} ở {tier} của {topic["title"]}: 1+1 bằng bao nhiêu?',
            'choices':['2','3','4','5'] if kind=='multiple_choice' else [],
            'correct':0 if kind=='multiple_choice' else '2',
            'question_type':kind, 'explanation':'Vì 1+1=2 theo phép cộng số nguyên.',
            'source':source,'form_id':i%2+1}


def make_paper(topic):
    qs=[]
    for tier in roadmap.DIFFICULTY:
        for i in range(3):
            qs.append(make_question(topic,tier,i,kind='written' if i==2 else 'multiple_choice'))
    return qs


def one_topic_blueprint(topic):
    return {'grade':topic['grade'],'version':'2026.11.11',
            'topics':[{'topic_id':topic['id'],'title':topic['title'],
                       'tiers':{tier:3 for tier in roadmap.DIFFICULTY}}]}


def test_all_three_grade_blueprints_complete_and_distinct():
    topics,_=roadmap._data()
    for grade, count in [(10,49),(11,51),(12,50)]:
        blueprint=load_blueprint(ROOT,grade)
        assert len(blueprint['topics'])==count
        assert [t['topic_id'] for t in blueprint['topics']]==[t['id'] for t in topics if t['grade']==grade]
        assert sum(sum(t['tiers'].values()) for t in blueprint['topics'])==count*9
    assert len({digest(load_blueprint(ROOT,g)) for g in (10,11,12)})==3


def test_fixed_assembly_deterministic_no_candidates_and_format_gate():
    t={'id':'test_topic','title':'Thử nghiệm','grade':10}
    blueprint=one_topic_blueprint(t)
    bank=make_paper(t)
    bank.append(make_question(t,'nền tảng',4,source='lesson-candidate'))
    one=assemble_fixed_paper(blueprint,{t['id']:bank})
    two=assemble_fixed_paper(blueprint,{t['id']:list(reversed(bank))})
    assert one['ready'] and two['ready']
    assert one['paper_hash']==two['paper_hash']
    assert [q['qid'] for q in one['questions']]==[q['qid'] for q in two['questions']]
    assert len(one['questions'])==9
    assert all(q['source']=='qf2-approved' for q in one['questions'])
    # No official paper is released if an entire tier lacks reviewed items.
    short=[q for q in bank if q['difficulty']!='nâng cao']
    blocked=assemble_fixed_paper(blueprint,{t['id']:short})
    assert not blocked['ready'] and blocked['selected']==6
    assert sum(g['missing'] for g in blocked['gaps'])==3
    only_mcq=[{**q,'question_type':'multiple_choice','choices':['2','3','4','5'],'correct':0}
               for q in make_paper(t)]
    assert not assemble_fixed_paper(blueprint,{t['id']:only_mcq})['ready']


def test_wilson_and_psychometric_require_actual_pilot():
    assert wilson_interval(0,0) is None
    assert wilson_interval(3,3)[0]<100
    assert wilson_interval(0,3)[1]>0
    assert evaluate_fixed_paper([],['a','b'])['pilot_status']=='insufficient_sample'
    reviews=[{'qid':'a','verdict':'correct'},{'qid':'b','verdict':'wrong'}]
    assert evaluate_fixed_paper([{'review':reviews}],['a','b'])['reliability_estimated'] is False
    # A 30-learner synthetic pilot yields descriptive metrics, not certification.
    synthetic=[]
    for i in range(30):
        synthetic.append({'review':[{'qid':'a','verdict':'correct' if i%3 else 'wrong'},
                                    {'qid':'b','verdict':'correct' if i%2 else 'skipped'}]})
    result=evaluate_fixed_paper(synthetic,['a','b'])
    assert result['sample_size']==30
    assert result['pilot_status']=='analysis_available_not_validated'
    assert len(result['items'])==2


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'v16.sqlite3')
    db.init_database()
    with TestClient(app) as c:yield c


def auth(client):
    r=client.post('/api/auth/register',json={'username':'V16Learner','password':'SafePass1234!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}


def test_fixed_paper_is_admin_published_and_not_leaked(client,monkeypatch):
    headers=auth(client)
    # No approval => cannot take official paper, regardless of candidate counts.
    blocked=client.post('/api/roadmap-v2/start',headers=headers,json={'grade':10,'mode':'fixed_placement'})
    assert blocked.status_code==409
    assert blocked.json()['detail']['reason']=='fixed_paper_not_published'
    assert client.post('/api/roadmap-v2/fixed/publish/10',headers=headers).status_code==403
    assert client.get('/api/roadmap-v2/fixed/calibration/10',headers=headers).status_code==403

    t={'id':'test_topic','title':'Thử nghiệm','grade':10}
    questions=make_paper(t)
    monkeypatch.setattr(roadmap,'_data',lambda:([t],{}))
    monkeypatch.setattr(roadmap,'_fixed_blueprint',lambda grade:(one_topic_blueprint(t),[t]))
    monkeypatch.setattr(roadmap,'_approved_bank_for_grade',lambda grade:{})
    monkeypatch.setattr(roadmap,'_lesson_reviews_for_grade',lambda grade:{})
    monkeypatch.setattr(roadmap,'pool',lambda topic,approved=None,lesson_reviews=None:list(questions))
    import app.admin_routes as admin_routes
    monkeypatch.setattr(admin_routes,'require_admin',lambda token:{'id':1})
    # The admin can only publish a fully reviewed, grade-specific frozen form.
    published=client.post('/api/roadmap-v2/fixed/publish/10').json()
    assert published['published'] and published['total']==9
    state=client.get('/api/roadmap-v2/fixed/status/10',headers=headers).json()
    assert state['published_valid'] and state['official_exam_available']
    assert 'questions' not in state
    attempt=client.post('/api/roadmap-v2/start',headers=headers,
                        json={'grade':10,'mode':'fixed_placement'})
    assert attempt.status_code==200,attempt.text
    payload=attempt.json()
    assert payload['total']==9
    assert all('correct' not in q and 'explanation' not in q for q in payload['questions'])
    answers={q['qid']:(0 if q['question_type']=='multiple_choice' else '2') for q in payload['questions']}
    submitted=client.post('/api/roadmap-v2/submit/'+payload['attempt_id'],headers=headers,json={'answers':answers})
    assert submitted.status_code==200,submitted.text
    result=submitted.json()
    assert result['correct']==9 and result['wrong']==0 and result['skipped']==0
    assert result['diagnostic_completeness']['reliable_for_placement']
    assert result['objective_evidence']['topics'][0]['tiers']['nền tảng']['correct']==3
    status=client.get('/api/roadmap-v2/status/10',headers=headers).json()
    assert status['official_placement_complete'] is True
    assert status['placement_validated'] is True
    # Repeating the exact frozen form would bias the diagnostic.
    again=client.post('/api/roadmap-v2/start',headers=headers,json={'grade':10,'mode':'fixed_placement'})
    assert again.status_code==409
    assert again.json()['detail']['reason']=='already_completed'
    # Aggregate psychometrics are admin-only and need real pilot sample.
    cal=client.get('/api/roadmap-v2/fixed/calibration/10').json()
    assert cal['analysis']['pilot_status']=='insufficient_sample'
    # Revoking/editing a question invalidates the published form, including
    # a learner's previously accepted result, until a new form is published.
    questions[0]['question']='Nội dung đã bị sửa sau khi duyệt.'
    revoked=client.get('/api/roadmap-v2/fixed/status/10',headers=headers).json()
    assert revoked['published'] and not revoked['published_valid']
    assert client.get('/api/roadmap-v2/status/10',headers=headers).json()['placement_validated'] is False
    blocked=client.post('/api/roadmap-v2/start',headers=headers,json={'grade':10,'mode':'fixed_placement'})
    assert blocked.status_code==409
