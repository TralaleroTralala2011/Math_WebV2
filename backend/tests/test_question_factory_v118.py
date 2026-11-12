from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
import pytest
from question_factory.v118_research import METHODS, generate, verify
from question_factory import engine, storage, worker
from question_factory.bootstrap import initialize_factory
from question_factory.operations import once


def test_38_v118_candidates_generate_ten_distinct_input_cases_with_oracle():
    assert len(METHODS)==38
    assert Counter(m.grade for m in METHODS)=={10:12,11:12,12:14}
    allstems=set();formats=Counter()
    catalog=json.loads((Path(__file__).resolve().parents[1]/'question_factory/catalog_150.json').read_text(encoding='utf8'))
    idx={r['id']:r for r in catalog}
    for method in METHODS:
        assert idx[method.topic]['grade']==method.grade
        params=set()
        for ordinal in range(10):
            question=engine.generate(method.family,ordinal,method.difficulty,seed_key='course')
            ok,evidence=engine.independently_verify(question)
            assert ok,(method.family,ordinal,evidence)
            assert question['method_review_status']=='pending-expert-review'
            assert question['independence_certified'] is False
            assert question['topic_id']==method.topic
            assert question['stem'] not in allstems
            allstems.add(question['stem'])
            serialized=json.dumps(question['params'],sort_keys=True,ensure_ascii=False)
            assert serialized not in params,(method.family,ordinal)
            params.add(serialized)
            formats[question['question_type']]+=1
        assert len(params)==10
    assert len(allstems)==380
    assert formats['tra_loi_ngan']==76
    assert formats['trac_nghiem']==76
    assert formats['dung_sai']==76
    assert formats['tu_luan_ngan']==76
    assert formats['toan_thuc_te']>0


def test_v118_invariant_tampering_is_rejected():
    for method in METHODS:
        baseline=generate(method.family,1,method.difficulty)
        for patch in [{'answer':'999999'},{'numeric_result':'999999'},
                      {'solution':'nonsense'},{'stem':'nonsense'},
                      {'params':{'a':100000}},{'correct_index':33}]:
            assert not verify({**baseline,**patch})[0],(method.family,patch)


def test_v118_mcq_has_distinct_choices_and_truth_value_matches():
    for method in METHODS:
        for i in (1,2,6,7):
            q=generate(method.family,i,method.difficulty)
            if q['question_type']=='trac_nghiem':
                assert len(q['options'])==len(set(q['options']))==4
                assert q['options'][q['correct_index']]==q['answer']
            else:
                assert q['question_type']=='dung_sai'
                assert q['truth']==(i==2)
                assert q['answer']==('Đúng' if q['truth'] else 'Sai')


def test_v118_registration_idempotent_and_review_lock(tmp_path):
    path=initialize_factory(str(tmp_path/'factory.sqlite3'))
    for loader,expected in [(storage.seed_curated,60),(storage.seed_v114,105),
                            (storage.seed_v116,31),(storage.seed_v117,56),(storage.seed_v118,38)]:
        assert loader(path)==expected
        assert loader(path)==expected
    status=storage.progress(path)
    assert status['topics']==150
    assert status['archetypes']==290
    assert status['approved_archetypes']==0
    assert status['pending_review_archetypes']==290
    assert storage.enqueue(path)==0
    assert worker.run(path,workers=2)==0
    storage.approve(path,METHODS[0].family,'explicit-reviewer-test')
    assert storage.enqueue(path)==1
    assert worker.run(path,workers=2)==1
    assert len(storage.read_questions(path,METHODS[0].topic))==10


def test_v118_operations_keep_candidates_pending(tmp_path):
    res=once(tmp_path)
    assert res['registered_v118_blueprints']==38
    assert res['jobs_enqueued_this_cycle']==0
    assert res['status']['archetypes']==770
    assert res['status']['pending_review_archetypes']==770
