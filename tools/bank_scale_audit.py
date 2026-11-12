#!/usr/bin/env python3
"""Stream-audit a MATH_WEB JSONL bank, without loading all questions into RAM.
Usage: python tools/bank_scale_audit.py backend/app/ai/verified_seed/verified_seed_bank.jsonl --output audit.json
This detects exact/normalized duplicates, short forms, and topic coverage; it does NOT certify distinct math types.
"""
import argparse,collections,hashlib,json,re,unicodedata
from pathlib import Path

def norm(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold()
    s=re.sub(r'\s+',' ',s).strip()
    return s

def audit(path):
    form_counts=collections.Counter(); topics=collections.Counter(); grades=collections.Counter()
    family_forms=collections.defaultdict(set); q_seen={}; duplicates=[]; missing=[]; malformed=[]
    total=0
    with Path(path).open(encoding='utf-8') as f:
        for line_no,line in enumerate(f,1):
            try: r=json.loads(line)
            except (ValueError,TypeError):malformed.append(line_no);continue
            total+=1
            g=str(r.get('grade',''));t=str(r.get('topic',''));fid=str(r.get('form_id',''))
            key=(g,t,fid);form_counts[key]+=1;topics[(g,t)]+=1;grades[g]+=1
            fam=norm(r.get('method_family') or r.get('form_signature') or fid)
            family_forms[(g,t,fam)].add(fid)
            if not all(norm(r.get(k,'')) for k in ('question','answer','solution')):
                if len(missing)<100:missing.append({'line':line_no,'form_id':fid})
            qhash=hashlib.sha256((g+'\0'+t+'\0'+norm(r.get('question',''))).encode()).digest()
            if qhash in q_seen and len(duplicates)<100:
                duplicates.append({'line':line_no,'first_line':q_seen[qhash],'form_id':fid})
            else:q_seen.setdefault(qhash,line_no)
    short=sum(v!=10 for v in form_counts.values())
    shared=sum(len(ids) for ids in family_forms.values() if len(ids)>1)
    return {'records':total,'form_ids':len(form_counts),'grade_counts':dict(grades),
            'topic_pairs':len(topics),'forms_not_exactly_10':short,
            'forms_sharing_family':shared,'duplicate_question_samples':duplicates,
            'missing_field_samples':missing,'malformed_line_samples':malformed,
            'independent_math_types_certified':0,
            'caveat':'Method-family similarity is a flag, not proof of same type; distinct IDs are not proof of independent math types.',
            'topic_counts':[{'grade':g,'topic':t,'questions':v,'form_ids':sum(1 for x in form_counts if x[0]==g and x[1]==t)} for (g,t),v in sorted(topics.items())]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('bank');p.add_argument('--output');a=p.parse_args()
    result=audit(a.bank);s=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s,encoding='utf-8')
    else:print(s)
