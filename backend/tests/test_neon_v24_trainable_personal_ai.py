"""V24: trainable online AI only learns from first, verified, server-graded answers."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app import learner_online as online
from app import roadmap_v2_routes as r
from database import database

ROOT=Path(__file__).resolve().parents[2]


def test_online_logistic_trains_updates_weights_and_never_uses_skips_or_candidates():
    rows=[
        {'qid':'a','topic_id':'T','tier':'nền tảng','verdict':'skipped','source':'qf2-approved'},
        {'qid':'a','topic_id':'T','tier':'nền tảng','verdict':'wrong','source':'qf2-approved'},
        {'qid':'a','topic_id':'T','tier':'nền tảng','verdict':'correct','source':'qf2-approved'},
        {'qid':'candidate','topic_id':'T','tier':'nâng cao','verdict':'correct','source':'lesson-candidate'},
        {'qid':'b','topic_id':'T','tier':'trung cấp','verdict':'correct','source':'lesson-reviewed'},
        {'qid':'invalid','topic_id':'T','tier':'chưa phân loại','verdict':'correct','source':'qf2-approved'},
    ]
    state=online.replay_events(rows)
    assert state['n']==2 and state['right']==1
    assert state['topic_stats']['T']==[1,2]
    assert state['weights']!=online.INITIAL
    assert online.replay_events(rows)==state
    assert online.public_report(state)['ready_for_soft_suggestions'] is False
    assert online.suggestions_for_topic(state,'T')['predicted_correct']=={}
    assert online.learn(state,'T','nâng cao','skipped') is False
    assert state['n']==2


def test_training_personalized_prediction_changes_from_real_verified_events():
    state=online.empty_state()
    before=online.probability(state,'chapter_A','trung cấp')
    for i in range(24):
        assert online.learn(state,'chapter_A','trung cấp','correct')
    after=online.probability(state,'chapter_A','trung cấp')
    assert after>before and state['n']==24
    focus=online.suggestions_for_topic(state,'chapter_A')
    # V25 no longer confuses many repetitions of one tier/topic with diverse
    # evidence. The predictor still learns, but soft probabilities are hidden.
    assert not focus['predictive_ready'] and focus['predicted_correct']=={}
    assert online.public_report(state)['population_calibrated'] is False


def test_per_student_retraining_idempotent_authorized_and_isolated(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v24_train.db')
    database.init_database()
    with TestClient(app) as client:
        assert client.post('/api/roadmap-v2/tutor/retrain/10').status_code in (401,403)
        u1=client.post('/api/auth/register',json={'username':'v24_train_one','password':'ValidPass9876!'}).json()
        u2=client.post('/api/auth/register',json={'username':'v24_train_two','password':'ValidPass9876!'}).json()
        a,b=u1['user']['id'],u2['user']['id']
        h1={'Authorization':'Bearer '+u1['token']}
        h2={'Authorization':'Bearer '+u2['token']}
        with r.db() as c:
            for attempt,qid,tier,verdict,src in [
                ('p1','q1','nền tảng','skipped','qf2-approved'),
                ('p2','q1','nền tảng','wrong','qf2-approved'),
                ('p3','q1','nền tảng','correct','qf2-approved'),
                ('p4','q2','trung cấp','correct','lesson-reviewed'),
                ('p5','q3','nâng cao','wrong','lesson-candidate'),
            ]:
                c.execute('INSERT INTO roadmap_v2_learning_events VALUES (?,?,?,?,?,?,?,?,?)',
                          (a,10,attempt,qid,'topic_01',tier,verdict,src,r.now()))
            c.commit()
        one=client.post('/api/roadmap-v2/tutor/retrain/10',headers=h1)
        assert one.status_code==200,one.text
        assert one.json()['training']['examples']==2
        assert one.json()['training']['correct']==1
        two=client.post('/api/roadmap-v2/tutor/retrain/10',headers=h1)
        assert two.status_code==200 and two.json()['training']==one.json()['training']
        zero=client.get('/api/roadmap-v2/tutor/10',headers=h2)
        assert zero.status_code==200 and zero.json()['online_training']['examples']==0
        data=client.get('/api/roadmap-v2/tutor-data/10',headers=h1)
        assert data.status_code==200
        assert data.json()['online_training']['examples']==2
        with r.db() as c:
            stored=c.execute('SELECT trained_count,state_json FROM roadmap_v2_personal_predictors WHERE user_id=? AND grade=10',(a,)).fetchone()
            assert stored['trained_count']==2
            assert json.loads(stored['state_json'])['n']==2
            assert c.execute('SELECT trained_count FROM roadmap_v2_personal_predictors WHERE user_id=? AND grade=10',(b,)).fetchone()['trained_count']==0
        assert client.post('/api/roadmap-v2/tutor/retrain/13',headers=h1).status_code==422


def test_v24_frontend_only_calls_authenticated_training_and_explains_estimates():
    js=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    css=(ROOT/'css/neon-v23-ai-tutor.css').read_text(encoding='utf-8')
    assert "call('/tutor/retrain/'+selected,{method:'POST'})" in js
    assert 'online_prediction_ready' in js and 'chưa hiệu chuẩn' in js
    assert 'mw-v24-prediction' in css
    assert 'innerHTML' not in js[js.index('async function showTutor(){'):js.index('function goToQuestion(index){')]


def test_auto_training_on_real_server_graded_submission_and_rebuild_matches(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v24_submit.db')
    database.init_database()
    topics=[{'id':'test_topic','title':'Tập hợp','grade':10}]
    qs=[]
    for tier in r.DIFFICULTY:
        for i in range(3):
            qs.append({'qid':f'{tier}-{i}', 'topic_id':'test_topic',
                'title':'Tập hợp','grade':10,'difficulty':tier,'source':'qf2-approved',
                'question':f'Ví dụ {tier} câu {i+1}: 4 cộng 1 bằng bao nhiêu?',
                'choices':['5','6','7','8'],'correct':0,'question_type':'multiple_choice',
                'explanation':'Cộng 4 với 1 bằng 5.', 'form_id':i%2+1})
    monkeypatch.setattr(r,'_data',lambda:(topics,{}))
    blueprint={'grade':10,'version':'v24-test','topics':[
        {'topic_id':'test_topic','title':'Tập hợp','tiers':{tier:3 for tier in r.DIFFICULTY}}]}
    monkeypatch.setattr(r,'_fixed_blueprint',lambda grade:(blueprint,topics))
    monkeypatch.setattr(r,'_paper_valid_now',lambda grade,paper:True)
    with TestClient(app) as client:
        u=client.post('/api/auth/register',json={'username':'v24_real_submit','password':'ValidPass9876!'}).json()
        uid=u['user']['id'];h={'Authorization':'Bearer '+u['token']}
        with r.db() as c:
            c.execute('INSERT INTO roadmap_v2_fixed_papers VALUES (?,?,?,?,?,?,?,?)',
                      ('test_v24_fixed',10,r.digest(qs),'blueprint',json.dumps(qs,ensure_ascii=False),r.now(),99,1))
            c.commit()
        started=client.post('/api/roadmap-v2/start',headers=h,json={'grade':10,'mode':'fixed_placement'})
        assert started.status_code==200,started.text
        questions=started.json()['questions']
        assert len(questions)==9 and all('correct' not in x for x in questions)
        answers={questions[0]['qid']:0,questions[1]['qid']:1,questions[2]['qid']:0}
        result=client.post('/api/roadmap-v2/submit/'+started.json()['attempt_id'],
                           headers=h,json={'answers':answers})
        assert result.status_code==200,result.text
        evidence=result.json()['training_evidence']
        assert evidence['unique_new_answers']==3
        assert evidence['trained_predictor']['examples']==3
        assert evidence['trained_predictor']['correct']==2
        trained=client.post('/api/roadmap-v2/tutor/retrain/10',headers=h).json()
        assert trained['training']['examples']==3
        assert trained['training']['correct']==2
        prof=client.get('/api/roadmap-v2/tutor/10',headers=h).json()
        assert prof['online_training']['examples']==3
        assert prof['online_training']['population_calibrated'] is False
        with r.db() as c:
            state=online.load(c,uid,10)
            assert state['n']==3 and state['topic_stats']['test_topic']==[2,3]
            assert state['weights'] != online.INITIAL
