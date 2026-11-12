"""Export precisely 10 reproducible, independently recomputed questions per blueprint.

Run with: python -m question_factory.export_curated --output ../V113_CURATED_600.jsonl
Output remains candidate/pending-review: verification of a numerical answer
is not the same as expert review or uniqueness certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from . import engine
from .expanded_catalog import BLUEPRINTS,CONCEPT_COLLISIONS


def export(output):
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    seen=set();records=0;report=[]
    with output.open('w',encoding='utf-8') as out:
        for family,topic,title,signature,difficulty in BLUEPRINTS:
            question_hashes=set()
            for ordinal in range(10):
                q=engine.generate(family,ordinal,difficulty,seed_key=f'{topic}:v113-{family}')
                ok,validation=engine.independently_verify(q)
                if not ok: raise RuntimeError(f'verifier rejects {family} {ordinal}: {validation}')
                if q['fingerprint'] in seen:raise RuntimeError(f'duplicate question stem: {family} {ordinal}')
                seen.add(q['fingerprint']);question_hashes.add(q['fingerprint'])
                value={
                    'topic_id':topic,'family':family,'method_name':title,'method_signature':signature,
                    'method_review_status':'pending-expert-review',
                    'possible_equivalence_group':CONCEPT_COLLISIONS.get(family,family),
                    'math_check_status':'symbolically-verified',
                    'ordinal':ordinal,'difficulty':difficulty,
                    'question':q['stem'],'answer':q['answer'],'solution':q['solution'],
                    'proof':{'parameters':q['params'],'verifier':validation},
                    'fingerprint':q['fingerprint'],
                }
                out.write(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n');records+=1
            if len(question_hashes)!=10:raise RuntimeError(f'not 10 distinct stems {family}')
            report.append(dict(family=family,topic_id=topic,count=len(question_hashes),
                validation='symbolically-verified',method_independence='not-certified'))
    summary={'blueprint_count':len(BLUEPRINTS),'question_count':records,
             'topics_touched':len(set(x[1] for x in BLUEPRINTS)),
             'questions_with_verified_math':records,'methods_independence_certified':0,
             'coarse_new_concept_groups':len({CONCEPT_COLLISIONS.get(row[0],row[0]) for row in BLUEPRINTS}),
             'human_approved_to_publish':0,
             'note':'All questions are review candidates, not authorized to leak into live games.',
             'methods':report}
    (output.parent/'V113_CURATED_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);a=parser.parse_args()
    result=export(a.output)
    print(f"{result['question_count']} candidate questions with symbolic checks; "
          f"{result['topics_touched']} topics; {result['human_approved_to_publish']} human-approved")

if __name__=='__main__':main()
