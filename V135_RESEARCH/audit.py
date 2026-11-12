"""Audit candidate V135 corpus; cannot establish educational method novelty.
Checks deterministic source regeneration, catalog consistency, exact stem collisions,
leakage, within-form diversity, and suspicious reuse of method descriptions.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import importlib.util
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parent.parent
DIR=ROOT/'V135_RESEARCH'
def prior_question_files():
 # Coverage is limited to JSONL banks packaged with this release.
 # Other database tables, generated/on-demand problems and remote stores
 # are outside the scan and must never be treated as certified duplicate-free.
 discovered=set(ROOT.rglob('*QUESTIONS.jsonl')) | set(ROOT.rglob('*questions.jsonl'))
 return sorted(p for p in discovered
   if 'V135_RESEARCH' not in p.parts and '.venv' not in p.parts
   and '__pycache__' not in p.parts and '.git' not in p.parts)

METHOD_FILES=[
 'V131_RESEARCH/V131_CANDIDATE_METHODS.jsonl',
 'V132_RESEARCH/V132_CANDIDATE_METHODS.jsonl',
 'V133_RESEARCH/V133_CANDIDATE_METHODS.jsonl',
 'V134_RESEARCH/V134_CANDIDATE_METHODS.jsonl',
]

def read(path):
 with Path(path).open(encoding='utf8') as f:
  for row in f:
   if row.strip():yield json.loads(row)

def norm(text):
 return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(text)).casefold().strip())

def check(methods,questions,catalog,old_stems=None,source_regeneration=None):
 errors=[];warnings=[]
 official={c['id']:c['grade'] for c in catalog}
 formids=[f.get('method_id') for f in methods]
 qids=[q.get('id') for q in questions]
 if len(formids)!=len(set(formids)):errors.append('duplicate method ID')
 if len(qids)!=len(set(qids)):errors.append('duplicate question ID')
 by_form=defaultdict(list)
 seen=set()
 for q in questions:
  qid=q.get('id','?');mid=q.get('method_id')
  by_form[mid].append(q)
  if mid not in formids:errors.append(f'{qid} missing method reference')
  if official.get(q.get('topic'))!=q.get('grade'):errors.append(f'{qid} wrong topic/grade')
  if q.get('review_status')!='pending-expert-review' or q.get('independence_certified') is not False or q.get('published') is not False:
   errors.append(f'{qid} publication or certification leak')
  if not isinstance(q.get('solution'),str) or len(q.get('solution',''))<65:errors.append(f'{qid} insufficient solution')
  if not q.get('answer') or not q.get('independent_check') or q.get('answer')!=q.get('independent_check'):
   errors.append(f'{qid} answer/check mismatch')
  stem=norm(q.get('question',''))
  if not stem:errors.append(f'{qid} blank question')
  if stem in seen:errors.append(f'{qid} duplicate stem in batch')
  seen.add(stem)
  if old_stems is not None and stem in old_stems:errors.append(f'{qid} previous exact collision')
  if source_regeneration is not None and qid in source_regeneration and q!=source_regeneration[qid]:
   errors.append(f'{qid} source regeneration mismatch')
 for f in methods:
  mid=f.get('method_id');qs=by_form[mid]
  if official.get(f.get('topic'))!=f.get('grade'):errors.append(f'{mid} wrong topic/grade')
  if f.get('review_status')!='pending-expert-review' or f.get('independence_certified') is not False or f.get('published') is not False:
   errors.append(f'{mid} method publication/certification leak')
  if len(qs)!=10 or f.get('questions_expected')!=10:errors.append(f'{mid} not exactly ten exercises')
  if any(q['topic']!=f['topic'] or q['grade']!=f['grade'] for q in qs):errors.append(f'{mid} conflicting question topic')
  if len(set(q['answer'] for q in qs))<8:warnings.append(f'{mid}: fewer than eight distinct answers in ten examples')
 return errors,warnings

def run():
 forms=list(read(DIR/'V135_CANDIDATE_METHODS.jsonl'))
 qs=list(read(DIR/'V135_VERIFIED_QUESTIONS.jsonl'))
 catalog=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text(encoding='utf8'))
 old=set();old_count=0;missing=[];first_seen={};duplicates=[]
 source_files=prior_question_files()
 for path in source_files:
  for line_index,q in enumerate(read(path),1):
   stem=q.get('question') or q.get('question_text') or q.get('stem') or q.get('problem')
   if stem:
    normalized=norm(stem)
    provenance={'file':str(path.relative_to(ROOT)),'line':line_index,'id':q.get('id',q.get('form_id',q.get('source_form_id')))}
    if normalized in first_seen:
     duplicates.append({'first':first_seen[normalized],'again':{'file':str(path.relative_to(ROOT)),'line':line_index,'id':q.get('id',q.get('form_id',q.get('source_form_id')))},'question':stem})
    else:first_seen[normalized]=provenance
    old.add(normalized)
   old_count+=1
 if not source_files:missing.append('no previous question JSONL found')
 gen_spec=importlib.util.spec_from_file_location('v135_source',ROOT/'V135_RESEARCH_generate.py')
 module=importlib.util.module_from_spec(gen_spec);gen_spec.loader.exec_module(module)
 regen={module.question(j,i)['id']:module.question(j,i) for j in range(len(module.SPECS)) for i in range(10)}
 errors,warnings=check(forms,qs,catalog,old,regen)
 if missing:errors.append('missing prior datasets: '+str(missing))
 if set(regen)!=set(q['id'] for q in qs):errors.append('source regeneration ID set mismatch')
 old_forms=[]
 for rel in METHOD_FILES:
  old_forms.extend(list(read(ROOT/rel)))
 exact_method_title_overlap=[]
 for f in forms:
  prev=[m['method_id'] for m in old_forms if m.get('topic')==f['topic'] and norm(m.get('title',''))==norm(f.get('title',''))]
  if prev:exact_method_title_overlap.append({'candidate':f['method_id'],'possible_prior_methods':prev})
 # This is a strictly limited signal: same title is not proof of same method;
 # different titles are not proof of novelty, either.
 result={
  'version':'V135','official_topics':len(catalog),'new_candidate_groups':len(forms),
  'new_worked_questions':len(qs),'oracle_crosscheck_recomputed':sum(q==regen.get(q['id']) for q in qs),
  'prior_question_files_scanned':len(source_files),'prior_question_records_scanned':old_count,'prior_unique_normalized_stems':len(old),
  'normalized_question_collisions_with_previous':sum(norm(q['question']) in old for q in qs),
  'prior_methods_with_same_topic_and_title':exact_method_title_overlap,
  'prior_jsonl_bytes_scanned':sum(p.stat().st_size for p in source_files),
  'historical_normalized_duplicate_occurrences':len(duplicates),
  'historical_duplicates_sample':duplicates[:10],
  'certified_new_independent_methods':0,'published_new_questions':sum(q.get('published',False) for q in qs),
  'fatal_errors':errors,'quality_warnings':warnings,
  'novelty_across_all_mathematics':'NOT ESTABLISHED: human/specialist review required',
  'publication_status':'PENDING_EXPERT_REVIEW_QUARANTINED'
 }
 (DIR/'V135_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 (DIR/'V135_HISTORICAL_DUPLICATES.json').write_text(json.dumps({'source_scan':'packaged historical JSONL only','duplicate_occurrences':duplicates,'automatic_deletion_performed':False,'publication_policy':'manual review before import'},ensure_ascii=False,indent=2),encoding='utf8')
 return result

if __name__=='__main__':
 report=run();print(json.dumps(report,ensure_ascii=False,indent=2))
 if report['fatal_errors']:raise SystemExit(1)
