"""V10: quality transparency survives resuming a placement assessment."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.roadmap_v2_routes import assessment_quality
from database import database as db


def test_quality_counts_are_per_topic_and_certified_only():
    topics=[{'id':'a','title':'A'},{'id':'b','title':'B'}]
    questions=[{'topic_id':'a','difficulty':tier,'source':'qf2-approved'} for tier in ('nền tảng','trung cấp','nâng cao') for _ in range(3)]
    questions += [{'topic_id':'b','difficulty':tier,'source':'lesson-candidate'} for tier in ('nền tảng','trung cấp','nâng cao') for _ in range(3)]
    quality=assessment_quality(questions,topics)
    assert not quality['complete_three_tier_coverage']
    assert quality['topics_missing_verified_tiers']==1
    assert quality['reviewed_items']==9
    assert quality['unreviewed_items']==9
    assert quality['missing_topic_details'][0]['topic_id']=='b'


def test_resumed_placement_has_same_quality_report(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'v10.db')
    db.init_database()
    with TestClient(app) as client:
        r=client.post('/api/auth/register',json={'username':'V10Student','password':'SafePass1234!'})
        assert r.status_code==200,r.text
        headers={'Authorization':'Bearer '+r.json()['token']}
        payload={'grade':10,'mode':'placement'}
        first=client.post('/api/roadmap-v2/start',json=payload,headers=headers)
        assert first.status_code==200,first.text
        second=client.post('/api/roadmap-v2/start',json=payload,headers=headers)
        assert second.status_code==200,second.text
        assert second.json()['resumed'] is True
        assert second.json()['attempt_id']==first.json()['attempt_id']
        assert second.json()['assessment_quality']==first.json()['assessment_quality']
