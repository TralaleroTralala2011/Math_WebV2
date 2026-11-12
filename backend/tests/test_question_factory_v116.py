"""V116 candidate question data integrity and publication guard regression tests."""
from __future__ import annotations
from collections import Counter
import json
from question_factory.v116_research import METHODS,FAMILIES,generate,verify,export
from question_factory import engine,storage,worker
from question_factory.bootstrap import initialize_factory


def test_31_new_curriculum_matched_methods_with_10_examples_each():
    assert len(METHODS)==31 and len(FAMILIES)==31
    ids={m.family for m in METHODS}
    assert len(ids)==31
    seen=set(); formats=Counter()
    for m in METHODS:
        family_fps=set()
        for n in range(10):
            q=engine.generate(m.family,n,m.difficulty,seed_key=f'{m.topic}:v116')
            valid,why=engine.independently_verify(q)
            assert valid, (m.family,n,why)
            assert q==engine.generate(m.family,n,m.difficulty,seed_key=f'{m.topic}:v116')
            assert q['fingerprint'] not in seen
            assert q['fingerprint'] not in family_fps
            assert q['method_review_status']=='pending-expert-review'
            assert q['topic_id']==m.topic
            formats[q['question_type']]+=1
            seen.add(q['fingerprint']);family_fps.add(q['fingerprint'])
        assert len(family_fps)==10
    assert len(seen)==310
    assert formats['tra_loi_ngan']==62
    assert formats['trac_nghiem']==62
    assert formats['dung_sai']==62
    assert formats['tu_luan_ngan']==62
    assert formats['toan_thuc_te']>0


def test_tampering_with_new_questions_is_rejected():
    for m in METHODS:
        q=generate(m.family,1,m.difficulty,seed_key=f'{m.topic}:v116')
        for change in ({'stem':'bị sửa'}, {'answer':'1234567890'},
                       {'solution':'bị sửa'}, {'numeric_result':'42'},
                       {'params':{'bad':3}}, {'options':['1','1','1','1']}):
            bad={**q,**change}
            assert not verify(bad)[0],(m.family,change)


def test_v116_registry_and_review_lock(tmp_path):
    path=initialize_factory(str(tmp_path/'qf.sqlite3'))
    assert storage.seed_curated(path)==60
    assert storage.seed_v114(path)==105
    assert storage.seed_v116(path)==31
    assert storage.seed_v116(path)==31
    state=storage.progress(path)
    assert state['topics']==150
    assert state['archetypes']==196
    assert state['approved_archetypes']==0
    assert state['pending_review_archetypes']==196
    assert storage.enqueue(path)==0
    assert worker.run(path,workers=2)==0
    storage.approve(path,'v116_quad_interpolate','human-reviewer-testing')
    assert storage.enqueue(path)==1
    assert worker.run(path,workers=2)==1
    assert len(storage.read_questions(path,'ham_so_bac_hai'))==10


def test_v116_export_and_readable_question_types(tmp_path):
    report=export(tmp_path)
    assert report['new_candidate_methods']==31
    assert report['new_math_checked_questions']==310
    assert report['methods_certified_independent']==0
    rows=[json.loads(x) for x in (tmp_path/'V116_NEW_QUESTIONS_10_EACH.jsonl').read_text().splitlines()]
    assert len(rows)==310
    for r in rows:
        assert r['verification']['independent_method_certified'] is False
        if r['question_type']=='trac_nghiem':
            assert len(set(r['options']))==4
            assert r['options'][r['correct_index']]==r['answer']
        if r['question_type']=='dung_sai':
            assert r['answer'] in ('Đúng','Sai')
