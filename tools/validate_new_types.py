
#!/usr/bin/env python3
"""Validate a candidate expansion before appending it to the verified bank.
Usage: python tools/validate_new_types.py existing.jsonl candidate.jsonl --min-new 10000
Counts are NOT evidence of mathematically independent problem archetypes.
"""
import argparse, collections, json, pathlib, sys, hashlib
p=argparse.ArgumentParser()
p.add_argument("existing",type=pathlib.Path)
p.add_argument("candidate",type=pathlib.Path)
p.add_argument("--min-new",type=int,default=10000)
a=p.parse_args()
def rows(path):
    with path.open(encoding="utf-8") as f:
        for lineno,line in enumerate(f,1):
            if line.strip():
                try: yield json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f"{path}:{lineno}: {e}")
def key(r):return (str(r.get("grade","")),str(r.get("topic","")).strip(),str(r.get("form_id","")).strip())
existing_keys=set()
for r in rows(a.existing): existing_keys.add(key(r))
forms=collections.Counter(); questions=set(); signatures=collections.defaultdict(set); failures=[]
for i,r in enumerate(rows(a.candidate),1):
    k=key(r)
    if not all(k) or not r.get("form_signature") or not str(r.get("question","")).strip() or not str(r.get("answer","")).strip() or not str(r.get("solution","")).strip():
        failures.append(f"row {i}: missing grade/topic/form_id/signature/question/answer/solution")
    if k in existing_keys:failures.append(f"row {i}: existing type ID {k}")
    q=(k[0],k[1],str(r.get("question","")).strip().casefold())
    if q in questions:failures.append(f"row {i}: repeated question")
    questions.add(q)
    forms[k]+=1
    signatures[k].add(str(r.get("form_signature","")).strip())
for k,n in forms.items():
    if n!=10:failures.append(f"{k}: {n} questions, expected 10")
    if len(signatures[k])!=1:failures.append(f"{k}: inconsistent form signature")
if len(forms)<a.min_new:failures.append(f"only {len(forms)} candidate type IDs, minimum {a.min_new}")
print(json.dumps({"new_type_ids":len(forms),"new_questions":sum(forms.values()),"errors":len(failures),
 "caution":"Structural validation does not certify mathematical independence or answer correctness",
 "sample_errors":failures[:20]},ensure_ascii=False,indent=2))
sys.exit(1 if failures else 0)
