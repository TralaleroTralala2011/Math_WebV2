"""Conservative candidate-method collision audit. Does not certify novelty."""
import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


def norm(value):
    value = unicodedata.normalize('NFKC', str(value or '')).casefold()
    return ' '.join(re.findall(r'\w+', value, flags=re.UNICODE))


def audit(root):
    files = sorted(root.glob('V*_RESEARCH/*CANDIDATE*jsonl'))
    records = []
    invalid = []
    for path in files:
        with path.open(encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    invalid.append({'file': str(path.relative_to(root)), 'line': line_number, 'error': str(e)})
                    continue
                if not isinstance(item, dict):
                    invalid.append({'file': str(path.relative_to(root)), 'line': line_number, 'error': 'not an object'})
                    continue
                if item.get('independence_certified') is True or item.get('published') is True:
                    invalid.append({'file': str(path.relative_to(root)), 'line': line_number, 'error': 'candidate marked certified or published'})
                method = norm(item.get('solving_method') or item.get('method') or item.get('method_description') or item.get('skill') or item.get('signature'))
                title = norm(item.get('title') or item.get('objective') or item.get('name'))
                topic = norm(item.get('topic') or item.get('topic_id'))
                records.append({'file': str(path.relative_to(root)), 'line': line_number,
                                'id': item.get('method_id') or item.get('form_id') or item.get('id') or item.get('signature'),
                                'identity_source': next((k for k in ('method_id', 'form_id', 'id', 'signature') if str(item.get(k) or '').strip()), None),
                                'shared_core_method': item.get('shared_core_method') is True,
                                'topic': topic, 'method': method, 'title': title})
    id_groups = defaultdict(list)
    for item in records:
        if not item['topic'] or not item['method']:
            invalid.append({'file': item['file'], 'line': item['line'], 'error': 'missing topic or solving method'})
        if item['id'] is not None and str(item['id']).strip():
            id_groups[str(item['id']).strip()].append(item)
    duplicate_ids = [v for v in id_groups.values() if len(v) > 1]
    groups = defaultdict(list)
    for item in records:
        if item['topic'] and item['method']:
            groups[(item['topic'], item['method'])].append(item)
    collisions = [v for v in groups.values() if len(v) > 1]
    return {'candidate_files': len(files), 'candidate_records': len(records),
            'records_with_method_and_topic': sum(bool(x['topic'] and x['method']) for x in records),
            'exact_topic_method_collision_groups': len(collisions),
            'exact_topic_method_collisions': collisions[:100],
            'duplicate_candidate_id_groups': len(duplicate_ids),
            'duplicate_candidate_ids': duplicate_ids[:100],
            'missing_candidate_ids': sum(not str(x['id'] or '').strip() for x in records),
            'identity_source_counts': {key: sum(x['identity_source'] == key for x in records) for key in ('method_id','form_id','id','signature')},
            'shared_core_method_candidates': sum(x['shared_core_method'] for x in records),
            'shared_core_method_examples': [x for x in records if x['shared_core_method']][:20],
            'invalid_or_unsafe_count': len(invalid),
            'invalid_or_unsafe': invalid[:100],
            'limitation': 'Exact normalized method labels only. Not semantic equivalence; no independent forms certified.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('exact_topic_method_collisions','duplicate_candidate_ids','invalid_or_unsafe','shared_core_method_examples')}, ensure_ascii=False, indent=2))
    if result['invalid_or_unsafe']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
