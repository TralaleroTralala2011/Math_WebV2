"""V119 auditable progress: exact text duplication, method-signature risks and slots.

An automated semantic similarity score cannot certify independent pedagogy.
Rows in the old seed are read only. Output stays quarantined from production.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from difflib import SequenceMatcher
from hashlib import sha256
import csv,json,unicodedata,re
from .v117_audit import all_candidate_records
from .v118_research import METHODS as V118
from .v119_research import METHODS as V119, export


def norm(s):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(s)).casefold().strip())

def text_id(s):return sha256(norm(s).encode('utf8')).hexdigest()


def audit(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((root/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
    assert len(catalog)==150 and len({x['id'] for x in catalog})==150
    catalog_index={r['id']:r for r in catalog}
    current=[(m.family,m.topic,m.title,m.signature,m.difficulty,'V119') for m in V119]
    historical=all_candidate_records()+[(m.family,m.topic,m.title,m.signature,m.difficulty,'V118') for m in V118]
    rows=historical+current
    if len(rows)!=len(set(r[0] for r in rows)):raise ValueError('duplicate registered ID')
    for m in V119:
        if m.topic not in catalog_index or m.grade!=catalog_index[m.topic]['grade']:
            raise ValueError('misclassified topic: '+m.family)
    result=export(out)
    counts=Counter(r[1] for r in rows)
    newly=Counter(r.topic for r in V119)
    status=[];slots=[]
    for item in catalog:
        key=item['id']
        n=newly[key]
        status.append(dict(grade=item['grade'],topic_id=key,topic=item['name'],
            target_new_methods=10,authored_v119_candidate_methods=n,
            pending_new_methods=10-n,existing_pre_v119_candidates=counts[key]-n,
            all_candidate_methods=counts[key],new_questions_math_checked=10*n,
            certified_independent_new_methods=0,approval_status='pending-expert-review'))
        for i in range(1,11):
            m=next((m for j,m in enumerate([m for m in V119 if m.topic==key],start=1) if j==i),None)
            slots.append(dict(grade=item['grade'],topic_id=key,topic=item['name'],slot=i,
                family=m.family if m else '', method_title=m.title if m else '',
                question_count=10 if m else 0,
                status='candidate-ready-for-expert-method-review' if m else 'not-authored'))
    for name,items in [('V119_TOPIC_PROGRESS_150.csv',status),('V119_REQUEST_1500_SLOTS.csv',slots)]:
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(items[0]));writer.writeheader();writer.writerows(items)
    old_sources=[root/'backend/app/ai/verified_seed/verified_seed_bank.jsonl',
        root/'V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl',
        root/'V116_RESEARCH/V116_NEW_QUESTIONS_10_EACH.jsonl',
        root/'V117_AUDIT/V117_NEW_QUESTIONS.jsonl',
        root/'V118_AUDIT/V118_NEW_QUESTIONS.jsonl']
    old_text=set();sources=[];bad=0
    for file in old_sources:
        rows_count=0
        if file.exists():
            with file.open(encoding='utf8') as stream:
                for line in stream:
                    if not line.strip():continue
                    try:r=json.loads(line)
                    except json.JSONDecodeError:
                        bad+=1;continue
                    stem=r.get('stem') or r.get('question')
                    if isinstance(stem,str) and stem.strip():old_text.add(text_id(stem))
                    rows_count+=1
        sources.append({'file':str(file.relative_to(root)), 'rows':rows_count, 'missing':not file.exists()})
    exact_collisions=[];seen=set();types=Counter();new_forms=set()
    with (out/'V119_NEW_QUESTIONS.jsonl').open(encoding='utf8') as f:
        for line in f:
            r=json.loads(line);h=text_id(r['stem'])
            if h in old_text:exact_collisions.append({'family':r['family'],'ordinal':r['ordinal']})
            if h in seen:raise ValueError('duplicate new text')
            seen.add(h);types[r['question_type']]+=1;new_forms.add(r['family'])
    existing_signatures=defaultdict(list)
    for id,topic,title,signature,diff,version in historical:
        existing_signatures[norm(signature)].append({'family':id,'topic':topic,'version':version})
    exact_method_overlaps=[];near_method=[]
    for m in V119:
        matching=existing_signatures.get(norm(m.signature),[])
        if matching: exact_method_overlaps.append({'family':m.family,'matching':matching})
        candidates=[]
        for id,topic,title,signature,diff,version in historical:
            if topic!=m.topic:continue
            sim=max(SequenceMatcher(None,norm(m.signature),norm(signature)).ratio(),
                    SequenceMatcher(None,norm(m.title),norm(title)).ratio())
            if sim>=0.65:candidates.append({'other':id,'version':version,'similarity':round(sim,3)})
        if candidates:near_method.append({'family':m.family,'topic':m.topic,
                                         'closest':sorted(candidates,key=lambda x:-x['similarity'])[:3]})
    summary={'version':'V119','requested_topics':150,'requested_new_forms_per_topic':10,
      'requested_new_forms_total':1500,'requested_new_questions':15000,
      'authored_new_candidate_forms':result['new_candidate_methods'],
      'authored_new_questions_with_math_checks':result['verified_answer_questions'],
      'topics_with_ten_new_candidate_forms':sum(n>=10 for n in newly.values()),
      'topics_with_no_new_candidate_forms':sum(newly[t['id']]==0 for t in catalog),
      'total_preexisting_candidate_forms':len(historical),
      'total_candidate_forms_after':len(rows),
      'independence_certified':0,'new_approved_for_publication':0,
      'new_question_formats':dict(types),'source_rows_checked':sources,
      'invalid_old_source_json_lines':bad,'exact_question_collisions_with_sources':len(exact_collisions),
      'exact_method_signature_collision_groups':len(exact_method_overlaps),
      'new_methods_with_near_same_topic_method_warning':len(near_method),
      'important_limitation':'A correct numeric answer and distinct text cannot certify an independent mathematical method. Method overlap needs expert validation. 147/150 topics have no V119 methods yet.'}
    for file,thing in [('V119_AUDIT_SUMMARY.json',summary),
        ('V119_QUESTION_COLLISIONS.json',exact_collisions),
        ('V119_SIGNATURE_COLLISIONS.json',exact_method_overlaps),
        ('V119_NEAR_METHOD_REVIEW.json',near_method)]:
        (out/file).write_text(json.dumps(thing,ensure_ascii=False,indent=2),encoding='utf8')
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(audit(a.root,a.out),ensure_ascii=False,indent=2))
