#!/usr/bin/env python3
"""V88: streaming audit; never treats an ID as proof of an independent type.
Run: python tools/type_integrity_audit.py [path/to/verified_seed_bank.jsonl] [report.json]
"""
import collections, hashlib, json, pathlib, sys
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1]/'backend/app/ai/verified_seed/verified_seed_bank.jsonl'
counts=collections.Counter(); families=collections.defaultdict(set); questions=collections.defaultdict(set)
per_topic=collections.Counter(); missing=collections.Counter(); exact_dupes=0; seen_hashes=set(); bad_lines=[]
with path.open(encoding='utf8') as f:
 for line_no,line in enumerate(f,1):
  try:r=json.loads(line)
  except Exception:bad_lines.append(line_no);continue
  g=str(r.get('grade',''));t=str(r.get('topic',''));fid=str(r.get('form_id',''))
  key=(g,t,fid);counts[key]+=1;per_topic[(g,t)]+=1
  family=str(r.get('method_family') or r.get('form_signature') or fid)
  families[(g,t,family)].add(fid)
  q=str(r.get('question','')).strip();h=hashlib.sha256((g+'\0'+t+'\0'+q).encode()).digest()
  if h in seen_hashes:exact_dupes+=1
  else:seen_hashes.add(h)
  if not q or not str(r.get('answer','')).strip() or not str(r.get('solution','')).strip():missing[key]+=1
forms_with_shared_family=set()
for ids in families.values():
 if len(ids)>1:forms_with_shared_family.update(ids)
report={'records':sum(counts.values()),'unique_form_ids_per_grade_topic':len(counts),'grade_topic_pairs':len(per_topic),'forms_with_not_exactly_10_questions':sum(v!=10 for v in counts.values()),'forms_with_missing_fields':len(missing),'duplicate_question_texts_within_grade_topic':exact_dupes,'method_family_clusters':len(families),'form_id_strings_in_shared_method_families':len(forms_with_shared_family),'invalid_json_lines':bad_lines[:30],'important':'Shared method family is a risk indicator, not proof of duplicate types. Distinct IDs do not prove independent mathematical types.'}
output=json.dumps(report,ensure_ascii=False,indent=2)
if len(sys.argv)>2:pathlib.Path(sys.argv[2]).write_text(output,encoding='utf8')
print(output)
