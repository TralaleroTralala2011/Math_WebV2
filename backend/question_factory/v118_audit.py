"""V118: read-only whole-corpus collision audit and 150-topic objective tracker.

Exact-duplicate checking is a *necessary* quality gate, never proof of
independence of mathematical methods. Audit does not promote/publish questions.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
import csv, json, re, unicodedata
from .v118_research import METHODS as CURRENT, export
from .v117_audit import all_candidate_records


def normalized(value):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(value)).casefold().strip())

def digest(s):return sha256(normalized(s).encode('utf8')).hexdigest()

def audit(root, out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    topics=json.loads((root/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
    if len(topics)!=150:raise ValueError('expected exactly 150 topics')
    previous=all_candidate_records()
    current=[(m.family,m.topic,m.title,m.signature,m.difficulty,'V118') for m in CURRENT]
    records=previous+current
    ids=[v[0] for v in records]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate family ID')
    idx={r['id']:r for r in topics}
    if len(idx)!=len(topics):raise ValueError('duplicate topic ID')
    for m in CURRENT:
        if m.topic not in idx or idx[m.topic]['grade']!=m.grade:
            raise ValueError('topic/grade mismatch: '+m.family)
    baseline=export(out)
    counts=Counter(item[1] for item in records)
    statuses=[{'grade':r['grade'],'topic_id':r['id'],'topic':r['name'],
               'target_types':500,'candidate_types':counts[r['id']],
               'candidate_gap':500-counts[r['id']],
               'independence_certified':0,'certified_gap':500,
               'status':'pending-method-review'} for r in topics]
    with (out/'V118_150_TOPIC_GAPS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(statuses[0]));writer.writeheader();writer.writerows(statuses)
    (out/'V118_150_TOPIC_GAPS.json').write_text(json.dumps(statuses,ensure_ascii=False,indent=2),encoding='utf8')

    # Compare new questions with prior published bank and previous candidate batches.
    sources=[root/'backend/app/ai/verified_seed/verified_seed_bank.jsonl',
             root/'V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl',
             root/'V116_RESEARCH/V116_NEW_QUESTIONS_10_EACH.jsonl',
             root/'V117_AUDIT/V117_NEW_QUESTIONS.jsonl']
    found=set();read=[];invalid=[]
    for file in sources:
        if not file.exists():
            read.append({'file':str(file.relative_to(root)),'rows':0,'missing':True})
            continue
        count=0
        with file.open(encoding='utf8') as stream:
            for line_no,line in enumerate(stream,1):
                if not line.strip():continue
                try:r=json.loads(line)
                except json.JSONDecodeError:
                    invalid.append({'file':file.name,'line':line_no});continue
                text=r.get('stem') or r.get('question')
                if isinstance(text,str) and text.strip():found.add(digest(text))
                count+=1
        read.append({'file':file.name,'rows':count,'missing':False})
    collisions=[];seen=set();fmt=Counter();exact_across_v118=[]
    with (out/'V118_NEW_QUESTIONS.jsonl').open(encoding='utf8') as f:
        for line in f:
            record=json.loads(line);h=digest(record['stem']);fmt[record['question_type']]+=1
            if h in found:collisions.append({'family':record['family'],'ordinal':record['ordinal']})
            if h in seen:exact_across_v118.append({'family':record['family'],'ordinal':record['ordinal']})
            seen.add(h)
    if exact_across_v118:
        raise ValueError('V118 repeated normalized stem')
    sigs=defaultdict(list)
    for family,topic,title,signature,difficulty,version in records:
        sigs[normalized(signature)].append({'family':family,'topic':topic,'version':version})
    exact_sig={k:v for k,v in sigs.items() if len(v)>1}
    near=[]
    for m in CURRENT:
        choices=[]
        for fam,topic,title,signature,difficulty,version in records:
            if fam==m.family:continue
            score=max(SequenceMatcher(None,normalized(m.signature),normalized(signature)).ratio(),
                      SequenceMatcher(None,normalized(m.title),normalized(title)).ratio())
            if topic==m.topic:score=min(1,score+0.06)
            if score>=0.69:choices.append({'other':fam,'source':version,'similarity':round(score,3)})
        if choices:
            near.append({'family':m.family,'review':sorted(choices,key=lambda x:-x['similarity'])[:4]})
    report={'source_version':'V117 + research V118',
            'target_topics':150,'target_types_per_topic':500,'target_types':75000,
            'target_questions':750000,'candidate_methods_previous':len(previous),
            'new_candidate_methods':len(CURRENT),'candidate_methods_total':len(records),
            'new_questions_generated':baseline['question_count'],
            'total_candidate_questions_at_10_per_type':len(records)*10,
            'formats':dict(fmt),'independence_certified':0,
            'topics_with_500_candidates':sum(s['candidate_types']>=500 for s in statuses),
            'minimum_candidates_in_topic':min(counts.values()),
            'maximum_candidates_in_topic':max(counts.values()),
            'old_corpus_files':read,'old_corpus_invalid_json':len(invalid),
            'normalized_text_collisions':len(collisions),'exact_method_signature_collisions':len(exact_sig),
            'new_methods_with_possible_similarity':len(near),
            'review_required':True,'publication_blocked':True,
            'do_not_claim_100_percent':True,
            'limitations':'No proof of novelty against legacy mathematical reasoning or expert pedagogical approval. Format changes and number substitutions are never counted as new independent methods.'}
    for name,obj in [('V118_SUMMARY.json',report),('V118_NEAR_METHODS.json',near),
                     ('V118_EXACT_SIGNATURE_COLLISIONS.json',exact_sig),('V118_TEXT_COLLISIONS.json',collisions)]:
        (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
    return report

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(audit(args.root,args.output),ensure_ascii=False,indent=2))
