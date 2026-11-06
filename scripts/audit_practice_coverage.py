"""Strict, conservative coverage report for an exported JSONL question bank.

Usage: python scripts/audit_practice_coverage.py bank.jsonl --topics topics.json --output coverage.json
The optional topics file is a JSON list of topic IDs (or objects with `id`).
This tool does not invent questions or certify mathematical/semantic correctness.
"""
import argparse
import collections
import json
import re
from pathlib import Path


def normalize(value):
    return re.sub(r'\s+', ' ', str(value if value is not None else '').strip()).casefold()


def read_lines(path):
    with Path(path).open(encoding="utf-8") as stream:
        yield from enumerate(stream, 1)


def inspect(bank, topic_ids=None, min_types=2000, min_questions=10):
    groups = collections.defaultdict(lambda: {'questions': set(), 'signatures': set(), 'rows': 0, 'invalid': 0})
    seen = set()
    question_owners = collections.defaultdict(set)
    signature_owners = collections.defaultdict(set)
    counters = collections.Counter()
    for line_no, line in read_lines(bank):
        if not line.strip():
            continue
        counters['rows'] += 1
        try:
            item = json.loads(line)
        except (ValueError, TypeError):
            counters['invalid_json'] += 1
            continue
        if not isinstance(item, dict):
            counters['invalid_json'] += 1
            continue
        topic, kind = normalize(item.get('topic_id')), normalize(item.get('type_id'))
        question, signature = normalize(item.get('question')), normalize(item.get('structure_signature'))
        if not all((topic, kind, question, signature, normalize(item.get('answer')), normalize(item.get('solution')))):
            counters['missing_required'] += 1
            if topic and kind:
                groups[(topic, kind)]['invalid'] += 1
            continue
        g = groups[(topic, kind)]
        g['rows'] += 1
        g['signatures'].add(signature)
        question_owners[question].add((topic, kind))
        signature_owners[(topic, signature)].add(kind)
        # Count only textually unique questions within a type, not repeated exports.
        if question in g['questions']:
            counters['duplicate_within_type'] += 1
        g['questions'].add(question)
        if question in seen:
            counters['duplicate_globally'] += 1
        seen.add(question)
        if not (item.get('answer_reviewed') is True and item.get('solution_reviewed') is True
                and item.get('topic_alignment_reviewed') is True
                and normalize(item.get('reviewed_topic_id')) == topic):
            g['invalid'] += 1
            counters['unreviewed'] += 1
        if normalize(item.get('solution')) == normalize(item.get('answer')):
            g['invalid'] += 1
            counters['solution_repeats_answer'] += 1
    # A question reused under another type cannot certify either type.
    # A signature reused by multiple type IDs within a topic is not evidence of independent types.
    for owners in question_owners.values():
        if len(owners) > 1:
            counters['cross_type_duplicate_questions'] += 1
            for owner in owners:
                groups[owner]['invalid'] += 1
    for owners in signature_owners.values():
        if len(owners) > 1:
            counters['shared_structure_signatures'] += 1
    for (topic, signature), owners in signature_owners.items():
        if len(owners) > 1:
            for kind in owners:
                groups[(topic, kind)]['invalid'] += 1
    expected = set(normalize(t.get('id') if isinstance(t, dict) else t) for t in (topic_ids or []))
    expected.discard('')
    actual = {topic for topic, _ in groups}
    if not expected:
        expected = actual
    by_topic = {}
    for topic in sorted(expected | actual):
        topic_groups = [g for (t, _), g in groups.items() if t == topic]
        complete = sum(len(g['questions']) >= min_questions and len(g['signatures']) == 1 and not g['invalid'] for g in topic_groups)
        by_topic[topic] = {'declared_types': len(topic_groups), 'metadata_qualified_types': complete,
                           'missing_qualified_types': max(0, min_types - complete),
                           'meets_metadata_target': complete >= min_types,
                           'listed_in_expected_topics': topic in expected}
    return {'requirements': {'types_per_topic': min_types, 'questions_per_type': min_questions},
            'counts': dict(counters), 'expected_topics': len(expected), 'observed_topics': len(actual),
            'metadata_qualified_topics': sum(v['meets_metadata_target'] for t, v in by_topic.items() if t in expected),
            'topics': by_topic, 'mathematical_correctness_verified': False,
            'distinct_mathematical_types_verified': False,
            'warning': 'Metadata-qualified is not mathematically certified. Manual or independent semantic/math verification is required.'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('bank', type=Path)
    p.add_argument('--topics', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--min-types', type=int, default=2000)
    p.add_argument('--min-questions', type=int, default=10)
    a = p.parse_args()
    topics = json.loads(a.topics.read_text(encoding='utf-8')) if a.topics else None
    report = inspect(a.bank, topics, a.min_types, a.min_questions)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if a.output:
        a.output.write_text(output, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
