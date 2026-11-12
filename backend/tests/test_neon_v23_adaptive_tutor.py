"""V23: actual personalized plans must respect evidence, student identity and unlock gates."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app import roadmap_v2_routes as r
from database import database

ROOT=Path(__file__).resolve().parents[2]


def test_unique_evidence_ignores_repeats_and_replaces_skips_with_first_answer():
    events=[
        {'qid':'a','topic_id':'t','tier':'nền tảng','verdict':'skipped'},
        {'qid':'a','topic_id':'t','tier':'nền tảng','verdict':'wrong'},
        {'qid':'a','topic_id':'t','tier':'nền tảng','verdict':'correct'},
        {'qid':'b','topic_id':'t','tier':'trung cấp','verdict':'skipped'},
        {'qid':'b','topic_id':'t','tier':'trung cấp','verdict':'skipped'},
    ]
    effective=r._effective_training_evidence(events)
    assert len(effective)==2
    assert [(e['qid'],e['verdict']) for e in effective]==[('a','wrong'),('b','skipped')]


def test_tutor_plan_auth_stage_unlock_per_user_and_no_duplicate_weakness(tmp_path, monkeypatch):
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v23_adaptive.db')
    database.init_database()
    grade_topics=[{'id':f'topic_{n}','title':f'Chủ đề {n}','grade':10} for n in range(1,5)]
    monkeypatch.setattr(r,'_data',lambda:(grade_topics,{}))
    monkeypatch.setattr(r,'_paper_valid_now',lambda grade,paper:True)
    with TestClient(app) as client:
        assert client.get('/api/roadmap-v2/tutor-plan/10').status_code in (401,403)
        reg=client.post('/api/auth/register',json={'username':'v23_student_a','password':'ValidPass9876!'}).json()
        reg2=client.post('/api/auth/register',json={'username':'v23_student_b','password':'ValidPass9876!'}).json()
        h={'Authorization':'Bearer '+reg['token']}
        h2={'Authorization':'Bearer '+reg2['token']}
        a=reg['user']['id']
        init=client.get('/api/roadmap-v2/tutor-plan/10',headers=h).json()
        assert init['status']=='placement_required' and not init['topics']
        result={'grade':10,'mode':'fixed_placement','fixed_paper_hash':'paper-for-10',
                'diagnostic_completeness':{'content_coverage_complete':True},
                'roadmap_order':[t['id'] for t in grade_topics]}
        with r.db() as conn:
            conn.execute('INSERT INTO roadmap_v2_fixed_papers VALUES (?,?,?,?,?,?,?,?)',
                         ('paper-001',10,'paper-for-10','blueprint','[]',r.now(),99,1))
            conn.execute('INSERT INTO roadmap_v2_attempts VALUES (?,?,?,?,?,?,?,?,?,?)',
                         ('submitted-001',a,10,'fixed_placement',None,'[]',r.now(),'{}',
                          json.dumps(result,ensure_ascii=False),r.now()))
            # Topic 2 has three unique answers, two wrong. Repeat wrong twice;
            # repeated events must not inflate the priority or wrong count.
            for attempt,qid,topic,tier,verdict in [
                ('a1','qid-a','topic_1','nền tảng','skipped'),
                ('a2','qid-b','topic_2','nền tảng','wrong'),
                ('a3','qid-b','topic_2','nền tảng','wrong'),
                ('a4','qid-c','topic_2','nền tảng','wrong'),
                ('a5','qid-d','topic_2','trung cấp','correct'),
                ('a6','qid-e','topic_3','nền tảng','skipped'),
            ]:
                conn.execute('INSERT INTO roadmap_v2_learning_events VALUES (?,?,?,?,?,?,?,?,?)',
                             (a,10,attempt,qid,topic,tier,verdict,'qf2-approved',r.now()))
            conn.execute('INSERT INTO roadmap_v2_skill_state VALUES (?,?,?,?,?,?,?)',
                         (a,10,'topic_2','nền tảng',.26,2,r.now()))
            conn.execute('INSERT INTO roadmap_v2_skill_state VALUES (?,?,?,?,?,?,?)',
                         (a,10,'topic_2','trung cấp',.55,1,r.now()))
            conn.commit()
        plan=client.get('/api/roadmap-v2/tutor-plan/10',headers=h)
        assert plan.status_code==200,plan.text
        data=plan.json()
        assert data['status']=='ready' and data['current_stage']==1
        assert len(data['topics'])==3
        assert data['topics'][0]['topic_id']=='topic_2'
        assert data['topics'][0]['wrong']==2 and data['topics'][0]['correct']==1
        assert data['topics'][0]['verified_answered']==3
        assert data['topics'][0]['focus_tier']=='nền tảng'
        assert data['training_events']==6
        assert data['unique_question_evidence']==5
        assert data['topics'][1]['mastery_estimate'] is None
        assert 'expected' not in str(data) and 'explanation' not in str(data)
        assert client.get('/api/roadmap-v2/tutor-plan/10',headers=h2).json()['status']=='placement_required'
        with r.db() as conn:
            for topic in ['topic_1','topic_2','topic_3']:
                conn.execute('INSERT INTO roadmap_v2_mastery VALUES (?,?,?,?,?,?)',
                             (a,10,topic,26,1,r.now()))
            conn.commit()
        next_stage=client.get('/api/roadmap-v2/tutor-plan/10',headers=h).json()
        assert next_stage['current_stage']==2
        assert [x['topic_id'] for x in next_stage['topics']]==['topic_4']
        assert next_stage['next_topic']=='topic_4'


def test_adaptive_panel_mobile_and_no_client_side_trust():
    html=(ROOT/'learning-path.html').read_text(encoding='utf-8')
    js=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    css=(ROOT/'css/neon-v23-ai-tutor.css').read_text(encoding='utf-8')
    assert 'neon-v23-ai-tutor.css' in html
    assert "call('/tutor-plan/'+selected)" in js
    assert 'rec.learning_steps' in js and 'rec.reason' in js
    assert 'call(\'/submit/\'' in js
    assert 'max-width:680px' in css
    assert 'innerHTML' not in js[js.index('async function showTutor(){'):js.index('function goToQuestion(index){')]


def test_training_after_actual_submitted_fixed_exam_changes_adaptive_plan(tmp_path, monkeypatch):
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v23_live.db')
    database.init_database()
    topics=[{'id':'topic_assessed','title':'Tập hợp','grade':10}]
    blueprint={'grade':10,'version':'v23-integration','topics':[
        {'topic_id':'topic_assessed','title':'Tập hợp','tiers':{tier:3 for tier in r.DIFFICULTY}}]}
    questions=[]
    for tier in r.DIFFICULTY:
        for i in range(3):
            questions.append({'qid':f'approved-{tier}-{i}',
                'topic_id':'topic_assessed','title':'Tập hợp','grade':10,
                'difficulty':tier,'source':'qf2-approved','form_id':i%2+1,
                'question':f'Tính {i+2}+1 ở mức {tier}.',
                'choices':[str(i+3),str(i+4),str(i+5),str(i+6)] if i<2 else [],
                'correct':0 if i<2 else str(i+3),
                'question_type':'multiple_choice' if i<2 else 'written',
                'explanation':f'Cộng {i+2} với 1 để có {i+3}.'})
    monkeypatch.setattr(r,'_data',lambda:(topics,{}))
    monkeypatch.setattr(r,'_fixed_blueprint',lambda grade:(blueprint,topics))
    monkeypatch.setattr(r,'_approved_bank_for_grade',lambda grade:{})
    monkeypatch.setattr(r,'_lesson_reviews_for_grade',lambda grade:{})
    monkeypatch.setattr(r,'pool',lambda topic,approved=None,lesson_reviews=None:list(questions))
    import app.admin_routes as ar
    monkeypatch.setattr(ar,'require_admin',lambda auth:{'id':1})
    with TestClient(app) as client:
        published=client.post('/api/roadmap-v2/fixed/publish/10')
        assert published.status_code==200,published.text
        user=client.post('/api/auth/register',json={'username':'v23_online_bkt','password':'ValidPass9876!'}).json()
        h={'Authorization':'Bearer '+user['token']}
        started=client.post('/api/roadmap-v2/start',headers=h,json={'grade':10,'mode':'fixed_placement'})
        assert started.status_code==200,started.text
        paper=started.json()['questions']
        response={paper[0]['qid']:1,paper[1]['qid']:0,paper[2]['qid']:'3'}
        submitted=client.post('/api/roadmap-v2/submit/'+started.json()['attempt_id'],
                              headers=h,json={'answers':response})
        assert submitted.status_code==200,submitted.text
        assert submitted.json()['training_evidence']['unique_new_answers']==3
        plan=client.get('/api/roadmap-v2/tutor-plan/10',headers=h)
        assert plan.status_code==200,plan.text
        payload=plan.json()
        assert payload['status']=='ready'
        assert payload['trained_answers']==3
        assert payload['unique_question_evidence']==9  # Six skips are recorded but not trained.
        assert payload['topics'][0]['verified_answered']==3
        assert payload['topics'][0]['wrong']>=1
        assert payload['topics'][0]['mastery_estimate'] is not None
        assert payload['topics'][0]['action'] in ('remediate','practice_and_check')
