"""V18: published-paper integrity and safe answers, no mock certification."""
import copy

import pytest
from fastapi import HTTPException
from app.fixed_placement import assemble_fixed_paper, validate_frozen_paper
from app.roadmap_v2_routes import _check_answer_payload


def fixture_blueprint():
    topic={'topic_id':'vektor','title':'Vectơ','tiers':{
        'nền tảng':3,'trung cấp':3,'nâng cao':3}}
    blueprint={'version':'2026.11.12','grade':10,'topics':[topic]}
    questions=[]
    for tier in topic['tiers']:
        for n in range(3):
            questions.append({'qid':f'{tier}-{n}', 'topic_id':'vektor', 'title':'Vectơ',
                'grade':10,'difficulty':tier,'source':'qf2-approved', 'form_id':n%2+1,
                'question':f'Cho vectơ a, tính {tier} phép {n} từ a, giải thích kết quả?',
                'choices':['1','2','3','4'] if n<2 else [],
                'correct':0 if n<2 else '1',
                'question_type':'multiple_choice' if n<2 else 'written',
                'explanation':'Lời giải đã được kiểm chứng bởi người có chuyên môn.'})
    return blueprint, questions


def test_frozen_exam_strict_structure_and_tier_diversity():
    blueprint, items = fixture_blueprint()
    assert validate_frozen_paper(blueprint,items)
    bad=copy.deepcopy(items)
    bad[0]['form_id']=2  # tier still has other form, remains valid
    assert validate_frozen_paper(blueprint,bad)
    bad=copy.deepcopy(items)
    for q in bad:
        if q['difficulty']=='nền tảng':q['form_id']=1
    assert not validate_frozen_paper(blueprint,bad)
    for mutation in [lambda b: b.pop(),
                     lambda b: b[0].update(grade=11),
                     lambda b: b[0].update(question=b[1]['question']),
                     lambda b: b[0].update(source='lesson-candidate'),
                     lambda b: b[0].update(correct=5),
                     lambda b: b[0].update(qid=b[1]['qid'])]:
        b=copy.deepcopy(items)
        mutation(b)
        assert not validate_frozen_paper(blueprint,b)
    altered=copy.deepcopy(blueprint)
    altered['topics'][0]['tiers']['nâng cao']=4
    assert not validate_frozen_paper(altered,items)


def test_selected_questions_not_available_pool_determine_form_diversity():
    blueprint, items = fixture_blueprint()
    # Only the second approved form has duplicate statements with first form.
    # The selection must NOT pass the diversity gate based on IDs alone.
    for q in items:
        if q['form_id']==2:
            q['question']=next(x['question'] for x in items if x['difficulty']==q['difficulty'] and x['form_id']==1)
    result=assemble_fixed_paper(blueprint,{'vektor':items})
    assert not result['ready']
    assert result['distinct_form_gaps']
    assert all(d['selected_distinct_forms']<2 for d in result['distinct_form_gaps'])


def test_answer_bounding_applied_to_drafts_and_submissions():
    assert _check_answer_payload({'a':'123','b':0},{'a','b'})
    with pytest.raises(HTTPException) as e:
        _check_answer_payload({'a':'X'*2001},{'a'})
    assert e.value.status_code==422
    with pytest.raises(HTTPException) as e:
        _check_answer_payload({'not_my_question':'1'},{'a'})
    assert e.value.status_code==422
    with pytest.raises(HTTPException) as e:
        _check_answer_payload({'a':{'weird':'shape'}},{'a'})
    assert e.value.status_code==422
    large={str(i):'𝜋'*1900 for i in range(40)}
    with pytest.raises(HTTPException) as e:
        _check_answer_payload(large,set(large))
    assert e.value.status_code==413


def test_published_paper_invalidated_on_blueprint_change(tmp_path,monkeypatch):
    from database import database as database
    from app import roadmap_v2_routes as roadmap
    from app.fixed_placement import digest
    from fastapi.testclient import TestClient
    from app.main import app
    import app.admin_routes as admin_routes
    from pathlib import Path
    blueprint,questions=fixture_blueprint()
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v18.sqlite3')
    database.init_database()
    monkeypatch.setattr(roadmap,'_data',lambda:([{'id':'vektor','title':'Vectơ','grade':10}],{}))
    monkeypatch.setattr(roadmap,'_fixed_blueprint',lambda g:(blueprint,[{'id':'vektor','title':'Vectơ','grade':10}]))
    monkeypatch.setattr(roadmap,'_approved_bank_for_grade',lambda g:{})
    monkeypatch.setattr(roadmap,'_lesson_reviews_for_grade',lambda g:{})
    monkeypatch.setattr(roadmap,'pool',lambda t,approved=None,lesson_reviews=None:copy.deepcopy(questions))
    monkeypatch.setattr(admin_routes,'require_admin',lambda auth:{'id':1})
    with TestClient(app) as client:
        r=client.post('/api/roadmap-v2/fixed/publish/10')
        assert r.status_code==200,r.text
        first_paper_id=r.json()['paper_id']
        with roadmap.db() as conn:
            paper=roadmap._active_fixed_paper(conn,10)
            assert roadmap._paper_valid_now(10,paper)
        registration=client.post('/api/auth/register',json={
            'username':'v18_learner','password':'SafePass1234!'})
        assert registration.status_code==200,registration.text
        headers={'Authorization':'Bearer '+registration.json()['token']}
        started=client.post('/api/roadmap-v2/start',headers=headers,
            json={'grade':10,'mode':'fixed_placement'})
        assert started.status_code==200,started.text
        payload=started.json()
        answers={q['qid']:(0 if q['question_type']=='multiple_choice' else '1')
                 for q in payload['questions']}
        submitted=client.post('/api/roadmap-v2/submit/'+payload['attempt_id'],
            headers=headers,json={'answers':answers})
        assert submitted.status_code==200,submitted.text
        result=submitted.json()
        assert result['review']==[]
        assert result['review_release_policy']=='fixed_paper_protected'
        assert 'objective_evidence' in result
        for url in ('/api/roadmap-v2/status/10','/api/roadmap-v2/latest/10'):
            r=client.get(url,headers=headers)
            assert r.status_code==200,r.text
            assert 'review_notice' in r.text
            assert '"expected"' not in r.text and '"explanation"' not in r.text
        with roadmap.db() as conn:
            stored=conn.execute('SELECT result_json FROM roadmap_v2_attempts WHERE attempt_id=?',
                                (payload['attempt_id'],)).fetchone()
            assert 'explanation' in stored['result_json']  # server-side for admin review
        changed=copy.deepcopy(blueprint)
        changed['version']='2026.11.13'
        monkeypatch.setattr(roadmap,'_fixed_blueprint',lambda g:(changed,[{'id':'vektor','title':'Vectơ','grade':10}]))
        with roadmap.db() as conn:
            paper=roadmap._active_fixed_paper(conn,10)
            assert not roadmap._paper_valid_now(10,paper)
        republished=client.post('/api/roadmap-v2/fixed/publish/10')
        assert republished.status_code==200,republished.text
        assert republished.json()['paper_id']!=first_paper_id
        with roadmap.db() as conn:
            assert roadmap._paper_valid_now(10,roadmap._active_fixed_paper(conn,10))
