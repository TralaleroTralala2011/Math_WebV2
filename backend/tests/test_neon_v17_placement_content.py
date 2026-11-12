"""V17 placement pilot: deterministic, math-checked candidates, no auto approval."""
from collections import Counter

from app.fixed_placement import assemble_fixed_paper
from app.qf2_verified_generators import PLACEMENT_GENERATORS
from app.question_factory_v2_routes import Candidate, norm_exact
from app.ai.engine.validator import options_equivalent


def test_six_new_original_forms_sixty_distinct_questions():
    forms = [Candidate.model_validate(generator()) for generator in PLACEMENT_GENERATORS.values()]
    assert len(forms) == 6
    assert Counter(f.grade for f in forms) == {10: 2, 11: 2, 12: 2}
    assert len({(f.grade, f.topic_id, f.method) for f in forms}) == 6
    for form in forms:
        assert len(form.questions) == 10
        assert len({norm_exact(q.question) for q in form.questions}) == 10
        assert Counter(q.question_type for q in form.questions) == {
            'multiple_choice': 7, 'written': 2, 'true_false': 1}
        assert Counter(q.difficulty for q in form.questions) == {
            'nền tảng': 4, 'trung cấp': 3, 'nâng cao': 3}
        for q in form.questions:
            assert len(q.explanation) >= 24
            if q.question_type == 'multiple_choice':
                assert q.answer == q.choices[q.correct_index]
                assert all(not options_equivalent(a, b)
                           for i, a in enumerate(q.choices) for b in q.choices[i+1:])


def test_fixed_exam_requires_two_distinct_approved_forms_in_each_tier():
    topic={'id':'cap_so_nhan','title':'Cấp số nhân','grade':11}
    blueprint={'grade':11,'version':'v17','topics':[{'topic_id':topic['id'],
        'title':topic['title'],'tiers':{'nền tảng':3,'trung cấp':3,'nâng cao':3}}]}
    one_form=[]
    for tier in ('nền tảng','trung cấp','nâng cao'):
        for i in range(4):
            one_form.append({'qid':f'{tier}-{i}', 'form_id':42,'topic_id':topic['id'],
                'title':topic['title'],'grade':11,'difficulty':tier,
                'source':'qf2-approved','question':f'Bài {i} {tier}: u₁=2, q=3, tính u₅?',
                'choices':['162','81','54','243'] if i%2 else [],
                'correct':0 if i%2 else '162',
                'question_type':'multiple_choice' if i%2 else 'written',
                'explanation':'Số hạng thứ năm bằng 2×3^4=162.'})
    blocked=assemble_fixed_paper(blueprint,{topic['id']:one_form})
    assert not blocked['ready']
    assert len(blocked['distinct_form_gaps'])==3
    assert all(x['available_distinct_forms']==1 for x in blocked['distinct_form_gaps'])
    second=[{**q,'qid':q['qid']+'-2','form_id':43,
             'question':q['question']+' Đề phiên bản phương pháp khác.'} for q in one_form]
    ready=assemble_fixed_paper(blueprint,{topic['id']:one_form+second})
    assert ready['ready']
    assert ready['selected']==9
    assert len({q['form_id'] for q in ready['questions']})==2
    assert ready['distinct_form_gaps']==[]


def test_equivalent_tangent_line_answers_are_graded_correctly():
    from app.questions.answer_checker import grade_answer
    q={'question_type':'short_answer'}
    assert grade_answer(q,'y=2x+3','y=2x+(3)')
    assert grade_answer(q,'2y=4x+6','y=2x+3')
    assert grade_answer(q,'y=2*x+3','y=2x+3')
    assert not grade_answer(q,'y=2x+4','y=2x+3')
    assert not grade_answer(q,'x=3','x=2')
    assert not grade_answer(q,'__import__("os").system("id")','y=2x+3')
    assert not grade_answer(q,'y=x**999999999','y=x')


def test_placement_expansion_admin_only_pending_and_idempotent(tmp_path, monkeypatch):
    import app.question_factory_v2_routes as qf2
    from database import database as database
    from fastapi import HTTPException
    from fastapi.testclient import TestClient
    from app.main import app
    from app import roadmap_v2_routes as roadmap
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v17.sqlite3')
    database.init_database()

    def fake_admin(auth):
        if auth!='Bearer v17-admin':raise HTTPException(403,'Admin only')
        return {'id':1}
    monkeypatch.setattr(qf2,'require_admin',fake_admin)
    with TestClient(app) as client:
        url='/api/admin/qf2/generate/placement-expansion'
        assert client.post(url).status_code==403
        first=client.post(url,headers={'Authorization':'Bearer v17-admin'})
        assert first.status_code==200,first.text
        assert first.json()['created_forms']==6
        assert first.json()['created_questions']==60
        second=client.post(url,headers={'Authorization':'Bearer v17-admin'}).json()
        assert second['already_present']==6
        assert second['created_questions']==0
        topic=next(t for t in roadmap._data()[0] if t['id']=='tap_hop')
        assert not [q for q in roadmap.pool(topic) if q['source']=='qf2-approved']


def test_fake_approved_source_without_real_approved_form_is_ignored(tmp_path,monkeypatch):
    from database import database as database
    from app import roadmap_v2_routes as roadmap
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'v17_fake.sqlite3')
    database.init_database()
    with database.get_connection() as c:
        c.execute('''INSERT INTO admin_question_bank
            (grade,topic,difficulty,question_type,question,choices_json,
             correct_answer,explanation,source,tags_json,created_at,updated_at)
            VALUES(10,'tap_hop','nền tảng','multiple_choice',?,?,'2',?, ?, ?, 'now','now')''',
            ('Cho A={1,2}, B={2,3}. Tính A∩B.',
             '["2","3","4","5"]','Giao là tập hợp các phần tử chung.',
             'Question Factory 2.0 · independently reviewed','["qf2","reviewed","form:999"]'))
        c.commit()
    assert roadmap._approved_bank_for_grade(10).get('tap_hop',[])==[]
