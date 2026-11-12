"""Tests for researched V117 candidates and the unchanged review gate."""
from __future__ import annotations
from collections import Counter
import json
import pytest
from question_factory import engine,storage,worker
from question_factory.bootstrap import initialize_factory
from question_factory.v117_research import METHODS, FAMILIES, generate, verify
from question_factory.v117_audit import audit


def test_v117_56_different_methods_ten_verified_questions_each():
    assert len(METHODS)==56 and len(FAMILIES)==56
    assert Counter(m.grade for m in METHODS)=={10:15,11:18,12:23}
    ids=set();fmt=Counter()
    for m in METHODS:
        family_stems=set();base_stems=set()
        for i in range(10):
            r=engine.generate(m.family,i,m.difficulty,seed_key='research')
            valid,evidence=engine.independently_verify(r)
            assert valid,(m.family,i,evidence)
            assert r['method_review_status']=='pending-expert-review'
            assert not r['independence_certified']
            assert r['topic_id']==m.topic
            assert r['fingerprint'] not in ids
            assert r['stem'] not in family_stems
            # The same mathematical inputs must not be used twice just by
            # switching from MCQ to free-response.
            assert str(r['params']) not in base_stems,(m.family,i)
            base_stems.add(str(r['params']))
            ids.add(r['fingerprint']);family_stems.add(r['stem'])
            fmt[r['question_type']]+=1
        assert len(family_stems)==10
    assert len(ids)==560
    assert fmt['tra_loi_ngan']==112 and fmt['trac_nghiem']==112
    assert fmt['dung_sai']==112 and fmt['tu_luan_ngan']==112
    assert fmt['toan_thuc_te']>0


def test_v117_mcq_plausibility_and_true_false():
    for m in METHODS:
        for i in (1,2,6,7):
            q=generate(m.family,i,m.difficulty)
            if q['question_type']=='trac_nghiem':
                assert len(set(q['options']))==4
                assert q['options'][q['correct_index']]==q['answer']
            else:
                assert q['answer'] in {'Đúng','Sai'}
                assert q['truth']==(i==2)


def test_v117_mutated_math_and_text_never_pass():
    for m in METHODS:
        original=generate(m.family,1,m.difficulty)
        for change in ({'answer':'-10000000'},{'stem':'tampered'},
                       {'solution':'tampered'},{'numeric_result':'7/123456'},
                       {'params':{'tampered':1}},{'correct_index':99}):
            assert not verify({**original,**change})[0],(m.family,change)


def test_v117_registry_remains_pending(tmp_path):
    path=initialize_factory(str(tmp_path/'db.sqlite3'))
    assert storage.seed_curated(path)==60
    assert storage.seed_v114(path)==105
    assert storage.seed_v116(path)==31
    assert storage.seed_v117(path)==56
    assert storage.seed_v117(path)==56
    state=storage.progress(path)
    assert state['topics']==150 and state['archetypes']==252
    assert state['pending_review_archetypes']==252
    assert state['approved_archetypes']==0
    assert storage.enqueue(path)==0
    assert worker.run(path,workers=2)==0
    storage.approve(path,METHODS[0].family,'test-reviewer')
    assert storage.enqueue(path)==1
    assert worker.run(path,workers=2)==1
    assert len(storage.read_questions(path,METHODS[0].topic))==10


def test_v117_audit_150_topic_gap(tmp_path):
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    report=audit(root,tmp_path)
    assert report['topics']==150
    assert report['candidate_forms_new']==56
    assert report['candidate_forms_total']==252
    assert report['target_unique_forms']==75000
    assert report['math_method_independence_certified']==0
    assert report['topics_with_at_least_500_candidate_forms']==0
    assert report['candidate_coverage_all_150']
    assert (tmp_path/'V117_150_TOPIC_GAPS.csv').is_file()
