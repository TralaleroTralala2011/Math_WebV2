"""NEON V21: mobile MathGeo handoff and privacy-preserving online learner model."""
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app import roadmap_v2_routes as r
from database import database

ROOT = Path(__file__).resolve().parents[2]


def test_bayesian_updates_behave_and_are_bounded():
    for tier in r.DIFFICULTY:
        yes=r._bkt_next(.35,True,tier)
        no=r._bkt_next(.35,False,tier)
        assert 0.35<yes<.98
        assert 0.02<no<.35
    assert r._bkt_next(0,False,'nền tảng')>=.02
    assert r._bkt_next(1,True,'nâng cao')<=.98


def test_mobile_toolbar_and_mathgeo_question_handoff():
    studio=(ROOT/'geometry-studio.html').read_text(encoding='utf-8')
    css=(ROOT/'css/geometry-mobile-v21.css').read_text(encoding='utf-8')
    js=(ROOT/'js/geometry-mobile-v21.js').read_text(encoding='utf-8')
    roadmap=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    assert 'data-geo-tool="point"' in studio
    assert 'data-geo-tool="pan"' in studio
    assert 'pointerdown' in studio and 'pointermove' in studio
    assert 'activePointers' in studio and 'pinchDistance' in studio
    assert 'get(\'question\')' in studio
    assert 'max-width:850px' in css and 'geo-panel-open' in css
    assert 'aria-pressed' in js and "real.click()" in js
    # V27 intentionally replaces the popup-only action with a verified inline SVG preview.
    inline=(ROOT/'js/geometry-inline-v27.js').read_text(encoding='utf-8')
    assert 'MATHWEB_INLINE_GEOMETRY?.render(q)' in roadmap
    assert 'document.createElementNS' in inline
    assert 'KHÔNG dùng hình để suy ra độ dài' in inline
    assert 'if(window.opener && new URLSearchParams(location.search).get(\'from\')===\'admin\')' in studio
    assert 'MATHWEB_GEOMETRY_STUDENT_PNG' in studio and 'geoStudentPreviews.set' in roadmap


def test_trained_evidence_saved_private_skipped_not_penalized(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v21_private.sqlite3')
    database.init_database()
    topic={'id':'topic_10','title':'Tập hợp','grade':10}
    blueprint={'grade':10,'version':'v21-test','topics':[{'topic_id':topic['id'],'title':topic['title'],
             'tiers':{tier:3 for tier in r.DIFFICULTY}}]}
    questions=[]
    for tier in r.DIFFICULTY:
        for i in range(3):
            kind='written' if i==2 else 'multiple_choice'
            questions.append({'qid':f'{tier}-{i}','topic_id':topic['id'],'title':topic['title'],
                 'grade':10,'difficulty':tier,'source':'qf2-approved','form_id':1+(i%2),
                 'question':f'Câu tập hợp {tier} số {i} có phép cộng 1+1?',
                 'choices':['2','3','4','5'] if kind=='multiple_choice' else [],
                 'correct':0 if kind=='multiple_choice' else '2',
                 'question_type':kind,'explanation':'Áp dụng số tự nhiên: 1 + 1 = 2.'})
    monkeypatch.setattr(r,'_data',lambda:([topic],{}))
    monkeypatch.setattr(r,'_fixed_blueprint',lambda grade:(blueprint,[topic]))
    monkeypatch.setattr(r,'_approved_bank_for_grade',lambda grade:{})
    monkeypatch.setattr(r,'_lesson_reviews_for_grade',lambda grade:{})
    monkeypatch.setattr(r,'pool',lambda t,approved=None,lesson_reviews=None:list(questions))
    import app.admin_routes as admin_routes
    monkeypatch.setattr(admin_routes,'require_admin',lambda auth:{'id':1})
    with TestClient(app) as client:
        assert client.post('/api/roadmap-v2/fixed/publish/10').status_code==200
        first=client.post('/api/auth/register',json={'username':'v21_student1','password':'ValidPass9876!'}).json()
        second=client.post('/api/auth/register',json={'username':'v21_student2','password':'ValidPass9876!'}).json()
        headers={'Authorization':'Bearer '+first['token']}
        other={'Authorization':'Bearer '+second['token']}
        assert client.get('/api/roadmap-v2/tutor-data/10').status_code in (401,403)
        start=client.post('/api/roadmap-v2/start',headers=headers,json={'grade':10,'mode':'fixed_placement'})
        assert start.status_code==200,start.text
        qs=start.json()['questions']
        # Correct and wrong from separate tiers; seven skipped are recorded.
        correct_q=qs[0];wrong_q=qs[3]
        answers={correct_q['qid']:(0 if correct_q['question_type']=='multiple_choice' else '2'),
                 wrong_q['qid']:(1 if wrong_q['question_type']=='multiple_choice' else '100')}
        done=client.post('/api/roadmap-v2/submit/'+start.json()['attempt_id'],headers=headers,json={'answers':answers})
        assert done.status_code==200,done.text
        assert done.json()['training_evidence']['verified_answered']==2
        assert done.json()['training_evidence']['verified_skipped']==7
        assert done.json()['review']==[]
        profile=client.get('/api/roadmap-v2/tutor/10',headers=headers)
        assert profile.status_code==200,profile.text
        assert profile.json()['training_events']==9
        assert profile.json()['topics_assessed']==1
        assert profile.json()['recommendations'][0]['observations']==2
        exported=client.get('/api/roadmap-v2/tutor-data/10',headers=headers)
        assert exported.status_code==200
        assert len(exported.json()['events'])==9
        assert {e['verdict'] for e in exported.json()['events']}=={'correct','wrong','skipped'}
        assert all('question' not in e and 'answer' not in e and 'user_id' not in e for e in exported.json()['events'])
        other_export=client.get('/api/roadmap-v2/tutor-data/10',headers=other)
        assert other_export.status_code==200 and other_export.json()['total_events']==0
        with r.db() as conn:
            observations=conn.execute('SELECT SUM(observations) FROM roadmap_v2_skill_state WHERE user_id=?',(first['user']['id'],)).fetchone()[0]
            events=conn.execute('SELECT COUNT(*) FROM roadmap_v2_learning_events WHERE user_id=?',(first['user']['id'],)).fetchone()[0]
        assert observations==2 and events==9
