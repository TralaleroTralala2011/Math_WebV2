"""Strict coverage gate for the 2,000 genuinely different types × 10 items requirement.

Usage: python scripts/audit_2000_types.py BANK.jsonl --output coverage_report.json
Each row must declare topic_id, type_id, skill_id, reviewed_topic_id,\ntopic_alignment_reviewed=true, question, answer, solution and
structure_signature. A structure signature must encode the mathematical method,
not coefficients. Human review of mathematical distinctness is still required.
This program never generates or certifies mathematical correctness.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

MIN_TYPES = 2000
MIN_QUESTIONS = 10


def normalized(value):
    return re.sub(r'\s+', ' ', str(value).strip().casefold())


def audit(rows, topic_ids):
    errors = []
    groups = collections.defaultdict(list)
    signatures = collections.defaultdict(set)
    global_questions = {}
    type_ownership = collections.defaultdict(set)
    topic_mismatch_count = collections.Counter()
    unreviewed_count = collections.Counter()
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            errors.append(f'row {number}: not an object')
            continue
        fields = ('topic_id', 'type_id', 'question', 'answer', 'solution', 'structure_signature')
        missing = [field for field in fields if not normalized(row.get(field, ''))]
        if missing:
            errors.append(f'row {number}: missing {", ".join(missing)}')
            continue
        topic, kind = str(row['topic_id']), str(row['type_id'])
        if topic not in topic_ids:
            errors.append(f'row {number}: unknown topic {topic}')
            continue
        # Each submitted type must have an explicit topic-specific skill,
        # independently reviewed against the curriculum catalog.
        skill = normalized(row.get('skill_id', ''))
        reviewed = row.get('topic_alignment_reviewed') is True
        if not skill:
            errors.append(f'row {number}: missing skill_id (curriculum alignment)')
            topic_mismatch_count[topic] += 1
        if not reviewed:
            errors.append(f'row {number}: topic alignment not reviewed')
            unreviewed_count[topic] += 1
        if normalized(row.get('reviewed_topic_id', '')) != normalized(topic):
            errors.append(f'row {number}: reviewed_topic_id does not match topic_id')
            topic_mismatch_count[topic] += 1
        type_ownership[(kind, normalized(row['structure_signature']))].add(topic)
        key = (topic, kind)
        groups[key].append(row)
        signatures[topic].add((kind, normalized(row['structure_signature'])))
        fingerprint = hashlib.sha256(normalized(row['question']).encode()).hexdigest()
        if fingerprint in global_questions:
            errors.append(f'row {number}: identical question to row {global_questions[fingerprint]}')
        else:
            global_questions[fingerprint] = number
    report = {}
    for topic in topic_ids:
        kinds = {kind: group for (t, kind), group in groups.items() if t == topic}
        # Same signature used for multiple type IDs is a collision, not a new type.
        signature_to_kinds = collections.defaultdict(set)
        for kind, group in kinds.items():
            signature_to_kinds[normalized(group[0]['structure_signature'])].add(kind)
            if len({normalized(r['structure_signature']) for r in group}) != 1:
                errors.append(f'{topic}/{kind}: inconsistent structure signatures')
        collisions = [sorted(ids) for ids in signature_to_kinds.values() if len(ids) > 1]
        for ids in collisions:
            errors.append(f'{topic}: duplicated structure signature across type IDs: {ids[:5]}')
        eligible = 0
        for kind, group in kinds.items():
            distinct = len({normalized(r['question']) for r in group})
            if distinct >= MIN_QUESTIONS and len({normalized(r['structure_signature']) for r in group}) == 1:
                eligible += 1
        total = sum(len(g) for g in kinds.values())
        report[topic] = {
            'topic_alignment_mismatches': topic_mismatch_count[topic],
            'unreviewed_questions': unreviewed_count[topic],
            'topic_alignment_gate_passed': topic_mismatch_count[topic] == 0 and unreviewed_count[topic] == 0 and total > 0,
            'declared_types': len(kinds), 'types_with_10_distinct_questions': eligible,
            'questions': total, 'type_target': MIN_TYPES,
            'question_target': MIN_TYPES * MIN_QUESTIONS,
            'quantity_gate_passed': eligible >= MIN_TYPES and not collisions,
            'mathematical_correctness_verified': False,
            'semantic_distinctness_human_verified': False,
        }
    # Reusing the exact same type ID + mathematical structure in different
    # topics is suspicious and must be explicitly reviewed, not counted.
    for (kind, signature), owners in type_ownership.items():
        if len(owners) > 1:
            errors.append(f'cross-topic type collision {kind}: {sorted(owners)[:8]}')
    for topic in report:
        report[topic]['quantity_gate_passed'] = (
            report[topic]['quantity_gate_passed']
            and report[topic]['topic_alignment_gate_passed']
        )
    return {'topic_count': len(topic_ids), 'total_questions': sum(len(g) for g in groups.values()),
            'total_declared_types': len(groups), 'topics_meeting_quantity_gate': sum(v['quantity_gate_passed'] for v in report.values()),
            'all_requirements_certified': False, 'errors': errors[:500], 'error_count': len(errors), 'topics': report}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bank', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    catalog = json.loads((root/'MATHWEB_KNOWLEDGE_LIBRARY/topic_coverage_catalog.json').read_text(encoding='utf-8'))
    topic_ids = [item['id'] for item in catalog['topics']]
    with args.bank.open(encoding='utf-8') as handle:
        if args.bank.suffix == '.jsonl':
            rows = [json.loads(line) for line in handle if line.strip()]
        else:
            data = json.load(handle)
            rows = data['questions'] if isinstance(data, dict) else data
    result = audit(rows, topic_ids)
    result_text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(result_text, encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'topics'}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['topics_meeting_quantity_gate'] == len(topic_ids) and not result['errors'] else 1)


if __name__ == '__main__':
    main()
