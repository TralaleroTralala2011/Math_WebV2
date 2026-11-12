"""V182: explicit bank schema, form grouping, and true/false grading regression."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.ai.engine.service import AIQuestionService
from app.questions.answer_checker import grade_answer
from scripts.import_bank_updates import load_and_validate


def test_v182_all_150_topics_have_import_ready_questions():
    coverage = json.loads((ROOT / 'bank_updates/V182_150_TOPIC_COVERAGE.json').read_text(encoding='utf-8'))
    assert len(coverage) == 150
    assert len({(x['grade'], x['topic']) for x in coverage}) == 150
    assert all(x['total_import_ready_if_both_imported'] > 0 for x in coverage)
    assert sum(x['v182_new_qa_checked'] for x in coverage) == 1660


def test_v182_83_families_20_questions_each_and_ratios():
    rows = load_and_validate(ROOT / 'bank_updates/V182_IMPORT_READY.jsonl')
    assert len(rows) == 1660
    counts = Counter(r['family'] for r in rows)
    assert len(counts) == 83 and set(counts.values()) == {20}
    types = Counter(r['question_type'] for r in rows)
    assert types == {'multiple_choice':1106,'short_answer':388,'true_false':166}
    assert all(not r['method_independence_certified'] and not r['production_integrated'] for r in rows)


def test_v182_true_false_accepts_text_or_boolean_array():
    item = {'id': 123, 'question_type': 'true_false', 'question': 'Cho x=2. Xét bốn mệnh đề.',
            'correct_answer': 'Đúng,Sai,Đúng,Sai',
            'choices': ['x=2', 'x=3', '2x=4', 'x=4'],
            'tags_json': json.dumps(['V182','form:v182_numeric_truth'])}
    service = AIQuestionService()
    q = service._build_curated_question(item, 10, 'menh_de', 'medium', 'true_false')
    assert q['archetype'] == 'admin_form_v182_numeric_truth'
    assert service._check(q, 'Đúng,Sai,Đúng,Sai')
    assert service._check(q, [True,False,True,False])
    assert service._check(q, ['Đúng','Sai','Đúng','Sai'])
    assert not service._check(q, ['Sai']*4)


def test_v182_form_tags_group_numerical_variants():
    service = AIQuestionService()
    common = {'question_type':'multiple_choice', 'choices':['1','2','3','4'],
              'correct_answer':'2','tags_json':json.dumps(['V182','form:v182_family'])}
    a = service._build_curated_question({'id':101,'question':'Tính 1+1.',**common},10,'menh_de','easy','multiple_choice')
    b = service._build_curated_question({'id':102,'question':'Tính 2+0.',**common},10,'menh_de','easy','multiple_choice')
    assert a['archetype'] == b['archetype'] == 'admin_form_v182_family'


def test_v182_no_false_certification_claim():
    report = json.loads((ROOT / 'bank_updates/V182_REPORT.json').read_text(encoding='utf-8'))
    assert report['form_independence_certified'] == 0
    assert report['production_integrated'] == 0
