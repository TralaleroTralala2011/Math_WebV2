"""Read-only, fail-closed integrity gate for V123 research bank; no publication."""
import collections, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMS = ROOT/'V123_RESEARCH/V123_1050_CANDIDATE_OBJECTIVES.jsonl'
QUESTIONS = ROOT/'V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl'

def records(path):
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line.strip(): yield json.loads(line)

def audit(forms, questions):
    forms=list(forms); questions=list(questions)
    families={f['family']:f for f in forms}
    problems=collections.Counter(); counts=collections.Counter(); texts=collections.defaultdict(set)
    fingerprints=collections.defaultdict(set); methods=collections.defaultdict(set)
    for f in forms:
        if f.get('published') is not False or f.get('independence_certified') is not False:
            problems['form_publication_or_certification_violation']+=1
        methods[f['source_family']].add(f['family'])
    for q in questions:
        fam=q.get('family'); counts[fam]+=1
        if fam not in families:
            problems['orphan_question']+=1; continue
        f=families[fam]
        if q.get('topic_id') != f.get('topic'):
            problems['topic_mismatch']+=1
        if q.get('independence_certified') is not False or q.get('verification',{}).get('publication_blocked') is not True:
            problems['unsafe_publication']+=1
        if not all(str(q.get(k,'')).strip() for k in ('stem','answer','solution','question_type','method_signature')):
            problems['missing_essential_field']+=1
        norm=' '.join(q.get('stem','').casefold().split())
        if norm in texts[fam]: problems['repeated_stem_within_family']+=1
        texts[fam].add(norm)
        fingerprint=q.get('fingerprint')
        if fingerprint in fingerprints[fam]:problems['repeated_fingerprint_within_family']+=1
        fingerprints[fam].add(fingerprint)
        if q.get('question_type') not in ('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung'):
            problems['unexpected_question_type']+=1
    for fam in families:
        if counts[fam]!=10:problems['family_not_ten_questions']+=1
    return {'forms':len(forms),'questions':len(questions),'source_method_groups':len(methods),
        'method_reuse_groups':sum(len(v)>1 for v in methods.values()),
        'families_with_ten_questions':sum(counts[k]==10 for k in families),
        'issues':dict(sorted(problems.items())), 'new_certified_independent_forms':0,
        'status':'PASS_STRUCTURE_ONLY' if not problems else 'REVIEW_REQUIRED',
        'scope':'Structural checks and publication safety only; no proof of mathematical or pedagogical correctness.'}

def main():
    result=audit(records(FORMS),records(QUESTIONS))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS_STRUCTURE_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
