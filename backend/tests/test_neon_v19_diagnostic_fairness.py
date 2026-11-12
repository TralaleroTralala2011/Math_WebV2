"""NEON V19: fixed placement content readiness != psychometric validation.

Skipping questions must be retained in diagnostics but not treated as proof
that a learner has low proficiency. Never publish an answer key to learners.
"""
from fastapi.testclient import TestClient
from app.main import app
from app import roadmap_v2_routes as roadmap
from database import database as database


def test_paper_ready_not_misrepresented_as_psychometric_validation(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DATABASE_PATH', tmp_path/'v19.db')
    database.init_database()
    topic={'id':'test_topic','title':'Tập hợp','grade':10}
    blueprint={'version':'v19-pilot','grade':10,'topics':[
        {'topic_id':'test_topic','title':'Tập hợp',
         'tiers':{'nền tảng':3,'trung cấp':3,'nâng cao':3}}]}
    questions=[]
    for tier in roadmap.DIFFICULTY:
        for i in range(3):
            kind = 'written' if i==2 else 'multiple_choice'
            questions.append({'qid':f'{tier}:{i}', 'topic_id':'test_topic',
               'title':'Tập hợp', 'grade':10, 'difficulty':tier,
               'source':'qf2-approved', 'form_id':i%2+1,
               'question':f'Tính {i+1}+1 ở mức {tier}.',
               'choices':[str(i+2),str(i+3),str(i+4),str(i+5)] if kind=='multiple_choice' else [],
               'correct':0 if kind=='multiple_choice' else str(i+2),
               'question_type':kind,'explanation':'Cộng đúng số hạng.'})
    monkeypatch.setattr(roadmap,'_data',lambda:([topic],{}))
    monkeypatch.setattr(roadmap,'_fixed_blueprint',lambda grade:(blueprint,[topic]))
    monkeypatch.setattr(roadmap,'_approved_bank_for_grade',lambda grade:{})
    monkeypatch.setattr(roadmap,'_lesson_reviews_for_grade',lambda grade:{})
    monkeypatch.setattr(roadmap,'pool',lambda t,approved=None,lesson_reviews=None:list(questions))
    import app.admin_routes as admin_routes
    monkeypatch.setattr(admin_routes,'require_admin',lambda auth:{'id':1})
    with TestClient(app) as client:
        published=client.post('/api/roadmap-v2/fixed/publish/10')
        assert published.status_code==200,published.text
        registered=client.post('/api/auth/register',json={'username':'v19_learner','password':'ValidPass9876!'})
        assert registered.status_code==200,registered.text
        headers={'Authorization':'Bearer '+registered.json()['token']}
        status=client.get('/api/roadmap-v2/fixed/status/10',headers=headers).json()
        assert status['published_valid'] is True
        assert status['psychometric_validated'] is False
        assert status['validation_stage']=='content_reviewed_not_empirically_validated'
        started=client.post('/api/roadmap-v2/start',headers=headers,json={
            'grade':10,'mode':'fixed_placement'})
        assert started.status_code==200,started.text
        # One correct answer and eight skipped answers.
        first=started.json()['questions'][0]
        selected=0 if first['question_type']=='multiple_choice' else '2'
        submitted=client.post('/api/roadmap-v2/submit/'+started.json()['attempt_id'],
            headers=headers,json={'answers':{first['qid']:selected}})
        assert submitted.status_code==200,submitted.text
        result=submitted.json()
        assert result['skipped']==8
        assert result['diagnostic_completeness']['content_coverage_complete']
        assert result['diagnostic_completeness']['psychometric_validated'] is False
        assert result['review']==[]
        assert result['objective_evidence']['topics'][0]['tiers']
        with roadmap.db() as conn:
            states=conn.execute('SELECT observations FROM roadmap_v2_skill_state WHERE user_id=?',
                                (registered.json()['user']['id'],)).fetchall()
        assert sum(x['observations'] for x in states)==1
        assert all(x['observations']==1 for x in states)
