"""Read-only, streaming audit of the V111 JSONL bank (no certification of method independence).

Usage: python tools/audit_v111_seed_stream.py [--input PATH] [--output PATH]
"""
from __future__ import annotations
import argparse, collections, hashlib, json
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BANK=ROOT/'backend/app/ai/verified_seed/verified_seed_bank.jsonl'


def audit(path: Path):
    row_count=0
    bad_json=0
    missing_fields=0
    bad_linear_proofs=0
    valid_linear_proofs=0
    duplicate_stems=0
    short_solutions=0
    proof_missing=0
    form_counts=collections.Counter()
    family_counts=collections.Counter()
    grade_topic_counts=collections.Counter()
    method_status_counts=collections.Counter()
    seen=set()
    for line in path.open(encoding='utf-8'):
        if not line.strip(): continue
        row_count += 1
        try: r=json.loads(line)
        except json.JSONDecodeError:
            bad_json+=1;continue
        g=r.get('grade');t=r.get('topic');q=str(r.get('question',''))
        if not g or not t or not q.strip() or not str(r.get('answer','')).strip() or not str(r.get('solution','')).strip():
            missing_fields+=1
        key=(g,t,str(r.get('form_signature','')))
        form_counts[key]+=1
        grade_topic_counts[(g,t)]+=1
        family_counts[(g,t,str(r.get('form_id') or r.get('method_family') or 'unknown'))]+=1
        method_status_counts[str(r.get('type_status','unspecified'))]+=1
        normalized=' '.join(q.casefold().split())
        fingerprint=hashlib.blake2b(f'{g}|{t}|{normalized}'.encode(),digest_size=16).digest()
        if fingerprint in seen:duplicate_stems+=1
        else:seen.add(fingerprint)
        if len(str(r.get('solution','')).strip())<25:short_solutions+=1
        proof=r.get('proof')
        if not proof:
            proof_missing+=1
        if r.get('form_id')=='linear_isolate' and proof:
            try:
                a,b,c,x=(Fraction(str(proof[k])) for k in ('a','b','c','x'))
                correct=a!=0 and a*x+b==c and Fraction(str(r['answer']))==x
            except (KeyError, ValueError, ZeroDivisionError, TypeError):correct=False
            if correct:valid_linear_proofs+=1
            else:bad_linear_proofs+=1
    catalog=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text(encoding='utf-8'))
    possible_names={(x['grade'],x['name'].casefold()) for x in catalog}
    title_matched={(g,t.casefold()) for g,t in grade_topic_counts if (g,str(t).casefold()) in possible_names}
    out={
      'scope':'structural and exact linear-equation checks; NOT independent-form certification',
      'source_bank':path.name,
      'source_question_rows':row_count,
      'invalid_json_rows':bad_json,
      'rows_missing_required_fields':missing_fields,
      'duplicate_stems_by_grade_and_topic':duplicate_stems,
      'solutions_under_25_characters':short_solutions,
      'rows_without_proof_field':proof_missing,
      'valid_linear_proofs':valid_linear_proofs,
      'invalid_linear_proofs':bad_linear_proofs,
      'grade_topic_pairs':len(grade_topic_counts),
      'canonical_topic_count':len(catalog),
      'canonical_grade_title_matches':len(title_matched),
      'grouped_form_signatures':len(form_counts),
      'signature_groups_with_at_least_10_rows':sum(v>=10 for v in form_counts.values()),
      'distinct_grade_topic_family_ids':len(family_counts),
      'top_family_groups':[{'grade':g,'topic':t,'family':f,'questions':n} for (g,t,f),n in family_counts.most_common(15)],
      'type_statuses':dict(method_status_counts),
      'certified_independent_form_count': None,
      'note':'An ID or parameter variation never establishes a genuinely new problem type.'
    }
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=DEFAULT_BANK)
    p.add_argument('--output',type=Path,default=ROOT/'QUESTION_FACTORY_V112_SOURCE_AUDIT.json')
    args=p.parse_args();out=audit(args.input)
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ('top_family_groups','type_statuses')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
