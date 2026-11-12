"""V20: QA every original placement review candidate; never auto-certify."""
from collections import Counter
from fractions import Fraction
from math import comb
import re

from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.question_factory_v2_routes import Candidate
from app.placement_v20_original_forms import candidate_forms
from app.ai.engine.validator import options_equivalent
from database import database


def value(x):
    # The written and MCQ keys must represent the same mathematical value.
    x=str(x)
    if x.endswith('π'):
        return ('pi', int(x[:-1]))
    return Fraction(x)


def test_31_original_methods_and_all_310_candidate_items():
    forms=candidate_forms()
    assert len(forms)==31
    assert Counter(f['grade'] for _,f in forms)=={10:10,11:10,12:11}
    assert len({(f['grade'],f['topic_id'],f['method']) for _,f in forms})==31
    assert sum(len(f['questions']) for _,f in forms)==310
    all_question_text=[]
    for slug,raw in forms:
        form=Candidate.model_validate(raw)
        assert len(form.questions)==10
        assert len({q.question for q in form.questions})==10,slug
        assert Counter(q.question_type for q in form.questions)=={
            'multiple_choice':7,'written':2,'true_false':1}
        assert Counter(q.difficulty for q in form.questions)=={
            'nền tảng':4,'trung cấp':3,'nâng cao':3}
        for i,q in enumerate(form.questions):
            all_question_text.append(q.question)
            assert len(q.explanation)>=24
            if q.question_type=='multiple_choice':
                assert q.answer==q.choices[q.correct_index]
                assert len(q.choices)==4
                assert all(not options_equivalent(a,b)
                           for ia,a in enumerate(q.choices) for b in q.choices[ia+1:]),slug
            elif q.question_type=='true_false':
                assert q.answer in ('Đúng','Sai')
            else:
                assert q.answer
            # Independently recomputed expected value from the transparent
            # deterministic parameter specifications; this is algorithmic QA,
            # not the required independent teacher review.
            answer=q.answer if q.question_type!='true_false' else q.question.split('Khẳng định đáp án là ',1)[1].split('. Đúng hay sai?')[0]
            if q.question_type=='true_false':
                # Verify whether the asserted answer equals the actual value.
                correct=value(_expected(slug,i))==value(answer)
                assert q.answer==('Đúng' if correct else 'Sai'),(slug,i)
            else:
                assert value(answer)==value(_expected(slug,i)),(slug,i,answer,_expected(slug,i))
    assert len(set(all_question_text))==310


def _as_fraction(n,d):
    return str(Fraction(n,d).numerator) if Fraction(n,d).denominator==1 else str(Fraction(n,d))


def _expected(slug,i):
    if slug=='g10-system-substitution':return (i%5-2)+(i//2-1)
    if slug=='g10-counting-multiplication':return (i+2)*(i%4+3)
    if slug=='g10-combinations-unordered':return comb(i+4,2+i%2)
    if slug=='g10-classical-probability':return _as_fraction(i%4+2,(i%4+2)+(i//2+3))
    if slug=='g10-sample-mean':return i+5
    if slug=='g10-vector-dot':return (i%5-2)*(i//2-3)+(i%4+1)*(3-i%3)
    if slug=='g10-coordinate-midpoint':return (i-4)+(3-i%6)
    if slug=='g10-linear-root':return i-5
    if slug=='g10-linear-inequality':return i-4
    if slug=='g10-circle-radius':return i%5+2
    if slug=='g11-polynomial-derivative':
        x=i%5-2
        return 3*(i%3+1)*x*x+2*(2-i)*x+(i-3)
    if slug=='g11-factor-limit':return 2*(i-4)+(i%5+1)
    if slug=='g11-translation':return (i-4)+(2-i%5)+(i%4+1)+(i%3-2)
    if slug=='g11-reflection-axis':return (i-5)-(i%7-3)
    if slug=='g11-median':return i+1
    if slug=='g11-continuity-parameter':return (i%5+1)*(i-4)+(i%3-2)
    if slug=='g11-independent-events':return _as_fraction((i%4+2)*(i%3+3), (i%4+4)*(i%3+6))
    if slug=='g11-additive-recurrence':return (i-3)+(3+(i%6)-1)*(i%5+1)
    if slug=='g11-origin-homothety':return (i%4+2)*((i%5-2)+(i//2-2))
    if slug=='g11-trigonometric-identity':return (i%4+1)**2+(i%5+1)**2
    if slug=='g12-exponential-equation':return i+1
    if slug=='g12-basic-logarithm':return (i%3+2)**(i%4+1)
    if slug=='g12-definite-polynomial-integral':
        n=2*(i%5+1)
        return Fraction((i%4+1)*n*n,2)+(i-4)*n
    if slug=='g12-global-minimum':return i%5-2
    if slug=='g12-plane-normal':return (i%4+1)+(i%3-2)+(i%5+1)
    if slug=='g12-sphere-radius':return i%6+2
    if slug=='g12-point-horizontal-plane-distance':return abs((i%6-2)-(i//2-3))
    if slug=='g12-cylinder-volume':return f'{(i%4+1)**2*(i%6+2)}π'
    if slug=='g12-vector-3d-norm-squared':return (i-4)**2+(i%5-2)**2+(i//2-2)**2
    if slug=='g12-rational-vertical-asymptote':return i-5
    if slug=='g12-population-variance':return _as_fraction(2*(i%5+1)**2,3)
    raise AssertionError(slug)


def test_staging_admin_only_and_never_approves(tmp_path,monkeypatch):
    from app import question_factory_v2_routes as qf
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'placement_v20.sqlite3')
    database.init_database()
    def admin_only(auth):
        if auth != 'Bearer v20-admin':raise HTTPException(403,'Forbidden')
        return {'id':100}
    monkeypatch.setattr(qf,'require_admin',admin_only)
    with TestClient(app) as c:
        url='/api/admin/qf2/generate/placement-v20-review-batch'
        assert c.post(url).status_code==403
        first=c.post(url,headers={'Authorization':'Bearer v20-admin'})
        assert first.status_code==200,first.text
        data=first.json()
        assert data['created_forms']==31,data
        assert data['created_questions']==310,data
        assert not data['errors']
        again=c.post(url,headers={'Authorization':'Bearer v20-admin'}).json()
        assert again['created_forms']==0
        assert again['already_present']==31
        with database.get_connection() as con:
            statuses=con.execute('SELECT status,COUNT(*) AS n FROM qf2_forms GROUP BY status').fetchall()
        assert [(x['status'],x['n']) for x in statuses]==[('pending_review',31)]


def test_frozen_paper_rejects_equivalent_multiple_choice_answers():
    from app.fixed_placement import validate_frozen_paper
    blueprint={'grade':10,'version':'pilot','topics':[
        {'topic_id':'topic','title':'Chủ đề kiểm tra','tiers':{'nền tảng':3,'trung cấp':3,'nâng cao':3}}]}
    questions=[]
    for tier in ('nền tảng','trung cấp','nâng cao'):
        for i in range(3):
            kind='written' if i==2 else 'multiple_choice'
            questions.append({'qid':f'{tier}-{i}','topic_id':'topic','grade':10,
                'title':'Chủ đề kiểm tra','difficulty':tier,'form_id':i%2+1,
                'question':f'Tính tổng {i+2}+{i+3} trong chủ đề {tier}.',
                'question_type':kind,'source':'qf2-approved','explanation':'Cộng hai số nguyên theo định nghĩa.',
                'choices':[str(i+5),str(i+6),str(i+7),str(i+8)] if kind=='multiple_choice' else [],
                'correct':0 if kind=='multiple_choice' else str(i+5)})
    assert validate_frozen_paper(blueprint,questions)
    questions[0]['choices']=['1/2','0,5','1','2']
    assert not validate_frozen_paper(blueprint,questions)
