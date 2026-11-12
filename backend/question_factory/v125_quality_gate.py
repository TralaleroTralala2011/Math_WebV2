"""Conservative V125 release gate. Never promotes pending forms to certified."""
import json
import re
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


def canonical_stem(s):
    return re.sub(r'\s+', ' ', str(s).casefold()).strip()


def audit(candidate_file, question_file):
    with Path(candidate_file).open(encoding='utf-8') as f:
        candidates = [json.loads(s) for s in f if s.strip()]
    with Path(question_file).open(encoding='utf-8') as f:
        questions = [json.loads(s) for s in f if s.strip()]
    family = Counter(q.get('family') for q in questions)
    candidate_family = Counter(c.get('family') for c in candidates)
    source = defaultdict(set)
    for c in candidates:
        source[c.get('source_family')].add(c.get('family'))
    stems = Counter(canonical_stem(q.get('stem','')) for q in questions)
    fingerprints = Counter(q.get('fingerprint') for q in questions if q.get('fingerprint'))
    discrepancies = Counter()
    for c in candidates:
        if c.get('published') is not False or c.get('independence_certified') is not False:
            discrepancies['candidate_publication_or_certification'] += 1
        if not c.get('source_family'):
            discrepancies['missing_source_family'] += 1
    for q in questions:
        if q.get('family') not in candidate_family:
            discrepancies['orphan_question'] += 1
        if not str(q.get('stem','')).strip() or not str(q.get('solution','')).strip():
            discrepancies['missing_stem_or_solution'] += 1
        if not str(q.get('answer','')).strip():
            discrepancies['missing_answer'] += 1
        if str(q.get('answer','')).strip() != str(q.get('numeric_result','')).strip():
            # Some question formats can encode answer differently: flag, do not auto-reject.
            discrepancies['answer_numeric_mismatch_review'] += 1
        if q.get('independence_certified') is not False:
            discrepancies['question_certification_not_false'] += 1
    discrepancies['duplicate_candidate_ids'] = sum(v-1 for v in candidate_family.values() if v>1)
    discrepancies['wrong_question_count'] = sum(v!=10 for v in family.values()) + sum(k not in family for k in candidate_family)
    discrepancies['duplicate_normalized_stems'] = sum(v-1 for v in stems.values() if v>1)
    discrepancies['duplicate_fingerprints'] = sum(v-1 for v in fingerprints.values() if v>1)
    blockers = ['candidate_publication_or_certification','missing_source_family','orphan_question','missing_stem_or_solution','missing_answer','question_certification_not_false','duplicate_candidate_ids','wrong_question_count','duplicate_normalized_stems','duplicate_fingerprints']
    return {'version':'V125','candidates':len(candidates),'questions':len(questions),
            'topics':len(set(c.get('topic') for c in candidates)),
            'source_method_clusters':len(source),
            'shared_core_clusters':sum(len(v)>1 for v in source.values()),
            'certified_new_independent_types':0,
            'discrepancies':dict(discrepancies),
            'structural_gate_pass':not any(discrepancies[k] for k in blockers),
            'mathematical_independence_gate_pass':False,
            'note':'Structural checks do not independently prove mathematical answers or method novelty.'}

if __name__=='__main__':
    import sys
    print(json.dumps(audit(sys.argv[1],sys.argv[2]),ensure_ascii=False,indent=2))
