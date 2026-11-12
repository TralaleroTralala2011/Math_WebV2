"""Audit the 500-form-per-topic *target* without miscounting variants as forms.

python -m question_factory.v116_audit --out ../V116_RESEARCH
All candidate types remain unpublished until expert review.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from .expanded_catalog import BLUEPRINTS as V113
from .v114_catalog import BLUEPRINTS as V114
from .v116_research import METHODS,export
from .bootstrap import CATALOG
from . import engine


def _fp(question):
    return hashlib.sha256(re.sub(r'\s+',' ',str(question).strip().casefold()).encode('utf-8')).hexdigest()


def audit(out_folder, legacy=None):
    path=Path(out_folder);path.mkdir(parents=True,exist_ok=True)
    topics=json.loads(CATALOG.read_text(encoding='utf-8'))
    assert len(topics)==150
    new=export(path)
    by_topic=defaultdict(list);recent=set();old_stems=set()
    records=[]
    for version,blueprints in [('V113',V113),('V114',V114)]:
        for fam,topic,title,signature,difficulty in blueprints:
            by_topic[topic].append((version,fam,title,signature))
            for n in range(10):
                key=f'{topic}:v113-{fam}' if version=='V113' else f'{topic}:v114-{fam}'
                q=engine.generate(fam,n,difficulty,seed_key=key)
                old_stems.add(q['fingerprint'])
    for method in METHODS:
        by_topic[method.topic].append(('V116',method.family,method.title,method.signature))
    for row in (path/'V116_NEW_QUESTIONS_10_EACH.jsonl').read_text(encoding='utf-8').splitlines():
        r=json.loads(row);recent.add(r['fingerprint'])
    assert len(recent)==310
    overlap_with_older_candidates=len(recent & old_stems)
    legacy_count=legacy_invalid=legacy_exact_overlap=0
    if legacy is not None:
        with Path(legacy).open('r',encoding='utf-8') as stream:
            for line in stream:
                try:
                    old=json.loads(line)
                    stem=old.get('question') or old.get('stem')
                    if not stem:continue
                    legacy_count+=1
                    if _fp(stem) in recent:
                        legacy_exact_overlap+=1
                except json.JSONDecodeError:
                    legacy_invalid+=1
    for topic in topics:
        c=by_topic[topic['id']];n=len(c)
        records.append({'topic_id':topic['id'],'grade':topic['grade'],'name':topic['name'],
                        'target_independent_types':500,'target_exercises':5000,
                        'candidate_blueprints_v113_v114_v116':n,
                        'new_v116_candidates':sum(x[0]=='V116' for x in c),
                        'candidate_examples_total':n*10,
                        'independently_certified_types':0,'reviewed_for_global_method_uniqueness':False,
                        'candidate_type_gap_if_all_pass':max(0,500-n),
                        'certified_type_gap':500})
    assert len(records)==150
    summary={'version':'V116','target_topics':150,'target_types_per_topic':500,
        'target_total_independent_types':75000,'target_total_questions':750000,
        'old_candidates':len(V113)+len(V114),'new_v116_candidates':len(METHODS),
        'all_candidate_blueprints':len(V113)+len(V114)+len(METHODS),
        'new_math_checked_exercises':310,'all_candidate_exercises':(len(V113)+len(V114)+len(METHODS))*10,
        'new_exact_collisions_with_165_older_candidate_questions':overlap_with_older_candidates,
        'legacy_questions_checked':legacy_count,'legacy_invalid_json_lines':legacy_invalid,
        'new_exact_collisions_with_legacy_questions':legacy_exact_overlap,
        'distinct_methods_globally_certified':0,
        'possible_candidate_gap_if_all_pass':75000-(len(V113)+len(V114)+len(METHODS)),
        'certified_methods_gap':75000,
        'quality_note':'An equation/answer check and absence of exact wording duplicates do NOT certify a distinct mathematical method or topic-level pedagogical fitness.',
        'research_sources':[
            {'title':'Vietnam general education curricula (Circular 32/2018/TT-BGDDT)','url':'https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721'},
            {'title':'OpenStax Algebra and Trigonometry 2e','url':'https://openstax.org/books/algebra-and-trigonometry-2e/pages/preface'},
            {'title':'Khan Academy high school mathematics curriculum outlines','url':'https://www.khanacademy.org/math'}],
        'source_policy':'References used only for content taxonomy; new problems and explanations were authored originally, not copied.',
        'coverage':{'topics_with_v116_new_content':sum(r['new_v116_candidates']>0 for r in records),
                    'topics_with_some_candidates':sum(r['candidate_blueprints_v113_v114_v116']>0 for r in records),
                    'topics_reaching_500_candidates':sum(r['candidate_blueprints_v113_v114_v116']>=500 for r in records)}
    }
    (path/'V116_AUDIT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (path/'V116_150_TOPIC_PROGRESS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='../V116_RESEARCH');p.add_argument('--legacy',default=None)
    args=p.parse_args();print(json.dumps(audit(args.out,args.legacy),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
