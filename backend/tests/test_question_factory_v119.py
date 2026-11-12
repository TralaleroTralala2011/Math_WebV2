from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
import pytest
from question_factory import engine, storage, worker, v119_research
from question_factory.bootstrap import initialize_factory
from question_factory.operations import once


def test_v119_30_methods_three_matching_topics_and_ten_examples():
    methods=v119_research.METHODS
    assert len(methods)==30
    assert Counter(m.topic for m in methods)=={'tap_hop':10,'bien_co_doc_lap_11':10,'so_phuc':10}
    catalog={r['id']:r for r in json.loads((Path(__file__).resolve().parents[1]/'question_factory/catalog_150.json').read_text(encoding='utf8'))}
    seen_stems=set()
    for m in methods:
        assert m.topic in catalog and catalog[m.topic]['grade']==m.grade
        seen_params=set()
        for ordinal in range(10):
            q=engine.generate(m.family,ordinal,m.difficulty,seed_key='v119-batch')
            okay,report=engine.independently_verify(q)
            assert okay,(m.family,ordinal,report)
            assert q['topic_id']==m.topic
            assert q['independence_certified'] is False
            assert q['method_review_status']=='pending-expert-review'
            assert q['stem'] not in seen_stems
            seen_stems.add(q['stem'])
            p=json.dumps(q['params'],sort_keys=True,ensure_ascii=False)
            assert p not in seen_params,(m.family,ordinal)
            seen_params.add(p)
        assert len(seen_params)==10
    assert len(seen_stems)==300


def test_v119_tampering_answer_and_mcq_blocked():
    for m in v119_research.METHODS:
        item=v119_research.generate(m.family,1)
        assert item['question_type']=='trac_nghiem'
        assert len(item['options'])==4 and len(set(item['options']))==4
        assert item['options'][item['correct_index']]==item['answer']
        for change in ({'answer':'999'}, {'stem':'bad'}, {'solution':'bad'},
                       {'correct_index':99},{'params':{'a':9999}}, {'numeric_result':'900'}):
            assert not engine.independently_verify({**item,**change})[0]


def test_v119_registration_review_lock_and_worker(tmp_path):
    db=initialize_factory(str(tmp_path/'factory.sqlite3'))
    assert storage.seed_v119(db)==30
    assert storage.seed_v119(db)==30
    state=storage.progress(db)
    assert state['topics']==150 and state['archetypes']==30
    assert state['approved_archetypes']==0
    assert storage.enqueue(db)==0
    assert worker.run(db,workers=2)==0
    m=v119_research.METHODS[0]
    storage.approve(db,m.family,'explicit-reviewer-for-test-only')
    assert storage.enqueue(db)==1
    assert worker.run(db,workers=2)==1
    questions=storage.read_questions(db,m.topic)
    assert len(questions)==10


def test_v119_operations_register_all_without_publishing(tmp_path):
    state=once(tmp_path)
    assert state['registered_v119_blueprints']==30
    assert state['status']['archetypes']==770
    assert state['status']['pending_review_archetypes']==770
    assert state['jobs_enqueued_this_cycle']==0
    again=once(tmp_path)
    assert again['status']['archetypes']==770


def test_v119_rejects_unknown_family_and_outside_ordinals():
    with pytest.raises(ValueError):v119_research.generate('v119_imaginary',0)
    with pytest.raises(ValueError):v119_research.generate(v119_research.METHODS[0].family,10)
