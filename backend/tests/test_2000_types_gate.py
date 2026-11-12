import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[2] / 'scripts' / 'audit_2000_types.py'
spec = importlib.util.spec_from_file_location('audit_2000_types', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def make(kind, question, signature='concept A'):
    return dict(topic_id='topic1', type_id=kind, question=question,
                skill_id='tested_concept_A', reviewed_topic_id='topic1',
                topic_alignment_reviewed=True, answer='2',
                solution='Verified separately', structure_signature=signature)


def test_rejects_numeric_substitution_as_new_type():
    rows = [make('type1', f'Question {i}') for i in range(10)]
    rows += [make('type2', f'Other {i}') for i in range(10)]
    result = module.audit(rows, ['topic1'])
    assert not result['topics']['topic1']['quantity_gate_passed']
    assert any('duplicated structure' in e for e in result['errors'])


def test_requires_ten_unique_questions():
    rows = [make('type1', f'Question {i % 9}') for i in range(10)]
    result = module.audit(rows, ['topic1'])
    assert result['topics']['topic1']['types_with_10_distinct_questions'] == 0
    assert result['error_count'] == 1


def test_rejects_unknown_topic():
    result = module.audit([make('type1', 'Question')], ['different'])
    assert result['error_count'] == 1
