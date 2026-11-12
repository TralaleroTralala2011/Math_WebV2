"""V113 regression tests: mathematical verification, novel candidate staging,
safety of symbolic grading, 150-topic coverage, and worker isolation.
"""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from question_factory import engine,storage,worker
from question_factory.bootstrap import initialize_factory
from question_factory.expanded_catalog import BLUEPRINTS, CONCEPT_COLLISIONS
from question_factory.export_curated import export
from question_factory.audit_corpus import audit,normalize_signature
from question_factory.grading import answers_equivalent,parse_numeric_expression,GradingSyntaxError


def test_curated_600_candidates_are_reproducible_math_verified_and_not_stem_duplicates():
    assert len(BLUEPRINTS)==60
    seen=set()
    for family,topic,name,signature,difficulty in BLUEPRINTS:
        assert name and signature and topic
        for n in range(10):
            key=f'{topic}:v113-{family}'
            q=engine.generate(family,n,difficulty,seed_key=key)
            assert q==engine.generate(family,n,difficulty,seed_key=key)
            good,reason=engine.independently_verify(q)
            assert good,(family,n,reason)
            assert q['fingerprint'] not in seen,(family,n)
            seen.add(q['fingerprint'])
            bad=dict(q,answer='99999999999')
            assert engine.independently_verify(bad)[0] is False
    assert len(seen)==600


def test_curated_multiseed_math_validity_including_1000_alternative_examples():
    for family,topic,name,signature,difficulty in BLUEPRINTS:
        for n in range(10):
            q=engine.generate(family,n,difficulty,seed_key=f'other-fixture-{topic}')
            assert engine.independently_verify(q)[0],(family,n,q)


def test_new_types_are_quarantined_until_review(tmp_path):
    db=initialize_factory(str(tmp_path/'v113.sqlite3'))
    assert storage.seed_curated(db)==60
    assert storage.seed_curated(db)==60
    state=storage.progress(db)
    assert state['topics']==150 and state['archetypes']==60
    assert state['pending_review_archetypes']==60
    assert state['approved_archetypes']==0
    assert storage.enqueue(db)==0
    assert worker.run(db,workers=4)==0
    assert state['verified_questions']==0
    # After a reviewer approves one method, it can produce 10 checked questions.
    storage.approve(db,'v113-circle_area','curriculum-reviewer')
    assert storage.enqueue(db)==1
    assert worker.run(db,workers=4)==1
    assert storage.progress(db)['verified_questions']==10
    assert len(storage.read_questions(db,'duong_tron'))==10
    assert storage.read_questions(db,'tap_hop')==[]


def test_curated_export_contains_600_checked_not_approved(tmp_path):
    summary=export(tmp_path/'q.jsonl')
    assert summary['question_count']==600
    assert summary['topics_touched']==55
    assert summary['methods_independence_certified']==0
    assert summary['human_approved_to_publish']==0
    rows=(tmp_path/'q.jsonl').read_text(encoding='utf-8').splitlines()
    assert len(rows)==600
    assert all(json.loads(row)['method_review_status']=='pending-expert-review' for row in rows)


def test_number_normalized_signature_catches_numeric_variant_name_changes():
    assert normalize_signature('V41 | ap | distinct requested mathematical operation 1')==normalize_signature('V99 | ap | distinct requested mathematical operation 2')
    assert normalize_signature('Định lý Viète / bộ 23')==normalize_signature('Định lý Viète / bộ 27')
    assert len({CONCEPT_COLLISIONS.get(x[0],x[0]) for x in BLUEPRINTS})<len(BLUEPRINTS)


def test_safe_symbolic_grading_and_vietnamese_decimal_notation():
    for expected,actual in [('25*pi','25π'),('sqrt(8)','2√(2)'),('1/2','0,5'),('16*pi/3','(16/3)*π'),('sqrt(2)','√(2)')]:
        assert answers_equivalent(expected,actual)[0],(expected,actual)
    for expected,actual in [('pi','3.14'),('2','3'),('sqrt(8)','sqrt(9)')]:
        assert answers_equivalent(expected,actual)[0] is False
    for malicious in ["__import__('os').system('ls')",'9**9999999999999','sqrt(-1)','1/0','2**9999','lambda:0']:
        with pytest.raises(GradingSyntaxError):parse_numeric_expression(malicious)


def test_streaming_audit_does_not_certify_raw_signatures(tmp_path):
    source=tmp_path/'raw.jsonl'
    base={'grade':10,'topic':'Tập hợp và các phép toán','answer':'5','solution':'Áp dụng nguyên tắc đếm; kết quả bằng 5.'}
    rows=[]
    for i in range(10):
        rows.append(dict(base,form_signature=f'V{i} numerically varied family {i}',
                         question=f'Đề toán số {i} khác số liệu {i*i}'))
    source.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in rows),encoding='utf-8')
    report=audit(source,tmp_path/'output')
    assert report['parsed_question_rows']==10
    assert report['exact_signature_groups']==10
    assert report['coarse_numeric_normalized_groups']==1
    assert len(report['coverage'])==150
    assert all(row['independent_methods_certified']==0 for row in report['coverage'])
