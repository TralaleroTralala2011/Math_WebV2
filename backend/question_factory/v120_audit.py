"""Read-only V120 exact-text and candidate-method collision audit.

Does NOT certify pedagogical novelty or mathematically prove narrative prompts.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher
import csv, json, re, unicodedata
from hashlib import sha256
from .v120_research import METHODS, export
from .v119_audit import audit as unused_v119_audit
from .v117_audit import all_candidate_records
from .v118_research import METHODS as V118
from .v119_research import METHODS as V119


def normalize(text):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(text)).casefold().strip())

def digest(text):
    return sha256(normalize(text).encode('utf8')).hexdigest()


def run(root,out):
    root,out=Path(root),Path(out)
    out.mkdir(parents=True,exist_ok=True)
    export_stats=export(out)
    catalog=json.loads((root/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
    older=all_candidate_records()
    older += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V118') for m in V118]
    older += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V119') for m in V119]
    if len(older)!=320:raise ValueError(f'unexpected previous candidate count {len(older)}')
    bytopic=Counter(row[1] for row in older)
    types=Counter(m.topic for m in METHODS)
    if any(types[t['id']]!=1 for t in catalog):raise ValueError('missing topic')
    # Existing questions are NOT modified; count old rows we truly read.
    sources=[root/'backend/app/ai/verified_seed/verified_seed_bank.jsonl',
             root/'V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl',
             root/'V116_RESEARCH/V116_NEW_QUESTIONS_10_EACH.jsonl',
             root/'V117_AUDIT/V117_NEW_QUESTIONS.jsonl',
             root/'V118_AUDIT/V118_NEW_QUESTIONS.jsonl',
             root/'V119_RESEARCH/V119_NEW_QUESTIONS.jsonl']
    old=set();counts=[];bad=[]
    for file in sources:
        n=0
        if file.exists():
            with file.open(encoding='utf8') as stream:
                for no,line in enumerate(stream,1):
                    if not line.strip():continue
                    try:rec=json.loads(line)
                    except ValueError:
                        bad.append([file.name,no]);continue
                    q=rec.get('stem') or rec.get('question')
                    if isinstance(q,str) and q.strip():old.add(digest(q))
                    n+=1
        counts.append({'file':str(file.relative_to(root)),'readable_rows':n,'missing':not file.exists()})
    collisions=[];newhash=set()
    qfile=out/'V120_1500_NEW_QUESTIONS.jsonl'
    with qfile.open(encoding='utf8') as stream:
        for line in stream:
            q=json.loads(line);key=digest(q['stem'])
            if key in old:collisions.append([q['family'],q['ordinal']])
            if key in newhash:raise ValueError('duplicate in new 1500')
            newhash.add(key)
    # Similarity alerts are triage, not an independence certificate.
    alerts=[]
    for m in METHODS:
        comparisons=[]
        for family,topic,title,signature,difficulty,version in older:
            if topic!=m.topic:continue
            s1=SequenceMatcher(None,normalize(m.title),normalize(title)).ratio()
            s2=SequenceMatcher(None,normalize(m.skill),normalize(signature)).ratio()
            if max(s1,s2)>=0.57:
                comparisons.append({'older_id':family,'older_version':version,'score':round(max(s1,s2),3),
                                    'older_title':title})
        if comparisons:alerts.append({'family':m.family,'topic':m.topic,'matches':sorted(comparisons,key=lambda x:-x['score'])[:5]})
    with (out/'V120_POSSIBLE_METHOD_OVERLAPS.json').open('w',encoding='utf8') as f:
        json.dump(alerts,f,ensure_ascii=False,indent=2)
    rows=[]
    for t in catalog:
        rows.append({'grade':t['grade'],'topic_id':t['id'],'topic':t['name'],
          'new_candidate_forms_V120':1,'new_questions_V120':10,
          'candidate_forms_before_V120':bytopic[t['id']],
          'candidate_forms_after_V120':bytopic[t['id']]+1,
          'independence_certified_V120':0,'expert_review':'pending',
          'target_new_forms_this_batch':1,
          'target_500_forms_per_topic_gap_candidates':max(0,500-bytopic[t['id']]-1)})
    with (out/'V120_PROGRESS_150_TOPICS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={
      'source_version':'V119','version':'V120','topics_requested':150,
      'new_candidate_forms':150,'new_questions':1500,
      'new_topics_covered':150,'new_questions_arithmetic_check_passed':export_stats['new_questions_checked_arithmetically'],
      'topic_ids_covered':len(types),'previous_candidate_forms':len(older),
      'candidate_forms_after_V120':len(older)+150,
      'formats':export_stats['question_formats'],
      'old_source_reads':counts,'old_json_read_errors':len(bad),
      'exact_question_text_collisions_with_old':len(collisions),
      'exact_question_text_collisions_within_V120':0,
      'new_methods_flagged_by_title_or_signature_similarity':len(alerts),
      'independent_methods_certified':0,'expert_review_complete':False,'published_new_methods':0,
      'method_novelty_warning':'150 authored candidate objectives, not 150 independently certified globally new math methods; similar skills in multiple topics may overlap.',
      'answer_correctness_warning':'SymPy evaluates the authored answer expression; method-level mathematical narratives and distractor pedagogy still require independent assessment.',
      'preservation':'No legacy application data, existing questions, social features, Battle code, or UI are modified in this stage.'
    }
    (out/'V120_AUDIT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'V120_QUESTION_COLLISIONS.json').write_text(json.dumps(collisions,ensure_ascii=False,indent=2),encoding='utf8')
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    print(json.dumps(run(a.root,a.out),ensure_ascii=False,indent=2))
