#!/usr/bin/env python3
"""Validate structural integrity of the MATH_WEB JSONL question bank.
This does NOT certify that methods are mathematically independent or that solutions are correct.
"""
import json,collections,sys
path=sys.argv[1] if len(sys.argv)>1 else 'backend/app/ai/verified_seed/verified_seed_bank.jsonl'
forms=collections.Counter(); seen=set();dups=0;bad=0;total=0
with open(path,encoding='utf-8') as f:
 for n,line in enumerate(f,1):
  try:
   r=json.loads(line)
   for k in ('grade','topic','form_id','question','answer','solution'): assert k in r and r[k] not in (None,'')
   key=(r['grade'],r['topic'],r['form_id']);forms[key]+=1
   qkey=(r['grade'],r['topic'],r['question'])
   if qkey in seen:dups+=1
   seen.add(qkey);total+=1
  except Exception as e: print('INVALID',n,str(e));bad+=1
incorrect=sum(n!=10 for n in forms.values())
print(json.dumps({'questions':total,'form_ids':len(forms),'forms_not_10':incorrect,'duplicate_questions':dups,'invalid_rows':bad,'mathematical_independence_verified':False},ensure_ascii=False,indent=2))
sys.exit(bool(incorrect or dups or bad))
