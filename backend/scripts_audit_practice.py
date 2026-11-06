"""Conservative audit of the MATH_WEB practice bank.

Counts only explicitly catalogued problem types. Numeric substitutions are NOT
accepted as evidence of distinct mathematical types; human review is required.
Run from backend: python scripts_audit_practice.py --output audit_practice.json
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET_TYPES = 2000
TARGET_QUESTIONS_PER_TYPE = 10

def load(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None

def audit():
    superbank = load('app/ai/knowledge/super_bank_catalog.json') or {}
    problem = load('app/ai/knowledge/problem_bank_catalog.json') or {}
    groups = superbank.get('groups', {})
    group_counts = {k: len(v.get('archetypes', [])) if isinstance(v, dict) else len(v) if isinstance(v, list) else 0 for k, v in groups.items()}
    topic_groups = superbank.get('topic_groups', {})
    declared = set()
    for group in groups.values():
        if isinstance(group, list):
            for item in group:
                if isinstance(item, dict) and item.get('id'):
                    declared.add(str(item['id']))
        elif isinstance(group, dict):
            declared.update(str(x) for x in group.get('archetypes', []) if isinstance(x, str))
    other = {str(a.get('id')) for a in problem.get('archetypes', []) if isinstance(a, dict) and a.get('id')}
    return {
        'target': {'topics': 150, 'distinct_types_per_topic': TARGET_TYPES,
                   'questions_per_type': TARGET_QUESTIONS_PER_TYPE,
                   'total_distinct_types': 300000, 'total_questions': 3000000},
        'catalogue_inventory': {'superbank_declared_type_ids': len(declared),
                                'problem_bank_declared_type_ids': len(other),
                                'superbank_group_sizes': group_counts,
                                'topic_group_entries': len(topic_groups)},
        'verified_distinct_types_per_topic': None,
        'verified_unique_questions_per_type': None,
        'verified_solution_correctness': None,
        'meets_target': False,
        'limitations': [
            'Catalogued archetypes are not proof of distinct mathematical problem types.',
            'This audit does not count dynamically generated question variants.',
            'A separate mathematical equivalence and solution review is required.',
            'No 100% completion claim is supported by this inventory.'
        ]
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='audit_practice.json')
    args = parser.parse_args()
    result = audit()
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
