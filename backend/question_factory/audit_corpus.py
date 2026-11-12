"""Streaming, repeatable structural audit of the legacy 344k-question seed bank.

This produces REVIEW CANDIDATES, never an assertion of independent methods.
Numbers in a signature, a new family ID, or altered prose do NOT count as
proof of mathematical type independence.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from .bootstrap import CATALOG

DIGITS = re.compile(r'\d+(?:[.,]\d+)?')
WHITESPACE = re.compile(r'\s+')
PLACEHOLDER_WORDS = re.compile(r'\b(?:not independent|same solution method|shared method family|numeric variant|parameterized variant)\b',re.I)


def normalize_signature(value):
    # This is a coarse collision warning, NOT a proof of semantic equivalence.
    value=unicodedata.normalize('NFKC',str(value or '')).casefold()
    value=DIGITS.sub('#',value)
    return WHITESPACE.sub(' ',re.sub(r'[^\w#]+',' ',value)).strip()


def audit(input_path, out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    catalog=json.loads(Path(CATALOG).read_text(encoding='utf-8'))
    if len(catalog)!=150:raise RuntimeError('canonical catalog must contain 150 entries')
    aliases=collections.defaultdict(list)
    for topic in catalog:
        aliases[(topic['grade'],topic['name'].strip().casefold())].append(topic['id'])
    groups={}; source_names=collections.Counter();total=0;invalid=0;proof_missing=0;short_solutions=0
    explicit_variant_rows=0
    for line_num,line in enumerate(Path(input_path).open(encoding='utf-8'),1):
        try:
            row=json.loads(line);grade=int(row['grade']);name=str(row['topic']).strip()
            signature=str(row.get('form_signature') or '').strip()
            if not signature or not str(row.get('question') or '').strip():
                invalid+=1;continue
        except (ValueError,TypeError,KeyError,json.JSONDecodeError):
            invalid+=1;continue
        total+=1;source_names[(grade,name)]+=1
        no_proof='proof' not in row or row['proof'] is None
        short=len(str(row.get('solution') or '').strip())<25
        proof_missing+=int(no_proof);short_solutions+=int(short)
        if PLACEHOLDER_WORDS.search(signature): explicit_variant_rows+=1
        key=(grade,name,signature)
        g=groups.get(key)
        if g is None:
            g=dict(grade=grade,topic=name,source_signature=signature,
                   coarse_signature=normalize_signature(signature),rows=0,
                   short_solutions=0,rows_without_proof=0,
                   sample_questions=[],unique_question_hashes=set(),method_family_samples=set())
            groups[key]=g
        g['rows']+=1;g['short_solutions']+=int(short);g['rows_without_proof']+=int(no_proof)
        if len(g['sample_questions'])<2:g['sample_questions'].append(str(row['question'])[:300])
        if len(g['method_family_samples'])<3:g['method_family_samples'].add(str(row.get('method_family') or row.get('form_id') or '')[:100])
        # Exactly repeated question text is reported, but do not retain huge strings.
        if len(g['unique_question_hashes'])<10:
            g['unique_question_hashes'].add(hashlib.blake2b(str(row['question']).encode(),digest_size=12).digest())
    count_coarse=collections.Counter((g['grade'],g['topic'],g['coarse_signature']) for g in groups.values())
    per_source=collections.defaultdict(lambda:dict(rows=0,raw_signature_groups=0,coarse_signature_groups=set()))
    oversized=[];priorities=collections.Counter();candidate_file=out_dir/'V113_SOURCE_FORM_CANDIDATES.jsonl'
    with candidate_file.open('w',encoding='utf-8') as writer:
        for g in sorted(groups.values(),key=lambda g:(g['grade'],g['topic'],g['source_signature'])):
            k=(g['grade'],g['topic']);dst=per_source[k];dst['rows']+=g['rows'];dst['raw_signature_groups']+=1
            dst['coarse_signature_groups'].add(g['coarse_signature'])
            matches=aliases[(g['grade'],g['topic'].casefold())]
            collisions=count_coarse[(g['grade'],g['topic'],g['coarse_signature'])]
            strong_evidence=(g['rows']>=10 and len(g['unique_question_hashes'])>=10
                             and g['rows_without_proof']==0 and g['short_solutions']==0)
            priority=('high' if strong_evidence and collisions==1 and g['rows']<=20
                      and not PLACEHOLDER_WORDS.search(g['source_signature'])
                      else ('medium' if len(g['unique_question_hashes'])>=10
                            and g['short_solutions']<=g['rows']//10 and collisions<=2
                            else 'low'))
            priorities[priority]+=1
            candidate=dict(grade=g['grade'],source_topic=g['topic'],source_signature=g['source_signature'],
                coarse_signature=g['coarse_signature'],source_rows=g['rows'],
                numeric_signature_collision_group_size=collisions,review_priority=priority,
                unique_stem_sample_count=min(10,len(g['unique_question_hashes'])),
                short_solutions=g['short_solutions'],rows_without_proof=g['rows_without_proof'],
                sample_questions=g['sample_questions'], source_family_samples=sorted(g['method_family_samples']),
                exact_catalog_topic_id=matches[0] if len(matches)==1 else None,
                catalog_match_status='unique' if len(matches)==1 else ('ambiguous' if matches else 'unmapped'),
                warning='CANDIDATE ONLY: NOT A CERTIFIED INDEPENDENT MATHEMATICAL METHOD')
            writer.write(json.dumps(candidate,ensure_ascii=False,separators=(',',':'))+'\n')
            if g['rows']>=100:
                oversized.append(dict(grade=g['grade'],topic=g['topic'],signature=g['source_signature'],rows=g['rows']))
    rows=[];linked=0
    for entry in catalog:
        grade,name,tid=entry['grade'],entry['name'],entry['id']
        matching=(grade,name.casefold())
        is_unique=len(aliases[matching])==1
        s=per_source.get((grade,name)) if is_unique else None
        exact=0 if not s else s['raw_signature_groups']
        coarse=0 if not s else len(s['coarse_signature_groups'])
        count=0 if not s else s['rows']
        linked+=int(count>0)
        rows.append(dict(topic_id=tid,grade=grade,name=name,source_exact_title_match=is_unique,
                         source_question_rows=count,source_signature_candidate_groups=exact,
                         coarse_collision_groups=coarse,independent_methods_certified=0,
                         required_methods=2000,remaining_unverified_methods=2000,
                         required_questions=20000,remaining_unverified_questions=20000,
                         note='0 certified here does not mean no good questions exist in the legacy bank'))
    report=dict(source=Path(input_path).name,requested_topics=150,target_methods=300000,target_questions=3000000,
                parsed_question_rows=total,invalid_or_missing_signature_rows=invalid,
                exact_signature_groups=len(groups),coarse_numeric_normalized_groups=len(count_coarse),
                explicitly_variant_labeled_question_rows=explicit_variant_rows,
                rows_without_proof=proof_missing,short_solution_rows=short_solutions,
                legacy_grade_topic_pairs=len(source_names),catalog_topics_with_unique_title_and_legacy_rows=linked,
                review_priorities=dict(priorities),
                oversized_signature_groups_ge_100=len(oversized),top_oversized_signatures=sorted(oversized,key=lambda x:-x['rows'])[:30],
                warning='Raw or normalized signature counts do not certify independent mathematical methods.',
                coverage=rows)
    (out_dir/'V113_COVERAGE_150.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (out_dir/'V113_CORPUS_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--out-dir',required=True)
    args=parser.parse_args();report=audit(args.input,args.out_dir)
    print(json.dumps({k:v for k,v in report.items() if k not in ('coverage','top_oversized_signatures')},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
