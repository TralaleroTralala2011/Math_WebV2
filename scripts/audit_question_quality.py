"""Conservative question-bank quality audit, no claim of mathematical proof.

Run: python scripts/audit_question_quality.py bank.jsonl --output quality.json
Requires one JSON object per line. Does not alter the running website.
"""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

REQUIRED = ('topic_id', 'type_id', 'skill_id', 'structure_signature', 'question', 'answer', 'solution')

def norm(v):
    return re.sub(r'\s+', ' ', str(v or '').strip()).casefold()

def audit(path):
    types = collections.defaultdict(lambda: {'questions': set(), 'signatures': set(), 'issues': collections.Counter()})
    seen_questions = {}
    issues = collections.Counter()
    examples = []
    total = 0
    with Path(path).open(encoding='utf-8') as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            total += 1
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError('not an object')
            except (ValueError, TypeError) as exc:
                issues['invalid_json_row'] += 1
                if len(examples) < 100: examples.append({'line': line_no, 'issue': 'invalid_json_row', 'detail': str(exc)})
                continue
            missing = [k for k in REQUIRED if not norm(row.get(k))]
            flags = []
            if missing: flags.append('missing_required_fields')
            if row.get('topic_alignment_reviewed') is not True or norm(row.get('reviewed_topic_id')) != norm(row.get('topic_id')):
                flags.append('topic_alignment_not_verified')
            if row.get('solution_reviewed') is not True:
                flags.append('solution_not_reviewed')
            if row.get('answer_reviewed') is not True:
                flags.append('answer_not_reviewed')
            if norm(row.get('solution')) == norm(row.get('answer')) and norm(row.get('answer')):
                flags.append('solution_only_repeats_answer')
            if len(norm(row.get('solution'))) < 50:
                flags.append('solution_too_short_for_detailed_explanation')
            key = (norm(row.get('topic_id')), norm(row.get('type_id')))
            group = types[key]
            signature = norm(row.get('structure_signature'))
            if signature: group['signatures'].add(signature)
            question = norm(row.get('question'))
            if question:
                digest = hashlib.sha256(question.encode('utf-8')).hexdigest()
                if digest in seen_questions:
                    flags.append('duplicate_question_text')
                else:
                    seen_questions[digest] = line_no
                group['questions'].add(digest)
            if len(group['signatures']) > 1: flags.append('inconsistent_type_signature')
            for flag in set(flags):
                issues[flag] += 1
                group['issues'][flag] += 1
                if len(examples) < 100: examples.append({'line': line_no, 'issue': flag, 'topic': key[0], 'type': key[1]})
    topic_stats = collections.defaultdict(lambda: {'declared_types': 0, 'types_with_10_unique_questions': 0, 'types_passing_metadata_checks': 0})
    for (topic, kind), group in types.items():
        stat = topic_stats[topic]
        stat['declared_types'] += 1
        if len(group['questions']) >= 10 and len(group['signatures']) == 1:
            stat['types_with_10_unique_questions'] += 1
            if not group['issues']: stat['types_passing_metadata_checks'] += 1
    return {
        'total_rows': total, 'declared_types': len(types), 'unique_question_texts': len(seen_questions),
        'issues': dict(issues), 'examples_first_100': examples,
        'topics': dict(sorted(topic_stats.items())),
        'topics_meeting_2000_types_10_questions_metadata_gate': sum(v['types_passing_metadata_checks'] >= 2000 for v in topic_stats.values()),
        'mathematical_correctness_proven': False,
        'semantic_type_distinctness_proven': False,
        'note': 'Review flags are metadata, not mathematical proof. Passing this audit does not certify correctness or genuinely distinct problem types.'
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bank', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.bank)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output: args.output.write_text(output, encoding='utf-8')
    print(output)

if __name__ == '__main__': main()
