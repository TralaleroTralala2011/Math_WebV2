"""Conservative V117 coverage + exact-duplicate + semantic-risk audit.

Never equates a unique ID / stem with a unique mathematical method.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
from difflib import SequenceMatcher
import csv, hashlib, json, re, unicodedata
from .v117_research import METHODS, export
from .expanded_catalog import BLUEPRINTS as V113
from .v114_catalog import BLUEPRINTS as V114
from .v116_research import METHODS as V116


def normalize(text):
    text=unicodedata.normalize('NFKC',str(text)).casefold().strip()
    return re.sub(r'\s+',' ',text)


def all_candidate_records():
    previous=[(a,b,c,d,e,'V113') for a,b,c,d,e in V113]
    previous += [(a,b,c,d,e,'V114') for a,b,c,d,e in V114]
    previous += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V116') for m in V116]
    previous += [(m.family,m.topic,m.title,m.signature,m.difficulty,'V117') for m in METHODS]
    return previous


def audit(project_root, output_dir):
    root=Path(project_root);out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((root/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
    assert len(catalog)==150
    meta=all_candidate_records();ids={v[0] for v in meta}
    if len(ids)!=len(meta):raise ValueError('duplicate family IDs')
    topic_ids={v['id'] for v in catalog}
    if any(m[1] not in topic_ids for m in meta):raise ValueError('uncatalogued method')
    produced=export(out)
    counts=Counter(m[1] for m in meta)
    statuses=[]
    for t in catalog:
        n=counts[t['id']]
        statuses.append({'grade':t['grade'],'topic_id':t['id'],'topic':t['name'],
                         'candidate_form_count':n,'target_forms':500,'missing_candidate_forms':max(0,500-n),
                         'certified_independent_form_count':0,'missing_certified_forms':500,
                         'confirmed_10_question_packages':0, 'candidate_10_question_packages':n,
                         'review_status':'pending'})
    with (out/'V117_150_TOPIC_GAPS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(statuses[0]));writer.writeheader();writer.writerows(statuses)
    (out/'V117_150_TOPIC_GAPS.json').write_text(json.dumps(statuses,ensure_ascii=False,indent=2),encoding='utf8')
    exact_signatures=defaultdict(list)
    for family,topic,name,signature,difficulty,version in meta:
        exact_signatures[normalize(signature)].append((family,topic,version))
    duplicates={s:v for s,v in exact_signatures.items() if len(v)>1}
    # Potential overlap includes different output goals built on the same operation.
    # This is a warning, not an automatic rejection/certification.
    new_signatures=[(m.family,m.topic,normalize(m.signature),normalize(m.title)) for m in METHODS]
    suspicious=[]
    for family,topic,signature,title in new_signatures:
        candidates=[]
        for a,b,c,d,e,version in meta:
            if a==family:continue
            score=max(SequenceMatcher(None,signature,normalize(d)).ratio(),
                      SequenceMatcher(None,title,normalize(c)).ratio())
            if b==topic:score=min(1,score+0.06)
            if score>=0.68:candidates.append((round(score,3),a,version))
        candidates=sorted(candidates,reverse=True)[:3]
        if candidates:
            suspicious.append({'family':family,'topic':topic,'similar_candidates':candidates,
                               'needs_comparative_method_review':True})
    # Both prior curated examples and the verified bank are read only.
    files=[root/'V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl',
           root/'V116_RESEARCH/V116_NEW_QUESTIONS_10_EACH.jsonl',
           root/'backend/app/ai/verified_seed/verified_seed_bank.jsonl']
    base_fps=set();invalid=0;by_file=[]
    for path in files:
        if not path.exists():continue
        num=0
        with path.open('r',encoding='utf8') as f:
            for line in f:
                if not line.strip():continue
                try:record=json.loads(line)
                except json.JSONDecodeError:
                    invalid+=1;continue
                stem=record.get('stem') or record.get('question')
                if isinstance(stem,str) and stem:
                    base_fps.add(hashlib.sha256(normalize(stem).encode('utf8')).hexdigest())
                num+=1
        by_file.append({'file':path.name,'rows':num})
    collisions=[]
    with (out/'V117_NEW_QUESTIONS.jsonl').open('r',encoding='utf8') as f:
        for line in f:
            d=json.loads(line)
            h=hashlib.sha256(normalize(d['stem']).encode('utf8')).hexdigest()
            if h in base_fps:collisions.append({'family':d['family'],'ordinal':d['ordinal']})
    # Risk labels don't constitute certification of dissimilarity.
    report={'topics':150,'target_forms_per_topic':500,'target_unique_forms':75000,
            'target_questions':750000,'candidate_forms_prior':len(meta)-len(METHODS),
            'candidate_forms_new':len(METHODS),'candidate_forms_total':len(meta),
            'candidate_questions_new':produced['questions'],
            'candidate_question_packages_total':len(meta),
            'candidate_questions_total_if_10_generated_per_prior_form':len(meta)*10,
            'math_method_independence_certified':0,
            'topics_with_at_least_500_candidate_forms':sum(n>=500 for n in counts.values()),
            'candidate_coverage_all_150':all(t['candidate_form_count']>0 for t in statuses),
            'new_exact_text_collisions_with_checked_sources':len(collisions),
            'source_rows_read':by_file,'invalid_source_json_lines':invalid,
            'exact_signature_collision_groups':len(duplicates),
            'new_methods_with_possible_similarity':len(suspicious),
            'new_example_checks':'deterministic regeneration + symbolic equivalence; expert proof not complete',
            'publication_blocked':True,
            'warning':'Type IDs, formats and numerical variants are not distinct independent problem-solving methods.'}
    (out/'V117_NEAR_METHOD_REVIEW.json').write_text(json.dumps(suspicious,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'V117_EXACT_SIGNATURE_COLLISIONS.json').write_text(json.dumps(duplicates,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'V117_AUDIT_SUMMARY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(audit(args.root,args.output),indent=2,ensure_ascii=False))
