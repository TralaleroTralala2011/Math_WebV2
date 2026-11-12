#!/usr/bin/env python3
"""Preflight for batches of genuinely different mathematical types.
This is a *structural* gate, not a certificate of mathematical independence.
Usage: python tools/batch_import_preflight.py new_questions.jsonl [existing_bank.jsonl]
Exit nonzero if 10 questions per form, missing fields, exact duplicates or signatures conflict.
"""
import collections,hashlib,json,pathlib,sys
if len(sys.argv)<2:sys.exit(__doc__)
source=pathlib.Path(sys.argv[1]);existing=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else None
required=('grade','topic','form_id','form_signature','question','answer','solution')
forms=collections.defaultdict(list);signatures=collections.defaultdict(set);qhash=set();errors=[];existing_keys=set();existing_signatures=set();existing_qhash=set()
def read(path):
 with path.open(encoding='utf8') as f:
  for i,line in enumerate(f,1):
   if line.strip():
    try:yield i,json.loads(line)
    except Exception as e:errors.append(f'{path}:{i}: invalid JSON: {e}')
def key(r):return (str(r.get('grade')),str(r.get('topic')),str(r.get('form_id')))
def sig(r):return (str(r.get('grade')),str(r.get('topic')),str(r.get('form_signature','')).strip().casefold())
def qkey(r):return (str(r.get('grade')),str(r.get('topic')),hashlib.sha256(str(r.get('question','')).strip().encode()).digest())
if existing:
 for _,r in read(existing):existing_keys.add(key(r));existing_signatures.add(sig(r));existing_qhash.add(qkey(r))
for i,r in read(source):
 missing=[field for field in required if r.get(field) is None or str(r[field]).strip()=='']
 if missing:errors.append(f'line {i}: missing {missing}')
 k=key(r);forms[k].append(r);s=sig(r);signatures[s].add(k)
 if k in existing_keys:errors.append(f'line {i}: form ID already exists: {k}')
 if s in existing_signatures:errors.append(f'line {i}: form signature already exists: {s}')
 q=qkey(r)
 if q in qhash or q in existing_qhash:errors.append(f'line {i}: duplicate question: {k}')
 qhash.add(q)
for k,items in forms.items():
 if len(items)!=10:errors.append(f'form {k}: {len(items)} questions, expected 10')
for s,ids in signatures.items():
 if len(ids)>1:errors.append(f'signature {s} reused by {len(ids)} IDs')
report={'candidate_form_ids':len(forms),'candidate_questions':sum(map(len,forms.values())),'errors':len(errors),'first_errors':errors[:30], 'independence_certified':False,'note':'A passing preflight cannot prove types are mathematically independent; requires expert semantic review.'}
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(errors))
