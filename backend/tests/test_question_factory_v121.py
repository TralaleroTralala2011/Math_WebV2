"""V121 coverage and guarded Question Factory registration tests."""
import json
from collections import Counter
from pathlib import Path
from question_factory import engine, storage, worker, v121_research
from question_factory.bootstrap import initialize_factory
from question_factory.operations import once


def test_v121_exactly_two_candidate_types_each_official_topic():
    cat=json.loads(Path(v121_research.__file__).with_name('catalog_150.json').read_text(encoding='utf8'))
    assert len(cat)==150 and len(v121_research.METHODS)==300
    assert Counter(m.topic for m in v121_research.METHODS)=={t['id']:2 for t in cat}
    assert len({m.family for m in v121_research.METHODS})==300
    assert all(m.grade in (10,11,12) for m in v121_research.METHODS)


def test_v121_all_3000_arithmetic_and_structural_checks():
    seen=set()
    for m in v121_research.METHODS:
        keys=set()
        for i in range(10):
            q=engine.generate(m.family,i,m.difficulty,seed_key='v121-test')
            valid,why=engine.independently_verify(q)
            assert valid,(m.family,i,why)
            assert q['topic_id']==m.topic
            assert q['independence_certified'] is False
            assert q['method_review_status']=='pending-expert-review'
            assert q['stem'] not in seen,(m.family,i)
            seen.add(q['stem'])
            keys.add(json.dumps(q['params'],sort_keys=True))
            assert len(q['solution'])>100
            if q['question_type']=='trac_nghiem':
                assert len(q['options'])==4 and len(set(q['options']))==4
            if q['question_type']=='dung_sai':
                assert q['answer'] in ('Đúng','Sai')
        assert len(keys)==10
    assert len(seen)==3000


def test_v121_tamper_detection():
    for m in v121_research.METHODS[::13]:
        q=v121_research.generate(m.family,2)
        for invalid in ({'answer':q['answer']+'-TAMPER'}, {'stem':'Đề khác'}, {'solution':'0'},
                        {'params':{'a':1}}, {'numeric_result':q['numeric_result']+'-TAMPER'}):
            assert not engine.independently_verify({**q,**invalid})[0]


def test_v121_register_twice_publishes_nothing(tmp_path):
    db=initialize_factory(str(tmp_path/'factory.sqlite3'))
    assert storage.seed_v121(db)==300
    assert storage.seed_v121(db)==300
    s=storage.progress(db)
    assert s['topics']==150 and s['archetypes']==300
    assert s['pending_review_archetypes']==300
    assert s['approved_archetypes']==0
    assert storage.enqueue(db)==0
    assert worker.run(db,workers=2)==0


def test_v121_approved_sample_uses_worker_and_one_time_review(tmp_path):
    db=initialize_factory(str(tmp_path/'factory.sqlite3'))
    storage.seed_v121(db)
    m=v121_research.METHODS[0]
    storage.approve(db,m.family,'test-only-reviewer')
    assert storage.enqueue(db)==1
    assert worker.run(db,workers=2)==1
    qs=storage.read_questions(db,m.topic)
    assert len(qs)==10


def test_v121_operations_idempotent(tmp_path):
    a=once(tmp_path)
    assert a['registered_v121_blueprints']==300
    assert a['status']['topics']==150
    assert a['status']['archetypes']==770
    assert a['status']['approved_archetypes']==0
    assert a['jobs_enqueued_this_cycle']==0
    b=once(tmp_path)
    assert b['status']['archetypes']==770
