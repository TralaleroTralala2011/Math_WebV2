"""V25: evidence diversity, prospective comparison, safe migration and UI."""
import json
import math
import sqlite3
from pathlib import Path
from app import learner_online as ai

ROOT=Path(__file__).resolve().parents[2]


def test_same_type_successes_do_not_claim_predictive_readiness():
    state=ai.empty_state()
    for _ in range(100):
        ai.learn(state,'only_topic','nền tảng','correct')
    report=ai.public_report(state)
    assert state['n']==100
    assert not report['ready_for_soft_suggestions']
    assert report['population_calibrated'] is False
    assert report['readiness_reasons']
    assert ai.suggestions_for_topic(state,'only_topic')['predicted_correct']=={}


def test_diverse_evidence_and_prospective_performance_can_offer_soft_advice():
    state=ai.empty_state()
    for i in range(120):
        topic=['T-A','T-B','T-C'][i%3]
        tier=['nền tảng','trung cấp','nâng cao'][i%3]
        verdict='wrong' if topic=='T-C' else 'correct'
        assert ai.learn(state,topic,tier,verdict)
    report=ai.public_report(state)
    assert report['evaluated_after_warmup']==110
    assert report['held_forward_brier']<report['reference_brier']
    assert report['ready_for_soft_suggestions']
    # A globally ready predictor may not choose tiers for a topic with no
    # level variation: only actual topic-level evidence can enable that.
    assert not ai.suggestions_for_topic(state,'T-A')['predictive_ready']
    assert report['population_calibrated'] is False


def test_topic_level_tier_diversity_is_required_and_prediction_is_optional():
    state=ai.empty_state()
    for i in range(150):
        topic=['T-A','T-B','T-C'][i%3]
        tier=['nền tảng','trung cấp','nâng cao'][(i//3)%3]
        verdict='wrong' if topic=='T-C' else 'correct'
        ai.learn(state,topic,tier,verdict)
    report=ai.public_report(state)
    assert report['ready_for_soft_suggestions']
    rec=ai.suggestions_for_topic(state,'T-A')
    assert rec['predictive_ready']
    assert set(rec['predicted_correct'])==set(ai.TIERS)
    assert all(0 < p < 1 for p in rec['predicted_correct'].values())
    assert all(rec['tier_evidence'][tier]['answered']>=2 for tier in ai.TIERS)


def test_skips_and_candidates_dont_pollute_and_replay_is_deterministic():
    events=[
        dict(qid='x1',topic_id='T-A',tier='nền tảng',verdict='skipped',source='qf2-approved'),
        dict(qid='x1',topic_id='T-A',tier='nền tảng',verdict='wrong',source='qf2-approved'),
        dict(qid='x1',topic_id='T-A',tier='nền tảng',verdict='correct',source='qf2-approved'),
        dict(qid='x2',topic_id='T-B',tier='nâng cao',verdict='correct',source='lesson-candidate'),
        dict(qid='x3',topic_id='T-C',tier='nâng cao',verdict='correct',source='lesson-reviewed'),
    ]
    assert ai.replay_events(events)==ai.replay_events(events)
    state=ai.replay_events(events)
    assert (state['n'],state['right'])==(2,1)
    assert state['evaluated_count']==0
    assert not ai.public_report(state)['ready_for_soft_suggestions']


def test_invalid_or_old_predictor_state_causes_retrain_not_an_exception():
    con=sqlite3.connect(':memory:');con.row_factory=sqlite3.Row
    ai.create_table(con)
    con.execute('INSERT INTO roadmap_v2_personal_predictors VALUES (?,?,?,?,?,?)',
                (8,11,ai.VERSION,json.dumps({'version':ai.VERSION,'weights':[float('nan')]*5}),1,'now'))
    assert ai.load(con,8,11) is None
    con.execute('''CREATE TABLE roadmap_v2_learning_events (
        user_id INTEGER, grade INTEGER, attempt_id TEXT, qid TEXT, topic_id TEXT,
        tier TEXT, verdict TEXT, source TEXT, created_at TEXT)''')
    con.execute('INSERT INTO roadmap_v2_learning_events VALUES (?,?,?,?,?,?,?,?,?)',
                (8,11,'a1','q1','T','nền tảng','correct','qf2-approved','2026-11-12'))
    state=ai.ensure(con,8,11)
    assert state['n']==1 and math.isfinite(ai.probability(state,'T','nền tảng'))
    assert ai.load(con,8,11)['n']==1


def test_ui_describes_prediction_baseline_and_reasons_without_leaking_answers():
    js=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    assert 'model.readiness_reasons' in js
    assert 'model.reference_brier' in js
    assert 'chưa được hiệu chuẩn' in js or 'chưa hiệu chuẩn' in js
    a=js.index('async function showTutor(){');b=js.index('function goToQuestion(index){')
    assert 'innerHTML' not in js[a:b]


def test_adaptive_plan_chooses_tier_with_verified_errors_not_model_guess(tmp_path,monkeypatch):
    """A learner who misses hard questions receives targeted hard-level review."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app import roadmap_v2_routes as road
    from database import database
    monkeypatch.setattr(database,'DATABASE_PATH',tmp_path/'tier_review.db')
    database.init_database()
    topics=[{'id':'T-target','title':'Hàm số','grade':10}]
    monkeypatch.setattr(road,'_data',lambda:(topics,{}))
    monkeypatch.setattr(road,'_paper_valid_now',lambda grade,paper:True)
    with TestClient(app) as client:
        reg=client.post('/api/auth/register',json={
            'username':'v25_focus_review','password':'ValidPass9876!'}).json()
        uid=reg['user']['id'];header={'Authorization':'Bearer '+reg['token']}
        result={'grade':10,'mode':'fixed_placement','fixed_paper_hash':'v25-fixed',
                'diagnostic_completeness':{'content_coverage_complete':True},
                'roadmap_order':['T-target']}
        with road.db() as c:
            c.execute('INSERT INTO roadmap_v2_fixed_papers VALUES (?,?,?,?,?,?,?,?)',
                      ('v25-paper',10,'v25-fixed','blueprint','[]',road.now(),99,1))
            c.execute('INSERT INTO roadmap_v2_attempts VALUES (?,?,?,?,?,?,?,?,?,?)',
                      ('v25-attempt',uid,10,'fixed_placement',None,'[]',road.now(),'{}',
                       json.dumps(result),road.now()))
            for i,(tier,verdict) in enumerate([
                    ('nền tảng','correct'),('nền tảng','correct'),
                    ('nâng cao','wrong'),('nâng cao','wrong'),('nâng cao','skipped')]):
                c.execute('INSERT INTO roadmap_v2_learning_events VALUES (?,?,?,?,?,?,?,?,?)',
                          (uid,10,f'attempt{i}',f'question{i}','T-target',tier,verdict,
                           'qf2-approved',road.now()))
            c.execute('INSERT INTO roadmap_v2_skill_state VALUES (?,?,?,?,?,?,?)',
                      (uid,10,'T-target','nền tảng',.80,2,road.now()))
            c.execute('INSERT INTO roadmap_v2_skill_state VALUES (?,?,?,?,?,?,?)',
                      (uid,10,'T-target','nâng cao',.28,2,road.now()))
            c.commit()
        response=client.get('/api/roadmap-v2/tutor-plan/10',headers=header)
        assert response.status_code==200,response.text
        body=response.json();assert body['status']=='ready'
        topic=body['topics'][0]
        assert topic['focus_tier']=='nâng cao'
        assert topic['wrong']==2 and topic['skipped']==1
        assert '2/2' in topic['focus_basis']
        assert topic['online_prediction_ready'] is False
        assert topic['action']=='practice_and_check' or topic['action']=='remediate'
