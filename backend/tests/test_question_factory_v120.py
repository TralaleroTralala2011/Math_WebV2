"""V120 150-topic candidate coverage; pending review, never auto-published."""
from collections import Counter
from pathlib import Path
import json
import pytest
from question_factory import engine, storage, worker, v120_research
from question_factory.bootstrap import initialize_factory
from question_factory.operations import once


def test_v120_exactly_one_distinct_family_per_official_topic():
    cat=json.loads(Path(v120_research.__file__).with_name('catalog_150.json').read_text(encoding='utf8'))
    methods=v120_research.METHODS
    assert len(cat)==len(methods)==150
    assert Counter(m.topic for m in methods)=={t['id']:1 for t in cat}
    assert len({m.signature for m in methods})==150
    assert all(m.grade==next(t['grade'] for t in cat if t['id']==m.topic) for m in methods)


def test_v120_generate_1500_distinct_stems_with_ten_per_topic():
    seen=set()
    for m in v120_research.METHODS:
        params=set()
        for i in range(10):
            item=engine.generate(m.family,i,m.difficulty,seed_key='v120-test')
            assert item['topic_id']==m.topic
            assert item['method_review_status']=='pending-expert-review'
            assert not item['independence_certified']
            passed,report=engine.independently_verify(item)
            assert passed,(m.family,i,report)
            assert item['stem'] not in seen
            seen.add(item['stem'])
            params.add(json.dumps(item['params'],sort_keys=True))
            assert len(item['solution'])>=65
            if item['question_type']=='trac_nghiem':
                assert len(item['options'])==4 and len(set(item['options']))==4
            if item['question_type']=='dung_sai':
                assert item['answer'] in ('Đúng','Sai')
        assert len(params)==10
    assert len(seen)==1500


def test_v120_rejects_modification_and_invalid_ordinals():
    for m in v120_research.METHODS:
        q=v120_research.generate(m.family,1)
        for change in ({'answer':'wrong'}, {'stem':'altered'}, {'solution':'altered'},
                       {'params':{'a':100}}, {'correct_index':99}):
            assert not engine.independently_verify({**q,**change})[0]
    with pytest.raises(ValueError):
        engine.generate(v120_research.METHODS[0].family,10,'nền tảng')


def test_v120_db_register_review_gate_and_worker(tmp_path):
    db=initialize_factory(str(tmp_path/'factory.db'))
    assert storage.seed_v120(db)==150
    assert storage.seed_v120(db)==150
    s=storage.progress(db)
    assert s['topics']==150 and s['archetypes']==150 and s['approved_archetypes']==0
    assert storage.enqueue(db)==0
    assert worker.run(db,workers=2)==0
    m=v120_research.METHODS[0]
    storage.approve(db,m.family,'manual-test-reviewer')
    assert storage.enqueue(db)==1
    assert worker.run(db,workers=2)==1
    assert len(storage.read_questions(db,m.topic))==10


def test_v120_operations_register_existing_and_new(tmp_path):
    s=once(tmp_path)
    assert s['registered_v120_blueprints']==150
    assert s['status']['archetypes']==770
    assert s['status']['topics']==150
    assert s['jobs_enqueued_this_cycle']==0
    s2=once(tmp_path)
    assert s2['status']['archetypes']==770
