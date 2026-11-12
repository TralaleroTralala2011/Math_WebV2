"""V114: all 150 topics have generated, verified, non-duplicated candidates.

All types remain locked until expert review, not certified as independent.
"""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from question_factory import engine, storage, worker
from question_factory.bootstrap import initialize_factory
from question_factory.expanded_catalog import BLUEPRINTS as V113
from question_factory.v114_catalog import BLUEPRINTS as V114
from question_factory.v114_audit import audit


def test_v114_ten_mathematically_verified_examples_each_with_distinct_stems():
    seen=set()
    assert len(V114)==105
    for family,topic,description,signature,difficulty in V114:
        assert description and signature
        for i in range(10):
            record=engine.generate(family,i,difficulty,seed_key=f'{topic}:v114-{family}')
            assert record==engine.generate(family,i,difficulty,seed_key=f'{topic}:v114-{family}')
            valid,evidence=engine.independently_verify(record)
            assert valid,(family,i,evidence)
            assert record['fingerprint'] not in seen,(family,i)
            seen.add(record['fingerprint'])
            assert record['method_review_status']=='pending-expert-review'
    assert len(seen)==1050


def test_v114_mutated_answers_and_question_text_are_rejected():
    for family,topic,_,_,difficulty in V114:
        q=engine.generate(family,0,difficulty,seed_key=f'{topic}:v114-{family}')
        bad=dict(q,answer='9999999999999999')
        assert not engine.independently_verify(bad)[0],family
        bad=dict(q,stem='Câu hỏi đã bị thay đổi hoặc hỏng sau khi tạo.')
        assert not engine.independently_verify(bad)[0],family
        bad=dict(q,solution='Giải sai: nhận đáp án do người dùng cung cấp.')
        assert not engine.independently_verify(bad)[0],family
        bad=dict(q,params={'x':100})
        assert not engine.independently_verify(bad)[0],family


def test_v114_multiple_seeds_preserve_math_correctness_and_uniqueness():
    for seed in ('v114-second-seed','v114-third-seed'):
        seen=set()
        for family,topic,_,_,difficulty in V114:
            for ordinal in range(10):
                q=engine.generate(family,ordinal,difficulty,seed_key=f'{seed}:{topic}')
                valid,details=engine.independently_verify(q)
                assert valid,(seed,family,ordinal,details)
                assert q['fingerprint'] not in seen,(seed,family,ordinal)
                seen.add(q['fingerprint'])
        assert len(seen)==1050


def test_v114_all_150_topics_touched_by_actual_generation():
    catalog=json.loads((Path(__file__).parents[1]/'question_factory'/'catalog_150.json').read_text())
    touched={bp[1] for bp in V113+V114}
    assert len(catalog)==150 and len(touched)==150
    assert touched=={topic['id'] for topic in catalog}
    assert len(V113)==60


def test_v114_new_types_are_staged_never_auto_published(tmp_path):
    path=initialize_factory(str(tmp_path/'v114.sqlite3'))
    assert storage.seed_curated(path)==60
    assert storage.seed_v114(path)==105
    assert storage.seed_v114(path)==105
    state=storage.progress(path)
    assert state['topics']==150
    assert state['archetypes']==165
    assert state['approved_archetypes']==0
    assert state['pending_review_archetypes']==165
    assert storage.enqueue(path)==0
    assert worker.run(path,workers=2)==0
    assert storage.progress(path)['verified_questions']==0
    storage.approve(path,'v114-three_set_union','test-reviewer')
    assert storage.enqueue(path)==1
    assert worker.run(path,workers=3)==1
    assert len(storage.read_questions(path,'tap_hop'))==10
    assert storage.progress(path)['verified_questions']==10


def test_v114_audit_catches_duplication_and_keeps_zero_certification(tmp_path):
    legacy=tmp_path/'legacy.jsonl'
    # Valid JSON with a question identical to the new reference.
    family,topic,_,_,difficulty=V114[0]
    q=engine.generate(family,0,difficulty,seed_key=f'{topic}:v114-{family}')
    legacy.write_text(json.dumps({'question':q['stem']},ensure_ascii=False)+'\n',encoding='utf-8')
    r=audit(tmp_path/'audit',str(legacy))
    assert r['topics_with_a_new_candidate']==150
    assert r['new_stem_exact_collisions_with_legacy']==1
    assert r['total_v113_v114_math_verified_candidate_questions']==1650
    assert r['independently_certified_methods']==0
    assert r['expert_review_approved_methods']==0
    assert len((tmp_path/'audit'/'V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl').read_text().splitlines())==1650
