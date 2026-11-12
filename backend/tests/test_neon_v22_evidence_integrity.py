"""V22: unique evidence, skip-safe uncertainty, exact historical counts."""
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.fixed_placement import evidence_profile
from app import roadmap_v2_routes as roadmap
from database import database


def test_skipped_is_missing_evidence_not_incorrect_in_accuracy_interval():
    blueprint = {'grade': 10, 'topics': [
        {'topic_id': 'tap_hop', 'title': 'Tập hợp', 'tiers': {t: 3 for t in roadmap.DIFFICULTY}}
    ]}
    review = [
        {'topic_id': 'tap_hop', 'difficulty': 'nền tảng', 'verdict': 'correct', 'verified_for_diagnostic': True},
        {'topic_id': 'tap_hop', 'difficulty': 'nền tảng', 'verdict': 'skipped', 'verified_for_diagnostic': True},
        {'topic_id': 'tap_hop', 'difficulty': 'nền tảng', 'verdict': 'skipped', 'verified_for_diagnostic': True},
    ]
    result = evidence_profile(review, blueprint)['topics'][0]['tiers']['nền tảng']
    assert result['total'] == 3 and result['answered'] == 1
    assert result['skipped'] == 2 and result['wrong'] == 0
    assert result['percent_correct'] == 33.3  # paper completion score
    assert result['accuracy_among_answered'] == 100
    assert result['wilson_95_percent'][0] > 10  # interval on one answer, not three
    assert result['coverage_complete'] and not result['evidence_sufficient']
    only_skips = [{**r, 'verdict': 'skipped'} for r in review]
    no_answers=evidence_profile(only_skips, blueprint)['topics'][0]['tiers']['nền tảng']
    assert no_answers['wilson_95_percent'] is None
    assert no_answers['accuracy_among_answered'] is None
    assert not no_answers['evidence_sufficient']


def test_same_verified_question_does_not_train_twice_but_attempt_is_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DATABASE_PATH', tmp_path / 'v22_training.sqlite3')
    database.init_database()
    topic={'id':'tap_hop','title':'Tập hợp','grade':10}
    monkeypatch.setattr(roadmap,'_data',lambda:([topic],{}))
    q={'qid':'approved-same-001','topic_id':'tap_hop','title':'Tập hợp','grade':10,
       'difficulty':'nền tảng','source':'qf2-approved','form_id':15,
       'question':'Hai tập {1,2} và {2,3} giao nhau là gì?',
       'choices':['{2}','{1}','{3}','{1,3}'],'correct':0,
       'question_type':'multiple_choice','explanation':'Phần tử chung duy nhất là 2.'}
    with TestClient(app) as client:
        auth=client.post('/api/auth/register',json={'username':'v22_unique_student','password':'ValidPass9876!'}).json()
        headers={'Authorization':'Bearer '+auth['token']}
        user=auth['user']['id']
        for n in range(2):
            with roadmap.db() as conn:
                aid=roadmap._new_attempt(conn,user,10,'placement',None,[q])['attempt_id']
            submit=client.post('/api/roadmap-v2/submit/'+aid,headers=headers,
                               json={'answers':{q['qid']:0}})
            assert submit.status_code==200,submit.text
            evidence=submit.json()['training_evidence']
            assert evidence['verified_answered']==1
            assert evidence['unique_new_answers']==(1 if n==0 else 0)
            assert evidence['repeated_answers_excluded']==n
        with roadmap.db() as conn:
            state=conn.execute('SELECT observations FROM roadmap_v2_skill_state WHERE user_id=? AND grade=? AND topic_id=?',
                               (user,10,'tap_hop')).fetchone()
            events=conn.execute('SELECT COUNT(*) FROM roadmap_v2_learning_events WHERE user_id=?',(user,)).fetchone()[0]
        assert state['observations']==1
        assert events==2  # Full history retained without inflating the model


def test_skipped_topics_are_not_ranked_as_confirmed_weakness():
    weak={'correct':0,'wrong':4,'skipped':0}
    all_skipped={'correct':0,'wrong':0,'skipped':9}
    only_one={'correct':0,'wrong':1,'skipped':8}
    assert roadmap._placement_topic_priority(weak,4)<roadmap._placement_topic_priority(only_one,0)
    assert roadmap._placement_topic_priority(only_one,0)<roadmap._placement_topic_priority(all_skipped,0)
    assert roadmap._placement_topic_priority(all_skipped,0)<roadmap._placement_topic_priority(all_skipped,1)
