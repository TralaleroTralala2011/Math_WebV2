"""Read-only independent V121 candidate audit. No publishing or certification."""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / 'V121_3000_NEW_QUESTIONS.jsonl'
FORMS = HERE / 'V121_300_CANDIDATE_FORMS.jsonl'

def load(path):
    with path.open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def independent_oracle(q):
    p = q['params']
    if q['family'] == 'v121_a_menh_de_tap_hop':
        return sum(x % p['a'] == 0 and x % p['b'] != 0 for x in range(1, p['N'] + 1))
    if q['family'] == 'v121_b_menh_de_tap_hop':
        return sum(x % p['a'] == 0 or x % p['b'] == 0 for x in range(1, p['N'] + 1))
    return None

def audit():
    questions, forms = load(DATA), load(FORMS)
    issues = []
    def flag(code, q): issues.append({'code':code,'family':q.get('family'),'ordinal':q.get('ordinal')})
    by_family = collections.Counter(q['family'] for q in questions)
    by_topic = collections.Counter(q['topic_id'] for q in questions)
    sigs = {f['family']:f['signature'] for f in forms}
    oracle_checked = 0
    seen_stems = set()
    for q in questions:
        if q['family'] not in sigs or q['method_signature'] != sigs[q['family']]: flag('family_signature_mismatch',q)
        if not q.get('stem') or not q.get('solution') or not q.get('answer'): flag('missing_required_field',q)
        if q.get('independence_certified') is not False or q.get('method_review_status') != 'pending-expert-review': flag('unexpected_certification',q)
        if not q.get('verification',{}).get('publication_blocked'): flag('unexpected_publication',q)
        stem = re.sub(r'\s+',' ',q['stem']).strip().casefold()
        if stem in seen_stems: flag('duplicate_stem',q)
        seen_stems.add(stem)
        if q['question_type'] == 'trac_nghiem':
            opts = q.get('options',[]); idx = q.get('correct_index')
            if len(opts)!=4 or len(set(map(str,opts)))!=4 or not isinstance(idx,int) or not 0<=idx<4 or str(opts[idx])!=str(q['answer']): flag('invalid_mcq',q)
        oracle = independent_oracle(q)
        if oracle is not None:
            oracle_checked += 1
            if str(oracle) != str(q['numeric_result']): flag('independent_oracle_mismatch',q)
    for family, count in by_family.items():
        if count != 10: issues.append({'code':'family_not_ten','family':family,'count':count})
    for topic, count in by_topic.items():
        if count != 20: issues.append({'code':'topic_not_twenty','topic':topic,'count':count})
    return {'version':'V122','source':'V121','candidate_forms':len(forms),'questions':len(questions),'topics':len(by_topic),'families':len(by_family),'independent_oracle_questions':oracle_checked,'independent_oracle_scope':'two integer-multiple counting families only','issues_total':len(issues),'issues_by_code':dict(collections.Counter(x['code'] for x in issues)),'issue_examples':issues[:30],'certified_new_independent_forms':0,'status':'candidate_only; independent-method and pedagogical review pending'}

if __name__=='__main__':
    result = audit()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if '--strict' in sys.argv and result['issues_total']:
        sys.exit(1)
